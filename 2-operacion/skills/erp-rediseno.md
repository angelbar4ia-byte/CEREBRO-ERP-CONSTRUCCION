---
name: erp-rediseno
description: Operaciones de autoría sobre un presupuesto cargado — fusión, división, extracción, composición, clonación y borrado — y las tres capas (CARGADO, REDISEÑO, VIGENTE) que las hacen reproducibles. Usar al implementar cualquiera de esas operaciones, al decidir qué pasa con un insumo sin dueño al dividir, al borrar o sustituir una clave, o al aplicar una receta de rediseño sobre un prototipo nuevo. NO cubre la carga desde OPUS — ver `erp-importacion`.
---

```
órgano:     vía mielinizada — rediseño
capa:       II — Operación
pregunta:   ¿cómo se transforma lo cargado sin perderlo?
tiempo:     se hace así
corte:      2026-09-12
compilado:  `CONOCIMIENTO.md` §6.4 · `CONOCIMIENTO.md` §8 · `CONOCIMIENTO.md` §9 · `CONOCIMIENTO.md` §12 — no se escribe a mano
```

> **Satélite.** Carga el skill base `erp-construccion` primero.

---

## 0. La regla de fondo

> **El rediseño no puede ser una edición. Tiene que ser una receta.**

Si fusionar, dividir, extraer y componer modificaran los datos cargados, al importar
el siguiente prototipo se llegaría a datos crudos otra vez y habría que rehacer todo
a mano.

```
1. CARGADO     lo que OPUS entregó. INMUTABLE
2. REDISEÑO    lista ordenada de transformaciones
3. VIGENTE     resultado de aplicar 2 sobre 1. Es lo que se edita
```

**Prototipo nuevo = capa 1 nueva + la misma capa 2 = capa 3 nueva.** El rediseño se
adopta solo.

Es la idea de las migraciones de base de datos: **no se guarda el resultado, se
guardan los pasos**, y se reproducen sobre cualquier punto de partida.

### Lo cargado no se toca

Si el rediseño escribiera sobre lo que OPUS entregó se perdería la única copia fiel
de lo que llegó, y con ella la respuesta a *¿esto lo trajo OPUS o lo hicimos
nosotros?* — que es lo que responde el campo `procedencia`.

### Cuando una regla no encuentra sus piezas

La regla dice fusionar salida hidráulica con sanitaria, pero la casa nueva no tiene
sanitaria.

> Se marca **no aplicada**. No se salta en silencio ni detiene la carga.

### La estructura permanece

Capítulos, subcapítulos, niveles y etapas **permanecen en el árbol**. Es la tercera
vez que aparece la misma regla —el programa reagrupa, el paramétrico reagrupa, el
ensamble reagrupa— y **ninguno reasigna**.

**En lo contratado el rediseño se detiene:** se congela la capa 3 y todo pasa por
control de cambio.

---

## 1. Las seis operaciones

| Operación | Qué hace | Inversa | ¿Clave nueva? |
|---|---|---|---|
| **Fusión** | Varios destajos → uno | División | Sí |
| **División** | Un concepto con 3 destajos → 3 conceptos | Fusión | Sí |
| **Extracción** | Materiales sin destajo → concepto propio | — | Sí |
| **Composición** | Varios conceptos → un concepto nuevo | Explosión | Sí |
| **Clonación** | Un insumo → otro igual | — | Sí |
| **Borrado** | Quita una clave sin uso | — | — |

Las cinco primeras **crean, no editan**. Por eso todas producen clave.

---

## 2. Las cuatro reglas comunes

1. **Conservación medida contra la línea base.** El ponderado por cantidad es siempre
   la base; la diferencia es el indicador de ahorro o pérdida.
2. **No reemplaza al original.** Lo nuevo se agrega. El repello a 4.20 m sigue
   haciendo falta para una casa con muro alto.
3. **Sólo en presupuestos en diseño.** Sobre lo contratado va por control de cambio.
4. **Bitácora de quién lo hizo.**

### Conservación fuerte, no por pieza

La verificación débil —que ninguna parte supere al original— deja pasar el caso feo:

```
concepto de $100  →  se divide en $60 y $50
                     cada uno es menor que $100
                     juntos son $110
```

**La verificación es de suma:** las partes contra el original, con la diferencia
visible.

---

## 3. Fusión

El precio se propone **siempre ponderado por cantidad**, ajustable a mano, y siempre
se puede volver al ponderado.

```
 5 × $85 =   425     Promedio simple: $82.50 → 40 × 82.50 = 3,300   +$75
35 × $80 = 2,800     Ponderado:       $80.63 → 40 × 80.63 = 3,225   neutro
           ─────
           3,225
```

**El promedio simple parece justo y no lo es:** las cantidades están 7 a 1.

> El indicador de ahorro o pérdida es siempre *precio decidido − precio ponderado, por
> la cantidad total*. Así la pregunta «¿comparado contra qué?» ya viene contestada.

El resultado puede bajar o subir el presupuesto. **Las dos son decisiones legítimas;
el sistema sólo tiene que mostrarlo.**

### Reglas propias

- **Unidades compatibles.** Sin unidad común no hay promedio posible: el sistema lo
  impide.
- El fusionado **convive** con los originales: ellos siguen disponibles para
  presupuestar, el fusionado se usa para contratar y programar.
- Si los destajos están enganchados, fusionar cuadrillas cambia el rendimiento y el
  precio nuevo puede salir del modelo en vez de teclearse.

