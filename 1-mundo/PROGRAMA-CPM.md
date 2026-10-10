# PROGRAMA-CPM

```
órgano:     cerebelo — la secuencia y el tiempo
capa:       I — Mundo
pregunta:   ¿cómo se calcula el programa y qué cifras lo prueban?
tiempo:     es así
corte:      2026-10-10
verificado: 168 pruebas · los siete programas reales (832 vínculos) reproducen las cifras publicadas
```

> **Este archivo es el mapa y la prueba del programa y del CPM.** Las reglas siguen donde ya
> vivían (`MODELO.md` §5c, `CONOCIMIENTO.md` §11.14); aquí vive lo que **solo existía en libros de
> Excel y en el código**: los siete programas completos, la red con sus identificadores, las
> listas del planeador, el motor que calcula fechas y ruta crítica, el cargador que lee un programa,
> la reprogramación, su persistencia y la pantalla del Gantt, y las cifras con que se comprueba. Desde D-461 nada de eso depende de un libro: `backend/core/motor_cpm.py` y
> `1-mundo/programas/` son la fuente, y `cd backend && python3 -m unittest discover` la prueba.

---

# 1. Dónde vive cada cosa

| Tema | Dónde |
|---|---|
| Las entidades (`ACTIVIDAD`, `PRECEDENCIA`, `CALENDARIO_OBRA`, `TRAMO`, los dos cuantificadores, `FRENTE_TOPE_CUADRILLA`, `CIERRE_FRENTE`, `CORTE_RETRASO`) | `MODELO.md` §5c |
| Las cuatro fórmulas de holgura, el bloque como predecesora, el desfase en horas ÷ 8 | `MODELO.md` §5c (D-442, D-443, D-445) |
| Duración teórica, `paso_dias`, `sentido_redondeo` | `MODELO.md` §5c (D-446) |
| Plazo en días hábiles o en semanas de calendario, feriados sugeridos | `MODELO.md` §5c (D-447) |
| Las alertas del programa (`vinculo_incumplido`, `obra_atrasada`, `subfrente_atrasado`, `subfrente_detenido`) | `MODELO.md` §5a (D-456 a D-459) |
| Recursos por fecha, la salida del CPM | `MODELO.md` §5f (B-41) |
| Las diez decisiones de política del CPM (precedencia en dos capas, reprogramar sin tocar lo registrado, qué aviso merece un cambio de ruta crítica…) | `PROPUESTA-CUATRO-MODULOS.md` (P-1 a P-10), D-90, D-99 a D-102, D-104, D-259 |
| Cómo se armó cada uno de los siete programas, paso a paso | `CONOCIMIENTO.md` §11.14 (D-389 a D-437) |
| La herencia de las duraciones, la red heredada, los vínculos que no se cumplen, los `SF` | `CONOCIMIENTO.md` §11.14 (D-424 a D-445) |
| El retraso por obra, por contratista y por residente | `CONOCIMIENTO.md` §11.14 (D-456 a D-459) |
| **Los datos de los siete programas, el catálogo de la red, las rutas, las listas del planeador** | **§2 a §7 de este archivo y `1-mundo/programas/`** |
| **El motor y su contrato** | **§4 y `backend/core/motor_cpm.py`** |
| **El cargador del programa, la cadena de relevos y el Gantt como dato** | **§4.5 y `backend/core/programa.py`** |
| **Editar y reprogramar** | **§4.6 y `backend/core/programa.py`** |
| **Guardar lo que se edita** | **§4.7, `backend/core/servicio_programa.py` y `database/migraciones/`** |
| **La pantalla del Gantt y sus reglas** | **§8 y `frontend/gantt/`** |

---

# 2. Los datos que ya viven en el repositorio

Trece archivos CSV (UTF-8, coma, una fila de encabezado) en `1-mundo/programas/`. Pasan al repositorio
lo que estaba en los libros de Excel de los siete prototipos y de las revisiones D-425 a D-445. **No
se regeneran desde Excel**: si cambia un programa, se cambia aquí, con una decisión nueva.

| Archivo | Qué es | Filas |
|---|---|---:|
| `PROGRAMAS-PROTOTIPOS.csv` | Los siete programas completos, fila por fila, con sus fechas, vínculos y regla de armado | 3,231 |
| `CATALOGO-DE-LA-RED.csv` | Cada vínculo de la red con su identificador: `V01`–`V52` (heredados de Zafiro), `P01`–`P30` (red mínima), `PX01`–`PX04` (propios de dos plantas) | 86 |
| `RED-MINIMA-E01-E18.csv` | La red mínima a nivel de bloque: 18 vínculos entre 17 bloques y partidas, y lo que crece con una planta más | 18 |
| `RUTAS-DE-RELEVOS.csv` | La cadena de relevos con holgura 0 de cada programa, paso por paso | 110 |
| `RED-NO-ESCRITA.csv` | Los vínculos de Zafiro que un derivado no hereda, y por qué | 77 |
| `PIDEN-MAS-CUADRILLA.csv` | Las partidas que piden dos o más veces la cantidad por día de su gemela de Zafiro | 59 |
| `EMPAREJAMIENTOS-POR-ROL.csv` | Las partidas de los cuatro de dos plantas que no tienen gemela por `Clave`, con la gemela de Zafiro que se les asignó y por qué | 205 |
| `ESTRUCTURA-PLANTA-ALTA-VS-BAJA.csv` | La estructura de la planta alta contra la de la planta baja de Zafiro | 25 |
| `SUPUESTOS-A-VALIDAR.csv` | Los doce supuestos que el planeador debe validar en cada programa de dos plantas | 48 |
| `ZAFIRO-15-INCUMPLIDOS.csv` | El registro de los 15 vínculos de Zafiro que no se cumplen, con la propuesta del sistema y qué pasa con cada uno al cargarlo | 15 |
| `SF-LOS-OCHO.csv` | Los ocho `SF` del libro, leídos como `SF` y al revés | 8 |
| `SEGUNDA-RUTA-BORRADOR.csv` | La segunda ruta de cuadrilla (D-444), en borrador | 21 |
| `SEGUNDA-RUTA-LO-QUE-SIGUE.csv` | Lo que arranca justo después de que termina esa ruta | 9 |

**`PROGRAMAS-PROTOTIPOS.csv`, columna por columna.** `prototipo`, `fila` (el número de fila del libro
de los siete, que es lo que citan los vínculos) y `oid` (la llave estable: único en las 3,231 filas,
así que el cargador resuelve fila → `Oid` → `Nodo` → `ACTIVIDAD` y guarda la llave, nunca el número
de fila, D-442) · `tipo` (`Capítulo`, `Subcapítulo`, `Nivel 2`, `Nivel 3`, `Concepto`), `nivel`,
`clave`, `descripcion`, `unidad`, `cantidad`, `total` · `vinculos` (el formato fuente
`<fila><FS|SS|FF|SF>[±horas]`, con el desfase en horas de 8 por día) y `vinculo_agregado_d460` (el
único token que sumó D-460 y no venía en el libro) · `inicio`, `termino`, `dias_laborables` ·
`frente` (el nivel de obra, Nivel 1) y `etapa` (el sub-frente, Nivel 2) y `cuadrillas` con
`cuadrillas_con_dato` (D-438, D-439, D-440) · `regla`, `gemelo_zafiro_fila` (cómo se programó y con
quién se emparejó, solo en los cuatro de dos plantas) · `duracion_origen` (`heredada`, `propia` o
`sin referencia`, D-441), `dias_zafiro` y `referencia_tipo`.

**Las filas de bloque** (`Subcapítulo`, `Nivel 2`, `Nivel 3`) llevan las fechas derivadas de sus
partidas; solo una fila de bloque con un vínculo que la cita como predecesora existe como
`ACTIVIDAD` resumen (D-442).

---

# 3. Los siete programas: cifras de referencia

Todos arrancan el lunes 9-jun-2025. Calendario del ejercicio: lunes a viernes sin el 25-dic ni el
1-ene (D-428); se trabaja el 16-sep y el 17-nov, como en Zafiro. Una planta cierra a las 28 semanas
(jueves 18-dic, 139 días hábiles) y dos plantas a las 30 (lunes 5-ene-2026, 149 días hábiles; D-419).

| Prototipo | Plantas | Cierre | Días hábiles | Partidas con fechas | Celdas con vínculos | Vínculos (libro) | FS | SS | FF | SF | Los que citan un bloque |
|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Zafiro | 1 | 18-dic | 139 | 315 | 102 | 124 | 97 | 15 | 8 | 4 | 44 |
| Rubí | 1 | 18-dic | 139 | 294 | 81 | 102 | 83 | 13 | 6 | 0 | 38 |
| Jade | 1 | 18-dic | 139 | 289 | 70 | 85 | 70 | 10 | 5 | 0 | 25 |
| Zafiro Plus | 2 | 5-ene | 149 | 388 | 108 | 130 | 106 | 14 | 9 | 1 | 34 |
| Diamante sin chimenea | 2 | 5-ene | 149 | 377 | 105 | 129 | 107 | 14 | 7 | 1 | 42 |
| Diamante con chimenea | 2 | 5-ene | 149 | 380 | 106 | 130 | 108 | 14 | 7 | 1 | 43 |
| Oro | 2 | 5-ene | 149 | 402 | 108 | 132 | 109 | 11 | 11 | 1 | 37 |
| **Siete** | | | | **2,445** | **680** | **832** | **680** | **91** | **53** | **8** | **263** |

Rubí y Jade suman un vínculo cada uno por D-460 (`498SF` y `1401SF`): 103 y 86 con él. Jade programa
además `MATERIAL PARA PRUEBAS`, sin cantidad (por eso D-423 habla de 289 y no de 288).

