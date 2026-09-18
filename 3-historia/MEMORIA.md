# MEMORIA

```
órgano:     hipocampo
capa:       III — Historia
pregunta:   ¿qué decidimos, qué descartamos?
tiempo:     fue así
corte:      2026-09-15
verificado: 230 decisiones · 12 descartes · 8 correcciones
```

> **Qué decidimos, qué descartamos y en qué nos equivocamos.**
>
> El conocimiento tiene la verdad de hoy. Este archivo tiene **cómo se llegó a
> ella** — y sobre todo **lo que ya se rechazó**, para que no se vuelva a proponer.
>
> Última actualización: 2026-09-15

---

## Por qué existe

Un agente propone lo razonable **una y otra vez**. Sin registro de lo descartado, en
tres meses alguien va a sugerir otra vez que `%MO` sea un campo, que se renombre el
prefijo o que se use MPTT — todas ideas sensatas que ya se evaluaron y se
rechazaron por razones concretas.

Y lo que estuvo mal y se corrigió también importa: el conocimiento tiene la versión
buena, pero **no el aviso de «esto se creyó al revés»**.

---

# 1. Decisiones

## Alcance y arquitectura

| # | Decisión | Por qué |
|---|---|---|
| D-01 | **CPU = APU**, no CPM | Aclarado en la primera sesión |
| D-02 | Python (Django/FastAPI) sobre PostgreSQL | |
| D-03 | Tres carpetas: `backend/` Render · `database/` Supabase · `frontend/` Vercel web y Google Studio móvil | |
| D-04 | Monolito con fachadas, migrable a microservicios. *Screaming* y *clean* | Evitar el efecto espagueti |
| D-05 | Agentes de desarrollo: arquitecto, constructor, migrador · **auditor (D-58)** · **gravity orquesta (D-64)** | El asistente de obra se aplaza |
| D-06 | El asistente de obra va con el Agent SDK, **en fase 2** | Sus herramientas *son* el modelo de datos: sin modelo no hay agente |
| D-07 | Los entregables van en **Markdown**, no Excel | Los catálogos corregidos sí regresan en xlsx: vuelven a OPUS |

## Modelo

| # | Decisión | Por qué |
|---|---|---|
| D-08 | **Un solo árbol recursivo**, padre-hijo con tipo en el nodo | Los datos ya lo hacen así |
| D-09 | El nodo se identifica **por posición**, no por clave | La misma clave aparece en decenas de nodos |
| D-10 | La profundidad de anidamiento es **libre** | Hoy llega a 2; el modelo no debe asumirlo |
| D-11 | Las partes **siempre suben**; lo declarado queda como cifra paralela | Verificado en los cuatro archivos |
| D-12 | Motor de cálculo **configurable en dos niveles** | México y Colombia difieren en la *base*, no solo en el porcentaje |
| D-13 | La **cuadrilla es capacidad**, no costo | Confirmado: ningún concepto la referencia |
| D-14 | Insumos colgados de la etapa son **intencionales** | |
| D-15 | El **paramétrico son ensambles**: el mismo mecanismo del APU un piso arriba | No es un módulo aparte |
| D-16 | En el ensamble, **la cantidad es receta**, no volumen | Por eso el traslape deja de ser problema |
| D-17 | El ensamble referencia **al concepto**, no al renglón de presupuesto | Para que sobreviva sin su presupuesto de origen |
| D-18 | El rediseño se guarda como **receta reaplicable**, en tres capas | Lo cargado es inmutable |

## Identidad

| # | Decisión | Por qué |
|---|---|---|
| D-19 | El `id` lo genera la base **en el `INSERT`** | Antes de tener posición |
| D-20 | El **WBS se separa con puntos**, ancho libre | Se acabó el techo de 99 hermanos… salvo al exportar |
| D-21 | **La clave nunca se reescribe** | Hay contratos apuntándole |
| D-22 | Se **clona**: mantener para variantes, sustituir para reemplazos | Las variantes son el uso principal |
| D-23 | **Se puede borrar**, solo si nada depende | Ninguna referencia, o solo con cantidad cero |
| D-24 | **El borrado no baja** | Borrar una mezcla no toca su cemento |
| D-25 | El estado de congelamiento es **del nodo**, no del presupuesto | Los planos llegan por partes |

## Contratación y obra

| # | Decisión | Por qué |
|---|---|---|
| D-26 | **Cuatro precios en cadena**: catálogo, presupuesto, contrato, ejecutado | Cada salto mide algo distinto |
| D-27 | El precio del contrato **no toca el catálogo** | Es una negociación, no un cambio de costo |
| D-28 | **Antes de pagar hay renegociación; después, descuento** | El descuento deja rastro; la renegociación no lo necesita |
| D-29 | El PU **no es piso ni techo**: es la referencia | El pactado puede quedar arriba, y eso es información |
| D-30 | **Registrar nunca se bloquea**; comprometer sí exige costeo | La obra no para |
| D-31 | El control de cambio **no edita, agrega** | Y registra si se autorizó antes o después de ejecutar |

## Método de trabajo

