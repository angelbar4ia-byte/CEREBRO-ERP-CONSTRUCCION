# Pendientes a mejorar o cambiar

```
órgano:     cola de impulsos
capa:       IV — Dirección
pregunta:   ¿qué falta?
tiempo:     vamos aquí
corte:      2026-09-15
verificado: 38 de decisión · 14 de datos · 25 módulos
```

> Backlog vivo. **Auditado el 2026-09-09** contra los catálogos vigentes.
> El objetivo no es replicar OPUS, sino **corregir de raíz** lo que hoy está mal.

**Estados**

| Estado | Significado |
|---|---|
| ✅ | Resuelto · reglas definidas |
| 🔧 | Accionable: la decisión es clara, falta hacerlo |
| 🔶 | Parcial: definido a medias |
| ⏸️ | Requiere decisión o información |
| ⛔ | Obsoleto: el catálogo se sustituyó |

**Secciones**

| | Qué contiene |
|---|---|
| A · B · C | Datos y decisiones |
| D | Los catálogos de la generación anterior |
| E | Orden sugerido |
| **F** | **Por construir** — los módulos del sistema |

---

## Catálogos: cuáles son los vigentes

| Vigente | Sustituye a |
|---|---|
| `CATALOGO_DE_MATERIALES` (387) | `Catalogo_de_Matriales` (325), `Catalogo_de_auxiliares` |
| `CATALOGO_DE_TRABAJOS` (265) | `catalogo_de_SUBCONTRATOS` |
| `CATALOGO_DE_MANO_DE_OBRA` (97) | `Catalogo_de_cuadrillas`, la mano de obra `MOOP` |
| `CATALOGO_DE_FLETES` (9) | — nuevo |
| `CATALOGO_DE_PRESUPUESTO` (3,231) | — |
| `ANALISIS_DE_BASICOS_COMPUESTOS` (267) | — |
| `ANALISIS_DE_BASICOS_CONCEPTOS` (2,568) | — |

**Sin actualizar desde el inicio:** `CATALOGO_DE_CONCEPTOS` (470),
`CATALOGO_DE_FAMILIAS` (35), `CATALOGO_DE_NIVELES` (15),
`CATALOGO_DE_ETAPAS_DE_CONSTRUCCIÓN` (50), `CATALOGO_DE_CONTRATISTAS` (29),
`Catalogo_de_unidades` (16).

---

## A. Resuelto

| # | Era | Cómo se resolvió |
|---|---|---|
| ✅ M-04 | Unidades a mano en materiales, trabajos, mano de obra y fletes | Normalizadas. `JOR` agregada al catálogo |
| ✅ M-05 | Unidades mezcladas en auxiliares | El catálogo se fusionó a materiales |
| ✅ M-09 | La familia se deducía del prefijo | Los catálogos vigentes traen `Tipo`, `Familia` y `Subfamilia` explícitos |
| ✅ M-11 | Jerarquía sin llave foránea | **`Nivel ERP`** mapea 1 a 1 contra el catálogo de niveles |
| ✅ M-19 | Prefijos fuera del catálogo de familias | La familia es campo, el prefijo es nomenclatura |

---

## B. Accionable — 🔧

| # | Problema | Evidencia | Corrección |
|---|---|---|---|
| ✅ M-04b | ~~Unidades sin normalizar en conceptos y materiales~~ | 470 en conceptos + 103 en materiales | **Resuelto.** La normalización de unidades está completa |
| ✅ M-01 | ~~Acentos parten términos en dos~~ | 381 descripciones corregidas | **Resuelto** |
| ✅ M-02 | ~~Erratas fijas~~ | `nescesario` ×32, `cosina` ×2 | **Resuelto** |
| M-14 | El alcance vive dentro de la descripción | 395 de 461 con *«Incluye:»*, en 36 variantes | Catálogo de textos de alcance |
| ✅ M-15 | ~~Duplicados exactos de concepto~~ | 22 casos: `ISN-02001`≡`ISN-02005`, `CAN-01001`≡`CAN-01011` | **Resuelto: `EQUIVALENCIA` ya cubre esto**, `tipo=duplicado_exacto`, aprobada en `MODELO.md` §4 desde el 10 de septiembre. Sin fusionar claves. D-194 |
| ✅ M-16 | ~~Mismo concepto en dos familias~~ | `CAR-01030` ≡ `ICA-01030`, texto idéntico | **Resuelto, igual que M-15.** D-194 |
| ✅ M-13 | ~~Moneda extranjera declarada y muerta~~ | `Costo base M. E.` en cero en los 387 | **Resuelto: no se modela hoy.** Se retoma el día que haga falta convertir a moneda extranjera. `MODELO.md` §6, D-186 |
| M-17 | Precio inconsistente entre presentaciones | `ELE-00044` en PZ a $580 y `ELE-00046`, misma descripción, en M a $29 | Verificar cuál es el correcto |
| M-18 | Mismo material en dos familias y presentaciones | Pija lámina: `COM-00200` en CJ a $8.96, `ELE-00048` en PZ a $0.50 | Igual |

