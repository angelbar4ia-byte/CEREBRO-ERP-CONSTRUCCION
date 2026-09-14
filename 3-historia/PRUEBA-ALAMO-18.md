# PRUEBA DE FLUJO — ALAMO 18

```
órgano:     memoria episódica — prueba de sistema
capa:       III — Historia
pregunta:   ¿el flujo completo aguanta sobre una obra real?
tiempo:     fue así
corte:      2026-09-13
verificado: 12 etapas recorridas · 5 pasan · 2 se rompen · 5 sin poder probarse
```

> **Escenario de prueba** en el sentido de B-42: un caso real recorrido de punta a
> punta para ver si el sistema hace lo que dice. Distinto de `CASO-TRABAJADO.md`, que
> explica el modelo sobre una zapata; **esto busca dónde se rompe.**
>
> Todo número de aquí está verificado en `CONOCIMIENTO.md` §11 o `CATALOGOS.md`.
> **Donde no hay dato, se dice — no se simula.**

---

# El caso

`ALAMO 18`: un lote real, **prototipo Diamante con chimenea**, con 12 ingenierías de
abril a septiembre de 2026 y presupuesto base de **$2,829,925.98**.

Se eligió porque es el único que tiene las dos puntas: **lo planeado** (presupuesto
del prototipo) y **lo planeado para esta obra** (ingeniería del lote). La tercera
punta —lo ejecutado— es justamente la que falta, y eso mismo es un resultado.

---

# El recorrido, etapa por etapa

| # | Etapa | Resultado |
|---|---|---|
| 1 | Diseño del presupuesto | ✅ Pasa |
| 2 | Escenarios | ⛔ No existe — **y la obra tenía uno sin declarar** |
| 3 | Cuantificación de volúmenes | ⛔ No existe |
| 4 | Paramétrico | ⛔ No existe |
| 5 | Carga de la ingeniería del lote | ✅ Pasa |
| 6 | Reversión por destajo | ⚠️ **Pasa al 84% — falta qué hacer con el 16%** |
| 7 | Comparación contra prototipo | ✅ Pasa, y encuentra un hecho real |
| 8 | Factorizador | ⚠️ **No resuelve el problema que parecía suyo** |
| 9 | Programa y ruta crítica | ⛔ No existe |
| 10 | Recursos por fecha | ⛔ No existe |
| 11 | Contratación y congelamiento | ⛔ Sin probar |
| 12 | Salidas y desviación | ⛔ **Falta el dato** (P-38) |

---

## 1 · Diseño del presupuesto — ✅

El árbol del Diamante con chimenea suma al centavo: **$2,829,933.69 calculado contra
$2,829,925.98 declarado**, la misma diferencia de redondeo de siempre.

> La invariante de rollup se cumple sobre una obra real, no sobre un ejemplo.

---

## 2 · Escenarios — ⛔, y aquí está el primer hallazgo

El módulo no existe (B-39). Pero al recorrer la obra apareció algo mejor que una
carencia teórica:

> **`ALAMO 18` se cargó con la versión anterior del catálogo**, donde el mortero se
> usaba para muros, repellos y finas exteriores — antes de que el cemento lo
> sustituyera. Confirmado por el usuario.

**Eso es un escenario.** Misma obra, distinto alcance de materiales. Pero como no
existe la figura, no se declaró: **apareció después, disfrazado de discrepancia**, y
costó una investigación descubrir que no era un error de datos.

| Con escenarios | Sin escenarios (hoy) |
|---|---|
| «Esta obra va con catálogo v1» | El cemento sale al 35% y nadie sabe por qué |
| La comparación lo descuenta | La comparación lo reporta como anomalía |
| Se compara contra su propia base | Se compara contra una base que no le toca |

> **Hallazgo:** un escenario no declarado no desaparece — **reaparece como
> desviación falsa**. Es el argumento más fuerte a favor de B-39, y salió de la obra,
> no del diseño.

---

## 3 · Cuantificación — ⛔

`CASO-TRABAJADO.md` §7 ya lo declara: no se sabe de dónde salió el `216 M2`. Sobre
ALAMO 18 pasa igual con todas las cantidades.

**Consecuencia para la prueba:** las cantidades de origen no son auditables, así que
todo lo que sigue hereda esa incertidumbre. No invalida los resultados —la aritmética
cuadra— pero **impide distinguir un error de medición de un cambio de obra.**

---

## 4 · Paramétrico — ⛔

No existe. Y con lo decidido en M-3, esta obra sería un buen caso: es de dos plantas,
y la cimentación de dos plantas tiene **32% de dispersión** contra 2% en una planta.
Entra en la cohorte difícil, no en la fácil.

---

## 5 · Carga de la ingeniería — ✅

Doce archivos, cuatro estructuras distintas, ninguno comparte nivel ni etapa.

| Archivo | Filas | Cubre |
|---|---|---|
| `CIM` | 118 | `NIV-00001` · etapas 1 a 5 |
| `PB` | 512 | `NIV-00002` · etapas 6-11, 57, 61 |
| `PA_AZO_ACA` | 956 | 8 niveles · 26 etapas |
| `PISOS` | 218 | etapas 24 y 25 — **sin declarar nivel** |

**Se suman, no se reemplazan**, y el sistema detecta solo que está incompleto: la
suma da **92%** del presupuesto. El 8% que falta son cinco niveles enteros sin
ingeniería — cancelería, carpintería, muebles, herrería y consumibles.

