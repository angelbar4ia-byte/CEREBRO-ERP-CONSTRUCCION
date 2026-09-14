# IDEAS POR DESARROLLAR

```
órgano:     —
capa:       IV — Dirección
pregunta:   ¿qué se pensó y aún no se diseña?
tiempo:     vamos aquí
corte:      2026-09-12
verificado: 6 ideas · ninguna diseñada
```

> **Sólo las ideas del modelo que aún no se diseñan.** Todo pendiente de datos, de
> decisión o de tarea vive en `PENDIENTES-MEJORAS.md`.

---
> **Aquí solo las ideas del modelo que aún no se diseñan.** Todo pendiente de datos,
> de decisión o de tarea vive en `PENDIENTES-MEJORAS.md` — un pendiente en dos
> archivos se separa y uno miente (`INDICE.md`).

| Idea | Sección |
|---|---|
| La matriz a partir de la descripción | §1 |
| Módulo de cuantificación gráfica | §2 |
| Clasificar los materiales: dos ejes | §3 |
| Constructor de matrices | §4 |
| Cambiar la unidad de un insumo | §5 |
| Corregir el prefijo `AUX-` | §6 |

## 1 Idea: la matriz a partir de la descripción

Que el **agente interno** proponga la matriz leyendo la descripción del concepto.
Valioso para auxiliares, compuestos y conceptos, incluyendo sus categorías.

Tres partes con dificultad muy distinta:

| Parte | Viabilidad |
|---|---|
| **Estructura** — que lleva estuco, mano de obra y agua | Alta: patrón contra los 467 APU existentes |
| **Insumos concretos** — qué clave de material | Alta, apoyada en el diccionario |
| **Cantidades** — el `0.13125` por m² | **Aquí no.** Ver abajo |

### Las cantidades no se generan

`0.13125` sacos por m² sale del espesor, del rendimiento del saco y del
desperdicio.

> Un agente que las genere produce números **plausibles y equivocados**. Es peor
> que dejarlas vacías: el APU se ve terminado.

### Razonar por analogía, no generar

En vez de inventar la matriz, **buscar el APU existente más parecido**, copiar su
estructura con sus cantidades reales, y marcar en qué difiere.

- Las cantidades vienen de un APU verdadero
- Se puede mostrar **de cuál salieron**
- Si no hay análogo, lo dice — en vez de rellenar

### La descripción trae los números

*3 mm de espesor* · *altura máxima 3.00 m* · *PVC 6" desarrollo 24.00 m*

Extraer esos parámetros del texto y usarlos para **escalar** las cantidades del
análogo es verificable, no adivinanza.

### El corpus ya existe

Los 89 conceptos que solo cambian de prototipo y las 22 familias detectadas
(`DICCIONARIO-DATOS.md`) son la base. No se entrena desde cero.

> Como todo en este sistema: **propone, no aplica.** Estado `propuesto`, con la
> procedencia visible.

### El agente aprende de lo que se decide

Cada matriz aprobada, corregida o rechazada **engorda el corpus de análogos**. Lo
que el usuario decidió al final es la mejor señal que existe.

Y sigue siendo auditable, porque **el aprendizaje es acumular casos, no reentrenar
un modelo opaco**: siempre se puede señalar de qué APU aprobado salió una propuesta.

Es el mismo principio del diccionario: **los rechazos se conservan**, porque también
enseñan.

## 2 Idea: módulo de cuantificación gráfica

Crear el presupuesto **trazando sobre el plano**, al estilo de PlanSwift o
Navisworks.

> **Resuelve de dónde nace la cantidad.** Se estableció que es el único dato propio
> del presupuesto (`CONOCIMIENTO.md` §2.4), pero no de dónde sale. Sale de aquí.

### La plantilla nace del árbol

El módulo **no inventa estructura**: consume el árbol de presupuesto con sus
matrices y compuestos. Solo se dedica a trazar. Si hace falta algo que no existe,
crea un concepto nuevo.

### Trazo, medida y cantidad son tres cosas

