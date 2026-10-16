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

### La OT en el cerebro: del borrador a lo firme (D-517, D-518 y D-519)

Con lo que el usuario ha dicho de la OT (D-508 a D-516) ya se ve qué del cerebro la cubre y qué falta. El usuario contestó las cinco preguntas (D-518) y la propuesta quedó escrita en `MODELO.md` §5i; en D-519 **confirmó los campos del bloque** y pasaron a firmes. Lo que sigue en propuesta se marca abajo. Una OT es el contrato informal con el contratista para ejecutar un subcontrato; empieza al contratar, y la venta al cliente (un presupuesto o un control de cambio) viene antes (D-511).

| Pieza | Hoy en la app de extraordinarios | Dónde cae en el cerebro | Estado |
|---|---|---|---|
| Quién la ejecuta | Asignación con historial; la hace Finanzas | `ASIGNACION_CONTRATISTA`, con alcance de concepto y cadena de reemplazos (D-453) | Ya está |
| Contratar y fijar el precio | Al cotizar nace la OT | `ESTADO_CONGELAMIENTO` en `contratado` (D-475) | Ya está |
| Número de la OT | Consecutivo único; se sugiere el siguiente y se puede escribir otro que no exista | Un número único | Firme (D-519) |
| Cotización del contratista | Partidas libres y un IVA que se teclea; al ampliar o disminuir el alcance se sobrescribe | Una cotización **con versión,** que se agrega y no se edita, con partidas libres (los «conceptos extraordinarios» de `CONOCIMIENTO.md` §1.4) | Firme (D-519) |
| Origen, quién absorbe el costo, forma de pago y estado | Un solo campo «tipo de contrato» con ocho valores | Cuatro campos: `origen`, `cobro`, `forma_de_pago` y `estado` (D-510) | Firme (D-519) |
| La venta al cliente de la que viene | No la guarda | Una liga a la orden de cambio (`PROPUESTA(orden_cambio)`), que viene del highlight o del adicional | Firme (D-519) |
| Pagos | Renglones por clase y tipo, que confirma Control de obra | Una tabla de pagos de la OT | Firme (D-519) |
| Retención de 5 % | Informativa | `CONTRATISTA.retencion_pct` y `RETENCION` (D-290 y B-112) | Propuesto |
| Descuentos | Un número sin tipo | `DEDUCCION` con los siete tipos nuevos (B-110), que puede ir a una OT o directo al contratista (D-519) | Propuesto |
| Saldo | Monto menos pagos confirmados | Se calcula, no se guarda | — |
| Reasignar | Cambia el nombre del contratista | Cambio de contratista (mueve el anticipo y avisa) o de obra (D-510); el traspaso del anticipo está por diseñar (B-124) | Firme el cambio; por diseñar el traspaso |
| Cancelar | No hay ruta | Un estado `cancelada` | Firme (D-519) |

**Las cinco respuestas del usuario (D-518).**

| Pregunta | Respuesta | Qué queda |
|---|---|---|
| ¿Qué es «a cuenta» frente a «transferencia»? | «A cuenta se entrega en efectivo» | El **medio** de pago es estimación, efectivo o transferencia *(lectura mía: transferencia bancaria)* |
| ¿La retención de 5 % sale de cada pago o del total? | «Total de la OT, y se retiene al finiquitar; el finiquito puede llevar la retención y/o la garantía, que es la retención» | Se calcula sobre el **total** y se retiene **al finiquitar.** «Garantía» **es** la retención: el pago `garantia` es su devolución |
| ¿El monto de una OT de presupuesto es la venta o lo que se paga? | «El precio de venta del prototipo; pero en todos los casos, si hay un incremento o decremento, lo vamos a comparar con el presupuesto base, para entender incrementos, deducciones, ahorros y sobrecostos» | El monto es el precio de venta; **toda** OT se compara contra su base. *Lectura mía:* incremento y deducción son cambio de alcance (más o menos obra) y ahorro y sobrecosto, la misma obra a otro precio |
| ¿Quién aprueba ampliar o disminuir el alcance? | «Lo realiza Proyectos y Control lo audita» | Proyectos lo hace y Control de obra lo **audita** *(lectura mía: después, no antes)* |
| ¿Quién concluye la OT y cuándo? | «Los residentes estiman hasta el pago de garantías, si es el caso» | La OT sigue abierta a la estimación hasta que **se pagó todo,** garantía incluida; *(lectura mía: el sistema propone concluirla y Proyectos lo confirma)* |

**Lo que el usuario contestó al confirmar el bloque (D-519).** Contestó que sí a las cinco lecturas y añadió dos cosas.

| Tema | Respuesta | Qué queda |
|---|---|---|
| Transferencia | «Es bancaria, pero ahorita no vamos a ver transferencias SPEI ni bancos» | El medio es solo una etiqueta: sin cuenta, banco ni clave de rastreo |
| Auditoría de Control | «Control va después: primero Proyectos cotiza y realiza la OT y después Control confirma o modifica si algo no está dentro del presupuesto» | La OT nace con la cotización de Proyectos; Control la **confirma o la modifica** después, contra el presupuesto base |
| Concluir | «Sí me parece» | El sistema propone concluir y Proyectos confirma |
| Cancelar, reasignar y retención | «Ok» | Sin cambios; el traspaso del anticipo sigue por diseñar (B-124) |
| Las partidas | «Vamos a realizar un cotizador; el presupuesto ya tiene algo por adelantado en carpintería y herrería que se necesita complementar, por ejemplo el costo de las puertas y los muebles» | Siguen libres por ahora; el cotizador es un pendiente aparte (B-123) |
| Los descuentos | «Pueden ir directamente a una OT o al contratista.» El caso: Floviesa reparó una pérgola hecha por Javier Galvan (OT ya pagada); se hace la OT de la reparación con un descuento a Javier Galvan que hace referencia a la OT inicial, pero no descuenta a esa OT, porque aparecería como falta por pagar; el descuento es solo al contratista y la empresa no paga por el arreglo | La deducción puede ir **sin ninguna OT**, y cuando hay OT distingue la que paga, la que originó y la que sirve de base: propuesta en `MODELO.md` §5d |

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
| R1 | Qué es una obra | **Contradice en forma** → ✅ **decidido (D-512)** | Es un `PRESUPUESTO` de tipo obra; no hay tabla de obras | Un catálogo con clave «CLUSTER + LOTE» y atributos propios (m², fechas, estatus) | **Decidió el usuario: cada lote o casa es una obra,** identificada por cluster y lote; el proyecto es Magnolia, con 7 clústeres y n lotes en cada uno. Se queda el `PRESUPUESTO` de tipo obra, que gana `cluster_id`, `lote`, `prototipo_id` y `m2_adicionales` (`MODELO.md` §3c, firme desde D-521). La urbanización también es una obra (R2). El estatus es el de ObraCtrl con «casi lista» renombrada: **pendiente · iniciada · en proceso · por entregar · entregada** (D-514). Falta el cliente |
| R2 | Proyecto y cluster | **Amplía** → ✅ **decidido (D-512)** | No existen como entidad | Agrupan las obras: proyecto, cluster, obra | **Decidió el usuario: el orden es proyecto > cluster > lote.** Entran `PROYECTO` y `CLUSTER` (`MODELO.md` §3c, firme desde D-521). **La urbanización es una sola obra para todo Magnolia,** y sus ramas son los clústeres y las amenidades |
| R3 | Prototipo | **Contradice en forma** → ✅ **decidido (D-512)** | Plantilla = `PRESUPUESTO` de tipo plantilla, que ya trae `plantas` y `plazo_semanas` | Tabla propia con m², niveles y recámaras | **Los m² son del prototipo;** una casa es un prototipo con o sin modificaciones y con o sin m² adicionales. Hay **niveles de presupuesto y niveles de casa** (planta baja, planta alta, roof garden), y no son lo mismo: el glosario los separa (*Nivel de casa*). En algún momento se desglosará por espacios y m² de espacios (B-113) |
| R4 | Contratista | **Amplía** → ✅ **decidido (D-512)** | Solo id y nombre, porque el crudo no trae más | `clave` y `activo` (auditoría); RFC, contacto, calificación (ObraCtrl) | **Se acepta la propuesta** (`activo` y la retención). **No hay clave corta y no se inventa una:** se toma la de OPUS si llega ese catálogo. **Nuevo: se categoriza por tipo y por oficio** (`MODELO.md` §4a, firme desde D-521: el tipo admite destajo y subcontrato a la vez, y el oficio es la `Familia`) |
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

