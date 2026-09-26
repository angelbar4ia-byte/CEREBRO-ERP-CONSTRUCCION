# ESTADO

```
órgano:     propiocepción
capa:       IV — Dirección
pregunta:   ¿dónde vamos y cómo retomar?
tiempo:     vamos aquí
corte:      2026-09-26
verificado: Punto de corte · sin bloqueos
```

> **Léeme primero.** Punto de corte, cómo retomar, y dónde va cada cosa.
>
> Corte: 2026-09-20

> **Si te dicen «continuar con el roadmap» o «continuar con pendientes»: es acá.**
> Este archivo es el punto de entrada — no un artifact publicado ni el historial de
> chat, que una sesión nueva no puede leer solo. Seguí la sección **Cómo retomar**.

---

## Qué es esto

Un **modelo de ERP de construcción verificado contra datos reales** — ocho catálogos
de OPUS 2025 y doce ingenierías de obra. Cada regla se comprobó aritméticamente
antes de escribirse.

**Para:** crear un ERP nuevo, reestructurar los existentes, y darles un idioma común.

---

## Cómo retomar

**Esto ya es un repo de git real — no hace falta subir nada a mano.** Una sesión
nueva de Claude Code lo tiene todo con solo abrir el repo.

**Primero, el estado de git — antes de leer un solo archivo de contenido:**

```
git branch --show-current           ← debería ser claude/serene-cannon-1g0zas
git log --oneline -5                ← el último commit tiene que coincidir con
                                       lo que este archivo describe como hecho
```

Y el estado del Pull Request — hay uno abierto:
**https://github.com/angelbar4ia-byte/CEREBRO-ERP-CONSTRUCCION/pull/1**
Si sigue abierto, el trabajo de esta rama todavía no se mergeó a `main`. Seguí
trabajando sobre la misma rama salvo que el usuario diga lo contrario.

**Después, leer en este orden — el cerebro está en carpetas por capa**
(`1-mundo`, `2-operacion`, `3-historia`, `4-direccion`; ver `INDICE.md`):

```
1. ESTADO.md          ← este: dónde vamos
2. METODO.md          ← cómo se piensa aquí
3. INDICE.md          ← dónde va cada cosa
4. CONOCIMIENTO.md    ← las reglas del sistema
   CATALOGOS.md       ← sólo si hay que verificar un dato de origen
5. MEMORIA.md         ← decidido, descartado y corregido
6. LENGUAJE.md        ← el canon y los dialectos
7. MODELO.md          ← el modelo de datos aprobado
8. INVARIANTES.md     ← contra qué se comprueba y cuándo se para
```

Los demás cuando se vayan a tocar: `erp-construccion.md`, `PRIORIDADES.md`,
`PENDIENTES-MEJORAS.md`, `APRENDIZAJE.md`, `GLOSARIO-DOMINIO.md`,
`DICCIONARIO-DATOS.md`, `CASO-TRABAJADO.md`, `PROPUESTA-CUATRO-MODULOS.md`,
`agentes/`, `backend/core/` (el motor de cálculo, con sus pruebas).

> **Las cuatro capas** — Mundo · Operación · Historia · Dirección — y el bloque de
> `órgano:` de cada encabezado están en `INDICE.md`.

Los catálogos y el artefacto **solo si hace falta verificar algo** — ya están
analizados y sus hallazgos escritos.

> **Antes de proponer cualquier cosa, leer `MEMORIA.md` §2.** Doce ideas razonables
> ya se evaluaron y se rechazaron.

> **Antes de decidir algo, no solo proponerlo: preguntar.** El usuario lo pidió
> explícitamente — «el sistema propone, el humano aprueba» (D-32) es la regla de
> siempre, pero se venía aplicando mal: una propuesta con evidencia se escribía
> directo en vez de esperar la aprobación. Desde entonces, cada decisión de
> `MODELO.md` se trajo como pregunta concreta antes de tocar el archivo.

Correr el verificador **antes de tocar nada y después de cada commit**:
```
python3 2-operacion/verificar-cerebro.py .
```
Tiene que decir *"Todo cuadra"* en los dos momentos.

---

## Lo terminado