```
TRAZO      la geometría sobre el plano      un polígono, una línea, un punto
MEDIDA     lo que se deriva de él           área, perímetro, longitud, conteo
CANTIDAD   medida × factor → al concepto    área → piso  ·  perímetro → zoclo
```

**Un solo trazo alimenta varios conceptos.** El polígono de una recámara da el área
para el piso y el perímetro para el zoclo. Si se guardara solo la cantidad, habría
que trazar la recámara tres veces.

### El trazo queda ligado

La cantidad no se copia: **se enlaza**. Si se corrige el trazo, la cantidad se
actualiza sola.

Y el trazo carga su evidencia —qué plano, qué versión, qué capa, qué polígono—, que
es lo que vuelve auditable una cuantificación.

> **La versión del plano importa.** Si el plano cambia, las cantidades trazadas
> sobre el anterior quedan marcadas para revisión, no se recalculan solas.

### El árbol del cuantificador

Navisworks organiza la cuantificación en árbol, y ese patrón sirve aquí: **el árbol
del cuantificador refleja el del presupuesto**. Trazar es colgar geometría de un
renglón que ya existe.

### El cuantificador NO se tipa

No hay «cuantificador de PU», «paramétrico» ni «alzado».

> El modo ya está declarado en el nodo que recibe (`modo_precio`, `CONOCIMIENTO.md` §7.1). Si el
> cuantificador también lo declarara, la misma distinción viviría en dos lugares —
> y algún día se contradicen.

**Lo que sí se tipa es el enlace**: qué medida toma y con qué factor.

| El nodo receptor | Lo que la cantidad significa ahí |
|---|---|
| Por PU | Volumen de obra |
| Paramétrico | El divisor del ensamble (`CONOCIMIENTO.md` §5.7) |
| Alzado | La unidad del precio declarado |

Así **el mismo polígono alimenta los tres a la vez**, y cada uno toma lo que le
sirve. La mezcla por renglón sale sola, sin declararla en ningún lado.

## 3 Clasificar los materiales: dos ejes que faltan

Al aislar insumos en `Fletes` (`CATALOGOS.md` §6) aparecieron **dos necesidades distintas**, y
ninguna es familia ni subfamilia.

> La familia dice **de qué es**. La subfamilia, **qué pieza es**. Estas dicen
> **cómo se adquiere** y **con qué frecuencia se usa**.

### Presentación de compra: la unidad de compra ≠ la de consumo

Caso real: **no es práctico comprar 0.026 de un camión de 14 m³.** Las tablas igual:
se consumen por pieza pero se entregan por lotes de 10.

```
Arena de río     consumo     m³
                 compra      camión de 14 m³        factor 14
                 mínimo      1 camión (indivisible)

APU dice         0.026 m³          ← el consumo real, sin distorsión
Compra dice      1 camión          ← redondeo al alza obligatorio
```

**Modelado así el problema se resuelve en vez de aislarse.** Y aparece algo que hoy
no se ve:

> Si se compran 14 m³ y se usan 8, **los 6 restantes no son desperdicio: son
> inventario.** Se vuelven pérdida solo si ningún otro concepto los consume.

Es exactamente lo que la comparación de almacén contra explosión (`CONOCIMIENTO.md` §13.6) debe
distinguir — y sin este mecanismo no puede.

### Recurrencia: se usa siempre, o a veces

La prueba hidráulica —lija, tapa, cople, manómetro— no tiene problema de unidad: se
compra y se consume igual. Lo que tiene es que **no siempre se usa**.

Eso sí es una etiqueta: `recurrente` contra `eventual`.

### Resumen

| Necesidad | Campo | Resuelve |
|---|---|---|
| Unidad de compra ≠ de consumo | **Presentación de compra**, con factor y mínimo | Arena, grava, tablas por lote |
| Se usa a veces | **Recurrencia** | Prueba hidráulica |

## 4 Constructor de matrices

Generar la matriz de un elemento en vez de armarla a mano. **No es un constructor,
son tres**, y no tienen la misma naturaleza:

