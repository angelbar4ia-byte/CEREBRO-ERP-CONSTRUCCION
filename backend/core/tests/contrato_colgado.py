"""
Colgar el programa del presupuesto (D-474): el contrato que cumplen los adaptadores del programa y del catálogo juntos, con los
siete programas de verdad (`1-mundo/programas/PROGRAMAS-PROTOTIPOS.csv`) contra los siete presupuestos de verdad
(`1-mundo/opus/CATALOGO_DE_PRESUPUESTO.csv`). Mezclar con `unittest.TestCase` y definir `nuevos_repositorios()`, que devuelve
`(RepositorioPrograma, RepositorioCatalogo)` vacíos y, si son de una base, de la misma.
"""
import csv
from dataclasses import replace
from decimal import Decimal
from fractions import Fraction

from core.catalogo import ServicioCarga
from core.colgado import ColgadoNoCuadra, ServicioColgado, TOPE_DEL_RESUMEN, alinear, informe_de_colgado
from core.programa import CambiarDuracion, cargar_programa
from core.servicio_programa import Enlace, PermisoDenegado, ProgramaNoExiste, ServicioPrograma, YaColgado, YaReemplazado
from core.tests.contrato_catalogo import USUARIO
from core.tests.contrato_programa import CAL, CO, CSV, RES, programa
from core.tests.datos_opus import CONCEPTOS, PRESUPUESTO, con_cantidad, con_copia, sin_renglon, texto

QUIEN = "luis@obra.mx"
# programa → (clave de su presupuesto, bloques que casan, partidas que casan, marcadores vacíos de OPUS que trae)
ESPERADO = {
    "Zafiro": ("CAS-00004", 83, 315, 16),
    "Rubí": ("CAS-00003", 79, 294, 15),
    "Zafiro Plus": ("CAS-00006", 107, 388, 19),
    "Jade": ("CAS-00002", 78, 289, 15),
    "Diamante sin chimenea": ("CAS-00005", 104, 377, 19),
    "Diamante con chimenea": ("CAS-00007", 105, 380, 18),
    "Oro": ("CAS-00001", 109, 402, 18),
}