---

## 4. División: qué hacer con lo que no tiene dueño

Al dividir, cada destajo se va con lo suyo. Pero **el agua, el andamio y el acarreo
sirven a las tres partes**.

**Lo decide quien hace la división, parte por parte.** El sistema puede recordar
repartos anteriores y **proponer** para casos similares, nunca aplicarlos solo.

> Si recuerda que el andamio fue proporcional y lo aplica sin preguntar, alguien firma
> un reparto que no revisó.

---

## 5. Clonación

Crear un insumo nuevo copiando el contenido de otro. **No edita: crea.**

El uso principal son las **variantes**: partir de la trabe T-3 y crear la T-4
cambiando la sección, sin capturar todo de nuevo. Arreglar un prefijo equivocado es
apenas un caso particular.

| Modo | Qué pasa con el original | Cuándo |
|---|---|---|
| **Clonar y mantener** | Sigue vivo. **Los dos se usan** | Variante real: T-3 y T-4 conviven |
| **Clonar y sustituir** | **Todo lo que apuntaba al original pasa al clon** | La misma cosa con otro nombre |

### La sustitución sí toca lo existente

Mueve referencias en presupuestos y matrices, así que tiene el mismo alcance que la
corrección de unidad: **libre en diseño, se detiene donde hay contrato.**

El aviso importa más que en el otro modo: **cuántas líneas se van a redirigir y en qué
presupuestos**, antes de aceptar.

### La equivalencia se registra

El clon apunta a su origen, en el diccionario. Sin eso, un año después nadie sabrá que
dos claves son la misma trabe: quedarían como dos insumos distintos con el mismo
precio.

---

## 6. Borrado

> **La clave nunca se reescribe. Se puede borrar, pero sólo mientras nada dependa de
> ella.**

### La condición es objetiva

El sistema **cuenta las referencias**; no lo juzga alguien:

- No está en ningún presupuesto ni en ninguna capa de matriz, **o**
- Está, pero **con cantidad cero**

> Una línea en cero es **referencia de forma, no de fondo**: no aporta al costo ni al
> consumo.

El conteo debe mirar también **compras y estimaciones**, no sólo presupuestos: un
insumo comprado directo tiene historia aunque ningún presupuesto lo use.

### El borrado no baja

| Dirección | Qué pasa |
|---|---|
| **Hacia arriba** | Las líneas donde aparece **en cero se eliminan** |
| **Hacia abajo** | **Nada** |

Al borrar una mezcla que contiene cemento en cero y arena en cinco, **el cemento y la
arena siguen existiendo** con todos sus otros usos intactos. Lo que desaparece es la
mezcla; sus propias líneas de composición se van con ella porque **son su
definición**.

**Si algo lo referencia con cantidad, el insumo ni siquiera es borrable.**

### Sustituir y borrar son dos actos

Sustituir es lo que **deja borrable** al original: después, nadie le apunta. Pero
borrar se decide aparte, después.

---

## 7. Composición — matriz dentro de matriz

Se distingue del ensamble en un punto que lo cambia todo: **produce clave nueva**, y
por eso entra al catálogo.

| | Clave nueva | Vive en | En el presupuesto |
|---|---|---|---|
| **Ensamble** | no | catálogo de ensambles | aparece como sus partes |
| **Concepto compuesto** | **sí** | catálogo de conceptos | **un renglón** |
| **Auxiliar** | sí | sólo ese presupuesto | agrupador |

La diferencia real entre compuesto y auxiliar es la **reutilización**. Un auxiliar
muere en su presupuesto; un compuesto sirve para cualquiera futuro. **Es la vía para
crear APU nuevos.**

### Flotante

El compuesto **toma siempre la versión vigente de cada hijo**, no las congela. El
cambio se propaga hacia arriba por todos los caminos.

> **La alerta debe decir qué cambió abajo**, no sólo que algo cambió. Con tres niveles
> de anidamiento, «este concepto se movió» no permite encontrar la causa.

### Prohibición de ciclo

> **Un compuesto A nunca puede vivir dentro de A**, ni directamente ni a través de otro.

La validación recorre **toda la cadena de ancestros**, no sólo el padre directo, y
ocurre **al agregar el hijo, no al calcular**.

### Unidad y cantidades

Se eligen manualmente. El compuesto declara su propia unidad y las cantidades de los
hijos son *por esa unidad*.

---

## 8. Los errores que este skill previene

1. Escribir el rediseño sobre la capa cargada y perder la copia fiel del origen.
2. Guardar el resultado en vez de los pasos — y tener que rehacerlo todo en el
   siguiente prototipo.
3. Saltar en silencio una regla que no encontró sus piezas.
4. Verificar la conservación pieza por pieza en vez de por suma.
5. Proponer promedio simple en una fusión con cantidades desiguales.
6. Fusionar unidades incompatibles.
7. Reemplazar los originales al fusionar.
8. Aplicar solo un reparto recordado de insumos sin dueño.
9. Sustituir una clave sin avisar cuántas líneas se redirigen.
10. Al borrar una mezcla, borrar hacia abajo sus insumos.
11. Borrar algo referenciado con cantidad distinta de cero.
12. Congelar las versiones de los hijos de un compuesto.
13. Validar el ciclo sólo contra el padre directo, o al calcular en vez de al agregar.
14. Rediseñar sobre un subárbol contratado.
