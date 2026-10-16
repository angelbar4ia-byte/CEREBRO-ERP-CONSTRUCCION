# WORKFLOWS

```
órgano:     comisuras — conectan los circuitos
capa:       II — Operación
pregunta:   ¿cómo trabajan juntos las personas, el sistema, el agente interno y las skills?
tiempo:     se hace así
corte:      2026-10-16
verificado: mapa derivado de lo decidido en MODELO, CONOCIMIENTO, gravity-obra y ESCALABILIDAD y de lo construido hasta D-485 · tres propuestas sin confirmar (D-484), construidas en la bandeja (D-485) · §8, el flujo de la app, armado en D-529 con lo decidido hasta D-528
```

> **Este archivo no define reglas del dominio.** Junta lo que ya está dicho en cuatro lugares para que se vea cómo
> se conecta: quién puede qué vive en `MODELO.md` §5b; la bandeja de propuestas, en `CONOCIMIENTO.md` §14; el agente
> interno, en `gravity-obra.md`; las superficies, en `ESCALABILIDAD.md` §4; los skills, en `ESCALABILIDAD.md` §9. Lo que aporta son **las
> relaciones entre ellos** y los huecos que aparecen al juntarlos (§7).
>
> Si un hecho cambia en su lugar, este archivo se corrige; no al revés.

---

# 1. Quién trabaja

```
 PERSONA ── token ──► API ──► SERVICIOS ──► base          la persona decide; el sistema escribe
   ▲  (usuario, roles,    │        │
   │   funciones)         │        └─ bitácora: quién, con qué rol, cuándo
   │ resuelve             │ lee · simula
   │                      │
 BANDEJA ◄── propone ── AGENTE INTERNO          sus herramientas son el modelo de datos
 (PROPUESTA · ALERTA)      detecta y explica     no escribe: deja la propuesta y espera

 SKILLS ── compiladas de CONOCIMIENTO ──► agentes de desarrollo ──► construyen todo lo de arriba
```

| Quién | Qué hace | Qué no hace nunca | De dónde sale su autoridad | Estado |
|---|---|---|---|---|
| **La persona** | Decide, aprueba, carga, contrata, clona, edita | Aprobar lo que ella misma originó (D-269) | Sus roles → las funciones de `ROL_FUNCION`; y qué obras ve, por la jerarquía | Roles y funciones, construidos (D-469); el alcance por obra, no (B-98) |
| **El sistema** (servicios y API) | Calcula, valida, escribe todo o nada, deja la bitácora | Escribir sin una persona con la función | Comprueba la función **de quien llama**, en cada acción, leyendo la tabla de hoy | Construido para programa, catálogo, presupuesto, colgado, contratación, clonación (D-461 a D-482) y la bandeja (D-485) |
| **El agente interno** (Gravity) | Lee, detecta, explica, simula y propone | Escribir, calcular dinero, aprobar lo suyo, reabrir lo rechazado sin evidencia nueva | **Ninguna propia**: lo que propone solo se aplica si una persona con la función lo aprueba | Diseñado, fase 2 (`gravity-obra.md`); la bandeja donde deja sus propuestas ya existe (D-485) |
| **Las skills y los agentes de desarrollo** | Hacen que quien construye el sistema no repita errores ya pagados | Tocar datos del producto | Ninguna: son conocimiento compilado, no actores del producto | Seis skills y cinco agentes escritos (y `gravity-obra`, diseñado) |

---

# 2. Las personas y los sistemas en que trabajan

## 2.1 Los sistemas

| Sistema | Papel | Cómo se relaciona con las personas |
|---|---|---|
| **OPUS 2025** | Fuente, nunca destino (`CONOCIMIENTO.md` §11.3) | Quien carga sus exportaciones —Costos y Control de obra, función `cargar_catalogo_opus`— lo hace por archivo; nada corregido vuelve a OPUS |
| **ERP externo** | Destino de las ingenierías, fuente de las salidas de almacén y de estimaciones (`ESTIMACION.fuente = erp_externo`) | Entra por archivo; la estimación la valida Control de obra (`validar_estimacion`) |
| **El ERP propio** (este) | Donde se decide y queda registrado quién decidió | Las personas trabajan en él por pantalla (hoy solo el programa), por API o por terminal |
| **El proveedor de identidad** (Supabase Auth) | Dice **quién eres** (el correo) | No dice qué puedes hacer: eso lo decide `ROL_FUNCION` (B-96, D-470) |

