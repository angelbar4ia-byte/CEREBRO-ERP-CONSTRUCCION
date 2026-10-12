"""
El adaptador de Postgres de `RepositorioBandeja` — `database/migraciones/0010_bandeja_de_propuestas.sql` (D-485).

Vive fuera de `core/` por lo mismo que los demás (D-182) y cumple el mismo contrato que la memoria (`core/tests/contrato_bandeja.py`).
Lo que aquí garantiza la base y no el código: una propuesta resuelta no se reescribe ni se borra, quien propone no la aprueba, y una
alerta activa por tipo y objeto es una sola fila (la que reaparece se cuenta con un `INSERT … ON CONFLICT`, sin carreras).
"""
from __future__ import annotations

from typing import Any, List, Mapping, Optional

import psycopg
from psycopg.types.json import Jsonb

from core.propuestas import Alerta, AlertaNoExiste, NuevaPropuesta, Propuesta, PropuestaNoExiste, YaResuelta

_P = ("id, tipo, objeto, valor_propuesto, evidencia, origen, propuesto_por, propuesto_con_rol, creada_en, estado, modelo, version_modelo,"
      " confianza, supuestos, base, resuelto_por, resuelto_con_rol, resuelta_en, nota, resultado")
_A = ("id, tipo, objeto, evidencia, parametro_usado, primera_vez, ultima_vez, veces_vista, estado, resuelto_por, resuelto_con_rol,"
      " resuelta_en, nota_resolucion")


def _json(x: Optional[Mapping[str, Any]]) -> Optional[Jsonb]:
    return None if x is None else Jsonb(dict(x))


class PostgresBandeja:
    def __init__(self, conexion: "psycopg.Connection") -> None:
        self.conn = conexion

    # ---- propuestas
    def agregar_propuesta(self, n: NuevaPropuesta) -> Propuesta:
        fila = self.conn.execute(
            "INSERT INTO propuesta (tipo, objeto, valor_propuesto, evidencia, origen, modelo, version_modelo, confianza, supuestos, base,"
            f" propuesto_por, propuesto_con_rol) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING {_P}",
            (n.tipo, n.objeto, _json(n.valor_propuesto), n.evidencia, n.origen, n.modelo, n.version_modelo, n.confianza, _json(n.supuestos),
             n.base, n.propuesto_por, n.propuesto_con_rol)).fetchone()
        return Propuesta(*fila)

    def propuesta(self, propuesta_id: int) -> Propuesta:
        fila = self.conn.execute(f"SELECT {_P} FROM propuesta WHERE id = %s", (propuesta_id,)).fetchone()
        if fila is None:
            raise PropuestaNoExiste(propuesta_id)
        return Propuesta(*fila)

    def propuestas(self, estado: Optional[str] = None, tipo: Optional[str] = None) -> List[Propuesta]:
        filas = self.conn.execute(
            f"SELECT {_P} FROM propuesta WHERE (%(e)s::text IS NULL OR estado = %(e)s) AND (%(t)s::text IS NULL OR tipo = %(t)s) ORDER BY id",
            {"e": estado, "t": tipo}).fetchall()
        return [Propuesta(*f) for f in filas]

    def parecidas(self, tipo: str, objeto: str, valor_propuesto: Mapping[str, Any]) -> List[Propuesta]:
        filas = self.conn.execute(
            f"SELECT {_P} FROM propuesta WHERE tipo = %s AND objeto = %s AND valor_propuesto = %s::jsonb ORDER BY id",
            (tipo, objeto, _json(valor_propuesto))).fetchall()
        return [Propuesta(*f) for f in filas]

    def resolver_propuesta(self, propuesta_id: int, estado: str, usuario: str, rol: str, nota: Optional[str],
                           resultado: Optional[Mapping[str, Any]]) -> Propuesta:
        fila = self.conn.execute(
            "UPDATE propuesta SET estado = %s, resuelto_por = %s, resuelto_con_rol = %s, resuelta_en = now(), nota = %s, resultado = %s"
            f" WHERE id = %s AND estado = 'pendiente' RETURNING {_P}",
            (estado, usuario, rol, nota, _json(resultado), propuesta_id)).fetchone()
        if fila is None:  # o no existe, o alguien la resolvió primero
            actual = self.propuesta(propuesta_id)
            raise YaResuelta(f"la propuesta {propuesta_id} ya está {actual.estado}", actual.estado)
        return Propuesta(*fila)

    # ---- alertas
    def registrar_alerta(self, tipo: str, objeto: str, evidencia: Mapping[str, Any], parametro_usado: Optional[Mapping[str, Any]]) -> Alerta:
        fila = self.conn.execute(
            "INSERT INTO alerta (tipo, objeto, evidencia, parametro_usado) VALUES (%s, %s, %s, %s)"
            " ON CONFLICT (tipo, objeto) WHERE estado = 'activa' DO UPDATE SET evidencia = EXCLUDED.evidencia, ultima_vez = now(),"
            " veces_vista = alerta.veces_vista + 1, parametro_usado = coalesce(EXCLUDED.parametro_usado, alerta.parametro_usado)"
            f" RETURNING {_A}", (tipo, objeto, _json(evidencia), _json(parametro_usado))).fetchone()
        return Alerta(*fila)

    def alerta(self, alerta_id: int) -> Alerta:
        fila = self.conn.execute(f"SELECT {_A} FROM alerta WHERE id = %s", (alerta_id,)).fetchone()
        if fila is None:
            raise AlertaNoExiste(alerta_id)
        return Alerta(*fila)

    def alertas(self, estado: Optional[str] = None, tipo: Optional[str] = None) -> List[Alerta]:
        filas = self.conn.execute(
            f"SELECT {_A} FROM alerta WHERE (%(e)s::text IS NULL OR estado = %(e)s) AND (%(t)s::text IS NULL OR tipo = %(t)s) ORDER BY id",
            {"e": estado, "t": tipo}).fetchall()
        return [Alerta(*f) for f in filas]

    def resolver_alerta(self, alerta_id: int, estado: str, usuario: str, rol: str, nota: str) -> Alerta:
        fila = self.conn.execute(
            "UPDATE alerta SET estado = %s, resuelto_por = %s, resuelto_con_rol = %s, resuelta_en = now(), nota_resolucion = %s"
            f" WHERE id = %s AND estado = 'activa' RETURNING {_A}", (estado, usuario, rol, nota, alerta_id)).fetchone()
        if fila is None:
            actual = self.alerta(alerta_id)
            raise YaResuelta(f"la alerta {alerta_id} ya está {actual.estado}", actual.estado)
        return Alerta(*fila)
