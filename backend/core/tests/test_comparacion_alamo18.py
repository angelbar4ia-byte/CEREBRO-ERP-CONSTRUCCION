"""
La comparación de `ALAMO 18` contra el Diamante con chimenea (`CONOCIMIENTO.md` §11.11), con los archivos de verdad de `1-mundo/opus/`.

No prueba código nuevo: prueba que lo que el cerebro dice de esa comparación se puede volver a sacar de los archivos que están en el
repo, con el motor que está en el repo. Toda cifra de aquí está en `CONOCIMIENTO.md` §11.8 y §11.11 (las 519 claves, el total de las
ingenierías, la arena) o es lo que se midió al volver a correr la comparación con P-36 cerrada (D-488).

**Lo que el repo tiene y el cerebro cita con otras cifras:** las ingenierías son las **once** de la línea base de §11.8 ($2,604,015.74);
§11.11 trabaja con las doce (la azotea se subió después y no está en el repo). Las claves comparadas son las mismas —519, 361, 29 y
129 salen exactos—; los pesos de ALAMO 18 salen menores (la arena, $48,239.51 y no los $49,755 de §11.11).

Correr con: cd backend && python3 -m unittest discover
"""
import csv
import io
import re
import unittest
from collections import defaultdict
from decimal import Decimal

from core.importacion_opus import armar_arbol, leer_matrices, leer_presupuesto
from core.motor_calculo import explosion

from core.tests.datos_opus import COMPUESTOS, CONCEPTOS, OPUS, PRESUPUESTO, texto

DIAMANTE_CON_CHIMENEA = "CAS-00007"
ARENA_DE_7, ARENA_DE_14 = "PET-00002", "PET-00015"


def _numero(s: str):
    s = s.replace("$", "").replace(",", "").strip()
    return Decimal(s) if s not in ("", "-") else None


def _ingenieria():
    """Las filas de insumo de las once ingenierías: (archivo, concepto, insumo, descripción, unidad, cantidad, pu, importe).
    Una fila de insumo es la que trae clave de insumo, cantidad e importe; el título y el concepto que las agrupa no."""
    filas, archivos = [], sorted((OPUS / "ingenieria-alamo-18").glob("*.csv"))
    for archivo in archivos:
        for r in csv.reader(io.StringIO(archivo.read_text(encoding="utf-8-sig"))):
            if len(r) < 7 or not r[1].strip():
                continue
            cantidad, pu, importe = _numero(r[4]), _numero(r[5]), _numero(r[6])
            if cantidad is not None and importe is not None:
                filas.append((archivo.name, r[0].strip(), r[1].strip(), r[2].strip(), r[3].strip(), cantidad, pu, importe))
    return archivos, filas


