# Unidades de Oro y contraste con la idea de paramétrico del cerebro

```
órgano:     fuente — unidades de Oro, contraste con el cerebro y medición en los 7 prototipos
capa:       I — Mundo
pregunta:   ¿las tasas paramétricas son estables entre prototipos?
tiempo:     es así
corte:      2026-11-11
```
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
| Hidrosanitarias (con muebles) | 1,904 | 7.5 % | Utilizable |
| Gas | 653 | 2.5 % | Utilizable |
| Eléctricas | 455 | 3.9 % | Utilizable |
| Equipos | 2,204 | 4.4 % | Utilizable |

**Lectura.** Con puntos como parámetro, las instalaciones salen más estables que por m² (hidrosanitarias 7.5 % contra 11.1 %, gas 2.5 % contra 19.6 %, eléctricas 3.9 % contra 9.1 %). Esto confirma lo que el cerebro suponía: el parámetro de las instalaciones es la salida, no el área. Hidrosanitarias baja un poco porque los muebles varían de calidad.

**Claves sin grupo: asignadas.** Las 19 claves que ningún libro curado usaba se asignaron a su grupo (`asignaciones_sin_grupo.json`, hoja ASIGNADAS con el motivo de cada una): 6 líneas principales y la acometida eléctrica a las redes (no son puntos), la cisterna prefabricada a fijos, la tarja del asador al asador fijo, y 9 variantes de salidas y cableados a su aparato (minisplit, lavavajillas, tarja, BAN, lavamanos, regadera, apagador mixto). Son claves de etapa, no de ancla: no cambian el conteo de puntos, solo suman su importe. Con ellas cada familia cuadra: puntos + fijos + redes = total, y SIN_GRUPO queda vacía. El efecto es pequeño: hidrosanitarias pasa de $1,880 a $1,904 por salida y eléctricas de $454 a $455.

**Qué falta.** (1) Revisar si las 9 variantes asignadas por parecido de nombre son las que usted habría elegido. (2) Que alguien confirme los 6 grupos donde Oro ajusta a mano. (3) El ancla de TV se corrigió a la salida de cimentación (IEC-01080): la del libro curado era una tapa ciega agregada.

## 9. Pretil en los 7 prototipos (2026-11-11)

Archivos: `PRETIL_7_PROTOTIPOS.xlsx` (hojas LEEME, RESUMEN y PARTIDAS) y `medir_pretil.py`. Aplica a los siete la regla que se resolvió en Zafiro (hoja Paramétrico PRETIL: 62 m², $75,537, $1,218/m²). La regla reproduce el libro curado de Zafiro **al centavo** ($75,537.12 en las cuatro capas).

**La regla.** Driver: m² de muro de pretil (tabique de 14 cm en la azotea). Obra negra, repellado 3.00, boquillas y finas 3.00 se toman completos de la azotea. La **franja de fachada +3.00** (repellado y finas) tiene un tope en los m² del pretil: de los 73 m² de Zafiro, 62 van al pretil y 11 al muro. La pintura es la línea de fachada con ubicación INTERIOR que más se parece al repellado del pretil.

| Prototipo | m² de pretil | Importe | $/m² |
|---|---|---|---|
| Zafiro 1.0 | 62 | 75,537 | 1,218 |
| Rubí | 74 | 84,611 | 1,143 |
| Zafiro Plus | 38 | 42,899 | 1,129 |
| Jade | 64 | 78,637 | 1,229 |
| Diamante − y + | 19.2 | 20,947 | 1,091 |
| Oro 4.01 (regla de Zafiro) | 45 | 47,154 | 1,048 |

Tasa total: media $1,136, CV 6 % → **utilizable**. Por capa: obra negra $512/m² (8 %, utilizable), obra gris $390 (11 %, revisar), obra blanca $181 (12 %, revisar), pintura $53 (65 %, no usar sola). Los ratios por m² de pretil (castillo 0.40, repellado 3.00 de 1.0 a 1.6, boquillas de 1.1 a 1.7, franja +3.00 de 1.0) son la parametrización de cada prototipo.

