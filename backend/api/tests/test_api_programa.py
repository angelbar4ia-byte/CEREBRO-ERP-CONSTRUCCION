"""
La API del programa, con los programas reales y el adaptador en memoria.

Lo que se prueba es lo que una pantalla necesita saber de la API: ver el programa, proponer sin guardar,
aplicar con su impacto, deshacer, y que cada falla diga qué pasó con el código que le toca (403, 404, 409, 422).
"""
import unittest
from datetime import date

from fastapi.testclient import TestClient

from api.app import crear_app
from core.memoria_programa import MemoriaPrograma
from core.servicio_programa import ServicioPrograma
from api.tests.ayudas import NO_HABILES, csv_de, mueve_fila
from core.tests.contrato_programa import CAL, programa

CO = {"X-Rol": "control_de_obra", "X-Usuario": "luis"}
RES = {"X-Rol": "residente", "X-Usuario": "ana"}


class PruebasApi(unittest.TestCase):
    def setUp(self):
        self.repo = MemoriaPrograma()
        self.plus = programa("Zafiro Plus")
        self.pid = self.repo.importar_programa("Zafiro Plus", self.plus, CAL)
        self.c = TestClient(crear_app(ServicioPrograma(self.repo)))
        self.f = {x.fila: x.llave for x in self.plus.filas}
        self.p16 = {"edicion": {"edicion": "agregar_vinculo", "predecesora": self.f[978], "sucesora": self.f[1102], "tipo": "FS", "desfase": "1"}}

    # ------------------------------------------------------------------ la lista y subir un programa
    def test_la_lista_trae_lo_que_hay(self):
        r = self.c.get("/programas")
        self.assertEqual(r.status_code, 200)
        (p,) = r.json()
        self.assertEqual((p["id"], p["nombre"], p["version"], p["ediciones"], p["importado_por"]), (self.pid, "Zafiro Plus", 0, 0, None))
        self.assertEqual((p["partidas"], p["vinculos"], p["rechazados"]), (len(self.plus.ventanas), len(self.plus.vinculos), len(self.plus.rechazados)))

    def test_subir_un_programa_real_dice_que_se_cargo_y_que_no(self):
        zafiro = programa("Zafiro")
        r = self.c.post("/programas", json={"nombre": " Zafiro subido ", "csv": csv_de("Zafiro"), "no_habiles": NO_HABILES}, headers=CO)
        self.assertEqual(r.status_code, 201, r.text)
        j = r.json()
        s = j["resumen"]
        self.assertEqual((s["nombre"], s["partidas"], s["vinculos"], s["rechazados"]), ("Zafiro subido", len(zafiro.ventanas), 118, 6))
        self.assertEqual((s["importado_por"], s["importado_con_rol"], s["version"], s["ediciones"]), ("luis", "control_de_obra", 0, 0))
        # los seis que el cargador de D-442 rechaza, cada uno con su motivo y la partida que lo traía
        self.assertEqual(sorted((x["fila"], x["token"], x["motivo"]) for x in j["rechazados"]), sorted((x.fila, x.token, x.motivo) for x in zafiro.rechazados))
        self.assertTrue(all(x["clave"] and x["descripcion"] for x in j["rechazados"]))
        self.assertEqual(j["incumplidos"], len(zafiro.incumplidos(CAL)))
        self.assertEqual([p["nombre"] for p in self.c.get("/programas").json()], ["Zafiro Plus", "Zafiro subido"])
        self.assertEqual(self.c.get(f"/programas/{s['id']}").json()["calendario"]["no_habiles"], NO_HABILES)

    def test_un_programa_subido_se_abre_y_se_edita_igual(self):
        pid = self.c.post("/programas", json={"nombre": "Plus 2", "csv": csv_de("Zafiro Plus"), "no_habiles": NO_HABILES}, headers=CO).json()["resumen"]["id"]
        self.assertEqual(self.c.get(f"/programas/{pid}/gantt").status_code, 200)
        r = self.c.post(f"/programas/{pid}/ediciones", json=self.p16, headers=CO)
        self.assertEqual((r.status_code, r.json()["impacto"]["dias_de_cambio"]), (201, 10))  # el mismo P16 que sobre el original
        self.assertEqual(self.c.get(f"/programas/{self.pid}").json()["version"], 0)  # y el original ni se enteró

    def test_el_archivo_de_los_siete_pide_decir_cual(self):
        todo = csv_de()
        r = self.c.post("/programas", json={"nombre": "x", "csv": todo}, headers=CO)
        self.assertEqual((r.status_code, r.json()["detail"]["codigo"]), (422, "importacion_invalida"))
        self.assertIn("varios programas", r.json()["detail"]["mensaje"])
        ok = self.c.post("/programas", json={"nombre": "Rubí", "csv": todo, "prototipo": "Rubí", "no_habiles": NO_HABILES}, headers=CO)
        self.assertEqual((ok.status_code, ok.json()["resumen"]["partidas"]), (201, len(programa("Rubí").ventanas)))
        mal = self.c.post("/programas", json={"nombre": "x", "csv": todo, "prototipo": "Ónix"}, headers=CO)
        self.assertEqual(mal.status_code, 422)
        self.assertIn("Ónix", mal.json()["detail"]["mensaje"])

    def test_el_csv_de_excel_en_espanol_tambien_entra(self):
        r = self.c.post("/programas", json={"nombre": "x", "csv": csv_de("Zafiro Plus", delimitador=";", bom=True), "no_habiles": NO_HABILES}, headers=CO)
        self.assertEqual((r.status_code, r.json()["resumen"]["partidas"]), (201, len(self.plus.ventanas)))

    def test_sin_permiso_se_sabe_antes_de_leer_el_archivo(self):
        basura = {"nombre": "x", "csv": "esto no es un programa"}
        self.assertEqual(self.c.post("/programas", json=basura).status_code, 401)
        r = self.c.post("/programas", json=basura, headers=RES)
        self.assertEqual((r.status_code, r.json()["detail"]["codigo"]), (403, "permiso_denegado"))  # y no el 422 del archivo
        self.assertEqual(len(self.c.get("/programas").json()), 1)

    def test_lo_que_no_es_un_programa_se_dice_con_la_linea_y_no_se_guarda_nada(self):
        casos = {
            "faltan columnas": ("oid,fila\n1,1\n", "faltan columnas"),
            "fecha ilegible": (csv_de("Zafiro", cambia=lambda r: r.update(inicio="9 de junio") if r["fila"] == "6" else None), "línea 6"),
            "oid repetido": (csv_de("Zafiro", cambia=lambda r: r.update(oid="5570560") if r["fila"] == "7" else None), "ya está en la línea"),
            "fila repetida": (csv_de("Zafiro", cambia=lambda r: r.update(fila="6") if r["fila"] == "7" else None), "la fila 6 ya está"),
            "tipo desconocido": (csv_de("Zafiro", cambia=lambda r: r.update(tipo="Partida") if r["fila"] == "6" else None), "uno de:"),
            "termina antes de empezar": (csv_de("Zafiro", cambia=lambda r: r.update(termino="2025-01-01") if r["fila"] == "6" else None), "anterior a"),
            "sin partidas": (csv_de("Zafiro", cambia=lambda r: r.update(dias_laborables="0")), "ninguna partida"),
            "vacío": ("", "está vacío"),
            "solo el encabezado": (csv_de("Zafiro").split("\n", 1)[0] + "\n", "ninguna fila"),
        }
        for nombre, (texto, esperado) in casos.items():
            r = self.c.post("/programas", json={"nombre": "x", "csv": texto, "no_habiles": NO_HABILES}, headers=CO)
            self.assertEqual((r.status_code, r.json()["detail"]["codigo"]), (422, "importacion_invalida"), nombre)
            self.assertIn(esperado, r.json()["detail"]["mensaje"], nombre)
        self.assertEqual(len(self.c.get("/programas").json()), 1)

    def test_el_nombre_en_blanco_y_los_dias_mal_escritos_son_422(self):
        for cuerpo in ({"nombre": "", "csv": csv_de("Zafiro Plus")}, {"nombre": "   ", "csv": csv_de("Zafiro Plus")},
                       {"nombre": "x", "csv": csv_de("Zafiro Plus"), "no_habiles": ["25/12/2025"]}):
            self.assertEqual(self.c.post("/programas", json=cuerpo, headers=CO).status_code, 422, cuerpo["nombre"])
        self.assertEqual(len(self.c.get("/programas").json()), 1)

    # ------------------------------------------------------------------ la versión nueva de un programa
    def _historia(self):
        for cuerpo, h in ((self.p16, CO), ({"edicion": {"edicion": "cambiar_duracion", "llave": self.f[982], "dias": "12"}}, CO),
                          ({"edicion": {"edicion": "fijar_inicio", "llave": self.f[1087], "fecha": "2025-10-30"}}, RES)):
            self.assertEqual(self.c.post(f"/programas/{self.pid}/ediciones", json=cuerpo, headers=h).status_code, 201)

    def test_la_version_nueva_dice_lo_que_paso_con_cada_edicion(self):
        self._historia()
        r = self.c.post(f"/programas/{self.pid}/versiones", json={"nombre": "Zafiro Plus v2", "csv": csv_de("Zafiro Plus", cambia=mueve_fila(1087, 2))}, headers=CO)
        self.assertEqual(r.status_code, 201, r.text)
        j = r.json()
        self.assertEqual((j["pasaron"], [(n["secuencia"], n["motivo"], n["usuario"], n["rol"]) for n in j["no_pasaron"]]),
                         (2, [(3, "la_version_nueva_ya_la_cambio", "ana", "residente")]))
        self.assertIn("no arranca antes del 2025-10-30", j["no_pasaron"][0]["texto"])
        s = j["resumen"]
        self.assertEqual((s["nombre"], s["version_de"], s["ediciones"], s["version"], s["importado_por"]), ("Zafiro Plus v2", self.pid, 2, 2, "luis"))
        nuevo = self.c.get(f"/programas/{s['id']}").json()
        self.assertEqual((nuevo["version_de"], nuevo["traspaso"]["de"], nuevo["traspaso"]["pasaron"], len(nuevo["traspaso"]["no_pasaron"])), (self.pid, self.pid, 2, 1))
        self.assertEqual([(e["usuario"], e["rol"], e["estado"]) for e in nuevo["guardadas"]], [("luis", "control_de_obra", "aplicada")] * 2)
        viejo = self.c.get(f"/programas/{self.pid}").json()
        self.assertEqual((viejo["reemplazado_por"], viejo["version"], len(viejo["guardadas"])), (s["id"], 3, 3))
        self.assertEqual([x["reemplazado_por"] for x in self.c.get("/programas").json()], [s["id"], None])

    def test_la_version_nueva_hereda_el_nombre_y_el_calendario_si_no_se_dicen(self):
        r = self.c.post(f"/programas/{self.pid}/versiones", json={"csv": csv_de("Zafiro Plus")}, headers=CO).json()
        self.assertEqual(r["resumen"]["nombre"], "Zafiro Plus")
        self.assertEqual(self.c.get(f"/programas/{r['resumen']['id']}").json()["calendario"]["no_habiles"], ["2025-12-25", "2026-01-01"])
        otra = self.c.post(f"/programas/{r['resumen']['id']}/versiones", json={"csv": csv_de("Zafiro Plus"), "no_habiles": ["2025-12-25"]}, headers=CO).json()
        self.assertEqual(self.c.get(f"/programas/{otra['resumen']['id']}").json()["calendario"]["no_habiles"], ["2025-12-25"])

    def test_una_version_nueva_solo_se_sube_sobre_la_ultima(self):
        primera = self.c.post(f"/programas/{self.pid}/versiones", json={"csv": csv_de("Zafiro Plus")}, headers=CO).json()["resumen"]["id"]
        r = self.c.post(f"/programas/{self.pid}/versiones", json={"csv": csv_de("Zafiro Plus")}, headers=CO)
        self.assertEqual((r.status_code, r.json()["detail"]["codigo"], r.json()["detail"]["reemplazado_por"]), (409, "reemplazado", primera))
        self.assertEqual(len(self.c.get("/programas").json()), 2)

    def test_una_pantalla_vieja_no_sube_la_version_nueva(self):
        visto = self.c.get(f"/programas/{self.pid}").json()["version"]
        self.c.post(f"/programas/{self.pid}/ediciones", json=self.p16, headers=CO)
        r = self.c.post(f"/programas/{self.pid}/versiones", json={"csv": csv_de("Zafiro Plus"), "esperaba": visto}, headers=CO)
        self.assertEqual((r.status_code, r.json()["detail"]["codigo"]), (409, "conflicto"))
        self.assertEqual(len(self.c.get("/programas").json()), 1)

    def test_la_version_nueva_pide_permiso_antes_de_leer_y_dice_cuando_el_archivo_no_sirve(self):
        basura = {"csv": "esto no es un programa"}
        self.assertEqual(self.c.post(f"/programas/{self.pid}/versiones", json=basura).status_code, 401)
        self.assertEqual(self.c.post(f"/programas/{self.pid}/versiones", json=basura, headers=RES).json()["detail"]["codigo"], "permiso_denegado")
        r = self.c.post(f"/programas/{self.pid}/versiones", json=basura, headers=CO)
        self.assertEqual((r.status_code, r.json()["detail"]["codigo"]), (422, "importacion_invalida"))
        self.assertEqual(self.c.post("/programas/9999/versiones", json=basura, headers=CO).status_code, 404)
        self.assertEqual(len(self.c.get("/programas").json()), 1)

    def test_la_pantalla_sabe_de_donde_viene_y_a_donde_fue(self):
        nuevo = self.c.post(f"/programas/{self.pid}/versiones", json={"csv": csv_de("Zafiro Plus")}, headers=CO).json()["resumen"]["id"]
        self.assertIn('"reemplazado_por":%d' % nuevo, self.c.get(f"/programas/{self.pid}/gantt").text)
        html = self.c.get(f"/programas/{nuevo}/gantt").text
        self.assertIn('"version_de":%d' % self.pid, html)
        self.assertIn('"traspaso":{"de":%d' % self.pid, html)

    def test_el_texto_de_quien_sube_no_se_toma_por_html(self):
        malo = lambda r: r.update(descripcion="</script><img src=x onerror=alert(1)>") if r["fila"] == "6" else None
        propio = "<script>alert(1)</script>"
        pid = self.c.post("/programas", json={"nombre": propio, "csv": csv_de("Zafiro", cambia=malo), "no_habiles": NO_HABILES}, headers=CO).json()["resumen"]["id"]
        html = self.c.get(f"/programas/{pid}/gantt").text
        normal = self.c.get(f"/programas/{self.pid}/gantt").text
        self.assertIn("<title>Gantt &lt;script&gt;alert(1)&lt;/script&gt;</title>", html)
        self.assertNotIn(propio, html)
        self.assertNotIn("</script><img", html)
        self.assertEqual(html.count("</script>"), normal.count("</script>"))  # ningún dato cerró un script de la página
        self.assertIn("\\u003c/script>\\u003cimg", html)  # viaja como dato, escapado

    def test_un_titulo_que_parece_marca_no_cambia_la_plantilla(self):
        pid = self.c.post("/programas", json={"nombre": "__DATOS__ /*__MOTOR__*/", "csv": csv_de("Zafiro Plus"), "no_habiles": NO_HABILES}, headers=CO).json()["resumen"]["id"]
        html = self.c.get(f"/programas/{pid}/gantt").text
        self.assertIn("<title>Gantt __DATOS__ /*__MOTOR__*/</title>", html)
        self.assertEqual(html.count("const Motor = "), 1)

    def test_la_pantalla_de_los_programas_no_lleva_datos(self):
        r = self.c.get("/")
        self.assertEqual(r.status_code, 200)
        self.assertIn("<title>Programas</title>", r.text)
        self.assertIn("const ClientePrograma", r.text)
        self.assertNotIn("Zafiro Plus", r.text)  # la lista se pide a la API

    # ------------------------------------------------------------------ ver
    def test_ver_el_programa(self):
        r = self.c.get(f"/programas/{self.pid}")
        self.assertEqual(r.status_code, 200)
        j = r.json()
        self.assertEqual((j["nombre"], j["version"], j["guardadas"]), ("Zafiro Plus", 0, []))
        self.assertEqual(len(j["vista"]["red"]["partidas"]), 388)
        self.assertEqual(j["calendario"]["no_habiles"], ["2025-12-25", "2026-01-01"])

    def test_un_programa_que_no_existe_es_404(self):
        self.assertEqual(self.c.get("/programas/9999").json()["detail"]["codigo"], "programa_inexistente")
        self.assertEqual(self.c.get("/programas/9999").status_code, 404)

    # ------------------------------------------------------------------ proponer
    def test_proponer_dice_que_pasaria_y_no_guarda(self):
        r = self.c.post(f"/programas/{self.pid}/propuestas", json=self.p16, headers=CO)
        self.assertEqual(r.status_code, 200)
        j = r.json()
        self.assertTrue(j["aplicable"])
        self.assertEqual((j["impacto"]["fin_antes"], j["impacto"]["fin_despues"], j["impacto"]["dias_de_cambio"]), ("2026-01-05", "2026-01-19", 10))
        self.assertEqual(j["impacto"]["partidas_movidas"], len(j["impacto"]["movidas"]))
        self.assertEqual(j["esperaba"], 0)
        self.assertEqual(self.c.get(f"/programas/{self.pid}/ediciones").json(), [])

    def test_una_propuesta_que_no_se_puede_aplicar_dice_por_que(self):
        e = {"edicion": {"edicion": "agregar_vinculo", "predecesora": self.f[1102], "sucesora": self.f[1102], "tipo": "FS", "desfase": "0"}}
        j = self.c.post(f"/programas/{self.pid}/propuestas", json=e, headers=CO).json()
        self.assertFalse(j["aplicable"])
        self.assertEqual([r["motivo"] for r in j["rechazadas"]], ["autovinculo"])

    # ------------------------------------------------------------------ aplicar
    def test_aplicar_guarda_y_devuelve_lo_guardado(self):
        r = self.c.post(f"/programas/{self.pid}/ediciones", json=self.p16, headers=CO)
        self.assertEqual(r.status_code, 201)
        g = r.json()["guardada"]
        self.assertEqual((g["secuencia"], g["rol"], g["usuario"], g["estado"]), (1, "control_de_obra", "luis", "aplicada"))
        self.assertEqual(g["impacto"]["dias_de_cambio"], 10)
        j = self.c.get(f"/programas/{self.pid}").json()
        self.assertEqual(j["version"], 1)
        self.assertEqual(j["guardadas"][0]["edicion"], {**self.p16["edicion"], "origen": None})

    def test_los_dias_cruzan_como_texto(self):
        e = {"edicion": {"edicion": "cambiar_duracion", "llave": self.f[982], "dias": "12"}}
        r = self.c.post(f"/programas/{self.pid}/ediciones", json=e, headers=CO)
        self.assertEqual(r.status_code, 201)
        self.assertEqual(r.json()["guardada"]["edicion"]["dias"], "12")

    def test_sin_decir_quien_eres_no_se_edita(self):
        r = self.c.post(f"/programas/{self.pid}/ediciones", json=self.p16)
        self.assertEqual((r.status_code, r.json()["detail"]["codigo"]), (401, "sin_identidad"))

    def test_el_rol_equivocado_es_403(self):
        r = self.c.post(f"/programas/{self.pid}/ediciones", json=self.p16, headers=RES)
        self.assertEqual((r.status_code, r.json()["detail"]["codigo"]), (403, "permiso_denegado"))
        fijar = {"edicion": {"edicion": "fijar_inicio", "llave": self.f[1102], "fecha": "2025-10-28"}}
        self.assertEqual(self.c.post(f"/programas/{self.pid}/ediciones", json=fijar, headers=CO).status_code, 403)
        self.assertEqual(self.c.post(f"/programas/{self.pid}/ediciones", json=fijar, headers=RES).status_code, 201)

    def test_lo_que_no_se_puede_aplicar_es_422_y_no_se_guarda(self):
        e = {"edicion": {"edicion": "cambiar_duracion", "llave": self.f[982], "dias": "0"}}
        r = self.c.post(f"/programas/{self.pid}/ediciones", json=e, headers=CO)
        self.assertEqual((r.status_code, r.json()["detail"]["codigo"], r.json()["detail"]["rechazadas"]), (422, "no_aplicable", ["duracion_invalida"]))
        self.assertEqual(self.c.get(f"/programas/{self.pid}/ediciones").json(), [])

    def test_una_edicion_que_no_se_entiende_es_422(self):
        for cuerpo in ({"edicion": {"edicion": "inventada"}}, {"edicion": {"edicion": "cambiar_duracion", "llave": "x"}}, {"edicion": {}}):
            r = self.c.post(f"/programas/{self.pid}/propuestas", json=cuerpo, headers=CO)
            self.assertEqual((r.status_code, r.json()["detail"]["codigo"]), (422, "edicion_invalida"), cuerpo)

    def test_la_version_dice_en_que_quedo_el_programa(self):
        p = self.c.post(f"/programas/{self.pid}/propuestas", json=self.p16, headers=CO).json()
        self.assertEqual((p["esperaba"], p["version"]), (0, 0))  # proponer no cambia nada
        g = self.c.post(f"/programas/{self.pid}/ediciones", json=self.p16, headers=CO).json()
        self.assertEqual((g["esperaba"], g["version"]), (0, 1))

    def test_una_pantalla_vieja_recibe_409_y_no_se_guarda(self):
        otra = {"edicion": {"edicion": "cambiar_duracion", "llave": self.f[982], "dias": "12"}}
        self.assertEqual(self.c.post(f"/programas/{self.pid}/ediciones", json=self.p16, headers=CO).status_code, 201)
        r = self.c.post(f"/programas/{self.pid}/ediciones", json={**otra, "esperaba": 0}, headers=CO)
        self.assertEqual((r.status_code, r.json()["detail"]["codigo"]), (409, "conflicto"))
        self.assertEqual(len(self.c.get(f"/programas/{self.pid}/ediciones").json()), 1)
        self.assertEqual(self.c.post(f"/programas/{self.pid}/ediciones", json={**otra, "esperaba": 1}, headers=CO).status_code, 201)

    # ------------------------------------------------------------------ deshacer
    def test_deshacer_y_la_bitacora_se_queda(self):
        g = self.c.post(f"/programas/{self.pid}/ediciones", json=self.p16, headers=CO).json()["guardada"]
        r = self.c.delete(f"/programas/{self.pid}/ediciones/{g['id']}", headers=CO)
        self.assertEqual(r.status_code, 200)
        j = r.json()
        self.assertEqual((j["version"], j["fin"]), (2, "2026-01-05"))
        self.assertEqual([(e["estado"], e["revertida_por"]) for e in j["guardadas"]], [("revertida", "luis")])

    def test_no_se_deshace_lo_que_otra_necesita_409(self):
        g = self.c.post(f"/programas/{self.pid}/ediciones", json=self.p16, headers=CO).json()["guardada"]
        cambiar = {"edicion": {"edicion": "cambiar_vinculo", "predecesora": self.f[978], "sucesora": self.f[1102], "tipo_actual": "FS", "tipo": "SS", "desfase": "0"}}
        self.assertEqual(self.c.post(f"/programas/{self.pid}/ediciones", json=cambiar, headers=CO).status_code, 201)
        r = self.c.delete(f"/programas/{self.pid}/ediciones/{g['id']}", headers=CO)
        self.assertEqual((r.status_code, r.json()["detail"]["codigo"], r.json()["detail"]["dependientes"]), (409, "dependen", [2]))

    def test_deshacer_con_el_rol_equivocado_o_algo_que_no_existe(self):
        g = self.c.post(f"/programas/{self.pid}/ediciones", json=self.p16, headers=CO).json()["guardada"]
        self.assertEqual(self.c.delete(f"/programas/{self.pid}/ediciones/{g['id']}", headers=RES).status_code, 403)
        self.assertEqual(self.c.delete(f"/programas/{self.pid}/ediciones/9999", headers=CO).status_code, 404)

    # ------------------------------------------------------------------ la pantalla
    def test_la_pantalla_sale_de_la_api_y_trae_lo_guardado(self):
        self.c.post(f"/programas/{self.pid}/ediciones", json=self.p16, headers=CO)
        r = self.c.get(f"/programas/{self.pid}/gantt")
        self.assertEqual(r.status_code, 200)
        self.assertIn("<title>Gantt Zafiro Plus</title>", r.text)
        self.assertIn('"api":{"programa":%d,"version":1' % self.pid, r.text)

    # ------------------------------------------------------------------ el spec
    def test_el_spec_nombra_las_operaciones_en_espanol(self):
        ops = {op["operationId"] for ruta in self.c.get("/openapi.json").json()["paths"].values() for op in ruta.values()}
        self.assertEqual(ops, {"listar_programas", "importar_programa", "subir_version", "pantalla_programas", "ver_programa", "ver_bitacora",
                               "proponer_edicion", "aplicar_edicion", "deshacer_edicion", "pantalla_gantt"})


if __name__ == "__main__":
    unittest.main()
