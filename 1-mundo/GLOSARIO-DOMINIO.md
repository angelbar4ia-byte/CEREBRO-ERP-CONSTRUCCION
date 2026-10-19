# GLOSARIO DEL DOMINIO

```
órgano:     léxico social
capa:       I — Mundo
pregunta:   ¿cómo lo dicen las personas?
tiempo:     es así
corte:      2026-10-12
verificado: 93 términos · 25 ambigüedades · ejemplos con cifra releídos contra los CSV del repo el 2026-10-12 (uno estaba mal: EST-01010); los de catálogos que no están en el repo —trabajos, mano de obra, fletes— sin releer
```

> **Cómo lo dicen las personas.** Vocabulario del oficio, sinónimos y ambigüedades.
>
> El comportamiento vive en `CONOCIMIENTO.md`; la traducción entre sistemas, en
> `LENGUAJE.md`. Aquí solo qué significa cada palabra.
>
> 93 términos · 25 ambigüedades · 2026-09-21

---

## Cómo leer cada entrada

| Campo | Qué es |
|---|---|
| **También** | Otras formas de decirle lo mismo |
| **No confundir con** | Términos cercanos que NO son lo mismo |
| **Se usa con** | Términos con los que aparece junto |
| **Ejemplo** | Un caso real de los catálogos |
| **Hoy vive en** | Qué archivo o campo lo contiene |

---

## Índice

**Identidad** — Clave · id interno · Clave usuario · Prefijo · Clon

**Clasificación** — Tipo · Categoría · Clase · Familia · Subfamilia · Frente · Especialidad

**El trabajo** — Concepto · Matriz · Matriz dentro de matriz · Concepto auxiliar · Descripción · Descripción corta · Alcance · Unidad

**Los insumos** — Insumo · Material · Compuesto · Auxiliar · Básico de obra · Presentación de compra · Flete · Insumo de etapa

**Mano de obra y trabajos** — Mano de obra · Trabajo · Destajo · Subcontrato · Acarreo · Cuadrilla · %MO · Contratista

**El cálculo** — APU · Cantidad · PU · Importe · Explosión · Reporte de montos · Costo directo · Costo indirecto · Utilidad

**La estructura del presupuesto** — Prototipo · Capítulo · Nivel de construcción · Etapa de construcción · WBS · Índice · Presupuesto · Volumen de obra

**El paramétrico** — Ensamble · Plantilla · Instancia · Divisor · Cohorte

**Tiempo y ejecución** — Rendimiento calculado · Rendimiento teórico · Rendimiento real · Gantt · Actividad · Asignación · Avance · Estimación

**El lugar** — Proyecto · Cluster · Lote · Urbanización · Nivel de casa

**Precios y cambios** — Precio propuesto · Precio pactado · Descuento · Presupuesto Formado · Orden de cambio · Highlight · Orden de trabajo (OT) · Extraordinario · Desviación · Ejecutado sin respaldo

**Operaciones** — Fusión · División · Extracción · Composición · Procedencia


---


## Identidad

### Clave

Identificador único de un registro. Es su identidad ante el negocio: nunca se reescribe, ni siquiera para corregir un prefijo.

- **También:** Código; Clave de concepto; Clave de insumo
- **No confundir con:** `id` interno (ese no se muestra); Clave usuario
- **Se usa con:** Prefijo; Clon; Familia
- **Ejemplo:** ACE-00001, EST-01040, MOCU-005
- **Hoy vive en:** `Columna `Clave` en todos los catálogos`

### id interno

Identificador que genera la base de datos en el INSERT. Nunca se muestra y nunca cambia, ni al mover ni al renumerar. En la estimación el usuario lo llama *oid* y sí viaja en el archivo que sale a revisión, para reconocer sus renglones cuando vuelve (D-516).

- **También:** Identidad interna
- **No confundir con:** Clave; WBS
- **Se usa con:** WBS; Contrato; Estimación
- **Ejemplo:** Lo que un contrato guarda además de la foto del WBS
- **Hoy vive en:** `— aún no existe`

### Clave usuario

Código alterno que captura el usuario, paralelo a la clave del sistema.

- **También:** Código interno; Clave alterna
- **No confundir con:** Clave
- **Se usa con:** Clave
- **Ejemplo:** 39, 40, 169 en el catálogo de trabajos
- **Hoy vive en:** ``Clave usuario` en trabajos`

### Prefijo

Las primeras letras de la clave. Es convención de nomenclatura, NO llave: no se puede deducir de él la familia ni la categoría.

- **También:** Sigla de clave
- **No confundir con:** Familia; Categoría
- **Se usa con:** Clave
- **Ejemplo:** `AUX-` sugiere auxiliar y son materiales; `MOC` es carpintería y ninguna está en Carpintería
- **Hoy vive en:** `Derivado de `Clave``

### Clon

Insumo nuevo creado copiando otro, con clave nueva. Dos modos: mantener el original, o sustituirlo redirigiendo sus referencias.

- **También:** Copia; Variante
- **No confundir con:** Duplicado (ese es un error, no una operación)
- **Se usa con:** Clave; Variante
- **Ejemplo:** Partir de la trabe T-3 para crear la T-4
- **Hoy vive en:** `— aún no existe`


## Clasificación

### Tipo

La categoría del insumo: de qué catálogo sale. Es el campo que dice qué clase de recurso es.

- **También:** Categoría
- **No confundir con:** Clase; Familia; el `Tipo` del presupuesto, que ahí es el rol
- **Se usa con:** Categoría; Familia; Subfamilia
- **Ejemplo:** Material · Trabajo · Mano de Obra · Flete
- **Hoy vive en:** `Columna `Tipo` en los catálogos de insumo`

### Categoría

Los ocho catálogos de insumo. Un insumo puede cambiar de categoría: la arena pasa de Material a Flete.

- **También:** Tipo
- **No confundir con:** Familia; Clase
- **Se usa con:** Tipo; Insumo
- **Ejemplo:** Materiales · Mano de obra · Herramienta · Equipo · Auxiliares · Fletes · Trabajos · Todos
- **Hoy vive en:** `Columna `Tipo``

### Clase

Bajo qué figura se ejecuta un trabajo.

- **También:** Tipo (en el catálogo de trabajos)
- **No confundir con:** Categoría
- **Se usa con:** Trabajo; Destajo; Subcontrato
- **Ejemplo:** Destajo · Subcontrato · Acarreo
- **Hoy vive en:** `Segunda columna `Tipo` en trabajos`

### Familia

Clasificación por naturaleza. Ojo: significa cosas distintas según el catálogo.

- **También:** Grupo; Categoría de material
- **No confundir con:** Categoría; Subfamilia; Frente
- **Se usa con:** Subfamilia; Insumo
- **Ejemplo:** En materiales la sustancia (Aceros); en trabajos el oficio (Albañilería); en mano de obra el rango (Peones)
- **Hoy vive en:** `Columna `Familia``

### Subfamilia

El elemento o la pieza. En trabajos es el elemento que se construye o instala, nunca el calificativo ni la ubicación.

- **También:** Tipo de pieza
- **No confundir con:** Familia
- **Se usa con:** Familia; Elemento
- **Ejemplo:** `MO MURO DE TABIQUE- HILO` → Muro. *Hilo* es cómo se ejecuta
- **Hoy vive en:** `Columna `Subfamilia``

### Frente

Agrupación de conceptos por organización del trabajo en obra, transversal a niveles y etapas.

- **También:** Frente de trabajo; Gremio
- **No confundir con:** Etapa; Especialidad; Familia
- **Se usa con:** Concepto; Cuadrilla; Programa
- **Ejemplo:** Instalaciones · Estructura · Acabados
- **Hoy vive en:** `Catálogo de conceptos-frentes`

*Corregido por D-450, dato del usuario: **frente** es el nivel constructivo de la obra
(Cimentación, Planta baja, Azotea…): las actividades programadas para ejecutar la obra en
ese nivel, con costo y fechas propios. Los **gremios** (Estructura, Instalaciones,
Albañilería…) son sus **sub-frentes**: lo que trabaja dentro de él. No es una zona
física (recámara, sala, fachada). Se lee del árbol del presupuesto —frente = Subcapítulo
(Nivel 1), sub-frente = las etapas (Nivel 2) del frente agrupadas por gremio—; no hay
«catálogo de conceptos-frentes».*

