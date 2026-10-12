"""
Clonar un insumo y sustituir el original (D-478, P-11): el contrato que cumplen los adaptadores del catálogo, con los tres archivos de
OPUS de verdad y los siete presupuestos de verdad. Mezclar con `unittest.TestCase` y definir `nuevo_repositorio()`.

`AUX-00001` —la trabe T-3 de 15x25— es el caso de todos los días: un compuesto de material que OPUS llama `AUX-` y que citan nueve
conceptos de estructura (`EST-21011`…). Las 79 claves `AUX-` son lo que se corrige de una vez.
"""
from dataclasses import replace
from decimal import Decimal

from core.accesos import PermisoDenegado
from core.catalogo import CatalogoCambio, ServicioCarga
from core.clonacion import (
    ClonacionNoProcede,
    ServicioClonacion,
    informe_de_clonacion,
    informe_de_correccion,
    informe_de_resultado,
)
from core.contratacion import ServicioContratacion
from core.motor_calculo import precio_unitario
from core.tests.contrato_catalogo import CAPITULOS, USUARIO
from core.tests.datos_opus import COMPUESTOS, CONCEPTOS, PRESUPUESTO, con_copia, con_otra_clave, reescalar_costo, reescalar_linea, texto

QUIEN = "luis@obra.mx"
CO = "control_de_obra"
TRABE = "AUX-00001"
LOS_NUEVE = ["EST-21011", "EST-21031", "EST-22010", "EST-22210", "EST-30012", "EST-30013", "EST-30040", "EST-30041", "EST-52010"]
ZAFIRO = "CAS-00004"
LA_DE_LA_TRABE_EN_ZAFIRO = "CAS-00004#1/NIV-00002#1/ECO-00061#1/EST-00010#1"  # el bloque donde está EST-21011
UNA_CINTA = "COM-00058"  # un insumo con precio que cita un solo compuesto, con tres renglones de presupuesto detrás


