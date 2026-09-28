# PRUEBA DE FLUJO — ALAMO 18

```
órgano:     memoria episódica — prueba de sistema
capa:       III — Historia
pregunta:   ¿el flujo completo aguanta sobre una obra real?
tiempo:     fue así
corte:      2026-09-28
verificado: 12 etapas recorridas · 4 pasan · 2 con matices · 4 diseñadas sin caso real que las ejercite · 2 sin poder probarse
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
| 2 | Escenarios | 🔶 **Diseñado desde el 26/09** (`PRESUPUESTO.tipo=escenario`, `MODELO.md` §3a) — sin caso real que lo ejercite en su sentido prospectivo. El caso que motivó B-39 (abajo) resultó ser otro mecanismo |
| 3 | Cuantificación de volúmenes | ⛔ No existe |
| 4 | Paramétrico | 🔶 **Diseñado desde el 26/09** (`NODO`(rol=ensamble)+`COMPOSICION`+`ENSAMBLE_PARAMETRO`, `MODELO.md` §1c) — sin correr todavía contra la cimentación de dos plantas de este lote |
| 5 | Carga de la ingeniería del lote | ✅ Pasa |
| 6 | Reversión por destajo | ⚠️ **Pasa al 84% — falta qué hacer con el 16%** |
| 7 | Comparación contra prototipo | ✅ Pasa, y encuentra un hecho real |
| 8 | Factorizador | ⚠️ **No resuelve el problema que parecía suyo — la política de consolidar ya cerró (P-36, 26/09), la comparación no se ha vuelto a correr con ella** |
| 9 | Programa y ruta crítica | 🔶 **Modelo de datos completo desde el 26/09** (`ACTIVIDAD`/`PRECEDENCIA`/`CALENDARIO_OBRA`/`TRAMO`, `MODELO.md` §5c) — el motor de cálculo del CPM sigue sin escribirse, y esta obra no tiene actividades cargadas para correrlo |
| 10 | Recursos por fecha | 🔶 **Diseñado desde el 26/09** (`MODELO.md` §5f, misma explosión leída por fecha) — depende de 9, que tampoco tiene datos que leer todavía |
| 11 | Contratación y congelamiento | ⛔ Sin probar |
| 12 | Salidas y desviación | ✅ **Pasa — cinco meses de almacén y cuatro de avance, el triángulo material-avance cuadra en acumulado al 99.8%** (`MOVIMIENTO_ALMACEN` §5e, comparación de cinco columnas §5f, `DESVIACION` §5g). El 27/09 pasó de uno a cinco meses de almacén; el 28/09 cerró el avance —y con él, un falso positivo propio: el 68.5% sin respaldo que parecía un hallazgo real era la ventana de datos incompleta (D-375) |

---

## 1 · Diseño del presupuesto — ✅

El árbol del Diamante con chimenea suma al centavo: **$2,829,933.69 calculado contra
$2,829,925.98 declarado**, la misma diferencia de redondeo de siempre.

> La invariante de rollup se cumple sobre una obra real, no sobre un ejemplo.

---

## 2 · Escenarios — 🔶, y aquí está el primer hallazgo

> **Actualización 2026-09-26 — el módulo ya existe, y el caso que lo motivó no
> lo necesitaba.** `PRESUPUESTO.tipo` gana el valor `escenario` (`MODELO.md`
> §3a, D-335): ya tiene gratis su propio árbol y su propio programa, y elegir
> uno se traduce a la obra vía rediseño sin reemplazar su identidad. Pero al
> revisar el caso real de abajo con la fecha correcta, resultó ser **otro
> mecanismo** — leer `VERSION_CONCEPTO` vigente a la fecha en que se cargó la
> obra, no la de hoy, con campos que ya existían desde antes (§4a). El
> mecanismo prospectivo (comparar precio/proveedor, alcance o programa antes
> de construir) queda diseñado sin un solo caso real que lo haya ejercitado
> todavía.

El módulo no existía cuando se corrió esta prueba (B-39). Al recorrer la obra
apareció algo mejor que una carencia teórica:

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

## 4 · Paramétrico — 🔶

> **Actualización 2026-09-26 — diseñado: no era tabla nueva, era el árbol un
> piso arriba.** `NODO`(rol=ensamble) + `COMPOSICION` ya cubrían plantilla/
> instancia, origen de cantidad y la referencia al concepto sin campo nuevo;
> lo único que faltaba era `ENSAMBLE_PARAMETRO` (tasa, cohorte, dispersión —
> `MODELO.md` §1c, D-325). Sigue sin correr contra ningún caso real, y este
> lote —cimentación de dos plantas, cohorte difícil— sería el primero.

No existía cuando se corrió esta prueba. Y con lo decidido en M-3, esta obra
sería un buen caso: es de dos plantas, y la cimentación de dos plantas tiene
**32% de dispersión** contra 2% en una planta. Entra en la cohorte difícil,
no en la fácil.

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

> **Precisión 2026-09-18, en dinero:** de los cinco niveles sin ingeniería,
> Consumibles vale $0 — no cuenta. Los otros cuatro sí tienen presupuesto real:
> **$542,464.67, 19.2% del base.** El 8% de arriba cuenta **etapas** (41 de las
> totales); 19.2% cuenta **pesos**. No se contradicen — miden cosas distintas, y
> cancelería/carpintería concentran presupuesto alto en pocas etapas. Detalle en
> `CONOCIMIENTO.md` §11.13.

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

### Escalado a diez niveles completos — 2026-09-18

Lo de arriba se probó solo sobre cimentación. Se repitió sobre **los diez
niveles con ingeniería cargada** —Planta Baja, Planta Alta, Azotea, Acabados,
Obras Exteriores, Asador, Barda Perimetral, Pintura y Pergolado Cochera— para
ver si el método aguanta a escala, no solo en el caso que lo probó.

**Resultado: $2,561,657.71 reconstruidos, +12.0% contra el catálogo de
referencia de esos mismos diez niveles ($2,287,461.31).** Tabla completa y
método —las dos técnicas, las reglas de desempate nuevas, el concepto "lote"
y la convención `TMP-XXXXX`— en `CONOCIMIENTO.md` §11.13. Acá solo lo que es
específico de esta obra.

La reversión por destajo **no fue la técnica que más se usó**: la mayoría de
los 72 conceptos nuevos ya traían su propio encabezado, y la cantidad salió
directo de su línea de mano de obra («concepto auxiliar», §5.4 de
`CONOCIMIENTO.md`). La reversión solo hizo falta en instalaciones y
cableado — y ahí encontró **las dos reglas de desempate que le faltaban** al
16% que se rompía arriba: deduplicar candidatos antes de declarar
ambigüedad, y que la mano de obra siempre ancla sobre el material.

**Hallazgos propios de ALAMO 18, no del método:**

| Hallazgo | Cifra |
|---|---|
| Barda perimetral, **por debajo** del presupuesto | $21,021.78 vs $27,434.63 — **-23.4%** |
| Pergolado cochera, **por debajo** — pérgola más chica que la de catálogo | 28.00 m² reales vs 34.57 m² de catálogo — **-18.1%** |
| Cableado eléctrico e instalaciones de obra exterior, **exactos** | $22,451.61 y $10,362.86 — **0.0%** de diferencia |
| Pisos de planta baja con **material distinto al presupuestado** | `ACA-02101` Brunei Ivory, `ACA-80473`/`80474` Sequoia Beige y Amaretto Tobacco — claves nuevas, no las del catálogo |
| Jardinería, **por arriba** — más pasto y más excavación de lo presupuestado | $21,419.50 vs $15,479.00 — **+38.4%** |
| `OBE-01010` (muros de cisterna) **sin ninguna fila en el catálogo maestro** | $12,726.59 — B-65 |

**Y confirma, con más peso, lo que arriba ya había encontrado:** cuatro
niveles —Cancelería, Carpintería, Muebles/Iluminación, Herrería— siguen sin
ninguna ingeniería cargada. Contados en dinero, no en etapas, son
**$542,464.67 — 19.2% del presupuesto base.**

> **`TMP-00002` cerrado — 2026-09-19, y trajo un hallazgo más grande que el
> prorrateo.** Al revisar la opción con el usuario (¿prorratear, cobrar la
> fila completa, o repartir a un concepto existente?), se cruzó el PU de
> los cuatro insumos sobrantes contra las matrices de concepto confirmadas
> —independientes de la fila de ingeniería, ya validadas en otros
> conceptos— y **no coincidía con la columna `Total` de la fila real:**
>
> | Insumo | `Total` de la fila (lo que se había usado) | Total real (cantidad × PU de matriz) |
> |---|---:|---:|
> | `SAN-00005` (Yee 4x4, cantidad real 3) | $63.50 | $190.50 |
> | `SAN-00006` (Yee 6x4, cantidad real 3) | $94.01 | $282.03 |
> | `SAN-00018` (tubo reforzado 6", cantidad real 6) | $3,034.00 | $4,551.00 |
> | `SAN-00019` (tubo reforzado 4", cantidad real 4) | $615.02 | $1,230.04 |
>
> **La columna `Total` de la ingeniería no es cantidad×PU en ninguna de las
> cuatro filas** — en dos, `Total` quedó igual al `PU` (como si la cantidad
> fuera 1); en las otras dos, `Total` corresponde a la cantidad *esperada*
> del catálogo, no a la cantidad real capturada. Es un error de captura de
> la fuente, no algo que el método pudiera prevenir sin el cruce contra la
> matriz — B-66.
>
> **Con el PU correcto, se prorrateó el excedente** (la opción del usuario,
> descontando lo que el concepto confirmado ya necesita, para no duplicar
> ese costo): `TMP-00002` sube de $1,423.84 a **$2,447.04** — $127.00 +
> $188.02 + $1,517.00 + $615.02. `NIV-00001` queda en **$292,339.84**
> (antes $291,316.64) y el total de los diez niveles en **$2,561,657.71**.
>
> **`TMP-00001` no se pudo revisar igual** — sus cuatro insumos (`HD-00411`,
> `HID-00134/135/181`) no aparecen en ninguna matriz de concepto confirmada,
> así que no hay PU independiente contra qué cruzarlos. Queda con su costo
> original ($658.28), con la duda abierta y sin forma de cerrarla con los
> datos de hoy.

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

> **Actualización 2026-09-26 — la pregunta que se quedó abierta detrás de esta
> (P-36) ya cerró.** Normalizar profundidad antes de comparar ya lo resolvía
> B-47; lo que faltaba era una capa más simple: si el cargador debía
> **consolidar** insumos repetidos como esta arena al importar. Dato del
> usuario: depende de quién lee, no del insumo — compras/obra necesitan el
> consolidado, costos/control necesitan el detalle crudo. No se consolida al
> cargar; cada lector agrupa a su modo (`CONOCIMIENTO.md` §11.11, D-340). No
> se volvió a correr la comparación de esta etapa con la regla ya aplicada.

---

## 9 a 11 · Programa, recursos por fecha, contratación — 🔶 🔶 ⛔

No se podían probar cuando se corrió esta prueba. **Actualización 2026-09-26 —
9 y 10 ya tienen modelo de datos completo**, sin que nada de esta obra lo haya
ejercitado todavía:

- **Programa** (`MODELO.md` §5c, D-327): `ACTIVIDAD` completa, `PRECEDENCIA`,
  `CALENDARIO_OBRA`/`CALENDARIO_EXCEPCION`, `TRAMO` — el motor de cálculo del
  CPM (fechas tempranas/tardías, ruta crítica) sigue siendo código, no
  schema, y esta obra no tiene ni una `ACTIVIDAD` cargada para correrlo.
- **Recursos por fecha** (`MODELO.md` §5f, D-336): la misma explosión leída
  por fecha, con `CONSTANTE_FISICA(categoria=tiempo_entrega)` para separar
  pedido de consumo — depende por completo de que 9 tenga datos que leer.
- **Contratación y congelamiento** sigue igual que el 2026-09-20: sin probar.
  `ESTADO_CONGELAMIENTO` existe desde la primera versión del modelo, antes de
  esta obra; nada de esta sesión lo tocó.

Las tres preguntas que dejó esta prueba ya tienen dónde resolverse, ninguna
probada aún contra este lote:

- **Los cinco niveles sin ingeniería** (§5): siguen sin lista de qué se
  contrata terminado y qué se programa — B-48 quedó parcial en esa misma
  pregunta.
- **La actividad en tramos** (P-5): `TRAMO.reparto_material` ya existe
  (`MODELO.md` §5c) — la cimentación de este lote, con colados que
  interrumpen, sigue siendo el caso que lo probaría primero.
- **El tiempo de entrega** (B-40): ya es `CONSTANTE_FISICA(categoria=
  tiempo_entrega)`, con base natural/hábil — sin un programa cargado para
  esta obra, no hay fecha de inicio de la que restarlo todavía.

---

## 12 · Salidas y desviación — ⚠️ modelo de datos completo, topado en dato real

Es la tercera pata, y la única que compara contra lo **ejecutado de verdad**:

```
Prototipo            →  lo que el modelo dice que debería llevar    ✅ existe
Ingeniería del lote  →  lo que se planeó para esta obra             ✅ existe
Salidas de almacén   →  lo que REALMENTE se entregó                 ⛔ falta
```

**Sin esa tabla, el sistema compara dos planes entre sí.** Puede decir que la obra se
planeó distinto al prototipo; **no puede decir si se construyó como se planeó.**

Es P-38, y esta prueba lo confirma como el dato que más falta.

> **Actualización 2026-09-18 — empezó a llegar el dato, y trae su propio riesgo.**
> Con `04_ABRIL_MOVIMIENTOS_DE_ALMACEN.xlsx` y el "resumen del lote" del ERP propio
> del usuario (`PRECIO_REAL_ALAMO_18.xlsx`) cargados, aparece algo que P-38 no
> había previsto: **dos exports del mismo lote pueden venir de la misma tabla de
> origen, solo que filtrada distinto.** 76 filas de la hoja `Materiales` del
> resumen comparten `# Reg` exacto —mismo movimiento, mismo Lote 18, misma
> cantidad— con filas ya presentes en el export de almacén de abril. **No son dos
> fuentes que se suman: es una sola, exportada dos veces con distinto filtro de
> fecha.** Sumarlas habría duplicado abril completo dentro de la desviación real.
>
> **Hallazgo: antes de combinar dos exports de salidas como si fueran
> independientes, hay que verificar identidad de origen (una llave como `# Reg`),
> no solo que las columnas se parezcan.** B-64.
>
> El dato para cerrar P-38 sigue incompleto —todavía no hay salidas para el resto
> de los meses de obra— pero ya se sabe cómo NO combinar lo que vaya llegando.

