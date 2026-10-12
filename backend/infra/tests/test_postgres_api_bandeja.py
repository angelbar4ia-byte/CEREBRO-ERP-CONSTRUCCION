"""
La API de la bandeja (D-485) contra un Postgres de verdad (`pgserver`): el mismo contrato que la memoria
(`api/tests/contrato_api_bandeja.py`), con los cuatro adaptadores —programa, catálogo, accesos y bandeja— sobre la misma conexión, como los
arma `api.servir`. Lo que se comprueba de más es lo que solo la base puede estropear en la respuesta: que lo que Postgres devuelve (jsonb,
fechas) cruce la API igual que lo que devuelve la memoria, y que lo que se aprueba por la API quede escrito en la base a nombre de quien
aprueba. Se salta si faltan `pgserver` y `psycopg`.
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

from api.tests.contrato_api_bandeja import CLONAR, CO, COSTOS, ContratoApiBandeja

if HAY_POSTGRES:
    from infra.postgres_accesos import PostgresAccesos
    from infra.postgres_bandeja import PostgresBandeja
    from infra.postgres_catalogo import PostgresCatalogo
    from infra.postgres_programa import PostgresPrograma, aplicar_migraciones

TABLAS = "propuesta, alerta, carga, presupuesto, nodo, unidad, version_concepto, composicion, precio_historico, programa, usuario"


@unittest.skipUnless(HAY_POSTGRES, "faltan pgserver y psycopg")
class PruebasPostgres(ContratoApiBandeja, unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.dir = tempfile.mkdtemp(prefix="pg_api_bandeja_")
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
        return PostgresPrograma(self.conn), PostgresCatalogo(self.conn), PostgresAccesos(self.conn), PostgresBandeja(self.conn)

    def test_lo_que_se_aprueba_queda_en_la_base_a_nombre_de_quien_aprueba(self):
        self.cargado()
        p = self.c.post("/bandeja/propuestas", json={**CLONAR, "base": 1}, headers=COSTOS).json()
        self.assertEqual(self.c.post(f"/bandeja/propuestas/{p['id']}/resolucion", json={"decision": "aprobar"}, headers=CO).status_code, 200)
        self.assertEqual(self.conn.execute("SELECT estado, propuesto_por, resuelto_por, resuelto_con_rol, resultado->>'clon' FROM propuesta").fetchone(),
                         ("aprobada", "ana@obra.mx", "luis@obra.mx", "control_de_obra", "PRE-00120"))
        self.assertEqual(self.conn.execute("SELECT usuario, rol FROM clon").fetchone(), ("luis@obra.mx", "control_de_obra"))

    def test_servir_arma_la_api_con_la_bandeja_de_postgres(self):
        from api.servir import armar

        self.conn.execute(f"TRUNCATE {TABLAS} RESTART IDENTITY CASCADE")
        app, _ = armar(self.servidor.get_uri(), [], usuarios=["ana@obra.mx|Ana Soto|costos", "luis@obra.mx|Luis Pérez|control_de_obra"])
        from fastapi.testclient import TestClient

        c = TestClient(app)
        r = c.post("/bandeja/propuestas", json=CLONAR, headers=COSTOS)
        self.assertEqual(r.status_code, 201, r.text)
        self.assertEqual(c.post("/bandeja/propuestas/1/resolucion", json={"decision": "rechazar", "nota": "No"}, headers=CO).status_code, 200)
        self.assertEqual(self.conn.execute("SELECT estado, nota FROM propuesta").fetchone(), ("rechazada", "No"))  # en la base, no en la memoria del servidor


if __name__ == "__main__":
    unittest.main()
