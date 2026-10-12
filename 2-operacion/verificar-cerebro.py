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

fallas, avisos, notas = [], [], []


def falla(archivo, msg):
    fallas.append((archivo, msg))


def aviso(archivo, msg):
    avisos.append((archivo, msg))


def nota(msg):
    notas.append(msg)


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
# 2 · Referencias a archivos que existan (y los retirados, solo donde se cuenta que se retiraron)
# ─────────────────────────────────────────────────────────────
RETIRADOS = {
    "ANALISIS-CATALOGOS-BASE.md", "ANALISIS-MATRIZ-Y-ARBOL.md",
    "DICCIONARIO-CONCEPTOS.md", "ERP-CONSTRUCCION-PLAN.md",
    "REDISEÑO.md", "PROPUESTAS.md",
}
# Los cuatro primeros fueron archivos de verdad y no tienen copia en el repo ni en su historia (B-30, D-490): el cerebro no se
# apoya en ellos. Solo se nombran donde se cuenta que se retiraron. Los dos últimos nunca fueron archivos: son secciones.
SIN_COPIA = RETIRADOS - {"REDISEÑO.md", "PROPUESTAS.md"}
DONDE_SE_NOMBRAN = {"INDICE.md", "3-historia/MEMORIA.md", "4-direccion/PENDIENTES-MEJORAS.md"}


def check_refs_archivo(p, texto, existentes):
    for n, linea in enumerate(texto.split("\n"), 1):
        for ref in re.findall(r"`([A-Za-zÑÁÉÍÓÚñáéíóú0-9_.\-]+\.md)`", linea):
            if ref in RETIRADOS:
                if ref in SIN_COPIA and rel(p) not in DONDE_SE_NOMBRAN:
                    falla(rel(p), f"línea {n}: se apoya en `{ref}`, un archivo retirado sin copia; "
                                  f"solo se nombra en {', '.join(sorted(DONDE_SE_NOMBRAN))}")
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

    # lo que se declara en más de un archivo y tiene una fuente que se puede contar (D-487: el índice decía 6 hallazgos, los
    # pendientes 13 y el encabezado 15, y la tabla de MODELO traía 12; CONOCIMIENTO tenía 17 partes y dos archivos decían 15)
    def declaraciones(patron, real, fuente, que):
        for arch, t in textos.items():
            for n, linea in enumerate(t.split("\n"), 1):
                if not (linea.startswith("verificado:") or linea.startswith("|")):
                    continue
                m = re.search(patron, linea)
                if m and int(m.group(1)) != real:
                    falla(arch, f"línea {n}: declara {m.group(1)} {que}; {fuente} trae {real}")

    mod = textos.get("MODELO.md", "")
    if "# Resumen de hallazgos" in mod:
        filas = [int(x) for x in re.findall(r"^\| (\d+) \|", mod.split("# Resumen de hallazgos", 1)[1], re.M)]
        if filas:
            declaraciones(r"(\d+)\s+hallazgos\s+resueltos", max(filas), "la tabla de hallazgos de MODELO.md", "hallazgos resueltos")
    con = textos.get("CONOCIMIENTO.md", "")
    partes = len(re.findall(r"^# \d+\. ", con, re.M))
    if partes:
        declaraciones(r"(\d+)\s+partes", partes, "CONOCIMIENTO.md", "partes")

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


def check_migraciones(textos):
    """Lo que el cerebro dice de las migraciones (cuántas, cuáles) contra la carpeta (D-491: dos agentes decían 0009 y había 0010)."""
    carpeta = RAIZ / "database" / "migraciones"
    reales = sorted(p.name for p in carpeta.glob("*.sql")) if carpeta.is_dir() else []
    if not reales:
        return
    ultima = max(int(n[:4]) for n in reales)
    for arch, t in textos.items():
        for n, linea in enumerate(t.split("\n"), 1):
            for m in re.finditer(r"0001`?\s*(?:…|\.\.\.|a)\s*`?(\d{4})", linea):
                # las filas de MEMORIA cuentan lo que era cierto el día de cada decisión
                if arch != "MEMORIA.md" and int(m.group(1)) != ultima:
                    falla(arch, f"línea {n}: dice que las migraciones llegan a {m.group(1)}; llegan a {ultima:04d}")
            for nombre in re.findall(r"\b(\d{4}_[a-z0-9_]+\.sql)\b", linea):
                if nombre not in reales:
                    falla(arch, f"línea {n}: nombra la migración {nombre}, que no existe")
    en_indice = set(re.findall(r"\b(\d{4}_[a-z0-9_]+\.sql)\b", textos.get("INDICE.md", "")))
    for nombre in reales:
        if en_indice and nombre not in en_indice:
            falla("INDICE.md", f"no lista la migración {nombre}")


SIMBOLOS_DE_ETAPA = {"✅": "pasan", "⚠": "con matices", "🔶": "diseñadas", "⛔": "sin poder probarse"}


