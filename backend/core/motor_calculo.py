"""
El motor de cálculo — erp-construccion.md §2 y §3, hecho funciones puras
sobre el dominio de `dominio.py`.

No conoce Django ni PostgreSQL: recibe un `RepositorioArbol` (protocolo)
y opera contra él. El recorrido —`ltree`, SQL recursivo, lo que sea— es
infraestructura detrás del puerto; la regla de qué suma a qué es dominio
(erp-construccion.md §9). `ArbolEnMemoria` es el único adaptador hoy; el
de Postgres/Django queda pendiente — es la siguiente pasada, no esta.
"""
from __future__ import annotations

from dataclasses import dataclass
from decimal import ROUND_HALF_UP, Decimal
from typing import Dict, FrozenSet, List, Optional, Protocol

from .dominio import (
    BasePorcentaje,
    Categoria,
    Composicion,
    ModoPrecio,
    Nodo,
    TipoCantidad,
)

CENTAVO = Decimal("0.01")
CLAVE_JORNAL = "JOR"


class CicloError(Exception):
    """Un compuesto se contiene a sí mismo, directa o indirectamente.

    INVARIANTES.md §3: "Ningún compuesto se contiene a sí mismo... si
    falla: recursión infinita en el motor." Esto lo convierte en un
    error explícito en vez de un `RecursionError` sin contexto.
    """


class RepositorioArbol(Protocol):
    """Puerto: lo mínimo que el motor necesita para recorrer un árbol."""

    def nodo(self, nodo_id: int) -> Nodo: ...

    def lineas(self, padre_id: int) -> List[Composicion]:
        """Las líneas de `COMPOSICION` donde `padre_id` es el padre, en orden."""
        ...


@dataclass
class ArbolEnMemoria:
    """Adaptador mínimo para pruebas: nodos y líneas viven en memoria.

    No es el adaptador de producción — ese habla con Postgres/ltree.
    """

    nodos: Dict[int, Nodo]
    composicion: List[Composicion]

    def nodo(self, nodo_id: int) -> Nodo:
        return self.nodos[nodo_id]

    def lineas(self, padre_id: int) -> List[Composicion]:
        return sorted(
            (c for c in self.composicion if c.padre_id == padre_id),
            key=lambda c: c.orden,
        )


def _redondear(monto: Decimal) -> Decimal:
    """A centavos, redondeo comercial.

    Sin este redondeo por línea, la zapata de `CASO-TRABAJADO.md` da
    $1,135.47 en vez de $1,135.48 — un centavo que ya está explicado
    como deriva conocida de OPUS (D-124, `INVARIANTES.md` §4: el PU se
    redondea a centavos antes de multiplicar). Este motor lo reproduce
    a propósito para cuadrar con el catálogo, línea por línea.

    Las CANTIDADES nunca pasan por acá: arrastran hasta doce decimales
    por Excel (erp-construccion.md §9) y son magnitud física, no dinero.
    """
    return monto.quantize(CENTAVO, rounding=ROUND_HALF_UP)


def precio_unitario(
    nodo_id: int,
    repo: RepositorioArbol,
    _visitando: Optional[FrozenSet[int]] = None,
) -> Decimal:
    """Costo de UNA unidad del nodo.

    Declarado si así está marcado (insumo de catálogo, o concepto en
    modo alzado); si no, la suma de su propia matriz —
    erp-construccion.md §2: `importe(compuesto) = Σ importe(hijos)`.
    """
    nodo = repo.nodo(nodo_id)
    if nodo.modo_precio == ModoPrecio.DECLARADO:
        assert nodo.precio_declarado is not None  # Nodo.__post_init__ lo garantiza
        return nodo.precio_declarado

    visitando = _visitando or frozenset()
    if nodo_id in visitando:
        raise CicloError(f"{nodo.clave}: se contiene a sí mismo, directa o indirectamente")
    visitando = visitando | {nodo_id}

    total = Decimal("0")
    for linea in repo.lineas(nodo_id):
        total += _importe_linea(linea, repo, visitando)
    return total


def _importe_linea(
    linea: Composicion, repo: RepositorioArbol, visitando: FrozenSet[int]
) -> Decimal:
    if linea.tipo_cantidad == TipoCantidad.PORCENTAJE:
        base = _base_porcentaje(linea, repo, visitando)
        return _redondear(linea.cantidad * base)
    pu_hijo = precio_unitario(linea.hijo_id, repo, visitando)
    return _redondear(linea.cantidad * pu_hijo)


