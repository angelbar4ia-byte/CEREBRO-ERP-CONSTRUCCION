"""
El adaptador en memoria de `RepositorioCatalogo` — para las pruebas y para quien quiera probar sin base (misma idea que
`memoria_programa.py`, D-182). Cumple el mismo contrato que el de Postgres: `core/tests/contrato_catalogo.py` corre las mismas
exigencias contra los dos.

Guarda lo mismo que `database/migraciones/0005_catalogo_apu_presupuesto.sql`, con la misma forma: nodos, versiones de matriz con
sus líneas, líneas de presupuesto que fijan una versión, la historia de precios y las cargas. Aplicar un plan es todo o nada:
se hace sobre una copia que sustituye a la original solo si no falló nada.
"""
from __future__ import annotations

import copy
from dataclasses import dataclass, field
from datetime import datetime, timezone
from decimal import Decimal
from typing import Dict, List, Optional, Set, Tuple

from .catalogo import (
    CatalogoCambio,
    Congelamiento,
    DatosDePresupuesto,
    EstadoVigente,
    InsumoGuardado,
    LineaDePresupuesto,
    LineaGuardada,
    NodoDePresupuesto,
    PlanDeCarga,
    PlanDeContratacion,
    PrecioGuardado,
    ResumenCarga,
    ResumenPresupuesto,
    ResultadoCarga,
    ResultadoContratacion,
    VersionGuardada,
    YaContratado,
)
from .dominio import BasePorcentaje, Categoria, Composicion, ModoPrecio, Nodo, Rol, TipoCantidad
from .motor_calculo import ArbolEnMemoria


@dataclass
class _Nodo:
    id: int
    clave: str
    descripcion: str
    unidad_id: Optional[int]
    rol: str
    categoria: str
    modo_precio: str = "calculado"
    precio_declarado: Optional[Decimal] = None
    presupuesto_id: Optional[int] = None
    tipo_opus: Optional[str] = None
    ruta_natural: Optional[str] = None


@dataclass
class _Linea:
    hijo_id: int
    cantidad: Decimal
    orden: int
    reporta_a: str
    porcentaje: bool


@dataclass
class _Version:
    id: int
    version: int
    huella: str
    pu: Decimal
    vigente_desde: datetime
    carga_id: int
    lineas: List[_Linea]


@dataclass
class _LineaDePresupuesto:
    id: int
    hijo_id: int
    hijo_version_id: Optional[int]
    cantidad: Decimal
    orden: int


@dataclass
class _Precio:
    precio: Decimal
    vigente_desde: datetime
    vigente_hasta: Optional[datetime]
    carga_id: Optional[int]


@dataclass
class _Presupuesto:
    id: int
    clave: str
    nombre: str
    tipo: str
    raiz_id: int
    huella: str
    carga_id: int


@dataclass
class _Congelamiento:
    id: int
    nodo_id: int
    estado: str
    fecha: datetime
    usuario: str
    rol: str
    carga_id: int
    resumen: Dict


@dataclass
class _Datos:
    unidades: Dict[str, Tuple[int, str]] = field(default_factory=dict)  # clave en minúsculas → (id, clave tal como vino)
    cargas: List[ResumenCarga] = field(default_factory=list)
    nodos: Dict[int, _Nodo] = field(default_factory=dict)
    por_clave: Dict[str, int] = field(default_factory=dict)  # solo los del catálogo
    versiones: Dict[int, List[_Version]] = field(default_factory=dict)
    renglones: Dict[int, List[_LineaDePresupuesto]] = field(default_factory=dict)  # padre estructural → sus líneas
    precios: Dict[int, List[_Precio]] = field(default_factory=dict)
    presupuestos: Dict[int, _Presupuesto] = field(default_factory=dict)
    congelamientos: List[_Congelamiento] = field(default_factory=list)
    sig_congelamiento: int = 0
    sig_nodo: int = 0
    sig_version: int = 0
    sig_unidad: int = 0
    sig_carga: int = 0
    sig_presupuesto: int = 0
    sig_linea: int = 0

    def unidad_de(self, nodo: _Nodo) -> str:
        if nodo.unidad_id is None:
            return ""
        return next(clave for i, clave in self.unidades.values() if i == nodo.unidad_id)

    def vigente(self, nodo_id: int) -> Optional[_Version]:
        v = self.versiones.get(nodo_id)
        return v[-1] if v else None

    def contratados(self) -> Set[int]:
        """Los bloques contratados y todos los que cuelgan de ellos."""
        out: Set[int] = set()
        pila = [c.nodo_id for c in self.congelamientos if c.estado == "contratado"]
        while pila:
            n = pila.pop()
            if n in out:
                continue
            out.add(n)
            pila += [l.hijo_id for l in self.renglones.get(n, ()) if self.nodos[l.hijo_id].rol == "estructural"]
        return out

    def arriba_de(self, nodo_id: int) -> List[int]:
        """El nodo y los bloques de arriba, hasta la raíz de su presupuesto."""
        padre_de = {l.hijo_id: padre for padre, ls in self.renglones.items() for l in ls if self.nodos[l.hijo_id].rol == "estructural"}
        out = [nodo_id]
        while out[-1] in padre_de:
            out.append(padre_de[out[-1]])
        return out


