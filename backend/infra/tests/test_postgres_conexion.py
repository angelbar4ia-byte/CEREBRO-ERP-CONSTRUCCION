"""
`ConexionPorHilo` (D-482) contra un Postgres de verdad (`pgserver`): dos peticiones que se traslapan no comparten sesión, así que lo que una
revierte queda revertido aunque la otra confirme. Se salta si faltan `pgserver` y `psycopg`.
"""
import shutil
import tempfile
import threading
import time
import unittest

try:
    import pgserver
    import psycopg

    HAY_POSTGRES = True
except ImportError:  # pragma: no cover
    HAY_POSTGRES = False

if HAY_POSTGRES:
    from infra.conexion import ConexionPorHilo


@unittest.skipUnless(HAY_POSTGRES, "faltan pgserver y psycopg")
class PruebasConexionPorHilo(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.dir = tempfile.mkdtemp(prefix="pg_conexion_")
        cls.servidor = pgserver.get_server(cls.dir)
        cls.uri = cls.servidor.get_uri()

    @classmethod
    def tearDownClass(cls):
        cls.servidor.cleanup()
        shutil.rmtree(cls.dir, ignore_errors=True)

    def setUp(self):
        self.conn = ConexionPorHilo(self.uri)
        self.addCleanup(self.conn.cerrar)
        self.conn.execute("DROP TABLE IF EXISTS t")
        self.conn.execute("CREATE TABLE t (n int)")

    def trabajo(self, errores, n, pausa, revierte=False):
        try:
            with self.conn.transaction():
                self.conn.execute("INSERT INTO t VALUES (%s)", (n,))
                time.sleep(pausa)
                if revierte:
                    raise RuntimeError("esta se revierte")
                self.conn.execute("INSERT INTO t VALUES (%s)", (n + 100,))
        except RuntimeError as e:
            errores.append((n, str(e)))

    def test_dos_peticiones_que_se_traslapan_no_se_mezclan(self):
        errores = []
        a = threading.Thread(target=self.trabajo, args=(errores, 1, 0.3, True))  # entra primero, sale primero y revierte
        b = threading.Thread(target=self.trabajo, args=(errores, 2, 0.9))  # entra en medio, sale después y confirma
        a.start()
        time.sleep(0.1)
        b.start()
        a.join()
        b.join()
        self.assertEqual(errores, [(1, "esta se revierte")])  # y ningún `OutOfOrderTransactionNesting`
        self.assertEqual(self.conn.execute("SELECT n FROM t ORDER BY n").fetchall(), [(2,), (102,)])  # lo de A no quedó escrito

    def test_cada_hilo_tiene_su_conexion_y_el_mismo_hilo_siempre_la_misma(self):
        pids = []
        hilos = [threading.Thread(target=lambda: pids.append((self.conn.info.backend_pid, self.conn.info.backend_pid))) for _ in range(3)]
        for h in hilos:
            h.start()
        for h in hilos:
            h.join()
        self.assertTrue(all(a == b for a, b in pids))  # dentro de un hilo, la misma sesión
        self.assertEqual(len({a for a, _ in pids}), 3)  # entre hilos, distintas
        self.assertEqual(self.conn.abiertas, 4)  # las tres y la de este hilo

    def test_cerrar_las_cierra_todas_y_una_cerrada_se_reabre(self):
        self.conn.execute("SELECT 1")
        antes = self.conn.info.backend_pid
        self.conn.cerrar()
        self.assertEqual(self.conn.abiertas, 0)
        self.assertEqual(self.conn.execute("SELECT 1").fetchone(), (1,))
        self.assertNotEqual(self.conn.info.backend_pid, antes)

    def test_lo_privado_no_se_delega(self):
        with self.assertRaises(AttributeError):
            self.conn._no_existe


if __name__ == "__main__":
    unittest.main()
