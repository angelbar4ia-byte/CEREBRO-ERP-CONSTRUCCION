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
| **ObraCtrl** (control de obra por avance) | 1, por ahora | Su base es PostgreSQL con RLS en Supabase y su API es FastAPI; repo `CONTROL-AVANCE`. La parte 10 de su especificación define un set de catálogos canónicos. Dónde corre (D-508): **el panel está en Vercel**, en `control-avance-chi.vercel.app` (la dirección la dio el usuario como la del panel, y así resolvió la duda de D-507; desde esta sesión no se puede abrir porque la red lo bloquea, así que no se vio qué sirve); según su documentación la API y un proceso de fondo están en Render, la base y el acceso en Supabase y los archivos en R2. La dirección de la API no se ha visto. **Es la app que más le importa al usuario** y se queda funcionando por ahora (D-508) | Reconciliar sus catálogos con el canon de aquí; su ficha y sus campos contra el cerebro están en D-513 |
| **Concentrador de estimaciones** | 1, por ahora | Flask con SQLite en la computadora del usuario (puerto 5000); repo `ERP-ESTIMACI-N`, privado. **Su Excel de salida tiene el formato que la app de auditoría sabe leer** (D-505) | Que el usuario confirme su ficha. Sobre los datos reales dentro del repo decidió dejarlos como están (D-506) |
| **Extraordinarios** (subcontratos con órdenes de trabajo) | — | Servidor Node.js en la computadora del usuario, con su propio PostgreSQL, y tres usuarios por la red local; **sin repo propio**: vive en `apps/extraordinarios` de `Multi-erp` desde D-504. **Se queda funcionando como está** y su código se leyó para anotar cómo trabaja (D-508) | Que el usuario confirme su ficha y diga si un archivo de muestra de respaldo trae datos reales |
| **Control de obra, auditoría** | — | En la computadora del usuario; **sin repo propio**: vive en `apps/auditoria` de `Multi-erp` desde D-503. La carpeta que se revisó (`obra-control`, por confirmar que sea esta) trae un backend con migraciones, un frontend de npm, un lanzador y un PostgreSQL con pgAdmin instalados adentro (D-498; por los nombres de archivo). La herramienta halló el directorio de datos de PostgreSQL en `data/pgdata` de esa misma carpeta: ahí viven las tablas reales (D-499). Esa base corre en el puerto 5433 y tiene 37 tablas con datos y unos 3.3 MB al volcarla (D-501). Su esquema se llama obra; de las 30 primeras tablas que se vieron (faltan 7), estas son las que tocan el dominio del cerebro: concepto, concepto_nuevo, concepto_version, familia_concepto, componente_cpu, estimacion, almacen, movimiento_almacen, motivo_almacen, cuadrilla, contratista, mano_de_obra, material, familia_material, nivel, cluster, etapa_construccion, prefijo_clave, lote_carga, bandeja_pendiente, hallazgo y discrepancia_reg. Solo se conocen los nombres de las tablas, no su contenido ni sus columnas. La especificación de ObraCtrl habla de un «Sistema de Control y Auditoría de Obra» como *Fuente de la Verdad*: parece ser este: su carpeta trae los documentos «FUENTE_DE_LA_VERDAD_Sistema_Control_Obra» y «MODULO_AUDITORIA_ESTIMACION» (D-500), leídos en D-503 | Confirmar con el usuario las preguntas marcadas en su ficha; ya subida a `Multi-erp` (D-503) |

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

Subida a `Multi-erp` (carpeta `apps/extraordinarios`, 36 archivos, sin claves ni datos). *El usuario dice que lo que maneja se llama **subcontrato** y que «extraordinario» solo describe lo que queda fuera del presupuesto (D-511); el nombre de la app y de su carpeta se conserva hasta que él pida cambiarlo.* Las siete preguntas salen de su README y de lo que midió la herramienta; **su código se leyó después y está en la sección siguiente (D-508)**.

| # | Pregunta | Respuesta | De dónde sale |
|---|---|---|---|
| 1 | ¿Cuál es y qué guarda? | «MAGNOLIA · App Web de Gestión»: asignaciones, cotizaciones, órdenes de trabajo (OT) y pagos de subcontratos, con sus anticipos y garantías | su README y los nombres de sus migraciones |
| 2 | ¿Quién lo usa y quién manda? | Tres usuarios con rol: `asignaciones` (asigna contratista a lote y trabajo), `cotizacion` (cotiza y concluye OT) y `pagos` (registra pagos y administra). Hay además un enlace público de solo lectura para gente externa | su README |
| 3 | ¿Cómo se llega a sus datos? | Servidor en el puerto 3000; PostgreSQL propio con su directorio de datos en `.pgdata`; descarga de un respaldo en JSON (rol `pagos`) y restauración —**que no incluye los archivos adjuntos de los contratistas ni los enlaces públicos**, solo seis tablas (D-507)—; exporta e importa Excel; sabe leer el respaldo de su versión anterior | su README y lo medido en la revisión |
| 4 | ¿Dónde vive? | Una computadora con Windows (también Mac y Linux), sin internet una vez instalada; los otros usuarios entran por la IP local de esa computadora | su README |
| 5 | ¿Hasta dónde puede actuar el cerebro? | **Sin decidir.** Con el respaldo en JSON y el Excel ya hay una vía para el peldaño 1 (leer) sin tocar la app | del usuario |
| 6 | Ejemplos reales | En `tests/` quedó un archivo de muestra de respaldo (1.3 KB: 2 OT y 1 pago, de junio de 2026) que **puede traer datos reales**; el usuario debe decir si lo son | pendiente del usuario |
| 7 | ¿Qué no se toca nunca? | **Por contestar.** Por su manual: un número de OT no se duplica (si ya existe, se actualiza) y solo `pagos` administra | su README |

Toca el mismo dominio que el módulo «Control de OT (subcontratos)» de la «Fuente de la Verdad» de auditoría; si las dos apps se relacionan, lo dirá el usuario.

### Cómo funciona extraordinarios hoy, leído en su código (D-508)

El usuario decidió que la app **se queda funcionando como está** y que el cerebro **anota cómo trabaja hoy para aprenderlo** (D-508). Esto sale de leer su código en `Multi-erp/apps/extraordinarios`: las rutas del servidor, el esquema (seis migraciones) y la lógica de la pantalla de pagos. **No se ejecutó la app ni se vieron sus datos**: describe lo que el código hace, no lo que la base contiene. Y el código no es una especificación: lo que parece un descuido se anota como observación, no como regla.

**El recorrido de una OT (orden de trabajo).**

