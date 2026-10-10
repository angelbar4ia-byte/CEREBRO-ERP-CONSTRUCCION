"""
El programa de una obra, de las filas del libro al CPM y al Gantt — `1-mundo/PROGRAMA-CPM.md` §4 y §8.

Une `dominio` (filas) con `motor_cpm` (cálculo): lee el árbol de un programa tal como lo traen los
siete prototipos (`1-mundo/programas/PROGRAMAS-PROTOTIPOS.csv`), resuelve los vínculos escritos en el
formato fuente `<fila><FS|SS|FF|SF>[±horas]` y entrega actividades y vínculos al motor. Las reglas de
carga son las de D-442 y D-443 (`MODELO.md` §5c):

- el desfase viene en horas y la jornada es de 8;
- la predecesora viene como número de fila del libro, que cambia si se inserta una fila; el programa
  guarda la llave estable (`oid`), nunca el número;
- un bloque puede ser predecesora, también el bloque que contiene a su sucesora (se lee sin ella);
- la sucesora siempre es una partida;
- se rechazan el autovínculo y los ciclos reales. De un ciclo se rechaza el vínculo que las fechas del
  propio programa ya contradicen, y si ninguno, el último que se escribió.

Un vínculo rechazado no detiene la carga: queda en `Programa.rechazados` con su motivo, para que lo vea
el planeador. Un vínculo que las fechas contradicen **sí se carga**: ese es el aviso de
`ALERTA(tipo=vinculo_incumplido)`, no un error de carga.

No depende de Django: recibe filas y devuelve estructuras.
"""
from __future__ import annotations

import csv
import re
from dataclasses import dataclass, field
from datetime import date, timedelta
from fractions import Fraction
from pathlib import Path
from typing import Dict, Iterable, List, Mapping, Optional, Sequence, Tuple

from .motor_cpm import (
    Actividad,
    Calendario,
    CicloError,
    ResultadoCPM,
    Vinculo,
    VinculoInvalido,
    Ventana,
    calcular_cpm,
    desfase_en_dias,
    holgura_vinculo,
    vinculos_incumplidos,
    ventana_de_bloque,
)

TOKEN = re.compile(r"^(\d+)(FS|SS|FF|SF)([+-]\d+(?:\.\d+)?)?$")


# --------------------------------------------------------------------------- filas


@dataclass(frozen=True)
class Fila:
    """Una fila del libro: un bloque (capítulo, subcapítulo, nivel 2 o 3) o un concepto."""

    llave: str  # `oid`: único en todo el libro, sobrevive a que se inserten filas
    fila: int  # número de fila del libro: es lo que citan los vínculos escritos
    nivel: int
    tipo: str  # Capítulo · Subcapítulo · Nivel 2 · Nivel 3 · Concepto
    clave: str
    descripcion: str
    inicio: Optional[date] = None
    termino: Optional[date] = None
    dias: Fraction = Fraction(0)
    vinculos: str = ""  # texto fuente: «80SF, 68SS+120.00000»
    etapa: str = ""  # sub-frente (Nivel 2) al que pertenece
    frente: str = ""  # frente (Nivel 1), el nivel constructivo de la obra

    @property
    def es_partida(self) -> bool:
        """Un concepto con fechas y días: lo único que el CPM programa."""
        return self.tipo == "Concepto" and self.inicio is not None and self.dias > 0


def filas_desde_csv(ruta: Path, prototipo: str) -> List[Fila]:
    """Las filas de un prototipo de `PROGRAMAS-PROTOTIPOS.csv`, en el orden del libro."""
    out: List[Fila] = []
    with open(ruta, encoding="utf-8", newline="") as fh:
        for r in csv.DictReader(fh):
            if r["prototipo"] != prototipo:
                continue
            out.append(
                Fila(
                    llave=r["oid"],
                    fila=int(r["fila"]),
                    nivel=int(r["nivel"]),
                    tipo=r["tipo"],
                    clave=r["clave"],
                    descripcion=r["descripcion"],
                    inicio=date.fromisoformat(r["inicio"]) if r["inicio"] else None,
                    termino=date.fromisoformat(r["termino"]) if r["termino"] else None,
                    dias=Fraction(r["dias_laborables"]) if r["dias_laborables"] else Fraction(0),
                    vinculos=r["vinculos"],
                    etapa=r["etapa"],
                    frente=r["frente"],
                )
            )
    if not out:
        raise ValueError(f"el prototipo {prototipo!r} no está en {ruta}")
    return out


