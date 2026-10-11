"""
Contratar un subárbol del presupuesto (D-475): el contrato que cumplen los adaptadores del catálogo, con los siete presupuestos de
verdad y un precio que se mueve de verdad (el del acero, `ACE-00001`, en los archivos de OPUS). Mezclar con `unittest.TestCase` y
definir `nuevo_repositorio()`.

La cimentación de Zafiro (`CAS-00004#1/NIV-00001#1`) es el bloque que se contrata en casi todas: son 56 conceptos en 56 renglones y
suma $178,768.69 en el archivo.
"""
from dataclasses import replace
from decimal import Decimal

from core.accesos import PermisoDenegado
from core.catalogo import CatalogoCambio, EN_CONTRATADO, ServicioCarga, YaContratado
from core.contratacion import (
    ContratacionPendiente,
    FIJAR_VIGENTE,
    IGUAL,
    SIN_MATRIZ,
    ServicioContratacion,
    VERSION_NUEVA,
    informe_de_contratacion,
    nodos_contratados,
)
from core.tests.contrato_catalogo import CAPITULOS, USUARIO
from core.tests.datos_opus import CONCEPTOS, PRESUPUESTO, reescalar_costo, reescalar_linea, texto

QUIEN = "luis@obra.mx"
CO = "control_de_obra"
ZAFIRO = "CAS-00004"
CIMENTACION = "CAS-00004#1/NIV-00001#1"
TOTAL_DE_LA_CIMENTACION = Decimal("178768.69")