def _base_porcentaje(
    linea: Composicion, repo: RepositorioArbol, visitando: FrozenSet[int]
) -> Decimal:
    if linea.base_porcentaje == BasePorcentaje.SUMA_JORNALES_HERMANOS:
        # erp-construccion.md §2, "La unidad %MO": la base es la suma de
        # las líneas de jornal del mismo padre. Fija, no acumulativa —
        # las líneas %MO no se afectan entre sí, así que el orden no
        # cambia el resultado (verificado con CUAD-001: $1,880 → $188).
        total = Decimal("0")
        for hermana in repo.lineas(linea.padre_id):
            if hermana.tipo_cantidad == TipoCantidad.PORCENTAJE:
                continue
            if repo.nodo(hermana.hijo_id).unidad == CLAVE_JORNAL:
                total += _importe_linea(hermana, repo, visitando)
        return total
    if linea.base_porcentaje == BasePorcentaje.ACUMULADO_HASTA_AQUI:
        # Pertenece a las capas de sobrecosto — MODELO.md §6 las deja
        # fuera del modelo: "sin datos reales que las usen." Mejor un
        # error explícito que adivinar la regla (constructor-erp.md:
        # "no inventás reglas de negocio; si falta una, la marcás como
        # pendiente").
        raise NotImplementedError(
            "acumulado_hasta_aqui: pendiente de las capas de sobrecosto "
            "(MODELO.md §6) — sin datos reales para verificarlo todavía"
        )
    raise ValueError(f"base_porcentaje no reconocida: {linea.base_porcentaje!r}")


@dataclass(frozen=True)
class LineaExplosion:
    """Una hoja encontrada al explotar un nodo hasta el fondo, con su
    propia naturaleza conservada — erp-construccion.md §3."""

    nodo: Nodo
    cantidad: Optional[Decimal]  # None en líneas %MO: no es cantidad comprable
    importe: Decimal


def explosion(
    nodo_id: int,
    repo: RepositorioArbol,
    cantidad: Decimal = Decimal("1"),
    _visitando: Optional[FrozenSet[int]] = None,
) -> List[LineaExplosion]:
    """Lectura profunda: llega hasta el fondo, cada hoja conserva su
    categoría propia — erp-construccion.md §3.

    `cantidad` es lo acumulado desde la raíz de la explosión: si un
    compuesto se usa 6 veces y él mismo usa 2.76 de un insumo, la hoja
    aparece a 16.56 (6 × 2.76) — verificado contra
    `CASO-TRABAJADO.md` §4.
    """
    visitando = _visitando or frozenset()
    if nodo_id in visitando:
        raise CicloError(f"nodo {nodo_id}: se contiene a sí mismo, directa o indirectamente")
    visitando = visitando | {nodo_id}

    resultado: List[LineaExplosion] = []
    for linea in repo.lineas(nodo_id):
        hijo = repo.nodo(linea.hijo_id)

        if linea.tipo_cantidad == TipoCantidad.PORCENTAJE:
            resultado.append(
                LineaExplosion(
                    nodo=hijo, cantidad=None, importe=_importe_linea(linea, repo, visitando)
                )
            )
            continue

        # Las cantidades no se redondean acá — son magnitud física, no
        # dinero (ver `_redondear`).
        cantidad_acumulada = cantidad * linea.cantidad
        if not repo.lineas(hijo.id):
            importe = _redondear(cantidad_acumulada * precio_unitario(hijo.id, repo, visitando))
            resultado.append(
                LineaExplosion(nodo=hijo, cantidad=cantidad_acumulada, importe=importe)
            )
        else:
            resultado.extend(explosion(hijo.id, repo, cantidad_acumulada, visitando))
    return resultado


def reporte_montos(nodo_id: int, repo: RepositorioArbol) -> Dict[Categoria, Decimal]:
    """Lectura superficial: se detiene en el compuesto y suma a la
    categoría que la propia línea declara (`reporta_a`) —
    erp-construccion.md §3. No baja a los hijos del compuesto: eso es
    trabajo de `explosion()`.
    """
    acumulado: Dict[Categoria, Decimal] = {}
    visitando = frozenset({nodo_id})
    for linea in repo.lineas(nodo_id):
        importe = _importe_linea(linea, repo, visitando)
        acumulado[linea.reporta_a] = acumulado.get(linea.reporta_a, Decimal("0")) + importe
    return acumulado
