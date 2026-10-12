"""
Clonar un insumo contra un Postgres de verdad (`pgserver`), con los tres archivos de OPUS de verdad: el mismo contrato que la memoria
(`core/tests/contrato_clonacion.py`) y lo que solo la base garantiza — que un clon no se reescriba ni se borre (lo único que cambia es que
alguien autorice dejar de exportar la clave vieja, y no se vuelve a abrir), que se lleve a lo sumo un original, que solo *sustituir*
reconozca la clave vieja, y que la categoría de un compuesto de material sea la de un material. Se salta si faltan `pgserver` y `psycopg`.
"""
import shutil
import tempfile
import unittest

try:
    import pgserver
    import psycopg

    HAY_POSTGRES = True
except ImportError:  # pragma: no cover
    HAY_POSTGRES = False

from core.tests.contrato_clonacion import CO, QUIEN, TRABE, ContratoClonacion

if HAY_POSTGRES:
    from infra.postgres_catalogo import PostgresCatalogo
    from infra.postgres_programa import aplicar_migraciones

TABLAS = "carga, presupuesto, nodo, unidad, version_concepto, composicion, precio_historico, programa"


@unittest.skipUnless(HAY_POSTGRES, "faltan pgserver y psycopg")
class PruebasPostgres(ContratoClonacion, unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.dir = tempfile.mkdtemp(prefix="pg_clonacion_")
        cls.servidor = pgserver.get_server(cls.dir)
        cls.conn = psycopg.connect(cls.servidor.get_uri(), autocommit=True)
        aplicar_migraciones(cls.conn)

    @classmethod
    def tearDownClass(cls):
        cls.conn.close()
        cls.servidor.cleanup()
        shutil.rmtree(cls.dir, ignore_errors=True)

    def nuevo_repositorio(self):
        self.conn.execute(f"TRUNCATE {TABLAS} RESTART IDENTITY CASCADE")
        return PostgresCatalogo(self.conn)

    def fila_del_clon(self):
        return self.conn.execute("SELECT id, original_id, clon_id, modo, exporta_clave_vieja FROM clon").fetchone()

    # ------------------------------------------------------------------ lo que solo la base garantiza
    def test_un_clon_no_se_reescribe_ni_se_borra_y_solo_se_cierra_la_exportacion(self):
        self.sustituir()
        id_, original, clon, modo, exporta = self.fila_del_clon()
        self.assertTrue(exporta)
        for sql in ("DELETE FROM clon", "UPDATE clon SET modo = 'mantener'", "UPDATE clon SET reconoce_clave_vieja_al_importar = false",
                    "UPDATE clon SET usuario = 'otro@obra.mx'", "UPDATE clon SET resumen = '{}'",
                    "UPDATE clon SET exporta_clave_vieja = false, usuario = 'otro@obra.mx'"):
            with self.assertRaises(psycopg.errors.RaiseException, msg=sql):
                self.conn.execute(sql)
        self.assertEqual(self.fila_del_clon(), (id_, original, clon, modo, True))
        # dejar de exportar la clave vieja se autoriza una vez y no se vuelve a abrir
        self.conn.execute("UPDATE clon SET exporta_clave_vieja = false")
        self.assertFalse(self.fila_del_clon()[4])
        with self.assertRaises(psycopg.errors.RaiseException):
            self.conn.execute("UPDATE clon SET exporta_clave_vieja = true")
        self.assertFalse(self.fila_del_clon()[4])
        self.assertEqual(self.repo.clones()[0].exporta_clave_vieja, False)
        # y la clave vieja deja de ser una cuestión de la carga: el archivo la sigue leyendo como el clon
        self.assertEqual(self.repo.estado_vigente().homologaciones, {TRABE: "PRE-00120"})

    def test_el_clon_nace_de_un_original_y_solo_sustituir_reconoce_la_clave_vieja(self):
        self.sc.clonar(TRABE, "PRE-00120", "mantener", CO, QUIEN)
        _, original, clon, _, _ = self.fila_del_clon()
        carga = self.conn.execute("SELECT max(id) FROM carga").fetchone()[0]
        otro = self.conn.execute("SELECT id FROM nodo WHERE clave = 'AUX-00005' AND rol <> 'estructural'").fetchone()[0]
        insert = ("INSERT INTO clon (original_id, clon_id, modo, reconoce_clave_vieja_al_importar, usuario, rol, carga_id, resumen)"
                  " VALUES (%s, %s, %s, %s, 'x', 'y', %s, '{}')")
        with self.assertRaises(psycopg.errors.UniqueViolation):  # un clon nace de un solo original
            self.conn.execute(insert, (otro, clon, "mantener", False, carga))
        with self.assertRaises(psycopg.errors.CheckViolation):  # mantener no reconoce nada: el original sigue siendo él
            self.conn.execute(insert, (otro, otro, "sustituir", True, carga))
        with self.assertRaises(psycopg.errors.CheckViolation):
            self.conn.execute(insert, (original, otro, "mantener", True, carga))
        with self.assertRaises(psycopg.errors.CheckViolation):
            self.conn.execute(insert, (original, otro, "duplicar", False, carga))
        with self.assertRaises(psycopg.errors.CheckViolation):
            self.conn.execute("INSERT INTO clon (original_id, clon_id, modo, reconoce_clave_vieja_al_importar, usuario, rol, carga_id, resumen)"
                              " VALUES (%s, %s, 'mantener', false, '', 'y', %s, '{}')", (original, otro, carga))
        self.assertEqual(self.conn.execute("SELECT count(*) FROM clon").fetchone()[0], 1)

    def test_el_clon_guarda_su_procedencia_y_la_carga_es_de_clonacion(self):
        _, r = self.sustituir()
        self.assertEqual(self.conn.execute("SELECT procedencia FROM nodo WHERE clave = 'PRE-00120'").fetchone()[0], "clonacion")
        self.assertEqual(self.conn.execute("SELECT procedencia FROM nodo WHERE clave = %s", (TRABE,)).fetchone()[0], "importado")
        self.assertEqual(self.conn.execute("SELECT tipo, archivos FROM carga WHERE id = %s", (r.carga_id,)).fetchone(), ("clonacion", {}))

    def test_ningun_compuesto_de_material_quedo_como_auxiliar(self):
        self.assertEqual(self.conn.execute("SELECT count(*) FROM nodo WHERE categoria = 'auxiliar'").fetchone()[0], 0)
        self.assertEqual(self.conn.execute("SELECT count(*) FROM nodo WHERE clave LIKE 'AUX-%' AND categoria = 'material'").fetchone()[0], 79)

    def test_la_migracion_siembra_la_funcion_para_control_de_obra(self):
        fila = self.conn.execute(
            "SELECT r.clave FROM rol_funcion rf JOIN rol r ON r.id = rf.rol_id JOIN funcion_atomica f ON f.id = rf.funcion_id"
            " WHERE f.clave = 'clonar_insumo'").fetchall()
        self.assertEqual(fila, [("control_de_obra",)])

    def test_la_version_nueva_de_cada_padre_queda_con_sus_lineas_en_orden(self):
        self.sustituir()
        for clave in ("EST-21011", "EST-52010"):
            v1, v2 = self.repo.versiones(clave)
            self.assertEqual([l.orden for l in v2.lineas], list(range(1, len(v1.lineas) + 1)))
        n = self.conn.execute(
            "SELECT count(*) FROM composicion c JOIN version_concepto v ON v.id = c.version_id JOIN nodo h ON h.id = c.hijo_id"
            " WHERE h.clave = %s AND v.version = (SELECT max(version) FROM version_concepto WHERE nodo_id = v.nodo_id)", (TRABE,)).fetchone()[0]
        self.assertEqual(n, 0)  # ya ninguna versión vigente cita la clave vieja


if __name__ == "__main__":
    unittest.main()
