"""
La carga desde OPUS — `CONOCIMIENTO.md` §2.4 (qué columnas se necesitan de verdad), §2.5 (las filas placeholder) y los
primeros pasos de §2.9: **se lee el archivo, se compara contra lo vigente y se muestra el diagnóstico. No se escribe nada.**

Los archivos son los de `1-mundo/opus/`: `CATALOGO_DE_PRESUPUESTO` (el árbol y las cantidades) y
`ANALISIS_DE_BASICOS_CONCEPTOS` (las matrices: de cada concepto, de cada compuesto y de cada cuadrilla). El archivo de
compuestos (`ANALISIS_DE_BASICOS_COMPUESTOS`) ya viene dentro del de conceptos —son las líneas con `Origen = Material`, las
267, idénticas—; se acepta aparte por si algún día llega solo.

Qué hace con lo que lee, y qué no:
- **No busca columnas por posición ni por nombre exacto**: lleva una tabla de alias y dice, antes de cargar nada, qué leyó
  como qué, qué descartó a propósito (`Ingenieria ERP`, `Nivel ERP`: se generan al exportar, no se importan) y qué no
  reconoció. Si falta una de las cuatro obligatorias —`Nivel`, `Clave`, `Cantidad`, `Tipo`— **la carga no procede**.
- **El árbol sale de `Nivel` y del orden de las filas**, y el WBS se calcula aquí, por posición. `Indice` no arma nada: es la
  suma de control, y se comprueba.
- **Los placeholders** (sin clave y sin descripción) se descartan **solo si se verifica** que su importe es cero y que no
  tienen descendientes con clave. Si alguno no pasa, se queda y se reporta: es un error, no una fila que se tira en silencio.
- **Los números se leen estrictos.** `1,842,426.01` es mil ochocientos millones con centavos; `1,5` no es un número que este
  archivo traiga, y si llegara sería un error y no un quince.
- **La huella de un concepto** es `f(unidad, insumos, cantidades)` y deja fuera la descripción y los precios: una corrección
  de acento no versiona nada, y un precio movido no es un cambio de matriz.

Lo que arma para el motor de cálculo (`motor_calculo.py`) son nodos y líneas de `dominio.py`, con lo mínimo que hace falta para
calcular un precio: lo demás de `NODO` y `COMPOSICION` (procedencia, familia, vigencia…) llega con la persistencia.
"""
from __future__ import annotations

import csv
import hashlib
import io
import re
import unicodedata
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from decimal import Decimal, InvalidOperation
from typing import Dict, Iterable, List, Mapping, Optional, Sequence, Tuple

from .dominio import BasePorcentaje, Categoria, Composicion, ModoPrecio, Nodo, Rol, TipoCantidad
from .motor_calculo import ArbolEnMemoria

# --------------------------------------------------------------------------- lo que el archivo debe traer

ALIAS_PRESUPUESTO: Mapping[str, Tuple[str, ...]] = {
    "nivel": ("nivel", "nv", "profundidad"),
    "clave": ("clave", "codigo", "clave concepto"),
    "cantidad": ("cantidad", "cant", "volumen"),
    "tipo": ("tipo", "clase"),
    "descripcion": ("descripcion",),
    "unidad": ("unidad",),
    "indice": ("indice",),
    "precio_unitario": ("precio unitario", "pu"),
    "total": ("total",),
    "origen": ("origen",),
}
OBLIGATORIAS_PRESUPUESTO = ("nivel", "clave", "cantidad", "tipo")
# se conocen y no se importan (§2.4): se generan al exportar, se derivan, o vienen del APU y del catálogo de conceptos
DESCARTADAS_PRESUPUESTO = (
    "nivel erp", "ingenieria erp", "%", "descripcion de matriz", "unidad de matriz", "descripcion corta", "ruta parametrica",
)

ALIAS_MATRIZ: Mapping[str, Tuple[str, ...]] = {
    "padre": ("clave padre", "padre"),
    "hijo": ("clave hijo", "hijo"),
    "descripcion": ("descripcion",),
    "unidad": ("unidad",),
    "cantidad": ("cantidad", "cant"),
    "costo": ("costo",),
    "importe": ("importe",),
    "tipo": ("tipo",),
    "origen": ("origen",),
}
OBLIGATORIAS_MATRIZ = tuple(ALIAS_MATRIZ)

