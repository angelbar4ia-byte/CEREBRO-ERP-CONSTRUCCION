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
from dataclasses import dataclass, field, replace
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
    tipo_normal,
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
    origenes: Dict[Vinculo, str] = field(default_factory=dict)  # por qué existe cada vínculo: lo que se declaró

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


def _estructura(filas: Sequence[Fila]):
    """Lo que dicen las filas por sí solas: sus índices, las ventanas del plan y las partidas de cada bloque."""
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
    return por_fila, por_llave, ventanas, bloques


def armar_programa(
    filas: Sequence[Fila],
    vinculos: Sequence[Vinculo],
    rechazados: Sequence[Rechazado],
    cal: Calendario,
    origenes: Optional[Mapping[Vinculo, str]] = None,
) -> Programa:
    """Un programa a partir de filas y de vínculos ya resueltos (por llave, no por número de fila): lo que
    entrega un repositorio. Los vínculos se dan por buenos: la validación ocurrió al cargarlos."""
    _, por_llave, ventanas, bloques = _estructura(filas)
    usados = {v.predecesora for v in vinculos if v.predecesora in bloques}
    actividades = [Actividad(f.llave, Fraction(cal.n(f.termino) + 1 - cal.n(f.inicio))) for f in filas if f.es_partida]
    actividades += [Actividad(b, 0, tuple(h for h in bloques[b])) for b in bloques if b in usados]
    return Programa(
        list(filas), actividades, list(vinculos), list(rechazados), ventanas, bloques, por_llave,
        {v: o for v, o in (origenes or {}).items() if v in set(vinculos)},
    )


def cargar_programa(filas: Sequence[Fila], cal: Calendario) -> Programa:
    por_fila, por_llave, ventanas, bloques = _estructura(filas)

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
    return armar_programa(filas, [v for v, _, _ in aceptados], rechazados, cal)


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


# --------------------------------------------------------------------------- editar y reprogramar
#
# El sistema propone, el planeador decide (`PROGRAMA-CPM.md` §8). Una edición no se aplica a ciegas: se
# reprograma y se devuelve el impacto —qué partidas se mueven, cuánto el cierre, si la ruta cambia—, y
# recién entonces el planeador la acepta. Dos permisos distintos (`MODELO.md` §5b): la estructura (duración
# y vínculos, `editar_estructura_programa`) y las fechas (`editar_fechas_programa`).


@dataclass(frozen=True)
class CambiarDuracion:
    """Estructura: la partida dura `dias` días hábiles (envolvente: incluye sus paros)."""

    llave: str
    dias: Fraction


@dataclass(frozen=True)
class FijarInicio:
    """Fechas: la partida no arranca antes de `fecha` (un disparador, como el ancla contractual)."""

    llave: str
    fecha: date


ORIGENES = ("tecnica", "recurso", "decision")  # `PRECEDENCIA.origen`: por qué existe ese orden
ORIGEN_POR_OMISION = "decision"  # el de menor confianza: lo que alguien edita sin decir por qué se revisa primero
CONFIANZA_DE = {"tecnica": "alta", "recurso": "media", "decision": "baja"}  # derivada del origen, no declarada


def confianza_de(origen: Optional[str]) -> Optional[str]:
    return CONFIANZA_DE.get(origen) if origen else None


@dataclass(frozen=True)
class AgregarVinculo:
    predecesora: str  # una partida o un bloque con partidas
    sucesora: str  # siempre una partida
    tipo: str = "FS"
    desfase: Fraction = Fraction(0)
    origen: Optional[str] = None  # técnica · recurso · decisión; sin declarar, `decision`


@dataclass(frozen=True)
class QuitarVinculo:
    predecesora: str
    sucesora: str
    tipo: Optional[str] = None  # None: todos los de ese par


@dataclass(frozen=True)
class CambiarVinculo:
    predecesora: str
    sucesora: str
    tipo_actual: str
    tipo: str
    desfase: Fraction = Fraction(0)
    origen: Optional[str] = None  # si no se declara, conserva el que tenía y, si no tenía, `decision`


PERMISO_DE = {
    CambiarDuracion: "editar_estructura_programa",
    AgregarVinculo: "editar_estructura_programa",
    QuitarVinculo: "editar_estructura_programa",
    CambiarVinculo: "editar_estructura_programa",
    FijarInicio: "editar_fechas_programa",
}