---

## C. Requiere decisión — ⏸️

| # | Tema | Por qué está detenido |
|---|---|---|
| ✅ P-01 | ~~El concepto no tiene clasificación~~ | **Confirmado con OPUS: no se importa, se deriva.** 92% desde el trabajo que usa; 8% requiere clasificación manual, como se hizo con trabajos |
| ✅ P-02 | ~~La clase `Acarreo` no tiene renglones~~ | **Resuelto: no falta, está bien.** El transporte que sería `Acarreo` se registra como `Flete` — la clase queda vacía porque el catálogo de Fletes ya lo cubre. D-187 |
| ✅ P-03 | ~~Frontera `Flete` contra `Acarreo`~~ | **Resuelto: el límite de la obra, no la dirección.** `Flete` la cruza —en cualquier sentido—; `Acarreo` se queda dentro. `CONOCIMIENTO.md` §10.2, D-187 |
| ✅ P-04 | ~~`Flete` se usa como apartado~~ | **Resuelto.** Campo `revisar` (boolean) en `NODO` — `MODELO.md` §1, hallazgo 9, D-189 |
| ✅ P-05 | ~~`%MO`: unidad o campo~~ | **Resuelto.** Se queda como unidad (`MEMORIA.md` §2). Forma canónica: `%MO` — mayúsculas, sin paréntesis; las otras dos se normalizan al cargar, igual que la unidad del presupuesto (D-146). D-184 |
| ✅ P-06 | ~~Precisión de cantidades~~ | **Resuelto: no hace falta definir por unidad.** `cantidad` es `NUMERIC` sin precisión ni escala fijas — se guarda lo que llegó, igual que ya pedía erp-construccion.md §9 para el arrastre de Excel. D-185 |
| P-07 | Histórico de precios | Un solo precio vigente. Sin versionado no hay presupuestos comparables entre periodos |
| P-08 | Antigüedad dispar de precios | Materiales de julio 2026; mano de obra desde enero 2023 |
| P-09 | 4 conceptos sin costear | `IGAS-02131`, `IGAS-02132`, `ISN-02061`, `ACC-00003` |
| P-10 | Agrupadores sin costear | `ACA-00021 Cubiertas cocina` y `NIV-00015 Consumibles`, en cero en los 7 prototipos |
| 🔧 P-11 | **Corregir el prefijo `AUX-`** | **Diseño completo en `IDEAS.md` §6**: clonar y sustituir, con el viaje de vuelta resuelto por homologación (`CONOCIMIENTO.md` §16.2). No queda decisión — falta ejecutarlo sobre las 79 claves reales |
| ✅ P-12 | ~~¿La subfamilia es obligatoria?~~ | **No.** `subfamilia_id` es nullable — resuelto en `MODELO.md` §1 y en B-51/D-149. Este renglón quedó sin sincronizar cuando eso se cerró; D-183 |
| ✅ P-13 | ~~**Identidad compartida**~~ | **El mecanismo y el único caso conocido ya están decididos:** D-41 (contar referencias vivas) y `LENGUAJE.md`, «El ERP externo → B · correspondencia». Lo que falta no es la forma: es llenar el resto de su ficha de mapeo |
| P-14 | **Columnas de Cabeceras, Materiales y Operaciones** | Los tres reportes que consume el ERP externo, más el formato de los cuatro catálogos que se volvieron salida |
| P-15 | ¿Hace falta un agente traductor? | El migrador trae OPUS a este sistema; no vuelve bilingüe a un tercero |
| P-16 | Declarar el dialecto del árbol de ingeniería | *No prioritario.* Sus cantidades vienen multiplicadas por el volumen y su PU congelado |
| P-17 | **`Ingenieria ERP` no es generable** | La prueba de ida y vuelta lo demostró: la regla no es deducible. O se obtiene del ERP externo, o el código se arrastra del archivo original |
| P-18 | **Estimaciones** | Cómo se emiten, qué congelan, deducciones y retenciones. Es donde el dinero se vuelve real |
| P-19 | **Almacén** | Surtido contra consumido, devoluciones, y el corte matricial |
| P-20 | **Programación** | Actividades, asignaciones y avance. Está en el skill, sin asentar en el conocimiento |
| P-21 | **Roles y permisos** | Quién captura causa, quién aprueba versión, quién autoriza cambio |
| P-22 | **Autoría de matrices y compuestos** | Cómo se arma una explosión desde cero. Ideas en `IDEAS.md` §1 y `IDEAS.md` §4 del conocimiento |
| ✅ P-23 | ~~**Ruta crítica**~~ | **Resuelto: las 4 decisiones del CPM están cerradas** (D-90, D-99 a D-102, `PROPUESTA-CUATRO-MODULOS.md`). Lo único abierto de ese módulo es P-5, ya con su propio renglón. D-195 |
| ~~P-24~~ | **16 decisiones de los cuatro módulos** | ✅ **Las 16 cerradas** (D-86 a D-113). Aparecieron tres piezas nuevas: P-5, B-40, B-45 |
| ✅ P-25 | ~~El presupuesto llega por partes~~ | **Resuelto, las tres.** Se suman; el sistema sabe si está completo comparando contra el presupuesto; y cuando falta una parte, **carga igual y avisa** — nunca bloquea (D-30) — con `ESTADO_CARGA` llevando el `%` como caché que se actualiza con cada carga (`MODELO.md` §3, hallazgo 8). D-190, D-191 |
| P-26 | **Cuatro estructuras distintas de ingeniería** | Completa, suelta, con concepto y ajena (`CONOCIMIENTO.md` §11.8). El cargador debe reconocerlas **por los datos**, no por el nombre de columna |
| P-31 | **Los archivos sueltos no dicen dónde van** | `AJU_PISOS` es una línea sin nivel ni etapa. **La estructura vive en el nombre del archivo.** ¿Se parsea el nombre, se pregunta, o se rechaza? |
| P-32 | **Las 26 claves fuera de catálogo** | 7 existían en los catálogos viejos y se perdieron al migrar; 19 son nuevas. ¿Se dan de alta, se rechazan, o se cargan como pendientes? |
| P-33 | **Dos claves con formato roto** | `HD-00411` (prefijo de 3) y `MOS-2079` (4 dígitos). ¿Se corrigen en origen o se mapean? |
| P-34 | **Anotaciones a mano en la descripción** | El «OK» que marca niveles revisados. ¿Se preserva como metadato o se descarta al normalizar? |
| P-35 | **Cómo se declararía una sustitución** | La ingeniería del lote no usa cantidades negativas en los 12 archivos vistos (`CONOCIMIENTO.md` §11.10). Sigue sin definirse el mecanismo para cuando sí haga falta |
| P-36 | **Consolidar insumos repetidos al cargar** | La arena aparece 150x mayor en ALAMO que en el prototipo porque viene suelta en cada bloque en vez de embebida en compuestos (`CONOCIMIENTO.md` §11.11). ¿El cargador debe agruparla, o se deja como está? |
| ✅ P-37 | ~~Confirmar la sustitución cemento↔mortero~~ | **Confirmado.** ALAMO 18 se cargó con la versión anterior del catálogo, donde el mortero se usaba para muros, repellos y finas exteriores |
| P-38 | **Cargar salidas de almacén de ALAMO 18** | La tercera pata: prototipo vs. ingeniería (ya funciona) + ingeniería vs. **almacén** = desviación real de obra. Objetivo en `CONOCIMIENTO.md` §11.12 del conocimiento |
| P-27 | **Cuál es el método de carga definitivo** | La carga por partes es un camino a explorar. Puede ser una mezcla de métodos o requerir confirmaciones (`CONOCIMIENTO.md` §11.4) |
| ✅ P-28 | ~~Reversar la explosión por destajo~~ | **Probado** sobre ALAMO 18: **84%** de los destajos resuelve a un solo concepto al filtrar por prototipo, y las cantidades salen **enteras exactas** (`CONOCIMIENTO.md` §11.9) |
| ✅ P-29 | ~~Auditoría prototipo contra ingeniería~~ | **Resuelto: sin causa declarada, alerta, nunca autocorrección.** Nueva tabla `ALERTA` (`MODELO.md` §5a). `CONOCIMIENTO.md` §11.7, D-192/D-193 |
| ✅ P-30 | ~~La descripción puede mentir sobre el prototipo~~ | **Resuelto: detecta y propone, nunca corrige solo.** Dos métodos —contenido y razón de cantidades, umbral 20% parametrizable— que se validan mutuamente. `CONOCIMIENTO.md` §11.7, D-193 |

