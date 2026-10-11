"""
`api.guardar_subidas.correr`: guardar las tablas de una sesión y comprobar que lo guardado sigue ahí, con tablas de verdad.
"""
import io
import shutil
import tempfile
import unittest
from pathlib import Path

from api.guardar_subidas import RAIZ, correr

CORTA = RAIZ / "1-mundo/opus/ingenieria-alamo-18/INGENIERIA_-_ALAMO_18__-_CENTRO_DE_CARGA.csv"


class PruebasGuardarSubidas(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="subidas_"))
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.raiz, self.subidas = self.tmp / "repo", self.tmp / "subidas"
        self.raiz.mkdir()
        self.subidas.mkdir()

    def correr(self, origen=None, raiz=None, solo_verificar=False):
        self.salida, self.errores = io.StringIO(), io.StringIO()
        return correr(origen or self.subidas, raiz or self.raiz, solo_verificar, self.salida, self.errores)

    def test_guarda_lo_que_se_sube_y_no_lo_repite(self):
        shutil.copyfile(CORTA, self.subidas / "0983bd6c-INGENIERIA_-_ALAMO_18__-_CENTRO_DE_CARGA.csv")
        self.assertEqual(self.correr(), 0)
        self.assertIn("guardado  1-mundo/opus/ingenieria-alamo-18/INGENIERIA_-_ALAMO_18__-_CENTRO_DE_CARGA.csv", self.salida.getvalue())
        self.assertIn("1 archivos nuevos · 0 subidas que ya estaban guardadas", self.salida.getvalue())
        self.assertEqual(self.correr(), 0)
        self.assertIn("0 archivos nuevos · 1 subidas que ya estaban guardadas", self.salida.getvalue())

    def test_una_carpeta_de_subidas_que_no_existe_se_dice(self):
        self.assertEqual(self.correr(origen=self.tmp / "nada"), 1)
        self.assertIn("No hay carpeta de subidas", self.errores.getvalue())

    def test_verificar_el_repositorio_de_verdad(self):
        self.assertEqual(self.correr(raiz=RAIZ, solo_verificar=True), 0)
        self.assertIn("Todo lo compartido sigue ahí, sin cambios.", self.salida.getvalue())

    def test_verificar_dice_los_problemas_y_sale_con_1(self):
        self.assertEqual(self.correr(solo_verificar=True), 1)
        self.assertIn("no hay manifiesto", self.errores.getvalue())
        shutil.copyfile(CORTA, self.subidas / "0983bd6c-INGENIERIA_-_ALAMO_18__-_CENTRO_DE_CARGA.csv")
        self.correr()
        guardada = self.raiz / "1-mundo/opus/ingenieria-alamo-18/INGENIERIA_-_ALAMO_18__-_CENTRO_DE_CARGA.csv"
        guardada.write_text("otra cosa\n", encoding="utf-8")
        self.assertEqual(self.correr(solo_verificar=True), 1)
        self.assertIn("cambió", self.errores.getvalue())
        self.assertIn("1 problemas", self.salida.getvalue())


if __name__ == "__main__":
    unittest.main()