**Oro cambia.** El pretil de Oro v19 salía casi al doble (2,421 contra 1,218) porque el libro curado pone en el pretil los **300 m²** de repellado y de finas de fachada +3.00 que el catálogo trae en la azotea. Con la regla de Zafiro al pretil le tocan 45 m² (su muro) y los otros 255 m² pertenecen a MURO FACHADA. La diferencia ($61,804) es exactamente 255 m² × $159.03 de repellado + 255 m² × $79.71 de finas + una boquilla de 18.2 m del libro curado. **El libro de Oro no se modificó:** si se aplica, hay que decidir cómo cobra MURO FACHADA esos 255 m².

**Efecto en la comparación anterior.** El pretil pasa de «no usar» (CV 47 % con n = 2) a «utilizable» (CV 6 % con n = 7). Era el contenido de la hoja de Oro, no el diseño.

**Límites.** Diamante − y + tienen un pretil de 19.2 m² (tercer nivel) y su línea de pintura es una suposición de poca confianza. Zafiro Plus y Diamante usan la clave `EST-02011` como muro de pretil. El catálogo no etiqueta la pintura de pretil.

## 10. Oro v20: corrección del pretil (2026-11-11)

Archivo: `CATALOGO_PARAMETRICO_ORO_v20.xlsx` (hoja `LEEME v20`). Parte de v19 y cambia solo el reparto de tres cosas; **el total ($2,635,265.32), la diferencia contra Hoja1 ($20,175.71) y todos los controles quedan iguales** (verificado recalculando).

| Hoja | v19 | v20 | Cambio |
|---|---|---|---|
| PRETIL | $108,957 ($2,421/m²) | $47,154 ($1,048/m²) | −$61,803: la franja +3.00 pasa de 300 a 45 m² (tope en el muro del pretil) y la boquilla de 18.2 m sale |
| MURO FACHADA | $93,142 | $154,021 | +$60,879: dos partidas nuevas (filas 31 y 32) cobran los 255 m² restantes de repellado y de finas +3.00 |
| MARCOS EXTERIORES | $42,540 | $43,464 | +$925: recibe la boquilla de 18.2 m (fila 319 de Hoja1), que estaba en el pretil por llevar la misma clave |

El pretil de Oro queda en $1,048/m², igual que la medición con la regla de Zafiro. Con eso la referencia congelada de Oro en el panel de Zafiro v45 pasó de 2,421 a 1,048.

**Pendiente de decisión.** La fila 320 de Hoja1 (boquilla en fachada, agregada) tiene la misma cantidad y precio que la 319 y también se cobra en MARCOS EXTERIORES: los marcos llevan hoy 36.4 m de boquilla gris. Hay que decidir si es una sola. Tampoco se cambió el selector de altura (D5): la franja de 255 m² se cobra siempre, con cualquier altura.

## 11. Boquilla gruesa y fina de los marcos: Oro v21 (2026-11-11)

Archivo: `CATALOGO_PARAMETRICO_ORO_v21.xlsx` (hoja `LEEME v21`). **Corrige un error de v20:** allí moví la boquilla de la fila 319 a MARCOS EXTERIORES y quedaron dos boquillas gruesas.

**Revisión.** La gruesa y la fina no son lo mismo y las dos están:

| Fila Hoja1 | Clave | Qué es | m | $/m | Origen |
|---|---|---|---|---|---|
| 319 | ACA-01051 | Boquilla gruesa (estuco exterior) | 18.2 | 50.81 | Presupuesto de Oro |
| 320 | ACA-01052 | Boquilla gruesa en fachada | 18.2 | 50.81 | Agregado, clave de Zafiro (su fila 204) |
| 321 | ACA-01071 | Boquilla fina en fachada | 18.2 | 9.34 | Presupuesto de Oro |

La 319 y la 320 son la misma boquilla gruesa: misma cantidad, mismo precio, y la 320 lleva el código de Zafiro (1052701). La pareja original de Oro es 319 + 321 (códigos 7052706 y 7052707, consecutivos); la 320 se agregó para usar la clave que Zafiro usa para la gruesa de los marcos. **No falta ninguna: sobra una.** Hoja1 de Oro trae la gruesa dos veces y la fina una.

