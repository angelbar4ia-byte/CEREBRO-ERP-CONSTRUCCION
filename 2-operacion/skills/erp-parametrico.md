---
name: erp-parametrico
description: Presupuesto paramétrico por ensambles en el ERP de construcción — plantilla e instancia, la cantidad como receta, divisor, cohorte y dispersión, extracción desde presupuestos existentes y generación de presupuestos nuevos. Usar al implementar ensambles, al decidir de dónde sale la cantidad de un renglón de ensamble, al calcular o publicar una tasa paramétrica, o al regenerar un presupuesto con renglones editados a mano. NO cubre el APU ni el rediseño — ver `erp-construccion` y `erp-rediseno`.
---

```
órgano:     vía mielinizada — paramétrico
capa:       II — Operación
pregunta:   ¿cómo se presupuesta sin tener el detalle todavía?
tiempo:     se hace así
corte:      2026-09-12
compilado:  `CONOCIMIENTO.md` §5 — no se escribe a mano
```

> **Satélite.** Carga el skill base `erp-construccion` primero.

---

## 0. Qué es

**El mismo mecanismo del APU, un piso más arriba.**

```
APU           concepto  →  insumos    con cantidad
PARAMÉTRICO   ensamble  →  conceptos  con cantidad
```

**No es un módulo con reglas propias:** es el árbol recursivo aplicado a otro nivel
de abstracción. Y es un documento aparte del presupuesto, igual que el concepto es
aparte de sus insumos.

```
ensamble       Recámara tipo A
  concepto       Aplanado en muros
    insumo         Estuco, mano de obra
```

Es desglosable: un ensamble puede contener sub-ensambles.

---

## 1. Plantilla e instancia

La misma distinción que ya existe un piso abajo: el APU de *aplanado en muros* no se
contrata; los 279 m² de aplanado de la Zafiro sí.

| | Qué es | Contratable | Programable |
|---|---|---|---|
| **Plantilla** | *Recámara tipo A*. Una receta | No | No |
| **Instancia** | *Recámara 1 del lote 14*, con cantidades reales | **Sí** | **Sí** |

**La instancia es lo que reemplaza al presupuesto detallado actual:** se opera sobre
30 ensambles en vez de 400 conceptos, y el detalle sigue abajo dando el precio.

---

## 2. La cantidad es receta, no volumen

Un ensamble puede tomar **1 regadera aunque el presupuesto tenga 3**, y los muros que
corresponden a esa regadera aunque en planta baja haya para tres. La relación lleva
**su propia cantidad**.

> Por lo tanto el paramétrico **nunca tuvo que cuadrar con el presupuesto**. No es una
> partición ni una vista: es un ensamble armado con piezas encontradas ahí.

**Un concepto puede estar en varios ensambles sin que eso sea doble contabilidad.**

### De dónde sale la cantidad

Tres orígenes, y **el origen es campo explícito del renglón**:

| Origen | Ejemplo |
|---|---|
| **Heredada del concepto** | La cantidad que tiene en el presupuesto |
| **Heredada de un destajo** | Los m² de un destajo dentro del concepto auxiliar |
| **Manual** | Capturada a mano |

> **Heredar es mejor que capturar.** Heredada, el día que cambie el volumen el
> ensamble se entera. Capturada, se desincroniza en silencio y nadie se entera.

---

## 3. La referencia apunta al concepto, no al renglón

Al armar un ensamble se navega el presupuesto —es donde las cosas están en su
contexto— pero **lo que se guarda es el concepto**.

Si se guardara el renglón, borrar o reordenar ese presupuesto dejaría el ensamble
colgando de algo que ya no existe. Apuntando al concepto, *Recámara tipo A* sigue
siendo armable aunque la Zafiro desaparezca — que es justo lo que hace falta para
componer un diseño nuevo desde el prototipo más parecido.

El presupuesto de origen se guarda como **referencia informativa**, no como liga
estructural.

---

## 4. Dos explosiones, no una

| Explosión | Contiene | Para qué |
|---|---|---|
| **De costo** | Todo: materiales, destajos, subcontratos | Da el precio |
| **De contratación** | Sólo destajos, agrupados por sub-ensamble | Se paga y se programa |

