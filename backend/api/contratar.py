"""
Contratar un subárbol del presupuesto, desde la terminal — D-475.

    # solo revisar: dice qué PU se fijan, cuánto cambia el monto y qué pide confirmación, y no escribe nada
    python3 -m api.contratar --postgres postgresql://… --usuario luis@obra.mx --presupuesto CAS-00004 --bloque CAS-00004#1/NIV-00001#1

    # contratarlo (sin --bloque, el presupuesto entero)
    python3 -m api.contratar … --contratar
    python3 -m api.contratar … --contratar --confirmar EST-10010 --confirmar EST-10020    (su PU se mueve más de 5 %, o no tiene matriz)

Contratar fija el PU de cada concepto del bloque a hoy y congela el bloque: lo que cambie después va por control de cambio. Quien
contrata es un usuario dado de alta (`api.usuarios`) de uno de los roles que tienen `contratar_subarbol` en `ROL_FUNCION` —Control de
obra por omisión—: queda en la contratación con su correo y el rol con que la hizo. Sin `--contratar` no se escribe nada.
"""
from __future__ import annotations

import argparse
import sys
from typing import Optional, Sequence, TextIO

from core.accesos import PermisoDenegado, RepositorioAccesos, normalizar_correo
from core.catalogo import CatalogoCambio, RepositorioCatalogo, YaContratado
from core.contratacion import ContratacionPendiente, ServicioContratacion, informe_de_contratacion


def contratar(
    catalogo: RepositorioCatalogo,
    accesos: RepositorioAccesos,
    *,
    correo: str,
    presupuesto: str,
    bloque: Optional[str] = None,
    contratar_ya: bool = False,
    confirmados: Sequence[str] = (),
    salida: TextIO = sys.stdout,
    errores: TextIO = sys.stderr,
) -> int:
    """0 si se revisó o se contrató; 1 si no se puede o falta una confirmación; 2 si quien contrata no puede."""
    u = accesos.usuario_por_correo(normalizar_correo(correo))
    if u is None or not u.activo:
        print(f"No se pudo: {correo} no es un usuario dado de alta y activo (python3 -m api.usuarios).", file=errores)
        return 2
    servicio = ServicioContratacion(catalogo, permisos=accesos.permisos)
    roles = list(u.roles)
    donde = presupuesto if not presupuesto.isdigit() else int(presupuesto)
    try:
        p = servicio.proponer(donde, roles, u.correo, bloque, confirmados)
        print(informe_de_contratacion(p), file=salida)
        if not contratar_ya:
            print("\nNo se escribió nada: con --contratar se contrata lo que se propuso.", file=salida)
            return 0
        _, r = servicio.contratar(donde, roles, u.correo, bloque, confirmados)
    except PermisoDenegado as e:
        print(f"No se pudo: {e}", file=errores)
        return 2
    except ContratacionPendiente as e:
        print(f"No se contrató: {e}. Con --confirmar CLAVE alguien dice que sí.", file=errores)
        return 1
    except (ValueError, YaContratado, CatalogoCambio) as e:
        print(f"No se pudo: {e}", file=errores)
        return 1
    print(f"\nContratado: {r.versiones_nuevas} versiones nuevas y {r.renglones_fijados} renglones fijados (contratación {r.carga_id}).", file=salida)
    return 0


def main(argv: Optional[Sequence[str]] = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--postgres", required=True, help="cadena de conexión")
    ap.add_argument("--usuario", required=True, help="el correo de quien contrata: un usuario dado de alta")
    ap.add_argument("--presupuesto", required=True, help="la clave del capítulo del presupuesto (o su id)")
    ap.add_argument("--bloque", help="la ruta natural del bloque (clave#n/clave#n…); si no se dice, el presupuesto entero")
    ap.add_argument("--contratar", action="store_true", help="contrata lo que se propone; sin esto, solo se revisa")
    ap.add_argument("--confirmar", action="append", default=[], metavar="CLAVE", help="confirma un concepto que pide confirmación")
    a = ap.parse_args(argv)
    import psycopg

    from infra.postgres_accesos import PostgresAccesos
    from infra.postgres_catalogo import PostgresCatalogo
    from infra.postgres_programa import aplicar_migraciones

    conn = psycopg.connect(a.postgres, autocommit=True)
    aplicar_migraciones(conn)
    return contratar(PostgresCatalogo(conn), PostgresAccesos(conn), correo=a.usuario, presupuesto=a.presupuesto, bloque=a.bloque,
                     contratar_ya=a.contratar, confirmados=a.confirmar)


if __name__ == "__main__":
    sys.exit(main())
