---
name: erp-construccion
description: Modelo de datos, reglas de cálculo y convenciones para construir, clonar, migrar o extender ERPs de construcción en Python (Django/FastAPI) sobre PostgreSQL. Usar SIEMPRE que aparezcan conceptos, matrices, APU, precios unitarios, insumos, destajos, cuadrillas, compuestos, básicos de obra, presupuestos de obra, catálogos de conceptos, prototipos de vivienda, estimaciones, avance, programas de obra o Gantt de construcción — aunque no se nombre "ERP". También al importar o exportar desde OPUS, Neodata u otros sistemas de precios unitarios, y al modelar cualquier árbol presupuestal con partidas e insumos.
---

# ERP de construcción

```
órgano:     reflejo medular
capa:       II — Operación
pregunta:   ¿qué respetar al construir?
tiempo:     se hace así
corte:      2026-09-15
verificado: Derivado de CONOCIMIENTO · 16 errores que previene
```


Este skill destila un sistema real y **verificado**: siete prototipos de vivienda,
un presupuesto de 3,231 renglones, 467 conceptos con explosión, 89 compuestos, 39
cuadrillas y cuatro catálogos de insumo. Los archivos **cierran entre sí al
centavo**.

**Antes de escribir código, leé `CONOCIMIENTO.md`.** Ahí está el detalle por
catálogo. Este archivo tiene las reglas.

---

## 0. El principio de fondo

Apareció solo, cuatro veces, en cuatro datos distintos: el catálogo al contratar, la
unidad del concepto, el precio pactado y la clave del insumo.

> **Mientras nada dependa de un dato, se corrige o se borra. En cuanto algo depende,
> se agrega encima.**

Al implementar, la pregunta nunca es *«¿esto se puede editar?»* sino **«¿ya hay algo
que dependa de esto?»** — y esa el sistema la contesta solo, contando referencias.

---

## 1. El árbol

**Un solo árbol recursivo, padre-hijo, con tipo en el nodo.** No hay una tabla por
nivel jerárquico.

```
presupuesto → capítulo → subcapítulo → nivel → concepto → insumo
                                              ↘ insumo          (directo, es válido)
concepto → compuesto → compuesto → insumo simple                (anidamiento libre)
```

### Tres reglas que se rompen a diario

**El tipo no lo determina la profundidad.** En el presupuesto real, 1,233 conceptos
cuelgan de Nivel 2 y 1,219 de Nivel 3 — mitad y mitad. Y el concepto puede colgar
directamente del presupuesto, de un capítulo o de un nivel.

**El nodo se identifica por posición, no por clave.** La misma clave de insumo
aparece en decenas de nodos con cantidades distintas. Indexar por clave hace que
solo sobreviva la última.

**El mismo insumo puede repetirse en una matriz.** `AUX-00001` lleva alambre
recocido en dos líneas —amarre de varilla y amarre de estribos—. 26 casos
verificados.

**Las cantidades pueden ser negativas.** 58 líneas en 23 conceptos: descuentan
material ya contado dentro de un compuesto. Validar solo positivos las rechaza; en
valor absoluto encarece el concepto **sin que ninguna suma falle**.

### La profundidad es libre

Hoy el anidamiento llega a dos niveles. **El modelo no debe asumirlo.** El recorrido
es recursivo y el único límite es la prohibición de ciclo.

> Una tabla por nivel, un `JOIN` por capa o una consulta de dos saltos funciona con
> los datos actuales y **se rompe con el primer compuesto de tres niveles**.

**La regla alcanza al código generado.** Ningún tipo de cliente, esquema de
validación ni consulta puede asumir cuántas capas tiene el árbol. El nodo se
auto-referencia; en TypeScript eso se resuelve con referencia perezosa, no
aplanando la estructura.

---

## 2. El cálculo

```
importe(insumo)      = cantidad × precio_del_catálogo
importe(compuesto)   = Σ importe(hijos)
importe(concepto)    = Σ importe(hijos)
importe(estructural) = Σ importe(hijos)
PU(concepto)         = importe / cantidad
```

**El precio vive en un solo lugar: el catálogo.** Verificado — los 39 insumos de la
explosión de compuestos coinciden con su catálogo de origen, sin excepción.

### Nunca guardes el resultado como dato

Los agregados se calculan. Si por rendimiento hace falta materializarlos, se marcan
como caché con su marca de tiempo, **nunca como fuente de verdad**.

### El redondeo vive en cada línea, no al final

