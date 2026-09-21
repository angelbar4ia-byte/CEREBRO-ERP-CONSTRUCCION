# PROPUESTA — cuatro módulos

```
órgano:     —
capa:       IV — Dirección
pregunta:   ¿qué se propone construir?
tiempo:     vamos aquí
corte:      2026-09-21
verificado: ✅ 21 decisiones cerradas · pendiente diseño formal
```

> **Para revisar y decidir, no para construir todavía.**
>
> Cada bloque trae: qué resuelve, qué necesita, qué propongo, qué cuesta y **qué hay
> que decidir**. Nada de esto está en `CONOCIMIENTO.md` hasta que lo apruebes.
>
> 2026-09-10

---

## Por qué estos cuatro, y en este orden

Los cuatro se necesitan entre sí, y en una sola dirección:

```
FACTORIZADOR ──→ CUANTIFICADOR ──→ PARAMÉTRICO ──→ CPM
   unidades         cantidades        tasas         tiempo
```

- El **cuantificador** produce cantidades, y las produce en la unidad del trazo.
  Sin factorizador, cada conversión es manual.
- El **paramétrico** aprende de cantidades medidas. Sin cuantificador, aprende de
  cantidades capturadas — que es lo que hoy no se puede auditar.
- El **CPM** necesita duraciones, y la duración sale del volumen. Sin cantidades
  confiables, la ruta crítica es ficción ordenada.

> **El factorizador es el más chico y el que más desbloquea.** Empezaría por ahí.

---

# 1 · Factorizador de unidades

## Qué resuelve

Tres problemas que hoy están sueltos y son el mismo:

| Hoy | Con factorizador |
|---|---|
| Para tener cemento en kilos y en sacos hacen falta **dos claves** | Un insumo, dos presentaciones |
| No es práctico comprar **0.026 de un camión** de 14 m³ | El APU dice 0.026 m³; la compra redondea a 1 camión |
| Cambiar la unidad **rompe el rendimiento** sin avisar | La conversión se detecta y se propone |

## Qué propongo

**Una unidad base por insumo, y presentaciones que la referencian.**

```
Arena de río
  unidad_base    m³
  presentaciones
    camión 14 m³   factor 14    mínimo 1   indivisible
    m³             factor 1

APU dice        0.026 m³        ← consumo real, sin distorsión
Compra dice     1 camión        ← redondeo al alza obligatorio
Sobra           13.974 m³       ← inventario, no desperdicio
```

### Las conversiones se clasifican solas

| Conversión | Factor viene de | Quién decide |
|---|---|---|
| Saco → kg | el empaque | **Automático** |
| Camión → m³ | el transporte | **Automático** |
| m³ de arena → kg | densidad, varía con la humedad | Automático **con aviso** |
| Tabique pza → m² de muro | el aparejo | **Propuesta** |

> **La regla que el agente puede aplicar solo:** si la conversión se queda dentro de
> la misma dimensión física —masa a masa, volumen a volumen, pieza a pieza— es
> segura. Si cruza dimensiones o mete una propiedad variable, propone y espera.

## Qué gana

- **El catálogo se encoge.** Desaparecen las claves duplicadas por presentación.
- **Se acaba el riesgo de desincronizar precios** entre dos claves del mismo material.
- **Sobrante deja de ser desperdicio.** Comprar 14 y usar 8 deja 6 de inventario;
  hoy se ve como sobreconsumo.
- Habilita la comparación almacén contra explosión (`CONOCIMIENTO.md` §13.6) sin falsos positivos.

## Qué cuesta

- Tocar el catálogo de materiales: definir unidad base y presentaciones.
- **El rendimiento se mueve al cambiar la unidad.** Es razón, no cantidad: 30 m²/jor
  pasa a 1,500 pza/jor sin que nadie trabaje distinto.

## Qué hay que decidir

