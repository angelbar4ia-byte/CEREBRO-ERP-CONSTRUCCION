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
- **Un presupuesto que ya existe se reconcilia, no se pisa** (D-476, `reconciliacion.py`): se reconoce por la clave de su capítulo; si
  lo que llega es lo mismo, se dice; si no, las cantidades distintas y los renglones nuevos entran con su historia, una baja pide
  confirmación y no borra, y lo contratado no se toca.
- **Lo que algo contratado usa no cambia de receta por la carga** (D-475, §2.2: «algo contratado: no entra en vigor, va a control de
  cambio»): la versión nueva de un concepto que fija un renglón de un subárbol contratado se detiene con su motivo.
- **Un texto que cambia de verdad con la receta es otro concepto** (D-477, §2.7.1): si la descripción de un concepto cambió de forma
  significativa —un número, el verbo o el elemento— **y** su matriz también, no se trata como una versión sino que se detiene y se
  propone una clave nueva; quien decide puede confirmar que es el mismo. Un texto que cambia sin la receta carga y alerta.
- **Una clave que se sustituyó por un clon sigue entrando** (D-478, §16.2): el archivo de OPUS que todavía trae `AUX-00001` se lee como
  `PRE-00120`; el catálogo no vuelve a tener dos nodos de lo mismo ni avisa de «ausentes» por la clave retirada.
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
from typing import Any, Callable, Dict, FrozenSet, Iterable, List, Mapping, Optional, Protocol, Sequence, Set, Tuple, Union

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
    canonizar_matrices,
    canonizar_presupuesto,
    catalogo_leido,
    diagnosticar,
    leer_matrices,
    leer_presupuesto,
)
from .motor_calculo import CicloError, ArbolEnMemoria, precio_unitario
from .servicio_programa import Roles, rol_efectivo
from .texto import ALTA, DiferenciaDeTexto, clave_nueva, comparar

FUNCION_DE_CARGAR = "cargar_catalogo_opus"
UMBRAL_DE_CONFIRMACION = Decimal("0.05")  # §2.2: si el PU se movió más de 5 %, pide confirmación aunque sea en diseño
TOLERANCIA_DE_PRECIO_OBSERVADO = Decimal("0.005")
TIPOS_DE_PRESUPUESTO = ("plantilla", "obra", "escenario")
TOPE_DE_CAMBIOS_EN_EL_RESUMEN = 500  # lo que se guarda en la carga de la lista de cambios; el total siempre se guarda

# por qué algo quedó pendiente
UNIDAD_CAMBIO = "unidad_cambio"
PRECIO_DE_TRABAJO = "precio_de_trabajo"
PU_MOVIO = "pu_movio_mas_de_5"
DEPENDE_DE = "depende_de"
EN_CONTRATADO = "en_contratado"
TEXTO_Y_RECETA = "texto_y_receta"
BAJA_SIN_CONFIRMAR = "baja_sin_confirmar"
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


@dataclass(frozen=True)
class PresupuestoExistente:
    """Un presupuesto guardado que el archivo trae otra vez, para reconciliarlo: su contenido y qué bloques están contratados."""

    datos: "DatosDePresupuesto"
    contratados: FrozenSet[int]  # los bloques contratados y todos los que cuelgan de ellos


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
    version: Dict[str, int] = field(default_factory=dict)  # padres con matriz → el número de su versión vigente
    descripcion: Dict[str, str] = field(default_factory=dict)  # todo nodo del catálogo → su descripción guardada (D-477)
    en_contratado: Set[str] = field(default_factory=set)  # conceptos que fija algún renglón de un subárbol contratado (D-475)
    homologaciones: Dict[str, str] = field(default_factory=dict)  # clave vieja → la vigente, de lo que se sustituyó por un clon (D-478)

    def como_catalogo(self) -> CatalogoLeido:
        """Lo vigente para compararlo con un archivo: sin las claves retiradas, que el archivo ya llega leídas como su clon."""
        retiradas = self.homologaciones
        return CatalogoLeido(
            {k: v for k, v in self.unidad.items() if k not in retiradas}, {k: v for k, v in self.huella.items() if k not in retiradas},
            tuple(sorted(c for c in self.sin_matriz if c not in retiradas)))


