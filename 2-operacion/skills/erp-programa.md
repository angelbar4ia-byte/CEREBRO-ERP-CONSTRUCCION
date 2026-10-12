---
name: erp-programa
description: El programa de obra en el ERP de construcción — actividades y vínculos (FS, SS, FF, SF) entre partidas y bloques, el CPM, el calendario y el plazo, reprogramar por empuje mínimo, guardar las ediciones en una bitácora y el Gantt. Usar al implementar o cambiar el motor del CPM, el cargador de programas, la reprogramación, la bitácora de ediciones, la API o la pantalla del Gantt, al medir si un vínculo se cumple, al contar un plazo o redondear una duración, al colgar un programa del presupuesto, o al programar un prototipo nuevo a partir de Zafiro. NO cubre el costo de los conceptos ni la carga de OPUS (ver `erp-importacion`), ni el trazo sobre el plano (ver `erp-cuantificador`).
---

```
órgano:     vía mielinizada — programa
capa:       II — Operación
pregunta:   ¿cómo se calcula, se edita y se guarda el programa sin inventar un orden que la obra no tiene?
tiempo:     se hace así
corte:      2026-10-12
compilado:  `PROGRAMA-CPM.md` §3 a §8 · `MODELO.md` §5c · `MODELO.md` §5a (las alertas del programa) y lo que D-461 a D-474 construyeron — no se escribe a mano
```

> **Satélite.** Carga el skill base `erp-construccion` primero.

---

## 0. Qué es, y dónde vive cada pieza

**El programa es la secuencia y el tiempo de una obra**: qué partidas hay, cuánto dura cada una, qué espera a qué y
cuándo cierra todo. Se calcula con un CPM, lo edita un planeador y el sistema dice qué costaría cada cambio antes de
que alguien decida.

| Pieza | Dónde |
|---|---|
| El CPM: vínculos, holguras, ruta crítica, calendario, retraso | `backend/core/motor_cpm.py` — funciones puras, sin base de datos |
| Leer un programa, la cadena de relevos, reprogramar, el Gantt como dato | `backend/core/programa.py` |
| Guardar lo que se edita | `servicio_programa.py` · `memoria_programa.py` · `infra/postgres_programa.py` (mismo contrato, dos adaptadores) |
| Colgar el programa del presupuesto | `backend/core/colgado.py` |
| La API y el cliente de la pantalla | `backend/api/` · `frontend/gantt/cliente_programa.js` (generado del spec, no se edita) |
| La pantalla | `frontend/gantt/` — con su propio motor de reprogramación en JavaScript |
| Los siete programas, su red y las listas del planeador | `1-mundo/programas/` (trece CSV). **No se regeneran desde Excel**: si un programa cambia, cambia ahí, con una decisión nueva |

**Lo que el motor calcula es caché, nunca fuente de verdad**: las fechas tempranas y tardías, la holgura y
`ACTIVIDAD.es_ruta_critica` se pueden tirar y recalcular. Lo que se guarda es lo que alguien decidió.

---

## 1. El vínculo, y cómo se sabe si se cumple

Cuatro tipos, con los nombres del enum del modelo: `fin_inicio` (FS), `inicio_inicio` (SS), `fin_fin` (FF) e
`inicio_fin` (SF). El desfase se cuenta en días hábiles y, si es negativo, traslapa. **El formato de origen lo guarda en
horas y la jornada es de 8**: ÷ 8 al leerlo.

```
Holgura de un vínculo (negativa = no se cumple). abre(x) = inicio del primer día hábil de x;
cierra(x) = fin de su último día. Un bloque abre con su primera partida y cierra con la última.
  fin_inicio     abre(sucesora)   − (cierra(predecesora) + desfase)   con fechas: bc(fin_p, ini_s) − 1 − desfase
  inicio_inicio  abre(sucesora)   − (abre(predecesora)   + desfase)   con fechas: bc(ini_p, ini_s)     − desfase
  fin_fin        cierra(sucesora) − (cierra(predecesora) + desfase)   con fechas: bc(fin_p, fin_s)     − desfase
  inicio_fin     cierra(sucesora) − (abre(predecesora)   + desfase)   con fechas: bc(ini_p, fin_s) + 1 − desfase
  (bc = días hábiles entre dos fechas del calendario de la obra)
```

- **Los dos que comparan un cierre contra una apertura llevan una corrección de un día** en fechas: `− 1` en
  `fin_inicio`, `+ 1` en `inicio_fin`. Los que comparan igual con igual no llevan ninguna. Medir `inicio_fin` sin ella
  cuenta un vínculo de menos.
