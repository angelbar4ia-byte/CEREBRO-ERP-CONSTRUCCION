# WORKFLOWS

```
órgano:     comisuras — conectan los circuitos
capa:       II — Operación
pregunta:   ¿cómo trabajan juntos las personas, el sistema, el agente interno y las skills?
tiempo:     se hace así
corte:      2026-10-16
verificado: mapa derivado de lo decidido en MODELO, CONOCIMIENTO, gravity-obra y ESCALABILIDAD y de lo construido hasta D-485 · tres propuestas sin confirmar (D-484), construidas en la bandeja (D-485) · §8, el flujo de la app, armado en D-529 con lo decidido hasta D-528 · §8.1, la cadena de la información y el diseño del presupuesto, agregada en D-530 con lo ya escrito en MODELO, CONOCIMIENTO y PROPUESTA-CUATRO-MODULOS · D-531: el cuantificador, la cotización al cliente, la ingeniería de costos y los niveles de «definido» · D-532: esas respuestas confirmadas y la segunda mitad de la cadena, del programa a la ejecución · D-533: quién registra el avance, la cadena para reprogramar lo contratado, cuándo se confirma el avance y los dos modos de precio de la cotización · D-534: quién confirma el avance y a qué nivel, qué corrige la estimación pagada y el precio por m² ajustable · D-535: confirmar no es candado pero lo estimado de más es una alerta importante, el usuario decide cómo se baja un porcentaje, y el precio por m² incluye IVA y no es fijo · D-536: §8.7, los roles paso por paso · D-537: tres roles nuevos y sus funciones, pasadas a `MODELO.md` · D-538: el proceso de hoy de la estimación y `validar_estimacion` en Compras · D-539: la justificación en el renglón, las pantallas son de las apps y §8.8 · D-540: el App flow se cierra, y la postventa será un módulo con una persona encargada · D-541: el colono abre el ticket de postventa, Atención a postventa es un rol propio y el cierre se confirma con la satisfacción del colono · D-542: el colono confirmado, la escala de 5 a 10, el cierre sin confirmación y que pedir cambios ya estaba definido · D-543: la re-solicitud al colono, el paso 0 de ObraCtrl descartado y las obras del piloto en la app
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
| **Residente** | Sus obras (`RESIDENTE_OBRA`) | `trazar` · `anotar_plano` · `originar_incidencia` · `ejecutar_incidencia` · `solicitar_cierre_frente` · `editar_fechas_programa` · `registrar_avance` · `trazar_avance` · `proponer_reprogramacion` (las tres últimas, D-533) · `confirmar_avance` · `entregar_obra` (propuestas, D-537) · `capturar_estimacion` (D-538) · `replicar_estimacion` (propuesta, D-538) |
| **Supervisor** | Las de los residentes que supervisa (`SUPERVISION`) | `trazar` · `anotar_plano` · `originar_incidencia` · `aprobar_incidencia` · `cerrar_incidencia` · `aprobar_cierre_frente` · `resolver_alerta` (propuesta, D-485) · `trazar_avance` · `proponer_reprogramacion` · `revisar_reprogramacion` (las tres últimas, D-533) · `justificar_fuera_de_catalogo` · `dar_visto_bueno_entrega` · `liberar_retencion` (propuestas, D-537) |
| **Superintendente** | Las de los supervisores que le reportan | `aprobar_precio_nuevo`, junto con Control de obra, y `firmar_entrega_superintendente` (propuesta, D-537). §5b dice «mismos privilegios que Supervisor», pero la tabla no lo escribe (§7, hueco 2) |
| **Costos** | Todas | `trazar` · `proponer_precio_nuevo` · `cargar_catalogo_opus` (propuesta) · `cargar_ingenieria` (propuesta, D-537) · `justificar_aumento_cantidad` (propuesta, D-538) |
| **Compras** | Ve todas | `validar_estimacion` (pasó de Control de obra) y `devolver_estimacion` (D-538) |
| **Finanzas** | Ve todas | `asignar_subcontrato` (D-537) |
| **Proyectos y atención al cliente** | Ve todas | `cotizar_ot` · `cambiar_alcance_ot` · `firmar_entrega` (D-537): es también el equipo de gestión de proyectos |
| **Atención a postventa** (D-541) | Las casas entregadas *(lectura mía)* | `solicitar_cierre_ticket` (propuesta, D-541) · `abrir_ticket_garantia`, en nombre del colono (D-542) |
| **Colono** (D-542) | Solo su casa | `abrir_ticket_garantia` (D-541) · `confirmar_cierre_ticket` (propuesta, D-541) |
| **Cotizador** | No es un rol activo | Hoy lo ejecuta Control de obra |
| **Control de obra** | Todas | `trazar` · `aprobar_trazo` · `originar_incidencia` · `validar_incidencia` · `validar_cierre_frente` · `trazar_avance` · `validar_reprogramacion` · `aplicar_reprogramacion` (las tres, D-533) · `editar_estructura_programa` (también subir un programa) · `aprobar_precio_nuevo` · `cargar_catalogo_opus` · `contratar_subarbol` · `clonar_insumo` · `aprobar_propuesta` y `resolver_alerta` (propuestas, D-485) · y el gobierno entre obras: `gestionar_rol_funcion` · `asignar_residente` · `asignar_supervision` · `renovar_invariante_valor` · `reclasificar_familia` · `resolver_revisar_parametro` · y, desde D-537, `dar_de_alta_obra` · `asignar_contratista` · `pactar_precio_contratista` · `marcar_obra_iniciada` · `autorizar_orden_cambio` · `enviar_estimacion` · `marcar_estimacion_pagada` (confirmadas; las dos últimas en D-538) y `cotizar_cambio_cliente` · `validar_calidad_entrega` · `confirmar_pago_ot` · `auditar_alcance_ot` · `justificar_aumento_cantidad` · `aprobar_cierre_ticket_sin_confirmar` (propuestas) |

**Lo que se ve de un vistazo:** el trabajo de obra se reparte en cadena —Residente ejecuta y pide, Supervisor aprueba
y cierra, Control de obra valida— y **el gobierno cruzado entre obras cae en Control de obra** (treinta y tres de las
sesenta funciones asignadas, D-538). Siete existen sin dueño (§7, hueco 1), como `comprometer_gasto` o
`aplicar_descuento`; `registrar_avance`, la que alimenta las alertas de frente y de atraso, ya lo tiene (D-533).

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
| 1 | **~~`registrar_avance` sin dueño~~ — ✅ cerrado (D-533):** el residente anota la cantidad o el porcentaje, y control, residente y supervisor hacen el trazo del avance (Costos no). *Queda por confirmar de D-485:* `aprobar_propuesta` a Control de obra y `resolver_alerta` a Supervisor y Control de obra, que siguen como propuestas | **El usuario** | Confirmar o cambiar las dos asignadas. Corregirlas no toca esquema (`gestionar_rol_funcion`) |
| 2 | **Superintendente tiene una sola función en la tabla**, aunque §5b le da «los mismos privilegios que Supervisor» | **El usuario** | Hoy un Superintendente no puede aprobar una incidencia que su Supervisor sí |
| 3 | **El alcance por obra no se aplica en código** (B-98) | Construir | Mientras no esté, el agente y cualquier herramienta de lectura solo se pueden dar a quien ve todo |
| 4 | **~~La bandeja no existe~~ — construida (D-485).** Quedan tres cosas: aprobar los demás tipos de propuesta (cada uno pide su operación y su función; hoy solo `clonacion`), los detectores que dejan alertas, y la pantalla (B-99) | Construir | La bandeja es el lugar; lo que la llena y lo que ejecuta cada tipo se construye tipo por tipo, no de golpe |
| 5 | **El MCP no existe** (B-63) | Construir; la bandeja ya está | La API de D-482 es su base. Para no escribir a mano su catálogo, cada operación de la API puede declarar su **efecto** (lee, simula o aplica) y su **función**, y de ahí se derivan las herramientas |
| 6 | **Con qué credencial actúa el agente**: la de quien pregunta para leer y simular (así se respeta su alcance y su función), y la suya propia, marcada `origen=agente`, para dejar propuestas | El usuario confirma | Es lo que hace que «quien decidió» siga siendo una persona. Mientras no exista, `dejar_propuesta` solo deja propuestas de personas: el servicio ya sabe recibir las del agente, la API no se las abre |
| 7 | **Las funciones de capturar y devolver una estimación** no tienen clave (`MODELO.md` §5d); las de capturar avance ya la tienen (D-533) | El usuario | Estimación y avance no se pueden construir sin saber quién las escribe |
| 8 | **~~`programa` no tenía skill~~ — compilado (D-486).** `2-operacion/skills/erp-programa.md` sale de `PROGRAMA-CPM.md` y `MODELO.md` §5c; `ESCALABILIDAD.md` §9 lo dejaba fuera porque sus reglas no estaban decididas | Hecho | Quien construya o cambie el motor del CPM, la reprogramación, la bitácora o el Gantt tiene sus reglas y sus 25 errores en un solo lugar |

**En qué orden**, con el criterio de `PRIORIDADES.md` (desbloqueo ÷ costo, y qué cuesta deshacerlo): primero confirmar lo
del hueco 1 —es una decisión, no cuesta código y deshacerla es una fila de `ROL_FUNCION`—; la bandeja (4) ya está, así que
sigue el filtro por obra (3); después el MCP de lectura y simulación con las herramientas de Consulta (5), que no propone nada y por eso es lo
primero seguro de soltar; y al final el primer detector que propone. Cada paso necesita su cifra de paro antes de
empezar (`INVARIANTES.md`).

---

# 8. El flujo de la app, de punta a punta (D-529)

> **Pedido del usuario (D-529):** «Vamos a trabajar en el App flow solo para quedar anotado en el cerebro.» Esto es el **primer borrador**, armado con lo ya decidido (D-453 a D-528); **no agrega reglas ni construye nada** (D-487). *Lectura mía:* el «App flow» es el recorrido de una obra por la app, por rol y por etapa. **El flujo de pantallas no es del cerebro: es de las apps** (D-539). Marcas: ✅ firme en el modelo · 🔶 propuesta · ❓ abierto · 💭 idea del usuario, sin modelar.

> **Por dónde se empieza (D-530).** El usuario pidió ver «todas» las lecturas —el recorrido por rol y por etapa, y el flujo de pantallas—, «pero primero entender el flujo de la información y sus redes: para que una obra exista debe haber un presupuesto, después un programa y su ejecución; el presupuesto pasa por un proceso de diseño; hay varios tipos de presupuesto y se puede partir de una base o de una ingeniería; y no sé si definir el cuantificador como una herramienta o como módulo de diseño o de comprobación». Por eso §8.1 es nueva y va antes que los roles: dice **qué viaja y de dónde sale** antes de decir **quién lo mueve**. Sigue siendo anotación (D-487): nada de esto agrega reglas.

## 8.1 De dónde sale una obra: la cadena de la información (D-530)

### La cadena: presupuesto, programa y ejecución

```
 CATÁLOGO (Costos, OPUS) ──── precio ───────────────────────────┐
                                                                ▼
 BASE (el prototipo)      ─┐                          ┌───────────────────┐
 INGENIERÍA (la del lote) ─┼─► DISEÑO ──────────────► │    PRESUPUESTO    │
 PLANOS o desde cero      ─┘   cuantificar · estimar  │  = la obra (tipo) │
                               · comparar             └─────────┬─────────┘
                                                                │ el programa cuelga de él
                                                                ▼
                                    PROGRAMA (ACTIVIDAD: duración, precedencia, fechas)
                                                                │ la ejecución se mide contra él
                                                                ▼
                    EJECUCIÓN (avance · incidencias · OT · estimación · almacén · cierre)
                                                                │
   lo medido y lo ejecutado vuelven ◄───────────────────────────┘
   al catálogo · a las plantillas · al paramétrico  (la bandeja propone; una persona decide)

   Cada rama del presupuesto: diseño → contratado.   Cada carga: incompleta → completa.
