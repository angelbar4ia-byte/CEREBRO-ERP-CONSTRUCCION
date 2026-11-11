"""
Las tablas que el usuario comparte, a salvo (D-479): lo guardado en el repo está completo y sin cambios, y guardar una subida hace lo que dice.
Las pruebas parten de las tablas de verdad —las de `1-mundo/opus/` y `1-mundo/fuentes/`— y les tocan lo que cada caso necesita.
"""
import csv
import shutil
import tempfile
import unittest
from pathlib import Path

try:
    import openpyxl

    HAY_OPENPYXL = True
except ImportError:  # pragma: no cover
    HAY_OPENPYXL = False

from core.fuentes import (
    MANIFIESTO,
    OTRAS,
    _hojas_a_csv,
    carpeta_de,
    guardar_subidas,
    leer_manifiesto,
    nombre_limpio,
    sha256_de,
    verificar,
)

RAIZ = Path(__file__).resolve().parents[3]

# lo que el usuario subió, con el nombre que le puso: (carpeta, hojas, registros de la primera hoja, con el encabezado)
LIBROS = {
    "03_MARZO_MOVIMIENTOS_DE_ALMACEN.xlsx": ("almacen", 1, 5023), "04_ABRIL_MOVIMIENTOS_DE_ALMACEN.xlsx": ("almacen", 1, 4446),
    "05_MAYO_MOVIMIENTOS_DE_ALMACEN.xlsx": ("almacen", 1, 4741), "06_JUNIO_MOVIMIENTOS_DE_ALMACEN.xlsx": ("almacen", 1, 4534),
    "07_JULIO_MOVIMIENTOS_DE_ALMACEN.xlsx": ("almacen", 1, 4336),
    "grid_AvanceOPEventosOpr_MARZO.xlsx": ("avance", 1, 212), "grid_AvanceOPEventosOpr_28.xlsx": ("avance", 1, 417),
    "grid_AvanceOPEventosOpr_MAYO.xlsx": ("avance", 1, 483), "grid_AvanceOPEventosOpr_JUNIO.xlsx": ("avance", 1, 679),
    "grid_AvanceOPEventosOpr_JULIO.xlsx": ("avance", 1, 1144),
    "PRECIO_REAL_ALAMO_18.xlsx": ("precio-real", 9, 6), "PRECIO_REAL_ALAMO_18__2.xlsx": ("precio-real", 9, 6),
    "SEMILLA-cuadrilla-rendimiento.xlsx": ("semilla", 1, 266), "PROGRAMA_ZAFIRO.xlsx": ("programa", 2, 3232),
}
CSV_DE_OPUS = {"CATALOGO_DE_PRESUPUESTO.csv": 3232, "ANALISIS_DE_BASICOS_CONCEPTOS.csv": 2569, "ANALISIS_DE_BASICOS_COMPUESTOS.csv": 268}