| # | Decisión | Por qué |
|---|---|---|
| D-32 | **El sistema propone, el humano aprueba** | Vale para diccionario, versiones, repartos y matrices generadas |
| D-33 | **Los rechazos se conservan** | Evitan reproponer lo mismo |
| D-34 | Cada hecho vive en **un solo archivo** | Ver `INDICE.md` |
| D-35 | Los catálogos de la generación anterior **pasan a ser salida generada** | Los otros ERP los siguen necesitando, pero alimentados desde OPUS y el conocimiento |
| D-36 | **Los vocabularios se derivan de los datos**, no se cargan ni se piden | Unidades, niveles, etapas y familias ya están dentro de OPUS 2025. Solo contratistas no es derivable |
| D-37 | **Son tres rendimientos**: calculado, teórico y real | El calculado nunca se captura; su diferencia con el teórico es el indicador |
| D-38 | Cuadrilla y rendimiento teórico se cargan como **semilla, una sola vez** | OPUS no los entrega y nunca los va a entregar. De ahí viven en el ERP |
| D-39 | Son **dos campos del trabajo**, no una tabla aparte | Uno a uno, como los tenía el catálogo anterior |
| D-40 | **El nuevo ERP es la clave neutra**; los demás se conectan a él | No elige entre A, B o C: él *es* la C |
| D-41 | La forma de conexión la decide **cuántas referencias vivas** tiene ese ERP | Ninguna → se alinea. Muchas → correspondencia. **El sistema puede contarlas** |
| D-42 | Se pasa de **A a B, nunca al revés** | Se decide al conectar, y queda registrado |
| D-43 | Cada dialecto se declara con una **ficha** | Si conectar un sistema es llenarla y nada más, el canon funcionó |
| D-44 | **La propuesta es una entidad**, no un campo por mecanismo | «Propone, no aplica» aparece 9 veces; sin entidad serían 9 bandejas |
| D-45 | **La evidencia no es opcional** | Una propuesta sin evidencia es una orden disfrazada |
| D-46 | **La detección no necesita permiso; la corrección sí** | Es la línea de lo que el agente hace solo |
| D-47 | **`MODELO.md` producido y aprobado**, con 6 hallazgos | `reporta_a` vive en la línea, no en el insumo |
| D-48 | **P-01 cerrado**: la subfamilia del concepto se deriva, no se importa | Confirmado con OPUS 2025 — no exporta esa clasificación |
| D-49 | **El `OID` de OPUS no se adopta como `id`** | Identidad del archivo ajeno, no del negocio. Sirve solo como reconciliación de importación |
| D-50 | **Las partes de ingeniería se suman**, no se reemplazan | Verificado: los 4 archivos grandes no comparten nivel ni etapa |
| D-51 | **La reversión por destajo es el método de carga** | 84% con prototipo detectado. Los conceptos son recuperables aunque el archivo no los traiga |
| D-52 | **Auditar la diferencia NO es un módulo nuevo** | Mismo mecanismo de desviación (`CONOCIMIENTO.md` §13.6), aplicado antes de construir en vez de durante |
| D-53 | **Los montos se serializan como `string` en la API**, no como `number` | `number` en JS es IEEE 754. El `Decimal` se pierde al cruzar JSON y el float reentra al camino del dinero por el frontend |
| D-54 | **FastAPI es la única superficie pública.** PostgREST no se expone al frontend | Dos specs producen dos clientes con dos estilos. Y PostgREST no sirve para el árbol: `?parent_id=eq.5` devuelve un solo nivel (`CONOCIMIENTO.md` §3.1) |
| D-55 | **El cliente de API se genera, no se escribe** | Séptima aparición de «si se puede derivar, deja de ser entrada». Requiere D-53 decidido **antes** de la primera generación |
| D-56 | **El cerebro se organiza en cuatro capas**, por tiempo verbal: Mundo · Operación · Historia · Dirección | El corte ya existía en `INDICE.md` sin nombre. **No se renombra ningún archivo:** el nombre es lo que enruta a diario |
| D-57 | **El órgano es un atributo del encabezado, no el nombre del archivo** | Se gana la anatomía sin perder el enrutamiento. `corte:` y `verificado:` resuelven la caducidad sin archivo aparte |
| D-58 | **Cuarto agente: auditor.** Corre las invariantes | Estaban repartidas entre constructor y migrador — los mismos que produjeron lo que hay que comprobar |
| D-59 | **El skill se parte por módulo cuando los módulos existan**, y se compila desde el conocimiento | Partirlo antes multiplica los lugares donde el mismo hecho puede divergir |
| D-60 | **Un módulo nuevo no crea árbol propio**: es una lectura más del mismo | Verificado en seis módulos. El programa, el paramétrico y el ensamble reagrupan; **ninguno reasigna** |
| D-61 | **La coherencia del cerebro se audita con script, no a ojo**, y la corre el auditor | Cuatro desincronizaciones vivieron semanas sin que nadie las viera. No es un agente nuevo: es el mismo trabajo sobre otro material |
| D-62 | **Tres skills satélite, no cuatro.** `erp-diccionario` queda bloqueado | Su diseño se dio por incorporado al conocimiento y no lo está. **Un skill no puede introducir un hecho que el conocimiento no tenga** |
| D-63 | **El arquitecto evalúa skills y agentes al diseñar un módulo nuevo** | Si nadie lo pregunta, el módulo nace sin tooling o con tooling de más. Las dos fallan distinto |
| D-64 | **GRAVITY 2.0 orquesta: entrega plan de ruta, no ejecuta a los demás** | Los subagentes no se lanzan entre sí. Y aunque pudieran: **una cadena que se ejecuta sola no tiene dónde rechazar** |
| D-65 | **Todos los agentes cierran con el mismo bloque de traspaso**, con `EVIDENCIA` obligatoria | Un reporte sin evidencia sólo se acepta o rechaza por confianza — mismo defecto que la propuesta sin evidencia |
| D-66 | **El orquestador interno nunca aprueba sus propias propuestas** | Un router que aprueba convierte cuatro detectores en cuatro autores sin registro de quién decidió |
| D-67 | **El interno se llama `gravity-obra`**; quien opera le dice «Gravity» | Misma marca, identificador único. Nunca conviven con el externo |
| D-68 | **Dos perfiles de despliegue, no ruteo por consulta**: local con Ollama, red con Groq | Se decide al instalar. Si algún día se mezclan, se diseña entonces |
| D-69 | **El agente le pregunta al motor, no a la base** | Cubre la frontera de datos —sale el resultado de una operación, no el registro— y de paso **el modelo no puede equivocarse sumando: nunca ve los sumandos** |
| D-70 | **La proyección se permite con los supuestos a la vista.** Nunca el número solo | Una estimación presentada como dato es la propuesta sin evidencia, en versión respuesta |
| D-71 | **Respuesta, alerta y propuesta son una escalera**, no alternativas | Lo que decide el peldaño: si hay `objeto` y `propone`. Un faltante de cemento no tiene ninguno de los dos — es alerta |
| D-72 | **La detección determinista encuentra; el LLM redacta** | Mantiene la evidencia reproducible: quien revisa corre la misma consulta y obtiene el mismo hallazgo |
| D-73 | **El modelo se usa en el diccionario**, con descripciones y claves, nunca precios ni contratistas | Es el único lugar donde el parecido de texto *es* el hallazgo. Se amplía o recorta al llegar ahí |
| D-74 | **La confianza se deriva de la evidencia**, no la declara el modelo | Un modelo que declara su confianza declara lo que suena bien |
| D-75 | **El primer agente interno es Consulta** | Sus herramientas son las de los otros tres, y es el único que no propone: se puede equivocar sin consecuencia |
| D-76 | **Cuatro preguntas al declarar algo nuevo**: dónde vive, qué lo persiste, contra qué se comprueba, qué más cambia | La alerta se declaró sin tabla ni archivo y se habría perdido. El contrato de módulo no la cubría: no es un módulo |
| D-77 | **La memoria del agente interno es la tabla `PROPUESTA`**, no un almacén aparte | Guarda qué propuso, con qué evidencia, qué modelo y cómo se resolvió. Las métricas del lazo salen de ahí sin guardar nada más |
| D-78 | **Toda referencia `§N` lleva su archivo** | 17 no lo decían y se leían como si fueran del propio archivo. Es lo que hace segura la división de `CONOCIMIENTO.md` |
| D-79 | **`CONOCIMIENTO.md` se dividió en tres**: reglas del sistema, `CATALOGOS.md` y `IDEAS.md` | 3,941 líneas en un archivo se escapan cosas. Los catálogos son datos de origen y las ideas ni siquiera responden «es así» |
| D-80 | **Cada archivo numera desde 1**, y la referencia cruzada lleva su archivo | Numeración global = namespace compartido: agregar una sección en un archivo renumeraba los demás. Eso es el espagueti que se quería evitar |
| D-81 | **Una reescritura masiva se audita contra el original, línea por línea** | El remapeo de la división renumeró encabezados de 6 archivos que no debía tocar y rompió 17 referencias. El verificador no lo vio: daba «todo cuadra» con los archivos ya corrompidos |
| D-82 | **Una referencia se audita por tema, no sólo por que resuelva** | 16 apuntaban a una sección existente y equivocada. Se detectan comparando el vocabulario de la frase con el de la sección destino |
| D-83 | **Buscar la misma cifra afirmada dos veces con valores distintos** | Tercer método de auditoría. Encontró once/doce en las ingenierías de `ALAMO 18` — resultó ser evolución en el tiempo, no contradicción |
| D-84 | **Once y doce conviven a propósito: azotea se subió después** | Un número que cambia con el dato no es un error a corregir. `ESTADO.md` y `METODO.md` usan doce porque hablan de hoy; `CONOCIMIENTO.md` §11.8 usa once porque es la línea base de esa fecha |
| D-85 | **M-4 del paramétrico ya estaba resuelta** — el regenerado marca desvinculado | `PROPUESTA-CUATRO-MODULOS.md` no se releyó tras escribirse `CONOCIMIENTO.md` §6. Misma familia que el hallazgo de B-01 en la auditoría original |
| D-86 | **F-1: unidad base** — lo cargado se toma como definido; lo nuevo se sugiere y se valida al alta; la validación es la excepción, no el default | No generar cola de validación masiva al cargar |
| D-87 | **F-2: el mínimo de compra es por insumo**, no por proveedor | La arena siempre se compra por camión, sin importar a quién se le compre |
| D-88 | **F-3: el sobrante queda a nombre del lote** | Varias obras del mismo desarrollo lo comparten |
| D-89 | **M-1: la plantilla paramétrica flota; la instancia se congela al cotizar** | Mismo patrón que el compuesto (no congela a sus hijos) y que el presupuesto (diseño fluye, contratado congela) |
| D-90 | **P-1: la precedencia de CPM va en dos capas** — técnica entre conceptos (automática), programa entre actividades/sub-ensambles (manual) | Las actividades heredan la precedencia técnica de sus conceptos; no se recaptura |
| D-91 | **F-4: la conversión entre dimensiones se permite, factor manual guardado por concepto o insumo**, nunca global | El factor varía con el contexto (el aparejo cambia por muro); un factor global lo perdería |
| D-92 | **El factorizador queda con sus cuatro decisiones cerradas** | Listo para que el arquitecto lo diseñe formalmente en `CONOCIMIENTO.md` |
| D-93 | **El chequeo de contradicción de «decisiones» se acotó a la declaración exacta del total** | Disparó con «4 decisiones cerradas» del factorizador — no es el mismo hecho que el total de MEMORIA. Cuarto método de auditoría: probar el propio verificador contra su próximo uso real |
| D-94 | **El propio chequeo de conteos se corrigió dos veces contra su primer uso real** | Disparó con el número entre comillas de D-93, que narra un caso, no afirma un total. Se excluye texto citado entre «» de la comparación |
| D-95 | **M-2: la cohorte la declara el usuario la primera vez; después el sistema la deduce y la propone** | Mismo patrón que todo lo demás: detectar no necesita permiso, aplicar sí |
| D-96 | **La tasa paramétrica aprende de cualquier presupuesto, incluso en diseño** | Consecuencia asumida: un presupuesto en diseño no es evidencia de ejecución, **la dispersión pasa a ser la única señal de calidad del corpus** |
| D-97 | **M-3: la dispersión alta es diagnóstico del parámetro, no un aviso sobre el número** | Herrería 38%, cancelería 20%, carpintería 11%. Ninguna escala con el m²: varían por diseño, no por tamaño |
| D-98 | **Herrería, carpintería, cancelería y pérgolas llevan parámetro propio** — por unidad distinta, por matriz o por diseño | Confirma §5.7: el paramétrico falla por el parámetro equivocado, no por ser paramétrico |
| D-99 | **P-2: un calendario por obra, con excepciones por cuadrilla** | La lluvia para la obra entera; el sábado de un subcontratista sólo lo para a él. El global manda salvo excepción declarada |
| D-100 | **P-3: la ruta crítica se recalcula siempre, pero sólo avisa si cambia de actividades** | Correr fechas no es noticia. Un aviso diario deja de leerse, y entonces el que importa tampoco se lee |
| D-101 | **P-4: la fecha contratada no se mueve sola** — se congela como el precio | En lo contratado, precio y fecha son las dos obligaciones. Reprogramar **propone** la fecha nueva; alguien la acepta |
| D-102 | **CPM queda con sus cuatro decisiones cerradas** | Segundo módulo listo para diseño formal, después del factorizador |
| D-103 | **El tiempo de entrega del material nunca se definió** | Se citaba con referencia a una sección de desviaciones. Caso de libro del contrato de lo declarado: se usó un concepto sin darle casa |
| D-104 | **La salida del CPM son los recursos por fecha**, no la ruta crítica en sí | Material, mano de obra, subcontratos y egreso. La ruta crítica es el medio; esto es lo que se pide |
| D-105 | **Los recursos por fecha no son módulo nuevo: son la explosión leída en el tiempo** | Quinta aparición de «ningún módulo crea árbol propio» |
| D-106 | **No se crea un quinto agente interno para predicciones** | Proyectar ya es el tercer tipo de pregunta del agente de Consulta. Lo que faltaba no era un agente: eran los recursos por fecha que necesita |
| D-107 | **Un escenario de presupuesto cambia precio, alcance o programa — los tres tipos** | Uno queda vigente, el resto **se archiva, no se descarta** |
| D-108 | **«Escenario» tiene dos significados y se separan** | Escenario de presupuesto (B-39) y escenario de prueba del sistema (B-42). Entrada nueva en el glosario |
| D-109 | **El modelo asumía que una actividad es una barra continua, sin decirlo** | El muro que se detiene para colar la cadena lo rompe. Con tramos la proyección diaria es correcta y el hueco de cuadrilla se ve; sin ellos, ninguna de las dos. Abierto como P-5 / B-43 |
| D-110 | **Un ERP en uso es evidencia, no sólo origen de datos** | Trae reglas probadas contra la realidad, y también errores que nadie corrigió. Se identifica, valida, decide e implementa — nunca se copia. B-44 |
| D-111 | **C-1: el usuario elige la fuente de trazo; hoy PDF.** Los tres conviven con una fuente autoritativa por elemento y precedencia `IFC > DWG > PDF` | La medida cuelga del concepto en su ubicación, no del plano. Lo desplazado se conserva como evidencia, **no se suma**: mezclar sin esa regla da doble contabilidad con apariencia de rigor |
| D-112 | **C-2: se traza en cada obra, con plantilla e instancia** | La plantilla sirve para reusar y **para comparar entre obras**. Cuarta aparición de plantilla/instancia |
| D-113 | **C-4: el trazo anterior se conserva sólo si el volumen cambió** | Se retraza sobre la revisión nueva y se compara; si da igual se reemplaza, si difiere quedan las dos con su revisión |
| D-114 | **C-3: sólo roles autorizados trazan; si además se aprueba, se define por obra** al asignarla a un residente | **Primera regla de gobierno configurable por obra.** El modelo no tiene hoy dónde ponerla — B-45 |
| D-115 | **Las 16 decisiones de los cuatro módulos quedan cerradas** | Y al cerrarlas aparecieron tres piezas que no estaban: P-5, B-40 y B-45 |
| D-116 | **Un escenario no declarado reaparece como desviación falsa** | `ALAMO 18` se cargó con catálogo v1 y el cemento salió al 35%. Costó una investigación descubrir que no era error de datos. Mejor argumento para B-39, y salió de la obra |
| D-117 | **Comparar dos fuentes exige normalizar la profundidad de explosión antes de restar** | La arena 150× no es problema de unidades: en el prototipo vive dentro de compuestos y en la ingeniería aparece suelta. **El factorizador no lo resuelve** — B-47 |
| D-118 | **El flujo aguanta hasta comparar dos planes y se corta donde empieza la ejecución** | Prueba completa sobre `ALAMO 18`: 5 etapas pasan, 2 se rompen, 5 sin dato. Confirma P-38 como lo que más falta |
| D-119 | **Hay tres modos de fallo distintos y no se arreglan igual** | Falta el dato (ALAMO 18) · el dato está sucio (Zafiro) · el dato existe pero no es el que hace falta (siete prototipos) |
| D-120 | **La cohorte convierte un 23% inservible en un 2% utilizable** | Cimentación de una planta: Zafiro 1,039 · Rubí 1,012 · Jade 1,053. Evidencia más fuerte del paramétrico, sobre datos reales |
| D-121 | **La identificación por contenido atrapa una descripción que miente** | «Losa cimentación Zafiro Plus» era Diamante: tres etapas en 1.00-1.03 contra Diamante, ninguna cerca contra Zafiro Plus |
| D-122 | **La cohorte de cimentación NO es el número de plantas** | 5 de 7 comparten tasa con CV 2.8%, los Diamante de dos plantas incluidos. Zafiro Plus y Oro están 1.71× abajo: es otra población, no dispersión |
| D-123 | **Una partición que mejora el número no queda probada por mejorarlo** | La de plantas bajaba a 2% un subgrupo y dejaba el otro en 32%. **El residuo alto era la señal de que faltaba explicación, y se leyó como ruido** |
| D-124 | **La Δ $4.30 no es redondeo de importes: sería ±$0.11** | Es compatible con redondear el **PU** a centavos antes de multiplicar por cantidad. Predicción comprobable: ~$11 sobre los siete prototipos |
| D-125 | **M-1 confirmado: la plantilla paramétrica flota** | Y es la única coherente: **el presupuesto base se actualiza cada seis meses**, así que una plantilla congelada quedaría desfasada dos veces al año sin que nadie la toque |
| D-126 | **El presupuesto base se actualiza cada seis meses** | Dato de operación. Convierte el desfase de catálogo en algo **estructural, no excepcional** |
| D-127 | **Una obra en curso conserva la base que tenía al arrancar** | Aunque el presupuesto se actualice, y aunque la ingeniería se cargue por partes a lo largo de meses |
| D-128 | **La base se fija al arrancar la obra, no al cargar cada parte** | `ALAMO 18` cargó de abril a septiembre: seis meses, un ciclo entero. El archivo tardío se resuelve contra la base de inicio |
| D-129 | **Las invariantes se parten en estructurales y de valor** | Las estructurales no caducan (665 nodos cuadran, los % suman 100). Las de valor son línea base con fecha y se renuevan cada semestre |
| D-130 | **Recursos por fecha es parte del mismo módulo de programa**, no uno aparte | Confirmado. Y sus motivos son varios: material, mano de obra y subcontratos, no sólo el flujo de efectivo |
| D-131 | **Al acortar una duración se mueve el número de cuadrillas; si sólo queda una, el rendimiento requerido.** El precio del destajo nunca | Nada se sobrescribe: la divergencia se vuelve indicador para renegociar después |
| D-132 | **Cuarto rendimiento: el requerido** — el que haría falta para cumplir la fecha | Derivado como el calculado, nunca se captura, no pisa a los otros tres |
| D-133 | **D-90 se amplía: se programa por árbol de presupuesto o por paramétrico** | Conceptos, etapas o niveles en el árbol; actividades completas en paramétrico. No sólo sub-ensambles |
| D-134 | **El flujo de efectivo sirve pero no es lo principal** | Corrige lo que yo había asumido. Los motivos principales son material, mano de obra y subcontratos |
| D-135 | **Protocolo ante contradicción: nombrar, parar, preguntar, proponer, registrar** | Nunca elegir solo ni seguir «mientras tanto». Vive en `METODO.md` §3.5; los agentes y el skill lo referencian, no lo copian |
| D-136 | **Antes de tratar algo como contradicción, descartar tres cosas** | Mismo hecho en dos fechas · dos ámbitos distintos · dos bases distintas. Descarta la mitad de los casos |
| D-137 | **`CONOCIMIENTO.md` no se divide por módulo: recupera su índice interno** | El límite por módulo ya existe en `skills/`. Duplicarlo daría dos lugares donde vive «lo de importación». El índice se había perdido al dividir |
| D-138 | **Una referencia rota suele llevar su destino escrito al lado** | Las dos de `MODELO.md` decían «caso trabajado» y «prueba de ida y vuelta». No hizo falta adivinar: bastó buscar dónde vive lo que la propia frase nombra |
| D-139 | **Comparar dos fuentes: primero lo financiero cerrado en la matriz del concepto y dentro de cada fuente; después la naturaleza al insumo atómico** | Sin ese orden aparece la arena 150× y la varilla contada dos veces con signos opuestos |
| D-140 | **La profundidad es de la línea, no del reporte** | OPUS muestra agrupadores y básicos en el mismo análisis de PU. No hay reporte «de montos» y otro «de explosión»: hay renglones cerrados y abiertos |
| D-141 | **Un compuesto abierto no lleva importe: lo llevan sus hijos** | Si lo llevan los dos, el total se duplica en esa rama |
| D-142 | **El residuo de la reversión son cuatro casos con respuestas distintas** | Resuelto · ambiguo · clave inexistente · destajo de compuesto. Tratarlos igual hace que el método parezca peor de lo que es |
| D-143 | **`MOC-12010` no era residuo: era profundidad** | Es la MO de la zapata, vive en la matriz del compuesto. Con la búsqueda ampliada la reversión sube de 84% a 87% |
| D-144 | **Nunca se corrige una clave por proximidad** | Verificado en el catálogo: `MOS-02070` está a un dígito de «2079» y es un trabajo distinto que sí existe. Cuadraría en apariencia y sería falso |
| D-145 | **Una clave que no existe puede ser un cambio no autorizado** | Es la *ausencia de causa* de `CONOCIMIENTO.md` §11.7. Corregirla o darla de alta solo borra la evidencia de que alguien cambió algo sin declararlo |
| D-146 | **La unidad del presupuesto se normaliza al cargar y se guarda normalizada** | Catálogo cerrado de 17 y mapeo uno a uno verificable. Aquí normalizar **sí** es seguro, al revés que corregir una clave por proximidad |
| D-147 | **Una unidad desconocida se carga igual y se da de alta por validar** | Van a aparecer unidades nuevas y no pueden detener una carga. Distinto del **cambio** de unidad en un concepto existente, que sí lo detiene |
| D-148 | **Corrección: los catálogos estaban limpios, el sucio es el presupuesto** | `M²` no existe en ningún archivo — yo lo había inventado como ejemplo. El problema real es un vocabulario paralelo: `pza` contra `PZ`, `ser` contra `SERV` |
| D-149 | **B-51 ya estaba resuelto en `MODELO.md`**: `subfamilia_id` nullable, se clasifica a mano después, no bloquea la carga | Tercera vez que un pendiente tenía respuesta escrita sin releerse — después de M-4 y de B-01 |
| D-150 | **Hay dos 92%/8% distintos y no se relacionan** | Uno es la ingeniería de `ALAMO 18` cubriendo el presupuesto; el otro, la clasificación derivable del concepto. Coincidencia de cifra, no de hecho |
| D-151 | **Segunda prueba de que el prefijo no determina la familia** | 61% de los conceptos y **100% de los trabajos** tienen prefijos ausentes del catálogo de 35 familias, que es de insumos |
| D-152 | **El catálogo de 35 familias es de materiales**, no de conceptos ni trabajos | 76% de los materiales mapean por prefijo; de los trabajos, cero. El trabajo sí tiene familia, sólo que no derivada del prefijo |
| D-153 | **Nueve familias están duplicadas por acento** entre catálogo y uso | El catálogo sin acentuar, el uso acentuado. Sin normalizar, toda agrupación las cuenta dos veces |
| D-154 | **El catálogo de familias nunca cubrió la mano de obra** | Faltan 13, de las cuales 10 son de mano de obra y se usan a diario: peones, oficiales, cuadrillas, supervisores |
| D-155 | **En las familias, la forma acentuada es la canónica** | Es la del dato real; el catálogo es el que está mal. Las nueve colapsan uno a uno sin ambigüedad |
| D-156 | **La mano de obra clasifica por otro eje** — familia = tipo de trabajador, subfamilia = especialidad | Contra materiales, donde familia = tipo de material |
| D-157 | **La familia está declarada en cada catálogo, no se deriva del prefijo** | Materiales, trabajos y mano de obra traen columnas `Familia` y `Subfamilia` **sin un solo vacío**. Corrige lo que yo había concluido leyendo sólo las primeras columnas |
| D-158 | **`CATALOGO_DE_FAMILIAS` no es el maestro de familias** | Es la nomenclatura de prefijos de clave de materiales. Su nombre engaña y por eso se construyó encima una conclusión falsa |
| D-159 | **El concepto es el único catálogo sin columna de familia** | Por eso la suya se deriva del trabajo que usa, y por eso tiene un 8% sin cubrir. Los demás no derivan nada |
| D-160 | **Se puede cambiar familia y subfamilia, con bitácora**: anterior, nueva, quién y cuándo | La familia no entra en la huella, así que no versiona. Pero es el eje de agrupación del paramétrico: la tasa se marca **recalculable** |
| D-161 | **Tres tablas nuevas: normalización, homologación y grupos funcionales** | Hoy esas correcciones caen entre capas: no son CARGADO porque ya se cambiaron, ni REDISEÑO porque no son una de las seis operaciones. `CONOCIMIENTO.md` §16 |
| D-162 | **Homologar y agrupar se distinguen por si son la misma cosa** | Homologadas, una sustituye a la otra sin preguntar. Agrupadas, sustituir **es decisión de obra** y cambia el costo |
| D-163 | **La homologación es bidireccional; la normalización no** | La clave vuelve como entró porque es identidad y el sistema externo la usa para reconocer el renglón. La unidad no vuelve: la forma no es dato |
| D-164 | **La clave vieja deja de salir cuando el usuario lo autoriza, individual o total** | Según haya actualizado o no cada sistema externo |
| D-165 | **API y MCP conviven; no contradicen D-54** | La razón de D-54 era que dos specs producen dos clientes generados. **MCP no genera cliente: lo consume un modelo** |
| D-166 | **El MCP habla con la misma capa de servicio que la API, nunca con la base** | Implementado aparte serían dos sistemas que se parecen, con las reglas separándose en silencio |
| D-167 | **La capa de servicio va separada de la API desde hoy** | Es lo único caro después. Si la lógica vive en los endpoints, el día del MCP hay que sacarla de ahí |
| D-168 | **Orden: API primero, MCP después del agente** | Las herramientas se diseñan mirando qué pregunta el agente de verdad. Un MCP sin API es un agente sin sistema debajo |
| D-169 | **Con MCP, «el agente no escribe» pasa de regla a estructura** | Si no existe herramienta de escritura, no puede escribir aunque quiera |
| D-170 | **Nunca una herramienta genérica de consulta** | `ejecutar_consulta(sql)` tira la frontera de datos. Las herramientas son específicas y cada una lleva su límite adentro |
| D-171 | **Un solo servidor MCP para empezar; se parte por permisos** — consulta contra propuestas | Partirlo antes de saber qué herramientas existen es adivinar |
| D-172 | **Una instalación local necesita las dos superficies igual** | El ERP completo vive ahí y la interfaz también. No es «MCP en local, API en red»: las dos existen y **el MCP se puede apagar** |
| D-173 | **El tiempo de entrega vive en la familia, con excepción por insumo** | 18 valores cubren 387 materiales; la excepción afina sólo lo que tarda distinto. Misma forma que el calendario: uno general, excepciones donde hacen falta |
| D-174 | **Cada valor de tiempo de entrega declara su base: naturales o hábiles** | Restarlos contra el calendario da fechas distintas. Sin la marca, la fórmula de fecha de pedido da dos resultados |
| D-175 | **No hay catálogo de proveedores, así que el tiempo de entrega no puede colgar de ahí** | Sería lo más exacto y no se puede. Y los días no laborables del proveedor no se modelan ni se inventan |
| D-176 | **Tercera forma de obtener la duración: preestablecida por nivel** | Para lo que se contrata terminado y no tiene rendimiento del cual derivarla |
| D-177 | **El disparador de la fecha puede ser contractual: anticipo o junta de arranque** | Dirección nueva entre programa y contratos. Hasta aquí el programa proponía y el contrato congelaba; **aquí el contrato arranca el reloj** |

