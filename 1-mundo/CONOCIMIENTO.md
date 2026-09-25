# CONOCIMIENTO

```
órgano:     corteza asociativa
capa:       I — Mundo
pregunta:   ¿cómo funciona el sistema?
tiempo:     es así
corte:      2026-09-25
verificado: 17 partes · cada regla comprobada antes de escribirse
```

> **Las reglas del sistema.** Los catálogos de origen están en `CATALOGOS.md`; las
> ideas sin diseñar, en `IDEAS.md`. Aquí sólo lo que es verdad y cómo se verificó.

## Contenido

| # | Parte | Líneas | Secciones |
|---|---|---|---|
| §1 | Identidad y posición | 94 | 4 |
| §2 | Importación desde OPUS | 386 | 9 |
| §3 | Notas de implementación | 129 | 5 |
| §4 | Estados del nodo y exportación | 110 | 3 |
| §5 | Presupuesto paramétrico — ensambles | 272 | 11 |
| §6 | Destajos: precio, cuadrilla y fusión | 178 | 4 |
| §7 | Modos de valuación | 82 | 3 |
| §8 | Operaciones de rediseño | 133 | 5 |
| §9 | Concepto compuesto — matriz dentro de matriz | 58 | 4 |
| §10 | Categorías | 234 | 6 |
| §11 | Los flujos entre sistemas | 1290 | 25 |
| §12 | Las tres capas del rediseño | 52 | 3 |
| §13 | Contratación, cambios y obra en marcha | 449 | 8 |
| §14 | La propuesta | 66 | 5 |
| §15 | La ruta crítica no está en el modelo | 39 | 0 |
| §16 | Normalización, homologación y grupos funcionales | 60 | 4 |
| §17 | Cuantificación gráfica — de inventario a regla verificada | 72 | 4 |

> **Las partes que ya tienen skill compilado:** §2 importación, §5 paramétrico,
> §8 y §12 rediseño. Ver `2-operacion/skills/`.

---
# 1. Identidad y posición

> Regla de fondo: **el árbol es la verdad; el WBS es presentación.**

## 1.1 El WBS se separa con puntos

```
1.100.01.1523.01        300.01.05.01.01.01
```

Con separador explícito, **el ancho de cada segmento deja de importar**. Se acabó
el techo de 99 hermanos del formato de ancho fijo, y desaparece la ambigüedad de
los ceros de relleno.

El WBS se calcula **por posición**, no se captura ni se hereda del export de OPUS.

## 1.2 Dos trabajos que se contradicen

El WBS quiere hacer dos cosas incompatibles:

| Trabajo | Qué exige |
|---|---|
| **Posición** | Reflejar el árbol de hoy → **tiene que renumerarse** |
| **Referencia** | Que el contrato siga apuntando a lo mismo → **no puede cambiar nunca** |

### Por qué renumerar hace daño

```
ANTES                        Estimación 1 pagada:
1.1  Cimentación             «partida 1.2 Estructura — $500,000»
1.2  Estructura
1.3  Albañilería

DESPUÉS (se inserta Excavación)
1.1  Cimentación
1.2  Excavación    ← lo nuevo
1.3  Estructura    ← era 1.2, y NO cambió nada de ella
1.4  Albañilería   ← era 1.3, tampoco cambió
```

La estimación pagada sigue diciendo `1.2`, que hoy es Excavación. **El renumerado
contagia a los hermanos inocentes:** Estructura no se tocó y su número cambió igual.

### La separación

- **`id` interno** — lo genera la base en el `INSERT`. Nunca se muestra, nunca cambia.
- **`wbs`** — atributo calculado. Se recalcula libremente al reordenar.
- **Documentos históricos** — guardan el `id` **más una foto del WBS al emitirse**.

Así se reordena cuanto se quiera, la estimación sigue apuntando a la partida
correcta, y al reimprimirla sale el número que tenía ese día.

## 1.3 Cuándo se fija el `id`

**En el `INSERT`.** No al aprobar, no al contratar: en el instante en que la fila
nace, antes de tener posición. Lo genera la base de datos, nunca la aplicación ni
el usuario.

Si se asignara después, durante el diseño los nodos no tendrían identidad estable
y cualquier referencia hecha en esa etapa quedaría huérfana.

## 1.4 Estado del presupuesto

La práctica del oficio: en obra pública, firmado el contrato **el catálogo se
congela** y los cambios entran como conceptos extraordinarios con número nuevo al
final, nunca renumerando lo existente.

| Estado | Qué permite |
|---|---|
| **En diseño** | Renumera libre |
| **Contratado** | Congelado; solo admite adiciones al final |

### El estado es del nodo, no del presupuesto

Los planos de proyecto **llegan por partes**, así que se contrata y se programa por
partes: cimentación entra a contrato mientras acabados sigue en diseño.

> Por eso **el congelamiento es por subárbol**. Un presupuesto no está «en diseño» o
> «contratado»: cada rama tiene su estado.

Consecuencias:

- El **rediseño sigue corriendo** en las ramas no congeladas.
- Las tres capas (§11) aplican por subárbol.
- Una regla de rediseño que toque un nodo congelado **queda «no aplicada»** y se
  reporta — el mecanismo de §12.2 ya lo cubre.

**Los subcapítulos y niveles son la unidad natural**, porque los planos llegan
justo así: por nivel y por especialidad. No hace falta una entidad «paquete»: el
estado va en el nodo y el subárbol se contrata completo. Mismo principio de que
nada reasigna.

---

# 2. Importación desde OPUS

## 2.1 La clave es la verdad

La clave reconcilia: al reimportar, un concepto con la misma clave **es el mismo
concepto**. La carga nunca se descarta ni se duplica.

Pero bajo una misma clave pueden cambiar dos cosas, y **no pesan igual**:

| Qué cambió | Gravedad | Qué hace la carga |
|---|---|---|
| **Descripción** | Texto | Normaliza. Si la diferencia es grande, **alerta** |
| **Los hijos** (insumos o cantidades) | **El PU se movió** | **Crea versión nueva** |

## 2.2 Versionado del concepto

El segundo caso es el peligroso. Si la carga sobrescribe la explosión, todos los
presupuestos históricos que usaron ese concepto pasan a mostrar un PU distinto del
que se contrató, **sin que nadie lo note**.

```
Concepto             ← identidad: la clave. Una sola, para siempre
├─ Versión 1         insumos + cantidades + PU      vigente ene–jun
└─ Versión 2         la explosión cambió            vigente jun–
```

> **Cualquier cambio en el conjunto de insumos o en sus cantidades crea versión
> nueva. Sin umbral, automático.** La versión es barata y es la verdad.

El umbral difuso queda **solo para el texto**, que es donde «muy diferente» sí es
un juicio.

El renglón del presupuesto apunta a **una versión concreta**, no a la clave suelta.
Mismo patrón que el `id` con la foto del WBS: identidad estable por un lado, valor
congelado por otro.

### Quién aprueba

**Por defecto, nadie.** La versión se crea sola y entra en vigor sola. La
aprobación aparece solo cuando hay algo en juego, y el sistema lo mide por impacto:

| Uso del concepto | Qué pasa |
|---|---|
| Sin presupuestos | Automático y silencioso |
| Solo en diseño | Automático, pero **avisa** a quienes usan esos presupuestos |
| Algo contratado | **No entra en vigor.** Va a control de cambio |

Más una compuerta por magnitud: **si el PU se movió más de 5%, pide confirmación**
aunque sea en diseño.

> **El silencio nunca aprueba.** Sin respuesta queda pendiente, no vigente por
> vencimiento de plazo.

## 2.3 Reconciliación

Las filas de OPUS llegan sin `id`. La primera carga lo asigna y **guarda la llave
natural** — clave, y ruta o prototipo para los nodos estructurales. Sin eso, la
segunda importación duplica todo el árbol.


## 2.4 El cargador — qué columnas se necesitan de verdad

> **`Ingenieria ERP` no se importa.** Esa columna se diseñó para un ERP de terceros
> sobre el que no hay control. Puede venir trunca, cambiar de formato o desaparecer.
> **El WBS se calcula aquí, por posición** (§1.1).
>
> Se pretendía **generarla de salida** junto con `Nivel ERP`. **La prueba de ida y
> vuelta demostró que no se puede** (`CATALOGOS.md` §11): la regla no es deducible de los datos.

Lo mismo aplica a todo lo que sea derivable: no se confía en ello, se recalcula.

### Las cuatro obligatorias

| Columna | Para qué | Por qué no se puede derivar |
|---|---|---|
| `Nivel` | Profundidad → arma el árbol | Sin esto no hay jerarquía |
| `Clave` | Identidad y reconciliación | Es la verdad (§2.1) |
| `Cantidad` | Volumen de obra | **Es el único dato propio del presupuesto** |
| `Tipo` | Distingue agrupador de concepto | Ver abajo |

**Más el orden de las filas**, que es lo que junto con `Nivel` reconstruye la
jerarquía.

**Y `Origen` en cuanto el presupuesto venga desglosado**, porque ahí deja de ser un
valor único y se vuelve la categoría de cada insumo.

### Por qué `Tipo` es obligatoria

Comprobado sobre las 3,231 filas:

| Tipo | Con hijos | Sin hijos |
|---|---|---|
| Capítulo | 7 | 0 |
| Subcapítulo | 102 | 0 |
| Nivel 2 | 325 | 0 |
| **Nivel 3** | **231** | **114** |
| Concepto | 0 | 2,452 |

Casi todo se derivaría de la estructura: **todo concepto es hoja y todo estructural
tiene hijos**. La excepción rompe la regla: **114 Nivel 3 no tienen hijos**, y ahí
un agrupador vacío es indistinguible de un concepto.

### `Origen`: es la categoría

**No se descarta.** En este export trae un solo valor porque todas las filas son
conceptos, pero **un presupuesto desglosado traerá mano de obra, materiales,
herramienta y equipo en esa columna**. Es la fuente de `categoria` (§10).

### Las tres de verificación

No arman nada, pero detectan que algo se rompió:

| Columna | Qué detecta |
|---|---|
| `Indice` | Filas perdidas o reordenadas. Es la suma de control del árbol |
| `Descripción` | Divergencia contra el catálogo → dispara la alerta de §2.1 |
| `Unidad` | Que el presupuesto no contradiga al concepto |

Las tres **deberían venir del catálogo de conceptos**, no del presupuesto. Si
llegan, se comparan; no se cargan encima.

### `Precio unitario`: señal, no dato

**El PU se crea en el APU**, no en el presupuesto. Pero cuando viene, sirve para
algo valioso: si el PU importado difiere del calculado desde la explosión vigente,
**la explosión cambió** → es el disparador del versionado de §2.2.

Se guarda como *observado*, nunca como fuente.

### Lo que se descarta

| Columna | Por qué |
|---|---|
| `Ingenieria ERP` | No se importa: **se genera** al exportar (§4) |
| `Nivel ERP` | No se importa: **se genera** al exportar (§4) |
| `Total` | `Cantidad × PU` |
| `%` | Total del nodo ÷ total general |
| `Descripción de matriz`, `Unidad de matriz` | Vienen del APU |
| `Descripcion Corta` | Del catálogo de conceptos |
| `Ruta paramétrica` | Es el paramétrico de OPUS. **El nuestro se construye aquí** (§5), no se importa |

### Mapeo de encabezados

Como las columnas pueden venir truncas o con otro nombre, el cargador **no busca
por posición ni por nombre exacto**. Lleva una tabla de alias por campo:

```
nivel      ← "Nivel", "Nivel ", "NIVEL", "Nv", "Profundidad"
clave      ← "Clave", "CLAVE", "Código", "Clave concepto"
cantidad   ← "Cantidad", "CANTIDAD", "Cant", "Volumen"
tipo       ← "Tipo", "TIPO", "Clase"
```

Y lo mismo aplica al **nombre del catálogo**: `Trabajos` y `Contrato` son el
mismo (§10.2).

> Cuando **dos columnas comparten nombre** —el caso de `Tipo` en trabajos (`CATALOGOS.md` §3)—
> el alias no basta: hay que leer **por posición**.

Y antes de cargar nada, un **informe de mapeo**: qué columna del archivo se leyó
como qué campo, cuáles no se reconocieron y cuáles obligatorias faltan. Si falta
una de las cuatro, **la carga no procede**.



## 2.5 Las filas placeholder de OPUS

Al explotar el presupuesto por agrupadores hasta cierto nivel para detectar los
conceptos, **OPUS genera renglones estructurales vacíos**. No son datos: son
andamio del propio export.

### Cómo se ven

Las 121 filas vacías del presupuesto, caracterizadas:

| Tipo | Nivel | Cuelga de | Filas | Hijos propios |
|---|---|---|---|---|
| Nivel 3 | 3 | Nivel 2 | 107 | ninguno |
| Nivel 2 | 2 | Subcapítulo | 7 | 1 (el concepto vacío) |
| Concepto | 3 | Nivel 2 vacío | 7 | ninguno |

Los 7 de `Nivel 2` y los 7 de `Concepto` forman una sola rama vacía repetida —
**una por prototipo**.

### La regla

> Sin clave y sin descripción → **placeholder. Se descarta.**

Verificado sobre las 121: ninguna tiene importe distinto de cero, y ninguna tiene
hijos con clave. **Descartarlas no deja nada huérfano.**

### Pero se verifica, no se asume

El cargador comprueba antes de descartar:

- ¿Importe en cero? — sí en las 121
- ¿Sin descendientes con clave? — sí en las 121

Si alguna vez un placeholder tuviera un hijo costeado, **eso es un error que se
reporta, no una fila que se tira en silencio.**

### Por qué importa

Son el **3.7% de las filas**. Cargarlas crearía 121 nodos fantasma en el árbol,
agrupadores sin contenido que después habría que explicar.


## 2.6 `Origen` y el vocabulario de campos

`Origen` **es la categoría con otro nombre**. En este export trae un solo valor
porque solo hay conceptos; en un presupuesto desglosado traerá mano de obra,
materiales, herramienta y equipo.

`Origen` dice **de qué catálogo tomó el renglón, según el informe que se pidió**.
Este archivo es el informe de presupuesto; un desglosado traerá materiales,
trabajos y matrices.

| Valor de `Origen` | `categoria` |
|---|---|
| Presupuesto | concepto |
| Matrices | concepto |
| Materiales | material |
| Trabajos | mano de obra |

> `Presupuesto` y `Matrices` mapean al mismo lugar. Lo que los distingue es **qué
> informe generó el archivo**, que es metadato del archivo y no del renglón: se usa
> para mapear y se descarta.

### Lo que `Origen` NO responde

Que un renglón sea material no dice **quién lo puso ahí**. Esa segunda pregunta no
tiene campo hoy, y hace falta:

> `procedencia` es la única forma de distinguir un renglón de la capa CARGADO de uno
> que produjo el REDISEÑO (§11). Sin él, después de aplicar una receta no se puede
> contestar *¿esto lo trajo OPUS o lo hicimos nosotros?*

### Vocabulario de campos

En estos datos **`tipo` significa cuatro cosas, `nivel` tres, y `clase` ya está
tomada**. Esas tres palabras quedan quemadas. Cada campo responde **una sola
pregunta**:

| Campo | Pregunta | Valores |
|---|---|---|
| `rol` | ¿Qué es en el árbol? | ensamble · concepto · insumo |
| `clase` | ¿Bajo qué figura se ejecuta? | destajo · subcontrato · **acarreo** |
| `categoria` | ¿Qué referencia el renglón? | material · mano de obra · herramienta · equipo · contrato · **concepto** |
| `familia` | ¿De qué naturaleza es? | aceros · adhesivos · albañilería… |
| `procedencia` | ¿Qué lo creó? | importado · manual · ensamble · fusión · división · extracción · composición |
| `modo_precio` | ¿De dónde sale su precio? | calculado · declarado |
| `modo_cantidad` | ¿De dónde sale su cantidad? | heredada · manual |

**La palabra «origen» se retira.** Cargaba dos significados y chocaba con
`origen_precio` y `origen_cantidad`, que pasan a llamarse `modo_`.

### El sexto valor se llama `concepto`, no `matriz`

Por la regla de §10.1: *el concepto es concepto, la matriz es su desglose*. Un
renglón no **es** una matriz; referencia un concepto que **tiene** matriz. Si el
valor se llamara `matriz`, la contradicción quedaría dentro del dato.

> `matriz` se conserva como **sinónimo en el glosario**, porque es el término que se
> usa en obra. Canónico `concepto`, sinónimo `matriz`.

## 2.7 Qué pasa cuando el concepto cambió en OPUS

Si alguien modificó en OPUS la descripción, la unidad y la matriz de un concepto y
se vuelve a cargar, **el sistema no puede tratarlo como si nada hubiera cambiado**.
Pero los tres cambios no pesan igual:

| Cambió | Gravedad | Qué hace la carga |
|---|---|---|
| **Descripción** | Cosmético — se dice distinto, cuesta lo mismo | Normaliza. Alerta según §2.7.1, pero **carga** |
| **Matriz** | Económico — el PU se movió | **Versión nueva**, automática (§2.2) |
| **Unidad** | **Estructural** — deja de ser comparable | **Se detiene** ese concepto |

### Por qué la unidad es la peor

Si un concepto era `m²` y llega como `pza`, **las cantidades de todos los
presupuestos que lo usaron dejan de significar lo mismo**. Los 120 m² de ayer contra
las 120 piezas de hoy no son el mismo trabajo.

> Y ninguna suma va a fallar. Solo va a estar mal.

Por eso no es alerta pasiva: es alto. Alguien decide si fue una unidad mal
capturada o si es **otro concepto metido en la clave equivocada** — en cuyo caso lo
natural es clave nueva, y el sistema lo propone.

### 2.7.1 Qué diferencia de texto dispara alerta

**Un porcentaje de diferencia no sirve como regla**: engaña en los dos sentidos.
*De 3.00 a 4.20 m* es un cambio mínimo de texto y enorme de significado; reordenar
una frase es un cambio grande sin consecuencia.

**Primero se normaliza** —minúsculas, acentos, sinónimos del diccionario, quitar el
«Incluye:»— y se compara el núcleo. Idéntico → era cosmético, sin alerta.

Si difiere, se clasifica por **qué tipo de palabra cambió**:

| Cambió | Nivel |
|---|---|
| Un número o dimensión | **Alta** |
| El verbo o el elemento (*colocación* → *suministro*) | **Alta** |
| Puntuación, orden, calificativos | Informativo |

### Cruzar texto con huella

Lo que más señal da: si **cambió el texto de forma significativa Y cambió la
huella**, ya no es una descripción distinta.

> Es otro concepto. El sistema propone **clave nueva**.

### La huella del concepto

Defensa que no depende de comparar campo por campo:

```
huella = f(unidad, insumos, cantidades)
```

Se calcula al cargar y se compara con la anterior. **Si cambió, cambió** — aunque
el texto sea idéntico y aunque el PU dé la misma cifra por coincidencia.

> **La descripción queda fuera de la huella a propósito.** Si entrara, cada
> corrección de acento generaría versión y el versionado perdería sentido.

## 2.8 Correcciones legítimas de unidad

La diferencia entre corregir y crear no está en la intención de quien lo hace, sino
en **si algo ya depende del concepto**. Y eso el sistema lo sabe solo: cuenta
cuántos renglones lo usan.

| Situación | Qué se permite |
|---|---|
| **Sin uso** | Corrección libre. Se aplica y queda en bitácora |
| **Con uso, todo en diseño** | Corrección con alcance: se muestran los presupuestos afectados. Corregir en todos, o dejarlos y crear clave nueva |
| **Con algo contratado** | **No hay corrección.** Control de cambio o clave nueva |

> Así no depende de que alguien clasifique bien su propia intención — porque cuando
> corregir es incómodo, la tentación es marcarlo como corrección aunque no lo sea.

**Las cantidades no se convierten solas.** Si un concepto pasa de `m²` a `pza`, los
120 de un presupuesto existente no son 120 piezas. O quien corrige da el factor, o
cada presupuesto afectado queda marcado para revisión. Convertir en automático sería
inventar números.

## 2.9 La secuencia de carga

Cargar primero y corregir después no sirve: **ya se pisó el dato y se perdió contra
qué comparar.**

```
1. Se lee el archivo              nada se escribe todavía
2. Se compara contra lo vigente   huella por concepto
3. Se muestra el diagnóstico      qué entra, qué versiona, qué se detiene
4. Alguien resuelve               solo lo detenido
5. Se aplica                      todo junto
```

**Lo que se detiene no es la carga: son los conceptos en conflicto.** El resto entra
normal.

```
Carga de presupuesto — Prototipo Almendro

  412 conceptos entran sin cambios
   18 versionan — cambió su matriz
    3 detenidos — cambió la unidad

  ACA-01010  era m², llega como pza
             lo usan 4 presupuestos, todos en diseño
             → corregir en los 4  ·  dejar y crear clave nueva
```

Con esto **el atajo desaparece**: no es «corrijo antes para que no se detenga» ni
«cargo y luego arreglo». La carga muestra el conflicto y obliga a resolverlo con el
dato viejo y el nuevo a la vista — que es el momento en que se puede decidir bien.

> Si nadie resuelve y se va, la carga **queda guardada como pendiente**, con los
> conceptos en conflicto sin aplicar. Lo que no se hace es aplicarla a medias sin
> registro: entonces nadie sabe que faltan tres.


---

# 3. Notas de implementación

## 3.1 `ltree` en lugar de recursión

PostgREST genera la API sola desde las tablas. `?parent_id=eq.5` devuelve los hijos
directos — **un solo nivel**. Traer todo un subárbol necesita `WITH RECURSIVE`, y
eso no se puede escribir en una URL.

```sql
-- con recursión: hay que envolverla en función y llamarla por RPC
WITH RECURSIVE sub AS (...)

-- con ltree: es un WHERE, y PostgREST lo expone directo
WHERE ruta <@ '1.1'        →   ?ruta=cd.1.1
```

`<@` significa «desciende de». Con índice GiST, traer un subárbol completo es una
consulta indexada normal, sin recursión y sin función intermedia.

## 3.2 Sin MPTT ni treebeard

Las dos guardan la posición dentro de la fila: MPTT con dos números (`lft`,
`rght`), treebeard con una ruta de texto. Las consultas son rápidas, pero **ambas
se reescriben al mover un nodo** — en MPTT un movimiento puede tocar cientos de
filas, porque renumera todo lo que queda a la derecha.