> **Actualización 2026-09-20 — la tercera pata ya se arma, con lo que hay.**
> Con `PRECIO_REAL_ALAMO_18.xlsx` (hoja Mano de Obra para destajo pagado, hojas
> Consolidado Materiales/MO para consumo de almacén) se construyó la
> comparación completa **por destajo y por material** —árbol y consolidado,
> presupuesto base / ingeniería / pagado real / **Presupuesto Formado** (el
> catálogo reconstruido a cantidad real, explotado con el rendimiento del
> catálogo base)— `CONOCIMIENTO.md` §11.14. Sigue siendo parcial: el pagado
> real mezcla lo registrado por concepto y por destajo suelto (se convierte),
> y 40 conceptos del catálogo reconstruido ($394,172.93) todavía no tienen
> matriz para esta capa (B-69). **No es la tabla de salidas completa
> que pide P-38** —siguen faltando meses de almacén— pero ya no se compara
> solo entre dos planes: la parte de mano de obra y material que sí llegó,
> ya se compara contra lo ejecutado de verdad.

> **Mismo día, un nivel más profundo — el archivo crudo de almacén, no solo el
> consolidado.** Con `04_ABRIL_MOVIMIENTOS_DE_ALMACEN.xlsx` (hoja `Consulta`) se
> resolvió su léxico —`Lote` numérico es el filtro correcto, no `Ubicacion`
> (nombre de calle, cruza cuatro lotes) ni `# Lote` (siempre `S/L`); `Ubicacion`
> además se repite dos veces en el encabezado con significados distintos— y se
> identificó la cadena de referencia de la actividad que pedía P-38:
> `Motivo="Implosión De Materiales"` + `Referencia` con `OP:folio,
> No.Parte:clave`, validada contra la columna `# OP` (67 de 67 exacto).
> `CONOCIMIENTO.md` §11.15, D-249/D-250.
>
> Con eso se cruzaron los dos únicos conceptos de abril con las dos puntas
> —`EST-01060` losa de cimentación, `EST-02010` muro de tabique— contra su
> propia matriz, a la misma escala implícita (reversión sobre un insumo ancla,
> no la cantidad pagada acumulada). **El primer resultado tenía un bug propio:**
> comparar material de almacén —que nunca registra mano de obra— contra un
> total de matriz que sí la incluía. Corregido: de -31.2%/-40.3% a
> **-19.7%/-2.6%**. `EST-02010` corregido prácticamente cuadra.
> (`CONOCIMIENTO.md` §11.16, D-251 a D-253.)
>
> Bajando un nivel más, a la semana: `PRECIO_REAL_ALAMO_18.xlsx` trae en su hoja
> `Mano de Obra` una columna `Semana` no usada hasta ahora. Cruzada contra la
> salida de almacén semana a semana, aparece una asimetría real de campo —el
> tabique se abastece por lote (desfase normal), el cemento a diario (señal
> confiable)— y con ella un hallazgo concreto: una semana de `EST-02010` pagó
> 293 m² con material que solo respalda ~92 m², **68.5% sin respaldo**.
> `CONOCIMIENTO.md` §11.17, D-254/D-255. Motivó una idea a futuro, sin diseñar
> todavía: verificar la estimación contra almacén *al prepararla*, no después
> del pago del viernes (B-70).
>
> Y en paralelo, los ajustes sueltos `AJU_*` —que P-38 no sabía dónde ubicar
> (P-31)— se resolvieron como **controles de cambio**, con clave propia
> `CC-ALM-18XXX`: agrupador con concepto hijo, o matriz invertida con residuo
> `TMP-ALM18-XX` cuando dos destajos están en desacuerdo, verificado contra el
> archivo crudo antes de contar cada línea. Cinco controles, $36,214.03,
> complementan —no se suman a— Presupuesto Formado.
> (`CONOCIMIENTO.md` §11.18 · §13.4, D-256.)
>
> **Sigue siendo parcial y probablemente traiga sus propios errores**: solo dos
> conceptos, un mes, y el patrón tabique/cemento se probó sobre un solo caso.
> Se anota así — «no digo que esté bien», en palabras del usuario— para que la
> siguiente corrida lo corrija si hace falta, no para cerrarlo.