## Implementación

Primeras decisiones de código, no solo de modelo. `MODELO.md` cierra pidiendo
exactamente esto: *"tipos de columna concretos, índices, y el motor de cálculo
como funciones sobre este schema... es la fase de implementación del
constructor."* Viven en `backend/core/`, probadas contra `CASO-TRABAJADO.md`.

| # | Decisión | Por qué |
|---|---|---|
| D-178 | **El motor de cálculo navega por `COMPOSICION`, no por `NODO.padre_id`** | El mismo insumo de catálogo (`ACR-00002`) aparece referenciado desde líneas distintas —bajo `EST-01053` directo y bajo la zapata `ZA1-000001`—, confirmando que la matriz vive en `COMPOSICION` (MODELO.md §1a: «de aquí sale el cálculo completo») |
| D-179 | **`precio_declarado` sirve igual para un insumo de catálogo que para un concepto en modo alzado** | Los dos casos significan lo mismo: el precio no se deriva de una matriz propia. `MODELO.md` no pide un campo aparte y no hace falta inventarlo |
| D-180 | **El importe de cada línea se redondea a centavos antes de sumarse al padre; la cantidad nunca se redondea** | Sin este redondeo por línea, la zapata da $1,135.47 en vez de $1,135.48 — confirma la hipótesis de D-124: el PU se redondea a centavos antes de multiplicar. Verificado contra los tres importes reales de `CASO-TRABAJADO.md` |
| D-181 | **`acumulado_hasta_aqui` (`COMPOSICION.base_porcentaje`) queda sin implementar, con error explícito** | Pertenece a las capas de sobrecosto (`MODELO.md` §6), que no tienen datos reales todavía. Mejor `NotImplementedError` que adivinar la regla |
| D-182 | **El motor de cálculo se escribe sin Django ni base concreta**: un puerto `RepositorioArbol` más un adaptador en memoria para las pruebas | erp-construccion.md §9: «ltree va detrás de un puerto de repositorio.» La capa de persistencia (Django, Postgres, migraciones) queda pendiente — es el siguiente paso, no este |
| D-183 | **`PENDIENTES-MEJORAS.md` no se resincroniza solo cuando otro archivo resuelve uno de sus temas** | P-12 y P-13 ya tenían respuesta —B-51/D-149 y D-41/`LENGUAJE.md`— sin reflejarse en su propio renglón. Cuarta vez que pasa, después de M-4, B-01 y B-51 |
| D-184 | **`%MO` se normaliza a esa forma exacta al cargar** — mayúsculas, sin paréntesis | Cierra P-05: que se queda como unidad ya estaba decidido (`MEMORIA.md` §2); faltaba solo la forma canónica entre las tres que trae OPUS. Mismo mecanismo que D-146 |
| D-185 | **`cantidad` se guarda como `NUMERIC` sin precisión ni escala fijas** | Cierra P-06: no hace falta una regla por tipo de unidad. Se guarda lo que llegó, consistente con erp-construccion.md §9 y con D-180 (la cantidad nunca se redondea) |
| D-186 | **La moneda extranjera (`Costo base M. E.`) no se modela hoy, pero no se descarta** | Cierra M-13: cero en los 387 materiales, sin evidencia de uso. Distinto del `OID` de OPUS —que no vuelve nunca—: si en algún momento hace falta convertir a moneda extranjera, ahí se modela. Anotado en `MODELO.md` §6 |

