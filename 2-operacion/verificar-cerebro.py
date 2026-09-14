#!/usr/bin/env python3
"""
verificar-cerebro.py — comprueba que el cerebro siga cuadrando consigo mismo.

No corrige nada. Reporta, con archivo y línea.
La detección nunca necesita permiso; la corrección siempre.

Uso:  python3 2-operacion/verificar-cerebro.py [ruta-al-cerebro]
Sale con código 1 si hay fallas.
"""
import re
import sys
import datetime
from pathlib import Path

RAIZ = Path(sys.argv[1] if len(sys.argv) > 1 else Path(__file__).resolve().parent.parent)
HOY = datetime.date.today()

fallas, avisos = [], []


def falla(archivo, msg):
    fallas.append((archivo, msg))


def aviso(archivo, msg):
    avisos.append((archivo, msg))


def archivos():
    return sorted(p for p in RAIZ.rglob("*.md"))


def rel(p):
    return str(p.relative_to(RAIZ))


# ─────────────────────────────────────────────────────────────
# 1 · Bloque de órgano
# ─────────────────────────────────────────────────────────────
CAMPOS = ["órgano", "capa", "pregunta", "corte"]
CAPAS = {"I — Mundo", "II — Operación", "III — Historia", "IV — Dirección", "—"}


def check_organo(p, texto):
    bloques = re.findall(r"```\n(órgano:.*?)```", texto, re.S)
    if not bloques:
        falla(rel(p), "sin bloque de órgano")
        return
    campos = dict(
        re.findall(r"^(\S+?):\s+(.*?)$", bloques[0], re.M)
    )
    for c in CAMPOS:
        if c not in campos:
            falla(rel(p), f"al bloque de órgano le falta «{c}:»")

    capa = campos.get("capa", "")
    if capa and capa not in CAPAS:
        falla(rel(p), f"capa desconocida: «{capa}»")

    # la carpeta debe coincidir con la capa declarada
    carpeta = p.relative_to(RAIZ).parts[0] if len(p.relative_to(RAIZ).parts) > 1 else None
    esperada = {"1-mundo": "I", "2-operacion": "II", "3-historia": "III", "4-direccion": "IV"}
    if carpeta in esperada and capa and not capa.startswith(esperada[carpeta]):
        falla(rel(p), f"vive en {carpeta}/ pero declara capa «{capa}»")

    corte = campos.get("corte", "")
    if re.fullmatch(r"\d{4}-\d{2}-\d{2}", corte or ""):
        f = datetime.date.fromisoformat(corte)
        if f > HOY:
            falla(rel(p), f"corte en el futuro: {corte}")
        elif (HOY - f).days > 90:
            aviso(rel(p), f"corte de hace {(HOY - f).days} días — ¿sigue vigente?")
    elif corte:
        falla(rel(p), f"corte con formato inválido: «{corte}»")


# ─────────────────────────────────────────────────────────────
# 2 · Referencias a archivos que existan
# ─────────────────────────────────────────────────────────────
RETIRADOS = {
    "ANALISIS-CATALOGOS-BASE.md", "ANALISIS-MATRIZ-Y-ARBOL.md",
    "DICCIONARIO-CONCEPTOS.md", "ERP-CONSTRUCCION-PLAN.md",
    "REDISEÑO.md", "PROPUESTAS.md",
}


def check_refs_archivo(p, texto, existentes):
    for n, linea in enumerate(texto.split("\n"), 1):
        for ref in re.findall(r"`([A-Za-zÑÁÉÍÓÚñáéíóú0-9_.\-]+\.md)`", linea):
            if ref in RETIRADOS:
                continue
            if ref not in existentes:
                falla(rel(p), f"línea {n}: referencia a `{ref}`, que no existe")


# ─────────────────────────────────────────────────────────────
# 3 · Referencias §N a secciones que existan
# ─────────────────────────────────────────────────────────────
def secciones(texto):
    """Números de sección declarados como encabezado: '# 13.' o '## 13.2'."""
    return set(re.findall(r"^#{1,3}\s+(\d+(?:\.\d+)?)\.?\s", texto, re.M))


