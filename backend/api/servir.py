"""
Levanta la API del programa con los programas reales — para trabajar con la pantalla y para las pruebas de punta a punta.

    python3 -m api.servir                              en memoria: lo que se guarda se pierde al apagar
    python3 -m api.servir --postgres postgresql://…    guarda en Postgres (aplica las migraciones y, si no hay
                                                       programas, importa los que pida --programa)
    python3 -m api.servir --programa "Zafiro Plus" --programa Rubí
    python3 -m api.servir --vacio                      sin programas: se suben desde la pantalla de inicio

La identidad por cabeceras de `app.py` **no se despliega**: esto es para trabajar en una máquina propia, por eso
escucha solo en 127.0.0.1 si no se le dice otra cosa.
"""
from __future__ import annotations

import argparse
from datetime import date
from pathlib import Path
from typing import List, Optional, Tuple

import uvicorn

from core.motor_cpm import Calendario
from core.programa import cargar_programa, filas_desde_csv
from core.servicio_programa import RepositorioPrograma, ServicioPrograma

from .app import crear_app

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


def armar(postgres: Optional[str], nombres: List[str]):
    """La aplicación y la lista de (id, nombre) de los programas que atiende."""
    if postgres is None:
        from core.memoria_programa import MemoriaPrograma

        repo = MemoriaPrograma()
        programas = importar(repo, nombres)
    else:
        import psycopg

        from infra.postgres_programa import PostgresPrograma, aplicar_migraciones

        conn = psycopg.connect(postgres, autocommit=True)
        aplicar_migraciones(conn)
        repo = PostgresPrograma(conn)
        programas = [(r[0], r[1]) for r in conn.execute("SELECT id, nombre FROM programa ORDER BY id")]
        if not programas:
            programas = importar(repo, nombres)
    return crear_app(ServicioPrograma(repo)), programas


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--postgres", help="cadena de conexión; sin ella, en memoria")
    ap.add_argument("--programa", action="append", help="programa del CSV que se importa (varios permitidos)")
    ap.add_argument("--vacio", action="store_true", help="no importar ningún programa al arrancar")
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--puerto", type=int, default=8000)
    a = ap.parse_args()
    app, programas = armar(a.postgres, [] if a.vacio else (a.programa or POR_OMISION))
    print(f"Los programas: http://{a.host}:{a.puerto}/")
    for pid, nombre in programas:
        print(f"{nombre}: http://{a.host}:{a.puerto}/programas/{pid}/gantt")
    uvicorn.run(app, host=a.host, port=a.puerto, log_level="warning")


if __name__ == "__main__":
    main()