## Modelo — enmiendas post-aprobación

Revisadas y aprobadas con el usuario el 2026-09-15, no en la revisión original del
modelo (2026-09-10). `MODELO.md` §6, hallazgos 7 a 9.

| # | Decisión | Por qué |
|---|---|---|
| D-187 | **La frontera `Flete`/`Acarreo` es el límite de la obra, no la dirección** | `Flete` cruza —de fuera hacia adentro, o de adentro hacia afuera—; `Acarreo` se queda dentro. Explica por qué `Acarreo` aparecía sin renglones: el transporte, cruce el límite en cualquier dirección, se registra como `Flete`. Cierra P-02 y P-03 |
| D-188 | **Las clases de `Trabajos` no son una lista cerrada** | Hoy `Destajo`, `Acarreo` y `Subcontrato`; pueden crecer —`Contrato`, `Permuta`, `Renta`—. Se modela `CLASE_TRABAJO` como tabla abierta, no `ENUM` de Postgres, que es caro de ampliar |
| D-189 | **Nuevo campo `revisar` (boolean) en `NODO`** | Insumo apartado sin clasificar bien, en vez de abusar de una categoría —el caso de `Tablas` y los materiales de prueba hidráulica marcados como `Flete`—. También sirve como bandera al revisar insumos para un cambio masivo. Cierra P-04 |
| D-190 | **Un presupuesto incompleto por partes se carga igual, nunca bloquea, y avisa con alerta no bloqueante** | D-30 (registrar nunca se bloquea) y D-71 (la escalera de alerta). Cierra P-25 en su parte de política |
| D-191 | **Nueva tabla `ESTADO_CARGA`, por nodo estructural** | `estado` incompleto/completo y `porcentaje_cargado` como caché con fecha, recalculado cada vez que entra una parte nueva. Mismo patrón que `ESTADO_CONGELAMIENTO` (D-25). Cierra P-25 en su parte de mecanismo |
| D-192 | **Nueva tabla `ALERTA`, peldaño de abajo de `PROPUESTA`** | Cierra B-32: la alerta no tenía dónde vivir y se perdía al cerrar la sesión que la detectaba. `veces_vista` contesta si algo ya salió antes, que es cuando deja de ser aviso |
| D-193 | **`diferencia_sin_causa` (P-29) e `identidad_dudosa` (P-30) nunca autocorrigen** | La identidad dudosa se calcula como razón entre el total cargado y el total del prototipo declarado, umbral 20% por defecto y parámetro, no número fijo. Dos métodos independientes —contenido y cantidad— que coinciden se validan mutuamente (`METODO.md` §1.4); no hace falta un tercer criterio |
| D-194 | **M-15/M-16 confirmados resueltos por `EQUIVALENCIA`** | La tabla ya estaba aprobada en `MODELO.md` §4 desde el 10 de septiembre, con `tipo=duplicado_exacto` cubriendo exactamente este caso. Sin cambios nuevos |
| D-195 | **P-23 confirmado resuelto** | El CPM tiene sus cuatro decisiones cerradas (D-90, D-99 a D-102, `PROPUESTA-CUATRO-MODULOS.md`). Lo único abierto de ese módulo es P-5 (la actividad interrumpida/tramos), que ya tiene su propio renglón |
| D-196 | **`ESCALABILIDAD.md` §10 corregido: el auditor no «falta»** | `agentes/auditor-erp.md` ya existe desde D-58. Quinta vez que un archivo queda sin sincronizar con una resolución ya escrita en otro |
| D-197 | **`diferencia_sin_causa` e `identidad_dudosa` viven bajo el detector `Desviación`**, no un quinto detector | Mismo mecanismo (D-52): comparan algo cargado contra una referencia declarada. Se separan solo si en la práctica necesitan herramientas distintas |
| D-198 | **B-31 (Agente de Consulta) ya no depende de B-01** | El modelo está aprobado. Sigue en fase 2 por D-06 —el asistente de obra se aplaza—, no por falta de esquema |
| D-199 | **Séptima idea del modelo: sustitución de insumo dentro de una matriz** | `IDEAS.md` §7. Ninguna de las seis operaciones de rediseño la cubre — clonación duplica el insumo entero, no dice cómo se usa dentro de un concepto que ya lo tenía. Necesita ser operación formal, no edición suelta, para seguir siendo reproducible |
| D-200 | **B-19 (cuantificador gráfico) confirmado resuelto** | Sus cuatro decisiones (C-1 a C-4) ya estaban en D-111 a D-114 desde antes de esta sesión, sin sincronizar en `PENDIENTES-MEJORAS.md`. Sexta vez que pasa este patrón |
| D-201 | **Nuevas tablas `TRAZO` y `ENLACE_CUANTIFICACION`** (`MODELO.md` §1b) | Conectan directo con `NODO.modo_cantidad = medida`, que existía desde la primera versión del modelo sin ningún mecanismo que lo alimentara |
| D-202 | **La vigencia por precedencia de fuente (`IFC > DWG > PDF`) vive en `ENLACE_CUANTIFICACION`, no en `TRAZO`** | El mismo trazo puede alimentar nodos distintos con vigencia independiente entre sí — la vigencia es de la relación trazo-nodo, no del trazo en sí |
| D-203 | **Un agente interno que cuantifique solo queda como aspiración, no como diseño** | `IDEAS.md` §2. Depende de que el cuantificador exista primero, y es una capacidad geométrica —interpretar un plano— distinta a la de los detectores actuales de `gravity-obra.md`, que leen texto y números |
| D-204 | **R-1: cinco roles de obra** — Residente, Supervisor, Costos, Cotizador, Control | Borrador de P-21, aprobado con el usuario. Queda pendiente cerrar el módulo completo |
| D-205 | **R-2: el rol es una combinación de funciones atómicas, no un bloque cerrado** | Permite variar una asignación sin tocar el catálogo de funciones — mismo principio que separar `categoria` de `clase` en D-187/D-188 |
| D-206 | **R-3: catorce funciones mínimas para el menú de herramientas** — `trazar`, `aprobar_trazo`, `registrar_avance`, `comprometer_gasto`, `capturar_causa_desviacion`, `revisar_patrones_desviacion`, `aprobar_version_concepto`, `pactar_precio_contratista`, `aplicar_descuento`, `autorizar_orden_cambio`, `aprobar_propuesta`, `resolver_alerta`, `clasificar_manualmente`, `correr_invariantes` | Ninguna inventada: ya estaban implícitas en D-30, D-114, `CONOCIMIENTO.md` §2.2, `CONOCIMIENTO.md` §13.2, `CONOCIMIENTO.md` §13.4, `CONOCIMIENTO.md` §13.6, D-32/D-44, D-192, P-01 e `INVARIANTES.md` §8. Faltan dos preguntas antes de cerrar P-21: tope por monto en `comprometer_gasto`, y si los roles son disjuntos en funciones |
| D-207 | **El cuantificador y el paramétrico comparten la misma fuente de cantidad, sin mecanismo nuevo** | Si el cuantificador encuentra algo que no existe en el árbol, crea concepto o nivel (`MODELO.md` §1b) y dispara versión nueva (`CONOCIMIENTO.md` §2.2) — las dos piezas ya existían, nadie las había conectado en un mismo flujo |
| D-208 | **`heredada` confirmado: un paramétrico nace con las cantidades de su presupuesto de referencia**, no las mide | Cierra la duda sobre un valor de `modo_cantidad` que estaba desde la primera versión del modelo sin caso escrito |
| D-209 | **Nuevo valor `cargada` en `modo_cantidad`** — la cantidad viene de una ingeniería ya importada, distinta de `heredada` (copiada al crear el paramétrico) y de `medida` (trazada por el cuantificador) | `CONOCIMIENTO.md` §11.9, reversión por destajo. `cargada` y `medida` que coinciden se validan mutuamente (`METODO.md` §1.4) — mismo principio que `identidad_dudosa` (D-193). `MODELO.md` §1, hallazgo 12 |
| D-210 | **Inventario de dieciocho funciones para el cuantificador**, básicas y especializadas, solo enlistadas en `IDEAS.md` §2 — ninguna diseñada todavía | Volumen y peso son las más urgentes: `M3` y `KG` ya son unidades canónicas, y el concreto de `CASO-TRABAJADO.md` se mide en `M3` |
| D-211 | **El inventario crece a 29 y se reorganiza en ocho tipos de herramienta** — escalas y mediciones, limpieza de planos, primitivas, medidas directas, cruce de capas, agrupación, relación espacial, especializadas de dominio | El usuario aportó funciones reales de PostGIS (`ST_MakeValid`, `ST_SnapToGrid`, `ST_SimplifyPreserveTopology`, `ST_Intersection`, `ST_Difference`, `ST_Buffer`, `ST_Union`, `ST_Centroid`, `ST_DWithin`, `ST_Touches`) que formalizan varias de las especializadas ya anotadas. Sigue siendo inventario, no schema — `IDEAS.md` §2 |
| D-212 | **Media lista con nombre real de PostGIS es evidencia fuerte a favor de un tipo espacial de Postgres para la geometría** | Responde en parte lo que `MODELO.md` §1b deja abierto a propósito. No se cierra solo con esto: es infraestructura —la extensión PostGIS tiene que estar habilitada donde corra la base—, y esa decisión la confirma el usuario, no queda implícita en una lista |
| D-213 | **Un nodo puede tener muchos enlaces vigentes a la vez, uno por instancia física; `vigente=falso` compite dentro de la misma instancia, no entre instancias distintas** | Aclara `MODELO.md` §1b: «una sola cantidad vigente» no era un tope de un enlace por nodo. Confirmado con el usuario sobre el caso de trabes repetidas dentro de una losa nervada |
| D-214 | **Muchas instancias repetidas del mismo elemento (cuarenta trabes) no son mecanismo nuevo**: cada una es su propio `TRAZO`, y la agregación a uno o a varios nodos la decide el árbol del presupuesto, no el cuantificador | Mismo principio que D-60. Descarta que hiciera falta "un generador de clones" o un cuantificador distinto para el caso de elementos repetidos |
| D-215 | **Dos campos nuevos para la fórmula personalizada**: `COMPOSICION.formula_personalizada` (si no es null, ignora `cantidad` y `tipo_cantidad`) y `NODO.variables` (JSONB, valores sueltos que no ameritan nodo propio) | Resuelve la «Variable del Usuario» y la puerta de escape que propuso el usuario. Ninguno de los dos vive en `ENLACE_CUANTIFICACION`: mezclaría costo con geometría pura (D-182). `MODELO.md` §1a, hallazgo 13 |
| D-216 | **Nodo hijo propio vs. `NODO.variables` se elige por concepto o compuesto, no con una regla global** | Mismo estatus que la elección entre `medida` y `estimada` (D-209). El usuario lo pidió explícito: «puede ser una o otra dependiendo la necesidad» |
| D-217 | **"Rendimiento de matriz" es alias de `COMPOSICION.cantidad`, no una cantidad nueva por categoría** | Evita dividir en `rendimiento_material`, `rendimiento_mano_obra`, etc. — un solo campo ya sirve a las seis categorías, mismo principio que evitó separar `base_porcentaje` por tipo. Cross-referenciado en `GLOSARIO-DOMINIO.md`, ambigüedad «Cantidad», para no chocar con el rendimiento de cuadrilla |
| D-218 | **PostGIS confirmado como motor de geometría pura — Decisión 1 de 3** | El usuario lo confirmó con sus propias palabras: «PostGIS solo se encarga de guardar el vector y entregar la métrica limpia... no mezcles lógica de costos dentro de las funciones espaciales». Cierra D-212. Quedan Decisión 2 (GeoJSON, transporte API↔frontend) y Decisión 3 (WKT, captura rápida) |
| D-219 | **GeoJSON confirmado como Decisión 2 de 3 — transporte de geometría entre API y frontend** | PostGIS lo exporta/importa nativo (`ST_AsGeoJSON`/`ST_GeomFromGeoJSON`), sin serialización a mano. Cada `Feature.properties` lleva `trazo_id`/`nodo_id` para el resaltado bidireccional tipo Navisworks que buscaba el usuario. `MODELO.md` §1b |
| D-220 | **GeoJSON es transporte, no almacenamiento; y usa coordenadas de plano, no geográficas** | `TRAZO.geometria` sigue en el tipo nativo de PostGIS —conserva el índice espacial—, GeoJSON se genera solo al leer. `ENLACE_CUANTIFICACION` sigue siendo la fuente de verdad; `properties.nodo_id` es copia de lectura, no un lugar nuevo donde ese dato pueda divergir. Coordenadas locales al plano: desviación deliberada de RFC 7946, no error a corregir |
| D-221 | **WKT confirmado como Decisión 3 de 3 — captura rápida de una geometría nueva** | `ST_GeomFromText` la convierte a geometría nativa en un solo paso, mismo principio que `ST_GeomFromGeoJSON` en la Decisión 2 pero para el momento de captura, no de transporte masivo. Resuelve el par que buscaba el usuario: WKT como PlanSwift, GeoJSON como Navisworks. `MODELO.md` §1b |
| D-222 | **Cierran las tres decisiones de geometría del cuantificador**: PostGIS almacena y calcula (D-218), GeoJSON transporta varios trazos con su enlace al árbol (D-219/D-220), WKT captura un trazo nuevo sin enlace todavía (D-221) | Ninguno es un tercer almacenamiento paralelo: WKT y GeoJSON son formato de entrada/salida, la fuente de verdad sigue siendo `TRAZO`/`ENLACE_CUANTIFICACION` en PostGIS |
| D-223 | **R-2 confirmado explícito: `ROL_FUNCION` es muchos-a-muchos, ninguna función atómica pertenece a un solo rol** | Consistente con «combinación, no bloque cerrado» (D-205) y el patrón «nada reasigna» repetido cinco veces (`ESTADO.md`) |
| D-224 | **`comprometer_gasto` no lleva tope por monto — es binaria** | Si hace falta controlar el gasto en subcontratos, la vía no es un límite por rol: es modelarlos como matriz (`COMPOSICION`), donde el control ya es por línea |
| D-225 | **P-21 cierra: roles y permisos completo** — R-1 a R-3 (D-204 a D-206) más D-223/D-224 | `ROL`, `FUNCION_ATOMICA`, `ROL_FUNCION` en `MODELO.md` §5b, hallazgo 14 |
| D-226 | **`PRECIO_HISTORICO` por insumo, independiente de `VERSION_CONCEPTO`** — `fuente` enum `catalogo` (auto-versiona) · `ingenieria` (requiere validación) | Cierra P-07/P-08. `almacen` y `estimacion` quedan pendientes de P-19/P-18, no se agregan hoy. `MODELO.md` §4a, hallazgo 15 |
| D-227 | **`VERSION_CONCEPTO` gana `pu`, congelado al crearse; segundo disparador de versión: pasar a `contratado`**, además del cambio de huella (§2.2) | Fija el PU exactamente al contratar, sin esperar a que cambie la receta |
| D-228 | **Precio de insumo y versión de concepto son independientes — excepto trabajo y subcontrato**, donde un cambio de precio dispara directo validar o descartar la versión | Su precio nace de una negociación puntual, no de un mercado que fluctúa |
| D-229 | **`TABULADOR_CONTRATISTA`, tabla separada, nunca toca el PU** — cierra la cita rota de `CONOCIMIENTO.md` §13.2 a un `M-12` inexistente | El PU es la referencia fija; lo pactado se compara contra él, nunca lo reemplaza |
| D-230 | **Dos huecos nuevos quedan anotados, sin diseñar**: catálogo de contratistas (P-39, mismo hueco que D-175 con proveedores) y marcador de presupuesto-base/plantilla en `PRESUPUESTO` (P-40) | No se inventan hoy |

