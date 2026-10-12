#!/usr/bin/env python3
"""
red-del-cerebro.py — mide cómo está conectado el cerebro consigo mismo.

No comprueba nada ni corrige nada (eso es `verificar-cerebro.py`): mide, para que lo que `METACOGNICION.md` dice de la red se
pueda volver a sacar. Dos clases de conexión, como en un cerebro de verdad:

  estructural   una referencia escrita de un archivo a otro (`OTRO.md`): la sinapsis anatómica
  funcional     dos archivos que cambian en los mismos commits: lo que se activa junto, aunque nadie lo haya escrito

Uso:  python3 2-operacion/red-del-cerebro.py [ruta-al-cerebro]
Con --vigencia (necesita la historia completa de git) añade, por archivo, cuánto se ha movido desde su `corte` él y los archivos en
los que se apoya.
Con --integracion mide cuánto se puede partir la red sin perder referencias (la idea de la información integrada) y dónde dos
archivos dicen casi lo mismo (lo que le falta para estar diferenciada).
Con --reentrada dice, para cada archivo compilado o derivado, si la sección de la que sale cambió después de su `corte` (la idea del
núcleo dinámico: lo que sale vuelve a entrar).
La parte funcional necesita la historia completa de git (en un clon superficial no hay nada que medir y se omite).
"""
import collections
import itertools
import re
import subprocess
import sys
from pathlib import Path

RAIZ = Path(next((a for a in sys.argv[1:] if not a.startswith("--")), Path(__file__).resolve().parent.parent))
CAPAS = {"1": "I", "2": "II", "3": "III", "4": "IV"}


def capa(p):
    r = p.relative_to(RAIZ).parts
    return CAPAS.get(r[0][0], "—") if len(r) > 1 and r[0][1:2] == "-" else "—"


def estructural(archivos):
    nombre = {p.name: p for p in archivos}
    texto = {p.name: p.read_text(encoding="utf-8") for p in archivos}
    aristas = collections.Counter()
    for a, t in texto.items():
        for ref in re.findall(r"`?([A-Za-zÑ0-9_\-]+\.md)`?", t):
            if ref in nombre and ref != a:
                aristas[(a, ref)] += 1
    return nombre, aristas


def distancias(vecinos, origen):
    visto, frontera, d = {origen: 0}, [origen], 0
    while frontera:
        d += 1
        nueva = []
        for n in frontera:
            for m in vecinos[n]:
                if m not in visto:
                    visto[m] = d
                    nueva.append(m)
        frontera = nueva
    return visto


def mostrar_estructura(archivos):
    nombre, aristas = estructural(archivos)
    entra, sale = collections.Counter(), collections.Counter()
    for a, b in aristas:
        sale[a] += 1
        entra[b] += 1
    print(f"ESTRUCTURAL · {len(nombre)} archivos · {len(aristas)} conexiones distintas · {sum(aristas.values())} referencias")
    print("  los que más reciben (archivos distintos que los nombran → a cuántos nombran):")
    for n, c in entra.most_common(6):
        print(f"    {n:30} {c:3} → {sale[n]:3}   capa {capa(nombre[n])}")
    print(f"  sin entrada: {[n for n in nombre if not entra[n]] or 'ninguno'} · sin salida: {[n for n in nombre if not sale[n]] or 'ninguno'}")
    reciprocas = sum(1 for (a, b) in aristas if (b, a) in aristas) // 2
    print(f"  recíprocas: {reciprocas} de {len(aristas)} ({100 * 2 * reciprocas // len(aristas)}% de las conexiones tienen vuelta)")

    # mundo pequeño: caminos cortos y vecinos que se conocen entre sí, sin mirar el sentido
    vecinos = collections.defaultdict(set)
    for a, b in aristas:
        vecinos[a].add(b)
        vecinos[b].add(a)
    todas = [d for n in nombre for d in distancias(vecinos, n).values() if d]
    agrupamiento = []
    for n, vs in vecinos.items():
        k = len(vs)
        if k > 1:
            enlaces = sum(1 for x, y in itertools.combinations(vs, 2) if y in vecinos[x])
            agrupamiento.append(enlaces / (k * (k - 1) / 2))
    print(f"  camino medio entre dos archivos: {sum(todas) / len(todas):.2f} saltos · diámetro: {max(todas)} · "
          f"agrupamiento: {sum(agrupamiento) / len(agrupamiento):.2f}")
    for ini in ("INDICE.md", "README.md"):
        if ini in nombre:
            print(f"  desde {ini} se llega a {len(distancias(vecinos, ini))} de {len(nombre)} archivos")

    capas = collections.Counter()
    for (a, b), w in aristas.items():
        capas[(capa(nombre[a]), capa(nombre[b]))] += w
    print("  referencias entre capas (de → a):  " + " · ".join(
        f"{x}→{y} {w}" for (x, y), w in sorted(capas.items()) if x != "—" and y != "—" and x != y))
    print("  (lo estable —I, Mundo— apuntando a lo volátil —IV, Dirección— es la dependencia que conviene vigilar)")