**Por qué Zafiro trae 124 vínculos y D-424 contó 75.** Son dos libros distintos de Zafiro, no un
error de conteo: el original (`PROGRAMA_ZAFIRO.xlsx`) tiene los 75 vínculos en 74 celdas de D-424; el
libro de los siete prototipos le suma la red mínima de D-426 (30 vínculos de red, `P01` a `P30`, que
se escriben en 42 celdas con 54 vínculos) y le quita los 5 que esa red reemplaza en la misma
partida: 75 − 5 + 54 = 124 vínculos, y 74 + 28 = 102 celdas. Los 15 que no se cumplen (§7) están en el
segundo; el original está intacto en cuanto a sus fechas.

**Qué prueba cada cifra** (`backend/core/tests/test_motor_cpm.py`): los 832 vínculos y su mezcla de
tipos; los 8 `SF` (5 se cumplen con holgura 0, todos las gualdras); Zafiro 15 incumplidos (10 `FS`, 2
`SS`, 3 `SF`) y 18 si el bloque se lee completo; 0 incumplidos en los otros seis; los 39 vínculos
cuyo bloque contiene a su sucesora, 35 cumplidos; el cierre en 139 o 149 días hábiles; la herencia de
duraciones 1,520 / 132 / 478 (D-441); las cadenas de relevos de los cinco programas que las tenían, fila por
fila (§6.4); y los seis vínculos de Zafiro que el cargador no deja pasar (§4.5).

---

# 4. El motor: `backend/core/motor_cpm.py`

Funciones puras sobre dataclasses, sin Django ni base de datos: recibe actividades, vínculos y un
calendario, y devuelve fechas, holguras y ruta crítica. **Nada se guarda ahí**: las fechas tempranas y
tardías, la holgura y `ACTIVIDAD.es_ruta_critica` son caché del motor, nunca fuente de verdad
(`MODELO.md` §5c). Los instantes son `Fraction` para que los medios días del `paso_dias` no pierdan
exactitud.

## 4.1 El contrato

| Pieza | Qué es |
|---|---|
| `Calendario(dias_laborables_semana, no_habiles, paso_dias, sentido_redondeo)` | `CALENDARIO_OBRA`: `n(d)` numera los días hábiles, `fecha(n)` los devuelve, `entre(a, b)` los cuenta, `acomodar(días)` aplica el redondeo de D-446 |
| `dias_teoricos(cantidad, rendimiento, cuadrillas)` · `cuadrillas_efectivas(cantidad, rendimiento, duración)` | La fórmula de D-446 y su inversa: el redondeo mueve las cuadrillas, no el esfuerzo |
| `Vinculo(predecesora, sucesora, tipo, desfase)` | Tipo `FS`, `SS`, `FF`, `SF` o los nombres del enum (`fin_inicio`, `inicio_inicio`, `fin_fin`, `inicio_fin`); desfase en días hábiles, negativo traslapa |
| `desfase_en_dias(horas)` | El formato fuente guarda horas; la jornada es de 8 |
| `Ventana(inicio, fin)` · `holgura_instantes` · `holgura_vinculo` | Las cuatro fórmulas de `MODELO.md` §5c, por instantes (apertura = inicio del primer día hábil, cierre = fin del último) |
| `ventana_de_bloque(descendientes, fechas, excluir)` | El mínimo de inicio y el máximo de fin de las partidas del bloque, sin la sucesora (D-443) |
| `vinculos_incumplidos(fechas, vínculos, calendario, bloques)` | Los vínculos con holgura negativa: la lectura que dispara `ALERTA(tipo=vinculo_incumplido)` |
| `Actividad(id, duración, hijos, ancla)` | Una partida, o un bloque con sus hijos (`derivada_de_hijos`); `ancla` es el disparador contractual: no arranca antes |
| `calcular_cpm(actividades, vínculos, calendario, inicio, plazo_dias)` → `ResultadoCPM` | Por actividad: inicio y fin tempranos y tardíos, holgura total, `es_ruta_critica`, fechas; además `fin_proyecto`, `limite` y `ruta_critica` |
| `dias_de_atraso(curva, t, avance)` · `retraso_neto(planeado, ejecutado, ingeniería)` | El retraso por tiempo ganado y el retraso neto con signo (D-456, D-457) |
| `CicloError` · `VinculoInvalido` | Se rechazan solo el autovínculo y los ciclos reales entre partidas, la sucesora que es un bloque (D-442), una actividad o un tipo desconocidos |

## 4.2 Lo que se decidió al construirlo

1. **Un bloque como predecesora no se ordena topológicamente: se itera hasta que nada se mueva.** La
   ventana de un bloque depende de las demás partidas del bloque, que pueden depender a su vez de la
   sucesora (la gualdra va antes de su losa y el `SF` de la gualdra cita el grupo de esa misma losa).
   Ordenar con aristas desde todos los descendientes del bloque da ciclos falsos en los seis programas
   limpios; el cálculo es un punto fijo creciente hacia adelante y decreciente hacia atrás, y solo las
   aristas directas partida → partida pueden formar un ciclo real.
2. **La ventana hacia atrás se toca solo en las partidas que la fijan.** Para `SS` y `SF`, el límite
   tardío de un bloque recae en los descendientes con el inicio más temprano; los demás se mueven por
   sus propios vínculos.
3. **El plazo da holgura negativa, no error.** Con `plazo_dias` menor al fin temprano, las partidas de
   la ruta crítica quedan con holgura negativa y se distinguen de las que no tienen margen.
4. **La ruta crítica son las partidas con holgura menor o igual a cero**, por inicio temprano. Los
   bloques derivan su holgura de sus partidas (la mínima) y no entran en la lista.
5. **Los hitos duran cero** y no ocupan un día.
6. **El arranque se corre al primer día hábil**; el ancla contractual solo retrasa.
7. **`Fraction` hasta el final**: las fechas se calculan al devolver el resultado, no antes.

## 4.3 Lo que el motor no hace (y dónde está pendiente)

- No nivela recursos ni respeta `FRENTE_TOPE_CUADRILLA`: el tope se vigila con la alerta, no se aplica
  en el cálculo (D-449).
- No parte una actividad en tramos con pausa (P-5, D-259): entrega una ventana por actividad, y los
  tramos que la parten por una pausa técnica o de recurso son de la capa de aplicación (`MODELO.md` §5c).
- No lee ni escribe en la base de datos; la integración con `ACTIVIDAD` y `PRECEDENCIA` es de la capa de
  aplicación.
- No dibuja: las reglas del Gantt están en §8 y siguen siendo propuesta.

## 4.4 Qué calcula con la red que hay

Los programas tienen unos 130 vínculos sobre unas 380 partidas; entre 213 y 294 partidas, según el
programa, no tienen ninguna predecesora. El CPM más temprano no tiene por qué reproducir el cierre del
plan hecho a mano, y de hecho solo lo hace en dos de los seis programas sin vínculos rotos. Es un hecho
medido, no una falla:

| Prototipo | CPM (días hábiles) | Plan | Ruta crítica del motor (partidas) | Lectura |
|---|---:|---:|---:|---|
| Rubí | 139 | 139 | 48 | La red alcanza para reproducir el cierre |
| Jade | 139 | 139 | 42 | Igual |
| Diamante sin chimenea | 139 | 149 | 56 | Los 10 días de la planta alta son decisión de cuadrilla, no precedencia |
| Diamante con chimenea | 139 | 149 | 55 | Igual |
| Oro | 139 | 149 | 55 | Igual |
| Zafiro Plus | 81 | 149 | 28 | Le falta `P16` (vertedero tras la boquilla fina interior, déficit 10 en el plan): sin él la cola de acabados no cuelga de la obra gris. Con `P16` escrito el motor calcularía 135 |

Dos consecuencias. **La ventana de dos semanas de la planta alta (D-426) se queda como decisión del
planeador**, no como algo que la red deduzca: es lo que D-425 ya observó en Zafiro («la estructura sí está
unida al cierre, pero por las fechas y no por un vínculo»). Y **`P16` es un vínculo que carga peso**: no es un
detalle que se pueda dejar sin escribir sin que el CPM lo note, y por eso queda anotado como el único
hueco de la red de Plus (§6.5). *(Corrige D-460, que lo daba como incumplido de los cuatro de dos
plantas: en Diamante sin chimenea, Diamante con chimenea y Oro está escrito y se cumple.)*

## 4.5 El cargador, la cadena de relevos y el Gantt como dato: `backend/core/programa.py`

Une las filas del libro con el motor. Lee un programa tal como lo traen los siete prototipos, resuelve sus
vínculos y entrega actividades al CPM; no dibuja y no toca la base de datos.

| Pieza | Qué hace |
|---|---|
| `Fila` · `filas_desde_csv(ruta, prototipo)` | Una fila del libro con su `oid`, su número de fila, sus fechas y el texto de sus vínculos; el CSV de `programas/` es entrada de primera clase |
| `leer_vinculos(texto)` | Separa `<fila><tipo>[±horas]`, con el tipo `FS`, `SS`, `FF` o `SF`, en fila, tipo y desfase en días; un token que no cumple el formato no se pierde, se rechaza |
| `cargar_programa(filas, calendario)` → `Programa` | Actividades, vínculos aceptados, `rechazados` con su motivo, las ventanas del plan y las partidas de cada bloque |
| `Programa.calcular()` · `.incumplidos()` | El CPM de la red cargada y los vínculos que las fechas del plan contradicen |
| `Programa.referencias(v)` | La partida que fija el extremo de la predecesora de un vínculo; si es un bloque, todas las que empatan |
| `cadena_de_relevos(programa, calendario)` | La cadena de partidas con holgura 0 sobre las fechas del plan (§6.4) |
| `vista_gantt(programa, calendario, …)` | El árbol completo (capítulo, frentes, etapas, Nivel 3, partidas) con su `padre`, las flechas, las marcas de §8 y, si se pide, la base de una reprogramación y todo lo necesario para editar en pantalla |