---

# 2. Descartado

**Ideas razonables que ya se evaluaron y se rechazaron.** No volver a proponerlas
sin argumento nuevo.

| Se propuso | Se descartó porque |
|---|---|
| **`%MO` como campo `tipo_cantidad`** | Se queda como **unidad**. La unidad ya dice cuál es la base. *(Sigue anotado como P-05 por si cambia el criterio)* |
| **Renombrar el prefijo `AUX-`** | La clave nunca se reescribe, ni antes de migrar. La vía es **clonar y sustituir** |
| **MPTT o treebeard** | Su path cambia al mover el nodo: es posición, no identidad. Dos mecanismos de árbol compitiendo se desincronizan |
| **Ampliar el WBS a 3 dígitos por segmento** | El ERP externo **no lo admite**. El remedio es reagrupar el árbol, con alerta a los 90 hermanos |
| **Invertir familia y subfamilia en mano de obra** | Tocaría los 97 registros y rompe los reportes existentes |
| **Dar familia a las cuadrillas según el oficial que las encabeza** | Una cuadrilla no tiene rango único: tiene un oficial *y* ayudantes. Asignarle el del líder es arbitrario |
| **Clasificar las cuadrillas por área** | El área ya está en la subfamilia. Se resolvió con una **referencia a frentes**, informativa |
| **Que la base de datos sea «dueña del árbol»** | Matizado: `ltree` va detrás de un puerto. El recorrido es infraestructura; **la regla de qué suma a qué es dominio** |
| **Escribir `referencias/modelo.md` ahora** | Sería adelantar decisiones abiertas y quitarle el trabajo al arquitecto. Nace cuando él lo proponga y se apruebe |
| **Un cuantificador tipado** (de PU, paramétrico o alzado) | El modo ya está en el nodo receptor. Tiparlo también duplicaría la distinción |
| **Tolerancias de comparación al importar** | Aún no se establecen cálculos. Queda el hecho observado, sin regla |
| **Corregir a mano los catálogos de la generación anterior** | Se volvieron salida generada: se corrige el generador, no el archivo. Su valor es la estructura, como contrato de exportación |

