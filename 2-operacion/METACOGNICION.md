# METACOGNICIÓN

```
órgano:     corteza prefrontal anterior — metacognición
capa:       II — Operación
pregunta:   ¿qué sabe el cerebro de sí mismo y cómo le llega a cada parte lo que cambia?
tiempo:     se hace así
corte:      2026-10-12
verificado: medido el 2026-10-12 con red-del-cerebro.py y verificar-cerebro.py
```

> **Cómo se mira el cerebro a sí mismo.** `METODO.md` dice cómo se averigua un hecho; este
> archivo dice cómo se averigua **el estado del propio cerebro**: qué le llega a quién, qué
> está conectado con qué y qué cree saber que quizá ya no sabe.

---

# 1. Tres ideas, usadas como instrumentos

`INDICE.md` ya da a cada archivo un órgano. Eso es una metáfora, y una metáfora solo se
queda si produce una prueba que pueda fallar. Estas cinco la producen:

| Idea | Qué dice en neurociencia | Qué se mide aquí |
|---|---|---|
| **Espacio de trabajo global** (Baars; Dehaene y Changeux) | Procesos especializados compiten por un escenario de capacidad limitada; lo que gana se difunde a todo el sistema —en el cerebro, a redes frontoparietales— en una «ignición» | Qué se lee primero, por dónde pasa todo cambio y si les llega a quienes actúan |
| **Conectividad estructural y funcional** | La anatomía (qué neurona se conecta con cuál) no es lo mismo que la estadística (qué se activa junto) | Referencias escritas entre archivos, contra archivos que cambian en los mismos commits |
| **Metacognición** (Flavell; Fleming) | Saber qué se sabe, con qué confianza, y dónde se falla | Vigencia, errores ya cometidos e ignorancia conocida |
| **Información integrada** (Tononi) | Un sistema tiene tanto más cuanto menos se puede partir sin perder información, y a la vez cada parte dice algo que las demás no. Su medida, Φ, es exacta solo en sistemas muy pequeños | Cuánto cuesta partir la red de referencias, y qué tanto de lo que dicen dos archivos es lo mismo (§3.1 y §3.2) |
| **Núcleo dinámico** (Edelman y Tononi) | Lo que cuenta es la reentrada: señales que vuelven en los dos sentidos y rápido, entre tálamo y corteza | Si un archivo compilado oye cuando cambia la sección de la que sale, y si todo cambio pasa por el relevo (`INDICE` y `ESTADO`) (§3.3) |

> **Lo que no se afirma.** Ni que este cerebro sea consciente, ni que alguna de estas teorías sea
> la correcta —son rivales entre sí, y la de información integrada es de las más disputadas—. Se
> toma su arquitectura, no su metafísica. **Φ no se calcula**: pide un modelo causal del sistema que
> un conjunto de archivos no tiene. De la información integrada se usa solo la idea de que integrar y
> diferenciar van juntos, y cada medida de abajo es un sustituto que puede fallar.

---

# 2. La difusión: el espacio de trabajo global

| Propiedad | En un cerebro | En este cerebro | Prueba | Resultado (2026-10-12) |
|---|---|---|---|---|
| **Capacidad limitada** | Pocos contenidos ocupan el escenario | `ESTADO.md` e `INDICE.md`, lo que se lee primero | Ninguna fila de tabla pasa de 2,500 caracteres | Había una celda de 35,438, una cronología de D-383 a D-489. Se condensó a estado y el verificador lo impide |
| **Difusión** | Lo seleccionado llega a todos | Toda decisión pasa por los mismos archivos | Qué cambia en cada commit (`red-del-cerebro.py`) | `ESTADO`, `MEMORIA` e `INDICE` cambian en más del 95% de los commits y `PENDIENTES-MEJORAS` en más del 80%: ese es el espacio de trabajo real, y coincide con el diseñado |
| **Recepción** | Los procesos especializados lo reciben | Cada agente que actúa lee el foco antes de actuar | Qué archivos nombra cada agente | De los seis, solo `gravity` leía `ESTADO.md`. `constructor-erp` y `arquitecto-erp`, los que construyen o diseñan, no sabían de D-487; ahora lo leen primero. `auditor`, `migrador` y `gravity-obra` comprueban, leen o corren dentro del producto: no lo necesitan |
| **Ignición** | Todo o nada: el cambio llega a todas partes o no cuenta | Una cifra que vive en varios sitios cambia en todos o falla | El verificador | Está guardada, y se dice abajo qué cifras no |
| **Informabilidad** | Lo difundido se puede reportar | Cada decisión lleva su razón | `MEMORIA.md` | Una fila por decisión, con la opción descartada |

