"""
La pantalla del Gantt en un navegador de verdad, contra un servidor de verdad y con el programa real de Zafiro Plus.

Es lo único que prueba lo que el usuario toca: que la pantalla en vivo muestra lo guardado, que lo que se decide
queda por guardar hasta que se guarda, que se guarda con quién y qué impacto, que se puede deshacer, que el rol
equivocado se avisa, y que una pantalla vieja no pisa lo que otro guardó. Se salta si no hay `playwright` o un
Chromium (en el CI de GitHub se instalan).
"""
import unittest

from api.tests.servidor import ServidorDePrueba
from core.tests.contrato_programa import CAL, programa

try:
    from playwright.sync_api import sync_playwright
except ImportError:  # pragma: no cover
    sync_playwright = None

CHROMIUM_LOCAL = "/opt/pw-browsers/chromium"  # el de los entornos de Claude Code, cuando la versión de playwright no coincide


def _lanzar(p):
    for opciones in ({}, {"executable_path": CHROMIUM_LOCAL, "args": ["--no-sandbox"]}):
        try:
            return p.chromium.launch(**opciones)
        except Exception:  # noqa: BLE001 — cualquier falla al lanzar es «no hay navegador»
            continue
    return None


@unittest.skipIf(sync_playwright is None, "no hay playwright")
class PruebasPantalla(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pw = sync_playwright().start()
        cls.navegador = _lanzar(cls.pw)
        if cls.navegador is None:
            cls.pw.stop()
            raise unittest.SkipTest("no hay un Chromium para lanzar")
        cls.servidor = ServidorDePrueba().arrancar()
        cls.plus = programa("Zafiro Plus")
        cls.f = {x.fila: x.llave for x in cls.plus.filas}

    @classmethod
    def tearDownClass(cls):
        cls.navegador.close()
        cls.pw.stop()
        cls.servidor.apagar()

    def setUp(self):
        self.pid = self.servidor.repo.importar_programa("Zafiro Plus", self.plus, CAL)  # uno nuevo por prueba: sin herencias
        self.errores = []
        self.paginas = []

    def tearDown(self):
        for pg in self.paginas:
            pg.close()
        # una falla de la pantalla (no de la red externa de las tipografías) es una falla de la prueba
        propios = [e for e in self.errores if e.startswith("error de la página")]
        self.assertEqual(propios, [])

    # ------------------------------------------------------------------ ayudas
    def abrir(self, usuario="luis", rol="control_de_obra"):
        pg = self.navegador.new_page(viewport={"width": 1400, "height": 900})
        pg.on("pageerror", lambda e: self.errores.append(f"error de la página: {e}"))
        self.paginas.append(pg)
        pg.goto(f"{self.servidor.url}/programas/{self.pid}/gantt")
        pg.wait_for_selector("#etiquetas .fila-eti")
        pg.select_option("#q-rol", rol)
        pg.fill("#q-usuario", usuario)
        return pg

    def fila(self, pg, n):
        pg.click("#b-todo")
        pg.locator(f'.fila-eti[data-l="{self.f[n]}"]').click()

    def duracion(self, pg, n, dias):
        self.fila(pg, n)
        pg.fill("#e-dur", str(dias))
        pg.click("#e-dur-ok")

    def cierre(self, pg):  # la fecha y lo que se movió, sin la línea de «contra qué se compara»
        return pg.inner_text("#t-cierre .v").replace("\n", " ")

    # ------------------------------------------------------------------ las pruebas
    def test_abre_con_lo_guardado_y_nada_por_guardar(self):
        pg = self.abrir()
        self.assertEqual(pg.locator("#g-quien").is_visible(), True)
        self.assertIn("versión 0", pg.inner_text("#q-version"))
        self.assertIn("Sin ediciones", pg.inner_text("#ediciones"))
        self.assertIn("5-ene-2026", self.cierre(pg))
        self.assertIn("0 aplicada", pg.inner_text("#bitacora summary"))

    def test_lo_que_se_decide_queda_por_guardar_y_al_guardar_entra_a_la_bitacora(self):
        pg = self.abrir()
        self.duracion(pg, 982, 12)
        self.assertIn("por guardar", pg.inner_text("#ediciones").lower())
        self.assertEqual(pg.locator("#ediciones .chip").count(), 1)
        self.assertEqual(len(self.servidor.repo.ediciones(self.pid)), 0)  # todavía no se guardó nada
        antes = self.cierre(pg)
        pg.click("#b-guardar")
        pg.wait_for_selector("#b-guardar", state="detached")
        self.assertEqual(self.cierre(pg), antes)  # guardar no cambia lo que se ve
        self.assertIn("1 edición(es) guardada(s)", pg.inner_text("#ediciones"))
        pg.click("#bitacora summary")
        fila = pg.inner_text("#bitacora li")
        self.assertIn("luis", fila)
        self.assertIn("Control de obra", fila)
        (e,) = self.servidor.repo.ediciones(self.pid)
        self.assertEqual((e.usuario, e.rol, e.estado), ("luis", "control_de_obra", "aplicada"))

    def test_lo_guardado_se_ve_al_volver_a_abrir_y_se_deshace(self):
        pg = self.abrir()
        self.duracion(pg, 982, 12)
        pg.click("#b-guardar")
        pg.wait_for_selector("#b-guardar", state="detached")
        con_la_edicion = self.cierre(pg)
        otra = self.abrir(usuario="ana")  # otra persona abre la pantalla
        self.assertEqual(self.cierre(otra), con_la_edicion)
        self.assertIn("versión 1", otra.inner_text("#q-version"))
        otra.click("#bitacora summary")
        otra.click("#bitacora button[data-d]")
        otra.wait_for_function("document.querySelector('#bitacora li.revertida') !== null")
        self.assertIn("5-ene-2026", self.cierre(otra))
        self.assertIn("versión 2", otra.inner_text("#q-version"))
        self.assertIn("revertida por ana", otra.inner_text("#bitacora li"))
        (e,) = self.servidor.repo.ediciones(self.pid)
        self.assertEqual((e.estado, e.revertida_por), ("revertida", "ana"))

    def test_el_rol_equivocado_se_avisa_antes_de_guardar(self):
        pg = self.abrir(usuario="ana", rol="residente")
        self.duracion(pg, 982, 12)  # la duración es de Control de obra
        self.assertIn("Control de obra", pg.inner_text("#aviso"))
        self.assertEqual(pg.locator("#ediciones .chip").count(), 0)
        pg.select_option("#q-rol", "control_de_obra")
        self.duracion(pg, 982, 12)
        pg.select_option("#q-rol", "residente")  # cambia de rol con algo por guardar: el servidor lo dice
        pg.click("#b-guardar")
        pg.wait_for_function("document.querySelector('#aviso') && !document.querySelector('#aviso').hidden")
        self.assertIn("residente", pg.inner_text("#aviso"))
        self.assertEqual(pg.locator("#ediciones .chip").count(), 1)  # se queda por guardar: nada se perdió
        self.assertEqual(self.servidor.repo.ediciones(self.pid), [])

    def test_guardar_pide_el_nombre(self):
        pg = self.abrir(usuario="")
        self.duracion(pg, 982, 12)
        pg.click("#b-guardar")
        self.assertIn("tu nombre", pg.inner_text("#aviso"))
        self.assertEqual(self.servidor.repo.ediciones(self.pid), [])

    def test_p16_con_su_origen_se_guarda_y_cierra_diez_dias_despues(self):
        pg = self.abrir()
        self.fila(pg, 1102)
        pg.select_option("#a-tipo", "FS")
        pg.fill("#a-lag", "1")
        pg.select_option("#a-origen", "tecnica")
        pg.click("#a-pick")
        pg.locator(f'.fila-eti[data-l="{self.f[978]}"]').click()
        self.assertIn("19-ene-2026", self.cierre(pg))
        self.assertIn("+10 d hábiles", self.cierre(pg))
        pg.click("#b-guardar")
        pg.wait_for_selector("#b-guardar", state="detached")
        (e,) = self.servidor.repo.ediciones(self.pid)
        self.assertEqual((e.edicion.predecesora, e.edicion.sucesora, e.edicion.origen, e.impacto["dias_de_cambio"]), (self.f[978], self.f[1102], "tecnica", 10))
        pg.click("#bitacora summary")
        self.assertIn("confianza alta", pg.inner_text("#bitacora li"))

    def test_una_pantalla_vieja_no_pisa_lo_que_otro_guardo(self):
        vieja = self.abrir(usuario="ana")
        self.duracion(vieja, 982, 12)  # decide con la versión 0
        nueva = self.abrir(usuario="luis")
        self.duracion(nueva, 1102, 3)
        nueva.click("#b-guardar")
        nueva.wait_for_selector("#b-guardar", state="detached")  # el programa ya va en la versión 1
        vieja.click("#b-guardar")
        vieja.wait_for_function("document.querySelector('#aviso') && !document.querySelector('#aviso').hidden")
        self.assertIn("Alguien editó", vieja.inner_text("#aviso"))
        self.assertEqual(len(self.servidor.repo.ediciones(self.pid)), 1)  # lo de ella no se guardó sobre lo que no vio
        self.assertIn("versión 1", vieja.inner_text("#q-version"))
        self.assertEqual(vieja.locator("#ediciones .chip").count(), 1)  # y su edición sigue ahí, revalidada
        vieja.click("#b-guardar")  # ahora sí, con lo de hoy a la vista
        vieja.wait_for_selector("#b-guardar", state="detached")
        self.assertEqual([e.usuario for e in self.servidor.repo.ediciones(self.pid)], ["luis", "ana"])

    def test_la_simulacion_sin_servidor_sigue_siendo_una_simulacion(self):
        from core.gantt_pagina import pagina_gantt

        pg = self.navegador.new_page(viewport={"width": 1400, "height": 900})
        pg.on("pageerror", lambda e: self.errores.append(f"error de la página: {e}"))
        self.paginas.append(pg)
        pg.set_content(pagina_gantt(self.plus, CAL, "Gantt Zafiro Plus"))
        pg.wait_for_selector("#etiquetas .fila-eti")
        self.assertFalse(pg.locator("#g-quien").is_visible())
        self.assertFalse(pg.locator("#bitacora").is_visible())
        self.duracion(pg, 982, 12)
        self.assertEqual(pg.locator("#b-guardar").count(), 0)
        self.assertIn("Deshacer todo", pg.inner_text("#ediciones"))


if __name__ == "__main__":
    unittest.main()
