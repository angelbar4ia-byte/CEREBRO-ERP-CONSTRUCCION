"""
Lo que todo `RepositorioPrograma` tiene que cumplir, con los programas reales de `1-mundo/programas/`.

No es un módulo de pruebas por sí solo: `test_servicio_programa.py` lo corre contra el adaptador en memoria y
`infra/tests/test_postgres_programa.py`, contra Postgres. Si los dos pasan lo mismo, el servicio no depende de
cuál se use.
"""
from dataclasses import replace
from datetime import date
from fractions import Fraction
from pathlib import Path

from core.motor_cpm import Calendario, Vinculo
from core.programa import (
    AgregarVinculo,
    CambiarDuracion,
    CambiarVinculo,
    FijarInicio,
    QuitarVinculo,
    armar_programa,
    cargar_programa,
    filas_desde_csv,
    reprogramar,
)
from core.servicio_programa import (
    Conflicto,
    NoSePuedeDeshacer,
    PermisoDenegado,
    ProgramaNoExiste,
    ServicioPrograma,
)

RAIZ = Path(__file__).resolve().parents[3]
CAL = Calendario(no_habiles=frozenset({date(2025, 12, 25), date(2026, 1, 1)}))
CSV = RAIZ / "1-mundo" / "programas" / "PROGRAMAS-PROTOTIPOS.csv"
CO, RES = "control_de_obra", "residente"

_cache = {}


def programa(proto):
    if proto not in _cache:
        _cache[proto] = cargar_programa(filas_desde_csv(CSV, proto), CAL)
    return _cache[proto]


