"""
Clonar un insumo, o corregir el prefijo de varios, desde la terminal — D-478.

    # un insumo: solo revisar (dice qué pasaría y no escribe nada)
    python3 -m api.clonar --postgres postgresql://… --usuario luis@obra.mx --original AUX-00001 --clave PRE-00120 --modo sustituir

    # hacerlo
    python3 -m api.clonar … --original AUX-00001 --clave PRE-00120 --modo sustituir --clonar

    # P-11: las 79 trabes, mallas y nervaduras que OPUS llama AUX- siendo materiales pasan a PRE-, desde el PRE-00120
    python3 -m api.clonar … --corregir-prefijo AUX --por PRE --desde 120
    python3 -m api.clonar … --corregir-prefijo AUX --por PRE --desde 120 --clonar

Clonar y mantener deja vivos los dos; clonar y sustituir pasa a lo que lo citaba al clon y deja que la clave vieja siga entrando (un archivo de
OPUS que la traiga se lee como el clon). Quien clona es un usuario dado de alta (`api.usuarios`) de uno de los roles que tienen `clonar_insumo`
en `ROL_FUNCION` —Control de obra por omisión—: queda en la clonación con su correo y el rol con que la hizo. Sin `--clonar` no se escribe nada.
"""
from __future__ import annotations

import argparse
import sys
from typing import Optional, Sequence, TextIO

from core.accesos import PermisoDenegado, RepositorioAccesos, normalizar_correo
from core.catalogo import CatalogoCambio, RepositorioCatalogo
from core.clonacion import (
    ClonacionNoProcede,
    ServicioClonacion,
    informe_de_clonacion,
    informe_de_correccion,
    informe_de_resultado,
)


def clonar(
    catalogo: RepositorioCatalogo,
    accesos: RepositorioAccesos,
    *,
    correo: str,
    original: Optional[str] = None,
    clave: Optional[str] = None,
    modo: str = "sustituir",
    prefijo: Optional[str] = None,
    por: Optional[str] = None,
    desde: int = 1,
    clonar_ya: bool = False,
    salida: TextIO = sys.stdout,
    errores: TextIO = sys.stderr,
) -> int:
    """0 si se revisó o se clonó; 1 si no se puede; 2 si quien clona no puede."""
    u = accesos.usuario_por_correo(normalizar_correo(correo))
    if u is None or not u.activo:
        print(f"No se pudo: {correo} no es un usuario dado de alta y activo (python3 -m api.usuarios).", file=errores)
        return 2
    if (original is None) == (prefijo is None):
        print("No se pudo: se clona un insumo (--original y --clave) o se corrige un prefijo (--corregir-prefijo y --por), no las dos cosas.", file=errores)
        return 1
    servicio = ServicioClonacion(catalogo, permisos=accesos.permisos)
    roles = list(u.roles)
    try:
        if original is not None:
            if not clave:
                print("No se pudo: falta --clave, la del clon.", file=errores)
                return 1
            p = servicio.proponer(original, clave, modo, roles, u.correo)
            print(informe_de_clonacion(p), file=salida)
            if not clonar_ya:
                print("\nNo se escribió nada: con --clonar se hace lo que se propuso.", file=salida)
                return 0 if p.aplicable else 1
            _, r = servicio.clonar(original, clave, modo, roles, u.correo)
            print(f"\nClonado: {r.versiones_nuevas} versiones nuevas y {r.renglones_fijados} renglones fijados (clonación {r.carga_id}).", file=salida)
            return 0
        if not por:
            print("No se pudo: falta --por, el prefijo nuevo.", file=errores)
            return 1
        c = servicio.proponer_correccion_de_prefijo(prefijo, por, desde, roles, u.correo)
        print(informe_de_correccion(c), file=salida)
        if not clonar_ya:
            print("\nNo se escribió nada: con --clonar se hace lo que se propuso.", file=salida)
            return 0
        r = servicio.corregir_prefijo(prefijo, por, desde, roles, u.correo)
        print("\n" + informe_de_resultado(r), file=salida)
        return 1 if r.rechazados else 0
    except PermisoDenegado as e:
        print(f"No se pudo: {e}", file=errores)
        return 2
    except (ValueError, ClonacionNoProcede, CatalogoCambio) as e:
        print(f"No se pudo: {e}", file=errores)
        return 1


def main(argv: Optional[Sequence[str]] = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--postgres", required=True, help="cadena de conexión")
    ap.add_argument("--usuario", required=True, help="el correo de quien clona: un usuario dado de alta")
    ap.add_argument("--original", help="la clave del insumo que se clona")
    ap.add_argument("--clave", help="la clave del clon")
    ap.add_argument("--modo", choices=("mantener", "sustituir"), default="sustituir", help="mantener el original vivo, o sustituirlo (por omisión)")
    ap.add_argument("--corregir-prefijo", dest="prefijo", help="el prefijo viejo de varias claves, p. ej. AUX")
    ap.add_argument("--por", help="el prefijo nuevo, p. ej. PRE")
    ap.add_argument("--desde", type=int, default=1, help="el número con que empieza la numeración nueva (por omisión 1; se saltan los ocupados)")
    ap.add_argument("--clonar", action="store_true", help="hace lo que se propone; sin esto, solo se revisa")
    a = ap.parse_args(argv)
    import psycopg

    from infra.postgres_accesos import PostgresAccesos
    from infra.postgres_catalogo import PostgresCatalogo
    from infra.postgres_programa import aplicar_migraciones

    conn = psycopg.connect(a.postgres, autocommit=True)
    aplicar_migraciones(conn)
    return clonar(PostgresCatalogo(conn), PostgresAccesos(conn), correo=a.usuario, original=a.original, clave=a.clave, modo=a.modo,
                  prefijo=a.prefijo, por=a.por, desde=a.desde, clonar_ya=a.clonar)


if __name__ == "__main__":
    sys.exit(main())