class ContratoColgado:
    def nuevos_repositorios(self):  # pragma: no cover
        raise NotImplementedError

    def setUp(self):
        self.programas, self.catalogo = self.nuevos_repositorios()
        ServicioCarga(self.catalogo).aplicar(texto(CONCEPTOS), texto(PRESUPUESTO), None, rol="costos", usuario=USUARIO)
        self.sp = ServicioPrograma(self.programas)
        self.sc = ServicioColgado(self.sp, self.catalogo)
        self.presupuestos = {p.clave: p for p in self.catalogo.presupuestos()}

    def subir(self, proto, nombre=None):
        return self.sp.importar(nombre or proto, programa(proto), CAL, CO, QUIEN)

    def colgar(self, proto, **kw):
        pid = self.subir(proto)
        return pid, self.sc.colgar(pid, CO, QUIEN, **kw)

    def una_edicion(self, pid):
        """Una edición real de las que ya usa el contrato del programa: la duración de la losa de la fila 982 de Zafiro Plus."""
        return CambiarDuracion(next(f.llave for f in self.programas.leer_programa(pid).filas if f.fila == 982), Fraction(12))

    # ------------------------------------------------------------------ los siete programas de verdad
    def test_cada_programa_se_cuelga_de_su_presupuesto_sin_que_se_le_diga_cual(self):
        for proto, (clave, bloques, partidas, vacias) in ESPERADO.items():
            pid, a = self.colgar(proto)
            g = self.programas.leer_programa(pid)
            self.assertEqual(g.presupuesto_id, self.presupuestos[clave].id, proto)
            self.assertEqual((a.bloques, a.partidas, a.vacias, a.nuevos), (bloques, partidas, vacias, bloques + partidas), proto)
            self.assertEqual(len(g.enlaces), bloques + partidas, proto)
            self.assertEqual(sum(e.nodo_id is not None for e in g.enlaces), bloques)
            self.assertEqual(sum(e.renglon_id is not None for e in g.enlaces), partidas)
            self.assertEqual(self.programas.listar_programas()[-1].enlazadas, bloques + partidas)

    def test_cuadra_de_los_dos_lados_salvo_una_partida_de_zafiro_que_el_presupuesto_no_tiene(self):
        for proto, (clave, *_) in ESPERADO.items():
            a = self.sc.proponer(self.subir(proto), CO)
            esperadas = [("ACA-02034", 327)] if proto == "Zafiro" else []
            self.assertEqual([(s.clave, s.fila) for s in a.sin_par], esperadas, proto)
            self.assertEqual(a.sin_programar, (), proto)  # y ningún renglón del presupuesto se quedó sin fecha
            self.assertEqual(a.conceptos_del_programa, a.partidas + len(esperadas), proto)

    def test_cada_enlace_apunta_a_lo_que_su_fila_dice_y_a_su_bloque(self):
        for proto in ("Zafiro", "Jade"):
            pid, a = self.colgar(proto)
            g = self.programas.leer_programa(pid)
            datos = self.catalogo.datos_de_presupuesto(g.presupuesto_id)
            renglon = {l.id: l for l in datos.lineas}
            enlace = {e.oid: e for e in g.enlaces}
            pila = []  # (nivel, nodo) del bloque en que va cada fila
            for f in g.filas:
                while pila and pila[-1][0] >= f.nivel:
                    pila.pop()
                e = enlace.get(f.llave)
                if e is None:  # sin enlace solo un marcador vacío o lo que el informe dijo que no tenía con qué casarse
                    self.assertTrue((not f.clave and not f.descripcion) or f.llave in {s.oid for s in a.sin_par}, f.fila)
                    if f.tipo != "Concepto":
                        pila.append((f.nivel, None))
                    continue
                if e.nodo_id is not None:
                    n = datos.nodos[e.nodo_id]
                    self.assertEqual((n.clave, n.tipo_opus), (f.clave, f.tipo), f.fila)
                    pila.append((f.nivel, e.nodo_id))
                else:
                    l = renglon[e.renglon_id]
                    self.assertEqual(datos.nodos[l.hijo_id].clave, f.clave, f.fila)
                    self.assertEqual(l.padre_id, pila[-1][1], f.fila)  # el renglón es del bloque que lo contiene en el programa

    def test_las_cantidades_del_programa_son_las_del_presupuesto_salvo_una_de_zafiro(self):
        """El programa de Zafiro dice 4 en OBE-04010 y el presupuesto, 1: lo dice el cruce, no se corrige solo."""
        for proto in ESPERADO:
            pid, _ = self.colgar(proto)
            g = self.programas.leer_programa(pid)
            renglon = {l.id: l for l in self.catalogo.datos_de_presupuesto(g.presupuesto_id).lineas}
            with open(CSV, encoding="utf-8-sig") as archivo:
                csv_ = {r["oid"]: r for r in csv.DictReader(archivo) if r["prototipo"] == proto}
            distintas = [(csv_[e.oid]["fila"], csv_[e.oid]["clave"], csv_[e.oid]["cantidad"], format(renglon[e.renglon_id].cantidad.normalize(), "f"))
                         for e in g.enlaces
                         if e.renglon_id is not None and Decimal(csv_[e.oid]["cantidad"] or "0") != renglon[e.renglon_id].cantidad]
            self.assertEqual(distintas, [("241", "OBE-04010", "4", "1")] if proto == "Zafiro" else [], proto)

    def test_un_concepto_repetido_en_el_bloque_casa_con_sus_renglones_en_orden(self):
        pid, _ = self.colgar("Zafiro Plus")
        g = self.programas.leer_programa(pid)
        datos = self.catalogo.datos_de_presupuesto(g.presupuesto_id)
        renglon = {l.id: l for l in datos.lineas}
        grupos = {}
        for e in g.enlaces:
            if e.renglon_id is not None:
                l = renglon[e.renglon_id]
                grupos.setdefault((l.padre_id, datos.nodos[l.hijo_id].clave), []).append(l.orden)
        repetidos = {k: v for k, v in grupos.items() if len(v) > 1}
        self.assertEqual(sorted(k[1] for k in repetidos), ["ACA-02032", "ACA-04010", "ACA-08050"])
        for ordenes in repetidos.values():
            self.assertEqual(ordenes, sorted(set(ordenes)))  # cada fila, su renglón; el segundo del programa es el segundo del presupuesto
        usados = [e.renglon_id for e in g.enlaces if e.renglon_id is not None]
        self.assertEqual(len(usados), len(set(usados)))

    def test_los_marcadores_vacios_de_opus_no_se_enlazan_ni_cuentan_como_faltantes(self):
        pid, a = self.colgar("Rubí")
        g = self.programas.leer_programa(pid)
        enlazadas = {e.oid for e in g.enlaces}
        vacias = [f for f in g.filas if not f.clave and not f.descripcion]
        self.assertEqual((len(vacias), a.vacias), (15, 15))
        self.assertTrue(all(f.llave not in enlazadas for f in vacias))
        self.assertEqual(a.sin_par, ())

    # ------------------------------------------------------------------ proponer, decidir, repetir
    def test_proponer_no_escribe_nada(self):
        pid = self.subir("Oro")
        a = self.sc.proponer(pid, CO)
        self.assertEqual((a.bloques, a.partidas, a.nuevos), (109, 402, 0))
        g = self.programas.leer_programa(pid)
        self.assertEqual((g.presupuesto_id, g.enlaces, g.colgaduras), (None, [], []))

    def test_colgar_deja_dicho_quien_cuando_y_que_cuadro(self):
        pid, a = self.colgar("Zafiro")
        (c,) = self.programas.leer_programa(pid).colgaduras
        self.assertEqual((c.usuario, c.rol, c.presupuesto_id, c.nuevos), (QUIEN, CO, self.presupuestos["CAS-00004"].id, 398))
        r = c.resumen
        self.assertEqual((r["presupuesto"], r["bloques"], r["partidas"], r["marcadores_vacios"], r["forzado"]), ("CAS-00004", 83, 315, 16, False))
        self.assertEqual(r["programa_sin_par"], [{"oid": r["programa_sin_par"][0]["oid"], "fila": 327, "tipo": "Concepto", "clave": "ACA-02034",
                                                  "motivo": "concepto_sin_par"}])
        self.assertEqual((r["presupuesto_sin_programa_total"], r["presupuesto_sin_programa"]), (0, []))

    def test_colgar_otra_vez_no_cambia_nada(self):
        pid, _ = self.colgar("Jade")
        antes = self.programas.leer_programa(pid)
        a = self.sc.colgar(pid, CO, QUIEN)
        self.assertEqual((a.nuevos, a.ya_estaban), (0, 78 + 289))
        despues = self.programas.leer_programa(pid)
        self.assertEqual((despues.enlaces, len(despues.colgaduras)), (antes.enlaces, 1))

    def test_colgar_no_es_editar(self):
        pid = self.subir("Zafiro Plus")
        self.sp.aplicar(pid, self.una_edicion(pid), CO, QUIEN)
        visto = self.sp.abrir(pid)
        self.sc.colgar(pid, CO, QUIEN)
        despues = self.sp.abrir(pid)
        self.assertEqual((despues.version, len(despues.aplicadas)), (visto.version, 1))
        self.assertEqual(despues.programa.ventanas, visto.programa.ventanas)

    def test_se_pide_el_permiso_de_editar_la_estructura(self):
        pid = self.subir("Oro")
        for roles in (RES, "costos", ["residente", "costos"]):
            with self.assertRaises(PermisoDenegado):
                self.sc.proponer(pid, roles)
            with self.assertRaises(PermisoDenegado):
                self.sc.colgar(pid, roles, QUIEN)
        with self.assertRaises(ValueError):
            self.sc.colgar(pid, CO, "")
        self.assertEqual(self.programas.leer_programa(pid).presupuesto_id, None)
        self.assertEqual(self.sc.colgar(pid, ["residente", CO], QUIEN).nuevos, 511)

    def test_el_programa_de_otro_presupuesto_no_se_cuelga_aunque_se_insista(self):
        pid = self.subir("Rubí")
        zafiro = self.presupuestos["CAS-00004"].id
        for forzar in (False, True):
            with self.assertRaises(ColgadoNoCuadra) as e:
                self.sc.colgar(pid, CO, QUIEN, presupuesto_id=zafiro, forzar=forzar)
            self.assertIn("ninguna fila", str(e.exception))
            self.assertEqual(e.exception.alineacion.partidas, 0)
        self.assertEqual(self.programas.leer_programa(pid).presupuesto_id, None)

    def test_si_casa_menos_de_la_mitad_hay_que_confirmarlo(self):
        plus = programa("Zafiro Plus")
        n = {"i": 0}

        def otra_clave(f):  # conserva la tercera parte de los conceptos de verdad; a los demás les cambia la clave
            if f.tipo != "Concepto" or not f.clave:
                return f
            n["i"] += 1
            return f if n["i"] % 3 == 0 else replace(f, clave=f.clave + "-X")

        pid = self.sp.importar("Plus a medias", cargar_programa([otra_clave(f) for f in plus.filas], CAL), CAL, CO, QUIEN)
        with self.assertRaises(ColgadoNoCuadra) as e:
            self.sc.colgar(pid, CO, QUIEN)  # la clave del capítulo es la de siempre: el presupuesto se encuentra, pero no cuadra
        a = e.exception.alineacion
        self.assertEqual((a.partidas, a.conceptos_del_programa), (129, 388))
        self.assertFalse(a.casa_bien)
        self.assertEqual(self.programas.leer_programa(pid).enlaces, [])  # nada se colgó
        forzada = self.sc.colgar(pid, CO, QUIEN, forzar=True)  # quien decide lo confirma
        self.assertEqual(forzada.partidas, 129)
        (c,) = self.programas.leer_programa(pid).colgaduras
        self.assertTrue(c.resumen["forzado"])
        self.assertEqual((c.resumen["programa_sin_par_total"], len(c.resumen["programa_sin_par"])), (259, TOPE_DEL_RESUMEN))
        self.assertEqual(c.resumen["presupuesto_sin_programa_total"], 259)
        self.assertEqual(len(c.resumen["presupuesto_sin_programa"]), TOPE_DEL_RESUMEN)  # el total siempre; la lista, con tope

    def test_no_cuelga_de_un_presupuesto_que_no_existe_ni_de_uno_que_no_se_ha_cargado(self):
        pid = self.subir("Oro")
        with self.assertRaises(ColgadoNoCuadra):
            self.sc.colgar(pid, CO, QUIEN, presupuesto_id=987654)
        programas, vacio = self.nuevos_repositorios()  # una base sin presupuestos
        sp = ServicioPrograma(programas)
        pid = sp.importar("Oro", programa("Oro"), CAL, CO, QUIEN)
        with self.assertRaises(ColgadoNoCuadra) as e:
            ServicioColgado(sp, vacio).colgar(pid, CO, QUIEN)
        self.assertIn("CAS-00001", str(e.exception))
        with self.assertRaises(ProgramaNoExiste):
            ServicioColgado(sp, vacio).proponer(4321, CO)

    # ------------------------------------------------------------------ un enlace puesto no se mueve
    def test_el_programa_no_cambia_de_presupuesto(self):
        pid, _ = self.colgar("Zafiro")
        with self.assertRaises(YaColgado) as e:
            self.sc.colgar(pid, CO, QUIEN, presupuesto_id=self.presupuestos["CAS-00003"].id)
        self.assertEqual(e.exception.presupuesto_id, self.presupuestos["CAS-00004"].id)
        with self.assertRaises(YaColgado):  # tampoco por el puerto
            self.programas.colgar(pid, self.presupuestos["CAS-00003"].id, [], usuario=QUIEN, rol=CO, resumen={})

    def test_una_fila_enlazada_no_se_enlaza_a_otra_cosa(self):
        pid, _ = self.colgar("Zafiro")
        g = self.programas.leer_programa(pid)
        con_renglon = [e for e in g.enlaces if e.renglon_id is not None]
        movido = Enlace(con_renglon[0].oid, renglon_id=con_renglon[1].renglon_id)
        with self.assertRaises(YaColgado):
            self.programas.colgar(pid, g.presupuesto_id, [movido], usuario=QUIEN, rol=CO, resumen={})
        self.assertEqual(self.programas.leer_programa(pid).enlaces, g.enlaces)

    def test_dos_filas_no_ocupan_el_mismo_renglon(self):
        pid = self.subir("Zafiro")
        presupuesto = self.presupuestos["CAS-00004"].id
        a = self.sc.proponer(pid, CO)
        renglones = [e for e in a.enlaces if e.renglon_id is not None]
        repetido = [renglones[0], Enlace(renglones[1].oid, renglon_id=renglones[0].renglon_id)]
        with self.assertRaises(YaColgado):
            self.programas.colgar(pid, presupuesto, repetido, usuario=QUIEN, rol=CO, resumen={})
        self.assertEqual(self.programas.leer_programa(pid).enlaces, [])

    def test_una_fila_que_no_es_del_programa_no_deja_nada_a_medias(self):
        pid = self.subir("Zafiro")
        a = self.sc.proponer(pid, CO)
        with self.assertRaises(ValueError):
            self.programas.colgar(pid, a.presupuesto_id, list(a.enlaces[:5]) + [Enlace("no-existe", nodo_id=a.enlaces[0].nodo_id)],
                                  usuario=QUIEN, rol=CO, resumen={})  # el nodo es de la primera fila, pero la que no existe se dice primero
        g = self.programas.leer_programa(pid)
        self.assertEqual((g.presupuesto_id, g.enlaces, g.colgaduras), (None, [], []))

    def test_un_enlace_es_a_un_nodo_o_a_un_renglon_y_a_uno_solo(self):
        for mal in (dict(), dict(nodo_id=1, renglon_id=2)):
            with self.assertRaises(ValueError):
                Enlace("x", **mal)

    def test_con_version_nueva_el_programa_se_cierra_tambien_a_colgarse(self):
        pid = self.subir("Zafiro Plus")
        self.sp.subir_version(pid, "v2", programa("Zafiro Plus"), CAL, CO, "marta")
        with self.assertRaises(YaReemplazado):
            self.sc.colgar(pid, CO, QUIEN)
        with self.assertRaises(YaReemplazado):
            self.sc.proponer(pid, CO)
        with self.assertRaises(YaReemplazado):  # y por el puerto, que lo mira con la fila bloqueada, tampoco
            self.programas.colgar(pid, self.presupuestos["CAS-00006"].id, [], usuario=QUIEN, rol=CO, resumen={})

    # ------------------------------------------------------------------ la versión nueva hereda lo colgado
    def test_la_version_nueva_hereda_el_presupuesto_y_los_enlaces_de_las_filas_que_comparte(self):
        pid, a = self.colgar("Zafiro Plus")
        r = self.sp.subir_version(pid, "Zafiro Plus v2", programa("Zafiro Plus"), CAL, CO, "marta")
        g, anterior = self.programas.leer_programa(r.id), self.programas.leer_programa(pid)
        self.assertEqual((g.presupuesto_id, g.enlaces), (anterior.presupuesto_id, anterior.enlaces))
        self.assertEqual((r.enlaces_pasaron, r.enlaces_anterior), (495, 495))
        (c,) = g.colgaduras
        self.assertEqual((c.usuario, c.rol, c.nuevos, c.resumen["heredada_de"]), ("marta", CO, 495, pid))
        self.assertEqual((g.traspaso["presupuesto_id"], g.traspaso["enlaces_pasaron"], g.traspaso["enlaces_anterior"]),
                         (anterior.presupuesto_id, 495, 495))
        self.assertEqual(self.sc.colgar(r.id, CO, QUIEN).nuevos, 0)  # y ya está completa: no hay nada que agregar

    def test_lo_que_el_archivo_nuevo_ya_no_trae_queda_sin_enlace_y_se_dice(self):
        pid, _ = self.colgar("Zafiro Plus")
        plus = programa("Zafiro Plus")
        quitada = next(f for f in plus.filas if f.fila == 982)  # una partida: la losa
        r = self.sp.subir_version(pid, "v2", cargar_programa([f for f in plus.filas if f is not quitada], CAL), CAL, CO, "marta")
        self.assertEqual((r.enlaces_anterior, r.enlaces_pasaron), (495, 494))
        g = self.programas.leer_programa(r.id)
        self.assertEqual(len(g.enlaces), 494)
        self.assertNotIn(quitada.llave, {e.oid for e in g.enlaces})
        # volver a colgar la versión nueva no pone nada y dice lo que quedó sin fecha: el renglón de la losa que ya no está en el programa
        a = self.sc.colgar(r.id, CO, QUIEN)
        self.assertEqual((a.nuevos, [(s.clave, s.renglon) for s in a.sin_programar]), (0, [(quitada.clave, True)]))

    def test_si_el_programa_nunca_se_colgo_la_version_nueva_tampoco(self):
        pid = self.subir("Zafiro Plus")
        r = self.sp.subir_version(pid, "v2", programa("Zafiro Plus"), CAL, CO, "marta")
        g = self.programas.leer_programa(r.id)
        self.assertEqual((g.presupuesto_id, g.enlaces, g.colgaduras), (None, [], []))
        self.assertNotIn("presupuesto_id", g.traspaso)
        self.assertEqual((r.enlaces_pasaron, r.enlaces_anterior), (0, 0))

    def test_la_lista_de_programas_dice_de_cual_presupuesto_cuelga_cada_uno(self):
        a, b = self.subir("Oro"), self.subir("Jade")
        self.sc.colgar(b, CO, QUIEN)
        por_id = {r.id: r for r in self.sp.listar()}
        self.assertEqual((por_id[a].presupuesto_id, por_id[a].enlazadas), (None, 0))
        self.assertEqual((por_id[b].presupuesto_id, por_id[b].enlazadas), (self.presupuestos["CAS-00002"].id, 78 + 289))

    # ------------------------------------------------------------------ el presupuesto cambia (D-476)
    def reconciliar(self, presupuesto, **kw):
        return ServicioCarga(self.catalogo).aplicar(texto(CONCEPTOS), presupuesto, None, rol="costos", usuario=USUARIO, **kw)

    def test_reconciliar_el_presupuesto_no_mueve_los_enlaces_del_programa(self):
        pid, _ = self.colgar("Zafiro")
        antes = self.programas.leer_programa(pid).enlaces
        nuevo = con_cantidad(texto(PRESUPUESTO), "CAS-00004", "EST-10010", "40")  # otra cantidad: el mismo renglón
        nuevo = con_copia(nuevo, "CAS-00004", "EST-10011", "EST-10011", cantidad="5")  # y un renglón que el programa no tiene
        self.reconciliar(nuevo)
        a = self.sc.proponer(pid, CO)
        self.assertEqual((self.programas.leer_programa(pid).enlaces, a.se_moverian, a.huerfanos, a.nuevos), (antes, (), (), 0))
        self.assertEqual(a.ya_estaban, 398)  # todos los enlaces de antes siguen valiendo
        self.assertEqual([(s.clave, s.cantidad, s.renglon) for s in a.sin_programar], [("EST-10011", "5", True)])  # dinero nuevo sin fecha
        self.assertEqual(self.sc.colgar(pid, CO, QUIEN).nuevos, 0)  # el renglón nuevo no tiene fila a la que enlazar

    def test_un_renglon_dado_de_baja_deja_su_enlace_huerfano_y_el_programa_lo_dice(self):
        pid, _ = self.colgar("Zafiro")
        g = self.programas.leer_programa(pid)
        fila = next(f for f in g.filas if f.fila == 241)  # OBE-04010, la que dice 4 en el programa y 1 en el presupuesto
        oid = fila.llave
        sin = sin_renglon(texto(PRESUPUESTO), "CAS-00004", "OBE-04010")
        self.reconciliar(sin, todas_las_bajas=True)
        a = self.sc.proponer(pid, CO)
        self.assertEqual(a.huerfanos, (oid,))
        self.assertIn(("OBE-04010", "concepto_sin_par"), [(s.clave, s.motivo) for s in a.sin_par])
        self.assertIn("dio de baja", informe_de_colgado(a))
        self.assertEqual(self.sc.colgar(pid, CO, QUIEN).nuevos, 0)  # no se mueve ni se borra: el enlace es historia
        self.assertEqual(self.programas.leer_programa(pid).enlaces, g.enlaces)
        (c,) = self.programas.leer_programa(pid).colgaduras
        self.assertEqual(c.nuevos, 398)

    # ------------------------------------------------------------------ alinear, puro
    def test_alinear_no_depende_del_orden_de_las_filas_del_presupuesto_sino_de_su_ruta(self):
        pid = self.subir("Oro")
        g = self.programas.leer_programa(pid)
        datos = self.catalogo.datos_de_presupuesto(self.presupuestos["CAS-00001"].id)
        a = alinear(g.filas, datos)
        # las mismas filas con otros números de fila y otros oid casan igual: nada se alinea por posición
        corridas = [replace(f, llave="x" + f.llave, fila=f.fila + 1000) for f in g.filas]
        b = alinear(corridas, datos)
        self.assertEqual([(e.nodo_id, e.renglon_id) for e in a.enlaces], [(e.nodo_id, e.renglon_id) for e in b.enlaces])
