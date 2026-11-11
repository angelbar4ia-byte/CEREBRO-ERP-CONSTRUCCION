# Estabilidad de los paramétricos y de sus rutas

Libros: `CATALOGO_PARAMETRICO_con_MURO_ZAFIRO_CAPAS_v46.xlsx` y `CATALOGO_PARAMETRICO_ORO_v22.xlsx`. Parten de v45 y v21 y **no cambian ningún importe** (comprobado celda por celda tras recalcular, salvo la columna de ruta de Hoja1).

## Qué se auditó

| Revisión | Resultado antes |
|---|---|
| Cada fila de Rutas apunta a su fila de la hoja del driver, y esa fila a su concepto de Hoja1 | **Bien**: 0 incongruencias en Zafiro (362 rutas) y en Oro (494) |
| Partidas de las hojas de driver sin fila en Rutas | **Bien**: ninguna |
| Texto de la ruta (`DRIVER > CAPA > ZONA > GRUPO > CONCEPTO`) | **Mal**: 27 rutas repetidas en Zafiro y 25 en Oro (por ejemplo, 16 castillos con el mismo texto). No servía como identificador |
| Rangos de Rutas en el panel y en PRESUPUESTO | **Mal**: tope escrito a mano (`$36:$700`, `$37:$828`). Una ruta nueva pasada el tope no entraba en los totales sin avisar |
| Llave de Hoja1 | **Mal**: se confundía entre prototipos. Un mismo código de ingeniería aparece en varios capítulos (por ejemplo, «Lavado de mármol travertino» en las filas 383, 1285 y 1672), y al reordenar Hoja1 el paramétrico de Zafiro tomaba la cantidad de otro prototipo. Lo encontró la prueba de Hoja1 barajada |
| Columna Q de Hoja1 (Ruta paramétrica) | **Floja**: era una etiqueta inferida por regla, no el driver que de verdad cobra el concepto |
| Constantes escritas dentro de fórmulas | **Visibles ahora**: 38 en Zafiro y 114 en Oro (repartos como `*9/21`, conteos como `=3`, mármol 11.2 m²). No se tocaron |

## Qué se hizo

1. **Llave con capítulo.** `Hoja1!AE` = capítulo | clave | ingeniería | descripción (60) | origen | nivel | desambiguador; `AF` agrega la ocurrencia. Hoja1 trae dos columnas nuevas: `AG` (capítulo auxiliar) y `AH` (desambiguador). Se reescribieron 2,632 llaves en Zafiro y 3,469 en Oro.
2. **Desambiguador.** Solo donde hay filas idénticas en Hoja1 (2 en Oro: la limpieza de columnas de cantera del asador y de la cochera, 27.6 y 13.8 m), `AH` dice qué driver las cobra. Así no dependen del orden.
3. **RUTA ID** (Rutas, columna `AS`): ruta + clave + código + ocurrencia en Hoja1. Única en las 362 y 494 rutas. No depende de la posición.
4. **Rangos sin tope** en el panel y en PRESUPUESTO (992 fórmulas en Zafiro, 1,334 en Oro).
5. **Cuatro controles de estabilidad en el panel**, todos deben dar 0: llaves de Rutas que no se encuentran en Hoja1, IDs repetidos, importe de Rutas que ningún driver del panel recoge, y rutas pasada la fila 2,000.
6. **Hoja1, columna Q**: ahora es el driver (o los drivers, unidos con +) que de verdad cobra cada concepto: 315 conceptos en Zafiro y 425 en Oro.
7. **Hoja `CONSTANTES EN FÓRMULAS`** y **hoja `LEEME ESTABILIDAD`** (cómo agregar una partida y qué hacer si se reordena Hoja1).

## Pruebas

`probar_parametricos.py LIBRO.xlsx ZAFIRO|ORO` recalcula el libro y verifica: sin errores de fórmula, importes por driver y controles iguales a `estado_esperado_ZAFIRO.json` / `estado_esperado_ORO.json`, controles de estabilidad en 0 e IDs únicos. Con `--completo` agrega:
- **Hoja1 barajada dentro de cada capítulo** (con `AH` viajando con su fila): los importes de todos los drivers no cambian. Pasa en Zafiro (7 bloques, 23 de 23) y en Oro (29 de 29).
- **Drivers al doble** (10 en Zafiro, 17 en Oro): sin errores, el total sube y los controles siguen en 0.

`estabilizar_parametricos.py` regenera v46 y v22 desde v45 y v21.

## Reglas para no romperlos

- Se puede ordenar o reemplazar Hoja1 **dentro de cada capítulo**. Las columnas `A:AD` y `AH` viajan juntas.
- Si cambia la clave, la ingeniería, el origen, el nivel o los primeros 60 caracteres de la descripción de un concepto de Hoja1, hay que actualizar su llave en la hoja del driver.
- Para agregar una partida: copiar una fila completa de su hoja de driver, cambiar la llave y el concepto, agregar su fila en Rutas (el ID se calcula solo) y revisar que los controles den 0.
- Si dos filas de Hoja1 llegan a ser idénticas, ponerles un valor distinto en `AH`.

## Límites

- Mover filas **entre capítulos** de Hoja1 sí cambia las llaves (el capítulo sale de la posición).
- PRESUPUESTO sigue siendo un espejo fila por fila de Hoja1: si se inserta un concepto en el capítulo, hay que ampliar el espejo.
- Las referencias del panel de Rutas a celdas de las hojas de driver siguen siendo por coordenada. Excel las ajusta solo cuando se insertan filas desde la interfaz; un script no.
- Las constantes escritas en fórmulas siguen ahí; ahora se ven, no se movieron a celdas editables.
- Se probó recalculando con LibreOffice, no con Excel.
