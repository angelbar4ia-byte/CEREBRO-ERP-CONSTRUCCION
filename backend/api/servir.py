"""
Levanta la API del programa — para trabajar con la pantalla y para las pruebas de punta a punta.

    # con token (lo que se despliega): la API verifica los tokens del proveedor de identidad y no emite ninguno
    python3 -m api.servir --postgres postgresql://… --jwt-secreto "$PROGRAMA_JWT_SECRETO" --login-url https://…/entrar
    python3 -m api.servir --postgres postgresql://… --jwks https://…/.well-known/jwks.json --jwt-audiencia programa

    # para trabajar en una máquina propia, sin proveedor: se elige el rol en la pantalla y cualquiera puede ser Control de obra
    python3 -m api.servir --inseguro-cabeceras
    python3 -m api.servir --inseguro-cabeceras --programa "Zafiro Plus" --programa Rubí    (importa esos al arrancar)
    python3 -m api.servir --inseguro-cabeceras --vacio                                     (sin programas: se suben desde `/`)

Los usuarios se dan de alta con `--usuario correo|Nombre|rol,rol` (repetible) o, en Postgres, con `python3 -m api.usuarios`.
Sin `--postgres` todo vive en memoria y se pierde al apagar. Escucha solo en 127.0.0.1 si no se le dice otra cosa.
"""
from __future__ import annotations

import argparse
import os
import sys
from datetime import date
from pathlib import Path
from typing import List, Optional, Tuple

import uvicorn

from core.accesos import MemoriaAccesos, RepositorioAccesos
from core.motor_cpm import Calendario
from core.programa import cargar_programa, filas_desde_csv
from core.servicio_programa import RepositorioPrograma, ServicioPrograma

from .app import crear_app
from .autenticacion import VerificadorJWT, por_cabeceras, por_token

RAIZ = Path(__file__).resolve().parents[2]
CSV = RAIZ / "1-mundo" / "programas" / "PROGRAMAS-PROTOTIPOS.csv"
# el calendario con que se construyeron los siete programas (`PROGRAMA-CPM.md` §2): sin sábados ni domingos y sin 25-dic ni 1-ene
CALENDARIO = Calendario(no_habiles=frozenset({date(2025, 12, 25), date(2026, 1, 1)}))
POR_OMISION = ["Zafiro Plus"]


def importar(repo: RepositorioPrograma, nombres: List[str]) -> List[Tuple[int, str]]:
    ids = []
    for n in nombres:
        ids.append((repo.importar_programa(n, cargar_programa(filas_desde_csv(CSV, n), CALENDARIO), CALENDARIO), n))
    return ids


def dar_de_alta(accesos: RepositorioAccesos, usuarios: List[str]) -> None:
    """`correo|Nombre|rol,rol`: los que ya existen se dejan como están."""
    for u in usuarios:
        partes = u.split("|")
        if len(partes) != 3:
            raise SystemExit(f"«{u}» no es correo|Nombre|rol,rol")
        correo, nombre, roles = partes
        if accesos.usuario_por_correo(correo) is None:
            accesos.agregar_usuario(nombre, correo, [r for r in roles.split(",") if r])


def adaptadores_postgres(cadena: str):
    """Los cuatro adaptadores de Postgres, sobre una conexión por hilo (`infra/conexion.py`, D-482): el servidor atiende cada petición en un
    hilo, y una sola conexión compartida mezcla las transacciones de dos peticiones que se traslapan. Aplica las migraciones al empezar."""
    import psycopg

    from infra.conexion import ConexionPorHilo
    from infra.postgres_accesos import PostgresAccesos
    from infra.postgres_bandeja import PostgresBandeja
    from infra.postgres_catalogo import PostgresCatalogo
    from infra.postgres_programa import PostgresPrograma, aplicar_migraciones

    with psycopg.connect(cadena, autocommit=True) as conn:
        aplicar_migraciones(conn)
    conexion = ConexionPorHilo(cadena)
    return PostgresPrograma(conexion), PostgresAccesos(conexion), PostgresCatalogo(conexion), PostgresBandeja(conexion)


