# CASO TRABAJADO

```
órgano:     memoria episódica
capa:       III — Historia
pregunta:   ¿cómo se ve todo junto?
tiempo:     fue así
corte:      2026-09-10
verificado: Un caso de punta a punta · 12 reglas
```

> **Un solo caso, de punta a punta.** Todas las reglas del modelo aparecen aquí,
> aplicadas sobre datos reales.
>
> Sirve de dos formas: para entender el modelo en la mitad del tiempo, y como
> **prueba del conocimiento** — todo lo que sigue está en los archivos.
>
> 2026-09-10

---

## El caso

La **losa de cimentación del prototipo Diamante con chimenea**, y dentro de ella una
zapata que resulta ser el ejemplo perfecto de las reglas más difíciles.

---

## 1. Dónde vive en el presupuesto

```
Nivel 0  Capítulo      CAS-00007  DIAMANTE CON CHIMENEA (239 m²)     $2,829,925.98
Nivel 1  Subcapítulo   NIV-00001  CIMENTACIÓN                          $259,315.61
Nivel 2  Nivel 2       ECO-00001  ESTRUCTURA CIM                       $214,257.37
Nivel 3  Nivel 3       EST-01080  LOSA CIMENTACIÓN DIAMANTE            $214,257.37
Nivel 4  Concepto      EST-01053  LOSA CIMENTACIÓN DIAMANTE C/CH       $185,864.48
Nivel 4  Concepto      EST-10011  K1 - 6.00 ACERO         61 pza         $8,589.41
```

**Tres reglas visibles de un vistazo:**

- El `Nivel 3` **es un concepto auxiliar**: agrupa la losa con sus castillos. Su
  importe es la suma de sus hijos, no un dato propio.
- El concepto `EST-01053` cuelga de él en **Nivel 4**; el castillo `EST-10011`
  también. **El tipo no lo determina la profundidad.**
- El capítulo se llama Diamante, pero **capítulo no significa prototipo**: aquí se
  usa así.

> **Cómo se sabe quién cuelga de quién:** por **orden de fila más profundidad**, no
> por el código. Extraer este prototipo filtrando por `Ingenieria ERP` deja fuera 11
> filas y el total sale $34,946 corto.

---

## 2. La matriz del concepto

`EST-01053` se explota en 20 líneas. Las que importan para el caso:

| Clave | Descripción | Cantidad | Costo | Importe | Tipo |
|---|---|---|---|---|---|
| CON-00001 | Concreto TD 200 | 34 M3 | 2,442.33 | 83,039.22 | Material |
| MOC-01010 | MO losa de cimentación | 216 M2 | 230.00 | 49,680.00 | **Contrato** |
| AUX-01011 | Contratrabe CT1 | 137 M | 146.79 | 20,110.23 | Material |
| AUX-00030 | Malla electrosoldada | 216 M2 | 45.72 | 9,875.52 | Material |
| **ZA1-000001** | **Zapata ZA-1** | **6 PZ** | **1,135.48** | **6,812.88** | **Material** |
| MAD-00004 | Tablas | 10 PZ | 198.00 | 1,980.00 | **Flete** |
| ACR-00002 | Varilla 1/2 | **−0.656 PZ** | 237.52 | **−155.81** | Material |

**Cuatro cosas que enseña esta matriz:**

**El concepto mezcla categorías.** Material, Contrato y Flete conviven. La regla de
homogeneidad no existe.

**Hay cantidades negativas.** `−0.656` de varilla, `−0.196` de varilla 3/8. Son
ajustes: descuentan acero que ya está contado dentro de un auxiliar. **El modelo
debe permitirlas.**

**Un material puede ser en realidad un flete.** `MAD-00004 Tablas` tiene `Tipo =
Flete` — es el caso de un insumo apartado en esa categoría.

**Y cinco de sus líneas son compuestos**, marcados `AUX-` y `ZA1-`. Se abren.

---

## 3. La zapata: el caso que lo explica todo

```
ZA1-000001   Zapata ZA-1 1.00×1.00        PZ     $1,135.48
             Familia: Elemento Estructural · Subfamilia: Zapata · Tipo: Material
             C = «+»  → se abre
```

Su matriz:

| Clave | Descripción | Cantidad | Costo | Importe | Tipo | Origen |
|---|---|---|---|---|---|---|
| ACR-00002 | Varilla 1/2 | 2.76 PZ | 237.52 | 655.56 | Material | Material |
| ACE-00001 | Alambre recocido | 0.807 KG | 24.68 | 19.92 | Material | Material |
| **MOC-12010** | **MO Zapata ZA-1** | 1 PZ | 460.00 | **460.00** | **Contrato** | **Material** |
| | | | | **1,135.48** | | |

### Aquí está todo

**Suma exacta.** Los tres componentes dan $1,135.48, el mismo costo unitario del
catálogo. Verificado en los 89 compuestos: **los 89 cuadran al centavo.**

**El 41% de esta zapata es mano de obra contratada** — $460 de $1,135.48. Y aun así:

| Columna | Dice | Es |
|---|---|---|
| `Tipo` = **Contrato** | La naturaleza de la línea | **El ADN** |
| `Origen` = **Material** | La categoría del padre | **A qué reporta el monto** |

