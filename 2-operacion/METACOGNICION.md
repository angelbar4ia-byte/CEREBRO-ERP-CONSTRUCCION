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
queda si produce una prueba que pueda fallar. Estas tres la producen:

| Idea | Qué dice en neurociencia | Qué se mide aquí |
|---|---|---|
| **Espacio de trabajo global** (Baars; Dehaene y Changeux) | Procesos especializados compiten por un escenario de capacidad limitada; lo que gana se difunde a todo el sistema —en el cerebro, a redes frontoparietales— en una «ignición» | Qué se lee primero, por dónde pasa todo cambio y si les llega a quienes actúan |
| **Conectividad estructural y funcional** | La anatomía (qué neurona se conecta con cuál) no es lo mismo que la estadística (qué se activa junto) | Referencias escritas entre archivos, contra archivos que cambian en los mismos commits |
| **Metacognición** (Flavell; Fleming) | Saber qué se sabe, con qué confianza, y dónde se falla | Vigencia, errores ya cometidos e ignorancia conocida |

> **Lo que no se afirma.** Ni que este cerebro sea consciente, ni que el espacio de trabajo
> global sea la teoría correcta —es una entre varias, junto a la de información integrada, las
> de orden superior y el procesamiento recurrente—. Se toma su arquitectura, no su metafísica.

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

Medido con `python3 2-operacion/red-del-cerebro.py .` el 2026-10-12.

- **Estructural.** 37 archivos y 293 conexiones distintas. Nadie queda sin que lo nombren, nadie
  sin nombrar a otro, y `INDICE` y `README` llegan a los 37. El camino medio entre dos archivos
  es de 1.66 saltos y el agrupamiento 0.75; con 37 nodos eso es lo esperable de una red
  tan densa, y no se saca de ahí ninguna conclusión.
- **Concentradores.** `CONOCIMIENTO` (lo nombran 28 archivos) y `MODELO` (23). `METODO` lo
  nombran 18 y él nombra 2: es la identidad, un receptor. `MEMORIA` es el integrador (la nombran 16 y
  nombra a 28).
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

---

# 4. Lo que el cerebro sabe de sí mismo

| Qué vigila | Instrumento | Su límite |
|---|---|---|
| ¿Está vigente? | `corte` y `verificado` en cada archivo | El corte se mueve al verificar, no al editar: el 2026-10-12 —antes de mover el de los archivos por donde pasa toda decisión— 20 de 36 habían cambiado después del suyo, y el verificador lo dice en una nota |
| ¿Se contradice? | El verificador (nueve comprobaciones) y el auditor | No ve dos archivos que dicen lo mismo con palabras distintas |
| ¿Dónde se equivocó? | `MEMORIA.md` §3 y las filas «Corrige» | Solo lo que alguien registró |
| ¿Qué está diseñado y qué probado? | Los símbolos de las pruebas de flujo: ✅ pasa · ⚠️ matices · 🔶 diseñado · ⛔ no se puede | Un símbolo no dice qué tan fuerte es la prueba |
| ¿Qué no se midió? | «Lo que esto no resuelve» y «lo que no se midió» | Depende de que quien escribe lo anote |
| ¿Qué se sabe que no se sabe? | `PENDIENTES-MEJORAS.md` | |
| ¿Quién lo revisa de afuera? | Proponer y esperar (`METODO.md` §3.2) | El mecanismo que más errores atrapó: `METODO.md` §4 |

---

# 5. Cómo se equivoca

Sobre los títulos de las filas «Corrige» de `MEMORIA.md` (clasificación propia, no exhaustiva):

| Familia | Ejemplos | Qué la atrapa |
|---|---|---|
| **La muestra era parcial**: un archivo incompleto, un mes, una sola fuente, una llave que no era única, una clave sumada en todo el capítulo | D-305, D-358, D-365, D-375, D-377 | Correr con toda la muestra (`METODO.md` §5.3: sospechar del alcance antes que del dato) |
| **Se generalizó desde un caso**, o se validó con algo que el dato no prometía | D-314, D-324, D-388, D-419 a D-422, D-488 | Una segunda fuente independiente (`METODO.md` §1.4) |
| **Error propio de cálculo o de lectura**: un cruce que duplicaba filas, un conteo, una holgura sin el «+ 1», días naturales por hábiles | D-309, D-415, D-416, D-443, D-445, D-448 | Contrastar contra un total conocido (`METODO.md` §1.1) |
| **No se leyó lo ya escrito** | D-347, D-405, D-490 | Buscar antes de proponer (`METODO.md` §5.1) |

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
5. **Una cifra que vive en dos sitios necesita guardián.** Si no se puede guardar mecánicamente, se
   dice cuál es y quién la cambia (la tabla de §2).

**Cómo se vuelve a medir:** `python3 2-operacion/red-del-cerebro.py .` para la red y
`python3 2-operacion/verificar-cerebro.py .` para el resto.