## D. Los catálogos de la generación anterior

**No se corrigen a mano.** Se dividen en dos grupos con destinos distintos.

### D.1 Se volvieron salida — 🔧

`Catalogo_de_Matriales` · `Catalogo_de_auxiliares` · `Catalogo_de_cuadrillas` ·
`catalogo_de_SUBCONTRATOS`

> Los otros ERP **siguen necesitando estos catálogos**, pero ahora se alimentan desde
> OPUS y desde el conocimiento. **Dejan de ser entrada: son salida generada.**

Corregirlos a mano no sirve — se corrige el generador, no el archivo. **Lo que sí
vale es su estructura**: sus columnas son el contrato de salida.

| Qué hacer |
|---|
| Documentar sus columnas como **formato de exportación**, junto con Cabeceras, Materiales y Operaciones (P-14) |

### D.2 Se derivaron — ✅

`Catalogo_de_unidades` · `CATALOGO_DE_NIVELES` ·
`CATALOGO_DE_ETAPAS_DE_CONSTRUCCIÓN` · `CATALOGO_DE_FAMILIAS`

**Ya estaban dentro de los datos de OPUS 2025.** Generados en
`vocabularios/VOCABULARIOS-derivados.xlsx` — ver `CATALOGOS.md` §9 del conocimiento.

