"""
Contratar un subárbol del presupuesto — `CONOCIMIENTO.md` §1.4 («el estado es del nodo»), §2.2 y `MODELO.md` §3 (hallazgo 6) y
§4a («dos disparadores de versión»), D-475.

Los planos llegan por partes y se contrata por partes: cimentación entra a contrato mientras acabados sigue en diseño. Un bloque del
presupuesto (capítulo, subcapítulo, nivel 2 o 3) pasa a **contratado** y **su subárbol se contrata completo**; los de abajo lo heredan.
Contratar hace dos cosas, en una sola transacción:

1. **Fija el PU de cada concepto del subárbol a ese momento**, «aunque la receta no haya cambiado ese día». Cada renglón del subárbol
   fija la versión vigente de su concepto; si el PU que da el motor de cálculo hoy no es el de esa versión (los precios de los insumos
   se movieron desde que se cargó), nace una versión nueva con **la misma receta y el PU de hoy**. Nada se recalcula después.
2. **Congela el subárbol**: su cantidad y la versión que fija no se tocan (la base lo garantiza). Lo que cambie va por control de
   cambio, que agrega y no edita (§13.4). Lo que se agregue «al final» sí se puede.

El sistema propone y el humano decide: `proponer` no escribe nada y dice, concepto por concepto, qué PU tenía fijado y cuál queda, y
cuánto cambia el monto del subárbol. **Si el PU de un concepto se mueve más de 5 %, pide confirmación** (§2.2), y un concepto sin matriz
—que vale cero— también la pide: contratar con un precio de cero es una decisión de alguien. Un subárbol con algo sin confirmar no se
contrata, porque no se contrata a medias.

Quién contrata es una función nueva, `contratar_subarbol` (§5b, propuesta): Control de obra.
"""
from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from decimal import Decimal
from typing import Dict, Iterable, List, Mapping, Optional, Set, Tuple, Union

from .catalogo import (
    Congelamiento,
    DatosDePresupuesto,
    Pendiente,
    PlanDeContratacion,
    PU_MOVIO,
    RepositorioCatalogo,
    ResultadoContratacion,
    UMBRAL_DE_CONFIRMACION,
    VersionPorFijar,
    YaContratado,
)
from .motor_calculo import _redondear, precio_unitario
from .servicio_programa import Roles, rol_efectivo

FUNCION_DE_CONTRATAR = "contratar_subarbol"
SIN_MATRIZ = "sin_matriz"  # el concepto no tiene matriz: vale cero y contratarlo así lo decide alguien

# qué se hace con el concepto al contratar
IGUAL = "igual"  # el renglón ya fija la versión vigente y su PU es el de hoy: no cambia nada
FIJAR_VIGENTE = "fijar_vigente"  # el renglón fija una versión vieja; la vigente tiene el PU de hoy: pasa a fijar la vigente
VERSION_NUEVA = "version_nueva"  # el PU de hoy no es el de la vigente: nace una versión con la misma receta y el PU de hoy


class ContratacionPendiente(Exception):
    """Hay conceptos que piden confirmación (el PU se mueve más de 5 %, o no tienen matriz): no se contrata a medias."""

    def __init__(self, mensaje: str, propuesta: "PropuestaDeContratacion") -> None:
        super().__init__(mensaje)
        self.propuesta = propuesta


@dataclass(frozen=True)
class ConceptoPorFijar:
    clave: str
    descripcion: str
    renglones: int  # cuántos renglones del subárbol lo usan
    version_fijada: Optional[int]  # la que fija el renglón hoy
    version_vigente: Optional[int]  # la última (nula si no tiene matriz)
    pu_fijado: Decimal  # el PU de la versión que fija el renglón
    pu_hoy: Decimal  # el que da el motor de cálculo con los precios de hoy
    accion: str

    @property
    def cambia(self) -> bool:
        return self.pu_hoy != self.pu_fijado or self.accion != IGUAL