**El importe de cada línea se redondea a centavos antes de sumarse al padre.** La
cantidad nunca se redondea — arrastra hasta doce decimales por Excel (§8) y es
magnitud física, no dinero.

Verificado con la zapata de `CASO-TRABAJADO.md` §3: sumar sin redondear por línea da
$1,135.47; redondeando cada línea da **$1,135.48**, el costo exacto del catálogo.
Confirma la hipótesis de D-124 — el PU se redondea a centavos antes de multiplicar.
Es la misma deriva de `INVARIANTES.md` §4, ahora con la regla que la reproduce.

### Los tres rendimientos

| Rendimiento | De dónde viene | ¿Se captura? |
|---|---|---|
| **Calculado** | `costo cuadrilla ÷ precio destajo` | Nunca. Siempre existe |
| **Teórico** | El supuesto al presupuestar | Sí |
| **Real** | El medido en obra | Sí, después |

**Su diferencia es un indicador, no un error**: precio mal puesto, cuadrilla
equivocada, o productividad distinta a la supuesta.

> **El enganche solo aplica a destajos.** En un subcontrato el precio incluye
> material y utilidad del tercero: dividir la cuadrilla entre él da un rendimiento
> bajo por construcción.

### El Gantt se calcula, no se dibuja

```
duración = volumen ÷ (rendimiento × número de cuadrillas)
```

**La relación no es lineal**: duplicar cuadrillas no parte el tiempo a la mitad — el
frente tiene un límite físico. Modelá un tope o un factor de eficiencia.

> **No hay precedencias en el modelo.** La fórmula da cuánto tarda cada actividad,
> pero nada dice **qué va antes que qué**. Sin precedencias no hay ruta crítica, y la
> suma de duraciones es una lista, no un programa. **Pendiente con el módulo de
> programa.**

**El programa reagrupa; no reasigna.** Mover un concepto entre actividades cambia
*cuándo* se ejecuta, no cuánto cuesta ni a qué etapa pertenece.

### La unidad `%MO`

Una línea con unidad `%MO` es **un porcentaje sobre la suma de los jornales de esa
cuadrilla**.

```
CUAD-001   Peón          2 JOR  ×  560  = 1,120
           Albañil       1 JOR  ×  760  =   760
                          suma de jornales = 1,880
           Contratista  0.1 %MO ×  1,880 =   188
```

Tres reglas:

1. La base es **la suma de las líneas de jornal**, no el total acumulado.
2. Se captura como `0.1`, **no como `10`**.
3. Con varias líneas `%MO`, **todas usan la misma base**. No se acumulan → **el
   orden de las líneas no afecta el resultado.**

> Distinto de las capas de sobrecosto (§6), donde la cascada **sí** es acumulativa.
> Dos comportamientos en dos niveles del árbol. No unificarlos.

**`%MO` no significa que la línea sea mano de obra**: nombra la base sobre la que se
calcula. El `Contratista` no es mano de obra, es un cargo sobre ella.

---

## 3. Dos lecturas del mismo árbol

> **El compuesto cambia cómo se reporta el monto, no la naturaleza de lo que
> contiene.** La explosión es la prueba de ADN de la matriz; el APU es la
> radiografía.

| Lectura | Cómo recorre | Para qué |
|---|---|---|
| **Reporte de montos** | **Se detiene en el compuesto** y suma a su categoría | Cuánto de la obra es material, cuánto mano de obra |
| **Explosión de insumos** | **Llega hasta el fondo**, cada hoja conserva su naturaleza | Qué se compra, qué se contrata, qué se programa |

**En el reporte de montos, el básico de obra más externo absorbe todo.**

Caso real verificado: `ZA1-000001` es una zapata de $1,135.48 cuyo **41% es mano de
obra contratada** — y reporta 100% como material. Correcto: para la obra, esa zapata
*es* un material.

OPUS ya guarda las dos lecturas en columnas separadas: **`Tipo`** = la naturaleza del
hijo, **`Origen`** = la categoría del padre.

> Sin la lectura profunda, la mano de obra dentro del tabique **desaparecería de la
> planeación** aunque estuviera en el costo. Y la comparación de almacén contra
> explosión no funcionaría: el almacén surte arena, no tabiques teóricos.

---

## 4. Categorías, familia y subfamilia

**Ocho catálogos de insumo:** Materiales · Mano de obra · Herramienta · Equipo ·
Auxiliares · Fletes · Trabajos · Todos. (`Todos` es la vista, no una categoría.)

