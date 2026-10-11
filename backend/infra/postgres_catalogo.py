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
    CambioDeRenglon,
    CatalogoCambio,
    CitasDe,
    ClonGuardado,
    Congelamiento,
    DatosDePresupuesto,
    EstadoVigente,
    InsumoGuardado,
    InsumoPlan,
    LineaDePresupuesto,
    LineaGuardada,
    NodoConMatriz,
    NodoDelCatalogo,
    NodoDePresupuesto,
    PadreCitante,
    PlanDeCarga,
    PlanDeClonacion,
    PlanDeContratacion,
    PrecioGuardado,
    ReconciliacionPlan,
    ResumenCarga,
    ResumenPresupuesto,
    ResultadoCarga,
    ResultadoClonacion,
    ResultadoContratacion,
    VersionGuardada,
    YaContratado,
    cerrar_homologaciones,
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
                "SELECT n.clave, n.rol, n.categoria, n.precio_declarado, coalesce(u.clave, ''), v.huella, v.pu, v.version, n.descripcion"
                " FROM nodo n LEFT JOIN unidad u ON u.id = n.unidad_id"
                " LEFT JOIN LATERAL (SELECT huella, pu, version FROM version_concepto WHERE nodo_id = n.id ORDER BY version DESC LIMIT 1) v ON true"
                " WHERE n.rol <> 'estructural'").fetchall()
            for clave, rol, categoria, precio, unidad, huella, pu, version, descripcion in filas:
                e.descripcion[clave] = descripcion
                if huella is not None or rol in ("concepto", "ensamble"):
                    e.unidad[clave] = unidad
                    if huella is not None:
                        e.huella[clave], e.pu[clave], e.version[clave] = huella, pu, version
                    else:
                        e.sin_matriz.add(clave)
                else:
                    e.insumos[clave] = InsumoGuardado(clave, unidad, categoria, precio)
            for p in self._presupuestos():
                e.presupuestos[p.clave] = p
            e.en_contratado = {r[0] for r in self.conn.execute(
                "WITH RECURSIVE bajo (id) AS ("
                "  SELECT nodo_id FROM estado_congelamiento WHERE estado = 'contratado'"
                "  UNION"
                "  SELECT c.hijo_id FROM composicion c JOIN bajo b ON c.padre_id = b.id JOIN nodo h ON h.id = c.hijo_id"
                "   WHERE c.version_id IS NULL AND c.baja_carga_id IS NULL AND h.rol = 'estructural')"
                " SELECT DISTINCT h.clave FROM composicion c JOIN bajo b ON c.padre_id = b.id JOIN nodo h ON h.id = c.hijo_id"
                "  WHERE c.version_id IS NULL AND c.baja_carga_id IS NULL AND h.rol <> 'estructural'")}
            e.homologaciones = cerrar_homologaciones(self.conn.execute(
                "SELECT o.clave, n.clave FROM clon c JOIN nodo o ON o.id = c.original_id JOIN nodo n ON n.id = c.clon_id"
                " WHERE c.reconoce_clave_vieja_al_importar ORDER BY c.id").fetchall())
        return e

    def _presupuestos(self) -> List[ResumenPresupuesto]:
        filas = self.conn.execute(
            "SELECT p.id, p.clave, p.nombre, p.tipo, p.huella, p.carga_id,"
            " (SELECT count(*) FROM nodo n WHERE n.presupuesto_id = p.id AND n.baja_carga_id IS NULL)"
            " + (SELECT count(*) FROM composicion c JOIN nodo pa ON pa.id = c.padre_id JOIN nodo h ON h.id = c.hijo_id"
            "     WHERE pa.presupuesto_id = p.id AND h.rol <> 'estructural' AND c.baja_carga_id IS NULL)"
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
                out.append(VersionGuardada(clave, version, huella, pu, desde, carga_id, self._lineas_de(vid)))
        return out

    def _lineas_de(self, version_id: int) -> Tuple[LineaGuardada, ...]:
        lineas = self.conn.execute(
            "SELECT h.clave, c.cantidad, c.orden, c.reporta_a, c.tipo_cantidad = 'porcentaje'"
            " FROM composicion c JOIN nodo h ON h.id = c.hijo_id WHERE c.version_id = %s ORDER BY c.orden", (version_id,)).fetchall()
        return tuple(LineaGuardada(*l) for l in lineas)

    def precios(self, clave: str) -> List[PrecioGuardado]:
        nodo_id = self.id_de(clave)
        filas = self.conn.execute(
            "SELECT precio, vigente_desde, vigente_hasta, carga_id FROM precio_historico WHERE nodo_id = %s ORDER BY vigente_desde, id",
            (nodo_id,)).fetchall()
        return [PrecioGuardado(clave, *f) for f in filas]

    def cargas(self) -> List[ResumenCarga]:
        filas = self.conn.execute("SELECT id, creada_en, usuario, rol, archivos, resumen, tipo FROM carga ORDER BY id").fetchall()
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
                    " LEFT JOIN unidad u ON u.id = n.unidad_id WHERE n.presupuesto_id = %s AND n.baja_carga_id IS NULL", (presupuesto_id,)):
                nodos[id_] = NodoDePresupuesto(id_, clave, desc, unidad, True, tipo, ruta)
            lineas: List[LineaDePresupuesto] = []
            for linea_id, padre, hijo, orden, cantidad, version, pu, estructural, clave, desc, unidad in self.conn.execute(
                    "SELECT c.id, c.padre_id, c.hijo_id, c.orden, c.cantidad, v.version, v.pu, h.rol = 'estructural', h.clave, h.descripcion,"
                    " coalesce(uh.clave, '') FROM composicion c JOIN nodo pa ON pa.id = c.padre_id JOIN nodo h ON h.id = c.hijo_id"
                    " LEFT JOIN unidad uh ON uh.id = h.unidad_id LEFT JOIN version_concepto v ON v.id = c.hijo_version_id"
                    " WHERE pa.presupuesto_id = %s AND c.baja_carga_id IS NULL ORDER BY c.padre_id, c.orden", (presupuesto_id,)):
                if not estructural:
                    nodos[hijo] = NodoDePresupuesto(hijo, clave, desc, unidad, False, "Concepto")
                lineas.append(LineaDePresupuesto(padre, hijo, orden, cantidad, version, pu, linea_id))
        return DatosDePresupuesto(resumen, raiz_id, nodos, tuple(lineas))

    def historia(self, renglon_id: int) -> List[CambioDeRenglon]:
        filas = self.conn.execute(
            "SELECT carga_id, campo, antes, despues, creada_en FROM renglon_historia WHERE renglon_id = %s ORDER BY id", (renglon_id,)).fetchall()
        return [CambioDeRenglon(*f) for f in filas]

    def congelamientos(self, presupuesto_id: int) -> List[Congelamiento]:
        filas = self.conn.execute(
            "SELECT e.id, e.nodo_id, n.ruta_natural, e.estado, e.fecha, e.usuario, e.rol, e.carga_id, e.resumen"
            " FROM estado_congelamiento e JOIN nodo n ON n.id = e.nodo_id WHERE n.presupuesto_id = %s ORDER BY e.id", (presupuesto_id,)).fetchall()
        return [Congelamiento(*f) for f in filas]

    def nodo(self, clave: str) -> NodoDelCatalogo:
        fila = self.conn.execute(
            "SELECT n.id, n.descripcion, coalesce(u.clave, ''), n.rol, n.categoria, n.procedencia, n.precio_declarado,"
            " EXISTS (SELECT 1 FROM precio_historico p WHERE p.nodo_id = n.id),"
            " EXISTS (SELECT 1 FROM version_concepto v WHERE v.nodo_id = n.id)"
            " FROM nodo n LEFT JOIN unidad u ON u.id = n.unidad_id WHERE n.clave = %s AND n.rol <> 'estructural'", (clave,)).fetchone()
        if fila is None:
            raise KeyError(clave)
        _, descripcion, unidad, rol, categoria, procedencia, precio, con_historico, con_matriz = fila
        return NodoDelCatalogo(clave, descripcion, unidad, rol, categoria, procedencia, precio if con_historico else None, con_matriz)

    def citas_de(self, clave: str) -> CitasDe:
        nodo_id = self.id_de(clave)
        with self.conn.transaction():
            self.conn.execute("SET TRANSACTION ISOLATION LEVEL REPEATABLE READ")
            versiones = self.conn.execute(
                "SELECT DISTINCT p.clave, v.id, v.version, v.huella, v.pu FROM composicion c JOIN version_concepto v ON v.id = c.version_id"
                " JOIN nodo p ON p.id = c.padre_id WHERE c.hijo_id = %s"
                " AND v.version = (SELECT max(version) FROM version_concepto WHERE nodo_id = v.nodo_id) ORDER BY p.clave", (nodo_id,)).fetchall()
            padres = []
            for padre, vid, version, huella, pu in versiones:
                renglones = tuple(r[0] for r in self.conn.execute(
                    "SELECT id FROM composicion WHERE version_id IS NULL AND hijo_version_id = %s AND baja_carga_id IS NULL ORDER BY id", (vid,)))
                padres.append(PadreCitante(padre, version, huella, pu, self._lineas_de(vid), renglones))
            directos = self.conn.execute(
                "SELECT count(*) FROM composicion WHERE hijo_id = %s AND version_id IS NULL AND baja_carga_id IS NULL", (nodo_id,)).fetchone()[0]
        return CitasDe(tuple(padres), directos)

    def clones(self) -> List[ClonGuardado]:
        filas = self.conn.execute(
            "SELECT c.id, o.clave, n.clave, c.modo, c.reconoce_clave_vieja_al_importar, c.exporta_clave_vieja, c.usuario, c.rol, c.carga_id,"
            " c.resumen, c.creada_en FROM clon c JOIN nodo o ON o.id = c.original_id JOIN nodo n ON n.id = c.clon_id ORDER BY c.id").fetchall()
        return [ClonGuardado(*f) for f in filas]

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
                    " WHERE (c.version_id IS NULL AND c.baja_carga_id IS NULL)"
                    " OR (c.version_id IS NOT NULL AND v.version = (SELECT max(version) FROM version_concepto WHERE nodo_id = v.nodo_id))"):
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
        for clave, texto in plan.descripciones:
            cur.execute("UPDATE nodo SET descripcion = %s WHERE id = %s", (texto, nodo_id[clave]))

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

        for r in plan.reconciliaciones:
            self._reconciliar(cur, r, carga_id, nodo_id, u)

    def _reconciliar(self, cur: "psycopg.Cursor", r: ReconciliacionPlan, carga_id: int, nodo_id: Dict[str, int], u) -> None:
        """Lo que `core/reconciliacion.py` decidió, aplicado: las cantidades, las bajas, el lugar y las altas, cada cosa con su historia."""
        def anota(renglon: int, campo: str, antes: Optional[str], despues: Optional[str]) -> None:
            cur.execute("INSERT INTO renglon_historia (renglon_id, carga_id, campo, antes, despues) VALUES (%s, %s, %s, %s, %s)",
                        (renglon, carga_id, campo, antes, despues))

        for lid, antes, ahora in r.cantidades:
            cur.execute("UPDATE composicion SET cantidad = %s WHERE id = %s AND version_id IS NULL", (ahora, lid))
            anota(lid, "cantidad", str(antes), str(ahora))
        if r.bajas:
            for lid, cantidad in cur.execute("SELECT id, cantidad FROM composicion WHERE id = ANY(%s)", (list(r.bajas),)).fetchall():
                anota(lid, "baja", str(cantidad), None)
            cur.execute("UPDATE composicion SET baja_carga_id = %s WHERE id = ANY(%s) AND version_id IS NULL", (carga_id, list(r.bajas)))
        if r.bajas_de_bloque:
            # su ruta queda libre para un bloque nuevo que se llame igual
            cur.execute("UPDATE nodo SET baja_carga_id = %s, ruta_natural = ruta_natural || '~baja' || %s WHERE id = ANY(%s)",
                        (carga_id, str(carga_id), list(r.bajas_de_bloque)))
        if r.ordenes:
            cur.execute("UPDATE composicion SET orden = orden + 1000000 WHERE id = ANY(%s)", ([lid for lid, _, _ in r.ordenes],))  # el índice es único
            for lid, antes, ahora in r.ordenes:
                cur.execute("UPDATE composicion SET orden = %s WHERE id = %s", (ahora, lid))
                anota(lid, "orden", str(antes), str(ahora))
        if r.altas:
            vigente: Dict[int, int] = {n: v for v, n in cur.execute(
                "SELECT DISTINCT ON (nodo_id) id, nodo_id FROM version_concepto ORDER BY nodo_id, version DESC")}
            nodo_de_alta: Dict[int, int] = {}
            for a in sorted(r.altas, key=lambda a: a.indice):
                padre = a.padre_id if a.padre_id is not None else nodo_de_alta[a.padre_alta]
                if a.tipo == "Concepto":
                    hijo = nodo_id[a.clave]
                    version = vigente.get(hijo)
                else:
                    hijo = cur.execute(
                        "INSERT INTO nodo (presupuesto_id, clave, descripcion, unidad_id, rol, categoria, tipo_opus, ruta_natural)"
                        " VALUES (%s, %s, %s, %s, 'estructural', 'concepto', %s, %s) RETURNING id",
                        (r.presupuesto_id, a.clave, a.descripcion, u(a.unidad), a.tipo, a.ruta_natural)).fetchone()[0]
                    nodo_de_alta[a.indice] = hijo
                    version = None
                linea = cur.execute(
                    "INSERT INTO composicion (padre_id, hijo_id, hijo_version_id, cantidad, orden, reporta_a)"
                    " VALUES (%s, %s, %s, %s, %s, 'concepto') RETURNING id", (padre, hijo, version, a.cantidad, a.orden)).fetchone()[0]
                anota(linea, "alta", None, str(a.cantidad))
        cur.execute("UPDATE presupuesto SET huella = %s WHERE id = %s", (r.huella or f"parcial:{carga_id}", r.presupuesto_id))

    def contratar(self, plan: PlanDeContratacion) -> ResultadoContratacion:
        with self.conn.transaction():
            self.conn.execute("SELECT pg_advisory_xact_lock(%s)", (CANDADO_DEL_CATALOGO,))
            ultima = self._ultima_carga()
            if ultima != plan.base:
                raise CatalogoCambio(f"la última carga es la {ultima} y esta se revisó sobre la {plan.base}")
            nodo = self.conn.execute("SELECT presupuesto_id, ruta_natural FROM nodo WHERE id = %s AND rol = 'estructural'", (plan.nodo_id,)).fetchone()
            if nodo is None or nodo[0] != plan.presupuesto_id:
                raise ValueError(f"el nodo {plan.nodo_id} no es un bloque del presupuesto {plan.presupuesto_id}")
            ya = self.conn.execute(
                "WITH RECURSIVE arriba (id) AS (SELECT %s::bigint UNION SELECT c.padre_id FROM composicion c JOIN arriba a ON c.hijo_id = a.id"
                " WHERE c.version_id IS NULL) SELECT n.ruta_natural, e.nodo_id FROM estado_congelamiento e JOIN arriba a ON a.id = e.nodo_id"
                " JOIN nodo n ON n.id = e.nodo_id WHERE e.estado = 'contratado' LIMIT 1", (plan.nodo_id,)).fetchone()
            if ya is not None:
                raise YaContratado(f"el bloque {ya[0]} ya está contratado", ya[1])
            carga_id = self.conn.execute(
                "INSERT INTO carga (usuario, rol, archivos, resumen, tipo) VALUES (%s, %s, '{}'::jsonb, %s, 'contratacion') RETURNING id",
                (plan.usuario, plan.rol, Jsonb(dict(plan.resumen)))).fetchone()[0]
            with self.conn.cursor() as cur:
                for v in plan.versiones_nuevas:
                    anterior = cur.execute(
                        "SELECT v.id, v.nodo_id, v.version, v.huella FROM version_concepto v JOIN nodo n ON n.id = v.nodo_id"
                        " WHERE n.clave = %s AND n.rol <> 'estructural' ORDER BY v.version DESC LIMIT 1", (v.clave,)).fetchone()
                    if anterior is None:
                        raise ValueError(f"{v.clave} no tiene matriz: no hay versión de la que sacar la nueva")
                    nueva = cur.execute(
                        "INSERT INTO version_concepto (nodo_id, version, huella, pu, carga_id) VALUES (%s, %s, %s, %s, %s) RETURNING id",
                        (anterior[1], anterior[2] + 1, anterior[3], v.pu, carga_id)).fetchone()[0]
                    cur.execute(
                        "INSERT INTO composicion (padre_id, version_id, hijo_id, cantidad, orden, reporta_a, tipo_cantidad, base_porcentaje)"
                        " SELECT padre_id, %s, hijo_id, cantidad, orden, reporta_a, tipo_cantidad, base_porcentaje FROM composicion"
                        " WHERE version_id = %s", (nueva, anterior[0]))
                for renglon_id, clave in plan.renglones:
                    n = cur.execute(
                        "UPDATE composicion c SET hijo_version_id ="
                        " (SELECT v.id FROM version_concepto v WHERE v.nodo_id = c.hijo_id ORDER BY v.version DESC LIMIT 1)"
                        " FROM nodo h WHERE c.id = %s AND c.version_id IS NULL AND h.id = c.hijo_id AND h.clave = %s AND h.rol <> 'estructural'",
                        (renglon_id, clave)).rowcount
                    if n != 1:
                        raise ValueError(f"el renglón {renglon_id} no es de {clave}")
                congelamiento_id = cur.execute(
                    "INSERT INTO estado_congelamiento (nodo_id, estado, usuario, rol, carga_id, resumen)"
                    " VALUES (%s, 'contratado', %s, %s, %s, %s) RETURNING id",
                    (plan.nodo_id, plan.usuario, plan.rol, carga_id, Jsonb(dict(plan.resumen)))).fetchone()[0]
        return ResultadoContratacion(carga_id, congelamiento_id, len(plan.versiones_nuevas), len(plan.renglones))

    def clonar(self, plan: PlanDeClonacion) -> ResultadoClonacion:
        with self.conn.transaction():
            self.conn.execute("SELECT pg_advisory_xact_lock(%s)", (CANDADO_DEL_CATALOGO,))
            ultima = self._ultima_carga()
            if ultima != plan.base:
                raise CatalogoCambio(f"la última carga es la {ultima} y esta se revisó sobre la {plan.base}")
            original = self.conn.execute(
                "SELECT id, unidad_id, rol, categoria FROM nodo WHERE clave = %s AND rol <> 'estructural'", (plan.original,)).fetchone()
            if original is None:
                raise ValueError(f"no hay un nodo del catálogo con la clave {plan.original}")
            if self.conn.execute("SELECT 1 FROM nodo WHERE clave = %s AND rol <> 'estructural'", (plan.clave,)).fetchone() is not None:
                raise ValueError(f"ya hay un nodo del catálogo con la clave {plan.clave}")
            original_id, unidad_id, rol, categoria = original
            carga_id = self.conn.execute(
                "INSERT INTO carga (usuario, rol, archivos, resumen, tipo) VALUES (%s, %s, '{}'::jsonb, %s, 'clonacion') RETURNING id",
                (plan.usuario, plan.rol, Jsonb(dict(plan.resumen)))).fetchone()[0]
            nuevo = plan.nuevo
            precio = nuevo.precio if isinstance(nuevo, InsumoPlan) else None
            with self.conn.cursor() as cur:
                clon_id = cur.execute(
                    "INSERT INTO nodo (clave, descripcion, unidad_id, rol, categoria, modo_precio, precio_declarado, procedencia)"
                    " VALUES (%s, %s, %s, %s, %s, %s, %s, 'clonacion') RETURNING id",
                    (plan.clave, nuevo.descripcion, unidad_id, rol, categoria, "declarado" if precio is not None else "calculado", precio)).fetchone()[0]
                if isinstance(nuevo, InsumoPlan) and nuevo.con_historico:
                    cur.execute("INSERT INTO precio_historico (nodo_id, precio, fuente, carga_id) VALUES (%s, %s, 'catalogo', %s)",
                                (clon_id, nuevo.precio, carga_id))
                if isinstance(nuevo, NodoConMatriz):
                    self._escribir_version(cur, clon_id, 1, nuevo.huella, nuevo.pu, carga_id, nuevo.lineas)
                fijados = 0
                for s in plan.sustituciones:
                    padre_id, ultima_version = cur.execute(
                        "SELECT n.id, coalesce(max(v.version), 0) FROM nodo n LEFT JOIN version_concepto v ON v.nodo_id = n.id"
                        " WHERE n.clave = %s AND n.rol <> 'estructural' GROUP BY n.id", (s.clave,)).fetchone()
                    version_id = self._escribir_version(cur, padre_id, ultima_version + 1, s.huella, s.pu, carga_id, s.lineas)
                    for renglon_id in s.renglones:
                        n = cur.execute(
                            "UPDATE composicion c SET hijo_version_id = %s FROM nodo h"
                            " WHERE c.id = %s AND c.version_id IS NULL AND h.id = c.hijo_id AND h.clave = %s AND h.rol <> 'estructural'",
                            (version_id, renglon_id, s.clave)).rowcount
                        if n != 1:
                            raise ValueError(f"el renglón {renglon_id} no es de {s.clave}")
                        fijados += 1
                cur.execute(
                    "INSERT INTO clon (original_id, clon_id, modo, reconoce_clave_vieja_al_importar, usuario, rol, carga_id, resumen)"
                    " VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
                    (original_id, clon_id, plan.modo, plan.modo == "sustituir", plan.usuario, plan.rol, carga_id, Jsonb(dict(plan.resumen))))
        return ResultadoClonacion(carga_id, clon_id, len(plan.sustituciones), fijados)

    @staticmethod
    def _escribir_version(cur: "psycopg.Cursor", nodo_id: int, version: int, huella: str, pu: Decimal, carga_id: int, lineas) -> int:
        """Una versión de matriz con sus líneas; las líneas se resuelven por clave."""
        version_id = cur.execute(
            "INSERT INTO version_concepto (nodo_id, version, huella, pu, carga_id) VALUES (%s, %s, %s, %s, %s) RETURNING id",
            (nodo_id, version, huella, pu, carga_id)).fetchone()[0]
        ids = {clave: id_ for id_, clave in cur.execute(
            "SELECT id, clave FROM nodo WHERE rol <> 'estructural' AND clave = ANY(%s)", ([l.hijo for l in lineas],))}
        for l in lineas:
            if l.hijo not in ids:
                raise ValueError(f"{l.hijo} no está en el catálogo")
        cur.executemany(
            "INSERT INTO composicion (padre_id, version_id, hijo_id, cantidad, orden, reporta_a, tipo_cantidad, base_porcentaje)"
            " VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
            [(nodo_id, version_id, ids[l.hijo], l.cantidad, orden, l.reporta_a.value,
              "porcentaje" if l.porcentaje else "fija", "suma_jornales_hermanos" if l.porcentaje else None)
             for orden, l in enumerate(lineas, start=1)])
        return version_id
