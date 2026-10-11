"""
`servir.armar`: cómo queda la aplicación según se pida identidad por token o por cabeceras, y los usuarios que se dan de alta
al arrancar. El arranque de uvicorn no se prueba aquí: lo que importa es lo que `armar` decide.
"""
import unittest

from fastapi.testclient import TestClient

from api.autenticacion import VerificadorJWT, emitir_token
from api.servir import armar, dar_de_alta
from core.accesos import MemoriaAccesos

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
        self.assertEqual(c.get("/yo", headers=h).json()["funciones"], ["cargar_catalogo_opus", "contratar_subarbol", "editar_estructura_programa"])

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