> **La zapata reporta 100% como material**, aunque lleve un contrato adentro. Y está
> bien: para la obra, esa zapata *es* un material — solo que lo produces tú.
>
> Es exactamente el caso de fabricar tu propio tabique.

**Y OPUS ya guarda las dos lecturas en columnas separadas.** No hubo que inventar el
mecanismo: estaba ahí.

---

## 4. Las dos lecturas, sobre este caso

Los 6 pza de zapata dentro del concepto:

```
REPORTE DE MONTOS — se detiene en el compuesto
  Material   $6,812.88   ← la zapata entera, incluido su contrato

EXPLOSIÓN DE INSUMOS — llega al fondo
  ACR-00002  Varilla 1/2        16.56 PZ    Material
  ACE-00001  Alambre recocido    4.84 KG    Material
  MOC-12010  MO Zapata ZA-1      6.00 PZ    Contrato   ← reaparece
```

**Suman lo mismo. Dicen cosas distintas.**

- La primera contesta *¿cuánto de esta obra es material?*
- La segunda contesta *¿qué hay que comprar y a quién hay que contratar?*

> Sin la segunda, **esos $2,760 de mano de obra desaparecerían de la planeación**
> aunque estuvieran en el costo. Alguien tiene que pagarlos y programarlos.
>
> Y la comparación de almacén contra explosión tampoco funcionaría: el almacén surte
> varilla y alambre, no zapatas teóricas.

---

## 5. El destajo, y su rendimiento

`MOC-12010` en el catálogo de trabajos:

```
Tipo: Destajo · Familia: Obra Civil · Subfamilia: Zapata
$460.00 por PZ
```

**Tres rendimientos, y solo dos se capturan:**

| Rendimiento | Valor | De dónde |
|---|---|---|
| **Calculado** | costo cuadrilla ÷ 460 | Siempre existe. Nunca se captura |
| **Teórico** | migrado del catálogo anterior | Semilla, una sola vez |
| **Real** | — | Aún sin capturar |

Su diferencia **no es un error, es un indicador**: precio mal puesto, cuadrilla
equivocada, o productividad distinta a la supuesta.

> Comprobado: al comparar los 265 trabajos, la razón entre calculado y teórico dio
> **1.085 en los 22 trabajos de pintor, sin variación.** No era desajuste: era que
> los rendimientos se calcularon con una cuadrilla que costaba 8.5% más.

---

## 6. Si mañana sube la varilla

Subir `ACR-00002` de $237.52 a $250:

```
1. La zapata ZA1-000001 sube            $1,135.48 → $1,169.92
2. El concepto EST-01053 sube            por sus 6 zapatas · y por la varilla suelta
3. El auxiliar EST-01080 sube            suma de sus hijos
4. La etapa, el nivel y el prototipo      cascada hasta arriba
```

**Nadie captura nada.** El precio vive en un solo lugar y todo lo demás se calcula.

> Verificado: los 39 insumos de la explosión de compuestos coinciden con su catálogo
> de origen, **sin un solo precio congelado dentro de una matriz**.

Y si el concepto ya estuviera contratado, el cambio **no lo toca**: el nodo
congelado se queda y el ajuste va por control de cambio.

---

## 7. Lo que este caso NO muestra

Para no dar por cubierto lo que sigue abierto:

| Falta | Dónde está |
|---|---|
| Indirectos, financiamiento, utilidad | No hay en ningún dato. `erp-construccion.md` §6 |
| De dónde salió el `216 M2` | Módulo de cuantificación, pendiente |
| Ensambles y paramétrico | Aún no existen |
| Programa, avance y estimaciones | Pendientes |
| La clasificación del concepto | `EST-01053` no tiene `Tipo`, `Familia` ni `Subfamilia` |

---

## Las reglas que este caso demuestra

| # | Regla | Dónde se ve |
|---|---|---|
| 1 | La jerarquía va **por orden y profundidad**, no por el código | `CATALOGOS.md` |
| 2 | **El tipo no lo determina la profundidad** | `CATALOGOS.md` |
| 3 | El auxiliar **es la suma de sus hijos**, no un dato propio | `CATALOGOS.md` |
| 4 | El concepto **mezcla categorías** | `CONOCIMIENTO.md` §1 |
| 5 | Las **cantidades negativas** son válidas | `CONOCIMIENTO.md` §1 |
| 6 | El compuesto **suma exacto** a su costo de catálogo | `CONOCIMIENTO.md` §2 |
| 7 | El compuesto **reporta a su categoría, entero** | `CONOCIMIENTO.md` §2 |
| 8 | `Tipo` es el ADN; `Origen` es el monto | `CONOCIMIENTO.md` §2 |
| 9 | **Dos lecturas** que suman lo mismo y dicen cosas distintas | `CONOCIMIENTO.md` §10.5 |
| 10 | **Tres rendimientos**, dos se capturan | `CONOCIMIENTO.md` §4 |
| 11 | El precio **vive en un solo lugar** | `CONOCIMIENTO.md` §5 |
| 12 | Lo contratado **no se reescribe** | `CONOCIMIENTO.md` §5 |
