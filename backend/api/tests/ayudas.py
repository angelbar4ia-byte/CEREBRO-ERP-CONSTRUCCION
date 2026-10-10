"""Lo que comparten las pruebas de la API: un archivo de programa armado con las filas reales del repositorio."""
import csv
import io

from core.tests.contrato_programa import CSV

NO_HABILES = ["2025-12-25", "2026-01-01"]


def csv_de(prototipo=None, delimitador=",", bom=False, cambia=None):
    """Un archivo de programa armado con las filas reales del CSV del repositorio: las de un prototipo, o las siete.
    `cambia(fila)` deja tocar una fila (un diccionario) antes de escribirla."""
    with open(CSV, encoding="utf-8", newline="") as fh:
        lector = csv.DictReader(fh)
        filas = [dict(r) for r in lector if prototipo is None or r["prototipo"] == prototipo]
        columnas = lector.fieldnames
    if cambia:
        for r in filas:
            cambia(r)
    sal = io.StringIO()
    w = csv.DictWriter(sal, fieldnames=columnas, delimiter=delimitador)
    w.writeheader()
    w.writerows(filas)
    return ("\ufeff" if bom else "") + sal.getvalue()
