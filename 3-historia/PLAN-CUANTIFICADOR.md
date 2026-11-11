# Plan del Cuantificador: auditoría (cerebro contra app contra mockup) y fases para completarlo

```
órgano:     plan de trabajo del Cuantificador
capa:       III — Historia
pregunta:   ¿qué falta del Cuantificador y en qué orden se completa?
tiempo:     se planeó así
corte:      2026-11-05
verificado: auditoría del cerebro contra la app y el mockup el 2026-11-05; lo construido después se anota en MEMORIA (D-641 a D-644)
```

> Formalizado a partir de la auditoría del 2026-11-05. Nota de numeración: **D-638** ya es «Muro · medir por y la altura se eligen antes de trazar»; las decisiones nuevas de este plan empiezan en **D-639**. Lo que la auditoría llamó F-6 «colocar elemento» sigue en este plan; el panel «Muro · medir por» ya está hecho.

Fecha: 2026-11-05. Solo lectura. Alcance: `cerebro-erp-construccion` (MEMORIA D-531 a D-637, WORKFLOWS §8.9, MODELO §1b y §5c, skill erp-cuantificador), la app `control-avance` (backend `backend/src/obractrl`, frontend `frontend/src/cuantificador`, migraciones hasta 0118, pruebas) y el mockup `cuantificador-pantalla.html`.

Método: cada requisito se verificó contra la función, endpoint o componente concreto. Lo que el cerebro marca como "construido" se comprobó en código, no se tomó de la redacción. Lo no verificado en ejecución real (solo lectura estática y lectura de pruebas) se dice.

Reglas del usuario respetadas al priorizar:
- Los costos se definen en Presupuesto; el Cuantificador solo maneja cantidades. Los requisitos de costo del cerebro (D-602 §9, D-603 precios, D-630 costo, D-590 recálculo de CPU, D-631 jornal por integrante) se marcan "FUERA (Presupuesto)" y no cuentan como falta del Cuantificador.
- PENDIENTES por decisión del usuario (fuera del plan activo, ver sección 4): filas del árbol izquierdo (receta, cuadrilla, duración, estado, conteo de trazos) y mover costo por día de cuadrilla, CPU y rendimiento teórico a Presupuesto.
- Girar trazos solo es para puertas (hoja, hecho en D-632 y D-637).
- Ya hechos recientemente: vanos completos (D-635, D-637), matriz que cuenta (D-636, migración 0118), línea sobre m² = largo × altura × caras (D-627, D-633).

---

## 1. Tabla de requisitos

Leyenda: H = HECHO, P = PARCIAL, F = FALTA, X = FUERA (corresponde a Presupuesto o a otro módulo; no cuenta como falta).

### 1.1 Motor, trazo y enlace

| # | Requisito | ID | Est. | Evidencia | Notas |
|---|---|---|---|---|---|
| 1 | Un motor con dos entradas: módulo y ventana flotante "Medir" con "Abrir en el módulo" | D-531, D-532 | H | `VentanaCuantificador.tsx`; botón Medir en `presupuesto/PanelRendimientos.tsx` y `avance/Avances.tsx`; `EspacioDeTrazo` en `Cuantificador.tsx` | Una sola ventana a la vez, minimiza sin desmontar |
| 2 | Uso diseño y uso comprobación (medido contra base, "dif.") | D-532 | H | `ArbolPresupuesto.tsx` ("Medido X de Y · dif."); `arbol.ts` (`cant_base`) | La comparación es visual; no genera propuesta con evidencia por discrepancia grande (ver F-2) |
| 3 | Uso programación: segundo cuantificador, mide una actividad contra el techo del presupuesto, hasta 20 % sigue solo | D-532, MODELO §5c | F | No existe `ENLACE_CUANTIFICACION_PROGRAMA` en migraciones ni código; `umbral_pct` solo vive en cierre de frente | Depende del programa (módulo CPM) |
| 4 | TRAZO y ENLACE_CUANTIFICACION: un trazo, varios enlaces; vigencia en el enlace; evidencia nunca se borra | D-201, MODELO §1b | H | `cuantificacion_sql.py`, `application/casos_uso/cuantificar.py`; `reemplazar` enlace (`/enlaces-cuantificacion/{id}/reemplazar`) | |
| 5 | Fuente de trazo elegible; precedencia IFC > DWG > PDF | D-111 | P | Campo `fuente` existe; solo se usa PDF | El cerebro dice "hoy PDF"; DWG e IFC son futuro (F-18) |
| 6 | Trazo con plantilla e instancia, para reusar y comparar entre obras | D-112 | F | No hay tabla ni UI de plantilla de trazo (`plantilla.ts` es del conteo automático, otra cosa) | Pregunta de producto pendiente: qué se compara y cuándo |
| 7 | Plano que cambia: lo trazado queda "por revisar", no se recalcula solo | D-113, skill §5 | H | `cuantificacion_sql.py` `por_revisar = version_plano < plano.version` | |
| 8 | Plano nuevo: retrazar y comparar volumen; si da igual reemplaza, si difiere quedan las dos | D-113 | P | Empalme manual (`/trazos/{id}/traer`, `empalme.ts`, `OpcionesDeEmpalme.tsx`) | No hay comparación automática de volumen entre revisiones ni la regla "reemplaza si iguala" |
| 9 | Quién traza y quién aprueba (roles atómicos) | D-114, D-236 | H | `ROLES_QUE_TRAZAN`, `ROLES_QUE_APRUEBAN`, `ROLES_QUE_ANOTAN` en `v1/cuantificacion.py` | Costos pone y quita en catálogo con límites (D-591) |
| 10 | Anotar el plano nunca genera cantidad | skill §6 | H | `AltaNota.tsx`, `OpcionesDeNota.tsx`, `/planos/{id}/notas` | |
| 11 | Peso desde longitud, superficie inclinada, volumen, conteo por patrón | skill §4 | H | `AltaTrazo.tsx` (`factorDePendiente`), `domain/cuantificacion/reglas.py`, `volumen.ts` | |
| 12 | Cubicación con taludes por fórmula personalizada | skill §4 | F | No hay `formula_personalizada` en código ni migraciones | Sin consumidor real; el cerebro lo documenta como "no verificado" |
| 13 | Ejes y niveles | skill §4 | X | Bloqueado en el cerebro: depende de `FRENTE` | No hacer |

### 1.2 Herramientas y mediciones