## 2.2 Los roles y lo que hacen

Derivado de la tabla de `MODELO.md` §5b; no agrega ninguna asignación.

| Rol | Ve | Hace (funciones asignadas) |
|---|---|---|
| **Residente** | Sus obras (`RESIDENTE_OBRA`) | `trazar` · `anotar_plano` · `originar_incidencia` · `ejecutar_incidencia` · `solicitar_cierre_frente` · `editar_fechas_programa` |
| **Supervisor** | Las de los residentes que supervisa (`SUPERVISION`) | `trazar` · `anotar_plano` · `originar_incidencia` · `aprobar_incidencia` · `cerrar_incidencia` · `aprobar_cierre_frente` · `resolver_alerta` (propuesta, D-485) |
| **Superintendente** | Las de los supervisores que le reportan | Solo `aprobar_precio_nuevo`, junto con Control de obra. §5b dice «mismos privilegios que Supervisor», pero la tabla no lo escribe (§7, hueco 2) |
| **Costos** | Todas | `trazar` · `proponer_precio_nuevo` · `cargar_catalogo_opus` (propuesta) |
| **Cotizador** | No es un rol activo | Hoy lo ejecuta Control de obra |
| **Control de obra** | Todas | `trazar` · `aprobar_trazo` · `originar_incidencia` · `validar_incidencia` · `validar_cierre_frente` · `validar_estimacion` · `editar_estructura_programa` (también subir un programa) · `aprobar_precio_nuevo` · `cargar_catalogo_opus` · `contratar_subarbol` · `clonar_insumo` · `aprobar_propuesta` y `resolver_alerta` (propuestas, D-485) · y el gobierno entre obras: `gestionar_rol_funcion` · `asignar_residente` · `asignar_supervision` · `renovar_invariante_valor` · `reclasificar_familia` · `resolver_revisar_parametro` |

**Lo que se ve de un vistazo:** el trabajo de obra se reparte en cadena —Residente ejecuta y pide, Supervisor aprueba
y cierra, Control de obra valida— y **el gobierno cruzado entre obras cae en Control de obra** (diecinueve de las
veintisiete funciones asignadas). Diez funciones existen sin dueño (§7, hueco 1): entre ellas `registrar_avance`, la que
alimenta las alertas de frente y de atraso.

## 2.3 Los módulos, y qué tan hechos están

| Módulo | Qué hacen las personas ahí | Patrón (§3) | En código |
|---|---|---|---|
| **Catálogo y presupuesto** | Cargar los archivos de OPUS, decidir lo detenido y las bajas, reconciliar | 1 | ✅ Servicios, API (D-482) y terminal |
| **Colgado, contratación, clonación** | Colgar un programa, contratar un bloque, clonar un insumo o corregir un prefijo | 1 | ✅ Igual |
| **Programa** | Subir, subir la versión nueva, editar estructura o fechas, deshacer | 1 | ✅ Servicios, API y pantalla |
| **Cuantificación** | Trazar sobre el plano; aprobar el trazo | 2 | Diseñado |
| **Incidencias** | Originar → aprobar → validar → ejecutar → cerrar | 2 | Diseñado |
| **Cierre de frente** | Solicitar al 90 % → aprobar → validar | 2 | Diseñado |
| **Precios nuevos** | Costos propone; Control de obra y Superintendente aprueban | 3 | Diseñado |
| **Estimación** | Capturar, devolver, validar, pagar; con el cruce contra almacén antes del pago | 6 | Diseñado; las funciones de capturar y devolver no tienen clave |
| **Avance y almacén** | Registrar avance físico y pagado; leer surtido contra consumido | — | Diseñado; los datos reales están en `1-mundo/fuentes/` |
| **La bandeja** (`PROPUESTA`, `ALERTA`) | Dejar una propuesta con su evidencia; aprobarla (y el sistema la hace a nombre de quien aprueba) o rechazarla; cerrar las alertas | 4 y 5 | ✅ Servicio, API (D-485) y terminal; sin pantalla. Hoy solo se aprueba `clonacion`; ningún detector deja alertas todavía |
| **Consulta** | Preguntar en lenguaje natural | — | Diseñada; once herramientas definidas (`gravity-obra.md` §6) |

---

# 3. Las formas de flujo

