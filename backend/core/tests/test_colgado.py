"""
`ServicioColgado` sobre los adaptadores en memoria: el contrato de `contrato_colgado.py` con los siete programas y los siete
presupuestos de verdad. Postgres corre el mismo contrato en `infra/tests/test_postgres_colgado.py`.
"""
import unittest

from core.memoria_catalogo import MemoriaCatalogo
from core.memoria_programa import MemoriaPrograma
from core.tests.contrato_colgado import ContratoColgado


class PruebasMemoria(ContratoColgado, unittest.TestCase):
    def nuevos_repositorios(self):
        return MemoriaPrograma(), MemoriaCatalogo()


if __name__ == "__main__":
    unittest.main()
