# ÍNDICE

```
órgano:     cuerpo calloso — conecta las capas, no pertenece a ninguna
capa:       —
pregunta:   ¿dónde va cada cosa?
corte:      2026-10-12
```

> **Regla de oro: cada hecho vive en un solo archivo. Los demás lo referencian.**
>
> Si algo aparece explicado en dos lugares, tarde o temprano se separan y uno miente.

---

# Las cuatro capas

El corte no se inventó: **es el tiempo verbal** que esta tabla ya usaba sin
nombrarlo.

| Capa | Tiempo | Qué contiene | Archivos |
|---|---|---|---|
| **I · Mundo** | *Es así* | El modelo de la realidad | `CONOCIMIENTO` · `CATALOGOS` · `MODELO` · `PROGRAMA-CPM` · `LENGUAJE` · `GLOSARIO` · `DICCIONARIO-DATOS` |
| **II · Operación** | *Se hace así* | Cómo se razona y cómo se actúa. Reflejo, sin deliberar | `METODO` · `METACOGNICION` · `RAZONAMIENTO` · `INVARIANTES` · `ESCALABILIDAD` · `WORKFLOWS` · `skills/` · `agentes/` |
| **III · Historia** | *Fue así* | Lo consolidado y lo que enseñó | `MEMORIA` · `CASO-TRABAJADO` · `APRENDIZAJE` |
| **IV · Dirección** | *Vamos aquí* | Dónde estoy, qué falta, qué merece el enfoque | `ESTADO` · `PENDIENTES` · `PRIORIDADES` · `IDEAS` · `PROPUESTA-…` |

### Cada archivo numera desde 1

**Ningún archivo depende de la numeración de otro.** Agregar o quitar una sección en
`CATALOGOS.md` no mueve nada en `CONOCIMIENTO.md`, y viceversa.

El precio es que **toda referencia cruzada lleva su archivo** —`` `CONOCIMIENTO.md` §11.9 ``,
no `§12.9`— y eso el verificador lo comprueba en cada corrida. Una referencia interna
va sin archivo: `§3.2` dentro de su propio archivo es legible y no se rompe.

### La estructura en disco

```
cerebro/
├── README.md                  ← puerta de entrada del repositorio
├── INDICE.md                  ← fuera de las capas: las conecta
├── 1-mundo/                   CONOCIMIENTO · CATALOGOS · MODELO · PROGRAMA-CPM · LENGUAJE · GLOSARIO · DICCIONARIO-DATOS
│   ├── programas/             los siete programas y sus listas, en CSV (13 archivos)
│   ├── opus/                  los archivos de OPUS que sí hay, tal cual: presupuesto, matrices, los cinco catálogos de D-527 y D-528 e ingenierías de ALAMO 18 (24 archivos)
│   └── fuentes/               las demás tablas que el usuario compartió, a salvo (D-479): almacén, avance, precio real, semilla y programa, cada libro tal cual y cada hoja en CSV, con su MANIFIESTO de huellas
├── 2-operacion/               METODO · METACOGNICION · RAZONAMIENTO · INVARIANTES · ESCALABILIDAD · WORKFLOWS
│   ├── verificar-cerebro.py    ← comprueba lo de abajo contra sí mismo
│   ├── red-del-cerebro.py      ← mide cómo está conectado: referencias, cambios que van juntos, qué se lee primero, a quién releer (--vigencia), cuánto se puede partir (--integracion), si lo compilado oye a su fuente (--reentrada)
│   ├── preparar-para-github.py ← revisa la carpeta de una app, aparta claves y datos reales y la deja lista para subir a GitHub (D-496)
│   ├── skills/                erp-construccion + importacion · rediseno · parametrico · cuantificador · programa
│   └── agentes/               gravity (orquesta) · arquitecto · constructor · migrador · auditor
│                               gravity-obra (interno, Agent SDK)
├── 3-historia/                MEMORIA · CASO-TRABAJADO · APRENDIZAJE · PRUEBA-* (3)
├── 4-direccion/               ESTADO · PENDIENTES · PRIORIDADES · IDEAS · PROPUESTA-…
├── backend/                   el código que el cerebro especifica: core/ (motor_calculo · motor_cpm · programa · servicio_programa · accesos · importacion_opus · catalogo · colgado · contratacion · reconciliacion · texto · clonacion · propuestas · fuentes, con sus pruebas) · infra/ (adaptadores de Postgres y la conexión por hilo) · api/ (FastAPI: el programa, el catálogo con sus presupuestos y la bandeja, autenticación por token, el cliente generado, servir y las terminales) · requirements.txt
├── database/migraciones/      el esquema, en SQL: 0001_programa.sql · 0002_programa_importado_por.sql · 0003_version_nueva_del_programa.sql · 0004_usuarios_y_permisos.sql · 0005_catalogo_apu_presupuesto.sql · 0006_programa_cuelga_del_presupuesto.sql · 0007_estado_de_congelamiento.sql · 0008_reconciliar_un_presupuesto.sql · 0009_clonar_un_insumo.sql · 0010_bandeja_de_propuestas.sql
└── frontend/gantt/            las pantallas del programa: gantt.html · programas.html (la lista y subir uno) · tokens.css (los colores) · motor_gantt.js (reprograma en el navegador; una prueba lo contrasta con Python) · cliente_programa.js (generado del spec de la API) · sesion.js (quién eres, compartida por las pantallas)
```

