"""
La bandeja contra un Postgres de verdad (`pgserver`): el mismo contrato que la memoria (`core/tests/contrato_bandeja.py`), con los tres
archivos de OPUS de verdad, y lo que solo la base garantiza — que una propuesta resuelta no se reescriba ni se borre, que quien la
propuso no la apruebe ni con SQL, que lo rechazado lleve su porqué, que una alerta activa por tipo y objeto sea una sola fila aunque
dos procesos la vean a la vez, y que lo resuelto no se reabra. Se salta si faltan `pgserver` y `psycopg`.
"""
import shutil
import tempfile
import threading
import unittest

try:
    import pgserver
    import psycopg

    HAY_POSTGRES = True
except ImportError:  # pragma: no cover
    HAY_POSTGRES = False

from core.tests.contrato_bandeja import ContratoBandeja

if HAY_POSTGRES:
    from infra.postgres_bandeja import PostgresBandeja
    from infra.postgres_catalogo import PostgresCatalogo
    from infra.postgres_programa import aplicar_migraciones

TABLAS = "propuesta, alerta, carga, presupuesto, nodo, unidad, version_concepto, composicion, precio_historico, programa"
INSERTAR = ("INSERT INTO propuesta (tipo, objeto, valor_propuesto, evidencia, origen, modelo, propuesto_por, propuesto_con_rol)"
            " VALUES ('clonacion', 'AUX-00001', '{\"original\": \"AUX-00001\", \"clave\": \"PRE-00120\"}', 'es una trabe', %s, %s, %s, %s)"
            " RETURNING id")