*D-513: ObraCtrl llama «frente» a lo que aquí es un sub-frente (Estructura, Albañilería, Hidrosanitaria, Eléctrica…) y, otras veces, a un nivel (Preliminares, Cimentación, Acabados). Entre los dos manda esta definición.*

*D-451, dato del usuario: **sub-frente = la etapa agrupada por gremio**, confirmado. Lo del
«Catálogo de conceptos-frentes» **no queda resuelto**: la frase anterior («no hay…») iba
de más. Solo se comprobó que ese catálogo no está en este entorno; no se sabe qué trae y
el usuario lo revisará (B-89). Hasta entonces ni se da por inexistente ni por innecesario,
y el «Hoy vive en» de arriba sigue siendo la pista original.*

*D-452, dato del usuario: **no existe el «Catálogo de conceptos-frentes»**; el «Hoy vive en» de
arriba no tenía respaldo. El **frente es por obra** —(obra, nivel), el nodo de Nivel 1 de su
presupuesto— y el **sub-frente es la etapa** (Nivel 2) del frente; agruparlas por gremio es
una forma de leer. Un sub-frente con dos contratistas se divide en uno por contratista.*

*D-453, dato del usuario: el sub-frente es la etapa **sin agrupar por gremio** (las etapas de
instalaciones se quedan separadas; solo Hidráulicas y Sanitarias se fusionarán después en
Hidrosanitarias). El contratista se asigna por obra y tipo de trabajo, de ahí por etapa, salvo
que un concepto se asigne a otro, y se puede dividir hasta la cantidad.*

### Especialidad

Oficio que domina un contratista. Uno puede tener varias.

- **También:** Oficio; Disciplina; Gremio
- **No confundir con:** Frente; Familia
- **Se usa con:** Contratista
- **Ejemplo:** Obra civil · Acabados · Eléctricas · Gas
- **Hoy vive en:** `Catálogo de contratistas`


## El trabajo

### Concepto

Descripción de un trabajo de obra que se puede medir, presupuestar y ejecutar. Unidad básica del catálogo.

- **También:** Actividad; Partida; Ítem; Matriz (por su desglose)
- **No confundir con:** Concepto auxiliar; Ensamble
- **Se usa con:** Descripción; Unidad; Cantidad; APU
- **Ejemplo:** ACA-01010 — Aplanado acabado fino en muros hasta 3.00 m
- **Hoy vive en:** ``CATALOGO_DE_CONCEPTOS``

### Matriz

El desglose de un concepto: sus insumos con cantidad. La matriz es lo que el concepto tiene adentro, no el concepto mismo.

- **También:** Explosión; Desglose; APU
- **No confundir con:** Concepto (la matriz es su contenido)
- **Se usa con:** Concepto; APU; Compuesto
- **Ejemplo:** Doble clic en el PU la abre
- **Hoy vive en:** ``ANALISIS_DE_BASICOS_CONCEPTOS``

### Matriz dentro de matriz

Un concepto dentro de la matriz de otro concepto, con su propia clave y su propio desglose.

- **También:** Anidamiento; Concepto compuesto
- **No confundir con:** Compuesto (ese es un insumo)
- **Se usa con:** Matriz; Concepto
- **Ejemplo:** La losa nervada contiene nervaduras, que contienen varilla
- **Hoy vive en:** `Verificado: llega a 2 niveles`

### Concepto auxiliar

Agrupador por prototipo: condensa varios conceptos con sus cantidades en un solo renglón. Su contenido es derivado: Σ(concepto × cantidad).

- **También:** Agrupador; Nivel 3
- **No confundir con:** Auxiliar (categoría de insumo); Concepto
- **Se usa con:** Concepto; Prototipo; Presupuesto
- **Ejemplo:** EST-01010 Losa cimentación Oro = $138,599.24, la suma exacta de sus 8 conceptos *(decía $132,364.24: ninguna fuente del repo lo da, y las tres que traen la fila dicen $138,599.24)*
- **Hoy vive en:** `Filas `Nivel 3` del presupuesto`

### Descripción

Texto que explica qué es y qué incluye un concepto. Lo describe; no lo identifica.

- **También:** Texto del concepto
- **No confundir con:** Clave (esa sí identifica); Descripción corta
- **Se usa con:** Concepto; Alcance
- **Ejemplo:** «Aplanado acabado fino en muros… Incluye: limpieza, material…»
- **Hoy vive en:** `Columna `Descripción``

### Descripción corta

Versión abreviada, para listados y reportes.

- **También:** Nombre corto
- **No confundir con:** Descripción
- **Se usa con:** Descripción; Concepto
- **Ejemplo:** «LOSA CIMENTACION ORO»
- **Hoy vive en:** ``Descripcion Corta` en el presupuesto`

### Alcance

Lo que el concepto incluye además del trabajo principal: limpieza, acarreos, herramienta, desperdicios.

- **También:** Incluye; Cláusula de alcance
- **No confundir con:** Descripción (el alcance es parte de ella)
- **Se usa con:** Concepto; Descripción
- **Ejemplo:** «Incluye: limpieza, material, mano de obra…» en 408 de 470 *(el CSV del presupuesto da 408 de 471 claves de concepto)*
- **Hoy vive en:** `Cola de la `Descripción``

### Unidad

Cómo se mide un concepto o un insumo. Debe venir del catálogo, no escribirse a mano.

- **También:** Unidad de medida; UM
- **No confundir con:** Presentación de compra
- **Se usa con:** Cantidad; Catálogo de unidades
- **Ejemplo:** M2 · KG · PZ · SAL · JOR · SERV
- **Hoy vive en:** ``Catalogo_de_unidades``


## Los insumos

### Insumo

Todo lo que se consume para ejecutar: material, mano de obra, trabajo, herramienta, equipo, auxiliar o flete.

- **También:** Recurso; Componente
- **No confundir con:** Concepto (el insumo se consume, el concepto se ejecuta)
- **Se usa con:** Categoría; Matriz; Compuesto
- **Ejemplo:** ADH-00006 Estuco saco 40 kg; MOA-00112 MO finas interiores
- **Hoy vive en:** `Los catálogos de insumo`

### Material

Insumo físico que se compra e incorpora a la obra.

- **También:** Suministro
- **No confundir con:** Insumo (material es una categoría de insumo)
- **Se usa con:** Presentación; Unidad; Familia
- **Ejemplo:** ACE-00001 Alambre recocido, KG, $24.68
- **Hoy vive en:** ``CATALOGO_DE_MATERIALES``

### Compuesto

Insumo con desglose propio. Pertenece a una categoría y reporta a ella entero, sin importar qué lleve dentro. Acepta cualquier categoría de hijo.

- **También:** Básico de obra
- **No confundir con:** Auxiliar (ese ES una categoría); Concepto
- **Se usa con:** Básico de obra; Matriz; Categoría
- **Ejemplo:** Un tabique que fabricas tú: lleva arena, cemento y mano de obra, y reporta 100% como material
- **Hoy vive en:** `Columna `C` = `+``

### Auxiliar

Una de las ocho categorías de insumo. A diferencia del compuesto, no depende de otra categoría: reporta a sí mismo.

- **También:** Básico de obra
- **No confundir con:** Compuesto; el prefijo `AUX-`, que NO indica esta categoría
- **Se usa con:** Compuesto; Categoría
- **Ejemplo:** **Hoy el catálogo está vacío.** Las claves `AUX-` son materiales compuestos
- **Hoy vive en:** `— sin uso`

### Básico de obra

Término que agrupa a compuestos y auxiliares: todo lo que dentro de una matriz se abre.

- **También:** Compuesto; Auxiliar
- **No confundir con:** Insumo sencillo (no se abre)
- **Se usa con:** Matriz; Compuesto; Auxiliar
- **Ejemplo:** Una trabe AUX-00001 y una mezcla MEZ-03010
- **Hoy vive en:** ``Catalogo` de materiales, con `C` = `+``