| # | Pregunta | Resuelta |
|---|---|---|
| ~~F-1~~ | ~~¿Quién define la unidad base?~~ | **Catálogo ya cargado: la unidad que trae es la definida, no se re-pregunta.** Insumo nuevo: el sistema sugiere y el usuario valida al alta. Sin unidad detectable: se sugiere y se marca sólo si es ambiguo — **no se genera cola de validación masiva al cargar** |
| ~~F-2~~ | ~~¿El mínimo de compra es por insumo o por proveedor?~~ | **Por insumo.** La arena siempre se compra por camión, sin importar el proveedor |
| ~~F-3~~ | ~~¿El sobrante a nombre de quién?~~ | **Del lote.** Varias obras del mismo desarrollo lo comparten |
| ~~F-4~~ | ~~¿Conversión entre dimensiones?~~ | **Se permite, con factor capturado a mano** — guardado **por concepto o insumo**, no global: `tabique pza → m²` depende del aparejo, que varía por muro, así que el factor vive donde varía |

**Las cuatro decididas. El factorizador queda listo para que el arquitecto lo diseñe
formalmente** — evaluando, por `ESCALABILIDAD.md` §2b, si necesita skill y agente
propios.

> **F-1 trae un límite explícito:** la validación es la excepción, no el paso por
> defecto. Mismo principio que `ESTADO.md`: el 92% de los conceptos ya se clasifica
> solo con el trabajo que usa; sólo lo genuinamente ambiguo pasa a revisión manual.

---

# 2 · Cuantificador gráfico

## Qué resuelve

**De dónde nace la cantidad.** Se estableció que es el único dato propio del
presupuesto, pero nunca de dónde sale. Hoy se captura y no se puede auditar.

## Qué propongo

**Trazo, medida y cantidad son tres cosas distintas.**

```
TRAZO      geometría sobre el plano       polígono · línea · punto
MEDIDA     lo que se deriva de él         área · perímetro · longitud · conteo
CANTIDAD   medida × factor → al concepto  área → piso  ·  perímetro → zoclo
```

> **Un solo trazo alimenta varios conceptos.** El polígono de una recámara da el
> área para el piso y el perímetro para el zoclo. Guardando solo la cantidad, habría
> que trazar la recámara tres veces.

### El árbol del cuantificador refleja el del presupuesto

No inventa estructura: **cuelga geometría de renglones que ya existen**. Si hace
falta algo que no existe, crea el concepto.

### El trazo queda ligado, no copiado

Corregir el trazo **actualiza la cantidad sola**. Y el trazo carga su evidencia:
qué plano, qué versión, qué capa, qué polígono.

> **Si el plano cambia**, las cantidades trazadas sobre el anterior quedan **marcadas
> para revisión**, no se recalculan solas.

### El cuantificador no se tipa

No hay «cuantificador de PU» ni «de alzado». El modo ya está en el nodo que recibe.
**Lo que se tipa es el enlace**: qué medida toma y con qué factor.

| El nodo receptor | Lo que la cantidad significa ahí |
|---|---|
| Por PU | Volumen de obra |
| Paramétrico | El divisor del ensamble |
| Alzado | La unidad del precio declarado |

**El mismo polígono alimenta los tres a la vez.**

## Qué cuesta

- Es el módulo **más caro de construir**: hay geometría, planos y versiones.
- Depende del factorizador para que el enlace medida → cantidad no sea manual.

## Qué hay que decidir

| # | Pregunta | Resuelta |
|---|---|---|
| ~~C-1~~ | ~~¿PDF, DWG o IFC?~~ | **El usuario decide; hoy PDF.** Los tres pueden convivir, con **una fuente autoritativa por elemento** y precedencia `IFC > DWG > PDF`. Lo desplazado **se conserva como evidencia, no se suma** |
| ~~C-2~~ | ~~¿El trazo se reutiliza?~~ | **Se traza en cada obra, con plantilla e instancia.** La plantilla existe para reusar y **para poder comparar entre obras** — cuarta aparición del patrón |
| ~~C-3~~ | ~~¿Quién traza y quién aprueba?~~ | **Sólo roles autorizados trazan. Si además hace falta aprobación, se define por obra**, al asignarla a un residente. Primera regla de gobierno configurable por obra — necesita dónde vivir (B-45) |
| ~~C-4~~ | ~~¿Histórico o reemplazo?~~ | **Se conserva sólo si el volumen cambió.** En la práctica: se retraza sobre la revisión nueva, se compara contra la anterior, y si da igual se reemplaza; si difiere, quedan las dos con su revisión |

