# Unidades de Oro y contraste con la idea de paramétrico del cerebro

Se contrastó el libro `ORO_v18` (recalculado) y Zafiro v44 contra lo que el cerebro ya define: `1-mundo/CONOCIMIENTO.md` §5, `2-operacion/skills/erp-parametrico.md`, `1-mundo/MODELO.md` (`ENSAMBLE_PARAMETRO`) y `3-historia/MEMORIA.md` D-312 y D-622.

## 1. Unidades de Oro

### 1.1 Unidades del catálogo (Hoja1 de Oro, 425 conceptos)

| Unidad | Conceptos | Dimensional | Nota |
|---|---|---|---|
| `sal` (salida) | 154 | PUNTUAL | Instalaciones |
| `pza` | 140 | PUNTUAL | |
| `m2` | 68 | SUPERFICIE | |
| `m` | 55 | LINEAL | |
| `act` (actividad) | 5 | GLOBAL | Las 5 losas: **pieza global** cuyo m² está solo en el texto de la descripción |
| `ser` (servicio) | 2 | GLOBAL | Cancelería (43,023 y 39,490) |
| `m3` | 1 | VOLUMEN | Excavación manual 11.63 m³ |

Las 5 losas (`act`) son las únicas cuyo driver no está en una columna: se leen del texto (160, 45.60, 140, 80 y 24 m²). Es el punto frágil del modelo. Oro: 425 de 426 conceptos ya traen `Ruta paramétrica` en Hoja1, y 23 llevan `Origen = Agregado`.

### 1.2 Drivers y unidades de las hojas

| Hoja | Driver | Unidad | Base | Cómo se lee |
|---|---|---|---|---|
| MURO PB | m² de tabique PB | m² | 286 | Área de muro |
| MURO PA | m² de tabique PA | m² | 246.42 | Área de muro |
| MURO FACHADA | m² de acabado de fachada | m² | 470 | **No es muro**: es la suma de repellado y finas |
| PRETIL | m² de pretil | m² | 45 | |
| VANO | perímetro interior | m | 221.5 | |
| MARCOS EXTERIORES | perímetro de marcos | m | 89.9 | |
| LOSA (azotea) | m² de losa de azotea | m² | 104 | 80 + 24 |
| LOSA ENTREPISO | m² de entrepiso | m² | 185.6 | 45.6 + 140 |
| PISO PB | **losa de cimentación (desplante)** | m² | 160 | Coincide con la regla D-312 |
| PISO PA | losa de entrepiso | m² | 185.6 | |
| ESCALERA | escalones | pza | 24 | |
| ASADOR, PÓRFIDO, SILLAR | área | m² | 16 / 47 / 12.8 | |
| COCHERA | m² de pérgola | m² | 34.8 | Escalones a +60 % y +160 % |
| BARDA | ml | ml | 15 | Castillo por piezas |
| JARDÍN | m² con sello | m² | 77.5 | |
| CUBIERTA | ml de cubierta | ml | 3.85 | |
| CISTERNA | litros y piezas | L | 3,000 | |
| HIDROSANITARIAS, GAS, ELÉCTRICAS, EQUIPOS | salidas por aparato | sal | 41 / 9 / 186 / 7 | Más redes por m² de losa de cimentación (160) y grupos fijos |
| HERRERÍA, CARPINTERÍA, CANCELERÍA | piezas por grupo | m², m, pza, ser | — | Fijas y editables |
| OBRA EXTERIOR, OBRA COMPLEMENTARIA | — | global | — | Fijas y editables |

### 1.3 Problemas de unidades encontrados

