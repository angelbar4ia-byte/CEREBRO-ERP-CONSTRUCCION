"""
Pruebas del cargador del programa, la cadena de relevos y la vista del Gantt — `core/programa.py`.

Datos reales, no fixtures: los siete programas de `1-mundo/programas/PROGRAMAS-PROTOTIPOS.csv` y las
cifras que `1-mundo/PROGRAMA-CPM.md` publica. Los casos chicos prueban las reglas de carga de D-442 y
D-443 con filas armadas a mano, donde la regla se ve completa.

Correr con: cd backend && python3 -m unittest discover
"""
import csv
import json
import re
import unittest
from collections import Counter
from datetime import date
from fractions import Fraction
from pathlib import Path

from core.gantt_pagina import pagina_gantt
from core.motor_cpm import Calendario, CicloError, calcular_cpm
from core.motor_cpm import Vinculo
from core.programa import (
    AgregarVinculo,
    CambiarDuracion,
    CambiarVinculo,
    FijarInicio,
    Fila,
    PERMISO_DE,
    QuitarVinculo,
    cadena_de_relevos,
    cargar_programa,
    filas_desde_csv,
    leer_vinculos,
    reprogramar,
    vista_gantt,
)

RAIZ = Path(__file__).resolve().parents[3]
PROGRAMAS = RAIZ / "1-mundo" / "programas"
CAL = Calendario(no_habiles=frozenset({date(2025, 12, 25), date(2026, 1, 1)}))
LOS_SIETE = ["Zafiro", "Rubí", "Jade", "Zafiro Plus", "Diamante sin chimenea", "Diamante con chimenea", "Oro"]
ORIGEN = date(2025, 6, 9)


