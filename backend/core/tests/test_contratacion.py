"""
`ServicioContratacion` sobre el adaptador en memoria del catálogo: el contrato de `contrato_contratacion.py` con los siete presupuestos
de verdad. Postgres corre el mismo contrato en `infra/tests/test_postgres_contratacion.py`.
"""
import unittest

from core.memoria_catalogo import MemoriaCatalogo
from core.tests.contrato_contratacion import ContratoContratacion


class PruebasMemoria(ContratoContratacion, unittest.TestCase):
    def nuevo_repositorio(self):
        return MemoriaCatalogo()


if __name__ == "__main__":
    unittest.main()
