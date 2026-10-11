"""
`api.contratar.contratar`: contratar un subárbol desde la terminal, con los presupuestos de verdad y los adaptadores en memoria. Lo que
importa es lo que dice y lo que escribe: revisar no escribe; contratar sí; y solo contrata quien está dado de alta y puede.
"""
import io
import unittest
from decimal import Decimal

from api.contratar import contratar
from core.accesos import MemoriaAccesos
from core.catalogo import ServicioCarga
from core.memoria_catalogo import MemoriaCatalogo
from core.tests.datos_opus import CONCEPTOS, PRESUPUESTO, reescalar_costo, texto

BLOQUE = "CAS-00004#1/NIV-00001#1"


class PruebasContratar(unittest.TestCase):
    def setUp(self):
        self.cat, self.acc = MemoriaCatalogo(), MemoriaAccesos()
        self.carga = ServicioCarga(self.cat)
        self.carga.aplicar(texto(CONCEPTOS), texto(PRESUPUESTO), None, rol="costos", usuario="ana@obra.mx")
        self.acc.agregar_usuario("Luis Pérez", "luis@obra.mx", ["control_de_obra"])
        self.acc.agregar_usuario("Ana Soto", "ana@obra.mx", ["costos"])
        self.acc.agregar_usuario("Retirado", "viejo@obra.mx", ["control_de_obra"])
        self.acc.desactivar_usuario("viejo@obra.mx")

    def correr(self, correo="luis@obra.mx", **kw):
        kw.setdefault("presupuesto", "CAS-00004")
        kw.setdefault("bloque", BLOQUE)
        self.salida, self.errores = io.StringIO(), io.StringIO()
        return contratar(self.cat, self.acc, correo=correo, salida=self.salida, errores=self.errores, **kw)

    def mover_el_acero(self, factor):
        self.carga.aplicar(reescalar_costo(texto(CONCEPTOS), "ACE-00001", Decimal(factor)), texto(PRESUPUESTO), None, rol="costos", usuario="ana@obra.mx")

    def test_revisar_dice_que_se_fija_y_cuanto_cambia_y_no_escribe(self):
        self.mover_el_acero("1.02")
        self.assertEqual(self.correr(), 0)
        t = self.salida.getvalue()
        self.assertIn("Contratar CAS-00004#1/NIV-00001#1 — CIMENTACIÓN", t)
        self.assertIn("56 conceptos en 56 renglones", t)
        self.assertIn("25 versiones nuevas", t)
        self.assertIn("178,768.69 y quedará en 178,809.66 (+40.97)", t)
        self.assertIn("No se escribió nada", t)
        self.assertEqual(self.cat.congelamientos(self.cat.presupuestos()[0].id), [])

    def test_contratar_escribe_con_quien_lo_hizo_y_no_se_repite(self):
        self.mover_el_acero("1.02")
        self.assertEqual(self.correr(contratar_ya=True), 0)
        self.assertIn("Contratado: 25 versiones nuevas y 25 renglones fijados", self.salida.getvalue())
        (c,) = self.cat.congelamientos(next(p.id for p in self.cat.presupuestos() if p.clave == "CAS-00004"))
        self.assertEqual((c.usuario, c.rol, c.ruta), ("luis@obra.mx", "control_de_obra", BLOQUE))
        self.assertEqual(self.correr(contratar_ya=True), 1)  # lo contratado no se vuelve a contratar
        self.assertIn("ya está contratado", self.errores.getvalue())

    def test_lo_que_pide_confirmacion_se_dice_y_la_confirmacion_lo_deja_pasar(self):
        self.mover_el_acero("4")
        self.assertEqual(self.correr(contratar_ya=True), 1)
        self.assertIn("EST-10010", self.errores.getvalue())
        self.assertIn("--confirmar", self.errores.getvalue())
        self.assertEqual(self.cat.congelamientos(1), [])
        self.assertEqual(self.correr(contratar_ya=True, confirmados=["EST-10010", "EST-10020", "EST-10021", "EST-10031", "EST-10041"]), 0)

    def test_solo_contrata_quien_esta_dado_de_alta_activo_y_puede(self):
        for correo, esperado in (("nadie@obra.mx", "no es un usuario dado de alta"), ("viejo@obra.mx", "no es un usuario dado de alta"),
                                 ("ana@obra.mx", "costos")):
            self.assertEqual(self.correr(correo=correo, contratar_ya=True), 2, correo)
            self.assertIn(esperado, self.errores.getvalue())
        self.assertEqual(self.cat.congelamientos(1), [])

    def test_lo_que_no_existe_se_dice(self):
        self.assertEqual(self.correr(presupuesto="CAS-99999"), 1)
        self.assertIn("no hay presupuesto", self.errores.getvalue())
        self.assertEqual(self.correr(bloque="CAS-00004#1/NIV-99999#1"), 1)
        self.assertIn("no tiene el bloque", self.errores.getvalue())
        self.assertEqual(self.correr(bloque=None), 0)  # el presupuesto entero
        self.assertIn("Contratar CAS-00004#1 —", self.salida.getvalue())


if __name__ == "__main__":
    unittest.main()
