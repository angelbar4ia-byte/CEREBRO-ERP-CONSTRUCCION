# CATÁLOGO PARAMÉTRICO — Bitácora y especificación

Archivo vivo: se actualiza con cada avance.

> **Libros vigentes:** ZAFIRO → `CATALOGO_PARAMETRICO_con_MURO_ZAFIRO_CAPAS_v45.xlsx`; ORO → `CATALOGO_PARAMETRICO_ORO_v21.xlsx` (v44, v18, v19 y v20 se conservan como originales recibidos; v45 y v19 agregan llaves, cohorte y unidades reales, ver bitácora). Antes: ZAFIRO v44, ORO v18 (la línea ORO nació de la v44 de Zafiro). Las secciones 11F, 11G y 13 y las últimas filas de la bitácora se **reconstruyeron leyendo los libros** (hojas, capas, filas de Hoja1 y notas), porque este .md no se había actualizado desde la v36. No traen importes: los libros no guardan valores calculados (solo fórmulas); se obtienen al abrirlos en Excel. El detalle de **qué cambió en cada versión** se recuperó comparando celda por celda cada libro con el anterior (bitácora, sección 12; criterios de Oro en la sección 13). Lo que sigue sin poderse recuperar es el razonamiento de las decisiones que no quedó escrito en notas del libro.

Libro de trabajo anterior: `CATALOGO_PARAMETRICO_con_MURO_ZAFIRO_CAPAS_v36.xlsx` (versiones previas: `..._CAPAS_v35.xlsx`, `..._CAPAS_v34.xlsx`, `..._CAPAS_v33.xlsx`, `..._CAPAS_v32.xlsx`, `..._CAPAS_v31.xlsx`, `..._CAPAS_v30.xlsx`, `..._CAPAS_v29.xlsx`, `..._CAPAS_v28.xlsx`, `..._CAPAS_v27.xlsx`, `..._CAPAS_v26.xlsx`, `..._CAPAS_v25.xlsx`, `..._CAPAS_v24.xlsx`, `..._CAPAS_v23.xlsx`, `..._CAPAS_v22.xlsx`, `..._CAPAS_v21.xlsx`, `..._CAPAS_v20.xlsx`, `..._CAPAS_v19.xlsx`, `..._CAPAS_v18.xlsx`, `..._CAPAS_v17.xlsx`, `..._CAPAS_v16.xlsx`, `..._CAPAS_v15.xlsx`, `..._CAPAS_v14.xlsx`, `..._CAPAS_v13.xlsx`, `..._CAPAS_v12.xlsx`, `..._CAPAS_v11.xlsx`, `..._CAPAS_v10.xlsx`, `..._CAPAS_v9.xlsx`, `..._CAPAS_v8.xlsx`, `..._CAPAS_v7.xlsx`, `..._CAPAS_v6.xlsx`, `..._CAPAS_v5.xlsx`, `..._CAPAS_v4.xlsx` [con el movimiento de finas/pretil que se revirtió], `..._CAPAS_v3.xlsx`, `..._CAPAS_v2.xlsx` y `..._CAPAS.xlsx`, `..._RUTAS.xlsx` sin capas y `CATALOGO_PARAMETRICO_con_MURO_ZAFIRO.xlsx` original; se guarda archivo nuevo porque Excel bloquea el abierto).
Última actualización: 2026-11-10 (capas del muro)

---

## 1. Objetivo

Construir un catálogo paramétrico lo más completo posible a partir del presupuesto del modelo **ZAFIRO 1.0 (172 m²)**. Cada partida se asocia a un **driver** (magnitud que captura el usuario) con una regla de escalamiento, de modo que al cambiar el driver cambien las cantidades y los importes.

## 2. Estructura del libro

| Hoja | Contenido |
|---|---|
| **Paramétrico MURO CONFINAMIENTO** | Cálculo del precio por m² de muro de confinamiento. Lee Hoja1 con fórmulas. |
| **Paramétrico MURO CAPAS** | Las 5 capas del muro con interruptores Sí/No, interior y fachada separados. Aquí se edita D4 (m² de muro del proyecto). |
| **Paramétrico PRETIL / VANO / LOSA / PISO / ASADOR / PÓRFIDO / COCHERA / SILLAR / BARDA / HIDROSANITARIAS / GAS / ELÉCTRICAS / EQUIPOS / HERRERÍA / CARPINTERÍA / CANCELERÍA** | Un driver por hoja, con capas e interruptores Sí/No (ver secciones 8 a 11). |
| **Rutas** | Resumen por driver y detalle de rutas, con todas las columnas de Hoja1 por partida. |
| **Hoja1** | Catálogo base: 3,234 filas, 30 columnas (A–AD), 2,452 conceptos. Presupuesto Zafiro 1.0 = $1,842,426.01. |
| **Leyenda Q-Z** | Reglas de inferencia de las columnas Q a AD y su cobertura. |
| **Claves sin Zafiro** | ~176 claves de otros modelos (Diamante, Jade, Oro, Rubí, Zafiro Plus) que no existen en Zafiro. |
| **Catálogo Geometría** | Resúmenes por DIMENSIONAL, ELEMENTO GEOMÉTRICO y ELEMENTO CONSTRUCTIVO. |

## 3. Concepto de ruta paramétrica

```
RUTA = DRIVER > GRUPO > PARTIDA        (+ regla de escalamiento)
cantidad proyecto = ratio base × valor del driver
ratio base        = cantidad en Zafiro 1.0 / valor base del driver
```

Tipos de escalamiento:
- **Proporcional:** crece con el driver (castillos, cadenas, acero).
- **Otro driver:** depende de otra magnitud (m de pretil, m de barda…); se parametriza en su propio bloque.
- **Fijo / Por conteo:** previstos, aún sin uso.

Relación con las columnas existentes de Hoja1: DIMENSIONAL (global, lineal, puntual, superficie, volumen) indica el tipo de driver; ELEMENTO GEOMÉTRICO (MURO, LOSA, PISO, VANO…) casi es el driver.

## 4. Driver definido: MURO DE CONFINAMIENTO

Parte de la estructura de planta baja; es el bloque con más detalle. Sus atributos sirven de plantilla para los demás drivers.

### 4.1 Parámetros (hoja Paramétrico MURO CONFINAMIENTO)

| Celda | Significado |
|---|---|
| `D3` | m² de muro base del catálogo (Hoja1): 279 m² de muro tabique. |
| `D4` | **m² de muro del proyecto (editable).** Por defecto `=D3`. |
| `D5` | Importe de estructura ajustado a D4. |
| `D6` | Precio paramétrico por m² de muro. |

Columnas por partida: F cantidad base, G precio, H importe base, I cantidad por m², J importe por m², K cantidad ajustada a D4, L importe ajustado, M % del total.

### 4.2 Alcance

**Incluido en el precio (18 partidas):**
- Muro: tabique de 14 cm (fila 68 de Hoja1).
- Castillos: 16 partidas, entre colado (K1, K2, K3, K4, K7, en m) y habilitado de acero (en pza).
- Cadena: CE-1 15x20 (fila 75).

**Fuera del precio (informativo):**
- Muro sillar de 20 cm (fila 69). Se sacó por decisión del usuario.
- Pretil de azotea: muro, castillo y cadena (filas 166, 167, 183).
- Barda perimetral: muro, castillo y cadenas (filas 363, 364, 362, 365).
- Muro para cisterna (fila 229).

### 4.3 Resultado con la base de 279 m²

- Importe de estructura: aprox. **$193,676.07**.
- Precio paramétrico: aprox. **$694.18 / m²** (valor calculado a mano; falta confirmarlo en Excel).
- Con el sillar incluido era $207,419.07 y $671.26 / m².
- Como todo es proporcional, el precio por m² no cambia al modificar D4; cambian las cantidades y el importe total.
- Las cantidades de piezas quedan con decimales al escalar. Pendiente decidir si se redondean hacia arriba (`ROUNDUP`).

### 4.4 Hoja Rutas

- Resumen por driver (filas 5–12): MURO DE CONFINAMIENTO definido; LOSA, PISO, VANO, PRETIL, CUBIERTA y PLAFOND como pendientes.
- Detalle (desde la fila 16): bloque de parametrización (columnas A–J), fila de Hoja1 (K) y las 30 columnas de Hoja1 (L–AO), leídas por número de fila con `INDEX`.


## 4B. Driver MURO por capas (obra negra, gris, blanca, revestimiento, pintura)

Hoja `Paramétrico MURO CAPAS`. Un solo driver (m² de muro, celda `D4`) mueve todas las capas; cada capa se calcula por separado y también combinada.

**Reglas acordadas**
- 5 capas: OBRA NEGRA, OBRA GRIS, OBRA BLANCA, REVESTIMIENTO, PINTURA.
- **Interruptores Sí/No por capa** (no por concepto). El precio combinado suma solo las capas en Sí.
- **Interior y fachada separados** dentro de cada capa (obra negra no se separa).
- REVESTIMIENTO = mármoles, piedras y canteras. Cada caso se define después.
- `D4` se edita en la hoja CAPAS; la hoja de confinamiento lo lee de ahí.

**Partidas por capa (filas de Hoja1)**

Cada partida tiene Grupo/elemento y Concepto. Los sellados y limpiezas van con su elemento; el lijado y sellado de muro es de PINTURA.

| Capa | Zona | Elemento > Concepto (fila) |
|---|---|---|
| OBRA NEGRA | — | Muro tabique, castillos, cadena (hoja confinamiento) |
| OBRA GRIS | Interior | Muro > Repellado 3.00 (147) y +3.00 (148) |
| OBRA GRIS | Fachada | Muro > Repellado fachada 3.00 (151) y +3.00 (173, solo 73 − 62 = 11 m²; los 62 m² van a PRETIL) |
| OBRA BLANCA | Interior | Muro > Fino 3.00 (157) y +3.00 (158) |
| OBRA BLANCA | Fachada | Muro > Fino 3.00 (181, 163 m²) y +3.00 (182, solo 73 − 62 = 11 m²; los 62 m² van a PRETIL) |
| REVESTIMIENTO | Interior | Mármol tomboleado > revestimiento (197) y sellado (377); jabonera (198); travertino largos libres > revestimiento (199) y limpieza (383); piedra laja > revestimiento (201) y limpieza y sellado (382); ojo de buey (156); sillar de cantera > limpieza y sellado (379); durmiente > limpieza, entintado y sellado (380) |
| REVESTIMIENTO | Fachada | Chapeo de piedra > revestimiento (184) y limpieza (392); rodapié 60 cm (206, 389); rodapié 20 cm (207, 390); sillar de cantera (393); gualdra (394); ojo de buey (395) |
| PINTURA | Interior | Muro > lijado y sellado (370), pintura 1ª y 2ª mano (371, 372) |
| PINTURA | Fachada | Muro > lijado y sellado (370, cantidad de 386), pintura 1ª y 2ª mano (386, 387) |

