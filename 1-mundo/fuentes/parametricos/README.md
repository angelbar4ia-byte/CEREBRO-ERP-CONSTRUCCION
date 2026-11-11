# Catálogo paramétrico (Zafiro y Oro)

Fuente compartida por el usuario el 2026-11-11, guardada tal cual. Huellas en `../MANIFIESTO.csv`.

| Archivo | Qué es |
|---|---|
| `CATALOGO_PARAMETRICO.md` | Bitácora y especificación (archivo vivo). Secciones 1–13 y bitácora. |
| `CATALOGO_PARAMETRICO_con_MURO_ZAFIRO_CAPAS_v44.xlsx` | Original recibido de **Zafiro 1.0** (172 m², una planta). 29 hojas, ~25 mil fórmulas. |
| `CATALOGO_PARAMETRICO_con_MURO_ZAFIRO_CAPAS_v45.xlsx` | **Vigente.** v44 con llaves en lugar de filas, cohorte, dispersión y unidades reales. Hoja `LEEME v45`. |
| `CATALOGO_PARAMETRICO_ORO_v19.xlsx` | Igual para Oro. Hoja `LEEME v19`. |
| `CATALOGO_PARAMETRICO_ORO_v21.xlsx` | **Vigente.** v20 con la boquilla gruesa de los marcos cobrada una sola vez (fila 319 en 0, fila 320 activa). Total $2,634,340.58. Hoja `LEEME v21`. |
| `CATALOGO_PARAMETRICO_ORO_v20.xlsx` | Reemplazada por v21 (dejaba dos boquillas gruesas en los marcos). v19 con el pretil corregido (franja +3.00 con tope; 255 m² pasan a MURO FACHADA; boquilla a MARCOS EXTERIORES). Mismos totales. Hoja `LEEME v20`. |
| `DISPERSION_7_PROTOTIPOS.xlsx` | Tasas de 14 drivers medidas con una misma regla en los 7 prototipos, con CV y confianza. Se regenera con `medir_dispersion.py`. |
| `TABLA_APARATOS_SALIDAS.xlsx` | Aparatos y salidas **por puntos** de los 7 prototipos, costo por salida y su CV. Se regenera con `tabla_aparatos_salidas.py` (usa `curado_aparatos.json`). |
| `PRETIL_7_PROTOTIPOS.xlsx` | Pretil de los 7 prototipos con la regla resuelta en Zafiro: partidas, ratios por m², tasas y CV. Se regenera con `medir_pretil.py`. |
| `CATALOGO_PARAMETRICO_ORO_v18.xlsx` | Original recibido de **Oro 4.01** (300 m², dos plantas). 32 hojas, ~34 mil fórmulas. Nació de la v44 de Zafiro. |

## Qué es un paramétrico

Un presupuesto de un modelo real (Zafiro 1.0 = $1,842,426.01) se vuelve escalable. Cada partida se asocia a un **driver**, la magnitud que captura el usuario (m² de muro, m² de losa, ml de barda, número de salidas…).

```
RUTA = DRIVER > GRUPO > PARTIDA        (+ regla de escalamiento)
cantidad del proyecto = (cantidad base / valor base del driver) × valor del driver
```

Escalamientos: **proporcional**, **fijo** (no escala, pero la cantidad sí es editable), **por piezas / por salidas**, **por escalón** (cochera: +60 % y +160 %) y **por m² de losa** (redes principales).

## Estructura de los libros

- **Panel** (`PARAMÉTRICOS ZAFIRO` / `ORO`): una fila por driver con valor base, valor del proyecto, importe y $/unidad. Incluye controles de cuadre (sin paramétrico, cantidad mayor que Hoja1, importe distinto) que deben dar 0.
- **PRESUPUESTO** generado: copia de `Hoja1` cuyas cantidades salen de los paramétricos.
- **Una hoja por driver**, con capas e interruptores Sí/No: obra negra, gris, blanca, revestimiento y pintura.
  - Zafiro: MURO CONFINAMIENTO, MURO CAPAS, SILLAR, BARDA, PRETIL, VANO, MARCOS EXTERIORES, LOSA, PISO, ASADOR, PÓRFIDO, COCHERA, HIDROSANITARIAS, GAS, ELÉCTRICAS, EQUIPOS, HERRERÍA, CARPINTERÍA, CANCELERÍA, OBRA EXTERIOR, JARDÍN, CUBIERTA, CISTERNA.
  - Oro: lo anterior, con MURO partido en PB / PA / FACHADA, PISO en PB / PA, y además LOSA ENTREPISO, ESCALERA y OBRA COMPLEMENTARIA.
- **Rutas**: detalle de cada partida con las 30 columnas de `Hoja1`.
- **Hoja1**: catálogo base (Zafiro: 3,234 filas, 2,452 conceptos; Oro: 556).

## Importes de referencia de Zafiro (del .md)

Son cálculos hechos en Python, no valores de Excel.

| Driver | Importe base | $/unidad |
|---|---|---|
| Muro, todas las capas | — | ≈ 1,642–1,696 / m² |
| Pretil | 77,688 | ≈ 1,253 / m² |
| Vano (interior) | 38,620 | ≈ 282 / m |
| Piso (con losa de cimentación) | 217,267 | ≈ 1,381 / m² |
| Losa de azotea | 261,854 | ≈ 1,587 / m² |
| Barda | 26,289 | ≈ 1,753 / ml |
| Hidrosanitarias | 88,072 | — |
| Eléctricas | 68,101 | — |
| Carpintería | 196,671 | fijo |

Análisis a fondo con los libros recalculados: ver `ANALISIS-EXCEL.md`.

## Advertencias

- **Los libros no guardan valores calculados**, solo fórmulas. Los importes salen al abrirlos en Excel, y el .md reconoce que **nunca se verificó el cuadre fuera de Python**. Abre el libro y revisa que los controles del panel den 0.
- El .md no se actualizó entre la v36 y la v44 de Zafiro, ni durante la línea Oro. Las secciones 11F, 11G y 13 y las últimas filas de la bitácora **se reconstruyeron comparando los libros**. El razonamiento de las decisiones que no quedó en notas del libro se perdió.
- Pendientes abiertos: cubiertas ligadas a los ml de vanity, relacionar puertas y cancelería con los vanos, accesorios por elemento (eléctricos y muebles), cantidades con decimales sin `ROUNDUP`, y columnas AREA y DESARROLLO vacías.
- Las versiones anteriores (Zafiro v1–v43, Oro v1–v17) no están en el repo; v44 y v18 son los originales recibidos y v45 y v19 las vigentes.
- La diferencia del paramétrico contra Hoja1 (+$447.82 en Zafiro, +$20,175.71 en Oro) **no es error de diseño**: es el faltante del catálogo original. Los libros nuevos lo rotulan así.
