"""
El adaptador de Postgres de `RepositorioPrograma` — `database/migraciones/0001_programa.sql`.

Vive fuera de `core/` a propósito: el dominio no conoce ninguna base (D-182). Usa `psycopg` (3) y una conexión
que le pasa quien lo arma; cada operación va en su propia transacción. El candado contra editores simultáneos
es `programa.version`, que se compara y se sube con la fila bloqueada (`FOR UPDATE`).
"""
from __future__ import annotations

import json
from datetime import datetime
from decimal import Decimal
from fractions import Fraction
from pathlib import Path
from typing import Any, List, Mapping, Optional, Sequence

import psycopg
from psycopg.types.json import Jsonb

from core.motor_cpm import ALIAS_TIPO, Calendario, Vinculo
from core.programa import (
    Fila,
    Programa,
    Rechazado,
    edicion_a_dict,
    edicion_desde_dict,
    origen_de_edicion,
)
from core.servicio_programa import (
    Conflicto,
    EdicionGuardada,
    Heredada,
    ProgramaGuardado,
    ProgramaNoExiste,
    ResumenPrograma,
    YaReemplazado,
)

MIGRACIONES = Path(__file__).resolve().parents[2] / "database" / "migraciones"
ENUM_A_TIPO = dict(ALIAS_TIPO)  # fin_inicio → FS, y así
TIPO_A_ENUM = {v: k for k, v in ALIAS_TIPO.items()}


def aplicar_migraciones(conn: "psycopg.Connection") -> List[str]:
    """Corre, en orden, las migraciones que aún no se han corrido. Devuelve cuáles corrió."""
    with conn.transaction():
        conn.execute("CREATE TABLE IF NOT EXISTS migracion (nombre text PRIMARY KEY, aplicada_en timestamptz NOT NULL DEFAULT now())")
        hechas = {r[0] for r in conn.execute("SELECT nombre FROM migracion")}
        nuevas = []
        for f in sorted(MIGRACIONES.glob("*.sql")):
            if f.name not in hechas:
                conn.execute(f.read_text(encoding="utf-8"))
                conn.execute("INSERT INTO migracion (nombre) VALUES (%s)", (f.name,))
                nuevas.append(f.name)
    return nuevas


def _a_numeric(x) -> Decimal:
    """Un `Fraction` de días como el decimal exacto que se guarda; si no cabe exacto, no se guarda."""
    f = Fraction(x)
    d = f.denominator
    for p in (2, 5):
        while d % p == 0:
            d //= p
    if d != 1:
        raise ValueError(f"{f} no tiene expresión decimal exacta: los días se guardan en NUMERIC")
    return Decimal(f.numerator) / Decimal(f.denominator)


def _a_fraction(x) -> Fraction:
    return Fraction(Decimal(x))