def mostrar_funcion(archivos):
    shallow = subprocess.run(["git", "-C", str(RAIZ), "rev-parse", "--is-shallow-repository"], capture_output=True, text=True).stdout.strip()
    if shallow != "false":
        print("\nFUNCIONAL · sin historia completa de git: se omite")
        return
    salida = subprocess.run(["git", "-C", str(RAIZ), "log", "--name-only", "--format=@@%h"], capture_output=True, text=True).stdout
    commits, actual = [], None
    for linea in salida.split("\n"):
        if linea.startswith("@@"):
            actual = []
            commits.append(actual)
        elif linea.strip().endswith(".md") and actual is not None:
            actual.append(linea.strip().split("/")[-1])
    commits = [sorted(set(c)) for c in commits if c]
    cambios, juntos = collections.Counter(), collections.Counter()
    for c in commits:
        cambios.update(c)
        if len(c) <= 14:  # el commit que trajo los 32 archivos no dice nada de quién cambia con quién
            juntos.update(itertools.combinations(c, 2))
    print(f"\nFUNCIONAL · {len(commits)} commits que tocan archivos .md")
    nucleo = [(n, c) for n, c in cambios.most_common() if c >= 0.8 * len(commits)]
    print("  los que cambian casi siempre (≥ 80% de los commits) —por donde pasa toda decisión—: " + ", ".join(f"{n} {100 * c // len(commits)}%" for n, c in nucleo))
    _, aristas = estructural(archivos)
    ocultas = [(a, b, w) for (a, b), w in juntos.most_common() if w >= 8 and (a, b) not in aristas and (b, a) not in aristas]
    print("  cambian juntos y ninguno nombra al otro:  " + ("; ".join(f"{a} ↔ {b} ({w})" for a, b, w in ocultas) or "ninguno"))


def mostrar_vigencia(archivos):
    """Por archivo: su corte, cuándo cambió por última vez, y qué archivos que nombra cambiaron después de su corte (sus fuentes)."""
    import datetime
    if subprocess.run(["git", "-C", str(RAIZ), "rev-parse", "--is-shallow-repository"], capture_output=True, text=True).stdout.strip() != "false":
        print("\nVIGENCIA · sin historia completa de git: se omite")
        return

    def ultimo(p):
        sucio = subprocess.run(["git", "-C", str(RAIZ), "status", "--porcelain", "--", str(p)], capture_output=True, text=True).stdout.strip()
        if sucio:
            return datetime.date.today()
        d = subprocess.run(["git", "-C", str(RAIZ), "log", "-1", "--format=%ad", "--date=short", "--", str(p)], capture_output=True, text=True).stdout.strip()
        return datetime.date.fromisoformat(d) if d else None

    nombre, aristas = estructural(archivos)
    corte, cambio = {}, {}
    for p in archivos:
        m = re.search(r"^corte:\s+(\d{4}-\d{2}-\d{2})", p.read_text(encoding="utf-8"), re.M)
        if m:
            corte[p.name] = datetime.date.fromisoformat(m.group(1))
        cambio[p.name] = ultimo(p)
    print("\nVIGENCIA · por archivo: días que se ha movido desde su corte, y sus fuentes (los que más nombra) que se movieron después")
    filas = []
    for n, c in corte.items():
        propio = (cambio[n] - c).days if cambio[n] else 0
        fuentes = sorted(((w, b) for (a, b), w in aristas.items() if a == n and b in cambio and cambio[b] and cambio[b] > c), reverse=True)
        filas.append((propio, len(fuentes), n, c, fuentes[:3]))
    for propio, nf, n, c, fuentes in sorted(filas, reverse=True):
        if propio > 0 or nf:
            print(f"  {n:30} corte {c} · él +{propio:3} d · {nf:2} fuentes movidas  " + ", ".join(f"{b}×{w}" for w, b in fuentes))


