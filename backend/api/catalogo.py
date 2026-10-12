"""
La API del catálogo y los presupuestos de OPUS — D-482.

Hasta D-481 lo construido sobre el catálogo (cargar los archivos de OPUS, colgar el programa del presupuesto, contratar un subárbol,
clonar un insumo) solo se podía hacer desde la terminal. Aquí cada uno tiene su ruta, con la misma regla que ya tenían los servicios:
**el sistema propone y el humano decide**. Cada acción son dos rutas gemelas:

    POST …/propuestas   dice qué pasaría, con las mismas cifras que el informe de la terminal, y no escribe nada
    POST …              hace lo que se propuso; si lo propuesto no procede, responde con el motivo y no escribe nada

| Se hace                        | Propuesta                                          | Se aplica                                   | Función que pide           |
|--------------------------------|----------------------------------------------------|---------------------------------------------|----------------------------|
| Cargar los archivos de OPUS    | `POST /cargas/propuestas`                          | `POST /cargas`                              | `cargar_catalogo_opus`     |
| Colgar un programa             | `POST /programas/{id}/colgado/propuestas`          | `POST /programas/{id}/colgado`              | `editar_estructura_programa` |
| Contratar un subárbol          | `POST /presupuestos/{id}/contrataciones/propuestas`| `POST /presupuestos/{id}/contrataciones`    | `contratar_subarbol`       |
| Clonar un insumo               | `POST /clonaciones/propuestas`                     | `POST /clonaciones`                         | `clonar_insumo`            |
| Corregir un prefijo entero     | `POST /correcciones-de-prefijo/propuestas`         | `POST /correcciones-de-prefijo`             | `clonar_insumo`            |

Quién llama y qué puede hacer sale de `autenticacion.py`, igual que en las rutas del programa: el usuario que queda en la carga, la
colgadura, la contratación o la clonación es el que dice el token, y el rol con que queda es el primero de los suyos que tiene la función.
Las lecturas (`GET`) piden estar identificado y nada más.

**Cómo contesta cuando algo no procede** (el código va en `detail.codigo`):

- `403 permiso_denegado` — ningún rol de quien llama tiene la función.
- `404 presupuesto_inexistente · programa_inexistente · nodo_inexistente` — lo que se pide no existe.
- `409` — el estado cambió o ya está hecho: `conflicto` (otra carga se aplicó entre que se propuso y se aplicó),
  `ya_contratado`, `ya_colgado`, `reemplazado` (el programa ya tiene una versión nueva).
- `422` — lo pedido no procede y quien decide puede corregirlo: `carga_no_procede` (el archivo trae algo que no cuadra),
  `colgado_no_cuadra` (con `forzable` si de todos modos se puede confirmar), `confirmacion_pendiente` (con los conceptos que piden
  confirmarse; se reenvían en `confirmados`), `clonacion_no_procede` (con `problemas`), `contratacion_invalida`, `peticion_invalida`.

**Lo que se vio es lo que se aplica.** Cada propuesta dice en `base` la última carga que vio quien la pidió; al aplicar se manda en
`esperaba`. Si entre una y otra alguien cargó, contrató o clonó algo, no se escribe nada y se responde `409 conflicto`: lo que quien decide
vio ya no es lo de hoy, y se vuelve a proponer. Sin `esperaba` se aplica sobre lo que haya (como `esperaba` en las ediciones del programa).

El dinero y las cantidades van como texto —«1234.56»—, como en el resto de la API: no cruzan como número.
"""
from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, List, Optional

from fastapi import Depends, FastAPI
from pydantic import BaseModel, Field

from api.autenticacion import Autenticacion, Identidad
from api.errores import _error
from core.catalogo import (
    CatalogoCambio,
    DiagnosticoDeCarga,
    MOTIVOS,
    Pendiente,
    RepositorioCatalogo,
    ServicioCarga,
    YaContratado,
    armar_presupuesto,
    informe_de_carga,
)
from core.clonacion import (
    ClonacionNoProcede,
    PropuestaDeClonacion,
    ServicioClonacion,
    informe_de_clonacion,
    informe_de_correccion,
    informe_de_resultado,
)
from core.colgado import Alineacion, ColgadoNoCuadra, ServicioColgado, citas_de_bajas, informe_de_colgado
from core.contratacion import ContratacionPendiente, PropuestaDeContratacion, ServicioContratacion, informe_de_contratacion
from core.importacion_opus import CargaNoProcede
from core.servicio_programa import PermisoDenegado, ProgramaNoExiste, ServicioPrograma, YaColgado, YaReemplazado

TOPE_EN_RESPUESTA = 200  # de las listas que pueden ser de miles (lo que no casa en un colgado): el total siempre va entero


ESPERABA = ("La última carga que vio quien decide: el `base` de la propuesta. Al aplicar, si el catálogo ya va en otra, no se escribe nada y se "
            "responde 409: lo que vio ya no es lo de hoy. Sin ella se aplica sobre lo que haya. Las propuestas la ignoran.")


def _num(x: Optional[Decimal]) -> Optional[str]:
    """Un decimal como texto, sin notación científica: «1234.5600»."""
    return None if x is None else format(x, "f")


# --------------------------------------------------------------------------- lo que entra