class ContratoPrograma:
    """Mezclar con `unittest.TestCase` y definir `nuevo_repositorio()`."""

    def nuevo_repositorio(self):  # pragma: no cover
        raise NotImplementedError

    def setUp(self):
        self.repo = self.nuevo_repositorio()
        self.sv = ServicioPrograma(self.repo)
        self.plus = programa("Zafiro Plus")
        self.pid = self.repo.importar_programa("Zafiro Plus", self.plus, CAL)
        self.f = {x.fila: x.llave for x in self.plus.filas}

    def p16(self, origen=None):
        return AgregarVinculo(self.f[978], self.f[1102], "FS", Fraction(1), origen)

    # ------------------------------------------------------------------ importar y leer
    def test_lo_que_se_importa_se_lee_igual(self):
        g = self.repo.leer_programa(self.pid)
        self.assertEqual((g.nombre, g.version, g.calendario), ("Zafiro Plus", 0, CAL))
        self.assertEqual(g.filas, [replace(f, vinculos="") for f in self.plus.filas])  # sus vínculos ya van resueltos aparte
        self.assertEqual([v for v, _ in g.vinculos], self.plus.vinculos)  # y en el mismo orden
        self.assertEqual({o for _, o in g.vinculos}, {None})  # lo importado viene sin origen declarado
        base = armar_programa(g.filas, [v for v, _ in g.vinculos], g.rechazados, g.calendario)
        self.assertEqual(base.ventanas, self.plus.ventanas)

    def test_los_vinculos_que_el_cargador_rechazo_se_quedan_con_su_motivo(self):
        zafiro = programa("Zafiro")
        pid = self.repo.importar_programa("Zafiro", zafiro, CAL)
        g = self.repo.leer_programa(pid)
        self.assertEqual(len(g.vinculos), 118)
        self.assertEqual(sorted((r.fila, r.token, r.motivo) for r in g.rechazados), sorted((r.fila, r.token, r.motivo) for r in zafiro.rechazados))
        self.assertEqual(len(g.rechazados), 6)

    def test_un_programa_que_no_existe(self):
        with self.assertRaises(ProgramaNoExiste):
            self.repo.leer_programa(987654)
        with self.assertRaises(ProgramaNoExiste):
            self.sv.abrir(987654)

    def test_sin_ediciones_el_vigente_es_la_base(self):
        v = self.sv.abrir(self.pid)
        self.assertEqual(v.programa.ventanas, self.plus.ventanas)
        self.assertEqual((v.aplicadas, v.version), ([], 0))

    # ------------------------------------------------------------------ proponer y aplicar
    def test_proponer_no_guarda_nada(self):
        p = self.sv.proponer(self.pid, self.p16(), CO)
        self.assertTrue(p.aplicable)
        self.assertEqual(p.impacto.dias_de_cambio, 10)
        self.assertEqual(self.repo.ediciones(self.pid), [])
        self.assertEqual(self.repo.leer_programa(self.pid).version, 0)

    def test_aplicar_guarda_lo_que_el_sistema_mostro(self):
        p = self.sv.aplicar(self.pid, self.p16(), CO, "luis")
        g = p.guardada
        self.assertEqual((g.secuencia, g.rol, g.usuario, g.estado), (1, CO, "luis", "aplicada"))
        self.assertEqual(g.impacto["dias_de_cambio"], 10)
        self.assertEqual((g.impacto["fin_antes"], g.impacto["fin_despues"]), ("2026-01-05", "2026-01-19"))
        (leida,) = self.repo.ediciones(self.pid)
        self.assertEqual(leida.edicion, self.p16())  # tal como se pidió; sin declarar, el vínculo nace con origen `decision`
        self.assertEqual(dict(leida.impacto), dict(g.impacto))
        v = self.sv.abrir(self.pid)
        self.assertEqual(v.version, 1)
        self.assertEqual(v.reprogramacion.fin_despues, date(2026, 1, 19))
        self.assertEqual(v.programa.origenes[Vinculo(self.f[978], self.f[1102], "FS", Fraction(1))], "decision")

    def test_el_vigente_es_la_base_mas_las_ediciones_repetidas(self):
        ed = [self.p16(), CambiarDuracion(self.f[982], Fraction(12)), FijarInicio(self.f[1087], date(2025, 10, 30))]
        roles = [CO, CO, RES]
        for e, r in zip(ed, roles):
            self.assertTrue(self.sv.aplicar(self.pid, e, r, "ana").aplicable)
        v = self.sv.abrir(self.pid)
        self.assertEqual(v.programa.ventanas, reprogramar(self.plus, CAL, [self.p16("decision")] + ed[1:]).programa.ventanas)
        self.assertEqual([e.secuencia for e in v.aplicadas], [1, 2, 3])

    def test_la_edicion_vuelve_tal_como_se_pidio(self):
        e = FijarInicio(self.f[1102], date(2025, 10, 28))
        self.sv.aplicar(self.pid, e, RES, "ana")
        c = CambiarVinculo(self.f[978], self.f[1102], "FS", "SS", Fraction(1, 2), "recurso")
        self.sv.aplicar(self.pid, self.p16(), CO, "luis")
        self.sv.aplicar(self.pid, c, CO, "luis")
        self.assertEqual([x.edicion for x in self.repo.ediciones(self.pid)], [e, self.p16(), c])

    def test_una_edicion_que_no_se_puede_aplicar_no_se_guarda(self):
        p = self.sv.aplicar(self.pid, AgregarVinculo(self.f[1102], self.f[1102]), CO, "luis")
        self.assertFalse(p.aplicable)
        self.assertEqual([r.motivo for r in p.rechazadas], ["autovinculo"])
        self.assertIsNone(p.guardada)
        self.assertEqual(self.repo.ediciones(self.pid), [])
        self.assertEqual(self.repo.leer_programa(self.pid).version, 0)

    def test_un_origen_que_no_existe_se_rechaza(self):
        p = self.sv.aplicar(self.pid, self.p16("capricho"), CO, "luis")
        self.assertEqual([r.motivo for r in p.rechazadas], ["origen_invalido"])

    def test_el_origen_declarado_se_guarda(self):
        self.sv.aplicar(self.pid, self.p16("recurso"), CO, "luis")
        v = self.sv.abrir(self.pid)
        self.assertEqual(v.programa.origenes[Vinculo(self.f[978], self.f[1102], "FS", Fraction(1))], "recurso")

    # ------------------------------------------------------------------ permisos
    def test_la_estructura_es_de_control_de_obra_y_las_fechas_del_residente(self):
        with self.assertRaises(PermisoDenegado):
            self.sv.aplicar(self.pid, self.p16(), RES, "ana")
        with self.assertRaises(PermisoDenegado):
            self.sv.aplicar(self.pid, CambiarDuracion(self.f[982], Fraction(9)), "supervisor", "ana")
        with self.assertRaises(PermisoDenegado):
            self.sv.aplicar(self.pid, FijarInicio(self.f[1102], date(2025, 10, 28)), CO, "luis")
        self.assertTrue(self.sv.aplicar(self.pid, FijarInicio(self.f[1102], date(2025, 10, 28)), RES, "ana").aplicable)
        self.assertEqual(len(self.repo.ediciones(self.pid)), 1)

    def test_toda_edicion_dice_quien_la_hizo(self):
        with self.assertRaises(ValueError):
            self.sv.aplicar(self.pid, self.p16(), CO, "")

    # ------------------------------------------------------------------ el candado
    def test_si_alguien_edito_entre_medio_se_dice_y_no_se_pisa(self):
        e = CambiarDuracion(self.f[982], Fraction(9))
        mia = self.sv.proponer(self.pid, e, CO)  # veo la versión 0
        self.sv.aplicar(self.pid, self.p16(), CO, "luis")  # otro edita
        with self.assertRaises(Conflicto):
            self.repo.guardar_edicion(self.pid, e, rol=CO, usuario="ana", impacto=mia.impacto.resumen(), esperaba=mia.esperaba)
        self.assertEqual(len(self.repo.ediciones(self.pid)), 1)

    def test_una_pantalla_vieja_no_aplica_sobre_lo_que_no_vio(self):
        e = CambiarDuracion(self.f[982], Fraction(9))
        visto = self.sv.proponer(self.pid, e, CO).esperaba  # la pantalla vio la versión 0
        self.sv.aplicar(self.pid, self.p16(), CO, "luis")  # otro edita: ya va en la 1
        with self.assertRaises(Conflicto):
            self.sv.aplicar(self.pid, e, CO, "ana", esperaba=visto)
        self.assertEqual(len(self.repo.ediciones(self.pid)), 1)
        # con la versión de hoy sí se aplica, y sin decir cuál vio se aplica sobre lo que haya
        self.assertEqual(self.sv.aplicar(self.pid, e, CO, "ana", esperaba=1).guardada.secuencia, 2)
        self.assertEqual(self.sv.aplicar(self.pid, CambiarDuracion(self.f[982], Fraction(8)), CO, "ana").guardada.secuencia, 3)

    # ------------------------------------------------------------------ deshacer
    def test_deshacer_repite_la_cuenta_sin_la_edicion_y_la_bitacora_se_queda(self):
        a = self.sv.aplicar(self.pid, CambiarDuracion(self.f[982], Fraction(12)), CO, "luis").guardada
        self.sv.aplicar(self.pid, self.p16(), CO, "luis")
        v = self.sv.deshacer(self.pid, a.id, CO, "luis")
        self.assertEqual(v.programa.ventanas, reprogramar(self.plus, CAL, [self.p16("decision")]).programa.ventanas)
        self.assertEqual([e.secuencia for e in v.aplicadas], [2])
        todas = self.repo.ediciones(self.pid)
        self.assertEqual([(e.secuencia, e.estado) for e in todas], [(1, "revertida"), (2, "aplicada")])
        self.assertEqual((todas[0].revertida_por, todas[0].revertida_en is not None), ("luis", True))
        self.assertEqual(v.version, 3)

    def test_no_se_deshace_lo_que_otra_edicion_necesita(self):
        a = self.sv.aplicar(self.pid, self.p16(), CO, "luis").guardada
        self.sv.aplicar(self.pid, CambiarVinculo(self.f[978], self.f[1102], "FS", "SS", Fraction(0)), CO, "luis")
        antes = self.sv.abrir(self.pid)
        with self.assertRaises(NoSePuedeDeshacer) as cm:
            self.sv.deshacer(self.pid, a.id, CO, "luis")
        self.assertEqual(cm.exception.dependientes, (2,))
        despues = self.sv.abrir(self.pid)
        self.assertEqual((despues.version, despues.programa.ventanas), (antes.version, antes.programa.ventanas))

    def test_deshacer_pide_el_permiso_de_la_edicion(self):
        a = self.sv.aplicar(self.pid, self.p16(), CO, "luis").guardada
        with self.assertRaises(PermisoDenegado):
            self.sv.deshacer(self.pid, a.id, RES, "ana")

    def test_lo_ya_revertido_no_se_revierte_otra_vez(self):
        a = self.sv.aplicar(self.pid, self.p16(), CO, "luis").guardada
        self.sv.deshacer(self.pid, a.id, CO, "luis")
        with self.assertRaises(KeyError):
            self.sv.deshacer(self.pid, a.id, CO, "luis")
