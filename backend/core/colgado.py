"""
Colgar el programa del presupuesto — `1-mundo/MODELO.md` §5c (`ACTIVIDAD.concepto_id` y `presupuesto_id`), D-474.

Hasta aquí el programa citaba sus filas por `oid` y el presupuesto vivía aparte. Colgar es decir, fila por fila, **a qué parte del
presupuesto se refiere**: un bloque (capítulo, subcapítulo, nivel 2 o 3) a un nodo estructural; una partida a un **renglón**, que es
la línea del bloque al concepto —el mismo concepto está en muchos lugares de un presupuesto y cada lugar tiene su cantidad—.

**Cómo se casan** (nada se adivina, nada se alinea por número de fila):

- Un bloque se casa por su **ruta natural**: `clave#n` de la raíz a él, donde `n` es el lugar entre los hermanos que se llaman igual
  (`CONOCIMIENTO.md` §2.3). Es la misma ruta que guardó la carga del presupuesto (D-473), así que no depende del orden del archivo
  ni de que se inserten filas.
- Una partida se casa por su **bloque y su clave**: dentro del bloque que ya se casó, la `n`-ésima vez que el programa nombra esa
  clave es la `n`-ésima línea del presupuesto con ese concepto, en el orden del presupuesto.
- Un renglón **sin clave y sin descripción** es un marcador vacío de OPUS (`CONOCIMIENTO.md` §2.5): el programa los trae donde OPUS los
  dejó, la carga del presupuesto los descartó (D-473) y aquí no se enlazan ni se cuentan como faltantes; solo se cuentan.
- Lo que no tiene con qué casarse **se queda sin enlace y se dice**, de los dos lados: lo que el programa tiene y el presupuesto no
  (un concepto que se programó y no se presupuestó) y lo que el presupuesto tiene y el programa no (dinero sin fecha).

El sistema propone y el humano decide: `proponer` no escribe nada; `colgar` escribe lo que `proponer` mostró. Si el programa casa
menos de la mitad de sus conceptos con el presupuesto, casi seguro es el presupuesto equivocado y no se cuelga, salvo que quien
decide lo diga (`forzar`). Un enlace puesto no se mueve; uno nuevo se agrega (así, al crecer el presupuesto, se vuelve a colgar y
se completan los que faltaban).
"""
from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, replace
from typing import Any, Dict, List, Mapping, Optional, Sequence, Set, Tuple

from .catalogo import DatosDePresupuesto, LineaDePresupuesto, RepositorioCatalogo
from .programa import Fila
from .servicio_programa import Enlace, Roles, ServicioPrograma, YaColgado

# Subir un programa y colgarlo piden lo mismo: es estructura (`MODELO.md` §5b). No se inventa una función sin un caso que la pida.
FUNCION_DE_COLGAR = "editar_estructura_programa"
MITAD = 2  # se cuelga si casa al menos 1/MITAD de los conceptos del programa
MARCADOR = "\0vacio"  # la «ruta» de un bloque sin clave: no se parece a ninguna ruta natural
TOPE_DEL_RESUMEN = 100  # lo que se guarda de cada lista; el total siempre se guarda

BLOQUE_SIN_PAR = "bloque_sin_par"  # el presupuesto no tiene ese bloque en esa ruta
SIN_SU_BLOQUE = "sin_su_bloque"  # el concepto está bajo un bloque que no se casó
CONCEPTO_SIN_PAR = "concepto_sin_par"  # el bloque se casó pero el presupuesto no tiene ese concepto ahí
SIN_CLAVE = "sin_clave"  # trae descripción pero no clave: sin clave no hay con qué casarlo
REPETIDO_DE_MAS = "repetido_de_mas"  # el programa nombra el concepto más veces de las que el presupuesto lo tiene en el bloque

TEXTO_DEL_MOTIVO = {
    SIN_CLAVE: "trae descripción pero no clave, y sin clave no se puede casar",
    BLOQUE_SIN_PAR: "el presupuesto no tiene ese bloque en esa ruta",
    SIN_SU_BLOQUE: "está bajo un bloque que no está en el presupuesto",
    CONCEPTO_SIN_PAR: "el presupuesto no tiene ese concepto en ese bloque",
    REPETIDO_DE_MAS: "el programa lo nombra más veces de las que el presupuesto lo tiene en ese bloque",
}


class ColgadoNoCuadra(Exception):
    """El programa no se puede colgar de ese presupuesto, y por qué. Si hubo alineación, va con ella."""

    def __init__(self, mensaje: str, alineacion: Optional["Alineacion"] = None) -> None:
        super().__init__(mensaje)
        self.alineacion = alineacion


@dataclass(frozen=True)
class SinPar:
    """Una fila del programa que no tiene con qué casarse en el presupuesto."""

    oid: str
    fila: int
    tipo: str
    clave: str
    descripcion: str
    motivo: str