| # | Requisito | ID | Est. | Evidencia | Notas |
|---|---|---|---|---|---|
| 14 | Tres tipos de medición con su bloque en la barra; área siempre cerrada; círculo, elipse, arco, contorno | D-586 | H | `BarraDeHerramientas.tsx` (`BLOQUES`), `formas.ts`, `geometria.ts` | Mockup y app tienen las mismas 24 herramientas |
| 15 | Barra dividida en "Trazo" y "Funciones" | D-586 | H | `BarraDeHerramientas.tsx` (acciones de vista y funciones) | |
| 16 | Mediciones como capa sombra: anidadas del mismo tipo, asignadas a conceptos, "sin asignar", borrar borra asignaciones | D-585 | H | migración 0088; `mediciones.py`; `PanelDeMediciones.tsx` | |
| 17 | Medición se crea sobre una selección (concepto o matriz), con nombre y unidad, con botón eliminar | D-601 | H | `PanelDeMediciones.tsx`, `/planos/{id}/mediciones` | El mockup quitó la anidación; la app la conserva (decisión abierta, ver F-19) |
| 18 | Color propio por medición; "Mostrar medidas" con clave, concepto, matriz, medición y medida | D-600 | H | `mediciones.ts` (`colorDeMedicion`), `etiquetas.ts`, `Visor.tsx` | El color depende de la posición en la lista (lectura del cerebro por confirmar) |
| 19 | Medición derivada: elemento con peso (K1) | D-587 | H | migración 0089; `elementos.py`; `PanelDeElementos.tsx`; e2e `y-elementos-con-peso` | |
| 20 | Sin botón de guardar: autoguardado con indicador y deshacer/rehacer | D-588 | H | "Guardando… / Todo guardado" en `Cuantificador.tsx:3380`; `historial.ts` | |
| 21 | Trazo se guarda al cerrar la figura si hay destino | D-599 | H | `trazoPeticion.ts`; e2e `zh-trazo-directo` | |
| 22 | Línea sobre m² = largo × altura × caras, editable | D-601, D-627, D-633 | H | `domain/cuantificacion/muro.py`, `conversion.py`, SQL `app.cantidad_conversion` (migraciones 0114, 0115) | Muro por partes de altura incluido |
| 23 | Cómo cuenta para el concepto: conversión por enlace (largo, área, volumen, piezas, perímetro, forma, punto), fórmula escrita, "se mide en m²", aplicar a N trazos | D-633 | H | `ConversionDelEnlace.tsx`, `/enlaces/{id}/conversion` (+ `/calcular`) | Pendiente declarado: radio, diámetro, ángulo en el resumen (F-14). Sin e2e |
| 24 | Uniones de muro: conexión, tope, empalme, fusión | D-629 | H | migración 0111; `UnionesDelMuro.tsx`; `/trazos/{id}/uniones`, `/trazos/{id}/fusion` | Falta dibujo del cuerpo continuo (F-13). Sin e2e |
| 25 | Volumen: calcular volumen, cuadro de datos, cotas, referencias, ortogonal | D-586, mockup | H | `PanelVolumen.tsx`, `CuadroDeDatos.tsx`, `AyudasDeDibujo.tsx`, `referencias.ts` | |
| 26 | Vista: girar y voltear el plano (solo presentación) | mockup | H | `vista.ts`, acciones de vista en la barra | |
| 27 | Empalme de versiones: fantasma con transparencia y desfase, traer uno o todos sin doble conteo | D-592 | H | `empalme.ts`, `OpcionesDeEmpalme.tsx`, e2e `za-empalme-de-versiones` | |
| 28 | Escala automática: propone y solo aplica al confirmar | D-593 | H | `escalaAuto.ts`, `ProponerEscala.tsx`, `domain/cuantificacion/escala.py`, e2e `zb` | |
| 29 | Enlaces entre hojas | D-594 | H | migración 0091; `AltaEnlaceDeHoja.tsx`; `enlaces_de_hoja.py`; e2e `zc` | |
| 30 | Propuestas automáticas nunca cuentan hasta aceptarse (trigger) | D-595 | H | migración 0092 (`trg_enlace_no_a_propuesta`); `PanelDePropuestas.tsx`; e2e `zd` | |
| 31 | Conteo automático por plantilla; takeoff de áreas y muros | D-596 | H | `ConteoAutomatico.tsx`, `TakeoffAutomatico.tsx`, `takeoff.ts`, `imagenGris.ts`; e2e `ze`, `zf` | Límites dichos: no lee vectores, no reconoce muro de dos líneas finas (F-16) |
| 32 | Conteo con IA leyendo la simbología ("donde dice K-1 marca el punto") | D-602 §6 | F | Ausente. El mockup tiene el botón "Contar con la simbología (IA)" | Hoy solo hay correlación por plantilla |

### 1.3 Matrices, árbol y conceptos

| # | Requisito | ID | Est. | Evidencia | Notas |
|---|---|---|---|---|---|
| 33 | Hojas matriz: cuantificar matrices internas a cualquier profundidad; cantidad de la obra, no del catálogo | D-583, D-584 | H | migración 0085; `MatricesDeActividad.tsx`; `matrices_de_concepto.py`; e2e `s-hojas-matriz` | |
| 34 | La matriz que cuenta para el concepto | D-636 | H | migración 0118 (`actividad.matriz_cuenta_id`); `PUT /actividades/{id}/matriz-que-cuenta`; "Que cuente" en `MatricesDeActividad.tsx`; confirmación al trazar directo | Sin e2e |
| 35 | Concepto padre con matrices medidas a medias | D-584 (abierto) | H | Resuelto por D-636 en la práctica | Queda el caso sin matriz que cuente: el ajuste solo suma lo medido |
| 36 | Concepto nace desde el cuantificador (adicional, sin cantidad) | D-589 | H | `AltaDeConcepto.tsx`; `POST /obras/{id}/conceptos-nuevos`; e2e `z-concepto-nuevo` | |
| 37 | Matrices se agregan y quitan en el catálogo del concepto | D-590 | H | `AltaDeMatriz.tsx`; `POST/DELETE /conceptos/{id}/matrices`; e2e `z2-matrices-de-concepto` | Recálculo de CPU: X (Presupuesto) |
| 38 | Cantidad de matriz por piezas comerciales con desperdicio | D-598 | H | migración 0094; `cantidad.ts`; `AltaDeMatriz.tsx` | Otras fórmulas (rendimientos, mezclas) siguen a mano, como dice el cerebro |
| 39 | Árbol se arma desde el cuantificador: niveles, etapas, partidas, mover, subir y bajar posición y nivel | D-597, D-634 | H | `PanelDelArbol.tsx`; migraciones 0093 y 0116; e2e `zg-arbol-editable` | |
| 40 | Cambiar la unidad de un concepto a otro tipo con equivalencia, versión del concepto, trazos marcados | D-601, D-623 | H | migración 0106; `cambio_de_unidad.py`; `CambioDeUnidadDelConcepto.tsx` | Residual: `arbol.cambiar_unidad` aún bloquea cambios del mismo tipo con medidas que no caben (F-12). Sin e2e de la propuesta completa |
| 41 | Árbol propio por obra en diseño, versión borrador, confirmar, reiniciar, cambiar prototipo | D-624, D-625, D-626 | H | migraciones 0107 a 0109; `ArbolDeLaObra.tsx`; `arbol_de_obra.py` | |
| 42 | Árbol por espacios: tronco = casa, ramas = espacios, subramas = niveles y etapas, hojas = conceptos o matrices | D-565 | F | No existen espacios en prototipo ni en el árbol del cuantificador | El propio cerebro dice "trabajo nuevo" y "falta por confirmar" (F-9) |
| 43 | Muro compartido: asignar a un espacio o repartir mitad y mitad; excedente de altura a un área | D-566 | P | Mecanismo existe (factor del enlace, cajón `AltaTrazo.tsx`; altura por partes en D-633) | No hay flujo guiado de reparto ni espacios a los que asignar (F-10) |
| 44 | Descripción corta del concepto en el árbol y en presupuesto del cuantificador | D-622 | H | `arbol.ts` (`corta`, `descripcionCorta`) | |