> **Actualización 2026-09-26 — el modelo de datos que faltaba ya no falta; el
> mes de almacén sigue siendo el único que hay.** Tres piezas cerraron:
>
> - **`MOVIMIENTO_ALMACEN`** (`MODELO.md` §5e, D-333): el archivo real de
>   abril ya separaba surtido (`salida_produccion`, nunca liga a concepto) de
>   consumido (`implosion`, siempre liga vía `op`/`nodo_id`) — exactamente la
>   fórmula de arriba, sin campo nuevo. Auditoría propia (D-337) le agregó
>   `presupuesto_id`, resuelto de la columna `Lote` al importar — sin él, la
>   tabla no tenía cómo decir de qué obra es un movimiento sin `nodo_id`.
> - **El reporte de cinco columnas** (`MODELO.md` §5f, D-334): Presupuesto
>   Base, Ingeniería, Pagado Real, Presupuesto Formado y Control de Cambio
>   quedaron con dónde vivir cada una — cuatro reusan tabla ya cerrada, la
>   quinta (`PROPUESTA(tipo=orden_cambio)`) solo necesitaba la forma de su
>   JSON. La misma auditoría corrigió un error real: «Pagado Real» de
>   material apuntaba a `motivo=recepcion`, que no se puede atribuir a una
>   obra (las 1,767 filas reales de ese motivo traen `Lote` vacío — la
>   compra entra a almacén general antes de saber a qué casa va). Corregido
>   a `salida_produccion`/`implosion`.
> - **`DESVIACION`** (`MODELO.md` §5g, D-343): la política de
>   `CONOCIMIENTO.md` §13.6 —nueve causas, «sin causa» válido, la causa se
>   agrega después sin penalizar— llevaba meses cerrada sin tabla. Los
>   patrones que dicen si algo corrige el catálogo (mismo insumo en todo
>   concepto, mismo concepto en toda obra) son consulta agregada sobre ella,
>   no tabla aparte.
>
> **Nada de esto agrega un segundo mes de almacén.** El cuello de botella
> sigue siendo el mismo que el 2026-09-20: `CONOCIMIENTO.md` §11.19 confirmó
> que la cobertura real es parcial (58 de 288 materiales, 36 de 225
> destajos, D-294), y D-322 confirmó que un segundo archivo que parecía
> traer más dato era el mismo abril exportado dos veces. El modelo ya no es
> lo que falta — el dato, sí.