Cada casa es un prototipo, con o sin modificaciones y con o sin m² adicionales. En el modelo: `MODELO.md` §3c. El concentrador trae **dos** proyectos (D-506): Magnolia y **«Antigua»,** un proyecto viejo al que le quedan una o muy pocas obras por cerrar (D-516; D-513 había leído mal «Antigua» como un estatus de obra).

**Tres precisiones del usuario sobre esta estructura (D-520).**

| Pregunta | Respuesta | Qué queda |
|---|---|---|
| ¿Las obras de «Antigua» se identifican por cluster y lote? | «Manzana y lote, ejemplo: 10-04, manzana 10 lote 4» | En «Antigua» lo que agrupa los lotes es la **manzana,** y la clave de la casa es manzana y lote («10-04»). En el modelo: `PROYECTO.agrupacion` (cluster o manzana), y la manzana usa la misma tabla `CLUSTER` *(lectura mía)*. El lote se guarda como texto para no perder el cero («04») |
| ¿Para qué sirve la sigla del cluster? | «Las siglas son para formar las claves e identificar a qué obra corresponde un control de cambio más rápido» | `CLUSTER.codigo` se queda: no es la clave de la casa sino la sigla con que se forman las claves de lo que cuelga de ella (`CC-ALM-18001`) |
| ¿El cliente es un dato de la obra? | «El cliente es el dueño de la casa; más adelante veremos cómo un usuario para un módulo de vivienda, donde podrá solicitar cambios antes y durante la construcción, y postventas y mantenimientos después de la entrega. Manéjalo como idea» | **Idea, sin modelar** (B-125). Los destinos ya existen: la orden de cambio, el ticket de garantía y las OT de postventa y mantenimiento |

**Al confirmar estos dos bloques (D-521).** El usuario confirmó la estructura (`MODELO.md` §3c) y el contratista (`MODELO.md` §4a) y contestó cuatro preguntas sobre el segundo:

| Pregunta | Respuesta | Qué queda |
|---|---|---|
| ¿Un contratista puede ser destajo y subcontrato a la vez? | «Sí» | El tipo es una tabla de relación (`CONTRATISTA_TIPO`), no un campo |
| ¿El oficio es la Familia del presupuesto? | «Sí» | `CONTRATISTA_ESPECIALIDAD` con `familia_id` |
| ¿El 5 % es igual para todos? | «Igual, pero déjalo editable por contratista» | `retencion_pct` por contratista, con 5 por defecto (parámetro, B-114) |
| ¿Falta algún dato del contratista? | «No» | Los campos quedan como se presentaron |

**2. Los niveles (R3).** El usuario avisó que «nivel» se dice de dos cosas distintas: el nivel del presupuesto y el nivel de la casa. Con el que el cerebro ya distinguía, son tres:

| Palabra | Qué es | Ejemplo | Dónde está |
|---|---|---|---|
| Nivel 2 y Nivel 3 | La profundidad en el árbol del presupuesto | Etapa de construcción (Nivel 2); concepto auxiliar (Nivel 3) | `NODO`; glosario |
| **Nivel de presupuesto** | Cada división del presupuesto bajo el prototipo; en el cerebro es el **frente** (D-450) | Cimentación, planta baja, planta alta, azotea, acabados, obras exteriores… (quince en el catálogo, `NIV-00001` a `NIV-00015`) | `Nivel ERP`; `CATALOGOS.md` |
| **Nivel de casa** | Cada piso de la vivienda | Planta baja, planta alta y roof garden | `Nivel OP` del avance (las órdenes de producción); `PRESUPUESTO.plantas` cuenta planta baja y planta alta |

El choque está en que «planta baja» y «planta alta» son **a la vez** un nivel de presupuesto (`NIV-00002` y `NIV-00003`) y un nivel de casa. Por eso el glosario los llama distinto. **Confirmado en D-514:** el roof garden es la azotea (`NIV-00004`, que el catálogo escribe «Azotea» y «Azotea/Roof») cuando el cliente lo pide, y **no cuenta en `plantas`,** igual que el plazo de 28 y 30 semanas (D-419), que depende de si la casa tiene una o dos plantas. Hoy el presupuesto solo trae conceptos de roof en los dos Diamante (el piso, el zoclo y la cancelería «Diamante ROOF»), y el título «Azotea/Roof» en Rubí.

**3. Los m² (R3).** Son del prototipo. Hoy viajan escritos en el nombre de su capítulo («ZAFIRO 1.0 (172 M2)»; son siete, de 172 a 300 m²) y no como dato. Una casa suma `m2_adicionales` si los tiene, y los m² totales se calculan, no se guardan. **En algún momento se desglosará por espacios** y por los m² de cada espacio (B-113).

**4. Contratistas (R4).** Se categorizan por **tipo** y por **oficio**; hay `activo`; no hay clave corta, y la que cite el catálogo de OPUS se toma cuando ese archivo llegue; el RFC es opcional, y el contacto y la calificación sí van, con el método de calificar por definir (D-514). El glosario cita la clave `FRE-00005` del catálogo de contratistas (29) de la generación anterior de OPUS, que no está en el repo y habría que pedir. Dos lecturas mías, por confirmar: el **tipo** es destajo o subcontrato (las dos clases de trabajo que el cerebro ya tiene), y el **oficio** es lo que el glosario llama *Especialidad*, uno o varios. En el modelo: `MODELO.md` §4a.

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