Y de paso se resolvió el desajuste: **etapas son 52, no 50.** Las tres que "faltaban"
—`ECO-00029`, `ECO-00035`, `ECO-00051`— no eran registros borrados: son nuevas.

### D.3 No derivable — ⏸️

`CATALOGO_DE_CONTRATISTAS` (29). **Ningún archivo de OPUS 2025 los menciona.**
Habría que pedirlo, y solo al llegar a contratación.

Sus problemas siguen sin confirmar: multivalor aplanado (`TIPO 1/2`,
`ESPECIALIDAD 1..5`) y 18 especialidades con espacios finales.

## E. Orden sugerido

Lo de abajo habilita lo de arriba:

```
✅ Cerrado: clasificación del concepto (P-01) — 92% deriva del trabajo que usa
1. Equivalencias de concepto (M-15, M-16)  ← los 10 grupos con el mismo núcleo
2. Estimaciones (P-18)                     ← donde el dinero se vuelve real
3. Alcance como catálogo (M-14)            ← el «Incluye:» en 408 de 470
4. Histórico de precios (P-07, P-08)

✅ Cerrado: normalización de unidades y ortografía en todos los catálogos.
```

> **Todo pendiente vive aquí.** Las *ideas del modelo* aún sin diseñar están en `IDEAS.md`
> del conocimiento; este archivo no las repite (`INDICE.md`).

**M-17 y M-18 se pueden reportar hoy**: no dependen de ninguna decisión pendiente.

---

## F. Por construir

Los módulos del sistema. **La columna que importa es «reglas»**: separa lo que ya se
puede escribir de lo que primero hay que definir.

### Base — nada corre sin esto