> **Actualización 2026-09-27 — el cuello de botella se movió, no
> desapareció.** Marzo, mayo, junio y julio se cargaron completos, sin
> traslape con abril ni entre sí — de 76 a 358 movimientos reales de
> ALAMO 18 (`Lote`=18 **y** `Ubicacion`=ALAMO juntos; `Lote` solo no basta
> — se repite en otras calles, corregido en `CONOCIMIENTO.md` §11.15/D-365),
> de 2 `# OP` a 47. `EST-02010` (muro tabique) tiene ahora
> cuatro meses seguidos de implosión, y julio —cero tabique, cemento
> normal— es la confirmación más limpia hasta hoy de que el tabique se
> abastece por lote y un mes sin movimiento no es desviación
> (`CONOCIMIENTO.md` §11.20). **Pero el archivo de avance/pagado sigue
> existiendo solo para abril** — sin él no se puede repetir el «% sin
> respaldo de cemento» para los meses nuevos, así que la tercera pata
> completa (ingeniería-almacén-pagado) sigue probada sobre un solo mes,
> aunque el almacén por sí solo ya no lo esté. De paso, dato del usuario
> al revisar estos archivos buscando insumos no registrados: **la cimbra
> nunca se mueve para esta obra** pese a que su presupuesto la exige en
> 167 renglones — no es hueco de diseño, es que nadie la registra
> (`CONOCIMIENTO.md` §11.20, D-356).