**Quedan abiertos, sin bloquear nada:** si el cliente es un dato de la obra; si «tipo» de contratista es destajo o subcontrato; si los tres contratistas con retención son todos subcontratistas; y qué significa el prefijo `MOO` (una sola clave).

### ObraCtrl campo por campo contra el cerebro (D-513)

Primero, el estatus de una obra. En D-513 se leyó que el usuario quería cinco —por arrancar, en construcción, por entregar, entregada y antigua—; **en D-514 aclaró que el de ObraCtrl está bien,** con «casi lista» llamada «por entregar» (ver abajo). Y **en D-516 se vio que «Antigua» no era un estatus:** es el nombre del segundo proyecto, al que le quedan una o muy pocas obras por cerrar.

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
| S1 | Estatus de la obra | `pendiente · iniciada · en_proceso · casi_lista · entregada` | Los mismos, con `casi_lista` llamada `por_entregar` (D-514) | ✅ **Decidido (D-514):** el de ObraCtrl. `antigua` no se agrega | — |
| S2 | Urbanización | `obra.es_urba`, siempre dentro de un cluster (`cluster_id` es obligatorio) | Una sola por proyecto, con ramas de clústeres y amenidades (D-512) | El cerebro; ObraCtrl no puede representar una obra sin cluster | — |
| S3 | Prototipo y m² | `prototipo.m2`, `niveles` y `recamaras`; `obra.m2` es un solo número | m² del prototipo más `m2_adicionales`; `plantas` | El cerebro; el `m2` de la obra sería el total y los adicionales su diferencia. ✅ **El roof garden no cuenta como nivel** (D-514) | — |
| S4 | Residente de una obra | `obra.residente_id` y además `residente_obra`, sin fechas | `RESIDENTE_OBRA` con vigencias (D-457) | El cerebro: sin fechas no se audita el retraso por residente | — |
| S5 | Quién ve qué | `supervisor_cluster` (supervisor y cluster) y `control_proyecto` (control y proyecto) | El alcance se hereda de `SUPERVISION`; Control ve todas | ✅ **Decidido (D-514):** el supervisor **no es por cluster,** ve las obras de sus residentes. `supervisor_cluster` sobra | — |
| S6 | Roles | Cuatro: `residente`, `supervisor`, `control_obra`, `super_intendente` | Seis, con las claves `control_de_obra` y `superintendente` | El cerebro: nombres y los dos roles que faltan, costos y cotizador | — |
| S7 | Contratista | Clave obligatoria, razón social, RFC, contacto, teléfono, correo, calificación y estatus; frentes y **especialidades** (varias) | `activo`, tipo, oficios y retención (D-512) | ✅ **Decidido (D-514):** sin clave (el id basta); RFC opcional; contacto y calificación sí, y el método de calificar se define después. La clave obligatoria de ObraCtrl sobra | — |
| S8 | Frente | Ocho canónicos —Preliminares, Cimentación, Estructura, Albañilería, Hidrosanitaria, Eléctrica, Acabados, Herrería y carpintería—; cada etapa pertenece a un frente (mezcla niveles y gremios) | Frente = nivel constructivo; los gremios son sus sub-frentes (D-450) | El cerebro: lo que ObraCtrl llama «frente» es aquí un sub-frente (gremio) o un nivel, según el caso | — |
| S9 | Estimación | Cabecera con `semana`, `anio`, `tipo_semana`, `modo` (destajo, concepto o subcontrato), estatus `borrador · enviada · validada` y el `folio` en la cabecera | Periodo, `fuente` y estado `capturada · devuelta · validada · pagada`: un documento que avanza (D-508) | ✅ **Decidido (D-514):** pasa por «enviada»; **Control de obra la marca «pagada»;** el folio va **en cada renglón** y el sistema crea además un identificador propio (oid) para la estimación | — |
| S10 | Control de cambio | De actividades: `extra_catalogo`, `fuera_catalogo`, `sustitucion` y `alta_catalogo`; estatus `solicitado · autorizado · rechazado`; la orden de cambio se captura al autorizar | Orden de cambio con el cliente (delta de monto y plazo, causa) más la incidencia que cambia la actividad | ✅ **Decidido (D-515):** son dos capas unidas: un extra **puede** pasar a una orden de cambio con el cliente; la liga es opcional | — |
| S11 | Cierre | `solicitud_cierre` por **actividad** | `CIERRE_FRENTE` por frente, al 90 % (D-261) | ✅ **Decidido (D-515 y D-516):** un doble candado. Se solicita **por frente** y, si se requiere, **por una o varias actividades;** y el segundo candado cierra **todo el lote.** Cerrar lo cierra **al residente;** para los demás sigue abierto hasta la entrega, y al entregar la obra **pasa a postventa** | — |
| S12 | Incidencia | Tipos `falta_material · error_ejecucion · cambio_cliente · proyecto_indef · retrabajo · detalle`; impacto `detalle · retraso · detiene`; seis estatus | Motivo (las nueve causas), efecto sobre la actividad y seis estados con tres manos (D-268 y D-269) | El cerebro | — |
| S13 | Costo de un insumo | Cuatro costos guardados: base, base actualizado, promedio de almacén y último | `PRECIO_HISTORICO`: una serie con fechas | El cerebro, que conserva la historia | — |
| S14 | Parámetros | Tabla `configuracion` con ámbito y vigencia | Sin tabla (B-114) | **Se toma la forma de ObraCtrl** | — |

**Lo que ObraCtrl tiene y el cerebro no:** la **entrega de obra** con cuatro participantes (el residente entrega, el supervisor da el visto bueno, control revisa calidad y expediente y el superintendente firma; cuando participan todos la obra queda entregada y congelada); **evaluaciones** de obra, residente y contratista en tres niveles (auto, control y final) con criterios ponderados; **revisión física** con fotos y calidad de uno a cinco; expediente de documentos y evidencias; notificaciones; bloqueo de periodo; captura sin conexión (`sync_status`, `device_id`, idempotencia); varias organizaciones (`org_id` en todo); una tolerancia de extra de 20 % por obra y por actividad; y cuadrillas con versión e integrantes.

**Lo que el cerebro tiene y ObraCtrl no:** vigencias de residente y de asignación de contratista con cadena de reemplazos; retraso auditado por corte; alertas con su parámetro; historia de precios; congelamiento de lo contratado; estado «pagada» de la estimación; deducción, retención y préstamo; postventa y su ticket de garantía; presentaciones de compra; la fecha de entrega al cliente; y los roles de costos y cotizador. En el esquema de ObraCtrl no hay nada de eso.