**Las reglas de carga son las de D-442 y D-443**: el desfase viene en horas y la jornada es de 8; el programa
guarda el `oid`, nunca el número de fila; un bloque puede ser predecesora, también el que contiene a su
sucesora, y se lee sin ella; la sucesora siempre es una partida. Se rechazan, sin detener la carga, y quedan
en `Programa.rechazados` para que los vea el planeador:

| Motivo | Cuándo |
|---|---|
| `autovinculo` | La partida cita su propia fila |
| `cierra_un_ciclo` | El vínculo forma parte de un ciclo entre partidas, o a través de un bloque cuyo extremo espera a la sucesora. De cada ciclo se rechaza el que las fechas del propio plan ya contradicen, y si ninguno, el último escrito |
| `sucesora_bloque` | La celda de vínculos está en una fila de bloque |
| `formato` · `predecesora_desconocida` · `predecesora_sin_partidas` | El token no se lee, cita una fila que no existe o un concepto sin fechas, o un bloque sin partidas |

**Un vínculo que las fechas contradicen sí se carga**: ese es el aviso de `ALERTA(tipo=vinculo_incumplido)`, no
un error de carga. Con los siete programas reales, solo Zafiro rechaza algo: **seis de sus 124 vínculos** (118
cargan). Son el autovínculo `EST-01151` y cinco ciclos: el de `BAP-01100` y `ICA-01030`, que se queda con el
`SS` y suelta el `FS`, y cuatro de partidas hermanas dentro de un mismo grupo —las dos manos de pintura de
`API-01010`, el muro sillar bajo `ECO-00046`, el firme de la cisterna—, donde cada una espera al resto del
grupo, que incluye a la otra. Los otros nueve de los 15 incumplidos cargan y avisan. `ZAFIRO-15-INCUMPLIDOS.csv`
dice qué pasa con cada uno (columna `al_cargar`).

Al motor se le añadió el diagnóstico que esto pedía: cuando el cálculo no converge, `CicloError.vinculos` trae
los vínculos que forman el ciclo que se alarga, rastreados desde quién empujó el arranque de cada partida.

## 4.6 Editar y reprogramar: `reprogramar` en `backend/core/programa.py`

El planeador edita y el sistema reprograma, por lo mínimo, y dice qué cuesta antes de que se decida
(§8). Cinco ediciones, repartidas en los dos permisos que ya existen (`MODELO.md` §5b):

| Edición | Qué cambia | Permiso |
|---|---|---|
| `CambiarDuracion(llave, días)` | La partida dura esos días hábiles, contando sus paros | `editar_estructura_programa` (Control de obra) |
| `AgregarVinculo` · `QuitarVinculo` · `CambiarVinculo` | Un vínculo de la red: tipo, espera o traslape, o que deje de existir | `editar_estructura_programa` |
| `FijarInicio(llave, fecha)` | La partida no arranca antes de esa fecha | `editar_fechas_programa` (Residente) |

**El empuje mínimo.** Cada partida conserva su arranque del plan y solo se corre lo que una edición obliga, y
solo hacia adelante. Es el CPM con el arranque del plan como disparador de cada partida. Tiene tres
consecuencias que son la regla, no un detalle:

- Sin ediciones, un plan que cumple todos sus vínculos queda **idéntico**. Pasa en los seis programas limpios
  (0 partidas movidas) y es la prueba de que el empuje no inventa nada.
- **Quitar un vínculo o acortar una duración nunca adelanta nada**: adelantar es una decisión y se toma
  fijando un arranque. Con `modo="temprano"` se suelta el plan y se calcula el CPM más temprano de la red,
  que con la red mínima de hoy colapsa (§4.4); es un diagnóstico, no un modo de trabajo.
- Un plan que no cumple sus vínculos se corre hasta cumplirlos. Si Zafiro obedeciera los 118 vínculos que
  cargan (§4.5) se moverían 47 partidas y cerraría el 7-ene-2026, 12 días hábiles después. Zafiro sigue de
  origen (D-444): es lo que costaría que la red mandara sobre el plan manual.

**El impacto**, que se devuelve con el programa nuevo, es lo que el planeador ve antes de decidir: las
partidas movidas (cuántos días hábiles se corre el arranque y el término de cada una), el cierre antes y
después, la ruta antes y después y si cambia —`ruta_cambia` sigue D-100: la ruta se recalcula siempre y
solo avisa si cambia de actividades; correr fechas no es noticia—, los vínculos que siguen sin cumplirse y
las ediciones que no se pudieron aplicar con su motivo (`actividad_desconocida`, `duracion_invalida`,
`autovinculo`, `sucesora_no_es_partida`, `repetido`, `cierra_un_ciclo`, `vinculo_inexistente`), que no frenan a
las demás.

**Lo que mide con datos reales.** Agregar `P16` a Plus (vertedero tras la boquilla fina interior, `FS+1`) corre el
cierre del 5 al 19-ene-2026: **10 días hábiles**, exactamente el «déficit 10» de D-437 y lo que D-460 decía
que costaría cerrarlo (30 a 32 semanas). Alargar el muro de la planta alta de 7 a 12 días mueve 5 partidas y
no mueve el cierre. Fijar el arranque del vertedero cinco días después mueve 31 y corre el cierre cinco.

**El mismo motor, en el navegador.** La pantalla reprograma sin ir al servidor y por eso trae su propia
implementación (`frontend/gantt/motor_gantt.js`). Una prueba corre las dos con las mismas ediciones sobre
Zafiro Plus —duraciones, arranques en sábado, vínculos agregados, quitados y cambiados, ediciones
rechazadas, el modo temprano— y exige el mismo cierre, los mismos días, las mismas partidas movidas, la
misma ruta y los mismos rechazos.

## 4.7 Guardar lo que se edita: `servicio_programa.py`, `memoria_programa.py` y `infra/postgres_programa.py`

Lo que se guarda es **la bitácora de ediciones**, no las fechas. El programa base —las filas y los vínculos
con que se importó— no cambia, y el programa vigente es `reprogramar(base, ediciones aplicadas)`. Así nada
puede quedar a medias, deshacer una edición es repetir la cuenta sin ella y cualquiera puede reconstruir cómo
se llegó a las fechas de hoy. Es la misma arquitectura del motor de cálculo (D-182): el dominio define un
puerto, `RepositorioPrograma`, y hay dos adaptadores, uno en memoria para las pruebas y otro para Postgres, que
cumplen el mismo contrato.

| Pieza | Qué hace |
|---|---|
| `ServicioPrograma.abrir(programa)` | La base más lo aplicado: el programa que se ve, con su versión |
| `proponer(programa, edición, rol)` | Qué pasaría: el impacto contra el programa vigente. No guarda nada |
| `aplicar(programa, edición, rol, usuario)` | Propone y, si se puede, guarda la edición con lo que el sistema mostró. Una que no se puede aplicar vuelve con su motivo y sin guardarse |
| `deshacer(programa, edición, rol, usuario)` | La marca revertida y repite la cuenta sin ella; si otras ediciones dependen de ella, dice cuáles y no toca nada (`NoSePuedeDeshacer`) |
| `PermisoDenegado` · `Conflicto` | El rol no puede esa edición; o alguien editó entre que se calculó el impacto y se quiso guardar |

**Los permisos son los de `MODELO.md` §5b**: la estructura (duración y vínculos) es de `control_de_obra` y las
fechas, de `residente`; ningún otro rol edita, y deshacer pide el permiso de la edición que se deshace.

**El candado es una versión.** Cada edición o reversión sube `programa.version`; quien guarda dice qué versión
vio y, si ya es otra, `Conflicto`, sin pisar. La versión se lee antes que las ediciones: si algo cambia entre
las dos lecturas, el candado salta en vez de dejar pasar un impacto viejo.

**Cada edición guarda** quién la hizo y con qué rol, la edición tal como se pidió (citando el `oid`, nunca el
número de fila), lo que el sistema mostró al decidir —partidas movidas, cierre antes y después, si cambia la
ruta— y, si agrega o cambia un vínculo, su **`origen`** (`tecnica`, `recurso` o `decision`; la confianza se
deriva de él). Sin declarar, el vínculo nace con `decision`, el de menor confianza, que es el que se revisa
primero. Los vínculos importados vienen sin origen declarado y se quedan así: no se inventa lo que el libro no
dice. *(Propuesta sin confirmar, de D-463; D-464 la implementa.)*

**En Postgres** (`database/migraciones/0001_programa.sql`): `programa`, `programa_fila`, `programa_vinculo` y
`edicion_programa`. La bitácora ni se borra ni se reescribe —un disparador deja pasar solo el cambio de
`aplicada` a `revertida`, y ni borrar el programa que la contiene—; un vínculo editado no puede quedar sin
origen, una edición no puede quedar sin autor, y un vínculo no puede citar una fila que no existe. Los
vínculos que el cargador rechazó se guardan con su motivo, y los tipos usan los nombres del modelo
(`fin_inicio`, `inicio_inicio`, `fin_fin`, `inicio_fin`).

**Lo que todavía no es ese esquema.** Este corte no cuelga de `NODO`, `PRESUPUESTO` ni `CALENDARIO_OBRA`, que
aún no tienen tabla (B-03): el calendario va como JSON dentro de `programa` y las filas guardan el árbol del
libro. Cuando esas tablas existan, `programa_fila` se vuelve `ACTIVIDAD` y `TRAMO` sin tocar la bitácora, que
cita `oid`. Tampoco hay API: la superficie pública es FastAPI (D-54) y se escribe sobre este servicio.

## 4.8 Cómo se prueba