class ContratoClonacion:
    def nuevo_repositorio(self):  # pragma: no cover
        raise NotImplementedError

    def setUp(self):
        self.repo = self.nuevo_repositorio()
        self.carga = ServicioCarga(self.repo)
        self.pres, self.con, self.comp = texto(PRESUPUESTO), texto(CONCEPTOS), texto(COMPUESTOS)
        self.carga.aplicar(self.con, self.pres, self.comp, rol="costos", usuario=USUARIO)
        self.sc = ServicioClonacion(self.repo)

    # ------------------------------------------------------------------ ayudas
    def totales(self):
        return {p.clave: self.carga.presupuesto(p.id).total for p in self.repo.presupuestos()}

    def pu_del_motor(self, clave):
        return precio_unitario(self.repo.id_de(clave), self.repo.arbol())

    def versiones_de_renglones(self, clave):
        """La versión que fija cada renglón de ese concepto, en los siete presupuestos."""
        return sorted(r.version for p in self.repo.presupuestos() for r in self.carga.presupuesto(p.id).renglones if r.clave == clave)

    def sustituir(self, original=TRABE, clave="PRE-00120"):
        return self.sc.clonar(original, clave, "sustituir", CO, QUIEN)

    def revisar_los_archivos(self):
        return self.carga.revisar(self.con, self.pres, self.comp, rol="costos", usuario=USUARIO)

    # ------------------------------------------------------------------ los compuestos de material son materiales
    def test_las_79_claves_aux_son_materiales_y_no_auxiliares(self):
        claves = sorted(k for k in self.repo.estado_vigente().descripcion if k.startswith("AUX-"))
        self.assertEqual(len(claves), 79)
        for k in claves:
            n = self.repo.nodo(k)
            self.assertEqual((n.categoria, n.rol, n.con_matriz), ("material", "insumo", True), k)

    # ------------------------------------------------------------------ clonar y sustituir un compuesto
    def test_proponer_dice_a_quien_cita_y_no_escribe(self):
        antes = self.repo.cargas()
        p = self.sc.proponer(TRABE, "PRE-00120", "sustituir", CO, QUIEN)
        self.assertTrue(p.aplicable)
        self.assertEqual(sorted(r.clave for r in p.redirigidos), LOS_NUEVE)
        self.assertEqual(p.renglones, 9)
        self.assertTrue(all((r.version_antes, r.version_despues) == (1, 2) for r in p.redirigidos))
        self.assertEqual(p.tipo, "compuesto")
        t = informe_de_clonacion(p)
        self.assertIn("Clonar y sustituir — AUX-00001 → PRE-00120", t)
        self.assertIn("EST-21011", t)
        self.assertIn("la clave vieja sigue entrando", t.replace("\n  ", " ").replace("La clave", "la clave"))
        self.assertEqual(self.repo.cargas(), antes)
        with self.assertRaises(KeyError):
            self.repo.nodo("PRE-00120")

    def test_sustituir_una_trabe_crea_el_clon_y_redirige_a_los_nueve_sin_mover_un_centavo(self):
        totales = self.totales()
        self.assertEqual(totales, {k: Decimal(v) for k, v in CAPITULOS.items()})
        vieja = self.repo.versiones(TRABE)[0]
        p, r = self.sustituir()
        self.assertEqual((r.versiones_nuevas, r.renglones_fijados), (9, 9))

        # el clon: lo mismo que el original, con su procedencia
        n, o = self.repo.nodo("PRE-00120"), self.repo.nodo(TRABE)
        self.assertEqual((n.descripcion, n.unidad, n.rol, n.categoria, n.con_matriz), (o.descripcion, o.unidad, o.rol, o.categoria, True))
        self.assertEqual((n.procedencia, o.procedencia), ("clonacion", "importado"))
        (v,) = self.repo.versiones("PRE-00120")
        self.assertEqual((v.version, v.huella, v.pu, v.lineas), (1, vieja.huella, vieja.pu, vieja.lineas))
        self.assertEqual(v.carga_id, r.carga_id)
        self.assertEqual(self.pu_del_motor("PRE-00120"), self.pu_del_motor(TRABE))
        self.assertEqual(len(self.repo.versiones(TRABE)), 1)  # el original no se toca

        # los nueve: versión nueva con la misma receta y el clon en lugar del original, el mismo PU
        for clave in LOS_NUEVE:
            v1, v2 = self.repo.versiones(clave)
            self.assertEqual((v2.version, v2.pu, v2.carga_id), (2, v1.pu, r.carga_id), clave)
            self.assertNotEqual(v2.huella, v1.huella, clave)
            self.assertEqual([("PRE-00120" if l.hijo == TRABE else l.hijo, l.cantidad, l.orden, l.reporta_a, l.porcentaje) for l in v1.lineas],
                             [(l.hijo, l.cantidad, l.orden, l.reporta_a, l.porcentaje) for l in v2.lineas], clave)
            self.assertEqual(self.pu_del_motor(clave), v2.pu, clave)
            self.assertEqual(set(self.versiones_de_renglones(clave)), {2}, clave)  # sus renglones fijan la nueva

        # nada se movió
        self.assertEqual(self.totales(), totales)
        self.assertEqual(self.repo.estado_vigente().homologaciones, {TRABE: "PRE-00120"})

        # la clonación queda dicha: quién, con qué rol, qué se redirigió
        carga = self.repo.cargas()[-1]
        self.assertEqual((carga.tipo, carga.usuario, carga.rol, carga.id), ("clonacion", QUIEN, CO, r.carga_id))
        (c,) = self.repo.clones()
        self.assertEqual((c.original, c.clon, c.modo, c.reconoce_clave_vieja_al_importar, c.exporta_clave_vieja, c.carga_id),
                         (TRABE, "PRE-00120", "sustituir", True, True, r.carga_id))
        self.assertEqual(sorted(x["clave"] for x in c.resumen["redirigidos"]), LOS_NUEVE)

    def test_el_archivo_de_siempre_se_lee_como_el_clon_y_no_cambia_nada(self):
        self.sustituir()
        rev = self.revisar_los_archivos()
        g = rev.diagnostico.diagnostico
        self.assertEqual((g.nuevos, g.versionan, g.detenidos, g.ausentes), ((), (), (), ()))
        self.assertFalse(rev.plan.cambia_algo)
        self.assertEqual(rev.diagnostico.pendientes, ())
        self.assertEqual(rev.diagnostico.alertas_de_texto, ())
        self.assertTrue(any("1 claves del archivo" in a and "AUX-00001 → PRE-00120" in a for a in rev.diagnostico.avisos), rev.diagnostico.avisos)
        antes = self.repo.cargas()
        self.assertIsNone(self.carga.aplicar(self.con, self.pres, self.comp, rol="costos", usuario=USUARIO).carga_id)
        self.assertEqual(self.repo.cargas(), antes)

    def test_un_cambio_de_receta_en_la_clave_vieja_versiona_al_clon_y_no_al_original(self):
        self.sustituir()
        con, comp = reescalar_linea(self.con, TRABE, 0, Decimal("1.01")), reescalar_linea(self.comp, TRABE, 0, Decimal("1.01"))  # la matriz viene en los dos
        rev = self.carga.revisar(con, self.pres, comp, rol="costos", usuario=USUARIO)
        self.assertEqual(rev.diagnostico.diagnostico.versionan, ("PRE-00120",))
        self.assertEqual(rev.diagnostico.pendientes, ())
        r = self.carga.aplicar(con, self.pres, comp, rol="costos", usuario=USUARIO)
        self.assertEqual(r.resumen["versiones_nuevas"], 1)
        self.assertEqual([v.version for v in self.repo.versiones("PRE-00120")], [1, 2])
        self.assertEqual([v.version for v in self.repo.versiones(TRABE)], [1])
        self.assertNotEqual(self.repo.versiones("PRE-00120")[1].pu, self.repo.versiones("PRE-00120")[0].pu)

    def test_un_precio_que_se_mueve_sigue_siendo_solo_un_precio(self):
        self.sustituir()
        con = reescalar_costo(self.con, "ACR-00001", Decimal("1.02"))  # la varilla de la trabe
        comp = reescalar_costo(self.comp, "ACR-00001", Decimal("1.02"))
        r = self.carga.aplicar(con, self.pres, comp, rol="costos", usuario=USUARIO)
        self.assertEqual(r.resumen["versiones_nuevas"], 0)
        self.assertGreater(r.resumen["precios_nuevos"], 0)
        self.assertEqual([v.version for v in self.repo.versiones("PRE-00120")], [1])

    def test_el_clon_de_un_clon_sigue_resolviendo_la_clave_de_siempre(self):
        self.sustituir()
        self.sustituir("PRE-00120", "PRE-00500")
        self.assertEqual(self.repo.estado_vigente().homologaciones, {TRABE: "PRE-00500", "PRE-00120": "PRE-00500"})
        rev = self.revisar_los_archivos()
        self.assertFalse(rev.plan.cambia_algo)
        self.assertEqual(rev.diagnostico.diagnostico.ausentes, ())
        self.assertEqual(self.repo.citas_de("PRE-00500").renglones_directos, 0)
        self.assertEqual({p.clave for p in self.repo.citas_de("PRE-00500").padres}, set(LOS_NUEVE))
        self.assertEqual(self.repo.citas_de("PRE-00120").padres, ())
        self.assertEqual(set(self.versiones_de_renglones("EST-21011")), {3})

    def test_lo_que_ya_se_sustituyo_no_se_vuelve_a_sustituir(self):
        self.sustituir()
        antes = self.repo.cargas()
        p = self.sc.proponer(TRABE, "PRE-00999", "sustituir", CO, QUIEN)
        self.assertFalse(p.aplicable)
        self.assertIn("ya se sustituyó por PRE-00120", p.problemas[0])
        with self.assertRaises(ClonacionNoProcede):
            self.sc.clonar(TRABE, "PRE-00999", "mantener", CO, QUIEN)
        self.assertEqual(self.repo.cargas(), antes)

    def test_si_se_sustituye_primero_el_compuesto_y_luego_su_hijo_el_compuesto_retirado_no_se_toca(self):
        # AUX-50001 (una nervadura) cita a AUX-00040 y AUX-00042: se sustituye ella primero, y luego lo que ella citaba
        self.sustituir("AUX-50001", "PRE-00200")
        p, r = self.sustituir("AUX-00040", "PRE-00201")
        self.assertEqual(sorted(x.clave for x in p.redirigidos), ["AUX-50009", "PRE-00200"])  # la retirada (AUX-50001) ya no cuenta
        self.assertEqual(len(self.repo.versiones("AUX-50001")), 1)
        self.assertEqual([v.version for v in self.repo.versiones("PRE-00200")], [1, 2])
        self.assertEqual([l.hijo for l in self.repo.versiones("PRE-00200")[1].lineas if l.hijo in ("AUX-00040", "PRE-00201")], ["PRE-00201"])
        # y los archivos de siempre siguen leyéndose igual: la retirada se lee como su clon, con el hijo que tiene hoy
        rev = self.revisar_los_archivos()
        self.assertFalse(rev.plan.cambia_algo)
        self.assertEqual(rev.diagnostico.diagnostico.versionan, ())
        self.assertEqual(self.totales(), {k: Decimal(v) for k, v in CAPITULOS.items()})

    def test_una_clave_vieja_en_un_renglon_nuevo_del_presupuesto_se_lee_como_el_clon(self):
        self.sustituir()
        # una copia de un renglón de Zafiro a la que se le pone la clave vieja de la trabe
        pres = con_otra_clave(con_copia(self.pres, ZAFIRO, "EST-10010", "EST-10010", cantidad="1"), ZAFIRO, "EST-10010", TRABE, n=2, unidad="M")
        rev = self.carga.revisar(self.con, pres, self.comp, rol="costos", usuario=USUARIO)
        self.assertEqual(rev.diagnostico.pendientes, ())
        self.assertEqual([c.clave for c in rev.diagnostico.cambios if c.tipo == "alta"], ["PRE-00120"])
        self.carga.aplicar(self.con, pres, self.comp, rol="costos", usuario=USUARIO)
        renglones = [r for r in self.carga.presupuesto(self.repo.presupuestos()[0].id).renglones if r.clave in (TRABE, "PRE-00120")]
        self.assertEqual([(r.clave, r.version) for r in renglones], [("PRE-00120", 1)])  # fija la versión del clon, no la del retirado

    # ------------------------------------------------------------------ clonar y mantener
    def test_mantener_deja_vivos_los_dos_y_no_toca_a_nadie(self):
        totales = self.totales()
        _, r = self.sc.clonar(TRABE, "PRE-00120", "mantener", CO, QUIEN)
        self.assertEqual((r.versiones_nuevas, r.renglones_fijados), (0, 0))
        self.assertEqual(self.repo.nodo("PRE-00120").procedencia, "clonacion")
        self.assertEqual({p.clave for p in self.repo.citas_de(TRABE).padres}, set(LOS_NUEVE))
        self.assertEqual(self.repo.citas_de("PRE-00120").padres, ())
        for clave in LOS_NUEVE:
            self.assertEqual(len(self.repo.versiones(clave)), 1)
        (c,) = self.repo.clones()
        self.assertEqual((c.modo, c.reconoce_clave_vieja_al_importar), ("mantener", False))
        self.assertEqual(self.repo.estado_vigente().homologaciones, {})
        self.assertEqual(self.totales(), totales)
        # el archivo no trae el clon: se dice, como con todo lo que ya no viene, y no se borra
        rev = self.revisar_los_archivos()
        self.assertEqual(rev.diagnostico.diagnostico.ausentes, ("PRE-00120",))
        self.assertFalse(rev.plan.cambia_algo)
        self.assertEqual(rev.diagnostico.avisos, ())

    # ------------------------------------------------------------------ clonar un insumo con precio
    def test_clonar_un_insumo_se_lleva_su_precio_y_los_precios_nuevos_van_al_clon(self):
        o = self.repo.nodo(UNA_CINTA)
        citas = self.repo.citas_de(UNA_CINTA)
        self.assertEqual((len(citas.padres), len(citas.padres[0].renglones)), (1, 3))
        padre = citas.padres[0].clave
        totales = self.totales()
        p, r = self.sc.clonar(UNA_CINTA, "COM-90058", "sustituir", CO, QUIEN)
        self.assertEqual(p.tipo, "insumo")
        n = self.repo.nodo("COM-90058")
        self.assertEqual((n.descripcion, n.unidad, n.categoria, n.rol, n.precio, n.con_matriz), (o.descripcion, o.unidad, o.categoria, "insumo", o.precio, False))
        self.assertEqual([x.precio for x in self.repo.precios("COM-90058")], [o.precio])
        self.assertEqual([v.version for v in self.repo.versiones(padre)], [1, 2])
        self.assertEqual(self.totales(), totales)
        # el archivo sigue trayendo el insumo viejo: su precio nuevo es el del clon
        sube, sube_comp = reescalar_costo(self.con, UNA_CINTA, Decimal("1.5")), reescalar_costo(self.comp, UNA_CINTA, Decimal("1.5"))
        rev = self.carga.revisar(sube, self.pres, sube_comp, rol="costos", usuario=USUARIO)
        self.assertEqual([c for c, _, _ in rev.diagnostico.precios_que_cambian], ["COM-90058"])
        self.carga.aplicar(sube, self.pres, sube_comp, rol="costos", usuario=USUARIO)
        self.assertEqual(len(self.repo.precios("COM-90058")), 2)
        self.assertEqual(len(self.repo.precios(UNA_CINTA)), 1)
        self.assertEqual([v.version for v in self.repo.versiones(padre)], [1, 2])  # un precio no versiona nada

    def test_clonar_un_concepto_sin_matriz_solo_se_mantiene(self):
        n = self.repo.nodo("ACC-00003")
        self.assertEqual((n.rol, n.con_matriz), ("concepto", False))
        p = self.sc.proponer("ACC-00003", "ACC-90003", "sustituir", CO, QUIEN)
        self.assertFalse(p.aplicable)
        self.assertIn("renglones de presupuesto", p.problemas[0])
        self.sc.clonar("ACC-00003", "ACC-90003", "mantener", CO, QUIEN)
        c = self.repo.nodo("ACC-90003")
        self.assertEqual((c.rol, c.con_matriz, c.procedencia, c.descripcion), ("concepto", False, "clonacion", n.descripcion))
        self.assertEqual(self.repo.versiones("ACC-90003"), [])

    # ------------------------------------------------------------------ lo que se rechaza
    def test_lo_que_no_se_puede_se_dice_y_no_se_escribe_nada(self):
        antes = self.repo.cargas()
        for original, clave, modo, frase in (
            (TRABE, "PRE-00001", "sustituir", "ya hay un nodo con la clave PRE-00001"),
            (TRABE, TRABE, "sustituir", "una clave distinta"),
            (TRABE, " ", "sustituir", "necesita una clave"),
            ("AUX-NO-ESTA", "PRE-00120", "sustituir", "no hay un nodo del catálogo con la clave AUX-NO-ESTA"),
            (TRABE, "PRE-00120", "duplicar", "el modo debe ser"),
        ):
            p = self.sc.proponer(original, clave, modo, CO, QUIEN)
            self.assertFalse(p.aplicable, (original, clave, modo))
            self.assertTrue(any(frase in x for x in p.problemas), (frase, p.problemas))
            self.assertIn("NO SE PUEDE", informe_de_clonacion(p))
            with self.assertRaises(ClonacionNoProcede):
                self.sc.clonar(original, clave, modo, CO, QUIEN)
        self.assertEqual(self.repo.cargas(), antes)

    def test_lo_que_cita_algo_contratado_no_se_sustituye_pero_si_se_mantiene(self):
        ServicioContratacion(self.repo).contratar(ZAFIRO, CO, QUIEN, LA_DE_LA_TRABE_EN_ZAFIRO)
        antes = self.repo.cargas()
        p = self.sc.proponer(TRABE, "PRE-00120", "sustituir", CO, QUIEN)
        self.assertFalse(p.aplicable)
        self.assertTrue(any("EST-21011" in x and "contratado" in x for x in p.problemas), p.problemas)
        with self.assertRaises(ClonacionNoProcede):
            self.sc.clonar(TRABE, "PRE-00120", "sustituir", CO, QUIEN)
        self.assertEqual(self.repo.cargas(), antes)
        with self.assertRaises(KeyError):
            self.repo.nodo("PRE-00120")
        self.assertEqual(len(self.repo.versiones("EST-21011")), 1)
        # mantener no redirige a nadie: se puede
        self.sc.clonar(TRABE, "PRE-00120", "mantener", CO, QUIEN)
        self.assertEqual(self.repo.nodo("PRE-00120").procedencia, "clonacion")

    def test_solo_clona_quien_tiene_la_funcion_y_dice_quien_es(self):
        for rol in ("residente", "costos", []):
            with self.assertRaises(PermisoDenegado):
                self.sc.proponer(TRABE, "PRE-00120", "sustituir", rol, QUIEN)
        with self.assertRaises(ValueError):
            self.sc.proponer(TRABE, "PRE-00120", "sustituir", CO, "")
        self.assertEqual(self.repo.clones(), [])
        p = ServicioClonacion(self.repo, permisos=lambda: {"clonar_insumo": frozenset({"costos"})}).proponer(TRABE, "PRE-00120", "sustituir", "costos", QUIEN)
        self.assertTrue(p.aplicable)  # la tabla de permisos manda, no un nombre de rol

    def test_si_la_carga_cambio_entre_proponer_y_aplicar_no_se_escribe_nada(self):
        p = self.sc.proponer(TRABE, "PRE-00120", "sustituir", CO, QUIEN)
        self.carga.aplicar(reescalar_costo(self.con, "ACE-00001", Decimal("1.1")), self.pres, reescalar_costo(self.comp, "ACE-00001", Decimal("1.1")),
                           rol="costos", usuario=USUARIO)
        antes = self.repo.cargas()
        with self.assertRaises(CatalogoCambio):
            self.repo.clonar(p.plan)
        self.assertEqual(self.repo.cargas(), antes)
        with self.assertRaises(KeyError):
            self.repo.nodo("PRE-00120")

    def test_una_clonacion_que_falla_a_medias_no_deja_nada(self):
        p = self.sc.proponer(TRABE, "PRE-00120", "sustituir", CO, QUIEN)
        antes, totales = self.repo.cargas(), self.totales()
        primera, otras = p.plan.sustituciones[0], p.plan.sustituciones[1:]
        con_renglon_ajeno = replace(otras[-1], renglones=(999_999,))  # las anteriores ya se habrían escrito
        with self.assertRaises(ValueError):
            self.repo.clonar(replace(p.plan, sustituciones=(primera,) + otras[:-1] + (con_renglon_ajeno,)))
        con_hijo_que_no_existe = replace(otras[-1], lineas=(replace(otras[-1].lineas[0], hijo="NO-EXISTE"),) + otras[-1].lineas[1:])
        with self.assertRaises(ValueError):
            self.repo.clonar(replace(p.plan, sustituciones=(primera,) + otras[:-1] + (con_hijo_que_no_existe,)))
        with self.assertRaises(ValueError):  # la clave del clon ya la ocupa otro: es la que el adaptador no deja pasar aunque nadie la revisara
            self.repo.clonar(replace(p.plan, clave="PRE-00001", nuevo=replace(p.plan.nuevo, clave="PRE-00001")))
        self.assertEqual(self.repo.cargas(), antes)
        self.assertEqual(self.totales(), totales)
        self.assertEqual(self.repo.clones(), [])
        for clave in LOS_NUEVE:
            self.assertEqual(len(self.repo.versiones(clave)), 1)
        with self.assertRaises(KeyError):
            self.repo.nodo("PRE-00120")

    # ------------------------------------------------------------------ el prefijo entero (P-11)
    def test_corregir_el_prefijo_aux_por_pre_cambia_las_79_sin_mover_un_centavo(self):
        totales = self.totales()
        todas = sorted(k for k in self.repo.estado_vigente().descripcion if k.startswith("AUX-"))
        self.assertEqual(len(todas), 79)
        c = self.sc.proponer_correccion_de_prefijo("AUX", "PRE", 120, CO, QUIEN)
        # en el orden de su número, desde el 120 (los PRE- que ya había son los primeros 20; el 120 está libre)
        self.assertEqual([o for o, _ in c.pares], todas)
        self.assertEqual([k for _, k in c.pares], [f"PRE-{n:05d}" for n in range(120, 199)])
        self.assertEqual((c.hechos, c.omitidos, c.rechazadas), ((), (), ()))
        self.assertEqual(c.pares[0], (TRABE, "PRE-00120"))
        t = informe_de_correccion(c)
        self.assertIn("79 claves por sustituir", t)
        self.assertIn("AUX-00001  → PRE-00120", t)
        self.assertEqual(self.repo.clones(), [])  # proponer no escribe

        # una tanda interrumpida: se hacen las diez primeras y se sigue donde se quedó
        for original, clave in c.pares[:10]:
            self.sc.clonar(original, clave, "sustituir", CO, QUIEN)
        c2 = self.sc.proponer_correccion_de_prefijo("AUX", "PRE", 120, CO, QUIEN)
        self.assertEqual(c2.pares, c.pares[10:])  # los números ocupados se saltan: la numeración sigue donde iba
        self.assertEqual(len(c2.hechos), 10)

        res = self.sc.corregir_prefijo("AUX", "PRE", 120, CO, QUIEN)
        self.assertEqual(([(o, k) for o, k, _ in res.hechos], res.rechazados), (list(c.pares[10:]), ()))
        self.assertIn("Sustituidas: 69", informe_de_resultado(res))

        self.assertEqual(len(self.repo.clones()), 79)
        self.assertEqual(self.repo.estado_vigente().homologaciones, dict(c.pares))
        self.assertEqual(self.totales(), totales)
        for original, clave in c.pares:
            self.assertEqual(self.repo.citas_de(original).padres, (), original)  # nadie vigente cita ya a la clave vieja
            n = self.repo.nodo(clave)
            self.assertEqual((n.categoria, n.procedencia, n.con_matriz), ("material", "clonacion", True))
            self.assertEqual(self.pu_del_motor(clave), self.pu_del_motor(original), clave)
        # las claves nuevas existen de verdad y las viejas siguen ahí, retiradas
        self.assertEqual(sorted(k for k in self.repo.estado_vigente().descripcion if k.startswith("AUX-")), todas)

        # el archivo de siempre se lee igual que antes: nada versiona, nada falta, nada se detiene
        rev = self.revisar_los_archivos()
        g = rev.diagnostico.diagnostico
        self.assertEqual((g.nuevos, g.versionan, g.detenidos, g.ausentes), ((), (), (), ()))
        self.assertFalse(rev.plan.cambia_algo)
        self.assertEqual((rev.diagnostico.pendientes, rev.diagnostico.alertas_de_texto), ((), ()))
        self.assertTrue(any(a.startswith("79 claves del archivo") for a in rev.diagnostico.avisos))

        # y no hay nada más que hacer
        c3 = self.sc.proponer_correccion_de_prefijo("AUX", "PRE", 120, CO, QUIEN)
        self.assertEqual((c3.pares, len(c3.hechos)), ((), 79))
        res3 = self.sc.corregir_prefijo("AUX", "PRE", 120, CO, QUIEN)
        self.assertEqual((res3.hechos, res3.rechazados), ((), ()))

    def test_las_claves_del_prefijo_que_no_terminan_en_numero_se_dicen_y_no_se_proponen(self):
        self.sc.clonar(TRABE, "AUX-ESPECIAL", "mantener", CO, QUIEN)
        c = self.sc.proponer_correccion_de_prefijo("AUX", "PRE", 120, CO, QUIEN)
        self.assertEqual(c.omitidos, ("AUX-ESPECIAL",))
        self.assertEqual(len(c.pares), 79)
        self.assertNotIn("AUX-ESPECIAL", [o for o, _ in c.pares])
        self.assertIn("AUX-ESPECIAL", informe_de_correccion(c))

    def test_el_prefijo_viejo_y_el_nuevo_tienen_que_ser_otros(self):
        for viejo, nuevo, desde in (("AUX", "AUX", 1), ("", "PRE", 1), ("AUX", "", 1), ("AUX", "PRE", 0)):
            with self.assertRaises(ValueError):
                self.sc.proponer_correccion_de_prefijo(viejo, nuevo, desde, CO, QUIEN)
        with self.assertRaises(PermisoDenegado):
            self.sc.proponer_correccion_de_prefijo("AUX", "PRE", 120, "costos", QUIEN)
        self.assertEqual(self.sc.proponer_correccion_de_prefijo("NOEXISTE", "PRE", 1, CO, QUIEN).pares, ())

    def test_lo_contratado_se_salta_y_se_dice_en_la_correccion_del_prefijo(self):
        ServicioContratacion(self.repo).contratar(ZAFIRO, CO, QUIEN, LA_DE_LA_TRABE_EN_ZAFIRO)
        res = self.sc.corregir_prefijo("AUX", "PRE", 120, CO, QUIEN)
        rechazados = {p.original for p in res.rechazados}
        self.assertIn(TRABE, rechazados)
        self.assertGreater(len(res.hechos), 0)
        self.assertEqual(len(res.hechos) + len(res.rechazados), 79)
        self.assertEqual(len(self.repo.clones()), len(res.hechos))
        self.assertIn("NO SE HIZO AUX-00001", informe_de_resultado(res))
        # lo contratado quedó como estaba
        self.assertEqual(len(self.repo.versiones("EST-21011")), 1)
        self.assertEqual(self.totales(), {k: Decimal(v) for k, v in CAPITULOS.items()})