@dataclass(frozen=True)
class PropuestaDeContratacion:
    presupuesto_id: int
    presupuesto_clave: str
    nodo_id: int
    ruta: str  # la ruta natural del bloque
    descripcion: str
    conceptos: Tuple[ConceptoPorFijar, ...]
    renglones: int  # los renglones que se fijan, sin contar los de bloques que ya estaban contratados
    ya_contratados: int  # renglones de bloques de abajo que ya estaban contratados y no se tocan
    total_antes: Decimal  # lo que suma el bloque hoy
    total_despues: Decimal  # lo que sumará con los PU fijados
    pendientes: Tuple[Pendiente, ...]
    plan: PlanDeContratacion

    @property
    def aplicable(self) -> bool:
        return not self.pendientes

    @property
    def diferencia(self) -> Decimal:
        return self.total_despues - self.total_antes


# --------------------------------------------------------------------------- lo contratado, de un presupuesto


def nodos_contratados(datos: DatosDePresupuesto, congelamientos: Iterable[Congelamiento]) -> Set[int]:
    """Los bloques contratados y todos los que cuelgan de ellos: el estado se hereda hacia abajo."""
    hijos: Dict[int, List[int]] = defaultdict(list)
    for l in datos.lineas:
        if datos.nodos[l.hijo_id].estructural:
            hijos[l.padre_id].append(l.hijo_id)
    out: Set[int] = set()
    pila = [c.nodo_id for c in congelamientos if c.estado == "contratado"]
    while pila:
        n = pila.pop()
        if n not in out:
            out.add(n)
            pila += hijos.get(n, ())
    return out


def _total_del_bloque(datos: DatosDePresupuesto, nodo_id: int, pu_de: Mapping[int, Decimal]) -> Decimal:
    """Lo que suma un bloque —sin su propia cantidad—, redondeando cada renglón a centavos antes de sumar, como OPUS. `pu_de` dice el PU
    de los renglones que cambian (por id de línea); los demás valen lo que su versión fijada."""
    hijos: Dict[int, list] = defaultdict(list)
    for l in datos.lineas:
        hijos[l.padre_id].append(l)

    def precio(n: int) -> Decimal:
        suma = Decimal("0")
        for l in hijos.get(n, ()):
            if datos.nodos[l.hijo_id].estructural:
                p = precio(l.hijo_id)
            else:
                p = pu_de.get(l.id, l.pu if l.pu is not None else Decimal("0"))
            suma += _redondear(l.cantidad * p)
        return suma

    return precio(nodo_id)


# --------------------------------------------------------------------------- el servicio