def leer_vinculos(texto: str) -> List[Tuple[Optional[int], str, str, Optional[Fraction]]]:
    """Separa el texto fuente de una celda en (fila predecesora, tipo, token, desfase en días).
    Un token que no cumple el formato devuelve fila `None`: la carga lo rechaza, no se pierde."""
    out = []
    for t in (x.strip() for x in texto.split(",")):
        if not t:
            continue
        m = TOKEN.match(t)
        if not m:
            out.append((None, "", t, None))
            continue
        out.append((int(m.group(1)), m.group(2), t, desfase_en_dias(float(m.group(3) or 0))))
    return out


# --------------------------------------------------------------------------- el programa cargado


@dataclass(frozen=True)
class Rechazado:
    sucesora: str  # llave
    fila: int
    token: str
    motivo: str  # formato · autovinculo · predecesora_desconocida · predecesora_sin_partidas
    #              sucesora_bloque · cierra_un_ciclo


@dataclass
class Programa:
    filas: List[Fila]
    actividades: List[Actividad]
    vinculos: List[Vinculo]
    rechazados: List[Rechazado]
    ventanas: Dict[str, Ventana]  # el plan: inicio y término de cada partida
    bloques: Dict[str, List[str]]  # llave de bloque -> sus partidas, en orden del libro
    por_llave: Dict[str, Fila] = field(default_factory=dict)

    def calcular(self, cal: Calendario, plazo_dias=None, inicio: Optional[date] = None) -> ResultadoCPM:
        """El CPM más temprano de la red cargada. `inicio` es el arranque de la obra, por defecto el
        de la primera partida del plan."""
        arranque = inicio or min(w.inicio for w in self.ventanas.values())
        return calcular_cpm(self.actividades, self.vinculos, cal, arranque, plazo_dias)

    def incumplidos(self, cal: Calendario) -> List[Tuple[Vinculo, Fraction]]:
        """Los vínculos que las fechas del plan contradicen (holgura negativa, bloque sin la sucesora)."""
        return vinculos_incumplidos(self.ventanas, self.vinculos, cal, self.bloques)

    def referencias(self, v: Vinculo) -> List[str]:
        """Las partidas que fijan el extremo de la predecesora de `v`: ella misma, o, si es un bloque,
        todas las del bloque que empatan en cerrar su ventana sin la sucesora (FS, FF) o en abrirla
        (SS, SF). Empatan seguido: la carpintería de planta baja cierra con hasta 12 a la vez."""
        if v.predecesora not in self.bloques:
            return [v.predecesora]
        hijos = [h for h in self.bloques[v.predecesora] if h != v.sucesora and h in self.ventanas]
        if not hijos:
            hijos = [h for h in self.bloques[v.predecesora] if h in self.ventanas]
        if v.tipo in ("FS", "FF"):
            tope = max(self.ventanas[h].fin for h in hijos)
            return [h for h in hijos if self.ventanas[h].fin == tope]
        piso = min(self.ventanas[h].inicio for h in hijos)
        return [h for h in hijos if self.ventanas[h].inicio == piso]

    def referencia(self, v: Vinculo, preferidas: Iterable[str] = ()) -> str:
        """Una sola de ellas, para dibujar la flecha: la que está en `preferidas` (la cadena de relevos)
        si empata, y si no, entre las empatadas la que arranca más tarde en el cierre (la más corta) o la
        primera del libro en la apertura."""
        empatadas = self.referencias(v)
        for h in empatadas:
            if h in set(preferidas):
                return h
        if v.tipo in ("FS", "FF"):
            return max(empatadas, key=lambda h: (self.ventanas[h].inicio, -self._orden(h)))
        return min(empatadas, key=lambda h: self._orden(h))

    def _orden(self, llave: str) -> int:
        return self.por_llave[llave].fila


