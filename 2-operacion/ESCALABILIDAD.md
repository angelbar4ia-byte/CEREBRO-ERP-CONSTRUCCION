# ESCALABILIDAD

```
órgano:     plasticidad — cómo crece sin rehacerse
capa:       II — Operación
pregunta:   ¿cómo se agrega un módulo, incluso uno que aún no está definido?
tiempo:     se hace así
corte:      2026-09-21
verificado: Derivado de los 25 módulos de PENDIENTES §F y de las costuras de `erp-construccion.md` §9
```

> **La lista de módulos vive en `PENDIENTES-MEJORAS.md` §F.** Aquí está el
> **contrato**: qué tiene que cumplir cualquier módulo para entrar, incluidos los
> que todavía nadie diseñó.
>
> Dos escenarios, un solo contrato: arrancar un ERP nuevo por partes, y colgarle
> módulos a uno que ya existe.

---

# 1. El hallazgo que hace posible todo esto

**Ningún módulo nuevo crea un árbol propio. Cada uno es una lectura distinta del
mismo árbol.**

| Módulo | Qué agrega | Qué reusa |
|---|---|---|
| `apu` | Matriz y versión | El árbol |
| `presupuesto` | Volumen de obra | El árbol + el motor |
| `parametrico` | La cantidad como receta | El árbol + el motor |
| `programa` | Duración y precedencia | El árbol + el rendimiento |
| `contratos` | Un precio pactado | El árbol + el concepto |
| `almacen` | Lo que salió de verdad | El árbol + la explosión |

Esto no se diseñó: **se repitió hasta hacerse evidente.** El programa reagrupa, el
paramétrico reagrupa, el ensamble reagrupa — y ninguno reasigna. Tres apariciones
de la misma regla ya describen algo real del dominio.

> **La consecuencia práctica:** un módulo que necesita su propia tabla de árbol está
> mal planteado. Casi siempre lo que necesita es una **dimensión nueva sobre los
> nodos que ya existen**.

---

# 2. El contrato de módulo

Seis preguntas. Un módulo que no las conteste no está listo para construirse — está
listo para discutirse.

| # | Pregunta | Si no se contesta |
|---|---|---|
| 1 | **¿Qué dimensión agrega?** Costo, tiempo, cantidad, ejecución, responsabilidad | Va a duplicar una existente |
| 2 | **¿De qué nodos cuelga?** Concepto, insumo, etapa, presupuesto | Va a inventar jerarquía |
| 3 | **¿Qué lee y qué escribe?** | Va a escribir donde otro es dueño |
| 4 | **¿Cuál es su cifra de paro?** Una invariante comprobable | No hay forma de saber si funciona |
| 5 | **¿Qué propone y qué aplica solo?** | Va a corregir sin permiso |
| 6 | **¿Qué pasa si no está?** | Si el sistema se rompe sin él, no es módulo: es núcleo |

## Las cuatro reglas que no negocia

- **Un dato tiene un solo dueño.** El módulo lee lo ajeno y escribe lo propio. El
  precio vive en el catálogo, una vez.
- **Nada reasigna.** Reagrupar sí, mover de padre no. El ensamble referencia al
  concepto; no lo saca de su etapa.
- **Propone, no aplica.** Todo lo que toca un dato de entrada ajeno va por la bandeja
  única, con evidencia.
- **Trae su invariante.** Entra a `INVARIANTES.md` el día que entra el módulo, no
  después.

---

# 3. El contrato de lo declarado

**El contrato de módulo cubre módulos. Casi nada de lo que se declara es un módulo.**

Un concepto nuevo —la *alerta*, la *procedencia*, el *nivel de confianza*— nace en
mitad de una conversación, se usa como si existiera, y nadie pregunta dónde vive.
**Ya pasó con la alerta:** se declaró, se le dieron reglas, y sólo después se notó
que no tenía tabla ni archivo — se habría perdido al cerrarse.

Cuatro preguntas. Cortas a propósito, porque se contestan en el momento, no después:

| # | Pregunta | Si no se contesta |
|---|---|---|
| 1 | **¿Dónde vive en el cerebro?** | Existe en la conversación y no en ningún archivo |
| 2 | **¿Qué lo persiste?** Tabla, campo, o nada a propósito | Se pierde al cerrarse y nadie lo nota |
| 3 | **¿Contra qué se comprueba?** | No hay forma de saber si funciona |
| 4 | **¿Qué otro archivo cambia por esto?** | El cerebro empieza a desincronizarse |

