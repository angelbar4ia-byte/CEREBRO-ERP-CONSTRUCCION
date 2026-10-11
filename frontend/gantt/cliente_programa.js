/* Generado por backend/api/generar_cliente.py a partir del OpenAPI de la API del programa (D-55).
   No se edita a mano: si la API cambia se vuelve a generar, y una prueba avisa si este archivo quedó viejo.

   Cada operación recibe un objeto con los parámetros por su nombre en el spec (`programa_id`, `x-rol`…) y,
   si lleva cuerpo, el cuerpo en `cuerpo`. Devuelve lo que contesta la API ya leído (JSON, o texto si es HTML)
   y, si contesta con error, lanza un `ErrorApi` con `status`, `codigo`, `mensaje` y `detalle`.

   Las operaciones que el spec declara protegidas mandan `Authorization: Bearer <token>` si `ClientePrograma.token` tiene uno
   (B-96): el cliente no sabe de dónde sale, solo lo manda. */
const OPERACIONES = {
  "aplicar_edicion": {
    "metodo": "POST",
    "ruta": "/programas/{programa_id}/ediciones",
    "ruta_params": [
      "programa_id"
    ],
    "consulta": [],
    "cabeceras": [
      "x-rol",
      "x-usuario"
    ],
    "cuerpo": true,
    "seguridad": true
  },
  "deshacer_edicion": {
    "metodo": "DELETE",
    "ruta": "/programas/{programa_id}/ediciones/{edicion_id}",
    "ruta_params": [
      "programa_id",
      "edicion_id"
    ],
    "consulta": [],
    "cabeceras": [
      "x-rol",
      "x-usuario"
    ],
    "cuerpo": false,
    "seguridad": true
  },
  "importar_programa": {
    "metodo": "POST",
    "ruta": "/programas",
    "ruta_params": [],
    "consulta": [],
    "cabeceras": [
      "x-rol",
      "x-usuario"
    ],
    "cuerpo": true,
    "seguridad": true
  },
  "listar_programas": {
    "metodo": "GET",
    "ruta": "/programas",
    "ruta_params": [],
    "consulta": [],
    "cabeceras": [],
    "cuerpo": false,
    "seguridad": true
  },
  "pantalla_gantt": {
    "metodo": "GET",
    "ruta": "/programas/{programa_id}/gantt",
    "ruta_params": [
      "programa_id"
    ],
    "consulta": [],
    "cabeceras": [],
    "cuerpo": false,
    "seguridad": false
  },
  "pantalla_programas": {
    "metodo": "GET",
    "ruta": "/",
    "ruta_params": [],
    "consulta": [],
    "cabeceras": [],
    "cuerpo": false,
    "seguridad": false
  },
  "proponer_edicion": {
    "metodo": "POST",
    "ruta": "/programas/{programa_id}/propuestas",
    "ruta_params": [
      "programa_id"
    ],
    "consulta": [],
    "cabeceras": [
      "x-rol",
      "x-usuario"
    ],
    "cuerpo": true,
    "seguridad": true
  },
  "quien_soy": {
    "metodo": "GET",
    "ruta": "/yo",
    "ruta_params": [],
    "consulta": [],
    "cabeceras": [
      "x-rol",
      "x-usuario"
    ],
    "cuerpo": false,
    "seguridad": true
  },
  "subir_version": {
    "metodo": "POST",
    "ruta": "/programas/{programa_id}/versiones",
    "ruta_params": [
      "programa_id"
    ],
    "consulta": [],
    "cabeceras": [
      "x-rol",
      "x-usuario"
    ],
    "cuerpo": true,
    "seguridad": true
  },
  "ver_bitacora": {
    "metodo": "GET",
    "ruta": "/programas/{programa_id}/ediciones",
    "ruta_params": [
      "programa_id"
    ],
    "consulta": [],
    "cabeceras": [],
    "cuerpo": false,
    "seguridad": true
  },
  "ver_programa": {
    "metodo": "GET",
    "ruta": "/programas/{programa_id}",
    "ruta_params": [
      "programa_id"
    ],
    "consulta": [],
    "cabeceras": [],
    "cuerpo": false,
    "seguridad": true
  }
};

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
  /** POST /programas/{programa_id}/ediciones — Aplicar una edición y guardarla en la bitácora */
  cliente.aplicar_edicion = args => llamar("aplicar_edicion", args || {});
  /** DELETE /programas/{programa_id}/ediciones/{edicion_id} — Deshacer una edición aplicada */
  cliente.deshacer_edicion = args => llamar("deshacer_edicion", args || {});
  /** POST /programas — Subir un programa: se carga, se guardan sus vínculos y se dice cuáles no entraron */
  cliente.importar_programa = args => llamar("importar_programa", args || {});
  /** GET /programas — Los programas que hay, del más viejo al más nuevo */
  cliente.listar_programas = args => llamar("listar_programas", args || {});
  /** GET /programas/{programa_id}/gantt — La pantalla del Gantt de este programa */
  cliente.pantalla_gantt = args => llamar("pantalla_gantt", args || {});
  /** GET / — La pantalla de los programas: la lista y subir uno */
  cliente.pantalla_programas = args => llamar("pantalla_programas", args || {});
  /** POST /programas/{programa_id}/propuestas — Qué pasaría si se aplicara esta edición: no guarda nada */
  cliente.proponer_edicion = args => llamar("proponer_edicion", args || {});
  /** GET /yo — Quién eres y qué puedes hacer */
  cliente.quien_soy = args => llamar("quien_soy", args || {});
  /** POST /programas/{programa_id}/versiones — Subir la versión nueva de un programa: las ediciones que siguen teniendo sentido pasan a ella */
  cliente.subir_version = args => llamar("subir_version", args || {});
  /** GET /programas/{programa_id}/ediciones — Todo lo que se ha editado, también lo revertido */
  cliente.ver_bitacora = args => llamar("ver_bitacora", args || {});
  /** GET /programas/{programa_id} — El programa base y su bitácora */
  cliente.ver_programa = args => llamar("ver_programa", args || {});
  return cliente;
})();
if (typeof module !== "undefined" && module.exports) module.exports = ClientePrograma;
