"""
Lo que todo `RepositorioAccesos` tiene que cumplir. `test_accesos.py` lo corre contra el adaptador en memoria y
`infra/tests/test_postgres_programa.py`, contra Postgres: si los dos pasan lo mismo, el servicio no depende de cuál se use.

Incluye lo que importa de verdad: que **la tabla manda**. Con el programa real de Zafiro Plus, si `ROL_FUNCION` cambia,
lo que el servicio permite cambia en la siguiente acción, y quien tiene dos roles queda registrado con el que sí puede.
"""
from datetime import date
from fractions import Fraction

from core.accesos import PERMISOS_POR_OMISION, ROLES, UsuarioInvalido
from core.programa import CambiarDuracion, FijarInicio
from core.servicio_programa import PermisoDenegado, ServicioPrograma
from core.tests.contrato_programa import CAL, programa

ESTRUCTURA, FECHAS = "editar_estructura_programa", "editar_fechas_programa"


class ContratoAccesos:
    """Mezclar con `unittest.TestCase` y definir `nuevos_accesos()` (con los permisos por omisión) y `nuevo_repositorio()`."""

    def nuevos_accesos(self):  # pragma: no cover
        raise NotImplementedError

    # ------------------------------------------------------------------ usuarios
    def test_los_permisos_de_partida_son_los_de_modelo_5b(self):
        self.assertEqual(self.nuevos_accesos().permisos(), PERMISOS_POR_OMISION)

    def test_un_usuario_se_encuentra_por_su_correo_sin_importar_mayusculas(self):
        a = self.nuevos_accesos()
        uid = a.agregar_usuario("  Luis Pérez ", "Luis.Perez@Obra.MX ", ["control_de_obra"])
        u = a.usuario_por_correo("LUIS.PEREZ@obra.mx")
        self.assertEqual((u.id, u.nombre, u.correo, u.activo, u.roles), (uid, "Luis Pérez", "luis.perez@obra.mx", True, ("control_de_obra",)))
        self.assertIsNone(a.usuario_por_correo("nadie@obra.mx"))

    def test_un_usuario_puede_tener_mas_de_un_rol(self):
        a = self.nuevos_accesos()
        a.agregar_usuario("Ana", "ana@obra.mx", ["supervisor", "residente", "residente"])
        self.assertEqual(a.usuario_por_correo("ana@obra.mx").roles, ("residente", "supervisor"))  # sin repetir y en orden
        a.agregar_usuario("Sin rol", "sin@obra.mx", [])
        self.assertEqual(a.usuario_por_correo("sin@obra.mx").roles, ())

    def test_los_usuarios_salen_del_mas_viejo_al_mas_nuevo(self):
        a = self.nuevos_accesos()
        for n in ("b", "a", "c"):
            a.agregar_usuario(n, f"{n}@obra.mx", ["costos"])
        self.assertEqual([u.nombre for u in a.usuarios()], ["b", "a", "c"])

    def test_lo_que_no_es_un_usuario_no_se_guarda(self):
        a = self.nuevos_accesos()
        a.agregar_usuario("Luis", "luis@obra.mx", ["residente"])
        for nombre, correo, roles in (("", "x@obra.mx", []), ("  ", "x@obra.mx", []), ("X", "sin-arroba", []), ("X", "@obra.mx", []),
                                      ("X", "x@", []), ("X", "", []), ("X", "x@obra.mx", ["jefe"]), ("Otro Luis", "LUIS@obra.mx", ["residente"])):
            with self.assertRaises(UsuarioInvalido, msg=f"{nombre!r} {correo!r} {roles}"):
                a.agregar_usuario(nombre, correo, roles)
        self.assertEqual([u.correo for u in a.usuarios()], ["luis@obra.mx"])  # y no quedó nada a medias

    def test_un_usuario_se_retira_no_se_borra(self):
        a = self.nuevos_accesos()
        a.agregar_usuario("Luis", "luis@obra.mx", ["residente"])
        a.desactivar_usuario("LUIS@obra.mx")
        u = a.usuario_por_correo("luis@obra.mx")
        self.assertEqual((u.activo, u.roles), (False, ("residente",)))  # sigue ahí, con sus roles
        with self.assertRaises(UsuarioInvalido):
            a.desactivar_usuario("nadie@obra.mx")

    def test_todos_los_roles_de_modelo_existen(self):
        a = self.nuevos_accesos()
        a.agregar_usuario("Todos", "todos@obra.mx", list(ROLES))
        self.assertEqual(set(a.usuario_por_correo("todos@obra.mx").roles), set(ROLES))

    # ------------------------------------------------------------------ la tabla manda
    def test_dar_y_quitar_una_funcion_cambia_los_permisos(self):
        a = self.nuevos_accesos()
        a.dar_funcion("supervisor", FECHAS)
        self.assertEqual(a.permisos()[FECHAS], frozenset({"residente", "supervisor"}))
        a.dar_funcion("supervisor", FECHAS)  # repetirlo no lo duplica ni falla
        a.quitar_funcion("residente", FECHAS)
        self.assertEqual(a.permisos()[FECHAS], frozenset({"supervisor"}))
        a.quitar_funcion("residente", FECHAS)  # ni quitar lo que no está
        with self.assertRaises(UsuarioInvalido):
            a.dar_funcion("jefe", FECHAS)

    def test_el_servicio_obedece_a_la_tabla_y_no_a_una_constante(self):
        a, repo = self.nuevos_accesos(), self.nuevo_repositorio()
        plus = programa("Zafiro Plus")
        pid = repo.importar_programa("Zafiro Plus", plus, CAL)
        f = {x.fila: x.llave for x in plus.filas}
        sv = ServicioPrograma(repo, permisos=a.permisos)
        edicion = CambiarDuracion(f[982], Fraction(12))
        with self.assertRaises(PermisoDenegado):
            sv.aplicar(pid, edicion, "residente", "ana")  # la estructura es de Control de obra
        a.dar_funcion("residente", ESTRUCTURA)  # alguien con `gestionar_rol_funcion` corrige la tabla
        self.assertEqual(sv.aplicar(pid, edicion, "residente", "ana").guardada.rol, "residente")  # y vale en la siguiente acción
        a.quitar_funcion("control_de_obra", ESTRUCTURA)
        with self.assertRaises(PermisoDenegado):
            sv.aplicar(pid, CambiarDuracion(f[982], Fraction(9)), "control_de_obra", "luis")
        with self.assertRaises(PermisoDenegado):
            sv.verificar_importar("control_de_obra")

    def test_quien_tiene_dos_roles_queda_con_el_que_si_puede(self):
        a, repo = self.nuevos_accesos(), self.nuevo_repositorio()
        plus = programa("Zafiro Plus")
        pid = repo.importar_programa("Zafiro Plus", plus, CAL)
        f = {x.fila: x.llave for x in plus.filas}
        sv = ServicioPrograma(repo, permisos=a.permisos)
        mios = ["supervisor", "residente"]  # el supervisor no puede nada del programa; el residente, las fechas
        self.assertEqual(sv.aplicar(pid, FijarInicio(f[1087], date(2025, 10, 30)), mios, "ana").guardada.rol, "residente")
        with self.assertRaises(PermisoDenegado) as cm:
            sv.aplicar(pid, CambiarDuracion(f[982], Fraction(12)), mios, "ana")  # la estructura no es de ninguno de los dos
        self.assertIn("ninguno de tus roles (residente, supervisor)", str(cm.exception))
        with self.assertRaises(PermisoDenegado):
            sv.proponer(pid, CambiarDuracion(f[982], Fraction(12)), [])
        # con los dos roles de verdad, queda el primero en orden alfabético que puede
        a.dar_funcion("supervisor", ESTRUCTURA)
        a.dar_funcion("control_de_obra", ESTRUCTURA)
        self.assertEqual(sv.aplicar(pid, CambiarDuracion(f[982], Fraction(12)), ["supervisor", "control_de_obra"], "ana").guardada.rol, "control_de_obra")
        self.assertEqual(sv.funciones_de(["supervisor", "residente"]), [ESTRUCTURA, FECHAS])
        self.assertEqual(sv.funciones_de("costos"), [])
