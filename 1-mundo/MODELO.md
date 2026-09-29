# MODELO — propuesto por el arquitecto

```
órgano:     esquema corporal
capa:       I — Mundo
pregunta:   ¿qué forma tienen los datos?
tiempo:     es así
corte:      2026-09-26
verificado: Aprobado · 15 hallazgos resueltos
```

> **Primera versión.** Nace de `CONOCIMIENTO.md`, verificado contra 8 catálogos de
> OPUS 2025. No es el esquema físico final: es lo que hoy se puede defender con
> evidencia, con las alternativas que quedaron abiertas.
>
> Al escribirlo aparecieron **6 contradicciones** que el texto no mostraba. Están
> marcadas como `⚠ HALLAZGO`.
>
> 2026-09-10 · para revisar y aprobar

---

## Cómo leer esto

Cada entidad trae sus campos, de dónde sale cada uno, y si hay más de una forma de
resolverlo. **No hay tipos de columna ni motor** — eso es la siguiente pasada, una
vez aprobada la forma.

```
campo            origen                              certeza
```

`certeza`: **firme** (verificado contra datos) · **propuesto** (razonado, no
verificado) · **abierto** (más de una opción)

---

# 1. El árbol — una sola tabla

> Regla de fondo: **un solo árbol recursivo con tipo en el nodo** (`CATALOGOS.md` del skill).

```
NODO
  id                 identity, INSERT                              firme
  padre_id           FK a Nodo (nullable en la raíz)                firme
  orden              posición entre hermanos                        firme
  rol                enum: ensamble · concepto · insumo ·
                      estructural (capítulo/subcapítulo/nivel/etapa)  firme
  ruta               calculada, con puntos, NO se guarda como fuente firme — es vista, no columna
  clave              único, nunca se reescribe                       firme
  descripcion        texto                                           firme
  unidad_id          FK Unidad, obligatoria                          firme
  cantidad           NUMERIC — puede ser negativa                    firme (58 casos verificados)
  modo_cantidad      enum: medida · estimada · capturada · heredada ·
                      cargada                                        firme — nuevo, ver hallazgo 12
  categoria          enum: material · mano_de_obra · herramienta ·
                      equipo · auxiliar · flete · trabajo · concepto firme
  familia_id         FK Familia                                      firme
  subfamilia_id      FK Subfamilia (nullable)                        firme — nullable, resuelto (P-12)
  clase_id           FK Clase_Trabajo (nullable)                     firme — nuevo, solo si categoria=trabajo (P-02/P-03)
  revisar            boolean, default false                          firme — nuevo, insumo apartado sin clasificar bien (P-04)
  marca_revisado     boolean, default false — checklist de captura
                      ("OK" en la descripción cruda). NO afirma que el
                      dato sea correcto, solo que alguien ya lo miró —
                      dato del usuario. Dirección opuesta a `revisar`
                      (ese pide revisión futura, este registra una ya
                      hecha)                                          nuevo — cierra P-34
  variables          JSONB, nullable — valores nombrados que una
                      `formula_personalizada` puede leer, cuando el
                      valor no amerita su propio nodo hijo             firme — nuevo, ver hallazgo 13
  modo_precio        enum: calculado · declarado                     firme
  precio_declarado   NUMERIC, nullable                                firme — solo si modo_precio=declarado
  procedencia        enum: importado · manual · fusion · division ·
                      extraccion · composicion · clonacion            firme
  reporta_a          categoría a la que el compuesto suma su monto    firme (D-hallazgo, ver §1a)
```

### Dos campos nuevos, agregados el 2026-09-15 — ver evidencia abajo

`clase_id` cierra P-02/P-03 (`clase` no tenía dónde vivir: sin él, `Acarreo` no se
podía distinguir de `Destajo` o `Subcontrato` en el dato). `revisar` cierra P-04.
Los dos con evidencia y aprobación explícita — no repiten el error de agregar un
campo sin marcarlo. Detalle en hallazgos 7 y 9, al final de este archivo.

### ⚠ HALLAZGO 12 — `modo_cantidad` tenía cuatro valores sin conectar a un caso

`medida · estimada · capturada · heredada` estaban desde la primera versión, pero
ninguno tenía escrito **para qué caso concreto servía cada uno** — en particular
`heredada`, que nunca se explicó. Al conectar el cuantificador con el paramétrico
aparecieron los casos reales, y faltaba uno: de dónde sale la cantidad cuando
**ya viene de una ingeniería cargada**, no de un plano ni de una captura a mano.

**El ciclo de vida completo de una cantidad, con evidencia:**

| `modo_cantidad` | De dónde sale | Caso |
|---|---|---|
| `capturada` | Alguien la tipeó | Presupuesto capturado a mano, sin ingeniería ni trazo |
| `cargada` | **Nuevo.** Vino de una ingeniería importada (`CONOCIMIENTO.md` §11.9, reversión por destajo) | La cantidad real de esa obra, ya reconstruida al importar |
| `heredada` | Se copió de un presupuesto de referencia al **crear** un paramétrico | El paramétrico nace con las cantidades del presupuesto base — no las mide, las hereda |
| `medida` | La produjo el cuantificador (`MODELO.md` §1b) | Se trazó sobre un plano — de esta obra en particular |

**Cómo se conectan, en el orden real:** un paramétrico se diseña a partir de un
presupuesto ya diseñado (`heredada`). Al aplicarse a una obra nueva, sus cantidades
pueden venir de una ingeniería que ya se cargó (`cargada`) — y el cuantificador
puede comprobarlas después, trazando sobre el plano de esa misma obra
(`medida`). **Dos fuentes independientes —lo cargado y lo trazado— que coinciden
se validan mutuamente** (`METODO.md` §1.4), igual que ya pasó con `identidad_dudosa`
(D-193).

> Esto no cambia nada de lo ya aprobado: los cuatro valores originales seguían
> firmes. Solo faltaba escribir para qué servía cada uno, y agregar el que faltaba.

### ⚠ HALLAZGO 1 — `reporta_a` es redundante si `categoria` ya está

El conocimiento dice: *el compuesto reporta a su propia categoría, entero* (`CONOCIMIENTO.md` §10.4).
Si eso es siempre cierto, `reporta_a` **es igual a `categoria`** y sobra como campo.

> **Pero el ejemplo real de la zapata lo contradice.** `ZA1-000001` tiene
> `categoria = Material`. Su hijo `MOC-12010` tiene `categoria = Contrato` y en la
> explosión trae `Origen = Material` (`CASO-TRABAJADO.md`). Ahí
> `Origen` no es la categoría del hijo: **es la categoría del padre, repetida en cada
> línea de la explosión.**

**Se resuelve así:** `reporta_a` no vive en el `NODO`, vive en `COMPOSICION` (`CONOCIMIENTO.md` §1) —
es un atributo de la **línea**, no del insumo. Un mismo insumo puede aparecer en
composiciones distintas reportando a categorías distintas según quién lo contenga.

### ⏸ PENDIENTE 2 — el código externo NO se modela todavía

El conocimiento establece que `Ingenieria ERP` **no es generable**: la prueba de
ida y vuelta demostró que la regla no es deducible — a veces el concepto recibe
segmento propio, a veces hereda el del padre, sin patrón encontrado
(`CATALOGOS.md` §11).

> **Decisión: no se agrega ningún campo para esto.** Ni calculado, ni opaco, ni
> arrastrado. Queda fuera del modelo hasta que P-17 se resuelva — sea porque se
> consigue la regla real del ERP externo, o porque se decide cómo tratarlo.
>
> Agregar un campo "provisional" ahora es el mismo riesgo que motivó la regla de
> dependencia: una vez que algo empieza a depender de él, deja de ser provisional.

### ✅ CONFIRMADO 3 — el concepto NO trae familia ni subfamilia de OPUS

Se confirmó contra OPUS 2025: el presupuesto no exporta clasificación del concepto,
solo lo ya conocido. **P-01 queda cerrado como derivación, no como importación.**

```
subfamilia_id   nullable
                92% se deriva de la matriz (el trabajo que usa el concepto)
                8% sin cobertura automática — requiere clasificación manual,
                mismo patrón que se usó en el catálogo de trabajos
```

**Decisión:** `subfamilia_id` es **nullable**. El 8% sin derivación se clasifica
después, a mano, como pendiente de datos — no bloquea la carga del concepto.



### ⏸ Nota — el `OID` de OPUS no se adopta como identidad

Al revisar OPUS apareció una columna `OID`. **No se usa como `id` del modelo.**

> Es el identificador interno del archivo de OPUS, no del negocio. Adoptarlo
> ataría la identidad de este sistema al ciclo de vida de un archivo ajeno: si OPUS
> reexporta y el `OID` cambia, el árbol se desincroniza sin aviso. Es justo lo que la
> regla del `id` existe para evitar — se genera en el `INSERT` de esta base, nunca se
> importa (`erp-construccion.md` §7).

**Dónde sí puede servir:** como columna auxiliar de reconciliación al importar,
junto a la clave — para saber si una fila es "la misma de antes" en una reimportación.
No como columna del modelo canónico.

```
IMPORTACION_RENGLON     (tabla de trabajo, no de negocio)
  oid_origen            el OID que trajo el archivo de OPUS
  clave                  
  nodo_id               a qué Nodo se resolvió, una vez importado
```

---

## 1a. Composición — la línea del árbol

> Es la tabla más importante del modelo: **de aquí sale el cálculo completo.**

```
COMPOSICION
  id                 identity — propia, NO el par (padre,hijo)        firme
  padre_id           FK Nodo                                          firme
  hijo_id            FK Nodo                                          firme
  cantidad           NUMERIC — puede repetirse el mismo hijo,
                      puede ser negativa                               firme
  orden              posición dentro del padre                        firme
  reporta_a          categoría a la que ESTA línea suma el monto       firme — ver hallazgo 1
  tipo_cantidad      enum: fija · porcentaje                           firme
  base_porcentaje    solo si tipo_cantidad=porcentaje:
                      "suma_jornales_hermanos" | "acumulado_hasta_aqui" firme — dos reglas distintas comprobadas
  formula_personalizada  texto/JSONB, nullable — si no es null, el motor
                          de cálculo ignora `cantidad` y `tipo_cantidad`
                          y evalúa la fórmula en su lugar                firme — nuevo, ver hallazgo 13
```

### ⚠ HALLAZGO 4 — dos reglas de porcentaje que se ven iguales y no lo son

`%MO` dentro de una cuadrilla: la base es **la suma de jornales de esa cuadrilla**,
fija, no acumulativa — las líneas `%MO` no se afectan entre sí (`CONOCIMIENTO.md` §6.2, comprobado con
CUAD-001: $1,880 → $188).

Las capas de sobrecosto (indirectos, utilidad): la base **sí es acumulativa** en la
convención mexicana — cada capa se calcula sobre lo que dejaron las anteriores
(`CONOCIMIENTO.md` §5).

> Si `COMPOSICION` y la futura tabla de capas comparten un solo campo genérico
> `porcentaje_sobre`, alguien va a copiar la lógica de una a la otra y romper el
> comportamiento. **Por eso `base_porcentaje` lleva un valor explícito por regla**, no
> un booleano "es acumulativo".

**Por qué la identidad propia en `COMPOSICION.id`:** el mismo insumo aparece dos
veces en una matriz con cantidades distintas — alambre recocido en `AUX-00001` para
amarre de varilla y amarre de estribos (26 casos verificados). Si la llave fuera
`(padre_id, hijo_id)`, la segunda línea no se podría insertar.

### ⚠ HALLAZGO 13 — la receta fija no basta cuando el múltiplo depende de esta obra

`COMPOSICION.cantidad` es un número de catálogo: sirve mientras la relación
hijo/padre no cambie de un presupuesto a otro. Pero pintura con dos manos y
pintura con tres manos son la misma matriz con un múltiplo distinto — y ese
múltiplo no es catálogo, es una decisión de **esta** obra. Ahí no alcanza un
solo número fijo. El campo `NODO.variables` (tabla `NODO`, arriba) existe para
esto.

**Dos formas de guardar esa variable, misma elección que ya existe entre
`medida` y `estimada` (D-209): por concepto o compuesto, según lo que haga
falta auditar — no una regla única para todos los casos.**

| Forma | Cuándo | Ejemplo |
|---|---|---|
| **Nodo hijo propio** (`modo_cantidad=capturada`) | La variable merece su propia línea, unidad y bitácora | Altura de muro, si se va a comparar contra otros muros |
| **`NODO.variables`** | Es un ajuste suelto, sin unidad propia que valga la pena auditar | Número de manos de pintura |

`formula_personalizada` se evalúa en `backend/core/motor_calculo.py`, **nunca
en SQL**: la geometría entrega la métrica (`ENLACE_CUANTIFICACION.medida`), la
fórmula la combina con `variables` y con los `cantidad` de otras líneas de
`COMPOSICION`. Misma frontera que D-182: **el recorrido es infraestructura, la
regla de qué suma a qué es dominio.**

> **"Rendimiento de matriz"** es el nombre que se usa en conversación para
> `COMPOSICION.cantidad` cuando alimenta una fórmula — es la misma «receta del
> ensamble» de siempre (`GLOSARIO-DOMINIO.md`, ambigüedad «Cantidad»), no una
> cantidad nueva por categoría. Material, mano de obra, flete, herramienta,
> equipo y trabajo comparten el mismo campo: dividirlo por categoría
> multiplicaría el lugar donde una misma regla puede divergir, el mismo riesgo
> que ya evitó `base_porcentaje` unas líneas arriba.

---

## 1b. Cuantificación — de dónde sale la cantidad

> Cierra B-19: las cuatro decisiones (C-1 a C-4, D-111 a D-114) ya estaban tomadas
> en `PROPUESTA-CUATRO-MODULOS.md` §2. Faltaba la tabla.

**Conecta directo con algo que el modelo ya tenía y nadie alimentaba:**
`NODO.modo_cantidad` incluye `medida` desde la primera versión — este es el
mecanismo que la produce.

```
TRAZO
  id
  geometria       polígono · línea · punto — la forma sobre el plano       firme
  plano_id, version_plano, capa                                           firme
  fuente          enum: PDF · DWG · IFC                                   firme
  autor, fecha                                                            firme — quién traza: C-3, por rol — ver abajo, B-45

ENLACE_CUANTIFICACION
  id
  trazo_id        FK Trazo                                                firme
  nodo_id         FK Nodo — a qué concepto alimenta                       firme
  medida          enum: area · perimetro · longitud · conteo              firme
  factor          NUMERIC — medida × factor = cantidad                    firme
  vigente         boolean — falso si otra fuente de mayor precedencia
                   lo reemplazó; queda como evidencia, no se borra        firme
```

**Un trazo, varios enlaces.** El polígono de una recámara da el área para el piso y
el perímetro para el zoclo — dos filas en `ENLACE_CUANTIFICACION`, un solo
`TRAZO` (`PROPUESTA-CUATRO-MODULOS.md` §2: *«guardando solo la cantidad, habría que
trazar la recámara tres veces»*).

### Muchas instancias del mismo elemento

Cuarenta trabes en una losa nervada no son mecanismo nuevo: son cuarenta filas en
`TRAZO` —una por trabe física, para poder auditar «la trabe 17 mide tanto»— cada
una enlazada por su propio `ENLACE_CUANTIFICACION`. Si el presupuesto quiere una
sola línea "trabe × 40 ml", los cuarenta enlaces apuntan al mismo `nodo_id` y la
cantidad se suma; si quiere cuarenta líneas, cada trazo enlaza a su propio nodo.
**La agregación es decisión del árbol del presupuesto, no del cuantificador** —
mismo principio que D-60: el cuantificador no crea árbol propio, alimenta el que
ya existe.

### La vigencia vive en el enlace, no en el trazo

El mismo trazo puede alimentar dos nodos con destinos distintos. **Un nodo puede
tener muchos enlaces vigentes a la vez** — uno por cada instancia física que lo
alimenta (las cuarenta trabes, cada una con el suyo) — y todos suman entre sí.
Lo que no puede haber son **dos enlaces vigentes de la misma instancia física**:
cuando llega una medida nueva de esa instancia con mayor precedencia
(`IFC > DWG > PDF`), el enlace anterior —de esa instancia, no de las demás—
pasa a `vigente = falso`, se conserva como evidencia y nunca se borra ni se
suma. Así se evita el pisamiento sin impedir la suma: el mismo muro medido en
PDF y en DWG no se cuenta dos veces, pero cuarenta muros distintos sí suman
cuarenta veces.

> **Cómo el sistema sabe que dos trazos son "la misma instancia"** queda sin
> resolver — hoy depende de que quien traza reemplace el enlace a mano, no de
> un emparejamiento automático por cercanía espacial. Anotado, no bloquea: es
> la misma familia de pregunta que B-45 (quién traza, gobierno por obra).

> **Dos fuentes que discrepan mucho no se promedian ni se eligen solas: es
> `PROPUESTA` con evidencia** (§5) — no corrección automática.

### Si el plano cambia

Las cantidades trazadas sobre la versión anterior **quedan marcadas para
revisión**, no se recalculan solas — mismo principio que «detectar no necesita
permiso, corregir sí» (D-46).

### Cómo viaja la geometría hacia el frontend

**GeoJSON — Decisión 2 de 3.** PostGIS la exporta nativa (`ST_AsGeoJSON`) y la
importa nativa (`ST_GeomFromGeoJSON`): no hace falta serialización a mano en
ninguna punta. Es JSON plano —el navegador lo parsea solo, sin librería— y
cualquier visor de planos (Leaflet, MapboxGL, OpenLayers, canvas propio) ya lo
entiende.

Cada `Feature` de la `FeatureCollection` lleva `properties: { trazo_id,
nodo_id }` junto a su `geometry` — así el clic en una forma del plano sabe a
qué nodo del árbol resaltar, y viceversa (el enlace bidireccional tipo
Navisworks que se buscaba).

> **Transporte, no almacenamiento.** `TRAZO.geometria` se guarda en el tipo
> nativo de PostGIS, no como texto GeoJSON — así conserva el índice espacial
> (`GiST`) y los `ST_*` no reparsean texto en cada cálculo. GeoJSON se genera
> al leer y se parsea al escribir, en el borde de la API — nunca es la fuente
> de verdad. Esa sigue siendo `ENLACE_CUANTIFICACION`: el `properties.nodo_id`
> de cada `Feature` es una copia de lectura para que el frontend resuelva el
> clic, no un lugar nuevo donde ese dato pueda vivir por su cuenta.

