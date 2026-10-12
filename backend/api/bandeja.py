"""
La API de la bandeja de propuestas y de alertas — D-485.

«El sistema propone y el humano decide» tiene aquí su lugar único: lo que una persona o el agente sugiere (una **propuesta**) y lo que el
sistema detecta que no cuadra (una **alerta**) se ven, se resuelven y se consultan por las mismas rutas.

| Se hace                                  | Ruta                                        | Quién puede                                              |
|------------------------------------------|---------------------------------------------|----------------------------------------------------------|
| Ver qué hay pendiente                    | `GET /bandeja`                              | cualquiera identificado                                  |
| Listar / ver propuestas                  | `GET /bandeja/propuestas` · `…/{id}`        | cualquiera identificado                                  |
| Dejar una propuesta                      | `POST /bandeja/propuestas`                  | cualquiera con un rol (proponer no cambia nada)          |
| Aprobar o rechazar una propuesta         | `POST /bandeja/propuestas/{id}/resolucion`  | `aprobar_propuesta`; aprobar pide además la función de la acción |
| Listar / ver alertas                     | `GET /bandeja/alertas` · `…/{id}`           | cualquiera identificado                                  |
| Resolver o descartar una alerta          | `POST /bandeja/alertas/{id}/resolucion`     | `resolver_alerta`                                        |

**Aprobar es hacer, con la identidad de quien aprueba.** Aprobar una clonación la ejecuta el sistema como si quien aprueba la hubiera
pedido en `POST /clonaciones`: pide `clonar_insumo` además de `aprobar_propuesta`, deja la carga a nombre de quien aprueba, y se ata a lo
que vio quien propuso (`base` de la propuesta → `esperaba` de la clonación; también se puede mandar `esperaba` al resolver). Quien
propone no aprueba lo suyo. Si la operación no procede, la propuesta sigue pendiente y se responde con el motivo.

**Solo se aprueba lo que el sistema sabe hacer.** Hoy, `clonacion`. Los demás tipos se pueden proponer y rechazar; aprobarlos responde
`422 sin_operacion`, porque decir «aprobada» sobre algo que nada ejecutó sería decir que se hizo lo que no se hizo.

**Lo rechazado se conserva**: no se borra, lleva la nota de quien lo rechazó, y la misma propuesta no vuelve a entrar mientras no traiga
evidencia que no existía.

Las alertas **no se crean por la API**: las deja el sistema cuando un detector las encuentra (`ServicioBandeja.alertar`), y si reaparecen
sin haberse resuelto se cuentan (`veces_vista`) en vez de repetirse. Aquí solo se ven y se resuelven. Tampoco se deja por la API una
propuesta «del agente»: el agente interno todavía no tiene una credencial propia (`WORKFLOWS.md` §7), y quien llama aquí es siempre una
persona (`origen = usuario`).

**Cómo contesta cuando algo no procede** (el código va en `detail.codigo`):

- `403 permiso_denegado · autoaprobacion` — falta la función, o quien aprueba es quien propuso.
- `404 propuesta_inexistente · alerta_inexistente`.
- `409` — ya está hecho o cambió: `ya_propuesta` y `rechazada_antes` (con `propuesta_id` de la que ya existe), `ya_resuelta` (con `estado`),
  `conflicto` (otra carga, contratación o clonación pasó entre que se propuso y se aprobó: se vuelve a proponer).
- `422` — lo pedido no procede y quien lo pidió puede corregirlo: `propuesta_invalida` (sin evidencia, sin valor, un tipo que no existe, un
  rechazo sin nota…), `sin_operacion` (con el `tipo`), `clonacion_no_procede` (con `problemas`), `peticion_invalida`.
"""
from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import Depends, FastAPI
from pydantic import BaseModel, Field

from api.autenticacion import Autenticacion, Identidad
from api.errores import _error
from core.catalogo import CatalogoCambio, RepositorioCatalogo
from core.clonacion import ClonacionNoProcede, ServicioClonacion
from core.propuestas import (
    Alerta,
    AlertaNoExiste,
    AutoAprobacion,
    Propuesta,
    PropuestaInvalida,
    PropuestaNoExiste,
    RechazadaAntes,
    RepositorioBandeja,
    ServicioBandeja,
    SinOperacion,
    YaPropuesta,
    YaResuelta,
    tipos_de_propuesta,
)
from core.servicio_programa import PermisoDenegado, ServicioPrograma