### Presentación de compra

La forma comercial en que se compra un material, con su factor y su mínimo. Cambiarla no cambia el material.

- **También:** Empaque; Formato de compra
- **No confundir con:** Unidad (la de medida)
- **Se usa con:** Material; Unidad; Factor
- **Ejemplo:** Arena: se consume en m³, se compra por camión de 14 m³
- **Hoy vive en:** `PRESENTACION_COMPRA` — `MODELO.md` §2a, D-348

### Flete

Categoría de insumo: el transporte del material a la obra.

- **También:** Acarreo (por definir la frontera)
- **No confundir con:** Acarreo, que es clase de trabajo
- **Se usa con:** Material; Acarreo
- **Ejemplo:** PET-00002 Arena 7 M3, SERV, $2,250
- **Hoy vive en:** ``CATALOGO_DE_FLETES``

### Insumo de etapa

Material o trabajo colgado directamente de una etapa, sin pasar por un concepto. Es intencional.

- **También:** Cargo de etapa
- **No confundir con:** Costo indirecto
- **Se usa con:** Etapa de construcción; Insumo
- **Ejemplo:** No atribuible a una partida concreta
- **Hoy vive en:** `Válido en el árbol`


## Mano de obra y trabajos

### Mano de obra

Categoría de insumo: el trabajo humano por jornada.

- **También:** MO; Jornal
- **No confundir con:** Trabajo (ese se paga por unidad de obra); Cuadrilla
- **Se usa con:** Cuadrilla; Jornal; Destajo
- **Ejemplo:** MOCA-014 Albañil, JOR, $760
- **Hoy vive en:** ``CATALOGO_DE_MANO_DE_OBRA``

### Trabajo

Categoría de insumo: mano de obra pagada por unidad de obra terminada. OPUS también lo llama Contrato.

- **También:** Contrato; Destajo
- **No confundir con:** Mano de obra (esa va por jornada)
- **Se usa con:** Destajo; Subcontrato; Acarreo
- **Ejemplo:** MOA-00112 MO finas interiores, $50 por M2
- **Hoy vive en:** ``CATALOGO_DE_TRABAJOS``

### Destajo

Clase de trabajo: se paga por unidad producida, no por jornada.

- **También:** Precio a destajo; Ajuste; Trato
- **No confundir con:** Jornal; Subcontrato
- **Se usa con:** Trabajo; Cuadrilla; Rendimiento
- **Ejemplo:** 259 de los 265 trabajos
- **Hoy vive en:** ``Tipo` = Destajo`

### Subcontrato

Clase de trabajo: se contrata completo a un tercero. Su precio incluye material y utilidad, no solo mano de obra. Al asignarse a un contratista se formaliza con una Orden de trabajo (OT), un contrato informal (D-511).

- **También:** Contrato a terceros
- **No confundir con:** Destajo; Contratista
- **Se usa con:** Trabajo; Contratista; Alzado; Orden de trabajo (OT)
- **Ejemplo:** Cuatro de los seis valen $1.00: son precio alzado
- **Hoy vive en:** ``Tipo` = Subcontrato`

### Acarreo

Clase de trabajo: mover material dentro de la obra. **Hoy sin renglones.**

- **No confundir con:** Flete, que es traerlo de fuera
- **Se usa con:** Trabajo; Flete
- **Ejemplo:** — sin uso
- **Hoy vive en:** ``Tipo` = Acarreo`

### Cuadrilla

Conjunto de personas que ejecuta un trabajo. Modelo de CAPACIDAD —cuánto tarda y con cuánta gente—, no de costo.

- **También:** Brigada; Equipo de trabajo
- **No confundir con:** Destajo (ese es el costo)
- **Se usa con:** Rendimiento; Destajo; Frente; Gantt
- **Ejemplo:** MOCU-002 (1 Albañil + 1 Peón) = $1,452/jornada
- **Hoy vive en:** ``C` = `+` en mano de obra`

### %MO

Unidad que indica un porcentaje sobre la suma de los jornales de esa cuadrilla. Nombra la base, no la naturaleza de la línea.

- **También:** Porcentaje sobre mano de obra
- **No confundir con:** Que la línea sea mano de obra: el Contratista no lo es
- **Se usa con:** Cuadrilla; Unidad
- **Ejemplo:** Contratista 0.1 %MO sobre $1,880 = $188
- **Hoy vive en:** `Unidad en mano de obra`

### Contratista

Persona o empresa que ejecuta trabajos, con su tabulador de precios propio. Se categoriza por **tipo** (destajo, subcontrato o los dos) y por **oficio** (la `Familia` del trabajo), y puede llevar una **retención** de 5 % por defecto, editable por contratista. No lleva clave, solo el id. (D-512 a D-521.)

- **También:** Ejecutor; Proveedor de mano de obra
- **No confundir con:** Subcontrato (ese es el trabajo, no quién lo hace)
- **Se usa con:** Subcontrato; Especialidad; Precio pactado
- **Ejemplo:** FRE-00005 Eduardo Andrade
- **Hoy vive en:** ``CATALOGO_DE_CONTRATISTAS``; en el modelo, `CONTRATISTA` con su tipo y sus oficios (`MODELO.md` §4a, firme desde D-521)


## El cálculo

### APU

Análisis de Precio Unitario. La explosión de un concepto en sus insumos con su cantidad, de donde sale el precio unitario.

- **También:** Análisis; Matriz; Explosión de insumos; Tarjeta
- **No confundir con:** PU (ese es el resultado)
- **Se usa con:** Concepto; Insumo; Cantidad; PU
- **Ejemplo:** ACA-01010 = mortero 1.05 M2 + MO 1 M2 = $71.71
- **Hoy vive en:** ``ANALISIS_DE_BASICOS_CONCEPTOS``

### Cantidad

Cuánto se consume. Significa cosas distintas según dónde esté.

- **También:** Consumo; Coeficiente; Rendimiento de matriz (alias en fórmulas del paramétrico — D-217)
- **No confundir con:** Volumen de obra; Rendimiento (de cuadrilla, en `§Tiempo y ejecución`)
- **Se usa con:** APU; Insumo; Volumen
- **Ejemplo:** 0.13125 PZ de estuco por m² de aplanado
- **Hoy vive en:** `Columna `Cantidad``

### PU

Precio unitario: lo que cuesta una unidad del concepto. Es el RESULTADO del APU.

- **También:** Precio unitario; P.U.
- **No confundir con:** APU (ese es el análisis); Importe
- **Se usa con:** APU; Importe; Costo directo
- **Ejemplo:** $71.71 por m² de ACA-01010
- **Hoy vive en:** ``Precio unitario` en el presupuesto`

### Importe

Cantidad × precio unitario. El monto de una línea.

- **También:** Monto; Total de línea; Parcial
- **No confundir con:** PU (ese es por unidad)
- **Se usa con:** PU; Cantidad
- **Ejemplo:** $1,952.79 = 79.124 KG × $24.68
- **Hoy vive en:** `Columna `Importe``

### Explosión

Recorrer el árbol hasta el fondo conservando la naturaleza de cada hoja. Es la prueba de ADN de la matriz.

- **También:** Explosión de insumos
- **No confundir con:** Reporte de montos, que se detiene en el compuesto
- **Se usa con:** Matriz; Compuesto; Almacén
- **Ejemplo:** Sirve para saber qué se compra y qué se contrata
- **Hoy vive en:** `Lectura del árbol`

### Reporte de montos

Recorrer el árbol sumando a la categoría de cada compuesto, sin abrirlo. El básico más externo absorbe todo.

- **También:** Costo por categoría
- **No confundir con:** Explosión
- **Se usa con:** Compuesto; Categoría
- **Ejemplo:** ZA1-000001 es 41% mano de obra y reporta 100% como material
- **Hoy vive en:** `Lectura del árbol`

### Costo directo

Suma de material, mano de obra, trabajo, flete y equipo. Es lo único que traen los datos actuales.

