"""
El adaptador de Postgres de `RepositorioAccesos` — `database/migraciones/0004_usuarios_y_permisos.sql`.

Vive fuera de `core/` por lo mismo que `postgres_programa.py` (D-182). `permisos()` lee `ROL_FUNCION` cada vez que se
le pide: lo que se corrige en la tabla vale en la siguiente acción, sin reiniciar nada.
"""
from __future__ import annotations

from typing import Dict, FrozenSet, List, Optional, Sequence

import psycopg

from core.accesos import ROLES, UsuarioInvalido, Usuario, normalizar_correo, validar_usuario


class PostgresAccesos:
    def __init__(self, conexion: "psycopg.Connection") -> None:
        self.conn = conexion

    def _usuarios(self, donde: str = "", args: tuple = ()) -> List[Usuario]:
        filas = self.conn.execute(
            "SELECT u.id, u.nombre, u.correo, u.activo,"
            " coalesce(array_agg(r.clave ORDER BY r.clave) FILTER (WHERE r.clave IS NOT NULL), '{}')"
            " FROM usuario u LEFT JOIN usuario_rol ur ON ur.usuario_id = u.id LEFT JOIN rol r ON r.id = ur.rol_id"
            f" {donde} GROUP BY u.id ORDER BY u.id", args).fetchall()
        return [Usuario(r[0], r[1], r[2], r[3], tuple(r[4])) for r in filas]

    def usuario_por_correo(self, correo: str) -> Optional[Usuario]:
        encontrados = self._usuarios("WHERE u.correo = %s", (normalizar_correo(correo),))
        return encontrados[0] if encontrados else None

    def usuarios(self) -> List[Usuario]:
        return self._usuarios()

    def agregar_usuario(self, nombre: str, correo: str, roles: Sequence[str]) -> int:
        nombre, correo, roles = validar_usuario(nombre, correo, roles)
        try:
            with self.conn.transaction():
                uid = self.conn.execute("INSERT INTO usuario (nombre, correo) VALUES (%s, %s) RETURNING id", (nombre, correo)).fetchone()[0]
                for r in roles:
                    self.conn.execute("INSERT INTO usuario_rol (usuario_id, rol_id) SELECT %s, id FROM rol WHERE clave = %s", (uid, r))
        except psycopg.errors.UniqueViolation:
            raise UsuarioInvalido(f"ya hay un usuario con el correo {correo}") from None
        return uid

    def desactivar_usuario(self, correo: str) -> None:
        n = self.conn.execute("UPDATE usuario SET activo = false WHERE correo = %s", (normalizar_correo(correo),)).rowcount
        if n != 1:
            raise UsuarioInvalido(f"no hay un usuario con el correo {normalizar_correo(correo)}")

    def permisos(self) -> Dict[str, FrozenSet[str]]:
        out: Dict[str, set] = {}
        for funcion, rol in self.conn.execute(
            "SELECT f.clave, r.clave FROM rol_funcion rf JOIN funcion_atomica f ON f.id = rf.funcion_id JOIN rol r ON r.id = rf.rol_id"
        ):
            out.setdefault(funcion, set()).add(rol)
        return {f: frozenset(rs) for f, rs in out.items()}

    def dar_funcion(self, rol: str, funcion: str) -> None:
        if rol not in ROLES:
            raise UsuarioInvalido(f"no existe el rol {rol}")
        with self.conn.transaction():
            self.conn.execute("INSERT INTO funcion_atomica (clave) VALUES (%s) ON CONFLICT (clave) DO NOTHING", (funcion,))
            self.conn.execute(
                "INSERT INTO rol_funcion (rol_id, funcion_id) SELECT r.id, f.id FROM rol r, funcion_atomica f"
                " WHERE r.clave = %s AND f.clave = %s ON CONFLICT (rol_id, funcion_id) DO NOTHING", (rol, funcion))

    def quitar_funcion(self, rol: str, funcion: str) -> None:
        self.conn.execute(
            "DELETE FROM rol_funcion WHERE rol_id = (SELECT id FROM rol WHERE clave = %s)"
            " AND funcion_id = (SELECT id FROM funcion_atomica WHERE clave = %s)", (rol, funcion))