| Paso | Quién (rol) | Qué hace el código | Qué queda guardado |
|---|---|---|---|
| 1. Asignar | `ASIGNACION` | Crea una asignación: lote, modelo, tipo de trabajo, contratista, descripción y observaciones, en estatus `PENDIENTE`. El lote se normaliza a «NOMBRE NN» más letra opcional, en mayúsculas y con el número a dos dígitos («fresno 3» queda «FRESNO 03»). Puede anotar un monto provisional y **planear un anticipo** (semana, año y clase) | `asignaciones` |
| 2. Reasignar o editar | `ASIGNACION` | Cambiar el contratista deja una fila de historial (anterior, nuevo, quién, cuándo); editar una asignación que ya tiene OT mueve también la OT; cancelar una pendiente la borra | `asignaciones_historial` |
| 3. Cotizar | `COTIZACION` | Desde una asignación pendiente, o **directa** sin asignación previa (entonces crea la asignación ya cotizada). Captura partidas (descripción, unidad, cantidad, precio unitario); solo cuentan las que tienen descripción, cantidad mayor a cero y precio mayor a cero, y sin ninguna válida no se genera (se valida en el servidor, no solo en pantalla). Subtotal = suma de cantidad × precio; IVA = subtotal × el porcentaje que mande la pantalla (el servidor no fija 16 %: si no llega nada, es 0); total = subtotal + IVA | `cotizaciones` (partidas como JSON) y **la OT** |
| 4. Numerar la OT | — | Consecutivo global y único (`ot_numero`). La pantalla sugiere el siguiente sin consumirlo y el usuario puede escribir otro que no exista; la secuencia se adelanta para no chocar después. Tipo de contrato por defecto `PRESUPUESTO`; el monto de la OT es el total cotizado | `ots` |
| 5. Concluir | `COTIZACION` | La OT pasa a `CONCLUIDA`, en un solo sentido (no vi ruta para reabrirla). El estatus `CANCELADA` existe en el esquema, pero **no vi ruta que lo ponga**; el usuario dice que sí se cancelan, aunque lo común es reasignar (D-509), y la lista de tipos de contrato trae `CANCELADO` (¿es así como se hace hoy?) | `ots.estatus` |
| 6. Pagar | `ADMIN` («pagos») | Registra renglones de pago por OT (tabla siguiente). Un anticipo planeado en el paso 1 aparece como **borrador sin confirmar**, con monto 0, hasta que el administrador lo captura y lo confirma | `pagos` |
| 7. Ver | todos | Resumen por lote o por contratista (contratado, pagado, por pagar y porcentaje); la OT en PDF con su resumen de pagos; la lista «Estimación» (pagos de clase estimación por semana, con casillas, subtotales por tipo y por contratista, y salida a Excel); y un enlace público de solo lectura con token | — |

**El renglón de pago, campo por campo.**

| Campo | Qué es |
|---|---|
| `clase` | `ESTIMACION` · `CUENTA` (pago a cuenta, «fuera de estimación») · `TRANSFERENCIA`. **Una OT puede pagarse dentro de la estimación o fuera de ella** |
| `tipo` | `ANTICIPO · AVANCE · FINIQUITO · GARANTIA · PAGO UNICO · DESCUENTO` |
| `ppto` | La base del cálculo; se llena con el monto de la OT |
| `pct` y `monto` | Se escribe uno y el otro se deriva: monto = ppto × pct / 100, o pct = monto / ppto × 100 |
| `garantia` | **5 % del presupuesto**, fijo en la pantalla; se guarda con cada renglón y es informativo: **no se resta del monto**. El usuario confirmó que es una retención que se devuelve y que **no aplica a todos los contratistas** (D-509); la pantalla la calcula siempre y no distingue |
| `anticipo`, `avance`, `finiquito`, `pago_unico` | El mismo `monto`, repetido en la columna que corresponde al tipo (las otras quedan vacías); sirven para el Excel de salida |
| `descuento` | Un número capturado aparte; **no se resta del monto ni entra en el saldo**; solo sale en el Excel. No guarda de qué tipo es: los tipos que el usuario nombró están en la sección siguiente (D-509) |
| `por_pagar` | Del renglón: ppto − monto. No es el saldo acumulado de la OT |
| `confirmado` | Falso en los borradores; guardar o editar un pago lo confirma; confirmar exige monto mayor a cero |

**El saldo de una OT** es su monto (o, si no lo tiene, el mayor `ppto` visto en sus pagos) menos la suma del `monto` de sus renglones **confirmados**, de cualquier tipo y sumado tal cual. Ningún cálculo resta `garantia` ni `descuento`: los dos se guardan para el Excel, no para el saldo. Si el usuario los usa para retener o descontar de verdad, esa regla vive fuera del código.

**Otras reglas que el código impone.** El número de OT es único y la importación desde Excel actualiza si ya existe, nunca duplica. Una OT se busca siempre por su identificador interno y no por su número (un error anterior mostraba la OT equivocada). El reflejo de un anticipo planeado nunca toca un pago ya confirmado. Los permisos: `ASIGNACION` tiene las pestañas de asignaciones y resumen, y es el único (con `ADMIN`) que sube y borra archivos de contratistas; `COTIZACION` tiene cotizaciones, OT y resumen; `ADMIN` tiene todas y además da de alta y borra OT, importa Excel, administra usuarios, descarga y restaura respaldos y genera el enlace público.

**Dos cosas más que conviene saber.** Los archivos de contratistas (PDF, Excel, JPG o PNG, hasta 20 MB y diez a la vez) se guardan **dentro de la base**, ligados a un contratista y, si se quiere, a un lote y una asignación. Y **el contratista y el lote son texto libre en todas las tablas**: no hay catálogo de contratistas ni de lotes, así que el mismo contratista puede aparecer con distintas grafías entre una OT y otra (el lote sí se normaliza al escribirlo; el contratista no).

**Contra el cerebro** (no cambia nada del canon; es para aprender):

| Tema | Extraordinarios hoy | El cerebro hoy | Lectura |
|---|---|---|---|
| Asignar contratista a lote y trabajo | `asignaciones` y su historial; el contratista es texto. **Reasignar es lo común** (D-509) | `ASIGNACION_CONTRATISTA`: alcance, vigencias, motivo y cadena de reemplazos (`reemplaza_id`) | El cerebro la cubre; falta el anticipo planeado que cuelga de ella |
| Cotización y OT | Partidas libres (sin clave de catálogo) y un número de OT consecutivo | La OT no existe. Sí existen el **highlight** y el **adicional** (D-280, `MODELO.md` §5b), foliados y vueltos control de cambio al aprobarse (`CONOCIMIENTO.md` §13.4) | La OT es **el contrato informal con el contratista** para ejecutar un subcontrato (D-511). Se contrata después de la venta: de un presupuesto o de un control de cambio. Cuando es un cambio del cliente, nace de la cotización del contratista tras un highlight cotizado al cliente; cuando es el subcontrato base, no. La app no guarda de dónde viene |
| Descuentos y retenciones | `garantia` (5 %) y `descuento` guardados sin restarse | `DEDUCCION` (sobrepago, rehacer trabajo), `RETENCION` (solo subcontratos, D-290) y `PRESTAMO` | El cerebro **ya tiene** el mecanismo. La garantía de 5 % **sí es una retención** que se devuelve y no aplica a todos (D-509); faltan quiénes la llevan y cuándo se devuelve. Los descuentos de calidad y cumplimiento (siete tipos, D-509) no caben aún en `DEDUCCION` |
| Anticipo, finiquito, pago único | Tipos de pago por OT | No existen | Dominio que el cerebro no modela |
| Estimación o fuera de ella | `clase` del pago: estimación, a cuenta, transferencia | `ESTIMACION.fuente` (ERP externo o manual) es otra cosa | No son el mismo eje |
| Ver lo pagado | Resumen por lote o contratista; enlace público | Reporte «Real contra Base» (D-313) | Parecido en espíritu, otro nivel de detalle |

**Lo que el usuario contestó sobre extraordinarios (D-509).** Las cuatro preguntas de D-508, con lo que implica cada respuesta.

