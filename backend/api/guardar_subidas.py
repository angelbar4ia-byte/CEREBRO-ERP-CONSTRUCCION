"""
Guardar en el repositorio las tablas que el usuario sube a una sesión — D-479.

    # guarda lo que haya en la carpeta de subidas de la sesión y no esté ya guardado (por su huella); no borra ni reescribe nada
    python3 -m api.guardar_subidas

    # de otra carpeta
    python3 -m api.guardar_subidas --origen /ruta/a/las/tablas

    # comprueba que todo lo guardado sigue ahí, sin cambios, y que no hay nada que el manifiesto no conozca
    python3 -m api.guardar_subidas --verificar

Los archivos que se suben a una sesión viven en una carpeta temporal y se pierden con ella (`METODO.md` §2.6): esto se corre al recibir una
tabla, antes de leerla. Un libro de Excel queda tal cual y cada una de sus hojas, como CSV; todo en `1-mundo/fuentes/` (lo de OPUS, en
`1-mundo/opus/`), con su huella en `1-mundo/fuentes/MANIFIESTO.csv`. Después hay que hacer commit y push: lo guardado en la máquina
tampoco sobrevive a ella.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Optional, Sequence, TextIO

from core.fuentes import guardar_subidas, verificar

RAIZ = Path(__file__).resolve().parents[2]
SUBIDAS = Path.home() / ".claude" / "uploads"


def correr(origen: Path, raiz: Path, solo_verificar: bool, salida: TextIO = sys.stdout, errores: TextIO = sys.stderr) -> int:
    """0 si todo quedó a salvo; 1 si algo no cuadra."""
    if solo_verificar:
        problemas = verificar(raiz)
        for p in problemas:
            print(p, file=errores)
        print("Todo lo compartido sigue ahí, sin cambios." if not problemas else f"{len(problemas)} problemas.", file=salida)
        return 1 if problemas else 0
    if not origen.exists():
        print(f"No hay carpeta de subidas en {origen}.", file=errores)
        return 1
    g = guardar_subidas(origen, raiz)
    for r in g.nuevos:
        print(f"  guardado  {r}", file=salida)
    print(f"{len(g.nuevos)} archivos nuevos · {len(g.ya_estaban)} subidas que ya estaban guardadas.", file=salida)
    problemas = verificar(raiz)
    for p in problemas:
        print(p, file=errores)
    return 1 if problemas else 0


def main(argv: Optional[Sequence[str]] = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--origen", type=Path, default=SUBIDAS, help=f"la carpeta con las subidas (por omisión {SUBIDAS})")
    ap.add_argument("--raiz", type=Path, default=RAIZ, help="la raíz del repositorio")
    ap.add_argument("--verificar", action="store_true", help="solo comprueba que lo guardado está completo y sin cambios")
    a = ap.parse_args(argv)
    return correr(a.origen, a.raiz, a.verificar)


if __name__ == "__main__":
    sys.exit(main())
