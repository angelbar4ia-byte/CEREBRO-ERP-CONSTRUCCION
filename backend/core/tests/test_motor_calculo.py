"""
Pruebas del motor de cálculo, contra datos reales verificados —
constructor-erp.md: "test con datos reales del proyecto, no con
fixtures inventadas."

Toda cifra de este archivo sale de `3-historia/CASO-TRABAJADO.md` o de
`2-operacion/skills/erp-construccion.md` §2 (el ejemplo de CUAD-001).
Ninguna se inventó para la prueba.

Correr con: cd backend && python3 -m unittest discover
"""
import unittest
from decimal import Decimal

from core.dominio import (
    BasePorcentaje,
    Categoria,
    Composicion,
    ModoPrecio,
    Nodo,
    Rol,
    TipoCantidad,
)
from core.motor_calculo import (
    ArbolEnMemoria,
    CicloError,
    explosion,
    precio_unitario,
    reporte_montos,
)


def _insumo(id_, clave, descripcion, unidad, categoria, precio) -> Nodo:
    """Un insumo de catálogo: su precio es dato, no se calcula de una
    matriz propia — MODELO.md §1, modo_precio=declarado."""
    return Nodo(
        id=id_,
        clave=clave,
        descripcion=descripcion,
        unidad=unidad,
        rol=Rol.INSUMO,
        categoria=categoria,
        modo_precio=ModoPrecio.DECLARADO,
        precio_declarado=Decimal(precio),
    )


class PruebaZapata(unittest.TestCase):
    """CASO-TRABAJADO.md §3: la zapata ZA1-000001, $1,135.48, 41% mano
    de obra contratada que aun así reporta 100% como material."""

    def setUp(self):
        self.varilla = _insumo(1, "ACR-00002", "Varilla 1/2", "PZ", Categoria.MATERIAL, "237.52")
        self.alambre = _insumo(2, "ACE-00001", "Alambre recocido", "KG", Categoria.MATERIAL, "24.68")
        self.mo_zapata = _insumo(3, "MOC-12010", "MO Zapata ZA-1", "PZ", Categoria.TRABAJO, "460.00")
        self.zapata = Nodo(
            id=10,
            clave="ZA1-000001",
            descripcion="Zapata ZA-1 1.00x1.00",
            unidad="PZ",
            rol=Rol.INSUMO,
            categoria=Categoria.MATERIAL,
        )
        self.repo = ArbolEnMemoria(
            nodos={n.id: n for n in [self.varilla, self.alambre, self.mo_zapata, self.zapata]},
            composicion=[
                Composicion(1, self.zapata.id, self.varilla.id, Decimal("2.76"), 1, Categoria.MATERIAL),
                Composicion(2, self.zapata.id, self.alambre.id, Decimal("0.807"), 2, Categoria.MATERIAL),
                # El hallazgo 1 de MODELO.md vive acá: MOC-12010 ES
                # Trabajo, pero REPORTA a Material porque la línea vive
                # dentro de la matriz de un compuesto que reporta como
                # material entero.
                Composicion(3, self.zapata.id, self.mo_zapata.id, Decimal("1"), 3, Categoria.MATERIAL),
            ],
        )

    def test_precio_unitario_suma_exacta(self):
        self.assertEqual(precio_unitario(self.zapata.id, self.repo), Decimal("1135.48"))

    def test_reporta_cien_por_ciento_como_material(self):
        # "la zapata reporta 100% como material, aunque lleve un
        # contrato adentro" — CASO-TRABAJADO.md §3
        self.assertEqual(
            reporte_montos(self.zapata.id, self.repo),
            {Categoria.MATERIAL: Decimal("1135.48")},
        )


