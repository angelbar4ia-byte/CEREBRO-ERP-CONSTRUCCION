"""
El adaptador en memoria de `RepositorioPrograma` — para las pruebas y para quien quiera probar sin base
(misma idea que el adaptador de `motor_calculo`, D-182). Cumple el mismo contrato que el de Postgres:
las pruebas de `test_servicio_programa.py` corren las mismas exigencias contra los dos.
"""
from __future__ import annotations

from dataclasses import replace
from datetime import datetime, timezone
from typing import Dict, List, Mapping, Optional

from .motor_cpm import Calendario
from .programa import Programa, edicion_a_dict, edicion_desde_dict
from .servicio_programa import Conflicto, EdicionGuardada, ProgramaGuardado, ProgramaNoExiste, ResumenPrograma


class MemoriaPrograma:
    def __init__(self) -> None:
        self._programas: Dict[int, ProgramaGuardado] = {}
        self._versiones: Dict[int, int] = {}
        self._ediciones: Dict[int, List[EdicionGuardada]] = {}
        self._llegada: Dict[int, tuple] = {}  # id → (cuándo, quién, con qué rol)
        self._sig_programa = 0
        self._sig_edicion = 0

    def importar_programa(self, nombre: str, programa: Programa, calendario: Calendario, *,
                          usuario: Optional[str] = None, rol: Optional[str] = None) -> int:
        self._sig_programa += 1
        self._llegada[self._sig_programa] = (datetime.now(timezone.utc), usuario, rol)
        self._programas[self._sig_programa] = ProgramaGuardado(
            id=self._sig_programa,
            nombre=nombre,
            filas=[replace(f, vinculos="") for f in programa.filas],  # los vínculos ya están resueltos aparte
            vinculos=[(v, programa.origenes.get(v)) for v in programa.vinculos],
            rechazados=list(programa.rechazados),
            calendario=calendario,
        )
        self._ediciones[self._sig_programa] = []
        self._versiones[self._sig_programa] = 0
        return self._sig_programa

    def listar_programas(self) -> List[ResumenPrograma]:
        out = []
        for pid, g in sorted(self._programas.items()):
            creado, quien, rol = self._llegada[pid]
            out.append(ResumenPrograma(
                id=pid, nombre=g.nombre, version=self._versiones[pid], partidas=sum(f.es_partida for f in g.filas),
                vinculos=len(g.vinculos), rechazados=len(g.rechazados),
                ediciones=sum(e.estado == "aplicada" for e in self._ediciones[pid]),
                creado_en=creado, importado_por=quien, importado_con_rol=rol,
            ))
        return out

    def leer_programa(self, programa_id: int) -> ProgramaGuardado:
        try:
            return replace(self._programas[programa_id], version=self._versiones[programa_id])
        except KeyError:
            raise ProgramaNoExiste(programa_id) from None

    def ediciones(self, programa_id: int) -> List[EdicionGuardada]:
        self.leer_programa(programa_id)
        return list(self._ediciones[programa_id])

    def _candado(self, programa_id: int, esperaba: int) -> None:
        if self._versiones[programa_id] != esperaba:
            raise Conflicto(f"el programa ya va en la versión {self._versiones[programa_id]}, no en la {esperaba}")

    def guardar_edicion(self, programa_id: int, edicion: object, *, rol: str, usuario: str,
                        impacto: Mapping[str, object], esperaba: int) -> EdicionGuardada:
        self.leer_programa(programa_id)
        self._candado(programa_id, esperaba)
        self._sig_edicion += 1
        # se guarda como se guardaría en una base: pasa por su forma de texto y vuelve
        g = EdicionGuardada(
            id=self._sig_edicion,
            secuencia=len(self._ediciones[programa_id]) + 1,
            edicion=edicion_desde_dict(edicion_a_dict(edicion)),
            rol=rol,
            usuario=usuario,
            estado="aplicada",
            impacto=dict(impacto),
            creada_en=datetime.now(timezone.utc),
        )
        self._ediciones[programa_id].append(g)
        self._versiones[programa_id] += 1
        return g

    def revertir_edicion(self, programa_id: int, edicion_id: int, *, usuario: str, esperaba: int) -> None:
        self.leer_programa(programa_id)
        self._candado(programa_id, esperaba)
        lista = self._ediciones[programa_id]
        for i, e in enumerate(lista):
            if e.id == edicion_id:
                if e.estado != "aplicada":
                    raise KeyError(f"la edición {edicion_id} no está aplicada")
                lista[i] = replace(e, estado="revertida", revertida_por=usuario, revertida_en=datetime.now(timezone.utc))
                self._versiones[programa_id] += 1
                return
        raise KeyError(f"no hay edición {edicion_id}")