**Los sub-ensambles son la unidad natural de contratación**, porque es donde el
destajo tiene sentido para quien ejecuta.

---

## 5. Parámetro, cohorte y dispersión — medido

Se probó sobre los siete prototipos si el costo escala con los m².

**Un paramétrico global no funciona.** El costo por m² va de $8,717 a $11,841: **36%
de variación**.

Por subcapítulo, algunos sí:

| Subcapítulo | $/m² | Dispersión |
|---|---|---|
| Acabados | 911 | **5%** |
| Planta alta | 1,371 | 10% |
| Carpintería | 1,063 | 11% |
| Cancelería | 405 | 20% |
| Cimentación | 931 | 23% |
| Herrería | 116 | **38%** |

Y la cimentación revela por qué falla:

```
1 planta    Zafiro 1,039   Rubí 1,012   Jade 1,053          → CV  2%
2 plantas   ZafPlus 660  Diam- 1,090  Diam+ 1,085  Oro 577  → CV 32%
                                                    juntos  → CV 23%
```

En una planta la cimentación por m² es prácticamente idéntica. **Lo que la rompía era
mezclar cohortes:** en dos plantas el m² construido ya no es proporcional a la
superficie de desplante.

> **El paramétrico no falla por ser paramétrico. Falla por usar el parámetro
> equivocado o la cohorte equivocada.**

### Las tres reglas que salen de ahí

- **Parámetro propio por ensamble.** Cimentación escala con desplante, instalaciones
  con salidas. No todo con el m² total.
- **Cohorte explícita.** Cada ensamble declara a qué aplica. **Fuera de ella, no se
  usa.**
- **La dispersión se guarda junto al valor.** Acabados a $911 ±5% es utilizable;
  Herrería a $116 ±38% es una adivinanza.

> **Un precio paramétrico sin su dispersión es un número disfrazado de certeza.**

El divisor vive **en el ensamble**, no en cada renglón.

---

## 6. Las dos direcciones

```
Extracción    presupuesto → ensamble     se arma la plantilla desde lo ya hecho
Generación    ensamble → presupuesto     se compone una casa nueva
```

**Las dos conviven sobre el mismo documento.** Sobrantes y faltantes son normales.

### El residuo es un indicador, no un error

```
presupuesto = Σ ensambles + conceptos sueltos
                             └── «el 12% de esta casa no está sistematizado»
```

Los conceptos sueltos miden **cobertura**, y son los candidatos naturales para el
siguiente ensamble.

> El residuo sólo tiene sentido **en generación**. En extracción no significa nada:
> tomar 1 de 3 regaderas no deja residuo, deja lo que no se quiso.

### Editar un presupuesto generado

Si se genera desde ensambles y luego se edita una cantidad a mano, al regenerar **no
se arrasa ni se respeta en silencio**: el renglón se marca **desvinculado** y se
muestra la divergencia. Resolverla es decisión de alguien.

---

## 7. Cuantificador y paramétrico no compiten

```
CUANTIFICADOR    plano → medida → cantidad     mide lo que hay
PARAMÉTRICO      cantidad ÷ divisor → tasa     aprende de lo medido
```

> **El paramétrico aprende de cantidades medidas.** Construido sobre cantidades
> capturadas hereda sus errores **y les da apariencia de estadística**.

---

## 8. Los errores que este skill previene

1. Tratar el paramétrico como módulo con árbol propio en vez de otro nivel del mismo.
2. Exigir que el ensamble cuadre con el presupuesto. **Nunca tuvo que cuadrar.**
3. Contar como doble contabilidad que un concepto esté en varios ensambles.
4. Capturar cantidades que se podían heredar — se desincronizan en silencio.
5. Guardar el renglón en vez del concepto, y dejar el ensamble colgando.
6. Una sola explosión: la de costo no sirve para contratar.
7. Un parámetro único para todo el presupuesto. El m² global varía 36%.
8. Mezclar cohortes: una planta y dos plantas no son la misma población.
9. Publicar una tasa sin su dispersión.
10. Usar un ensamble fuera de su cohorte declarada.
11. Al regenerar, arrasar los renglones editados a mano —o respetarlos en silencio—.
12. Construir el corpus paramétrico sobre cantidades capturadas y llamarlo estadística.
