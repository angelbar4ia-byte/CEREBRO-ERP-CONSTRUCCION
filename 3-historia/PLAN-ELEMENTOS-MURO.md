# Plan de registro y construcción: elementos de muro, Artefacto, Paramétrico y Cuantificador

```
órgano:     plan de trabajo de los elementos de muro
capa:       III — Historia
pregunta:   ¿en qué orden se registra y se construye lo diseñado en el mockup?
tiempo:     se planeó así
corte:      2026-11-12
verificado: mockup interactivo publicado y probado en Chromium; su especificación completa está en 3-historia/mockups/muros-parametricos.especificacion.json
```

> La decisión está en **D-647**. El mockup sigue abierto: este plan fija el orden para avanzar sin que después pese más; cada fase cierra con su PR y se ajusta si el mockup cambia. Lo que no está decidido está en `preguntas_abiertas` de la especificación (Q17 a Q28).

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
| J | **Migración de `muro_tipo`** (pretil, barda, sillar) y de los muros existentes | E | los muros anteriores se leen igual |

## 3. Riesgos y lo que falta decidir

- Puntas de 40 diámetros y 50 cm en armex: confirmar con el estructurista (Q22).
- Conceptos EJ-420 a EJ-425 (entrepiso, azotea, pretil y barda) son del mockup: Control de obra los autoriza y se confirma su composición (Q26).
- Escalones de más de 6.00 m: se diseñan después (Q27).
- Mano de obra por tipo de actividad y bastón: preguntas Q19 y Q28.
- El armex no tiene peso en el catálogo: el kg de acero con armex queda sin dato.