class PruebasDeLoGuardado(unittest.TestCase):
    """Sobre el repositorio de verdad: si alguien borra o toca una tabla compartida, esto falla."""

    @classmethod
    def setUpClass(cls):
        cls.filas = {r.ruta: r for r in leer_manifiesto(RAIZ)}

    def test_todo_lo_compartido_sigue_ahi_sin_cambios(self):
        self.assertEqual(verificar(RAIZ), [])

    def test_estan_los_36_archivos_que_el_usuario_subio(self):
        subidos = [nombre_limpio(r.subido_como) for r in self.filas.values() if r.subido_como]
        self.assertEqual(len(subidos), 36)  # los 28 de D-479, los cuatro catálogos de OPUS en Excel de D-527, el de trabajos de D-528 y los tres del catálogo paramétrico
        self.assertEqual(len(set(subidos)), 35)  # `PRECIO_REAL_ALAMO_18.xlsx` se subió dos veces, con otro contenido
        for libro in ("03_MARZO_MOVIMIENTOS_DE_ALMACEN.xlsx", "07_JULIO_MOVIMIENTOS_DE_ALMACEN.xlsx", "PROGRAMA_ZAFIRO.xlsx", "SEMILLA-cuadrilla-rendimiento.xlsx",
                      "PRECIO_REAL_ALAMO_18.xlsx", "grid_AvanceOPEventosOpr_28.xlsx", "CATALOGO_DE_PRESUPUESTO.csv", "INGENIERIA_-_ALAMO_18__-_PB.csv"):
            self.assertIn(libro, subidos)
        self.assertEqual(sum(1 for r in self.filas.values() if r.ruta.endswith(".xlsx") and "/parametricos/" not in r.ruta), 19)
        self.assertEqual(sum(1 for r in self.filas.values() if r.subido_como and r.ruta.endswith(".csv")), 14)
        self.assertEqual(sum(1 for r in self.filas.values() if r.ruta.startswith("1-mundo/opus/ingenieria-alamo-18/")), 11)

    def test_cada_libro_esta_en_su_carpeta_y_cada_hoja_tiene_su_csv(self):
        for nombre, (tema, hojas, registros) in LIBROS.items():
            libro = self.filas[f"1-mundo/fuentes/{tema}/{nombre}"]
            hijos = sorted((r for r in self.filas.values() if r.derivado_de.startswith(libro.ruta + " :: ")), key=lambda r: r.ruta)
            self.assertEqual(len(hijos), hojas, nombre)
            if nombre.startswith("PRECIO_REAL"):
                self.assertEqual({h.derivado_de.split(" :: ")[1] for h in hijos}, {
                    "Resumen", "Mano de Obra", "Materiales", "Subcontratos", "Consolidado Materiales", "Consolidado MO", "Consolidado MO por ID",
                    "Consolidado Materiales x Motivo", "Resumen MO-ID y Mat-Motivo"})
            else:
                self.assertEqual(next(h for h in hijos if h.derivado_de.endswith((":: Consulta", ":: Semilla", ":: Hoja1"))).registros, registros, nombre)

    def test_las_dos_versiones_de_precio_real_se_distinguen(self):
        v1, v2 = (self.filas[f"1-mundo/fuentes/precio-real/PRECIO_REAL_ALAMO_18{s}.xlsx"] for s in ("", "__2"))
        self.assertLess(v1.bytes, v2.bytes)  # la primera que subió, la chica; la segunda, la completa
        self.assertLess(v1.subido_el, v2.subido_el)
        self.assertNotEqual(v1.sha256, v2.sha256)
        self.assertEqual(self.filas["1-mundo/fuentes/precio-real/PRECIO_REAL_ALAMO_18__2/Mano_de_Obra.csv"].registros, 194)
        self.assertEqual(self.filas["1-mundo/fuentes/precio-real/PRECIO_REAL_ALAMO_18/Mano_de_Obra.csv"].registros, 33)

    def test_los_csv_de_opus_siguen_siendo_los_que_se_subieron(self):
        for nombre, registros in CSV_DE_OPUS.items():
            r = self.filas[f"1-mundo/opus/{nombre}"]
            self.assertEqual(r.registros, registros, nombre)
            self.assertEqual(sha256_de(RAIZ / r.ruta), r.sha256)

    @unittest.skipUnless(HAY_OPENPYXL, "falta openpyxl")
    def test_cada_csv_es_lo_que_su_hoja_muestra(self):
        # los libros paramétricos solo guardan fórmulas (sin valores calculados): no tienen CSV por hoja
        for libro in [r for r in self.filas.values() if r.ruta.endswith(".xlsx") and "/parametricos/" not in r.ruta]:
            hojas = _hojas_a_csv(RAIZ / libro.ruta)
            hijos = {r.derivado_de.split(" :: ")[1]: r for r in self.filas.values() if r.derivado_de.startswith(libro.ruta + " :: ")}
            self.assertEqual({h for h, _, _ in hojas}, set(hijos), libro.ruta)
            for hoja, texto, registros in hojas:
                self.assertEqual(hijos[hoja].registros, registros, (libro.ruta, hoja))
                self.assertEqual((RAIZ / hijos[hoja].ruta).read_text(encoding="utf-8"), texto, (libro.ruta, hoja))


