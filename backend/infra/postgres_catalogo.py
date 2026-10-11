"""
El adaptador de Postgres de `RepositorioCatalogo` — `database/migraciones/0005_catalogo_apu_presupuesto.sql`.

Vive fuera de `core/` por lo mismo que `postgres_programa.py` (D-182). Aplicar un plan es **una sola transacción**: o entra todo
o no entra nada. Antes de escribir se toma un candado de la base para que dos cargas no corran a la vez, y se comprueba que la
última carga sea la que vio quien revisó (el mismo candado optimista que `programa.version`): si no, `CatalogoCambio`.
"""
from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Dict, List, Optional, Tuple

import psycopg
from psycopg.types.json import Jsonb

from core.catalogo import (
    CatalogoCambio,
    DatosDePresupuesto,
    EstadoVigente,
    InsumoGuardado,
    LineaDePresupuesto,
    LineaGuardada,
    NodoDePresupuesto,
    PlanDeCarga,
    PrecioGuardado,
    ResumenCarga,
    ResumenPresupuesto,
    ResultadoCarga,
    VersionGuardada,
)
from core.dominio import BasePorcentaje, Categoria, Composicion, ModoPrecio, Nodo, Rol, TipoCantidad
from core.motor_calculo import ArbolEnMemoria

CANDADO_DEL_CATALOGO = 4_730_000_001  # cualquier número fijo: solo tiene que ser el mismo para todos los que cargan


def _insertar_varios(cur: "psycopg.Cursor", sql: str, filas: List[tuple]) -> List[int]:
    """Inserta todas las filas en un solo viaje y devuelve los `id` en el mismo orden."""
    if not filas:
        return []
    cur.executemany(sql, filas, returning=True)
    ids = []
    while True:
        ids.append(cur.fetchone()[0])
        if not cur.nextset():
            break
    return ids