**Aclaración final (v6):** las finas de fachada van en MURO. De las finas +3.00 (182, 73 m²) solo se pasa a PRETIL la parte de pretil (62 m² = fila 166); en MURO quedan 11 m². En Hoja1 las filas 181 y 182 se corrigieron de VANO a MURO. El repello fachada +3.00 (173) se parte igual que las finas: 62 m² a PRETIL y 11 m² a MURO (confirmado por el usuario). El sellado de marco de cantera (378) pasó de MURO a VANO.

**Reglas de piso compartido (aclaradas por el usuario)**
- **Mármol tomboleado** existe en muro y en piso. Los m² de piso = m² de renivelación de charola de regadera (fila 190, 4.81 m²). Muro = total de Hoja1 menos esa cantidad (37 − 4.81 = 32.19 m²). Igual para su sellado (377). La parte de piso queda en un bloque "otro driver: PISO", fuera de los totales de muro.
- **Mármol travertino largos libres** (199) es para muro y piso (45 m²). La limpieza de mármol largos libres (383) corresponde al muro. **Pendiente:** el usuario dará los m² de piso; mientras tanto todo cuenta como muro.

**Importes base Zafiro 1.0 (279 m² de muro; cálculo en Python, falta confirmar en Excel)**

| Capa | Interior | Fachada | $/m² |
|---|---|---|---|
| Obra negra | — | — | 694.18 |
| Obra gris | 60,895 | 24,829 | 307.26 |
| Obra blanca | 31,475 | 12,566 | 157.85 |
| Revestimiento (sin piso del tomboleado ni marcos de cantera) | 63,821 | 43,281 | 383.88 |
| Pintura | 23,423 | 19,234 | 152.89 |
| **Todas las capas** | | | **≈ 1,696.05** |

Notas: el repellado (467 m² interior) y los finos (432 m²) no coinciden con los 279 m² de muro porque cubren ambas caras y otros muros; por eso el ratio es mayor que 1 m² por m². La pintura interior (432 m²) coincide con los finos.


**Cambios v20 (elementos fijos, sillar, gualdra y durmiente)**
- **FIJOS por ahora** (no crecen con los m² de muro): ojo de buey (156 y su sellado 395), durmiente (380) y gualdra (394). Vertedero de sardinel (192) es fijo en PISO. Las columnas `L`/`M` de esas filas dicen «Fijo»: cantidad proyecto = cantidad base.
- **Sillar fuera de MURO:** las limpiezas y sellados del sillar (379 interior y 393 fachada) salieron de MURO CAPAS y pasaron al driver SILLAR (sección 4C).
- **Agregados como fijos (no estaban en ningún driver):** suministro de la gualdra 6x12x8 (fila 80, $1,770) y del durmiente 20x20 (fila 185, $1,080).
- Efecto en el muro (cálculo a mano): revestimiento baja ≈ $5,392 (−8,242 de sillar + 2,850), de ≈ $349 a ≈ $330 por m²; total de todas las capas ≈ $1,642/m².

**Revisión de limpiezas y sellados (v20)**

| Elemento | Suministro | Limpieza / sellado | Observación |
|---|---|---|---|
| Ojo de buey | 156 (1 pza) | 395 (1 pza) | Cuadra. |
| Gualdra | 80 (1 pza) | 394 (2.4 m) | El suministro no estaba en ningún driver; ahora sí. |
| Durmiente | 185 (1 pza) | 380 (2.3 m) | El suministro no estaba en ningún driver; ahora sí. |
| Marcos de cantera | 162 interior (21 m), 186 fachada (44.4 m) | 378 interior (14.4 m en Hoja1), 391 fachada (44.4 m) | El interior no cuadraba; **resuelto**: el sellado interior se deja en 21 m. La fachada cuadra. |
| Sillar | 69 (30 m²) | 379 interior (30 m²) y 393 fachada (30 m²) | Una limpieza por cada cara; cuadra con el muro. |

## 4C. Driver SILLAR (hoja Paramétrico SILLAR)

Driver: m² de muro de sillar de 20 cm (`D4`; base **30 m²**, fila 69). Dos capas con interruptor.

| Capa | Partidas (fila) | Importe base |
|---|---|---|
| Obra negra | Muro sillar de 20 cm (69) | 13,743 |
| Revestimiento | Limpieza y sellado de silicón de sillar de cantera: interior (379) y fachada (393), 30 m² cada una | 8,242 |
| **Total** | | **≈ 21,985 (≈ $732.82/m²)** |

- El muro sillar de la barda (fila 363, 35.88 m²) no entra: va con la barda.
- Si el sillar solo tiene una cara a la vista, se debe quitar una de las dos limpiezas.

## 4D. Driver BARDA PERIMETRAL (hoja Paramétrico BARDA)

Driver: **metros lineales de barda** (`D4`; base **15 ml**, cadena CD-1 de la fila 362). La barda es aparente: sin repello, fino, pintura ni limpieza y sellado (decisión del usuario). Una capa (obra negra) con interruptor.

| Partida (fila) | Cantidad base | Escalamiento | Importe base |
|---|---|---|---|
| Muro sillar de 20 cm (363) | 35.88 m² (2.39 m de altura implícita) | Proporcional a los ml | 13,172 |
| Castillo K-1 aparente 25x20 (364) | 15.6 m (8 piezas de 1.95 m) | **Por piezas** (+1 cada 3 ml adicionales) | 4,647 |
| Cadena CD-1 aparente 20x25 (362) | 15 m | Proporcional a los ml | 4,502 |
| Cadena de cerramiento CE-1 aparente 20x25 (365) | 15 m | Proporcional a los ml | 3,969 |
| **Total** | | | **26,289.28 (≈ $1,752.62/ml)** |

- **Castillo: piezas de 1.95 m de altura, 8 piezas en la modulación base de 15 ml** (decisión del usuario): 8 × 1.95 = 15.6 m, igual que Zafiro. Altura en `I3` y piezas base en `I4` (ambas editables).
- **Escalamiento:** a partir de cada **3 ml adicionales** se agrega un castillo (`K4`, editable): piezas del proyecto (`I5`) = `8 + ROUNDDOWN((ml − 15) / 3)`; cantidad proyecto = piezas × 1.95 m. Igual hacia abajo si bajan los ml.
- Separación de castillos a ejes de 3.95 ml y módulo de 7.00 ml: solo referencia, no agregan costo.
- Ejemplos: 12 ml (7 piezas) ≈ $21,380; 15 ml (8) = $26,289; 18 ml (9) ≈ $31,199; 21 ml (10) ≈ $36,108; 28 ml (12) ≈ $47,369.
- Las filas 39–42 del bloque informativo de MURO CONFINAMIENTO llevan la nota «ahora en Paramétrico BARDA».
- En las hojas con escalón (COCHERA) el «importe base Zafiro» de las partidas por escalón es 0 (corrección v22).

## 5. Decisiones tomadas

**Qué significa «Fijo»** (aclarado por el usuario): *fijo no significa que no sea editable*. Un concepto fijo **no escala automáticamente con un driver**, pero su cantidad sí se captura:
- En las hojas por driver (MURO, PISO, ASADOR, COCHERA…), la celda de **cantidad proyecto** de las partidas fijas es de captura (se marca como entrada) y arranca igual a la cantidad base.
- En las hojas por grupos (instalaciones, equipos), cada grupo fijo trae un factor **«Salidas proyecto (EDITABLE)» = 1** (columna E, «conjunto»): se puede poner 0 para quitarlo o 2 para duplicarlo.

1. El sillar queda fuera del driver de muro.
2. Si suben los m² de muro, suben también las cantidades de castillos, acero y cadenas (todo proporcional).
3. El driver se llama MURO DE CONFINAMIENTO.
4. El detalle debe traer todas las columnas de Hoja1, porque servirán para todos los demás drivers.
5. Meta: catálogo paramétrico lo más completo posible.
6. Muro por 5 capas con interruptores por capa; interior y fachada separados; acabados = REVESTIMIENTO (mármoles, piedras, canteras).

## 6. Hallazgos y problemas abiertos

| # | Hallazgo | Estado |
|---|---|---|
| 1 | 92 celdas con `#NAME?` en `Catálogo Geometría`: la columna "Regla" tiene `=igual`, que Excel toma como fórmula. | Pendiente |
| 2 | Clave `EST-10013` (K1 – 1.00 acero) aparece en las filas 81 y 85 de Hoja1 (20 y 4 pza). Posible duplicado. | Por confirmar |
| 3 | Acero de castillos de las filas 81, 84, 85 está en etapa "LOSAS PB" pero se cuenta como muro. | Por decidir |
| 4 | Acero de castillos de las filas 7–14 está en NIVEL "CIMENTACION" (ETAPA "ESTRUCTURA"). El driver reúne partidas de tres etapas. | Por decidir |
| 5 | Columna AREA vacía en todas las partidas de muro; DESARROLLO solo existe en el acero de castillos. | Por llenar |
| 6 | Muro de cisterna (fila 229) sin Nivel ERP ni Ingeniería ERP. | Pendiente |
| 7 | Cobertura inferida: NIVEL, ETAPA y UBICACIÓN son casi todos inferidos por regla; SUB-ELEMENTO y DESARROLLO vacíos en ~2,150 partidas. | Conocido |
| 8 | El precio es solo del modelo Zafiro 1.0; no sirve como referencia general sin ajustar. | Conocido |
| 9 | Castillos mezclan acero (por pieza) y colado (por metro); el precio por m² junta dos formas de medir. | Por revisar |

## 7. Pendientes y siguientes pasos