class PruebasDeNombresYCarpetas(unittest.TestCase):
    def test_el_prefijo_de_la_plataforma_se_quita_y_nada_mas(self):
        self.assertEqual(nombre_limpio("6fa61918-04_ABRIL_MOVIMIENTOS_DE_ALMACEN.xlsx"), "04_ABRIL_MOVIMIENTOS_DE_ALMACEN.xlsx")
        self.assertEqual(nombre_limpio("04_ABRIL_MOVIMIENTOS_DE_ALMACEN.xlsx"), "04_ABRIL_MOVIMIENTOS_DE_ALMACEN.xlsx")
        self.assertEqual(nombre_limpio("0e98db92-ANALISIS_DE_BASICOS_COMPUESTOS.csv"), "ANALISIS_DE_BASICOS_COMPUESTOS.csv")
        self.assertEqual(nombre_limpio("abcdefgh-mi-tabla.csv"), "abcdefgh-mi-tabla.csv")  # no es hexadecimal: es parte del nombre

    def test_cada_tabla_va_a_su_carpeta(self):
        casos = {
            "CATALOGO_DE_PRESUPUESTO.csv": "1-mundo/opus", "ANALISIS_DE_BASICOS_CONCEPTOS.csv": "1-mundo/opus",
            "INGENIERIA_-_ALAMO_18__-_PB.csv": "1-mundo/opus/ingenieria-alamo-18",
            "03_MARZO_MOVIMIENTOS_DE_ALMACEN.xlsx": "1-mundo/fuentes/almacen", "grid_AvanceOPEventosOpr_JULIO.xlsx": "1-mundo/fuentes/avance",
            "PRECIO_REAL_ALAMO_18.xlsx": "1-mundo/fuentes/precio-real", "SEMILLA-cuadrilla-rendimiento.xlsx": "1-mundo/fuentes/semilla",
            "PROGRAMA_ZAFIRO.xlsx": "1-mundo/fuentes/programa", "CATALOGO_DE_MATERIALES.csv": "1-mundo/opus", "CATALOGO_DE_MANO_DE_OBRA.xlsx": "1-mundo/opus", "algo-nuevo.xlsx": OTRAS,
        }
        for nombre, carpeta in casos.items():
            self.assertEqual(carpeta_de(nombre), carpeta, nombre)


