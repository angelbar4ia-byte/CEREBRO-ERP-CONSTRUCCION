"""
Pruebas del motor del CPM, contra los siete programas reales —
constructor-erp.md: "test con datos reales del proyecto, no con fixtures
inventadas."

Las cifras de conformidad salen de `1-mundo/CONOCIMIENTO.md` §11.14 (D-443, D-445,
D-460) y los datos de `1-mundo/programas/PROGRAMAS-PROTOTIPOS.csv`, que es el
libro de los siete prototipos pasado al repositorio. Los casos chicos de red
(cadenas, desfases, bloques, plazo) son aritmética de las fórmulas de D-445,
verificada a mano.

Correr con: cd backend && python3 -m unittest discover
"""
import csv
import re
import unittest
from collections import Counter, defaultdict
from datetime import date
from fractions import Fraction
from pathlib import Path

from core.motor_cpm import (
    Actividad,
    Calendario,
    CicloError,
    Vinculo,
    VinculoInvalido,
    Ventana,
    calcular_cpm,
    cuadrillas_efectivas,
    desfase_en_dias,
    dias_de_atraso,
    dias_teoricos,
    holgura_instantes,
    holgura_vinculo,
    retraso_neto,
    ventana_de_bloque,
    vinculos_incumplidos,
)

RAIZ = Path(__file__).resolve().parents[3]
CSV_PROGRAMAS = RAIZ / "1-mundo" / "programas" / "PROGRAMAS-PROTOTIPOS.csv"

# el calendario de los siete programas: lunes a viernes sin el 25-dic ni el 1-ene (D-428)
CAL = Calendario(no_habiles=frozenset({date(2025, 12, 25), date(2026, 1, 1)}))
TOKEN = re.compile(r"^(\d+)(FS|SS|FF|SF)([+-]\d+(?:\.\d+)?)?$")


# --------------------------------------------------------------------------- carga de los programas reales


def _cargar():
    por = defaultdict(list)
    with open(CSV_PROGRAMAS, encoding="utf-8", newline="") as fh:
        for r in csv.DictReader(fh):
            por[r["prototipo"]].append(r)
    return por


PROGRAMAS = _cargar()


def _red(proto):
    """fechas por fila, bloques (fila -> partidas descendientes) y vínculos, de un prototipo.
    Un vínculo lleva `agregado=True` si lo sumó D-460 y no venía en el libro."""
    filas = PROGRAMAS[proto]
    fechas, bloques, vinculos = {}, {}, []
    for i, r in enumerate(filas):
        f, nivel = int(r["fila"]), int(r["nivel"])
        dias = float(r["dias_laborables"]) if r["dias_laborables"] else 0
        if r["tipo"] == "Concepto" and dias > 0 and r["inicio"]:
            fechas[f] = Ventana(date.fromisoformat(r["inicio"]), date.fromisoformat(r["termino"]))
        if r["tipo"] != "Concepto":
            hijos = []
            for q in filas[i + 1 :]:
                if int(q["nivel"]) <= nivel:
                    break
                if q["tipo"] == "Concepto":
                    hijos.append(int(q["fila"]))
            bloques[f] = hijos
        for t in (r["vinculos"].split(",") if r["vinculos"] else []):
            t = t.strip()
            m = TOKEN.match(t)
            assert m, f"formato de vínculo raro en {proto} fila {f}: {t}"
            v = Vinculo(int(m.group(1)), f, m.group(2), desfase_en_dias(float(m.group(3) or 0)))
            vinculos.append((v, t == r["vinculo_agregado_d460"]))
    return fechas, bloques, vinculos


# --------------------------------------------------------------------------- calendario


class PruebasCalendario(unittest.TestCase):
    def test_numera_dias_habiles_y_vuelve(self):
        for d in (date(2025, 6, 9), date(2025, 7, 14), date(2025, 12, 24), date(2025, 12, 26), date(2026, 1, 2), date(2026, 1, 5)):
            self.assertTrue(CAL.es_habil(d))
            self.assertEqual(CAL.fecha(CAL.n(d)), d)

    def test_fin_de_semana_y_feriados_no_cuentan(self):
        self.assertEqual(CAL.entre(date(2025, 12, 24), date(2025, 12, 26)), 1)  # el 25 no se trabaja
        self.assertEqual(CAL.entre(date(2025, 12, 31), date(2026, 1, 2)), 1)  # el 1-ene tampoco
        self.assertEqual(CAL.entre(date(2025, 6, 13), date(2025, 6, 16)), 1)  # viernes a lunes
        self.assertFalse(CAL.es_habil(date(2025, 12, 25)))
        self.assertFalse(CAL.es_habil(date(2025, 6, 14)))  # sábado
        # un día que no se trabaja abre en el siguiente día hábil
        self.assertEqual(CAL.n(date(2025, 6, 14)), CAL.n(date(2025, 6, 16)))

    def test_el_sabado_se_agrega_como_opcion(self):
        con_sabado = Calendario(dias_laborables_semana=frozenset({0, 1, 2, 3, 4, 5}))
        self.assertEqual(con_sabado.entre(date(2025, 6, 9), date(2025, 6, 16)), 6)
        self.assertEqual(con_sabado.fecha(con_sabado.n(date(2025, 6, 14))), date(2025, 6, 14))

    def test_los_siete_programas_cierran_en_139_y_149_dias_habiles(self):
        # D-447: una planta 139 (cierra el 18-dic), dos plantas 149 (cierra el 5-ene)
        esperado = {"Zafiro": 139, "Rubí": 139, "Jade": 139, "Zafiro Plus": 149, "Diamante sin chimenea": 149, "Diamante con chimenea": 149, "Oro": 149}
        for proto, dias in esperado.items():
            cap = next(r for r in PROGRAMAS[proto] if r["tipo"] == "Capítulo")
            self.assertEqual(int(cap["dias_laborables"]), dias, proto)
            self.assertEqual(CAL.n(date.fromisoformat(cap["termino"])) + 1 - CAL.n(date.fromisoformat(cap["inicio"])), dias, proto)


