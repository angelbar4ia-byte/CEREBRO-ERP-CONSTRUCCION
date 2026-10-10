"""
Las pantallas del programa como páginas sueltas — `frontend/gantt/` y `1-mundo/PROGRAMA-CPM.md` §4.8 y §8.

Cada pantalla es un solo HTML que se abre solo: la plantilla, los colores compartidos (`tokens.css`), el cliente de la
API (`cliente_programa.js`, generado del spec, D-55) y, en el Gantt, el motor que reprograma en el navegador
(`motor_gantt.js`, que una prueba contrasta con `reprogramar`) y los datos de un programa
(`vista_gantt(..., para_editar=True)`). Con `api` el Gantt habla con el servidor para guardar lo que se edita.

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


def pagina_gantt(
    prog: Programa,
    cal: Calendario,
    titulo: str,
    ventana: Optional[Tuple[date, date]] = None,
    api: Optional[Dict[str, Any]] = None,
) -> str:
    """La pantalla de `prog`, con su cadena de relevos, su ruta crítica de la red y todo lo necesario
    para editar y reprogramar sin el servidor. `titulo` es el nombre de la pantalla («Gantt Zafiro Plus»).

    Con `api` —`{"programa": id, "version": n, "guardadas": [...]}`— la pantalla trabaja contra la API: `prog`
    es el programa **base**, `guardadas` lo ya aplicado, y las ediciones se proponen y se guardan en el
    servidor. Sin `api` es la simulación de siempre: nada se guarda."""
    vista = vista_gantt(prog, cal, ventana=ventana, resultado=prog.calcular(cal), para_editar=True)
    if api is not None:
        vista["api"] = api
    # un `<` solo puede estar dentro de un texto del JSON: escapado, ningún dato puede cerrar el script
    datos = json.dumps(vista, ensure_ascii=False, separators=(",", ":")).replace("<", "\\u003c")
    return _armar(
        _leer("gantt.html"),
        {
            "__TITULO__": html.escape(titulo),
            "/*__TOKENS__*/": _leer("tokens.css"),
            "/*__MOTOR__*/": _leer("motor_gantt.js"),
            "/*__CLIENTE__*/": _leer("cliente_programa.js"),
            "__DATOS__": datos,
        },
    )


def pagina_programas() -> str:
    """La lista de programas y subir uno. No lleva datos: los pide a la API."""
    return _armar(
        _leer("programas.html"),
        {"/*__TOKENS__*/": _leer("tokens.css"), "/*__CLIENTE__*/": _leer("cliente_programa.js")},
    )