> El riesgo real: que un reporte, una integración o un contrato guarde el `lft` o
> el `path` como referencia. El día que se mueva un nodo, apunta a otra cosa.
> **La referencia siempre es el `id`.**

Recomendación para este stack: `parent_id` más `ltree` en Postgres, y que Django
solo mapee la llave foránea. Dos mecanismos de árbol compitiendo, uno en el ORM y
otro en la base, es una fuente de desincronización innecesaria.

> **Matiz que impone la arquitectura limpia (§3.4):** la base es el lugar *más
> rápido para recorrer* el árbol, no la dueña de las reglas. `ltree` va detrás de
> un puerto de repositorio. **El recorrido es infraestructura; la regla de qué suma
> a qué es dominio.**

## 3.3 La estructura y el stack

**Tres carpetas:**

```
backend/     ← Render
database/    ← Supabase
frontend/    ← web en Vercel · móvil en Google Studio
```

### Dónde corre cada cosa

| Pieza | Qué aporta | Cuidado |
|---|---|---|
| **PostgreSQL** | `id bigint GENERATED ALWAYS AS IDENTITY`, `parent_id` autorreferencial, `ltree` para la ruta | El WBS se calcula, no se captura |
| **Supabase** | Es Postgres: `ltree` y `gen_random_uuid()` disponibles | Los recorridos de árbol van por RPC o vista |
| **Python / Django** | `parent = ForeignKey('self')`, `Decimal` en toda la ruta del dinero | Nunca `float` |
| **Render** | Backend y base | — |
| **Vercel** | Frontend **web** | **Serverless agota conexiones.** Cadena *pooled* para la app, directa solo para migraciones |
| **Google Studio** | Frontend **móvil** | Consume la misma API del backend; nunca la base directo |

## 3.4 Arquitectura

**Monolito con fachadas, migrable a microservicios.** Arquitectura *screaming* y
*clean*, para evitar el efecto espagueti.

### Qué implica

- **Screaming** — la estructura de carpetas grita el dominio, no el framework. No
  `models/`, `views/`, `serializers/`, sino `presupuesto/`, `apu/`, `catalogo/`.
- **Clean** — el dominio al centro, la infraestructura al borde. El dominio **no
  sabe** que existe Django, Postgres ni el ERP externo.
- **Fachadas** — cada módulo expone un solo punto de entrada; lo interno es privado.
  Mañana una fachada se vuelve el borde de un servicio.

> Los nombres de los módulos salen del **glosario** (`GLOSARIO-DOMINIO.md`). Si el
> vocabulario ya está normalizado, la estructura de carpetas se escribe sola.

### Los módulos

| Módulo | De qué es dueño |
|---|---|
| `catalogo` | Insumos, unidades, familias, conceptos, claves |
| `apu` | Matrices, explosión, versionado (§2.2) |
| `presupuesto` | Árbol, WBS, cantidades, estados |
| `parametrico` | Ensambles: plantilla e instancia (§5) |
| `rediseno` | Las cuatro operaciones y las tres capas (§8, §11) |
| `programa` | Actividades, asignaciones, avance |
| `contratos` | Contratación, estimaciones, control de cambio |
| `diccionario` | Términos, equivalencias, homologación |
| `importacion` | Carga desde OPUS |
| `exportacion` | Cabeceras, Materiales, Operaciones |

### Lo que la arquitectura confirma

- **`Ingenieria ERP` es un formato ajeno.** En Clean, el ERP externo es un
  adaptador de borde: el dominio nunca conoce el código de 7 dígitos, solo el árbol
  (§4.2).
- **El WBS se calcula, no se guarda.** Es presentación, y la presentación vive
  afuera (§1.1).
- **`Origen` se traduce al entrar.** El vocabulario externo se mapea a `categoria`
  en el borde; adentro solo existe el nuestro (§2.6).

## 3.5 El motor de cálculo no se puede partir

`presupuesto`, `apu` y `parametrico` usan **el mismo cálculo**: la suma de partes
(§7.2). No es coincidencia: es el mismo árbol recursivo en tres niveles.

> Ese motor es un **núcleo compartido**. No es un módulo más: es de lo que dependen
> los otros tres.

Consecuencia al migrar a microservicios: **las costuras naturales no están donde
parece.** Separar presupuesto de APU obligaría a duplicar el motor o a una llamada
remota por nodo del árbol — inviable con miles de nodos.

Las costuras que sí funcionan son las que **no participan del cálculo recursivo**:

| Se puede separar | Por qué |
|---|---|
| `importacion` / `exportacion` | Hablan con sistemas externos, no con el árbol |
| `diccionario` | Consulta de vocabulario, sin cálculo |
| `contratos` | Consume totales ya calculados |
| `programa` | Reagrupa; no reasigna ni recalcula (§11.3) |

Que `programa` sea separable no es casualidad: **la regla de que nada reasigna** es
justo lo que lo desacopla del cálculo.


---

# 4. Estados del nodo y exportación

## 4.1 Pendiente de costear

Un agrupador puede existir antes de tener contenido. Comprobado en el presupuesto:

| Clave | Descripción | Prototipos | Importe |
|---|---|---|---|
| `ACA-00021` | Cubiertas cocina | 7 | $0.00 |
| `NIV-00015` | Consumibles | 7 | $0.00 |

Más **5 conceptos con precio unitario en cero**: `IGAS-02131`, `IGAS-02132`,
`ACC-00003`, `ISN-02061` (×2).

### La regla

> **Lo que no está costeado no se puede contratar ni programar.**

No es un filtro de presentación: es una restricción del sistema. Un nodo sin costo
no puede entrar a un contrato, a una estimación ni a una actividad del programa.

### El riesgo que introduce

Un agrupador vacío **aporta cero y no se queja**. El total del presupuesto sale
más bajo de lo que corresponde, sin ninguna señal.

Hoy el total declarado es **$16,460,623.50**, y está subestimado por lo que valgan
Cubiertas cocina y Consumibles en los siete prototipos.

Por eso el estado tiene que ser explícito y visible, no deducirse de un cero:

| Estado | Contratable | Programable |
|---|---|---|
| **Costeado** | Sí | Sí |
| **Pendiente de costear** | **No** | **No** |

### Cantidad estimada con precio alzado: la combinación peligrosa

Cruzando el modo de la cantidad (§7.1) con el del precio:

| Cantidad | Precio | Riesgo |
|---|---|---|
| Medida | Cualquiera | Normal |
| **Estimada** | **Por PU** | Aceptable: se ajusta con la cantidad real |
| **Estimada** | **Alzado** | **Alto** |

> Si la cantidad vino de un paramétrico **y** encima se fija el total, se está
> comprometiendo un monto sobre una suposición. Con precio unitario el riesgo se
> corrige al medir; **con alzado no hay ajuste posible**.

El sistema debe advertirlo al contratar, no después.

Y el total del presupuesto debe mostrar **cuántos nodos pendientes contiene**. Un
presupuesto con pendientes no es un presupuesto terminado, aunque sume.

## 4.2 `Ingenieria ERP` y `Nivel ERP` se generan

Las dos son **salida, no entrada**. Se recalculan cuando cambia la agrupación o la
posición, igual que el WBS.

| Campo | Cómo se genera |
|---|---|
| `Ingenieria ERP` | Del WBS, con ancho de segmento fijo |
| `Nivel ERP` | Del nivel de construcción al que pertenece el nodo |

### El techo vuelve aquí

Internamente el WBS con puntos no tiene límite de hermanos (§1.1). **Pero el
formato numérico sí**: dos dígitos por segmento topan en 99, y **el ERP externo no
admite un tercer dígito**.

Es un techo duro. Y por eso **el remedio no es ampliar el código: es reagrupar el
árbol**, insertando un nivel intermedio que reparta los hijos.

| Hijos | Qué hace el sistema |
|---|---|
| Hasta 89 | Nada |
| **90 en adelante** | **Alerta**: se acerca al límite, conviene agrupar en subniveles |
| 100 | La exportación **se detiene**, nombrando el nodo |

> **Nunca truncar ni reciclar el código.** Produciría un archivo que se ve válido
> con dos nodos compartiendo número — y eso se descubre tarde, del lado de ellos.

### Advertencia sobre el ERP externo

El código **cambia cuando se reordena**. Si el otro ERP lo usa como llave, mover un
nodo aquí rompe su referencia allá, y es un sistema sobre el que no hay control.

> Conviene mandarle también el `id` interno, que no cambia nunca. Si no acepta un
> campo extra, hay que saber que la referencia entre sistemas es frágil por diseño.

## 4.3 Los tres reportes de salida

El ERP externo se alimenta de tres reportes:

| Reporte | Qué contiene |
|---|---|
| **Cabeceras** | *(pendiente de especificar)* |
| **Materiales** | *(pendiente de especificar)* |
| **Operaciones** | *(pendiente de especificar)* |

**Hipótesis a confirmar:** cabeceras son los nodos estructurales del árbol;
materiales, las hojas de tipo material con su cantidad; operaciones, las de mano de
obra y destajo. Es decir, el mismo árbol partido en tres por tipo de hoja.

Falta definir de cada uno: columnas exactas, si llevan el árbol completo o solo lo
costeado, y si el ERP externo los consume por archivo o por API.

---

# 5. Presupuesto paramétrico — ensambles

## 5.1 Qué es

**El mismo mecanismo del APU, un piso más arriba.**

```
APU           concepto  →  insumos    con cantidad
PARAMÉTRICO   ensamble  →  conceptos  con cantidad
```

No es un módulo con reglas propias: es el árbol recursivo aplicado a otro nivel de
abstracción. Y es un **documento aparte** del presupuesto, igual que el concepto es
aparte de sus insumos.

```
ensamble       Recámara tipo A        ← el nivel nuevo
  concepto       Aplanado en muros
    insumo         Estuco, mano de obra
```

Es desglosable: un ensamble puede contener sub-ensambles. *Recámara* contiene
*Baño*, que contiene WC, regadera y lavamanos.

## 5.2 Plantilla e instancia

Es la misma distinción que ya existe un piso abajo: el APU de *aplanado en muros*
no se contrata; los 279 m² de aplanado de la Zafiro sí.

| | Qué es | Contratable | Programable |
|---|---|---|---|
| **Plantilla** | *Recámara tipo A*. Una receta | No | No |
| **Instancia** | *Recámara 1 del lote 14*, con cantidades reales | **Sí** | **Sí** |

**La instancia es lo que reemplaza al presupuesto detallado actual.** Se opera sobre
30 ensambles en vez de 400 conceptos; el detalle sigue abajo dando el precio.

## 5.3 La cantidad es receta, no volumen

Aquí se disuelve la pregunta del traslape.

Un ensamble puede tomar **1 regadera aunque el presupuesto tenga 3**, y los muros
que corresponden a esa regadera aunque en planta baja haya para tres. La relación
lleva **su propia cantidad**.

> Por lo tanto el paramétrico **nunca tuvo que cuadrar con el presupuesto**. No es
> una partición ni una vista: es un ensamble armado con piezas encontradas ahí.

Un concepto puede estar en varios ensambles sin que eso sea doble contabilidad.

## 5.4 De dónde sale la cantidad

Tres orígenes, y **el origen es un campo explícito del renglón**:

| Origen | Ejemplo |
|---|---|
| **Heredada del concepto** | La cantidad que el concepto tiene en el presupuesto |
| **Heredada de un destajo** | Los m² de un destajo dentro del concepto auxiliar |
| **Manual** | Capturada a mano |

> **Heredar es mejor que capturar.** Los m² de losa muchas veces ya están en los
> datos: son la cantidad de algún destajo. Heredados, el día que cambie el volumen
> el ensamble se entera. Capturados, se desincronizan en silencio y nadie se entera.

## 5.5 Dos explosiones, no una

| Explosión | Contiene | Para qué |
|---|---|---|
| **De costo** | Todo: materiales, destajos, subcontratos | Da el precio |
| **De contratación** | Solo destajos, agrupados por sub-ensamble | Se paga y se programa |

Como pedir una hamburguesa y que el desglose muestre lo que se pagó por hacer el
pan y por cortar la verdura: **los sub-ensambles son la unidad natural de
contratación**, porque es donde el destajo tiene sentido para quien ejecuta.

## 5.6 La referencia apunta al concepto

Al armar un ensamble se navega el presupuesto —es donde las cosas están en su
contexto— pero **lo que se guarda es el concepto, no el renglón**.

Si se guardara el renglón, borrar o reordenar ese presupuesto dejaría el ensamble
colgando de algo que ya no existe. Apuntando al concepto, *Recámara tipo A* sigue
siendo armable aunque la Zafiro desaparezca — que es justo lo que hace falta para
componer un diseño nuevo desde el prototipo más parecido.

El presupuesto de origen se guarda como **referencia informativa**, no como liga
estructural.

## 5.7 El parámetro y la cohorte — medido

Se probó sobre los siete prototipos si el costo escala con los m².

**Un paramétrico global no funciona.** El costo por m² va de $8,717 a $11,841:
**36% de variación**.

**Por subcapítulo, algunos sí:**

| Subcapítulo | $/m² | Dispersión |
|---|---|---|
| Acabados | 911 | **5%** |
| Planta alta | 1,371 | 10% |
| Carpintería | 1,063 | 11% |
| Cancelería | 405 | 20% |
| Cimentación | 931 | 23% |
| Herrería | 116 | **38%** |

**Y la cimentación revela por qué falla:**

```
1 planta    Zafiro 1,039    Rubí 1,012    Jade 1,053         → CV  2%
2 plantas   ZafPlus 660   Diam- 1,090   Diam+ 1,085  Oro 577 → CV 32%
                                                     juntos  → CV 23%
```

En una planta la cimentación por m² es prácticamente idéntica. Lo que la rompía era
mezclar cohortes.

### Corrección: la cohorte no es el número de plantas

Separar por plantas mejoró el número, y eso hizo creer que la explicación era ésa.
**No lo es.** Los dos Diamante tienen planta alta y su cimentación por m² se comporta
igual que la de una planta:

| Grupo | Prototipos | $/m² | CV |
|---|---|---|---|
| **A** | Zafiro 1.0, Rubí, Jade, Diamante −, Diamante + | 1,056 | **2.8%** |
| **B** | Zafiro Plus, Oro 4.01 | 618 | 6.7% |

**Cinco de los siete comparten tasa, tengan una planta o dos.** Los que se salen son
Zafiro Plus y Oro, y están **1.71× por debajo** — eso no es dispersión, es otra
población.

> **La lección es de método, no de cimentación:** una partición que mejora el número
> no queda probada por mejorarlo. La de plantas bajaba 23% a 2% en un subgrupo y
> dejaba el otro en 32% — **el residuo alto era la señal de que la explicación estaba
> incompleta, y se leyó como ruido.**

Qué separa al grupo B sigue sin saberse (B-52). Lo que sí se sabe es que **no es el
número de plantas.**

### B-49 cierra: la Δ es redondeo del PU en la explosión, confirmado en los siete

D-124 (sesión anterior) probó un prototipo y predijo: la Δ$4.30 es compatible con
redondear el **PU** a centavos antes de multiplicar, no con redondear el importe
(eso daría solo ±$0.11) — comprobable, dijo, sobre los siete.

Repetido con el motor de explosión (`explosion_recursiva.py`): explotar cada
concepto por su matriz y sumar el costo atómico, contra el importe declarado del
catálogo maestro. Primero salió mal — $220,137 de diferencia en Zafiro 1.0 — pero
la causa no era el redondeo: **8 conceptos de subcontrato** (`CAR-`, `CAN-`,
`HER-04010`) tienen una matriz de relleno que no llega ni al 1% de su valor real,
mismo patrón que los `SUB-` de `ALAMO 18` (§11.14) — no se construyen del
catálogo, no hay receta que explotar.

Excluidos esos 8, el drift de Zafiro 1.0 cae a **-$4.59** — el mismo orden que el
$4.30 original. Repetido sobre los siete:

| Prototipo | Drift |
|---|---:|
| Zafiro 1.0 | -$4.59 |
| Rubí | -$4.68 |
| Zafiro Plus | -$3.15 |
| Jade | -$4.29 |
| Diamante sin chimenea | -$6.42 |
| Diamante con chimenea | -$7.73 |
| Oro 4.01 | -$8.28 |

**Siempre negativo, y crece con la complejidad del prototipo — la firma de
redondeo acumulado, no de un error.** El total (-$39.14) no calza con el "~$11"
que predijo D-124, pero esa predicción era una extrapolación simple sobre un solo
caso — el mecanismo, que es lo que importaba, queda comprobado en los siete, no
solo en uno. D-311.

> **El paramétrico no falla por ser paramétrico. Falla por usar el parámetro
> equivocado o la cohorte equivocada.**

De ahí, tres reglas:

- **Parámetro propio por ensamble.** Cimentación escala con desplante, instalaciones
  con salidas, no todo con el m² total.
- **Cohorte explícita.** Cada ensamble declara a qué aplica. Fuera de ella, no se usa.
- **La dispersión se guarda junto al valor.** Acabados a $911 ±5% es utilizable;
  Herrería a $116 ±38% es una adivinanza. Un precio sin su dispersión es un número
  disfrazado de certeza.

## 5.8 Funciona en las dos direcciones

```
Extracción    presupuesto → ensamble     se arma la plantilla desde lo ya hecho
Generación    ensamble → presupuesto     se compone una casa nueva
```

**Las dos conviven sobre el mismo documento.** Se toma 1 regadera para la recámara 1,
y lo que sobra alimenta las recámaras 2 y 3. Sobrantes y faltantes son normales.

### El residuo es un indicador, no un error

```
presupuesto = Σ ensambles + conceptos sueltos
                              └── «el 12% de esta casa no está sistematizado»
```

Los conceptos sueltos miden **cobertura**, y son los candidatos naturales para el
siguiente ensamble.

> El residuo solo tiene sentido **en generación**. En extracción no significa nada:
> tomar 1 de 3 regaderas no deja residuo, deja lo que no se quiso.

### Editar un presupuesto generado

Si se genera desde ensambles y luego se edita una cantidad a mano, al regenerar
**no se arrasa ni se respeta en silencio**: el renglón se marca como
**desvinculado** y se muestra la divergencia. Resolverla es decisión de alguien.

## 5.9 Las pantallas

| Momento | Pantalla |
|---|---|
| **Armar** | Dos paneles: presupuesto arriba, ensamble abajo. Tomar un renglón crea la relación con cantidad propia |
| **Ver cobertura** | La pantalla de presupuesto con una columna más: a qué ensambles pertenece cada concepto. Es una lista, porque puede estar en varios |
| **Componer** | Catálogo de ensambles. Se eligen y se ponen cantidades: 3 recámaras, 2 baños |
| **Receta de rediseño** | No es árbol: lista ordenada de operaciones con su estado al aplicarse (§9) |

El divisor vive **en el ensamble**, no en cada renglón. Los sub-ensambles se ven
igual que un concepto, con su icono. Y las cantidades son editables desde el
inicio, porque son receta y no volumen medido.


## 5.10 Cuantificador y paramétrico no compiten

```
CUANTIFICADOR    plano → medida → cantidad          mide lo que hay
PARAMÉTRICO      cantidad ÷ divisor → tasa          aprende de lo medido
                 tasa × divisor nuevo → cantidad    estima lo que no está
```

El cuantificador **produce** cantidades. El paramétrico **las consume para
aprender** y después las **genera** cuando no hay plano que medir.

> **El paramétrico se calcula desde lo cuantificado, no en lugar de ello.** La tasa
> de $1,039/m² de cimentación salió de casas realmente medidas. Sin cuantificación
> previa no hay paramétrico: solo habría una opinión.

Lo que los distingue no es la técnica, sino **en qué momento del proyecto se está**:

| Se tiene | Se usa | Precisión |
|---|---|---|
| Planos ejecutivos | Cuantificador | Alta, medida |
| Croquis o programa arquitectónico | Paramétrico | Estimada, con su dispersión |
| Planos parciales | **Los dos, por renglón** | Mezclada |

**El tercer caso es el normal**: la cimentación ya está en planos y se mide,
acabados todavía no y se estima. Ninguno es dueño del presupuesto completo.

### El campo que evita el choque

`modo_cantidad` (§7.1) dice **cómo se obtuvo cada cantidad**. Con él:

- Se ve **qué tanto de un presupuesto está medido y qué tanto estimado**
- Se sabe qué renglones reemplazar cuando lleguen los planos
- Cuando un trazo sustituye a una estimación, **queda registrado cuánto se movió** —
  que es lo que dice si los paramétricos son buenos

### Los dos arranques

| Se arranca | Qué pasa |
|---|---|
| **Desde cero** | El paramétrico compone la estructura con cantidades `estimada`. El cuantificador las sustituye conforme haya planos |
| **Copiando un presupuesto base** | Las cantidades llegan como `heredada` — honesto: no son de esta obra. Y eso dice qué falta revisar |


---

# 6. Destajos: precio, cuadrilla y fusión

## 6.1 Los tres estados

| Estado | De dónde sale el PU | Si sube la cuadrilla |
|---|---|---|
| **Capturado** | Negociado a mano | No se mueve |
| **Enganchado** | De la cuadrilla | **Sube** |
| **Fusionado** | Ponderado de sus orígenes | Según sus orígenes |

> El origen del PU es un **campo visible del destajo**, no una convención implícita.
> Si no, nadie entiende por qué unos precios se movieron y otros no.

## 6.2 Los tres rendimientos

**No es uno, son tres**, y solo dos se capturan:

| Rendimiento | De dónde viene | ¿Se captura? |
|---|---|---|
| **Calculado** | `costo de la cuadrilla ÷ precio del destajo` | **Nunca.** Siempre existe |
| **Teórico** | El que se supone al presupuestar | **Sí** |
| **Real** | El medido en obra | **Sí**, después |
| **Requerido** | El que haría falta para cumplir la fecha del programa | **Nunca.** Sale del CPM |

> **El requerido se agregó con el módulo de programa.** Es derivado como el
> calculado: nadie lo captura y no sobrescribe a ninguno de los otros tres.

### El calculado sale del enganche

```
Al enganchar la cuadrilla
   jornadas por unidad = precio del destajo ÷ precio de la cuadrilla
   $50/m² ÷ $1,452/jornada → 0.0344 jor/m² = 29.04 m² por jornada

Si la cuadrilla sube a $1,600
   el destajo calculado sube: 0.0344 × 1,600 = $55.10/m²
```