class PruebaPorcentajeMO(unittest.TestCase):
    """erp-construccion.md §2, CUAD-001: 0.1 %MO sobre $1,880 de
    jornales da $188, sin importar el orden de las líneas."""

    def _cuadrilla(self, orden_contratista):
        peon = _insumo(1, "MOB-001", "Peón", "JOR", Categoria.MANO_DE_OBRA, "560")
        albanil = _insumo(2, "MOB-002", "Albañil", "JOR", Categoria.MANO_DE_OBRA, "760")
        contratista = _insumo(3, "MOB-003", "Contratista", "%MO", Categoria.MANO_DE_OBRA, "0")
        cuadrilla = Nodo(
            id=10,
            clave="CUAD-001",
            descripcion="Cuadrilla 001",
            unidad="CUAD",
            rol=Rol.ENSAMBLE,
            categoria=Categoria.MANO_DE_OBRA,
        )
        lineas = [
            Composicion(1, cuadrilla.id, peon.id, Decimal("2"), 1, Categoria.MANO_DE_OBRA),
            Composicion(2, cuadrilla.id, albanil.id, Decimal("1"), 2, Categoria.MANO_DE_OBRA),
            Composicion(
                3,
                cuadrilla.id,
                contratista.id,
                Decimal("0.1"),
                orden_contratista,
                Categoria.MANO_DE_OBRA,
                tipo_cantidad=TipoCantidad.PORCENTAJE,
                base_porcentaje=BasePorcentaje.SUMA_JORNALES_HERMANOS,
            ),
        ]
        repo = ArbolEnMemoria(
            nodos={n.id: n for n in [peon, albanil, contratista, cuadrilla]},
            composicion=lineas,
        )
        return cuadrilla, repo

    def test_base_es_la_suma_de_jornales(self):
        cuadrilla, repo = self._cuadrilla(orden_contratista=3)
        # 2×560 + 1×760 = 1,880 de jornales; 0.1 × 1,880 = 188
        self.assertEqual(precio_unitario(cuadrilla.id, repo), Decimal("2068.00"))

    def test_el_orden_no_cambia_el_resultado(self):
        # "no se acumulan → el orden de las líneas no afecta el
        # resultado" — erp-construccion.md §2
        _, repo_al_final = self._cuadrilla(orden_contratista=3)
        _, repo_primero = self._cuadrilla(orden_contratista=0)
        self.assertEqual(precio_unitario(10, repo_al_final), precio_unitario(10, repo_primero))


class PruebaCantidadNegativa(unittest.TestCase):
    """CASO-TRABAJADO.md §2: -0.656 PZ de varilla, ajuste que descuenta
    acero ya contado. El modelo tiene que admitirlo tal cual —
    INVARIANTES.md §2: "un validador de solo-positivos las está
    tirando" es la falla, no la cantidad negativa."""

    def test_importe_negativo_se_calcula_igual(self):
        varilla = _insumo(1, "ACR-00002", "Varilla 1/2", "PZ", Categoria.MATERIAL, "237.52")
        padre = Nodo(2, "EST-01053", "Losa (parcial)", "M2", Rol.CONCEPTO, Categoria.MATERIAL)
        repo = ArbolEnMemoria(
            nodos={varilla.id: varilla, padre.id: padre},
            composicion=[
                Composicion(1, padre.id, varilla.id, Decimal("-0.656"), 1, Categoria.MATERIAL),
            ],
        )
        self.assertEqual(precio_unitario(padre.id, repo), Decimal("-155.81"))


class PruebaDosLecturas(unittest.TestCase):
    """CASO-TRABAJADO.md §1-4: la losa EST-01053, con solo las líneas
    que trae el caso trabajado (no las 20 completas), para probar que
    el reporte de montos se detiene en el compuesto y la explosión
    llega al fondo conservando la naturaleza de cada hoja."""

    def setUp(self):
        self.varilla = _insumo(1, "ACR-00002", "Varilla 1/2", "PZ", Categoria.MATERIAL, "237.52")
        self.alambre = _insumo(2, "ACE-00001", "Alambre recocido", "KG", Categoria.MATERIAL, "24.68")
        self.mo_zapata = _insumo(3, "MOC-12010", "MO Zapata ZA-1", "PZ", Categoria.TRABAJO, "460.00")
        self.zapata = Nodo(10, "ZA1-000001", "Zapata ZA-1", "PZ", Rol.INSUMO, Categoria.MATERIAL)

        self.concreto = _insumo(4, "CON-00001", "Concreto TD 200", "M3", Categoria.MATERIAL, "2442.33")
        self.mo_losa = _insumo(5, "MOC-01010", "MO losa de cimentación", "M2", Categoria.TRABAJO, "230.00")
        self.losa = Nodo(
            20, "EST-01053", "Losa cimentación Diamante c/ch (parcial)", "M2", Rol.CONCEPTO, Categoria.MATERIAL
        )

        self.repo = ArbolEnMemoria(
            nodos={
                n.id: n
                for n in [
                    self.varilla,
                    self.alambre,
                    self.mo_zapata,
                    self.zapata,
                    self.concreto,
                    self.mo_losa,
                    self.losa,
                ]
            },
            composicion=[
                # matriz propia de la zapata
                Composicion(1, self.zapata.id, self.varilla.id, Decimal("2.76"), 1, Categoria.MATERIAL),
                Composicion(2, self.zapata.id, self.alambre.id, Decimal("0.807"), 2, Categoria.MATERIAL),
                Composicion(3, self.zapata.id, self.mo_zapata.id, Decimal("1"), 3, Categoria.MATERIAL),
                # matriz de la losa (parcial: 3 de sus 20 líneas reales)
                Composicion(4, self.losa.id, self.concreto.id, Decimal("34"), 1, Categoria.MATERIAL),
                Composicion(5, self.losa.id, self.mo_losa.id, Decimal("216"), 2, Categoria.TRABAJO),
                Composicion(6, self.losa.id, self.zapata.id, Decimal("6"), 3, Categoria.MATERIAL),
            ],
        )

    def test_reporte_de_montos_se_detiene_en_el_compuesto(self):
        montos = reporte_montos(self.losa.id, self.repo)
        # 83,039.22 (concreto) + 6,812.88 (zapata entera, sin abrir) = 89,852.10
        self.assertEqual(montos[Categoria.MATERIAL], Decimal("89852.10"))
        # 49,680.00 — el $460×6 de mano de obra que vive DENTRO de la
        # zapata no aparece acá: se quedó adentro del compuesto.
        self.assertEqual(montos[Categoria.TRABAJO], Decimal("49680.00"))

    def test_explosion_llega_al_fondo_y_conserva_la_cantidad(self):
        hojas = explosion(self.losa.id, self.repo)
        por_clave = {linea.nodo.clave: linea for linea in hojas}

        self.assertEqual(por_clave["CON-00001"].cantidad, Decimal("34"))

        # Las cantidades de la zapata se multiplican por las 6 que se
        # usan en la losa — CASO-TRABAJADO.md §4, "Las dos lecturas,
        # sobre este caso": 16.56 PZ · 4.84 KG · 6.00 PZ.
        self.assertEqual(por_clave["ACR-00002"].cantidad, Decimal("16.56"))
        self.assertEqual(
            por_clave["ACE-00001"].cantidad.quantize(Decimal("0.01")), Decimal("4.84")
        )
        self.assertEqual(por_clave["MOC-12010"].cantidad, Decimal("6.00"))

        # Y cada hoja conserva SU categoría propia, no la del compuesto
        # que la contiene — erp-construccion.md §3.
        self.assertEqual(por_clave["MOC-12010"].nodo.categoria, Categoria.TRABAJO)


