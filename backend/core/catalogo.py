"""
Persistir el catálogo, las matrices y los presupuestos de OPUS — `CONOCIMIENTO.md` §2.2 a §2.9, `MODELO.md` §1, §1a, §3 y §4.

Lo que `importacion_opus.py` lee y compara, aquí se **aplica**: el paso 5 de la secuencia de §2.9, «se aplica, todo junto».
El orden de siempre: se lee el archivo, se compara contra lo vigente, se muestra el diagnóstico, y solo entonces se escribe.

    revisar(...)  →  (DiagnosticoDeCarga, PlanDeCarga)      no escribe nada
    aplicar(...)  →  ResultadoCarga                         escribe el plan, en una sola transacción

**Lo que se detiene no es la carga: son los conceptos en conflicto; el resto entra normal** (§2.9). Un concepto se detiene,
con su motivo, si cambió su unidad (§2.7), si su PU se movió más de 5 % y nadie lo confirmó (§2.2), si depende de algo que
se detuvo, o si es un trabajo cuyo precio cambió (§4a: ahí «un cambio de precio dispara validar o descartar»). Lo detenido
queda en la carga, con su motivo, y no se aplica a medias: «entonces nadie sabe que faltan tres».

Reglas que aquí se hacen concretas:
- **Cualquier cambio en los insumos o en sus cantidades es una versión nueva, sin umbral y sola** (§2.2). La descripción y los
  precios no cuentan: un precio que se mueve es una fila de `PRECIO_HISTORICO`, no una versión de nada.
- **El PU de una versión se congela** al crearse, calculado con el motor sobre el archivo que se carga. Nunca se recalcula.
- **El renglón de un presupuesto fija la versión del concepto** que tenía al cargarse.
- **Un presupuesto que ya existe no se toca.** Si lo que llega es lo mismo, se dice; si es distinto, se dice que cambió y que no
  se aplicó —cómo se reconcilian las cantidades de un presupuesto vivo no está diseñado—. Se reconoce por la clave de su capítulo.
- **El estado del catálogo no cambia entre que se revisa y se aplica**: cada plan trae la última carga que vio, y si ya hay otra,
  `CatalogoCambio` y no se escribe nada (el mismo candado que `programa.version`).

No conoce ninguna base (D-182): el puerto `RepositorioCatalogo` lo cumplen `MemoriaCatalogo` y `infra/postgres_catalogo.py`.
"""
from __future__ import annotations

import hashlib
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from typing import Any, Callable, Dict, FrozenSet, Iterable, List, Mapping, Optional, Protocol, Sequence, Set, Tuple

from .accesos import PermisoDenegado  # noqa: F401  (se re-exporta: quien llama lo captura de aquí)
from .dominio import Categoria, Rol
from .importacion_opus import (
    CATEGORIA_DE_TIPO,
    CargaNoProcede,
    CatalogoLeido,
    Diagnostico,
    FilaPresupuesto,
    LecturaPresupuesto,
    Matrices,
    armar_arbol,
    catalogo_leido,
    diagnosticar,
    leer_matrices,
    leer_presupuesto,
)
from .motor_calculo import CicloError, ArbolEnMemoria, precio_unitario
from .servicio_programa import Roles, rol_efectivo

FUNCION_DE_CARGAR = "cargar_catalogo_opus"
UMBRAL_DE_CONFIRMACION = Decimal("0.05")  # §2.2: si el PU se movió más de 5 %, pide confirmación aunque sea en diseño
TOLERANCIA_DE_PRECIO_OBSERVADO = Decimal("0.005")
TIPOS_DE_PRESUPUESTO = ("plantilla", "obra", "escenario")

# por qué algo quedó pendiente
UNIDAD_CAMBIO = "unidad_cambio"
PRECIO_DE_TRABAJO = "precio_de_trabajo"
PU_MOVIO = "pu_movio_mas_de_5"
DEPENDE_DE = "depende_de"
CONCEPTO_PENDIENTE = "concepto_pendiente"
CONCEPTO_CON_PRECIO_Y_SIN_MATRIZ = "concepto_con_precio_y_sin_matriz"


class CatalogoCambio(Exception):
    """Otra carga se aplicó entre que se revisó esta y se quiso aplicar: lo que se vio ya no es lo de hoy."""


# --------------------------------------------------------------------------- lo vigente, tal como lo entrega un adaptador


@dataclass(frozen=True)
class InsumoGuardado:
    clave: str
    unidad: str  # vacía si no se sabe
    categoria: str
    precio: Optional[Decimal]  # el vigente (el último de PRECIO_HISTORICO); nulo en los que no tienen precio propio


