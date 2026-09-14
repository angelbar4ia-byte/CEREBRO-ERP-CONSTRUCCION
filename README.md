# Cerebro — ERP de construcción

Gobernanza del ERP: qué es verdad, cómo se piensa, qué se decidió y qué falta.
**No es documentación del código: es la fuente de la que el código se deriva.**

```
INDICE.md          ← empezar aquí. Dice dónde va cada cosa
├── 1-mundo/       Es así        CONOCIMIENTO · CATALOGOS · MODELO · LENGUAJE · GLOSARIO · DICCIONARIO-DATOS
├── 2-operacion/   Se hace así   METODO · INVARIANTES · ESCALABILIDAD · skills/ · agentes/
├── 3-historia/    Fue así       MEMORIA · CASO-TRABAJADO · APRENDIZAJE · PRUEBA-*
└── 4-direccion/   Vamos aquí    ESTADO · PENDIENTES · PRIORIDADES · IDEAS · PROPUESTA-*
```

## Cómo retomar

1. `4-direccion/ESTADO.md` — dónde vamos y qué está en curso
2. `2-operacion/METODO.md` — cómo se piensa aquí
3. `INDICE.md` — dónde va cada cosa
4. `3-historia/MEMORIA.md` §2 — **lo ya descartado**, antes de proponer nada

## Las tres reglas que gobiernan el repo

**Un hecho vive en un archivo; los demás lo referencian.** Si algo aparece explicado
en dos lugares, tarde o temprano se separan y uno miente.

**Cada archivo numera desde 1**, y toda referencia cruzada lleva su archivo —
`` `CONOCIMIENTO.md` §11.9 ``, no `§11.9`. Así agregar una sección en un archivo no
mueve nada en los demás.

**Nada entra sin su evidencia.** Una regla que no dice cómo se verificó es una
creencia con buena redacción.

## El verificador

```bash
python3 2-operacion/verificar-cerebro.py .
```

Nueve comprobaciones mecánicas: bloque de órgano completo, capa igual a la carpeta,
fechas de corte, referencias que resuelven, secciones que existen, conteos declarados
contra reales, cifras de control en su fuente, tablas bien formadas y párrafos
duplicados entre archivos.

**Corre solo en cada push** (`.github/workflows/verificar.yml`). Sale con código 1 si
hay fallas.

> Lo que el verificador **no** ve: dos archivos que dicen lo mismo con palabras
> distintas, y una referencia que resuelve a la sección equivocada. Eso sigue siendo
> trabajo de lectura — ver `2-operacion/agentes/auditor-erp.md`.

## Los agentes

`gravity` orquesta y entrega plan de ruta · `arquitecto` diseña · `constructor`
construye · `migrador` lee sistemas ajenos · `auditor` comprueba. Más `gravity-obra`,
el orquestador interno del producto, diseñado y no construido.

## Convenciones al contribuir

- **Los skills se compilan desde `CONOCIMIENTO.md`, no se escriben a mano.**
- Una decisión nueva va a `3-historia/MEMORIA.md` con su razón, incluida la opción
  descartada.
- Un pendiente resuelto no se borra: se marca resuelto con cómo se resolvió.
- Ante una contradicción: **parar, preguntar, proponer** — `METODO.md` §3.5.