El cerebro tiene seis formas de que algo pase de «alguien lo pidió» a «quedó hecho». Todas cumplen lo mismo: **el sistema
propone y el humano decide**; cambia cuántos pasos hay y quién da cada uno.

| # | Forma | Cómo va | Dónde se usa | Estado |
|---|---|---|---|---|
| 1 | **Propuesta y aplicación del sistema** | `…/propuestas` calcula qué pasaría y no escribe. La aplicación vuelve a revisar, comprueba la función de quien la pide y escribe todo o nada con su correo y su rol. `esperaba` ata lo aplicado a lo que se vio: si algo cambió en medio, 409 y no se escribe | Cargar, reconciliar, colgar, contratar, clonar, corregir un prefijo, editar el programa | ✅ (D-473 a D-482) |
| 2 | **Cadena de pasos con salto** | Originar → aprobar → validar → ejecutar → cerrar. Quien origina se salta su propio paso; el Supervisor da seguimiento hasta el cierre sin excepción (D-269) | Incidencia, cierre de frente, trazo | Diseñado |
| 3 | **Doble aprobación obligatoria** | Los dos aprueban, no uno de dos: el estado pasa a `aprobada` solo cuando están los dos | Precio nuevo | Diseñado |
| 4 | **Bandeja de propuestas** | Una persona o el agente deja una `PROPUESTA` con evidencia; otra persona la aprueba o la rechaza; el rechazo se conserva | Nueve tipos, más `precio_nuevo` (`CONOCIMIENTO.md` §14) | ✅ Construida (D-485); solo `clonacion` se puede aprobar |
| 5 | **Alerta** | Detectar no pide permiso; resolver sí. Una alerta no sugiere valor, solo señala; nunca se resuelve sola | Veinte alertas especificadas (`MODELO.md` §5a) | ✅ La bandeja las guarda y las cuenta (D-485); los detectores, sin construir |
| 6 | **Validación con cruce** | Capturada → devuelta → validada → pagada, y antes de pagar se cruza contra lo que salió de almacén | Estimación | Diseñado |

## 3.1 Las formas 1 y 4 son la misma acción vista desde dos lados

> **Una `PROPUESTA` es una intención guardada; la propuesta y aplicación del sistema es su ejecución.** Cuando una
> persona aprueba una propuesta del agente, lo que corre es la operación de la forma 1, **con la identidad y la función
> de quien aprueba**, nunca las del agente.

De ahí sale una regla que no hay que inventar porque el sistema ya la cumple: **aprobar una propuesta pide la misma
función que pediría hacer a mano lo que propone.** El agente no gana poder: una propuesta de clonar solo la puede
aprobar quien puede clonar.

| `tipo` de `PROPUESTA` | Operación que corre al aprobarla | Función que pide | Operación |
|---|---|---|---|
| `clonacion` | `POST /clonaciones` o `POST /correcciones-de-prefijo` | `clonar_insumo` | ✅ construida |
| `version` | La carga con `confirmados` (hoy la versión sola entra; un PU que se mueve más de 5 % pide confirmación) | `cargar_catalogo_opus` hoy; `aprobar_version_concepto` si se separa | ✅ en parte |
| `precio_nuevo` | Sin construir | `aprobar_precio_nuevo`, las dos firmas | Diseñada |
| `orden_cambio` | Sin construir | `autorizar_orden_cambio` (sin asignar) | Diseñada |
| `equivalencia` · `reparto` · `conversion` · `matriz_generada` · `fusion` · `patron_carga` | Sin construir | Sin función todavía | Diseñadas |

`aprobar_propuesta` es, con esta regla, **la función de resolver la bandeja** —aprobar o rechazar—, no de aplicar: aplicar
siempre pide la función de la acción, y por eso aprobar una clonación pide las dos. *Propuesta de D-484, construida así en
D-485 (`api/bandeja.py`); el usuario no la ha confirmado, y cambiar quién la tiene es una fila de `ROL_FUNCION`.*

---

# 4. El agente interno, paso a paso

## 4.1 Qué recibe

Quien pregunta llega con su sesión: el token da el usuario, `GET /yo` dice sus roles y lo que puede hacer, y de la
jerarquía sale qué obras ve. **Toda herramienta filtra por ese alcance** (`gravity-obra.md` §6), igual que lo haría la
pantalla. Hoy la API no filtra por obra (B-98): hasta que lo haga, **el agente solo se puede soltar con Control de obra
y Costos**, que ven todo, y no con Residente ni Supervisor.