---

# 3. Corregido

**Cosas que se afirmaron mal y se corrigieron.** Están aquí porque el conocimiento
tiene la versión buena pero no el aviso.

| Se dijo | Es | Cómo se detectó |
|---|---|---|
| La trabe es un **auxiliar** porque mezcla acero, concreto y mano de obra | Es un **material compuesto**: `Tipo = Material` en las 79 | El prefijo `AUX-` engañó |
| Un **compuesto solo admite insumos de su categoría** | Admite **cualquiera**. Verificado: hay fletes y un contrato dentro de compuestos de material | Corrección del usuario, luego comprobada |
| **La obra corrige al catálogo** | La obra **informa**; alguien decide. Corregir por un mal proceso institucionaliza el error | Corrección del usuario |
| El **reporte por recurso debe explotar** el árbol | Se **detiene en el compuesto**. La explosión profunda es otra lectura, para compra y programa | Corrección del usuario |
| La **categoría no se cruza editando** | **Sí se cambia**: la arena pasa de Material a Flete. Lo que no se cruza es insumo ↔ concepto | Corrección del usuario |
| **Zafiro Plus tiene 4 subcapítulos** | Tiene 15. El «4» era Planta Alta apareciendo en 4 prototipos | Error de lectura propio |
| La primera carga marcará **deriva masiva** | **Cero deriva**: los 467 conceptos cuadran. OPUS recalcula | Verificado contra los datos |
| Conviene **renombrar** el prefijo antes de migrar | No se renombra: **se clona** | Corrección del usuario |
| Los cinco vocabularios **hay que pedirlos** a OPUS 2025 | **Cuatro se derivan** de los datos ya cargados | Al intentar derivarlos salieron completos |
| Se extrajo el prototipo filtrando por `Ingenieria ERP` | **Faltaban 11 filas** y el total salía $34,946 corto. Por posición cuadra exacto | Al validar el artefacto contra el total declarado |
| `Ingenieria ERP` **se genera al exportar** | **No se puede**: la regla no es deducible. A veces el concepto recibe segmento y a veces no | La prueba de ida y vuelta |
| Los conceptos **llevan el código de su contenedor** | Solo a veces. Bajo `ECO-00006` reciben segmento propio | Igual |
| A etapas le **faltan** tres claves | No faltaban: el catálogo viejo estaba atrasado. Derivadas dan **52** | Igual |

