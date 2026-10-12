# DICCIONARIO DE DATOS

```
órgano:     —
capa:       I — Mundo
pregunta:   ¿qué renglones hay que corregir?
tiempo:     es así
corte:      2026-10-12
verificado: Reconstruido contra los catálogos vigentes (2026-09-10) · §1 releída contra `CATALOGO_DE_PRESUPUESTO.csv` el 2026-10-12: 9 de sus 10 grupos salen idénticos · §2 a §6 sin releer: el método que dio sus conteos no está escrito
```

> **Los datos concretos a corregir.** Qué homologar, qué es equivalente, qué está
> repetido.
>
> El vocabulario del oficio vive en `GLOSARIO-DOMINIO.md`; qué hay que hacer, en
> `PENDIENTES-MEJORAS.md`. Aquí están **los renglones**.
>
> Reconstruido contra los catálogos vigentes · 2026-09-10

---

## La regla que no se rompe

> **La clave nunca se reescribe.** `ISN-02001` sigue existiendo aunque sea
> duplicado de otro. Hay estimaciones y contratos apuntando ahí.
>
> Todo lo de aquí es **una capa encima**, no una reescritura.

## Estados

| Estado | Significado |
|---|---|
| `propuesto` | Esperando revisión |
| `aprobado` | Se aplica en el ERP |
| `rechazado` | **No se borra**: evita que se vuelva a proponer |
| `informativo` | Solo para conocimiento, no es un cambio |

---

## Ya resuelto — no volver a listarlo

| Qué | Cómo |
|---|---|
| Unidades sin normalizar | Corregidas en los cinco catálogos vigentes |
| Acentos que partían términos | 381 descripciones de concepto corregidas |
| Erratas fijas | `nescesario` ×32, `cosina` ×2 |
| Familias y subfamilias con errata | `Cosumible`, `Impearmeabilizante`, `Pegapiso `, `Marmol`/`Marmoles` |
| Frentes duplicados | `Equipamientos` unificado a `Equipamiento` |
| Familia `Auxiliar` que no informaba | Los 79 reasignados por naturaleza |

---

## 1. Conceptos con el mismo núcleo — `propuesto`

**10 grupos, 20 conceptos.** Misma descripción, claves distintas.

> *Releído el 2026-10-12 contra `1-mundo/opus/CATALOGO_DE_PRESUPUESTO.csv`:* **9 de los 10 son idénticos** (mismo
> texto completo, tras quitar acentos y signos). El décimo, `IEC-01010` ≡ `IEC-01011`, **no lo es**: el texto largo dice
> «desarrollo de 5.00 m» en uno y «4.00 m» en el otro, y la línea cortada a 70 caracteres de abajo lo escondía.
> Es una variante dimensional (§3), no un duplicado; los PU distintos de la fila ya lo anticipaban. Aparece también en las
> familias de dos miembros de §2.

> Van a **tabla de equivalencia**. No se fusionan.

| Claves | Núcleo | Unidad | PU |
|---|---|---|---|
| `ACC-00001` ≡ `ACC-00003` | Material adicional y de consumo | ACT | 159.72 · 0.00 |
| `ALB-01110` ≡ `ALB-01112` | Repellado en plafond a una altura de 3.00 mts, con mezcla mortero-aren | M2 | 169.88 · 174.88 |
| `CAN-01001` ≡ `CAN-01011` | Canceleria oro | SERV | 43,022.75 · 39,489.53 |
| `CAR-01030` ≡ `ICA-01030` | Colocación de durmiente 20x20 cm en vanos de fachada, | PZ | 1,080.00 · 1,080.00 |
| ⚠️ `IEC-01010` ≡ `IEC-01011` | Salida eléctrica para contacto, ahogado en piso o en losa a base de po (**5.00 m contra 4.00 m**) | SAL | 71.33 · 67.20 |
| `IGAS-02131` ≡ `IGAS-02132` | Caja de valvulas GAS PRO, valvulas de paso y codos 3/8" modelo RUBI | SAL | 0.00 · 0.00 |
| `IHD-02202` ≡ `IHD-02203` | Linea alimentacion cisterna-hidroneumatico de CPVC de 1" desarrollo 12 | SAL | 531.39 · 267.39 |
| `ISN-02001` ≡ `ISN-02005` | Linea principal sanitaria de pvc de 6" desarrollo 24.00 mts | SAL | 5,419.73 · 3,640.26 |
| `ISN-02002` ≡ `ISN-02004` | Linea principal sanitaria de pvc de 6" desarrollo 30.00 mts | SAL | 4,501.78 · 5,142.81 |
| `ISN-02060` ≡ `ISN-02061` | Ranura y conexión sanitaria para tarja de pvc de 2" en muro | SAL | 61.27 · 0.00 |