| Pregunta | Respuesta del usuario | Qué implica |
|---|---|---|
| ¿La garantía de 5 % es una retención que se devuelve? | «Sí, no aplica para todos los contratistas» | Es una retención, pero **qué contratistas la llevan no está en la app**: la pantalla la calcula siempre al 5 % de la OT. En el cerebro `RETENCION` aplica solo a subcontratos (D-290); queda por confirmar si «los que la llevan» son ellos, y cuándo se devuelve |
| ¿Cómo se captura un descuento? | «No está definido» en la app, pero **hay siete tipos** (lista siguiente) | Hoy el descuento es un número sin tipo ni responsable. Los tipos que el usuario nombró son lo que le falta |
| ¿Una OT es siempre un adicional al contrato original? | «No siempre; de hecho se tiene que renombrar **extraordinario por subcontrato**» *(D-511: el usuario aclaró que el nombre correcto es «subcontrato»; «extraordinario» sería «fuera del presupuesto»)*. Los subcontratos están en el presupuesto; el cliente puede modificar su alcance o rediseñarlos, y a eso se le llama **highlight**, ya definido y cotizado al cliente; con la cotización del contratista se crea la OT | Ver la cadena abajo. El glosario ya trae *Highlight* y *Orden de trabajo (OT)* (D-509 y D-511) |
| ¿Hay OT canceladas? | «Sí se pueden cancelar, pero es más común reasignar» | El camino común (reasignar) ya está cubierto por `ASIGNACION_CONTRATISTA`; para cancelar hay que decidir cómo se registra (¿estado de la OT?) |

**Los tipos de descuento, con las palabras del usuario.** Son siete frases separadas por comas; no se sabe si «mal trabajo» es el paraguas de las demás.

| # | Tipo | En el cerebro |
|---|---|---|
| 1 | Mal trabajo | No está como tipo. ¿Es lo mismo que el 4? |
| 2 | Mal trabajo: **otro contratista realiza la reparación de la misma actividad** | Es `rehacer_trabajo` (D-289): se descuenta al responsable si sigue activo; si ya no, la empresa absorbe |
| 3 | La misma actividad quedó **no terminada** | No está |
| 4 | La misma actividad, **de mala calidad** | No está |
| 5 | **Afectación a otros trabajos** | No está |
| 6 | **Abandono de trabajo** | No está |
| 7 | **Pagado a otro contratista** | No está. ¿Es el monto de lo que costó repararlo o terminarlo? |

Hoy el cerebro solo tiene dos tipos de `DEDUCCION`: `sobrepago` (se pagó de más por precio) y `rehacer_trabajo`. Los siete de arriba pertenecen a otra familia, **la de calidad y cumplimiento**, y la lista cabe como valores nuevos de `tipo`; **es una propuesta, no cambia `MODELO.md` hasta que el usuario confirme la lista y su estructura** (B-110).

**La cadena que el usuario describió, puesta en los términos del cerebro:**

1. El cliente pide modificar el alcance o rediseñar un subcontrato que está en el presupuesto.
2. Se le entrega un **highlight** cotizado (se folia; al aprobarse es control de cambio, D-280 y `CONOCIMIENTO.md` §13.4).
3. El contratista cotiza ese cambio.
4. Con esa cotización nace la **OT**: el contrato informal con el contratista (D-511).

Lo que la app hace hoy es solo los pasos 3 y 4, con una asignación de por medio. Los pasos 1 y 2 viven en otra parte, y **la OT no guarda el highlight del que viene**. La app no sabe de qué cambio viene cada OT. *(Una primera lectura mía de por qué su tipo de contrato incluye `PRESUPUESTO` quedó superada en D-510: ese tipo es el subcontrato base del presupuesto, no un cambio.)*

**Una observación del código sobre reasignar** (no se vieron datos): al reasignar, la app cambia el contratista de la asignación y de la OT, pero los pagos ya hechos conservan el nombre del contratista anterior y el saldo se calcula por número de OT. Resultado: **el resumen por contratista le atribuye al nuevo todo lo pagado en la OT, incluido lo que cobró el anterior.** Es relevante porque reasignar es lo común, y porque «pagado a otro contratista» es uno de los tipos de descuento.

**Lo que el usuario contestó después (D-510).** Las cinco preguntas que quedaron abiertas en D-509.

| Pregunta | Respuesta del usuario | Qué implica |
|---|---|---|
| ¿«Mal trabajo» es el paraguas de los demás descuentos? | «Son distintos, pero muy similares» | Siete tipos separados; ninguno contiene a otro. Eso responde también si el 1 y el 4 de la lista son lo mismo: no |
| ¿Quién decide el monto y cómo se calcula? | «Depende de cada motivo»: la calidad puede ser un porcentaje; las afectaciones, el valor de otra OT o un concepto estimado de obra, instalaciones o urbanización, «por mencionar algunos» | El monto **no tiene una sola fórmula: la base de cálculo depende del motivo**. Ver la tabla de abajo |
| ¿Qué contratistas llevan retención? | «Es por contratista actualmente»; recuerda a Gerardo Sierra, Melpro y Floviesa | La retención es **un atributo del contratista**, no del tipo de trabajo. La lista es de memoria, no necesariamente completa. Cuándo se devuelve no se contestó |
| ¿Qué significa cada tipo de contrato? | Ver la tabla de tipos de contrato | Ocho valores que mezclan **cuatro cosas distintas**; ver abajo |
| ¿Qué pasa con lo ya pagado cuando se reasigna? | Hay **dos clases de reasignación**; ver abajo | La app solo hace una de las dos |

*Para el diccionario de equivalencias:* en los cinco meses de almacén del repo, «Gerardo Sierra» aparece como contratista en 25 movimientos y «Productos Forestales Floviesa» en 1; Melpro no aparece en esa columna.

**Los ocho tipos de contrato de la OT, con las palabras del usuario.**

| Tipo | Qué es, según el usuario | Qué es en el cerebro (lectura mía) |
|---|---|---|
| `PRESUPUESTO` | Lo que el presupuesto base tiene como venta; cada prototipo tiene su precio de subcontrato de venta | **El subcontrato base.** Es el nodo de subcontrato de la plantilla del prototipo (D-313 lo compara contra su propia base). **No es un cambio**: es el caso normal |
| `ADICIONAL AL CLIENTE` | Cuando el cliente agrega algo: proyecto de obra nueva, cambio de accesorios, cambio de acabados | Cambio pedido por el cliente: highlight o adicional, y control de cambio al aprobarse (causa 5, `CONOCIMIENTO.md` §13.6) |
| `PPTO + ADICIONAL` | Se contrató y después se modificó (una cocina contratada en base y luego modificada) | Subcontrato base con una orden de cambio encima |
| `PAGO UNICO` | «Realmente es un método de pago»: no necesariamente requiere pagos posteriores ni cobro al cliente | **No es un tipo de contrato sino una forma de pago**; vive en otro eje |
| `POSTVENTA` | Trabajo posterior a la entrega de la vivienda; hay dos tipos: **costo al cliente** o **garantía** | La garantía es el `TICKET_GARANTIA` que el cerebro ya tiene (`MODELO.md` §3b). «Costo al cliente» no tiene dónde caer |
| `MANTENIMIENTO` | Trabajo por temporada; dos tipos: **costo al cliente** o **necesario para la entrega** | No está modelado. Sus dos tipos dicen quién absorbe el costo |
| `CANCELADO` | El cliente ya no quiso alguno de los anteriores, o ya no era necesario; **aplica a todos los anteriores** | **Es un estado, no un tipo**: cualquiera de los otros puede terminar así |
| `OTRO` | Un comodín, algún motivo que no estén viendo | Se queda como comodín abierto |

Las cuatro cosas que mezcla esa lista: **de dónde viene el trabajo** (base, adicional, modificado, postventa, mantenimiento), **cómo se paga** (pago único), **en qué estado está** (cancelado) y **un comodín**. Y dos de los orígenes se subdividen por **quién absorbe el costo**: el cliente, la garantía o «lo necesario para la entrega». Lo que propongo —sin decidirlo— es separarlos en campos distintos: `origen`, `forma_de_pago`, `estado` y `cobro` (al cliente, garantía o necesario para la entrega). Eso es lo que `MODELO.md` ya hace en otras partes (el «quién paga» de las nueve causas, `CONOCIMIENTO.md` §13.6).