| # | Módulo | Qué hace | Reglas | Depende de |
|---|---|---|---|---|
| B-01 | **Modelo de datos** | Entidades, relaciones, migraciones | ✅ Aprobado — `MODELO.md`, 10 hallazgos resueltos | — |
| B-02 | **Motor de cálculo** | Suma de partes, recursivo sin límite de capas, `%MO`, las dos lecturas | ✅ **Escrito y probado** — `backend/core/`, 11 pruebas contra `CASO-TRABAJADO.md` (D-178 a D-182) | B-01 |
| B-03 | **`catalogo`** | Insumos, unidades, familias, claves, clonar y borrar | ✅ Definidas | B-01 |
| B-04 | **`apu`** | Matrices, compuestos, versionado | ✅ Definidas | B-02, B-03 |
| B-05 | **`presupuesto`** | Árbol, WBS, cantidades, estados | ✅ Definidas | B-02, B-04 |

> **B-02 es núcleo compartido**, no un módulo más: `presupuesto`, `apu` y
> `parametrico` dependen del mismo motor. No se puede partir en servicios.

### Entrada y salida

| # | Módulo | Qué hace | Reglas | Depende de |
|---|---|---|---|---|
| B-06 | **`importacion`** | Carga desde OPUS: 4 columnas obligatorias, alias, placeholders, huella, versionado | ✅ Definidas | B-03, B-05 |
| B-07 | **Semilla** | Cuadrilla y rendimiento teórico, una sola vez | ✅ El archivo ya existe | B-03 |
| B-08 | **`exportacion`** | Cabeceras, Materiales, Operaciones + los 4 catálogos que se volvieron salida | ⏸️ **P-14** — columnas sin definir | B-05 |
| B-09 | **Traductor de dialectos** | Canon, mapeo por ficha, prueba de ida y vuelta | 🔶 Canon listo; falta el segundo dialecto | B-06 |

### Sobre el modelo ya definido

| # | Módulo | Qué hace | Reglas | Depende de |
|---|---|---|---|---|
| B-10 | **`diccionario`** | Términos, equivalencias, homologación. **Vive dentro del ERP** | ✅ Definidas · datos en `DICCIONARIO-DATOS.md` | B-03 |
| B-11 | **`rediseno`** | Fusión, división, extracción, composición, clonación + las tres capas | ✅ Definidas | B-04 |
| B-12 | **`parametrico`** | Ensambles: plantilla e instancia, divisor, cohorte | ✅ Definidas | B-02, B-04 |
| B-13 | **`programa`** | Actividades, asignaciones, avance, Gantt calculado **y ruta crítica** | 🔶 **P-20**, **P-23** — faltan las precedencias | B-05, B-07 |
| B-14 | **`contratos`** | Cadena de precios, precio por contratista, control de cambio | ✅ Definidas | B-05 |
| B-15 | **Estimaciones** | Cómo se emiten, qué congelan, deducciones, retenciones | ⏸️ **P-18** — sin definir | B-14 |
| B-16 | **Almacén** | Surtido contra consumido, corte matricial contra explosión | ⏸️ **P-19** — sin definir | B-06 |
| B-17 | **Roles y permisos** | Quién captura, aprueba y autoriza | ⏸️ **P-21** — sin definir | Todos |
| B-24 | **`propuestas`** | La bandeja única de «propone, no aplica». Con evidencia, origen y rechazos conservados | ✅ Definidas en `CONOCIMIENTO.md` §14 | B-01 |

### Aún sin diseñar

