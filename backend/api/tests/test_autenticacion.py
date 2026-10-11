"""
La autenticación por token (B-96, D-469), con llaves de verdad: HS256 con un secreto, y RS256 y ES256 con llaves
públicas publicadas en un JWKS, como las que da un proveedor. Lo que se prueba es lo que importa de un token:
que el bueno pase y que ninguno de los malos —vencido, sin vencimiento, con otra firma, `none`, firmado con la llave
pública como si fuera secreto— lo haga; y que la API, con ese verificador y los usuarios reales, deje o no deje hacer.
"""
import json
import time
import unittest

import jwt
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ec, rsa
from fastapi.testclient import TestClient

from api.app import crear_app
from api.autenticacion import ErrorDeToken, VerificadorJWT, emitir_token, por_token
from api.tests.ayudas import csv_de
from core.accesos import MemoriaAccesos
from core.memoria_programa import MemoriaPrograma
from core.servicio_programa import ServicioPrograma
from core.tests.contrato_programa import CAL, programa

SECRETO = "un-secreto-compartido-de-prueba-largo-de-32-bytes!"
LOGIN = "https://proveedor.example/entrar"


def _llaves():
    rsa_privada = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    ec_privada = ec.generate_private_key(ec.SECP256R1())
    return rsa_privada, ec_privada


def _jwk(privada, kid, alg):
    cls = jwt.algorithms.RSAAlgorithm if alg == "RS256" else jwt.algorithms.ECAlgorithm
    d = json.loads(cls.to_jwk(privada.public_key()))
    d.update({"kid": kid, "alg": alg, "use": "sig"})
    return d


def _pem(privada):
    return privada.private_bytes(serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8, serialization.NoEncryption())


def _token(llave, alg, correo="luis@obra.mx", kid=None, **extra):
    datos = {"email": correo, "exp": int(time.time()) + 3600, **extra}
    return jwt.encode(datos, llave, algorithm=alg, headers={"kid": kid} if kid else None)