> **Ojo con los PU distintos.** Si dos conceptos idénticos cuestan diferente, uno
> de los dos está mal — o no son idénticos y la descripción no lo dice.

---

## 2. Familias de concepto — `propuesto`

**19 familias**, 49 conceptos. El mismo trabajo repetido por variante.

**10 varían por prototipo.**

> Hoy nada los relaciona: si mejoras el APU de uno, los otros no se enteran.


**Canceleria** — 9 miembros · prototipos: Diamante, Jade, Oro, Rubi, Zafiro, Zafiro Plus

| Clave | Núcleo | PU |
|---|---|---|
| `CAN-01001` | Canceleria oro | 43,022.75 |
| `CAN-01002` | Canceleria zafiro planta baja | 53,220.00 |
| `CAN-01004` | Canceleria JADE planta baja | 60,615.00 |
| `CAN-01006` | Canceleria RUBI planta baja | 54,785.50 |
| `CAN-01008` | Canceleria Diamante planta baja | 70,607.18 |
| `CAN-01009` | Canceleria Diamante ROOF | 39,999.30 |
| `CAN-01011` | Canceleria oro | 39,489.53 |
| `CAN-01021` | Canceleria ZAFIRO PLUS planta baja | 55,336.40 |
| `CAN-01022` | Canceleria ZAFIRO PLUS planta alta | 40,695.40 |

**Closet Recamara 2** — 3 miembros · prototipos: Diamante, Oro, Zafiro

| Clave | Núcleo | PU |
|---|---|---|
| `CAR-02080` | CLOSET RECAMARA 2 ZAFIRO | 20,100.00 |
| `CAR-04090` | CLOSET RECAMARA 2 DIAMANTE | 18,500.00 |
| `CAR-04130` | CLOSET RECAMARA 2 ORO | 24,000.00 |

**Caja De Valvulas Gas Pro Valvulas De Paso Y Codos 3 8 Modelo** — 3 miembros · prototipos: Rubi, Zafiro

| Clave | Núcleo | PU |
|---|---|---|
| `IGAS-02130` | Caja de valvulas GAS PRO, valvulas de paso y codos 3/8" modelo | 1,330.00 |
| `IGAS-02131` | Caja de valvulas GAS PRO, valvulas de paso y codos 3/8" modelo | 0.00 |
| `IGAS-02132` | Caja de valvulas GAS PRO, valvulas de paso y codos 3/8" modelo | 0.00 |

**Cocina** — 3 miembros · prototipos: Oro, Rubi, Zafiro

| Clave | Núcleo | PU |
|---|---|---|
| `CAR-03020` | COCINA ZAFIRO | 65,060.00 |
| `CAR-03040` | COCINA RUBI | 78,060.00 |
| `CAR-05050` | COCINA ORO | 103,740.00 |

**Vestidor Recamara 3** — 3 miembros · prototipos: Diamante, Oro, Zafiro

| Clave | Núcleo | PU |
|---|---|---|
| `CAR-02110` | VESTIDOR RECAMARA 3 ZAFIRO | 21,384.00 |
| `CAR-04110` | VESTIDOR RECAMARA 3 DIAMANTE | 21,384.00 |
| `CAR-04140` | VESTIDOR RECAMARA 3 ORO | 18,500.00 |

**Familias de 2 miembros** (14)