class PruebasDuracion(unittest.TestCase):
    """D-446: los días teóricos no se redondean; el paso es del calendario."""

    def test_la_formula_no_redondea(self):
        self.assertEqual(dias_teoricos(36, Fraction("26.25")), Fraction(36) / Fraction("26.25"))
        self.assertEqual(dias_teoricos(100, 10, 2), Fraction(5))

    def test_cercano_manda_el_medio_hacia_arriba_y_nunca_menos_de_un_paso(self):
        self.assertEqual(CAL.acomodar(Fraction(5, 2)), 3)
        self.assertEqual(CAL.acomodar(Fraction("1.37")), 1)  # 36 m² ÷ 26.25
        self.assertEqual(CAL.acomodar(Fraction("0.17")), 1)  # una instalación de 0.17 día
        self.assertEqual(CAL.acomodar(4), 4)  # un múltiplo exacto no se mueve
        self.assertEqual(CAL.acomodar(0), 0)

    def test_arriba_y_abajo_toleran_un_centesimo_de_dia(self):
        arriba = Calendario(sentido_redondeo="arriba")
        abajo = Calendario(sentido_redondeo="abajo")
        self.assertEqual(arriba.acomodar(Fraction(183.83) / Fraction(26.25)), 7)  # 7.003 días se quedan en 7, no en 8
        self.assertEqual(arriba.acomodar(Fraction("7.2")), 8)
        self.assertEqual(abajo.acomodar(Fraction("6.997")), 7)
        self.assertEqual(abajo.acomodar(Fraction("6.5")), 6)
        self.assertEqual(abajo.acomodar(Fraction("0.4")), 1)  # nunca menos de un paso

    def test_otro_paso_acomoda_a_medios_dias(self):
        medios = Calendario(paso_dias=Fraction(1, 2))
        self.assertEqual(medios.acomodar(Fraction("1.37")), Fraction(3, 2))
        self.assertEqual(medios.acomodar(Fraction("0.1")), Fraction(1, 2))
        sin_redondeo = Calendario(paso_dias=None)
        self.assertEqual(sin_redondeo.acomodar(Fraction("1.37")), Fraction("1.37"))

    def test_el_redondeo_mueve_las_cuadrillas_no_el_esfuerzo(self):
        cantidad, rend = 36, Fraction("26.25")
        programada = CAL.acomodar(dias_teoricos(cantidad, rend))
        efectivas = cuadrillas_efectivas(cantidad, rend, programada)
        self.assertEqual(programada * efectivas * 8, Fraction(cantidad) / rend * 8)
        self.assertAlmostEqual(float(efectivas), 1.371, places=3)


# --------------------------------------------------------------------------- las cuatro holguras de D-445