def cargar_programa(filas: Sequence[Fila], cal: Calendario) -> Programa:
    por_fila: Dict[int, Fila] = {}
    for f in filas:
        if f.fila in por_fila:
            raise ValueError(f"fila {f.fila} repetida")
        por_fila[f.fila] = f
    por_llave = {f.llave: f for f in filas}
    if len(por_llave) != len(filas):
        raise ValueError("la llave (`oid`) se repite: no hay forma de seguir una fila cuando se inserta otra")

    ventanas = {f.llave: Ventana(f.inicio, f.termino) for f in filas if f.es_partida}

    # los bloques: cada fila que no es concepto con las partidas que cuelgan de ella
    bloques: Dict[str, List[str]] = {}
    for i, f in enumerate(filas):
        if f.tipo == "Concepto":
            continue
        hijos = []
        for q in filas[i + 1 :]:
            if q.nivel <= f.nivel:
                break
            if q.es_partida:
                hijos.append(q.llave)
        bloques[f.llave] = hijos

    # 1. leer y validar cada vínculo
    aceptados: List[Tuple[Vinculo, int, str]] = []  # (vínculo, fila sucesora, token)
    rechazados: List[Rechazado] = []
    for f in filas:
        if not f.vinculos.strip():
            continue
        for fila_p, tipo, token, desfase in leer_vinculos(f.vinculos):
            def no(motivo: str) -> None:
                rechazados.append(Rechazado(f.llave, f.fila, token, motivo))

            if not f.es_partida:
                no("sucesora_bloque")
            elif fila_p is None:
                no("formato")
            elif fila_p == f.fila:
                no("autovinculo")
            elif fila_p not in por_fila:
                no("predecesora_desconocida")
            else:
                p = por_fila[fila_p]
                if p.es_partida:
                    aceptados.append((Vinculo(p.llave, f.llave, tipo, desfase), f.fila, token))
                elif p.llave in bloques and bloques[p.llave]:
                    aceptados.append((Vinculo(p.llave, f.llave, tipo, desfase), f.fila, token))
                elif p.llave in bloques:
                    no("predecesora_sin_partidas")
                else:
                    no("predecesora_desconocida")  # concepto sin fechas: no es nada que el CPM programe

    # 2. los ciclos reales: solo entre partidas; un bloque nunca cierra un ciclo por sí mismo
    aceptados = _sin_ciclos(aceptados, ventanas, bloques, cal, por_llave, rechazados)

    vinculos = [v for v, _, _ in aceptados]
    usados = {v.predecesora for v in vinculos if v.predecesora in bloques}
    actividades = [Actividad(f.llave, Fraction(cal.n(f.termino) + 1 - cal.n(f.inicio))) for f in filas if f.es_partida]
    actividades += [Actividad(b, 0, tuple(h for h in bloques[b])) for b in bloques if b in usados]
    return Programa(list(filas), actividades, vinculos, rechazados, ventanas, bloques, por_llave)


def _holgura_en_el_plan(v: Vinculo, ventanas, bloques, cal) -> Optional[Fraction]:
    """La holgura del vínculo sobre las fechas del plan, con el bloque leído sin la sucesora (D-443).
    `None` si la predecesora no tiene ninguna otra partida (nada que medir)."""
    if v.predecesora in bloques:
        pred = ventana_de_bloque(bloques[v.predecesora], ventanas, v.sucesora)
    else:
        pred = ventanas.get(v.predecesora)
    suc = ventanas.get(v.sucesora)
    if pred is None or suc is None:
        return None
    return holgura_vinculo(v, pred, suc, cal)


def _sin_ciclos(aceptados, ventanas, bloques, cal, por_llave, rechazados):
    """Quita, de cada ciclo, el vínculo que las fechas ya contradicen; si ninguno, el último escrito.
    Primero los ciclos entre partidas; después los que pasan por un bloque como predecesora (la partida
    que fija el extremo del bloque espera a su vez a la sucesora), que se reconocen porque el motor no
    converge. Un par que se cierra en cero (la gualdra termina la víspera de su losa y la losa arranca
    al día siguiente) no es un ciclo: es un `SF` y un `FS` que se cumplen a la vez."""
    vivos = list(aceptados)
    pendientes = lambda i: -_holgura_en_el_plan(vivos[i][0], ventanas, bloques, cal) if _holgura_en_el_plan(vivos[i][0], ventanas, bloques, cal) is not None else Fraction(-10**9)

    def quitar(candidatos):
        peor = max(candidatos, key=lambda i: (pendientes(i), i))
        v, fila, token = vivos.pop(peor)
        rechazados.append(Rechazado(v.sucesora, fila, token, "cierra_un_ciclo"))

    # 1. entre partidas
    while True:
        directos = [i for i, (v, _, _) in enumerate(vivos) if v.predecesora in ventanas]
        grupo = _componente_con_ciclo([(vivos[i][0].predecesora, vivos[i][0].sucesora) for i in directos])
        if not grupo:
            break
        quitar([i for i in directos if vivos[i][0].predecesora in grupo and vivos[i][0].sucesora in grupo])

    # 2. a través de bloques: el motor no converge y dice qué vínculos forman el ciclo que se alarga
    while True:
        try:
            _probar(vivos, ventanas, bloques, cal)
            return vivos
        except CicloError as e:
            culpables = [i for i, (v, _, _) in enumerate(vivos) if v in e.vinculos]
            if not culpables:
                raise  # el motor no converge y no dice por qué: no se adivina
            quitar(culpables)