- [x] Pretil: lleva repellos, finas y chapeo en fachada, pero NO se considera por ahora (decisión del usuario).
- [ ] LOSA DE ENTREPISO: **diferida** (decisión del usuario); se define cuando se parametrice un modelo de dos plantas como Oro (datos de Oro en la sección 10C).
- [ ] Confirmar que los 165 m² de losa de azotea (125 + 40) son los m² correctos frente a 146–148 m² de relleno e impermeabilización.
- [ ] Confirmar el perímetro base de vanos (137 m) (el sellado de marcos de cantera interior ya quedó en 21 m).
- [ ] Relacionar puertas, cancelería y domos con los vanos (hoy fijos y editables); revisar muro neto/bruto frente a vanos.
- [x] Piso del travertino = 17.52 m²; muro = 27.48 m² (v12).
- [x] Hoja Paramétrico PISO creada (v13); el bloque PISO de MURO CAPAS queda como referencia.
- [x] Dover = asador (piso exterior) y pórfido aparte: hojas propias (v14).
- [ ] Confirmar zapatas y columnas del asador como FIJAS y el chaflán como proporcional.
- [x] Barda: el castillo de 1.95 m suma 1 pieza por cada 3 ml adicionales.
- [x] Drivers de instalaciones definidos (HIDROSANITARIAS, GAS y ELÉCTRICAS, v27); incluyen las del asador como grupos fijos.
- [x] Muebles sanitarios (MSA) y boiler (ACC-01010) van en HIDROSANITARIAS (v35); los equipamientos (EQU), en la hoja EQUIPOS.
- [x] Herrería, carpintería y cancelería: hojas fijas con piezas editables (v36).
- [ ] Cubiertas de baño: definir su driver (CUBIERTA ligada a los ml de vanity).
- [x] Redes principales escalan por m² de losa (decisión del usuario).
- [ ] Usuario: definir cuántos accesorios de cada tipo lleva cada elemento, y lo mismo para los muebles hidrosanitarios (MSA).
- [x] Matriz «cuánto sale una salida por etapa» hecha para ELÉCTRICAS y HIDROSANITARIAS (sanitaria, hidráulica y mueble). Falta evaluarla para GAS.
- [ ] Instalaciones: confirmar los grupos fijos restantes (hidroneumático, ventilación, tapas, centro de carga).
- [x] Cochera: escalón a +60% y a +160% (máx. 2 juegos); chaflán escala; sellado de columna (396) dividido entre asador y cochera.
- [x] Asador: el «lijado y sellado» era la fila 396 (limpieza y sellado de columna de cantera), no la 370 (muro interior); ya está dividida con la cochera.
- [x] «Hasta +160%» en la cochera confirmado (2º juego a +160%, máx. 2 juegos).
- [ ] Más adelante: hacer editable la longitud del asador (la fila 381, de 3.00 m, escalaría con ella).
- [ ] Plafón con LOSA DE ENTREPISO: asociar las tres capas cuando haya datos de otros modelos.
- [ ] Definir caso por caso el REVESTIMIENTO (mármoles, piedras, canteras).
- [x] Chapeo de piedra (184) es REVESTIMIENTO (confirmado).
- [ ] Llenar AREA y DESARROLLO de las partidas de muro de confinamiento.
- [x] Castillos de cimentación y de losas PB siguen contando como MURO y PRETIL (decisión del usuario).
- [x] `EST-10013` no es duplicado (distinto Ingeniería ERP).
- [x] Corregidos los `#NAME?` de `Catálogo Geometría` (v11).
- [ ] Propagar la ruta paramétrica a la columna Q de Hoja1 para MURO DE CONFINAMIENTO.
- [ ] Definir el siguiente driver (propuesta: LOSA, el segundo elemento por importe).
- [x] Cantidades con decimales por ahora (sin `ROUNDUP`); se retoma después.
- [ ] Recalcular y revisar el libro en Excel (aún no verificado fuera de Python).

## 8. Driver PRETIL (hoja Paramétrico PRETIL)

Driver: m² de muro de pretil (`D4`; base 62 m², fila 166). Cuatro capas con interruptores Sí/No: obra negra, obra gris, obra blanca y pintura (sin revestimiento por ahora).

| Capa | Partidas (fila) | Importe base | $/m² pretil |
|---|---|---|---|
| Obra negra | Muro tabique (166), castillo K-1 (167), cadena (183) | 29,656 | 478.32 |
| Obra gris | Repellado 3.00 (172), repellado fachada +3.00 (173, solo 62 m²), boquilla exterior (174) | 26,863 | 433.27 |
| Obra blanca | Finas exteriores (177), boquilla fina (178), finas fachada +3.00 (182, solo 62 m²) | 12,448 | 200.77 |
| Pintura | Lijado y sellado (370, cantidad de 399), pintura fachada 1ª y 2ª mano (399, 400) | 8,721 | 140.65 |
| **Total** | | **77,688** | **≈ 1,253.03** |

Observaciones: la boquilla exterior (174, estuco) y la boquilla fina (178, estuco fino) del pretil están confirmadas, 105 m cada una. Zafiro no tiene lijado y sellado de pretil: se usa la clave y precio de ACA-30010 (fila 370, única partida de lijado de muro en todo Hoja1) con los 107 m² de la pintura del pretil. 172 y 173 vienen clasificadas OBRA BLANCA en FAMILIA pero son repellado (obra gris). Las filas 399–400 tienen UBICACIÓN interior aunque el concepto dice fachada.

## 9. Driver VANO (hoja Paramétrico VANO) — inicial

Decisión del usuario: **puertas, cancelería y domos quedan APARTE** (no entran en VANO ni en ningún total; se relacionan después). VANO solo incluye lo medido por **perímetro**. El muro de 279 m² está medido NETO; se revisa después.

| Capa | Partidas (fila) | Importe base | $/m perímetro |
|---|---|---|---|
| Obra gris | Boquilla interior (152) y fachada (204) | 6,961 | 50.81 |
| Obra blanca | Boquilla fina interior (161) y fachada (205) | 1,130 | 8.25 |
| Revestimiento | Marcos de cantera interior (162) y fachada (186) y su sellado (378, 391) | 30,530 | 222.85 |
| **Total** | | **38,620** | **≈ 281.90** |

- **Sellado de marco interior = 21 m** (decisión del usuario): Hoja1 trae 14.4 m en la fila 378; se ajusta a los 21 m del marco (fila 162). Sube el sellado de $977 a $1,425.
- **Perímetro base = 137 m** (boquilla interior 127 + fachada 10): supuesto a confirmar.
- **Aparte (fuera de totales):** puertas de intercomunicación, baño y principal (272–274), puerta de cuarto de máquinas (329), cancelería (258) y domos (260).

## 10. Driver LOSA (hoja Paramétrico LOSA)

**Desde v15 la LOSA DE PISO (cimentación) ya no está aquí: pasó a la hoja Paramétrico PISO como capa de obra negra.** Esta hoja conserva LOSA DE AZOTEA, el plafón (10B) y el entrepiso pendiente.

Se separa en **LOSA DE PISO** (la de cimentación), **LOSA DE AZOTEA** y **LOSA DE ENTREPISO** (Zafiro es de un nivel y no tiene; queda pendiente, hay datos en otros modelos en la hoja Claves sin Zafiro). En Hoja1 las losas vienen como **pieza global (act)** y se **convierten a m²** con los m² de su descripción (fórmula que los lee del texto, ver `D4`/`C5` de la hoja).

| Driver | Capa | Partida (fila) | m² base | Importe base | $/m² |
|---|---|---|---|---|---|
| Losa de piso | Obra negra | Losa de cimentación (6) | 172 | 130,105 | 756.42 |
| Losa de azotea | Obra negra | Losa maciza 3.00 (79) | 125 | 130,198 | 1,041.59 |
| Losa de azotea | Obra negra | Losa nervada 4.20 (83) | 40 | 59,476 | 1,486.91 |
| Losa de azotea | Obra gris | Relleno antihumedad (170, 146 m²) y chaflán (171, 107 m) | — | 52,938 | 320.84 sobre 165 m² |
| Losa de azotea | Impermeabilización | Impermeabilización subcontrato (402, 148 m²) | — | 19,241 | 116.62 sobre 165 m² |

- **Losa de piso:** $130,105 en total, unos **$756.42/m²** (sobre 172 m²).
- **Losa de azotea:** base de 165 m² (125 maciza + 40 nervada); total $261,854, unos **$1,587.00/m²** con las tres capas.
- **No entran:** las instalaciones de cimentación (otros drivers) ni el acero de castillos y la gualdra de las filas de losa (80, 81, 84, 85), que son de MURO. Las losas de cisterna, asador y firmes de cochera tampoco (otros elementos).
- Los ratios de chaflán, relleno e impermeabilización se calculan por m² de losa de azotea; el relleno (146 m²) y la impermeabilización (148 m²) no coinciden con los 165 m² de losa.

## 10B. Plafón bajo losa (hoja Paramétrico LOSA, filas 27–44)

El plafón de planta baja **cuelga de la losa de azotea** y usa sus m² como driver (165 m²; el plafón de Zafiro mide 147 m², ratio 0.891). Tres capas con interruptor, nombradas PLAFÓN OBRA GRIS, PLAFÓN OBRA BLANCA y PLAFÓN PINTURA para no chocar con las capas de la losa.

| Capa | Partidas (fila) | Importe base |
|---|---|---|
| Plafón obra gris | Repellado plafond 3.00 (149, 111 m²) y +3.00 (150, 36 m²) | 25,152 |
| Plafón obra blanca | Finas plafond 3.00 (159) y 4.20 (160) | 11,123 |
| Plafón pintura | Lijado y sellado (373), pintura 1ª y 2ª mano (374, 375) | 8,117 |
| **Total plafón** | | **≈ 44,393 (≈ $269.05 por m² de losa)** |

- La fila 33 de la hoja suma losa de azotea + plafón.
- **Con entrepiso** el plafón de planta baja se asociará a LOSA DE ENTREPISO con estas mismas tres capas (pendiente de datos).
- La pintura de plafón sigue la misma regla de capas con interruptor que en muro y pretil.

## 10C. Losa de entrepiso — diferida (referencia Oro)

Decisión del usuario: la losa de entrepiso **se deja para un modelo de dos plantas como Oro**; no se parametriza con Zafiro (una planta). El plafón de planta baja con entrepiso se asociará a esa losa con las tres capas de la sección 10B.

Datos de **Oro 4.01 (300 m², 4 recámaras y 1 estudio; capítulo desde la fila 2703 de Hoja1)** para cuando se retome:

| Fila | Partida | Cantidad | Importe |
|---|---|---|---|
| 2774 | Losa nervada de 0.20 m, **entrepiso** (EST-51016) | 45.60 m² | 79,091 |
| 2775 | Losa nervada de 0.20 m, «azotea» en planta baja (EST-51010) | 140 m² | 159,086 |
| 2776 | Cadena intermedia 15x70 | 10 | 3,028 |
| 2777 | Escalera forjada de una rampa (PB) | 18 pza | 13,239 |
| 2903 | Losa maciza de 12 cm, azotea (PA) | 80 m² | 88,631 |
| 2904 | Losa maciza de 11 cm, azotea (PA) | 24 m² | 25,871 |
| 2906 | Escalera forjada (PA) | 6 pza | 4,413 |

- Oro agrupa LOSAS PB ($268,595) y LOSAS PA ($119,696). La losa de cimentación de Oro es de 160 m² ($123,431).
- **Inconsistencia a resolver en su momento:** la losa de entrepiso rotulada mide 45.60 m², pero la planta alta de Oro tiene ≈ 104 m² de losa (80 + 24); la losa nervada de 140 m² está rotulada como «azotea» dentro de LOSAS PB. Hay que confirmar cuál es el entrepiso real.
- Las escaleras, las cadenas intermedias y las gualdras de las losas de Oro irán a su driver correspondiente.

**CUBIERTA (pendiente).** Las cubiertas de mármol (filas 324 y 325, 3.6 ml sencilla + 2.05 ml doble = 5.65 ml, ≈ $16,049 en Zafiro) corresponderán a los **ml de muebles de baño (vanity)**. Se deja pendiente por decisión del usuario.

## 11. Drivers PISO, ASADOR y PÓRFIDO

**PISO** — base **157.33 m²** (Lugano 57 + Brunei 78 + tomboleado 4.81 + travertino 17.52). Desde v15 incluye la **losa de piso (cimentación)** como capa de obra negra; la losa mide 172 m² y escala con los m² de piso (ratio 172 / 157.33 = 1.093).

| Capa | Partidas (fila) | Importe base | $/m² piso |
|---|---|---|---|
| Obra negra | Losa de cimentación (6, pieza global convertida a 172 m²) | 130,105 | 827.00 |
| Obra gris | Renivelación de charolas (190), sardinel (191), vertedero (192) | 1,767 | 11.23 |
| Revestimiento | Loseta y zoclo Lugano (193, 194) y Brunei (195, 196); tomboleado piso y sellado (197, 377, cantidad = fila 190); travertino piso y limpieza (199, 383, cantidad = 17.52) | 85,395 | 542.78 |
| **Total** | | **≈ 217,267** | **≈ 1,380.96** |

**ASADOR** — base 13.32 m² (piso Dover, fila 200). Decisión del usuario: la pérgola, el forjado y el revestido son **FIJOS**; si crece el área de asador, el asador no cambia de precio.

| Capa | Escala | Partidas (fila) | Importe base |
|---|---|---|---|
| Obra negra | Sí | Firme de concreto 10 cm (334) | 4,282 |
| Obra gris | Sí | Chaflán antihumedad (339) | 834 |
| Revestimiento | Sí | Piso Dover (200) | 5,359 |
| Pérgola (FIJO) | No | Pérgola asador 14.80 m² (359) | 25,726 |
| Asador forjado y revestido (FIJO) | No | Zapatas Z-1 (335), columnas forradas (336), forjado (337), forrado de cantera (338), limpieza y sellado del asador (381, 3.00 m), limpieza y sellado de columna de cantera (396, mitad: 6.9 m = 1,323) | 15,589 |
| **Total** | | | **≈ 51,790** (las capas que escalan ≈ $786.37/m²; las fijas ≈ $41,315) |

- Ejemplo: con 20 m² de área de asador el total sería ≈ $57,043 (solo crece el piso).
- Supuestos a confirmar: zapatas y columnas forradas se tratan como fijas (cimentación y soporte del asador y la pérgola); el chaflán escala con el área.
- La fila 381 es el sellado del asador (3.00 m de longitud): FIJA por ahora; si más adelante se decide crecer la longitud del asador, escalaría con ella (hoy no es editable).
- La limpieza y sellado de columna de cantera (fila 396, 13.8 m) se divide a partes iguales entre asador y cochera.
- **Instalaciones:** las del asador (filas 343–357, ≈ $3,696) ya están en las hojas de HIDROSANITARIAS, GAS y ELÉCTRICAS como grupos fijos; el equipo (319) y los accesorios (310) quedan fuera (pendiente).

**PÓRFIDO** — base 57 m² (fila 238). Una capa de revestimiento: pórfido, boquilla (m²), zoclo y jardinera (m, escalan con los m²). Total ≈ $30,856, ≈ $541.34/m².

- Sardinel (m) y vertedero (pza) escalan proporcional a los m² de piso. No se incluyen los poyos de cocina (153).
- Los elementos fijos usan escalamiento "Fijo" en Rutas (cantidad proyecto = cantidad base).
- Importes calculados en Python desde Hoja1 (sin motor de Excel); falta confirmar al abrir el libro.

## 11B. Driver COCHERA (hoja Paramétrico COCHERA)

Pérgola de cochera (subcapítulo PERGOLADO COCHERA, $60,330.09 en Zafiro). Driver: m² de pérgola (`D4`; base **29.92 m²**, tomados de la descripción de la fila 412).

| Capa | Escalamiento | Partidas (fila) | Importe base |
|---|---|---|---|
| Pérgola | Proporcional a los m² | Pérgola cochera (412, pieza global convertida a m²) | 51,762 |
| Obra gris | Proporcional (como en el asador) | Chaflán antihumedad (409) | 834 |
| Estructura base (FIJO) | No escala | 2 zapatas Z-1 (406), 1 columna de cantera (407), 1 columna forrada (408), sellado de columna de cantera (396, mitad) | 9,057 |
| Columnas adicionales (ESCALÓN) | Por umbral | +1 columna de cantera con su limpieza y sellado (396, 6.9 m), +1 forrada y +2 zapatas por juego | 0 en la base (9,057 por juego) |

**Regla del escalón** (decisión del usuario): 1er juego al crecer **+60%** y 2º juego al llegar a **+160%** (máximo 2 juegos). Parámetros en la hoja: `I3` umbral 1 (60%), `I4` umbral 2 (160%), `K5` crecimiento del proyecto, `I5` juegos adicionales.

- Total base ≈ $61,653 (los $60,330 de Hoja1 + el sellado de columna de cantera, que sale de otra partida).
- Ejemplos: con +60% ≈ $102,268; con +160% ≈ $163,921.
- Supuestos a confirmar: «hasta +160% las siguientes dos» se leyó como 2º juego a +160% y tope de 2 juegos; cada columna de cantera adicional suma su limpieza y sellado (396, 6.9 m por juego).
- **Instalaciones de cochera aparte.**

## 11C. Drivers de INSTALACIONES: HIDROSANITARIAS, GAS y ELÉCTRICAS

Decisión del usuario: se separan **hidrosanitarias** y **gas**; las **eléctricas van aparte**. Tres hojas con la misma estructura, porque las instalaciones se miden por **salidas** y no por m²:

- **Tabla de salidas por grupo:** cada aparato (WC, lavamanos, regadera, contactos, apagadores…) es un grupo con sus **salidas base** (de Zafiro) y sus **salidas del proyecto** (columna E, editable). Al cambiar las salidas escalan todas las partidas del grupo (cimentación, muros, cableado y dispositivos).
- **Grupos «Fijo»:** equipo, asador y varios no cambian.
- **Grupos «Por m² de losa»** (decisión del usuario): las **redes principales escalan con los m² de la losa**. Se enlazan a la losa de cimentación de la hoja PISO (172 m² en la base, `'Paramétrico PISO'!M17`); si se agrega entrepiso se revisará qué losa corresponde.
- **Capas con interruptor Sí/No** y un renglón de $/m² de construcción (informativo, 172 m²).
- Cobertura completa: todas las partidas ISN, IHD, IGAS e IEC de Zafiro (más el material de consumo ACC-00001) están repartidas, sin duplicados.

**HIDROSANITARIAS — $88,072 (instalación $45,134 + muebles $42,939)**

Decisión del usuario: **los muebles (WC, regadera, lavamanos, tarja, calentador, etc.) van con hidrosanitarias.** La hoja tiene tres capas con interruptor Sí/No: **SANITARIA** ($26,406), **HIDRÁULICA** ($18,728) y **MUEBLES** ($42,939; claves MSA y boiler estándar ACC-01010). Igual que en las eléctricas, la columna A del detalle es el aparato y la C la etapa, y a la derecha de la tabla de grupos está lo que **cuesta una salida** en cada etapa:

| Aparato (grupo) | Salidas | Sanitaria | Hidráulica | Mueble | **Total / salida** |
|---|---|---|---|---|---|
| WC | 4 | 554.38 | 445.68 | 3,011.64 | **4,011.70** |
| Lavamanos | 4 | 465.93 | 424.66 | 1,340.16 | **2,230.75** |
| Regadera | 3 | 416.62 | 1,388.27 | 1,358.01 | **3,162.90** |
| Tarja de cocina | 1 | 462.65 | 420.91 | 2,797.85 | **3,681.41** |
| Lavadero | 1 | 459.38 | 458.64 | 949.08 | **1,867.10** |
| Lavadora | 1 | 502.45 | 698.97 | 659.56 | **1,860.98** |
| Lavavajillas | 1 | 476.72 | 475.49 | 413.27 | **1,365.48** |
| Refrigerador | 1 | — | 208.18 | 206.64 | **414.82** |
| Boiler / calentador | 1 | — | 1,024.75 | 5,326.86 | **6,351.61** |
| Llave de nariz | 3 | — | 310.08 | 325.94 | **636.02** |
| Minisplit (condensado) | 4 | 1,835.38 | — | 548.87 | **2,384.25** |
| Respiración / rejillas | 3 | 266.21 | — | 233.13 | **499.34** |
| Bajada de agua pluvial (BAP) | 6 | 488.52 | — | — | **488.52** |
| Coladera de piso | 1 | 614.62 | — | 399.77 | **1,014.39** |
| Coladera de jardín (1 por cada 22.5 m² de jardín con sello) | 1 | 618.01 | — | 399.77 | **1,017.78** |
| **Por m² de losa:** redes principales (líneas fría y caliente, cisterna, domiciliaria, principal sanitaria) | 172 m² | 10,100 | | | 58.72/m² |
| **Fijos:** vertedero (por decisión del usuario; mueble $839), hidroneumático (presurizadora $4,530), varios (material de consumo) y asador (tarja; accesorios $1,063) | | instalación 3,634 + mueble 6,432 = 10,066 | | | |

