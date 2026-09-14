# ESTADO

```
órgano:     propiocepción
capa:       IV — Dirección
pregunta:   ¿dónde vamos y cómo retomar?
tiempo:     vamos aquí
corte:      2026-09-13
verificado: Punto de corte · sin bloqueos
```

> **Léeme primero.** Punto de corte, cómo retomar, y dónde va cada cosa.
>
> Corte: 2026-09-12

---

## Qué es esto

Un **modelo de ERP de construcción verificado contra datos reales** — ocho catálogos
de OPUS 2025 y doce ingenierías de obra. Cada regla se comprobó aritméticamente
antes de escribirse.

**Para:** crear un ERP nuevo, reestructurar los existentes, y darles un idioma común.

---

## Cómo retomar

**Los archivos no persisten entre sesiones.** Hay que volver a subirlos.

**Sube estos siete, en este orden:**

**El cerebro está en carpetas por capa** — `1-mundo`, `2-operacion`,
`3-historia`, `4-direccion`. Ver `INDICE.md`.

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
`agentes/`.

> **Las cuatro capas** — Mundo · Operación · Historia · Dirección — y el bloque de
> `órgano:` de cada encabezado están en `INDICE.md`.

Los catálogos y el artefacto **solo si hace falta verificar algo** — ya están
analizados y sus hallazgos escritos.

> **Antes de proponer cualquier cosa, leer `MEMORIA.md` §2.** Doce ideas razonables
> ya se evaluaron y se rechazaron.

---

## Lo terminado

| Bloque | Estado |
|---|---|
| **Conocimiento** | 15 partes de reglas · `CATALOGOS.md` con los 8 de OPUS · `IDEAS.md` con lo no diseñado |
| **Cadena de costo** | Los 467 conceptos, 89 compuestos y 39 cuadrillas **cuadran al centavo** |
| **Modelo de datos** | `MODELO.md` aprobado, con 6 hallazgos resueltos |
| **Método** | `METODO.md` — cómo se razona, con los errores que lo enseñaron |
| **Lenguaje** | Canon 1.0, tres dialectos, prueba de ida y vuelta ejecutada |
| **Memoria** | 177 decisiones · 12 descartes · 8 correcciones · 11 hallazgos de construcción |
| **Skill** | Base + 3 satélites compilados: importación, rediseño, paramétrico |
| **Agentes** | 🆕 **gravity** orquesta · arquitecto, constructor, migrador, auditor · 🆕 **gravity-obra** interno |
| **Glosario** | 78 términos · 25 ambigüedades |
| **Módulos** | 🆕 Las 16 decisiones de los cuatro cerradas · pendiente diseño formal |
| **Pruebas de flujo** | 🆕 Tres corridas: ALAMO 18, Zafiro 1.0, siete prototipos · 13 pasan, 8 se rompen, 5 sin dato |
| **Invariantes** | 🆕 Las cifras de control, juntas · condición de paro |
| **Capas** | 🆕 Cuatro: Mundo · Operación · Historia · Dirección |
| **Escalabilidad** | 🆕 Contrato de módulo · ERP nuevo y ERP existente |
| **Coherencia** | 🆕 `verificar-cerebro.py` — el cerebro se comprueba solo |
| **Caso trabajado** | Un ejemplo de punta a punta con 12 reglas |
| **Artefacto** | Rehecho con datos verificados: $1,842,430.31 vs $1,842,426.01 |
| **Catálogos corregidos** | Conceptos, materiales, trabajos, mano de obra, fletes |
| **Vocabularios** | Unidades, niveles, etapas, familias — **derivados**, no pedidos |
| **Semilla** | Cuadrilla y rendimiento teórico, 265 filas |
| **Ingenierías de ALAMO 18** | 12 archivos. Las partes se suman; faltan 5 niveles |
| **Reversión por destajo** | **Probada: 84%.** Es el método de carga de la ingeniería |

---

## Lo que sigue, en orden

| # | Qué | Dónde |
|---|---|---|
| 1 | **Montos como `string` en la API** (D-53) | Barato hoy, caro tras generar clientes. `erp-construccion.md` §9 |
| 2 | **Salidas de almacén de ALAMO 18** | Cierra el triángulo: prototipo → ingeniería → **ejecutado**. P-38, objetivo en `CONOCIMIENTO.md` §11.12 |
| 3 | ~~**Las 16 decisiones de los cuatro módulos**~~ ✅ cerradas · quedan P-5, B-40, B-45 | Factorizador primero: el más barato y el que más desbloquea |
| 4 | **Pasar `MODELO.md` a implementación** | Tipos, índices, motor de cálculo. Trabajo del constructor |
| 5 | **Clasificar a mano el 8% de conceptos** sin derivación | El 92% sale del trabajo que usa. **No confundir con el otro 92%**: el de la ingeniería de `ALAMO 18` cubriendo el presupuesto |
| 6 | Los demás pendientes | `PENDIENTES-MEJORAS.md` — 38 de decisión, 14 de datos, 25 módulos |
| 7 | Las ideas del modelo | `IDEAS.md` — seis, sin diseñar |

---

> **El criterio de este orden vive en `PRIORIDADES.md`.** Aquí sólo la cola.

---

## Lo único que bloquea

**Nada.** `MODELO.md` está aprobado, y con él **once módulos tienen sus reglas
escritas y verificadas**: motor de cálculo, catálogo, APU, presupuesto, importación,
semilla, diccionario, rediseño, paramétrico, propuestas.

Los que esperan decisión están identificados: exportación (P-14), estimaciones
(P-18), almacén (P-19), programa y CPM (P-20, P-23), permisos (P-21).

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