**Esto resuelve un hueco real:** el rendimiento calculado no hay que capturarlo ni
inventarlo — sale del precio ya negociado.

Y da el dato que le falta al Gantt: esos 29 m²/jornada son lo que la fórmula de
duración necesita.

### Acortar la duración: qué se mueve y qué no

En el programa se puede acortar una actividad a mano. **El precio del destajo nunca se
mueve** — eso ya está decidido para lo contratado (P-4) y vale igual en base.

```
1. baja el número de cuadrillas          ← variable libre primaria
2. si sólo queda una, la que absorbe     ← rendimiento REQUERIDO
   es el rendimiento
3. el precio del destajo no se toca      ← nunca
```

**Un tiempo más corto no significa que el rendimiento inicial cambie.** Significa que
haría falta otro para cumplir la fecha, y esa distancia es información:

| requerido vs calculado | Qué dice |
|---|---|
| Requerido **mayor** | La fecha exige más de lo pactado — o se mete gente, o el destajo está barato |
| Requerido **menor** | Hay holgura, o el destajo está caro |

> **No corrige nada: alimenta la renegociación futura.** Es el mismo mecanismo de la
> comparación de rendimientos que ya existe, aplicado al eje del tiempo.

### La comparación es el indicador

> Si el **calculado** y el **teórico** difieren, una de tres: el precio del destajo
> está mal, la cuadrilla asignada no es la correcta, o **la productividad real no es
> la que el precio supone**.

Comprobado con los datos reales: al comparar los 265 trabajos, la razón entre uno y
otro dio **1.085 en los 22 trabajos de pintor, sin variación**, y 1.085 en 58 de 78
de albañil.

**No era desajuste: era un cambio de salario.** Los rendimientos teóricos se habían
calculado con una cuadrilla que costaba 8.5% más que la actual.

En instalaciones no hay factor único —la razón va de 0.03 a 4.9 en eléctrico—, así
que ahí el teórico heredado **no es confiable** y conviene tomar el calculado.

### Cuidado con los subcontratos

En un subcontrato el precio **no es solo mano de obra**: incluye material,
herramienta y la utilidad del tercero. Dividir el costo de la cuadrilla entre ese
precio da un rendimiento bajo por construcción.

> **El enganche solo aplica a destajos.** En subcontratos el rendimiento se captura,
> no se deduce.

Se ve en los cuatro subcontratos a **$1.00** —precio de alzado— cuyo rendimiento
calculado sale absurdo.

### La unidad va anclada al rendimiento

Arrastra tres anclajes —obra, tiempo y **cuál cuadrilla**—. Ver `IDEAS.md` §5.

### El "real" de este cuadro es de mano de obra — hay otro real, y no es el mismo dato

**"Rendimiento real" nombra dos cosas distintas en este sistema, y mezclarlas repite
un error ya cometido:**

| | Rendimiento real de **mano de obra** | Rendimiento real de **material** |
|---|---|---|
| Qué mide | Cuadrillas × avance físico ÷ tiempo | Insumo consumido ÷ unidad de avance |
| Quién lo registra | El residente, al capturar avance y cuadrillas | Se concilia después, contra salida de almacén |
| Vive en | Esta sección (§6.2) | §11.16 · §11.17 |
| A quién alimenta | **Solo al programa** (`PROPUESTA-CUATRO-MODULOS.md` §4) | Al costo — Presupuesto Formado, control de cambio. **Nunca al programa** |

> Mezclarlos repite D-252 en la otra dirección: ahí comparar material contra un total
> que incluía mano de obra infló la brecha. Explicar un retraso de cuadrilla con el
> rendimiento del material —o al revés— sería el mismo error.

El teórico **nunca se sobrescribe** con ninguno de los dos reales — misma cadena que
el precio (§13.1). Si el real de mano de obra diverge, el programa gana una
**segunda proyección que convive con la teórica**, no un reemplazo —
`PROPUESTA-CUATRO-MODULOS.md` §4.

## 6.3 Es un APU de un solo insumo

El destajo enganchado no es un caso especial:

```
destajo enganchado
└── cuadrilla × (jornadas por unidad)      ← el inverso del rendimiento
```

Es un APU con un componente. Por eso la relación es **bidireccional**, igual que
cualquier APU:

| Cambia | Efecto |
|---|---|
| Precio de la cuadrilla ↑ | Destajo ↑ |
| **Rendimiento ↑** | **Destajo ↓** (menos jornadas por unidad) |

Y como cualquier cambio de APU, se propaga al concepto y **crea versión** (§2.2).

## 6.4 Fusión

Fusionar destajos —*salida hidráulica* + *salida sanitaria* = *hidro-sanitaria*—
crea un destajo nuevo. El precio se propone **siempre ponderado por cantidad**, y
se puede ajustar a mano; siempre se puede volver al ponderado.

**Por qué ponderado y no promedio simple:**

```
 5 × $85 =   425          Promedio simple:    $82.50 → 40 × 82.5 = 3,300   +$75
35 × $80 = 2,800          Ponderado:          $80.63 → 40 × 80.63 = 3,225   neutro
           ─────
           3,225
```

El promedio simple parece justo y no lo es: las cantidades están 7 a 1.

> **El ponderado es la línea base.** El indicador de ahorro o pérdida es siempre
> *precio decidido − precio ponderado, por la cantidad total*. Así la pregunta
> «¿comparado contra qué?» ya viene contestada.

El resultado puede **bajar o subir** el presupuesto. Las dos son decisiones
legítimas; el sistema solo tiene que mostrarlo.

### Reglas de la fusión

- **Unidades compatibles.** Sin unidad común no hay promedio posible. El sistema
  lo impide.
- **No reemplaza a los originales.** El fusionado convive con ellos: los originales
  siguen disponibles para presupuestar —el repello a 4.20 m sigue haciendo falta
  para una casa con muro alto—, el fusionado se usa para contratar y programar.
  Mismo principio que no reescribir la clave.
- **Solo en presupuestos en diseño.** Sobre lo contratado va por control de cambio.
- **Si los destajos son enganchados**, fusionar cuadrillas cambia el rendimiento, y
  el precio nuevo puede salir del modelo en vez de teclearse.


---

# 7. Modos de valuación

**No son cuatro tipos de presupuesto: son cuatro modos de valuar un renglón.**
Si el mixto existe —y existe, porque los subcontratos van a precio alzado—
los otros tres son casos particulares suyos.

```
ASCENDENTE    el precio sube de los hijos      ← PU, APU, ensamble, paramétrico
DESCENDENTE   el precio se declara y baja      ← alzado
```

Ese es todo el motor. El **mixto no es un quinto caso**: es un árbol con nodos de
las dos clases.

## 7.1 Dos campos, independientes

```
Nodo
  rol             ensamble | concepto | insumo      ← qué es en el árbol
  categoria       material | mano de obra | … | concepto
  procedencia     importado | manual | fusión | …   ← qué lo creó
  modo_precio     calculado | declarado             ← de dónde sale su número

Relación padre → hijo
  cantidad
  modo_cantidad   medida | estimada | capturada | heredada
```

| `modo_cantidad` | De dónde viene | Trae consigo |
|---|---|---|
| `medida` | Un trazo del cuantificador | Su evidencia: plano, versión, capa |
| `estimada` | Un paramétrico | Su dispersión (§5.7) |
| `capturada` | Alguien la escribió | — |
| `heredada` | Copiada de otro presupuesto | De cuál |

**El padre no hereda nada de sus hijos.** Un ensamble puede contener conceptos por
PU, conceptos alzados y otros ensambles a la vez, y sigue siendo un ensamble.
Mezclar es lo normal.

```
ensamble   Recámara tipo A                    calculado
├─ concepto  Aplanado en muros    120 m²      calculado    (APU)
├─ concepto  Subcontrato cocina     4 ml      declarado    (alzado con desglose)
│   └─ concepto  Cajones            8 pza     calculado
└─ ensamble  Baño tipo B             1        calculado
```

> **El presupuesto no tiene tipo.** «Mixto» no se guarda: es una descripción de lo
> que contiene. Se puede reportar —*68% por PU, 22% ensamble, 10% alzado*— y eso es
> una medida, no una etiqueta.

## 7.2 Las partes siempre suben

> **El nodo hoja aporta su valor. El nodo con hijos aporta la suma de sus hijos.**
> Sin excepción: fusiones, divisiones, extracciones, auxiliares, APU, alzados.

Es la regla ya verificada contra el presupuesto real: 665 nodos con hijos, 665
cuadran (`CATALOGOS.md` §1).

El alzado no la rompe. Sin hijos, es hoja y su valor declarado sube. Con hijos,
suben ellos y **el declarado queda como cifra paralela** — mismo trato que el PU
importado: señal, no dato.

## 7.3 Dos totales que conviven

```
Costo        suma de las partes         ← lo que cuesta
Contratado   suma de lo pactado         ← lo que se va a pagar
```

No compiten: uno es el presupuesto, el otro la cartera de contratos. **La
diferencia es el margen o la exposición**, visible por nodo y acumulada.

Y es el mismo indicador de la fusión (§6.4) y de la extracción: *declarado menos
calculado*. Tres situaciones, un solo mecanismo.

> Todo renglón alzado necesita un **PU sombra** como base de reparto. Sin él no se
> puede estimar avance parcial, ni programar, ni controlar material. Sale del
> presupuesto por PU.

---

# 8. Operaciones de rediseño

Cuatro operaciones de la misma familia. Todas reagrupan lo mismo con distinta forma.

| Operación | Qué hace | Inversa |
|---|---|---|
| **Fusión** | Varios destajos → uno (§6.4) | División |
| **División** | Un concepto con 3 destajos → 3 conceptos | Fusión |
| **Extracción** | Materiales sin destajo → concepto propio | — |
| **Composición** | Varios conceptos → un concepto nuevo (§9) | Explosión |
| **Clonación** | Un insumo → otro igual con clave nueva (§8.4) | — |

## 8.1 Las cuatro reglas comunes

1. **Conservación medida contra la línea base.** El ponderado por cantidad es
   siempre la base; la diferencia es el indicador de ahorro o pérdida.
2. **No reemplaza al original.** Lo nuevo se agrega. El repello a 4.20 m sigue
   haciendo falta para una casa con muro alto.
3. **Solo en presupuestos en diseño.** Sobre lo contratado va por control de cambio.
4. **Bitácora de quién lo hizo.**

## 8.2 Conservación fuerte, no por pieza

La verificación débil —que ninguna parte supere al original— deja pasar el caso feo:

```
concepto de $100  →  se divide en $60 y $50
                     cada uno es menor que $100
                     juntos son $110
```

**La verificación es de suma**: las partes contra el original, con la diferencia
visible.

## 8.3 Qué hacer con lo que no tiene dueño

Al dividir, cada destajo se va con lo suyo. Pero el agua, el andamio y el acarreo
sirven a las tres partes.

**Lo decide quien hace la división, parte por parte.** El sistema puede recordar
repartos anteriores y **proponer** para casos similares, pero nunca aplicarlos solo:
si recuerda que el andamio fue proporcional y lo hace sin preguntar, alguien firma
un reparto que no revisó. Mismo principio del diccionario: propone, no aplica.

## 8.4 Clonar un insumo

Crear un insumo nuevo copiando el contenido de otro. **No edita: crea**, y por eso
produce clave — igual que las cuatro operaciones anteriores.

### El uso principal son las variantes

Partir de la trabe T-3 y crear la T-4 cambiando la sección, **sin capturar todo de
nuevo**. Arreglar un prefijo equivocado (`IDEAS.md` §6) es apenas un caso particular.

### Dos modos

| Modo | Qué pasa con el original | Cuándo |
|---|---|---|
| **Clonar y mantener** | Sigue vivo y disponible. **Los dos se usan** | Variante real: la T-3 y la T-4 conviven |
| **Clonar y sustituir** | **Todo lo que apuntaba al original pasa al clon** | No se quieren dos iguales: la misma trabe con otro nombre |

### La sustitución sí toca lo existente

Mueve referencias en presupuestos y matrices. Por eso **tiene el mismo alcance que
la corrección de unidad** (§2.8):

> **Libre en diseño. Se detiene donde hay contrato** — lo contratado no se reescribe.

Y el aviso importa más que en el otro modo: **cuántas líneas se van a redirigir y en
qué presupuestos**, antes de aceptar.

### La equivalencia se registra

El clon apunta a su origen, en el diccionario. Sin eso, un año después nadie sabrá
que `PRE-00120` y `AUX-00001` son la misma trabe: quedarían como dos insumos
distintos con el mismo precio.

---

## 8.5 Borrar un insumo

> **La clave nunca se reescribe. Se puede borrar, pero solo mientras nada dependa de
> ella.**

Es **la cuarta vez que aparece la misma regla** —§1.4 el catálogo al contratar,
§2.8 la unidad del concepto, §13.2 el precio pactado—. Cambia el dato, no la lógica:
*mientras nada dependa, se corrige o se borra; en cuanto algo dependa, se agrega
encima.*

### La condición es objetiva

El sistema **cuenta las referencias**, no lo juzga alguien:

- No está en ningún presupuesto ni en ninguna capa de matriz, **o**
- Está, pero **con cantidad cero**

> Una línea en cero es una **referencia de forma, no de fondo**: no aporta al costo
> ni al consumo.

El conteo debe mirar también **compras y estimaciones**, no solo presupuestos: un
insumo comprado directo tiene historia aunque ningún presupuesto lo use.

### El borrado no baja

Dos direcciones, y solo una se toca:

| Dirección | Qué pasa |
|---|---|
| **Hacia arriba** | Las líneas donde aparece **en cero se eliminan** — referencian algo que deja de existir |
| **Hacia abajo** | **Nada** |

Si se borra una mezcla que adentro tiene cemento en cero y arena en cinco, **el
cemento y la arena siguen existiendo** en el catálogo, con todos sus otros usos
intactos. Lo que desaparece es la mezcla.

> Sus propias líneas de composición sí se van con ella —la de cemento y la de
> arena—: no tienen sentido sin la mezcla, **son su definición**.

Y nada con cantidad se toca en ningún sentido: **si algo lo referencia con cantidad,
el insumo ni siquiera es borrable.**

### El aviso

Antes de aceptar: **«se va a eliminar de 3 matrices donde está en cero»**.

### Los dos mecanismos encajan

**Sustituir es lo que deja borrable al original.** Después de una sustitución, nadie
le apunta y cae justo en la condición de borrable. Pero **borrar es un acto aparte**,
que se decide después.

---

# 9. Concepto compuesto — matriz dentro de matriz

Es **distinto del ensamble en un punto que lo cambia todo: produce clave nueva**, y
por eso entra al catálogo.

| | Clave nueva | Vive en | En el presupuesto |
|---|---|---|---|
| **Ensamble** | no | catálogo de ensambles | aparece como sus partes |
| **Concepto compuesto** | **sí** | catálogo de conceptos | **un renglón** |
| **Auxiliar** | sí | solo ese presupuesto | agrupador |

La diferencia real entre compuesto y auxiliar es la **reutilización**: `EST-01040`
es la losa de la Zafiro y muere ahí; un compuesto sirve para cualquier presupuesto
futuro. **Es la vía para crear APU nuevos.**

Estructuralmente no es capacidad nueva —en `CATALOGO_DE_OBRA` un auxiliar ya
contiene conceptos—. Lo nuevo es volverlo **operación de autoría, con herramientas**.

> **Matriz dentro de matriz** es un concepto dentro de la matriz de otro concepto,
> con su propia clave y su propio desglose. Ver §10.1.

## 9.1 Navegación recursiva

Doble clic sobre el precio unitario abre lo que contiene. Dentro hay simples
—mano de obra, materiales, herramienta, equipo, contratos— y compuestos; doble clic
sobre el PU de un compuesto entra un nivel más, **y se repite sin límite**.

> Es la misma acción en el nivel 1 que en el 5. No hay tipos especiales por
> profundidad: hay nodos con hijos y nodos sin ellos.

## 9.2 Flotante

El compuesto **toma siempre la versión vigente de cada hijo**, no las congela.

El cambio se propaga hacia arriba por todos los caminos: mover el alambre recocido
sube por cada compuesto que lo contiene y por cada compuesto que contenga a esos.

> **La alerta debe decir qué cambió abajo**, no solo que algo cambió. Con tres
> niveles de anidamiento, «este concepto se movió» no permite encontrar la causa.

## 9.3 Prohibición de ciclo

> **Un compuesto A nunca puede vivir dentro de A**, ni directamente ni a través de
> otro compuesto.

Si se copia un compuesto B que contiene a A y se pega dentro de A, **se rechaza**.
La validación recorre **toda la cadena de ancestros**, no solo el padre directo, y
ocurre al agregar el hijo — no al calcular.

Aplica igual a matriz dentro de matriz.

## 9.4 Unidad y cantidades

Se eligen **manualmente**, como en OPUS. El compuesto declara su propia unidad y
las cantidades de los hijos son *por esa unidad*.

---

# 10. Categorías

En OPUS la categoría tiene **seis valores mutuamente excluyentes**:

```
mano de obra · materiales · herramienta · equipo · contratos · matriz
```

O es mano de obra **o** es matriz. Nunca las dos.

## 10.1 Matriz es el desglose, no el nodo

**El concepto es concepto. La matriz es su desglose.** No son la misma cosa: la
matriz es lo que el concepto tiene adentro.

Cuando la categoría de un renglón dice *matriz*, está diciendo que ese renglón
referencia **un concepto, y el concepto trae su matriz consigo**. Los otros cinco
valores referencian insumos simples, que no se abren.

| Categoría | Qué referencia el renglón |
|---|---|
| **matriz** | Un concepto, con su desglose |
| materiales, mano de obra, herramienta, equipo, auxiliares, fletes, trabajos | Un insumo (§10.2) |

Por eso el doble clic sobre el PU funciona igual en todos los niveles: **abre la
matriz**, y dentro hay simples y más conceptos con su matriz.

### Matriz dentro de matriz

Es **un concepto dentro de la matriz de otro concepto**, con su propia clave, que
trae su matriz consigo.

Lo recursivo no viene de que un nodo cambie de naturaleza, sino de que **lo que
entra ya venía con desglose**.

## 10.2 Los ocho catálogos de insumo

**Los insumos son los que alimentan las matrices.** Sus catálogos:

```
Materiales · Mano de obra · Herramienta · Equipo
Auxiliares · Fletes · Trabajos · Todos
```

`Todos` es la vista que los reúne, no una categoría propia.

Dos cosas a notar:

- **Herramienta y Equipo van separados.** En los árboles antiguos todo estaba
  metido como material (`EQU`).
- **Fletes es un catálogo propio**, y explica el `Acarreo` sin renglones que
  apareció en trabajos (`CATALOGOS.md` §6).

### `Trabajos` también se llama `Contrato`

OPUS lo nombra de las dos formas según el reporte. **Es el mismo catálogo**, y el
cargador debe aceptar ambos nombres (§2.4).

Tiene **tres clases**: `Destajo` · `Acarreo` · `Subcontrato`.

### `Flete` contra la clase `Acarreo` — resuelto (P-02/P-03)

La frontera es **el límite de la obra, no la dirección**:

| | Cruza el límite de la obra | Paga |
|---|---|---|
| **`Flete`** | Sí — de fuera hacia adentro, o de adentro hacia afuera | El transporte, como **categoría de insumo**: se compra |
| **`Acarreo`** | No — se queda dentro de la obra | Mover material ya en la obra, como **clase de `Trabajos`**: se paga por hacerlo |

Son de naturaleza distinta —insumo contra trabajo— y por eso `Acarreo` aparece sin
renglones: el transporte, cruce el límite en cualquier dirección, se registra como
`Flete`.

> **Las clases de `Trabajos` no son una lista cerrada.** Hoy son `Destajo`,
> `Acarreo` y `Subcontrato`; pueden crecer —`Contrato`, `Permuta`, `Renta`— sin que
> eso cambie esta frontera. Por eso `MODELO.md` la modela como tabla abierta, no
> como `ENUM` (`MODELO.md` §2, hallazgo 7).

## 10.3 La categoría sí se puede cambiar

> **Un insumo puede cambiar de categoría.** La arena puede pasar de `Material` a
> `Flete`: es la misma arena, cambia lo que se está costeando — el material o su
> transporte.

Lo que **no** se cruza editando es la frontera entre **insumo y concepto**: un
material no se vuelve matriz. Para que unos insumos tengan desglose se crea un
concepto nuevo, con clave nueva (§8).

> Son dos fronteras distintas. La de categoría es porosa; la de insumo a concepto
> no.

## 10.4 El compuesto acepta cualquier categoría

> **Un compuesto de material puede llevar mano de obra, flete, herramienta o lo que
> haga falta.** No es homogéneo.

El único límite: **no puede contenerse a sí mismo en ninguna de sus capas** (§9.3).

### Entonces, ¿en qué se diferencian compuesto y auxiliar?

Estructuralmente en nada: los dos se abren y los dos aceptan de todo. **La
diferencia es de reporte:**

| | Qué es | A qué categoría reporta |
|---|---|---|
| **Compuesto** | **Depende de** una categoría | **A la suya, entero** |
| **Auxiliar** | **Es** una categoría | A sí mismo |

### El caso que lo explica: fabricar tu propio tabique

Un compuesto en Materiales con arena, cemento y mano de obra de fabricación.

- En el reporte por categoría cuenta **100% como material** — que es lo correcto:
  para la obra *es* un material, solo que lo produces tú.
- Y aun así **se abre** y muestra cuánto es fabricación.
- Comparable contra precio de mercado **sin que la mano de obra se escape a otra
  categoría**.

> Por eso elegir entre uno y otro es una decisión con significado, no una
> preferencia: **compuesto cuando el costo debe verse como su categoría; auxiliar
> cuando la mezcla no debe atribuirse a ninguna.**

### Corrección: la trabe NO es un auxiliar

Las 79 claves `AUX-` del catálogo de materiales —trabes, mallas— tienen
**`Tipo = Material`** y son compuestas. Son exactamente el caso del tabique:
compuestos que reportan a material, **y está bien que así sea**, porque para la obra
una trabe *es* un material.

> **El prefijo `AUX-` engaña.** Se creó sin saber qué prefijo poner, y termina
> nombrando una categoría que el insumo no tiene.

Es el peor caso de prefijo encontrado. Los otros (`CATALOGOS.md` §3, M-09) simplemente no
correspondían a una familia; **este nombra una categoría equivocada**, y cualquiera
—persona o agente— concluirá que esas trabes son auxiliares.

