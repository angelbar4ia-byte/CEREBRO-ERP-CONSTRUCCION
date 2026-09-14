# PRIORIDADES

```
órgano:     atención selectiva
capa:       IV — Dirección
pregunta:   ¿en qué se gasta el hiperenfoque?
tiempo:     esto primero
corte:      2026-09-12
derivado:   ESTADO.md · PENDIENTES-MEJORAS.md · PROPUESTA-CUATRO-MODULOS.md
```

> **El criterio, no la lista.** La cola de pendientes vive en
> `PENDIENTES-MEJORAS.md`; el orden vigente en `ESTADO.md`. Aquí está **por qué ese
> orden y no otro** — que es lo único que hoy no estaba escrito en ningún lado.
>
> Un cerebro que asigna el 100% de su capacidad a un nodo necesita elegir bien el
> nodo. No tiene forma de notar desde adentro que eligió mal.

---

# 1. El criterio

Se razonó una sola vez, para el factorizador — *«el más chico y el que más
desbloquea»* — y nunca se generalizó. Generalizado:

```
prioridad  =  desbloqueo  ÷  costo         ajustado por dos frenos
```

| Eje | Pregunta | Alto |
|---|---|---|
| **Desbloqueo** | ¿Cuántas otras cosas esperan a esta? | El factorizador: tres módulos dependen de él |
| **Costo** | ¿Cuánto trabajo y cuántas decisiones cuesta? | El cuantificador: geometría, planos, versiones |

**Freno 1 — ¿está decidido?** Lo que requiere decisión ajena no se prioriza, se
escala. Sube a la cola sólo cuando la decisión existe.

**Freno 2 — ¿qué cuesta deshacerlo?** Lo que arrastra datos históricos se decide
antes que lo que se arregla con una migración barata. Es el principio de fondo
aplicado al orden del trabajo: *mientras nada dependa, se corrige; en cuanto algo
depende, se agrega encima.*

> **El segundo freno invierte el criterio a veces, y hay que dejarlo.** Una
> decisión barata hoy y carísima en dos meses sube por encima de algo con más
> desbloqueo. Es lo que pasa con los montos como string en la API.

---

# 2. Las cuatro casillas

| | Costo bajo | Costo alto |
|---|---|---|
| **Desbloqueo alto** | **Ahora.** Sin discusión | Planear. Partir en trozos con invariante propia |
| **Desbloqueo bajo** | Se hace mientras se pasa por ahí | **No se hace.** Queda en la cola y se revisa al corte |

La casilla que hace daño es la de abajo a la derecha: caro y no desbloquea nada.
Es donde el hiperenfoque se pierde sin que nadie lo note, porque desde adentro se
siente igual de productivo.

---

# 3. Condición de paro

**El hiperenfoque termina cuando la invariante da, no cuando el trabajo parece
correcto.** Toda tarea que entra a la cola declara contra qué cifra de
`INVARIANTES.md` se comprueba.

Si una tarea no puede declarar su cifra, no está lista para trabajarse: **está
lista para discutirse.** Es el mismo corte entre `PENDIENTES` (lo abierto) y lo
accionable.

---

# 4. Cuándo se reordena

Tres disparadores, y sólo tres:

| Disparador | Qué obliga |
|---|---|
| Se aprueba una decisión pendiente | Lo que bloqueaba entra a la cola |
| Llegan datos nuevos | Puede habilitar algo caro o invalidar algo hecho |
| Cambia `ESTADO.md` | Se relee la cola contra el corte nuevo |

> **Lo que no reordena: que algo se sienta más interesante.** La inercia cognitiva
> es real y sirve —terminar lo empezado vale—, pero no es criterio de prioridad.

---

# 5. La cola vigente

Tomada de `ESTADO.md`, con su casilla. **No se duplica aquí: si difieren, manda
`ESTADO.md`.**

| # | Qué | Costo | Desbloqueo | Nota |
|---|---|---|---|---|
| 1 | `INVARIANTES.md` como archivo | Bajo | **Alto** | Ya hecho. Era la condición de paro de todo lo demás |
| 2 | Montos como string en la API | **Muy bajo** | Medio | **Freno 2:** hoy es una línea; después de generar clientes, son veinte archivos |
| 3 | Salidas de almacén de `ALAMO 18` | Medio | **Alto** | Cierra prototipo → ingeniería → ejecutado. P-38 |
| 4 | `MODELO.md` a implementación | Alto | **Alto** | Tipos, índices, motor. Partir en trozos |
| 5 | Las 16 decisiones de los cuatro módulos | Bajo (decidir) | Alto | Factorizador primero. **Releer la propuesta contra el estado actual** |
| 6 | Clasificar a mano el 8% de conceptos | Medio | Bajo | El 92% ya sale derivado |
| 7 | Los 77 de `PENDIENTES-MEJORAS.md` | Variable | Variable | Se clasifican con §2 al tocarlos |
| 8 | Las 6 ideas de `IDEAS.md` | Alto | Bajo | Sin diseñar. No entran hasta que algo las pida |

---

# 6. Lo que nunca se pospone

Independiente del criterio, porque no compite con nada:

- **Una invariante que falla.** Se reporta el mismo día. No se acumula.
- **Una contradicción entre dos archivos.** Ya pasó dos veces y las dos se detectaron
  tarde. Un hecho que vive en dos lugares empieza a mentir solo.
- **Un hecho verificado sin registrar.** Lo que no se escribe en el corte, se pierde
  entre sesiones.
