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
    YaReemplazado,
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

    # ------------------------------------------------------------------ la lista y subir un programa
    def test_la_lista_cuenta_lo_que_se_cargo(self):
        zafiro = programa("Zafiro")
        otro = self.sv.importar("  Zafiro de prueba ", zafiro, CAL, CO, "luis")
        a, b = self.sv.listar()  # del más viejo al más nuevo
        self.assertEqual((a.id, a.nombre, a.version, a.ediciones), (self.pid, "Zafiro Plus", 0, 0))
        self.assertEqual((a.partidas, a.vinculos, a.rechazados), (len(self.plus.ventanas), len(self.plus.vinculos), len(self.plus.rechazados)))
        self.assertEqual((a.importado_por, a.importado_con_rol), (None, None))  # cargado sin decir quién: no se inventa
        self.assertEqual((b.id, b.nombre, b.importado_por, b.importado_con_rol), (otro, "Zafiro de prueba", "luis", CO))
        self.assertEqual((b.partidas, b.vinculos, b.rechazados), (len(zafiro.ventanas), 118, 6))
        self.assertIsNotNone(b.creado_en)
        self.assertLessEqual(a.creado_en, b.creado_en)

    def test_la_lista_sigue_las_ediciones_y_las_reversiones(self):
        e = self.sv.aplicar(self.pid, self.p16(), CO, "luis").guardada
        (r,) = self.sv.listar()
        self.assertEqual((r.version, r.ediciones), (1, 1))
        self.sv.deshacer(self.pid, e.id, CO, "luis")
        (r,) = self.sv.listar()
        self.assertEqual((r.version, r.ediciones), (2, 0))  # la versión sube; lo revertido ya no cuenta como aplicado

    def test_subir_un_programa_pide_el_permiso_y_quien(self):
        for rol in (RES, "supervisor"):
            with self.assertRaises(PermisoDenegado):
                self.sv.importar("x", self.plus, CAL, rol, "ana")
            with self.assertRaises(PermisoDenegado):
                self.sv.verificar_importar(rol)
        with self.assertRaises(ValueError):
            self.sv.importar("x", self.plus, CAL, CO, "")
        with self.assertRaises(ValueError):
            self.sv.importar("   ", self.plus, CAL, CO, "luis")
        self.assertEqual(len(self.sv.listar()), 1)  # nada de eso dejó un programa a medias

    def test_un_programa_subido_se_abre_igual_que_el_original(self):
        pid = self.sv.importar("Plus subido", self.plus, CAL, CO, "luis")
        self.assertEqual(self.sv.abrir(pid).programa.ventanas, self.plus.ventanas)
        self.assertTrue(self.sv.aplicar(pid, self.p16(), CO, "luis").aplicable)
        self.assertEqual(self.sv.abrir(self.pid).version, 0)  # editar uno no toca al otro

    # ------------------------------------------------------------------ la versión nueva de un programa
    def _archivo_nuevo(self, cambia=None, sin=()):
        """El programa de Zafiro Plus como lo volvería a subir el planeador, con lo que `cambia` le hace a unas filas."""
        filas = [f for f in self.plus.filas if f.fila not in sin]
        for fila, cambio in (cambia or {}).items():
            filas = [cambio(f) if f.fila == fila else f for f in filas]
        return cargar_programa(filas, CAL)

    @staticmethod
    def _mueve(dias):
        """Corre una partida `dias` días hábiles, sin cambiar lo que dura."""
        return lambda f: replace(f, inicio=CAL.fecha(CAL.n(f.inicio) + dias), termino=CAL.fecha(CAL.n(f.termino) + dias))

    @staticmethod
    def _alarga(dias):
        return lambda f: replace(f, termino=CAL.fecha(CAL.n(f.termino) + dias))

    def _con_historia(self):
        """Tres decisiones sobre Zafiro Plus, de dos personas: la duración de una losa, P16 y el arranque de otra partida."""
        self.sv.aplicar(self.pid, CambiarDuracion(self.f[982], Fraction(12)), CO, "luis")
        self.sv.aplicar(self.pid, self.p16(), CO, "luis")
        self.sv.aplicar(self.pid, FijarInicio(self.f[1087], date(2025, 10, 30)), RES, "ana")

    def test_la_version_nueva_hereda_lo_que_sigue_teniendo_sentido(self):
        self._con_historia()
        nuevo = self._archivo_nuevo()  # el planeador no tocó nada de esas tres partidas
        r = self.sv.subir_version(self.pid, "Zafiro Plus v2", nuevo, CAL, CO, "marta")
        self.assertEqual([n for n in r.no_pasaron], [])
        antes = self.repo.ediciones(self.pid)
        despues = self.repo.ediciones(r.id)
        self.assertEqual([(e.secuencia, e.usuario, e.rol, e.estado) for e in despues], [(1, "luis", CO, "aplicada"), (2, "luis", CO, "aplicada"), (3, "ana", RES, "aplicada")])
        self.assertEqual([e.edicion for e in despues], [e.edicion for e in antes])  # las mismas decisiones, citando el mismo `oid`
        self.assertEqual([e.heredada_de for e in despues], [e.id for e in antes])
        self.assertEqual([e.creada_en for e in despues], [e.creada_en for e in antes])  # se decidieron cuando se decidieron
        self.assertEqual(self.sv.abrir(r.id).programa.ventanas, reprogramar(nuevo, CAL, [e.edicion for e in antes]).programa.ventanas)
        self.assertEqual(self.repo.leer_programa(r.id).version, 3)  # la versión del nuevo va en lo que heredó
        self.assertEqual(self.repo.leer_programa(self.pid).version, 3)  # y el anterior ni se enteró
        self.assertEqual(len([e for e in self.repo.ediciones(self.pid) if e.heredada_de is not None]), 0)

    def test_el_impacto_de_lo_heredado_es_contra_el_programa_nuevo(self):
        self._con_historia()
        nuevo = self._archivo_nuevo()
        r = self.sv.subir_version(self.pid, "v2", nuevo, CAL, CO, "marta")
        ultimo = self.repo.ediciones(r.id)[-1]
        self.assertEqual(ultimo.impacto["fin_despues"], self.sv.abrir(r.id).reprogramacion.fin_despues.isoformat())
        self.assertEqual(self.repo.ediciones(r.id)[1].impacto["dias_de_cambio"], 10)  # P16, otra vez: +10 días hábiles sobre el programa nuevo

    def test_lo_que_la_version_nueva_ya_cambio_gana_el_archivo_y_se_avisa(self):
        self._con_historia()
        # el planeador alargó la losa (982) y corrió la partida 1087: sus dos ediciones viejas ya no se le ponen encima
        nuevo = self._archivo_nuevo({982: self._alarga(3), 1087: self._mueve(2)})
        r = self.sv.subir_version(self.pid, "v2", nuevo, CAL, CO, "marta")
        self.assertEqual([(n.anterior.secuencia, n.motivo) for n in r.no_pasaron],
                         [(1, "la_version_nueva_ya_la_cambio"), (3, "la_version_nueva_ya_la_cambio")])
        self.assertEqual([n.texto for n in r.no_pasaron][0], f"{self.plus.por_llave[self.f[982]].clave} dura 12 d")
        self.assertEqual([e.edicion for e in self.repo.ediciones(r.id)], [self.p16()])  # solo P16 pasó
        self.assertEqual(self.sv.abrir(r.id).programa.ventanas, reprogramar(nuevo, CAL, [self.p16()]).programa.ventanas)

    def test_lo_que_el_motor_rechaza_sobre_la_base_nueva_se_dice_con_su_motivo(self):
        self._con_historia()
        sin_losa = self._archivo_nuevo(sin={982})  # la partida desapareció del programa
        r = self.sv.subir_version(self.pid, "sin la losa", sin_losa, CAL, CO, "marta")
        self.assertEqual([(n.anterior.secuencia, n.motivo) for n in r.no_pasaron], [(1, "actividad_desconocida")])
        ya = self._archivo_nuevo({1102: lambda f: replace(f, vinculos=f.vinculos + ", 978FS+8")})  # el planeador ya escribió P16
        r2 = self.sv.subir_version(r.id, "con P16 escrita", ya, CAL, CO, "marta")
        self.assertEqual([(n.anterior.secuencia, n.motivo) for n in r2.no_pasaron], [(1, "repetido")])

    def test_el_traspaso_queda_guardado_con_lo_que_no_paso(self):
        self._con_historia()
        r = self.sv.subir_version(self.pid, "v2", self._archivo_nuevo({1087: self._mueve(2)}), CAL, CO, "marta")
        g = self.repo.leer_programa(r.id)
        self.assertEqual((g.version_de, g.traspaso["de"], g.traspaso["de_nombre"], g.traspaso["pasaron"]), (self.pid, self.pid, "Zafiro Plus", 2))
        (no,) = g.traspaso["no_pasaron"]
        self.assertEqual((no["secuencia"], no["usuario"], no["rol"], no["motivo"]), (3, "ana", RES, "la_version_nueva_ya_la_cambio"))
        self.assertIn("no arranca antes del 2025-10-30", no["texto"])
        self.assertEqual((self.repo.leer_programa(self.pid).version_de, self.repo.leer_programa(self.pid).traspaso), (None, None))
        a, b = self.sv.listar()
        self.assertEqual((a.reemplazado_por, a.version_de, b.version_de, b.reemplazado_por), (r.id, None, self.pid, None))
        self.assertEqual((b.importado_por, b.importado_con_rol, b.ediciones), ("marta", CO, 2))

    def test_lo_revertido_no_pasa(self):
        e = self.sv.aplicar(self.pid, self.p16(), CO, "luis").guardada
        self.sv.deshacer(self.pid, e.id, CO, "luis")
        r = self.sv.subir_version(self.pid, "v2", self._archivo_nuevo(), CAL, CO, "marta")
        self.assertEqual((self.repo.ediciones(r.id), r.no_pasaron, self.repo.leer_programa(r.id).version), ([], [], 0))

    def test_la_version_nueva_se_sigue_editando_y_la_cadena_es_una_sola(self):
        self._con_historia()
        r = self.sv.subir_version(self.pid, "v2", self._archivo_nuevo(), CAL, CO, "marta")
        p = self.sv.aplicar(r.id, CambiarDuracion(self.f[1102], Fraction(3)), CO, "marta")
        self.assertEqual((p.guardada.secuencia, p.esperaba), (4, 3))
        with self.assertRaises(YaReemplazado) as cm:  # sobre el viejo no: ya tiene versión nueva
            self.sv.subir_version(self.pid, "otra v2", self._archivo_nuevo(), CAL, CO, "marta")
        self.assertEqual(cm.exception.por, r.id)
        r3 = self.sv.subir_version(r.id, "v3", self._archivo_nuevo(), CAL, CO, "marta")  # sobre la última sí
        self.assertEqual(len(self.repo.ediciones(r3.id)), 4)
        self.assertEqual([x.reemplazado_por for x in self.sv.listar()], [r.id, r3.id, None])
        self.assertEqual(len(self.sv.listar()), 3)

    def test_un_programa_con_version_nueva_se_ve_pero_no_se_edita(self):
        self._con_historia()
        r = self.sv.subir_version(self.pid, "v2", self._archivo_nuevo(), CAL, CO, "marta")
        antes = (self.repo.leer_programa(self.pid).version, self.repo.ediciones(self.pid))
        mas = CambiarDuracion(self.f[1102], Fraction(3))
        # ni por el servicio…
        with self.assertRaises(YaReemplazado) as cm:
            self.sv.proponer(self.pid, mas, CO)
        self.assertEqual(cm.exception.por, r.id)
        with self.assertRaises(YaReemplazado):
            self.sv.aplicar(self.pid, mas, CO, "luis")
        with self.assertRaises(YaReemplazado):
            self.sv.deshacer(self.pid, antes[1][0].id, CO, "luis")
        # …ni por el puerto, aunque quien edita traiga la versión al día: el cierre se mira con la fila bloqueada, y antes que la versión
        with self.assertRaises(YaReemplazado):
            self.repo.guardar_edicion(self.pid, mas, rol=CO, usuario="luis", impacto={}, esperaba=antes[0])
        with self.assertRaises(YaReemplazado):
            self.repo.guardar_edicion(self.pid, mas, rol=CO, usuario="luis", impacto={}, esperaba=antes[0] - 1)
        with self.assertRaises(YaReemplazado):
            self.repo.revertir_edicion(self.pid, antes[1][0].id, usuario="luis", esperaba=antes[0])
        # se queda como estaba, con su bitácora, y se sigue viendo
        self.assertEqual((self.repo.leer_programa(self.pid).version, self.repo.ediciones(self.pid)), antes)
        self.assertEqual(self.repo.leer_programa(self.pid).reemplazado_por, r.id)
        self.assertEqual(self.sv.abrir(self.pid).programa.ventanas, reprogramar(self.plus, CAL, [e.edicion for e in antes[1]]).programa.ventanas)
        # y la nueva sí se edita, y deshace lo que heredó
        self.assertIsNone(self.repo.leer_programa(r.id).reemplazado_por)
        self.assertEqual(self.sv.aplicar(r.id, mas, CO, "marta").guardada.secuencia, 4)
        self.sv.deshacer(r.id, self.repo.ediciones(r.id)[0].id, CO, "marta")

    def test_el_traspaso_dice_cuantas_partidas_comparte_el_archivo_nuevo(self):
        n = len(self.plus.ventanas)
        r = self.sv.subir_version(self.pid, "v2", self._archivo_nuevo(), CAL, CO, "marta")
        self.assertEqual((r.partidas_anterior, r.partidas_en_comun), (n, n))
        g = self.repo.leer_programa(r.id)
        self.assertEqual((g.traspaso["partidas_anterior"], g.traspaso["partidas_nueva"], g.traspaso["partidas_en_comun"]), (n, n, n))
        r2 = self.sv.subir_version(r.id, "v3", self._archivo_nuevo(sin={982}), CAL, CO, "marta")  # una partida menos
        self.assertEqual((r2.partidas_anterior, r2.partidas_en_comun), (n, n - 1))
        self.assertEqual(self.repo.leer_programa(r2.id).traspaso["partidas_nueva"], n - 1)

    def test_las_partidas_se_reconocen_por_oid_y_el_archivo_de_otro_programa_no_pasa_nada(self):
        """Casar por clave sería adivinar: en el mismo Zafiro Plus hay claves que se repiten. Y casar por fila, peor: se corre."""
        claves = [f.clave for f in self.plus.filas if f.llave in self.plus.ventanas]
        self.assertGreater(len(claves), len(set(claves)))
        self._con_historia()
        rubi = programa("Rubí")  # otro programa real, que no comparte ni un `oid` con Zafiro Plus
        r = self.sv.subir_version(self.pid, "Rubí por error", rubi, CAL, CO, "marta")
        self.assertEqual((r.partidas_en_comun, r.partidas_anterior, len(r.pasaron)), (0, len(self.plus.ventanas), 0))
        self.assertEqual([(n.anterior.secuencia, n.motivo) for n in r.no_pasaron], [(i, "actividad_desconocida") for i in (1, 2, 3)])
        self.assertEqual(self.repo.ediciones(r.id), [])  # nada se forzó

    def test_una_version_nueva_que_se_pide_con_una_pantalla_vieja_no_se_sube(self):
        self.sv.aplicar(self.pid, self.p16(), CO, "luis")
        visto = self.sv.abrir(self.pid).version
        self.sv.aplicar(self.pid, CambiarDuracion(self.f[982], Fraction(12)), CO, "luis")  # otro editó entre medio
        with self.assertRaises(Conflicto):
            self.sv.subir_version(self.pid, "v2", self._archivo_nuevo(), CAL, CO, "marta", esperaba=visto)
        self.assertEqual(len(self.sv.listar()), 1)  # y no quedó nada a medias
        r = self.sv.subir_version(self.pid, "v2", self._archivo_nuevo(), CAL, CO, "marta", esperaba=visto + 1)
        self.assertEqual(len(self.repo.ediciones(r.id)), 2)

    def test_subir_una_version_pide_el_permiso_quien_y_nombre_y_el_programa_existe(self):
        nuevo = self._archivo_nuevo()
        with self.assertRaises(PermisoDenegado):
            self.sv.subir_version(self.pid, "v2", nuevo, CAL, RES, "ana")  # aunque lo heredado incluya fechas de Residente
        with self.assertRaises(ValueError):
            self.sv.subir_version(self.pid, "v2", nuevo, CAL, CO, "")
        with self.assertRaises(ValueError):
            self.sv.subir_version(self.pid, "  ", nuevo, CAL, CO, "marta")
        with self.assertRaises(ProgramaNoExiste):
            self.sv.subir_version(987654, "v2", nuevo, CAL, CO, "marta")
        self.assertEqual(len(self.sv.listar()), 1)

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