class ServicioContratacion:
    def __init__(self, repositorio: RepositorioCatalogo, permisos=None) -> None:
        """`permisos` entrega `ROL_FUNCION` tal como está hoy (`RepositorioAccesos.permisos`); sin ella, la tabla por omisión."""
        self.repo = repositorio
        self._permisos = permisos

    def rol_para(self, roles: Roles) -> str:
        return rol_efectivo(FUNCION_DE_CONTRATAR, roles, None if self._permisos is None else self._permisos())

    def _presupuesto(self, presupuesto: Union[int, str]) -> int:
        todos = self.repo.presupuestos()
        for p in todos:
            if (isinstance(presupuesto, int) and p.id == presupuesto) or (isinstance(presupuesto, str) and p.clave == presupuesto):
                return p.id
        raise ValueError(f"no hay presupuesto {presupuesto}")

    def contratados(self, presupuesto: Union[int, str]) -> Tuple[Congelamiento, ...]:
        return tuple(self.repo.congelamientos(self._presupuesto(presupuesto)))

    def proponer(
        self,
        presupuesto: Union[int, str],
        rol: Roles,
        usuario: str,
        donde: Optional[Union[int, str]] = None,
        confirmados: Iterable[str] = (),
    ) -> PropuestaDeContratacion:
        """Qué pasaría si se contratara ese bloque (por su id o su ruta natural; sin decirlo, el presupuesto entero). No escribe nada."""
        rol_con_que = self.rol_para(rol)
        if not usuario:
            raise ValueError("toda contratación dice quién la hizo")
        confirmados = frozenset(confirmados)
        pid = self._presupuesto(presupuesto)
        estado = self.repo.estado_vigente()  # primero la última carga y después el árbol: si algo cambia en medio, el candado salta
        datos = self.repo.datos_de_presupuesto(pid)
        nodo = self._bloque(datos, donde)
        congelamientos = self.repo.congelamientos(pid)

        # lo contratado: el bloque o uno de arriba no se vuelve a contratar; uno de abajo se respeta
        padre_de = {l.hijo_id: l.padre_id for l in datos.lineas if datos.nodos[l.hijo_id].estructural}
        directos = {c.nodo_id for c in congelamientos if c.estado == "contratado"}
        arriba, n = [], nodo.id
        while True:
            arriba.append(n)
            if n not in padre_de:
                break
            n = padre_de[n]
        for a in arriba:
            if a in directos:
                raise YaContratado(f"el bloque {datos.nodos[a].ruta_natural} ya está contratado", a)
        bajo_contratado = nodos_contratados(datos, congelamientos)

        # los renglones del subárbol que se fijan (los concepto), sin los de un bloque que ya estaba contratado
        hijos: Dict[int, list] = defaultdict(list)
        for l in datos.lineas:
            hijos[l.padre_id].append(l)
        por_fijar: List = []
        respetados = 0
        pila = [nodo.id]
        while pila:
            b = pila.pop()
            for l in hijos.get(b, ()):
                if datos.nodos[l.hijo_id].estructural:
                    pila.append(l.hijo_id)
                elif b in bajo_contratado:
                    respetados += 1
                else:
                    por_fijar.append(l)

        arbol = self.repo.arbol()
        pu_hoy: Dict[str, Decimal] = {}
        for l in por_fijar:
            clave = datos.nodos[l.hijo_id].clave
            if clave not in pu_hoy:
                pu_hoy[clave] = precio_unitario(l.hijo_id, arbol) if clave in estado.version else Decimal("0")

        agrupados: Dict[str, list] = defaultdict(list)
        for l in por_fijar:
            agrupados[datos.nodos[l.hijo_id].clave].append(l)
        conceptos: List[ConceptoPorFijar] = []
        pendientes: List[Pendiente] = []
        versiones_nuevas: List[VersionPorFijar] = []
        renglones: List[Tuple[int, str]] = []
        pu_despues: Dict[int, Decimal] = {}
        for clave in sorted(agrupados):
            ls = agrupados[clave]
            hoy = pu_hoy[clave]
            vigente = estado.version.get(clave)
            fijadas = sorted({l.version for l in ls if l.version is not None})
            fijada = fijadas[-1] if fijadas else None
            pu_fijado = next((l.pu for l in ls if l.version == fijada and l.pu is not None), Decimal("0"))
            if vigente is None:
                accion = IGUAL
                if clave not in confirmados:
                    pendientes.append(Pendiente(clave, SIN_MATRIZ, "no tiene matriz: vale cero y se contrataría así"))
            elif hoy == estado.pu[clave]:
                accion = IGUAL if all(l.version == vigente for l in ls) else FIJAR_VIGENTE
            else:
                accion = VERSION_NUEVA
                versiones_nuevas.append(VersionPorFijar(clave, hoy))
            if vigente is not None and pu_fijado > 0 and abs(hoy - pu_fijado) / pu_fijado > UMBRAL_DE_CONFIRMACION and clave not in confirmados:
                pendientes.append(Pendiente(clave, PU_MOVIO, f"el PU pasa de {pu_fijado} a {hoy}: pide confirmación"))
            descripcion = datos.nodos[ls[0].hijo_id].descripcion
            conceptos.append(ConceptoPorFijar(clave, descripcion, len(ls), fijada, vigente, pu_fijado, hoy, accion))
            if vigente is not None:
                for l in ls:
                    pu_despues[l.id] = hoy
                    if accion != IGUAL or l.version != vigente:
                        renglones.append((l.id, clave))

        antes = _total_del_bloque(datos, nodo.id, {})
        despues = _total_del_bloque(datos, nodo.id, pu_despues)
        resumen = {
            "presupuesto": datos.resumen.clave, "ruta": nodo.ruta_natural, "conceptos": len(conceptos), "renglones": len(por_fijar),
            "respetados": respetados, "versiones_nuevas": [v.clave for v in versiones_nuevas], "renglones_que_cambian_de_version": len(renglones),
            "total_antes": str(antes), "total_despues": str(despues), "confirmados": sorted(confirmados),
            "conceptos_que_se_mueven": [{"clave": c.clave, "antes": str(c.pu_fijado), "despues": str(c.pu_hoy)} for c in conceptos if c.cambia][:100],
        }
        plan = PlanDeContratacion(estado.ultima_carga, pid, nodo.id, usuario, rol_con_que, resumen, tuple(versiones_nuevas), tuple(renglones))
        return PropuestaDeContratacion(pid, datos.resumen.clave, nodo.id, nodo.ruta_natural, nodo.descripcion, tuple(conceptos), len(por_fijar),
                                       respetados, antes, despues, tuple(pendientes), plan)

    @staticmethod
    def _bloque(datos: DatosDePresupuesto, donde: Optional[Union[int, str]]):
        if donde is None:
            return datos.nodos[datos.raiz_id]
        for n in datos.nodos.values():
            if n.estructural and ((isinstance(donde, int) and n.id == donde) or (isinstance(donde, str) and n.ruta_natural == donde)):
                return n
        raise ValueError(f"el presupuesto {datos.resumen.clave} no tiene el bloque {donde}")

    def contratar(
        self,
        presupuesto: Union[int, str],
        rol: Roles,
        usuario: str,
        donde: Optional[Union[int, str]] = None,
        confirmados: Iterable[str] = (),
    ) -> Tuple[PropuestaDeContratacion, ResultadoContratacion]:
        """Propone y, si nada pide confirmación, contrata lo que se propuso. Con algo sin confirmar, `ContratacionPendiente`."""
        p = self.proponer(presupuesto, rol, usuario, donde, confirmados)
        if not p.aplicable:
            raise ContratacionPendiente(
                f"{len(p.pendientes)} concepto(s) piden confirmación antes de contratar {p.ruta}: " + ", ".join(x.clave for x in p.pendientes[:10]), p)
        return p, self.repo.contratar(p.plan)


