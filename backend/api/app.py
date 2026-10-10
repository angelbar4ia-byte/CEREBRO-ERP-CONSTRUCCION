"""
La API del programa — la única superficie pública (D-54), escrita sobre `ServicioPrograma`.

Todo pasa por el servicio: listar los programas y subir uno, ver un programa con lo que ya se aplicó, preguntar
qué pasaría con una edición (`propuestas`, no guarda nada), aplicarla (`ediciones`) o deshacerla.
El cliente de la pantalla se genera de este mismo spec y no se edita a mano (`generar_cliente.py`, D-55).

**Quién llama.** El cerebro todavía no decide cómo se autentica nadie. Mientras tanto, quien llama dice quién es
con dos cabeceras, `X-Rol` y `X-Usuario`: sirve para trabajar y probar y **no se despliega así** —cualquiera
podría decir que es Control de obra—. `crear_app(identidad=...)` acepta otra dependencia de FastAPI, y es el
único lugar que cambia cuando haya autenticación.
"""
from __future__ import annotations

from datetime import date, datetime
from typing import Any, Callable, Dict, List, Optional

from fastapi import Depends, FastAPI, Header, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel, Field

from core.gantt_pagina import pagina_gantt, pagina_programas
from core.motor_cpm import Calendario
from core.programa import (
    ImportacionInvalida,
    cargar_programa,
    edicion_a_dict,
    edicion_desde_dict,
    filas_desde_texto,
    vista_gantt,
)
from core.servicio_programa import (
    Conflicto,
    EdicionGuardada,
    NoSePuedeDeshacer,
    PermisoDenegado,
    ProgramaNoExiste,
    Propuesta,
    ResumenPrograma,
    ServicioPrograma,
    Vigente,
)


# --------------------------------------------------------------------------- lo que entra y lo que sale


class Identidad(BaseModel):
    rol: str
    usuario: str


class EdicionEntrada(BaseModel):
    edicion: Dict[str, Any] = Field(
        description='La edición como la guarda la bitácora, p. ej. {"edicion": "cambiar_duracion", "llave": "5669540", "dias": "12"}. '
        "Los días y las esperas van como texto —«12», «1/2»—: no cruzan como número."
    )
    esperaba: Optional[int] = Field(
        None,
        description="La versión del programa que vio quien decide. Si el programa ya va en otra, no se guarda y se responde 409: "
        "el impacto que vio ya no es el de hoy. Sin ella se aplica sobre lo que haya.",
    )


class ResumenSalida(BaseModel):
    id: int
    nombre: str
    version: int
    partidas: int = Field(description="Los conceptos con fechas y días: lo que el CPM programa")
    vinculos: int = Field(description="Los vínculos que se cargaron")
    rechazados: int = Field(description="Los que el cargador no aceptó, cada uno con su motivo")
    ediciones: int = Field(description="Las aplicadas, sin contar las revertidas")
    creado_en: datetime
    importado_por: Optional[str] = Field(None, description="Quién lo subió; nulo si se cargó sin decirlo")
    importado_con_rol: Optional[str] = None


class ImportacionEntrada(BaseModel):
    nombre: str = Field(min_length=1, max_length=120, description="Cómo se llama el programa en la lista")
    csv: str = Field(description="El programa en el formato de `1-mundo/programas/PROGRAMAS-PROTOTIPOS.csv` (`PROGRAMA-CPM.md` §2)")
    prototipo: Optional[str] = Field(None, description="Cuál programa del archivo, si trae varios (columna `prototipo`)")
    no_habiles: List[date] = Field(default_factory=list, description="Los días entre semana en que la obra no trabaja: 25-dic, 1-ene… Sin ellos, todos los días de semana cuentan")


class RechazoDeCarga(BaseModel):
    fila: int
    clave: str
    descripcion: str
    token: str = Field(description="El vínculo tal como venía escrito")
    motivo: str = Field(description="formato · autovinculo · predecesora_desconocida · predecesora_sin_partidas · sucesora_bloque · cierra_un_ciclo")


class ImportacionSalida(BaseModel):
    resumen: ResumenSalida
    rechazados: List[RechazoDeCarga] = Field(description="Los vínculos que no se cargaron, para que los vea el planeador")
    incumplidos: int = Field(description="Vínculos cargados que las fechas escritas del propio programa no cumplen: no son error, son aviso")


class RechazoSalida(BaseModel):
    motivo: str
    token: str


class MovidaSalida(BaseModel):
    llave: str
    dias_inicio: int
    dias_fin: int


class ImpactoSalida(BaseModel):
    partidas_movidas: int
    fin_antes: date
    fin_despues: date
    dias_de_cambio: int
    ruta_cambia: bool
    pasos_antes: int
    pasos_despues: int
    movidas: List[MovidaSalida]


class EdicionSalida(BaseModel):
    id: int
    secuencia: int
    edicion: Dict[str, Any]
    rol: str
    usuario: str
    estado: str
    impacto: Dict[str, Any]
    creada_en: datetime
    revertida_por: Optional[str] = None
    revertida_en: Optional[datetime] = None