def check_refs_internas(p, texto, propias):
    """Referencias §N sin archivo: tienen que existir en el propio archivo.

    Prepara la división de archivos grandes: al partir uno, las referencias
    internas que quedan apuntando a otro lado saltan aquí.
    """
    if not propias:
        return
    for n, linea in enumerate(texto.split("\n"), 1):
        # descarta las que ya traen archivo: «`X.md` §N»
        # quita sólo lo ya calificado: un nombre de archivo del cerebro
        # —con o sin .md, con o sin backticks— seguido de una o varias §
        limpia = re.sub(
            r"`?(?:[A-ZÑ][A-ZÑ0-9_\-]{2,}|[a-z0-9_\-]+\.md)(?:\.md)?`?[^\n]{0,4}?"
            r"§\d+(?:\.\d+)?(?:\s*[·,]\s*§\d+(?:\.\d+)?)*",
            "", linea)
        for sec in re.findall(r"§(\d+(?:\.\d+)?)", limpia):
            if sec not in propias and sec.split(".")[0] not in propias:
                falla(rel(p), f"línea {n}: §{sec} no existe en este archivo")


def check_refs_seccion(p, texto, indice_secciones):
    # «`ARCHIVO.md` §N» — referencia cruzada explícita
    for n, linea in enumerate(texto.split("\n"), 1):
        for arch, sec in re.findall(r"`([A-Za-zÑ0-9_.\-]+\.md)`[^\n]{0,12}?§(\d+(?:\.\d+)?)", linea):
            if arch in RETIRADOS or arch not in indice_secciones:
                continue
            secs = indice_secciones[arch]
            if sec not in secs and sec.split(".")[0] not in secs:
                falla(rel(p), f"línea {n}: apunta a `{arch}` §{sec}, que no existe ahí")


# ─────────────────────────────────────────────────────────────
# 4 · Conteos declarados contra conteos reales
# ─────────────────────────────────────────────────────────────
def check_conteos(textos):
    mem = textos.get("MEMORIA.md", "")
    reales = len(re.findall(r"^\| D-\d+ \|", mem, re.M))
    if reales:
        for arch, t in textos.items():
            for n, linea in enumerate(t.split("\n"), 1):
                # sólo cuenta si la línea habla de MEMORIA: «las 16 decisiones
                # de los cuatro módulos» es otra cosa y no debe disparar
                if "MEMORIA" not in linea.upper() and "decisiones ·" not in linea:
                    continue
                # un número citado entre « » es narración de un caso, no afirmación
                sin_citas = re.sub(r"«[^»]*»", "", linea)
                m = re.search(r"(\d+)\s+decisiones", sin_citas)
                if m and int(m.group(1)) != reales:
                    falla(arch, f"línea {n}: declara {m.group(1)} decisiones; en MEMORIA hay {reales}")

    glo = textos.get("GLOSARIO-DOMINIO.md", "")
    if glo:
        # los términos son encabezados de tercer nivel sin numerar
        terminos = len([h for h in re.findall(r"^### (.+)$", glo, re.M)
                        if not h.startswith("«")])
        for arch, t in textos.items():
            for n, linea in enumerate(t.split("\n"), 1):
                # sólo declaraciones —bloque de órgano o tabla de estado—,
                # no la narración de un error histórico
                if not (linea.startswith("verificado:") or linea.startswith("|")):
                    continue
                m = re.search(r"(\d+)\s+términos", linea)
                if m and abs(int(m.group(1)) - terminos) > 2:
                    aviso(arch, f"línea {n}: declara {m.group(1)} términos; conté {terminos} encabezados")


# ─────────────────────────────────────────────────────────────
# 5 · Las cifras de control siguen en su fuente
# ─────────────────────────────────────────────────────────────
CIFRAS = {
    "$16,460,623.50": "CATALOGOS.md",
    "$1,842,426.01": "CATALOGOS.md",
    "665": "CATALOGOS.md",
    "84%": "CONOCIMIENTO.md",
    "1.085": "CONOCIMIENTO.md",
}


def check_cifras(textos):
    inv = textos.get("INVARIANTES.md", "")
    if not inv:
        falla("INVARIANTES.md", "no existe: el cerebro no tiene contra qué comprobarse")
        return
    for cifra, fuente in CIFRAS.items():
        if cifra not in inv:
            aviso("INVARIANTES.md", f"ya no menciona la cifra {cifra}")
        elif cifra not in textos.get(fuente, ""):
            falla("INVARIANTES.md", f"la cifra {cifra} ya no está en su fuente {fuente}")