@dataclass(frozen=True)
class SinProgramar:
    """Algo del presupuesto que ninguna fila del programa reclamó: dinero sin fecha."""

    clave: str
    descripcion: str
    ruta: str  # la ruta natural del bloque (o del bloque en que está el renglón)
    cantidad: Optional[str] = None  # de un renglón; vacía en un bloque
    renglon: bool = False


@dataclass(frozen=True)
class Alineacion:
    programa_id: int
    presupuesto_id: int
    presupuesto_clave: str
    enlaces: Tuple[Enlace, ...]  # todos los que cuadran, también los que el programa ya tenía puestos
    bloques: int
    partidas: int
    conceptos_del_programa: int
    bloques_del_programa: int
    sin_par: Tuple[SinPar, ...]
    sin_programar: Tuple[SinProgramar, ...]
    vacias: int = 0  # los marcadores vacíos de OPUS que el programa trae: no cuentan ni como casados ni como faltantes
    ya_estaban: int = 0  # de `enlaces`, los que ya estaban puestos tal cual
    se_moverian: Tuple[str, ...] = ()  # los `oid` cuyo enlace puesto es otro: no se mueven, se dice y no se cuelga
    nuevos: int = 0  # lo que `colgar` puso

    @property
    def casan_los_conceptos(self) -> float:
        return 1.0 if self.conceptos_del_programa == 0 else self.partidas / self.conceptos_del_programa

    @property
    def casa_bien(self) -> bool:
        return self.partidas > 0 and self.partidas * MITAD >= self.conceptos_del_programa

    def resumen(self, forzado: bool = False) -> Dict[str, Any]:
        """Lo que se guarda en la bitácora de colgaduras: qué cuadró y qué no, de los dos lados."""
        return {
            "presupuesto": self.presupuesto_clave,
            "bloques": self.bloques,
            "partidas": self.partidas,
            "conceptos_del_programa": self.conceptos_del_programa,
            "marcadores_vacios": self.vacias,
            "ya_estaban": self.ya_estaban,
            "forzado": forzado,
            "programa_sin_par_total": len(self.sin_par),
            "programa_sin_par": [
                {"oid": s.oid, "fila": s.fila, "tipo": s.tipo, "clave": s.clave, "motivo": s.motivo} for s in self.sin_par[:TOPE_DEL_RESUMEN]
            ],
            "presupuesto_sin_programa_total": len(self.sin_programar),
            "presupuesto_sin_programa": [
                {"clave": s.clave, "ruta": s.ruta, "cantidad": s.cantidad, "renglon": s.renglon} for s in self.sin_programar[:TOPE_DEL_RESUMEN]
            ],
        }


# --------------------------------------------------------------------------- alinear: puro


