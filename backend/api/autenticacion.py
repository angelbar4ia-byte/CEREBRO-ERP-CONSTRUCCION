"""
Cómo prueba alguien quién es — B-96 (D-469).

La API **no emite tokens ni tiene contraseñas**: verifica los que entrega un proveedor de identidad (Supabase Auth,
Auth0, Keycloak, el que se elija) y se queda solo con el correo que ya comprobó ese proveedor. Con el correo busca al
`USUARIO` (`core/accesos.py`) y de él salen sus roles y, de los roles, lo que puede hacer (`ROL_FUNCION`). Cambiar de
proveedor es cambiar la llave y, a lo más, el nombre del reclamo del correo; nada más de la API se entera.

Se acepta un token solo si:
- trae `exp` y no ha vencido (con un margen de 30 s por relojes desfasados);
- está firmado con el algoritmo de la llave que se configuró: `HS256` con el secreto compartido, o `RS256`/`ES256` con
  una llave de las que publica el proveedor (JWKS) —el algoritmo lo fija el servidor, no el token: un token que diga
  `none`, o `HS256` firmado con la llave pública de otro, no pasa—;
- si se configuraron, coincide en audiencia y emisor;
- trae un correo.

Un token bueno de alguien que no está dado de alta, o que ya se retiró, es 403: el proveedor dice quién es, pero no es
el proveedor quien decide qué puede hacer aquí.

**Las cabeceras `X-Rol` y `X-Usuario`** (la identidad provisional de D-465) siguen existiendo como `modo="cabeceras"` para
trabajar y probar en una máquina propia; en ese modo cualquiera puede decir que es Control de obra. `servir.py` no las
activa sin `--inseguro-cabeceras`.
"""
from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Mapping, Optional, Sequence, Union

import jwt
from fastapi import Depends, Header, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel

from api.errores import _error
from core.accesos import RepositorioAccesos, normalizar_correo

HS = ("HS256",)
ASIMETRICOS = ("RS256", "ES256")
MARGEN_DE_RELOJ = 30  # segundos


class ErrorDeToken(Exception):
    def __init__(self, codigo: str, mensaje: str) -> None:
        super().__init__(mensaje)
        self.codigo = codigo
        self.mensaje = mensaje


class Identidad(BaseModel):
    usuario: str  # lo que queda en la bitácora: el correo en modo token, el nombre que se dijo en modo cabeceras
    roles: List[str]
    nombre: Optional[str] = None
    correo: Optional[str] = None


class VerificadorJWT:
    def __init__(
        self,
        *,
        secreto: Optional[str] = None,
        jwks: Union[None, str, Mapping[str, Any]] = None,
        audiencia: Optional[str] = None,
        emisor: Optional[str] = None,
        reclamo_correo: str = "email",
    ) -> None:
        """`jwks` es el documento con las llaves públicas del proveedor (un diccionario) o la dirección donde lo publica."""
        if not secreto and not jwks:
            raise ValueError("falta una llave: el secreto compartido o las llaves públicas (JWKS) del proveedor")
        self.secreto = secreto or None
        self.audiencia, self.emisor, self.reclamo_correo = audiencia, emisor, reclamo_correo
        self._cliente_jwks = jwt.PyJWKClient(jwks) if isinstance(jwks, str) else None
        self._juego_jwks = jwt.PyJWKSet.from_dict(dict(jwks)) if isinstance(jwks, Mapping) else None

    def _llave(self, token: str, algoritmo: str):
        if algoritmo in HS:
            if self.secreto is None:
                raise ErrorDeToken("token_invalido", "Este servidor no acepta tokens con secreto compartido.")
            return self.secreto
        if algoritmo in ASIMETRICOS:
            sin_llave = ErrorDeToken("token_invalido", "No encuentro la llave con que se firmó ese token.")
            try:
                if self._cliente_jwks is not None:
                    llave = self._cliente_jwks.get_signing_key_from_jwt(token)
                elif self._juego_jwks is not None:
                    kid = jwt.get_unverified_header(token).get("kid")
                    llaves = [k for k in self._juego_jwks.keys if kid is None or k.key_id == kid]
                    if len(llaves) != 1:
                        raise sin_llave
                    llave = llaves[0]
                else:
                    raise ErrorDeToken("token_invalido", "Este servidor no acepta tokens con llave pública.")
            except jwt.PyJWTError:
                raise sin_llave from None
            # una llave de un tipo no sirve para un algoritmo de otro: ES256 con la llave RSA que dijo el `kid`, no
            if getattr(llave, "algorithm_name", algoritmo) != algoritmo:
                raise sin_llave
            return llave.key
        raise ErrorDeToken("token_invalido", "Ese token no usa un algoritmo que este servidor acepte.")

    def correo_de(self, token: str) -> str:
        """El correo que el proveedor comprobó, o por qué no se acepta el token."""
        try:
            algoritmo = jwt.get_unverified_header(token).get("alg")
        except jwt.PyJWTError:
            raise ErrorDeToken("token_invalido", "Eso no es un token.") from None
        llave = self._llave(token, algoritmo)
        try:
            datos = jwt.decode(
                token, llave, algorithms=[algoritmo], audience=self.audiencia, issuer=self.emisor, leeway=MARGEN_DE_RELOJ,
                options={"require": ["exp"], "verify_aud": self.audiencia is not None},
            )
        except jwt.ExpiredSignatureError:
            raise ErrorDeToken("token_vencido", "Tu sesión venció: vuelve a entrar.") from None
        except (jwt.PyJWTError, TypeError, ValueError):  # una llave que no es del tipo que el algoritmo pide también es un token que no sirve
            raise ErrorDeToken("token_invalido", "Ese token no es válido.") from None
        correo = datos.get(self.reclamo_correo)
        if not isinstance(correo, str) or "@" not in correo:
            raise ErrorDeToken("token_sin_correo", f"El token no trae tu correo (reclamo «{self.reclamo_correo}»).")
        return normalizar_correo(correo)


