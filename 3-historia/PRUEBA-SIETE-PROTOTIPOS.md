# PRUEBA DE FLUJO — LOS SIETE PROTOTIPOS

```
órgano:     memoria episódica — prueba de sistema
capa:       III — Historia
pregunta:   ¿el camino paramétrico aguanta sobre el catálogo real?
tiempo:     fue así
corte:      2026-10-12
verificado: 6 etapas · 2 pasan · 1 con matices · 2 diseñadas sin caso real que las ejerciten · 1 sin poder probarse · cifras de las etapas 1 a 4 vueltas a sacar de `CATALOGO_DE_PRESUPUESTO.csv` el 2026-10-12
```

> **Tercera prueba (B-42).** Las otras dos siguen **una obra**. Ésta sigue **el
> conjunto**: los siete prototipos, $16,460,623.50, de 172 a 300 m².
>
> Es el camino que ninguna prueba de una sola obra puede recorrer, porque el
> paramétrico sólo existe cuando hay varios casos que comparar.

---

# El recorrido

| # | Etapa | Resultado |
|---|---|---|
| 1 | Paramétrico global | ⛔ **Se rompe — y era esperado** |
| 2 | Paramétrico por subcapítulo | ⚠️ **Pasa en 3 de 6** |
| 3 | La cohorte como explicación | ✅ Pasa — el mejor resultado |
| 4 | La dispersión como diagnóstico | ✅ Pasa |
| 5 | El parámetro propio | 🔶 **Diseñado (B-53)** — desplante ya se usó con dato real; salidas y el parámetro de Herrería siguen sin confirmarse |
| 6 | Extracción y generación | 🔶 **Diseñado desde antes** (`CONOCIMIENTO.md` §5.8) — ninguna dirección construida |

---

## 1 · Paramétrico global — ⛔ se rompe

```
$8,717/m²  ───────────────────────────  $11,841/m²
                 36% de variación
```

**Un solo número por m² para toda la casa no sirve.** Sobre 172 m², ese rango son
$537,000 de diferencia: más que decidir a ojo.

> No es un fallo del método: es el resultado que hacía falta para descartar la
> solución fácil. **Si no se mide, alguien la implementa.**

---

## 2 · Por subcapítulo — ⚠️ pasa en la mitad

| Subcapítulo | $/m² | Dispersión | ¿Usable? |
|---|---|---|---|
| Acabados | 911 | **5%** | ✅ |
| Planta alta | 1,371 | 10% | ✅ |
| Carpintería | 1,063 | 11% | ✅ al límite |
| Cancelería | 405 | 20% | ⚠️ |
| Cimentación | 931 | 23% | ⚠️ |
| Herrería | 116 | **38%** | ⛔ |

Bajar un nivel de agregación mejora mucho, **pero no arregla todo**. Y el patrón
tiene sentido físico: lo que se mide por superficie funciona; lo que se cuenta por
pieza o depende del diseño, no.

---

## 3 · La cohorte — ✅ el mejor resultado de las tres pruebas

La cimentación parecía irregular con 23%. Separando por número de plantas:

```
1 planta    Zafiro 1,039   Rubí 1,012   Jade 1,053           → CV  2%
2 plantas   ZafPlus 660  Diam− 1,090  Diam+ 1,085  Oro 577   → CV 32%
                                                     juntos  → CV 23%
```

**En una planta la cimentación por m² es prácticamente idéntica: 2%.** Lo que la
rompía no era el dato: era mezclar dos poblaciones distintas.

> En dos plantas el m² construido ya no es proporcional a la superficie de desplante.
> El dato siempre fue bueno; la pregunta estaba mal hecha.

**Esto valida la decisión M-2 con evidencia**: la cohorte no es burocracia, es lo que
convierte un 23% inservible en un 2% utilizable.

Y deja ver algo más: los de dos plantas siguen en 32% **incluso separados**. La
cohorte «dos plantas» no basta — hay otra variable adentro. Zafiro Plus a 660 y Oro a
577 contra los dos Diamante en 1,085-1,090 es demasiada distancia para llamarlo
dispersión.

**Y al recalcularlo, la explicación de las plantas se cayó.**

| Grupo | Prototipos | $/m² | CV |
|---|---|---|---|
| **A** | Zafiro 1.0, Rubí, Jade, **Diamante −, Diamante +** | 1,056 | **2.8%** |
| **B** | Zafiro Plus, Oro 4.01 | 618 | 6.7% |

**Los dos Diamante tienen planta alta y se comportan como los de una planta.** Cinco
de siete comparten tasa; los dos que se salen están **1.71× por debajo** — eso no es
dispersión, es otra población.

> **Hallazgo doble.** Uno de dominio: la cohorte de cimentación no es el número de
> plantas, y qué es sigue sin saberse (**B-52**; D-312: es el desplante). Y uno de método: **una partición que
> mejora el número no queda probada por mejorarlo.** El 32% que quedaba en el otro
> subgrupo era la señal de que faltaba explicación, y se leyó como ruido.

> **Releído el 2026-10-12 contra `1-mundo/opus/CATALOGO_DE_PRESUPUESTO.csv`.** Salen igual: los $16,460,623.50, el rango
> de $8,717 a $11,841 por m² (35.8%, $537,328 sobre 172 m²), los $/m² de cada subcapítulo y de la cimentación por
> prototipo, el 1.71× y el CV de 6.0% contra el desplante. Con dos matices en cómo se calculó la dispersión: el
> 2.8% del grupo A da 2.7% con desviación poblacional y 3.1% con muestral, y el 2% y el 32% de la cohorte por plantas
> son muestrales (poblacional: 1.6% y 27.7%) mientras que el 6.7% del grupo B es poblacional. La conclusión no cambia,
> pero una cifra de dispersión debe decir cuál de las dos es.

