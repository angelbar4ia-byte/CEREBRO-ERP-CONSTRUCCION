# LENGUAJE

```
órgano:     área de Wernicke
capa:       I — Mundo
pregunta:   ¿cómo se nombra en cada sistema?
tiempo:     es así
corte:      2026-09-10
verificado: Canon 1.0 · prueba de ida y vuelta ejecutada
```

> **Este archivo dice cómo se nombra cada cosa. No dice cómo funciona.**
> El comportamiento vive en `CONOCIMIENTO.md`; aquí solo el nombre y su traducción.
>
> Canon versión **1.0** · 2026-09-10

---

## Para qué existe

Cada ERP habla su dialecto. Sin un canon, unir dos sistemas obliga a traducir
A↔B, y con cada sistema nuevo el trabajo se multiplica.

```
SIN CANON              CON CANON

A ↔ B                       A
A ↔ C                       ↓
B ↔ C                  ┌── CANON ──┐
A ↔ D  …               B     C     D
```

**El canon es el idioma; cada ERP es un dialecto.** Un agente aprende el canon una
vez y traduce cualquier dialecto contra él.

---

## Las tres reglas del traductor

### 1. Se traduce por significado, no por nombre

> **La pregunta es qué responde el campo, no cómo se llama.**

Es la trampa más peligrosa, y OPUS la tiene tres veces:

| El nombre | En materiales significa | En trabajos | En mano de obra |
|---|---|---|---|
| `Familia` | la **sustancia** | el **oficio** | el **rango** |

Un traductor que empareje por nombre produce datos que **cuadran y mienten**.

### 2. Un nombre puede significar varias cosas en el mismo sistema

En el catálogo de trabajos hay **dos columnas llamadas `Tipo`**: una es la clase
(destajo/subcontrato) y la otra la categoría. **El alias no basta: hay que leer por
posición.**

### 3. Lo intraducible se declara, no se inventa

Cuando algo no tiene equivalente, el traductor **lo dice**. Nunca fabrica un campo
para que encaje.

---

## El canon

Semántico, no físico: **dice qué pregunta responde cada campo**, no cómo se llama la
tabla. El esquema concreto es otra cosa y nace del arquitecto.

### Identidad

| Campo | Pregunta que responde |
|---|---|
| `id` | ¿Cuál es este registro, para siempre? Interno, nunca se muestra |
| `clave` | ¿Cómo lo nombra el negocio? Nunca se reescribe |
| `clave_usuario` | ¿Tiene un código alterno propio del usuario? |

### Qué es

| Campo | Valores |
|---|---|
| `rol` | ensamble · concepto · insumo |
| `categoria` | material · mano de obra · herramienta · equipo · auxiliar · flete · trabajo |
| `clase` | destajo · subcontrato · acarreo *(solo dentro de trabajo)* |
| `es_compuesto` | sí / no — ¿tiene desglose propio? |

### Cómo se clasifica

| Campo | Pregunta |
|---|---|
| `familia` | ¿De qué naturaleza es? |
| `subfamilia` | ¿Qué elemento o pieza es? |

### Cuánto y cuánto cuesta

| Campo | Pregunta |
|---|---|
| `unidad` | ¿En qué se mide? |
| `cantidad` | ¿Cuánto? |
| `precio` | ¿Cuánto cuesta la unidad? |
| `importe` | `cantidad × precio` |
| `moneda` · `vigencia` | ¿En qué moneda y desde cuándo? |

### Cómo se obtuvo

| Campo | Valores |
|---|---|
| `modo_precio` | calculado · declarado |
| `modo_cantidad` | medida · estimada · capturada · heredada |
| `procedencia` | importado · manual · fusión · división · extracción · composición · clonación |
| `reporta_a` | la categoría a la que suma el monto |

### Dónde está en el árbol

| Campo | Pregunta |
|---|---|
| `padre` | ¿De quién cuelga? |
| `orden` | ¿En qué posición dentro de su padre? |
| `profundidad` | ¿A qué nivel del árbol? |
| `ruta` | La ruta calculada, con puntos. **Presentación, no identidad** |

---

## Dialecto: OPUS 2025

**El mapeo es por archivo, no por sistema.** El mismo campo canónico cambia de
nombre entre exports del mismo OPUS.

### Catálogos de insumo — materiales, trabajos, fletes, mano de obra