@dataclass(frozen=True)
class ResumenPresupuesto:
    id: int
    clave: str
    nombre: str
    tipo: str
    huella: str
    carga_id: int
    renglones: int


@dataclass
class EstadoVigente:
    """Lo mínimo del catálogo guardado para decidir qué entra: la unidad y la huella de cada matriz, su PU, los insumos."""

    unidad: Dict[str, str] = field(default_factory=dict)  # padres con o sin matriz → su unidad ("" si no se sabe)
    huella: Dict[str, str] = field(default_factory=dict)  # padres con matriz → la huella de su versión vigente
    pu: Dict[str, Decimal] = field(default_factory=dict)  # padres con matriz → el PU de su versión vigente
    sin_matriz: Set[str] = field(default_factory=set)  # conceptos que existen y no tienen matriz (P-09)
    insumos: Dict[str, InsumoGuardado] = field(default_factory=dict)
    presupuestos: Dict[str, ResumenPresupuesto] = field(default_factory=dict)  # por la clave de su capítulo
    ultima_carga: int = 0

    def como_catalogo(self) -> CatalogoLeido:
        return CatalogoLeido(dict(self.unidad), dict(self.huella), tuple(sorted(self.sin_matriz)))


# --------------------------------------------------------------------------- lo que se escribe


@dataclass(frozen=True)
class LineaPlan:
    hijo: str  # su clave
    cantidad: Decimal
    reporta_a: Categoria
    porcentaje: bool = False  # `(%)mo`: porcentaje sobre la suma de jornales de las demás líneas de la cuadrilla


@dataclass(frozen=True)
class NodoConMatriz:
    """Un concepto, un compuesto o una cuadrilla, con la versión que se crea: su huella, su PU de hoy y sus líneas."""

    clave: str
    descripcion: str
    unidad: str
    rol: Rol
    categoria: Categoria
    huella: str
    pu: Decimal
    lineas: Tuple[LineaPlan, ...]


@dataclass(frozen=True)
class InsumoPlan:
    clave: str
    descripcion: str
    unidad: str
    categoria: Categoria
    precio: Decimal
    con_historico: bool  # el `(%)mo` no tiene precio propio: vale por su porcentaje


@dataclass(frozen=True)
class ConceptoSinMatriz:
    clave: str
    descripcion: str
    unidad: str


@dataclass(frozen=True)
class RenglonPlan:
    posicion: int  # dentro del capítulo, en el orden del archivo
    padre: Optional[int]
    tipo: str  # Capítulo · Subcapítulo · Nivel 2 · Nivel 3 · Concepto
    nivel: int
    clave: str
    descripcion: str
    unidad: str
    cantidad: Decimal
    ruta_natural: str  # solo de los estructurales; vacía en un concepto


@dataclass(frozen=True)
class PresupuestoPlan:
    clave: str
    nombre: str
    tipo: str
    huella: str
    renglones: Tuple[RenglonPlan, ...]


@dataclass(frozen=True)
class PlanDeCarga:
    base: int  # la última carga que vio quien revisó: si hay otra, no se aplica
    usuario: str
    rol: str
    archivos: Mapping[str, str]
    resumen: Mapping[str, Any]
    unidades: Tuple[str, ...]
    insumos_nuevos: Tuple[InsumoPlan, ...] = ()
    precios_nuevos: Tuple[Tuple[str, Decimal], ...] = ()
    unidades_que_se_saben: Tuple[Tuple[str, str], ...] = ()  # (clave, unidad) de lo que existía sin unidad
    nodos_nuevos: Tuple[NodoConMatriz, ...] = ()
    versiones_nuevas: Tuple[NodoConMatriz, ...] = ()
    conceptos_sin_matriz: Tuple[ConceptoSinMatriz, ...] = ()
    presupuestos_nuevos: Tuple[PresupuestoPlan, ...] = ()

    @property
    def cambia_algo(self) -> bool:
        return bool(self.insumos_nuevos or self.precios_nuevos or self.unidades_que_se_saben or self.nodos_nuevos
                    or self.versiones_nuevas or self.conceptos_sin_matriz or self.presupuestos_nuevos)


@dataclass(frozen=True)
class Pendiente:
    clave: str
    motivo: str
    detalle: str


@dataclass(frozen=True)
class EstadoDePresupuesto:
    clave: str
    nombre: str
    estado: str  # nuevo · sin_cambios · cambio_no_aplicado · pendiente
    detalle: str = ""


