"""
Colgar el programa del presupuesto contra un Postgres de verdad (`pgserver`), con los siete programas y los siete presupuestos de
verdad: el mismo contrato que la memoria (`core/tests/contrato_colgado.py`) y lo que solo la base garantiza — que un enlace puesto
no se mueva, que cada nodo o renglón sea del presupuesto del programa, que un nodo no lo ocupen dos filas y que la bitácora de
colgaduras solo se agregue. Se salta si faltan `pgserver` y `psycopg`.
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

from core.servicio_programa import Enlace
from core.tests.contrato_colgado import ContratoColgado, QUIEN
from core.tests.contrato_programa import CO

if HAY_POSTGRES:
    from infra.postgres_catalogo import PostgresCatalogo
    from infra.postgres_programa import PostgresPrograma, aplicar_migraciones

TABLAS = "carga, presupuesto, nodo, unidad, version_concepto, composicion, precio_historico, programa"


@unittest.skipUnless(HAY_POSTGRES, "faltan pgserver y psycopg")
class PruebasPostgres(ContratoColgado, unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.dir = tempfile.mkdtemp(prefix="pg_colgado_")
        cls.servidor = pgserver.get_server(cls.dir)
        cls.conn = psycopg.connect(cls.servidor.get_uri(), autocommit=True)
        aplicar_migraciones(cls.conn)

    @classmethod
    def tearDownClass(cls):
        cls.conn.close()
        cls.servidor.cleanup()
        shutil.rmtree(cls.dir, ignore_errors=True)

    def nuevos_repositorios(self):
        self.conn.execute(f"TRUNCATE {TABLAS} RESTART IDENTITY CASCADE")
        return PostgresPrograma(self.conn), PostgresCatalogo(self.conn)

    # ------------------------------------------------------------------ lo que solo la base garantiza
    def test_los_ids_de_otro_presupuesto_no_entran(self):
        pid = self.subir("Rubí")
        rubi = self.presupuestos["CAS-00003"].id
        zafiro = self.sc.proponer(self.subir("Zafiro"), CO)
        ajeno_nodo = next(e for e in zafiro.enlaces if e.nodo_id is not None)
        ajeno_renglon = next(e for e in zafiro.enlaces if e.renglon_id is not None)
        for e in (Enlace(self.programas.leer_programa(pid).filas[0].llave, nodo_id=ajeno_nodo.nodo_id),
                  Enlace(self.programas.leer_programa(pid).filas[0].llave, renglon_id=ajeno_renglon.renglon_id),
                  Enlace(self.programas.leer_programa(pid).filas[0].llave, nodo_id=987654)):
            with self.assertRaises(ValueError):
                self.programas.colgar(pid, rubi, [e], usuario=QUIEN, rol=CO, resumen={})
        g = self.programas.leer_programa(pid)
        self.assertEqual((g.presupuesto_id, g.enlaces, g.colgaduras), (None, [], []))

    def test_un_enlace_puesto_no_se_mueve_ni_con_sql(self):
        pid, _ = self.colgar("Zafiro")
        (a, b) = [e for e in self.programas.leer_programa(pid).enlaces if e.renglon_id is not None][:2]
        with self.assertRaises(psycopg.errors.RaiseException):
            self.conn.execute("UPDATE programa_fila SET renglon_id = %s WHERE programa_id = %s AND oid = %s", (b.renglon_id, pid, a.oid))
        with self.assertRaises(psycopg.errors.RaiseException):
            self.conn.execute("UPDATE programa_fila SET renglon_id = NULL WHERE programa_id = %s AND oid = %s", (pid, a.oid))
        with self.assertRaises(psycopg.errors.RaiseException):
            self.conn.execute("UPDATE programa SET presupuesto_id = %s WHERE id = %s", (self.presupuestos["CAS-00003"].id, pid))
        # lo que no cambia el enlace sí pasa: el programa se sigue editando
        self.conn.execute("UPDATE programa SET version = version + 1 WHERE id = %s", (pid,))
        self.conn.execute("UPDATE programa_fila SET renglon_id = renglon_id WHERE programa_id = %s AND oid = %s", (pid, a.oid))

    def test_una_fila_no_tiene_dos_enlaces_ni_un_nodo_o_renglon_lo_ocupan_dos_filas(self):
        pid = self.subir("Zafiro")
        a = self.sc.proponer(pid, CO)
        n1, n2 = [e for e in a.enlaces if e.nodo_id is not None][:2]
        r1, r2 = [e for e in a.enlaces if e.renglon_id is not None][:2]
        with self.assertRaises(psycopg.errors.CheckViolation):
            self.conn.execute("UPDATE programa_fila SET nodo_id = %s, renglon_id = %s WHERE programa_id = %s AND oid = %s",
                              (n1.nodo_id, r1.renglon_id, pid, n1.oid))
        self.conn.execute("UPDATE programa_fila SET nodo_id = %s WHERE programa_id = %s AND oid = %s", (n1.nodo_id, pid, n1.oid))
        with self.assertRaises(psycopg.errors.UniqueViolation):
            self.conn.execute("UPDATE programa_fila SET nodo_id = %s WHERE programa_id = %s AND oid = %s", (n1.nodo_id, pid, n2.oid))
        self.conn.execute("UPDATE programa_fila SET renglon_id = %s WHERE programa_id = %s AND oid = %s", (r1.renglon_id, pid, r1.oid))
        with self.assertRaises(psycopg.errors.UniqueViolation):
            self.conn.execute("UPDATE programa_fila SET renglon_id = %s WHERE programa_id = %s AND oid = %s", (r1.renglon_id, pid, r2.oid))

    def test_la_bitacora_de_colgaduras_solo_se_agrega(self):
        pid, _ = self.colgar("Oro")
        for sql in ("UPDATE programa_colgadura SET usuario = 'otro'", "DELETE FROM programa_colgadura"):
            with self.assertRaises(psycopg.errors.RaiseException, msg=sql):
                self.conn.execute(sql)
        with self.assertRaises(psycopg.errors.CheckViolation):
            self.conn.execute("INSERT INTO programa_colgadura (programa_id, presupuesto_id, usuario, rol, nuevos, resumen)"
                              " VALUES (%s, %s, '', 'x', 0, '{}'::jsonb)", (pid, self.presupuestos["CAS-00001"].id))

    def test_el_presupuesto_de_un_programa_colgado_no_se_puede_borrar(self):
        self.colgar("Oro")
        with self.assertRaises(psycopg.errors.ForeignKeyViolation):
            self.conn.execute("DELETE FROM presupuesto WHERE clave = 'CAS-00001'")


if __name__ == "__main__":
    unittest.main()