- **También:** CD
- **No confundir con:** Precio de venta; Costo indirecto
- **Se usa con:** APU; PU; Sobrecosto
- **Ejemplo:** El PU del concepto = suma de sus componentes
- **Hoy vive en:** `Verificado en 467 conceptos`

### Costo indirecto

Gastos no atribuibles a un concepto: administración, oficina, supervisión. Capa sobre el costo directo.

- **También:** Indirectos; Cargos indirectos
- **No confundir con:** Costo directo; Insumo de etapa
- **Se usa con:** Sobrecosto; Utilidad
- **Ejemplo:** — no aparece en ningún archivo
- **Hoy vive en:** `— pendiente`

### Utilidad

Margen del constructor, aplicado como capa. La base sobre la que se calcula cambia según el país.

- **También:** Margen; Ganancia
- **No confundir con:** Costo indirecto
- **Se usa con:** Sobrecosto; Costo directo
- **Ejemplo:** En México va sobre directo + indirectos + financiamiento
- **Hoy vive en:** `— pendiente`


## La estructura del presupuesto

### Prototipo

Modelo de vivienda que se repite. Cada uno con su presupuesto completo. Los m² son del prototipo; una casa es un prototipo con o sin modificaciones y con o sin m² adicionales (D-512).

- **También:** Modelo; Tipo de casa
- **No confundir con:** Frente; Nivel
- **Se usa con:** Presupuesto; Nivel de construcción
- **Ejemplo:** CAS-00004 Zafiro 1.0 (172 m²)
- **Hoy vive en:** `Filas `Capítulo` del presupuesto`

### Capítulo

El nivel más alto del presupuesto. En esta empresa se usa para el prototipo, pero puede ser cualquier agrupación.

- **También:** Prototipo (aquí)
- **No confundir con:** Prototipo como regla del modelo
- **Se usa con:** Presupuesto; WBS
- **Ejemplo:** Los 7 prototipos
- **Hoy vive en:** ``Tipo` = Capítulo`

### Nivel de construcción

División del presupuesto bajo el capítulo: mezcla pisos, zonas y oficios (Cimentación, Planta baja, Azotea, Acabados, Cancelería…). El usuario la llama *nivel de presupuesto* y en el cerebro es el frente (D-450). No es el nivel de casa (D-512).

- **También:** Subcapítulo; Zona; Nivel de presupuesto
- **No confundir con:** Nivel 2 / Nivel 3, que son profundidad; Nivel de casa
- **Se usa con:** Etapa de construcción; Prototipo
- **Ejemplo:** NIV-00001 Cimentación
- **Hoy vive en:** ``Nivel ERP` + filas `Subcapítulo``

### Etapa de construcción

División del trabajo por fase o especialidad dentro de un nivel.

- **También:** Etapa; Fase; Nivel 2
- **No confundir con:** Frente
- **Se usa con:** Nivel de construcción; Concepto
- **Ejemplo:** ECO-00001 Estructura CIM. Son 52
- **Hoy vive en:** `Filas `Nivel 2``

### WBS

Ruta jerárquica que ubica cada renglón en el árbol. Se calcula por posición y se separa con puntos.

- **También:** Estructura de desglose; Ruta
- **No confundir con:** Índice; `id` interno
- **Se usa con:** Prototipo; Nivel; Etapa
- **Ejemplo:** 1.100.01.1523.01
- **Hoy vive en:** `— se calcula, no se importa`

### Índice

Número de orden de un renglón dentro de su padre.

- **También:** Orden; Consecutivo
- **No confundir con:** WBS; Clave
- **Se usa con:** WBS; Presupuesto
- **Ejemplo:** `Indice` 1, 2, 3 dentro de cada etapa
- **Hoy vive en:** `Columna `Indice``

### Presupuesto

El árbol completo de un prototipo u obra con cantidades y precios.

- **También:** Catálogo de conceptos; Catálogo de obra
- **No confundir con:** El catálogo de conceptos como vocabulario
- **Se usa con:** Prototipo; Concepto; Volumen
- **Ejemplo:** $16,460,623.50 en los 7 prototipos
- **Hoy vive en:** ``CATALOGO_DE_PRESUPUESTO``

### Volumen de obra

Cuánta obra hay que ejecutar de un concepto. Multiplica al PU.

- **También:** Cantidad de obra; Cómputo métrico
- **No confundir con:** Cantidad del APU
- **Se usa con:** Cantidad; Presupuesto; Importe
- **Ejemplo:** 279 m² de muro de tabique
- **Hoy vive en:** ``Cantidad` en el presupuesto`


## El paramétrico

### Ensamble

Agrupación de conceptos con cantidad propia, un piso arriba del APU. Su cantidad es receta, no volumen.

- **También:** Paramétrico; Módulo
- **No confundir con:** Concepto auxiliar; Concepto compuesto
- **Se usa con:** Plantilla; Instancia; Divisor
- **Ejemplo:** Recámara tipo A: 1 regadera aunque el presupuesto tenga 3
- **Hoy vive en:** `— aún no existe`

### Plantilla

La receta. No se contrata ni se programa porque no está pegada a ninguna obra.

- **También:** Tipo; Modelo
- **No confundir con:** Instancia
- **Se usa con:** Ensamble; Instancia
- **Ejemplo:** *Recámara tipo A*
- **Hoy vive en:** `— aún no existe`

### Instancia

La plantilla aplicada, con cantidades reales dentro de un presupuesto. Sí se contrata y se programa.

- **También:** Aplicación
- **No confundir con:** Plantilla
- **Se usa con:** Ensamble; Plantilla
- **Ejemplo:** *Recámara 1 del lote 14*
- **Hoy vive en:** `— aún no existe`

### Divisor

El parámetro por el que se divide un ensamble para obtener su tasa.

- **También:** Parámetro
- **No confundir con:** Cantidad
- **Se usa con:** Ensamble; Cohorte
- **Ejemplo:** 1 recámara; m² de losa
- **Hoy vive en:** `— aún no existe`

### Cohorte

A qué casos aplica un paramétrico. Fuera de ella, no se usa.

- **También:** Criterio de aplicabilidad
- **No confundir con:** Familia
- **Se usa con:** Ensamble; Divisor
- **Ejemplo:** Cimentación de 1 planta: 2% de dispersión. Mezclada con 2 plantas: 23%
- **Hoy vive en:** `— aún no existe`


## Tiempo y ejecución

### Rendimiento calculado

Costo de la cuadrilla ÷ precio del destajo. Nunca se captura: siempre existe.

- **También:** Rendimiento del enganche
- **No confundir con:** Rendimiento teórico
- **Se usa con:** Cuadrilla; Destajo; Gantt
- **Ejemplo:** $1,452 ÷ $50/m² = 29.04 m² por jornada
- **Hoy vive en:** `— se calcula`

### Rendimiento teórico

El rendimiento que se supone al presupuestar. Se captura.

- **También:** Rendimiento de proyecto
- **No confundir con:** Rendimiento calculado; Rendimiento real
- **Se usa con:** Cuadrilla; Destajo
- **Ejemplo:** 18.53 m²/jornada para repellado de muro
- **Hoy vive en:** `Semilla, 265 filas`

### Rendimiento real

El medido en obra. Comparado con el teórico, mide desviación de productividad.

- **También:** Rendimiento de campo
- **No confundir con:** Rendimiento teórico
- **Se usa con:** Rendimiento; Control de obra
- **Ejemplo:** — aún sin capturar
- **Hoy vive en:** `— pendiente`

### Gantt

Programa de obra. No se dibuja: se calcula desde el volumen, el rendimiento y el número de cuadrillas.

- **También:** Programa de obra; Cronograma
- **No confundir con:** Ruta crítica (CPM)
- **Se usa con:** Rendimiento; Cuadrilla; Volumen
- **Ejemplo:** duración = volumen ÷ (rendimiento × cuadrillas)
- **Hoy vive en:** `— pendiente`

### Actividad

Agrupación de conceptos en el programa, con cantidad y unidad propias. El programa reagrupa; no reasigna.