Los skills **no** leen el estado, y es a propósito: se compilan del conocimiento, y el estado
cambia más rápido que una regla.

**Las cifras que viven en más de un sitio**, y quién las guarda:

| Cifra | Dónde se repite | Guardián |
|---|---|---|
| Decisiones | `MEMORIA`, `INDICE`, `ESTADO` | verificador |
| Hallazgos de `MODELO`, partes de `CONOCIMIENTO` | varios | verificador (D-487) |
| Migraciones | `INDICE`, dos agentes | verificador (D-491) |
| Etapas que pasan, con matices, diseñadas y sin poder probarse | tres `PRUEBA-*`, `ESTADO`, `PENDIENTES-MEJORAS` | verificador (D-491) |
| **Pruebas del backend** | `INDICE`, `ESTADO`, `PROGRAMA-CPM`, `PENDIENTES-MEJORAS` | **nadie**: se corre la suite y se cambian las cuatro a mano |
| **Lo que dice cada agente del código que existe** | `agentes/` | **nadie**: por eso `constructor-erp` decía 0009 con la 0010 ya hecha |

---

# 3. Las conexiones: estructural y funcional

Medido con `python3 2-operacion/red-del-cerebro.py .` el 2026-10-12, al terminar el día. **Estas cifras se mueven cada vez que se agrega un archivo** —el mismo día, entre la primera medida y esta, pasaron de 37 archivos y 293 conexiones a 38 y 310—: son una foto con fecha, no un invariante.

- **Estructural.** 38 archivos y 310 conexiones distintas (2,081 referencias). Nadie queda sin que lo
  nombren, nadie sin nombrar a otro, y `INDICE` y `README` llegan a los 38. El camino medio entre dos
  archivos es de 1.66 saltos y el agrupamiento 0.75; con 38 nodos eso es lo esperable de una red
  tan densa, y no se saca de ahí ninguna conclusión. 68 de las 310 conexiones tienen vuelta.
- **Concentradores.** `CONOCIMIENTO` (lo nombran 28 archivos) y `MODELO` (23). `METODO` lo
  nombran 20 y él nombra 3: es la identidad, un receptor. `MEMORIA` es el integrador (la nombran 17 y
  nombra a 30).
- **La estructura y la función coinciden.** De los pares que cambian juntos al menos ocho veces,
  solo dos no se nombran (`INDICE` con `PRUEBA-ALAMO-18` y `ESTADO` con `gravity-obra`). No hay un
  acoplamiento escondido grande.
- **Lo estable apunta a lo volátil.** La capa I (Mundo) tiene 103 referencias a la IV
  (Dirección), 62 de ellas de `CONOCIMIENTO` a `PENDIENTES-MEJORAS`. Es segura mientras los
  identificadores no se reutilicen ni se borren (`README.md`: «un pendiente resuelto no se
  borra»); se comprobó que ningún `B-` citado queda sin definir.
- **Lo que se desactualiza no es la conexión, es la afirmación que viaja por ella.** Una
  referencia que lleva un identificador (`B-82`) no caduca. Una que lleva un estado («sigue
  abierto») sí: el 2026-10-12 se encontraron ocho en `CONOCIMIENTO`, `RAZONAMIENTO` y
  `PRUEBA-SIETE-PROTOTIPOS` que decían abierto algo ya resuelto.

## 3.1 Integración: ¿se puede partir la red sin perder referencias?

`red-del-cerebro.py --integracion`, el 2026-10-12.

- **Ningún archivo desconecta la red al salir y no hay un solo puente.** Quitar cualquiera deja a los demás conectados.
- **La partición más floja** (con al menos cinco archivos por lado) corta 40 de las 2,081 referencias, 1.9%: separa a `auditor-erp`, `migrador-erp`
  y tres skills (`erp-parametrico`, `erp-programa`, `erp-rediseno`) de todo lo demás. Con diez por lado corta 4.8% y el lado chico son
  agentes, skills y dos pruebas de flujo. Lo que se parte más barato es **lo derivado**, que es justo donde se desincronizó
  el cerebro: dos agentes en la migración 0009 (D-491), skills que repetían una explicación retirada (D-480).
- **Una predicción que no se sostuvo.** Si lo menos integrado envejeciera primero, los archivos con menos vecinos tendrían el `corte` más viejo.
  Medido sobre los 36 archivos antes de D-491, fue lo contrario: ρ de Spearman = +0.30 entre vecinos y edad del corte (los más conectados, 14.7 días de
  edad media; los menos, 8.8). Los más conectados son los que más se editan, y se editan sin verificar. Lo que envejece es lo que se edita
  sin mirarlo, esté cerca o lejos del centro. Con los cortes de hoy la relación casi desaparece (ρ = −0.22), así que no se saca ninguna regla.

