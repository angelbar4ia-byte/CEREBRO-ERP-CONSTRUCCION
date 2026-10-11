"""
Lo que todo `RepositorioCatalogo` tiene que cumplir, con los archivos de verdad de `1-mundo/opus/`.

No es un módulo de pruebas por sí solo: `test_servicio_carga.py` lo corre contra el adaptador en memoria y
`infra/tests/test_postgres_catalogo.py`, contra Postgres. Si los dos pasan lo mismo, el servicio no depende de cuál se use.

Las pruebas parten de la primera carga completa —los siete presupuestos, 596 matrices, 612 insumos— y le tocan a una fila real
lo que cada una necesita: un precio, una cantidad, una unidad.
"""
import csv
from decimal import Decimal

from core.accesos import PermisoDenegado
from core.catalogo import (
    CatalogoCambio,
    DEPENDE_DE,
    PRECIO_DE_TRABAJO,
    PU_MOVIO,
    ServicioCarga,
    TEXTO_Y_RECETA,
    UNIDAD_CAMBIO,
)
from core.importacion_opus import CargaNoProcede, armar_arbol, huella, leer_matrices, leer_presupuesto
from core.motor_calculo import precio_unitario
from core.tests.datos_opus import (
    COMPUESTOS,
    CONCEPTOS,
    OPUS,
    PRESUPUESTO,
    cambiar_unidad_del_concepto,
    cambiar_unidad_del_hijo,
    columna,
    con_descripcion_del_concepto,
    con_descripcion_del_hijo,
    editar,
    reescalar_costo,
    reescalar_linea,
    sin_capitulo,
    texto,
)

USUARIO = "ana@obra.mx"
LOS_CUATRO_SIN_MATRIZ = ["ACC-00003", "IGAS-02131", "IGAS-02132", "ISN-02061"]
CAPITULOS = {"CAS-00004": "1842426.01", "CAS-00003": "2040945.97", "CAS-00006": "2175243.96", "CAS-00002": "2156131.02",
             "CAS-00005": "2800860.95", "CAS-00007": "2829925.98", "CAS-00001": "2615089.61"}


