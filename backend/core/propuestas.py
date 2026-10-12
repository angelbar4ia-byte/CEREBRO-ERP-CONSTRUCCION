"""
La bandeja de propuestas y de alertas — `1-mundo/CONOCIMIENTO.md` §14, `1-mundo/MODELO.md` §5 y §5a, `2-operacion/WORKFLOWS.md`, D-485.

«El sistema propone y el humano decide» aparecía nueve veces; sin una bandeja única, quien decide tendría nueve y el agente interno
no tendría dónde dejar lo que propone. Dos cosas viven aquí, y no son lo mismo:

- **La propuesta** sugiere un valor concreto para un objeto concreto, con su evidencia. Una persona o el agente la deja; **otra
  persona** la aprueba o la rechaza. Lo rechazado se conserva, y no se vuelve a proponer sin evidencia que no existía antes. Sin un
  valor que proponer no es una propuesta: es una alerta.
- **La alerta** señala algo que no cuadra y no sugiere nada. Si reaparece sin haberse resuelto, se cuenta (`veces_vista`), no se
  repite. Detectar no pide permiso; resolver, sí; y una alerta nunca se resuelve sola.

**Aprobar una propuesta pide la misma función que pediría hacer a mano lo que propone** (`WORKFLOWS.md` §3.1), y lo que se propone se
ejecuta con la identidad de quien aprueba, nunca con la del agente: la bandeja no le da poder a nadie. Por eso aprobar pide dos cosas
—`aprobar_propuesta`, que es resolver la bandeja, y la función de la acción— y por eso **solo se puede aprobar un tipo que tenga
operación en el sistema** (hoy, `clonacion`): los demás se pueden proponer y rechazar, pero aprobar lo que nada ejecuta sería decir que
algo se hizo cuando no se hizo.

La propuesta trae `base` —la última carga que vio quien propone—; al aprobarla viaja a la aplicación como `esperaba`, así que quien
aprueba no puede aprobar algo distinto de lo que se vio. Si la operación falla, la propuesta sigue pendiente: se corrige o se rechaza.

Este módulo no sabe de ninguna base ni de FastAPI: define lo que se guarda, el puerto y el servicio. `core/memoria_bandeja.py` y
`infra/postgres_bandeja.py` son los adaptadores, y los dos cumplen el mismo contrato (`core/tests/contrato_bandeja.py`).
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Callable, Dict, List, Mapping, Optional, Protocol

from .clonacion import MODOS, ClonacionNoProcede, ServicioClonacion
from .servicio_programa import PermisoDenegado, Roles, rol_efectivo

FUNCION_DE_RESOLVER_PROPUESTA = "aprobar_propuesta"
FUNCION_DE_RESOLVER_ALERTA = "resolver_alerta"

ESTADOS_DE_PROPUESTA = ("pendiente", "aprobada", "rechazada")
ESTADOS_DE_ALERTA = ("activa", "resuelta", "descartada")
ORIGENES = ("usuario", "agente")
CONFIANZAS = ("alta", "media", "baja")
DECISIONES = ("aprobar", "rechazar")

# `MODELO.md` §5 (los nueve) y §5b (`precio_nuevo`). Abierto: crece igual que `PROPUESTA.tipo`.
TIPOS_CONOCIDOS = ("equivalencia", "version", "reparto", "conversion", "matriz_generada", "fusion", "clonacion", "orden_cambio",
                   "patron_carga", "precio_nuevo")


# --------------------------------------------------------------------------- lo que no procede


class PropuestaInvalida(ValueError):
    """Lo que se quiso proponer, alertar o resolver no se puede: sin evidencia, sin valor que proponer, un tipo que no existe…"""


class PropuestaNoExiste(KeyError):
    pass


class AlertaNoExiste(KeyError):
    pass


class YaResuelta(Exception):
    """Ya la resolvió alguien: una propuesta o una alerta se resuelve una vez."""

    def __init__(self, mensaje: str, estado: str) -> None:
        super().__init__(mensaje)
        self.estado = estado


class YaPropuesta(Exception):
    """Ya hay una igual pendiente: se resuelve esa, no se amontona otra."""

    def __init__(self, mensaje: str, propuesta_id: int) -> None:
        super().__init__(mensaje)
        self.propuesta_id = propuesta_id


class RechazadaAntes(Exception):
    """Ya se rechazó y esta no trae evidencia nueva: el rechazo se conserva justo para que no se insista (`CONOCIMIENTO.md` §14.3)."""

    def __init__(self, mensaje: str, propuesta_id: int) -> None:
        super().__init__(mensaje)
        self.propuesta_id = propuesta_id


class AutoAprobacion(Exception):
    """Quien propone no aprueba lo suyo (D-269): otra persona."""


class SinOperacion(Exception):
    """Ese tipo de propuesta todavía no tiene operación en el sistema: se puede rechazar, no aprobar."""

    def __init__(self, mensaje: str, tipo: str) -> None:
        super().__init__(mensaje)
        self.tipo = tipo


# --------------------------------------------------------------------------- lo que se guarda


@dataclass(frozen=True)
class NuevaPropuesta:
    tipo: str
    objeto: str
    valor_propuesto: Mapping[str, Any]
    evidencia: str
    origen: str
    propuesto_por: str
    propuesto_con_rol: str
    modelo: Optional[str] = None
    version_modelo: Optional[str] = None
    confianza: Optional[str] = None
    supuestos: Optional[Mapping[str, Any]] = None
    base: Optional[int] = None


@dataclass(frozen=True)
class Propuesta:
    id: int
    tipo: str
    objeto: str
    valor_propuesto: Mapping[str, Any]
    evidencia: str
    origen: str
    propuesto_por: str
    propuesto_con_rol: str
    creada_en: datetime
    estado: str
    modelo: Optional[str] = None
    version_modelo: Optional[str] = None
    confianza: Optional[str] = None
    supuestos: Optional[Mapping[str, Any]] = None
    base: Optional[int] = None
    resuelto_por: Optional[str] = None
    resuelto_con_rol: Optional[str] = None
    resuelta_en: Optional[datetime] = None
    nota: Optional[str] = None
    resultado: Optional[Mapping[str, Any]] = None


@dataclass(frozen=True)
class Alerta:
    id: int
    tipo: str
    objeto: str  # vacío si no hay un objeto al que apuntar
    evidencia: Mapping[str, Any]
    parametro_usado: Optional[Mapping[str, Any]]
    primera_vez: datetime
    ultima_vez: datetime
    veces_vista: int
    estado: str
    resuelto_por: Optional[str] = None
    resuelto_con_rol: Optional[str] = None
    resuelta_en: Optional[datetime] = None
    nota_resolucion: Optional[str] = None


@dataclass(frozen=True)
class ResumenDeBandeja:
    """Lo que tiene pendiente quien decide: el motivo de que la bandeja sea una sola."""

    propuestas_pendientes: int
    pendientes_por_tipo: Mapping[str, int]
    alertas_activas: int
    alertas_por_tipo: Mapping[str, int]
    alerta_mas_vista: Optional[Alerta] = None


class RepositorioBandeja(Protocol):
    def agregar_propuesta(self, nueva: NuevaPropuesta) -> Propuesta: ...

    def propuesta(self, propuesta_id: int) -> Propuesta:
        """`PropuestaNoExiste` si no hay."""

    def propuestas(self, estado: Optional[str] = None, tipo: Optional[str] = None) -> List[Propuesta]:
        """Por número, de la más vieja a la más nueva."""

    def parecidas(self, tipo: str, objeto: str, valor_propuesto: Mapping[str, Any]) -> List[Propuesta]:
        """Las que recaen en lo mismo y proponen lo mismo, en cualquier estado."""

    def resolver_propuesta(self, propuesta_id: int, estado: str, usuario: str, rol: str, nota: Optional[str],
                           resultado: Optional[Mapping[str, Any]]) -> Propuesta:
        """Pasa una pendiente a aprobada o rechazada. `YaResuelta` si ya no estaba pendiente; `PropuestaNoExiste` si no hay."""

    def registrar_alerta(self, tipo: str, objeto: str, evidencia: Mapping[str, Any], parametro_usado: Optional[Mapping[str, Any]]) -> Alerta:
        """Si hay una activa del mismo tipo y objeto, la cuenta otra vez (y le pone la evidencia de hoy); si no, nace."""

    def alerta(self, alerta_id: int) -> Alerta: ...

    def alertas(self, estado: Optional[str] = None, tipo: Optional[str] = None) -> List[Alerta]: ...

    def resolver_alerta(self, alerta_id: int, estado: str, usuario: str, rol: str, nota: str) -> Alerta:
        """`YaResuelta` si ya no estaba activa; `AlertaNoExiste` si no hay."""


# --------------------------------------------------------------------------- los tipos y lo que hacen al aprobarse


Ejecutar = Callable[[Mapping[str, Any], Roles, str, Optional[int]], Mapping[str, Any]]


@dataclass(frozen=True)
class TipoDePropuesta:
    clave: str
    funcion: Optional[str] = None  # la que pide aprobarla, además de `aprobar_propuesta`: la de la acción
    normalizar: Optional[Callable[[str, Mapping[str, Any]], Dict[str, Any]]] = None
    ejecutar: Optional[Ejecutar] = None  # la operación del sistema; sin ella, no se puede aprobar

    @property
    def ejecutable(self) -> bool:
        return self.ejecutar is not None


def _texto(valor: Mapping[str, Any], campo: str) -> str:
    x = valor.get(campo)
    if not isinstance(x, str) or not x.strip():
        raise PropuestaInvalida(f"falta «{campo}» en lo que se propone")
    return x.strip()


def _entero(valor: Mapping[str, Any], campo: str, por_omision: int, minimo: int) -> int:
    x = valor.get(campo, por_omision)
    if isinstance(x, bool) or not isinstance(x, int) or x < minimo:
        raise PropuestaInvalida(f"«{campo}» debe ser un número entero de {minimo} o más")
    return x


def _normalizar_clonacion(objeto: str, valor: Mapping[str, Any]) -> Dict[str, Any]:
    """Una clonación (`original`, `clave`, `modo`) o la corrección de un prefijo entero (`viejo`, `nuevo`, `desde`)."""
    if "viejo" in valor or "nuevo" in valor:
        sobran = set(valor) - {"viejo", "nuevo", "desde"}
        if sobran:
            raise PropuestaInvalida(f"una corrección de prefijo no trae {', '.join(sorted(sobran))}")
        viejo, nuevo = _texto(valor, "viejo"), _texto(valor, "nuevo")
        if viejo == nuevo:
            raise PropuestaInvalida("el prefijo viejo y el nuevo deben ser distintos")
        if objeto != viejo:
            raise PropuestaInvalida(f"la propuesta recae en el prefijo {viejo}, no en {objeto}")
        return {"viejo": viejo, "nuevo": nuevo, "desde": _entero(valor, "desde", 1, 1)}
    sobran = set(valor) - {"original", "clave", "modo"}
    if sobran:
        raise PropuestaInvalida(f"una clonación no trae {', '.join(sorted(sobran))}")
    original, clave = _texto(valor, "original"), _texto(valor, "clave")
    modo = valor.get("modo", "sustituir")
    if modo not in MODOS:
        raise PropuestaInvalida(f"el modo debe ser uno de: {', '.join(MODOS)}")
    if original == clave:
        raise PropuestaInvalida("el clon necesita una clave distinta de la del original")
    if objeto != original:
        raise PropuestaInvalida(f"la propuesta recae en {original}, no en {objeto}")
    return {"original": original, "clave": clave, "modo": modo}


def _ejecutor_de_clonacion(servicio: ServicioClonacion) -> Ejecutar:
    def ejecutar(valor: Mapping[str, Any], rol: Roles, usuario: str, esperaba: Optional[int]) -> Mapping[str, Any]:
        if "viejo" in valor:
            r = servicio.corregir_prefijo(valor["viejo"], valor["nuevo"], valor["desde"], rol, usuario, esperaba)
            if not r.hechos and r.rechazados:
                problemas = tuple(x for p in r.rechazados for x in p.problemas)
                raise ClonacionNoProcede("no se pudo sustituir ninguna clave: " + "; ".join(problemas[:3]), problemas)
            return {
                "hechos": [{"original": o, "clon": k, "carga_id": x.carga_id, "versiones_nuevas": x.versiones_nuevas,
                            "renglones_fijados": x.renglones_fijados} for o, k, x in r.hechos],
                "rechazados": [{"original": p.original, "clon": p.clave, "problemas": list(p.problemas)} for p in r.rechazados],
                "versiones_nuevas": sum(x.versiones_nuevas for _, _, x in r.hechos),
                "renglones_fijados": sum(x.renglones_fijados for _, _, x in r.hechos),
            }
        _, r = servicio.clonar(valor["original"], valor["clave"], valor["modo"], rol, usuario, esperaba)
        return {"clon": valor["clave"], "modo": valor["modo"], "carga_id": r.carga_id, "versiones_nuevas": r.versiones_nuevas,
                "renglones_fijados": r.renglones_fijados}

    return ejecutar


# Las funciones de la acción que ya tienen dueño en `MODELO.md` §5b. El resto de los tipos no tiene función ni operación todavía.
FUNCION_DE_LA_ACCION = {"clonacion": "clonar_insumo", "precio_nuevo": "aprobar_precio_nuevo", "orden_cambio": "autorizar_orden_cambio"}


def tipos_de_propuesta(clonacion: Optional[ServicioClonacion] = None) -> Dict[str, TipoDePropuesta]:
    """Los tipos que la bandeja conoce y cuáles se pueden aprobar. Sin el servicio que lo ejecuta, un tipo se puede proponer y rechazar."""
    tipos = {t: TipoDePropuesta(t, FUNCION_DE_LA_ACCION.get(t)) for t in TIPOS_CONOCIDOS}
    tipos["clonacion"] = TipoDePropuesta(
        "clonacion", FUNCION_DE_LA_ACCION["clonacion"], _normalizar_clonacion,
        None if clonacion is None else _ejecutor_de_clonacion(clonacion))
    return tipos


# --------------------------------------------------------------------------- el servicio


def _huella(texto: str) -> str:
    return " ".join(texto.split()).casefold()


def _a_json(x: Mapping[str, Any], que: str) -> Dict[str, Any]:
    try:
        return json.loads(json.dumps(dict(x), sort_keys=True))
    except (TypeError, ValueError):
        raise PropuestaInvalida(f"{que} debe poder escribirse como JSON") from None


def _rol_de(roles: Roles) -> str:
    mios = (roles,) if isinstance(roles, str) else tuple(roles)
    return sorted(mios)[0] if mios else ""


class ServicioBandeja:
    def __init__(
        self,
        repositorio: RepositorioBandeja,
        permisos: Optional[Callable[[], Mapping[str, Any]]] = None,
        tipos: Optional[Mapping[str, TipoDePropuesta]] = None,
    ) -> None:
        """`permisos` entrega `ROL_FUNCION` tal como está hoy (`RepositorioAccesos.permisos`); sin ella, la tabla por omisión.
        `tipos` dice qué se puede aprobar y cómo (`tipos_de_propuesta`)."""
        self.repo = repositorio
        self._permisos = permisos
        self.tipos: Mapping[str, TipoDePropuesta] = tipos if tipos is not None else tipos_de_propuesta()

    def _tabla(self) -> Optional[Mapping[str, Any]]:
        return None if self._permisos is None else self._permisos()

    def rol_para(self, funcion: str, roles: Roles) -> str:
        return rol_efectivo(funcion, roles, self._tabla())

    # ---- propuestas
    def proponer(
        self,
        tipo: str,
        objeto: str,
        valor_propuesto: Mapping[str, Any],
        evidencia: str,
        *,
        usuario: str,
        rol: Roles = (),
        origen: str = "usuario",
        modelo: Optional[str] = None,
        version_modelo: Optional[str] = None,
        confianza: Optional[str] = None,
        supuestos: Optional[Mapping[str, Any]] = None,
        base: Optional[int] = None,
    ) -> Propuesta:
        """Deja una propuesta pendiente. Cualquier persona con un rol, o el agente, puede proponer: proponer no cambia nada."""
        if tipo not in self.tipos:
            raise PropuestaInvalida(f"no conozco el tipo «{tipo}»; los tipos son {', '.join(self.tipos)}")
        if not (objeto or "").strip():
            raise PropuestaInvalida("toda propuesta dice sobre qué recae")
        if not (evidencia or "").strip():
            raise PropuestaInvalida("una propuesta sin evidencia es una orden disfrazada: di de dónde sale")
        if not (usuario or "").strip():
            raise PropuestaInvalida("toda propuesta dice quién la dejó")
        if origen not in ORIGENES:
            raise PropuestaInvalida(f"el origen debe ser uno de: {', '.join(ORIGENES)}")
        if origen == "agente":
            if not (modelo or "").strip():
                raise PropuestaInvalida("una propuesta del agente dice qué modelo la produjo")
            if confianza is not None and confianza not in CONFIANZAS:
                raise PropuestaInvalida(f"la confianza debe ser una de: {', '.join(CONFIANZAS)}")
            rol_con = "agente"
        else:
            if modelo or version_modelo or confianza or supuestos:
                raise PropuestaInvalida("el modelo, su versión, la confianza y los supuestos son de una propuesta del agente")
            rol_con = _rol_de(rol)
            if not rol_con:
                raise PermisoDenegado("no tienes ningún rol: no puedes dejar una propuesta")
        if not isinstance(valor_propuesto, Mapping) or not valor_propuesto:
            raise PropuestaInvalida("sin un valor concreto que proponer no es una propuesta, es una alerta")
        if base is not None and (isinstance(base, bool) or not isinstance(base, int) or base < 0):
            raise PropuestaInvalida("«base» es el número de la última carga que se vio")
        objeto = objeto.strip()
        t = self.tipos[tipo]
        valor = _a_json(valor_propuesto, "lo que se propone")
        if t.normalizar is not None:
            valor = t.normalizar(objeto, valor)
        for p in self.repo.parecidas(tipo, objeto, valor):
            if p.estado == "pendiente":
                raise YaPropuesta(f"ya hay una propuesta igual pendiente, la {p.id}: se resuelve esa", p.id)
            if p.estado == "rechazada" and _huella(p.evidencia) == _huella(evidencia):
                raise RechazadaAntes(
                    f"la propuesta {p.id} era igual, se rechazó ({p.nota}) y esta no trae evidencia nueva: no se vuelve a proponer", p.id)
        return self.repo.agregar_propuesta(NuevaPropuesta(
            tipo, objeto, valor, evidencia.strip(), origen, usuario.strip(), rol_con, modelo, version_modelo, confianza,
            None if supuestos is None else _a_json(supuestos, "los supuestos"), base))

    def resolver(
        self,
        propuesta_id: int,
        decision: str,
        *,
        rol: Roles,
        usuario: str,
        nota: Optional[str] = None,
        esperaba: Optional[int] = None,
    ) -> Propuesta:
        """Aprobar o rechazar. Rechazar pide `aprobar_propuesta` y una nota. Aprobar pide además la función de la acción, no puede
        hacerlo quien propuso, y ejecuta la operación con la identidad de quien aprueba; si falla, sigue pendiente."""
        if decision not in DECISIONES:
            raise PropuestaInvalida(f"la decisión debe ser una de: {', '.join(DECISIONES)}")
        if not (usuario or "").strip():
            raise PropuestaInvalida("toda resolución dice quién la tomó")
        rol_con = self.rol_para(FUNCION_DE_RESOLVER_PROPUESTA, rol)
        p = self.repo.propuesta(propuesta_id)
        if p.estado != "pendiente":
            raise YaResuelta(f"la propuesta {propuesta_id} ya está {p.estado}", p.estado)
        if decision == "rechazar":
            if not (nota or "").strip():
                raise PropuestaInvalida("rechazar pide decir por qué: el rechazo se conserva y es lo que evita que se insista")
            return self.repo.resolver_propuesta(propuesta_id, "rechazada", usuario.strip(), rol_con, nota.strip(), None)
        if usuario.strip().casefold() == p.propuesto_por.casefold():
            raise AutoAprobacion("quien propone no aprueba lo suyo: que la apruebe otra persona")
        t = self.tipos[p.tipo]
        if t.ejecutar is None:
            raise SinOperacion(f"las propuestas de tipo «{p.tipo}» todavía no tienen operación en el sistema: se pueden rechazar, no aprobar", p.tipo)
        if t.funcion:
            self.rol_para(t.funcion, rol)  # aprobar pide la misma función que hacer a mano lo que se propone
        resultado = t.ejecutar(p.valor_propuesto, rol, usuario.strip(), esperaba if esperaba is not None else p.base)
        return self.repo.resolver_propuesta(
            propuesta_id, "aprobada", usuario.strip(), rol_con, (nota or "").strip() or None, _a_json(resultado, "el resultado"))

    def propuesta(self, propuesta_id: int) -> Propuesta:
        return self.repo.propuesta(propuesta_id)

    def propuestas(self, estado: Optional[str] = None, tipo: Optional[str] = None) -> List[Propuesta]:
        if estado is not None and estado not in ESTADOS_DE_PROPUESTA:
            raise PropuestaInvalida(f"el estado debe ser uno de: {', '.join(ESTADOS_DE_PROPUESTA)}")
        return self.repo.propuestas(estado, tipo)

    # ---- alertas
    def alertar(self, tipo: str, evidencia: Mapping[str, Any], objeto: Optional[str] = None,
                parametro_usado: Optional[Mapping[str, Any]] = None) -> Alerta:
        """Lo usan los detectores: detectar no pide permiso. Si la alerta ya está activa, se cuenta otra vez en vez de repetirse."""
        if not (tipo or "").strip():
            raise PropuestaInvalida("toda alerta tiene un tipo")
        if not isinstance(evidencia, Mapping) or not evidencia:
            raise PropuestaInvalida("una alerta dice qué se comparó y qué dio: sin evidencia no hay nada que mirar")
        return self.repo.registrar_alerta(
            tipo.strip(), (objeto or "").strip(), _a_json(evidencia, "la evidencia"),
            None if parametro_usado is None else _a_json(parametro_usado, "el parámetro usado"))

    def resolver_alerta(self, alerta_id: int, estado: str, *, rol: Roles, usuario: str, nota: str) -> Alerta:
        """Resolverla (era real y se atendió) o descartarla (no era nada); en los dos casos alguien dice qué era."""
        if estado not in ("resuelta", "descartada"):
            raise PropuestaInvalida("una alerta se resuelve o se descarta")
        if not (usuario or "").strip():
            raise PropuestaInvalida("toda resolución dice quién la tomó")
        rol_con = self.rol_para(FUNCION_DE_RESOLVER_ALERTA, rol)
        if not (nota or "").strip():
            raise PropuestaInvalida("una alerta se cierra diciendo qué era")
        a = self.repo.alerta(alerta_id)
        if a.estado != "activa":
            raise YaResuelta(f"la alerta {alerta_id} ya está {a.estado}", a.estado)
        return self.repo.resolver_alerta(alerta_id, estado, usuario.strip(), rol_con, nota.strip())

    def alerta(self, alerta_id: int) -> Alerta:
        return self.repo.alerta(alerta_id)

    def alertas(self, estado: Optional[str] = None, tipo: Optional[str] = None) -> List[Alerta]:
        if estado is not None and estado not in ESTADOS_DE_ALERTA:
            raise PropuestaInvalida(f"el estado debe ser uno de: {', '.join(ESTADOS_DE_ALERTA)}")
        return self.repo.alertas(estado, tipo)

    # ---- lo que hay pendiente
    def resumen(self) -> ResumenDeBandeja:
        pendientes = self.repo.propuestas("pendiente")
        activas = self.repo.alertas("activa")
        por = lambda xs: {t: sum(1 for x in xs if x.tipo == t) for t in sorted({x.tipo for x in xs})}
        return ResumenDeBandeja(len(pendientes), por(pendientes), len(activas), por(activas),
                                max(activas, key=lambda a: (a.veces_vista, a.ultima_vez), default=None))