### 1.4 Elementos paramétricos y cimbra

| # | Requisito | ID | Est. | Evidencia | Notas |
|---|---|---|---|---|---|
| 45 | Catálogo de elementos paramétricos (castillo, lineal, zapata, losa) con receta calculada por el servidor | D-602, D-604, D-622 | H | migración 0104; `domain/cuantificacion/elementos_parametricos.py`; `PanelDeParametricos.tsx`; e2e backend `test_elementos_parametricos_endtoend` | Sin e2e de navegador |
| 46 | Catálogo con versiones | D-602 §8 | P | La tabla `elemento_parametrico` no tiene versionado | Hoy editar cambia todos los usos |
| 47 | Constantes (vara 12 m, peso por varilla, calibre de alambre) en `CONSTANTE_FISICA` | D-602 §7, D-326 | P | Están fijas en código: `PESO_VARILLA_KG_M`, `PESO_ALAMBRE_KG_M`, `VARA_COMERCIAL_M` | El docstring dice lo contrario; no hay lectura de la tabla (F-8) |
| 48 | Marcar el trazo como elemento y que el concepto "tome" su parte de la receta | D-604 §7, D-630 | P | migración 0112; `ElementoDelTrazo.tsx`, `ConceptosDelElemento.tsx`; `elementos_parametricos_sql.py` | La toma se calcula al leer y se muestra en "En este plano"; no alimenta cantidades de la matriz del concepto ni de Presupuesto (F-5) |
| 49 | Modo "Colocar este elemento": activar el elemento y trazar con Punto, Línea o Área | D-604 §7, mockup | P | Hoy se traza y luego se elige el elemento en el detalle del trazo | Faltan la activación previa y el cierre automático (F-6) |
| 50 | Cimbra por número de lados (4, 3, 2) como cantidad (m²) | D-602 §4 | H | `cimbra_m2` por lados en `elementos_parametricos.py` | |
| 51 | Lados de cimbra detectados del plano (junto a vano = 3, sobre muro continuo = 2, aislado = 4) | D-602 §7 | F | Solo selector manual en `ElementoDelTrazo.tsx` | Depende de vanos y muros ya hechos; es calculable (F-4) |
| 52 | Cimbra como sub-elemento: diseño elegible (forro tabla, triplay o tarima; listones, barrotes, puntales, vigas, tuino), usos por pieza, cantidad ÷ usos | D-603, D-604 §5 y §6 | F | Ausente en backend y frontend. El mockup tiene `pintaCimbra`, `cimbraDet` | La parte de precios es X (Presupuesto); la estructura y las cantidades son del Cuantificador (F-1) |
| 53 | Alambre de amarre de la cimbra (cada cuánto, hilos, longitud, calibre) | D-603 §6 | F | Solo existe el alambre del armado | Parte de F-1 |
| 54 | Alambre de amarre del armado (varillas × estribos × longitud × peso) | D-603 §5 | H | `alambre` en la receta | |
| 55 | Dibujo del diseño de cimbra en alzado, corte, planta e isométrico, actualizado solo | D-603 §4 | F | Ausente. El mockup: `dibAlzado`, `dibCorte`, `dibPlanta`, `dibIso`, "Ver las 4 vistas", "Duplicar el diseño" | Parte de F-1, la más grande |
| 56 | Pendientes de D-604: traslapes y bastones de trabe, nervaduras y aligerantes de losa, zapata corrida, cimbra de columna y dado, tuino | D-604 | F | Tipos soportados solo castillo, lineal, zapata aislada y losa maciza | Cada uno exige definición del usuario antes (F-7) |
| 57 | Costo base, real y actual del elemento | D-602 §9, D-630 | X | No aplica al Cuantificador | Presupuesto, regla del usuario |
| 58 | "Buscar elemento" en la pestaña Elementos | mockup | F | No existe en `Cuantificador.tsx` ni `PanelDeElementos.tsx` | Trivial (F-17) |

### 1.5 Vanos

| # | Requisito | ID | Est. | Evidencia | Notas |
|---|---|---|---|---|---|
| 59 | Vano sobre muro: descuenta ancho × alto × piezas × caras; en ml descuenta ancho si llega al piso | D-635 | H | migración 0103; `vanos.ts`; e2e backend `test_vanos_endtoend` | |
| 60 | "Cómo se coloca": punto o línea, rejilla de nueve puntos, tipos, antepecho, cantidad idéntica | D-635 | H | `OpcionesDeVano.tsx`; migración 0117 (`vano.lado_muro`) | |
| 61 | Versiones del catálogo de vanos (P-01, V-01…), "+ Nueva", papelera, mínimo una por tipo | D-635 | H | `vanos_catalogo.py`; migración 0117 (`vano_version`) | |
| 62 | Vanos sobre áreas | D-635 | H | `vanos.ts`, `VanosDelPlano.tsx` | |
| 63 | Barra de estado con lo descontado y el total; leyenda de atajos | D-635 | H | `Cuantificador.tsx` | |
| 64 | Hoja de la puerta: bisagra, lado, apertura; solo especificación | D-632 | H | migración 0113; `PUT /vanos/{id}/hoja`; `VanoElegido.tsx` | Sin e2e |
| 65 | Vano elegido: "Elemento colocado", asas (mover y ensanchar), versión que sigue al ancho, deshacer, menú de clic derecho | D-637 | H | `VanoElegido.tsx`, `accionesDeVano.ts`, `Visor.tsx` (asas), e2e `zi-vano-por-clic` | |
| 66 | Girar trazos solo para puertas | D-637 | H | Lo que queda de "girar" es la hoja | Cerrado por el usuario |

