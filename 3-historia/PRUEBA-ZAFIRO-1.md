# PRUEBA DE FLUJO — ZAFIRO 1.0

```
órgano:     memoria episódica — prueba de sistema
capa:       III — Historia
pregunta:   ¿el camino de diseño aguanta a fondo?
tiempo:     fue así
corte:      2026-09-26
verificado: 8 etapas · 7 pasan · 1 diseñada sin caso real que la ejercite
```

> **Segunda prueba (B-42).** `PRUEBA-ALAMO-18.md` recorrió el flujo entero y pasó el
> diseño en una línea. **Aquí se abre esa línea.**
>
> El caso es `CAS-00004 Zafiro 1.0`: 172 m², **$1,842,426.01**, 14 subcapítulos, una
> planta. Es el prototipo sobre el que se rehizo el artefacto, así que tiene una
> cifra externa contra la cual comparar — lo que `METODO.md` §1.1 exige para que un
> error no pase desapercibido.

---

# El recorrido

| # | Etapa | Resultado |
|---|---|---|
| 1 | El árbol y su rollup | ✅ Pasa |
| 2 | Reconstrucción independiente (el artefacto) | ✅ **Δ $4.30 explicado y confirmado (B-49)** |
| 3 | Participación sobre el total | ✅ Pasa |
| 4 | Reuso de conceptos | ✅ Pasa |
| 5 | Unidades | 🔶 **Normalización diseñada (B-50)** — sin recargar este caso con la regla puesta |
| 6 | Estructura por subcapítulo | ✅ Pasa |
| 7 | Identificación del prototipo por contenido | ✅ Pasa — y es el caso fuerte |
| 8 | Clasificación del concepto | ✅ **Nunca fue un bloqueo real (B-51)** |

---

## 1 · El árbol y su rollup — ✅

665 nodos con hijos, 665 cuadran, cero diferencias. Sobre Zafiro en particular, los
14 subcapítulos suman su capítulo y el capítulo entra al total general.

---

## 2 · La reconstrucción independiente — ✅

El artefacto reconstruyó el presupuesto desde los datos y dio **$1,842,430.31**
contra **$1,842,426.01** declarado. **Δ $4.30**, sobre 1.84 millones: 0.00023%.

Esta es la etapa más valiosa de la prueba, porque es **la única del sistema que se
verifica contra algo externo**. Todas las demás comprueban que el sistema es
consistente consigo mismo.

> **Pero la diferencia está registrada como «explicada» y no está explicada.**
> `INVARIANTES.md` §2 dice *«la diferencia está explicada; si crece, algo cambió»* —
> y en ningún archivo dice **cuál** es la explicación.

**Al calcular las magnitudes, una hipótesis queda descartada y otra encaja:**

| Hipótesis | Deriva esperada | ¿Explica $4.30? |
|---|---|---|
| Redondear el **importe** de cada renglón a centavos | ±$0.11 | ⛔ Cien veces menos |
| Redondear el **PU** a centavos y multiplicar por cantidad | ±$4.7 con 350 renglones | ✅ Del orden exacto |

> **Predicción comprobable:** si la causa es la segunda, la deriva sobre los siete
> prototipos debería escalar ~√7 y rondar **$11**, no $30 ni $1. Eso se puede medir
> el día que se rehaga el artefacto completo.

**Hallazgo: una invariante decía estar explicada sin decir por qué.** Ahora tiene
hipótesis y forma de falsarla. **B-49.**

> **Actualización 2026-09-26 — la predicción se cumplió.** `explosion_recursiva.py`
> reprodujo el artefacto: ocho conceptos de subcontrato con matriz de relleno
> distorsionaban la prueba (mismo patrón que `SUB-` de `ALAMO 18`) — excluidos, el
> drift es -$4.59 en `Zafiro 1.0` (casi exacto al original) y se repite, siempre
> negativo, en los otros seis prototipos. Es redondeo acumulado del PU, confirmado
> con dato real, no solo la magnitud esperada. `CONOCIMIENTO.md` §5.7, D-311

---

## 3 · Participación sobre el total — ✅

Zafiro 1.0 es **11.19%** de $16,460,623.50. Los siete porcentajes suman exactamente
100.

> Es la comprobación más barata del catálogo y detectaría al instante un capítulo
> perdido o duplicado.

---

## 4 · Reuso de conceptos — ✅

**2,445 renglones de concepto sobre 471 claves distintas**: cada concepto se usa en
promedio en cinco lugares.

Eso valida la decisión de fondo: **la clave es la identidad y el renglón es el uso.**
Si el modelo guardara el concepto por renglón, habría 2,445 definiciones que
mantener en vez de 471.

---

## 5 · Unidades — 🔶

```
sal 827 · pza 798 · m2 421 · m 337 · act 52 · m3 8 · ser 2
```

En minúsculas y **sin normalizar**. Sobre este prototipo funciona igual, porque nadie
las suma entre sí.

**Corrección (2026-09-13):** al verificarlo contra los catálogos, `M²` no existe en
ningún archivo — ese ejemplo estaba inventado. El problema real es otro y mayor: el
presupuesto usa un **vocabulario paralelo**, `pza` contra `PZ` y `ser` contra `SERV`,
mientras los catálogos usan las 17 canónicas sin una sola variante.

> **D-86 queda intacto:** el catálogo cargado sí trae la unidad definida y es
> confiable. La duda estaba mal dirigida — el desorden no está en el catálogo.