### El riesgo de mezclar fuentes: pisamiento

Es real y hay que resolverlo antes de permitir las tres. **El mismo muro medido en PDF
y en DWG produce dos cantidades para una sola cosa.**

La regla que lo evita ya existe en el modelo: la medida no cuelga del plano, **cuelga
del concepto en su ubicación**. Un elemento tiene una sola cantidad vigente, con su
fuente declarada.

| | Qué pasa |
|---|---|
| Llega una medida más precisa | **Sustituye**, no suma. Precedencia `IFC > DWG > PDF` |
| La anterior | Queda como evidencia, con su fuente y fecha |
| Dos fuentes discrepan mucho | **Es propuesta con evidencia**, no corrección automática |

> Sin esa regla, mezclar fuentes no da más precisión: **da doble contabilidad con
> apariencia de rigor.**

> **El cuantificador tiene un segundo uso, para programar en vez de
> presupuestar** — con su propio techo y tolerancia: `§4`, "Dos cuantificadores".

---

# 3 · Paramétrico

> Ya está definido en `CONOCIMIENTO.md` §5. **Esto es solo lo que falta para
> construirlo.**

## Lo que ya está resuelto

Ensamble como mecanismo del APU un piso arriba · plantilla e instancia · la cantidad
es receta, no volumen · referencia al concepto y no al renglón · dos explosiones ·
divisor y cohorte · las cuatro pantallas.

## Lo que falta

### El corpus de aprendizaje

El paramétrico **aprende de cantidades medidas**. Hoy todas son capturadas.

> Sin cuantificador, un paramétrico construido sobre cantidades capturadas hereda
> sus errores **y les da apariencia de estadística.**

### La dispersión se guarda junto al valor

Ya está escrito, pero conviene subrayar el efecto medido:

```
Cimentación 1 planta      2% de dispersión    ← usable
Cimentación mezclada     23%                  ← engaña
Herrería                 38%                  ← es una adivinanza
```

**Un precio paramétrico sin su dispersión es un número disfrazado de certeza.**

### Qué hay que decidir

| # | Pregunta | Resuelta |
|---|---|---|
| ~~M-1~~ | ~~¿Se congela o flota?~~ | **La plantilla siempre flota** — es receta, no número guardado; coherente con que el compuesto tampoco congela a sus hijos. **La instancia se congela** al usarse para cotizar, mismo patrón que presupuesto: diseño fluye, contratado se congela |
| ~~M-2~~ | ~~¿Quién define la cohorte?~~ | **La primera vez la declara el usuario.** De ahí en adelante el sistema la deduce de los datos y la ofrece como propuesta. Mismo patrón que el resto: detecta solo, corrige con permiso |
| ~~M-nueva~~ | ~~¿De qué presupuestos aprende la tasa?~~ | **De cualquiera, incluso en diseño.** Con la consecuencia asumida: un presupuesto en diseño no es evidencia de ejecución, así que **la dispersión es la única señal de calidad del corpus** |
| ~~M-3~~ | ~~¿Qué pasa con dispersión alta?~~ | **La dispersión alta no se publica ni se bloquea: dice que el parámetro es el equivocado.** Herrería (38%), cancelería (20%), carpintería (11%) y pérgolas no escalan con el m² — **cada uno lleva parámetro propio**: unidad distinta, matriz o diseño. El sistema propone cambiar el divisor, no maquillar el número |
| ~~M-4~~ | ~~Al regenerar, ¿qué pasa con lo editado a mano?~~ | **Resuelta** — `CONOCIMIENTO.md` §6: se marca *desvinculado* y se muestra la divergencia |

---

# 4 · CPM — la ruta crítica

## Qué resuelve

Hoy el Gantt calcula **cuánto tarda cada actividad**. No dice **qué va antes que
qué**.