class PropuestaSalida(BaseModel):
    aplicable: bool
    permiso: str
    rechazadas: List[RechazoSalida]
    impacto: ImpactoSalida
    esperaba: int
    version: int = Field(description="La versión del programa después de esto: la misma si no se guardó, la siguiente si se guardó")
    guardada: Optional[EdicionSalida] = None


class ProgramaSalida(BaseModel):
    id: int
    nombre: str
    version: int
    calendario: Dict[str, Any]
    vista: Dict[str, Any] = Field(description="El programa base dibujable, con lo necesario para reprogramar en pantalla")
    guardadas: List[EdicionSalida] = Field(description="Toda la bitácora, también lo revertido, en orden")


class VigenteSalida(BaseModel):
    version: int
    guardadas: List[EdicionSalida]
    fin: date


def _resumen_salida(r: ResumenPrograma) -> ResumenSalida:
    return ResumenSalida(**r.__dict__)


def _edicion_salida(e: EdicionGuardada) -> EdicionSalida:
    return EdicionSalida(
        id=e.id, secuencia=e.secuencia, edicion=edicion_a_dict(e.edicion), rol=e.rol, usuario=e.usuario, estado=e.estado,
        impacto=dict(e.impacto), creada_en=e.creada_en, revertida_por=e.revertida_por, revertida_en=e.revertida_en,
    )


def _propuesta_salida(p: Propuesta) -> PropuestaSalida:
    i = p.impacto
    return PropuestaSalida(
        aplicable=p.aplicable,
        permiso=p.permiso,
        rechazadas=[RechazoSalida(motivo=r.motivo, token=r.token) for r in p.rechazadas],
        impacto=ImpactoSalida(**i.resumen(), movidas=[MovidaSalida(llave=m.llave, dias_inicio=m.dias_inicio, dias_fin=m.dias_fin) for m in i.movidas]),
        esperaba=p.esperaba,
        version=p.esperaba + (1 if p.guardada else 0),
        guardada=_edicion_salida(p.guardada) if p.guardada else None,
    )


def _error(status: int, codigo: str, mensaje: str, **extra: Any) -> HTTPException:
    return HTTPException(status_code=status, detail={"codigo": codigo, "mensaje": mensaje, **extra})


def identidad_por_cabeceras(x_rol: Optional[str] = Header(None), x_usuario: Optional[str] = Header(None)) -> Identidad:
    """Quien llama dice quién es (ver el docstring del módulo: no se despliega así)."""
    if not x_rol or not x_usuario:
        raise _error(401, "sin_identidad", "Falta decir quién eres: las cabeceras X-Rol y X-Usuario.")
    return Identidad(rol=x_rol, usuario=x_usuario)


# --------------------------------------------------------------------------- la aplicación


