"""
Clonar un insumo y, si se quiere, sustituir el original — `CONOCIMIENTO.md` §8.4 y §16.2, `MODELO.md` §4 y §4b, D-478.

Una clave **nunca se reescribe** (§16.2): para corregir una que engaña —P-11: las 79 trabes, mallas, nervaduras y losas nervadas que OPUS
llama `AUX-` siendo materiales— nace un **clon** con la clave correcta y el contenido del original, y lo que lo citaba pasa a citar al clon.

| Modo | Qué pasa con el original | Para qué |
|---|---|---|
| **mantener** | sigue vivo, los dos se usan | la trabe T-3 y la T-4: dos variantes de la misma receta |
| **sustituir** | todo lo que lo citaba pasa al clon; **la clave vieja sigue entrando** | corregir el prefijo, el nombre o la forma de la clave |

*Sustituir* no reescribe nada: cada concepto o compuesto que citaba al original recibe una **versión nueva** —la misma receta con el clon
en lugar del original, el mismo PU, porque el clon vale lo que valía el original— y los renglones de presupuesto que fijaban la versión
vigente pasan a fijar la nueva. Las versiones viejas quedan como estaban. El original no se borra: queda, retirado, en el catálogo.

**La homologación** (§16.2): después de sustituir, un archivo de OPUS que todavía trae `AUX-00001` se lee como `PRE-00120` (la carga lo
dice en un aviso, no lo ignora ni lo trata como un concepto ausente). El viaje de vuelta —que la clave vieja siga saliendo hacia otros
sistemas hasta que alguien autorice dejar de usarla— se guarda como una bandera de la clonación (`exporta_clave_vieja`); todavía no hay
quien exporte.

**Lo que no se hace:** no se sustituye lo que fija un renglón de un subárbol contratado (D-475: lo contratado no se toca; va a control de
cambio) ni lo que un renglón de presupuesto pone directo (un concepto se sustituye renglón por renglón, no aquí). En esos casos, el
original no se toca y se dice por qué.

El sistema propone y el humano decide: `proponer` no escribe nada. Quién clona es una función nueva, `clonar_insumo` (§5b, propuesta):
Control de obra, porque cambia lo que citan los conceptos de todas las obras. Corregir un prefijo entero (`corregir_prefijo`) son tantas
clonaciones como claves, **cada una completa y con su carga**: si se interrumpe, se reanuda donde se quedó y no deja nada a medias.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from decimal import Decimal
from typing import Dict, List, Optional, Tuple

from .catalogo import (
    CatalogoCambio,
    ConceptoSinMatriz,
    InsumoPlan,
    LineaPlan,
    NodoConMatriz,
    PlanDeClonacion,
    RepositorioCatalogo,
    ResultadoClonacion,
    SustitucionDePadre,
)
from .dominio import Categoria, Rol
from .importacion_opus import huella as huella_de_matriz
from .servicio_programa import Roles, rol_efectivo

FUNCION_DE_CLONAR = "clonar_insumo"
MODOS = ("mantener", "sustituir")
ANCHO_DE_NUMERO = 5  # `PRE-00120`


class ClonacionNoProcede(Exception):
    """La clonación tiene un impedimento: se dice cuál, y el original no se toca."""

    def __init__(self, mensaje: str, problemas: Tuple[str, ...] = ()) -> None:
        super().__init__(mensaje)
        self.problemas = problemas


@dataclass(frozen=True)
class PadreRedirigido:
    clave: str
    version_antes: int
    version_despues: int
    renglones: int  # los renglones de presupuesto que pasan a fijar la versión nueva
    pu: Decimal  # el mismo: no se mueve dinero


@dataclass(frozen=True)
class PropuestaDeClonacion:
    original: str
    clave: str
    modo: str
    descripcion: str
    unidad: str
    tipo: str  # insumo · compuesto (un material con matriz) · concepto sin matriz
    redirigidos: Tuple[PadreRedirigido, ...]
    problemas: Tuple[str, ...]  # lo que impide hacerla: el original no se toca
    plan: Optional[PlanDeClonacion]

    @property
    def aplicable(self) -> bool:
        return not self.problemas

    @property
    def renglones(self) -> int:
        return sum(p.renglones for p in self.redirigidos)


@dataclass(frozen=True)
class PropuestaDeCorreccion:
    """Corregir un prefijo entero: qué clave vieja pasa a cuál nueva, qué ya estaba hecho y qué no se puede."""

    viejo: str
    nuevo: str
    pares: Tuple[Tuple[str, str], ...]  # (clave vieja, clave del clon) de lo que falta por hacer, en el orden en que se hace
    hechos: Tuple[Tuple[str, str], ...]  # lo que ya se sustituyó
    omitidos: Tuple[str, ...]  # claves del prefijo cuyo número no se sabe leer: no se proponen
    propuestas: Tuple[PropuestaDeClonacion, ...]  # lo que cada una haría hoy; las que dependen de otra se rehacen al llegar a ellas
    base: int = 0  # la última carga que vio quien revisó: si al aplicar hay otra, `CatalogoCambio` (D-485)

    @property
    def rechazadas(self) -> Tuple[PropuestaDeClonacion, ...]:
        return tuple(p for p in self.propuestas if not p.aplicable)


@dataclass(frozen=True)
class ResultadoDeCorreccion:
    hechos: Tuple[Tuple[str, str, ResultadoClonacion], ...]  # (clave vieja, clon, lo que se escribió)
    rechazados: Tuple[PropuestaDeClonacion, ...]


def _tipo(con_matriz: bool, rol: str) -> str:
    if con_matriz:
        return "compuesto"
    return "insumo" if rol == "insumo" else "concepto sin matriz"


class ServicioClonacion:
    def __init__(self, repositorio: RepositorioCatalogo, permisos=None) -> None:
        """`permisos` entrega `ROL_FUNCION` tal como está hoy (`RepositorioAccesos.permisos`); sin ella, la tabla por omisión."""
        self.repo = repositorio
        self._permisos = permisos

    def rol_para(self, roles: Roles) -> str:
        return rol_efectivo(FUNCION_DE_CLONAR, roles, None if self._permisos is None else self._permisos())

    # ------------------------------------------------------------------ una clonación
    def proponer(self, original: str, clave: str, modo: str, rol: Roles, usuario: str) -> PropuestaDeClonacion:
        """Qué pasaría si se clonara `original` como `clave`. No escribe nada."""
        rol_con_que = self.rol_para(rol)
        if not usuario:
            raise ValueError("toda clonación dice quién la hizo")
        estado = self.repo.estado_vigente()  # primero la última carga y después el contenido: si algo cambia en medio, el candado salta
        problemas: List[str] = []
        if modo not in MODOS:
            problemas.append(f"el modo debe ser uno de: {', '.join(MODOS)}")
        if not clave.strip():
            problemas.append("el clon necesita una clave")
        elif clave == original:
            problemas.append("el clon necesita una clave distinta de la del original")
        elif clave in estado.descripcion:
            problemas.append(f"ya hay un nodo con la clave {clave}")
        if original not in estado.descripcion:
            problemas.append(f"no hay un nodo del catálogo con la clave {original}")
            return PropuestaDeClonacion(original, clave, modo, "", "", "", (), tuple(problemas), None)
        nodo = self.repo.nodo(original)
        tipo = _tipo(nodo.con_matriz, nodo.rol)
        sustituido_por = next((c.clon for c in self.repo.clones() if c.original == original and c.modo == "sustituir"), None)
        if sustituido_por is not None:
            problemas.append(f"{original} ya se sustituyó por {sustituido_por}: la clave vigente es la del clon")
        padres = ()
        if modo == "sustituir" and sustituido_por is None:
            citas = self.repo.citas_de(original)
            if citas.renglones_directos:
                problemas.append(
                    f"{original} lo ponen directo {citas.renglones_directos} renglones de presupuesto: un concepto se sustituye renglón por renglón, no aquí")
            # los compuestos ya retirados no se tocan: nadie los cita, y lo que reciba su clon ya está en el clon
            padres = tuple(p for p in citas.padres if p.clave not in estado.homologaciones)
            for p in padres:
                if p.clave in estado.en_contratado:
                    problemas.append(f"{original} lo cita {p.clave}, que fija un renglón contratado: va a control de cambio, no se redirige aquí")

        if problemas:
            return PropuestaDeClonacion(original, clave, modo, nodo.descripcion, nodo.unidad, tipo, (), tuple(problemas), None)

        if nodo.con_matriz:
            v = self.repo.versiones(original)[-1]
            nuevo = NodoConMatriz(
                clave, nodo.descripcion, nodo.unidad, Rol(nodo.rol), Categoria(nodo.categoria), v.huella, v.pu,
                tuple(LineaPlan(l.hijo, l.cantidad, Categoria(l.reporta_a), l.porcentaje) for l in v.lineas))
        elif nodo.rol == "insumo":
            nuevo = InsumoPlan(clave, nodo.descripcion, nodo.unidad, Categoria(nodo.categoria), nodo.precio or Decimal("0"), nodo.precio is not None)
        else:
            nuevo = ConceptoSinMatriz(clave, nodo.descripcion, nodo.unidad)

        sustituciones: List[SustitucionDePadre] = []
        redirigidos: List[PadreRedirigido] = []
        for p in padres:
            lineas = tuple(
                LineaPlan(clave if l.hijo == original else l.hijo, l.cantidad, Categoria(l.reporta_a), l.porcentaje) for l in p.lineas)
            sustituciones.append(SustitucionDePadre(
                p.clave, lineas, huella_de_matriz((l.hijo, l.cantidad) for l in lineas), p.pu, p.renglones))
            redirigidos.append(PadreRedirigido(p.clave, p.version, p.version + 1, len(p.renglones), p.pu))
        resumen: Dict[str, object] = {
            "original": original, "clon": clave, "modo": modo, "tipo": tipo,
            "redirigidos": [{"clave": r.clave, "version_antes": r.version_antes, "version_despues": r.version_despues, "renglones": r.renglones}
                            for r in redirigidos],
        }
        plan = PlanDeClonacion(estado.ultima_carga, original, clave, modo, usuario, rol_con_que, resumen, nuevo, tuple(sustituciones))
        return PropuestaDeClonacion(original, clave, modo, nodo.descripcion, nodo.unidad, tipo, tuple(redirigidos), (), plan)

    def clonar(self, original: str, clave: str, modo: str, rol: Roles, usuario: str,
               esperaba: Optional[int] = None) -> Tuple[PropuestaDeClonacion, ResultadoClonacion]:
        """Propone y aplica. Si la propuesta tiene un impedimento, `ClonacionNoProcede` y no se escribe nada. `esperaba` es la última
        carga que vio quien decide (`plan.base` de la propuesta): si el catálogo ya va en otra, `CatalogoCambio`."""
        p = self.proponer(original, clave, modo, rol, usuario)
        if not p.aplicable:
            raise ClonacionNoProcede("no se puede clonar: " + "; ".join(p.problemas), p.problemas)
        assert p.plan is not None
        if esperaba is not None and p.plan.base != esperaba:
            raise CatalogoCambio(f"la última carga es la {p.plan.base} y esta se revisó sobre la {esperaba}")
        return p, self.repo.clonar(p.plan)

    # ------------------------------------------------------------------ un prefijo entero
    def proponer_correccion_de_prefijo(self, viejo: str, nuevo: str, desde: int, rol: Roles, usuario: str) -> PropuestaDeCorreccion:
        """Qué claves `viejo-NNNNN` pasarían a `nuevo-NNNNN` (desde `desde`, en el orden de su número, saltando los números ocupados) y
        qué diría cada clonación hoy. No escribe nada."""
        self.rol_para(rol)
        if not viejo or not nuevo or viejo == nuevo:
            raise ValueError("el prefijo viejo y el nuevo deben existir y ser distintos")
        if desde < 1:
            raise ValueError("la numeración empieza en 1 o más")
        estado = self.repo.estado_vigente()
        patron = re.compile(rf"{re.escape(viejo)}-(\d+)")
        candidatas: List[Tuple[int, str]] = []
        omitidos: List[str] = []
        for c in estado.descripcion:
            if not c.startswith(viejo + "-") or c in estado.homologaciones:
                continue
            m = patron.fullmatch(c)
            if m is None:
                omitidos.append(c)
            else:
                candidatas.append((int(m.group(1)), c))
        candidatas.sort()
        hechos = tuple(sorted((c.original, c.clon) for c in self.repo.clones() if c.modo == "sustituir" and c.original.startswith(viejo + "-")))
        ocupadas = set(estado.descripcion)
        pares: List[Tuple[str, str]] = []
        n = desde
        for _, c in candidatas:
            while f"{nuevo}-{n:0{ANCHO_DE_NUMERO}d}" in ocupadas:
                n += 1
            clave = f"{nuevo}-{n:0{ANCHO_DE_NUMERO}d}"
            ocupadas.add(clave)
            pares.append((c, clave))
        propuestas = tuple(self.proponer(o, k, "sustituir", rol, usuario) for o, k in pares)
        return PropuestaDeCorreccion(viejo, nuevo, tuple(pares), hechos, tuple(sorted(omitidos)), propuestas, estado.ultima_carga)

    def corregir_prefijo(self, viejo: str, nuevo: str, desde: int, rol: Roles, usuario: str,
                         esperaba: Optional[int] = None) -> ResultadoDeCorreccion:
        """Sustituye cada clave `viejo-NNNNN` por su clon `nuevo-NNNNN`, una clonación completa tras otra. Lo que no se puede (algo
        contratado lo cita) se salta y se dice; el resto se hace. Si se interrumpe, se reanuda: lo ya sustituido no se repite.
        `esperaba` es la última carga que vio quien decide (`PropuestaDeCorreccion.base`): si el catálogo ya va en otra, `CatalogoCambio`."""
        propuesta = self.proponer_correccion_de_prefijo(viejo, nuevo, desde, rol, usuario)
        if esperaba is not None and propuesta.base != esperaba:
            raise CatalogoCambio(f"la última carga es la {propuesta.base} y esta se revisó sobre la {esperaba}")
        hechos: List[Tuple[str, str, ResultadoClonacion]] = []
        rechazados: List[PropuestaDeClonacion] = []
        for original, clave in propuesta.pares:
            try:
                _, r = self.clonar(original, clave, "sustituir", rol, usuario)  # se propone con lo de hoy: las anteriores ya se escribieron
            except ClonacionNoProcede:
                rechazados.append(self.proponer(original, clave, "sustituir", rol, usuario))
                continue
            hechos.append((original, clave, r))
        return ResultadoDeCorreccion(tuple(hechos), tuple(rechazados))


# --------------------------------------------------------------------------- en palabras


def informe_de_clonacion(p: PropuestaDeClonacion) -> str:
    modo = "clonar y sustituir" if p.modo == "sustituir" else "clonar y mantener"
    o = [f"{modo.capitalize()} — {p.original} → {p.clave}", ""]
    if p.descripcion:
        o.append(f"  {p.tipo}: {p.descripcion}" + (f" ({p.unidad})" if p.unidad else ""))
    if p.problemas:
        o += ["", "NO SE PUEDE — el original no se toca"] + [f"  {x}" for x in p.problemas]
        return "\n".join(o)
    if p.modo == "mantener":
        o.append(f"  {p.original} sigue vivo; {p.clave} nace con su misma receta y precio. Los dos se usan.")
        return "\n".join(o)
    o.append(f"  {p.original} deja de usarse; {p.clave} nace con su misma receta y precio. La clave vieja sigue entrando: un archivo que la")
    o.append(f"  traiga se lee como {p.clave}.")
    if p.redirigidos:
        o += ["", f"Lo que lo citaba pasa a citar al clon ({len(p.redirigidos)} versiones nuevas, {p.renglones} renglones de presupuesto; el PU no se mueve)"]
        o += [f"  {r.clave:<12} v{r.version_antes} → v{r.version_despues}   {r.renglones} renglones   PU {r.pu}" for r in p.redirigidos[:40]]
        if len(p.redirigidos) > 40:
            o.append(f"  … y {len(p.redirigidos) - 40} más")
    else:
        o.append("  Nada lo citaba.")
    return "\n".join(o)


def informe_de_correccion(c: PropuestaDeCorreccion) -> str:
    o = [f"Corregir el prefijo {c.viejo}- por {c.nuevo}-", ""]
    o.append(f"  {len(c.pares):>4} claves por sustituir · {len(c.hechos)} ya sustituidas · {len(c.rechazadas)} que hoy no se pueden")
    if c.omitidos:
        o.append(f"  {len(c.omitidos):>4} claves con prefijo {c.viejo}- que no terminan en un número, no se proponen: {', '.join(c.omitidos)}")
    por_propuesta = {p.original: p for p in c.propuestas}
    if c.pares:
        o += ["", "Cada una, con lo que la cita hoy"]
        for original, clave in c.pares:
            p = por_propuesta[original]
            marca = "" if p.aplicable else "  [NO SE PUEDE: " + "; ".join(p.problemas) + "]"
            o.append(f"  {original:<10} → {clave:<10} {p.renglones:>4} renglones · {len(p.redirigidos):>3} versiones nuevas  {p.descripcion[:44]}{marca}")
    return "\n".join(o)


def informe_de_resultado(r: ResultadoDeCorreccion) -> str:
    o = [f"Sustituidas: {len(r.hechos)} · versiones nuevas: {sum(x.versiones_nuevas for _, _, x in r.hechos)} · renglones fijados: "
         f"{sum(x.renglones_fijados for _, _, x in r.hechos)}"]
    for p in r.rechazados:
        o.append(f"  NO SE HIZO {p.original} → {p.clave}: " + "; ".join(p.problemas))
    return "\n".join(o)