1. **Se mezclan unidades bajo la misma etiqueta.** HERRERÍA rotula «Por salidas» a la puerta del cuarto de máquinas (3.22 **m²**), el barandal (6.41 **m**) y las piezas. El rótulo no dice la unidad real.
2. **El panel de Oro no trae unidad ni valor base de 9 hojas** (obra exterior, obra complementaria, hidrosanitarias, gas, eléctricas, equipos, herrería, carpintería y cancelería). Sin unidad no se calcula $/unidad ni se compara con otro prototipo.
3. **FACHADA como driver aparte (470 m²)** rompe la lógica de Zafiro, donde la fachada cuelga del mismo driver de muro. En Oro, si cambian los m² de muro PB o PA la fachada **no se entera**: es una captura independiente.
4. **PISO PA = 185.6 m²** contra 104 m² de azotea y 300 m² de construcción. 160 + 185.6 = 345.6, mayor que 300. Puede ser terraza o volado, pero **no está explicado**.
5. **Coladera de jardín: 77.5 m² por coladera** en Oro contra **22.5** en Zafiro. El parámetro se movió para que la base dé justo 1 coladera. Con la regla de Zafiro darían 4 (`ROUNDUP(77.5/22.5)`).
6. **Hay un grupo «APAGADOR/CONTACTO (MIXTO)»** de 5 salidas que no pertenece a ninguna unidad limpia.
7. **El m² de construcción (300) solo es informativo**, bien: coincide con la regla de que las instalaciones no escalan por m² total.

## 2. La idea de paramétrico: cerebro frente a Excel

| Idea | Cerebro | Excel (Zafiro / Oro) | Veredicto |
|---|---|---|---|
| Qué es | **Ensamble** = conceptos con cantidad propia; `tasa × divisor` | **Driver**: `cantidad = ratio base × driver`, con capas Sí/No | Equivalentes: la hoja de cada driver es un ensamble y su `$/unidad` es la tasa |
| Parámetro propio por ensamble | Cimentación con desplante, instalaciones con salidas | Piso PB con desplante (160); redes por m² de losa de cimentación; instalaciones por salidas | **Coincide y lo aplica** |
| La cantidad es receta | Un ensamble toma 1 regadera aunque haya 3 | Grupos con «salidas proyecto (EDITABLE)» y fijos editables | **Coincide** |
| Heredar mejor que capturar | Sí | Las cantidades base se leen de Hoja1 | Coincide. Salvo constantes escritas a mano (barda 1.95 y 8 piezas) |
| Referencia al **concepto**, no al renglón | Regla firme (§5.6) | `INDEX` por **número de fila** de Hoja1 | **Contradice.** Es el punto más débil |
| El ensamble no tiene que cuadrar | Un concepto puede estar en varios | Cada concepto cuenta una sola vez y se exige cuadre con Hoja1 | Diferente. El cuadre sirve como medida de **cobertura** (residuo), que el cerebro también define |
| Cohorte explícita | Obligatoria | No existe: se parametriza un prototipo | **Falta** |
| Dispersión junto al valor | Obligatoria | No existe: una sola muestra | **Falta** |
| Dos explosiones (costo y contratación) | Sí | Solo costo | Falta |
| Aprender de lo cuantificado | La tasa sale de casas medidas | Sale de un solo presupuesto | Parcial |

## 3. Contraste cruzado Zafiro vs Oro (la dispersión que falta)

Con dos prototipos se puede aproximar la dispersión que el cerebro exige (con n = 2 es indicativa, no estadística). $/unidad del driver, importes recalculados:

| Driver | Zafiro | Oro | Diferencia | Lectura |
|---|---|---|---|---|
| Losa de cimentación / desplante | 756 | 771 | **2 %** | Estable. Coincide con D-312 (CV 6 % en siete) |
| Losa de azotea con plafón / m² | 1,856 | 1,898 | **2 %** | Estable |
| Barda / ml | 1,753 | 1,829 | **4 %** | Estable |
| Asador / m² | 3,888 | 4,072 | 5 % | Estable |
| Cochera / m² | 2,061 | 2,176 | 6 % | Estable |
| Pórfido / m² | 541 | 602 | 11 % | Aceptable |
| Muro (todas las capas) / m² tabique | 1,625 | 1,396 | 14 % | Atención: Oro suma PB + PA + fachada (532 m²) |
| Sillar / m² | 733 | 1,008 | 37 % | Revisar contenido |
| Jardín / m² | 238 | 115 | 52 % | Parte fija de excavación |
| Cubierta / ml | 3,181 | 5,738 | 80 % | Revisar contenido |
| Vano / m | 138 | 60 | 79 % | Revisar contenido |
| **Pretil / m²** | 1,218 | 2,421 | **99 %** | **Sospechoso**: casi el doble |
| Cisterna / L | 7.37 | 7.37 | 0 | Idéntica: mismo precio y base copiados |

