---
name: erp-importacion
description: Cargar presupuestos y catálogos desde OPUS, Neodata u otros sistemas de precios unitarios hacia el ERP de construcción. Usar al escribir o modificar el cargador, al mapear encabezados de un export, al decidir qué hacer cuando un concepto cambió en el sistema origen, al versionar conceptos, o al diagnosticar por qué una carga no cuadra. NO cubre el cálculo del APU ni el rediseño — ver `erp-construccion` y `erp-rediseno`.
---

```
órgano:     vía mielinizada — importación
capa:       II — Operación
pregunta:   ¿cómo entra un dato ajeno sin romper lo que ya existe?
tiempo:     se hace así
corte:      2026-10-12
verificado: releído el 2026-10-12 contra el cambio que `CONOCIMIENTO.md` §2 tuvo ese día (la huella sin la unidad): el skill ya lo decía
compilado:  `CONOCIMIENTO.md` §2 · `CATALOGOS.md` §11 · `CONOCIMIENTO.md` §4.2 · lo que D-472 a D-479 agregaron a `CONOCIMIENTO.md` (la carga persistida,
            la reconciliación, la alerta de texto, la clonación) y `METODO.md` §2.6 — no se escribe a mano
```

> **Satélite.** Carga el skill base `erp-construccion` primero: el árbol, el motor,
> las dos lecturas y las convenciones de código viven ahí y **no se repiten aquí**.

---

## 0. La regla de fondo de la importación

> **Lo derivable no se importa: se recalcula.**

`Ingenieria ERP` y `Nivel ERP` se diseñaron para un ERP de terceros sobre el que no
hay control — pueden venir truncas, cambiar de formato o desaparecer. El WBS se
calcula aquí, por posición.

Y no basta con no confiar: **la prueba de ida y vuelta demostró que esas columnas
tampoco se pueden generar** — la regla no es deducible de los datos.

> *D-615:* el valor del archivo se **conserva como rastro** hacia OPUS (en el nodo,
> sin mostrarse); **ni el árbol ni la identidad lo usan**, así que el árbol queda
> igual con o sin esas columnas. Lo que sigue prohibido es usarlo para armarlo.

---

## 0b. Lo primero: guardar lo que se sube

Lo que el usuario sube a una sesión vive en una carpeta temporal y **se pierde con la máquina**. Antes de leer una tabla —antes del informe de
mapeo, antes de cualquier cuenta— se guarda en el repo:

```
cd backend && python3 -m api.guardar_subidas             guarda lo nuevo (por su huella); un libro de Excel queda tal cual y cada hoja, en CSV
cd backend && python3 -m api.guardar_subidas --verificar comprueba que todo lo guardado sigue ahí, sin cambios
```

Los de OPUS van a `1-mundo/opus/`; el resto, a `1-mundo/fuentes/`, con su huella en `MANIFIESTO.csv`. Después, commit y push. Una prueba del CI falla si
falta una tabla, si cambió o si llega una que el manifiesto no conoce (`METODO.md` §2.6, D-479). **No se vuelve a pedir lo que ya se subió.**

---

## 1. La clave es la verdad

Al reimportar, un concepto con la misma clave **es el mismo concepto**. La carga
nunca lo descarta ni lo duplica.

Bajo una misma clave pueden cambiar tres cosas, y **no pesan igual**:

| Cambió | Gravedad | Qué hace la carga |
|---|---|---|
| **Descripción** | Cosmético — se dice distinto, cuesta lo mismo | Normaliza, alerta si es significativo, **carga** |
| **Matriz** (insumos o cantidades) | Económico — el PU se movió | **Versión nueva**, automática |
| **Unidad** | **Estructural** — deja de ser comparable | **Se detiene ese concepto** |

### Por qué la unidad es la peor

Si un concepto era `m²` y llega como `pza`, las cantidades de todos los presupuestos
que lo usaron dejan de significar lo mismo. Los 120 m² de ayer no son las 120 piezas
de hoy.

> **Y ninguna suma va a fallar. Sólo va a estar mal.**

Por eso no es alerta pasiva: es alto. Alguien decide si fue una unidad mal capturada
o si es otro concepto metido en la clave equivocada — y en ese caso el sistema
propone clave nueva.