def alinear(
    filas: Sequence[Fila], datos: DatosDePresupuesto, puestos: Optional[Mapping[str, Enlace]] = None, *, programa_id: int = 0,
) -> Alineacion:
    """Casa las filas de un programa con un presupuesto guardado. No lee ni escribe nada; `puestos` son los enlaces que el programa
    ya tiene (por `oid`), para decir cuáles ya estaban y cuáles se moverían."""
    puestos = puestos or {}
    por_ruta: Dict[str, int] = {n.ruta_natural: n.id for n in datos.nodos.values() if n.estructural}
    ruta_de: Dict[int, str] = {n.id: n.ruta_natural for n in datos.nodos.values() if n.estructural}
    renglones: Dict[int, List[LineaDePresupuesto]] = defaultdict(list)
    for l in datos.lineas:
        if not datos.nodos[l.hijo_id].estructural:
            renglones[l.padre_id].append(l)
    for ls in renglones.values():
        ls.sort(key=lambda l: l.orden)

    enlaces: List[Enlace] = []
    sin_par: List[SinPar] = []
    nodos_casados: Set[int] = set()
    renglones_casados: Set[int] = set()
    pila: List[Tuple[int, str, Optional[int]]] = []  # (nivel, ruta natural, nodo) de la raíz al bloque en que va el programa
    hermanos: Dict[Tuple[str, str], int] = defaultdict(int)  # bloques con la misma clave bajo el mismo padre
    veces: Dict[Tuple[str, str], int] = defaultdict(int)  # conceptos con la misma clave en el mismo bloque
    conceptos = bloques = vacias = 0

    for f in filas:
        while pila and pila[-1][0] >= f.nivel:
            pila.pop()
        padre_ruta, padre_nodo = (pila[-1][1], pila[-1][2]) if pila else ("", None)
        if not f.clave.strip():
            if not f.descripcion.strip():
                vacias += 1
                if f.tipo != "Concepto":
                    pila.append((f.nivel, MARCADOR, None))  # lo que cuelgue de un marcador vacío no tiene con qué casarse
                continue
            sin_par.append(SinPar(f.llave, f.fila, f.tipo, f.clave, f.descripcion, SIN_CLAVE))
            conceptos += f.tipo == "Concepto"
            bloques += f.tipo != "Concepto"
            if f.tipo != "Concepto":
                pila.append((f.nivel, MARCADOR, None))
            continue
        if f.tipo != "Concepto":
            bloques += 1
            hermanos[(padre_ruta, f.clave)] += 1
            segmento = f"{f.clave}#{hermanos[(padre_ruta, f.clave)]}"
            ruta = f"{padre_ruta}/{segmento}" if padre_ruta else segmento
            nodo = por_ruta.get(ruta)
            pila.append((f.nivel, ruta, nodo))
            if nodo is None or nodo in nodos_casados:
                sin_par.append(SinPar(f.llave, f.fila, f.tipo, f.clave, f.descripcion, BLOQUE_SIN_PAR))
            else:
                nodos_casados.add(nodo)
                enlaces.append(Enlace(f.llave, nodo_id=nodo))
            continue
        conceptos += 1
        veces[(padre_ruta, f.clave)] += 1
        if padre_nodo is None:
            sin_par.append(SinPar(f.llave, f.fila, f.tipo, f.clave, f.descripcion, SIN_SU_BLOQUE))
            continue
        propias = [l for l in renglones.get(padre_nodo, ()) if datos.nodos[l.hijo_id].clave == f.clave]
        n = veces[(padre_ruta, f.clave)]
        if not propias:
            sin_par.append(SinPar(f.llave, f.fila, f.tipo, f.clave, f.descripcion, CONCEPTO_SIN_PAR))
        elif n > len(propias):
            sin_par.append(SinPar(f.llave, f.fila, f.tipo, f.clave, f.descripcion, REPETIDO_DE_MAS))
        else:
            renglon = propias[n - 1]
            if renglon.id <= 0:
                raise ValueError(f"el renglón de {f.clave} en {padre_ruta} no trae su id: no se puede enlazar")
            renglones_casados.add(renglon.id)
            enlaces.append(Enlace(f.llave, renglon_id=renglon.id))

    sin_programar: List[SinProgramar] = []
    for n in datos.nodos.values():
        if n.estructural and n.id not in nodos_casados:
            sin_programar.append(SinProgramar(n.clave, n.descripcion, n.ruta_natural))
    for padre, ls in renglones.items():
        for l in ls:
            if l.id not in renglones_casados:
                h = datos.nodos[l.hijo_id]
                sin_programar.append(SinProgramar(h.clave, h.descripcion, ruta_de.get(padre, ""), format(l.cantidad.normalize(), "f"), True))
    sin_programar.sort(key=lambda s: (s.ruta, s.clave))

    ya = [e for e in enlaces if puestos.get(e.oid) == e]
    mueven = tuple(e.oid for e in enlaces if e.oid in puestos and puestos[e.oid] != e)
    return Alineacion(
        programa_id=programa_id,
        presupuesto_id=datos.resumen.id,
        presupuesto_clave=datos.resumen.clave,
        enlaces=tuple(enlaces),
        bloques=sum(e.nodo_id is not None for e in enlaces),
        partidas=sum(e.renglon_id is not None for e in enlaces),
        conceptos_del_programa=conceptos,
        bloques_del_programa=bloques,
        sin_par=tuple(sin_par),
        sin_programar=tuple(sin_programar),
        vacias=vacias,
        ya_estaban=len(ya),
        se_moverian=mueven,
    )


# --------------------------------------------------------------------------- el servicio