class MemoriaCatalogo:
    def __init__(self) -> None:
        self._d = _Datos()

    # ------------------------------------------------------------------ leer
    def estado_vigente(self) -> EstadoVigente:
        d = self._d
        e = EstadoVigente(ultima_carga=d.sig_carga)
        for clave, nodo_id in d.por_clave.items():
            n = d.nodos[nodo_id]
            v = d.vigente(nodo_id)
            if v is not None or n.rol in ("concepto", "ensamble"):
                e.unidad[clave] = d.unidad_de(n)
                if v is not None:
                    e.huella[clave], e.pu[clave], e.version[clave] = v.huella, v.pu, v.version
                else:
                    e.sin_matriz.add(clave)
            else:
                e.insumos[clave] = InsumoGuardado(clave, d.unidad_de(n), n.categoria, n.precio_declarado)
        for p in d.presupuestos.values():
            e.presupuestos[p.clave] = self._resumen(p)
        for bloque in d.contratados():
            e.en_contratado |= {d.nodos[l.hijo_id].clave for l in d.renglones.get(bloque, ()) if d.nodos[l.hijo_id].rol != "estructural"}
        return e

    def _resumen(self, p: _Presupuesto) -> ResumenPresupuesto:
        renglones = 0
        pendientes = [p.raiz_id]
        while pendientes:
            padre = pendientes.pop()
            for l in self._d.renglones.get(padre, ()):
                renglones += 1
                if self._d.nodos[l.hijo_id].rol == "estructural":
                    pendientes.append(l.hijo_id)
        return ResumenPresupuesto(p.id, p.clave, p.nombre, p.tipo, p.huella, p.carga_id, renglones + 1)

    def id_de(self, clave: str) -> int:
        return self._d.por_clave[clave]

    def versiones(self, clave: str) -> List[VersionGuardada]:
        d = self._d
        nodo_id = d.por_clave[clave]
        return [
            VersionGuardada(clave, v.version, v.huella, v.pu, v.vigente_desde, v.carga_id,
                            tuple(LineaGuardada(d.nodos[l.hijo_id].clave, l.cantidad, l.orden, l.reporta_a, l.porcentaje) for l in v.lineas))
            for v in d.versiones.get(nodo_id, [])
        ]

    def precios(self, clave: str) -> List[PrecioGuardado]:
        nodo_id = self._d.por_clave[clave]
        return [PrecioGuardado(clave, p.precio, p.vigente_desde, p.vigente_hasta, p.carga_id) for p in self._d.precios.get(nodo_id, [])]

    def cargas(self) -> List[ResumenCarga]:
        return list(self._d.cargas)

    def presupuestos(self) -> List[ResumenPresupuesto]:
        return [self._resumen(p) for p in sorted(self._d.presupuestos.values(), key=lambda p: p.id)]

    def datos_de_presupuesto(self, presupuesto_id: int) -> DatosDePresupuesto:
        d = self._d
        p = d.presupuestos[presupuesto_id]
        nodos: Dict[int, NodoDePresupuesto] = {}
        lineas: List[LineaDePresupuesto] = []
        pila = [p.raiz_id]
        while pila:
            padre = pila.pop()
            n = d.nodos[padre]
            nodos[padre] = NodoDePresupuesto(n.id, n.clave, n.descripcion, d.unidad_de(n), True, n.tipo_opus or "", n.ruta_natural or "")
            for l in d.renglones.get(padre, ()):
                h = d.nodos[l.hijo_id]
                if h.rol == "estructural":
                    pila.append(l.hijo_id)
                    lineas.append(LineaDePresupuesto(padre, l.hijo_id, l.orden, l.cantidad, None, None, l.id))
                else:
                    nodos[l.hijo_id] = NodoDePresupuesto(h.id, h.clave, h.descripcion, d.unidad_de(h), False, "Concepto")
                    v = next((v for v in d.versiones.get(l.hijo_id, ()) if v.id == l.hijo_version_id), None)
                    lineas.append(LineaDePresupuesto(padre, l.hijo_id, l.orden, l.cantidad, v.version if v else None, v.pu if v else None, l.id))
        return DatosDePresupuesto(self._resumen(p), p.raiz_id, nodos, tuple(lineas))

    def congelamientos(self, presupuesto_id: int) -> List[Congelamiento]:
        d = self._d
        return [
            Congelamiento(c.id, c.nodo_id, d.nodos[c.nodo_id].ruta_natural or "", c.estado, c.fecha, c.usuario, c.rol, c.carga_id, dict(c.resumen))
            for c in d.congelamientos if d.nodos[c.nodo_id].presupuesto_id == presupuesto_id
        ]

    def contratar(self, plan: PlanDeContratacion) -> ResultadoContratacion:
        d0 = self._d
        if plan.base != d0.sig_carga:
            raise CatalogoCambio(f"la última carga es la {d0.sig_carga} y esta se revisó sobre la {plan.base}")
        trabajo = copy.deepcopy(d0)
        r = _contratar(trabajo, plan)
        self._d = trabajo
        return r

    def arbol(self) -> ArbolEnMemoria:
        d = self._d
        nodos = {
            n.id: Nodo(n.id, n.clave, n.descripcion, d.unidad_de(n), Rol(n.rol), Categoria(n.categoria), ModoPrecio(n.modo_precio), n.precio_declarado)
            for n in d.nodos.values()
        }
        composicion: List[Composicion] = []

        def agrega(padre: int, hijo: int, cantidad: Decimal, orden: int, reporta_a: str, porcentaje: bool) -> None:
            composicion.append(Composicion(
                len(composicion) + 1, padre, hijo, cantidad, orden, Categoria(reporta_a),
                TipoCantidad.PORCENTAJE if porcentaje else TipoCantidad.FIJA,
                BasePorcentaje.SUMA_JORNALES_HERMANOS if porcentaje else None))

        for nodo_id, versiones in d.versiones.items():
            for l in versiones[-1].lineas:
                agrega(nodo_id, l.hijo_id, l.cantidad, l.orden, l.reporta_a, l.porcentaje)
        for padre, lineas in d.renglones.items():
            for l in lineas:
                agrega(padre, l.hijo_id, l.cantidad, l.orden, "concepto", False)
        return ArbolEnMemoria(nodos, composicion)

    # ------------------------------------------------------------------ escribir
    def aplicar(self, plan: PlanDeCarga) -> ResultadoCarga:
        if plan.base != self._d.sig_carga:
            raise CatalogoCambio(f"la última carga es la {self._d.sig_carga} y esta se revisó sobre la {plan.base}")
        trabajo = copy.deepcopy(self._d)
        r = _aplicar(trabajo, plan)
        self._d = trabajo
        return r


