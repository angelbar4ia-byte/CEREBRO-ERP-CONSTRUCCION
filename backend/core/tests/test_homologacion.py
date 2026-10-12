"""
La clave vieja que se lee como su clon (D-478, `CONOCIMIENTO.md` §16.2): las funciones puras que reescriben un archivo ya leído, con los
archivos de OPUS de verdad. El contrato de lo que pasa en el catálogo está en `contrato_clonacion.py`.
"""
import unittest
from dataclasses import replace

from core.catalogo import EstadoVigente, cerrar_homologaciones
from core.importacion_opus import canonizar_matrices, canonizar_presupuesto, leer_matrices, leer_presupuesto
from core.tests.datos_opus import COMPUESTOS, CONCEPTOS, PRESUPUESTO, texto

MAPA = {"AUX-00001": "PRE-00120"}


class PruebasDeCanonizarMatrices(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.m = leer_matrices(texto(CONCEPTOS), texto(COMPUESTOS))

    def test_sin_mapa_no_se_toca_nada(self):
        m, leidas = canonizar_matrices(self.m, {})
        self.assertIs(m, self.m)
        self.assertEqual(leidas, ())

    def test_la_vieja_se_lee_como_el_clon_de_padre_y_de_hijo(self):
        m, leidas = canonizar_matrices(self.m, MAPA)
        self.assertEqual(leidas, (("AUX-00001", "PRE-00120"),))
        self.assertNotIn("AUX-00001", m.por_padre)
        self.assertEqual([(l.hijo, l.cantidad) for l in m.por_padre["PRE-00120"]], [(l.hijo, l.cantidad) for l in self.m.por_padre["AUX-00001"]])
        self.assertEqual({l.padre for l in m.lineas if l.hijo == "PRE-00120"}, {l.padre for l in self.m.lineas if l.hijo == "AUX-00001"})
        self.assertFalse(any("AUX-00001" in (l.padre, l.hijo) for l in m.lineas))
        self.assertEqual(len(m.lineas), len(self.m.lineas))
        self.assertEqual(m.solo_en_compuestos, self.m.solo_en_compuestos)
        # lo demás, tal cual
        self.assertEqual([l for l in m.lineas if "PRE-00120" not in (l.padre, l.hijo)], [l for l in self.m.lineas if "AUX-00001" not in (l.padre, l.hijo)])

    def test_el_orden_de_las_lineas_de_una_matriz_se_conserva(self):
        m, _ = canonizar_matrices(self.m, MAPA)
        for padre in ("EST-21011", "EST-22010"):
            self.assertEqual([l.linea for l in m.por_padre[padre]], [l.linea for l in self.m.por_padre[padre]])

    def test_si_el_archivo_trae_la_vieja_y_el_clon_manda_la_del_clon(self):
        con_clon = tuple(replace(l, padre="PRE-00120", linea=l.linea + 100_000) for l in self.m.por_padre["AUX-00001"])
        revuelto = replace(self.m, lineas=self.m.lineas + con_clon, por_padre={**self.m.por_padre, "PRE-00120": con_clon})
        m, leidas = canonizar_matrices(revuelto, MAPA)
        self.assertEqual(leidas, (("AUX-00001", "PRE-00120"),))
        self.assertEqual(m.por_padre["PRE-00120"], con_clon)  # cuatro líneas, no ocho
        self.assertEqual(len(m.lineas), len(self.m.lineas))

    def test_los_importes_que_no_cuadran_tambien_se_leen_con_la_clave_vigente(self):
        una = self.m.por_padre["AUX-00001"][0]
        m, _ = canonizar_matrices(replace(self.m, importes_que_no_cuadran=(una,)), MAPA)
        self.assertEqual([(l.padre, l.hijo) for l in m.importes_que_no_cuadran], [("PRE-00120", una.hijo)])

    def test_una_clave_que_solo_es_hijo_tambien_se_lee(self):
        m, leidas = canonizar_matrices(self.m, {"ACR-00001": "ACR-90001"})  # un insumo: nunca es padre
        self.assertEqual(leidas, (("ACR-00001", "ACR-90001"),))
        self.assertNotIn("ACR-90001", m.por_padre)
        self.assertTrue(all(l.hijo != "ACR-00001" for l in m.lineas))
        self.assertGreater(sum(1 for l in m.lineas if l.hijo == "ACR-90001"), 0)

    def test_una_clave_del_mapa_que_el_archivo_no_trae_no_se_cuenta(self):
        m, leidas = canonizar_matrices(self.m, {"XXX-99999": "YYY-99999"})
        self.assertEqual(leidas, ())
        self.assertEqual(m.lineas, self.m.lineas)


class PruebasDeCanonizarPresupuesto(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.p = leer_presupuesto(texto(PRESUPUESTO))

    def test_sin_conceptos_afectados_es_el_mismo(self):
        self.assertIs(canonizar_presupuesto(self.p, {}), self.p)
        self.assertIs(canonizar_presupuesto(self.p, MAPA), self.p)  # ninguna trabe es un renglón: se cita desde una matriz

    def test_un_concepto_del_presupuesto_se_lee_con_la_clave_vigente_en_todas_sus_apariciones(self):
        antes = self.p.conceptos["EST-21011"]
        p = canonizar_presupuesto(self.p, {"EST-21011": "EST-90011"})
        self.assertNotIn("EST-21011", p.conceptos)
        self.assertEqual([(f.posicion, f.cantidad) for f in p.conceptos["EST-90011"]], [(f.posicion, f.cantidad) for f in antes])
        self.assertEqual(len(p.filas), len(self.p.filas))
        self.assertTrue(all(f.clave != "EST-21011" for f in p.filas))
        # los demás conceptos, y los bloques, igual
        self.assertEqual({k: v for k, v in p.conceptos.items() if k != "EST-90011"}, {k: v for k, v in self.p.conceptos.items() if k != "EST-21011"})
        self.assertEqual([f for f in p.filas if not f.es_concepto], [f for f in self.p.filas if not f.es_concepto])
        self.assertEqual(p.problemas, self.p.problemas)

    def test_un_bloque_que_se_llama_como_la_clave_no_se_toca(self):
        bloque = next(f for f in self.p.filas if not f.es_concepto)
        p = canonizar_presupuesto(self.p, {bloque.clave: "XXX-00001", "EST-21011": "EST-90011"})
        self.assertIn(bloque.clave, {f.clave for f in p.filas if not f.es_concepto})


class PruebasDeCerrarHomologaciones(unittest.TestCase):
    def test_una_cadena_entra_como_la_ultima(self):
        self.assertEqual(cerrar_homologaciones([("A", "B"), ("B", "C")]), {"A": "C", "B": "C"})
        self.assertEqual(cerrar_homologaciones([("B", "C"), ("A", "B")]), {"A": "C", "B": "C"})

    def test_cada_una_por_su_lado(self):
        self.assertEqual(cerrar_homologaciones([("A", "B"), ("X", "Y")]), {"A": "B", "X": "Y"})
        self.assertEqual(cerrar_homologaciones([]), {})

    def test_un_ciclo_no_cuelga_el_sistema(self):
        self.assertEqual(set(cerrar_homologaciones([("A", "B"), ("B", "A")])), {"A", "B"})


class PruebasDelEstadoVigente(unittest.TestCase):
    def test_lo_retirado_no_se_compara_contra_el_archivo(self):
        e = EstadoVigente(unidad={"AUX-00001": "M", "PRE-00120": "M", "EST-1": "M2"}, huella={"AUX-00001": "a", "PRE-00120": "a", "EST-1": "b"},
                          sin_matriz={"AUX-00002", "ACC-1"}, homologaciones={"AUX-00001": "PRE-00120", "AUX-00002": "PRE-00121"})
        c = e.como_catalogo()
        self.assertEqual(set(c.unidad), {"PRE-00120", "EST-1"})
        self.assertEqual(set(c.huella), {"PRE-00120", "EST-1"})
        self.assertEqual(c.sin_matriz, ("ACC-1",))

    def test_sin_homologaciones_es_lo_de_siempre(self):
        e = EstadoVigente(unidad={"A": "M"}, huella={"A": "h"}, sin_matriz={"B"})
        c = e.como_catalogo()
        self.assertEqual((dict(c.unidad), dict(c.huella), c.sin_matriz), ({"A": "M"}, {"A": "h"}, ("B",)))


if __name__ == "__main__":
    unittest.main()
