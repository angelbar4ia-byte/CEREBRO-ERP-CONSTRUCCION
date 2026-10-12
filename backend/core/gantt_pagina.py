"""
Las pantallas del programa como páginas sueltas — `frontend/gantt/` y `1-mundo/PROGRAMA-CPM.md` §4.8 y §8.

Cada pantalla es un solo HTML que se abre solo: la plantilla, los colores compartidos (`tokens.css`), el cliente de la
API (`cliente_programa.js`, generado del spec, D-55), la sesión (`sesion.js`) y, en el Gantt, el motor que reprograma en
el navegador (`motor_gantt.js`, que una prueba contrasta con `reprogramar`).

Dos Gantt: la simulación (`pagina_gantt`), con el programa dentro de la página, y el que sirve la API
(`pagina_gantt_en_vivo`), **sin ningún dato**: los pide ya con el token (B-96). La lista de programas tampoco lleva datos.

Lo que viene de quien subió el programa —su nombre, las descripciones, las claves— es texto de otro: el título se
escapa aquí y los datos viajan como JSON sin un solo `<`; la plantilla escapa todo lo que dibuja.
"""
from __future__ import annotations

import html
import json
import re
from datetime import date
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

from .motor_cpm import Calendario
from .programa import Programa, vista_gantt

FRONTEND = Path(__file__).resolve().parents[2] / "frontend" / "gantt"


def _leer(nombre: str) -> str:
    return (FRONTEND / nombre).read_text(encoding="utf-8")


def _armar(plantilla: str, valores: Dict[str, str]) -> str:
    """Pone cada marca en su lugar de una sola pasada: lo que se inserta no se vuelve a leer, así que un título que
    se parezca a una marca no sustituye nada."""
    faltan = [m for m in valores if m not in plantilla]
    if faltan:
        raise ValueError(f"la plantilla ya no tiene {', '.join(faltan)}")
    return re.sub("|".join(re.escape(m) for m in valores), lambda m: valores[m.group(0)], plantilla)


def _json_seguro(datos: Any) -> str:
    """Un `<` solo puede estar dentro de un texto del JSON: escrito `\\u003c`, ningún dato puede cerrar un script de la página."""
    return json.dumps(datos, ensure_ascii=False, separators=(",", ":")).replace("<", "\\u003c")


def _compartido() -> Dict[str, str]:
    return {"/*__TOKENS__*/": _leer("tokens.css"), "/*__CLIENTE__*/": _leer("cliente_programa.js"), "/*__SESION__*/": _leer("sesion.js")}


def pagina_gantt(prog: Programa, cal: Calendario, titulo: str, ventana: Optional[Tuple[date, date]] = None) -> str:
    """La **simulación**: la pantalla de `prog`, con su cadena de relevos, su ruta crítica de la red y todo lo necesario
    para editar y reprogramar sin servidor —el programa va dentro de la página y nada se guarda—. `titulo` es el nombre
    de la pantalla («Gantt Zafiro Plus»)."""
    vista = vista_gantt(prog, cal, ventana=ventana, resultado=prog.calcular(cal), para_editar=True)
    return _armar(
        _leer("gantt.html"),
        {
            "__TITULO__": html.escape(titulo),
            "/*__MOTOR__*/": _leer("motor_gantt.js"),
            "__CONFIG__": "null",
            "__DATOS__": _json_seguro(vista),
            **_compartido(),
        },
    )


def pagina_gantt_en_vivo(config: Dict[str, Any]) -> str:
    """La pantalla que trabaja contra la API (`config`: modo, `login_url` y el `programa`). **No lleva ningún dato del
    programa, ni su nombre**: los pide a la API con el token de quien la abre (B-96, D-469)."""
    return _armar(
        _leer("gantt.html"),
        {"__TITULO__": "Gantt", "/*__MOTOR__*/": _leer("motor_gantt.js"), "__CONFIG__": _json_seguro(config), "__DATOS__": "null", **_compartido()},
    )


def pagina_programas(config: Dict[str, Any]) -> str:
    """La lista de programas y subir uno. Tampoco lleva datos: los pide a la API."""
    return _armar(_leer("programas.html"), {"__CONFIG__": _json_seguro(config), **_compartido()})
