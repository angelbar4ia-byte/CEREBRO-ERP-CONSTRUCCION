"""
La reconciliación de un presupuesto que ya existe sobre el adaptador en memoria del catálogo: el contrato de
`contrato_reconciliacion.py` con los siete presupuestos de verdad. Postgres corre el mismo contrato en
`infra/tests/test_postgres_reconciliacion.py`.
"""
import unittest

from core.memoria_catalogo import MemoriaCatalogo
from core.tests.contrato_reconciliacion import ContratoReconciliacion


class PruebasMemoria(ContratoReconciliacion, unittest.TestCase):
    def nuevo_repositorio(self):
        return MemoriaCatalogo()


if __name__ == "__main__":
    unittest.main()
