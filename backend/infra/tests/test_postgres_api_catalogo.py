"""
La API del catálogo y los presupuestos (D-482) contra un Postgres de verdad (`pgserver`): el mismo contrato que la memoria
(`api/tests/contrato_api_catalogo.py`), con los tres adaptadores —programa, catálogo y accesos— sobre la misma conexión, como los arma
`api.servir`. Lo que se comprueba de más es lo que solo la base puede estropear en la respuesta: que lo que Postgres devuelve (jsonb, fechas,
decimales) cruce la API igual que lo que devuelve la memoria. Se salta si faltan `pgserver` y `psycopg`.
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

from api.tests.contrato_api_catalogo import ContratoApiCatalogo

if HAY_POSTGRES:
    from infra.postgres_accesos import PostgresAccesos
    from infra.postgres_catalogo import PostgresCatalogo
    from infra.postgres_programa import PostgresPrograma, aplicar_migraciones

TABLAS = "carga, presupuesto, nodo, unidad, version_concepto, composicion, precio_historico, programa, usuario"


@unittest.skipUnless(HAY_POSTGRES, "faltan pgserver y psycopg")
class PruebasPostgres(ContratoApiCatalogo, unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.dir = tempfile.mkdtemp(prefix="pg_api_catalogo_")
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
        return PostgresPrograma(self.conn), PostgresCatalogo(self.conn), PostgresAccesos(self.conn)

    def test_servir_arma_la_api_con_el_catalogo_de_postgres(self):
        from fastapi.testclient import TestClient

        from api.servir import armar
        from core.tests.datos_opus import CONCEPTOS, PRESUPUESTO, texto

        self.conn.execute(f"TRUNCATE {TABLAS} RESTART IDENTITY CASCADE")
        app, programas = armar(self.servidor.get_uri(), [], usuarios=["ana@obra.mx|Ana Soto|costos"])
        c = TestClient(app)
        self.assertEqual((programas, c.get("/presupuestos").json()), ([], []))
        r = c.post("/cargas", json={"conceptos": texto(CONCEPTOS), "presupuesto": texto(PRESUPUESTO)}, headers={"X-Rol": "costos", "X-Usuario": "ana@obra.mx"})
        self.assertEqual((r.status_code, r.json()["carga_id"]), (201, 1), r.text)
        self.assertEqual(len(PostgresCatalogo(self.conn).presupuestos()), 7)  # lo escribió en la base, no en la memoria del servidor

    def test_servir_da_a_cada_hilo_su_conexion_y_dos_peticiones_que_se_traslapan_no_se_estorban(self):
        import threading
        import time

        from api.servir import adaptadores_postgres
        from core.tests.contrato_programa import CAL, programa
        from infra.conexion import ConexionPorHilo

        self.conn.execute(f"TRUNCATE {TABLAS} RESTART IDENTITY CASCADE")
        repo, accesos, catalogo = adaptadores_postgres(self.servidor.get_uri())
        self.assertTrue(all(isinstance(x.conn, ConexionPorHilo) for x in (repo, accesos, catalogo)))
        self.assertIs(repo.conn, catalogo.conn)
        errores, ids = [], []

        def larga():  # una escritura que tarda y se revierte
            try:
                with catalogo.conn.transaction():
                    catalogo.conn.execute("INSERT INTO unidad (clave) VALUES ('ZZZ')")
                    time.sleep(0.8)
                    raise RuntimeError("se revierte")
            except RuntimeError:
                pass

        def corta():  # otra petición que llega en medio y se confirma
            try:
                time.sleep(0.2)
                ids.append(repo.importar_programa("Mientras tanto", programa("Zafiro"), CAL))
            except Exception as e:  # pragma: no cover
                errores.append(e)

        hilos = [threading.Thread(target=larga), threading.Thread(target=corta)]
        for h in hilos:
            h.start()
        for h in hilos:
            h.join()
        self.assertEqual(errores, [])
        self.assertEqual(len(ids), 1)
        self.assertEqual([r.nombre for r in repo.listar_programas()], ["Mientras tanto"])
        self.assertEqual(self.conn.execute("SELECT count(*) FROM unidad WHERE clave = 'ZZZ'").fetchone()[0], 0)  # y lo que se revirtió no quedó escrito


if __name__ == "__main__":
    unittest.main()