**Confirmado en D-511:** la OT cubre la vida del subcontrato **desde que se contrata, no desde la venta**. La venta al cliente es un presupuesto o un control de cambio; de ahí se contrata la OT, que «funciona como un contrato informal para el contratista». Y el nombre: lo que yo había llamado «extraordinario por subcontrato» **debe llamarse simplemente subcontrato**; si algo es «extraordinario», es lo que queda **fuera del presupuesto**, que es lo más parecido que el usuario encuentra a la palabra.

**Cómo se calcula el monto de un descuento, según el motivo** (lo dicho por el usuario, sin completar):

| Motivo | Base del monto |
|---|---|
| Calidad (mala calidad) | Un porcentaje |
| Afectación a otros trabajos | El valor de otra OT, o un concepto estimado de obra, instalaciones o urbanización |
| Los demás | No se dijo; «por mencionar algunos» deja la lista abierta |

Las tres hojas de la estimación del concentrador (obra, instalaciones y urbanización) ya existen, así que un «concepto estimado de obra, instalaciones o urbanización» es una línea de esas estimaciones. Esto hace que **un descuento tenga una base de cálculo que se elige** (porcentaje, valor de otra OT, línea de estimación), además de su tipo. `DEDUCCION` hoy cuelga de una línea de estimación; estos cuelgan del pago de una OT, que el modelo no tiene. **Por eso `MODELO.md` espera a que la OT se modele** (B-111).

**Las dos clases de reasignación.**

| Clase | Qué pasa, según el usuario | En el cerebro | En la app de hoy |
|---|---|---|---|
| **Cambio de contratista** | Si ya se entregó un pago o anticipo, «que se pueda mover o cambiar como avance de otra u otras OT pendientes por pagar». Solo se pide una **alerta**: que el contratista esté enterado y que **no tenga avanzado el trabajo** | `ASIGNACION_CONTRATISTA` con `reemplaza_id` y motivo (abandono o logística). Lo avanzado se queda con quien lo hizo (D-453); el aviso de «quien avanza distinto del asignado» ya existe. **Mover un anticipo a otra OT se parece a `PRESTAMO`** (se salda con avance de obra, D-290), pero el cerebro no lo ha dicho así | Solo cambia el nombre en la asignación y en la OT; **no mueve pagos ni avisa** |
| **Cambio de obra** | «Solo cambia el recurso de una obra a otra» | Se cierra la asignación en una obra y se abre en otra (`presupuesto_id`) | Se logra editando el lote de la asignación, que mueve el de la OT |

*Lectura mía que falta confirmar:* «otra u otras OT pendientes por pagar» son las **otras OT del mismo contratista** que sale. También es posible que el descuento «pagado a otro contratista» sea esta misma situación vista desde el otro lado.

**Ampliar o disminuir el alcance.** El usuario dice que ambos se pueden hacer. En la app, editar una cotización **sobrescribe** las partidas y recalcula el monto: no queda la versión anterior. El cerebro hace lo contrario (la orden de cambio «no edita, agrega», `CONOCIMIENTO.md` §13.4, con un delta firmado). Hay además un caso hacia abajo: **descuentos al cliente**, cuando no quiso algo y hay que bajar el presupuesto (una cocina; en equipamiento, una estufa y una campana, aunque eso lo lleva **otra área, no subcontratos**). Eso es una orden de cambio con delta negativo y el cerebro ya tiene la forma de guardarla.

**Lo que el usuario aclaró después (D-511).**

| Tema | Respuesta del usuario | Qué implica |
|---|---|---|
| El nombre | «Extraordinario» **debe ser «subcontrato»**; si algo es extraordinario, es «más bien un fuera del presupuesto, lo más similar» | El nombre de lo que maneja la app es **subcontrato**. «Extraordinario» queda como calificativo: lo que está fuera del presupuesto. El nombre de la app (y su carpeta `apps/extraordinarios`) es del usuario; no se renombra sin que lo pida |
| Dónde empieza la OT | «Sí, pero no desde la venta»: la venta es un presupuesto o un control de cambio; de ahí se contrata la OT, un contrato informal para el contratista | Hay **dos lados**: el del cliente (presupuesto, highlight, control de cambio) y el del contratista (OT). La OT es el segundo |
| Reasignar | «Sí, correcto»: las otras OT pendientes por pagar son las del mismo contratista que sale | Se confirma la lectura de D-510 |
| Retención por garantías | **5 % normalmente**, «posterior a la entrega de la vivienda o cuando el supervisor autoriza»; **Control solo valida, de ser necesario** | Ver abajo |

**La retención por garantías, completa.** Es un atributo del contratista (D-510); el porcentaje es **5 % normalmente** (hay excepciones); se libera **al entregarse la vivienda o antes, cuando el Supervisor lo autoriza**, y Control de obra **solo valida si hace falta**. En el cerebro: la fecha de entrega ya existe (`PRESUPUESTO.fecha_entrega`, `MODELO.md` §3b); `RETENCION` hoy cuelga de una línea de estimación y no dice cuándo se libera; y las dos manos —el Supervisor autoriza, Control valida— son el patrón de siempre (D-269), con una diferencia: **aquí la validación es opcional**, y el modelo no tiene validaciones condicionales. La retención parece respaldar la garantía de postventa (`TICKET_GARANTIA`), pero eso no se dijo.

**Lo que el cerebro ya tiene de una OT** *(lectura mía)*: contratar un subcontrato del presupuesto **ya existe** —`ESTADO_CONGELAMIENTO` en `contratado` fija el precio (D-475) y `ASIGNACION_CONTRATISTA` dice quién lo ejecuta (D-453)—. Lo que no tiene es el **folio de la OT**, la **cotización del contratista** con partidas fuera de catálogo (los «conceptos extraordinarios» con número nuevo de `CONOCIMIENTO.md` §1.4), los **pagos por clase y tipo**, los **descuentos** y la **retención con su liberación**. Es decir, la OT quizá no sea una entidad nueva sino la contratación que el cerebro ya modela más lo que le cuelga.

**Siguen abiertas** (no bloquean nada): el porcentaje y la lista exacta de los contratistas con retención (la lista es de memoria); si el 5 % varía por contratista; y si «extraordinario» es sinónimo de *adicional* o abarca también la postventa y el mantenimiento.

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

### Las listas maestras a nivel de columnas, y qué choca con el cerebro (D-507)

El usuario pidió dar preferencia al cerebro y revisar con él lo que se contradiga o se amplíe. Las columnas salen de las migraciones de cada app; las cifras del concentrador, de contar valores distintos en su base sin leer ningún renglón.