def emitir_token(secreto: str, correo: str, *, horas: float = 8, audiencia: Optional[str] = None, emisor: Optional[str] = None,
                 reclamo_correo: str = "email", ahora: Optional[float] = None) -> str:
    """Un token `HS256` como los que daría el proveedor. **Solo para trabajar y probar**: en producción los emite el proveedor."""
    t = time.time() if ahora is None else ahora
    datos: Dict[str, Any] = {reclamo_correo: correo, "iat": int(t), "exp": int(t + horas * 3600)}
    if audiencia:
        datos["aud"] = audiencia
    if emisor:
        datos["iss"] = emisor
    return jwt.encode(datos, secreto, algorithm="HS256")


# --------------------------------------------------------------------------- lo que la API usa


@dataclass
class Autenticacion:
    """Las dos dependencias de FastAPI que usan las rutas, y lo que las pantallas necesitan saber del modo."""

    modo: str  # "token" · "cabeceras"
    identidad: Callable[..., Identidad]  # quien hace algo: siempre pide saber quién es
    lectura: Callable[..., Optional[Identidad]]  # quien solo ve: en modo token también, en modo cabeceras no
    login_url: Optional[str] = None


_esquema_bearer = HTTPBearer(auto_error=False, description="El token que entrega el proveedor de identidad")


def por_cabeceras() -> Autenticacion:
    def identidad(
        x_rol: Optional[str] = Header(None), x_usuario: Optional[str] = Header(None),
        _bearer: Optional[HTTPAuthorizationCredentials] = Depends(_esquema_bearer),
    ) -> Identidad:
        if not x_rol or not x_usuario:
            raise _error(401, "sin_identidad", "Falta decir quién eres: las cabeceras X-Rol y X-Usuario.")
        return Identidad(usuario=x_usuario, roles=[x_rol])

    def lectura(_bearer: Optional[HTTPAuthorizationCredentials] = Depends(_esquema_bearer)) -> None:
        return None

    return Autenticacion("cabeceras", identidad, lectura)


def por_token(verificador: VerificadorJWT, accesos: RepositorioAccesos, login_url: Optional[str] = None) -> Autenticacion:
    def identidad(credenciales: Optional[HTTPAuthorizationCredentials] = Depends(_esquema_bearer)) -> Identidad:
        if credenciales is None or credenciales.scheme.lower() != "bearer" or not credenciales.credentials:
            raise HTTPException(
                status_code=401, headers={"WWW-Authenticate": "Bearer"},
                detail={"codigo": "sin_token", "mensaje": "Falta iniciar sesión.", "login_url": login_url},
            )
        try:
            correo = verificador.correo_de(credenciales.credentials)
        except ErrorDeToken as e:
            raise HTTPException(
                status_code=401, headers={"WWW-Authenticate": f'Bearer error="{e.codigo}"'},
                detail={"codigo": e.codigo, "mensaje": e.mensaje, "login_url": login_url},
            ) from None
        u = accesos.usuario_por_correo(correo)
        if u is None:
            raise _error(403, "usuario_desconocido", f"Tu correo {correo} no está dado de alta en este sistema.")
        if not u.activo:
            raise _error(403, "usuario_inactivo", "Tu usuario está retirado.")
        return Identidad(usuario=u.correo, roles=list(u.roles), nombre=u.nombre, correo=u.correo)

    return Autenticacion("token", identidad, identidad, login_url)