class ContratoCatalogo:
    """Mezclar con `unittest.TestCase` y definir `nuevo_repositorio()`."""

    def nuevo_repositorio(self):  # pragma: no cover
        raise NotImplementedError

    def setUp(self):
        self.repo = self.nuevo_repositorio()
        self.sv = ServicioCarga(self.repo)
        self.pres, self.con, self.comp = texto(PRESUPUESTO), texto(CONCEPTOS), texto(COMPUESTOS)
        self.m = leer_matrices(self.con, self.comp)
        self.lectura = leer_presupuesto(self.pres)

    def cargar(self, conceptos=None, presupuesto=None, compuestos=None, **kw):
        kw.setdefault("rol", "costos")
        return self.sv.aplicar(self.con if conceptos is None else conceptos, self.pres if presupuesto is None else presupuesto,
                               compuestos, usuario=USUARIO, **kw)

    def revisar(self, conceptos=None, presupuesto=None, compuestos=None, **kw):
        kw.setdefault("rol", "costos")
        return self.sv.revisar(self.con if conceptos is None else conceptos, self.pres if presupuesto is None else presupuesto,
                               compuestos, usuario=USUARIO, **kw)

    def base(self):
        return self.cargar(compuestos=self.comp)

    def pu(self, clave):
        return precio_unitario(self.repo.id_de(clave), self.repo.arbol())

    def presupuesto(self, clave_del_capitulo):
        resumen = next(p for p in self.repo.presupuestos() if p.clave == clave_del_capitulo)
        return self.sv.presupuesto(resumen.id)

    # ------------------------------------------------------------------ la primera carga
    def test_la_primera_carga_guarda_todo_lo_que_el_diagnostico_decia(self):
        r = self.revisar(compuestos=self.comp)
        self.assertTrue(r.diagnostico.aplicable, r.diagnostico.problemas)
        self.assertEqual((len(r.diagnostico.diagnostico.nuevos), r.diagnostico.insumos_nuevos, len(r.diagnostico.pendientes)), (596, 612, 0))
        res = self.base()
        e = self.repo.estado_vigente()
        self.assertEqual((len(e.huella), len(e.pu), len(e.insumos), sorted(e.sin_matriz), e.ultima_carga), (596, 596, 612, LOS_CUATRO_SIN_MATRIZ, res.carga_id))
        (carga,) = self.repo.cargas()
        self.assertEqual((carga.usuario, carga.rol), (USUARIO, "costos"))
        self.assertEqual(set(carga.archivos), {"CATALOGO_DE_PRESUPUESTO", "ANALISIS_DE_BASICOS_CONCEPTOS", "ANALISIS_DE_BASICOS_COMPUESTOS"})
        self.assertEqual((carga.resumen["nodos_nuevos"], carga.resumen["insumos_nuevos"], len(carga.resumen["presupuestos_nuevos"])), (596, 612, 7))

    def test_los_siete_presupuestos_se_leen_de_vuelta_renglon_por_renglon_como_el_archivo(self):
        self.base()
        with open(OPUS / f"{PRESUPUESTO}.csv", encoding="utf-8-sig", newline="") as fh:
            crudas = [r for r in csv.DictReader(fh) if any(v.strip() for v in r.values())]
        total = lambda s: Decimal(s.replace(",", ""))
        self.assertEqual({p.clave for p in self.repo.presupuestos()}, set(CAPITULOS))
        for cap in self.lectura.capitulos():
            g = self.presupuesto(cap.raiz.clave)
            self.assertEqual(g.total, Decimal(CAPITULOS[cap.raiz.clave]), cap.raiz.clave)
            self.assertEqual(len(g.renglones), len(cap.filas))
            for guardado, fila in zip(g.renglones, cap.filas):
                cruda = crudas[fila.posicion]
                wbs = "1" + fila.wbs[len(cap.raiz.wbs):]  # cada capítulo es un presupuesto, y su árbol empieza en 1
                esperado = (wbs, fila.tipo, fila.clave, fila.cantidad, total(cruda["Precio unitario"]), total(cruda["Total"]))
                self.assertEqual((guardado.wbs, guardado.tipo, guardado.clave, guardado.cantidad, guardado.pu, guardado.total), esperado,
                                 f"{cap.raiz.clave} línea {fila.linea}")

    def test_el_motor_sobre_lo_guardado_da_el_precio_de_cada_matriz_y_el_total_de_cada_presupuesto(self):
        self.base()
        arbol = self.repo.arbol()
        for clave, total in CAPITULOS.items():
            resumen = next(p for p in self.repo.presupuestos() if p.clave == clave)
            raiz = self.repo.datos_de_presupuesto(resumen.id).raiz_id
            self.assertEqual(precio_unitario(raiz, arbol), Decimal(total), clave)
        for clave in self.m.por_padre:  # los 596: lo que se congeló al cargar es lo que el motor calcula hoy
            self.assertEqual(self.repo.versiones(clave)[0].pu, precio_unitario(self.repo.id_de(clave), arbol), clave)

    def test_una_version_guarda_la_receta_con_su_orden_su_huella_y_su_pu(self):
        self.base()
        (v,) = self.repo.versiones("EST-01040")
        propias = self.m.por_padre["EST-01040"]
        self.assertEqual((v.version, [l.hijo for l in v.lineas], [l.cantidad for l in v.lineas], [l.orden for l in v.lineas]),
                         (1, [l.hijo for l in propias], [l.cantidad for l in propias], list(range(1, len(propias) + 1))))
        self.assertEqual(v.huella, huella([(l.hijo, l.cantidad) for l in propias]))
        self.assertEqual(v.pu, self.lectura.conceptos["EST-01040"][0].precio_observado)
        (cuad,) = self.repo.versiones("CUAD-001")
        self.assertEqual((cuad.pu, [l.porcentaje for l in cuad.lineas]), (Decimal("2068.00"), [False, False, True]))

    def test_el_alambre_dos_veces_y_las_cantidades_negativas_se_guardan_tal_cual(self):
        self.base()
        (aux,) = self.repo.versiones("AUX-00001")
        self.assertEqual([l.hijo for l in aux.lineas].count("ACE-00001"), 2)  # una línea por cada amarre: el par (padre, hijo) se repite
        negativas = sum(1 for clave in self.m.por_padre for l in self.repo.versiones(clave)[0].lineas if l.cantidad < 0)
        self.assertEqual(negativas, 58)

    def test_los_conceptos_sin_matriz_existen_sin_versiones_y_valen_cero(self):
        self.base()
        for clave in LOS_CUATRO_SIN_MATRIZ:
            self.assertEqual(self.repo.versiones(clave), [])
        for cap in self.lectura.capitulos():
            for r in self.presupuesto(cap.raiz.clave).renglones:
                if r.clave in LOS_CUATRO_SIN_MATRIZ:
                    self.assertEqual((r.version, r.pu, r.total), (None, Decimal("0"), Decimal("0")))

    def test_un_insumo_tiene_su_historia_de_precio_y_el_porcentaje_no_tiene_precio(self):
        self.base()
        (p,) = self.repo.precios("ACE-00001")
        self.assertEqual((p.precio, p.vigente_hasta), (Decimal("24.68"), None))
        self.assertEqual(self.repo.precios("MOCA-110"), [])  # su «costo» en cada línea es la base de jornales de su cuadrilla
        self.assertEqual(self.repo.estado_vigente().insumos["ACE-00001"].precio, Decimal("24.68"))

    def test_las_unidades_se_guardan_como_vienen_y_la_que_no_se_sabe_queda_vacia(self):
        self.base()
        e = self.repo.estado_vigente()
        self.assertEqual((e.insumos["ACR-00001"].unidad, e.unidad["EST-01040"]), ("PZ", self.lectura.unidad_de("EST-01040")))
        self.assertNotEqual(self.lectura.unidad_de("EST-01040").lower(), "pz")  # «PZ» de los insumos y «pza» de los conceptos: no se juntan, no se sabe
        sin = sorted(c for c, u in e.unidad.items() if u == "")
        self.assertEqual(len(sin), 40)  # las 39 cuadrillas y el concepto que ningún prototipo usa
        self.assertIn("CUAD-001", sin)
        self.assertIn("ACA-01070", sin)

    # ------------------------------------------------------------------ volver a cargar
    def test_cargar_lo_mismo_otra_vez_no_cambia_nada(self):
        self.base()
        antes = self.repo.estado_vigente()
        r = self.revisar(compuestos=self.comp)
        self.assertEqual((len(r.diagnostico.diagnostico.entran), r.diagnostico.pendientes), (596, ()))
        self.assertEqual({e.estado for e in r.diagnostico.presupuestos}, {"sin_cambios"})
        self.assertFalse(r.plan.cambia_algo)
        self.assertIsNone(self.cargar(compuestos=self.comp).carga_id)
        self.assertEqual((len(self.repo.cargas()), self.repo.estado_vigente()), (1, antes))

    def test_un_precio_que_se_mueve_es_historia_y_no_versiona_nada(self):
        self.base()
        antes = self.pu("AUX-00001")
        nuevo = reescalar_costo(self.con, "ACE-00001", Decimal("1.2"))
        r = self.revisar(nuevo)
        self.assertEqual(r.diagnostico.precios_que_cambian, (("ACE-00001", Decimal("24.68"), Decimal("29.62")),))
        self.assertEqual((r.diagnostico.diagnostico.versionan, r.diagnostico.pendientes), ((), ()))
        self.cargar(nuevo)
        cerrado, vigente = self.repo.precios("ACE-00001")
        self.assertEqual((cerrado.precio, vigente.precio, vigente.vigente_hasta), (Decimal("24.68"), Decimal("29.62"), None))
        self.assertEqual(cerrado.vigente_hasta, vigente.vigente_desde)  # una historia sin huecos ni empalmes
        self.assertEqual(self.repo.estado_vigente().insumos["ACE-00001"].precio, Decimal("29.62"))
        # la receta sigue siendo la misma versión y su PU de ese día no se recalcula; el motor, con el precio de hoy, sí lo ve
        self.assertEqual(len(self.repo.versiones("AUX-00001")), 1)
        self.assertEqual(self.repo.versiones("AUX-00001")[0].pu, antes)
        self.assertGreater(self.pu("AUX-00001"), antes)

    def test_cambiar_una_cantidad_versiona_ese_concepto_y_deja_la_anterior_intacta(self):
        self.base()
        v1 = self.repo.versiones("ACA-01010")[0]
        arriba = self.presupuesto("CAS-00004").total
        nuevo = reescalar_linea(self.con, "ACA-01010", 0, Decimal("1.1"))  # un 10 % más de mortero: el PU se mueve poco
        r = self.revisar(nuevo)
        self.assertEqual((r.diagnostico.diagnostico.versionan, r.diagnostico.pendientes), (("ACA-01010",), ()))
        self.cargar(nuevo)
        viejo, vigente = self.repo.versiones("ACA-01010")
        self.assertEqual(viejo, v1)  # la 1 ni se enteró
        self.assertEqual((vigente.version, vigente.carga_id), (2, 2))
        self.assertNotEqual(vigente.huella, v1.huella)
        self.assertGreater(vigente.pu, v1.pu)
        self.assertEqual(vigente.lineas[0].cantidad, v1.lineas[0].cantidad * Decimal("1.1"))
        self.assertEqual(self.pu("ACA-01010"), vigente.pu)  # el motor lee la vigente
        # los presupuestos que lo usan siguen apuntando a la versión que fijaron
        self.assertEqual(self.presupuesto("CAS-00004").total, arriba)
        self.assertEqual({r.version for p in self.repo.presupuestos() for r in self.sv.presupuesto(p.id).renglones if r.clave == "ACA-01010"}, {1})

    def test_la_misma_receta_en_otro_orden_o_con_otro_texto_no_versiona(self):
        self.base()

        def retocar(filas):
            p, d = columna(filas, "Clave Padre"), columna(filas, "Descripción")
            mias = [i for i, f in enumerate(filas) if i and f[p] == "ACA-01010"]
            filas[mias[0]], filas[mias[1]] = filas[mias[1]], filas[mias[0]]
            filas[mias[0]][d] += " (corregido)"

        r = self.revisar(editar(self.con, retocar))
        self.assertEqual((r.diagnostico.diagnostico.versionan, r.plan.versiones_nuevas, r.plan.nodos_nuevos), ((), (), ()))
        # el texto sí se dice, como informativo (§2.7.1: «corregido» es una anotación, no un cambio de qué se trata)
        self.assertEqual([(a.nivel, a.estado) for a in r.diagnostico.alertas_de_texto], [("informativa", "carga")])

    def test_un_cambio_de_mas_de_5_por_ciento_pide_confirmacion_y_lo_demas_entra(self):
        self.base()
        grande = reescalar_linea(self.con, "ACA-01010", 1, Decimal("2"))  # la mano de obra al doble: el PU se mueve 70 %
        nuevo = reescalar_linea(grande, "ACA-01020", 0, Decimal("1.1"))  # y otro concepto que cambia poco
        r = self.revisar(nuevo)
        self.assertEqual([(p.clave, p.motivo) for p in r.diagnostico.pendientes], [("ACA-01010", PU_MOVIO)])
        self.assertEqual({v.clave for v in r.plan.versiones_nuevas}, {"ACA-01020"})
        self.cargar(nuevo)
        self.assertEqual((len(self.repo.versiones("ACA-01010")), len(self.repo.versiones("ACA-01020"))), (1, 2))
        # nadie confirmó: queda dicho en la carga, para que no sea un pendiente que nadie sabe que tiene
        self.assertEqual([(p["clave"], p["motivo"]) for p in self.repo.cargas()[-1].resumen["pendientes"]], [("ACA-01010", PU_MOVIO)])
        # y con la confirmación, entra
        self.cargar(nuevo, confirmados=["ACA-01010"])
        self.assertEqual(len(self.repo.versiones("ACA-01010")), 2)
        self.assertEqual(self.repo.versiones("ACA-01010")[1].pu, self.pu("ACA-01010"))

    def test_lo_que_depende_de_algo_detenido_tambien_se_detiene_y_lo_que_no_cambia_sigue_igual(self):
        self.base()
        citan = [c for c in self.m.padres_de_origen("Concepto")
                 if c in self.lectura.conceptos and any(l.hijo == "AUX-00001" for l in self.m.por_padre[c])]
        b, b2 = citan[0], citan[1]
        nuevo = reescalar_linea(self.con, "AUX-00001", 0, Decimal("3"))  # el compuesto se mueve mucho
        nuevo = reescalar_linea(nuevo, b, 0, Decimal("1.01"))  # b cambia su propia receta; b2 no
        r = self.revisar(nuevo)
        motivos = {p.clave: p.motivo for p in r.diagnostico.pendientes}
        self.assertEqual(motivos, {"AUX-00001": PU_MOVIO, b: DEPENDE_DE})
        self.assertIn(b2, r.diagnostico.diagnostico.entran)
        self.cargar(nuevo)
        self.assertEqual([len(self.repo.versiones(c)) for c in ("AUX-00001", b, b2)], [1, 1, 1])

    def test_un_cambio_de_unidad_detiene_ese_concepto_y_el_resto_entra_normal(self):
        self.base()
        antes = self.repo.estado_vigente().unidad["EST-01040"]
        r = self.revisar(presupuesto=cambiar_unidad_del_concepto(self.pres, "EST-01040", "ml"))
        (d,) = r.diagnostico.diagnostico.detenidos
        self.assertEqual((d.clave, d.unidad_vigente, d.unidad_nueva), ("EST-01040", antes, "ml"))
        self.assertEqual([(p.clave, p.motivo) for p in r.diagnostico.pendientes], [("EST-01040", UNIDAD_CAMBIO)])
        self.assertEqual(len(r.diagnostico.diagnostico.entran), 595)
        self.cargar(presupuesto=cambiar_unidad_del_concepto(self.pres, "EST-01040", "ml"))
        self.assertEqual(self.repo.estado_vigente().unidad["EST-01040"], antes)  # nada la cambió

    def test_la_unidad_de_un_insumo_que_cambia_tambien_se_detiene(self):
        self.base()
        r = self.revisar(cambiar_unidad_del_hijo(self.con, "ACE-00001", "TON"))
        self.assertEqual([(p.clave, p.motivo) for p in r.diagnostico.pendientes], [("ACE-00001", UNIDAD_CAMBIO)])

    def test_el_precio_de_un_trabajo_que_cambia_se_valida_y_no_se_aplica(self):
        self.base()
        nuevo = reescalar_costo(reescalar_costo(self.con, "MOA-00112", Decimal("1.5")), "ACE-00001", Decimal("1.1"))
        r = self.revisar(nuevo)
        self.assertEqual([(p.clave, p.motivo) for p in r.diagnostico.pendientes], [("MOA-00112", PRECIO_DE_TRABAJO)])
        self.assertEqual([c for c, _, _ in r.diagnostico.precios_que_cambian], ["ACE-00001"])  # el material sí entra solo
        self.cargar(nuevo)
        self.assertEqual(len(self.repo.precios("MOA-00112")), 1)
        self.assertEqual(len(self.repo.precios("ACE-00001")), 2)

    def test_un_concepto_nuevo_con_su_matriz_entra_con_el_pu_del_motor(self):
        self.base()

        def agregar(filas):
            filas.append(["ZZZ-00001", "ACE-00001", "ALAMBRE RECOCIDO", "KG", "2.000000", "$24.68", "$49.36", "Material", "Concepto"])
            filas.append(["ZZZ-00001", "MOA-00112", "MO FINAS INTERIORES EN MUROS 0-3.00 MTS", "M2", "1.000000", "$50.00", "$50.00", "Contrato", "Concepto"])

        nuevo = editar(self.con, agregar)
        r = self.revisar(nuevo)
        self.assertEqual((r.diagnostico.diagnostico.nuevos, "ZZZ-00001" in r.diagnostico.sin_unidad), (("ZZZ-00001",), True))
        self.cargar(nuevo)
        (v,) = self.repo.versiones("ZZZ-00001")
        self.assertEqual((v.pu, [l.hijo for l in v.lineas]), (Decimal("99.36"), ["ACE-00001", "MOA-00112"]))
        self.assertEqual(self.repo.estado_vigente().unidad["ZZZ-00001"], "")  # no cuelga de ningún presupuesto: no se sabe su unidad

    # ------------------------------------------------------------------ los presupuestos que ya existen y los que llegan
    def test_un_presupuesto_que_ya_existe_se_reconcilia_y_los_demas_siguen_igual(self):
        """Lo que antes no se aplicaba (D-473) ahora se reconcilia (D-476); los casos están en `contrato_reconciliacion.py`."""
        self.base()
        total = self.presupuesto("CAS-00004").total

        def mas_de_algo(filas):
            c, t = columna(filas, "Cantidad"), columna(filas, "Tipo")
            fila = next(f for f in filas[1:] if f[t] == "Concepto")
            fila[c] = "99"

        r = self.revisar(presupuesto=editar(self.pres, mas_de_algo))
        estados = {e.clave: e.estado for e in r.diagnostico.presupuestos}
        self.assertEqual(estados["CAS-00004"], "reconciliado")
        self.assertEqual({e for c, e in estados.items() if c != "CAS-00004"}, {"sin_cambios"})
        self.assertEqual(self.presupuesto("CAS-00004").total, total)  # revisar no escribe
        self.assertIsNotNone(self.cargar(presupuesto=editar(self.pres, mas_de_algo)).carga_id)
        self.assertGreater(self.presupuesto("CAS-00004").total, total)
        self.assertEqual(len(self.repo.cargas()), 2)

    def test_un_presupuesto_nuevo_cuelga_de_lo_que_ya_hay(self):
        self.cargar(presupuesto=sin_capitulo(self.pres, "CAS-00001"), compuestos=self.comp)
        self.assertEqual(len(self.repo.presupuestos()), 6)
        r = self.revisar(compuestos=self.comp)
        self.assertEqual({e.clave: e.estado for e in r.diagnostico.presupuestos}["CAS-00001"], "nuevo")
        self.cargar(compuestos=self.comp)
        g = self.presupuesto("CAS-00001")
        self.assertEqual((len(self.repo.presupuestos()), g.total), (7, Decimal(CAPITULOS["CAS-00001"])))
        capitulo = next(c for c in self.lectura.capitulos() if c.raiz.clave == "CAS-00001")
        usados = {f.clave for f in capitulo.filas if f.es_concepto and f.clave in self.m.por_padre}
        self.assertEqual({r.version for r in g.renglones if r.clave in usados}, {1})  # fijó las versiones que ya estaban

    def test_saber_la_unidad_que_no_se_sabia_la_llena_y_no_versiona_nada(self):
        capitulos = self.lectura.capitulos()
        oro = next(c for c in capitulos if c.raiz.clave == "CAS-00001")
        otros = {f.clave for c in capitulos if c.raiz.clave != "CAS-00001" for f in c.filas if f.es_concepto}
        solo_oro = sorted({f.clave for f in oro.filas if f.es_concepto and f.clave in self.m.por_padre and f.clave not in otros})
        self.assertTrue(solo_oro)
        self.cargar(presupuesto=sin_capitulo(self.pres, "CAS-00001"))
        self.assertEqual({self.repo.estado_vigente().unidad[c] for c in solo_oro}, {""})  # ningún prototipo cargado los usa
        r = self.revisar()
        self.assertEqual((r.diagnostico.diagnostico.versionan, r.diagnostico.pendientes), ((), ()))
        self.cargar()
        e = self.repo.estado_vigente()
        self.assertTrue(all(e.unidad[c] for c in solo_oro))  # ya se sabe cuál es
        self.assertEqual({len(self.repo.versiones(c)) for c in solo_oro}, {1})  # y saberlo no cambió su receta

    def test_un_presupuesto_cuyo_concepto_quedo_pendiente_espera(self):
        self.cargar(presupuesto=sin_capitulo(self.pres, "CAS-00004"))
        capitulo = next(c for c in self.lectura.capitulos() if c.raiz.clave == "CAS-00004")
        c = next(f.clave for f in capitulo.filas if f.es_concepto and f.clave in self.m.por_padre)
        nuevo = reescalar_linea(self.con, c, 0, Decimal("100"))  # su PU se mueve mucho y nadie lo confirma
        r = self.revisar(nuevo)
        self.assertIn((c, PU_MOVIO), [(p.clave, p.motivo) for p in r.diagnostico.pendientes])
        self.assertEqual({e.clave: e.estado for e in r.diagnostico.presupuestos}["CAS-00004"], "pendiente")
        self.cargar(nuevo)
        self.assertEqual(len(self.repo.presupuestos()), 6)  # no se cargó a medias

    # ------------------------------------------------------------------ las garantías de la carga
    def test_otra_carga_en_medio_no_se_pisa(self):
        self.base()
        a = self.revisar(reescalar_costo(self.con, "ACE-00001", Decimal("1.2")))
        self.cargar(reescalar_costo(self.con, "ACE-00001", Decimal("1.3")))  # alguien más cargó mientras se decidía
        with self.assertRaises(CatalogoCambio):
            self.repo.aplicar(a.plan)
        self.assertEqual(len(self.repo.precios("ACE-00001")), 2)  # y la que se rechazó no dejó nada

    def test_sin_el_permiso_no_se_revisa_ni_se_aplica(self):
        for rol in ("residente", "cotizador"):
            with self.assertRaises(PermisoDenegado):
                self.revisar(rol=rol)
            with self.assertRaises(PermisoDenegado):
                self.cargar(rol=rol)
        self.assertEqual(self.repo.cargas(), [])
        self.assertEqual(self.cargar(rol="control_de_obra").carga_id, 1)  # Control de obra y Costos sí

    def test_lo_que_no_cuadra_en_el_archivo_no_se_carga_a_medias(self):
        def con_total(filas):
            c, t, k, d = (columna(filas, n) for n in ("Total", "Tipo", "Clave", "Descripción"))
            fila = next(f for f in filas[1:] if f[t] == "Nivel 3" and not f[k] and not f[d])
            fila[c] = "1,000.00"

        with self.assertRaises(CargaNoProcede):
            self.cargar(presupuesto=editar(self.pres, con_total))
        self.assertEqual((self.repo.cargas(), self.repo.presupuestos()), ([], []))
        with self.assertRaises(ValueError):
            self.sv.revisar(self.con, self.pres, rol="costos", usuario="")  # toda carga dice quién la hizo
        with self.assertRaises(ValueError):
            self.revisar(tipo="prototipo")

    def test_una_carga_solo_con_pendientes_queda_registrada(self):
        self.base()
        nuevo = reescalar_linea(self.con, "ACA-01010", 1, Decimal("2"))
        r = self.revisar(nuevo)
        self.assertFalse(r.plan.cambia_algo)
        res = self.cargar(nuevo)
        self.assertEqual(res.carga_id, 2)
        self.assertEqual(self.repo.cargas()[-1].resumen["pendientes"][0]["motivo"], PU_MOVIO)
        self.assertEqual(len(self.repo.versiones("ACA-01010")), 1)

    # ------------------------------------------------------------------ el texto que cambia (§2.7.1, D-477)
    K1 = "EST-10010"

    def alertas(self, r):
        return {a.clave: a for a in r.diagnostico.alertas_de_texto}

    def test_un_cambio_cosmetico_de_texto_ni_alerta_ni_escribe(self):
        self.base()
        r = self.revisar(presupuesto=con_descripcion_del_concepto(self.pres, self.K1, str.lower))
        self.assertEqual((r.diagnostico.alertas_de_texto, r.plan.cambia_algo, r.plan.descripciones), ((), False, ()))
        self.assertIsNone(self.cargar(presupuesto=con_descripcion_del_concepto(self.pres, self.K1, str.upper)).carga_id)

    def test_el_orden_de_las_palabras_o_un_calificativo_solo_informa_y_el_texto_entra(self):
        self.base()
        antes = self.repo.estado_vigente().descripcion[self.K1]
        nuevo = con_descripcion_del_concepto(self.pres, self.K1, lambda d: "Nuevo. " + d)
        r = self.revisar(presupuesto=nuevo)
        a = self.alertas(r)[self.K1]
        self.assertEqual((a.nivel, a.motivo, a.estado), ("informativa", "calificativo", "carga"))
        self.cargar(presupuesto=nuevo)
        self.assertEqual(self.repo.estado_vigente().descripcion[self.K1], "Nuevo. " + antes)
        self.assertEqual(len(self.repo.versiones(self.K1)), 1)  # el texto no versiona nada
        self.assertEqual(self.repo.cargas()[-1].resumen["alertas_de_texto"][0]["antes"], antes)  # y el de antes queda en la carga

    def test_un_numero_que_cambia_es_alta_y_carga_si_la_receta_es_la_misma(self):
        self.base()
        nuevo = con_descripcion_del_concepto(self.pres, self.K1, lambda d: d.replace("4.00", "5.00"))
        r = self.revisar(presupuesto=nuevo)
        a = self.alertas(r)[self.K1]
        self.assertEqual((a.nivel, a.motivo, a.detalle, a.estado), ("alta", "numero", "4 → 5", "carga"))
        self.assertEqual(r.diagnostico.pendientes, ())
        self.cargar(presupuesto=nuevo)
        self.assertIn("5.00", self.repo.estado_vigente().descripcion[self.K1])
        self.assertEqual(self.estado_de_texto(self.revisar(presupuesto=nuevo)), ())  # y ya no vuelve a alertar

    def estado_de_texto(self, r):
        return r.diagnostico.alertas_de_texto

    def test_el_texto_que_cambia_de_verdad_junto_con_la_receta_es_otro_concepto(self):
        self.base()
        antes = self.repo.estado_vigente().descripcion[self.K1]
        pres = con_descripcion_del_concepto(self.pres, self.K1, lambda d: d.replace("4.00", "5.00"))
        con = reescalar_linea(self.con, self.K1, 0, Decimal("1.01"))  # y la receta también: el PU se mueve poco
        r = self.revisar(con, pres)
        a = self.alertas(r)[self.K1]
        self.assertEqual((a.estado, a.nivel), ("detenido", "alta"))
        self.assertNotIn(a.clave_propuesta, self.repo.estado_vigente().unidad)  # la clave que se propone está libre
        self.assertTrue(a.clave_propuesta.startswith("EST-"), a.clave_propuesta)
        self.assertEqual([(p.clave, p.motivo) for p in r.diagnostico.pendientes], [(self.K1, TEXTO_Y_RECETA)])
        self.assertEqual(r.diagnostico.diagnostico.versionan, (self.K1,))
        self.cargar(con, pres)
        self.assertEqual((len(self.repo.versiones(self.K1)), self.repo.estado_vigente().descripcion[self.K1]), (1, antes))  # nada entró
        # quien decide dice que es el mismo concepto: entra como versión y el texto con ella
        self.cargar(con, pres, confirmados=[self.K1])
        self.assertEqual(len(self.repo.versiones(self.K1)), 2)
        self.assertIn("5.00", self.repo.estado_vigente().descripcion[self.K1])

    def test_lo_que_contiene_un_compuesto_detenido_por_texto_tambien_espera_si_cambia(self):
        self.base()
        aux, usa = "AUX-00001", "EST-21011"
        nuevo_texto = con_descripcion_del_hijo(self.con, aux, lambda d: d.replace("15x25", "15x30"))
        con = reescalar_linea(reescalar_linea(nuevo_texto, aux, 0, Decimal("1.01")), usa, 0, Decimal("1.01"))  # la trabe cambia, y el concepto que la lleva
        r = self.revisar(con)
        self.assertEqual(self.alertas(r)[aux].estado, "detenido")
        self.assertEqual([(p.clave, p.motivo) for p in r.diagnostico.pendientes], [(aux, TEXTO_Y_RECETA), (usa, DEPENDE_DE)])
        self.cargar(con)
        self.assertEqual({len(self.repo.versiones(c)) for c in (aux, usa)}, {1})
        # los que la llevan y no cambian de receta no esperan nada: su PU está congelado en su versión
        solo_la_trabe = self.revisar(nuevo_texto)
        self.assertEqual([p.motivo for p in solo_la_trabe.diagnostico.pendientes], [])

    def test_el_texto_de_un_insumo_alerta_y_entra_porque_no_tiene_receta_que_cruzar(self):
        self.base()
        nuevo = con_descripcion_del_hijo(self.con, "ACE-00001", lambda d: d + " CAL. 16")
        r = self.revisar(nuevo)
        a = self.alertas(r)["ACE-00001"]
        self.assertEqual((a.nivel, a.estado), ("alta", "carga"))
        self.cargar(nuevo)
        self.assertEqual(self.repo.estado_vigente().descripcion["ACE-00001"], "ALAMBRE RECOCIDO CAL. 16")

    def test_lo_que_se_detiene_por_otra_razon_no_cambia_de_texto(self):
        self.base()
        grande = reescalar_linea(self.con, "ACA-01010", 1, Decimal("2"))  # el PU se mueve 70 %: pide confirmación
        nuevo = con_descripcion_del_concepto(self.pres, "ACA-01010", lambda d: d.replace("3.00", "2.40"))
        antes = self.repo.estado_vigente().descripcion["ACA-01010"]
        r = self.revisar(grande, nuevo)
        self.assertEqual(self.alertas(r)["ACA-01010"].estado, "detenido")
        self.cargar(grande, nuevo)
        self.assertEqual(self.repo.estado_vigente().descripcion["ACA-01010"], antes)