| Claves | Núcleo |
|---|---|
| `ACA-01070` · `ACA-01071` | Boquilla A Base De Mortero Fino |
| `CAR-02100` · `CAR-04020` | Alacena Cocina |
| `CAR-01030` · `ICA-01030` | Colocacion De Durmiente 20X20 Cm En Vanos De |
| `CAN-01005` · `CAN-01007` | Domos |
| `IHD-02202` · `IHD-02203` | Linea Alimentacion Cisterna Hidroneumatico De Cpvc De 1 Desarrollo 12  |
| `CAR-05030` · `CAR-05040` | Cocina Estandar Modelo |
| `ISN-02001` · `ISN-02005` | Linea Principal Sanitaria De Pvc De 6 Desarrollo 24 00 Mts |
| `ISN-02002` · `ISN-02004` | Linea Principal Sanitaria De Pvc De 6 Desarrollo 30 00 Mts |
| `ISN-02060` · `ISN-02061` | Ranura Y Conexion Sanitaria Para Tarja De Pvc De 2 En Muro |
| `ACC-00001` · `ACC-00003` | Material Adicional Y De Consumo |
| `ALB-01110` · `ALB-01112` | Repellado En Plafond A Una Altura De 3 00 Mts Con Mezcla Mortero Arena |
| `IEC-01010` · `IEC-01011` | Salida Electrica Para Contacto Ahogado En Piso O En Losa A Base De Pol |
| `CAR-04010` · `CAR-05010` | Vestidor Recamara Modelo |
| `CAR-04080` · `CAR-04120` | Vestidor Recamara1 |

---

## 3. Equivalencias y variantes

- **77 variantes dimensionales** — difieren solo en un número. *No son duplicados* → `informativo`
- **133 casi idénticos** — requieren criterio → `propuesto`

### Variantes dimensionales — las 20 más parecidas

| A | B | Núcleo |
|---|---|---|
| `EST-20017` | `EST-20022` | LOSA NERVADA DE 25 CM DE ESPESOR DIAMANTE ENTREPISO DE 63 M2 CON C |
| `EST-10020` | `EST-10021` | COLOCACION DE ACERO EN CIMENTACION K2 ARMADO CON 4 VAR DE NO 3 Y E |
| `IEC-01130` | `IEC-01132` | SALIDA VOZ Y DATOS PARA ACOMETIDA AHOGADO EN PISO O EN LOSA A BASE |
| `ACA-11013` | `ACA-11014` | FORRADO DE COLUMNA 40X50 CM 4 CARAS CON PIEDRA GALARZA CON ADHESIV |
| `ACA-11013` | `ACA-11015` | FORRADO DE COLUMNA 40X50 CM 4 CARAS CON PIEDRA GALARZA CON ADHESIV |
| `EST-02010` | `EST-02020` | MURO DE 14 CM DE ESPESOR DE TABIQUE ROJO RECOCIDO ASENTADO CON MEZ |
| `ISN-01131` | `ISN-01132` | SALIDA SANITARIA PARA MINI SPLIT DE PVC HD DE 1 2 DESARROLLO 6 00  |
| `EST-10010` | `EST-10011` | COLOCACION DE ACERO EN CIMENTACION K1 ARMADO CON ARMEX DE 10X10 4  |
| `EST-10070` | `EST-10071` | COLOCACION DE ACERO EN CIMENTACION K7 ARMADO CON ARMEX DE 10X15 HA |
| `EST-10070` | `EST-10072` | COLOCACION DE ACERO EN CIMENTACION K7 ARMADO CON ARMEX DE 10X15 HA |
| `EST-10071` | `EST-10072` | COLOCACION DE ACERO EN CIMENTACION K7 ARMADO CON ARMEX DE 10X15 HA |
| `EST-52010` | `EST-52040` | LOSA MACIZA MZ 01 DE 12 CM DE ESPESOR ZAFIRO PLUS 47 M2 A 3 00 DE  |
| `EST-52020` | `EST-52040` | LOSA MACIZA MZ 02 DE 12 CM DE ESPESOR ZAFIRO PLUS 22 M2 A 3 00 DE  |
| `EST-52030` | `EST-52040` | LOSA MACIZA MZ 03 DE 12 CM DE ESPESOR ZAFIRO PLUS 16 M2 A 3 00 DE  |
| `IEC-01010` | `IEC-01012` | SALIDA ELECTRICA PARA CONTACTO AHOGADO EN PISO O EN LOSA A BASE DE |
| `IEC-01011` | `IEC-01012` | SALIDA ELECTRICA PARA CONTACTO AHOGADO EN PISO O EN LOSA A BASE DE |
| `IEC-01100` | `IEC-01110` | SALIDA ELECTRICA ACOMETIDA PARA PANELES SOLARES SOBRE MURO Y O CAS |
| `EST-10012` | `EST-10013` | COLOCACION DE ACERO K1 ARMADO CON ARMEX DE 10X10 4 HASTA 1 50 M DE |
| `EST-52010` | `EST-52030` | LOSA MACIZA MZ 01 DE 12 CM DE ESPESOR ZAFIRO PLUS 47 M2 A 3 00 DE  |
| `EST-52010` | `EST-52020` | LOSA MACIZA MZ 01 DE 12 CM DE ESPESOR ZAFIRO PLUS 47 M2 A 3 00 DE  |