**Ajuste en v21.** MARCOS EXTERIORES cobra una gruesa (fila 320) y una fina (fila 321). La 319 se queda con cantidad 0 para que Hoja1 tenga cobertura, y entra a las excepciones autorizadas. El pretil conserva sus dos boquillas, gruesa (fila 270) y fina (fila 274), y VANO las suyas.

| | v19 | v21 |
|---|---|---|
| Total del paramétrico | $2,635,265.32 | $2,634,340.58 (−$924.74) |
| Diferencia contra Hoja1 | +$20,175.71 | +$19,250.97 |
| Conceptos con importe distinto | 25 | 26 |
| PRETIL | $108,957 | $47,154 |
| MURO FACHADA | $93,142 | $154,021 |
| MARCOS EXTERIORES | $42,540 | $42,540 |

Si la 319 y la 320 no fueran la misma boquilla (por ejemplo, una de ventanas y otra de puertas), la corrección es devolverle a la 319 su cantidad de 18.2 m.

## 12. Vano y marcos exteriores en los 7 prototipos (2026-11-11)

Archivos: `VANO_MARCOS_7_PROTOTIPOS.xlsx` (hojas LEEME, RESUMEN y PARTIDAS) y `medir_vano_marcos.py`. La regla reproduce los libros curados: VANO de Zafiro $17,550.08 y de Oro $13,323.23, MARCOS EXTERIORES de Zafiro $21,070.34 y de Oro $42,539.53.

**La regla.** La boquilla fina define el tipo: `ACA-01060` es interior (VANO), `ACA-01071` es de fachada (MARCOS EXTERIORES), `ACA-01072` es del pretil. La boquilla gruesa que le corresponde es la de la misma zona y la misma cantidad, sea cual sea su clave (el catálogo usa ACA-01050, 01051 y 01052 sin orden). Driver de VANO: metros de boquilla gruesa interior. Driver de MARCOS: metros de marco de cantera exterior (`ACA-07011`).

**VANO.**

| | Zafiro | Rubí | Z. Plus | Jade | Dia − y + | Oro |
|---|---|---|---|---|---|---|
| Perímetro (m) | 127 | 101 | 211 | 99.8 | 148.3 | 221.5 |
| $/m con revestimiento | 138.19 | 60.15 | 60.15 | 60.15 | 60.15 | 60.15 |
| $/m **sin** revestimiento | 58.97 | 60.15 | 60.15 | 60.15 | 60.15 | 60.15 |

Con n = 2 el vano salía «no usar» (CV de 56 %). La causa es que Zafiro lleva una capa de revestimiento (marco de cantera interior y su sellado, $79/m) que **ningún otro prototipo trae**. La tasa comparable, sin esa capa, da $60/m con CV de 1 %: utilizable. La capa de marco interior queda como opcional, solo de Zafiro.

**MARCOS EXTERIORES.**

| | Zafiro | Rubí | Z. Plus | Jade | Dia − y + | Oro |
|---|---|---|---|---|---|---|
| Marco (m) | 44.4 | 83 | 71.6 | 52.6 | 132 | 89.9 |
| $/m total | 474.56 | 466.81 | 486.21 | 485.48 | 513.62 | 473.19 |

Media $488/m, CV 4 %: **utilizable**. El marco con su sellado cuesta $461/m en los siete (es precio); lo que varía es la boquilla, de 0.10 a 0.87 m por m de marco (CV 71 %), pero pesa menos de $50/m. Las boquillas no son proporcionales al marco: dependen del diseño de las ventanas, no de su largo.

**Hallazgos del catálogo (no de los libros).**
- Zafiro trae 127 m de boquilla gruesa interior y solo 111 m de fina: faltan 16 m de fina ($149) o sobran de gruesa.
- Jade trae 59.2 m de sellado de marco contra 52.6 m de marco exterior: 6.6 m de sellado sin marco, que no se cobran (los mismos 6.6 m que Zafiro ajustó a 21 m).
- Diamante − y + codifican la boquilla gruesa de fachada como `ACA-01051` (la del pretil), igual que la fila 319 de Oro; Zafiro, Rubí, Zafiro Plus y Jade usan `ACA-01052`.
- Zafiro Plus lleva la boquilla gruesa interior de la planta alta con la clave `ACA-01051`.

