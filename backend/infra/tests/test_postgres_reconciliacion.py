"""
Reconciliar un presupuesto que ya existe contra un Postgres de verdad (`pgserver`), con los siete presupuestos de verdad: el mismo
contrato que la memoria (`core/tests/contrato_reconciliacion.py`) y lo que solo la base garantiza — que lo dado de baja se quede en
la tabla sin estorbar, que la historia de un renglón solo se agregue y que lo contratado no se dé de baja ni con SQL. Se salta si
faltan `pgserver` y `psycopg`.
"""
import shutil
import tempfile
import unittest
from decimal import Decimal

try:
    import pgserver
    import psycopg

    HAY_POSTGRES = True
except ImportError:  # pragma: no cover
    HAY_POSTGRES = False

from core.contratacion import ServicioContratacion
from core.tests.contrato_reconciliacion import BLOQUE, CO, ContratoReconciliacion, K1, ZAFIRO
from core.tests.datos_opus import con_copia, sin_renglon

if HAY_POSTGRES:
    from infra.postgres_catalogo import PostgresCatalogo
    from infra.postgres_programa import aplicar_migraciones

TABLAS = "carga, presupuesto, nodo, unidad, version_concepto, composicion, precio_historico, programa"


@unittest.skipUnless(HAY_POSTGRES, "faltan pgserver y psycopg")
class PruebasPostgres(ContratoReconciliacion, unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.dir = tempfile.mkdtemp(prefix="pg_reconciliacion_")
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

    # ------------------------------------------------------------------ lo que solo la base garantiza
    def test_lo_dado_de_baja_sigue_en_la_tabla_y_su_lugar_queda_libre(self):
        antes = self.renglon()
        self.cargar(sin_renglon(self.pres, ZAFIRO, "EST-10010"), bajas_confirmadas=[K1])
        fila = self.conn.execute("SELECT baja_carga_id, orden, padre_id FROM composicion WHERE id = %s", (antes.id,)).fetchone()
        self.assertEqual(fila[0], 2)  # la carga que la dio de baja
        self.assertEqual(self.conn.execute("SELECT count(*) FROM composicion WHERE baja_carga_id IS NOT NULL").fetchone()[0], 1)
        # otro renglón vivo puede ocupar el lugar del que se fue: el índice solo cuenta lo vivo
        self.conn.execute("INSERT INTO composicion (padre_id, hijo_id, cantidad, orden, reporta_a) SELECT padre_id, hijo_id, 1, orden, reporta_a"
                          " FROM composicion WHERE id = %s", (antes.id,))

    def test_un_bloque_dado_de_baja_deja_libre_su_ruta_y_no_cuenta(self):
        antes = self.presupuesto().renglones
        self.cargar(sin_renglon(self.pres, ZAFIRO, "EST-01040"), bajas_confirmadas=[BLOQUE])
        n = self.conn.execute("SELECT ruta_natural, baja_carga_id FROM nodo WHERE ruta_natural LIKE %s", (BLOQUE + "~baja%",)).fetchall()
        self.assertEqual(len(n), 1)
        self.assertLess(self.presupuesto().renglones, antes)
        self.cargar(self.pres)  # volver a ponerlo: la ruta natural vuelve a ser de un bloque vivo
        self.assertEqual(self.conn.execute("SELECT count(*) FROM nodo WHERE ruta_natural = %s", (BLOQUE,)).fetchone()[0], 1)

    def test_la_historia_de_un_renglon_solo_se_agrega(self):
        self.cargar(con_copia(self.pres, ZAFIRO, "EST-10011", "EST-10011", cantidad="5"))
        for sql in ("UPDATE renglon_historia SET despues = '0'", "DELETE FROM renglon_historia"):
            with self.assertRaises(psycopg.errors.RaiseException, msg=sql):
                self.conn.execute(sql)
        with self.assertRaises(psycopg.errors.CheckViolation):
            self.conn.execute("INSERT INTO renglon_historia (renglon_id, carga_id, campo) VALUES (%s, 1, 'otra')", (self.renglon().id,))

    def test_lo_contratado_no_se_da_de_baja_ni_con_sql(self):
        ServicioContratacion(self.repo).contratar(ZAFIRO, CO, "luis@obra.mx", "CAS-00004#1/NIV-00001#1")
        id_ = self.renglon().id
        with self.assertRaises(psycopg.errors.RaiseException):
            self.conn.execute("UPDATE composicion SET baja_carga_id = 1 WHERE id = %s", (id_,))
        with self.assertRaises(psycopg.errors.RaiseException):
            self.conn.execute("DELETE FROM composicion WHERE id = %s", (id_,))

    def test_una_matriz_no_se_da_de_baja(self):
        with self.assertRaises(psycopg.errors.RaiseException):  # sus líneas solo se agregan
            self.conn.execute("UPDATE composicion SET baja_carga_id = 1 WHERE version_id IS NOT NULL")

    def test_cargar_lo_mismo_no_escribe_historia_ni_carga(self):
        r = self.cargar(self.pres)
        self.assertIsNone(r.carga_id)
        self.assertEqual(self.conn.execute("SELECT count(*) FROM renglon_historia").fetchone()[0], 0)

if __name__ == "__main__":
    unittest.main()