- **Un vínculo que las fechas contradicen se carga y se avisa**; no se rechaza. Es lo que dispara
  `ALERTA(tipo=vinculo_incumplido)`, sin umbral, porque el plan hecho a mano no pasó por ningún CPM. Quién corrige es
  quien programa.
- Los 832 vínculos de los siete programas son 680 `FS`, 91 `SS`, 53 `FF` y 8 `SF`.

### El bloque como predecesora

- **Un bloque solo puede ser predecesora; la sucesora siempre es una partida.** `fin_inicio` y `fin_fin` leen el máximo
  de los fines de sus partidas; `inicio_inicio` e `inicio_fin`, el mínimo de los inicios. La ruta sigue por la partida
  que de verdad fija esa fecha, no por el bloque.
- **Si la predecesora es el bloque de su propia sucesora, se lee sin ella**: «después de lo demás del grupo». Son 39 de
  los 832 y 35 se cumplen. Rechazarlos (como hizo D-442) era un error, no cautela.
- **Un vínculo cuya intención es un hecho físico concreto cita la partida, no el bloque.** La ventana de un bloque es lo
  que el catálogo mete adentro, y a veces mete de más (el ojo de buey está en la obra gris de un prototipo y dentro de la
  estructura de planta baja en otros).
- **El motor no ordena topológicamente cuando hay bloques**: itera hasta que nada se mueve. Ordenar con aristas desde
  todos los descendientes del bloque inventa ciclos que no existen (la gualdra va antes de su losa y el `SF` de la
  gualdra cita el grupo de esa misma losa). Solo las aristas directas partida → partida pueden formar un ciclo real.

---

## 2. Qué rechaza el cargador y qué no

El programa guarda el `oid` de cada fila, **nunca el número de fila**: la clave se repite dentro de un mismo programa y
las filas se corren. Se rechazan, sin detener la carga y diciendo por qué:

| Motivo | Cuándo |
|---|---|
| `autovinculo` | La partida cita su propia fila |
| `cierra_un_ciclo` | El vínculo forma parte de un ciclo entre partidas, o a través de un bloque cuyo extremo espera a la sucesora. De cada ciclo se rechaza el que las fechas del propio plan ya contradicen; si ninguno, el último escrito |
| `sucesora_bloque` | La celda de vínculos está en una fila de bloque |
| `formato` · `predecesora_desconocida` · `predecesora_sin_partidas` | El token no se lee, cita una fila que no existe, o un bloque sin partidas |

Con los siete programas reales solo Zafiro rechaza algo: **6 de sus 124 vínculos** (118 cargan) —el autovínculo de
`EST-01151` y cinco ciclos—. Los 15 que no se cumplen cargan y avisan. **El programa original de Zafiro no se toca**
(D-444): se anota y lo decide el planeador.

---

## 3. Lo que el CPM entrega, y lo que no

- **Resultado por actividad:** inicio y fin tempranos y tardíos, holgura total, ruta crítica y fechas. La ruta crítica
  son las partidas con holgura ≤ 0; los bloques derivan su holgura de sus partidas y no entran en la lista.
- Los hitos duran cero. El arranque se corre al primer día hábil. El ancla contractual solo retrasa, nunca adelanta.
- **Un plazo menor al fin temprano da holgura negativa, no error.**
- **`Fraction` hasta el final**: las fechas se calculan al devolver el resultado, para que el medio día de un paso
  fraccionario no pierda exactitud.
- **No nivela recursos ni respeta `FRENTE_TOPE_CUADRILLA`**: el tope se vigila con una alerta, no se aplica en el
  cálculo. **No parte una actividad en tramos con pausa**: eso es de la capa de aplicación.
- **El CPM más temprano no reproduce el cierre del plan hecho a mano, y está bien.** Con la red mínima de hoy,
  Rubí y Jade lo reproducen (139 días hábiles); las dos versiones de Diamante y Oro dan 139 contra los 149 del plan, y
  Zafiro Plus da 81 porque le falta `P16`. Las dos semanas de la planta alta son una decisión de cuadrilla del
  planeador, no una precedencia. **No se arregla agregando vínculos hasta que cuadre.**

---

## 4. La duración, el calendario y el plazo

```
días teóricos        = cantidad ÷ (rendimiento × cuadrillas)        fraccionarios, sin redondear
duración programada  = acomodar(días teóricos, paso_dias, sentido_redondeo)     nunca menos de un paso
cuadrillas efectivas = cantidad ÷ (rendimiento × duración programada)
esfuerzo             = duración programada × cuadrillas efectivas × 8 = cantidad ÷ rendimiento × 8
```