def cerrar_homologaciones(pares: Iterable[Tuple[str, str]]) -> Dict[str, str]:
    """`vieja → vigente` de una cadena de sustituciones: si `A` se sustituyó por `B` y `B` por `C`, `A` entra como `C`."""
    directo = dict(pares)
    out: Dict[str, str] = {}
    for vieja in directo:
        actual, vistas = directo[vieja], {vieja}
        while actual in directo and actual not in vistas:
            vistas.add(actual)
            actual = directo[actual]
        out[vieja] = actual
    return out


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
class AltaPlan:
    """Un renglón o un bloque que el archivo trae y el presupuesto guardado no tiene (D-476)."""

    indice: int  # su lugar en la tupla de altas: los bloques nuevos van antes que lo que cuelga de ellos
    padre_id: Optional[int]  # el bloque que ya existe…
    padre_alta: Optional[int]  # …o el índice de otra alta, si cuelga de un bloque nuevo
    tipo: str  # Subcapítulo · Nivel 2 · Nivel 3 · Concepto
    nivel: int
    clave: str
    descripcion: str
    unidad: str
    cantidad: Decimal
    ruta_natural: str  # solo de los bloques
    orden: int  # el lugar que ocupa entre los hermanos vivos


@dataclass(frozen=True)
class ReconciliacionPlan:
    """Lo que se le hace a un presupuesto que ya existe cuando llega con otro contenido: solo lo que se puede aplicar."""

    presupuesto_id: int
    clave: str
    huella: str  # la del archivo si se aplica todo; vacía si algo quedó detenido (el adaptador pone una marca con la carga)
    cantidades: Tuple[Tuple[int, Decimal, Decimal], ...] = ()  # (renglón, antes, ahora)
    altas: Tuple[AltaPlan, ...] = ()
    bajas: Tuple[int, ...] = ()  # los renglones que se dan de baja, también los de abajo de un bloque que se va
    bajas_de_bloque: Tuple[int, ...] = ()  # los bloques (nodos) que se dan de baja
    ordenes: Tuple[Tuple[int, int, int], ...] = ()  # (renglón, antes, ahora): el lugar entre los hermanos

    @property
    def cambia_algo(self) -> bool:
        return bool(self.cantidades or self.altas or self.bajas or self.bajas_de_bloque or self.ordenes)


@dataclass(frozen=True)
class CambioDePresupuesto:
    """Una diferencia entre un presupuesto guardado y el que llega, y qué se hace con ella."""

    presupuesto: str  # la clave de su capítulo
    tipo: str  # cantidad · alta · baja
    id: str  # con lo que se identifica: la ruta del bloque, o `ruta del bloque::CLAVE#n` en un renglón; es lo que se confirma en una baja
    clave: str
    descripcion: str
    es_bloque: bool
    antes: Optional[Decimal]
    ahora: Optional[Decimal]
    estado: str  # aplica · detenido
    motivo: str = ""  # si está detenido
    detalle: str = ""
    renglones: Tuple[int, ...] = ()  # de una baja: los renglones que se van con ella…
    bloques: Tuple[int, ...] = ()  # …y los bloques, para saber quién los cita (el programa, D-474)


@dataclass(frozen=True)
class AlertaDeTexto:
    """Una descripción que llega distinta de la guardada, y qué se hace con ella (§2.7.1, D-477)."""

    clave: str
    antes: str
    despues: str
    nivel: str  # informativa · alta
    motivo: str  # numero · palabra · orden · calificativo
    detalle: str  # lo que cambió: «3 → 4.2», «tabique → block»
    estado: str  # carga: la descripción nueva entra · detenido: con la receta, parece otro concepto
    clave_propuesta: str = ""  # si está detenido: la clave nueva que el sistema propone


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
    reconciliaciones: Tuple[ReconciliacionPlan, ...] = ()
    descripciones: Tuple[Tuple[str, str], ...] = ()  # (clave, descripción nueva): lo que cambió de texto y entra

    @property
    def cambia_algo(self) -> bool:
        return bool(self.insumos_nuevos or self.precios_nuevos or self.unidades_que_se_saben or self.nodos_nuevos
                    or self.versiones_nuevas or self.conceptos_sin_matriz or self.presupuestos_nuevos
                    or any(r.cambia_algo or r.huella for r in self.reconciliaciones) or self.descripciones)


