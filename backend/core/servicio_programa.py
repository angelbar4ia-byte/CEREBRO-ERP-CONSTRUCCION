"""
Guardar lo que el planeador edita — `1-mundo/PROGRAMA-CPM.md` §4.7 y §8.

Un puerto (`RepositorioPrograma`) y un servicio (`ServicioPrograma`) sobre `programa.py`, con la misma
arquitectura que el motor de cálculo (D-182): el dominio no conoce ninguna base. Los adaptadores viven
aparte: `memoria_programa.py` para las pruebas y `infra/postgres_programa.py` para Postgres.

Lo que se guarda es **la bitácora de ediciones**, no las fechas. El programa base —las filas y los vínculos
con que se importó— no cambia; el programa vigente es `reprogramar(base, ediciones aplicadas)`, así que
nada puede quedar a medias y deshacer una edición es repetir la cuenta sin ella. Cada edición guarda quién
la hizo, con qué rol, qué dijo el sistema que pasaría (el impacto que vio quien decidió) y, si toca un
vínculo, por qué existe ese orden (`origen`).

El sistema propone y el humano decide: `proponer` no guarda nada; `aplicar` guarda lo que el sistema
mostró y nada más; si entre una cosa y otra alguien editó, el conflicto se dice en vez de pisar.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from dataclasses import replace
from typing import Any, Callable, Dict, FrozenSet, List, Mapping, Optional, Protocol, Sequence, Tuple, Union

from .accesos import PERMISOS_POR_OMISION, PermisoDenegado
from .motor_cpm import Calendario, Vinculo
from .programa import (
    CambiarDuracion,
    FijarInicio,
    Fila,
    Impacto,
    PERMISO_DE,
    Programa,
    Rechazado,
    Reprogramacion,
    armar_programa,
    comparar,
    describir_edicion,
    reprogramar,
)

# `MODELO.md` §5b: la estructura es de Control de obra y las fechas, del Residente. Esta es la tabla por omisión (la que
# siembra la migración 0004); el servicio lee la vigente de `ROL_FUNCION` cuando se la dan (`ServicioPrograma(permisos=)`)
ROLES_CON_PERMISO = PERMISOS_POR_OMISION


ETIQUETA_DE_PERMISO = {
    "editar_estructura_programa": "editar la estructura del programa",
    "editar_fechas_programa": "editar las fechas del programa",
}


class Conflicto(Exception):
    """Alguien editó el programa entre que se calculó el impacto y se quiso guardar."""


class NoSePuedeDeshacer(Exception):
    """Deshacer esa edición dejaría sin sentido a otras que se hicieron después."""

    def __init__(self, mensaje: str, dependientes: Sequence[int]) -> None:
        super().__init__(mensaje)
        self.dependientes = tuple(dependientes)


class ProgramaNoExiste(KeyError):
    pass


class YaReemplazado(Exception):
    """Ese programa ya tiene una versión más nueva: la nueva se sube sobre ella, para que la cadena sea una sola."""

    def __init__(self, mensaje: str, por: int) -> None:
        super().__init__(mensaje)
        self.por = por


# --------------------------------------------------------------------------- lo que el puerto guarda y entrega


@dataclass
class ProgramaGuardado:
    id: int
    nombre: str
    filas: List[Fila]
    vinculos: List[Tuple[Vinculo, Optional[str]]]  # (vínculo, origen): el origen es nulo si vino sin declarar
    rechazados: List[Rechazado]
    calendario: Calendario
    version: int = 0  # sube con cada edición o reversión: es lo que `esperaba` compara
    version_de: Optional[int] = None  # el programa del que esta es la versión nueva
    traspaso: Optional[Dict[str, Any]] = None  # qué pasó con sus ediciones al subirla: lo que pasó y lo que no, y por qué


@dataclass(frozen=True)
class EdicionGuardada:
    id: int
    secuencia: int  # el orden en que se aplicaron: 1, 2, 3…
    edicion: object  # una de las ediciones de `programa.py`
    rol: str
    usuario: str
    estado: str  # aplicada · revertida
    impacto: Mapping[str, object]  # lo que el sistema mostró al decidir (`Impacto.resumen`)
    creada_en: datetime
    revertida_por: Optional[str] = None
    revertida_en: Optional[datetime] = None
    heredada_de: Optional[int] = None  # la edición de la versión anterior de la que esta es el traspaso


@dataclass(frozen=True)
class Heredada:
    """Una edición de la versión anterior que pasa a la nueva: conserva quién la hizo, con qué rol y cuándo se decidió;
    lo único que se vuelve a calcular es el impacto, que ahora es contra el programa nuevo."""

    edicion: object
    rol: str
    usuario: str
    creada_en: datetime
    impacto: Mapping[str, object]
    heredada_de: int


@dataclass(frozen=True)
class NoPaso:
    anterior: EdicionGuardada  # la edición, tal como quedó en la versión anterior
    motivo: str
    texto: str  # «EST-02010 dura 12 d»


@dataclass
class VersionNueva:
    id: int
    pasaron: List[EdicionGuardada]  # ya en la versión nueva, en el mismo orden
    no_pasaron: List[NoPaso]


@dataclass(frozen=True)
class ResumenPrograma:
    """Lo que se ve de un programa en la lista, sin abrirlo."""

    id: int
    nombre: str
    version: int
    partidas: int  # los conceptos con fechas y días: lo que el CPM programa
    vinculos: int  # los que se cargaron
    rechazados: int  # los que el cargador no aceptó, con su motivo
    ediciones: int  # las aplicadas, sin contar las revertidas
    creado_en: datetime
    importado_por: Optional[str] = None  # quién lo subió; nulo si se cargó sin decirlo (las pruebas, `servir`)
    importado_con_rol: Optional[str] = None
    version_de: Optional[int] = None  # si es la versión nueva de otro programa, cuál
    reemplazado_por: Optional[int] = None  # si ya tiene versión nueva, cuál (lo pone `ServicioPrograma.listar`)


class RepositorioPrograma(Protocol):
    def importar_programa(
        self, nombre: str, programa: Programa, calendario: Calendario, *, usuario: Optional[str] = None, rol: Optional[str] = None
    ) -> int: ...

    def listar_programas(self) -> List[ResumenPrograma]:
        """Todos, del más viejo al más nuevo."""

    def importar_version(
        self, anterior_id: int, nombre: str, programa: Programa, calendario: Calendario, *, usuario: str, rol: str,
        heredadas: Sequence[Heredada], traspaso: Mapping[str, Any], esperaba: int,
    ) -> int:
        """Guarda el programa nuevo junto con las ediciones que pasan, todo o nada, y lo deja como la versión nueva de
        `anterior_id`. `esperaba` es la versión del anterior que vio quien sube: si ya es otra, `Conflicto`; si el
        anterior ya tiene versión nueva, `YaReemplazado`. La versión del programa nuevo queda en lo que heredó."""

    def leer_programa(self, programa_id: int) -> ProgramaGuardado: ...

    def ediciones(self, programa_id: int) -> List[EdicionGuardada]:
        """Todas, en orden de secuencia, también las revertidas: la bitácora no se borra."""

    def guardar_edicion(
        self, programa_id: int, edicion: object, *, rol: str, usuario: str, impacto: Mapping[str, object], esperaba: int
    ) -> EdicionGuardada:
        """Agrega la edición con la secuencia siguiente y sube la versión. `esperaba` es la versión que vio
        quien decidió; si el programa ya va en otra, `Conflicto` y no se guarda nada."""

    def revertir_edicion(self, programa_id: int, edicion_id: int, *, usuario: str, esperaba: int) -> None:
        """Marca la edición como revertida y sube la versión. Igual que `guardar_edicion`, con candado."""


# --------------------------------------------------------------------------- el servicio


@dataclass
class Vigente:
    guardado: ProgramaGuardado
    base: Programa  # tal como se importó
    reprogramacion: Reprogramacion  # base + ediciones aplicadas: el programa que se ve
    aplicadas: List[EdicionGuardada]
    version: int  # la que se leyó antes que las ediciones: si algo cambia entre las dos lecturas, el candado salta

    @property
    def programa(self) -> Programa:
        return self.reprogramacion.programa


@dataclass
class Propuesta:
    edicion: object
    rol: str
    permiso: str
    aplicable: bool  # False si la edición no se puede aplicar (ver `rechazadas`)
    rechazadas: List[Rechazado]
    impacto: Impacto  # contra el programa vigente de antes de la edición
    programa: Programa  # el programa vigente si se aplicara
    esperaba: int
    guardada: Optional[EdicionGuardada] = None


def permiso_de(edicion: object) -> str:
    try:
        return PERMISO_DE[type(edicion)]
    except KeyError:
        raise TypeError(f"edición desconocida: {edicion!r}") from None


Roles = Union[str, Sequence[str]]  # el rol con que se pide, o todos los que tiene quien pide


def rol_efectivo(funcion: str, roles: Roles, permisos: Optional[Mapping[str, FrozenSet[str]]] = None) -> str:
    """El rol con que queda hecha la acción: el primero —en orden alfabético— de los que tiene quien la pide y que tienen la
    función. Si ninguno la tiene, `PermisoDenegado`."""
    tabla = ROLES_CON_PERMISO if permisos is None else permisos
    mios = (roles,) if isinstance(roles, str) else tuple(roles)
    tienen = tabla.get(funcion, frozenset())
    for r in sorted(mios):
        if r in tienen:
            return r
    quehacer = ETIQUETA_DE_PERMISO.get(funcion, funcion)
    if not mios:
        raise PermisoDenegado(f"no tienes ningún rol: no puedes {quehacer}")
    if len(mios) == 1:
        raise PermisoDenegado(f"el rol «{mios[0]}» no puede {quehacer}")
    raise PermisoDenegado(f"ninguno de tus roles ({', '.join(sorted(mios))}) puede {quehacer}")


def verificar_funcion(funcion: str, rol: Roles, permisos: Optional[Mapping[str, FrozenSet[str]]] = None) -> str:
    rol_efectivo(funcion, rol, permisos)
    return funcion


def verificar_permiso(edicion: object, rol: Roles, permisos: Optional[Mapping[str, FrozenSet[str]]] = None) -> str:
    return verificar_funcion(permiso_de(edicion), rol, permisos)


# Subir un programa es lo más estructural que hay —las partidas, sus duraciones y todos sus vínculos—: pide la misma
# función que editar la estructura. No se inventa una función nueva sin un caso que la pida (`MODELO.md` §5b).
FUNCION_DE_IMPORTAR = "editar_estructura_programa"


class ServicioPrograma:
    def __init__(
        self, repositorio: RepositorioPrograma, permisos: Optional[Callable[[], Mapping[str, FrozenSet[str]]]] = None
    ) -> None:
        """`permisos` entrega `ROL_FUNCION` tal como está hoy (`RepositorioAccesos.permisos`); sin ella, la tabla por omisión.
        Se lee en cada acción: lo que `gestionar_rol_funcion` cambia vale desde la siguiente."""
        self.repo = repositorio
        self._permisos = permisos

    def tabla_de_permisos(self) -> Mapping[str, FrozenSet[str]]:
        return ROLES_CON_PERMISO if self._permisos is None else self._permisos()

    def rol_para(self, funcion: str, roles: Roles) -> str:
        return rol_efectivo(funcion, roles, self.tabla_de_permisos())

    def funciones_de(self, roles: Roles) -> List[str]:
        """Lo que puede hacer quien tiene esos roles."""
        mios = {roles} if isinstance(roles, str) else set(roles)
        return sorted(f for f, rs in self.tabla_de_permisos().items() if rs & mios)

    def listar(self) -> List[ResumenPrograma]:
        todos = self.repo.listar_programas()
        sucesor = {r.version_de: r.id for r in todos if r.version_de is not None}
        return [replace(r, reemplazado_por=sucesor.get(r.id)) for r in todos]

    def reemplazo_de(self, programa_id: int) -> Optional[int]:
        return next((r.reemplazado_por for r in self.listar() if r.id == programa_id), None)

    def verificar_importar(self, rol: Roles) -> str:
        """Quien no puede importar lo sabe antes de subir el archivo, no después de leerlo. Devuelve el rol con que lo haría."""
        return self.rol_para(FUNCION_DE_IMPORTAR, rol)

    def importar(self, nombre: str, programa: Programa, calendario: Calendario, rol: Roles, usuario: str) -> int:
        """Guarda un programa ya cargado, diciendo quién lo subió. Devuelve su id."""
        rol = self.verificar_importar(rol)
        if not usuario:
            raise ValueError("todo programa dice quién lo subió")
        if not nombre.strip():
            raise ValueError("todo programa lleva nombre")
        return self.repo.importar_programa(nombre.strip(), programa, calendario, usuario=usuario, rol=rol)

    def subir_version(
        self, programa_id: int, nombre: str, programa: Programa, calendario: Calendario, rol: Roles, usuario: str,
        esperaba: Optional[int] = None,
    ) -> VersionNueva:
        """Sube `programa` como la versión nueva de `programa_id`. Las ediciones que ya estaban aplicadas pasan a la
        nueva **si siguen teniendo sentido**, con su autor, su rol y su fecha; las que no, se dicen con su motivo
        y no se guardan. El que sube no necesita el permiso de lo que se hereda: se decidió con el de quien lo hizo.

        Dos razones para que una edición no pase: el motor la rechaza sobre la base nueva (la partida ya no está, el
        vínculo ya existe o ya no existe, cerraría un ciclo), o **la versión nueva ya cambió esa partida** —su
        duración o su arranque—: ahí gana el archivo nuevo, porque el planeador decidió algo y una edición vieja no se
        lo desdice en silencio. El sistema propone y el humano decide."""
        rol = self.verificar_importar(rol)
        if not usuario:
            raise ValueError("todo programa dice quién lo subió")
        if not nombre.strip():
            raise ValueError("todo programa lleva nombre")
        v = self.abrir(programa_id)
        if esperaba is not None and esperaba != v.version:
            raise Conflicto(f"el programa ya va en la versión {v.version}, no en la {esperaba}")
        sucesor = self.reemplazo_de(programa_id)
        if sucesor is not None:
            raise YaReemplazado(f"el programa {programa_id} ya tiene una versión más nueva, la {sucesor}", sucesor)

        anterior_cal = v.guardado.calendario

        def cambio_la_nueva(e: object) -> bool:
            llave = getattr(e, "llave", None)
            if llave is None or llave not in v.base.ventanas or llave not in programa.ventanas:
                return False  # lo que no está en alguna de las dos lo dice el motor
            vieja, nueva = v.base.ventanas[llave], programa.ventanas[llave]
            if isinstance(e, CambiarDuracion):
                return anterior_cal.n(vieja.fin) - anterior_cal.n(vieja.inicio) != calendario.n(nueva.fin) - calendario.n(nueva.inicio)
            return isinstance(e, FijarInicio) and vieja.inicio != nueva.inicio

        aceptadas: List[object] = []
        heredadas: List[Heredada] = []
        no_pasaron: List[NoPaso] = []
        antes = reprogramar(programa, calendario, []).programa
        for g in v.aplicadas:
            e = g.edicion
            motivo = "la_version_nueva_ya_la_cambio" if cambio_la_nueva(e) else None
            if motivo is None:
                prueba = reprogramar(programa, calendario, aceptadas + [e])
                if prueba.rechazadas:
                    motivo = prueba.rechazadas[0].motivo
            if motivo is not None:
                no_pasaron.append(NoPaso(g, motivo, describir_edicion(e, v.base.por_llave)))
                continue
            aceptadas.append(e)
            despues = prueba.programa
            heredadas.append(Heredada(e, g.rol, g.usuario, g.creada_en, comparar(antes, despues, calendario).resumen(), g.id))
            antes = despues
        traspaso = {
            "de": programa_id,
            "de_nombre": v.guardado.nombre,
            "pasaron": len(heredadas),
            "no_pasaron": [
                {"secuencia": n.anterior.secuencia, "texto": n.texto, "usuario": n.anterior.usuario, "rol": n.anterior.rol, "motivo": n.motivo}
                for n in no_pasaron
            ],
        }
        nuevo_id = self.repo.importar_version(
            programa_id, nombre.strip(), programa, calendario, usuario=usuario, rol=rol, heredadas=heredadas, traspaso=traspaso,
            esperaba=v.version,
        )
        return VersionNueva(nuevo_id, [e for e in self.repo.ediciones(nuevo_id)], no_pasaron)

    def abrir(self, programa_id: int) -> Vigente:
        """El programa tal como está hoy: la base más lo aplicado."""
        g = self.repo.leer_programa(programa_id)  # primero la versión y después las ediciones: nunca al revés
        base = armar_programa(
            g.filas,
            [v for v, _ in g.vinculos],
            g.rechazados,
            g.calendario,
            {v: o for v, o in g.vinculos if o},
        )
        todas = self.repo.ediciones(programa_id)
        aplicadas = [e for e in todas if e.estado == "aplicada"]
        rep = reprogramar(base, g.calendario, [e.edicion for e in aplicadas])
        return Vigente(g, base, rep, aplicadas, g.version)

    def proponer(self, programa_id: int, edicion: object, rol: Roles) -> Propuesta:
        """Qué pasaría si se aplicara. No guarda nada."""
        permiso = permiso_de(edicion)
        rol = self.rol_para(permiso, rol)
        v = self.abrir(programa_id)
        cal = v.guardado.calendario
        nuevo = reprogramar(v.base, cal, [e.edicion for e in v.aplicadas] + [edicion])
        # lo que ya estaba rechazado al repetir la bitácora no cuenta: solo lo que trae esta edición
        propias = nuevo.rechazadas[len(v.reprogramacion.rechazadas):]
        return Propuesta(
            edicion=edicion,
            rol=rol,
            permiso=permiso,
            aplicable=not propias,
            rechazadas=propias,
            impacto=comparar(v.programa, nuevo.programa, cal),
            programa=nuevo.programa,
            esperaba=v.version,
        )

    def aplicar(self, programa_id: int, edicion: object, rol: Roles, usuario: str, esperaba: Optional[int] = None) -> Propuesta:
        """Propone y, si se puede, guarda con lo que el sistema mostró. Una edición que no se puede aplicar
        se devuelve sin guardar y con su motivo. `esperaba` es la versión que vio quien decidió —una pantalla
        abierta desde hace rato—: si el programa ya va en otra, `Conflicto`, porque el impacto que vio ya no
        es el de hoy. Sin `esperaba` se aplica sobre lo que haya al momento de proponer."""
        if not usuario:
            raise ValueError("toda edición dice quién la hizo")
        p = self.proponer(programa_id, edicion, rol)
        if esperaba is not None and esperaba != p.esperaba:
            raise Conflicto(f"el programa ya va en la versión {p.esperaba}, no en la {esperaba}")
        if not p.aplicable:
            return p
        p.guardada = self.repo.guardar_edicion(
            programa_id, edicion, rol=p.rol, usuario=usuario, impacto=p.impacto.resumen(), esperaba=p.esperaba
        )
        return p

    def deshacer(self, programa_id: int, edicion_id: int, rol: Roles, usuario: str) -> Vigente:
        """Revierte una edición, con el permiso que la hizo, si las que vinieron después siguen teniendo
        sentido sin ella. Si no, dice cuáles dependen de ella y no toca nada."""
        if not usuario:
            raise ValueError("todo deshacer dice quién lo hizo")
        v = self.abrir(programa_id)
        objetivo = next((e for e in v.aplicadas if e.id == edicion_id), None)
        if objetivo is None:
            raise KeyError(f"la edición {edicion_id} no está aplicada")
        self.rol_para(permiso_de(objetivo.edicion), rol)
        cal = v.guardado.calendario
        resto = [e for e in v.aplicadas if e.id != edicion_id]
        acumuladas: List[object] = []
        dependientes = []
        for e in resto:
            if reprogramar(v.base, cal, acumuladas + [e.edicion]).rechazadas:
                dependientes.append(e.secuencia)  # ya no aplica: se queda fuera de la cuenta
            else:
                acumuladas.append(e.edicion)
        if dependientes:
            raise NoSePuedeDeshacer(
                f"las ediciones {', '.join(map(str, dependientes))} dependen de la {objetivo.secuencia}", dependientes
            )
        self.repo.revertir_edicion(programa_id, edicion_id, usuario=usuario, esperaba=v.version)
        return self.abrir(programa_id)