**Libros.** No hizo falta cambiar partidas ni importes en Zafiro v46 ni en Oro v22. Solo agregué una nota de contraste en el panel de VANO y de MARCOS EXTERIORES de los dos libros, para que la tasa de $138/m de Zafiro no se lea como dispersión. Las pruebas de estabilidad siguen pasando.

## 13. Todos los conceptos de los 7 prototipos en su driver (2026-11-11)

Archivos: `PARAMETRICOS_7_PROTOTIPOS.xlsx` (hojas LEEME, RESUMEN, VALIDACIÓN y ASIGNACIÓN), `asignar_drivers.py`, `mapa_aprendido.json` y `curado_drivers.json`.

**El hueco que cierra.** Zafiro y Oro tenían su presupuesto repartido en drivers, con cuadre contra Hoja1. Los otros cinco prototipos no. Ahora cada uno de los 2,452 conceptos de los siete tiene driver y capa, y el total asignado de cada prototipo **cuadra con su presupuesto de Hoja1 (diferencia 0 en los siete)**. Queda 1 concepto sin asignar, con importe 0 (`PRB-01001` de Jade).

**Cómo se asigna** (en este orden): (1) boquillas por pares, la fina define el tipo; (2) franja de fachada +3.00 con tope en el muro del pretil; (3) pintura del pretil; (4) lo aprendido de los libros curados, misma clave en el mismo subcapítulo, mismo driver y capa (2,130 filas); (5) reglas por clave y subcapítulo para lo propio de cada prototipo (245 filas: losas, cocinas, cancelerías, pérgolas, herrería). En la hoja ASIGNACIÓN se puede cambiar el driver o la capa de cualquier concepto y RESUMEN se recalcula.

**Validación contra los libros curados** (regla automática contra el libro armado a mano):

| Driver | Zafiro | Oro |
|---|---|---|
| Pretil, vano, marcos exteriores, pórfido, barda, sillar, jardín, cubierta, cisterna, carpintería, cancelería, obra exterior, equipos | idéntico | idéntico |
| Losa | idéntico | +0.3 % |
| Muro, piso (con el reparto del mármol, §14) | idéntico | −0.1 %, −0.3 % |
| Asador, cochera | ±2.6 % | −8.1 %, −3.5 % |
| Herrería, gas, eléctricas | idéntico | −11.2 %, −12.8 %, −4.4 % |

Las diferencias que quedan vienen de los ajustes de Oro (excepciones autorizadas, columnas de cantera) y de la losa de cimentación convertida de pieza global a m². (Antes del reparto del mármol, §14, muro y piso diferían 2.6 % y 5.3 % en Zafiro.) La regla automática es la misma para los siete, así que la comparación entre prototipos es justa.

**Tasas en los 7 prototipos:**

| Driver | Divisor | Tasa media | CV | Lectura |
|---|---|---|---|---|
| Muro | m² de tabique | 1,471 | 9.0 % | Utilizable |
| Pretil | m² de pretil | 1,136 | 5.9 % | Utilizable |
| Vano sin revestimiento | m de boquilla interior | 60 | 0.7 % | Utilizable |
| Marcos exteriores | m de marco | 489 | 3.9 % | Utilizable |
| Losa | m² de losa de nivel | 1,891 | 9.6 % | Utilizable |
| Piso (loseta, zoclo, mármol) | m² de piso | 548 | 0.8 % | Utilizable (§15) |
| Losa de cimentación | m² de desplante | 793 | 6.4 % | Utilizable (§15) |
| Asador | m² de piso | 3,571 | 7.7 % | Utilizable |
| Pórfido | m² | 545 | 5.1 % | Utilizable |
| Cochera | m² de pérgola (n = 5) | 2,101 | 2.7 % | Utilizable |
| Barda | ml | 1,813 | 1.6 % | Utilizable (mismo concepto en los 7) |
| Cubierta | ml | 3,098 | 7.6 % | Utilizable |
| Cisterna | L | 7.4 | 0 % | Precio, no dispersión |
| Sillar | m² (n = 4) | 836 | 15.7 % | Insuficiente |
| Jardín | m² de sello (n = 4) | 242 | 13.2 % | Insuficiente |

