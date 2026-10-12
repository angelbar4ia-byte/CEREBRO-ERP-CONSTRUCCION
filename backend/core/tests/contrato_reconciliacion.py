"""
Reconciliar un presupuesto que ya existe (D-476): el contrato que cumplen los adaptadores del catálogo, con los siete presupuestos de
verdad del archivo de OPUS y ediciones de verdad a ese archivo (una cantidad, una fila que se quita, una que se agrega, dos hermanos
que se cambian de lugar). Mezclar con `unittest.TestCase` y definir `nuevo_repositorio()`.

El renglón de siempre es el acero K1 de la cimentación de Zafiro, `EST-10010`: 37 piezas a $95.01, en el bloque
`CAS-00004#1/NIV-00001#1/ECO-00001#1/EST-01040#1`. Zafiro suma $1,842,426.01.
"""
from dataclasses import replace
from decimal import Decimal

from core.catalogo import BAJA_SIN_CONFIRMAR, CONCEPTO_PENDIENTE, EN_CONTRATADO, PU_MOVIO, ServicioCarga
from core.contratacion import ServicioContratacion
from core.motor_calculo import precio_unitario
from core.tests.contrato_catalogo import CAPITULOS, USUARIO
from core.tests.datos_opus import (
    CONCEPTOS,
    PRESUPUESTO,
    con_cantidad,
    con_copia,
    con_orden_cambiado,
    reescalar_linea,
    sin_renglon,
    texto,
)

ZAFIRO = "CAS-00004"
BLOQUE = "CAS-00004#1/NIV-00001#1/ECO-00001#1/EST-01040#1"
K1 = f"{BLOQUE}::EST-10010#1"
PU_K1 = Decimal("95.01")
CO = "control_de_obra"


