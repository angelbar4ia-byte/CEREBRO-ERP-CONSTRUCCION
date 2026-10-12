"""
La API de la bandeja (D-485): el contrato que cumple con los adaptadores en memoria y con los de Postgres, con los archivos de OPUS de
verdad. Mezclar con `unittest.TestCase` y definir `nuevos_repositorios()`, que devuelve
`(RepositorioPrograma, RepositorioCatalogo, RepositorioAccesos, RepositorioBandeja)` vacíos y, si son de una base, de la misma.

Lo que se prueba es lo que una pantalla necesita saber: que una propuesta lleva su evidencia y quién la dejó; que aprobar una clonación la
hace el sistema **a nombre de quien aprueba** y solo si tiene las dos funciones; que quien propone no aprueba lo suyo; que lo rechazado se
conserva y no se repite; que una alerta que reaparece se cuenta; y que cada impedimento llega con el código y el estado que le toca.
"""
from decimal import Decimal

from fastapi.testclient import TestClient

from api.app import crear_app
from api.autenticacion import VerificadorJWT, emitir_token, por_token
from core.catalogo import ServicioCarga
from core.propuestas import ServicioBandeja
from core.servicio_programa import ServicioPrograma
from core.tests.datos_opus import CONCEPTOS, PRESUPUESTO, reescalar_costo, texto

CO = {"X-Rol": "control_de_obra", "X-Usuario": "luis@obra.mx"}
COSTOS = {"X-Rol": "costos", "X-Usuario": "ana@obra.mx"}
RES = {"X-Rol": "residente", "X-Usuario": "rosa@obra.mx"}
SUP = {"X-Rol": "supervisor", "X-Usuario": "sofia@obra.mx"}
SECRETO = "un-secreto-compartido-de-prueba-largo-de-32-bytes!"
LOGIN = "https://proveedor.example/entrar"

EVIDENCIA = "AUX-00001 es una trabe terminada: un material, no un auxiliar. Lo citan nueve conceptos de estructura."
CLONAR = {"tipo": "clonacion", "objeto": "AUX-00001", "valor_propuesto": {"original": "AUX-00001", "clave": "PRE-00120"}, "evidencia": EVIDENCIA}
PREFIJO = {"tipo": "clonacion", "objeto": "AUX", "valor_propuesto": {"viejo": "AUX", "nuevo": "PRE", "desde": 120},
           "evidencia": "Las 79 claves AUX- son materiales (P-11)"}
EQUIVALENCIA = {"tipo": "equivalencia", "objeto": "ISN-02005", "valor_propuesto": {"equivale_a": "ISN-02001"}, "evidencia": "Descripciones idénticas"}


