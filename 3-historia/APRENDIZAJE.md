# APRENDIZAJE

```
órgano:     lazo hebbiano
capa:       III — Historia
pregunta:   ¿cómo lo aprobado cambia lo que el sistema cree?
tiempo:     se aprendió así
corte:      2026-10-12
derivado:   `CONOCIMIENTO.md` §14 · `MEMORIA.md` · `MODELO.md` §5
verificado: §7 releído contra `0010_bandeja_de_propuestas.sql` y `propuestas.py` el 2026-10-12; §1 a §6 son diseño, sin código que contrastar
```

> **El lazo que faltaba.** Se menciona tres veces en el conocimiento —*«el corpus
> del agente son las propuestas aprobadas»*— y nunca se diseñó. La prueba de que
> faltaba está en el propio archivo: el conocimiento remitía a *«el ciclo del agente
> que aprende de lo decidido»* señalando una sección que hablaba de otra cosa —la
> matriz a partir de la descripción, hoy `IDEAS.md` §1—.
> **La referencia apuntaba a un lugar que nunca se escribió. Es éste.**

---

# 1. Qué no es

| No es | Eso vive en |
|---|---|
| Registrar qué se decidió | `MEMORIA.md` |
| Registrar qué se sugirió | La tabla `PROPUESTA` (`MODELO.md` §5) |
| Reentrenar un modelo | **Nada aquí entrena nada.** Es indexación de casos |

El aprendizaje es **el tramo entre una propuesta resuelta y el conocimiento
cambiado**. Hoy ese tramo lo hace una persona, a mano, y se pierde si nadie escribe.

---

# 2. El ciclo, completo

```
1. El sistema detecta            sin permiso — masa a masa, volumen a volumen
2. Propone con evidencia         estado: pendiente
3. Alguien resuelve              aprobada · rechazada
4. Se indexa el caso             ← ESTE ARCHIVO. Lo que antes se perdía
5. Cambia lo que el sistema cree
```

El paso 5 se bifurca, y la bifurcación importa:

| Qué cambió | A dónde va |
|---|---|
| Un dato concreto | Se aplica y ya. No es aprendizaje |
| **Una regla del sistema** | `CONOCIMIENTO.md` |
| **Por qué se decidió así** | `MEMORIA.md` |
| **Una regla al construir** | `erp-construccion.md` — derivada, nunca inventada |
| **Una cifra de control** | `INVARIANTES.md` |

> Una propuesta aprobada que no cambia ninguno de los cinco **no era conocimiento:
> era una corrección**. Distinguirlo evita inflar el cerebro con ruido.

---

# 3. El rechazo es la mitad del corpus

Ya está decidido para el diccionario y para las propuestas, y aquí es donde cobra
efecto:

> **Un agente que aprende sólo de lo aprobado reproduce indefinidamente lo que ya
> se rechazó.**

Un rechazo enseña dos cosas que una aprobación no enseña: **dónde está el límite**,
y **cuál es la razón** — que casi nunca es «estaba mal», sino «no aplica aquí».

Por eso el corpus son las propuestas **resueltas**, no las aprobadas. Doce ideas
razonables ya evaluadas y descartadas viven en `MEMORIA.md` §2, y es lo primero
que se lee antes de proponer cualquier cosa.

---

# 4. Analogía, no estadística

El sistema propone por parecido a casos resueltos, **con el caso a la vista**:

```
Propongo el factor 1.085
porque en ACA-01010 se aprobó el mismo factor, por la misma razón,
el 2026-09-04.
```

No *«el modelo sugiere 1.085»*. La diferencia es que lo primero se puede rechazar
con criterio y lo segundo sólo por desconfianza.

> **Una propuesta sin evidencia es una orden disfrazada.** Un caso indexado con su
> resolución **es** la evidencia. Por eso el corpus no necesita ser opaco.

---

# 5. Lo que el aprendizaje no puede tocar

**El lazo entra al cerebro sólo por la bandeja de propuestas.**

| Puede | No puede |
|---|---|
| Leer todas las capas | **Escribir en Capa I o III sin aprobación** |
| Indexar lo resuelto | Reabrir lo rechazado sin evidencia nueva |
| Proponer un cambio de regla | Aplicarlo |

> Un cerebro que reescribe su propia memoria no aprende: **confabula.** Es la misma
> razón por la que la capa CARGADO es inmutable — si se pierde lo que llegó, se
> pierde la respuesta a *¿esto lo trajimos o lo hicimos nosotros?*

Y hay un caso especial: **una propuesta rechazada que vuelve a proponerse** sólo
entra con evidencia que no existía antes. Si no, el lazo se vuelve insistencia.

---

# 6. Métricas del propio lazo

Miden si el aprendizaje funciona. Van a `INVARIANTES.md` cuando haya datos:

| Métrica | Qué dice |
|---|---|
| % de propuestas resueltas contra pendientes | Si nadie resuelve, el lazo está cortado |
| % rechazadas | Muy alto: el sistema propone mal. **Muy bajo: nadie está revisando de verdad** |
| Reproposiciones de algo ya rechazado | Debería ser cero. Si no, el corpus no se está consultando |

---

# 7. Estado

**Diseñado; la mitad de abajo ya está construida y la de arriba no.** Cuando esto se escribió faltaba la tabla
`PROPUESTA`. Desde D-485 existe (`database/migraciones/0010_bandeja_de_propuestas.sql` y
`backend/core/propuestas.py`), y ya hace dos cosas que este archivo pide: **conserva lo rechazado con su nota** y
**no deja volver a proponer lo rechazado** si la evidencia es la misma (`RechazadaAntes`). Lo que no existe es el
paso 4 —indexar el caso resuelto— ni la búsqueda por parecido de §4: la bandeja guarda los casos, nadie los consulta
todavía. Y con D-487 no se construye.

Lo que sí aplica desde hoy, sin código: **cuando se resuelve algo en sesión, el
paso 4 se escribe.** Es lo que hacía falta para que la referencia rota dejara de
apuntar al vacío.

---

# 8. Notas de casos resueltos en sesión

> Nota, no decisión: no cambia nada de lo que el cerebro sabe; solo deja el caso
> para quien lo busque (paso 4, §7).

**2026-11-03 · Una prueba de concurrencia de la infra falla de forma intermitente en CI y no depende del contenido del cerebro.**
En el PR de las decisiones D-607 a D-616 (cuatro archivos `.md`), `pruebas (infra)` falló dos veces seguidas con
`test_dos_procesos_que_ven_lo_mismo_a_la_vez_no_la_repiten_ni_pierden_cuentas`
(`backend/infra/tests/test_postgres_bandeja.py`, línea 139): esperaba `(1, 30)` en `alerta` y obtuvo `(1, 15)`, es decir,
una de las dos cuentas de `veces_vista` se perdió. Las otras tres comprobaciones (`cerebro`, `pruebas (api)`,
`pruebas (core)`) pasaron; `verificar` solo resume las anteriores. El mismo commit de `main` ya había fallado y pasado
esa misma prueba el 2026-11-02, así que la carrera es anterior a este PR. Lo que se hizo: la fusión de documentación no
esperó a esa prueba. Lo que queda abierto: revisar si la actualización de `veces_vista` pierde cuentas cuando dos procesos
ven la misma alerta a la vez (es lo que la prueba dice cuidar), antes de que la bandeja se use con carga real.
