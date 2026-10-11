"""
La API del catálogo y los presupuestos (D-482) con los adaptadores en memoria: el contrato de `contrato_api_catalogo.py`. El mismo
contrato corre contra Postgres de verdad en `infra/tests/test_postgres_api_catalogo.py`.
"""
import unittest

from api.tests.contrato_api_catalogo import ContratoApiCatalogo
from core.accesos import MemoriaAccesos
from core.memoria_catalogo import MemoriaCatalogo
from core.memoria_programa import MemoriaPrograma


class PruebasApiCatalogo(ContratoApiCatalogo, unittest.TestCase):
    def nuevos_repositorios(self):
        return MemoriaPrograma(), MemoriaCatalogo(), MemoriaAccesos()


if __name__ == "__main__":
    unittest.main()