**Contestadas:** S1, S3, S5, S7 y S9 en D-514, S10 y S11 en D-515 y la duda del candado en D-516. **De lo que ObraCtrl tiene de más,** el usuario pidió seguir (D-516) y la partición propuesta está abajo.

**Lo que el usuario contestó sobre ObraCtrl (D-515).**

| Tema | Respuesta del usuario | Qué queda |
|---|---|---|
| Un extra y el cliente | «Sí, un extra puede pasar a un control de cambio con el cliente» | Las dos capas de S10 se unen con una liga **opcional:** nula mientras el extra es interno. En el cerebro un extra es una incidencia que cambia la actividad (`crece_actividad`, `crea_actividad`), y `CONOCIMIENTO.md` §13.6 ya decía que una incidencia «puede o no» generar un control de cambio. Lo que faltaba era la liga (`MODELO.md` §5c, propuesta) |
| El cierre | «Vamos a ponerlo por frente, y si se requiere alguna actividad también; o sea, un doble candado: por un lado una actividad o varias, y segundo todo el lote» | Dos candados. **Primero** el frente y, si hace falta, una o varias actividades; **segundo** el lote entero. Las manos no cambian: el residente solicita, el supervisor aprueba y control valida (D-269). El candado del lote parece ser la **entrega de obra** de ObraCtrl (cuatro firmas; la obra queda entregada y congelada) *(lectura mía)*; el de las actividades es su `solicitud_cierre`, pero una solicitud puede llevar varias |

*Una duda de palabra, resuelta en D-516:* «doble candado» podía ser dos controles o dos bloqueos. El usuario contestó que **lo cerrado se cierra al residente, y para los demás sigue abierto hasta la entrega de la casa, cuando pasa a postventa.**

**Lo que el usuario contestó (D-516).**

| Tema | Respuesta del usuario | Qué queda |
|---|---|---|
| El oid de la estimación | «El presupuesto sí tiene un oid; de ahí toma la idea para la estimación, porque cuando se descarga y se manda a revisión fuera del sistema se pueden eliminar, cambiar, agregar y modificar renglones» | La estimación **y cada renglón** llevan un oid que **genera este sistema y viaja en el archivo que sale;** al volver, se reconcilia por él. Es la misma idea con que el cerebro ya usa el `OID` de OPUS, con una diferencia: aquel es de un sistema ajeno y no se adopta como identidad (`MODELO.md` §1); este lo genera el cerebro y por eso sí puede serlo. Las reglas están en `MODELO.md` §5d |
| «Antigua» | «No sé a qué te refieras, ¿al proyecto?» | Sí: «Antigua» es el segundo proyecto, no un estatus. Se corrigió D-513 |
| El correo | «Sí, solo que el correo es para el login» | Contacto, teléfono y correo siguen opcionales en el contratista, **pero el correo es el del inicio de sesión:** en `USUARIO` es obligatorio y único (D-469 y D-470). Si el contratista entra algún día al sistema —y el usuario dice que sí, más adelante (D-517)—, será con ese correo |
| La entrega de obra | «Sí, aunque el superintendente puede o no estar; es más como el equipo de gestión de proyectos» | El candado del lote es la entrega de obra de ObraCtrl, con cuatro participantes: **el residente entrega, el supervisor da el visto bueno, control revisa calidad y expediente, y el equipo de gestión de proyectos firma;** el superintendente puede estar o no. *Lectura mía:* ese equipo es el área de Proyectos de R10 |
| El candado | «Más bien tendría que pasar a postventa; lo puedes cerrar al residente, pero para los demás se puede mantener abierto hasta la entrega de la casa» | Cerrar un frente, una actividad o el lote **cierra al residente** (ya no registra avance ahí); supervisor, control y gestión de proyectos siguen pudiendo hasta la entrega. **Al entregar, la obra pasa a postventa** (`MODELO.md` §3b) y no queda solo «congelada» como en ObraCtrl |

**Las piezas que ObraCtrl tiene de más: qué entra al cerebro (propuesta, D-516).** El criterio: el cerebro guarda el **dominio** de la obra, no la **plomería** de una aplicación (D-487).

| Pieza de ObraCtrl | Propuesta | Por qué |
|---|---|---|
| Entrega de obra con cuatro participantes | **Entra** (ya contestado arriba) | Es el segundo candado y lo que pasa la obra a postventa |
| Expediente técnico (planos, contratos, actas, evidencias, bitácora y otros, por obra) | **Entra,** chico | La entrega pide a control revisar «calidad y expediente»; el cerebro ya tiene planos y notas sobre ellos, pero no el expediente |
| Revisión física de control (fotos, comentario y calidad de **5 a 10,** D-517) | **Entra,** chica | De ahí puede salir la incidencia de calidad de un cierre (`CIERRE_FRENTE.incidencia_calidad_id`) y, después, la postventa |
| Bloqueo de periodo (una estimación validada cierra esa semana de la obra) | **Entra como regla** | Generaliza «una pagada ya no se toca»; **cierra la semana para todos** (D-517) |
| Tolerancia de extra de 20 % por obra y por actividad | **Entra como parámetro** | Es el mismo 20 % que el cerebro usa de ejemplo de umbral; cabe en la tabla de parámetros (B-114) |
| Evaluaciones de obra, residente y contratista (auto, control y final, con criterios ponderados) | **Después** | Es el punto de partida del método de calificar a los contratistas, que el usuario dejó para más adelante (B-117) |
| Cuadrillas con versión e integrantes | **Ya está** | Las cuadrillas son nodos con su matriz (D-473) |
| Avisos y notificaciones, captura sin conexión, varias organizaciones, idempotencia, respaldos | **Fuera del cerebro** | Son de la aplicación, no del dominio. Varias organizaciones se retoma si algún día se vende a otras constructoras |

**Las tres preguntas chicas, contestadas en D-517:** la calidad de la revisión física va **de 5 a 10** (ObraCtrl usa de 1 a 5 y tendría que cambiar); una estimación validada cierra la semana de esa obra **para todos;** y los contratistas **hoy no entran al sistema,** pero sí más adelante, para el cotizador, el programa de ejecución y, probablemente, su estado de cuenta (B-121).

**Al confirmar la estimación y el cierre (D-522).** El usuario confirmó los dos bloques (`MODELO.md` §5d y `MODELO.md` §5c) y, al contestar quién envía la estimación, **contó el recorrido real,** que corrige mi lectura de que la enviaba quien la captura:

| Paso | Qué pasa | Estado en el cerebro |
|---|---|---|
| 1 | El residente crea su estimación en Excel | — (es el archivo de origen) |
| 2 | Control de obra las recolecta y las pasa al extractor (el concentrador) | `capturada` |
| 3 | Salen y Control de obra las envía al **validador de topes,** que hoy es el rol de **Compras** | `enviada` |
| 4 | Vuelven a los residentes para revisar los ajustes de lo que no pasa por topes; se solicita verificar la cuantificación; los **supervisores justifican lo fuera de catálogo** | `devuelta` |
| 5 | El validador ajusta, y **esa es la estimación que se paga** | `validada` |
| 6 | Control de obra comparte la estimación final para el pago | `pagada` (la marca Control de obra) |