def _aplicar(d: _Datos, plan: PlanDeCarga) -> ResultadoCarga:
    ahora = datetime.now(timezone.utc)
    d.sig_carga += 1
    carga_id = d.sig_carga
    d.cargas.append(ResumenCarga(carga_id, ahora, plan.usuario, plan.rol, dict(plan.archivos), dict(plan.resumen), "archivos"))

    def unidad(texto: str) -> Optional[int]:
        t = texto.strip()
        if not t:
            return None
        return d.unidades[t.casefold()][0]

    for u in plan.unidades:
        if u.strip().casefold() not in d.unidades:
            d.sig_unidad += 1
            d.unidades[u.strip().casefold()] = (d.sig_unidad, u.strip())

    def nuevo_nodo(**campos) -> _Nodo:
        d.sig_nodo += 1
        n = _Nodo(id=d.sig_nodo, **campos)
        if n.rol != "estructural":
            if n.clave in d.por_clave:
                raise ValueError(f"ya hay un nodo del catálogo con la clave {n.clave}")
            d.por_clave[n.clave] = n.id
        d.nodos[n.id] = n
        return n

    for i in plan.insumos_nuevos:
        n = nuevo_nodo(clave=i.clave, descripcion=i.descripcion, unidad_id=unidad(i.unidad), rol="insumo", categoria=i.categoria.value,
                       modo_precio="declarado", precio_declarado=i.precio)
        if i.con_historico:
            d.precios[n.id] = [_Precio(i.precio, ahora, None, carga_id)]
    for clave, precio in plan.precios_nuevos:
        nodo_id = d.por_clave[clave]
        historia = d.precios.setdefault(nodo_id, [])
        if historia:
            historia[-1].vigente_hasta = ahora
        historia.append(_Precio(precio, ahora, None, carga_id))
        d.nodos[nodo_id].precio_declarado = precio
    for clave, u in plan.unidades_que_se_saben:
        d.nodos[d.por_clave[clave]].unidad_id = unidad(u)

    for c in plan.conceptos_sin_matriz:
        nuevo_nodo(clave=c.clave, descripcion=c.descripcion, unidad_id=unidad(c.unidad), rol="concepto", categoria="concepto")
    for m in plan.nodos_nuevos:
        nuevo_nodo(clave=m.clave, descripcion=m.descripcion, unidad_id=unidad(m.unidad), rol=m.rol.value, categoria=m.categoria.value)

    for m in list(plan.nodos_nuevos) + list(plan.versiones_nuevas):
        nodo_id = d.por_clave[m.clave]
        previas = d.versiones.setdefault(nodo_id, [])
        d.sig_version += 1
        previas.append(_Version(
            d.sig_version, len(previas) + 1, m.huella, m.pu, ahora, carga_id,
            [_Linea(d.por_clave[l.hijo], l.cantidad, orden, l.reporta_a.value, l.porcentaje) for orden, l in enumerate(m.lineas, start=1)]))

    for p in plan.presupuestos_nuevos:
        d.sig_presupuesto += 1
        ids: Dict[int, int] = {}
        raiz_id = 0
        for r in p.renglones:
            if r.tipo == "Concepto":
                ids[r.posicion] = d.por_clave[r.clave]
                continue
            n = nuevo_nodo(clave=r.clave, descripcion=r.descripcion, unidad_id=unidad(r.unidad), rol="estructural", categoria="concepto",
                           presupuesto_id=d.sig_presupuesto, tipo_opus=r.tipo, ruta_natural=r.ruta_natural)
            ids[r.posicion] = n.id
            if r.padre is None:
                raiz_id = n.id
        orden: Dict[int, int] = {}
        for r in p.renglones:
            if r.padre is None:
                continue
            padre = ids[r.padre]
            orden[padre] = orden.get(padre, 0) + 1
            hijo = ids[r.posicion]
            v = d.vigente(hijo) if r.tipo == "Concepto" else None
            d.sig_linea += 1
            d.renglones.setdefault(padre, []).append(_LineaDePresupuesto(d.sig_linea, hijo, v.id if v else None, r.cantidad, orden[padre]))
        d.presupuestos[d.sig_presupuesto] = _Presupuesto(d.sig_presupuesto, p.clave, p.nombre, p.tipo, raiz_id, p.huella, carga_id)
    return ResultadoCarga(carga_id, dict(plan.resumen))


