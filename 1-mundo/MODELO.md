# MODELO — propuesto por el arquitecto

```
órgano:     esquema corporal
capa:       I — Mundo
pregunta:   ¿qué forma tienen los datos?
tiempo:     es así
corte:      2026-09-15
verificado: Aprobado · 6 hallazgos resueltos
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
  modo_cantidad      enum: medida · estimada · capturada · heredada  firme
  categoria          enum: material · mano_de_obra · herramienta ·
                      equipo · auxiliar · flete · trabajo · concepto firme
  familia_id         FK Familia                                      firme
  subfamilia_id      FK Subfamilia (nullable)                        firme — pero P-12 abierta
  modo_precio        enum: calculado · declarado                     firme
  precio_declarado   NUMERIC, nullable                                firme — solo si modo_precio=declarado
  procedencia        enum: importado · manual · fusion · division ·
                      extraccion · composicion · clonacion            firme
  reporta_a          categoría a la que el compuesto suma su monto    firme (D-hallazgo, ver §1a)
```

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

---

# 3. Presupuesto y proyecto

```
PRESUPUESTO
  id, nombre, estado (por SUBÁRBOL, ver hallazgo 6)                    firme
  raiz_id            FK Nodo                                            firme

ESTADO_CONGELAMIENTO   (por nodo, no por presupuesto)
  nodo_id            FK Nodo
  estado             enum: diseño · contratado                         firme
  fecha              cuándo cambió                                     firme
```

### ⚠ HALLAZGO 6 — el estado no puede vivir en `PRESUPUESTO`

El conocimiento decidió explícitamente: *el estado es del nodo, no del presupuesto*
— los planos llegan por partes, cimentación se contrata mientras acabados sigue en
diseño (`CONOCIMIENTO.md` §1.4).

**Si `estado` fuera una columna de `PRESUPUESTO`**, contradice esa decisión de raíz.
Se modela como tabla aparte, por nodo, y el presupuesto no tiene estado propio —
solo se puede preguntar "¿qué % de sus nodos está contratado?".

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

# 5. La propuesta — entidad transversal

> Ver `CONOCIMIENTO.md` §14. Nace para que "propone, no aplica" no tenga 9 bandejas
> distintas.

```
PROPUESTA
  id
  tipo             enum: equivalencia · version · reparto · conversion ·
                    matriz_generada · fusion · clonacion · orden_cambio
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
son 8 tablas para una entidad que hoy no tiene volumen. **Queda anotado como deuda
técnica**, no como error.

---

# 6. Lo que este modelo deliberadamente NO resuelve

| No incluido | Por qué |
|---|---|
| Motor de cálculo (funciones, no tablas) | Es código sobre este modelo, no schema |
| Capas de sobrecosto (indirectos/utilidad) | Sin datos reales que las usen (`CONOCIMIENTO.md` §5) |
| Paramétrico / Ensamble | Diseño en `CONOCIMIENTO.md` §5 del conocimiento, sin tabla propuesta aún |
| Programa / CPM | Depende de la propuesta de 4 módulos, sin aprobar |
| Estimaciones, contratos, almacén | P-18, P-19 — sin definir |
| Roles y permisos | P-21 — sin definir |
| Código externo (Ingenieria ERP) | Pendiente P-17. Sin campo propuesto — ver §hallazgos |
| Moneda extranjera (`Costo base M. E.`) | Cero en los 387 materiales — sin evidencia de uso. Mismo criterio que el `OID` de OPUS: no se carga un campo muerto «por si acaso». M-13 |

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

**Los seis hallazgos fueron revisados y aprobados el 2026-09-10**, con dos ajustes
sobre la propuesta original:

- Hallazgo 2 (código externo): en vez de un campo opaco, **se retira del modelo por
  completo**. No se agrega ni un campo provisional hasta resolver P-17.
- Hallazgo 3 (`subfamilia_id`): en vez de fijar nullable, **queda sin restricción
  decidida** hasta confirmar si OPUS ya trae la clasificación del concepto.

Los hallazgos 1, 4, 5 y 6 quedan tal como se propusieron.

> **Este modelo puede pasar a la siguiente fase**: tipos de columna concretos,
> índices, y el motor de cálculo como funciones sobre este schema. Eso no se hace
> aquí — es la fase de implementación del constructor.
