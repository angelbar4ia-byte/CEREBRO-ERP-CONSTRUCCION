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
| **Histórico de precios** | Cierra P-07/P-08 — `PRECIO_HISTORICO`, `VERSION_CONCEPTO.pu`, `TABULADOR_CONTRATISTA` (`MODELO.md` §4a) · marcador de prototipo (P-40) cierra con `PRESUPUESTO.tipo` · 🆕 `fuente` gana `almacen`/`estimacion`, pendiente desde que P-18/P-19 cerraron · 🆕 **Confirmado con dato real (D-362): la deriva de precio es pequeña y real** (tabique +3.6%/5 meses), pero `C/Ultimo`/`C/Promedio` traen ruido de captura (filas rotas que su propio `Efecto Costo` no respalda, cancelaciones con precio negativo) — si se alimenta `PRECIO_HISTORICO` desde este crudo, hay que validar contra `Efecto Costo`, no leer el precio directo · 🆕 **Cierra P-39 (D-366): `CONTRATISTA` nuevo** — el nombre viaja al 100% en el crudo de almacén, 39 reales con volumen recurrente entre lotes; desbloquea `TABULADOR_CONTRATISTA`, `DEDUCCION` y `PRESTAMO` de un golpe |
| **Almacén** | Cierra P-19/B-16 — tabla `MOVIMIENTO_ALMACEN`; el archivo real ya separaba surtido (`salida_produccion`) de consumido (`implosion`) sin campo nuevo, corte matricial es vista sobre `COMPOSICION`, no tabla (`MODELO.md` §5e, D-333). Devoluciones sin espécimen real todavía, queda abierto. 🆕 **Auditoría (D-337): le faltaba `presupuesto_id`** — sin él, siete de ocho motivos no tenían cómo decir de qué obra son. Se agrega, resuelto de `Lote` al importar. 🆕 **Hallazgo (D-367): postventa es un proceso real y separado, nunca modelado** — 213 filas reales en cinco meses (10 de gasto de oficina excluidas), $104,901.95 en reparaciones de garantía sobre casas ya entregadas. 🆕 **Cierra P-41 (D-370): modelo completo, dato del usuario** — `PRESUPUESTO.fecha_entrega`, `TICKET_GARANTIA` (causa en ocho valores reales) y `MOVIMIENTO_ALMACEN.ticket_garantia_id` nuevos; costo de garantía es consulta aparte, no sexta columna de B-71 (`MODELO.md` §3b) |
| **Comparación y reportes de obra** | Cierra B-71 — de las cinco columnas (Base, Ingeniería, Pagado Real, Formado, Control de Cambio), cuatro reusan tabla ya cerrada y la quinta (`PROPUESTA(tipo=orden_cambio)`) solo necesitaba la forma de su JSON (`MODELO.md` §5f, D-334). Subcontratos siguen bloqueados en dato (`subcontratos.csv` vacío, D-321), no en diseño. 🆕 **Auditoría (D-337): Pagado Real de material corregido** — era `motivo=recepcion` (sin `Lote`, no atribuible a obra), ahora `salida_produccion`/`implosion`. 🆕 **Cierra B-78: sin umbral por %, dato del usuario** — `ALERTA(tipo=subcontrato_fuera_de_base)` dispara en cualquier divergencia Real-vs-Base; el lado bajo puede ser ahorro o reducción de alcance (como la cochera, D-321), simétrico al lado alto — mismo `orden_cambio`, `delta_monto` con signo (`MODELO.md` §5a, D-354). 🆕 **Segunda corrección a Pagado Real (D-363): el andamio tampoco es material directo, dato del usuario** — `HET-00034` se excluye, su costo pasa a la capa de indirectos (`CONOCIMIENTO.md` §5), primer dato real que la ejerce; acotado a esta clave, no a toda `categoria=herramienta`/`equipo` (`MODELO.md` §5f) |
| **Escenario** | 🆕 Cierra B-39 — `PRESUPUESTO.tipo` gana `escenario`, gratis con su propio árbol y programa; elegir uno se traduce a la obra vía rediseño, sin reemplazar su identidad (`MODELO.md` §3a, D-335). El caso real que lo motivó (mortero/cemento) resultó ser otro mecanismo — leer `VERSION_CONCEPTO` a la fecha correcta, sin campo nuevo |
| **Recursos por fecha** | 🆕 Cierra B-40/B-41 — `CONSTANTE_FISICA` gana `categoria=tiempo_entrega` (mismo mecanismo que la vara comercial); material por fecha resta ese tiempo a la fecha de `TRAMO`/`ACTIVIDAD`, sin tabla nueva (`MODELO.md` §1c/§5f, D-336). De paso, confirmado que `CONOCIMIENTO.md` §15 ya tenía cerradas precedencias/holguras/ruta crítica desde P-20 — título desactualizado, corregido. Quedan dos huecos de dato: cuándo contratar un subcontrato y cuándo se paga, los dos atados al catálogo de proveedores que no existe (P-39). 🆕 **Confirmado con dato real (D-361): el proveedor y la orden de compra ya viajan en el crudo del almacén** (`Proveedor`, `Orden Compra` formato `PC-nnnnnn`, 97.3% de las recepciones de julio) — sin catálogo que los normalice, mismo hueco, ahora con evidencia concreta de la forma que tendría |
| **Ensamble / Paramétrico** | 🆕 Cierra B-53 — `NODO`(rol=ensamble)+`COMPOSICION` reusados sin campo nuevo, `ENSAMBLE_PARAMETRO` nuevo para tasa/cohorte/dispersión (`MODELO.md` §1c, D-325). `CONSTANTE_FISICA` (B-18) con dos filas reales; el motor de cálculo del constructor sigue sin diseñar, D-326. 🆕 **P-22 se parte en dos rutas** — por analogía cierra (`PROPUESTA(tipo=matriz_generada)`, copia y escala, nunca genera; corpus es `PROPUESTA` misma, `MODELO.md` §5, D-352); por fórmula sigue siendo B-18, bloqueado en constantes físicas |
| **Método** | `METODO.md` — cómo se razona, con los errores que lo enseñaron |
| **Lenguaje** | Canon 1.0, tres dialectos, prueba de ida y vuelta ejecutada · 🆕 Avanza P-14/B-09 — Cabeceras/Materiales/Operaciones confirmados contra el propio dialecto OPUS y el join entre ellos validado sin huérfanos; `Flete`, archivo-vs-API y los 4 catálogos de salida siguen abiertos (`CONOCIMIENTO.md` §4.3, D-331/D-332) |
| **Memoria** | 388 decisiones · 12 descartes · 21 correcciones · 13 hallazgos de construcción · 🆕 recuento completo desde D-01, el número venía sobrestimado (D-338) |
| **Desviación, Consulta y renovación de invariantes** | 🆕 `DESVIACION` cierra tercera aparición del mismo hueco — patrones son `GROUP BY`, no tabla (`MODELO.md` §5g, D-343). `CONSULTA_LOG` le da bandeja propia a Consulta, persistente sin retención (§5h, D-344, B-33). Renovación semestral de invariantes es una `ALERTA` más, lee el `corte:` que ya existe, sin campo nuevo — Control de obra la resuelve (§5a, D-345, B-54). 🆕 **Corrección (D-347): `causa` tenía el vocabulario equivocado** — las nueve causas de §13.6 deciden si la fila es `DESVIACION` siquiera, no la describen; el vocabulario real es «causas por categoría», del mismo §13.6 |
| **Cuatro decisiones de política del usuario** | 🆕 P-34 (`NODO.marca_revisado`, checklist no validación) · P-35 (sustitución = `PROPUESTA(tipo=version)` + `GRUPO_FUNCIONAL`, ya lo tenía el caso mortero/cemento) · P-36 (consolidar solo al leer, no al cargar — depende de compras/obra vs. costos/control) · P-27 (`PROPUESTA(tipo=patron_carga)`, confirma la forma una vez, no por archivo) — D-339 a D-342. 🆕 **Cierra P-26**: las cinco estructuras de ingeniería (`CONOCIMIENTO.md` §11.8) ya caían bajo `patron_carga` — la firma solo necesitaba el patrón de llenado de la columna de agrupador, no solo conteo de columnas (D-351) |
| **Skill** | Base + 4 satélites compilados: importación, rediseño, paramétrico, 🆕 cuantificador |
| **Agentes** | 🆕 **gravity** orquesta · arquitecto, constructor, migrador, auditor · 🆕 **gravity-obra** interno |
| **Glosario** | 79 términos · 25 ambigüedades |
| **Diccionario de datos** | 🆕 Cierra B-60/B-61/B-29 — homologación reusa `EQUIVALENCIA` + `CLON` (viaje de vuelta, dos campos nuevos); `NORMALIZACION` y `GRUPO_FUNCIONAL` son tabla nueva; `BITACORA_RECLASIFICACION` con `ENSAMBLE_PARAMETRO.revisar` (`MODELO.md` §4b, D-328) |
| **Módulos** | Las 22 decisiones de los cuatro cerradas (CPM cierra con P-10: reiniciar programa no toca lo registrado) · Cuantificador con tabla (`MODELO.md` §1b) · CPM con tabla completa (`MODELO.md` §5c, D-327) — `ACTIVIDAD`, `PRECEDENCIA`, `CALENDARIO`, `TRAMO`, los dos cuantificadores, `FRENTE_TOPE_CUADRILLA`, `CIERRE_FRENTE` · 🆕 **Factorizador con tabla (B-25 cierra)** — `PRESENTACION_COMPRA` nueva (`MODELO.md` §2a, D-348); la conversión dimensional (aparejo) reusa `CONSTANTE_FISICA`, sin caso real todavía. 🆕 **F-3 confirmado del lado del consumo (D-359):** el cemento comprado a existencia general lo reparten 26 lotes distintos en cinco meses reales — quince materiales masivos repiten el patrón |
| **Estimación** | 🆕 Cierra P-18 — dos fuentes, el tope es el mismo techo del cuantificador de presupuesto (D-273/D-285), topes pagados = Tope − Pagado, deducciones/retenciones/préstamos definidos. Validado contra un archivo real: 0 de 416 filas exceden el tope. `CONOCIMIENTO.md` §13.8 |
| **Pruebas de flujo** | 🆕 Tres corridas, mismo criterio en las tres desde D-346: ALAMO 18, Zafiro 1.0, siete prototipos · 26 etapas — 13 pasan, 3 con matices, 7 diseñadas sin caso real que las ejerciten, 3 sin poder probarse — cinco hallazgos de Zafiro/prototipos ya estaban resueltos sin sincronizar. 🆕 ALAMO 18 sube de 3 a 4 pasan (D-375): salidas y desviación cierra, el triángulo material-avance cuadra en acumulado |
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
| **Semilla** | Cuadrilla y rendimiento teórico, 265 filas · 🆕 **archivo guardado (D-386):** 26 claves ya cruzadas contra ejecución real en `CATALOGOS.md` §10, castillo K1 cierra exacto |
| **Ingenierías de ALAMO 18** | 12 archivos. Las partes se suman; faltan 5 niveles (uno, Consumibles, en $0). 🆕 De los otros 4 sin ingeniería —Cancelería/Carpintería/Muebles-Iluminación/Herrería— se sabe el costo exacto: $542,464.67, 19.2% del base **en dinero** (no confundir con el 92%/8% por conteo de etapas de `PRUEBA-ALAMO-18.md` §5). 🆕 **Cierra B-48: dato del usuario, Cancelería/Carpintería/Herrería se contratan terminados, Muebles/Iluminación se programa con detalle** — mecanismo ya existente, `ACTIVIDAD.modo_duracion=preestablecida_nivel`+`disparador_fecha=contractual` (`MODELO.md` §5c, D-327/D-353). Cubiertas/Pérgolas/Impermeabilizante también van terminados aunque sí tienen presupuesto — ingeniería cargada y contrato terminado son ejes independientes |
| **Reversión por destajo** | Probada: 84% en cimentación. 🆕 Escalada a diez niveles completos: **catálogo de presupuesto reconstruido desde la ingeniería real**, $2,561,657.71, +12.0% vs. catálogo de referencia. Dos técnicas nuevas fijas —concepto auxiliar (dominante) y concepto "lote" para material compartido sin llave— más las reglas de desempate que le faltaban a la reversión. 🆕 **Extendido a instalaciones (D-383):** prototipo con/sin chimenea comparten casi todo el catálogo (una sola línea distinta); hidráulica y gas cierran limpio contra el presupuesto base; eléctrica sube ~45-51% de forma sostenida, mezcla de efecto cantidad y receta, sin separar todavía. 🆕 **Destajo, no solo material (D-384):** eléctrica también se sale +31.5% en mano de obra, misma dirección que en material — dos dimensiones de costo de acuerdo. `PRECIO_REAL` no registra ni una fila de destajo eléctrico en cinco meses. 🆕 **Antes de un programa real (D-385):** explorado el resto de `grid_AvanceOPEventosOpr` — `Nivel OP` confirma castillo K1 multi-nivel (D-377) por un campo distinto y encuentra que `ALB-01010` también lo es; teoría del usuario sobre `C/Liberada` confirmada solo en `EST-01060` (-30% de tarifa en revisión) — en los otros nueve conceptos la tarifa no cambia y las dos banderas hacen falta para el total real, validando D-376 a D-384. 🆕 **`SEMILLA-cuadrilla-rendimiento.xlsx` llega y se guarda (D-386):** castillo K1 cierra en 1.00 cuadrilla exacta contra el rendimiento teórico, usando los huecos de D-385 — valida los dos mecanismos a la vez. 🆕 **Precedencia técnica violada, deficiencia de calidad real (D-387):** dato del usuario — instalaciones de muro debían pasar antes de colar la cadena de cerramiento; en `ALAMO 18` las tres que arrancaron llegan el mismo día o después de las dos cadenas del prototipo, nunca antes. 🆕 **Corregido (D-388): solo eléctrica.** Dato del usuario — hidráulica/sanitaria no cruzan la cadena salvo la línea a Planta Alta, y esa línea específica sale a tiempo en las dos; queda exonerada. `CONOCIMIENTO.md` §11.13, §11.14, §13.6, `CATALOGOS.md` §10, `PENDIENTES-MEJORAS.md` B-43, D-238 a D-242, D-383 a D-388 |
| **Rendimiento real vs. almacén** | 🆕 Léxico del archivo resuelto (`Lote`, no `Ubicacion`/`# Lote`; cadena `OP:`/`No.Parte:`). Dos conceptos de abril cruzados contra su matriz a la misma escala (reversión), con el bug de mano de obra corregido: -19.7%/-2.6%. Corte semanal nuevo: tabique y cemento se abastecen los dos por lote, diferencia de grado no de tipo — una primera lectura con solo abril decía 68.5% del pagado sin respaldo de cemento en una semana de `EST-02010`, 🆕 **corregido con cinco meses (D-375): era la ventana incompleta, en acumulado el respaldo cuadra al 99.8%.** La hipótesis de tramo sobre ese mismo caso no se confirmó (D-260). 🆕 «Rendimiento real» separado en dos: mano de obra (alimenta al CPM) y material (alimenta al costo), nunca el mismo dato (`CONOCIMIENTO.md` §6.2) · avance físico y avance pagado son dos registros que no se sobrescriben, la diferencia es la señal (§13.7). `CONOCIMIENTO.md` §11.15 a §11.17, D-249 a D-256, D-260, D-263, D-264. 🆕 **Cierra B-70: el cruce se mueve de después del pago a antes** — `ALERTA(tipo=estimacion_sin_respaldo_material)` corre en `validar_estimacion`, sin tabla nueva (`MODELO.md` §5a, D-350). 🆕 **P-38 avanza (D-355): marzo a julio cargados, de 76 a 358 movimientos reales de ALAMO 18** (`Lote`=18 **y** `Ubicacion`=ALAMO juntos) — `EST-02010` confirma tabique/cemento en cuatro meses seguidos, julio con cero tabique es la prueba más limpia hasta hoy. 🆕 **Hallazgo (D-356): la cimbra no se registra para esta obra** pese a exigirla en 167 renglones del presupuesto — no es hueco de `MOVIMIENTO_ALMACEN`, es que nadie la registra (`CONOCIMIENTO.md` §11.20). 🆕 **Auditoría de los 20 conceptos reales (D-357): la cimbra es caso único, no síntoma** — 14 de 20 calzan exacto contra su matriz, el resto ya tenía explicación (abasto por lote, efecto receta de B-68). 🆕 **Corrige D-333 (D-358): `motivo` no era cerrado** — cinco meses trajeron `reversion_movimiento_erroneo` (limpio) y `devolucion_cliente` (candidato débil, no cierra la pregunta de P-19 sobre devoluciones). 🆕 **La otra mitad de la pregunta (D-360): insumos que no hacen falta, uno real, no un patrón** — de 387 materiales por `Clase`, solo `MOF-00020` (ventilador de oficina) es limpio, gasto de oficina en el mismo catálogo, nunca ligado a un `Lote` real; el resto de `Consumo Internos` no distorsiona ningún corte matricial. Hallazgo aparte: ruido de `Grupo` (Servicios/Clientes/Equipo De Computo) es limpieza de catálogo, no diseño (`CONOCIMIENTO.md` §11.20). 🆕 **Corrige D-249/D-337 (D-365): `Lote` solo tampoco es único** — se repite entre calles distintas (26 de 31 números, hasta seis calles para uno solo); la llave real es `(Ubicacion, Lote)`. El conteo de ALAMO 18 baja de 386 a 358 movimientos reales (28 eran de otras casas, sin `# OP`); `EST-02010`, la cimbra y el conteo de 47 `# OP` quedan exactos, no los tocaba la contaminación. `MODELO.md` §5e, `CONOCIMIENTO.md` §11.15/§11.20. 🆕 **Cierra B-55/P-38 (D-375): el triángulo material-avance cuadra en acumulado** — con `grid_AvanceOPEventosOpr` de los cinco meses, 238 sacos de cemento real contra 237.6 que pide el rendimiento teórico para los 730.15 M² pagados de `EST-02010`, 0.17% de diferencia. Corrige el 68.5% original y el diseño de `estimacion_sin_respaldo_material` (ahora compara acumulado, no periodo suelto). 🆕 **Extendido a 17 conceptos (D-376): confirma la regla en la mayoría, semilla `TESTIGO_MATERIAL` nueva (`CATALOGOS.md` §12)** — castillo K1 en `ALAMO 18` mostró +141.7% del cemento teórico en una primera lectura. Cierra B-79: `ALERTA(tipo=consumo_material_sin_respaldo_avance)`, el mismo cruce vigilando también el lado de exceso, no solo el de faltante. 🆕 **Corrige D-376 (D-377): castillo K1 no era exceso** — cruzado contra la ingeniería (`EST-02110` diseñado 3 veces, 339.20 M) y `PRECIO_REAL`, es el único de sus seis hermanos sin terminar (71.1% vs. 97-100%) y el único donde `grid_AvanceOPEventosOpr` se quedó corto (32.8%); el cemento seguía el avance real, no el recorte de una sola fuente. 🆕 **Mismo cruce sobre los `insuficiente` (D-378): `ALB-01010` se resuelve igual que K1 (+109%→+15.5%); `ALB-01212` es el caso limpio que `estimacion_sin_respaldo_material` necesitaba** — 100% avanzado en las tres fuentes, cero movimientos de almacén en su orden. 🆕 **Corrige D-378 (D-379): `ALB-01012` es el caso real de `consumo_material_sin_respaldo_avance`, no una anomalía sin explicar** — dato del usuario, el testigo es cemento de su matriz genérica (no el mortero de la ingeniería del lote, desactualizada); adelantado a todas las fuentes de avance a la vez, dos hipótesis de campo no excluyentes (avance sin estimar, o material desviado a otra actividad) con el mismo riesgo: faltante que solo se ve hasta el cierre de obra. 🆕 **Cierra el cruce contra ingeniería (D-380):** los últimos dos `Consistente` (`EST-02011`, `ALB-01210`) confirman sin drama — los diecisiete conceptos originales de la semilla `TESTIGO_MATERIAL` quedan completamente validados. 🆕 **Extendido a instalaciones (D-381/D-382):** eléctrica (72.8%), hidráulica (100.0%, triple confirmado) y gas (96.9%, con su propia clave doble corregida) confirman sin novedad; sanitaria repite por tercera vez el patrón de B-70 —`HID-00411` emitido una sola vez para cuatro conceptos activos, tres facturando 86.6%-100% de avance sin material—, la primera vez fuera de estructura |
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
él los módulos con reglas escritas y verificadas siguen creciendo: motor de
cálculo, catálogo, APU, presupuesto, importación, semilla, diccionario,
rediseño, paramétrico/ensamble, propuestas, alerta, cuantificación, histórico
de precios, estimaciones, programa (modelo de datos completo — el motor de
cálculo del CPM sigue siendo código, no schema), permisos, almacén,
comparación/reportes de obra y escenario.

Lo único que sigue sin decisión: exportación —los tres reportes ya resueltos,
faltan los cuatro catálogos que se volvieron salida, bloqueados en el catálogo
viejo— (P-14).

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