**Las cantidades no se convierten solas.** O quien corrige da el factor, o cada
presupuesto afectado queda marcado para revisión. Convertir en automático sería
inventar números.

---

## 2. La huella

```
huella = f(insumos, cantidades)
```

Se calcula al cargar y se compara con la anterior. **Si cambió, cambió** — aunque el
texto sea idéntico y aunque el PU dé la misma cifra por coincidencia. Una cantidad
`1.050000` y una `1.05` son la misma; una línea repetida (el alambre de `AUX-00001`)
cuenta dos veces; el orden de las líneas no cuenta.

> **La descripción queda fuera de la huella a propósito.** Si entrara, cada
> corrección de acento generaría versión y el versionado perdería sentido.

> **La unidad también quedó fuera** *(D-473, corrige a `CONOCIMIENTO.md` §2.7, que la
> definía con ella)*: se compara **aparte y antes**. Si cambió, el concepto se detiene sin
> mirar la receta; y si antes no se sabía, saber cuál es no cambia la receta ni crea
> versión.

**Lo que más señal da:** texto significativamente distinto **y** huella distinta. Ya
no es otra descripción — es otro concepto: **se detiene** (motivo `texto_y_receta`) y
el sistema **propone la clave nueva** —la siguiente libre del mismo prefijo, con el
mismo ancho—. Quien decide puede confirmar que es el mismo, y confirmar una clave
confirma a la vez la compuerta del 5 % (§3). Un texto que cambia **sin** la receta
carga y alerta.

### Qué diferencia de texto dispara alerta

Un porcentaje de diferencia no sirve: engaña en los dos sentidos. *De 3.00 a 4.20 m*
es cambio mínimo de texto y enorme de significado; reordenar una frase es lo
contrario.

Primero se normaliza —minúsculas, acentos, plurales, conectores, quitar el «Incluye:»
y los sinónimos que se den— y se compara el núcleo. Idéntico → cosmético, sin alerta.
Si difiere:

| Cambió | Nivel |
|---|---|
| Un número o dimensión (se comparan como números: *3.00* es *3*) | **Alta** |
| El verbo o el elemento (*colocación* → *suministro*) | **Alta** |
| El orden de las palabras, o un calificativo (*nuevo*, *similar*, *aproximado*, *corregido*…) | Informativo |

Ante una palabra que no es calificativo se alerta: «alerta» por sí sola no detiene nada;
lo que detiene es cruzar el texto con la huella. **El diccionario de sinónimos no
existe todavía** (la comparación lo recibe como parámetro): sin él, *fabricación* y
*elaboración* son palabras distintas.

---

## 3. Versionado

```
Concepto             ← identidad: la clave. Una sola, para siempre
├─ Versión 1         insumos + cantidades + PU
└─ Versión 2         la explosión cambió
```

**Cualquier cambio en el conjunto de insumos o en sus cantidades crea versión nueva.
Sin umbral, automático.** La versión es barata y es la verdad. El umbral difuso queda
sólo para el texto, que es donde «muy diferente» sí es juicio.

El renglón del presupuesto apunta a **una versión concreta**, no a la clave suelta.

### Quién aprueba

Por defecto, nadie. La versión se crea y entra en vigor sola. La aprobación aparece
sólo cuando hay algo en juego, medido por impacto:

| Uso del concepto | Qué pasa |
|---|---|
| Sin presupuestos | Automático y silencioso |
| Sólo en diseño | Automático, pero **avisa** a quienes usan esos presupuestos |
| Algo contratado | **No entra en vigor.** La versión se detiene (`en_contratado`), ninguna confirmación la deja pasar, y va a control de cambio |

Más una compuerta por magnitud: **si el PU se movió más de 5%, pide confirmación**
aunque sea en diseño.

**El PU de una versión se congela al crearse**, calculado con el motor sobre el archivo que se carga, y no se recalcula nunca. **Un precio que se mueve no es una
versión:** es una fila de `PRECIO_HISTORICO` (el precio de un *trabajo* es la excepción: se valida). El renglón del presupuesto fija la versión que tenía al cargarse.