def _csv(nombre):
    with open(PROGRAMAS / nombre, encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


_cache = {}


def programa(proto):
    if proto not in _cache:
        _cache[proto] = cargar_programa(filas_desde_csv(PROGRAMAS / "PROGRAMAS-PROTOTIPOS.csv", proto), CAL)
    return _cache[proto]


# --------------------------------------------------------------------------- reglas de carga, a mano


def _f(n, nivel, tipo, ini=None, fin=None, dias=0, vinc="", clave=None):
    return Fila(
        llave=f"oid{n}", fila=n, nivel=nivel, tipo=tipo, clave=clave or f"C{n}", descripcion=f"fila {n}",
        inicio=ini, termino=fin, dias=Fraction(dias), vinculos=vinc,
    )


def _d(dia):  # lunes 9-jun-2025 + n días hábiles (semana de 5)
    return CAL.fecha(CAL.n(date(2025, 6, 9)) + dia)


def _partida(n, ini, fin, vinc=""):
    return _f(n, 4, "Concepto", _d(ini), _d(fin), fin - ini + 1, vinc)


class PruebasLeerVinculos(unittest.TestCase):
    def test_el_formato_fuente(self):
        self.assertEqual(
            leer_vinculos("80SF, 68SS+120.00000,4FS-8.00000"),
            [(80, "SF", "80SF", Fraction(0)), (68, "SS", "68SS+120.00000", Fraction(15)), (4, "FS", "4FS-8.00000", Fraction(-1))],
        )

    def test_lo_que_no_cumple_el_formato_no_se_pierde(self):
        (fila, tipo, token, desfase), = leer_vinculos("ocho veces")
        self.assertEqual((fila, tipo, token, desfase), (None, "", "ocho veces", None))

    def test_celda_vacia(self):
        self.assertEqual(leer_vinculos(""), [])
        self.assertEqual(leer_vinculos(" , "), [])


class PruebasCarga(unittest.TestCase):
    def test_una_cadena_sencilla_se_carga_y_se_calcula(self):
        filas = [
            _f(1, 1, "Subcapítulo"),
            _partida(2, 0, 1),
            _partida(3, 2, 3, "2FS"),
        ]
        prog = cargar_programa(filas, CAL)
        self.assertEqual([r.motivo for r in prog.rechazados], [])
        self.assertEqual(len(prog.vinculos), 1)
        r = prog.calcular(CAL)
        self.assertEqual(r["oid3"].fecha_inicio, _d(2))
        self.assertEqual(r["oid3"].es_ruta_critica, True)

    def test_se_rechaza_el_autovinculo(self):
        prog = cargar_programa([_partida(1, 0, 1, "1FS")], CAL)
        self.assertEqual([(r.fila, r.motivo) for r in prog.rechazados], [(1, "autovinculo")])
        self.assertEqual(prog.vinculos, [])

    def test_la_sucesora_nunca_es_un_bloque(self):
        filas = [_f(1, 1, "Subcapítulo", vinc="2FS"), _partida(2, 0, 1)]
        prog = cargar_programa(filas, CAL)
        self.assertEqual([(r.fila, r.motivo) for r in prog.rechazados], [(1, "sucesora_bloque")])

    def test_predecesora_que_no_existe_y_formato_roto(self):
        filas = [_partida(1, 0, 1, "99FS, nada"), _f(5, 4, "Concepto")]  # un concepto sin fechas no se programa
        filas[0] = _partida(1, 0, 1, "99FS, nada, 5FS")
        prog = cargar_programa(filas, CAL)
        self.assertEqual(
            sorted(r.motivo for r in prog.rechazados), ["formato", "predecesora_desconocida", "predecesora_desconocida"]
        )

    def test_un_bloque_puede_ser_predecesora_y_el_que_contiene_a_su_sucesora_se_lee_sin_ella(self):
        # D-443: la gualdra (fila 3) termina la víspera de que arranque el resto de su losa: SF con holgura 0
        filas = [
            _f(1, 3, "Nivel 3"),
            _partida(2, 3, 5),  # la losa
            _partida(3, 2, 2, "1SF"),  # la gualdra, del propio grupo
        ]
        filas[0] = _f(1, 3, "Nivel 3")
        filas[1] = _f(2, 4, "Concepto", _d(3), _d(5), 3)
        filas[2] = _f(3, 4, "Concepto", _d(2), _d(2), 1, "1SF")
        prog = cargar_programa(filas, CAL)
        self.assertEqual(prog.rechazados, [])
        self.assertEqual(prog.incumplidos(CAL), [])  # cumple con holgura 0: el bloque, sin la gualdra, abre en el día 3

    def test_de_un_ciclo_se_rechaza_el_vinculo_que_las_fechas_ya_contradicen(self):
        # 2 espera a 3 (FS) y 3 espera a 2 (SS+1): en el plan 3 va después de 2, así que el primero es el roto
        filas = [_partida(2, 0, 1, "3FS"), _partida(3, 2, 3, "2SS+8.00000")]
        prog = cargar_programa(filas, CAL)
        self.assertEqual([(r.fila, r.token, r.motivo) for r in prog.rechazados], [(2, "3FS", "cierra_un_ciclo")])
        self.assertEqual(len(prog.vinculos), 1)

    def test_un_ciclo_a_traves_de_un_bloque_tambien_se_rechaza(self):
        # las dos manos de pintura dentro de un grupo: cada una espera al resto del grupo, que incluye a la otra
        filas = [
            _f(1, 3, "Nivel 3"),
            _f(2, 4, "Concepto", _d(0), _d(1), 2, "1FS"),
            _f(3, 4, "Concepto", _d(2), _d(3), 2, "1FS"),
        ]
        prog = cargar_programa(filas, CAL)
        self.assertEqual([r.motivo for r in prog.rechazados], ["cierra_un_ciclo"])
        self.assertEqual(prog.rechazados[0].fila, 2)  # la que las fechas contradicen
        prog.calcular(CAL)  # y lo que queda se calcula

    def test_dos_filas_con_el_mismo_oid_no_se_cargan(self):
        a = _partida(1, 0, 1)
        with self.assertRaises(ValueError):
            cargar_programa([a, Fila(**{**a.__dict__, "fila": 2})], CAL)


# --------------------------------------------------------------------------- los siete programas reales


class PruebasLosSiete(unittest.TestCase):
    def test_vinculos_cargados_por_programa(self):
        # los del libro (D-442) más los dos de D-460; Zafiro pierde los 6 que la red no puede calcular
        esperado = {
            "Zafiro": 118, "Rubí": 103, "Jade": 86, "Zafiro Plus": 130,
            "Diamante sin chimenea": 129, "Diamante con chimenea": 130, "Oro": 132,
        }
        self.assertEqual({p: len(programa(p).vinculos) for p in LOS_SIETE}, esperado)

    def test_solo_zafiro_trae_vinculos_que_la_red_no_puede_calcular(self):
        for p in LOS_SIETE:
            malos = programa(p).rechazados
            self.assertEqual(len(malos), 6 if p == "Zafiro" else 0, p)
        zafiro = programa("Zafiro")
        self.assertEqual(Counter(r.motivo for r in zafiro.rechazados), Counter({"autovinculo": 1, "cierra_un_ciclo": 5}))
        # el autovínculo de D-424 es `EST-01151`
        (auto,) = [r for r in zafiro.rechazados if r.motivo == "autovinculo"]
        self.assertEqual(zafiro.por_llave[auto.sucesora].clave, "EST-01151")

    def test_los_seis_que_zafiro_no_deja_cargar_estan_entre_sus_15_incumplidos(self):
        # el registro de D-444 (`ZAFIRO-15-INCUMPLIDOS.csv`) cita fila sucesora y fila predecesora
        registro = {(int(r["fila_sucesora"]), int(r["fila_predecesora"])) for r in _csv("ZAFIRO-15-INCUMPLIDOS.csv")}
        for r in programa("Zafiro").rechazados:
            fila_p = int(re.match(r"\d+", r.token).group())
            self.assertIn((r.fila, fila_p), registro, r)

    def test_el_registro_dice_que_pasa_con_cada_uno_al_cargar(self):
        registro = _csv("ZAFIRO-15-INCUMPLIDOS.csv")
        self.assertEqual(
            Counter(r["al_cargar"] for r in registro),
            Counter({"carga y avisa": 9, "no carga: cierra un ciclo": 5, "no carga: autovínculo": 1}),
        )
        rechazados = {(r.fila, int(re.match(r"\d+", r.token).group())) for r in programa("Zafiro").rechazados}
        marcados = {(int(r["fila_sucesora"]), int(r["fila_predecesora"])) for r in registro if r["al_cargar"].startswith("no carga")}
        self.assertEqual(rechazados, marcados)

    def test_los_incumplidos_que_si_se_cargan(self):
        # 15 en el libro (D-445) menos los 6 rechazados: los 9 que cargan y avisan con `vinculo_incumplido`
        self.assertEqual(len(programa("Zafiro").incumplidos(CAL)), 9)
        for p in LOS_SIETE[1:]:
            self.assertEqual(programa(p).incumplidos(CAL), [], p)

    def test_las_siete_redes_se_calculan(self):
        for p in LOS_SIETE:
            r = programa(p).calcular(CAL)
            self.assertTrue(r.ruta_critica, p)

    def test_el_cpm_de_la_red_cargada_es_el_de_la_prueba_del_motor(self):
        # los mismos días que `test_que_calcula_el_cpm_con_la_red_que_hay`
        esperado = {"Rubí": 139, "Jade": 139, "Zafiro Plus": 81, "Diamante sin chimenea": 139, "Diamante con chimenea": 139, "Oro": 139}
        for p, dias in esperado.items():
            r = programa(p).calcular(CAL)
            self.assertEqual(r.fin_proyecto - CAL.n(ORIGEN), dias, p)

    def test_las_cadenas_de_relevos_son_las_publicadas_fila_por_fila(self):
        publicadas = {}
        for r in _csv("RUTAS-DE-RELEVOS.csv"):
            publicadas.setdefault(r["prototipo"], []).append(int(r["fila"]))
        self.assertEqual(set(publicadas), {"Zafiro", "Zafiro Plus", "Diamante sin chimenea", "Diamante con chimenea", "Oro"})
        for p, filas in publicadas.items():
            prog = programa(p)
            cadena = [prog.por_llave[x].fila for x in cadena_de_relevos(prog, CAL)]
            self.assertEqual(cadena, filas, p)

    def test_las_cadenas_de_relevos_de_rubi_y_jade(self):
        # D-425 las daba por cumplidas en la red mínima (16 de 16 y 15 de 15); ahora se leen completas
        self.assertEqual(len(cadena_de_relevos(programa("Rubí"), CAL)), 28)
        self.assertEqual(len(cadena_de_relevos(programa("Jade"), CAL)), 27)

    def test_la_cadena_cierra_con_el_programa(self):
        # Zafiro arranca el 9-jun con la losa de cimentación; los de dos plantas arrancan donde la red se ata
        for p, cierre in (("Zafiro", date(2025, 12, 18)), ("Zafiro Plus", date(2026, 1, 5)), ("Oro", date(2026, 1, 5))):
            prog = programa(p)
            cadena = cadena_de_relevos(prog, CAL)
            self.assertEqual(prog.ventanas[cadena[-1]].fin, cierre, p)
        z = programa("Zafiro")
        self.assertEqual(z.ventanas[cadena_de_relevos(z, CAL)[0]].inicio, ORIGEN)


class PruebasGantt(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.prog = programa("Zafiro Plus")
        cls.v = vista_gantt(cls.prog, CAL, ventana=(date(2025, 8, 18), date(2025, 8, 29)))

    def test_el_arbol_completo_por_defecto_y_los_resumenes_de_d432_si_se_piden(self):
        # el árbol: 388 partidas y 105 resúmenes (capítulo, 14 frentes, 49 etapas y 41 de Nivel 3)
        filas = self.v["filas"]
        self.assertEqual(sum(1 for f in filas if not f["resumen"]), 388)
        self.assertEqual(Counter(f["nivel"] for f in filas if f["resumen"]), Counter({0: 1, 1: 14, 2: 49, 3: 41}))
        # D-432: 389 filas de concepto y 90 resúmenes de Nivel 2 y 3 = 479; la fila de cierre en blanco no tiene barra
        solo = vista_gantt(self.prog, CAL, niveles_resumen=(2, 3))["filas"]
        self.assertEqual(sum(1 for f in solo if f["resumen"]), 90)
        self.assertEqual({f["nivel"] for f in solo if f["resumen"]}, {2, 3})

    def test_cada_fila_cuelga_de_su_padre_y_se_puede_plegar(self):
        por = {f["llave"]: f for f in self.v["filas"]}
        raices = [f for f in self.v["filas"] if f["padre"] is None]
        self.assertEqual([f["nivel"] for f in raices], [0])
        for f in self.v["filas"]:
            if f["padre"] is None:
                continue
            padre = por[f["padre"]]
            self.assertLess(padre["nivel"], f["nivel"])
            self.assertTrue(padre["resumen"])
            self.assertLessEqual(padre["inicio"], f["inicio"])
            self.assertGreaterEqual(padre["fin"], f["fin"])
        # subiendo desde cualquier partida se llega a su frente y al capítulo
        frente = {k: f for k, f in por.items() if f["nivel"] == 1}
        for f in self.v["filas"]:
            if f["resumen"]:
                continue
            x = f
            while x["nivel"] != 1:
                x = por[x["padre"]]
            self.assertEqual(x["clave"], f["frente"])
            self.assertIn(x["llave"], frente)

    def test_el_resumen_abarca_a_sus_partidas(self):
        por = {f["llave"]: f for f in self.v["filas"]}
        for b, hijos in self.prog.bloques.items():
            if b in por and hijos:
                self.assertEqual(por[b]["inicio"], min(por[h]["inicio"] for h in hijos))
                self.assertEqual(por[b]["fin"], max(por[h]["fin"] for h in hijos))

    def test_una_flecha_por_vinculo_y_ninguna_sale_de_un_bloque(self):
        flechas = self.v["flechas"]
        self.assertEqual(len(flechas), 130)
        filas = {f["llave"]: f for f in self.v["filas"] if not f["resumen"]}
        for fl in flechas:
            self.assertIn(fl["de"], filas)
            self.assertIn(fl["a"], filas)
            self.assertNotEqual(fl["de"], fl["a"])
        self.assertEqual(Counter(f["tipo"] for f in flechas), Counter({"FS": 106, "SS": 14, "FF": 9, "SF": 1}))

    def test_la_red_cargada_no_trae_flechas_incumplidas_y_la_cadena_las_une(self):
        flechas = self.v["flechas"]
        self.assertFalse([f for f in flechas if f["incumplido"]])
        self.assertTrue(all(f["holgura"] is not None and f["holgura"] >= 0 for f in flechas))
        # la cadena de 13 pasos se une con 12 flechas con holgura 0
        entre = [f for f in flechas if f["entre_relevos"] and f["holgura"] == 0]
        self.assertGreaterEqual(len(entre), 12)
        self.assertEqual(len(self.v["relevos"]), 13)
        self.assertEqual(sum(1 for f in self.v["filas"] if f["critica"]), 13)

    def test_se_marcan_los_fines_de_semana_los_feriados_y_la_ventana(self):
        marcas = self.v["marcas"]
        feriados = [m["fecha"] for m in marcas["no_laborables"] if m["motivo"] == "feriado"]
        self.assertEqual(feriados, ["2025-12-25", "2026-01-01"])
        self.assertEqual(marcas["ventana"], {"inicio": "2025-08-18", "fin": "2025-08-29"})
        self.assertEqual(self.v["desde"], "2025-06-09")
        self.assertEqual(self.v["hasta"], "2026-01-05")
        for m in marcas["no_laborables"]:
            if m["motivo"] == "fin de semana":
                self.assertIn(date.fromisoformat(m["fecha"]).weekday(), (5, 6))

    def test_zafiro_muestra_sus_flechas_rotas(self):
        v = vista_gantt(programa("Zafiro"), CAL)
        self.assertEqual(sum(1 for f in v["flechas"] if f["incumplido"]), 9)


def _por_fila(prog):
    return {f.fila: f for f in prog.filas}


class PruebasReprogramar(unittest.TestCase):
    """Editar es proponer: se reprograma por empuje mínimo y se devuelve el impacto (§8 de PROGRAMA-CPM.md)."""

    def test_sin_ediciones_un_plan_que_cumple_sus_vinculos_queda_identico(self):
        for p in LOS_SIETE[1:]:
            prog = programa(p)
            r = reprogramar(prog, CAL)
            self.assertEqual(r.movidas, [], p)
            self.assertEqual(r.programa.ventanas, prog.ventanas, p)
            self.assertEqual((r.fin_antes, r.fin_despues, r.dias_de_cambio, r.ruta_cambia), (r.fin_antes, r.fin_antes, 0, False), p)

    def test_si_zafiro_obedeciera_los_118_vinculos_que_cargan_cerraria_12_dias_habiles_despues(self):
        # D-444: Zafiro queda de origen. Esto solo mide qué costaría que la red mandara sobre el plan manual
        prog = programa("Zafiro")
        r = reprogramar(prog, CAL)
        self.assertEqual(len(r.movidas), 47)
        self.assertEqual((r.fin_antes, r.fin_despues, r.dias_de_cambio), (date(2025, 12, 18), date(2026, 1, 7), 12))
        self.assertEqual(r.incumplidos, [])
        self.assertTrue(all(m.dias_inicio >= 0 and m.dias_fin >= 0 for m in r.movidas))  # el empuje nunca adelanta

    def test_p16_en_plus_corre_el_cierre_diez_dias_habiles(self):
        # D-437 y D-460: «cerrarlo pide mover el plazo diez días hábiles (30 a 32 semanas)»
        prog = programa("Zafiro Plus")
        f = _por_fila(prog)
        r = reprogramar(prog, CAL, [AgregarVinculo(f[978].llave, f[1102].llave, "FS", Fraction(1))])
        self.assertEqual((r.fin_antes, r.fin_despues, r.dias_de_cambio), (date(2026, 1, 5), date(2026, 1, 19), 10))
        self.assertEqual(r.rechazadas, [])
        self.assertTrue(r.ruta_cambia)

    def test_alargar_una_partida_con_holgura_no_mueve_el_cierre_ni_avisa_de_ruta(self):
        prog = programa("Zafiro Plus")
        f = _por_fila(prog)
        r = reprogramar(prog, CAL, [CambiarDuracion(f[982].llave, Fraction(12))])  # el muro de la planta alta, 7 días hoy
        self.assertEqual(r.dias_de_cambio, 0)
        self.assertFalse(r.ruta_cambia)  # D-100: correr fechas no es noticia
        self.assertTrue(r.movidas)
        self.assertGreater(CAL.n(r.programa.ventanas[f[982].llave].fin), CAL.n(prog.ventanas[f[982].llave].fin))

    def test_la_fecha_que_fija_el_residente_corre_lo_que_cuelga_y_nada_mas(self):
        prog = programa("Zafiro Plus")
        f = _por_fila(prog)
        r = reprogramar(prog, CAL, [FijarInicio(f[1102].llave, date(2025, 10, 28))])  # el vertedero abre la cadena de relevos
        self.assertEqual(r.dias_de_cambio, 5)
        self.assertEqual(len(r.movidas), 31)
        self.assertFalse(r.ruta_cambia)

    def test_quitar_un_vinculo_nunca_adelanta_el_plan(self):
        prog = programa("Zafiro Plus")
        v = prog.vinculos[0]
        r = reprogramar(prog, CAL, [QuitarVinculo(v.predecesora, v.sucesora)])
        self.assertEqual(r.movidas, [])
        self.assertEqual(len(r.programa.vinculos), len(prog.vinculos) - 1)

    def test_el_modo_temprano_suelta_el_plan_y_calcula_la_red(self):
        prog = programa("Zafiro Plus")
        r = reprogramar(prog, CAL, modo="temprano")
        self.assertEqual(CAL.n(r.fin_despues) - CAL.n(ORIGEN) + 1, 81)  # los 81 días de §4.4
        self.assertLess(r.fin_despues, r.fin_antes)

    def test_lo_que_no_se_puede_aplicar_queda_dicho_y_no_frena_a_lo_demas(self):
        prog = programa("Zafiro Plus")
        f = _por_fila(prog)
        v = next(x for x in prog.vinculos if x.predecesora in prog.ventanas)
        nivel2 = next(x for x in prog.filas if x.tipo == "Nivel 2")
        r = reprogramar(prog, CAL, [
            CambiarDuracion("no existe", 3),
            CambiarDuracion(f[1102].llave, 0),
            AgregarVinculo(f[1102].llave, f[1102].llave),
            AgregarVinculo(f[1102].llave, nivel2.llave),
            AgregarVinculo(v.predecesora, v.sucesora, v.tipo, v.desfase),
            AgregarVinculo(v.sucesora, v.predecesora, "FS"),
            QuitarVinculo(v.predecesora, "no existe"),
            CambiarDuracion(f[982].llave, Fraction(8)),  # esta sí se aplica
        ])
        self.assertEqual(
            [x.motivo for x in r.rechazadas],
            ["actividad_desconocida", "duracion_invalida", "autovinculo", "sucesora_no_es_partida", "repetido", "cierra_un_ciclo", "vinculo_inexistente"],
        )
        self.assertTrue(r.movidas)  # la duración del muro sí se aplicó

    def test_cambiar_el_tipo_de_un_vinculo(self):
        prog = programa("Zafiro Plus")
        v = next(x for x in prog.vinculos if x.tipo == "FS" and x.predecesora in prog.ventanas)
        r = reprogramar(prog, CAL, [CambiarVinculo(v.predecesora, v.sucesora, "FS", "SS", Fraction(0))])
        self.assertEqual(r.rechazadas, [])
        self.assertIn(Vinculo(v.predecesora, v.sucesora, "SS", Fraction(0)), r.programa.vinculos)
        self.assertNotIn(v, r.programa.vinculos)

    def test_cada_edicion_dice_con_que_permiso_se_hace(self):
        # `MODELO.md` §5b: la estructura es de Control de obra y las fechas, del Residente
        self.assertEqual(PERMISO_DE[CambiarDuracion], "editar_estructura_programa")
        self.assertEqual(PERMISO_DE[AgregarVinculo], "editar_estructura_programa")
        self.assertEqual(PERMISO_DE[FijarInicio], "editar_fechas_programa")

    def test_el_programa_reprogramado_se_dibuja_con_su_base(self):
        prog = programa("Zafiro Plus")
        f = _por_fila(prog)
        r = reprogramar(prog, CAL, [AgregarVinculo(f[978].llave, f[1102].llave, "FS", Fraction(1))])
        v = vista_gantt(r.programa, CAL, base=prog)
        movidas = [x for x in v["filas"] if x.get("dias_movida")]
        self.assertTrue(movidas)
        cierre = next(x for x in v["filas"] if x["nivel"] == 0)  # el capítulo: cierra con el programa
        self.assertEqual(cierre["dias_movida"], 10)
        self.assertEqual(cierre["base_fin"], "2026-01-05")
        self.assertEqual(cierre["fin"], "2026-01-19")


class PruebasPagina(unittest.TestCase):
    def test_la_pagina_junta_plantilla_motor_y_datos(self):
        html = pagina_gantt(programa("Zafiro Plus"), CAL, "Gantt Zafiro Plus", ventana=(date(2025, 8, 18), date(2025, 8, 29)))
        self.assertIn("<title>Gantt Zafiro Plus</title>", html)
        for marca in ("/*__MOTOR__*/", "/*__CLIENTE__*/", "/*__TOKENS__*/", "/*__SESION__*/", "__DATOS__", "__TITULO__", "__CONFIG__"):
            self.assertNotIn(marca, html)
        self.assertIn("const Motor", html)
        self.assertIn("const ClientePrograma", html)
        self.assertIn("const Sesion", html)
        self.assertIn("--bg:", html)  # los colores compartidos
        self.assertIn("const CFG = null;", html)  # la simulación: sin servidor, con el programa dentro
        datos = html.split("else G = ", 1)[1].split(";\n} catch", 1)[0]
        v = json.loads(datos)
        self.assertEqual(len(v["red"]["partidas"]), 388)
        self.assertEqual(len(v["relevos"]), 13)
        self.assertEqual(len(v["ruta_critica_red"]), 28)
        self.assertEqual(v["marcas"]["ventana"]["inicio"], "2025-08-18")


class PruebasMotorDiagnostico(unittest.TestCase):
    def test_el_ciclo_que_se_alarga_dice_que_vinculos_lo_forman(self):
        filas = [
            _f(1, 3, "Nivel 3"),
            _f(2, 4, "Concepto", _d(0), _d(1), 2, "1FS"),
            _f(3, 4, "Concepto", _d(2), _d(3), 2, "1FS"),
        ]
        # armado a mano, sin pasar por el cargador que lo rechazaría
        from core.motor_cpm import Actividad, Vinculo

        acts = [Actividad("a", 2), Actividad("b", 2), Actividad("G", 0, ("a", "b"))]
        with self.assertRaises(CicloError) as cm:
            calcular_cpm(acts, [Vinculo("G", "a", "FS"), Vinculo("G", "b", "FS")], CAL, ORIGEN)
        self.assertEqual(len(cm.exception.vinculos), 2)
        self.assertEqual({v.sucesora for v in cm.exception.vinculos}, {"a", "b"})


if __name__ == "__main__":
    unittest.main()
