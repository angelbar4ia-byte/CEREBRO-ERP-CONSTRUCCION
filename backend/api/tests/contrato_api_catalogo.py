"""
La API del catálogo y los presupuestos (D-482): el contrato que cumple con los adaptadores en memoria y con los de Postgres, con los archivos
de OPUS de verdad (`1-mundo/opus/`) y los siete programas de verdad. Mezclar con `unittest.TestCase` y definir `nuevos_repositorios()`, que
devuelve `(RepositorioPrograma, RepositorioCatalogo, RepositorioAccesos)` vacíos y, si son de una base, de la misma.

Lo que se prueba es lo que una pantalla necesita saber: que cada acción tiene su propuesta (que no escribe) y su aplicación (que escribe con
quien la hizo y el rol con que la hizo), que solo la hace quien tiene la función, y que cada impedimento llega con el código y el código de
estado que le toca.
"""
from dataclasses import replace
from decimal import Decimal

from fastapi.testclient import TestClient

from api.app import crear_app
from api.autenticacion import VerificadorJWT, emitir_token, por_token
from api.tests.ayudas import NO_HABILES, csv_de
from core.catalogo import ServicioCarga, UNIDAD_CAMBIO
from core.programa import cargar_programa
from core.servicio_programa import ServicioPrograma
from core.tests.contrato_programa import CAL, programa
from core.tests.datos_opus import (
    CONCEPTOS,
    PRESUPUESTO,
    cambiar_unidad_del_concepto,
    con_cantidad,
    con_descripcion_del_concepto,
    reescalar_costo,
    reescalar_linea,
    sin_renglon,
    texto,
)

CO = {"X-Rol": "control_de_obra", "X-Usuario": "luis@obra.mx"}
COSTOS = {"X-Rol": "costos", "X-Usuario": "ana@obra.mx"}
RES = {"X-Rol": "residente", "X-Usuario": "rosa@obra.mx"}
SECRETO = "un-secreto-compartido-de-prueba-largo-de-32-bytes!"
LOGIN = "https://proveedor.example/entrar"

ZAFIRO = 1  # el id de CAS-00004 en el catálogo recién cargado: el primero del archivo
BLOQUE = "CAS-00004#1/NIV-00001#1"  # la cimentación de Zafiro: 56 renglones
K1 = "CAS-00004#1/NIV-00001#1/ECO-00001#1/EST-01040#1::EST-10010#1"  # el renglón EST-10010 de Zafiro
LOS_NUEVE = ["EST-21011", "EST-21031", "EST-22010", "EST-22210", "EST-30012", "EST-30013", "EST-30040", "EST-30041", "EST-52010"]


def carga(conceptos=None, presupuesto=None, **extra):
    return {"conceptos": conceptos or texto(CONCEPTOS), "presupuesto": presupuesto or texto(PRESUPUESTO), **extra}


