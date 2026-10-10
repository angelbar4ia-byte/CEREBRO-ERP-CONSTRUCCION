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
from typing import List, Mapping, Optional, Protocol, Sequence, Tuple

from .motor_cpm import Calendario, Vinculo
from .programa import (
    Fila,
    Impacto,
    PERMISO_DE,
    Programa,
    Rechazado,
    Reprogramacion,
    armar_programa,
    comparar,
    reprogramar,
)

# `MODELO.md` §5b: la estructura es de Control de obra y las fechas, del Residente
ROLES_CON_PERMISO = {
    "editar_estructura_programa": frozenset({"control_de_obra"}),
    "editar_fechas_programa": frozenset({"residente"}),
}


ETIQUETA_DE_PERMISO = {
    "editar_estructura_programa": "editar la estructura del programa",
    "editar_fechas_programa": "editar las fechas del programa",
}


class PermisoDenegado(Exception):
    """El rol no puede hacer esa edición."""


class Conflicto(Exception):
    """Alguien editó el programa entre que se calculó el impacto y se quiso guardar."""


class NoSePuedeDeshacer(Exception):
    """Deshacer esa edición dejaría sin sentido a otras que se hicieron después."""

    def __init__(self, mensaje: str, dependientes: Sequence[int]) -> None:
        super().__init__(mensaje)
        self.dependientes = tuple(dependientes)


class ProgramaNoExiste(KeyError):
    pass


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


class RepositorioPrograma(Protocol):
    def importar_programa(self, nombre: str, programa: Programa, calendario: Calendario) -> int: ...

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


def verificar_permiso(edicion: object, rol: str) -> str:
    permiso = permiso_de(edicion)
    if rol not in ROLES_CON_PERMISO[permiso]:
        raise PermisoDenegado(f"el rol «{rol}» no puede {ETIQUETA_DE_PERMISO[permiso]}")
    return permiso


class ServicioPrograma:
    def __init__(self, repositorio: RepositorioPrograma) -> None:
        self.repo = repositorio

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

    def proponer(self, programa_id: int, edicion: object, rol: str) -> Propuesta:
        """Qué pasaría si se aplicara. No guarda nada."""
        permiso = verificar_permiso(edicion, rol)
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

    def aplicar(self, programa_id: int, edicion: object, rol: str, usuario: str) -> Propuesta:
        """Propone y, si se puede, guarda con lo que el sistema mostró. Una edición que no se puede aplicar
        se devuelve sin guardar y con su motivo."""
        if not usuario:
            raise ValueError("toda edición dice quién la hizo")
        p = self.proponer(programa_id, edicion, rol)
        if not p.aplicable:
            return p
        p.guardada = self.repo.guardar_edicion(
            programa_id, edicion, rol=rol, usuario=usuario, impacto=p.impacto.resumen(), esperaba=p.esperaba
        )
        return p

    def deshacer(self, programa_id: int, edicion_id: int, rol: str, usuario: str) -> Vigente:
        """Revierte una edición, con el permiso que la hizo, si las que vinieron después siguen teniendo
        sentido sin ella. Si no, dice cuáles dependen de ella y no toca nada."""
        if not usuario:
            raise ValueError("todo deshacer dice quién lo hizo")
        v = self.abrir(programa_id)
        objetivo = next((e for e in v.aplicadas if e.id == edicion_id), None)
        if objetivo is None:
            raise KeyError(f"la edición {edicion_id} no está aplicada")
        verificar_permiso(objetivo.edicion, rol)
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
