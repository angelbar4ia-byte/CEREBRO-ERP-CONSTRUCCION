"""
Las tablas que el usuario comparte, a salvo — D-479.

Un archivo que se sube a una sesión vive en una carpeta temporal de la máquina y **se pierde con ella**. Lo que el usuario comparte es dato
del proyecto y no se reconstruye: se guarda en el repositorio, tal cual, antes de leerlo.

    1-mundo/opus/                 los archivos de OPUS (presupuesto, análisis de básicos, ingenierías de ALAMO 18)
    1-mundo/fuentes/<tema>/       el resto: almacén, avance, precio real, semilla de cuadrillas, programa
    1-mundo/fuentes/MANIFIESTO.csv   de cada archivo: cómo se subió, cuándo, cuánto pesa y su huella sha256

- **El original no se toca:** se copia byte por byte (la huella lo prueba) y se le quita solo el prefijo con que la plataforma lo renombró.
- **Cada hoja de un libro de Excel también queda como CSV**, para leerla, compararla y probar con ella sin más herramientas que las del
  lenguaje. El CSV trae los valores que la hoja mostraba, no las fórmulas; el original sigue ahí para quien las necesite.
- **El manifiesto es la lista de lo que hay:** `verificar` falla si falta un archivo, si cambió uno (la huella no coincide) o si hay uno que
  el manifiesto no conoce. Lo corre una prueba, así que perder o tocar una tabla compartida rompe el CI.

No lee ninguna base ni sabe de OPUS: es solo guardar y comprobar. La conversión de Excel usa `openpyxl`, que solo hace falta para guardar.
"""
from __future__ import annotations

import csv
import hashlib
import io
import re
import shutil
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple

CARPETAS_VIGILADAS = ("1-mundo/opus", "1-mundo/fuentes")
MANIFIESTO = "1-mundo/fuentes/MANIFIESTO.csv"
COLUMNAS = ("ruta", "subido_como", "subido_el", "bytes", "sha256", "registros", "derivado_de")
# lo de la carpeta vigilada que no es una tabla compartida: el manifiesto mismo y las notas de lectura que se escribieron al recibirlas
NO_SON_TABLAS = (MANIFIESTO,)
NOTAS = "1-mundo/fuentes/notas/"
PREFIJO_DE_LA_PLATAFORMA = re.compile(r"^[0-9a-f]{8}-")

# (patrón del nombre ya limpio, carpeta): el primero que coincide manda
DESTINOS: Tuple[Tuple[str, str], ...] = (
    (r"^INGENIERIA_-_ALAMO_18.*\.csv$", "1-mundo/opus/ingenieria-alamo-18"),
    (r"^(ANALISIS_DE_BASICOS_|CATALOGO_DE_).*\.csv$", "1-mundo/opus"),
    (r".*MOVIMIENTOS_DE_ALMACEN.*", "1-mundo/fuentes/almacen"),
    (r"^grid_AvanceOPEventosOpr.*", "1-mundo/fuentes/avance"),
    (r"^PRECIO_REAL.*", "1-mundo/fuentes/precio-real"),
    (r"^SEMILLA.*", "1-mundo/fuentes/semilla"),
    (r"^PROGRAMA_.*", "1-mundo/fuentes/programa"),
)
OTRAS = "1-mundo/fuentes/otras"


def nombre_limpio(nombre_subido: str) -> str:
    """El nombre con que el usuario lo tenía, sin el prefijo de ocho caracteres hexadecimales con que lo renombra la plataforma."""
    return PREFIJO_DE_LA_PLATAFORMA.sub("", nombre_subido)


def carpeta_de(nombre: str) -> str:
    for patron, carpeta in DESTINOS:
        if re.match(patron, nombre, re.IGNORECASE):
            return carpeta
    return OTRAS


def sha256_de(ruta: Path) -> str:
    h = hashlib.sha256()
    with open(ruta, "rb") as f:
        for bloque in iter(lambda: f.read(1 << 20), b""):
            h.update(bloque)
    return h.hexdigest()


def registros_de_csv(ruta: Path) -> int:
    """Registros del CSV, con el encabezado (una celda con saltos de línea cuenta una vez)."""
    with open(ruta, encoding="utf-8-sig", newline="") as f:
        return sum(1 for _ in csv.reader(f))


@dataclass(frozen=True)
class Fila:
    ruta: str
    subido_como: str
    subido_el: str
    bytes: int
    sha256: str
    registros: Optional[int]  # de un CSV; vacío en un libro de Excel (sus hojas tienen su propio CSV)
    derivado_de: str  # de un CSV sacado de un libro: «ruta del libro :: hoja»


def leer_manifiesto(raiz: Path) -> List[Fila]:
    f = raiz / MANIFIESTO
    if not f.exists():
        return []
    with open(f, encoding="utf-8", newline="") as fh:
        return [Fila(r["ruta"], r["subido_como"], r["subido_el"], int(r["bytes"]), r["sha256"],
                     int(r["registros"]) if r["registros"] else None, r["derivado_de"]) for r in csv.DictReader(fh)]