TIPOS_ESTRUCTURALES = ("Capítulo", "Subcapítulo", "Nivel 2", "Nivel 3")
TIPO_CONCEPTO = "Concepto"
CATEGORIA_DE_TIPO = {
    "Material": Categoria.MATERIAL,
    "ManoDeObra": Categoria.MANO_DE_OBRA,
    "Contrato": Categoria.TRABAJO,
    "Flete": Categoria.FLETE,
}
UNIDAD_PORCENTAJE_MO = "(%)mo"  # la línea de «Contratista»: 10 % de los jornales de la cuadrilla (erp-construccion.md §2)
TOLERANCIA_DE_IMPORTE = Decimal("0.01")


class CargaNoProcede(ValueError):
    """El archivo no se puede leer como lo que dice ser: se dice por qué, con la línea, y no se carga nada."""

    def __init__(self, mensaje: str, informe: Optional["InformeDeMapeo"] = None) -> None:
        super().__init__(mensaje)
        self.informe = informe


@dataclass(frozen=True)
class InformeDeMapeo:
    """Antes de cargar nada: qué columna del archivo se leyó como qué campo (§2.4)."""

    leidas: Mapping[str, str]  # campo → el nombre de la columna tal como vino
    descartadas: Tuple[str, ...]  # las que se saben y no se importan
    sin_reconocer: Tuple[str, ...]
    faltan: Tuple[str, ...]  # obligatorias que no están


# --------------------------------------------------------------------------- leer texto


def _normal(s: str) -> str:
    s = unicodedata.normalize("NFD", s)
    return " ".join("".join(c for c in s if unicodedata.category(c) != "Mn").casefold().split())


_NUMERO = re.compile(r"^-?\d{1,3}(,\d{3})+(\.\d+)?$|^-?\d+(\.\d+)?$")


def _numero(texto: str, donde: str) -> Optional[Decimal]:
    """`1,842,426.01` y `$20.68` sí; `1,5` no: una coma que no separa miles no se adivina."""
    t = texto.strip().replace("$", "").replace(" ", "")
    if not t:
        return None
    if not _NUMERO.match(t):
        raise CargaNoProcede(f"{donde}: «{texto}» no es un número como los de este archivo (1,234.56)")
    return Decimal(t.replace(",", ""))


def _tabla(texto: str) -> Tuple[List[str], List[Tuple[int, List[str]]]]:
    texto = texto.lstrip("﻿")
    if not texto.strip():
        raise CargaNoProcede("el archivo está vacío")
    primera = texto.split("\n", 1)[0]
    lector = csv.reader(io.StringIO(texto, newline=""), delimiter=";" if primera.count(";") > primera.count(",") else ",")
    try:
        encabezados = next(lector)
        filas = [(lector.line_num, fila) for fila in lector if any(c.strip() for c in fila)]
    except csv.Error as e:
        raise CargaNoProcede(f"línea {lector.line_num}: el archivo no se puede leer como CSV ({e})") from None
    return encabezados, filas


def _mapear(
    encabezados: Sequence[str], alias: Mapping[str, Tuple[str, ...]], obligatorias: Sequence[str], descartadas: Sequence[str] = ()
) -> Tuple[Dict[str, int], InformeDeMapeo]:
    por_alias = {a: campo for campo, als in alias.items() for a in als}
    columnas: Dict[str, int] = {}
    leidas: Dict[str, str] = {}
    descartadas_vistas: List[str] = []
    sin_reconocer: List[str] = []
    for i, enc in enumerate(encabezados):
        n = _normal(enc)
        campo = por_alias.get(n)
        if campo is None:
            (descartadas_vistas if n in descartadas else sin_reconocer).append(enc)
        elif campo in columnas:
            if campo in obligatorias:
                raise CargaNoProcede(f"la columna «{enc}» aparece dos veces ({campo}): no se sabe cuál leer, y por nombre no se decide")
            sin_reconocer.append(enc)
        else:
            columnas[campo], leidas[campo] = i, enc
    faltan = tuple(c for c in obligatorias if c not in columnas)
    informe = InformeDeMapeo(leidas, tuple(descartadas_vistas), tuple(sin_reconocer), faltan)
    if faltan:
        raise CargaNoProcede(f"al archivo le faltan columnas obligatorias: {', '.join(faltan)}", informe)
    return columnas, informe


# --------------------------------------------------------------------------- el presupuesto


