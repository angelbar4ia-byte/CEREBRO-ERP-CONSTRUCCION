"""
`api.cargar_opus.cargar`: la carga desde la terminal, con los archivos de verdad de `1-mundo/opus/` y los adaptadores en memoria.
Lo que importa es lo que dice y lo que escribe: revisar no escribe; aplicar sí; y solo carga quien está dado de alta y puede.
"""
import io
import unittest
from decimal import Decimal

from api.cargar_opus import cargar
from core.accesos import MemoriaAccesos
from core.memoria_catalogo import MemoriaCatalogo
from core.tests.datos_opus import CONCEPTOS, OPUS, PRESUPUESTO, reescalar_linea, texto


class PruebasCargarOpus(unittest.TestCase):
    def setUp(self):
        self.cat, self.acc = MemoriaCatalogo(), MemoriaAccesos()
        self.acc.agregar_usuario("Ana Soto", "ana@obra.mx", ["costos"])
        self.acc.agregar_usuario("Luis Pérez", "luis@obra.mx", ["residente"])
        self.acc.agregar_usuario("Retirado", "viejo@obra.mx", ["costos"])
        self.acc.desactivar_usuario("viejo@obra.mx")
        self.salida, self.errores = io.StringIO(), io.StringIO()

    def correr(self, correo="ana@obra.mx", **kw):
        kw.setdefault("conceptos", OPUS / f"{CONCEPTOS}.csv")
        kw.setdefault("presupuesto", OPUS / f"{PRESUPUESTO}.csv")
        self.salida, self.errores = io.StringIO(), io.StringIO()
        return cargar(self.cat, self.acc, correo=correo, salida=self.salida, errores=self.errores, **kw)

    def test_revisar_dice_que_entra_y_no_escribe_nada(self):
        self.assertEqual(self.correr(), 0)
        t = self.salida.getvalue()
        self.assertIn("596 son nuevas", t)
        self.assertIn("612 insumos nuevos", t)
        self.assertIn("CAS-00004  ZAFIRO 1.0 (172 M2) — se cargará", t)
        self.assertIn("Sin matriz (4): ACC-00003, IGAS-02131, IGAS-02132, ISN-02061", t)
        self.assertIn("Sin unidad conocida (40)", t)
        self.assertIn("No se escribió nada", t)
        self.assertEqual((self.cat.cargas(), self.cat.presupuestos()), ([], []))

    def test_aplicar_escribe_con_quien_la_hizo_y_el_rol(self):
        self.assertEqual(self.correr(aplicar=True), 0)
        self.assertIn("Carga 1 aplicada.", self.salida.getvalue())
        (c,) = self.cat.cargas()
        self.assertEqual((c.usuario, c.rol), ("ana@obra.mx", "costos"))
        self.assertEqual(len(self.cat.presupuestos()), 7)
        self.assertEqual(self.correr(aplicar=True), 0)  # lo mismo otra vez
        self.assertIn("No había nada que aplicar.", self.salida.getvalue())

    def test_lo_pendiente_se_dice_y_la_confirmacion_lo_aplica(self):
        self.correr(aplicar=True)

        nuevo = reescalar_linea(texto(CONCEPTOS), "ACA-01010", 1, Decimal("2"))
        ruta = self.escribir(nuevo)
        self.assertEqual(self.correr(conceptos=ruta, aplicar=True), 0)
        self.assertIn("ACA-01010", self.salida.getvalue())
        self.assertIn("pide confirmación", self.salida.getvalue())
        self.assertEqual(len(self.cat.versiones("ACA-01010")), 1)
        self.assertEqual(self.correr(conceptos=ruta, aplicar=True, confirmados=["ACA-01010"]), 0)
        self.assertEqual(len(self.cat.versiones("ACA-01010")), 2)

    def escribir(self, contenido):
        import tempfile
        from pathlib import Path

        d = Path(tempfile.mkdtemp(prefix="cargar_opus_"))
        self.addCleanup(lambda: __import__("shutil").rmtree(d, ignore_errors=True))
        ruta = d / "conceptos.csv"
        ruta.write_text(contenido, encoding="utf-8")
        return ruta

    def test_solo_carga_quien_esta_dado_de_alta_activo_y_puede(self):
        for correo, esperado in (("nadie@obra.mx", "no es un usuario dado de alta"), ("viejo@obra.mx", "no es un usuario dado de alta"),
                                 ("luis@obra.mx", "residente")):
            self.assertEqual(self.correr(correo=correo, aplicar=True), 2, correo)
            self.assertIn(esperado, self.errores.getvalue())
        self.assertEqual(self.cat.cargas(), [])

    def test_un_archivo_que_no_cuadra_se_dice_y_no_se_carga(self):
        ruta = self.escribir("esto,no,es,un,archivo\n1,2,3,4,5\n")
        self.assertEqual(self.correr(conceptos=ruta, presupuesto=None, aplicar=True), 1)
        self.assertIn("faltan columnas obligatorias", self.errores.getvalue())
        self.assertEqual(self.cat.cargas(), [])


if __name__ == "__main__":
    unittest.main()