Instalaciones y equipos usan la tasa por salida de `TABLA_APARATOS_SALIDAS.xlsx`. Carpintería, cancelería, herrería, obra exterior, escalera y obra complementaria son fijos: solo traen importe por prototipo. **Piso quedó en «revisar» solo por un error de divisor, corregido en §15.** **Obra complementaria** es el cajón de lo propio de cada prototipo (galarza, forrados de columna, vigas de madera): $1 mil en Zafiro y $73 mil en Diamante; ver §16.

**Pendientes.** (1) Sillar y jardín solo existen en 4 de los 7 prototipos. (2) El mármol de piso de los otros cinco (resuelto con datos, §14). (3) Obra complementaria: resuelto en §16.

## 14. Mármol de piso en los otros cinco (2026-11-11)

Hoja `MÁRMOL` de `PARAMETRICOS_7_PROTOTIPOS.xlsx`. Reparte el mármol (tomboleado y travertino largos libres, con su sellado y limpieza) entre muro y piso, como hacen los libros curados de Zafiro y Oro. Mover mármol de muro a piso **no cambia el total del prototipo**, solo cuánto cuesta el muro y cuánto el piso.

Los m² de mármol en piso son **dato del usuario**, por nivel:

| Prototipo | Nivel | Largos libres (m²) | Tomboleado (m²) | Total largos libres | Total tomboleado |
|---|---|---|---|---|---|
| Zafiro 1.0 | — | 17.52 | 4.81 | 17.52 | 4.81 |
| Rubí | PB | 30.19 | 5.87 | 30.19 | 5.87 |
| Zafiro Plus | PB / PA | 14.85 / 10.98 | 1.94 / 3.61 | 25.83 | 5.55 |
| Jade | PB | 10.86 | 5.72 | 10.86 | 5.72 |
| Diamante − y + | PB / PA | 22.54 / 3.57 | 4.73 / 1.57 | 26.11 | 6.30 |
| Oro 4.01 | PB / PA | 13.24 / 19.64 | 1.8 / 6.24 | 32.88 | 8.04 |

Zafiro y Oro son los datos de sus libros curados. El catálogo trae el mármol por prototipo, no por nivel; cuando un prototipo tiene dos líneas (Zafiro Plus y Diamante), lo que va en piso se reparte entre ellas en proporción a su cantidad.

**Lo que dijo el estimado.** Antes de tener estos datos se había estimado el travertino en piso con el 42.6 % del total (promedio de Zafiro y Oro). Contra el dato real: Rubí 30.41 contra 30.19 m² (acierto casi exacto), Zafiro Plus 24.38 contra 25.83, Diamante 30.95 contra 26.11, **Jade 14.69 contra 10.86**. La fracción real va de 31 % (Jade) a 46 % (Oro): el estimado servía para saber que no importaba mucho, no para sustituir el dato. El tomboleado, estimado con la renivelación de charolas, quedó entre 6 % y 8 % por debajo del dato (por ejemplo Rubí 5.47 contra 5.87).

**Resultado.** Muro $1,471/m² (CV 9.0 %, utilizable) y piso $1,406/m² (CV 11.8 %, revisar): casi igual que con el estimado ($1,470 y $1,409). Zafiro sigue reproduciendo su libro al centavo y Oro queda en −0.1 % (muro) y −0.3 % (piso). El CV del piso viene de otra parte: la losa de cimentación y la composición del piso por prototipo. Los cinco prototipos nuevos cuadran con Hoja1 (centavos por redondeo); la diferencia de +$447.82 de Zafiro es el sellado interior de 21 m, excepción ya autorizada.

## 15. Piso: el problema era el divisor (2026-11-11)

**Hallazgo.** El piso salía «revisar» (CV de 11.8 %) porque se medía contra los m² de **desplante**, y el desplante es la huella de la losa de cimentación, no el área que se pisa. Un prototipo de dos plantas pisa casi el doble de lo que desplanta: Oro desplanta 160 m² y coloca 266 m² de piso, Zafiro 172 y 157. Los libros curados ya lo sabían: Zafiro mide el piso contra 157.33 m² de piso colocado, y Oro contra la losa de cada nivel.

