"""
Contratar un subárbol contra un Postgres de verdad (`pgserver`), con los siete presupuestos de verdad: el mismo contrato que la memoria
(`core/tests/contrato_contratacion.py`) y lo que solo la base garantiza — que lo contratado no se edite ni se borre ni con SQL, que el
estado de congelamiento solo se agregue y sea de un bloque, y que una contratación que falla a medias no deje nada. Se salta si faltan
`pgserver` y `psycopg`.
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

from core.tests.contrato_contratacion import CIMENTACION, ContratoContratacion, CO, QUIEN, ZAFIRO

if HAY_POSTGRES:
    from infra.postgres_catalogo import PostgresCatalogo
    from infra.postgres_programa import aplicar_migraciones

TABLAS = "carga, presupuesto, nodo, unidad, version_concepto, composicion, precio_historico, programa"


@unittest.skipUnless(HAY_POSTGRES, "faltan pgserver y psycopg")
class PruebasPostgres(ContratoContratacion, unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.dir = tempfile.mkdtemp(prefix="pg_contratacion_")
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

    def renglon_de(self, clave, presupuesto=ZAFIRO):
        return self.conn.execute(
            "SELECT c.id, c.cantidad, c.hijo_version_id FROM composicion c JOIN nodo h ON h.id = c.hijo_id JOIN nodo p ON p.id = c.padre_id"
            " JOIN presupuesto pr ON pr.id = p.presupuesto_id WHERE h.clave = %s AND pr.clave = %s AND c.version_id IS NULL ORDER BY c.id",
            (clave, presupuesto)).fetchone()

    # ------------------------------------------------------------------ lo que solo la base garantiza
    def test_lo_contratado_no_se_edita_ni_se_borra_ni_con_sql(self):
        self.mover_el_acero("1.02")
        self.sc.contratar(ZAFIRO, CO, QUIEN, CIMENTACION)
        for clave in ("EST-10010", "EST-01040"):
            id_, cantidad, version = self.renglon_de(clave)
            for sql in ("UPDATE composicion SET cantidad = cantidad + 1 WHERE id = %s", "UPDATE composicion SET hijo_version_id = NULL WHERE id = %s",
                        "UPDATE composicion SET orden = orden + 1000 WHERE id = %s", "DELETE FROM composicion WHERE id = %s"):
                with self.assertRaises(psycopg.errors.RaiseException, msg=sql):
                    self.conn.execute(sql, (id_,))
            self.assertEqual(self.renglon_de(clave), (id_, cantidad, version))
        # un renglón que no es de un bloque contratado se edita como siempre: en diseño «renumera libre»
        fuera = self.conn.execute(
            "SELECT c.id FROM composicion c JOIN nodo p ON p.id = c.padre_id JOIN presupuesto pr ON pr.id = p.presupuesto_id"
            " WHERE pr.clave = 'CAS-00003' AND c.version_id IS NULL ORDER BY c.id LIMIT 1").fetchone()[0]
        self.conn.execute("UPDATE composicion SET cantidad = cantidad WHERE id = %s", (fuera,))

    def test_lo_que_se_agrega_a_lo_contratado_entra(self):
        self.sc.contratar(ZAFIRO, CO, QUIEN, CIMENTACION)
        padre, hijo = self.conn.execute(
            "SELECT c.padre_id, c.hijo_id FROM composicion c JOIN nodo h ON h.id = c.hijo_id WHERE h.clave = 'EST-10010' AND c.version_id IS NULL"
            " ORDER BY c.id LIMIT 1").fetchone()
        orden = self.conn.execute("SELECT max(orden) + 1 FROM composicion WHERE padre_id = %s AND version_id IS NULL", (padre,)).fetchone()[0]
        self.conn.execute("INSERT INTO composicion (padre_id, hijo_id, cantidad, orden, reporta_a) VALUES (%s, %s, 1, %s, 'concepto')", (padre, hijo, orden))

    def test_el_estado_solo_se_agrega_y_es_de_un_bloque(self):
        self.sc.contratar(ZAFIRO, CO, QUIEN, CIMENTACION)
        for sql in ("UPDATE estado_congelamiento SET estado = 'diseño'", "DELETE FROM estado_congelamiento"):
            with self.assertRaises(psycopg.errors.RaiseException, msg=sql):
                self.conn.execute(sql)
        (c,) = self.sc.contratados(ZAFIRO)
        carga = c.carga_id
        concepto = self.conn.execute("SELECT id FROM nodo WHERE clave = 'EST-10010' AND rol <> 'estructural'").fetchone()[0]
        with self.assertRaises(psycopg.errors.RaiseException):  # un concepto no se contrata: se contrata un bloque
            self.conn.execute("INSERT INTO estado_congelamiento (nodo_id, estado, usuario, rol, carga_id, resumen) VALUES (%s, 'contratado', 'x', 'y', %s, '{}')",
                              (concepto, carga))
        with self.assertRaises(psycopg.errors.UniqueViolation):  # y un bloque se contrata una vez
            self.conn.execute("INSERT INTO estado_congelamiento (nodo_id, estado, usuario, rol, carga_id, resumen) VALUES (%s, 'contratado', 'x', 'y', %s, '{}')",
                              (c.nodo_id, carga))
        with self.assertRaises(psycopg.errors.CheckViolation):
            self.conn.execute("INSERT INTO estado_congelamiento (nodo_id, estado, usuario, rol, carga_id, resumen) VALUES (%s, 'diseño', '', 'y', %s, '{}')",
                              (c.nodo_id, carga))

    def test_una_carga_es_de_archivos_o_de_contratacion(self):
        with self.assertRaises(psycopg.errors.CheckViolation):
            self.conn.execute("INSERT INTO carga (usuario, rol, archivos, resumen, tipo) VALUES ('x', 'y', '{}', '{}', 'otra')")

    def test_la_migracion_siembra_la_funcion_para_control_de_obra(self):
        fila = self.conn.execute(
            "SELECT r.clave FROM rol_funcion rf JOIN rol r ON r.id = rf.rol_id JOIN funcion_atomica f ON f.id = rf.funcion_id"
            " WHERE f.clave = 'contratar_subarbol'").fetchall()
        self.assertEqual(fila, [("control_de_obra",)])


if __name__ == "__main__":
    unittest.main()