class PruebasDeLaComparacion(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.archivos, cls.ing = _ingenieria()
        # lo de ALAMO 18, sumado por clave: la agregación al leer de P-36 (`SUM(cantidad) GROUP BY clave`), sin tocar lo cargado
        cls.alamo = defaultdict(lambda: [Decimal(0), Decimal(0)])
        for f in cls.ing:
            cls.alamo[f[2]][0] += f[5]
            cls.alamo[f[2]][1] += f[7]

        presupuesto = leer_presupuesto(texto(PRESUPUESTO))
        cls.matrices = leer_matrices(texto(CONCEPTOS), texto(COMPUESTOS))
        arbol = armar_arbol(cls.matrices, {c: presupuesto.unidad_de(c) for c in presupuesto.conceptos})
        cap = next(c for c in presupuesto.capitulos() if c.raiz.clave == DIAMANTE_CON_CHIMENEA)
        cls.declarado = cap.raiz.precio_observado
        cls.renglones = [f for f in cap.filas if f.es_concepto]
        # el prototipo, explotado a fondo y con el volumen real de cada renglón (§11.11): una hoja por insumo, sumada por clave
        cls.proto = defaultdict(lambda: [Decimal(0), Decimal(0)])
        for f in cls.renglones:
            if f.clave in arbol.id_de:  # ISN-02061 no tiene matriz y su precio es cero: no suma ni resta
                for hoja in explosion(arbol.id_de[f.clave], arbol.repo, f.cantidad or Decimal(0)):
                    cls.proto[hoja.nodo.clave][0] += hoja.cantidad or Decimal(0)
                    cls.proto[hoja.nodo.clave][1] += hoja.importe

    # ------------------------------------------------------------------ los dos lados, contra lo que el cerebro ya dijo de ellos
    def test_las_once_ingenierias_suman_lo_de_la_linea_base_de_11_8(self):
        self.assertEqual(len(self.archivos), 11)
        self.assertEqual(len(self.ing), 1176)
        self.assertEqual(len(self.alamo), 390)
        self.assertEqual(sum(f[7] for f in self.ing), Decimal("2604015.74"))

    def test_el_prototipo_explotado_a_fondo_cierra_contra_lo_declarado_con_la_diferencia_de_siempre(self):
        self.assertEqual(self.declarado, Decimal("2829925.98"))
        self.assertEqual((len(self.renglones), len({f.clave for f in self.renglones})), (380, 287))
        total = sum(h[1] for h in self.proto.values())
        # §11.11 cita $2,829,933.69; el motor, que redondea cada línea al centavo, da $2,829,933.96 — el redondeo del PU acumulado (D-311)
        self.assertLess(abs(total - self.declarado), Decimal("10"))

    def test_519_claves_361_en_ambos_29_solo_en_alamo_129_solo_en_el_prototipo(self):
        a, p = set(self.alamo), set(self.proto)
        self.assertEqual((len(a | p), len(a & p), len(a - p), len(p - a)), (519, 361, 29, 129))

    # ------------------------------------------------------------------ P-36: agrupar al leer no mueve ninguna cifra
    def test_consolidar_al_leer_no_suma_de_mas_ni_de_menos_y_el_detalle_sigue_ahi(self):
        # la vista consolidada es una agregación del original (CONOCIMIENTO.md §11.11): sumarla es sumar el original
        self.assertEqual(sum(h[1] for h in self.alamo.values()), sum(f[7] for f in self.ing))
        # compras ve una arena de 7 m³ —21.43974 viajes—; costos sigue viendo las 85 líneas de las que salió, sin que nadie las haya tocado
        lineas = [f for f in self.ing if f[2] == ARENA_DE_7]
        self.assertEqual((len(lineas), sum(f[5] for f in lineas)), (85, Decimal("21.43974")))
        self.assertEqual(self.alamo[ARENA_DE_7], [Decimal("21.43974"), Decimal("48239.51")])

    def test_de_361_claves_en_ambos_solo_dos_se_desproporcionan_diez_veces(self):
        grandes = {
            k for k in set(self.alamo) & set(self.proto)
            if max(self.alamo[k][1], self.proto[k][1]) >= 1000 and (
                self.alamo[k][1] >= 10 * self.proto[k][1] or self.proto[k][1] >= 10 * self.alamo[k][1])
        }
        # la arena de 7 m³, y MOA-00214 (un destajo de boquilla de pretil: $1,298.15 contra $120.00)
        self.assertEqual(grandes, {ARENA_DE_7, "MOA-00214"})

    # ------------------------------------------------------------------ la arena: dos camiones, no un problema de profundidad ni de consolidar
    def _citan(self, insumo):
        return sorted({l.padre for l in self.matrices.lineas if l.hijo == insumo})

    def test_el_150x_sobrevive_a_la_explosion_profunda_porque_las_claves_son_dos(self):
        # con el prototipo ya abierto hasta el insumo, la arena de 7 m³ sigue en $332.05 y la de 14 m³ vale $37,862.83 en el prototipo y $0 en la obra
        self.assertEqual(self.proto[ARENA_DE_7][1], Decimal("332.05"))
        self.assertEqual(self.proto[ARENA_DE_14][1], Decimal("37862.83"))
        self.assertNotIn(ARENA_DE_14, self.alamo)
        por_clave = self.alamo[ARENA_DE_7][1] / self.proto[ARENA_DE_7][1]
        self.assertTrue(Decimal("145") < por_clave < Decimal("146"))  # §11.11 dice 150: con la doceava ingeniería, $49,755
        # las recetas del catálogo piden casi siempre la de 14 m³; la obra compró siempre la de 7 m³ (D-310)
        self.assertEqual(self._citan(ARENA_DE_7), ["MEZ-03020"])
        self.assertEqual(self._citan(ARENA_DE_14), ["MEZ-01010", "MEZ-01020", "MEZ-01030", "MEZ-03060", "MEZ-07010"])

    def test_son_dos_camiones_al_mismo_precio_por_metro_cubico(self):
        pu = {l.hijo: (l.unidad.upper(), l.costo) for l in self.matrices.lineas if l.hijo in (ARENA_DE_7, ARENA_DE_14)}
        self.assertEqual(pu, {ARENA_DE_7: ("SERV", Decimal("2250.00")), ARENA_DE_14: ("SERV", Decimal("4500.00"))})
        self.assertEqual(Decimal("2250") / 7, Decimal("4500") / 14)  # $321.43 por m³ en los dos

    def test_leida_en_metros_cubicos_la_arena_de_alamo_es_1_26_veces_la_del_prototipo(self):
        obra = self.alamo[ARENA_DE_7][0] * 7 + self.alamo[ARENA_DE_14][0] * 14
        proto = self.proto[ARENA_DE_7][0] * 7 + self.proto[ARENA_DE_14][0] * 14
        self.assertAlmostEqual(float(obra), 150.08, places=2)
        self.assertAlmostEqual(float(proto), 118.83, places=2)
        self.assertAlmostEqual(float(obra / proto), 1.26, places=2)
        # a igual precio por m³, los pesos dicen lo mismo que los metros
        pesos = (self.alamo[ARENA_DE_7][1] + self.alamo[ARENA_DE_14][1]) / (self.proto[ARENA_DE_7][1] + self.proto[ARENA_DE_14][1])
        self.assertAlmostEqual(float(pesos), float(obra / proto), places=3)

    # ------------------------------------------------------------------ el inventario de camiones del catálogo: la unidad es el viaje, los m³ están en el texto
    def test_los_camiones_del_catalogo_traen_la_unidad_del_viaje_y_los_metros_en_la_descripcion(self):
        vistos = {}
        for l in self.matrices.lineas:
            vistos.setdefault(l.hijo, (l.descripcion, l.unidad.upper()))
        for f in self.ing:
            vistos.setdefault(f[2], (f[3], f[4].upper()))
        con_metros = {k: int(m.group(1)) for k, (d, u) in vistos.items() if u == "SERV" and (m := re.search(r"\b(\d+)\s*M3\b", d, re.I))}
        self.assertEqual(con_metros, {"PET-00002": 7, "PET-00003": 7, "PET-00004": 6, "PET-00007": 14, "PET-00015": 14})
        self.assertEqual(vistos["PET-00069"], ("TEZONTLE ROJO 7 MTS", "SERV"))  # el sexto camión lo escribe «MTS»: ambiguo, se marca


if __name__ == "__main__":
    unittest.main()