class CargaEntrada(BaseModel):
    conceptos: str = Field(description="`ANALISIS_DE_BASICOS_CONCEPTOS.csv` tal como sale de OPUS: las matrices (APU) de los conceptos")
    presupuesto: Optional[str] = Field(None, description="`CATALOGO_DE_PRESUPUESTO.csv`: los presupuestos. Sin él, solo se carga el catálogo")
    compuestos: Optional[str] = Field(None, description="`ANALISIS_DE_BASICOS_COMPUESTOS.csv`, opcional: sus líneas ya vienen dentro del de conceptos")
    tipo: str = Field("plantilla", description="Qué son los presupuestos que se crean: plantilla · obra · escenario")
    confirmados: List[str] = Field(default_factory=list, description="Las claves de los conceptos cuyo PU se movió más de 5 % y alguien confirmó")
    bajas_confirmadas: List[str] = Field(default_factory=list, description="Los `id` de las bajas de renglones o bloques que alguien confirmó (la propuesta los da)")
    todas_las_bajas: bool = Field(False, description="Confirma todas las bajas de esta carga")
    esperaba: Optional[int] = Field(None, description=ESPERABA)


class ColgadoPropuestaEntrada(BaseModel):
    presupuesto_id: Optional[int] = Field(None, description="De cuál presupuesto; sin decirlo, el de la clave del capítulo con que abre el programa")


class ColgadoEntrada(ColgadoPropuestaEntrada):
    forzar: bool = Field(False, description="Confirma colgar aunque casen menos de la mitad de los conceptos del programa")


class ContratacionEntrada(BaseModel):
    bloque: Optional[str] = Field(None, description="La ruta natural del bloque (`clave#n/clave#n…`); sin decirla, el presupuesto entero")
    confirmados: List[str] = Field(default_factory=list, description="Las claves de los conceptos que piden confirmación y alguien confirmó")
    esperaba: Optional[int] = Field(None, description=ESPERABA)


class ClonacionEntrada(BaseModel):
    original: str = Field(min_length=1, description="La clave del insumo, compuesto o concepto que se clona")
    clave: str = Field(description="La clave del clon")
    modo: str = Field("sustituir", description="sustituir: lo que citaba al original pasa a citar al clon · mantener: los dos quedan vivos")
    esperaba: Optional[int] = Field(None, description=ESPERABA)


class CorreccionEntrada(BaseModel):
    viejo: str = Field(min_length=1, description="El prefijo que se corrige, p. ej. AUX")
    nuevo: str = Field(min_length=1, description="El prefijo nuevo, p. ej. PRE")
    desde: int = Field(1, ge=1, description="El número con que empieza la numeración nueva; se saltan los ocupados")
    esperaba: Optional[int] = Field(None, description=ESPERABA)


# --------------------------------------------------------------------------- lo que sale: una carga


class MatrizDetenida(BaseModel):
    clave: str
    unidad_vigente: str
    unidad_nueva: str


class MatricesSalida(BaseModel):
    entran: int = Field(description="Las matrices que llegan iguales: no cambian nada")
    nuevas: List[str]
    versionan: List[str] = Field(description="Cambió su receta: versión nueva, automática")
    detenidas: List[MatrizDetenida] = Field(description="Cambió la unidad: alguien decide")
    ausentes: List[str] = Field(description="Estaban y el archivo ya no las trae (informativo: no se borran)")


class PrecioQueCambia(BaseModel):
    clave: str
    antes: str
    ahora: str


class PrecioObservado(BaseModel):
    clave: str
    presupuesto: str = Field(description="El PU que trae el presupuesto de OPUS")
    matriz: str = Field(description="El que sale de la matriz con los precios de hoy")


class PendienteSalida(BaseModel):
    clave: str
    motivo: str
    detalle: str
    texto: str = Field(description="El motivo dicho en palabras")


class EstadoDePresupuestoSalida(BaseModel):
    clave: str
    nombre: str
    estado: str = Field(description="nuevo · sin_cambios · reconciliado · parcial · pendiente")
    detalle: str


class CambioSalida(BaseModel):
    presupuesto: str = Field(description="La clave del capítulo")
    tipo: str = Field(description="cantidad · alta · baja")
    id: str = Field(description="Con lo que se identifica; en una baja, lo que se confirma en `bajas_confirmadas`")
    clave: str
    descripcion: str
    es_bloque: bool
    antes: Optional[str]
    ahora: Optional[str]
    estado: str = Field(description="aplica · detenido")
    motivo: str
    detalle: str
    renglones: int = Field(description="De una baja: los renglones que se van con ella")
    bloques: int = Field(description="De una baja: los bloques que se van con ella")


class AlertaDeTextoSalida(BaseModel):
    clave: str
    antes: str
    despues: str
    nivel: str = Field(description="informativa · alta")
    motivo: str = Field(description="numero · palabra · orden · calificativo")
    detalle: str
    estado: str = Field(description="carga: la descripción nueva entra · detenido: con la receta, parece otro concepto")
    clave_propuesta: str


class CitaDeBajaSalida(BaseModel):
    baja: str = Field(description="El `id` de la baja")
    programa_id: int
    programa: str
    filas: int = Field(description="Cuántas filas del programa quedarían enlazadas a algo dado de baja")


class DiagnosticoSalida(BaseModel):
    aplicable: bool = Field(description="Falso si el archivo trae algo que no cuadra (`problemas`): no se escribe nada")
    matrices: MatricesSalida
    insumos_nuevos: int
    precios_que_cambian: List[PrecioQueCambia]
    pendientes: List[PendienteSalida] = Field(description="Lo que no se aplica y queda dicho en la carga")
    presupuestos: List[EstadoDePresupuestoSalida]
    cambios: List[CambioSalida] = Field(description="Lo que cambia en los presupuestos que ya existían")
    alertas_de_texto: List[AlertaDeTextoSalida]
    sin_matriz: List[str]
    sin_unidad: List[str]
    precios_observados_distintos: List[PrecioObservado]
    avisos: List[str]
    problemas: List[str]


