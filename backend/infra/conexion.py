"""
Una conexión por hilo — D-482.

`api.servir` atiende cada petición en un hilo y los adaptadores (`PostgresPrograma`, `PostgresCatalogo`, `PostgresAccesos`) guardan **una**
conexión. Con una sola conexión compartida, dos peticiones que se traslapan abren sus `transaction()` en la misma sesión: la segunda se vuelve un
punto de guardado dentro de la primera y, al salir en otro orden, psycopg lanza `OutOfOrderTransactionNesting` —y lo que la primera había
escrito antes de fallar se queda escrito—. Una carga de OPUS tarda segundos, así que traslaparse con otra petición no es raro.

`ConexionPorHilo` se usa donde un adaptador espera una conexión: reparte a cada hilo la suya, abierta al primer uso. Cada petición queda en su
propia sesión, y el aislamiento y los candados los pone la base, como ya los pensaban las transacciones de los adaptadores. Las conexiones son
tantas como hilos tenga el servidor (40 por omisión en FastAPI) y se cierran con `cerrar()` o al terminar el proceso.
"""
from __future__ import annotations

import threading
from typing import Any, List


class ConexionPorHilo:
    def __init__(self, cadena: str) -> None:
        import psycopg

        self._psycopg = psycopg
        self._cadena = cadena
        self._local = threading.local()
        self._abiertas: List[Any] = []
        self._candado = threading.Lock()

    def _conexion(self) -> Any:
        c = getattr(self._local, "conexion", None)
        if c is None or c.closed:
            c = self._psycopg.connect(self._cadena, autocommit=True)
            self._local.conexion = c
            with self._candado:
                self._abiertas = [x for x in self._abiertas if not x.closed] + [c]
        return c

    def __getattr__(self, nombre: str) -> Any:
        # `execute`, `cursor`, `transaction`…: lo que el adaptador le pida a una conexión, se lo pide a la de este hilo
        if nombre.startswith("_"):
            raise AttributeError(nombre)
        return getattr(self._conexion(), nombre)

    @property
    def abiertas(self) -> int:
        with self._candado:
            return sum(1 for c in self._abiertas if not c.closed)

    def cerrar(self) -> None:
        with self._candado:
            for c in self._abiertas:
                if not c.closed:
                    c.close()
            self._abiertas = []