def armar(
    postgres: Optional[str],
    nombres: List[str],
    usuarios: Optional[List[str]] = None,
    verificador: Optional[VerificadorJWT] = None,
    login_url: Optional[str] = None,
):
    """La aplicación y la lista de (id, nombre) de los programas que atiende. Sin `verificador`, identidad por cabeceras
    (lo inseguro, que quien llama pidió a propósito)."""
    if postgres is None:
        from core.memoria_bandeja import MemoriaBandeja
        from core.memoria_catalogo import MemoriaCatalogo
        from core.memoria_programa import MemoriaPrograma

        repo, accesos, catalogo, bandeja = MemoriaPrograma(), MemoriaAccesos(), MemoriaCatalogo(), MemoriaBandeja()
        programas = importar(repo, nombres)
    else:
        repo, accesos, catalogo, bandeja = adaptadores_postgres(postgres)
        programas = [(r[0], r[1]) for r in repo.conn.execute("SELECT id, nombre FROM programa ORDER BY id")]
        if not programas:
            programas = importar(repo, nombres)
    dar_de_alta(accesos, usuarios or [])
    autenticar = por_token(verificador, accesos, login_url) if verificador is not None else por_cabeceras()
    return crear_app(ServicioPrograma(repo, permisos=accesos.permisos), autenticar, catalogo, bandeja), programas


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--postgres", help="cadena de conexión; sin ella, en memoria")
    ap.add_argument("--programa", action="append", help="programa del CSV que se importa al arrancar si la base está vacía (varios permitidos)")
    ap.add_argument("--vacio", action="store_true", help="no importar ningún programa al arrancar")
    ap.add_argument("--usuario", action="append", default=[], help="correo|Nombre|rol,rol: se da de alta si no existe (varios permitidos)")
    ap.add_argument("--inseguro-cabeceras", action="store_true",
                    help="identidad por X-Rol y X-Usuario: cualquiera puede decir que es Control de obra. Solo para trabajar y probar")
    ap.add_argument("--jwt-secreto", default=os.environ.get("PROGRAMA_JWT_SECRETO"), help="el secreto compartido (HS256); también en PROGRAMA_JWT_SECRETO")
    ap.add_argument("--jwks", help="dirección de las llaves públicas del proveedor (RS256, ES256)")
    ap.add_argument("--jwt-audiencia", help="si se da, el token debe traerla")
    ap.add_argument("--jwt-emisor", help="si se da, el token debe venir de ahí")
    ap.add_argument("--jwt-reclamo-correo", default="email", help="el reclamo del token que trae el correo (por omisión «email»)")
    ap.add_argument("--login-url", help="a dónde se manda a quien no ha iniciado sesión")
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--puerto", type=int, default=8000)
    a = ap.parse_args()

    verificador = None
    if a.inseguro_cabeceras:
        print("AVISO: identidad por cabeceras. Cualquiera puede decir que es Control de obra: no se despliega así.", file=sys.stderr)
    elif a.jwt_secreto or a.jwks:
        verificador = VerificadorJWT(secreto=a.jwt_secreto, jwks=a.jwks, audiencia=a.jwt_audiencia, emisor=a.jwt_emisor, reclamo_correo=a.jwt_reclamo_correo)
    else:
        raise SystemExit("Falta decir cómo se sabe quién llama: --jwt-secreto o --jwks (lo que se despliega), o --inseguro-cabeceras (solo para trabajar).")
    app, programas = armar(a.postgres, [] if a.vacio else (a.programa or POR_OMISION), usuarios=a.usuario, verificador=verificador, login_url=a.login_url)
    print(f"Los programas: http://{a.host}:{a.puerto}/")
    for pid, nombre in programas:
        print(f"{nombre}: http://{a.host}:{a.puerto}/programas/{pid}/gantt")
    uvicorn.run(app, host=a.host, port=a.puerto, log_level="warning")


if __name__ == "__main__":
    main()