class PruebasHolguras(unittest.TestCase):
    LUN, MAR, MIE = date(2025, 6, 9), date(2025, 6, 10), date(2025, 6, 11)

    def h(self, tipo, desfase, p, s):
        return holgura_vinculo(Vinculo("p", "s", tipo, desfase), Ventana(*p), Ventana(*s), CAL)

    def test_fin_inicio(self):
        # p termina el lunes: s puede arrancar el martes con holgura 0
        self.assertEqual(self.h("FS", 0, (self.LUN, self.LUN), (self.MAR, self.MAR)), 0)
        self.assertEqual(self.h("FS", 0, (self.LUN, self.LUN), (self.MIE, self.MIE)), 1)
        self.assertEqual(self.h("FS", 0, (self.LUN, self.LUN), (self.LUN, self.LUN)), -1)
        self.assertEqual(self.h("FS", 1, (self.LUN, self.LUN), (self.MAR, self.MAR)), -1)  # una espera de un día
        self.assertEqual(self.h("FS", -1, (self.LUN, self.LUN), (self.LUN, self.LUN)), 0)  # un traslape de un día

    def test_inicio_inicio_fin_fin(self):
        self.assertEqual(self.h("SS", 0, (self.LUN, self.MAR), (self.LUN, self.MIE)), 0)
        self.assertEqual(self.h("SS", 0, (self.LUN, self.MAR), (self.MAR, self.MIE)), 1)
        self.assertEqual(self.h("FF", 0, (self.LUN, self.MAR), (self.LUN, self.MAR)), 0)
        self.assertEqual(self.h("FF", 0, (self.LUN, self.MAR), (self.LUN, self.MIE)), 1)
        self.assertEqual(self.h("FF", 1, (self.LUN, self.MAR), (self.LUN, self.MAR)), -1)

    def test_inicio_fin_suma_un_instante(self):
        # la gualdra termina el lunes 14-jul y el martes 15 arranca el resto de su losa: SF con holgura 0 (D-445)
        gualdra = Ventana(date(2025, 7, 14), date(2025, 7, 14))
        losa = Ventana(date(2025, 7, 15), date(2025, 8, 4))
        self.assertEqual(holgura_vinculo(Vinculo("losa", "gualdra", "SF"), losa, gualdra, CAL), 0)
        # si la gualdra termina un día antes, el vínculo no se cumple
        antes = Ventana(date(2025, 7, 11), date(2025, 7, 11))
        self.assertEqual(holgura_vinculo(Vinculo("losa", "gualdra", "SF"), losa, antes, CAL), -1)

    def test_las_cuatro_en_instantes(self):
        # abre(s)=10, cierra(s)=14; abre(p)=2, cierra(p)=6, desfase 3
        args = (3, 2, 6, 10, 14)
        self.assertEqual(holgura_instantes("FS", *args), 10 - (6 + 3))
        self.assertEqual(holgura_instantes("SS", *args), 10 - (2 + 3))
        self.assertEqual(holgura_instantes("FF", *args), 14 - (6 + 3))
        self.assertEqual(holgura_instantes("SF", *args), 14 - (2 + 3))
        self.assertEqual(holgura_instantes("inicio_fin", *args), holgura_instantes("SF", *args))

    def test_el_desfase_del_formato_fuente_viene_en_horas(self):
        self.assertEqual(desfase_en_dias(120), 15)
        self.assertEqual(desfase_en_dias(-8), -1)

    def test_ventana_de_bloque_sin_la_sucesora(self):
        fechas = {1: Ventana(date(2025, 6, 9), date(2025, 6, 10)), 2: Ventana(date(2025, 6, 11), date(2025, 6, 13)), 3: Ventana(date(2025, 6, 16), date(2025, 6, 17))}
        self.assertEqual(ventana_de_bloque([1, 2, 3], fechas), Ventana(date(2025, 6, 9), date(2025, 6, 17)))
        self.assertEqual(ventana_de_bloque([1, 2, 3], fechas, excluir=3), Ventana(date(2025, 6, 9), date(2025, 6, 13)))
        self.assertIsNone(ventana_de_bloque([3], fechas, excluir=3))


# --------------------------------------------------------------------------- CPM en redes chicas


def _act(i, d, **kw):
    return Actividad(i, d, **kw)