## 4.2 Qué puede hacer: tres manos, ninguna que escriba

| Mano | Qué es | En la API de hoy | Qué garantiza |
|---|---|---|---|
| **Lee** | Resultados ya calculados | Las operaciones `listar_*` y `ver_*` | El agente no ve registros para recorrer, sino cifras: no puede equivocarse sumando |
| **Simula** | «¿Qué pasaría si…?» | Las operaciones `…/propuestas`: calculan, no escriben y piden la función de quien pregunta | Puede explicar una consecuencia antes de que nadie decida. Si quien pregunta no tiene la función, el 403 es la respuesta: «eso lo puede hacer Control de obra» |
| **Propone** | Deja una `PROPUESTA` o una `ALERTA` en la bandeja | El servicio ya acepta `origen=agente` (con su modelo); **la API todavía no lo deja entrar**: falta la credencial del agente (§7, hueco 6) | Es la única vía de entrada al sistema (`gravity-obra.md` §7) |

Las operaciones que **aplican** (`aplicar_*`, `colgar_programa`, `contratar_subarbol`, `clonar_insumo`, `corregir_prefijo`,
`aplicar_edicion`…) **no se le dan**. Cuando exista el MCP, «el agente no escribe» deja de ser una regla que alguien
respeta y pasa a ser estructural: no hay herramienta que escriba (`ESCALABILIDAD.md` §4.3).

## 4.3 Qué pasa con lo que encuentra

1. **Detecta** con consulta determinista siempre; con modelo solo donde el parecido de texto es el hallazgo (`gravity-obra.md` §4). El modelo redacta; la detección encuentra.
2. **Escala** según haya o no un dato concreto que cambiar: respuesta, alerta o propuesta (`gravity-obra.md` §3).
3. **Si propone, la evidencia es una simulación del sistema.** Para proponer corregir un prefijo, el agente llama a la mano que simula, y lo que vuelve —los pares, lo que cita cada uno, lo que impide hacerlo— **es** el `valor_propuesto` y la `evidencia`. Su `base` (la última carga que vio) viaja con la propuesta.
4. **Una persona resuelve.** Quien aprueba lo hace con su función (§3.1). La aplicación manda `esperaba = base`: si entre la propuesta y la aprobación alguien cargó, contrató o clonó algo, **no se aplica y se vuelve a simular** — el agente no puede hacer que la persona apruebe algo distinto de lo que vio.
5. **Queda dicho quién decidió.** La bitácora del servicio trae el correo y el rol de quien aprobó; la propuesta, el modelo que la produjo. Un rechazo se conserva y no se vuelve a proponer sin evidencia nueva.

## 4.4 Lo que no se negocia

No calcula dinero · no escribe · no aprueba sus propuestas · no presenta una estimación como dato (supuestos a la vista,
siempre) · no reabre lo rechazado · toda respuesta declara su fecha de corte. Están en `gravity-obra.md` §7 y
`RAZONAMIENTO.md` §1 a §3; aquí solo se enlazan.

**Cómo se sabe si sirve:** la tasa de rechazo **por nivel de confianza**. Si lo marcado alto se rechaza tanto como lo
marcado bajo, la confianza no significa nada (`gravity-obra.md` §5).

---

# 5. Cómo resuelven las skills

## 5.1 Qué son, y qué no

Una skill es **conocimiento compilado** de `CONOCIMIENTO.md`, no escrito a mano: una base (`erp-construccion`, se carga
siempre) y satélites que se disparan por su descripción (`erp-importacion`, `erp-rediseno`, `erp-parametrico`,
`erp-cuantificador`, `erp-programa`). **Nunca introduce un hecho que no esté en el conocimiento** (`ESCALABILIDAD.md` §9): por eso,
cuando cambia la sección de la que sale, hay que recompilarla —D-480 encontró cuatro viejas—.

Dos cosas que conviene tener claras:

- **Las skills son para quien construye, no para el producto.** Un agente interno corriendo en un modelo chico (Llama
  3.1 8B, `gravity-obra.md` §0) no cargaría un skill de seiscientas líneas. Lo que hace de skill dentro del producto
  son **tres cosas**: las consultas deterministas de los detectores, el servicio que ya lleva la regla y la descripción de
  cada herramienta. Las tres se escriben contra la misma fuente —`CONOCIMIENTO.md`—; la tercera es la que el modelo lee
  para elegir y la que más fácil se desactualiza (`ESCALABILIDAD.md` §4.4).
