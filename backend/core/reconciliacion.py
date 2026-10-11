"""
Reconciliar un presupuesto que ya existe — `CONOCIMIENTO.md` §1.4 («en diseño renumera libre; contratado, congelado»), §2.3 y §2.9, D-476.

Un presupuesto guardado llega otra vez con otras cantidades, con renglones nuevos o sin renglones que tenía. D-473 decía que no lo
tocaba y que lo diría; ahora lo reconcilia, con las reglas del cerebro:

- **Se casa por la ruta natural, no por posición** (§2.3): un bloque por su `clave#n` de la raíz a él; un renglón por su bloque y su
  clave, la n-ésima vez que se nombra. Es lo mismo con lo que se cuelga el programa (D-474), así que **un renglón que sigue siendo el
  mismo conserva su identidad** y el programa no se entera de que cambió su cantidad.
- **En diseño se aplica, con historia:** una cantidad distinta actualiza el renglón; un renglón o un bloque nuevo entra, con la versión
  vigente de su concepto; el lugar entre los hermanos sigue el del archivo.
- **Una baja pide confirmación y no borra** (el programa la puede citar): el renglón queda dado de baja con su carga; mientras nadie la
  confirme sigue en el presupuesto y la carga lo dice. Un bloque que se va se lleva todo lo que cuelga de él, con una sola confirmación.
- **Lo contratado no se toca** (§1.4, D-475): ni una cantidad, ni un renglón nuevo, ni una baja dentro de un bloque contratado, ni un
  bloque que contenga a uno contratado. Se dice y va a control de cambio, que agrega y no edita (§13.4).
- **Lo que depende de algo detenido espera:** un renglón nuevo cuyo concepto quedó pendiente, y el bloque nuevo que lo contiene.
- **Lo que no se aplica no se pierde ni se aplica a medias:** queda en la carga con su motivo.

Es una función pura: recibe el capítulo que llegó y el presupuesto guardado y devuelve el plan y la lista de cambios. No escribe nada.
"""
from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from decimal import Decimal
from typing import Callable, Dict, FrozenSet, List, Optional, Set, Tuple

from .catalogo import (
    BAJA_SIN_CONFIRMAR,
    CONCEPTO_PENDIENTE,
    AltaPlan,
    CambioDePresupuesto,
    DatosDePresupuesto,
    EN_CONTRATADO,
    LineaDePresupuesto,
    ReconciliacionPlan,
    _rutas_naturales,
)
from .importacion_opus import Capitulo, FilaPresupuesto

UNO = Decimal("1")
DETALLE_DE_CONTRATADO = "está en un bloque contratado: va a control de cambio"


def id_de_renglon(ruta_del_bloque: str, clave: str, n: int) -> str:
    """Con lo que se nombra un renglón al confirmar su baja: su bloque, su clave y qué vez es."""
    return f"{ruta_del_bloque}::{clave}#{n}"


@dataclass
class _Alta:
    indice: int
    fila: FilaPresupuesto
    padre_id: Optional[int]  # el bloque guardado en que entra…
    padre_alta: Optional[int]  # …o el bloque nuevo
    ruta: str  # la ruta natural, si es un bloque
    detenida: Optional[Tuple[str, str]] = None  # (motivo, detalle)


