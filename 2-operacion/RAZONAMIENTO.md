# RAZONAMIENTO

```
órgano:     corteza prefrontal — razonamiento en el momento
capa:       II — Operación
pregunta:   ¿cómo se responde una pregunta que el cerebro no tiene guardada?
tiempo:     se hace así
corte:      2026-10-12
verificado: 3 preguntas de prueba sobre ALAMO 18 · referencias a `CONOCIMIENTO.md` §11 y a `MODELO.md` §5f releídas el 2026-10-12 contra su destino (una estaba mal) · las cifras de §5 vienen de un archivo de comparación que no está en el repositorio y no se pudieron volver a sacar
```

> **`METODO.md` dice cómo se construyó y se audita el cerebro** — mirando hacia
> adentro, con tiempo por delante. **Esto dice cómo se responde, con el cerebro ya
> construido, una pregunta que alguien hace hoy** — mirando hacia afuera, en el
> momento. Si una regla explica cómo se verificó un hecho, es método. Si explica
> cómo contestar sin tener el hecho guardado, es esto.

---

## 1. Dos tipos de pregunta

| Tipo | Ejemplo | Dónde está la respuesta |
|---|---|---|
| **De método** — ¿cómo se calcula, por qué es así? | «¿Qué es Presupuesto Formado?» | Ya está en `CONOCIMIENTO.md` — se cita, no se recalcula |
| **De valor vigente** — ¿cuánto es, hoy? | «¿Cuánto llevamos pagado de destajo en cimentación?» | El cerebro **nunca** lo guarda — cambia cada corte. Hay que ir a calcularlo |

> **Cómo distinguirlas:** si la respuesta es igual hoy que en seis meses, es
> método. Si cambia con cada corte de obra, es valor vigente.

Confundir las dos produce dos fallas distintas: tratar una pregunta de método
como si tuviera un número (inventarlo), o tratar una de valor vigente como si el
cerebro la tuviera memorizada (contestar con un dato viejo sin decirlo).

## 2. Antes de dar un valor vigente: desambiguar el alcance

Toda pregunta operativa de obra esconde hasta cuatro decisiones que hay que
tomar **antes** de calcular, no después:

| Pregunta que hay que hacerse | Opciones | Dónde están definidas |
|---|---|---|
| ¿De qué alcance? | Toda la obra · un nivel · un concepto · una semana | `CONOCIMIENTO.md` §11.14 · §11.17 |
| ¿Contra qué referencia? | Presupuesto Base · Ingeniería · Pagado Real · Presupuesto Formado | `CONOCIMIENTO.md` §11.14 |
| ¿Real o teórico? | La matriz estándar del catálogo · lo que salió de almacén o se pagó | `CONOCIMIENTO.md` §11.9 · §11.16 |
| ¿Qué ventana de tiempo? | Acumulado del proyecto · un mes · una semana | `CONOCIMIENTO.md` §11.16 · §11.17 |

> Mismo principio que `METODO.md` §1.2 («comparar cosas del mismo alcance»),
> aplicado hacia adelante: ahí sirve para **auditar** una diferencia ya
> calculada; aquí, para no calcular mal desde el principio.

## 3. No elegir una interpretación en silencio

Ejemplo real, verificado sobre `ALAMO 18`: «¿cuál es el rendimiento del
cemento?» tiene al menos tres respuestas distintas y válidas — 35% consolidado
de toda la obra (que además resultó ser sustitución, no rendimiento,
`CONOCIMIENTO.md` §11.11), 0% en una orden específica de abril
(`CONOCIMIENTO.md` §11.16), y una tasa teórica de referencia usada en un corte
semanal (`CONOCIMIENTO.md` §11.17). Ninguna es «la» respuesta.

> Elegir una y contestar como si fuera la única es la misma falla que una
> propuesta sin evidencia (`METODO.md` §3.2) — aquí, **un número sin decir de
> qué alcance es una cifra disfrazada de certeza.**