- **También:** Tarea
- **No confundir con:** Concepto; Etapa
- **Se usa con:** Frente; Asignación; Avance
- **Ejemplo:** — aún no existe
- **Hoy vive en:** `— pendiente`

### Asignación

La relación entre una actividad y un concepto, con su cantidad. Es la unidad de trabajo del programa.

- **No confundir con:** Concepto
- **Se usa con:** Actividad; Avance
- **Ejemplo:** 1 de las 3 regaderas
- **Hoy vive en:** `— pendiente`

### Avance

Porcentaje o volumen ejecutado. Alimenta el Gantt y la estimación.

- **También:** Progreso; Ejecutado
- **No confundir con:** Rendimiento
- **Se usa con:** Estimación; Gantt; Asignación
- **Ejemplo:** — aún no modelado
- **Hoy vive en:** `— pendiente`

### Estimación

Documento que cobra el avance ejecutado en un periodo. Es **un solo documento que avanza:** el residente la crea en Excel, Control de obra la concentra y la envía a Compras, Compras revisa los topes y la devuelve a todos, el residente tiene oportunidad de réplica si alguna cantidad bajó, Costos y Control de obra regresan a Compras las justificaciones de por qué debe subir la cantidad, Compras la modifica (esa es la que se paga) y se la envía a Control de obra, que establece la estimación pagada (D-522 y D-538; es el proceso de hoy y se irá puliendo con el sistema).

- **También:** Valuación; Corte; Generador
- **No confundir con:** Presupuesto (eso es lo planeado)
- **Se usa con:** Avance; Presupuesto; Contratista
- **Ejemplo:** — aún no modelado
- **Hoy vive en:** `CONOCIMIENTO.md` §13.8


## Precios y cambios

### Precio propuesto

Lo que pide el contratista antes de negociar.

- **También:** Cotización
- **No confundir con:** Precio pactado; PU
- **Se usa con:** Precio pactado; Contratista
- **Ejemplo:** $55 cuando el PU es $50
- **Hoy vive en:** `— pendiente`

### Precio pactado

Lo acordado con un contratista concreto. No toca el catálogo.

- **También:** Precio de contrato
- **No confundir con:** PU; Precio propuesto
- **Se usa con:** Contratista; Descuento
- **Ejemplo:** $52: ni el PU ni lo que se pedía
- **Hoy vive en:** `— pendiente`

### Descuento

Deducción sobre un pago ya hecho, para que el costo efectivo respete el PU. Antes de pagar no hay descuento: hay renegociación. **Hay una segunda familia, de calidad y cumplimiento** (trabajo mal hecho, no terminado, abandonado, que afectó otros trabajos, o que pagó otro contratista), que no tiene que ver con el precio (D-509). **Puede ir a una OT o directo al contratista** (D-519): si el trabajo de una OT ya pagada lo repara otro, el descuento va solo al contratista que lo hizo mal y no baja esa OT.

- **También:** Deducción
- **No confundir con:** Renegociación
- **Se usa con:** Precio pactado; Estimación
- **Ejemplo:** Cobró a $55, se le deduce $5
- **Hoy vive en:** `DEDUCCION` (`MODELO.md` §5d): diez tipos desde D-544 —los siete de calidad y cumplimiento, más monto mal capturado y cantidad mal capturada—, que se cobran de las estimaciones del contratista y, si se define así, en parcialidades

### Presupuesto Formado

El catálogo reconstruido a cantidad real (Paso 1), explotado con el mismo
rendimiento (matriz) que usa el presupuesto base. Aísla si el excedente es por
construir más (efecto cantidad) o por usar distinto rendimiento (efecto receta).

- **También:** Presupuesto reformado (variante hablada — no canónica, se resuelve igual)
- **No confundir con:** Presupuesto Base; Ingeniería; Control de Cambio
- **Se usa con:** Efecto cantidad; Efecto receta; Concepto auxiliar
- **Ejemplo:** 244 m² reales de losa, explotados con el rendimiento del catálogo base
- **Hoy vive en:** `CONOCIMIENTO.md` §11.14

### Orden de cambio

Documento que referencia un nodo congelado y propone un delta. No edita: agrega. Puede nacer de un extra interno de la obra (D-515).

- **También:** Control de cambio
- **No confundir con:** Desviación
- **Se usa con:** Contrato; Causa; Autorización
- **Ejemplo:** Con causa, impacto y si se autorizó antes o después de ejecutar
- **Hoy vive en:** `PROPUESTA(tipo=orden_cambio)` — `MODELO.md` §5f, D-334

### Highlight

Estimado que se le entrega al cliente cuando pide modificar el alcance o rediseñar los subcontratos de su presupuesto. Se hace antes de ejecutar y se folia; al aprobarse se vuelve control de cambio.

- **También:** —
- **No confundir con:** Adicional al presupuesto (ese ya está en ejecución); Cotización del contratista (esa es la que sigue)
- **Se usa con:** Orden de cambio; Orden de trabajo (OT); Cotizador
- **Ejemplo:** El cliente rediseña el pergolado de la cochera: se le cotiza el cambio (highlight) y, con la cotización del contratista, nace la OT
- **Hoy vive en:** `MODELO.md` §5b (Cotizador), D-280; la app de extraordinarios no lo registra

### Orden de trabajo (OT)

El contrato informal con un contratista para ejecutar un subcontrato. Se contrata **después de la venta al cliente**, a partir de un presupuesto o de un control de cambio, y cubre la vida del subcontrato desde ahí: pagos, descuentos, reasignaciones, cambios de alcance y cancelación. (D-511.)

- **También:** OT. En D-509 y D-510 se le llamó «extraordinario por subcontrato»; el usuario aclaró que el nombre correcto es **subcontrato** (D-511)
- **No confundir con:** Orden de cambio (esa es con el cliente, esta con el contratista); Subcontrato (la clase de trabajo en el presupuesto, que la OT contrata); Extraordinario
- **Se usa con:** Subcontrato; Contratista; Asignación; Highlight; Cotización
- **Ejemplo:** *(sin ejemplo con cifra: no se han visto los datos de la app)*
- **Hoy vive en:** la tabla `ots` de la app de extraordinarios, con un campo de tipo de contrato que mezcla origen, forma de pago y estado (`LENGUAJE.md`); no está en el modelo del cerebro

### SOV (Schedule of Values)

En la construcción de habla inglesa, el desglose de un trabajo o de un contrato en partidas cobrables, cada una con su valor; sirve de base para revisar los avances y los pagos (en los contratos AIA se carga en la hoja G703 de la solicitud de pago). No es el presupuesto interno de la empresa. **En esta empresa** (D-555) es el desglose con que Atención a postventa solicita los recursos y los insumos de un trabajo y saca su costo: lo que se le cobra al cliente o lo que le va a costar a la empresa una garantía. Se hace después de dictaminar y antes de programar la ejecución: lo otorga el sistema, lo llena Atención a postventa (una compostura) o el residente (un ajuste de obra: mejora, omisión de proyecto o de costos, error de ejecución), lo evalúa y confirma Control de obra (en un cambio en obra, también Costos) y Compras cotiza con proveedores y compra el material. (D-553 a D-558.)

- **También:** desglose de valores *(traducción mía)*; en las siglas del usuario, «SOV»
- **No confundir con:** el presupuesto de la obra; la cotización al cliente (el SOV es de uso interno y puede acabar en una)
- **Se usa con:** Orden de trabajo (OT); Estimación; Postventa
- **Ejemplo:** tras dictaminar que una fuga no está en garantía, Atención a postventa parte la compostura en renglones con su valor, de ahí sale lo que se le cobra al cliente y se piden los insumos
- **Hoy vive en:** nada propio. *Lectura mía:* los renglones de la cotización de la OT (`PARTIDA_COTIZACION`, `MODELO.md` §5i); el desglose de lo que cuesta la garantía lo confirma el usuario

### Extraordinario