Precio por salida (mismo catálogo en ambos): WC $4,012 en Zafiro y $3,993 en Oro, lavamanos $2,231 en ambos, regadera $3,163 contra $3,166. **La salida es un parámetro estable.** Las redes por m² de losa sí varían: hidráulica $58.7 contra $74.5/m² (+27 %); eléctrica $7.1 contra $3.9/m².

## 4. Veredicto: qué tomar y qué no

**Se pueden tomar tal cual** (coinciden con el cerebro y son estables entre prototipos):
- Losa de cimentación por desplante, losa de azotea con plafón, barda por ml, asador, cochera, pórfido, y el costo por salida de cada aparato.
- La estructura de capas con interruptores y el patrón «fijo editable».

**Complementan al cerebro** (lo que el cerebro tiene en teoría y el Excel ya ejecuta): una receta funcional por driver con el escalamiento por piezas, escalones y umbrales (cochera, barda), que `ENSAMBLE_PARAMETRO` hoy no cubre. D-622 ya implementó otra cosa distinta (elementos como castillo, trabe, zapata y losa, con su receta de insumos), que es un piso más abajo y no choca.

**No tomar todavía:**
- Pretil, vano, cubierta, sillar y jardín de Oro: sus tasas se separan 37 a 99 % de Zafiro. Falta saber si es el contenido o el driver.
- Fachada como driver independiente y el piso PA de 185.6 m².
- La coladera a 77.5 m².
- Cualquier tasa sin cohorte ni dispersión: el cerebro la rechaza (regla 9 del skill).

## 5. Estado (2026-11-11)

Hechos en Zafiro v45 y Oro v19: **pasos 1 y 2** (llaves; parámetro, cohorte, dispersión y unidad real), los problemas 1 y 2 de §1.3 (unidades mezcladas y panel sin unidad) y el panel de MARCOS EXTERIORES de Zafiro. **Siguen abiertos:** 3 (fachada como driver aparte), 4 (piso PA de 185.6 m²), 5 (coladera a 77.5 m²), 6 (grupo mixto de apagador y contacto) y el reparto por capas de los otros 5 prototipos. Con el CV de n = 2, pretil, vano, jardín y cubierta salen «no usar» (CV de 41 a 56 %) y sillar «revisar» (22 %).

## 6. Propuesta original (pasos 1 y 2 ya hechos)

1. Reemplazar `INDEX` por fila por **clave de concepto** (`BUSCARX` sobre `Clave` + descripción), para cumplir §5.6.
2. Agregar a cada hoja de driver tres campos: **cohorte**, **dispersión** y **unidad real**.
3. Parametrizar los cinco prototipos restantes (Rubí, Zafiro Plus, Jade, Diamante −, Diamante +) para medir la dispersión con 7 muestras, como hace §5.7.
4. Mapear cada hoja a `ENSAMBLE_PARAMETRO`: `parametro` = desplante, salidas, piezas o m² de muro.
5. Resolver los cinco puntos abiertos de §1.3 antes de tomar las tasas de Oro.

## 7. Dispersión en los 7 prototipos (2026-11-11)

Archivos: `DISPERSION_7_PROTOTIPOS.xlsx` (hojas LEEME, TASAS y DETALLE, con SUMIFS auditables) y `medir_dispersion.py` (lo regenera desde Hoja1 de Zafiro v45).

**Qué se hizo y qué no.** No se armó un libro paramétrico por prototipo: el reparto en capas, fijos y divisiones de Zafiro y Oro es decisión manual de 44 versiones y no existe para los otros cinco. Se midió cada driver con una **misma regla automática** (filtro por subcapítulo, prefijo de clave o ruta, y divisor del concepto ancla o de los m² de la descripción), que reproduce el libro curado donde las definiciones coinciden.