> Sin precedencias, la suma de duraciones es una lista. Y sin ruta crítica, **no se
> sabe qué retraso importa y cuál no.**

## Qué propongo

### Lo mínimo que hace falta

| Elemento | Para qué |
|---|---|
| **Precedencia** entre actividades | Qué debe terminar para que otra empiece |
| **Tipo de vínculo** | Fin-inicio · inicio-inicio · fin-fin |
| **Traslape o espera** | Días de adelanto o de holgura entre dos |
| **Calendario** | Días hábiles, lluvia, suspensiones |

Con eso salen solas: fechas tempranas y tardías, **holgura por actividad** y **la
ruta crítica**.

### De dónde salen las precedencias

Tres fuentes, y conviene no mezclarlas:

| Fuente | Ejemplo | Confianza |
|---|---|---|
| **Técnica** — no se puede al revés | Colar antes de descimbrar | Alta. Es física |
| **De recurso** — la misma cuadrilla no puede estar en dos lados | Un solo albañil, dos muros | Media. Cambia si contratas más |
| **De decisión** — así se quiso organizar | Empezar por la planta alta | Baja. Es preferencia |

> **La técnica se puede proponer sola**: si un concepto de descimbrado usa el mismo
> elemento que uno de colado, hay precedencia. Las otras dos las pone quien programa.

### La conexión que ya está a medias

El tiempo de entrega del material daría la fecha de pedido:

```
fecha de pedido = inicio de actividad − tiempo de entrega − holgura
```

**Ese inicio solo se conoce si hay precedencias** — eso lo resuelve este módulo. Y la
otra mitad ya está: **el tiempo de entrega vive en la familia con excepción por
insumo, y cada valor declara si es en días naturales o hábiles** (B-40 cerrado,
`CONOCIMIENTO.md` §15).

> Con eso, la fórmula es calculable en cuanto existan las precedencias.

### Tres formas de obtener la duración

```
1. el usuario asigna días                        tradicional
2. destajo con cuadrilla → rendimiento → días    calculada
3. duración preestablecida por nivel             para lo que se contrata terminado
```

La tercera es para las partidas que **no llevan ingeniería por naturaleza** —no se
despiezan, se compran o contratan armadas—. No hay rendimiento del cual derivar días,
así que la duración se declara.

### Cómo se arma el programa: manual o por carga

Dos orígenes, y dentro de cada uno el mismo reparto de roles:

| | Quién | Qué controla |
|---|---|---|
| **Manual, con diseño** | Control de obra | Marca o edita duración desde un presupuesto PU o paramétrico. Vincula actividades: sucesora, predecesora, interrupción |
| **Manual, sin diseño** | Residente | Captura fechas de inicio y fin concretas — la duración se calcula al revés que arriba (fecha menos fecha, no rendimiento). Al registrarse avance, reprograma solo |
| **Por carga, estructura** | Control de obra | Fija el vínculo entre actividades cargadas; puede modificar duración, inicio, fin, predecesor, sucesor e interrupciones |
| **Por carga, fechas** | Residente | Ajusta fechas sobre lo cargado — no toca estructura |

**El patrón se repite: Control de obra edita estructura; Residente edita fechas.**
Es la misma separación que ya existe entre roles (`MODELO.md` §5b) — aquí aparece su
primer caso concreto para el programa. Nombrar las funciones atómicas queda para
cuando el módulo se modele (`PENDIENTES-MEJORAS.md` B-73).

> **"Manual, sin diseño" agrega una cuarta forma de obtener la duración**, distinta
> de las tres de arriba: no se declara el número de días ni se deriva de
> rendimiento — se derivan las fechas dadas. Es el modo de una obra sin presupuesto
> formal todavía colgado del árbol.

### El disparador de la fecha puede ser contractual

En esas partidas el inicio no lo fija una precedencia técnica ni la disponibilidad de
una cuadrilla: **lo fija el anticipo o la junta de arranque.**

> Es una dirección nueva entre programa y contratos. Hasta aquí el programa proponía
> fechas y el contrato las congelaba; **aquí el contrato es lo que arranca el reloj.**

