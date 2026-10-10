"""
El motor del CPM — `1-mundo/PROGRAMA-CPM.md` y `1-mundo/MODELO.md` §5c, hechos
funciones puras.

No conoce Django ni PostgreSQL: recibe actividades, vínculos y un calendario, y
devuelve fechas, holguras y la ruta crítica. Nada se guarda aquí: las fechas
tempranas y tardías, la holgura y `es_ruta_critica` son caché del motor, nunca
fuente de verdad (MODELO.md §5c).

Convención de instantes (D-445). Un plan de días hábiles completos abre cada
tramo al empezar su primer día y lo cierra al terminar el último: el inicio del
día hábil `d` es el instante `n(d)` y su fin es `n(d) + 1`. Un tramo de `D` días
que arranca en el instante `S` termina en `S + D`. Con eso las cuatro holguras
son:

    fin_inicio    (FS)   abre(s)   - (cierra(p) + desfase)
    inicio_inicio (SS)   abre(s)   - (abre(p)   + desfase)
    fin_fin       (FF)   cierra(s) - (cierra(p) + desfase)
    inicio_fin    (SF)   cierra(s) - (abre(p)   + desfase)

El desfase está en días hábiles; negativo es traslape y positivo es espera.
"""
from __future__ import annotations

import bisect
import math
from dataclasses import dataclass, field
from datetime import date, timedelta
from fractions import Fraction
from typing import Dict, FrozenSet, Iterable, List, Mapping, Optional, Sequence, Tuple

LUNES = date(2000, 1, 3)  # origen de la numeración de días hábiles
TIPOS = ("FS", "SS", "FF", "SF")
ALIAS_TIPO = {
    "fin_inicio": "FS",
    "inicio_inicio": "SS",
    "fin_fin": "FF",
    "inicio_fin": "SF",
}
HORAS_JORNADA = 8
TOLERANCIA_REDONDEO = Fraction(1, 100)


class CicloError(Exception):
    """Las precedencias forman un ciclo: no hay orden posible.

    MODELO.md §5c: se rechazan solo el autovínculo y los ciclos reales (D-443). Cuando el ciclo
    pasa por un bloque como predecesora y el cálculo no converge, `vinculos` trae los vínculos
    que lo forman, para que quien carga el programa decida cuál rechazar.
    """

    def __init__(self, mensaje: str = "", vinculos: Iterable["Vinculo"] = ()) -> None:
        super().__init__(mensaje)
        self.vinculos = tuple(vinculos)


class VinculoInvalido(ValueError):
    """Un vínculo que el modelo no admite: sucesora que es un bloque (D-442),
    actividad desconocida o tipo desconocido."""


def _fr(x) -> Fraction:
    if isinstance(x, Fraction):
        return x
    if isinstance(x, float):
        return Fraction(x).limit_denominator(10_000)
    return Fraction(x)


def tipo_normal(tipo: str) -> str:
    t = ALIAS_TIPO.get(tipo, tipo)
    if t not in TIPOS:
        raise VinculoInvalido(f"tipo de vínculo desconocido: {tipo!r}")
    return t


def desfase_en_dias(horas: float, jornada: int = HORAS_JORNADA) -> Fraction:
    """El formato fuente guarda el desfase en horas (`+120.00000`); la jornada es de 8."""
    return _fr(horas) / jornada


# --------------------------------------------------------------------------- calendario