# --------------------------------------------------------------------------- el informe, para quien decide


MOTIVOS_DE_CONTRATACION = {
    PU_MOVIO: "el PU se movió más de 5 %: pide confirmación",
    SIN_MATRIZ: "no tiene matriz: vale cero y se contrataría así",
}


def informe_de_contratacion(p: PropuestaDeContratacion, *, tope: int = 20) -> str:
    se_mueven = [c for c in p.conceptos if c.cambia]
    o = [f"Contratar {p.ruta} — {p.descripcion.strip()} (presupuesto {p.presupuesto_clave})", "",
         f"  {len(p.conceptos)} conceptos en {p.renglones} renglones se fijan a hoy"
         + (f" ({p.ya_contratados} renglones de bloques de abajo ya estaban contratados y no se tocan)" if p.ya_contratados else ""),
         f"  {len(p.plan.versiones_nuevas)} versiones nuevas (la misma receta, con el PU de hoy) · {len(p.plan.renglones)} renglones cambian de versión",
         f"  el bloque suma {p.total_antes:,.2f} y quedará en {p.total_despues:,.2f}"
         + (f" ({'+' if p.diferencia > 0 else ''}{p.diferencia:,.2f})" if p.diferencia else " — no cambia")]
    if se_mueven:
        o += ["", "PU que se mueven al contratar"]
        o += [f"  {c.clave:<12} {c.pu_fijado:,.2f} → {c.pu_hoy:,.2f}  (versión {c.version_fijada} → {c.version_vigente}"
              + (" y nueva" if c.accion == VERSION_NUEVA else "") + ")" for c in se_mueven[:tope]]
        if len(se_mueven) > tope:
            o.append(f"  … y {len(se_mueven) - tope} más")
    if p.pendientes:
        o += ["", "Piden confirmación (no se contrata hasta que alguien la dé)"]
        o += [f"  {x.clave:<12} {MOTIVOS_DE_CONTRATACION.get(x.motivo, x.motivo)}: {x.detalle}" for x in p.pendientes[:tope]]
        if len(p.pendientes) > tope:
            o.append(f"  … y {len(p.pendientes) - tope} más")
    return "\n".join(o)