| Bloque | Estado |
|---|---|
| **Conocimiento** | 15 partes de reglas · `CATALOGOS.md` con los 8 de OPUS · `IDEAS.md` con lo no diseñado |
| **Cadena de costo** | Los 467 conceptos, 89 compuestos y 39 cuadrillas **cuadran al centavo** |
| **Modelo de datos** | `MODELO.md` aprobado, con 15 hallazgos resueltos |
| **Roles y permisos** | Cierra P-21 — `ROL`, `FUNCION_ATOMICA`, `ROL_FUNCION` (`MODELO.md` §5b) · muchos-a-muchos, sin tope por monto · Cierra B-73 — 28 funciones atómicas (12 nuevas: incidencia, cierre de frente, edición de programa, precio nuevo con aprobación doble), D-329 · 🆕 Cierra B-75 — `validar_estimacion` a Control de obra, `gestionar_rol_funcion` nueva para reasignar sin tocar esquema, lista completa de 33 funciones (21 asignadas, 12 a propósito sin asignar), D-330 |
| **Histórico de precios** | Cierra P-07/P-08 — `PRECIO_HISTORICO`, `VERSION_CONCEPTO.pu`, `TABULADOR_CONTRATISTA` (`MODELO.md` §4a) · catálogo de contratistas (P-39) sigue anotado, marcador de prototipo (P-40) cierra con `PRESUPUESTO.tipo` |
| **Ensamble / Paramétrico** | 🆕 Cierra B-53 — `NODO`(rol=ensamble)+`COMPOSICION` reusados sin campo nuevo, `ENSAMBLE_PARAMETRO` nuevo para tasa/cohorte/dispersión (`MODELO.md` §1c, D-325). `CONSTANTE_FISICA` (B-18) con dos filas reales; el motor de cálculo del constructor sigue sin diseñar, D-326 |
| **Método** | `METODO.md` — cómo se razona, con los errores que lo enseñaron |
| **Lenguaje** | Canon 1.0, tres dialectos, prueba de ida y vuelta ejecutada |
| **Memoria** | 330 decisiones · 12 descartes · 15 correcciones · 12 hallazgos de construcción |
| **Skill** | Base + 4 satélites compilados: importación, rediseño, paramétrico, 🆕 cuantificador |
| **Agentes** | 🆕 **gravity** orquesta · arquitecto, constructor, migrador, auditor · 🆕 **gravity-obra** interno |
| **Glosario** | 79 términos · 25 ambigüedades |
| **Diccionario de datos** | 🆕 Cierra B-60/B-61/B-29 — homologación reusa `EQUIVALENCIA` + `CLON` (viaje de vuelta, dos campos nuevos); `NORMALIZACION` y `GRUPO_FUNCIONAL` son tabla nueva; `BITACORA_RECLASIFICACION` con `ENSAMBLE_PARAMETRO.revisar` (`MODELO.md` §4b, D-328) |
| **Módulos** | Las 22 decisiones de los cuatro cerradas (CPM cierra con P-10: reiniciar programa no toca lo registrado) · Cuantificador con tabla (`MODELO.md` §1b) · 🆕 CPM con tabla completa (`MODELO.md` §5c, D-327) — `ACTIVIDAD`, `PRECEDENCIA`, `CALENDARIO`, `TRAMO`, los dos cuantificadores, `FRENTE_TOPE_CUADRILLA`, `CIERRE_FRENTE` · Factorizador listo para diseño formal |
| **Estimación** | 🆕 Cierra P-18 — dos fuentes, el tope es el mismo techo del cuantificador de presupuesto (D-273/D-285), topes pagados = Tope − Pagado, deducciones/retenciones/préstamos definidos. Validado contra un archivo real: 0 de 416 filas exceden el tope. `CONOCIMIENTO.md` §13.8 |
| **Pruebas de flujo** | 🆕 Tres corridas: ALAMO 18, Zafiro 1.0, siete prototipos · 13 pasan, 8 se rompen, 5 sin dato |
| **Invariantes** | 🆕 Las cifras de control, juntas · condición de paro |
| **Capas** | 🆕 Cuatro: Mundo · Operación · Historia · Dirección |
| **Escalabilidad** | 🆕 Contrato de módulo · ERP nuevo y ERP existente |
| **Coherencia** | 🆕 `verificar-cerebro.py` — el cerebro se comprueba solo |
| **Motor de cálculo** | `backend/core/` — sin Django, puerto + adaptador en memoria. 11 pruebas contra `CASO-TRABAJADO.md`, D-178 a D-182. **Falta la persistencia** (Django/Postgres) |
| **La alerta** | Tabla `ALERTA` (`MODELO.md` §5a) — peldaño de abajo de `PROPUESTA`. Cierra B-32, P-29, P-30 |
| **Cuantificación** | Tablas `TRAZO`/`ENLACE_CUANTIFICACION` y geometría cerrados (PostGIS D-218, GeoJSON D-219/D-220, WKT D-221) — cierra B-19. 🆕 Gobierno cierra (B-45, roles reusados, D-236) · 5 de 7 reglas de dominio en `medida×factor`, taludes vía `formula_personalizada` (`CONOCIMIENTO.md` §17) · `NOTA_PLANO` nueva (D-237) · skill `erp-cuantificador` compilado. Quedan ejes/niveles (bloqueado por `FRENTE`) y la aspiración de un agente que trace solo |
| **Caso trabajado** | Un ejemplo de punta a punta con 12 reglas |
| **Artefacto** | Rehecho con datos verificados: $1,842,430.31 vs $1,842,426.01 |
| **Catálogos corregidos** | Conceptos, materiales, trabajos, mano de obra, fletes |
| **Vocabularios** | Unidades, niveles, etapas, familias — **derivados**, no pedidos |
| **Semilla** | Cuadrilla y rendimiento teórico, 265 filas |
| **Ingenierías de ALAMO 18** | 12 archivos. Las partes se suman; faltan 5 niveles (uno, Consumibles, en $0). 🆕 De los otros 4 sin ingeniería —Cancelería/Carpintería/Muebles-Iluminación/Herrería— se sabe el costo exacto: $542,464.67, 19.2% del base **en dinero** (no confundir con el 92%/8% por conteo de etapas de `PRUEBA-ALAMO-18.md` §5) |
| **Reversión por destajo** | Probada: 84% en cimentación. 🆕 Escalada a diez niveles completos: **catálogo de presupuesto reconstruido desde la ingeniería real**, $2,561,657.71, +12.0% vs. catálogo de referencia. Dos técnicas nuevas fijas —concepto auxiliar (dominante) y concepto "lote" para material compartido sin llave— más las reglas de desempate que le faltaban a la reversión. `CONOCIMIENTO.md` §11.13, D-238 a D-242 |
| **Rendimiento real vs. almacén** | 🆕 Léxico del archivo resuelto (`Lote`, no `Ubicacion`/`# Lote`; cadena `OP:`/`No.Parte:`). Dos conceptos de abril cruzados contra su matriz a la misma escala (reversión), con el bug de mano de obra corregido: -19.7%/-2.6%. Corte semanal nuevo: tabique por lote (normal) vs. cemento a diario (señal confiable) — una semana de `EST-02010` con 68.5% del pagado sin respaldo de cemento. La hipótesis de tramo sobre ese mismo caso no se confirmó (D-260). 🆕 «Rendimiento real» separado en dos: mano de obra (alimenta al CPM) y material (alimenta al costo), nunca el mismo dato (`CONOCIMIENTO.md` §6.2) · avance físico y avance pagado son dos registros que no se sobrescriben, la diferencia es la señal (§13.7). `CONOCIMIENTO.md` §11.15 a §11.17, D-249 a D-256, D-260, D-263, D-264 |
| **Controles de cambio — CC-ALM-18XXX** | 🆕 Método cerrado para los archivos `AJU_*` sueltos: agrupador con hijo, o matriz invertida con residuo `TMP-ALM18-XX`; verificado contra crudo antes de contar. Cinco controles, $36,214.03, capa complementaria a Presupuesto Formado. Cierra P-31. `CONOCIMIENTO.md` §11.18, §13.4, D-256 |