def escribir_manifiesto(raiz: Path, filas: Iterable[Fila]) -> None:
    f = raiz / MANIFIESTO
    f.parent.mkdir(parents=True, exist_ok=True)
    with open(f, "w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(COLUMNAS)
        for r in sorted(filas, key=lambda r: r.ruta):
            w.writerow([r.ruta, r.subido_como, r.subido_el, r.bytes, r.sha256, "" if r.registros is None else r.registros, r.derivado_de])


def archivos_vigilados(raiz: Path) -> List[str]:
    out = []
    for carpeta in CARPETAS_VIGILADAS:
        base = raiz / carpeta
        if base.exists():
            out += [p.relative_to(raiz).as_posix() for p in base.rglob("*") if p.is_file() and not p.name.startswith(".")]
    return sorted(r for r in out if r not in NO_SON_TABLAS and not r.startswith(NOTAS))


def verificar(raiz: Path) -> List[str]:
    """Lo que no cuadra entre el manifiesto y lo que hay. Vacío si todo está a salvo."""
    problemas: List[str] = []
    filas = leer_manifiesto(raiz)
    if not filas:
        return ["no hay manifiesto de las tablas compartidas"]
    por_ruta: Dict[str, Fila] = {}
    for r in filas:
        if r.ruta in por_ruta:
            problemas.append(f"{r.ruta}: está dos veces en el manifiesto")
        por_ruta[r.ruta] = r
    for r in filas:
        f = raiz / r.ruta
        if not f.is_file():
            problemas.append(f"{r.ruta}: falta (el manifiesto dice que está)")
            continue
        if f.stat().st_size != r.bytes or sha256_de(f) != r.sha256:
            problemas.append(f"{r.ruta}: cambió (no coincide con la huella con que se guardó)")
        elif r.registros is not None and f.suffix.lower() == ".csv" and registros_de_csv(f) != r.registros:
            problemas.append(f"{r.ruta}: tiene {registros_de_csv(f)} registros y el manifiesto dice {r.registros}")
        if r.derivado_de and r.derivado_de.split(" :: ")[0] not in por_ruta:
            problemas.append(f"{r.ruta}: sale de {r.derivado_de.split(' :: ')[0]}, que el manifiesto no tiene")
    for ruta in archivos_vigilados(raiz):
        if ruta not in por_ruta:
            problemas.append(f"{ruta}: está en el repo y el manifiesto no lo conoce")
    return problemas


# --------------------------------------------------------------------------- guardar lo que se sube


def _hojas_a_csv(libro: Path) -> List[Tuple[str, str, int]]:
    """(nombre de la hoja, su CSV como texto, sus registros): los valores que la hoja mostraba, no las fórmulas."""
    import openpyxl

    wb = openpyxl.load_workbook(libro, read_only=True, data_only=True)
    out = []
    for ws in wb.worksheets:
        buf = io.StringIO()
        w = csv.writer(buf, lineterminator="\n")
        n = 0
        for fila in ws.iter_rows(values_only=True):
            w.writerow(["" if v is None else v for v in fila])
            n += 1
        out.append((ws.title, buf.getvalue(), n))
    wb.close()
    return out


def _nombre_de_hoja(hoja: str) -> str:
    return re.sub(r"[^\w\-. ]+", "_", hoja).strip().replace(" ", "_")


@dataclass(frozen=True)
class Guardado:
    nuevos: Tuple[str, ...]  # las rutas que entraron (libros, CSV y hojas)
    ya_estaban: Tuple[str, ...]  # subidas cuyo contenido ya estaba guardado (misma huella)


def guardar_subidas(origen: Path, raiz: Path) -> Guardado:
    """Copia al repo toda tabla de `origen` (con sus subcarpetas) que no esté ya guardada por su huella, la registra en el manifiesto y,
    si es un libro de Excel, guarda cada hoja como CSV. No borra ni reescribe nada de lo guardado."""
    filas = {r.ruta: r for r in leer_manifiesto(raiz)}
    huellas = {r.sha256: r.ruta for r in filas.values()}
    nuevos: List[str] = []
    ya: List[str] = []
    subidas = sorted((p for p in origen.rglob("*") if p.is_file() and p.suffix.lower() in (".csv", ".xlsx", ".xls", ".xlsm", ".tsv")),
                     key=lambda p: (p.stat().st_mtime, p.name))
    for p in subidas:
        huella = sha256_de(p)
        if huella in huellas:
            ya.append(huellas[huella])
            continue
        nombre = nombre_limpio(p.name)
        destino = raiz / carpeta_de(nombre) / nombre
        n = 1
        while destino.exists() and sha256_de(destino) != huella or destino.relative_to(raiz).as_posix() in filas:
            n += 1  # el mismo nombre con otro contenido: otra versión de la misma tabla, en el orden en que se subió
            destino = destino.with_name(f"{Path(nombre).stem}__{n}{Path(nombre).suffix}")
        if not destino.exists():  # si ya estaba (guardado antes de que hubiera manifiesto), solo se registra
            destino.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(p, destino)
        ruta = destino.relative_to(raiz).as_posix()
        subido = datetime.fromtimestamp(p.stat().st_mtime, timezone.utc).strftime("%Y-%m-%d %H:%M")
        es_libro = destino.suffix.lower() in (".xlsx", ".xls", ".xlsm")
        filas[ruta] = Fila(ruta, p.name, subido, destino.stat().st_size, huella, None if es_libro else registros_de_csv(destino), "")
        huellas[huella] = ruta
        nuevos.append(ruta)
        if es_libro:
            hojas = _hojas_a_csv(destino)
            for hoja, texto, registros in hojas:
                if len(hojas) == 1:
                    csv_destino = destino.with_suffix(".csv")
                else:
                    csv_destino = destino.with_suffix("") / f"{_nombre_de_hoja(hoja)}.csv"
                csv_destino.parent.mkdir(parents=True, exist_ok=True)
                csv_destino.write_text(texto, encoding="utf-8", newline="")
                r = csv_destino.relative_to(raiz).as_posix()
                filas[r] = Fila(r, "", subido, csv_destino.stat().st_size, sha256_de(csv_destino), registros, f"{ruta} :: {hoja}")
                nuevos.append(r)
    escribir_manifiesto(raiz, filas.values())
    return Guardado(tuple(nuevos), tuple(ya))