def crear_app(servicio: ServicioPrograma, identidad: Callable[..., Identidad] = identidad_por_cabeceras) -> FastAPI:
    app = FastAPI(title="Programa", version="1", description="El programa de obra: verlo, proponer una edición, aplicarla y deshacerla.")

    def edicion_de(entrada: EdicionEntrada):
        try:
            return edicion_desde_dict(entrada.edicion)
        except (ValueError, TypeError, KeyError, ArithmeticError) as e:
            raise _error(422, "edicion_invalida", f"No entiendo esa edición: {e}") from None

    def guardado(programa_id: int):
        try:
            return servicio.abrir(programa_id)
        except ProgramaNoExiste:
            raise _error(404, "programa_inexistente", f"No hay un programa {programa_id}.") from None

    def vista_de(v: Vigente) -> Dict[str, Any]:
        base = v.base
        return vista_gantt(base, v.guardado.calendario, resultado=base.calcular(v.guardado.calendario), para_editar=True)

    @app.get("/programas", response_model=List[ResumenSalida], operation_id="listar_programas", summary="Los programas que hay, del más viejo al más nuevo")
    def listar_programas() -> List[ResumenSalida]:
        return [_resumen_salida(r) for r in servicio.listar()]

    @app.post("/programas", response_model=ImportacionSalida, status_code=201, operation_id="importar_programa",
              summary="Subir un programa: se carga, se guardan sus vínculos y se dice cuáles no entraron")
    def importar_programa(entrada: ImportacionEntrada, quien: Identidad = Depends(identidad)) -> ImportacionSalida:
        try:
            servicio.verificar_importar(quien.rol)  # antes de leer el archivo: quien no puede, no espera
        except PermisoDenegado as e:
            raise _error(403, "permiso_denegado", str(e)) from None
        cal = Calendario(no_habiles=frozenset(entrada.no_habiles))
        try:
            programa = cargar_programa(filas_desde_texto(entrada.csv, entrada.prototipo), cal)
        except (ImportacionInvalida, ValueError) as e:
            raise _error(422, "importacion_invalida", str(e)) from None
        try:
            pid = servicio.importar(entrada.nombre, programa, cal, quien.rol, quien.usuario)
        except ValueError as e:  # el nombre en blanco o quien sube sin nombre
            raise _error(422, "importacion_invalida", str(e)) from None
        (resumen,) = [r for r in servicio.listar() if r.id == pid]
        return ImportacionSalida(
            resumen=_resumen_salida(resumen),
            rechazados=[
                RechazoDeCarga(fila=r.fila, clave=programa.por_llave[r.sucesora].clave, descripcion=programa.por_llave[r.sucesora].descripcion,
                               token=r.token, motivo=r.motivo)
                for r in programa.rechazados
            ],
            incumplidos=len(programa.incumplidos(cal)),
        )

    @app.get("/programas/{programa_id}", response_model=ProgramaSalida, operation_id="ver_programa", summary="El programa base y su bitácora")
    def ver_programa(programa_id: int) -> ProgramaSalida:
        v = guardado(programa_id)
        return ProgramaSalida(
            id=programa_id, nombre=v.guardado.nombre, version=v.version, calendario=v.guardado.calendario.a_dict(), vista=vista_de(v),
            guardadas=[_edicion_salida(e) for e in servicio.repo.ediciones(programa_id)],
        )

    @app.get("/programas/{programa_id}/ediciones", response_model=List[EdicionSalida], operation_id="ver_bitacora", summary="Todo lo que se ha editado, también lo revertido")
    def ver_bitacora(programa_id: int) -> List[EdicionSalida]:
        guardado(programa_id)
        return [_edicion_salida(e) for e in servicio.repo.ediciones(programa_id)]

    @app.post("/programas/{programa_id}/propuestas", response_model=PropuestaSalida, operation_id="proponer_edicion",
              summary="Qué pasaría si se aplicara esta edición: no guarda nada")
    def proponer_edicion(programa_id: int, entrada: EdicionEntrada, quien: Identidad = Depends(identidad)) -> PropuestaSalida:
        guardado(programa_id)
        try:
            return _propuesta_salida(servicio.proponer(programa_id, edicion_de(entrada), quien.rol))
        except PermisoDenegado as e:
            raise _error(403, "permiso_denegado", str(e)) from None

    @app.post("/programas/{programa_id}/ediciones", response_model=PropuestaSalida, status_code=201, operation_id="aplicar_edicion",
              summary="Aplicar una edición y guardarla en la bitácora")
    def aplicar_edicion(programa_id: int, entrada: EdicionEntrada, quien: Identidad = Depends(identidad)) -> PropuestaSalida:
        guardado(programa_id)
        try:
            p = servicio.aplicar(programa_id, edicion_de(entrada), quien.rol, quien.usuario, entrada.esperaba)
        except PermisoDenegado as e:
            raise _error(403, "permiso_denegado", str(e)) from None
        except Conflicto as e:
            raise _error(409, "conflicto", f"Alguien editó el programa mientras decidías. Vuelve a verlo. ({e})") from None
        if not p.aplicable:
            raise _error(422, "no_aplicable", "Esa edición no se puede aplicar.", rechazadas=[r.motivo for r in p.rechazadas])
        return _propuesta_salida(p)

    @app.delete("/programas/{programa_id}/ediciones/{edicion_id}", response_model=VigenteSalida, operation_id="deshacer_edicion",
                summary="Deshacer una edición aplicada")
    def deshacer_edicion(programa_id: int, edicion_id: int, quien: Identidad = Depends(identidad)) -> VigenteSalida:
        guardado(programa_id)
        try:
            v = servicio.deshacer(programa_id, edicion_id, quien.rol, quien.usuario)
        except PermisoDenegado as e:
            raise _error(403, "permiso_denegado", str(e)) from None
        except NoSePuedeDeshacer as e:
            raise _error(409, "dependen", str(e), dependientes=list(e.dependientes)) from None
        except Conflicto as e:
            raise _error(409, "conflicto", f"Alguien editó el programa mientras decidías. Vuelve a verlo. ({e})") from None
        except KeyError as e:
            raise _error(404, "edicion_inexistente", f"Esa edición no está aplicada: {e}") from None
        return VigenteSalida(version=v.version, guardadas=[_edicion_salida(e) for e in servicio.repo.ediciones(programa_id)],
                             fin=v.reprogramacion.fin_despues)

    @app.get("/", response_class=HTMLResponse, operation_id="pantalla_programas", summary="La pantalla de los programas: la lista y subir uno")
    def pantalla_programas() -> HTMLResponse:
        return HTMLResponse(pagina_programas())

    @app.get("/programas/{programa_id}/gantt", response_class=HTMLResponse, operation_id="pantalla_gantt", summary="La pantalla del Gantt de este programa")
    def pantalla_gantt(programa_id: int) -> HTMLResponse:
        v = guardado(programa_id)
        guardadas = [_edicion_salida(e).model_dump(mode="json") for e in servicio.repo.ediciones(programa_id)]
        return HTMLResponse(pagina_gantt(
            v.base, v.guardado.calendario, f"Gantt {v.guardado.nombre}",
            api={"programa": programa_id, "version": v.version, "guardadas": guardadas},
        ))

    return app
