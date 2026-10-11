# CATÁLOGOS DE ORIGEN

```
órgano:     memoria perceptiva — los datos de origen
capa:       I — Mundo
pregunta:   ¿qué trae cada catálogo de OPUS y qué trampas tiene?
tiempo:     es así
corte:      2026-09-21
verificado: 8 catálogos de OPUS 2025 · aritmética comprobada
```

> **Lo que entrega OPUS 2025.** Punto de partida, no alcance final. Las reglas del
> sistema viven en `CONOCIMIENTO.md`; aquí sólo qué contiene cada archivo, cómo se
> relaciona con los demás y qué esconde.

---

### Hay dos generaciones de export, y no son lo mismo

| Generación | Archivos | Para qué existía |
|---|---|---|
| **Anterior** | `Catalogo_de_Matriales`, `Catalogo_de_auxiliares`, `Catalogo_de_cuadrillas`, `catalogo_de_SUBCONTRATOS` | **Alimentar a los otros ERP** |
| **OPUS 2025** | `CATALOGO_DE_PRESUPUESTO`, `CATALOGO_DE_MATERIALES`, `CATALOGO_DE_TRABAJOS`, `CATALOGO_DE_MANO_DE_OBRA`, `CATALOGO_DE_FLETES`, `CATALOGO_DE_CONCEPTOS`, los dos `ANALISIS_DE_BASICOS_*` | **Esta parte del conocimiento** |

**Los de la generación anterior no son una versión vieja del mismo dato**: son un
export distinto, con otro propósito y otras columnas.

Y cambian de dirección: **los otros ERP los siguen necesitando, pero ahora se
alimentan desde OPUS y desde este conocimiento.** Dejan de ser entrada y **pasan a
ser salida generada** — su estructura es el contrato de exportación.

### Los que no compiten y siguen vigentes

Tres catálogos de la generación anterior **no tienen equivalente en OPUS 2025 y
siguen siendo referenciados**:

| Catálogo | Estado |
|---|---|
| `Catalogo_de_unidades` (16) | El vocabulario de unidades. **Vigente** |
| `CATALOGO_DE_NIVELES` (15) | **Los 15 se usan** como subcapítulo del presupuesto, vía `Nivel ERP` |
| `CATALOGO_DE_ETAPAS_DE_CONSTRUCCIÓN` (50) | **Desactualizado:** el presupuesto usa 52 etapas y **tres no están en el catálogo** — `ECO-00029`, `ECO-00035`, `ECO-00051` |
| `CATALOGO_DE_FAMILIAS` (35) | Es el vocabulario maestro, con prefijo. **Desactualizado:** 20 de 35 coinciden con las familias vigentes, y sin acentos |
| `CATALOGO_DE_CONTRATISTAS` (29) | Sin equivalente en OPUS 2025 |

*D-453: las etapas de instalaciones se quedan separadas; solo Hidráulicas y Sanitarias se fusionarán después en Hidrosanitarias, con claves nuevas y sin reescribir las actuales (B-91). `ECO-00039` «HIDRO-SANITARIOS» ya existe, en Muebles / Iluminación.*

*D-460 diseña la fusión: «INSTALACIONES HIDROSANITARIAS» más CIM, PB o PA, con claves ECO nuevas (no choca con `ECO-00039`); convive con las dos originales, se usa en versiones nuevas de la plantilla y solo en presupuestos en diseño; ninguna partida cambia de fecha. Detalle en `CONOCIMIENTO.md` §11.14.*

### Qué archivos de OPUS están en el repo, y cuáles no (D-472)

Los archivos que se suben a una sesión viven en una carpeta temporal de la máquina y se pierden con ella. Lo que sirve de
dato para probar se guarda en el repo, tal cual.

| Archivo | Filas | Dónde está |
|---|---|---|
| `CATALOGO_DE_PRESUPUESTO` | 3,231 | `1-mundo/opus/CATALOGO_DE_PRESUPUESTO.csv` |
| `ANALISIS_DE_BASICOS_CONCEPTOS` | 2,568 | `1-mundo/opus/ANALISIS_DE_BASICOS_CONCEPTOS.csv` — trae también los compuestos y las 39 cuadrillas |
| `ANALISIS_DE_BASICOS_COMPUESTOS` | 267 | `1-mundo/opus/ANALISIS_DE_BASICOS_COMPUESTOS.csv` — son las líneas de `Origen = Material` del anterior, idénticas |
| `INGENIERIA - ALAMO 18 - …` | 11 archivos | `1-mundo/opus/ingenieria-alamo-18/` |
| `CATALOGO_DE_MATERIALES` (387), `_TRABAJOS`, `_MANO_DE_OBRA`, `_FLETES`, `_CONCEPTOS` | — | **No están.** Se describen arriba porque se leyeron en sesiones anteriores; el archivo no está ni en el repo ni en la máquina |
| Los de la generación anterior: unidades (16), niveles (15), etapas (50), familias (35), contratistas (29), cuadrillas, auxiliares, materiales (325), subcontratos | — | **No están**, por lo mismo |

*Lo que falta bloquea P-09, P-32, M-14, B-07 y el cierre de P-14. Quien los tenga puede subirlos tal cual (`.xlsx` o `.csv`).*

*D-479: por indicación del usuario esto ya no es una petición —son temas menores y no se vuelve a preguntar por ellos—; se registran como no disponibles. Lo que el usuario sí compartió está completo en el repo, con la lista de abajo.*

### Las demás tablas que el usuario compartió, a salvo (D-479)

Además de los 14 CSV de OPUS (arriba), el usuario subió 14 libros de Excel que solo vivían en la carpeta temporal de la sesión. Cada uno está **tal cual** (la huella lo prueba) y cada hoja, también como CSV, en `1-mundo/fuentes/`; `1-mundo/fuentes/MANIFIESTO.csv` lista los 59 archivos con su huella sha256.

| Tabla | Qué es | Dónde está |
|---|---|---|
| `03_MARZO` a `07_JULIO_MOVIMIENTOS_DE_ALMACEN` | El export de movimientos de almacén del ERP externo, un mes por archivo (hoja `Consulta`, 46 columnas; la de julio trae una 47ª) | `1-mundo/fuentes/almacen/` |
| `grid_AvanceOPEventosOpr_MARZO`, `_28` (abril), `_MAYO`, `_JUNIO`, `_JULIO` | El avance de operación por evento, todas las obras (hoja `Consulta`, 25 columnas) | `1-mundo/fuentes/avance/` |
| `PRECIO_REAL_ALAMO_18` (dos versiones) | Lo realmente pagado en ALAMO 18, nueve hojas. **La primera que se subió (27 KB) es la chica; `__2` (89 KB, cinco minutos después) es la completa** | `1-mundo/fuentes/precio-real/` |
| `SEMILLA-cuadrilla-rendimiento` | La semilla de cuadrillas y rendimientos (hoja `Semilla`) | `1-mundo/fuentes/semilla/` |
| `PROGRAMA_ZAFIRO` | El programa de Zafiro del que salen los siete (hojas `Hoja1`, 222 columnas, y `Hoja2`) | `1-mundo/fuentes/programa/` |

Las notas de lectura que se escribieron al recibir almacén y precio real están en `1-mundo/fuentes/notas/`. **Una prueba del CI vigila todo esto**: falla si falta una tabla, si cambió o si llega una que el manifiesto no conoce. `METODO.md` §2.6 dice qué hacer cuando llega una nueva.

### Lo que OPUS tiene y aún no está en este proyecto

Se pueden agregar más adelante. **No hacen falta por ahora:**

- **Costos horarios** de maquinaria y equipo
- **Herramienta**
- **FSR** — factor de salario real (el cálculo existe en §4 pero no se carga)
- **Análisis de indirectos** — de campo y de oficina
- **Utilidad**

Los tres últimos son justamente las capas de sobrecosto de `erp-construccion.md` §6, que hoy no están en
ningún dato: **el sistema calcula el costo directo, no el precio de venta.**

## 1 Presupuesto de obra — `CATALOGO_DE_PRESUPUESTO.xlsx`

**Qué es.** El presupuesto completo de siete prototipos de vivienda, exportado de
OPUS 25. Es el documento central del sistema: todo lo demás lo alimenta o se
deriva de él.

**Tamaño.** 3,231 filas · 17 columnas · una sola hoja.

### Los siete capítulos

En este presupuesto cada capítulo es un prototipo de vivienda. **Es el uso que le
da esta empresa, no una regla del modelo** — ver «El WBS».

| Clave | Prototipo | m² | Total | % |
|---|---|---|---|---|
| CAS-00004 | Zafiro 1.0 | 172 | $1,842,426.01 | 11.19 |
| CAS-00003 | Rubí | 207 | $2,040,945.97 | 12.40 |
| CAS-00006 | Zafiro Plus | 224 | $2,175,243.96 | 13.21 |
| CAS-00002 | Jade | 230 | $2,156,131.02 | 13.10 |
| CAS-00005 | Diamante sin chimenea | 239 | $2,800,860.95 | 17.02 |
| CAS-00007 | Diamante con chimenea | 239 | $2,829,925.98 | 17.19 |
| CAS-00001 | Oro 4.01 (4 rec + estudio) | 300 | $2,615,089.61 | 15.89 |

**Total general: $16,460,623.50.** La columna `%` es la participación de cada
prototipo sobre ese total, y suma exactamente 100.

### Las columnas

| Columna | Qué contiene |
|---|---|
| `Tipo` | Etiqueta semántica: Capítulo, Subcapítulo, Nivel 2, Nivel 3, Concepto |
| `Nivel` | **Profundidad real en el árbol** (0 a 4) |
| `Indice` | Orden del renglón dentro de su padre |
| `Nivel ERP` | **Llave foránea al catálogo de niveles** (1..15) |
| `Ingenieria ERP` | **El WBS**, en su forma numérica de 7 dígitos (ver «El WBS») |
| `Clave` | Identificador del concepto o del agrupador |
| `Descripción de matriz` | Descripción que viene del APU |
| `Descripción` | Descripción usada en el presupuesto |
| `Descripcion Corta` | Versión abreviada, para listados |
| `Unidad de matriz` | Unidad que viene del APU |
| `Unidad` | Unidad usada en el presupuesto |
| `Cantidad` | Volumen de obra a ejecutar |
| `Precio unitario` | PU del concepto |
| `Total` | Cantidad × PU |
| `%` | Participación sobre el total general |
| `Origen` | Procedencia — hoy siempre `Presupuesto`. Puede traer también el catálogo: material, trabajo… |
| `Ruta paramétrica` | **Vacía en las 3,231 filas** |

### Cómo se arma la jerarquía

**Es una lista indentada: el padre se determina por orden de fila más profundidad.**
No hay columna de clave del padre.