| Driver | Tasa media | CV | Lectura |
|---|---|---|---|
| Losa de cimentación ($/m² de desplante) | 793 | 6.4 % | Utilizable. Reproduce Zafiro (756) y Oro (771) |
| Cimentación completa ($/m² de desplante) | 1,101 | 6.5 % (6.0 % poblacional) | Utilizable. **Reproduce D-312** |
| Estructura de muro ($/m² de tabique) | 631 | 4.9 % | Utilizable |
| Piso colocado ($/m²) | 544 | 2.7 % | Utilizable |
| Pórfido ($/m²) | 545 | 5.1 % | Utilizable. Reproduce el libro curado |
| Barda ($/ml) | 1,813 | 1.6 % | Utilizable, pero es el mismo concepto en los 7 |
| Pérgola de cochera ($/m²) | 1,760 | 1.6 % | Utilizable (n = 5: Rubí y Jade no tienen) |
| Cubierta de mármol ($/ml) | 2,756 | 5.7 % | Utilizable |
| Asador ($/m² de piso) | 3,021 | 9.6 % | Utilizable al límite |
| Losas de nivel ($/m² de losa) | 1,247 | 14.1 % | Revisar |
| Eléctricas ($/m² construido, referencia) | 377 | 9.1 % | Estable por m² |
| Hidrosanitarias y muebles ($/m² construido) | 423 | 11.1 % | Revisar |
| Gas ($/m² construido) | 34 | 19.6 % | Revisar |

**Lo que cambia respecto de la comparación con n = 2.** La losa de azotea (con plafón), la barda, el pórfido, el asador y la cochera se confirman estables con siete muestras. Los casos que con n = 2 salían «no usar» (pretil, vano, jardín, cubierta curada) **no se pudieron medir**: el divisor no existe en todos los prototipos. La cubierta, medida sin poyos, es estable (5.7 %); la diferencia con n = 2 venía del contenido del libro curado, no del diseño.

**Qué faltaba y ya está (sección 8).** La tasa por salida de las instalaciones.

## 8. Aparatos y salidas por puntos (2026-11-11)

Archivos: `TABLA_APARATOS_SALIDAS.xlsx` (hojas SISTEMAS, SIN_GRUPO, GRUPOS, ETAPAS, ANCLAS, IMPORTES), `tabla_aparatos_salidas.py` y `curado_aparatos.json`. Todo se cuenta en **puntos** (piezas y salidas), nunca en área; las redes por m² de losa y los conceptos fijos quedan fuera.

**Método.** Cada grupo de los libros curados (WC, lavamanos, apagador, estufa…) tiene un concepto ancla que trae una unidad por punto. El conteo de un prototipo es la suma de las cantidades de esas claves en su capítulo de Hoja1; si Zafiro y Oro anclan el grupo en claves distintas se toma el mayor de los dos conteos. En Zafiro la tabla reproduce todos los conteos «por salidas» del libro curado (35, 7, 6; en eléctricas 122 contra 121 por el arbotante); en Oro difiere en 6 grupos donde el libro curado ajusta a mano (excepciones autorizadas).

| Sistema | Zafiro | Rubí | Z. Plus | Jade | Dia − | Dia + | Oro |
|---|---|---|---|---|---|---|---|
| Salidas hidrosanitarias | 35 | 35 | 41 | 36 | 49 | 49 | 41 |
| Salidas de gas | 7 | 7 | 7 | 8 | 8 | 8 | 9 |
| Salidas eléctricas | 122 | 138 | 165 | 161 | 175 | 175 | 190 |
| Piezas de equipos | 6 | 6 | 6 | 6 | 7 | 7 | 7 |

**Costo por salida (por puntos) y su dispersión en los 7:**

| Sistema | $/salida media | CV | Lectura |
|---|---|---|---|
| Hidrosanitarias (con muebles) | 1,880 | 7.4 % | Utilizable |
| Gas | 653 | 2.5 % | Utilizable |
| Eléctricas | 454 | 3.4 % | Utilizable |
| Equipos | 2,204 | 4.4 % | Utilizable |

**Lectura.** Con puntos como parámetro, las instalaciones salen más estables que por m² (hidrosanitarias 7.4 % contra 11.1 %, gas 2.5 % contra 19.6 %, eléctricas 3.4 % contra 9.1 %). Esto confirma lo que el cerebro suponía: el parámetro de las instalaciones es la salida, no el área. Hidrosanitarias baja un poco porque los muebles varían de calidad.

**Qué falta.** (1) El bloque «sin grupo» de la hoja SIN_GRUPO (19 claves; sobre todo líneas principales sanitarias e hidráulicas y la cisterna prefabricada, que no son puntos). (2) Que alguien confirme los 6 grupos donde Oro ajusta a mano. (3) El ancla de TV se corrigió a la salida de cimentación (IEC-01080): la del libro curado era una tapa ciega agregada.