class RevisionSalida(BaseModel):
    diagnostico: DiagnosticoSalida
    base: int = Field(description="La última carga que vio quien revisó: se manda en `esperaba` al aplicar; si ya hay otra, 409")
    resumen: Dict[str, Any]
    citan_las_bajas: List[CitaDeBajaSalida] = Field(description="Qué programas citan lo que se da de baja")
    informe: str = Field(description="El mismo informe que imprime la terminal")


class CargaAplicadaSalida(BaseModel):
    carga_id: Optional[int] = Field(description="Nulo si no había nada que aplicar")
    resumen: Dict[str, Any]


class ResumenCargaSalida(BaseModel):
    id: int
    creada_en: datetime
    usuario: str
    rol: str
    archivos: Dict[str, str] = Field(description="De cada archivo que se cargó, su huella sha256")
    resumen: Dict[str, Any]
    tipo: str = Field(description="archivos · contratacion · clonacion")


# --------------------------------------------------------------------------- lo que sale: colgar, contratar, clonar


class SinParSalida(BaseModel):
    oid: str
    fila: int
    tipo: str
    clave: str
    descripcion: str
    motivo: str


class SinProgramarSalida(BaseModel):
    clave: str
    descripcion: str
    ruta: str
    cantidad: Optional[str] = None
    renglon: bool


class AlineacionSalida(BaseModel):
    programa_id: int
    presupuesto_id: int
    presupuesto_clave: str
    casa_bien: bool = Field(description="Casa al menos la mitad de los conceptos del programa: si no, casi seguro es otro presupuesto")
    casan_los_conceptos: float
    enlaces: int = Field(description="Los que cuadran, también los que el programa ya tenía puestos")
    nuevos: int = Field(description="Los que `colgar` puso; cero en una propuesta")
    ya_estaban: int
    bloques: int
    partidas: int
    conceptos_del_programa: int
    bloques_del_programa: int
    vacias: int = Field(description="Marcadores vacíos de OPUS: ni casados ni faltantes")
    se_moverian: List[str] = Field(description="Los `oid` cuyo enlace puesto es otro: un enlace puesto no se mueve")
    huerfanos: List[str] = Field(description="Los `oid` enlazados a algo que el presupuesto dio de baja")
    sin_par: List[SinParSalida] = Field(description=f"Filas del programa sin con qué casarse (las primeras {TOPE_EN_RESPUESTA})")
    sin_par_total: int
    sin_programar: List[SinProgramarSalida] = Field(description=f"Dinero sin fecha: lo del presupuesto que ninguna fila reclamó (las primeras {TOPE_EN_RESPUESTA})")
    sin_programar_total: int
    informe: str


class ConceptoPorFijarSalida(BaseModel):
    clave: str
    descripcion: str
    renglones: int
    version_fijada: Optional[int]
    version_vigente: Optional[int]
    pu_fijado: str
    pu_hoy: str
    accion: str = Field(description="igual · fijar_vigente · version_nueva")
    cambia: bool


class ContratacionPropuestaSalida(BaseModel):
    base: int = Field(description="La última carga que vio quien revisó: se manda en `esperaba` al contratar")
    presupuesto_id: int
    presupuesto_clave: str
    nodo_id: int
    ruta: str
    descripcion: str
    aplicable: bool = Field(description="Falso si algún concepto pide confirmación (`pendientes`)")
    renglones: int
    ya_contratados: int
    total_antes: str
    total_despues: str
    diferencia: str
    conceptos: List[ConceptoPorFijarSalida]
    pendientes: List[PendienteSalida]
    informe: str


class ContratacionSalida(BaseModel):
    propuesta: ContratacionPropuestaSalida
    carga_id: int
    congelamiento_id: int
    versiones_nuevas: int
    renglones_fijados: int


class CongelamientoSalida(BaseModel):
    id: int
    nodo_id: int
    ruta: str
    estado: str
    fecha: datetime
    usuario: str
    rol: str
    carga_id: int
    resumen: Dict[str, Any]


class PadreRedirigidoSalida(BaseModel):
    clave: str
    version_antes: int
    version_despues: int
    renglones: int
    pu: str


class ClonacionPropuestaSalida(BaseModel):
    base: Optional[int] = Field(description="La última carga que vio quien revisó: se manda en `esperaba` al clonar. Nulo si no se puede clonar")
    original: str
    clave: str
    modo: str
    descripcion: str
    unidad: str
    tipo: str = Field(description="insumo · compuesto · concepto sin matriz")
    aplicable: bool
    problemas: List[str] = Field(description="Lo que impide hacerla: el original no se toca")
    redirigidos: List[PadreRedirigidoSalida]
    renglones: int = Field(description="Los renglones de presupuesto que pasan a fijar la versión nueva")
    informe: str


class ClonacionSalida(BaseModel):
    propuesta: ClonacionPropuestaSalida
    carga_id: int
    nodo_id: int = Field(description="El nodo del catálogo que nació: el clon")
    versiones_nuevas: int
    renglones_fijados: int


class ParDeCorreccion(BaseModel):
    original: str
    clon: str
    descripcion: str
    aplicable: bool
    renglones: int
    versiones_nuevas: int
    problemas: List[str]


class ParHecho(BaseModel):
    original: str
    clon: str


class CorreccionPropuestaSalida(BaseModel):
    base: int = Field(description="La última carga que vio quien revisó: se manda en `esperaba` al corregir el prefijo")
    viejo: str
    nuevo: str
    pares: List[ParDeCorreccion] = Field(description="Lo que falta por hacer, en el orden en que se hace, cada uno con lo que haría hoy")
    hechos: List[ParHecho] = Field(description="Lo que ya se sustituyó")
    omitidos: List[str] = Field(description="Claves del prefijo que no terminan en un número: no se proponen")
    rechazadas: int
    informe: str