def particion_mas_debil(nombre, aristas, minimo, intentos=60):
    """La partición de la red en dos lados, con al menos `minimo` archivos cada uno, que menos referencias corta. Búsqueda local desde
    arranques al azar con semilla fija: no prueba que sea la mejor, pero se repite igual."""
    import random
    peso = collections.Counter()
    for (a, b), w in aristas.items():
        peso[frozenset((a, b))] += w
    nodos = sorted(nombre)
    n = len(nodos)

    def corte(lado):
        return sum(w for k, w in peso.items() if (next(iter(k)) in lado) != (list(k)[1] in lado))

    azar, mejor = random.Random(1), (None, None)
    for _ in range(intentos):
        lado = set(azar.sample(nodos, azar.randint(minimo, n - minimo)))
        actual = corte(lado)
        mejora = True
        while mejora:
            mejora = False
            for x in nodos:
                prueba = set(lado)
                if x in prueba:
                    if len(prueba) <= minimo:
                        continue
                    prueba.remove(x)
                else:
                    if n - len(prueba) <= minimo:
                        continue
                    prueba.add(x)
                c = corte(prueba)
                if c < actual:
                    lado, actual, mejora = prueba, c, True
        if mejor[0] is None or actual < mejor[0]:
            mejor = (actual, lado)
    chico = mejor[1] if len(mejor[1]) <= n / 2 else set(nodos) - mejor[1]
    return mejor[0], sorted(chico), sum(peso.values())


def articulaciones(nombre, aristas):
    """Archivos cuya salida desconecta la red (sin mirar el sentido de la referencia)."""
    vecinos = collections.defaultdict(set)
    for a, b in aristas:
        vecinos[a].add(b)
        vecinos[b].add(a)
    return [n for n in sorted(nombre) if len(distancias({k: v - {n} for k, v in vecinos.items() if k != n}, next(x for x in sorted(nombre) if x != n))) < len(nombre) - 1]


def parrafos_largos(archivos, minimo=280):
    """[(archivo, línea, texto)] de los párrafos de prosa de al menos `minimo` caracteres; tablas y código fuera, y MEMORIA también
    (la historia repite todo a propósito)."""
    salida = []
    for p in archivos:
        if p.name == "MEMORIA.md":
            continue
        buf, ini = [], 1
        lineas = p.read_text(encoding="utf-8").split("\n") + [""]
        for i, l in enumerate(lineas, 1):
            if l.strip() == "":
                texto = " ".join(buf)
                if len(texto) >= minimo and not texto.lstrip().startswith(("|", "```")):
                    salida.append((p.name, ini, texto))
                buf = []
            else:
                if not buf:
                    ini = i
                buf.append(l.strip())
    return salida


def pares_casi_iguales(parrafos, umbral=0.55):
    """Pares de párrafos de archivos distintos con coseno TF-IDF de al menos `umbral`. Los idénticos también salen: aquí no se distingue."""
    import math
    import unicodedata
    parar = set("de la el los las un una y o en a que se por con para del al es no lo su sus como mas si ya cada son sin sobre entre este esta esto estos estas hay ser fue era solo muy tambien pero todo todos todas cuando donde quien cual otra otro otros otras mismo misma ver".split())

    def palabras(t):
        t = unicodedata.normalize("NFKD", t.lower())
        t = "".join(c for c in t if not unicodedata.combining(c))
        return [w for w in re.findall(r"[a-z0-9]{4,}", t) if w not in parar]

    cuentas = [collections.Counter(palabras(t)) for _, _, t in parrafos]
    df = collections.Counter()
    for c in cuentas:
        df.update(c.keys())
    n = len(cuentas)
    vectores = []
    for c in cuentas:
        v = {w: (1 + math.log(f)) * math.log(n / df[w]) for w, f in c.items()}
        norma = math.sqrt(sum(x * x for x in v.values())) or 1
        vectores.append({w: x / norma for w, x in v.items()})
    inv = collections.defaultdict(list)
    for i, v in enumerate(vectores):
        for w in v:
            inv[w].append(i)
    pares = []
    for i, v in enumerate(vectores):
        cand = collections.Counter()
        for w in v:
            if df[w] > 40:
                continue
            for j in inv[w]:
                if j > i and parrafos[j][0] != parrafos[i][0]:
                    cand[j] += v[w] * vectores[j][w]
        pares += [(s, i, j) for j, s in cand.items() if s >= umbral]
    return sorted(pares, reverse=True)