### 1.6 Trabajos (destajos y cuadrillas)

| # | Requisito | ID | Est. | Evidencia | Notas |
|---|---|---|---|---|---|
| 67 | Pestaña Trabajos: destajos por concepto, cuadrillas con tres rendimientos, importe, capacidad, duración, jornales | D-605 | H | `PanelDeTrabajos.tsx`, `EditorDeTrabajo.tsx`, `trabajos.ts`; `trabajos_de_obra`; e2e `x-pestanas-del-cuantificador` | El editor muestra calculado y teórico; el real no se captura aquí |
| 68 | "+ Destajo" y "+ Cuadrilla" desde la pestaña | D-631 | H | `AltaDeTrabajo.tsx`; `POST /conceptos/{id}/destajos` | Sin e2e específico |
| 69 | Destajos y cuadrillas bajo cada concepto del árbol de la izquierda | D-605 §5 | P | Solo en la pestaña Trabajos | PENDIENTE por decisión del usuario (sección 4) |
| 70 | Partir un destajo entre varios conceptos (lote), subcontratos y acarreos como clases de trabajo | D-605 | F | Ausente. El cerebro lo marca "pendiente de definir" | Requiere decisión (D-240, D-188) |
| 71 | Integrantes de cuadrilla con puesto y jornal; costo recalculado | D-631 | X | Costo por persona | Presupuesto |

### 1.7 Escenarios, gobierno y calidad

| # | Requisito | ID | Est. | Evidencia | Notas |
|---|---|---|---|---|---|
| 72 | Escenarios de arranque 1 a 4 y estado por parte (envío a presupuesto, autorizar, programar, asignar, candado) | D-571 a D-580 | H | migraciones 0074 a 0082; e2e `n` a `r` | Fuera del núcleo del Cuantificador, funciona |
| 73 | Crear obra solo en "Creador de obra"; prototipo editable mientras es diseño | D-626 | H | `proyectos/PanelObra.tsx`, `CambiarPrototipo.tsx` | |
| 74 | Aprendizaje del paramétrico con lo medido: se reporta, no se aplica | D-580, §8.1 | H | `valuacion_de_partes.py` (desviación) | |
| 75 | Móvil y offline | — | X | `mobile/` no tiene cuantificador; el cerebro no lo exige | No hay requisito |
| 76 | Pruebas de los vanos y la conversión | calidad | P | Hay pruebas de dominio y por HTTP; faltan e2e de navegador de D-629, D-632, D-633, D-636, elementos y cambio de unidad | Ver fase 6 |

### Conteo

76 filas: HECHO 51, PARCIAL 9 (filas 5, 8, 43, 46, 47, 48, 49, 69 y 76), FALTA 12 (filas 3, 6, 12, 32, 42, 51, 52, 53, 55, 56, 58 y 70), FUERA 4 (filas 13, 57, 71 y 75).

Sobre las 72 filas evaluables: 51 HECHO (71 %), 9 PARCIAL, 12 FALTA. La fila 69 es PARCIAL solo porque su cierre es un pendiente del usuario (sección 4).

---

## 2. Qué FALTA y qué es PARCIAL, por área

Tamaños: S = menos de un día, M = 2 a 4 días, L = una semana o más. Dependencia = qué debe existir antes.

### Trazo y herramientas

- F-2 (PARCIAL, S). Cuando la medida difiere mucho de la cantidad cargada, mostrarlo es suficiente hoy; el cerebro pide que sea "propuesta con evidencia" (D-46). Dependencia: ninguna. **Resuelto (D-641): el Cuantificador no tiene umbral;** el umbral solo aplica en ejecución (estimación excedente).
- F-16 (FALTA, L, riesgo alto). Takeoff de muros dibujados con dos líneas finas y lectura de vectores del PDF. Es límite declarado en D-596. Dependencia: pruebas con planos reales de la organización; no empezar sin ellos.
- F-18 (FALTA, L, futuro). Fuente DWG e IFC con precedencia (D-111). El campo `fuente` ya existe. Dependencia: decisión de producto; el cerebro dice "hoy PDF".
- F-12 (PARCIAL, S). `arbol.cambiar_unidad` aún bloquea cambios dentro del mismo tipo cuando hay medidas que no caben (m² a m³ con área ya medida, `application/casos_uso/arbol.py` líneas 118 a 129). D-601 pide no bloquear: reutilizar el flujo de D-623 con equivalencia 1 o marcar el enlace.

### Detalle del trazo

- F-13 (FALTA, M). Dibujo del cuerpo continuo del muro con conexión y largo exacto por cara en el plano (D-629 pendiente). El cálculo ya está en SQL; falta el trazado en `Visor.tsx`.
- F-14 (FALTA, S). Radio, diámetro y ángulo de arcos y círculos en el resumen del detalle (D-633 pendiente). Dependencia: `resumen.ts`.
- F-3 (PARCIAL, M). Ingletes y cantidades en esquinas ya salen de `app.cantidad_conversion`; revisar con un caso de muro en L, T y cruz que la vista previa del frontend coincida con el servidor (la regla es "una sola función"; verificar que el front no recalcula).

### Vanos

Sin faltas. D-635 y D-637 están completos contra el código. Único detalle: no hay e2e de navegador de la hoja de la puerta (D-632), ver fase 6.

### Elementos, catálogo y paramétricos