class PruebasCPM(unittest.TestCase):
    INI = date(2025, 6, 9)  # lunes

    def test_cadena_fin_inicio(self):
        r = calcular_cpm([_act("a", 3), _act("b", 2), _act("c", 1)], [Vinculo("a", "b"), Vinculo("b", "c")], CAL, self.INI)
        self.assertEqual((r["a"].fecha_inicio, r["a"].fecha_fin), (date(2025, 6, 9), date(2025, 6, 11)))
        self.assertEqual((r["b"].fecha_inicio, r["b"].fecha_fin), (date(2025, 6, 12), date(2025, 6, 13)))
        self.assertEqual((r["c"].fecha_inicio, r["c"].fecha_fin), (date(2025, 6, 16), date(2025, 6, 16)))
        self.assertEqual(r.dias_habiles, 6)
        self.assertEqual(r.ruta_critica, ["a", "b", "c"])
        self.assertTrue(all(r[i].holgura == 0 for i in "abc"))

    def test_holgura_de_la_rama_corta(self):
        r = calcular_cpm([_act("a", 4), _act("b", 2), _act("c", 1)], [Vinculo("a", "c"), Vinculo("b", "c")], CAL, self.INI)
        self.assertEqual(r["b"].holgura, 2)
        self.assertEqual(r.ruta_critica, ["a", "c"])
        self.assertEqual(r["c"].fecha_inicio, date(2025, 6, 13))

    def test_inicio_inicio_con_espera_y_traslape(self):
        r = calcular_cpm([_act("a", 5), _act("b", 5)], [Vinculo("a", "b", "SS", 2)], CAL, self.INI)
        self.assertEqual(r["b"].fecha_inicio, date(2025, 6, 11))  # dos días después de que arranca a
        r = calcular_cpm([_act("a", 5), _act("b", 5)], [Vinculo("a", "b", "FS", -2)], CAL, self.INI)
        self.assertEqual(r["b"].fecha_inicio, date(2025, 6, 12))  # se traslapa dos días con el final de a
        self.assertEqual(r["b"].inicio_temprano, r["a"].fin_temprano - 2)

    def test_fin_fin_pone_piso_al_termino_de_la_sucesora(self):
        # b dura 2 y no puede terminar antes que a (4 días): arranca en el día 3
        r = calcular_cpm([_act("a", 4), _act("b", 2)], [Vinculo("a", "b", "FF")], CAL, self.INI)
        self.assertEqual(r["b"].fin_temprano, r["a"].fin_temprano)
        self.assertEqual(r["b"].fecha_inicio, date(2025, 6, 11))

    def test_inicio_fin_pone_piso_al_termino_de_la_sucesora(self):
        # b no puede terminar antes de que empiece a, que arranca tras x (3 días)
        r = calcular_cpm([_act("x", 3), _act("a", 2), _act("b", 1)], [Vinculo("x", "a"), Vinculo("a", "b", "SF")], CAL, self.INI)
        self.assertEqual(r["a"].inicio_temprano, r["x"].fin_temprano)
        self.assertGreaterEqual(r["b"].fin_temprano, r["a"].inicio_temprano)
        self.assertEqual(r["b"].inicio_temprano, r["a"].inicio_temprano - 1)  # termina justo cuando a arranca

    def test_ancla_contractual(self):
        r = calcular_cpm([_act("a", 2, ancla=date(2025, 6, 18))], [], CAL, self.INI)
        self.assertEqual(r["a"].fecha_inicio, date(2025, 6, 18))

    def test_el_arranque_se_corre_al_primer_dia_habil(self):
        r = calcular_cpm([_act("a", 1)], [], CAL, date(2025, 6, 14))  # sábado
        self.assertEqual(r["a"].fecha_inicio, date(2025, 6, 16))

    def test_el_fin_de_semana_y_el_feriado_mueven_la_fecha_no_el_trabajo(self):
        r = calcular_cpm([_act("a", 3), _act("b", 3)], [Vinculo("a", "b")], CAL, date(2025, 12, 22))
        self.assertEqual(r["a"].fecha_fin, date(2025, 12, 24))
        self.assertEqual(r["b"].fecha_inicio, date(2025, 12, 26))  # el 25 no se trabaja
        self.assertEqual(r["b"].fecha_fin, date(2025, 12, 30))

    def test_plazo_menor_al_fin_da_holgura_negativa(self):
        r = calcular_cpm([_act("a", 5)], [], CAL, self.INI, plazo_dias=4)
        self.assertEqual(r["a"].holgura, -1)
        self.assertTrue(r["a"].es_ruta_critica)
        r = calcular_cpm([_act("a", 5)], [], CAL, self.INI, plazo_dias=8)
        self.assertEqual(r["a"].holgura, 3)
        self.assertFalse(r["a"].es_ruta_critica)

    def test_duracion_fraccionaria_con_paso_de_medio_dia(self):
        medios = Calendario(paso_dias=Fraction(1, 2))
        r = calcular_cpm([_act("a", Fraction(3, 2)), _act("b", Fraction(1, 2))], [Vinculo("a", "b")], medios, self.INI)
        self.assertEqual(r["b"].inicio_temprano, r["a"].fin_temprano)
        self.assertEqual(r.dias_habiles, 2)

    def test_hito_de_duracion_cero(self):
        r = calcular_cpm([_act("a", 2), _act("h", 0)], [Vinculo("a", "h")], CAL, self.INI)
        self.assertEqual(r["h"].fecha_inicio, date(2025, 6, 11))
        self.assertEqual(r["h"].fecha_fin, r["h"].fecha_inicio)

    def test_bloque_como_predecesora_usa_el_minimo_y_el_maximo_de_sus_partidas(self):
        acts = [_act("x", 1), _act("y", 4), _act("bloque", 0, hijos=("x", "y")), _act("s", 1)]
        r = calcular_cpm(acts, [Vinculo("bloque", "s")], CAL, self.INI)
        self.assertEqual(r["bloque"].inicio_temprano, r["x"].inicio_temprano)
        self.assertEqual(r["bloque"].fin_temprano, r["y"].fin_temprano)
        self.assertEqual(r["s"].inicio_temprano, r["y"].fin_temprano)
        self.assertEqual(r["bloque"].holgura, 0)

    def test_bloque_que_contiene_a_su_sucesora_se_lee_sin_ella(self):
        # la losa maciza va «después de lo demás del grupo» (D-443): el acero (4 días) y la propia losa (2)
        acts = [_act("acero", 4), _act("losa", 2), _act("grupo", 0, hijos=("acero", "losa"))]
        r = calcular_cpm(acts, [Vinculo("grupo", "losa")], CAL, self.INI)
        self.assertEqual(r["losa"].inicio_temprano, r["acero"].fin_temprano)
        self.assertEqual(r.ruta_critica, ["acero", "losa"])

    def test_la_gualdra_y_su_losa_no_son_un_ciclo(self):
        # gualdra --FS--> losa maciza, y gualdra --SF--> grupo de la losa (que incluye a la maciza)
        acts = [_act("acero", 3), _act("maciza", 2), _act("grupo", 0, hijos=("acero", "maciza")), _act("gualdra", 1)]
        vincs = [Vinculo("gualdra", "maciza", "FS"), Vinculo("grupo", "gualdra", "SF")]
        r = calcular_cpm(acts, vincs, CAL, self.INI)
        self.assertEqual(r["maciza"].inicio_temprano, r["gualdra"].fin_temprano)
        self.assertGreaterEqual(r["gualdra"].fin_temprano, r["acero"].inicio_temprano)

    def test_ciclo_real_entre_partidas(self):
        with self.assertRaises(CicloError):
            calcular_cpm([_act("a", 1), _act("b", 1)], [Vinculo("a", "b"), Vinculo("b", "a")], CAL, self.INI)

    def test_autovinculo(self):
        with self.assertRaises(CicloError):
            calcular_cpm([_act("a", 1)], [Vinculo("a", "a")], CAL, self.INI)

    def test_la_sucesora_nunca_es_un_bloque(self):
        acts = [_act("x", 1), _act("y", 1), _act("bloque", 0, hijos=("y",))]
        with self.assertRaises(VinculoInvalido):
            calcular_cpm(acts, [Vinculo("x", "bloque")], CAL, self.INI)

    def test_vinculo_con_actividad_desconocida(self):
        with self.assertRaises(VinculoInvalido):
            calcular_cpm([_act("a", 1)], [Vinculo("a", "zzz")], CAL, self.INI)

    def test_tipo_de_vinculo_desconocido(self):
        with self.assertRaises(VinculoInvalido):
            Vinculo("a", "b", "XX")

    def test_acepta_los_nombres_del_enum(self):
        self.assertEqual(Vinculo("a", "b", "fin_inicio").tipo, "FS")
        self.assertEqual(Vinculo("a", "b", "inicio_fin").tipo, "SF")


