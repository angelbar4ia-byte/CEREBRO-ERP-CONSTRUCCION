---
name: erp-cuantificador
description: Cuantificación gráfica en el ERP de construcción — trazar sobre el plano para producir la cantidad de un concepto, y las siete reglas de dominio (de 29 funciones inventariadas) que sí necesitan verificarse contra datos reales. Usar al implementar TRAZO/ENLACE_CUANTIFICACION, al decidir si una función del cuantificador es infraestructura o dominio, al calcular volumen/peso/superficie inclinada/taludes desde una medida gráfica, o al asignar quién puede trazar. NO cubre las funciones de PostGIS en sí —ST_Intersection, ST_Union, etc.— eso es infraestructura, ver `IDEAS.md` §2 y D-182.
---

```
órgano:     vía mielinizada — cuantificador
capa:       II — Operación
pregunta:   ¿de dónde sale la cantidad cuando se traza sobre el plano?
tiempo:     se hace así
corte:      2026-09-18
compilado:  `CONOCIMIENTO.md` §17 — no se escribe a mano
```

> **Satélite.** Carga el skill base `erp-construccion` primero.

---

## 0. Qué es

**Trazar sobre el plano, al estilo PlanSwift o Navisworks, para producir la
cantidad de un concepto que ya existe en el árbol.**

```
TRAZO      la geometría sobre el plano      un polígono, una línea, un punto
MEDIDA     lo que se deriva de él           área, perímetro, longitud, conteo
CANTIDAD   medida × factor → al concepto    área → piso  ·  perímetro → zoclo
```

**No inventa estructura.** Consume el árbol de presupuesto con sus matrices y
compuestos — solo se dedica a trazar. Si hace falta un concepto que no
existe, se crea, igual que en cualquier otro punto del árbol.

---

## 1. Un trazo, varios enlaces — nunca se copia

Un solo polígono alimenta varios conceptos a la vez: el área de una recámara
da el piso y el perímetro da el zoclo. La cantidad **no se copia, se enlaza**
— si se corrige el trazo, la cantidad se actualiza sola.

**Cuarenta trabes no son mecanismo nuevo:** son cuarenta filas de `TRAZO`,
cada una con su propio enlace. Si el presupuesto quiere una sola línea, los
enlaces apuntan al mismo nodo y la cantidad se suma; si quiere cuarenta
líneas, cada trazo enlaza al suyo. **La agregación es del árbol del
presupuesto, no del cuantificador.**

**Dos enlaces vigentes de la misma instancia física no pueden coexistir** —
por precedencia (`IFC > DWG > PDF`) el más reciente reemplaza al anterior, que
se conserva como evidencia y nunca se borra ni se suma. Instancias distintas
sí suman entre sí; la misma instancia medida dos veces no.

---

## 2. El cuantificador NO se tipa

No hay «cuantificador de PU», «paramétrico» ni «alzado». El modo ya está
declarado en el nodo que recibe. Lo que sí se tipa es **el enlace**: qué
medida toma y con qué factor — así el mismo polígono alimenta los tres tipos
de nodo a la vez, cada uno tomando lo que le sirve.

---

## 3. Veintidós de las 29 funciones inventariadas son infraestructura

Calibrar escala, reparar geometría rota, medir un área, cruzar capas, agrupar
polígonos — es PostGIS genérico, sin regla de construcción detrás. **El
recorrido es infraestructura; la regla de qué suma a qué es dominio.** No se
implementan como conocimiento de dominio — son función de PostGIS, se llaman
donde el motor de cálculo las necesite, documentadas en el código, no aquí.

---

## 4. Las siete funciones de dominio

| Función | Cómo se resuelve |
|---|---|
| Volumen | `medida`=área × `factor`=espesor → `M3`. Nada nuevo |
| Peso desde longitud | `medida`=longitud × `factor`=peso lineal por diámetro → `KG` |
| Superficie inclinada | `medida`=área (proyección) × `factor`=corrección por pendiente |
| Conteo por patrón | `medida`=conteo, factor 1 — cambia cómo se detecta, no qué se mide |
| Paramétrico por fórmula | No es del cuantificador: ya resuelto por el paramétrico |
| **Cubicación con taludes** | **No es medida×factor** — dos áreas + una longitud, combinadas por `formula_personalizada`: `V = L × (A1+A2)/2` |
| Ejes y niveles | Bloqueado — depende de `FRENTE`, sin uso operativo todavía |

**Solo taludes pide el escape hatch; las otras cuatro que sí calzan no piden
campo nuevo.** Ninguna de las siete está verificada contra un caso real de
obra con taludes — se documentan como fórmula estándar, no como dato medido.

---

## 5. Si el plano cambia

Las cantidades trazadas sobre la versión anterior **quedan marcadas para
revisión**, no se recalculan solas — mismo principio que «detectar no
necesita permiso, corregir sí».

**Dos fuentes que discrepan mucho no se promedian ni se eligen solas:** es
propuesta con evidencia, no corrección automática.

---

## 6. Quién traza

`trazar` y `aprobar_trazo` son funciones atómicas de roles, no una tabla de
gobierno por obra:

```
trazar          →  Costos · Control · Residente · Supervisor   (no Cotizador)
aprobar_trazo   →  Control
```

Residente y Supervisor trazan igual que Costos y Control — la diferencia es
**para qué**, no de permiso: cuantifican para sustentar una orden de cambio,
que ya pasa por su propia aprobación antes de tocar un nodo contratado.
**Visualizar el estado de cuantificación no es una función atómica** — es
lectura, abierta a quien tiene acceso a la obra.

**Anotar el plano** (`anotar_plano`, Residente/Supervisor) es distinto de
trazar: una nota nunca alimenta una cantidad. Si algún día necesita generarla,
no se amplía la nota — se convierte en trazo.

---

## 7. Los errores que este skill previene

1. Guardar solo la cantidad en vez del trazo — obliga a volver a medir cada
   vez que algo cambia.
2. Tratar cuarenta instancias del mismo elemento como si necesitaran un
   mecanismo distinto al de una sola.
3. Sumar dos enlaces vigentes de la misma instancia física medida dos veces
   en dos planos.
4. Tipar el cuantificador por modo de precio — la distinción ya vive en el
   nodo, duplicarla las desincroniza.
5. Implementar las funciones de PostGIS como si fueran regla de dominio
   verificada — son infraestructura.
6. Inventar un mecanismo nuevo para volumen, peso o superficie inclinada
   cuando `medida × factor` ya alcanza.
7. Resolver taludes con un campo nuevo en vez de `formula_personalizada`.
8. Forzar ejes y niveles sin que `FRENTE` tenga todavía un consumidor real.
9. Recalcular sola una cantidad trazada cuando el plano cambia de versión, en
   vez de marcarla para revisión.
10. Promediar o elegir sola entre dos fuentes que discrepan — eso es
    propuesta con evidencia, no corrección automática.
11. Crear una tabla de gobierno por obra para "quién traza" en vez de asignar
    la función atómica que ya existía.
12. Confundir `anotar_plano` con `trazar` — la nota nunca genera cantidad.