Lo que queda **fuera del presupuesto**: no estaba en lo contratado con el cliente. Es la palabra del oficio para lo que entra después del contrato, con número nuevo al final y sin renumerar nada (`CONOCIMIENTO.md` §1.4). El usuario dice que es el calificativo más cercano, pero que lo que maneja su app se llama **subcontrato** (D-511).

- **También:** Fuera del presupuesto
- **No confundir con:** Subcontrato (aquel puede ser base o extraordinario); Adicional al presupuesto (el cerebro no ha decidido si son sinónimos)
- **Se usa con:** Orden de cambio; Highlight; Orden de trabajo (OT)
- **Ejemplo:** El cliente agrega un cambio de acabados que no estaba en lo vendido
- **Hoy vive en:** `CONOCIMIENTO.md` §1.4 (conceptos extraordinarios); el nombre de la app de extraordinarios

### Desviación

La misma obra a otro precio o consumo. Se descompone en desviación de precio y de consumo.

- **También:** Variación
- **No confundir con:** Cambio de alcance (ese se cobra)
- **Se usa con:** Causa; Almacén; Explosión
- **Ejemplo:** Se absorbe; el cambio de alcance se factura
- **Hoy vive en:** `DESVIACION` — `MODELO.md` §5g, D-343

### Ejecutado sin respaldo

Obra registrada sin presupuesto aprobado. Es una deuda medible, con antigüedad.

- **No confundir con:** Desviación
- **Se usa con:** Orden de cambio; Registro
- **Ejemplo:** Dos destinos: orden de cambio, o pérdida
- **Hoy vive en:** `— pendiente`


## El lugar

### Proyecto

El desarrollo completo: agrupa clústeres y una urbanización. Hoy hay dos: Magnolia y «Antigua», un proyecto viejo al que le quedan una o muy pocas obras por cerrar. (D-512 y D-516.)

- **También:** Desarrollo
- **No confundir con:** Lote (una casa); Prototipo; Presupuesto
- **Se usa con:** Cluster; Urbanización; Lote
- **Ejemplo:** Magnolia; «Antigua»
- **Hoy vive en:** `proyectos` del concentrador (2), `proyecto` en auditoría y en ObraCtrl; el modelo del cerebro aún no lo tiene (`MODELO.md` §3c, firme desde D-521)

### Cluster

Agrupación de lotes dentro del proyecto. Magnolia tiene siete. Su nombre forma parte de la clave de la casa. En «Antigua» esa agrupación se llama **manzana** y la clave es manzana y lote («10-04»). (D-512 y D-520.)

- **También:** Clúster
- **No confundir con:** Proyecto; Frente
- **Se usa con:** Proyecto; Lote; Control de cambio
- **Ejemplo:** Acacia, Alamo, Fresno, Maple, Olivo, Olmo y Tabachín (los siete que aparecen en el avance del ERP, lectura mía); en «Antigua», la manzana 10
- **Hoy vive en:** dentro del texto del lote («FRESNO 12»); `cluster` en auditoría y en ObraCtrl; la sigla (`ALM`) en la clave de un control de cambio, que sirve para formarla y para reconocer a qué obra corresponde

### Lote

La casa y, a la vez, la obra: cada lote es una obra y se identifica por clúster y número de lote. Es un prototipo con o sin modificaciones, con o sin m² adicionales. (D-512.)

- **También:** Obra; Casa
- **No confundir con:** Prototipo (el modelo que se repite); Urbanización
- **Se usa con:** Cluster; Prototipo; Presupuesto
- **Ejemplo:** FRESNO 12; ALAMO 18; 10-04 (manzana 10, lote 4, en «Antigua»)
- **Hoy vive en:** la columna `Lote` del almacén y de las estimaciones (texto suelto: 114 valores distintos en el concentrador); `PRESUPUESTO` de tipo obra en el modelo (`MODELO.md` §3c, firme desde D-521)
- **Estatus:** pendiente (en planeación o próxima a construir), iniciada, en proceso, por entregar (desde el 90 % de avance, hasta que el cliente la recibe) y entregada, como en ObraCtrl (D-514)

### Colono

El dueño de la casa, que es el cliente. Es quien abre un ticket de postventa y quien confirma su cierre con un nivel de satisfacción; más adelante será el usuario del módulo de vivienda. (D-541.)

- **También:** Cliente; Dueño de la casa
- **No confundir con:** Contratista; Residente (empleados de la empresa)
- **Se usa con:** Lote; Postventa; Control de cambio
- **Ejemplo:** el dueño de FRESNO 12 abre un ticket por humedad en la azotea
- **Hoy vive en:** la idea del módulo de vivienda (B-125); en el modelo, el rol `colono` (confirmado en D-542) y las funciones `abrir_ticket_garantia` y `confirmar_cierre_ticket` (`MODELO.md` §3b y §5b)

### Ticket de postventa

El pedido de un colono después de entregada la casa: reporta un problema, solicita un servicio o solicita un mantenimiento. Atención a postventa le da seguimiento, programa una visita, dictamina si la garantía es válida, hace un SOV y programa la ejecución; se cierra a solicitud de Atención a postventa, con la confirmación y el nivel de satisfacción del colono (de 5 a 10). (D-541 a D-562.)

- **También:** ticket de garantía (el nombre anterior)
- **No confundir con:** Orden de trabajo (el ticket puede llegar a una OT, o resolverse sin ella)
- **Se usa con:** Colono; Garantía; SOV; Cuadrilla
- **Ejemplo:** el dueño de FRESNO 12 reporta humedad en la azotea
- **Hoy vive en:** `TICKET_POSTVENTA` y `VISITA_POSTVENTA` (`MODELO.md` §3b); propuesta, nada construido (D-487)

### Garantía

Dice dos cosas. **La de la vivienda** dura **un año desde la entrega, para todos;** no es válida si venció o si el problema fue provocado, y cuando es válida no se cobra al cliente. **La del contratista** es su retención (5 % normalmente): el pago de tipo `garantia` es su devolución. (D-518, D-554 y D-556.)

- **También:** retención por garantías (la del contratista)
- **No confundir con:** Postventa (el proceso); una OT de postventa cobrada al cliente
- **Se usa con:** Ticket de postventa; Retención; Contratista
- **Ejemplo:** una fuga reportada a los 14 meses de la entrega no es de garantía; se le ofrece la compostura con costo al cliente
- **Hoy vive en:** `PARAMETRO` `plazo_garantia_meses` y `VISITA_POSTVENTA.dictamen` (`MODELO.md` §3b y §5j); `RETENCION` (§5d); propuesta, nada construido

### Espacio

Una rama de la casa en el árbol del presupuesto: una recámara, la cocina, un baño. El tronco es la casa; las subramas del espacio son los niveles y las etapas de construcción, y las hojas, los conceptos o las matrices. Su área en m² es lo único que se captura a mano. Sirve para que una casa crezca por módulos, sin tocar el resto. (D-564 a D-566.)

- **También:** área; módulo de crecimiento
- **No confundir con:** Nivel de casa (planta baja, planta alta); Frente (el nivel constructivo del programa)
- **Se usa con:** Control de cambio; Paramétrico; Ampliación
- **Ejemplo:** el cliente crece una recámara 10 m²: cambian solo el precio y los conceptos de esa recámara
- **Hoy vive en:** nada propio: reutiliza el árbol, el cuantificador y `ENSAMBLE_PARAMETRO` (`MODELO.md` §3c); propuesta, nada construido

### Parámetro del negocio

Un valor que cambia con el tiempo y que no debe vivir en el código: el factor 0.7, los 17,000 pesos por m² de lista, el plazo de un año de la garantía, los 20 días de las re-solicitudes. Lo cambia Control de obra, y el que vale es el de la fecha del hecho. (D-563.)

- **No confundir con:** el parámetro de un ensamble paramétrico (`ENSAMBLE_PARAMETRO`: una tasa de pesos por m², por pieza o por salida)
- **Se usa con:** Control de obra; Garantía; Descuento
- **Ejemplo:** `factor_precio` = 0.7, vigente desde el 2026-10-12
- **Hoy vive en:** `PARAMETRO` (`MODELO.md` §5j); propuesta, nada construido

