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
        self.assertEqual(ops, {"ver_programa", "ver_bitacora", "proponer_edicion", "aplicar_edicion", "deshacer_edicion", "pantalla_gantt"})


if __name__ == "__main__":
    unittest.main()