| Pregunta | Respuesta | Qué queda |
|---|---|---|
| ¿Quién envía la estimación? | El recorrido de arriba: **Control de obra** | `enviada_por` es de Control de obra, no del residente |
| ¿Sirve la tabla de historia? | «Sí, sí me sirve» | `ESTIMACION_LINEA_HISTORIA` firme: con ella se compara la versión previa con la revisada (B-109) |
| ¿Los cuatro participantes de la entrega, en orden? | «En cualquier orden» | `ENTREGA_OBRA` sin orden |
| ¿Falta algo en el cierre o la entrega? | «No de momento, pero en algún momento puede escalar, como una acta de entrega y recepción» | Idea sin modelar: la entrega podría escalar a un acta de entrega y recepción |

**Una diferencia con lo ya decidido.** D-330 asignó `validar_estimacion` a Control de obra «sin formalizar Compras como rol propio». El recorrido dice que el validador de topes es de Compras y que Control de obra recolecta, envía y comparte. Queda como **pregunta abierta para el usuario;** mi propuesta es sumar `compras` a `ROL` (como `finanzas` y `proyectos`, B-115) y asignarle `validar_estimacion`, sin cambiar el esquema.

**Lo que el usuario contestó sobre ObraCtrl (D-514).**

| Tema | Respuesta del usuario | Qué queda |
|---|---|---|
| Estatus de la obra | «Está bien así, como ObraCtrl»; «casi lista» es lo mismo que «por entregar» y prefiere ese nombre | `pendiente · iniciada · en_proceso · por_entregar · entregada`. En ObraCtrl el estatus **se deriva del avance:** desde 90 % es `casi_lista` (ahora por entregar) y con más de 0 % es `en_proceso`; `iniciada` se marca al arrancar la obra y `entregada` al entregarla, y **una obra entregada queda congelada;** tampoco se entrega una que nunca arrancó. El 90 % es el mismo del cierre de frente (D-261). La definición del usuario («terminada, pero el cliente no la ha recibido») y la regla de ObraCtrl (desde el 90 %) quedan juntas: por entregar va del 90 % hasta la entrega. «Antigua» **no es un estatus:** es el segundo proyecto (D-516) |
| Roof garden | «Actualmente el presupuesto solo combina en la Diamante planta alta y roof garden; algunos títulos dicen Azotea/Roof, porque la azotea puede pasar a roof garden si el cliente lo pide» | El roof garden **no es un nivel aparte ni cuenta en `plantas`:** es la azotea que el cliente convierte. Los datos lo confirman: el presupuesto solo trae conceptos de roof en los dos Diamante, y el título «Azotea/Roof» en Rubí. Convertirla es un cambio sobre esa casa |
| Supervisor | «No es por cluster, ve las obras de sus residentes» | Se queda `SUPERVISION`; `supervisor_cluster` de ObraCtrl sobra |
| Contratista | «No ponemos clave al contratista; solo el id. RFC opcional, no obligatorio. Contacto y calificación sí; después veremos el método de calificar» | Sin clave; `rfc` opcional; contacto, teléfono y correo opcionales *(lectura mía: ObraCtrl los trae separados)*; `calificacion` sin método todavía (B-117). La clave obligatoria de ObraCtrl sobra |
| Estimación | «Debe pasar por enviada; Control de obra la marca pagada; el folio va en cada renglón, e incluso en el sistema necesitamos crear un oid para las estimaciones» | Estados `capturada · enviada · devuelta · validada · pagada` *(lectura mía: la envía quien la captura, y `borrador` de ObraCtrl es `capturada`)*. **Control de obra la marca pagada,** y una pagada ya no se toca (la «Fuente de la Verdad»). El folio va en el renglón; la estimación lleva **su propio identificador generado por el sistema** —el oid del usuario—, que no se teclea. En ObraCtrl el `folio` está en la cabecera y pasaría al renglón (B-118) |

---

### ObraCtrl y el avance de obra: ¿rediseño o piloto? (D-523)

El usuario pidió ver el avance de obra para planear si hace falta rediseñar y para poner la app en operación. Esto es lo que se encontró; **no se construyó ni se conectó nada** (D-487 sigue en pie) y ObraCtrl no se tocó.

**Qué hace hoy el avance en ObraCtrl.** El residente captura la cantidad ejecutada de cada actividad (web, o móvil sin conexión); `cant_ejecutada` se deriva de la suma de lo capturado y el avance es esa cantidad entre la base; no se puede ejecutar más de lo programado, ni programar más de 120 % de la base (se pasa por control de cambio); desde 90 % la actividad queda «casi lista». Cerrar una actividad es residente solicita, supervisor autoriza y control valida; el cierre dispara el recálculo de la ruta crítica. Es la parte más completa de la app: la hoja de ruta de ObraCtrl da por cerradas sus 16 fases y dice que **lo que falta ya no es código sino ponerla frente a una obra real.**

**Qué se verificó (en esta sesión, con una copia aparte).**

| Capa | Resultado |
|---|---|
| Backend | **1,451 pruebas pasan:** 1,069 de dominio y 382 de integración contra un Postgres 16 con las 50 migraciones aplicadas |
| Base de datos | Las 50 migraciones aplican limpias, y las pruebas de aislamiento por rol (RLS) pasan |
| Web | **825 pruebas pasan** y la web compila |
| No se verificó | El móvil, las pruebas de navegador, la reversa de las migraciones, y **lo que está desplegado hoy:** el panel de Vercel no se pudo abrir desde la sesión y no se sabe qué hay en Render, Supabase, Redis y R2 |

**Qué avance real existe hoy (corregido en D-524).** Las exportaciones `grid_AvanceOPEventosOpr` del ERP externo (marzo a julio de 2026, en `1-mundo/fuentes/avance`) traen **2,920 eventos de operación** en 41 combinaciones de ubicación y lote, con 24 contratistas, 216 operaciones de destajo y 22 semanas con eventos; el avance es un porcentaje por operación (1,137 en 100 % y 1,783 por debajo, ninguno arriba) y el estatus del ERP no sirve (2,889 de 2,920 dicen «En Especificación»). Aparecen los **siete clústeres** por nombre —Acacia, Alamo, Fresno, Maple, Olivo, Olmo y Tabachín— y la planta tratadora, la vía Magnolia y la casa club. **El usuario aclaró (D-524 y D-525)** que el ERP externo no lleva avance, solo salidas de almacén y estimaciones, y que estas exportaciones **sí son avance, pero de pago:** no dice que no coincida con el físico, y sirven para **cruzar** contra él. Por eso D-523 se equivocó al decir que el avance físico ya existía en otro sistema: lo que existe es avance **pagado,** y **no hay en ninguna parte un avance físico capturado en campo.** ObraCtrl sería el primero, que es justo el hueco de `CONOCIMIENTO.md` §13.7. **No cambia nada de lo ya definido** (D-375 y D-377 siguen como están); el cruce solo lo mejora.

