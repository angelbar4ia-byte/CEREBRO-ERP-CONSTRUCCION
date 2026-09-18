# CONOCIMIENTO

```
órgano:     corteza asociativa
capa:       I — Mundo
pregunta:   ¿cómo funciona el sistema?
tiempo:     es así
corte:      2026-09-15
verificado: 16 partes · cada regla comprobada antes de escribirse
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
| §5 | Presupuesto paramétrico — ensambles | 240 | 10 |
| §6 | Destajos: precio, cuadrilla y fusión | 157 | 4 |
| §7 | Modos de valuación | 82 | 3 |
| §8 | Operaciones de rediseño | 133 | 5 |
| §9 | Concepto compuesto — matriz dentro de matriz | 58 | 4 |
| §10 | Categorías | 168 | 6 |
| §11 | Los flujos entre sistemas | 468 | 12 |
| §12 | Las tres capas del rediseño | 52 | 3 |
| §13 | Contratación, cambios y obra en marcha | 318 | 6 |
| §14 | La propuesta | 66 | 5 |
| §15 | La ruta crítica no está en el modelo | 39 | 0 |
| §16 | Normalización, homologación y grupos funcionales | 60 | 4 |

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
existe**: la descomposición en desviación de precio y de consumo, y las seis causas
con quién paga cada una (§13.6).

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
ninguna de las seis causas de §13.6. Se marca como alerta. Alguien decide si es
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

## 11.12 La tercera pata: salidas de almacén — pendiente

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

### Las seis causas, y quién paga cada una

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