```

- **Que una obra necesita presupuesto es literal en el modelo ✅.** No hay tabla `OBRA`: una casa **es** un `PRESUPUESTO(tipo=obra)` con su cluster (o manzana) y su lote, y nace con estatus `pendiente` (`MODELO.md` §3c). El programa cuelga de ese presupuesto (`ACTIVIDAD.presupuesto_id`, `MODELO.md` §5c y §4a, D-474) y todo lo de la ejecución —avance, incidencias, estimación, almacén— cuelga de las mismas filas. Crear la obra y crear su presupuesto son un solo acto.
- **El orden es de dependencia, no de calendario ✅.** No se programa lo que no está en el presupuesto, ni se ejecuta lo que no está programado; pero **cada rama avanza a su paso:** los planos llegan por partes y el congelamiento es por subárbol, así que cimentación puede estar contratada, programada y ejecutándose mientras acabados sigue en diseño (`CONOCIMIENTO.md` §1.4). «Presupuesto definido» no es un momento de la obra, es un estado de cada rama.
- **El programa puede nacer antes de que el presupuesto esté completo 🔶.** *Lectura mía:* se cuelga el programa del prototipo mientras la obra está en `pendiente` y se ajusta mientras la rama sigue en diseño; contratar la rama lo congela, y solo a nivel diseño se puede reiniciar (`MODELO.md` §4a, D-475, y `PROPUESTA-CUATRO-MODULOS.md` §4, «Reiniciar programa o actividad»). Queda por confirmar si el programa puede arrancar con la rama aún en diseño (§8.6, hueco 9).

### Las redes: seis recorridos de la información

Cada red es una de las dimensiones del contrato de módulo (`ESCALABILIDAD.md` §2, pregunta 1); ninguna crea árbol propio, todas leen el mismo (`ESCALABILIDAD.md` §1). **Un dato tiene un solo dueño.**

| Red | Qué viaja | Nace en | Pasa por | Llega a | Dueño del dato |
|---|---|---|---|---|---|
| **Costo** | Precio de insumo → matriz → PU → importe | El catálogo (export de OPUS, Costos) | `VERSION_CONCEPTO`; el precio se fija al contratar la rama (D-475) | Presupuesto, OT, estimación | El catálogo es de Costos; fijar el precio, de Control de obra |
| **Cantidad** | Plano → trazo → medida → cantidad, con su `modo_cantidad` | Planos, la base, la ingeniería o el paramétrico | El cuantificador (§8.1, «El cuantificador») | Cada renglón del presupuesto | El presupuesto: la cantidad es su único dato propio |
| **Tiempo** | Rendimiento, duración, precedencia, fechas | El presupuesto y el rendimiento del catálogo | CPM y calendario de obra | El programa y las fechas que ajusta el residente | El programa |
| **Ejecución** | Avance físico, incidencias, lo que el almacén surtió | La obra | Alertas y cruces (§8.5) | Cierre de frente, estimación | Residente y supervisor para el avance (❓ §7, hueco 1); el ERP externo para el almacén |
| **Pago y responsabilidad** | Contrato u OT, estimación, pago | La asignación del contratista y la OT | El validador de topes | `pagada`; la retención | Control de obra; Compras, el validador |
| **Aprendizaje** | Lo medido y lo ejecutado: tasas, precios nuevos, rediseños | La ejecución y el cuantificador | El paramétrico y la bandeja de propuestas | El catálogo, las plantillas y las estimaciones paramétricas | Nadie aplica solo: «propone, no aplica» (`CONOCIMIENTO.md` §14) |

### El proceso de diseño del presupuesto

Es lo que ocurre entre «la obra existe» y «la rama se contrata». No es una pantalla: son **cuatro movimientos** que el cerebro ya tiene, repetidos por rama.

| # | Movimiento | Qué pasa | Dónde está escrito |
|---|---|---|---|
| 1 | **Arrancar** | La obra nace de una de tres fuentes (tabla siguiente) | `CONOCIMIENTO.md` §5.10, «Los dos arranques» |
| 2 | **Cargar o cuantificar** | La ingeniería llega **por partes, normalmente por niveles** (D-531), a veces durante meses (`ALAMO 18`: abril a septiembre): `ESTADO_CARGA` va de `incompleto` a `completo` por nodo, y **una carga incompleta nunca bloquea,** solo avisa. Donde hay plano se mide; donde no, se estima | `MODELO.md` §3, hallazgo 8; `CONOCIMIENTO.md` §5.10 |
| 3 | **Comparar** | La ingeniería del lote contra su prototipo, antes de construir: la diferencia se descompone en precio y consumo y cae en alguna de las nueve causas; **una diferencia sin causa, o una razón fuera del 20 %, es alerta y no se corrige sola** | `CONOCIMIENTO.md` §11.7 y `CONOCIMIENTO.md` §13.6 |
| 4 | **Contratar la rama** | Control de obra contrata un bloque; con eso se fijan los PU y la rama pasa de `diseño` a `contratado`: solo admite adiciones al final | `MODELO.md` §4a, D-475 |

**Las tres fuentes del arranque.** El cerebro nombraba dos («los dos arranques»); el usuario nombró «una base o una ingeniería», y la ingeniería del lote no es lo mismo que copiar la base. Las tres filas ya existen en el cerebro; *separarlas así es lectura mía, para confirmar:*

| Se arranca | Qué entra | `modo_cantidad` | Qué dice | Marca |
|---|---|---|---|---|
| **De una base** | Se copia el prototipo (la plantilla) con sus cantidades; la obra queda con `prototipo_id`. Las modificaciones que pida el cliente no se marcan en el árbol: son órdenes de cambio | `heredada` | «No son de esta obra»: es lo que falta revisar | ✅ |
| **De una ingeniería** | Se carga la ingeniería del lote, que es la instancia (el prototipo es la plantilla). **La prepara Costos (la ingeniería de costos) y llega como un Excel, por partes, normalmente por niveles** (D-531); en algún momento Costos podrá hacerla en esta plataforma 💭. La ingeniería **base** de cada prototipo ya existe: es la explosión de la matriz de cada concepto | `capturada` (viene de un archivo); `medida` si después se traza | Trae su propia estructura (cinco formas, `firma`); sus compuestos vienen abiertos | ✅ |
| **Desde cero** | El paramétrico compone la estructura con cantidades estimadas, y el cuantificador las sustituye conforme haya planos | `estimada`, con su dispersión | Es el único caso en que no hay obra anterior de dónde copiar | ✅ |

Una misma obra suele mezclar las tres, rama por rama: *«el tercer caso es el normal: la cimentación ya está en planos y se mide, acabados todavía no y se estima»* (`CONOCIMIENTO.md` §5.10). Por eso el arranque no es un campo de la obra, sino el `modo_cantidad` de cada renglón.

### ¿Cuándo está «definido» un presupuesto? Cuatro niveles (D-531, confirmado en D-532)

El usuario pidió **más contexto** sobre esta pregunta (§8.6, hueco 9). Lo que el cerebro ya tiene son **cuatro niveles de «listo», por nodo y no por obra,** de menos a más exigente:

| Nivel | Qué significa | Quién lo mueve | Qué permite o qué avisa | Dónde está |
|---|---|---|---|---|
| **Cargado** | La ingeniería de ese nivel llegó entera contra el presupuesto vigente (`ESTADO_CARGA = completo`) | Se marca solo al llegar al 100 % | Nada se bloquea si falta: avisa | `MODELO.md` §3, hallazgo 8 |
| **Costeado** | El nodo tiene costo; no está «pendiente de costear» | Costos | **Programarlo y contratarlo.** Es la regla dura: *«lo que no está costeado no se puede contratar ni programar»* | `CONOCIMIENTO.md` §4.1 |
| **Listo** | Cantidad `medida`, costeado y aprobado | Costos y quien aprueba | Sale de la cola de trabajo, que ordena la dispersión por el monto: *«el presupuesto nunca está incompleto, está provisional en algunas partes»* | `CONOCIMIENTO.md` §13.5 |
| **Contratado** | PU fijados y rama congelada: solo admite adiciones al final | Control de obra | Pagar a un contratista a precio pactado; los cambios van por control de cambio | `MODELO.md` §4a, D-475 |

**Un caso real.** `ALAMO 18` tuvo once ingenierías de abril a septiembre, casi todas por nivel (`CIM` es el nivel 1, `PB` el nivel 2, `PA` cubre los niveles 3 al 6 y 11 al 14, y `PISOS` ni siquiera declaraba el suyo). Sumadas llegaban al **92 %** del presupuesto del Diamante con chimenea; faltaban cinco niveles completos (cancelería, carpintería, muebles, herrería y consumibles) y el sistema lo detectó solo, comparando contra el presupuesto (`CONOCIMIENTO.md` §11.8). La obra no esperó, y el cerebro lo dice así: *comprometer —contratar, programar— exige costeo; registrar un avance nunca se bloquea* (`CONOCIMIENTO.md` §13.3).

**Lo que esto contesta:**

- **¿Puede arrancar el programa con la rama en diseño?** Sí, y no hay que inventar la regla: programar pide que el nodo esté **costeado,** no contratado ni medido; una cantidad `estimada` sirve para programar (aunque con precisión baja y declarada). Lo que una rama en diseño no puede es contratarse con precio alzado sobre una cantidad estimada sin que el sistema lo advierta (`CONOCIMIENTO.md` §4.1, «la combinación peligrosa»).
- **¿Quién declara que una rama está lista para contratarse?** No hay una declaración aparte: **contratar la rama es la declaración,** y la hace Control de obra. El sistema la frena y pide confirmación si el PU de un concepto se mueve más de 5 % o si un concepto sin matriz valdría cero (`MODELO.md` §4a, D-475).

**Tres lecturas posibles de «definido»,** y la que el usuario confirmó (D-532):

| Lectura | Qué implicaría | Qué pasó |
|---|---|---|
| **A. Costeado** | «Definido» es lo que ya se puede programar; contratado es otro estado | **✅ Confirmada (D-532).** Es lo que el cerebro ya dice, y deja programar mientras el resto de la obra sigue en diseño |
| **B. Contratado** | Solo se programa lo contratado | Descartada: obligaría a contratar antes de programar, y el programa del prototipo se cuelga cuando la obra aún está `pendiente` |
| **C. Cargado completo o medido** | No se programa hasta tener toda la ingeniería o todos los planos | Descartada: la obra tendría que esperar niveles que llegan meses después. *«La obra no para»* |

### Los tipos de presupuesto: tres ejes, y el cerebro ya los tiene

*Lectura mía:* «varios tipos de presupuesto» cabe en tres preguntas distintas. Ninguna es nueva; hace falta que el usuario diga si falta alguna.

| Eje | Pregunta | Valores | Dónde vive | Marca |
|---|---|---|---|---|
| **Para qué sirve** | ¿Qué es este presupuesto? | **plantilla** (el prototipo: siete, de 172 a 300 m²) · **obra** (una casa, o la urbanización: una por proyecto) · **escenario** (un candidato para comparar precio/proveedor, alcance o programa, D-107) · **cotización** (la oferta al cliente de un cambio o adicional, D-532) | `PRESUPUESTO.tipo` | ✅ |
| **Cómo se valúa cada renglón** | ¿Cómo se llega al importe? | **por PU** (la matriz) · **por ensamble** (paramétrico) · **alzado** (precio declarado, con o sin desglose) | El nodo, no el presupuesto: *«el presupuesto no tiene tipo; “mixto” no se guarda, se reporta en porcentaje»* | ✅ |
| **De dónde viene cada cantidad** | ¿Quién dice cuánto? | **medida** · **estimada** · **capturada** · **heredada** | `modo_cantidad` en la relación | ✅ |

**El usuario (D-531) dijo que el único tipo que falta es el del control de cambio:** *«antes de que sea control de cambio se realiza un presupuesto al cliente del cambio o adicional»*. Con eso los tipos quedan en esos tres ejes, y la cotización es **el cuarto valor de `PRESUPUESTO.tipo`** (D-532, `MODELO.md` §3a; siguiente subsección). La cotización de una OT (`COTIZACION_OT`) es el costo del subcontrato, no un presupuesto al cliente: es otra cosa.

### Después de contratar: la cotización al cliente y el control de cambio (D-531 y D-532)

**El cerebro ya la nombra.** El Cotizador (`MODELO.md` §5b) tiene **dos artefactos:** el **Highlight** (antes de la ejecución, el cliente pide un estimado preliminar) y el **Adicional al presupuesto** (ya en ejecución, un presupuesto extra sobre lo contratado). Los dos se foliaban y, al aprobarse, se vuelven control de cambio (`CONOCIMIENTO.md` §13.4), y una cotización se estructura como presupuesto por PU. Hoy lo ejecuta Control de obra.

```
 petición de un cambio o de un adicional
   └─► COTIZACIÓN al cliente  (Highlight o Adicional; foliada; estructura de presupuesto por PU)
         └─► el cliente la aprueba ─► CONTROL DE CAMBIO  (PROPUESTA tipo orden_cambio, p. ej. CC-ALM-18001)
               └─► se agrega al final de la rama congelada: lo contratado no se reescribe
                     └─► programa y ejecución; si el trabajo, además, se subcontrata, nace una OT