```
Nivel 0  Capítulo      CAS-00004  ZAFIRO 1.0 (172 M2)
Nivel 1  Subcapítulo   NIV-00001  CIMENTACIÓN
Nivel 2  Nivel 2       ECO-00001  ESTRUCTURA CIM
Nivel 3  Nivel 3       EST-01040  LOSA CIMENTACIÓN ZAFIRO 1P
Nivel 4  Concepto      EST-01040  Losa de cimentación…      1 act   $130,104.85
Nivel 4  Concepto      EST-10010  K1 - 4.00 acero          37 pza     $3,515.37
Nivel 4  Concepto      EST-10011  K1 - 6.00 acero           6 pza       $844.86
```

Para reconstruirla: recorrer las filas en orden, manteniendo una pila por
profundidad. El padre de una fila de nivel *n* es la última fila vista de nivel
*n−1*.

> **Ojo con `Ingenieria ERP`.** A veces el concepto lleva el código de su contenedor
> —el Nivel 3 es `1010101` y sus conceptos dicen `1010100`— y a veces recibe segmento
> propio: bajo `ECO-00006` los conceptos son `1020601`, `1020602`.
>
> **La regla no se pudo deducir** (§11). Sirve para ubicar, no para identificar.

### El WBS — la estructura de verdad

`Ingenieria ERP` es la representación numérica de lo que en el ERP se llama
**WBS**. La columna con ese nombre no viene en el Excel, pero es la que el sistema
necesita.

```
1 01 01 01 [01] [01] …
│  │  │  │   │    └── material / insumo
│  │  │  │   └─────── concepto
│  │  │  └─────────── Nivel 3
│  │  └────────────── Nivel 2
│  └───────────────── Subcapítulo
└──────────────────── Capítulo
```

**El WBS es extensible.** Los 7 dígitos del export son lo que este presupuesto
necesitaba, no un límite del modelo. Se agregan pares de dígitos para bajar a
concepto y a material.

#### Tres cosas que hay que entender bien

**1. El capítulo no es un prototipo.** En esta empresa el capítulo se usa para
representar cada prototipo de vivienda, pero eso es *cómo lo usa esta empresa*, no
lo que el nivel significa. El formador de presupuestos es libre: un capítulo puede
ser una obra, una torre, un lote, una etapa comercial o cualquier agrupación que
convenga.

**2. El concepto puede colgar de cualquier nivel.** Directo del presupuesto, de un
capítulo, de un subcapítulo, de un nivel o de un Nivel 3. No hay una profundidad
reservada para él.

**3. Por lo tanto, la profundidad no dice qué es un nodo.** En este archivo ya se
ve, aun sin llegar a insumos:

| Ubicación del concepto | Filas |
|---|---|
| Nivel 3 — cuelga directo de Nivel 2 | 1,233 |
| Nivel 4 — cuelga de un Nivel 3 | 1,219 |

Casi mitad y mitad. Cualquier importador que asuma «nivel 4 = concepto» se rompe
con la mitad de los datos.

#### Cómo guardarlo en el ERP

> **El árbol es la verdad; el código numérico es presentación.**

Guardar el WBS como entero de ancho fijo tiene dos problemas:

- **Techo de hermanos.** Dos dígitos por segmento topan en 99 hijos. Un subcapítulo
  con 100 conceptos no cabe.
- **Ambigüedad de los ceros.** `1010100` no distingue «capítulo 1, subcap 1,
  nivel 1» de esa misma ruta con un nivel más en cero.

Recomendación: guardar la **ruta** (`1.1.1.1`) o la relación padre-hijo, y
**generar** el código numérico al exportar, con el ancho de segmento como
configuración. Así el formador queda libre y el export sigue siendo compatible
con OPUS.

### El Nivel 3 es el concepto auxiliar

Los renglones de `Nivel 3` son los **agrupadores por prototipo**: condensan varios
conceptos bajo un renglón. 238 filas, 67 claves distintas.

Comprobado en el ejemplo de arriba:

```
Nivel 3   EST-01040   LOSA CIMENTACIÓN ZAFIRO 1P    $143,413.40
          └── concepto EST-01040                     $130,104.85
          └── 8 conceptos de castillos                $13,308.55
                                          suma =     $143,413.40 ✓
```

> **Cuatro claves aparecen como Nivel 3 y como Concepto al mismo tiempo.** El
> agrupador y su concepto principal comparten clave. Al importar, la clave sola no
> distingue uno de otro: hace falta el tipo o la profundidad.

### La aritmética cuadra por completo

**665 nodos con hijos. Los 665 cuadran.** Cero diferencias.

El total reconstruido desde las hojas coincide al centavo con la suma declarada
de los capítulos: $16,460,623.50.

> **Son dos verificaciones distintas y hay que hacer las dos**: que el árbol sume
> bien, y que el PU de cada concepto corresponda a su explosión. Esta primera cierra;
> la segunda necesita el análisis de básicos de conceptos.

### Qué contiene

- **2,445 renglones de concepto**, sobre **471 claves distintas**. Cada concepto se
  usa en promedio en cinco lugares.
- **102 subcapítulos**, repartidos así:

| Prototipo | Subcapítulos |
|---|---|
| Zafiro 1.0, Rubí, Jade | 14 |
| Zafiro Plus, Diamante −, Diamante +, Oro | 15 |

  La diferencia es exactamente **Planta Alta**, que solo tienen los cuatro de dos
  plantas — los mismos cuya cimentación se comporta distinto (`CONOCIMIENTO.md` §5.7).
  Rubí escribe `AZOTEA/ROOF` donde los demás dicen `AZOTEA`: mismo nivel, caso de
  diccionario.
- **No hay insumos.** Este archivo llega hasta el concepto. La explosión a
  materiales y destajos vive en el análisis de básicos de conceptos.

**Unidades usadas** (en minúsculas, sin normalizar):
`sal` 827 · `pza` 798 · `m2` 421 · `m` 337 · `act` 52 · `m3` 8 · `ser` 2

**Prefijos de concepto más usados:**
`IEC` 505 · `ACA` 501 · `EST` 255 · `ISN` 246 · `IHD` 241 · `OBE` 124 ·
`IGAS` 116 · `MSA` 114 · `ALB` 104 · `CAR` 94

### Hallazgo: `Nivel ERP` es la llave que faltaba

En el análisis de los catálogos base quedó anotado que la jerarquía
nivel → etapa no tenía llave foránea. **Aquí está.**

`Nivel ERP` mapea uno a uno contra el catálogo de niveles, sin ambigüedad:

| Nivel ERP | Clave | Descripción |
|---|---|---|
| 1 | NIV-00001 | Cimentación |
| 2 | NIV-00002 | Planta baja |
| 3 | NIV-00003 | Planta alta |
| 4 | NIV-00004 | Azotea |
| 5 | NIV-00005 | Acabados |
| 6 | NIV-00006 | Obras exteriores |
| 7 | NIV-00007 | Cancelería |
| 8 | NIV-00008 | Carpintería |
| 9 | NIV-00009 | Muebles / iluminación |
| 10 | NIV-00010 | Herrería |
| 11 | NIV-00011 | Asador |
| 12 | NIV-00012 | Barda perimetral |
| 13 | NIV-00013 | Pintura |
| 14 | NIV-00014 | Pergolado cochera |
| 15 | NIV-00015 | Consumibles |

`NIV-00004` aparece con dos descripciones cortas —*Azotea* y *Azotea/Roof*—
apuntando al mismo nivel 4. Es un caso para el diccionario, no un error de datos.

### Trampas al importar

1. **121 filas vacías: placeholders del propio OPUS.** Ver `CONOCIMIENTO.md` §2.5 — se descartan.
2. **Las descripciones duplicadas por columna.** `Descripción de matriz` y
   `Descripción` son idénticas en 2,445 de 2,452 filas; las 7 que difieren son
   justamente las filas vacías. Lo mismo con las dos columnas de unidad. **Hoy son
   redundantes, pero el hecho de que existan por separado significa que el sistema
   contempla que el presupuesto sobrescriba lo que dice el APU.**
3. **7 conceptos con total en cero** y 5 con precio unitario en cero.
4. **`Ruta paramétrica` está vacía.** Es el paramétrico de OPUS 25, sin usar. El
   paramétrico de este sistema se diseña aparte (`CONOCIMIENTO.md` §5): la columna se descarta.
5. **Unidades sin normalizar**, igual que en el catálogo de conceptos.

---

### Preguntas abiertas de este catálogo

| # | Pregunta |
|---|---|
| ~~K-01~~ | ~~¿Qué son las 121 filas vacías?~~ ✅ **Resuelta:** placeholders de OPUS, se descartan (`CONOCIMIENTO.md` §2.5) |
| ~~K-02~~ | ~~¿Zafiro Plus con 4 subcapítulos?~~ ✅ **Resuelta:** error de lectura. Son 14 o 15 según tenga planta alta |
| K-03 | ¿Los 5 conceptos con PU en cero están pendientes de costear? |
| ~~K-04~~ | ~~¿Para qué sirve `Ruta paramétrica`?~~ ✅ **Resuelta:** es el paramétrico de OPUS. Se descarta; el nuestro es `CONOCIMIENTO.md` §5 |
| ~~K-05~~ | ~~¿`Origen` tiene otros valores?~~ ✅ **Resuelta:** sí, trae catálogo. Se parte en dos (`CONOCIMIENTO.md` §2.6) |
| ~~K-06~~ | ~~¿La descripción puede diferir de la del APU?~~ ✅ **Resuelta:** `CONOCIMIENTO.md` §2.7, tres gravedades y la huella |
| ~~K-07~~ | ~~¿Cuántos dígitos por segmento del WBS?~~ ✅ **Resuelta:** separador por puntos, ancho libre (`CONOCIMIENTO.md` §1.1) |
| ~~K-08~~ | ~~¿El WBS se renumera al reordenar?~~ ✅ **Resuelta:** sí, y por eso la identidad es el `id` (`CONOCIMIENTO.md` §1.2) |
| ~~K-09~~ | ~~¿Qué diferencia de texto alerta?~~ ✅ **Resuelta:** `CONOCIMIENTO.md` §2.7.1 |
| ~~K-10~~ | ~~¿Quién aprueba una versión nueva?~~ ✅ **Resuelta:** nadie por defecto; por impacto (`CONOCIMIENTO.md` §2.2) |
| ~~K-11~~ | ~~`ACA-00021` vacío~~ ✅ **Resuelta:** agrupador pendiente de costear (`CONOCIMIENTO.md` §4.1) |
| ~~K-12~~ | ~~¿Qué columnas llevan Cabeceras, Materiales y Operaciones?~~ ✅ **Resuelta:** contra especímenes reales de `ALAMO 18` (`CONOCIMIENTO.md` §4.3). Los cuatro catálogos de solo salida siguen sin columna documentada — falta el catálogo viejo, igual que P-32 |
| ~~K-13~~ | ~~¿El hermano 100?~~ ✅ **Resuelta:** alerta en 90, reagrupar. No hay tercer dígito (`CONOCIMIENTO.md` §4.2) |