`cd backend && python3 -m unittest discover` corre 168 pruebas. Las del CPM están en
`backend/core/tests/test_motor_cpm.py`, las del cargador, la reprogramación y el Gantt en `test_programa.py` y
la del motor del navegador en `test_motor_gantt_js.py` (usa `node`, que el CI trae); la persistencia se prueba
con un mismo contrato (`contrato_programa.py`) contra el adaptador en memoria y contra un **Postgres de
verdad** (`pgserver`, embebido, que el CI instala), más lo que solo Postgres garantiza; siguen el principio del repositorio —datos reales del
proyecto, no fixtures inventadas—: los casos chicos son aritmética de las fórmulas de D-445 verificada
a mano, y las de conformidad cargan `PROGRAMAS-PROTOTIPOS.csv` y los demás archivos de `programas/`
y comprueban las cifras de §3, §6 y §7. Si un número de este archivo cambia, una prueba tiene que
cambiar con él.

---

# 5. Cómo se armó cada programa derivado

Los seis derivados parten de Zafiro, el único programa terminado por el residente (D-390). La regla con
la que se programó cada partida de los cuatro de dos plantas está en la columna `regla` del CSV, y con
quién se emparejó en `gemelo_zafiro_fila`:

| Regla | Qué hace | Plus | Diamante sin | Diamante con | Oro |
|---|---|---:|---:|---:|---:|
| `gemelo por Clave` | Misma `Clave` en Zafiro: toma su ventana, y si cruza el 18-ago, los 10 días de la planta alta | 204 | 202 | 204 | 230 |
| `gemelo por Clave (otro bloque)` | La misma `Clave` en otro bloque de Zafiro | 10 | 14 | 15 | 7 |
| `gemelo por rol` | Lo que Zafiro no tiene toma la ventana de lo que hace el mismo trabajo; cada par, con su porqué, está en `EMPAREJAMIENTOS-POR-ROL.csv` y lo corrige el planeador | 15 | 26 | 25 | 17 |
| `ventana del bloque (Zafiro)` | La partida toma la ventana de su bloque en Zafiro | 16 | 19 | 21 | 20 |
| `nivel preestablecido (Zafiro)` | Cancelería, carpintería, impermeabilización y cubiertas: duración fija (D-421) | 7 | 10 | 10 | 11 |
| `cimentación (bloque de Zafiro)` | La cimentación se arma con los bloques de Zafiro (D-418) | 43 | 49 | 48 | 51 |
| `losa por altura` | Primero las losas de 3.00, luego el muro que enrasa, luego las de 4.20 (D-421) | 49 | 26 | 26 | 34 |
| `losa única (unión)` | Una sola altura: las losas toman las dos ventanas unidas, como Jade (D-423) | — | 4 | 4 | — |
| `planta alta (ventana)` | La estructura y la losa de azotea dentro de la ventana de 10 días hábiles (18 al 29-ago en el calendario de Zafiro) | 44 | 27 | 27 | 32 |
| **Partidas** | | **388** | **377** | **380** | **402** |

Las reglas que valen para todos, con la decisión que las fijó:

- **Los metros extra no suman días** (D-421): una partida con más cantidad que su gemela conserva la
  ventana y sube la cantidad por día; el costo es más cuadrilla, y la lista de quién la pide está en §7.
- **El plazo lo fija el número de plantas**, no los metros cuadrados: 28 y 30 semanas (D-419).
- **El último día absorbe el residuo** del reparto diario, en los seis derivados; Zafiro queda como estaba
  (D-433).
- **Los pretiles van después de la losa de azotea completa** y la cadena de acabados que sigue se
  comprime con más cuadrilla para no mover el cierre (D-434 a D-437); en Plus, además, las cuatro losas de
  azotea van escalonadas 5 días y la cimentación se comprime de 11 a 7. `P16` es el único vínculo que no
  cierra en Plus y queda sin escribir (D-437).
- **El calendario es una opción del sistema** (D-428, D-447): agregar o quitar días no laborables y
  fines de semana, «solo como opción, no para este ejercicio».
- **Cada duración tiene origen** (D-441): de las 2,130 duraciones de los seis derivados, 1,520 se
  heredan de su gemela de Zafiro (71.4%), 132 son propias (6.2%) y 478 no tienen referencia (22.4%). La
  referencia es una llave explícita, no se deduce por `Clave`; quien edita una duración pasa a ser la
  referencia de su alcance.

---

# 6. La red

## 6.1 Las familias de vínculos

Los vínculos escritos en el libro vienen de tres familias (`V`, `P` y `PX`); la cuarta (`E`) es la red a
nivel de bloque de la que salieron las `P`. El identificador dice de dónde viene un vínculo y quién lo
mantiene:

| Familia | Cuántos | Origen |
|---|---:|---|
| `V01`–`V52` | 52 | Los vínculos de Zafiro que se cumplen con sus propias fechas (D-424); Rubí hereda 46 y Jade 42 (D-425) |
| `E01`–`E18` | 18 | La red mínima a nivel de bloque: la cadena de 28 pasos de Zafiro leída de sus propias fechas (D-425) |
| `P01`–`P30` | 30 | La red mínima bajada a las partidas que arrancan o terminan por ella, con la cadena validada por el usuario (D-426) |
| `PX01`–`PX04` | 4 | Los eslabones propios de las dos plantas: lo que une la planta alta con la baja (D-427) |

El catálogo completo de las 86 filas `V`, `P` y `PX` está en `CATALOGO-DE-LA-RED.csv`.

## 6.2 La red mínima entre bloques (`E01`–`E18`)

La espina del programa: 18 vínculos entre 17 bloques y partidas, todos con holgura 0 en Zafiro; 14 son
de origen técnico y 4 de decisión (la cancelería arranca al terminar el piso de áreas comunes y la
carpintería entra cuando terminan las dos cancelerías, ambas de contrato terminado). Las instalaciones
no están en la cadena: las de muros terminan de 17 a 22 días hábiles antes del repellado y las de
losa viven dentro de las ventanas de armado.

| Id | Predecesora → sucesora | Vínculo | Origen | Por qué |
|---|---|---|---|---|
| E01 | ECO-00001 ESTRUCTURA CIM → EST-02010 MURO TABIQUE DE 14 CM | FS-1 | técnica | los muros se levantan sobre la losa de cimentación; el primer día de muro es el último de la losa (traslape de 1 día) |
| E02 | EST-02010 MURO TABIQUE DE 14 CM → CAR-01011 GUALDRA 6X12X8 | SS+15 | técnica | la gualdra se coloca cuando ya están levantados los muros de 3.00 (corridas 1 y 2 del muro tabique) |
| E03 | CAR-01011 GUALDRA 6X12X8 → EST-21011 LOSA MACIZA ZAFIRO 3.00 (125 M2) | FS | técnica | la losa de 3.00 arranca al día siguiente de colocar la gualdra (en Zafiro el vínculo estaba al revés: gualdra SF losa) |
| E04 | EST-21011 LOSA MACIZA ZAFIRO 3.00 (125 M2) → EST-21031 LOSA NERVADA ZAFIRO 4.20 (40 M2) | SS+9 | técnica | entre una losa y otra va el muro que enrasa la de 4.20; la de 4.20 arranca 9 días hábiles después de que arranca la de 3.00 |
| E05 | EST-21031 LOSA NERVADA ZAFIRO 4.20 (40 M2) → ECO-00018 ESTRUCTURA AZ | FF+3 | técnica | pretiles y castillos de la azotea terminan 3 días hábiles después de que termina la losa de 4.20 (curada) |
| E06 | EST-21011 LOSA MACIZA ZAFIRO 3.00 (125 M2) → ECO-00018 ESTRUCTURA AZ | SS+7 | técnica | los pretiles arrancan 7 días hábiles después de que arranca la losa de 3.00: ya hay losa colada donde pararlos |
| E07 | ECO-00018 ESTRUCTURA AZ → ECO-00023 ALBAÑILERÍA AZ | FF+15 | técnica | la albañilería de azotea (repellados, boquilla, relleno, chaflán) termina 15 días hábiles después de los pretiles: es lo que dura esa cadena |
| E08 | ECO-00023 ALBAÑILERÍA AZ → ECO-00050 IMPERMEABILIZACIÓN | FS | técnica | la membrana va sobre el relleno y el chaflán terminados |
| E09 | ECO-00050 IMPERMEABILIZACIÓN → ECO-00057 OBRA GRIS PB | FF+15 | técnica | las finas interiores esperan la impermeabilización y duran 15 días hábiles: plafones, interiores, boquilla fina |
| E10 | ECO-00057 OBRA GRIS PB → ECO-00024 ACABADOS PB | FS+1 | técnica | pisos, regaderas y mármol van después de las finas; en Zafiro hay un día de espera (lunes 6-oct sin trabajo en este bloque) |
| E11 | ECO-00024 ACABADOS PB → ECO-00033 CANCELERÍA PB | SS+19 | decisión | la cancelería de planta baja arranca al terminar el piso de áreas comunes (31-oct); el vínculo derivado es SS+19 desde el arranque de acabados |
| E12 | ECO-00024 ACABADOS PB → ECO-00035 CANCELERÍA AZ | SS+19 | decisión | igual para la cancelería de azotea: el mismo día que la de planta baja |
| E13 | ECO-00033 CANCELERÍA PB → ECO-00036 CARPINTERÍA PB | FS | decisión (contrato terminado) | la carpintería entra al terminar la cancelería (casa cerrada); en la ruta de Cancelería, Carpintería y Herrería, de contrato terminado |
| E14 | ECO-00035 CANCELERÍA AZ → ECO-00036 CARPINTERÍA PB | FS | decisión (contrato terminado) | la carpintería entra cuando terminan las dos cancelerías, la de planta baja y la de azotea (las dos terminan el 14-nov) |
| E15 | ECO-00036 CARPINTERÍA PB → API-01010 PINTURA PB | FF+5 | técnica | la segunda mano de pintura va después de puertas, closets y vanities; termina 5 días hábiles después de que termina la carpintería |
| E16 | API-01010 PINTURA PB → API-01020 LIMPIEZA Y SELLADO SILICÓN PB | FF+4 | técnica | limpieza y sellado final después de la segunda mano; termina 4 días hábiles después y cierra la obra |
| E17 | ECO-00036 CARPINTERÍA PB → ACA-00021 CUBIERTAS COCINA | FS | técnica | la cubierta de cocina va sobre los muebles de cocina: arranca al día siguiente de terminar la carpintería (segunda ruta que termina el 18-dic) |
| E18 | ACA-00021 CUBIERTAS COCINA → ECO-00040 EQUIPAMIENTOS | FF | técnica | estufa, campana y accesorios terminan el mismo día que la cubierta de cocina: el último día de la obra |