@dataclass(frozen=True)
class FilaPresupuesto:
    posicion: int  # el lugar en el archivo: junto con `nivel` reconstruye la jerarquía
    linea: int
    tipo: str
    nivel: int
    clave: str
    descripcion: str
    unidad: str
    cantidad: Optional[Decimal]
    precio_observado: Optional[Decimal]  # señal, nunca fuente (§2.4): si no coincide con el calculado, la explosión cambió
    padre: Optional[int]  # posición del padre
    wbs: str  # por posición, entre las filas que se quedan; vacío en las descartadas

    @property
    def es_concepto(self) -> bool:
        return self.tipo == TIPO_CONCEPTO


@dataclass(frozen=True)
class LecturaPresupuesto:
    informe: InformeDeMapeo
    filas: Tuple[FilaPresupuesto, ...]  # las que se quedan, en el orden del archivo
    descartadas: Tuple[FilaPresupuesto, ...]  # los placeholders verificados
    problemas: Tuple[str, ...]  # lo que no cuadró: un placeholder con contenido, un salto de nivel, un `Indice` fuera de orden…
    por_tipo: Mapping[str, Tuple[int, int]]  # tipo → (con hijos, sin hijos), sobre todas las filas, como se leyeron
    conceptos: Mapping[str, Tuple[FilaPresupuesto, ...]]  # clave → sus apariciones: un concepto se repite en varios niveles

    @property
    def limpia(self) -> bool:
        return not self.problemas

    def unidad_de(self, clave: str) -> str:
        return next((f.unidad for f in self.conceptos.get(clave, ()) if f.unidad), "")


def leer_presupuesto(texto: str) -> LecturaPresupuesto:
    encabezados, filas_csv = _tabla(texto)
    col, informe = _mapear(encabezados, ALIAS_PRESUPUESTO, OBLIGATORIAS_PRESUPUESTO, DESCARTADAS_PRESUPUESTO)

    def celda(fila: List[str], campo: str) -> str:
        i = col.get(campo)
        return fila[i].strip() if i is not None and i < len(fila) else ""

    crudas: List[FilaPresupuesto] = []
    totales: Dict[int, Optional[Decimal]] = {}
    indices: Dict[int, Optional[int]] = {}
    problemas: List[str] = []
    pila: List[int] = []  # posiciones, de la raíz a la fila anterior
    for pos, (n, fila) in enumerate(filas_csv):
        donde = f"línea {n}"
        try:
            nivel = int(celda(fila, "nivel"))
        except ValueError:
            raise CargaNoProcede(f"{donde}: «Nivel» debe ser un número entero, no «{celda(fila, 'nivel')}»", informe) from None
        if nivel < 0:
            raise CargaNoProcede(f"{donde}: «Nivel» no puede ser negativo", informe)
        tipo = celda(fila, "tipo")
        if not tipo:
            raise CargaNoProcede(f"{donde}: la fila no trae «Tipo», y sin él un agrupador vacío no se distingue de un concepto", informe)
        while pila and crudas[pila[-1]].nivel >= nivel:
            pila.pop()
        padre = pila[-1] if pila else None
        if padre is not None and nivel > crudas[padre].nivel + 1:
            problemas.append(f"{donde}: salta del nivel {crudas[padre].nivel} al {nivel}")
        elif padre is None and pos > 0 and nivel != 0:
            problemas.append(f"{donde}: no tiene a quién colgarse (nivel {nivel} sin un nivel menor antes)")
        cantidad = _numero(celda(fila, "cantidad"), f"{donde}, «Cantidad»")
        precio = _numero(celda(fila, "precio_unitario"), f"{donde}, «Precio unitario»") if "precio_unitario" in col else None
        totales[pos] = _numero(celda(fila, "total"), f"{donde}, «Total»") if "total" in col else None
        indices[pos] = int(celda(fila, "indice")) if celda(fila, "indice").isdigit() else None
        crudas.append(FilaPresupuesto(pos, n, tipo, nivel, celda(fila, "clave"), celda(fila, "descripcion"), celda(fila, "unidad"),
                                      cantidad, precio, padre, ""))
        pila.append(pos)

    # el `Indice` es el lugar entre los hermanos: si no coincide, se perdieron filas o se reordenaron
    hermanos: Dict[Optional[int], int] = defaultdict(int)
    for f in crudas:
        hermanos[f.padre] += 1
        if "indice" in col and indices[f.posicion] != hermanos[f.padre]:
            problemas.append(f"línea {f.linea}: «Indice» es {indices[f.posicion]} y por su lugar entre los hermanos debería ser {hermanos[f.padre]}")

    con_hijos = {f.padre for f in crudas if f.padre is not None}
    por_tipo: Dict[str, List[int]] = defaultdict(lambda: [0, 0])
    for f in crudas:
        por_tipo[f.tipo][0 if f.posicion in con_hijos else 1] += 1

    # descendientes con clave de cada fila
    con_clave_debajo = set()
    for f in crudas:
        if f.clave:
            p = f.padre
            while p is not None and p not in con_clave_debajo:
                con_clave_debajo.add(p)
                p = crudas[p].padre

    descartadas, quedan = [], []
    for f in crudas:
        if f.clave or f.descripcion:
            quedan.append(f)
            continue
        total = totales[f.posicion]
        if total:
            problemas.append(f"línea {f.linea}: es un placeholder (sin clave ni descripción) pero trae un total de {total}; no se descarta")
            quedan.append(f)
        elif f.posicion in con_clave_debajo:
            problemas.append(f"línea {f.linea}: es un placeholder (sin clave ni descripción) pero tiene descendientes con clave; no se descarta")
            quedan.append(f)
        else:
            descartadas.append(f)

    # el WBS por posición, entre las que se quedan
    wbs: Dict[int, str] = {}
    hijos_contados: Dict[Optional[int], int] = defaultdict(int)
    finales: List[FilaPresupuesto] = []
    for f in quedan:
        hijos_contados[f.padre] += 1
        mio = str(hijos_contados[f.padre])
        wbs[f.posicion] = f"{wbs[f.padre]}.{mio}" if f.padre is not None else mio
        finales.append(FilaPresupuesto(**{**f.__dict__, "wbs": wbs[f.posicion]}))

    conceptos: Dict[str, List[FilaPresupuesto]] = defaultdict(list)
    for f in finales:
        if f.es_concepto and f.clave:
            conceptos[f.clave].append(f)
    return LecturaPresupuesto(
        informe, tuple(finales), tuple(descartadas), tuple(problemas),
        {t: (v[0], v[1]) for t, v in por_tipo.items()}, {k: tuple(v) for k, v in conceptos.items()},
    )