def check_tallas(textos):
    """El recuento de cada prueba de flujo contra los símbolos de su tabla, y la suma de las tres contra lo que dicen ESTADO y PENDIENTES
    (D-489 movió una etapa de ⚠️ a ✅ y hubo que cambiar el número en cinco sitios a mano)."""
    suma = dict.fromkeys(SIMBOLOS_DE_ETAPA.values(), 0)
    suma["etapas"] = 0
    for arch, t in textos.items():
        if not arch.startswith("PRUEBA-"):
            continue
        cuenta = dict.fromkeys(SIMBOLOS_DE_ETAPA.values(), 0)
        for fila in re.findall(r"^\| \d+ \| [^|]+ \| (\S+)", t, re.M):
            for simbolo, nombre in SIMBOLOS_DE_ETAPA.items():
                if fila.startswith(simbolo):
                    cuenta[nombre] += 1
        linea = re.search(r"^verificado:.*$", t, re.M)
        if not linea or not sum(cuenta.values()):
            continue
        dice = {"pasan": r"(\d+) pasan", "con matices": r"(\d+) con matices", "diseñadas": r"(\d+) diseñadas?", "sin poder probarse": r"(\d+) sin poder probarse"}
        for nombre, patron in dice.items():
            m = re.search(patron, linea.group(0))
            if int(m.group(1) if m else 0) != cuenta[nombre]:
                falla(arch, f"el encabezado dice {m.group(1) if m else 0} «{nombre}» y la tabla de etapas trae {cuenta[nombre]}")
        for nombre, n in cuenta.items():
            suma[nombre] += n
        suma["etapas"] += sum(cuenta.values())
    if not suma["etapas"]:
        return
    esperado = (f"{suma['etapas']} etapas — {suma['pasan']} pasan, {suma['con matices']} con matices, {suma['diseñadas']} diseñadas sin caso real que las ejerciten, "
                f"{suma['sin poder probarse']} sin poder probarse")
    for arch in ("ESTADO.md", "PENDIENTES-MEJORAS.md"):
        for n, linea in enumerate(textos.get(arch, "").split("\n"), 1):
            m = re.search(r"\d+ etapas — \d+ pasan, \d+ con matices, \d+ diseñadas sin caso real que las ejerciten, \d+ sin poder probarse", linea)
            if m and m.group(0) != esperado:
                falla(arch, f"línea {n}: dice «{m.group(0)}»; las tres pruebas de flujo suman «{esperado}»")


LIMITE_DE_FILA = 2500  # caracteres; el espacio de trabajo es de capacidad limitada (D-491)


def check_capacidad(textos):
    """ESTADO.md e INDICE.md se leen primero y por todos: una fila de tabla no puede ser una cronología. La cronología es de MEMORIA.md.
    (D-491: una sola celda de ESTADO.md llegó a 35,438 caracteres, de D-383 a D-489.)"""
    for arch in ("ESTADO.md", "INDICE.md"):
        for n, linea in enumerate(textos.get(arch, "").split("\n"), 1):
            if linea.startswith("|") and len(linea) > LIMITE_DE_FILA:
                falla(arch, f"línea {n}: una fila de {len(linea):,} caracteres (el límite es {LIMITE_DE_FILA:,}); el qué pasó va a MEMORIA.md y aquí queda cómo está hoy")


def check_cortes_contra_git():
    """Cuántos archivos cambiaron después de su `corte`. Es una nota y no un aviso: el corte se mueve cuando se verifica el archivo,
    no en cada edición. Solo con historia completa (en el CI el clon es superficial y todos los archivos parecerían de hoy)."""
    import subprocess
    try:
        if subprocess.run(["git", "-C", str(RAIZ), "rev-parse", "--is-shallow-repository"], capture_output=True, text=True).stdout.strip() != "false":
            return
        tarde = []
        for p in archivos():
            m = re.search(r"^corte:\s+(\d{4}-\d{2}-\d{2})", p.read_text(), re.M)
            if not m:
                continue
            sucio = subprocess.run(["git", "-C", str(RAIZ), "status", "--porcelain", "--", str(p)], capture_output=True, text=True).stdout.strip()
            ultimo = HOY.isoformat() if sucio else subprocess.run(
                ["git", "-C", str(RAIZ), "log", "-1", "--format=%ad", "--date=short", "--", str(p)], capture_output=True, text=True).stdout.strip()
            if ultimo and ultimo > m.group(1):
                tarde.append((p.name, (datetime.date.fromisoformat(ultimo) - datetime.date.fromisoformat(m.group(1))).days))
        if tarde:
            tarde.sort(key=lambda x: -x[1])
            nota(f"{len(tarde)} archivos cambiaron después de su corte; los más atrasados: " + ", ".join(f"{n} (+{d} d)" for n, d in tarde[:4]))
    except (OSError, ValueError):
        pass