- **El redondeo es del calendario, no de la fórmula ni de la actividad**: `paso_dias` y `sentido_redondeo` son campos de
  `CALENDARIO_OBRA`, editables. Por defecto paso 1 y sentido cercano (el medio va hacia arriba; un múltiplo exacto no se
  mueve; en arriba y abajo un excedente menor a 0.01 día no sube un paso: 7.003 se programa en 7).
- **El redondeo mueve las cuadrillas, no el esfuerzo.** Calculada y redondeada paso por paso, la ruta de 28 pasos de
  Zafiro gana 14.6 días hábiles con `arriba`, pierde 12.6 con `abajo` y gana 0.8 con `cercano`. El sistema muestra las cuadrillas efectivas
  junto a las pedidas y las compara con el tope; decide el planeador.
- **Los metros extra no suman días**: una partida con más cantidad que su gemela conserva la ventana y sube la
  cantidad por día. El costo es más cuadrilla.
- **El último día absorbe el residuo** del reparto diario (D-433). La cantidad por día no se guarda: es la cantidad
  entre los días hábiles del tramo en el calendario vigente.
- **El calendario es una opción del sistema.** El ejercicio de los siete programas va de lunes a viernes sin el 25-dic
  ni el 1-ene, y se trabaja el 16-sep y el 17-nov. El sistema ofrece una plantilla de feriados y **nunca la aplica sola**:
  un calendario nuevo sale sin ningún feriado.
- **El plazo lo fija el número de plantas, no los metros cuadrados**: 28 semanas una planta, 30 dos. Se cuenta en días
  hábiles por defecto (límite = semanas × días laborables por semana: 140 y 150) y el calendario mueve la fecha de
  cierre, no el trabajo; en semanas de calendario cada feriado se come un día del plazo. El programa muestra las dos
  cuentas y `plazo_medido_en` decide cuál dispara `plazo_excedido`. Los siete cierran un día hábil antes del límite.

---

## 5. Reprogramar: el empuje mínimo

Cinco ediciones, repartidas en los dos permisos de `MODELO.md` §5b:

| Edición | Qué cambia | Permiso |
|---|---|---|
| `CambiarDuracion` | La partida dura esos días hábiles | `editar_estructura_programa` (Control de obra) |
| `AgregarVinculo` · `QuitarVinculo` · `CambiarVinculo` | Un vínculo de la red | `editar_estructura_programa` |
| `FijarInicio` | La partida no arranca antes de esa fecha | `editar_fechas_programa` (Residente) |

**Cada partida conserva su arranque del plan y solo se corre lo que una edición obliga, y solo hacia adelante.** De ahí
sale la regla, no un detalle:

- Sin ediciones, un plan que cumple todos sus vínculos queda **idéntico** (0 partidas movidas en los seis programas
  limpios). Es la prueba de que el empuje no inventa nada.
- **Quitar un vínculo o acortar una duración nunca adelanta nada.** Adelantar es una decisión y se toma fijando un
  arranque. El modo `temprano` suelta el plan y calcula el CPM más temprano de la red: es un diagnóstico, no un modo
  de trabajo.
- Un plan que no cumple sus vínculos se corre hasta cumplirlos. Si Zafiro obedeciera sus 118 vínculos cargados se
  moverían 47 partidas y cerraría el 7-ene-2026, 12 días hábiles después: es lo que costaría que la red mandara sobre
  el plan manual.

**El impacto se devuelve con el programa nuevo, antes de decidir:** las partidas movidas (cuántos días hábiles se corre
cada arranque y término), el cierre antes y después, la ruta antes y después, si cambia, y los vínculos que siguen sin
cumplirse. `ruta_cambia` avisa solo si cambian las actividades de la ruta; correr fechas no es noticia (D-100). Una
edición que no se puede aplicar vuelve con su motivo y no frena a las demás: `actividad_desconocida`,
`duracion_invalida`, `autovinculo`, `sucesora_no_es_partida`, `repetido`, `cierra_un_ciclo`, `vinculo_inexistente`.

Cifra de control: agregar `P16` a Zafiro Plus (`FS+1`) corre el cierre del 5 al 19-ene-2026, **10 días hábiles**, el
déficit que ya medía D-437.

---

## 6. Guardar: la bitácora, no las fechas