### El catálogo de Auxiliares existe pero está vacío

No hay auxiliares todavía. Ni Herramienta ni Equipo se usan en este presupuesto.
Tres de los ocho catálogos están previstos y sin uso.

## 10.5 Dos lecturas del mismo árbol

> **El compuesto cambia cómo se reporta el monto, no la naturaleza de lo que
> contiene.** La explosión es la prueba de ADN de la matriz; el APU es la
> radiografía.

| Lectura | Cómo recorre | Para qué sirve |
|---|---|---|
| **Reporte de montos** | **Se detiene en el compuesto** y suma a su categoría | Cuánto de la obra es material, cuánto mano de obra |
| **Explosión de insumos** | **Llega hasta el fondo** y conserva la naturaleza de cada hoja | Qué se compra, qué se contrata, qué se programa |

### La regla del anidamiento

> **En el reporte de montos, el básico de obra más externo absorbe todo.**

Un compuesto de material que contiene otro compuesto de mano de obra reporta **el
total como material**. Si el interno reportara por su cuenta, la mano de obra de
fabricación saldría del material y el tabique dejaría de ser comparable contra
precio de mercado.

**En la explosión no hay absorción**: llega al fondo y cada hoja conserva su
naturaleza, sin importar cuántas capas la envuelvan.

### La profundidad es de la línea, no del reporte

OPUS muestra **las dos profundidades en un mismo reporte**: en el análisis de PU, los
agrupadores y los básicos conviven — unos cerrados, otros abiertos.

```
EST-01053  Losa de cimentación
  CON-00001  Concreto TD 200      34 M3     ← atómico
  ZA1-000001 Zapata ZA-1           6 PZ     ← compuesto CERRADO, lleva su importe
  AUX-01011  Contratrabe CT1     137 M      ← compuesto ABIERTO
    ACR-00002  Varilla 1/2       ...        ← el importe lo llevan los hijos
    ACE-00001  Alambre           ...
```

> **Cada línea declara su profundidad.** No hay un reporte «de montos» y otro «de
> explosión»: hay un reporte donde cada renglón está cerrado o abierto.

**La trampa, y es de doble contabilidad:** un compuesto abierto **no lleva importe** —
lo llevan sus hijos. Si lleva los dos, el total se duplica en esa rama.

| Línea | ¿Lleva importe? | ¿Lo llevan sus hijos? |
|---|---|---|
| Compuesto **cerrado** | **Sí** | No aparecen |
| Compuesto **abierto** | **No** | **Sí** |

### Comparar dos fuentes: primero el dinero, después la naturaleza

Son dos comparaciones distintas, a profundidad distinta, y **en este orden**:

| Orden | Qué compara | Profundidad | Dentro de |
|---|---|---|---|
| **1 · Financiera** | Cuánto cuesta | **Se cierra en la matriz del concepto** | **Cada fuente consigo misma**, antes de cruzarse |
| **2 · Naturaleza** | Qué hay realmente | **Hasta el insumo atómico** | Ya cruzando las dos fuentes |

**Primero cada fuente cierra su propio dinero.** La zapata entra como $1,135.48 × 6 y
no se abre para contar pesos.

**Después se explota al fondo para comparar naturalezas**, porque qué es realmente un
material sólo se ve abajo.

> **Sin ese orden aparece la desproporción de `PET-00002 Arena`:** $49,755 contra
> $332, 150×. No es un hallazgo — es comparar una fuente donde la arena está suelta
> contra otra donde vive dentro de mezclas.

Y hay un caso peor que la desproporción: `ACR-00002 Varilla` aparece **en dos
profundidades a la vez** — negativa en la matriz del concepto, positiva dentro de la
zapata. Comparando a profundidad mixta **se cuenta dos veces con signos opuestos**.

### Por qué hacen falta las dos

Si solo existiera el reporte de montos, **la mano de obra dentro del tabique
desaparecería de la planeación** aunque estuviera en el costo. Alguien tiene que
pagarla y programarla.

Y la comparación de almacén contra explosión (§13.6) **solo funciona con la lectura
profunda**: el almacén surte arena y cemento reales, no tabiques teóricos.

## 10.6 Categoría, familia y rol son cosas distintas

| Atributo | Clasifica por | Ejemplo |
|---|---|---|
| **Categoría** | de qué catálogo de insumo sale | material, flete, **concepto** |
| **Familia** | naturaleza | aceros, adhesivos |
| **Rol** | posición en el árbol | insumo, concepto, ensamble |

> **`EQU` es equipamiento, y equipamiento es material.** No es equipo mal
> clasificado. Equipo y herramienta van a llevar su propio prefijo.

---

# 11. Los flujos entre sistemas

## 11.1 Cómo es hoy

```
              OPUS 2025
                  │  exporta
                  ↓
        ┌─────────────────────┐
        │ Catálogos alterados │   modificados por el usuario para
        │ = base de los       │   que sus ERP se formaran.
        │ prototipos          │   Se mantienen; cambian solo si
        └──────────┬──────────┘   cambia el presupuesto.
                   │ alimentan
                   ↓
        ┌─────────────────────┐         ┌──────────────────┐
        │    ERPS PROPIOS     │ ←───────│   ERP EXTERNO    │
        │   (con control)     │ salidas │  (sin control)   │
        └─────────────────────┘ almacén └────────▲─────────┘
                                                  │
                   OPUS ────────────────────────→ │
                        ingenierías: cabeceras,
                        operaciones, materiales

        ┌─────────────────────┐
        │  TABLAS CORREGIDAS  │   Materiales, Trabajos,
        │  = la nueva fuente  │   Mano de Obra, Fletes
        │  NO alimentan nada  │   ← hoy desconectadas
        └─────────────────────┘
```

**Dos cosas que solo se ven en este dibujo:**

**Hay dos flujos que no se tocan.** Los catálogos alterados sostienen lo que ya
funciona; las tablas corregidas están completas y **desconectadas**.

> Por eso se pudieron corregir con libertad: **nada dependía de ellas.** Es la regla
> de la dependencia otra vez.

**Los ERP propios reciben de dos lados que no se conocen entre sí:** de los catálogos
alterados y de las salidas de almacén del ERP externo. Ahí entra sola la comparación
de almacén contra explosión (§13.6) — lo planeado por un lado, lo surtido por otro.

## 11.2 A dónde vamos

```
              OPUS 2025
                  ↓
   ┌──────────────────────────────────┐
   │        LA NUEVA FUENTE            │
   │  catálogos corregidos +           │
   │  conocimiento + lenguaje          │
   └──────────────┬───────────────────┘
                  │  sirve para CREAR y REESTRUCTURAR
        ┌─────────┴──────────┐
        ↓                    ↓
┌───────────────┐   ┌──────────────────┐
│   ERP NUEVO   │   │  ERPS PROPIOS    │
│  (por crear)  │   │ (reestructurados)│
└───┬───────▲───┘   └───┬──────────▲───┘
    │       │           │          │
    │       └───────────┼──────────┘
    │        salidas de │ almacén
    │   ingenierías     │
    └───────┬───────────┘
            ↓
   ┌──────────────────┐
   │   ERP EXTERNO    │ ──→ envía información a todos
   └──────────────────┘
```

**No hay jerarquía entre el ERP nuevo y los reestructurados.** La nueva fuente
alimenta a los dos por igual. Las ingenierías al ERP externo pueden salir de uno o
de varios.

> Lo que la nueva fuente aporta **no es un sistema: es el lenguaje común** que
> permite que el nuevo y los reestructurados hablen igual.

## 11.3 Reglas de los flujos

| Regla | Detalle |
|---|---|
| **OPUS es fuente, no destino** | Lo corregido **nunca vuelve a OPUS**. Quizás al final se explore devolver presupuestos completos |
| **El ERP externo es destino y fuente** | Recibe ingenierías, devuelve **salidas de almacén** |
| **Hoy OPUS alimenta al externo directo** | La meta es **interponer un ERP propio**: ahí es donde hoy se pierde el control |

## 11.4 El presupuesto se arma por partes

Existe una tabla llamada **ingeniería** que en realidad es una **explosión de
insumos por agrupador**, similar al exportador. **No trae encabezados de columna.**

> **Corrige un supuesto anterior:** el presupuesto no se carga completo desde un
> archivo. **Cada tabla es un fragmento** que hay que ensamblar.

Eso impone dos problemas al cargador que no estaban previstos:

| Problema | Por qué es distinto |
|---|---|
| **Sin encabezados** | Hay que reconocer qué columna es qué **por los datos**, no por el nombre |
| **Es parcial** | No es un presupuesto: es un pedazo que se ensambla con otros |

> **No es el método definitivo.** Es un camino a explorar; puede terminar siendo una
> mezcla de varios o requerir confirmaciones de por medio.

**Advertencia:** se parece al árbol de ingeniería que salió del alcance — el que
traía **las cantidades ya multiplicadas por el volumen**. Si es de la misma familia,
esa característica reaparece, y es la que cambia los números en dos órdenes de
magnitud al interpretarla mal.


## 11.5 La ingeniería es del lote, no del prototipo

Analizada `INGENIERIA_-_ALAMO_18_-_CIM.xlsx`: 118 filas, 5 bloques, **$289,432.80**.

### Qué se puede extraer

| De dónde | Qué dice |
|---|---|
| **El nombre del archivo** | `ALAMO 18` = el **lote** · `CIM` = la etapa |
| **El contenido** | El prototipo del que salió, por la descripción del concepto |
| **Los metadatos** | Modificado el **2026-04-01** por **Carlos Miguel López Torres**. *La fecha de creación que reporta es falsa: la escribe la librería al abrir el archivo* |

> **El nombre dice dónde; el contenido dice de qué modelo salió.**

### La estructura, deducida sin encabezados

```
col 0   clave del agrupador — solo en la primera fila del bloque
col 1   clave del insumo
col 2   descripción
col 3   unidad
col 4   cantidad
col 5   precio
col 6   importe
```

**La jerarquía no tiene profundidad explícita:** `NIV`, `ECO` y `EST` se distinguen
por prefijo — y el prefijo no es llave confiable (§4 del skill).

### Dos características que la definen

**Los insumos cuelgan de la etapa.** `ECO-00002` instalaciones sanitarias no tiene
concepto de por medio: los tubos cuelgan de la etapa. Caso ya documentado como
intencional (`CATALOGOS.md` §1).

**Los compuestos vienen abiertos.** El presupuesto usa `AUX-01010 Contratrabe`; la
ingeniería trae acero y alambre directo. **Es la explosión profunda, no el reporte
de montos** (§10.5).

### ⚠ La descripción puede mentir sobre el prototipo

El archivo dice *«LOSA CIMENTACIÓN ZAFIRO PLUS»*. **No lo es.** Comparando las cinco
etapas contra los siete prototipos:

| Etapa | contra Zafiro Plus | contra **Diamante c/ch** |
|---|---|---|
| Estructura | 2.08 | **1.12** |
| Sanitarias | 1.46 | **1.03** |
| Hidráulicas | 1.38 | **1.00** |
| Eléctricas | 1.70 | 1.48 |
| Gas | 2.18 | **1.00** |

**Tres etapas dan 1.00 o 1.03 contra Diamante.** Contra Zafiro Plus ninguna se
acerca.

> **Si alguien forma el presupuesto leyendo la descripción, costea el prototipo
> equivocado.** El contenido es la evidencia; la descripción es solo una etiqueta.

### La dispersión entre etapas es información, no ruido

Contra el prototipo correcto, el patrón habla:

- **1.00 exacto** en hidráulicas y gas → **no cambiaron**; confirman que el prototipo
  es el correcto
- **1.03 y 1.12** → ajustes menores y más superficie de desplante
- **1.48 en eléctricas** → **la única que se sale del patrón**

> Las etapas que dan 1.00 **confirman** el prototipo. Las que se salen **señalan
> dónde este lote se apartó del modelo** — que es exactamente lo que se quiere saber
> al revisar una ingeniería.

## 11.6 El destajo es la huella del concepto

La ingeniería **no trae conceptos, solo insumos**. Para formar un presupuesto hacen
falta conceptos.

**El destajo los recupera.** Medido sobre la matriz completa:

| | En 1 solo concepto | En 3 o más |
|---|---|---|
| **Destajos** (262) | **199 · 76%** | 31 |
| Materiales (381) | 185 · 49% | 130 |

> **El destajo identifica al concepto; el material no.** Y los más compartidos son
> los subcontratos —`SUB-00002` en 34 conceptos— que son alzado y caso aparte.

### Dos caminos al mismo número

Con el APU se sabe **qué destajo interviene y cuál es su rendimiento**:

```
cantidad del destajo  → cuánto concepto hay
rendimiento           → cuántas jornadas costó
```

**Si los dos no coinciden, algo se movió.**

> Esto no es auditoría: **es el cargador.** Reversar la explosión es cómo se
> reconstruyen los conceptos que la ingeniería no trae. Ver P-25.

## 11.7 Auditar la diferencia no es un módulo nuevo

Comparar la ingeniería del lote contra su prototipo usa **el mecanismo que ya
existe**: la descomposición en desviación de precio y de consumo, y las nueve
causas con quién paga cada una (§13.6).

**Lo único nuevo es cuándo se compara:**

| Momento | Compara |
|---|---|
| Ya definido | Presupuesto contra ejecutado — **durante la obra** |
| Esto | **Prototipo contra ingeniería del lote** — antes de construir |

Los dos escenarios caen en causas ya definidas:

| Escenario | Causa | Quién paga |
|---|---|---|
| **Cambio solicitado por el cliente** | Petición nueva (causa 5) | **El cliente** — cobrable |
| **Ajuste o cambio de APU no reconocido** | **Ninguna** | — |

> El segundo no es una causa: **es la ausencia de causa.** Es una diferencia que
> nadie declaró, y es justo lo que el sistema detecta solo al comparar.

### Plantilla e instancia, quinta vez

**El prototipo es la plantilla; la ingeniería del lote es la instancia.** Mismo
patrón que APU, ensamble, contrato y trazo.

### Sin causa declarada, o con la identidad en duda: alerta, no autocorrección

**El sistema nunca corrige solo.** Cuando detecta algo raro, lo marca — nunca
cambia el dato por su cuenta. Mismo principio que D-145: corregir sin que quede
declarado borra la evidencia de que algo cambió sin avisar.

Dos disparadores distintos, la misma respuesta:

**1 · Diferencia sin causa (P-29).** Es la «ausencia de causa» de arriba: no cae en
ninguna de las nueve causas de §13.6. Se marca como alerta. Alguien decide si es
desviación real de obra, si faltaba declarar la causa, o si es un error de captura.

**2 · Identidad dudosa por cantidades (P-30).** Comparar por contenido —qué trae la
ingeniería, sin mirar la etiqueta— ya atrapó una descripción que mentía: `ALAMO 18`
decía «Zafiro Plus», era Diamante (D-121, `PRUEBA-ZAFIRO-1.md`). Se formaliza así:

```
razón = total de la ingeniería cargada ÷ total del prototipo que dice la etiqueta
```

Verificado sobre `ALAMO 18`: las etapas que sí eran Diamante dieron razón 1.00 a
1.03; ninguna se acercó a Zafiro Plus. **Si la razón se desvía más del umbral
—20% por defecto, parámetro, no número fijo en el código—, la etiqueta queda en
duda** y se marca como alerta, igual que el caso 1.

> **Dos métodos independientes que coinciden se validan mutuamente** (`METODO.md`
> §1.4): identificar por contenido (qué trae) y por cantidad (cuánto suma) miden
> cosas distintas. Cuando los dos apuntan al mismo prototipo, la identidad queda
> confirmada sin ambigüedad — y no hace falta un tercer criterio.

**Ninguno de los dos se resuelve solo.** Quedan en `ALERTA` (`MODELO.md` §5a) hasta
que alguien las mira — nunca se pierden al cerrar la sesión que las detectó, que es
justo lo que le pasaba a toda alerta antes de esto (B-32).


## 11.8 Once archivos del mismo lote

Se analizaron las 11 ingenierías de `ALAMO 18`, de abril a septiembre de 2026.
Suman **$2,604,015.74**.

> **No es error: es fecha de corte.** Azotea se subió después. §11.10 y §11.11 ya
> trabajan con las doce; esta cifra es la línea base de cuando eran once, y se deja
> así — es la que se compara si algún día hace falta medir qué trajo la doceava.

### Se suman, no se reemplazan

**Los cuatro archivos grandes no comparten un solo nivel ni etapa:**

| Archivo | Cubre |
|---|---|
| `CIM` · 118 filas | `NIV-00001` · etapas 1 a 5 |
| `PB` · 512 filas | `NIV-00002` · etapas 6-11, 57, 61 |
| `PA_AZO_ACA...` · 956 filas | `NIV` 3,4,5,6,11,12,13,14 · 26 etapas |
| `PISOS` · 218 filas | etapas 24 y 25 — **sin declarar nivel** |

> **Contesta P-25:** las partes **se suman**. Y el sistema puede saber si está
> completo **comparando contra el presupuesto**.

### Faltan cinco niveles completos — y el sistema lo detecta solo

La suma da **92%** del presupuesto del Diamante con chimenea. El 8% que falta son
niveles enteros sin ingeniería:

`NIV-00007` cancelería · `NIV-00008` carpintería · `NIV-00009` muebles ·
`NIV-00010` herrería · `NIV-00015` consumibles

**Ninguna etapa de la ingeniería es ajena al presupuesto.** Las 41 existen.

### Cuatro estructuras distintas en once archivos

| Estructura | Archivos | Qué la distingue |
|---|---|---|
| **Completa** · 7 col | CIM, PB, PA, PISOS | Agrupador + insumos |
| **Suelta** · 7 col | AJU_PB, AJU_PISOS, CENTRO_DE_CARGA, AJU_PIEDRA | **Sin agrupador**: solo insumos |
| **Con concepto** · 7 col | CEMENTO_EXTRA | El agrupador es un **concepto** (`ALB-01212`) |
| **Ajena** · 6 col | CIM_CAMARAS | Título propio, encabezados propios, columnas corridas, **clave dentro de la descripción** |
| **Sin costear** · 5 col | AJU_GUALDRA_PB | Insumo **sin clave, sin precio** |

> **Los archivos sueltos no dicen dónde van.** `AJU_PISOS` es una línea con clave
> `PIS-80475` y nada más. **Solo el nombre del archivo dice a qué corresponde:** la
> estructura vive en el nombre, no en el contenido.

### La fila en blanco es el separador de bloque

Verificado en los cuatro archivos grandes: **después de una fila vacía siempre viene
un agrupador.** 155 casos, sin una sola excepción.

> **Es dato estructural, no adorno.** En `CEMENTO_EXTRA` dos filas en blanco separan
> el cemento de fachada de un grupo distinto —pegapiso, rodapié y marco de cantera—
> que no tiene relación con el título del archivo.

### Anotaciones a mano dentro de la descripción

En el archivo grande los niveles dicen **«PLANTA ALTA OK», «AZOTEA OK»**. Ese `OK`
no está en el catálogo: **alguien lo escribió para marcar que ya revisó ese nivel.**

**Es metadato escondido en un campo de texto**, y se pierde al cargar si nadie lo
busca.

### 26 claves fuera de catálogo

| | Claves |
|---|---|
| **Existían en los catálogos viejos y se perdieron** | 7 — `ADH-00004`, `ADH-00036`, `ADH-00043`, `MOA-05010`, `MOA-05011`, `MOE-30020`, `MOE-30030` |
| **Nuevas del todo** | 19 — pisos, pinturas, centro de carga, `BAC-01010` |

> Las siete primeras son de las diez que se detectaron como «trabajos que ya no
> existen» al migrar a OPUS 2025. **No desaparecieron: se siguen usando en obra.**

**Y dos tienen el formato roto:**

```
HD-00411     prefijo de 3 letras donde debería decir HID
MOS-2079     4 dígitos en vez de 5
```

Pasan cualquier validación laxa y fallan cualquier búsqueda exacta.

## 11.9 La reversión por destajo — probada

La ingeniería no trae conceptos. **Se reconstruyen desde el destajo.**

### El resultado, sobre la cimentación de ALAMO 18

| | Destajos |
|---|---|
| Sin filtrar por prototipo | 16 de 38 · 42% |
| **Filtrando por el prototipo correcto** | **32 de 38 · 84%** |
| Siguen ambiguos | 4 |
| Sin candidato | 2 — `MOC-12010` y `MOS-2079`, la de formato roto |

### El residuo no es una cosa: son cuatro

El 16% que no revierte se parte en casos que piden respuestas distintas. Tratarlos
igual es lo que hace que el método parezca peor de lo que es.

| Clase | Cuántos | Qué hace el sistema |
|---|---|---|
| **Resuelto** | 32 | Se aplica solo. Detectar no necesita permiso |
| **Ambiguo** — varios candidatos | 4 | **Propuesta con todos los candidatos y su evidencia.** No se elige el más probable |
| **Clave inexistente** | 1 · `MOS-2079` | **Propuesta con las dos lecturas** —errata o trabajo nuevo— **y se reporta sin tocar** |
| **Destajo de compuesto** | 1 · `MOC-12010` | **No es residuo.** La reversión debe buscar también dentro de compuestos |

### `MOC-12010` no era residuo: era profundidad

Es la mano de obra de la zapata `ZA1-000001`, y vive en la matriz del **compuesto**,
no en la del concepto. Buscando candidatos sólo entre conceptos nunca iba a tener uno.

> No le faltaba candidato: **se estaba buscando en la profundidad equivocada.** Con la
> búsqueda ampliada a compuestos, la reversión sube de 84% a 87%.

### La clave que no existe puede ser un cambio no autorizado

`MOS-2079` tiene el formato roto **y** no existe en el catálogo. Verificado: ni
`MOS-02079`, ni `MOS-20790`, ni `MOS-02790`. Normalizar el formato da **cero**
candidatos, no uno.

Y no está entre las 7 claves perdidas al migrar, así que lo más probable es que sea de
las 19 nuevas del todo. Pero hay una tercera lectura que obliga a no tocarla:

> **Puede ser un cambio que nadie autorizó** — la *ausencia de causa* de §11.7. Si el
> sistema la corrige o la da de alta solo, borra la evidencia de que alguien cambió
> algo sin declararlo.

Por eso son las dos cosas a la vez: **propuesta con las dos lecturas, y reporte que no
toca nada.**