# --------------------------------------------------------------------------- lo que entra


class PropuestaEntrada(BaseModel):
    tipo: str = Field(description="Qué se propone: equivalencia · version · reparto · conversion · matriz_generada · fusion · clonacion · "
                      "orden_cambio · patron_carga · precio_nuevo")
    objeto: str = Field(min_length=1, description="Sobre qué recae: la clave del insumo, la ruta del bloque, el prefijo…")
    valor_propuesto: Dict[str, Any] = Field(
        description='Lo que se propone; su forma cambia según el tipo. Una clonación: {"original": "AUX-00001", "clave": "PRE-00120"} (y '
        '`modo`, «sustituir» si no se dice); la corrección de un prefijo: {"viejo": "AUX", "nuevo": "PRE"} (y `desde`, 1 si no se dice).')
    evidencia: str = Field(min_length=1, description="De dónde sale. Sin evidencia no hay propuesta, hay una orden disfrazada")
    base: Optional[int] = Field(None, description="La última carga que vio quien propone (`base` de la propuesta que pidió antes): viaja a la "
                                "aplicación, y si el catálogo ya va en otra, aprobarla responde 409")


class ResolucionDePropuestaEntrada(BaseModel):
    decision: str = Field(description="aprobar · rechazar")
    nota: Optional[str] = Field(None, description="Por qué. Obligatoria al rechazar: el rechazo se conserva y es lo que evita que se insista")
    esperaba: Optional[int] = Field(None, description="La última carga que vio quien aprueba. Sin ella se usa la `base` de la propuesta")


class ResolucionDeAlertaEntrada(BaseModel):
    estado: str = Field(description="resuelta (era real y se atendió) · descartada (no era nada)")
    nota: str = Field(min_length=1, description="Qué era: lo que alguien decidió al mirarla")


# --------------------------------------------------------------------------- lo que sale


class PropuestaSalida(BaseModel):
    id: int
    tipo: str
    objeto: str
    valor_propuesto: Dict[str, Any]
    evidencia: str
    origen: str = Field(description="usuario · agente")
    propuesto_por: str
    propuesto_con_rol: str
    creada_en: datetime
    estado: str = Field(description="pendiente · aprobada · rechazada")
    modelo: Optional[str] = Field(None, description="Solo si la dejó el agente: qué modelo la produjo")
    version_modelo: Optional[str] = None
    confianza: Optional[str] = Field(None, description="alta · media · baja; solo la trae el agente")
    supuestos: Optional[Dict[str, Any]] = None
    base: Optional[int] = Field(None, description="La última carga que vio quien propuso")
    resuelto_por: Optional[str] = None
    resuelto_con_rol: Optional[str] = None
    resuelta_en: Optional[datetime] = None
    nota: Optional[str] = None
    resultado: Optional[Dict[str, Any]] = Field(None, description="Lo que hizo el sistema al aprobarla (para una clonación: carga, versiones y renglones)")
    se_puede_aprobar: bool = Field(description="El sistema sabe ejecutar este tipo de propuesta. Si es falso, solo se puede rechazar")


class AlertaSalida(BaseModel):
    id: int
    tipo: str
    objeto: str = Field(description="A qué aplica; vacío si no hay un objeto al que apuntar")
    evidencia: Dict[str, Any] = Field(description="Qué se comparó, con qué método y qué dio — la de la última vez que se vio")
    parametro_usado: Optional[Dict[str, Any]] = Field(None, description="El umbral que la disparó")
    primera_vez: datetime
    ultima_vez: datetime
    veces_vista: int = Field(description="Cuántas veces volvió a aparecer sin haberse resuelto")
    estado: str = Field(description="activa · resuelta · descartada")
    resuelto_por: Optional[str] = None
    resuelto_con_rol: Optional[str] = None
    resuelta_en: Optional[datetime] = None
    nota_resolucion: Optional[str] = None


class ResumenDeBandejaSalida(BaseModel):
    propuestas_pendientes: int
    pendientes_por_tipo: Dict[str, int]
    alertas_activas: int
    alertas_por_tipo: Dict[str, int]
    alerta_mas_vista: Optional[AlertaSalida] = Field(None, description="La activa que más veces volvió a aparecer")