## 2 Materiales — `CATALOGO_DE_MATERIALES.xlsx`

**387 filas · 10 columnas.** Versión más reciente y más grande que la analizada al
inicio (325).

### La columna `C` es el marcador de compuesto

| `C` | Filas | Qué son |
|---|---|---|
| `+` | **89** | **Se abren**: tienen desglose propio |
| *(vacío)* | 298 | Insumos sencillos |

Los 89 compuestos son `AUX` 79, `MEZ` 8, `ZA1`/`ZA2` 2 — trabes, mallas, mezclas y
zapatas.

> **Confirma `CONOCIMIENTO.md` §10.3 con datos.** El `+` es literalmente lo que se abre: los básicos
> de obra existen y están marcados en el propio catálogo.

### Los auxiliares viven aquí, no en un catálogo aparte

`AUX-00001 Trabe T-3 de 15x25 cm`, familia **Auxiliar**, $72.14 por m.

### Tres niveles de clasificación

La versión corregida del catálogo trae `Tipo` y `Subfamilia`, y con eso queda claro
que **son tres campos distintos**:

| Campo | Qué clasifica | Valores |
|---|---|---|
| `Tipo` | **La categoría** | `Material` en las 387 |
| `Familia` | La naturaleza | 18 valores: Electrico, Sanitario, Aceros… |
| `Subfamilia` | El tipo de pieza | 34 valores: Trabe, Parrillas, Nervadura… |

> **`Tipo` es la categoría de `CONOCIMIENTO.md` §10.** Vale `Material` en todo el archivo, como
> corresponde al catálogo de materiales.

### «Auxiliar» era familia mal usada — ya está corregido

En la versión anterior, 79 compuestos tenían familia `Auxiliar`, que no decía de qué
estaban hechos. **Esa familia desapareció** y quedaron repartidos por naturaleza:

| Familia | AUX reasignados |
|---|---|
| Elemento Estructural | 46 |
| Acero De Refuerzo | 31 |
| Aceros | 4 |

> Queda resuelto: **`Auxiliar` nunca fue categoría.** La categoría es `Tipo`, y ser
> compuesto lo marca la columna `C`. Ser compuesto no exime de tener familia.

### La subfamilia es donde cae lo estructural

Los 89 compuestos quedaron clasificados con precisión:

| Subfamilia | Compuestos |
|---|---|
| Parrillas | 35 |
| Trabe | 24 |
| Contratrabe | 7 |
| Losa Nervada | 6 |
| Nervadura | 5 |
| Morteros · Concretos | 6 |
| Mampostería · Zapata | 4 |
| Estuco · Pegapiso | 2 |

**Una parrilla o una nervadura son tipos de elemento, no de material.** La
subfamilia es donde naturalmente cae esa información.

### Dos cosas sueltas

**171 de 387 no tienen subfamilia** — casi la mitad. Falta decidir si es opcional
por diseño o si está pendiente de llenar.

**Erratas nuevas en el vocabulario**, del mismo tipo que las del diccionario:

| Escrito | Debería ser | Veces |
|---|---|---|
| `Cosumible` | Consumible | 7 |
| `Marmol` / `Marmoles` | uno de los dos | 3 / 2 |
| `Impearmeabilizante` | Impermeabilizante | 2 |
| `Pegapiso ` | sin espacio final | 1 |

Hay que homologarlas **antes** de que la subfamilia se vuelva llave.

### Las columnas

| Columna | Contenido |
|---|---|
| `C` | `+` si es compuesto |
| `Clave` · `Descripción` | Identidad |
| `Comentarios` | **Un número**, no texto. Parece un id o conteo interno. Descartable |
| `Unidad` | **Sin normalizar** |
| `Costo base M. N.` · `M. E.` · `Costo unitario` | M.E. en cero en las 387 |
| `Fecha` | Todas entre el 21 y el 29 de julio de 2026 |
| `Familia` | 18 valores — la naturaleza |
| `Subfamilia` | 34 valores — el tipo de pieza |
| `Tipo` | La categoría. `Material` en las 387 |

### Unidades sin normalizar

Conviven `PZ` con `m`, `m2`, `m3`, `kg`, `serv` y **`CUB ` con espacio final**.
Aplica la misma corrección que se hizo antes (M-04, M-05).

> **Y son un vocabulario distinto al del presupuesto.** El concepto se mide en
> unidades de obra —`m2`, `sal`, `act`—; el insumo en unidades de compra —`RLL`,
> `BTS`, `CUB`, `TMO`—. Comparten catálogo pero **no son intercambiables**: nadie
> compra una salida ni instala un rollo.

### Estado

Sin claves duplicadas. Una descripción repetida. Ningún costo en cero. Precios
todos de la misma semana: **el catálogo de materiales está al día.**

## 3 Trabajos — `CATALOGO_DE_TRABAJOS.xlsx`

**265 filas · 12 columnas.** Es el catálogo de mano de obra que faltaba: aquí viven
los destajos que el árbol referencia.

> `MOA-00112 MO FINAS INTERIORES EN MUROS 0-3.00 MTS`, $50.00 por M2 — **el mismo
> destajo y el mismo precio** con que se usa en los presupuestos. Cruce verificado.

> **Este catálogo reemplaza al de mano de obra `MOOP`.** Aquel quedó sin validez;
> las claves `MOOP-####` que referencian las cuadrillas son de un modelo anterior.
> **Deja de buscarse: el catálogo válido de mano de obra es este.**

### Dos tipos en un solo catálogo

| `Tipo` | Filas |
|---|---|
| Destajo | 259 |
| Subcontrato | 6 |

### Prefijos por especialidad

`MOA` 82 (albañilería) · `MOE` 76 (eléctrica) · `MOS` 45 (sanitaria) ·
`MOH` 23 (hidráulica) · `MOG` 17 (gas) · `MOC` 8 (carpintería) ·
`MOP` 7 (pintura) · `SUB` 6 · `MOO` 1

**17 familias**, que son especialidades: Albañilería, Eléctrico, Obra Civil,
Sanitario, Pinturas, Hidráulico…

### Las unidades sí están normalizadas

`PZ` 147 · `M2` 69 · `M` 43 · `SERV` 4 · `M3` 2. Todas en mayúsculas y del catálogo.

> Contraste con materiales, que no lo están. **La normalización no es pareja por
> catálogo**, así que el cargador no puede asumirla en ninguno.

### Dos columnas se llaman `Tipo`

El archivo trae **dos encabezados idénticos**, y son campos distintos:

| Posición | Valores | Qué es realmente |
|---|---|---|
| 2ª columna | `Destajo` · `Subcontrato` | **Clase** |
| Última columna | `Trabajo` | **Tipo** = la categoría, como `Material` en §2 |

> **Un cargador que busque por nombre tomará una de las dos en silencio.** Es de las
> trampas más difíciles de detectar después. Se resuelve en la capa de mapeo
> (`CONOCIMIENTO.md` §2.4) **leyendo por posición cuando el nombre está duplicado** — nunca
> renombrando el archivo, que vuelve a OPUS.

### Las tres clases, y `Acarreo` vacía

La clase tiene tres valores —**`Destajo`, `Acarreo`, `Subcontrato`**— pero
**`Acarreo` no tiene ni un renglón**.

> Significa que hoy el acarreo o no se costea, o va escondido dentro de otros
> destajos. Si va escondido, ningún análisis de logística lo va a ver.
>
> Y existe además un **catálogo propio de Fletes** (`CONOCIMIENTO.md` §10.2), así que hay que definir
> qué va en cada uno.

### El catálogo también se llama `Contrato`

OPUS lo nombra de las dos formas según el reporte que se pida. **Es el mismo
catálogo**, y el cargador debe reconocer ambos nombres.

### La subfamilia es el elemento

**75 subfamilias en 17 familias**, todas asignadas. La regla que las gobierna:

> La subfamilia es **el elemento que se construye o se instala**, nunca el
> calificativo ni la ubicación.

Se ve en tres decisiones del catálogo:

- `MO MURO DE TABIQUE- HILO` → **Muro**. *Hilo* es cómo se ejecuta, no qué se hace.
- *Fachada* se eliminó como subfamilia: era **ubicación**. Sus repellados y afines
  se unieron a `Muro`, junto a los de interior.
- *Boquillas* pasó a `Vano`, que es donde se ejecutan.

### Por qué sirve: el elemento cruza familias

`Boiler` aparece en tres familias y muestra sus seis trabajos de una vez:

| Clave | Trabajo | Familia | Costo |
|---|---|---|---|
| MOG-05010 | Salida gas | Gas | $200 |
| MOG-06010 | Conexión gas | Gas | $150 |
| MOH-01020 | Salida hidráulica | Hidráulico | $625 |
| MOH-02012 | Conexión hidráulica | Hidráulico | $100 |
| MOS-04010 | Base | Equipamiento | $125 |
| MOS-08090 | Colocación | Equipamiento | $300 |

**$1,500 de mano de obra que antes había que juntar a mano.** Es exactamente lo que
el paramétrico necesita para armar un ensamble (`CONOCIMIENTO.md` §5).

### El prefijo tampoco sirve aquí

| Prefijo | Su familia esperada | Dónde está realmente |
|---|---|---|
| `MOE` (eléctrica) | Eléctrico | **38 sí, pero 33 en Obra Civil y 5 en Albañilería** |
| `MOC` (carpintería) | Carpintería | **ninguna**: 4 en Obra Civil, 3 en Albañilería |
| `MOA` (albañilería) | Albañilería | 31, más 25 en Pinturas y 16 en Acabados |

> Mismo hallazgo que en los conceptos (M-09): **el prefijo es nomenclatura, no
> llave.** La familia va como campo explícito.

### Correcciones aplicadas

Acentos en familias —`Eléctrico`, `Hidráulico`, `Albañilería`, `Cancelería`,
`Carpintería`, `Herrerías`, `Pérgolas`— y en subfamilias —`Cerámico`, `Chaflán`,
`Excavación`, `Jardín`, `Pórfido`, `Recámara`, `Rodapié`, `Caja de Válvulas`,
`Línea principal`—, más `Tv` → `TV`.

Plurales unificados a singular: `Muro`, `Registro`, `Respiración`, `Recubrimiento`,
`Marco`, `Vano`, `Bajada`, `Panel Solar`. Y `Equipamientos` → `Equipamiento`.

> Se conservan en plural `Lavamanos`, `Lavavajillas`, `Voz y Datos` y `Caja de
> Válvulas`: no son plurales sueltos, son nombres compuestos.

**Los encabezados no se tocaron.** El archivo regresa a OPUS y debe conservar su
formato.