### Nunca se corrige una clave por proximidad

El catálogo numera en secuencia densa:

```
MOS-02050  MO SALIDA SAN REGADERA
MOS-02060  MO SALIDA SAN TARJA COCINA
MOS-02062  MO SALIDA SAN TARJA ASADOR
MOS-02070  MO SALIDA SAN LAVADORA      ← a un dígito de «2079»
MOS-02090  MO SALIDA SAN LAVAVAJILLAS
```

**Un dígito de diferencia cae sobre otro trabajo que sí existe.** Corregir por
proximidad asignaría un destajo real a un trabajo real equivocado: cuadra en
apariencia y es falso, que es el peor error posible porque nadie lo revisa después.

### Las cantidades salen enteras

```
ISN-01080   6.000        ISN-01050   3.000
ISN-01130   4.000        ISN-01060   2.000
ISN-01031   5.000        ISN-01010   1.000
```

> **Enteros exactos no pasan por casualidad.** Significa que la reversión recupera
> cantidades reales, no aproximaciones.

### La que no es entera es la más informativa

`EST-01053` da **1.130** — la losa de cimentación. Y el 1.13 coincide con el **1.12**
que salió al comparar la estructura contra el prototipo (§11.5).

> **Dos caminos independientes llegan al mismo número:** uno comparando totales, otro
> reconstruyendo desde el destajo. **Se validan entre sí.**

### El encadenamiento

```
1. Comparar totales por etapa   →  detecta el PROTOTIPO
2. Filtrar por el prototipo     →  desambigua el DESTAJO
3. Aplicar el rendimiento       →  reconstruye la CANTIDAD del concepto
```

**Cada paso alimenta al siguiente.** Y con eso la ingeniería sí se puede cargar como
presupuesto: **los conceptos son recuperables aunque el archivo no los traiga.**


## 11.10 Sin cantidades negativas en la ingeniería del lote

Se buscaron cantidades negativas en las 12 ingenierías de `ALAMO 18`. **Ninguna.**

> Contrasta con la matriz de conceptos, donde sí existen —58 líneas en 23
> conceptos— para descontar material ya contado dentro de un compuesto (§8).

No prueba que el mecanismo de sustitución no exista — solo que **en estos 12
archivos no se usó**. Sigue abierta la pregunta de cómo se declararía una
sustitución si hiciera falta (P-35).

## 11.11 Comparar ALAMO 18 contra el prototipo — el método

Se comparó el consolidado de las 12 ingenierías contra la explosión **profunda**
del Diamante con chimenea completo (todos los conceptos, con su volumen real del
presupuesto, compuestos abiertos hasta el fondo).

### El primer intento estaba mal, y por qué importa saberlo

Comparar contra un solo concepto, o contra la matriz sin multiplicar por el
volumen del presupuesto, da diferencias de 500x y 700x que **no significan nada** —
es un error de alcance, no un hallazgo.

> **La comparación válida es: consolidado del lote contra explosión profunda del
> prototipo completo, con cantidades multiplicadas por el volumen real.** Verificado:
> así, el total base da $2,829,933.69 contra $2,829,925.98 declarado — la misma
> diferencia de redondeo de siempre.

### Resultado, sobre 519 insumos comparados

| | Insumos |
|---|---|
| En ambos | 361 |
| Solo en ALAMO 18 | 29 |
| Solo en el prototipo, no usados | 129 |

### Los 29 exclusivos de ALAMO 18 son las claves ya identificadas

`ADH-00004` mortero, `MOA-05010`/`05011` azotea, entre otros — **son las mismas 7
claves detectadas en §11.8 como «existían en catálogos viejos y se perdieron al
migrar»**. Aquí queda confirmado: **siguen usándose en obra real**, con importe
relevante — el mortero solo suma $184,587.

### Una desproporción que no es de obra: es de cómo se arma el archivo

`PET-00002 Arena` sale **150 veces mayor** en ALAMO que en el prototipo —$49,755
contra $332.

> No es una obra con 150 veces más arena. **Es que en el prototipo la arena vive
> embebida dentro de compuestos** (mezclas, morteros) y **en la ingeniería del lote
> aparece suelta, repetida en cada bloque.** Es un artefacto de cómo se construye el
> archivo, no un hecho de la obra.

### Un caso que rompe el patrón, y por eso destaca

Casi todo en ALAMO 18 sale **igual o mayor** que el prototipo — ampliaciones,
ajustes. `ADH-00005 Cemento` sale al **35%** de lo esperado — el único que baja
fuerte.

> Cuando casi todo crece y una cosa baja mucho, **es candidato a sustitución**: el
> cemento que falta puede estar convertido en el mortero que sobra. Es exactamente
> el tipo de pista que este método de comparación existe para encontrar.

**Confirmado por el usuario: sí hubo sustitución.** `ALAMO 18` se cargó con la
versión anterior del catálogo, donde el mortero se usaba para muros, repellos y
finas exteriores — antes de que el cemento la sustituyera.

> **El método encontró un hecho real de la obra, no un error de datos.** La
> comparación contra el prototipo detecta correctamente cuándo una obra quedó
> capturada con una versión de APU distinta a la vigente.

## 11.12 La tercera pata: salidas de almacén — primeros cruces reales

> **Actualización:** los primeros cruces reales contra almacén ya se hicieron —
> cómo se lee el archivo (§11.15), el rendimiento real contra la matriz (§11.16),
> el corte semanal (§11.17) y los controles de cambio que lo completan (§11.18).
> Sigue parcial: solo dos conceptos de un mes.

Hoy la comparación cruza dos momentos **planeados**: el prototipo vigente contra la
ingeniería del lote. Falta la que compara contra lo **ejecutado de verdad**.

> Es la comparación de almacén contra explosión que quedó anotada en §13.6 desde el
> diseño del modelo — **sin datos para probarla hasta ahora.**

**Objetivo para cuando se cargue la tabla de salidas de `ALAMO 18`:**

```
Prototipo          →  lo que el modelo dice que debería llevar
Ingeniería del lote →  lo que se planeó para esta obra en particular
Salidas de almacén  →  lo que REALMENTE se entregó
```

Con las tres, se puede distinguir:

| Si difieren... | Significa |
|---|---|
| Prototipo vs. ingeniería | Ajuste de diseño para este lote (ya se puede hacer) |
| Ingeniería vs. almacén | **Desviación de obra** — se pidió una cosa, se usó otra |
| Prototipo vs. almacén, pero ingeniería coincide con almacén | El ajuste fue correcto y se ejecutó tal cual |

> El caso del cemento y el mortero es la prueba de que el primer cruce ya funciona.
> Falta el segundo para saber si lo planeado en la ingeniería **de verdad se
> surtió así**, o si hubo otra desviación encima.

## 11.13 El catálogo completo se reconstruye con dos técnicas, no una

§11.9 probó la reversión por destajo sobre un solo nivel —cimentación, 84%—.
Escalada a **diez niveles completos** de `ALAMO 18` (los cuatro ya probados más
Acabados, Obras Exteriores, Asador, Barda Perimetral, Pintura y Pergolado
Cochera — 72 conceptos nuevos), la reversión no fue la técnica dominante:
**la mayoría de los bloques no la necesitaron.**

### Técnica A — concepto auxiliar: la cantidad ya está ahí

Es el mismo mecanismo de §5.4 («heredada de un destajo»), aplicado ahora a
construir el presupuesto completo y no solo la cantidad de un ensamble.
Cuando el bloque de ingeniería ya trae su propio encabezado —
`ACA-01090,,"Renivelación con concreto h.o...."`— y una sola línea de mano
de obra clara debajo, no hace falta revertir nada:

```
cantidad  = la cantidad de la línea MO-/MOA-/MOC-/...
PU        = importe total del bloque ÷ cantidad
importe   = suma de todas las líneas del bloque
```

De los 72 conceptos nuevos, la gran mayoría llegó así — acabados, pintura,
obra exterior, asador, barda, pergolado. La reversión (técnica B, §11.9) solo
hizo falta donde el bloque **no** trae encabezado propio: instalaciones y
cableado, agrupados bajo un rótulo de etapa o ubicación, no de concepto.

### Técnica B — la reversión gana el desempate que le faltaba

§11.9 dejó **4 ambiguos** sin regla de desempate. El recorrido a diez niveles
encontró los dos huecos que esa regla necesitaba:

> **La ambigüedad se prueba después de deduplicar candidatos, no antes.**
> `ECO-00009` (eléctricas PB) traía una clave de catálogo repetida
> —`IEC-01260` dos veces, a cantidades de referencia distintas, una por
> sub-ubicación— y el primer intento de desambiguar leyó eso como **dos
> candidatos en conflicto** cuando era **un solo concepto**. Corrección:
> `sorted(set(...))` sobre las claves candidatas, sumando la cantidad del
> destajo en todas sus ocurrencias de la etapa, antes de decidir si hay
> empate.
>
> **El ancla de mano de obra siempre gana.** Un primer intento eligió, para
> cada insumo, «el candidato que da el entero más limpio» de forma
> independiente — y produjo un vertedero de 25 unidades, absurdo. El motivo:
> los materiales compartidos (`SAN-`, `HID-`) tienen tarifas por unidad
> pequeñas en muchos conceptos a la vez, así que cualquier ruido parece
> «limpio». La mano de obra no tiene ese problema — es 1.0 por unidad por
> convención — así que **la cantidad del concepto es siempre la de su propia
> línea MO**, y el material solo estima cuando no hay línea MO que anclar.
>
> **Dos destajos de un mismo concepto en desacuerdo se resuelven por el de
> armado, o el de mayor costo.** La losa maciza de Planta Baja traía armado
> (32.80) y descimbrado (56.80) en desacuerdo — se tomó armado. Validado
> independiente: 182.40 (nervada) + 32.80 (maciza) + 24.00 (losa 4.20) =
> 239.20 exacto contra la cimbra declarada aparte (`MAD-00002`).

### Cuando ni A ni B alcanzan: el concepto "lote"

Cuatro de los 72 bloques compartían material entre varios sub-conceptos sin
una llave real de prorrateo — el cable de una misma bobina alimenta
contacto, apagador y timbre a la vez, sin metraje declarado por punto—.
Forzar un split ahí no reconstruye un dato: **inventa uno.**

> Mismo principio que `EST-01060` en cimentación: cuando no hay llave
> confiable, **el bloque completo se registra como un solo concepto "lote"**,
> cantidad 1, en vez de una división ficticia con apariencia de precisión.
> `IEC-00410`/`IEC-00420` (cableado PB/PA) y `API-01020`/`API-04020`
> (limpieza y sellado, mezclan M2 de mármol, piedra y metros de durmiente
> bajo un solo encabezado) se cerraron así.

### `OBE-01010` no era "sin referencia" — era un auxiliar sin reconocer (B-65)

`OBE-01010` (muros de cisterna, $12,726.59) también se cerró como lote, pero
por una razón que resultó incorrecta: se registró como «sin ninguna
referencia en el catálogo maestro». No es cierto. El catálogo maestro trae
`OBE-01010` en los **siete prototipos**, como Nivel 3 —concepto auxiliar,
igual que `EST-01060`—, agregando 7 hijos reales (afine, firme, muro de
tabique, repellado, aplanado, losa, tapa) bajo un rótulo engañoso:
"ENCOFRADO DE CISTERNA 3000 LTS" para lo que en realidad es el paquete
completo de muros, no solo la cimbra. El error no fue de catálogo: fue no
reconocer un Nivel 3 como concepto auxiliar y tratarlo como concepto suelto.

No es el mismo error que la matriz prestada (D-245): ahí la clave
pertenecía a *otro prototipo*; aquí la clave es la correcta, pero al *nivel
equivocado* de la jerarquía — un agregador no es una referencia de PU
directa, aunque el grep lo encuentre.

Mejor aún: la ingeniería cruda de `ALAMO 18` trae ancla de MO propia para 6
de los 7 hijos (`MOE-02010` muro, `MOE-30010` firme, `MOE-30020` repello,
`MOE-30030` finas, `MOE-30040` afine, `MOE-31110` tapa, cada una con su
propia cantidad) — mejor evidencia de la que tenían `EST-01060` o las losas
de Planta Baja cuando se explotaron por el método de §11.14. El lote
($12,726.59) sigue siendo el valor vigente; explotarlo en sus 7 hijos
reales quedó documentado como oportunidad — ejecutado después, junto con el
resto de B-69, ver abajo.

### Los otros ocho de B-69: mismo patrón, no todos se explotan igual

Confirmado el patrón en `OBE-01010`, se revisaron los ocho Nivel 3
restantes de la lista de B-69 (`IEC-00410`, `IEC-00420`, `API-01010`,
`API-01020`, `API-02010`, `API-02020`, `API-04010`, `API-04020`,
`API-05010`) contra el catálogo maestro y la ingeniería cruda. **Los siete
`API-` sí se explotaron** — la MO trae ancla propia por hijo, algunas veces
con cantidades idénticas al catálogo:

| Código (antes) | Hijos reales | Real vs. antes |
|---|---|---|
| `API-01010` Pintura PB | 2 (muro, plafond) | $36,828.57 vs $37,139.61 (-0.8%) |
| `API-01020` Limpieza/sellado PB | 5 (mármol×2, piedra, gualdra, asador) | $11,123.88 vs $9,603.71 (**+15.8%**, todo en `ACA-10040`, sin ancla propia — se queda en catálogo, no es hallazgo, es límite del dato) |
| `API-02010` Pintura PA | 3 (muro, plafond, fachada) | $14,513.88 vs $14,603.66 (-0.6%) |
| `API-02020` Limpieza/sellado PA | 2 (mármol sellado, mármol lavado) | $1,975.73 vs $1,704.36 (**`ACA-10040` faltaba por completo** en la reconstrucción anterior — no es alza real, es un hijo nunca capturado) |
| `API-04010` Pintura fachada | 1 (ya era real) | $17,288.13, sin cambio |
| `API-04020` Limpieza/sellado fachada | 6 (piedra, moldura, 2 rodapiés, gualdra, durmiente) | $16,680.48 vs $16,680.49, sin cambio real |
| `API-05010` Pintura azotea | 1 (ya era real) | $798.14, sin cambio — la reconstrucción ya había detectado que la azotea real (19.2 M2) triplica el supuesto del catálogo (6 M2, $249.42) y lo había corregido antes de esta revisión |

`IEC-00410`/`IEC-00420` (cableado) **no se explotaron.** El material sigue
genuinamente compartido (bobina sin metraje por punto), y aunque la MO trae
más estructura de la que este mismo párrafo reconocía antes (4 categorías
de accesorio, no cero), no alcanza para separar los hijos específicos del
catálogo — `apagador sencillo/doble/triple/...` son un solo bulto de 19 en
la ingeniería, cuando el catálogo distingue 6 subtipos. Validación parcial,
sí posible, por agregado: contacto (49 real = 39+4+6 del catálogo, exacto)
y timbre+zumbador+arbotante (2+2=4, exacto) reconcilian; apagador no (19
real contra 26 que implica la suma del catálogo, más un bulto "general" de
10 sin atribuir) — brecha real, sin explicar, sin forzar.

> Aplicado sobre el catálogo reconstruido de `ALAMO 18` (scratchpad, fuera
> del repo): 20 filas nuevas reemplazan 7 lotes/mezclas, el total del
> prototipo sube $1,390.71 (0.05% de $2.57M) — explotar no cambia el
> presupuesto, lo hace auditable hijo por hijo. D-303.

### El residuo se anota, no se fuerza — `TMP-XXXXX`

Cuando el material real sobra contra lo que el catálogo esperaría para ese
concepto, y no hay dónde asignarlo con evidencia, se anota como **concepto
temporal**: clave `TMP-00001`, `TMP-00002`…, descripción corta al estilo del
catálogo, costo íntegro si el concepto esperado era cero, o **prorrateado
por `(excedente) × PU`** si el concepto sí llama parte del material —
prorratear por cantidad, nunca por dinero de la fila entera, para no
duplicar lo que el concepto confirmado ya paga. Decisión del usuario: «de
momento solo crea como concepto temporal… ya en sistema se desglosa su
matriz temporal».

> **El PU del prorrateo sale de la matriz de concepto confirmada, nunca de
> la columna `Total` de la ingeniería sin cruzarla antes.** `TMP-00002`
> (Cimentación) se armó primero confiando en `Total ÷ cantidad` de la
> propia fila — y las cuatro filas resultaron tener `Total` mal capturado:
> dos con `Total = PU` (como si la cantidad fuera 1, ignorando la cantidad
> real de 3), dos con `Total` calculado sobre la cantidad *esperada* del
> catálogo en vez de la real capturada. Cruzando el mismo insumo contra
> siete referencias independientes en `ANALISIS_DE_BASICOS_CONCEPTOS.csv`
> —todas de acuerdo entre sí en su propio PU— se encontró el precio
> confiable y `TMP-00002` subió de $1,423.84 a $2,447.04. **Cuando existe
> una matriz de concepto que ya usa el mismo insumo, es la fuente de PU —
> la fila de ingeniería sola no se valida a sí misma.** B-66.

### El resultado, a diez niveles

| Nivel | Real (ingeniería) | Catálogo de referencia | Diferencia |
|---|---:|---:|---:|
| NIV-00005 Acabados | $247,970.03 | $226,708.45 | +9.4% |
| NIV-00006 Obras Exteriores | $103,069.66 | $100,735.02 | +2.3% |
| NIV-00011 Asador | $56,204.80 | $54,790.44 | +2.6% |
| NIV-00012 Barda Perimetral | $21,021.78 | $27,434.63 | **-23.4%** |
| NIV-00013 Pintura | $123,023.14 | $114,344.55 | +7.6% |
| NIV-00014 Pergolado Cochera | $59,567.51 | $72,734.53 | **-18.1%** |
| **Diez niveles (con los cuatro de §11.9)** | **$2,561,657.71** | $2,287,461.31 | **+12.0%** |

Dos validaron exacto contra el catálogo — `ECO-00028` cableado y
`ECO-00031` instalaciones OE, **0.0% de diferencia** — evidencia de que la
técnica no arrastra sesgo sistemático. Las dos peores —barda perimetral y
pergolado cochera— van **por debajo** del presupuesto, no por arriba: menos
metro lineal de barda y una pérgola de cochera de 28.00 m² real contra
34.57 m² de catálogo. Y en pisos de Planta Baja aparecen **claves de
material distintas a las presupuestadas** —`ACA-02101` Brunei Ivory donde
el catálogo tenía Brunei Beige, `ACA-80473`/`ACA-80474` Sequoia Beige y
Amaretto Tobacco donde tenía Lugano Naturale— sustituciones reales, no
error de captura, en la misma familia que la del cemento (§11.7).

**Cuatro niveles no tienen ninguna ingeniería cargada** —Cancelería,
Carpintería, Muebles/Iluminación, Herrería— $542,464.67, **19.2% del
presupuesto base en dinero.** Es un número distinto al 92%/8% de §5, que
cuenta **etapas**, no **pesos** — ahí no se toca. Contar etapas y contar
dinero miden cosas distintas y **las dos son correctas a la vez**: cancelería
y carpintería concentran presupuesto alto en pocas etapas.

> Con las cuatro técnicas fijas, la reconstrucción es reproducible: dado un
> archivo de ingeniería con encabezados de concepto, el catálogo se arma sin
> intervención humana en la mayoría de los bloques. Lote, TMP y ambiguos
> siguen pidiendo criterio — pero ahora con reglas escritas, no con juicio
> caso por caso.

## 11.14 Comparar por destajo y material — la explosión de matriz sobre el catálogo reconstruido

§11.13 reconstruye el catálogo **por concepto**. Compararlo contra el
presupuesto base y lo pagado real **por destajo** (mano de obra, que es lo que
se contrata) y **por material** (insumo, que es lo que se surte) necesita una
capa más: explotar cada concepto por su matriz, no solo sumar su importe.
Probado sobre `ALAMO 18`, catálogo Diamante con chimenea — **hallazgos
recientes, sujetos a corrección** conforme se prueben sobre más casos.

### La explosión no se detiene en el primer nivel

Un insumo dentro de la matriz de un concepto puede ser él mismo un
**compuesto** (`AUX-`, `ZA1-`… — §10.4, `CASO-TRABAJADO.md` §3) y ese
compuesto puede anidar **otro** compuesto. De 90 compuestos usados como
insumo en matrices de concepto, 89 se usan al menos una vez y **12 anidan
otro compuesto adentro** — hasta **dos niveles** encontrados. Detenerse en el
primer nivel subvalúa destajo y material por igual, y puede esconder mano de
obra: `ZA1-000001` (zapata, `Tipo=Material`) contiene `MOC-12010` (`Tipo=
Contrato`) — ya descrito en `CASO-TRABAJADO.md` §3. **La explosión recursiva
tiene que llegar al insumo atómico en las dos lecturas (de costo y de
contratación, §5.5), clasificando por el `Tipo` de cada hoja, no por el de su
contenedor.**

### La matriz prestada: una clave puede pertenecer a otro prototipo

Una clave puede existir en el archivo de matrices **perteneciendo a un
prototipo distinto** del que se está armando — incluso con la cantidad de
referencia en una unidad de convención distinta (`act`). `EST-01060` y
`ACA-01070` tienen matriz en el archivo, pero son de **Zafiro Plus**, no de
Diamante con chimenea: usarla escaló el material a **10-13 veces** el valor
esperado antes de detectarse.

> **Antes de usar la matriz de una clave, se cruza contra el conjunto de
> claves del prototipo que se está armando.** Que la clave *tenga* matriz no
> basta — tiene que ser *su* matriz. Este error ya había aparecido una vez
> (`EST-01060` confundida con `EST-01053`, antes de esta sesión) y volvió a
> aparecer en un camino de cálculo distinto: **no es un caso aislado, es una
> clase de error que se repite** cada vez que se cruza contra el archivo de
> matrices sin filtrar por prototipo primero.

### El concepto auxiliar no se explota directo — se descompone en sus hijos reales

El concepto auxiliar (Nivel 3, agregador — `GLOSARIO-DOMINIO.md`, término
«Concepto auxiliar») **no tiene matriz propia**: su valor es la suma de sus
hijos. Igual que el concepto "lote" de §11.13 no se prorratea por no haber
llave confiable de costo (D-240), el agregado tampoco se explota directo por
destajo/material — pero **no es el mismo problema**: el lote no tiene forma
de separar su costo combinado; el concepto auxiliar sí tiene, casi siempre,
hijos identificables en el catálogo base con su propia matriz.