**Coladera de jardín (decisión del usuario):** 1 por cada **22.5 m² de jardín con sello** (`D4` = m² de jardín con sello del proyecto, base 22 m² de «SELLO 5 CM», fila 250; `I4` = 22.5, editable); coladeras = `ROUNDUP(m² / 22.5)`. Se enlaza a la coladera de jardín de MUEBLES Y EQUIPOS.

**GAS — $8,311** (escalan $4,651; fijos $3,660): boiler 1 ($609), estufa 1 ($786), secadora 1 ($646), estancia 1 ($649), recámara 3 ($1,962, $654 c/u). Fijos: tanque estacionario, caja de válvulas y asador.

**ELÉCTRICAS — $68,101: cuánto sale una salida, por etapa y por accesorio**

Decisión del usuario: se necesita saber **cuánto sale una salida desde cimentación, muros, losas, cableados y accesorios**, y el **concepto de accesorio guía la columna A (grupo)**. En la hoja ELÉCTRICAS:

- Las **capas son las etapas de la salida**: CIMENTACIÓN, MUROS, LOSA, CABLEADO y ACCESORIOS (cada una con interruptor Sí/No).
- La columna A de la tabla de grupos y del detalle es el **tipo de accesorio** (apagador sencillo, doble, triple, de escalera; contacto dúplex, de fuerza, USB, intemperie; TV; centro de luz; arbotante; spot; minisplit). El detalle lleva **Grupo (accesorio)** en la columna A y **Etapa** en la C.
- A la derecha de la tabla de grupos (columnas K–P) están los **$/salida por etapa y el total por salida** de cada accesorio.
- Las **salidas de cada tipo** (columna E) se editan por separado; ahí se captura lo que decida el usuario por elemento. La salida de cimentación y de muros (y los registros) se reparte entre los tipos de apagador y de contacto en proporción a sus salidas (21 apagadores y 46 contactos, contando los del asador, que quedan dentro de sus tipos: contacto de intemperie y apagador sencillo).

| Accesorio (grupo) | Salidas | Cimentación | Muros | Losa | Cableado | Accesorio | **Total / salida** |
|---|---|---|---|---|---|---|---|
| Apagador sencillo | 9 | 67.06 | 89.26 | — | 139.96 | 103.93 | **400.21** |
| Apagador doble | 6 | 67.06 | 89.26 | — | 219.91 | 128.14 | **504.37** |
| Apagador triple | 3 | 67.06 | 89.26 | — | 299.87 | 142.76 | **598.95** |
| Apagador de escalera | 3 | 67.06 | 89.26 | — | 199.88 | 93.40 | **449.60** |
| Contacto dúplex | 37 | 67.74 | 96.41 | — | 248.52 | 122.33 | **535.00** |
| Contacto de fuerza | 4 | 67.74 | 96.41 | — | 385.55 | 122.33 | **672.03** |
| Contacto USB | 3 | 67.74 | 96.41 | — | 248.52 | 407.74 | **820.41** |
| Contacto intemperie | 2 | 67.74 | 96.41 | — | 248.25 | 124.00 | **536.40** |
| TV | 4 | 92.66 | 61.16 | — | — | 82.25 | **236.07** |
| Centro de luz (soquet) | 17 | — | — | 125.33 | — | 181.73 | **307.06** |
| Arbotante | 14 | — | — | 137.06 | 146.58 | — | **283.64** |
| Spot de plafón | 15 | — | — | 198.00 | — | 341.33 | **539.33** |
| Minisplit (eléctrico) | 4 | — | — | 99.94 | — | — | **99.94** |

- **Escalan por salidas:** $53,686. **Redes principales** (acometida y cable, $1,229) escalan con los m² de la losa de cimentación. **Fijos** ($13,186): timbre y zumbador, centro de carga, tapas ciegas y especiales (con TV aérea y paneles solares), arbotante y cableado de la pérgola del asador, murete de instalaciones.
- Los cableados quedan ligados a su accesorio (misma fila de grupo). Si un accesorio no tiene partida de cableado o de accesorio propia en Zafiro (por ejemplo, el centro de luz no trae cableado y el arbotante no trae accesorio), esa etapa queda en cero.
- El resumen por «tipo» (iluminación/accesorios/infraestructura) de las versiones 31 y 32 se sustituyó por esta estructura.
- **Pendiente del usuario:** decidir **cuántos accesorios de cada tipo lleva cada elemento** (recámara, baño, etc.) para las eléctricas, y lo mismo para los **muebles hidrosanitarios** (MSA). Con eso se calculan las salidas del proyecto (columna E).
- Importes calculados en Python desde Hoja1 (sin motor de Excel); falta confirmar al abrir el libro.

- **Muebles y equipos:** los muebles sanitarios (MSA), el boiler estándar y los equipamientos (EQU) están en la hoja MUEBLES Y EQUIPOS (sección 11D).
- Importes calculados en Python desde Hoja1 (sin motor de Excel); falta confirmar al abrir el libro.

## 11D. Driver EQUIPOS (hoja Paramétrico EQUIPOS)

Cubre las claves EQU de Zafiro: **$33,211**, una capa con interruptor. Los **muebles sanitarios y accesorios (MSA, boiler estándar) pasaron a HIDROSANITARIAS** (sección 11C) por decisión del usuario; esta hoja ya no los lleva.

Las piezas del proyecto (columna E) están enlazadas a las salidas de HIDROSANITARIAS y GAS:

| Grupo | Piezas base | Importe | $/pieza | Enlace |
|---|---|---|---|---|
| Estufa | 1 | 7,354 | 7,354 | Estufa (GAS) |
| Campana | 1 | 2,404 | 2,404 | Estufa (GAS): una campana por estufa |
| Set de accesorios de baño (baño completo) | 3 | 3,027 | 1,009 | `MIN(WC, regaderas)` |
| Set de medio baño | 1 | 909 | 909 | `MAX(0, WC − regaderas)` |
| **Fijos:** asador (equipo, $2,800), tanque de gas ($8,503), cisterna prefabricada de 3,000 L ($8,214) | | 19,517 | | |

- Escalan por piezas $13,694; fijos (editables) $19,517. Estufa y campana van **por separado** (decisión del usuario).
- **Fuera de esta hoja:** las cubiertas de baño y los muebles vanity (CUBIERTA, ligada a los ml de vanity), la carpintería (cocina, closets, puertas) y la iluminación y accesorios eléctricos (ELÉCTRICAS).
- Importes calculados en Python desde Hoja1 (sin motor de Excel); falta confirmar al abrir el libro.

## 11E. Drivers HERRERÍA, CARPINTERÍA y CANCELERÍA (fijos por ahora, editables)

Decisión del usuario: **herrería, carpintería y cancelería son fijas de momento** (no escalan con un driver), pero sus piezas son **editables**. Cada concepto es un grupo con su cantidad base de Zafiro y su cantidad del proyecto (columna E, editable, por defecto igual a la base). Se relacionarán con los vanos y las cubiertas más adelante.

| Hoja | Total | Contenido |
|---|---|---|
| **HERRERÍA** | **$15,390** | Puerta del cuarto de máquinas (3.45 m², $2,765/m²), escalera marina (1), tapas de nicho de gas (4) |
| **CARPINTERÍA** | **$196,671** | Muebles ($135,928): cocina ($65,060), alacena (0 pzas, $12,000 c/u), closets de recámara 1 y 2 ($20,100 c/u), vestidor ($21,384), vanity de baño (3 × $2,808), vanity de medio baño ($860). Puertas ($60,743): intercomunicación (4 × $6,427), baños (4 × $6,417), principal 2 hojas ($9,369) |
| **CANCELERÍA** | **$85,533** | Cancelería ($53,220, monto global) y domos ($32,313, monto global) |

- Los tres totales coinciden con los subcapítulos de Hoja1.
- La alacena viene con cantidad 0 en Zafiro; se activa capturando piezas.
- Las puertas, la cancelería y los domos eran la lista «APARTE» de VANO; ahora tienen su hoja (la lista de VANO lleva una nota).
- Pendiente: relacionar puertas, cancelería y domos con los vanos, y los vanity con las cubiertas de baño (ml de vanity).
- Importes calculados en Python desde Hoja1 (sin motor de Excel); falta confirmar al abrir el libro.

## 11F. Hojas nuevas de ZAFIRO (v37–v44) — reconstruido de los libros

Todas con la misma estructura de capas con interruptor Sí/No, tabla de detalle por partida (fila de Hoja1, clave, cantidad base, precio, ratio) y «Todas las capas» frente a «Combinado (solo capas en Sí)».

| Hoja | Aparece en | Driver | Capas / contenido (filas de Hoja1) |
|---|---|---|---|
| **OBRA EXTERIOR** | v37 | Ninguno (FIJA; cantidades editables, celdas amarillas, col. M) | Registros sanitarios 60x40 y tapas (235, 236); murete de instalaciones (241); plantas de ornato: durantas, fornio, lirio, suculenta (252–255) |
| **JARDÍN** | v37 | m² de jardín con sello (base fila 250), **ligado a `D4` de HIDROSANITARIAS** para capturarlo en un solo lugar | SELLO (excavación manual 249 y sello de 5 cm 250) y PASTO (kicuyo 251), independientes: se puede llevar solo sello, solo pasto o ambos |
| **CUBIERTA** | v37 | Dos drivers lineales: ml de cubierta (`D4`, filas 324+325) y ml de poyo (`D6`, fila 153) | Cubiertas de mármol travertino sencilla y doble (324, 325); poyos de cocina (153). Se relacionarán después con los ml de vanity de CARPINTERÍA (pendiente de la sección 7) |
| **CISTERNA** | v38 | Volumen en litros y número de piezas. Base 3,000 L; hasta **6 cisternas** del proyecto, cada una con capacidad y piezas propias | OBRA NEGRA (afine 227, firme 228, muro 229, losa 232, tapa 233, boquilla 234), OBRA GRIS (repellado 230), OBRA BLANCA (fino 231) y EQUIPO (cisterna prefabricada 245). Tapa y boquilla escalan por PIEZA; lo demás por VOLUMEN (editable en col. L). **La cisterna prefabricada salió de EQUIPOS, donde quedó en cero** |
| **MARCOS EXTERIORES** | v44 | m de marco de cantera exterior (base fila 186) | OBRA GRIS: boquilla de fachada (204); OBRA BLANCA: boquilla fina de fachada (205); REVESTIMIENTO: marcos de cantera exteriores (186) y su sellado (391). Lo interior se queda en VANO. La boquilla (10 m) escala con los metros de marco; si la relación es otra, se ajusta la cantidad |

