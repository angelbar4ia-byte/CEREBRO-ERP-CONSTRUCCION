"""
La pantalla del Gantt como una sola página — `frontend/gantt/` y `1-mundo/PROGRAMA-CPM.md` §8.

Junta cuatro cosas: la plantilla de la pantalla (`gantt.html`), el motor que reprograma en el navegador
(`motor_gantt.js`, que una prueba contrasta con `reprogramar`), el cliente de la API (`cliente_programa.js`,
generado del spec, D-55) y los datos de un programa (`vista_gantt(..., para_editar=True)`). El resultado es un
HTML que se abre solo, sin servidor; con `api` habla con él para guardar lo que se edita.
"""
from __future__ import annotations

import json
from datetime import date
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

from .motor_cpm import Calendario
from .programa import Programa, vista_gantt

FRONTEND = Path(__file__).resolve().parents[2] / "frontend" / "gantt"


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
    datos = json.dumps(vista, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    html = (FRONTEND / "gantt.html").read_text(encoding="utf-8")
    motor = (FRONTEND / "motor_gantt.js").read_text(encoding="utf-8")
    cliente = (FRONTEND / "cliente_programa.js").read_text(encoding="utf-8")
    for marca in ("/*__MOTOR__*/", "/*__CLIENTE__*/", "__DATOS__", "__TITULO__"):
        if marca not in html:
            raise ValueError(f"la plantilla ya no tiene {marca}")
    # el título va primero y los datos al final: nada de lo que traen puede parecerse a una marca
    return html.replace("__TITULO__", titulo).replace("/*__MOTOR__*/", motor).replace("/*__CLIENTE__*/", cliente).replace("__DATOS__", datos)