class ContratoApiBandeja:
    def nuevos_repositorios(self):  # pragma: no cover
        raise NotImplementedError

    def setUp(self):
        self.pro, self.cat, self.acc, self.bandeja = self.nuevos_repositorios()
        for nombre, correo, roles in (("Luis Pérez", "luis@obra.mx", ["control_de_obra"]), ("Ana Soto", "ana@obra.mx", ["costos"]),
                                      ("Rosa Díaz", "rosa@obra.mx", ["residente"]), ("Sofía Ruiz", "sofia@obra.mx", ["supervisor"]),
                                      ("Sin Rol", "sinrol@obra.mx", [])):
            self.acc.agregar_usuario(nombre, correo, roles)
        self.servicio = ServicioPrograma(self.pro, permisos=self.acc.permisos)
        self.c = TestClient(crear_app(self.servicio, catalogo=self.cat, bandeja=self.bandeja))

    # ------------------------------------------------------------------ ayudas
    def cargado(self):
        ServicioCarga(self.cat).aplicar(texto(CONCEPTOS), texto(PRESUPUESTO), None, rol="costos", usuario="ana@obra.mx")
        return self

    def mover_el_acero(self):
        ServicioCarga(self.cat).aplicar(reescalar_costo(texto(CONCEPTOS), "ACE-00001", Decimal("1.02")), texto(PRESUPUESTO), None,
                                        rol="costos", usuario="ana@obra.mx")

    def codigo(self, r):
        return r.json()["detail"]["codigo"]

    def proponer(self, cuerpo=CLONAR, quien=COSTOS, **cambios):
        r = self.c.post("/bandeja/propuestas", json={**cuerpo, **cambios}, headers=quien)
        self.assertEqual(r.status_code, 201, r.text)
        return r.json()

    def resolver(self, propuesta_id, decision, quien=CO, **cuerpo):
        return self.c.post(f"/bandeja/propuestas/{propuesta_id}/resolucion", json={"decision": decision, **cuerpo}, headers=quien)

    def alertar(self, tipo="avance_sin_orden", objeto="EST-21011", **evidencia):
        return ServicioBandeja(self.bandeja).alertar(tipo, evidencia or {"visto": True}, objeto=objeto)

    # ------------------------------------------------------------------ lo que hay pendiente
    def test_la_bandeja_dice_lo_que_hay_pendiente_de_decidir(self):
        v = self.c.get("/bandeja").json()
        self.assertEqual(v, {"propuestas_pendientes": 0, "pendientes_por_tipo": {}, "alertas_activas": 0, "alertas_por_tipo": {}, "alerta_mas_vista": None})
        p = self.proponer()
        self.proponer(EQUIVALENCIA)
        a = self.alertar()
        self.alertar()  # reaparece sin haberse resuelto
        self.alertar("frente_listo_para_cierre", "FRENTE-1")
        v = self.c.get("/bandeja").json()
        self.assertEqual((v["propuestas_pendientes"], v["pendientes_por_tipo"]), (2, {"clonacion": 1, "equivalencia": 1}))
        self.assertEqual((v["alertas_activas"], v["alertas_por_tipo"]), (2, {"avance_sin_orden": 1, "frente_listo_para_cierre": 1}))
        self.assertEqual((v["alerta_mas_vista"]["id"], v["alerta_mas_vista"]["veces_vista"]), (a.id, 2))  # la que más vuelve
        self.assertEqual(self.resolver(p["id"], "rechazar", nota="Todavía no").status_code, 200)
        self.assertEqual(self.c.get("/bandeja").json()["propuestas_pendientes"], 1)  # lo resuelto ya no está pendiente

    # ------------------------------------------------------------------ dejar una propuesta
    def test_una_propuesta_queda_con_su_evidencia_quien_la_dejo_y_cuando(self):
        p = self.proponer(base=1)
        self.assertEqual((p["id"], p["tipo"], p["objeto"], p["estado"], p["origen"]), (1, "clonacion", "AUX-00001", "pendiente", "usuario"))
        self.assertEqual(p["valor_propuesto"], {"original": "AUX-00001", "clave": "PRE-00120", "modo": "sustituir"})  # el modo por omisión, dicho
        self.assertEqual((p["evidencia"], p["propuesto_por"], p["propuesto_con_rol"], p["base"]), (EVIDENCIA, "ana@obra.mx", "costos", 1))
        self.assertTrue(p["creada_en"])
        self.assertEqual((p["resuelto_por"], p["resuelta_en"], p["nota"], p["resultado"], p["modelo"], p["confianza"]), (None,) * 6)
        self.assertTrue(p["se_puede_aprobar"])
        self.assertEqual(self.c.get(f"/bandeja/propuestas/{p['id']}").json(), p)
        otra = self.proponer(EQUIVALENCIA, quien=RES)
        self.assertEqual((otra["propuesto_por"], otra["propuesto_con_rol"], otra["se_puede_aprobar"]), ("rosa@obra.mx", "residente", False))
        self.assertEqual([x["id"] for x in self.c.get("/bandeja/propuestas").json()], [p["id"], otra["id"]])
        self.assertEqual([x["id"] for x in self.c.get("/bandeja/propuestas", params={"tipo": "equivalencia"}).json()], [otra["id"]])
        self.assertEqual([x["id"] for x in self.c.get("/bandeja/propuestas", params={"estado": "pendiente"}).json()], [p["id"], otra["id"]])
        self.assertEqual(self.c.get("/bandeja/propuestas", params={"estado": "aprobada"}).json(), [])
        r = self.c.get("/bandeja/propuestas/987")
        self.assertEqual((r.status_code, self.codigo(r)), (404, "propuesta_inexistente"))

    def test_lo_que_no_es_una_propuesta_responde_422_y_no_se_guarda(self):
        malas = [
            ({"evidencia": "  "}, "propuesta_invalida"),  # una propuesta sin evidencia es una orden disfrazada
            ({"tipo": "invento"}, "propuesta_invalida"),
            ({"valor_propuesto": {}}, "propuesta_invalida"),  # sin un valor que proponer es una alerta
            ({"valor_propuesto": {"original": "AUX-00001"}}, "propuesta_invalida"),  # falta la clave del clon
            ({"valor_propuesto": {"original": "AUX-00002", "clave": "PRE-00120"}}, "propuesta_invalida"),  # recae en otra cosa que el objeto
            ({"base": -1}, "propuesta_invalida"),
        ]
        for cambio, codigo in malas:
            r = self.c.post("/bandeja/propuestas", json={**CLONAR, **cambio}, headers=COSTOS)
            self.assertEqual((r.status_code, self.codigo(r)), (422, codigo), str(cambio))
        for faltante in ("tipo", "objeto", "valor_propuesto", "evidencia"):  # lo que ni siquiera viene
            r = self.c.post("/bandeja/propuestas", json={k: v for k, v in CLONAR.items() if k != faltante}, headers=COSTOS)
            self.assertEqual(r.status_code, 422, faltante)
        self.assertEqual(self.c.get("/bandeja/propuestas").json(), [])
        self.assertEqual(self.c.post("/bandeja/propuestas", json=CLONAR).status_code, 401)  # y sin saber quién es, nada

    def test_una_igual_pendiente_no_se_amontona_y_una_rechazada_no_se_repite_sin_evidencia_nueva(self):
        p = self.proponer()
        r = self.c.post("/bandeja/propuestas", json=CLONAR, headers=RES)  # otra persona, la misma propuesta
        self.assertEqual((r.status_code, self.codigo(r), r.json()["detail"]["propuesta_id"]), (409, "ya_propuesta", p["id"]))
        self.assertEqual(self.resolver(p["id"], "rechazar", nota="Todavía no: lo decide Costos con el cliente").status_code, 200)
        r = self.c.post("/bandeja/propuestas", json={**CLONAR, "evidencia": EVIDENCIA.upper()}, headers=COSTOS)  # las mismas palabras no son evidencia nueva
        self.assertEqual((r.status_code, self.codigo(r), r.json()["detail"]["propuesta_id"]), (409, "rechazada_antes", p["id"]))
        nueva = self.proponer(evidencia=EVIDENCIA + " Y además el cliente ya lo confirmó por escrito.")
        self.assertEqual((nueva["id"], nueva["estado"]), (2, "pendiente"))

    # ------------------------------------------------------------------ rechazar
    def test_rechazar_pide_la_funcion_y_decir_por_que_y_el_rechazo_se_conserva(self):
        p = self.proponer()
        r = self.resolver(p["id"], "rechazar", quien=COSTOS, nota="no")  # Costos propone, no resuelve la bandeja
        self.assertEqual((r.status_code, self.codigo(r)), (403, "permiso_denegado"))
        for cuerpo in ({}, {"nota": "  "}):  # rechazar sin decir por qué no sirve de nada
            r = self.resolver(p["id"], "rechazar", **cuerpo)
            self.assertEqual((r.status_code, self.codigo(r)), (422, "propuesta_invalida"), str(cuerpo))
        r = self.resolver(p["id"], "quizá", nota="x")
        self.assertEqual((r.status_code, self.codigo(r)), (422, "propuesta_invalida"))
        self.assertEqual(self.c.get(f"/bandeja/propuestas/{p['id']}").json()["estado"], "pendiente")
        r = self.resolver(p["id"], "rechazar", nota="Lo decide Costos")
        j = r.json()
        self.assertEqual(r.status_code, 200, r.text)
        self.assertEqual((j["estado"], j["resuelto_por"], j["resuelto_con_rol"], j["nota"], j["resultado"]), ("rechazada", "luis@obra.mx", "control_de_obra", "Lo decide Costos", None))
        self.assertTrue(j["resuelta_en"])
        self.assertEqual((j["tipo"], j["valor_propuesto"], j["evidencia"]), (p["tipo"], p["valor_propuesto"], p["evidencia"]))  # lo propuesto no cambia
        self.assertEqual([x["id"] for x in self.c.get("/bandeja/propuestas", params={"estado": "rechazada"}).json()], [p["id"]])  # se conserva
        for decision in ("rechazar", "aprobar"):
            r = self.resolver(p["id"], decision, nota="otra vez")
            self.assertEqual((r.status_code, self.codigo(r), r.json()["detail"]["estado"]), (409, "ya_resuelta", "rechazada"))
        r = self.resolver(987, "rechazar", nota="x")
        self.assertEqual((r.status_code, self.codigo(r)), (404, "propuesta_inexistente"))

    # ------------------------------------------------------------------ aprobar
    def test_aprobar_una_clonacion_la_hace_el_sistema_a_nombre_de_quien_aprueba(self):
        self.cargado()
        base = max(c["id"] for c in self.c.get("/cargas").json())  # lo último que vio quien propone: la carga más reciente
        p = self.proponer(base=base)  # Costos la deja: Costos no puede clonar
        r = self.resolver(p["id"], "aprobar", nota="Confirmado con Costos")
        j = r.json()
        self.assertEqual(r.status_code, 200, r.text)
        self.assertEqual((j["estado"], j["resuelto_por"], j["resuelto_con_rol"], j["nota"]), ("aprobada", "luis@obra.mx", "control_de_obra", "Confirmado con Costos"))
        self.assertEqual((j["resultado"]["clon"], j["resultado"]["modo"], j["resultado"]["versiones_nuevas"], j["resultado"]["renglones_fijados"]), ("PRE-00120", "sustituir", 9, 9))
        (clon,) = self.c.get("/clones").json()
        self.assertEqual((clon["original"], clon["clon"], clon["modo"], clon["usuario"], clon["rol"]), ("AUX-00001", "PRE-00120", "sustituir", "luis@obra.mx", "control_de_obra"))
        self.assertEqual(clon["carga_id"], j["resultado"]["carga_id"])  # a nombre de quien aprobó, no de quien propuso
        self.assertEqual(self.c.get("/catalogo/PRE-00120").status_code, 200)
        self.assertEqual(self.c.get("/bandeja").json()["propuestas_pendientes"], 0)

    def test_quien_propone_no_aprueba_lo_suyo(self):
        self.cargado()
        p = self.proponer(quien=CO)  # Control de obra puede clonar y puede resolver, pero no su propia propuesta
        for quien in (CO, {**CO, "X-Usuario": "LUIS@obra.mx"}):
            r = self.resolver(p["id"], "aprobar", quien=quien)
            self.assertEqual((r.status_code, self.codigo(r)), (403, "autoaprobacion"))
        self.assertEqual((self.c.get(f"/bandeja/propuestas/{p['id']}").json()["estado"], self.c.get("/clones").json()), ("pendiente", []))
        self.assertEqual(self.resolver(p["id"], "rechazar", quien=CO, nota="la retiro").status_code, 200)  # retirar lo propio sí se puede

    def test_aprobar_pide_la_funcion_de_la_accion_ademas_de_resolver_la_bandeja(self):
        self.cargado()
        self.acc.dar_funcion("supervisor", "aprobar_propuesta")  # Supervisión puede resolver la bandeja, pero no clonar
        p = self.proponer(quien=RES)
        r = self.resolver(p["id"], "aprobar", quien=SUP)
        self.assertEqual((r.status_code, self.codigo(r)), (403, "permiso_denegado"))
        self.assertIn("clonar", r.json()["detail"]["mensaje"])
        self.assertEqual((self.c.get(f"/bandeja/propuestas/{p['id']}").json()["estado"], self.c.get("/clones").json()), ("pendiente", []))
        self.acc.dar_funcion("supervisor", "clonar_insumo")  # y ahora que sí puede, aprueba
        self.assertEqual(self.resolver(p["id"], "aprobar", quien=SUP).json()["estado"], "aprobada")
        self.assertEqual(self.c.get("/clones").json()[0]["usuario"], "sofia@obra.mx")

    def test_un_tipo_sin_operacion_se_puede_rechazar_pero_no_aprobar(self):
        p = self.proponer(EQUIVALENCIA)
        r = self.resolver(p["id"], "aprobar")
        self.assertEqual((r.status_code, self.codigo(r), r.json()["detail"]["tipo"]), (422, "sin_operacion", "equivalencia"))
        self.assertEqual(self.c.get(f"/bandeja/propuestas/{p['id']}").json()["estado"], "pendiente")  # no se dice que algo se hizo cuando no se hizo
        self.assertEqual(self.resolver(p["id"], "rechazar", nota="No son lo mismo").json()["estado"], "rechazada")

    def test_si_el_catalogo_cambio_desde_que_se_vio_responde_409_y_sigue_pendiente(self):
        self.cargado()
        p = self.proponer(base=1)  # vio el catálogo en la carga 1
        self.mover_el_acero()  # y alguien más carga: ahora va en la 2
        for esperaba in (None, 1):
            r = self.resolver(p["id"], "aprobar", **({} if esperaba is None else {"esperaba": esperaba}))
            self.assertEqual((r.status_code, self.codigo(r)), (409, "conflicto"), str(esperaba))
        self.assertEqual((self.c.get(f"/bandeja/propuestas/{p['id']}").json()["estado"], self.c.get("/clones").json()), ("pendiente", []))
        r = self.resolver(p["id"], "aprobar", esperaba=2)  # quien aprueba mira lo de hoy y lo dice
        self.assertEqual((r.status_code, r.json()["estado"]), (200, "aprobada"))

    def test_lo_que_impide_la_operacion_deja_la_propuesta_pendiente_para_corregirla_o_rechazarla(self):
        self.cargado()
        p = self.proponer(valor_propuesto={"original": "AUX-00001", "clave": "PRE-00001"})  # esa clave ya existe
        r = self.resolver(p["id"], "aprobar")
        self.assertEqual((r.status_code, self.codigo(r)), (422, "clonacion_no_procede"))
        self.assertTrue(r.json()["detail"]["problemas"])
        self.assertEqual((self.c.get(f"/bandeja/propuestas/{p['id']}").json()["estado"], self.c.get("/clones").json()), ("pendiente", []))
        self.assertEqual(self.resolver(p["id"], "rechazar", nota="La clave ya existe").json()["estado"], "rechazada")

    def test_se_aprueba_la_correccion_de_un_prefijo_entero(self):
        self.cargado()
        p = self.proponer(PREFIJO, base=1)
        j = self.resolver(p["id"], "aprobar").json()
        self.assertEqual((len(j["resultado"]["hechos"]), j["resultado"]["rechazados"], j["estado"]), (79, [], "aprobada"))
        self.assertEqual((j["resultado"]["hechos"][0]["clon"], j["resultado"]["hechos"][-1]["clon"]), ("PRE-00120", "PRE-00198"))
        clones = self.c.get("/clones").json()
        self.assertEqual((len(clones), {c["usuario"] for c in clones}), (79, {"luis@obra.mx"}))

    # ------------------------------------------------------------------ alertas
    def test_una_alerta_se_ve_cuantas_veces_volvio_y_se_resuelve_diciendo_que_era(self):
        a = ServicioBandeja(self.bandeja).alertar("pu_movio_mas_de_5", {"antes": "20", "despues": "21.5"}, objeto="ACE-00001", parametro_usado={"umbral": "5"})
        ServicioBandeja(self.bandeja).alertar("pu_movio_mas_de_5", {"antes": "21.5", "despues": "23"}, objeto="ACE-00001")
        otra = self.alertar("frente_listo_para_cierre", "FRENTE-1", avance=0.91)
        j = self.c.get(f"/bandeja/alertas/{a.id}").json()
        self.assertEqual((j["tipo"], j["objeto"], j["veces_vista"], j["estado"], j["parametro_usado"]), ("pu_movio_mas_de_5", "ACE-00001", 2, "activa", {"umbral": "5"}))
        self.assertEqual(j["evidencia"], {"antes": "21.5", "despues": "23"})  # la de la última vez
        self.assertTrue(j["primera_vez"] and j["ultima_vez"])
        self.assertEqual([x["id"] for x in self.c.get("/bandeja/alertas").json()], [a.id, otra.id])
        self.assertEqual([x["id"] for x in self.c.get("/bandeja/alertas", params={"tipo": "frente_listo_para_cierre"}).json()], [otra.id])
        r = self.c.get("/bandeja/alertas/987")
        self.assertEqual((r.status_code, self.codigo(r)), (404, "alerta_inexistente"))
        r = self.c.post(f"/bandeja/alertas/{a.id}/resolucion", json={"estado": "resuelta", "nota": "x"}, headers=COSTOS)  # Costos no resuelve alertas
        self.assertEqual((r.status_code, self.codigo(r)), (403, "permiso_denegado"))
        for cuerpo in ({"estado": "resuelta", "nota": "  "}, {"estado": "quizá", "nota": "x"}):
            r = self.c.post(f"/bandeja/alertas/{a.id}/resolucion", json=cuerpo, headers=SUP)
            self.assertEqual((r.status_code, self.codigo(r)), (422, "propuesta_invalida"), str(cuerpo))
        self.assertEqual(self.c.post(f"/bandeja/alertas/{a.id}/resolucion", json={"estado": "resuelta"}, headers=SUP).status_code, 422)  # ni viene la nota
        r = self.c.post(f"/bandeja/alertas/{a.id}/resolucion", json={"estado": "resuelta", "nota": "Se capturó la orden de cambio"}, headers=SUP)
        j = r.json()
        self.assertEqual(r.status_code, 200, r.text)
        self.assertEqual((j["estado"], j["resuelto_por"], j["resuelto_con_rol"], j["nota_resolucion"]), ("resuelta", "sofia@obra.mx", "supervisor", "Se capturó la orden de cambio"))
        r = self.c.post(f"/bandeja/alertas/{a.id}/resolucion", json={"estado": "descartada", "nota": "otra vez"}, headers=CO)
        self.assertEqual((r.status_code, self.codigo(r), r.json()["detail"]["estado"]), (409, "ya_resuelta", "resuelta"))
        r = self.c.post("/bandeja/alertas/987/resolucion", json={"estado": "resuelta", "nota": "x"}, headers=CO)
        self.assertEqual((r.status_code, self.codigo(r)), (404, "alerta_inexistente"))
        self.assertEqual([x["id"] for x in self.c.get("/bandeja/alertas", params={"estado": "activa"}).json()], [otra.id])
        self.assertEqual(self.c.get("/bandeja").json()["alertas_activas"], 1)

    def test_un_estado_que_no_existe_en_la_lista_responde_422(self):
        for ruta in ("/bandeja/propuestas", "/bandeja/alertas"):
            r = self.c.get(ruta, params={"estado": "olvidada"})
            self.assertEqual((r.status_code, self.codigo(r)), (422, "propuesta_invalida"), ruta)

    # ------------------------------------------------------------------ quién llama
    def test_en_modo_token_el_usuario_y_el_rol_salen_del_token(self):
        self.cargado()
        auth = por_token(VerificadorJWT(secreto=SECRETO), self.acc, LOGIN)
        c = TestClient(crear_app(self.servicio, auth, self.cat, self.bandeja))
        bearer = lambda correo: {"Authorization": "Bearer " + emitir_token(SECRETO, correo)}
        for ruta in ("/bandeja", "/bandeja/propuestas", "/bandeja/propuestas/1", "/bandeja/alertas", "/bandeja/alertas/1"):
            r = c.get(ruta)
            self.assertEqual((r.status_code, self.codigo(r)), (401, "sin_token"), ruta)  # ver también pide saber quién eres
        self.assertEqual(c.post("/bandeja/propuestas", json=CLONAR).status_code, 401)
        r = c.post("/bandeja/propuestas", json=CLONAR, headers=bearer("sinrol@obra.mx"))
        self.assertEqual((r.status_code, self.codigo(r)), (403, "permiso_denegado"))  # sin ningún rol no se deja ni una propuesta
        r = c.post("/bandeja/propuestas", json=CLONAR, headers=bearer("ana@obra.mx"))
        self.assertEqual((r.status_code, r.json()["propuesto_por"], r.json()["propuesto_con_rol"]), (201, "ana@obra.mx", "costos"), r.text)
        r = c.post("/bandeja/propuestas/1/resolucion", json={"decision": "aprobar"}, headers={**bearer("rosa@obra.mx"), "X-Rol": "control_de_obra"})
        self.assertEqual((r.status_code, self.codigo(r)), (403, "permiso_denegado"))  # la cabecera no manda: manda el token
        r = c.post("/bandeja/propuestas/1/resolucion", json={"decision": "aprobar"}, headers=bearer("luis@obra.mx"))
        self.assertEqual((r.status_code, r.json()["resuelto_por"]), (200, "luis@obra.mx"), r.text)
        (clon,) = c.get("/clones", headers=bearer("rosa@obra.mx")).json()
        self.assertEqual((clon["usuario"], clon["rol"]), ("luis@obra.mx", "control_de_obra"))  # el correo del token, no lo que se diga

    def test_lo_que_cambia_la_tabla_de_permisos_vale_desde_la_siguiente_accion(self):
        p = self.proponer(EQUIVALENCIA)
        a = self.alertar()
        quien = {"X-Rol": "residente", "X-Usuario": "rosa@obra.mx"}
        resolver_p = lambda: self.resolver(p["id"], "rechazar", quien=quien, nota="x")
        resolver_a = lambda: self.c.post(f"/bandeja/alertas/{a.id}/resolucion", json={"estado": "resuelta", "nota": "x"}, headers=quien)
        self.assertEqual((resolver_p().status_code, resolver_a().status_code), (403, 403))
        self.acc.dar_funcion("residente", "resolver_alerta")
        self.assertEqual((resolver_p().status_code, resolver_a().status_code), (403, 200))  # una función no da la otra
        self.acc.dar_funcion("residente", "aprobar_propuesta")
        self.assertEqual(resolver_p().status_code, 200)

    # ------------------------------------------------------------------ la forma de la API
    def test_sin_catalogo_la_bandeja_guarda_y_rechaza_pero_no_sabe_aprobar(self):
        c = TestClient(crear_app(self.servicio, bandeja=self.bandeja))
        p = c.post("/bandeja/propuestas", json=CLONAR, headers=COSTOS).json()
        self.assertFalse(p["se_puede_aprobar"])  # nada que la ejecute
        r = c.post(f"/bandeja/propuestas/{p['id']}/resolucion", json={"decision": "aprobar"}, headers=CO)
        self.assertEqual((r.status_code, self.codigo(r)), (422, "sin_operacion"))
        self.assertEqual(c.post(f"/bandeja/propuestas/{p['id']}/resolucion", json={"decision": "rechazar", "nota": "x"}, headers=CO).status_code, 200)

    def test_la_api_sin_bandeja_no_tiene_estas_rutas(self):
        solo = TestClient(crear_app(self.servicio, catalogo=self.cat))
        for ruta in ("/bandeja", "/bandeja/propuestas", "/bandeja/alertas"):
            self.assertEqual(solo.get(ruta).status_code, 404, ruta)
        self.assertEqual(solo.get("/clones").status_code, 200)

    def test_el_spec_declara_las_ocho_operaciones_de_la_bandeja_y_las_protege(self):
        spec = self.c.get("/openapi.json").json()
        nuevas = {"ver_bandeja", "listar_propuestas", "ver_propuesta", "dejar_propuesta", "resolver_propuesta", "listar_alertas", "ver_alerta", "resolver_alerta"}
        ops = {op["operationId"]: op for ruta in spec["paths"].values() for op in ruta.values()}
        self.assertEqual(len(nuevas), 8)
        self.assertTrue(nuevas <= set(ops))
        for nombre in nuevas:
            self.assertTrue(ops[nombre].get("security"), f"{nombre} no está protegida")
            self.assertTrue(ops[nombre].get("summary"), nombre)
        self.assertEqual([p["name"] for p in ops["listar_propuestas"]["parameters"]], ["estado", "tipo"])