| Tipo | De dónde salen las cantidades | Ejemplos |
|---|---|---|
| **Paramétrico** | **Se calculan** con fórmulas | Trabe, zapata, castillo, losa |
| **De plantilla** | Lista fija con variantes | WC, boiler, regadera |
| **De composición** | Alguien las pone | Recámara, baño |

Los dos últimos ya están definidos: son el **ensamble** de `CONOCIMIENTO.md` §5, en su forma plantilla
y en su forma instancia. **El que aporta capacidad nueva es el paramétrico.**

### Orden acordado

```
1. ESTRUCTURAL      ← el que sí hay que hacer
2. INSTALACIONES    ← con más ambición: albercas, fotovoltaico
3. CARPINTERÍA
```

Los dos últimos no son imposibles, pero **exigen más alcance del que hoy tienen los
datos**: deben poder resolver salidas hidrosanitarias que aún no existen —albercas,
sistemas fotovoltaicos— y no solo replicar lo ya costeado.

### 1. Estructural — el que sí hay que hacer

De *«trabe de 15×25, 6 m, f'c 250, armado 4#4 con estribos #2 a 20 cm»* sale todo
por cálculo:

- Volumen de concreto → geometría
- Acero → peso por metro × longitud + ganchos y traslapes
- Cimbra → superficie de contacto
- Desperdicio → factor configurable

**Todo son fórmulas, no juicio.**

> **Ventaja de partida:** ya existen **89 compuestos** con subfamilias `Trabe`,
> `Contratrabe`, `Nervadura`, `Parrillas`, `Losa Nervada` (`CATALOGOS.md` §2). No hay que
> inventar el catálogo: hay que **darle fórmula a lo que ya existe** — y validar el
> generador contra las trabes ya costeadas. Si genera la T-3 y da $72.14, funciona.

### 2. Instalaciones

Las cuatro fases —punta, ranura, cableado, accesorios— **ya están sistematizadas**
en el catálogo de trabajos (`CATALOGOS.md` §3). El parámetro es el desarrollo de manguera y cable
desde el centro de carga.

En sanitarios, el parámetro real es **la distancia de ramaleo**: es lo único que
varía entre un WC y otro.

### 3. Carpintería — la más difícil, y no por técnica

Un clóset se mide en metros lineales, pero lo que cuesta depende de entrepaños,
cajones y herrajes.

> **Dos clósets de 3 ml pueden diferir al doble.** El parámetro no es la medida sino
> el nivel de equipamiento, y eso hay que definirlo antes de generar nada.

### Dos clases de dato, que no se mezclan

| Qué es | Dónde vive | Ejemplo |
|---|---|---|
| **Constante física** | Tabla de datos | Peso de la varilla, densidad del concreto |
| **Regla de la operación** | Este documento | Ramaleo de 4", clóset con entrepaños |

La primera es universal y se consulta. La segunda es propia, cambia si cambia el
criterio, y **es lo que hace que el generador produzca los APU de esta empresa y no
unos genéricos.**

### Falta capturar

Peso por metro de cada varilla · factores de traslape y gancho · desperdicio por
tipo de elemento · calibre por tipo de circuito · puntas por circuito.

### La advertencia

> **Una fórmula equivocada se multiplica en silencio.** Un APU mal armado a mano lo
> ve alguien; uno generado sale igual de mal en cien elementos y todos se ven
> correctos.

Por eso la validación contra los APU existentes no es una prueba inicial: es un
**control permanente**.

## 5 Cambiar la unidad de un insumo

Poder cambiar la unidad **desde la matriz**, sin crear un insumo nuevo. Hoy, para
tener cemento en kilos y en sacos, hacen falta dos claves — que pueden
desincronizarse de precio.

Con **presentación de compra** (§3) es un solo insumo con varias formas, y el APU
elige cuál usa.

### Afecta al rendimiento

El factor convierte **cantidad**. Pero el rendimiento es una **razón entre dos
unidades**, así que el número se mueve aunque la productividad sea idéntica:

```
30 m² por jornada        el muro se pasa a piezas de tabique
                         50 pza/m²
= 1,500 pza por jornada  el albañil trabaja igual; el número cambió 50 veces
```