> **El silencio nunca aprueba.** Sin respuesta queda pendiente, no vigente por
> vencimiento de plazo.

---

## 4. Las cuatro columnas obligatorias

| Columna | Para qué | Por qué no se deriva |
|---|---|---|
| `Nivel` | Profundidad → arma el árbol | Sin esto no hay jerarquía |
| `Clave` | Identidad y reconciliación | Es la verdad |
| `Cantidad` | Volumen de obra | **Es el único dato propio del presupuesto** |
| `Tipo` | Distingue agrupador de concepto | Ver abajo |

**Más el orden de las filas**, que junto con `Nivel` reconstruye la jerarquía. **Si
falta una de las cuatro, la carga no procede.**

### Por qué `Tipo` es obligatoria

Casi todo se derivaría de la estructura —todo concepto es hoja, todo estructural
tiene hijos—. **La excepción rompe la regla: 114 filas de Nivel 3 no tienen hijos**,
y ahí un agrupador vacío es indistinguible de un concepto.

### `Origen` es la categoría

No se descarta. En un export de sólo conceptos trae un valor único; **un presupuesto
desglosado traerá mano de obra, materiales, herramienta y equipo** en esa columna.

### Las tres de verificación

No arman nada, pero detectan que algo se rompió:

| Columna | Qué detecta |
|---|---|
| `Indice` | Filas perdidas o reordenadas. Es la suma de control del árbol |
| `Descripción` | Divergencia contra el catálogo |
| `Unidad` | Que el presupuesto no contradiga al concepto |

Las tres deberían venir del catálogo de conceptos. Si llegan, **se comparan; no se
cargan encima**.

### `Precio unitario`: señal, no dato

El PU se crea en el APU. Pero si el PU importado difiere del calculado desde la
explosión vigente, **la explosión cambió** → dispara el versionado. Se guarda como
*observado*, nunca como fuente.

### Lo que se descarta

`Ingenieria ERP` y `Nivel ERP` (se generan) · `Total` (cantidad × PU) · `%` ·
`Descripción de matriz` y `Unidad de matriz` (vienen del APU) · `Descripción corta`
(del catálogo) · `Ruta paramétrica` (es el paramétrico de OPUS; el nuestro se
construye aquí).

---

## 4b. Normalizar la unidad al cargar

**Los catálogos vienen limpios; el presupuesto no.** Verificado sobre los datos
reales:

| Fuente | Unidades distintas | Forma |
|---|---|---|
| Catálogo de unidades | **17** — `PZ` `M2` `M` `M3` `KG` `SAL` `ACT` `SERV` `JOR`… | Canónicas |
| Materiales · Trabajos · Conceptos | 13 · 5 · 7 | **Todas del catálogo, en mayúsculas** |
| **Presupuesto** (4,890 renglones) | 7 | **Vocabulario paralelo** |

```
pza → PZ     sal → SAL     m2 → M2     m → M
act → ACT    m3 → M3       ser → SERV
```

> **No es un problema de mayúsculas:** `pza` no es `PZ` en minúscula y `ser` no es
> `SERV`. Son abreviaturas distintas para lo mismo.

**Se normaliza al cargar y se guarda ya normalizada.** Aquí normalizar es seguro
porque hay **catálogo cerrado y mapeo uno a uno verificable** — al revés que corregir
una clave por proximidad, donde no hay mapeo sino cercanía.

### Unidad desconocida: se carga, no se bloquea

Una cadena que no mapea a ninguna de las 17 **entra igual**, y se da de alta en el
catálogo marcada **por validar u homologar**. Van a aparecer unidades nuevas y no
pueden detener una carga.

> Coherente con la regla de la unidad base: **la validación es la excepción, no el
> paso por defecto.**

### No confundir con el cambio de unidad

Son dos cosas distintas y las dos siguen vivas:

| Caso | Qué hace |
|---|---|
| **Unidad desconocida** — cadena nueva | Se carga · alta en catálogo por validar |
| **Unidad que cambia** en un concepto existente | **Se detiene ese concepto** (§1) |

El segundo es estructural: si un concepto era `m2` y llega como `pza`, las cantidades
de todos los presupuestos que lo usaron dejan de significar lo mismo.