@dataclass(frozen=True)
class DiagnosticoDeCarga:
    """Lo que se le muestra a quien decide, antes de aplicar nada (§2.9, paso 3)."""

    diagnostico: Diagnostico  # de las matrices: entran · nuevos · versionan · detenidos · ausentes
    insumos_nuevos: int
    precios_que_cambian: Tuple[Tuple[str, Decimal, Decimal], ...]  # (clave, antes, ahora)
    pendientes: Tuple[Pendiente, ...]
    presupuestos: Tuple[EstadoDePresupuesto, ...]
    sin_matriz: Tuple[str, ...]  # conceptos del presupuesto que no traen matriz (P-09)
    sin_unidad: Tuple[str, ...]  # lo que se va a crear sin saber su unidad
    precios_observados_distintos: Tuple[Tuple[str, Decimal, Decimal], ...]  # (clave, el del presupuesto, el calculado)
    avisos: Tuple[str, ...]
    problemas: Tuple[str, ...]  # lo que impide aplicar: el archivo trae algo que no cuadra

    @property
    def aplicable(self) -> bool:
        return not self.problemas


@dataclass(frozen=True)
class ResultadoCarga:
    carga_id: Optional[int]  # nulo si no había nada que escribir ni nada pendiente que dejar dicho
    resumen: Mapping[str, Any]


# --------------------------------------------------------------------------- lo guardado, para leerlo de vuelta


@dataclass(frozen=True)
class LineaGuardada:
    hijo: str  # su clave
    cantidad: Decimal
    orden: int
    reporta_a: str
    porcentaje: bool


@dataclass(frozen=True)
class VersionGuardada:
    clave: str
    version: int
    huella: str
    pu: Decimal
    vigente_desde: datetime
    carga_id: int
    lineas: Tuple[LineaGuardada, ...]


@dataclass(frozen=True)
class PrecioGuardado:
    clave: str
    precio: Decimal
    vigente_desde: datetime
    vigente_hasta: Optional[datetime]
    carga_id: Optional[int]


@dataclass(frozen=True)
class ResumenCarga:
    id: int
    creada_en: datetime
    usuario: str
    rol: str
    archivos: Mapping[str, str]
    resumen: Mapping[str, Any]


@dataclass(frozen=True)
class NodoDePresupuesto:
    """Un nodo de un presupuesto guardado, tal como lo entrega el adaptador: estructural o concepto."""

    id: int
    clave: str
    descripcion: str
    unidad: str
    estructural: bool
    tipo_opus: str  # Capítulo… para un estructural; «Concepto» para un concepto


@dataclass(frozen=True)
class LineaDePresupuesto:
    padre_id: int
    hijo_id: int
    orden: int
    cantidad: Decimal
    version: Optional[int]  # la versión del concepto que el renglón fijó; nula en un estructural o en un concepto sin matriz
    pu: Optional[Decimal]  # el PU congelado de esa versión


@dataclass(frozen=True)
class DatosDePresupuesto:
    resumen: ResumenPresupuesto
    raiz_id: int
    nodos: Mapping[int, NodoDePresupuesto]
    lineas: Tuple[LineaDePresupuesto, ...]


@dataclass(frozen=True)
class RenglonGuardado:
    posicion: int
    padre: Optional[int]
    wbs: str  # por posición, como siempre (`CONOCIMIENTO.md` §1.1)
    nivel: int
    tipo: str
    clave: str
    descripcion: str
    unidad: str
    cantidad: Decimal
    pu: Decimal
    total: Decimal
    version: Optional[int]


@dataclass(frozen=True)
class PresupuestoGuardado:
    resumen: ResumenPresupuesto
    renglones: Tuple[RenglonGuardado, ...]

    @property
    def total(self) -> Decimal:
        return self.renglones[0].total


class RepositorioCatalogo(Protocol):
    def estado_vigente(self) -> EstadoVigente: ...

    def aplicar(self, plan: PlanDeCarga) -> ResultadoCarga:
        """Escribe el plan completo o nada. Si la última carga ya no es `plan.base`, `CatalogoCambio`."""

    def versiones(self, clave: str) -> List[VersionGuardada]:
        """De la primera a la última; la vigente es la última."""

    def precios(self, clave: str) -> List[PrecioGuardado]:
        """De un insumo, del más viejo al vigente."""

    def cargas(self) -> List[ResumenCarga]: ...

    def presupuestos(self) -> List[ResumenPresupuesto]: ...

    def datos_de_presupuesto(self, presupuesto_id: int) -> DatosDePresupuesto: ...

    def arbol(self) -> ArbolEnMemoria:
        """Lo vigente, listo para el motor de cálculo: la última versión de cada matriz y el árbol de cada presupuesto."""

    def id_de(self, clave: str) -> int:
        """El nodo del catálogo con esa clave."""