> **La pregunta 2 es la que más se salta**, porque «se guarda» suena obvio hasta que
> alguien busca la tabla. *Nada, a propósito* es respuesta válida — pero escrita,
> no supuesta.

**Quién lo aplica:** `gravity` lo incluye en el plan cuando la tarea declara algo
nuevo, y el `auditor` lo revisa al cerrar. Ninguna de las cuatro se puede comprobar
con script: son prosa, y por eso dependen de que alguien pregunte.

---

# 4. Dos superficies: API y MCP

**Una API es para software. Un MCP es para modelos.** El frontend llama lo que alguien
escribió en el código; el agente **elige** herramienta leyendo su descripción. No
compiten: el frontend no puede elegir, y el agente no puede tener llamadas escritas a
mano para preguntas que nadie previó.

```
frontend web / móvil  ──►  API   ──┐
                                   ├──►  capa de servicio  ──►  motor  ──►  base
agente (Ollama/Groq)  ──►  MCP  ───┘
```

**El MCP no habla con la base: habla con el mismo servicio que la API.** Implementado
aparte no son dos superficies de un sistema — son dos sistemas que se parecen, y las
reglas se separan en silencio.

## 4.1 No contradice D-54

D-54 dice que FastAPI es la única superficie pública, **y su razón era que dos specs
producen dos clientes generados con dos estilos**. MCP no genera cliente: lo consume un
modelo. La razón no aplica, así que D-54 sigue en pie y MCP cabe al lado.

## 4.2 El orden: API primero, MCP después

**La API no es discutible:** sin ella no hay producto. Un MCP sin API es un agente sin
sistema debajo.

**El MCP va después del agente, no antes.** Las herramientas se diseñan mirando qué
pregunta el agente de verdad, no qué imaginamos que va a preguntar. Y es delgado: cada
herramienta es una llamada al servicio que ya existe, más una buena descripción.

> **Lo que sí se decide hoy, porque es caro después: la capa de servicio va separada de
> la API.** Si la lógica vive dentro de los endpoints, el día del MCP hay que sacarla de
> ahí. Mismo principio que los montos como `string`.

## 4.3 Lo que MCP cambia para bien

Hoy «el agente no escribe» es una regla escrita que alguien debe respetar. Con MCP se
vuelve **estructural**: si no existe herramienta de escritura, el agente no puede
escribir aunque quiera. Es más fuerte que la regla.

## 4.4 Los dos riesgos

**Una herramienta genérica tira la frontera de datos.** Si existe
`ejecutar_consulta(sql)`, el agente lee cuentas bancarias y todo lo demás. Las
herramientas son específicas —`explosion_de_concepto`, `gasto_por_obra`— y cada una
lleva su límite adentro.

**Demasiadas herramientas degradan la elección.** Con veinte parecidas el modelo toma la
equivocada, y el síntoma no es un error: es una respuesta plausible y falsa. Empuja
hacia lo mismo que los detectores: pocos, angostos y bien descritos.

> **Y una honestidad sobre MCP:** su especificación es joven y se mueve. Su valor
> depende casi por completo de **cómo se describen las herramientas**, que se parece más
> a escribir instrucciones que a diseñar una API. Ese mantenimiento se subestima.

## 4.5 Un servidor para empezar; partir por permisos

Partir un MCP no es decisión técnica sino **de permisos**: uno **de consulta** —sólo
lee, no puede hacer daño— y otro **de propuestas** —escribe en la bandeja—. Así un
agente recibe el primero y otro los dos.

**Uno solo para empezar.** Partirlo antes de saber qué herramientas existen es adivinar.
Cuando se parta, que sea por ese límite, que es el único que ya se sabe que importa.

## 4.6 Por instalación, con un matiz

Cada instalación elige. Pero **una instalación local necesita las dos igual**: el ERP
completo vive ahí y la interfaz también. No es «MCP en local, API en red» — es que las
dos existen y **el MCP se puede apagar**.

---

# 5. El núcleo, que no es módulo

**No se puede partir.** `presupuesto`, `apu` y `parametrico` usan el mismo motor:
separarlos en servicios obligaría a duplicarlo o a una llamada remota por nodo.

```
NÚCLEO     árbol recursivo · motor de cálculo · catálogo · propuestas
           ↑ nadie lo sustituye, todos lo usan
MÓDULOS    cuelgan del núcleo por una costura declarada
```

**Las costuras que sí funcionan** —donde un módulo se puede separar sin romper
nada—: importación, exportación, diccionario, contratos, programa, almacén.