## 3.2 Diferenciación: ¿qué tanto dicen lo mismo dos archivos?

`red-del-cerebro.py --integracion`, el 2026-10-12.

- De 1,007 párrafos de prosa de 280 caracteres o más (sin `MEMORIA`, que repite a propósito), **17 pares de archivos distintos se parecen 0.55 o más**
  (coseno TF-IDF). Siete son un compilado y su fuente, que es lo que significa compilar. Los otros diez no: `CONOCIMIENTO` con `MODELO`
  cuatro veces (la misma decisión contada una vez como evidencia y otra como esquema), `CATALOGOS` con `CONOCIMIENTO` dos (la corrección de D-404 contada
  en los dos), y cuatro sueltos.
- **Ningún par se contradice en sus cifras.** Se comparó la lista de números de cada párrafo y se leyeron a mano los diez pares de 0.5 o más donde difieren: eran detalles distintos
  de la misma decisión (por ejemplo, los días de cada nivel con y sin sus fechas), ninguno una cifra contraria. Esto cubre el hueco que `verificar-cerebro.py` no ve (dos
  archivos con la misma idea en palabras distintas), pero solo por vocabulario: una paráfrasis con otras palabras no aparece.
- No se deduplicó nada: cada copia lleva su contexto, y quitar una dejaría un puntero a cambio de una frase que se entiende sola.

## 3.3 Reentrada: lo que sale vuelve a entrar

`red-del-cerebro.py --reentrada` y la nota nueva del verificador, el 2026-10-12.

- **Un archivo compilado dice de qué sección sale** (`compilado:` o `derivado:` en su órgano), y con `git blame` se sabe cuándo cambió esa sección por
  última vez. Si fue después del `corte` del compilado, el verificador lo dice en una nota: el compilado **no oyó** el cambio. Cinco skills y `APRENDIZAJE`
  declaran fuente con sección.
- **Al encenderla señaló dos:** `erp-importacion` (`CONOCIMIENTO.md` §2, tocado ese día por la huella sin la unidad) y `erp-rediseno` (`CONOCIMIENTO.md` §8, tocado por las seis
  operaciones). Se releyeron y los dos ya decían lo corregido, así que cambió su `corte` y no su texto. El caso al revés, un skill que no lo dijera, sería la
  reentrada rota que la nota existe para ver.
- **Se probó rompiéndola:** tocar una línea de `CONOCIMIENTO.md` §17 hizo aparecer a `erp-cuantificador`; al restaurarla, desapareció.
- **El relevo.** De 185 commits que tocan `CONOCIMIENTO` o `MODELO`, solo 2 no tocan `INDICE` ni `ESTADO`: por ahí pasa casi todo, como en el tálamo.
- **Lo que no se mide:** el ritmo fino. Git da el orden de los commits y su día, no oscilaciones; hablar de coordinación temporal más allá de eso sería poner
  una metáfora donde no hay dato.
- **Límites de la nota:** la fecha es por día (un cambio de la fuente el mismo día del `corte` no se ve), solo mira las secciones que el compilado nombra, y los
  agentes no declaran fuente, así que lo que dicen del código no entra.

---

# 4. Lo que el cerebro sabe de sí mismo

| Qué vigila | Instrumento | Su límite |
|---|---|---|
| ¿Está vigente? | `corte` y `verificado` en cada archivo; `red-del-cerebro.py --vigencia` dice a quién releer | El corte se mueve al verificar, no al editar: el 2026-10-12 —antes de mover el de los archivos por donde pasa toda decisión— 20 de 36 habían cambiado después del suyo. Después de releer 13 contra su fuente (D-492) quedan 5, y los tres más grandes solo se releyeron en parte: lo dice su `verificado`, no su fecha. Que un archivo cite a otro que se movió no prueba que esté viejo: casi todos citan `CONOCIMIENTO` y `MODELO` |
| ¿Oyen los derivados a su fuente? | La nota de «archivos compilados» del verificador, por sección (D-493) | Fecha por día; no cubre a los agentes |
| ¿Se contradice? | El verificador (nueve comprobaciones) y el auditor | No ve dos archivos que dicen lo mismo con palabras distintas |
| ¿Dónde se equivocó? | `MEMORIA.md` §3 y las filas «Corrige» | Solo lo que alguien registró |
| ¿Qué está diseñado y qué probado? | Los símbolos de las pruebas de flujo: ✅ pasa · ⚠️ matices · 🔶 diseñado · ⛔ no se puede | Un símbolo no dice qué tan fuerte es la prueba |
| ¿Qué no se midió? | «Lo que esto no resuelve» y «lo que no se midió» | Depende de que quien escribe lo anote |
| ¿Qué se sabe que no se sabe? | `PENDIENTES-MEJORAS.md` | |
| ¿Quién lo revisa de afuera? | Proponer y esperar (`METODO.md` §3.2) | De las trece filas de `MEMORIA.md` §3, cinco las señaló quien revisaba y siete salieron de contrastar contra los datos: hacen falta los dos (`METODO.md` §4) |