> **Coordenadas de plano, no geográficas.** GeoJSON asume por convención
> lon/lat WGS84 (RFC 7946); acá las coordenadas son locales al plano —igual
> que hace cualquier herramienta CAD-a-web—, con su propia escala (categoría
> A del inventario, `IDEAS.md` §2: calibración de escala). Es una desviación
> deliberada de la convención, no un error a corregir después.

### Cómo se captura una geometría nueva

**WKT — Decisión 3 de 3.** Cuando alguien traza un elemento nuevo con clics
sobre el plano, la secuencia de puntos se arma directo como texto WKT
(`LINESTRING(x1 y1, x2 y2, ...)`) del lado del frontend, y `ST_GeomFromText`
la convierte a geometría nativa de un solo golpe — mismo principio nativo que
`ST_GeomFromGeoJSON` en la Decisión 2, para el otro momento del flujo.

**No compite con GeoJSON, resuelve otro momento.** GeoJSON transporta *varios*
trazos ya existentes con su enlace al árbol (`properties.nodo_id`) para
pintarlos todos y habilitar el clic. WKT captura *un* trazo nuevo, todavía sin
enlace, mientras se dibuja — el mismo par que ya usan PlanSwift (captura) y
Navisworks (coordinación con el modelo) por separado en la construcción real.

> **WKT no tiene bolsillo de propiedades.** `nodo_id`, `medida`, `factor`,
> `plano_id`, `autor` viajan como campos comunes de la misma llamada a la
> API, nunca adentro del texto WKT — el formato solo contesta "qué forma es".
> Meter metadato ahí sería inventar un WKT no estándar.
>
> **Es formato de entrada, no un tercer almacenamiento.** `ST_GeomFromText`
> convierte y el texto WKT se descarta — lo que persiste es siempre la
> geometría nativa de PostGIS (D-218). Igual que GeoJSON en la Decisión 2, no
> es una copia paralela de la fuente de verdad.

### Quién puede trazar — B-45 cierra

No hace falta tabla nueva de gobierno por obra: **`ROL_FUNCION` (§5b) ya es el
mecanismo**, y ya tenía dos de las tres funciones que hacían falta — `trazar`
y `aprobar_trazo` — declaradas desde P-21, antes de que este hallazgo las
necesitara.

```
trazar          →  Costos · Control · Residente · Supervisor   (no Cotizador)
aprobar_trazo   →  Control
```

**No es tan restrictivo como sonaba en la propuesta original.** Residente y
Supervisor trazan igual que Costos y Control — la diferencia no es de
permiso, es de para qué: cuantifican para sustentar una orden de cambio
(`CONOCIMIENTO.md` §13.4), y esa orden ya pasa por `autorizar_orden_cambio`
antes de tocar un nodo contratado. El control no se duplica en el trazo: ya
existe un paso más adelante en la cadena.

**Visualizar el estado de cuantificación no es una función atómica nueva.**
Las catorce de §5b son todas de acción — ninguna de lectura. Ver cómo está
cuantificada la obra sigue el mismo patrón: es lectura, abierta a quien tiene
acceso a la obra, no un permiso aparte.

### Notas flotantes sobre el plano — capacidad nueva, entidad chica

Residente y Supervisor pueden **anotar el plano** sin que la nota alimente
ninguna cantidad — distinto de `TRAZO`, que siempre alimenta un
`ENLACE_CUANTIFICACION`. Entidad propia, la más chica posible:

```
NOTA_PLANO
  id
  plano_id, version_plano                                              firme
  ubicacion       punto — WKT al capturar, GeoJSON al transportar,
                   mismo par de decisiones que TRAZO (D-219 a D-222)    firme
  autor_id, fecha                                                       firme
  texto                                                                 firme
  nodo_id         FK Nodo, nullable — si la nota es sobre un concepto
                   puntual y no solo un lugar del plano                 firme
```

**Nunca tiene `ENLACE_CUANTIFICACION`.** Si algún día una nota necesita
generar cantidad, no se amplía esta tabla: se convierte en `TRAZO`, que ya
sabe hacer eso.

`FUNCION_ATOMICA` gana una decimoquinta: `anotar_plano` → Residente,
Supervisor.

> **Propuesto, no cerrado del todo.** La forma de `NOTA_PLANO` es la más
> chica que cubre lo pedido. Si hace falta algo más —adjuntar una foto, marcar
> la nota como resuelta— se agrega encima cuando haya un caso real.

---

## 1c. Ensamble — el árbol un piso arriba (cierra la mitad de B-53/Paramétrico)

**Ensamble no es una tabla nueva.** `CONOCIMIENTO.md` §5.1 ya lo dice: "no es
un módulo con reglas propias, es el árbol recursivo aplicado a otro nivel de
abstracción." Es un `NODO` con `rol=ensamble` (el valor ya existe en el enum
de §1) cuyos hijos en `COMPOSICION` son otros nodos —`rol=ensamble` para
sub-ensambles, `rol=concepto` para hojas— nunca insumos directos.

```
[reusa NODO + COMPOSICION de §1/§1a, sin campo nuevo, para:]
  - plantilla/instancia (§5.2)        → heredado de PRESUPUESTO.tipo (§3)     firme
  - de dónde sale la cantidad (§5.4)  → NODO.modo_cantidad ya cubre los 3
                                         casos: heredada (nace del presupuesto
                                         base) · cargada (de una ingeniería
                                         importada) · medida (del cuantificador,
                                         §1b, hallazgo 12)                     firme
  - la referencia apunta al concepto,
    no al renglón (§5.6)              → COMPOSICION.hijo_id ya apunta a NODO,
                                         nunca a una fila de presupuesto       firme
```

### ⏸ PENDIENTE — lo genuinamente nuevo: el parámetro propio y su cohorte (B-53)

`CONOCIMIENTO.md` §5.7 cerró la regla, comprobada esta sesión en los siete
prototipos (D-311, D-312): un ensamble no escala con el m² total, escala con
**su propio divisor** —desplante para cimentación, salidas para
instalaciones— con una cohorte explícita (a qué población aplica) y una
dispersión que se guarda junto al valor, nunca sola. Esto no tiene dónde
vivir en `NODO`/`COMPOSICION` — es atributo del ensamble-plantilla, no de la
línea del árbol.

```
ENSAMBLE_PARAMETRO
  id
  ensamble_id      FK Nodo — solo válido si rol=ensamble                      firme
  parametro        enum: desplante · m2_total · salidas · piezas · ... —
                    abierto, §5.7 solo probó desplante                        abierto
  tasa             NUMERIC — $/parámetro, aprendido sobre obras ya
                    cuantificadas                                             propuesto
  cohorte          texto — a qué población aplica esta tasa (§5.7: "cada
                    ensamble declara a qué aplica; fuera de ella, no se usa")  abierto
  dispersion       NUMERIC — CV medido junto con la tasa (§5.7: "un precio
                    sin su dispersión es un número disfrazado de certeza")     firme
  revisar          boolean, default false — mismo patrón que `NODO.revisar`
                    (P-04): se enciende cuando un insumo de su cohorte
                    cambia de familia (`BITACORA_RECLASIFICACION`, §4b),
                    la tasa no se recalcula sola                              nuevo — B-61
```

**El valor del divisor para una instancia nueva no necesita campo propio.**
Los 216 m² de desplante de una obra real ya son la `cantidad` del `NODO` de
esa instancia, con `modo_cantidad=medida` si vino del cuantificador
(`TRAZO`/`ENLACE_CUANTIFICACION`, §1b) o `capturada` si se declaró a mano —
mismo mecanismo que ya existe, sin duplicarlo. `ENSAMBLE_PARAMETRO` guarda la
**tasa** (cuánto cuesta cada unidad del divisor), no el divisor en sí.

> **Aprender y generar leen el mismo campo en direcciones opuestas** (§5.10):
> dividir cantidad medida entre divisor la escribe (`tasa`); multiplicar
> `tasa` por el divisor de una obra nueva la usa para generar. No son dos
> números — es el mismo, leído en un sentido o en otro.

### ⏸ Lo que esto NO resuelve

- **Cómo se declara la cohorte** — hoy es texto libre, sin regla de qué la
  hace válida ni de cómo el sistema decide "esta obra cae en esta cohorte."
  §5.7 la prueba a mano (desplante/m² total, plantas) — falta el mecanismo.
- **Quién puede crear o aprobar un `ENSAMBLE_PARAMETRO`** — mismo pendiente
  que el resto del modelo: sin clave todavía en `FUNCION_ATOMICA`.
- **El constructor de matrices paramétrico (B-18)** es una capa distinta y
  más abajo del árbol: genera la `COMPOSICION` de un **concepto** (trabe,
  castillo) a partir de fórmula, no la de un ensamble. Motor de cálculo, no
  schema — mismo criterio que ya excluye el resto de §6. Lo único que sí es
  schema es la tabla de constantes físicas que ese motor consulta:

```
CONSTANTE_FISICA
  id
  categoria        enum: longitud_comercial · factor_corte_por_altura ·
                    factor_traslape · desperdicio · calibre_circuito ·
                    puntas_circuito · tiempo_entrega ·
                    factor_conversion_dimensional — abierto, crece
                    con evidencia                                        abierto — gana factor_conversion_dimensional
  clave             qué fila específica dentro de la categoría (ej. "varilla",
                     "castillo 4.20m", una familia, un insumo o un
                     concepto — este último solo para
                     `factor_conversion_dimensional`, F-4/D-91)                firme
  valor             NUMERIC                                                    firme
  unidad_id         FK Unidad                                                  firme
  base               enum: natural · habil, nullable — solo aplica a
                     `categoria=tiempo_entrega` (`CONOCIMIENTO.md` §15):
                     quince días naturales y quince hábiles descuentan
                     distinto contra el calendario                            nuevo
  fuente             texto — de dónde salió (norma, medición propia, dato de
                     usuario)                                                  firme
```

> **Ya tiene evidencia real, no hipotética.** La vara comercial de
> varilla mide 12 M (`categoria=longitud_comercial`); un castillo de
> 4.20 M corta cada vara a 6 M, uno de 3.00 M la corta a 4 M
> (`categoria=factor_corte_por_altura`) — verificado exacto contra la
> descripción real de K3 en `ALAMO 18` (D-319). El generador de B-18
> todavía no existe; la tabla que va a consultar, sí. **`tiempo_entrega`
> (B-40) se agrega con la misma forma**: `clave` lleva la familia por
> default —18 valores cubren los 387 materiales— o el insumo cuando
> hace falta afinar la excepción; **por proveedor no se puede** — no hay
> catálogo de proveedores (mismo hueco que P-39). `CONOCIMIENTO.md` §15.
> **`factor_conversion_dimensional` (B-25) se agrega igual**: tabique
> pza→m² depende del aparejo del muro, no es constante universal — por
> eso `clave` puede apuntar a un concepto, no solo a insumo o familia.
> `MODELO.md` §2a

---

# 2. Catálogos de vocabulario

```
UNIDAD
  id, clave, nombre                                                    firme
  sinonimo                nombre legible ("Metro Cuadrado")            firme — es lo único no derivable

FAMILIA
  id, nombre, categoria_id  FK a qué categoría pertenece esta familia   firme

SUBFAMILIA
  id, familia_id, nombre                                                firme

FRENTE
  id, nombre                                                            firme — hoy sin uso operativo, pendiente ligar a programa

CLASE_TRABAJO
  id, nombre        destajo · acarreo · subcontrato…                    firme — nuevo (P-02/P-03), ver hallazgo 7
```

### ⚠ HALLAZGO 5 — `Familia` no puede ser una sola tabla plana

El conocimiento documenta que `Familia` significa **tres cosas distintas** según el
catálogo de origen: sustancia en materiales, oficio en trabajos, rango en mano de
obra (`CATALOGOS.md` §5). Y 8 nombres coinciden literalmente por accidente (Eléctrico,
Hidráulico...).

**Si `FAMILIA` es una tabla única sin distinguir de qué universo viene**, esos 8
nombres se van a fusionar en una sola fila cuando deberían ser tres filas distintas
con el mismo texto.

**Se resuelve así:** `FAMILIA.categoria_id` es obligatorio y forma parte de la
identidad — la unicidad es `(nombre, categoria_id)`, no `(nombre)` solo.

### ⚠ HALLAZGO 7 — `Acarreo` no tenía dónde vivir en el dato

`clase` está en el vocabulario del skill desde antes (`erp-construccion.md` §9b:
destajo · subcontrato · acarreo), pero `NODO` nunca tuvo un campo para guardarla.
Sin él, un trabajo `Acarreo` era indistinguible de un `Destajo` en el dato.

**Se resuelve así:** `CLASE_TRABAJO` como tabla abierta, no un `ENUM` de Postgres
—caro de ampliar—. **Las clases de `Trabajos` no son una lista cerrada:** hoy
`Destajo`, `Acarreo` y `Subcontrato`; van a crecer —`Contrato`, `Permuta`,
`Renta`— sin que eso pida una migración de tipo.

La frontera que separa `Flete` (categoría de insumo, en `NODO.categoria`) de
`Acarreo` (clase de trabajo, en `NODO.clase_id`) es **el límite de la obra, no la
dirección**: `Flete` cruza —de fuera hacia adentro, o de adentro hacia afuera—;
`Acarreo` se queda dentro. Evidencia completa en `CONOCIMIENTO.md` §10.2 (P-02/P-03).

---

## 2a. Presentación de compra — el factorizador de unidades (cierra B-25)

Cuatro decisiones cerradas desde el 10 de septiembre (F-1 a F-4,
`PROPUESTA-CUATRO-MODULOS.md` §1, D-86 a D-92) sin diseño formal — la
misma clase de hueco que dejó P-14 o B-39 antes de cerrar: **la política
ya estaba, faltaba la tabla.**

```
PRESENTACION_COMPRA
  id
  material_id        FK Material — nunca FK proveedor: el mínimo de
                      compra es del insumo, no de a quién se le compre
                      (F-2, D-87) — mismo hueco que P-39, no se inventa
                      un catálogo de proveedores para esto               nuevo
  nombre              texto — "camión", "saco"... no es `UNIDAD` del
                      catálogo (esa es de medida; esto es de empaque o
                      compra, `GLOSARIO-DOMINIO.md`: Presentación de
                      compra, no confundir con Unidad)                   nuevo
  factor              NUMERIC — cuántas `unidad_base` (la que ya trae el
                      material en su catálogo) equivale una unidad de
                      esta presentación                                  nuevo
  minimo              NUMERIC, default 1 — cantidad mínima comprable en
                      esta presentación                                  nuevo
  indivisible         boolean — si no se puede comprar una fracción
                      (no hay medio camión)                              nuevo
  fuente              texto — empaque, transporte, norma, o la
                      `PROPUESTA` que aprobó un factor capturado a mano  nuevo
```

**`unidad_base` no es campo nuevo — ya es la `unidad_id` que trae el
material desde su catálogo (F-1, D-86): lo cargado se toma como
definido, nunca se re-pregunta.** Insumo nuevo sin unidad detectable: se
sugiere y se marca solo si es ambiguo — la validación es la excepción,
no el paso por defecto, mismo criterio que el 92% de conceptos que ya se
clasifica solo (`CONOCIMIENTO.md` §11.7).

### Las conversiones se clasifican solas, y eso decide si hace falta `PROPUESTA`

| Conversión | Ejemplo | ¿Cruza dimensión física? | Captura |
|---|---|---|---|
| Empaque | Saco → kg | No | Directa en `factor`, nadie aprueba |
| Transporte | Camión → m³ | No | Directa en `factor`, nadie aprueba |
| Propiedad variable | m³ de arena → kg (densidad) | No, pero varía | Directa, **con aviso** al usarse |
| Dimensional | Tabique pza → m² de muro (aparejo) | Sí | `PROPUESTA` — nunca automática |

> **La regla:** si la conversión se queda dentro de la misma dimensión
> física —masa a masa, volumen a volumen, pieza a pieza— el sistema la
> aplica solo. Si cruza dimensiones o mete una propiedad que varía con
> el contexto, propone y espera — mismo principio que ya rige cada
> automatización de este modelo (`CONOCIMIENTO.md` §14).

**El caso dimensional (F-4, D-91) no vive en `PRESENTACION_COMPRA`.**
Depende del **aparejo**, propiedad del muro, no del insumo — guardado
**por concepto o por insumo, nunca global** (tabique pza→m² cambia si
cambia el aparejo). Reusa `CONSTANTE_FISICA` (`MODELO.md` §1c,
`categoria=factor_conversion_dimensional`) en vez de abrir tabla nueva.

### Qué desbloquea

- **El catálogo se encoge** — una clave por material, no una por
  presentación.
- **El sobrante deja de ser desperdicio.** Comprar 1 camión (14 m³) y
  gastar 0.026 m³ se veía como 13.974 de sobreconsumo; ahora es
  inventario. A nombre de quién queda ese sobrante es **F-3 (D-88): del
  lote de compra, no de un `PRESUPUESTO`** — lo comparten varias obras
  del mismo desarrollo. No es la misma palabra que `Lote` en
  `MOVIMIENTO_ALMACEN` (§5e) —ahí identifica una obra, aquí un lote de
  compra— y **ya se ve en el dato real**: los movimientos `recepcion`
  entran sin `presupuesto_id` en el 100% de las 1,767 filas reales
  (D-337) — la compra siempre entra a existencia general, nunca a
  nombre de una obra. F-3 no pide tabla nueva: ya es lo que el dato hacía
  antes de que se le pusiera nombre.
- **Habilita `MODELO.md` §5g sin falsos positivos**: sin factorizador,
  comparar una compra de 1 camión contra una explosión en m³ se ve como
  una `DESVIACION` de consumo enorme que no existe — la causa
  `cambio_de_presentacion` (§5g) ahora tiene de dónde salir.

### ⏸ Lo que esto NO resuelve

**Sin caso real confirmado todavía.** Esta sesión no verificó si algún
movimiento de `MOVIMIENTO_ALMACEN` ya registra una compra en
presentación distinta de la unidad base — confirmarlo es el primer paso
para poblar `PRESENTACION_COMPRA` con datos reales, más allá del ejemplo
de la arena que ya trae `PROPUESTA-CUATRO-MODULOS.md` §1. El diseño
queda completo; el caso real que lo ejerza, no.

---

# 3. Presupuesto y proyecto