### Casi idénticos — los 30 más parecidos

| A | B | Similitud | Núcleo |
|---|---|---|---|
| `ALB-01210` | `ALB-01212` | 0.99 | REPELLADO EN MUROS DE FACHADA A UNA ALTURA DE 3 00 MTS CON M |
| `ALB-01010` | `ALB-01012` | 0.989 | REPELLADO EN MUROS A UNA ALTURA DE 3 00 MTS CON MEZCLA MORTE |
| `EST-01053` | `EST-01054` | 0.989 | LOSA DE CIMENTACION DIAMANTE 216 M2 CON CHIMENEA CON CONCRET |
| `EST-51010` | `EST-51016` | 0.982 | LOSA NERVADA DE 0 20 DE ESPESOR ORO 4 01 AZOTEA DE 140 M2 DE |
| `IEC-10040` | `IEC-10130` | 0.982 | CABLEADO CONTACTO DUPLEX 1 CABLE CAL 12 NEGRO 1 CABLE CAL 12 |
| `ACA-01010` | `ACA-01020` | 0.978 | APLANADO ACABADO FINO EN MUROS A UNA ALTURA MAXIMA DE 3 00 M |
| `EST-21011` | `EST-51110` | 0.975 | LOSA MACIZA DE 12 CM DE ESPESOR ZAFIRO 125 M2 A 3 00 DE ALTU |
| `IEC-01010` | `IEC-01210` | 0.975 | SALIDA ELECTRICA PARA CONTACTO AHOGADO EN PISO O EN LOSA A B |
| `IEC-01011` | `IEC-01210` | 0.975 | SALIDA ELECTRICA PARA CONTACTO AHOGADO EN PISO O EN LOSA A B |
| `IEC-01060` | `IEC-01063` | 0.975 | SALIDA ELECTRICA PARA ACOMETIDA AHOGADO EN PISO O EN LOSA A  |
| `IEC-01060` | `IEC-01062` | 0.975 | SALIDA ELECTRICA PARA ACOMETIDA AHOGADO EN PISO O EN LOSA A  |
| `EST-30012` | `EST-51110` | 0.972 | LOSA MACIZA DE 10 CM DE ESPESOR RUBI 93 M2 A 3 00 DE ALTURA  |
| `IEC-01020` | `IEC-01030` | 0.967 | SALIDA ELECTRICA PARA ZUMBADOR AHOGADO EN PISO O EN LOSA A B |
| `ISN-02020` | `ISN-02070` | 0.967 | RANURA Y CONEXION SANITARIA PARA LAVADERO DE PVC DE 2 EN MUR |
| `EST-10010` | `EST-10070` | 0.966 | COLOCACION DE ACERO EN CIMENTACION K1 ARMADO CON ARMEX DE 10 |
| `EST-10011` | `EST-10071` | 0.966 | COLOCACION DE ACERO EN CIMENTACION K1 ARMADO CON ARMEX DE 10 |
| `EST-21011` | `EST-52030` | 0.966 | LOSA MACIZA DE 12 CM DE ESPESOR ZAFIRO 125 M2 A 3 00 DE ALTU |
| `IEC-01030` | `IEC-01210` | 0.966 | SALIDA ELECTRICA PARA TIMBRE AHOGADO EN PISO O EN LOSA A BAS |
| `ISN-01030` | `ISN-01031` | 0.964 | SALIDA SANITARIA PARA LAVAMANOS DE PVC DE 2 DESARROLLO 2 00  |
| `IEC-01012` | `IEC-01210` | 0.963 | SALIDA ELECTRICA PARA CONTACTO AHOGADO EN PISO O EN LOSA A B |
| `IHD-01020` | `IHD-01110` | 0.963 | SALIDA HIDRAULICA PARA LAVADERO DE TUBERIA CPVC DE 1 2 |
| `EST-30013` | `EST-51110` | 0.962 | LOSA MACIZA DE 10 CM DE ESPESOR RUBI 46 M2 A 4 20 DE ALTURA  |
| `EST-21011` | `EST-52020` | 0.961 | LOSA MACIZA DE 12 CM DE ESPESOR ZAFIRO 125 M2 A 3 00 DE ALTU |
| `IEC-11060` | `IEC-11080` | 0.961 | APAGADOR DOBLE ESCALERA CON PLACA METALICA CONSIDERANDO 2 IN |
| `EST-20010` | `EST-30013` | 0.96 | LOSA MACIZA DE 11 CM DE ESPESOR DIAMANTE 39 M2 A 4 20 DE ALT |
| `IEC-01020` | `IEC-01050` | 0.959 | SALIDA ELECTRICA PARA ZUMBADOR AHOGADO EN PISO O EN LOSA A B |
| `IHD-02020` | `IHD-02110` | 0.959 | RANURA Y CONEXION HIDRAULICA PARA LAVADERO DE 1 2 |
| `IGAS-02050` | `IGAS-02140` | 0.956 | RANURA Y CONEXION GAS PRO PARA SECADORA DE 3 8 |
| `ISN-01040` | `ISN-01041` | 0.956 | SALIDA SANITARIA PARA WC DE PVC DE 4 CODO 4X90 SAL LATERAL C |
| `ACA-01010` | `ACA-01030` | 0.955 | APLANADO ACABADO FINO EN MUROS A UNA ALTURA MAXIMA DE 3 00 M |

