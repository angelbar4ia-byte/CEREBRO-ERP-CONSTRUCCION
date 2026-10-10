"""
El motor del Gantt en el navegador (`frontend/gantt/motor_gantt.js`) contra `reprogramar` de Python.

La pantalla reprograma sin ir al servidor, y por eso su motor es una segunda implementación de lo mismo.
Esta prueba corre las dos con las mismas ediciones sobre los programas reales y exige el mismo resultado:
el cierre, los días que se mueve, cuántas partidas se corren, la ruta y qué ediciones se rechazan.
Se salta si no hay `node` (el CI de GitHub lo trae).

Correr con: cd backend && python3 -m unittest discover
"""
import json
import shutil
import subprocess
import unittest
from datetime import date
from fractions import Fraction
from pathlib import Path

from core.motor_cpm import Calendario
from core.programa import (
    AgregarVinculo,
    CambiarDuracion,
    CambiarVinculo,
    FijarInicio,
    QuitarVinculo,
    cargar_programa,
    filas_desde_csv,
    reprogramar,
    vista_gantt,
)

RAIZ = Path(__file__).resolve().parents[3]
CAL = Calendario(no_habiles=frozenset({date(2025, 12, 25), date(2026, 1, 1)}))
MOTOR_JS = RAIZ / "frontend" / "gantt" / "motor_gantt.js"

SCRIPT = """
const fs = require('fs');
const Motor = require(process.argv[1]);
const entrada = JSON.parse(fs.readFileSync(0, 'utf8'));
const salida = entrada.escenarios.map(ed => {
  const r = Motor.reprogramar(entrada.red, ed, entrada.modo || 'empuje');
  return { finDespues: entrada.red.dias[r.finDespues], diasDeCambio: r.diasDeCambio, nMovidas: r.nMovidas,
           ruta: r.rutaDespues, rutaCambia: r.rutaCambia, rechazadas: r.rechazadas, nVinculos: r.vinculos.length };
});
process.stdout.write(JSON.stringify(salida));
"""


def _edicion_python(e, por_llave_fila):
    t = e["t"]
    if t == "dur":
        return CambiarDuracion(e["k"], Fraction(e["dias"]))
    if t == "ini":
        return FijarInicio(e["k"], date.fromisoformat(e["fecha"]))
    if t == "add":
        return AgregarVinculo(e["de"], e["a"], e["tipo"], Fraction(e.get("desfase", 0)))
    if t == "del":
        return QuitarVinculo(e["de"], e["a"], e.get("tipo"))
    return CambiarVinculo(e["de"], e["a"], e["tipoActual"], e["tipo"], Fraction(e.get("desfase", 0)))


@unittest.skipUnless(shutil.which("node"), "no hay node")
class PruebasMotorJS(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.prog = cargar_programa(filas_desde_csv(RAIZ / "1-mundo" / "programas" / "PROGRAMAS-PROTOTIPOS.csv", "Zafiro Plus"), CAL)
        cls.red = vista_gantt(cls.prog, CAL, para_editar=True)["red"]
        f = {x.fila: x.llave for x in cls.prog.filas}
        cls.f = f
        v = next(x for x in cls.prog.vinculos if x.tipo == "FS" and x.predecesora in cls.prog.ventanas)
        w = next(x for x in cls.prog.vinculos if x.tipo == "SS")
        nivel2 = next(x.llave for x in cls.prog.filas if x.tipo == "Nivel 2")
        cls.escenarios = [
            [],
            [{"t": "add", "de": f[978], "a": f[1102], "tipo": "FS", "desfase": 1}],
            [{"t": "dur", "k": f[982], "dias": 12}],
            [{"t": "dur", "k": f[982], "dias": 12}, {"t": "add", "de": f[978], "a": f[1102], "tipo": "FS", "desfase": 1}],
            [{"t": "ini", "k": f[1102], "fecha": "2025-10-28"}],
            [{"t": "ini", "k": f[1102], "fecha": "2025-10-14"}],
            [{"t": "ini", "k": f[1102], "fecha": "2025-10-25"}],  # un sábado: arranca el lunes
            [{"t": "del", "de": v.predecesora, "a": v.sucesora}],
            [{"t": "chg", "de": v.predecesora, "a": v.sucesora, "tipoActual": "FS", "tipo": "SS", "desfase": 0}],
            [{"t": "chg", "de": w.predecesora, "a": w.sucesora, "tipoActual": "SS", "tipo": "FS", "desfase": 2}],
            [{"t": "dur", "k": f[1102], "dias": 4}, {"t": "dur", "k": f[1102], "dias": 2}],
            [
                {"t": "dur", "k": "no existe", "dias": 3},
                {"t": "dur", "k": f[1102], "dias": 0},
                {"t": "add", "de": f[1102], "a": f[1102], "tipo": "FS"},
                {"t": "add", "de": f[1102], "a": nivel2, "tipo": "FS"},
                {"t": "add", "de": v.predecesora, "a": v.sucesora, "tipo": v.tipo, "desfase": float(v.desfase)},
                {"t": "add", "de": v.sucesora, "a": v.predecesora, "tipo": "FS"},
                {"t": "del", "de": v.predecesora, "a": "no existe"},
                {"t": "dur", "k": f[982], "dias": 8},
            ],
        ]

    def _con_node(self, escenarios, modo="empuje"):
        entrada = json.dumps({"red": self.red, "escenarios": escenarios, "modo": modo})
        r = subprocess.run(["node", "-e", SCRIPT, str(MOTOR_JS)], input=entrada, capture_output=True, text=True, timeout=120)
        self.assertEqual(r.returncode, 0, r.stderr)
        return json.loads(r.stdout)

    def _con_python(self, ed, modo="empuje"):
        rep = reprogramar(self.prog, CAL, [_edicion_python(e, None) for e in ed], modo)
        return {
            "finDespues": rep.fin_despues.isoformat(),
            "diasDeCambio": rep.dias_de_cambio,
            "nMovidas": len(rep.movidas),
            "ruta": rep.ruta_despues,
            "rutaCambia": rep.ruta_cambia,
            "rechazadas": [x.motivo for x in rep.rechazadas],
            "nVinculos": len(rep.programa.vinculos),
        }

    def test_los_dos_motores_dan_lo_mismo_con_las_mismas_ediciones(self):
        js = self._con_node(self.escenarios)
        for i, (ed, a) in enumerate(zip(self.escenarios, js)):
            self.assertEqual(a, self._con_python(ed), f"escenario {i}: {ed}")

    def test_el_escenario_de_p16_lo_cierra_diez_dias_despues_en_los_dos(self):
        (a,) = self._con_node([self.escenarios[1]])
        self.assertEqual((a["finDespues"], a["diasDeCambio"]), ("2026-01-19", 10))

    def test_el_modo_temprano_tambien_coincide(self):
        ed = [[{"t": "dur", "k": self.f[982], "dias": 12}]]
        (a,) = self._con_node(ed, "temprano")
        self.assertEqual(a, self._con_python(ed[0], "temprano"))


if __name__ == "__main__":
    unittest.main()
