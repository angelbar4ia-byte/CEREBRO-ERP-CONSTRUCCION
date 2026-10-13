# LENGUAJE

```
órgano:     área de Wernicke
capa:       I — Mundo
pregunta:   ¿cómo se nombra en cada sistema?
tiempo:     es así
corte:      2026-09-26
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
| **ERP externo** | 1.0 | B · correspondencia | 🔶 Dos campos de entrada + tres reportes de salida confirmados (`CONOCIMIENTO.md` §4.3, D-331/D-332); falta `Flete`, archivo-vs-API y los 4 catálogos que se volvieron salida |
| **Árbol de ingeniería** | — | — | ⏸️ P-16, no prioritario |

## Antes de la ficha: qué hay que saber de un ERP

La ficha de arriba se llena **con datos en la mano**. Antes hay que contestar siete cosas, y las cinco primeras no las sabe el cerebro: las sabe
quien usa el sistema.

| # | Pregunta | Por qué importa |
|---|---|---|
| 1 | **¿Cuál es y qué guarda?** Nombre, versión, proveedor; presupuesto, almacén, avance, compras, nómina, contabilidad… | Dice a qué parte del canon se parece y qué no tiene equivalente |
| 2 | **¿Quién lo usa y quién manda en él?** | Decide quién aprueba lo que el cerebro proponga ahí |
| 3 | **¿Cómo se llega a sus datos?** Exportación a mano · reporte programado · API · lectura de su base de datos · de ninguna manera | Decide el conector, y con él el stack |
| 4 | **¿Dónde vive?** En la nube del proveedor · en un servidor propio · en una sola computadora | Decide dónde tiene que correr lo que se le conecte |
| 5 | **¿Hasta dónde puede actuar el cerebro ahí?** Los peldaños de abajo | Es la decisión que más riesgo mueve, y es del usuario, ERP por ERP |
| 6 | **Dos o tres archivos o respuestas reales** | Se guardan en el repositorio antes de leerlos (`METODO.md` §2.6): el dialecto sale del dato y no de la documentación |
| 7 | **¿Qué no se toca nunca?** | Entra a `NO_TRADUCIBLE` y a las invariantes |

### Los peldaños de lo que el cerebro hace sobre un ERP

Un ERP sube un peldaño a la vez, con una decisión del usuario por peldaño. Detectar no necesita permiso y corregir sí (`METODO.md` §3.2).

| Peldaño | Qué hace | Lo que protege |
|---|---|---|
| 1 · **Leer** | Carga lo que el ERP exporta o expone; no escribe nada | El ERP no se entera |
| 2 · **Proponer** | Deja una propuesta con evidencia en la bandeja; una persona la aprueba (`CONOCIMIENTO.md` §14) | Nada cambia sin quien decide |
| 3 · **Devolver en su formato** | Entrega un archivo que una persona carga en el ERP (`ESCALABILIDAD.md` §7, paso 5) | El ERP sigue operando y el cerebro no lo secuestra |
| 4 · **Escribir directo** | Por API o por su base de datos, con credencial propia y registro de quién aprobó | **No decidido para ningún ERP.** Un ERP en uso tiene reglas que el cerebro todavía no conoce |

### Dónde están hoy

| ERP | Peldaño | Cómo entra | Qué falta |
|---|---|---|---|
| **OPUS 2025** | 1 | Por archivo; «fuente, nunca destino» (`WORKFLOWS.md` §2.1) | Los cuatro catálogos que no se subieron (`MEMORIA.md` D-472) |
| **ERP externo** | 1, y parte del 3 | Por archivo, y devuelve tres reportes de salida confirmados (`CONOCIMIENTO.md` §4.3). No es ninguno de los cuatro sistemas de abajo ni está en GitHub (el usuario, D-496) | Archivo contra API, `Flete` y los cuatro catálogos de salida |
| **ObraCtrl** (control de obra por avance) | 1, por ahora | Su base es PostgreSQL con RLS en Supabase y su API es FastAPI; repo `CONTROL-AVANCE`. La parte 10 de su especificación define un set de catálogos canónicos. Dónde corre cada parte (API y panel, Render y Vercel) está por confirmar (D-496) | Reconciliar sus catálogos con el canon de aquí; ficha pendiente |
| **Concentrador de estimaciones** | 1, por ahora | Flask con SQLite en la computadora del usuario (puerto 5000); repo `ERP-ESTIMACI-N`, privado. **Su Excel de salida tiene el formato que la app de auditoría sabe leer** (D-505) | Que el usuario confirme su ficha. Sobre los datos reales dentro del repo decidió dejarlos como están (D-506) |
| **Extraordinarios** (subcontratos con órdenes de trabajo) | — | Servidor Node.js en la computadora del usuario, con su propio PostgreSQL, y tres usuarios por la red local; **sin repo propio**: vive en `apps/extraordinarios` de `Multi-erp` desde D-504 | Que el usuario confirme su ficha y diga si un archivo de muestra de respaldo trae datos reales |
| **Control de obra, auditoría** | — | En la computadora del usuario; **sin repo propio**: su carpeta será `apps/auditoria` en `Multi-erp`, todavía vacía (D-496). La carpeta que se revisó (`obra-control`, por confirmar que sea esta) trae un backend con migraciones, un frontend de npm, un lanzador y un PostgreSQL con pgAdmin instalados adentro (D-498; por los nombres de archivo). La herramienta halló el directorio de datos de PostgreSQL en `data/pgdata` de esa misma carpeta: ahí viven las tablas reales (D-499). Esa base corre en el puerto 5433 y tiene 37 tablas con datos y unos 3.3 MB al volcarla (D-501). Su esquema se llama obra; de las 30 primeras tablas que se vieron (faltan 7), estas son las que tocan el dominio del cerebro: concepto, concepto_nuevo, concepto_version, familia_concepto, componente_cpu, estimacion, almacen, movimiento_almacen, motivo_almacen, cuadrilla, contratista, mano_de_obra, material, familia_material, nivel, cluster, etapa_construccion, prefijo_clave, lote_carga, bandeja_pendiente, hallazgo y discrepancia_reg. Solo se conocen los nombres de las tablas, no su contenido ni sus columnas. La especificación de ObraCtrl habla de un «Sistema de Control y Auditoría de Obra» como *Fuente de la Verdad*: parece ser este: su carpeta trae los documentos «FUENTE_DE_LA_VERDAD_Sistema_Control_Obra» y «MODULO_AUDITORIA_ESTIMACION» (D-500), leídos en D-503 | Confirmar con el usuario las preguntas marcadas en su ficha; ya subida a `Multi-erp` (D-503) |

### La ficha de auditoría, con lo que ya se sabe (D-503)

Subida a `Multi-erp` (carpeta `apps/auditoria`, 220 archivos, sin claves ni datos). Las siete preguntas, contestadas con sus propios documentos y con lo que se midió; lo que solo el usuario sabe queda marcado.

| # | Pregunta | Respuesta | De dónde sale |
|---|---|---|---|
| 1 | ¿Cuál es y qué guarda? | «Sistema de Control y Auditoría de Obra» v1.0.0: almacén (movimientos), presupuesto, estimaciones, avance, catálogos y los hallazgos de cruzar lo pagado contra lo que salió de almacén. Su base tiene 37 tablas con datos y pesa unos 3.3 MB al volcarla | su README, la «Fuente de la Verdad» y el volcado (D-501) |
| 2 | ¿Quién lo usa y quién manda? | Un solo operador captura y opera; gerencia lee sin editar. Perfiles `operador` y `gerencia` | la «Fuente de la Verdad» (reglas transversales); **por confirmar** si hoy es así |
| 3 | ¿Cómo se llega a sus datos? | API REST de FastAPI (170 endpoints; su descripción de la API trae 158 rutas), PostgreSQL en el puerto 5433 de esa computadora y cargas por Excel | su README y lo medido en D-501 |
| 4 | ¿Dónde vive? | Una computadora con Windows, sin Docker y sin internet (lanzador por doble clic); gerencia puede leer por la red local | su README y la «Fuente de la Verdad» (infraestructura local) |
| 5 | ¿Hasta dónde puede actuar el cerebro? | **Sin decidir.** La API existe, así que el peldaño 2 (proponer) tiene por dónde entrar; el 4 sigue sin decidirse | del usuario |
| 6 | Ejemplos reales | El volcado de la base (3.3 MB) existe y **no se subió**; siete reportes semanales en PDF quedaron fuera a propósito | el usuario decide si comparte alguno |
| 7 | ¿Qué no se toca nunca? | La estimación pagada es inmutable (los ajustes del cruce se guardan aparte); el sistema propone y la persona decide; los catálogos no los cambia solo | el documento del módulo de auditoría de estimación |

### La ficha de extraordinarios, con lo que ya se sabe (D-504)

Subida a `Multi-erp` (carpeta `apps/extraordinarios`, 36 archivos, sin claves ni datos). Todo sale de su README y de lo que midió la herramienta; **no se ha leído su código**.

| # | Pregunta | Respuesta | De dónde sale |
|---|---|---|---|
| 1 | ¿Cuál es y qué guarda? | «MAGNOLIA · App Web de Gestión»: asignaciones, cotizaciones, órdenes de trabajo (OT) y pagos de subcontratos, con sus anticipos y garantías | su README y los nombres de sus migraciones |
| 2 | ¿Quién lo usa y quién manda? | Tres usuarios con rol: `asignaciones` (asigna contratista a lote y trabajo), `cotizacion` (cotiza y concluye OT) y `pagos` (registra pagos y administra). Hay además un enlace público de solo lectura para gente externa | su README |
| 3 | ¿Cómo se llega a sus datos? | Servidor en el puerto 3000; PostgreSQL propio con su directorio de datos en `.pgdata`; descarga de un respaldo completo en JSON (rol `pagos`) y restauración; exporta e importa Excel; sabe leer el respaldo de su versión anterior | su README y lo medido en la revisión |
| 4 | ¿Dónde vive? | Una computadora con Windows (también Mac y Linux), sin internet una vez instalada; los otros usuarios entran por la IP local de esa computadora | su README |
| 5 | ¿Hasta dónde puede actuar el cerebro? | **Sin decidir.** Con el respaldo en JSON y el Excel ya hay una vía para el peldaño 1 (leer) sin tocar la app | del usuario |
| 6 | Ejemplos reales | En `tests/` quedó un archivo de muestra de respaldo (1.3 KB: 2 OT y 1 pago, de junio de 2026) que **puede traer datos reales**; el usuario debe decir si lo son | pendiente del usuario |
| 7 | ¿Qué no se toca nunca? | **Por contestar.** Por su manual: un número de OT no se duplica (si ya existe, se actualiza) y solo `pagos` administra | su README |

Toca el mismo dominio que el módulo «Control de OT (subcontratos)» de la «Fuente de la Verdad» de auditoría; si las dos apps se relacionan, lo dirá el usuario.

### La ficha del concentrador de estimaciones, con lo que ya se sabe (D-505)

Ya estaba en GitHub (`ERP-ESTIMACI-N`, privado). Todo sale de su README, de la estructura de su base y de la lista de sus rutas; **no se ha leído su lógica de extracción**, y no se leyó el contenido de sus datos.

| # | Pregunta | Respuesta | De dónde sale |
|---|---|---|---|
| 1 | ¿Cuál es y qué guarda? | «Concentrador de Estimaciones de Residentes de Obra»: junta las estimaciones semanales en Excel de los residentes (Obra, Instalaciones y Urbanización), las extrae, normaliza la semana, el lote, el contratista y el residente contra un catálogo con alias, marca alertas (duplicados, nombres no reconocidos) y genera un Excel consolidado. Su base tiene 12,848 renglones de 45 sesiones semanales de 2026 (semanas 1 a 40): 8,449 de Obra, 3,960 de Instalaciones y 439 de Urbanización; 29 contratistas, 13 residentes y 59 alias | su README y la estructura de su base |
| 2 | ¿Quién lo usa y quién manda? | **Por contestar.** No tiene inicio de sesión: quien abre el puerto 5000 entra | la lista de sus rutas |
| 3 | ¿Cómo se llega a sus datos? | API de Flask con unas 35 rutas `/api/...` (catálogos, alias, proyectos, sesiones, registros, alertas, exportar); SQLite en `db/estimaciones.db`; entra por Excel y sale por Excel | su código (rutas) |
| 4 | ¿Dónde vive? | La computadora del usuario; se arranca con un guion de bash (en Windows, con `python app.py`). Corre con el modo de depuración encendido: no debe abrirse a la red | su código |
| 5 | ¿Hasta dónde puede actuar el cerebro? | **Sin decidir.** Ya existe una vía natural para el peldaño 3 (devolver en su formato): el Excel consolidado | del usuario |
| 6 | Ejemplos reales | 330 archivos de Excel dentro del repo (306 subidos y 24 generados) y la base completa. **Son datos reales** y están en GitHub; el usuario decidió dejarlos así (D-506) | lo medido |
| 7 | ¿Qué no se toca nunca? | **Por contestar** | del usuario |

**Un flujo entre dos apps del usuario (D-505).** El Excel que genera el concentrador lleva en la primera fila un título «proyecto · tipo — SEMANA nn — año», en la segunda las cabeceras y los datos desde la tercera, con las 15 primeras columnas que la «Fuente de la Verdad» de auditoría describe para OBRA (SEMANA, CONTRATISTA, RESIDENTE, LOTE/CLUSTER, UBICACIÓN, CLAVE, ACTIVIDAD, UNIDAD, %, CANTIDAD, P.U., TOTAL, OBSERVACIÓN, ⚠, TOTAL CONTRATISTA). Le faltan TOPE, ACUMULADO y X ESTIMAR, que esa fuente dice que no son confiables y que su cargador tolera ausentes. **El formato coincide, y el usuario confirmó (D-506) que carga en auditoría lo que sale del concentrador.**

### Dónde vive cada dato hoy, en las cuatro apps (D-506)

El usuario fijó la dirección de largo plazo (D-506): **unir las apps, o crear una nueva en segundo plano que use lo que ya funciona, sin perder datos**, mientras las actuales siguen operando. Para eso, lo primero es saber dónde está cada dato. Este mapa sale de los nombres de las tablas que crean sus migraciones (y, en auditoría, del volcado de su base); **todavía no baja a las columnas**.

| Dato | Concentrador de estimaciones (8 tablas) | Extraordinarios (8 tablas) | Auditoría (37 tablas) | ObraCtrl (69 tablas) |
|---|---|---|---|---|
| Contratistas | Tabla `contratistas` (29), solo el nombre, con alias | **Texto suelto** en cada asignación, OT y pago; solo hay una tabla de archivos adjuntos por contratista | Tabla `contratista` | Tabla `contratista`, con especialidad y frente |
| Residentes | Tabla `residentes` (13), solo el nombre | No aparece | Tabla `residente` | `residente_obra`, más supervisores y superintendentes |
| Proyecto, cluster, obra o lote, prototipo | `proyectos` (2); el lote es **texto suelto** en cada renglón | El lote es **texto suelto** | Las cuatro: `proyecto`, `cluster`, `obra`, `prototipo` | Las cuatro |
| Conceptos (clave, actividad, unidad) | **Texto suelto** en cada renglón, sin catálogo | El trabajo es texto | `concepto`, con versiones y variantes de análisis de precio | `concepto`, `cpu`, `explosion` e `insumo` |
| Estimación semanal | `registros` (12,848) y `sesiones` (45) | La estimación de un subcontrato es un tipo de pago | `estimacion` y `renglon_estimacion` (previa, revisada, pagada) | `estimacion` y `estimacion_concepto` |
| Órdenes de trabajo y subcontratos | No | `asignaciones`, `cotizaciones`, `ots` y `pagos` | El catálogo `subcontrato` y la hoja EXT de la estimación | El modo de pago «subcontrato» |
| Almacén | No | No | `movimiento_almacen`, `almacen`, `ubicacion`, `motivo_almacen` | `salida_almacen`, `motivo_almacen` |
| Usuarios y roles | Sin inicio de sesión | `users`, con tres roles | Dos cuentas guardadas en `configuracion` | `usuario`, `organizacion` y roles |
| Alias y mapeos | `alias_nombres` (59) | No | `mapeo` y `bandeja_pendiente` | `mapeo` y `pendiente` |
| Bitácora | No | `asignaciones_historial` | `bitacora` | `bitacora` |
| Cargas | `sesiones` | No | `lote_carga` y `periodo` | `carga_datos` y `carga_snapshot` |

**Lo que muestra:**
1. **Las listas maestras —contratistas, residentes, obras— viven por separado en las cuatro apps**, y en dos de ellas como texto suelto sin identificador. Ese texto suelto es lo más difícil de unir; las listas maestras son lo primero que habría que unificar.
2. **Auditoría y ObraCtrl comparten casi todo el vocabulario** (mapeo, motivo de almacén, cluster, prototipo, cuadrilla, grupo funcional), lo que confirma D-503: ObraCtrl se adaptó de la «Fuente de la Verdad».
3. **La base viva de auditoría no coincide del todo con sus migraciones:** el volcado trae `concepto_version` y sus migraciones crean `version_cpu`. Cualquier traslado de datos debe partir de la base real (su respaldo), no de las migraciones ni de los documentos.

**Cómo se uniría sin perder datos — propuesta, no decisión (D-506):**
1. Las apps actuales siguen operando. No se apaga ninguna hasta que la nueva reproduzca lo que hace, medido con la prueba de ida y vuelta de este archivo.
2. Primero se une el dato, no la pantalla: listas maestras únicas y un diccionario de equivalencias entre los nombres.
3. Se copia, no se mueve: cada app conserva sus datos y su respaldo, y el dato unificado guarda de qué app y de qué fila viene.
4. Una pieza a la vez, empezando por el flujo que ya existe: concentrador, Excel consolidado, auditoría.
5. Por los peldaños de arriba (leer, proponer, devolver en su formato y solo al final escribir directo), con decisión del usuario en el cuarto.
6. Cada traslado parte de la base viva y de su respaldo.

Qué base tendría la app nueva (¿ObraCtrl?, ¿otra?) **no está decidido**; se decide después de reconciliar los cánones (B-105).

### Los cánones contra la «Fuente de la Verdad» — primera pasada (D-503)

La especificación de ObraCtrl declara que su glosario, sus reglas transversales y su diccionario son una **adaptación** de la «Fuente de la Verdad» (su parte 10 la llama «producto hermano»). Entonces los tres cánones no son tres: son **la «Fuente de la Verdad» con su adaptación de ObraCtrl, y el de este cerebro**. Se leyó el documento completo de reglas, catálogos y diccionario; faltan las cabeceras por archivo y los módulos 5 a 8.

| Tema | «Fuente de la Verdad» y ObraCtrl | Este cerebro | Veredicto |
|---|---|---|---|
| Principio rector | El sistema propone, la persona confirma; lo dudoso va a una bandeja única | Propuestas con evidencia y bandeja (D-485) | ✅ coincide |
| Signo de los movimientos de almacén | Viene en `Efecto Qty` y `Efecto Costo` del archivo | `cantidad` con signo, mismo origen | ✅ coincide |
| Motivos de almacén | 9 motivos canónicos | 10: agrega `reversion_movimiento_erroneo`, que apareció en cinco meses de datos reales | 🔶 difiere: la «Fuente» dice que la lista es extensible; falta darlo de alta allá |
| Origen de la estimación | El prefijo `E-` del folio marca que salió del ERP | `fuente` ∈ erp_externo · manual (D-284) | ✅ misma idea, forma distinta |
| Estados de la estimación | previa · revisada · pagada | capturada · devuelta · validada · pagada; ObraCtrl: borrador · enviada · validada (otra entidad, la de campo) | ⏸️ tres vocabularios; la equivalencia la decide el usuario |
| Prefijos de mano de obra | `MOA` y `MOS` | En los CSV del repo: MOA 85 · MOE 78 · MOS 46 · MOH 23 · MOG 17 · MOC 8 · MOP 7 · MOO 1 claves distintas | 🔶 difiere: faltan seis en la lista de la «Fuente»; la tabla viva de la app (`prefijo_clave`) puede traerlos |
| Semana | Ordinaria (lun–dom) y de obra (jue–mié, 5 días laborales), con selector por reporte | Pregunta abierta: con cuál se cortan los baldes del programa | ✅ la «Fuente» la contesta: las dos, a elección por reporte |
| Roles | `operador` y `gerencia` (un eje distinto: operar o leer) | residente · supervisor · superintendente · costos · cotizador · control de obra; ObraCtrl: residente · supervisor · control de obra · superintendente | ⏸️ tres conjuntos; ObraCtrl y el cerebro comparten cuatro |
| Jerarquía de fuentes | Catálogos mandan; entre datos cargados, almacén gana a estimación | No está escrita | ⏸️ solo en uno; decidir si entra al canon |
| Folio de la estimación | `[E-]SSAA-NNN` (semana, año, consecutivo) | No lo tiene: su «folio» es el de la orden de producción | ⏸️ solo en uno |
| Parámetros del negocio | IVA 16 % (exentos pétreos y jardinería), umbral ±5 % de consumo, similitud 90 %, razón material/mano de obra ~60 % | No los tiene; su `umbral_pct` es de otra cosa (identidad dudosa) | ⏸️ solo en uno |

> Primera pasada: cada fila se verificó contra el texto o contra los CSV del repo, pero no se leyeron las cabeceras por archivo ni los módulos 5 a 8, y no se ha visto el código de la app. Nada de esto cambia un canon todavía: son diferencias a decidir (B-105).

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