*Se muestran 30 de 133.*

---

## 4. Textos de alcance — `propuesto`

**34 formas canónicas** cubren **408 conceptos** de 470.

> Sacarlos de la descripción quita entre el 40% y el 70% del texto de cada
> concepto. Hoy todos se parecen entre sí porque comparten la cola.

| # | Conceptos | Texto |
|---|---|---|
| ALC-001 | 60 | limpieza, tuberia, conexiones, pegamento, materiales, mano de obra, herramienta, equipo  |
| ALC-002 | 59 | limpieza, materiales, mano de obra, herramienta, equipo y todo lo necesario para su corr |
| ALC-003 | 56 | limpieza, material, mano de obra, herramienta, y todo lo necesario para su correcta ejec |
| ALC-004 | 32 | limpieza, accesorios, mano de obra, herramienta, equipo y todo lo necesario para su corr |
| ALC-005 | 23 | limpieza, trazo, presentacion, corte, fijacion, mano de obra, material, pruebas para su  |
| ALC-006 | 22 | limpieza, suministro, colocacion, cables, conectores, elementos de sujecion, cinta de ai |
| ALC-007 | 22 | limpieza, tuberia, conexiones, pruebas, material, mano de obra, herramienta, equipo y to |
| ALC-008 | 19 | limpieza, suministro, colocacion, cables, conectores, elementos de sujecion, cinta de ai |
| ALC-009 | 14 | limpieza, pruebas, herramienta y mano de obra necesarias para su correcta instalacion |
| ALC-010 | 12 | cimbra, decimbrado, vaciado, mano de obra, equipo y herramienta, equipo y todo lo necesa |
| ALC-011 | 11 | limpieza, cimbra, descimbra, colado y vibrado, material, mano de obra, herramienta, equi |
| ALC-012 | 11 | limpieza, material, mano de obra, herramienta, equipo y todo lo necesario para su correc |

*Se muestran 12 de 34.*

---

## 5. Grupos funcionales de material

**5 grupos, 13 materiales.**