- **Hoy se cargan a mano.** Los skills y los agentes viven como archivos en `2-operacion/`; el `.claude/` del repo está
  vacío, así que Claude Code no los carga solo.

## 5.2 Cómo se resuelve una petición

| Petición | Quién la resuelve | Con qué | Quién decide |
|---|---|---|---|
| «Carga el export de OPUS» | La persona con `cargar_catalogo_opus`, por la API | `proponer_carga` → `aplicar_carga`. La regla está en el servicio; el skill `erp-importacion` es para quien la modifica | La persona, con `esperaba` |
| «¿Cuánto cemento falta para la cimentación?» | El agente de Consulta | Una herramienta que pregunta al motor. Ningún skill | Nadie: solo lee |
| «Estas dos claves parecen la misma» | Un detector del agente | Consulta determinista + redacción del modelo → `PROPUESTA(equivalencia)` | Quien tenga la función de aprobarla |
| «Corrige el prefijo `AUX-`» | La persona con `clonar_insumo`, o el agente si lo detecta | `proponer_correccion_de_prefijo` → `corregir_prefijo`; la regla está en `erp-rediseno` | La persona |
| «Construye el módulo de estimaciones» | `gravity` arma el plan; la sesión lo ejecuta | arquitecto → constructor → auditor; skill base. **No hay skill de estimaciones** (sus reglas no están decididas) | El humano, en cada `BLOQUEA` |

## 5.3 Cómo se encadenan los de desarrollo

`gravity` entrega **un plan de ruta, no una cadena ejecutada**: los agentes no se invocan entre sí, la sesión principal
ejecuta paso por paso y por eso hay un humano en cada salto. Cada uno cierra con el mismo bloque —`DE`, `PARA`, `HECHO`,
`EVIDENCIA`, `ABIERTO`, `BLOQUEA`— y si `BLOQUEA` trae algo, el plan se detiene ahí. El auditor cierra casi todos.
Es **la misma forma** que el agente interno (un router y detectores angostos, una sola salida, el humano al final) con
una diferencia: el interno deja propuestas en una bandeja, el externo deja un plan.

---

# 6. Cuatro recorridos

**a · Costos carga el export de OPUS** *(construido, sin pantalla)*. Costos manda los CSV a `proponer_carga` y recibe el
informe: qué entra, qué versiona, qué se detiene y por qué, qué programas citan lo que se da de baja. Decide: confirma lo
que se movió más de 5 % o las bajas que quiere. `aplicar_carga` con `esperaba` escribe todo o nada, y la carga queda con
su correo y el rol `costos`.

**b · Control de obra contrata un bloque** *(construido, sin pantalla)*. `proponer_contratacion` dice, concepto por
concepto, el PU que se fija y cuánto cambia el monto; lo que pide confirmación, no se contrata a medias. Al contratar, la
base congela el bloque. Lo que cambie después va por control de cambio (`orden_cambio`: diseñada, y
`autorizar_orden_cambio` sin dueño).

**c · Un frente llega al 90 %** *(diseñado)*. El sistema calcula `frente_listo_para_cierre` —alerta, no propuesta: no hay
valor que proponer—. El Residente solicita el cierre, el Supervisor aprueba, Control de obra valida; quien origina se
salta su paso. El agente puede mostrar la alerta en Consulta; **no solicita nada**.

**d · El agente propone corregir un prefijo** *(casi toda construida)*. Un detector ve claves cuyo prefijo no corresponde
a lo que son —como las 79 `AUX-` que eran materiales—, llama a la mano que simula y deja una `PROPUESTA(clonacion)` con
la simulación como evidencia y su `base`. Control de obra la aprueba; corre `corregir_prefijo` con su identidad y
`esperaba`. Lo que falta es el detector, la credencial del agente y el MCP; la bandeja, la operación, la simulación y los permisos ya existen.

---

# 7. Lo que falta decidir o construir

> **Desde D-487 la app no se construye.** Los huecos de construcción (3 a 5, y del 6 la credencial) quedan descritos y no se trabajan; los de decisión (1, 2 y 7) siguen siendo del cerebro.

