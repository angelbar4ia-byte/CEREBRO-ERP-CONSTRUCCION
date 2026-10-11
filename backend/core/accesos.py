"""
Quién es cada quien y qué puede hacer — `1-mundo/MODELO.md` §5b (D-204 a D-206, D-329, B-74).

`MODELO.md` ya decidió que quién puede qué **es una tabla** (`ROL_FUNCION`) y no una regla de código, para poder
corregirla sin tocar esquema (`gestionar_rol_funcion`). Este módulo es esa tabla vista desde el dominio: el puerto
`RepositorioAccesos` entrega el usuario que corresponde a un correo, con los roles que tiene, y los permisos vigentes;
`MemoriaAccesos` es el adaptador para las pruebas y `infra/postgres_accesos.py` el de Postgres.

Un usuario puede tener más de un rol (`USUARIO_ROL` es muchos a muchos, D-205). Lo que decide una acción es si **alguno**
de sus roles tiene la función; el rol con que queda registrada es el primero que la tiene.

Aquí no hay autenticación: este módulo no sabe cómo prueba alguien quién es. Eso es de la API (`api/autenticacion.py`),
que entrega un correo ya comprobado y pregunta aquí quién es.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Dict, FrozenSet, Iterable, List, Mapping, Optional, Protocol, Sequence, Tuple


class PermisoDenegado(Exception):
    """El rol no puede hacer eso."""


class UsuarioInvalido(ValueError):
    """Lo que se quiso guardar de un usuario no se puede: nombre o correo vacíos, correo repetido, rol que no existe."""


# `MODELO.md` §5b: seis roles. Se llaman por su clave; `control_de_obra` es el «Control» del enum y el «Control de obra» del texto.
ROLES: Dict[str, str] = {
    "residente": "Residente",
    "supervisor": "Supervisor",
    "superintendente": "Superintendente",
    "costos": "Costos",
    "cotizador": "Cotizador",
    "control_de_obra": "Control de obra",
}

# Las funciones que ya tienen código detrás y quién las tiene (`MODELO.md` §5b, lista completa: «§5c, D-329»). El resto
# de las treinta y cuatro se agrega cuando haya un módulo que la use: este cerebro no asigna sin un caso.
PERMISOS_POR_OMISION: Dict[str, FrozenSet[str]] = {
    "editar_estructura_programa": frozenset({"control_de_obra"}),
    "editar_fechas_programa": frozenset({"residente"}),
}


@dataclass(frozen=True)
class Usuario:
    id: int
    nombre: str
    correo: str  # en minúsculas: es con lo que se le encuentra
    activo: bool
    roles: Tuple[str, ...]  # claves de rol, en orden alfabético


def normalizar_correo(correo: str) -> str:
    return (correo or "").strip().lower()


class RepositorioAccesos(Protocol):
    def usuario_por_correo(self, correo: str) -> Optional[Usuario]:
        """El usuario con ese correo (sin importar mayúsculas), esté activo o no; `None` si no existe."""

    def usuarios(self) -> List[Usuario]:
        """Todos, del más viejo al más nuevo."""

    def agregar_usuario(self, nombre: str, correo: str, roles: Sequence[str]) -> int:
        """Lo da de alta, activo. `UsuarioInvalido` si el nombre o el correo van vacíos, el correo ya existe o un rol no existe."""

    def desactivar_usuario(self, correo: str) -> None:
        """Se retira, no se borra (`MODELO.md` §5b): su nombre sigue en la bitácora."""

    def permisos(self) -> Dict[str, FrozenSet[str]]:
        """Función → los roles que la tienen: `ROL_FUNCION`, leída hoy."""

    def dar_funcion(self, rol: str, funcion: str) -> None: ...

    def quitar_funcion(self, rol: str, funcion: str) -> None: ...


def validar_usuario(nombre: str, correo: str, roles: Iterable[str]) -> Tuple[str, str, Tuple[str, ...]]:
    """Lo común a los dos adaptadores: lo que se guarda, o por qué no."""
    nombre, correo = (nombre or "").strip(), normalizar_correo(correo)
    if not nombre:
        raise UsuarioInvalido("todo usuario lleva nombre")
    if "@" not in correo or correo.startswith("@") or correo.endswith("@"):
        raise UsuarioInvalido(f"«{correo}» no es un correo")
    roles = tuple(sorted(set(roles)))
    desconocidos = [r for r in roles if r not in ROLES]
    if desconocidos:
        raise UsuarioInvalido(f"no existe el rol {', '.join(desconocidos)}; los roles son {', '.join(ROLES)}")
    return nombre, correo, roles


class MemoriaAccesos:
    """El adaptador en memoria: mismo contrato que el de Postgres (`core/tests/contrato_accesos.py`)."""

    def __init__(self) -> None:
        self._usuarios: Dict[int, Usuario] = {}
        self._permisos: Dict[str, FrozenSet[str]] = dict(PERMISOS_POR_OMISION)
        self._sig = 0

    def usuario_por_correo(self, correo: str) -> Optional[Usuario]:
        c = normalizar_correo(correo)
        return next((u for u in self._usuarios.values() if u.correo == c), None)

    def usuarios(self) -> List[Usuario]:
        return [self._usuarios[i] for i in sorted(self._usuarios)]

    def agregar_usuario(self, nombre: str, correo: str, roles: Sequence[str]) -> int:
        nombre, correo, roles = validar_usuario(nombre, correo, roles)
        if self.usuario_por_correo(correo) is not None:
            raise UsuarioInvalido(f"ya hay un usuario con el correo {correo}")
        self._sig += 1
        self._usuarios[self._sig] = Usuario(self._sig, nombre, correo, True, roles)
        return self._sig

    def desactivar_usuario(self, correo: str) -> None:
        u = self.usuario_por_correo(correo)
        if u is None:
            raise UsuarioInvalido(f"no hay un usuario con el correo {normalizar_correo(correo)}")
        self._usuarios[u.id] = replace(u, activo=False)

    def permisos(self) -> Dict[str, FrozenSet[str]]:
        return dict(self._permisos)

    def dar_funcion(self, rol: str, funcion: str) -> None:
        if rol not in ROLES:
            raise UsuarioInvalido(f"no existe el rol {rol}")
        self._permisos[funcion] = self._permisos.get(funcion, frozenset()) | {rol}

    def quitar_funcion(self, rol: str, funcion: str) -> None:
        self._permisos[funcion] = self._permisos.get(funcion, frozenset()) - {rol}