# --------------------------------------------------------------------------- el presupuesto guardado, armado


def armar_presupuesto(datos: DatosDePresupuesto) -> PresupuestoGuardado:
    """El árbol de un presupuesto con su WBS por posición, el PU congelado de cada concepto y los totales.

    Un concepto vale lo que valía su versión al cargarse; un estructural, lo que suman sus hijos. Cada renglón se redondea
    a centavos antes de sumar, como OPUS (`motor_calculo._redondear`)."""
    from .motor_calculo import _redondear

    hijos: Dict[int, List[LineaDePresupuesto]] = defaultdict(list)
    for l in datos.lineas:
        hijos[l.padre_id].append(l)
    for ls in hijos.values():
        ls.sort(key=lambda l: l.orden)
    out: List[RenglonGuardado] = []

    def total_de(nodo_id: int, cantidad: Decimal, version: Optional[int], pu: Optional[Decimal], padre: Optional[int], wbs: str) -> Decimal:
        n = datos.nodos[nodo_id]
        posicion = len(out)
        out.append(None)  # type: ignore[arg-type]  # se llena al volver, cuando se sepa el PU
        if n.estructural:
            suma = Decimal("0")
            for i, l in enumerate(hijos.get(nodo_id, ()), start=1):
                suma += total_de(l.hijo_id, l.cantidad, l.version, l.pu, posicion, f"{wbs}.{i}")
            precio = suma
        else:
            precio = pu if pu is not None else Decimal("0")
        total = _redondear(cantidad * precio)
        nivel = len(wbs.split(".")) - 1
        out[posicion] = RenglonGuardado(posicion, padre, wbs, nivel, n.tipo_opus, n.clave, n.descripcion, n.unidad, cantidad,
                                        precio, total, version)
        return total

    total_de(datos.raiz_id, Decimal("1"), None, None, None, "1")
    return PresupuestoGuardado(datos.resumen, tuple(out))


# --------------------------------------------------------------------------- huellas de lo que se lee


def sha256_de(texto: str) -> str:
    return hashlib.sha256(texto.encode("utf-8")).hexdigest()


def huella_presupuesto(filas: Iterable[FilaPresupuesto]) -> str:
    """De la estructura y las cantidades de un capítulo, no de sus textos ni de sus precios: dos cargas son «lo mismo» si
    tienen los mismos renglones en el mismo orden con las mismas cantidades."""
    return sha256_de("\n".join(
        f"{f.nivel}|{f.tipo}|{f.clave}|{format(f.cantidad.normalize(), 'f') if f.cantidad is not None else ''}" for f in filas))


def _rutas_naturales(filas: Sequence[FilaPresupuesto]) -> Dict[int, str]:
    """`clave#n` de la raíz a cada estructural; `n` es el lugar entre los hermanos que se llaman igual (CONOCIMIENTO.md §2.3)."""
    rutas: Dict[int, str] = {}
    vistos: Dict[Tuple[Optional[int], str], int] = defaultdict(int)
    for f in filas:
        if f.es_concepto:
            continue
        vistos[(f.padre, f.clave)] += 1
        segmento = f"{f.clave}#{vistos[(f.padre, f.clave)]}"
        rutas[f.posicion] = f"{rutas[f.padre]}/{segmento}" if f.padre is not None else segmento
    return rutas


# --------------------------------------------------------------------------- planificar: decidir qué entra y qué se detiene


def _unidad_igual(a: str, b: str) -> bool:
    return a.strip().casefold() == b.strip().casefold()