---

## Lo que sigue, en orden

**Veintiún pendientes se cerraron el 2026-09-15** (P-02, P-03, P-04, P-05, P-06,
P-11, P-12, P-13, P-19→B-19, P-23, P-25, P-29, P-30, M-13, M-15, M-16, B-01, B-02,
B-31, B-32, y el auditor en `ESCALABILIDAD.md`) — todas revisadas y aprobadas con
el usuario, con evidencia en `MEMORIA.md` D-178 a D-203. El detalle día por día
está en la Hoja de Ruta (artifact publicado, fuera de este repo — pedile el link
al usuario si hace falta, este archivo no lo guarda).

| # | Qué | Dónde |
|---|---|---|
| 1 | **Revisar y mergear el PR abierto** | [PR #1](https://github.com/angelbar4ia-byte/CEREBRO-ERP-CONSTRUCCION/pull/1) — motor de cálculo + los 21 pendientes de arriba |
| 2 | **Módulos grandes sin diseñar**: estimaciones, almacén | P-18 · P-19 — ninguno tiene decisiones tomadas todavía, a diferencia de factorizador/CPM/cuantificador/roles/histórico de precios |
| 3 | **`IDEAS.md` §7 — Sustitución de insumo dentro de una matriz** | Séptima operación de rediseño, propuesta pero sin que el arquitecto la revise |
| 4 | **Persistencia del motor de cálculo** | `backend/core/` es solo dominio — Django/Postgres, el resto del schema de `MODELO.md`, y las demás piezas de B-03 a B-07 |
| 5 | **Clasificar a mano el 8% de conceptos** sin derivación — ⛔ bloqueado: falta el dato | El 92% sale del trabajo que usa. No confundir con el otro 92%: el de la ingeniería de `ALAMO 18` cubriendo el presupuesto |
| 6 | **Salidas de almacén de ALAMO 18** — 🔶 primeros cruces reales hechos, solo 2 conceptos de abril | Cierra el triángulo prototipo → ingeniería → **ejecutado**. P-38, `CONOCIMIENTO.md` §11.12 a §11.17: léxico del archivo, rendimiento real vs. matriz (con el bug de mano de obra corregido), corte semanal tabique/cemento. Ver `PRUEBA-ALAMO-18.md` §12, B-55, B-64, B-70 |
| 7 | El resto de `PENDIENTES-MEJORAS.md` — mayormente ⛔ bloqueado por los catálogos crudos de OPUS, que no están en este repo | M-14, M-17/18, P-09/10, P-26 a P-36 |
| 8 | **Completar el catálogo de ALAMO 18** — faltan 4 niveles sin ingeniería cargada (Cancelería, Carpintería, Muebles/Iluminación, Herrería — $542,464.67) | ⛔ Bloqueado: no se sabe si los archivos existen y no se subieron, o si de verdad no hay ingeniería para esos niveles todavía. Después, Paso 2: explotar el catálogo reconstruido contra salidas de almacén (fila 6) |
| 8 | Las ideas sin tocar del modelo | `IDEAS.md` §1, §3, §4, §5, §6 — seis, sin diseñar. Cuantificación (§2) cierra hoy — ver tabla de arriba |

---

> **El criterio de este orden vive en `PRIORIDADES.md`.** Aquí sólo la cola.

---

## Lo único que bloquea

**Nada para seguir construyendo lo ya aprobado.** `MODELO.md` está aprobado, y con
él **trece módulos tienen sus reglas escritas y verificadas**: motor de cálculo,
catálogo, APU, presupuesto, importación, semilla, diccionario, rediseño,
paramétrico, propuestas, alerta, cuantificación, y las cuatro decisiones de
factorizador y CPM listas para diseño formal.

Los que esperan decisión están identificados: exportación (P-14), histórico de
precios (P-07/P-08), estimaciones (P-18), almacén (P-19), programa —más allá del
CPM, ya resuelto— (P-20), permisos (P-21).

---

## Los cinco patrones que sostienen el modelo

Ninguno se diseñó — se repitieron hasta hacerse evidentes:

| Regla | Veces |
|---|---|
| **Mientras nada dependa, se corrige; en cuanto algo depende, se agrega encima** | **5** |
| **Plantilla e instancia** | **5** |
| Nada reasigna | 3 |
| Declarado menos calculado | 3 |
| El prefijo no es llave | 3 catálogos |

---

## El artefacto

`artefacto-erp-construccion.jsx` — datos verificados del prototipo Zafiro: 398
renglones, 491 insumos, 26 compuestos.

Demuestra las tres reglas difíciles de explicar en texto: **las dos lecturas del
árbol**, el **anidamiento sin límite** y la **cascada por compuestos**.

---

## Lo que no se puede automatizar

No hay forma de agendar tareas ni ejecutar nada entre sesiones. **Este archivo es la
continuidad:** no arranca solo, pero arranca bien.