`Trabajos` **también se llama `Contrato`** según el reporte. Es el mismo catálogo,
con tres clases: `Destajo`, `Acarreo`, `Subcontrato`.

### Tres campos independientes

| Campo | Qué clasifica | Ejemplo |
|---|---|---|
| `Tipo` | **La categoría** — de qué catálogo sale | Material · Trabajo · Mano de Obra · Flete |
| `Familia` | **La naturaleza** | Aceros, Maderas, Albañilería, Peones |
| `Subfamilia` | **El elemento o pieza** | Trabe, Muro, WC, Boiler |

> **`Familia` significa cosas distintas en cada catálogo**: en materiales es la
> sustancia, en trabajos el oficio, en mano de obra el rango. Ocho valores coinciden
> literalmente entre catálogos —Eléctrico, Hidráulico, Sanitario, Gas…— **por
> accidente**, porque en instalaciones la sustancia y el oficio se llaman igual.

### La subfamilia es el sujeto, nunca el calificativo

`MO MURO DE TABIQUE- HILO` → subfamilia **Muro**. *Hilo* es cómo se ejecuta.
*Fachada* no es subfamilia: es ubicación, y sus trabajos van a `Muro`.

**Y cruza catálogos**: filtrar por `Boiler` devuelve sus seis trabajos repartidos en
tres familias. Eso es lo que el paramétrico necesita.

### El compuesto acepta cualquier categoría

**No es homogéneo.** Un compuesto de material lleva mano de obra, flete, lo que haga
falta. El único límite: **no puede contenerse a sí mismo en ninguna de sus capas.**

La diferencia con el auxiliar **no es estructural, es de reporte**:

| | Qué es | A qué reporta |
|---|---|---|
| **Compuesto** | **Depende de** una categoría | A la suya, entero |
| **Auxiliar** | **Es** una categoría | A sí mismo |

*Compuesto* cuando el costo debe verse como su categoría —fabricar tu propio
tabique—; *auxiliar* cuando la mezcla no debe atribuirse a ninguna.

---

## 5. El prefijo de la clave NO es llave foránea

Comprobado en tres catálogos:

| Prefijo | Debería ser | Es |
|---|---|---|
| `MOC` (carpintería) | Carpintería | **ninguna** en Carpintería |
| `MOE` (eléctrica) | Eléctrico | 38 sí, **43 no** |
| `AUX-` | categoría Auxiliar | **`Tipo = Material`** en las 79 |

> **El peor es `AUX-`**: nombra una categoría que el insumo no tiene, y hace concluir
> que las trabes son auxiliares cuando son **materiales compuestos**.

La familia y la categoría van como **campos explícitos**. El prefijo es
nomenclatura.

Y hay un riesgo latente: **conceptos e insumos comparten espacio de claves.** `EQU` y
`HER` colisionan como prefijo; hoy no colisiona ninguna clave completa solo porque
los insumos usan `000xx` y los conceptos `01xxx` en adelante — **una convención
tácita que nada garantiza.**

---

## 6. Motor de cálculo configurable

La convención de precios unitarios **no se codifica**.

**Nivel 1 — factores sobre el insumo.** FSR sobre mano de obra, costo horario sobre
maquinaria. Por tipo de insumo.

**Nivel 2 — capas de sobrecosto.** Tabla ordenada; cada capa declara `orden`,
`nombre`, `tipo`, `valor` y **`base`**.

> **`base` es el campo que hace necesario todo esto.** En México la cascada es
> acumulativa —la utilidad va sobre directo + indirectos + financiamiento—; en el AIU
> colombiano las tres van sobre el costo directo. Codificá una sola y la otra sale mal.

> **Los datos actuales son costo directo puro.** No hay indirectos ni utilidad en
> ningún archivo. El sistema calcula el costo, no el precio de venta.
>
> OPUS sí tiene costos horarios, herramienta, FSR, análisis de indirectos —de campo
> y de oficina— y utilidad. **No están cargados en este proyecto**, y se agregan
> cuando haga falta.

### Modos de valuación

**No son tipos de presupuesto: son modos de valuar un renglón.**

```
ASCENDENTE    el precio sube de los hijos     ← PU, APU, ensamble
DESCENDENTE   el precio se declara y baja     ← alzado
```

**Las partes siempre suben.** El alzado con hijos no rompe la regla: suben ellos y
el declarado queda como cifra paralela. De ahí **dos totales que conviven** —costo y
contratado— y su diferencia es el margen.