@unittest.skipUnless(HAY_POSTGRES, "faltan pgserver y psycopg")
class PruebasPostgres(ContratoBandeja, unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.dir = tempfile.mkdtemp(prefix="pg_bandeja_")
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
        return PostgresBandeja(self.conn), PostgresCatalogo(self.conn)

    def una_propuesta(self, origen="usuario", modelo=None, por="ana@obra.mx", rol="costos"):
        return self.conn.execute(INSERTAR, (origen, modelo, por, rol)).fetchone()[0]

    # ------------------------------------------------------------------ lo que solo la base garantiza: propuestas
    def test_una_propuesta_no_se_reescribe_ni_se_borra_y_solo_se_resuelve_una_vez(self):
        pid = self.una_propuesta()
        for sql in ("DELETE FROM propuesta", "UPDATE propuesta SET evidencia = 'otra'", "UPDATE propuesta SET valor_propuesto = '{}'",
                    "UPDATE propuesta SET propuesto_por = 'luis@obra.mx'", "UPDATE propuesta SET base = 9",
                    "UPDATE propuesta SET nota = 'una nota sin resolver'", "UPDATE propuesta SET resultado = '{}'"):  # estando pendiente, nada se escribe
            with self.assertRaises(psycopg.errors.RaiseException, msg=sql):
                self.conn.execute(sql)
        for campo, valor in (("evidencia", "'otra'"), ("tipo", "'version'"), ("objeto", "'AUX-00002'"), ("valor_propuesto", "'{}'"),
                             ("propuesto_por", "'luis@obra.mx'"), ("propuesto_con_rol", "'residente'"), ("base", "9"),
                             ("creada_en", "now() + interval '1 day'")):  # y al resolverla, lo propuesto no cambia
            sql = ("UPDATE propuesta SET estado = 'rechazada', resuelto_por = 'luis@obra.mx', resuelto_con_rol = 'control_de_obra',"
                   f" resuelta_en = now(), nota = 'no', {campo} = {valor}")
            with self.assertRaises(psycopg.errors.RaiseException, msg=sql):
                self.conn.execute(sql)
        self.conn.execute("UPDATE propuesta SET estado = 'rechazada', resuelto_por = 'luis@obra.mx', resuelto_con_rol = 'control_de_obra',"
                          " resuelta_en = now(), nota = 'Todavía no'")
        for sql in ("DELETE FROM propuesta", "UPDATE propuesta SET estado = 'pendiente', resuelto_por = NULL, resuelto_con_rol = NULL,"
                    " resuelta_en = NULL, nota = NULL", "UPDATE propuesta SET nota = 'ahora sí'",
                    "UPDATE propuesta SET estado = 'aprobada', resultado = '{}', nota = NULL"):
            with self.assertRaises(psycopg.errors.RaiseException, msg=sql):
                self.conn.execute(sql)
        self.assertEqual(self.conn.execute("SELECT estado, nota FROM propuesta WHERE id = %s", (pid,)).fetchone(), ("rechazada", "Todavía no"))

    def test_quien_propone_no_aprueba_ni_con_sql(self):
        self.una_propuesta()
        with self.assertRaises(psycopg.errors.CheckViolation):
            self.conn.execute("UPDATE propuesta SET estado = 'aprobada', resuelto_por = 'ANA@obra.mx', resuelto_con_rol = 'control_de_obra',"
                              " resuelta_en = now(), resultado = '{}'")  # ni cambiando mayúsculas
        self.conn.execute("UPDATE propuesta SET estado = 'aprobada', resuelto_por = 'luis@obra.mx', resuelto_con_rol = 'control_de_obra',"
                          " resuelta_en = now(), resultado = '{\"hecho\": true}'")
        self.assertEqual(self.conn.execute("SELECT estado FROM propuesta").fetchone()[0], "aprobada")

    def test_una_propuesta_resuelta_trae_quien_cuando_y_una_aprobada_lo_que_se_hizo(self):
        self.una_propuesta()
        resolver = "UPDATE propuesta SET estado = %s, resuelto_por = %s, resuelto_con_rol = %s, resuelta_en = now(), nota = %s, resultado = %s"
        for args in (("rechazada", "luis@obra.mx", "control_de_obra", None, None),  # rechazar sin decir por qué
                     ("rechazada", "luis@obra.mx", "control_de_obra", "   ", None),
                     ("aprobada", "luis@obra.mx", "control_de_obra", None, None),  # aprobar sin dejar lo que se hizo
                     ("rechazada", "", "control_de_obra", "no", None),
                     ("rechazada", "luis@obra.mx", "", "no", None)):
            with self.assertRaises(psycopg.errors.CheckViolation, msg=str(args)):
                self.conn.execute(resolver, args)
        with self.assertRaises(psycopg.errors.CheckViolation):  # resuelta sin quién
            self.conn.execute("UPDATE propuesta SET estado = 'rechazada', nota = 'no', resuelta_en = now()")
        self.assertEqual(self.conn.execute("SELECT estado FROM propuesta").fetchone()[0], "pendiente")

    def test_el_origen_y_el_modelo_van_juntos(self):
        with self.assertRaises(psycopg.errors.CheckViolation):  # un agente dice qué modelo
            self.una_propuesta(origen="agente", por="gravity", rol="agente")
        with self.assertRaises(psycopg.errors.CheckViolation):  # una persona no trae modelo
            self.una_propuesta(modelo="llama")
        with self.assertRaises(psycopg.errors.CheckViolation):
            self.conn.execute(INSERTAR.replace("'es una trabe'", "'  '"), ("usuario", None, "ana@obra.mx", "costos"))
        with self.assertRaises(psycopg.errors.CheckViolation):
            self.conn.execute(INSERTAR.replace("INSERT INTO propuesta (tipo,", "INSERT INTO propuesta (confianza, tipo,")
                              .replace("VALUES ('clonacion'", "VALUES ('altísima', 'clonacion'"), ("usuario", None, "ana@obra.mx", "costos"))
        pid = self.una_propuesta(origen="agente", modelo="llama-3.1-8b", por="gravity", rol="agente")  # (los intentos que fallaron gastaron números)
        self.assertEqual(self.conn.execute("SELECT origen, modelo FROM propuesta WHERE id = %s", (pid,)).fetchone(), ("agente", "llama-3.1-8b"))

    # ------------------------------------------------------------------ lo que solo la base garantiza: alertas
    def test_una_alerta_activa_por_tipo_y_objeto_es_una_sola_fila_y_reaparecer_la_cuenta(self):
        self.bandeja.registrar_alerta("pu_movio_mas_de_5", "ACE-00001", {"antes": "20", "despues": "21"}, {"umbral": "5"})
        a = self.bandeja.registrar_alerta("pu_movio_mas_de_5", "ACE-00001", {"antes": "21", "despues": "23"}, None)
        self.assertEqual((a.veces_vista, dict(a.parametro_usado)), (2, {"umbral": "5"}))  # sin parámetro nuevo, conserva el que había
        with self.assertRaises(psycopg.errors.UniqueViolation):
            self.conn.execute("INSERT INTO alerta (tipo, objeto, evidencia) VALUES ('pu_movio_mas_de_5', 'ACE-00001', '{}')")
        self.assertEqual(self.conn.execute("SELECT count(*) FROM alerta").fetchone()[0], 1)

    def test_dos_procesos_que_ven_lo_mismo_a_la_vez_no_la_repiten_ni_pierden_cuentas(self):
        otra = psycopg.connect(self.servidor.get_uri(), autocommit=True)
        try:
            bandejas = [self.bandeja, PostgresBandeja(otra)]
            veces = 15

            def ver(b):
                for _ in range(veces):
                    b.registrar_alerta("avance_sin_orden", "EST-21011", {"visto": True}, None)

            hilos = [threading.Thread(target=ver, args=(b,)) for b in bandejas]
            [h.start() for h in hilos]
            [h.join() for h in hilos]
        finally:
            otra.close()
        self.assertEqual(self.conn.execute("SELECT count(*), max(veces_vista) FROM alerta").fetchone(), (1, 2 * 15))

    def test_una_alerta_resuelta_se_conserva_y_si_reaparece_es_otra(self):
        a = self.bandeja.registrar_alerta("avance_sin_orden", "EST-21011", {"visto": 1}, None)
        self.bandeja.resolver_alerta(a.id, "resuelta", "sofia@obra.mx", "supervisor", "Se capturó la orden")
        nueva = self.bandeja.registrar_alerta("avance_sin_orden", "EST-21011", {"visto": 2}, None)
        self.assertEqual((nueva.id > a.id, nueva.veces_vista), (True, 1))  # lo resuelto no se reabre: la historia queda como quedó
        self.assertEqual(self.bandeja.alerta(a.id).estado, "resuelta")
        for sql in ("DELETE FROM alerta", "UPDATE alerta SET evidencia = '{}' WHERE estado = 'resuelta'",
                    "UPDATE alerta SET estado = 'activa', resuelto_por = NULL, resuelto_con_rol = NULL, resuelta_en = NULL,"
                    " nota_resolucion = NULL WHERE estado = 'resuelta'",
                    "UPDATE alerta SET tipo = 'otra' WHERE estado = 'activa'"):
            with self.assertRaises(psycopg.errors.RaiseException, msg=sql):  # todas tocan al menos una fila: la resuelta o la activa
                self.conn.execute(sql)
        self.assertEqual(self.bandeja.alerta(a.id).nota_resolucion, "Se capturó la orden")

    def test_una_alerta_no_se_baja_de_cuenta_ni_se_resuelve_sin_decir_que_era(self):
        a = self.bandeja.registrar_alerta("avance_sin_orden", "", {"visto": 1}, None)
        self.bandeja.registrar_alerta("avance_sin_orden", "", {"visto": 2}, None)
        with self.assertRaises(psycopg.errors.RaiseException):
            self.conn.execute("UPDATE alerta SET veces_vista = 1")
        for nota in (None, "  "):
            with self.assertRaises(psycopg.errors.CheckViolation):
                self.conn.execute("UPDATE alerta SET estado = 'descartada', resuelto_por = 'sofia@obra.mx', resuelto_con_rol = 'supervisor',"
                                  " resuelta_en = now(), nota_resolucion = %s", (nota,))
        self.assertEqual((self.bandeja.alerta(a.id).estado, self.bandeja.alerta(a.id).veces_vista), ("activa", 2))

    # ------------------------------------------------------------------ la migración
    def test_la_migracion_siembra_quien_resuelve_la_bandeja(self):
        filas = self.conn.execute(
            "SELECT f.clave, r.clave FROM rol_funcion rf JOIN rol r ON r.id = rf.rol_id JOIN funcion_atomica f ON f.id = rf.funcion_id"
            " WHERE f.clave IN ('aprobar_propuesta', 'resolver_alerta') ORDER BY 1, 2").fetchall()
        self.assertEqual(filas, [("aprobar_propuesta", "control_de_obra"), ("resolver_alerta", "control_de_obra"),
                                 ("resolver_alerta", "supervisor")])


if __name__ == "__main__":
    unittest.main()
