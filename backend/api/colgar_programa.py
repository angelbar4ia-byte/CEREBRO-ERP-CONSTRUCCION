"""
Colgar un programa del presupuesto, desde la terminal — D-474.

    # solo revisar: dice qué casa y qué no, de los dos lados, y no escribe nada
    python3 -m api.colgar_programa --postgres postgresql://… --usuario luis@obra.mx --programa 3

    # colgarlo (el presupuesto se encuentra por la clave del capítulo con que abre el programa)
    python3 -m api.colgar_programa … --colgar
    python3 -m api.colgar_programa … --colgar --presupuesto 2        (di cuál, si el programa no abre con su capítulo)
    python3 -m api.colgar_programa … --colgar --forzar               (casan menos de la mitad de los conceptos y quien decide lo confirma)

Quien cuelga es un usuario dado de alta (`api.usuarios`) de uno de los roles que pueden editar la estructura del programa —Control de
obra por omisión—: queda en la bitácora de colgaduras con su correo y el rol con que lo hizo. Sin `--colgar` no se escribe nada.
Un enlace puesto no se mueve: volver a colgar solo agrega los que falten.
"""
from __future__ import annotations

import argparse
import sys
from typing import Optional, Sequence, TextIO

from core.accesos import PermisoDenegado, RepositorioAccesos, normalizar_correo
from core.catalogo import RepositorioCatalogo
from core.colgado import ColgadoNoCuadra, ServicioColgado, informe_de_colgado
from core.servicio_programa import ProgramaNoExiste, RepositorioPrograma, ServicioPrograma, YaColgado, YaReemplazado


def colgar(
    programas: RepositorioPrograma,
    catalogo: RepositorioCatalogo,
    accesos: RepositorioAccesos,
    *,
    correo: str,
    programa: int,
    presupuesto: Optional[int] = None,
    colgar_ya: bool = False,
    forzar: bool = False,
    salida: TextIO = sys.stdout,
    errores: TextIO = sys.stderr,
) -> int:
    """0 si se revisó o se colgó; 1 si no cuadra o no se puede; 2 si quien cuelga no puede."""
    u = accesos.usuario_por_correo(normalizar_correo(correo))
    if u is None or not u.activo:
        print(f"No se pudo: {correo} no es un usuario dado de alta y activo (python3 -m api.usuarios).", file=errores)
        return 2
    servicio = ServicioColgado(ServicioPrograma(programas, permisos=accesos.permisos), catalogo)
    roles = list(u.roles)
    try:
        a = servicio.proponer(programa, roles, presupuesto)
        print(informe_de_colgado(a), file=salida)
        if not colgar_ya:
            print("\nNo se escribió nada: con --colgar se cuelga lo que casa.", file=salida)
            return 0
        a = servicio.colgar(programa, roles, u.correo, presupuesto, forzar=forzar)
    except PermisoDenegado as e:
        print(f"No se pudo: {e}", file=errores)
        return 2
    except ProgramaNoExiste:
        print(f"No se pudo: no hay programa {programa}.", file=errores)
        return 1
    except (ColgadoNoCuadra, YaColgado, YaReemplazado) as e:
        print(f"No se pudo: {e}", file=errores)
        return 1
    print("\n" + (f"Se pusieron {a.nuevos} enlace(s) nuevos." if a.nuevos else "No había enlaces nuevos que poner."), file=salida)
    return 0


def main(argv: Optional[Sequence[str]] = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--postgres", required=True, help="cadena de conexión")
    ap.add_argument("--usuario", required=True, help="el correo de quien cuelga: un usuario dado de alta")
    ap.add_argument("--programa", required=True, type=int, help="el id del programa (el de la lista de programas)")
    ap.add_argument("--presupuesto", type=int, help="el id del presupuesto; si no se dice, el de la clave del capítulo con que abre el programa")
    ap.add_argument("--colgar", action="store_true", help="cuelga lo que casa; sin esto, solo se revisa")
    ap.add_argument("--forzar", action="store_true", help="confirma colgar aunque casen menos de la mitad de los conceptos")
    a = ap.parse_args(argv)
    import psycopg

    from infra.postgres_accesos import PostgresAccesos
    from infra.postgres_catalogo import PostgresCatalogo
    from infra.postgres_programa import PostgresPrograma, aplicar_migraciones

    conn = psycopg.connect(a.postgres, autocommit=True)
    aplicar_migraciones(conn)
    return colgar(PostgresPrograma(conn), PostgresCatalogo(conn), PostgresAccesos(conn), correo=a.usuario, programa=a.programa,
                  presupuesto=a.presupuesto, colgar_ya=a.colgar, forzar=a.forzar)


if __name__ == "__main__":
    sys.exit(main())