# --------------------------------------------------------------------------- retraso (D-456, D-457)


class PruebasRetraso(unittest.TestCase):
    CURVA = [0.1, 0.3, 0.6, 0.9, 1.0]

    def test_sin_retraso_si_el_plan_no_va_por_delante(self):
        self.assertEqual(dias_de_atraso(self.CURVA, 2, 0.6), 0)
        self.assertEqual(dias_de_atraso(self.CURVA, 2, 0.7), 0)

    def test_tiempo_ganado(self):
        # hoy es el día 3 (el plan va en 90%); lo ejecutado, 30%, es lo que el plan tenía al cierre del día 1
        self.assertEqual(dias_de_atraso(self.CURVA, 3, 0.3), 2)
        # real desde un día hábil: el plan pasó de 60% a 90% y lo ejecutado se quedó en 60%
        self.assertEqual(dias_de_atraso(self.CURVA, 3, 0.6), 1)

    def test_lo_que_debio_haber_arrancado(self):
        # sin avance, el plan lleva trabajando los días que van desde que arrancó
        self.assertEqual(dias_de_atraso(self.CURVA, 3, 0.0), 4)

    def test_retraso_neto_con_signo(self):
        self.assertAlmostEqual(retraso_neto(0.598, 0.452, 1031772.69), 150640.4, delta=1000)
        self.assertLess(retraso_neto(0.10, 0.30, 1000), 0)  # adelanto


# --------------------------------------------------------------------------- conformidad con los siete programas


