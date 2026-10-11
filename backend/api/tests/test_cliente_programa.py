"""
El cliente generado (`frontend/gantt/cliente_programa.js`) contra la API de verdad.

Dos cosas: que el archivo es el que da el spec de hoy (D-55: el cliente no se edita a mano) y que, ejecutado en
node contra un servidor que atiende de verdad, ve, propone, aplica y deshace con los programas reales, y que los
errores llegan con su código. Se salta si no hay `node` (el CI de GitHub lo trae).
"""
import json
import shutil
import subprocess
import unittest
from decimal import Decimal

from api.generar_cliente import DESTINO, generar, spec_de_la_api
from api.tests.servidor import ServidorDePrueba
from core.catalogo import ServicioCarga
from core.tests.contrato_programa import CAL, programa
from core.tests.datos_opus import CONCEPTOS, PRESUPUESTO, reescalar_costo, texto

SCRIPT = r"""
const C = require(process.argv[1]);
C.base = process.argv[2];
const pid = +process.argv[3];
const CO = { "x-rol": "control_de_obra", "x-usuario": "luis" };
const f = JSON.parse(process.argv[4]);
(async () => {
  const sal = {};
  const v = await C.ver_programa({ programa_id: pid });
  sal.version0 = v.version; sal.partidas = v.vista.red.partidas.length;
  const ed = { edicion: "agregar_vinculo", predecesora: f.a, sucesora: f.b, tipo: "FS", desfase: "1" };
  const p = await C.proponer_edicion({ programa_id: pid, cuerpo: { edicion: ed }, ...CO });
  sal.propuesta = [p.aplicable, p.impacto.dias_de_cambio, p.version];
  sal.bitacoraTrasProponer = (await C.ver_bitacora({ programa_id: pid })).length;
  const a = await C.aplicar_edicion({ programa_id: pid, cuerpo: { edicion: ed, esperaba: 0 }, ...CO });
  sal.aplicada = [a.guardada.secuencia, a.guardada.usuario, a.version];
  try { await C.aplicar_edicion({ programa_id: pid, cuerpo: { edicion: { edicion: "fijar_inicio", llave: f.b, fecha: "2025-10-28" }, esperaba: 0 }, "x-rol": "residente", "x-usuario": "ana" }); }
  catch (e) { sal.viejo = [e instanceof C.ErrorApi, e.status, e.codigo]; }
  try { await C.aplicar_edicion({ programa_id: pid, cuerpo: { edicion: { edicion: "fijar_inicio", llave: f.b, fecha: "2025-10-28" } }, "x-rol": "control_de_obra", "x-usuario": "luis" }); }
  catch (e) { sal.permiso = [e.status, e.codigo]; }
  try { await C.ver_programa({ programa_id: 9999 }); } catch (e) { sal.noExiste = [e.status, e.codigo]; }
  try { await C.proponer_edicion({ programa_id: pid, cuerpo: { edicion: ed } }); } catch (e) { sal.sinIdentidad = [e.status, e.codigo]; }
  try { await C.proponer_edicion({ programa_id: pid, cuerpo: { edicion: { edicion: "no existe" } }, ...CO }); } catch (e) { sal.invalida = [e.status, e.codigo]; }
  const d = await C.deshacer_edicion({ programa_id: pid, edicion_id: a.guardada.id, ...CO });
  sal.deshecha = [d.guardadas.map(g => g.estado), d.version];
  sal.html = (await C.pantalla_gantt({ programa_id: pid })).includes("ClientePrograma");
  process.stdout.write(JSON.stringify(sal));
})().catch(e => { process.stderr.write(String(e && e.stack || e)); process.exit(1); });
"""


class PruebasClienteGenerado(unittest.TestCase):
    def test_el_cliente_publicado_es_el_que_da_el_spec_de_hoy(self):
        self.assertEqual(DESTINO.read_text(encoding="utf-8"), generar(spec_de_la_api()), "corre: cd backend && python3 -m api.generar_cliente")

    def test_hay_una_funcion_por_operacion(self):
        spec = spec_de_la_api()
        ids = {op["operationId"] for metodos in spec["paths"].values() for op in metodos.values()}
        texto = DESTINO.read_text(encoding="utf-8")
        for i in ids:
            self.assertIn(f"cliente.{i} = ", texto)