- **El programa vigente es `reprogramar(base, ediciones aplicadas)`.** El programa base (filas y vínculos con que se
  importó) no cambia. Así nada queda a medias, deshacer es repetir la cuenta sin esa edición y cualquiera reconstruye
  cómo se llegó a las fechas de hoy.
- **El candado es una versión.** Cada edición o reversión sube `programa.version`; quien guarda dice cuál vio
  (`esperaba`) y, si ya es otra, `Conflicto` (409), sin pisar. La versión se lee antes que las ediciones.
- **Los permisos salen de `ROL_FUNCION` y se leen en cada acción**, no de una constante. Quien tiene más de un rol puede
  lo que alguno pueda y queda registrado con el primero, en orden alfabético, que tiene la función. Deshacer pide el
  permiso de la edición que se deshace; si otras dependen de ella, dice cuáles y no toca nada.
- **Cada edición guarda** quién y con qué rol, la edición tal como se pidió (citando `oid`), lo que el sistema mostró al
  decidir y, si es un vínculo, su `origen` (`tecnica`, `recurso` o `decision`). Sin declarar, nace como `decision`, el de
  menor confianza, que es el que se revisa primero. *(Propuesta sin confirmar, implementada.)*
- **En Postgres la bitácora ni se borra ni se reescribe**: solo deja pasar el paso de `aplicada` a `revertida`. Una
  edición no queda sin autor, un vínculo editado no queda sin origen y un vínculo no cita una fila que no existe.
- **Un programa con versión nueva se cierra a ediciones**: proponer, aplicar y deshacer responden 409 `reemplazado`.
  Se mira, no se edita. Las partidas del archivo nuevo se reconocen **por `oid` y por nada más**; las ediciones decididas
  pasan si siguen teniendo sentido y las que no, se dicen con su motivo.
- **Colgar el programa del presupuesto** pone en cada fila el bloque o el renglón al que se refiere. Un bloque se casa
  por su ruta natural `clave#n` y una partida por su bloque y su clave, la n-ésima vez que se nombra contra la n-ésima
  línea con ese concepto. **Nada se alinea por número de fila.** Lo que no casa se dice de los dos lados; un enlace
  puesto no se mueve; con menos de la mitad de los conceptos casados pide confirmar.

---

## 7. El Gantt

- **El rojo es la cadena de relevos de las fechas vigentes** (la cadena de partidas con holgura 0 sobre el plan, que el
  usuario validó), no la ruta crítica de la red, que con la red mínima apunta a cadenas que el plan no sigue. Si se
  reprograma, es la ruta crítica de lo reprogramado.
- **Se ven los vínculos que importan** (los de la cadena, los de lo que se toca y los incumplidos, punteados) y todos
  están a un clic. Un árbol que se pliega: las flechas de lo plegado se suman al bloque visible sin perder ninguna.
- **Nada se aplica a ciegas**: cada edición muestra el cierre antes y después, cuántas partidas se mueven y si la
  cadena cambia. Lo que se decide queda **por guardar** hasta que se presiona «Guardar», que manda las ediciones una
  por una con la versión que se vio; si hubo un 409, trae lo de hoy, revalida y pide revisar el impacto.
- **La pantalla reprograma sin ir al servidor** y por eso tiene su propio motor (`motor_gantt.js`). Una prueba corre el
  de Python y el de JavaScript con las mismas ediciones sobre Zafiro Plus y exige el mismo cierre, las mismas partidas
  movidas, la misma ruta y los mismos rechazos. **Cambiar uno sin el otro rompe esa prueba.**
- **Lo que la pantalla puede hacer lo dice la API** (`GET /yo`, desde `ROL_FUNCION`); no repite la tabla de permisos.
  El token llega en el fragmento de la dirección, no en la consulta. El texto de quien sube un programa se trata como
  ajeno: título escapado, datos como JSON sin `<`.

---

## 8. Programar un prototipo derivado desde Zafiro

Los seis derivados parten de Zafiro, el único programa terminado por el residente. La regla con que se armó cada
partida está en la columna `regla` de `PROGRAMAS-PROTOTIPOS.csv` y con quién se emparejó, en `gemelo_zafiro_fila`.

- **Gemelo por clave** (lo más común), por clave en otro bloque, por rol (cada par con su porqué, y lo corrige el
  planeador), por la ventana de su bloque, por nivel preestablecido (cancelería, carpintería, impermeabilización y
  cubiertas: duración fija) y por reglas propias de losas y planta alta.
- **Cada duración tiene origen.** De las 2,130 duraciones de los derivados, 1,520 se heredan de su gemela de Zafiro
  (71.4 %), 132 son propias (6.2 %) y 478 no tienen referencia (22.4 %). **La referencia es una llave explícita, no se
  deduce por clave**, y quien edita una duración pasa a ser la referencia de su alcance.