| Canon | OPUS | Nota |
|---|---|---|
| `clave` | `Clave` | |
| `clave_usuario` | `Clave usuario` | Solo en trabajos |
| `descripcion` | `Descripción` | |
| `es_compuesto` | `C` | `+` si se abre |
| `unidad` | `Unidad` | |
| `precio` | `Costo unitario` | |
| `moneda` | `Costo base M. N.` / `M. E.` | M.E. en cero en todos |
| `vigencia` | `Fecha` | |
| `familia` | `Familia` | **Significado distinto por catálogo** |
| `subfamilia` | `Subfamilia` | |
| `categoria` | `Tipo` *(última columna)* | Material · Trabajo · Mano de Obra · Flete |
| `clase` | `Tipo` *(segunda columna)* | **Solo trabajos. Homónima — leer por posición** |
| — | `Comentarios` | Un número, sin uso. **No se traduce** |

### Presupuesto

| Canon | OPUS | Nota |
|---|---|---|
| `profundidad` | `Nivel ` | Con espacio final |
| `orden` | `Indice` | |
| `clave` | `Clave` | |
| `descripcion` | `Descripción` · `Descripcion Corta` · `Descripción de matriz` | Tres columnas |
| `unidad` | `Unidad` · `Unidad de matriz` | Dos |
| `cantidad` | `Cantidad` | **El único dato propio del presupuesto** |
| `precio` | `Precio unitario` | **Señal, no dato** |
| `importe` | `Total` | Derivado |
| `rol` | `Tipo` | Capítulo · Subcapítulo · Nivel 2 · Nivel 3 · Concepto |
| — | `%` | Derivado. No se traduce |
| — | `Ingenieria ERP` · `Nivel ERP` | **Del otro ERP.** Ver abajo |
| — | `Origen` | Aquí vale `Presupuesto`: es el informe, no el dato |
| — | `Ruta paramétrica` | Vacía |

### Análisis de básicos — la explosión

| Canon | OPUS | Nota |
|---|---|---|
| `padre` | `Clave Padre` | |
| `clave` del hijo | `Clave Hijo` | |
| `cantidad` | `Cantidad` | |
| `precio` | `Costo` | **En líneas `%MO` no es precio: es la base** |
| `importe` | `Importe` | |
| `categoria` del hijo | `Tipo` | La naturaleza — **el ADN** |
| `reporta_a` | `Origen` | La categoría del padre — **el monto** |

> Estas dos últimas son las dos lecturas del árbol. **OPUS ya las separa.**

---

## Dialecto: el ERP externo

Sistema sobre el que **no hay control**. Sus columnas pueden venir truncas o cambiar
de formato.

| Canon | ERP externo | Nota |
|---|---|---|
| `ruta` | `Ingenieria ERP` | Numérico, ancho fijo. **No se importa — y tampoco se puede generar**: la regla no es deducible (`CATALOGOS.md` §11) |
| nivel de construcción | `Nivel ERP` | Llave al catálogo de niveles |

**Reportes de salida:** Cabeceras · Materiales · Operaciones. Columnas
confirmadas contra especímenes reales de `ALAMO 18` — `CONOCIMIENTO.md` §4.3.
Cabeceras reutiliza estas mismas dos columnas de esta tabla (`Nivel ERP` e
`Ingenieria ERP`).

---

## Qué no se traduce

### De OPUS al canon

| Qué | Por qué |
|---|---|
| Desglose del FSR — 20 columnas | Calculado y no aplicado. **No se carga** |
| `Comentarios` | Un número sin significado conocido |
| `Ruta paramétrica` | Vacía. El paramétrico se construye aquí |
| `Total`, `%` | Derivados |
| `Ingenieria ERP`, `Nivel ERP` | Formato del ERP externo |

### Del canon a OPUS

Lo que **OPUS no tiene y se perdería** al exportar:

| Qué | Dónde vive |
|---|---|
| `procedencia` | Distingue lo cargado de lo rediseñado |
| `modo_cantidad` | Medida contra estimada |
| `modo_precio` | Ascendente contra descendente |
| Ensambles y paramétrico | No existen en OPUS |
| Las tres capas del rediseño | No existen |
| `id` inmutable | OPUS identifica por clave |

> **El traductor debe reportar esta pérdida**, no ignorarla.

---

## La prueba de ida y vuelta

Un idioma se valida retraduciendo:

```
OPUS  →  canon  →  OPUS
```

**Debe devolver el mismo archivo.** Si no vuelve igual, la traducción perdió algo, y
la diferencia dice exactamente qué.

> **Renombrar columnas y devolverlas no prueba nada.** Hay que **reconstruir lo
> derivable desde el canon**, sin copiarlo del original.

### Ejecutada el 2026-09-10

| Columna | Resultado |
|---|---|
| `Total` | ✅ 3,224 de 3,231 · máx. $0.03 |
| `%` | ✅ exacto |
| `Ingenieria ERP` | ❌ **no generable** |