**Corrección.** `PARAMETRICOS_7_PROTOTIPOS.xlsx` separa dos drivers:

| Driver | Divisor | Qué incluye |
|---|---|---|
| Losa de cimentación | m² de desplante (los m² de la descripción de la losa) | La losa de cimentación |
| Piso | m² de piso colocado = loseta (Lugano y Brunei) + mármol de piso | Loseta, zoclo, renivelación de charolas, sardinel, vertedero, mármol de piso |

| $ por m² | Zafiro | Rubí | Z. Plus | Jade | Dia − | Dia + | Oro | Media | CV |
|---|---|---|---|---|---|---|---|---|---|
| Piso (m² de piso) | 554.0 | 547.3 | 547.7 | 550.3 | 541.5 | 541.5 | 550.1 | 547.5 | **0.8 %** |
| Losa de cimentación (m² de desplante) | 756.4 | 749.2 | 768.6 | 776.3 | 871.1 | 860.5 | 771.4 | 793.4 | **6.4 %** |

El piso de Zafiro da $554.0/m², el mismo $554.01 que tenía su libro curado. El piso colocado por prototipo es 157.3, 183.1, 196.4, 203.9, 217.5, 217.5 y 266.0 m². Los precios de loseta y zoclo son los mismos en todos, por eso el piso es casi constante: su CV bajo es precio, no estabilidad del diseño. Lo que varía es **cuántos m² se pisan**, no cuánto cuesta cada uno.

**Validación.** Piso + losa de cimentación suma lo mismo que el piso del libro curado: Zafiro $217,267 (idéntico) y Oro $269,763 contra $270,519 (−0.3 %).

**Consecuencia.** Ya no queda ningún driver de peso en «revisar». Siguen insuficientes sillar y jardín (n = 4). Los libros de Zafiro v46 y Oro v22 no cambian; la separación está en la medición de los siete.

## 16. Obra complementaria: qué hay dentro (2026-11-11)

Era el cajón de lo que no entraba en ningún driver. Ahora tiene **ocho grupos con su unidad** (la piedra galarza salió a la chimenea, §17), en la hoja RESUMEN de `PARAMETRICOS_7_PROTOTIPOS.xlsx` (bloque «Obra complementaria por grupo»):

| Grupo | Unidad | Zafiro | Rubí | Z. Plus | Jade | Dia − | Dia + | Oro | $/unidad |
|---|---|---|---|---|---|---|---|---|---|
| Durmiente | pza | 1 | 1 | 1 | 1 | 2 | 2 | 2 | 1,080 |
| Goterón | m | — | — | 7.8 | — | 7.8 | 7.8 | 7.8 | 80 |
| Tejas sobre losa | m² | — | — | 43 | 14.4 | 25 | 25 | 24.0 | 288.7 |
| Vigas empotradas a muro | pza | — | — | 17 | 10 | 10 | 10 | 12 | 326 |
| Vigas de madera | pza | — | — | — | 3 | — | — | — | 2,424 |
| Columnas de piedra (forrados y de cantera) | pza | — | — | 1 | — | 13 | 13 | — | 4,333 a 5,132 |
| Fachaleta de cantera | m² | — | — | — | 25.6 | — | — | — | 469 |
| Roof (piso y zoclo Dover) | m² | — | — | — | — | 5.8 | 5.8 | — | 576 |
| **Importe total** | | **1,080** | **1,080** | **23,990** | **27,778** | **73,065** | **73,065** | **13,630** | |

**Lectura.** Todo es precio unitario por pieza: la tasa por unidad no tiene dispersión que medir (CV de 0 en los grupos que se repiten). Lo que varía entre prototipos es **qué lleva cada diseño y cuántas piezas**: el durmiente está en los siete, las tejas y las vigas en cinco, y Diamante concentra el resto (13 columnas forradas o de cantera = $56 mil y roof, $3 mil). No es un driver que escale con un área; es un catálogo de piezas por prototipo, igual que carpintería o herrería.