```

Lo que hace al control de cambio distinto de editar el presupuesto: **no edita, agrega;** lleva causa, impacto en monto y plazo, quién autoriza y **si se autorizó antes o después de ejecutar** (el porcentaje de retroactivas mide qué tan sano está el proceso, `CONOCIMIENTO.md` §13.4).

**Lo que el usuario resolvió (D-532 y D-533):** *(a)* la cotización **es un presupuesto con su propio `tipo`** (`cotizacion`) y **se convierte en control de cambio una vez que el cliente la acepta**; *(b)* **el precio depende de qué se cotiza** (`MODELO.md` §3a):

| Cuándo | Cómo se fija el precio | Se confirma |
|---|---|---|
| **Una ampliación por m²** | **m² × 17,000.** Ese precio abarca todo, desde la cimentación hasta los equipamientos | Con el presupuesto de la ampliación (costo directo ÷ 0.7) |
| **Algo específico,** como un cambio de sanitarios | **Se presenta la diferencia** (costo directo de lo que entra − el de lo que sale) **÷ 0.7** | — es el cálculo |

El 0.7 se guarda como parámetro editable con su fecha. **Los 17,000 pesos son lo que el cliente paga por cada m² de construcción adicional, con el IVA incluido** (no se presenta por separado), y **no son fijos:** a veces se pacta más barato, y cada cotización lleva el precio pactado (D-535). *Lecturas mías, por confirmar:* los m² de una ampliación son los `m2_adicionales` de la casa; manda el precio pactado y el presupuesto de la ampliación confirma qué tan lejos queda de su costo directo entre 0.7, sin bloquear. **Sigue abierto (B-123):** si el precio varía por proyecto o prototipo, cómo se representa lo que sale, el folio, quién la hace (hoy Control de obra) y si la orden de cambio guarda también el precio al cliente. **D-487:** nada se construye.

### El cuantificador: un motor con dos entradas (D-531, confirmado en D-532)

**El usuario (D-531)** no se decidía y pidió ayuda; ofrece una salida: *«puede ser un módulo para profundizar y proyectos desde cero o partidas grandes, y una herramienta para un concepto en específico»*. **Se adoptó y el usuario lo confirmó (D-532) ✅.** Es un **solo motor** con **dos entradas** que se distinguen por **alcance,** no por etapa:

| Entrada | Alcance | Cuándo se usa | Cómo se abre |
|---|---|---|---|
| **Herramienta (puntual)** | Un concepto, un renglón o una actividad | Comprobar una cantidad que el renglón ya trae (`heredada`, de la ingeniería o `estimada`); medir un adicional; ajustar tras un cambio de plano; medir una actividad del programa | Un botón «medir» en el renglón del presupuesto o en la actividad; abre el plano en el lugar de ese concepto |
| **Módulo (espacio de trabajo)** | Un nivel, una partida grande o una obra completa | Arrancar **desde cero;** cuando llega un nivel nuevo de planos; cuantificar cimentación o acabados de una vez | Una entrada propia del menú: el plano completo, con el árbol del cuantificador reflejando el del presupuesto |

**Lo que no cambia entre las dos entradas:** el mismo motor y los mismos datos —trazo → medida → cantidad, con su evidencia, una sola cantidad vigente por elemento y el modo en el nodo que recibe—. Lo que se descarta es **partirlo por etapa,** uno de «diseño» y otro de «comprobación»: diseñar o comprobar es lo que el motor hace con un renglón según lo que ese renglón ya traiga.

**Cómo se abre la herramienta (D-532).** El usuario preguntó si la herramienta lleva al módulo o es una ventana flotante y dejó la decisión a la experiencia de uso. **Decisión: una ventana flotante sobre el renglón o la actividad, con un botón «Abrir en el módulo».** Por qué: *(1)* conserva el contexto: el renglón y su cantidad siguen a la vista y se actualizan al cerrar el trazo, y lo habitual en la herramienta es medir un concepto y volver, así que mandar al usuario a otra pantalla le hace perder dónde estaba; *(2)* puede crecer sin empezar de nuevo: «Abrir en el módulo» lleva el mismo plano, el mismo concepto y lo ya trazado, para cuando la tarea se vuelve un nivel entero; *(3)* se puede mover y minimizar para ver el presupuesto debajo, y en una pantalla chica se vuelve una hoja a pantalla completa; *(4)* ventana y módulo son la misma sesión de trazo, así que lo trazado no se pierde al pasar de una a otro. Una sola ventana a la vez.

**Tres usos, que son el «para qué» (y no el «dónde»):**

| Uso | Cuándo | Qué hace | Quién lo abre |
|---|---|---|---|
| **Diseño** | El renglón no tiene cantidad medida: está vacío, `estimada` por el paramétrico o `capturada` | Traza sobre el plano y deja la cantidad como `medida`, con su evidencia (plano, versión, capa) y **cuánto se movió** frente a lo que había | Quien cuantifica (Costos) |
| **Comprobación** | El renglón ya trae una cantidad de otra fuente: `heredada` de la base, o cargada con la ingeniería | Mide por su lado y compara: *«dos fuentes que discrepan mucho son una propuesta con evidencia, no una corrección automática»*. Lo anterior queda como evidencia | Quien cuantifica; si hace falta aprobación, se define por obra (C-3) |
| **Programación** | Una actividad del programa | Es el segundo cuantificador: se mide **contra el techo** del presupuesto, y hasta el 20 % sigue solo; más, se solicita a Control de obra (`PROPUESTA-CUATRO-MODULOS.md` §4, «Dos cuantificadores») | El planeador |

Cualquiera de los tres usos puede entrar por cualquiera de las dos entradas: diseñar un concepto suelto es la herramienta; diseñar un nivel nuevo, el módulo; comprobar un renglón, la herramienta; comprobar un nivel entero antes de contratarlo, el módulo; la programación entra por la actividad.

**Por qué esta salida y no una sola o dos separadas:**

1. **No duplica datos.** Las dos entradas escriben lo mismo, y el cerebro lo pide así: *«el cuantificador no se tipa; el modo ya está en el nodo que recibe»*. Dos módulos por etapa dirían lo contrario.
2. **Ningún módulo crea árbol propio** (`ESCALABILIDAD.md` §1): el espacio de trabajo cuelga geometría de renglones que ya existen, y si hace falta uno que no existe, crea el concepto.
3. **Es módulo y no núcleo:** si no está, el presupuesto sigue y las cantidades se capturan a mano (hoy así, sin poder auditarse), que contesta la pregunta 6 del contrato de módulo (`ESCALABILIDAD.md` §2). Por eso tampoco es una etapa del recorrido.
4. **El costo se reparte bien:** el espacio de trabajo es la parte cara de construir (geometría, planos y versiones, `PROPUESTA-CUATRO-MODULOS.md` §2); la herramienta puntual es un subconjunto suyo. Qué se hace primero lo decidirá `PRIORIDADES.md` cuando D-487 se levante.
5. **El paramétrico depende de él** y no compite con él: aprende de lo medido y genera donde no hay plano (`CONOCIMIENTO.md` §5.10).

**Dos «comprobaciones» que no hay que mezclar.** *(a)* **Comparar la ingeniería del lote contra su prototipo** (movimiento 3): compara **cantidades ya cargadas** entre dos presupuestos y **no necesita plano ni cuantificador;** es el mecanismo de precio y consumo de `CONOCIMIENTO.md` §13.6. *(b)* **Medir contra el plano** (uso «comprobación» de arriba): sí es el cuantificador.

**En el App flow** aparece de dos formas: un botón «medir» que abre la ventana flotante en el renglón y la actividad, y una entrada del menú para trabajar un nivel o una obra completa; no es un paso del recorrido, por eso las etapas de §8.3 no le dan una fila propia. **Lo que sigue abierto:** el umbral de «discrepan mucho» para comprobar un presupuesto no está dicho (el 20 % es el del programa y el de la identidad de la ingeniería), y quién traza y quién aprueba se define por obra, pero nadie ha dicho cuál es la regla de una obra normal.

### La otra mitad de la cadena: del programa a la ejecución (D-532)

**Pedido del usuario (D-532):** «Continuamos con el programa a la ejecución». Todo lo que sigue **ya está en el cerebro** (`MODELO.md` §5c y §5a, `PROPUESTA-CUATRO-MODULOS.md` §4 y `CONOCIMIENTO.md` §13); aquí se junta como recorrido de información, sin agregar reglas.

```
 PRESUPUESTO ── cantidad (el techo) ──┐
 CATÁLOGO ── rendimiento y tiempo de entrega ──┤
                                      ▼
                  PROGRAMA  (ACTIVIDAD · PRECEDENCIA · TRAMO · CALENDARIO)
                      │  duración · vínculos · fechas · cuadrillas · ruta crítica
                      ├──► PROYECCIONES: material, mano de obra, subcontratos y flujo de efectivo, por fecha
                      ▼
          JUNTA DE ARRANQUE ── dispara las fechas contractuales; la obra pasa a `iniciada`
                      ▼
          LA SEMANA DE OBRA:  avance físico · almacén · incidencias · control de cambio
                      ▼                                         ▼
              ESTIMACIÓN → avance pagado → pago        TABLERO Y ALERTAS (se calculan; avisan, no corrigen)
                      └──────────────┬───────────────────────────┘
                                     ▼
            reprogramar (propone) ◄── incidencia · control de cambio · lo real contra lo teórico
                                     ▼
            CIERRE: frente → actividades → lote → entrega → postventa   ·   lo aprendido vuelve a la plantilla y al catálogo