| # | Hueco | Quién lo mueve | Por qué importa |
|---|---|---|---|
| 1 | **`registrar_avance` sigue sin dueño** (quién captura el avance que alimenta las alertas de frente y de atraso). Recomendación, siguiendo lo que ya hay: Residente y Supervisor, que ejecutan y dan seguimiento. *D-485 asignó, como propuestas, las otras dos del lazo: `aprobar_propuesta` a Control de obra, que ya gobierna entre obras, y `resolver_alerta` a Supervisor y Control de obra* | **El usuario** | Confirmar o cambiar las dos asignadas, y decidir la tercera. Corregirlas no toca esquema (`gestionar_rol_funcion`) |
| 2 | **Superintendente tiene una sola función en la tabla**, aunque §5b le da «los mismos privilegios que Supervisor» | **El usuario** | Hoy un Superintendente no puede aprobar una incidencia que su Supervisor sí |
| 3 | **El alcance por obra no se aplica en código** (B-98) | Construir | Mientras no esté, el agente y cualquier herramienta de lectura solo se pueden dar a quien ve todo |
| 4 | **~~La bandeja no existe~~ — construida (D-485).** Quedan tres cosas: aprobar los demás tipos de propuesta (cada uno pide su operación y su función; hoy solo `clonacion`), los detectores que dejan alertas, y la pantalla (B-99) | Construir | La bandeja es el lugar; lo que la llena y lo que ejecuta cada tipo se construye tipo por tipo, no de golpe |
| 5 | **El MCP no existe** (B-63) | Construir; la bandeja ya está | La API de D-482 es su base. Para no escribir a mano su catálogo, cada operación de la API puede declarar su **efecto** (lee, simula o aplica) y su **función**, y de ahí se derivan las herramientas |
| 6 | **Con qué credencial actúa el agente**: la de quien pregunta para leer y simular (así se respeta su alcance y su función), y la suya propia, marcada `origen=agente`, para dejar propuestas | El usuario confirma | Es lo que hace que «quien decidió» siga siendo una persona. Mientras no exista, `dejar_propuesta` solo deja propuestas de personas: el servicio ya sabe recibir las del agente, la API no se las abre |
| 7 | **Las funciones de capturar y devolver una estimación**, y las de capturar avance, no tienen clave (`MODELO.md` §5d) | El usuario | Estimación y avance no se pueden construir sin saber quién las escribe |
| 8 | **~~`programa` no tenía skill~~ — compilado (D-486).** `2-operacion/skills/erp-programa.md` sale de `PROGRAMA-CPM.md` y `MODELO.md` §5c; `ESCALABILIDAD.md` §9 lo dejaba fuera porque sus reglas no estaban decididas | Hecho | Quien construya o cambie el motor del CPM, la reprogramación, la bitácora o el Gantt tiene sus reglas y sus 25 errores en un solo lugar |

**En qué orden**, con el criterio de `PRIORIDADES.md` (desbloqueo ÷ costo, y qué cuesta deshacerlo): primero confirmar lo
del hueco 1 —es una decisión, no cuesta código y deshacerla es una fila de `ROL_FUNCION`—; la bandeja (4) ya está, así que
sigue el filtro por obra (3); después el MCP de lectura y simulación con las herramientas de Consulta (5), que no propone nada y por eso es lo
primero seguro de soltar; y al final el primer detector que propone. Cada paso necesita su cifra de paro antes de
empezar (`INVARIANTES.md`).

---

# 8. El flujo de la app, de punta a punta (D-529)

> **Pedido del usuario (D-529):** «Vamos a trabajar en el App flow solo para quedar anotado en el cerebro.» Esto es el **primer borrador**, armado con lo ya decidido (D-453 a D-528); **no agrega reglas ni construye nada** (D-487). *Lectura mía:* el «App flow» es el recorrido de una obra por la app, por rol y por etapa; el flujo de pantallas vendrá cuando se diseñe la app. Marcas: ✅ firme en el modelo · 🔶 propuesta · ❓ abierto · 💭 idea del usuario, sin modelar.

## 8.1 Quién aparece en el flujo