def rangos_de_seccion(texto):
    """{'5c': (primera línea, última línea)} de cada encabezado numerado; una sección llega hasta el siguiente encabezado de su nivel o de uno más alto."""
    lineas = texto.split("\n")
    hs = []
    for i, l in enumerate(lineas, 1):
        m = re.match(r"^(#{1,4})\s+(\d+[a-z]?(?:\.\d+[a-z]?)*)[.\s]", l)
        if m:
            hs.append((i, len(m.group(1)), m.group(2)))
    rangos = {}
    for k, (i, nivel, clave) in enumerate(hs):
        fin = len(lineas)
        for j, nivel2, _ in hs[k + 1:]:
            if nivel2 <= nivel:
                fin = j - 1
                break
        rangos.setdefault(clave, (i, fin))
    return rangos


def fuentes_de_los_derivados(textos):
    """De qué secciones dice cada archivo que sale: el campo `compilado:` o `derivado:` de su bloque de órgano.

    Devuelve [(derivado, corte, fuente, texto de la sección, primera línea, última línea)]. Solo cuentan las fuentes con sección
    (`X.md` §N, o §N a §M): «el archivo entero» cambia a cada paso y no dice nada. Lo que sigue a «lo que D-…» o a un guion largo
    ya no es una fuente sino un comentario."""
    salida = []
    for p in archivos():
        t = textos.get(p.name) or p.read_text()
        campo = re.search(r"^(?:compilado|derivado):\s+(.*)$", t, re.M)
        corte = re.search(r"^corte:\s+(\d{4}-\d{2}-\d{2})", t, re.M)
        if not campo or not corte:
            continue
        linea = re.split(r"\s(?:y|·)\s+lo que\s|\s—\s", campo.group(1))[0]
        for fuente, desde, hasta in re.findall(r"`?([A-Za-zÑ0-9_\-]+\.md)`?\s*§\s*(\d+[a-z]?(?:\.\d+[a-z]?)*)(?:\s+a\s+§\s*(\d+))?", linea):
            if fuente == p.name or fuente not in textos:
                continue
            rangos = rangos_de_seccion(textos[fuente])
            if hasta:
                claves = [k for k in rangos if k.split(".")[0].isdigit() and int(desde) <= int(k.split(".")[0]) <= int(hasta)]
            else:
                claves = [desde] if desde in rangos else []
            if not claves:
                continue
            salida.append((p.name, corte.group(1), fuente, desde + (f" a §{hasta}" if hasta else ""),
                           min(rangos[k][0] for k in claves), max(rangos[k][1] for k in claves)))
    return salida


def ultimo_cambio_de_lineas(archivo, ini, fin):
    """Fecha (AAAA-MM-DD) del cambio más reciente entre esas líneas, según git blame; hoy si hay algo sin guardar."""
    import subprocess
    r = subprocess.run(["git", "-C", str(RAIZ), "blame", "--line-porcelain", "-L", f"{ini},{fin}", "--", str(archivo)], capture_output=True, text=True)
    if r.returncode != 0:
        return None
    if "Not Committed Yet" in r.stdout:
        return HOY.isoformat()
    tiempos = [int(l.split()[1]) for l in r.stdout.split("\n") if l.startswith("committer-time ")]
    return datetime.datetime.fromtimestamp(max(tiempos), datetime.timezone.utc).date().isoformat() if tiempos else None


def derivados_que_no_oyeron(textos):
    """[(derivado, corte, fuente, sección, último cambio de esa sección)] de lo que cambió después del corte del derivado. Vacío sin historia completa."""
    import subprocess
    if subprocess.run(["git", "-C", str(RAIZ), "rev-parse", "--is-shallow-repository"], capture_output=True, text=True).stdout.strip() != "false":
        return []
    tarde = []
    for deriv, corte, fuente, sec, ini, fin in fuentes_de_los_derivados(textos):
        ultimo = ultimo_cambio_de_lineas(RAIZ / next(str(p.relative_to(RAIZ)) for p in archivos() if p.name == fuente), ini, fin)
        if ultimo and ultimo > corte:
            tarde.append((deriv, corte, fuente, sec, ultimo))
    return tarde


def check_derivados_contra_fuente(textos):
    """La reentrada: un archivo compilado u derivado «oye» cuando cambia la sección de la que sale. Es una nota y no un aviso, igual que el
    corte: el derivado se revisa y su corte se mueve cuando se verifica, no en cada edición de la fuente (D-493)."""
    try:
        tarde = derivados_que_no_oyeron(textos)
    except (OSError, ValueError, StopIteration):
        return
    if tarde:
        por = {}
        for deriv, corte, fuente, sec, ultimo in tarde:
            por.setdefault(deriv, []).append(f"{fuente} §{sec}")
        nota(f"{len(por)} {'archivo compilado no ha oído' if len(por) == 1 else 'archivos compilados no han oído'} un cambio en la sección de la que salen: " + "; ".join(f"{d} ({', '.join(s)})" for d, s in por.items()))


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
    check_migraciones(textos)
    check_tallas(textos)
    check_capacidad(textos)
    check_cortes_contra_git()
    check_derivados_contra_fuente(textos)
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
    for n in notas:
        print(f"Nota: {n}")
    return 1 if fallas else 0


if __name__ == "__main__":
    sys.exit(main())