- **VANO (confirmado en v44):** pasa a ser solo perímetro **INTERIOR** (boquillas y marco de cantera interior); los marcos, sellado y boquillas exteriores (186, 204, 205, 391) están en MARCOS EXTERIORES.
- **VANO (v41):** se quitó la lista «APARTE». Puertas, cancelería y domos ya están cobrados en CARPINTERÍA (puertas), HERRERÍA (puerta del cuarto de máquinas) y CANCELERÍA (cancelería y domos).
- **Lijado y sellado (v38):** en MURO CAPAS (fachada) y en PRETIL la cantidad base queda en **0**: Zafiro no tiene esas partidas y la fila 370 (432 m²) ya se usa en el interior de MURO; se conserva solo el precio para escalar.
- **Sellado de marco interior (v38→v42):** en v38 se ligó a la fila 378 (14.4 m) y en v42 se regresó a los 21 m del marco (fila 162) como **excepción autorizada**.
- **Historia de reubicaciones:** en v37 la cisterna estaba dentro de OBRA EXTERIOR y JARDÍN tenía la capa PLANTAS; en v38 la cisterna pasó a su hoja y JARDÍN se dividió en SELLO / PASTO / PLANTAS; en v39 las plantas pasaron a OBRA EXTERIOR y JARDÍN quedó en dos capas.
- **CUBIERTA (v38):** el $/unidad de las capas usa el driver de cubierta (`D4`); los poyos escalan con `D6`.

## 11G. Panel de control y presupuesto generado (v40) — reconstruido de los libros

- **PARAMÉTRICOS ZAFIRO** (panel): una fila por hoja paramétrica con driver, unidad, valor base, valor del proyecto, importe del proyecto (capas en Sí), $/unidad de driver y número de partidas en Sí. Los valores del proyecto se editan en la hoja de cada paramétrico (columna D) y el panel solo los lee. Suma un TOTAL de los paramétricos.
- **PRESUPUESTO ZAFIRO**: copia de Hoja1 (mismas columnas) cuyas cantidades salen de los paramétricos; reconstruye el presupuesto completo de Zafiro con los valores del proyecto.
- **Control de cobertura y cuadre** (en el panel): presupuesto base de Hoja1 vs. presupuesto generado y su diferencia (cero solo si los valores del proyecto son los base de Zafiro); conceptos de Zafiro **sin paramétrico (debe ser 0)**; conceptos con cantidad base mayor que Hoja1 (debe ser 0); conceptos con importe distinto al de Hoja1.
- En **v41** se eliminó la hoja `Claves sin Zafiro`.
- Estado: **no verificado en Excel**; hay que abrir el libro y revisar que los controles den 0 antes de darlo por cuadrado.

## 13. Línea ORO (Oro 4.01, 300 m², dos plantas) — reconstruido de los libros

`CATALOGO_PARAMETRICO_ORO_v1.xlsx` (8:23 p. m.) → `..._v18.xlsx` (11:21 p. m.). Reutiliza la arquitectura de Zafiro: panel **PARAMÉTRICOS ORO**, **PRESUPUESTO ORO**, **Rutas**, **Hoja1** (catálogo de Oro) y una hoja por driver. Se quitaron las hojas propias de Zafiro (MURO CONFINAMIENTO, MURO CAPAS, Leyenda Q-Z, Catálogo Geometría).

**Hojas (v18, 32 en total).** Hojas nuevas respecto de Zafiro por ser de dos plantas o propias de Oro:

| Hoja | Contenido (filas de Hoja1 de Oro) |
|---|---|
| **MURO PB** | Cimentación: castillos K1/K2/K3/K7 (7–13); PB: tabique 14 cm (65), castillos (67–70), cadena CE-1 (71); repellado (180, 181); finas (190, 191); revestimiento: mármol tomboleado (296), jabonera (297), travertino (298), durmiente (515), sellado (516), limpieza (519); pintura interior (511) |
| **MURO PA** | Cadena intermedia 15x70 (77), castillos y gualdra (79–83); PA: tabique (198), castillos, cadenas CE-1/CE-2 (199–205), K1-1.50 (212); repellado (247, 248); finas (254, 255); revestimiento: ojo de buey (206), mármoles (307–309) y sus sellados/limpiezas (524–527) |
| **MURO FACHADA** | Repellado fachada 3.00/+3.00 (184, 185); finas fachada 3.00/+3.00 (277, 278); chapeo de piedra (281); rodapiés 60 y 20 cm (315, 316) y limpiezas (532, 534, 535, 537); pintura fachada (530). **Altura editable 3.00 o 4.20** (`D5`): cambia cuál de las dos partidas se cobra |
| **LOSA** (azotea) | Losa maciza y maciza inclinada (210, 211); relleno antihumedad (266) y chaflán (267); plafón PA con 3 capas (249–250, 256–257, 522); impermeabilización (543) |
| **LOSA ENTREPISO** | Losa nervada de entrepiso (75) y nervada «azotea» de PB (76); plafón PB con 3 capas (182–183, 192–193, 512). **Retoma lo diferido en la sección 10C** |
| **PISO PB** | Ligado a la losa de cimentación de 160 m²: losa de cimentación (6); renivelación, sardinel, vertedero (288–290); Lugano y Brunei con zoclo (291–294); tomboleado y travertino de piso (296, 298) con sellado y limpieza (516, 519) |
| **PISO PA** | Ligado a la losa de entrepiso: sardinel y renivelación (310, 311); Lugano y Brunei (302–305); mármoles (307, 308) y sus sellados (524, 525) |
| **ESCALERA** | Driver en piezas. Escalón forjado de 1.00 PB y PA (78, 213) y forrado Brunei (295, 306) |
| **OBRA COMPLEMENTARIA** | Fijas: durmiente 20x20 (282), goterón (284), tejas sobre losa (314), viga ornamental de 60 cm (317) |
| **MARCOS EXTERIORES** | Boquilla de fachada (320), boquilla fina exterior (321), marcos de cantera (283) y sellado (533) |

Se conservan, adaptadas a Oro: PRETIL, VANO, ASADOR, PÓRFIDO, COCHERA, SILLAR, BARDA, JARDÍN, CUBIERTA, CISTERNA, OBRA EXTERIOR, HIDROSANITARIAS, GAS, ELÉCTRICAS, EQUIPOS, HERRERÍA, CARPINTERÍA y CANCELERÍA.

**Evolución por versión (comparación celda por celda de los libros):**

| Versión | Cambio |
|---|---|
| v1 | Estructura de Oro: MURO, LOSA ENTREPISO, ESCALERA, OBRA COMPLEMENTARIA, panel y PRESUPUESTO ORO. |
| v2 | HIDROSANITARIAS, GAS, ELÉCTRICAS y EQUIPOS se rehacen con la estructura de Zafiro (grupos por salidas, «Por salidas» vs. «Fijo»); JARDÍN se liga a HIDROSANITARIAS. |
| v3–v6 | Calibración de eléctricas e hidrosanitarias contra los accesorios de cada planta: contactos de muros PB = 49 (Hoja1 trae 40), lavamanos, minisplit, TV, arbotante y spot (ver excepciones abajo). |
| v7–v8 | Se agregan a Hoja1 las partidas del **lavavajillas** (salida sanitaria de cimentación y ranura/conexión de muros PB; clave y precio de Zafiro). |
| v9 | Se agregan 12 conceptos de Zafiro que Oro no traía (coladera de jardín y de piso, domiciliaria hidráulica, caja de válvulas de gas, timbre, zumbador, centro de carga, tapas ciegas de TV, voz y datos, internet aéreo y paneles solares); rehace instalaciones. |
| v10–v11 | ASADOR: la pérgola pasa a tener su propio driver (m² de pérgola) y se agrega una capa de obra gris; COCHERA se ajusta igual. |
| v12–v13 | LOSA: la base de azotea queda en 80 + 24 m² (la nervada de 140 m² se va a LOSA ENTREPISO); plafón de PB con 3 capas en LOSA ENTREPISO; plafón PA ajustado a 104 m² (= losa PA). |
| v14 | **MURO se parte en MURO PB / MURO PA / MURO FACHADA, PISO en PISO PB / PISO PA, y se agrega MARCOS EXTERIORES**; VANO queda solo interior. |
| v15 | Renivelación de charolas PA = 6.24 m² (= tomboleado de piso PA). |
| v16 | BARDA pasa a metros lineales (15 ml base) con castillo de altura y piezas editables, igual que en Zafiro. |
| v17 | Se agregan 5 conceptos: limpieza y sellado de ojo de buey, durmiente y columna de cantera, boquilla de fachada a base de estuco y escalera marina (herrería); MARCOS EXTERIORES gana capa de obra gris; se reordenan filas de Hoja1 (los demás libros se re-ligan). |
| v18 | Se documentan las excepciones autorizadas y los conceptos agregados (ámbar) en el panel. |

**Criterios de ORO escritos en el libro (excepciones autorizadas)**
- **Mármol y piso compartidos:** el mármol tomboleado y el travertino se reparten entre MURO y PISO. PB: tomboleado 13 → 11.2 m² muro + 1.8 m² piso; travertino 23 → 9.76 muro + 13.24 piso. PA: tomboleado 43 → 36.76 muro + 6.24 piso; travertino 48 → 28.36 muro + 19.64 piso. La renivelación de charolas PB (0.1 en Hoja1, «error de captura») se toma como 1.8 m².
- **Plafón PA = losa PA = 104 m²** (repellado y finas ajustados de 90.47 a 85.93 m²; pintura de 108.54 a 104).
- **Hidrosanitarias:** lavamanos hidráulica de muros PB = 3; lavamanos 3 PB + 4 PA = 7; minisplit 2 PB + 3 PA = 5 (cimentación de PA en losa entrepiso 4.20).
- **Eléctricas:** contactos de muros PB = 49 (= salidas de cimentación PB); USB 3, todos en PB; contacto de intemperie 5 (cableado y accesorio), con el duplicado de la fila 402 en 0; apagadores 23 en PB; TV 3 PB y 3 PA; spot de escalera 4 PB y 2 PA; arbotante 4 en PA (= losa PA); spot de plafón 6 en PA.

