"""
La reversión por destajo de `ALAMO 18` (`CONOCIMIENTO.md` §11.9), con los archivos de verdad de `1-mundo/opus/`.

No prueba código nuevo: prueba que lo que el cerebro dice del residuo de la reversión se puede volver a sacar de los archivos que están
en el repo. La ingeniería no trae conceptos: trae, por etapa (`ECO-`), los insumos sumados, y entre ellos los destajos (`MO…`). De cada
destajo se buscan los conceptos del Diamante con chimenea, **en esa misma etapa**, cuya matriz lo lleva; con uno solo, su cantidad es la
del destajo entre el rendimiento. Toda cifra de aquí está en `CONOCIMIENTO.md` §11.9 (los 38 destajos de la cimentación, 32 / 4 / 2) o es
lo que se midió al volver a correrla (D-489).

Correr con: cd backend && python3 -m unittest discover
"""
import csv
import io
import re
import unittest
from collections import defaultdict
from decimal import Decimal

from core.importacion_opus import leer_matrices, leer_presupuesto

from core.tests.datos_opus import COMPUESTOS, CONCEPTOS, OPUS, PRESUPUESTO, texto

DIAMANTE_CON_CHIMENEA = "CAS-00007"
ES_DESTAJO = re.compile(r"MO[A-Z]?-")
CIMENTACION = OPUS / "ingenieria-alamo-18" / "INGENIERIA_-_ALAMO_18_-_CIM.csv"


def _numero(s: str):
    s = s.replace("$", "").replace(",", "").strip()
    return Decimal(s) if s else None


def _insumos_por_etapa(archivo):
    """(etapa, clave, descripción, cantidad, precio) de cada línea de insumo, con la etapa que la encabeza."""
    etapa, filas = None, []
    for r in csv.reader(io.StringIO(archivo.read_text(encoding="utf-8-sig"))):
        if len(r) < 7:
            continue
        if r[0].startswith("ECO-") and not r[1].strip() and r[2].strip():
            etapa = r[0].strip()
        if r[1].strip() and _numero(r[4]) is not None:
            filas.append((etapa, r[1].strip(), r[2].strip(), _numero(r[4]), _numero(r[5])))
    return filas