class ClonHechoSalida(BaseModel):
    original: str
    clon: str
    carga_id: int
    versiones_nuevas: int
    renglones_fijados: int


class ClonRechazadoSalida(BaseModel):
    original: str
    clon: str
    problemas: List[str]


class CorreccionSalida(BaseModel):
    hechos: List[ClonHechoSalida]
    rechazados: List[ClonRechazadoSalida] = Field(description="Lo que hoy no se puede (algo contratado lo cita): se salta y se dice; el resto se hace")
    versiones_nuevas: int
    renglones_fijados: int
    informe: str


# --------------------------------------------------------------------------- lo que sale: lo guardado


class ResumenPresupuestoSalida(BaseModel):
    id: int
    clave: str = Field(description="La clave del capítulo: con ella se reconoce al volver a cargar")
    nombre: str
    tipo: str
    huella: str
    carga_id: int
    renglones: int


class RenglonSalida(BaseModel):
    posicion: int
    padre: Optional[int]
    wbs: str
    nivel: int
    tipo: str
    clave: str
    descripcion: str
    unidad: str
    cantidad: str
    pu: str
    total: str
    version: Optional[int] = Field(description="La versión del concepto que el renglón fijó")


class PresupuestoSalida(BaseModel):
    resumen: ResumenPresupuestoSalida
    total: str
    renglones: List[RenglonSalida]


class LineaDeMatrizSalida(BaseModel):
    hijo: str
    cantidad: str
    orden: int
    reporta_a: str
    porcentaje: bool


class VersionDeMatrizSalida(BaseModel):
    clave: str
    version: int
    huella: str
    pu: str
    vigente_desde: datetime
    carga_id: int
    lineas: List[LineaDeMatrizSalida]


class PrecioSalida(BaseModel):
    clave: str
    precio: str
    vigente_desde: datetime
    vigente_hasta: Optional[datetime] = None
    carga_id: Optional[int] = None


class PadreCitanteSalida(BaseModel):
    clave: str
    version: int
    pu: str
    renglones: int


class NodoSalida(BaseModel):
    clave: str
    descripcion: str
    unidad: str
    rol: str = Field(description="insumo · ensamble · concepto")
    categoria: str
    procedencia: str
    precio: Optional[str] = Field(None, description="El vigente, de un insumo con historia de precio")
    con_matriz: bool
    citado_por: List[PadreCitanteSalida] = Field(description="Las matrices que lo citan en su versión vigente")
    renglones_directos: int = Field(description="Los renglones de presupuesto que lo ponen directo")
    sustituido_por: Optional[str] = Field(None, description="Si ya se sustituyó por un clon, la clave vigente")


class ClonSalida(BaseModel):
    id: int
    original: str
    clon: str
    modo: str
    reconoce_clave_vieja_al_importar: bool
    exporta_clave_vieja: bool = Field(description="Solo la bandera: sigue saliendo con la clave vieja hasta que alguien autorice lo contrario (B-08)")
    usuario: str
    rol: str
    carga_id: int
    resumen: Dict[str, Any]
    creada_en: datetime


# --------------------------------------------------------------------------- de lo que devuelve el dominio a lo que sale


def _pendiente(p: Pendiente) -> PendienteSalida:
    return PendienteSalida(clave=p.clave, motivo=p.motivo, detalle=p.detalle, texto=MOTIVOS.get(p.motivo, p.motivo))


def _diagnostico(d: DiagnosticoDeCarga) -> DiagnosticoSalida:
    g = d.diagnostico
    return DiagnosticoSalida(
        aplicable=d.aplicable,
        matrices=MatricesSalida(
            entran=len(g.entran), nuevas=list(g.nuevos), versionan=list(g.versionan), ausentes=list(g.ausentes),
            detenidas=[MatrizDetenida(clave=x.clave, unidad_vigente=x.unidad_vigente, unidad_nueva=x.unidad_nueva) for x in g.detenidos]),
        insumos_nuevos=d.insumos_nuevos,
        precios_que_cambian=[PrecioQueCambia(clave=c, antes=_num(a), ahora=_num(b)) for c, a, b in d.precios_que_cambian],
        pendientes=[_pendiente(p) for p in d.pendientes],
        presupuestos=[EstadoDePresupuestoSalida(clave=e.clave, nombre=e.nombre, estado=e.estado, detalle=e.detalle) for e in d.presupuestos],
        cambios=[CambioSalida(presupuesto=c.presupuesto, tipo=c.tipo, id=c.id, clave=c.clave, descripcion=c.descripcion, es_bloque=c.es_bloque,
                              antes=_num(c.antes), ahora=_num(c.ahora), estado=c.estado, motivo=c.motivo, detalle=c.detalle,
                              renglones=len(c.renglones), bloques=len(c.bloques)) for c in d.cambios],
        alertas_de_texto=[AlertaDeTextoSalida(clave=a.clave, antes=a.antes, despues=a.despues, nivel=a.nivel, motivo=a.motivo, detalle=a.detalle,
                                              estado=a.estado, clave_propuesta=a.clave_propuesta) for a in d.alertas_de_texto],
        sin_matriz=list(d.sin_matriz), sin_unidad=list(d.sin_unidad),
        precios_observados_distintos=[PrecioObservado(clave=c, presupuesto=_num(o), matriz=_num(m)) for c, o, m in d.precios_observados_distintos],
        avisos=list(d.avisos), problemas=list(d.problemas),
    )