### El rendimiento se guarda con su unidad anclada

Nunca como un número solo. Arrastra **tres anclajes**:

```
30 m² por jornada  de esa cuadrilla
   └┬┘    └──┬──┘      └────┬────┘
  obra    tiempo         quién
```

En el enganche (`CONOCIMIENTO.md` §6.2) **hereda la unidad del destajo**. Guardarla es lo que permite
detectar la deriva solo: si la unidad vigente del destajo ya no coincide con la
anclada, el sistema lo sabe sin que nadie revise. **Sin anclaje esa deriva es
invisible** — el número sigue siendo válido, solo que ya no significa lo mismo.

> `30 m²/jornada` y `0.0333 jornadas/m²` son el mismo hecho al revés. La segunda es
> la que el APU usa como cantidad; la primera es la que la obra entiende. **Guardar
> una y mostrar la otra**, nunca capturar las dos.

### Cuándo convierte solo y cuándo pide revisión

> **Automático cuando el factor es propiedad del insumo. Revisión cuando depende de
> cómo se usa.**

| Conversión | Factor | Resultado |
|---|---|---|
| Saco → kg | 50 | Del empaque. **Automático** |
| Camión → m³ | 14 | Del transporte. **Automático** |
| m³ de arena → kg | densidad | Del material, varía con la humedad. **Automático con aviso** |
| Tabique pza → m² de muro | aparejo y junta | **De cómo se construye. Revisión** |

Las tres primeras son aritmética; nadie aporta juicio. La última no: cuántas piezas
caben en un metro cuadrado depende del aparejo, que es decisión de obra.

**El agente puede aplicar esta línea solo**, porque es verificable: si la conversión
se queda **dentro de la misma dimensión física** —masa a masa, volumen a volumen,
pieza a pieza— es segura. Si cruza dimensiones o mete una propiedad variable,
propone y espera.

### Y convertir no siempre conserva la verdad

Un excavador rinde distinto en m³ de tierra suelta que de roca. **Misma unidad
nominal, trabajos distintos.** Ahí no hay factor que valga.

> Por eso cambiar la unidad de un insumo con rendimiento enganchado **no es una
> conversión: es una revisión.** El sistema propone el número convertido; alguien
> confirma.

## 6 Corregir el prefijo `AUX-`

Las 79 trabes y mallas llevan prefijo `AUX-` pero son **materiales compuestos**
(`CONOCIMIENTO.md` §10.4). El prefijo nombra una categoría que no tienen.

### No se renombra: se clona

El prefijo **es parte de la clave**, y la clave nunca se reescribe (`CONOCIMIENTO.md` §2.1) — ni antes
de migrar.

> La vía es **clonar y sustituir** (`CONOCIMIENTO.md` §8.4): nace `PRE-00120` con el contenido de
> `AUX-00001`, las referencias se redirigen al clon, y el original queda sin nadie
> apuntándole. Después se decide si se borra (`CONOCIMIENTO.md` §8.5).

### Por qué pesa poco técnicamente

**En este modelo el prefijo no significa nada**: la categoría es `Tipo`, la
naturaleza es `Familia`, y ya quedó escrito tres veces que el prefijo es
nomenclatura y no llave.

> Corregirlo es **cosmético para el sistema y valioso para las personas**. Si se
> decide no hacerlo, **no se rompe nada** — solo queda un nombre que engaña, y por
> eso la advertencia queda escrita en `CONOCIMIENTO.md` §10.4.

### Y falta el viaje de vuelta

Clonar y sustituir resuelve el prefijo dentro del sistema. **No resuelve la salida:**
los demás sistemas siguen conociendo la clave vieja.

Eso lo cubre la tabla de homologación (`CONOCIMIENTO.md` §16.2): entra la clave vieja
y se actualiza; sale la clave vieja hasta que el usuario autorice el cambio, individual
o total.

> **El caso no es sólo `AUX-`.** Un material hidráulico con prefijo sanitario tiene el
> mismo problema, y ahí corregir sí importa: el prefijo engaña sobre la naturaleza.