> **Actualización 2026-09-28 — la tercera pata completa, y un falso
> positivo propio corregido.** El usuario cargó `grid_AvanceOPEventosOpr`
> de marzo, mayo, junio y julio — el archivo de avance/pagado que faltaba
> en la actualización de arriba. Con la semana 19 de `EST-02010` completa
> (antes cortada a la mitad por el mes que faltaba), el 68.5% sin
> respaldo de cemento que este mismo documento reportó **no se sostiene**:
> esa semana traía 80 sacos, no 30 — los otros 50 llegaron en mayo, fuera
> de la ventana que existía cuando se calculó. Extendido a las ocho
> semanas reales de `EST-02010` entre abril y julio: en acumulado, 238
> sacos de cemento real contra 237.6 que pide el rendimiento teórico para
> los 730.15 M² pagados — **0.17% de diferencia**. El aprendizaje de
> fondo también se corrige: cemento y tabique se abastecen los dos por
> lote, diferencia de grado (tandas chicas y frecuentes contra tandas
> grandes y espaciadas), no de tipo — ninguno se lee bien semana a
> semana sin ver el acumulado. Corregido en `CONOCIMIENTO.md` §11.17 y en
> el diseño de `estimacion_sin_respaldo_material` (`MODELO.md` §5a), que
> ahora compara contra el acumulado. `CONOCIMIENTO.md` §11.17, D-375.