### La salida que justifica el módulo: recursos por fecha

Las precedencias y la ruta crítica son el medio. **Lo que hace útil al CPM es poder
preguntar qué se necesita y cuándo.**

```
actividad  →  tramos con fecha       (la da el CPM)
actividad  →  conceptos              (ya existe)
concepto   →  explosión de insumos   (ya existe)
─────────────────────────────────────────────────
           →  material · mano de obra · subcontratos, por fecha
```

### La actividad se interrumpe: no es una barra continua

El muro de tabique se detiene un día para colar la cadena de cerramiento, y sigue.
Es una sola actividad, un solo destajo, un solo responsable — **pero su consumo de
material tiene un hueco en medio**.

| Si la actividad es una barra continua | Si tiene tramos |
|---|---|
| El material se reparte parejo entre inicio y fin | Se reparte **por tramo** |
| El día de la cadena pide tabique que nadie va a usar | Pide cero tabique y sí acero |
| La cuadrilla figura ocupada todo el periodo | Queda **libre ese día**, y se puede ver |

> **Cuanto más fina la proyección, más pesa el hueco.** Por mes casi no se nota; por
> semana desplaza una compra; **por día, la lista de material del miércoles está
> simplemente mal.**

Y hay un segundo efecto, en la dirección contraria: **el hueco es capacidad
disponible.** Si la cuadrilla de tabique no trabaja ese día, o se le da otro frente o
se asume el paro. Hoy ninguna de las dos cosas se puede ver.

**La interrupción no es una excepción rara** — es la forma normal de construir un
muro: se levanta hasta el nivel de cadena, se cuela, se sigue. Pasa en losas,
aplanados y acabados igual.

> Lo que hay que decidir es **si el tramo es dato del programa o se deduce de la
> precedencia técnica** — el CPM ya sabe que la cadena va en medio, porque esa
> precedencia es física y se propone sola (P-1). **P-5.**

**No es un módulo nuevo: es la misma explosión leída a lo largo del tiempo.** Quinta
aparición de que ningún módulo crea árbol propio — cada uno es otra lectura del
mismo.

| Proyección | De dónde sale | Para qué |
|---|---|---|
| **Material por fecha** | Explosión de costo por semana | Programa de compras |
| **Mano de obra por fecha** | Explosión de contratación por cuadrilla | Cuánta gente y cuándo |
| **Subcontratos por fecha** | Sub-ensambles con su calendario | Cuándo contratar a cada uno |
| **Egreso por fecha** | Las tres juntas, valuadas | **Flujo de efectivo** |

> **El flujo de efectivo es la única de las cuatro que un director de obra pide sola,
> y no se puede construir sin las otras tres.**

Dos consecuencias que hay que asumir:

- **`B-40` deja de ser menor.** Sin tiempo de entrega, el material por fecha da la
  fecha de **consumo**, no la de **pedido**. Para comprar, la útil es la segunda.
- **La proyección cae bajo la regla de la proyección** (`gravity-obra.md` §3): sale
  con sus supuestos a la vista, nunca el número solo. Un flujo de efectivo presentado
  como dato es la forma más cara de esa confusión.

### El tope de cuadrillas, por oficio dentro del frente

Ya está anotado que la relación no es lineal. Con CPM se vuelve concreto: **acortar
la ruta crítica metiendo gente tiene un techo** — no por frente, sino por cuántas
cuadrillas del mismo oficio caben en la misma etapa sin estorbarse. **P-6**, abajo.

### Dos disparadores de reprogramar, y no son el mismo

Algo obliga a tocar el programa por dos caminos distintos:

| Disparador | Quién | Qué hace |
|---|---|---|
| **Control de cambio** | Costos o Control de obra — o se detecta al cargar | Altera el árbol de presupuesto (`CONOCIMIENTO.md` §13.4). Si cambia qué hay que construir, cambia cuándo |
| **Incidencia** | Residente, Supervisor o Control de obra, desde el campo | Afecta el programa con o sin tocar el árbol de costo |