> Monolito con fachadas, migrable a microservicios. La costura se declara desde el
> día uno aunque nunca se corte.

---

# 6. Escenario A — ERP nuevo, por partes

El orden lo fija la dependencia real, no el entusiasmo.

```
catálogo  →  APU  →  presupuesto  →  [ lo que se quiera ]
   ↑           ↑          ↑
   insumos   matriz    volumen
```

| Paso | Qué entrega solo | Por qué ahí |
|---|---|---|
| 1 · Catálogo | Insumos con precio y unidad | Sin él no hay de qué costear |
| 2 · Motor + APU | Un precio unitario que cuadra | **Es el corazón.** Todo lo demás lo usa |
| 3 · Presupuesto | Un total que cuadra al centavo | Primer entregable con valor real |
| 4 · Importación | Datos reales en vez de capturados | Antes de esto, el sistema vive de fixtures |
| 5+ · Lo que haga falta | — | Ya es elección, no dependencia |

**Cada paso es entregable por sí solo.** Si el proyecto se detiene en el 3, lo
construido sirve. Es la prueba de que la partición es correcta.

> **La trampa a evitar:** empezar por lo visible —el Gantt, el dashboard— porque se
> demuestra mejor. El programa necesita duraciones, la duración necesita rendimiento,
> el rendimiento necesita catálogo. Construido al revés, el Gantt es ficción
> ordenada.

---

# 7. Escenario B — módulo sobre un ERP existente

El caso que ya se resolvió una vez: los datos llegaron de OPUS y hubo que
entenderlos sin tocarlos.

| Paso | Qué hacer | Regla que lo gobierna |
|---|---|---|
| 1 | **Leer el sistema vivo, no su documentación** | La descripción puede mentir; el contenido es la evidencia |
| 2 | **Traducir al canon por significado, no por nombre** | Un traductor que empareja por nombre produce datos que **cuadran y mienten** |
| 3 | **Verificar la aritmética contra un total conocido** | Sin cifra contra la cual comparar, un error de un tercio pasa inadvertido |
| 4 | **Colgar el módulo, no reescribir el sistema** | Mientras nada dependa se corrige; en cuanto algo depende, **se agrega encima** |
| 5 | **Devolver lo corregido en el formato del sistema origen** | El ERP existente sigue operando; el módulo no lo secuestra |

> **Y en los cinco pasos, la regla que más se usa contra un sistema ajeno: si el dato
> se contradice, se para** (`METODO.md` §3.5). Un ERP en uso acumula reglas de épocas
> distintas, y la mayoría de las contradicciones que muestra **no son errores: son dos
> momentos, dos ámbitos o dos bases.** Resolverlas eligiendo importa el error al
> sistema nuevo y le quita la evidencia de por qué existía.

## Un ERP en uso es evidencia, no solo origen de datos

Un sistema que lleva años operando **trae reglas ya probadas contra la realidad**: qué
campos se usan de verdad y cuáles quedaron muertos, qué validaciones nadie pudo
saltarse, qué se decidió una vez y nunca se volvió a tocar.

Eso no se copia: **se identifica, se valida contra los datos, se decide, y sólo
entonces se implementa.** Un ERP en uso también acumula errores que nadie corrigió
porque ya nadie recuerda por qué están.

> Es la misma disciplina de siempre, un nivel arriba: **el contenido es la evidencia,
> la documentación es sólo una etiqueta.** Lo que un sistema *hace* dice más que lo
> que su manual dice que hace.

Los cuatro pasos son los de una propuesta, no los de una importación: **detectar no
necesita permiso, adoptar sí** — ver `PENDIENTES-MEJORAS.md` B-44.

> **El dialecto es el punto de entrada.** Cada ERP nombra distinto lo mismo. El canon
> ya está escrito y probado con ida y vuelta sobre OPUS 2025; un sistema nuevo agrega
> **una ficha de dialecto**, no un modelo nuevo.

## Módulos que se pueden colgar sin tocar el sistema origen

Son los que sólo **leen** y producen una dimensión que el sistema viejo no tiene:

| Módulo | Sólo necesita | Entrega |
|---|---|---|
| Diccionario | El catálogo | Equivalencias y homologación |
| Factorizador | Materiales y unidades | Compras reales, sobrante contra desperdicio |
| Auditoría de explosión | Presupuesto y matrices | Dónde no cuadra y por qué — ya es detector de `gravity-obra.md` §6 |
| Comparador de obras | Dos presupuestos | Desviación entre lotes o prototipos — catalogado como `comparar_obras` en `gravity-obra.md` §6 |

