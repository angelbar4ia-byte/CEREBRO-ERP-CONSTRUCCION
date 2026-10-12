"""
`ServicioBandeja` sobre los adaptadores en memoria: el contrato de `contrato_bandeja.py` con los tres archivos de OPUS de verdad.
Postgres corre el mismo contrato en `infra/tests/test_postgres_bandeja.py`.
"""
import unittest

from core.memoria_bandeja import MemoriaBandeja
from core.memoria_catalogo import MemoriaCatalogo
from core.tests.contrato_bandeja import ContratoBandeja


class PruebasMemoria(ContratoBandeja, unittest.TestCase):
    def nuevos_repositorios(self):
        return MemoriaBandeja(), MemoriaCatalogo()


if __name__ == "__main__":
    unittest.main()