| # | Módulo | Qué hace | Reglas |
|---|---|---|---|
| B-18 | **Constructor de matrices** | Generar el APU de un elemento. Orden: estructural → instalaciones → carpintería | ⏸️ `IDEAS.md` §4 |
| B-19 | **Cuantificador gráfico** | Trazo → medida → cantidad, ligado al plano | 🔶 **Propuesta escrita** — `PROPUESTA-CUATRO-MODULOS.md` |
| B-25 | **Factorizador de unidades** | Unidad base, presentaciones, mínimo de compra, conversión segura | ✅ **Sus 4 decisiones cerradas** (D-86 a D-92) — listo para que el arquitecto lo diseñe en `CONOCIMIENTO.md` |
| B-20 | **Agente interno** `gravity-obra` | Orquestador + detectores angostos, una sola bandeja | 🔶 **Diseñado** en `gravity-obra.md`. Sigue en fase 2: sus herramientas *son* el modelo de datos |
| 🔧 B-31 | **Agente de Consulta** — el primero de los internos | Define la superficie de herramientas que reusan los otros tres | Su bloqueo (B-01) ya está resuelto — sigue en fase 2 por D-06, no por falta de modelo |
| ✅ B-32 | ~~La alerta no tiene dónde vivir~~ | No es propuesta —sin `objeto` ni `propone`— y hoy se pierde al cerrarse. Sin persistirla no se sabe si la misma salió tres meses seguidos, que es cuando deja de ser aviso | **Resuelto: tabla `ALERTA`**, `MODELO.md` §5a, D-192 |
| B-33 | **La consulta no deja rastro** | El agente de Consulta no escribe nada por diseño. Se pierde qué se pregunta seguido, qué no supo responder y qué herramienta le faltó | ⏸️ Decidir si se registra y con qué retención |
| B-34 | **Embeddings para el diccionario** | Si la detección semántica los usa, necesita `pgvector` en la misma base, y traer su propia regla: cuándo se recalculan al cambiar una descripción | ⏸️ Se decide al llegar al diccionario |
| B-35 | **Dividir `CONOCIMIENTO.md`** | Tres archivos, cada uno numera desde 1 | ✅ Hecho: `CATALOGOS.md` (1,080) · `CONOCIMIENTO.md` (2,444) · `IDEAS.md` (355). Cada uno numera desde 1 |
| B-36 | **Auditoría semántica de referencias** | Comprobar que cada `§N` apunte al tema, no sólo que resuelva | ✅ Hecha: 16 apuntaban a sección equivocada, 3 de ellas **anteriores a la división** (las capas de sobrecosto nunca estuvieron en el conocimiento, viven en `erp-construccion.md` §6) |
| B-37 | **Dos referencias de `MODELO.md` sin destino claro** | Decidir a dónde debían apuntar | ✅ **Resuelto por el propio texto, sin adivinar.** `Origen = Material` decía «caso trabajado» → `CASO-TRABAJADO.md` (ahí están `ZA1-000001` y `MOC-12010`). El WBS sin patrón decía «prueba de ida y vuelta» → `CATALOGOS.md` §11 (ahí está el ejemplo de `EST-02010` con segmento propio) |
| B-38 | **¿Once o doce ingenierías de `ALAMO 18`?** | Conteo aparentemente contradictorio | ✅ **No era contradicción: azotea se subió después de §11.8.** §11.8 queda como línea base de once; §11.10 y §11.11 ya son doce. Aclarado en `CONOCIMIENTO.md` §11.8 |
| B-39 | **Escenarios de presupuesto** | Varias versiones de la misma casa para comparar antes de decidir | ⏸️ **Decidido el alcance:** cambian precio/proveedor, alcance y programa — los tres tipos. **Uno queda vigente, el resto se archiva, no se descarta.** Falta diseñar |
| B-42 | **Escenarios de prueba** (funcionamiento del sistema) | Casos con datos reales para probar que el sistema hace lo que dice | 🔶 **Tres corridos:** ALAMO 18, Zafiro 1.0 y los siete prototipos. 13 pasan, 8 se rompen, 5 sin dato |
| B-40 | **El tiempo de entrega del material** | Dónde vive y en qué base | ✅ **Resuelto:** por familia con excepción por insumo, y **cada valor declara si es en días naturales o hábiles**. `CONOCIMIENTO.md` §15. Verificado que ningún catálogo lo traía, ni hay proveedores |
| B-41 | **Recursos por fecha — la salida del CPM** | Material, mano de obra, subcontratos y egreso, proyectados en el tiempo | 🔶 Escrito en la propuesta. Misma explosión leída por fecha, no es módulo nuevo. **Depende de B-40 para que el material dé fecha de pedido y no de consumo** |
| B-43 | **La actividad interrumpida (tramos)** | Una actividad que se detiene y continúa — muro que para para colar cadena | ⏸️ **No contemplado.** El modelo asume barra continua. Sin tramos, la proyección diaria de material es incorrecta y el hueco de cuadrilla es invisible. **P-5** |
| B-44 | **Aprender de los ERPs ya formados o semiformados** | Un sistema en uso trae reglas probadas contra la realidad. Hay que **identificar, aprender, decidir e implementar** — validando, nunca copiando | ⏸️ Idea general, sin diseñar. Distinto de `ESCALABILIDAD.md` §6, que es cómo **colgar** un módulo sobre un ERP ajeno; esto es qué **extraerle** |
| B-45 | **Reglas de gobierno configurables por obra** | Dónde vive lo que se decide al asignar la obra a un residente: quién traza, si hace falta aprobar | ⏸️ **Primera de su tipo.** El modelo no tiene hoy configuración por obra — hace falta decidir si es tabla, campo o perfil |
| B-46 | **La regla del residuo de la reversión** | Qué hace el sistema con los destajos ambiguos y los sin candidato | ✅ **Resuelto: son cuatro casos, no uno.** Ambiguo → propuesta con todos los candidatos · clave inexistente → dos lecturas y reporte sin tocar · destajo de compuesto → ampliar la búsqueda (sube a 87%) · **nunca por proximidad**. `CONOCIMIENTO.md` §11.9 |
| B-47 | **Normalizar profundidad de explosión antes de comparar** | Dos fuentes con distinto nivel de desglose no se restan directamente | ✅ **Resuelto:** financiera primero, cerrada en la matriz del concepto y dentro de cada fuente; naturaleza después, al insumo atómico. Escrito en `CONOCIMIENTO.md` §10.5 y en el skill base |
| B-48 | **¿Se programan los niveles sin ingeniería?** | 5 niveles del Diamante — el 8% | 🔶 **Sí, por inicio y duración**, con la duración preestablecida por nivel y el inicio disparado por anticipo o junta de arranque. **Falta la lista de qué partidas se contratan terminadas y cuáles no** |
| B-49 | **La Δ $4.30 del artefacto** | Saber si es redondeo acumulado u otra cosa | 🔶 **Hipótesis con predicción:** redondear el importe a centavos daría ±$0.11 — cien veces menos. Redondear el **PU** a centavos y multiplicar por cantidad da ±$4.7 con 350 renglones. **Comprobable:** sobre los 7 prototipos la deriva debería rondar $11 |
| B-50 | **Normalizar la unidad del presupuesto al cargar** | El presupuesto usa `pza`/`ser`; los catálogos usan `PZ`/`SERV` | ✅ **Resuelto:** se normaliza al cargar y se guarda normalizada, contra el catálogo cerrado de 17. Lo que no mapea **se carga igual** y se da de alta por validar. `erp-importacion.md` §4b. **Verificado: los catálogos estaban limpios; `M²` no existía** |
| B-51 | **La regla del concepto no clasificable** | Qué pasa con el 8% que no tiene de dónde derivar su clase | ✅ **Ya estaba resuelto en `MODELO.md`:** `subfamilia_id` es nullable, se clasifica después a mano y **no bloquea la carga**. Tercera vez que un pendiente ya tenía respuesta sin releerse |
| B-52 | **La cohorte de cimentación no es el número de plantas** | Qué separa a Zafiro Plus y Oro del resto | 🔶 **Recalculado:** 5 de 7 comparten tasa con CV 2.8% —los Diamante de dos plantas incluidos—; Zafiro Plus y Oro están 1.71× abajo. **No es plantas.** Falta saber qué es |
| B-53 | **El parámetro propio por ensamble no tiene dónde vivir ni de dónde salir** | Decidido en D-98, sin campo ni fuente | ⏸️ El catálogo trae m² construidos, no desplante ni salidas. **El cuantificador es quien los produciría** |
| B-54 | **Renovación semestral de las invariantes de valor** | Quién y cuándo actualiza $16,460,623.50 y las demás cifras base | ⏸️ Sin proceso. Si nadie las renueva, el verificador marcará falla sobre datos correctos |
| B-55 | **Rendimiento de material — el triángulo con el avance** | Salida de almacén + avance físico + rendimiento del material: dos comprueban el tercero | ⏸️ **Nuevo y de otra familia:** los tres rendimientos del modelo son de mano de obra. Caso: 500 ladrillos no alcanzan para 200 m² de muro. §11.12 hoy compara salidas contra explosión, **sin avance** |
| B-56 | **El frente está marcado como informativo y se quiere calcular con él** | Cuántas cuadrillas hacen falta para atacar un frente | ⏸️ `CATALOGOS.md` advierte: «no valida, no impide, no calcula… si no, alguien construirá encima algo que no la soporta». Además el frente hoy es catálogo propio, no concepto/etapa/nivel |
| B-57 | **¿De dónde saca su familia un trabajo?** | La cadena de derivación | ✅ **De su propia columna `Familia`.** No se deriva: está declarada, en los tres catálogos, sin vacíos. **El concepto es el único que no la trae** |
| B-58 | **Nueve familias duplicadas por acento** | El catálogo las guarda sin acentuar y el uso las acentúa | ✅ **Resuelto: la acentuada es la canónica**, se corrige el catálogo. Mapeo verificado uno a uno, ninguna ambigua. En `DICCIONARIO-DATOS.md` |
| B-59 | ~~Faltan 13 familias en el catálogo~~ | — | ✅ **No faltaba nada.** Materiales, trabajos y mano de obra **declaran su familia y subfamilia en columnas propias, sin un solo vacío**. `CATALOGO_DE_FAMILIAS` no es el maestro: es la nomenclatura de prefijos de clave de materiales |
| B-60 | **Las tres tablas: normalización, homologación, grupos funcionales** | Cada una con su lista, su origen y su evidencia | 🔶 **Diseñadas en `CONOCIMIENTO.md` §16.** Falta modelarlas. Recuperan parte del diseño del diccionario perdido en B-29 |
| B-61 | **Bitácora de cambio de familia y subfamilia** | Anterior, nueva, quién, cuándo · y marcar recalculable la tasa paramétrica | ⏸️ Decidido, sin modelar |
| B-62 | **Capa de servicio separada de la API** | La lógica no vive en los endpoints | ⏸️ **Decidido (D-167), sin construir.** Es lo único de MCP que es caro si se deja para después |
| B-63 | **Servidor MCP** | Herramientas específicas sobre la capa de servicio | ⏸️ **Después del agente interno.** Uno solo para empezar; se parte por permisos cuando haga falta |

