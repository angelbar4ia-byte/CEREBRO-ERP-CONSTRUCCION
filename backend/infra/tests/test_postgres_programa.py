"""
`PostgresPrograma` contra un Postgres de verdad (`pgserver`: Postgres embebido, sin instalar nada).

Corre el mismo contrato que el adaptador en memoria (`core/tests/contrato_programa.py`) y además lo que solo
Postgres puede garantizar: la migración, las restricciones y que la bitácora no se borre ni se reescriba.
Se salta si faltan `pgserver` y `psycopg` (`pip install pgserver "psycopg[binary]"`; el CI los instala).
"""
import shutil
import tempfile
import unittest
from datetime import date
from fractions import Fraction

try:
    import pgserver
    import psycopg
    from psycopg.types.json import Jsonb

    HAY_POSTGRES = True
except ImportError:  # pragma: no cover
    HAY_POSTGRES = False

from core.tests.contrato_programa import CAL, CO, ContratoPrograma, programa
from core.programa import AgregarVinculo
from core.servicio_programa import Conflicto, ServicioPrograma

if HAY_POSTGRES:
    from infra.postgres_programa import PostgresPrograma, aplicar_migraciones


@unittest.skipUnless(HAY_POSTGRES, "faltan pgserver y psycopg")
class PruebasPostgres(ContratoPrograma, unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.dir = tempfile.mkdtemp(prefix="pg_programa_")
        cls.servidor = pgserver.get_server(cls.dir)
        cls.uri = cls.servidor.get_uri()
        cls.conn = psycopg.connect(cls.uri, autocommit=True)
        cls.nuevas = aplicar_migraciones(cls.conn)

    @classmethod
    def tearDownClass(cls):
        cls.conn.close()
        cls.servidor.cleanup()
        shutil.rmtree(cls.dir, ignore_errors=True)

    def nuevo_repositorio(self):
        self.conn.execute("TRUNCATE programa CASCADE")
        return PostgresPrograma(self.conn)

    # ------------------------------------------------------------------ lo que solo Postgres garantiza
    def test_la_migracion_corre_una_vez(self):
        self.assertEqual(self.nuevas, ["0001_programa.sql"])
        self.assertEqual(aplicar_migraciones(self.conn), [])

    def test_los_tipos_de_vinculo_se_guardan_con_los_nombres_del_modelo(self):
        tipos = {r[0] for r in self.conn.execute("SELECT DISTINCT tipo_vinculo FROM programa_vinculo WHERE estado = 'vigente'")}
        self.assertEqual(tipos, {"fin_inicio", "inicio_inicio", "fin_fin", "inicio_fin"})

    def test_la_confianza_se_deriva_del_origen(self):
        v = self.plus.vinculos[0]
        for origen, confianza in (("tecnica", "alta"), ("recurso", "media"), ("decision", "baja"), (None, None)):
            r = self.conn.execute(
                "INSERT INTO programa_vinculo (programa_id, predecesora_oid, sucesora_oid, tipo_vinculo, origen)"
                " VALUES (%s, %s, %s, 'fin_inicio', %s) RETURNING confianza", (self.pid, v.predecesora, v.sucesora, origen)).fetchone()
            self.assertEqual(r[0], confianza)

    def test_un_vinculo_no_puede_citar_una_fila_que_no_existe(self):
        with self.assertRaises(psycopg.errors.ForeignKeyViolation):
            self.conn.execute(
                "INSERT INTO programa_vinculo (programa_id, predecesora_oid, sucesora_oid, tipo_vinculo)"
                " VALUES (%s, 'no existe', %s, 'fin_inicio')", (self.pid, self.plus.vinculos[0].sucesora))

    def test_la_bitacora_ni_se_borra_ni_se_reescribe(self):
        self.sv.aplicar(self.pid, self.p16(), CO, "luis")
        with self.assertRaises(psycopg.Error):
            self.conn.execute("DELETE FROM edicion_programa")
        with self.assertRaises(psycopg.Error):
            self.conn.execute("UPDATE edicion_programa SET usuario = 'otro'")
        with self.assertRaises(psycopg.Error):
            self.conn.execute("UPDATE edicion_programa SET impacto = '{}'::jsonb")
        with self.assertRaises(psycopg.Error):  # ni siquiera borrando el programa que la contiene
            self.conn.execute("DELETE FROM programa WHERE id = %s", (self.pid,))
        self.assertEqual(len(self.repo.ediciones(self.pid)), 1)

    def test_una_edicion_sin_autor_no_entra(self):
        with self.assertRaises(psycopg.errors.CheckViolation):
            self.conn.execute(
                "INSERT INTO edicion_programa (programa_id, secuencia, edicion, datos, rol, usuario, impacto)"
                " VALUES (%s, 1, 'cambiar_duracion', '{}'::jsonb, 'control_de_obra', '', '{}'::jsonb)", (self.pid,))

    def test_un_vinculo_editado_nunca_queda_sin_origen(self):
        with self.assertRaises(psycopg.errors.CheckViolation):
            self.conn.execute(
                "INSERT INTO edicion_programa (programa_id, secuencia, edicion, datos, rol, usuario, impacto)"
                " VALUES (%s, 1, 'agregar_vinculo', '{}'::jsonb, 'control_de_obra', 'luis', '{}'::jsonb)", (self.pid,))

    def test_una_edicion_se_guarda_con_su_origen_en_su_propia_columna(self):
        self.sv.aplicar(self.pid, self.p16("recurso"), CO, "luis")
        self.sv.aplicar(self.pid, AgregarVinculo(self.f[1087], self.f[1088], "SS", Fraction(1, 2)), CO, "luis")
        self.assertEqual(
            [r for r in self.conn.execute("SELECT edicion, origen FROM edicion_programa ORDER BY secuencia")],
            [("agregar_vinculo", "recurso"), ("agregar_vinculo", "decision")],
        )

    def test_dos_conexiones_no_se_pisan(self):
        otra = psycopg.connect(self.uri, autocommit=True)
        try:
            a, b = ServicioPrograma(self.repo), ServicioPrograma(PostgresPrograma(otra))
            vista_de_b = b.proponer(self.pid, self.p16(), CO)  # b ve la versión 0
            a.aplicar(self.pid, AgregarVinculo(self.f[1087], self.f[1088], "SS"), CO, "luis")  # a edita
            with self.assertRaises(Conflicto):
                b.repo.guardar_edicion(self.pid, self.p16(), rol=CO, usuario="ana", impacto=vista_de_b.impacto.resumen(), esperaba=vista_de_b.esperaba)
            self.assertEqual(len(self.repo.ediciones(self.pid)), 1)
        finally:
            otra.close()

    def test_los_dias_que_no_caben_exactos_no_se_guardan(self):
        from infra.postgres_programa import _a_numeric

        self.assertEqual(_a_numeric(Fraction(1, 2)), 0.5)
        with self.assertRaises(ValueError):
            _a_numeric(Fraction(1, 3))


if __name__ == "__main__":
    unittest.main()