class ServicioColgado:
    """Colgar un programa guardado de un presupuesto guardado, con quien decide y con el permiso de editar la estructura."""

    def __init__(self, programas: ServicioPrograma, catalogo: RepositorioCatalogo) -> None:
        self.programas = programas
        self.catalogo = catalogo

    def _presupuesto(self, programa_id: int, presupuesto_id: Optional[int], colgado_de: Optional[int], filas: Sequence[Fila]) -> int:
        if colgado_de is not None:
            if presupuesto_id is not None and presupuesto_id != colgado_de:
                raise YaColgado(f"el programa {programa_id} ya cuelga del presupuesto {colgado_de}: no se cambia, se sube otro programa", colgado_de)
            return colgado_de
        todos = self.catalogo.presupuestos()
        if presupuesto_id is not None:
            if presupuesto_id not in {p.id for p in todos}:
                raise ColgadoNoCuadra(f"no hay presupuesto {presupuesto_id}")
            return presupuesto_id
        raiz = next((f for f in filas if f.tipo == "Capítulo"), None)
        if raiz is None:
            raise ColgadoNoCuadra(f"el programa {programa_id} no trae ningún capítulo: no se sabe de qué presupuesto es")
        # la clave del capítulo es la del presupuesto (es con lo que se reconoce al volver a cargar, D-473)
        hallado = [p for p in todos if p.clave == raiz.clave]
        if not hallado:
            raise ColgadoNoCuadra(f"el programa abre con el capítulo {raiz.clave} y no hay presupuesto con esa clave: cárgalo primero o di cuál es")
        return hallado[0].id

    def proponer(self, programa_id: int, rol: Roles, presupuesto_id: Optional[int] = None) -> Alineacion:
        """Cómo quedaría colgado. No escribe nada."""
        self.programas.rol_para(FUNCION_DE_COLGAR, rol)
        g = self.programas.repo.leer_programa(programa_id)
        ServicioPrograma._abierto(g)
        elegido = self._presupuesto(programa_id, presupuesto_id, g.presupuesto_id, g.filas)
        a = alinear(g.filas, self.catalogo.datos_de_presupuesto(elegido), {e.oid: e for e in g.enlaces}, programa_id=programa_id)
        return a

    def colgar(self, programa_id: int, rol: Roles, usuario: str, presupuesto_id: Optional[int] = None, forzar: bool = False) -> Alineacion:
        """Propone y, si cuadra, guarda lo que se propuso. Devuelve la alineación con los enlaces nuevos que puso (`nuevos`)."""
        if not usuario:
            raise ValueError("todo colgado dice quién lo hizo")
        rol_con_que = self.programas.rol_para(FUNCION_DE_COLGAR, rol)
        a = self.proponer(programa_id, rol, presupuesto_id)
        if a.se_moverian:
            raise YaColgado(
                f"{len(a.se_moverian)} fila(s) del programa {programa_id} ya están enlazadas a otra cosa ({', '.join(a.se_moverian[:5])}…): "
                "un enlace puesto no se mueve", a.presupuesto_id)
        if not a.enlaces:
            raise ColgadoNoCuadra(
                f"ninguna fila del programa {programa_id} casa con el presupuesto {a.presupuesto_clave}: no hay nada que colgar", a)
        if not a.casa_bien and not forzar:
            raise ColgadoNoCuadra(
                f"solo {a.partidas} de {a.conceptos_del_programa} conceptos del programa casan con el presupuesto {a.presupuesto_clave}: "
                "casi seguro es otro presupuesto. Si de todos modos es ése, confírmalo.", a)
        nuevos = self.programas.repo.colgar(
            programa_id, a.presupuesto_id, a.enlaces, usuario=usuario, rol=rol_con_que, resumen=a.resumen(forzado=forzar and not a.casa_bien))
        return replace(a, nuevos=nuevos)


# --------------------------------------------------------------------------- el informe, para quien decide


def informe_de_colgado(a: Alineacion, *, tope: int = 20) -> str:
    """Lo que se le muestra a quien decide: qué casó y qué no, de los dos lados."""
    L = [f"Programa {a.programa_id} contra el presupuesto {a.presupuesto_clave}:",
         f"  casan {a.bloques} de {a.bloques_del_programa} bloques y {a.partidas} de {a.conceptos_del_programa} conceptos."]
    if a.vacias:
        L.append(f"  {a.vacias} marcador(es) vacío(s) de OPUS (sin clave ni descripción) que no se enlazan.")
    if a.ya_estaban:
        L.append(f"  {a.ya_estaban} enlace(s) ya estaban puestos.")
    if a.sin_par:
        L.append(f"\nEl programa tiene {len(a.sin_par)} fila(s) que el presupuesto no tiene (quedan sin enlace):")
        for s in a.sin_par[:tope]:
            L.append(f"  fila {s.fila}  {s.tipo}  {s.clave}  {s.descripcion} — {TEXTO_DEL_MOTIVO.get(s.motivo, s.motivo)}")
        if len(a.sin_par) > tope:
            L.append(f"  … y {len(a.sin_par) - tope} más")
    if a.sin_programar:
        L.append(f"\nEl presupuesto tiene {len(a.sin_programar)} renglón(es) o bloque(s) que el programa no tiene (dinero sin fecha):")
        for s in a.sin_programar[:tope]:
            cuanto = f" × {s.cantidad}" if s.renglon else ""
            L.append(f"  {s.clave}{cuanto}  {s.descripcion} — en {s.ruta}")
        if len(a.sin_programar) > tope:
            L.append(f"  … y {len(a.sin_programar) - tope} más")
    if not a.sin_par and not a.sin_programar:
        L.append("  cuadra completo, de los dos lados.")
    if a.nuevos:
        L.append(f"\nSe pusieron {a.nuevos} enlace(s) nuevos.")
    return "\n".join(L)