## 6.3 La red de las partidas (`P01`–`P30`, `PX01`–`PX04`)

Un vínculo `P` se escribe solo si se cumple con las fechas del propio programa; cada sucesora se
enlaza con la predecesora de su piso. Las columnas «Predecesora» llevan el tipo y el desfase en días
hábiles.

| Id | Sucesora(s) en Zafiro | Predecesora(s) y vínculo | Origen | Por qué |
|---|---|---|---|---|
| P01 | 68 EST-02010 MURO TABIQUE DE 14 CM | 4 ECO-00001 FS-1 | técnica | el muro tabique de planta baja arranca el último día de la losa de cimentación (traslape de 1 día) |
| P02 | 80 CAR-01011 GUALDRA 6X12X8 | 68 EST-02010 SS+15 | técnica | la gualdra se coloca 15 días hábiles después de que arranca el muro (levantados los muros de 3.00) |
| P03 | 79 EST-21011 LOSA MACIZA ZAFIRO 3.00 (125 M2) | 80 CAR-01011 FS | técnica | la losa maciza de 3.00 arranca al día siguiente de la gualdra |
| P04 | 83 EST-21031 LOSA NERVADA ZAFIRO 4.20 (40 M2) | 79 EST-21011 SS+9 | técnica | la losa de 4.20 arranca 9 días hábiles después que la de 3.00: entre una y otra va el muro que enrasa |
| P05 | 166 EST-02010 MURO TABIQUE DE 14 CM | 79 EST-21011 SS+7; 83 EST-21031 FF | técnica | el muro de pretiles arranca 7 días hábiles tras la losa de 3.00 y termina con la losa de 4.20 |
| P06 | 167 EST-02110 CASTILLO K-1 15X15 | 79 EST-21011 SS+9; 83 EST-21031 FF+3 | técnica | los castillos de azotea arrancan tras la losa de 3.00 y terminan 3 días hábiles después de la de 4.20 |
| P07 | 172 ALB-01010 REPELLADO MURO 3.00 | 167 EST-02110 FS | técnica | repellado de muro de azotea el día siguiente de terminar castillos y pretiles |
| P08 | 173 ALB-01212 REPELLADO MUROS FACHADA +3.00 | 167 EST-02110 FF+7 | técnica | el repellado de muros +3.00 termina 7 días hábiles después de los castillos de azotea |
| P09 | 174 ACA-01051 BOQUILLA EXTERIOR | 173 ALB-01212 FS | técnica | boquilla exterior tras el repellado de muros +3.00 |
| P10 | 170 ALB-03014 RELLENO EN AZOTEA ANTIHUMEDAD | 174 ACA-01051 FS | técnica | relleno de azotea tras la boquilla exterior |
| P11 | 171 ALB-03020 CHAFLÁN 10 CM ANCHO ANTIHUMEDAD + RESINA + FIBRA | 170 ALB-03014 FS | técnica | chaflán tras el relleno |
| P12 | 403 ACA-04010 IMPERMEABILIZACIÓN SUBCONTRATO | 171 ALB-03020 FS | técnica | la membrana va sobre el chaflán terminado |
| P13 | 158 ACA-01020 FINAS INTERIORES +3.00 | 160 ACA-01040 FS | técnica | finas interiores +3.00 tras las finas de plafond de 4.20 |
| P14 | 157 ACA-01010 FINAS INTERIORES 3.00 | 158 ACA-01020 SS+1 | técnica | finas interiores de 3.00 arrancan un día después que las de +3.00 |
| P15 | 161 ACA-01060 BOQUILLA FINA INTERIOR | 157 ACA-01010 FS | técnica | boquilla fina interior tras las finas interiores |
| P16 | 192 ACA-01110 VERTEDERO SARDINEL 10X10 | 161 ACA-01060 FS+1 | técnica | los acabados arrancan tras la boquilla fina, con un día de espera (lunes 6-oct) |
| P17 | 190 ACA-01090 RENIVELACIÓN CHAROLAS DE REGADERA | 192 ACA-01110 FS | recurso | renivelación de charolas tras el vertedero (misma cuadrilla de baños) |
| P18 | 191 ACA-01100 SARDINEL 10X10 REGADERAS | 190 ACA-01090 FS | técnica | el sardinel de regaderas va sobre la charola renivelada |
| P19 | 197 ACA-02040 MÁRMOL TOMBOLEADO 10X10 CM | 191 ACA-01100 FS | recurso | mármol tomboleado tras el sardinel (orden de la cuadrilla de pisos) |
| P20 | 199 ACA-02050 MÁRMOL TRAVERTINO LARGOS LIBRES 30.05 CM | 197 ACA-02040 FS | recurso | mármol travertino tras el tomboleado |
| P21 | 193 ACA-02010 PISO LUGANO NATURALE 15X50 (RECÁMARAS) | 199 ACA-02050 FS | recurso | piso Lugano de recámaras tras el mármol |
| P22 | 195 ACA-02020 PISO BRUNEI BEIGE 60X60 (ÁREAS COMUNES) | 193 ACA-02010 FS | recurso | piso Brunei de áreas comunes tras el piso de recámaras |
| P23 | todas las partidas de ECO-00033 CANCELERÍA PB; todas las partidas de ECO-00035 CANCELERÍA AZ | 195 ACA-02020 FS | decisión | la cancelería arranca al terminar el piso de áreas comunes (31-oct) |
| P24 | todas las partidas de ECO-00036 CARPINTERÍA PB | 257 ECO-00033 FS; 259 ECO-00035 FS | decisión | la carpintería entra cuando terminan las dos cancelerías (contrato terminado) |
| P25 | 373 ACA-30012 PINTURA MURO INTERIOR 2DA MANO | 262 ECO-00036 FF+3 | técnica | la segunda mano de pintura de muros termina 3 días hábiles después de la carpintería |
| P26 | 376 ACA-30022 PINTURA PLAFOND 2DA MANO | 373 ACA-30012 FF+2 | técnica | la segunda mano de plafond termina 2 días hábiles después que la de muros |
| P27 | 379 ACA-08030 SELLADO CON SILICÓN MARCO DE CANTERA | 376 ACA-30022 FS | técnica | sellado y limpieza final tras la segunda mano de plafond |
| P28 | 383 ACA-10030 LIMPIEZA Y SELLADO PIEDRA LAJA; 384 ACA-10040 LIMPIEZA DE MÁRMOL | 379 ACA-08030 SS+2 | recurso | limpieza de piedra y de mármol, los dos últimos días |
| P29 | 327 ACA-02034 CUBIERTA DE COCINA | 262 ECO-00036 FS | técnica | la cubierta de cocina va sobre los muebles de cocina |
| P30 | 316 EQU-02010 ESTUFA ESTANDAR; 317 EQU-02020 CAMPANA ESTANDAR | 327 ACA-02034 FF | técnica | estufa y campana terminan con la cubierta de cocina, el último día |

Los eslabones propios de las dos plantas. `PX04` reemplaza a `P05` y `P06` en los cuatro: los pretiles
cuelgan de la losa de azotea y no de las de entrepiso.

| Id | Sucesora | Predecesora | Vínculo | Por qué |
|---|---|---|---|---|
| PX01 | estructura de la planta alta: muro tabique, castillos K-1, K-2, K-7 (y K-3, K-6 en Oro) | la última losa de la planta baja: la nervada de 4.20 en Plus y en Oro, el grupo de las losas en los dos Diamante | FS | la planta alta arranca el día hábil siguiente a que termina la última losa de la planta baja, que le sirve de piso |
| PX02 | cadenas CE-1 (y CE-2 en Diamante y Oro) de la planta alta | muro tabique de la planta alta | FF | las cadenas de cierre terminan el mismo día que el muro sobre el que se cuelan |
| PX03 | losa(s) de azotea, el acero K1 1.50 y el escalón forjado de la planta alta | cadena CE-1 de la planta alta | FS | la losa de azotea se cuela al día hábil siguiente de la cadena que la corona |
| PX04 | pretiles de la azotea: muro tabique 3er nivel y castillo K-1 | losa de azotea (la primera que cuela) | SS+3 | el muro de pretiles arranca 3 días hábiles después de que arranca la losa de azotea; D-434 los lleva a después de la losa completa |

## 6.4 Las rutas de relevos

Una ruta de relevos es la cadena de partidas con holgura 0 **sobre las fechas del plan**: cada una
arranca el día hábil en que termina la anterior. No es lo que calcula el motor (§4.4), que mide la
ruta crítica de la red, sino lo que lee el planeador en el programa hecho a mano. Ya no
se lee a mano: `cadena_de_relevos` la calcula (la cadena más larga de vínculos con holgura 0 que termina en el
cierre, contando como extremos del bloque a todas las partidas que empatan) y **reproduce fila por fila las
cinco publicadas**; para Rubí da 28 pasos y para Jade 27, que D-425 solo daba por cumplidas como red mínima. La de Zafiro, 28
pasos, cubre 138 de los 139 días hábiles (solo el lunes 6-oct no tiene paso) y es la que sostiene la
red mínima; el único relevo con espera es obra gris → acabados, un día, que la red declara como `FS+1`
para que diez días insertados antes lleguen completos al cierre. La validó el usuario (D-426).

