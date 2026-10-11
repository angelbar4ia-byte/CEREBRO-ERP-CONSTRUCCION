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
    import psycopg.conninfo
    from psycopg.types.json import Jsonb

    HAY_POSTGRES = True
except ImportError:  # pragma: no cover
    HAY_POSTGRES = False

from core.accesos import PERMISOS_POR_OMISION
from core.tests.contrato_accesos import ContratoAccesos
from core.tests.contrato_programa import CAL, CO, ContratoPrograma, programa
from core.programa import AgregarVinculo
from core.servicio_programa import Conflicto, ServicioPrograma

if HAY_POSTGRES:
    from infra.postgres_accesos import PostgresAccesos
    from infra.postgres_programa import PostgresPrograma, aplicar_migraciones


@unittest.skipUnless(HAY_POSTGRES, "faltan pgserver y psycopg")
class PruebasPostgres(ContratoPrograma, ContratoAccesos, unittest.TestCase):
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

    def _permisos_de_vuelta(self):
        self.conn.execute("DELETE FROM rol_funcion")
        self.conn.execute("DELETE FROM funcion_atomica")
        accesos = PostgresAccesos(self.conn)
        for funcion, roles in PERMISOS_POR_OMISION.items():
            for rol in roles:
                accesos.dar_funcion(rol, funcion)
        return accesos

    def nuevos_accesos(self):
        self.conn.execute("TRUNCATE usuario CASCADE")
        return self._permisos_de_vuelta()

    def tearDown(self):  # las pruebas de permisos corrigen la tabla: la siguiente la encuentra como la dejó la migración
        self._permisos_de_vuelta()

    # ------------------------------------------------------------------ lo que solo Postgres garantiza
    def test_la_migracion_corre_una_vez(self):
        self.assertEqual(self.nuevas, ["0001_programa.sql", "0002_programa_importado_por.sql", "0003_version_nueva_del_programa.sql", "0004_usuarios_y_permisos.sql",
                                       "0005_catalogo_apu_presupuesto.sql",
                                       "0006_programa_cuelga_del_presupuesto.sql"])
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

    def test_la_migracion_siembra_los_roles_y_los_permisos_de_modelo_5b(self):
        # en una base limpia: la de las demás pruebas ya se usó y se restablece con código, no con la migración
        self.conn.execute("DROP DATABASE IF EXISTS limpia")
        self.conn.execute("CREATE DATABASE limpia")
        with psycopg.connect(psycopg.conninfo.make_conninfo(self.uri, dbname="limpia"), autocommit=True) as c:
            aplicar_migraciones(c)
            self.assertEqual([r[0] for r in c.execute("SELECT clave FROM rol ORDER BY id")],
                             ["residente", "supervisor", "superintendente", "costos", "cotizador", "control_de_obra"])
            self.assertEqual(PostgresAccesos(c).permisos(), PERMISOS_POR_OMISION)
            self.assertEqual(c.execute("SELECT count(*) FROM usuario").fetchone()[0], 0)  # sin usuarios: se dan de alta a propósito
        self.conn.execute("DROP DATABASE limpia")

    def test_el_cli_de_usuarios_da_de_alta_lista_y_retira(self):
        import contextlib
        import io

        from api.usuarios import main

        self.conn.execute("TRUNCATE usuario CASCADE")

        def corre(*args):
            salida, error = io.StringIO(), io.StringIO()
            with contextlib.redirect_stdout(salida), contextlib.redirect_stderr(error):
                codigo = main(["--postgres", self.uri, *args])
            return codigo, salida.getvalue(), error.getvalue()

        self.assertEqual(corre("agregar", "Luis@Obra.MX", "Luis Pérez", "control_de_obra")[0], 0)
        self.assertEqual(corre("agregar", "ana@obra.mx", "Ana Soto", "residente", "supervisor")[0], 0)
        codigo, _, error = corre("agregar", "luis@obra.mx", "Otro", "costos")
        self.assertEqual(codigo, 1)
        self.assertIn("ya hay un usuario", error)
        self.assertEqual(corre("agregar", "x@obra.mx", "X", "jefe")[0], 1)  # un rol que no existe
        self.assertEqual(corre("retirar", "ana@obra.mx")[0], 0)
        _, listado, _ = corre("listar")
        self.assertEqual([l.split("\t")[1:] for l in listado.splitlines()],
                         [["luis@obra.mx", "Luis Pérez", "control_de_obra", "activo"], ["ana@obra.mx", "Ana Soto", "residente,supervisor", "retirado"]])

    def test_el_correo_de_un_usuario_va_en_minusculas_y_sin_repetirse_en_la_base_misma(self):
        self.conn.execute("TRUNCATE usuario CASCADE")
        with self.assertRaises(psycopg.errors.CheckViolation):
            self.conn.execute("INSERT INTO usuario (nombre, correo) VALUES ('X', 'X@OBRA.MX')")
        self.conn.execute("INSERT INTO usuario (nombre, correo) VALUES ('X', 'x@obra.mx')")
        with self.assertRaises(psycopg.errors.UniqueViolation):
            self.conn.execute("INSERT INTO usuario (nombre, correo) VALUES ('Y', 'x@obra.mx')")
        with self.assertRaises(psycopg.errors.CheckViolation):
            self.conn.execute("INSERT INTO usuario (nombre, correo) VALUES ('', 'z@obra.mx')")

    def test_un_usuario_no_puede_tener_un_rol_que_no_existe_ni_repetido(self):
        self.conn.execute("TRUNCATE usuario CASCADE")
        uid = self.conn.execute("INSERT INTO usuario (nombre, correo) VALUES ('X', 'x@obra.mx') RETURNING id").fetchone()[0]
        with self.assertRaises(psycopg.errors.ForeignKeyViolation):
            self.conn.execute("INSERT INTO usuario_rol (usuario_id, rol_id) VALUES (%s, 9999)", (uid,))
        self.conn.execute("INSERT INTO usuario_rol (usuario_id, rol_id) SELECT %s, id FROM rol WHERE clave = 'costos'", (uid,))
        with self.assertRaises(psycopg.errors.UniqueViolation):
            self.conn.execute("INSERT INTO usuario_rol (usuario_id, rol_id) SELECT %s, id FROM rol WHERE clave = 'costos'", (uid,))

    def test_la_cadena_de_versiones_es_una_sola_tambien_en_la_base(self):
        insertar = ("INSERT INTO programa (nombre, calendario, version_de, traspaso) VALUES ('v', '{}'::jsonb, %s, %s)")
        self.conn.execute(insertar, (self.pid, Jsonb({})))
        with self.assertRaises(psycopg.errors.UniqueViolation):  # un programa no tiene dos versiones nuevas directas
            self.conn.execute(insertar, (self.pid, Jsonb({})))
        with self.assertRaises(psycopg.errors.CheckViolation):  # una versión nueva siempre dice qué pasó con las ediciones
            self.conn.execute("INSERT INTO programa (nombre, calendario, version_de) VALUES ('v', '{}'::jsonb, %s)", (self.pid,))

    def test_una_version_nueva_que_falla_a_medias_no_deja_nada(self):
        from datetime import datetime, timezone

        from core.servicio_programa import Heredada

        self.sv.aplicar(self.pid, self.p16(), CO, "luis")
        buena = Heredada(self.p16("decision"), CO, "luis", datetime.now(timezone.utc), {}, self.repo.ediciones(self.pid)[0].id)
        mala = Heredada(self.p16("decision"), CO, "", datetime.now(timezone.utc), {}, buena.heredada_de)  # sin autor: la base la rechaza
        with self.assertRaises(psycopg.errors.CheckViolation):
            self.repo.importar_version(self.pid, "v2", self.plus, CAL, usuario="marta", rol=CO, heredadas=[buena, mala], traspaso={"de": self.pid}, esperaba=1)
        self.assertEqual([r.id for r in self.repo.listar_programas()], [self.pid])  # ni el programa ni la edición buena quedaron
        self.assertEqual(self.conn.execute("SELECT count(*) FROM edicion_programa WHERE heredada_de IS NOT NULL").fetchone()[0], 0)

    def test_de_donde_viene_una_edicion_heredada_no_se_reescribe(self):
        self.sv.aplicar(self.pid, self.p16(), CO, "luis")
        r = self.sv.subir_version(self.pid, "v2", self.plus, CAL, CO, "marta")
        (heredada,) = self.repo.ediciones(r.id)
        self.assertIsNotNone(heredada.heredada_de)
        with self.assertRaises(psycopg.Error):  # revertirla sí, pero no de paso cambiar de dónde venía
            self.conn.execute("UPDATE edicion_programa SET estado = 'revertida', revertida_en = now(), revertida_por = 'x', heredada_de = NULL WHERE id = %s", (heredada.id,))
        self.sv.deshacer(r.id, heredada.id, CO, "marta")  # lo que sí se puede
        self.assertEqual(self.repo.ediciones(r.id)[0].estado, "revertida")
        self.assertEqual(self.repo.ediciones(r.id)[0].heredada_de, heredada.heredada_de)

    def test_los_dias_que_no_caben_exactos_no_se_guardan(self):
        from infra.postgres_programa import _a_numeric

        self.assertEqual(_a_numeric(Fraction(1, 2)), 0.5)
        with self.assertRaises(ValueError):
            _a_numeric(Fraction(1, 3))


if __name__ == "__main__":
    unittest.main()