---

# 4. Cambios de premisa

Cosas que cambiaron el marco, no un detalle.

| Fecha | Cambio |
|---|---|
| 2026-09-09 | **El árbol de ingeniería sale del alcance.** Se usará para otra cosa. Todos sus análisis se retiraron |
| 2026-09-09 | **Hay dos generaciones de export.** Los primeros 10 catálogos alimentaban a **otros ERP**; la parte 1 del conocimiento es **OPUS 2025** |
| 2026-09-09 | **El FSR es contexto, no se carga.** El cálculo existe en el catálogo pero queda fuera |
| 2026-09-10 | **El conocimiento pasa de documentar OPUS a ser un idioma.** Va a unificar los demás ERP, no solo describir uno |
| 2026-09-10 | Se separan **LENGUAJE** y **MEMORIA** del conocimiento |
| 2026-09-10 | El **artefacto se rehace** con datos verificados: cuadra en $1,842,430.31 contra $1,842,426.01 declarado |
| 2026-09-10 | **Se dibujan los flujos entre sistemas** (`CONOCIMIENTO.md` §11). OPUS es fuente y nunca destino; el ERP externo es **destino y fuente** a la vez | 

---

# 5. Patrones que aparecieron solos

No se diseñaron: se repitieron hasta hacerse evidentes.