@dataclass(frozen=True)
class Pendiente:
    clave: str
    motivo: str
    detalle: str


@dataclass(frozen=True)
class EstadoDePresupuesto:
    clave: str
    nombre: str
    estado: str  # nuevo · sin_cambios · reconciliado · parcial · pendiente
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
    cambios: Tuple[CambioDePresupuesto, ...] = ()  # lo que cambia en los presupuestos que ya existían (D-476)
    alertas_de_texto: Tuple[AlertaDeTexto, ...] = ()  # las descripciones que llegan distintas (D-477)

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
    tipo: str = "archivos"  # archivos · contratacion (D-475: contratar un subárbol también deja su carga)


@dataclass(frozen=True)
class NodoDePresupuesto:
    """Un nodo de un presupuesto guardado, tal como lo entrega el adaptador: estructural o concepto."""

    id: int
    clave: str
    descripcion: str
    unidad: str
    estructural: bool
    tipo_opus: str  # Capítulo… para un estructural; «Concepto» para un concepto
    ruta_natural: str = ""  # de un estructural: clave#n/clave#n…; vacía en un concepto


@dataclass(frozen=True)
class LineaDePresupuesto:
    padre_id: int
    hijo_id: int
    orden: int
    cantidad: Decimal
    version: Optional[int]  # la versión del concepto que el renglón fijó; nula en un estructural o en un concepto sin matriz
    pu: Optional[Decimal]  # el PU congelado de esa versión
    id: int = 0  # el de la línea de COMPOSICION: es la identidad del renglón, a la que se cuelga una partida del programa


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


@dataclass(frozen=True)
class CambioDeRenglon:
    """Algo que le pasó a un renglón del presupuesto al reconciliarlo (D-476): quedó en la carga que lo hizo."""

    carga_id: int
    campo: str  # alta · cantidad · orden · baja
    antes: Optional[str]
    despues: Optional[str]
    creada_en: datetime


@dataclass(frozen=True)
class Congelamiento:
    """Un subárbol que se contrató: el nodo, su ruta natural, quién, con qué rol, cuándo y qué se fijó."""

    id: int
    nodo_id: int
    ruta: str
    estado: str  # contratado (diseño es lo que tiene todo nodo sin fila)
    fecha: datetime
    usuario: str
    rol: str
    carga_id: int
    resumen: Mapping[str, Any]


@dataclass(frozen=True)
class VersionPorFijar:
    """Una versión nueva de un concepto que nace al contratar: la misma receta que la vigente, con el PU de hoy."""

    clave: str
    pu: Decimal


@dataclass(frozen=True)
class PlanDeContratacion:
    base: int  # la última carga que vio quien revisó: si hay otra, no se aplica
    presupuesto_id: int
    nodo_id: int
    usuario: str
    rol: str
    resumen: Mapping[str, Any]
    versiones_nuevas: Tuple[VersionPorFijar, ...] = ()
    renglones: Tuple[Tuple[int, str], ...] = ()  # (renglón, clave de su concepto): pasan a fijar la versión vigente de ese concepto


@dataclass(frozen=True)
class ResultadoContratacion:
    carga_id: int
    congelamiento_id: int
    versiones_nuevas: int
    renglones_fijados: int