```
1. Identificar los hijos reales del concepto auxiliar en el catálogo base
   (Nivel 4 bajo el mismo Nivel 3 — CATALOGO_DE_PRESUPUESTO, no inventado)
2. Para cada hijo, buscar su línea de mano de obra ancla en la ingeniería
   cruda — si aparece sola y reconocible, su cantidad real se reconstruye
   por reversión (§11.9): cantidad_real = cantidad_ancla_real / rendimiento
3. Explotar cada hijo con SU matriz, a su cantidad real
4. El hijo sin ancla propia en la ingeniería se queda a la cantidad del
   catálogo base — no se inventa (mismo principio que D-240)
```

Probado sobre los tres auxiliares de cimentación/losas de `ALAMO 18`:

| Auxiliar (mi catálogo) | Hijos reales (catálogo base) | Ancla | Real vs. base |
|---|---|---|---|
| `EST-01060` (losa cim. + castillos) | `EST-01053` losa | `MOC-01010` | 244 vs 216 M2 (+13.0%) |
| | `EST-10011/10021/10031/10071/10081` (K1/K2/K3/K7/K8) | sin ancla propia — validación indirecta abajo | K2 confirmado (19=19); K1/K3/K8 dividen limpio a 4.00 pero en un conteo distinto (66/5/6, no 61/7/5); K7 sin resolver |
| `EST-00090` (losas PB) | `EST-20010` losa maciza 11cm | `MOE-02213` | 32.80 vs 39 M2 (-15.9%) |
| | `EST-20020` losa maciza 12cm ("4.20") | `MOE-02217` | 24.00 vs 24 M2 (exacto) |
| | `EST-20017`+`EST-20022` losa nervada (63+84 M2) | `MOE-02211`, **compartida** | 182.40 vs 147 M2 combinados — mismo factor (+24.1%) a las dos, sin forma de separarlas |
| `EST-00100` (losa azotea) | `EST-20033` losa azotea | `MOE-02213` | 43.90 vs 33 M2 (+33.0%) |
| | `EST-01510` escalón forjado | `MOE-02311`/`02312` | 4 vs 4 PZA (exacto) |

`MOC-01010` reconstruido ($56,120) cuadra **exacto** contra la ingeniería
cruda — es la propia ancla, así que confirma el mecanismo, no lo prueba
contra un tercero. La losa nervada de PB es el caso honesto de datos
insuficientes: dos hijos, una sola ancla combinada en la ingeniería — se
aplicó el mismo factor a los dos por no haber llave para separarlos, **no
porque sea lo correcto, sino porque es lo que hay.**

### Los castillos de Planta Baja, en metros, abren una validación cruzada para los de cimentación (B-67)

Los cinco castillos de cimentación (K1/K2/K3/K7/K8, dentro de `EST-01060`)
se quedaron sin ancla de MO propia — cantidad de catálogo, sin evidencia de
que fuera correcta. Planta Baja tiene sus propios castillos — misma
nomenclatura K1-K8, pero **en metros lineales, no en piezas** (es el tramo
de muro, no el arranque de cimentación) — y sí traen ancla real en la
ingeniería cruda.

> **Primer intento, corregido.** La primera lectura solo buscó en el
> archivo `PB` y encontró que K1 (260 M) casi cuadraba con 61 PZA a 4.20 m
> (256.2 M, 1.5%). Faltaba revisar otros dos archivos que también traen
> estos códigos: `AJU_PB` sí es de Planta Baja (K1 y K8 adicionales); el
> otro reutiliza los mismos códigos K1/K2/K7 para **Planta Alta, Azotea y
> Asador** — otro nivel, no cuenta aquí, y se excluye. Filtrado
> correctamente (`PB`+`AJU_PB`, sin los de otro nivel), K1 sube a 264 M y
> la aparente confirmación se cae: fue coincidencia sobre un dato
> incompleto, no una validación real.

Con la altura estándar (**solo dos: 3.00 y 4.20 m** — dato del usuario) y
el material completo, probando **las dos alturas** contra cada castillo
(el intento anterior solo probó 4.20) salió un primer resultado: ninguno
confirmaba limpio, K2 y K3 quedaban plausibles cada uno a su propia altura.

> **Segunda corrección: 3.00/2.80 no aplican a este prototipo.** La
> estructura de cimentación distingue dos tipos de castillo por altura —
> pero eso es la regla general entre prototipos, no dentro de uno.
> `ALAMO 18` (Diamante con chimenea) **es toda de 4.20 m** — no tiene
> castillos de 3.00 en ningún punto. El ajuste de K3 a 2.80 (§ anterior)
> estaba probando una altura que este prototipo no usa. Se repite la
> prueba con solo 4.20 (nominal) y 4.00 (descontando ~20 cm de cadena de
> cerramiento, la misma resta que explica K2, y que el usuario confirmó
> también para pretiles: 1.00 nominal cuela a 0.80).

| Castillo | M real (PB+`AJU_PB`) | PZA cimentación | ÷ 4.20 | ÷ 4.00 |
|---|---|---|---|---|
| K1 | 264.00 | 61 | 62.86 | **66.00 exacto** |
| K2 | 76.00 | 19 | 18.10 | **19.00 exacto — coincide** |
| K3 | 20.00 | 7 | 4.76 | **5.00 exacto** |
| K7 | 24.40 | 5 | 5.81 | 6.10 (no exacto) |
| K8 | 24.00 | 5 | 5.71 | **6.00 exacto** |

**Cuatro de cinco dividen exacto a 4.00 — solo K7 no cierra.** Que cuatro
códigos independientes caigan en un entero exacto a la misma altura no es
casualidad: confirma el modelo (4.20 nominal, 4.00 real por la cadena de
cerramiento) para Planta Baja completa. De esos cuatro, **solo K2 coincide
con el PZA que cimentación declaró** (19=19). K1 (66≠61), K3 (5≠7) y K8
(6≠5) dividen igual de limpio, pero a un conteo **distinto** del que
cimentación asume — ya no es falta de dato ni altura equivocada, es que el
PZA de cimentación probablemente no refleja lo que Planta Baja construyó.
K7 queda como el único caso realmente sin resolver. **No se cambia ningún
valor de cimentación** — B-67 sigue abierto: la pista ahora apunta a
revisar el PZA de `EST-10011`/`EST-10031`/`EST-10081` (K1/K3/K8) contra el
conteo real, no a seguir buscando más ingeniería. D-306 (extiende D-305).

### Efecto cantidad y efecto receta — separar por qué creció el excedente

Con el concepto auxiliar bien descompuesto, se puede leer el excedente
(Ingeniería − Presupuesto base) en dos partes, calculando un tercer valor:
**Presupuesto Formado** — mi catálogo reconstruido, a su cantidad REAL,
explotado con el MISMO rendimiento (matriz) que usa el presupuesto base.

```
Efecto cantidad = Presupuesto Formado − Presupuesto base   (construir más o menos, misma receta)
Efecto receta    = Ingeniería − Presupuesto Formado          (usar distinto rendimiento, misma cantidad)
Efecto cantidad + Efecto receta = Excedente                  (identidad exacta, fila por fila)
```

El auxiliar mal explotado (matriz prestada, o excluido sin descomponer)
**invierte la lectura**: al no tener Presupuesto Formado, todo el excedente
de esa clave se ve como "mal rendimiento" cuando puede ser, en gran parte,
"se construyó más". En `ALAMO 18`, corregir las tres losas cambió el signo:

| | Efecto cantidad | Efecto receta | = Excedente |
|---|---:|---:|---:|
| Destajo, con las losas mal explotadas | -$83,254 | +$164,940 | $81,687 |
| Destajo, con las losas descompuestas | **+$71,372** | **+$10,315** | $81,687 |
| Material, con las losas mal explotadas | -$485,127 | +$601,452 | $116,325 |
| Material, con las losas descompuestas | +$15,254 | +$101,071 | $116,325 |
| Material, con los 7 `API-` también explotados (B-69) | +$59,138 | +$57,187 | $116,325 |
| Material, sin los dos subcontratos (`SUB-`) | +$181,973 | -$52,267 | $129,706 |
| Material, con Piedra Galarza corregida (era bug, no receta) | **-$66,998** | **+$196,704** | $129,706 |

**87% del excedente de destajo es construir más (244 m² reales contra 216
del catálogo), no mal rendimiento.**

### B-68 cierra: el residuo de material no era una causa, eran tres

Explotar los 7 `API-` de B-69 con el mismo método que las losas bajó el
residuo de $101,071 a $57,187 — **~$43,884 era el mismo error: concepto
auxiliar sin descomponer**, no receta distinta ni desperdicio.

Lo que quedaba no era limpio. Dos subcontratos (`SUB-00001` pergolado,
`SUB-00006` impermeabilización) se comparaban contra una matriz de
materiales que no les aplica — un subcontrato no se construye del catálogo
propio, no tiene receta que comparar contra la suya. Al excluirlos **de las
tres columnas** (el catálogo base también trae $122,835.50 en material
para ese mismo alcance, asumiendo que se construye y no se subcontrata) el
universo comparado cambia — el excedente sube a $129,706 — y el efecto
receta **cambia de signo**: la receta ahora sobra ($52,267), no falta.

Lo que sigue después de las dos correcciones **no es desperdicio: son
pares que huelen a la misma clave contada dos veces**, insumo por insumo:

| Par | Ingeniería | Formado | Lectura |
|---|---:|---:|---|
| `ADH-00004` Mortero / `ADH-00005` Cemento | +$180,526 / -$136,201 | | Misma obra gris, dos códigos |
| `PET-00033`+`PET-00032` Piedra Galarza 40×40/60×40 | -$134,114 / -$95,968 | | La receta espera mucha más piedra de la que el real usó |
| `PET-00002` Arena 7M3 / `PET-00015` Arena de Rio 14M3 | +$47,355 / -$38,459 | | Mismo patrón: dos SKU, un insumo |
| `PIS-80473`/`PIS-00003` Pisos Sequoia/Brunei | +$33,528 / +$23,342 | | Insumo real de conceptos sin matriz — ver abajo, no es sustitución |

> `PIS-80473`/`PIS-00003` no son sustitución de clave: son el material real
> de siete conceptos (`EST-00080`, `ACA-02101`, `ACA-02073`,
> `ACA-80473`/`80474`/`80475`/`80476`) que resultaron **sin matriz en
> ningún archivo de referencia** — ni en conceptos ni en compuestos. A
> diferencia de los `API-`, esto no se puede explotar: es un límite real
> del método (acabados de piso elegidos por el cliente, sin receta
> genérica que comparar), no un hueco por cerrar. Estas siete claves
> faltaban en la enumeración de B-69 — se corrige ahí.

Mortero/Cemento y las dos Piedras Galarza son, juntos, ~$366K de las
diferencias brutas — el siguiente paso es confirmar insumo por insumo si de
verdad son la misma compra con clave distinta. D-307.

### Mortero/Cemento resuelto: confirma por qué el ancla es la MO, no el material (B-77)

34 conceptos de muro y aplanado (`ALB-`, `ACA-`, `EST-020xx`, `BAP-`,
`OBE-`) tienen en su matriz `MEZ-07010` — "Mezcla Cemento-Arena 1:4", un
compuesto que explota en Cemento (7.28 sacos), Arena de Rio (0.0786) y
Pipa (0.0185) por M3. La ingeniería real de esos mismos conceptos no trae
`MEZ-07010` ni una vez: trae `MORTERO SACO DE 50 KG` — un producto
premezclado que la matriz nunca referencia.

> **No es un dato mal capturado — es la ingeniería de referencia sin
> actualizar.** La obra usó mortero premezclado y lo dejó de usar (dato
> del usuario), pero la matriz de referencia nunca se puso al día con el
> cambio — ni cuando se adoptó, ni cuando se abandonó. **Por eso el
> destajo se calcula a la inversa**: no se puede partir del material de
> la ingeniería como ancla porque queda desactualizado; se parte de la
> MO/destajo, que no cambia con el proveedor o el producto del día, y el
> material se deriva de ahí. Es el mismo principio ya establecido — «el
> ancla de mano de obra siempre gana» (§11.13) — con una causa raíz
> concreta detrás: este caso es la evidencia de por qué, no solo un
> ejemplo más.

Agrupando las tres líneas que en realidad son el mismo evento (Mortero
real vs. Cemento+Arena de Rio+Pipa que explota la matriz), el neto es
**+$6,443 — 1.8% de los $366K en diferencias brutas.** No es desperdicio:
comprar mortero en costal salió, en conjunto, casi igual que mezclar
cemento y arena en obra. El cemento que sigue apareciendo en la
ingeniería real ($60,443) es el correcto — castillos y firmes nunca pasan
por `MEZ-07010`, no tienen por qué cambiar.

> **La arena también se actualizó (dato del usuario) — el grupo completo
> es más grande de lo que este párrafo cerró.** `PET-00002` "Arena 7M3"
> aparece en castillos, muros y columnas forjadas, pero ninguna de las
> tres recetas de mezcla del catálogo la referencia — `MEZ-07010` (muro),
> `MEZ-01020` (concreto de castillo), `MEZ-03020` (`ALB-01110`/`01112`)
> piden las tres `PET-00015` "Arena de Rio 14M3", que la ingeniería real
> nunca compró ($0 en 454 filas). Mismo mecanismo que el mortero, misma
> causa raíz — la matriz no se actualizó — solo que en la arena, no en el
> cemento. Agrupando el grupo completo (Mortero + Cemento + Arena 7M3 +
> Arena de Rio + Pipa + Grava), el neto sube de $6,443 a **+$54,633**: el
> 27.8% del efecto receta total ($196,704, tras corregir Piedra Galarza)
> queda explicado por este grupo — no todo. Lo que resta ($142,071) sigue
> siendo una cola larga sin un patrón tan limpio como este. D-310 (extiende
> D-308).

Queda la Piedra Galarza 40×40/60×40 (-$134,114/-$95,968) sin revisar —
mismo patrón sospechado, sin confirmar. D-308.

### Piedra Galarza era un bug mío, no receta — y corregirlo reabre B-68

No era sustitución. `ACA-11013`/`14`/`15` (forrado de columna con piedra
galarza) tenían **unidad M2** en mi catálogo reconstruido, con cantidades
(60.48/11.76/6.3) que no correspondían a nada real. El catálogo maestro
las define en **PZA** (8/2/1) — y el material real de la ingeniería cruda
confirma, exacto, esas mismas 8/2/1 piezas:

```
ACA-11013: 168.00 PET-00032 / 21 (matriz) = 8.0000 PZA   168.00 PET-00033 / 21 = 8.0000 PZA
ACA-11014:  44.00 PET-00032 / 22 (matriz) = 2.0000 PZA    24.00 PET-00033 / 12 = 2.0000 PZA
ACA-11015:  21.00 PET-00032 / 21 (matriz) = 1.0000 PZA    21.00 PET-00033 / 21 = 1.0000 PZA
```

Corregidas unidad/cantidad/PU/importe a los del catálogo maestro — el
total de mi catálogo reconstruido baja $16,691.81. Piedra Galarza ahora
cuadra a los centavos (diff -$0.01 y -$0.04).

> **El bug estaba enmascarando el hueco real, no explicándolo.** La
> inflación de Piedra Galarza sumaba ~$249K de más al Presupuesto Formado
> — de casualidad, en la dirección que hacía ver el efecto receta más
> chico de lo que es. Corregido el bug, el efecto receta (material, sin
> subcontratos) no queda en -$52,267 como reportó D-307: **sube a
> +$196,704.** Con subcontratos incluidos, comparable con la tabla
> original de B-68, pasa de +$101,071 (el original) a **+$306,158**. El
> excedente total no cambia (siempre fue Ingeniería − Presupuesto base,
> ninguno de los dos depende de mi catálogo) — lo que cambia es cuánto de
> ese excedente queda sin explicar.

Revisado si hay más bugs del mismo tipo (unidad de mi catálogo distinta a
la del maestro, para toda clave que ambos comparten): dos más, ninguno del
calibre de Piedra Galarza. `ACA-07011` dice M2, debería decir "m" — pero
cantidad × PU ya da el importe correcto, es error de etiqueta, no de
cálculo. `EST-10020` (JGO vs PZA, $122.22) es un dato deliberado de una
sesión anterior, no un bug.

**B-68 se reabre.** Las tres causas de D-307 (concepto auxiliar sin
descomponer, subcontratos sin matriz aplicable, Mortero/Cemento por
ingeniería de referencia sin actualizar) siguen siendo ciertas — juntas
explican una parte real. Pero con Piedra Galarza corregida, lo que queda
sin explicar ($196,704) es mucho más grande de lo que D-307 reportó, y
está repartido en una cola larga de 206 pares de insumo, no en dos o tres
grandes — mortero/cemento (ya resuelto, D-308) es la única excepción
grande y limpia encontrada hasta ahora. D-309 (corrige D-307).

### Alcance: qué queda fuera, y qué no se debe leer de más

- **No reconcilia contra el total en dinero del catálogo reconstruido**
  (§11.13). Son dos lecturas de valor distintas — costo real declarado
  contra rendimiento estándar a cantidad real — y no tienen por qué sumar
  igual.
- **Una clave del catálogo base/ingeniería que nunca aparece en el
  catálogo reconstruido explotado no significa que "no se construyó"**:
  puede ser un hijo sin ancla propia dentro de un concepto auxiliar (los
  castillos de la tabla arriba), o una clave que mi catálogo agrupó bajo
  otro nombre. Se marca, no se interpreta en automático.
- **40 conceptos de mi catálogo ($394,172.93) siguen sin matriz para esta
  comparación** — TMP-/AJU-/agregados propios sin matriz válida del
  prototipo. Cuentan en el total del catálogo (§11.13) pero no en esta
  capa. `PENDIENTES-MEJORAS.md` B-69.
- **Cuando una clave de destajo/material se repite en más de un
  nivel/etapa**, lo pagado real (que no distingue ubicación) solo se cuenta
  en su primera aparición del recorrido — sumarlo en cada rama triplicó el
  total pagado en el primer intento.

## 11.15 Salidas de almacén: cómo leer el archivo

El export mensual de almacén (hoja `Consulta`, 46 columnas) no se puede cruzar a
ciegas — dos de sus columnas engañan y una tercera se repite. Hallazgos válidos
para cualquier obra, no solo `ALAMO 18`.

### El filtro de lote correcto

Hay **tres** columnas candidatas a decir «de qué lote es este movimiento», y solo
una sirve:

| Columna | Qué trae | ¿Sirve para filtrar por lote? |
|---|---|---|
| `Lote` | Numérico: 0, 1, 4, 9, 11, 16, 18, 19, 20… | **Sí — es la correcta** |
| `# Lote` | Siempre `S/L` | No. Es un campo de lote de fabricación/calidad, no de la casa |
| `Ubicacion` | Nombre de calle (`ALAMO`, `FRESNO`, `TABACHIN`…) | No confiable: una calle cruza varios números de lote — `ALAMO` sola trae Lote 19 (106 filas), Lote 18 (76), Lote 1 (58) y Lote 0 (7) mezclados |

> Filtrar por `Ubicacion="ALAMO"` en vez de `Lote=18` da un conjunto equivocado —
> mezcla cuatro lotes distintos bajo el mismo nombre de calle.

### `Ubicacion` aparece dos veces, con significados distintos

El encabezado trae `Ubicacion` en la columna 4 (nombre de calle) **y otra vez** en
la columna 17 (bodega física: `GENERAL`, `UBC-PRUEBA`, `EXTERIOR`). Armar un
diccionario `{encabezado: índice}` de la forma habitual **se queda solo con la
última ocurrencia** — la de bodega, no la de calle — sin ningún error visible: la
consulta corre, regresa datos, y están mal.

> **Con dos columnas del mismo nombre, el mapeo por nombre no basta: hay que leer
> por posición.** Ya estaba escrito para `Tipo` en `Trabajos` (`CATALOGOS.md` §3,
> §2.4 arriba) — es la misma trampa, en un archivo distinto.

### La cadena de referencia de la actividad

El movimiento clave es `Motivo = "Implosión De Materiales"`: el propio sistema
explota el concepto en sus insumos — no es una entrega genérica, es la traza que
`P-38` necesitaba. Su columna `Referencia` (texto libre) trae, cuando está
poblada:

```
OP:23186, No.Parte:EST-01060, Parte ALAMO 18 - LOSA DE CIMENTACION...
```

`OP` es el folio de la orden de producción — agrupa todas las líneas de insumo de
una misma ejecución de concepto. `No.Parte` es la clave del concepto o etapa que
se explotó — puede ser a nivel concepto (`EST-02010`) o a nivel etapa
(`ECO-00002`).

> La columna `# OP` (índice 36) trae el mismo folio que el `OP:` de `Referencia`,
> **validado exacto en 67 de 67 filas** con ambos poblados. Es un join limpio
> alternativo, y confirma que el texto libre no miente.

### Por qué esto no es un caso aislado

Ninguna de las tres trampas de arriba se ve en una revisión superficial: la
consulta corre, no tira error, y el resultado *parece* razonable hasta que se
cruza contra una segunda fuente. Mismo patrón que la matriz prestada (§11.14) y el
`Total` mal capturado de la ingeniería (§11.13, B-66): **un archivo de origen no
se valida solo por correr sin errores.**

## 11.16 Rendimiento real de material contra la matriz — primera prueba, y un bug propio

Con la lectura correcta de almacén (§11.15), se puede comparar material real
consumido contra el rendimiento estándar del catálogo, **para el mismo concepto y
la misma escala**. Probado sobre los dos únicos conceptos de abril con las dos
puntas —almacén y matriz— en `ALAMO 18`: `EST-01060` (losa de cimentación) y
`EST-02010` (muro de tabique).

### La escala se revierte, no se copia del pagado acumulado

`PRECIO_REAL_ALAMO_18.xlsx` trae la cantidad pagada **acumulada a la fecha de
corte**, de todo el proyecto — mezclar eso contra un solo mes de almacén compara
ventanas de tiempo distintas. En su lugar, la escala real de cada orden se obtiene
**revirtiendo un insumo ancla contra su propia matriz** — misma idea de §11.9
(«la mano de obra siempre ancla»), **generalizada**: cualquier insumo con una tasa
limpia y exclusiva del concepto sirve de ancla, no solo la mano de obra.
`CON-00001` (concreto, exclusivo de la losa — los castillos usan otro concreto)
para `EST-01060`; `PET-00001` (tabique, 50 PZ/M2 exacto) para `EST-02010`.