Todo renglón alzado necesita un **PU sombra** como base de reparto; sin él no hay
avance parcial ni control de material.

---

## 7. Identidad y posición

> **El árbol es la verdad; el WBS es presentación.**

- **`id` interno** — lo genera la base en el `INSERT`, antes de tener posición. Nunca
  se muestra, nunca cambia.
- **`wbs`** — ruta calculada, separada por puntos (`1.100.01.1523.01`), ancho libre.
  Se recalcula al reordenar.
- **Documentos históricos** — guardan el `id` **más una foto del WBS al emitirse**.

**Renumerar contagia a los hermanos inocentes**: insertar una partida cambia el
número de las que no se tocaron, y una estimación pagada pasa a apuntar a otra cosa.

**La clave nunca se reescribe** —hay contratos apuntándole—. Se **clona**: clonar y
mantener para variantes, clonar y sustituir para reemplazos. **La sustitución se
detiene donde hay contrato.**

**Borrar sí se puede**, solo si nada depende: ninguna referencia, o solo con cantidad
cero. **El borrado no baja**: borrar una mezcla no toca su cemento ni su arena.

---

## 8. Importación

### Las cuatro columnas obligatorias

`Nivel` · `Clave` · `Cantidad` · `Tipo` — **más el orden de las filas**.

**`Cantidad` es el único dato propio del presupuesto**; todo lo demás vive en otro
catálogo. `Tipo` es obligatoria porque 114 nodos estructurales no tienen hijos y ahí
son indistinguibles de un concepto.

De verificación: `Indice` detecta filas perdidas, `Descripción` dispara la alerta de
divergencia, `Unidad` valida.

`Precio unitario` es **señal, no dato**: si difiere del calculado, la explosión
cambió.

### La ingeniería: el presupuesto llega por partes

Archivos **sin encabezados**, cada uno un fragmento. Verificado sobre 11 archivos de
un mismo lote:

| Regla | Detalle |
|---|---|
| **Las partes se suman** | No comparten nivel ni etapa |
| **La fila en blanco separa bloques** | Después de una vacía **siempre** viene un agrupador — 155 casos |
| **Es del lote, no del prototipo** | Y **su descripción puede mentir**: decía Zafiro Plus siendo Diamante |
| **Los compuestos vienen abiertos** | Explosión profunda, no reporte de montos |
| **No trae conceptos** | Se reconstruyen por **reversión de destajo** |

**La reversión por destajo:**

```
1. Comparar totales por etapa  → detecta el PROTOTIPO
2. Filtrar por el prototipo    → desambigua el DESTAJO  (84% resuelve a uno)
3. Aplicar el rendimiento      → reconstruye la CANTIDAD del concepto
```

> El destajo identifica al concepto en el **76%** de los casos; el material solo en
> el 49%. **El destajo es la huella; el material no.**

### Trampas verificadas

| Trampa | Qué hacer |
|---|---|
| **Dos columnas llamadas `Tipo`** en trabajos | El alias no basta: **leer por posición** |
| **121 filas placeholder** sin clave, generadas por OPUS | Descartar, **verificando** que no tengan hijos con clave |
| **`Origen` es la categoría** | `Trabajos`→mano de obra, `Materiales`→material. En un desglosado trae varios valores |
| **`Costo` en líneas `%MO`** | No es un precio: es **la base ya calculada** |
| **Un insumo migra de catálogo** | La categoría es **campo del insumo**, no la tabla. Reconciliar por clave contra **el conjunto completo** |
| **Unidades sin normalizar** | Cuatro estados distintos entre catálogos. No asumir normalización en ninguno |
| `Ingenieria ERP`, `Nivel ERP` | **No se importan** — y tampoco se generan: la regla no es deducible |
| **Archivos sueltos sin agrupador** | La estructura vive **en el nombre del archivo**, no en el contenido |
| **Claves con formato roto** | `HD-00411` (prefijo de 3), `MOS-2079` (4 dígitos). Pasan validación laxa, fallan búsqueda exacta |
| **Anotaciones a mano en la descripción** | El «OK» que marca revisado. Se pierde al normalizar si nadie lo busca |

### Reconciliación y versionado

La clave reconcilia. Bajo la misma clave pueden cambiar tres cosas, **y no pesan
igual**:

| Cambió | Gravedad | Qué hace |
|---|---|---|
| Descripción | Cosmético | Normaliza, alerta si difiere el núcleo, **carga** |
| Matriz | El PU se movió | **Versión nueva**, automática |
| **Unidad** | **Estructural** | **Se detiene ese concepto** |