> Salió corto y hay que decirlo: solo se detectan grupos por **color**. Para los
> que de verdad sirven —mismo material en distinta presentación— hace falta
> definir la unidad base de cada material. Es aritmética, no comparación de texto.

| Grupo | Clave | Descripción | Unidad | Costo | Atributo | Alerta |
|---|---|---|---|---|---|---|
| Cable 10 | `ELE-00031` | CABLE BLANCO 10 | RLL | 1,474.51 | Blanco |  |
| Cable 10 | `ELE-00032` | CABLE NEGRO 10 | RLL | 1,474.51 | Negro |  |
| Cable 12 | `ELE-00028` | CABLE NEGRO 12 | RLL | 933.01 | Negro |  |
| Cable 12 | `ELE-00029` | CABLE BLANCO 12 | RLL | 933.01 | Blanco |  |
| Cable 14 | `ELE-00025` | CABLE ROJO 14 | RLL | 664.50 | Rojo |  |
| Cable 14 | `ELE-00026` | CABLE BLANCO 14 | RLL | 664.50 | Blanco |  |
| Cable 14 | `ELE-00027` | CABLE NEGRO 14 | RLL | 664.50 | Negro |  |
| Cable 14 | `ELE-00030` | CABLE VERDE 14 | RLL | 664.50 | Verde |  |
| Cable 8 | `ELE-00078` | CABLE NEGRO 8 | RLL | 2,140.00 | Negro |  |
| Cable 8 | `ELE-00294` | CABLE BLANCO 8 | RLL | 2,140.00 | Blanco |  |
| Cable 8 | `ELE-00321` | CABLE ROJO 8 | RLL | 2,140.00 | Rojo |  |
| Poliflex 50 Mts 1" 5L | `ELE-00044` | POLIFLEX NARANJA 50 MTS 1" 5L | PZ | 580.00 | Naranja | PRESENTACIONES DISTINTAS |
| Poliflex 50 Mts 1" 5L | `ELE-00046` | POLIFLEX NARANJA 50 MTS 1" 5L | M | 29.00 | Naranja | PRESENTACIONES DISTINTAS |

---

## 6. Los dos casos que parecían error de precio — ninguno lo era (D-323)

| Caso | Por qué parecía error | Qué es en realidad |
|---|---|---|
| **Poliflex naranja** | `ELE-00044` en PZ a $580 y `ELE-00046`, descripción idéntica, en M a $29 | **Presentaciones reales distintas**, no error — confirmado con ingeniería real de `ALAMO 18`: `ELE-00044` es el rollo completo (50 M), `ELE-00046` el metro suelto. El metro suelto cuesta más por metro equivalente ($29 contra $11.60 del rollo), normal al menudeo. Ya estaba bien marcado en §5 ("PRESENTACIONES DISTINTAS") |
| **Pija lámina** | `COM-00200` en CJ a $8.96 y `ELE-00048` en PZ a $0.50 — y en dos familias distintas | **No es el mismo material.** `COM-00200` es pija 8×1/2"; `ELE-00048` es pija 8×1 1/2" — tres veces más larga. El nombre corto coincide, la descripción completa no |

> Los dos quedan cerrados sin corrección de catálogo — `PENDIENTES-MEJORAS.md` M-17/M-18, `MEMORIA.md` D-323.

## Familias: el catálogo sin acentuar contra el uso acentuado

Nueve familias están escritas de dos formas. **La acentuada es la canónica** — es la
del dato real; el catálogo es el que está mal.

| Catálogo (corregir) | Uso (canónico) |
|---|---|
| `Albañileria` | **Albañilería** |
| `Canceleria` | **Cancelería** |
| `Carpinteria` | **Carpintería** |
| `Electrico` | **Eléctrico** |
| `Herrerias` | **Herrerías** |
| `Hidraulico` | **Hidráulico** |
| `Impermeabilizacion` | **Impermeabilización** |
| `Pergolas` | **Pérgolas** |
| `Petreos` | **Pétreos** |

> Verificado: normalizando acentos, las nueve colapsan uno a uno. **Ninguna es
> ambigua** — no hay dos familias distintas que se confundan al quitar el acento.