> **Las 41 etapas de la ingeniería existen en el presupuesto.** Ninguna es ajena: la
> detección de faltantes funciona y no produce falsos positivos.

**Pregunta que abre para el programa:** si cinco niveles no tienen ingeniería,
**¿el CPM puede programarlos?** Hoy no hay respuesta.

---

## 6 · Reversión por destajo — ⚠️

Sobre la cimentación: **32 de 38 destajos · 84%**, filtrando por el prototipo
correcto. Sin filtrar, 42%.

Y las cantidades salen **enteras exactas** —6.000, 4.000, 5.000, 3.000, 2.000,
1.000—, lo que significa que recupera cantidades reales, no aproximaciones.

**Lo que se rompe es el 16% restante**, y el modelo no dice qué hacer con él:

| Caso | Cuántos | Qué hace el sistema hoy |
|---|---|---|
| Ambiguos — varios candidatos | 4 | **No definido** |
| Sin candidato | 2 | **No definido** |
| `MOS-2079` — formato roto | 1 de los 2 | Falla cualquier búsqueda exacta |

> La regla general dice que detectar no necesita permiso y corregir sí, así que **un
> destajo ambiguo debería ser propuesta con sus candidatos**. Pero eso no está
> escrito en ninguna parte, y sin escribirlo cada implementación lo resolverá
> distinto.

**Hallazgo: falta la regla del residuo de la reversión.**

---

## 7 · Comparación contra el prototipo — ✅

519 insumos comparados: **361 en ambos, 29 solo en ALAMO 18, 129 solo en el
prototipo**.

Y encontró un hecho real de la obra: `ADH-00005 Cemento` al **35%** de lo esperado,
el único que baja fuerte cuando casi todo sube. Eso llevó a la sustitución de la
etapa 2.

> **El método funciona como se diseñó:** cuando casi todo crece y una cosa baja
> mucho, es candidato a sustitución. No fue un error de datos, fue la obra.

También confirmó que **7 claves perdidas al migrar siguen usándose en obra real** —
el mortero solo suma $184,587.

---

## 8 · Factorizador — ⚠️ no resuelve lo que parecía suyo

`PET-00002 Arena` sale **150 veces mayor** en ALAMO que en el prototipo: $49,755
contra $332.

Parece el caso típico de unidades. **No lo es.** En el prototipo la arena vive
embebida dentro de compuestos —mezclas, morteros— y en la ingeniería del lote aparece
suelta, repetida en cada bloque. Es **cómo se arma el archivo**, no cuántos metros
cúbicos hay.

| El factorizador resuelve | Esto necesita |
|---|---|
| Unidad base, presentaciones, mínimo de compra | **Consolidar antes de comparar**: abrir compuestos a un solo nivel de detalle en los dos lados |

> **Hallazgo:** la comparación entre dos fuentes necesita **normalizar profundidad de
> explosión** antes de restar. Eso no está en ninguno de los cuatro módulos, y sin
> ello cualquier comparación produce desproporciones que parecen hallazgos.

---

## 9 a 11 · Programa, recursos por fecha, contratación — ⛔

No se pueden probar. Pero el recorrido deja tres preguntas concretas para cuando
existan:

- **Los cinco niveles sin ingeniería** (§5): ¿se programan con la cantidad del
  prototipo, o quedan fuera del programa?
- **La actividad en tramos** (P-5): la cimentación de este lote tiene colados que
  interrumpen — es exactamente el caso.
- **El tiempo de entrega** (B-40): sin él, el material por fecha da consumo, no
  pedido.

---

## 12 · Salidas y desviación — ⛔ falta el dato

Es la tercera pata, y la única que compara contra lo **ejecutado de verdad**:

```
Prototipo            →  lo que el modelo dice que debería llevar    ✅ existe
Ingeniería del lote  →  lo que se planeó para esta obra             ✅ existe
Salidas de almacén   →  lo que REALMENTE se entregó                 ⛔ falta
```

**Sin esa tabla, el sistema compara dos planes entre sí.** Puede decir que la obra se
planeó distinto al prototipo; **no puede decir si se construyó como se planeó.**

Es P-38, y esta prueba lo confirma como el dato que más falta.

---

# Resultado de la prueba

**Cinco etapas pasan, dos se rompen, cinco no se pueden probar.** El flujo aguanta
completo desde la carga hasta la comparación entre planes, y se corta justo donde
empieza la ejecución.

## Lo que la prueba encontró y no estaba

| # | Hallazgo | Dónde quedó |
|---|---|---|
| 1 | **Un escenario no declarado reaparece como desviación falsa** | B-39 gana su mejor argumento |
| 2 | **Falta la regla del residuo de la reversión** — qué hacer con los ambiguos y los sin candidato | B-46 |
| 3 | **Comparar dos fuentes exige normalizar la profundidad de explosión primero** | B-47 |
| 4 | ¿Se programan los niveles sin ingeniería? | B-48 |

## Lo que la prueba validó

- El rollup cuadra sobre una obra real, no sólo sobre un ejemplo.
- La detección de ingeniería incompleta funciona **sin falsos positivos**: las 41
  etapas existen en el presupuesto.
- La reversión recupera cantidades **enteras exactas** — no aproxima.
- La comparación contra prototipo **encuentra hechos de obra**, no sólo errores de
  captura.

## Cómo se vuelve a correr

Los cuatro pasos de arriba son reproducibles con los mismos archivos. **Cuando se
cargue la tabla de salidas, esta prueba se retoma desde la etapa 12** y entonces se
puede cerrar el flujo completo por primera vez.