**Hallazgo: falta normalizar la unidad del presupuesto al cargar.** Resuelto en
B-50: se normaliza al cargar contra el catálogo cerrado de 17, y lo que no mapea
entra marcado por validar.

> **Actualización 2026-09-26 — diseñado, y el catálogo ya se revisó, pero no se ha
> vuelto a correr sobre este caso.** `erp-importacion.md` §4b especifica la regla
> de carga y B-50 confirmó que los 17 canónicos están limpios (no existe un `M²`
> fantasma). Falta lo único que probaría si de verdad funciona: recargar
> `Zafiro 1.0` con la regla puesta y ver si `pza`/`ser` resuelven a `PZ`/`SERV`
> sin fricción. Por eso queda en `🔶`, no en `✅` — mecanismo cerrado, caso real
> sin correr encima todavía.

---

## 6 · Estructura por subcapítulo — ✅

Zafiro 1.0 tiene **14 subcapítulos**; los de dos plantas tienen 15. La diferencia es
exactamente **Planta Alta**.

Y el sistema resistió una trampa: parecía que Zafiro Plus tenía 4 subcapítulos —
resultó ser error de lectura, no del dato (K-02).

> **La estructura es predecible desde una sola variable** —tiene o no planta alta—, y
> eso es lo que hace que la cohorte del paramétrico sea declarable.

---

## 7 · Identificar el prototipo por contenido — ✅ el caso fuerte

Un archivo llamado *«Losa cimentación Zafiro Plus»* resultó **no ser Zafiro Plus**:

| Etapa | contra Zafiro Plus | contra Diamante c/ch |
|---|---|---|
| Estructura | 2.08 | **1.12** |
| Sanitarias | 1.46 | **1.03** |
| Hidráulicas | 1.38 | **1.00** |
| Gas | 2.18 | **1.00** |
| Eléctricas | 1.70 | 1.48 |

Contra Diamante, tres etapas dan 1.00 o 1.03. Contra Zafiro Plus, **ninguna se
acerca.**

> **Si alguien forma el presupuesto leyendo la descripción, costea el prototipo
> equivocado.** El contenido es la evidencia; la descripción es sólo una etiqueta.

Y el patrón de la dispersión también informa: el **1.48 de eléctricas** es la única
etapa que se sale, así que es la candidata a mirar — no ruido, señal.

---

## 8 · Clasificación del concepto — ✅

El 92% de los conceptos se clasifica solo con el trabajo que usa. **El 8% restante no
tiene de dónde derivarse** y hay que clasificarlo a mano.

`CASO-TRABAJADO.md` §7 ya lo muestra en un caso concreto: `EST-01053` no tiene `Tipo`,
`Familia` ni `Subfamilia`.

> No es un defecto del método de derivación — **es que esos conceptos no usan ningún
> trabajo del que se pueda deducir nada.** Y hoy nada dice qué pasa con ellos mientras
> no se clasifiquen: ¿se bloquean, entran sin clasificar, o se proponen?

**Hallazgo: falta la regla del concepto no clasificable. B-51.**

> **Actualización 2026-09-26 — nunca fue un bloqueo real.** `subfamilia_id` ya era
> nullable en `MODELO.md` desde antes de esta prueba: el 8% sin derivar se clasifica
> después, a mano, y no bloquea la carga. Tercera vez que un pendiente ya tenía
> respuesta sin releerse.

---

# Resultado

**Siete pasan, una queda diseñada sin caso real que la ejercite.** Cuando se corrió
esta prueba (2026-09-13) el resumen era otro —cinco pasan, tres se rompen— y las
tres roturas eran de la misma familia: **el modelo suponía que el dato de entrada
venía limpio.**

| Rompía en 2026-09-13 | Porque el modelo suponía | Hoy |
|---|---|---|
| Δ $4.30 sin explicar | Que «explicada» significa que alguien la explicó | ✅ Confirmado en los siete (B-49) |
| Unidades sin normalizar | Que la unidad del catálogo es confiable | 🔶 Mecanismo listo, sin recargar este caso (B-50) |
| 8% sin clasificar | Que todo concepto tiene de dónde derivar su clase | ✅ Nunca fue bloqueo real (B-51) |

> **Lo que distinguía esta prueba de la de ALAMO 18 sigue siendo cierto:** allá el
> flujo se corta por **falta de datos** (salidas de almacén, todavía así hoy). Aquí
> no faltaba dato — **la suciedad estaba en cómo se leía**, y leerlo distinto
> alcanzó para cerrar dos de los tres sin esperar dato nuevo.

> **Actualización 2026-09-26.** Cuando se corrió esta prueba, cinco de ocho etapas
> pasaban. Los tres hallazgos ya tienen respuesta en `PENDIENTES-MEJORAS.md`: B-49
> y B-51 quedaron confirmados con evidencia real, B-50 tiene la regla escrita y el
> catálogo verificado limpio, pero nadie ha vuelto a cargar `Zafiro 1.0` con ella
> puesta para confirmar que `pza`/`ser` resuelven a `PZ`/`SERV` sin fricción — de
> ahí que quede en `🔶` y no en `✅`.

## Lo que validó

- El rollup cuadra y los porcentajes suman 100 exacto.
- El reuso 2,445 → 471 confirma que clave e instancia están bien separadas.
- **La identificación por contenido funciona y atrapa una descripción que miente** —
  es la mejor defensa del principio de que el contenido es la evidencia.
- La estructura es predecible desde una variable, lo que hace declarable la cohorte.