class PruebaCiclo(unittest.TestCase):
    """INVARIANTES.md §3: "ningún compuesto se contiene a sí mismo...
    si falla: recursión infinita en el motor." Se convierte en error
    explícito en vez de reventar el stack."""

    def test_ciclo_directo_se_detecta(self):
        nodo = Nodo(1, "X", "se contiene a sí mismo", "PZ", Rol.INSUMO, Categoria.MATERIAL)
        repo = ArbolEnMemoria(
            nodos={1: nodo},
            composicion=[Composicion(1, 1, 1, Decimal("1"), 1, Categoria.MATERIAL)],
        )
        with self.assertRaises(CicloError):
            precio_unitario(1, repo)

    def test_ciclo_indirecto_se_detecta(self):
        a = Nodo(1, "A", "a", "PZ", Rol.INSUMO, Categoria.MATERIAL)
        b = Nodo(2, "B", "b", "PZ", Rol.INSUMO, Categoria.MATERIAL)
        repo = ArbolEnMemoria(
            nodos={1: a, 2: b},
            composicion=[
                Composicion(1, 1, 2, Decimal("1"), 1, Categoria.MATERIAL),
                Composicion(2, 2, 1, Decimal("1"), 1, Categoria.MATERIAL),
            ],
        )
        with self.assertRaises(CicloError):
            precio_unitario(1, repo)


class PruebaPlaceholder(unittest.TestCase):
    """INVARIANTES.md §2: 121 filas de OPUS, 3.7%, "importe cero y sin
    descendientes con clave." Un nodo calculado sin matriz cargada es
    cero por diseño — no un error a rechazar."""

    def test_nodo_calculado_sin_lineas_es_cero(self):
        nodo = Nodo(1, "PLACEHOLDER", "fila vacía de OPUS", "PZA", Rol.ESTRUCTURAL, Categoria.CONCEPTO)
        repo = ArbolEnMemoria(nodos={1: nodo}, composicion=[])
        self.assertEqual(precio_unitario(1, repo), Decimal("0"))


class PruebaCapasDeSobrecosto(unittest.TestCase):
    """MODELO.md §6 deja las capas de sobrecosto fuera del modelo: "sin
    datos reales que las usen." `acumulado_hasta_aqui` está en el enum
    porque MODELO.md lo declara, pero no hay regla verificada que
    implementar todavía — mejor un error explícito que adivinarla."""

    def test_acumulado_hasta_aqui_no_implementado(self):
        insumo = _insumo(1, "X", "insumo", "PZ", Categoria.MATERIAL, "1")
        padre = Nodo(2, "Y", "padre", "PZ", Rol.CONCEPTO, Categoria.MATERIAL)
        repo = ArbolEnMemoria(
            nodos={1: insumo, 2: padre},
            composicion=[
                Composicion(
                    1,
                    padre.id,
                    insumo.id,
                    Decimal("0.1"),
                    1,
                    Categoria.MATERIAL,
                    tipo_cantidad=TipoCantidad.PORCENTAJE,
                    base_porcentaje=BasePorcentaje.ACUMULADO_HASTA_AQUI,
                )
            ],
        )
        with self.assertRaises(NotImplementedError):
            precio_unitario(padre.id, repo)


if __name__ == "__main__":
    unittest.main()