@unittest.skipUnless(shutil.which("node"), "no hay node")
class PruebasClienteContraLaApi(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.servidor = ServidorDePrueba().arrancar()
        cls.plus = programa("Zafiro Plus")
        cls.pid = cls.servidor.repo.importar_programa("Zafiro Plus", cls.plus, CAL)

    @classmethod
    def tearDownClass(cls):
        cls.servidor.apagar()

    def test_ve_propone_aplica_y_deshace_y_los_errores_llegan_con_su_codigo(self):
        f = {x.fila: x.llave for x in self.plus.filas}
        r = subprocess.run(
            ["node", "-e", SCRIPT, str(DESTINO), self.servidor.url, str(self.pid), json.dumps({"a": f[978], "b": f[1102]})],
            capture_output=True, text=True, timeout=120,
        )
        self.assertEqual(r.returncode, 0, r.stderr)
        s = json.loads(r.stdout)
        self.assertEqual((s["version0"], s["partidas"]), (0, 388))
        self.assertEqual(s["propuesta"], [True, 10, 0])  # proponer no sube la versión
        self.assertEqual(s["bitacoraTrasProponer"], 0)
        self.assertEqual(s["aplicada"], [1, "luis", 1])
        self.assertEqual(s["viejo"], [True, 409, "conflicto"])  # esperaba la versión 0 y ya va en la 1
        self.assertEqual(s["permiso"], [403, "permiso_denegado"])
        self.assertEqual(s["noExiste"], [404, "programa_inexistente"])
        self.assertEqual(s["sinIdentidad"], [401, "sin_identidad"])
        self.assertEqual(s["invalida"], [422, "edicion_invalida"])
        self.assertEqual(s["deshecha"], [["revertida"], 2])
        self.assertTrue(s["html"])


SCRIPT_CATALOGO = r"""
const C = require(process.argv[1]);
C.base = process.argv[2];
const CO = { "x-rol": "control_de_obra", "x-usuario": "luis@obra.mx" };
const RES = { "x-rol": "residente", "x-usuario": "ana@obra.mx" };
const bloque = "CAS-00004#1/NIV-00001#1";
(async () => {
  const sal = {};
  const lista = await C.listar_presupuestos({});
  sal.lista = [lista.length, lista[0].clave];
  const pid = lista[0].id;
  const pr = await C.ver_presupuesto({ presupuesto_id: pid });
  sal.total = [pr.renglones.length, pr.total];
  const p = await C.proponer_contratacion({ presupuesto_id: pid, cuerpo: { bloque }, ...CO });
  sal.propuesta = [p.aplicable, p.renglones, p.total_antes, p.total_despues, p.diferencia];
  sal.contratadosAntes = (await C.ver_contratados({ presupuesto_id: pid })).length;
  const c = await C.contratar_subarbol({ presupuesto_id: pid, cuerpo: { bloque }, ...CO });
  sal.contratada = [c.versiones_nuevas, c.renglones_fijados];
  try { await C.contratar_subarbol({ presupuesto_id: pid, cuerpo: { bloque }, ...CO }); } catch (e) { sal.repetida = [e instanceof C.ErrorApi, e.status, e.codigo]; }
  try { await C.contratar_subarbol({ presupuesto_id: pid, cuerpo: { bloque }, ...RES }); } catch (e) { sal.permiso = [e.status, e.codigo]; }
  try { await C.ver_presupuesto({ presupuesto_id: 9999 }); } catch (e) { sal.noExiste = [e.status, e.codigo]; }
  try { await C.ver_nodo({ clave: "NOEXISTE" }); } catch (e) { sal.sinNodo = [e.status, e.codigo]; }
  try { await C.proponer_carga({ cuerpo: { conceptos: "esto,no,es,un,archivo\n1,2,3,4,5\n" }, ...CO }); } catch (e) { sal.archivo = [e.status, e.codigo]; }
  try { await C.proponer_carga({ cuerpo: { conceptos: "x" } }); } catch (e) { sal.sinIdentidad = [e.status, e.codigo]; }
  const cl = await C.proponer_clonacion({ cuerpo: { original: "AUX-00001", clave: "PRE-00120" }, ...CO });
  sal.clonacion = [cl.aplicable, cl.redirigidos.length, cl.renglones];
  const hecha = await C.clonar_insumo({ cuerpo: { original: "AUX-00001", clave: "PRE-00120" }, ...CO });
  sal.clonada = [hecha.versiones_nuevas, hecha.renglones_fijados];
  const nodo = await C.ver_nodo({ clave: "AUX-00001" });
  sal.nodo = [nodo.sustituido_por, nodo.citado_por.length];
  sal.clones = (await C.listar_clones({})).map(x => [x.original, x.clon, x.usuario]);
  sal.cargas = (await C.listar_cargas({})).map(x => x.tipo);
  const prec = await C.ver_precios({ clave: "ACE-00001" });
  sal.precio = prec[0].precio;
  process.stdout.write(JSON.stringify(sal));
})().catch(e => { process.stderr.write(String(e && e.stack || e)); process.exit(1); });
"""


@unittest.skipUnless(shutil.which("node"), "no hay node")
class PruebasClienteDelCatalogo(unittest.TestCase):
    """Las operaciones del catálogo (D-482) por el cliente generado, contra un servidor que atiende de verdad."""

    @classmethod
    def setUpClass(cls):
        cls.servidor = ServidorDePrueba().arrancar()
        carga = ServicioCarga(cls.servidor.catalogo)
        carga.aplicar(texto(CONCEPTOS), texto(PRESUPUESTO), None, rol="costos", usuario="ana@obra.mx")
        # y el acero sube 2 %: los renglones siguen con el PU de su versión; contratar los fija a hoy
        carga.aplicar(reescalar_costo(texto(CONCEPTOS), "ACE-00001", Decimal("1.02")), texto(PRESUPUESTO), None, rol="costos", usuario="ana@obra.mx")

    @classmethod
    def tearDownClass(cls):
        cls.servidor.apagar()

    def test_ve_contrata_y_clona_y_los_errores_llegan_con_su_codigo(self):
        r = subprocess.run(["node", "-e", SCRIPT_CATALOGO, str(DESTINO), self.servidor.url], capture_output=True, text=True, timeout=300)
        self.assertEqual(r.returncode, 0, r.stderr)
        s = json.loads(r.stdout)
        self.assertEqual(s["lista"], [7, "CAS-00004"])
        self.assertEqual(s["total"], [398, "1842426.01"])
        self.assertEqual(s["propuesta"], [True, 56, "178768.69", "178809.66", "40.97"])
        self.assertEqual((s["contratadosAntes"], s["contratada"]), (0, [25, 25]))
        self.assertEqual(s["repetida"], [True, 409, "ya_contratado"])
        self.assertEqual(s["permiso"], [403, "permiso_denegado"])
        self.assertEqual(s["noExiste"], [404, "presupuesto_inexistente"])
        self.assertEqual(s["sinNodo"], [404, "nodo_inexistente"])
        self.assertEqual(s["archivo"], [422, "carga_no_procede"])
        self.assertEqual(s["sinIdentidad"], [401, "sin_identidad"])
        self.assertEqual(s["clonacion"], [True, 9, 9])
        self.assertEqual(s["clonada"], [9, 9])
        self.assertEqual(s["nodo"], ["PRE-00120", 0])
        self.assertEqual(s["clones"], [["AUX-00001", "PRE-00120", "luis@obra.mx"]])
        self.assertEqual(s["cargas"], ["archivos", "archivos", "contratacion", "clonacion"])
        self.assertEqual(s["precio"], "24.68")


SCRIPT_TOKEN = r"""
const C = require(process.argv[1]);
C.base = process.argv[2];
const token = process.argv[3];
(async () => {
  const sal = {};
  try { await C.quien_soy({}); } catch (e) { sal.sinToken = [e.status, e.codigo, e.detalle.login_url]; }
  C.token = "basura";
  try { await C.listar_programas({}); } catch (e) { sal.malo = [e.status, e.codigo]; }
  C.token = token;
  const yo = await C.quien_soy({});
  sal.yo = [yo.usuario, yo.roles, yo.funciones, yo.modo];
  sal.lista = (await C.listar_programas({})).length;
  C.token = null;  // las pantallas no mandan token: no hay a quien mandárselo
  try { await C.listar_programas({}); } catch (e) { sal.sinTokenOtraVez = e.status; }
  sal.pantalla = (await C.pantalla_programas({})).includes("const CFG");  // las pantallas se abren sin token
  process.stdout.write(JSON.stringify(sal));
})().catch(e => { process.stderr.write(String(e && e.stack || e)); process.exit(1); });
"""


@unittest.skipUnless(shutil.which("node"), "no hay node")
class PruebasClienteConToken(unittest.TestCase):
    """El cliente manda `Authorization: Bearer` en las operaciones que el spec declara protegidas, y solo si tiene un token."""

    @classmethod
    def setUpClass(cls):
        cls.servidor = ServidorDePrueba("token").arrancar()
        cls.servidor.repo.importar_programa("Zafiro Plus", programa("Zafiro Plus"), CAL)

    @classmethod
    def tearDownClass(cls):
        cls.servidor.apagar()

    def test_el_token_va_en_las_operaciones_protegidas(self):
        r = subprocess.run(["node", "-e", SCRIPT_TOKEN, str(DESTINO), self.servidor.url, self.servidor.token("luis@obra.mx")],
                           capture_output=True, text=True, timeout=120)
        self.assertEqual(r.returncode, 0, r.stderr)
        s = json.loads(r.stdout)
        self.assertEqual(s["sinToken"], [401, "sin_token", "https://proveedor.example/entrar"])
        self.assertEqual(s["malo"], [401, "token_invalido"])
        self.assertEqual(s["yo"], ["luis@obra.mx", ["control_de_obra"], ["cargar_catalogo_opus", "clonar_insumo", "contratar_subarbol", "editar_estructura_programa"], "token"])
        self.assertEqual((s["lista"], s["sinTokenOtraVez"], s["pantalla"]), (1, 401, True))


if __name__ == "__main__":
    unittest.main()