### Los subcontratos traen precio ficticio

| Clave | Descripción | Unidad | Costo |
|---|---|---|---|
| SUB-00002 | Subcontrato carpintería | SERV | **$1.00** |
| SUB-00003 | Subcontrato cancelería | SERV | **$1.00** |
| SUB-00004 | Subcontrato herrería | SERV | **$1.00** |
| SUB-00005 | Subcontrato cubiertas lavamanos | SERV | **$1.00** |
| SUB-00001 | Subcontrato pergolado | M2 | $1,730.00 |
| SUB-00006 | Subcontrato imper-casas | M2 | $130.00 |

**Cuatro de los seis valen un peso.** No es un error: son **precio alzado** cuyo
monto real se fija en cada contrato, no en el catálogo (`CONOCIMIENTO.md` §7).

> Es el caso descendente de `CONOCIMIENTO.md` §7 apareciendo en datos reales. Y explica por qué la
> unidad es `SERV`: no hay medida, hay un trato.

### Los precios están envejeciendo

| Año | Destajos |
|---|---|
| 2023 | 1 |
| 2024 | 8 |
| 2025 | **249** |
| 2026 | 7 |

`MOP-00302 MO Preparación de instalaciones para murete`, $600.00, **fechado en
agosto de 2023**. Y toda la familia de Pinturas quedó en enero de 2024.

> Los materiales se actualizaron esta semana; **la mano de obra lleva un año o más
> sin tocarse**. Cualquier PU que mezcle ambos combina precios de épocas distintas
> sin advertirlo — que es exactamente lo que el versionado con vigencia (M-12) debe
> hacer visible.


## 4 Mano de obra — `CATALOGO_DE_MANO_DE_OBRA.xlsx`

**97 filas · 36 columnas · los datos están en `Hoja2`, no en `Hoja1`.**

> **Sustituye a dos catálogos anteriores**: el de mano de obra `MOOP` y el de
> cuadrillas. Los dos quedan sin validez.

### Individuales y cuadrillas en un solo catálogo

| `C` | Filas | Qué son |
|---|---|---|
| `+` | **39** | Cuadrillas: se abren |
| *(vacío)* | 58 | Personas |

`Tipo` = **`Mano de Obra`** en las 97, que completa el trío con `Material` (§2) y
`Trabajo` (§3).

### Clasificación

| Campo | Qué clasifica | Valores |
|---|---|---|
| `Familia` | **Categoría laboral** | Cuadrillas 39 · Oficiales calificados 16 · Operadores 14 · Ayudantes 12 · Oficiales de albañilería 10 · Oficiales de urbanización 2 · Peones · Supervisores · Laboratoristas · Contratistas |
| `Subfamilia` | **Área de trabajo** | Albañilería y Estructura 29 · Equipo y Maquinaria 22 · Instalaciones 16 · Acabados 9 · Carpintería 6 · Cristal y Aluminio 6 · Exteriores 5 · Topografía 4 |

> **`Familia` significa aquí una tercera cosa.** En materiales es la sustancia, en
> trabajos el oficio, aquí el **rango**. Tres taxonomías con un solo nombre de campo
> (ver §5).

`Cuadrillas` como familia repite el patrón que tenía `Auxiliar` en materiales —una
composición ocupando el lugar de una clasificación— **pero aquí se deja así**: una
cuadrilla no tiene un rango único, tiene un oficial *y* ayudantes, y asignarle el
del que la encabeza sería arbitrario.

### Las cuadrillas se referencian a frentes

Relación **muchos a muchos** entre cuadrilla y frente. Una cuadrilla de albañil y
ayudante sirve a Estructura y a Obra Exterior; un frente ocupa varias cuadrillas.

| Alcance | Detalle |
|---|---|
| Aplica a | **Solo cuadrillas**, no a individuales |
| Naturaleza | **Informativa.** No valida, no impide, no calcula |

> Debe quedar marcada como informativa **desde el principio**. Si no, alguien la
> tomará como restricción y construirá encima algo que no la soporta.


Sirve para filtrar 39 cuadrillas por frente al programar, en vez de recorrer 97
registros. **Las relaciones operativas se definen después.**

> Dónde se definen: `PROPUESTA-CUATRO-MODULOS.md` §4 · P-6, el tope de cuadrillas
> por oficio dentro del frente.

*Nota (D-450): «frente» quedó definido como el nivel constructivo de la obra
(Cimentación, Planta baja…); el gremio es el **sub-frente**, lo que trabaja dentro de un
frente. Esta relación cuadrilla–frente es la del gremio de arriba y sigue siendo
informativa. D-451: cómo queda este catálogo ahora que «frente» cambió de significado
se revisa con el usuario (B-89); no se renombra ni se reinterpreta mientras tanto.*

*D-452: el usuario aclara que no existe catálogo de conceptos-frentes. Esta relación queda como la intención de filtrar cuadrillas por lo que se ejecuta —el sub-frente—, a definir cuando se programe.*

### La unidad `%MO`

96 registros en `JOR`; uno en `%MO` — `MOCA-110 Contratista`, hoy en costo cero.

**`%MO` es una unidad que indica un porcentaje sobre la suma total de la cuadrilla.**

```
Cuadrilla       1 Albañil            $1,452.00
                Contratista  0.1 %MO   $145.20   ← 10% de 1,452
                                     ─────────
                                     $1,597.20
```

Tres reglas:

1. **La base es la suma de las líneas de jornal** de esa cuadrilla.
2. **Se captura como `0.1`, no como `10`.**
3. Si hay varias líneas `%MO`, **todas calculan sobre la misma base**. No se
   acumulan entre ellas.

> **La tercera importa para el motor: el orden de las líneas no afecta el
> resultado.** Si se acumularan, poner el contratista antes o después cambiaría el
> total.

Y **es distinto de las capas de sobrecosto de `erp-construccion.md` §6**, donde el campo `base` existe
porque en México la cascada sí es acumulativa. Dentro de la cuadrilla la base es
siempre la misma. **Son dos comportamientos en dos niveles del árbol; no
unificarlos.**

Por confirmar contra la matriz de compuestos cuando se cargue.

### El FSR viene calculado pero no se carga

20 de las 36 columnas son el desglose del Factor de Salario Real: cuota fija IMSS,
prestaciones en especie y dinero, invalidez y vida, cesantía, riesgos de trabajo,
guarderías, SAR, INFONAVIT, impuesto sobre nómina.

> **No se establece ni se importa.** Se descartan, igual que `Ingenieria ERP`.

### Correcciones aplicadas

`jor` → `JOR` (96) · `Mano De Obra` → `Mano de Obra` (97) · doble espacio en la
descripción de `MOCU-044`.


## 5 Lo que se ve al cruzar los catálogos

Tres hallazgos que **solo aparecen comparando**, no leyendo cada uno por separado.

### `Familia` significa tres cosas distintas

| Catálogo | Qué clasifica la familia | Ejemplos |
|---|---|---|
| Materiales | **La sustancia** | Aceros, Maderas, Pétreos, Adhesivos, Mezclas |
| Trabajos | **El oficio** | Albañilería, Obra Civil, Acabados, Cubiertas |
| Mano de obra | **El rango** | Peones, Ayudantes, Oficiales, Operadores |

Y lo engañoso: **ocho familias coinciden literalmente** —Eléctrico, Hidráulico,
Sanitario, Gas, Pinturas, Plantas, Equipamiento, Herrerías— porque en instalaciones
la sustancia y el oficio se llaman igual.

> Parece un vocabulario común cuando son **tres taxonomías que se cruzan por
> accidente en la mitad**. Mismo patrón que `Tipo` y `Nivel`: un nombre, varios
> significados.

### Las subfamilias no deben homologarse: deben relacionarse

Solo **3 de 108 coinciden**: Cerámico, Recubrimiento y Zapata. Pero no es un
problema de nombres, es **diferencia de granularidad**:

```
trabajos      Losa
materiales    Trabe · Nervadura · Contratrabe · Losa Nervada · Bovedilla
```

La subfamilia del material es una **parte** de lo que la del trabajo nombra como
**elemento**. La relación es *parte-de*, no *igual-a*.

> No hay que unificar los vocabularios: hay que ligarlos. Y ligándolos se contesta
> algo que hoy no se puede — **¿cuánto me cuesta un muro, material más mano de
> obra?**

### El concepto es el eslabón sin clasificación

Materiales tiene `Tipo`, `Familia` y `Subfamilia`. Trabajos también. Mano de obra
también.

> **El presupuesto no trae ninguno de los tres.** El concepto —que es justo donde
> material, trabajo y mano de obra se encuentran— es el único sin clasificar.

### Las unidades están en tres estados

| Catálogo | Estado |
|---|---|
| Trabajos | Normalizado: `PZ`, `M2`, `M`, `SERV` |
| Mano de obra | Normalizado tras corrección: `JOR`, `%MO` |
| Materiales | **Mezclado**: `PZ` con `m`, `m2`, `kg`, `serv`, `CUB ` |
| Presupuesto | **Todo en minúsculas**: `sal`, `pza`, `act`, `m2` |

Cuatro versiones del mismo vocabulario conviviendo. **El cargador no puede asumir
normalización en ninguno.**


## 6 Fletes — `CATALOGO_DE_FLETES.xlsx`

**9 filas.** Catálogo en construcción. `Tipo` = `Flete`.

### Confirma que el insumo cambia de categoría — y destapa un bug

`PET-00015 ARENA DE RIO 14 M3` aparece en **materiales y en fletes**, con la misma
clave, descripción, unidad y costo. Solo cambia `Tipo`.

Otros que ya migraron y **ya no están en materiales**: `PET-00002 ARENA 7 M3`,
`PET-00003 GRAVA 7 M3`, `SER-00003 PIPA 10000` —esta última era componente
`Material` del aplanado en la matriz vieja—.

> **El bug:** si el cargador carga por catálogo, un insumo que migró entra **dos
> veces**. `PET-00015` lo demostró sin buscarlo.
>
> **La regla:** la categoría es **un campo del insumo, no la tabla donde vive**. La
> reconciliación al importar es por clave contra **el conjunto completo de
> insumos**, nunca contra el catálogo que se está cargando.

### `Flete` se estaba usando como apartado — resuelto

Cinco de los nueve no son fletes:

| Clave | Qué es | Por qué está aquí |
|---|---|---|
| `MAD-00004` Tablas | Material — se dan por lotes de 10 pza | Aislado |
| `HID-00026` Lija · `SAN-00091` Tapa · `SAN-00092` Cople · `HID-00038` Manómetro | Materiales de **prueba hidráulica** | Aislados: no se usan siempre |

Se mandaron ahí para **apartarlos**, no para clasificarlos.