> **Actualización 2026-09-26 — B-52 ya contestó qué es.** Medido contra el
> desplante declarado en la propia losa de cimentación de cada prototipo (no el
> número de plantas), los siete caen en el mismo rango, CV 6.0%. `Zafiro Plus` y
> `Oro` tenían mucha más planta alta relativa que los otros cinco — por eso salían
> «1.71× abajo» al dividir entre m² total. `CONOCIMIENTO.md` §5.7, D-312

---

## 4 · La dispersión como diagnóstico — ✅

Funciona tal como se decidió en M-3: **la dispersión alta no avisa sobre el número,
dice que el parámetro está mal elegido.**

| Dispersión | Qué significa de verdad |
|---|---|
| Acabados 5% | El m² **es** el parámetro correcto |
| Cimentación 23% | La cohorte está mal armada — se arregla separando |
| Herrería 38% | El m² **no es** el parámetro. Es otra cosa |

**Tres diagnósticos distintos con el mismo síntoma.** Si la dispersión sólo se
mostrara como aviso, los tres se verían igual.

---

## 5 · El parámetro propio — 🔶

Está decidido que cimentación escala con desplante e instalaciones con salidas
(D-98). **Pero no hay datos para comprobarlo:** el catálogo trae m² construidos, no
superficie de desplante ni número de salidas.

| Para probar | Hace falta |
|---|---|
| Cimentación por desplante | Superficie de desplante por prototipo |
| Instalaciones por salidas | Conteo de salidas por prototipo |
| Herrería por su parámetro | Saber cuál es — **ni eso está decidido** |

> **Hallazgo: se decidió que cada ensamble lleva parámetro propio, y no existe dónde
> guardarlo ni de dónde sacarlo.** Es el contrato de lo declarado otra vez: el
> concepto se usó sin darle casa. **B-53.**

Y cierra un círculo con la prueba de ALAMO 18: **el cuantificador es el que produciría
esos parámetros.** Sin él, el paramétrico está limitado a lo que el catálogo ya trae.

> **Actualización 2026-09-26 — diseñado, y parcialmente probado con dato real.**
> `ENSAMBLE_PARAMETRO` (B-53, `MODELO.md` §1c, D-325) le da dónde vivir a
> tasa/cohorte/dispersión; el resto —plantilla/instancia, origen de cantidad,
> referencia al concepto— ya lo cubrían `NODO`/`COMPOSICION` sin campo nuevo. El
> desplante en concreto ya se usó con dato real, declarado en la propia losa de
> cimentación de cada prototipo (arriba, B-52). Pero el cuantificador que
> produciría estos valores de forma sistemática para un caso nuevo **sigue sin
> existir** — `PRUEBA-ALAMO-18.md` etapa 3 sigue `⛔` — y el parámetro propio de
> Herrería sigue sin identificarse. Por eso queda en `🔶`, no en `✅`: tiene schema
> y un caso real parcial, no el mecanismo completo.

---

## 6 · Extracción y generación — 🔶

No existen. Las dos direcciones están diseñadas (§5.8) y ninguna construida.

> **Actualización 2026-09-26 — cambia el símbolo, no el contenido.** Este mismo
> texto ya decía «diseñadas, ninguna construida» desde 2026-09-13 — es exactamente
> lo que `🔶` significa en las otras dos pruebas de flujo. Se corrige el símbolo
> para que las tres cuenten igual (B-42).

---

# Resultado

**Dos pasan, una tiene matices, dos quedan diseñadas sin caso real que las
ejerciten, una no se puede probar.** Cuando se corrió esta prueba (2026-09-13) el
resumen era otro —tres pasan, tres se rompen— y las tres roturas eran de un tipo
distinto al de las otras pruebas:

| Prueba | Modo de fallo |
|---|---|
| ALAMO 18 | **Falta el dato** — las salidas de almacén |
| Zafiro 1.0 | **El dato está sucio** — unidades sin normalizar |
| Siete prototipos | **El dato existe pero no es el que hace falta** — m² construidos donde se necesita desplante |

> Tres modos de fallo distintos, y ninguno se arregla igual. Eso por sí solo
> justificaba correr las tres.

> **Actualización 2026-09-26.** El modo de fallo de esta prueba seguía siendo
> cierto en parte: el desplante sí estaba, declarado en la propia losa de
> cimentación de cada prototipo, y ya se usó con dato real para cerrar B-52. Lo que
> sigue faltando es el mecanismo que produzca ese dato de forma sistemática para un
> caso nuevo (el cuantificador, todavía `⛔` en `PRUEBA-ALAMO-18.md`) y el parámetro
> propio de Herrería, que sigue sin identificarse. Por eso la etapa 5 pasa de `⛔` a
> `🔶` y no a `✅`. La etapa 6 solo corrige símbolo: «diseñadas, ninguna construida»
> ya era `🔶` desde el 2026-09-13, en todo menos el nombre.

## Lo que validó

- **La cohorte convierte un 23% inservible en un 2% utilizable.** Es la evidencia más
  fuerte de todo el paramétrico y sale de datos reales.
- La dispersión distingue tres problemas distintos con el mismo síntoma.
- El paramétrico global se descartó **con medición**, no por intuición.

## Lo que encontró

| # | Hallazgo | Dónde quedó |
|---|---|---|
| 1 | La cohorte de dos plantas esconde una segunda variable | B-52 |
| 2 | El parámetro propio no tiene dónde guardarse ni de dónde salir | B-53 |
| 3 | Sin cuantificador, el paramétrico se limita a lo que el catálogo trae | Refuerza C-1 |