### El bug: comparar material contra material-más-mano-de-obra

Almacén **nunca** registra mano de obra — los destajos se pagan aparte. La
primera versión de esta comparación sumaba, del lado de la matriz, también las
líneas `Tipo=Contrato` (mano de obra) — una resta que nunca podía cuadrar, sin
importar qué tan bien construida esté la casa.

| Concepto | $ matriz, con mano de obra (mal) | $ matriz, solo material | Real | Diferencia correcta |
|---|---:|---:|---:|---:|
| `EST-01060` (losa + castillos) | $232,460.08 | $174,884.05 | $140,346.91 | **-19.7%** |
| `EST-02010` (muro tabique) | $46,440.48 | $28,440.48 | $27,712.92 | **-2.6%** |

> **Comparar material real contra un total que incluye mano de obra infla la
> brecha artificialmente.** El primer reporte de esta comparación decía -31.2% y
> -40.3% — el error era del cálculo, no del dato de obra.

`EST-02010`, una vez corregido, prácticamente cuadra: el tabique sale **exacto**
(6,000 de 6,000 piezas, 0.0%).

### El concepto auxiliar necesita su alcance completo, no solo el hijo con ancla

Una orden de almacén no distingue de cuál sub-concepto viene cada insumo — agrupa
todo bajo un mismo folio. Comparar `EST-01060` solo contra la matriz de su hijo
con ancla propia (`EST-01053`, la losa) deja fuera lo que la misma orden también
cubrió (los castillos K1/K2/K3/K7/K8, `EST-10011`/`10021`/`10031`/`10071`/`10081`)
— y por eso la primera versión (solo losa) mostraba -31.2% en vez de -19.7%: la
mitad de la diferencia era simplemente material que la matriz de comparación no
estaba mirando.

### Lo que queda, después del bug: en su mayoría explicable

Sobre `EST-01060`, con material puro y alcance completo, ~55% de los $34,537
restantes es **precio, no rendimiento**: el concreto sale en cantidad **idéntica**
(37.330 = 37.330 M3, 0.0% de diferencia de rendimiento) pero a un precio real
(~$1,928/M3) menor al que asume la matriz (~$2,442/M3). El resto se reparte entre
insumos que corren por encima del estándar (varios aceros y alambres) y tres
—cemento, tablas, tabique— **100% ausentes** de esta orden de abril pese a que la
matriz los espera: la hipótesis más simple es que ya se habían surtido en un mes
anterior, fuera de la ventana de este archivo — **sin datos de meses previos no
se puede confirmar.**

## 11.17 Rendimiento semanal: tabique y cemento no se leen igual

`PRECIO_REAL_ALAMO_18.xlsx`, hoja `Mano de Obra`, trae columna `Semana` — permite
comparar la salida de almacén contra lo pagado en la **misma semana**
(jueves-miércoles), más fino que el acumulado de §11.16.

### Dos insumos, dos patrones de abasto — dato de campo, no supuesto

Sobre `EST-02010` (único concepto con las dos semanas completas en abril):

| Semana | Tabique (almacén) | Cemento (almacén) | M² pagado |
|---|---:|---:|---:|
| 18 | 6,000 PZ | 30 sacos | 50 |
| 19 | 0 PZ | 30 sacos | 293 |

> **El tabique se abastece por lote — más de lo que se consume en una semana. Su
> desfase semana a semana es normal, no comparable 1:1.** El cemento se entrega
> **a diario**: es la señal confiable para verificar si lo pagado esa semana tiene
> respaldo real de material. Aportado por el usuario, con experiencia directa de
> obra — no se dedujo de los datos.

### El hallazgo: la semana 19 no tiene respaldo de cemento

Con el rendimiento teórico exacto (0.325416 sacos/M2), 30 sacos alcanzan para
~92.2 M2. La semana 18 pagó 50 M2 —hay margen, consistente con abasto por
adelantado—. **La semana 19 pagó 293 M2 con los mismos 30 sacos: 68.5% de lo
pagado esa semana no tiene material que lo respalde.**

> Consistente con una hipótesis de campo del usuario: **tiende a sobre-estimarse
> para cerrar la semana el viernes**, y hoy la verificación contra almacén ocurre
> *después* del pago —cuando ya no hay oportunidad de comparar— en vez de al
> momento de preparar la estimación.

### Idea a futuro, sin diseñar

Automatizar este mismo cruce (salida de cemento del día/semana contra el M2 que se
va a estimar) para que corra **al preparar la estimación, antes del cierre del
viernes** — hoy este cruce se hizo a mano y después del hecho.
`PENDIENTES-MEJORAS.md` B-70.

## 11.18 Los controles de cambio de ALAMO 18 — CC-ALM-18XXX

§13.4 define el control de cambio en general: referencia un nodo congelado,
propone un delta, no edita. Los archivos `AJU_*` de `ALAMO 18` —ajustes sueltos
sin nivel ni etapa declarados, `P-31`— son la primera aplicación concreta.

### La clave

```
CC-ALM-18XXX
CC   control de cambio
ALM  cluster Alamo
18   número de lote
XXX  consecutivo
```

### Clasificación, por lo que el propio archivo trae

| El archivo trae… | Tratamiento |
|---|---|
| Un destajo claro | El control de cambio es un **agrupador con un concepto hijo** — mismo patrón que concepto auxiliar |
| Dos destajos en desacuerdo | **Matriz invertida**: se reparte el material contra lo que cada concepto hijo ya reclama; el residuo que no cuadra con ninguno se anota como concepto temporal `TMP-ALM18-XX` |
| Material sin destajo propio | Se queda como **concepto auxiliar** — mismo tratamiento que si no tuviera destajo en la reconstrucción base (§11.13) |
| Sin encabezado `NIV-`/`ECO-` | Se marca **«sin identificar»**: entra al consolidado (cuenta en el total) pero se excluye del árbol por nivel/etapa — no se le inventa una ubicación |

> Responde la pregunta abierta de `P-31` («¿se parsea el nombre, se pregunta o se
> rechaza?»): **se lee primero el propio encabezado interno del archivo** —casi
> siempre trae su `NIV-`/`ECO-`—, y solo si no lo trae se marca sin identificar.

### Se verifica contra el archivo crudo, no se asume

Antes de contar una línea, se revisa si de verdad es aditiva o si ya vive dentro
de otro concepto. Ejemplo probado: cemento extra en fachada se confirmó **no
traslapado** porque el concepto base de esa fachada usa mortero, no cemento — son
insumos distintos, no el mismo material contado dos veces.

> Si el material que baja fuera el mismo que el concepto base ya reclama, **eso
> es una alerta para el usuario** —puede señalar que el concepto base quedó sin
> usar el material que se le asignó—, no un control de cambio silencioso.

### Es una capa complementaria, no se suma

Sobre `ALAMO 18`, cinco controles de cambio (`CC-ALM-18001` a `18005`,
$36,214.03) cubren exactamente el hueco que PRESUPUESTO FORMADO (§11.14) no pudo
explotar por no tener matriz propia del prototipo — no se suman a Presupuesto
Formado, se leen en su columna aparte.

## 11.19 El cruce se extiende a todo el catálogo, no solo a los dos casos investigados

Los cruces de §11.16/§11.17 probaron el método sobre `EST-01060` y
`EST-02010`. Extendido a **todo el catálogo de destajo y de material**, el
método es el mismo — solo cambia qué se agrupa:

| | Material | Destajo |
|---|---|---|
| Fuente | Almacén (`Lote`=18, `Efecto Qty` negativo = salida) | Estimación del ERP externo (`Lote`=18, `Operacion` → clave por prefijo, §13.8) |
| Se agrupa por | `# Parte` | Clave extraída de `Operacion` (el prefijo, ej. `MOC-01010`) |
| Se suma | Cantidad de salida | `O/Avance` y `$/Operación` |

**Cobertura parcial, no total** — las dos fuentes son fotos de abril, no el
catálogo completo: 58 de 288 materiales y 36 de 225 destajos tienen dato ese
mes. Una clave sin dato no significa «sin consumo»: significa «sin
movimiento ese mes».

**Ya aparecen dos lecturas** al cruzar: claves donde ambas fuentes coinciden
casi exacto (`MOC-12010`: 6 y 6 · `ACE-00010`: 4.31 y 4.31) — señal de que
las dos fuentes miran lo mismo —, y claves con brecha real (`ACE-00001`:
487.42 contra 133.7) — candidatas a revisar, mismo patrón que `EST-01060` y
`EST-02010`.

> El resultado vive en el workbook de trabajo (pestañas de consolidado por
> material y por destajo), fuera del repo por la misma razón de siempre
> (`INDICE.md`) — aquí queda el método, no la cifra.

---

# 12. Las tres capas del rediseño

**El rediseño no puede ser una edición. Tiene que ser una receta.**

Si fusionar, dividir, extraer y componer modificaran los datos cargados, al
importar el siguiente prototipo se llegaría a datos crudos otra vez y habría que
rehacer todo a mano.

```
1. CARGADO     lo que OPUS entregó. INMUTABLE
2. REDISEÑO    lista ordenada de transformaciones
3. VIGENTE     resultado de aplicar 2 sobre 1. Es lo que se edita
```

**Prototipo nuevo = capa 1 nueva + la misma capa 2 = capa 3 nueva.** El rediseño se
adopta solo.

Es la idea de las migraciones de base de datos: no se guarda el resultado, se
guardan los pasos, y se reproducen sobre cualquier punto de partida.

## 12.1 Lo cargado no se toca

Si el rediseño escribiera sobre lo que OPUS entregó, se perdería la única copia
fiel de lo que llegó, y con ella la respuesta a *¿esto lo trajo OPUS o lo hicimos
nosotros?*

Mismo principio que la clave que no se reescribe y el `id` que no cambia.

Con las tres capas siempre se puede **comparar**: cuánto cambió el rediseño
respecto de lo que venía, y si mejoró o encareció.

## 12.2 Cuando una regla no encuentra sus piezas

La regla dice fusionar salida hidráulica con sanitaria, pero la casa nueva no tiene
sanitaria.

> Se marca como **no aplicada**. No se salta en silencio ni detiene la carga.
> Quien carga la mueve para generar un rediseño.

## 12.3 La estructura permanece

Capítulos, subcapítulos, niveles y etapas **permanecen en el árbol**. El ensamble
referencia al concepto; no lo saca de su etapa.

Es la tercera vez que aparece la misma regla —el programa reagrupa, el paramétrico
reagrupa, el ensamble reagrupa— y **ninguno reasigna**.

En lo contratado el rediseño se detiene: se congela la capa 3 y todo pasa por
control de cambio.

---

# 13. Contratación, cambios y obra en marcha

## 13.1 La cadena de precios

**Cuatro precios, cada uno en su lugar. Ninguno sobrescribe al anterior.**

```
Catálogo       PU del APU                   lo que cuesta según la matriz
Presupuesto    PU de la versión vigente     lo que esta obra presupuestó
Contrato       precio pactado               lo acordado con ESE contratista
Ejecutado      lo realmente pagado          lo que salió
```

Cada salto tiene significado propio:

| Salto | Qué mide |
|---|---|
| Catálogo → Presupuesto | Versión y vigencia (§2.2) |
| Presupuesto → Contrato | **El resultado de negociar** |
| Contrato → Ejecutado | **La desviación de obra** |

> Si se sobrescriben, los dos significados se pierden. **El precio de un contrato no
> toca el catálogo:** es una negociación con un contratista concreto, no un cambio
> en lo que el trabajo cuesta. Escribirlo encima contaminaría todos los demás
> presupuestos.

## 13.2 Precio por contratista

El mismo concepto tiene **precios distintos según con quién se contrate**. Es un
tabulador por contratista, con vigencia — igual que el precio del insumo
(`MODELO.md` §4a, `TABULADOR_CONTRATISTA`).

### Cuando el pactado no coincide con el PU

**La respuesta depende de si ya se pagó.**

| Momento | Qué es | Qué se hace |
|---|---|---|
| **Antes de pagar** | Renegociación | Se **cambia** el precio pactado de $55 a $50. Sin línea aparte |
| **Después de pagar** | Descuento | El pactado **no se toca**. Se registra una deducción de $5 sobre el pago |

Antes de pagar no hay descuento: no ocurrió ningún hecho, solo se acordó otra cosa.
El precio pactado es un acuerdo vigente y puede cambiar mientras nadie haya cobrado
contra él.

Después de pagar sí lo hay, y necesita rastro: el contratista cobró a $55 y se le
deduce $5. **El pactado ya no se puede tocar porque hay una estimación emitida que
lo usó.**

> Es la misma frontera de todo el modelo: **mientras nada dependa de un dato, se
> corrige; en cuanto algo dependa, se agrega encima.** Igual que la unidad del
> concepto (§2.8) y que el catálogo congelado al contratar (§1.4).

### El PU no es piso ni techo: es la referencia

Renegociar no significa llegar al PU. El pactado puede quedar en $52 — ni lo que se
pedía ni lo presupuestado. **Son tres números independientes:**

```
PU presupuestado    $50    la referencia
Precio propuesto    $55    lo que pidió el contratista
Precio pactado      $52    lo que se acordó
```

Y de ahí salen **dos lecturas que hoy se confunden en una sola**:

| Comparación | Qué mide |
|---|---|
| Pactado contra **propuesto** | Lo que se ganó negociando |
| Pactado contra **PU** | La desviación contra el presupuesto |

Lo primero mide al comprador; lo segundo mide al presupuesto. **Guardando solo el
pactado, ninguna de las dos se puede calcular.**

> El pactado **no tiene por qué ser menor**. Puede quedar arriba del PU si el
> mercado subió, o abajo si el contratista quería el trabajo. Que quede arriba no es
> un error a corregir: es información.

Por eso se guarda el **motivo cuando el pactado supera al PU** — alza de mercado,
urgencia, o un PU que ya quedó viejo.

> **Si muchos contratos del mismo concepto quedan arriba del PU, el que está mal es
> el PU.** Ahí está la señal para revisar el APU (§13.6).

## 13.3 Registrar no es comprometer

> **La obra no para.** Si el sistema bloquea, la gente trabaja fuera de él —Excel,
> WhatsApp— y el dato se pierde por completo.

| Acción | Exige costeo |
|---|---|
| **Comprometer** — contratar, programar | **Sí** (§4.1) |
| **Registrar** — esto ya pasó | **Nunca se bloquea** |

Impedir registrar avance sobre un renglón sin presupuesto obliga a mentir o a no
capturar. Se registra y queda marcado como **ejecutado sin respaldo**.

### Es una deuda medible

*$X de obra ejecutada sin presupuesto aprobado*, **con su antigüedad**. Un renglón
que lleva seis semanas ejecutándose sin costear es un problema visible, no un dato
ausente.

Y tiene **solo dos destinos**: se vuelve orden de cambio, o es pérdida.

## 13.4 Control de cambio

Mismo patrón que todo lo demás: **no edita, agrega.**

La orden de cambio es un documento propio que **referencia el nodo congelado y
propone un delta**. El nodo contratado no se reescribe — igual que la clave no se
reescribe (§2.1) y lo cargado no se toca (§11.1).

Lleva:

- **Causa** — cambio de proyecto, error, condición de sitio
- **Impacto** en monto y en plazo
- **Quién autoriza**
- **Si la autorización fue antes o después de ejecutar**

> En obra la orden de cambio casi siempre se autoriza **después**. No se prohíbe,
> pero se registra: **el porcentaje de órdenes retroactivas es una medida directa de
> qué tan sano está el proceso**, y hoy nadie la tiene.

> **Aplicación concreta, con clave y método cerrados:** §11.18, sobre los
> ajustes sueltos (`AJU_*`) de `ALAMO 18` — `CC-ALM-18XXX`.

## 13.5 Empujar el presupuesto sin frenar la obra

**El presupuesto nunca está incompleto: está provisional en algunas partes.**

Con el paramétrico hay número desde el primer día (§5.10). Un renglón estimado no
es un renglón faltante: es un renglón con **precisión baja y declarada**.

Eso cambia la carrera. En vez de correr para *terminar* el presupuesto, se corre
para **mejorar lo más caro y lo más incierto** — y eso el sistema lo ordena solo:

```
prioridad = dispersión × monto
```

Un renglón está **listo** cuando su cantidad es `medida`, está costeado y aprobado.
Lo demás es cola de trabajo, no bloqueo.


## 13.6 Desviaciones en todas las categorías

Lo que pasa con el destajo pasa con todo. Pero **toda desviación se descompone en
dos factores**, y conviene no mezclarlos:

```
desviación = (precio real − precio plan) × cantidad real      ← DE PRECIO
           + (cantidad real − cantidad plan) × precio plan    ← DE CONSUMO
```

> **Separarlos importa porque responden distintas personas.** «Pagamos más» es de
> compras; «usamos más» es de obra. Una cifra global no le sirve a ninguno.

### Causas por categoría

Vocabulario controlado, no texto libre — si no, las desviaciones no se pueden
agregar ni comparar:

| Categoría | De precio | De consumo |
|---|---|---|
| **Materiales** | Mercado · volumen · proveedor distinto · cambio de presentación | Desperdicio mayor al teórico · merma por daño, clima o robo · sustitución por equivalente (§ grupo funcional) |
| **Mano de obra / destajo** | Renegociación · urgencia · alza de tabulador | **Rendimiento real distinto al teórico** (§6.2) · retrabajo · trabajo fuera de alcance |
| **Herramienta y equipo** | Tarifa distinta | Días reales de renta · **equipo parado**: costo sin producción |
| **Maquinaria** | Tarifa · combustible | Horas efectivas contra horas facturadas |
| **Contratos** | §13.2 | Volumen realmente ejecutado |
| **Auxiliares y compuestos** | Heredan las de sus componentes | Heredan las de sus componentes |

### Tres cosas distintas que se confunden

| Es | Qué pasó | A dónde va | ¿Recuperable? |
|---|---|---|---|
| **Desviación** | La misma obra, a otro precio o consumo | Análisis | No |
| **Cambio de alcance** | **Obra distinta** | Orden de cambio (§13.4) | **Sí, se cobra** |
| **Faltante o sobrante** | Una línea que no existía en el APU | Corrige el APU, o pérdida | A veces |

> **Clasificar mal cuesta dinero.** Un cambio del cliente registrado como
> desperdicio es un monto que se pudo cobrar y no se cobró. La desviación se
> absorbe; el cambio de alcance se factura.

Por eso la primera pregunta al capturar no es la causa, sino: **¿es la misma obra?**

### Las nueve causas, y quién paga cada una

La palabra «omisión» tapa situaciones que se pagan al revés. **Lo que las separa es
contra qué se comparan, y la única referencia que importa es el contrato del
cliente.**

| # | Causa | ¿Obra distinta? | Quién paga | A dónde va |
|---|---|---|---|---|
| 1 | **Error de ejecución** | No | Tú o el contratista | Desviación |
| 2 | **Necesario para ejecutar** | No — es medio, no fin | Tú | Desviación, o falta en el APU |
| 3 | **Omisión de presupuesto** — el proyecto lo tenía, el presupuesto lo olvidó | No | **Tú** | Ejecutado sin respaldo → corrige el APU |
| 4 | **Omisión de proyecto, dentro del contrato** — el cliente ya lo compró, el plano no lo dibujó | No | **Tú** | **No es cobrable.** Error de proyecto |
| 5 | **Petición nueva del cliente** — fuera de lo contratado | **Sí** | **El cliente** | Orden de cambio, precio nuevo |
| 6 | **Contrato cambiado sin propagar** — autorizado, pero nadie bajó el impacto | **Sí** | **El cliente** | Orden de cambio · ver abajo |
| 7 | **Falta de insumos** | No | No aplica — es causa de tiempo, no de costo | Programa: tramo de una actividad existente (P-5 abajo) |
| 8 | **Temporalidad o clima** | Depende — si solo detiene, no; si daña, la reparación sí | Si solo detiene, nadie; si daña, **Tú** (salvo que el contrato diga otra cosa) | Si solo detiene: calendario, sin pasar de ahí. Si daña y crece obra: incidencia + merma por daño/clima (fila Materiales, arriba) |
| 9 | **Mejora de proyecto** — nadie la pidió, ni el proyecto ni el cliente | **Sí** | **Sin definir** — no es error que se absorba (3/4) ni petición del cliente que se cobre sola (5) | Incidencia, propuesta — no se ejecuta sola |

> **Las causas 7 a 9 se agregaron leyendo el programa, no el costo** — mismo
> vocabulario, pero no siempre caen limpio en las columnas de arriba: una falta de
> insumos casi nunca es una desviación de precio o consumo, es un hueco en el
> programa. Cuando el motivo además cambia el alcance —el viento que tira un muro,
> una mejora que nadie pidió— el hecho se registra como **incidencia**
> (`PROPUESTA-CUATRO-MODULOS.md` §4), un registro aparte que puede o no generar
> también una desviación o un control de cambio: no son el mismo renglón.

### Las dos omisiones son opuestas

Se parecen y se pagan al revés:

- **Si el proyecto no lo contemplaba y el cliente tampoco lo compró** → trabajo
  nuevo, **cobrable** (5).
- **Si el contrato lo contemplaba** → el trabajo siempre estuvo vendido. Es error de
  documentación y **lo absorbes** (3 y 4).

> Confundirlas es cobrar de más, o comerse lo que era cobrable.

**Las causas 3 y 4 son la misma clase de error en documentos distintos**: algo que
siempre estuvo vendido y no se documentó. Conviene leerlas juntas: su monto
acumulado es **el costo de la mala documentación**, un indicador que hoy nadie tiene.

### La causa 6 no es un evento: es una falla de propagación

Un cambio **ya autorizado** cuya consecuencia nunca llegó a planos ni a presupuesto.
Es cobrable —el cliente lo aceptó— pero se descubre en obra, cuando ya se ejecutó y
nadie recuerda qué se acordó.

> Remedio: **la orden de cambio (§13.4) registra a qué nodos afecta.** Una orden
> autorizada cuyo impacto no se bajó queda como **pendiente de propagar**, visible y
> con antigüedad — igual que el ejecutado sin respaldo (§13.3).

Así la propagación deja de depender de que alguien se acuerde.

### «Necesario para ejecutar» merece atención aparte

