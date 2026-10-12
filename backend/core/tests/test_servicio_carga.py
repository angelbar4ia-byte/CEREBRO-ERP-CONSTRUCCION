"""
El servicio de carga y el adaptador en memoria, contra el contrato de `contrato_catalogo.py`, con los archivos de verdad.
El mismo contrato corre contra Postgres en `infra/tests/test_postgres_catalogo.py`.
"""
import unittest

from core.memoria_catalogo import MemoriaCatalogo
from core.tests.contrato_catalogo import ContratoCatalogo


class PruebasMemoria(ContratoCatalogo, unittest.TestCase):
    def nuevo_repositorio(self):
        return MemoriaCatalogo()


if __name__ == "__main__":
    unittest.main()