> **El riesgo:** hoy son cinco y se controlan de memoria. Cuando alguien saque el
> costo de fletes de una obra, va a incluir unas tablas y un manómetro sin saberlo.
> Y en la explosión reportarán como flete — justo lo que `CONOCIMIENTO.md` §10.5 dice que no debe pasar.

**Resuelto: `revisar` es un campo del insumo, no un abuso de la categoría.**
`MODELO.md` §1 lo agrega como booleano en `NODO` (hallazgo 9) — aísla igual que
antes —se filtra y ahí está—, pero el insumo se queda en Materiales, sigue
reportando como material y no ensucia el costo de fletes. Y cuando toque
clasificar los materiales, ese campo **es** la lista de trabajo.

Sirve para más que este caso: **es la misma bandera para cuando se revisan
insumos al preparar un cambio masivo** — cualquier insumo que necesite mirarse
antes de tocarlo se marca igual, sin inventar un mecanismo aparte.

### Vocabulario

`Petreos` contra `Pétreos`, `Hidraulico`, y `agregado` en minúscula contra
`Agregado`.

### OPUS recalcula

**El presupuesto se recalcula cuando cambian los precios**, así que el desfase entre
catálogos no se traslada al PU importado.

### `Flete` contra la clase `Acarreo` — resuelto

Existe un catálogo `Fletes` y también una clase `Acarreo` dentro de Trabajos (§3).
**La frontera es el límite de la obra, no la dirección**: `Flete` es cruzarlo —de
fuera hacia adentro, o de adentro hacia afuera—; `Acarreo` es moverlo sin cruzarlo.
Regla completa y evidencia en `CONOCIMIENTO.md` §10.2 (P-02/P-03).


## 7 Análisis de básicos compuestos — `ANALISIS_DE_BASICOS_COMPUESTOS.xlsx`

**267 filas.** La explosión de los compuestos: `Clave Padre` → `Clave Hijo` con
cantidad, costo e importe.

> **Es el primer eslabón del hueco central que se llena.** Hasta aquí había árbol
> por arriba del concepto e insumos por abajo, pero ninguna matriz verificada.

### Cierra completa

| Comprobación | Resultado |
|---|---|
| Compuestos del catálogo (`C = +`) | 89 |
| Con explosión en este archivo | **89** — ninguno falta ni sobra |
| Suma de la explosión contra `Costo unitario` del catálogo | **Los 89 cuadran al centavo** |
| Precio de cada hijo contra su catálogo de origen | **39 de 39 coinciden** |

Esa última fila importa: **el precio no está congelado dentro de la matriz.**
Coincide con el catálogo, que es la regla de «el precio vive en un solo lugar».

### El compuesto mezcla categorías — comprobado

| `Tipo` del hijo | Líneas |
|---|---|
| Material | 250 |
| **Flete** | 16 |
| **Contrato** | 1 |

Los fletes son arena, grava y pipa dentro de las mezclas. Y el contrato es el caso
que confirma todo `CONOCIMIENTO.md` §10.5:

```
ZA1-000001  Zapata                                   $1,135.48
  ACR-00002  Varilla 1/2        2.76 PZ   Material      655.56
  ACE-00001  Alambre recocido   0.81 KG   Material       19.92
  MOC-12010  MO ZAPATA ZA-1     1.00 PZ   Contrato      460.00   ← 41%
```

> **El 41% de esa zapata es mano de obra contratada, y aun así reporta como
> material.** Es el caso del tabique, en datos reales.

### Las dos lecturas están en columnas separadas

| Columna | Qué dice | En el ejemplo |
|---|---|---|
| `Tipo` | La naturaleza del hijo — **el ADN** | `Contrato` |
| `Origen` | A qué categoría reporta — **el monto** | `Material` |

**OPUS ya las guarda por separado.** No hay que inventarlas: `CONOCIMIENTO.md` §10.5 estaba
describiendo algo que el sistema actual ya hace.

### Anidamiento: existe, y llega a dos niveles

Seis claves son padre e hijo a la vez. Doce líneas de compuesto dentro de compuesto.

```
AUX-50001  Losa nervada
  └ AUX-00040  Nervadura N-1   ×2
      └ varilla, alambre
  └ AUX-00042  Nervadura N-2   ×2
```

Y `AUX-00201` contiene `MEZ-07010`, una mezcla.

| Profundidad | Compuestos |
|---|---|
| 1 nivel | 81 |
| 2 niveles | 8 |

> **Hoy llega a dos niveles, pero el modelo no debe asumirlo.** El anidamiento tiene
> que ser **escalable a cualquier profundidad** — el recorrido es recursivo y el
> único límite es la prohibición de ciclo (`CONOCIMIENTO.md` §9.3).
>
> Cualquier implementación que fije el número de capas —una tabla por nivel, un
> `JOIN` por capa, una consulta de dos saltos— se rompe con el primer compuesto de
> tres niveles.

### Las cantidades pueden ser negativas

**58 líneas de 2,568, en 23 conceptos.** Todas de tipo Material, y suman −$2,364.69.

```
EST-01053   ACR-00002  Varilla 1/2    −0.656 PZ  ×  237.52  =  −155.81
            ACE-00008  Anillo 15x25   −0.240 KG  ×   24.01  =    −5.77
```

Son **ajustes**: descuentan acero que ya viene contado dentro de un compuesto. Sin
ellos el concepto quedaría duplicando material.

> **Un importador que valide cantidades positivas las rechaza.** Y si las carga en
> valor absoluto, el concepto sale más caro **sin que ninguna suma falle**.

No aparecen en los compuestos: **cero negativas en las 267 líneas**. Es un
mecanismo del nivel de concepto.

### El mismo insumo puede repetirse en una matriz

`AUX-00001` lleva alambre recocido en **dos líneas** —`0.131779` y `0.051713`—
porque son dos usos distintos: amarre de varilla y amarre de estribos. **26 casos.**

> El modelo debe permitirlo. Y refuerza que **la línea se identifica por posición,
> no por la clave del hijo** (§1).

### La unidad se arrastra sin normalizar

Los fletes entran con `serv` en minúscula, tal como está en su catálogo de origen.
**La matriz hereda la unidad, con sus inconsistencias.**


## 8 Análisis de básicos de conceptos — `ANALISIS_DE_BASICOS_CONCEPTOS.xlsx`

**2,568 filas.** Misma estructura que §7, pero **contiene tres explosiones, no
una** — lo dice la columna `Origen`:

| `Origen` | Filas | Padres | Qué es |
|---|---|---|---|
| `Concepto` | 2,189 | 468 | La matriz de conceptos |
| `Material` | 267 | 89 | Los compuestos — **idéntico a §7** |
| `ManoDeObra` | 112 | 39 | **Las cuadrillas** |

> `Origen` es **la categoría del padre**, no la del hijo. Es el campo que dice a qué
> reporta el monto (`CONOCIMIENTO.md` §10.5).

### Cierra al centavo, y sin deriva

| Comprobación | Resultado |
|---|---|
| Conceptos del presupuesto | 471 |
| Con explosión | **467** |
| Suma de la explosión contra el `Precio unitario` del presupuesto | **Los 467 cuadran** |
| Cuadrillas contra el `Costo unitario` de mano de obra | **Las 39 cuadran** |

**Cero diferencias.** No hay PU congelado ni desfasado: OPUS recalcula (§1).

Los **4 conceptos sin explosión** son los de precio cero: `IGAS-02131`,
`IGAS-02132`, `ISN-02061` y `ACC-00003`. Pendientes de costear (`CONOCIMIENTO.md` §4.1).

### El `%MO` comprobado al peso

```
CUAD-001   MOCA-001  Peón          2 JOR  ×   560  = 1,120
           MOCA-014  Albañil       1 JOR  ×   760  =   760
                                    suma de jornales = 1,880
           MOCA-110  Contratista  0.1 %MO ×  1,880 =   188
```

Las 39 cuadrillas llevan **exactamente una línea `%MO`**, siempre al `0.1`.

> **Trampa del cargador: en las líneas `%MO`, la columna `Costo` no es un precio de
> catálogo — es la base ya calculada.** Vale 1,880 en una cuadrilla, 560 en otra,
> 1,320 en otra. **La misma columna significa cosas distintas según la unidad.**

Y la unidad viene como `(%)mo` — tercera forma de escribirla, junto a `%mo` y
`%MO`.

### Ningún concepto usa una cuadrilla

Los hijos de concepto son **Material 1,693 · Contrato 461 · Flete 35**. Ni uno solo
es cuadrilla.

> Las 39 cuadrillas existen, están explotadas y cuadran — **pero nada las
> referencia.** El trabajo se carga como destajo, no como jornal.

Confirma D-12 en datos: **la cuadrilla es modelo de capacidad, no de costo.** Su
explosión sirve para saber cuánta gente y cuánto rinde, no para formar el PU.

### El concepto mezcla categorías, igual que el compuesto

```
ACA-01010   Aplanado fino en muros                        $71.71
  MEZ-03010  Mortero estuco blanco   1.05 M2  Material     21.71
  MOA-00112  MO finas interiores     1.00 M2  Contrato     50.00
```

Y llega a los compuestos: `MEZ-03010` es un compuesto de material, que a su vez se
abre. **El árbol completo va de concepto a compuesto a insumo simple.**


## 9 Los vocabularios se derivan, no se cargan

Cuatro de los cinco vocabularios que los catálogos viejos aportaban **ya están
dentro de los datos de OPUS 2025**. No hay que pedirlos ni mantenerlos aparte.

### Qué reemplaza a qué

| Vocabulario viejo | Se reemplaza con | Resultado |
|---|---|---|
| `Catalogo_de_unidades` (16) | Las unidades en uso en los catálogos vigentes | **17 en uso**, todas en el catálogo salvo `(%)mo` |
| `CATALOGO_DE_NIVELES` (15) | Las filas `Subcapítulo` del presupuesto, con su `Nivel ERP` | **15** — coinciden |
| `CATALOGO_DE_ETAPAS` (50) | Las filas `Nivel 2` del presupuesto | **52** — aparecen las tres que faltaban |
| `CATALOGO_DE_FAMILIAS` (35) | Los campos `Familia` y `Subfamilia` de los cuatro catálogos de insumo | **50** familias y **243** subfamilias, por categoría |
| `CATALOGO_DE_CONTRATISTAS` (29) | **Nada.** No es derivable | Único que habría que pedir, y solo al llegar a contratación |

### Las tres etapas que faltaban

Derivarlas resolvió el desajuste sin pedir nada:

| Clave | Descripción | Usos |
|---|---|---|
| `ECO-00029` | Iluminación / Accesorios | 3 |
| `ECO-00035` | Cancelería AZ | 3 |
| `ECO-00051` | Cubiertas mármol y granito | 7 |

**No eran registros borrados**, como se supuso al ver los huecos en la numeración:
son etapas nuevas que el catálogo viejo no alcanzó.