- F-5 (PARCIAL, M). Que lo que un concepto "toma" de un elemento alimente de verdad la cantidad de su matriz (hoy solo se muestra). Es la brecha más importante de esta área. Requiere decisión: ¿la toma escribe la cantidad medida de la matriz interna (D-584) o solo sirve de comprobación? Dependencia: D-584 (cantidad medida de matriz) y `elemento_concepto` (0112).
- F-6 (PARCIAL, M). Modo "Colocar este elemento en el plano": elegir el elemento, activar la herramienta que corresponde (Punto, Línea, Área) y que cada trazo nazca ya marcado y con destino. Hoy es en dos pasos. Dependencia: ninguna.
- F-4 (FALTA, M). Detectar los lados de cimbra del plano: castillo junto a un vano = 3, sobre un muro continuo = 2, aislado = 4. Calculable con la geometría de vanos y muros que ya existe; se propone y se puede fijar a mano (regla "el sistema propone"). Dependencia: vanos y muros (hechos).
- F-8 (PARCIAL, S a M). Mover las constantes de `elementos_parametricos.py` a `CONSTANTE_FISICA` como dice D-602 §7 y D-326 (hoy están fijas en el código y el docstring afirma lo contrario). Dependencia: confirmar si existe la tabla poblada.
- F-20 (PARCIAL, M). Versiones del catálogo de elementos paramétricos (D-602 §8): hoy editar cambia todos los usos. Decidir si las obras asignadas se congelan, como en vanos (D-635).
- F-7 (FALTA, L en conjunto). Más tipos: traslapes y bastones de trabe, nervaduras y aligerantes de losa, zapata corrida, columna y dado, tuino. Cada uno exige definición del usuario antes de programarse. No planear fechas.
- F-17 (FALTA, S). "Buscar elemento" en la pestaña Elementos del mockup.
- F-32 (FALTA, L, riesgo alto). Conteo con IA que lee la simbología (D-602 §6). Entra solo como propuesta (D-595, ya soportado). Dependencia: F-4 no, pero sí "muros trazados y tipos de área" como precondición declarada por el usuario; y una decisión de proveedor de modelo.

### Cimbra

- F-1 (FALTA, L). La cimbra como sub-elemento (D-603, D-604 §5 y §6): catálogo de diseños de cimbra (forro, piezas con sus usos, "cada cuánto" por ml o m², alambre de amarre), elección de diseño por elemento, cantidad ÷ usos, por lado (4, 3, 2) y por elemento (trabe, cadenas, zapata, losa). Los precios son de Presupuesto y se excluyen; el Cuantificador entrega cantidades por pieza y su número de usos. Dependencia: F-5 (para que la receta llegue a la matriz) y F-4 (lados).
- F-15 (FALTA, L). Dibujo del diseño en alzado, corte, planta e isométrico que se actualiza al cambiar medidas ("Ver las 4 vistas", "Duplicar el diseño"). Se puede entregar después de F-1 como segunda parte, porque la cantidad no depende del dibujo.

### Árbol

- F-9 (FALTA, L, requiere decisión). Árbol por espacios (D-565): casa, espacios, niveles y etapas, conceptos. El cerebro lo deja "falta por confirmar" y reconoce que los siete prototipos de hoy no tienen espacios. Dependencia: B-113 (espacios y sus m²) y decisión sobre el programa que suma etapas de cada espacio.
- F-10 (PARCIAL, M). Muros compartidos (D-566): flujo guiado "asignar a un espacio" o "repartir mitad y mitad" y banda de excedente de altura. Hoy se logra a mano con factor en el cajón. Dependencia: F-9; sin espacios el flujo no tiene a qué asignar.
- Filas del árbol izquierdo con receta, cuadrilla, duración, estado y conteo de trazos: PENDIENTE por decisión del usuario, ver sección 4.

### Matrices

Sin faltas de producto. Observaciones:
- Borde del ajuste (D-584 regla 1): cuando no hay matriz que cuente, el importe se ajusta solo por lo medido; D-636 resuelve el caso con una sola matriz que cuenta, pero no el caso de dos matrices medidas con unidad distinta del concepto. Documentarlo o cubrirlo con una prueba.
- Sin e2e de navegador para D-636 (S, en fase 6).

### Mediciones

- F-19 (decisión abierta, S). El mockup quitó la anidación madre e hija de mediciones; la app la conserva (D-601 lectura 3). Preguntar al usuario si se retira de la interfaz o se mantiene. No tocar sin respuesta.

### Automáticos e IA

Ver F-32 (simbología), F-16 (takeoff de dos líneas) y F-2 (discrepancia). Conteo por plantilla y takeoff de áreas y muros están hechos y revisan antes de sumar.

### Plano y versiones

- Fila 8: la regla D-113 "retrazar y comparar volumen; si da igual reemplaza, si difiere quedan las dos" solo existe como flujo manual de empalme. Un comparador automático entre revisiones es M y depende de que la geometría de ambas revisiones sea comparable (F-16 no lo bloquea).
- D-112 plantilla e instancia entre obras (F-11, L, requiere decisión): no hay modelo. Qué se compara entre obras y para qué lo usa el paramétrico no está definido en el cerebro más allá de "sirve para reusar y comparar".

### Roles y gobierno

Sin faltas: roles `trazar`, `aprobar_trazo`, `anotar_plano` y los de Costos están implementados. Costos no cambia ni borra conceptos existentes (D-591), comprobado en políticas de migración 0090.

### Offline y móvil

No aplica: el cerebro no lo pide y `mobile/` no incluye el cuantificador. Se menciona solo para dejar constancia.

### Programación (segundo cuantificador)

- F-21 (FALTA, L). `ENLACE_CUANTIFICACION_PROGRAMA`, medir actividades contra el techo del presupuesto con umbral 20 % y solicitud a Control (MODELO §5c, D-532 uso programación). Dependencia: módulo de programa (`programacion/`), alertas con `parametro_usado`. Decisión de prioridad: el cerebro lo deja a `PRIORIDADES.md`.

---

## 3. Funciones del mockup que la app no tiene

Verificadas por etiqueta y por función contra `frontend/src/cuantificador`:

| Mockup | Estado en la app |
|---|---|
| "Contar con la simbología (IA)" (`data-pia`) | F, F-32 |
| Cimbra: `pintaCimbra`, `cimbraDet`, "Ver las 4 vistas", "Duplicar el diseño", "Abrir el diseño de la cimbra", dibujos `dibAlzado/dibCorte/dibPlanta/dibIso` (y variantes lineal y de zapata/losa) | F, F-1 y F-15 |
| "Colocar este elemento en el plano" (`data-colocar`) con activación de herramienta | P, F-6 |
| "Buscar elemento" (`findEle`) | F, F-17 |
| "Ver el elemento" desde el detalle del trazo (`data-pk`) | F, S (el detalle del trazo no abre el elemento en la pestaña Elementos) |
| Lados de cimbra detectados | F, F-4 |
| Filas del árbol con trabajo, cuadrilla y estado (`trb` bajo cada concepto: "Clic: abrir en Trabajos") | PENDIENTE usuario |
| "+ Integrante" en cuadrilla | X (costo, Presupuesto) |
| Rendimiento real de cuadrilla capturado | X (obra y Presupuesto) |