@dataclass(frozen=True)
class NodoDelCatalogo:
    """Un nodo del catálogo tal como está guardado: lo que hace falta saber para clonarlo."""

    clave: str
    descripcion: str
    unidad: str
    rol: str  # insumo · ensamble · concepto
    categoria: str
    procedencia: str
    precio: Optional[Decimal]  # el vigente, de un insumo con historia de precio; nulo en el resto
    con_matriz: bool  # tiene versión vigente


@dataclass(frozen=True)
class PadreCitante:
    """Un concepto o compuesto cuya versión vigente cita a un nodo, y los renglones de presupuesto que fijan esa versión (D-478)."""

    clave: str
    version: int
    huella: str
    pu: Decimal
    lineas: Tuple[LineaGuardada, ...]
    renglones: Tuple[int, ...]  # las líneas de COMPOSICION de presupuesto (sin baja) que fijan esa versión


@dataclass(frozen=True)
class CitasDe:
    """Quién usa un nodo: las matrices que lo citan en su versión vigente, y los renglones que lo ponen directo en un presupuesto."""

    padres: Tuple[PadreCitante, ...]
    renglones_directos: int = 0


@dataclass(frozen=True)
class ClonGuardado:
    id: int
    original: str
    clon: str
    modo: str  # mantener · sustituir
    reconoce_clave_vieja_al_importar: bool
    exporta_clave_vieja: bool  # sigue saliendo con la clave vieja hasta que alguien autorice lo contrario: es solo la bandera (B-08)
    usuario: str
    rol: str
    carga_id: int
    resumen: Mapping[str, Any]
    creada_en: datetime


@dataclass(frozen=True)
class SustitucionDePadre:
    """La versión nueva que nace en un concepto o compuesto cuando lo que citaba pasa a citar al clon: la misma receta, el mismo PU."""

    clave: str
    lineas: Tuple[LineaPlan, ...]
    huella: str
    pu: Decimal
    renglones: Tuple[int, ...]  # pasan a fijar esa versión nueva


@dataclass(frozen=True)
class PlanDeClonacion:
    base: int  # la última carga que vio quien revisó: si hay otra, no se aplica
    original: str
    clave: str  # la del clon
    modo: str
    usuario: str
    rol: str
    resumen: Mapping[str, Any]
    nuevo: Union[InsumoPlan, NodoConMatriz, ConceptoSinMatriz]  # el clon, con lo que copia del original
    sustituciones: Tuple[SustitucionDePadre, ...] = ()


@dataclass(frozen=True)
class ResultadoClonacion:
    carga_id: int
    clon_id: int
    versiones_nuevas: int
    renglones_fijados: int