class PruebasConformidad(unittest.TestCase):
    """Las cifras publicadas (D-443, D-445, D-460) salen de este mismo libro."""

    @classmethod
    def setUpClass(cls):
        cls.redes = {p: _red(p) for p in PROGRAMAS}

    def libro(self, proto):
        return [v for v, agregado in self.redes[proto][2] if not agregado]

    def test_hay_siete_programas_y_3231_filas(self):
        self.assertEqual(len(PROGRAMAS), 7)
        self.assertEqual(sum(len(f) for f in PROGRAMAS.values()), 3231)

    def test_832_vinculos_en_el_libro_y_dos_que_suma_d460(self):
        self.assertEqual(sum(len(self.libro(p)) for p in PROGRAMAS), 832)
        agregados = [(p, v.sucesora) for p in PROGRAMAS for v, ag in self.redes[p][2] if ag]
        self.assertEqual(sorted(agregados), [("Jade", 1397), ("Rubí", 493)])
        self.assertEqual(len(self.libro("Rubí")), 102)
        self.assertEqual(len(self.redes["Rubí"][2]), 103)
        self.assertEqual(len(self.libro("Jade")), 85)
        self.assertEqual(len(self.redes["Jade"][2]), 86)

    def test_la_mezcla_de_tipos_de_vinculo(self):
        # D-445: 824 holguras de FS (680), SS (91) y FF (53), y 8 SF
        c = Counter(v.tipo for p in PROGRAMAS for v in self.libro(p))
        self.assertEqual((c["FS"], c["SS"], c["FF"], c["SF"]), (680, 91, 53, 8))

    def test_zafiro_tiene_15_vinculos_que_no_se_cumplen(self):
        fechas, bloques, _ = self.redes["Zafiro"]
        malos = vinculos_incumplidos(fechas, self.libro("Zafiro"), CAL, bloques)
        self.assertEqual(len(malos), 15)
        self.assertEqual(Counter(v.tipo for v, _ in malos), Counter({"FS": 10, "SS": 2, "SF": 3}))
        self.assertEqual(sorted(h for v, h in malos if v.tipo == "SF"), [-6, -6, -5])

    def test_zafiro_con_la_ventana_completa_del_bloque_son_18(self):
        # D-442: con la ventana completa del bloque, sin quitar la sucesora
        fechas, bloques, _ = self.redes["Zafiro"]
        cuenta = 0
        for v in self.libro("Zafiro"):
            pred = ventana_de_bloque(bloques[v.predecesora], fechas) if v.predecesora in bloques else fechas.get(v.predecesora)
            suc = fechas.get(v.sucesora)
            if pred and suc and holgura_vinculo(v, pred, suc, CAL) < 0:
                cuenta += 1
        self.assertEqual(cuenta, 18)

    def test_los_otros_seis_programas_cumplen_todos_sus_vinculos(self):
        for p in PROGRAMAS:
            if p == "Zafiro":
                continue
            fechas, bloques, vincs = self.redes[p]
            self.assertEqual(vinculos_incumplidos(fechas, [v for v, _ in vincs], CAL, bloques), [], p)

    def test_ocho_sf_en_el_libro_cinco_se_cumplen_con_holgura_cero(self):
        cumplen = 0
        for p in PROGRAMAS:
            fechas, bloques, _ = self.redes[p]
            for v in self.libro(p):
                if v.tipo != "SF":
                    continue
                pred = ventana_de_bloque(bloques[v.predecesora], fechas, v.sucesora) if v.predecesora in bloques else fechas[v.predecesora]
                h = holgura_vinculo(v, pred, fechas[v.sucesora], CAL)
                if h >= 0:
                    self.assertEqual(h, 0)
                    cumplen += 1
        self.assertEqual(cumplen, 5)

    def test_los_dos_sf_de_d460_se_cumplen_con_holgura_cero(self):
        for p in ("Rubí", "Jade"):
            fechas, bloques, vincs = self.redes[p]
            (v,) = [v for v, ag in vincs if ag]
            pred = ventana_de_bloque(bloques[v.predecesora], fechas, v.sucesora)
            self.assertEqual(holgura_vinculo(v, pred, fechas[v.sucesora], CAL), 0, p)

    def test_39_vinculos_tienen_a_su_sucesora_dentro_del_bloque_y_35_se_cumplen(self):
        total = cumplen = 0
        for p in PROGRAMAS:
            fechas, bloques, _ = self.redes[p]
            for v in self.libro(p):
                if v.predecesora in bloques and v.sucesora in bloques[v.predecesora]:
                    total += 1
                    pred = ventana_de_bloque(bloques[v.predecesora], fechas, v.sucesora)
                    if pred is not None and holgura_vinculo(v, pred, fechas[v.sucesora], CAL) >= 0:
                        cumplen += 1
        self.assertEqual((total, cumplen), (39, 35))

    def _actividades(self, proto):
        fechas, bloques, vincs = self.redes[proto]
        acts = [Actividad(f, Fraction(CAL.n(w.fin) + 1 - CAL.n(w.inicio))) for f, w in fechas.items()]
        usados = {v.predecesora for v, _ in vincs if v.predecesora in bloques}
        acts += [Actividad(b, 0, tuple(d for d in bloques[b] if d in fechas)) for b in usados]
        ids = {a.id for a in acts}
        vv = [v for v, _ in vincs if v.sucesora in fechas and v.predecesora in ids]
        return acts, vv

    def test_zafiro_trae_un_autovinculo_y_el_motor_lo_rechaza(self):
        # D-424: `EST-01151` cita su propia fila; el cargador lo descarta
        acts, vv = self._actividades("Zafiro")
        with self.assertRaises(CicloError):
            calcular_cpm(acts, vv, CAL, date(2025, 6, 9))

    def test_el_plan_que_cumple_sus_vinculos_nunca_arranca_antes_que_el_inicio_temprano(self):
        # Si el plan cumple todos los vínculos, es una solución factible de la red, y el CPM calcula
        # la más temprana: ninguna partida puede arrancar antes en el CPM que en el plan.
        for p in PROGRAMAS:
            if p == "Zafiro":
                continue
            acts, vv = self._actividades(p)
            r = calcular_cpm(acts, vv, CAL, date(2025, 6, 9))
            fechas = self.redes[p][0]
            tarde = [f for f, w in fechas.items() if r[f].inicio_temprano > CAL.n(w.inicio)]
            self.assertEqual(tarde, [], p)
            self.assertLessEqual(r.fin_proyecto, max(CAL.n(w.fin) + 1 for w in fechas.values()), p)
            self.assertTrue(r.ruta_critica, p)
            self.assertTrue(all(r[i].holgura >= 0 for i in r.ruta_critica), p)

    def test_el_oid_identifica_cada_fila_del_libro(self):
        # D-442: el libro trae `Oid` único en las 3,231 filas; el cargador guarda la llave, nunca el número de fila
        oids = [r["oid"] for p in PROGRAMAS for r in PROGRAMAS[p]]
        self.assertEqual(len(oids), 3231)
        self.assertTrue(all(oids))
        self.assertEqual(len(set(oids)), 3231)

    def test_que_calcula_el_cpm_con_la_red_que_hay(self):
        # Con solo la red mínima, el CPM más temprano no reproduce el cierre del plan. Rubí y Jade cierran
        # en 139 días hábiles igual que su plan; los tres de dos plantas calculan 139 contra los 149 del plan
        # (la ventana de la planta alta es decisión de cuadrilla, no precedencia); Plus calcula 81 porque
        # `P16`, el vínculo que une la obra gris con los acabados, no está escrito (déficit 10, D-437).
        # Con `P16` escrito, el CPM de Plus calcularía 135 (prueba siguiente).
        esperado = {  # prototipo: (días del CPM, días del plan, pasos de la ruta crítica)
            "Rubí": (139, 139, 48),
            "Jade": (139, 139, 42),
            "Zafiro Plus": (81, 149, 28),
            "Diamante sin chimenea": (139, 149, 56),
            "Diamante con chimenea": (139, 149, 55),
            "Oro": (139, 149, 55),
        }
        origen = date(2025, 6, 9)
        for p, (cpm, plan, pasos) in esperado.items():
            acts, vv = self._actividades(p)
            r = calcular_cpm(acts, vv, CAL, origen)
            fechas = self.redes[p][0]
            self.assertEqual(r.fin_proyecto - CAL.n(origen), cpm, p)
            self.assertEqual(max(CAL.n(w.fin) + 1 for w in fechas.values()) - CAL.n(origen), plan, p)
            self.assertEqual(len(r.ruta_critica), pasos, p)

    def test_p16_sostiene_el_cierre_de_plus(self):
        # El vínculo que Plus no tiene (vertedero FS+1 tras la boquilla fina interior, déficit 10 en el plan)
        # vale 54 días hábiles al CPM: con él, Plus calcula 135 en vez de 81.
        acts, vv = self._actividades("Zafiro Plus")
        origen = date(2025, 6, 9)
        claves = {int(r["fila"]): r["clave"] for r in PROGRAMAS["Zafiro Plus"]}
        boquilla_pb, vertedero = 978, 1102
        self.assertEqual((claves[boquilla_pb], claves[vertedero]), ("ACA-01060", "ACA-01110"))
        r = calcular_cpm(acts, vv + [Vinculo(boquilla_pb, vertedero, "FS", 1)], CAL, origen)
        self.assertEqual(r.fin_proyecto - CAL.n(origen), 135)


