// Reprogramación por empuje mínimo, en el navegador. Es el mismo contrato que `reprogramar` de
// backend/core/programa.py (PROGRAMA-CPM.md §4.5 y §8): cada partida conserva su arranque y solo se corre lo
// que una duración, un vínculo o una fecha editada obliga. Los días son índices de días hábiles (red.dias).
const Motor = (() => {
  const TIPOS = ["FS", "SS", "FF", "SF"];

  function indiceDeFecha(dias, iso) { // el primer día hábil igual o posterior: `siguiente_habil`
    let lo = 0, hi = dias.length - 1;
    if (iso <= dias[0]) return 0;
    while (lo < hi) { const m = (lo + hi) >> 1; if (dias[m] >= iso) hi = m; else lo = m + 1; }
    return lo;
  }

  function holgura(tipo, L, pAbre, pCierra, sAbre, sCierra) {
    if (tipo === "FS") return sAbre - (pCierra + L);
    if (tipo === "SS") return sAbre - (pAbre + L);
    if (tipo === "FF") return sCierra - (pCierra + L);
    return sCierra - (pAbre + L);
  }

  function ventanaDeBloque(red, win, b, excluir) {
    const hs = (red.bloques[b] || []).filter(h => h !== excluir && win[h]);
    if (!hs.length) return null;
    return [Math.min(...hs.map(h => win[h][0])), Math.max(...hs.map(h => win[h][1]))];
  }

  function referencias(red, win, v) {
    if (!red.bloques[v.de]) return [v.de];
    let hs = red.bloques[v.de].filter(h => h !== v.a && win[h]);
    if (!hs.length) hs = red.bloques[v.de].filter(h => win[h]);
    if (v.tipo === "FS" || v.tipo === "FF") { const t = Math.max(...hs.map(h => win[h][1])); return hs.filter(h => win[h][1] === t); }
    const p = Math.min(...hs.map(h => win[h][0])); return hs.filter(h => win[h][0] === p);
  }

  // una sola referencia para dibujar la flecha, como `Programa.referencia`
  function referencia(red, win, v, preferidas, orden) {
    const emp = referencias(red, win, v);
    for (const h of emp) if (preferidas.has(h)) return h;
    if (v.tipo === "FS" || v.tipo === "FF") return emp.reduce((a, b) => (win[b][0] > win[a][0] || (win[b][0] === win[a][0] && orden[b] < orden[a])) ? b : a);
    return emp.reduce((a, b) => orden[b] < orden[a] ? b : a);
  }

  function cadenaDeRelevos(red, win, vinculos) {
    const entrantes = new Map();
    for (const v of vinculos) {
      if (!win[v.a]) continue;
      const p = red.bloques[v.de] ? ventanaDeBloque(red, win, v.de, v.a) : win[v.de];
      if (!p) continue;
      if (holgura(v.tipo, v.desfase, p[0], p[1] + 1, win[v.a][0], win[v.a][1] + 1) !== 0) continue;
      for (const r of referencias(red, win, v)) if (r !== v.a) { if (!entrantes.has(v.a)) entrantes.set(v.a, []); entrantes.get(v.a).push(r); }
    }
    const memo = new Map(), visitando = new Set();
    const mejor = n => {
      if (memo.has(n)) return memo.get(n);
      if (visitando.has(n)) return [n];
      visitando.add(n);
      let cola = [n];
      for (const p of (entrantes.get(n) || [])) {
        const c = mejor(p).concat([n]);
        if (c.length > cola.length || (c.length === cola.length && -win[c[0]][0] > -win[cola[0]][0])) cola = c;
      }
      visitando.delete(n);
      memo.set(n, cola);
      return cola;
    };
    const llaves = red.partidas.map(p => p.k);
    const fin = Math.max(...llaves.map(k => win[k][1]));
    let mejorC = null;
    for (const n of llaves.filter(k => win[k][1] === fin)) {
      const c = mejor(n);
      if (mejorC === null || c.length > mejorC.length || (c.length === mejorC.length && -win[c[0]][0] > -win[mejorC[0]][0])) mejorC = c;
    }
    return mejorC;
  }

  // ¿hay un ciclo entre partidas? (DFS con colores sobre los vínculos directos)
  function cicloDirecto(red, vinculos) {
    const par = new Set(red.partidas.map(p => p.k));
    const sig = new Map();
    for (const v of vinculos) if (par.has(v.de) && par.has(v.a)) { if (!sig.has(v.de)) sig.set(v.de, []); sig.get(v.de).push(v.a); }
    const color = new Map();
    const visita = n => {
      color.set(n, 1);
      for (const m of (sig.get(n) || [])) {
        if (color.get(m) === 1) return true;
        if (!color.has(m) && visita(m)) return true;
      }
      color.set(n, 2);
      return false;
    };
    for (const n of sig.keys()) if (!color.has(n) && visita(n)) return true;
    return false;
  }

  // el arranque más temprano que respeta anclas, duraciones y vínculos; null si no converge (ciclo que se alarga)
  function empujar(red, D, anclas, vinculos) {
    const ks = red.partidas.map(p => p.k);
    const ES = {};
    for (const k of ks) ES[k] = Math.max(0, anclas[k] === undefined ? 0 : anclas[k]);
    const ent = {};
    for (const v of vinculos) {
      if (!ES.hasOwnProperty(v.a)) continue;
      let orig;
      if (red.bloques[v.de]) { orig = red.bloques[v.de].filter(h => h !== v.a && ES.hasOwnProperty(h)); if (!orig.length) continue; }
      else orig = [v.de];
      (ent[v.a] = ent[v.a] || []).push([orig, v]);
    }
    for (let pasada = 0; pasada < ks.length + 5; pasada++) {
      let cambio = false;
      for (const s of ks) {
        let piso = ES[s];
        for (const [orig, v] of (ent[s] || [])) {
          const pAbre = Math.min(...orig.map(o => ES[o])), pCierra = Math.max(...orig.map(o => ES[o] + D[o]));
          const c = v.tipo === "FS" ? pCierra + v.desfase : v.tipo === "SS" ? pAbre + v.desfase : v.tipo === "FF" ? pCierra + v.desfase - D[s] : pAbre + v.desfase - D[s];
          if (c > piso) piso = c;
        }
        if (piso > ES[s]) { ES[s] = piso; cambio = true; }
      }
      if (!cambio) return ES;
    }
    return null;
  }

  // ediciones: {t:'dur',k,dias} · {t:'ini',k,fecha} · {t:'add',de,a,tipo,desfase} · {t:'del',de,a,tipo|null} · {t:'chg',de,a,tipoActual,tipo,desfase}
  function reprogramar(red, ediciones, modo) {
    modo = modo || "empuje";
    const win0 = {}; const D = {}; const anclas = {};
    for (const p of red.partidas) { win0[p.k] = [p.ini, p.fin]; D[p.k] = p.fin - p.ini + 1; if (modo === "empuje") anclas[p.k] = p.ini; }
    const conocidas = new Set(red.conocidas); const esPartida = new Set(red.partidas.map(p => p.k));
    let vivos = red.vinculos.map(v => Object.assign({}, v));
    const rechazadas = [];
    const iguales = (a, b) => a.de === b.de && a.a === b.a && a.tipo === b.tipo && a.desfase === b.desfase;
    const valido = (de, a) => {
      if (!esPartida.has(a)) return conocidas.has(a) ? "sucesora_no_es_partida" : "actividad_desconocida";
      if (esPartida.has(de) || (red.bloques[de] && red.bloques[de].length)) return null;
      return conocidas.has(de) ? "predecesora_sin_partidas" : "actividad_desconocida";
    };
    const cierraCiclo = lista => cicloDirecto(red, lista) || empujar(red, D, anclas, lista) === null;
    for (const e of ediciones) {
      if (e.t === "dur") {
        if (!esPartida.has(e.k)) rechazadas.push("actividad_desconocida");
        else if (!(e.dias > 0)) rechazadas.push("duracion_invalida");
        else D[e.k] = e.dias;
      } else if (e.t === "ini") {
        if (!esPartida.has(e.k)) rechazadas.push("actividad_desconocida");
        else anclas[e.k] = indiceDeFecha(red.dias, e.fecha);
      } else if (e.t === "add") {
        const m = valido(e.de, e.a);
        const nuevo = { de: e.de, a: e.a, tipo: e.tipo, desfase: e.desfase || 0 };
        if (m) rechazadas.push(m);
        else if (e.de === e.a) rechazadas.push("autovinculo");
        else if (vivos.some(v => iguales(v, nuevo))) rechazadas.push("repetido");
        else if (cierraCiclo(vivos.concat([nuevo]))) rechazadas.push("cierra_un_ciclo");
        else vivos.push(nuevo);
      } else if (e.t === "del") {
        const quedan = vivos.filter(v => !(v.de === e.de && v.a === e.a && (e.tipo == null || v.tipo === e.tipo)));
        if (quedan.length === vivos.length) rechazadas.push("vinculo_inexistente");
        vivos = quedan;
      } else if (e.t === "chg") {
        const i = vivos.findIndex(v => v.de === e.de && v.a === e.a && v.tipo === e.tipoActual);
        if (i < 0) { rechazadas.push("vinculo_inexistente"); continue; }
        const nuevo = { de: e.de, a: e.a, tipo: e.tipo, desfase: e.desfase || 0 };
        const resto = vivos.slice(0, i).concat(vivos.slice(i + 1));
        if (resto.some(v => iguales(v, nuevo))) rechazadas.push("repetido");
        else if (cierraCiclo(resto.concat([nuevo]))) rechazadas.push("cierra_un_ciclo");
        else vivos = resto.slice(0, i).concat([nuevo], resto.slice(i));
      }
    }
    const ES = empujar(red, D, anclas, vivos);
    const win = {};
    for (const p of red.partidas) win[p.k] = [ES[p.k], ES[p.k] + D[p.k] - 1];
    const movidas = {};
    let nMov = 0;
    for (const p of red.partidas) {
      const di = win[p.k][0] - win0[p.k][0], df = win[p.k][1] - win0[p.k][1];
      if (di || df) { movidas[p.k] = [di, df]; nMov++; }
    }
    const finAntes = Math.max(...red.partidas.map(p => p.fin)), finDespues = Math.max(...red.partidas.map(p => win[p.k][1]));
    const antes = cadenaDeRelevos(red, win0, red.vinculos), despues = cadenaDeRelevos(red, win, vivos);
    const a = new Set(antes), b = new Set(despues);
    return {
      win, vinculos: vivos, movidas, nMovidas: nMov, finAntes, finDespues, diasDeCambio: finDespues - finAntes,
      rutaAntes: antes, rutaDespues: despues, rutaCambia: a.size !== b.size || [...a].some(x => !b.has(x)), rechazadas, D, anclas,
    };
  }

  return { reprogramar, cadenaDeRelevos, referencia, referencias, ventanaDeBloque, holgura, indiceDeFecha, TIPOS };
})();
if (typeof module !== "undefined" && module.exports) module.exports = Motor;