class YaContratado(Exception):
    """El nodo, o un bloque de arriba, ya está contratado: lo contratado no se vuelve a contratar."""

    def __init__(self, mensaje: str, nodo_id: Optional[int] = None) -> None:
        super().__init__(mensaje)
        self.nodo_id = nodo_id


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

    def historia(self, renglon_id: int) -> List["CambioDeRenglon"]:
        """Todo lo que le pasó a un renglón del presupuesto, del primero al último: alta, cantidad, lugar y baja (D-476)."""

    def congelamientos(self, presupuesto_id: int) -> List["Congelamiento"]:
        """Los nodos de ese presupuesto que se contrataron, del más viejo al más nuevo (D-475). Un nodo sin fila está en diseño."""

    def contratar(self, plan: "PlanDeContratacion") -> "ResultadoContratacion":
        """Escribe la contratación completa o nada: una carga de tipo `contratacion`, las versiones nuevas (la misma receta que la
        vigente, con el PU del plan), los renglones fijados a la versión vigente y el estado del nodo. Si la última carga ya no es
        `plan.base`, `CatalogoCambio`; si el nodo o uno de arriba ya está contratado, `YaContratado`."""

    def nodo(self, clave: str) -> "NodoDelCatalogo":
        """El nodo del catálogo con esa clave; `KeyError` si no existe (D-478)."""

    def citas_de(self, clave: str) -> "CitasDe":
        """Quién usa a ese nodo hoy: las matrices que lo citan en su versión vigente, con los renglones que fijan esa versión (D-478)."""

    def clones(self) -> List["ClonGuardado"]:
        """Todas las clonaciones, de la más vieja a la más nueva."""

    def clonar(self, plan: "PlanDeClonacion") -> "ResultadoClonacion":
        """Escribe la clonación completa o nada: una carga de tipo `clonacion`, el clon (con la receta y el precio del original), una versión
        nueva de cada concepto que se redirige —la misma receta con el clon en lugar del original— con sus renglones fijados a ella, y la
        fila de `CLON`. Si la última carga ya no es `plan.base`, `CatalogoCambio`; si la clave del clon existe, `ValueError`."""


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
    existentes: Optional[Mapping[str, PresupuestoExistente]] = None,
    bajas_confirmadas: Iterable[str] = (),
    todas_las_bajas: bool = False,
) -> Tuple[DiagnosticoDeCarga, PlanDeCarga]:
    """Puro: lo que haría cargar este archivo sobre lo vigente. No escribe ni lee nada más. `existentes` trae el contenido de los
    presupuestos guardados que el archivo trae distintos, para reconciliarlos."""
    from .reconciliacion import reconciliar

    confirmados = frozenset(confirmados)
    bajas_confirmadas = frozenset(bajas_confirmadas)
    existentes = existentes or {}
    matrices, leidas = canonizar_matrices(matrices, estado.homologaciones)  # la clave vieja que se sustituyó entra como su clon (D-478)
    if presupuesto is not None:
        presupuesto = canonizar_presupuesto(presupuesto, estado.homologaciones)
    unidades_de_concepto = {c: presupuesto.unidad_de(c) for c in presupuesto.conceptos} if presupuesto is not None else {}
    arbol = armar_arbol(matrices, unidades_de_concepto)
    problemas: List[str] = list(arbol.problemas) + (list(presupuesto.problemas) if presupuesto is not None else [])
    avisos: List[str] = [
        f"línea {l.linea}: {l.padre} → {l.hijo}: cantidad × costo no da el importe ({l.importe})" for l in matrices.importes_que_no_cuadran]
    if leidas:
        ejemplo = ", ".join(f"{v} → {n}" for v, n in leidas[:3]) + (" …" if len(leidas) > 3 else "")
        avisos.append(f"{len(leidas)} claves del archivo se sustituyeron por un clon y se leyeron como él ({ejemplo}); la clave vieja sigue entrando")
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

    # ---- los textos (§2.7.1, D-477): lo cosmético no alerta; lo informativo y lo alto se dicen; lo alto junto con la receta es otro concepto
    entrante: Dict[str, str] = {}
    for l in matrices.lineas:
        entrante.setdefault(l.hijo, l.descripcion)
    if presupuesto is not None:
        for c_, filas_ in presupuesto.conceptos.items():
            entrante[c_] = filas_[0].descripcion
    claves_del_catalogo = frozenset(estado.descripcion) | frozenset(padres) | frozenset(hojas)
    de_texto: List[Tuple[str, str, str, "DiferenciaDeTexto"]] = []  # (clave, antes, después, diferencia) de lo que llega distinto
    llenar: List[Tuple[str, str]] = []  # lo que existía sin texto y ahora lo trae
    for c, despues in sorted(entrante.items()):
        antes = estado.descripcion.get(c)
        if antes is None or not despues.strip():
            continue  # un nodo nuevo no tiene con qué compararse
        if not antes.strip():
            llenar.append((c, despues))
            continue
        dif = comparar(antes, despues)
        if not dif.alerta:
            continue
        de_texto.append((c, antes, despues, dif))
        if dif.nivel == ALTA and c in versionan and c not in confirmados and c not in retenido:
            propuesta = clave_nueva(c, claves_del_catalogo | frozenset(entrante))
            retenido[c] = TEXTO_Y_RECETA
            pendientes.append(Pendiente(
                c, TEXTO_Y_RECETA,
                f"el texto cambió ({dif.detalle}) y la matriz también: parece otro concepto; la clave nueva sería {propuesta}, o confírmalo si es el mismo"))

    for c in orden:
        if c not in nuevos and c not in versionan:
            if c not in retenido and not estado.unidad.get(c) and nuevo.unidad.get(c):
                unidades_que_se_saben.append((c, nuevo.unidad[c]))
            continue
        if retenido.get(c) == TEXTO_Y_RECETA:
            continue  # ya quedó dicho arriba
        if c in versionan and c in estado.en_contratado:
            retenido[c] = EN_CONTRATADO
            pendientes.append(Pendiente(c, EN_CONTRATADO, "lo fija un renglón contratado: el cambio de su matriz va a control de cambio"))
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
    reconciliaciones: List[ReconciliacionPlan] = []
    cambios_de_presupuesto: List[CambioDePresupuesto] = []
    sin_matriz: List[str] = []
    observados: List[Tuple[str, Decimal, Decimal]] = []
    creados = {n.clave for n in nodos_nuevos}

    def detenido_hoy(c: str) -> Optional[str]:
        """Por qué un concepto no puede entrar hoy a un presupuesto, o nulo si puede."""
        if c in retenido:
            return f"{c} quedó pendiente ({retenido[c]})"
        if c in sin_matriz and any((f.precio_observado or Decimal("0")) != 0 for f in presupuesto.conceptos.get(c, ())):
            return f"{c} trae precio y ninguna matriz"
        return None

    if presupuesto is not None and presupuesto.limpia:
        sin_matriz = sorted(c for c in presupuesto.conceptos if c not in matrices.por_padre and c not in estado.huella)
        for cap in presupuesto.capitulos():
            clave, nombre = cap.raiz.clave, cap.raiz.descripcion
            huella_p = huella_presupuesto(cap.filas)
            guardado = estado.presupuestos.get(clave)
            if guardado is not None:
                if guardado.huella == huella_p:
                    estados_p.append(EstadoDePresupuesto(clave, nombre, "sin_cambios"))
                    continue
                existente = existentes.get(clave)
                if existente is None:
                    raise ValueError(f"el presupuesto {clave} llega distinto y no se trajo su contenido para reconciliarlo")
                plan_r, cambios_r = reconciliar(
                    cap, existente.datos, existente.contratados, huella_del_archivo=huella_p, concepto_detenido=detenido_hoy,
                    bajas_confirmadas=bajas_confirmadas, todas_las_bajas=todas_las_bajas)
                cambios_de_presupuesto += cambios_r
                detenidos = [c for c in cambios_r if c.estado == "detenido"]
                aplican = [c for c in cambios_r if c.estado == "aplica"]
                for c in detenidos:
                    pendientes.append(Pendiente(c.id, c.motivo, f"{clave}: {c.tipo} de {c.clave}: {c.detalle}"))
                cuenta = {k: sum(1 for c in aplican if c.tipo == k) for k in ("cantidad", "alta", "baja")}
                detalle = f"{cuenta['cantidad']} cantidades · {cuenta['alta']} altas · {cuenta['baja']} bajas"
                if detenidos:
                    detalle += f" · {len(detenidos)} detenidos"
                estados_p.append(EstadoDePresupuesto(clave, nombre, "parcial" if detenidos else "reconciliado", detalle if cambios_r else "ya estaba igual"))
                if plan_r.cambia_algo or plan_r.huella:
                    reconciliaciones.append(plan_r)
                for al in plan_r.altas:
                    if al.tipo == "Concepto" and al.clave in sin_matriz and al.clave not in estado.unidad \
                            and al.clave not in {x.clave for x in conceptos_sin_matriz}:
                        fila = presupuesto.conceptos[al.clave][0]
                        conceptos_sin_matriz.append(ConceptoSinMatriz(al.clave, fila.descripcion, fila.unidad))
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

    # ---- lo que de los textos entra: nada de lo que quedó detenido por otra razón
    alertas_de_texto = tuple(
        AlertaDeTexto(c, antes, despues, dif.nivel, dif.motivo, dif.detalle, "detenido" if c in retenido else "carga",
                      clave_nueva(c, claves_del_catalogo | frozenset(entrante)) if retenido.get(c) == TEXTO_Y_RECETA else "")
        for c, antes, despues, dif in de_texto)
    descripciones = tuple([(c, despues) for c, _, despues, _ in de_texto if c not in retenido] + [(c, d) for c, d in llenar if c not in retenido])

    # ---- las unidades que hay que tener
    vistas: Dict[str, str] = {}
    for u in ([i.unidad for i in insumos_nuevos] + [n.unidad for n in nodos_nuevos + versiones_nuevas] + [c.unidad for c in conceptos_sin_matriz]
              + [u for _, u in unidades_que_se_saben] + [r.unidad for p in presupuestos_nuevos for r in p.renglones]
              + [a.unidad for r in reconciliaciones for a in r.altas]):
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
        "bajas_confirmadas": sorted(bajas_confirmadas) + (["todas"] if todas_las_bajas else []),
        "cambios_de_presupuesto": [
            {"presupuesto": c.presupuesto, "tipo": c.tipo, "id": c.id, "clave": c.clave, "antes": None if c.antes is None else str(c.antes),
             "ahora": None if c.ahora is None else str(c.ahora), "estado": c.estado, "motivo": c.motivo}
            for c in cambios_de_presupuesto[:TOPE_DE_CAMBIOS_EN_EL_RESUMEN]],
        "cambios_de_presupuesto_total": len(cambios_de_presupuesto),
        "alertas_de_texto": [
            {"clave": a.clave, "antes": a.antes, "despues": a.despues, "nivel": a.nivel, "motivo": a.motivo, "detalle": a.detalle, "estado": a.estado,
             "clave_propuesta": a.clave_propuesta} for a in alertas_de_texto[:TOPE_DE_CAMBIOS_EN_EL_RESUMEN]],
        "alertas_de_texto_total": len(alertas_de_texto),
    }
    diagnostico = DiagnosticoDeCarga(
        diag, len(insumos_nuevos), tuple(precios_que_cambian), tuple(pendientes), tuple(estados_p), tuple(sin_matriz), sin_unidad,
        tuple(observados), tuple(avisos), tuple(problemas), tuple(cambios_de_presupuesto), alertas_de_texto)
    plan = PlanDeCarga(
        estado.ultima_carga, usuario, rol, dict(archivos), resumen, tuple(vistas.values()), tuple(insumos_nuevos), tuple(precios_nuevos),
        tuple(unidades_que_se_saben), tuple(nodos_nuevos), tuple(versiones_nuevas), tuple(conceptos_sin_matriz), tuple(presupuestos_nuevos),
        tuple(reconciliaciones), descripciones)
    return diagnostico, plan


