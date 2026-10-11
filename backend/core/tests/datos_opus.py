"""
Los archivos de OPUS de `1-mundo/opus/` como texto, y cómo «cambiarles» una celda para probar una recarga.

Las pruebas de la carga no inventan datos: parten de los archivos de verdad y le tocan a una fila real lo que la prueba necesita
(un precio, una cantidad, una unidad). Lo demás es tal cual vino.
"""
import csv
import io
from decimal import ROUND_HALF_UP, Decimal
from pathlib import Path
from typing import Callable, List

OPUS = Path(__file__).resolve().parents[3] / "1-mundo" / "opus"
PRESUPUESTO = "CATALOGO_DE_PRESUPUESTO"
CONCEPTOS = "ANALISIS_DE_BASICOS_CONCEPTOS"
COMPUESTOS = "ANALISIS_DE_BASICOS_COMPUESTOS"
_textos = {}


def texto(nombre: str) -> str:
    if nombre not in _textos:
        _textos[nombre] = (OPUS / f"{nombre}.csv").read_text(encoding="utf-8")
    return _textos[nombre]


def editar(contenido: str, cambia: Callable[[List[List[str]]], None]) -> str:
    """Una copia del archivo con lo que `cambia(filas)` le haga a sus filas (la primera es el encabezado)."""
    filas = list(csv.reader(io.StringIO(contenido.lstrip("﻿"), newline="")))
    cambia(filas)
    sal = io.StringIO()
    csv.writer(sal, lineterminator="\n").writerows(filas)
    return sal.getvalue()


def columna(filas: List[List[str]], nombre: str) -> int:
    return [c.strip() for c in filas[0]].index(nombre)


def dinero(x: Decimal) -> str:
    return f"${x.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP):,.2f}"


def _numero(s: str) -> Decimal:
    return Decimal(s.replace("$", "").replace(",", ""))


def reescalar_linea(conceptos: str, padre: str, n: int, factor: Decimal) -> str:
    """La `n`-ésima línea (desde 0) de la matriz de `padre` con su cantidad por `factor`, y su importe al día."""

    def cambia(filas):
        p, c, k, i = (columna(filas, x) for x in ("Clave Padre", "Cantidad", "Costo", "Importe"))
        propias = [f for f in filas[1:] if f[p] == padre]
        f = propias[n]
        cantidad = _numero(f[c]) * factor
        f[c] = f"{cantidad:.6f}"
        f[i] = dinero(cantidad * _numero(f[k]))

    return editar(conceptos, cambia)


def reescalar_costo(conceptos: str, hijo: str, factor: Decimal) -> str:
    """El costo de `hijo` por `factor` en todas las líneas que lo citan, con su importe al día."""

    def cambia(filas):
        h, c, k, i = (columna(filas, x) for x in ("Clave Hijo", "Cantidad", "Costo", "Importe"))
        for f in filas[1:]:
            if f[h] == hijo:
                costo = _numero(f[k]) * factor
                f[k] = dinero(costo)
                f[i] = dinero(_numero(f[c]) * _numero(f[k]))

    return editar(conceptos, cambia)


def cambiar_unidad_del_hijo(conceptos: str, hijo: str, unidad: str) -> str:
    def cambia(filas):
        h, u = columna(filas, "Clave Hijo"), columna(filas, "Unidad")
        for f in filas[1:]:
            if f[h] == hijo:
                f[u] = unidad

    return editar(conceptos, cambia)


def cambiar_unidad_del_concepto(presupuesto: str, clave: str, unidad: str) -> str:
    def cambia(filas):
        k, u = columna(filas, "Clave"), columna(filas, "Unidad")
        for f in filas[1:]:
            if f[k] == clave:
                f[u] = unidad

    return editar(presupuesto, cambia)


def sin_capitulo(presupuesto: str, clave_del_capitulo: str) -> str:
    """El presupuesto sin las filas de un capítulo (todas las que van desde él hasta el siguiente capítulo)."""

    def cambia(filas):
        n, k = columna(filas, "Nivel"), columna(filas, "Clave")
        fuera, dentro = [], False
        for f in filas[1:]:
            if f[n].strip() == "0":
                dentro = f[k] == clave_del_capitulo
            if not dentro:
                fuera.append(f)
        filas[:] = [filas[0]] + fuera

    return editar(presupuesto, cambia)