- **Un vínculo de Zafiro no se hereda** si el derivado no tiene la partida (sin equivalente), si el orden ya no es un
  vínculo (no aplica) o si se cumple al revés (no se cumple). El motivo queda fila por fila en `RED-NO-ESCRITA.csv`.
- **La red tiene cuatro familias con dueño**: `V` (los 52 de Zafiro que se cumplen), `E` (la red mínima entre bloques),
  `P` (la red mínima bajada a las partidas) y `PX` (los eslabones propios de dos plantas). El identificador dice de
  dónde viene un vínculo.

---

## 9. Lo que decide el planeador, no el sistema

*El sistema propone, el humano decide.* Estas listas no se aplican solas: los doce supuestos de cada programa de dos
plantas, los 15 vínculos de Zafiro que no se cumplen, los 8 `SF`, las 59 partidas que piden más cuadrilla que su
gemela, los emparejamientos por rol, la segunda ruta de cuadrilla y **`P16` en Zafiro Plus**, el único vínculo de toda
la red cuyo estado es «no se cumple» (30 a 32 semanas, o relajar el vínculo: se decide por obra).

---

## 10. Cifras con que se comprueba cualquier cambio

Si un número de esta lista cambia, una prueba tiene que cambiar con él (`backend/core/tests/test_motor_cpm.py`):

| Qué | Cifra |
|---|---|
| Vínculos de los siete programas | 832 (680 FS · 91 SS · 53 FF · 8 SF) |
| Cierre | 139 días hábiles una planta (jueves 18-dic) · 149 dos plantas (lunes 5-ene) |
| Zafiro | 124 vínculos, 118 cargan, 15 incumplidos (10 FS · 2 SS · 3 SF); 18 si el bloque se lee completo |
| Los otros seis | 0 vínculos incumplidos |
| `SF` | 8, de los que 5 se cumplen con holgura 0 (las gualdras) |
| Herencia de duraciones | 1,520 · 132 · 478 |
| Cadena de relevos de Zafiro | 28 pasos, cubre 138 de los 139 días hábiles |
| Programa colgado del presupuesto | 3,110 enlaces, uno por cada renglón de los siete presupuestos |

---

## 11. Los errores que este skill previene

1. Ordenar topológicamente con aristas desde todos los descendientes de un bloque — inventa ciclos que no existen.
2. Rechazar el vínculo cuya predecesora es el bloque de su propia sucesora — se lee sin ella.
3. Rechazar un vínculo porque las fechas lo contradicen — se carga y se avisa.
4. Medir `fin_inicio` o `inicio_fin` con fechas sin la corrección de un día.
5. Olvidar que el formato de origen guarda el desfase en horas.
6. Guardar las fechas del programa vigente — se guarda la bitácora de ediciones.
7. Citar una fila por su número — se cita por `oid`.
8. Adelantar partidas al quitar un vínculo o acortar una duración — adelantar es fijar un arranque.
9. Alinear el programa con el presupuesto por número de fila — por ruta natural y clave.
10. Redondear la fórmula de días teóricos, o redondear por actividad — el paso es del calendario.
11. Tomar el redondeo por un cambio de esfuerzo — mueve las cuadrillas, no las horas.
12. Sumar días por metros extra — suben las cuadrillas, no la duración.
13. Contar el plazo en semanas de calendario sin decirlo, o aplicar sola la plantilla de feriados.
14. Fijar el plazo por metros cuadrados — lo fija el número de plantas.
15. Llamar falla al CPM porque no reproduce el plan manual, y agregar vínculos hasta que cuadre.
16. Cerrar el «no se cumple» de `P16` moviendo fechas o plazo por cuenta propia — lo decide el planeador.
17. Tocar el programa original de Zafiro para que cumpla su red.
18. Dejar editar un programa que ya tiene versión nueva.
19. Guardar una edición sin la versión que vio quien decide, o sin que el candado se lea antes que las ediciones.
20. Reconocer partidas de una versión nueva por clave o por fila — por `oid`.
21. Poner en la pantalla una tabla de permisos — la API dice qué puede cada quien.
22. Pintar de rojo la ruta crítica de la red — el rojo es la cadena de relevos.
23. Deducir la referencia de una duración heredada por clave — es una llave explícita.
24. Cambiar el motor de Python sin el del navegador, o al revés.
25. Dibujar un texto que subió el usuario como si fuera HTML.