| Dato | Concentrador | Extraordinarios | Auditoría | ObraCtrl | Cerebro |
|---|---|---|---|---|---|
| **Contratista** | `contratistas`: id, nombre. **29** en el catálogo y **47 grafías** en los renglones; 30 alias | **Texto suelto**, con tres nombres de columna: `asignaciones.contratista`, `pagos.contratista` y, al parecer, `ots.subcontrato` (inferido: el valor coincide en el archivo de muestra) | `contratista`: id, clave, nombre, activo | `contratista`: id, clave, razón social, RFC, contacto, teléfono, correo, calificación, estatus | `CONTRATISTA`: id, nombre —mínima a propósito—; 39 nombres en cinco meses de almacén |
| **Residente** | `residentes`: id, nombre. **13** en el catálogo y 28 grafías; 29 alias | No aparece | `residente`: id, clave, nombre, activo | `residente_obra` (residente, obra) y `obra.residente_id` | `USUARIO` + `RESIDENTE_OBRA` (usuario, obra, vigencias, corte de inicio) |
| **Obra o lote** | Texto `lote_cluster`: **114** valores distintos | Texto `lote` (y `modelo`) | `obra`: clave, proyecto, cluster, prototipo, m², fechas, estatus, desfase, duración real… | `obra`: cluster, prototipo, clave, residente, estatus, fechas, avance, m², tolerancia extra | **No hay tabla:** una obra es un `PRESUPUESTO` de tipo obra |
| **Proyecto y cluster** | `proyectos` (2); el cluster va dentro del texto del lote | No | `proyecto` y `cluster` | `proyecto` y `cluster` | **No existen** como entidad: el cluster es parte del nombre |
| **Prototipo** | No | `modelo` (texto) | `prototipo`: id, clave, nombre | `prototipo`: clave, nombre, m², niveles, recámaras | `PRESUPUESTO` de tipo plantilla: «es una convención de nombre, no un campo» |
| **Concepto** | Texto: **562** claves, **2,576** actividades y 24 unidades distintas | El trabajo, en texto | `concepto`: clave, descripción, unidad, familia, precio, es_nuevo, con versiones y variantes | `concepto`: tipo, clave, descripción, unidad, familia, especialidad, estatus | `NODO` con `VERSION_CONCEPTO` |
| **Asignar contratista** | No | `asignaciones` (lote, tipo de trabajo, contratista, estatus) y su historial de cambios | No | `contratista_frente` y similares | `ASIGNACION_CONTRATISTA`: alcance, vigencias, motivo y cadena de reemplazos |

Dos cifras del concentrador que sostienen una regla ya escrita: **562 claves con 2,576 descripciones** (casi cinco por clave) es la razón de que la clave mande y la descripción desempate, y **24 unidades distintas** frente a las 11 canónicas de la «Fuente de la Verdad» muestran cuánta normalización pide la unidad.

**Para revisar con el usuario.** Por defecto manda el cerebro; cada fila dice qué cambiaría si el usuario acepta la ampliación.

| # | Tema | Tipo | Cerebro dice | Las apps dicen | Por defecto (cerebro) |
|---|---|---|---|---|---|
| R1 | Qué es una obra | **Contradice en forma** → ✅ **decidido (D-512)** | Es un `PRESUPUESTO` de tipo obra; no hay tabla de obras | Un catálogo con clave «CLUSTER + LOTE» y atributos propios (m², fechas, estatus) | **Decidió el usuario: cada lote o casa es una obra,** identificada por cluster y lote; el proyecto es Magnolia, con 7 clústeres y n lotes en cada uno. Se queda el `PRESUPUESTO` de tipo obra, que gana `cluster_id`, `lote`, `prototipo_id` y `m2_adicionales` (`MODELO.md` §3c, propuesta). La urbanización también es una obra (R2). El estatus es **por arrancar · en construcción · por entregar · entregada · antigua** (D-513). Falta el cliente |
| R2 | Proyecto y cluster | **Amplía** → ✅ **decidido (D-512)** | No existen como entidad | Agrupan las obras: proyecto, cluster, obra | **Decidió el usuario: el orden es proyecto > cluster > lote.** Entran `PROYECTO` y `CLUSTER` (`MODELO.md` §3c, propuesta). **La urbanización es una sola obra para todo Magnolia,** y sus ramas son los clústeres y las amenidades |
| R3 | Prototipo | **Contradice en forma** → ✅ **decidido (D-512)** | Plantilla = `PRESUPUESTO` de tipo plantilla, que ya trae `plantas` y `plazo_semanas` | Tabla propia con m², niveles y recámaras | **Los m² son del prototipo;** una casa es un prototipo con o sin modificaciones y con o sin m² adicionales. Hay **niveles de presupuesto y niveles de casa** (planta baja, planta alta, roof garden), y no son lo mismo: el glosario los separa (*Nivel de casa*). En algún momento se desglosará por espacios y m² de espacios (B-113) |
| R4 | Contratista | **Amplía** → ✅ **decidido (D-512)** | Solo id y nombre, porque el crudo no trae más | `clave` y `activo` (auditoría); RFC, contacto, calificación (ObraCtrl) | **Se acepta la propuesta** (`activo` y la retención). **No hay clave corta y no se inventa una:** se toma la de OPUS si llega ese catálogo. **Nuevo: se categoriza por tipo y por oficio** (`MODELO.md` §4a, propuesta) |
| R5 | Residente | **Amplía** → ✅ **decidido (D-512)** | Es una persona con cuenta (`USUARIO`) asignada a una obra con vigencias | En los Excel es solo un nombre | **Los nombres son personas reales; falta asignarles cuenta y rol, y dos están inactivos** (se conservan con `activo` falso, no se borran). Se queda el cerebro (B-115) |
| R6 | Asignación de contratista | **Confirma y supera** → ✅ **decidido (D-512)** | Alcance, vigencias, motivo y cadena | `asignaciones` y su historial, por lote y tipo de trabajo | Se queda el cerebro. **Dos momentos:** la asignación de la obra se hace **antes de la junta de arranque, en la planeación,** y la de los subcontratos, **en la OT** |
| R7 | Estados de la estimación | **Contradice** → ✅ **decidido (D-508)** | `capturada · devuelta · validada · pagada`, en un solo registro | `previa · revisada · pagada` como **tres versiones** que se comparan entre sí; ObraCtrl: `borrador · enviada · validada` | **Decidió el usuario: es el mismo documento que va avanzando**, así que se queda el cerebro. Equivalencia que propongo y falta confirmar: previa ≈ capturada, revisada ≈ validada, pagada = pagada; `devuelta` no existe en la «Fuente». Lo que se rescata de las tres versiones es poder comparar cómo cambió el documento: se guardaría un corte de sus líneas al pasar de un estado a otro (B-109) |
| R8 | Categoría de los insumos | **Contradice en nivel** → ✅ **decidido (D-512)** | `destajo` y `subcontrato` son la clase de la categoría `trabajo` | ObraCtrl los pone al nivel de la categoría | Se queda el cerebro (el usuario: «ok») |
| R9 | Control de pagos de subcontratos | **Amplía** → ✅ **decidido (D-508)** | Conoce `DEDUCCION`, `RETENCION` (solo subcontratos, D-290) y `PRESTAMO` por línea de estimación, la garantía de postventa y el real contra la base de un subcontrato (D-313); **no tiene** cotización, OT, clase de pago, anticipo, finiquito ni pago único | Extraordinarios: anticipo, garantía de 5 %, avance, finiquito, pago único, descuento, cotizaciones y OT | **Decidió el usuario: la app se queda por ahora y el cerebro anota cómo funciona hoy para aprenderlo** (sección anterior). No entra al canon todavía. *Nota: D-507 dijo que el cerebro «no modela» este dominio; era incompleto, porque ya tiene el mecanismo de retención, préstamo y deducción* |
| R10 | Roles | **Amplía** → ✅ **decidido (D-512)** | Seis roles | ObraCtrl: cuatro (todos están en el cerebro); la «Fuente»: dos perfiles de la app | Se queda el cerebro. **Las tres cuentas de extraordinarios son áreas:** Asignaciones es **Finanzas,** Cotización es **Proyectos y atención al cliente,** Pagos es **Control de obra;** los demás roles corresponden con los del cerebro. Finanzas y Proyectos no son todavía roles del cerebro (B-111 y B-115) |
| R11 | Motivos de almacén y prefijos de mano de obra | **Amplía** → ✅ **decidido (D-512)** | Diez motivos y ocho prefijos, de datos reales | La «Fuente»: nueve y dos | **El cerebro es el correcto.** El usuario dice que «en algún momento» se evaluará **adaptar las apps al cerebro** (B-107) |
| R12 | Jerarquía de fuentes, folio de estimación y parámetros | **Amplía** → ✅ **decidido (D-512)** | No los tiene | La «Fuente» y ObraCtrl los definen | **El usuario confirmó que siguen vigentes** el folio, el IVA, los umbrales y la jerarquía de fuentes. Entran al canon la jerarquía y el folio, y los parámetros como configuración con esos valores iniciales (abajo; B-114) |