**Control de cuadre y excepciones (panel PARAMÉTRICOS ORO)**
- Mismos controles que en Zafiro: conceptos sin paramétrico (debe ser 0), cantidad base mayor que Hoja1 (debe ser 0) e importe distinto al de Hoja1.
- **Excepciones autorizadas** (el paramétrico difiere de Hoja1 a propósito; la nota va en la hoja de cada fila): filas de Hoja1 50, 52, 116, 122, 145, 149, 152, 234, 235, 249, 256, 288, 296, 298, 307, 308, 311, 335, 336, 337, 347, 411, 413, 416, 432, 433, 434, 440, 516, 519, 522, 524, 525.
- **Conceptos AGREGADOS que no estaban en Hoja1 de Oro** (se toman con clave y precio de Zafiro; se marcan en **color ámbar** en Hoja1, PRESUPUESTO ORO, las hojas y Rutas): lavavajillas (sanitaria de cimentación y de muros PB); red domiciliaria hidráulica; coladera de jardín sanitaria y coladera de piso (mueble del vertedero); timbre y zumbador en muros; caja de válvulas de gas; repellado y finas de fachada +3.00 (precio alterno para altura 4.20, cantidad 0 en el caso base); boquilla gris en fachada (18.2 m); centro de carga (cableado y tapa); tapas ciegas de TV PB y PA (3 c/u), de cable, de internet aéreo y de paneles solares; escalera marina; limpieza y sellado de columnas del asador (4 × 6.9 m), de ojo de buey (2 pzas), de gualdra (2.4 m) y de columnas de cantera de la cochera (2 × 6.9 m).

## 12. Bitácora

