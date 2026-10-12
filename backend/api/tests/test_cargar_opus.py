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
from core.contratacion import ServicioContratacion
from core.colgado import ServicioColgado
from core.memoria_programa import MemoriaPrograma
from core.servicio_programa import ServicioPrograma
from core.tests.contrato_programa import CAL, programa
from core.tests.datos_opus import CONCEPTOS, OPUS, PRESUPUESTO, con_cantidad, con_descripcion_del_concepto, reescalar_linea, sin_renglon, texto


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

    def escribir(self, contenido, nombre="conceptos.csv"):
        import tempfile
        from pathlib import Path

        d = Path(tempfile.mkdtemp(prefix="cargar_opus_"))
        self.addCleanup(lambda: __import__("shutil").rmtree(d, ignore_errors=True))
        ruta = d / nombre
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

    # ------------------------------------------------------------------ un presupuesto que ya existe (D-476)
    K1 = "CAS-00004#1/NIV-00001#1/ECO-00001#1/EST-01040#1::EST-10010#1"

    def test_un_presupuesto_que_llega_distinto_se_reconcilia_y_lo_dice(self):
        self.correr(aplicar=True)
        nuevo = self.escribir(con_cantidad(texto(PRESUPUESTO), "CAS-00004", "EST-10010", "40"), "presupuesto.csv")
        self.assertEqual(self.correr(presupuesto=nuevo), 0)
        t = self.salida.getvalue()
        self.assertIn("CAS-00004  ZAFIRO 1.0 (172 M2) — ya está y llega distinto: se reconcilia (1 cantidades · 0 altas · 0 bajas)", t)
        self.assertIn(f"cantidad EST-10010   37 → 40  ({self.K1})", t)
        self.assertEqual(len(self.cat.cargas()), 1)  # revisar no escribe
        self.assertEqual(self.correr(presupuesto=nuevo, aplicar=True), 0)
        self.assertIn("Carga 2 aplicada.", self.salida.getvalue())
        self.assertEqual(self.correr(presupuesto=nuevo, aplicar=True), 0)
        self.assertIn("No había nada que aplicar.", self.salida.getvalue())

    def test_una_baja_se_confirma_con_su_id_o_con_todas(self):
        self.correr(aplicar=True)
        sin = self.escribir(sin_renglon(texto(PRESUPUESTO), "CAS-00004", "EST-10010"), "presupuesto.csv")
        self.assertEqual(self.correr(presupuesto=sin, aplicar=True), 0)
        t = self.salida.getvalue()
        self.assertIn(f"baja     EST-10010   × 37  ({self.K1})  [DETENIDO: una baja pide confirmación]", t)
        self.assertIn("baja_sin_confirmar", str(self.cat.cargas()[-1].resumen))
        self.assertEqual(self.correr(presupuesto=sin, aplicar=True, bajas=[self.K1]), 0)
        self.assertEqual(self.correr(presupuesto=sin), 0)
        self.assertIn("ya está, igual", self.salida.getvalue())
        otro = self.escribir(sin_renglon(texto(PRESUPUESTO), "CAS-00004", "EST-10011"), "presupuesto2.csv")
        self.assertEqual(self.correr(presupuesto=otro, aplicar=True, todas_las_bajas=True), 0)

    def test_lo_contratado_se_dice_detenido(self):
        self.correr(aplicar=True)
        ServicioContratacion(self.cat).contratar("CAS-00004", "control_de_obra", "luis@obra.mx", "CAS-00004#1/NIV-00001#1")
        nuevo = self.escribir(con_cantidad(texto(PRESUPUESTO), "CAS-00004", "EST-10010", "40"), "presupuesto.csv")
        self.assertEqual(self.correr(presupuesto=nuevo, aplicar=True), 0)
        self.assertIn("[DETENIDO: lo usa algo contratado: va a control de cambio]", self.salida.getvalue())

    def test_la_terminal_dice_que_programas_citan_lo_que_se_da_de_baja(self):
        self.correr(aplicar=True)
        pro = MemoriaPrograma()
        pid = ServicioPrograma(pro).importar("Zafiro de obra", programa("Zafiro"), CAL, "control_de_obra", "luis@obra.mx")
        ServicioColgado(ServicioPrograma(pro), self.cat).colgar(pid, "control_de_obra", "luis@obra.mx")
        sin = self.escribir(sin_renglon(texto(PRESUPUESTO), "CAS-00004", "EST-10010"), "presupuesto.csv")
        self.assertEqual(self.correr(presupuesto=sin, programas=pro), 0)
        self.assertIn(f"{self.K1}: lo cita el programa {pid} «Zafiro de obra» en 1 fila(s)", self.salida.getvalue())
        self.assertEqual(self.correr(presupuesto=self.escribir(con_cantidad(texto(PRESUPUESTO), "CAS-00004", "EST-10010", "40"), "p2.csv"), programas=pro), 0)
        self.assertNotIn("Programas que citan", self.salida.getvalue())  # una cantidad no quita el piso a nadie

    # ------------------------------------------------------------------ el texto que cambia (D-477)
    def test_un_texto_que_cambia_se_dice_y_con_la_receta_se_detiene_y_propone_clave_nueva(self):
        self.correr(aplicar=True)
        presupuesto = self.escribir(con_descripcion_del_concepto(texto(PRESUPUESTO), "EST-10010", lambda d: d.replace("4.00", "5.00")), "presupuesto.csv")
        self.assertEqual(self.correr(presupuesto=presupuesto), 0)
        t = self.salida.getvalue()
        self.assertIn("Descripciones que cambiaron (§2.7.1)", t)
        self.assertIn("EST-10010    ALTA        4 → 5", t)
        self.assertNotIn("DETENIDO", t)
        conceptos = self.escribir(reescalar_linea(texto(CONCEPTOS), "EST-10010", 0, Decimal("1.01")))
        self.assertEqual(self.correr(conceptos=conceptos, presupuesto=presupuesto, aplicar=True), 0)
        t = self.salida.getvalue()
        self.assertIn("[DETENIDO — clave nueva propuesta: EST-", t)
        self.assertIn("parece otro concepto", t)
        self.assertEqual(len(self.cat.versiones("EST-10010")), 1)
        self.assertEqual(self.correr(conceptos=conceptos, presupuesto=presupuesto, aplicar=True, confirmados=["EST-10010"]), 0)
        self.assertEqual(len(self.cat.versiones("EST-10010")), 2)


if __name__ == "__main__":
    unittest.main()