class ContratoApiCatalogo:
    def nuevos_repositorios(self):  # pragma: no cover
        raise NotImplementedError

    def setUp(self):
        self.pro, self.cat, self.acc = self.nuevos_repositorios()
        for nombre, correo, roles in (("Luis Pérez", "luis@obra.mx", ["control_de_obra"]), ("Ana Soto", "ana@obra.mx", ["costos"]),
                                      ("Rosa Díaz", "rosa@obra.mx", ["residente"]), ("Sin Rol", "sinrol@obra.mx", [])):
            self.acc.agregar_usuario(nombre, correo, roles)
        self.servicio = ServicioPrograma(self.pro, permisos=self.acc.permisos)
        self.c = TestClient(crear_app(self.servicio, catalogo=self.cat))

    # ------------------------------------------------------------------ ayudas
    def cargado(self):
        """El catálogo con los siete presupuestos de verdad ya cargados."""
        ServicioCarga(self.cat).aplicar(texto(CONCEPTOS), texto(PRESUPUESTO), None, rol="costos", usuario="ana@obra.mx")
        return self

    def subir(self, nombre="Zafiro"):
        return self.servicio.importar(f"{nombre} de obra", programa(nombre), CAL, "control_de_obra", "luis@obra.mx")

    def codigo(self, r):
        return r.json()["detail"]["codigo"]

    # ------------------------------------------------------------------ cargar los archivos de OPUS
    def test_proponer_la_carga_dice_lo_que_el_informe_y_no_escribe(self):
        r = self.c.post("/cargas/propuestas", json=carga(), headers=COSTOS)
        self.assertEqual(r.status_code, 200, r.text)
        j, d = r.json(), r.json()["diagnostico"]
        self.assertTrue(d["aplicable"])
        m = d["matrices"]
        self.assertEqual((m["entran"], len(m["nuevas"]), m["versionan"], m["detenidas"], m["ausentes"]), (0, 596, [], [], []))
        self.assertEqual((d["insumos_nuevos"], len(d["sin_unidad"]), d["sin_matriz"]), (612, 40, ["ACC-00003", "IGAS-02131", "IGAS-02132", "ISN-02061"]))
        self.assertEqual([(p["clave"], p["estado"]) for p in d["presupuestos"]][:2], [("CAS-00004", "nuevo"), ("CAS-00003", "nuevo")])
        self.assertEqual((len(d["presupuestos"]), d["pendientes"], d["problemas"], d["cambios"]), (7, [], [], []))
        self.assertIn("596 son nuevas", j["informe"])
        self.assertIn("CAS-00004  ZAFIRO 1.0 (172 M2) — se cargará", j["informe"])
        self.assertEqual((j["base"], j["citan_las_bajas"]), (0, []))
        self.assertEqual((self.cat.cargas(), self.cat.presupuestos()), ([], []))  # proponer no escribe

    def test_aplicar_la_carga_deja_quien_la_hizo_y_su_rol_y_repetirla_no_hace_nada(self):
        r = self.c.post("/cargas", json=carga(), headers=COSTOS)
        self.assertEqual((r.status_code, r.json()["carga_id"]), (201, 1), r.text)
        self.assertEqual(r.json()["resumen"]["insumos_nuevos"], 612)
        (c,) = self.c.get("/cargas").json()
        self.assertEqual((c["usuario"], c["rol"], c["tipo"], sorted(c["archivos"])), ("ana@obra.mx", "costos", "archivos", ["ANALISIS_DE_BASICOS_CONCEPTOS", "CATALOGO_DE_PRESUPUESTO"]))
        self.assertEqual(len(c["archivos"]["CATALOGO_DE_PRESUPUESTO"]), 64)  # su huella sha256
        lista = self.c.get("/presupuestos").json()
        self.assertEqual([p["clave"] for p in lista], ["CAS-00004", "CAS-00003", "CAS-00006", "CAS-00002", "CAS-00005", "CAS-00007", "CAS-00001"])
        self.assertEqual((lista[0]["id"], lista[0]["nombre"], lista[0]["tipo"], lista[0]["renglones"]), (ZAFIRO, "ZAFIRO 1.0 (172 M2)", "plantilla", 398))
        otra = self.c.post("/cargas", json=carga(), headers=COSTOS)
        self.assertEqual((otra.status_code, otra.json()["carga_id"]), (201, None))  # nada que aplicar
        self.assertEqual(len(self.c.get("/cargas").json()), 1)

    def test_el_tipo_de_presupuesto_se_elige_al_cargar(self):
        self.c.post("/cargas", json=carga(tipo="obra"), headers=COSTOS)
        self.assertEqual({p["tipo"] for p in self.c.get("/presupuestos").json()}, {"obra"})

    def test_lo_que_pide_confirmacion_se_dice_y_la_confirmacion_lo_aplica(self):
        self.cargado()
        nuevo = reescalar_linea(texto(CONCEPTOS), "ACA-01010", 1, Decimal("2"))
        p = self.c.post("/cargas/propuestas", json=carga(nuevo), headers=COSTOS).json()
        (pend,) = p["diagnostico"]["pendientes"]
        self.assertEqual((pend["clave"], pend["motivo"], pend["texto"]), ("ACA-01010", "pu_movio_mas_de_5", "el PU se movió más de 5 %: pide confirmación"))
        self.assertIn("ACA-01010", p["informe"])
        self.assertEqual(self.c.post("/cargas", json=carga(nuevo), headers=COSTOS).status_code, 201)
        self.assertEqual(len(self.c.get("/catalogo/ACA-01010/versiones").json()), 1)  # sin confirmar, no versiona
        self.assertEqual(self.c.post("/cargas", json=carga(nuevo, confirmados=["ACA-01010"]), headers=COSTOS).status_code, 201)
        v1, v2 = self.c.get("/catalogo/ACA-01010/versiones").json()
        self.assertEqual((v1["version"], v2["version"]), (1, 2))
        self.assertNotEqual((v1["huella"], v1["pu"]), (v2["huella"], v2["pu"]))
        self.assertEqual(len(v1["lineas"]), len(v2["lineas"]))
        self.assertEqual([l["orden"] for l in v2["lineas"]], list(range(1, len(v2["lineas"]) + 1)))

    def test_solo_carga_quien_tiene_la_funcion(self):
        for h in (RES, CO | {"X-Rol": "supervisor"}):
            for ruta in ("/cargas/propuestas", "/cargas"):
                r = self.c.post(ruta, json=carga(), headers=h)
                self.assertEqual((r.status_code, self.codigo(r)), (403, "permiso_denegado"), (ruta, h))
        self.assertEqual(self.c.post("/cargas", json=carga(), headers={}).status_code, 401)  # y sin decir quién eres, tampoco
        self.assertEqual(self.cat.cargas(), [])
        for h in (CO, COSTOS):  # Control de obra y Costos sí
            self.assertEqual(self.c.post("/cargas/propuestas", json=carga(), headers=h).status_code, 200)

    def test_un_archivo_que_no_cuadra_o_un_tipo_malo_se_dicen_con_su_codigo(self):
        r = self.c.post("/cargas", json={"conceptos": "esto,no,es,un,archivo\n1,2,3,4,5\n"}, headers=COSTOS)
        self.assertEqual((r.status_code, self.codigo(r)), (422, "carga_no_procede"))
        self.assertIn("faltan columnas obligatorias", r.json()["detail"]["mensaje"])
        r = self.c.post("/cargas/propuestas", json={"conceptos": "esto,no,es,un,archivo\n1,2,3,4,5\n"}, headers=COSTOS)
        self.assertEqual((r.status_code, self.codigo(r)), (422, "carga_no_procede"))
        r = self.c.post("/cargas", json=carga(tipo="borrador"), headers=COSTOS)
        self.assertEqual((r.status_code, self.codigo(r)), (422, "peticion_invalida"))
        self.assertEqual(self.c.post("/cargas", json={"presupuesto": "x"}, headers=COSTOS).status_code, 422)  # falta `conceptos`
        self.assertEqual(self.cat.cargas(), [])

    def test_un_presupuesto_que_llega_distinto_se_reconcilia_y_la_baja_pide_su_id(self):
        self.cargado()
        nuevo = con_cantidad(texto(PRESUPUESTO), "CAS-00004", "EST-10010", "40")
        d = self.c.post("/cargas/propuestas", json=carga(presupuesto=nuevo), headers=COSTOS).json()["diagnostico"]
        (cambio,) = d["cambios"]
        self.assertEqual((cambio["tipo"], cambio["id"], cambio["clave"], cambio["estado"]), ("cantidad", K1, "EST-10010", "aplica"))
        self.assertEqual((Decimal(cambio["antes"]), Decimal(cambio["ahora"])), (37, 40))
        self.assertEqual(next(e["estado"] for e in d["presupuestos"] if e["clave"] == "CAS-00004"), "reconciliado")
        self.assertEqual(self.c.post("/cargas", json=carga(presupuesto=nuevo), headers=COSTOS).json()["carga_id"], 2)
        # una baja se detiene hasta que alguien dice cuál: con su id, o todas
        sin = sin_renglon(texto(PRESUPUESTO), "CAS-00004", "EST-10010")
        (baja,) = self.c.post("/cargas/propuestas", json=carga(presupuesto=sin), headers=COSTOS).json()["diagnostico"]["cambios"]
        self.assertEqual((baja["tipo"], baja["id"], baja["estado"], baja["motivo"], baja["renglones"]), ("baja", K1, "detenido", "baja_sin_confirmar", 1))
        self.c.post("/cargas", json=carga(presupuesto=sin), headers=COSTOS)
        self.assertEqual(len(self.c.get(f"/presupuestos/{ZAFIRO}").json()["renglones"]), 398)  # sigue ahí
        self.c.post("/cargas", json=carga(presupuesto=sin, bajas_confirmadas=[K1]), headers=COSTOS)
        self.assertEqual(len(self.c.get(f"/presupuestos/{ZAFIRO}").json()["renglones"]), 397)

    def test_todas_las_bajas_se_confirman_de_una_vez(self):
        self.cargado()
        otro = sin_renglon(texto(PRESUPUESTO), "CAS-00004", "EST-10011")
        (baja,) = self.c.post("/cargas/propuestas", json=carga(presupuesto=otro), headers=COSTOS).json()["diagnostico"]["cambios"]
        self.assertEqual((baja["tipo"], baja["clave"], baja["estado"]), ("baja", "EST-10011", "detenido"))
        (baja,) = self.c.post("/cargas/propuestas", json=carga(presupuesto=otro, todas_las_bajas=True), headers=COSTOS).json()["diagnostico"]["cambios"]
        self.assertEqual(baja["estado"], "aplica")
        self.assertEqual(self.c.post("/cargas", json=carga(presupuesto=otro, todas_las_bajas=True), headers=COSTOS).status_code, 201)
        self.assertEqual(len(self.c.get(f"/presupuestos/{ZAFIRO}").json()["renglones"]), 397)

    def test_la_propuesta_dice_que_programas_citan_lo_que_se_da_de_baja(self):
        self.cargado()
        pid = self.subir()
        self.assertEqual(self.c.post(f"/programas/{pid}/colgado", json={}, headers=CO).status_code, 201)
        sin = sin_renglon(texto(PRESUPUESTO), "CAS-00004", "EST-10010")
        p = self.c.post("/cargas/propuestas", json=carga(presupuesto=sin), headers=COSTOS).json()
        self.assertEqual(p["citan_las_bajas"], [{"baja": K1, "programa_id": pid, "programa": "Zafiro de obra", "filas": 1}])
        # una cantidad no le quita el piso a nadie
        q = self.c.post("/cargas/propuestas", json=carga(presupuesto=con_cantidad(texto(PRESUPUESTO), "CAS-00004", "EST-10010", "40")), headers=COSTOS)
        self.assertEqual(q.json()["citan_las_bajas"], [])

    def test_un_programa_con_version_nueva_ya_no_cita_nada(self):
        self.cargado()
        pid = self.subir()
        self.c.post(f"/programas/{pid}/colgado", json={}, headers=CO)
        sin = sin_renglon(texto(PRESUPUESTO), "CAS-00004", "EST-10010")
        self.assertEqual([x["programa_id"] for x in self.c.post("/cargas/propuestas", json=carga(presupuesto=sin), headers=COSTOS).json()["citan_las_bajas"]], [pid])
        nueva = self.c.post(f"/programas/{pid}/versiones", json={"csv": csv_de("Zafiro"), "no_habiles": NO_HABILES}, headers=CO)
        self.assertEqual(nueva.status_code, 201, nueva.text)
        nueva_id = nueva.json()["resumen"]["id"]
        citan = [x["programa_id"] for x in self.c.post("/cargas/propuestas", json=carga(presupuesto=sin), headers=COSTOS).json()["citan_las_bajas"]]
        self.assertNotIn(pid, citan)  # el viejo está cerrado
        self.c.post(f"/programas/{nueva_id}/colgado", json={}, headers=CO)
        citan = [x["programa_id"] for x in self.c.post("/cargas/propuestas", json=carga(presupuesto=sin), headers=COSTOS).json()["citan_las_bajas"]]
        self.assertEqual(citan, [nueva_id])  # y el que sigue es el nuevo, una vez colgado

    def test_un_cambio_de_unidad_detiene_ese_concepto_y_el_resto_entra_normal(self):
        self.cargado()
        antes = self.cat.estado_vigente().unidad["EST-01040"]
        d = self.c.post("/cargas/propuestas", json=carga(presupuesto=cambiar_unidad_del_concepto(texto(PRESUPUESTO), "EST-01040", "ml")), headers=COSTOS).json()["diagnostico"]
        (det,) = d["matrices"]["detenidas"]
        self.assertEqual((det["clave"], det["unidad_vigente"], det["unidad_nueva"]), ("EST-01040", antes, "ml"))
        self.assertEqual([(p["clave"], p["motivo"], p["texto"]) for p in d["pendientes"]], [("EST-01040", UNIDAD_CAMBIO, "cambió la unidad")])
        self.assertEqual(d["matrices"]["entran"], 595)
        self.assertEqual(self.c.post("/cargas", json=carga(presupuesto=cambiar_unidad_del_concepto(texto(PRESUPUESTO), "EST-01040", "ml")), headers=COSTOS).status_code, 201)
        self.assertEqual(self.cat.estado_vigente().unidad["EST-01040"], antes)  # nada la cambió

    def test_una_descripcion_que_cambia_se_alerta_y_con_la_receta_se_detiene(self):
        self.cargado()
        presupuesto = con_descripcion_del_concepto(texto(PRESUPUESTO), "EST-10010", lambda d: d.replace("4.00", "5.00"))
        (a,) = self.c.post("/cargas/propuestas", json=carga(presupuesto=presupuesto), headers=COSTOS).json()["diagnostico"]["alertas_de_texto"]
        self.assertEqual((a["clave"], a["nivel"], a["motivo"], a["detalle"], a["estado"]), ("EST-10010", "alta", "numero", "4 → 5", "carga"))
        conceptos = reescalar_linea(texto(CONCEPTOS), "EST-10010", 0, Decimal("1.01"))
        (b,) = [x for x in self.c.post("/cargas/propuestas", json=carga(conceptos, presupuesto), headers=COSTOS).json()["diagnostico"]["alertas_de_texto"]]
        self.assertEqual(b["estado"], "detenido")
        self.assertTrue(b["clave_propuesta"].startswith("EST-"))
        self.assertNotEqual(b["clave_propuesta"], "EST-10010")

    # ------------------------------------------------------------------ lo guardado
    def test_se_lee_un_presupuesto_renglon_por_renglon_y_lo_que_no_existe_es_404(self):
        self.cargado()
        j = self.c.get(f"/presupuestos/{ZAFIRO}").json()
        self.assertEqual((j["resumen"]["clave"], len(j["renglones"]), j["total"]), ("CAS-00004", 398, "1842426.01"))
        raiz, cimentacion = j["renglones"][:2]
        self.assertEqual((raiz["wbs"], raiz["tipo"], raiz["padre"], raiz["total"]), ("1", "Capítulo", None, "1842426.01"))
        self.assertEqual((cimentacion["wbs"], cimentacion["clave"], cimentacion["descripcion"], cimentacion["total"]), ("1.1", "NIV-00001", "CIMENTACIÓN", "178768.69"))
        # lo que la API dice es lo que el servicio calcula
        g = ServicioCarga(self.cat).presupuesto(ZAFIRO)
        self.assertEqual([(r["clave"], Decimal(r["total"])) for r in j["renglones"]], [(r.clave, r.total) for r in g.renglones])
        concepto = next(r for r in j["renglones"] if r["clave"] == "EST-10010")
        self.assertEqual((concepto["tipo"], concepto["version"], Decimal(concepto["cantidad"])), ("Concepto", 1, 37))
        r = self.c.get("/presupuestos/987")
        self.assertEqual((r.status_code, self.codigo(r)), (404, "presupuesto_inexistente"))
        self.assertEqual(self.c.get("/presupuestos/987/contratados").status_code, 404)

    def test_se_lee_un_nodo_con_quien_lo_cita_su_matriz_y_su_historia_de_precio(self):
        self.cargado()
        n = self.c.get("/catalogo/AUX-00001").json()
        self.assertEqual((n["rol"], n["categoria"], n["unidad"], n["con_matriz"], n["sustituido_por"]), ("insumo", "material", "M", True, None))
        self.assertEqual([p["clave"] for p in n["citado_por"]], LOS_NUEVE)
        self.assertEqual((n["citado_por"][0]["version"], n["citado_por"][0]["renglones"], n["renglones_directos"]), (1, 1, 0))
        (precio,) = self.c.get("/catalogo/ACE-00001/precios").json()
        self.assertEqual((precio["precio"], precio["vigente_hasta"], precio["carga_id"]), ("24.68", None, 1))
        (v,) = self.c.get("/catalogo/EST-21011/versiones").json()
        self.assertEqual((v["version"], v["pu"], v["lineas"][0]["hijo"], v["lineas"][0]["reporta_a"]), (1, "130198.35", "AUX-10106", "material"))
        for ruta in ("/catalogo/NOEXISTE", "/catalogo/NOEXISTE/versiones", "/catalogo/NOEXISTE/precios"):
            r = self.c.get(ruta)
            self.assertEqual((r.status_code, self.codigo(r)), (404, "nodo_inexistente"), ruta)
        self.assertEqual(self.c.get("/clones").json(), [])

    # ------------------------------------------------------------------ colgar el programa
    def test_proponer_el_colgado_dice_que_casa_de_los_dos_lados_y_no_escribe(self):
        self.cargado()
        pid = self.subir()
        r = self.c.post(f"/programas/{pid}/colgado/propuestas", json={}, headers=CO)
        self.assertEqual(r.status_code, 200, r.text)
        a = r.json()
        self.assertEqual((a["presupuesto_id"], a["presupuesto_clave"], a["casa_bien"]), (ZAFIRO, "CAS-00004", True))
        self.assertEqual((a["bloques"], a["partidas"], a["conceptos_del_programa"], a["vacias"]), (83, 315, 316, 16))
        self.assertEqual((a["enlaces"], a["nuevos"], a["ya_estaban"], a["se_moverian"], a["huerfanos"]), (398, 0, 0, [], []))
        (sin,) = a["sin_par"]
        self.assertEqual((sin["clave"], sin["motivo"], sin["tipo"]), ("ACA-02034", "concepto_sin_par", "Concepto"))
        self.assertEqual((a["sin_par_total"], a["sin_programar"], a["sin_programar_total"]), (1, [], 0))
        self.assertIn("casan 83 de 83 bloques y 315 de 316 conceptos", a["informe"])
        g = self.pro.leer_programa(pid)
        self.assertEqual((g.presupuesto_id, g.enlaces, g.colgaduras), (None, [], []))

    def test_colgar_deja_quien_lo_hizo_y_repetirlo_no_pone_nada_nuevo(self):
        self.cargado()
        pid = self.subir()
        r = self.c.post(f"/programas/{pid}/colgado", json={}, headers=CO)
        self.assertEqual((r.status_code, r.json()["nuevos"], r.json()["enlaces"]), (201, 398, 398), r.text)
        (c,) = self.pro.leer_programa(pid).colgaduras
        self.assertEqual((c.usuario, c.rol, c.nuevos), ("luis@obra.mx", "control_de_obra", 398))
        v = self.c.get(f"/programas/{pid}").json()
        self.assertEqual((v["presupuesto_id"], v["enlazadas"]), (ZAFIRO, 398))
        otra = self.c.post(f"/programas/{pid}/colgado", json={"presupuesto_id": ZAFIRO}, headers=CO)
        self.assertEqual((otra.status_code, otra.json()["nuevos"], otra.json()["ya_estaban"]), (201, 0, 398))
        self.assertEqual(len(self.pro.leer_programa(pid).colgaduras), 1)

    def test_lo_que_casa_menos_de_la_mitad_se_confirma_y_la_lista_viene_con_tope(self):
        self.cargado()
        plus = programa("Zafiro Plus")
        n = {"i": 0}

        def otra_clave(f):  # conserva la tercera parte de los conceptos de verdad; a los demás les cambia la clave
            if f.tipo != "Concepto" or not f.clave:
                return f
            n["i"] += 1
            return f if n["i"] % 3 == 0 else replace(f, clave=f.clave + "-X")

        pid = self.servicio.importar("Plus a medias", cargar_programa([otra_clave(f) for f in plus.filas], CAL), CAL, "control_de_obra", "luis@obra.mx")
        r = self.c.post(f"/programas/{pid}/colgado", json={}, headers=CO)
        self.assertEqual((r.status_code, self.codigo(r)), (422, "colgado_no_cuadra"))
        d = r.json()["detail"]
        self.assertTrue(d["forzable"])
        self.assertEqual((d["alineacion"]["partidas"], d["alineacion"]["conceptos_del_programa"], d["alineacion"]["casa_bien"]), (129, 388, False))
        self.assertEqual((d["alineacion"]["sin_par_total"], len(d["alineacion"]["sin_par"])), (259, 200))  # el total entero; la lista, con tope
        self.assertEqual(self.pro.leer_programa(pid).enlaces, [])
        propuesta = self.c.post(f"/programas/{pid}/colgado/propuestas", json={}, headers=CO)
        self.assertEqual((propuesta.status_code, propuesta.json()["casa_bien"]), (200, False))  # proponer no se detiene: lo dice
        forzado = self.c.post(f"/programas/{pid}/colgado", json={"forzar": True}, headers=CO)
        self.assertEqual((forzado.status_code, forzado.json()["partidas"]), (201, 129))
        self.assertTrue(self.pro.leer_programa(pid).colgaduras[0].resumen["forzado"])

    def test_colgar_lo_que_no_se_puede_se_dice_con_su_codigo(self):
        self.cargado()
        pid, rubi = self.subir(), self.subir("Rubí")
        r = self.c.post("/programas/987/colgado", json={}, headers=CO)
        self.assertEqual((r.status_code, self.codigo(r)), (404, "programa_inexistente"))
        r = self.c.post(f"/programas/{rubi}/colgado", json={"presupuesto_id": ZAFIRO, "forzar": True}, headers=CO)  # Rubí no casa con Zafiro
        self.assertEqual((r.status_code, self.codigo(r)), (422, "colgado_no_cuadra"))
        self.assertFalse(r.json()["detail"]["forzable"])  # ninguna fila casa: no hay qué confirmar
        self.assertIn("ninguna fila", r.json()["detail"]["mensaje"])
        r = self.c.post(f"/programas/{pid}/colgado", json={"presupuesto_id": 987}, headers=CO)
        self.assertEqual((r.status_code, self.codigo(r)), (422, "colgado_no_cuadra"))
        self.assertIsNone(r.json()["detail"]["alineacion"])
        self.c.post(f"/programas/{pid}/colgado", json={}, headers=CO)
        r = self.c.post(f"/programas/{pid}/colgado", json={"presupuesto_id": 2}, headers=CO)  # y un programa colgado no cambia de presupuesto
        self.assertEqual((r.status_code, self.codigo(r)), (409, "ya_colgado"))
        self.assertEqual(r.json()["detail"]["presupuesto_id"], ZAFIRO)
        nueva = self.c.post(f"/programas/{pid}/versiones", json={"csv": csv_de("Zafiro"), "no_habiles": NO_HABILES}, headers=CO)
        self.assertEqual(nueva.status_code, 201, nueva.text)
        for ruta in ("propuestas", ""):
            r = self.c.post(f"/programas/{pid}/colgado" + ("/" + ruta if ruta else ""), json={}, headers=CO)
            self.assertEqual((r.status_code, self.codigo(r)), (409, "reemplazado"), ruta)
            self.assertEqual(r.json()["detail"]["reemplazado_por"], nueva.json()["resumen"]["id"])

    def test_solo_cuelga_quien_puede_editar_la_estructura(self):
        self.cargado()
        pid = self.subir()
        for h in (COSTOS, RES):
            for ruta in ("/colgado/propuestas", "/colgado"):
                r = self.c.post(f"/programas/{pid}{ruta}", json={}, headers=h)
                self.assertEqual((r.status_code, self.codigo(r)), (403, "permiso_denegado"), (ruta, h))
        self.assertEqual(self.pro.leer_programa(pid).enlaces, [])

    # ------------------------------------------------------------------ contratar un subárbol
    def mover_el_acero(self, factor):
        ServicioCarga(self.cat).aplicar(reescalar_costo(texto(CONCEPTOS), "ACE-00001", Decimal(factor)), texto(PRESUPUESTO), None,
                                        rol="costos", usuario="ana@obra.mx")

    def test_proponer_la_contratacion_dice_que_se_fija_y_cuanto_cambia_y_no_escribe(self):
        self.cargado()
        self.mover_el_acero("1.02")
        r = self.c.post(f"/presupuestos/{ZAFIRO}/contrataciones/propuestas", json={"bloque": BLOQUE}, headers=CO)
        self.assertEqual(r.status_code, 200, r.text)
        p = r.json()
        self.assertEqual((p["presupuesto_clave"], p["ruta"], p["descripcion"], p["aplicable"]), ("CAS-00004", BLOQUE, "CIMENTACIÓN", True))
        self.assertEqual((p["renglones"], p["ya_contratados"], len(p["conceptos"]), p["pendientes"]), (56, 0, 56, []))
        self.assertEqual((p["total_antes"], p["total_despues"], p["diferencia"]), ("178768.69", "178809.66", "40.97"))
        self.assertEqual(sum(1 for c in p["conceptos"] if c["accion"] == "version_nueva"), 25)
        nueva = next(c for c in p["conceptos"] if c["accion"] == "version_nueva")
        self.assertTrue(nueva["cambia"])
        self.assertEqual(nueva["version_vigente"], nueva["version_fijada"])  # la misma versión, con el PU de hoy en la que nace
        self.assertGreater(Decimal(nueva["pu_hoy"]), Decimal(nueva["pu_fijado"]))
        self.assertIn("178,768.69 y quedará en 178,809.66 (+40.97)", p["informe"])
        self.assertEqual(self.c.get(f"/presupuestos/{ZAFIRO}/contratados").json(), [])

    def test_contratar_fija_el_bloque_con_quien_lo_hizo_y_no_se_repite(self):
        self.cargado()
        self.mover_el_acero("1.02")
        r = self.c.post(f"/presupuestos/{ZAFIRO}/contrataciones", json={"bloque": BLOQUE}, headers=CO)
        self.assertEqual(r.status_code, 201, r.text)
        j = r.json()
        self.assertEqual((j["versiones_nuevas"], j["renglones_fijados"], j["propuesta"]["total_despues"]), (25, 25, "178809.66"))
        (c,) = self.c.get(f"/presupuestos/{ZAFIRO}/contratados").json()
        self.assertEqual((c["usuario"], c["rol"], c["ruta"], c["estado"], c["id"], c["carga_id"]), ("luis@obra.mx", "control_de_obra", BLOQUE, "contratado", j["congelamiento_id"], j["carga_id"]))
        self.assertEqual(self.c.get(f"/presupuestos/{ZAFIRO}").json()["renglones"][1]["total"], "178809.66")  # el monto del bloque ya es el fijado
        self.assertEqual([x["tipo"] for x in self.c.get("/cargas").json()][-1], "contratacion")
        otra = self.c.post(f"/presupuestos/{ZAFIRO}/contrataciones", json={"bloque": BLOQUE}, headers=CO)
        self.assertEqual((otra.status_code, self.codigo(otra)), (409, "ya_contratado"))  # lo contratado no se vuelve a contratar
        self.assertEqual(len(self.c.get(f"/presupuestos/{ZAFIRO}/contratados").json()), 1)

    def test_lo_que_pide_confirmacion_no_se_contrata_a_medias(self):
        self.cargado()
        self.mover_el_acero("4")
        p = self.c.post(f"/presupuestos/{ZAFIRO}/contrataciones/propuestas", json={"bloque": BLOQUE}, headers=CO).json()
        self.assertFalse(p["aplicable"])
        claves = [x["clave"] for x in p["pendientes"]]
        self.assertEqual(claves[0], "EST-10010")
        self.assertEqual(p["pendientes"][0]["motivo"], "pu_movio_mas_de_5")
        r = self.c.post(f"/presupuestos/{ZAFIRO}/contrataciones", json={"bloque": BLOQUE}, headers=CO)
        self.assertEqual((r.status_code, self.codigo(r)), (422, "confirmacion_pendiente"))
        self.assertEqual([x["clave"] for x in r.json()["detail"]["pendientes"]], claves)
        self.assertEqual(self.c.get(f"/presupuestos/{ZAFIRO}/contratados").json(), [])
        ok = self.c.post(f"/presupuestos/{ZAFIRO}/contrataciones", json={"bloque": BLOQUE, "confirmados": claves}, headers=CO)
        self.assertEqual(ok.status_code, 201, ok.text)

    def test_contratar_lo_que_no_existe_o_quien_no_puede_se_dice(self):
        self.cargado()
        r = self.c.post("/presupuestos/987/contrataciones/propuestas", json={}, headers=CO)
        self.assertEqual((r.status_code, self.codigo(r)), (404, "presupuesto_inexistente"))
        r = self.c.post(f"/presupuestos/{ZAFIRO}/contrataciones/propuestas", json={"bloque": "CAS-00004#1/NIV-99999#1"}, headers=CO)
        self.assertEqual((r.status_code, self.codigo(r)), (422, "contratacion_invalida"))
        self.assertIn("no tiene el bloque", r.json()["detail"]["mensaje"])
        entero = self.c.post(f"/presupuestos/{ZAFIRO}/contrataciones/propuestas", json={}, headers=CO).json()  # sin bloque, el presupuesto entero
        self.assertEqual((entero["ruta"], entero["renglones"]), ("CAS-00004#1", 315))
        for h in (COSTOS, RES):
            for ruta in ("/contrataciones/propuestas", "/contrataciones"):
                r = self.c.post(f"/presupuestos/{ZAFIRO}{ruta}", json={}, headers=h)
                self.assertEqual((r.status_code, self.codigo(r)), (403, "permiso_denegado"), (ruta, h))
        self.assertEqual(self.c.get(f"/presupuestos/{ZAFIRO}/contratados").json(), [])

    # ------------------------------------------------------------------ clonar un insumo
    def test_proponer_la_clonacion_dice_a_quien_cita_y_no_escribe(self):
        self.cargado()
        r = self.c.post("/clonaciones/propuestas", json={"original": "AUX-00001", "clave": "PRE-00120"}, headers=CO)
        self.assertEqual(r.status_code, 200, r.text)
        p = r.json()
        self.assertEqual((p["modo"], p["tipo"], p["aplicable"], p["problemas"], p["unidad"]), ("sustituir", "compuesto", True, [], "M"))
        self.assertEqual((len(p["redirigidos"]), p["renglones"]), (9, 9))
        self.assertEqual([x["clave"] for x in p["redirigidos"]], LOS_NUEVE)
        self.assertEqual((p["redirigidos"][0]["version_antes"], p["redirigidos"][0]["version_despues"], p["redirigidos"][0]["pu"]), (1, 2, "130198.35"))
        self.assertIn("Clonar y sustituir — AUX-00001 → PRE-00120", p["informe"])
        self.assertEqual(self.c.get("/clones").json(), [])
        self.assertEqual(len(self.c.get("/catalogo/EST-21011/versiones").json()), 1)

    def test_clonar_sustituye_deja_quien_lo_hizo_y_la_clave_vieja_sigue_entrando(self):
        self.cargado()
        r = self.c.post("/clonaciones", json={"original": "AUX-00001", "clave": "PRE-00120"}, headers=CO)
        self.assertEqual(r.status_code, 201, r.text)
        j = r.json()
        self.assertEqual((j["versiones_nuevas"], j["renglones_fijados"], j["propuesta"]["aplicable"]), (9, 9, True))
        (c,) = self.c.get("/clones").json()
        self.assertEqual((c["original"], c["clon"], c["modo"], c["usuario"], c["rol"]), ("AUX-00001", "PRE-00120", "sustituir", "luis@obra.mx", "control_de_obra"))
        self.assertEqual((c["reconoce_clave_vieja_al_importar"], c["exporta_clave_vieja"], c["carga_id"]), (True, True, j["carga_id"]))
        self.assertGreater(j["nodo_id"], 0)
        self.assertEqual(self.c.get("/catalogo/AUX-00001").json()["sustituido_por"], "PRE-00120")
        nuevo = self.c.get("/catalogo/PRE-00120").json()
        self.assertEqual((nuevo["descripcion"], nuevo["categoria"], nuevo["procedencia"]), ("Trabe T-3 de 15x25 cm 4 var. del #3 est. no. 2 @25 cm.", "material", "clonacion"))
        self.assertEqual([p["clave"] for p in nuevo["citado_por"]], LOS_NUEVE)  # lo que citaba al original cita al clon
        self.assertEqual(self.c.get("/catalogo/AUX-00001").json()["citado_por"], [])
        self.assertEqual(len(self.c.get("/catalogo/EST-21011/versiones").json()), 2)
        self.assertEqual(self.c.get(f"/presupuestos/{ZAFIRO}").json()["total"], "1842426.01")  # no se mueve dinero
        otra = self.c.post("/clonaciones", json={"original": "AUX-00001", "clave": "PRE-00121"}, headers=CO)
        self.assertEqual((otra.status_code, self.codigo(otra)), (422, "clonacion_no_procede"))
        self.assertIn("ya se sustituyó por PRE-00120", otra.json()["detail"]["problemas"][0])
        self.assertEqual(len(self.c.get("/clones").json()), 1)

    def test_clonar_y_mantener_deja_vivos_los_dos(self):
        self.cargado()
        r = self.c.post("/clonaciones", json={"original": "AUX-00001", "clave": "PRE-00120", "modo": "mantener"}, headers=CO)
        self.assertEqual((r.status_code, r.json()["versiones_nuevas"], r.json()["renglones_fijados"]), (201, 0, 0))
        (c,) = self.c.get("/clones").json()
        self.assertEqual((c["modo"], c["reconoce_clave_vieja_al_importar"]), ("mantener", False))
        self.assertEqual(len(self.c.get("/catalogo/AUX-00001").json()["citado_por"]), 9)

    def test_lo_que_impide_clonar_se_dice_sin_tocar_al_original(self):
        self.cargado()
        p = self.c.post("/clonaciones/propuestas", json={"original": "AUX-00001", "clave": "PRE-00001"}, headers=CO)  # esa clave ya existe
        self.assertEqual((p.status_code, p.json()["aplicable"], p.json()["redirigidos"]), (200, False, []))  # proponer lo dice, no lo rechaza
        self.assertIn("ya hay un nodo con la clave PRE-00001", p.json()["problemas"][0])
        self.assertIn("NO SE PUEDE", p.json()["informe"])
        r = self.c.post("/clonaciones", json={"original": "AUX-00001", "clave": "PRE-00001"}, headers=CO)
        self.assertEqual((r.status_code, self.codigo(r)), (422, "clonacion_no_procede"))
        self.assertIn("ya hay un nodo con la clave PRE-00001", r.json()["detail"]["problemas"][0])
        r = self.c.post("/clonaciones", json={"original": "NOEXISTE", "clave": "PRE-00120"}, headers=CO)
        self.assertEqual((r.status_code, self.codigo(r)), (422, "clonacion_no_procede"))
        r = self.c.post("/clonaciones", json={"original": "AUX-00001", "clave": "PRE-00120", "modo": "duplicar"}, headers=CO)
        self.assertEqual((r.status_code, self.codigo(r)), (422, "clonacion_no_procede"))
        self.assertEqual(self.c.post("/clonaciones", json={"clave": "PRE-00120"}, headers=CO).status_code, 422)  # falta el original
        self.assertEqual(self.c.get("/clones").json(), [])

    def test_lo_que_cita_algo_contratado_se_rechaza(self):
        self.cargado()
        self.assertEqual(self.c.post(f"/presupuestos/{ZAFIRO}/contrataciones", json={"bloque": BLOQUE}, headers=CO).status_code, 201)
        r = self.c.post("/clonaciones", json={"original": "AUX-00030", "clave": "PRE-00120"}, headers=CO)
        self.assertEqual((r.status_code, self.codigo(r)), (422, "clonacion_no_procede"))
        self.assertIn("fija un renglón contratado", r.json()["detail"]["problemas"][0])
        self.assertEqual(self.c.get("/clones").json(), [])

    def test_solo_clona_quien_tiene_la_funcion(self):
        self.cargado()
        for h in (COSTOS, RES):
            for ruta, cuerpo in (("/clonaciones/propuestas", {"original": "AUX-00001", "clave": "PRE-00120"}), ("/clonaciones", {"original": "AUX-00001", "clave": "PRE-00120"}),
                                 ("/correcciones-de-prefijo/propuestas", {"viejo": "AUX", "nuevo": "PRE"}), ("/correcciones-de-prefijo", {"viejo": "AUX", "nuevo": "PRE"})):
                r = self.c.post(ruta, json=cuerpo, headers=h)
                self.assertEqual((r.status_code, self.codigo(r)), (403, "permiso_denegado"), (ruta, h))
        self.assertEqual(self.c.get("/clones").json(), [])

    # ------------------------------------------------------------------ corregir un prefijo entero (P-11)
    def test_la_correccion_de_prefijo_propone_las_79_y_las_hace(self):
        self.cargado()
        p = self.c.post("/correcciones-de-prefijo/propuestas", json={"viejo": "AUX", "nuevo": "PRE", "desde": 120}, headers=CO).json()
        self.assertEqual((len(p["pares"]), p["hechos"], p["omitidos"], p["rechazadas"]), (79, [], [], 0))
        primero = p["pares"][0]
        self.assertEqual((primero["original"], primero["clon"], primero["aplicable"], primero["renglones"], primero["versiones_nuevas"]), ("AUX-00001", "PRE-00120", True, 9, 9))
        self.assertEqual(p["pares"][-1]["clon"], "PRE-00198")
        self.assertIn("79 claves por sustituir", p["informe"])
        self.assertEqual(self.c.get("/clones").json(), [])
        r = self.c.post("/correcciones-de-prefijo", json={"viejo": "AUX", "nuevo": "PRE", "desde": 120}, headers=CO)
        self.assertEqual(r.status_code, 201, r.text)
        j = r.json()
        self.assertEqual((len(j["hechos"]), j["rechazados"]), (79, []))
        self.assertEqual((j["hechos"][0]["original"], j["hechos"][0]["clon"], j["hechos"][-1]["clon"]), ("AUX-00001", "PRE-00120", "PRE-00198"))  # desde el 120
        self.assertEqual((j["versiones_nuevas"], j["renglones_fijados"]), (sum(h["versiones_nuevas"] for h in j["hechos"]), sum(h["renglones_fijados"] for h in j["hechos"])))
        self.assertEqual(len(self.c.get("/clones").json()), 79)
        self.assertIn("Sustituidas: 79", j["informe"])
        otra = self.c.post("/correcciones-de-prefijo/propuestas", json={"viejo": "AUX", "nuevo": "PRE", "desde": 120}, headers=CO).json()
        self.assertEqual((otra["pares"], len(otra["hechos"])), ([], 79))  # lo ya sustituido no se repite
        self.assertEqual(self.c.get(f"/presupuestos/{ZAFIRO}").json()["total"], "1842426.01")

    def test_la_correccion_salta_lo_que_cita_algo_contratado_y_lo_dice(self):
        self.cargado()
        self.c.post(f"/presupuestos/{ZAFIRO}/contrataciones", json={"bloque": BLOQUE}, headers=CO)
        p = self.c.post("/correcciones-de-prefijo/propuestas", json={"viejo": "AUX", "nuevo": "PRE", "desde": 120}, headers=CO).json()
        self.assertEqual(p["rechazadas"], 5)
        self.assertEqual(sorted(x["original"] for x in p["pares"] if not x["aplicable"]), ["AUX-00030", "AUX-01010", "AUX-01030", "AUX-02010", "AUX-02030"])
        j = self.c.post("/correcciones-de-prefijo", json={"viejo": "AUX", "nuevo": "PRE", "desde": 120}, headers=CO).json()  # no es un error: lo demás se hace
        self.assertEqual((len(j["hechos"]), sorted(x["original"] for x in j["rechazados"])), (74, ["AUX-00030", "AUX-01010", "AUX-01030", "AUX-02010", "AUX-02030"]))
        self.assertIn("fija un renglón contratado", j["rechazados"][0]["problemas"][0])
        self.assertIn("NO SE HIZO AUX-00030", j["informe"])

    def test_una_correccion_mal_pedida_se_dice(self):
        self.cargado()
        r = self.c.post("/correcciones-de-prefijo", json={"viejo": "AUX", "nuevo": "AUX"}, headers=CO)
        self.assertEqual((r.status_code, self.codigo(r)), (422, "peticion_invalida"))
        self.assertEqual(self.c.post("/correcciones-de-prefijo/propuestas", json={"viejo": "AUX", "nuevo": "PRE", "desde": 0}, headers=CO).status_code, 422)
        self.assertEqual(self.c.post("/correcciones-de-prefijo/propuestas", json={"viejo": "", "nuevo": "PRE"}, headers=CO).status_code, 422)
        sin = self.c.post("/correcciones-de-prefijo/propuestas", json={"viejo": "ZZZ", "nuevo": "PRE"}, headers=CO).json()  # un prefijo que no existe: nada que hacer
        self.assertEqual((sin["pares"], sin["hechos"]), ([], []))
        self.assertEqual(self.c.get("/clones").json(), [])

    # ------------------------------------------------------------------ quién llama
    def test_en_modo_token_el_usuario_y_el_rol_salen_del_token(self):
        auth = por_token(VerificadorJWT(secreto=SECRETO), self.acc, LOGIN)
        c = TestClient(crear_app(self.servicio, auth, self.cat))
        bearer = lambda correo: {"Authorization": "Bearer " + emitir_token(SECRETO, correo)}
        for ruta in ("/presupuestos", "/cargas", "/clones", "/catalogo/AUX-00001"):
            r = c.get(ruta)
            self.assertEqual((r.status_code, self.codigo(r)), (401, "sin_token"), ruta)  # ver también pide saber quién eres
        for ruta in ("/cargas/propuestas", "/cargas"):
            self.assertEqual(c.post(ruta, json=carga()).status_code, 401)
        self.assertEqual(c.post("/cargas", json=carga(), headers=bearer("nadie@obra.mx")).status_code, 403)  # el proveedor lo conoce; aquí no está dado de alta
        r = c.post("/cargas", json=carga(), headers=bearer("sinrol@obra.mx"))
        self.assertEqual((r.status_code, self.codigo(r)), (403, "permiso_denegado"))
        r = c.post("/cargas", json=carga(), headers=bearer("ana@obra.mx"))
        self.assertEqual(r.status_code, 201, r.text)
        (carga_1,) = c.get("/cargas", headers=bearer("rosa@obra.mx")).json()  # ver lo ve cualquiera que esté dado de alta
        self.assertEqual((carga_1["usuario"], carga_1["rol"]), ("ana@obra.mx", "costos"))
        r = c.post("/clonaciones", json={"original": "AUX-00001", "clave": "PRE-00120"}, headers=bearer("luis@obra.mx"))
        self.assertEqual(r.status_code, 201, r.text)
        (clon,) = c.get("/clones", headers=bearer("rosa@obra.mx")).json()
        self.assertEqual((clon["usuario"], clon["rol"]), ("luis@obra.mx", "control_de_obra"))  # el correo del token, no lo que se diga
        yo = c.get("/yo", headers=bearer("luis@obra.mx")).json()
        self.assertEqual([f for f in yo["funciones"] if f in ("cargar_catalogo_opus", "contratar_subarbol", "clonar_insumo", "editar_estructura_programa")],
                         ["cargar_catalogo_opus", "clonar_insumo", "contratar_subarbol", "editar_estructura_programa"])

    def test_lo_que_cambia_la_tabla_de_permisos_vale_desde_la_siguiente_accion(self):
        self.cargado()
        pid = self.subir()
        acciones = {  # la función → cómo se pide una propuesta que ella autoriza
            "cargar_catalogo_opus": lambda: self.c.post("/cargas/propuestas", json=carga(), headers=RES),
            "contratar_subarbol": lambda: self.c.post(f"/presupuestos/{ZAFIRO}/contrataciones/propuestas", json={"bloque": BLOQUE}, headers=RES),
            "clonar_insumo": lambda: self.c.post("/clonaciones/propuestas", json={"original": "AUX-00001", "clave": "PRE-00120"}, headers=RES),
            "editar_estructura_programa": lambda: self.c.post(f"/programas/{pid}/colgado/propuestas", json={}, headers=RES),
        }
        for funcion, pide in acciones.items():
            self.assertEqual(pide().status_code, 403, funcion)
            self.acc.dar_funcion("residente", funcion)
            try:
                self.assertEqual(pide().status_code, 200, funcion)
            finally:
                self.acc.quitar_funcion("residente", funcion)
            self.assertEqual(pide().status_code, 403, funcion)

    def test_lo_que_se_vio_ya_no_es_lo_de_hoy_si_otro_cargo_entre_la_propuesta_y_la_aplicacion(self):
        self.cargado()
        cambia = con_cantidad(texto(PRESUPUESTO), "CAS-00004", "EST-10010", "40")
        bases = (
            self.c.post("/cargas/propuestas", json=carga(presupuesto=cambia), headers=COSTOS).json()["base"],
            self.c.post(f"/presupuestos/{ZAFIRO}/contrataciones/propuestas", json={"bloque": BLOQUE}, headers=CO).json()["base"],
            self.c.post("/clonaciones/propuestas", json={"original": "AUX-00001", "clave": "PRE-00120"}, headers=CO).json()["base"],
        )
        self.assertEqual(bases, (1, 1, 1))  # las tres vieron el catálogo en la carga 1
        self.mover_el_acero("1.02")  # y alguien más carga: ahora va en la 2
        pedidas = (("/cargas", carga(presupuesto=cambia, esperaba=1)), (f"/presupuestos/{ZAFIRO}/contrataciones", {"bloque": BLOQUE, "esperaba": 1}),
                   ("/clonaciones", {"original": "AUX-00001", "clave": "PRE-00120", "esperaba": 1}))
        for ruta, cuerpo in pedidas:
            h = COSTOS if ruta == "/cargas" else CO
            r = self.c.post(ruta, json=cuerpo, headers=h)
            self.assertEqual((r.status_code, self.codigo(r)), (409, "conflicto"), ruta)
            self.assertIn("Vuelve a revisarlo", r.json()["detail"]["mensaje"])
        self.assertEqual(len(self.c.get("/cargas").json()), 2)  # no se escribió nada
        self.assertEqual((self.c.get(f"/presupuestos/{ZAFIRO}/contratados").json(), self.c.get("/clones").json()), ([], []))
        # con lo que ve hoy, sí; y cada cosa que se aplica mueve la base de las demás
        self.assertEqual(self.c.post("/cargas/propuestas", json=carga(presupuesto=cambia), headers=COSTOS).json()["base"], 2)
        self.assertEqual(self.c.post("/cargas", json=carga(presupuesto=cambia, esperaba=2), headers=COSTOS).json()["carga_id"], 3)
        self.assertEqual(self.c.post(f"/presupuestos/{ZAFIRO}/contrataciones", json={"bloque": BLOQUE, "esperaba": 2}, headers=CO).status_code, 409)
        propuesta = self.c.post(f"/presupuestos/{ZAFIRO}/contrataciones/propuestas", json={"bloque": BLOQUE}, headers=CO).json()
        self.assertEqual(propuesta["base"], 3)
        ok = self.c.post(f"/presupuestos/{ZAFIRO}/contrataciones", json={"bloque": BLOQUE, "esperaba": propuesta["base"]}, headers=CO)
        self.assertEqual((ok.status_code, ok.json()["carga_id"]), (201, 4))
        self.assertEqual(self.c.post("/clonaciones", json={"original": "AUX-00001", "clave": "PRE-00120", "esperaba": 3}, headers=CO).status_code, 409)
        clon = self.c.post("/clonaciones/propuestas", json={"original": "AUX-00001", "clave": "PRE-00120"}, headers=CO).json()
        self.assertEqual(clon["base"], 4)
        self.assertEqual(self.c.post("/clonaciones", json={"original": "AUX-00001", "clave": "PRE-00120", "esperaba": clon["base"]}, headers=CO).status_code, 201)
        # una propuesta que no se puede hacer no trae base: no hay nada que aplicar
        self.assertIsNone(self.c.post("/clonaciones/propuestas", json={"original": "AUX-00001", "clave": "PRE-00121"}, headers=CO).json()["base"])

    def test_la_correccion_de_prefijo_tambien_ata_lo_aplicado_a_lo_visto(self):
        self.cargado()
        cuerpo = {"viejo": "AUX", "nuevo": "PRE", "desde": 120}
        self.assertEqual(self.c.post("/correcciones-de-prefijo/propuestas", json=cuerpo, headers=CO).json()["base"], 1)
        self.mover_el_acero("1.02")  # alguien más carga: ahora va en la 2
        r = self.c.post("/correcciones-de-prefijo", json={**cuerpo, "esperaba": 1}, headers=CO)
        self.assertEqual((r.status_code, self.codigo(r)), (409, "conflicto"))
        self.assertEqual(self.c.get("/clones").json(), [])  # no se escribió nada
        ok = self.c.post("/correcciones-de-prefijo", json={**cuerpo, "esperaba": 2}, headers=CO)
        self.assertEqual((ok.status_code, len(ok.json()["hechos"])), (201, 79))

    def test_la_api_sin_catalogo_no_tiene_estas_rutas(self):
        solo = TestClient(crear_app(self.servicio))
        for ruta in ("/presupuestos", "/cargas", "/clones", "/catalogo/AUX-00001"):
            self.assertEqual(solo.get(ruta).status_code, 404, ruta)
        self.assertEqual(solo.get("/programas").status_code, 200)

    def test_el_spec_declara_las_dieciocho_operaciones_nuevas_y_las_protege(self):
        spec = self.c.get("/openapi.json").json()
        nuevas = {"listar_presupuestos", "ver_presupuesto", "ver_contratados", "listar_cargas", "ver_nodo", "ver_versiones_de_matriz", "ver_precios",
                  "listar_clones", "proponer_carga", "aplicar_carga", "proponer_colgado", "colgar_programa", "proponer_contratacion",
                  "contratar_subarbol", "proponer_clonacion", "clonar_insumo", "proponer_correccion_de_prefijo", "corregir_prefijo"}
        ops = {op["operationId"]: op for ruta in spec["paths"].values() for op in ruta.values()}
        self.assertEqual(len(nuevas), 18)
        self.assertEqual(set(ops) - nuevas, {"quien_soy", "listar_programas", "importar_programa", "subir_version", "pantalla_programas", "ver_programa",
                                             "ver_bitacora", "proponer_edicion", "aplicar_edicion", "deshacer_edicion", "pantalla_gantt"})
        for nombre in nuevas:
            self.assertTrue(ops[nombre].get("security"), f"{nombre} no está protegida")
            self.assertTrue(ops[nombre].get("summary"), nombre)