| Paso | Clave | Partida | Del → al | Relevo | Origen |
|---|---|---|---|---|---|
| 1 | EST-01040 | LOSA CIMENTACIÓN ZAFIRO 1P | 9-jun → 23-jun | — | arranque |
| 2 | EST-02010 | MURO TABIQUE DE 14 CM | 23-jun → 29-jul | FS-1 | técnica |
| 3 | CAR-01011 | GUALDRA 6X12X8 | 14-jul → 14-jul | SS+15 | técnica |
| 4 | EST-21011 | LOSA MACIZA ZAFIRO 3.00 (125 M2) | 15-jul → 4-ago | FS | técnica |
| 5 | EST-21031 | LOSA NERVADA ZAFIRO 4.20 (40 M2) | 28-jul → 15-ago | SS+9 | técnica |
| 6 | EST-02110 | CASTILLO K-1 15X15 | 28-jul → 20-ago | FF+3 | técnica |
| 7 | ALB-01212 | REPELLADO MUROS FACHADA +3.00 | 4-ago → 29-ago | FF+7 | técnica |
| 8 | ACA-01051 | BOQUILLA EXTERIOR | 1-sep → 3-sep | FS | técnica |
| 9 | ALB-03014 | RELLENO EN AZOTEA ANTIHUMEDAD | 4-sep → 8-sep | FS | técnica |
| 10 | ALB-03020 | CHAFLÁN 10 CM ANCHO ANTIHUMEDAD + RESINA + FIBRA | 9-sep → 10-sep | FS | técnica |
| 11 | ACA-04010 | IMPERMEABILIZACIÓN SUBCONTRATO | 11-sep → 12-sep | FS | técnica |
| 12 | ACA-01040 | FINAS PLAFOND 4.20 | 15-sep → 16-sep | FS | técnica |
| 13 | ACA-01020 | FINAS INTERIORES +3.00 | 17-sep → 22-sep | FS | técnica |
| 14 | ACA-01010 | FINAS INTERIORES 3.00 | 18-sep → 30-sep | SS+1 | técnica |
| 15 | ACA-01060 | BOQUILLA FINA INTERIOR | 1-oct → 3-oct | FS | técnica |
| 16 | ACA-01110 | VERTEDERO SARDINEL 10X10 | 7-oct → 7-oct | FS+1 | técnica |
| 17 | ACA-01090 | RENIVELACIÓN CHAROLAS DE REGADERA | 8-oct → 8-oct | FS | recurso |
| 18 | ACA-01100 | SARDINEL 10X10 REGADERAS | 9-oct → 9-oct | FS | técnica |
| 19 | ACA-02040 | MÁRMOL TOMBOLEADO 10X10 CM | 10-oct → 15-oct | FS | recurso |
| 20 | ACA-02050 | MÁRMOL TRAVERTINO LARGOS LIBRES 30.05 CM | 16-oct → 21-oct | FS | recurso |
| 21 | ACA-02010 | PISO LUGANO NATURALE 15X50 (RECÁMARAS) | 22-oct → 24-oct | FS | recurso |
| 22 | ACA-02020 | PISO BRUNEI BEIGE 60X60 (ÁREAS COMUNES) | 27-oct → 31-oct | FS | recurso |
| 23 | CAN-01002 | CANCELERÍA ZAFIRO | 3-nov → 14-nov | FS | decisión |
| 24 | CAR-03020 | COCINA ZAFIRO | 17-nov → 5-dic | FS | contractual |
| 25 | ACA-30012 | PINTURA MURO INTERIOR 2DA MANO | 8-dic → 10-dic | FS | técnica |
| 26 | ACA-30022 | PINTURA PLAFOND 2DA MANO | 11-dic → 12-dic | FS | técnica |
| 27 | ACA-08030 | SELLADO CON SILICÓN MARCO DE CANTERA | 15-dic → 16-dic | FS | técnica |
| 28 | ACA-10030 | LIMPIEZA Y SELLADO PIEDRA LAJA | 17-dic → 18-dic | SS+2 | recurso |

Las de los cuatro de dos plantas (el detalle, paso por paso, está en `RUTAS-DE-RELEVOS.csv`). La de Plus
arranca en el vertedero (21-oct) porque `P16` no está escrito; las de los otros tres arrancan en el
castillo de los pretiles de la azotea (15-sep) y cierran en la limpieza de mármol:

| Prototipo | Pasos | Del → al | Claves en orden |
|---|---:|---|---|
| Zafiro Plus | 13 | 21-oct → 5-ene | ACA-01110 → ACA-01090 → ACA-01100 → ACA-02040 → ACA-02050 → ACA-02010 → ACA-02020 → CAN-01021 → CAR-02050 → ACA-03025 → ACA-03026 → ACA-08050 → ACA-10040 |
| Diamante sin chimenea | 23 | 15-sep → 5-ene | EST-02110 → ALB-01212 → ACA-01051 → ALB-03014 → ALB-03020 → ACA-04010 → ACA-01040 → ACA-01020 → ACA-01010 → ACA-01060 → ACA-01110 → ACA-01090 → ACA-01100 → ACA-02040 → ACA-02050 → ACA-02010 → ACA-02020 → CAN-01008 → CAR-02050 → ACA-03025 → ACA-03026 → ACA-08041 → ACA-10040 |
| Diamante con chimenea | 23 | 15-sep → 5-ene | EST-02110 → ALB-01212 → ACA-01051 → ALB-03014 → ALB-03020 → ACA-04010 → ACA-01040 → ACA-01020 → ACA-01010 → ACA-01060 → ACA-01110 → ACA-01090 → ACA-01100 → ACA-02040 → ACA-02050 → ACA-02010 → ACA-02020 → CAN-01008 → CAR-02050 → ACA-03025 → ACA-03026 → ACA-08041 → ACA-10040 |
| Oro | 23 | 15-sep → 5-ene | EST-02110 → ALB-01212 → ACA-01051 → ALB-03014 → ALB-03020 → ACA-04010 → ACA-01040 → ACA-01020 → ACA-01010 → ACA-01060 → ACA-01110 → ACA-01090 → ACA-01100 → ACA-02040 → ACA-02050 → ACA-02010 → ACA-02020 → CAN-01001 → CAR-02050 → ACA-03025 → ACA-03026 → ACA-08050 → ACA-10040 |

## 6.5 La red que no se escribió

Un vínculo de Zafiro no se hereda si el derivado no tiene la partida o si la cumple al revés. El
motivo queda registrado fila por fila en `RED-NO-ESCRITA.csv`:

| Prototipo | Sin equivalente | No aplica | No se cumple | Total |
|---|---:|---:|---:|---:|
| Zafiro Plus | 9 | 4 | 1 | 14 |
| Diamante sin chimenea | 15 | 8 | 0 | 23 |
| Diamante con chimenea | 15 | 8 | 0 | 23 |
| Oro | 13 | 4 | 0 | 17 |

«Sin equivalente»: la sucesora o la predecesora no tiene gemelo en el prototipo (la cubierta de
cocina, la estufa, la campana, los marcos de cantera, la piedra laja…). «No aplica»: el orden ya no es
un vínculo (la pintura de muro y la de plafón son una sola partida de dos manos; Diamante tiene una
sola altura de losa y no hay losa de 3.00 que separar; los pretiles van sobre la losa de azotea).
**El estado «no se cumple» es uno solo en todo el libro: `P16` en Zafiro Plus, déficit de 10 días hábiles.**
Cerrarlo pide mover el plazo diez días hábiles (30 a 32 semanas) o relajar el vínculo, y cualquiera de
las dos lo decide el planeador por obra (D-437). Mientras no esté escrito, `vinculo_incumplido` no lo
ve; escrito, la alerta se enciende con holgura −10.

---

# 7. Lo que queda en manos del planeador

El sistema propone, el humano decide. Estas listas no se aplican solas.

## 7.1 Los doce supuestos que el planeador valida en cada programa de dos plantas

El texto completo de cada uno, con «qué pasa si se cambia», está en `SUPUESTOS-A-VALIDAR.csv`
(doce por prototipo). Los temas, y en qué prototipo difiere el texto del de Plus:

| Id | Tema (según el libro de Plus) | Cambia en |
|---|---|---|
| A1 | La ventana de las dos plantas | igual en los cuatro |
| A2 | Cuadrilla de la estructura de PA | Diamante con chimenea, Diamante sin chimenea, Oro |
| A3 | La losa de azotea, por panel (D-434, D-436) | Diamante con chimenea, Diamante sin chimenea, Oro |
| A4 | Pretiles de la azotea: después de la losa completa (D-434); la cadena que sigue, comprimida (D-436, D-437) | Diamante con chimenea, Diamante sin chimenea, Oro |
| A5 | Plafón y muro +3.00 de PA | igual en los cuatro |
| A6 | Instalaciones en muros de PA | igual en los cuatro |
| A7 | Las losas de planta baja: por altura | Diamante con chimenea, Diamante sin chimenea, Oro |
| A8 | Ojo de buey | Diamante con chimenea, Diamante sin chimenea, Oro |
| A9 | Acabados de PA | igual en los cuatro |
| A10 | Sin equivalente en Zafiro | Diamante con chimenea, Diamante sin chimenea, Oro |
| A11 | Calendario (D-428) | igual en los cuatro |
| A12 | La red | Diamante con chimenea, Diamante sin chimenea, Oro |

Dos de ellos merecen estar a la vista aquí. **La cuadrilla de la estructura de la planta alta (`A2`):**
la ventana de 10 días solo cabe si el muro y la cadena de la planta alta usan más cuadrilla que la
planta baja de Zafiro, y los castillos menos:

