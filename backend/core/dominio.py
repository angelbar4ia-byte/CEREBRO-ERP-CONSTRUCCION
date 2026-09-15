"""
Modelo de dominio del motor de cálculo.

Deriva de `1-mundo/MODELO.md` §1, §1a y §2. No depende de Django ni de
ninguna base concreta: es el dominio de la arquitectura que pide
`2-operacion/skills/erp-construccion.md` §9 — el recorrido del árbol es
infraestructura, la regla de qué suma a qué es dominio.

MODELO.md deja los tipos de columna y el motor para "la siguiente pasada,
una vez aprobada la forma" (última línea del archivo). Este módulo es esa
pasada, para lo ya verificado contra `3-historia/CASO-TRABAJADO.md` y
`2-operacion/INVARIANTES.md` §3.

Trae menos campos que `NODO`/`COMPOSICION` en MODELO.md — procedencia,
modo_cantidad, familia_id, vigencia... No hacen falta para calcular un
importe. Se agregan cuando la capa de persistencia los necesite.
"""
from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from enum import Enum
from typing import Optional


class Rol(str, Enum):
    ENSAMBLE = "ensamble"
    CONCEPTO = "concepto"
    INSUMO = "insumo"
    ESTRUCTURAL = "estructural"


class Categoria(str, Enum):
    MATERIAL = "material"
    MANO_DE_OBRA = "mano_de_obra"
    HERRAMIENTA = "herramienta"
    EQUIPO = "equipo"
    AUXILIAR = "auxiliar"
    FLETE = "flete"
    TRABAJO = "trabajo"
    CONCEPTO = "concepto"


class ModoPrecio(str, Enum):
    CALCULADO = "calculado"
    DECLARADO = "declarado"


class TipoCantidad(str, Enum):
    FIJA = "fija"
    PORCENTAJE = "porcentaje"


class BasePorcentaje(str, Enum):
    SUMA_JORNALES_HERMANOS = "suma_jornales_hermanos"
    ACUMULADO_HASTA_AQUI = "acumulado_hasta_aqui"


@dataclass(frozen=True)
class Nodo:
    """
    Una entidad de catálogo: un insumo, un compuesto, un concepto o un
    nodo estructural.

    `modo_precio=DECLARADO` cubre dos casos reales con el mismo mecanismo
    (MODELO.md no los distingue con un campo aparte): un insumo atómico
    de catálogo, cuyo precio es dato y no se deriva de ninguna matriz
    propia (Varilla 1/2 a $237.52), y un concepto en modo alzado, cuyo
    precio se declara y baja (erp-construccion.md §6). Un nodo sin
    líneas de `COMPOSICION` y sin `modo_precio=DECLARADO` no es un error:
    es una fila placeholder de OPUS, cuyo importe es cero por diseño
    (`INVARIANTES.md` §2, 121 filas verificadas).
    """
    id: int
    clave: str
    descripcion: str
    unidad: str
    rol: Rol
    categoria: Categoria
    modo_precio: ModoPrecio = ModoPrecio.CALCULADO
    precio_declarado: Optional[Decimal] = None

    def __post_init__(self) -> None:
        if self.modo_precio == ModoPrecio.DECLARADO and self.precio_declarado is None:
            raise ValueError(
                f"{self.clave}: modo_precio=declarado exige precio_declarado (MODELO.md §1)"
            )


@dataclass(frozen=True)
class Composicion:
    """
    Una línea de matriz: el padre consume `cantidad` del hijo.

    MODELO.md §1a: "la tabla más importante del modelo — de aquí sale el
    cálculo completo." Tiene identidad propia (`id`, no `(padre_id,
    hijo_id)`) porque el mismo par puede repetirse: alambre recocido en
    `AUX-00001` aparece dos veces en una misma matriz —amarre de varilla
    y de estribos—, 26 casos verificados.

    `reporta_a` es la categoría a la que ESTA línea suma su monto en la
    lectura superficial (`reporte_montos`) — MODELO.md, hallazgo 1: no
    siempre coincide con la categoría del hijo. `MOC-12010` (Trabajo) es
    Material cuando la línea vive dentro de la matriz de la zapata.
    """
    id: int
    padre_id: int
    hijo_id: int
    cantidad: Decimal
    orden: int
    reporta_a: Categoria
    tipo_cantidad: TipoCantidad = TipoCantidad.FIJA
    base_porcentaje: Optional[BasePorcentaje] = None

    def __post_init__(self) -> None:
        if self.tipo_cantidad == TipoCantidad.PORCENTAJE and self.base_porcentaje is None:
            raise ValueError(
                f"composicion {self.id}: tipo_cantidad=porcentaje exige "
                "base_porcentaje (MODELO.md §1a, hallazgo 4)"
            )
