"""
Los archivos de OPUS de `1-mundo/opus/` como texto, y cómo «cambiarles» una celda para probar una recarga.

Las pruebas de la carga no inventan datos: parten de los archivos de verdad y le tocan a una fila real lo que la prueba necesita
(un precio, una cantidad, una unidad). Lo demás es tal cual vino.
"""
import csv
import io
from decimal import ROUND_HALF_UP, Decimal
from pathlib import Path
from typing import Callable, List, Optional

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


# ---------------------------------------------------------------------------- editar el presupuesto: lo que cambia entre dos cargas


def _capitulo(filas: List[List[str]], capitulo: str):
    """(columnas, desde, hasta) de las filas de un capítulo: desde el que lleva su clave en el nivel 0 hasta el siguiente nivel 0."""
    n, k = columna(filas, "Nivel"), columna(filas, "Clave")
    desde = next(i for i, f in enumerate(filas) if i and f[n].strip() == "0" and f[k] == capitulo)
    hasta = next((i for i in range(desde + 1, len(filas)) if filas[i][n].strip() == "0"), len(filas))
    return n, k, desde, hasta


def _fila_de(filas: List[List[str]], capitulo: str, clave: str, n: int = 1) -> int:
    """El índice de la `n`-ésima fila con esa clave dentro del capítulo."""
    _, k, desde, hasta = _capitulo(filas, capitulo)
    return [i for i in range(desde, hasta) if filas[i][k] == clave][n - 1]


def _fin_del_subarbol(filas: List[List[str]], i: int, nivel: int) -> int:
    nv = columna(filas, "Nivel")
    j = i + 1
    while j < len(filas) and int(filas[j][nv]) > int(filas[i][nivel]) and filas[j][nv].strip() != "0":
        j += 1
    return j


def _renumerar(filas: List[List[str]]) -> None:
    """El `Indice` es el lugar entre los hermanos (lo comprueba el lector): se vuelve a poner en las filas que no son raíz."""
    nv, ind = columna(filas, "Nivel"), columna(filas, "Indice")
    contador: List[int] = []
    for f in filas[1:]:
        nivel = int(f[nv])
        del contador[nivel + 1:]
        while len(contador) <= nivel:
            contador.append(0)
        contador[nivel] += 1
        if nivel > 0:
            f[ind] = str(contador[nivel])


def con_cantidad(presupuesto: str, capitulo: str, clave: str, cantidad: str, n: int = 1) -> str:
    """La `n`-ésima fila con esa clave del capítulo, con otra cantidad."""
    def cambia(filas):
        filas[_fila_de(filas, capitulo, clave, n)][columna(filas, "Cantidad")] = cantidad

    return editar(presupuesto, cambia)


def sin_renglon(presupuesto: str, capitulo: str, clave: str, n: int = 1) -> str:
    """El capítulo sin la `n`-ésima fila con esa clave —y sin lo que cuelga de ella—, con el `Indice` de los hermanos al día."""
    def cambia(filas):
        i = _fila_de(filas, capitulo, clave, n)
        del filas[i:_fin_del_subarbol(filas, i, columna(filas, "Nivel"))]
        _renumerar(filas)

    return editar(presupuesto, cambia)


def con_copia(presupuesto: str, capitulo: str, origen: str, despues_de: str, *, cantidad: Optional[str] = None, n_origen: int = 1,
              n_despues: int = 1, como_hijo_de_la_misma: bool = False) -> str:
    """Una copia de la fila `origen` (y de lo que cuelga de ella) puesta justo después de `despues_de` y de lo que cuelga de ésta.
    Si `despues_de` es hermana de `origen`, la copia queda en el mismo bloque; si no, en el bloque de `despues_de`."""
    def cambia(filas):
        o = _fila_de(filas, capitulo, origen, n_origen)
        nivel_columna = columna(filas, "Nivel")
        copia = [list(f) for f in filas[o:_fin_del_subarbol(filas, o, nivel_columna)]]
        if cantidad is not None:
            copia[0][columna(filas, "Cantidad")] = cantidad
        d = _fila_de(filas, capitulo, despues_de, n_despues)
        # la copia se ajusta al nivel de la fila después de la que va
        ajuste = int(filas[d][nivel_columna]) - int(copia[0][nivel_columna])
        for f in copia:
            f[nivel_columna] = str(int(f[nivel_columna]) + ajuste)
        filas[_fin_del_subarbol(filas, d, nivel_columna):_fin_del_subarbol(filas, d, nivel_columna)] = copia
        _renumerar(filas)

    return editar(presupuesto, cambia)


def con_otra_clave(presupuesto: str, capitulo: str, clave: str, nueva: str, n: int = 1, *, unidad: Optional[str] = None) -> str:
    """La `n`-ésima fila con esa clave del capítulo, con otra clave (y otra unidad, si se dice; el texto se queda como estaba)."""
    def cambia(filas):
        i = _fila_de(filas, capitulo, clave, n)
        filas[i][columna(filas, "Clave")] = nueva
        if unidad is not None:
            filas[i][columna(filas, "Unidad")] = unidad

    return editar(presupuesto, cambia)


def con_orden_cambiado(presupuesto: str, capitulo: str, primera: str, segunda: str, n_primera: int = 1, n_segunda: int = 1) -> str:
    """Dos hermanos seguidos (sin nada que cuelgue de ellos) con su lugar cambiado."""
    def cambia(filas):
        a, b = _fila_de(filas, capitulo, primera, n_primera), _fila_de(filas, capitulo, segunda, n_segunda)
        filas[a], filas[b] = filas[b], filas[a]
        _renumerar(filas)

    return editar(presupuesto, cambia)


def con_descripcion_del_concepto(presupuesto: str, clave: str, cambia: Callable[[str], str]) -> str:
    """La descripción de un concepto del presupuesto, en todas las filas que lo nombran, con lo que `cambia` le haga."""
    def edita(filas):
        k, t, d = columna(filas, "Clave"), columna(filas, "Tipo"), columna(filas, "Descripción")
        for f in filas[1:]:
            if f[k] == clave and f[t] == "Concepto":
                f[d] = cambia(f[d])

    return editar(presupuesto, edita)


def con_descripcion_del_hijo(conceptos: str, hijo: str, cambia: Callable[[str], str]) -> str:
    """La descripción de un insumo o un compuesto, en todas las líneas de matriz que lo citan."""
    def edita(filas):
        h, d = columna(filas, "Clave Hijo"), columna(filas, "Descripción")
        for f in filas[1:]:
            if f[h] == hijo:
                f[d] = cambia(f[d])

    return editar(conceptos, edita)