| Prototipo | Partida | Cantidad PA | Días PA | Por día PA | Por día PB de Zafiro | Veces |
|---|---|---:|---:|---:|---:|---:|
| Zafiro Plus | EST-02010 MURO TABIQUE DE 14 CM | 197 | 7 | 28.14 | 17.44 | 1.61 |
| Zafiro Plus | EST-02110 CASTILLO K-1 15X15 | 93.4 | 7 | 13.34 | 18.13 | 0.74 |
| Zafiro Plus | EST-02120 CASTILLO K-2 15X15 | 41.8 | 7 | 5.97 | 13.68 | 0.44 |
| Zafiro Plus | EST-02170 CASTILLO K-7 15X20 | 11.2 | 7 | 1.6 | 7.73 | 0.21 |
| Zafiro Plus | EST-02310 CADENA CE-1 15X20 | 78 | 2 | 39 | 24 | 1.62 |
| Diamante sin chimenea | EST-02010 MURO TABIQUE DE 14 CM | 211 | 7 | 30.14 | 17.44 | 1.73 |
| Diamante sin chimenea | EST-02110 CASTILLO K-1 15X15 | 79.8 | 7 | 11.4 | 18.13 | 0.63 |
| Diamante sin chimenea | EST-02120 CASTILLO K-2 15X15 | 12 | 7 | 1.71 | 13.68 | 0.13 |
| Diamante sin chimenea | EST-02170 CASTILLO K-7 15X20 | 6 | 7 | 0.86 | 7.73 | 0.11 |
| Diamante sin chimenea | EST-02310 CADENA CE-1 15X20 | 42 | 2 | 21 | 24 | 0.88 |
| Diamante sin chimenea | EST-02320 CADENA CE-2 15X25 | 3 | 2 | 1.5 | 24 | 0.06 |
| Diamante con chimenea | EST-02010 MURO TABIQUE DE 14 CM | 211 | 7 | 30.14 | 17.44 | 1.73 |
| Diamante con chimenea | EST-02110 CASTILLO K-1 15X15 | 79.8 | 7 | 11.4 | 18.13 | 0.63 |
| Diamante con chimenea | EST-02120 CASTILLO K-2 15X15 | 12 | 7 | 1.71 | 13.68 | 0.13 |
| Diamante con chimenea | EST-02170 CASTILLO K-7 15X20 | 6 | 7 | 0.86 | 7.73 | 0.11 |
| Diamante con chimenea | EST-02310 CADENA CE-1 15X20 | 42 | 2 | 21 | 24 | 0.88 |
| Diamante con chimenea | EST-02320 CADENA CE-2 15X25 | 3 | 2 | 1.5 | 24 | 0.06 |
| Oro | EST-02010 MURO TABIQUE DE 14 CM | 246.42 | 7 | 35.2 | 17.44 | 2.02 |
| Oro | EST-02110 CASTILLO K-1 15X15 | 33.6 | 7 | 4.8 | 18.13 | 0.26 |
| Oro | EST-02120 CASTILLO K-2 15X15 | 84 | 7 | 12 | 13.68 | 0.88 |
| Oro | EST-02130 CASTILLO K-3 15X30 | 21 | 7 | 3 | 4 | 0.75 |
| Oro | EST-02160 CASTILLO K-6 15X15 | 14.4 | 7 | 2.06 | 13.68 | 0.15 |
| Oro | EST-02170 CASTILLO K-7 15X20 | 16.2 | 7 | 2.31 | 7.73 | 0.3 |
| Oro | EST-02310 CADENA CE-1 15X20 | 101.61 | 2 | 50.8 | 24 | 2.12 |
| Oro | EST-02320 CADENA CE-2 15X25 | 7.3 | 2 | 3.65 | 24 | 0.15 |

**El colado de la losa de azotea (`A3`):** cada losa cuela en 3 días y se descimbra 8 días hábiles
después; la base sigue el patrón de la losa de 4.20 de Zafiro porque no hay una losa de azotea en
Zafiro con qué compararla (D-434, D-436).

## 7.2 Quién pide más cuadrilla

Una partida con la misma ventana que su gemela de Zafiro y más cantidad sube su cantidad por día: la
consecuencia directa de que los metros extra no suman días (§5). Son 59 partidas en los cuatro de dos
plantas (`PIDEN-MAS-CUADRILLA.csv`); las más altas:

| Prototipo | Partidas | Las tres más altas (veces la cantidad por día de su gemela de Zafiro) |
|---|---:|---|
| Zafiro Plus | 7 | ACA-08060 LIMPIEZA ENTINTADO Y  SELLADO DURMIENTE ×4.4; ACA-01071 BOQUILLA FINA EN FACHADA ×3.0; ACA-01052 BOQUILLA EN FACHADA ×3.0 |
| Diamante sin chimenea | 19 | ACA-01071 BOQUILLA FINA EN FACHADA ×9.8; ALB-01012 REPELLADO MURO +3.00 ×6.2; EST-10012 K1 - 1.50 ACERO ×6.0 |
| Diamante con chimenea | 18 | ACA-01071 BOQUILLA FINA EXTERIOR ×9.8; ALB-01012 REPELLADO MURO +3.00 ×6.2; EST-10012 K1 - 1.50 ACERO ×6.0 |
| Oro | 15 | ACA-08060 LIMPIEZA ENTINTADO Y  SELLADO DURMIENTE ×5.3; EST-02130 CASTILLO K-3 15X30 ×5.0; ACA-20020 FINAS EN FACHADA +3.00 ×4.1 |

Es la parte con menos dato fuerte: el planeador corrige las que no le parezcan. La alerta por
ventana de trabajo (D-449) revisa esos casos de otra manera —17 ventanas piden al menos el doble de
cuadrillas de su referencia y al menos una más; 53 líneas sin rendimiento emparejado tienen el doble
o más de su gemela— y sus listas siguen siendo del planeador (`CONOCIMIENTO.md` §11.14).

## 7.3 Los 15 vínculos de Zafiro que no se cumplen

Zafiro es el original y no se toca (D-444): la lista pasa de «pendiente de aplicar» a **registro**. La
lectura es la de D-443 (el bloque sin la sucesora): 10 `FS`, 2 `SS` y 3 `SF`; leyendo el bloque completo
son 18 (D-442). La propuesta del sistema para cada uno no se aplica; la última columna dice qué pasa con
él al cargar el programa (§4.5):

| Sucesora (fila) | Predecesora (fila) | Vínculo | Holgura | Propuesta del sistema (no se aplica, D-444) | Al cargar |
|---|---|---|---:|---|---|
| EST-03020 ZAPATA Z-1 DE 60X60X20 CM (407) | OBE-02020 JARDINERA PÓRFIDO EN LAJA (237) | SF | -6 | Anotar (SF, B-81) · Media | carga y avisa |
| IEC-01070 MURETE INSTALACIONES ACCESORIOS (247) | OBE-02030 ZOCLO DE PÓRFIDO LAJA 10-15 CM (240) | SF+2 | -5 | Anotar (SF, B-81) · Media | carga y avisa |
| IEC-01070 MURETE INSTALACIONES ACCESORIOS (247) | OBE-02020 JARDINERA PÓRFIDO EN LAJA (237) | SF | -6 | Anotar (SF, B-81) · Media | carga y avisa |
| ALB-01010 REPELLADO MURO 3.00 (147) | ALB-01012 REPELLADO MURO +3.00 (148) | FS-1 | -8 | Descartar · Media | carga y avisa |
| BAP-01100 CADENA CD-1 DE 15X20 (183) | ICA-01030 DURMIENTE 20X20 (185) | FS | -5 | Descartar · Alta | no carga: cierra un ciclo |
| EST-01151 FIRME DE CONCRETO 10 CM NIVELADO Y COMPACTADO (335) | EST-01151 FIRME DE CONCRETO 10 CM NIVELADO Y COMPACTADO (335) | FS | -1 | Descartar · Alta | no carga: autovínculo |
| ACA-02041 JABONERA (198) | ACA-02070 ZOCLO BRUNEI BEIGE 60X60 (ÁREAS COMUNES) (196) | SS+1 | -16 | Invertir · Baja | carga y avisa |
| ACA-05010 CHAPEO DE PIEDRA (184) | ACA-20020 FINAS EN FACHADA +3.00 (182) | FS | -16 | Invertir · Baja | carga y avisa |
| ACA-30021 PINTURA PLAFOND 1ER MANO (375) | ACA-30012 PINTURA MURO INTERIOR 2DA MANO (373) | FS | -20 | Invertir · Baja | carga y avisa |
| OBE-02012 BOQUILLA EN PÓRFIDO (239) | OBE-02020 JARDINERA PÓRFIDO EN LAJA (237) | SS+2 | -6 | Invertir · Baja | carga y avisa |
| ACA-02510 PISO DOVER BERKSHIRE RED (ASADOR) (200) | ECO-00043 ESTRUCTURA / ACABADOS (334) | FS | -14 | Reasignar a hermanas · Media | carga y avisa |
| ACA-30011 PINTURA MURO INTERIOR 1ER MANO (372) | API-01010 PINTURA PB (370) | FS | -24 | Reasignar a hermanas · Media | no carga: cierra un ciclo |
| ACA-30020 LIJADO Y SELLADO DE PLAFOND (374) | API-01010 PINTURA PB (370) | FS | -24 | Reasignar a hermanas · Media | no carga: cierra un ciclo |
| BAP-01010 MURO SILLAR 20 CM (364) | ECO-00046 ESTRUCTURA BP (362) | FS | -4 | Reasignar a hermanas · Media | no carga: cierra un ciclo |
| OBE-01012 FIRME PARA CISTERNA (228) | OBE-01010 ENCOFRADO DE CISTERNA 3000 LTS (226) | FS | -7 | Reasignar a hermanas · Media | no carga: cierra un ciclo |