**Este archivo queda fuera de las cuatro.** Un órgano que se clasifica a sí mismo
dentro de lo que clasifica ya no puede arbitrar.

### Las dos velocidades

La Capa II es la **rápida**: detecta, no pide permiso, `Decimal` nunca `float`, el
rollup cuadra o truena. Las Capas I y III son la **lenta**: deliberan, exigen
evidencia, esperan aprobación.

No es una metáfora agregada — es `CONOCIMIENTO.md` §14.4 textual: *la detección
nunca necesita permiso; la corrección siempre.*

---

# El bloque de órgano

Cada archivo del cerebro abre con esto. Da la anatomía **sin renombrar nada** — el
nombre sigue diciendo dónde va un hecho, que es lo único que hay que saber a
diario.

```
órgano:     hipocampo
capa:       III — Historia
pregunta:   ¿qué decidimos, qué descartamos?
tiempo:     fue así
corte:      2026-09-10
verificado: MEMORIA §2 · 13 descartes
```

**Las dos últimas líneas son el registro de vigencia.** Una regla sin corte y sin
fuente no es regla verificada: es una creencia con buena redacción. Por eso la
caducidad no necesita archivo propio — vive en el encabezado de cada uno.

---

# La pregunta que decide dónde va cada cosa

| Archivo | Capa | Responde | Órgano |
|---|---|---|---|
| **ESTADO** | IV | ¿Dónde vamos y cómo retomar? | Propiocepción |
| **MÉTODO** | II | ¿Cómo se piensa aquí? · identidad | Función ejecutiva |
| **RAZONAMIENTO** | II | ¿Cómo se responde una pregunta que el cerebro no tiene guardada? | Corteza prefrontal |
| **METACOGNICION** | II | ¿Qué sabe el cerebro de sí mismo y cómo le llega a cada parte lo que cambia? | Corteza prefrontal anterior |
| **CONOCIMIENTO** | I | ¿Cómo funciona el sistema? | Corteza asociativa |
| **CATALOGOS** | I | ¿Qué trae cada catálogo de origen? | Memoria perceptiva |
| **MODELO** | I | ¿Qué forma tienen los datos? | Esquema corporal |
| **PROGRAMA-CPM** | I | ¿Cómo se calcula el programa y qué cifras lo prueban? | Cerebelo |
| **LENGUAJE** | I | ¿Cómo se nombra en cada sistema? | Área de Wernicke |
| **GLOSARIO** | I | ¿Cómo lo dicen las personas? | Léxico social |
| **DICCIONARIO-DATOS** | I | Los renglones concretos a corregir | — |
| **MEMORIA** | III | ¿Qué decidimos, descartamos, erramos? | Hipocampo |
| **CASO-TRABAJADO** | III | ¿Cómo se ve todo junto, sobre datos reales? | Memoria episódica |
| **PRUEBA-…** | III | ¿El sistema aguanta sobre datos reales? Tres pruebas | Memoria episódica — prueba |
| **APRENDIZAJE** | III | ¿Cómo lo aprobado cambia lo que creemos? | Lazo hebbiano |
| **SKILL** | II | ¿Qué respetar al construir? | Reflejo medular |
| **ESCALABILIDAD** | II | ¿Cómo se agrega un módulo nuevo? | Plasticidad |
| **WORKFLOWS** | II | ¿Cómo trabajan juntos las personas, el sistema, el agente interno y las skills? | Comisuras |
| **INVARIANTES** | II | ¿Esto sigue cuadrando? ¿Ya terminé? | Nocicepción |
| **PENDIENTES** | IV | ¿Qué falta? | Cola de impulsos |
| **PRIORIDADES** | IV | ¿En qué se gasta el enfoque? | Atención selectiva |
| **IDEAS** | IV | ¿Qué se pensó y aún no se diseña? | — |
| **PROPUESTA-…** | IV | ¿Qué se propone construir? | — |
| **agentes/** | II | **Orquesta** · planea · ejecuta · percibe · audita | Prefrontal, premotora, motora, sensorial y nociceptiva |

---

# Dónde va cada cosa, con ejemplos

| Si es… | Va a | Ejemplo |
|---|---|---|
| Un hecho verificado de los datos | CONOCIMIENTO | *«Los 467 conceptos cuadran al centavo»* |
| Una regla del modelo | CONOCIMIENTO | *«El borrado no baja»* |
| **Una cifra contra la cual comprobar** | **INVARIANTES** | *«665 nodos con hijos, 665 cuadran»* |
| Cómo un sistema nombra un campo | LENGUAJE | *«OPUS llama `Tipo` a la categoría»* |
| Una decisión tomada | MEMORIA | *«El descuento no reescribe el precio pactado»* |
| Una opción **descartada** | MEMORIA | *«`%MO` como campo: descartado»* |
| Un error que se corrigió | MEMORIA | *«Se creyó que la trabe era auxiliar»* |
| **Una propuesta resuelta que cambió una regla** | **APRENDIZAJE** | *«Se aprobó el 1.085; por eso el APU cambió»* |
| Algo por decidir | PENDIENTES | *«¿El concepto lleva clasificación?»* |
| Algo por hacer, ya decidido | PENDIENTES | *«Normalizar unidades de conceptos»* |
| **Por qué eso va antes que aquello** | **PRIORIDADES** | *«Barato hoy, carísimo en dos meses»* |
| Un sinónimo del oficio | GLOSARIO | *«Actividad = Concepto»* |
| Una errata concreta a corregir | DICCIONARIO-DATOS | *«`nescesario` → necesario, ×32»* |
| Una regla para quien programa | SKILL | *«`Decimal`, nunca `float`»* |
| Cómo se averigua algo | MÉTODO | *«Hay que calcular con el catálogo, no leerlo»* |
| Una entidad del esquema | MODELO | *«`reporta_a` vive en la línea, no en el insumo»* |
| Los datos de un programa, su red, su ruta o el motor que los calcula | PROGRAMA-CPM | *«La ruta de relevos de Zafiro son 28 pasos»* |
| Un módulo propuesto y sin aprobar | PROPUESTA | *«El factorizador primero»* |
| **Cómo encaja un módulo que no existe** | **ESCALABILIDAD** | *«¿Qué dimensión agrega y de qué nodos cuelga?»* |
| **Cómo se relacionan personas, sistema, agente y skills** | **WORKFLOWS** | *«Aprobar una propuesta pide la función de la acción que propone»* |

---

# Los cortes que más se confunden

**CONOCIMIENTO contra MÉTODO.** El conocimiento dice **qué es verdad**; el método
dice **cómo se averigua**. Si una línea empieza con «se descubrió que…», es
conocimiento. Si empieza con «para descubrir…», es método.

**MÉTODO contra RAZONAMIENTO.** El método dice cómo se construyó y se audita el
cerebro — mirando hacia adentro, con tiempo por delante. El razonamiento dice
cómo se responde, con el cerebro ya construido, una pregunta que alguien hace
hoy — mirando hacia afuera, en el momento. Si la regla explica cómo se verificó
un hecho, es método. Si explica cómo contestar sin tener el hecho guardado, es
razonamiento.

**CONOCIMIENTO contra INVARIANTES.** El conocimiento trae el hecho con su
explicación; las invariantes traen **la cifra desnuda contra la cual se comprueba**.
Si una invariante explica por qué, ya duplicó.

**ESCALABILIDAD contra PENDIENTES §F.** Pendientes tiene **la lista** de módulos
con sus dependencias; escalabilidad tiene **el contrato** que cualquier módulo debe
cumplir, incluidos los que nadie diseñó. Si escalabilidad enumera módulos, duplicó.

**CONOCIMIENTO contra SKILL.** El conocimiento trae la evidencia; el skill la regla
destilada. **El skill nunca introduce un hecho que no esté en el conocimiento** —
se deriva de él, no lo amplía.

**CONOCIMIENTO contra LENGUAJE.** El conocimiento explica **qué hace** `%MO`; el
lenguaje dice **cómo lo llama cada sistema**.

**CONOCIMIENTO contra MEMORIA.** El conocimiento tiene la verdad de hoy; la memoria
tiene cómo se llegó a ella y **qué se rechazó por el camino**.

**MEMORIA contra APRENDIZAJE.** La memoria guarda **la decisión**; el aprendizaje
guarda **el efecto de la decisión sobre lo que el sistema cree**, y el caso indexado
que permite reconocer el siguiente parecido.

**PENDIENTES contra MEMORIA.** Pendientes es lo abierto; memoria es lo cerrado.
Cuando algo se decide, **se mueve**.

**PENDIENTES contra PRIORIDADES.** Pendientes tiene **qué falta**; prioridades tiene
**el criterio de orden**. La cola vigente vive en `ESTADO.md`; si difieren, manda
`ESTADO.md`.

**GLOSARIO contra LENGUAJE.** El glosario es vocabulario **entre personas**; el
lenguaje es traducción **entre sistemas**.

**PENDIENTES contra DICCIONARIO-DATOS.** Pendientes dice *qué hacer*; el diccionario
tiene *los datos con que hacerlo*.

**PENDIENTES contra CONOCIMIENTO `IDEAS.md`.** Pendientes tiene todo lo que falta hacer o
decidir. `IDEAS.md` tiene sólo **las ideas del modelo que aún no se diseñan**. Si un tema
aparece en los dos, uno sobra.

---

# El flujo de una decisión

```
1. Aparece la duda             → PENDIENTES
2. Se ordena contra las demás  → PRIORIDADES (criterio)
3. Se discute y se decide      → MEMORIA (incluido lo descartado)
4. Si cambia el sistema        → CONOCIMIENTO
5. Si deja una cifra de control→ INVARIANTES
6. Si hay que respetarlo       → SKILL
7. Si cambia cómo se nombra    → LENGUAJE
8. Si vino de una propuesta    → APRENDIZAJE (el caso, para reconocer el próximo)
```

Un mismo tema puede tocar varios archivos, pero **cada frase vive en uno solo**.

---

# Las tres reglas de método que ahora son obligación

No son nuevas: estaban en `METODO.md` como observación. Pasan a requisito.

**1 · Nada entra a la Capa I por una sola ruta.** Un hecho llega con su segunda
ruta de verificación, o entra marcado como no verificado y **no se puede construir
encima**. Las convergencias ya logradas están en `INVARIANTES.md` §5.

**2 · Toda tarea declara su cifra de paro.** Si no puede declararla, no está lista
para trabajarse: está lista para discutirse.

**3 · Opción y alternativa donde deshacer es caro.** Se exige alternativa cuando el
cambio arrastra datos históricos; no cuando se arregla con una migración barata.

---

# Estado de los archivos

| Archivo | Capa | Estado |
|---|---|---|
| `ESTADO.md` | IV | ✅ Punto de entrada · punto de corte |
| `METODO.md` | II | ✅ Razonamiento e identidad |
| `RAZONAMIENTO.md` | II | 🆕 Cómo responder preguntas operativas con el cerebro ya construido |
| `METACOGNICION.md` | II | 🆕 La difusión, las conexiones, la integración, la reentrada y lo que el cerebro sabe de sí mismo, medido |
| `MODELO.md` | I | ✅ Aprobado, 15 hallazgos resueltos |
| `CONOCIMIENTO.md` | I | ✅ 17 partes · las reglas del sistema |
| `CATALOGOS.md` | I | 🆕 8 catálogos de OPUS 2025 · dividido de CONOCIMIENTO |
| `LENGUAJE.md` | I | ✅ Canon 1.0 con el dialecto OPUS 2025 |
| `MEMORIA.md` | III | ✅ 630 decisiones · 13 descartes · 35 correcciones |
| `PENDIENTES-MEJORAS.md` | IV | ✅ Auditado contra los catálogos vigentes |
| `skills/erp-construccion.md` | II | ✅ Base. Regenerado desde el conocimiento |
| `PROGRAMA-CPM.md` | I | ✅ 901 pruebas · los siete programas reproducen las cifras publicadas |
| `GLOSARIO-DOMINIO.md` | I | **93 términos · 25 ambigüedades** |
| `DICCIONARIO-DATOS.md` | I | Homologación y equivalencias |
| `CASO-TRABAJADO.md` | III | ✅ Un caso de punta a punta |
| `INVARIANTES.md` | II | 🆕 Cifras de control y condición de paro |
| `PRIORIDADES.md` | IV | 🆕 Criterio de orden |
| `APRENDIZAJE.md` | III | 🆕 Diseñado, no construido |
| `ESCALABILIDAD.md` | II | 🆕 Contrato de módulo · dos escenarios de crecimiento |
| `WORKFLOWS.md` | II | 🆕 Personas, sistema, agente interno y skills: cómo se conectan y qué falta decidir · el flujo de la app (§8, D-529), empezando por la cadena de la información (§8.1, D-530 a D-532), con la otra mitad: del programa a la ejecución, y los roles paso por paso (§8.7, D-536 a D-538), y dónde queda (§8.8, D-539 a D-544) |
| `skills/erp-importacion.md` | II | 🆕 Compilado · carga desde OPUS |
| `skills/erp-rediseno.md` | II | 🆕 Compilado · las seis operaciones y las tres capas |
| `skills/erp-parametrico.md` | II | 🆕 Compilado · ensambles, cohorte, dispersión |
| `skills/erp-cuantificador.md` | II | Compilado · trazar sobre el plano |
| `skills/erp-programa.md` | II | 🆕 Compilado · el CPM, los vínculos, reprogramar, guardar y el Gantt |
| `agentes/arquitecto-erp.md` | II | Diseña el esquema · evalúa skills y agentes de un módulo nuevo |
| `agentes/constructor-erp.md` | II | Escribe el código |
| `agentes/migrador-erp.md` | II | Lee los exports ajenos |
| `agentes/gravity.md` | II | 🆕 Orquestador externo · entrega plan de ruta, no ejecuta |
| `agentes/gravity-obra.md` | II | 🆕 Orquestador interno · Ollama local, Groq red · diseñado, no construido |
| `agentes/auditor-erp.md` | II | 🆕 Corre las invariantes — **de los datos y del cerebro** |
| `verificar-cerebro.py` | II | 🆕 9 comprobaciones mecánicas de coherencia |
| `red-del-cerebro.py` | II | 🆕 Mide la red: conexiones escritas, cambios que van juntos, capacidad; con `--vigencia` a quién releer, con `--integracion` cuánto se puede partir y qué se repite, con `--reentrada` si lo compilado oye a su fuente |
| `preparar-para-github.py` | II | 🆕 Deja la carpeta de una app lista para GitHub: aparta `.env`, llaves, bases y hojas de datos, busca claves dentro del texto (valores tapados) y arma `.gitignore`, `.env.example` y una ficha por llenar, aparta el directorio de datos de una base, deja fuera lo que se pida con `--excluir` y puede sacar de la copia las contraseñas escritas en el código (`--quitar-contrasenas`, que las ve en asignaciones, diccionarios, llamadas, guiones, documentos y comillas invertidas, y además las busca por toda la copia) y lista los archivos que por su nombre parecen respaldos o muestras de datos; con `--autoprueba` se prueba con claves falsas (D-496) |
| `IDEAS.md` | IV | 🆕 8 ideas sin diseñar · dividido de CONOCIMIENTO |
| `PROPUESTA-CUATRO-MODULOS.md` | IV | ✅ **22 decisiones cerradas** · pendiente diseño formal |
| `agentes/` | II | Gravity, arquitecto, constructor, migrador, auditor |

---

# Archivos retirados

Se retiraron antes del primer commit de este repo, por «incorporados al conocimiento»:
`ANALISIS-CATALOGOS-BASE.md` · `ANALISIS-MATRIZ-Y-ARBOL.md` ·
`DICCIONARIO-CONCEPTOS.md` · `ERP-CONSTRUCCION-PLAN.md`. **No hay copia de ellos en el repo
ni en su historia** (B-30, D-490): no se consultan ni se actualizan, y ningún otro archivo del
cerebro se apoya en ellos —el verificador lo comprueba—. Si alguno apareciera, se coteja
contra el cerebro antes de fusionar nada.

---

# Dos archivos que no existen y a veces se nombran

`REDISEÑO.md` y `PROPUESTAS.md` **no son archivos**. Son secciones: el rediseño es
`CONOCIMIENTO.md` §12 —y en producción es una tabla, no un markdown: se guardan
pasos, no resultados—, y la propuesta es `CONOCIMIENTO.md` §14 más la tabla
`PROPUESTA` de `MODELO.md` §5.