_TIPO_DE_EDICION = {
    "cambiar_duracion": CambiarDuracion,
    "fijar_inicio": FijarInicio,
    "agregar_vinculo": AgregarVinculo,
    "quitar_vinculo": QuitarVinculo,
    "cambiar_vinculo": CambiarVinculo,
}
_NOMBRE_DE_EDICION = {c: n for n, c in _TIPO_DE_EDICION.items()}


def edicion_a_dict(e: object) -> Dict[str, object]:
    """La edición tal como se guarda: un diccionario de texto y números, sin objetos."""
    nombre = _NOMBRE_DE_EDICION.get(type(e))
    if nombre is None:
        raise TypeError(f"edición desconocida: {e!r}")
    d: Dict[str, object] = {"edicion": nombre}  # «tipo» ya es el del vínculo (FS, SS…)
    for k, v in e.__dict__.items():
        d[k] = v.isoformat() if isinstance(v, date) else (str(Fraction(v)) if k in ("dias", "desfase") else v)
    return d


def edicion_desde_dict(d: Mapping[str, object]) -> object:
    clase = _TIPO_DE_EDICION.get(d.get("edicion"))  # type: ignore[arg-type]
    if clase is None:
        raise ValueError(f"edición desconocida: {d.get('edicion')!r}")
    campos = {k: v for k, v in d.items() if k != "edicion"}
    for k in ("dias", "desfase"):
        if k in campos:
            campos[k] = Fraction(campos[k])
    if "fecha" in campos:
        campos["fecha"] = date.fromisoformat(campos["fecha"])  # type: ignore[arg-type]
    return clase(**campos)


def origen_de_edicion(e: object) -> Optional[str]:
    """El origen que declara la edición, si es de las que agregan o cambian un vínculo."""
    if isinstance(e, (AgregarVinculo, CambiarVinculo)):
        return e.origen or ORIGEN_POR_OMISION
    return None


@dataclass(frozen=True)
class Movida:
    llave: str
    dias_inicio: int  # días hábiles que se corre el arranque
    dias_fin: int


@dataclass(frozen=True)
class Impacto:
    """Lo que el planeador ve antes de decidir: qué se mueve, cuánto el cierre y si cambia la ruta."""

    movidas: List[Movida]
    fin_antes: date
    fin_despues: date
    dias_de_cambio: int  # días hábiles que se mueve el cierre
    ruta_antes: List[str]
    ruta_despues: List[str]
    ruta_cambia: bool  # D-100: la ruta se recalcula siempre, pero solo avisa si cambia de actividades

    def resumen(self) -> Dict[str, object]:
        """Lo que se guarda con una edición aplicada: lo que se le mostró a quien decidió."""
        return {
            "partidas_movidas": len(self.movidas),
            "fin_antes": self.fin_antes.isoformat(),
            "fin_despues": self.fin_despues.isoformat(),
            "dias_de_cambio": self.dias_de_cambio,
            "ruta_cambia": self.ruta_cambia,
            "pasos_antes": len(self.ruta_antes),
            "pasos_despues": len(self.ruta_despues),
        }


def comparar(antes: Programa, despues: Programa, cal: Calendario) -> Impacto:
    """El impacto de pasar del programa `antes` al programa `despues`, sobre las mismas partidas."""
    movidas = []
    for k, w in antes.ventanas.items():
        di, df = cal.n(despues.ventanas[k].inicio) - cal.n(w.inicio), cal.n(despues.ventanas[k].fin) - cal.n(w.fin)
        if di or df:
            movidas.append(Movida(k, di, df))
    fin_antes = max(w.fin for w in antes.ventanas.values())
    fin_despues = max(w.fin for w in despues.ventanas.values())
    ra, rd = cadena_de_relevos(antes, cal), cadena_de_relevos(despues, cal)
    return Impacto(movidas, fin_antes, fin_despues, cal.n(fin_despues) - cal.n(fin_antes), ra, rd, set(ra) != set(rd))


