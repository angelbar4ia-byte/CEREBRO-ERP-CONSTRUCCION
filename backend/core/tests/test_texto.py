"""
`core/texto.py` — qué diferencia de texto dispara alerta (§2.7.1) — con las descripciones de verdad de los archivos de OPUS: las 472
de los conceptos del presupuesto y las de los insumos y compuestos de las matrices. Cada propiedad se prueba contra todas, y los
casos concretos que dice el cerebro, a mano.
"""
import re
import unicodedata
import unittest

from core.importacion_opus import leer_matrices, leer_presupuesto
from core.tests.datos_opus import COMPUESTOS, CONCEPTOS, PRESUPUESTO, texto
from core.texto import ALTA, IGUAL, INFORMATIVA, clave_nueva, comparar, nucleo

PRESUPUESTO_LEIDO = leer_presupuesto(texto(PRESUPUESTO))
MATRICES = leer_matrices(texto(CONCEPTOS), texto(COMPUESTOS))
DE_CONCEPTOS = sorted({fs[0].descripcion for fs in PRESUPUESTO_LEIDO.conceptos.values() if fs[0].descripcion})
DE_INSUMOS = sorted({l.descripcion for l in MATRICES.lineas if l.descripcion})
TODAS = DE_CONCEPTOS + DE_INSUMOS


def sin_acentos(t):
    return "".join(c for c in unicodedata.normalize("NFD", t) if not unicodedata.combining(c))


