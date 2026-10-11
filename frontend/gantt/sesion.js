/* La sesión de quien usa las pantallas — B-96 (D-469). Las dos pantallas la comparten.

   Dos modos, que dice la API en la configuración de la página:
   - «token» (el que se despliega): el proveedor de identidad devuelve al usuario a la pantalla con `#access_token=…`;
     se guarda para esta pestaña (sessionStorage), se quita de la dirección y el cliente lo manda en cada llamada.
     Quién es y qué puede hacer lo dice la API (`quien_soy`); aquí no se elige nada.
   - «cabeceras» (solo para trabajar y probar): se elige un rol y se escribe un nombre, que viajan en X-Rol y X-Usuario.

   Lo que puede hacer cada quien viene de la API, de `ROL_FUNCION`, y no está escrito aquí: si se corrige la tabla, esta
   pantalla lo sabe en la siguiente carga. Mientras no se sabe (la respuesta no ha llegado), se deja intentar: quien decide
   es el servidor, esto solo avisa a tiempo. */
const Sesion = (() => {
  const ROLES = { control_de_obra: "Control de obra", residente: "Residente", supervisor: "Supervisor",
                  superintendente: "Superintendente", costos: "Costos", cotizador: "Cotizador" };
  const CLAVE_TOKEN = "programa.token", CLAVE_QUIEN = "gantt.quien";
  const esc = s => String(s).replace(/[&<>"']/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
  let cfg = { modo: "cabeceras", login_url: null };
  let ident = { rol: "control_de_obra", usuario: "" };
  let yo = null, lista = false, contenedor = null, espera = null;
  const oyentes = [];

  const leer = (almacen, clave) => { try { return window[almacen].getItem(clave); } catch (_) { return null; } };
  const escribir = (almacen, clave, valor) => { try { valor === null ? window[almacen].removeItem(clave) : window[almacen].setItem(clave, valor); } catch (_) { /* sin almacenamiento: se vuelve a pedir */ } };
  const nombreDeRol = r => ROLES[r] || r;
  const modo = () => cfg.modo;

  function iniciar(config) {
    cfg = Object.assign({ modo: "cabeceras", login_url: null }, config || {});
    if (cfg.modo === "token") {
      const m = /[#&]access_token=([^&]+)/.exec(location.hash);
      if (m) { escribir("sessionStorage", CLAVE_TOKEN, decodeURIComponent(m[1])); history.replaceState(null, "", location.pathname + location.search); }
      ClientePrograma.token = leer("sessionStorage", CLAVE_TOKEN);
    } else {
      try { Object.assign(ident, JSON.parse(leer("localStorage", CLAVE_QUIEN) || "{}")); } catch (_) { /* se escribe cada vez */ }
      if (!ROLES[ident.rol]) ident.rol = "control_de_obra";
    }
    return refrescar();
  }

  // en modo cabeceras van las dos cabeceras; el token, si hay, lo agrega el cliente solo
  const llamar = (op, args) => ClientePrograma[op](cfg.modo === "cabeceras" ? Object.assign({ "x-rol": ident.rol, "x-usuario": ident.usuario.trim() }, args) : (args || {}));

  function refrescar() {
    yo = null; lista = false; pintar();
    const pedir = cfg.modo === "cabeceras" && !ident.usuario.trim()
      ? ClientePrograma.quien_soy({ "x-rol": ident.rol, "x-usuario": "(sin nombre)" }) // para saber qué puede ese rol aunque no haya nombre todavía
      : llamar("quien_soy", {});
    espera = pedir.then(r => { yo = r; }, () => { yo = null; }).then(() => { lista = true; pintar(); oyentes.forEach(f => f()); });
    return espera;
  }

  const puede = funcion => yo ? yo.funciones.includes(funcion) : true;
  const describir = () => yo ? yo.roles.map(nombreDeRol).join(", ") || "ningún rol" : nombreDeRol(ident.rol);
  const usuario = () => cfg.modo === "cabeceras" ? ident.usuario.trim() : (yo ? yo.usuario : "");
  const falta = () => cfg.modo === "cabeceras"
    ? (ident.usuario.trim() ? null : "Escribe tu nombre arriba: toda acción dice quién la hizo.")
    : (yo ? null : "Falta iniciar sesión.");
  const esFaltaDeSesion = err => err && err.status === 401 && cfg.modo === "token";

  function salir() {
    escribir("sessionStorage", CLAVE_TOKEN, null); ClientePrograma.token = null;
    if (cfg.login_url) location.href = cfg.login_url; else location.reload();
  }

  function pintar() {
    if (!contenedor) return;
    contenedor.dataset.listo = lista ? "1" : "0";
    if (cfg.modo === "token") {
      contenedor.innerHTML = yo
        ? `<b>${esc(yo.nombre || yo.correo || yo.usuario)}</b> <span class="mono">· ${esc(yo.roles.map(nombreDeRol).join(", ") || "sin rol")}</span> <button class="b" type="button" id="b-salir">Salir</button>`
        : (lista ? `<span>Sin sesión</span> ${cfg.login_url ? `<a class="b" href="${esc(cfg.login_url)}">Entrar</a>` : ""}` : `<span class="mono">…</span>`);
      const b = contenedor.querySelector("#b-salir"); if (b) b.onclick = salir;
      return;
    }
    // cabeceras: los controles se dibujan una vez; después solo se mantienen al día
    if (!contenedor.querySelector("#q-rol")) {
      contenedor.innerHTML = `<select id="q-rol" aria-label="Rol">${Object.entries(ROLES).map(([k, t]) => `<option value="${k}">${esc(t)}</option>`).join("")}</select> ` +
        `<input type="text" id="q-usuario" placeholder="tu nombre" aria-label="Tu nombre" maxlength="60" autocomplete="off">`;
      let reloj = null;
      const cambio = () => {
        ident.rol = contenedor.querySelector("#q-rol").value; ident.usuario = contenedor.querySelector("#q-usuario").value;
        escribir("localStorage", CLAVE_QUIEN, JSON.stringify(ident));
        yo = null; lista = false; contenedor.dataset.listo = "0";
        clearTimeout(reloj); reloj = setTimeout(refrescar, 150); // al teclear, una pregunta al terminar y no una por letra
      };
      contenedor.querySelector("#q-rol").onchange = cambio;
      contenedor.querySelector("#q-usuario").oninput = cambio;
    }
    const r = contenedor.querySelector("#q-rol"), u = contenedor.querySelector("#q-usuario");
    if (r.value !== ident.rol) r.value = ident.rol;
    if (u.value !== ident.usuario) u.value = ident.usuario;
  }

  function montar(elemento) { contenedor = elemento; pintar(); }
  const alCambiar = f => oyentes.push(f);

  // lo que la pantalla muestra en lugar de sí misma cuando no se puede ni empezar
  function pantallaDeEntrada(caja) {
    const boton = "display:inline-block;padding:6px 16px;border-radius:4px;background:var(--acento);color:#fff;text-decoration:none;font-weight:500";
    caja.innerHTML = `<h1 style="font-size:1.6rem;font-weight:600;margin:0 0 4px">Falta iniciar sesión</h1>` +
      `<p style="margin:0 0 14px;color:var(--muted);max-width:60ch">Este sistema pide saber quién eres. ${cfg.login_url ? `Entra con tu cuenta y vuelve aquí.` : `Entra con tu proveedor de identidad y vuelve a esta dirección.`}</p>` +
      (cfg.login_url ? `<a href="${esc(cfg.login_url)}" style="${boton}">Entrar</a>` : "");
  }

  return { iniciar, llamar, refrescar, puede, describir, usuario, falta, esFaltaDeSesion, salir, montar, alCambiar, pantallaDeEntrada, nombreDeRol, modo, listo: () => espera };
})();