**¿Se necesita rediseño? Para operar el avance, no.** Lo que difiere del cerebro se reparte así:

| # | Brecha | Evidencia | Clase |
|---|---|---|---|
| G1 | El estatus `casi_lista` debe llamarse `por_entregar` (D-514) | Valor del enum de estatus de obra | **Ajuste menor:** renombrar el valor |
| G2 | La clave del contratista es obligatoria y única (D-514 dijo que no hay clave) | Columna `clave` no nula | **Ajuste menor:** al cargar, una clave provisional; después quitar la restricción |
| G3 | Toda obra exige cluster, así que la urbanización y las amenidades no caben (D-512) | `cluster_id` no nulo en la obra | **Antes de capturar esas obras;** no estorba a las casas |
| G4 | `supervisor_cluster` sobra (D-514) | La tabla sigue, pero ObraCtrl ya dejó de usarla para el alcance (migración 0042: el alcance sigue a la gente) y la conserva como dato territorial | **Ya resuelto en el código;** solo queda quitar la tabla cuando convenga |
| G5 | La estimación de ObraCtrl se genera del avance validado (`borrador`, `enviada`, `validada`), y el recorrido real es otro: Excel del residente, extractor, validador de topes de Compras, ajustes, pago (D-522) | Reglas de negocio y flujo de estimación de su especificación | **Rediseño diferido:** en el piloto el módulo de estimación se deja sin usar y la estimación sigue como hoy (R9) |
| G6 | Las órdenes de trabajo y los extraordinarios no están en ObraCtrl (su control de cambio es interno) | — | Fuera: extraordinarios se queda (R9) |
| G7 | El cerebro propone el % de avance desde el programa y el residente solo corrige lo raro; ObraCtrl pide la cantidad capturada | `CONOCIMIENTO.md` §13.7 y D-393 | **Mejora posterior,** con evidencia del piloto |
| G8 | Calidad de la revisión física de 1 a 5 (D-517 dijo de 5 a 10), roles con otros nombres, Antigua con manzanas | — | No bloquean; se ajustan cuando se usen |

**El plan, por etapas.**

| Etapa | Qué | Quién |
|---|---|---|
| 0 · Inventario | Saber qué hay desplegado hoy y con qué datos (panel, API, base, cola, evidencias), y dejar a punto lo que pide la hoja de ruta de ObraCtrl: sellar la base de producción, los orígenes permitidos (CORS), el modo de producción, la llave de servicio, etiquetas de versión y un respaldo probado | El usuario |
| 1 · Decisiones | Obra piloto (los residentes ya están: Leonardo López y Guadalupe, D-524); la señal en campo no hay y se deja para el final | El usuario |
| 2 · Datos de la obra piloto | Cargar en orden: unidades y familias, catálogo de conceptos con sus matrices, materiales, mano de obra y subcontratos, prototipo con su árbol, programa base, contratistas, la obra, usuarios y asignaciones. **El cerebro ya tiene casi todo en CSV** (los tres catálogos de OPUS, los siete programas de prototipos, la ingeniería de ALAMO 18, el almacén y el avance real); falta darle el formato de carga de ObraCtrl | El cerebro, **si el usuario levanta D-487 solo para preparar archivos de carga** |
| 3 · Piloto | Cuatro semanas con una obra en proceso o por arrancar: el residente captura el avance físico cada semana desde la web, control valida los cierres, **la estimación sigue en Excel**, y cada semana se compara el avance físico con el pagado (la alerta de dos sentidos de `CONOCIMIENTO.md` §13.7) | Residente y control |
| 4 · Decisión | Con lo que dejó el piloto: seguir, y qué de G1 a G8 rediseñar primero | El usuario |

**Una observación sobre la obra piloto.** ALAMO 18 es la obra mejor documentada del cerebro (ingeniería, precio real, cinco meses de almacén y de avance), pero probablemente ya esté avanzada. Sirve mejor para **repetir su historia por ObraCtrl** y comprobar la carga y la ruta crítica; el piloto en vivo conviene en una obra que esté en proceso o por arrancar.

**Lo que respondió el usuario (D-524)** y lo que sigue pendiente (B-126): lo desplegado son solo catálogos e ingenierías por prototipo, sin avance, y quiere cambiarlos; los residentes del piloto son Leonardo López y Guadalupe y las obras se definen después; no hay señal en campo, y eso se deja para el final; el ERP externo no lleva avance; y no está seguro de levantar D-487, pero quiere una comparativa de qué reemplazar en ObraCtrl, que es la sección siguiente.

### Qué alinear en ObraCtrl al cerebro: comparativa y orden (D-524 y D-525)

El usuario pidió, sin decidir todavía si levanta D-487, **un plan o una comparativa de qué hay que cambiar en ObraCtrl.** En D-525 aclaró el criterio: lo del árbol no es un disgusto, **tiene que estar alineado al cerebro.** Esto es solo el plan: no se tocó ObraCtrl ni se construyó nada.

| Pregunta | Respuesta | Qué queda |
|---|---|---|
| ¿Qué hay desplegado y con qué datos? (D-524) | «Catálogos y ingenierías por prototipo, que es algo que quiero cambiar; realmente no pasa nada si se elimina, porque no hay más datos de programas de avances empezados» | Lo desplegado es **solo catálogos y el árbol de los prototipos,** sin una sola captura de avance; se puede borrar |
| ¿Qué le disgusta del árbol? (D-525) | «No es disgusto, pero tiene que estar alineado al cerebro» | **El cerebro manda:** el árbol, los frentes, los catálogos y las cantidades de ObraCtrl se alinean a él, sin importar cuál esté mejor hecho |
| ¿Qué obra y qué residentes? | D-524: residentes Leonardo López y Guadalupe. D-525: «lo definimos más adelante» (las obras) | Residentes del piloto definidos; **obras por definir más adelante** |
| ¿Hay señal en campo? | «No hay señal, pero esto lo dejamos al final» | El móvil sin conexión será necesario y queda **para el final.** Mientras tanto el piloto captura donde haya señal; la web reintenta sin duplicar (llave de idempotencia) |
| ¿Qué son las exportaciones de OP? (D-525) | «Sí son avance, pero de pago; no digo que no corresponda con físico, solo es para cruzar. No debería alterar nada de lo ya definido en el cerebro, solo mejorar» | Son avance **pagado,** para cruzar con el físico; D-375 y D-377 no cambian (B-127 cerrado) |
| ¿Quién hace el respaldo y el reinicio? (D-525) | «Lo voy a realizar desde la rama de avance de obra; aquí lo debe entender el cerebro» | **Lo hace el usuario desde el trabajo de avance de obra;** el cerebro no lo ejecuta ni lo autoriza, pero tiene que entenderlo (abajo). D-487 sigue en pie |