### Urbanización

La obra única del proyecto, que sirve a todos los clústeres y a las amenidades. Hay una sola por proyecto y sus ramas son los clústeres y las amenidades. (D-512.)

- **También:** URBA, que es como se llama su hoja en las estimaciones
- **No confundir con:** Lote (la obra de una casa)
- **Se usa con:** Proyecto; Cluster
- **Ejemplo:** La urbanización de Magnolia
- **Hoy vive en:** la hoja URBA de las estimaciones; en el modelo, un `PRESUPUESTO` de tipo obra con `proyecto_id` (`MODELO.md` §3c, firme desde D-521)

### Nivel de casa

Cada piso de la vivienda: planta baja, planta alta y la azotea, que es roof garden cuando el cliente lo pide. No es el nivel del presupuesto. El roof garden no cuenta como planta. (D-512 y D-514.)

- **También:** Planta; Piso; Roof garden (que el catálogo escribe «Azotea» o «Azotea/Roof»)
- **No confundir con:** Nivel de construcción (el del presupuesto, que es el frente); Nivel 2 y Nivel 3 (profundidad)
- **Se usa con:** Prototipo; Nivel de construcción
- **Ejemplo:** Castillo K1 (`EST-02110`) se ejecuta en planta baja, planta alta y azotea/roof
- **Hoy vive en:** `Nivel OP` del avance (las órdenes de producción); `PRESUPUESTO.plantas` cuenta planta baja y planta alta

---

## Operaciones

### Fusión

Varios destajos se vuelven uno. El precio se propone ponderado por cantidad.

- **No confundir con:** División
- **Se usa con:** Destajo; Ponderado
- **Ejemplo:** Salida hidráulica + sanitaria = hidro-sanitaria
- **Hoy vive en:** `— pendiente`

*D-460: también se fusionan etapas —Hidráulicas y Sanitarias en «Instalaciones hidrosanitarias» por nivel—, con la misma regla: convive con las originales (`CATALOGOS.md`).*

### División

Un concepto con varios destajos se vuelve varios conceptos.

- **No confundir con:** Fusión
- **Se usa con:** Concepto; Destajo
- **Ejemplo:** Quien divide decide qué hacer con lo que no tiene dueño
- **Hoy vive en:** `— pendiente`

### Extracción

Materiales sin destajo se vuelven concepto propio, con clave nueva.

- **No confundir con:** Composición
- **Se usa con:** Concepto; Material
- **Ejemplo:** El insumo no se transforma: vive dentro de la matriz de algo nuevo
- **Hoy vive en:** `— pendiente`

### Composición

Varios conceptos se vuelven un concepto nuevo, con clave nueva.

- **No confundir con:** Ensamble (ese no crea clave)
- **Se usa con:** Concepto; Matriz
- **Ejemplo:** Su inversa es la explosión
- **Hoy vive en:** `— pendiente`

### Procedencia

Qué creó un renglón: importado, manual, o alguna de las operaciones.

- **También:** Origen (nombre retirado)
- **No confundir con:** Categoría
- **Se usa con:** Rediseño; Capas
- **Ejemplo:** Es lo único que distingue lo cargado de lo rediseñado
- **Hoy vive en:** `MODELO.md` §1 · `NODO.procedencia` — aprobado 2026-09-10


---

## Términos ambiguos

Una misma palabra con varios significados. **El glosario los expone; resolverlos
es decisión, no vocabulario.**


### «Nivel» — 3 significados

| Significado | Dónde aparece | Cómo se distingue |
|---|---|---|
| División física de la obra: planta baja, azotea | ``CATALOGO_DE_NIVELES`, `Nivel ERP`` | Es un lugar de la casa |
| Profundidad en el árbol: Nivel 2, Nivel 3 | `Columna `Tipo` del presupuesto` | Es la posición jerárquica |
| Altura de ejecución: 0-3.00 m, +3.00 m | `Descripciones de conceptos y destajos` | Es una condición de trabajo |

### «Cantidad» — 3 significados

| Significado | Dónde aparece | Cómo se distingue |
|---|---|---|
| Consumo de insumo por unidad de concepto | ``ANALISIS_DE_BASICOS_*`` | 0.13125 PZ de estuco por m² |
| Volumen de obra a ejecutar | ``CATALOGO_DE_PRESUPUESTO`` | 279 m² de muro |
| Receta del ensamble, alias **rendimiento de matriz** en fórmulas | `Paramétrico` | 1 regadera de las 3 — no confundir con el rendimiento de cuadrilla |

### «Tipo» — 4 significados

| Significado | Dónde aparece | Cómo se distingue |
|---|---|---|
| La categoría del insumo | `Última columna de los catálogos de insumo` | Material · Trabajo · Mano de Obra |
| La clase del trabajo | `Segunda columna de trabajos` | Destajo · Subcontrato · Acarreo |
| El rol en el árbol | ``CATALOGO_DE_PRESUPUESTO`` | Capítulo · Nivel 2 · Concepto |
| La naturaleza del hijo en la explosión | ``ANALISIS_DE_BASICOS_*`` | El ADN de la línea |

### «Auxiliar» — 3 significados

| Significado | Dónde aparece | Cómo se distingue |
|---|---|---|
| Categoría de insumo que reporta a sí misma | `— hoy vacía` | No depende de otra categoría |
| Concepto auxiliar: agrupador por prototipo | `Filas `Nivel 3`` | Suma de conceptos |
| El prefijo `AUX-` | `Catálogo de materiales` | **Engaña: son materiales compuestos** |

### «Familia» — 3 significados

| Significado | Dónde aparece | Cómo se distingue |
|---|---|---|
| La sustancia | `Materiales` | Aceros, Maderas, Pétreos |
| El oficio | `Trabajos` | Albañilería, Obra Civil |
| El rango | `Mano de obra` | Peones, Oficiales |

### «Origen» — 2 significados

| Significado | Dónde aparece | Cómo se distingue |
|---|---|---|
| La categoría del padre en la explosión | ``ANALISIS_DE_BASICOS_*`` | A qué reporta el monto |
| Qué informe generó el archivo | ``CATALOGO_DE_PRESUPUESTO`` | Vale `Presupuesto` |

### «Catálogo de conceptos» — 2 significados

| Significado | Dónde aparece | Cómo se distingue |
|---|---|---|
| El vocabulario: los conceptos disponibles | ``CATALOGO_DE_CONCEPTOS`, 470` | Lo que se puede usar |
| El presupuesto de una obra | `Uso común en México` | Lo que se va a construir |

### «Costo unitario» — 2 significados

| Significado | Dónde aparece | Cómo se distingue |
|---|---|---|
| Precio de compra de un insumo | `Catálogos de insumo` | $24.68 por KG |
| Precio unitario de un concepto | `Presupuesto` | $71.71 por m² |

### «Costo» — 2 significados

| Significado | Dónde aparece | Cómo se distingue |
|---|---|---|
| Precio del hijo en la explosión | ``ANALISIS_DE_BASICOS_*`` | El del catálogo |
| **La base ya calculada**, en líneas `%MO` | ``ANALISIS_DE_BASICOS_*`` | 1,880 en una cuadrilla, 560 en otra |

---

## Índice de búsqueda

Cualquier forma de decirlo → término canónico. Es lo que consulta el agente.