@dataclass
class Reprogramacion:
    programa: Programa  # el programa con sus fechas nuevas: se puede calcular, dibujar y volver a editar
    resultado: ResultadoCPM
    impacto: Impacto  # contra el programa que se reprogramó
    rechazadas: List[Rechazado]  # ediciones que no se aplican, con su motivo
    incumplidos: List[Tuple[Vinculo, Fraction]]  # los que siguen sin cumplirse tras reprogramar

    # el impacto, a la mano
    @property
    def movidas(self) -> List[Movida]:
        return self.impacto.movidas

    @property
    def fin_antes(self) -> date:
        return self.impacto.fin_antes

    @property
    def fin_despues(self) -> date:
        return self.impacto.fin_despues

    @property
    def dias_de_cambio(self) -> int:
        return self.impacto.dias_de_cambio

    @property
    def ruta_antes(self) -> List[str]:
        return self.impacto.ruta_antes

    @property
    def ruta_despues(self) -> List[str]:
        return self.impacto.ruta_despues

    @property
    def ruta_cambia(self) -> bool:
        return self.impacto.ruta_cambia


def reprogramar(
    prog: Programa,
    cal: Calendario,
    ediciones: Iterable[object] = (),
    modo: str = "empuje",
) -> Reprogramacion:
    """Aplica las ediciones y reprograma.

    `empuje` (por defecto) respeta el plan: cada partida conserva su arranque y solo se corre lo que un
    vínculo, una duración o una fecha editada obliga, por lo mínimo. Sin ediciones, un plan que cumple
    todos sus vínculos queda idéntico. `temprano` suelta el plan y calcula el CPM más temprano de la red
    (con la red mínima de hoy colapsa: ver `PROGRAMA-CPM.md` §4.4).

    Una edición que no se puede aplicar —actividad desconocida, duración inválida, un vínculo repetido o que
    cierra un ciclo— no detiene a las demás: queda en `rechazadas` con su motivo."""
    if modo not in ("empuje", "temprano"):
        raise ValueError("modo: empuje o temprano")
    duraciones = {k: Fraction(cal.n(w.fin) + 1 - cal.n(w.inicio)) for k, w in prog.ventanas.items()}
    anclas: Dict[str, date] = {k: w.inicio for k, w in prog.ventanas.items()} if modo == "empuje" else {}
    vivos: List[Tuple[Vinculo, int, str]] = [(v, 0, "") for v in prog.vinculos]
    origenes: Dict[Vinculo, str] = dict(prog.origenes)
    rechazadas: List[Rechazado] = []

    def no(llave: str, motivo: str, token: str = "") -> None:
        fila = prog.por_llave[llave].fila if llave in prog.por_llave else 0
        rechazadas.append(Rechazado(llave, fila, token, motivo))

    def valido(pred: str, suc: str):
        if suc not in prog.ventanas:
            return "sucesora_no_es_partida" if suc in prog.por_llave else "actividad_desconocida"
        if pred in prog.ventanas:
            return None
        if pred in prog.bloques and prog.bloques[pred]:
            return None
        return "actividad_desconocida" if pred not in prog.por_llave else "predecesora_sin_partidas"

    for e in ediciones:
        if isinstance(e, CambiarDuracion):
            if e.llave not in prog.ventanas:
                no(e.llave, "actividad_desconocida", "duracion")
            elif Fraction(e.dias) <= 0:
                no(e.llave, "duracion_invalida", str(e.dias))
            else:
                duraciones[e.llave] = Fraction(e.dias)
        elif isinstance(e, FijarInicio):
            if e.llave not in prog.ventanas:
                no(e.llave, "actividad_desconocida", "inicio")
            else:
                anclas[e.llave] = cal.siguiente_habil(e.fecha)
        elif isinstance(e, AgregarVinculo):
            token = f"{e.predecesora}{e.tipo}"
            motivo = valido(e.predecesora, e.sucesora)
            if motivo:
                no(e.sucesora, motivo, token)
            elif e.origen is not None and e.origen not in ORIGENES:
                no(e.sucesora, "origen_invalido", token)
            elif e.predecesora == e.sucesora:
                no(e.sucesora, "autovinculo", token)
            else:
                nuevo = Vinculo(e.predecesora, e.sucesora, e.tipo, e.desfase)
                if any(v == nuevo for v, _, _ in vivos):
                    no(e.sucesora, "repetido", token)
                elif _cierra_ciclo(vivos + [(nuevo, 0, "")], prog, cal):
                    no(e.sucesora, "cierra_un_ciclo", token)
                else:
                    vivos.append((nuevo, 0, ""))
                    origenes[nuevo] = e.origen or ORIGEN_POR_OMISION
        elif isinstance(e, QuitarVinculo):
            tipo = None if e.tipo is None else tipo_normal(e.tipo)
            quedan = [t for t in vivos if not (t[0].predecesora == e.predecesora and t[0].sucesora == e.sucesora and (tipo is None or t[0].tipo == tipo))]
            if len(quedan) == len(vivos):
                no(e.sucesora, "vinculo_inexistente", f"{e.predecesora}{e.tipo or ''}")
            for v, _, _ in vivos:
                if all(v != q for q, _, _ in quedan):
                    origenes.pop(v, None)
            vivos = quedan
        elif isinstance(e, CambiarVinculo):
            actual = tipo_normal(e.tipo_actual)
            idx = next((i for i, (v, _, _) in enumerate(vivos) if v.predecesora == e.predecesora and v.sucesora == e.sucesora and v.tipo == actual), None)
            if idx is None:
                no(e.sucesora, "vinculo_inexistente", f"{e.predecesora}{e.tipo_actual}")
            elif e.origen is not None and e.origen not in ORIGENES:
                no(e.sucesora, "origen_invalido", f"{e.predecesora}{e.tipo}")
            else:
                nuevo = Vinculo(e.predecesora, e.sucesora, e.tipo, e.desfase)
                resto = vivos[:idx] + vivos[idx + 1 :]
                if any(v == nuevo for v, _, _ in resto):
                    no(e.sucesora, "repetido", f"{e.predecesora}{e.tipo}")
                elif _cierra_ciclo(resto + [(nuevo, 0, "")], prog, cal):
                    no(e.sucesora, "cierra_un_ciclo", f"{e.predecesora}{e.tipo}")
                else:
                    viejo = vivos[idx][0]
                    origenes[nuevo] = e.origen or origenes.get(viejo) or ORIGEN_POR_OMISION
                    if viejo != nuevo:
                        origenes.pop(viejo, None)
                    vivos = resto[:idx] + [(nuevo, 0, "")] + resto[idx:]
        else:
            raise TypeError(f"edición desconocida: {e!r}")

    vinculos = [v for v, _, _ in vivos]
    usados = {v.predecesora for v in vinculos if v.predecesora in prog.bloques}
    acts = [Actividad(k, duraciones[k], ancla=anclas.get(k)) for k in prog.ventanas]
    acts += [Actividad(b, 0, tuple(prog.bloques[b])) for b in prog.bloques if b in usados]
    arranque = min(w.inicio for w in prog.ventanas.values())
    res = calcular_cpm(acts, vinculos, cal, arranque)
    nuevas = {k: Ventana(res[k].fecha_inicio, res[k].fecha_fin) for k in prog.ventanas}
    nuevo_prog = replace(prog, actividades=acts, vinculos=vinculos, ventanas=nuevas,
                         origenes={v: o for v, o in origenes.items() if v in set(vinculos)})

    return Reprogramacion(
        programa=nuevo_prog,
        resultado=res,
        impacto=comparar(prog, nuevo_prog, cal),
        rechazadas=rechazadas,
        incumplidos=nuevo_prog.incumplidos(cal),
    )


