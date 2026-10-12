"""
`servir.armar`: cómo queda la aplicación según se pida identidad por token o por cabeceras, y los usuarios que se dan de alta
al arrancar. El arranque de uvicorn no se prueba aquí: lo que importa es lo que `armar` decide.
"""
import unittest

from fastapi.testclient import TestClient

from api.autenticacion import VerificadorJWT, emitir_token
from api.servir import armar, dar_de_alta
from core.accesos import MemoriaAccesos
from core.tests.datos_opus import CONCEPTOS, PRESUPUESTO, texto

SECRETO = "un-secreto-compartido-de-prueba-largo-de-32-bytes!"


class PruebasServir(unittest.TestCase):
    def test_con_verificador_exige_token_y_da_de_alta_a_los_usuarios(self):
        app, programas = armar(None, ["Zafiro Plus"], usuarios=["luis@obra.mx|Luis Pérez|control_de_obra"], verificador=VerificadorJWT(secreto=SECRETO), login_url="https://p.example/entrar")
        c = TestClient(app)
        self.assertEqual([n for _, n in programas], ["Zafiro Plus"])
        self.assertEqual(c.get("/programas").status_code, 401)
        r = c.get("/yo", headers={"Authorization": "Bearer " + emitir_token(SECRETO, "luis@obra.mx")})
        self.assertEqual((r.status_code, r.json()["nombre"], r.json()["roles"]), (200, "Luis Pérez", ["control_de_obra"]))
        self.assertEqual(c.get("/yo", headers={"Authorization": "Bearer " + emitir_token(SECRETO, "otro@obra.mx")}).status_code, 403)

    def test_sin_verificador_son_las_cabeceras_y_los_permisos_salen_de_la_tabla(self):
        app, _ = armar(None, [])
        c = TestClient(app)
        h = {"X-Rol": "control_de_obra", "X-Usuario": "luis"}
        self.assertEqual(c.get("/programas").status_code, 200)  # en modo cabeceras ver no pide identidad
        self.assertEqual(c.get("/yo", headers=h).json()["funciones"], ["aprobar_propuesta", "cargar_catalogo_opus", "clonar_insumo", "contratar_subarbol", "editar_estructura_programa", "resolver_alerta"])

    def test_la_aplicacion_trae_las_rutas_del_catalogo_con_los_mismos_permisos(self):
        app, _ = armar(None, [], usuarios=["ana@obra.mx|Ana Soto|costos", "rosa@obra.mx|Rosa Díaz|residente"], verificador=VerificadorJWT(secreto=SECRETO))
        c = TestClient(app)
        ana, rosa = ({"Authorization": "Bearer " + emitir_token(SECRETO, x)} for x in ("ana@obra.mx", "rosa@obra.mx"))
        cuerpo = {"conceptos": texto(CONCEPTOS), "presupuesto": texto(PRESUPUESTO)}
        self.assertEqual(c.get("/presupuestos").status_code, 401)
        self.assertEqual(c.get("/presupuestos", headers=rosa).json(), [])
        self.assertEqual(c.post("/cargas", json=cuerpo, headers=rosa).status_code, 403)
        self.assertEqual(c.post("/cargas", json=cuerpo, headers=ana).status_code, 201)
        self.assertEqual(len(c.get("/presupuestos", headers=rosa).json()), 7)

    def test_la_aplicacion_trae_la_bandeja_y_aprobar_pide_la_funcion_de_la_tabla(self):
        app, _ = armar(None, [], usuarios=["ana@obra.mx|Ana Soto|costos", "luis@obra.mx|Luis Pérez|control_de_obra"])
        c = TestClient(app)
        ana, luis = ({"X-Rol": rol, "X-Usuario": correo} for rol, correo in (("costos", "ana@obra.mx"), ("control_de_obra", "luis@obra.mx")))
        self.assertEqual(c.get("/bandeja").json()["propuestas_pendientes"], 0)
        propuesta = {"tipo": "equivalencia", "objeto": "ISN-02005", "valor_propuesto": {"equivale_a": "ISN-02001"}, "evidencia": "Descripciones idénticas"}
        self.assertEqual(c.post("/bandeja/propuestas", json=propuesta, headers=ana).status_code, 201)
        self.assertEqual(c.post("/bandeja/propuestas/1/resolucion", json={"decision": "rechazar", "nota": "x"}, headers=ana).status_code, 403)
        self.assertEqual(c.post("/bandeja/propuestas/1/resolucion", json={"decision": "rechazar", "nota": "x"}, headers=luis).status_code, 200)

    def test_dar_de_alta_no_pisa_a_los_que_ya_estan_y_pide_el_formato(self):
        a = MemoriaAccesos()
        dar_de_alta(a, ["luis@obra.mx|Luis|control_de_obra", "ana@obra.mx|Ana|residente,supervisor"])
        dar_de_alta(a, ["luis@obra.mx|Otro Nombre|costos"])  # ya existe: se queda como estaba
        self.assertEqual([(u.correo, u.nombre, u.roles) for u in a.usuarios()],
                         [("luis@obra.mx", "Luis", ("control_de_obra",)), ("ana@obra.mx", "Ana", ("residente", "supervisor"))])
        with self.assertRaises(SystemExit):
            dar_de_alta(a, ["sin-formato"])


if __name__ == "__main__":
    unittest.main()