def _alineacion(a: Alineacion) -> AlineacionSalida:
    return AlineacionSalida(
        programa_id=a.programa_id, presupuesto_id=a.presupuesto_id, presupuesto_clave=a.presupuesto_clave, casa_bien=a.casa_bien,
        casan_los_conceptos=a.casan_los_conceptos, enlaces=len(a.enlaces), nuevos=a.nuevos, ya_estaban=a.ya_estaban, bloques=a.bloques,
        partidas=a.partidas, conceptos_del_programa=a.conceptos_del_programa, bloques_del_programa=a.bloques_del_programa, vacias=a.vacias,
        se_moverian=list(a.se_moverian), huerfanos=list(a.huerfanos),
        sin_par=[SinParSalida(oid=s.oid, fila=s.fila, tipo=s.tipo, clave=s.clave, descripcion=s.descripcion, motivo=s.motivo)
                 for s in a.sin_par[:TOPE_EN_RESPUESTA]],
        sin_par_total=len(a.sin_par),
        sin_programar=[SinProgramarSalida(clave=s.clave, descripcion=s.descripcion, ruta=s.ruta, cantidad=s.cantidad, renglon=s.renglon)
                       for s in a.sin_programar[:TOPE_EN_RESPUESTA]],
        sin_programar_total=len(a.sin_programar),
        informe=informe_de_colgado(a),
    )


def _contratacion(p: PropuestaDeContratacion) -> ContratacionPropuestaSalida:
    return ContratacionPropuestaSalida(
        base=p.plan.base, presupuesto_id=p.presupuesto_id, presupuesto_clave=p.presupuesto_clave, nodo_id=p.nodo_id, ruta=p.ruta, descripcion=p.descripcion,
        aplicable=p.aplicable, renglones=p.renglones, ya_contratados=p.ya_contratados, total_antes=_num(p.total_antes),
        total_despues=_num(p.total_despues), diferencia=_num(p.diferencia),
        conceptos=[ConceptoPorFijarSalida(clave=c.clave, descripcion=c.descripcion, renglones=c.renglones, version_fijada=c.version_fijada,
                                          version_vigente=c.version_vigente, pu_fijado=_num(c.pu_fijado), pu_hoy=_num(c.pu_hoy),
                                          accion=c.accion, cambia=c.cambia) for c in p.conceptos],
        pendientes=[_pendiente(x) for x in p.pendientes],
        informe=informe_de_contratacion(p),
    )


def _clonacion(p: PropuestaDeClonacion) -> ClonacionPropuestaSalida:
    return ClonacionPropuestaSalida(
        base=None if p.plan is None else p.plan.base, original=p.original, clave=p.clave, modo=p.modo, descripcion=p.descripcion, unidad=p.unidad, tipo=p.tipo, aplicable=p.aplicable,
        problemas=list(p.problemas), renglones=p.renglones, informe=informe_de_clonacion(p),
        redirigidos=[PadreRedirigidoSalida(clave=r.clave, version_antes=r.version_antes, version_despues=r.version_despues,
                                           renglones=r.renglones, pu=_num(r.pu)) for r in p.redirigidos],
    )


def _conflicto(e: CatalogoCambio) -> Any:
    return _error(409, "conflicto", f"Alguien cargó algo en el catálogo mientras decidías. Vuelve a revisarlo. ({e})")


def _denegado(e: PermisoDenegado) -> Any:
    return _error(403, "permiso_denegado", str(e))


# --------------------------------------------------------------------------- las rutas