class PostgresPrograma:
    def __init__(self, conexion: "psycopg.Connection") -> None:
        self.conn = conexion

    # ------------------------------------------------------------------ importar
    def importar_programa(self, nombre: str, programa: Programa, calendario: Calendario, *,
                          usuario: Optional[str] = None, rol: Optional[str] = None) -> int:
        with self.conn.transaction():
            return self._insertar(nombre, programa, calendario, usuario, rol)

    def importar_version(self, anterior_id: int, nombre: str, programa: Programa, calendario: Calendario, *, usuario: str, rol: str,
                         heredadas: Sequence[Heredada], traspaso: Mapping[str, Any], esperaba: int) -> int:
        with self.conn.transaction():
            self._bloquear(anterior_id, esperaba)  # el anterior, con su fila bloqueada: nadie edita mientras se hereda
            sucesor = self.conn.execute("SELECT id FROM programa WHERE version_de = %s", (anterior_id,)).fetchone()
            if sucesor is not None:
                raise YaReemplazado(f"el programa {anterior_id} ya tiene una versión más nueva, la {sucesor[0]}", sucesor[0])
            pid = self._insertar(nombre, programa, calendario, usuario, rol, anterior_id, traspaso, len(heredadas))
            for i, h in enumerate(heredadas, start=1):
                datos = edicion_a_dict(h.edicion)
                tipo = datos.pop("edicion")
                self.conn.execute(
                    "INSERT INTO edicion_programa (programa_id, secuencia, edicion, datos, origen, rol, usuario, impacto, creada_en, heredada_de)"
                    " VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                    (pid, i, tipo, Jsonb(datos), origen_de_edicion(h.edicion), h.rol, h.usuario, Jsonb(dict(h.impacto)), h.creada_en, h.heredada_de),
                )
        return pid

    def _insertar(self, nombre: str, programa: Programa, calendario: Calendario, usuario: Optional[str], rol: Optional[str],
                  version_de: Optional[int] = None, traspaso: Optional[Mapping[str, Any]] = None, version: int = 0) -> int:
        pid = self.conn.execute(
            "INSERT INTO programa (nombre, calendario, importado_por, importado_con_rol, version_de, traspaso, version)"
            " VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING id",
            (nombre, Jsonb(calendario.a_dict()), usuario, rol, version_de, None if traspaso is None else Jsonb(dict(traspaso)), version),
        ).fetchone()[0]
        with self.conn.cursor() as cur:
            cur.executemany(
                "INSERT INTO programa_fila (programa_id, oid, orden, fila, nivel, tipo, clave, descripcion, inicio, termino, dias, frente, etapa)"
                " VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                [
                    (pid, f.llave, i, f.fila, f.nivel, f.tipo, f.clave, f.descripcion, f.inicio, f.termino, _a_numeric(f.dias), f.frente, f.etapa)
                    for i, f in enumerate(programa.filas)
                ],
            )
            cur.executemany(
                "INSERT INTO programa_vinculo (programa_id, predecesora_oid, sucesora_oid, tipo_vinculo, traslape_espera, origen)"
                " VALUES (%s, %s, %s, %s, %s, %s)",
                [
                    (pid, v.predecesora, v.sucesora, TIPO_A_ENUM[v.tipo], _a_numeric(v.desfase), programa.origenes.get(v))
                    for v in programa.vinculos
                ],
            )
            cur.executemany(
                "INSERT INTO programa_vinculo (programa_id, sucesora_oid, estado, motivo, texto_fuente) VALUES (%s, %s, 'rechazado', %s, %s)",
                [(pid, r.sucesora, r.motivo, r.token) for r in programa.rechazados],
            )
        return pid

    # ------------------------------------------------------------------ listar
    def listar_programas(self) -> List[ResumenPrograma]:
        with self.conn.transaction():
            filas = self.conn.execute(
                """
                SELECT p.id, p.nombre, p.version, p.creado_en, p.importado_por, p.importado_con_rol, p.version_de,
                       (SELECT count(*) FROM programa_fila f WHERE f.programa_id = p.id
                         AND f.tipo = 'Concepto' AND f.inicio IS NOT NULL AND f.dias > 0),
                       (SELECT count(*) FROM programa_vinculo v WHERE v.programa_id = p.id AND v.estado = 'vigente'),
                       (SELECT count(*) FROM programa_vinculo v WHERE v.programa_id = p.id AND v.estado = 'rechazado'),
                       (SELECT count(*) FROM edicion_programa e WHERE e.programa_id = p.id AND e.estado = 'aplicada')
                  FROM programa p ORDER BY p.id
                """).fetchall()
        return [
            ResumenPrograma(id=r[0], nombre=r[1], version=r[2], creado_en=r[3], importado_por=r[4], importado_con_rol=r[5],
                            version_de=r[6], partidas=r[7], vinculos=r[8], rechazados=r[9], ediciones=r[10])
            for r in filas
        ]

    # ------------------------------------------------------------------ leer
    def leer_programa(self, programa_id: int) -> ProgramaGuardado:
        with self.conn.transaction():
            fila = self.conn.execute(
                "SELECT nombre, calendario, version, version_de, traspaso FROM programa WHERE id = %s", (programa_id,)).fetchone()
            if fila is None:
                raise ProgramaNoExiste(programa_id)
            nombre, cal, version, version_de, traspaso = fila
            filas = [
                Fila(llave=r[0], fila=r[1], nivel=r[2], tipo=r[3], clave=r[4], descripcion=r[5], inicio=r[6], termino=r[7],
                     dias=_a_fraction(r[8]), frente=r[9], etapa=r[10])
                for r in self.conn.execute(
                    "SELECT oid, fila, nivel, tipo, clave, descripcion, inicio, termino, dias, frente, etapa"
                    " FROM programa_fila WHERE programa_id = %s ORDER BY orden", (programa_id,))
            ]
            por_oid = {f.llave: f for f in filas}
            vinculos = [
                (Vinculo(r[0], r[1], ENUM_A_TIPO[r[2]], _a_fraction(r[3])), r[4])
                for r in self.conn.execute(
                    "SELECT predecesora_oid, sucesora_oid, tipo_vinculo, traslape_espera, origen FROM programa_vinculo"
                    " WHERE programa_id = %s AND estado = 'vigente' ORDER BY id", (programa_id,))
            ]
            rechazados = [
                Rechazado(r[0], por_oid[r[0]].fila, r[1], r[2])
                for r in self.conn.execute(
                    "SELECT sucesora_oid, texto_fuente, motivo FROM programa_vinculo"
                    " WHERE programa_id = %s AND estado = 'rechazado' ORDER BY id", (programa_id,))
            ]
        return ProgramaGuardado(programa_id, nombre, filas, vinculos, rechazados, Calendario.desde_dict(cal), version, version_de, traspaso)

    def ediciones(self, programa_id: int) -> List[EdicionGuardada]:
        with self.conn.transaction():
            if self.conn.execute("SELECT 1 FROM programa WHERE id = %s", (programa_id,)).fetchone() is None:
                raise ProgramaNoExiste(programa_id)
            filas = self.conn.execute(
                "SELECT id, secuencia, edicion, datos, rol, usuario, estado, impacto, creada_en, revertida_por, revertida_en, heredada_de"
                " FROM edicion_programa WHERE programa_id = %s ORDER BY secuencia", (programa_id,)).fetchall()
        return [
            EdicionGuardada(id=r[0], secuencia=r[1], edicion=edicion_desde_dict({"edicion": r[2], **r[3]}), rol=r[4], usuario=r[5],
                            estado=r[6], impacto=r[7], creada_en=r[8], revertida_por=r[9], revertida_en=r[10], heredada_de=r[11])
            for r in filas
        ]

    # ------------------------------------------------------------------ escribir
    def _bloquear(self, programa_id: int, esperaba: int) -> None:
        fila = self.conn.execute("SELECT version FROM programa WHERE id = %s FOR UPDATE", (programa_id,)).fetchone()
        if fila is None:
            raise ProgramaNoExiste(programa_id)
        if fila[0] != esperaba:
            raise Conflicto(f"el programa ya va en la versión {fila[0]}, no en la {esperaba}")

    def guardar_edicion(self, programa_id: int, edicion: object, *, rol: str, usuario: str,
                        impacto: Mapping[str, object], esperaba: int) -> EdicionGuardada:
        datos = edicion_a_dict(edicion)
        nombre = datos.pop("edicion")
        with self.conn.transaction():
            self._bloquear(programa_id, esperaba)
            secuencia = self.conn.execute(
                "SELECT coalesce(max(secuencia), 0) + 1 FROM edicion_programa WHERE programa_id = %s", (programa_id,)).fetchone()[0]
            r = self.conn.execute(
                "INSERT INTO edicion_programa (programa_id, secuencia, edicion, datos, origen, rol, usuario, impacto)"
                " VALUES (%s, %s, %s, %s, %s, %s, %s, %s) RETURNING id, creada_en",
                (programa_id, secuencia, nombre, Jsonb(datos), origen_de_edicion(edicion), rol, usuario, Jsonb(dict(impacto))),
            ).fetchone()
            self.conn.execute("UPDATE programa SET version = version + 1 WHERE id = %s", (programa_id,))
        return EdicionGuardada(id=r[0], secuencia=secuencia, edicion=edicion_desde_dict({"edicion": nombre, **datos}), rol=rol,
                               usuario=usuario, estado="aplicada", impacto=dict(impacto), creada_en=r[1])

    def revertir_edicion(self, programa_id: int, edicion_id: int, *, usuario: str, esperaba: int) -> None:
        with self.conn.transaction():
            self._bloquear(programa_id, esperaba)
            n = self.conn.execute(
                "UPDATE edicion_programa SET estado = 'revertida', revertida_en = now(), revertida_por = %s"
                " WHERE id = %s AND programa_id = %s AND estado = 'aplicada'", (usuario, edicion_id, programa_id)).rowcount
            if n != 1:
                raise KeyError(f"la edición {edicion_id} no está aplicada")
            self.conn.execute("UPDATE programa SET version = version + 1 WHERE id = %s", (programa_id,))
