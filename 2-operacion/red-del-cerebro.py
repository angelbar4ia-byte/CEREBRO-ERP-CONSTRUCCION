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