| Quién | Qué hace en el flujo | ¿Es un rol del cerebro? |
|---|---|---|
| **Residente** | Planea su obra y ajusta las fechas del programa; captura el avance; origina incidencias; crea su estimación en Excel y revisa los ajustes; solicita los cierres; entrega la casa; estima hasta el pago de las garantías | ✅ |
| **Supervisor** | Aprueba y cierra incidencias; aprueba el cierre de frente; justifica lo fuera de catálogo; da el visto bueno de la entrega; autoriza liberar la retención | ✅ |
| **Superintendente y equipo de gestión de proyectos** | Firman la entrega de obra (el superintendente puede estar o no). *Lectura mía:* el equipo es el área de Proyectos | ✅ el superintendente, con una sola función (§7, hueco 2) · ❓ el equipo |
| **Control de obra** | Recolecta y envía las estimaciones y comparte la final para el pago; la marca pagada; valida cierres y la calidad de la entrega; confirma los pagos de una OT; confirma o modifica su cotización; contrata un bloque | ✅ |
| **Compras** | Validador de topes: ajusta la estimación, y esa es la que se paga | ❓ no es un rol; D-330 asignó `validar_estimacion` a Control de obra |
| **Finanzas** | Asigna el contratista de un subcontrato | 🔶 no es un rol (B-115) |
| **Proyectos y atención al cliente** | Cotiza y genera la OT; cambia su alcance; atiende al cliente | 🔶 no es un rol (B-115) |
| **Costos** | Carga el export de OPUS; propone precios nuevos | ✅ |
| **Cotizador** | Hoy lo ejecuta Control de obra; sería una herramienta (B-123) | 💭 |
| **Contratista y cliente** | Más adelante entran como usuarios: el contratista al cotizador, al programa de ejecución y a su estado de cuenta (B-121); el cliente a un módulo de vivienda (B-125) | 💭 |

## 8.2 Las nueve etapas

| # | Etapa | Quién hace qué | Qué queda registrado | Dónde está decidido | Marca |
|---|---|---|---|---|---|
| 1 | **Preparar el catálogo y los presupuestos** | Costos carga el export de OPUS; Control de obra decide lo detenido y las bajas; Costos propone precios nuevos y Control de obra y Superintendente los aprueban | El catálogo con sus versiones y el presupuesto de cada prototipo como plantilla | §6 (recorrido a) y `MODELO.md` §3 | ✅ sin pantalla |
| 2 | **Dar de alta el lugar** | Proyecto (Magnolia y «Antigua»), clusters o manzanas y lotes: cada casa es una obra, con su prototipo y sus m² adicionales; una urbanización por proyecto | El proyecto, el cluster y la obra con su estatus `pendiente` | `MODELO.md` §3c (D-512, D-520, D-521) | ✅ |
| 3 | **Planear la obra, antes de la junta de arranque** | Se asignan residente y supervisor; se asigna el contratista por obra y tipo de trabajo, y de ahí por etapa o concepto; se cuelga el programa del prototipo y el residente ajusta las fechas; Control de obra contrata un bloque y con eso se fija el precio | `RESIDENTE_OBRA`, `SUPERVISION`, `ASIGNACION_CONTRATISTA`, el programa de la obra y `ESTADO_CONGELAMIENTO` | `MODELO.md` §4a y `MODELO.md` §5c; D-475 y D-512 | ✅ · ❓ cuándo cierra la junta de arranque |
| 4 | **Contratar un subcontrato (la OT)** | La venta al cliente es un presupuesto o un control de cambio; Finanzas asigna el contratista; Proyectos cotiza y genera la OT; Control de obra, después, la confirma o la modifica contra el presupuesto base | `ORDEN_TRABAJO` en `cotizada`, con su `COTIZACION_OT` por versión | `MODELO.md` §5i (D-518 y D-519) | ✅ · 🔶 descuentos y cotizador |
| 5 | **Ejecutar y registrar el avance, cada semana** | El residente captura el avance físico (el sistema propone el porcentaje y se corrige solo lo raro); origina incidencias que aprueba el supervisor, valida control, ejecuta el residente y cierra el supervisor; un extra puede pasar a orden de cambio con el cliente; el almacén surte | `REGISTRO_AVANCE` físico, `INCIDENCIA` y `ALERTA` | `CONOCIMIENTO.md` §13.7 y `MODELO.md` §5c | ✅ · ❓ quién captura el avance (§7, hueco 1) |
| 6 | **Estimar y pagar, cada semana** | El residente crea su estimación en Excel; Control de obra las recolecta, las pasa al extractor y las envía al validador de topes (hoy Compras); vuelven a residentes y supervisores para ajustar y justificar lo fuera de catálogo; el validador ajusta y esa es la que se paga; Control de obra comparte la final y la marca pagada. Los pagos de una OT entran por la estimación, en efectivo o por transferencia, y Control de obra los confirma | `ESTIMACION` de `capturada` a `pagada`, con el oid de cada renglón y su historia; `PAGO_OT` | `MODELO.md` §5d y `MODELO.md` §5i (D-522 y D-519) | ✅ · ❓ el validador |
| 7 | **Cerrar** | Frente al 90 %: el residente solicita, el supervisor aprueba, control valida; si se requiere, también por actividades; el lote se entrega con los cuatro participantes en cualquier orden; cerrar cierra al residente | `CIERRE_FRENTE`, `CIERRE_ACTIVIDADES` y `ENTREGA_OBRA` | `MODELO.md` §5c (D-515, D-516 y D-522) | ✅ |
| 8 | **Entregar y atender la postventa** | La obra pasa a `entregada` y entra a postventa: garantía, y OT de postventa y de mantenimiento (con cobro al cliente, por garantía o necesaria para la entrega); la retención se libera al entregar la vivienda o antes si el supervisor lo autoriza; la OT concluye cuando se pagó todo | `TICKET_GARANTIA` y `ORDEN_TRABAJO` | `MODELO.md` §3b y `MODELO.md` §5i | ✅ |
| 9 | **Más adelante** | El cliente pide cambios antes y durante la obra, y postventas y mantenimientos después; el contratista entra al sistema; la entrega puede escalar a un acta de entrega y recepción | — | B-125, B-121 y D-522 | 💭 |

