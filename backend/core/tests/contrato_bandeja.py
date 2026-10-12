"""
La bandeja de propuestas y de alertas (D-485): el contrato que cumplen los adaptadores. Mezclar con `unittest.TestCase` y definir
`nuevos_repositorios()`, que devuelve `(RepositorioBandeja, RepositorioCatalogo)` vacíos y, si son de una base, de la misma.

Lo que se prueba es lo que la bandeja promete: que una propuesta sin evidencia no entra; que lo rechazado se conserva y no se repite
sin evidencia nueva; que quien propone no aprueba lo suyo; que aprobar pide la función de la acción y la hace con la identidad de quien
aprueba —con los archivos de OPUS de verdad y las 79 claves `AUX-` de P-11—; y que una alerta que reaparece se cuenta en vez de repetirse.
"""
from decimal import Decimal

from core.accesos import MemoriaAccesos
from core.catalogo import CatalogoCambio, ServicioCarga
from core.clonacion import ClonacionNoProcede, ServicioClonacion
from core.propuestas import (
    AlertaNoExiste,
    AutoAprobacion,
    PropuestaInvalida,
    PropuestaNoExiste,
    RechazadaAntes,
    ServicioBandeja,
    SinOperacion,
    TipoDePropuesta,
    YaPropuesta,
    YaResuelta,
    tipos_de_propuesta,
)
from core.servicio_programa import PermisoDenegado
from core.tests.datos_opus import CONCEPTOS, PRESUPUESTO, reescalar_costo, texto

ANA = ("ana@obra.mx", ["costos"])  # propone, y no puede clonar ni resolver la bandeja
LUIS = ("luis@obra.mx", ["control_de_obra"])  # resuelve la bandeja y puede clonar
SOFIA = ("sofia@obra.mx", ["supervisor"])  # cierra alertas, y nada más
ROSA = ("rosa@obra.mx", ["residente"])
CLONAR_LA_TRABE = {"original": "AUX-00001", "clave": "PRE-00120"}
EVIDENCIA = "AUX-00001 es una trabe terminada: un material, no un auxiliar. Lo citan nueve conceptos de estructura."


def quien(persona):
    return {"usuario": persona[0], "rol": persona[1]}


