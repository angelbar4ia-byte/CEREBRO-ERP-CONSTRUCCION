# INVARIANTES

```
órgano:     nocicepción · condición de paro
capa:       II — Operación
pregunta:   ¿esto sigue cuadrando?
tiempo:     tiene que dar esto
corte:      2026-10-12
derivado:   CONOCIMIENTO.md · ESTADO.md · SKILL.md · agentes/ · backend/core/
verificado: las cifras de §1, §2, §3 y §6 que tienen fuente en el repo vueltas a sacar de los CSV de `1-mundo/opus/` el 2026-10-12; sin fuente en el repo: los catálogos de materiales, trabajos, mano de obra y fletes de §6, el Δ $4.30 de §1 y toda la §5
```

> **Las cifras contra las cuales se para.** Nada de aquí es nuevo: todo estaba
> verificado y disperso en seis archivos. Aquí está junto, para poder comprobarlo
> de un tirón.
>
> Cumple dos funciones que son la misma: **avisar cuando algo se rompió**, y
> **decir cuándo terminó el trabajo**. Sin un número contra el cual parar,
> persistencia es bucle (`METODO.md` §1.1).

---

## Dos clases de invariante, y sólo una caduca

**El presupuesto base se actualiza cada seis meses** (D-126). Eso parte esta lista en
dos:

| Clase | Ejemplo | Al actualizar la base |
|---|---|---|
| **Estructural** | 665 nodos con hijos cuadran · los 7 % suman 100 · ningún ciclo · `Decimal` en todo el camino | **No cambia.** Si falla, es falla |
| **De valor** | $16,460,623.50 · $1,842,426.01 · 387 materiales | **Cambia.** Es línea base con fecha, se renueva |

> Una cifra de valor que cambia en la actualización semestral **no es un error**: es
> la línea base nueva. Lo que sí es error es que cambie **sin** actualización.

| Sección | Clase |
|---|---|
| §1 Aritmética del árbol | **Mixta** — «el árbol suma» es estructural; los totales son de valor |
| §2 Estructura · §3 Cálculo · §7 El propio cerebro | **Estructurales** |
| §6 Volúmenes de referencia | **De valor** |
| §4 Deriva conocida · §5 Convergencia | **Históricas** — no se renuevan, se conservan |

## Cómo se lee

| Columna | Qué es |
|---|---|
| **Invariante** | Lo que tiene que ser cierto siempre |
| **Valor** | La cifra de control verificada |
| **Fuente** | Contra qué archivo se midió |
| **Si falla** | Qué significa que no cuadre |

**Ninguna cifra de aquí se escribe sin fuente.** Si una regla no dice contra qué
se verificó, no es invariante: es una creencia.

---

# 1. Aritmética del árbol

| Invariante | Valor | Fuente | Si falla |
|---|---|---|---|
| El árbol suma de las hojas a la raíz | **665 nodos con hijos, 665 cuadran. Cero diferencias** | `CATALOGO_DE_PRESUPUESTO` · `CATALOGOS.md` §1 | El rollup está mal, o hay nodos huérfanos |
| Total general del presupuesto | **$16,460,623.50** | `CATALOGOS.md` §1 | Cambió el alcance, no el cálculo |
| Los 7 prototipos suman el 100% | Exacto | `CATALOGOS.md` §1 | Falta o sobra un capítulo |
| Prototipo Zafiro 1.0 (`CAS-00004`) | **$1,842,426.01** · 172 m² | `CATALOGOS.md` §1 | Es la cifra de prueba del artefacto |
| Artefacto contra declarado | **$1,842,430.31 vs $1,842,426.01** · Δ $4.30 | `ESTADO.md` | **Hipótesis: PU redondeado a centavos × cantidad** (B-49). Predicción: sobre los 7 prototipos la deriva debe rondar $11, no $30 |
| Conceptos, compuestos y cuadrillas | **467 · 89 · 39**, cuadran al centavo (467 de los 471 conceptos del presupuesto tienen matriz) | `ESTADO.md` · `erp-construccion.md` | Se rompió la cadena de costo |

> **Son dos verificaciones distintas y hay que hacer las dos:** que el árbol sume
> bien, y que el PU de cada concepto corresponda a su explosión. La primera cierra;
> la segunda tiene deriva conocida — ver §4.

---

# 2. Estructura — lo que parece error y no lo es

Cada una de estas se habría destruido en una migración que las tratara como
suciedad. **Un cargador que las rechace está mal el cargador, no el dato.**

| Invariante | Valor | Fuente | Si falla |
|---|---|---|---|
| Cantidades negativas son legítimas | **58 líneas en 23 conceptos** | `METODO.md` §2.3 · `erp-construccion.md` §1 | Un validador de solo-positivos las está tirando |
| El mismo insumo se repite en una matriz | **26 casos** (`AUX-00001`, alambre recocido) | `CATALOGOS.md` §7 | La llave es `(padre, hijo)` en vez de posición |
| Fila en blanco = separador de bloque | **155 bloques, sin una sola excepción**: 151 con un agrupador detrás y 4 que cierran el archivo | `CONOCIMIENTO.md` §11.8 | Se están cargando como nodos fantasma |
| Placeholders de OPUS descartables | **121 filas · 3.7%** — importe cero **y** sin descendientes con clave | `CONOCIMIENTO.md` §2.5 | Si una tiene hijo costeado, **es error que se reporta, no fila que se tira** |
| El prefijo no es llave | **79 claves `AUX-` son `Tipo = Material`** | `METODO.md` §2.1 | Alguien dedujo categoría del prefijo |
| Profundidad libre | **1,233 conceptos cuelgan de un Nivel 2 · 1,219 de un Nivel 3** | `erp-construccion.md` §1 | Una consulta asumió el número de capas |