def mostrar_integracion(archivos):
    nombre, aristas = estructural(archivos)
    total = sum(aristas.values())
    print("\nINTEGRACIÓN · cuánto se puede partir la red sin perder referencias")
    art = articulaciones(nombre, aristas)
    print(f"  archivos cuya salida desconecta la red: {art or 'ninguno'}")
    for minimo in (5, 10, 15):
        corte, chico, _ = particion_mas_debil(nombre, aristas, minimo)
        print(f"  la partición más floja con al menos {minimo} por lado corta {corte} de {total} referencias ({100 * corte / total:.1f}%); el lado chico: " + ", ".join(chico))
    print("  (una red integrada no se parte barato; el lado que sale casi suelto es donde la sincronía se rompe primero)")
    ps = parrafos_largos(archivos)
    pares = pares_casi_iguales(ps)
    print(f"\nDIFERENCIACIÓN · {len(ps)} párrafos de prosa de 280 caracteres o más; {len(pares)} pares de archivos distintos con parecido de 0.55 o más")
    por = collections.Counter(tuple(sorted((ps[i][0], ps[j][0]))) for _, i, j in pares)
    for (a, b), c in por.most_common(8):
        print(f"    {a} ~ {b}: {c}")
    print("  (los compilados repiten a su fuente a propósito; lo que preocupa es el parecido entre dos archivos que ninguno deriva del otro)")


def mostrar_reentrada(archivos):
    """Por archivo compilado o derivado: de qué secciones sale y cuándo cambió cada una. La lógica es la del verificador."""
    import importlib.util
    spec = importlib.util.spec_from_file_location("verificar_cerebro", Path(__file__).resolve().parent / "verificar-cerebro.py")
    v = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(v)
    v.RAIZ = RAIZ
    textos = {p.name: p.read_text(encoding="utf-8") for p in archivos}
    print("\nREENTRADA · de qué sección sale cada archivo compilado y cuándo cambió esa sección")
    if subprocess.run(["git", "-C", str(RAIZ), "rev-parse", "--is-shallow-repository"], capture_output=True, text=True).stdout.strip() != "false":
        print("  sin historia completa de git: se omite")
        return
    ruta = {p.name: p for p in archivos}
    for deriv, corte, fuente, sec, ini, fin in v.fuentes_de_los_derivados(textos):
        ultimo = v.ultimo_cambio_de_lineas(ruta[fuente], ini, fin)
        marca = "   ◄ cambió después de su corte" if ultimo and ultimo > corte else ""
        print(f"  {deriv:28} corte {corte} · {fuente} §{sec} (líneas {ini}-{fin}) cambió el {ultimo}{marca}")
    cortex, relevo = {"CONOCIMIENTO.md", "MODELO.md"}, {"INDICE.md", "ESTADO.md"}
    salida = subprocess.run(["git", "-C", str(RAIZ), "log", "--name-only", "--format=@@%h"], capture_output=True, text=True).stdout
    commits, actual = [], None
    for linea in salida.split("\n"):
        if linea.startswith("@@"):
            actual = set()
            commits.append(actual)
        elif linea.strip().endswith(".md") and actual is not None:
            actual.add(linea.strip().split("/")[-1])
    tocan = [c for c in commits if c & cortex]
    sin_relevo = [c for c in tocan if not c & relevo]
    print(f"  el relevo: de {len(tocan)} commits que tocan `CONOCIMIENTO` o `MODELO`, {len(sin_relevo)} no tocan ni `INDICE` ni `ESTADO`")


def mostrar_capacidad(archivos):
    print("\nCAPACIDAD · la fila de tabla más larga de lo que se lee primero")
    for p in archivos:
        if p.name in ("ESTADO.md", "INDICE.md"):
            filas = [len(l) for l in p.read_text(encoding="utf-8").split("\n") if l.startswith("|")]
            print(f"  {p.name:12} {len(p.read_text(encoding='utf-8')):7,} caracteres · fila más larga {max(filas):6,}")


if __name__ == "__main__":
    todos = sorted(RAIZ.rglob("*.md"))
    mostrar_estructura(todos)
    mostrar_funcion(todos)
    mostrar_capacidad(todos)
    if "--vigencia" in sys.argv:
        mostrar_vigencia(todos)
    if "--integracion" in sys.argv:
        mostrar_integracion(todos)
    if "--reentrada" in sys.argv:
        mostrar_reentrada(todos)