class ContratoBandeja:
    def nuevos_repositorios(self):  # pragma: no cover
        raise NotImplementedError

    def setUp(self):
        self.bandeja, self.cat = self.nuevos_repositorios()
        self.acc = MemoriaAccesos()
        self.sv = ServicioBandeja(self.bandeja, self.acc.permisos, tipos_de_propuesta(ServicioClonacion(self.cat, self.acc.permisos)))

    # ------------------------------------------------------------------ ayudas
    def cargado(self):
        ServicioCarga(self.cat).aplicar(texto(CONCEPTOS), texto(PRESUPUESTO), None, rol="costos", usuario="ana@obra.mx")
        return self

    def mover_el_acero(self):
        ServicioCarga(self.cat).aplicar(reescalar_costo(texto(CONCEPTOS), "ACE-00001", Decimal("1.02")), texto(PRESUPUESTO), None,
                                        rol="costos", usuario="ana@obra.mx")

    def proponer(self, persona=ANA, tipo="clonacion", objeto="AUX-00001", valor=None, evidencia=EVIDENCIA, **kw):
        return self.sv.proponer(tipo, objeto, CLONAR_LA_TRABE if valor is None else valor, evidencia, **quien(persona), **kw)

    def ultima_carga(self):
        return self.cat.estado_vigente().ultima_carga

    # ------------------------------------------------------------------ proponer
    def test_una_propuesta_queda_con_su_evidencia_quien_la_dejo_y_cuando(self):
        p = self.proponer(base=1)
        self.assertEqual((p.id, p.tipo, p.objeto, p.estado, p.origen), (1, "clonacion", "AUX-00001", "pendiente", "usuario"))
        self.assertEqual(dict(p.valor_propuesto), {"original": "AUX-00001", "clave": "PRE-00120", "modo": "sustituir"})  # el modo por omisión, dicho
        self.assertEqual((p.evidencia, p.propuesto_por, p.propuesto_con_rol, p.base), (EVIDENCIA, "ana@obra.mx", "costos", 1))
        self.assertIsNotNone(p.creada_en)
        self.assertEqual((p.resuelto_por, p.resuelta_en, p.nota, p.resultado), (None, None, None, None))
        self.assertEqual(self.sv.propuesta(p.id), p)
        otra = self.proponer(tipo="equivalencia", objeto="ISN-02005", valor={"equivale_a": "ISN-02001"}, evidencia="Descripciones idénticas")
        self.assertEqual([x.id for x in self.sv.propuestas()], [p.id, otra.id])
        self.assertEqual([x.id for x in self.sv.propuestas(tipo="equivalencia")], [otra.id])
        self.assertEqual([x.id for x in self.sv.propuestas(estado="pendiente")], [p.id, otra.id])
        self.assertEqual(self.sv.propuestas(estado="aprobada"), [])
        with self.assertRaises(PropuestaNoExiste):
            self.sv.propuesta(987)
        with self.assertRaises(PropuestaInvalida):  # un estado que no existe no es una lista vacía
            self.sv.propuestas(estado="olvidada")
        with self.assertRaises(PropuestaInvalida):
            self.sv.alertas(estado="olvidada")

    def test_quien_tiene_varios_roles_deja_la_propuesta_con_uno_que_no_cambia(self):
        con_dos = self.sv.proponer("equivalencia", "ISN-02005", {"equivale_a": "ISN-02001"}, "Descripciones idénticas",
                                   usuario="ana@obra.mx", rol=["supervisor", "costos"])
        self.assertEqual(con_dos.propuesto_con_rol, "costos")  # el primero por orden alfabético: el mismo cada vez
        con_uno = self.sv.proponer("equivalencia", "ISN-02006", {"equivale_a": "ISN-02001"}, "Descripciones idénticas",
                                   usuario="ana@obra.mx", rol="residente")  # un solo rol, dicho como texto
        self.assertEqual(con_uno.propuesto_con_rol, "residente")

    def test_lo_que_no_es_una_propuesta_no_entra(self):
        invalidas = [
            dict(evidencia="  "),  # una propuesta sin evidencia es una orden disfrazada
            dict(tipo="invento"),
            dict(objeto=" "),
            dict(tipo="equivalencia", objeto=" ", valor={"equivale_a": "ISN-02001"}),  # un tipo sin forma propia tampoco recae en nada
            dict(valor={}),  # sin un valor que proponer es una alerta
            dict(valor={"original": "AUX-00001"}),  # falta la clave del clon
            dict(valor={"original": "AUX-00001", "clave": "PRE-00120", "modo": "duplicar"}),
            dict(valor={"original": "AUX-00001", "clave": "AUX-00001"}),
            dict(valor={"original": "AUX-00001", "clave": "PRE-00120", "de_mas": 1}),
            dict(valor={"original": "AUX-00002", "clave": "PRE-00120"}),  # recae en otra cosa que el objeto
            dict(valor={"viejo": "AUX", "nuevo": "AUX"}, objeto="AUX"),
            dict(valor={"viejo": "AUX", "nuevo": "PRE", "desde": 0}, objeto="AUX"),
            dict(valor={"viejo": "AUX", "nuevo": "PRE"}, objeto="PRE"),
            dict(valor={"viejo": "AUX", "nuevo": "PRE", "de_mas": 1}, objeto="AUX"),
            dict(valor={"viejo": "AUX", "nuevo": "PRE", "desde": "120"}, objeto="AUX"),  # el número de la primera clave nueva es un número
            dict(valor={"viejo": "AUX", "nuevo": "PRE", "desde": 1.5}, objeto="AUX"),
            dict(valor={"viejo": "AUX", "nuevo": "PRE", "desde": True}, objeto="AUX"),
            dict(valor={"original": "AUX-00001", "clave": {1, 2}}),  # no es JSON
            dict(tipo="equivalencia", objeto="ISN-02005", valor={}),  # sin valor, aunque el tipo no tenga forma propia
            dict(base=-1),
            dict(base=True),  # un sí no es el número de una carga
            dict(origen="robot"),
            dict(modelo="llama"),  # el modelo es de una propuesta del agente
            dict(confianza="alta"),
        ]
        for mal in invalidas:
            with self.assertRaises(PropuestaInvalida, msg=str(mal)):
                self.proponer(**mal)
        with self.assertRaises(PropuestaInvalida):
            self.sv.proponer("clonacion", "AUX-00001", CLONAR_LA_TRABE, EVIDENCIA, usuario=" ", rol=["costos"])
        with self.assertRaises(PermisoDenegado):  # sin ningún rol no se deja ni una propuesta
            self.sv.proponer("clonacion", "AUX-00001", CLONAR_LA_TRABE, EVIDENCIA, usuario="x@obra.mx", rol=[])
        self.assertEqual(self.sv.propuestas(), [])

    def test_el_agente_deja_propuestas_con_su_modelo_y_sin_rol_de_persona(self):
        p = self.sv.proponer("clonacion", "AUX-00001", CLONAR_LA_TRABE, EVIDENCIA, usuario="gravity", origen="agente", modelo="llama-3.1-8b",
                             version_modelo="2026-09", confianza="media", supuestos={"ritmo": "últimos tres meses"}, base=3)
        self.assertEqual((p.origen, p.propuesto_por, p.propuesto_con_rol, p.modelo, p.version_modelo, p.confianza, p.base),
                         ("agente", "gravity", "agente", "llama-3.1-8b", "2026-09", "media", 3))
        self.assertEqual(dict(p.supuestos), {"ritmo": "últimos tres meses"})
        with self.assertRaises(PropuestaInvalida):  # un agente dice qué modelo
            self.sv.proponer("equivalencia", "X", {"a": 1}, "e", usuario="gravity", origen="agente")
        with self.assertRaises(PropuestaInvalida):  # y la confianza es una de tres
            self.sv.proponer("equivalencia", "X", {"a": 1}, "e", usuario="gravity", origen="agente", modelo="m", confianza="altísima")

    def test_una_igual_pendiente_no_se_amontona_y_una_rechazada_no_se_repite_sin_evidencia_nueva(self):
        p = self.proponer()
        with self.assertRaises(YaPropuesta) as e:
            self.proponer(persona=ROSA)  # otra persona, la misma propuesta
        self.assertEqual(e.exception.propuesta_id, p.id)
        self.sv.resolver(p.id, "rechazar", **quien(LUIS), nota="Todavía no: lo decide Costos con el cliente")
        with self.assertRaises(RechazadaAntes) as e:
            self.proponer(evidencia="  " + EVIDENCIA.upper() + "  ")  # las mismas palabras no son evidencia nueva
        self.assertEqual(e.exception.propuesta_id, p.id)
        nueva = self.proponer(evidencia=EVIDENCIA + " Y además el cliente ya lo confirmó por escrito.")  # evidencia que no existía
        self.assertEqual((nueva.id, nueva.estado), (2, "pendiente"))
        self.assertEqual(self.proponer(valor={"original": "AUX-00001", "clave": "PRE-00121"}).id, 3)  # otro valor es otra propuesta
        uno = self.proponer(tipo="equivalencia", objeto="ISN-02005", valor={"equivale_a": "ISN-02001"}, evidencia="Descripciones idénticas")
        otro = self.proponer(tipo="equivalencia", objeto="ISN-02006", valor={"equivale_a": "ISN-02001"}, evidencia="Descripciones idénticas")
        self.assertNotEqual(uno.id, otro.id)  # el mismo valor sobre otro objeto es otra propuesta, no un duplicado

    # ------------------------------------------------------------------ rechazar y aprobar
    def test_rechazar_pide_la_funcion_y_decir_por_que_y_el_rechazo_se_conserva(self):
        p = self.proponer()
        with self.assertRaises(PermisoDenegado):  # Costos propone, no resuelve
            self.sv.resolver(p.id, "rechazar", **quien(ANA), nota="no")
        with self.assertRaises(PropuestaInvalida):  # rechazar sin decir por qué no sirve de nada
            self.sv.resolver(p.id, "rechazar", **quien(LUIS), nota="  ")
        with self.assertRaises(PropuestaInvalida):
            self.sv.resolver(p.id, "quizá", **quien(LUIS), nota="x")
        with self.assertRaises(PropuestaInvalida):  # toda resolución dice quién la tomó
            self.sv.resolver(p.id, "rechazar", usuario="  ", rol=["control_de_obra"], nota="x")
        self.assertEqual(self.sv.propuesta(p.id).estado, "pendiente")
        r = self.sv.resolver(p.id, "rechazar", **quien(LUIS), nota="  Lo decide Costos ")  # lo que se guarda no lleva los espacios de teclear
        self.assertEqual((r.estado, r.resuelto_por, r.resuelto_con_rol, r.nota, r.resultado), ("rechazada", "luis@obra.mx", "control_de_obra", "Lo decide Costos", None))
        self.assertIsNotNone(r.resuelta_en)
        self.assertEqual((r.tipo, dict(r.valor_propuesto), r.evidencia), (p.tipo, dict(p.valor_propuesto), p.evidencia))  # lo propuesto no cambia
        self.assertEqual([x.id for x in self.sv.propuestas(estado="rechazada")], [p.id])  # se conserva
        for decision in ("rechazar", "aprobar"):
            with self.assertRaises(YaResuelta) as e:  # una vez
                self.sv.resolver(p.id, decision, **quien(LUIS), nota="otra vez")
            self.assertEqual(e.exception.estado, "rechazada")
        with self.assertRaises(PropuestaNoExiste):
            self.sv.resolver(987, "rechazar", **quien(LUIS), nota="x")

    def test_quien_propone_no_aprueba_lo_suyo(self):
        self.cargado()
        p = self.proponer(persona=LUIS)  # Control de obra puede clonar y puede resolver, pero no su propia propuesta
        for quien_es in ("luis@obra.mx", "LUIS@obra.mx"):
            with self.assertRaises(AutoAprobacion):
                self.sv.resolver(p.id, "aprobar", usuario=quien_es, rol=["control_de_obra"])
        self.assertEqual(self.sv.propuesta(p.id).estado, "pendiente")
        self.assertEqual(self.cat.clones(), [])

    def test_el_adaptador_tambien_impide_que_quien_propuso_apruebe_su_propuesta(self):
        p = self.proponer(persona=LUIS, tipo="equivalencia", objeto="ISN-02005", valor={"equivale_a": "ISN-02001"}, evidencia="Descripciones idénticas")
        with self.assertRaises(Exception):  # la memoria lo dice con ValueError y la base con su restricción: lo que importa es que no pasa
            self.bandeja.resolver_propuesta(p.id, "aprobada", "LUIS@obra.mx", "control_de_obra", None, {"hecho": True})
        self.assertEqual(self.bandeja.propuesta(p.id).estado, "pendiente")

    def test_un_tipo_sin_operacion_se_puede_rechazar_pero_no_aprobar(self):
        p = self.proponer(tipo="equivalencia", objeto="ISN-02005", valor={"equivale_a": "ISN-02001"}, evidencia="Descripciones idénticas")
        with self.assertRaises(SinOperacion) as e:
            self.sv.resolver(p.id, "aprobar", **quien(LUIS))
        self.assertEqual(e.exception.tipo, "equivalencia")
        self.assertEqual(self.sv.propuesta(p.id).estado, "pendiente")  # no se dice que algo se hizo cuando no se hizo
        self.assertEqual(self.sv.resolver(p.id, "rechazar", **quien(LUIS), nota="No son lo mismo").estado, "rechazada")

    def test_aprobar_una_clonacion_la_hace_con_la_identidad_de_quien_aprueba(self):
        self.cargado()
        p = self.proponer(base=self.ultima_carga())  # Costos la deja: Costos no puede clonar
        r = self.sv.resolver(p.id, "aprobar", **quien(LUIS), nota="Confirmado con Costos")
        self.assertEqual((r.estado, r.resuelto_por, r.resuelto_con_rol, r.nota), ("aprobada", "luis@obra.mx", "control_de_obra", "Confirmado con Costos"))
        self.assertEqual((r.resultado["clon"], r.resultado["modo"], r.resultado["versiones_nuevas"], r.resultado["renglones_fijados"]), ("PRE-00120", "sustituir", 9, 9))
        (c,) = self.cat.clones()
        self.assertEqual((c.original, c.clon, c.modo, c.usuario, c.rol), ("AUX-00001", "PRE-00120", "sustituir", "luis@obra.mx", "control_de_obra"))
        self.assertEqual(c.carga_id, r.resultado["carga_id"])  # la clonación dice quién la hizo: quien aprobó, no quien propuso
        self.assertNotEqual(c.usuario, p.propuesto_por)

    def test_aprobar_pide_la_funcion_de_la_accion_ademas_de_resolver_la_bandeja(self):
        self.cargado()
        self.acc.dar_funcion("costos", "aprobar_propuesta")  # Costos puede resolver la bandeja, pero no clonar
        p = self.proponer(persona=ROSA)
        with self.assertRaises(PermisoDenegado) as e:
            self.sv.resolver(p.id, "aprobar", **quien(ANA))
        self.assertIn("clonar", str(e.exception))
        self.assertEqual((self.sv.propuesta(p.id).estado, self.cat.clones()), ("pendiente", []))
        self.acc.dar_funcion("costos", "clonar_insumo")  # y ahora que sí puede, aprueba
        self.assertEqual(self.sv.resolver(p.id, "aprobar", **quien(ANA)).estado, "aprobada")
        self.assertEqual(len(self.cat.clones()), 1)

    def test_la_bandeja_pide_la_funcion_de_la_accion_aunque_la_operacion_no_la_compruebe(self):
        llamadas = []
        ejecutar = lambda valor, rol, usuario, esperaba: llamadas.append((usuario, esperaba)) or {"hecho": True}  # una operación que no mira permisos
        sv = ServicioBandeja(self.bandeja, self.acc.permisos, {"clonacion": TipoDePropuesta("clonacion", "clonar_insumo", None, ejecutar)})
        self.acc.dar_funcion("costos", "aprobar_propuesta")
        p = sv.proponer("clonacion", "AUX-00001", {"a": 1}, "porque sí", **quien(ROSA), base=4)
        with self.assertRaises(PermisoDenegado):  # resolver la bandeja no basta
            sv.resolver(p.id, "aprobar", **quien(ANA))
        self.assertEqual((llamadas, sv.propuesta(p.id).estado), ([], "pendiente"))  # y no se ejecutó nada
        self.acc.dar_funcion("costos", "clonar_insumo")
        self.assertEqual(sv.resolver(p.id, "aprobar", **quien(ANA)).estado, "aprobada")
        self.assertEqual(llamadas, [("ana@obra.mx", 4)])  # con la identidad de quien aprueba y la base de lo que se vio

    def test_si_el_catalogo_cambio_desde_que_se_vio_no_se_aplica(self):
        self.cargado()
        p = self.proponer(base=self.ultima_carga())  # vio el catálogo en la carga 1
        self.mover_el_acero()  # y alguien más carga
        with self.assertRaises(CatalogoCambio):
            self.sv.resolver(p.id, "aprobar", **quien(LUIS))  # `esperaba` sale de lo que vio quien propuso
        self.assertEqual((self.sv.propuesta(p.id).estado, self.cat.clones()), ("pendiente", []))
        with self.assertRaises(CatalogoCambio):
            self.sv.resolver(p.id, "aprobar", **quien(LUIS), esperaba=1)
        r = self.sv.resolver(p.id, "aprobar", **quien(LUIS), esperaba=self.ultima_carga())  # quien aprueba mira lo de hoy y lo dice
        self.assertEqual(r.estado, "aprobada")

    def test_lo_que_impide_la_operacion_deja_la_propuesta_pendiente_para_corregirla_o_rechazarla(self):
        self.cargado()
        p = self.proponer(valor={"original": "AUX-00001", "clave": "PRE-00001"})  # esa clave ya existe
        with self.assertRaises(ClonacionNoProcede):
            self.sv.resolver(p.id, "aprobar", **quien(LUIS))
        self.assertEqual((self.sv.propuesta(p.id).estado, self.cat.clones()), ("pendiente", []))
        self.assertEqual(self.sv.resolver(p.id, "rechazar", **quien(LUIS), nota="La clave ya existe").estado, "rechazada")

    def test_se_aprueba_la_correccion_de_un_prefijo_entero(self):
        self.cargado()
        p = self.sv.proponer("clonacion", "AUX", {"viejo": "AUX", "nuevo": "PRE", "desde": 120}, "Las 79 claves AUX- son materiales (P-11)",
                             **quien(ANA), base=self.ultima_carga())
        r = self.sv.resolver(p.id, "aprobar", **quien(LUIS))
        self.assertEqual((len(r.resultado["hechos"]), r.resultado["rechazados"]), (79, []))
        self.assertEqual((r.resultado["hechos"][0]["original"], r.resultado["hechos"][0]["clon"], r.resultado["hechos"][-1]["clon"]),
                         ("AUX-00001", "PRE-00120", "PRE-00198"))
        self.assertEqual(len(self.cat.clones()), 79)
        self.assertEqual({c.usuario for c in self.cat.clones()}, {"luis@obra.mx"})

    def test_lo_que_un_renglon_contratado_cita_se_salta_y_se_dice_y_el_resto_se_hace(self):
        self.cargado()
        from core.contratacion import ServicioContratacion

        ServicioContratacion(self.cat).contratar("CAS-00004", "control_de_obra", "luis@obra.mx", "CAS-00004#1/NIV-00001#1")
        # AUX-00030, -01010, -01030, -02010 y -02030 los citan renglones contratados: se dicen y no se tocan; las otras 74 sí se sustituyen
        p = self.sv.proponer("clonacion", "AUX", {"viejo": "AUX", "nuevo": "PRE", "desde": 120}, "P-11", **quien(ANA))
        r = self.sv.resolver(p.id, "aprobar", **quien(LUIS))
        self.assertEqual((len(r.resultado["hechos"]), sorted(x["original"] for x in r.resultado["rechazados"])),
                         (74, ["AUX-00030", "AUX-01010", "AUX-01030", "AUX-02010", "AUX-02030"]))
        self.assertEqual(r.resultado["versiones_nuevas"], sum(h["versiones_nuevas"] for h in r.resultado["hechos"]))

    def test_un_prefijo_sin_claves_no_tiene_nada_que_hacer_y_se_dice_en_el_resultado(self):
        self.cargado()
        p = self.sv.proponer("clonacion", "ZZZ", {"viejo": "ZZZ", "nuevo": "PRE", "desde": 120}, "Una errata del prefijo", **quien(ANA))
        r = self.sv.resolver(p.id, "aprobar", **quien(LUIS))
        self.assertEqual((r.estado, r.resultado["hechos"], r.resultado["rechazados"], r.resultado["versiones_nuevas"]), ("aprobada", [], [], 0))
        self.assertEqual(self.cat.clones(), [])

    def test_una_correccion_donde_nada_se_pudo_sustituir_no_se_da_por_hecha(self):
        from types import SimpleNamespace

        from core.clonacion import ResultadoDeCorreccion

        class Atorada:  # el servicio de clonación cuando todo lo que se quería sustituir lo cita algo contratado
            def corregir_prefijo(self, *args):
                return ResultadoDeCorreccion((), (SimpleNamespace(original="AUX-00001", clave="PRE-00120", problemas=("lo cita un renglón contratado",)),))

        sv = ServicioBandeja(self.bandeja, self.acc.permisos, tipos_de_propuesta(Atorada()))
        p = sv.proponer("clonacion", "AUX", {"viejo": "AUX", "nuevo": "PRE"}, "P-11", **quien(ANA))
        self.assertEqual(dict(p.valor_propuesto), {"viejo": "AUX", "nuevo": "PRE", "desde": 1})  # el desde por omisión, dicho
        with self.assertRaises(ClonacionNoProcede) as e:
            sv.resolver(p.id, "aprobar", **quien(LUIS))
        self.assertIn("contratado", str(e.exception))
        self.assertEqual(sv.propuesta(p.id).estado, "pendiente")  # no se dice que se hizo lo que no se hizo

    # ------------------------------------------------------------------ alertas
    def test_una_alerta_que_reaparece_se_cuenta_no_se_repite(self):
        a = self.sv.alertar("frente_listo_para_cierre", {"avance": 0.91}, objeto="FRENTE-1", parametro_usado={"porcentaje": 90})
        self.assertEqual((a.tipo, a.objeto, a.veces_vista, a.estado), ("frente_listo_para_cierre", "FRENTE-1", 1, "activa"))
        self.assertEqual(dict(a.parametro_usado), {"porcentaje": 90})
        otra_vez = self.sv.alertar("frente_listo_para_cierre", {"avance": 0.95}, objeto="FRENTE-1")
        self.assertEqual((otra_vez.id, otra_vez.veces_vista, dict(otra_vez.evidencia)), (a.id, 2, {"avance": 0.95}))  # la evidencia de hoy
        self.assertEqual(dict(otra_vez.parametro_usado), {"porcentaje": 90})  # el umbral que la disparó no se pierde
        self.assertGreaterEqual(otra_vez.ultima_vez, otra_vez.primera_vez)
        self.assertEqual(otra_vez.primera_vez, a.primera_vez)
        b = self.sv.alertar("frente_listo_para_cierre", {"avance": 0.9}, objeto="FRENTE-2")  # otro objeto, otra alerta
        c = self.sv.alertar("invariante_por_vencer", {"meses": 7})  # sin objeto: es sobre el archivo completo
        self.assertEqual(len({a.id, b.id, c.id}), 3)
        self.assertEqual(self.sv.alertar("invariante_por_vencer", {"meses": 8}, objeto="").id, c.id)
        self.assertEqual(self.sv.alerta(c.id).veces_vista, 2)
        self.assertEqual(sorted(x.id for x in self.sv.alertas(estado="activa")), sorted([a.id, b.id, c.id]))
        self.assertEqual([x.id for x in self.sv.alertas(tipo="invariante_por_vencer")], [c.id])
        with self.assertRaises(AlertaNoExiste):
            self.sv.alerta(987)

    def test_una_alerta_sin_evidencia_no_es_una_alerta(self):
        for mal in (dict(tipo=" ", evidencia={"a": 1}), dict(tipo="x", evidencia={}), dict(tipo="x", evidencia={"a": {1, 2}})):
            with self.assertRaises(PropuestaInvalida, msg=str(mal)):
                self.sv.alertar(**mal)
        self.assertEqual(self.sv.alertas(), [])

    def test_resolver_una_alerta_pide_la_funcion_y_decir_que_era_y_nunca_se_resuelve_sola(self):
        a = self.sv.alertar("subfrente_detenido", {"dias": 25}, objeto="CIM-2")
        with self.assertRaises(PermisoDenegado):  # Costos no cierra alertas
            self.sv.resolver_alerta(a.id, "resuelta", **quien(ANA), nota="visto")
        with self.assertRaises(PropuestaInvalida):  # se cierra diciendo qué era
            self.sv.resolver_alerta(a.id, "resuelta", **quien(SOFIA), nota=" ")
        with self.assertRaises(PropuestaInvalida):
            self.sv.resolver_alerta(a.id, "olvidada", **quien(SOFIA), nota="x")
        with self.assertRaises(PropuestaInvalida):  # toda resolución dice quién la tomó
            self.sv.resolver_alerta(a.id, "resuelta", usuario="  ", rol=["supervisor"], nota="x")
        self.assertEqual(self.sv.alerta(a.id).estado, "activa")
        r = self.sv.resolver_alerta(a.id, "descartada", **quien(SOFIA), nota="El avance no se había capturado")
        self.assertEqual((r.estado, r.resuelto_por, r.resuelto_con_rol, r.nota_resolucion), ("descartada", "sofia@obra.mx", "supervisor", "El avance no se había capturado"))
        self.assertIsNotNone(r.resuelta_en)
        with self.assertRaises(YaResuelta):
            self.sv.resolver_alerta(a.id, "resuelta", **quien(LUIS), nota="otra vez")
        nueva = self.sv.alertar("subfrente_detenido", {"dias": 30}, objeto="CIM-2")  # resuelta una, la que reaparece es otra historia
        self.assertEqual((nueva.id, nueva.veces_vista, nueva.estado), (2, 1, "activa"))
        self.assertEqual(self.sv.alerta(a.id).veces_vista, 1)  # y la resuelta quedó como quedó
        self.assertEqual(self.sv.resolver_alerta(nueva.id, "resuelta", **quien(LUIS), nota="Se retomó").estado, "resuelta")

    def test_el_resumen_dice_lo_que_hay_pendiente(self):
        self.assertEqual((self.sv.resumen().propuestas_pendientes, self.sv.resumen().alertas_activas, self.sv.resumen().alerta_mas_vista), (0, 0, None))
        a = self.proponer()
        self.proponer(tipo="equivalencia", objeto="ISN-02005", valor={"equivale_a": "ISN-02001"}, evidencia="Descripciones idénticas")
        self.proponer(tipo="equivalencia", objeto="ISN-02006", valor={"equivale_a": "ISN-02002"}, evidencia="Descripciones idénticas")
        self.sv.resolver(a.id, "rechazar", **quien(LUIS), nota="No")
        for _ in range(3):
            self.sv.alertar("obra_atrasada", {"dias": 4}, objeto="ALAMO 18")
        self.sv.alertar("subfrente_detenido", {"dias": 22}, objeto="CIM-2")  # la última en verse no es la que más vuelve
        r = self.sv.resumen()
        self.assertEqual((r.propuestas_pendientes, dict(r.pendientes_por_tipo)), (2, {"equivalencia": 2}))  # lo rechazado ya no es pendiente
        self.assertEqual((r.alertas_activas, dict(r.alertas_por_tipo)), (2, {"obra_atrasada": 1, "subfrente_detenido": 1}))
        self.assertEqual((r.alerta_mas_vista.tipo, r.alerta_mas_vista.veces_vista), ("obra_atrasada", 3))

    def test_la_tabla_de_permisos_manda_desde_la_siguiente_accion(self):
        p = self.proponer(tipo="equivalencia", objeto="ISN-02005", valor={"equivale_a": "ISN-02001"}, evidencia="Descripciones idénticas")
        with self.assertRaises(PermisoDenegado):
            self.sv.resolver(p.id, "rechazar", **quien(ROSA), nota="x")
        self.acc.dar_funcion("residente", "aprobar_propuesta")
        self.assertEqual(self.sv.resolver(p.id, "rechazar", **quien(ROSA), nota="No son lo mismo").estado, "rechazada")
        q = self.proponer(tipo="equivalencia", objeto="ISN-02006", valor={"equivale_a": "ISN-02002"}, evidencia="Descripciones idénticas")
        self.acc.quitar_funcion("control_de_obra", "aprobar_propuesta")
        with self.assertRaises(PermisoDenegado):
            self.sv.resolver(q.id, "rechazar", **quien(LUIS), nota="x")