**No son el mismo registro** — la evidencia es directa: un error de ejecución puede
cobrarse al contratista sin pagar el destajo de repararlo (no hay desviación de
costo que registrar), y el programa **igual se retrasa**. El costo se resolvió por
un lado; el tiempo se perdió por el otro, sin que uno dependa del otro. **P-8**,
abajo.

### La incidencia: tres formas de tocar el programa, no una

Comparte vocabulario de causa con `CONOCIMIENTO.md` §13.6 —cuatro de las nueve
causas son las mismas que ya pagan una desviación de costo—, pero el efecto sobre
el programa no es uniforme:

| Efecto | Cuándo | Mecanismo |
|---|---|---|
| **Pausa una actividad que ya existe** | Falta un insumo · una lluvia detiene un colado | Es un tramo (P-5) — si la causa es solo calendario (lluvia sobre la obra entera), ya lo cubre P-2 y no hace falta incidencia |
| **Crea o hace crecer una actividad** | El viento tira un muro (crece, excedente de catálogo) · el cliente pide algo fuera de catálogo (nueva) | Sí es incidencia — cambia qué hay que construir, no solo cuándo |
| **Se propone, no se ejecuta todavía** | Mejora de proyecto · algo necesario para ejecutar que nadie había visto | Incidencia que **propone** una actividad — mismo patrón que `PROPUESTA`: alguien la aprueba antes de que exista |

### Quién puede tocar una incidencia, en qué orden

**Quien la origina no se autoaprueba ni se autovalida** — salta ese paso y sigue con
el siguiente rol de la cadena. Lo único constante en los tres casos: **el
Supervisor siempre da seguimiento hasta que cierra.**

| Origina | Aprueba | Valida en sitio | Ejecuta |
|---|---|---|---|
| Residente | Supervisor | Control de obra | Residente |
| Supervisor | *(se salta)* | Control de obra | Residente |
| Control de obra | Supervisor | *(se salta)* | Residente |

### Cierre de frente: el primer trámite propio de Frente

Al 90% de avance de un frente —10% antes de cerrarlo—, el Residente solicita el
cierre, el Supervisor aprueba y Control de obra valida. Es el momento natural para
levantar una **incidencia de calidad**, con la misma cadena de arriba.

> **Frente estaba marcado como puramente informativo** (`CATALOGOS.md`: «no valida,
> no impide, no calcula»). Un trámite de cierre no lo contradice —no calcula nada,
> solo pregunta si ya se puede dar por terminado lo que vive ahí— pero es la primera
> vez que Frente carga un evento propio en vez de ser solo etiqueta para filtrar.

### Cómo se registra el avance

Dos formas de capturar, y una no reemplaza a la otra:

| | Cómo | Contra qué compara |
|---|---|---|
| **Número o porcentaje** | El Residente anota cantidad o % avanzado — la vía rápida, siempre disponible | Lo programado |
| **Trazo** | Opcional — un segundo trazo, "lo realmente construido", sobre el mismo plano | El trazo de programación (C-4, `§2`: mismo mecanismo — se compara, las dos versiones quedan) |

**Traza avance quien ya traza en general, menos Costos**: Control, Residente y
Supervisor — Costos participa en el trazo de presupuesto (`MODELO.md` §1b, B-45)
pero no en el de avance, que es de campo.

El Residente puede ver la brecha contra lo programado **y contra el presupuesto**;
si la brecha contra presupuesto importa, **solicita ajuste de cantidad a Control de
obra** — mismo patrón que pedir extender el techo de programación, abajo.

La alerta que nace de lo pagado (`CONOCIMIENTO.md` §13.7) sigue la misma regla:
**nunca corrige sola**, invita a revisar, y de ahí sale corregido, explicado con
una causa (`CONOCIMIENTO.md` §13.6) o sin explicar.

### Dos cuantificadores: uno fija presupuesto, el otro programa sobre él

No es el mismo trazo con otro nombre — son dos usos distintos:

| | Cuantificador de presupuesto (§2) | Cuantificador de programación |
|---|---|---|
| Para qué | Fija la cantidad de presupuesto | Fija la cantidad de una actividad del programa |
| Es el techo o se mide contra él | **Es el techo** — no se pretende superar | Se mide contra el techo, con tolerancia |
| Si se excede | No aplica | Hasta un umbral configurable (hoy 20%) sigue solo. Más de eso, se solicita extender a Control de obra |

**El umbral no es mecanismo nuevo** — reusa `ALERTA.parametro_usado`
(`MODELO.md` §5a), que ya trae `{"umbral_pct": 20}` como su propio ejemplo en el
modelo. Cruzar el umbral dispara la alerta; no crea la incidencia por sí sola.

### Cruzar el umbral no es lo mismo que una incidencia

Cuando Control revisa la alerta, decide una de dos: **es una incidencia real**
—y con eso la origina, misma cadena de aprobación de arriba— **o se descarta**
—fue un error del trazo original, no pasó nada en obra, se corrige el dato—.
**P-9**, abajo.

Validado contra siete escenarios de campo: seis caen en alguna de las nueve causas
de `CONOCIMIENTO.md` §13.6 (incluida la causa 6, "plano desactualizado" — un
cambio que nunca llegó a planos), y el séptimo —cuantificación mal trazada desde
el inicio— no es causa: es alerta descartada.

## Qué cuesta

- Es el módulo con **más aritmética** y el más fácil de implementar mal.
- Necesita duraciones confiables → necesita rendimiento → necesita la semilla, que
  ya existe.

## Qué hay que decidir

| # | Pregunta | Resuelta |
|---|---|---|
| ~~P-1~~ | ~~¿Entre actividades o entre conceptos?~~ | **Las dos, en capas.** Técnica: entre conceptos, automática (física). Programa: manual, sobre **el árbol de presupuesto —conceptos, etapas o niveles— o sobre el paramétrico —actividades completas—** (D-133). Se hereda la precedencia técnica, no se recaptura |
| ~~P-2~~ | ~~¿Cuántos calendarios?~~ | **Uno por obra, con excepciones por cuadrilla.** La lluvia para la obra entera; que un subcontratista no trabaje sábados sólo lo para a él. El global manda salvo excepción declarada |
| ~~P-3~~ | ~~¿Cuándo se recalcula?~~ | **Siempre se recalcula; sólo avisa si cambia la ruta**, no cuando únicamente se corren fechas. Un aviso diario deja de leerse |
| ~~P-4~~ | ~~¿Las fechas contratadas se mueven?~~ | **Se congelan: una fecha contratada no se mueve sola.** Misma regla que el precio — en lo contratado, el cambio pasa por control de cambio |
| ~~P-5~~ | ~~¿La actividad puede partirse en tramos?~~ | **Depende de la fuente de la pausa — misma clasificación que ya usa P-1.** Si la fuerza una precedencia técnica (la cadena debe colarse antes de seguir), el tramo se deduce solo, igual que cualquier precedencia técnica (es física). Si la fuerza un recurso o una decisión (la cuadrilla se fue a otro frente, el clima), se captura a mano — no hay de dónde deducirlo. El reparto de material entre tramos se calcula por default y queda como campo editable — cuarta aparición de «declarado menos calculado» (`MEMORIA.md` D-259) |
| ~~P-6~~ | ~~¿Hay un tope de cuadrillas por frente, y de dónde sale?~~ | **No es «por frente»: es por oficio dentro del frente.** Frente agrupa actividades de una etapa donde conviven cuadrillas de oficios distintos a la vez —cimentación usa albañil y peón para lo estructural, y otra cuadrilla para instalaciones, al mismo tiempo—; eso es normal, no la restricción. Lo que sí tiene techo es cuántas cuadrillas del **mismo oficio** caben en el mismo frente/etapa sin estorbarse, y depende de la actividad. **Se declara, no se deriva** del catálogo de Frente —que sigue siendo informativo, `CATALOGOS.md`—: mismo origen que una precedencia de Recurso (arriba), media confianza, capturado por quien programa, por combinación frente+oficio. Cierra `PENDIENTES-MEJORAS.md` B-56 |
| ~~P-7~~ | ~~¿El CPM usa el rendimiento real (mano de obra, `CONOCIMIENTO.md` §6.2) en vez del teórico cuando existe?~~ | **El teórico nunca se sobrescribe** — misma cadena que el precio (`CONOCIMIENTO.md` §13.1). El real de mano de obra da una **segunda proyección que convive con la teórica**, nunca un reemplazo. Si diverge más allá de un umbral, avisa `Desviación` (`gravity-obra.md` §6) — nunca reprograma sola, mismo «propone, no aplica». **El umbral no es un número fijo:** es un **rango sugerido —2 a 4 semanas seguidas de datos—** que el sistema propone y el usuario confirma, por dos caminos: proactivo (alerta) o a petición directa (agente Consulta). Puede existir un rendimiento real **global**, agregado entre obras, como referencia adicional — el usuario siempre decide cuál usar |
| ~~P-8~~ | ~~¿Una incidencia de programa y una desviación de costo son el mismo registro?~~ | **No — son independientes.** Comparten vocabulario de causa (`CONOCIMIENTO.md` §13.6, extendido a nueve), pero no siempre coexisten: un error de ejecución puede cobrarse al contratista sin pagar destajo —sin desviación de costo que registrar— y el programa igual se retrasa. Cada uno decide si el motivo le aplica |
| ~~P-9~~ | ~~¿Cruzar el umbral del cuantificador de programación es la misma incidencia?~~ | **No — pero se resuelven con el mismo mecanismo.** La alerta es un disparador automático (`ALERTA`, `MODELO.md` §5a); Control la revisa y decide si es una incidencia real (la origina él, misma cadena de P-8) o se descarta (error de trazo, no de obra) |