def planificar(
    estado: EstadoVigente,
    matrices: Matrices,
    presupuesto: Optional[LecturaPresupuesto],
    *,
    usuario: str,
    rol: str,
    archivos: Mapping[str, str],
    tipo: str = "plantilla",
    confirmados: Iterable[str] = (),
) -> Tuple[DiagnosticoDeCarga, PlanDeCarga]:
    """Puro: lo que haría cargar este archivo sobre lo vigente. No escribe ni lee nada más."""
    confirmados = frozenset(confirmados)
    unidades_de_concepto = {c: presupuesto.unidad_de(c) for c in presupuesto.conceptos} if presupuesto is not None else {}
    arbol = armar_arbol(matrices, unidades_de_concepto)
    problemas: List[str] = list(arbol.problemas) + (list(presupuesto.problemas) if presupuesto is not None else [])
    avisos: List[str] = [
        f"línea {l.linea}: {l.padre} → {l.hijo}: cantidad × costo no da el importe ({l.importe})" for l in matrices.importes_que_no_cuadran]
    nuevo = catalogo_leido(matrices, presupuesto)
    diag = diagnosticar(nuevo, estado.como_catalogo())
    padres = set(matrices.por_padre)

    pendientes: List[Pendiente] = []
    retenido: Dict[str, str] = {}  # clave → motivo: lo que no se aplica, y de lo que dependen los demás

    # ---- los insumos: lo que no tiene matriz propia
    hojas: Dict[str, List] = defaultdict(list)
    for l in matrices.lineas:
        if l.hijo not in padres:
            hojas[l.hijo].append(l)
    insumos_nuevos: List[InsumoPlan] = []
    precios_nuevos: List[Tuple[str, Decimal]] = []
    precios_que_cambian: List[Tuple[str, Decimal, Decimal]] = []
    unidades_que_se_saben: List[Tuple[str, str]] = []
    for clave, lineas in hojas.items():
        primera = lineas[0]
        categoria = CATEGORIA_DE_TIPO[primera.tipo]
        solo_porcentaje = all(l.es_porcentaje_mo for l in lineas)
        precio = Decimal("0") if solo_porcentaje else primera.costo
        previo = estado.insumos.get(clave)
        if previo is None:
            insumos_nuevos.append(InsumoPlan(clave, primera.descripcion, primera.unidad, categoria, precio, not solo_porcentaje))
            continue
        if previo.unidad and primera.unidad and not _unidad_igual(previo.unidad, primera.unidad):
            retenido[clave] = UNIDAD_CAMBIO
            pendientes.append(Pendiente(clave, UNIDAD_CAMBIO, f"era {previo.unidad}, llega {primera.unidad}"))
            continue
        if not previo.unidad and primera.unidad:
            unidades_que_se_saben.append((clave, primera.unidad))
        if not solo_porcentaje and previo.precio is not None and previo.precio != precio:
            if categoria == Categoria.TRABAJO:
                retenido[clave] = PRECIO_DE_TRABAJO
                pendientes.append(Pendiente(clave, PRECIO_DE_TRABAJO, f"era {previo.precio}, llega {precio}: un trabajo se valida"))
            else:
                precios_nuevos.append((clave, precio))
                precios_que_cambian.append((clave, previo.precio, precio))

    # ---- los padres: el orden de los de abajo hacia arriba, para decidir con lo ya decidido de lo que contienen
    orden: List[str] = []
    visto: Set[str] = set()

    def visita(c: str, pila: Set[str]) -> None:
        if c in visto:
            return
        if c in pila:
            raise CargaNoProcede(f"{c} se contiene a sí mismo, directa o indirectamente")
        pila.add(c)
        for l in matrices.por_padre.get(c, ()):
            if l.hijo in padres:
                visita(l.hijo, pila)
        pila.discard(c)
        visto.add(c)
        orden.append(c)

    for c in matrices.por_padre:
        visita(c, set())

    debajo: Dict[str, Set[str]] = {}
    for c in orden:
        s: Set[str] = set()
        for l in matrices.por_padre[c]:
            s.add(l.hijo)
            s |= debajo.get(l.hijo, set())
        debajo[c] = s

    for d in diag.detenidos:
        retenido[d.clave] = UNIDAD_CAMBIO
        pendientes.append(Pendiente(d.clave, UNIDAD_CAMBIO, f"era {d.unidad_vigente}, llega {d.unidad_nueva}"))

    nuevos, versionan = set(diag.nuevos), set(diag.versionan)
    nodos_nuevos: List[NodoConMatriz] = []
    versiones_nuevas: List[NodoConMatriz] = []
    pu_de: Dict[str, Decimal] = {}  # el PU con que queda cada matriz que se aplica
    descripcion_de = {l.hijo: l.descripcion for l in matrices.lineas}
    for c in orden:
        if c not in nuevos and c not in versionan:
            if c not in retenido and not estado.unidad.get(c) and nuevo.unidad.get(c):
                unidades_que_se_saben.append((c, nuevo.unidad[c]))
            continue
        causa = next((d for d in sorted(debajo[c]) if d in retenido), None)
        if causa is not None:
            retenido[c] = DEPENDE_DE
            pendientes.append(Pendiente(c, DEPENDE_DE, f"{causa} quedó pendiente ({retenido[causa]})"))
            continue
        try:
            pu = precio_unitario(arbol.id_de[c], arbol.repo)
        except CicloError as e:
            raise CargaNoProcede(str(e)) from None
        if c in versionan:
            antes = estado.pu.get(c, Decimal("0"))
            if antes > 0 and abs(pu - antes) / antes > UMBRAL_DE_CONFIRMACION and c not in confirmados:
                retenido[c] = PU_MOVIO
                pendientes.append(Pendiente(c, PU_MOVIO, f"el PU pasa de {antes} a {pu}: pide confirmación"))
                continue
        nodo = arbol.nodo(c)
        if c in versionan and not estado.unidad.get(c) and nodo.unidad:
            unidades_que_se_saben.append((c, nodo.unidad))
        descripcion = (presupuesto.conceptos[c][0].descripcion if presupuesto is not None and c in presupuesto.conceptos
                       else descripcion_de.get(c, ""))
        plan_nodo = NodoConMatriz(
            c, descripcion, nodo.unidad, nodo.rol, nodo.categoria, nuevo.huella[c], pu,
            tuple(LineaPlan(l.hijo, l.cantidad, CATEGORIA_DE_TIPO[l.tipo], l.es_porcentaje_mo) for l in matrices.por_padre[c]),
        )
        pu_de[c] = pu
        (nodos_nuevos if c in nuevos else versiones_nuevas).append(plan_nodo)

    # ---- el presupuesto
    estados_p: List[EstadoDePresupuesto] = []
    presupuestos_nuevos: List[PresupuestoPlan] = []
    conceptos_sin_matriz: List[ConceptoSinMatriz] = []
    sin_matriz: List[str] = []
    observados: List[Tuple[str, Decimal, Decimal]] = []
    creados = {n.clave for n in nodos_nuevos}
    if presupuesto is not None and presupuesto.limpia:
        sin_matriz = sorted(c for c in presupuesto.conceptos if c not in matrices.por_padre and c not in estado.huella)
        for cap in presupuesto.capitulos():
            clave, nombre = cap.raiz.clave, cap.raiz.descripcion
            huella_p = huella_presupuesto(cap.filas)
            guardado = estado.presupuestos.get(clave)
            if guardado is not None:
                if guardado.huella == huella_p:
                    estados_p.append(EstadoDePresupuesto(clave, nombre, "sin_cambios"))
                else:
                    estados_p.append(EstadoDePresupuesto(
                        clave, nombre, "cambio_no_aplicado",
                        "lo que llega no es lo que está guardado; reconciliar un presupuesto que ya existe no está diseñado"))
                continue
            conceptos = sorted({f.clave for f in cap.filas if f.es_concepto})
            frena = [(c, retenido[c]) for c in conceptos if c in retenido]
            if frena:
                c, motivo = frena[0]
                estados_p.append(EstadoDePresupuesto(clave, nombre, "pendiente", f"{c} quedó pendiente ({motivo})"))
                pendientes.append(Pendiente(clave, CONCEPTO_PENDIENTE, f"{c} quedó pendiente ({motivo})"))
                continue
            con_precio_sin_matriz = [
                f.clave for f in cap.filas if f.es_concepto and f.clave in sin_matriz and (f.precio_observado or Decimal("0")) != 0]
            if con_precio_sin_matriz:
                c = con_precio_sin_matriz[0]
                estados_p.append(EstadoDePresupuesto(clave, nombre, "pendiente", f"{c} trae precio y ninguna matriz"))
                pendientes.append(Pendiente(clave, CONCEPTO_CON_PRECIO_Y_SIN_MATRIZ, f"{c} trae precio y ninguna matriz"))
                continue
            for f in cap.filas:
                calculado = pu_de.get(f.clave, estado.pu.get(f.clave)) if f.es_concepto else None
                if calculado is not None and f.precio_observado is not None \
                        and abs(f.precio_observado - calculado) > TOLERANCIA_DE_PRECIO_OBSERVADO:
                    observados.append((f.clave, f.precio_observado, calculado))
            rutas = _rutas_naturales(cap.filas)
            lugar = {f.posicion: i for i, f in enumerate(cap.filas)}  # sin los huecos que dejan los placeholders descartados
            renglones = tuple(
                RenglonPlan(lugar[f.posicion], None if f.padre is None else lugar[f.padre], f.tipo, f.nivel, f.clave, f.descripcion,
                            f.unidad, f.cantidad if f.cantidad is not None else Decimal("1"), "" if f.es_concepto else rutas[f.posicion])
                for f in cap.filas)
            presupuestos_nuevos.append(PresupuestoPlan(clave, nombre, tipo, huella_p, renglones))
            estados_p.append(EstadoDePresupuesto(clave, nombre, "nuevo"))
            for c in conceptos:
                if c in sin_matriz and c not in estado.unidad and c not in {x.clave for x in conceptos_sin_matriz}:
                    fila = presupuesto.conceptos[c][0]
                    conceptos_sin_matriz.append(ConceptoSinMatriz(c, fila.descripcion, fila.unidad))
    elif presupuesto is not None:
        estados_p.append(EstadoDePresupuesto("", "", "pendiente", "el archivo trae problemas: no se carga ningún presupuesto"))

    # ---- las unidades que hay que tener
    vistas: Dict[str, str] = {}
    for u in ([i.unidad for i in insumos_nuevos] + [n.unidad for n in nodos_nuevos + versiones_nuevas] + [c.unidad for c in conceptos_sin_matriz]
              + [u for _, u in unidades_que_se_saben] + [r.unidad for p in presupuestos_nuevos for r in p.renglones]):
        if u.strip():
            vistas.setdefault(u.strip().casefold(), u.strip())
    sin_unidad = tuple(sorted([i.clave for i in insumos_nuevos if not i.unidad.strip()] + [n.clave for n in nodos_nuevos if not n.unidad.strip()]))

    resumen: Dict[str, Any] = {
        "insumos_nuevos": len(insumos_nuevos), "precios_nuevos": len(precios_nuevos), "nodos_nuevos": len(nodos_nuevos),
        "versiones_nuevas": len(versiones_nuevas), "conceptos_sin_matriz": len(conceptos_sin_matriz),
        "presupuestos_nuevos": [p.clave for p in presupuestos_nuevos],
        "pendientes": [{"clave": p.clave, "motivo": p.motivo, "detalle": p.detalle} for p in pendientes],
        "presupuestos": [{"clave": e.clave, "estado": e.estado, "detalle": e.detalle} for e in estados_p],
        "confirmados": sorted(confirmados),
    }
    diagnostico = DiagnosticoDeCarga(
        diag, len(insumos_nuevos), tuple(precios_que_cambian), tuple(pendientes), tuple(estados_p), tuple(sin_matriz), sin_unidad,
        tuple(observados), tuple(avisos), tuple(problemas))
    plan = PlanDeCarga(
        estado.ultima_carga, usuario, rol, dict(archivos), resumen, tuple(vistas.values()), tuple(insumos_nuevos), tuple(precios_nuevos),
        tuple(unidades_que_se_saben), tuple(nodos_nuevos), tuple(versiones_nuevas), tuple(conceptos_sin_matriz), tuple(presupuestos_nuevos))
    return diagnostico, plan