> La unidad es la peor: si un concepto era `m²` y llega como `pza`, las cantidades de
> todos los presupuestos dejan de significar lo mismo. **Ninguna suma falla — solo
> están mal.**

**Huella del concepto** = `f(unidad, insumos, cantidades)`. La descripción queda
fuera a propósito: si entrara, cada acento generaría versión.

**La secuencia:** leer → comparar → diagnosticar → resolver lo detenido → aplicar
todo junto. Cargar primero y corregir después no sirve: ya se pisó el dato.

---

## 9. Convenciones de código

- **Estructura**: tres carpetas — `backend/` (Render), `database/` (Supabase),
  `frontend/` (web en Vercel, móvil en Google Studio). El móvil consume la misma API
  del backend, **nunca la base directo**.
- **Arquitectura**: monolito con fachadas, migrable a microservicios. *Screaming* y
  *clean*. Los nombres de módulo salen del glosario.
- **El motor de cálculo es núcleo compartido.** `presupuesto`, `apu` y `parametrico`
  usan el mismo. Separarlos en servicios obligaría a duplicarlo o a una llamada
  remota por nodo. Las costuras que sí funcionan: importación, exportación,
  diccionario, contratos, programa.
- **PostgreSQL** con `parent_id` y `ltree`. `ltree` va **detrás de un puerto de
  repositorio**: el recorrido es infraestructura, la regla de qué suma a qué es
  dominio.
- **Sin MPTT ni treebeard.** Su path cambia al mover un nodo: es posición, no
  identidad. La referencia siempre es el `id`.
- **`Decimal`, nunca `float`** para dinero y cantidades. Los datos traen cantidades
  con doce decimales por arrastre de Excel.
- **Unidad siempre como llave foránea.**
- **Precio con vigencia.** Los catálogos envejecen dispar: materiales de esta
  semana, mano de obra de hace tres años. Un PU mezcla épocas sin advertirlo.
- **Vercel serverless agota conexiones**: cadena *pooled* para la app, directa solo
  para migraciones.
- **Nombres en español** para el dominio. El código lo leen constructores.
- **El dinero no cruza la API como número.** `Decimal` en Postgres y en Python;
  **`string` en el JSON** — `"1842430.31"`, no `1842430.31`. OpenAPI tipa los
  decimales como `number`, y `number` en JavaScript es el float que esta misma
  sección prohíbe. El texto no se corrompe; el cliente lo convierte con una
  librería decimal cuando necesita operarlo. **Aplica con o sin generador de
  clientes**: el problema no lo crea la herramienta, lo crea la serialización.
- **El cliente de API se genera desde el spec y no se edita a mano.** Vive en su
  propia carpeta; la siguiente generación lo pisa. Si hay que cambiarlo, se cambia
  el backend y se regenera. Y se decide el punto anterior **antes** de la primera
  generación: después, cambiarlo significa tocar cada componente que ya recibe
  `number`.

---

## 9b. Vocabulario de campos y las tres capas

**Cada campo responde una sola pregunta.** `tipo`, `nivel` y `clase` significan
varias cosas en los datos de origen: están quemadas y no se usan como nombre.

| Campo | Pregunta | Valores |
|---|---|---|
| `rol` | ¿Qué es en el árbol? | ensamble · concepto · insumo · estructural |
| `clase` | ¿Bajo qué figura se ejecuta? | destajo · subcontrato · acarreo |
| `categoria` | ¿Qué referencia el renglón? | material · mano de obra · herramienta · equipo · contrato · concepto |
| `familia` | ¿De qué naturaleza es? | aceros · adhesivos · albañilería… |
| `procedencia` | **¿Qué lo creó?** | importado · manual · ensamble · fusión · división · extracción · composición · clonación |
| `modo_precio` | ¿De dónde sale su precio? | calculado · declarado |
| `modo_cantidad` | ¿De dónde sale su cantidad? | medida · estimada · capturada · heredada |

**La palabra `origen` se retira.** Cargaba dos significados y chocaba con
`origen_precio` y `origen_cantidad`, que pasan a `modo_`.

### `procedencia` no es opcional

Es **lo único que distingue un renglón cargado de uno que produjo el rediseño**. Sin
él, después de aplicar una receta no se puede contestar *¿esto lo trajo OPUS o lo
hicimos nosotros?*

### Las tres capas