```
PRESUPUESTO
  id, nombre, estado (por SUBÁRBOL, ver hallazgo 6)                    firme
  raiz_id            FK Nodo                                            firme
  tipo               enum: plantilla · obra                             nuevo — cierra P-40, ver abajo

ESTADO_CONGELAMIENTO   (por nodo, no por presupuesto)
  nodo_id            FK Nodo
  estado             enum: diseño · contratado                         firme
  fecha              cuándo cambió                                     firme
```

### ✅ `PRESUPUESTO.tipo` cierra P-40 — y le da hogar a plantilla/instancia del ensamble

**"Prototipo" era convención de nombre, no campo** (`GLOSARIO-DOMINIO.md`,
P-40): nada distinguía, en el dato, un presupuesto de referencia reutilizable
(Zafiro 1.0, Diamante) de uno de obra real (`ALAMO 18`) — ambos eran la misma
fila de `PRESUPUESTO` sin marca. Un solo campo lo resuelve, sin tabla nueva:
`estado` es por nodo (hallazgo 6, abajo) porque el avance de la obra varía
por subárbol; `tipo` es del presupuesto entero porque **una plantilla no dejó
de serlo a medias** — o es la receta reutilizable, o es la obra que la usó.

**Este mismo campo le da hogar a la distinción plantilla/instancia del
ensamble** (`CONOCIMIENTO.md` §5.2, `MODELO.md` §1c más abajo): un ensamble no
declara dos veces si es plantilla o instancia — lo hereda del `PRESUPUESTO`
que contiene su raíz.

### ⚠ HALLAZGO 6 — el estado no puede vivir en `PRESUPUESTO`

El conocimiento decidió explícitamente: *el estado es del nodo, no del presupuesto*
— los planos llegan por partes, cimentación se contrata mientras acabados sigue en
diseño (`CONOCIMIENTO.md` §1.4).

**Si `estado` fuera una columna de `PRESUPUESTO`**, contradice esa decisión de raíz.
Se modela como tabla aparte, por nodo, y el presupuesto no tiene estado propio —
solo se puede preguntar "¿qué % de sus nodos está contratado?".

### ⚠ HALLAZGO 8 — falta una tercera pata de estado: cuánta ingeniería está cargada

`ESTADO_CONGELAMIENTO` dice si un nodo está en diseño o contratado. No dice si **la
ingeniería que lo sustenta ya llegó completa** — y el presupuesto llega por partes,
a veces durante meses (`ALAMO 18`: abril a septiembre, `CONOCIMIENTO.md` §11.8). P-25.

**Se resuelve así:** tabla aparte, mismo patrón que `ESTADO_CONGELAMIENTO` — por
nodo estructural, no por presupuesto entero.

```
ESTADO_CARGA   (por nodo estructural, igual que ESTADO_CONGELAMIENTO)
  nodo_id                 FK Nodo                                        firme
  estado                  enum: incompleto · completo                    firme
  porcentaje_cargado      caché — importe cargado / importe presupuestado.
                           NUNCA fuente de verdad (§2: "nunca guardes el
                           resultado como dato")                          firme
  actualizado_en          cuándo se recalculó — cada vez que entra
                           una parte nueva                                firme
```

**Una carga incompleta nunca bloquea** (D-30). Se carga lo que llegó, `estado`
queda en `incompleto`, y dispara una alerta no bloqueante (D-71, la escalera de
alerta) — no un error. `completo` se marca solo cuando `porcentaje_cargado` da
100% contra el presupuesto vigente.

---

## 3a. Escenario — versiones de la misma obra para comparar antes de decidir (B-39 cierra)

D-107 ya había decidido la política, sin tabla: un escenario cambia
precio/proveedor, alcance o programa — los tres tipos — y uno queda
vigente mientras el resto se archiva, nunca se descarta. El caso real
que probó por qué hace falta no fue una comparación prospectiva: fue
`ALAMO 18` cargada con la versión anterior del catálogo (mortero, antes
de que el cemento lo sustituyera) — sin escenario declarado, la
diferencia se leyó como desviación falsa, 35% de cemento sin explicar,
hasta que costó una investigación (`PRUEBA-ALAMO-18.md` §2, D-116).

### `PRESUPUESTO.tipo` gana un tercer valor — el mismo campo que ya cerró P-40

```
PRESUPUESTO.tipo         enum: plantilla · obra · escenario
PRESUPUESTO.escenario_de_id   FK PRESUPUESTO, nullable — solo si
                          tipo=escenario: la obra real de la que este
                          escenario es candidato                          nuevo
PRESUPUESTO.tipo_cambio   enum: precio_proveedor · alcance · programa,
                          nullable — solo si tipo=escenario, cuál de los
                          tres tipos de D-107 varía                       nuevo
PRESUPUESTO.elegido       boolean, default false — solo si tipo=escenario.
                          El elegido es el único hecho que no se puede
                          derivar de otra tabla —se guarda—; el resto
                          queda archivado, nunca se borra (D-107)          nuevo
```

**Un escenario ya tiene, gratis, su propio árbol y su propio programa** —
`raiz_id` (como cualquier `PRESUPUESTO`) y `ACTIVIDAD.presupuesto_id`
(`MODELO.md` §5c) ya apuntan a cualquier presupuesto, escenario incluido.
Comparar «6 meses contra 8 meses» no pide tabla nueva: son dos
`PRESUPUESTO(tipo=escenario)`, cada uno con su propio `ACTIVIDAD`.

**Crear un escenario de precio/proveedor o de alcance es clonar el árbol
de la obra** (reusando `procedencia=clonación`, canon `LENGUAJE.md` — la
operación de copiar es código, no schema, mismo criterio que excluye el
resto de `MODELO.md` §6); **uno de programa no necesita clonar nada**:
sus `ACTIVIDAD` pueden apuntar a los mismos `concepto_id` de la obra,
solo con `presupuesto_id` distinto — comparar calendarios no exige
duplicar el árbol de costo que no cambia.

**Elegir un escenario no reemplaza la obra — se traduce a ella.** La
identidad de `PRESUPUESTO(tipo=obra)` nunca cambia: una vez que tiene
`ESTIMACION`/`ACTIVIDAD`/`MOVIMIENTO_ALMACEN` reales colgando de su
`id`, intercambiar cuál fila "es" la obra rompería esas referencias. Lo
que gana el escenario elegido se aplica a la obra vía rediseño
(`CONOCIMIENTO.md` §12 — "propone, no aplica", el rediseño se adopta
solo) — el escenario en sí se queda como archivo, `elegido=true`.

### El caso real (D-116) no necesitaba un escenario — necesitaba leer la fecha correcta

`ALAMO 18` no comparó conscientemente dos versiones antes de decidir: el
catálogo base cambió *después* de que la obra se cargara. Ese caso no
pide `tipo=escenario` — pide que la columna «Presupuesto Base» del
reporte de `MODELO.md` §5f lea `VERSION_CONCEPTO` **vigente a la fecha en
que se cargó la obra**, no la vigente hoy. `vigente_desde`/`vigente_hasta`
ya existen (§4a) — es disciplina de consulta, no campo nuevo.

> **B-39 tenía dos preguntas mezcladas bajo un solo nombre.** «Comparar
> opciones antes de construir» (`tipo=escenario`, arriba) y «comparar
> contra la referencia correcta después de construir» (leer
> `VERSION_CONCEPTO` a la fecha, sin campo nuevo) son mecanismos
> distintos — el caso real que motivó B-39 solo necesitaba el segundo.

### Sin caso real todavía

Ningún caso de esta sesión ejercitó `tipo=escenario` en sentido
prospectivo — comparar precio/proveedor, alcance o programa **antes** de
construir. La política (D-107) y el mecanismo quedan listos; falta el
primer caso real que lo use, mismo principio que las devoluciones de
almacén (`MODELO.md` §5e) o `Flete` en los reportes de salida
(`CONOCIMIENTO.md` §4.3).

---

## 3b. Postventa — la casa entregada abre una garantía (P-41 cierra, dato del usuario)

Dato del usuario: modelo completo, no el mínimo. `CONOCIMIENTO.md` §11.20
(D-367 a D-369) ya probó que el proceso es real — 223 movimientos en
cinco meses, $116,319.20 — pero 10 de esos (`"cierre oficinas de
bodega"`, `"oficina bodega"`, `"VENTILADOR PARA OFICINA"`, $11,417.25)
son gasto de oficina/bodega, no garantía de una casa — mismo patrón que
`MOF-00020` en D-360, se excluyen. **Quedan 213 filas reales, $104,901.95,
las que sí ejercen este diseño.**

```
PRESUPUESTO.fecha_entrega   DATE, nullable — cuándo se entregó al
                             cliente. Null = sigue en construcción. No
                             contradice el Hallazgo 6 (`estado` es por
                             nodo): entrega es un solo evento de la obra
                             entera, no una etapa de un subárbol           nuevo

TICKET_GARANTIA
  id
  presupuesto_id       FK PRESUPUESTO — la casa                            nuevo
  fecha_reporte        DATE — cuándo se reporta el defecto. Dato nuevo:
                        el crudo de almacén solo trae la fecha en que se
                        despachó el material para atenderlo, no cuándo
                        se reportó — se captura desde ahora, no hay
                        valor real que reconstruir para los cinco meses
                        ya cargados                                        nuevo
  causa                enum, abierto: humedad_impermeabilizacion ·
                        electrico · acabado_piso_cantera ·
                        estructural_menor · hidraulico_drenaje ·
                        equipamiento · pintura · sin_especificar — del
                        vocabulario real de las 213 filas
                        (`CONOCIMIENTO.md` §11.20); `sin_especificar` es
                        legítimo, no un cajón de sastre — 23 de 213 filas
                        genuinamente no dicen más que "material postventa"  abierto — nuevo
  contratista_id       FK CONTRATISTA — quien resuelve (D-366)             nuevo
  estado               enum: abierto · cerrado                            nuevo

MOVIMIENTO_ALMACEN.ticket_garantia_id   FK TICKET_GARANTIA, nullable —
                             qué ticket generó este despacho; reemplaza
                             la `Referencia` en texto libre como forma de
                             ligar un movimiento a su causa                 nuevo
```

**Costo de garantía es su propia consulta, no una sexta columna de B-71**
(`MODELO.md` §5f) — mismo criterio que ya excluyó ahí a
`PRESUPUESTO(tipo=escenario)`: es otra pregunta, sobre otro periodo (después
de la entrega, no durante la obra). `SUM(MOVIMIENTO_ALMACEN.costo_total)
WHERE ticket_garantia_id IS NOT NULL`, agrupable por `presupuesto_id`,
`causa` o periodo — sin tabla nueva de reporte.

**Lo que este diseño no resuelve retroactivo:** de las 213 filas reales,
160 ($69,771.87) no traen `Lote` real —cayeron en la bolsa general
`Ubicacion=POSTVENTA`— y se quedan sin `presupuesto_id` posible; el
ticket exige una casa desde que se abre, pero no hay forma honesta de
reconstruir a cuál pertenecía cada una de esas 160 filas ya capturadas.
El diseño corrige la captura hacia adelante, no reescribe lo que ya
pasó suelto.

---

# 4. Identidad y versionado

```
VERSION_CONCEPTO
  id, concepto_id (nodo), version, vigente_desde
  huella          hash de (unidad, insumos, cantidades) — NO incluye descripción   firme

EQUIVALENCIA
  id, concepto_a_id, concepto_b_id, tipo (duplicado_exacto|casi_identico|variante_dimensional)
  estado          propuesto · aprobado · rechazado                     firme

CLON
  id, original_id, clon_id, modo (mantener|sustituir)                  firme
```

---

## 4a. Histórico de precios — de dónde sale el precio, y cuándo se congela

> Cierra P-07 (histórico de precios) y P-08 (antigüedad dispar). De paso
> cierra una referencia rota: `CONOCIMIENTO.md` §13.2 citaba un `M-12` que
> no existe en `PENDIENTES-MEJORAS.md`.

`VERSION_CONCEPTO.huella` (arriba) versiona la receta —insumos y
cantidades— a propósito sin precio: la receta cambia rara vez, el precio
todo el tiempo, mezclarlos ahogaría la señal real de «cambió la matriz» en
ruido de mercado. El precio necesita su propio mecanismo, independiente:

```
PRECIO_HISTORICO
  id
  nodo_id          FK Nodo — solo si modo_precio=declarado                  firme
  precio           NUMERIC                                                  firme
  vigente_desde    DATE                                                     firme
  vigente_hasta    DATE, nullable — null = el vigente hoy                   firme
  fuente           enum: catalogo · ingenieria                              firme
```

**`catalogo` es fuente de verdad y versiona sola**, sin validar — mismo
principio que F-1 (D-86: lo cargado se toma como definido). **`ingenieria`
exige validación** antes de aceptarse, y esa validación puede confirmar una
fila ya existente o crear una nueva. `almacen` y `estimacion` se agregan al
enum en §5e, ahora que P-19 y P-18 ya cerraron.

**Nunca se edita una fila cerrada** — mismo principio que
`ENLACE_CUANTIFICACION.vigente`. `NODO.precio_declarado` pasa a ser caché de
la fila vigente, nunca fuente de verdad — mismo principio que
`ESTADO_CARGA.porcentaje_cargado` (hallazgo 8).

### `VERSION_CONCEPTO` gana un campo, y un segundo disparador

```
VERSION_CONCEPTO
  id, concepto_id (nodo), version, vigente_desde
  huella          hash de (unidad, insumos, cantidades) — NO incluye descripción   firme
  pu              NUMERIC — el PU resuelto al crear esta versión, usando
                   PRECIO_HISTORICO de cada insumo a esa fecha. Se congela,
                   nunca se recalcula                                        firme — nuevo
```

**Dos disparadores de versión, no uno**: cambia la huella (§2.2, ya firme),
o **el nodo pasa a `contratado`** (`ESTADO_CONGELAMIENTO`) — este segundo es
nuevo, y fija el `pu` exactamente al momento de contratar, aunque la receta
no haya cambiado ese día.

**`PRECIO_HISTORICO` y `VERSION_CONCEPTO` son independientes.** Que el
precio de un insumo se mueva no crea versión nueva por sí solo: la tabla de
precio registra el movimiento, la versión sigue siendo la misma receta.
**Trabajo y subcontrato son la excepción** — ahí un cambio de precio no pasa
por `PRECIO_HISTORICO` como un insumo más: dispara directo validar o
descartar la versión, porque su precio nace de una negociación puntual, no
de un mercado que fluctúa.

**Solo `ORDEN DE CAMBIO` mueve un PU ya contratado** — `CONOCIMIENTO.md` §13.4, ya firme — con causa, impacto en monto, quién autoriza.

### El tabulador por contratista no toca el PU

```
TABULADOR_CONTRATISTA
  id
  nodo_id          FK Nodo — trabajo o subcontrato                          firme
  contratista_id   FK CONTRATISTA — cierra P-39, ver abajo                   firme — corregido
  precio           NUMERIC — lo pactado con este contratista                firme
  vigente_desde    DATE                                                     firme
  vigente_hasta    DATE, nullable                                           firme
```

Cierra `CONOCIMIENTO.md` §13.2 («tabulador por contratista, con vigencia —
igual que el precio del insumo»). **Tabla separada, a propósito**: el PU es
la referencia fija (`CONOCIMIENTO.md` §13.2: «no es piso ni techo»), y lo
pactado con cada contratista se compara contra él, nunca lo reemplaza.

### `CONTRATISTA` — cierra P-39, evidencia real en el crudo de almacén

`D-175` había verificado que no hay catálogo de proveedores; `P-39` anotó
el mismo hueco para contratistas, «no se inventa». Los cinco meses de
almacén sí lo dan: la columna `Contratista` viene poblada al 100% en cada
movimiento (no solo en recepción, como `Proveedor`), con 39 nombres
reales que se repiten con volumen alto entre docenas de lotes —evidencia
del mismo tipo que ya cerró `PRESENTACION_COMPRA` (B-25, D-348/D-359),
esta vez suficiente para dar de alta la tabla, no solo para confirmar el
hueco:

```
CONTRATISTA
  id
  nombre           texto — tal como aparece en el crudo de almacén         firme — nuevo
```

Mínima a propósito: el crudo no trae oficio, contacto ni identificador
fiscal — solo el nombre. Dos advertencias de captura, no de diseño:
**"Bodega" y "Cuadrilla Postventa" no son contratistas** (son etiquetas
de operación interna, mismo tipo de ruido que `Grupo` en
`CONOCIMIENTO.md` §11.20) y se excluyen al cargar; **"Abelardo
Sanabria"/"Avelardo Sanabria"
son la misma persona**, una sola letra de diferencia — homologa con el
mismo mecanismo que ya resolvió `nescesario`×32 (`EQUIVALENCIA`/
`NORMALIZACION`, `MODELO.md` §4b), no pide tabla propia.

### Lo que esto ya resuelve, de paso

`contratista_responsable_id` (`DEDUCCION`, abajo) y `PRESTAMO.contratista_id`
dejan de apuntar a la nada — ambos citaban «mismo hueco que P-39». La
lectura de `DESVIACION` por contratista (§5g) también se desbloquea: se
agrupa uniendo `nodo_id` contra `TABULADOR_CONTRATISTA.contratista_id`,
sin campo nuevo en `DESVIACION` — mismo criterio de «se calcula al
preguntar» que ya evitó una tabla de comparación en `MODELO.md` §5f.

### Lo que ya quedaba resuelto por otro lado

«Prototipo» es una convención de nombre, no un campo (P-40) — resuelto:
`PRESUPUESTO.tipo` (§3) lo cierra, y de paso le da hogar a
plantilla/instancia del ensamble (§1c, D-325).

---

## 4b. Diccionario de datos — normalización, homologación y grupo funcional (B-60/B-61 cierran)

**Homologación ya tenía tabla, sin saberlo.** `CONOCIMIENTO.md` §16
distingue tres relaciones entre insumos, y la que exige juicio sobre **la
misma cosa** —homologación— es exactamente lo que `EQUIVALENCIA` (arriba)
ya modela: sus tres valores de `tipo` (`duplicado_exacto` ·
`casi_identico` · `variante_dimensional`) son la homologación de
`CONOCIMIENTO.md` §16, con
datos reales ya reunidos en `DICCIONARIO-DATOS.md` §1 y §3 — 10 grupos
"mismo núcleo", 77 variantes dimensionales, 133 casi idénticos. Lo que le
faltaba a `EQUIVALENCIA`/`CLON` no era la relación: era el viaje de
vuelta que `CONOCIMIENTO.md` §16.2 y `CONOCIMIENTO.md` §16.3 describen y
que hoy ninguna tabla resuelve.