Funciones que el mockup y la app tienen por igual (comprobadas): las 24 herramientas con sus atajos, vista (girar y voltear), ayudas de dibujo (F3, F8), tres tipos de medición con bloques, mediciones con color y anidación en la app, propuestas por revisar (Aceptar y Rechazar), Planos con Subir plano y buscar, Trazos con buscador y lista, Elementos del plano, Trabajos con buscador, Árbol con catálogo propio y reinicio, detalle del trazo con "Cómo cuenta para el concepto", uniones, hoja de puerta, vanos completos, matriz que cuenta, cambio de unidad, cantidad por piezas comerciales.

Lo que la app tiene y el mockup no: anidación de mediciones, ventana flotante "Medir", cuadro de datos real con servidor, propuestas persistidas con trigger, escala automática desde el PDF, takeoff real, enlaces entre hojas persistidos.

---

## 4. Pendientes por decisión del usuario (fuera del plan activo)

No entran a las fases. Se dejan registrados para cuando el usuario los reactive:

1. Filas del árbol de la izquierda: receta de cada matriz con su cuadrilla y duración, estado y conteo de trazos (D-635 "pendiente, decisión del usuario"; D-605 §5 "bajo cada concepto en Presupuesto y en Árbol").
2. Mover a Presupuesto: costo por día de la cuadrilla, CPU y rendimiento teórico. Hoy `EditorDeTrabajo.tsx` captura el costo por día y el rendimiento teórico dentro del Cuantificador, lo que contradice la regla "el Cuantificador solo maneja cantidades"; la reubicación se hará cuando el usuario lo decida.
3. Costos de elementos (base, real, actual), precios de cimbra, integrantes con jornal (D-602 §9, D-603 §7, D-630, D-631) quedan del lado de Presupuesto.

---

## 5. PLAN por fases

Orden recomendado por valor de uso y por dependencia. Cada fase termina con un entregable verificable y cierra con una anotación en el cerebro. Convención de pruebas del proyecto: dominio con pytest, HTTP contra Postgres real (`test_*_endtoend.py`), componentes con Vitest en `frontend/src/pruebas/`, flujo con Playwright en `frontend/e2e/workflows/`. La numeración de migración continúa en 0119.

### Fase 0. Decisiones y calibración (sin código, 1 a 2 días)

Entregable: respuestas escritas del usuario registradas como D-639 en adelante, antes de tocar F-5, F-9, F-11, F-19, F-20, F-21.

Preguntas concretas:
1. F-5: ¿lo que un concepto toma de un elemento escribe la cantidad medida de una matriz interna o solo comprueba?
2. F-19: ¿se conserva la anidación de mediciones?
3. F-20: ¿los elementos paramétricos se versionan y las obras asignadas se congelan?
4. F-9 y F-10: ¿se construyen los espacios ahora o se difiere hasta B-113?
5. F-1: cuáles piezas de cimbra son obligatorias en la primera entrega y qué es el tuino.
6. F-21: ¿el segundo cuantificador entra en este ciclo?

Cerebro: registrar cada respuesta como decisión con su ID. Riesgo: construir F-1 o F-5 sin esto obliga a rehacer.

### Fase 1. Cerrar lo parcial barato (S, 3 a 5 días)

Entregable: pequeñas brechas que ya están definidas y no necesitan decisión.

- F-8: leer las constantes de `CONSTANTE_FISICA` (o corregir el docstring si no existe la tabla).
- F-12: `cambiar_unidad` de mismo tipo sin bloqueo (reutiliza el flujo de D-623).
- F-14: radio, diámetro y ángulo en `resumen.ts` y en el detalle.
- F-17: "Buscar elemento" y "Ver el elemento" desde el detalle del trazo.
- Backend: ajuste en `application/casos_uso/arbol.py` y en `domain/cuantificacion/cambio_de_unidad.py`; sin migración salvo F-8.
- Frontend: `Cuantificador.tsx`, `PanelDeElementos.tsx`, `resumen.ts`.
- Pruebas: `test_cambio_de_unidad_endtoend.py` (caso mismo tipo), `cuantificador-parametricos.test.ts`, caso de `resumen`.
- E2E: ampliar `zg-arbol-editable.spec.ts` con el cambio de unidad sin bloqueo.
- Cerebro: nota en D-601 y D-623 ("cambio de mismo tipo ya no bloquea").
- Riesgo: bajo. Aceptación: cambiar m² a m³ con área ya medida no pide quitar trazos y deja el enlace marcado; las constantes salen de una sola fuente.

### Fase 2. Elementos que alimentan de verdad (M, 1 semana; depende de la respuesta 1 de la fase 0)

Entregable: F-4 y F-6, y F-5 según la decisión.

- F-4 lados de cimbra por contexto: función de dominio `lados_por_contexto(trazo, vanos, muros)` que propone 4, 3 o 2; el usuario puede fijarlo; se guarda en `trazo_elemento_parametrico` solo si lo fija (lo propuesto se calcula al leer).
- F-6 modo "Colocar": estado `elementoActivo` en `Cuantificador.tsx`, elige la herramienta según `GEOMETRIA_DEL_TIPO`, y al cerrar la figura crea el trazo con el elemento marcado y el destino de la toma.
- F-5 (según decisión): endpoint que convierte la toma en cantidad medida de la matriz interna (reutiliza `actividad_matriz`, D-584) o en comprobación visible.
- Migración 0119 solo si F-5 escribe cantidades (nueva columna de origen en `actividad_matriz`, por ejemplo `origen_elemento_id`).
- Pruebas: dominio de `lados_por_contexto` (aislado, junto a vano, sobre muro continuo), HTTP de la toma, Vitest de `parametricos.ts`.
- E2E nuevo `zj-elementos-parametricos.spec.ts`: crear K-1, colocarlo con Punto, ver lados propuestos y totales del plano.
- Cerebro: D-639 con la decisión de F-5 y actualizar WORKFLOWS §8.9 (lista de pendientes de D-602).
- Riesgo: que la toma duplique la medición del concepto (doble conteo). Mitigar con la regla D-584 regla 2 ("lo medido manda sobre lo de adentro") y con una prueba de no duplicar.
- Aceptación: colocar 10 castillos K-1 da concreto, acero, estribos, alambre y cimbra por lados propuestos, sin sumar dos veces lo trazado y lo tomado.