```
1. CARGADO    lo que OPUS entregó. INMUTABLE
2. REDISEÑO   lista ordenada de transformaciones
3. VIGENTE    resultado de aplicar 2 sobre 1. Es lo que se edita
```

**El rediseño no es una edición: es una receta.** No se guarda el resultado, se
guardan los pasos, y se reproducen sobre cualquier punto de partida — como las
migraciones de base de datos. *Prototipo nuevo = capa 1 nueva + la misma capa 2.*

Una regla que no encuentra sus piezas se marca **no aplicada**. No se salta en
silencio ni detiene la carga.

### El estado es del nodo, no del presupuesto

Los planos llegan por partes: cimentación se contrata mientras acabados sigue en
diseño. **`estado` no es columna de `presupuesto`** — es tabla aparte por nodo. Del
presupuesto sólo se puede preguntar qué porcentaje de sus nodos está contratado.

**En lo contratado el rediseño se detiene:** se congela la capa 3 y todo pasa por
control de cambio.

---

## 9e. Reversión por destajo: el residuo son cuatro casos

| Clase | Qué hacés |
|---|---|
| Resuelto | Se aplica solo |
| Ambiguo | Propuesta con **todos** los candidatos. Nunca el más probable |
| Clave inexistente | Propuesta con las dos lecturas —errata o alta— **y reporte sin tocar** |
| Destajo de compuesto | No es residuo: **buscá también dentro de compuestos** |

> **Nunca corrijas una clave por proximidad.** Las claves van en secuencia densa: un
> dígito de diferencia cae sobre otro trabajo que existe y es distinto.

**Y una clave que no existe puede ser un cambio no autorizado.** Corregirla o darla de
alta solo borra la evidencia de que alguien cambió algo sin declararlo.

## 9d. Comparar dos fuentes: el dinero primero, la naturaleza después

```
1. cada fuente cierra su dinero en la matriz del concepto   (compuestos cerrados)
2. se explota al fondo para comparar naturalezas            (compuestos abiertos)
```

**Nunca restes a profundidad mixta.** Un insumo puede vivir en dos niveles a la vez
—`ACR-00002` está negativo en la matriz y positivo dentro de la zapata— y mezclarlos
lo cuenta dos veces con signos opuestos.

**En un reporte de profundidad mixta, el importe lo lleva el compuesto cerrado o sus
hijos, nunca los dos.** Es doble contabilidad en esa rama.

## 9c. Si el dato se contradice, parás

**No elijas el valor que conviene y sigas.** Una contradicción resuelta en silencio
reaparece cuando ya hay código encima de las dos versiones.

Protocolo completo en `METODO.md` §3.5. Lo mínimo al construir:

- **Descartá primero** que sea el mismo hecho en dos fechas, dos ámbitos o dos bases.
- Si es contradicción real: **no la modeles.** Un campo provisional deja de serlo en
  cuanto algo depende de él.
- Reportala con las dos afirmaciones y dónde vive cada una.

## 10. La propuesta

**«El sistema propone, el humano aprueba» necesita un lugar propio**, no un campo en
cada mecanismo. Una entidad `propuesta` con: tipo, objeto, valor sugerido,
**evidencia**, origen —persona o agente—, estado y quién resolvió.

- **Una propuesta sin evidencia es una orden disfrazada.**
- **El rechazo se conserva**: sin eso, un agente que aprende de lo aprobado
  reproduce indefinidamente lo que ya se rechazó.
- **La detección nunca necesita permiso; la corrección siempre.**

---

## 11. Los dieciséis errores que este skill previene

1. Indexar el árbol por clave de insumo en vez de por posición.
2. Asumir que la profundidad determina el tipo de nodo.
3. Fijar el número de capas de anidamiento.
4. Guardar el PU del concepto como dato en vez de calcularlo.
5. Deducir la familia o la categoría del prefijo de la clave.
6. Creer que `AUX-` significa categoría auxiliar.
7. Suponer que un compuesto solo admite insumos de su categoría.
8. Explotar el compuesto en el reporte de montos, o detenerse en él en la explosión.
9. Leer `Costo` como precio en las líneas `%MO`.
10. Cargar un insumo dos veces porque migró de catálogo.
11. Tomar una de dos columnas homónimas por nombre.
12. Cargar las filas placeholder de OPUS como nodos.
13. Fusionar o renombrar claves duplicadas en la migración.
14. Codificar la cascada de sobrecostos de un solo país.
15. Dejar que reorganizar el programa mueva dinero entre etapas.
16. Rechazar o absolutizar las cantidades negativas.