# --------------------------------------------------------------------------- lo que antes vivía solo en los libros de revisión


def _csv(nombre):
    with open(RAIZ / "1-mundo" / "programas" / nombre, encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


class PruebasDatosDelPrograma(unittest.TestCase):
    """Los CSV de `1-mundo/programas/` reemplazan a los libros de Excel de revisión: estas
    pruebas los atan a las cifras que `CONOCIMIENTO.md` §11.14 y `PROGRAMA-CPM.md` publican."""

    def test_la_herencia_de_las_duraciones_es_la_de_d441(self):
        # 2,130 duraciones de los seis derivados: 1,520 heredadas, 132 propias, 478 sin referencia
        c = Counter(r["duracion_origen"] for r in sum((PROGRAMAS[p] for p in PROGRAMAS), []) if r["duracion_origen"])
        self.assertEqual((c["heredada"], c["propia"], c["sin referencia"]), (1520, 132, 478))
        self.assertEqual(sum(c.values()), 2130)
        self.assertFalse([r for r in PROGRAMAS["Zafiro"] if r["duracion_origen"]])  # Zafiro es la referencia

    def test_la_regla_que_programo_cada_partida_de_los_cuatro_de_dos_plantas(self):
        for proto, partidas in {"Zafiro Plus": 388, "Diamante sin chimenea": 377, "Diamante con chimenea": 380, "Oro": 402}.items():
            self.assertEqual(sum(1 for r in PROGRAMAS[proto] if r["regla"]), partidas, proto)
        # los gemelos de Zafiro que citan una fila existen y son de Zafiro
        filas_z = {r["fila"] for r in PROGRAMAS["Zafiro"]}
        citadas = {r["gemelo_zafiro_fila"] for p in PROGRAMAS for r in PROGRAMAS[p] if r["gemelo_zafiro_fila"]}
        self.assertTrue(citadas <= filas_z)

    def test_las_rutas_de_relevos(self):
        rutas = defaultdict(list)
        for r in _csv("RUTAS-DE-RELEVOS.csv"):
            rutas[r["prototipo"]].append(r)
        self.assertEqual({p: len(v) for p, v in rutas.items()},
                         {"Zafiro": 28, "Zafiro Plus": 13, "Diamante sin chimenea": 23, "Diamante con chimenea": 23, "Oro": 23})
        for proto, pasos in rutas.items():
            self.assertEqual([int(r["paso"]) for r in pasos], list(range(1, len(pasos) + 1)), proto)
            for r in pasos:  # la fila citada es la partida: misma clave, mismas fechas
                libro = next(q for q in PROGRAMAS[proto] if q["fila"] == r["fila"])
                self.assertEqual((libro["clave"], libro["inicio"], libro["termino"]), (r["clave"], r["inicio"], r["termino"]), proto)
        # Zafiro: cada relevo arranca el día hábil en que termina el anterior y cubre 138 de 139 días
        z = rutas["Zafiro"]
        self.assertEqual(z[0]["inicio"], "2025-06-09")
        self.assertEqual(z[-1]["termino"], "2025-12-18")
        # los programas de dos plantas cierran el 5-ene-2026 con el último relevo
        for proto in ("Zafiro Plus", "Diamante sin chimenea", "Diamante con chimenea", "Oro"):
            self.assertEqual(rutas[proto][-1]["termino"], "2026-01-05", proto)

    def test_los_quince_incumplidos_de_zafiro_son_los_que_calcula_el_motor(self):
        fechas, bloques, _ = _red("Zafiro")
        libro = [v for v, ag in _red("Zafiro")[2] if not ag]
        malos = vinculos_incumplidos(fechas, libro, CAL, bloques)
        esperados = sorted((int(r["fila_sucesora"]), int(r["fila_predecesora"]), r["tipo"], int(r["holgura"]))
                           for r in _csv("ZAFIRO-15-INCUMPLIDOS.csv"))
        self.assertEqual(len(esperados), 15)
        self.assertEqual(sorted((v.sucesora, v.predecesora, v.tipo, int(h)) for v, h in malos), esperados)

    def test_los_ocho_sf(self):
        sf = _csv("SF-LOS-OCHO.csv")
        self.assertEqual(len(sf), 8)
        self.assertEqual(Counter(r["se_cumple_como_sf"] for r in sf), Counter({"Sí": 5, "No": 3}))
        self.assertEqual(Counter(r["se_cumple_al_reves"] for r in sf), Counter({"Sí": 8}))

    def test_el_catalogo_de_la_red(self):
        cat = _csv("CATALOGO-DE-LA-RED.csv")
        ids = [r["id"] for r in cat]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertEqual(Counter(r["id"][0] + ("X" if r["id"].startswith("PX") else "") for r in cat), Counter({"V": 52, "P": 30, "PX": 4}))
        # los 52 vínculos de Zafiro que se heredan (D-425) llevan uno de los cuatro tipos
        self.assertTrue(all(r["tipo_y_desfase_dias_habiles"][:2] in ("FS", "SS", "FF", "SF") for r in cat if r["id"].startswith("V")))

    def test_la_red_minima_son_18_vinculos_entre_17_bloques_y_partidas(self):
        e = _csv("RED-MINIMA-E01-E18.csv")
        self.assertEqual(len(e), 18)
        self.assertEqual(Counter(r["origen"] for r in e), Counter({"técnica": 14, "decisión": 2, "decisión (contrato terminado)": 2}))
        self.assertEqual({r["holgura_en_zafiro"] for r in e}, {"0"})
        self.assertEqual(len({r["predecesora"] for r in e} | {r["sucesora"] for r in e}), 17)

    def test_quien_pide_mas_cuadrilla(self):
        pid = _csv("PIDEN-MAS-CUADRILLA.csv")
        self.assertEqual(Counter(r["prototipo"] for r in pid),
                         Counter({"Zafiro Plus": 7, "Diamante sin chimenea": 19, "Diamante con chimenea": 18, "Oro": 15}))
        self.assertTrue(all(float(r["veces"]) >= 2 for r in pid))

    def test_los_supuestos_a_validar_son_doce_por_prototipo(self):
        sup = _csv("SUPUESTOS-A-VALIDAR.csv")
        self.assertEqual(Counter(r["prototipo"] for r in sup), Counter({p: 12 for p in ("Zafiro Plus", "Diamante sin chimenea", "Diamante con chimenea", "Oro")}))

    def test_la_segunda_ruta_es_un_borrador(self):
        self.assertEqual(len(_csv("SEGUNDA-RUTA-BORRADOR.csv")), 21)
        self.assertEqual(len(_csv("SEGUNDA-RUTA-LO-QUE-SIGUE.csv")), 9)

    def test_la_red_no_escrita_y_su_motivo(self):
        n = _csv("RED-NO-ESCRITA.csv")
        self.assertEqual(Counter(r["prototipo"] for r in n),
                         Counter({"Zafiro Plus": 14, "Diamante sin chimenea": 23, "Diamante con chimenea": 23, "Oro": 17}))
        # P16 (vertedero tras boquilla fina interior) es el único que no se cumple: déficit 10 en Plus
        no_cumple = [(r["prototipo"], r["id"], r["motivo"]) for r in n if r["estado"] == "no se cumple"]
        self.assertTrue(no_cumple and all(i == "P16" for _, i, _ in no_cumple), no_cumple)

    def test_los_emparejamientos_por_rol_coinciden_con_el_libro_de_los_programas(self):
        pares = _csv("EMPAREJAMIENTOS-POR-ROL.csv")
        self.assertEqual(len(pares), 205)
        self.assertEqual(Counter(r["regla"] for r in pares),
                         Counter({"gemelo por rol": 83, "ventana del bloque (Zafiro)": 76, "gemelo por Clave (otro bloque)": 46}))
        libro = {(p, r["fila"]): r for p in PROGRAMAS for r in PROGRAMAS[p]}
        for r in pares:
            fila = libro[(r["prototipo"], r["fila"])]
            self.assertEqual((fila["clave"], fila["regla"], fila["gemelo_zafiro_fila"]), (r["clave"], r["regla"], r["fila_zafiro"]))
            if r["fila_zafiro"]:  # la regla «ventana del bloque» cita el bloque, no una fila
                self.assertEqual(libro[("Zafiro", r["fila_zafiro"])]["clave"], r["clave_zafiro"])


if __name__ == "__main__":
    unittest.main()
