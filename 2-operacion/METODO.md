# MÉTODO

```
órgano:     función ejecutiva · identidad
capa:       II — Operación
pregunta:   ¿cómo se piensa aquí?
tiempo:     se hace así
corte:      2026-09-11
verificado: 6 reglas · cada una con su error en MEMORIA
```

> **Cómo se piensa aquí.** Los otros archivos dicen qué es verdad; este dice **cómo
> se averigua**.
>
> Todo lo que sigue se ganó equivocándose. Cada regla tiene detrás un error concreto
> registrado en `MEMORIA.md`.
>
> 2026-09-11

---

## Qué es este cerebro

Un modelo de ERP de construcción **verificado contra datos reales**, no diseñado en
abstracto. Ocho catálogos de OPUS 2025, doce ingenierías de obra, y cada regla
comprobada aritméticamente antes de escribirse.

**Para qué sirve:** crear un ERP nuevo, reestructurar los existentes, y darles a
todos un idioma común para que hablen entre sí.

**Lo que NO es:** una propuesta teórica. Si algo está escrito como regla, se verificó.
Si no se verificó, dice que no se verificó.

---

# 1. Las seis reglas de trabajo

## 1.1 Leer un catálogo no basta

> **Hay que calcular con él y contrastar contra un total conocido.**

Cinco hallazgos importantes **no salieron de leer archivos**, salieron de hacer algo
con ellos:

| Hallazgo | Apareció al |
|---|---|
| 58 cantidades negativas | Escribir el caso trabajado |
| El filtro por código pierde 11 filas | Validar el artefacto contra el total declarado |
| Las etapas son 52, no 50 | Derivar el vocabulario en vez de leer el catálogo |
| El factor 1.085 entre rendimientos | Cruzar el catálogo viejo con el vigente |
| El `Costo` de `%MO` es la base, no un precio | Explotar las cuadrillas |

**El total conocido es lo que salva.** Sin un número contra el cual comparar, un
error de un tercio pasa desapercibido.

## 1.2 Comparar cosas del mismo alcance

El error más caro de esta etapa: comparar el consolidado de **12 archivos parciales**
contra **la matriz de un solo concepto**. Daba diferencias de 500x y 700x que no
significaban nada.

> **Antes de interpretar una diferencia, verificar que las dos cosas midan lo
> mismo.** Una diferencia enorme casi siempre es un error de alcance, no un hallazgo.

Cómo se detecta: si el total de la base no cuadra con el declarado, el alcance está
mal. En este caso daba $1.9M contra $2.83M — faltaba explotar los compuestos.

## 1.3 Derivar antes que pedir

Cuatro vocabularios —unidades, niveles, etapas, familias— iban a pedirse a OPUS.
**Ya estaban dentro de los datos.**

> **Si algo se puede derivar del uso, el catálogo deja de ser entrada: es un
> subproducto.** Siempre completo, sin huérfanos, y no se desactualiza.

Y derivar **encuentra lo que leer esconde**: al derivar las etapas aparecieron 52
donde el catálogo decía 50. Los huecos en la numeración no eran registros borrados
— eran etapas nuevas.

## 1.4 Dos métodos independientes que coinciden son una validación

La losa de `ALAMO 18` dio **1.12** comparando totales por etapa, y **1.130**
reversando desde el destajo.

> Cuando dos caminos distintos llegan al mismo número **sin conocer el resultado del
> otro**, los dos quedan validados. Es la mejor prueba disponible cuando no hay una
> respuesta de antemano.

## 1.5 Una regla que aparece tres veces ya no es coincidencia

Cinco reglas llegaron solas, repetidas, sin buscarlas:

| Regla | Veces | Dónde |
|---|---|---|
| **Mientras nada dependa, se corrige; en cuanto algo depende, se agrega encima** | **5** | Catálogo al contratar · unidad del concepto · precio pactado · clave del insumo · identidad entre ERPs |
| **Plantilla e instancia** | **5** | APU · ensamble · contrato · trazo · prototipo-ingeniería |
| **Nada reasigna** | 3 | Programa · paramétrico · ensamble |
| **Declarado menos calculado** | 3 | Fusión · extracción · alzado |
| **El prefijo no es llave** | 3 catálogos | Conceptos · trabajos · materiales |

> Cuando una regla llega sola al cuarto o quinto lugar donde aplica, **describe algo
> real del dominio**, no una preferencia de diseño. Esas son las que van al skill.

## 1.6 Registrar lo descartado, no solo lo decidido

Doce ideas razonables se evaluaron y se rechazaron: `%MO` como campo, renombrar el
prefijo `AUX-`, MPTT, ampliar el WBS, invertir familia y subfamilia.

> Sin ese registro, **un agente que aprende de lo aprobado reproduce indefinidamente
> lo que ya se rechazó.** Por eso el rechazo se conserva — en el diccionario, en las
> propuestas, y en `MEMORIA.md` §2.

---

# 2. Cómo tratar los datos