class PostgresCatalogo:
    def __init__(self, conexion: "psycopg.Connection") -> None:
        self.conn = conexion

    # ------------------------------------------------------------------ leer
    def _ultima_carga(self) -> int:
        return self.conn.execute("SELECT coalesce(max(id), 0) FROM carga").fetchone()[0]

    def estado_vigente(self) -> EstadoVigente:
        with self.conn.transaction():
            self.conn.execute("SET TRANSACTION ISOLATION LEVEL REPEATABLE READ")  # una sola foto, aunque alguien cargue mientras tanto
            e = EstadoVigente(ultima_carga=self._ultima_carga())
            filas = self.conn.execute(
                "SELECT n.clave, n.rol, n.categoria, n.precio_declarado, coalesce(u.clave, ''), v.huella, v.pu"
                " FROM nodo n LEFT JOIN unidad u ON u.id = n.unidad_id"
                " LEFT JOIN LATERAL (SELECT huella, pu FROM version_concepto WHERE nodo_id = n.id ORDER BY version DESC LIMIT 1) v ON true"
                " WHERE n.rol <> 'estructural'").fetchall()
            for clave, rol, categoria, precio, unidad, huella, pu in filas:
                if huella is not None or rol in ("concepto", "ensamble"):
                    e.unidad[clave] = unidad
                    if huella is not None:
                        e.huella[clave], e.pu[clave] = huella, pu
                    else:
                        e.sin_matriz.add(clave)
                else:
                    e.insumos[clave] = InsumoGuardado(clave, unidad, categoria, precio)
            for p in self._presupuestos():
                e.presupuestos[p.clave] = p
        return e

    def _presupuestos(self) -> List[ResumenPresupuesto]:
        filas = self.conn.execute(
            "SELECT p.id, p.clave, p.nombre, p.tipo, p.huella, p.carga_id,"
            " (SELECT count(*) FROM nodo n WHERE n.presupuesto_id = p.id)"
            " + (SELECT count(*) FROM composicion c JOIN nodo pa ON pa.id = c.padre_id JOIN nodo h ON h.id = c.hijo_id"
            "     WHERE pa.presupuesto_id = p.id AND h.rol <> 'estructural')"
            " FROM presupuesto p ORDER BY p.id").fetchall()
        return [ResumenPresupuesto(*r) for r in filas]

    def presupuestos(self) -> List[ResumenPresupuesto]:
        with self.conn.transaction():
            return self._presupuestos()

    def id_de(self, clave: str) -> int:
        fila = self.conn.execute("SELECT id FROM nodo WHERE clave = %s AND rol <> 'estructural'", (clave,)).fetchone()
        if fila is None:
            raise KeyError(clave)
        return fila[0]

    def versiones(self, clave: str) -> List[VersionGuardada]:
        nodo_id = self.id_de(clave)
        with self.conn.transaction():
            versiones = self.conn.execute(
                "SELECT id, version, huella, pu, vigente_desde, carga_id FROM version_concepto WHERE nodo_id = %s ORDER BY version",
                (nodo_id,)).fetchall()
            out = []
            for vid, version, huella, pu, desde, carga_id in versiones:
                lineas = self.conn.execute(
                    "SELECT h.clave, c.cantidad, c.orden, c.reporta_a, c.tipo_cantidad = 'porcentaje'"
                    " FROM composicion c JOIN nodo h ON h.id = c.hijo_id WHERE c.version_id = %s ORDER BY c.orden", (vid,)).fetchall()
                out.append(VersionGuardada(clave, version, huella, pu, desde, carga_id, tuple(LineaGuardada(*l) for l in lineas)))
        return out

    def precios(self, clave: str) -> List[PrecioGuardado]:
        nodo_id = self.id_de(clave)
        filas = self.conn.execute(
            "SELECT precio, vigente_desde, vigente_hasta, carga_id FROM precio_historico WHERE nodo_id = %s ORDER BY vigente_desde, id",
            (nodo_id,)).fetchall()
        return [PrecioGuardado(clave, *f) for f in filas]

    def cargas(self) -> List[ResumenCarga]:
        filas = self.conn.execute("SELECT id, creada_en, usuario, rol, archivos, resumen FROM carga ORDER BY id").fetchall()
        return [ResumenCarga(*f) for f in filas]

    def datos_de_presupuesto(self, presupuesto_id: int) -> DatosDePresupuesto:
        with self.conn.transaction():
            fila = self.conn.execute("SELECT raiz_id FROM presupuesto WHERE id = %s", (presupuesto_id,)).fetchone()
            if fila is None:
                raise KeyError(presupuesto_id)
            raiz_id = fila[0]
            resumen = next(p for p in self._presupuestos() if p.id == presupuesto_id)
            nodos: Dict[int, NodoDePresupuesto] = {}
            for id_, clave, desc, unidad, tipo, ruta in self.conn.execute(
                    "SELECT n.id, n.clave, n.descripcion, coalesce(u.clave, ''), n.tipo_opus, n.ruta_natural FROM nodo n"
                    " LEFT JOIN unidad u ON u.id = n.unidad_id WHERE n.presupuesto_id = %s", (presupuesto_id,)):
                nodos[id_] = NodoDePresupuesto(id_, clave, desc, unidad, True, tipo, ruta)
            lineas: List[LineaDePresupuesto] = []
            for linea_id, padre, hijo, orden, cantidad, version, pu, estructural, clave, desc, unidad in self.conn.execute(
                    "SELECT c.id, c.padre_id, c.hijo_id, c.orden, c.cantidad, v.version, v.pu, h.rol = 'estructural', h.clave, h.descripcion,"
                    " coalesce(uh.clave, '') FROM composicion c JOIN nodo pa ON pa.id = c.padre_id JOIN nodo h ON h.id = c.hijo_id"
                    " LEFT JOIN unidad uh ON uh.id = h.unidad_id LEFT JOIN version_concepto v ON v.id = c.hijo_version_id"
                    " WHERE pa.presupuesto_id = %s ORDER BY c.padre_id, c.orden", (presupuesto_id,)):
                if not estructural:
                    nodos[hijo] = NodoDePresupuesto(hijo, clave, desc, unidad, False, "Concepto")
                lineas.append(LineaDePresupuesto(padre, hijo, orden, cantidad, version, pu, linea_id))
        return DatosDePresupuesto(resumen, raiz_id, nodos, tuple(lineas))

    def arbol(self) -> ArbolEnMemoria:
        with self.conn.transaction():
            self.conn.execute("SET TRANSACTION ISOLATION LEVEL REPEATABLE READ")
            nodos = {
                id_: Nodo(id_, clave, desc, unidad, Rol(rol), Categoria(categoria), ModoPrecio(modo), precio)
                for id_, clave, desc, unidad, rol, categoria, modo, precio in self.conn.execute(
                    "SELECT n.id, n.clave, n.descripcion, coalesce(u.clave, ''), n.rol, n.categoria, n.modo_precio, n.precio_declarado"
                    " FROM nodo n LEFT JOIN unidad u ON u.id = n.unidad_id")
            }
            composicion: List[Composicion] = []
            for id_, padre, hijo, cantidad, orden, reporta_a, porcentaje, base in self.conn.execute(
                    "SELECT c.id, c.padre_id, c.hijo_id, c.cantidad, c.orden, c.reporta_a, c.tipo_cantidad = 'porcentaje', c.base_porcentaje"
                    " FROM composicion c LEFT JOIN version_concepto v ON v.id = c.version_id"
                    " WHERE c.version_id IS NULL OR v.version = (SELECT max(version) FROM version_concepto WHERE nodo_id = v.nodo_id)"):
                composicion.append(Composicion(
                    id_, padre, hijo, cantidad, orden, Categoria(reporta_a),
                    TipoCantidad.PORCENTAJE if porcentaje else TipoCantidad.FIJA, BasePorcentaje(base) if base else None))
        return ArbolEnMemoria(nodos, composicion)

    # ------------------------------------------------------------------ escribir
    def aplicar(self, plan: PlanDeCarga) -> ResultadoCarga:
        with self.conn.transaction():
            self.conn.execute("SELECT pg_advisory_xact_lock(%s)", (CANDADO_DEL_CATALOGO,))
            ultima = self._ultima_carga()
            if ultima != plan.base:
                raise CatalogoCambio(f"la última carga es la {ultima} y esta se revisó sobre la {plan.base}")
            carga_id = self.conn.execute(
                "INSERT INTO carga (usuario, rol, archivos, resumen) VALUES (%s, %s, %s, %s) RETURNING id",
                (plan.usuario, plan.rol, Jsonb(dict(plan.archivos)), Jsonb(dict(plan.resumen)))).fetchone()[0]
            with self.conn.cursor() as cur:
                self._escribir(cur, plan, carga_id)
        return ResultadoCarga(carga_id, dict(plan.resumen))

    def _escribir(self, cur: "psycopg.Cursor", plan: PlanDeCarga, carga_id: int) -> None:
        for u in plan.unidades:
            cur.execute("INSERT INTO unidad (clave) VALUES (%s) ON CONFLICT ((lower(clave))) DO NOTHING", (u.strip(),))
        unidad_id = {clave.lower(): id_ for id_, clave in cur.execute("SELECT id, clave FROM unidad")}

        def u(texto: str) -> Optional[int]:
            return unidad_id[texto.strip().casefold()] if texto.strip() else None

        # los nodos del catálogo que nacen: insumos, conceptos sin matriz y los que traen su primera versión
        nuevos: List[tuple] = []
        for i in plan.insumos_nuevos:
            nuevos.append((i.clave, i.descripcion, u(i.unidad), "insumo", i.categoria.value, "declarado", i.precio))
        for c in plan.conceptos_sin_matriz:
            nuevos.append((c.clave, c.descripcion, u(c.unidad), "concepto", "concepto", "calculado", None))
        for m in plan.nodos_nuevos:
            nuevos.append((m.clave, m.descripcion, u(m.unidad), m.rol.value, m.categoria.value, "calculado", None))
        ids = _insertar_varios(
            cur, "INSERT INTO nodo (clave, descripcion, unidad_id, rol, categoria, modo_precio, precio_declarado)"
                 " VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING id", nuevos)
        nodo_id: Dict[str, int] = {clave: id_ for id_, clave in cur.execute("SELECT id, clave FROM nodo WHERE rol <> 'estructural'")}
        assert len(ids) == len(nuevos)

        # el precio: la historia, y el caché en el nodo
        for i in plan.insumos_nuevos:
            if i.con_historico:
                cur.execute("INSERT INTO precio_historico (nodo_id, precio, fuente, carga_id) VALUES (%s, %s, 'catalogo', %s)",
                            (nodo_id[i.clave], i.precio, carga_id))
        for clave, precio in plan.precios_nuevos:
            cur.execute("UPDATE precio_historico SET vigente_hasta = now() WHERE nodo_id = %s AND vigente_hasta IS NULL", (nodo_id[clave],))
            cur.execute("INSERT INTO precio_historico (nodo_id, precio, fuente, carga_id) VALUES (%s, %s, 'catalogo', %s)",
                        (nodo_id[clave], precio, carga_id))
            cur.execute("UPDATE nodo SET precio_declarado = %s WHERE id = %s", (precio, nodo_id[clave]))
        for clave, unidad in plan.unidades_que_se_saben:
            cur.execute("UPDATE nodo SET unidad_id = %s WHERE id = %s", (u(unidad), nodo_id[clave]))

        # las versiones y sus líneas
        ultima: Dict[int, int] = {n: v for n, v in cur.execute("SELECT nodo_id, max(version) FROM version_concepto GROUP BY nodo_id")}
        todas = list(plan.nodos_nuevos) + list(plan.versiones_nuevas)
        vids = _insertar_varios(
            cur, "INSERT INTO version_concepto (nodo_id, version, huella, pu, carga_id) VALUES (%s, %s, %s, %s, %s) RETURNING id",
            [(nodo_id[m.clave], ultima.get(nodo_id[m.clave], 0) + 1, m.huella, m.pu, carga_id) for m in todas])
        lineas = []
        for vid, m in zip(vids, todas):
            for orden, l in enumerate(m.lineas, start=1):
                lineas.append((nodo_id[m.clave], vid, nodo_id[l.hijo], l.cantidad, orden, l.reporta_a.value,
                               "porcentaje" if l.porcentaje else "fija", "suma_jornales_hermanos" if l.porcentaje else None))
        if lineas:
            cur.executemany(
                "INSERT INTO composicion (padre_id, version_id, hijo_id, cantidad, orden, reporta_a, tipo_cantidad, base_porcentaje)"
                " VALUES (%s, %s, %s, %s, %s, %s, %s, %s)", lineas)

        # los presupuestos: sus nodos estructurales y sus renglones
        if plan.presupuestos_nuevos:
            vigente: Dict[int, int] = {n: v for v, n in cur.execute(
                "SELECT DISTINCT ON (nodo_id) id, nodo_id FROM version_concepto ORDER BY nodo_id, version DESC")}
            for p in plan.presupuestos_nuevos:
                pid = cur.execute(
                    "INSERT INTO presupuesto (clave, nombre, tipo, huella, carga_id) VALUES (%s, %s, %s, %s, %s) RETURNING id",
                    (p.clave, p.nombre, p.tipo, p.huella, carga_id)).fetchone()[0]
                estructurales = [r for r in p.renglones if r.tipo != "Concepto"]
                sids = _insertar_varios(
                    cur, "INSERT INTO nodo (presupuesto_id, clave, descripcion, unidad_id, rol, categoria, tipo_opus, ruta_natural)"
                         " VALUES (%s, %s, %s, %s, 'estructural', 'concepto', %s, %s) RETURNING id",
                    [(pid, r.clave, r.descripcion, u(r.unidad), r.tipo, r.ruta_natural) for r in estructurales])
                nodo_de_renglon = {r.posicion: sid for r, sid in zip(estructurales, sids)}
                for r in p.renglones:
                    if r.tipo == "Concepto":
                        nodo_de_renglon[r.posicion] = nodo_id[r.clave]
                raiz = next(nodo_de_renglon[r.posicion] for r in p.renglones if r.padre is None)
                cur.execute("UPDATE presupuesto SET raiz_id = %s WHERE id = %s", (raiz, pid))
                orden: Dict[int, int] = {}
                renglones = []
                for r in p.renglones:
                    if r.padre is None:
                        continue
                    padre, hijo = nodo_de_renglon[r.padre], nodo_de_renglon[r.posicion]
                    orden[padre] = orden.get(padre, 0) + 1
                    version = vigente.get(hijo) if r.tipo == "Concepto" else None
                    renglones.append((padre, hijo, version, r.cantidad, orden[padre]))
                cur.executemany(
                    "INSERT INTO composicion (padre_id, hijo_id, hijo_version_id, cantidad, orden, reporta_a)"
                    " VALUES (%s, %s, %s, %s, %s, 'concepto')", renglones)
