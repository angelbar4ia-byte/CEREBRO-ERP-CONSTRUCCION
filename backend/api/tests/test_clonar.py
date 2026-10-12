"""
`api.clonar.clonar`: clonar un insumo o corregir un prefijo desde la terminal, con los archivos de verdad y los adaptadores en memoria. Lo
que importa es lo que dice y lo que escribe: revisar no escribe; clonar sí; solo clona quien está dado de alta y puede; y lo que se rechaza
se dice sin tocar al original.
"""
import io
import unittest

from api.clonar import clonar
from core.accesos import MemoriaAccesos
from core.catalogo import ServicioCarga
from core.contratacion import ServicioContratacion
from core.memoria_catalogo import MemoriaCatalogo
from core.tests.datos_opus import COMPUESTOS, CONCEPTOS, PRESUPUESTO, texto


class PruebasClonar(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.con, cls.comp, cls.pres = texto(CONCEPTOS), texto(COMPUESTOS), texto(PRESUPUESTO)

    def setUp(self):
        self.cat, self.acc = MemoriaCatalogo(), MemoriaAccesos()
        ServicioCarga(self.cat).aplicar(self.con, self.pres, self.comp, rol="costos", usuario="ana@obra.mx")
        self.acc.agregar_usuario("Luis Pérez", "luis@obra.mx", ["control_de_obra"])
        self.acc.agregar_usuario("Ana Soto", "ana@obra.mx", ["costos"])
        self.acc.agregar_usuario("Retirado", "viejo@obra.mx", ["control_de_obra"])
        self.acc.desactivar_usuario("viejo@obra.mx")

    def correr(self, correo="luis@obra.mx", **kw):
        self.salida, self.errores = io.StringIO(), io.StringIO()
        return clonar(self.cat, self.acc, correo=correo, salida=self.salida, errores=self.errores, **kw)

    def test_revisar_un_insumo_dice_a_quien_cita_y_no_escribe(self):
        self.assertEqual(self.correr(original="AUX-00001", clave="PRE-00120"), 0)
        t = self.salida.getvalue()
        self.assertIn("Clonar y sustituir — AUX-00001 → PRE-00120", t)
        self.assertIn("9 versiones nuevas, 9 renglones de presupuesto", t)
        self.assertIn("No se escribió nada", t)
        self.assertEqual(self.cat.clones(), [])

    def test_clonar_escribe_con_quien_lo_hizo_y_no_se_repite(self):
        self.assertEqual(self.correr(original="AUX-00001", clave="PRE-00120", clonar_ya=True), 0)
        self.assertIn("Clonado: 9 versiones nuevas y 9 renglones fijados", self.salida.getvalue())
        (c,) = self.cat.clones()
        self.assertEqual((c.original, c.clon, c.usuario, c.rol), ("AUX-00001", "PRE-00120", "luis@obra.mx", "control_de_obra"))
        self.assertEqual(self.correr(original="AUX-00001", clave="PRE-00121", clonar_ya=True), 1)  # ya se sustituyó
        self.assertIn("ya se sustituyó por PRE-00120", self.salida.getvalue())

    def test_mantener_deja_vivo_el_original(self):
        self.assertEqual(self.correr(original="AUX-00001", clave="PRE-00120", modo="mantener", clonar_ya=True), 0)
        self.assertIn("Clonado: 0 versiones nuevas y 0 renglones fijados", self.salida.getvalue())
        self.assertEqual(self.cat.clones()[0].modo, "mantener")

    def test_lo_que_no_se_puede_se_dice(self):
        self.assertEqual(self.correr(original="AUX-00001", clave="PRE-00001"), 1)
        self.assertIn("ya hay un nodo con la clave PRE-00001", self.salida.getvalue())
        self.assertEqual(self.correr(original="AUX-00001", clave="PRE-00001", clonar_ya=True), 1)
        self.assertIn("No se pudo: no se puede clonar", self.errores.getvalue())
        self.assertEqual(self.correr(original="AUX-00001"), 1)
        self.assertIn("falta --clave", self.errores.getvalue())
        self.assertEqual(self.correr(), 1)
        self.assertIn("se clona un insumo", self.errores.getvalue())
        self.assertEqual(self.correr(original="AUX-00001", clave="PRE-00120", prefijo="AUX", por="PRE"), 1)
        self.assertEqual(self.correr(prefijo="AUX"), 1)
        self.assertIn("falta --por", self.errores.getvalue())
        self.assertEqual(self.cat.clones(), [])

    def test_lo_que_cita_algo_contratado_se_rechaza_y_se_dice(self):
        ServicioContratacion(self.cat).contratar("CAS-00004", "control_de_obra", "luis@obra.mx", "CAS-00004#1/NIV-00002#1/ECO-00061#1/EST-00010#1")
        self.assertEqual(self.correr(original="AUX-00001", clave="PRE-00120", clonar_ya=True), 1)
        self.assertIn("EST-21011, que fija un renglón contratado", self.salida.getvalue())
        self.assertEqual(self.cat.clones(), [])

    def test_solo_clona_quien_esta_dado_de_alta_activo_y_puede(self):
        for correo, esperado in (("nadie@obra.mx", "no es un usuario dado de alta"), ("viejo@obra.mx", "no es un usuario dado de alta"),
                                 ("ana@obra.mx", "costos")):
            self.assertEqual(self.correr(correo=correo, original="AUX-00001", clave="PRE-00120", clonar_ya=True), 2, correo)
            self.assertIn(esperado, self.errores.getvalue())
        self.assertEqual(self.cat.clones(), [])

    def test_corregir_un_prefijo_se_revisa_y_luego_se_hace(self):
        self.assertEqual(self.correr(prefijo="AUX", por="PRE", desde=120), 0)
        t = self.salida.getvalue()
        self.assertIn("Corregir el prefijo AUX- por PRE-", t)
        self.assertIn("79 claves por sustituir", t)
        self.assertIn("AUX-00001  → PRE-00120", t)
        self.assertIn("No se escribió nada", t)
        self.assertEqual(self.cat.clones(), [])
        self.assertEqual(self.correr(prefijo="AUX", por="PRE", desde=120, clonar_ya=True), 0)
        self.assertIn("Sustituidas: 79", self.salida.getvalue())
        self.assertEqual(len(self.cat.clones()), 79)
        self.assertEqual(self.correr(prefijo="AUX", por="PRE", desde=120, clonar_ya=True), 0)  # ya no hay nada que hacer
        self.assertIn("0 claves por sustituir · 79 ya sustituidas", self.salida.getvalue())
        self.assertIn("Sustituidas: 0", self.salida.getvalue())

    def test_corregir_un_prefijo_con_algo_contratado_hace_lo_demas_y_sale_con_1(self):
        ServicioContratacion(self.cat).contratar("CAS-00004", "control_de_obra", "luis@obra.mx", "CAS-00004#1/NIV-00002#1/ECO-00061#1/EST-00010#1")
        self.assertEqual(self.correr(prefijo="AUX", por="PRE", desde=120, clonar_ya=True), 1)
        t = self.salida.getvalue()
        self.assertIn("NO SE HIZO AUX-00001", t)
        self.assertGreater(len(self.cat.clones()), 0)
        self.assertLess(len(self.cat.clones()), 79)

    def test_el_prefijo_tiene_que_ser_otro(self):
        self.assertEqual(self.correr(prefijo="AUX", por="AUX"), 1)
        self.assertIn("deben existir y ser distintos", self.errores.getvalue())


if __name__ == "__main__":
    unittest.main()
