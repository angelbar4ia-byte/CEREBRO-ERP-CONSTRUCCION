"""
El servicio de programa y el adaptador en memoria, contra el contrato de `contrato_programa.py`.
El mismo contrato corre contra Postgres en `infra/tests/test_postgres_programa.py`.
"""
import unittest

from core.memoria_programa import MemoriaPrograma
from core.motor_cpm import Calendario
from core.programa import CambiarDuracion
from core.servicio_programa import ETIQUETA_DE_PERMISO, PermisoDenegado, verificar_permiso
from core.tests.contrato_programa import ContratoPrograma


class PruebasMemoria(ContratoPrograma, unittest.TestCase):
    def nuevo_repositorio(self):
        return MemoriaPrograma()


class PruebasPermiso(unittest.TestCase):
    def test_el_mensaje_dice_que_no_se_puede_en_palabras(self):
        with self.assertRaises(PermisoDenegado) as cm:
            verificar_permiso(CambiarDuracion("x", 3), "residente")
        self.assertIn(ETIQUETA_DE_PERMISO["editar_estructura_programa"], str(cm.exception))

    def test_una_edicion_desconocida_no_pasa(self):
        with self.assertRaises(TypeError):
            verificar_permiso(object(), "control_de_obra")


if __name__ == "__main__":
    unittest.main()
