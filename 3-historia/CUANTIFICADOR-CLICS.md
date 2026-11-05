# Los clics de cada herramienta del Cuantificador

Revisado el 2026-11-05 contra el código (`Visor.tsx`, `Cuantificador.tsx`) y el mockup. «Derecho» es el clic sin arrastrar;
arrastrar con el derecho o con el botón de la rueda **mueve el plano** con cualquier herramienta; la rueda hace zoom; con dos
dedos, pellizco y arrastre.

| Herramienta | Clic izquierdo | Clic derecho | Teclado |
|---|---|---|---|
| **Seleccionar** | Elige trazo, nota o vano (Mayús/Ctrl suma). Arrastrar dibuja una ventana: hacia abajo elige lo que cubre por completo, hacia arriba lo que toca. Sobre las asas de un vano lo mueve o le cambia el ancho. | Menú del trazo (Mover, Girar 90° izquierda/derecha, Borrar) o, si hay un vano bajo el cursor, el del vano. | Supr / Retroceso borra lo elegido (también un vano). Esc suelta. |
| **Mano** | Nada (arrastrar mueve el plano). | Nada. | — |
| **Zoom** | Acerca (Mayús o Alt aleja). | **Aleja** (nuevo). | — |
| **Polígono, Polilínea, Contorno** | Un vértice por clic. En Contorno, un clic sobre el primer vértice cierra. | **Termina** la figura (como Intro) si ya tiene los puntos mínimos; si no, la cancela (nuevo). | Intro termina · Retroceso quita el último vértice · Esc cancela · T cambia recto/arco en Contorno. |
| **Rectángulo, Círculo, Elipse, Arco, Línea** y sus variantes lineales | Dos o tres clics según la figura; el último guarda el trazo. | Cancela la figura a medias (como Esc) (nuevo). | Esc cancela. |
| **Punto** | Una pieza; con una forma elegida estampa su polígono; con «Colocar este elemento» lo marca como el elemento. | Nada (o el menú de un vano si hay uno bajo el cursor). | — |
| **Hueco** | Un vértice del hueco dentro del área elegida. | Cierra el hueco si tiene 3 puntos; si no, lo descarta (nuevo). | Intro cierra · Retroceso quita el último · Esc cancela. |
| **Vano** | Coloca el vano en el muro, línea o área bajo el clic (por línea, dos clics). | Menú del vano si hay uno bajo el cursor. | Esc vuelve a Seleccionar. |
| **Copiar en lote** | Copia la pieza elegida en el punto. | Nada. | Esc vuelve a Seleccionar. |
| **Mover** | Dos clics: punto base y destino. | Menú del trazo. | Esc cancela. |
| **Borrar** | Sobre un trazo pide borrarlo; **sobre un vano lo quita** (no el muro) (nuevo); sobre una zona de enlace la quita. | Nada. | Supr borra lo elegido. |
| **Nota** | Coloca la nota o el texto; flecha y llamada llevan dos clics. | Nada. | — |
| **Calibrar escala / Conteo automático / Enlace entre hojas** | Dos puntos o dos esquinas; al segundo pide el dato. | Nada. | Esc cancela. |

**Lo que cambió en esta revisión**
- Las puertas (vanos) ahora se borran con Supr, con «Eliminar selección» y con la herramienta Borrar; antes solo con «Quitar el vano» del detalle.
- El clic derecho con una herramienta de dibujo termina o cancela la figura, y con Zoom aleja; antes no hacía nada.

**Diferencias con el mockup, sin cambiar**
- En el mockup, el clic derecho con una herramienta de línea abre el menú de uniones del muro; en la app las uniones se eligen en el detalle del trazo.