| Fecha | Cambio |
|---|---|
| 2026-11-10 | Análisis inicial del libro (5 hojas, hallazgos 1–8). |
| 2026-11-10 | Sillar fuera del divisor; cantidades escalan con D4; se agregan columnas K–M. |
| 2026-11-10 | Se define el concepto de ruta paramétrica y se crea la hoja Rutas (driver MURO). |
| 2026-11-10 | Driver renombrado a MURO DE CONFINAMIENTO; Rutas con las 30 columnas de Hoja1. Se crea este archivo `.md`. |
| 2026-11-10 | Nueva hoja Paramétrico MURO CAPAS (5 capas, interruptores, interior/fachada); Rutas reconstruida con capa y zona. Libro `_CAPAS.xlsx`. |
| 2026-11-10 | Sellados, limpiezas y entintados asignados a REVESTIMIENTO (grupo SELLADO/LIMPIEZA); se elimina el bloque Por asignar. Libro `_CAPAS_v2.xlsx`. |
| 2026-11-10 | Sellados y limpiezas ligados a su elemento (columna Concepto); lijado y sellado de muro en PINTURA; tomboleado de piso = renivelación de charola; travertino pendiente de m² de piso. Libro `_CAPAS_v3.xlsx`. |
| 2026-11-10 | Se revierte el movimiento de finas/repello de fachada y descuento de pretil (el usuario estaba confundido). Se crean Paramétrico PRETIL y Paramétrico VANO; Rutas con los tres drivers. Libro `_CAPAS_v5.xlsx`. |
| 2026-11-10 | Puertas, cancelería y domos pasan a APARTE; finas de fachada a MURO (solo 62 m² de pretil de las +3.00 pasan a PRETIL). Libro `_CAPAS_v6.xlsx`. |
| 2026-11-10 | Repello fachada +3.00 (173) partido: 62 m² a PRETIL y 11 m² a MURO. Libro `_CAPAS_v7.xlsx`. |
| 2026-11-10 | PRETIL: boquilla confirmada; se agrega lijado y sellado (precio de la fila 370) a la capa de pintura junto con pintura fachada 1ª y 2ª mano. Libro `_CAPAS_v8.xlsx`. |
| 2026-11-10 | MURO > pintura fachada: se agrega lijado y sellado (precio de la fila 370, cantidad de la fila 386). Libro `_CAPAS_v9.xlsx`. |
| 2026-11-10 | Corregidos 92 `#NAME?` de Catálogo Geometría (`=igual` pasa a texto `igual`). `EST-10013` (filas 81 y 85) NO es duplicado: tienen distinto Ingeniería ERP (1020610 / 1020611). Libro `_CAPAS_v11.xlsx`. |
| 2026-11-10 | Driver LOSA: hoja Paramétrico LOSA con LOSA DE PISO (cimentación) y LOSA DE AZOTEA, piezas globales convertidas a m²; entrepiso pendiente. Libro `_CAPAS_v10.xlsx`. |
| 2026-11-10 | Travertino largos libres: piso = 17.52 m² (celda `I58`, editable), muro = 45 − 17.52 = 27.48 m² (revestimiento 199 y limpieza 383). Piso en bloque PISO (filas 56–57). Revestimiento de muro baja ≈ $9,759 (≈ $348.90/m²; total todas las capas ≈ $1,661/m²; cálculo a mano, falta confirmar en Excel). Libro `_CAPAS_v12.xlsx`. Decisiones: pretil sin revestimiento por ahora, castillos siguen en MURO/PRETIL, decimales sin redondeo, chapeo = revestimiento. |
| 2026-11-10 | Driver PISO: hoja Paramétrico PISO (obra gris + revestimiento, base 170.65 m², ≈ $542.17/m²); pórfido exterior y firme de asador informativos; Rutas con 12 partidas de piso + 5 informativas y resumen conectado. Libro `_CAPAS_v13.xlsx`. |
| 2026-11-10 | PISO queda solo interior (157.33 m², ≈ $554.01/m²); nuevas hojas ASADOR (firme + Dover) y PÓRFIDO. LOSA gana el bloque de plafón PB con 3 capas (obra gris, obra blanca, pintura; ≈ $269.05/m² de losa). Rutas con resumen de PISO, PLAFÓN PB, ASADOR y PÓRFIDO. Libro `_CAPAS_v14.xlsx`. |
| 2026-11-10 | La losa de piso (cimentación) pasa de LOSA a PISO como capa de obra negra (PISO ≈ $217,267, ≈ $1,380.96/m²). ASADOR: pérgola, forjado y revestido como partidas FIJAS (≈ $39,992) + piso que escala (≈ $786.37/m²). Libro `_CAPAS_v15.xlsx`. |
| 2026-11-10 | Instalaciones quedan aparte. Nueva hoja Paramétrico COCHERA: pérgola proporcional (29.92 m²), estructura base fija y escalón de columnas (cantera + forrada + 2 zapatas) al crecer 60%. Rutas con escalamiento "Escalón". Libro `_CAPAS_v16.xlsx`. |
| 2026-11-10 | COCHERA: escalón de columnas a +60% y +160% (máx. 2 juegos), chaflán escala como en el asador, sellado de columna de cantera (396) a la mitad entre asador y cochera. ASADOR: se agrega el sellado de columna (396, mitad). Libro `_CAPAS_v17.xlsx`. |
| 2026-11-10 | Corrección: el lijado y sellado del asador es la fila 396 (ya dividida con la cochera), no la 370; se quita la partida y la celda de m². Libro `_CAPAS_v18.xlsx`. |
| 2026-11-10 | COCHERA: cada columna de cantera adicional suma su limpieza y sellado (396, 6.9 m por juego; juego ≈ $9,057; +60% ≈ $102,268, +160% ≈ $163,921). ASADOR: nota de que la 381 (3.00 m) es del asador y su longitud se hará editable después. Libro `_CAPAS_v19.xlsx`. |
| 2026-11-10 | Confirmado «hasta +160%» de la cochera. Elementos FIJOS: ojo de buey, durmiente, gualdra (MURO) y vertedero (PISO). Revisión de limpiezas y sellados (hallazgo: sellado de marco interior 14.4 m vs 21 m). Nuevo driver SILLAR (muro 30 m² + limpieza y sellado por ambas caras, ≈ $21,985). Gualdra (80) y durmiente (185) agregados como fijos. Libro `_CAPAS_v20.xlsx`. |
| 2026-11-10 | Driver BARDA PERIMETRAL: hoja Paramétrico BARDA (muro sillar, castillo y 2 cadenas aparentes, 35.88 m², ≈ $26,289 / $732.70 por m²). Las 4 rutas informativas de Rutas pasan a la hoja nueva y se agrega el resumen. Libro `_CAPAS_v21.xlsx`. |
| 2026-11-10 | BARDA: el driver pasa a metros lineales (15 ml base); se agregan tramos de 7.00 ml con 1 zapata y 1 castillo adicional (≈ $1,513 por tramo). Corrección: el importe base de las partidas por escalón (cochera y barda) es 0. Libro `_CAPAS_v22.xlsx`. |
| 2026-11-10 | BARDA: se quitan la zapata y el castillo adicional por tramo; el módulo de 7.00 ml queda solo como referencia; los castillos se cuentan a cada 3.95 ml a ejes (ROUNDUP(ml/3.95)+1, 3.12 m c/u); la barda no lleva limpieza y sellado. Libro `_CAPAS_v23.xlsx`. |
| 2026-11-10 | BARDA: castillo de 1.95 m de altura, 8 piezas en la modulación base de 15 ml (8 × 1.95 = 15.6 m, cuadra con Zafiro); se quita el cálculo por separación de 3.95 ml (queda como referencia). Libro `_CAPAS_v24.xlsx`. |
| 2026-11-10 | LOSA DE ENTREPISO diferida: se define con un modelo de dos plantas como Oro. Se anotan en la sección 10C los datos de Oro (filas 2773–2782 y 2902–2906) y la inconsistencia de áreas. Libro `_CAPAS_v25.xlsx`. |
| 2026-11-10 | CUBIERTA queda pendiente (ml de vanity). BARDA: el castillo de 1.95 m suma 1 pieza por cada 3 ml adicionales (+1 cada 3 ml). VANO: sellado de marco de cantera interior en 21 m (antes 14.4), VANO ≈ $38,620 / $281.90 por m. Libro `_CAPAS_v26.xlsx`. |
| 2026-11-10 | Instalaciones: tres hojas nuevas por salidas — HIDROSANITARIAS ($45,134), GAS ($8,311) y ELÉCTRICAS ($68,101), con grupos que escalan por salidas y grupos fijos; cobertura total de las claves ISN/IHD/IGAS/IEC de Zafiro. Rutas con 3 filas de resumen y todas las partidas. Libro `_CAPAS_v27.xlsx` (incluye los ajustes de v25 y v26). |
| 2026-11-10 | Instalaciones: las redes principales (hidráulicas, sanitaria y eléctricas) escalan por m² de losa, enlazadas a la losa de cimentación de PISO. Accesorios por elemento (eléctricos y muebles hidrosanitarios): queda en manos del usuario. Libro `_CAPAS_v28.xlsx`. |
| 2026-11-10 | Nuevo driver MUEBLES Y EQUIPOS ($76,150: muebles hidrosanitarios $42,939 + equipos $33,211), con piezas enlazadas a las salidas de HIDROSANITARIAS y GAS; fijos: vertedero, presurizadora, coladera de jardín, medio baño, asador, tanque de gas y cisterna ($27,258). Libro `_CAPAS_v29.xlsx`. |
| 2026-11-10 | Coladera de jardín: 1 por cada 22.5 m² de jardín con sello (HIDROSANITARIAS y su mueble). Sets de baño: 1 por baño completo = MIN(WC, regaderas); medio baño = WC sin regadera = MAX(0, WC − regaderas). Hidrosanitarias fijos $3,634 y muebles fijos $25,949. Libro `_CAPAS_v30.xlsx`. |
| 2026-11-10 | ELÉCTRICAS: los grupos se reorganizan por concepto de iluminación / accesorios (columna «Tipo» y resumen por tipo: iluminación $26,758, accesorios $30,037, infraestructura $10,068, asador y exterior $1,238). Libro `_CAPAS_v31.xlsx`. |
| 2026-11-10 | ELÉCTRICAS: los cableados corresponden a los accesorios (tipo por partida; iluminación $20,768, accesorios $38,129 con todo el cableado, infraestructura $8,726, asador y exterior $479). Libro `_CAPAS_v32.xlsx`. |
| 2026-11-10 | ELÉCTRICAS: el concepto de accesorio guía la columna A; capas = etapas de la salida (cimentación, muros, losa, cableado, accesorios); matriz de $/salida por etapa y tipo de accesorio (apagadores sencillo/doble/triple/escalera, contactos dúplex/fuerza/USB/intemperie, TV, centro de luz, arbotante, spot, minisplit). Los contactos y apagadores del asador pasan a sus tipos. Libro `_CAPAS_v34.xlsx`. |
| 2026-11-10 | Los muebles hidrosanitarios (WC, regadera, lavamanos, tarja, calentador, etc.; $42,939) pasan a HIDROSANITARIAS como capa MUEBLES; la hoja suma $88,072 y muestra cuánto sale una salida por etapa (sanitaria, hidráulica, mueble). La hoja MUEBLES Y EQUIPOS queda como EQUIPOS ($33,211). Libro `_CAPAS_v35.xlsx`. |
| 2026-11-10 | Estufa y campana se separan (EQUIPOS). Aclarado: «fijo» no es «no editable» (cantidades de partidas y factor por grupo editables). Nuevas hojas HERRERÍA ($15,390), CARPINTERÍA ($196,671) y CANCELERÍA ($85,533), fijas por ahora y con piezas editables. Libro `_CAPAS_v36.xlsx`. |
| 2026-11-10 | *(reconstruido)* Nuevas hojas OBRA EXTERIOR (registros, murete, plantas) , JARDÍN (sello + pasto, ligado a HIDROSANITARIAS) y CUBIERTA (mármol y poyos, dos drivers en ml). Libro `_CAPAS_v37.xlsx`. |
| 2026-11-10 | *(reconstruido)* Nueva hoja CISTERNA (volumen en litros y piezas, hasta 6 cisternas); la cisterna prefabricada sale de EQUIPOS. Libro `_CAPAS_v38.xlsx`. |
| 2026-11-10 | *(reconstruido)* v39: las plantas pasan de JARDÍN a OBRA EXTERIOR (JARDÍN queda en sello y pasto). v40: panel PARAMÉTRICOS ZAFIRO y PRESUPUESTO ZAFIRO con control de cobertura y cuadre. v41: se elimina `Claves sin Zafiro` y se quita la lista APARTE de VANO. v42: sellado de marco interior regresa a 21 m (excepción autorizada). v43: solo ajustes en Rutas. Libros `_CAPAS_v39` a `_v43.xlsx`. |
| 2026-11-10 | *(reconstruido)* Nueva hoja MARCOS EXTERIORES (marcos de cantera de fachada, sellado y boquillas). Libro `_CAPAS_v44.xlsx`, **última de Zafiro**. |
| 2026-11-10 | *(reconstruido)* Nace la línea ORO 4.01 a partir de Zafiro v44: `CATALOGO_PARAMETRICO_ORO_v1.xlsx` con MURO, LOSA ENTREPISO, ESCALERA, OBRA COMPLEMENTARIA, panel PARAMÉTRICOS ORO y PRESUPUESTO ORO. Entrepiso, antes diferido (10C), ya se parametriza. |
| 2026-11-10 | *(reconstruido)* ORO v14: MURO se parte en PB / PA / FACHADA, PISO en PB / PA y se agrega MARCOS EXTERIORES. ORO v15–v18: afinaciones, excepciones autorizadas y conceptos agregados (ámbar). Libro vigente `ORO_v18.xlsx`. |
| 2026-11-11 | **Zafiro v45 / Oro v19.** (1) Referencias a Hoja1 por **llave** (`Clave|Ingeniería ERP|60 caracteres de la descripción|ocurrencia`, columnas AE y AF de Hoja1) en lugar de número de fila: 1,977 referencias directas y 655 columnas «Fila Hoja1» en Zafiro (2,488 y 984 en Oro) pasan a `INDEX/MATCH`; PRESUPUESTO usa `ROW()`. Importes idénticos a v44/v18 (0 diferencias celda por celda); con Hoja1 barajada el total y los drivers no cambian, y en v44 sí se rompían. (2) Panel con parámetro, unidad real, cohorte, estatus, tasa del otro prototipo, CV (n=2) y confianza. (3) Unidades reales en herrería, carpintería y cancelería; Oro: unidad, base y $/unidad en hidrosanitarias, gas, eléctricas, equipos y carpintería; Zafiro: panel de MARCOS EXTERIORES completo. (4) La diferencia contra Hoja1 queda rotulada como **faltante del catálogo original**, no error de diseño (decisión del usuario). Hoja nueva `LEEME`. |
| 2026-11-11 | **Dispersión en los 7 prototipos.** `DISPERSION_7_PROTOTIPOS.xlsx` y `medir_dispersion.py`: 14 drivers medidos con una misma regla sobre Hoja1 (todos los prototipos están ahí). Reproduce D-312 (cimentación, CV 6.0 % poblacional) y el libro curado en losa de cimentación, barda, pórfido y cisterna. Utilizables: cimentación, muro (estructura), piso, pórfido, barda, cochera, cubierta, asador. Sin medir: pretil, vano, jardín, fachada, herrería, y la tasa por salida de las instalaciones. |
| 2026-11-11 | **Aparatos y salidas por puntos en los 7 prototipos.** `TABLA_APARATOS_SALIDAS.xlsx`, `tabla_aparatos_salidas.py` y `curado_aparatos.json`: conteo de puntos por grupo (ancla = concepto con una unidad por punto), reproduce los conteos de Zafiro y difiere en 6 grupos de Oro (ajustes a mano). Costo por salida: hidrosanitarias $1,904 (CV 7.5 %), gas $653 (2.5 %), eléctricas $455 (3.9 %), equipos $2,204 (4.4 %). Con puntos las instalaciones son más estables que por m². Las redes por m² de losa y los fijos quedan fuera. |
| 2026-11-11 | **Claves sin grupo asignadas.** Las 19 claves de SIN_GRUPO pasan a su grupo (`asignaciones_sin_grupo.json`, hoja ASIGNADAS): 7 a redes, 1 a fijos (cisterna prefabricada), 2 al asador fijo y 9 variantes de salida o cableado a su aparato. SIN_GRUPO queda vacía y cada familia cuadra con su total. |
| 2026-11-11 | **Pretil en los 7 prototipos.** `PRETIL_7_PROTOTIPOS.xlsx` y `medir_pretil.py`: la regla de Zafiro (franja +3.00 con tope en los m² del pretil) reproduce su libro al centavo ($75,537.12) y se aplica a Rubí, Zafiro Plus, Jade, Diamante y Oro. Total $1,136/m², CV 6 %, utilizable. Oro v19 carga 300 m² de fachada +3.00 en su pretil; con la regla le tocan 45 y los 255 restantes van a MURO FACHADA (pendiente decidir). |
| 2026-11-11 | **Oro v20.** Corrección del pretil con la regla de Zafiro: la franja de fachada +3.00 del pretil pasa de 300 a 45 m² (celdas I22 e I27); los 255 m² restantes de repellado y de finas se cobran en MURO FACHADA (filas 31 y 32 nuevas); la boquilla de 18.2 m (fila 319 de Hoja1) pasa de PRETIL a MARCOS EXTERIORES. PRETIL baja a $47,154 ($1,048/m²). Total y cuadre contra Hoja1 sin cambio. Pendiente: la fila 320 de Hoja1 duplica la 319 en MARCOS EXTERIORES. |
| 2026-11-11 | **Oro v21.** Revisión de las boquillas de los marcos: la gruesa (filas 319 y 320, 18.2 m, $50.81/m) y la fina (fila 321, 18.2 m, $9.34/m) no son lo mismo y las dos están; la 319 y la 320 son la misma gruesa (la 320 se agregó con la clave de Zafiro, ACA-01052), así que sobra una, no falta. MARCOS EXTERIORES cobra la 320 y la fina; la 319 queda en 0 como excepción autorizada. Corrige v20, que había dejado dos gruesas. Total $2,634,340.58, diferencia contra Hoja1 +$19,250.97. |