# --------------------------------------------------------------------------- las matrices


@dataclass(frozen=True)
class LineaDeMatriz:
    linea: int
    padre: str
    hijo: str
    descripcion: str
    unidad: str  # la del hijo
    cantidad: Decimal
    costo: Decimal  # el del hijo; en la línea `(%)mo`, la base de jornales sobre la que se saca el porcentaje
    importe: Decimal
    tipo: str  # Material · ManoDeObra · Contrato · Flete
    origen: str  # de qué clase es el padre: Concepto · Material (un compuesto) · ManoDeObra (una cuadrilla)

    @property
    def es_porcentaje_mo(self) -> bool:
        return self.unidad == UNIDAD_PORCENTAJE_MO

    def clave_de_igualdad(self) -> Tuple:
        return (self.padre, self.hijo, self.cantidad, self.costo, self.importe, self.tipo)


@dataclass(frozen=True)
class Matrices:
    informe: InformeDeMapeo
    lineas: Tuple[LineaDeMatriz, ...]
    por_padre: Mapping[str, Tuple[LineaDeMatriz, ...]]  # en el orden del archivo: el orden es el de la matriz
    importes_que_no_cuadran: Tuple[LineaDeMatriz, ...]  # cantidad × costo no da el importe (±1 centavo)
    solo_en_compuestos: int  # líneas del archivo de compuestos que el de conceptos no traía

    def padres_de_origen(self, origen: str) -> Tuple[str, ...]:
        return tuple(dict.fromkeys(l.padre for l in self.lineas if l.origen == origen))


def _leer_lineas(texto: str) -> Tuple[InformeDeMapeo, List[LineaDeMatriz]]:
    encabezados, filas = _tabla(texto)
    col, informe = _mapear(encabezados, ALIAS_MATRIZ, OBLIGATORIAS_MATRIZ)
    out: List[LineaDeMatriz] = []
    for n, fila in filas:
        def celda(campo: str) -> str:
            i = col[campo]
            return fila[i].strip() if i < len(fila) else ""

        donde = f"línea {n}"
        numeros = {c: _numero(celda(c), f"{donde}, «{c}»") for c in ("cantidad", "costo", "importe")}
        vacios = [c for c, v in numeros.items() if v is None]
        if vacios or not celda("padre") or not celda("hijo"):
            raise CargaNoProcede(f"{donde}: la línea no trae padre, hijo, cantidad, costo e importe completos", informe)
        if celda("tipo") not in CATEGORIA_DE_TIPO:
            raise CargaNoProcede(f"{donde}: «Tipo» es «{celda('tipo')}» y debe ser uno de: {', '.join(CATEGORIA_DE_TIPO)}", informe)
        out.append(LineaDeMatriz(n, celda("padre"), celda("hijo"), celda("descripcion"), celda("unidad"), numeros["cantidad"],
                                 numeros["costo"], numeros["importe"], celda("tipo"), celda("origen")))
    return informe, out


