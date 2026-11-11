# Catálogo paramétrico (Zafiro y Oro)

Fuente compartida por el usuario el 2026-11-11, guardada tal cual. Huellas en `../MANIFIESTO.csv`.

| Archivo | Qué es |
|---|---|
| `CATALOGO_PARAMETRICO.md` | Bitácora y especificación (archivo vivo). Secciones 1–13 y bitácora. |
| `CATALOGO_PARAMETRICO_con_MURO_ZAFIRO_CAPAS_v44.xlsx` | Libro vigente de **Zafiro 1.0** (172 m², una planta). 29 hojas, ~25 mil fórmulas. |
| `CATALOGO_PARAMETRICO_ORO_v18.xlsx` | Libro vigente de **Oro 4.01** (300 m², dos plantas). 32 hojas, ~34 mil fórmulas. Nació de la v44 de Zafiro. |

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

## Advertencias

- **Los libros no guardan valores calculados**, solo fórmulas. Los importes salen al abrirlos en Excel, y el .md reconoce que **nunca se verificó el cuadre fuera de Python**. Abre el libro y revisa que los controles del panel den 0.
- El .md no se actualizó entre la v36 y la v44 de Zafiro, ni durante la línea Oro. Las secciones 11F, 11G y 13 y las últimas filas de la bitácora **se reconstruyeron comparando los libros**. El razonamiento de las decisiones que no quedó en notas del libro se perdió.
- Pendientes abiertos: cubiertas ligadas a los ml de vanity, relacionar puertas y cancelería con los vanos, accesorios por elemento (eléctricos y muebles), cantidades con decimales sin `ROUNDUP`, y columnas AREA y DESARROLLO vacías.
- Las versiones anteriores (Zafiro v1–v43, Oro v1–v17) no están en el repo; la v44 y la v18 son las vigentes.
