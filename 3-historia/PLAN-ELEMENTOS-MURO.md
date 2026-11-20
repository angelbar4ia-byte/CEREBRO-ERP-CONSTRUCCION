# Plan de registro y construcción: elementos de muro, Artefacto, Paramétrico y Cuantificador

```
órgano:     plan de trabajo de los elementos de muro
capa:       III — Historia
pregunta:   ¿en qué orden se registra y se construye lo diseñado en el mockup?
tiempo:     se planeó así
corte:      2026-11-20
verificado: mockup interactivo publicado y probado en Chromium; su especificación completa está en 3-historia/mockups/muros-parametricos.especificacion.json
```

> La decisión está en **D-647** y **D-648** (segunda parte: muros de piedra, vistas y ubicación en el Cuantificador). El mockup sigue abierto: este plan fija el orden para avanzar sin que después pese más; cada fase cierra con su PR y se ajusta si el mockup cambia. Lo que no está decidido está en `preguntas_abiertas` de la especificación (Q17 a Q28).

## 0. Cómo se trabaja cada fase

1. Una rama y un PR por fase, chicos y revisables. El PR se mezcla solo con orden del usuario.
2. Cada PR del backend lleva sus pruebas (unitarias, integración con Postgres y, si cambia la pantalla, una de Playwright) y su migración numerada a partir de la 0127.
3. Tras el push, la sesión se suscribe al PR y atiende cualquier falla de CI o comentario.
4. Al cerrar la fase se anota en MEMORIA lo construido (como D-646 con D-645).

## 1. Cerebro (este PR)

| Paso | Qué | Dónde |
|---|---|---|
| 1.1 | Decisión D-647 y conteos | `3-historia/MEMORIA.md`, `INDICE.md`, `4-direccion/ESTADO.md` |
| 1.2 | Especificación del mockup, para construir sin volver a pedirla | `3-historia/mockups/muros-parametricos.especificacion.json` |
| 1.3 | Este plan | `3-historia/PLAN-ELEMENTOS-MURO.md` |
| 1.4 | Cuando el mockup cierre: volcar `reglas_de_elementos` a MODELO y las familias de insumos a CATALOGOS | `1-mundo/` |

## 2. Backend y app: orden de construcción

| Fase | Qué se construye | Depende de | Pruebas clave |
|---|---|---|---|
| A | **Biblioteca**: `categoria` y `subcategoria` en el elemento, firma anti-duplicados (categoría, subcategoría, medidas, armado, cimbra, materiales), límite de posición por subcategoría | 0120 (versiones) | dos elementos idénticos se rechazan; cerramiento y desplante idénticos conviven |
| B | **Receta y cortes**: armex y varillas con traslape, anillos por zonas (pza y kg), consumos de cimbra por ml, regla de cortes con módulos y puntas; drivers nuevos (traslapes, puntas, tolerancia, máximo de piezas) | A | tabla de cortes del mockup (2.00 a 9.00 m) y contraste con EST-02110, EST-02310 y EST-02320 |
| C | **Conceptos del elemento por contexto**: `elemento_concepto` con contextos, escalones por altura (`alto_hasta_m`) y concepto nuevo pendiente de autorizar | B | cada parte la toma un solo concepto por contexto; alto sin escalón avisa |
| D | **Insumos permitidos por tipo de elemento** (familias, nueva familia Cimbra) y comparación contra el concepto del catálogo | C | un insumo de otra familia se rechaza |
| E | **Artefacto y plantillas**: tipo de muro, ubicación con caras A/B, nivel, partes de altura, plantilla por validar/validada | A, C | el cuerpo se divide alrededor de cada cadena |
| F | **Paramétrico**: drivers global, por obra y mixto; enlace de ranuras con conceptos del Presupuesto | B | un driver ajustable de obra cambia solo esa obra |
| G | **Cuantificador**: elegir el elemento, tomar altura y nivel del muro, descontar su área y alimentar los conceptos del contexto; reconciliar `app.cantidad_conversion` y `GestionarVanos` (altura 2.6 a driver 3.00) | C, E | 3.00 m en planta baja da EST-10010 y EST-02110; en barda, un solo concepto |
| H | **Bastones** (por longitud de trazo) | B | piezas, varillas y kg del mockup |
| I | **Roles y permisos**: Costos propone, Control de obra autoriza, versión al autorizar | C | Control edita sin pedir autorización |
| K | **Muros de piedra** (contención MCT-01010 y cimentación CIM-01010): sección por altura, dentellón, dren dentro del concepto, tubería en piezas, vistas; **primera prueba en producción: solo MCT-01010** con las pestañas Elementos, Artefacto y Paramétrico del panel del Cuantificador | A, B, C | las tablas del Cuadro 1 y el 1.5:1 del mockup; ml de tubería y piezas |
| J | **Migración de `muro_tipo`** (pretil, barda, sillar) y de los muros existentes | E | los muros anteriores se leen igual |

## 3. Riesgos y lo que falta decidir

- Puntas de 40 diámetros y 50 cm en armex: confirmar con el estructurista (Q22).
- Conceptos EJ-420 a EJ-425 (entrepiso, azotea, pretil y barda) son del mockup: Control de obra los autoriza y se confirma su composición (Q26).
- Escalones de más de 6.00 m: se diseñan después (Q27).
- Mano de obra por tipo de actividad y bastón: preguntas Q19 y Q28.
- El armex no tiene peso en el catálogo: el kg de acero con armex queda sin dato.

## 4. Estado de construcción al cierre de la Ola 5 (2026-11-20)

Las decisiones están en **D-649** a **D-658**. Todo lo de la tabla se construyó en la app (`control-avance`) con sus pruebas y la prueba de punta a punta `zz-flujo-completo.spec.ts`; el mockup ya no es la fuente: la fuente es la app.

| Fase | Estado | Dónde quedó |
|---|---|---|
| A Biblioteca | construida | migración 0127 |
| B Receta y cortes | construida | dominio puro `receta_acero` |
| C Conceptos por contexto | construida | migración 0128; el nivel es `nivel.numero_de_nivel` explícito (0141, D-656) |
| D Insumos por tipo | construida | migración 0129 |
| E Artefacto y plantillas | construida, con plantillas por prototipo y «muros y cadena» | migraciones 0133 y 0136 |
| F Paramétrico | construida; el plano ya no lee `altura_estandar` (D-653) | migración 0134; cambios de driver con autorización (0141) |
| G Cuantificador | construida: elemento colocado, tomas, zonas de losa y fachada por bandas | migraciones 0135, 0137 y 0138 |
| H Bastones | construida con gancho; faltan E2, E3 y E4 | sin migración |
| I Roles y versiones | construida | migraciones 0130 a 0132 |
| J Migración de `muro_tipo` | construida | migración 0133 |
| K Muros de piedra | construida (MCT-01010 y CIM-01010) | sin migración |

**Pendiente (todo con su porqué en D-658):** losa fase 2 y relleno; escaleras y cimentación; capa «espacio»; vanos y domos como elementos; muros de concreto y zapata corrida (Q104 a Q109); block hueco y cantera rosa; fachada que alimente conceptos; E2, E3 y E4 de bastones; D2, D3, D4, D9 y D13; T-2 con Costos; los supuestos del sillar (junta de 2 cm, que el catálogo no trae, y desperdicio único de pieza y mezcla de 5 %, por confirmar); unicidad de `numero_de_nivel`; Q92 a Q95, Q101 a Q103.