# --------------------------------------------------------------------------- el diagnóstico, en palabras

MOTIVOS = {
    UNIDAD_CAMBIO: "cambió la unidad",
    PRECIO_DE_TRABAJO: "el precio de un trabajo se valida",
    PU_MOVIO: "el PU se movió más de 5 %: pide confirmación",
    DEPENDE_DE: "depende de algo que quedó pendiente",
    CONCEPTO_PENDIENTE: "tiene un concepto pendiente",
    CONCEPTO_CON_PRECIO_Y_SIN_MATRIZ: "trae precio y ninguna matriz",
}


def informe_de_carga(d: DiagnosticoDeCarga) -> str:
    """Lo que se le muestra a quien decide antes de aplicar (§2.9, paso 3): qué entra, qué versiona, qué se detiene y por qué."""
    g = d.diagnostico
    o = [f"Carga de OPUS — {len(g.nuevos) + len(g.versionan) + len(g.entran) + len(g.detenidos)} matrices en el archivo", ""]
    o.append(f"  {len(g.entran):>5} entran sin cambios")
    o.append(f"  {len(g.nuevos):>5} son nuevas")
    o.append(f"  {len(g.versionan):>5} versionan — cambió su matriz")
    o.append(f"  {len(g.detenidos):>5} detenidas — cambió la unidad")
    o.append(f"  {d.insumos_nuevos:>5} insumos nuevos · {len(d.precios_que_cambian)} precios que cambian")
    if g.ausentes:
        o.append(f"  {len(g.ausentes):>5} ya no vienen en el archivo (no se borran)")
    if d.presupuestos:
        o += ["", "Presupuestos"]
        etiqueta = {"nuevo": "se cargará", "sin_cambios": "ya está, igual", "cambio_no_aplicado": "ya está y llega distinto: NO se aplica", "pendiente": "pendiente"}
        o += [f"  {e.clave:<10} {e.nombre} — {etiqueta.get(e.estado, e.estado)}" + (f" ({e.detalle})" if e.detalle else "") for e in d.presupuestos]
    if d.pendientes:
        o += ["", "Pendientes (no se aplican; quedan dichos en la carga)"]
        o += [f"  {p.clave:<12} {MOTIVOS.get(p.motivo, p.motivo)}: {p.detalle}" for p in d.pendientes]
    if d.precios_que_cambian:
        o += ["", "Precios que se mueven (historia de precio; no versionan nada)"]
        o += [f"  {c:<12} {antes} → {ahora}" for c, antes, ahora in d.precios_que_cambian]
    if d.sin_matriz:
        o += ["", f"Sin matriz ({len(d.sin_matriz)}): " + ", ".join(d.sin_matriz)]
    if d.sin_unidad:
        o += [f"Sin unidad conocida ({len(d.sin_unidad)}): se crean con la unidad vacía hasta que se sepa"]
    if d.precios_observados_distintos:
        o += ["", "El PU del presupuesto no es el que sale de la matriz"]
        o += [f"  {c:<12} presupuesto {obs} · matriz {calc}" for c, obs, calc in d.precios_observados_distintos]
    if d.avisos:
        o += ["", "Avisos"] + [f"  {a}" for a in d.avisos]
    if d.problemas:
        o += ["", "NO SE PUEDE APLICAR — el archivo trae algo que no cuadra"] + [f"  {p}" for p in d.problemas]
    return "\n".join(o)