class ContratoReconciliacion:
    def nuevo_repositorio(self):  # pragma: no cover
        raise NotImplementedError

    def setUp(self):
        self.repo = self.nuevo_repositorio()
        self.carga = ServicioCarga(self.repo)
        self.con, self.pres = texto(CONCEPTOS), texto(PRESUPUESTO)
        self.carga.aplicar(self.con, self.pres, None, rol="costos", usuario=USUARIO)

    def cargar(self, presupuesto, conceptos=None, **kw):
        return self.carga.aplicar(self.con if conceptos is None else conceptos, presupuesto, None, rol="costos", usuario=USUARIO, **kw)

    def revisar(self, presupuesto, conceptos=None, **kw):
        return self.carga.revisar(self.con if conceptos is None else conceptos, presupuesto, None, rol="costos", usuario=USUARIO, **kw)

    def presupuesto(self, clave=ZAFIRO):
        return next(p for p in self.repo.presupuestos() if p.clave == clave)

    def total(self, clave=ZAFIRO):
        return self.carga.presupuesto(self.presupuesto(clave).id).total

    def renglon(self, clave="EST-10010", n=1, presupuesto=ZAFIRO):
        """El renglón guardado (su id y su línea) de la `n`-ésima vez que el presupuesto nombra esa clave."""
        datos = self.repo.datos_de_presupuesto(self.presupuesto(presupuesto).id)
        return [l for l in sorted(datos.lineas, key=lambda l: (l.padre_id, l.orden)) if datos.nodos[l.hijo_id].clave == clave][n - 1]

    def estado(self, r, clave=ZAFIRO):
        return next(e for e in r.diagnostico.presupuestos if e.clave == clave)

    def otros_seis(self):
        return {c: self.total(c) for c in CAPITULOS if c != ZAFIRO}

    # ------------------------------------------------------------------ una cantidad distinta
    def test_una_cantidad_distinta_actualiza_el_renglon_conserva_su_identidad_y_deja_su_historia(self):
        antes = self.renglon()
        seis = self.otros_seis()
        nuevo = con_cantidad(self.pres, ZAFIRO, "EST-10010", "40")
        r = self.revisar(nuevo)
        self.assertEqual((self.estado(r).estado, self.estado(r).detalle), ("reconciliado", "1 cantidades · 0 altas · 0 bajas"))
        self.assertEqual([(c.tipo, c.id, c.antes, c.ahora, c.estado) for c in r.diagnostico.cambios], [("cantidad", K1, Decimal("37"), Decimal("40"), "aplica")])
        self.assertEqual(self.total(), Decimal(CAPITULOS[ZAFIRO]))  # revisar no escribe
        res = self.cargar(nuevo)
        despues = self.renglon()
        self.assertEqual((despues.id, despues.cantidad), (antes.id, Decimal("40")))  # el mismo renglón: el programa lo sigue citando
        self.assertEqual(self.total(), Decimal(CAPITULOS[ZAFIRO]) + 3 * PU_K1)
        self.assertEqual(self.otros_seis(), seis)
        (h,) = self.repo.historia(antes.id)
        self.assertEqual((h.carga_id, h.campo, h.antes, h.despues), (res.carga_id, "cantidad", "37", "40"))
        self.assertEqual(despues.version, antes.version)  # y sigue fijando la versión que fijaba

    def test_el_mismo_archivo_otra_vez_no_cambia_nada(self):
        nuevo = con_cantidad(self.pres, ZAFIRO, "EST-10010", "40")
        self.cargar(nuevo)
        cargas = len(self.repo.cargas())
        r = self.revisar(nuevo)
        self.assertEqual((self.estado(r).estado, r.plan.cambia_algo, r.diagnostico.cambios), ("sin_cambios", False, ()))
        self.assertIsNone(self.cargar(nuevo).carga_id)
        self.assertEqual(len(self.repo.cargas()), cargas)

    def test_volver_al_archivo_de_antes_deshace_la_cantidad_y_queda_en_la_historia(self):
        nuevo = con_cantidad(self.pres, ZAFIRO, "EST-10010", "40")
        self.cargar(nuevo)
        self.cargar(self.pres)
        self.assertEqual(self.total(), Decimal(CAPITULOS[ZAFIRO]))
        self.assertEqual([(h.campo, h.antes, h.despues) for h in self.repo.historia(self.renglon().id)], [("cantidad", "37", "40"), ("cantidad", "40", "37")])

    def test_de_dos_renglones_con_el_mismo_concepto_en_el_bloque_cambia_el_que_es(self):
        """Zafiro Plus nombra dos veces `ACA-02032` en el mismo bloque (2.65 y 1.8): el segundo del archivo es el segundo guardado."""
        plus = "CAS-00006"
        primero, segundo = self.renglon("ACA-02032", 1, plus), self.renglon("ACA-02032", 2, plus)
        self.assertEqual((primero.cantidad, segundo.cantidad), (Decimal("2.65"), Decimal("1.8")))
        r = self.revisar(con_cantidad(self.pres, plus, "ACA-02032", "9", n=2))
        (c,) = r.diagnostico.cambios
        self.assertTrue(c.id.endswith("::ACA-02032#2"), c.id)
        self.cargar(con_cantidad(self.pres, plus, "ACA-02032", "9", n=2))
        self.assertEqual((self.renglon("ACA-02032", 1, plus).cantidad, self.renglon("ACA-02032", 2, plus).cantidad), (Decimal("2.65"), Decimal("9")))
        self.assertEqual((self.repo.historia(primero.id), [h.campo for h in self.repo.historia(segundo.id)]), ([], ["cantidad"]))
        # y quitar el segundo deja el primero: la baja es de la segunda vez, no de la clave
        self.cargar(sin_renglon(self.pres, plus, "ACA-02032", n=2), bajas_confirmadas=[c.id])
        self.assertEqual([x.cantidad for x in self.carga.presupuesto(self.presupuesto(plus).id).renglones if x.clave == "ACA-02032"], [Decimal("2.65")])

    # ------------------------------------------------------------------ lo que entra
    def test_un_renglon_nuevo_entra_con_la_version_vigente_y_en_su_lugar(self):
        nuevo = con_copia(self.pres, ZAFIRO, "EST-10011", "EST-10011", cantidad="5")  # otra vez el K1 de 6.00, en el mismo bloque
        r = self.revisar(nuevo)
        (c,) = r.diagnostico.cambios
        self.assertEqual((c.tipo, c.clave, c.ahora, c.estado), ("alta", "EST-10011", Decimal("5"), "aplica"))
        seis = self.otros_seis()
        antes = self.carga.presupuesto(self.presupuesto().id)
        pu = next(x.pu for x in antes.renglones if x.clave == "EST-10011")
        res = self.cargar(nuevo)
        g = self.carga.presupuesto(self.presupuesto().id)
        self.assertEqual(g.total, antes.total + 5 * pu)
        de_esa_clave = [x for x in g.renglones if x.clave == "EST-10011"]
        self.assertEqual(([x.cantidad for x in de_esa_clave], {x.version for x in de_esa_clave}), ([Decimal("6"), Decimal("5")], {1}))  # fija la vigente
        self.assertEqual([x.wbs for x in de_esa_clave], ["1.1.1.1.3", "1.1.1.1.4"])  # justo después del que ya estaba
        self.assertEqual(next(x.clave for x in g.renglones if x.wbs == "1.1.1.1.5"), "EST-10020")  # y lo que seguía se corrió un lugar
        nuevo_renglon = self.renglon("EST-10011", 2)
        self.assertEqual([(h.carga_id, h.campo, h.despues) for h in self.repo.historia(nuevo_renglon.id)], [(res.carga_id, "alta", "5")])
        self.assertEqual(self.otros_seis(), seis)
        self.assertEqual(self.estado(self.revisar(nuevo)).estado, "sin_cambios")

    def test_un_bloque_nuevo_entra_entero_con_sus_renglones(self):
        nuevo = con_copia(self.pres, ZAFIRO, "EST-00010", "EST-01040")  # la losa de PB (Nivel 3), también en la cimentación
        r = self.revisar(nuevo)
        (c,) = r.diagnostico.cambios
        self.assertEqual((c.tipo, c.clave, c.es_bloque, c.estado), ("alta", "EST-00010", True, "aplica"))
        self.assertIn("renglones", c.detalle)
        antes = self.carga.presupuesto(self.presupuesto().id)
        self.cargar(nuevo)
        g = self.carga.presupuesto(self.presupuesto().id)
        self.assertEqual(len(g.renglones), len(antes.renglones) + 1 + int(c.detalle.split()[0]))
        original = next(x for x in antes.renglones if x.clave == "EST-00010")
        copia = [x for x in g.renglones if x.clave == "EST-00010"]
        self.assertEqual(len(copia), 2)
        self.assertEqual(g.total, antes.total + original.total)  # lo mismo que la original: los mismos renglones a los mismos PU
        self.assertEqual(self.estado(self.revisar(nuevo)).estado, "sin_cambios")

    # ------------------------------------------------------------------ lo que se va
    def test_una_baja_pide_confirmacion_y_hasta_entonces_el_renglon_sigue(self):
        sin = sin_renglon(self.pres, ZAFIRO, "EST-10010")
        r = self.revisar(sin)
        (c,) = r.diagnostico.cambios
        self.assertEqual((c.tipo, c.id, c.estado, c.motivo), ("baja", K1, "detenido", BAJA_SIN_CONFIRMAR))
        self.assertEqual(self.estado(r).estado, "parcial")
        self.assertIn((K1, BAJA_SIN_CONFIRMAR), [(p.clave, p.motivo) for p in r.diagnostico.pendientes])
        self.cargar(sin)  # queda dicho en la carga y no se aplica
        self.assertEqual(self.total(), Decimal(CAPITULOS[ZAFIRO]))
        self.assertEqual(self.renglon().cantidad, Decimal("37"))
        self.assertEqual(self.repo.historia(self.renglon().id), [])
        self.assertEqual(self.repo.cargas()[-1].resumen["pendientes"][0]["motivo"], BAJA_SIN_CONFIRMAR)

    def test_confirmada_la_baja_el_renglon_se_va_sin_borrarse(self):
        sin = sin_renglon(self.pres, ZAFIRO, "EST-10010")
        antes = self.renglon()
        renglones = self.presupuesto().renglones
        res = self.cargar(sin, bajas_confirmadas=[K1])
        self.assertEqual(self.total(), Decimal(CAPITULOS[ZAFIRO]) - 37 * PU_K1)
        self.assertEqual([x for x in self.carga.presupuesto(self.presupuesto().id).renglones if x.clave == "EST-10010"], [])
        self.assertEqual([(h.carga_id, h.campo, h.antes) for h in self.repo.historia(antes.id)], [(res.carga_id, "baja", "37")])
        self.assertEqual(self.presupuesto().renglones, renglones - 1)  # lo dado de baja no cuenta
        self.assertEqual(self.estado(self.revisar(sin)).estado, "sin_cambios")  # la baja confirmada deja el presupuesto igual al archivo
        # el motor de cálculo tampoco la cuenta
        arbol = self.repo.arbol()
        raiz = self.repo.datos_de_presupuesto(self.presupuesto().id).raiz_id
        self.assertAlmostEqual(float(precio_unitario(raiz, arbol)), float(Decimal(CAPITULOS[ZAFIRO]) - 37 * PU_K1), delta=0.5)

    def test_una_baja_confirmada_en_otra_carga_tambien_entra(self):
        sin = sin_renglon(self.pres, ZAFIRO, "EST-10010")
        self.cargar(sin)  # sin confirmar
        self.assertEqual(self.total(), Decimal(CAPITULOS[ZAFIRO]))
        self.cargar(sin, bajas_confirmadas=[K1])  # y después alguien la confirma
        self.assertEqual(self.total(), Decimal(CAPITULOS[ZAFIRO]) - 37 * PU_K1)

    def test_la_baja_de_un_bloque_se_lleva_lo_que_cuelga_de_el_con_una_sola_confirmacion(self):
        sin = sin_renglon(self.pres, ZAFIRO, "EST-01040")  # el Nivel 3 de la losa de cimentación, con sus 8 conceptos
        r = self.revisar(sin)
        (c,) = r.diagnostico.cambios
        self.assertEqual((c.id, c.es_bloque, c.estado), (BLOQUE, True, "detenido"))
        self.assertIn("se van", c.detalle)
        antes = self.carga.presupuesto(self.presupuesto().id)
        bloque = next(x for x in antes.renglones if x.clave == "EST-01040" and x.tipo == "Nivel 3")
        self.cargar(sin, bajas_confirmadas=[BLOQUE])
        g = self.carga.presupuesto(self.presupuesto().id)
        self.assertEqual(g.total, antes.total - bloque.total)
        self.assertNotIn("EST-01040", [x.clave for x in g.renglones])
        self.assertEqual(self.estado(self.revisar(sin)).estado, "sin_cambios")
        # lo que se quitó se puede volver a poner: su ruta quedó libre, y entra como lo que es, un bloque nuevo
        self.cargar(self.pres)
        h = self.carga.presupuesto(self.presupuesto().id)
        self.assertEqual((h.total, len(h.renglones)), (antes.total, len(antes.renglones)))

    def test_todas_las_bajas_se_confirman_juntas_si_se_pide(self):
        sin = sin_renglon(sin_renglon(self.pres, ZAFIRO, "EST-10010"), ZAFIRO, "EST-10011")
        r = self.revisar(sin)
        self.assertEqual(sorted(c.motivo for c in r.diagnostico.cambios), [BAJA_SIN_CONFIRMAR] * 2)
        self.cargar(sin, todas_las_bajas=True)
        self.assertEqual(self.estado(self.revisar(sin)).estado, "sin_cambios")
        self.assertLess(self.total(), Decimal(CAPITULOS[ZAFIRO]))

    # ------------------------------------------------------------------ el lugar entre los hermanos
    def test_dos_hermanos_que_cambian_de_lugar_se_reordenan_sin_cambiar_su_cantidad(self):
        nuevo = con_orden_cambiado(self.pres, ZAFIRO, "EST-10010", "EST-10011")
        a, b = self.renglon("EST-10010"), self.renglon("EST-10011")
        self.cargar(nuevo)
        g = self.carga.presupuesto(self.presupuesto().id)
        orden = [x.clave for x in g.renglones if x.clave in ("EST-10010", "EST-10011")]
        self.assertEqual(orden, ["EST-10011", "EST-10010"])
        self.assertEqual(g.total, Decimal(CAPITULOS[ZAFIRO]))
        self.assertEqual((self.renglon("EST-10010").id, self.renglon("EST-10011").id), (a.id, b.id))  # la identidad es la misma
        self.assertEqual([h.campo for h in self.repo.historia(a.id)], ["orden"])
        self.assertEqual(self.estado(self.revisar(nuevo)).estado, "sin_cambios")

    # ------------------------------------------------------------------ lo contratado no se toca
    def test_lo_contratado_no_se_reconcilia_y_lo_demas_si(self):
        ServicioContratacion(self.repo).contratar(ZAFIRO, CO, "luis@obra.mx", "CAS-00004#1/NIV-00001#1")
        fuera_n = self.renglon("EST-21011")  # la losa de PB: no está en la cimentación
        nuevo = con_cantidad(self.pres, ZAFIRO, "EST-10010", "40")  # dentro de lo contratado
        nuevo = con_cantidad(nuevo, ZAFIRO, "EST-21011", "2")  # fuera
        nuevo = sin_renglon(nuevo, ZAFIRO, "EST-10011")  # una baja dentro
        nuevo = con_copia(nuevo, ZAFIRO, "EST-10020", "EST-10020", cantidad="9")  # un renglón nuevo dentro
        r = self.revisar(nuevo, todas_las_bajas=True)
        por_motivo = sorted((c.tipo, c.estado, c.motivo) for c in r.diagnostico.cambios)
        self.assertEqual(por_motivo, [("alta", "detenido", EN_CONTRATADO), ("baja", "detenido", EN_CONTRATADO),
                                      ("cantidad", "aplica", ""), ("cantidad", "detenido", EN_CONTRATADO)])
        self.assertEqual(self.estado(r).estado, "parcial")
        antes_dentro = self.renglon("EST-10010")
        res = self.cargar(nuevo, todas_las_bajas=True)
        self.assertEqual(self.renglon("EST-10010").cantidad, antes_dentro.cantidad)  # lo contratado no cambió
        self.assertEqual(self.renglon("EST-10011").cantidad, Decimal("6"))
        self.assertEqual(len([x for x in self.carga.presupuesto(self.presupuesto().id).renglones if x.clave == "EST-10020"]), 1)
        self.assertEqual(self.renglon("EST-21011").cantidad, Decimal("2"))  # lo de fuera sí entró
        self.assertEqual(self.renglon("EST-21011").id, fuera_n.id)
        self.assertTrue(self.presupuesto().huella.startswith("parcial:"))  # lo guardado ya no es ninguno de los archivos
        self.assertEqual(sorted(p["motivo"] for p in self.repo.cargas()[-1].resumen["pendientes"]), [EN_CONTRATADO] * 3)
        # decirlo otra vez no cambia nada más: lo detenido sigue dicho
        r2 = self.revisar(nuevo, todas_las_bajas=True)
        self.assertEqual(sorted(c.estado for c in r2.diagnostico.cambios), ["detenido"] * 3)
        self.assertEqual(res.carga_id, len(self.repo.cargas()))  # y la carga que lo dijo es la última

    def test_quitar_un_bloque_que_contiene_algo_contratado_se_detiene(self):
        ServicioContratacion(self.repo).contratar(ZAFIRO, CO, "luis@obra.mx", "CAS-00004#1/NIV-00001#1/ECO-00001#1")
        sin = sin_renglon(self.pres, ZAFIRO, "NIV-00001")  # toda la cimentación, que contiene a un bloque contratado
        r = self.revisar(sin, todas_las_bajas=True)
        (c,) = r.diagnostico.cambios
        self.assertEqual((c.tipo, c.id, c.estado, c.motivo), ("baja", "CAS-00004#1/NIV-00001#1", "detenido", EN_CONTRATADO))
        self.cargar(sin, todas_las_bajas=True)
        self.assertEqual(self.total(), Decimal(CAPITULOS[ZAFIRO]))

    # ------------------------------------------------------------------ lo que depende de algo detenido
    def test_un_renglon_nuevo_cuyo_concepto_quedo_pendiente_espera(self):
        mov = reescalar_linea(self.con, "ACA-01010", 1, Decimal("2"))  # el PU de ACA-01010 se mueve 70 % y nadie lo confirma
        nuevo = con_copia(self.pres, ZAFIRO, "ACA-01010", "EST-10011", cantidad="3")
        r = self.revisar(nuevo, mov)
        (alta,) = [c for c in r.diagnostico.cambios if c.tipo == "alta"]
        self.assertEqual((alta.clave, alta.estado, alta.motivo), ("ACA-01010", "detenido", CONCEPTO_PENDIENTE))
        self.assertIn(PU_MOVIO, alta.detalle)
        usos = lambda: len([x for x in self.carga.presupuesto(self.presupuesto().id).renglones if x.clave == "ACA-01010"])
        antes = usos()
        self.cargar(nuevo, mov)
        self.assertEqual((usos(), self.total()), (antes, Decimal(CAPITULOS[ZAFIRO])))  # nada entró a medias
        # con el PU confirmado, el concepto entra y el renglón nuevo también
        self.cargar(nuevo, mov, confirmados=["ACA-01010"])
        self.assertEqual(usos(), antes + 1)
        self.assertGreater(self.total(), Decimal(CAPITULOS[ZAFIRO]))

    # ------------------------------------------------------------------ todo o nada, y el candado de siempre
    def test_una_reconciliacion_que_falla_a_medias_no_deja_nada(self):
        nuevo = con_copia(con_cantidad(self.pres, ZAFIRO, "EST-10010", "40"), ZAFIRO, "EST-10011", "EST-10011", cantidad="5")
        r = self.revisar(nuevo)
        (rec,) = r.plan.reconciliaciones
        mala = replace(rec, altas=tuple(replace(a, clave="ZZZ-99999") for a in rec.altas))  # la cantidad ya se habría cambiado cuando falla el alta
        cargas, antes = len(self.repo.cargas()), self.renglon()
        with self.assertRaises(KeyError):
            self.repo.aplicar(replace(r.plan, reconciliaciones=(mala,)))
        self.assertEqual((len(self.repo.cargas()), self.renglon(), self.total(), self.repo.historia(antes.id)), (cargas, antes, Decimal(CAPITULOS[ZAFIRO]), []))
        self.repo.aplicar(r.plan)  # y la buena sigue entrando
        self.assertEqual(self.renglon().cantidad, Decimal("40"))

    def test_otra_carga_en_medio_no_se_pisa_tampoco_al_reconciliar(self):
        nuevo = con_cantidad(self.pres, ZAFIRO, "EST-10010", "40")
        r = self.revisar(nuevo)
        self.cargar(con_cantidad(self.pres, ZAFIRO, "EST-10011", "7"))  # alguien reconcilió otra cosa entre una y otra
        from core.catalogo import CatalogoCambio

        with self.assertRaises(CatalogoCambio):
            self.repo.aplicar(r.plan)
        self.assertEqual(self.renglon().cantidad, Decimal("37"))