### Fase 3. Cimbra como sub-elemento (L, 2 a 3 semanas; depende de fases 0 y 2)

Entregable: F-1 y, después, F-15.

- Backend: migración con `diseno_cimbra` y `diseno_cimbra_pieza` (clave, unidad, "cada cuánto", usos), por organización, con RLS; elección de diseño por elemento (columna en `elemento_parametrico`); cálculo en `domain/cuantificacion/cimbra.py` (cantidad por pieza ÷ usos, alambre de amarre por hilos × longitud × peso por calibre); rutas en `elementos_parametricos.py`; permisos Control de obra y Costos para definir, lectura para todos.
- Los precios no se guardan en esta fase (regla del usuario). Se devuelve cantidad y usos para que Presupuesto los costee.
- Frontend: sección de diseños en `PanelDeParametricos.tsx`; entrega en dos pasos: primero cantidades y formulario; después el dibujo de cuatro vistas (`dibujosDeCimbra.ts`, SVG puro, solo funciones) como F-15.
- Pruebas: dominio con los valores del mockup (castillo K-1 con tabla y listón), HTTP, Vitest del dibujo (coordenadas por vista).
- E2E: `zk-cimbra.spec.ts` (elegir diseño, cambiar usos, ver kg de alambre y m² por lado).
- Cerebro: D-640 con el diseño elegido y los límites; WORKFLOWS §8.9 actualizado; retirar de "lo que aún no está" de D-622.
- Riesgo: alcance. Las piezas "tuino", puntales y vigas dependen de la fase 0 (pregunta 5). Entregar primero castillo y trabe, luego zapata y losa.
- Aceptación: castillo K-1 con 4 lados, forro de tabla y 3 usos arroja las mismas cantidades que el mockup, y el cambio de usos recalcula sin tocar precios.

### Fase 4. Espacios y muros compartidos (L, 2 semanas) — EN ESPERA por decisión del usuario (D-640: diseño anotado, sin construir)

Entregable: F-9 y F-10, solo si el usuario decide construirlos ahora.

- Backend: espacios como rama del prototipo de obra (nivel de árbol sobre etapas) y cálculo de m² por espacio como único dato capturado; el reparto de muros por factor del enlace (sin tabla nueva, como dice D-566).
- Frontend: `ArbolDeLaObra.tsx` y `PanelDelArbol.tsx` con la rama de espacios; flujo "Asignar muro a un espacio" y "Repartir mitad y mitad" en el detalle del trazo; banda de excedente de altura.
- El programa que suma las etapas de cada espacio es del módulo de programa: coordinar, no duplicar.
- Pruebas: dominio del reparto (1 y 0, 0.5 y 0.5, banda 3.00 a 4.20); HTTP de espacios; árbol Vitest.
- E2E: `zl-espacios-y-muros-compartidos.spec.ts`.
- Cerebro: D-641 cerrando "falta por confirmar" de D-565; B-113 actualizado.
- Riesgo alto: migrar los siete prototipos sin espacios. Proponer un espacio único "Casa" por defecto para no romper obras en curso.
- Aceptación: una recámara con muro compartido reparte la longitud sin duplicar área y el total de la casa coincide con la suma de espacios más los muros duplicados declarados.

### Fase 5. Automáticos e IA (L, 2 a 3 semanas; depende de pruebas con planos reales)

Entregable: F-32, F-16 y F-2, en ese orden de riesgo creciente.

- F-2: **descartado por D-641** (sin umbral en el Cuantificador; solo mostrar medido contra cargado).
- F-32: servicio de lectura de simbología sobre la imagen del plano; entra siempre como propuesta por revisar; requiere decisión de proveedor y manejo de claves (tema de seguridad, revisar con el equipo antes).
- F-16: muros de dos líneas finas en `takeoff.ts`; solo con un conjunto de planos reales de la organización para medir precisión.
- Pruebas: Vitest con imágenes sintéticas (ya hay patrón en `cuantificador-takeoff.test.ts`); HTTP de propuestas; criterio de precisión en un conjunto real.
- E2E: ampliar `ze-conteo-automatico` y `zf-takeoff-automatico`.
- Cerebro: D-642 con los resultados medidos; actualizar los límites de D-596.
- Riesgo: que una propuesta de IA se cuente sin revisión. El trigger de 0092 ya lo impide; agregar prueba de regresión.
- Aceptación: sobre 3 planos reales, el conteo por simbología propone al menos el 80 % de los castillos marcados y ninguno suma sin aceptarse.

### Fase 6. Cobertura de pruebas de lo reciente (M, 3 a 4 días; puede correr en paralelo a la 1)

Entregable: e2e de navegador de lo construido en D-627 a D-637 que hoy solo tiene pruebas de dominio y HTTP.

- Nuevos specs: `zm-conversion-del-enlace.spec.ts` (D-633), `zn-uniones-de-muro.spec.ts` (D-629), `zo-hoja-de-puerta.spec.ts` (D-632), `zp-matriz-que-cuenta.spec.ts` (D-636), `zq-cambio-de-unidad.spec.ts` (D-623), `zr-destajo-y-cuadrilla.spec.ts` (D-631), `zs-arbol-lugar.spec.ts` (D-634).
- Verificar que la vista previa de `ConversionDelEnlace.tsx` coincide con `app.cantidad_conversion` (una sola función de la base, F-3).
- Cerebro: sin cambios, salvo anotar la cobertura.
- Riesgo: bajo. Aceptación: cada decisión D-623 y D-627 a D-637 tiene al menos un e2e que la recorre de punta a punta.

### Fase 7. Catálogo con versiones, programación y plantillas (L, diferible)

Entregable: F-20, F-21, F-11, F-18, F-13, F-7, F-3 y la comparación automática de revisiones (fila 8). Ninguna de las dos primeras debe empezar sin decisión.

- F-20: versionar `elemento_parametrico` como `vano_version` (patrón de 0117), obras asignadas congeladas.
- F-21: segundo cuantificador con `ENLACE_CUANTIFICACION_PROGRAMA`, umbral 20 %, solicitud a Control.
- F-11: plantilla e instancia de trazo entre obras, solo cuando el cerebro defina qué se compara.
- F-13: dibujo del cuerpo continuo del muro.
- F-7: nuevos tipos de elemento uno por uno, cada uno con su definición previa.
- Riesgo: crecimiento sin dueño. Cada ítem se abre como decisión propia.

### Resumen del orden