class ContratoContratacion:
    def nuevo_repositorio(self):  # pragma: no cover
        raise NotImplementedError

    def setUp(self):
        self.repo = self.nuevo_repositorio()
        self.carga = ServicioCarga(self.repo)
        self.con = texto(CONCEPTOS)
        self.carga.aplicar(self.con, texto(PRESUPUESTO), None, rol="costos", usuario=USUARIO)
        self.sc = ServicioContratacion(self.repo)

    def mover_el_acero(self, factor):
        """Una carga nueva en la que el acero costó `factor` veces lo de antes: solo un precio, ninguna receta."""
        r = self.carga.aplicar(reescalar_costo(self.con, "ACE-00001", Decimal(factor)), texto(PRESUPUESTO), None, rol="costos", usuario=USUARIO)
        self.assertEqual(r.resumen["versiones_nuevas"], 0)
        return r

    def proponer(self, donde=CIMENTACION, **kw):
        return self.sc.proponer(ZAFIRO, CO, QUIEN, donde, **kw)

    def zafiro(self):
        return next(p for p in self.repo.presupuestos() if p.clave == ZAFIRO)

    def renglones_de(self, clave, presupuesto=ZAFIRO):
        p = next(p for p in self.repo.presupuestos() if p.clave == presupuesto)
        return [r for r in self.carga.presupuesto(p.id).renglones if r.clave == clave]

    # ------------------------------------------------------------------ contratar sin que nada se haya movido
    def test_contratar_la_cimentacion_de_zafiro_la_congela_y_no_cambia_ningun_precio(self):
        p = self.proponer()
        self.assertEqual((len(p.conceptos), p.renglones, p.ya_contratados), (56, 56, 0))
        self.assertEqual((p.total_antes, p.total_despues, p.plan.versiones_nuevas, p.plan.renglones), (TOTAL_DE_LA_CIMENTACION,) * 2 + ((), ()))
        self.assertTrue(p.aplicable)
        self.assertEqual({c.accion for c in p.conceptos}, {IGUAL})
        antes = self.repo.cargas()
        _, r = self.sc.contratar(ZAFIRO, CO, QUIEN, CIMENTACION)
        self.assertEqual((r.versiones_nuevas, r.renglones_fijados), (0, 0))
        (c,) = self.sc.contratados(ZAFIRO)
        self.assertEqual((c.ruta, c.estado, c.usuario, c.rol, c.carga_id), (CIMENTACION, "contratado", QUIEN, CO, r.carga_id))
        self.assertEqual(c.resumen["total_antes"], c.resumen["total_despues"])
        # una contratación deja su carga, con quién y qué rol, y sin archivos
        nueva = self.repo.cargas()[len(antes):]
        self.assertEqual([(x.tipo, x.usuario, x.rol, dict(x.archivos)) for x in nueva], [("contratacion", QUIEN, CO, {})])
        self.assertEqual([x.tipo for x in antes], ["archivos"])
        self.assertEqual(self.carga.presupuesto(self.zafiro().id).total, Decimal(CAPITULOS[ZAFIRO]))
        self.assertEqual(len(self.repo.versiones("EST-10010")), 1)  # nada nuevo: ya estaban al precio de hoy

    def test_un_bloque_o_presupuesto_que_no_existe_se_dice(self):
        for donde in ("CAS-00004#1/NIV-99999#1", 987654):
            with self.assertRaises(ValueError):
                self.proponer(donde)
        with self.assertRaises(ValueError):
            self.sc.proponer("CAS-99999", CO, QUIEN)
        self.assertEqual(self.sc.contratados(ZAFIRO), ())

    def test_sin_decir_donde_se_contrata_el_presupuesto_entero(self):
        p = self.proponer(None)
        self.assertEqual((p.ruta, p.renglones, p.total_antes), ("CAS-00004#1", 315, Decimal(CAPITULOS[ZAFIRO])))

    # ------------------------------------------------------------------ un precio que se movió
    def test_contratar_fija_el_pu_de_hoy_en_versiones_nuevas_con_la_misma_receta(self):
        self.mover_el_acero("1.02")
        viejo = self.repo.versiones("EST-10010")[0]
        p = self.proponer()
        self.assertEqual(len(p.plan.versiones_nuevas), 25)  # los conceptos de la cimentación que llevan acero
        self.assertEqual({c.accion for c in p.conceptos}, {IGUAL, VERSION_NUEVA})
        self.assertGreater(p.total_despues, p.total_antes)
        self.assertEqual(p.total_antes, TOTAL_DE_LA_CIMENTACION)
        _, r = self.sc.contratar(ZAFIRO, CO, QUIEN, CIMENTACION)
        self.assertEqual((r.versiones_nuevas, r.renglones_fijados), (25, 25))
        v1, v2 = self.repo.versiones("EST-10010")
        self.assertEqual(v1, viejo)  # la anterior ni se enteró
        self.assertEqual((v2.version, v2.huella, v2.lineas, v2.carga_id), (2, v1.huella, v1.lineas, r.carga_id))  # misma receta, otra carga
        self.assertEqual(v2.pu, next(c.pu_hoy for c in p.conceptos if c.clave == "EST-10010"))
        self.assertGreater(v2.pu, v1.pu)
        # el presupuesto leído de vuelta dice lo mismo que la propuesta: el renglón fija la 2 y el bloque suma lo que se dijo
        (renglon,) = self.renglones_de("EST-10010")
        self.assertEqual((renglon.version, renglon.pu), (2, v2.pu))
        zafiro = self.carga.presupuesto(self.zafiro().id)
        bloque = next(x for x in zafiro.renglones if x.clave == "NIV-00001")
        self.assertEqual(bloque.total, p.total_despues)

    def test_lo_que_no_se_contrato_sigue_fijando_su_version_y_su_precio(self):
        self.mover_el_acero("1.02")
        antes = {p.clave: self.carga.presupuesto(p.id).total for p in self.repo.presupuestos()}
        self.sc.contratar(ZAFIRO, CO, QUIEN, CIMENTACION)
        despues = {p.clave: self.carga.presupuesto(p.id).total for p in self.repo.presupuestos()}
        self.assertEqual({k: v for k, v in despues.items() if k != ZAFIRO}, {k: v for k, v in antes.items() if k != ZAFIRO})  # los otros seis
        self.assertGreater(despues[ZAFIRO], antes[ZAFIRO])
        # el resto de Zafiro, tampoco: solo la cimentación
        self.assertTrue(self.renglones_de("EST-10010"))
        resto = [r for r in self.renglones_de("EST-10010") if r.version != 2]
        self.assertEqual(resto, [])  # el acero K1 solo está en la cimentación…
        otros = [(p.clave, r.version) for p in self.repo.presupuestos() if p.clave != ZAFIRO
                 for r in self.carga.presupuesto(p.id).renglones if r.clave == "EST-10010"]
        self.assertTrue(otros and {v for _, v in otros} == {1})  # …y en los demás prototipos sigue la 1

    def test_mas_de_5_por_ciento_pide_confirmacion_y_no_se_contrata_a_medias(self):
        self.mover_el_acero("4")
        cargas = len(self.repo.cargas())
        p = self.proponer()
        pide = ["EST-10010", "EST-10020", "EST-10021", "EST-10031", "EST-10041"]
        self.assertEqual([x.clave for x in p.pendientes], pide)
        self.assertFalse(p.aplicable)
        with self.assertRaises(ContratacionPendiente) as e:
            self.sc.contratar(ZAFIRO, CO, QUIEN, CIMENTACION)
        self.assertEqual([x.clave for x in e.exception.propuesta.pendientes], pide)
        self.assertEqual((self.sc.contratados(ZAFIRO), len(self.repo.cargas()), len(self.repo.versiones("EST-10010"))), ((), cargas, 1))
        # quien decide confirma esos cinco y entonces sí
        _, r = self.sc.contratar(ZAFIRO, CO, QUIEN, CIMENTACION, confirmados=pide)
        self.assertEqual(r.versiones_nuevas, 25)
        (c,) = self.sc.contratados(ZAFIRO)
        self.assertEqual(c.resumen["confirmados"], sorted(pide))

    def test_el_informe_dice_que_se_fija_y_cuanto_cambia_el_monto(self):
        self.mover_el_acero("4")
        t = informe_de_contratacion(self.proponer())
        self.assertIn("Contratar CAS-00004#1/NIV-00001#1 — CIMENTACIÓN (presupuesto CAS-00004)", t)
        self.assertIn("56 conceptos en 56 renglones", t)
        self.assertIn("25 versiones nuevas", t)
        self.assertIn("EST-10010", t)
        self.assertIn("Piden confirmación", t)

    # ------------------------------------------------------------------ lo contratado se respeta
    def test_lo_contratado_no_se_vuelve_a_contratar_ni_por_arriba_ni_por_abajo(self):
        self.sc.contratar(ZAFIRO, CO, QUIEN, CIMENTACION)
        ECO = "CAS-00004#1/NIV-00001#1/ECO-00001#1"
        for donde in (CIMENTACION, ECO):  # el mismo, y uno que cuelga de él
            with self.assertRaises(YaContratado):
                self.proponer(donde)
        self.assertEqual(len(self.sc.contratados(ZAFIRO)), 1)

    def test_contratar_un_bloque_respeta_los_renglones_de_uno_de_abajo_que_ya_estaba_contratado(self):
        self.mover_el_acero("1.02")
        ECO = "CAS-00004#1/NIV-00001#1/ECO-00001#1"
        _, r1 = self.sc.contratar(ZAFIRO, CO, QUIEN, ECO)
        # el acero sube otra vez: lo que ya se contrató no se entera
        self.carga.aplicar(reescalar_costo(self.con, "ACE-00001", Decimal("1.04")), texto(PRESUPUESTO), None, rol="costos", usuario=USUARIO)
        p = self.proponer(CIMENTACION)
        self.assertGreater(p.ya_contratados, 0)
        self.assertEqual(p.renglones + p.ya_contratados, 56)
        antes = {(r.clave, r.version) for r in self.renglones_de("EST-01040")}
        self.sc.contratar(ZAFIRO, CO, QUIEN, CIMENTACION)
        self.assertEqual({(r.clave, r.version) for r in self.renglones_de("EST-01040")}, antes)  # EST-01040 es del ECO-00001, ya contratado
        self.assertEqual(len(self.sc.contratados(ZAFIRO)), 2)
        datos = self.repo.datos_de_presupuesto(self.zafiro().id)
        bajo = nodos_contratados(datos, self.sc.contratados(ZAFIRO))
        self.assertGreaterEqual({datos.nodos[n].ruta_natural for n in bajo if datos.nodos[n].ruta_natural.startswith(CIMENTACION)}, {CIMENTACION, ECO})
        self.assertLess(r1.carga_id, self.sc.contratados(ZAFIRO)[1].carga_id)

    def test_el_estado_se_hereda_hacia_abajo_y_no_hacia_arriba(self):
        self.sc.contratar(ZAFIRO, CO, QUIEN, CIMENTACION)
        datos = self.repo.datos_de_presupuesto(self.zafiro().id)
        contratados = nodos_contratados(datos, self.sc.contratados(ZAFIRO))
        rutas = {datos.nodos[n].ruta_natural for n in contratados}
        self.assertIn(CIMENTACION, rutas)
        self.assertIn(CIMENTACION + "/ECO-00001#1", rutas)
        self.assertNotIn("CAS-00004#1", rutas)  # el capítulo no se contrató por contratar un subcapítulo
        self.assertTrue(all(r.startswith(CIMENTACION) for r in rutas))

    def test_sin_el_permiso_no_se_propone_ni_se_contrata(self):
        for roles in ("costos", "residente", ["costos", "residente"]):
            with self.assertRaises(PermisoDenegado):
                self.sc.proponer(ZAFIRO, roles, QUIEN, CIMENTACION)
            with self.assertRaises(PermisoDenegado):
                self.sc.contratar(ZAFIRO, roles, QUIEN, CIMENTACION)
        with self.assertRaises(ValueError):
            self.sc.contratar(ZAFIRO, CO, "", CIMENTACION)
        self.assertEqual(self.sc.contratados(ZAFIRO), ())
        self.sc.contratar(ZAFIRO, ["residente", CO], QUIEN, CIMENTACION)

    def test_un_concepto_sin_matriz_pide_que_alguien_confirme_contratarlo_a_cero(self):
        # los cuatro conceptos sin matriz (P-09) y dónde están: un bloque de un presupuesto que tenga alguno
        buscado = None
        for p in self.repo.presupuestos():
            datos = self.repo.datos_de_presupuesto(p.id)
            for l in datos.lineas:
                if datos.nodos[l.hijo_id].clave == "ACC-00003":
                    buscado = (p.clave, datos.nodos[l.padre_id].ruta_natural)
        self.assertIsNotNone(buscado)
        presupuesto, ruta = buscado
        propuesta = self.sc.proponer(presupuesto, CO, QUIEN, ruta)
        self.assertIn(("ACC-00003", SIN_MATRIZ), [(x.clave, x.motivo) for x in propuesta.pendientes])
        with self.assertRaises(ContratacionPendiente):
            self.sc.contratar(presupuesto, CO, QUIEN, ruta)
        sin = [x.clave for x in propuesta.pendientes if x.motivo == SIN_MATRIZ]
        _, r = self.sc.contratar(presupuesto, CO, QUIEN, ruta, confirmados=sin)
        self.assertEqual(len(self.sc.contratados(presupuesto)), 1)
        renglon = next(x for x in self.renglones_de("ACC-00003", presupuesto))
        self.assertEqual((renglon.version, renglon.pu), (None, Decimal("0")))  # sigue valiendo cero: contratarlo no le inventó precio

    # ------------------------------------------------------------------ el candado y lo que no queda a medias
    def test_otra_carga_en_medio_no_se_pisa(self):
        p = self.proponer()
        self.mover_el_acero("1.02")  # alguien cargó entre que se revisó y se quiso contratar
        with self.assertRaises(CatalogoCambio):
            self.repo.contratar(p.plan)
        self.assertEqual(self.sc.contratados(ZAFIRO), ())

    def test_una_contratacion_que_falla_a_medias_no_deja_nada(self):
        self.mover_el_acero("1.02")
        p = self.proponer()
        cargas, version = len(self.repo.cargas()), self.repo.versiones("EST-10010")
        mala = replace(p.plan, renglones=p.plan.renglones + ((987654, "EST-10010"),))  # un renglón que no existe, al final
        with self.assertRaises(ValueError):
            self.repo.contratar(mala)
        self.assertEqual((len(self.repo.cargas()), self.repo.versiones("EST-10010"), self.sc.contratados(ZAFIRO)), (cargas, version, ()))
        self.repo.contratar(p.plan)  # y la buena sigue entrando

    def test_el_puerto_tampoco_contrata_dos_veces_lo_mismo(self):
        p = self.proponer()
        self.repo.contratar(p.plan)
        otra = replace(p.plan, base=len(self.repo.cargas()))
        with self.assertRaises(YaContratado):
            self.repo.contratar(otra)
        self.assertEqual(len(self.sc.contratados(ZAFIRO)), 1)

    # ------------------------------------------------------------------ la carga con algo contratado
    def test_una_carga_no_cambia_la_receta_de_lo_que_algo_contratado_usa(self):
        self.sc.contratar(ZAFIRO, CO, QUIEN, CIMENTACION)
        self.assertIn("EST-10010", self.repo.estado_vigente().en_contratado)
        self.assertNotIn("ACA-01010", self.repo.estado_vigente().en_contratado)
        cambia_acero_k1 = reescalar_linea(self.con, "EST-10010", 0, Decimal("1.1"))  # el K1 de la cimentación, que está contratada
        cambia_mortero = reescalar_linea(cambia_acero_k1, "ACA-01010", 0, Decimal("1.1"))  # y un concepto que ningún bloque contratado usa
        r = self.carga.revisar(cambia_mortero, texto(PRESUPUESTO), None, rol="costos", usuario=USUARIO)
        self.assertEqual([(p.clave, p.motivo) for p in r.diagnostico.pendientes if p.motivo == EN_CONTRATADO], [("EST-10010", EN_CONTRATADO)])
        self.carga.aplicar(cambia_mortero, texto(PRESUPUESTO), None, rol="costos", usuario=USUARIO)
        self.assertEqual(len(self.repo.versiones("EST-10010")), 1)  # lo contratado no cambió de receta: va a control de cambio
        self.assertEqual(len(self.repo.versiones("ACA-01010")), 2)  # lo demás sí
        # y no hay confirmación que lo deje entrar: «clave nueva o control de cambio»
        self.carga.aplicar(cambia_mortero, texto(PRESUPUESTO), None, rol="costos", usuario=USUARIO, confirmados=["EST-10010"])
        self.assertEqual(len(self.repo.versiones("EST-10010")), 1)

    def test_lo_que_no_cambio_se_dice_igual_despues_de_contratar(self):
        self.sc.contratar(ZAFIRO, CO, QUIEN, CIMENTACION)
        r = self.carga.revisar(self.con, texto(PRESUPUESTO), None, rol="costos", usuario=USUARIO)
        self.assertEqual((r.plan.cambia_algo, r.diagnostico.pendientes), (False, ()))
        self.assertEqual(self.carga.aplicar(self.con, texto(PRESUPUESTO), None, rol="costos", usuario=USUARIO).carga_id, None)