### La regla de la dependencia — cuatro veces

> **Mientras nada dependa de un dato, se corrige o se borra. En cuanto algo depende,
> se agrega encima.**

Apareció en el catálogo al contratar, la unidad del concepto, el precio pactado y la
clave del insumo. **Es el principio de fondo del sistema**, y encabeza el skill.

### Nada reasigna — tres veces

El programa reagrupa, el paramétrico reagrupa, el ensamble reagrupa. **Ninguno
reasigna.** Y resultó ser también lo que desacopla técnicamente al módulo de
programa del motor de cálculo.

### Plantilla e instancia — cuatro veces

APU, ensamble, contrato y —probablemente— el trazo del cuantificador. La misma
forma en cuatro niveles distintos.

### El indicador *declarado menos calculado* — tres usos

Fusión, extracción y precio alzado. **Un solo mecanismo, tres situaciones.**

### Hallazgos que solo aparecieron al construir

No salieron de leer los catálogos, sino de hacer algo con ellos:

| Hallazgo | Cómo apareció |
|---|---|
| **Cantidades negativas** en 58 líneas | Al escribir el caso trabajado |
| `Ingenieria ERP` **no es generable** | Al ejecutar la prueba de ida y vuelta |
| El filtro por `Ingenieria ERP` **pierde 11 filas** | Al validar el artefacto contra el total declarado |
| Las etapas son **52, no 50** | Al derivar el vocabulario en vez de leer el catálogo |
| El factor **1.085** entre rendimientos | Al cruzar el catálogo viejo con el vigente |
| El **`Costo` de las líneas `%MO`** es la base, no un precio | Al explotar las cuadrillas |

> **Leer un catálogo no basta. Hay que calcular con él y contrastar contra un total
> conocido.**

### El prefijo no es llave — tres catálogos

Conceptos, trabajos y materiales. Dejó de ser un caso y pasó a ser regla.