### La regla

> **Si el vocabulario se puede derivar del uso, el catálogo deja de ser entrada: es
> un subproducto de la carga.**

Siempre está completo, nunca tiene huérfanos y **no se desactualiza** — que es
exactamente lo que le pasó al de etapas.

### Lo que se pierde al derivar

| Se pierde | Detalle |
|---|---|
| Lo que **aún no se usa** | Una unidad válida que nadie usó todavía no aparece |
| Los **atributos que no están en los datos** | La clave `FML-000xx` y el prefijo de familias; el sinónimo legible de unidades |

Por eso el catálogo de unidades **sí se conserva**: aporta el nombre legible
—`M2` → *Metro Cuadrado*— que ningún dato de uso contiene.


## 10 Cuadrilla y rendimiento: lo que OPUS no entrega

OPUS 2025 **no relaciona el trabajo con una cuadrilla ni guarda su rendimiento.** El
catálogo de la generación anterior sí lo hacía, en las columnas `CUADRILLA`,
`RENDIMIENTO TEORICO` y `RENDIMIENTO REAL`.

### Solo dos datos no son derivables

De las 21 columnas que tendría una tabla completa, **19 salen de los catálogos o se
calculan**: descripción, unidad, precio, familia, costo de cuadrilla, rendimiento
calculado, jornadas por unidad, la razón entre teórico y calculado.

**Los únicos dos que no existen en ningún lado son `Cuadrilla` y `Rendimiento
teórico`.**

### `Rendimiento calculado` ya tenía fórmula — D-404 la inventó mal

**Corrige D-404.** La fórmula que D-404 propuso (`Rendimiento teórico`
× `Unidades ejecutoras`) nunca hacía falta: `Rendimiento calculado` ya
estaba definido, desde antes de esta sesión, en `CONOCIMIENTO.md` §6.2
— `Costo de la cuadrilla` ÷ `Precio del destajo` —. No pasa por
`Unidades ejecutoras` en absoluto: es el precio ya negociado visto al
revés, para **una** cuadrilla tal como cuesta hoy. D-404 lo redefinió
sin cruzarlo contra esa sección, y el resultado no coincidía con
ninguno de los cuatro rendimientos que §6.2 ya distingue (Calculado,
Teórico, Real, Requerido).

**Lo que D-404 de verdad necesitaba nombrar era otra fórmula, para otro
campo:** cómo entra `Unidades ejecutoras` en la *duración* de
`calculada_rendimiento` — `Duración` = `Cantidad` ÷ (`Rendimiento
teórico` × `Unidades ejecutoras`) —, que no toca `Rendimiento
calculado`. Y el lado que motivó la confusión (`PROGRAMA_ZAFIRO.xlsx`,
cantidad entre duración capturada a mano) ya tenía nombre en §6.2 sin
un caso real que lo probara: es `Rendimiento Requerido`. Con números
reales de los dos lados, `CONOCIMIENTO.md` §6.2 (D-406).

**Los dos límites de alcance, dato del usuario, siguen de pie —solo
cambia a qué fórmula se atan—:** `Rendimiento calculado` solo existe
cuando el destajo tiene su propia línea de mano de obra en la matriz
—si un concepto se contrata completo (`preestablecida_nivel`, B-48,
sin línea `MO-` propia, como Cancelería o Domos, D-400), no hay nada
que dividir—; y el mismo mecanismo aplica a maquinaria, no solo a
cuadrillas de personas.

### Es una semilla, no un cargador

> OPUS no entrega esos dos datos **y nunca los va a entregar.**

Se cargan **una sola vez** para no perder lo que ya existía, y de ahí en adelante
viven en el ERP y se editan ahí. Un cargador implica que el dato llega de afuera
cada vez; este llega una vez.

`SEMILLA-cuadrilla-rendimiento.xlsx` — 265 filas, tres columnas más referencias.

| Origen | Filas |
|---|---|
| Migrado del catálogo anterior | 260 |
| Completado con el factor de su cuadrilla | 5 |

### Dónde viven

**Son dos atributos del trabajo, uno a uno.** Cada destajo tiene su cuadrilla y su
rendimiento teórico. No hace falta tabla aparte: son dos campos más — exactamente
como los tenía el catálogo anterior.

### La semilla, guardada — mismo criterio que `TESTIGO_MATERIAL`

`SEMILLA-cuadrilla-rendimiento.xlsx` llega como archivo aparte de este cerebro;
dato del usuario, se guarda aquí para no depender de que el archivo original
siga disponible. Mismo principio que `TESTIGO_MATERIAL` (§12): **se carga con lo
ya cruzado contra ejecución real, y crece fila por fila** — no un volcado
mecánico de las 265 filas completas.

| Clave | Descripción | Cuadrilla | Rendimiento teórico | Unidad | Costo unitario |
|---|---|---|---:|---|---:|
| `MOA-00001` | MO repellado muro 0-3.00 | `MOCU-005` | 18.53 | M2 | $85.00 |
| `MOA-00020` | MO repellado muro fachada 0-3.00 | `MOCU-005` | 18.53 | M2 | $85.00 |
| `MOA-00022` | MO repellado muro fachada +3.00 | `MOCU-005` | 15.00 | M2 | $105.00 |
| `MOC-10040` | MO gualdra chica | `MOCU-033` | 4.77 | PZ | $330.00 |
| `MOE-01008` | MO ranura acometida voz y datos | `MOCU-009` | 30.00 | PZ | $50.00 |
| `MOE-01013` | MO ranura TV | `MOCU-009` | 2.50 | PZ | $50.00 |
| `MOE-01015` | MO salida spot muro | `MOCU-009` | 0.96 | PZ | $130.00 |
| `MOE-01041` | MO ranura acometida principal a 220V | `MOCU-009` | 1.56 | PZ | $160.00 |
| `MOE-01111` | MO ranura eléctrica contacto | `MOCU-009` | 1.56 | PZ | $80.00 |
| `MOE-01121` | MO ranura eléctrica apagador | `MOCU-009` | 1.56 | PZ | $80.00 |
| `MOE-02010` | MO muro de tabique - hilo | `MOCU-005` | 10.50 | M2 | $150.00 |
| `MOE-02020` | MO castillos K1 (15x15) | `MOCU-005` | 12.12 | M | $130.00 |
| `MOE-02021` | MO castillos K2 (15x15) | `MOCU-005` | 12.12 | M | $130.00 |
| `MOE-02027` | MO castillos K7 (15x20) | `MOCU-005` | 11.25 | M | $140.00 |
| `MOE-02102` | MO cadena CE2 (15x20) | `MOCU-005` | 10.50 | M | $150.00 |
| `MOE-02211` | MO armado de losa nervada | `MOCU-005` | 5.57 | M2 | $283.00 |
| `MOE-02212` | MO descimbrado de losa nervada | `MOCU-005` | 31.50 | M2 | $50.00 |
| `MOE-02213` | MO armado de losa maciza | `MOCU-005` | 5.57 | M2 | $283.00 |
| `MOE-02214` | MO descimbrado de losa maciza | `MOCU-005` | 31.50 | M2 | $50.00 |
| `MOE-02217` | MO armado y cimbrado losa 4.20 | `MOCU-005` | 5.57 | M2 | $283.00 |
| `MOE-02311` | MO armado y colado escalera | `MOCU-005` | 6.19 | PZ | $254.50 |
| `MOE-02312` | MO descimbra escalera | `MOCU-005` | 31.50 | M2 | $50.00 |
| `MOS-01030` | MO bajadas sanitarias | `MOCU-010` | 1.39 | PZ | $225.00 |
| `MOS-02040` | MO conexión san minisplit | `MOCU-025` | 0.78 | PZ | $1,000.00 |
| `MOS-07030` | MO conexión san lavamanos | `MOCU-010` | 2.50 | PZ | $50.00 |
| `MOS-07060` | MO conexión san tarja cocina | `MOCU-010` | 2.50 | PZ | $50.00 |
| `MOC-01010` | MO losa de cimentación | `MOCU-005` | 6.85 | M2 | $230.00 |
| `MOC-12010` | MO zapata ZA-1 (100x100x25) | `MOCU-005` | 3.42 | PZ | $460.00 |
| `MOE-02022` | MO castillos K3 (15x30) | `MOCU-005` | 10.50 | M | $150.00 |
| `MOE-02028` | MO castillos K8 (15x40) | `MOCU-005` | 9.84 | M | $160.00 |
| `MOE-02101` | MO cadena CE1 (15x20) | `MOCU-005` | 11.25 | M | $140.00 |
| `MOC-02010` | MO firme de concreto de 10 cm | `MOCU-005` | 15.75 | M2 | $100.00 |
| `MOA-09020` | MO columna forrada | `MOCU-005` | 1.89 | PZ | $835.00 |
| `MOE-05010` | MO zapata aislada (60x60x20) pérgola | `MOCU-005` | 2.63 | PZ | $600.00 |
| `MOA-01510` | MO fabricación de asador | `MOCU-005` | 0.63 | PZ | $2,500.00 |
| `MOA-02510` | MO forrado de asador con cantera | `MOCU-008` | 0.68 | PZ | $2,300.00 |
| `MOA-00115` | MO finas en muros exteriores 0-3.00 | `MOCU-005` | 31.50 | M2 | $50.00 |
| `MOA-05021` | MO chaflán teja | `MOCU-005` | 26.25 | M | $60.00 |
| `MOE-02016` | MO muro de sillar - hilo | `MOCU-005` | 8.29 | M2 | $190.00 |
| `MOE-02025` | MO castillos K9 (15x25) aparente | `MOCU-005` | 9.84 | M | $160.00 |
| `MOE-02103` | MO cadena CE1 aparente (20x25) | `MOCU-005` | 9.84 | M | $160.00 |
| `MOE-02202` | MO cadena CD-1 aparente (20x25) | `MOCU-005` | 9.84 | M | $160.00 |
| `MOA-00002` | MO repellado muro +3.00 | `MOCU-005` | 15.00 | M2 | $105.00 |
| `MOA-00010` | MO repellado plafón 0-3.00 | `MOCU-005` | 15.00 | M2 | $105.00 |
| `MOA-00011` | MO repellado plafón +3.00 | `MOCU-005` | 14.32 | M2 | $110.00 |
| `MOA-00112` | MO finas interiores en muros 0-3.00 | `MOCU-005` | 31.50 | M2 | $50.00 |
| `MOA-00113` | MO finas interiores en muros +3.00 | `MOCU-005` | 27.16 | M2 | $58.00 |
| `MOA-00114` | MO finas en muros de fachada 0-3.00 | `MOCU-005` | 31.50 | M2 | $50.00 |
| `MOA-00120` | MO finas en plafón 0-3.00 | `MOCU-005` | 30.29 | M2 | $52.00 |
| `MOA-00121` | MO finas en plafón +3.00 | `MOCU-005` | 26.25 | M2 | $60.00 |
| `MOA-00211` | MO boquillas interiores | `MOCU-005` | 39.38 | M | $40.00 |
| `MOA-00212` | MO boquilla fina estuco vanos | `MOCU-005` | 315.00 | M | $5.00 |
| `MOA-00213` | MO boquilla gruesa pretil | `MOCU-005` | 39.38 | M | $40.00 |
| `MOA-01010` | MO muro chapeado piedra | `MOCU-005` | 2.72 | M2 | $580.00 |
| `MOA-02010` | MO pórfido en cocheras | `MOCU-005` | 19.69 | M2 | $80.00 |
| `MOA-02020` | MO boquilla pórfido | `MOCU-005` | 52.50 | M2 | $30.00 |
| `MOA-02030` | MO rodapié cantera 60 cm | `MOCU-005` | 8.56 | M | $184.00 |
| `MOA-02031` | MO rodapié cantera 20 cm | `MOCU-005` | 35.00 | M | $45.00 |
| `MOA-02070` | MO columna de cantera | `MOCU-005` | 1.58 | PZ | $1,000.00 |
| `MOA-02080` | MO forjado de jardinera | `MOCU-024` | 21.00 | M | $75.00 |
| `MOA-02081` | MO zoclo pórfido en laja | `MOCU-008` | 35.00 | M | $45.00 |
| `MOA-05020` | MO chaflán azotea | `MOCU-005` | 39.38 | M | $40.00 |
| `MOE-02201` | MO cadena CD-1 (15x25) | `MOCU-005` | 11.25 | M | $140.00 |
| `MOE-31010` | MO registros sanitarios | `MOCU-005` | 4.50 | PZ | $350.00 |
| `MOE-31110` | MO tapa registros sanitarios/cisterna | `MOCU-005` | 15.75 | PZ | $100.00 |
| `MOP-00301` | MO murete de instalaciones | `MOCU-005` | 0.55 | PZ | $2,850.00 |
| `MOE-02215` | MO armado y cimbrado losa 3.00 | `MOCU-005` | 5.57 | M2 | $283.00 |
| `MOE-02216` | MO descimbrado de losa 3.00 | `MOCU-005` | 31.50 | M2 | $50.00 |
| `MOE-02218` | MO descimbrado de losa 4.20 | `MOCU-005` | 31.50 | M2 | $50.00 |