Siete de los 18 tienen como causa común que la predecesora es un bloque que contiene a su sucesora;
con la lectura de D-443 esa forma no se rechaza. De los 15, **seis no se pueden cargar** (el autovínculo
`EST-01151` y cinco ciclos) y nueve cargan y avisan con `vinculo_incumplido`.

## 7.4 Los ocho `SF`

El `SF` entra al enum como `inicio_fin` (B-81, D-445). Cinco de los ocho se cumplen leídos tal como
están, todos con holgura 0 —las gualdras, que terminan la víspera de que empiece el resto de su
losa—; los tres que no, se cumplen todos al revés. Rubí y Jade heredan el de su gualdra (D-460).

| Prototipo | Sucesora | Predecesora | Desfase | Holgura como SF | Se cumple | Al revés |
|---|---|---|---:|---:|---|---|
| Zafiro | CAR-01011 GUALDRA 6X12X8 | EST-00010 LOSA ZAFIRO 3.00 | 0 | 0 | Sí | Sí |
| Zafiro | IEC-01070 MURETE INSTALACIONES ACCESORIOS | OBE-02030 ZOCLO DE PÓRFIDO LAJA 10-15 CM | 2 | -5 | No | Sí |
| Zafiro | IEC-01070 MURETE INSTALACIONES ACCESORIOS | OBE-02020 JARDINERA PÓRFIDO EN LAJA | 0 | -6 | No | Sí |
| Zafiro | EST-03020 ZAPATA Z-1 DE 60X60X20 CM | OBE-02020 JARDINERA PÓRFIDO EN LAJA | 0 | -6 | No | Sí |
| Zafiro Plus | CAR-01015 GUALDRA 6X12X16 | EST-00180 LOSA ENTREPISO - 3.00 ZAFIRO PLUS | 0 | 0 | Sí | Sí |
| Diamante sin chimenea | CAR-01013 GUALDRA 6X12X8 | EST-00090 DIAMANTE (208 M2) | 0 | 0 | Sí | Sí |
| Diamante con chimenea | CAR-01013 GUALDRA 6X12X8 | EST-00090 DIAMANTE CON CHIMENEA (208 M2) | 0 | 0 | Sí | Sí |
| Oro | CAR-01010 GUALDRA 6X12X20 | EST-00110 LOSA ENTREPISO ORO | 0 | 0 | Sí | Sí |

## 7.5 La segunda ruta de cuadrilla

Entre el 3-oct y el 3-nov hay otra cadena igual de ajustada que la espina, pero de **cuadrilla y no de
física**: cableado → barda → instalaciones del asador y pergolado de cochera → arranque del 3-nov.
No la comparten todos los prototipos y no se escribe (D-444): el recurso se captura a mano, con
`origen = recurso`.

| Eslabón | Predecesora → sucesora | Vínculo | Prototipos donde se cumple | Por qué (origen = recurso) |
|---|---|---|---|---|
| R1 | CABLEADO ELÉCTRICO → ESTRUCTURA BP | FS | 4 de 7 | Misma cuadrilla: la barda arranca el día hábil siguiente al cableado |
| R2 | ESTRUCTURA BP → INSTALACIONES | FS | 2 de 7 | Misma cuadrilla: las instalaciones del asador arrancan el día hábil siguiente a la barda |
| R3 | ESTRUCTURA BP → ESTRUCTURA / ACABADO | FS | 7 de 7 | Misma cuadrilla: el pergolado de cochera arranca el día hábil siguiente a la barda |

Lo que arranca justo después de que termina esa ruta está en `SEGUNDA-RUTA-LO-QUE-SIGUE.csv`.

---

# 8. El Gantt: pantalla y reglas (B-95 cierra)

`vista_gantt` entrega los datos y `frontend/gantt/` los dibuja y los edita: una página sola, sin servidor, que
`pagina_gantt` arma con los datos de un programa. Las tres preguntas que dejaba B-95 las contestó el usuario
(D-463), y esto es lo que quedó:

**1. El rojo es la cadena de relevos** de las fechas vigentes, la que el usuario validó en D-426 y la que lee
el planeador. Se recalcula sola con cada edición, y cuando el programa se reprograma es la ruta crítica de lo
reprogramado. La ruta crítica de la red queda como lectura de diagnóstico: la pantalla la ofrece mientras no
hay ediciones y no la recalcula, porque con la red mínima apunta a cadenas que el plan no sigue (§4.4).

**2. Un árbol que se pliega, sin perder detalle.** Capítulo, frente, etapa, Nivel 3 y partida, con las barras de
resumen que abarcan lo que contienen. Se abre con los frentes y las etapas a la vista (64 filas en Plus) y el
detalle a un clic, o con «Todo el detalle» (493). Las flechas de lo plegado se suman al bloque que se ve, sin
perder ninguna, y una partida movida se marca aunque su bloque esté plegado. Un frente se puede aislar desde la
leyenda.

**3. Autónomo, pero editable.** El sistema dibuja y propone; el planeador decide:
- Los vínculos se dibujan solos, pero no todos a la vez: por defecto se ven **los que importan** —los de la
  cadena en rojo, los de la partida o el bloque que se toca y los incumplidos, punteados—, y todos están a un
  clic. Nadie configura nada para que la pantalla se lea.
- Todo lo que se ve se edita: la duración, el arranque y cada vínculo de una partida (tipo, espera, quitarlo), y
  se agrega una predecesora eligiéndola en el propio Gantt, que si es un bloque sale de la partida que fija la
  fecha. Estructura es de Control de obra y fechas, del Residente (§4.6).
- **Nada se aplica a ciegas**: cada edición reprograma por empuje mínimo y la pantalla muestra, en tres tarjetas,
  el cierre (antes y después), cuántas partidas se mueven y si la cadena cambia. Una edición que no se puede
  aplicar se dice con su motivo y no se aplica. Las ediciones se ven como fichas que se quitan una por una.
- **Propuesta sin confirmar:** el vínculo que alguien agrega o cambia lleva el `origen` que declare
  (`PRECEDENCIA.origen`: técnica, recurso o decisión) y, si no declara, `decision`, que es la de menor
  confianza y la que se revisa primero.

El resto de las reglas viene de la imagen de D-432: color por frente (los seis niveles constructivos con su
color y los nueve paquetes contratados terminados en gris; las etapas, 49 en Plus, no se distinguen por color),
anclaje de la flecha según el tipo (`FS` del fin al inicio, `SS` de inicio a inicio, `FF` de fin a fin, `SF` del
inicio al fin), fines de semana, feriados y ventana de la planta alta marcados, la barra de antes en trazo
punteado cuando una edición mueve una partida, y el horizonte del programa más largo (D-449).

**Lo que la pantalla todavía no hace**, y es de la capa de aplicación: guardar. Es una simulación; las
ediciones reales las hace Control de obra y el Residente sobre la base de datos, con la misma
`reprogramar`.

---

# 9. Lo que sigue abierto

| Qué | Por qué sigue abierto |
|---|---|
| La API y la pantalla conectadas a lo guardado | La persistencia existe (§4.7); falta la superficie FastAPI (D-54) y que la pantalla deje de simular y llame a `proponer` y `aplicar` |
| Colgar el programa de `NODO`, `PRESUPUESTO` y `CALENDARIO_OBRA` | Esas tablas aún no existen (B-03); entonces `programa_fila` se vuelve `ACTIVIDAD` y `TRAMO` |
| `origen` del vínculo que se edita | Implementado como se propuso (lo que declare quien edita y, si no, `decision`), sin confirmar |
| `P16` en Zafiro Plus | Pide mover el plazo a 32 semanas o relajar el vínculo; lo decide el planeador por obra (§6.5) |
| Las listas del planeador | Los 12 supuestos de cada programa, los 15 de Zafiro, las 59 que piden más cuadrilla, las 17 ventanas, las 53 líneas sin rendimiento, los emparejamientos por rol |
| La segunda ruta de cuadrilla | Borrador; se captura a mano con `origen = recurso` (§7.5) |
| Hidrosanitarias (B-91) | Se ejecuta cuando se crea una versión nueva de la plantilla; los programas no cambian |
| Reasignar parte de la cantidad de una partida a otro contratista | Propuesta sin confirmar (`CONOCIMIENTO.md` §11.14) |
| Los emparejamientos por rol de Rubí y Jade (28 y 18, D-449) | Sus filas no están en `EMPAREJAMIENTOS-POR-ROL.csv` ni llevan `regla`: su detalle vivía en libros que no se conservaron; se rehace con el planeador cuando revise esos dos programas |

---

# 10. Las decisiones que construyeron esto

| Tema | Decisiones |
|---|---|
| El diseño del CPM | D-90, D-99 a D-104, D-259, D-262, D-263, D-327 |
| El plan manual de Zafiro y sus columnas | D-389 a D-392, D-396, D-409, D-411, D-412 |
| Rubí, Jade y las reglas de herencia | D-414 a D-423 |
| La red | D-424 a D-426, D-442 a D-445 |
| Los cuatro de dos plantas | D-427 a D-431, D-433 a D-437 |
| Duraciones, cuadrillas y ritmo | D-438 a D-441, D-446, D-449 |
| Calendario y plazo | D-417, D-428, D-447 |
| Retraso y alertas | D-456 a D-459 |
| Pendientes de B-86 | D-444, D-445, D-460 |
| **El motor, los datos en el repositorio y esta consolidación** | **D-461** |
| **El cargador, la cadena de relevos calculada y el Gantt como dato** | **D-462** |
| **Reprogramar por empuje mínimo, el árbol plegable y la edición en pantalla (B-95 cierra)** | **D-463** |
| **Guardar las ediciones: puerto, servicio, Postgres y origen del vínculo** | **D-464** |