---

# Resultado de la prueba

**Cuatro etapas pasan, dos tienen matices, cuatro quedaron diseñadas sin caso real
que las ejercite, dos no se pueden probar.** El flujo aguanta completo desde la
carga hasta la comparación entre planes, y donde empieza la ejecución ya hay
modelo de datos completo y probado con cinco meses reales — el cuello de botella
dejó de ser el diseño y pasó a ser, en cada una de las cuatro `🔶`, la falta de un
caso real corriendo encima.

> **Actualización 2026-09-26.** Cuando se corrió esta prueba (2026-09-20), 6 de
> las 12 etapas no tenían dónde apoyarse (`⛔`). Hoy son 2 (`Cuantificación`,
> `Contratación`) — las otras 4 pasaron a `🔶` (2, 4, 9, 10); las notas de 8 y
> 12 también cambiaron, pero esas dos ya eran `⚠️` desde el 20/09, no `⛔`.
> Todo por el mismo patrón: la política ya estaba escrita, y la mayoría de las veces la
> tabla que hacía falta resultó ser mucho más chica de lo que el hueco
> parecía prometer. Ninguna de las cuatro `🔶` se ha corrido todavía contra
> este lote — «diseñado» no es «probado», y esta prueba existe justamente
> para no confundir las dos cosas.