**Ninguno escribe en el sistema origen.** Por eso son los primeros candidatos: el
riesgo de deshacerlos es cero.

---

# 8. Un módulo que aún no está definido

Es el caso que el usuario va a tener seguido. **No hace falta que esté diseñado para
saber dónde encaja.**

```
1. Contestar las seis del §2         si falla la 1 o la 6, no es módulo
2. Ubicarlo: ¿qué dimensión?         costo · tiempo · cantidad · ejecución
3. Ubicar su costura                 ¿de qué nodos cuelga, qué lee, qué escribe?
4. Declarar su invariante            aunque el módulo no exista todavía
5. Entra a PENDIENTES §F             con sus dependencias
6. Se ordena con PRIORIDADES         desbloqueo ÷ costo, con los dos frenos
```

**Lo que no se hace:** diseñarlo entero antes de saber si entra. Dos campos ya se
retiraron del modelo por dejarlos «provisionales» — un campo provisional deja de
serlo en cuanto algo empieza a depender de él.

---

# 9. Cada módulo trae su skill, derivado

**Hoy hay un solo skill porque hay un solo sistema.** Cuando los módulos existan,
cada uno gana el suyo — y se **compila** desde el conocimiento, nunca se escribe a
mano.

| Skill | Compilado de | Estado |
|---|---|---|
| `erp-construccion` | El conocimiento entero, destilado | ✅ Base. Se carga siempre |
| `erp-importacion` | `CONOCIMIENTO.md` §2 · `CATALOGOS.md` §11 · `CONOCIMIENTO.md` §4.2 | ✅ |
| `erp-rediseno` | `CONOCIMIENTO.md` §6.4 · `CONOCIMIENTO.md` §8 · `CONOCIMIENTO.md` §9 · `CONOCIMIENTO.md` §12 | ✅ |
| `erp-parametrico` | `CONOCIMIENTO.md` §5 | ✅ |
| `erp-diccionario` | — | ⛔ **Bloqueado: su diseño no está en el conocimiento** |

**Lo que califica para skill propio:** reglas verificadas que los demás módulos no
necesitan leer. El motor, el APU, el catálogo y el presupuesto **no califican** — son
núcleo, y sacarlos del base los vuelve opcionales. `programa`, `exportacion`,
estimaciones y almacén **todavía no**: sus reglas están sin decidir, y escribirles
skill hoy sería inventar hechos.

**El costo de partir de más:** un skill se dispara por su descripción. Con cuatro
satélites bien separados no hay solape; con doce, se carga el equivocado y el skill
pasa de prevenir errores a causarlos.

> **El skill nunca introduce un hecho que no esté en el conocimiento.** Si se escribe
> a mano, dos skills terminan afirmando cosas distintas del `%MO`, dos agentes las
> leen, y nadie sabe cuál mintió.

Sería la séptima aparición de *si algo se puede derivar del uso, deja de ser entrada:
es un subproducto* — siempre completo, sin huérfanos, y no se desactualiza.

**Cuándo partir el skill:** cuando un módulo tenga reglas que los demás no necesitan
leer. Antes de eso, partirlo sólo multiplica los lugares donde el mismo hecho puede
divergir.

---

# 10. Los agentes, en dos familias

| Familia | Dónde vive | Qué hace | Estado |
|---|---|---|---|
| **De desarrollo** | Fuera del producto, en la sesión | Diseñan, construyen, migran, auditan | ✅ Tres escritos · uno propuesto |
| **Interno** | **Dentro del ERP**, con el Agent SDK | Consulta, detecta, propone | ⏸️ Fase 2 |

## Los de desarrollo

```
arquitecto   planea la forma        premotor
constructor  la vuelve código       motor
migrador     lee el mundo crudo     sensorial
auditor      comprueba que cuadra   nociceptivo
```

**Los cuatro están escritos** (D-58, `agentes/auditor-erp.md`). Esta sección decía
«el auditor falta» — quedó desactualizada desde que se escribió: otro caso de
pendiente-ya-resuelto-sin-sincronizar, como D-183.

## El interno

Sus herramientas **son** el modelo de datos: sin modelo no hay agente. Y su límite es
absoluto: **entra al sistema sólo por la bandeja de propuestas.** Lee todo, escribe
nada.

> Un agente embebido que pueda aplicar sus propias conclusiones no es un asistente:
> es un segundo autor sin registro de quién decidió.