class PruebasVerificador(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rsa, cls.ec = _llaves()
        cls.otra_rsa, _ = _llaves()
        cls.jwks = {"keys": [_jwk(cls.rsa, "k-rsa", "RS256"), _jwk(cls.ec, "k-ec", "ES256")]}

    def casi(self, f, codigo):
        with self.assertRaises(ErrorDeToken) as cm:
            f()
        self.assertEqual(cm.exception.codigo, codigo)

    # ------------------------------------------------------------------ secreto compartido (HS256)
    def test_un_token_bueno_da_el_correo_en_minusculas(self):
        v = VerificadorJWT(secreto=SECRETO)
        self.assertEqual(v.correo_de(emitir_token(SECRETO, "Luis.Perez@Obra.MX")), "luis.perez@obra.mx")

    def test_un_token_de_supabase_con_aud_authenticated_pasa_si_no_se_pidio_audiencia(self):
        v = VerificadorJWT(secreto=SECRETO)
        self.assertEqual(v.correo_de(_token(SECRETO, "HS256", aud="authenticated", sub="3f2c-uuid", role="authenticated")), "luis@obra.mx")

    def test_vencido_no_pasa_pero_con_el_margen_de_reloj_si(self):
        v = VerificadorJWT(secreto=SECRETO)
        self.casi(lambda: v.correo_de(_token(SECRETO, "HS256", exp=int(time.time()) - 120)), "token_vencido")
        self.assertEqual(v.correo_de(_token(SECRETO, "HS256", exp=int(time.time()) - 10)), "luis@obra.mx")  # relojes desfasados

    def test_un_token_sin_vencimiento_no_pasa(self):
        v = VerificadorJWT(secreto=SECRETO)
        sin_exp = jwt.encode({"email": "luis@obra.mx"}, SECRETO, algorithm="HS256")
        self.casi(lambda: v.correo_de(sin_exp), "token_invalido")

    def test_otra_firma_no_pasa(self):
        v = VerificadorJWT(secreto=SECRETO)
        self.casi(lambda: v.correo_de(emitir_token("otro-secreto-de-prueba-de-32-bytes-o-mas!!", "luis@obra.mx")), "token_invalido")
        bueno = emitir_token(SECRETO, "luis@obra.mx")
        manipulado = bueno[:-3] + ("AAA" if not bueno.endswith("AAA") else "BBB")
        self.casi(lambda: v.correo_de(manipulado), "token_invalido")

    def test_alg_none_no_pasa(self):
        v = VerificadorJWT(secreto=SECRETO)
        sin_firma = jwt.encode({"email": "luis@obra.mx", "exp": int(time.time()) + 3600}, None, algorithm="none")
        self.casi(lambda: v.correo_de(sin_firma), "token_invalido")

    def test_lo_que_no_es_un_token_no_pasa(self):
        v = VerificadorJWT(secreto=SECRETO)
        for basura in ("", "no.es.token", "a.b.c", "x" * 40):
            self.casi(lambda: v.correo_de(basura), "token_invalido")

    def test_sin_ninguna_llave_no_se_puede_ni_armar_el_verificador(self):
        with self.assertRaises(ValueError):
            VerificadorJWT()

    # ------------------------------------------------------------------ llaves públicas (JWKS)
    def test_rs256_y_es256_con_la_llave_publicada_pasan(self):
        v = VerificadorJWT(jwks=self.jwks)
        self.assertEqual(v.correo_de(_token(self.rsa, "RS256", kid="k-rsa")), "luis@obra.mx")
        self.assertEqual(v.correo_de(_token(self.ec, "ES256", kid="k-ec")), "luis@obra.mx")

    def test_una_firma_de_otra_llave_o_un_kid_que_no_existe_no_pasan(self):
        v = VerificadorJWT(jwks=self.jwks)
        self.casi(lambda: v.correo_de(_token(self.otra_rsa, "RS256", kid="k-rsa")), "token_invalido")  # dice ser la buena
        self.casi(lambda: v.correo_de(_token(self.rsa, "RS256", kid="otra")), "token_invalido")
        self.casi(lambda: v.correo_de(_token(self.ec, "ES256", kid="k-rsa")), "token_invalido")  # llave de otro tipo

    def test_el_algoritmo_lo_fija_el_servidor_y_no_el_token(self):
        solo_secreto, solo_jwks = VerificadorJWT(secreto=SECRETO), VerificadorJWT(jwks=self.jwks)
        self.casi(lambda: solo_secreto.correo_de(_token(self.rsa, "RS256", kid="k-rsa")), "token_invalido")  # no hay llave pública configurada
        self.casi(lambda: solo_jwks.correo_de(emitir_token(SECRETO, "luis@obra.mx")), "token_invalido")  # no hay secreto configurado

    def test_la_confusion_de_algoritmos_no_pasa(self):
        # el ataque clásico: firmar con HS256 usando como secreto la llave pública, que es pública, esperando que el servidor la use
        publica = self.rsa.public_key().public_bytes(serialization.Encoding.PEM, serialization.PublicFormat.SubjectPublicKeyInfo)
        # PyJWT ya se niega a firmar así; se arma a mano con HMAC para probar al verificador, no a la biblioteca
        import base64
        import hashlib
        import hmac

        def b64(b):
            return base64.urlsafe_b64encode(b).rstrip(b"=").decode()

        cabecera = b64(json.dumps({"alg": "HS256", "typ": "JWT", "kid": "k-rsa"}).encode())
        cuerpo = b64(json.dumps({"email": "luis@obra.mx", "exp": int(time.time()) + 3600}).encode())
        firma = b64(hmac.new(publica, f"{cabecera}.{cuerpo}".encode(), hashlib.sha256).digest())
        token = f"{cabecera}.{cuerpo}.{firma}"
        for v in (VerificadorJWT(jwks=self.jwks), VerificadorJWT(secreto=SECRETO, jwks=self.jwks)):
            self.casi(lambda: v.correo_de(token), "token_invalido")

    def test_con_secreto_y_llaves_publicas_cada_algoritmo_usa_la_suya(self):
        v = VerificadorJWT(secreto=SECRETO, jwks=self.jwks)
        self.assertEqual(v.correo_de(emitir_token(SECRETO, "ana@obra.mx")), "ana@obra.mx")
        self.assertEqual(v.correo_de(_token(self.rsa, "RS256", correo="ana@obra.mx", kid="k-rsa")), "ana@obra.mx")

    # ------------------------------------------------------------------ audiencia, emisor y correo
    def test_audiencia_y_emisor_si_se_pidieron(self):
        v = VerificadorJWT(secreto=SECRETO, audiencia="programa", emisor="https://proveedor.example")
        self.assertEqual(v.correo_de(emitir_token(SECRETO, "luis@obra.mx", audiencia="programa", emisor="https://proveedor.example")), "luis@obra.mx")
        self.casi(lambda: v.correo_de(emitir_token(SECRETO, "luis@obra.mx", audiencia="otra", emisor="https://proveedor.example")), "token_invalido")
        self.casi(lambda: v.correo_de(emitir_token(SECRETO, "luis@obra.mx", audiencia="programa", emisor="https://otro.example")), "token_invalido")
        self.casi(lambda: v.correo_de(emitir_token(SECRETO, "luis@obra.mx")), "token_invalido")  # sin audiencia ni emisor

    def test_sin_correo_el_token_no_sirve(self):
        v = VerificadorJWT(secreto=SECRETO)
        exp = int(time.time()) + 3600
        for datos in ({"exp": exp}, {"exp": exp, "email": 7}, {"exp": exp, "email": "sin-arroba"}, {"exp": exp, "email": None}):
            self.casi(lambda: v.correo_de(jwt.encode(datos, SECRETO, algorithm="HS256")), "token_sin_correo")

    def test_el_reclamo_del_correo_se_puede_cambiar(self):
        v = VerificadorJWT(secreto=SECRETO, reclamo_correo="mail")
        self.assertEqual(v.correo_de(emitir_token(SECRETO, "luis@obra.mx", reclamo_correo="mail")), "luis@obra.mx")
        self.casi(lambda: v.correo_de(emitir_token(SECRETO, "luis@obra.mx")), "token_sin_correo")


class PruebasApiConToken(unittest.TestCase):
    def setUp(self):
        self.repo = MemoriaPrograma()
        self.plus = programa("Zafiro Plus")
        self.pid = self.repo.importar_programa("Zafiro Plus", self.plus, CAL)
        self.f = {x.fila: x.llave for x in self.plus.filas}
        self.accesos = MemoriaAccesos()
        self.accesos.agregar_usuario("Luis Pérez", "luis@obra.mx", ["control_de_obra"])
        self.accesos.agregar_usuario("Ana Soto", "ana@obra.mx", ["residente"])
        self.accesos.agregar_usuario("Doble", "doble@obra.mx", ["supervisor", "residente"])
        self.accesos.agregar_usuario("Sin Rol", "sinrol@obra.mx", [])
        self.accesos.agregar_usuario("Retirado", "retirado@obra.mx", ["control_de_obra"])
        self.accesos.desactivar_usuario("retirado@obra.mx")
        auth = por_token(VerificadorJWT(secreto=SECRETO), self.accesos, login_url=LOGIN)
        self.c = TestClient(crear_app(ServicioPrograma(self.repo, permisos=self.accesos.permisos), auth))
        self.p16 = {"edicion": {"edicion": "agregar_vinculo", "predecesora": self.f[978], "sucesora": self.f[1102], "tipo": "FS", "desfase": "1"}}
        self.fecha = {"edicion": {"edicion": "fijar_inicio", "llave": self.f[1087], "fecha": "2025-10-30"}}

    def de(self, correo):
        return {"Authorization": "Bearer " + emitir_token(SECRETO, correo)}

    # ------------------------------------------------------------------ sin token, o con uno que no sirve
    def test_sin_token_nada_de_datos_sale(self):
        for metodo, ruta in (("get", "/programas"), ("get", f"/programas/{self.pid}"), ("get", f"/programas/{self.pid}/ediciones"), ("get", "/yo")):
            r = getattr(self.c, metodo)(ruta)
            self.assertEqual((r.status_code, r.json()["detail"]["codigo"]), (401, "sin_token"), ruta)
            self.assertEqual(r.json()["detail"]["login_url"], LOGIN)
            self.assertEqual(r.headers["www-authenticate"], "Bearer")
        for ruta in ("/programas", f"/programas/{self.pid}/ediciones", f"/programas/{self.pid}/propuestas", f"/programas/{self.pid}/versiones"):
            self.assertEqual(self.c.post(ruta, json=self.p16).status_code, 401, ruta)
        self.assertEqual(self.c.delete(f"/programas/{self.pid}/ediciones/1").status_code, 401)

    def test_un_token_que_no_sirve_es_401_con_su_motivo(self):
        malos = {
            "token_invalido": {"Authorization": "Bearer basura"},
            "token_vencido": {"Authorization": "Bearer " + emitir_token(SECRETO, "luis@obra.mx", horas=0.5, ahora=time.time() - 7200)},
            "sin_token": {"Authorization": "Basic bHVpczpjbGF2ZQ=="},
        }
        for codigo, cabeceras in malos.items():
            r = self.c.get("/programas", headers=cabeceras)
            self.assertEqual((r.status_code, r.json()["detail"]["codigo"]), (401, codigo))

    def test_un_token_bueno_de_quien_no_esta_dado_de_alta_o_se_retiro_es_403(self):
        r = self.c.get("/programas", headers=self.de("nadie@obra.mx"))
        self.assertEqual((r.status_code, r.json()["detail"]["codigo"]), (403, "usuario_desconocido"))
        r = self.c.get("/programas", headers=self.de("retirado@obra.mx"))
        self.assertEqual((r.status_code, r.json()["detail"]["codigo"]), (403, "usuario_inactivo"))

    def test_las_cabeceras_provisionales_no_sirven_para_nada_en_modo_token(self):
        r = self.c.get("/programas", headers={"X-Rol": "control_de_obra", "X-Usuario": "luis"})
        self.assertEqual(r.status_code, 401)
        h = {**self.de("ana@obra.mx"), "X-Rol": "control_de_obra"}  # un token de Residente y una cabecera que dice otra cosa
        self.assertEqual(self.c.post(f"/programas/{self.pid}/ediciones", json=self.p16, headers=h).status_code, 403)

    # ------------------------------------------------------------------ con token
    def test_quien_soy_dice_roles_y_lo_que_puede_hacer(self):
        j = self.c.get("/yo", headers=self.de("Luis@Obra.MX")).json()
        self.assertEqual((j["nombre"], j["correo"], j["usuario"], j["roles"], j["modo"]), ("Luis Pérez", "luis@obra.mx", "luis@obra.mx", ["control_de_obra"], "token"))
        self.assertEqual(j["funciones"], ["editar_estructura_programa"])
        j = self.c.get("/yo", headers=self.de("doble@obra.mx")).json()
        self.assertEqual((j["roles"], j["funciones"]), (["residente", "supervisor"], ["editar_fechas_programa"]))
        self.assertEqual(self.c.get("/yo", headers=self.de("sinrol@obra.mx")).json()["funciones"], [])

    def test_con_token_se_ve_y_se_edita_lo_que_el_rol_permite(self):
        luis, ana = self.de("luis@obra.mx"), self.de("ana@obra.mx")
        self.assertEqual(len(self.c.get("/programas", headers=luis).json()), 1)
        self.assertEqual(self.c.get(f"/programas/{self.pid}", headers=ana).status_code, 200)  # ver lo ve cualquiera con sesión
        g = self.c.post(f"/programas/{self.pid}/ediciones", json=self.p16, headers=luis).json()["guardada"]
        self.assertEqual((g["usuario"], g["rol"]), ("luis@obra.mx", "control_de_obra"))  # queda el correo: no se repite ni se confunde
        r = self.c.post(f"/programas/{self.pid}/ediciones", json=self.p16 | {"edicion": {**self.p16["edicion"], "desfase": "2"}}, headers=ana)
        self.assertEqual((r.status_code, r.json()["detail"]["codigo"]), (403, "permiso_denegado"))  # la estructura no es de Residente
        g2 = self.c.post(f"/programas/{self.pid}/ediciones", json=self.fecha, headers=ana).json()["guardada"]
        self.assertEqual((g2["usuario"], g2["rol"]), ("ana@obra.mx", "residente"))
        self.assertEqual(self.c.post(f"/programas/{self.pid}/ediciones", json=self.fecha, headers=self.de("sinrol@obra.mx")).status_code, 403)

    def test_quien_tiene_dos_roles_queda_con_el_que_puede(self):
        g = self.c.post(f"/programas/{self.pid}/ediciones", json=self.fecha, headers=self.de("doble@obra.mx")).json()["guardada"]
        self.assertEqual((g["usuario"], g["rol"]), ("doble@obra.mx", "residente"))  # el supervisor no puede fechas; el residente sí
        r = self.c.post(f"/programas/{self.pid}/ediciones", json=self.p16, headers=self.de("doble@obra.mx"))
        self.assertIn("ninguno de tus roles (residente, supervisor)", r.json()["detail"]["mensaje"])

    def test_deshacer_pide_el_permiso_de_la_edicion_y_queda_quien_lo_hizo(self):
        e = self.c.post(f"/programas/{self.pid}/ediciones", json=self.p16, headers=self.de("luis@obra.mx")).json()["guardada"]
        self.assertEqual(self.c.delete(f"/programas/{self.pid}/ediciones/{e['id']}", headers=self.de("ana@obra.mx")).status_code, 403)
        r = self.c.delete(f"/programas/{self.pid}/ediciones/{e['id']}", headers=self.de("luis@obra.mx"))
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json()["guardadas"][0]["revertida_por"], "luis@obra.mx")

    def test_subir_programas_pide_el_permiso_y_queda_quien_lo_subio(self):
        cuerpo = {"nombre": "Zafiro", "csv": csv_de("Zafiro"), "no_habiles": ["2025-12-25", "2026-01-01"]}
        r = self.c.post("/programas", json=cuerpo, headers=self.de("ana@obra.mx"))
        self.assertEqual((r.status_code, r.json()["detail"]["codigo"]), (403, "permiso_denegado"))
        r = self.c.post("/programas", json=cuerpo, headers=self.de("luis@obra.mx"))
        self.assertEqual((r.status_code, r.json()["resumen"]["importado_por"], r.json()["resumen"]["importado_con_rol"]), (201, "luis@obra.mx", "control_de_obra"))

    def test_la_tabla_de_permisos_manda_y_vale_en_la_siguiente_accion(self):
        ana = self.de("ana@obra.mx")
        self.assertEqual(self.c.post(f"/programas/{self.pid}/ediciones", json=self.p16, headers=ana).status_code, 403)
        self.accesos.dar_funcion("residente", "editar_estructura_programa")  # `gestionar_rol_funcion`
        self.assertEqual(self.c.post(f"/programas/{self.pid}/ediciones", json=self.p16, headers=ana).status_code, 201)
        self.assertIn("editar_estructura_programa", self.c.get("/yo", headers=ana).json()["funciones"])

    def test_un_usuario_que_se_retira_pierde_el_acceso_aunque_su_token_siga_vigente(self):
        luis = self.de("luis@obra.mx")
        self.assertEqual(self.c.get("/programas", headers=luis).status_code, 200)
        self.accesos.desactivar_usuario("luis@obra.mx")
        self.assertEqual(self.c.get("/programas", headers=luis).status_code, 403)

    # ------------------------------------------------------------------ las pantallas
    def test_las_pantallas_se_abren_sin_token_y_dicen_como_entrar(self):
        for ruta in ("/", f"/programas/{self.pid}/gantt"):
            r = self.c.get(ruta)
            self.assertEqual(r.status_code, 200, ruta)
            self.assertIn('"modo":"token"', r.text)
            self.assertIn(f'"login_url":"{LOGIN}"', r.text)
            self.assertNotIn("Zafiro Plus", r.text)  # y no llevan nada del programa


if __name__ == "__main__":
    unittest.main()