class PruebasTexto(unittest.TestCase):
    def test_hay_descripciones_de_verdad_con_que_probar(self):
        self.assertEqual((len(DE_CONCEPTOS) > 400, len(DE_INSUMOS) > 500), (True, True))
        self.assertGreater(sum(bool(re.search(r"\d", d)) for d in TODAS), 400)

    # ------------------------------------------------------------------ lo cosmético no alerta
    def test_mayusculas_acentos_espacios_y_puntuacion_son_cosmeticos_en_todas(self):
        for d in TODAS:
            puntuacion = re.sub(r",(?=\s)", " ;", re.sub(r"\.(?=\s|$)", " . ", d))  # los puntos y comas que separan, no los decimales
            for variante in (d.lower(), sin_acentos(d), d.upper(), "  " + d.replace(" ", "   ") + " ", puntuacion):
                self.assertEqual(comparar(d, variante).nivel, IGUAL, (d, variante))

    def test_los_conectores_no_son_el_nucleo(self):
        for d in TODAS:
            sin_conectores = re.sub(r"\b(de|del|la|las|el|los|en|y|con|para|por)\s+", "", d, flags=re.IGNORECASE)
            self.assertEqual(comparar(d, sin_conectores).nivel, IGUAL, (d, sin_conectores))
        self.assertEqual(comparar("LOSA DE CIMENTACIÓN", "losa cimentación").nivel, IGUAL)

    def test_el_incluye_del_principio_se_quita(self):
        for d in DE_CONCEPTOS[:200]:
            self.assertEqual(comparar(d, "INCLUYE: " + d).nivel, IGUAL, d)
            self.assertEqual(comparar("Incluye: " + d, d).nivel, IGUAL, d)

    def test_un_plural_es_el_mismo_elemento(self):
        self.assertEqual(comparar("COLOCACIÓN DE BLOQUE DE CONCRETO", "colocación de bloques de concreto").nivel, IGUAL)
        self.assertEqual(comparar("CIMENTACIONES", "cimentacion").nivel, IGUAL)

    # ------------------------------------------------------------------ el orden y los calificativos informan
    def test_las_mismas_palabras_en_otro_orden_solo_informan(self):
        for d in TODAS:
            palabras, numeros = nucleo(d)
            if len(palabras) < 2 or len(set(palabras)) < 2:
                continue
            r = comparar(d, " ".join(reversed(d.split())))
            self.assertIn(r.nivel, (IGUAL, INFORMATIVA), (d, r))
            self.assertNotEqual(r.nivel, ALTA)

    def test_un_calificativo_informa_y_no_alerta(self):
        r = comparar("MURO DE TABIQUE ROJO RECOCIDO", "muro de tabique rojo recocido nuevo")
        self.assertEqual((r.nivel, r.motivo, r.detalle), (INFORMATIVA, "calificativo", "— → nuevo"))

    # ------------------------------------------------------------------ un número o una palabra alertan
    def test_cambiar_un_numero_es_alta_en_toda_descripcion_que_lo_tiene(self):
        con_numero = [d for d in TODAS if re.search(r"\d", d)]
        for d in con_numero:
            nuevo = re.sub(r"\d+", lambda m: str(int(m.group()) + 1), d, count=1)
            r = comparar(d, nuevo)
            self.assertEqual((r.nivel, r.motivo), (ALTA, "numero"), (d, nuevo))

    def test_de_3_00_a_4_20_es_un_cambio_chico_de_texto_y_enorme_de_significado(self):
        r = comparar("LOSA MACIZA ZAFIRO 3.00 (125 M2)", "LOSA MACIZA ZAFIRO 4.20 (125 M2)")
        self.assertEqual((r.nivel, r.motivo, r.detalle), (ALTA, "numero", "3 → 4.2"))

    def test_un_numero_es_un_numero_no_un_texto(self):
        self.assertEqual(comparar("LOSA 3.00", "LOSA 3").nivel, IGUAL)
        self.assertEqual(comparar("TUBO 1,5", "tubo 1.50").nivel, IGUAL)
        self.assertEqual(comparar("CASTILLO 15X30", "castillo 15 x 30").nivel, IGUAL)
        self.assertEqual(comparar("CASTILLO 15X30", "castillo 15x20").nivel, ALTA)

    def test_cambiar_el_verbo_o_el_elemento_es_alta(self):
        r = comparar("COLOCACIÓN DE LOSETA CERÁMICA", "SUMINISTRO DE LOSETA CERÁMICA")
        self.assertEqual((r.nivel, r.motivo, r.detalle), (ALTA, "palabra", "colocacion → suministro"))
        r = comparar("MURO DE TABIQUE 15 CM", "MURO DE BLOCK 15 CM")
        self.assertEqual((r.nivel, r.motivo, r.detalle), (ALTA, "palabra", "tabique → block"))

    def test_cambiarle_la_primera_palabra_a_cualquier_descripcion_real_alerta(self):
        for d in DE_CONCEPTOS:
            palabras, _ = nucleo(d)
            if not palabras or palabras[0] in ("nuevo", "nueva"):
                continue
            partes = d.split()
            nuevo = " ".join(["XYZZY"] + partes[1:]) if partes[0].lower() not in ("de", "del", "la", "el", "los", "las") else d
            if nuevo != d:
                self.assertEqual(comparar(d, nuevo).nivel, ALTA, (d, nuevo))

    # ------------------------------------------------------------------ los sinónimos
    def test_los_sinonimos_del_diccionario_se_igualan_si_se_dan(self):
        self.assertEqual(comparar("FABRICACIÓN DE CASTILLO", "elaboración de castillo").nivel, ALTA)  # sin diccionario no se sabe
        self.assertEqual(comparar("FABRICACIÓN DE CASTILLO", "elaboración de castillo", {"fabricacion": "elaboracion"}).nivel, IGUAL)

    # ------------------------------------------------------------------ la clave nueva
    def test_la_clave_nueva_es_la_siguiente_libre_del_prefijo_con_el_mismo_ancho(self):
        existentes = frozenset(MATRICES.por_padre) | frozenset(PRESUPUESTO_LEIDO.conceptos)
        for clave in sorted(existentes):
            nueva = clave_nueva(clave, existentes)
            if re.fullmatch(r"[A-Z]+-\d+", clave):
                self.assertNotIn(nueva, existentes, clave)
                self.assertEqual((nueva.split("-")[0], len(nueva)), (clave.split("-")[0], len(clave)), clave)
        self.assertEqual(clave_nueva("ZZZ-00001", frozenset()), "ZZZ-00002")
        self.assertEqual(clave_nueva("ACA-01010", frozenset({"ACA-01010", "ACA-02034", "EST-99999"})), "ACA-02035")


if __name__ == "__main__":
    unittest.main()