## 2.1 El prefijo nunca es llave

Comprobado en tres catálogos. **El peor caso: `AUX-`** — nombra una categoría que el
insumo no tiene. Las 79 claves `AUX-` son `Tipo = Material`.

> Ese error lo cometió este mismo cerebro: dedujo del prefijo teniendo la regla
> escrita. **La regla escrita no basta si el dato tiene una columna que invita a
> usarla mal.**

## 2.2 Un nombre igual no significa lo mismo

`Familia` significa sustancia en materiales, oficio en trabajos, rango en mano de
obra. Y **ocho nombres coinciden literalmente por accidente**.

> **Se traduce por significado, no por nombre.** Un traductor que empareje por nombre
> produce datos que **cuadran y mienten**.

Lo mismo con `Tipo` —cuatro significados—, `Nivel` —tres—, `Cantidad` —tres— y
`Costo`, que en las líneas `%MO` **no es un precio sino la base ya calculada**.

## 2.3 Lo que parece error suele ser intencional

| Parecía error | Era |
|---|---|
| Insumos colgando de la etapa sin concepto | Intencional: costo no atribuible a una partida |
| Cantidades negativas | Ajustes que descuentan material ya contado |
| El mismo insumo dos veces en una matriz | Dos usos distintos — amarre de varilla y de estribos |
| Filas en blanco | **Separador de bloque** — 155 casos sin excepción |
| `EQU` clasificado como material | Equipamiento *es* material |

> **Antes de "limpiar" algo raro, preguntar.** Cuatro de estas cinco se habrían
> destruido en una migración que las tratara como suciedad.

## 2.4 El nombre del archivo es dato

`INGENIERIA_-_ALAMO_18_-_CIM` dice el lote y la etapa. Y en los archivos sueltos
—`AJU_PISOS`, `CENTRO_DE_CARGA`— **la estructura vive solo en el nombre**: el
contenido no dice a qué nivel ni etapa pertenece.

También los metadatos: quién modificó y cuándo. *La fecha de creación que reporta la
librería es falsa — la escribe al abrir el archivo.*

## 2.5 La descripción puede mentir

`ALAMO 18` decía «Losa cimentación Zafiro Plus». **Era Diamante con chimenea**, y se
descubrió comparando totales por etapa: tres dieron 1.00 o 1.03 contra Diamante
y ninguna
se acercó contra Zafiro Plus.

> **El contenido es la evidencia; la descripción es una etiqueta.** Si alguien forma
> el presupuesto leyendo la etiqueta, costea el prototipo equivocado.

## 2.6 Una tabla que el usuario sube se guarda en el repo antes de leerla

Lo que se sube a una sesión vive en una carpeta temporal de la máquina y **se pierde con ella**: el usuario no tiene por qué volver a subirlo ni
volver a oír la pregunta. Al recibir una tabla —antes de analizarla—:

1. `cd backend && python3 -m api.guardar_subidas` copia lo nuevo a `1-mundo/opus/` o `1-mundo/fuentes/` (el libro tal cual, cada hoja en CSV) y lo anota en
   `1-mundo/fuentes/MANIFIESTO.csv`.
2. Commit y push: lo guardado solo en la máquina tampoco sobrevive a ella.
3. `python3 -m api.guardar_subidas --verificar` (y el CI, con una prueba) dice si algo falta, cambió o llegó sin registrarse.

Los CSV recortados o consolidados que se generen para analizar son derivados: se regeneran del original y no se guardan en su lugar.

---

# 3. Cómo decidir

## 3.1 La pregunta correcta no es «¿se puede editar?»

Es **«¿ya hay algo que dependa de esto?»** — y esa el sistema la contesta solo,
contando referencias.

```
Sin uso            →  se corrige o se borra libremente
Con uso, en diseño →  se corrige mostrando el alcance
Con algo contratado→  no se toca: se agrega encima
```

## 3.2 Propone, no aplica

Aparece nueve veces en el modelo. Por eso **la propuesta es una entidad**, no un
campo en cada mecanismo — si no, serían nueve bandejas distintas.

**Tres reglas que la sostienen:**

- **Una propuesta sin evidencia es una orden disfrazada.**
- **El rechazo se conserva.**
- **La detección nunca necesita permiso; la corrección siempre.**

## 3.3 No modelar lo que no está decidido

Dos campos se retiraron del modelo en vez de dejarlos «provisionales»: el código
externo y la restricción de subfamilia.

> **Un campo provisional deja de serlo en cuanto algo empieza a depender de él.** Es
> la misma trampa que la regla de dependencia existe para evitar.

## 3.4 Cada hecho vive en un archivo

Ya pasó dos veces que un hecho vivía en dos lugares y empezaron a separarse: un
bloque duplicado dentro del conocimiento, y once pendientes en dos archivos.

> `INDICE.md` tiene la regla de enrutamiento. **Si un tema está en dos archivos, uno
> sobra.**

---

## 3.5 Al detectar una contradicción: parar

