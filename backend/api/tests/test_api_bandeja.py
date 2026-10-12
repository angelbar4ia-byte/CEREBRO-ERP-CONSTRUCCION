"""
La API de la bandeja (D-485) con los adaptadores en memoria: el contrato de `contrato_api_bandeja.py`. El mismo contrato corre contra
Postgres de verdad en `infra/tests/test_postgres_api_bandeja.py`.
"""
import unittest

from api.tests.contrato_api_bandeja import ContratoApiBandeja
from core.accesos import MemoriaAccesos
from core.memoria_bandeja import MemoriaBandeja
from core.memoria_catalogo import MemoriaCatalogo
from core.memoria_programa import MemoriaPrograma


class PruebasApiBandeja(ContratoApiBandeja, unittest.TestCase):
    def nuevos_repositorios(self):
        return MemoriaPrograma(), MemoriaCatalogo(), MemoriaAccesos(), MemoriaBandeja()


if __name__ == "__main__":
    unittest.main()