def _cierra_ciclo(vivos, prog: Programa, cal: Calendario) -> bool:
    """¿Esta red tiene un ciclo? Entre partidas, o a través de un bloque (el motor no converge)."""
    directos = [(v.predecesora, v.sucesora) for v, _, _ in vivos if v.predecesora in prog.ventanas]
    if _componente_con_ciclo(directos):
        return True
    try:
        _probar(vivos, prog.ventanas, prog.bloques, cal)
    except CicloError:
        return True
    return False


# --------------------------------------------------------------------------- el Gantt como dato


def vista_gantt(
    prog: Programa,
    cal: Calendario,
    ventana: Optional[Tuple[date, date]] = None,
    relevos: Optional[Sequence[str]] = None,
    niveles_resumen: Sequence[int] = (0, 1, 2, 3),
    resultado: Optional[ResultadoCPM] = None,
    base: Optional[Programa] = None,
    para_editar: bool = False,
) -> Dict[str, object]:
    """Lo que una pantalla necesita para dibujar el Gantt de `PROGRAMA-CPM.md` §8, sin dibujar nada:

    - `filas`: una por partida y una por bloque de los `niveles_resumen`, en el orden del libro. Por
      defecto todos los niveles (capítulo, frente, etapa, nivel 3): el árbol completo, que la pantalla
      pliega y despliega con `padre`. Cada fila lleva su frente y etapa para el color y `critica` si
      está en la cadena de relevos. Zafiro Plus: 388 partidas y 105 resúmenes (90 de Nivel 2 y 3, como
      la imagen de D-432, más los 14 frentes y el capítulo);
    - `flechas`: una por vínculo, desde la partida que fija la fecha de la predecesora (no desde el
      bloque), con su holgura y `incumplido` si las fechas lo contradicen;
    - `marcas`: los fines de semana y feriados que caen dentro del programa y la ventana, si la hay;
    - `ruta_critica_red`: si se pasa el `resultado` del CPM, las partidas de la ruta crítica de la red,
      para que la pantalla pueda marcar una u otra (la cadena de relevos lee el plan; esta lee la red);
    - `base`: si se pasa el programa de antes de una reprogramación, cada fila trae `base_inicio` y
      `base_fin` (la barra fantasma) y `dias_movida`;
    - `red`: si `para_editar`, lo que una pantalla necesita para reprogramar sin el servidor —días hábiles
      numerados, partidas en orden del libro, bloques y vínculos—, con el mismo contrato que
      `reprogramar` (`frontend/gantt/motor_gantt.js` lo implementa y una prueba lo contrasta).
    """
    if relevos is None:
        relevos = cadena_de_relevos(prog, cal)
    critica = set(relevos)

    def ventana_de(p: Programa, f: Fila) -> Optional[Tuple[date, date]]:
        if f.es_partida:
            w = p.ventanas[f.llave]
            return w.inicio, w.fin
        hijos = p.bloques.get(f.llave)
        if not hijos:
            return None
        ws = [p.ventanas[h] for h in hijos]
        return min(w.inicio for w in ws), max(w.fin for w in ws)

    filas = []
    pila: List[Tuple[int, str]] = []  # (nivel, llave) de los resúmenes que ya entraron: el padre es el tope
    for f in prog.filas:
        if not f.es_partida and f.nivel not in niveles_resumen:
            continue
        v = ventana_de(prog, f)
        if v is None:
            continue
        while pila and pila[-1][0] >= f.nivel:
            pila.pop()
        fila = {
            "llave": f.llave,
            "fila": f.fila,
            "nivel": f.nivel,
            "padre": pila[-1][1] if pila else None,
            "clave": f.clave,
            "descripcion": f.descripcion,
            "resumen": not f.es_partida,
            "inicio": v[0].isoformat(),
            "fin": v[1].isoformat(),
            "frente": f.frente,
            "etapa": f.etapa,
            "critica": f.llave in critica,
        }
        if base is not None:
            b = ventana_de(base, f)
            if b is not None:
                fila["base_inicio"], fila["base_fin"] = b[0].isoformat(), b[1].isoformat()
                fila["dias_movida"] = cal.n(v[1]) - cal.n(b[1])
        filas.append(fila)
        if not f.es_partida:
            pila.append((f.nivel, f.llave))
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
                "de_vinculo": v.predecesora,
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
    vista: Dict[str, object] = {
        "filas": filas, "flechas": flechas, "marcas": marcas, "relevos": list(relevos),
        "frentes": frentes, "etapas": etapas, "desde": desde.isoformat(), "hasta": hasta.isoformat(),
        "ruta_critica_red": list(resultado.ruta_critica) if resultado is not None else [],
    }
    if para_editar:
        n0 = cal.n(desde)
        horizonte = cal.n(hasta) - n0 + 260
        vista["red"] = {
            "n0": n0,
            "dias": [cal.fecha(n0 + i).isoformat() for i in range(horizonte)],
            "partidas": [{"k": k, "ini": cal.n(w.inicio) - n0, "fin": cal.n(w.fin) - n0} for k, w in prog.ventanas.items()],
            "conocidas": list(prog.por_llave),
            "bloques": {b: list(h) for b, h in prog.bloques.items() if h},
            "vinculos": [
                {"de": v.predecesora, "a": v.sucesora, "tipo": v.tipo, "desfase": float(v.desfase)} for v in prog.vinculos
            ],
        }
    return vista