**Correcciones al asignar.**
- **Durmiente:** Zafiro lo trae con la clave `ICA-01030` y Oro con `CAR-01030`; estaba en el muro en unos prototipos y en obra complementaria en otros. Ahora está en obra complementaria en los siete, como en Oro. Zafiro queda −$1,080 en muro (−0.24 %) contra su libro curado, que lo tenía como fijo del muro.
- **Columnas de cantera** (`ACA-07040`): las de asador y cochera se quedan en su driver, como en los libros curados; solo las que no tienen un asador o cochera donde caer (Zafiro Plus) pasan aquí.
- **Vigas:** las de 15×20 a 60 cm ($326) y las de madera a 140 cm ($2,424) son piezas distintas y van en grupos separados.

**Validación.** Oro queda **idéntico** a su libro curado: $13,630 (durmiente $2,160, goterón $620, tejas $6,938 y vigas $3,912). Zafiro no tiene obra complementaria en su libro; aquí solo trae el durmiente.

**Pendiente.** Los grupos de Diamante (columnas forradas con piedra galarza y roof) no tienen libro curado contra el cual validarse; son $56 mil de forrados y $3 mil de roof que dependen del diseño. Si algún prototipo nuevo trae más, caen en «Sin clasificar» para decidirlos.

## 17. Ensamble de chimenea (2026-11-11)

**Corrección del usuario:** la piedra galarza de 40×40 y 60×40 **no es de piso, es de la chimenea**. Estaba mal en obra complementaria como «piso». Pasa a un driver nuevo, **CHIMENEA**, que es un ensamble de una pieza (`pza`, una chimenea por prototipo) en `PARAMETRICOS_7_PROTOTIPOS.xlsx`, hoja `CHIMENEA`.

**Cómo se armó la receta.** La chimenea solo existe en Diamante con chimenea. Se comparó contra Diamante sin chimenea y se tomó lo que la versión con chimenea agrega a cada concepto. El muro lo confirma: Diamante con chimenea mide 602.52 m² de tabique y sin chimenea 591; al sacar los 11.52 m² del cuerpo de la chimenea, **el muro de las dos versiones queda en 591 m²**.

| Grupo | Concepto | Cantidad | Importe | Certeza |
|---|---|---|---|---|
| Cimentación | Acero de cimentación K3 (la base) | 2 pza | $1,789 | Probable |
| Obra negra | Muro de tabique de 14 cm (el cuerpo) | 11.52 m² | $4,458 | Probable |
| Obra negra | Castillo K7 para encofrar tubería (el tiro) | 8.4 m | $1,698 | Probable |
| Obra gris | Repellado del cuerpo | 19.74 m² | $2,531 | Probable |
| Revestimiento | Piedra galarza 40×40 | 4.32 m² | $4,715 | **Cierta** |
| Revestimiento | Piedra galarza 60×40 | 10.72 m² | $8,536 | **Cierta** |
| **Total de la chimenea** | | | **$23,728** | $13,251 ciertas, $10,477 probables |

**Lo que la hoja también muestra.** Diamante con chimenea cuesta $29,065 más que sin chimenea. La chimenea explica **$23,728**; los otros **$5,337** son cambios de diseño entre las dos versiones (otras losas, 85 m² más de relleno, columnas C-1 que desaparecen, la línea sanitaria de cimentación). Las dos losas de cimentación y las dos de entrepiso son distintas en cada versión, y cada par casi se compensa.

**Qué falta, y es del usuario.**
- Las piezas de la chimenea que **el catálogo no trae**: el hogar, el tiro metálico, el remate y la campana no tienen precio en ningún concepto.
- Confirmar las cuatro piezas «probables» (cimentación, cuerpo, tiro y repellado) y el castillo K7: sale de comparar las dos versiones, no de una descripción que diga «chimenea».
- La línea sanitaria de cimentación (+$731 con chimenea) la atribuye `CONOCIMIENTO.md` a la chimenea; aquí queda fuera porque es otra clave, no una pieza propia.

**Efecto en las tasas.** Diamante con chimenea ya no mezcla el cuerpo de la chimenea con el muro: su divisor de muro baja a 591 m², igual que el de sin chimenea, y su tasa de muro queda en $1,487 contra $1,492. Obra complementaria de Diamante con chimenea queda igual que la de sin chimenea ($73,065).