# --------------------------------------------------------------------------- el servicio


@dataclass(frozen=True)
class Revision:
    diagnostico: DiagnosticoDeCarga
    plan: PlanDeCarga


class ServicioCarga:
    def __init__(
        self, repositorio: RepositorioCatalogo, permisos: Optional[Callable[[], Mapping[str, FrozenSet[str]]]] = None
    ) -> None:
        """`permisos` entrega `ROL_FUNCION` tal como está hoy (`RepositorioAccesos.permisos`); sin ella, la tabla por omisión."""
        self.repo = repositorio
        self._permisos = permisos

    def rol_para(self, roles: Roles) -> str:
        return rol_efectivo(FUNCION_DE_CARGAR, roles, None if self._permisos is None else self._permisos())

    def revisar(
        self,
        conceptos: str,
        presupuesto: Optional[str] = None,
        compuestos: Optional[str] = None,
        *,
        rol: Roles,
        usuario: str,
        tipo: str = "plantilla",
        confirmados: Iterable[str] = (),
    ) -> Revision:
        """Lee los archivos y dice qué haría cargarlos hoy. No escribe nada."""
        rol_con_que = self.rol_para(rol)
        if not usuario:
            raise ValueError("toda carga dice quién la hizo")
        if tipo not in TIPOS_DE_PRESUPUESTO:
            raise ValueError(f"el tipo de presupuesto debe ser uno de: {', '.join(TIPOS_DE_PRESUPUESTO)}")
        archivos = {"ANALISIS_DE_BASICOS_CONCEPTOS": sha256_de(conceptos)}
        if compuestos is not None:
            archivos["ANALISIS_DE_BASICOS_COMPUESTOS"] = sha256_de(compuestos)
        if presupuesto is not None:
            archivos["CATALOGO_DE_PRESUPUESTO"] = sha256_de(presupuesto)
        matrices = leer_matrices(conceptos, compuestos)
        lectura = leer_presupuesto(presupuesto) if presupuesto is not None else None
        d, plan = planificar(self.repo.estado_vigente(), matrices, lectura, usuario=usuario, rol=rol_con_que, archivos=archivos,
                             tipo=tipo, confirmados=confirmados)
        return Revision(d, plan)

    def aplicar(
        self,
        conceptos: str,
        presupuesto: Optional[str] = None,
        compuestos: Optional[str] = None,
        *,
        rol: Roles,
        usuario: str,
        tipo: str = "plantilla",
        confirmados: Iterable[str] = (),
    ) -> ResultadoCarga:
        """Revisa y aplica lo que entra. Lo detenido no se aplica y queda dicho en la carga. Si el archivo trae algo que no
        cuadra (`problemas`), no se escribe nada."""
        r = self.revisar(conceptos, presupuesto, compuestos, rol=rol, usuario=usuario, tipo=tipo, confirmados=confirmados)
        if not r.diagnostico.aplicable:
            raise CargaNoProcede("el archivo trae algo que no cuadra: " + "; ".join(r.diagnostico.problemas))
        if not r.plan.cambia_algo and not r.diagnostico.pendientes:
            return ResultadoCarga(None, r.plan.resumen)
        return self.repo.aplicar(r.plan)

    # ---- lo que se lee de vuelta
    def presupuesto(self, presupuesto_id: int) -> PresupuestoGuardado:
        return armar_presupuesto(self.repo.datos_de_presupuesto(presupuesto_id))