---

# 3. Cálculo

| Invariante | Valor | Fuente | Si falla |
|---|---|---|---|
| `%MO` calcula sobre la suma de jornales | **39 cuadrillas, exactamente una línea `%MO`, siempre al `0.1`** | `CATALOGOS.md` §4 | Se tomó `Costo` como precio; **en líneas `%MO` es la base ya calculada** |
| El orden de las capas no altera el total | Todas sobre la misma base | `constructor-erp.md` | Se implementó acumulativo donde no lo es |
| Ningún compuesto se contiene a sí mismo | Cero ciclos, en cualquier capa | `constructor-erp.md` | Recursión infinita en el motor |
| El dinero es `Decimal` de punta a punta | Ningún `float` intermedio | `erp-construccion.md` | Los centavos dejan de cuadrar y **nadie se entera hasta el total** |
| Las dos lecturas conviven | Montos **se detienen** en el compuesto · explosión **llega al fondo** | `CONOCIMIENTO.md` §10.5 | El esquema solo soporta una; el diseño está mal |

> Las cinco corren como test automático desde D-178: `backend/core/tests/test_motor_calculo.py`,
> 11 pruebas contra `CASO-TRABAJADO.md`. Esta tabla sigue siendo la lista para lo que
> el código todavía no cubre — persistencia, capas de sobrecosto, el resto del schema.

---

# 4. Deriva conocida — no es falla

**Estas diferencias existen, están explicadas, y no se corrigen en silencio.**
Si desaparecen sin que nadie lo decida, eso sí es la falla.

| Deriva | Valor | Qué es |
|---|---|---|
| PU declarado vs. suma de la explosión | Diverge en ~la mitad de los conceptos | Artefacto de OPUS. **La matriz tiene deriva; el presupuesto no** |
| Artefacto vs. presupuesto Zafiro | $4.30 | Explicada |

> `METODO.md`: la deriva se nombra, no se esconde.

---

# 5. Convergencia — la prueba de dos caminos

No son cifras a mantener: son **validaciones cruzadas ya ejecutadas**. Se registran
porque un método que acertó dos veces es el método a repetir.

| Hecho | Camino A | Camino B | Resultado |
|---|---|---|---|
| Factor de la losa de `ALAMO 18` | **1.12** por totales de etapa | **1.130** reversando desde el destajo | Los dos validados |
| Prototipo real de `ALAMO 18` | Tres etapas dieron **1.00** contra Diamante | Ninguna se acercó contra Zafiro Plus | La descripción mentía |
| Rendimiento entre catálogos | **1.085** en los 22 trabajos de pintor, sin variación | 1.085 en 58 de 78 | Factor real, no coincidencia |
| Reversión por destajo | **32 de 38 · 84%** filtrando por prototipo | 16 de 38 · 42% sin filtrar | El filtro es lo que la hace viable |

> **Dos caminos que no se conocen entre sí y llegan al mismo número se validan
> mutuamente** (`METODO.md` §1.4). Es la mejor prueba disponible cuando no hay
> respuesta de antemano.

---

# 6. Volúmenes de referencia

Contra esto se compara cualquier carga. **Si el conteo no coincide, el alcance está
mal antes que el dato** (`METODO.md` §1.2).

| Catálogo vigente | Filas |
|---|---|
| `CATALOGO_DE_PRESUPUESTO` | 3,231 |
| `ANALISIS_DE_BASICOS_CONCEPTOS` | 2,568 |
| `CATALOGO_DE_MATERIALES` | 387 |
| `ANALISIS_DE_BASICOS_COMPUESTOS` | 267 |
| `CATALOGO_DE_TRABAJOS` | 265 |
| `CATALOGO_DE_MANO_DE_OBRA` | 97 |
| `CATALOGO_DE_FLETES` | 9 |

---

# 7. Invariantes del propio cerebro

**Los archivos de gobernanza también se desincronizan**, y sin ruido. Se comprueban
con `verificar-cerebro.py`, que no corrige: reporta.

| Invariante | Si falla |
|---|---|
| Cada archivo trae bloque de órgano completo | Nadie sabe qué capa es ni contra qué se verificó |
| La capa declarada coincide con la carpeta | El enrutamiento empezó a mentir |
| `corte:` válido y no futuro | La vigencia dejó de ser comprobable |
| Toda referencia a un archivo apunta a uno que existe | Se renombró algo y quedaron cabos |
| Toda referencia `§N` apunta a una sección que existe | Ya pasó dos veces |
| Los conteos declarados son los reales | Pasó con el conteo de términos del glosario: el índice se quedó viejo |
| Las cifras de aquí siguen en su archivo fuente | La invariante quedó huérfana |
| Ningún párrafo largo aparece en dos archivos | **Un hecho empezó a vivir en dos lugares** |

> El script comprueba lo mecánico. **Dos archivos que dicen lo mismo con palabras
> distintas sólo se detectan leyendo** — eso sigue siendo trabajo del auditor.

---

# 8. Cómo se usa

**Al cargar datos** — se corren los de §1 y §6. Si el total no da, el alcance está
mal; no se interpreta la diferencia hasta descartarlo.

**Al escribir código** — §2 y §3 son la lista de comprobación del constructor. Un
test que pasa con fixtures limpias no dice nada: se prueba con los datos reales que
contienen los 58 negativos y los 26 repetidos.

**Al terminar una tarea** — el trabajo está hecho cuando las invariantes que toca
siguen dando. No cuando parece correcto.

> **Lo que este archivo no hace:** decidir. Una invariante que falla **se reporta**;
> corregirla es propuesta. La detección nunca necesita permiso; la corrección
> siempre (`CONOCIMIENTO.md` §14.4).