> Los **tipos** son una lectura mía de las dos fuentes; no se contrastó con el código de las apps salvo extraordinarios (D-508). **Los doce temas están revisados:** R7 y R9 en D-508 y los otros diez en D-512. Lo que cambia en el modelo queda como **propuesta** hasta que el usuario confirme los campos (`MODELO.md` §3c, `MODELO.md` §4a y `MODELO.md` §5d); el canon de nombres no cambia.

### Los cánones contra la «Fuente de la Verdad» — primera pasada (D-503)

La especificación de ObraCtrl declara que su glosario, sus reglas transversales y su diccionario son una **adaptación** de la «Fuente de la Verdad» (su parte 10 la llama «producto hermano»). Entonces los tres cánones no son tres: son **la «Fuente de la Verdad» con su adaptación de ObraCtrl, y el de este cerebro**. Se leyó el documento completo de reglas, catálogos y diccionario; faltan las cabeceras por archivo y los módulos 5 a 8.

| Tema | «Fuente de la Verdad» y ObraCtrl | Este cerebro | Veredicto |
|---|---|---|---|
| Principio rector | El sistema propone, la persona confirma; lo dudoso va a una bandeja única | Propuestas con evidencia y bandeja (D-485) | ✅ coincide |
| Signo de los movimientos de almacén | Viene en `Efecto Qty` y `Efecto Costo` del archivo | `cantidad` con signo, mismo origen | ✅ coincide |
| Motivos de almacén | 9 motivos canónicos | 10: agrega `reversion_movimiento_erroneo`, que apareció en cinco meses de datos reales | ✅ decidido (D-512): el cerebro es el correcto; la «Fuente» dice que su lista es extensible y falta darlo de alta allá |
| Origen de la estimación | El prefijo `E-` del folio marca que salió del ERP | `fuente` ∈ erp_externo · manual (D-284) | ✅ misma idea, forma distinta |
| Estados de la estimación | previa · revisada · pagada | capturada · devuelta · validada · pagada; ObraCtrl: borrador · enviada · validada (otra entidad, la de campo) | ✅ decidido (D-508): un solo documento que avanza, como el cerebro; falta confirmar la equivalencia previa ≈ capturada y revisada ≈ validada |
| Prefijos de mano de obra | `MOA` y `MOS` | En los CSV del repo: MOA 85 · MOE 78 · MOS 46 · MOH 23 · MOG 17 · MOC 8 · MOP 7 · MOO 1 claves distintas | ✅ decidido (D-512): el cerebro es el correcto; faltan seis en la lista de la «Fuente» |
| Semana | Ordinaria (lun–dom) y de obra (jue–mié, 5 días laborales), con selector por reporte | Pregunta abierta: con cuál se cortan los baldes del programa | ✅ la «Fuente» la contesta: las dos, a elección por reporte |
| Roles | `operador` y `gerencia` (un eje distinto: operar o leer) | residente · supervisor · superintendente · costos · cotizador · control de obra; ObraCtrl: residente · supervisor · control de obra · superintendente | ✅ decidido (D-512): se queda el cerebro; las tres cuentas de extraordinarios son áreas (Finanzas, Proyectos y atención al cliente, Control de obra) |
| Jerarquía de fuentes | Catálogos mandan; entre datos cargados, almacén gana a estimación | No está escrita | ✅ entra al canon (D-512): catálogos primero y, entre datos cargados, almacén antes que estimación; se combina con «la clave manda» (`CONOCIMIENTO.md` §2.1) |
| Folio de la estimación | `[E-]SSAA-NNN` (semana, año, consecutivo) | No lo tiene: su «folio» es el de la orden de producción | ✅ entra al canon (D-512), **por renglón y no por documento** (`MODELO.md` §5d, propuesta) |
| Parámetros del negocio | IVA 16 % (exentos pétreos y jardinería), umbral ±5 % de consumo, similitud 90 %, razón material/mano de obra ~60 % | No los tiene; su `umbral_pct` es de otra cosa (identidad dudosa) | ✅ vigentes (D-512); entran como configuración con estos valores iniciales (abajo) |

> Primera pasada: cada fila se verificó contra el texto o contra los CSV del repo, pero no se leyeron las cabeceras por archivo ni los módulos 5 a 8, y no se ha visto el código de la app. Nada de esto cambia un canon todavía: son diferencias a decidir (B-105).

### La revisión de los diez temas, con lo que dijo el usuario (D-512)

El usuario contestó los diez temas que quedaban (R1 a R6, R8 y R10 a R12). Esto es lo que queda decidido y lo que cambia en el cerebro. Los campos nuevos de modelo son **propuesta** hasta que él los confirme.

**1. La estructura de Magnolia (R1 y R2).**

```
Proyecto: Magnolia
├─ Urbanización ......... una sola obra para todo el proyecto; sus ramas son los clústeres y las amenidades
└─ Clúster (siete hoy)
   └─ Lote = una casa = una obra ......... se identifica por clúster y lote («FRESNO 12»)
```

Cada casa es un prototipo, con o sin modificaciones y con o sin m² adicionales. En el modelo: `MODELO.md` §3c. El concentrador trae **dos** proyectos (D-506) y el usuario habla de uno, Magnolia: falta saber cuál es el otro.

**2. Los niveles (R3).** El usuario avisó que «nivel» se dice de dos cosas distintas: el nivel del presupuesto y el nivel de la casa. Con el que el cerebro ya distinguía, son tres:

| Palabra | Qué es | Ejemplo | Dónde está |
|---|---|---|---|
| Nivel 2 y Nivel 3 | La profundidad en el árbol del presupuesto | Etapa de construcción (Nivel 2); concepto auxiliar (Nivel 3) | `NODO`; glosario |
| **Nivel de presupuesto** | Cada división del presupuesto bajo el prototipo; en el cerebro es el **frente** (D-450) | Cimentación, planta baja, planta alta, azotea, acabados, obras exteriores… (quince en el catálogo, `NIV-00001` a `NIV-00015`) | `Nivel ERP`; `CATALOGOS.md` |
| **Nivel de casa** | Cada piso de la vivienda | Planta baja, planta alta y roof garden | `Nivel OP` del avance (las órdenes de producción); `PRESUPUESTO.plantas` cuenta planta baja y planta alta |

El choque está en que «planta baja» y «planta alta» son **a la vez** un nivel de presupuesto (`NIV-00002` y `NIV-00003`) y un nivel de casa. Por eso el glosario los llama distinto. *Lectura mía, por confirmar:* el roof garden es la azotea (`NIV-00004`, que el catálogo escribe «Azotea» y «Azotea/Roof») y **no cuenta en `plantas`**, igual que el plazo de 28 y 30 semanas (D-419), que depende de si la casa tiene una o dos plantas.

**3. Los m² (R3).** Son del prototipo. Hoy viajan escritos en el nombre de su capítulo («ZAFIRO 1.0 (172 M2)»; son siete, de 172 a 300 m²) y no como dato. Una casa suma `m2_adicionales` si los tiene, y los m² totales se calculan, no se guardan. **En algún momento se desglosará por espacios** y por los m² de cada espacio (B-113).

