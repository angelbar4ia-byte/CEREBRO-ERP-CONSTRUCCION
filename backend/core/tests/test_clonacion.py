"""
`ServicioClonacion` sobre el adaptador en memoria del catálogo: el contrato de `contrato_clonacion.py` con los tres archivos de OPUS de
verdad. Postgres corre el mismo contrato en `infra/tests/test_postgres_clonacion.py`.
"""
import unittest

from core.memoria_catalogo import MemoriaCatalogo
from core.tests.contrato_clonacion import ContratoClonacion


class PruebasMemoria(ContratoClonacion, unittest.TestCase):
    def nuevo_repositorio(self):
        return MemoriaCatalogo()


if __name__ == "__main__":
    unittest.main()