---

# 5. Cómo se equivoca

Sobre los títulos de las filas «Corrige» de `MEMORIA.md` (clasificación propia, no exhaustiva):

| Familia | Ejemplos | Qué la atrapa |
|---|---|---|
| **La muestra era parcial**: un archivo incompleto, un mes, una sola fuente, una llave que no era única, una clave sumada en todo el capítulo | D-305, D-358, D-365, D-375, D-377 | Correr con toda la muestra (`METODO.md` §5, punto 3: sospechar del alcance antes que del dato) |
| **Se generalizó desde un caso**, o se validó con algo que el dato no prometía | D-314, D-324, D-388, D-419 a D-422, D-488 | Una segunda fuente independiente (`METODO.md` §1.4) |
| **Error propio de cálculo o de lectura**: un cruce que duplicaba filas, un conteo, una holgura sin el «+ 1», días naturales por hábiles | D-309, D-415, D-416, D-443, D-445, D-448 | Contrastar contra un total conocido (`METODO.md` §1.1) |
| **No se leyó lo ya escrito** | D-347, D-405, D-490 | Buscar antes de proponer (`METODO.md` §5, punto 1) |
| **La cifra viajó sin su fuente**: «seis de ocho», «22 casos», $132,364.24, «cinco compuestos»; una referencia que resuelve y apunta a otra cosa | D-492 | Volver a sacarla del dato (`METODO.md` §1.1) y leer el título del destino junto a la frase (`METODO.md` §3.7) |

**Las correcciones vienen en cadenas**: D-376 → D-377 → D-378 → D-379; D-414 → D-415 → D-416;
D-419 → D-420 → D-421 y D-422; D-442 → D-443 → D-445. Cada eslabón corrige al anterior con más
datos: la primera lectura salió de una parte y el error se arrastra hasta que la muestra se
completa. De ahí la regla: **si la primera lectura salió de una parte, se corre con todo antes de
escribirla como regla.**

---

# 6. Lo que sabe que no sabe

Está dicho en su lugar y aquí solo se señala, para que no se tome por completo lo que no lo es:

- **Diseñado sin caso real que lo ejerza**: las etapas 🔶 de las pruebas de flujo.
- **Las tablas de OPUS que no están** (materiales, trabajos, mano de obra, fletes, conceptos), y la
  doceava ingeniería de `ALAMO 18`, la azotea (`MEMORIA.md` D-472, D-488).
- **Los cuatro archivos retirados** y lo que pudieron contener (`MEMORIA.md` D-490).
- **Lo que no se pudo volver a sacar** (D-492): las cifras de cimentación de `RAZONAMIENTO.md`, las 11 filas del filtro por `Ingenieria ERP`, el 1.085 y los conteos de `DICCIONARIO-DATOS.md` §3. Están en el `verificado` de su archivo.
- **Lo que ningún instrumento de arriba puede ver**: un tercer hecho perdido que nadie sabe que
  existió, y dos archivos que se contradicen sin repetir una sola cifra.

---

# 7. Qué se hace con esto

1. **El espacio de trabajo es pequeño y se lee primero.** `ESTADO.md` e `INDICE.md` dicen cómo está
   hoy; lo que pasó va a `MEMORIA.md`. El verificador rechaza una fila de más de 2,500 caracteres.
2. **Quien actúa lee el foco antes.** `gravity`, `arquitecto-erp` y `constructor-erp` abren con
   «El foco» de `ESTADO.md`. Quien solo percibe o comprueba no lo necesita.
3. **Un enlace lleva identificadores, no estados.** `B-82` sí. «Sigue abierto» fuera de
   `4-direccion/` solo con la decisión que lo fecha («dicho antes de D-439»).
4. **El corte se mueve cuando se verifica**, no cuando se edita. La nota del verificador dice
   cuántos archivos van atrasados; leerla es parte de retomar.
5. **Un compilado dice de qué sección sale** (`compilado:` o `derivado:`), para que el verificador pueda decir cuándo dejó de oír.
6. **Una cifra que vive en dos sitios necesita guardián.** Si no se puede guardar mecánicamente, se
   dice cuál es y quién la cambia (la tabla de §2).

**Cómo se vuelve a medir:** `python3 2-operacion/red-del-cerebro.py .` para la red y
`python3 2-operacion/verificar-cerebro.py .` para el resto.