**4. Contratistas (R4).** Se categorizan por **tipo** y por **oficio**; hay `activo`; no hay clave corta, y la que cite el catálogo de OPUS se toma cuando ese archivo llegue. El glosario cita la clave `FRE-00005` del catálogo de contratistas (29) de la generación anterior de OPUS, que no está en el repo y habría que pedir. Dos lecturas mías, por confirmar: el **tipo** es destajo o subcontrato (las dos clases de trabajo que el cerebro ya tiene), y el **oficio** es lo que el glosario llama *Especialidad*, uno o varios. En el modelo: `MODELO.md` §4a.

**5. Residentes (R5).** Los nombres son personas reales. Falta asignarles cuenta y rol, y dos están inactivos: se conservan con `activo` falso, no se borran. El concentrador trae 13 residentes con 28 grafías; el diccionario de equivalencias las lleva a cada persona (B-115).

**6. Asignar contratista (R6).** Hay dos momentos: la asignación de la **obra** se hace antes de la junta de arranque, en la planeación, y la de los **subcontratos**, en la OT. En el cerebro lo primero es `ASIGNACION_CONTRATISTA` con motivo `inicial`, y la junta de arranque ya existe como momento del programa (`disparador_fecha=contractual`, `MODELO.md` §5c); lo segundo sería la misma tabla con alcance de concepto, en el momento en que se contrata el subcontrato (`ESTADO_CONGELAMIENTO`, D-475).

**7. Roles y áreas (R10).** Las tres cuentas de extraordinarios son **áreas**, no roles del cerebro:

| Cuenta de extraordinarios | Área del usuario | Qué hace en la app | En el cerebro |
|---|---|---|---|
| `asignaciones` | **Finanzas** | Asigna contratista a lote y trabajo | No es un rol |
| `cotizacion` | **Proyectos y atención al cliente** | Cotiza y genera la OT, y la concluye | Se parece al *Cotizador* (D-280), que hoy no es un rol activo |
| `pagos` | **Control de obra** | Registra y confirma pagos | `control_de_obra` |

Hay precedente: Compras ejerce `validar_estimacion` sin ser un rol del cerebro (D-299). `ROL` es una tabla (migración 0004), así que sumar `finanzas` y `proyectos` es agregar filas y no cambiar el esquema. Se propone hacerlo cuando se modele la OT (B-111).

**8. Reglas y parámetros que el canon adopta (R12).** El usuario confirmó que siguen vigentes.

- **Jerarquía de fuentes:** los catálogos son la verdad; entre datos cargados, **el almacén gana a la estimación** para normalizar nombres de contratista, obra, material y concepto. Se combina con «la clave manda» (`CONOCIMIENTO.md` §2.1): primero se empata por clave y la jerarquía resuelve las discrepancias de texto. La estimación se normaliza hacia lo que dice el almacén.
- **Folio de la estimación:** `[E-]SSAA-NNN`, con la semana en dos dígitos, el año en dos y un consecutivo de tres que no se corta; el prefijo `E-` solo si el origen es el ERP externo. Es **por renglón, no por documento**, y si el campo de semana que llega ya trae esa forma, se toma como folio.
- **Parámetros**, que son valores iniciales y siempre se leen de la configuración, nunca de una constante en código:

| Parámetro | Valor vigente | Cómo funciona | En el cerebro |
|---|---|---|---|
| IVA | 16 % | Exentas las familias Pétreos y Jardinería; se resuelve por la casilla del material, luego por la familia y al final por el 16 % | No lo maneja todavía |
| Umbral de auditoría | ±5 % | Consumo real contra teórico; configurable en tres niveles (global, familia o concepto, insumo); se guarda el umbral usado en cada cruce | `ALERTA.parametro_usado.umbral_pct` guarda el usado; los tres niveles no están |
| Similitud | 90 % | Para proponer coincidencias de clave o descripción; el sistema propone y la persona confirma | Hay una alerta por diferencia de texto (D-477); no se comparó su umbral con este |
| Razón material y mano de obra | ~60 %, con banda de tolerancia | Salidas de almacén ÷ mano de obra pagada, por obra, contratista y tipo de estimación | No está |

La «Fuente» dice también que las estimaciones **no generan IVA, ni llevan retenciones ni amortización de anticipo**. Cuadra con lo dicho de extraordinarios: la retención es del subcontrato (la OT) y no de la estimación de destajo; en el cerebro `RETENCION` solo aplica a líneas de subcontrato (D-290).

**9. Dirección (R11).** El cerebro es el correcto, y el usuario dice que «en algún momento» se evaluará **adaptar las apps al cerebro**. Es un tercer camino junto a los dos de D-506 (unir las apps o crear una nueva en segundo plano); la decisión sigue siendo suya (B-107) y D-487 sigue en pie.

**Quedan abiertos, sin bloquear nada:** si el cliente es un dato de la obra; cuál es el segundo proyecto del concentrador; si «tipo» de contratista es destajo o subcontrato; si el roof garden cuenta en `plantas`; si los tres contratistas con retención son todos subcontratistas; y qué significa el prefijo `MOO` (una sola clave).

### ObraCtrl campo por campo contra el cerebro (D-513)

Primero, lo que el usuario contestó sobre el estatus de una obra: **por arrancar** (aún en planeación o próxima a construir), **en construcción**, **por entregar** (terminada, pero el cliente no la ha recibido), **entregada** y **antigua** (una obra vieja que ya debe ser una o muy pocas por cerrar).

Para lo demás se leyeron las 50 migraciones de `database/migrations` de `CONTROL-AVANCE` (69 tablas, último cambio el 3 de septiembre de 2026, commit `8dfb1b4`), su semilla canónica y su especificación. **No se corrió la app ni se vieron sus datos,** que viven en Supabase. En todo lo que se contradice manda el cerebro, como pidió el usuario (D-507); lo que ObraCtrl tiene de más queda como pregunta.

**Su ficha, con lo que ya se sabe.**

| # | Pregunta | Respuesta | De dónde sale |
|---|---|---|---|
| 1 | ¿Cuál es y qué guarda? | Control de obra por avance: organización, proyecto, cluster, obra (lote) y prototipo; catálogos (concepto, análisis de precio, insumo, familia, unidad, cuadrilla, nivel y etapa); presupuesto y programa; actividades con avance; estimación semanal; incidencias; control de cambio; solicitudes de cierre; evaluaciones, revisión física y entrega de obra; almacén y cargas | sus migraciones |
| 2 | ¿Quién lo usa y quién manda? | Cuatro roles —residente, supervisor, control de obra y superintendente— en una jerarquía residente → supervisor → superintendente. **Por contestar:** quiénes lo usan hoy | sus migraciones |
| 3 | ¿Cómo se llega a sus datos? | PostgreSQL con seguridad por fila en Supabase, una API de FastAPI y una descripción OpenAPI; cargas por Excel con huella (idempotentes y reversibles) | su repo |
| 4 | ¿Dónde vive? | El panel en Vercel (`control-avance-chi.vercel.app`, que dio el usuario, D-508); la API y un proceso de fondo en Render, la base en Supabase y los archivos en R2, según su documentación | D-508 |
| 5 | ¿Hasta dónde puede actuar el cerebro? | **Sin decidir.** Con API ya hay por dónde entrar al peldaño 2 (proponer); el 4 sigue sin decidirse | del usuario |
| 6 | Ejemplos reales | El repo solo trae una semilla canónica y pruebas con datos inventados; los datos reales no se han visto | lo medido |
| 7 | ¿Qué no se toca nunca? | **Por contestar.** Por su esquema: una estimación validada cierra la semana de esa obra (`periodo_bloqueado`) y un control de cambio no se autoriza sin su orden de cambio | sus migraciones |