```

#### El programa: de qué está hecho y de dónde sale cada dato

| Dato | De dónde sale | Quién lo toca |
|---|---|---|
| **Cantidad** de la actividad | El presupuesto: es el **techo.** El cuantificador de programación la mide contra él; hasta el 20 % sigue solo, más se solicita a Control de obra | El planeador; Control de obra si pasa del umbral |
| **Duración** | Cinco modos: capturada · **calculada** (cantidad ÷ rendimiento × cuadrillas) · **preestablecida por nivel** (lo que se contrata terminado: cancelería, carpintería, herrería, cubiertas, pérgolas e impermeabilización) · derivada de fechas (obra sin presupuesto colgado) · derivada de hijos (un bloque) | Control de obra la estructura; el residente las fechas |
| **Herencia** | La duración sigue a su referencia (Zafiro por defecto); al editarla se elige a quién alcanza: este programa, todos, 1 planta, 2 plantas o los que se señalen | El planeador |
| **Precedencias** | Técnica (el sistema la propone sola) · de recurso · de decisión; fin-inicio, inicio-inicio o fin-fin, con traslape o espera | La técnica, el sistema; las otras, quien programa |
| **Calendario** | Uno por obra: días laborables, días no hábiles, excepciones por cuadrilla y el paso del plan (un día hábil por defecto) | Control de obra |
| **Tramos** | La actividad se interrumpe (el muro se detiene para colar la cadena): reparte material y cuadrillas por tramo | Se deduce de la precedencia técnica; el resto se captura |
| **Cuadrillas** | Se proponen desde el rendimiento; hay un **tope por oficio dentro del frente** | El planeador confirma |
| **Disparador de fecha** | Precedencia · recurso · **contractual** (el anticipo o la junta de arranque) | Quien programa; lo contractual lo fija el contrato |

*Fuentes:* `MODELO.md` §5c (`ACTIVIDAD`, `TRAMO`, `CALENDARIO_OBRA`, `FRENTE_TOPE_CUADRILLA`) y `PROPUESTA-CUATRO-MODULOS.md` §4. **El patrón que se repite:** Control de obra edita la **estructura** (duraciones y vínculos, función `editar_estructura_programa`) y el residente edita las **fechas;** cada edición se agrega a una bitácora que no se borra, y una versión nueva del programa es otro programa con su traspaso.

#### Lo que el programa le da al resto: las proyecciones

*Diseñadas, sin construir.* El programa multiplicado por la explosión de insumos da **qué se necesita y cuándo:** material por fecha (y de ahí la **fecha de pedido** = inicio de la actividad − tiempo de entrega − holgura), mano de obra por fecha, subcontratos por fecha y el **egreso por fecha, que es el flujo de efectivo.** Salen **con sus supuestos a la vista,** nunca el número solo (`PROPUESTA-CUATRO-MODULOS.md` §4).

#### El arranque: la junta de arranque y lo que se congela

- **Hay fechas que las dispara un contrato y no una precedencia:** `disparador_fecha = contractual` con su `fecha_disparador`, la fija el anticipo o la **junta de arranque.** Es el caso de lo que se contrata terminado. *Aquí el contrato arranca el reloj,* al revés de lo habitual (`MODELO.md` §5c).
- **La obra pasa a `iniciada` cuando alguien la marca** (`MODELO.md` §3c); es una de las dos marcas manuales del estatus, junto con `entregada`.
- **Contratar una rama congela sus fechas:** *las fechas contratadas no se mueven solas;* reprogramar **propone** la fecha nueva y alguien la acepta (P-4, `MODELO.md` §5c).
- **Reprogramar lo contratado es una cadena con salto ✅ (D-533).** El **residente propone, el supervisor revisa y control valida;** o el **supervisor propone y control valida;** y **finalmente Control de obra la realiza y se notifica el cambio a los demás.** Es el molde de la incidencia, con la diferencia de que aquí la realiza Control de obra (`MODELO.md` §5c). *Lectura mía:* es para lo contratado; mientras la rama está en diseño, el residente edita las fechas y Control de obra la estructura.
- **Queda abierto:** quién declara cerrada la junta de arranque (§8.6, hueco 4) y a quiénes se notifica (§8.6, hueco 6).

#### La semana de obra: qué entra y adónde va

| Qué entra | Quién lo registra | Dónde queda | A qué alimenta |
|---|---|---|---|
| **Avance físico** | El **residente** anota la cantidad o el porcentaje, la vía rápida y siempre disponible; el **trazo** de lo realmente construido es opcional y lo hacen control, residente y supervisor (Costos no) ✅ D-533. Se puede anotar **a diario,** o **confirmarse al terminar una actividad** | `REGISTRO_AVANCE` con `fuente = fisico` | El tablero, las alertas de atraso, el cierre de frente y el rendimiento real |
| **Confirmar los avances** (antes de estimar) | El **residente** (D-534), en dos momentos: al terminar una actividad y antes de estimar. Se confirma **al nivel en que se capturó:** por actividad, lo ideal; por su concepto paramétrico, si es paramétrico; y si se capturó por frente en porcentaje, ese porcentaje **se baja a los niveles siguientes, y el usuario decide cómo se reparte** (D-535) | `REGISTRO_AVANCE` (`MODELO.md` §5c). **No es un candado de la estimación (D-535)** | La estimación del residente y el cruce de físico y pagado |
| **Lo que surtió el almacén** | El almacén (ERP externo) | `MOVIMIENTO_ALMACEN` | El cruce contra lo estimado y contra el avance |
| **Incidencias** | Residente, supervisor o control de obra; quien origina no se aprueba a sí mismo y el supervisor da seguimiento hasta cerrar | `INCIDENCIA` | El programa, de tres formas: pausa una actividad, la crea o la hace crecer, o propone una (se aprueba antes de existir) |
| **Control de cambio** | Se origina en una cotización al cliente aceptada o en una incidencia que llega al cliente | `PROPUESTA(tipo=orden_cambio)` | El árbol del presupuesto y, por eso, el programa |
| **Estimación y pago** | Residente (Excel), Control de obra y Compras (§8.7) | `ESTIMACION` y el avance pagado, `REGISTRO_AVANCE` con `fuente = pagado` | El cruce de físico y pagado (§8.5), la retención y los pagos |

**Registrar nunca se bloquea.** Lo ejecutado sin respaldo se registra y queda como una deuda medible con su antigüedad, que tiene dos destinos: se vuelve control de cambio, o es pérdida (`CONOCIMIENTO.md` §13.3). **Físico y pagado no se corrigen entre sí;** su diferencia es la señal y la resuelve Control de obra con evidencia (`CONOCIMIENTO.md` §13.7). **La estimación pagada corrige lo administrativo** (D-534; lectura mía: el registro del avance pagado, no el físico), y por eso confirmar los avances antes de estimar no frena la estimación. **Pero lo estimado por encima de lo confirmado es una alerta importante** (D-535), y su salida es **bajar las cantidades de la estimación.**

#### Lo que se calcula solo: el tablero y las alertas

El **tablero del frente se calcula, no se guarda:** cada cifra de un nodo es la suma de las de sus partidas y se lee a cualquier fecha. Las alertas contestan cuatro preguntas; **todas avisan, ninguna corrige,** nunca se resuelven solas y cuentan cuántas veces se han visto (`MODELO.md` §5a):

| Pregunta | Alertas | Qué la dispara |
|---|---|---|
| **¿Va atrasada?** | `obra_atrasada` · `subfrente_atrasado` · `subfrente_detenido` · `plazo_excedido` · `vinculo_incumplido` | Un día hábil detrás del programa; 21 días sin avance; el cierre pasa del plazo; las fechas contradicen un vínculo |
| **¿Va al ritmo?** | `ritmo_sobre_referencia` · `rendimiento_bajo_para_destajo` · `rendimiento_excede_destajo` · `rendimiento_en_perdida` · `duracion_propia_en_herencia` | El rendimiento real contra el teórico; heredar los días no hereda el ritmo |
| **¿Lo pagado, lo construido y lo surtido coinciden?** | `pago_sin_respaldo_avance` · `avance_sin_respaldo_pago` · `estimacion_sin_respaldo_material` · `consumo_material_sin_respaldo_avance` · `subcontrato_fuera_de_base` | El cruce de las tres corrientes de la semana |
| **¿Ya se puede cerrar, o se pasó?** | `frente_listo_para_cierre` · `ejecutado_sobre_ingenieria` | El frente llega al 90 %; lo ejecutado excede la ingeniería del lote |

*Hoy la bandeja guarda y cuenta las alertas; los detectores están sin construir* (§2.3).

#### Cómo vuelve la ejecución al programa

| Disparador | Qué pasa | La regla |
|---|---|---|
| **Una incidencia** | Cambia cuándo (pausa) o qué (crea o crece una actividad) | Un error de ejecución puede cobrarse al contratista sin tocar el costo y el programa **igual se retrasa:** son dos registros que no dependen uno del otro |
| **Un control de cambio** | Cambia qué hay que construir y, con eso, cuándo | Agrega, no edita; lo contratado no se reescribe |
| **Una fecha nueva de lo contratado** | La propone el residente o el supervisor | **Cadena con salto:** revisa el supervisor (si no fue quien propone), valida y realiza Control de obra, y se notifica a los demás (D-533) |
| **Lo real contra lo teórico** | El rendimiento real da una segunda proyección calculada al vuelo | **Nunca sobrescribe el teórico y nunca reprograma sola:** avisa si diverge más de un umbral (P-7) |
| **Registrar avance** | En una obra sin presupuesto colgado, el programa se reprograma solo con el avance | Solo en ese modo; en los demás, el residente ajusta fechas y Control de obra la estructura |

#### El cierre, y lo que se aprende

**El cierre** va de lo chico a lo grande: al 90 % de un frente el residente solicita, el supervisor aprueba y control valida (con una incidencia de calidad si hace falta); luego, si se requiere, por actividades; y al final **el lote,** con los cuatro participantes en cualquier orden, que lo pasa a `entregada` y a postventa. Cerrar un frente, una actividad o el lote **cierra al residente:** ya no registra avance ahí (`MODELO.md` §5c, D-515, D-516 y D-522).

**Lo que se aprende vuelve por la bandeja,** nunca aplicado solo: el rendimiento real se compara con el teórico y, si el planeador lo decide, lleva a cambiar duraciones (se propone, no se aplica), los precios nuevos entran al catálogo con doble aprobación, y lo medido alimenta al paramétrico y a las plantillas (la red de aprendizaje de arriba).

#### Qué hay hecho de esta mitad

| Pieza | Estado |
|---|---|
| **Programa** (subir, editar estructura o fechas, deshacer) | ✅ Servicios, API y pantalla (`MODELO.md` §5c) |
| **Avance, incidencias, cierre, estimación y almacén** | Diseñado; el avance físico es lo que el piloto de ObraCtrl va a capturar primero (B-126) |
| **Proyecciones** (material, mano de obra, subcontratos y flujo de efectivo) | Diseñadas, sin construir |
| **Alertas** | La bandeja las guarda; los detectores, sin construir |

**Lo que esta mitad deja abierto:** a quiénes se notifica un cambio de fechas (hueco 6) y si Control de obra puede proponer él mismo una reprogramación. **Ya contestado (D-533 a D-535):** quién acepta una fecha nueva de lo contratado (la cadena de arriba), cada cuánto se captura el avance, quién lo registra (el residente la cantidad o el porcentaje; control, residente y supervisor el trazo), quién lo confirma (el residente), a qué nivel (actividad; su concepto paramétrico; o el frente en porcentaje, que se baja y cuyo reparto decide el usuario), y que confirmar no es candado pero lo estimado de más es una alerta importante.

## 8.2 Quién aparece en el flujo

| Quién | Qué hace en el flujo | ¿Es un rol del cerebro? |
|---|---|---|
| **Residente** | Planea su obra y ajusta las fechas del programa; captura el avance; origina incidencias; crea su estimación en Excel y revisa los ajustes; solicita los cierres; entrega la casa; estima hasta el pago de las garantías | ✅ |
| **Supervisor** | Aprueba y cierra incidencias; aprueba el cierre de frente; justifica lo fuera de catálogo; da el visto bueno de la entrega; autoriza liberar la retención | ✅ |
| **Superintendente y equipo de gestión de proyectos** | Firman la entrega de obra (el superintendente puede estar o no). **El equipo de gestión de proyectos es Proyectos y atención al cliente** (D-537) | ✅ el superintendente, con dos funciones (§7, hueco 2) · ✅ el equipo, como Proyectos y atención al cliente |
| **Control de obra** | Recolecta y envía las estimaciones y comparte la final para el pago; la marca pagada; valida cierres y la calidad de la entrega; confirma los pagos de una OT; confirma o modifica su cotización; contrata un bloque | ✅ |
| **Compras** | Validador de topes: revisa los topes, devuelve la estimación, y al modificarla deja la que se paga | ✅ rol nuevo (D-537); `validar_estimacion` ya es suya (D-538) |
| **Finanzas** | Asigna el contratista de un subcontrato | ✅ rol nuevo (D-537) |
| **Proyectos y atención al cliente** | Cotiza y genera la OT; cambia su alcance; atiende al cliente; firma la entrega como equipo de gestión de proyectos | ✅ rol nuevo (D-537) |
| **Atención a postventa** | Atiende los tickets de garantía, los abre en nombre del colono si hace falta y pide su cierre. La postventa será un módulo completo (B-129) | ✅ rol propio (D-541) |
| **Colono** | El dueño de la casa, que es el cliente: abre el ticket de garantía y confirma su cierre con su nivel de satisfacción, de 5 a 10 | ✅ rol (D-542); es un usuario externo |
| **Costos** | Carga el export de OPUS; cuantifica (produce el presupuesto) y propone precios nuevos | ✅ |
| **Cotizador** | Hoy lo ejecuta Control de obra; sería una herramienta (B-123) | 💭 |
| **Contratista** | Más adelante entra como usuario: al cotizador, al programa de ejecución y a su estado de cuenta (B-121) | 💭 |
| **Cliente** | Ya es el colono para la postventa (arriba). Pedir cambios antes y durante la obra **ya está definido** como la petición del cliente, la cotización y el control de cambio (§8.8, punto 3); el módulo de vivienda (B-125) solo sería la puerta para que el colono la entre él mismo | 💭 la puerta |

## 8.3 Las diez etapas

| # | Etapa | Quién hace qué | Qué queda registrado | Dónde está decidido | Marca |
|---|---|---|---|---|---|
| 1 | **Preparar el catálogo y las plantillas** | Costos carga el export de OPUS; Control de obra decide lo detenido y las bajas; Costos propone precios nuevos y Control de obra y Superintendente los aprueban | El catálogo con sus versiones y el presupuesto de cada prototipo como plantilla | §6 (recorrido a) y `MODELO.md` §3 | ✅ sin pantalla |
| 2 | **Dar de alta el lugar** | Proyecto (Magnolia y «Antigua»), clusters o manzanas y lotes: cada casa es una obra, con su prototipo y sus m² adicionales; una urbanización por proyecto | El proyecto, el cluster y la obra con su estatus `pendiente` | `MODELO.md` §3c (D-512, D-520, D-521) | ✅ |
| 3 | **Diseñar el presupuesto de la obra** (D-530) | Al darle de alta, la obra ya es un presupuesto. Se arranca de la base, de una ingeniería o desde cero (§8.1); Costos cuantifica, donde hay plano se mide con el cuantificador (capa de medición) y donde no se estima; se compara la ingeniería del lote contra su prototipo; Control de obra contrata la rama cuando está lista | El presupuesto de la obra con `modo_cantidad` por renglón, `ESTADO_CARGA` y `ESTADO_CONGELAMIENTO` por rama | §8.1; `MODELO.md` §3 y §3a; `CONOCIMIENTO.md` §5.10 y `CONOCIMIENTO.md` §11.7 | ✅ el modelo y que Costos prepara la ingeniería, en Excel y por niveles · ✅ el cuantificador, un motor con dos entradas, y «definido» = costeado |
| 4 | **Programar la obra y asignar a quienes la ejecutan, antes de la junta de arranque** | Se asignan residente y supervisor; se asigna el contratista por obra y tipo de trabajo, y de ahí por etapa o concepto; se cuelga el programa del prototipo y el residente ajusta las fechas; Control de obra contrata un bloque y con eso se fija el precio | `RESIDENTE_OBRA`, `SUPERVISION`, `ASIGNACION_CONTRATISTA`, el programa de la obra y `ESTADO_CONGELAMIENTO` | `MODELO.md` §4a y `MODELO.md` §5c; D-475 y D-512; §8.1, «del programa a la ejecución» | ✅ · ✅ la junta de arranque la declara Control de obra (D-537) |
| 5 | **Contratar un subcontrato (la OT)** | La venta al cliente es un presupuesto o un control de cambio (y antes del control de cambio, una cotización al cliente del cambio o adicional, §8.1); Finanzas asigna el contratista; Proyectos cotiza y genera la OT; Control de obra, después, la confirma o la modifica contra el presupuesto base | `ORDEN_TRABAJO` en `cotizada`, con su `COTIZACION_OT` por versión | `MODELO.md` §5i (D-518 y D-519) | ✅ · 🔶 descuentos y cotizador |
| 6 | **Ejecutar y registrar el avance, cada semana** | El residente captura el avance físico (el sistema propone el porcentaje y se corrige solo lo raro; se anota a diario o se confirma al terminar la actividad, y antes de estimar se confirman los avances); origina incidencias que aprueba el supervisor, valida control, ejecuta el residente y cierra el supervisor; un extra puede pasar a orden de cambio con el cliente; el almacén surte | `REGISTRO_AVANCE` físico, `INCIDENCIA` y `ALERTA` | `CONOCIMIENTO.md` §13.7 y `MODELO.md` §5c | ✅ incluido quién captura y quién confirma el avance (D-533 y D-534) |
| 7 | **Estimar y pagar, cada semana** | *El proceso de hoy (D-538), que se irá puliendo con el sistema:* el residente crea su estimación en Excel; Control de obra la concentra y la envía a Compras; Compras revisa los topes y la devuelve a todos; el residente tiene oportunidad de réplica si alguna cantidad bajó; Costos y Control de obra regresan a Compras las justificaciones de por qué debe subir la cantidad (los supervisores justifican lo fuera de catálogo); Compras modifica, y esa es la que se paga, y se la envía a Control de obra, que establece la estimación pagada. Si lo estimado excede lo confirmado, una alerta importante invita a bajar las cantidades. Los pagos de una OT entran por la estimación, en efectivo o por transferencia, y Control de obra los confirma | `ESTIMACION` de `capturada` a `pagada`, con el oid de cada renglón y su historia; `PAGO_OT` | `MODELO.md` §5d y `MODELO.md` §5i (D-522, D-538 y D-519) | ✅ incluido el validador, que es Compras (D-538) |
| 8 | **Cerrar** | Frente al 90 %: el residente solicita, el supervisor aprueba, control valida; si se requiere, también por actividades; el lote se entrega con los cuatro participantes en cualquier orden; cerrar cierra al residente | `CIERRE_FRENTE`, `CIERRE_ACTIVIDADES` y `ENTREGA_OBRA` | `MODELO.md` §5c (D-515, D-516 y D-522) | ✅ |
| 9 | **Entregar y atender la postventa** | La obra pasa a `entregada` y entra a postventa, **que será un módulo completo con una persona encargada, Atención a postventa** (D-540 y D-541): el colono abre el ticket de garantía (o Atención a postventa en su nombre), Atención a postventa lo atiende y solicita su cierre, y el colono lo confirma con su nivel de satisfacción, de 5 a 10; si no lo confirma tras la tercera re-solicitud, o no queda satisfecho, Control de obra puede aprobar cerrarlo con una nota de insatisfacción o de desatención del colono; hay también OT de postventa y de mantenimiento (con cobro al cliente, por garantía o necesaria para la entrega); la retención se libera al entregar la vivienda o antes si el supervisor lo autoriza; la OT concluye cuando se pagó todo | `TICKET_GARANTIA` y `ORDEN_TRABAJO` | `MODELO.md` §3b y `MODELO.md` §5i | ✅ el mínimo y el ticket · 🔶 el módulo completo, por diseñar (B-129) |
| 10 | **Más adelante** | El cliente pide cambios antes y durante la obra, y postventas y mantenimientos después; el contratista entra al sistema; la entrega puede escalar a un acta de entrega y recepción | — | B-125, B-121 y D-522 | 💭 |

## 8.4 Cómo cambia de estado lo que viaja

| Cosa | Estados | Quién los mueve |
|---|---|---|
| **Rama del presupuesto** (D-530) | `diseño` → `contratado`; y su carga, `incompleto` → `completo` | Control de obra contrata la rama; la carga se marca sola cuando el importe cargado llega al 100 % del vigente |
| **Escenario** (D-530) | candidato → `elegido` o archivado, nunca borrado | Quién lo elige no está dicho; lo elegido se aplica a la obra por rediseño («propone, no aplica»), no la reemplaza (`MODELO.md` §3a) |
| **Obra** | `pendiente` → `iniciada` → `en_proceso` → `por_entregar` → `entregada` y postventa | `iniciada` y `entregada` se marcan; los demás se derivan del avance (desde el 90 %, `por_entregar`) |
| **Estimación** | `capturada` → `enviada` → `devuelta` → `validada` → `pagada` | Control de obra la envía a Compras y establece la pagada; Compras la devuelve y, al modificarla, la deja `validada` |
| **OT** | `cotizada` → `concluida` o `cancelada` | Proyectos la cotiza; el sistema propone concluirla y Proyectos lo confirma |
| **Ticket de garantía** (D-541) | `abierto` → `cierre_solicitado` → `cerrado` *(los nombres de los estados son propuestos)* | El colono lo abre; Atención a postventa solicita el cierre; el colono lo confirma con su nivel de satisfacción, o, tras la tercera re-solicitud sin respuesta o si no queda satisfecho, Control de obra aprueba cerrarlo con una nota de insatisfacción o de desatención del colono (D-542 y D-543) |
| **Incidencia** | `originada` → `aprobada` → `validada` → `ejecutada` → `cerrada`, o `descartada` | Residente y supervisor, control y supervisor; quien origina no se aprueba a sí mismo |
| **Cierre de frente** | solicitado → aprobado → validado | Residente, supervisor y control de obra |

## 8.5 Dónde se cruzan el avance físico y el pagado

Cada semana el flujo produce **dos avances que no se corrigen entre sí:** el **físico,** que captura el residente (etapa 6), y el **pagado,** que sale de la estimación (etapa 7) y que las exportaciones de OP también reflejan (D-525). La diferencia es la señal, y la resuelve Control de obra con evidencia (`CONOCIMIENTO.md` §13.7). Antes del pago, la estimación se cruza además con lo que el almacén surtió (§2.3). Una estimación validada **cierra esa semana de la obra para todos** (B-120, 🔶).

## 8.6 Lo que el flujo todavía no resuelve

| # | Hueco | Quién lo mueve |
|---|---|---|
| 1 | **~~Compras como validador de topes~~ — ✅ cerrado (D-537 y D-538):** rol nuevo, y `validar_estimacion` pasó de Control de obra a Compras | — |
| 2 | **~~Funciones sin clave~~ — ✅ pasadas a la lista de `MODELO.md` §5b (D-537),** las confirmadas y las propuestas. *Quedan sin dueño:* `aplicar_descuento` (B-110) y la revisión de los ajustes que no pasan por topes | — |
| 3 | **Descuentos, traspaso del anticipo y cotizador** (B-110, B-124 y B-123) | El usuario |
| 4 | **~~La junta de arranque~~ — ✅ cerrado (D-537):** la declara Control de obra con `marcar_obra_iniciada`, y eso dispara las fechas contractuales | — |
| 5 | **~~La urbanización~~ — ✅ cerrado en lo esencial (D-540):** sigue el mismo flujo que una casa —presupuesto, programa, avance y estimación—, con cada clúster o amenidad como un frente que se cierra por separado. *Queda:* si tiene entrega y postventa, y a quién (D-523, G3) | — |
| 6 | **~~Los avisos~~ — ✅ la regla de partida de §8.7 queda aceptada (D-540):** se avisa a quien tiene que dar el siguiente paso de la cadena, y a los demás de la obra (el residente, el supervisor y control de obra de esa obra) cuando cambian las fechas. Los avisos siguen siendo plomería de la aplicación (D-516) | — |
| 7 | **~~El cuantificador~~ — ✅ cerrado (D-532):** un motor con dos entradas, la herramienta como ventana flotante que abre el módulo y el espacio de trabajo por nivel o partida grande (§8.1). *Queda abierto:* el umbral de «discrepan mucho» al comprobar un presupuesto y la regla normal de quién traza y quién aprueba | El usuario |
| 8 | **~~Los tipos de presupuesto~~ — ✅ cerrado (D-532 a D-535):** la cotización al cliente es el cuarto valor de `PRESUPUESTO.tipo` y se vuelve control de cambio al aceptarla el cliente. Su precio es **m² × el precio pactado** en una ampliación (17,000 pesos de lista, IVA incluido, **no fijo**) y **la diferencia ÷ 0.7** en algo específico. *Queda por confirmar (B-123):* si el precio varía por proyecto o prototipo, cómo se representa lo que sale, el folio y quién la hace | El usuario |
| 9 | **~~Cuándo está «definido» un presupuesto~~ — ✅ cerrado (D-532):** definido es **costeado**; contratado es otro estado, y contratar la rama es la declaración, de Control de obra (§8.1) | — |
| 10 | **~~La ingeniería del lote~~ — ✅ cerrado (D-531):** la prepara Costos (ingeniería de costos), llega como un Excel, por partes y normalmente por niveles. *Idea 💭:* en algún momento Costos podrá hacerla en esta plataforma | — |
| 11 | **~~Quién acepta una fecha nueva de lo contratado~~ — ✅ cerrado (D-533):** el residente propone, el supervisor revisa y control valida; o el supervisor propone y control valida; y control la realiza y se notifica a los demás (`MODELO.md` §5c) | — |
| 12 | **~~Cada cuánto se captura el avance físico~~ — ✅ contestado (D-533):** a diario, o confirmándolo al terminar la actividad; y antes de estimar se confirman los avances | — |
| 13 | **~~Confirmar los avances antes de estimar~~ — ✅ cerrado (D-534 y D-535):** lo confirma el residente, al nivel en que se capturó (actividad; concepto paramétrico; o el frente en porcentaje, que se baja y cuyo reparto decide el usuario). No es un candado de la estimación, pero lo estimado por encima de lo confirmado es una alerta importante y se pueden bajar las cantidades de la estimación | — |
| 14 | **~~Los roles que faltan~~ — ✅ cerrado (D-537):** Compras, Finanzas, y Proyectos y atención al cliente, que es también el equipo de gestión de proyectos | — |
| 15 | **~~Los dueños de 26 funciones~~ — ✅ pasados a `MODELO.md` §5b (D-537 y D-538).** Control de obra pasa de 22 a 28 funciones con lo confirmado y a 34 con lo propuesto (§8.7) | — |
| 16 | **~~La estimación, para pulir con el sistema~~ — ✅ contestado (D-539):** la réplica y las justificaciones pueden dar más de una vuelta; la justificación va en el renglón del concepto, como una celda de texto, y también la de lo fuera de catálogo. *Lo demás se pule con el sistema* (D-538) | — |

## 8.7 Los roles paso por paso (D-536 y D-537)

**Pedido del usuario (D-536):** «Sí, seguimos con los roles paso por paso». Cada etapa de §8.3 se abre en sus pasos, y cada paso dice **quién lo hace, con qué función y en qué estado está esa asignación.** Todo sale de lo ya decidido (`MODELO.md` §5b y las funciones de D-533) y de las propuestas que ya había (B-115, B-118 y `MODELO.md` §5i). **D-537:** el usuario contestó tres de las cuatro decisiones —los **tres roles nuevos** (Compras, Finanzas, y Proyectos y atención al cliente), que **el equipo de gestión de proyectos es Proyectos y atención al cliente,** y **Control de obra como dueño** del alta, el contratista, el precio pactado, el arranque y el control de cambio—, y las funciones pasaron a la lista de `MODELO.md` §5b, las confirmadas y las propuestas, cada una marcada. Falta la cuarta, la de la estimación.

Marcas: ✅ rol y función asignados y confirmados · 🔶 dicho o propuesto, con la clave o el rol sin confirmar · ❓ falta el dueño o la clave · ⚙ no es una persona del cerebro. Donde actúa el Supervisor, el Superintendente podría hacerlo igual (§7, hueco 2; recomendación: hereda).

**Etapa 1 · Preparar el catálogo y las plantillas**

| Paso | Quién | Función | Estado | Nota |
|---|---|---|---|---|
| Cargar el export de OPUS y decidir lo detenido y las bajas al reconciliar | Costos y Control de obra | `cargar_catalogo_opus` | 🔶 | Propuesta de D-473; la misma carga cubre la reconciliación (D-476) |
| Proponer un precio nuevo | Costos | `proponer_precio_nuevo` | ✅ |  |
| Aprobar el precio nuevo | Control de obra **y** Superintendente, los dos | `aprobar_precio_nuevo` | ✅ | Doble aprobación obligatoria |
| Clonar un insumo o corregir un prefijo | Control de obra | `clonar_insumo` | 🔶 | Propuesta de D-478: cambia lo que citan los conceptos de todas las obras |
| Reclasificar una familia o resolver un parámetro por revisar | Control de obra | `reclasificar_familia` · `resolver_revisar_parametro` | 🔶 | Menos firme |

**Etapa 2 · Dar de alta el lugar**

| Paso | Quién | Función | Estado | Nota |
|---|---|---|---|---|
| Crear el proyecto, el cluster (o la manzana) y la obra, con su prototipo y sus m² adicionales | Control de obra | `dar_de_alta_obra` | ✅ | Confirmado en D-537. Crear la obra es crear su presupuesto (§8.1) |

**Etapa 3 · Diseñar el presupuesto de la obra**

| Paso | Quién | Función | Estado | Nota |
|---|---|---|---|---|
| Cargar la ingeniería del lote (el Excel de Costos, por niveles) | Costos *(la prepara; que la cargue también es mi lectura)* | `cargar_ingenieria` | 🔶 | `cargar_catalogo_opus` es del catálogo y los presupuestos de OPUS |
| Trazar sobre el plano | Costos, Control de obra, Residente y Supervisor | `trazar` | ✅ |  |
| Aprobar el trazo | Control de obra | `aprobar_trazo` | ✅ |  |
| Anotar el plano | Residente y Supervisor | `anotar_plano` | ✅ |  |
| Resolver una alerta de comparación (diferencia sin causa, identidad dudosa) | Supervisor y Control de obra | `resolver_alerta` | 🔶 | Propuesta de D-485 |
| Contratar la rama: fija los PU y la congela | Control de obra | `contratar_subarbol` | 🔶 | Propuesta de D-475 |

**Etapa 4 · Programar y asignar, hasta la junta de arranque**

| Paso | Quién | Función | Estado | Nota |
|---|---|---|---|---|
| Asignar al residente | Control de obra | `asignar_residente` | ✅ |  |
| Asignar la supervisión | Control de obra | `asignar_supervision` | ✅ |  |
| Asignar al contratista, por obra y tipo de trabajo y de ahí por etapa o concepto | Control de obra *(el de un subcontrato lo asigna Finanzas)* | `asignar_contratista` | ✅ | Confirmado en D-537. `MODELO.md` §4a |
| Pactar el precio con el contratista | Control de obra | `pactar_precio_contratista` | ✅ | Asignada en D-537 (existía sin dueño desde P-21) |
| Colgar el programa del prototipo y editar su estructura | Control de obra | `editar_estructura_programa` | ✅ | También subir un programa (D-466) |
| Ajustar las fechas del programa | Residente | `editar_fechas_programa` | ✅ |  |
| Declarar la junta de arranque y marcar la obra `iniciada` | Control de obra | `marcar_obra_iniciada` | ✅ | Confirmado en D-537. Dispara las fechas contractuales (§8.1) |

**Etapa 5 · Contratar un subcontrato (OT) y cotizar al cliente**

| Paso | Quién | Función | Estado | Nota |
|---|---|---|---|---|
| Cotizar al cliente un cambio o adicional (Highlight o Adicional) | Control de obra *(hoy, como cotizador)* | `cotizar_cambio_cliente` | 🔶 | El cotizador no es un rol activo |
| Autorizar el control de cambio cuando el cliente acepta | Control de obra | `autorizar_orden_cambio` | ✅ | Asignada en D-537. *Idea, sin confirmar:* doble, con el Superintendente |
| Asignar al contratista de un subcontrato | Finanzas | `asignar_subcontrato` | ✅ | Rol confirmado en D-537 |
| Cotizar y generar la OT; cambiar su alcance | Proyectos y atención al cliente | `cotizar_ot` · `cambiar_alcance_ot` | ✅ | Va primero Proyectos y después Control (D-519). Rol confirmado en D-537 |
| Confirmar o modificar la cotización contra el presupuesto base; auditar el cambio de alcance | Control de obra | `auditar_alcance_ot` | 🔶 | Propuesta de `MODELO.md` §5i |
| Confirmar los pagos de una OT | Control de obra | `confirmar_pago_ot` | 🔶 | Propuesta de `MODELO.md` §5i |
| Autorizar liberar la retención | Supervisor; Control de obra la valida si hace falta | `liberar_retencion` | 🔶 | `MODELO.md` §5i |

**Etapa 6 · Ejecutar y registrar el avance, cada semana**

| Paso | Quién | Función | Estado | Nota |
|---|---|---|---|---|
| Anotar la cantidad o el porcentaje del avance | Residente | `registrar_avance` | ✅ | D-533 |
| Trazar el avance | Control de obra, Residente y Supervisor; Costos no | `trazar_avance` | 🔶 | El rol lo dijo el usuario (D-533); la clave es propuesta |
| Confirmar los avances: al terminar la actividad y antes de estimar | Residente | `confirmar_avance` | 🔶 | El rol lo dijo el usuario (D-534); la clave es propuesta |
| Originar una incidencia | Residente, Supervisor o Control de obra | `originar_incidencia` | ✅ |  |
| Aprobar la incidencia | Supervisor | `aprobar_incidencia` | ✅ | Quien origina no se aprueba a sí mismo |
| Validar la incidencia en sitio | Control de obra | `validar_incidencia` | ✅ |  |
| Ejecutar la incidencia | Residente | `ejecutar_incidencia` | ✅ |  |
| Cerrar la incidencia | Supervisor | `cerrar_incidencia` | ✅ | Da seguimiento hasta cerrar |
| Proponer, revisar, validar y realizar una fecha nueva de lo contratado | Residente o Supervisor · Supervisor · Control de obra · Control de obra | `proponer_reprogramacion` · `revisar_reprogramacion` · `validar_reprogramacion` · `aplicar_reprogramacion` | 🔶 | Los roles los dijo el usuario (D-533); las claves son propuestas |
| Resolver una alerta de atraso, de ritmo o de respaldo | Supervisor y Control de obra | `resolver_alerta` | 🔶 | Propuesta de D-485 |
| Surtir el almacén | El almacén *(ERP externo)* | — | ⚙ | No es un usuario del cerebro |

**Etapa 7 · Estimar y pagar, cada semana** *(el proceso de hoy, D-538)*

| Paso | Quién | Función | Estado | Nota |
|---|---|---|---|---|
| Crear la estimación (en Excel) | Residente | `capturar_estimacion` | ✅ | D-538 |
| Concentrarla (recolectar y pasar por el extractor) y enviarla a Compras | Control de obra | `enviar_estimacion` | ✅ | D-538 |
| Revisar los topes | Compras | `validar_estimacion` | ✅ | D-538: pasó de Control de obra a Compras |
| Devolverla a todos | Compras | `devolver_estimacion` | ✅ | D-538. *Todos:* residentes, supervisores, Costos y Control de obra |
| Réplica, si alguna cantidad bajó | Residente | `replicar_estimacion` | 🔶 | El rol lo dijo el usuario (D-538); la clave es propuesta. Puede dar más de una vuelta (D-539). Se apoya en la alerta de lo estimado de más (D-535) |
| Regresar a Compras las justificaciones de por qué debe subir la cantidad | Costos y Control de obra | `justificar_aumento_cantidad` | 🔶 | Los roles los dijo el usuario (D-538); la clave es propuesta. Va en la celda de texto del renglón del concepto (D-539) |
| Justificar lo fuera de catálogo | Supervisor | `justificar_fuera_de_catalogo` | 🔶 | D-522. Va en la misma celda de texto del renglón (D-539), que es firme |
| Modificar la estimación (es la que se paga) y enviarla a Control de obra | Compras | `validar_estimacion` | ✅ | D-538 |
| Establecer la estimación pagada | Control de obra | `marcar_estimacion_pagada` | ✅ | D-538. Propuesta de B-118 |
| Aplicar un descuento o una deducción | ❓ | `aplicar_descuento` | ❓ | Existe sin dueño desde P-21; esperan los descuentos (B-110) |

**Etapa 8 · Cerrar**

| Paso | Quién | Función | Estado | Nota |
|---|---|---|---|---|
| Solicitar el cierre del frente, al 90 % | Residente | `solicitar_cierre_frente` | ✅ |  |
| Aprobar el cierre del frente | Supervisor | `aprobar_cierre_frente` | ✅ |  |
| Validar el cierre del frente | Control de obra | `validar_cierre_frente` | ✅ |  |
| Cerrar por una o varias actividades, si se requiere | Residente · Supervisor · Control de obra: las mismas manos | las tres de arriba *(lectura mía)* | 🔶 | `MODELO.md` §5c, D-522 |
| Entregar la obra | Residente | `entregar_obra` | 🔶 | En cualquier orden; la obra queda entregada cuando participan los cuatro |
| Dar el visto bueno de la entrega | Supervisor | `dar_visto_bueno_entrega` | 🔶 |  |
| Revisar la calidad y el expediente de la entrega | Control de obra | `validar_calidad_entrega` | 🔶 |  |
| Firmar la entrega | Proyectos y atención al cliente: es el equipo de gestión de proyectos | `firmar_entrega` | ✅ | Confirmado en D-537 |
| Firmar la entrega, si está | Superintendente | `firmar_entrega_superintendente` | 🔶 | Puede estar o no (D-522) |

**Etapa 9 · Entregar y atender la postventa** *(la postventa será un módulo completo, D-540 a D-542)*

| Paso | Quién | Función | Estado | Nota |
|---|---|---|---|---|
| Pasar la obra a `entregada` y a postventa | El sistema, cuando participan los cuatro de la entrega | — | ⚙ | `MODELO.md` §3c y §3b |
| Abrir el ticket de garantía | El colono: el dueño de la casa; o Atención a postventa en su nombre | `abrir_ticket_garantia` | ✅ | D-541 y D-542 |
| Atender el ticket y, si hace falta un trabajo, generar la OT de postventa o de mantenimiento | Atención a postventa *(lectura mía)* | `cotizar_ot` | 🔶 | El módulo lo definirá |
| Solicitar el cierre del ticket | Atención a postventa | `solicitar_cierre_ticket` | 🔶 | El rol lo dijo el usuario (D-541); la clave es propuesta |
| Re-solicitar la confirmación al colono, hasta la tercera re-solicitud (D-543) | El sistema | — | ⚙ | Es un parámetro; cada cuánto no se dijo |
| Confirmar el cierre con el nivel de satisfacción, de 5 a 10 | El colono | `confirmar_cierre_ticket` | 🔶 | El rol y la escala los dijo el usuario (D-541 y D-542); la clave es propuesta |
| Si el colono no confirma tras la tercera re-solicitud o no queda satisfecho: aprobar cerrarlo con una nota de insatisfacción o de desatención | Control de obra | `aprobar_cierre_ticket_sin_confirmar` | 🔶 | El rol lo dijo el usuario (D-542); la clave es propuesta |
| Concluir la OT cuando se pagó todo | El sistema lo propone y Atención a postventa lo confirma *(lectura mía)* | propuesta de `MODELO.md` §5i | 🔶 | Los residentes estiman hasta el pago de la garantía |

### Qué dice el conjunto

De los **64 pasos,** 33 están ✅, 27 son 🔶, 1 está ❓ y 3 son ⚙. Con D-537 y D-538 los pasos del arranque, de la OT y de la estimación tienen dueño. **El único ❓ son los descuentos,** que esperan a B-110. La postventa es la más provisional: será un módulo completo (D-540 a D-543).

### Los roles nuevos (D-537)

`ROL` pasa de seis a **nueve**, y con la postventa (D-540 a D-542) a **once**: Atención a postventa y el colono (la clave de máquina entre paréntesis, como `control_de_obra`). Los usuarios pueden tener varios roles a la vez (`USUARIO_ROL`).

| Rol | Qué hace | Estado |
|---|---|---|
| **Compras** (`compras`) | El validador de topes: `validar_estimacion` y `devolver_estimacion` | ✅ El rol y sus dos funciones (D-538) |
| **Finanzas** (`finanzas`) | `asignar_subcontrato`: asigna al contratista de un subcontrato | ✅ |
| **Proyectos y atención al cliente** (`proyectos`) | `cotizar_ot` y `cambiar_alcance_ot` y, como equipo de gestión de proyectos, `firmar_entrega` | ✅ |
| **Atención a postventa** (`atencion_postventa`) | La persona encargada de postventa: atiende los tickets de garantía, los abre en nombre del colono (`abrir_ticket_garantia`) y solicita su cierre (`solicitar_cierre_ticket`) | ✅ El rol (D-541); 🔶 la clave de la segunda función |
| **Colono** (`colono`) | El dueño de la casa, que es el cliente: `abrir_ticket_garantia` y `confirmar_cierre_ticket`, con su nivel de satisfacción de 5 a 10 | ✅ El rol (D-542): un usuario externo que ve solo su casa; 🔶 la clave de la segunda función |
| **Cotizador** | Cotizar al cliente un cambio o adicional | Sin activar: Control de obra lo hace hoy (B-123) |

*El código no cambia (D-487):* la migración de permisos solo siembra los seis roles de antes y las dos funciones del programa; los tres roles nuevos y sus funciones se siembran cuando se levante D-487.

### Las funciones nuevas y su dueño

Las veintiocho funciones nuevas (veintitrés de D-537, dos de D-538, dos de D-541 y una de D-542) y las dos que existían sin dueño (`pactar_precio_contratista` y `autorizar_orden_cambio`) ya están en la lista de `MODELO.md` §5b. `aplicar_descuento` sigue sin dueño hasta que se resuelvan los descuentos (B-110).

| Función | Dueño | Estado |
|---|---|---|
| `dar_de_alta_obra` · `asignar_contratista` · `pactar_precio_contratista` · `marcar_obra_iniciada` · `autorizar_orden_cambio` | Control de obra | ✅ D-537 |
| `asignar_subcontrato` | Finanzas | ✅ D-537 |
| `cotizar_ot` · `cambiar_alcance_ot` · `firmar_entrega` | Proyectos y atención al cliente | ✅ D-537 |
| `abrir_ticket_garantia` · `confirmar_cierre_ticket` | Colono (la primera, también Atención a postventa en su nombre) | ✅ la primera (D-541 y D-542) · 🔶 la segunda |
| `solicitar_cierre_ticket` | Atención a postventa | 🔶 D-541 |
| `aprobar_cierre_ticket_sin_confirmar` | Control de obra | 🔶 D-542 |
| `cargar_ingenieria` · `justificar_aumento_cantidad` | Costos | 🔶 |
| `enviar_estimacion` · `marcar_estimacion_pagada` | Control de obra | ✅ D-538 |
| `cotizar_cambio_cliente` · `validar_calidad_entrega` · `confirmar_pago_ot` · `auditar_alcance_ot` · `justificar_aumento_cantidad` *(con Costos)* | Control de obra | 🔶 |
| `capturar_estimacion` | Residente | ✅ D-538 |
| `confirmar_avance` · `replicar_estimacion` · `entregar_obra` | Residente | 🔶 |
| `justificar_fuera_de_catalogo` · `dar_visto_bueno_entrega` | Supervisor | 🔶 |
| `liberar_retencion` | Supervisor la autoriza; Control de obra la valida si hace falta | 🔶 |
| `validar_estimacion` *(pasó de Control de obra)* · `devolver_estimacion` | Compras | ✅ D-538 |
| `firmar_entrega_superintendente` | Superintendente | 🔶 |

**Una advertencia de diseño.** Con lo confirmado Control de obra pasa de **22 a 28 funciones** (gana siete y pierde `validar_estimacion`, que pasó a Compras), y con lo propuesto, a **34.** Sale de la regla que ya existe, el gobierno cruzado entre obras (D-330), pero junta en una sola mano el alta de obras, los contratistas, el arranque, el control de cambio, el envío y el pago de las estimaciones. Si en la práctica eso es un cuello de botella, el remedio no cambia el esquema: es reasignar filas de `ROL_FUNCION`.

### Los avisos: una regla de partida

El cerebro dejó los avisos fuera como plomería de la aplicación (D-516), y así sigue: **solo anota a quién le toca enterarse cuando el usuario lo dice.** Lo único dicho (D-533): al aplicarse una reprogramación se avisa **a los demás.** *Regla de partida, mía, para que la app la use mientras el usuario decide:* se avisa **a quien tiene que dar el siguiente paso de la cadena,** y a los demás de la obra cuando cambian las fechas. Por ejemplo:

| Qué pasó | A quién se avisa |
|---|---|
| Se aplicó una reprogramación | A los demás de la obra: el residente, el supervisor y control de obra de esa obra *(quiénes son no se dijo)* |
| Un paso de una incidencia o de un cierre | Al que sigue en la cadena; al cerrar, a quienes participaron |
| Se envió, se devolvió, se validó o se pagó una estimación | Al que sigue; si se devuelve, al residente y al supervisor; si se paga, a ellos también |
| Hay una alerta nueva, sobre todo la de lo estimado de más | A quienes la resuelven: supervisor y control de obra |
| Se contrató una rama | Al residente y al supervisor de la obra |
| Se propuso un precio nuevo | A quienes lo aprueban: control de obra y superintendente |
| El cliente aceptó una cotización | A quien autoriza el control de cambio: Control de obra |

### Lo que falta del usuario

1. **A quiénes se avisa** cuando cambian las fechas (hueco 6).
2. **El orden de las etapas** (de D-529).
3. **Pulir la estimación con el sistema,** sin prisa: el usuario dijo que este es el proceso de hoy y que se irá puliendo. Las dudas de D-538 (las vueltas, dónde va la justificación y si los supervisores siguen justificando lo fuera de catálogo) quedaron contestadas en D-539.

## 8.8 Dónde queda el App flow (D-539 y D-540)

**D-539:** las **pantallas son de las apps** y no se escriben en el cerebro. **D-540:** el usuario revisó los seis puntos que quedaban, aceptó cinco («todo lo demás correcto») y precisó la postventa. **D-541:** precisó quién abre el ticket y cómo se cierra. **D-542:** confirmó el colono, la escala de la satisfacción, el cierre sin confirmación y que pedir cambios ya estaba definido. **El App flow queda cerrado en el cerebro.** Lo que tiene, de lo más general a lo más fino:

| Capa | Dónde | Estado |
|---|---|---|
| La cadena de la información: presupuesto, programa y ejecución, y sus redes | §8.1 | ✅ |
| El diseño del presupuesto, los tipos y el cuantificador | §8.1 | ✅ |
| La cotización al cliente y el control de cambio | §8.1 y `MODELO.md` §3a | ✅ |
| Del programa a la ejecución, con el avance, su confirmación y la reprogramación | §8.1, `MODELO.md` §5c | ✅ |
| Las diez etapas, los estados y los roles paso por paso | §8.3, §8.4 y §8.7 | ✅ |
| La estimación, como la hace hoy la empresa | `MODELO.md` §5d y §8.7 | ✅ El proceso de hoy, que se irá puliendo con el sistema |

**Los seis puntos, como quedaron (D-540):**

| # | Qué | Cómo quedó | Estado |
|---|---|---|---|
| 1 | **El orden de las etapas** | Las diez son un **orden de dependencia, no de calendario:** cada rama avanza a su paso, y la OT (5) puede ocurrir en cualquier momento entre la planeación y la postventa. Esquema abajo | ✅ |
| 2 | **Los avisos** | Se avisa a quien da el siguiente paso, y a los demás de la obra cuando cambian las fechas (regla de §8.7) | ✅ |
| 3 | **La petición del cliente** de un cambio o adicional | Proyectos y atención al cliente la recibe y la registra; Control de obra cotiza (hoy hace de cotizador); el cliente la acepta; Control de obra autoriza el control de cambio. **Es lo que el módulo de vivienda llamaba «pedir cambios antes y durante la obra»** (D-542): ya estaba definido, y el módulo solo sería la puerta para que el colono la entre él mismo | ✅ |
| 4 | **La urbanización** | Sigue el mismo flujo que una casa, con cada clúster o amenidad como un frente que se cierra por separado. *Queda:* si tiene entrega y postventa, y a quién | ✅ en lo esencial |
| 5 | **La postventa** | **Será un módulo completo, con una persona encargada: Atención a postventa, un rol propio** (D-540 y D-541). **Lo abre el dueño de la casa, que es el cliente y se llama colono** (o Atención a postventa en su nombre); **se cierra a solicitud de Atención a postventa, confirmando el colono con su nivel de satisfacción, de 5 a 10; y si no confirma o no queda satisfecho, Control de obra puede aprobar cerrarlo con una nota de insatisfacción o de desatención del colono, la desatención después de la tercera re-solicitud** (D-542 y D-543). El detalle —cada cuánto se re-solicita, cómo llega a una OT— se diseña con el módulo (B-129) | ✅ el flujo y los roles · 🔶 las claves |
| 6 | **El cierre de semana** | Se cierra al pasar la estimación a `validada` (cuando Compras la modifica), y lo anterior sigue abierto (D-517) | ✅ |

**El orden de las etapas, como quedó:**

```
 1 catálogo ─► 2 lugar ─► 3 presupuesto ─► 4 programar y asignar ─► (junta de arranque)
                                │                                           │
                                └──── por rama: una rama puede estar en 6 mientras otra sigue en 3
                                                                            ▼
                                                   6 avance ⇄ 7 estimar y pagar   (cada semana)
                                                                            ▼
                                           8 cerrar: frente → actividades → lote ─► 9 entregar y postventa
        5 la OT y la cotización al cliente: en cualquier momento, de la etapa 4 a la 9
```

**No son del App flow, aunque lo tocan:** el módulo de postventa (B-129), los descuentos y el traspaso del anticipo (B-110 y B-124, cada uno con sus preguntas), los campos del expediente y la revisión física (B-120) y el contratista y el cliente como usuarios (B-121 y B-125, ideas). Se resuelven aparte.
