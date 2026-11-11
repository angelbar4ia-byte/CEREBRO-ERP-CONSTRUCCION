# Análisis a fondo de los libros paramétricos

Método: se recalcularon ambos libros con LibreOffice (los originales no guardan valores) y se leyeron fórmulas y resultados. No se usó Excel, así que conviene confirmar una vez allí. Ningún error `#REF!`, `#NAME?` ni `#DIV/0!` en ninguna hoja de los dos libros.

## 1. Anatomía

| | Zafiro v44 | Oro v18 |
|---|---|---|
| Hojas | 29 | 32 |
| Fórmulas | 25,455 | 34,040 |
| Hoja1 (catálogo base) | 3,234 filas, 30 columnas, solo valores | 556 filas |
| Conceptos | 315 en el presupuesto | 425 |
| Drivers (hojas) | 22 | 28 |
| Partidas "Sí" | 356 | 492 |

Flujo de datos: `Hoja1` (valores) → hoja de cada driver (capas, interruptores, cantidades) → `Rutas` (unión de todas las partidas, ~13 mil fórmulas, lee Hoja1 con `INDEX`) → `PRESUPUESTO` (reconstruye el presupuesto con cantidades del proyecto) → `PARAMÉTRICOS` (panel con `SUMIFS` y `COUNTIFS` sobre Rutas, más los controles de cuadre).

Convención de color: azul = encabezado, verde = resultado, amarillo = entrada editable, gris = informativo. En Oro, ámbar = concepto agregado que no está en Hoja1.

## 2. Resultados recalculados

### Zafiro 1.0 (172 m²)

| Controles | Valor |
|---|---|
| Presupuesto Hoja1 | $1,842,426.01 |
| Generado por los paramétricos | $1,842,873.83 |
| Diferencia | **+$447.82** |
| Conceptos sin paramétrico | **0** |
| Cantidad mayor que Hoja1 | 1 |
| Importe distinto de Hoja1 | 1 |

La diferencia no es error de diseño: es **faltante del catálogo original** (decisión del usuario, 2026-11-11). Se explica entera por una excepción autorizada: ACA-08030, sellado de marco de cantera interior, 21 m contra 14.4 m en Hoja1 (6.6 m × $67.85 = $447.81). **El modelo cuadra.**

| Driver | Base | Importe | $/unidad |
|---|---|---|---|
| Muro (5 capas) | 279 m² | 453,305 | 1,624.75 |
| Losa de azotea + plafón | 165 m² | 306,247 | 1,856.05 |
| Piso (con losa de cimentación) | 157.33 m² | 217,267 | 1,380.96 |
| Carpintería | fija | 196,671 | — |
| Hidrosanitarias | 35 salidas | 88,072 | 2,516 |
| Cancelería | fija | 85,533 | — |
| Pretil | 62 m² | 75,537 | 1,218.34 |
| Eléctricas | 121 salidas | 68,101 | 563 |
| Cochera | 29.92 m² | 61,653 | 2,060.60 |
| Asador | 13.32 m² | 51,790 | 3,888 |

Por subcapítulo: planta baja 32.5 %, carpintería 10.7 %, cimentación 9.7 %, azotea 9.7 %, acabados 8.8 %, muebles e iluminación 5.7 %, pintura 5.6 %.

Partidas más caras: losa maciza de azotea $130,198; losa de cimentación $130,105; muro de 14 cm $107,973; cocina $65,060; losa nervada $59,476.

### Oro 4.01 (300 m²)

| Controles | Valor |
|---|---|
| Presupuesto Hoja1 | $2,615,089.61 |
| Generado por los paramétricos | $2,635,265.32 |
| Diferencia | **+$20,175.71 (0.77 %)** |
| Conceptos sin paramétrico | **0** |
| Cantidad mayor que Hoja1 | **14** |
| Importe distinto de Hoja1 | **25** |

Los 20 mil se reparten por subcapítulo: pintura +$8,498; herrería +$3,850; planta baja +$3,694; muebles e iluminación +$2,392; acabados +$1,904; cimentación +$1,155; planta alta −$1,317. Corresponden a las excepciones autorizadas (calibraciones de salidas eléctricas, hidráulicas y de plafón) y a los conceptos agregados con clave y precio de Zafiro.

Aquí el control no da 0, pero tampoco es error: son conceptos o cantidades que el catálogo original de Oro no traía (33 filas de excepción documentadas). Desde v19 el panel lo rotula así.

Dos partidas de Oro llevan la misma clave `EST-02010` (muro de 14 cm, $110,682 y $95,365): son PB y PA, no un duplicado.

## 3. Prueba de sensibilidad (Zafiro)

Se duplicó muro (558 m²), losa (330), piso (314.66), pretil (124), barda (30 ml) y WC (de 4 a 8 salidas).

| Driver | Resultado |
|---|---|
| Muro | ×1.99 (parte fija: ojo de buey, durmiente y gualdra) |
| Pretil, piso, losa | ×2.00 exacto |
| Barda | ×1.93 (castillos por pieza: +1 cada 3 ml, no proporcional) |
| Hidrosanitarias | ×1.30 (solo escala el WC y lo ligado a él) |
| Eléctricas | ×1.02 (solo las redes por m² de losa) |
| Equipos | ×1.15 (enlazados a salidas de WC) |
| Total | ×1.60 (de $1.84 M a $2.94 M) |

El motor responde como dice la bitácora. Sin cambios de driver no hay errores. El control "cantidad mayor que Hoja1" pasa de 1 a 93, lo cual es esperado: marca toda partida que crece.

## 4. Hallazgos

1. **Los $/unidad del panel no coinciden con el .md.** El muro da $1,624.75/m² (el .md decía ≈ $1,642 y ≈ $1,696 en etapas previas) y la losa $1,856/m² con plafón (el .md daba $1,587 sin plafón). Es normal por los cambios posteriores, pero el .md no se actualizó.
2. **Paneles heterogéneos.** En Oro, 9 drivers de instalaciones y obra no tienen unidad ni valor base ("global/salidas"), por lo que no tienen $/unidad. No hay una métrica comparable entre drivers.
3. **Equipos:** Zafiro $24,997 (el .md decía $33,211; la diferencia de $8,214 es la cisterna, que pasó a CISTERNA). Consistente.
4. **Hojas sobrantes en Zafiro:** `Leyenda Q-Z` y `Catálogo Geometría` son estáticas, sin fórmulas. `Hoja1` no tiene fórmulas: es la única fuente de precios y cantidades base. Si cambia una fila, se re-liga todo (la v17 de Oro ya tuvo que reordenar filas).
5. **Constantes dentro de las hojas** (altura de castillo 1.95, 8 piezas, umbral de 3 ml, 22.5 m² por coladera): están en celdas editables, no enterradas en fórmulas. Bien.
6. **Riesgo estructural:** `Rutas` y `PRESUPUESTO` leen Hoja1 por número de fila con `INDEX`. Insertar o borrar filas en Hoja1 rompe el cuadre en silencio. El control "importe distinto de Hoja1" es la red de seguridad.
7. **Pendientes de fondo siguen abiertos:** los drivers de carpintería, cancelería y herrería son "fijos"; no hay relación con vanos ni con ml de vanity; las cantidades escalan con decimales (sin `ROUNDUP`).

## 5. Cómo reproducir

Recalcular con `soffice --headless --convert-to xlsx` y leer con `openpyxl` en modo `data_only`. Los resultados recalculados no se guardan en el repo para no duplicar los 800 KB; se regeneran en segundos.
