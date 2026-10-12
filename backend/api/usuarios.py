"""
Los usuarios de la base, desde la terminal — B-96 (D-469).

    python3 -m api.usuarios --postgres postgresql://… agregar luis@obra.mx "Luis Pérez" control_de_obra
    python3 -m api.usuarios --postgres postgresql://… agregar ana@obra.mx "Ana Soto" residente supervisor
    python3 -m api.usuarios --postgres postgresql://… retirar luis@obra.mx
    python3 -m api.usuarios --postgres postgresql://… listar

`MODELO.md` §5b no define todavía quién da de alta a un usuario (`asignar_residente` y `asignar_supervision` son de
Control de obra, pero no hay una función para crear personas): hasta que se decida, es quien administra la base.
Un usuario se retira, no se borra: su correo sigue en la bitácora.
"""
from __future__ import annotations

import argparse
import sys

import psycopg

from core.accesos import ROLES, UsuarioInvalido
from infra.postgres_accesos import PostgresAccesos
from infra.postgres_programa import aplicar_migraciones


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--postgres", required=True, help="cadena de conexión")
    sub = ap.add_subparsers(dest="orden", required=True)
    a = sub.add_parser("agregar", help="da de alta a un usuario")
    a.add_argument("correo")
    a.add_argument("nombre")
    a.add_argument("roles", nargs="*", help=f"uno o más de: {', '.join(ROLES)}")
    sub.add_parser("listar", help="los usuarios, del más viejo al más nuevo")
    r = sub.add_parser("retirar", help="retira a un usuario: ya no entra, y su correo sigue en la bitácora")
    r.add_argument("correo")
    args = ap.parse_args(argv)
    conn = psycopg.connect(args.postgres, autocommit=True)
    aplicar_migraciones(conn)
    accesos = PostgresAccesos(conn)
    try:
        if args.orden == "agregar":
            uid = accesos.agregar_usuario(args.nombre, args.correo, args.roles)
            print(f"Usuario {uid}: {args.correo}")
        elif args.orden == "retirar":
            accesos.desactivar_usuario(args.correo)
            print(f"Retirado: {args.correo}")
        else:
            for u in accesos.usuarios():
                print(f"{u.id}\t{u.correo}\t{u.nombre}\t{','.join(u.roles) or '-'}\t{'activo' if u.activo else 'retirado'}")
    except UsuarioInvalido as e:
        print(f"No se pudo: {e}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
