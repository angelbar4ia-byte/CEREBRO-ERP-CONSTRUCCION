"""
Las pantallas en un navegador de verdad, contra un servidor de verdad y con los programas reales.

Es lo único que prueba lo que el usuario toca: que la pantalla en vivo muestra lo guardado, que lo que se decide
queda por guardar hasta que se guarda, que se guarda con quién y qué impacto, que se puede deshacer, que el rol
equivocado se avisa, y que una pantalla vieja no pisa lo que otro guardó; que la lista muestra los programas y
deja subir uno diciendo qué vínculos no entraron; y que el texto de quien sube un programa nunca se toma por HTML. Se salta si no hay `playwright` o un
Chromium (en el CI de GitHub se instalan).
"""
import unittest

from api.tests.ayudas import NO_HABILES, csv_de, mueve_fila
from api.tests.servidor import ServidorDePrueba
from dataclasses import replace

from core.programa import CambiarDuracion, FijarInicio, cargar_programa
from core.servicio_programa import ServicioPrograma
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

    # ------------------------------------------------------------------ la lista de programas
    def inicio(self, usuario="luis", rol="control_de_obra"):
        pg = self.navegador.new_page(viewport={"width": 1400, "height": 900})
        pg.on("pageerror", lambda e: self.errores.append(f"error de la página: {e}"))
        self.paginas.append(pg)
        pg.goto(f"{self.servidor.url}/")
        pg.wait_for_selector("#lista table, #lista .vacio:not(:has-text('Cargando'))")
        pg.select_option("#q-rol", rol)
        pg.fill("#q-usuario", usuario)
        return pg

    def subir(self, pg, csv, nombre="Zafiro subido", prototipo="", no_habiles="\n".join(NO_HABILES)):
        pg.fill("#f-nombre", nombre)
        pg.set_input_files("#f-archivo", files=[{"name": "programa.csv", "mimeType": "text/csv", "buffer": csv.encode("utf-8")}])
        pg.fill("#f-prototipo", prototipo)
        pg.fill("#f-no-habiles", no_habiles)
        pg.click("#f-subir")

    def test_la_lista_muestra_los_programas_y_enlaza_a_su_gantt(self):
        pg = self.inicio()
        fila = pg.locator("#lista tbody tr", has_text="Zafiro Plus").first
        self.assertIn("388", fila.inner_text())
        fila.locator("a").click()
        pg.wait_for_selector("#etiquetas .fila-eti")
        self.assertIn("Gantt Zafiro Plus", pg.inner_text("h1"))
        pg.click("#atras")  # y de vuelta a la lista
        pg.wait_for_selector("#lista table")

    def test_subir_un_programa_dice_que_se_cargo_y_cuales_vinculos_no(self):
        pg = self.inicio()
        self.subir(pg, csv_de("Zafiro"))
        pg.wait_for_selector("#reporte:not([hidden])")
        texto = pg.inner_text("#reporte")
        self.assertIn("Se subió «Zafiro subido»", texto)
        self.assertEqual(pg.locator("#reporte tbody tr").count(), 6)  # los seis que el cargador de D-442 no acepta
        self.assertIn("118", texto)
        self.assertIn("cierra un ciclo", texto)  # cada motivo, en palabras
        self.assertTrue(pg.locator("#lista tbody tr", has_text="Zafiro subido").count() >= 1)
        self.assertIn("luis", pg.locator("#lista tbody tr", has_text="Zafiro subido").first.inner_text())
        pg.click("#reporte a")
        pg.wait_for_selector("#etiquetas .fila-eti")
        self.assertIn("Gantt Zafiro subido", pg.inner_text("h1"))

    def test_lo_que_sale_mal_al_subir_se_dice_y_no_se_pierde_lo_escrito(self):
        pg = self.inicio()
        self.subir(pg, "esto,no,es,un,programa\n1,2,3,4,5\n")
        pg.wait_for_function("document.querySelector('#aviso') && !document.querySelector('#aviso').hidden")
        self.assertIn("faltan columnas", pg.inner_text("#aviso"))
        self.assertEqual(pg.input_value("#f-nombre"), "Zafiro subido")  # el formulario se queda como estaba
        pg.select_option("#q-rol", "residente")  # y con el rol equivocado, el servidor lo dice antes de leer nada
        pg.click("#f-subir")
        pg.wait_for_function("document.querySelector('#aviso').textContent.includes('residente')")
        pg.fill("#q-usuario", "")
        pg.click("#f-subir")
        self.assertIn("tu nombre", pg.inner_text("#aviso"))

    # ------------------------------------------------------------------ la versión nueva de un programa
    def test_subir_la_version_nueva_desde_la_lista_y_ver_lo_que_paso(self):
        from datetime import date
        from fractions import Fraction

        sv = ServicioPrograma(self.servidor.repo)
        sv.aplicar(self.pid, CambiarDuracion(self.f[982], Fraction(12)), "control_de_obra", "luis")
        sv.aplicar(self.pid, FijarInicio(self.f[1087], date(2025, 10, 30)), "residente", "ana")
        pg = self.inicio(usuario="marta")
        pg.locator(f'button[data-version="{self.pid}"]').click()
        self.assertEqual(pg.input_value("#f-nombre"), "Zafiro Plus")  # propone el mismo nombre
        pg.fill("#f-nombre", "Zafiro Plus v2")
        pg.set_input_files("#f-archivo", files=[{"name": "v2.csv", "mimeType": "text/csv", "buffer": csv_de("Zafiro Plus", cambia=mueve_fila(1087, 2)).encode()}])
        pg.fill("#f-prototipo", "")
        pg.click("#f-subir")
        pg.wait_for_selector("#reporte:not([hidden])")
        texto = pg.inner_text("#reporte")
        self.assertIn("como versión nueva de «Zafiro Plus»", texto)
        self.assertIn("1 edición pasó a la versión nueva", texto)  # la de luis, que el archivo nuevo no tocó
        self.assertIn("1 no pasó", texto)  # la de ana
        self.assertEqual(pg.locator("#reporte tbody tr").count(), 1)  # la de ana: la versión nueva ya movió esa partida
        self.assertIn("El archivo nuevo ya cambió esa partida", pg.inner_text("#reporte tbody"))
        self.assertIn("ana (Residente)", pg.inner_text("#reporte tbody"))
        antes = pg.locator("#lista tbody tr", has_text="Zafiro Plus").filter(has=pg.locator(f'a[href="/programas/{self.pid}/gantt"]'))
        self.assertIn("reemplazado por", antes.inner_text())
        self.assertEqual(antes.locator("button[data-version]").count(), 0)  # sobre la última, no sobre esta
        pg.click("#reporte a")
        pg.wait_for_selector("#etiquetas .fila-eti")
        self.assertTrue(pg.locator("#version-aviso").is_visible())
        self.assertIn("Versión nueva de «Zafiro Plus»", pg.inner_text("#version-aviso"))
        pg.click("#version-aviso summary")
        no_paso = pg.inner_text("#version-aviso li")
        self.assertIn("no arranca antes del 2025-10-30", no_paso)
        self.assertIn("ana (Residente)", no_paso)
        pg.click("#bitacora summary")
        self.assertIn("1 aplicada", pg.inner_text("#bitacora summary"))
        fila = pg.inner_text("#bitacora li")
        self.assertIn("luis (Control de obra)", fila)  # conserva quién la decidió
        self.assertIn("pasó de la versión anterior", fila)
        pg.goto(f"{self.servidor.url}/programas/{self.pid}/gantt")  # y el viejo avisa que ya hay uno nuevo
        pg.wait_for_selector("#etiquetas .fila-eti")
        self.assertIn("versión más nueva", pg.inner_text("#version-aviso"))
        pg.click("#version-aviso a")
        pg.wait_for_selector("#etiquetas .fila-eti")
        self.assertIn("Gantt Zafiro Plus v2", pg.inner_text("h1"))

    def test_si_alguien_edito_la_pantalla_de_la_lista_lo_dice_y_se_actualiza(self):
        from fractions import Fraction

        pg = self.inicio(usuario="marta")
        ServicioPrograma(self.servidor.repo).aplicar(self.pid, CambiarDuracion(self.f[982], Fraction(12)), "control_de_obra", "luis")  # después de abrir la lista
        pg.locator(f'button[data-version="{self.pid}"]').click()
        pg.fill("#f-nombre", "v2")
        pg.set_input_files("#f-archivo", files=[{"name": "v2.csv", "mimeType": "text/csv", "buffer": csv_de("Zafiro Plus").encode()}])
        pg.click("#f-subir")
        pg.wait_for_function("document.querySelector('#aviso') && !document.querySelector('#aviso').hidden")
        self.assertIn("Alguien editó", pg.inner_text("#aviso"))
        self.assertEqual(pg.locator("#reporte:not([hidden])").count(), 0)
        pg.click("#f-subir")  # ya con la lista al día
        pg.wait_for_selector("#reporte:not([hidden])")
        self.assertIn("1", pg.inner_text("#reporte .cifras"))

    def test_el_texto_ajeno_del_traspaso_se_ve_como_texto(self):
        from datetime import date

        avisos = []
        pg = self.inicio(usuario="marta")
        pg.on("dialog", lambda d: (avisos.append(d.message), d.dismiss()))
        # quien decidió se llama como un HTML, y la clave de la partida también
        filas = [replace(f, clave="<b id=intruso2>EST") if f.fila == 1087 else f for f in self.plus.filas]
        sv = ServicioPrograma(self.servidor.repo)
        malo = sv.importar("Con clave rara", cargar_programa(filas, CAL), CAL, "control_de_obra", "luis")
        sv.aplicar(malo, FijarInicio(self.f[1087], date(2025, 10, 30)), "residente", "<img src=x onerror=alert(3)>")
        pg.reload()
        pg.wait_for_selector("#lista table")
        pg.locator(f'button[data-version="{malo}"]').click()
        pg.fill("#f-nombre", "v2 rara")
        pg.set_input_files("#f-archivo", files=[{"name": "v2.csv", "mimeType": "text/csv", "buffer": csv_de("Zafiro Plus", cambia=mueve_fila(1087, 2)).encode()}])
        pg.click("#f-subir")
        pg.wait_for_selector("#reporte:not([hidden])")
        self.assertIn("<b id=intruso2>EST", pg.inner_text("#reporte tbody"))
        self.assertIn("<img src=x onerror=alert(3)>", pg.inner_text("#reporte tbody"))
        pg.click("#reporte a")
        pg.wait_for_selector("#etiquetas .fila-eti")
        pg.click("#version-aviso summary")
        self.assertIn("<b id=intruso2>EST", pg.inner_text("#version-aviso li"))
        self.assertEqual(pg.locator("img, #intruso2").count(), 0)
        pg.wait_for_timeout(300)
        self.assertEqual(avisos, [])

    # ------------------------------------------------------------------ el texto de otros no es HTML
    def test_lo_que_trae_el_programa_se_ve_como_texto_y_no_se_ejecuta(self):
        avisos = []
        malo = lambda r: r.update(descripcion="<img src=x onerror=alert(1)> losa") if r["fila"] == "6" else None
        propio = "<b id=intruso>Zafiro</b>"
        pg = self.inicio(usuario="<img src=x onerror=alert(2)>")
        pg.on("dialog", lambda d: (avisos.append(d.message), d.dismiss()))
        self.subir(pg, csv_de("Zafiro", cambia=malo), nombre=propio)
        pg.wait_for_selector("#reporte:not([hidden])")
        self.assertIn(propio, pg.inner_text("#lista"))  # el nombre se lee tal cual
        pg.click("#reporte a")
        pg.wait_for_selector("#etiquetas .fila-eti")
        self.assertIn("<b id=intruso>Zafiro</b>", pg.inner_text("h1"))
        pg.click("#b-todo")
        etiqueta = pg.locator(".fila-eti .desc", has_text="<img src=x onerror=alert(1)>")
        self.assertEqual(etiqueta.count(), 1)  # la descripción está ahí, como letras
        etiqueta.click()
        self.assertIn("<img src=x onerror=alert(1)>", pg.inner_text("#panel h2"))
        # y quien edita con un nombre que parece HTML tampoco rompe la bitácora
        pg.fill("#e-dur", "12")
        pg.click("#e-dur-ok")
        pg.click("#b-guardar")
        pg.wait_for_selector("#b-guardar", state="detached")
        pg.click("#bitacora summary")
        self.assertIn("<img src=x onerror=alert(2)>", pg.inner_text("#bitacora li"))
        self.assertEqual(pg.locator("img, #intruso").count(), 0)  # nada se coló al documento
        pg.wait_for_timeout(300)
        self.assertEqual(avisos, [])  # y ningún script corrió

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