**Las nueve decididas.**

> **P-4 completa la simetría:** en lo contratado, el precio y la fecha son las dos
> obligaciones, y ninguna de las dos se mueve por recálculo. Reprogramar propone la
> fecha nueva; alguien la acepta.

> **P-6 y P-7 cierran los dos cabos que quedaban sueltos en el cuerpo del módulo:**
> el techo de cuadrillas y qué hacer cuando el rendimiento real diverge del teórico.
> Las dos se declaran o se avisan; ninguna se calcula ni se aplica sola.

---

# Resumen de la propuesta

| Módulo | Qué desbloquea | Costo | Decisiones |
|---|---|---|---|
| **Factorizador** | Compras reales, inventario contra desperdicio, catálogo más chico | Bajo | ✅ 4 de 4 |
| **Cuantificador** | Cantidades auditables, corpus del paramétrico | **Alto** | ✅ 4 de 4 |
| **Paramétrico** | Presupuestar sin planos, priorizar por incertidumbre | Medio | ✅ 4 de 4 + corpus |
| **CPM** | Recursos por fecha, flujo de efectivo, qué retraso importa | Medio | ✅ 9 de 9 |

**Las 21 decisiones están cerradas** — las 20 anteriores más `P-9` (cruzar el
umbral del cuantificador de programación no es la misma incidencia, aunque se
resuelven igual). Las dos piezas que aparecieron al cerrar las primeras 16 también
se resolvieron: `B-40` (tiempo de entrega) y `B-45` (dónde vive una regla de
gobierno por obra) — ninguna sigue abierta.

## Mi recomendación

**Factorizador primero.** Es el más barato, no depende de nada y arregla tres
problemas que ya tienes hoy en los datos.

**CPM segundo**, aunque el orden de dependencia sugiera otra cosa: sus precedencias
no necesitan cantidades perfectas, y sin ruta crítica el programa que ya existe no
sirve para decidir. Con los recursos por fecha, es además el que entrega el flujo de
efectivo.

**Cuantificador y paramétrico después**, en ese orden, porque el segundo aprende del
primero.

> **Nota de 2026-09-13:** esta propuesta cerraba diciendo que nada era urgente
> mientras B-01 bloqueara. `MODELO.md` ya está aprobado, así que **ese bloqueo no
> existe**; lo que falta de B-01 es implementarlo. El orden recomendado sigue en pie,
> ahora por costo y desbloqueo, no por espera.