def _probar(vivos, ventanas, bloques, cal) -> None:
    vinculos = [v for v, _, _ in vivos]
    usados = {v.predecesora for v in vinculos if v.predecesora in bloques}
    acts = [Actividad(k, Fraction(cal.n(w.fin) + 1 - cal.n(w.inicio))) for k, w in ventanas.items()]
    acts += [Actividad(b, 0, tuple(bloques[b])) for b in bloques if b in usados]
    calcular_cpm(acts, vinculos, cal, min(w.inicio for w in ventanas.values()))


def _componente_con_ciclo(aristas: Sequence[Tuple[str, str]]) -> Optional[set]:
    """Un componente fuertemente conexo con más de un nodo (Kosaraju, iterativo), o None."""
    sig: Dict[str, List[str]] = {}
    ant: Dict[str, List[str]] = {}
    nodos = []
    for a, b in aristas:
        for n in (a, b):
            if n not in sig:
                sig[n] = []
                ant[n] = []
                nodos.append(n)
        sig[a].append(b)
        ant[b].append(a)
    visto, orden = set(), []
    for s in nodos:
        if s in visto:
            continue
        pila = [(s, iter(sig[s]))]
        visto.add(s)
        while pila:
            n, it = pila[-1]
            for m in it:
                if m not in visto:
                    visto.add(m)
                    pila.append((m, iter(sig[m])))
                    break
            else:
                orden.append(n)
                pila.pop()
    asignado: Dict[str, int] = {}
    for s in reversed(orden):
        if s in asignado:
            continue
        comp, pila = [], [s]
        asignado[s] = 1
        while pila:
            n = pila.pop()
            comp.append(n)
            for m in ant[n]:
                if m not in asignado:
                    asignado[m] = 1
                    pila.append(m)
        if len(comp) > 1:
            return set(comp)
    return None


# --------------------------------------------------------------------------- la cadena de relevos


def cadena_de_relevos(prog: Programa, cal: Calendario) -> List[str]:
    """La cadena de partidas con holgura 0 sobre las fechas del plan, de la que cierra el programa hacia
    atrás: cada una arranca (o termina) justo cuando el vínculo de la anterior lo permite. Es la ruta
    que lee el planeador en el programa hecho a mano (`PROGRAMA-CPM.md` §6.4), no la ruta crítica de la
    red que calcula `calcular`. Entre varias cadenas posibles, la más larga; a igual largo, la que
    arranca antes."""
    entrantes: Dict[str, List[str]] = {}
    for v in prog.vinculos:
        if v.sucesora not in prog.ventanas:
            continue
        pred = ventana_de_bloque(prog.bloques[v.predecesora], prog.ventanas, v.sucesora) if v.predecesora in prog.bloques else prog.ventanas[v.predecesora]
        if pred is None or holgura_vinculo(v, pred, prog.ventanas[v.sucesora], cal) != 0:
            continue
        for ref in prog.referencias(v):
            if ref != v.sucesora:
                entrantes.setdefault(v.sucesora, []).append(ref)
    memo: Dict[str, List[str]] = {}
    visitando: set = set()

    def mejor(n: str) -> List[str]:
        if n in memo:
            return memo[n]
        if n in visitando:
            return [n]
        visitando.add(n)
        cola = [n]
        for p in entrantes.get(n, ()):
            c = mejor(p) + [n]
            if (len(c), -cal.n(prog.ventanas[c[0]].inicio)) > (len(cola), -cal.n(prog.ventanas[cola[0]].inicio)):
                cola = c
        visitando.discard(n)
        memo[n] = cola
        return cola

    fin = max(w.fin for w in prog.ventanas.values())
    finales = [n for n, w in prog.ventanas.items() if w.fin == fin]
    return max((mejor(n) for n in finales), key=lambda c: (len(c), -cal.n(prog.ventanas[c[0]].inicio)))