**Una contradicción no se resuelve sobre la marcha.** Se para, se pregunta, se
propone. Nunca se elige solo, nunca se promedia, nunca se sigue «mientras tanto».

```
1. NOMBRAR    las dos afirmaciones, y dónde vive cada una
2. PARAR      el trabajo que depende de ellas
3. PREGUNTAR  con las opciones y la consecuencia de cada una
4. PROPONER   una, con la evidencia que la respalda
5. REGISTRAR  la resolución, incluida la opción que se descartó
```

**Antes del paso 1, una comprobación que ahorra la mitad de los casos:**

| Parece contradicción | Y puede ser |
|---|---|
| Dos valores del mismo hecho | **El mismo hecho en dos fechas.** Once y doce ingenierías no se contradicen: azotea se subió después |
| Una regla que choca con otra | **Dos ámbitos distintos.** En diseño fluye, en contratado se congela: no es contradicción, es alcance |
| Un dato que no cuadra | **Dos bases distintas.** Una obra con catálogo viejo no tiene desviación por eso |

> **Preguntar primero si es el mismo hecho o el mismo hecho en dos momentos.** Tratar
> una evolución como error hace perder el dato que la explica.

Y lo que nunca se hace: **elegir el valor que conviene y seguir.** Una contradicción
resuelta en silencio reaparece más tarde, y para entonces ya hay cosas construidas
encima de las dos versiones.

## 3.6 La misma cifra afirmada dos veces es donde vive la contradicción

Comprobar estructura y comprobar referencias no encuentra que dos partes del mismo
archivo sostengan números distintos del mismo hecho. Eso sale de otra manera:
**agrupar cada cifra por el sustantivo que la acompaña y mirar dónde hay más de un
valor.**

Así apareció que el conocimiento analiza **once** ingenierías de `ALAMO 18` en una
sección y habla de **doce** en las dos siguientes, y que el estado y este archivo
declaran doce en su frase de identidad.

> **Ninguna de las tres revisiones anteriores lo vio.** Cada una comprobaba que las
> partes encajaran, no que dijeran lo mismo.
>
> Qué cifras viven en más de un sitio y quién las guarda: `METACOGNICION.md` §2.

## 3.7 Una referencia se audita por tema, no por que resuelva

Que una sección exista no significa que hable de lo que dice la frase que la cita. Después
de renumerar, 16 referencias apuntaban a una sección **existente y equivocada** — y el
verificador las daba por buenas, porque resolvían.

Se detectan comparando el vocabulario de la frase con el de la sección destino: si no
comparten casi nada, o la referencia está mal o la frase no dice lo que cree decir.

> **Tres de las 16 estaban mal desde antes de dividir.** Las capas de sobrecosto se
> citaban como conocimiento y nunca vivieron ahí. Un error de referencia sobrevive
> años si nadie comprueba el tema.

## 3.8 Una reescritura masiva se audita contra el original

Un remapeo automático sobre 28 archivos renumeró encabezados de seis que no debía
tocar, y rompió 17 referencias que ya apuntaban a otro archivo.

> **El verificador daba «todo cuadra» con los archivos corrompidos.** Comprobaba que
> las referencias resolvieran, y resolvían — a la sección equivocada.

Lo que lo encontró fue **comparar contra el original línea por línea**, normalizando
lo que sí debía cambiar. Es la misma regla de §1.1 aplicada al propio cerebro: sin un
punto de comparación conocido, un error grande pasa desapercibido.

# 4. Los errores que este cerebro ya cometió

Están completos en `MEMORIA.md` §3. Los que más enseñan:

| Se afirmó | Era | Lección |
|---|---|---|
| La trabe es un auxiliar | Material compuesto | El prefijo engañó |
| El compuesto solo admite su categoría | Admite cualquiera | Se generalizó sin verificar |
| La obra corrige al catálogo | La obra **informa**; alguien decide | Corregir por un mal proceso institucionaliza el error |
| El reporte por recurso debe explotar | Se detiene en el compuesto | Dos lecturas, no una |
| Zafiro Plus tiene 4 subcapítulos | Tiene 15 | Error de lectura de una propia salida |
| La primera carga marcará deriva masiva | **Cero deriva** | Predicción sin verificar |

> **Seis de ocho las detectó el usuario, no el sistema.** Por eso el patrón de
> proponer y esperar aprobación no es cortesía: es el mecanismo que atrapa estos
> errores.
>
> Las familias en que se agrupan los errores posteriores, y qué atrapa cada una:
> `METACOGNICION.md` §5.

---

# 5. Qué hacer al retomar

1. **Leer `MEMORIA.md` §2 antes de proponer cualquier cosa.** Ahí está lo descartado
   con su razón.
2. **No dar por buena ninguna regla que no diga cómo se verificó.**
3. **Si algo no cuadra, sospechar del alcance antes que del dato.**
4. **Preguntar antes de limpiar.** Lo raro suele ser intencional.
5. **Proponer, no aplicar.** Con evidencia.
