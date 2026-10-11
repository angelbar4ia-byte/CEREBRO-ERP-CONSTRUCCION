"""Cómo contesta la API cuando algo no procede: un código que la pantalla lee y un mensaje que lee la persona."""
from __future__ import annotations

from typing import Any

from fastapi import HTTPException


def _error(status: int, codigo: str, mensaje: str, **extra: Any) -> HTTPException:
    """`detail = {codigo, mensaje, …}`: el cliente generado lo convierte en un `ErrorApi` con esos campos."""
    return HTTPException(status_code=status, detail={"codigo": codigo, "mensaje": mensaje, **extra})
