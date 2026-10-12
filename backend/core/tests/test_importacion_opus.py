"""
La carga desde OPUS, con los archivos de verdad de `1-mundo/opus/` — no con fixtures inventadas.

Toda cifra de este archivo está en `CONOCIMIENTO.md` §2.4 y §2.5 (las 3,231 filas, la tabla de tipos, las 121 filas
placeholder), en `CATALOGOS.md` o en `erp-construccion.md` §2 (CUAD-001: 0.1 de $1,880 son $188), o es lo que se midió en los
archivos al escribir esto. Cuando una prueba necesita un archivo «cambiado», se le cambia una celda a una fila real.

Correr con: cd backend && python3 -m unittest discover
"""
import unittest
from decimal import Decimal

from core.importacion_opus import (
    CargaNoProcede,
    armar_arbol,
    catalogo_leido,
    diagnosticar,
    huella,
    leer_matrices,
    leer_presupuesto,
)
from core.motor_calculo import precio_unitario, reporte_montos

from core.tests.datos_opus import COMPUESTOS, CONCEPTOS, PRESUPUESTO, columna, editar, texto


CONCEPTO_CON_MATRIZ = "EST-01040"  # la losa de cimentación de Zafiro, la primera del presupuesto


class PruebasDelPresupuesto(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.p = leer_presupuesto(texto(PRESUPUESTO))

    # ------------------------------------------------------------------ el mapeo de columnas (§2.4)
    def test_el_informe_dice_que_leyo_que_descarto_y_que_no_reconocio(self):
        i = self.p.informe
        self.assertEqual((i.faltan, i.sin_reconocer), ((), ()))
        self.assertEqual(i.leidas["nivel"], "Nivel ")  # con el espacio que trae el archivo
        # lo que se sabe y no se importa: se genera al exportar, se deriva o viene del APU y del catálogo de conceptos
        self.assertEqual(set(i.descartadas), {"Nivel ERP", "Ingenieria ERP", "%", "Descripción de matriz", "Unidad de matriz",
                                              "Descripcion Corta", "Ruta paramétrica"})

    def test_los_alias_leen_encabezados_con_otro_nombre(self):
        def renombrar(filas):
            nuevos = {"Nivel ": "NIVEL", "Clave": "Código", "Cantidad": "Cant", "Tipo": "Clase"}
            filas[0] = [nuevos.get(c, c) for c in filas[0]]

        otra = leer_presupuesto(editar(texto(PRESUPUESTO), renombrar))
        self.assertEqual([(f.clave, f.nivel, f.cantidad, f.tipo) for f in otra.filas], [(f.clave, f.nivel, f.cantidad, f.tipo) for f in self.p.filas])
        self.assertEqual(otra.informe.leidas["tipo"], "Clase")

    def test_si_falta_una_de_las_cuatro_obligatorias_la_carga_no_procede(self):
        sin_cantidad = editar(texto(PRESUPUESTO), lambda f: f.__setitem__(0, ["Piezas" if c == "Cantidad" else c for c in f[0]]))
        with self.assertRaises(CargaNoProcede) as cm:
            leer_presupuesto(sin_cantidad)
        self.assertEqual(cm.exception.informe.faltan, ("cantidad",))
        self.assertIn("Piezas", cm.exception.informe.sin_reconocer)  # y lo dice: «Piezas» no es nada que se conozca
        self.assertIn("cantidad", str(cm.exception))

    def test_una_obligatoria_repetida_no_se_adivina(self):
        # dos «Tipo»: el caso de `CATALOGO_DE_TRABAJOS` (`CATALOGOS.md` §3), donde hay que leer por posición y no por nombre
        dos_tipos = editar(texto(PRESUPUESTO), lambda f: f.__setitem__(0, ["Tipo" if c == "Origen" else c for c in f[0]]))
        with self.assertRaises(CargaNoProcede) as cm:
            leer_presupuesto(dos_tipos)
        self.assertIn("dos veces", str(cm.exception))

    # ------------------------------------------------------------------ el árbol (§2.4) y los placeholders (§2.5)
    def test_las_3231_filas_son_las_que_se_quedan_mas_los_121_placeholders(self):
        self.assertEqual((len(self.p.filas), len(self.p.descartadas)), (3110, 121))
        self.assertEqual(len(self.p.filas) + len(self.p.descartadas), 3231)
        self.assertTrue(self.p.limpia, self.p.problemas)

    def test_la_tabla_de_tipos_de_conocimiento_sale_de_los_datos(self):
        # CONOCIMIENTO.md §2.4: todo concepto es hoja, todo estructural tiene hijos, salvo 114 «Nivel 3» vacíos
        self.assertEqual(dict(self.p.por_tipo), {
            "Capítulo": (7, 0), "Subcapítulo": (102, 0), "Nivel 2": (325, 0), "Nivel 3": (231, 114), "Concepto": (0, 2452),
        })

    def test_los_121_placeholders_son_los_que_dice_conocimiento(self):
        from collections import Counter

        self.assertEqual(Counter((f.tipo, f.nivel) for f in self.p.descartadas), {("Nivel 3", 3): 107, ("Nivel 2", 2): 7, ("Concepto", 3): 7})
        self.assertTrue(all(not f.clave and not f.descripcion for f in self.p.descartadas))
        # y nada quedó huérfano: todo lo que se queda cuelga de algo que se queda
        quedan = {f.posicion for f in self.p.filas}
        self.assertTrue(all(f.padre is None or f.padre in quedan for f in self.p.filas))

    def test_un_placeholder_con_total_se_queda_y_se_reporta(self):
        def con_total(filas):
            c, t, k, d = (columna(filas, n) for n in ("Total", "Tipo", "Clave", "Descripción"))
            fila = next(f for f in filas[1:] if f[t] == "Nivel 3" and not f[k] and not f[d])
            fila[c] = "1,000.00"

        p = leer_presupuesto(editar(texto(PRESUPUESTO), con_total))
        self.assertEqual(len(p.descartadas), 120)
        (problema,) = p.problemas
        self.assertIn("placeholder", problema)
        self.assertIn("1000.00", problema.replace(",", ""))

    def test_un_placeholder_con_un_descendiente_con_clave_se_queda_y_se_reporta(self):
        def con_hijo_costeado(filas):
            t, k, d = (columna(filas, n) for n in ("Tipo", "Clave", "Descripción"))
            fila = next(f for f in filas[1:] if f[t] == "Concepto" and not f[k] and not f[d])
            fila[k], fila[d] = "ZZZ-00001", "un concepto que apareció donde no debía"

        p = leer_presupuesto(editar(texto(PRESUPUESTO), con_hijo_costeado))
        self.assertEqual(len(p.descartadas), 119)  # ya no es placeholder ni el concepto ni el «Nivel 2» vacío del que cuelga
        (problema,) = p.problemas
        self.assertIn("descendientes con clave", problema)
        self.assertIn("ZZZ-00001", p.conceptos)

    def test_el_indice_es_la_suma_de_control_del_arbol(self):
        def desordenar(filas):
            i, n = columna(filas, "Indice"), columna(filas, "Nivel")
            # dos hermanos seguidos (el 1 y el 2 del mismo nivel): se reordenaron
            k = next(k for k in range(1, len(filas) - 1) if (filas[k][i], filas[k + 1][i]) == ("1", "2") and filas[k][n] == filas[k + 1][n])
            filas[k][i], filas[k + 1][i] = filas[k + 1][i], filas[k][i]

        p = leer_presupuesto(editar(texto(PRESUPUESTO), desordenar))
        self.assertEqual(len(p.problemas), 2)
        self.assertTrue(all("Indice" in x for x in p.problemas))

    def test_el_wbs_se_calcula_por_posicion_y_es_unico(self):
        wbs = [f.wbs for f in self.p.filas]
        self.assertEqual(wbs[:3], ["1", "1.1", "1.1.1"])  # capítulo, subcapítulo, nivel 2
        self.assertEqual(len(set(wbs)), len(wbs))
        self.assertEqual([f.wbs for f in self.p.filas if f.nivel == 0], [str(n) for n in range(1, 8)])  # los siete prototipos
        porcion = {f.wbs: f for f in self.p.filas}
        # cada WBS es el de su padre más un número, y el número es el lugar entre los hermanos que se quedan
        for f in self.p.filas:
            if f.padre is None:
                continue
            padre = next(g for g in self.p.filas if g.posicion == f.padre)
            self.assertTrue(f.wbs.startswith(padre.wbs + "."), f.wbs)
            self.assertIn(padre.wbs, porcion)

    def test_un_concepto_se_repite_pero_con_el_mismo_precio(self):
        self.assertEqual(len(self.p.conceptos), 471)  # claves distintas, entre las 2,452 filas de concepto (menos 7 vacías)
        for clave, filas in self.p.conceptos.items():
            self.assertEqual(len({f.precio_observado for f in filas}), 1, clave)

    def test_las_cantidades_y_los_precios_con_comas_de_miles_se_leen(self):
        capitulo = self.p.filas[0]
        self.assertEqual((capitulo.tipo, capitulo.clave, capitulo.precio_observado), ("Capítulo", "CAS-00004", Decimal("1842426.01")))

    # ------------------------------------------------------------------ lo que no es un archivo de OPUS
    def test_un_numero_con_coma_decimal_no_se_vuelve_otro_numero(self):
        def coma(filas):
            filas[1][columna(filas, "Cantidad")] = "1,5"

        with self.assertRaises(CargaNoProcede) as cm:
            leer_presupuesto(editar(texto(PRESUPUESTO), coma))
        self.assertIn("línea 2", str(cm.exception))
        self.assertIn("1,5", str(cm.exception))

    def test_lo_ilegible_se_dice_con_su_linea(self):
        for contenido, esperado in (("", "vacío"), ("a,b\n1,2\n", "faltan columnas")):
            with self.assertRaises(CargaNoProcede) as cm:
                leer_presupuesto(contenido)
            self.assertIn(esperado, str(cm.exception))

        def nivel_malo(filas):
            filas[5][columna(filas, "Nivel")] = "tres"

        with self.assertRaises(CargaNoProcede) as cm:
            leer_presupuesto(editar(texto(PRESUPUESTO), nivel_malo))
        self.assertIn("línea 6", str(cm.exception))

        def sin_tipo(filas):
            filas[7][columna(filas, "Tipo")] = ""

        with self.assertRaises(CargaNoProcede) as cm:
            leer_presupuesto(editar(texto(PRESUPUESTO), sin_tipo))
        self.assertIn("Tipo", str(cm.exception))

    def test_un_salto_de_nivel_se_reporta(self):
        def saltar(filas):
            filas[2][columna(filas, "Nivel")] = "3"  # un «Nivel 2» que cae de golpe desde el subcapítulo

        p = leer_presupuesto(editar(texto(PRESUPUESTO), saltar))
        self.assertTrue(any("salta del nivel" in x for x in p.problemas))


class PruebasDeLasMatrices(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.m = leer_matrices(texto(CONCEPTOS), texto(COMPUESTOS))

    def test_las_2568_lineas_cuadran_cantidad_por_costo_es_el_importe(self):
        self.assertEqual((len(self.m.lineas), len(self.m.por_padre)), (2568, 596))
        self.assertEqual(self.m.importes_que_no_cuadran, ())

    def test_el_archivo_de_compuestos_ya_venia_dentro_del_de_conceptos(self):
        solo = leer_matrices(texto(CONCEPTOS))
        self.assertEqual(len(solo.lineas), 2568)
        self.assertEqual(self.m.solo_en_compuestos, 0)  # las 267 líneas de COMPUESTOS son las de `Origen = Material`
        self.assertEqual(sum(1 for l in solo.lineas if l.origen == "Material"), 267)

    def test_un_compuesto_que_el_otro_archivo_no_traia_se_agrega(self):
        sin_aux = editar(texto(CONCEPTOS), lambda f: f.__setitem__(slice(None), [r for r in f if r[0] != "AUX-00001"]))
        m = leer_matrices(sin_aux, texto(COMPUESTOS))
        suyas = len(self.m.por_padre["AUX-00001"])
        self.assertGreater(suyas, 1)
        self.assertEqual((m.solo_en_compuestos, len(m.lineas), len(m.por_padre["AUX-00001"])), (suyas, 2568, suyas))  # el otro archivo las devuelve

    def test_quienes_son_los_padres(self):
        self.assertEqual({o: len(self.m.padres_de_origen(o)) for o in ("Concepto", "Material", "ManoDeObra")},
                         {"Concepto": 468, "Material": 89, "ManoDeObra": 39})  # conceptos, compuestos (AUX, MEZ, ZA) y cuadrillas
        self.assertEqual(self.m.padres_de_origen("ManoDeObra")[0], "CUAD-001")

    def test_hay_cantidades_negativas_y_una_linea_de_porcentaje_por_cuadrilla(self):
        self.assertEqual(sum(1 for l in self.m.lineas if l.cantidad < 0), 58)  # los ajustes que descuentan lo ya contado
        porcentajes = [l for l in self.m.lineas if l.es_porcentaje_mo]
        self.assertEqual(len(porcentajes), 39)
        self.assertEqual({l.origen for l in porcentajes}, {"ManoDeObra"})

    def test_un_importe_que_no_es_cantidad_por_costo_se_reporta(self):
        def cambiar(filas):
            filas[10][columna(filas, "Importe")] = "$999,999.00"

        m = leer_matrices(editar(texto(CONCEPTOS), cambiar))
        (mal,) = m.importes_que_no_cuadran
        self.assertEqual(mal.linea, 11)

    def test_un_tipo_que_no_se_conoce_o_una_linea_incompleta_no_cargan(self):
        def tipo(filas):
            filas[3][columna(filas, "Tipo")] = "Herramienta"

        with self.assertRaises(CargaNoProcede) as cm:
            leer_matrices(editar(texto(CONCEPTOS), tipo))
        self.assertIn("línea 4", str(cm.exception))
        self.assertIn("Herramienta", str(cm.exception))

        def sin_costo(filas):
            filas[3][columna(filas, "Costo")] = ""

        with self.assertRaises(CargaNoProcede) as cm:
            leer_matrices(editar(texto(CONCEPTOS), sin_costo))
        self.assertIn("línea 4", str(cm.exception))


class PruebasDelArbolContraElMotor(unittest.TestCase):
    """El motor de cálculo (B-02) estaba probado contra un caso trabajado; aquí, contra los 467 conceptos de verdad."""

    @classmethod
    def setUpClass(cls):
        cls.p = leer_presupuesto(texto(PRESUPUESTO))
        cls.m = leer_matrices(texto(CONCEPTOS), texto(COMPUESTOS))
        cls.a = armar_arbol(cls.m, {c: cls.p.unidad_de(c) for c in cls.p.conceptos})

    def pu(self, clave):
        return precio_unitario(self.a.id_de[clave], self.a.repo)

    def test_no_hay_insumos_con_dos_costos(self):
        self.assertEqual(self.a.problemas, ())  # `MOCA-110` trae 18 costos, pero es el `(%)mo`: su costo es la base de cada cuadrilla

    def test_el_precio_unitario_del_motor_es_el_de_opus_en_los_467_conceptos_al_centavo(self):
        con_matriz = [c for c in self.p.conceptos if c in self.m.por_padre]
        self.assertEqual(len(con_matriz), 467)
        distintos = [(c, self.pu(c), self.p.conceptos[c][0].precio_observado) for c in con_matriz if self.pu(c) != self.p.conceptos[c][0].precio_observado]
        self.assertEqual(distintos, [])

    def test_los_89_compuestos_y_las_39_cuadrillas_cuadran_con_lo_que_dice_el_archivo(self):
        for origen in ("Material", "ManoDeObra"):
            for padre in self.m.padres_de_origen(origen):
                esperado = sum(l.importe for l in self.m.por_padre[padre])
                self.assertAlmostEqual(float(self.pu(padre)), float(esperado), delta=0.01, msg=padre)

    def test_cuad_001_es_el_ejemplo_de_erp_construccion_los_jornales_mas_el_diez_por_ciento(self):
        self.assertEqual(self.pu("CUAD-001"), Decimal("2068.00"))  # 2×560 + 760 = 1,880 de jornales; 0.1 × 1,880 = 188
        (linea,) = [l for l in self.m.por_padre["CUAD-001"] if l.es_porcentaje_mo]
        self.assertEqual((linea.cantidad, linea.costo, linea.importe), (Decimal("0.100000"), Decimal("1880.00"), Decimal("188.00")))

    def test_una_linea_que_cita_un_compuesto_trae_el_costo_que_el_motor_calcula(self):
        citan = [l for l in self.m.lineas if l.hijo in self.m.por_padre and not l.es_porcentaje_mo]
        self.assertEqual(len(citan), 264)
        self.assertEqual([l.linea for l in citan if abs(l.costo - self.pu(l.hijo)) > Decimal("0.01")], [])

    def test_la_lectura_superficial_suma_el_precio_en_las_categorias_de_opus(self):
        for clave in (CONCEPTO_CON_MATRIZ, "ACA-01010", "AUX-00001"):
            montos = reporte_montos(self.a.id_de[clave], self.a.repo)
            self.assertEqual(sum(montos.values()), self.pu(clave), clave)

    def test_los_cuatro_conceptos_sin_matriz_son_los_de_p_09(self):
        self.assertEqual(sorted(catalogo_leido(self.m, self.p).sin_matriz), ["ACC-00003", "IGAS-02131", "IGAS-02132", "ISN-02061"])

    def test_un_insumo_con_dos_costos_distintos_se_dice(self):
        self.assertNotIn("ACE-00001", self.m.por_padre)  # el alambre recocido es un insumo: no tiene matriz propia

        def encarecer(filas):
            h, c = columna(filas, "Clave Hijo"), columna(filas, "Costo")
            fila = next(f for f in filas[1:] if f[h] == "ACE-00001")
            fila[c] = "$99.99"

        m = leer_matrices(editar(texto(CONCEPTOS), encarecer))
        a = armar_arbol(m)
        self.assertEqual(len(a.problemas), 1)
        self.assertIn("ACE-00001", a.problemas[0])


class PruebasDeLaHuellaYElDiagnostico(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.p = leer_presupuesto(texto(PRESUPUESTO))
        cls.m = leer_matrices(texto(CONCEPTOS))
        cls.vigente = catalogo_leido(cls.m, cls.p)

    def nuevo(self, conceptos=None, presupuesto=None):
        m = leer_matrices(conceptos) if conceptos is not None else self.m
        return catalogo_leido(m, leer_presupuesto(presupuesto) if presupuesto is not None else self.p)

    def test_la_huella_no_depende_del_orden_ni_de_los_ceros_ni_de_los_textos_ni_de_los_precios(self):
        lineas = [(l.hijo, l.cantidad) for l in self.m.por_padre[CONCEPTO_CON_MATRIZ]]
        base = huella(lineas)
        self.assertEqual(huella(list(reversed(lineas))), base)
        self.assertEqual(huella([(h, Decimal(str(c)) * Decimal("1.000000")) for h, c in lineas]), base)
        self.assertNotEqual(huella([(lineas[0][0], lineas[0][1] + 1)] + lineas[1:]), base)  # una cantidad sí
        self.assertNotEqual(huella(lineas[1:]), base)  # un insumo menos sí
        self.assertEqual(huella([("a", Decimal("1.050000"))]), huella([("a", Decimal("1.05"))]))
        self.assertNotEqual(huella([("a", Decimal("1")), ("a", Decimal("1"))]), huella([("a", Decimal("1"))]))  # el alambre dos veces

    def test_cambiar_el_texto_o_el_precio_de_una_linea_no_versiona_nada(self):
        def retocar(filas):
            d, c, i = columna(filas, "Descripción"), columna(filas, "Costo"), columna(filas, "Importe")
            for f in filas[1:]:
                if f[0] == CONCEPTO_CON_MATRIZ:
                    f[d], f[c], f[i] = f[d] + " (corregido)", "$1.00", "$1.00"

        d = diagnosticar(self.nuevo(editar(texto(CONCEPTOS), retocar)), self.vigente)
        self.assertEqual((d.versionan, d.detenidos, d.nuevos, d.ausentes), ((), (), (), ()))

    def test_el_mismo_archivo_entra_completo(self):
        d = diagnosticar(self.nuevo(), self.vigente)
        self.assertEqual(len(d.entran), len(self.vigente.huella))
        self.assertEqual((d.versionan, d.detenidos, d.nuevos, d.ausentes), ((), (), (), ()))

    def test_una_cantidad_cambiada_versiona_solo_ese_concepto(self):
        def mas_cemento(filas):
            c = columna(filas, "Cantidad")
            fila = next(f for f in filas[1:] if f[0] == CONCEPTO_CON_MATRIZ)
            fila[c] = str(Decimal(fila[c]) + 1)

        d = diagnosticar(self.nuevo(editar(texto(CONCEPTOS), mas_cemento)), self.vigente)
        self.assertEqual(d.versionan, (CONCEPTO_CON_MATRIZ,))
        self.assertEqual(len(d.entran), len(self.vigente.huella) - 1)

    def test_una_unidad_cambiada_detiene_ese_concepto_y_lo_dice_con_las_dos(self):
        def otra_unidad(filas):
            k, u = columna(filas, "Clave"), columna(filas, "Unidad")
            for f in filas[1:]:
                if f[k] == CONCEPTO_CON_MATRIZ:
                    f[u] = "pza" if f[u].lower() != "pza" else "m2"

        antes = self.p.unidad_de(CONCEPTO_CON_MATRIZ)
        d = diagnosticar(self.nuevo(presupuesto=editar(texto(PRESUPUESTO), otra_unidad)), self.vigente)
        (detenido,) = d.detenidos
        self.assertEqual((detenido.clave, detenido.unidad_vigente), (CONCEPTO_CON_MATRIZ, antes))
        self.assertNotEqual(detenido.unidad_nueva.lower(), antes.lower())
        self.assertEqual((d.versionan, d.nuevos), ((), ()))  # el resto entra normal: se detiene el concepto, no la carga

    def test_un_concepto_que_llega_y_uno_que_ya_no_viene(self):
        def cambiar(filas):
            filas.append(["ZZZ-00001", "MEZ-03010", "MORTERO ESTUCO BLANCO", "M2", "1.000000", "$20.68", "$20.68", "Material", "Concepto"])
            filas[:] = [f for f in filas if f[0] != "ACA-01010"]

        d = diagnosticar(self.nuevo(editar(texto(CONCEPTOS), cambiar)), self.vigente)
        self.assertEqual((d.nuevos, d.ausentes), (("ZZZ-00001",), ("ACA-01010",)))  # lo ausente se avisa, no se borra


if __name__ == "__main__":
    unittest.main()