| Casa | Lote |
| Clúster | Cluster |
| Cluster | **Cluster** |
| Desarrollo | Proyecto |
| Lote | **Lote** |
| Nivel de casa | **Nivel de casa** |
| Nivel de presupuesto | Nivel de construcción |
| Obra | Lote |
| Piso | Nivel de casa |
| Proyecto | **Proyecto** |
| Roof garden | Nivel de casa |
| Se dice | Término canónico |
|---|---|
| %MO | **%MO** |
| Acarreo | Flete |
| Acarreo | **Acarreo** |
| Actividad | **Actividad** |
| Actividad | Concepto |
| Agrupador | Concepto auxiliar |
| Ajuste | Destajo |
| Alcance | **Alcance** |
| Anidamiento | Matriz dentro de matriz |
| Análisis | APU |
| Aplicación | Instancia |
| APU | **APU** |
| APU | Matriz |
| Asignación | **Asignación** |
| Auxiliar | **Auxiliar** |
| Auxiliar | Básico de obra |
| Avance | **Avance** |
| Brigada | Cuadrilla |
| Básico de obra | Auxiliar |
| Básico de obra | **Básico de obra** |
| Básico de obra | Compuesto |
| Cantidad | **Cantidad** |
| Cantidad de obra | Volumen de obra |
| Capítulo | **Capítulo** |
| Cargo de etapa | Insumo de etapa |
| Cargos indirectos | Costo indirecto |
| Categoría | **Categoría** |
| Categoría | Tipo |
| Categoría de material | Familia |
| Catálogo de conceptos | Presupuesto |
| Catálogo de obra | Presupuesto |
| CD | Costo directo |
| Clase | **Clase** |
| Clave | **Clave** |
| Clave alterna | Clave usuario |
| Clave de concepto | Clave |
| Clave de insumo | Clave |
| Clave usuario | **Clave usuario** |
| Clon | **Clon** |
| Cláusula de alcance | Alcance |
| Coeficiente | Cantidad |
| Cohorte | **Cohorte** |
| Componente | Insumo |
| Composición | **Composición** |
| Compuesto | Básico de obra |
| Compuesto | **Compuesto** |
| Concepto | **Concepto** |
| Concepto auxiliar | **Concepto auxiliar** |
| Concepto compuesto | Matriz dentro de matriz |
| Consecutivo | Índice |
| Consumo | Cantidad |
| Contratista | **Contratista** |
| Contrato | Trabajo |
| Contrato a terceros | Subcontrato |
| Control de cambio | Orden de cambio |
| Copia | Clon |
| Corte | Estimación |
| Costo directo | **Costo directo** |
| Costo indirecto | **Costo indirecto** |
| Costo por categoría | Reporte de montos |
| Cotización | Precio propuesto |
| Criterio de aplicabilidad | Cohorte |
| Cronograma | Gantt |
| Cuadrilla | **Cuadrilla** |
| Código | Clave |
| Código interno | Clave usuario |
| Cómputo métrico | Volumen de obra |
| Deducción | Descuento |
| Descripción | **Descripción** |
| Descripción corta | **Descripción corta** |
| Descuento | **Descuento** |
| Desglose | Matriz |
| Destajo | **Destajo** |
| Destajo | Trabajo |
| Desviación | **Desviación** |
| Disciplina | Especialidad |
| División | **División** |
| Divisor | **Divisor** |
| Ejecutado | Avance |
| Ejecutado sin respaldo | **Ejecutado sin respaldo** |
| Ejecutor | Contratista |
| Empaque | Presentación de compra |
| Ensamble | **Ensamble** |
| Equipo de trabajo | Cuadrilla |
| Especialidad | **Especialidad** |
| Estimación | **Estimación** |
| Estructura de desglose | WBS |
| Etapa | Etapa de construcción |
| Etapa de construcción | **Etapa de construcción** |
| Explosión | Matriz |
| Explosión | **Explosión** |
| Explosión de insumos | Explosión |
| Explosión de insumos | APU |
| Extraordinario | **Extraordinario** |
| Extracción | **Extracción** |
| Familia | **Familia** |
| Fase | Etapa de construcción |
| Flete | **Flete** |
| Formato de compra | Presentación de compra |
| Frente | **Frente** |
| Frente de trabajo | Frente |
| Fusión | **Fusión** |
| Ganancia | Utilidad |
| Gantt | **Gantt** |
| Generador | Estimación |
| Gremio | Especialidad |
| Gremio | Frente |
| Grupo | Familia |
| id interno | **id interno** |
| Identidad interna | id interno |
| Highlight | **Highlight** |
| Importe | **Importe** |
| Incluye | Alcance |
| Indirectos | Costo indirecto |
| Instancia | **Instancia** |
| Insumo | **Insumo** |
| Insumo de etapa | **Insumo de etapa** |
| Jornal | Mano de obra |
| Mano de obra | **Mano de obra** |
| Margen | Utilidad |
| Material | **Material** |
| Matriz | **Matriz** |
| Matriz | APU |
| Matriz | Concepto |
| Matriz dentro de matriz | **Matriz dentro de matriz** |
| MO | Mano de obra |
| Modelo | Plantilla |
| Modelo | Prototipo |
| Monto | Importe |
| Módulo | Ensamble |
| Nivel 2 | Etapa de construcción |
| Nivel 3 | Concepto auxiliar |
| Nivel de construcción | **Nivel de construcción** |
| Nombre corto | Descripción corta |
| Oficio | Especialidad |
| OT | Orden de trabajo (OT) |
| Orden | Índice |
| Orden de cambio | **Orden de cambio** |
| Orden de trabajo (OT) | **Orden de trabajo (OT)** |
| Origen | Procedencia |
| P.U. | PU |
| Paramétrico | Ensamble |
| Parcial | Importe |
| Partida | Concepto |
| Parámetro | Divisor |
| Planta | Nivel de casa |
| Plantilla | **Plantilla** |
| Porcentaje sobre mano de obra | %MO |
| Precio a destajo | Destajo |
| Precio de contrato | Precio pactado |
| Precio pactado | **Precio pactado** |
| Precio propuesto | **Precio propuesto** |
| Precio unitario | PU |
| Prefijo | **Prefijo** |
| Presentación de compra | **Presentación de compra** |
| Presupuesto | **Presupuesto** |
| Procedencia | **Procedencia** |
| Programa de obra | Gantt |
| Progreso | Avance |
| Prototipo | **Prototipo** |
| Prototipo | Capítulo |
| Proveedor de mano de obra | Contratista |
| PU | **PU** |
| Recurso | Insumo |
| Rendimiento calculado | **Rendimiento calculado** |
| Rendimiento de campo | Rendimiento real |
| Rendimiento de proyecto | Rendimiento teórico |
| Rendimiento del enganche | Rendimiento calculado |
| Rendimiento real | **Rendimiento real** |
| Rendimiento teórico | **Rendimiento teórico** |
| Reporte de montos | **Reporte de montos** |
| Ruta | WBS |
| Sigla de clave | Prefijo |
| Subcapítulo | Nivel de construcción |
| Subcontrato | **Subcontrato** |
| Subfamilia | **Subfamilia** |
| Sub-frente | Frente |
| Suministro | Material |
| Tarea | Actividad |
| Tarjeta | APU |
| Texto del concepto | Descripción |
| Tipo | Categoría |
| Tipo | Plantilla |
| Tipo | Clase |
| Tipo | **Tipo** |
| Tipo de casa | Prototipo |
| Tipo de pieza | Subfamilia |
| Total de línea | Importe |
| Trabajo | **Trabajo** |
| Trato | Destajo |
| UM | Unidad |
| Unidad | **Unidad** |
| Unidad de medida | Unidad |
| Urbanización | **Urbanización** |
| Utilidad | **Utilidad** |
| Valuación | Estimación |
| Variación | Desviación |
| Variante | Clon |
| Volumen de obra | **Volumen de obra** |
| WBS | **WBS** |
| Zona | Nivel de construcción |
| Índice | **Índice** |
| Ítem | Concepto |

### Escenario

**Palabra con dos usos, y conviene no mezclarlos.**

- **Escenario de presupuesto** — una versión alternativa de la misma obra, para
  comparar antes de decidir. Cambian precios, alcance o programa. Uno queda vigente
  y el resto se archiva (B-39).
- **Escenario de prueba** — un caso con datos reales para comprobar que el sistema
  hace lo que dice (B-42).

- **No confundir con:** Versión; Prototipo
- **Se usa con:** Presupuesto; Paramétrico; Programa
- **Hoy vive en:** Escenario de presupuesto — `PRESUPUESTO(tipo=escenario)`,
  `MODELO.md` §3a, D-335. Escenario de prueba — `PENDIENTES-MEJORAS.md`
  B-42, sin diseñar (no aplica: son casos de prueba, no schema)

