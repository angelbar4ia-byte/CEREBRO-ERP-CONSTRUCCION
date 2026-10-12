"""
`api.colgar_programa.colgar`: colgar un programa desde la terminal, con los programas y los presupuestos de verdad y los adaptadores
en memoria. Lo que importa es lo que dice y lo que escribe: revisar no escribe; colgar sí; y solo cuelga quien está dado de alta y puede.
"""
import io
import unittest

from api.colgar_programa import colgar
from core.accesos import MemoriaAccesos
from core.catalogo import ServicioCarga
from core.memoria_catalogo import MemoriaCatalogo
from core.memoria_programa import MemoriaPrograma
from core.tests.contrato_programa import CAL, programa
from core.tests.datos_opus import CONCEPTOS, PRESUPUESTO, texto


class PruebasColgarPrograma(unittest.TestCase):
    def setUp(self):
        self.pro, self.cat, self.acc = MemoriaPrograma(), MemoriaCatalogo(), MemoriaAccesos()
        ServicioCarga(self.cat).aplicar(texto(CONCEPTOS), texto(PRESUPUESTO), None, rol="costos", usuario="ana@obra.mx")
        self.acc.agregar_usuario("Luis Pérez", "luis@obra.mx", ["control_de_obra"])
        self.acc.agregar_usuario("Ana Soto", "ana@obra.mx", ["costos"])
        self.acc.agregar_usuario("Retirado", "viejo@obra.mx", ["control_de_obra"])
        self.acc.desactivar_usuario("viejo@obra.mx")
        self.zafiro = self.pro.importar_programa("Zafiro", programa("Zafiro"), CAL)
        self.rubi = self.pro.importar_programa("Rubí", programa("Rubí"), CAL)

    def correr(self, correo="luis@obra.mx", **kw):
        kw.setdefault("programa", self.zafiro)
        self.salida, self.errores = io.StringIO(), io.StringIO()
        return colgar(self.pro, self.cat, self.acc, correo=correo, salida=self.salida, errores=self.errores, **kw)

    def test_revisar_dice_que_casa_y_que_no_de_los_dos_lados_y_no_escribe(self):
        self.assertEqual(self.correr(), 0)
        t = self.salida.getvalue()
        self.assertIn("contra el presupuesto CAS-00004", t)
        self.assertIn("casan 83 de 83 bloques y 315 de 316 conceptos", t)
        self.assertIn("16 marcador(es) vacío(s) de OPUS", t)
        self.assertIn("ACA-02034", t)
        self.assertIn("el presupuesto no tiene ese concepto en ese bloque", t)
        self.assertIn("No se escribió nada", t)
        g = self.pro.leer_programa(self.zafiro)
        self.assertEqual((g.presupuesto_id, g.enlaces, g.colgaduras), (None, [], []))

    def test_un_programa_que_cuadra_completo_lo_dice(self):
        self.assertEqual(self.correr(programa=self.rubi), 0)
        self.assertIn("cuadra completo, de los dos lados.", self.salida.getvalue())

    def test_colgar_escribe_con_quien_lo_hizo_y_repetirlo_no_cambia_nada(self):
        self.assertEqual(self.correr(colgar_ya=True), 0)
        self.assertIn("Se pusieron 398 enlace(s) nuevos.", self.salida.getvalue())
        (c,) = self.pro.leer_programa(self.zafiro).colgaduras
        self.assertEqual((c.usuario, c.rol, c.nuevos), ("luis@obra.mx", "control_de_obra", 398))
        self.assertEqual(self.correr(colgar_ya=True), 0)
        self.assertIn("No había enlaces nuevos que poner.", self.salida.getvalue())
        self.assertEqual(len(self.pro.leer_programa(self.zafiro).colgaduras), 1)

    def test_solo_cuelga_quien_esta_dado_de_alta_activo_y_puede(self):
        for correo, esperado in (("nadie@obra.mx", "no es un usuario dado de alta"), ("viejo@obra.mx", "no es un usuario dado de alta"),
                                 ("ana@obra.mx", "costos")):
            self.assertEqual(self.correr(correo=correo, colgar_ya=True), 2, correo)
            self.assertIn(esperado, self.errores.getvalue())
        self.assertEqual(self.pro.leer_programa(self.zafiro).enlaces, [])

    def test_lo_que_no_se_puede_se_dice_sin_escribir(self):
        self.assertEqual(self.correr(programa=987), 1)
        self.assertIn("no hay programa 987", self.errores.getvalue())
        zafiro = self.cat.presupuestos()
        otro = next(p.id for p in zafiro if p.clave == "CAS-00004")
        self.assertEqual(self.correr(programa=self.rubi, presupuesto=otro, colgar_ya=True, forzar=True), 1)  # Rubí no casa con Zafiro
        self.assertIn("ninguna fila", self.errores.getvalue())
        self.assertEqual(self.pro.leer_programa(self.rubi).enlaces, [])
        self.assertEqual(self.correr(colgar_ya=True), 0)
        self.assertEqual(self.correr(colgar_ya=True, presupuesto=next(p.id for p in zafiro if p.clave == "CAS-00003")), 1)  # y no se cambia
        self.assertIn("no se cambia", self.errores.getvalue())


if __name__ == "__main__":
    unittest.main()