**69 filas, todas `Origen=migrado`** — ninguna de las 5 filas `completado` (factor
1.085 de `MOCU-023`/`MOCU-005`) se ha cruzado todavía contra ejecución real.

### El costo de la cuadrilla no era anónimo — tres niveles en `ANALISIS_DE_BASICOS_CONCEPTOS.csv`

Dato del usuario, buscar si existe un catálogo de cuadrillas con precio
propio. Existe, y ya estaba cargado: §8 ya lo señalaba en una fila
(`Origen=ManoDeObra`, 112 filas, 39 padres, "Las cuadrillas") sin
desarrollarla. Son tres niveles, no uno:

```
MOCA-xxx         rol/oficio con su jornal     Albañil $760, Ayudante $560,
  ↓ compone                                   Fierrero $760… (44 roles)
MOCU-xxx/CUAD-   cuadrilla (39 en total)      MOCU-005 = 1 Albañil + 1
  ↓ liga (semilla, tabla de arriba)            Ayudante + 10% contratista
MOA-/MOE-/MOC-…  destajo con su teórico       MOE-02020 (castillo K1) → MOCU-005
```

`MOCU-005` suma **$1,452.00/jornada** exacto (760 + 560 + 132 de
contratista) — el mismo número que el ejemplo de `CONOCIMIENTO.md` §6.2
ya usaba sin decir de dónde salía. De las 39 cuadrillas con composición
propia, solo 14 están ligadas hoy a algún destajo en la semilla
cargada; **25 existen y nadie las usa todavía.**

**Primera validación: castillo K1 (`ALAMO 18`) cierra exacto, 1.00 cuadrilla.**
`MOE-02020` a 12.12 M/día contra las 339.20 M de sus tres niveles da 28.0 días
teóricos — que coinciden con los 28 días reales activos que quedan una vez
descontados los dos huecos que `CONOCIMIENTO.md` §11.14/D-385 ya había
encontrado (56 de los 84 días de calendario). Confirma el rendimiento de la
semilla y el método de huecos, los dos a la vez, con el mismo caso.
`CONOCIMIENTO.md` §11.14.

**Segundo uso: primer programa completo de prototipo, 30 semanas para
Diamante.** Las 16 filas nuevas (cimentación, K3/K8/CE-1, firme, zapatas,
barda perimetral, asador) reconstruyen Cimentación→Azotea en 21 semanas
y encuentran que eléctrica en muro PB necesita 2 cuadrillas —no 1— para
no repetir la deficiencia de calidad de D-387/D-388. `CONOCIMIENTO.md`
§11.14.

**Tercer uso: contra el plan manual de Zafiro 1.0, no contra ejecución
real.** Las 24 filas nuevas (acabados, boquillas, pórfido, registros
sanitarios, murete) salen al cruzar las 317 líneas de
`PROGRAMA_ZAFIRO.xlsx` contra esta semilla — 50 pares concepto×`MO-` en
total. A
diferencia de castillo K1, este cruce no cierra limpio: mediana 0.83-1.25
cuadrillas implícitas según el filtro, con 67-74% fuera de una banda
razonable. No es que el rendimiento esté mal — es que un plan manual no
pasa por rendimiento × cuadrillas de forma sistemática, que es justo la
brecha que un programa calculado cerraría. `CONOCIMIENTO.md` §11.14.

**Cuarto uso: completar los conceptos "act" que el tercer uso no pudo
ver.** `MOE-02215`/`MOE-02216` (losa maciza 3.00) y `MOE-02218` (losa
nervada 4.20) llegan al comprobar cuadrillas concepto por concepto
—`MOE-02217` ya estaba—: los conceptos en unidad "act" (lump sum) no
tienen unidad que coincida con ninguna línea `MO-`, así que el tercer
uso los dejó fuera sin darse cuenta. `CONOCIMIENTO.md` §11.14.

**Quinto uso: el costo del destajo, comprobado contra duración real y
de diseño a la vez, con el mismo concepto.** Dato del usuario. Castillo
K1 conecta, con números reales, el costo y el tiempo —
`CONOCIMIENTO.md` §6.2 trae la tabla completa. El caso real
(`ALAMO 18`) cierra los tres rendimientos entre 11.17 y 12.12; los dos
tramos de diseño (`PROGRAMA_ZAFIRO.xlsx`) se disparan en direcciones
opuestas (18.13 y 4.20) — confirma por el lado del dinero lo que D-397
ya probaba por el lado del tiempo: el plan manual no pasa
sistemáticamente por esta tabla, el destajo no está mal fijado.
`CONOCIMIENTO.md` §6.2 (D-406).

## 10b El prefijo no determina la familia — segunda prueba

Ya estaba probado con las 79 claves `AUX-` que son `Tipo = Material`. Contando
prefijos contra el catálogo de 35 familias sale una evidencia mayor:

| Catálogo | Prefijos sin familia |
|---|---|
| Conceptos (470) | **287 · 61%** — `IEC` `EST` `ISN` `IHD` `IGAS` `MSA` `BAP` |
| Trabajos (265) | **265 · 100%** — `MOA` `MOE` `MOS` `MOH` `MOG` `MOC` `MOP` `SUB` `MOO` |

> **El catálogo de familias es de insumos.** Ni conceptos ni trabajos tienen familia
> propia ahí, y por eso la del concepto se deriva del trabajo que usa.

### Cada catálogo declara su familia: no se deriva de nada

**Materiales, mano de obra y trabajos traen columnas propias `Familia` y
`Subfamilia`, y ninguna está vacía:**

| Catálogo | Filas | Sin familia | Familias | Subfamilias |
|---|---|---|---|---|
| Materiales | 387 | **0** | 18 | 49 |
| Trabajos | 265 | **0** | 17 | 75 |
| Mano de obra | 97 | **0** | 10 | 8 |
| **Conceptos** | 470 | — | **no tiene columna** | — |

> **El prefijo no determina la familia ni la subfamilia: la familia está declarada.**
> La coincidencia de 35 prefijos con 35 nombres en `CATALOGO_DE_FAMILIAS` es un
> catálogo de nomenclatura de claves, no el origen de la clasificación.

**El único que no declara familia es el concepto** — por eso la suya se deriva del
trabajo que usa, y por eso su 8% queda sin cubrir. Los demás no derivan nada.

### El catálogo está desincronizado con el uso: 38 contra 35

De las 38 familias en uso, **22 no están en el catálogo**. Y se parten en dos:

**Nueve difieren sólo por el acento** — el catálogo las guarda sin acentuar:

```
uso «Albañilería»        catálogo «Albañileria»
uso «Cancelería»                  «Canceleria»
uso «Carpintería»                 «Carpinteria»
uso «Eléctrico»                   «Electrico»
uso «Herrerías»                   «Herrerias»
uso «Hidráulico»                  «Hidraulico»
uso «Impermeabilización»          «Impermeabilizacion»
uso «Pérgolas»                    «Pergolas»
uso «Pétreos»                     «Petreos»
```

> **No son familias distintas: es la misma escrita de dos formas.** Sin normalizar
> acentos, cualquier agrupación las cuenta por separado — **incluida la dispersión del
> paramétrico**, que agrupa por familia.

**Regla: la forma acentuada es la canónica**, porque es la que usa el dato real. El
catálogo se corrige, no el uso. Y la comparación de familias normaliza acentos
siempre, igual que la de unidades normaliza mayúsculas.

**Trece faltan de verdad**, y diez son de mano de obra: `Ayudantes` ·
`Contratistas` · `Cuadrillas` · `Laboratoristas` · `Oficiales calificados` ·
`Oficiales de albañilería` · `Oficiales de urbanización` · `Operadores` · `Peones` ·
`Supervisores`. Más tres de material: `Elemento Estructural` · `Loseta` · `Mezclas`.

> El catálogo nunca cubrió la mano de obra. **Las familias existen y se usan; lo que
> falta es el catálogo que las declare.**

### El eje de clasificación no es el mismo en los dos

| | Familia | Subfamilia |
|---|---|---|
| **Materiales** | Tipo de material — Concretos, Aceros | Detalle del material |
| **Mano de obra** | **Tipo de trabajador** — Peones, Oficiales, Cuadrillas | **Especialidad** — Albañilería, Instalaciones, Topografía |

Las 31 subfamilias de mano de obra lo confirman: `Ayudantes → Topografía`,
`Cuadrillas → Equipo y Maquinaria`. **No es la jerarquía de material con otros
nombres: es otra clasificación.**