## Lo que la prueba encontró y no estaba

| # | Hallazgo | Dónde quedó |
|---|---|---|
| 1 | **Un escenario no declarado reaparece como desviación falsa** | B-39 gana su mejor argumento |
| 2 | **Falta la regla del residuo de la reversión** — qué hacer con los ambiguos y los sin candidato | B-46 |
| 3 | **Comparar dos fuentes exige normalizar la profundidad de explosión primero** | B-47 |
| 4 | ¿Se programan los niveles sin ingeniería? | B-48 |
| 5 | **Dos exports de salidas pueden ser la misma fuente filtrada distinto** — hay que verificar identidad de origen antes de sumar | B-64 |
| 6 | **El catálogo maestro no cubre el 100% de los conceptos reales**, aunque nivel y etapa existan — `OBE-01010` no tiene ninguna fila de referencia | B-65 |
| 7 | **Comparar material real contra un total de matriz que incluye mano de obra infla la brecha artificialmente** — almacén nunca la registra | D-252, `CONOCIMIENTO.md` §11.16 |
| 8 | **Ningún insumo se verifica bien semana a semana sin ver el acumulado** — corregido: se creyó que cemento (diario) servía y tabique (por lote) no; los dos se abastecen por lote, solo que en tandas de tamaño distinto | D-255, D-375, B-70 |

## Lo que la prueba validó

- El rollup cuadra sobre una obra real, no sólo sobre un ejemplo.
- La detección de ingeniería incompleta funciona **sin falsos positivos**: las 41
  etapas existen en el presupuesto.
- La reversión recupera cantidades **enteras exactas** — no aproxima.
- La comparación contra prototipo **encuentra hechos de obra**, no sólo errores de
  captura.
- **La reconstrucción escala:** de cimentación (un nivel, prueba de concepto) a
  diez niveles completos ($2,561,657.71, +12.0% vs. catálogo) sin cambiar de
  método — solo agregando dos reglas de desempate y una técnica más
  («concepto auxiliar», dominante sobre la reversión). `CONOCIMIENTO.md` §11.13.

## Cómo se vuelve a correr

Los cuatro pasos de arriba son reproducibles con los mismos archivos. **Cuando se
cargue la tabla de salidas, esta prueba se retoma desde la etapa 12** y entonces se
puede cerrar el flujo completo por primera vez.

**Y ahora hay cuatro etapas más con la misma forma de pendiente** (2, 4, 9, 10):
diseño cerrado, sin un caso real que lo corra sobre `ALAMO 18`. Ninguna necesita
dato nuevo para intentarse — a diferencia de la 12, que sí lo necesita. Correrlas
es la forma más directa de encontrar el próximo hallazgo real, mismo principio que
motivó esta prueba desde el inicio: **el modelo se rompe donde nadie miró
todavía, no donde se supone que debería.**
