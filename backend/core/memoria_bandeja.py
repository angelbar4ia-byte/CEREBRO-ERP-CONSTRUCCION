"""
El adaptador en memoria de `RepositorioBandeja` — para las pruebas y para trabajar sin base (D-485).

Cumple el mismo contrato que `infra/postgres_bandeja.py` (`core/tests/contrato_bandeja.py`). Lo que la base garantiza con
restricciones y disparadores, aquí lo garantiza el código: una propuesta se resuelve una vez, quien propone no la aprueba, una alerta
activa por tipo y objeto, y nada se borra.
"""
from __future__ import annotations

import copy
from dataclasses import replace
from datetime import datetime, timezone
from typing import Any, Dict, List, Mapping, Optional

from .propuestas import (
    Alerta,
    AlertaNoExiste,
    NuevaPropuesta,
    Propuesta,
    PropuestaNoExiste,
    YaResuelta,
)


def _ahora() -> datetime:
    return datetime.now(timezone.utc)


class MemoriaBandeja:
    def __init__(self) -> None:
        self._propuestas: Dict[int, Propuesta] = {}
        self._alertas: Dict[int, Alerta] = {}
        self._sig_propuesta = 0
        self._sig_alerta = 0

    # ---- propuestas
    def agregar_propuesta(self, nueva: NuevaPropuesta) -> Propuesta:
        self._sig_propuesta += 1
        p = Propuesta(
            self._sig_propuesta, nueva.tipo, nueva.objeto, copy.deepcopy(dict(nueva.valor_propuesto)), nueva.evidencia, nueva.origen,
            nueva.propuesto_por, nueva.propuesto_con_rol, _ahora(), "pendiente", nueva.modelo, nueva.version_modelo, nueva.confianza,
            None if nueva.supuestos is None else copy.deepcopy(dict(nueva.supuestos)), nueva.base)
        self._propuestas[p.id] = p
        return p

    def propuesta(self, propuesta_id: int) -> Propuesta:
        try:
            return self._propuestas[propuesta_id]
        except KeyError:
            raise PropuestaNoExiste(propuesta_id) from None

    def propuestas(self, estado: Optional[str] = None, tipo: Optional[str] = None) -> List[Propuesta]:
        return [p for _, p in sorted(self._propuestas.items())
                if (estado is None or p.estado == estado) and (tipo is None or p.tipo == tipo)]

    def parecidas(self, tipo: str, objeto: str, valor_propuesto: Mapping[str, Any]) -> List[Propuesta]:
        return [p for p in self.propuestas(tipo=tipo) if p.objeto == objeto and dict(p.valor_propuesto) == dict(valor_propuesto)]

    def resolver_propuesta(self, propuesta_id: int, estado: str, usuario: str, rol: str, nota: Optional[str],
                           resultado: Optional[Mapping[str, Any]]) -> Propuesta:
        p = self.propuesta(propuesta_id)
        if p.estado != "pendiente":
            raise YaResuelta(f"la propuesta {propuesta_id} ya está {p.estado}", p.estado)
        if estado == "aprobada" and usuario.casefold() == p.propuesto_por.casefold():
            raise ValueError("quien propone no aprueba lo suyo")
        if estado == "aprobada" and resultado is None:
            raise ValueError("una propuesta aprobada guarda lo que hizo el sistema")
        if estado == "rechazada" and not (nota or "").strip():
            raise ValueError("rechazar pide decir por qué")
        r = replace(p, estado=estado, resuelto_por=usuario, resuelto_con_rol=rol, resuelta_en=_ahora(), nota=nota,
                    resultado=None if resultado is None else copy.deepcopy(dict(resultado)))
        self._propuestas[propuesta_id] = r
        return r

    # ---- alertas
    def registrar_alerta(self, tipo: str, objeto: str, evidencia: Mapping[str, Any], parametro_usado: Optional[Mapping[str, Any]]) -> Alerta:
        ahora = _ahora()
        for a in self._alertas.values():
            if a.estado == "activa" and a.tipo == tipo and a.objeto == objeto:
                r = replace(a, evidencia=copy.deepcopy(dict(evidencia)), ultima_vez=ahora, veces_vista=a.veces_vista + 1,
                            parametro_usado=a.parametro_usado if parametro_usado is None else copy.deepcopy(dict(parametro_usado)))
                self._alertas[a.id] = r
                return r
        self._sig_alerta += 1
        a = Alerta(self._sig_alerta, tipo, objeto, copy.deepcopy(dict(evidencia)),
                   None if parametro_usado is None else copy.deepcopy(dict(parametro_usado)), ahora, ahora, 1, "activa")
        self._alertas[a.id] = a
        return a

    def alerta(self, alerta_id: int) -> Alerta:
        try:
            return self._alertas[alerta_id]
        except KeyError:
            raise AlertaNoExiste(alerta_id) from None

    def alertas(self, estado: Optional[str] = None, tipo: Optional[str] = None) -> List[Alerta]:
        return [a for _, a in sorted(self._alertas.items())
                if (estado is None or a.estado == estado) and (tipo is None or a.tipo == tipo)]

    def resolver_alerta(self, alerta_id: int, estado: str, usuario: str, rol: str, nota: str) -> Alerta:
        a = self.alerta(alerta_id)
        if a.estado != "activa":
            raise YaResuelta(f"la alerta {alerta_id} ya está {a.estado}", a.estado)
        if not (nota or "").strip():
            raise ValueError("una alerta se cierra diciendo qué era")
        r = replace(a, estado=estado, resuelto_por=usuario, resuelto_con_rol=rol, resuelta_en=_ahora(), nota_resolucion=nota)
        self._alertas[alerta_id] = r
        return r
