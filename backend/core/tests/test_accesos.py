"""El adaptador en memoria de `RepositorioAccesos`, contra el contrato de `contrato_accesos.py`."""
import unittest

from core.accesos import MemoriaAccesos
from core.memoria_programa import MemoriaPrograma
from core.tests.contrato_accesos import ContratoAccesos


class PruebasAccesosEnMemoria(ContratoAccesos, unittest.TestCase):
    def nuevos_accesos(self):
        return MemoriaAccesos()

    def nuevo_repositorio(self):
        return MemoriaPrograma()


if __name__ == "__main__":
    unittest.main()