@unittest.skipUnless(HAY_OPENPYXL, "falta openpyxl")
class PruebasDeGuardar(unittest.TestCase):
    """Guardar una subida, con tablas de verdad: una semilla de cuadrillas (un libro de una hoja) y el precio real (uno de nueve)."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="fuentes_"))
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.raiz, self.subidas = self.tmp / "repo", self.tmp / "subidas"
        self.raiz.mkdir()
        self.subidas.mkdir()
        self.semilla = RAIZ / "1-mundo/fuentes/semilla/SEMILLA-cuadrilla-rendimiento.xlsx"
        self.precio = RAIZ / "1-mundo/fuentes/precio-real/PRECIO_REAL_ALAMO_18__2.xlsx"
        self.corta = RAIZ / "1-mundo/opus/ingenieria-alamo-18/INGENIERIA_-_ALAMO_18__-_CENTRO_DE_CARGA.csv"

    def sube(self, origen, como):
        shutil.copyfile(origen, self.subidas / como)

    def test_guarda_el_original_igual_quita_el_prefijo_y_hace_un_csv_por_hoja(self):
        self.sube(self.semilla, "800bcfb7-SEMILLA-cuadrilla-rendimiento.xlsx")
        self.sube(self.precio, "4446a559-PRECIO_REAL_ALAMO_18.xlsx")
        self.sube(self.corta, "0983bd6c-INGENIERIA_-_ALAMO_18__-_CENTRO_DE_CARGA.csv")
        g = guardar_subidas(self.subidas, self.raiz)
        libro = self.raiz / "1-mundo/fuentes/semilla/SEMILLA-cuadrilla-rendimiento.xlsx"
        self.assertEqual(sha256_de(libro), sha256_de(self.semilla))  # byte por byte
        self.assertEqual((self.raiz / "1-mundo/fuentes/semilla/SEMILLA-cuadrilla-rendimiento.csv").read_text(encoding="utf-8"),
                         (RAIZ / "1-mundo/fuentes/semilla/SEMILLA-cuadrilla-rendimiento.csv").read_text(encoding="utf-8"))
        hojas = sorted(p.name for p in (self.raiz / "1-mundo/fuentes/precio-real/PRECIO_REAL_ALAMO_18").glob("*.csv"))
        self.assertEqual(len(hojas), 9)
        self.assertIn("Mano_de_Obra.csv", hojas)
        self.assertEqual(sha256_de(self.raiz / "1-mundo/opus/ingenieria-alamo-18/INGENIERIA_-_ALAMO_18__-_CENTRO_DE_CARGA.csv"), sha256_de(self.corta))
        self.assertEqual(len(g.nuevos), 1 + 1 + 1 + 9 + 1)
        self.assertEqual(verificar(self.raiz), [])
        filas = {r.ruta: r for r in leer_manifiesto(self.raiz)}
        r = filas["1-mundo/fuentes/semilla/SEMILLA-cuadrilla-rendimiento.xlsx"]
        self.assertEqual((r.subido_como, r.bytes, r.registros, r.derivado_de), ("800bcfb7-SEMILLA-cuadrilla-rendimiento.xlsx", self.semilla.stat().st_size, None, ""))
        self.assertEqual(filas["1-mundo/fuentes/semilla/SEMILLA-cuadrilla-rendimiento.csv"].derivado_de,
                         "1-mundo/fuentes/semilla/SEMILLA-cuadrilla-rendimiento.xlsx :: Semilla")

    def test_volver_a_guardar_lo_mismo_no_escribe_nada(self):
        self.sube(self.semilla, "800bcfb7-SEMILLA-cuadrilla-rendimiento.xlsx")
        guardar_subidas(self.subidas, self.raiz)
        antes = (self.raiz / MANIFIESTO).read_bytes()
        self.sube(self.semilla, "99999999-SEMILLA-cuadrilla-rendimiento.xlsx")  # subida otra vez, con otro prefijo
        g = guardar_subidas(self.subidas, self.raiz)
        self.assertEqual((g.nuevos, len(g.ya_estaban)), ((), 2))
        self.assertEqual((self.raiz / MANIFIESTO).read_bytes(), antes)
        self.assertEqual(len(list((self.raiz / "1-mundo/fuentes/semilla").iterdir())), 2)

    def test_el_mismo_nombre_con_otro_contenido_es_otra_version_y_la_anterior_se_queda(self):
        self.sube(self.semilla, "800bcfb7-SEMILLA-cuadrilla-rendimiento.xlsx")
        guardar_subidas(self.subidas, self.raiz)
        # la misma tabla con una celda cambiada, subida después
        wb = openpyxl.load_workbook(self.semilla)
        ws = wb.worksheets[0]
        ws.cell(row=2, column=1).value = "CAMBIADA"
        nueva = self.subidas / "aaaaaaaa-SEMILLA-cuadrilla-rendimiento.xlsx"
        wb.save(nueva)
        import os, time
        os.utime(nueva, (time.time() + 60, time.time() + 60))
        g = guardar_subidas(self.subidas, self.raiz)
        self.assertEqual(g.nuevos[0], "1-mundo/fuentes/semilla/SEMILLA-cuadrilla-rendimiento__2.xlsx")
        self.assertEqual(sha256_de(self.raiz / "1-mundo/fuentes/semilla/SEMILLA-cuadrilla-rendimiento.xlsx"), sha256_de(self.semilla))  # la primera, intacta
        self.assertIn("CAMBIADA", (self.raiz / "1-mundo/fuentes/semilla/SEMILLA-cuadrilla-rendimiento__2.csv").read_text(encoding="utf-8"))
        self.assertNotIn("CAMBIADA", (self.raiz / "1-mundo/fuentes/semilla/SEMILLA-cuadrilla-rendimiento.csv").read_text(encoding="utf-8"))
        self.assertEqual(verificar(self.raiz), [])

    def test_lo_que_ya_estaba_en_el_repo_solo_se_registra(self):
        # una tabla guardada antes de que hubiera manifiesto: no se duplica con «__2»
        destino = self.raiz / "1-mundo/opus/ingenieria-alamo-18/INGENIERIA_-_ALAMO_18__-_CENTRO_DE_CARGA.csv"
        destino.parent.mkdir(parents=True)
        shutil.copyfile(self.corta, destino)
        self.sube(self.corta, "0983bd6c-INGENIERIA_-_ALAMO_18__-_CENTRO_DE_CARGA.csv")
        g = guardar_subidas(self.subidas, self.raiz)
        self.assertEqual(g.nuevos, ("1-mundo/opus/ingenieria-alamo-18/INGENIERIA_-_ALAMO_18__-_CENTRO_DE_CARGA.csv",))
        self.assertEqual(len(list(destino.parent.iterdir())), 1)
        self.assertEqual(verificar(self.raiz), [])

    def test_verificar_dice_lo_que_falta_lo_que_cambio_y_lo_que_no_conoce(self):
        self.sube(self.semilla, "800bcfb7-SEMILLA-cuadrilla-rendimiento.xlsx")
        self.sube(self.corta, "0983bd6c-INGENIERIA_-_ALAMO_18__-_CENTRO_DE_CARGA.csv")
        guardar_subidas(self.subidas, self.raiz)
        self.assertEqual(verificar(self.raiz), [])
        csv_ = self.raiz / "1-mundo/fuentes/semilla/SEMILLA-cuadrilla-rendimiento.csv"
        otro = self.raiz / "1-mundo/opus/ingenieria-alamo-18/INGENIERIA_-_ALAMO_18__-_CENTRO_DE_CARGA.csv"
        libro = self.raiz / "1-mundo/fuentes/semilla/SEMILLA-cuadrilla-rendimiento.xlsx"
        csv_.unlink()  # se perdió
        otro.write_text(otro.read_text(encoding="utf-8") + "\n", encoding="utf-8")  # se tocó
        (self.raiz / "1-mundo/fuentes/semilla/otra.csv").write_text("a,b\n1,2\n", encoding="utf-8")  # llegó sin registrarse
        (self.raiz / "1-mundo/opus/CATALOGO_DE_MATERIALES.csv").write_text("a,b\n1,2\n", encoding="utf-8")  # también en la carpeta de OPUS
        (self.raiz / "1-mundo/fuentes/notas").mkdir()
        (self.raiz / "1-mundo/fuentes/notas/lo-que-leimos.txt").write_text("una nota, no una tabla\n", encoding="utf-8")  # una nota no cuenta
        libro_bytes = libro.read_bytes()
        p = verificar(self.raiz)
        self.assertEqual(len(p), 4, p)
        self.assertTrue(any("CATALOGO_DE_MATERIALES.csv: está en el repo y el manifiesto no lo conoce" in x for x in p))
        self.assertTrue(any("SEMILLA-cuadrilla-rendimiento.csv: falta" in x for x in p))
        self.assertTrue(any("CENTRO_DE_CARGA.csv: cambió" in x for x in p))
        self.assertTrue(any("otra.csv: está en el repo y el manifiesto no lo conoce" in x for x in p))
        libro.write_bytes(libro_bytes[:-1] + bytes([libro_bytes[-1] ^ 1]))  # un solo bit distinto, del mismo tamaño
        self.assertTrue(any("SEMILLA-cuadrilla-rendimiento.xlsx: cambió" in x for x in verificar(self.raiz)))

    def test_un_csv_con_registros_de_mas_o_de_menos_no_cuadra(self):
        self.sube(self.corta, "0983bd6c-INGENIERIA_-_ALAMO_18__-_CENTRO_DE_CARGA.csv")
        guardar_subidas(self.subidas, self.raiz)
        filas = leer_manifiesto(self.raiz)
        from core.fuentes import escribir_manifiesto
        from dataclasses import replace
        escribir_manifiesto(self.raiz, [replace(f, registros=f.registros + 1) for f in filas])
        self.assertTrue(any("registros y el manifiesto dice" in x for x in verificar(self.raiz)))

    def test_una_ruta_dos_veces_en_el_manifiesto_se_dice(self):
        self.sube(self.corta, "0983bd6c-INGENIERIA_-_ALAMO_18__-_CENTRO_DE_CARGA.csv")
        guardar_subidas(self.subidas, self.raiz)
        from core.fuentes import escribir_manifiesto
        filas = leer_manifiesto(self.raiz)
        escribir_manifiesto(self.raiz, filas + filas[:1])
        self.assertEqual(sum("está dos veces en el manifiesto" in x for x in verificar(self.raiz)), 1)

    def test_sin_manifiesto_no_hay_nada_a_salvo(self):
        self.assertEqual(verificar(self.raiz), ["no hay manifiesto de las tablas compartidas"])

    def test_un_csv_derivado_de_un_libro_que_no_esta_se_dice(self):
        self.sube(self.semilla, "800bcfb7-SEMILLA-cuadrilla-rendimiento.xlsx")
        guardar_subidas(self.subidas, self.raiz)
        filas = [f for f in leer_manifiesto(self.raiz) if not f.ruta.endswith(".xlsx")]
        from core.fuentes import escribir_manifiesto
        escribir_manifiesto(self.raiz, filas)
        p = verificar(self.raiz)
        self.assertTrue(any("sale de 1-mundo/fuentes/semilla/SEMILLA-cuadrilla-rendimiento.xlsx, que el manifiesto no tiene" in x for x in p), p)
        self.assertTrue(any("SEMILLA-cuadrilla-rendimiento.xlsx: está en el repo y el manifiesto no lo conoce" in x for x in p), p)


if __name__ == "__main__":
    unittest.main()