## 8.3 Cómo cambia de estado lo que viaja

| Cosa | Estados | Quién los mueve |
|---|---|---|
| **Obra** | `pendiente` → `iniciada` → `en_proceso` → `por_entregar` → `entregada` y postventa | `iniciada` y `entregada` se marcan; los demás se derivan del avance (desde el 90 %, `por_entregar`) |
| **Estimación** | `capturada` → `enviada` → `devuelta` → `validada` → `pagada` | Control de obra envía y marca pagada; el validador de topes la ajusta y valida |
| **OT** | `cotizada` → `concluida` o `cancelada` | Proyectos la cotiza; el sistema propone concluirla y Proyectos lo confirma |
| **Incidencia** | `originada` → `aprobada` → `validada` → `ejecutada` → `cerrada`, o `descartada` | Residente y supervisor, control y supervisor; quien origina no se aprueba a sí mismo |
| **Cierre de frente** | solicitado → aprobado → validado | Residente, supervisor y control de obra |

## 8.4 Dónde se cruzan el avance físico y el pagado

Cada semana el flujo produce **dos avances que no se corrigen entre sí:** el **físico,** que captura el residente (etapa 5), y el **pagado,** que sale de la estimación (etapa 6) y que las exportaciones de OP también reflejan (D-525). La diferencia es la señal, y la resuelve Control de obra con evidencia (`CONOCIMIENTO.md` §13.7). Antes del pago, la estimación se cruza además con lo que el almacén surtió (§2.3). Una estimación validada **cierra esa semana de la obra para todos** (B-120, 🔶).

## 8.5 Lo que el flujo todavía no resuelve

| # | Hueco | Quién lo mueve |
|---|---|---|
| 1 | **Compras como validador de topes:** ¿rol nuevo con `validar_estimacion`, o sigue Control de obra? (B-115) | El usuario |
| 2 | **Funciones sin clave:** capturar, enviar, devolver y marcar pagada una estimación; asignar un subcontrato; cotizar y auditar una OT; liberar la retención; capturar avance (§7, hueco 7, y B-115) | El usuario |
| 3 | **Descuentos, traspaso del anticipo y cotizador** (B-110, B-124 y B-123) | El usuario |
| 4 | **La junta de arranque:** cuándo se cierra la planeación y quién la declara cerrada | El usuario |
| 5 | **La urbanización:** una obra única con ramas de clústeres y amenidades; su flujo propio no está escrito, y ObraCtrl hoy no la representa (D-523, G3) | El usuario |
| 6 | **Los avisos:** quién se entera de qué en cada paso (devoluciones, cierres, pagos); ObraCtrl los tiene y el cerebro los dejó fuera (D-516) | El usuario |