class PruebasDeLaReversion(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        presupuesto = leer_presupuesto(texto(PRESUPUESTO))
        cls.matrices = leer_matrices(texto(CONCEPTOS), texto(COMPUESTOS))
        cap = next(c for c in presupuesto.capitulos() if c.raiz.clave == DIAMANTE_CON_CHIMENEA)
        por_posicion = {f.posicion: f for f in cap.filas}
        # la cantidad de cada concepto del presupuesto, por etapa: la misma clave está en varias etapas y niveles, y no es la misma fila
        cls.presupuesto = defaultdict(lambda: defaultdict(Decimal))
        for f in cap.filas:
            if not f.es_concepto:
                continue
            ancestro, etapa = f, None
            while ancestro is not None and etapa is None:
                etapa = ancestro.clave if ancestro.clave.startswith("ECO-") else None
                ancestro = por_posicion.get(ancestro.padre)
            cls.presupuesto[etapa][f.clave] += f.cantidad or Decimal(0)
        cls.rendimiento = defaultdict(Decimal)  # (concepto, destajo) → cuánto destajo lleva una unidad del concepto
        cls.citan = defaultdict(list)  # destajo → (padre, origen)
        for l in cls.matrices.lineas:
            cls.citan[l.hijo].append((l.padre, l.origen))
            if l.origen == "Concepto":
                cls.rendimiento[(l.padre, l.hijo)] += l.cantidad

    def clasificar(self, archivo):
        """Cada destajo de la ingeniería, sumado por etapa, con la clase que le toca y sus candidatos."""
        suma, dice = defaultdict(Decimal), {}
        for etapa, clave, descripcion, cantidad, precio in _insumos_por_etapa(archivo):
            if ES_DESTAJO.match(clave):
                suma[(etapa, clave)] += cantidad
                dice[(etapa, clave)] = (descripcion, precio)
        out = {}
        for (etapa, clave), cantidad in suma.items():
            candidatos = sorted({p for p, o in self.citan.get(clave, ()) if o == "Concepto" and p in self.presupuesto.get(etapa, {})})
            de_compuesto = sorted({p for p, o in self.citan.get(clave, ()) if o != "Concepto"})
            presupuestado = sum(self.presupuesto[etapa][c] * self.rendimiento[(c, clave)] for c in candidatos)
            clase = ("unico" if len(candidatos) == 1 else "varios" if candidatos else "compuesto" if de_compuesto else "sin")
            out[clave] = (etapa, clase, candidatos, cantidad, presupuestado, dice[(etapa, clave)])
        return out

    # ------------------------------------------------------------------ §11.9: los 38 destajos de la cimentación
    def test_de_38_destajos_32_tienen_un_candidato_4_varios_1_cae_en_un_compuesto_y_1_no_tiene(self):
        c = self.clasificar(CIMENTACION)
        self.assertEqual(len(c), 38)
        clases = defaultdict(list)
        for clave, (_, clase, *_) in c.items():
            clases[clase].append(clave)
        self.assertEqual({k: len(v) for k, v in clases.items()}, {"unico": 32, "varios": 4, "compuesto": 1, "sin": 1})
        self.assertEqual(clases["compuesto"], ["MOC-12010"])
        self.assertEqual(clases["sin"], ["MOS-2079"])

    def test_los_cuatro_varios_son_sumas_y_cierran_exacto_contra_el_presupuesto(self):
        # la ingeniería suma los insumos de la etapa: un destajo con dos conceptos es lo que hicieron los dos, no uno de los dos
        c = self.clasificar(CIMENTACION)
        varios = {k: (cands, real, esperado) for k, (_, clase, cands, real, esperado, _) in c.items() if clase == "varios"}
        self.assertEqual(varios, {
            "MOS-01030": (["ISN-01111", "ISN-01112"], Decimal("10"), Decimal("10")),  # 9 + 1
            "MOH-01020": (["IHD-01090", "IHD-01100"], Decimal("2"), Decimal("2")),    # 1 + 1
            "MOH-01030": (["IHD-01070", "IHD-01080"], Decimal("4"), Decimal("4")),    # 3 + 1
            "MOE-01101": (["IEC-01020", "IEC-01030"], Decimal("2"), Decimal("2")),    # 1 + 1
        })
        etapa = c["MOS-01030"][0]
        self.assertEqual((self.presupuesto[etapa]["ISN-01111"], self.presupuesto[etapa]["ISN-01112"]), (9, 1))

    def test_el_reparto_de_la_bajada_sanitaria_lo_confirman_cuatro_insumos_que_ningun_destajo_decide(self):
        # 9 y 1 reproducen lo que la ingeniería compró de cuatro materiales; 10 y 0 no reproducen ninguno de los cuatro
        real = defaultdict(Decimal)
        for etapa, clave, _, cantidad, _ in _insumos_por_etapa(CIMENTACION):
            if etapa == "ECO-00002":
                real[clave] += cantidad
        # fuera de las dos bajadas, SAN-00009 lo usa una sola vez más: ISN-02001, 1 en el presupuesto
        resto = {"SAN-00009": self.presupuesto["ECO-00002"]["ISN-02001"] * self._tasa("ISN-02001", "SAN-00009")}

        def esperado(insumo, nueve, uno):
            return (nueve * self._tasa("ISN-01111", insumo) + uno * self._tasa("ISN-01112", insumo) + resto.get(insumo, 0))

        for insumo in ("SAN-00009", "SAN-00017", "SAN-00015", "SAN-00020"):
            self.assertAlmostEqual(float(esperado(insumo, 9, 1)), float(real[insumo]), places=3, msg=insumo)
        malos = [i for i in ("SAN-00009", "SAN-00017", "SAN-00015", "SAN-00020") if abs(esperado(i, 10, 0) - real[i]) < Decimal("0.01")]
        self.assertEqual(malos, [])

    def _tasa(self, concepto, insumo):
        return sum((l.cantidad for l in self.matrices.por_padre[concepto] if l.hijo == insumo), Decimal(0))

    def test_el_destajo_de_la_zapata_vive_en_un_compuesto_y_cae_en_la_losa_de_cimentacion(self):
        # §11.9: «se estaba buscando en la profundidad equivocada». ZA1-000001 lo cita EST-01053 (6 por unidad) y EST-01054, que está en otro nivel
        etapa, clase, _, real, _, _ = self.clasificar(CIMENTACION)["MOC-12010"]
        self.assertEqual(clase, "compuesto")
        citan = {p: l.cantidad for l in self.matrices.lineas if l.hijo == "ZA1-000001" for p in (l.padre,)}
        en_la_etapa = {p: q for p, q in citan.items() if p in self.presupuesto[etapa]}
        self.assertEqual(en_la_etapa, {"EST-01053": Decimal("6")})
        self.assertEqual(self.presupuesto[etapa]["EST-01053"] * en_la_etapa["EST-01053"], real)  # 1 × 6 = 6 zapatas

    # ------------------------------------------------------------------ la clave que no existe, contra lo que falta
    def test_mos_2079_es_el_unico_destajo_que_sobra_y_mos_02020_el_unico_que_falta(self):
        c = self.clasificar(CIMENTACION)
        sobran = [k for k, (_, clase, *_) in c.items() if clase == "sin"]
        # los destajos que el presupuesto de la cimentación pide y la ingeniería no trae
        pide = {l.hijo for etapa in ("ECO-00001", "ECO-00002", "ECO-00003", "ECO-00004", "ECO-00005")
                for concepto in self.presupuesto[etapa] for l in self.matrices.por_padre.get(concepto, ())
                if ES_DESTAJO.match(l.hijo)}
        faltan = sorted(pide - set(c))
        self.assertEqual((sobran, faltan), (["MOS-2079"], ["MOS-02020"]))
        # no es cercanía de claves: es la misma descripción, la misma cantidad y el mismo precio
        etapa, _, _, cantidad, _, (descripcion, precio) = c["MOS-2079"]
        pedido = next(l for l in self.matrices.lineas if l.hijo == "MOS-02020")
        self.assertEqual((descripcion, cantidad, precio), (pedido.descripcion, self.presupuesto[etapa]["ISN-01020"], pedido.costo))
        self.assertEqual((descripcion, cantidad, precio), ("MO SALIDA SAN LAVADERO", Decimal("1"), Decimal("312.50")))

    # ------------------------------------------------------------------ a escala: las once ingenierías
    def test_en_las_once_ingenierias_diez_de_quince_sumas_cierran_exacto_y_cinco_no(self):
        varios = {}
        for archivo in sorted((OPUS / "ingenieria-alamo-18").glob("*.csv")):
            for clave, (etapa, clase, cands, real, esperado, _) in self.clasificar(archivo).items():
                if clase == "varios":
                    varios[(archivo.name, etapa, clave)] = (real, esperado)
        self.assertEqual(len(varios), 15)
        no_cierran = sorted(k[2] for k, (real, esperado) in varios.items() if real != esperado)
        # la losa nervada de Planta Baja (dos hijos, una sola ancla) y el cableado de Planta Alta: lo que la obra hizo de más o de menos
        self.assertEqual(no_cierran, ["MOE-01112", "MOE-01122", "MOE-02211", "MOE-02212", "MOE-02214"])


if __name__ == "__main__":
    unittest.main()
