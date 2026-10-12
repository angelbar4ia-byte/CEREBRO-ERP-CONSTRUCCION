/* Generado por backend/api/generar_cliente.py a partir del OpenAPI de la API del programa (D-55).
   No se edita a mano: si la API cambia se vuelve a generar, y una prueba avisa si este archivo quedó viejo.

   Cada operación recibe un objeto con los parámetros por su nombre en el spec (`programa_id`, `x-rol`…) y,
   si lleva cuerpo, el cuerpo en `cuerpo`. Devuelve lo que contesta la API ya leído (JSON, o texto si es HTML)
   y, si contesta con error, lanza un `ErrorApi` con `status`, `codigo`, `mensaje` y `detalle`.

   Las operaciones que el spec declara protegidas mandan `Authorization: Bearer <token>` si `ClientePrograma.token` tiene uno
   (B-96): el cliente no sabe de dónde sale, solo lo manda. */
const OPERACIONES = {
  "aplicar_carga": {
    "metodo": "POST",
    "ruta": "/cargas",
    "ruta_params": [],
    "consulta": [],
    "cabeceras": [
      "x-rol",
      "x-usuario"
    ],
    "cuerpo": true,
    "seguridad": true
  },
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
  "clonar_insumo": {
    "metodo": "POST",
    "ruta": "/clonaciones",
    "ruta_params": [],
    "consulta": [],
    "cabeceras": [
      "x-rol",
      "x-usuario"
    ],
    "cuerpo": true,
    "seguridad": true
  },
  "colgar_programa": {
    "metodo": "POST",
    "ruta": "/programas/{programa_id}/colgado",
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
  "contratar_subarbol": {
    "metodo": "POST",
    "ruta": "/presupuestos/{presupuesto_id}/contrataciones",
    "ruta_params": [
      "presupuesto_id"
    ],
    "consulta": [],
    "cabeceras": [
      "x-rol",
      "x-usuario"
    ],
    "cuerpo": true,
    "seguridad": true
  },
  "corregir_prefijo": {
    "metodo": "POST",
    "ruta": "/correcciones-de-prefijo",
    "ruta_params": [],
    "consulta": [],
    "cabeceras": [
      "x-rol",
      "x-usuario"
    ],
    "cuerpo": true,
    "seguridad": true
  },
  "dejar_propuesta": {
    "metodo": "POST",
    "ruta": "/bandeja/propuestas",
    "ruta_params": [],
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
  "listar_alertas": {
    "metodo": "GET",
    "ruta": "/bandeja/alertas",
    "ruta_params": [],
    "consulta": [
      "estado",
      "tipo"
    ],
    "cabeceras": [],
    "cuerpo": false,
    "seguridad": true
  },
  "listar_cargas": {
    "metodo": "GET",
    "ruta": "/cargas",
    "ruta_params": [],
    "consulta": [],
    "cabeceras": [],
    "cuerpo": false,
    "seguridad": true
  },
  "listar_clones": {
    "metodo": "GET",
    "ruta": "/clones",
    "ruta_params": [],
    "consulta": [],
    "cabeceras": [],
    "cuerpo": false,
    "seguridad": true
  },
  "listar_presupuestos": {
    "metodo": "GET",
    "ruta": "/presupuestos",
    "ruta_params": [],
    "consulta": [],
    "cabeceras": [],
    "cuerpo": false,
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
  "listar_propuestas": {
    "metodo": "GET",
    "ruta": "/bandeja/propuestas",
    "ruta_params": [],
    "consulta": [
      "estado",
      "tipo"
    ],
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
  "proponer_carga": {
    "metodo": "POST",
    "ruta": "/cargas/propuestas",
    "ruta_params": [],
    "consulta": [],
    "cabeceras": [
      "x-rol",
      "x-usuario"
    ],
    "cuerpo": true,
    "seguridad": true
  },
  "proponer_clonacion": {
    "metodo": "POST",
    "ruta": "/clonaciones/propuestas",
    "ruta_params": [],
    "consulta": [],
    "cabeceras": [
      "x-rol",
      "x-usuario"
    ],
    "cuerpo": true,
    "seguridad": true
  },
  "proponer_colgado": {
    "metodo": "POST",
    "ruta": "/programas/{programa_id}/colgado/propuestas",
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
  "proponer_contratacion": {
    "metodo": "POST",
    "ruta": "/presupuestos/{presupuesto_id}/contrataciones/propuestas",
    "ruta_params": [
      "presupuesto_id"
    ],
    "consulta": [],
    "cabeceras": [
      "x-rol",
      "x-usuario"
    ],
    "cuerpo": true,
    "seguridad": true
  },
  "proponer_correccion_de_prefijo": {
    "metodo": "POST",
    "ruta": "/correcciones-de-prefijo/propuestas",
    "ruta_params": [],
    "consulta": [],
    "cabeceras": [
      "x-rol",
      "x-usuario"
    ],
    "cuerpo": true,
    "seguridad": true
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
  "resolver_alerta": {
    "metodo": "POST",
    "ruta": "/bandeja/alertas/{alerta_id}/resolucion",
    "ruta_params": [
      "alerta_id"
    ],
    "consulta": [],
    "cabeceras": [
      "x-rol",
      "x-usuario"
    ],
    "cuerpo": true,
    "seguridad": true
  },
  "resolver_propuesta": {
    "metodo": "POST",
    "ruta": "/bandeja/propuestas/{propuesta_id}/resolucion",
    "ruta_params": [
      "propuesta_id"
    ],
    "consulta": [],
    "cabeceras": [
      "x-rol",
      "x-usuario"
    ],
    "cuerpo": true,
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
  "ver_alerta": {
    "metodo": "GET",
    "ruta": "/bandeja/alertas/{alerta_id}",
    "ruta_params": [
      "alerta_id"
    ],
    "consulta": [],
    "cabeceras": [],
    "cuerpo": false,
    "seguridad": true
  },
  "ver_bandeja": {
    "metodo": "GET",
    "ruta": "/bandeja",
    "ruta_params": [],
    "consulta": [],
    "cabeceras": [],
    "cuerpo": false,
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
  "ver_contratados": {
    "metodo": "GET",
    "ruta": "/presupuestos/{presupuesto_id}/contratados",
    "ruta_params": [
      "presupuesto_id"
    ],
    "consulta": [],
    "cabeceras": [],
    "cuerpo": false,
    "seguridad": true
  },
  "ver_nodo": {
    "metodo": "GET",
    "ruta": "/catalogo/{clave}",
    "ruta_params": [
      "clave"
    ],
    "consulta": [],
    "cabeceras": [],
    "cuerpo": false,
    "seguridad": true
  },
  "ver_precios": {
    "metodo": "GET",
    "ruta": "/catalogo/{clave}/precios",
    "ruta_params": [
      "clave"
    ],
    "consulta": [],
    "cabeceras": [],
    "cuerpo": false,
    "seguridad": true
  },
  "ver_presupuesto": {
    "metodo": "GET",
    "ruta": "/presupuestos/{presupuesto_id}",
    "ruta_params": [
      "presupuesto_id"
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
  },
  "ver_propuesta": {
    "metodo": "GET",
    "ruta": "/bandeja/propuestas/{propuesta_id}",
    "ruta_params": [
      "propuesta_id"
    ],
    "consulta": [],
    "cabeceras": [],
    "cuerpo": false,
    "seguridad": true
  },
  "ver_versiones_de_matriz": {
    "metodo": "GET",
    "ruta": "/catalogo/{clave}/versiones",
    "ruta_params": [
      "clave"
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
  /** POST /cargas — Cargar los archivos de OPUS: entra lo que se propuso, lo detenido queda dicho en la carga */
  cliente.aplicar_carga = args => llamar("aplicar_carga", args || {});
  /** POST /programas/{programa_id}/ediciones — Aplicar una edición y guardarla en la bitácora */
  cliente.aplicar_edicion = args => llamar("aplicar_edicion", args || {});
  /** POST /clonaciones — Clonar un insumo (y, si se pide, sustituir el original): la clave vieja sigue entrando */
  cliente.clonar_insumo = args => llamar("clonar_insumo", args || {});
  /** POST /programas/{programa_id}/colgado — Colgar el programa del presupuesto: se ponen los enlaces que casan; uno puesto no se mueve */
  cliente.colgar_programa = args => llamar("colgar_programa", args || {});
  /** POST /presupuestos/{presupuesto_id}/contrataciones — Contratar un bloque del presupuesto: fija el PU de sus conceptos a hoy y lo congela */
  cliente.contratar_subarbol = args => llamar("contratar_subarbol", args || {});
  /** POST /correcciones-de-prefijo — Sustituir cada clave de un prefijo por su clon con el prefijo nuevo; lo que hoy no se puede se salta y se dice */
  cliente.corregir_prefijo = args => llamar("corregir_prefijo", args || {});
  /** POST /bandeja/propuestas — Dejar una propuesta con su evidencia: queda pendiente hasta que otra persona la apruebe o la rechace */
  cliente.dejar_propuesta = args => llamar("dejar_propuesta", args || {});
  /** DELETE /programas/{programa_id}/ediciones/{edicion_id} — Deshacer una edición aplicada */
  cliente.deshacer_edicion = args => llamar("deshacer_edicion", args || {});
  /** POST /programas — Subir un programa: se carga, se guardan sus vínculos y se dice cuáles no entraron */
  cliente.importar_programa = args => llamar("importar_programa", args || {});
  /** GET /bandeja/alertas — Las alertas, de la más vieja a la más nueva; se filtran por estado y por tipo */
  cliente.listar_alertas = args => llamar("listar_alertas", args || {});
  /** GET /cargas — Todo lo que se ha cargado, contratado o clonado, con quién y cuándo */
  cliente.listar_cargas = args => llamar("listar_cargas", args || {});
  /** GET /clones — Los insumos clonados y sustituidos, y quién lo decidió */
  cliente.listar_clones = args => llamar("listar_clones", args || {});
  /** GET /presupuestos — Los presupuestos cargados */
  cliente.listar_presupuestos = args => llamar("listar_presupuestos", args || {});
  /** GET /programas — Los programas que hay, del más viejo al más nuevo */
  cliente.listar_programas = args => llamar("listar_programas", args || {});
  /** GET /bandeja/propuestas — Las propuestas, de la más vieja a la más nueva; se filtran por estado y por tipo */
  cliente.listar_propuestas = args => llamar("listar_propuestas", args || {});
  /** GET /programas/{programa_id}/gantt — La pantalla del Gantt de este programa */
  cliente.pantalla_gantt = args => llamar("pantalla_gantt", args || {});
  /** GET / — La pantalla de los programas: la lista y subir uno */
  cliente.pantalla_programas = args => llamar("pantalla_programas", args || {});
  /** POST /cargas/propuestas — Qué pasaría si se cargaran estos archivos de OPUS: no escribe nada */
  cliente.proponer_carga = args => llamar("proponer_carga", args || {});
  /** POST /clonaciones/propuestas — Qué pasaría si se clonara un insumo: lo que lo cita y lo que impide hacerlo; no escribe nada */
  cliente.proponer_clonacion = args => llamar("proponer_clonacion", args || {});
  /** POST /programas/{programa_id}/colgado/propuestas — Cómo quedaría colgado el programa del presupuesto, de los dos lados: no escribe nada */
  cliente.proponer_colgado = args => llamar("proponer_colgado", args || {});
  /** POST /presupuestos/{presupuesto_id}/contrataciones/propuestas — Qué PU se fijarían al contratar un bloque y cuánto cambia el monto: no escribe nada */
  cliente.proponer_contratacion = args => llamar("proponer_contratacion", args || {});
  /** POST /correcciones-de-prefijo/propuestas — Qué claves de un prefijo pasarían a otro, cada una con lo que la cita hoy: no escribe nada */
  cliente.proponer_correccion_de_prefijo = args => llamar("proponer_correccion_de_prefijo", args || {});
  /** POST /programas/{programa_id}/propuestas — Qué pasaría si se aplicara esta edición: no guarda nada */
  cliente.proponer_edicion = args => llamar("proponer_edicion", args || {});
  /** GET /yo — Quién eres y qué puedes hacer */
  cliente.quien_soy = args => llamar("quien_soy", args || {});
  /** POST /bandeja/alertas/{alerta_id}/resolucion — Resolver una alerta (era real y se atendió) o descartarla (no era nada), diciendo qué era */
  cliente.resolver_alerta = args => llamar("resolver_alerta", args || {});
  /** POST /bandeja/propuestas/{propuesta_id}/resolucion — Aprobar (el sistema hace lo propuesto, a nombre de quien aprueba) o rechazar (y decir por qué) */
  cliente.resolver_propuesta = args => llamar("resolver_propuesta", args || {});
  /** POST /programas/{programa_id}/versiones — Subir la versión nueva de un programa: las ediciones que siguen teniendo sentido pasan a ella */
  cliente.subir_version = args => llamar("subir_version", args || {});
  /** GET /bandeja/alertas/{alerta_id} — Una alerta: qué se comparó, con qué umbral, cuántas veces volvió a aparecer y, si ya se cerró, quién y qué era */
  cliente.ver_alerta = args => llamar("ver_alerta", args || {});
  /** GET /bandeja — Lo que hay pendiente de decidir: propuestas por tipo y alertas activas */
  cliente.ver_bandeja = args => llamar("ver_bandeja", args || {});
  /** GET /programas/{programa_id}/ediciones — Todo lo que se ha editado, también lo revertido */
  cliente.ver_bitacora = args => llamar("ver_bitacora", args || {});
  /** GET /presupuestos/{presupuesto_id}/contratados — Los bloques del presupuesto que ya se contrataron */
  cliente.ver_contratados = args => llamar("ver_contratados", args || {});
  /** GET /catalogo/{clave} — Un insumo, compuesto o concepto del catálogo, con quién lo cita */
  cliente.ver_nodo = args => llamar("ver_nodo", args || {});
  /** GET /catalogo/{clave}/precios — La historia de precio de un insumo */
  cliente.ver_precios = args => llamar("ver_precios", args || {});
  /** GET /presupuestos/{presupuesto_id} — Un presupuesto: renglón por renglón, con su cantidad, su PU y su total */
  cliente.ver_presupuesto = args => llamar("ver_presupuesto", args || {});
  /** GET /programas/{programa_id} — El programa base y su bitácora */
  cliente.ver_programa = args => llamar("ver_programa", args || {});
  /** GET /bandeja/propuestas/{propuesta_id} — Una propuesta, con su evidencia, quién la dejó y, si ya se resolvió, quién y por qué */
  cliente.ver_propuesta = args => llamar("ver_propuesta", args || {});
  /** GET /catalogo/{clave}/versiones — Las versiones de la matriz (APU) de un concepto o compuesto, con sus líneas */
  cliente.ver_versiones_de_matriz = args => llamar("ver_versiones_de_matriz", args || {});
  return cliente;
})();
if (typeof module !== "undefined" && module.exports) module.exports = ClientePrograma;