**El canon aguanta**: con clave, cantidad, precio y profundidad se reconstruye todo
el aparato numérico. Y la prueba **encontró un error**: la regla del código
documentada era incompleta.

> Se compara **solo lo traducible**: lo declarado en «Qué no se traduce» queda fuera
> de la prueba por diseño.

---

## Cómo se declara un dialecto

Cada ERP que se conecta declara **una ficha**. Con eso, agregar un sistema nuevo es
escribir una tabla — no rehacer nada.

```
DIALECTO
  nombre              OPUS 2025
  version_canon       1.0
  forma_de_conexion   A · alineado   |   B · correspondencia
  fecha_de_conexion   2026-09-10

MAPEO            por archivo, no por sistema
  campo_canon  ←  columna         nota
  ...                             homónimas → leer por posición

NO_TRADUCIBLE
  de_entrada   qué trae y no se importa
  de_salida    qué del canon se perdería al exportar

PRUEBA
  ida_y_vuelta  qué columnas se reconstruyen, y con qué resultado
```

> **Es la prueba de si el canon sirve:** si conectar un sistema nuevo es llenar esta
> ficha y nada más, funcionó.

### Los dialectos declarados

| Dialecto | Canon | Conexión | Estado |
|---|---|---|---|
| **OPUS 2025** | 1.0 | Fuente | ✅ Mapeado y probado |
| **ERP externo** | 1.0 | B · correspondencia | ⏸️ Solo dos campos conocidos |
| **Árbol de ingeniería** | — | — | ⏸️ P-16, no prioritario |

---

## Versión del canon

El canon va a cambiar. Cada ERP quedará hablando la versión con que se conectó.

- Cada dialecto declara **contra qué versión mapea**.
- Un cambio que **agrega** campo es menor: los dialectos viejos siguen funcionando.
- Un cambio que **renombra o resignifica** es mayor: obliga a revisar cada dialecto.

---

## Identidad compartida

> **Hablar el mismo idioma no une los datos.**

Si dos ERP hablan el canon pero cada uno tiene sus claves, *muro de tabique* aquí y
allá siguen siendo **dos cosas distintas**. El idioma traduce las palabras; no dice
que nombren lo mismo.

### El nuevo ERP es la identidad

No elige entre las opciones de abajo: **él es la clave neutra**. Las tres opciones
son **cómo se conecta cada sistema a él**.

### Tres formas de conectar — y no se eligen por gusto

| Forma | Cuándo | Qué pasa con sus claves |
|---|---|---|
| **A · Se alinea** | Sistema nuevo o con poco cargado | Adopta las claves del canon |
| **B · Correspondencia** | Sistema ya alimentado | Conserva las suyas; se mantiene una tabla de equivalencia |
| **C · Clave neutra** | El ERP nuevo | Es la referencia contra la que todos apuntan |

### La regla que decide

> **¿Cuántas referencias vivas tiene ese ERP a sus propias claves?**
>
> Ninguna o pocas → **A**. Muchas → **B**.

Es la misma regla de la dependencia que gobierna todo el modelo: *mientras nada
dependa de un dato, se corrige; en cuanto algo depende, se agrega encima*.

**Y el sistema puede contar esas referencias.** No es un juicio.

### Se pasa de A a B, nunca al revés

Un ERP vacío hoy se alinea; en dos años tiene historia y **ya no se puede
realinear**.

> El momento de decidir es **al conectarlo**, y esa decisión queda registrada junto
> al dialecto.

### El caso mixto es el normal

El ERP externo tiene el catálogo viejo alimentado —92 cuadrillas, 170 claves
`MOOP`— pero **ese mismo catálogo ahora se genera desde OPUS**.

```
Lo que ya tiene historia   → B · correspondencia
Lo que llegue nuevo        → A · alineado
```

Las dos formas conviven **en el mismo sistema y hasta en el mismo catálogo**.

### El tamaño real del trabajo

Medido entre las claves `MOOP` del catálogo anterior y las `MOCA` vigentes:

| | Claves |
|---|---|
| Coinciden exacto por descripción | 23 |
| Coinciden aproximado —**no confiable**— | 8 |
| **Sin equivalente** | 47 |
| Nuevas, que no existían antes | 30 |

> Y las aproximadas engañan: *Ayudante de soldador* y *Ayudante de pintor* cayeron
> las dos en la misma clave. **El emparejamiento por texto no alcanza.**

Ninguna de las tres formas evita ese trabajo. **Solo cambia dónde vive el
resultado**: en las claves del sistema, o en una tabla de correspondencia.