def reconciliar(
    cap: Capitulo,
    guardado: DatosDePresupuesto,
    contratados: FrozenSet[int],
    *,
    huella_del_archivo: str,
    concepto_detenido: Callable[[str], Optional[str]],
    bajas_confirmadas: FrozenSet[str] = frozenset(),
    todas_las_bajas: bool = False,
) -> Tuple[ReconciliacionPlan, Tuple[CambioDePresupuesto, ...]]:
    """Qué hay que hacerle a `guardado` para que sea `cap`, y qué de eso se puede.

    `contratados` son los bloques contratados y todos los que cuelgan de ellos. `concepto_detenido(clave)` dice por qué un concepto no
    puede entrar hoy a un presupuesto (nulo si puede). `bajas_confirmadas` son los `id` de las bajas que alguien ya confirmó."""
    presupuesto = guardado.resumen.clave
    rutas = _rutas_naturales(cap.filas)
    nodos = guardado.nodos
    por_ruta: Dict[str, int] = {n.ruta_natural: n.id for n in nodos.values() if n.estructural}
    ruta_de: Dict[int, str] = {n.id: n.ruta_natural for n in nodos.values() if n.estructural}
    vivas: Dict[int, List[LineaDePresupuesto]] = defaultdict(list)
    for l in guardado.lineas:
        vivas[l.padre_id].append(l)
    for ls in vivas.values():
        ls.sort(key=lambda l: l.orden)
    linea_por_id = {l.id: l for l in guardado.lineas}
    hijos_archivo: Dict[Optional[int], List[FilaPresupuesto]] = defaultdict(list)
    for f in cap.filas:
        hijos_archivo[f.padre].append(f)

    def ocurrencia(l: LineaDePresupuesto) -> int:
        """Qué vez es este renglón entre los de su bloque que nombran el mismo concepto, en el orden guardado."""
        clave = nodos[l.hijo_id].clave
        return 1 + sum(1 for x in vivas[l.padre_id] if x.orden < l.orden and not nodos[x.hijo_id].estructural and nodos[x.hijo_id].clave == clave)

    def identificar(l: LineaDePresupuesto) -> str:
        h = nodos[l.hijo_id]
        return ruta_de[h.id] if h.estructural else id_de_renglon(ruta_de.get(l.padre_id, ""), h.clave, ocurrencia(l))

    # ---- 1. casar lo que trae el archivo con lo guardado
    cantidades: List[Tuple[LineaDePresupuesto, Decimal]] = []
    altas: List[_Alta] = []
    casadas: Set[int] = set()  # renglones guardados que el archivo también trae
    bloques_casados: Set[int] = set()
    secuencia: Dict[int, List[Tuple[str, int]]] = defaultdict(list)  # bloque guardado → lo que el archivo pone en él: ("linea", id) | ("alta", índice)

    def cantidad_nueva(f: FilaPresupuesto) -> Decimal:
        return f.cantidad if f.cantidad is not None else UNO

    def nueva_alta(f: FilaPresupuesto, padre_id: Optional[int], padre_alta: Optional[int]) -> _Alta:
        a = _Alta(len(altas), f, padre_id, padre_alta, rutas.get(f.posicion, ""))
        altas.append(a)
        return a

    def visita(fila: FilaPresupuesto, bloque_id: Optional[int], bloque_alta: Optional[int]) -> None:
        veces: Dict[str, int] = defaultdict(int)
        for h in hijos_archivo.get(fila.posicion, ()):
            linea: Optional[LineaDePresupuesto] = None
            if bloque_id is not None:
                if h.es_concepto:
                    veces[h.clave] += 1
                    propias = [l for l in vivas.get(bloque_id, ()) if not nodos[l.hijo_id].estructural and nodos[l.hijo_id].clave == h.clave]
                    if veces[h.clave] <= len(propias):
                        linea = propias[veces[h.clave] - 1]
                else:
                    nid = por_ruta.get(rutas[h.posicion])
                    linea = next((l for l in vivas.get(bloque_id, ()) if l.hijo_id == nid), None) if nid is not None else None
            if linea is not None:
                casadas.add(linea.id)
                secuencia[bloque_id].append(("linea", linea.id))
                if cantidad_nueva(h) != linea.cantidad:
                    cantidades.append((linea, cantidad_nueva(h)))
                if not h.es_concepto:
                    bloques_casados.add(linea.hijo_id)
                    visita(h, linea.hijo_id, None)
                continue
            a = nueva_alta(h, bloque_id, bloque_alta)
            if bloque_id is not None:
                secuencia[bloque_id].append(("alta", a.indice))
            if not h.es_concepto:
                visita(h, None, a.indice)

    raiz_id = por_ruta.get(rutas[cap.raiz.posicion])
    if raiz_id != guardado.raiz_id:
        raise ValueError(f"el capítulo {cap.raiz.clave} no es la raíz del presupuesto guardado")
    bloques_casados.add(raiz_id)
    visita(cap.raiz, raiz_id, None)

    # ---- 2. lo guardado que el archivo ya no trae: cada baja es lo más alto que se va, y se lleva lo que cuelga de ello
    def debajo(bloque_id: int) -> List[LineaDePresupuesto]:
        out: List[LineaDePresupuesto] = []
        for l in vivas.get(bloque_id, ()):
            out.append(l)
            if nodos[l.hijo_id].estructural:
                out += debajo(l.hijo_id)
        return out

    cambios: List[CambioDePresupuesto] = []

    # ---- 3. las cantidades
    plan_cantidades: List[Tuple[int, Decimal, Decimal]] = []
    for l, nueva in cantidades:
        h = nodos[l.hijo_id]
        if l.padre_id in contratados:
            cambios.append(CambioDePresupuesto(presupuesto, "cantidad", identificar(l), h.clave, h.descripcion, h.estructural, l.cantidad, nueva,
                                               "detenido", EN_CONTRATADO, DETALLE_DE_CONTRATADO))
        else:
            plan_cantidades.append((l.id, l.cantidad, nueva))
            cambios.append(CambioDePresupuesto(presupuesto, "cantidad", identificar(l), h.clave, h.descripcion, h.estructural, l.cantidad, nueva, "aplica"))

    # ---- 4. las altas: un bloque nuevo entra entero o no entra
    hijas: Dict[int, List[_Alta]] = defaultdict(list)
    for a in altas:
        if a.padre_alta is not None:
            hijas[a.padre_alta].append(a)

    def conceptos_de(a: _Alta) -> List[_Alta]:
        return ([a] if a.fila.es_concepto else []) + [c for h in hijas.get(a.indice, ()) for c in conceptos_de(h)]

    def detener(a: _Alta, motivo: str, detalle: str) -> None:
        a.detenida = (motivo, detalle)
        for h in hijas.get(a.indice, ()):
            detener(h, motivo, detalle)

    for a in altas:
        if a.padre_alta is not None:
            continue  # lo decide el bloque nuevo de que cuelga
        if a.padre_id in contratados:
            detener(a, EN_CONTRATADO, DETALLE_DE_CONTRATADO)
            continue
        for c in conceptos_de(a):
            motivo = concepto_detenido(c.fila.clave)
            if motivo is not None:
                detener(a, CONCEPTO_PENDIENTE, motivo)
                break

    def renglones_de(a: _Alta) -> int:
        return len(conceptos_de(a))

    for a in altas:
        if a.padre_alta is not None:
            continue
        if a.fila.es_concepto:
            n = 1 + sum(1 for b in altas if b.indice < a.indice and b.fila.es_concepto and b.fila.clave == a.fila.clave and b.padre_id == a.padre_id)
            ident = id_de_renglon(ruta_de[a.padre_id], a.fila.clave, len([l for l in vivas.get(a.padre_id, ()) if not nodos[l.hijo_id].estructural
                                                                         and nodos[l.hijo_id].clave == a.fila.clave]) + n)
        else:
            ident = a.ruta
        detalle = "" if a.fila.es_concepto else f"{renglones_de(a)} renglones"
        estado, motivo = ("aplica", "") if a.detenida is None else ("detenido", a.detenida[0])
        if a.detenida is not None:
            detalle = a.detenida[1]
        cambios.append(CambioDePresupuesto(presupuesto, "alta", ident, a.fila.clave, a.fila.descripcion, not a.fila.es_concepto, None,
                                           cantidad_nueva(a.fila), estado, motivo, detalle))

    # ---- 5. las bajas
    baja_lineas: List[int] = []
    baja_bloques: List[int] = []
    for bloque_id in sorted(bloques_casados):
        for l in vivas.get(bloque_id, ()):
            if l.id in casadas:
                continue
            h = nodos[l.hijo_id]
            se_van = [l] + (debajo(h.id) if h.estructural else [])
            ident = identificar(l)
            toca_lo_contratado = bloque_id in contratados or any(
                nodos[x.hijo_id].estructural and x.hijo_id in contratados for x in se_van)
            citas = dict(renglones=tuple(x.id for x in se_van), bloques=tuple(x.hijo_id for x in se_van if nodos[x.hijo_id].estructural))
            if toca_lo_contratado:
                cambios.append(CambioDePresupuesto(presupuesto, "baja", ident, h.clave, h.descripcion, h.estructural, l.cantidad, None,
                                                   "detenido", EN_CONTRATADO, DETALLE_DE_CONTRATADO, **citas))
            elif not (todas_las_bajas or ident in bajas_confirmadas):
                detalle = "el archivo ya no lo trae: darlo de baja pide confirmación"
                if len(se_van) > 1:
                    detalle += f" (con él se van {len(se_van) - 1} renglones y bloques de abajo)"
                cambios.append(CambioDePresupuesto(presupuesto, "baja", ident, h.clave, h.descripcion, h.estructural, l.cantidad, None,
                                                   "detenido", BAJA_SIN_CONFIRMAR, detalle, **citas))
            else:
                baja_lineas += [x.id for x in se_van]
                baja_bloques += [x.hijo_id for x in se_van if nodos[x.hijo_id].estructural]
                cambios.append(CambioDePresupuesto(presupuesto, "baja", ident, h.clave, h.descripcion, h.estructural, l.cantidad, None, "aplica",
                                                   detalle=f"{len(se_van)} renglones y bloques" if len(se_van) > 1 else "", **citas))

    # ---- 6. el lugar entre los hermanos, en cada bloque guardado que no está contratado
    se_van_ya = set(baja_lineas)
    aplicadas = {a.indice for a in altas if a.detenida is None}
    ordenes: List[Tuple[int, int, int]] = []
    orden_de_alta: Dict[int, int] = {}
    for bloque_id, seq in secuencia.items():
        if bloque_id in contratados:
            continue
        actuales = vivas.get(bloque_id, [])
        final: List[Tuple[str, int]] = [x for x in seq if x[0] == "linea" or x[1] in aplicadas]  # lo que el archivo pone, en su orden
        # lo que el archivo ya no trae y no se da de baja (todavía) se queda donde estaba: justo después de lo que lo precedía
        previo: Optional[Tuple[str, int]] = None
        for l in actuales:
            if l.id in se_van_ya:
                continue
            if l.id in casadas:
                previo = ("linea", l.id)
                continue
            lugar = 0 if previo is None else final.index(previo) + 1
            final.insert(lugar, ("linea", l.id))
            previo = ("linea", l.id)
        antes = [("linea", l.id) for l in actuales if l.id not in se_van_ya]
        hay_alta = any(x[0] == "alta" for x in final)
        if not hay_alta and [x for x in final if x[0] == "linea"] == antes:
            continue  # nada entra y el orden relativo es el de siempre: los huecos que dejan las bajas no estorban
        lugar_actual = {l.id: l.orden for l in actuales}
        for i, (clase, ref) in enumerate(final, start=1):
            if clase == "alta":
                orden_de_alta[ref] = i
            elif lugar_actual[ref] != i:
                ordenes.append((ref, lugar_actual[ref], i))
    for padre, hs in hijas.items():
        siguientes = 0
        for h in sorted(hs, key=lambda x: x.indice):
            if h.detenida is None:
                siguientes += 1
                orden_de_alta[h.indice] = siguientes

    plan_altas = tuple(
        AltaPlan(a.indice, a.padre_id, a.padre_alta, a.fila.tipo, a.fila.nivel, a.fila.clave, a.fila.descripcion, a.fila.unidad,
                 cantidad_nueva(a.fila), "" if a.fila.es_concepto else a.ruta, orden_de_alta.get(a.indice, 1))
        for a in altas if a.detenida is None)
    completa = not any(c.estado == "detenido" for c in cambios)
    plan = ReconciliacionPlan(
        guardado.resumen.id, presupuesto, huella_del_archivo if completa else "", tuple(plan_cantidades), plan_altas,
        tuple(baja_lineas), tuple(baja_bloques), tuple(ordenes))
    return plan, tuple(cambios)