def leer_matrices(conceptos: str, compuestos: Optional[str] = None) -> Matrices:
    informe, lineas = _leer_lineas(conceptos)
    extra = 0
    if compuestos is not None:
        _, otras = _leer_lineas(compuestos)
        ya = Counter(l.clave_de_igualdad() for l in lineas if l.origen == "Material")
        for l in otras:
            if ya[l.clave_de_igualdad()] > 0:
                ya[l.clave_de_igualdad()] -= 1
            else:
                lineas.append(l)
                extra += 1
    por_padre: Dict[str, List[LineaDeMatriz]] = defaultdict(list)
    for l in lineas:
        por_padre[l.padre].append(l)
    mal = tuple(l for l in lineas if abs(l.cantidad * l.costo - l.importe) > TOLERANCIA_DE_IMPORTE and not l.es_porcentaje_mo)
    return Matrices(informe, tuple(lineas), {k: tuple(v) for k, v in por_padre.items()}, mal, extra)


# --------------------------------------------------------------------------- para el motor de cálculo


@dataclass(frozen=True)
class ArbolOpus:
    repo: ArbolEnMemoria
    id_de: Mapping[str, int]
    problemas: Tuple[str, ...]  # un insumo con dos costos distintos, que el motor no puede representar como un precio

    def nodo(self, clave: str) -> Nodo:
        return self.repo.nodo(self.id_de[clave])


def armar_arbol(matrices: Matrices, unidades: Optional[Mapping[str, str]] = None) -> ArbolOpus:
    """Un nodo por cada clave que aparece como padre o como hijo, y una línea de composición por cada línea de matriz.

    - Un padre se **calcula** de su matriz; un hijo sin matriz es un insumo con el **precio que traía la línea**.
    - La unidad de un hijo es la de sus líneas; la de un concepto sale de `unidades` (el presupuesto).
    - Una línea `(%)mo` es un porcentaje sobre la suma de jornales de las demás líneas de su cuadrilla, no una cantidad."""
    unidades = unidades or {}
    padres = {l.padre: l.origen for l in reversed(matrices.lineas)}  # el origen de la primera aparición
    unidad_hijo = {l.hijo: l.unidad for l in reversed(matrices.lineas)}
    texto_hijo = {l.hijo: l.descripcion for l in reversed(matrices.lineas)}
    claves = list(dict.fromkeys([l.padre for l in matrices.lineas] + [l.hijo for l in matrices.lineas]))
    id_de = {c: i for i, c in enumerate(claves, start=1)}
    problemas: List[str] = []

    costos: Dict[str, Dict[Decimal, int]] = defaultdict(dict)
    for l in matrices.lineas:
        if not l.es_porcentaje_mo and l.hijo not in padres:
            costos[l.hijo].setdefault(l.costo, l.linea)
    for clave, vistos in costos.items():
        if len(vistos) > 1:
            problemas.append(f"{clave}: trae {len(vistos)} costos distintos ({', '.join(str(c) for c in sorted(vistos))}) y un insumo tiene un precio")

    tipo_de: Dict[str, str] = {}
    for l in matrices.lineas:
        tipo_de.setdefault(l.hijo, l.tipo)
    nodos: Dict[int, Nodo] = {}
    for clave in claves:
        i = id_de[clave]
        unidad = unidad_hijo.get(clave) or unidades.get(clave, "")
        if clave in padres:
            origen = padres[clave]
            rol, categoria = {
                "Concepto": (Rol.CONCEPTO, Categoria.CONCEPTO),
                "Material": (Rol.INSUMO, Categoria.AUXILIAR),
                "ManoDeObra": (Rol.ENSAMBLE, Categoria.MANO_DE_OBRA),
            }.get(origen, (Rol.CONCEPTO, Categoria.CONCEPTO))
            nodos[i] = Nodo(i, clave, texto_hijo.get(clave, ""), unidad, rol, categoria)
        else:
            precio = next(iter(costos[clave]), Decimal("0"))  # un `(%)mo` no tiene precio propio: vale por su porcentaje
            nodos[i] = Nodo(i, clave, texto_hijo[clave], unidad, Rol.INSUMO, CATEGORIA_DE_TIPO[tipo_de[clave]], ModoPrecio.DECLARADO, precio)
    composicion: List[Composicion] = []
    for padre, lineas in matrices.por_padre.items():
        for orden, l in enumerate(lineas, start=1):
            porcentaje = l.es_porcentaje_mo
            composicion.append(Composicion(
                len(composicion) + 1, id_de[padre], id_de[l.hijo], l.cantidad, orden, CATEGORIA_DE_TIPO[l.tipo],
                TipoCantidad.PORCENTAJE if porcentaje else TipoCantidad.FIJA,
                BasePorcentaje.SUMA_JORNALES_HERMANOS if porcentaje else None,
            ))
    return ArbolOpus(ArbolEnMemoria(nodos, composicion), id_de, tuple(problemas))