### Infraestructura

| # | Qué | Estado |
|---|---|---|
| B-21 | `backend/` en Render · `database/` en Supabase | Definido en `CONOCIMIENTO.md` §3.3 |
| B-22 | `frontend/` web en Vercel · móvil en Google Studio | El móvil consume la API, **nunca la base directo** |
| B-23 | Los agentes de desarrollo en `.claude/agents/` | ✅ Cuatro escritos: arquitecto, constructor, migrador, **auditor** |
| B-26 | **Contrato de módulo** — seis preguntas que todo módulo contesta antes de construirse | ✅ Escrito en `ESCALABILIDAD.md` |
| B-27 | **Partir el skill por módulo**, compilado desde el conocimiento | ⏸️ No antes de que los módulos existan |
| B-28 | **Verificador de coherencia del cerebro** | ✅ `2-operacion/verificar-cerebro.py` · 7 comprobaciones · lo corre el auditor |
| B-29 | **El diseño del diccionario no está en `CONOCIMIENTO.md`** | ⏸️ Se retiró `DICCIONARIO-CONCEPTOS.md` por «incorporado al conocimiento», pero ahí sólo quedaron 12 menciones de paso y **ninguna sección propia**. Bloquea el skill `erp-diccionario` |
| B-30 | **Auditar los cuatro archivos retirados antes de darlos por absorbidos** | ⏸️ Dos hechos verificados se perdieron al retirarlos: el diseño del diccionario (B-29) y la restricción de que los subagentes no se lanzan entre sí, recuperada en D-64 |

---

### Lo que se puede empezar hoy

**B-01 ya no bloquea: está aprobado.** B-02, su núcleo, ya tiene código y pruebas
en `backend/core/`. B-03 a B-07 y B-10 a B-12 siguen con sus reglas escritas y
verificadas: **se pueden construir sin esperar ninguna decisión.**

Lo demás espera a que se definan P-14, P-18, P-19, P-20 y P-21.