Andamios, obra falsa, bombeo, protecciones. **No es cambio de alcance** —el
resultado es el mismo— pero **su recurrencia sí dice que el APU está incompleto**:
si siempre hace falta el mismo apuntalamiento, debería estar dentro.

### La comprobación más fuerte: almacén contra explosión

**No depende de que nadie declare nada.** El almacén registra salidas para operar,
no para reportar desviaciones. Comparar eso contra la explosión de insumos detecta
el consumo real sin preguntarle a nadie.

**Y se lee matricialmente** — insumos por concepto, con lo teórico, lo surtido y la
diferencia:

| El patrón | Lo que significa |
|---|---|
| Un **insumo** se desvía en todos los conceptos | Problema de compra o de medida |
| Un **concepto** se desvía en todos sus insumos | Problema de ese trabajo |

Misma lectura por filas y columnas que se usa para contratistas y obras.

> **Cuidado: salida de almacén no es consumo.** Lo que salió pudo quedar en obra sin
> instalar, o regresar. Sin separar **surtido** de **consumido**, todo se ve como
> sobreconsumo al principio y como ahorro al final. La diferencia se lee acumulada,
> no por corte.

### La recurrencia no prueba que el catálogo esté mal

Que algo se repita solo prueba que se repite. Hay al menos tres razones:

| Razón | ¿Corrige el catálogo? |
|---|---|
| **El catálogo está mal** — la cantidad teórica no corresponde a la práctica | **Sí** |
| **La ejecución está mal** — mezclas mal dosificadas, cortes mal trazados, mala mano | **No.** Corregir aquí **institucionaliza el error** |
| **Condición ajena** — lluvia, viento, calidad del material recibido, acceso al lote | **No** |

> Corregir el APU por un mal proceso significa **presupuestar el desperdicio de ese
> proceso como si fuera normal**. El error se vuelve estándar.

**Y hay causas permanentes y transitorias.** Una lluvia atípica no toca el catálogo
aunque se repita tres meses. El acceso difícil de un lote es de ese lote, no del
concepto.

> Corrige el catálogo solo la desviación **recurrente, atribuible al método, y no
> explicada por condición local ni por error corregible.**

### Cómo distinguirlas sin depender de un diagnóstico

Los patrones lo dicen, y el sistema ya los tiene:

| El patrón | Lo que significa | La acción |
|---|---|---|
| Se repite en **todos** los contratistas | Es del método | Revisar el APU |
| Se repite en **uno solo** | Es de ese contratista | Actuar sobre él, no sobre el APU |
| Se repite en **todas** las obras | Es del catálogo | Revisar el APU |
| Se repite en **una sola** | Es de esa obra | Condición local |

La comparación entre contratistas sale gratis del precio por contratista (§13.2).

### El problema de quién captura la causa

**La causa la registra quien ejecutó, que es el mismo con interés en que la culpa no
sea suya.** *«Mezcla mal ejecutada»* y *«material de mala calidad»* describen el
mismo desperdicio y reparten la responsabilidad al revés. Y si capturar la causa
tiene consecuencia, sencillamente no se captura.

Cuatro decisiones de diseño frente a eso:

1. **La detección no depende de nadie.** El sistema sabe cuánto decía el APU y cuánto
   se consumió. **La desviación existe se declare o no.** Lo único que se pierde al
   omitir es la explicación, no el hecho.
2. **Quien decide corregir el catálogo mira los patrones, no las causas
   capturadas.** Los patrones no se pueden maquillar.
3. **«Sin causa» es un estado válido, y su porcentaje es una métrica.** Si el 60% de
   las desviaciones no tiene causa, eso ya dice algo del proceso.
4. **La causa se puede agregar después, sin penalización.** Que omitir no sea
   permanente.

> Y el vocabulario de causas **no debe ser solo auto-incriminatorio**. Si las
> opciones son «error de ejecución» y «mala mezcla», nadie elige ninguna. Hacen
> falta opciones neutrales y un **«no determinada»** honesto.

### Cuando sí corrige el catálogo

Se resuelve con lo que ya existe: **versión nueva del concepto** (§2.2), propuesta
por el sistema con la evidencia acumulada, aprobada por alguien.

Es el mismo ciclo del agente que aprende de lo decidido (`APRENDIZAJE.md`): **la
obra informa al catálogo — y alguien decide si lo corrige.**

## 13.7 Avance físico y avance pagado no se sobrescriben

**Dos registros, cada uno en su lugar. Ninguno corrige al otro.**

```
Avance físico     lo que Control ve en obra          inspección directa
Avance pagado     lo que la estimación reconoce      proceso financiero, semanal
```

Igual que la cadena de precios (§13.1): **pueden ser el mismo número, registrado en
momentos distintos, y con eso basta.** No hace falta que uno actualice al otro.

> El pagado no pesa más por mover dinero. Si la estimación se ajusta, el avance
> físico ya registrado **no se pierde**: sigue siendo el dato de qué había en obra,
> en esa fecha.

Cuando difieren, **la diferencia es la señal, no un error que se resuelve eligiendo
uno** — mismo mecanismo que «dos métodos independientes que coinciden validan»
(`METODO.md` §1.4, D-209), leído al revés: aquí divergen, y divergir también informa.
Resuelve con evidencia el rol **Control** (D-204 a D-206) — nunca ajustando uno al
otro en automático.

### Por qué esto le falta al rendimiento de material

El rendimiento real de material (§11.16 · §11.17) divide insumo consumido entre
avance. **Sin avance físico independiente, el único avance disponible es el
pagado** — y pagado no es lo mismo que construido.

Caso real: `EST-02010`, semana 19 — 293 m² pagados, con respaldo de cemento para
solo ~92 m² (§11.17, D-255). Sin un registro de avance físico esa semana, no se
puede distinguir «se pagó de más» de «el cemento llegó antes de instalarse»: son
dos historias distintas y solo el avance físico las separa. Pendiente de método de
captura — `PENDIENTES-MEJORAS.md` B-55.

## 13.8 Estimación — cuando el avance se vuelve pago

**Documento que cobra el avance ejecutado en un periodo**, semanal
(`GLOSARIO-DOMINIO.md`: Corte, Generador y Valuación son el mismo concepto en
otro dialecto).

### Dos fuentes, no una

| Fuente | Cuándo |
|---|---|
| ERP externo | Cuando hay ingeniería cargada ahí |
| Manual / Excel | Sin ingeniería, actividades fuera de catálogo, o una incidencia (`PROPUESTA-CUATRO-MODULOS.md` §4) |

Las dos se consolidan en un extractor y se acomodan a mano en un formato o
machote — hoy manual, con el mismo destino que el resto del sistema: que el
reporte consolidado salga ya armado, y quien revisa **solo valide**.

### El tope es el mismo techo, de cualquier fuente

**Topes** se alimenta de varios lados —ingeniería, cuantificador, paramétrico—,
pero solo importa uno: **cuál se volvió el contratado**. Mismo patrón de
siempre: el contratado se congela (M-1, `PROPUESTA-CUATRO-MODULOS.md` §3;
D-227). Es el mismo techo del cuantificador de presupuesto (D-273) leído al
momento de estimar, no al programar.

**Ampliar el tope no es mecanismo nuevo** — reusa lo que ya existe: una
incidencia (P-8, `PROPUESTA-CUATRO-MODULOS.md` §4) si la causa aplica, o el
umbral del cuantificador de programación (P-9) si el origen es ahí.

### Topes pagados

```
Topes pagados = Remanente + (Programado − Pagado)
              = (Tope − Programado) + (Programado − Pagado)
              = Tope − Pagado
```

Se simplifica al mismo mecanismo que Remanente (D-273 · D-282), pero contra lo
pagado en vez de lo programado.

### Validación y conciliación

Un rol **distinto** valida la estimación — no es Control de obra con otro
sombrero. **Hoy lo realiza Compras**, y puede recaer en cualquier usuario
existente; no está formalizado como los seis roles de `MODELO.md` §5b. Si algo
excede su tope, **se regresa**.

En la conciliación: el Residente ve la brecha (sube lo que quedó bajo,
reduce lo que un contratista no cumplió), **Costos recuantifica**, y
**Control valida después y descuenta si hace falta**. Lo olvidado se agrega al
final, revisado contra su propio tope.

### Deducciones, retenciones y préstamos

| Mecanismo | Cómo funciona |
|---|---|
| **Deducción por sobrepago** | Ya definida (§13.2) — se descuenta sin tocar el pactado |
| **Deducción por rehacer trabajo** | Si el contratista responsable sigue activo, se descuenta de su estimación; si ya no está, la empresa absorbe — mismo «quién paga» de la causa 1 (§13.6), ahora concreto |
| **Retención** | Solo para subcontratos |
| **Préstamo** | Se salda con avance de obra, o directo contra una estimación futura |

### Un archivo real valida el diseño sin haberlo visto

Export de abril del ERP externo, 416 filas, a nivel de operación: `O/Requerida`
(el tope) · `O/Avance` (el pagado) · `C/Promedio` (precio unitario) ·
`$/Operación = O/Avance × C/Promedio`. **Cero de 416 filas exceden el tope** —
el límite se respeta en la práctica, no solo en el diseño.

### El léxico de este archivo trae una trampa

`UDM OP` y `UDM Operación` no son la misma unidad en 59% de las filas —
`UDM OP` cuenta la orden en piezas (1 orden = 1 pieza), `UDM Operación` trae la
unidad real del concepto (m², m...). No es error: son dos objetos distintos en
la misma fila.

**`Nivel OP` mezcla nivel y etapa sin avisar** — mismo tipo de hallazgo que
`Lote` contra `Ubicacion` en el archivo de almacén (D-249). Antes de que el
edificio tenga niveles que lo justifiquen (cimentación), el campo etiqueta por
etapa; en cuanto hay plantas, etiqueta por nivel. `# Parte/SKU` es el concepto
real (`EST-`, `ECO-`...); `Operacion` es el destajo (`Moc-`, `Moe-`, `Mog-`...)
— de los cinco campos de identidad de este archivo, `Nivel OP` es el único
ambiguo. **No cruzar por `Nivel OP` sin filtrar primero por etapa conocida.**

---

# 14. La propuesta

**«El sistema propone, el humano aprueba» aparece nueve veces en este documento** —
diccionario, versión de concepto, clave nueva por unidad cambiada, reparto en
divisiones, precio de fusión, conversión de unidad, matrices generadas,
equivalencias, orden de cambio.

> Si cada mecanismo lo implementa por su lado, quien decide termina con **nueve
> bandejas distintas** y ninguna forma de ver qué tiene pendiente. Y el agente
> interno no tendría dónde dejar lo que propone.

**Falta una entidad: la propuesta.**

## 14.1 Qué guarda

| Campo | Contenido |
|---|---|
| `tipo` | Qué clase de propuesta: equivalencia, versión, reparto, conversión, matriz, fusión… |
| `objeto` | Sobre qué recae — la clave, el nodo, la línea |
| `propone` | El valor sugerido |
| `evidencia` | **Por qué.** De qué APU salió, qué patrón lo respalda, qué factor se usó |
| `origen` | Quién la hizo: persona o **agente** |
| `estado` | `pendiente` · `aprobada` · `rechazada` |
| `resuelve` | Quién decidió y cuándo |

## 14.2 La evidencia no es opcional

> Una propuesta sin evidencia es una orden disfrazada.

Quien decide necesita ver **de dónde salió**: que el rendimiento se completó con el
factor 1.085 de su cuadrilla, que la matriz se copió del APU `ACA-01010`, que la
equivalencia se detectó porque dos descripciones son idénticas.

**Es lo que permite rechazar con criterio en vez de por desconfianza.**

## 14.3 El rechazo se conserva

Ya está decidido para el diccionario y aplica igual aquí: **una propuesta rechazada
no se borra.**

> Es lo que evita que el agente vuelva a proponer lo mismo el mes siguiente. Sin
> eso, un agente que aprende de lo aprobado **reproduce indefinidamente lo que ya se
> rechazó**.

## 14.4 Lo que el agente puede hacer solo

No todo necesita aprobación. La línea ya está trazada en `IDEAS.md` §5:

| Puede solo | Debe proponer |
|---|---|
| Conversión **dentro de la misma dimensión física** —masa a masa, volumen a volumen— | Conversión que cruza dimensiones o mete una propiedad variable |
| Cálculos derivados: importes, porcentajes, rutas | Cualquier cosa que cambie un dato de entrada |
| Detectar y reportar | Corregir |

> **La detección nunca necesita permiso; la corrección siempre.**

## 14.5 Por qué esto es la base del agente interno

El asistente de obra (fase 2, Agent SDK) **necesita este mecanismo para existir**.
Sin él, solo puede consultar; con él, puede sugerir sin poder romper nada.

Y hace verificable su aprendizaje: **el corpus del agente son las propuestas
aprobadas**, con su evidencia y su historia de rechazos.

---

# 15. La ruta crítica no está en el modelo

El Gantt quedó definido como **duración calculada**:

```
duración = volumen ÷ (rendimiento × cuadrillas)
```

Eso da **cuánto tarda cada actividad**. Pero no hay nada que diga **qué va antes que
qué**.

> Sin precedencias no hay ruta crítica. Y sin ruta crítica, la suma de duraciones no
> es un programa: **es una lista.**

Lo que falta:

| Falta | Por qué importa |
|---|---|
| **Precedencias** entre actividades | Qué debe terminar para que otra empiece |
| **Tipo de vínculo** | Fin-inicio, inicio-inicio, con o sin traslape |
| **Holguras** | Cuánto puede retrasarse algo sin mover la fecha final |
| **La ruta crítica** | Qué retraso importa y cuál no |

Y hay una conexión que ya está a medias: **el tiempo de entrega del material** daría
la fecha de pedido a partir del inicio de la actividad — pero ese inicio solo se
conoce si hay precedencias.

### El tiempo de entrega: dónde vive

**Verificado: ningún catálogo lo trae**, ni tampoco hay catálogo de proveedores. No
estaba mal ubicado — no existía el dato.

```
familia      valor por defecto      18 valores cubren los 387 materiales
insumo       excepción              sólo lo que de verdad tarda distinto
```

**El default por familia hace el trabajo y la excepción afina.** Es la misma forma que
el calendario del programa: uno general, excepciones donde hacen falta.

> Por familia solo sería demasiado grueso —`Eléctrico` son 61 materiales, de cable a
> tableros—, y por material solo serían 387 valores que alguien mantiene.

**No se puede por proveedor**, que sería lo más exacto: no hay catálogo de proveedores.

### Cada valor declara su base: naturales o hábiles

Quince días no es una cifra sola. **El valor lleva su base**, porque restarlos contra
el calendario da fechas distintas:

| Base | Cuándo aplica |
|---|---|
| **Naturales** | El proveedor no sabe del calendario de la obra |
| **Hábiles** | Se descuenta contra el calendario, como el resto del programa |

Sin esa marca, `fecha de pedido = inicio − tiempo de entrega − holgura` da dos
resultados distintos y nadie sabe cuál es el bueno.

> **Y queda un límite conocido:** si el valor es en hábiles, se descuenta contra el
> calendario de la obra — que no es el del proveedor. Los días no laborables del
> proveedor no están modelados y **no se van a inventar**.

> Al inicio del proyecto se aclaró que **CPU es APU, no CPM**. Eso resolvió una
> ambigüedad de nombre, pero **el CPM como capacidad quedó fuera y nunca se
> retomó.**

Va con la definición del módulo de programa — **P-20**.


---

---

# 16. Normalización, homologación y grupos funcionales

Tres tablas, tres reglas distintas. **Hoy las tres correcciones caen entre las capas:**
no son CARGADO porque ya se cambiaron, y no son REDISEÑO porque no son ninguna de las
seis operaciones. Aquí es donde viven.

| Tabla | Qué relaciona | ¿Juicio? | Ejemplo |
|---|---|---|---|
| **Normalización** | La misma cosa escrita de dos formas | **No**, es mecánico | `pza` → `PZ` · `Petreos` → `Pétreos` |
| **Homologación** | Dos claves que son **el mismo insumo** | **Sí** | `AUX-00001` ≡ `PRE-00120` · `ISN-02001` ≡ `ISN-02005` |
| **Grupo funcional** | Insumos **distintos** e intercambiables | **Sí** | Dos adhesivos que cumplen la misma función |

> **La diferencia entre homologar y agrupar es si son la misma cosa.** Homologadas,
> una sustituye a la otra sin preguntar. Agrupadas, sustituir una por otra **es una
> decisión de obra**, y cambia el costo.

## 16.1 Cada una lleva su lista y su origen

Las tres guardan de dónde salió cada línea: **quién la creó, cuándo, y con qué
evidencia.** Sin eso, dentro de un año nadie sabe si `ISN-02001 ≡ ISN-02005` lo
decidió una persona o lo dedujo el sistema.

## 16.2 El cambio de prefijo entra por homologación

Un material hidráulico con prefijo sanitario es un nombre que engaña. **La clave no se
reescribe** (§2.1): se clona y sustituye (§8.4), y nace la clave nueva con el prefijo
correcto.

Lo que agrega la homologación es el **viaje de vuelta**:

```
entra   un archivo con la clave vieja   →  el sistema la reconoce y la actualiza
sale    hacia otro sistema              →  vuelve la clave vieja
```

> **Porque los demás sistemas no cambiaron.** Si sale con la clave nueva, el otro
> sistema no la reconoce y el ida y vuelta se rompe.

La clave vieja deja de salir **cuando el usuario lo autoriza** — individual o total,
según haya actualizado o no cada sistema externo.

## 16.3 La homologación es bidireccional; la normalización no

| | Al entrar | Al salir |
|---|---|---|
| **Normalización** | `pza` → `PZ` | Sale `PZ`. **La forma sucia no vuelve** |
| **Homologación** | clave vieja → clave vigente | **Vuelve la clave vieja**, salvo autorización |

La normalización no necesita volver porque **la forma no es dato**: `pza` y `PZ` son
la misma unidad y cualquier sistema entiende la canónica. La clave sí es dato: es la
identidad, y el sistema externo la usa para reconocer el renglón.

## 16.4 Lo que no se resuelve aquí

**El prefijo mal capturado antes de cargar** —un dedazo, no una reclasificación— no es
homologación: es un error de captura. **Se propone y el usuario decide**, porque no
hay forma de distinguirlo solo de un prefijo legítimamente distinto.

Y nunca por proximidad: §11.9 ya probó que un dígito de diferencia cae sobre otra
clave que existe y es distinta.

---

# 17. Cuantificación gráfica — de inventario a regla verificada

> `IDEAS.md` §2 enlistó 29 funciones por tipo de herramienta, sin schema y sin
> distinguir qué es infraestructura y qué es dominio. Esta sección cierra esa
> distinción para los siete casos que sí son dominio — los otros 22 no entran
> aquí, y esa ausencia es la decisión, no un olvido.

## 17.1 Veintidós de las 29 son infraestructura, no conocimiento

Calibrar escala, reparar geometría rota (`ST_MakeValid`), medir un área,
cruzar dos capas (`ST_Intersection`), agrupar polígonos (`ST_Union`) — ninguna
lleva una regla de construcción detrás. Son PostGIS, igual que el CPM es
forward pass y backward pass: **el recorrido es infraestructura, la regla de
qué suma a qué es dominio** (D-182 — el mismo límite que ya separó `ltree`
del modelo y `formula_personalizada` del SQL).

No se documentan aquí — el inventario ya vive en `IDEAS.md` §2, con su nombre
real de función PostGIS, y ahí se queda. Repetirlo en dos archivos sería el
mismo riesgo que ya se evitó con los catálogos crudos de OPUS: un hecho, un
archivo.

## 17.2 Cinco de las siete de dominio no piden campo nuevo

`ENLACE_CUANTIFICACION.medida × factor = cantidad` (`MODELO.md` §1b) ya
alcanza:

| Función (`IDEAS.md` §2) | Medida | Factor | Cantidad |
|---|---|---|---|
| Volumen | área (losa, muro) | espesor | `M3` |
| Peso desde longitud | longitud (acero) | peso lineal por diámetro, de tabla | `KG` |
| Desarrollo de superficie inclinada | área (proyección plana) | corrección por pendiente (secante del ángulo) | `M2` real |
| Conteo por patrón o símbolo | conteo | 1 | `PZ` — la diferencia es **cómo** se detecta (selección por patrón), no qué se mide |
| Cómputo paramétrico por fórmula | — | — | Ya resuelto: reusa el paramétrico existente (§5), no es mecanismo del cuantificador |

**Ninguna es dato nuevo — las primeras cuatro son el mismo mecanismo con otro
factor.** Se documentan como ejemplo trabajado, no como campo: si en la
práctica alguna necesita algo que `factor` no alcanza a expresar, eso sí sería
un hallazgo. No lo hay todavía.

## 17.3 Cubicación con taludes — no es medida×factor, es `formula_personalizada`

El volumen de una excavación con taludes no sale de una sola medida: la
sección transversal es un trapecio que cambia con la profundidad, y el
volumen del tramo depende de **dos secciones, no una**.

```
A1, A2     áreas de las secciones transversales en cada extremo del tramo
            (trapecio: base_menor + 2 × talud × profundidad = base_mayor)
L          longitud del tramo

V = L × (A1 + A2) / 2        método del área media — el estándar de obra
```

Encaja en `COMPOSICION.formula_personalizada` (`MODELO.md` §1a, hallazgo 13):
`A1` y `A2` son dos `ENLACE_CUANTIFICACION.medida` (área) sobre dos trazos —
dos secciones—, `L` es un tercer trazo (longitud) o un valor en
`NODO.variables`, y la fórmula los combina. **No es un mecanismo nuevo del
cuantificador** — es el mismo escape hatch que ya resolvía "número de manos
de pintura", con tres entradas en vez de una.

> **Sin verificar contra dato real todavía.** A diferencia del resto de este
> archivo, no hay un caso de obra con taludes en lo cargado hasta hoy. Es la
> fórmula estándar de ingeniería civil, no una regla comprobada
> aritméticamente contra un caso real. Se anota así, no como excepción
> silenciosa.

## 17.4 Ejes y niveles — sigue sin poder usarse

Referenciar una medida a la rejilla estructural depende de `FRENTE`
(`MODELO.md` §2), que hoy no tiene uso operativo — existe la tabla, nadie la
alimenta. No se fuerza: cuando `FRENTE` tenga un consumidor real —el
candidato natural es el programa (§15)— esta función se revisita.