```
CLON   (ya existía — gana dos campos, CONOCIMIENTO.md §16.2, CONOCIMIENTO.md §16.3)
  id, original_id, clon_id, modo (mantener|sustituir)                  firme
  reconoce_clave_vieja_al_importar   boolean, default true — si modo=
                                       sustituir, la clave vieja sigue
                                       entrando y se resuelve al original  nuevo
  exporta_clave_vieja                 boolean, default true hasta que el
                                       usuario autorice — individual por
                                       sistema externo, o total             nuevo
```

**Solo homologación viaja de vuelta; normalización no** (`CONOCIMIENTO.md` §16.3):
`pza` no sale como `pza`, sale `PZ` siempre — es forma, no identidad. La clave sí
es identidad: el sistema externo la reconoce por ella, así que la vieja
tiene que poder seguir saliendo hasta que se autorice lo contrario.

```
NORMALIZACION
  id
  forma_sucia            texto — como llega ("pza", "Petreos")            firme
  forma_canonica          texto — como se guarda y como sale siempre       firme
  campo                    enum: unidad · familia · subfamilia ·
                          texto_libre                                     firme
  origen, evidencia,
  capturado_por, fecha       mismo patrón que las otras dos — CONOCIMIENTO.md §16.1
                          exige que las tres guarden su origen             firme
  estado                    propuesto · aprobado · rechazado — mismo
                          enum que `EQUIVALENCIA`                         firme
```