@dataclass(frozen=True)
class Calendario:
    """`CALENDARIO_OBRA` (MODELO.md §5c, D-428, D-446). Todo cálculo con días
    hábiles pasa por aquí y por ningún otro."""

    dias_laborables_semana: FrozenSet[int] = frozenset({0, 1, 2, 3, 4})  # 0 = lunes
    no_habiles: FrozenSet[date] = frozenset()
    paso_dias: Optional[Fraction] = Fraction(1)  # None = sin redondeo
    sentido_redondeo: str = "cercano"  # cercano · arriba · abajo
    _feriados: Tuple[date, ...] = field(default=(), init=False, repr=False, compare=False)

    def __post_init__(self) -> None:
        if not self.dias_laborables_semana:
            raise ValueError("el calendario necesita al menos un día laborable por semana")
        if self.sentido_redondeo not in ("cercano", "arriba", "abajo"):
            raise ValueError("sentido_redondeo: cercano, arriba o abajo")
        # solo cuentan los no hábiles que caen en un día de trabajo
        efectivos = sorted(d for d in self.no_habiles if d.weekday() in self.dias_laborables_semana)
        object.__setattr__(self, "_feriados", tuple(efectivos))

    def a_dict(self) -> dict:
        """Como se guarda: días de la semana, no hábiles y redondeo, sin objetos."""
        return {
            "dias_laborables_semana": sorted(self.dias_laborables_semana),
            "no_habiles": sorted(d.isoformat() for d in self.no_habiles),
            "paso_dias": None if self.paso_dias is None else str(self.paso_dias),
            "sentido_redondeo": self.sentido_redondeo,
        }

    @classmethod
    def desde_dict(cls, d: dict) -> "Calendario":
        return cls(
            dias_laborables_semana=frozenset(d["dias_laborables_semana"]),
            no_habiles=frozenset(date.fromisoformat(x) for x in d["no_habiles"]),
            paso_dias=None if d["paso_dias"] is None else Fraction(d["paso_dias"]),
            sentido_redondeo=d["sentido_redondeo"],
        )

    @property
    def habiles_por_semana(self) -> int:
        return len(self.dias_laborables_semana)

    def es_habil(self, d: date) -> bool:
        return d.weekday() in self.dias_laborables_semana and d not in self.no_habiles

    def n(self, d: date) -> int:
        """Días hábiles anteriores a `d`: es el instante en que abre `d`. Para un
        día que no se trabaja es el instante en que abre el siguiente día hábil."""
        total = (d - LUNES).days
        if total < 0:
            raise ValueError("fecha anterior al origen del calendario")
        semanas, resto = divmod(total, 7)
        cuenta = semanas * self.habiles_por_semana + sum(1 for i in range(resto) if i in self.dias_laborables_semana)
        return cuenta - bisect.bisect_left(self._feriados, d)

    def fecha(self, n: int) -> date:
        """El día hábil número `n` (inverso de `n`)."""
        d = LUNES + timedelta(days=7 * (n // self.habiles_por_semana))
        for _ in range(60):
            if self.es_habil(d) and self.n(d) == n:
                return d
            d += timedelta(days=1) if self.n(d) <= n else -timedelta(days=1)
        raise ArithmeticError("no se encontró el día hábil")  # no debería ocurrir

    def entre(self, a: date, b: date) -> int:
        """`bc(a, b)` de los libros: días hábiles de `a` (incluido) a `b` (excluido)."""
        return self.n(b) - self.n(a)

    def siguiente_habil(self, d: date) -> date:
        while not self.es_habil(d):
            d += timedelta(days=1)
        return d

    # -- duraciones (D-446)

    def acomodar(self, dias_teoricos) -> Fraction:
        """La duración programada: los días teóricos puestos en el paso del
        calendario, nunca menos de un paso. Un múltiplo exacto no se mueve; en
        `arriba` y `abajo` un excedente (o faltante) menor a 0.01 día no sube
        ni baja un paso."""
        dias = _fr(dias_teoricos)
        if dias <= 0:
            return Fraction(0)
        paso = self.paso_dias
        if paso is None:
            return dias
        q = dias / paso
        if q.denominator == 1:
            pasos = int(q)
        elif self.sentido_redondeo == "cercano":
            pasos = math.floor(q + Fraction(1, 2))  # el medio va hacia arriba
        else:
            tol = TOLERANCIA_REDONDEO / paso
            if self.sentido_redondeo == "arriba":
                pasos = math.ceil(q - tol)
            else:
                pasos = math.floor(q + tol)
        return max(pasos, 1) * paso


def dias_teoricos(cantidad, rendimiento, cuadrillas=1) -> Fraction:
    """`cantidad ÷ (rendimiento × cuadrillas)`, fraccionarios y sin redondear (D-446)."""
    return _fr(cantidad) / (_fr(rendimiento) * _fr(cuadrillas))


def cuadrillas_efectivas(cantidad, rendimiento, duracion_programada) -> Fraction:
    """Lo que guarda `TRAMO.cuadrillas`: el redondeo mueve las cuadrillas, no el esfuerzo."""
    return _fr(cantidad) / (_fr(rendimiento) * _fr(duracion_programada))


# --------------------------------------------------------------------------- vínculos


@dataclass(frozen=True)
class Vinculo:
    """`PRECEDENCIA`: `tipo` en FS/SS/FF/SF (o el nombre del enum) y `desfase` en días hábiles."""

    predecesora: str
    sucesora: str
    tipo: str = "FS"
    desfase: Fraction = Fraction(0)

    def __post_init__(self) -> None:
        object.__setattr__(self, "tipo", tipo_normal(self.tipo))
        object.__setattr__(self, "desfase", _fr(self.desfase))


@dataclass(frozen=True)
class Ventana:
    """Primer y último día con trabajo de una partida o de un bloque."""

    inicio: date
    fin: date


def holgura_instantes(tipo: str, desfase, p_abre, p_cierra, s_abre, s_cierra) -> Fraction:
    """Las cuatro holguras de D-445, en instantes."""
    d = _fr(desfase)
    t = tipo_normal(tipo)
    if t == "FS":
        return _fr(s_abre) - (_fr(p_cierra) + d)
    if t == "SS":
        return _fr(s_abre) - (_fr(p_abre) + d)
    if t == "FF":
        return _fr(s_cierra) - (_fr(p_cierra) + d)
    return _fr(s_cierra) - (_fr(p_abre) + d)


def holgura_vinculo(v: Vinculo, pred: Ventana, suc: Ventana, cal: Calendario) -> Fraction:
    """Holgura de un vínculo a partir de las fechas del plan: `bc(fin_p, ini_s) - 1 - desfase`
    para FS, `bc(ini_p, ini_s) - desfase` para SS, `bc(fin_p, fin_s) - desfase` para FF y
    `bc(ini_p, fin_s) + 1 - desfase` para SF. Negativa = el plan no lo cumple."""
    return holgura_instantes(
        v.tipo,
        v.desfase,
        cal.n(pred.inicio),
        cal.n(pred.fin) + 1,
        cal.n(suc.inicio),
        cal.n(suc.fin) + 1,
    )


def ventana_de_bloque(
    descendientes: Iterable[str], fechas: Mapping[str, Ventana], excluir: Optional[str] = None
) -> Optional[Ventana]:
    """La ventana de un bloque como predecesora: el mínimo y el máximo de las fechas de
    sus partidas, **sin la sucesora** («después de lo demás del grupo», D-443).
    `None` si no queda ninguna partida con fechas."""
    ch = [fechas[d] for d in descendientes if d != excluir and d in fechas]
    if not ch:
        return None
    return Ventana(min(w.inicio for w in ch), max(w.fin for w in ch))


def vinculos_incumplidos(
    fechas: Mapping[str, Ventana],
    vinculos: Sequence[Vinculo],
    cal: Calendario,
    bloques: Optional[Mapping[str, Sequence[str]]] = None,
) -> List[Tuple[Vinculo, Fraction]]:
    """Los vínculos cuya holgura es negativa, según las fechas dadas: la lógica de
    `ALERTA(tipo=vinculo_incumplido)`. Sin umbral (D-409): el plan hecho a mano puede no
    pasar por el CPM. `bloques` da, por bloque, sus partidas descendientes."""
    bloques = bloques or {}
    malos: List[Tuple[Vinculo, Fraction]] = []
    for v in vinculos:
        suc = fechas.get(v.sucesora)
        pred = ventana_de_bloque(bloques[v.predecesora], fechas, excluir=v.sucesora) if v.predecesora in bloques else fechas.get(v.predecesora)
        if suc is None or pred is None:
            continue
        h = holgura_vinculo(v, pred, suc, cal)
        if h < 0:
            malos.append((v, h))
    return malos


# --------------------------------------------------------------------------- CPM


@dataclass(frozen=True)
class Actividad:
    """Una partida (con `duracion` en días hábiles) o un bloque (con `hijos`, modo
    `derivada_de_hijos`: sus fechas son el mínimo y el máximo de las de sus partidas
    y solo existe como predecesora, D-442). `ancla` es el disparador contractual:
    la actividad no arranca antes de esa fecha."""

    id: str
    duracion: Fraction = Fraction(0)
    hijos: Tuple[str, ...] = ()
    ancla: Optional[date] = None

    def __post_init__(self) -> None:
        object.__setattr__(self, "duracion", _fr(self.duracion))
        object.__setattr__(self, "hijos", tuple(self.hijos))
        if self.duracion < 0:
            raise ValueError("la duración no puede ser negativa")

    @property
    def es_bloque(self) -> bool:
        return bool(self.hijos)


@dataclass(frozen=True)
class Calculada:
    """Lo que el motor calcula por actividad. Todo es caché."""

    id: str
    inicio_temprano: Fraction  # instantes absolutos de días hábiles
    fin_temprano: Fraction
    inicio_tardio: Fraction
    fin_tardio: Fraction
    holgura: Fraction  # total: inicio tardío - inicio temprano
    es_ruta_critica: bool
    fecha_inicio: date
    fecha_fin: date


@dataclass(frozen=True)
class ResultadoCPM:
    actividades: Dict[str, Calculada]
    origen: Fraction  # instante en que arranca la obra
    fin_proyecto: Fraction  # el último fin temprano
    limite: Fraction  # contra lo que se mide la holgura: el plazo, o el fin si no hay
    ruta_critica: List[str]  # partidas con holgura <= 0, por inicio temprano

    def __getitem__(self, id_: str) -> Calculada:
        return self.actividades[id_]

    @property
    def dias_habiles(self) -> Fraction:
        return self.fin_proyecto - self.origen


def _ciclo_de_causas(movidas: Sequence[str], causa: Mapping[str, Tuple["Vinculo", str]]) -> List["Vinculo"]:
    """Sigue, desde las partidas que aún se movían, quién las empujó: el cuerpo del ciclo que se alarga."""
    for s in movidas:
        visto: Dict[str, int] = {}
        camino: List["Vinculo"] = []
        x = s
        while x not in visto and x in causa:
            visto[x] = len(camino)
            v, x = causa[x]
            camino.append(v)
        if x in visto:
            return camino[visto[x] :]
    return []


def _descendientes(id_: str, por_id: Mapping[str, Actividad], memo: Dict[str, Tuple[str, ...]]) -> Tuple[str, ...]:
    if id_ in memo:
        return memo[id_]
    a = por_id[id_]
    out: List[str] = []
    for h in a.hijos:
        if h not in por_id:
            raise VinculoInvalido(f"el bloque {id_} cita a {h}, que no existe")
        if por_id[h].es_bloque:
            out.extend(_descendientes(h, por_id, memo))
        else:
            out.append(h)
    memo[id_] = tuple(out)
    return memo[id_]


def calcular_cpm(
    actividades: Sequence[Actividad],
    vinculos: Sequence[Vinculo],
    cal: Calendario,
    inicio: date,
    plazo_dias: Optional[object] = None,
) -> ResultadoCPM:
    """Fechas tempranas y tardías, holgura total y ruta crítica.

    - Hacia adelante: cada partida arranca en el primer instante que sus vínculos, su ancla
      y el arranque de la obra permiten (`inicio` se corre al primer día hábil).
    - Un bloque como predecesora actúa por su ventana sin la sucesora (D-443). Como la ventana
      depende de las demás partidas del bloque, que pueden depender a su vez de la sucesora
      (la gualdra y la losa de su grupo), el cálculo es un punto fijo creciente: parte del
      arranque y sube hasta que nada se mueve. Si no converge hay un ciclo real.
    - Hacia atrás contra `limite`: el plazo en días hábiles desde el arranque, o el último fin
      temprano si no hay plazo. Con plazo menor al fin, la holgura sale negativa.
    - Un bloque no tiene holgura propia: la de su partida más apretada.
    Para `inicio_inicio` e `inicio_fin` con un bloque como predecesora, la pasada hacia atrás
    acota a la partida de menor inicio temprano.
    Se rechazan el autovínculo y el ciclo entre partidas (`CicloError`) y una sucesora que es un
    bloque (`VinculoInvalido`, D-442).
    """
    por_id: Dict[str, Actividad] = {}
    for a in actividades:
        if a.id in por_id:
            raise ValueError(f"actividad repetida: {a.id}")
        por_id[a.id] = a
    memo: Dict[str, Tuple[str, ...]] = {}
    desc = {i: _descendientes(i, por_id, memo) for i, a in por_id.items() if a.es_bloque}
    partidas = [a for a in actividades if not a.es_bloque]

    # restricciones al nivel de partida: (partidas de origen, es ventana de bloque, vínculo)
    entrantes: Dict[str, List[Tuple[Tuple[str, ...], bool, Vinculo]]] = {a.id: [] for a in partidas}
    directos: Dict[str, set] = {a.id: set() for a in partidas}
    for v in vinculos:
        if v.predecesora not in por_id or v.sucesora not in por_id:
            raise VinculoInvalido(f"vínculo con actividad desconocida: {v.predecesora} -> {v.sucesora}")
        if por_id[v.sucesora].es_bloque:
            raise VinculoInvalido(f"la sucesora {v.sucesora} es un bloque; siempre es una partida (D-442)")
        if v.predecesora == v.sucesora:
            raise CicloError(f"autovínculo en {v.sucesora}")
        if por_id[v.predecesora].es_bloque:
            orig = tuple(d for d in desc[v.predecesora] if d != v.sucesora)
            if not orig:
                continue  # el bloque se reduce a la sucesora: no hay nada que ordenar
            entrantes[v.sucesora].append((orig, True, v))
        else:
            entrantes[v.sucesora].append(((v.predecesora,), False, v))
            directos[v.sucesora].add(v.predecesora)

    # ciclo entre partidas (vínculos directos) y orden de barrido
    salientes: Dict[str, set] = {a.id: set() for a in partidas}
    for s, ps in directos.items():
        for o in ps:
            salientes[o].add(s)
    pendientes = {s: len(ps) for s, ps in directos.items()}
    cola = [a.id for a in partidas if pendientes[a.id] == 0]
    orden: List[str] = []
    while cola:
        x = cola.pop(0)
        orden.append(x)
        for s in sorted(salientes[x], key=str):
            pendientes[s] -= 1
            if pendientes[s] == 0:
                cola.append(s)
    if len(orden) != len(partidas):
        atoradas = sorted((s for s, n in pendientes.items() if n > 0), key=str)
        raise CicloError("ciclo entre las precedencias de: " + ", ".join(str(x) for x in atoradas[:8]))

    origen = Fraction(cal.n(cal.siguiente_habil(inicio)))
    D = {a.id: a.duracion for a in partidas}
    ES: Dict[str, Fraction] = {}
    for a in partidas:
        piso = origen
        if a.ancla is not None:
            piso = max(piso, Fraction(cal.n(a.ancla)))
        ES[a.id] = piso
    EF: Dict[str, Fraction] = {i: ES[i] + D[i] for i in ES}

    maxbarridos = len(partidas) + 5
    causa: Dict[str, Tuple[Vinculo, str]] = {}  # quién subió el arranque de cada partida, por último
    for _ in range(maxbarridos):
        cambio = False
        movidas: List[str] = []
        for s in orden:
            piso = ES[s]
            for orig, _, v in entrantes[s]:
                p_abre = min(ES[o] for o in orig)
                p_cierra = max(EF[o] for o in orig)
                if v.tipo == "FS":
                    c = p_cierra + v.desfase
                elif v.tipo == "SS":
                    c = p_abre + v.desfase
                elif v.tipo == "FF":
                    c = p_cierra + v.desfase - D[s]
                else:  # SF
                    c = p_abre + v.desfase - D[s]
                if c > piso:
                    piso = c
                    o_fija = max(orig, key=lambda o: EF[o]) if v.tipo in ("FS", "FF") else min(orig, key=lambda o: ES[o])
                    fija = (v, o_fija)
            if piso > ES[s]:
                ES[s] = piso
                EF[s] = piso + D[s]
                causa[s] = fija
                movidas.append(s)
                cambio = True
        if not cambio:
            break
    else:
        raise CicloError("las precedencias no convergen: hay un ciclo que se alarga", _ciclo_de_causas(movidas, causa))

    fin = max(EF.values()) if EF else origen
    limite = origen + _fr(plazo_dias) if plazo_dias is not None else fin

    # hacia atrás: punto fijo decreciente desde el límite
    sucesoras: Dict[str, List[Tuple[str, Vinculo]]] = {a.id: [] for a in partidas}
    for s, lst in entrantes.items():
        for orig, bloque, v in lst:
            if bloque and v.tipo in ("SS", "SF"):
                minimo = min(ES[o] for o in orig)  # la ventana arranca donde arranca la primera
                afectadas = [o for o in orig if ES[o] == minimo]
            else:
                afectadas = list(orig)
            for o in afectadas:
                sucesoras[o].append((s, v))
    LF: Dict[str, Fraction] = {a.id: limite for a in partidas}
    for _ in range(maxbarridos):
        cambio = False
        for p in reversed(orden):
            lf = LF[p]
            for s, v in sucesoras[p]:
                ls_s = LF[s] - D[s]
                if v.tipo == "FS":
                    c = ls_s - v.desfase
                elif v.tipo == "SS":
                    c = ls_s - v.desfase + D[p]
                elif v.tipo == "FF":
                    c = LF[s] - v.desfase
                else:  # SF
                    c = LF[s] - v.desfase + D[p]
                if c < lf:
                    lf = c
            if lf < LF[p]:
                LF[p] = lf
                cambio = True
        if not cambio:
            break
    else:
        raise CicloError("las precedencias no convergen hacia atrás")

    res: Dict[str, Calculada] = {}

    def fechas(es: Fraction, ef: Fraction, dur: Fraction) -> Tuple[date, date]:
        fi = cal.fecha(math.floor(es))
        ff = cal.fecha(max(math.ceil(ef) - 1, math.floor(es))) if dur > 0 else fi
        return fi, ff

    for p in partidas:
        ls = LF[p.id] - D[p.id]
        h = ls - ES[p.id]
        fi, ff = fechas(ES[p.id], EF[p.id], D[p.id])
        res[p.id] = Calculada(p.id, ES[p.id], EF[p.id], ls, LF[p.id], h, h <= 0, fi, ff)
    for b, hijos in desc.items():
        if not hijos:
            continue
        es = min(res[h].inicio_temprano for h in hijos)
        ef = max(res[h].fin_temprano for h in hijos)
        ls = min(res[h].inicio_tardio for h in hijos)
        lf = max(res[h].fin_tardio for h in hijos)
        h_min = min(res[h].holgura for h in hijos)
        fi, ff = fechas(es, ef, ef - es)
        res[b] = Calculada(b, es, ef, ls, lf, h_min, h_min <= 0, fi, ff)

    critica = sorted((p.id for p in partidas if res[p.id].es_ruta_critica), key=lambda i: (res[i].inicio_temprano, str(i)))
    return ResultadoCPM(res, origen, fin, limite, critica)


# --------------------------------------------------------------------------- retraso (D-456, D-457)


def dias_de_atraso(curva_acumulada: Sequence[float], t: int, avance: float, eps: float = 1e-9) -> int:
    """Tiempo ganado: cuántos días hábiles lleva el plan por delante de lo ejecutado. Hoy (día
    hábil `t` de la obra, contado desde 0) menos el último día en que el plan estaba en el avance
    ejecutado. `curva_acumulada[i]` es la fracción programada acumulada al cierre del día `i`.
    Cero si el plan no va por delante: el retraso es real desde un día hábil (D-457)."""
    if curva_acumulada[t] <= avance + eps:
        return 0
    ultimo = -1
    for i in range(t + 1):
        if curva_acumulada[i] <= avance + eps:
            ultimo = i
    return t - ultimo


def retraso_neto(planeado: float, ejecutado: float, ingenieria: float) -> float:
    """(planeado - ejecutado) × ingeniería: positivo es retraso, negativo adelanto (D-457)."""
    return (planeado - ejecutado) * ingenieria