**Cómo forman el árbol ObraCtrl y el cerebro** (corregido en D-525: D-524 había dicho que ObraCtrl lo deduce por el orden de las filas, y el cerebro también usa el orden):

| | ObraCtrl | Cerebro |
|---|---|---|
| De dónde sale | Un archivo **propio de ObraCtrl,** distinto del export de OPUS: con una columna de tipo y otra de la clave del padre (en la prueba real, 7 prototipos y 8,014 filas) | El **export nativo de OPUS** (`CATALOGO_DE_PRESUPUESTO`): 7 capítulos, 102 subcapítulos, 325 y 345 niveles intermedios y 2,452 conceptos en 3,231 filas (`1-mundo/opus`) |
| Cómo se arma el padre | Por la **clave del padre** que trae cada fila; si una clave se repite, gana la última vista de ese prototipo | **No hay columna de padre:** el nivel viene declarado y el padre de una fila de nivel *n* es la última fila vista de nivel *n−1* (una pila); el código de ingeniería sirve para ubicar, no para identificar (`CATALOGOS.md`, «Cómo se arma la jerarquía») |
| Qué clases tiene | Cuatro fijas en secuencia: prototipo, nivel, etapa y concepto (más sus componentes) | La profundidad **no dice qué es un nodo:** un concepto puede colgar de cualquier nivel (1,233 cuelgan de un Nivel 2 y 1,219 de un Nivel 3), y los Nivel 3 son agrupadores por prototipo |
| Un nodo repetido | La misma clave de concepto puede colgar de **dos etapas;** hubo que cambiar la identidad a (prototipo, padre, clave) para que no se pisaran | Cuatro claves aparecen como Nivel 3 y como Concepto a la vez: la clave sola no distingue, hace falta el tipo o la profundidad |
| Qué es un «frente» | Ocho frentes canónicos que mezclan niveles y gremios; cada etapa pertenece a uno | **Frente = nivel constructivo** (Nivel 1) y **sub-frente = etapa** (Nivel 2), D-450 |
| De dónde salen las cantidades de una obra | Se **copian las del prototipo** al generar la obra (157 actividades por casa) | Prototipo como plantilla y casa como instancia: la cantidad real viene de la **ingeniería del lote** y lo que cambia es una orden de cambio |

**Comparativa: qué se conserva, qué se alinea y qué se deja para después.**

| Pieza | Veredicto | Qué debe cumplir (dónde lo define el cerebro) |
|---|---|---|
| Árbol del prototipo | **Alinear** | Leer el export nativo de OPUS; nivel declarado y padre por pila; el concepto puede colgar de cualquier nivel; identidad por posición (`CATALOGOS.md` y `MODELO.md` §1) |
| Frentes | **Alinear** | Frente = nivel constructivo y sub-frente = etapa (`GLOSARIO-DOMINIO.md`, Frente) |
| Catálogos y sus cargadores | **Alinear los datos y la lectura;** conservar la mecánica de prueba en seco, versión y reversa | Los catálogos de OPUS que ya están en el repo (`CATALOGOS.md`, «Qué archivos de OPUS están en el repo») |
| Cantidades de la obra | **Alinear** | Plantilla e instancia, con la ingeniería del lote cuando exista (`MODELO.md` §3) |
| Programa base | **Alinear los datos;** el motor de ruta crítica de ObraCtrl puede quedarse (tiene sus pruebas de referencia) | La red, los relevos y las duraciones de los siete programas (`PROGRAMA-CPM.md` y `MODELO.md` §5c) |
| Captura de avance, cierre por actividad, ruta crítica, calendario | **Conservar** | El avance físico queda separado del pagado, y no se corrigen entre sí (`CONOCIMIENTO.md` §13.7) |
| Cierre de obra | **Alinear** | Doble candado: cierre de actividades y entrega de obra (`MODELO.md` §5c) |
| Estatus de obra, clave del contratista, obra sin cluster | **Alinear** | G1 a G3 de D-523; estructura en `MODELO.md` §3c y `MODELO.md` §4a |
| Estimación (se genera del avance validado) | **Después** | El recorrido real es otro (D-522, `MODELO.md` §5d); en el piloto sigue en Excel |
| Órdenes de trabajo y extraordinarios | **Fuera** | Extraordinarios se queda (R9); la OT firme está en `MODELO.md` §5i |
| Evaluaciones, revisión física, expediente, notificaciones, bitácora, respaldo, aislamiento por rol, varias organizaciones, captura sin conexión | **Conservar** | Plomería y piezas que el cerebro ya aceptó (D-516) |

**El orden de los pasos.** Cada uno se puede pedir por separado:

| # | Paso | Quién |
|---|---|---|
| 0 | **Respaldo y reinicio de la organización de ObraCtrl.** ObraCtrl ya trae la función de reiniciar: borra catálogos, prototipos, presupuestos y programas, y **conserva las cuentas** | **Pendiente (corregido en D-529):** D-526 lo dio por hecho, pero el usuario aclaró que **no se realizó: la base de datos no se borró para empezar de nuevo.** Falta repetirlo y comprobar que quedó vacía |
| 1 | **Árbol y frentes alineados:** leer el export de OPUS y las clases del cerebro | Cambio de código en ObraCtrl: **pide levantar D-487** |
| 2 | **Catálogos desde los CSV de OPUS** del cerebro, en el formato que pida ObraCtrl | Preparar archivos: **pide levantar D-487** solo para eso |
| 3 | **Plantilla y obra:** generar la casa desde el prototipo con su ingeniería | Cambio de código: **pide levantar D-487** |
| 4 | **Programa:** red, relevos y duraciones de los siete prototipos | Preparar archivos y ajustar la carga |
| 5 | Ajustes menores: estatus, clave del contratista, obra sin cluster, cierre en doble candado | Cambios chicos de código |
| 6 | **Piloto** con Leonardo López y Guadalupe, cuatro semanas, la estimación en Excel y el avance físico **cruzado cada semana con el pagado** (las exportaciones de OP y las estimaciones) | Definir las obras más adelante |
| 7 | Después: móvil sin conexión (no hay señal en campo), estimación y propuesta automática del porcentaje | Se decide con lo que deje el piloto |