### El caso aparte de `(%)mo`

El catálogo de mano de obra trae 96 `JOR` y **un `(%)mo`**. No es una unidad: es la
línea de porcentaje sobre mano de obra. No entra al mapeo.

## 5. Mapeo de encabezados

El cargador **no busca por posición ni por nombre exacto**. Lleva alias por campo:

```
nivel      ← "Nivel", "Nivel ", "NIVEL", "Nv", "Profundidad"
clave      ← "Clave", "CLAVE", "Código", "Clave concepto"
cantidad   ← "Cantidad", "CANTIDAD", "Cant", "Volumen"
tipo       ← "Tipo", "TIPO", "Clase"
```

Lo mismo con el nombre del catálogo: `Trabajos` y `Contrato` son el mismo.

> **Cuando dos columnas comparten nombre, el alias no basta: hay que leer por
> posición.** Pasa con `Tipo` en el catálogo de trabajos.

**Antes de cargar nada, un informe de mapeo**: qué columna se leyó como qué campo,
cuáles no se reconocieron, cuáles obligatorias faltan.

---

## 6. Reconciliación

Las filas llegan sin `id`. La primera carga lo asigna y **guarda la llave natural** —
clave, y para los nodos estructurales la **ruta natural** (`clave#n/clave#n…`, la
*n*-ésima vez que esa clave aparece entre sus hermanos).

> Sin eso, la segunda importación **duplica todo el árbol**.

---

## 6b. La obra fija su base al arrancar

**El presupuesto base se actualiza cada seis meses.** Una obra en curso **conserva la
base que tenía al arrancar**, aunque el catálogo avance.

```
la obra se abre      →  fija la versión de cada concepto que va a usar
llega una parte      →  se resuelve contra esa versión, no contra la vigente
el catálogo avanza   →  la obra no se entera, y eso es correcto
```

> **La base se fija al arrancar la obra, no al cargar cada parte.** `ALAMO 18` cargó
> doce archivos de abril a septiembre — un ciclo completo. El archivo de septiembre
> se resuelve contra la base de abril.

Esto no contradice el versionado: **el renglón ya apunta a una versión concreta, no a
la clave suelta.** Lo que faltaba era decir quién la fija y cuándo.

**Consecuencia al comparar:** una obra con base vieja **no tiene desviación por eso**.
Comparar contra el catálogo vigente produce diferencias que son de calendario, no de
obra — fue exactamente lo que pasó con el cemento al 35% de `ALAMO 18`.

## 6c. Un presupuesto que ya existe se reconcilia, no se pisa (D-476)

Un capítulo se reconoce por su clave. Si llega **igual**, se dice («ya está, igual») y no se escribe nada. Si llega distinto, se casa **por ruta natural**: un renglón
que sigue siendo el mismo conserva su identidad, y con ella los enlaces del programa.

| Cambió | En diseño | En lo contratado |
|---|---|---|
| Una cantidad | Entra, con su historia | **No entra nada** |
| Un renglón o un bloque nuevo | Entra, con la versión vigente y en su lugar | — |
| El lugar entre hermanos | Entra, con su historia | — |
| **Una baja** | **Pide confirmación** con un id que el informe da (`ruta::CLAVE#n`), o todas juntas; un bloque que se va se lleva lo que cuelga con una sola | — |

**Una baja no borra:** el renglón deja de contar —en el presupuesto, en el motor, en el lugar que ocupaba— y se queda, porque el programa lo puede citar. La historia de un
renglón (alta, cantidad, lugar, baja) **solo se agrega**. Si algo quedó detenido (una baja sin confirmar, un concepto pendiente), el presupuesto queda marcado `parcial` y se vuelve a ofrecer lo que falta. Antes
de confirmar una baja se dice **qué programas la citan**.

---

## 6d. La clave vieja de un clon sigue entrando (D-478)

Cuando una clave se corrige por clonar y sustituir (`erp-rediseno` §5), los archivos de OPUS siguen trayendo la clave vieja. La carga **los lee con las claves vigentes**:

- la vieja se lee como el clon, de padre y de hijo, y los conceptos del presupuesto también; **lo dice** en un aviso, no lo hace en silencio;
- si el archivo trae las dos —la vieja y el clon— con matriz, **manda la del clon**: no se suman;
- lo retirado **no sale como «ausente»** ni como concepto nuevo;
- un cambio de receta en el archivo versiona **al clon**, y un precio nuevo entra a **su** historia.

El viaje de vuelta (la clave vieja sigue saliendo hacia otros sistemas hasta que alguien lo autorice) es hoy solo una bandera: no hay exportador.

---

## 7. Placeholders

OPUS genera renglones estructurales vacíos al explotar por agrupadores. **Son andamio
del export, no datos.** 121 filas, el 3.7%.

Se descartan sólo si cumplen las dos condiciones, **verificadas, no supuestas**:

- importe en cero, **y**
- sin descendientes con clave

> Si alguna vez un placeholder tuviera un hijo costeado, **eso es un error que se
> reporta, no una fila que se tira en silencio.**

---

## 8. La secuencia de carga

Cargar primero y corregir después no sirve: **ya se pisó el dato y se perdió contra
qué comparar.**

```
1. Se lee el archivo              nada se escribe todavía            revisar
2. Se compara contra lo vigente   huella por concepto                revisar
3. Se muestra el diagnóstico      qué entra, qué versiona, qué se detiene
4. Alguien resuelve               sólo lo detenido                   confirmar
5. Se aplica                      todo junto, en una transacción     aplicar
```

**Lo que se detiene no es la carga: son los conceptos en conflicto.** El resto entra
normal. Se detiene, con su motivo: la unidad que cambió, el PU que se movió más de 5 %
sin confirmar, el texto que cambió junto con la receta, lo que depende de algo detenido,
la versión de lo que fija un renglón contratado, el precio de un trabajo, y una baja sin
confirmar. **`revisar` no escribe nada; `aplicar` escribe el plan completo o nada**, y si
entre una y otra se cargó otra cosa (cada plan trae la última carga que vio), no se
escribe: `CatalogoCambio`. Si el archivo trae algo que no cuadra, no se escribe nada.

En la terminal: `python3 -m api.cargar_opus` revisa; con `--aplicar` escribe (solo un usuario con la
función `cargar_catalogo_opus`). Por la API (D-482): `POST /cargas/propuestas` revisa —trae el informe, lo
detenido y la `base`, la última carga que vio quien revisó— y `POST /cargas` aplica; ahí se manda `esperaba`
con esa `base`, y si otro cargó, contrató o clonó entre las dos, responde 409 `conflicto` y no escribe nada.

```
412 conceptos entran sin cambios
 18 versionan — cambió su matriz
  3 detenidos — cambió la unidad
```

> Si nadie resuelve y se va, la carga **queda guardada como pendiente**. Lo que no se
> hace es aplicarla a medias sin registro: entonces nadie sabe que faltan tres.

---

## 9. Los errores que este skill previene

1. Importar `Ingenieria ERP` en vez de calcular el WBS.
2. Sobrescribir la explosión de un concepto sin versionar — los presupuestos
   históricos pasan a mostrar un PU distinto del contratado, **sin que nadie lo note**.
3. Meter la descripción en la huella y versionar por cada acento.
4. Descartar `Origen` porque en este archivo trae un valor único.
5. Buscar columnas por posición cuando el archivo cambió de formato.
6. Leer por nombre cuando **dos columnas se llaman igual**.
7. Tirar los placeholders sin comprobar que no tengan hijos costeados.
8. Convertir cantidades solo porque cambió la unidad.
9. Cargar y luego corregir: ya no hay contra qué comparar.
10. Aplicar la carga a medias sin dejar registro de lo que faltó.
11. Meter la unidad en la huella: versiona por una unidad que apenas se aprendió.
12. Dejar entrar la versión nueva de un concepto que fija un renglón contratado.
13. Reconciliar un presupuesto por número de fila en vez de por ruta natural: los enlaces del programa dejan de valer.
14. Borrar una baja, o aplicarla sin confirmación: el programa puede citar lo que se va.
15. Tratar la clave vieja de un clon como concepto nuevo o como «ausente».
16. Leer una tabla que el usuario subió sin haberla guardado antes en el repo.