# ─────────────────────────────────────────────────────────────
# 6 · Un hecho, un archivo — señales de duplicación
# ─────────────────────────────────────────────────────────────
def check_duplicacion(textos):
    """Párrafos largos idénticos en dos archivos distintos.

    Los archivos compilados quedan fuera: repetir su fuente es lo que significa
    compilar, y no divergen porque se regeneran. Se reconocen por el campo
    `compilado:` de su bloque de órgano.
    """
    vistos = {}
    for arch, t in textos.items():
        if re.search(r"^compilado:", t, re.M):
            continue
        for parrafo in t.split("\n\n"):
            limpio = " ".join(parrafo.split())
            if len(limpio) < 180 or limpio.startswith("|"):
                continue
            if limpio in vistos and vistos[limpio] != arch:
                falla(arch, f"párrafo idéntico al de {vistos[limpio]}: «{limpio[:60]}…»")
            vistos[limpio] = arch


# ─────────────────────────────────────────────────────────────
# 7 · Tablas bien formadas
# ─────────────────────────────────────────────────────────────
def check_tablas(p, texto):
    """Una fila con menos columnas que su encabezado se corta al renderizar."""
    L = texto.split("\n")
    for i, l in enumerate(L):
        if not re.match(r"^\|[-: |]+\|$", l) or i == 0:
            continue
        n = l.count("|") - 1
        if L[i - 1].startswith("|") and L[i - 1].count("|") - 1 != n:
            falla(rel(p), f"línea {i}: encabezado de {L[i-1].count('|')-1} columnas, separador de {n}")
        for j in range(i + 1, len(L)):
            if not L[j].startswith("|"):
                break
            if L[j].count("|") - 1 != n:
                falla(rel(p), f"línea {j+1}: fila de {L[j].count('|')-1} columnas en tabla de {n}")


# ─────────────────────────────────────────────────────────────
# 8 · La misma cifra de control, dos valores distintos
# ─────────────────────────────────────────────────────────────
CONTROL = {
    "términos del glosario": r"(\d+) términos",
    "decisiones registradas": r"(\d+) decisiones · \d+ descartes",
    "conceptos que cuadran": r"(\d+) conceptos.{0,30}cuadran",
}
NUM = {"once": "11", "doce": "12"}


def check_contradicciones(textos):
    """Comprueba que cada cifra de control tenga un solo valor en todo el cerebro."""
    for nombre, pat in CONTROL.items():
        vistos = {}
        for arch, t in textos.items():
            for n, linea in enumerate(t.split("\n"), 1):
                # la narración de un error pasado no cuenta como afirmación
                if any(w in linea for w in ("decía", "declaraba", "se leía")):
                    continue
                for m in re.findall(pat, linea):
                    v = NUM.get(m.lower(), m)
                    vistos.setdefault(v, []).append(f"{arch}:{n}")
        if len(vistos) > 1:
            detalle = " · ".join(f"{v} ({d[0]})" for v, d in sorted(vistos.items()))
            falla("(cerebro)", f"«{nombre}» se afirma con valores distintos: {detalle}")


# ─────────────────────────────────────────────────────────────
def main():
    paths = archivos()
    if not paths:
        print(f"No hay archivos .md en {RAIZ}")
        return 1

    textos = {p.name: p.read_text() for p in paths}
    existentes = set(textos)
    indice_secciones = {n: secciones(t) for n, t in textos.items()}

    for p in paths:
        t = textos[p.name]
        # INDICE enruta y README es la puerta del repo: ninguno es archivo de capa
        if p.name not in ("INDICE.md", "README.md"):
            check_organo(p, t)
        check_refs_archivo(p, t, existentes)
        check_refs_seccion(p, t, indice_secciones)
        check_refs_internas(p, t, indice_secciones[p.name])
        check_tablas(p, t)

    check_conteos(textos)
    check_cifras(textos)
    check_contradicciones(textos)
    check_duplicacion(textos)

    print(f"Cerebro: {len(paths)} archivos · {RAIZ}\n")
    if fallas:
        print(f"FALLAS ({len(fallas)})")
        for a, m in fallas:
            print(f"  ✗ {a}: {m}")
        print()
    if avisos:
        print(f"AVISOS ({len(avisos)})")
        for a, m in avisos:
            print(f"  · {a}: {m}")
        print()
    if not fallas and not avisos:
        print("Todo cuadra.")
    return 1 if fallas else 0


if __name__ == "__main__":
    sys.exit(main())
