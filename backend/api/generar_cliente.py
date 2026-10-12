"""
El cliente de la pantalla, generado del spec de la API (D-55): una función por cada `operationId`.

    python3 -m api.generar_cliente              escribe frontend/gantt/cliente_programa.js
    python3 -m api.generar_cliente --verificar  sale con error si el archivo ya no es el que daría el spec

Nadie escribe a mano una ruta, un encabezado o un código de error en la pantalla: se lo pide a este cliente. Si la
API cambia, el archivo viejo deja de coincidir y la prueba de `tests/test_cliente_programa.py` lo dice.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Dict, List

from core.memoria_bandeja import MemoriaBandeja
from core.memoria_catalogo import MemoriaCatalogo
from core.memoria_programa import MemoriaPrograma
from core.servicio_programa import ServicioPrograma

from .app import crear_app

DESTINO = Path(__file__).resolve().parents[2] / "frontend" / "gantt" / "cliente_programa.js"

ENCABEZADO = """\
/* Generado por backend/api/generar_cliente.py a partir del OpenAPI de la API del programa (D-55).
   No se edita a mano: si la API cambia se vuelve a generar, y una prueba avisa si este archivo quedó viejo.

   Cada operación recibe un objeto con los parámetros por su nombre en el spec (`programa_id`, `x-rol`…) y,
   si lleva cuerpo, el cuerpo en `cuerpo`. Devuelve lo que contesta la API ya leído (JSON, o texto si es HTML)
   y, si contesta con error, lanza un `ErrorApi` con `status`, `codigo`, `mensaje` y `detalle`.

   Las operaciones que el spec declara protegidas mandan `Authorization: Bearer <token>` si `ClientePrograma.token` tiene uno
   (B-96): el cliente no sabe de dónde sale, solo lo manda. */
"""

EJECUCION = """\
const ClientePrograma = (() => {
  class ErrorApi extends Error {
    constructor(status, detalle) {
      const d = detalle && typeof detalle === "object" && !Array.isArray(detalle) ? detalle : {};
      super(d.mensaje || (status === 0 ? "No hay conexión con el servidor." : "El servidor contestó " + status + "."));
      this.status = status;
      this.codigo = d.codigo || (status === 422 ? "validacion" : "error");
      this.mensaje = this.message;
      this.detalle = detalle;
    }
  }

  async function llamar(nombre, args) {
    const op = OPERACIONES[nombre];
    let ruta = op.ruta;
    for (const p of op.ruta_params) {
      if (args[p] === undefined) throw new Error(nombre + ": falta " + p);
      ruta = ruta.replace("{" + p + "}", encodeURIComponent(args[p]));
    }
    const consulta = op.consulta.filter(p => args[p] !== undefined && args[p] !== null)
      .map(p => encodeURIComponent(p) + "=" + encodeURIComponent(args[p])).join("&");
    const cabeceras = {};
    for (const h of op.cabeceras) if (args[h] !== undefined && args[h] !== null) cabeceras[h] = String(args[h]);
    if (op.seguridad && cliente.token) cabeceras["Authorization"] = "Bearer " + cliente.token;
    const init = { method: op.metodo, headers: cabeceras };
    if (op.cuerpo) { cabeceras["Content-Type"] = "application/json"; init.body = JSON.stringify(args.cuerpo); }
    let r;
    try { r = await fetch(cliente.base + ruta + (consulta ? "?" + consulta : ""), init); }
    catch (e) { throw new ErrorApi(0, null); }
    const tipo = r.headers.get("content-type") || "";
    const dato = tipo.includes("json") ? await r.json() : await r.text();
    if (!r.ok) throw new ErrorApi(r.status, dato && dato.detail !== undefined ? dato.detail : dato);
    return dato;
  }

  const cliente = { ErrorApi, base: "", token: null };
"""


def _operaciones(spec: Dict[str, Any]) -> List[Dict[str, Any]]:
    ops = []
    for ruta, metodos in spec["paths"].items():
        for metodo, op in metodos.items():
            parametros = op.get("parameters", [])
            ops.append(
                {
                    "nombre": op["operationId"],
                    "resumen": op.get("summary", ""),
                    "metodo": metodo.upper(),
                    "ruta": ruta,
                    "ruta_params": [p["name"] for p in parametros if p["in"] == "path"],
                    "consulta": [p["name"] for p in parametros if p["in"] == "query"],
                    "cabeceras": [p["name"] for p in parametros if p["in"] == "header"],
                    "cuerpo": "requestBody" in op,
                    "seguridad": bool(op.get("security")),
                }
            )
    return sorted(ops, key=lambda o: o["nombre"])


def generar(spec: Dict[str, Any]) -> str:
    ops = _operaciones(spec)
    tabla = {
        o["nombre"]: {k: o[k] for k in ("metodo", "ruta", "ruta_params", "consulta", "cabeceras", "cuerpo", "seguridad")} for o in ops
    }
    partes = [ENCABEZADO]
    partes.append("const OPERACIONES = " + json.dumps(tabla, ensure_ascii=False, indent=2) + ";\n\n")
    partes.append(EJECUCION)
    for o in ops:
        partes.append(f"  /** {o['metodo']} {o['ruta']} — {o['resumen']} */\n")
        partes.append(f"  cliente.{o['nombre']} = args => llamar({json.dumps(o['nombre'])}, args || {{}});\n")
    partes.append("  return cliente;\n})();\nif (typeof module !== \"undefined\" && module.exports) module.exports = ClientePrograma;\n")
    return "".join(partes)


def spec_de_la_api() -> Dict[str, Any]:
    # el spec no depende de los datos: basta una aplicación con repositorios vacíos, el del programa, el del catálogo y el de la bandeja
    return crear_app(ServicioPrograma(MemoriaPrograma()), catalogo=MemoriaCatalogo(), bandeja=MemoriaBandeja()).openapi()


def main(argv: List[str]) -> int:
    texto = generar(spec_de_la_api())
    if "--verificar" in argv:
        actual = DESTINO.read_text(encoding="utf-8") if DESTINO.exists() else ""
        if actual != texto:
            print(f"{DESTINO} no coincide con el spec de la API: corre python3 -m api.generar_cliente", file=sys.stderr)
            return 1
        print("El cliente coincide con el spec.")
        return 0
    DESTINO.write_text(texto, encoding="utf-8")
    print(f"Escrito {DESTINO} ({len(texto)} caracteres).")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