**Cómo entiende el cerebro lo que pasa en el trabajo de avance de obra (D-525).** El cerebro no ejecuta nada allá ni se conecta (D-487): **entiende por lo que se le dice.** Por eso, cuando se haga cada paso, el usuario avisa aquí y el cerebro lo registra con cuatro datos: qué paso fue y qué día; qué respaldo se hizo y dónde quedó; qué quedó cargado (o borrado) en ObraCtrl; y si algo difiere de la tabla de arriba. Si la rama o el repo de avance de obra se agrega a esta sesión, el cerebro puede además leerlo y compararlo (solo lectura). En el repo de ObraCtrl no hay hoy una rama con ese nombre (sus ramas son `main`, `fase-1/proyectos-obras-y-captura-offline` y `claude/app-folder-structure-perxoy`); no se sabe en cuál se trabajará.

**Lo que se necesita del usuario** (B-126): las **obras del piloto,** más adelante; **avisar al cerebro** cuando haga el respaldo y el reinicio (paso 0); y, cuando quiera pasar al paso 1, **levantar D-487** para ese cambio.

### Los pasos para el trabajo de avance de obra (D-526)

El usuario pidió los pasos para la rama de control de avance. El cerebro **no construye** (D-487): estos pasos son el encargo para quien trabaje en ObraCtrl, partiendo de su `main` (la copia verificada en D-523 estaba en la fusión #90). **Corrección de D-529:** D-526 escribió que el paso 0 estaba hecho porque el usuario dijo «ya reinicié la organización»; después aclaró que **no se realizó, porque la base de datos no se borró para empezar de nuevo.** **Estado de partida:** lo desplegado sigue siendo lo de D-524 —catálogos y el árbol de los prototipos, sin una captura de avance—, y el paso 0 sigue pendiente. Para dar por hecho el paso 0 hay que **contar filas** de las tablas de catálogos, prototipos, presupuestos, programas y obras, y que den cero (las cuentas de usuario no cuentan).

| # | Paso | Dónde se toca en ObraCtrl | Qué manda el cerebro | Cómo se sabe que quedó |
|---|---|---|---|---|
| 1 | **Leer el árbol del export nativo de OPUS** y alinear las clases de nodo y los frentes | El cargador de presupuesto jerárquico (hoy pide una columna con la clave del padre); las clases de nodo y el enum del tipo de nodo (hoy etapa, nivel y concepto); la restricción de que solo el concepto es hoja; la generación de actividades | `CATALOGOS.md` («Cómo se arma la jerarquía» y «El Nivel 3 es el concepto auxiliar»): el nivel viene declarado y el padre de una fila de nivel *n* es la última de nivel *n−1*; un concepto cuelga de cualquier nivel; el Nivel 3 es un agrupador; la clave sola no distingue (hay cuatro que son Nivel 3 y concepto a la vez). Frente = nivel constructivo y sub-frente = etapa (D-450). **Referencia de lectura:** `backend/core/importacion_opus.py` (`leer_presupuesto`) | Cargar `1-mundo/opus/CATALOGO_DE_PRESUPUESTO.csv` da **7 árboles**, con 7 capítulos, 102 subcapítulos, 325 y 345 niveles intermedios y 2,452 renglones de concepto, y la suma de cada capítulo coincide con su total declarado |
| 2 | **Catálogos** | Los cargadores de conceptos y de CPU (hoy leen sus propias cabeceras, no el export de OPUS), de niveles, etapas, familias y unidades | `1-mundo/opus/ANALISIS_DE_BASICOS_CONCEPTOS.csv` (2,568 filas: conceptos, compuestos y las 39 cuadrillas) y, desde D-527, los catálogos `CATALOGO_DE_MATERIALES` (386), `CATALOGO_DE_MANO_DE_OBRA` (97, con las cuadrillas), `CATALOGO_DE_MATRICES` (472) y `CATALOGO_DE_FLETES` (9), todos en `1-mundo/opus/`. Niveles (15) y etapas (52) **se derivan del árbol,** y las unidades y las familias vienen en los catálogos. Desde D-528 también está `CATALOGO_DE_TRABAJOS` (265: 259 destajos y 6 subcontratos): **con los cinco catálogos las 1,208 claves del análisis tienen catálogo y los costos de las 462 líneas de contrato coinciden.** Solo queda, si existe, la lista oficial de contratistas | Cargar en el orden de dependencia: unidades y familias, niveles y etapas, conceptos y CPU, materiales, mano de obra y subcontratos, cuadrillas |
| 3 | **Prototipo como plantilla, casa como instancia** | La generación de la obra desde el prototipo; la clave de la obra | Una casa es cluster y lote («FRESNO 12»), con el lote como texto para conservar el cero (`MODELO.md` §3c). Por ahora se copian las cantidades del prototipo; la ingeniería del lote entra después | Generar una obra de prueba da actividades solo de las hojas de concepto, sin duplicar un Nivel 3 con su concepto |
| 4 | **Programa base de cada prototipo** | El alta del programa base y sus renglones (no hay cargador: se da de alta por la API de programas base) | `1-mundo/programas/PROGRAMAS-PROTOTIPOS.csv` (siete programas), `CATALOGO-DE-LA-RED.csv` y `RED-MINIMA-E01-E18.csv`; la regla en `PROGRAMA-CPM.md` | El motor de ruta crítica de ObraCtrl devuelve para un prototipo las mismas fechas que el programa del cerebro |
| 5 | **Ajustes menores** | Renombrar `casi_lista` a `por_entregar` (en la base, la web y el móvil, y mover la línea base del contrato, porque el móvil aún no está publicado); la clave del contratista (revisar primero las claves automáticas que ya trae) | `MODELO.md` §3c y `MODELO.md` §4a | Las pruebas de ObraCtrl siguen en verde; el verificador de compatibilidad del contrato acepta el cambio a propósito |
| 6 | **Piloto de cuatro semanas** | Cuentas de Leonardo López y Guadalupe como residentes (con su supervisor y control de obra), una obra para cada uno y su alcance | Las obras las define el usuario más adelante. La **estimación sigue en Excel;** cada semana el avance físico se cruza con el pagado (las exportaciones de OP y las estimaciones) | Cuatro semanas con captura completa; cada diferencia entre físico y pagado explicada o anotada (`CONOCIMIENTO.md` §13.7) |
| 7 | **Después del piloto** | Móvil sin conexión (no hay señal en campo), estimación (D-522), obra sin cluster (urbanización), cierre en doble candado, propuesta automática del porcentaje | `MODELO.md` §5d, `MODELO.md` §5c y `MODELO.md` §3c | Se decide con lo que deje el piloto |

**Cómo se entera el cerebro.** Al terminar cada paso, quien lo hizo avisa aquí con cuatro datos: qué paso y qué día; qué quedó cargado o cambiado en ObraCtrl; si algo difiere de esta tabla; y, si falló algo, qué. El cerebro lo registra y ajusta el plan. El paso 0 está pendiente (D-529); cuando se haga, además de los cuatro datos, dónde quedó el respaldo y el conteo de filas que prueba que la base quedó vacía.

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