**`GRUPO_FUNCIONAL` es genuinamente distinto: no son la misma cosa, son
intercambiables** (`CONOCIMIENTO.md` §16: "sustituir una por otra es una
decisión de obra, y
cambia el costo"). No cabe en `EQUIVALENCIA` a propósito — ahí, sustituir
no pregunta.

```
GRUPO_FUNCIONAL
  id
  nombre                   texto — ej. "Cable 12", "Poliflex 50 Mts 1\" 5L" firme
  criterio                   texto — qué los hace intercambiables          firme
  origen, evidencia, estado    mismo patrón que arriba                     firme

GRUPO_FUNCIONAL_MIEMBRO
  id
  grupo_id                  FK GRUPO_FUNCIONAL                             firme
  insumo_id                   FK Nodo                                      firme
  atributo_diferenciador        texto, nullable — ej. "Negro", "Blanco" —
                             por qué esta fila y no otra del grupo          firme
```

> **Ya tiene datos reales, no hipotéticos** (`DICCIONARIO-DATOS.md` §5): 5
> grupos, 13 materiales — cuatro por color (cable 8/10/12/14) y uno por
> presentación (`ELE-00044`/`ELE-00046`, poliflex en rollo contra metro
> suelto). Este último ya se confirmó esta sesión con dato real: no es
> error de precio, son presentaciones reales que cuestan distinto por
> volumen (D-323) — y esa misma confirmación **corrige** el marcado de
> "error de precio" que `DICCIONARIO-DATOS.md` §6 le puso a
> `COM-00200`/`ELE-00048` (pija lámina): son dos largos de tornillo
> distintos (1/2" contra 1 1/2"), no el mismo material a dos precios.

### Bitácora de reclasificación — cierra B-61

```
BITACORA_RECLASIFICACION
  id
  nodo_id                       FK Nodo                                    firme
  familia_anterior_id,
  familia_nueva_id                 FK Familia                              firme
  subfamilia_anterior_id,
  subfamilia_nueva_id               FK Subfamilia, nullable                firme
  usuario_id, fecha                                                        firme
```

**"Marcar recalculable la tasa paramétrica" no pide campo en la
bitácora — pide uno en el otro lado.** `ENSAMBLE_PARAMETRO` (§1c) gana
`revisar` (boolean, default false) — mismo patrón que `NODO.revisar`
(P-04): cuando un insumo que alimenta una cohorte cambia de familia, la
tasa que aprendió de él no se recalcula sola, se marca para revisar. Al
escribir en `BITACORA_RECLASIFICACION`, el motor busca qué
`ENSAMBLE_PARAMETRO` dependían de ese `nodo_id` y los marca — misma regla
que ya rige todo el sistema: **propone, no aplica.**

> **`reclasificar_familia` y `resolver_revisar_parametro`, tentativamente
> a Control de obra — con menos certeza que las de arriba.** Extiende el
> mismo criterio (gobierno cruzado entre obras), pero reclasificar familia
> es más catálogo que obra — se acerca más a lo que hoy hace Costos al
> cuantificar y crear precios. Queda anotado como propuesto, no firme;
> confirmar cuando aparezca un caso real de reclasificación.

---

# 5. La propuesta — entidad transversal

> Ver `CONOCIMIENTO.md` §14. Nace para que "propone, no aplica" no tenga 9 bandejas
> distintas.

```
PROPUESTA
  id
  tipo             enum: equivalencia · version · reparto · conversion ·
                    matriz_generada · fusion · clonacion · orden_cambio ·
                    patron_carga
  objeto_id         a qué nodo o línea aplica
  valor_propuesto   JSON — la forma cambia según `tipo`
  evidencia         texto — de dónde salió
  origen            enum: usuario · agente
  modelo            qué motor la produjo — nullable si origen=usuario
  version_modelo    nullable
  confianza         derivada de la evidencia, no declarada por el modelo
  supuestos         JSON — sólo si la respuesta proyecta a futuro
  estado            enum: pendiente · aprobada · rechazada
  resuelto_por, resuelto_en
```

### Por qué `modelo` y `version_modelo`

Una instalación local corre con Ollama y una de red con Groq, y **las propuestas
aprobadas de las dos terminan en el mismo corpus de aprendizaje**. Sin el campo, se
mezclan dos calidades distintas y en tres meses nadie puede explicar por qué el
sistema propone peor. No es para rutear: el perfil de despliegue se decide al
instalar.

### Por qué `confianza` se deriva y no se declara

Un modelo que declara su propia confianza declara lo que suena bien. Derivada de la
evidencia —cuántos casos la respaldan, si la comparación cruza dimensiones físicas—
es auditable, que es la misma razón por la que la evidencia no es opcional.

**Una propuesta de baja confianza nunca se auto-aprueba**, aunque su tipo lo
permitiría, y **no entra al corpus como caso positivo hasta resolverse** — si
entrara, el modelo aprendería de sus propias dudas.

### ⚠ nota, no hallazgo — `valor_propuesto` como JSON es una concesión

Cada `tipo` de propuesta tiene forma distinta (una equivalencia son dos claves; una
conversión es un factor). Modelarlo con una tabla por tipo sería más limpio pero
son nueve tablas para una entidad que hoy no tiene volumen. **Queda anotado como
deuda técnica**, no como error.

### `patron_carga` cierra P-27 — confirmar una vez, no una vez por archivo

El cargador reconoce una tabla sin encabezados por los datos, según ya
fija `CONOCIMIENTO.md` §11.4; cuando no está seguro, propone en vez de
adivinar — dato del usuario, con un cuidado explícito: que confirmar no
se vuelva una cola que crece con cada
archivo nuevo hasta que nadie la revise.

```
valor_propuesto (JSON, tipo=patron_carga)
  firma             hash de la forma estructural — conteo de columnas,
                    posición de los marcadores que identifican clave/
                    cantidad/unidad, y el patrón de llenado de la
                    columna de agrupador (nunca · siempre con prefijo de
                    nivel/etapa · siempre con prefijo de concepto) —
                    nunca el contenido de una fila, P-26/D-351
  mapeo             qué columna es qué campo canon, propuesto por el
                    cargador
```

**El cargador consulta primero si ya existe una `patron_carga` con esa
`firma` exacta, `estado=aprobada`.** Si sí, aplica el mapeo sin volver a
preguntar — la firma es de la *forma* del archivo, no del archivo en sí,
así que un lote nuevo con la misma estructura no genera una propuesta
nueva. Solo pide confirmación **la primera vez que aparece una forma**,
no cada vez que aparece un archivo. El número de decisiones que le
llegan a alguien está acotado por cuántas formas distintas existen, no
por cuántos archivos se cargan — y eso ya se vio: doce archivos de
`ALAMO 18` cayeron en muy pocas formas reales (`CONOCIMIENTO.md` §11.8).

### La firma necesita un dato más para las cinco formas de la ingeniería — cierra P-26

`CONOCIMIENTO.md` §11.8 documenta cinco estructuras reales, y el conteo
de columnas por sí solo separa solo tres grupos: 5 columnas
(`Sin costear`), 6 (`Ajena`) y **7 para Completa, Suelta y Con concepto a
la vez** — la misma firma, si `firma` fuera solo conteo de columnas más
qué columna es cuál. Lo que las distingue no está en qué columna es la
del agrupador, sino en **cómo se llena esa columna**: nunca (`Suelta`,
«sin agrupador, solo insumos»), en la primera fila de cada bloque con un
prefijo de nivel/etapa (`Completa`), o con un prefijo de concepto
(`Con concepto`) — el mismo patrón que ya fijó `CONOCIMIENTO.md` §11.5
(«col 0, clave del agrupador, solo en la primera fila del bloque») y
`CONOCIMIENTO.md` §11.8 («después de una fila vacía siempre viene un
agrupador», 155 de 155 casos). **Sigue siendo estructura, no contenido de una fila**: es el
patrón de llenado de una columna a través de todo el archivo, la misma
clase de dato que ya captura «posición de los marcadores» — solo hacía
falta nombrarlo. `firma` queda así: conteo de columnas, posición de
clave/cantidad/unidad, y si la columna de agrupador está siempre vacía,
siempre con prefijo de nivel/etapa, o siempre con prefijo de concepto.

### `matriz_generada` cierra la mitad de P-22 — ya tenía enum, nunca tuvo forma

`tipo=matriz_generada` lleva en la lista de arriba desde que se escribió
esta tabla, sin `valor_propuesto` propio — el mismo hueco que dejó a
`APRENDIZAJE.md` naciendo de una referencia rota: `CONOCIMIENTO.md`
señalaba «el ciclo del agente que aprende de lo decidido» hacia una
sección que hablaba de otra cosa, la matriz a partir de la descripción,
`IDEAS.md` §1. Esa idea ya traía la decisión de fondo, solo sin schema:
**razonar por analogía, no generar.**

```
valor_propuesto (JSON, tipo=matriz_generada)
  analogo_id            FK Nodo — el concepto o compuesto existente más
                        parecido, con su propia COMPOSICION ya aprobada
  parametros_extraidos  JSON — lo leído de la descripción (espesor,
                        altura máxima, desarrollo…) que escala las
                        cantidades del análogo
  composicion_propuesta JSON — estructura e insumos del análogo,
                        copiados tal cual; solo la cantidad cambia,
                        escalada por los parámetros de arriba
```

**Las cantidades nunca se generan de cero** (`IDEAS.md` §1: «un agente
que las genere produce números plausibles y equivocados, peor que
dejarlas vacías»). Se copian de `analogo_id` y se escalan — verificable
contra un caso real, no adivinanza. Si no hay análogo con parecido
suficiente, no se genera propuesta: se dice, no se rellena.

**El corpus contra el que se busca el análogo no es tabla nueva — es
`PROPUESTA(tipo=matriz_generada, estado=aprobada)` acumulada**, mismo
mecanismo que ya cierra `APRENDIZAJE.md` en general: el rechazo enseña
tanto como la aprobación (§3 de ese archivo — «el rechazo es la mitad
del corpus»), así que una `matriz_generada` rechazada también queda
indexada, no se descarta. El corpus semilla ya existe y es real: los 89
conceptos que solo cambian de prototipo y las 22 familias detectadas
(`DICCIONARIO-DATOS.md`) — no arranca vacío. Buscar cuál es «el más
parecido» sigue siendo código, no schema, mismo criterio que el resto de
§6: esta pasada solo le da forma a lo que ya se decide proponer.

**La otra mitad de P-22 es B-18** (`IDEAS.md` §4): generar por fórmula en
vez de por analogía, para lo estructural donde sí hay cálculo exacto
detrás. Las dos rutas conviven — no compiten — y B-18 sigue abierto,
bloqueado en constantes físicas que este archivo no trae (peso por
metro de varilla, factores de traslape y gancho), no en diseño.

---

## 5a. La alerta — cuando algo no cuadra y nadie lo declaró

> Cierra B-32: **«la alerta no tiene dónde vivir»** — se detectaba y se perdía al
> cerrar la sesión que la encontró. Es el peldaño de abajo de `PROPUESTA` en la
> escalera de D-71: tiene objeto, pero no sugiere un valor — solo dice *«mirá esto»*.

```
ALERTA
  id
  tipo              enum: diferencia_sin_causa · identidad_dudosa · …
                     — abierta, crece igual que PROPUESTA.tipo
  objeto_id         FK Nodo, nullable — a qué nodo, etapa o prototipo aplica
  evidencia         JSON — qué se comparó, con qué método, y qué dio
  parametro_usado   JSON, nullable — el umbral que la disparó
                     (ej. {"umbral_pct": 20}), para ajustar sin tocar código
  primera_vez       timestamp
  ultima_vez        timestamp
  veces_vista       entero, default 1 — sube si la misma alerta (tipo + objeto)
                     reaparece sin resolverse
  estado            enum: activa · resuelta · descartada
  resuelto_por, resuelto_en, nota_resolucion
```

**`veces_vista` es la razón de ser de esta tabla.** Sin ella nadie puede contestar
*«¿esto ya salió antes?»* — la pregunta que decide si algo sigue siendo un aviso o
ya merece atención (B-32, «tres meses seguidos» es cuando deja de ser aviso).

**No es `PROPUESTA` con otro nombre.** `PROPUESTA` sugiere un `valor_propuesto`;
`ALERTA` no sugiere nada, solo señala. Si alguien quiere convertir una alerta en
una propuesta de corrección, crea una `PROPUESTA` nueva que la referencia dentro de
su `evidencia` — no se reusa la fila.

**Nunca se autorresuelve.** Detectar no necesita permiso; corregir sí (D-46). Una
alerta pasa a `resuelta` solo cuando alguien la mira y decide qué era.

Los dos primeros usos, con su regla completa en `CONOCIMIENTO.md` §11.7:

| `tipo` | Dispara cuando | Cierra |
|---|---|---|
| `diferencia_sin_causa` | Prototipo contra ingeniería difiere y la diferencia no cae en ninguna de las nueve causas de `CONOCIMIENTO.md` §13.6 | P-29 |
| `identidad_dudosa` | La razón entre el total cargado y el total del prototipo declarado se desvía más del `umbral_pct` | P-30 |
| `invariante_por_vencer` | Pasan más de `parametro_usado.meses_vencimiento` (default 6, D-129) desde el `corte:` de `INVARIANTES.md` — sin campo nuevo, lee el mismo encabezado que ya lleva todo archivo del cerebro | B-54 |
| `estimacion_sin_respaldo_material` | Al correr `validar_estimacion`, la salida de almacén del insumo testigo (`MOVIMIENTO_ALMACEN`, `motivo` ∈ {`salida_produccion`, `implosion`}) del periodo no alcanza, contra el rendimiento teórico, para los m² que la estimación reclama — más del `umbral_pct` de faltante | B-70 |
| `consumo_material_sin_respaldo_avance` | Mismo cruce, dirección contraria: el insumo testigo consumido excede, contra el rendimiento teórico, lo que el avance reclamado necesita — más del `umbral_pct` de exceso | B-79 |
| `subcontrato_fuera_de_base` | El Real de un subcontrato (D-313) difiere de su Base, en cualquier dirección — sin umbral por %, dato del usuario | B-78 |

**`invariante_por_vencer` no necesita `objeto_id`** — ya es nullable, y aquí
no hay un nodo al que apuntar: es sobre el archivo completo. Dato del
usuario: la resuelve Control de obra, mismo criterio de gobierno cruzado
entre obras que ya asignó `gestionar_rol_funcion`/`asignar_residente`
(D-330) — nueva función atómica `renovar_invariante_valor` → Control de
obra, en la lista de §5b.

### `estimacion_sin_respaldo_material` cierra B-70 — mover el cruce de después del pago a antes

`CONOCIMIENTO.md` §11.17 probó el método a mano: la primera lectura, con
solo abril cargado, decía que la semana 19 de `EST-02010` pagó 293 M²
con 30 sacos de cemento —68.5% sin respaldo—, detectado **después** del
pago, cuando ya no había oportunidad de comparar. La idea de mover el
momento en que corre sigue siendo válida — pero **corregido con cinco
meses reales, el 68.5% era la ventana incompleta, no un problema real**:
esa semana traía 80 sacos, no 30 —los otros 50 llegaron en mayo, fuera
de la ventana de abril—, y en acumulado sobre las ocho semanas reales de
`EST-02010` el respaldo cuadra al 99.8%. `CONOCIMIENTO.md` §11.17.

**El punto de enganche ya existe: `validar_estimacion`** (`MODELO.md`
§5b, asignada a Control de obra desde D-206). Antes de aprobar, corre el
mismo cruce de `CONOCIMIENTO.md` §11.16 y `CONOCIMIENTO.md` §11.17
—salida de almacén del insumo testigo contra el rendimiento teórico— y
si no alcanza para lo reclamado, dispara la alerta en vez de aprobar en
silencio. **Corregido: la comparación es contra el acumulado, nunca
contra el periodo suelto** —el falso positivo de la semana 19 fue
exactamente comparar un periodo aislado—. `evidencia` guarda
`{insumo_testigo, cantidad_almacen_acumulada, m2_soportado_acumulado,
m2_estimado_acumulado, periodo}`; `parametro_usado.umbral_pct` acota
cuánto faltante acumulado es tolerable, mismo mecanismo que
`identidad_dudosa`.

**Cuál insumo es el «testigo» ya no es criterio suelto caso por caso —
es la semilla `TESTIGO_MATERIAL` (`CATALOGOS.md` §12).** El hallazgo
original decía que cemento servía por entregarse a diario y tabique no,
por abastecerse por lote — **corregido: es diferencia de grado, no de
tipo.** Cemento también llega por lote —tandas de diez sacos cada pocos
días, no una entrega diaria—, solo que su tanda es más chica y más
frecuente que la de tabique. Los dos necesitan vista acumulada; lo que
cambia entre insumos es cuánta ventana hace falta acumular antes de que
la comparación sea justa, no si hace falta acumular. Extendido el
cruce a diecisiete conceptos reales (`CONOCIMIENTO.md` §11.20, D-376),
la mayoría confirma la misma lectura dentro del ruido esperado por
redondeo a saco entero — suficiente para dejar de tratarlo caso por
caso. Guardar el insumo usado en `evidencia` de cada alerta sigue
siendo la forma de auditar la elección, ahora contra un catálogo en vez
de contra la memoria de quien configuró la revisión.

**Ya no topado en dato:** cinco meses de almacén y cuatro de avance
(`grid_AvanceOPEventosOpr`) están cargados, y la prueba ya se extendió
más allá de `EST-02010` — ver `consumo_material_sin_respaldo_avance`,
abajo.

**El caso que la motivó originalmente resultó falso positivo (D-375) —
pero ya apareció uno real y más limpio.** `ALB-01212` (repellado muros
fachada) está prácticamente terminado según las tres fuentes de avance
que existen (ingeniería, `PRECIO_REAL`, `grid_AvanceOPEventosOpr`), y su
orden no tiene **un solo movimiento de almacén, de ningún insumo**, en
los cinco meses (`CONOCIMIENTO.md` §11.20, D-378). A diferencia de la
semana 19, aquí no hay ventana incompleta que lo explique — las tres
fuentes ya están de acuerdo en que el trabajo se dio por terminado.
Exactamente el patrón que esta alerta existe para atrapar antes de
aprobar, no meses después con un cruce manual.

**Y un tercer caso, el primero fuera de estructura.** Extendido el
mismo cruce a instalaciones (`CONOCIMIENTO.md` §11.20, D-381/D-382),
sanitaria repite el patrón: `HID-00411` (tubo de conexión hidro-
sanitaria, 3/4") se emitió una sola vez en los cinco meses de
`ALAMO 18` —para el primero de cuatro conceptos activos—, mientras los
otros tres (`ISA-00110`/`00150`/`00210`, mayo a julio) facturan 86.6% a
100% de avance sin que su propio tubo saliera nunca del almacén. Dos
hipótesis de campo nuevas, dato del usuario, junto a las ya anotadas
para `ALB-01212`: el material pudo no hacer falta en la cantidad que
pide la ingeniería, o se trajo de otra obra sin pasar por este almacén
— ninguna confirmable todavía con los datos de este cerebro.

### `consumo_material_sin_respaldo_avance` cierra B-79 — el mismo cruce, vigilando el otro lado

Extender el cruce de `CONOCIMIENTO.md` §11.17 a los demás conceptos que
comparten cemento como testigo (`CONOCIMIENTO.md` §11.20, D-376) confirmó
la lectura en la mayoría, y de paso mostró que
`estimacion_sin_respaldo_material` solo vigila **un** lado: cuando el
material no alcanza para lo reclamado. Nunca vigiló el lado contrario
—cuando el material consumido **excede** por mucho lo que el avance
reclamado necesita—, pese a que el mismo cruce ya lo calcula.

**El caso que lo motiva:** castillo K1 (`EST-02110`) en `ALAMO 18`
consumió 33 sacos de cemento contra 13.65 que su rendimiento teórico
pedía para los M avanzados según `grid_AvanceOPEventosOpr` en sus tres
meses —+141.7%—. **Corregido, cruzando contra una tercera fuente
(`CONOCIMIENTO.md` §11.20): no era exceso, era avance incompleto.** La
ingeniería de `ALAMO 18` diseña castillo K1 tres veces (una por nivel,
339.20 M en total) — más del triple que cualquiera de sus cinco
hermanos, todos ya 97-100% construidos. Castillo K1 mismo va en 71.1%
según `PRECIO_REAL` (Mano de Obra) pero solo 32.8% según
`grid_AvanceOPEventosOpr` — la única fuente de las tres que se quedó
corta, y solo para este concepto. Los 33 sacos reales alcanzan para
268.6 M teóricos, justo entre lo ya avanzado (241.19 M) y el diseño
completo (339.20 M): el cemento seguía el avance real, no el recorte
que una sola fuente alcanzó a capturar.

`evidencia` guarda la misma forma que su espejo:
`{insumo_testigo, cantidad_almacen_acumulada, avance_esperado_acumulado,
periodo}`; `parametro_usado.umbral_pct` acota cuánto exceso acumulado es
tolerable antes de disparar. Ambas alertas corren en la misma pasada de
`validar_estimacion` —un cruce, dos lados posibles de salirse—, y solo
sobre pares `TESTIGO_MATERIAL.confiabilidad` ∈ {`confirmado`,
`consistente`} (`CATALOGOS.md` §12): no tiene caso alertar sobre un par
que todavía no tiene suficiente historia para saber qué es normal.
**Lección del caso que la motivó:** antes de que la alerta se tome como
exceso real, `avance_esperado_acumulado` debería corroborarse contra una
segunda fuente cuando exista —la ingeniería del concepto es la más
disponible, ya cargada siempre—; el mismo `# OP` puede estar completo
en una fuente e incompleto en otra, y ahí es donde este mecanismo
repetiría el falso positivo que ya corrigió D-375 a nivel de periodo.

**Que el hueco de diseño (ningún lado de exceso vigilado hasta hoy)
siga siendo real, aunque el caso que lo mostró se haya resuelto, es
exactamente por qué la alerta vale la pena tenerla corriendo:** el
cruce manual que encontró y luego resolvió el caso de castillo K1 tomó
varias rondas y dos fuentes adicionales — corriendo dentro de
`validar_estimacion`, con la corroboración de arriba, se hace en una
sola pasada en vez de a mano, meses después.

**Y ya apareció el caso real que confirma que hacía falta.**
`ALB-01012` (repellado muro, `ALAMO 18`) consume 42 sacos de cemento
—rendimiento de su propia matriz genérica, no de la ingeniería
específica del lote, que pide mortero y nunca lo mueve (mismo patrón
que B-68/D-308)— contra 9.86 que pide `PRECIO_REAL` a su 24.1%
avanzado: **+326%**. A diferencia de castillo K1, corroborarlo contra
la ingeniería no lo resuelve —contra el diseño completo da +2.8%, casi
exacto—: el material está adelantado a **todas** las fuentes de avance
a la vez, no solo a una que se haya quedado corta. Dos hipótesis de
campo, dato del usuario, no excluyentes: avance físico sin estimar
todavía, o material desviado de esta orden hacia otra actividad. Con
cualquiera de las dos, el faltante no se ve mientras la obra sigue —se
ve hasta el cierre, cuando ya no hay margen para resolverlo.
`CONOCIMIENTO.md` §11.20, D-379.

### `subcontrato_fuera_de_base` cierra B-78 — no hay umbral por %, hay alerta y criterio

`CONOCIMIENTO.md` §11.14/D-313 ya separaba Real-vs-Base de un
subcontrato en dos destinos —crecimiento esperado (mismo alcance, se
absorbe) y adicional al cliente (alcance cambió, `PROPUESTA(tipo=
orden_cambio)`)— pero **cuánto crecimiento es «esperado» antes de
volverse adicional dependía de un umbral por tipo de espacio que nunca
se definió.** Dato del usuario: no hay número. La alerta dispara en
cuanto `Real` difiere de `Base` en cualquier dirección, y quien resuelve
—informado por qué tipo de espacio es, entre otro contexto— decide a
mano de qué lado cae. `evidencia` guarda `{subcontrato_id, base, real,
diferencia_pct}`; no lleva `parametro_usado.umbral_pct` como
`identidad_dudosa` o `estimacion_sin_respaldo_material` — no hay umbral
que parametrizar, ese es justo el punto.

**El lado bajo tiene el mismo criterio, con el mismo mecanismo de
siempre.** `CONOCIMIENTO.md` §11.14 ya lo nombraba para la cochera de
`ALAMO 18` (81% de su base, D-321): no toda baja es ahorro, puede ser
**reducción de alcance** —se construyó menos, por diseño— y eso también
es cambio de alcance, solo que a la baja. `PROPUESTA(tipo=orden_cambio)`
ya soporta esto sin tocarlo: `delta_monto` es «NUMERIC con signo» desde
que se escribió (§5, D-334) — un descuento al cliente es la misma fila,
con el signo al revés. Si en cambio es variación normal del mismo
alcance, se absorbe igual que el crecimiento esperado: ninguna de las
dos mitades simétricas pide una propuesta.

**Los tres casos reales conocidos nunca ejercieron el lado alto:**
pergolado asador 100% de su base, impermeabilización 99.4%, pergolado
cochera 81% —confirmada como reducción real por diseño, no error
(D-321)—. El umbral por tipo de espacio que B-78 pedía definir deja de
hacer falta: no hay umbral, hay alerta bidireccional más criterio de
quien resuelve.

---

## 5b. Roles y permisos — quién puede hacer qué

> Cierra P-21: seis roles (R-1, D-204 · Superintendente agregado después,
> D-278), catorce funciones atómicas (R-3, D-206), y las dos preguntas que
> faltaban para cerrar el módulo — confirmadas con el usuario.

```
ROL
  id, nombre        Residente · Supervisor · Superintendente · Costos ·
                     Cotizador · Control                                    firme

FUNCION_ATOMICA
  id, clave         trazar · aprobar_trazo · registrar_avance ·
                     comprometer_gasto · capturar_causa_desviacion ·
                     revisar_patrones_desviacion · aprobar_version_concepto ·
                     pactar_precio_contratista · aplicar_descuento ·
                     autorizar_orden_cambio · aprobar_propuesta ·
                     resolver_alerta · clasificar_manualmente ·
                     correr_invariantes · anotar_plano ·
                     validar_estimacion                                    firme
                     · originar_incidencia · aprobar_incidencia ·
                     validar_incidencia · ejecutar_incidencia ·
                     cerrar_incidencia · solicitar_cierre_frente ·
                     aprobar_cierre_frente · validar_cierre_frente ·
                     editar_estructura_programa · editar_fechas_programa ·
                     proponer_precio_nuevo · aprobar_precio_nuevo ·
                     gestionar_rol_funcion · asignar_residente ·
                     asignar_supervision · reclasificar_familia ·
                     resolver_revisar_parametro                          nuevo — B-73/B-75, ver abajo
                     · renovar_invariante_valor                          nuevo — B-54, ver abajo

ROL_FUNCION
  id, rol_id FK, funcion_id FK                                              firme
```

**Muchos a muchos, no disjunto.** La misma función puede estar en varios roles
a la vez — Residente y Supervisor pueden compartir `registrar_avance` sin que
asignársela a uno se la quite al otro. Es la misma «combinación, no bloque
cerrado» de R-2 (D-205), y el mismo patrón que ya se repitió cinco veces en
este cerebro: nada reasigna, se agrega encima.

**Primeras asignaciones concretas de `ROL_FUNCION`, cerrando B-45:** quién
traza y quién anota el plano — ver §1b. Dieciséis de las veintiocho
funciones existen desde P-21 o de cierres posteriores; las asignaciones
reales se agregan según aparece el caso, no todas de una vez — las doce
que agrega esta pasada (abajo) son el siguiente caso concreto, no las
últimas.

**`validar_estimacion` cierra B-75: se asigna a Control de obra, sin
formalizar Compras como rol propio (dato del usuario).** Compras sigue
sin existir en `ROL` — Control de obra absorbe la función en la práctica,
sin que eso impida reasignarla después: `ROL_FUNCION` es muchos-a-muchos
precisamente para que una asignación no sea definitiva.

> **La reasignación no pide mecanismo nuevo — pide dueño para el
> mecanismo que ya existe.** `ROL_FUNCION` ya es una tabla, no una regla
> de código: reasignar `validar_estimacion` de Control de obra a otro rol
> es un `INSERT`/`DELETE` sobre esa tabla, no un cambio de esquema. Lo que
> faltaba —y sigue faltando en el resto del modelo— es **quién tiene
> permiso de tocar `ROL_FUNCION` misma**. Se agrega `gestionar_rol_funcion`
> (diecisieteava función, asignada a Control de obra, mismo criterio que
> el usuario dio para `validar_estimacion`) — es la función que hace
> posible reasignar todas las demás, incluida ella misma.

### La lista completa — qué está asignado y qué no (pedida por el usuario)

`ROL_FUNCION` ya es la respuesta de fondo a "poder reasignar quién puede
hacer qué": es una tabla, no una regla de código — `gestionar_rol_funcion`
(arriba) decide quién puede editarla, no un tipo de dato nuevo. Esto es
el inventario que faltaba encima: las treinta y cuatro funciones a la
fecha, en un solo lugar.

| Función | Rol(es) asignados | Fuente |
|---|---|---|
| `trazar` | Costos, Control de obra, Residente, Supervisor | §1b, B-45 |
| `aprobar_trazo` | Control de obra | §1b, B-45 |
| `anotar_plano` | Residente, Supervisor | §1b, B-45 |
| `validar_estimacion` | Control de obra | dato del usuario, cierra B-75 |
| `originar_incidencia` | Residente, Supervisor, Control de obra | §5c, D-329 |
| `aprobar_incidencia` | Supervisor | §5c, D-329 |
| `validar_incidencia` | Control de obra | §5c, D-329 |
| `ejecutar_incidencia` | Residente | §5c, D-329 |
| `cerrar_incidencia` | Supervisor | §5c, D-329 |
| `solicitar_cierre_frente` | Residente | §5c, D-329 |
| `aprobar_cierre_frente` | Supervisor | §5c, D-329 |
| `validar_cierre_frente` | Control de obra | §5c, D-329 |
| `editar_estructura_programa` | Control de obra | §5c, D-329 |
| `editar_fechas_programa` | Residente | §5c, D-329 |
| `proponer_precio_nuevo` | Costos | D-329 |
| `aprobar_precio_nuevo` | Control de obra **y** Superintendente (los dos) | D-329 |
| `gestionar_rol_funcion` | Control de obra | dato del usuario |
| `asignar_residente` | Control de obra | dato del usuario |
| `asignar_supervision` | Control de obra | dato del usuario |
| `reclasificar_familia` | Control de obra — propuesto, menos firme | dato del usuario, extendido |
| `resolver_revisar_parametro` | Control de obra — propuesto, menos firme | dato del usuario, extendido |
| `renovar_invariante_valor` | Control de obra | dato del usuario, D-345 |
| `registrar_avance` | **Sin asignar** | P-21 |
| `comprometer_gasto` | **Sin asignar** | P-21 |
| `capturar_causa_desviacion` | **Sin asignar** | P-21 |
| `revisar_patrones_desviacion` | **Sin asignar** | P-21 |
| `aprobar_version_concepto` | **Sin asignar** | P-21 |
| `pactar_precio_contratista` | **Sin asignar** | P-21 |
| `aplicar_descuento` | **Sin asignar** | P-21 |
| `autorizar_orden_cambio` | **Sin asignar** | P-21 |
| `aprobar_propuesta` | **Sin asignar** | P-21 |
| `resolver_alerta` | **Sin asignar** | P-21 |
| `clasificar_manualmente` | **Sin asignar** | P-21 |
| `correr_invariantes` | **Sin asignar** | P-21 |

**Veintidós asignadas, doce sin asignar — a propósito, no por olvido.**
Las doce existen como clave desde P-21 (D-206): están catalogadas para
que el sistema pueda apuntar a ellas, pero nunca tuvieron un caso
concreto que forzara decidir el rol, y este cerebro no asigna sin
evidencia. Se cierran conforme aparezca el caso, igual que las
veintidós de arriba se cerraron cuando apareció el suyo.

> **Todas estas asignaciones son `propuesto`, no `firme`, salvo las
> heredadas de P-21/B-45** — son la primera pasada de un criterio nuevo
> (gobierno cruzado entre obras → Control de obra), no verificadas contra
> un caso real todavía. `gestionar_rol_funcion` existe precisamente para
> poder corregirlas sin tocar esquema el día que un caso real diga lo
> contrario.

**`comprometer_gasto` no lleva tope por monto.** Es binaria: el rol la tiene o
no la tiene, sin límite de monto asociado. Si algún día hace falta controlar
el gasto en subcontratos específicamente, la vía no es un tope por rol — es
modelarlos como matriz (`COMPOSICION`), donde el control ya es por línea, no
por permiso.

### El alcance de datos — quién ve qué obra, aparte de quién hace qué

`ROL_FUNCION` dice qué **acciones** puede hacer cada rol. Falta la otra mitad: qué
**datos** ve — es una regla general del sistema, no solo de reportes de insumo.

| Rol | Ve |
|---|---|
| **Residente** | Sus obras asignadas |
| **Supervisor** | Hereda las obras de los residentes que supervisa |
| **Superintendente** | Hereda las obras de los supervisores que le reportan — mismos privilegios que Supervisor, alcance más amplio |
| **Control** | Todas las obras. Filtra por obra, por residente, por supervisor o por superintendente |
| **Costos** | Todas las obras, igual que Control — consecuencia de que cuantificar y fijar precio son procesos compartidos entre obras, no una asignación arbitraria |
| **Cotizador** | No aplica todavía — no es un rol activo, ver abajo |

**Es jerárquico, no una lista plana**: el alcance de cada nivel se deriva de a
quién supervisa o le reporta, no se declara obra por obra. Cuatro niveles:
Residente → Supervisor → Superintendente → Control.

Aplica a todo lo que el sistema muestra, no solo a insumos: reportes, Consulta
(`gravity-obra.md` §6), avance, incidencias.

### El campo que lo sostiene — cierra B-74

`ROL_FUNCION` conecta un **tipo** de rol con lo que puede hacer. Faltaba la
pieza de abajo: **quién es la persona**, y a qué o a quién queda asignada.

```
USUARIO
  id, nombre, correo                                                     firme
  activo            boolean — se retira, no se borra                     firme

USUARIO_ROL
  id, usuario_id FK, rol_id FK                                           firme

RESIDENTE_OBRA
  id, usuario_id FK USUARIO, presupuesto_id FK PRESUPUESTO                firme

SUPERVISION
  id, supervisor_id FK USUARIO, supervisado_id FK USUARIO                 firme
```

**`USUARIO_ROL` es muchos-a-muchos, mismo patrón que `ROL_FUNCION`** — una
persona puede tener más de un rol (D-205), y quitarle uno no le quita el
otro.

**No hay tabla `OBRA` aparte** — `PRESUPUESTO` ya es esa entidad (§3): su
`raiz_id` cuelga del árbol completo de una obra. `RESIDENTE_OBRA` apunta ahí,
cerrando la asignación que C-3 (`PROPUESTA-CUATRO-MODULOS.md` §2) ya había
anotado sin tabla.

**`SUPERVISION` es una sola tabla para los dos niveles de la cascada**, no
dos — Supervisor-sobre-Residente y Superintendente-sobre-Supervisor tienen
la misma forma (`usuario` que supervisa a `usuario`); cuál de los dos es
cada fila lo dice el rol de cada quien en `USUARIO_ROL`, no un campo nuevo.
El alcance de Superintendente y Control (D-277 a D-279) se calcula
recorriendo esta tabla, no se declara aparte.

**Cierra aquí: `asignar_residente` y `asignar_supervision`, a Control de
obra.** Mismo criterio que el usuario dio para `validar_estimacion` y
para `gestionar_rol_funcion` arriba: quién queda asignado a qué obra, y
quién supervisa a quién, es gobierno cruzado entre obras — no de una obra
en particular —, y Control de obra ya es el rol con visibilidad completa
para ejercerlo.

### Costos: cuantifica y crea precios, con doble aprobación — cierra B-73 en ese punto

Costos **cuantifica** (produce presupuesto) y **crea precios nuevos** — estos
últimos necesitan aprobación de **Control de obra y Superintendente**, los
dos, no uno solo. `proponer_precio_nuevo` → Costos; `aprobar_precio_nuevo` →
Control de obra **y** Superintendente.

> ⚠ **Primer caso de aprobación doble obligatoria, no de cadena secuencial
> con salto.** `INCIDENCIA` y `CIERRE_FRENTE` (§5c) resuelven "quién aprueba"
> con un solo campo que puede quedar en null si el paso se salta (D-269) —
> aquí hacen falta **los dos**, no uno de dos posibles. Se modela como
> `PROPUESTA` (`tipo=precio_nuevo`) con dos campos nuevos, en vez de forzar
> el patrón de un solo `aprobado_por`:
>
> ```
> PROPUESTA   (gana dos campos, solo aplican si tipo=precio_nuevo)
>   aprobado_control_en          DATE, nullable                      propuesto
>   aprobado_superintendente_en  DATE, nullable                      propuesto
> ```
>
> `estado` pasa a `aprobada` solo cuando los dos están llenos — el motor lo
> verifica, no un campo booleano nuevo que pueda desincronizarse de los
> dos anteriores.

### Programa: cinco funciones de incidencia, tres de cierre de frente, dos de edición — cierra B-73

Formaliza en `ROL_FUNCION` lo que la política de `PROPUESTA-CUATRO-MODULOS.md`
§4 ya describía en prosa para `INCIDENCIA`, `CIERRE_FRENTE` y `ACTIVIDAD`
(§5c), sin una sola asignación todavía escrita como tabla:

| Función | Rol(es) | Por qué |
|---|---|---|
| `originar_incidencia` | Residente, Supervisor, Control de obra | Los tres pueden originarla — quien lo hace se salta su propio paso de aprobación/validación (D-269) |
| `aprobar_incidencia` | Supervisor | Salvo que Supervisor haya originado |
| `validar_incidencia` | Control de obra | Salvo que Control de obra haya originado |
| `ejecutar_incidencia` | Residente | Siempre, en los tres casos |
| `cerrar_incidencia` | Supervisor | "El Supervisor siempre da seguimiento hasta que cierra" — nunca se salta |
| `solicitar_cierre_frente` | Residente | Al 90% de avance del frente |
| `aprobar_cierre_frente` | Supervisor | |
| `validar_cierre_frente` | Control de obra | |
| `editar_estructura_programa` | Control de obra | Vincular actividades, marcar duración desde presupuesto/paramétrico — `origen_captura` manual-con-diseño y por-carga-estructura |
| `editar_fechas_programa` | Residente | Ajustar fechas sin tocar estructura — `origen_captura` manual-sin-diseño y por-carga-fechas |

> **El patrón se repite en los tres módulos que este cerebro ya modeló con
> cadena de aprobación**: quien origina no se autoaprueba ni se autovalida
> (D-269), y hay un rol que da seguimiento hasta el cierre sin excepción.
> No es tres veces la misma regla por casualidad — es la misma regla,
> aplicada donde aparece.

### Cotizador: la responsabilidad existe, el rol activo todavía no

Dos artefactos, no uno:

| Artefacto | Cuándo | Qué es |
|---|---|---|
| **Highlight** | Antes de la ejecución | El cliente pide un estimado preliminar |
| **Adicional al presupuesto** | Ya en ejecución | Presupuesto extra sobre lo contratado |

Los dos se **folian** — y al aprobarse, se vuelven **control de cambio**
(`CONOCIMIENTO.md` §13.4), mismo mecanismo, no uno nuevo. Cotizador también
lleva el registro de conceptos nuevos, y una cotización se estructura como
presupuesto PU (`CONOCIMIENTO.md` §7, mismo modo de valuación ya definido).

> **Hoy esto lo ejecuta Control de obra** — Cotizador no es todavía un rol
> separado en la práctica. Puede evolucionar a rol propio, o fundirse con
> Costos; ninguna de las dos está decidida.

---

## 5c. Programa — precedencias, calendario, tramos y los dos cuantificadores (P-20 cierra)

**Las diez decisiones de política ya estaban cerradas**
(`PROPUESTA-CUATRO-MODULOS.md` §4, P-1 a P-10) desde antes de que existiera
tabla — `ACTIVIDAD` era un stub de tres campos con `INCIDENCIA` y
`REGISTRO_AVANCE` colgando de él. Esta pasada le pone forma al resto: qué
va antes que qué, con qué calendario, partido en cuántos tramos, y los dos
cuantificadores que P-9 ya distinguía sin tabla donde vivir.

```
ACTIVIDAD
  id
  concepto_id           FK Nodo                                             firme
  presupuesto_id        FK PRESUPUESTO                                      firme
  origen_captura        enum: manual_con_diseño · manual_sin_diseño ·
                         por_carga_estructura · por_carga_fechas — el mismo
                         patrón en los dos orígenes: Control de obra edita
                         estructura, Residente edita fechas                 firme
  modo_duracion         enum: capturada · calculada_rendimiento ·
                         preestablecida_nivel · derivada_fechas — la cuarta
                         es «manual sin diseño»: no hay días ni rendimiento,
                         se derivan de fecha_fin − fecha_inicio              firme
  duracion_dias         NUMERIC, nullable si modo_duracion=derivada_fechas   firme
  disparador_fecha      enum: precedencia · recurso · contractual — el
                         contractual lo fija el anticipo o la junta de
                         arranque, no una precedencia técnica ni una
                         cuadrilla libre                                    firme
  fecha_disparador      DATE, nullable — solo si disparador_fecha=contractual firme
  fecha_inicio_real,
  fecha_fin_real        nullable — capturadas cuando origen_captura=
                         manual_sin_diseño o al registrarse avance          firme
  fecha_inicio_temprana / fecha_inicio_tardia /
  fecha_fin_temprana / fecha_fin_tardia          calculadas por el motor
                         CPM — caché, nunca fuente de verdad (§2)           calculado
  holgura                calculada, misma regla                             calculado
  es_ruta_critica        boolean, calculado — recalcula siempre (P-3); solo
                         dispara aviso cuando este valor cambia de una
                         corrida a la siguiente, nunca cuando solo corren
                         las fechas                                         calculado
```

### `modo_duracion=preestablecida_nivel` + `disparador_fecha=contractual` cierran B-48

Un nivel que se contrata **terminado** —un solo subcontratista entrega el
paquete completo, sin actividades internas que programar— no necesita
tabla ni campo nuevo: ya es esta combinación exacta. La duración no se
calcula del rendimiento ni se captura a mano: es la misma para ese nivel
en cualquier obra (`preestablecida_nivel`). El arranque no depende de una
precedencia técnica ni de una cuadrilla libre: lo dispara el anticipo o
la junta de arranque (`contractual`, con `fecha_disparador`). Dato del
usuario: en `ALAMO 18` van por esta ruta Cancelería, Carpintería,
Herrería, Cubiertas, Pérgolas e Impermeabilizante — «tiene ingeniería
cargada» y «se contrata terminado» resultaron ejes independientes, no el
mismo (`CONOCIMIENTO.md` §11.13). Muebles/Iluminación no entra aquí: se
programa como el resto, con `modo_duracion` calculada o capturada.

### `modo_duracion=calculada_rendimiento` tiene su primer caso real: 30 semanas para el prototipo Diamante

Dato del usuario, primer programa completo por **prototipo** (no por
lote): cimentación, muros, castillos, cadenas, losas, barda perimetral y
la estructura del asador se programan con `calculada_rendimiento`
—cantidad del prototipo ÷ rendimiento de la cuadrilla, ver `CATALOGOS.md` §10— y reconstruyen Cimentación→Azotea en 21 semanas. Cancelería,
Carpintería, Herrería y Pérgola Cochera se quedan en
`preestablecida_nivel` (B-48, arriba): sus semanas son dato del usuario,
no derivadas de rendimiento — confirma que las dos formas de duración
coexisten en el mismo programa sin pisarse. `CONOCIMIENTO.md` §11.14.

### ⚠ Precedencia, calendario y tramo comparten el mismo eje de confianza

Precedencia (P-1), tramo (P-5) y el origen de una duración (arriba) usan
la **misma clasificación de tres**: técnica (física, se propone sola) ·
recurso (media confianza, cambia si cambia la disponibilidad) · decisión
(baja confianza, es preferencia de quien programa). No es casualidad —es
la misma pregunta, "¿por qué existe este orden?", hecha en tres lugares
del árbol. Un solo enum se reutiliza en las tres tablas.

```
PRECEDENCIA
  id
  predecesora_id        FK ACTIVIDAD                                        firme
  sucesora_id            FK ACTIVIDAD                                       firme
  tipo_vinculo            enum: fin_inicio · inicio_inicio · fin_fin         firme
  traslape_espera         NUMERIC — días; negativo es traslape, positivo
                          es espera                                          firme
  origen                  enum: tecnica · recurso · decision                 firme — P-1
  confianza                enum: alta · media · baja — derivada de origen,
                          no declarada (mismo patrón que `PROPUESTA.confianza`,
                          §5)                                                firme

CALENDARIO_OBRA
  id
  presupuesto_id          FK PRESUPUESTO — uno por obra                      firme — P-2
  dias_no_habiles          definición (feriados, domingos, lo que aplique)   firme

CALENDARIO_EXCEPCION
  id
  calendario_obra_id       FK CALENDARIO_OBRA
  cuadrilla_id               FK Cuadrilla (semilla, B-07)                     firme
  regla                       override sobre el global — ej. "no trabaja
                             sábados". El global manda salvo excepción       firme — P-2

TRAMO
  id
  actividad_id               FK ACTIVIDAD                                    firme
  orden                        posición dentro de la actividad                firme
  fecha_inicio, fecha_fin                                                     firme
  origen                       mismo enum que `PRECEDENCIA.origen` — técnica
                             se deduce sola de una precedencia física (la
                             cadena que interrumpe el muro); recurso o
                             decisión se capturan a mano, no hay de dónde
                             deducirlos                                      firme — P-5
  reparto_material             NUMERIC o % — calculado por default,
                             editable (`MEMORIA.md` D-259, «declarado
                             menos calculado»)                                firme — P-5
```

### El segundo cuantificador no es tabla nueva, es otro destino del mismo trazo

`PROPUESTA-CUATRO-MODULOS.md` §4 ya distinguía los dos sin tabla: el
cuantificador de presupuesto (§1b) **fija el techo**, no se pretende
superar; el cuantificador de programación **mide contra ese techo, con
tolerancia**. Mismo mecanismo de `TRAZO`, otro destino del enlace:

```
ENLACE_CUANTIFICACION_PROGRAMA
  id
  trazo_id                FK TRAZO (§1b) — el mismo trazo puede alimentar
                          presupuesto y programa a la vez, con dos enlaces  firme
  actividad_id              FK ACTIVIDAD, en vez de FK Nodo                  firme
  medida, factor              igual que `ENLACE_CUANTIFICACION`              firme
  vigente                      igual                                        firme
```

**El umbral no es mecanismo nuevo.** Reusa `ALERTA.parametro_usado`
(`MODELO.md` §5a), que ya trae `{"umbral_pct": 20}` como su propio ejemplo.
Cruzar el umbral dispara la alerta; Control decide si es incidencia real
o se descarta (P-9) — no crea la incidencia por sí solo.

### Frente gana su primer par de tablas propias — cierra B-56, P-6 y P-20 en ese punto

`Frente` seguía siendo puro catálogo informativo (`CATALOGOS.md`: "no
valida, no impide, no calcula"). El tope de cuadrillas (B-56, ya resuelto
como política) y el cierre de frente son sus dos primeros eventos reales
— ninguno lo convierte en validador: el tope se declara, no se calcula
del catálogo, y el cierre pregunta, no impide.

```
FRENTE_TOPE_CUADRILLA
  id
  frente_id                FK Frente                                        firme
  oficio_id                  FK Familia (el oficio, no el frente completo —
                            cimentación usa albañil y peón en instalaciones
                            a la vez, eso es normal)                          firme
  tope                       INTEGER — cuántas cuadrillas del mismo oficio
                            caben sin estorbarse                             firme — P-6
  capturado_por, fecha         media confianza, mismo origen que una
                            precedencia de recurso                           firme

CIERRE_FRENTE
  id
  frente_id                 FK Frente
  solicitado_por             FK USUARIO — Residente, al 90% de avance        firme
  aprobado_por, aprobado_en   FK USUARIO — Supervisor                         firme
  validado_por, validado_en    FK USUARIO — Control de obra                  firme
  incidencia_calidad_id        FK INCIDENCIA, nullable — si el cierre
                              levantó una                                    firme

INCIDENCIA
  id
  actividad_id        FK ACTIVIDAD — nullable si efecto crea una que aún no existe
  motivo               enum: las nueve causas (`CONOCIMIENTO.md` §13.6)    firme
  efecto                enum: pausa_actividad · crea_actividad ·
                        crece_actividad · propone_actividad (D-268)       firme
  origen_usuario_id    FK USUARIO
  origen_rol_id         FK ROL — bajo cuál rol se originó, si el usuario
                        tiene más de uno (`USUARIO_ROL`)                   firme
  estado                enum: originada · aprobada · validada · ejecutada
                        · cerrada · descartada                             firme
  aprobado_por, aprobado_en      nullable — null si quien origina se lo
                                  salta (D-269)                            firme
  validado_por, validado_en      nullable — mismo caso                    firme
  cierra_supervisor_id  FK USUARIO — el seguimiento, siempre (D-269)      firme
  evidencia             texto

REGISTRO_AVANCE
  id
  actividad_id          FK ACTIVIDAD
  fuente                 enum: fisico · pagado — nunca se sobrescriben,
                         cada uno su fila (`CONOCIMIENTO.md` §13.7, D-264)  firme
  tipo                   enum: numero · porcentaje · trazo (D-271)        firme
  valor                  numérico — nullable si tipo=trazo
  trazo_id               FK TRAZO (§1b) — nullable si tipo≠trazo
  capturado_por          FK USUARIO
  fecha
```

**`INCIDENCIA` no se autoaprueba ni se autovalida** — el patrón de D-269 se
modela dejando `aprobado_por`/`validado_por` en null cuando el paso se salta,
no con un valor especial. **`REGISTRO_AVANCE` separa físico de pagado por
fila, no por columna** — es la forma más directa de que ninguno sobrescriba
al otro: son filas distintas, con su propia fecha y su propio autor.
**`CIERRE_FRENTE` sigue la misma forma que `INCIDENCIA`** a propósito —tres
pasos, cada uno nullable si se salta— porque es el mismo patrón de
aprobación, aplicado a un trámite distinto.

**Dos reglas de política no piden campo nuevo, piden reusar lo que ya
existe:**

- **P-4, fechas contratadas no se mueven solas** — reusa
  `ESTADO_CONGELAMIENTO` (§3) sobre el `concepto_id` de la actividad: una vez
  `contratado`, `fecha_inicio_real`/`fecha_fin_real` no se editan directo,
  igual que el precio no se edita directo en un nodo contratado. Reprogramar
  propone la fecha nueva; alguien la acepta.
- **P-7, el rendimiento real nunca sobrescribe el teórico** — `duracion_dias`
  quedó `firme` como la teórica; el real (`CONOCIMIENTO.md` §11.16,
  `CONOCIMIENTO.md` §11.17, ya con datos de `ALAMO 18`) da una **segunda
  proyección calculada al vuelo**, comparando contra `duracion_dias`, no un
  campo paralelo que duplique el dato y pueda desincronizarse. Si diverge
  más de un umbral
  sugerido (2 a 4 semanas de datos, no un número fijo), avisa — nunca
  reprograma sola.

> **Quién puede escribir cada campo sigue sin nombrar** — mismo pendiente
> en todo el módulo: aprobar/validar/ejecutar una incidencia, solicitar o
> validar un cierre de frente, editar estructura contra editar fechas
> (P-20 arriba) — ninguna tiene clave todavía en `FUNCION_ATOMICA`.

### ⏸ Lo que esto sigue sin resolver

- **Reglas de visualización declaradas como regla de negocio** (rótulo de
  barra, las dos escalas de Gantt, vincular/configurar vínculo por
  separado) — el texto de política las marca explícitamente como no
  preferencia de pantalla, pero no piden tabla propia todavía: son
  parámetros de una pantalla, no una entidad. Se resuelve al diseñar esa
  pantalla, no aquí.
- **`FUNCION_ATOMICA`** no gana ninguna clave nueva en esta pasada — quedan
  nombradas en prosa (arriba), sin asignar a rol.

---

## 5d. Estimación — el tope, la conciliación y las tres formas de ajustar el pago

Cierra B-76. La política ya estaba completa (`CONOCIMIENTO.md` §13.8); esto
es su forma de tabla.

```
ESTIMACION
  id, presupuesto_id FK PRESUPUESTO
  periodo_inicio, periodo_fin      semanal (`CONOCIMIENTO.md` §13.8)       firme
  fuente             enum: erp_externo · manual (D-284)                   firme
  estado             enum: capturada · devuelta · validada · pagada       firme
  validado_por        FK USUARIO — bajo validar_estimacion, D-299
  validado_en

ESTIMACION_LINEA
  id, estimacion_id FK ESTIMACION
  concepto_id         FK Nodo — nullable si es fuera de catálogo
  actividad_id         FK ACTIVIDAD (§5c) — nullable
  incidencia_id         FK INCIDENCIA (§5c) — nullable, si esta línea nace
                        de una incidencia ya aprobada
  cantidad_avance       lo que esta línea reconoce en este periodo
  monto
  excede_tope           caché — compara contra el contratado vigente
                        (D-285) al validar. NUNCA fuente de verdad, mismo
                        principio que `ESTADO_CARGA.porcentaje_cargado` (§3)

DEDUCCION
  id, estimacion_linea_id FK ESTIMACION_LINEA
  tipo                enum: sobrepago · rehacer_trabajo (D-289)           firme
  monto
  contratista_responsable_id   FK CONTRATISTA — cierra P-39 (§4a)          firme — corregido
  absorbe_empresa      boolean — true si el responsable ya no está activo

RETENCION
  id, estimacion_linea_id FK ESTIMACION_LINEA
  monto                — solo si el contratista de esa línea es
                        subcontrato (D-290)

PRESTAMO
  id, contratista_id   FK CONTRATISTA — cierra P-39 (§4a)                 firme — corregido
  monto
  salda_via            enum: avance_obra · estimacion_futura (D-290)      firme
  saldo_restante
```

**No hay columna `tope` guardada en ningún lado** — el tope es el contratado
vigente (D-285), se lee de donde ya vive (`VERSION_CONCEPTO`/`ACTIVIDAD`),
nunca se copia. Guardarlo aparte lo desincroniza en cuanto el contratado
cambie.

**`contratista_responsable_id` y `PRESTAMO.contratista_id` ya apuntan a
`CONTRATISTA`** — cierran junto con `TABULADOR_CONTRATISTA.contratista_id`
(§4a, D-366): mismo hueco de P-39, resuelto una sola vez para las tres
FK.

> **Quién escribe cada campo sigue sin nombrar** — mismo pendiente que
> `INCIDENCIA` y `REGISTRO_AVANCE`: las funciones de capturar, devolver y
> conciliar una estimación no tienen clave en `FUNCION_ATOMICA` todavía.
> Solo `validar_estimacion` (D-299) ya existe, sin asignar a rol.

---

## 5e. Almacén — surtido, consumido y el hueco de las devoluciones (P-19/B-16 cierran)

El primer cruce real (`CONOCIMIENTO.md` §11.15 a `CONOCIMIENTO.md` §11.19)
ya probó el método sobre el export mensual real (4,445 filas, un mes) —
esto es su tabla.

### `Motivo`, no `Tipo`, es la señal real — misma trampa, otro archivo

El export trae 46 columnas; `Tipo` (`PUR-STK`/`STK-UNK`/`STK-ASM`) parece
la clasificación, pero es más grueso que `Motivo` y no agrega nada que
`Motivo` no diga ya — **no se traduce**, mismo principio que `Ubicacion`
repetida que `CONOCIMIENTO.md` §11.15 ya documentó.

```
MOVIMIENTO_ALMACEN
  id
  presupuesto_id     FK PRESUPUESTO — se resuelve de la COMBINACIÓN
                      `(Ubicacion, Lote)` al importar, nunca de `Lote`
                      solo ni de `Ubicacion` sola — ninguna de las dos es
                      única por sí misma, ni de `# Lote` (siempre `S/L`,
                      es otro campo). **Corrige D-249/D-337**: con cinco
                      meses y todas las obras, 26 de 31 números de `Lote`
                      se repiten bajo más de una `Ubicacion` (`Lote`=16
                      aparece en seis calles distintas) — un número de
                      lote tampoco es único por sí solo, la misma trampa
                      que ya se sabía de `Ubicacion` pero en la otra
                      dirección. Con un mes y una sola obra de referencia
                      no se veía; con el portafolio completo, el 51% de
                      las filas con `Lote` real caen bajo la calle
                      minoritaria de su número. Es la única forma de
                      filtrar por obra en los motivos que no tienen
                      `nodo_id`                                              firme — corregido
  clave              texto — el insumo (`# Parte`)                          firme — nuevo
  cantidad           NUMERIC con signo — `Efecto Qty`: + entrada, - salida   firme — nuevo
  costo_total        NUMERIC con signo — `Efecto Costo`, el impacto en
                      dinero de este movimiento                             firme — nuevo
  fecha              TIMESTAMP                                              firme — nuevo
  motivo             enum: recepcion · salida_produccion · implosion ·
                      ajuste_salida · sobrante · faltante ·
                      inventario_inicial · consumo_interno ·
                      reversion_movimiento_erroneo · devolucion_cliente —
                      abierto, crece con evidencia (D-357: cinco meses
                      reales trajeron dos motivos que abril no traía)     abierto — corregido
  nivel              texto — la etapa (Cimentación, Planta Baja…), misma
                      llave que «nivel de construcción» (`LENGUAJE.md`);
                      null en `recepcion` — no aplica a algo que aún no
                      sale a obra. Trae también la variante «Control de
                      Cambio X» — la misma señal cruda que
                      `CONOCIMIENTO.md` §11.18 ya trata como
                      `CC-ALM-18XXX`, no un caso nuevo                       firme — nuevo
  nodo_id            FK Nodo, nullable — el concepto/etapa que se explotó
                      (`No.Parte`). Solo poblado cuando `motivo=implosion`
                      — es la única vía con esta liga; `salida_produccion`
                      no la tiene nunca en el archivo real, sale a un
                      `nivel`, no a un concepto                             firme — nuevo
  op                 texto, nullable — folio de orden de producción, solo
                      en `motivo=implosion`. Se lee de `Referencia` (texto
                      libre: `OP:23622, No.Parte:BAP-03010…`), no hay
                      columna propia — mismo parseo validado ya (67 de 67
                      contra `# OP`) por `CONOCIMIENTO.md` §11.15          firme — nuevo
  proveedor          texto, nullable — solo poblado en `motivo=recepcion`
                      (1,764 de 1,767 filas reales)                         firme — nuevo
  referencia         texto libre, nullable                                  firme — nuevo
  ticket_garantia_id FK TICKET_GARANTIA, nullable — cierra P-41 (§3b),
                      solo poblado cuando el despacho es para una
                      reparación de garantía, no obra nueva                 nuevo
```

**`bodega` no se modela como campo propio todavía** — 4,440 de 4,445 filas
reales son el mismo almacén; sin un segundo almacén real en uso, es una
dimensión sin variación que observar.

### `motivo` no era cerrado — cinco meses trajeron dos valores que uno no traía

Corrige la marca «firme» que llevaba desde D-333: sobre 23,075 filas
reales (cinco meses, todas las obras, no solo Lote 18) aparecen
`reversion_movimiento_erroneo` y `devolucion_cliente`, ninguno visto en
abril solo. Mismo criterio que ya llevó a declarar `CLASE_TRABAJO` tabla
abierta en vez de enum cerrado (§2): **una lista de motivos reales no se
cierra con un mes de evidencia.**

Los dos son casos únicos (1 fila cada uno, julio) y piden lectura
cuidadosa, no una fila más sin más:

- **`reversion_movimiento_erroneo`**: `Lote`=4 (no 18), `Referencia`
  dice «REVERSION DE LOTE ALAMO 4» — deshace una salida capturada por
  error. Caso limpio: confirma que el ERP real sí corrige movimientos
  equivocados, con su propio motivo, no editando la fila original.
- **`devolucion_cliente`**: **no es el espécimen de devolución que P-19
  dejó pendiente.** `Lote` viene vacío y `Referencia` dice «INGRESO
  AJUSTE DE INVENTARIO» — el nombre del motivo no calza con su propio
  texto libre. Más parece un ajuste de inventario capturado bajo el
  motivo equivocado que una devolución real de material sobrante desde
  una obra. **La pregunta de P-19 sigue sin espécimen limpio** — esto no
  la cierra, solo agrega un candidato débil que conviene no confundir
  con la respuesta.

### Surtido contra consumido no es un campo — ya lo separa `motivo`

B-16 pedía distinguir **surtido** de **consumido**. En el archivo real son
dos motivos distintos, no una lectura que haya que calcular:

| | `salida_produccion` | `implosion` |
|---|---|---|
| Qué es | Sale del almacén hacia una etapa (`nivel`) | El sistema la explota y la liga a un concepto (`nodo_id`) vía `op` |
| Se liga a concepto | **Nunca** (0 de 1,674 filas reales) | **Siempre** (950 de 950) |
| Es el «surtido» de B-16 | Sí | — |
| Es el «consumido» de B-16 | — | Sí |

**No hace falta un booleano `es_consumido`** — `motivo IN (...)` ya lo
dice, mismo criterio que evitó un campo nuevo en P-7 (`CONOCIMIENTO.md`
§5c).

### El corte matricial es vista, no tabla — y solo alcanza donde hay `nodo_id`

`CONOCIMIENTO.md` §13.6 ya lo describe: insumo × concepto, con lo teórico
(`COMPOSICION.cantidad`, vía `nodo_id`), lo surtido/consumido
(`MOVIMIENTO_ALMACEN` agrupado por `clave`+`nodo_id`) y la diferencia.
**Se calcula al cruzar, no se guarda** — mismo principio que el
rendimiento real del programa (P-7) y que
`ESTADO_CARGA.porcentaje_cargado`: nunca un campo paralelo que se
desincronice.

**El cruce por concepto solo corre sobre `motivo=implosion`** — es el
único motivo con `nodo_id`, el mismo que ya usaron para esto
`CONOCIMIENTO.md` §11.16 y `CONOCIMIENTO.md` §11.17. `salida_produccion`
no tiene concepto, solo `nivel`:
compara contra el presupuesto por etapa, no insumo por insumo — más
grueso, no el mismo cruce.

### Las devoluciones no tienen espécimen real todavía

B-16 las esperaba. El archivo real de abril no las trae como motivo
propio — lo más parecido son `sobrante`/`faltante` (20 filas), que son
**otra cosa**: corrección de conteo físico de inventario, sin
`referencia` ni `op`, no material que vuelve de obra sin usar. Si esa
devolución existe, hoy no deja rastro distinto de una `salida_produccion`
que nunca se registró — **queda abierto, sin forzar `sobrante`/`faltante`
a significar algo que el dato no confirma.**

### Dos formas consideradas y descartadas

- **`ORDEN_PRODUCCION` como tabla propia** — el `op` agrupa varias líneas
  (ej. `IEC-00410` con 4 líneas bajo el mismo folio), pero no tiene ciclo
  de vida propio ni estado que aprobar: es una llave de agrupación, no una
  entidad. Se queda como campo en `MOVIMIENTO_ALMACEN`, no como tabla.
- **Un catálogo `NIVEL`/`ETAPA` formal** — `nivel` ya es la misma «llave al
  catálogo de niveles» que `LENGUAJE.md` nombra para `Nivel ERP`, y ese
  catálogo tampoco tiene tabla propia todavía en este modelo. Es un hueco
  más chico que éste, compartido con Programa — se anota, no se resuelve
  aquí.

### `PRECIO_HISTORICO` cobra las dos fuentes que quedaron pendientes

`MODELO.md` §4a dejó anotado que «almacén y estimación quedan pendientes
de P-19 y P-18 — se agregan al enum cuando esos módulos existan, no
antes.» P-18 ya cerró (D-300) sin que nadie volviera a esa línea — se
corrige aquí, junto con almacén:

```
PRECIO_HISTORICO.fuente   enum: catalogo · ingenieria · almacen ·
                           estimacion
```

`almacen` lee `costo_total`/`cantidad` de cada `MOVIMIENTO_ALMACEN` con
`motivo=recepcion` — el precio real de compra, con proveedor. `estimacion`
lee `monto`/`cantidad_avance` de cada `ESTIMACION_LINEA` (§5d) al
conciliar — mismo principio que la excepción de trabajo y subcontrato que
`MODELO.md` §4a ya declaraba (su precio nace de negociación puntual, no de
mercado).

---

## 5f. Comparación y reportes de obra — cinco columnas, cuatro ya tenían dónde vivir (B-71 cierra)

`RAZONAMIENTO.md` §4 y `CONOCIMIENTO.md` §11.14 a `CONOCIMIENTO.md` §11.18
ya probaron el método sobre datos reales de `ALAMO 18` — Presupuesto Base,
Ingeniería, Pagado Real, Presupuesto Formado y Control de Cambio, por
destajo y por material. Lo que faltaba no era el método: era ver que
cuatro de las cinco columnas ya tenían tabla, y la quinta ya tenía
`enum`.

### De dónde sale cada columna — ninguna se guarda aparte

| Columna | Fuente | Nueva? |
|---|---|---|
| Presupuesto Base | `PRESUPUESTO(tipo=plantilla)` — su árbol, su matriz | No — cierra con P-40, §3 |
| Ingeniería (del lote) | `PRESUPUESTO(tipo=obra)` — su propio árbol, su cantidad y matriz reales tal como quedaron tras el rediseño | No — §1, §1a |
| Pagado Real | `ESTIMACION_LINEA` (§5d) para destajo/MO · `MOVIMIENTO_ALMACEN` con `motivo` ∈ {`salida_produccion`, `implosion`} (§5e) para material — **no** `recepcion`: esa entra a almacén general, sin `presupuesto_id` (`Lote` vacío en las 1,767 filas reales), no se le puede atribuir a una obra | No — cerraron hoy mismo, corregido en auditoría (D-337) |
| Presupuesto Formado | Cálculo, no tabla — ver abajo | No |
| Control de Cambio | `PROPUESTA(tipo=orden_cambio)` — ya existía en el enum, sin forma escrita para `valor_propuesto` | Solo la forma, no la tabla |

**Ninguna columna se persiste.** Mismo principio que `RAZONAMIENTO.md` §4:
«el cerebro nunca guarda un valor vigente» — este módulo es la consulta que
hoy corre a mano en un script fuera del repositorio, no un lugar nuevo
donde guardar el número.

> **`PRESUPUESTO(tipo=escenario)` (§3a) queda fuera de este reporte por
> diseño** — Ingeniería lee solo `tipo=obra`, nunca sus escenarios
> candidatos. Un escenario se compara contra su obra o contra otro
> escenario con la misma mecánica (Base/Formado/Efecto), pero eso es
> otra consulta, no una sexta columna aquí.

### El andamio no es material directo — primer caso real de la capa de indirectos (dato del usuario)

`NODO.categoria` ya separaba `herramienta`/`equipo` de `material` (§1);
lo que faltaba era que **`Pagado Real` (tabla de arriba) también los
separara.** Confirmado con los cinco meses reales: el andamio
(`HET-00034`, única clave, `Clase=Herramienta` en el catálogo de origen)
se despacha con el mismo `motivo=salida_produccion` que el material que sí
se consume, cargando el 100% de su costo de reposición ($1,661.54/pieza)
contra la obra que lo recibió — y su regreso casi nunca se registra (2 de
18 movimientos, ninguno ligado a la obra que lo devuelve). Cinco meses,
todas las obras: -$73,107.73; solo `ALAMO 18`: -$13,292.31. Cero
renglones de "andamio" en todo `CATALOGO_DE_PRESUPUESTO.csv` — no hay
partida que estuviera esperando ese costo.

**No es costo directo de material de una obra — es costo indirecto que se
reparte.** `Pagado Real` de material (fila de arriba) excluye los
movimientos cuyo insumo es `HET-00034`; ese costo pasa a la capa de
indirectos que ya estaba diseñada (`COMPOSICION.reportar_a` +
`base_porcentaje=acumulado_hasta_aqui`, `CONOCIMIENTO.md` §5) pero que
hasta hoy no tenía **ningún** dato real que la ejerciera — el andamio es
el primer caso real de esa capa. La regla se queda acotada a esta clave
por ahora, a propósito: generalizarla a toda `categoria=herramienta`/
`equipo` —lo que también le daría cierre a la cimbra, D-356— queda
pospuesto, dato del usuario; un caso a la vez, no una regla general
todavía sin más evidencia.

### Presupuesto Formado es el cruce de dos instancias, no una tercera

`CONOCIMIENTO.md` §11.14 ya lo define: el catálogo reconstruido, **a su
cantidad real, explotado con el mismo rendimiento que usa el presupuesto
base.** Cantidad real ya vive en `PRESUPUESTO(tipo=obra)`
(`NODO.cantidad`, con `modo_cantidad` diciendo cómo se obtuvo); el
rendimiento base ya vive en `PRESUPUESTO(tipo=plantilla)`
(`COMPOSICION`+`VERSION_CONCEPTO`). Formado es el cruce de las dos — la
cantidad de una instancia, la matriz de la otra —, nunca una tercera copia
que se pueda desincronizar:

```
Efecto cantidad = Presupuesto Formado − Presupuesto Base   (construir más o menos, misma receta)
Efecto receta    = Ingeniería − Presupuesto Formado          (usar distinto rendimiento, misma cantidad)
```

Identidad ya probada en los siete prototipos y en `ALAMO 18`
(`CONOCIMIENTO.md` §11.14): las dos suman exacto el excedente total, fila
por fila.

### Control de Cambio ya tenía bandeja — le faltaba la forma de su JSON

`PROPUESTA.tipo` ya incluye `orden_cambio` (§5) desde el primer diseño;
`autorizar_orden_cambio` ya es función atómica (P-21, hoy sin rol
asignado). Lo único que el glosario marcaba «— pendiente» era la forma de
`valor_propuesto` para ese `tipo` — `CONOCIMIENTO.md` §13.4 y el espécimen
real `CC-ALM-18XXX` de `CONOCIMIENTO.md` §11.18 ya la dan:

```
valor_propuesto (JSON, tipo=orden_cambio)
  clave                texto — patrón CC-{cluster}-{lote}{consecutivo},
                        ej. CC-ALM-18001
  delta_monto          NUMERIC con signo — impacto en costo
  delta_plazo_dias     INTEGER, nullable — impacto en plazo
  causa                enum: cambio_proyecto · error · condicion_sitio
  ejecutado_en         TIMESTAMP, nullable — si ya se ejecutó en obra
                        antes de esta propuesta
```

**`objeto_id` (el campo que ya existe en `PROPUESTA`) es el nodo
congelado que referencia** — y también resuelve, sin campo nuevo, el caso
«sin identificar» de `CONOCIMIENTO.md` §11.18 (el archivo no trae
`NIV-`/`ECO-`): se liga a la raíz del árbol de `PRESUPUESTO(tipo=obra)`,
no a un concepto — cuenta en el consolidado de la obra, como pide el
método, sin inventar un nodo que el dato no dio.

**Retroactividad no es un campo — es comparar dos fechas que ya
existen.** `PROPUESTA.resuelto_en` (cuándo se autorizó) contra
`ejecutado_en` (arriba, cuándo se ejecutó): si `ejecutado_en` es
anterior, fue retroactiva. El **porcentaje de órdenes retroactivas** que
`CONOCIMIENTO.md` §13.4 pide como medida de salud del proceso es una
consulta sobre `PROPUESTA(tipo=orden_cambio)`, no una columna aparte.

### Por destajo y por material — un solo eje, tres formas de aplicarlo

Las cinco columnas no necesitan un filtro nuevo: `categoria` (canon,
`LENGUAJE.md`) ya distingue `material` de `mano de obra`/`trabajo`, y ya
es el eje que usó todo `CONOCIMIENTO.md` §11.14 para separar destajo de
material. Cómo se aplica cambia según la columna, no el eje:

| Columna | Cómo se filtra |
|---|---|
| Base · Ingeniería · Formado | `categoria` de cada hoja de la explosión (insumo), no de su contenedor — mismo principio que `CONOCIMIENTO.md` §11.14 ya fijó para la explosión recursiva |
| Pagado Real | Ya viene separado por tabla de origen: `ESTIMACION_LINEA` es destajo, `MOVIMIENTO_ALMACEN` es material |
| Control de Cambio | `categoria` del nodo que referencia `objeto_id` |

### Los subcontratos no entran en esta comparación — tienen la suya, y le falta dato

`CONOCIMIENTO.md` §11.14 ya lo estableció (D-307): un subcontrato no se
explota contra su propia matriz de material, así que no cruza por este
eje. Se compara Real contra su propia Base (D-313, validado en los tres
casos de `ALAMO 18`, D-321) — un tercer eje, ya probado, que no necesita
tabla nueva: lee `PROPUESTA`/`ESTIMACION_LINEA` del subcontrato contra la
misma partida en `PRESUPUESTO(tipo=plantilla)`. **Lo que falta no es
diseño, es dato**: el archivo `subcontratos.csv` del resumen de obra
llegó vacío (D-321) — sin origen de subcontratos reales, este eje no
tiene qué leer todavía.

### Lo que esto NO resuelve

**Desviación y Ejecutado sin respaldo** (`GLOSARIO-DOMINIO.md`, «Precios y
cambios» — los dos seguían «— pendiente») no cierran aquí. Este reporte
ya da los números que las definen (Ingeniería contra Base es la
desviación; lo pagado sin orden de cambio que lo respalde es lo
ejecutado sin respaldo), pero **capturar y persistir la causa**
(`CONOCIMIENTO.md` §13.6 — vocabulario controlado, quién la captura, que
«sin causa» sea un estado válido) es su propio diseño, todavía sin
hacer. `capturar_causa_desviacion`/`revisar_patrones_desviacion` ya
existen como función atómica (P-21) sin tabla a la que escribir.

### Recursos por fecha — la salida del CPM (B-41 cierra)

`PROPUESTA-CUATRO-MODULOS.md` §4 ya daba la fórmula: la misma explosión
de siempre, leída a lo largo del tiempo, no un módulo nuevo.

```
actividad  →  tramos con fecha       (ACTIVIDAD/TRAMO, §5c)
actividad  →  conceptos              (ACTIVIDAD.concepto_id)
concepto   →  explosión de insumos   (COMPOSICION, §1)
─────────────────────────────────────────────────────────
           →  material · mano de obra · subcontratos, por fecha
```

| Proyección | Cómo se filtra/fecha | Nueva? |
|---|---|---|
| Material por fecha | `categoria=material` (mismo eje que §5f arriba), fecha de `TRAMO`/`ACTIVIDAD` **menos** `CONSTANTE_FISICA(categoria=tiempo_entrega)` — pedido, no consumo | No |
| Mano de obra por fecha | `categoria` ∈ {mano de obra, trabajo}, fecha de `TRAMO`/`ACTIVIDAD` sin corrimiento — no hay tiempo de entrega para contratar gente | No |
| Subcontratos por fecha | Igual, filtrado a `clase=subcontrato` — **cuándo contratar, no solo cuándo empieza**, sigue sin un tiempo de entrega propio (no es el de material) | Sin resolver — ver abajo |
| Egreso por fecha | Las tres anteriores, valuadas con `PRECIO_HISTORICO`/`TABULADOR_CONTRATISTA` y sumadas por periodo — es el flujo de efectivo | No |

`TRAMO.reparto_material` (§5c, P-5) ya reparte el material por tramo, no
parejo entre inicio y fin de la actividad — el hueco que deja una
actividad interrumpida (el muro que para para colar la cadena) ya no
lo esconde una proyección por fecha.

**Dos huecos reales, los dos de dato, no de diseño:**

- **Cuándo contratar un subcontrato** necesita su propio tiempo de
  entrega (negociación, no logística de material) — no existe, y crearlo
  sin evidencia sería inventar. Sigue como P-39 lo dejó anotado: falta
  catálogo de contratistas.
- **Cuándo se paga**, no solo cuándo se consume, movería el flujo de
  efectivo más cerca de lo real — necesita términos de pago por
  proveedor/contratista, y **no hay catálogo de proveedores** (mismo
  hueco que P-39/D-175). El egreso por fecha de arriba es por fecha de
  consumo, no de pago.

> **La fórmula de fecha de pedido tiene una ambigüedad sin resolver**
> (`CONOCIMIENTO.md` §15, `RAZONAMIENTO.md` §3): «inicio» puede ser la
> fecha temprana o la tardía de la actividad. No se elige aquí en
> silencio — queda para cuando haya un caso real que la fuerce a
> decidirse.

---

## 5g. Desviación — la comprobación más fuerte, con causa opcional y patrones que se leen sin ella

Tercera vez que el hueco aparece (auditoría de `MODELO.md` §5f, D-334;
mecanismo de sustitución, D-342) es la señal de que ya toca. La política
lleva meses cerrada sin tabla — `CONOCIMIENTO.md` §13.6 la describe con
la fórmula de dos factores, las causas por categoría y las cuatro reglas
de captura; esta pasada solo le pone forma.

```
DESVIACION
  id
  nodo_id              FK Nodo — el concepto o insumo donde se detecta   firme — nuevo
  presupuesto_id       FK PRESUPUESTO — la obra. No basta con `nodo_id`
                       para agrupar por obra en un cruce entre obras,
                       mismo motivo que llevó a `presupuesto_id` en
                       `MOVIMIENTO_ALMACEN` (D-337)                      firme — nuevo
  tipo                 enum: precio · consumo — los dos factores de la
                       fórmula de `CONOCIMIENTO.md` §13.6, nunca sumados
                       en una sola fila                                  firme — nuevo
  monto                NUMERIC — el efecto en dinero de este factor,
                       solamente                                         firme — nuevo
  cantidad_plan,
  cantidad_real        NUMERIC, nullable — solo si tipo=consumo           firme — nuevo
  precio_plan,
  precio_real          NUMERIC, nullable — solo si tipo=precio            firme — nuevo
  causa                enum, nullable — «Causas por categoría» de
                       `CONOCIMIENTO.md` §13.6, según el tipo del
                       nodo_id y el `tipo` de esta fila: material·precio
                       (mercado · volumen · proveedor_distinto ·
                       cambio_de_presentacion) · material·consumo
                       (desperdicio_mayor_al_teorico ·
                       merma_por_dano_clima_o_robo ·
                       sustitucion_por_equivalente, D-342) ·
                       mano_de_obra·precio (renegociacion · urgencia ·
                       alza_de_tabulador) · mano_de_obra·consumo
                       (rendimiento_real_distinto · retrabajo ·
                       trabajo_fuera_de_alcance) · herramienta·precio
                       (tarifa_distinta) · herramienta·consumo
                       (dias_reales_de_renta · equipo_parado) ·
                       maquinaria·precio (tarifa · combustible) ·
                       maquinaria·consumo
                       (horas_efectivas_contra_facturadas) ·
                       contratos·consumo (volumen_realmente_ejecutado) —
                       null es «sin causa», estado válido, no dato
                       faltante                                          corregido — D-347
  causa_capturada_por  FK USUARIO, nullable                               firme — nuevo
  causa_capturada_en   TIMESTAMP, nullable — puede llegar después de
                       `detectada_en`, sin penalización                  firme — nuevo
  detectada_en         TIMESTAMP — la detección no espera a la causa,
                       `CONOCIMIENTO.md` §13.6: «existe se declare o
                       no»                                               firme — nuevo
```

**`cantidad_plan`/`precio_plan` se congelan al detectar, no se leen en vivo
cada vez.** Si se recalcularan contra la versión vigente de la matriz,
una `DESVIACION` de hace tres meses cambiaría de valor cuando el catálogo
avance — mismo error que ya evitó `VERSION_CONCEPTO.pu` (§4a: «se congela,
nunca se recalcula»). Es un registro histórico, no una vista.

### Las nueve causas de `CONOCIMIENTO.md` §13.6 no son el vocabulario de `causa`

Corrige D-343: la primera versión de `causa` tomaba «las nueve causas, y
quién paga cada una» (`CONOCIMIENTO.md` §13.6) como si fueran su
vocabulario. Pero esa tabla resuelve algo anterior a `causa` —**si el
hecho es una `DESVIACION` siquiera**— y su propia columna «a dónde va» lo
dice sin ambigüedad: de las nueve, solo 1 (error de ejecución) y 2
(necesario para ejecutar) terminan ahí. La 3 y la 4 (omisión de
presupuesto, omisión de proyecto) van a **ejecutado sin respaldo** —
`GLOSARIO-DOMINIO.md` ya marca ese término «no confundir con Desviación»,
y sigue sin tabla propia. La 5, la 6 y la 9 (petición del cliente,
contrato cambiado sin propagar, mejora de proyecto) van a
`PROPUESTA(tipo=orden_cambio)` o a `INCIDENCIA`. La 7 (falta de insumos)
es un hueco de programa, no de costo. El propio `CONOCIMIENTO.md` §13.6
lo dice explícito para estos casos: **«no son el mismo renglón».** Cuando
una incidencia o una orden de cambio generan además una desviación real,
esa desviación es su propia fila, con su propia causa de categoría —
nunca copia el motivo que la disparó.

### Las cuatro reglas de captura ya estaban escritas — el schema solo las deja cumplirse

`CONOCIMIENTO.md` §13.6 las fija en prosa; aquí es donde se ven en columna:

| Regla | Cómo la cumple el schema |
|---|---|
| La detección no depende de nadie | `detectada_en` se llena solo, `causa` puede quedar `null` indefinidamente |
| Quien corrige el catálogo mira patrones, no causas | Los patrones (`nodo_id` que se desvía en toda obra, `presupuesto_id` que se desvía en todo concepto) son consulta agregada sobre `DESVIACION`, no un campo que alguien declare |
| «Sin causa» es un estado válido, con su propio % | `causa IS NULL` es una fila completa, nunca un placeholder a rellenar |
| La causa se agrega después, sin penalizar | `causa_capturada_en` es independiente de `detectada_en` — nunca bloquea ni vence |

### Los patrones no piden tabla — son la misma consulta de siempre

`CONOCIMIENTO.md` §13.6 ya da la lectura: un insumo que se desvía en **todos**
los conceptos es problema de compra o medida; un concepto que se desvía en
**todos** sus insumos es problema de ese trabajo; repetido en todas las
obras apunta al catálogo, repetido en una sola es condición local. Las
cuatro son `GROUP BY nodo_id` / `GROUP BY presupuesto_id` sobre
`DESVIACION` — mismo criterio que excluyó una tabla de "comparación" en
`MODELO.md` §5f: se calcula al preguntar, no se guarda aparte.
`revisar_patrones_desviacion` (P-21) ya tenía nombre de función; ahora
tiene sobre qué correr.

**Por contratista, la misma lectura se desbloqueó con `CONTRATISTA`
(§4a, D-366, cierra P-39)** — se agrupa uniendo `nodo_id` contra
`TABULADOR_CONTRATISTA.contratista_id`, sin campo nuevo aquí.

### Cuando el patrón corrige el catálogo, ya sabe a quién avisar

Una `DESVIACION` recurrente y atribuible al método (no a condición local ni
a error corregible, `CONOCIMIENTO.md` §13.6) se resuelve con lo que ya
existe: `PROPUESTA(tipo=version)`, evidencia = las filas de `DESVIACION`
que la sustentan. Es el mismo mecanismo que acaba de cerrar P-35 — una
sustitución detectada es un caso particular de este patrón general, no
uno aparte.

**`capturar_causa_desviacion` y `revisar_patrones_desviacion` (P-21) siguen
sin asignar a rol** — nada en esta pasada cambia esa decisión; ahora
tienen tabla a la que escribir y consultar, que es lo que les faltaba.

---

## 5h. Rastro de Consulta — la única bandeja fuera de `PROPUESTA` (B-33 cierra)

`PROPUESTA` es la memoria de los agentes que proponen (D-77) — Consulta no
califica: **nunca propone, solo lee** (D-75). Necesita su propia bandeja,
más chica, porque no tiene dónde más vivir.

```
CONSULTA_LOG
  id
  pregunta               texto — tal como llegó                          firme — nuevo
  herramienta_usada_id   FK a la tool del catálogo (`gravity-obra.md`
                         §6), nullable si ninguna aplicó                 firme — nuevo
  respondida             boolean — ¿hubo con qué contestar?               firme — nuevo
  herramienta_faltante   texto, nullable — qué tool hubiera hecho falta,
                         cuando se puede nombrar                         firme — nuevo
  usuario_id             FK USUARIO, nullable                             firme — nuevo
  capturada_en           TIMESTAMP                                       firme — nuevo
```

**Sin retención — dato del usuario, explícito: persistente, para que la
señal de mejora no se pierda.** Distinto de `ALERTA`/`PROPUESTA`, que sí
resuelven y cierran: aquí no hay «resuelto», el valor está en acumular
para ver qué se pregunta seguido y qué herramienta falta, no en cerrar
cada fila. `PENDIENTES-MEJORAS.md` B-33.

---

# 6. Lo que este modelo deliberadamente NO resuelve

| No incluido | Por qué |
|---|---|
| Motor de cálculo (funciones, no tablas) | Es código sobre este modelo, no schema |
| Capas de sobrecosto (indirectos/utilidad) | Sin datos reales que las usen (`CONOCIMIENTO.md` §5) |
| Constructor de matrices (B-18) | Motor de cálculo (fórmula), no schema — `CONSTANTE_FISICA` que consulta ya tiene tabla, §1c |
| Programa / CPM — solo lo que queda | Las diez decisiones de política y toda la tabla (`ACTIVIDAD`, `PRECEDENCIA`, `CALENDARIO_OBRA`, `TRAMO`, los dos cuantificadores, `FRENTE_TOPE_CUADRILLA`, `CIERRE_FRENTE`) ya cerraron en §5c. Queda: motor de cálculo del CPM (fechas tempranas/tardías, ruta crítica — código, no schema) y reglas de visualización del Gantt (pantalla, no entidad) |
| Código externo (Ingenieria ERP) | Pendiente P-17. Sin campo propuesto — ver §hallazgos |
| Moneda extranjera (`Costo base M. E.`) | Cero en los 387 materiales — sin evidencia de uso hoy. **Distinto del `OID`:** no es un descarte permanente. Se modela en cuanto haga falta convertir a moneda extranjera, no antes. M-13 |

---

# Resumen de hallazgos — para decidir

| # | Hallazgo | Cómo se resolvió aquí | ¿Aprobado? |
|---|---|---|---|
| 1 | `reporta_a` no es igual a `categoria` del hijo | Se mueve a `COMPOSICION`, no a `NODO` | ⏸️ |
| 2 | El código externo no es generable | **No se modela.** Queda fuera hasta resolver P-17 | ⏸️ |
| 3 | `subfamilia_id`, obligatoria o no | **Nullable.** Confirmado: no viene de OPUS, se deriva al 92% | ✅ |
| 4 | Dos reglas de porcentaje distintas (`%MO` vs. capas) | Campo explícito por regla, no genérico | ⏸️ |
| 5 | `Familia` es ambigua entre categorías | Unicidad compuesta `(nombre, categoria_id)` | ⏸️ |
| 6 | El estado es del nodo, no del presupuesto | Tabla aparte `ESTADO_CONGELAMIENTO` | ⏸️ |
| 7 | `Acarreo` no tenía dónde guardarse en el dato | Tabla abierta `CLASE_TRABAJO`, no `ENUM` — las clases van a crecer | ✅ |
| 8 | Falta saber cuánta ingeniería está cargada | Tabla aparte `ESTADO_CARGA`, por nodo, con caché de porcentaje | ✅ |
| 9 | `Flete` se usaba como apartado para insumos no clasificables | Campo `revisar` (boolean) en `NODO`, en vez de abusar de la categoría | ✅ |
| 10 | La alerta no tenía dónde vivir, y se perdía al cerrar la sesión que la detectaba | Tabla `ALERTA`, peldaño de abajo de `PROPUESTA`, con `veces_vista` para saber si reaparece | ✅ |
| 11 | `NODO.modo_cantidad = medida` no tenía mecanismo que lo alimentara | Tablas `TRAZO` y `ENLACE_CUANTIFICACION` — el trazo es evidencia, el enlace tipa qué mide y con qué factor | ✅ |
| 12 | `modo_cantidad` no tenía sus casos escritos, y faltaba uno (ingeniería cargada) | Ciclo de vida completo con evidencia; quinto valor `cargada`, verificable contra `medida` | ✅ |

**Los seis primeros hallazgos fueron revisados y aprobados el 2026-09-10**, con dos
ajustes sobre la propuesta original:

- Hallazgo 2 (código externo): en vez de un campo opaco, **se retira del modelo por
  completo**. No se agrega ni un campo provisional hasta resolver P-17.
- Hallazgo 3 (`subfamilia_id`): en vez de fijar nullable, **queda sin restricción
  decidida** hasta confirmar si OPUS ya trae la clasificación del concepto.

Los hallazgos 1, 4, 5 y 6 quedan tal como se propusieron.

**Los hallazgos 7 a 12 se agregaron el 2026-09-15**, resolviendo P-02, P-03, P-04,
P-25, P-29, P-30 y B-19 en una sesión de trabajo con el usuario — no en la revisión
original del 09-10. Los seis aprobados en la misma conversación que los originó.

> **Este modelo puede pasar a la siguiente fase**: tipos de columna concretos,
> índices, y el motor de cálculo como funciones sobre este schema. Eso no se hace
> aquí — es la fase de implementación del constructor.