# --------------------------------------------------------------------------- el Gantt como dato


def vista_gantt(
    prog: Programa,
    cal: Calendario,
    ventana: Optional[Tuple[date, date]] = None,
    relevos: Optional[Sequence[str]] = None,
    niveles_resumen: Sequence[int] = (2, 3),
    resultado: Optional[ResultadoCPM] = None,
) -> Dict[str, object]:
    """Lo que una pantalla necesita para dibujar el Gantt de `PROGRAMA-CPM.md` §8, sin dibujar nada:

    - `filas`: una por partida y una por bloque de los `niveles_resumen` (por defecto el 2 y el 3, como
      la imagen de D-432: 388 partidas y 90 resúmenes en Zafiro Plus), en el orden del libro, con su
      etapa para el color y `critica` si está en la cadena de relevos;
    - `flechas`: una por vínculo, desde la partida que fija la fecha de la predecesora (no desde el
      bloque), con su holgura y `incumplido` si las fechas lo contradicen;
    - `marcas`: los fines de semana y feriados que caen dentro del programa y la ventana, si la hay;
    - `ruta_critica_red`: si se pasa el `resultado` del CPM, las partidas de la ruta crítica de la red,
      para que la pantalla pueda marcar una u otra (la cadena de relevos lee el plan; esta lee la red).
    """
    if relevos is None:
        relevos = cadena_de_relevos(prog, cal)
    critica = set(relevos)
    filas = []
    for f in prog.filas:
        if f.es_partida:
            w = prog.ventanas[f.llave]
            ini, fin = w.inicio, w.fin
        elif f.nivel in niveles_resumen and f.llave in prog.bloques and prog.bloques[f.llave]:
            ws = [prog.ventanas[h] for h in prog.bloques[f.llave]]
            ini, fin = min(w.inicio for w in ws), max(w.fin for w in ws)
        else:
            continue
        filas.append(
            {
                "llave": f.llave,
                "fila": f.fila,
                "nivel": f.nivel,
                "clave": f.clave,
                "descripcion": f.descripcion,
                "resumen": not f.es_partida,
                "inicio": ini.isoformat(),
                "fin": fin.isoformat(),
                "frente": f.frente,
                "etapa": f.etapa,
                "critica": f.llave in critica,
            }
        )
    flechas = []
    for v in prog.vinculos:
        suc = prog.ventanas.get(v.sucesora)
        if suc is None:
            continue
        ref = prog.referencia(v, critica)
        if ref == v.sucesora:
            continue
        pred = ventana_de_bloque(prog.bloques[v.predecesora], prog.ventanas, v.sucesora) if v.predecesora in prog.bloques else prog.ventanas[v.predecesora]
        h = holgura_vinculo(v, pred, suc, cal) if pred is not None else None
        flechas.append(
            {
                "de": ref,
                "a": v.sucesora,
                "tipo": v.tipo,
                "desfase": float(v.desfase),
                "holgura": None if h is None else float(h),
                "incumplido": h is not None and h < 0,
                "entre_relevos": ref in critica and v.sucesora in critica,
            }
        )
    desde = min(w.inicio for w in prog.ventanas.values())
    hasta = max(w.fin for w in prog.ventanas.values())
    marcas = {
        "no_laborables": [],
        "ventana": None if ventana is None else {"inicio": ventana[0].isoformat(), "fin": ventana[1].isoformat()},
    }
    d = desde
    while d <= hasta:
        if not cal.es_habil(d):
            marcas["no_laborables"].append({"fecha": d.isoformat(), "motivo": "fin de semana" if d.weekday() not in cal.dias_laborables_semana else "feriado"})
        d += timedelta(days=1)
    frentes = {f.clave: f.descripcion for f in prog.filas if f.tipo == "Subcapítulo"}
    etapas = {f.clave: f.descripcion for f in prog.filas if f.tipo == "Nivel 2"}
    return {
        "filas": filas, "flechas": flechas, "marcas": marcas, "relevos": list(relevos),
        "frentes": frentes, "etapas": etapas, "desde": desde.isoformat(), "hasta": hasta.isoformat(),
        "ruta_critica_red": list(resultado.ruta_critica) if resultado is not None else [],
    }