# --------------------------------------------------------------------------- la huella y el diagnóstico (§2.7 y §2.9)


def huella(unidad: str, lineas: Iterable[Tuple[str, Decimal]]) -> str:
    """`f(unidad, insumos, cantidades)`: sin la descripción, sin los precios y sin el orden de las líneas.

    `1.050000` y `1.05` son la misma cantidad; una línea repetida (el alambre de `AUX-00001`) cuenta dos veces."""
    canon = "\n".join(sorted(f"{hijo}|{format(cantidad.normalize(), 'f')}" for hijo, cantidad in lineas))
    return hashlib.sha256(f"{unidad.strip().casefold()}\n{canon}".encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class CatalogoLeido:
    """Lo que de un archivo hace falta para compararlo con lo vigente: la unidad y la huella de cada matriz."""

    unidad: Mapping[str, str]
    huella: Mapping[str, str]
    sin_matriz: Tuple[str, ...]  # conceptos del presupuesto que no traen matriz en el archivo (P-09)


def catalogo_leido(matrices: Matrices, presupuesto: Optional[LecturaPresupuesto] = None) -> CatalogoLeido:
    unidad_hijo = {l.hijo: l.unidad for l in matrices.lineas}
    unidad: Dict[str, str] = {}
    hue: Dict[str, str] = {}
    for padre, lineas in matrices.por_padre.items():
        u = (presupuesto.unidad_de(padre) if presupuesto is not None else "") or unidad_hijo.get(padre, "")
        unidad[padre] = u
        hue[padre] = huella(u, ((l.hijo, l.cantidad) for l in lineas))
    sin = tuple(c for c in (presupuesto.conceptos if presupuesto is not None else ()) if c not in matrices.por_padre)
    return CatalogoLeido(unidad, hue, sin)


@dataclass(frozen=True)
class Detenido:
    clave: str
    unidad_vigente: str
    unidad_nueva: str


@dataclass(frozen=True)
class Diagnostico:
    """§2.9: lo que se detiene no es la carga sino los conceptos en conflicto; el resto entra normal."""

    entran: Tuple[str, ...]  # sin cambios
    nuevos: Tuple[str, ...]  # no estaban
    versionan: Tuple[str, ...]  # cambió su matriz: versión nueva, automática
    detenidos: Tuple[Detenido, ...]  # cambió la unidad: alguien decide
    ausentes: Tuple[str, ...]  # estaban y el archivo nuevo ya no los trae (informativo: no se borran)


def diagnosticar(nuevo: CatalogoLeido, vigente: CatalogoLeido) -> Diagnostico:
    entran, nuevos, versionan, ausentes = [], [], [], []
    detenidos: List[Detenido] = []
    for clave, h in nuevo.huella.items():
        if clave not in vigente.huella:
            nuevos.append(clave)
            continue
        u_antes, u_ahora = vigente.unidad.get(clave, ""), nuevo.unidad.get(clave, "")
        if u_antes and u_ahora and u_antes.casefold() != u_ahora.casefold():
            detenidos.append(Detenido(clave, u_antes, u_ahora))  # la unidad es la peor: deja de ser comparable (§2.7)
        elif h == vigente.huella[clave]:
            entran.append(clave)
        else:
            versionan.append(clave)
    ausentes = [c for c in vigente.huella if c not in nuevo.huella]
    return Diagnostico(tuple(entran), tuple(nuevos), tuple(versionan), tuple(detenidos), tuple(ausentes))