def _contratar(d: _Datos, plan: PlanDeContratacion) -> ResultadoContratacion:
    nodo = d.nodos.get(plan.nodo_id)
    if nodo is None or nodo.rol != "estructural" or nodo.presupuesto_id != plan.presupuesto_id:
        raise ValueError(f"el nodo {plan.nodo_id} no es un bloque del presupuesto {plan.presupuesto_id}")
    contratados = {c.nodo_id for c in d.congelamientos if c.estado == "contratado"}
    for arriba in d.arriba_de(plan.nodo_id):
        if arriba in contratados:
            raise YaContratado(f"el bloque {d.nodos[arriba].ruta_natural} ya está contratado", arriba)
    ahora = datetime.now(timezone.utc)
    d.sig_carga += 1
    carga_id = d.sig_carga
    d.cargas.append(ResumenCarga(carga_id, ahora, plan.usuario, plan.rol, {}, dict(plan.resumen), "contratacion"))
    for v in plan.versiones_nuevas:
        previas = d.versiones[d.por_clave[v.clave]]
        ultima = previas[-1]
        d.sig_version += 1
        previas.append(_Version(d.sig_version, ultima.version + 1, ultima.huella, v.pu, ahora, carga_id, copy.deepcopy(ultima.lineas)))
    fijados = 0
    for renglon_id, clave in plan.renglones:
        linea = next((l for ls in d.renglones.values() for l in ls if l.id == renglon_id), None)
        if linea is None or d.nodos[linea.hijo_id].clave != clave:
            raise ValueError(f"el renglón {renglon_id} no es de {clave}")
        linea.hijo_version_id = d.vigente(linea.hijo_id).id
        fijados += 1
    d.sig_congelamiento += 1
    d.congelamientos.append(_Congelamiento(d.sig_congelamiento, plan.nodo_id, "contratado", ahora, plan.usuario, plan.rol, carga_id, dict(plan.resumen)))
    return ResultadoContratacion(carga_id, d.sig_congelamiento, len(plan.versiones_nuevas), fijados)