# --------------------------------------------------------------------------- el diagnóstico, en palabras

MOTIVOS = {
    UNIDAD_CAMBIO: "cambió la unidad",
    PRECIO_DE_TRABAJO: "el precio de un trabajo se valida",
    PU_MOVIO: "el PU se movió más de 5 %: pide confirmación",
    DEPENDE_DE: "depende de algo que quedó pendiente",
    EN_CONTRATADO: "lo usa algo contratado: va a control de cambio",
    BAJA_SIN_CONFIRMAR: "una baja pide confirmación",
    TEXTO_Y_RECETA: "el texto y la matriz cambiaron: parece otro concepto",
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
        etiqueta = {"nuevo": "se cargará", "sin_cambios": "ya está, igual", "reconciliado": "ya está y llega distinto: se reconcilia",
                    "parcial": "ya está y llega distinto: se reconcilia, con cambios detenidos", "pendiente": "pendiente"}
        o += [f"  {e.clave:<10} {e.nombre} — {etiqueta.get(e.estado, e.estado)}" + (f" ({e.detalle})" if e.detalle else "") for e in d.presupuestos]
    if d.cambios:
        o += ["", "Cambios en presupuestos que ya existen"]
        nombre_de_tipo = {"cantidad": "cantidad", "alta": "alta", "baja": "baja"}
        for c in d.cambios[:40]:
            valor = (f"{c.antes} → {c.ahora}" if c.tipo == "cantidad" else (f"× {c.ahora}" if c.tipo == "alta" else f"× {c.antes}"))
            marca = "" if c.estado == "aplica" else f"  [DETENIDO: {MOTIVOS.get(c.motivo, c.motivo)}]"
            o.append(f"  {c.presupuesto} · {nombre_de_tipo[c.tipo]:<8} {c.clave:<11} {valor}  ({c.id}){marca}")
        if len(d.cambios) > 40:
            o.append(f"  … y {len(d.cambios) - 40} más")
    if d.alertas_de_texto:
        o += ["", "Descripciones que cambiaron (§2.7.1)"]
        nivel = {"alta": "ALTA", "informativa": "informativa"}
        for a in d.alertas_de_texto[:30]:
            marca = "" if a.estado == "carga" else f"  [DETENIDO — clave nueva propuesta: {a.clave_propuesta}]" if a.clave_propuesta else "  [DETENIDO por otra razón]"
            o.append(f"  {a.clave:<12} {nivel.get(a.nivel, a.nivel):<11} {a.detalle}{marca}")
        if len(d.alertas_de_texto) > 30:
            o.append(f"  … y {len(d.alertas_de_texto) - 30} más")
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
        bajas_confirmadas: Iterable[str] = (),
        todas_las_bajas: bool = False,
    ) -> Revision:
        """Lee los archivos y dice qué haría cargarlos hoy. No escribe nada. `bajas_confirmadas` son los `id` de las bajas de renglones o
        bloques de presupuestos que ya existen que alguien confirmó (el informe los dice); `todas_las_bajas` las confirma todas."""
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
        estado = self.repo.estado_vigente()  # primero la última carga y después el contenido: si algo cambia en medio, el candado salta
        existentes: Dict[str, PresupuestoExistente] = {}
        if lectura is not None and lectura.limpia:
            from .contratacion import nodos_contratados

            for cap in canonizar_presupuesto(lectura, estado.homologaciones).capitulos():  # igual que lo lee `planificar`
                guardado = estado.presupuestos.get(cap.raiz.clave)
                if guardado is not None and guardado.huella != huella_presupuesto(cap.filas):
                    datos = self.repo.datos_de_presupuesto(guardado.id)
                    existentes[cap.raiz.clave] = PresupuestoExistente(
                        datos, frozenset(nodos_contratados(datos, self.repo.congelamientos(guardado.id))))
        d, plan = planificar(estado, matrices, lectura, usuario=usuario, rol=rol_con_que, archivos=archivos, tipo=tipo,
                             confirmados=confirmados, existentes=existentes, bajas_confirmadas=bajas_confirmadas, todas_las_bajas=todas_las_bajas)
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
        bajas_confirmadas: Iterable[str] = (),
        todas_las_bajas: bool = False,
    ) -> ResultadoCarga:
        """Revisa y aplica lo que entra. Lo detenido no se aplica y queda dicho en la carga. Si el archivo trae algo que no
        cuadra (`problemas`), no se escribe nada."""
        r = self.revisar(conceptos, presupuesto, compuestos, rol=rol, usuario=usuario, tipo=tipo, confirmados=confirmados,
                         bajas_confirmadas=bajas_confirmadas, todas_las_bajas=todas_las_bajas)
        if not r.diagnostico.aplicable:
            raise CargaNoProcede("el archivo trae algo que no cuadra: " + "; ".join(r.diagnostico.problemas))
        if not r.plan.cambia_algo and not r.diagnostico.pendientes:
            return ResultadoCarga(None, r.plan.resumen)
        return self.repo.aplicar(r.plan)

    # ---- lo que se lee de vuelta
    def presupuesto(self, presupuesto_id: int) -> PresupuestoGuardado:
        return armar_presupuesto(self.repo.datos_de_presupuesto(presupuesto_id))