**Regla:** cuando la pregunta admite más de una lectura razonable, se muestran
las alternativas encontradas, cada una con su alcance explícito — no se adivina
cuál quiso decir quien preguntó.

## 4. Dónde vive el valor vigente

El cerebro nunca guarda un valor vigente — lo dejaría desactualizado en el
próximo corte, el mismo riesgo que un `%` de avance declarado a mano en vez de
calculado (`CONOCIMIENTO.md` §4.1). El valor vive siempre en un artefacto
aparte.

**Hoy:** ese artefacto es un archivo de comparación construido con scripts ad
hoc, **fuera de este repositorio** — no es todavía parte del sistema. Si no
está disponible, se dice explícitamente que no se tiene el dato: no se
aproxima ni se inventa.

**Cuando exista el sistema real:** esto lo resuelve el módulo de
reportes/comparación — ya diseñado, `MODELO.md` §5f (B-71, D-334) —, no un
script aparte. Cuatro de las cinco columnas reusan tabla ya existente; la
quinta (Control de Cambio) solo necesitaba la forma de su JSON dentro de
`PROPUESTA`. Sigue habiendo un hueco, pero de dato: los subcontratos
necesitan su propio origen (`subcontratos.csv`, vacío — D-321), no diseño
nuevo.

## 5. Caso de prueba — las tres preguntas de ALAMO 18

Tres preguntas reales, usadas para probar si el cerebro razona o solo guarda
hechos sueltos. Igual que `PRUEBA-ALAMO-18.md` prueba el modelo, esto prueba
**cómo se responde con él**.

### 1 · ¿Cuál es el rendimiento del cemento?

Pregunta de valor vigente, con alcance ambiguo. Tres respuestas, ninguna sola
(§3 arriba): 35% consolidado (sustitución, no rendimiento), 0% en una orden de
abril de `EST-01060`, y la tasa teórica usada como referencia semanal para
`EST-02010`.

### 2 · ¿Cuánto falta por pagar de destajo en cimentación?

Pregunta de valor vigente. Depende de contra qué se compare — leído del
artefacto de comparación (§4), corte 2026-09-21, para `NIV-00001`:

| Contra | Cálculo | Resultado |
|---|---|---|
| Presupuesto Base | $78,677.50 − $80,030.50 | Ya se pagó $1,353.00 de más |
| Ingeniería | $87,517.50 − $80,030.50 | Faltan $7,487.00 |
| Presupuesto Formado | $87,875.28 − $80,030.50 | Faltan $7,844.78 |

Tres respuestas correctas y distintas — «cuánto falta» no significa nada sin
decir contra cuál de las tres.

> *Releído el 2026-10-12.* Las cifras son del corte 2026-09-21 y de un archivo que no está en
> el repo. La hoja de mano de obra que sí está (`1-mundo/fuentes/precio-real/PRECIO_REAL_ALAMO_18__2/Mano_de_Obra.csv`)
> suma $79,228.00 con ubicación `CIMENTACIÓN` y $79,728.00 con `HIDROSANITARIAS CIM`; ninguna
> es $80,030.50. Con lo que hay en el repo no se puede saber cómo se asignaba cada clave a su
> nivel, y por eso el número no se puede volver a sacar. Lo que sí se sostiene es la forma: tres
> referencias, tres respuestas.

### 3 · ¿Cuál es el Presupuesto Formado?

Mitad método, mitad valor. El método es fijo (`CONOCIMIENTO.md` §11.14); el
número, leído del artefacto de comparación en la misma fecha, tiene dos
alcances — no uno:

| Alcance | Presupuesto Formado |
|---|---|
| Destajo | $1,021,457.64 |
| Material | $1,439,761.33 |

Aparte, $394,172.93 del catálogo reconstruido **no entran en ninguno de los
dos** — todavía no tenían matriz para esta capa (`PENDIENTES-MEJORAS.md` B-69, que después los clasificó y explotó donde procedía):
no es un tercer alcance, es lo que se queda fuera de los dos de arriba.