def registrar_catalogo(app: FastAPI, servicio: ServicioPrograma, catalogo: RepositorioCatalogo, auth: Autenticacion) -> None:
    """Agrega a `app` las rutas del catálogo, los presupuestos y lo que se hace con ellos. Los permisos se leen de la misma tabla que usa el
    servicio del programa (`ROL_FUNCION` tal como está hoy)."""
    identidad, lectura = auth.identidad, auth.lectura
    permisos = servicio.tabla_de_permisos
    carga = ServicioCarga(catalogo, permisos=permisos)
    colgado = ServicioColgado(servicio, catalogo)
    contratacion = ServicioContratacion(catalogo, permisos=permisos)
    clonacion = ServicioClonacion(catalogo, permisos=permisos)

    def existe_presupuesto(presupuesto_id: int) -> None:
        if all(p.id != presupuesto_id for p in catalogo.presupuestos()):
            raise _error(404, "presupuesto_inexistente", f"No hay un presupuesto {presupuesto_id}.")

    def existe_nodo(clave: str) -> None:
        try:
            catalogo.id_de(clave)
        except KeyError:
            raise _error(404, "nodo_inexistente", f"No hay un insumo, compuesto o concepto con la clave {clave}.") from None

    # ---- lo guardado
    @app.get("/presupuestos", response_model=List[ResumenPresupuestoSalida], operation_id="listar_presupuestos", dependencies=[Depends(lectura)],
             summary="Los presupuestos cargados")
    def listar_presupuestos() -> List[ResumenPresupuestoSalida]:
        return [ResumenPresupuestoSalida(**p.__dict__) for p in catalogo.presupuestos()]

    @app.get("/presupuestos/{presupuesto_id}", response_model=PresupuestoSalida, operation_id="ver_presupuesto", dependencies=[Depends(lectura)],
             summary="Un presupuesto: renglón por renglón, con su cantidad, su PU y su total")
    def ver_presupuesto(presupuesto_id: int) -> PresupuestoSalida:
        existe_presupuesto(presupuesto_id)
        g = armar_presupuesto(catalogo.datos_de_presupuesto(presupuesto_id))
        return PresupuestoSalida(
            resumen=ResumenPresupuestoSalida(**g.resumen.__dict__), total=_num(g.total),
            renglones=[RenglonSalida(posicion=r.posicion, padre=r.padre, wbs=r.wbs, nivel=r.nivel, tipo=r.tipo, clave=r.clave,
                                     descripcion=r.descripcion, unidad=r.unidad, cantidad=_num(r.cantidad), pu=_num(r.pu), total=_num(r.total),
                                     version=r.version) for r in g.renglones])

    @app.get("/presupuestos/{presupuesto_id}/contratados", response_model=List[CongelamientoSalida], operation_id="ver_contratados",
             dependencies=[Depends(lectura)], summary="Los bloques del presupuesto que ya se contrataron")
    def ver_contratados(presupuesto_id: int) -> List[CongelamientoSalida]:
        existe_presupuesto(presupuesto_id)
        return [CongelamientoSalida(id=c.id, nodo_id=c.nodo_id, ruta=c.ruta, estado=c.estado, fecha=c.fecha, usuario=c.usuario, rol=c.rol,
                                    carga_id=c.carga_id, resumen=dict(c.resumen)) for c in catalogo.congelamientos(presupuesto_id)]

    @app.get("/cargas", response_model=List[ResumenCargaSalida], operation_id="listar_cargas", dependencies=[Depends(lectura)],
             summary="Todo lo que se ha cargado, contratado o clonado, con quién y cuándo")
    def listar_cargas() -> List[ResumenCargaSalida]:
        return [ResumenCargaSalida(id=c.id, creada_en=c.creada_en, usuario=c.usuario, rol=c.rol, archivos=dict(c.archivos), resumen=dict(c.resumen),
                                   tipo=c.tipo) for c in catalogo.cargas()]

    @app.get("/catalogo/{clave}", response_model=NodoSalida, operation_id="ver_nodo", dependencies=[Depends(lectura)],
             summary="Un insumo, compuesto o concepto del catálogo, con quién lo cita")
    def ver_nodo(clave: str) -> NodoSalida:
        existe_nodo(clave)
        n = catalogo.nodo(clave)
        citas = catalogo.citas_de(clave)
        sustituido = next((c.clon for c in catalogo.clones() if c.original == clave and c.modo == "sustituir"), None)
        return NodoSalida(
            clave=n.clave, descripcion=n.descripcion, unidad=n.unidad, rol=n.rol, categoria=n.categoria, procedencia=n.procedencia,
            precio=_num(n.precio), con_matriz=n.con_matriz, renglones_directos=citas.renglones_directos, sustituido_por=sustituido,
            citado_por=[PadreCitanteSalida(clave=p.clave, version=p.version, pu=_num(p.pu), renglones=len(p.renglones)) for p in citas.padres])

    @app.get("/catalogo/{clave}/versiones", response_model=List[VersionDeMatrizSalida], operation_id="ver_versiones_de_matriz",
             dependencies=[Depends(lectura)], summary="Las versiones de la matriz (APU) de un concepto o compuesto, con sus líneas")
    def ver_versiones_de_matriz(clave: str) -> List[VersionDeMatrizSalida]:
        existe_nodo(clave)
        return [VersionDeMatrizSalida(
            clave=v.clave, version=v.version, huella=v.huella, pu=_num(v.pu), vigente_desde=v.vigente_desde, carga_id=v.carga_id,
            lineas=[LineaDeMatrizSalida(hijo=l.hijo, cantidad=_num(l.cantidad), orden=l.orden, reporta_a=l.reporta_a, porcentaje=l.porcentaje)
                    for l in v.lineas]) for v in catalogo.versiones(clave)]

    @app.get("/catalogo/{clave}/precios", response_model=List[PrecioSalida], operation_id="ver_precios", dependencies=[Depends(lectura)],
             summary="La historia de precio de un insumo")
    def ver_precios(clave: str) -> List[PrecioSalida]:
        existe_nodo(clave)
        return [PrecioSalida(clave=p.clave, precio=_num(p.precio), vigente_desde=p.vigente_desde, vigente_hasta=p.vigente_hasta, carga_id=p.carga_id)
                for p in catalogo.precios(clave)]

    @app.get("/clones", response_model=List[ClonSalida], operation_id="listar_clones", dependencies=[Depends(lectura)],
             summary="Los insumos clonados y sustituidos, y quién lo decidió")
    def listar_clones() -> List[ClonSalida]:
        return [ClonSalida(id=c.id, original=c.original, clon=c.clon, modo=c.modo, reconoce_clave_vieja_al_importar=c.reconoce_clave_vieja_al_importar,
                           exporta_clave_vieja=c.exporta_clave_vieja, usuario=c.usuario, rol=c.rol, carga_id=c.carga_id, resumen=dict(c.resumen),
                           creada_en=c.creada_en) for c in catalogo.clones()]

    # ---- cargar los archivos de OPUS
    def revisar(entrada: CargaEntrada, quien: Identidad):
        try:
            return carga.revisar(
                entrada.conceptos, entrada.presupuesto, entrada.compuestos, rol=quien.roles, usuario=quien.usuario, tipo=entrada.tipo,
                confirmados=entrada.confirmados, bajas_confirmadas=entrada.bajas_confirmadas, todas_las_bajas=entrada.todas_las_bajas)
        except PermisoDenegado as e:
            raise _denegado(e) from None
        except CargaNoProcede as e:
            raise _error(422, "carga_no_procede", f"No se pudo leer: {e}") from None
        except ValueError as e:
            raise _error(422, "peticion_invalida", str(e)) from None

    @app.post("/cargas/propuestas", response_model=RevisionSalida, operation_id="proponer_carga",
              summary="Qué pasaría si se cargaran estos archivos de OPUS: no escribe nada")
    def proponer_carga(entrada: CargaEntrada, quien: Identidad = Depends(identidad)) -> RevisionSalida:
        r = revisar(entrada, quien)
        citas = citas_de_bajas(servicio.repo, r.diagnostico.cambios)
        return RevisionSalida(
            diagnostico=_diagnostico(r.diagnostico), base=r.plan.base, resumen=dict(r.plan.resumen), informe=informe_de_carga(r.diagnostico),
            citan_las_bajas=[CitaDeBajaSalida(baja=c.baja, programa_id=c.programa_id, programa=c.programa, filas=c.filas) for c in citas])

    @app.post("/cargas", response_model=CargaAplicadaSalida, status_code=201, operation_id="aplicar_carga",
              summary="Cargar los archivos de OPUS: entra lo que se propuso, lo detenido queda dicho en la carga")
    def aplicar_carga(entrada: CargaEntrada, quien: Identidad = Depends(identidad)) -> CargaAplicadaSalida:
        try:
            r = carga.aplicar(
                entrada.conceptos, entrada.presupuesto, entrada.compuestos, rol=quien.roles, usuario=quien.usuario, tipo=entrada.tipo,
                confirmados=entrada.confirmados, bajas_confirmadas=entrada.bajas_confirmadas, todas_las_bajas=entrada.todas_las_bajas,
                esperaba=entrada.esperaba)
        except PermisoDenegado as e:
            raise _denegado(e) from None
        except CargaNoProcede as e:
            raise _error(422, "carga_no_procede", f"No se pudo: {e}") from None
        except CatalogoCambio as e:
            raise _conflicto(e) from None
        except ValueError as e:
            raise _error(422, "peticion_invalida", str(e)) from None
        return CargaAplicadaSalida(carga_id=r.carga_id, resumen=dict(r.resumen))

    # ---- colgar un programa del presupuesto
    def colgar_o_proponer(programa_id: int, presupuesto_id: Optional[int], quien: Identidad, forzar: Optional[bool]) -> Alineacion:
        try:
            if forzar is None:
                return colgado.proponer(programa_id, quien.roles, presupuesto_id)
            return colgado.colgar(programa_id, quien.roles, quien.usuario, presupuesto_id, forzar=forzar)
        except PermisoDenegado as e:
            raise _denegado(e) from None
        except ProgramaNoExiste:
            raise _error(404, "programa_inexistente", f"No hay un programa {programa_id}.") from None
        except YaReemplazado as e:
            raise _error(409, "reemplazado", f"Ese programa ya tiene una versión más nueva, la {e.por}: ahí se cuelga; éste queda como estaba.",
                         reemplazado_por=e.por) from None
        except YaColgado as e:
            raise _error(409, "ya_colgado", str(e), presupuesto_id=e.presupuesto_id) from None
        except ColgadoNoCuadra as e:
            a = e.alineacion
            raise _error(422, "colgado_no_cuadra", str(e), forzable=bool(a is not None and a.enlaces and not a.casa_bien and not a.se_moverian),
                         alineacion=None if a is None else _alineacion(a).model_dump(mode="json")) from None
        except ValueError as e:
            raise _error(422, "peticion_invalida", str(e)) from None

    @app.post("/programas/{programa_id}/colgado/propuestas", response_model=AlineacionSalida, operation_id="proponer_colgado",
              summary="Cómo quedaría colgado el programa del presupuesto, de los dos lados: no escribe nada")
    def proponer_colgado(programa_id: int, entrada: ColgadoPropuestaEntrada, quien: Identidad = Depends(identidad)) -> AlineacionSalida:
        return _alineacion(colgar_o_proponer(programa_id, entrada.presupuesto_id, quien, None))

    @app.post("/programas/{programa_id}/colgado", response_model=AlineacionSalida, status_code=201, operation_id="colgar_programa",
              summary="Colgar el programa del presupuesto: se ponen los enlaces que casan; uno puesto no se mueve")
    def colgar_programa(programa_id: int, entrada: ColgadoEntrada, quien: Identidad = Depends(identidad)) -> AlineacionSalida:
        return _alineacion(colgar_o_proponer(programa_id, entrada.presupuesto_id, quien, entrada.forzar))

    # ---- contratar un subárbol
    def contratar_o_proponer(presupuesto_id: int, entrada: ContratacionEntrada, quien: Identidad, contratar: bool):
        existe_presupuesto(presupuesto_id)
        try:
            if contratar:
                return contratacion.contratar(presupuesto_id, quien.roles, quien.usuario, entrada.bloque, entrada.confirmados, entrada.esperaba)
            return contratacion.proponer(presupuesto_id, quien.roles, quien.usuario, entrada.bloque, entrada.confirmados)
        except PermisoDenegado as e:
            raise _denegado(e) from None
        except ContratacionPendiente as e:
            raise _error(422, "confirmacion_pendiente", str(e), pendientes=[_pendiente(x).model_dump() for x in e.propuesta.pendientes]) from None
        except YaContratado as e:
            raise _error(409, "ya_contratado", str(e), nodo_id=e.nodo_id) from None
        except CatalogoCambio as e:
            raise _conflicto(e) from None
        except ValueError as e:
            raise _error(422, "contratacion_invalida", str(e)) from None

    @app.post("/presupuestos/{presupuesto_id}/contrataciones/propuestas", response_model=ContratacionPropuestaSalida,
              operation_id="proponer_contratacion", summary="Qué PU se fijarían al contratar un bloque y cuánto cambia el monto: no escribe nada")
    def proponer_contratacion(presupuesto_id: int, entrada: ContratacionEntrada, quien: Identidad = Depends(identidad)) -> ContratacionPropuestaSalida:
        return _contratacion(contratar_o_proponer(presupuesto_id, entrada, quien, False))

    @app.post("/presupuestos/{presupuesto_id}/contrataciones", response_model=ContratacionSalida, status_code=201, operation_id="contratar_subarbol",
              summary="Contratar un bloque del presupuesto: fija el PU de sus conceptos a hoy y lo congela")
    def contratar_subarbol(presupuesto_id: int, entrada: ContratacionEntrada, quien: Identidad = Depends(identidad)) -> ContratacionSalida:
        p, r = contratar_o_proponer(presupuesto_id, entrada, quien, True)
        return ContratacionSalida(propuesta=_contratacion(p), carga_id=r.carga_id, congelamiento_id=r.congelamiento_id,
                                  versiones_nuevas=r.versiones_nuevas, renglones_fijados=r.renglones_fijados)

    # ---- clonar un insumo, o corregir un prefijo entero
    @app.post("/clonaciones/propuestas", response_model=ClonacionPropuestaSalida, operation_id="proponer_clonacion",
              summary="Qué pasaría si se clonara un insumo: lo que lo cita y lo que impide hacerlo; no escribe nada")
    def proponer_clonacion(entrada: ClonacionEntrada, quien: Identidad = Depends(identidad)) -> ClonacionPropuestaSalida:
        try:
            return _clonacion(clonacion.proponer(entrada.original, entrada.clave, entrada.modo, quien.roles, quien.usuario))
        except PermisoDenegado as e:
            raise _denegado(e) from None
        except ValueError as e:
            raise _error(422, "peticion_invalida", str(e)) from None

    @app.post("/clonaciones", response_model=ClonacionSalida, status_code=201, operation_id="clonar_insumo",
              summary="Clonar un insumo (y, si se pide, sustituir el original): la clave vieja sigue entrando")
    def clonar_insumo(entrada: ClonacionEntrada, quien: Identidad = Depends(identidad)) -> ClonacionSalida:
        try:
            p, r = clonacion.clonar(entrada.original, entrada.clave, entrada.modo, quien.roles, quien.usuario, entrada.esperaba)
        except PermisoDenegado as e:
            raise _denegado(e) from None
        except ClonacionNoProcede as e:
            raise _error(422, "clonacion_no_procede", str(e), problemas=list(e.problemas)) from None
        except CatalogoCambio as e:
            raise _conflicto(e) from None
        except ValueError as e:
            raise _error(422, "peticion_invalida", str(e)) from None
        return ClonacionSalida(propuesta=_clonacion(p), carga_id=r.carga_id, nodo_id=r.clon_id, versiones_nuevas=r.versiones_nuevas,
                               renglones_fijados=r.renglones_fijados)

    @app.post("/correcciones-de-prefijo/propuestas", response_model=CorreccionPropuestaSalida, operation_id="proponer_correccion_de_prefijo",
              summary="Qué claves de un prefijo pasarían a otro, cada una con lo que la cita hoy: no escribe nada")
    def proponer_correccion_de_prefijo(entrada: CorreccionEntrada, quien: Identidad = Depends(identidad)) -> CorreccionPropuestaSalida:
        try:
            c = clonacion.proponer_correccion_de_prefijo(entrada.viejo, entrada.nuevo, entrada.desde, quien.roles, quien.usuario)
        except PermisoDenegado as e:
            raise _denegado(e) from None
        except ValueError as e:
            raise _error(422, "peticion_invalida", str(e)) from None
        por_original = {p.original: p for p in c.propuestas}
        return CorreccionPropuestaSalida(
            base=c.base, viejo=c.viejo, nuevo=c.nuevo, hechos=[ParHecho(original=o, clon=k) for o, k in c.hechos], omitidos=list(c.omitidos),
            rechazadas=len(c.rechazadas), informe=informe_de_correccion(c),
            pares=[ParDeCorreccion(original=o, clon=k, descripcion=por_original[o].descripcion, aplicable=por_original[o].aplicable,
                                   renglones=por_original[o].renglones, versiones_nuevas=len(por_original[o].redirigidos),
                                   problemas=list(por_original[o].problemas)) for o, k in c.pares])

    @app.post("/correcciones-de-prefijo", response_model=CorreccionSalida, status_code=201, operation_id="corregir_prefijo",
              summary="Sustituir cada clave de un prefijo por su clon con el prefijo nuevo; lo que hoy no se puede se salta y se dice")
    def corregir_prefijo(entrada: CorreccionEntrada, quien: Identidad = Depends(identidad)) -> CorreccionSalida:
        try:
            r = clonacion.corregir_prefijo(entrada.viejo, entrada.nuevo, entrada.desde, quien.roles, quien.usuario, entrada.esperaba)
        except PermisoDenegado as e:
            raise _denegado(e) from None
        except CatalogoCambio as e:
            raise _conflicto(e) from None
        except ValueError as e:
            raise _error(422, "peticion_invalida", str(e)) from None
        return CorreccionSalida(
            hechos=[ClonHechoSalida(original=o, clon=k, carga_id=x.carga_id, versiones_nuevas=x.versiones_nuevas, renglones_fijados=x.renglones_fijados)
                    for o, k, x in r.hechos],
            rechazados=[ClonRechazadoSalida(original=p.original, clon=p.clave, problemas=list(p.problemas)) for p in r.rechazados],
            versiones_nuevas=sum(x.versiones_nuevas for _, _, x in r.hechos), renglones_fijados=sum(x.renglones_fijados for _, _, x in r.hechos),
            informe=informe_de_resultado(r))