> **Y por eso no hay nada que cargar.** Las 10 familias de mano de obra ya están
> declaradas en su propio catálogo, con sus 8 subfamilias. Lo que falta no son datos:
> es que `CATALOGO_DE_FAMILIAS` no es el catálogo maestro de familias que su nombre
> sugiere — **es la nomenclatura de prefijos de clave de los materiales.**

## 11 La prueba de ida y vuelta

`OPUS → canon → OPUS`. Es lo que valida si `LENGUAJE.md` está bien escrito o solo
bien redactado.

> **Renombrar columnas y devolverlas no prueba nada.** La prueba real es
> **reconstruir lo derivable desde el canon**, sin copiarlo del original.

### Resultado

| Columna | Reconstruida desde clave, cantidad, precio y profundidad |
|---|---|
| `Total` | ✅ **3,224 de 3,231** · máxima diferencia $0.03 (redondeo) |
| `%` | ✅ **3,231 de 3,231**, exacto |
| `Ingenieria ERP` | ❌ **No se pudo** |

Las dos primeras confirman que el canon aguanta: **con cuatro campos se reconstruye
todo el aparato numérico del presupuesto.**

### `Ingenieria ERP` no es generable

Se probaron tres reglas de generación y ninguna reproduce el original. Y los datos
se contradicen entre sí:

```
ECO-00006  Estructura PB     1020600
  EST-02010  Muro tabique    1020601   ← segmento propio
  EST-02080  Muro sillar     1020602

ECO-00002                    1010200
  ISN-01010  Vertedero       1010200   ← sin segmento, hereda
  ISN-01020  Lavadero        1010200
```

**A veces el concepto recibe segmento y a veces no**, y no se encontró qué lo
determina.

> Refuerza por otra vía lo ya decidido —esa columna no se importa— pero **corrige la
> promesa de generarla**: hoy no se puede.
>
> O se obtiene la regla del ERP externo, o **el código se arrastra del archivo
> original** en vez de calcularse.

---

## 12 `TESTIGO_MATERIAL` — qué insumo sirve de testigo para verificar cada concepto

`MODELO.md` §5a necesita, para `ALERTA(tipo=estimacion_sin_respaldo_material)` y su
espejo `consumo_material_sin_respaldo_avance`, saber **qué insumo confiar como
testigo de cada concepto** — el mismo criterio de campo que ya distinguió cemento de
tabique en `CONOCIMIENTO.md` §11.17. Con un solo caso completo (`EST-02010`) eso era
«criterio de quien configura la revisión, caso por caso»; con diecisiete conceptos
reales cruzados contra cinco meses de almacén (`CONOCIMIENTO.md` §11.20), ya es
catálogo.

### Es semilla, no derivado

**Qué insumo es confiable como testigo no sale de ningún catálogo ni se calcula —se
confirma cruzando contra almacén real, obra por obra, hasta que el patrón se
repite.** Igual que `SEMILLA-cuadrilla-rendimiento.xlsx` (§10): OPUS no lo sabe y no
lo va a saber, porque no es un dato de OPUS — es evidencia acumulada de este cerebro.
Se carga con lo ya confirmado hoy y **crece fila por fila** conforme se cruzan más
conceptos; nunca se recalcula desde cero ni se repite este cruce a mano.

| Concepto | Insumo testigo | Confiabilidad | Evidencia |
|---|---|---|---|
| `EST-02010` (muro tabique 14cm) | `PET-00001` (tabique) | **Confirmado** | Exacto — 6,000/6,000 PZ, abril (`CONOCIMIENTO.md` §11.16) |
| `EST-02010` (muro tabique 14cm) | `ADH-00005` (cemento) | **Confirmado** | 0.2% de diferencia en acumulado, 4 meses, 8 eventos reales (§11.17, D-375) |
| `EST-01060` (losa de cimentación) | `CON-00001` (concreto premezclado) | **Confirmado** | Exacto — 37.330/37.330 M3, abril (§11.16) |
| `EST-02011` (muro tabique, 3er nivel) | `ADH-00005` | Consistente | -1.0%. Cruzado contra ingeniería (D-380): las tres fuentes coinciden exactas —31.03 M, 100% completo—, sin ambigüedad; base chica (10 sacos, un evento) es lo único que lo deja en `Consistente` y no `Confirmado`, mismo criterio que `EST-02320`/`07010`/`07011` (§11.20, D-380) |
| `EST-02110`/`02120`/`02130`/`02170`/`02180` (castillos K1-K8), `EST-02310` (cadena CE-1) | `ADH-00005` | **Confirmado** | -22.3% a +6.8% por concepto en `ALAMO 18`; a escala completa (todos los lotes, 5 meses) -7.4% a -14.1% — dentro de lo esperado. Castillo K1 mostró +141.7% en una primera lectura — **corregido: era avance incompleto en una sola fuente (`grid_AvanceOPEventosOpr`, 32.8% de un diseño de 339.20 M), no exceso de material** (`CONOCIMIENTO.md` §11.20) |
| `ALB-01210` (repello fachada) | `ADH-00005` | **Confirmado** | +15.5% cruzado contra ingeniería/`PRECIO_REAL` (192.53 M, ambas coinciden) — el +18.9% original usaba solo la escala de `grid_AvanceOPEventosOpr` (187 M, 97.1%). Volumen decente (34 sacos, tres eventos), tres fuentes de acuerdo — sube de `Consistente` (§11.20, D-380) |
| `EST-02320` (cadena CE-2), `EST-07010`/`07011` (columnas CM-1) | `ADH-00005` | Consistente | Un solo evento, base pequeña (1-8 sacos) — el % es ruido de redondeo a saco entero, **confirmado, no artefacto de fuente incompleta: las tres fuentes de avance coinciden 100%** (§11.20, D-378) |
| `ALB-01010` (repello muro 3.00) | `ADH-00005` | **Confirmado** | +15.5% cruzado contra `PRECIO_REAL` (60.2% avanzado) — el +109.1% original era `grid_AvanceOPEventosOpr` viendo solo 33.2% del avance real, mismo patrón que castillo K1. **Corrige D-376** (§11.20, D-378) |
| `ALB-01212` (repello muros fachada 3.00) | `ADH-00005` | **Confirmado** | Rate correcto —el testigo funciona—, pero **anomalía real sin resolver**: las tres fuentes de avance coinciden en ~100% completado y la orden no tiene un solo movimiento de almacén, de ningún insumo. Caso limpio para `estimacion_sin_respaldo_material` (§11.20, D-378) |
| `ALB-01110` (repello plafond 3.00) | `ADH-00005` | Consistente | Déficit -48% a -59% bajo cualquier lectura, nunca exceso — consistente con material aún por surtir. Nota sin resolver: `PRECIO_REAL` supera a la ingeniería para este concepto, único caso así (§11.20, D-378) |
| `ALB-01012` (repello muro 3.00, código distinto de `ALB-01212`) | `ADH-00005` | **Confirmado** | Rate confirmado, dato del usuario: es cemento, el de su propia matriz genérica (`MEZ-07010`) — no el mortero de la ingeniería específica del lote, desactualizada (mismo patrón que B-68/D-308). +2.8% contra el diseño completo, casi exacto. El +326% contra `PRECIO_REAL` (24.1% avanzado) **no es ruido — es el caso real de `consumo_material_sin_respaldo_avance`** (B-79, D-379): material adelantado a todas las fuentes de avance a la vez (§11.20, D-379) |
| `ECO-00004` + familia `IEC-` (habilitado eléctrico) | `ELE-00001` (poliducto) | Consistente | 72.8% del alcance completo (13.83→10.07), 169.2% del esperado ponderado — patrón «avance sin estimar» (D-379) del lado del material adelantado; confirmado con accesorio `ELE-00003` (chalupa, 78.7%). Prototipo verificado: es Diamante pese a etiqueta «Zafiro Plus» en almacén — método de identificación por contenido, D-121 (§11.20, D-381) |
| `ECO-00003` + familia `IHD-` (habilitado hidráulico) | `HID-00004` (codo) | **Confirmado** | 100.0% exacto del alcance completo (111.00/111.00) — triple confirmado con `HID-00024` (tubo, 100.0%) y `HID-00012` (tee, 100.0%) (§11.20, D-381) |
| `ECO-00005` + familia `IGA-` (habilitado gas) | `HID-00025`+`IGS-00014` combinados | **Confirmado** | 96.9% del esperado ponderado (83.4% del alcance completo) — dos claves de ingeniería para el mismo producto físico («2024446»), ambas reales, se suman (distinto de `HID-00411`, donde una clave nunca se usa); confirmado con accesorio `ACE-00001` (sellador, 92.2%) (§11.20, D-381) |
| `ECO-00002` + familia `ISA-` (habilitado sanitario) | `HID-00411` (la ingeniería lo captura como `HD-00411`, misma trampa de D-371) | **Confirmado** | Testigo confiable —accesorios `HID-00135`/`SAN-00002` al 100.0%/125.6%— pero **anomalía real, tercer caso de `estimacion_sin_respaldo_material` (B-70)**: solo 41.7% del alcance completo; se emitió una sola vez (21/04/2026, `ECO-00002`) y nunca para `ISA-00110`/`00150`/`00210`, pese a que facturan 86.6%-100% de avance (§11.20, D-382) |

**Los diecisiete conceptos originales (estructura) ya quedaron cruzados contra
ingeniería, uno por uno** (D-377 a D-380). Ninguno queda pendiente de esa
validación — lo que sigue abierto (`ALB-01012` como caso real de B-79) es
interpretación de campo, no falta de dato. **Extendido a instalaciones (D-381/
D-382):** eléctrica, hidráulica y gas confirman con el mismo método sobre un
dominio compuesto (concepto con varias sub-actividades, alcance en $ ponderado
por `O/Requerida`); sanitaria repite, por tercera vez y por primera fuera de
estructura, el patrón que cierra B-70 — avance alto sin el material que lo
respalde.

**Cómo se usa:** `estimacion_sin_respaldo_material` y `consumo_material_sin_respaldo_avance`
(`MODELO.md` §5a) solo corren en automático sobre pares marcados `Confirmado` o
`Consistente`. Los `Insuficiente` quedan documentados —para no repetir el cruce a
mano la próxima vez— pero no disparan alerta sola todavía: hace falta historia, no
solo una lectura, mismo criterio que ya frenó una regla automática de tamaño de
ventana en `MODELO.md` §5a.

```
TESTIGO_MATERIAL
  id
  concepto_id           FK Nodo (rol=concepto)                                firme — nuevo
  insumo_id             FK Nodo (rol=material) — el insumo testigo            firme — nuevo
  confiabilidad         enum: confirmado · consistente · insuficiente         firme — nuevo
  evidencia             texto — de qué corrida y con qué cifra sale           firme — nuevo
```


---