1. Fase 0 (decisiones) y Fase 6 (e2e) arrancan ya y son baratas.
2. Fase 1 cierra lo parcial sin riesgo.
3. Fase 2 da el mayor valor para el castillo y la trabe en obra real.
4. Fase 3 es la más grande del mockup que la app no tiene.
5. Fase 4 espera decisión; fase 5 espera planos reales; fase 7 es diferible.

---

## 6. Notas de honestidad y límites de la auditoría

- Las cifras de conteo cuentan filas de la tabla 1; varios requisitos del cerebro se agrupan en una sola fila (por ejemplo D-633 es una fila aunque tiene dos etapas).
- No se ejecutó la app ni se corrieron las pruebas: el estado HECHO se basa en lectura de código, migraciones y especificaciones de pruebas. Donde el cerebro dice "construido" y el código lo confirma, se marcó HECHO.
- El mockup (337 KB) se revisó por funciones y etiquetas, no pixel por pixel.
- Lo que parece falta por comparar textos se verificó contra función: por ejemplo, el árbol de armado (D-634), el cambio de unidad (D-601, resuelto por D-623) y la "descripción corta" (D-622) sí están hechos; el cerebro mismo corrigió un caso así en D-634.

---

## Los paramétricos del cerebro y el Cuantificador (revisión del 2026-11-12)

Fuente: `1-mundo/fuentes/parametricos/` (catálogo de Zafiro 1.0 y Oro 4.01, `CATALOGO_PARAMETRICO.md`, `README.md`, `ESTABILIDAD.md`) y el skill `erp-parametrico` sección 7. **Dos cosas con el mismo apellido:** el *elemento paramétrico* de la app (castillo, trabe, zapata, losa; D-602, D-622, D-630) y el *catálogo paramétrico por drivers* (una magnitud que captura el usuario, p. ej. m² de muro o ml de barda, de la que sale la cantidad de cada partida). Esta revisión es del segundo.

**Regla del cerebro (skill `erp-parametrico`, sección 7):** el Cuantificador mide (plano → medida → cantidad) y el paramétrico **aprende de lo medido** (cantidad ÷ divisor → tasa). Si se construye sobre cantidades capturadas hereda sus errores y los disfraza de estadística. Por eso solo deben alimentarlo trazos medidos y **aprobados**.

| Driver del catálogo (Zafiro / Oro) | Lo que pide medir | Lo que el Cuantificador ya da | Brecha |
|---|---|---|---|
| MURO CONFINAMIENTO / MURO CAPAS / SILLAR (Oro: PB, PA y FACHADA) | m² de muro **neto** (el catálogo dice que lo base está neto) | Línea con grosor → largo × altura × caras, con vanos y uniones descontados (D-629, D-632, D-633) | Falta separar PB / PA / FACHADA y las capas como categoría del trazo; hoy la capa es texto libre del plano. |
| PRETIL | m² de pretil (franja a +3.00 con tope; lo que pasa de 3.00 es FACHADA) | Altura por partes: una parte hasta 3.00 y otra sobre 3.00 | Falta nombrar la franja de pretil como parte con significado (hoy es solo una parte que suma o no). |
| BARDA | ml de barda; castillo por piezas (+1 cada 3 ml) | Línea en ml; castillo como elemento por pieza | El escalón «+1 cada 3 ml» no existe como regla de escalamiento. |
| VANO | **perímetro** interior y de fachada; puertas, cancelería y domos **aparte** | Vanos con tipo (puerta, ventana, cancel, arco, paso), ancho, alto, piezas y versiones de catálogo (D-632, 0117) | Falta el total «perímetro de vanos» por interior y fachada como cantidad que alimente el driver, y marcar puertas, cancelería y domos como aparte. |
| LOSA (azotea, piso, entrepiso) | m² de cada losa; en Hoja1 las losas vienen como pieza global y se convierten a m² | Áreas en m²; conversión del enlace pieza ↔ m² (D-633) | Falta distinguir azotea, piso y entrepiso como categoría del área. |
| CIMENTACIÓN (D-312) | **área de desplante**, no el m² total (CV 6 % contra 21.5 %) | Cualquier área en m² | Falta un tipo de área «desplante» frente a «construida». Es la regla que más pesa en la dispersión. |
| PISO, ASADOR, PÓRFIDO, COCHERA | m² por zona; la cochera escala por escalones (+60 %, +160 %) | Áreas | Falta zona como categoría y el escalamiento por escalón. |
| HIDROSANITARIAS, GAS, ELÉCTRICAS | **salidas o puntos** por aparato | Conteo con punto con forma; conteo automático por plantilla (F2.4) | El conteo por simbología con IA sigue en espera (F-32). |
| ESCALERA (Oro) | **escalones**, escalable a lo largo, con spots cada 3 | Línea y conteo | No hay medición por escalones. |
| HERRERÍA, CARPINTERÍA, CANCELERÍA | fijos, editables | Conteo de vanos por tipo | Sin brecha de medición; el cerebro los deja fijos por ahora. |

**Propuestas (sin construir; requieren decisión del usuario):**

- **F-22 Categoría del trazo.** Un campo opcional que diga a qué driver y capa pertenece un trazo o un área (muro PB, PA o fachada; pretil; barda; losa azotea, piso o entrepiso; desplante frente a construida; zona de piso). Es la base de las demás.
- **F-23 Resumen por driver.** Una vista que sume lo medido y **aprobado** por driver y capa, con su unidad (m², ml, m de perímetro, salidas), lista para compararse con el valor base del catálogo. Sin trazos aprobados, el driver sale vacío y no se rellena con una cifra capturada.
- **F-24 Perímetro de vanos.** El total de perímetro de los vanos, interior y de fachada, por separado de puertas, cancelería y domos.
- **F-25 Escalamiento por escalón y por piezas.** La regla «+1 castillo cada 3 ml» y los escalones de la cochera como regla declarada, no como fórmula suelta.
- **F-26 Cohorte y dispersión junto a la tasa** cuando el resumen alimente un precio paramétrico: «un precio paramétrico sin su dispersión es un número disfrazado de certeza» (skill `erp-parametrico`, sección 5).

**Lo que no cambia:** el catálogo paramétrico nunca tuvo que cuadrar con el presupuesto (skill `erp-parametrico`, sección 2), y la diferencia contra Hoja1 (+$447.82 en Zafiro, +$20,175.71 en Oro) es el faltante del catálogo original, no un error. Tampoco se verificó el cuadre fuera de Python: los libros no guardan valores calculados.

