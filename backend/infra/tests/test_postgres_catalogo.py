"""
`PostgresCatalogo` contra un Postgres de verdad (`pgserver`: Postgres embebido, sin instalar nada), con los archivos de OPUS de verdad.

Corre el mismo contrato que el adaptador en memoria (`core/tests/contrato_catalogo.py`) y además lo que solo Postgres puede
garantizar: que lo que se guardó no se reescriba, que una carga que falla a la mitad no deje nada, y las restricciones de la
migración 0005. Se salta si faltan `pgserver` y `psycopg`.
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

from core.accesos import PERMISOS_POR_OMISION
from core.catalogo import LineaPlan
from core.tests.contrato_catalogo import ContratoCatalogo, USUARIO
from dataclasses import replace

if HAY_POSTGRES:
    from infra.postgres_accesos import PostgresAccesos
    from infra.postgres_catalogo import PostgresCatalogo
    from infra.postgres_programa import aplicar_migraciones

TABLAS = "carga, presupuesto, nodo, unidad, version_concepto, composicion, precio_historico"


@unittest.skipUnless(HAY_POSTGRES, "faltan pgserver y psycopg")
class PruebasPostgres(ContratoCatalogo, unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.dir = tempfile.mkdtemp(prefix="pg_catalogo_")
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
    def test_los_permisos_sembrados_son_los_de_omision(self):
        self.assertEqual(PostgresAccesos(self.conn).permisos(), PERMISOS_POR_OMISION)
        self.assertEqual(PERMISOS_POR_OMISION["cargar_catalogo_opus"], frozenset({"control_de_obra", "costos"}))

    def test_una_version_y_sus_lineas_no_se_reescriben_ni_se_borran(self):
        self.base()
        for sql in ("UPDATE version_concepto SET pu = 0", "DELETE FROM version_concepto",
                    "UPDATE composicion SET cantidad = 0 WHERE version_id IS NOT NULL",
                    "DELETE FROM composicion WHERE version_id IS NOT NULL", "UPDATE carga SET usuario = 'otro'", "DELETE FROM carga"):
            with self.assertRaises(psycopg.errors.RaiseException, msg=sql):
                self.conn.execute(sql)
        self.assertEqual(self.repo.versiones("EST-01040")[0].pu, self.lectura.conceptos["EST-01040"][0].precio_observado)

    def test_un_precio_historico_solo_se_cierra(self):
        self.base()
        for sql in ("UPDATE precio_historico SET precio = 1", "DELETE FROM precio_historico"):
            with self.assertRaises(psycopg.errors.RaiseException, msg=sql):
                self.conn.execute(sql)
        self.conn.execute("UPDATE precio_historico SET vigente_hasta = now() WHERE nodo_id = %s", (self.repo.id_de("ACE-00001"),))
        with self.assertRaises(psycopg.errors.RaiseException):  # y una vez cerrado, no se vuelve a abrir
            self.conn.execute("UPDATE precio_historico SET vigente_hasta = NULL WHERE nodo_id = %s", (self.repo.id_de("ACE-00001"),))

    def test_la_clave_del_catalogo_es_unica_pero_las_de_un_presupuesto_se_repiten(self):
        self.base()
        with self.assertRaises(psycopg.errors.UniqueViolation):
            self.conn.execute("INSERT INTO nodo (clave, rol, categoria) VALUES ('ACE-00001', 'insumo', 'material')")
        repetidas = self.conn.execute(
            "SELECT count(*) FROM (SELECT clave FROM nodo WHERE rol = 'estructural' GROUP BY clave HAVING count(*) > 1) t").fetchone()[0]
        self.assertGreater(repetidas, 100)  # ECO-00001, NIV-00001… están en cada prototipo
        self.assertEqual(self.conn.execute("SELECT count(*) FROM (SELECT presupuesto_id, ruta_natural FROM nodo WHERE rol = 'estructural'"
                                           " GROUP BY 1, 2 HAVING count(*) > 1) t").fetchone()[0], 0)

    def test_una_linea_no_puede_citar_la_version_de_otro_nodo(self):
        self.base()
        v = self.conn.execute("SELECT id, nodo_id FROM version_concepto ORDER BY id LIMIT 1").fetchone()
        otro = self.conn.execute("SELECT id FROM nodo WHERE id <> %s AND rol = 'insumo' LIMIT 1", (v[1],)).fetchone()[0]
        with self.assertRaises(psycopg.errors.ForeignKeyViolation):
            self.conn.execute("INSERT INTO composicion (padre_id, version_id, hijo_id, cantidad, orden, reporta_a)"
                              " VALUES (%s, %s, %s, 1, 99, 'material')", (otro, v[0], v[1]))

    def test_el_estructural_pide_su_presupuesto_su_ruta_y_su_tipo(self):
        self.base()
        for columnas in ("clave, rol, categoria, ruta_natural, tipo_opus", "clave, rol, categoria, presupuesto_id, tipo_opus",
                         "clave, rol, categoria, presupuesto_id, ruta_natural"):
            with self.assertRaises(psycopg.errors.CheckViolation, msg=columnas):
                self.conn.execute(f"INSERT INTO nodo ({columnas}) SELECT 'X-1', 'estructural', 'concepto', "
                                  + ", ".join({"ruta_natural": "'x#1'", "tipo_opus": "'Nivel 2'", "presupuesto_id": "(SELECT min(id) FROM presupuesto)"}[c.strip()]
                                              for c in columnas.split(",")[3:]))

    def test_una_carga_que_falla_a_la_mitad_no_deja_nada(self):
        self.base()
        antes = self.repo.estado_vigente()
        r = self.revisar(reescalar_para_versionar(self))
        malo = replace(r.plan.versiones_nuevas[0], lineas=r.plan.versiones_nuevas[0].lineas + (LineaPlan("NO-EXISTE", Decimal("1"), r.plan.versiones_nuevas[0].lineas[0].reporta_a),))
        plan = replace(r.plan, precios_nuevos=(("ACE-00001", Decimal("99")),), versiones_nuevas=(malo,))
        with self.assertRaises(KeyError):
            self.repo.aplicar(plan)
        self.assertEqual((len(self.repo.cargas()), len(self.repo.precios("ACE-00001")), self.repo.estado_vigente()), (1, 1, antes))


def reescalar_para_versionar(prueba):
    from core.tests.datos_opus import reescalar_linea

    return reescalar_linea(prueba.con, "ACA-01010", 0, Decimal("1.1"))


if __name__ == "__main__":
    unittest.main()