**Lo que coincide con el cerebro** (y confirma que ObraCtrl nació del mismo diseño):
- La jerarquía residente → supervisor → superintendente (`supervisor_residente` y `superintendente_usuario`) tiene la forma de `SUPERVISION`.
- Las dos semanas (ordinaria, lunes a domingo; de obra, jueves a miércoles) en `calendario`, con `tipo_semana` en cada estimación.
- `mapeo` (alias, clave canónica y quién lo confirmó) hace lo de `EQUIVALENCIA` y `NORMALIZACION`; `pendiente` es la bandeja, con propuesta y resolución humana; `carga_datos` guarda la huella del archivo y puede revertirse.
- El análisis de precio (`cpu`) va versionado y con variante, como `VERSION_CONCEPTO`; `explosion` tiene como hijo un insumo o un concepto, nunca los dos, como `COMPOSICION`.
- `motivo_almacen` lleva signo y bucket; `etapa_constructiva.ponderacion` es el peso de cada etapa en el avance.
- Cerrar una actividad pide tres manos: el residente solicita, el supervisor autoriza y control valida (el patrón de D-269).
- El IVA sale de la familia (Pétreos y Jardinería sin IVA) con excepción por insumo (R12), y `configuracion` guarda los parámetros **con ámbito (global, familia, insumo o concepto) y vigencia: es la tabla que B-114 proponía.**

**Diferencias a decidir.** Por defecto manda el cerebro; la última columna es lo que solo el usuario puede contestar.

| # | Tema | ObraCtrl | Cerebro | Por defecto (cerebro) | Pregunta |
|---|---|---|---|---|---|
| S1 | Estatus de la obra | `pendiente · iniciada · en_proceso · casi_lista · entregada` | Los cinco del usuario (arriba) | El del usuario; en ObraCtrl `pendiente` pasa a por arrancar, `iniciada` y `en_proceso` a en construcción, `entregada` queda igual y `antigua` no existe | ¿«Casi lista» es lo mismo que «por entregar»? |
| S2 | Urbanización | `obra.es_urba`, siempre dentro de un cluster (`cluster_id` es obligatorio) | Una sola por proyecto, con ramas de clústeres y amenidades (D-512) | El cerebro; ObraCtrl no puede representar una obra sin cluster | — |
| S3 | Prototipo y m² | `prototipo.m2`, `niveles` y `recamaras`; `obra.m2` es un solo número | m² del prototipo más `m2_adicionales`; `plantas` | El cerebro; el `m2` de la obra sería el total y los adicionales su diferencia | ¿«Niveles» de un prototipo cuenta el roof garden? |
| S4 | Residente de una obra | `obra.residente_id` y además `residente_obra`, sin fechas | `RESIDENTE_OBRA` con vigencias (D-457) | El cerebro: sin fechas no se audita el retraso por residente | — |
| S5 | Quién ve qué | `supervisor_cluster` (supervisor y cluster) y `control_proyecto` (control y proyecto) | El alcance se hereda de `SUPERVISION`; Control ve todas | El cerebro | ¿Un supervisor ve todo su cluster o solo las obras de los residentes que supervisa? |
| S6 | Roles | Cuatro: `residente`, `supervisor`, `control_obra`, `super_intendente` | Seis, con las claves `control_de_obra` y `superintendente` | El cerebro: nombres y los dos roles que faltan, costos y cotizador | — |
| S7 | Contratista | Clave obligatoria, razón social, RFC, contacto, teléfono, correo, calificación y estatus; frentes y **especialidades** (varias) | `activo`, tipo, oficios y retención (D-512) | El cerebro; el oficio ya existe allá como `especialidad`, el tipo (destajo o subcontrato) no | ¿Qué clave le ponen allá, y usan RFC, contacto y calificación? |
| S8 | Frente | Ocho canónicos —Preliminares, Cimentación, Estructura, Albañilería, Hidrosanitaria, Eléctrica, Acabados, Herrería y carpintería—; cada etapa pertenece a un frente (mezcla niveles y gremios) | Frente = nivel constructivo; los gremios son sus sub-frentes (D-450) | El cerebro: lo que ObraCtrl llama «frente» es aquí un sub-frente (gremio) o un nivel, según el caso | — |
| S9 | Estimación | Cabecera con `semana`, `anio`, `tipo_semana`, `modo` (destajo, concepto o subcontrato), estatus `borrador · enviada · validada` y el `folio` en la cabecera | Periodo, `fuente` y estado `capturada · devuelta · validada · pagada`: un documento que avanza (D-508) | El cerebro | ¿Hay un paso de «enviada» antes de validar, y quién la marca «pagada»? ¿El folio es de cada renglón o de la estimación completa? |
| S10 | Control de cambio | De actividades: `extra_catalogo`, `fuera_catalogo`, `sustitucion` y `alta_catalogo`; estatus `solicitado · autorizado · rechazado`; la orden de cambio se captura al autorizar | Orden de cambio con el cliente (delta de monto y plazo, causa) más la incidencia que cambia la actividad | Son dos capas: la de ObraCtrl es interna y la del cerebro es con el cliente | ¿Un «extra» de ObraCtrl pasa después a una orden de cambio con el cliente? |
| S11 | Cierre | `solicitud_cierre` por **actividad** | `CIERRE_FRENTE` por frente, al 90 % (D-261) | El cerebro | ¿Se solicita el cierre de cada actividad o del frente? |
| S12 | Incidencia | Tipos `falta_material · error_ejecucion · cambio_cliente · proyecto_indef · retrabajo · detalle`; impacto `detalle · retraso · detiene`; seis estatus | Motivo (las nueve causas), efecto sobre la actividad y seis estados con tres manos (D-268 y D-269) | El cerebro | — |
| S13 | Costo de un insumo | Cuatro costos guardados: base, base actualizado, promedio de almacén y último | `PRECIO_HISTORICO`: una serie con fechas | El cerebro, que conserva la historia | — |
| S14 | Parámetros | Tabla `configuracion` con ámbito y vigencia | Sin tabla (B-114) | **Se toma la forma de ObraCtrl** | — |

**Lo que ObraCtrl tiene y el cerebro no:** la **entrega de obra** con cuatro participantes (el residente entrega, el supervisor da el visto bueno, control revisa calidad y expediente y el superintendente firma; cuando participan todos la obra queda entregada y congelada); **evaluaciones** de obra, residente y contratista en tres niveles (auto, control y final) con criterios ponderados; **revisión física** con fotos y calidad de uno a cinco; expediente de documentos y evidencias; notificaciones; bloqueo de periodo; captura sin conexión (`sync_status`, `device_id`, idempotencia); varias organizaciones (`org_id` en todo); una tolerancia de extra de 20 % por obra y por actividad; y cuadrillas con versión e integrantes.

**Lo que el cerebro tiene y ObraCtrl no:** vigencias de residente y de asignación de contratista con cadena de reemplazos; retraso auditado por corte; alertas con su parámetro; historia de precios; congelamiento de lo contratado; estado «pagada» de la estimación; deducción, retención y préstamo; postventa y su ticket de garantía; presentaciones de compra; la fecha de entrega al cliente; y los roles de costos y cotizador. En el esquema de ObraCtrl no hay nada de eso.

**Preguntas que solo el usuario puede contestar:** S1 (casi lista), S3 (niveles y roof garden), S5 (alcance del supervisor), S7 (clave y datos del contratista), S9 (enviada, pagada y folio), S10 (si un extra pasa a una orden de cambio con el cliente), S11 (cierre por actividad o por frente) y, de lo que ObraCtrl tiene de más, **cuáles de esas piezas usan hoy y deben entrar al cerebro** —sobre todo la entrega de obra con cuatro firmas, las evaluaciones y la revisión física—.

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