def _propuesta(p: Propuesta, aprobables: frozenset) -> PropuestaSalida:
    return PropuestaSalida(
        **{k: getattr(p, k) for k in (
            "id", "tipo", "objeto", "valor_propuesto", "evidencia", "origen", "propuesto_por", "propuesto_con_rol", "creada_en", "estado",
            "modelo", "version_modelo", "confianza", "supuestos", "base", "resuelto_por", "resuelto_con_rol", "resuelta_en", "nota", "resultado")},
        se_puede_aprobar=p.tipo in aprobables)


def _alerta(a: Alerta) -> AlertaSalida:
    return AlertaSalida(**a.__dict__)


# --------------------------------------------------------------------------- las rutas


def registrar_bandeja(app: FastAPI, servicio: ServicioPrograma, bandeja: RepositorioBandeja, catalogo: Optional[RepositorioCatalogo],
                      auth: Autenticacion) -> None:
    """Agrega a `app` las rutas de la bandeja. Los permisos se leen de la misma tabla que usa el servicio del programa. Sin `catalogo`, la
    bandeja recibe y guarda propuestas pero no sabe ejecutar ninguna: todas se pueden rechazar y ninguna aprobar."""
    identidad, lectura = auth.identidad, auth.lectura
    permisos = servicio.tabla_de_permisos
    tipos = tipos_de_propuesta(None if catalogo is None else ServicioClonacion(catalogo, permisos=permisos))
    sv = ServicioBandeja(bandeja, permisos, tipos)
    aprobables = frozenset(t for t, x in tipos.items() if x.ejecutable)

    def ver(p: Propuesta) -> PropuestaSalida:
        return _propuesta(p, aprobables)

    def invalida(e: PropuestaInvalida) -> Any:
        return _error(422, "propuesta_invalida", str(e))

    @app.get("/bandeja", response_model=ResumenDeBandejaSalida, operation_id="ver_bandeja", dependencies=[Depends(lectura)],
             summary="Lo que hay pendiente de decidir: propuestas por tipo y alertas activas")
    def ver_bandeja() -> ResumenDeBandejaSalida:
        r = sv.resumen()
        return ResumenDeBandejaSalida(
            propuestas_pendientes=r.propuestas_pendientes, pendientes_por_tipo=dict(r.pendientes_por_tipo), alertas_activas=r.alertas_activas,
            alertas_por_tipo=dict(r.alertas_por_tipo), alerta_mas_vista=None if r.alerta_mas_vista is None else _alerta(r.alerta_mas_vista))

    # ---- propuestas
    @app.get("/bandeja/propuestas", response_model=List[PropuestaSalida], operation_id="listar_propuestas", dependencies=[Depends(lectura)],
             summary="Las propuestas, de la más vieja a la más nueva; se filtran por estado y por tipo")
    def listar_propuestas(estado: Optional[str] = None, tipo: Optional[str] = None) -> List[PropuestaSalida]:
        try:
            return [ver(p) for p in sv.propuestas(estado, tipo)]
        except PropuestaInvalida as e:
            raise invalida(e) from None

    @app.get("/bandeja/propuestas/{propuesta_id}", response_model=PropuestaSalida, operation_id="ver_propuesta", dependencies=[Depends(lectura)],
             summary="Una propuesta, con su evidencia, quién la dejó y, si ya se resolvió, quién y por qué")
    def ver_propuesta(propuesta_id: int) -> PropuestaSalida:
        try:
            return ver(sv.propuesta(propuesta_id))
        except PropuestaNoExiste:
            raise _error(404, "propuesta_inexistente", f"No hay una propuesta {propuesta_id}.") from None

    @app.post("/bandeja/propuestas", response_model=PropuestaSalida, status_code=201, operation_id="dejar_propuesta",
              summary="Dejar una propuesta con su evidencia: queda pendiente hasta que otra persona la apruebe o la rechace")
    def dejar_propuesta(entrada: PropuestaEntrada, quien: Identidad = Depends(identidad)) -> PropuestaSalida:
        try:
            return ver(sv.proponer(entrada.tipo, entrada.objeto, entrada.valor_propuesto, entrada.evidencia, usuario=quien.usuario,
                                   rol=quien.roles, base=entrada.base))
        except PermisoDenegado as e:
            raise _error(403, "permiso_denegado", str(e)) from None
        except PropuestaInvalida as e:
            raise invalida(e) from None
        except (YaPropuesta, RechazadaAntes) as e:
            raise _error(409, "ya_propuesta" if isinstance(e, YaPropuesta) else "rechazada_antes", str(e), propuesta_id=e.propuesta_id) from None

    @app.post("/bandeja/propuestas/{propuesta_id}/resolucion", response_model=PropuestaSalida, operation_id="resolver_propuesta",
              summary="Aprobar (el sistema hace lo propuesto, a nombre de quien aprueba) o rechazar (y decir por qué)")
    def resolver_propuesta(propuesta_id: int, entrada: ResolucionDePropuestaEntrada, quien: Identidad = Depends(identidad)) -> PropuestaSalida:
        try:
            return ver(sv.resolver(propuesta_id, entrada.decision, rol=quien.roles, usuario=quien.usuario, nota=entrada.nota,
                                   esperaba=entrada.esperaba))
        except PermisoDenegado as e:
            raise _error(403, "permiso_denegado", str(e)) from None
        except AutoAprobacion as e:
            raise _error(403, "autoaprobacion", str(e)) from None
        except PropuestaNoExiste:
            raise _error(404, "propuesta_inexistente", f"No hay una propuesta {propuesta_id}.") from None
        except YaResuelta as e:
            raise _error(409, "ya_resuelta", str(e), estado=e.estado) from None
        except CatalogoCambio as e:
            raise _error(409, "conflicto", f"Alguien cargó algo en el catálogo desde que se propuso. Vuelve a proponerlo. ({e})") from None
        except SinOperacion as e:
            raise _error(422, "sin_operacion", str(e), tipo=e.tipo) from None
        except ClonacionNoProcede as e:
            raise _error(422, "clonacion_no_procede", str(e), problemas=list(e.problemas)) from None
        except PropuestaInvalida as e:
            raise invalida(e) from None
        except ValueError as e:
            raise _error(422, "peticion_invalida", str(e)) from None

    # ---- alertas
    @app.get("/bandeja/alertas", response_model=List[AlertaSalida], operation_id="listar_alertas", dependencies=[Depends(lectura)],
             summary="Las alertas, de la más vieja a la más nueva; se filtran por estado y por tipo")
    def listar_alertas(estado: Optional[str] = None, tipo: Optional[str] = None) -> List[AlertaSalida]:
        try:
            return [_alerta(a) for a in sv.alertas(estado, tipo)]
        except PropuestaInvalida as e:
            raise invalida(e) from None

    @app.get("/bandeja/alertas/{alerta_id}", response_model=AlertaSalida, operation_id="ver_alerta", dependencies=[Depends(lectura)],
             summary="Una alerta: qué se comparó, con qué umbral, cuántas veces volvió a aparecer y, si ya se cerró, quién y qué era")
    def ver_alerta(alerta_id: int) -> AlertaSalida:
        try:
            return _alerta(sv.alerta(alerta_id))
        except AlertaNoExiste:
            raise _error(404, "alerta_inexistente", f"No hay una alerta {alerta_id}.") from None

    @app.post("/bandeja/alertas/{alerta_id}/resolucion", response_model=AlertaSalida, operation_id="resolver_alerta",
              summary="Resolver una alerta (era real y se atendió) o descartarla (no era nada), diciendo qué era")
    def resolver_alerta(alerta_id: int, entrada: ResolucionDeAlertaEntrada, quien: Identidad = Depends(identidad)) -> AlertaSalida:
        try:
            return _alerta(sv.resolver_alerta(alerta_id, entrada.estado, rol=quien.roles, usuario=quien.usuario, nota=entrada.nota))
        except PermisoDenegado as e:
            raise _error(403, "permiso_denegado", str(e)) from None
        except AlertaNoExiste:
            raise _error(404, "alerta_inexistente", f"No hay una alerta {alerta_id}.") from None
        except YaResuelta as e:
            raise _error(409, "ya_resuelta", str(e), estado=e.estado) from None
        except PropuestaInvalida as e:
            raise invalida(e) from None
