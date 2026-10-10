"""Un servidor de verdad (uvicorn en un hilo) con el adaptador en memoria, para las pruebas que hablan por HTTP."""
import socket
import threading
import time

import uvicorn

from api.app import crear_app
from core.memoria_programa import MemoriaPrograma
from core.servicio_programa import ServicioPrograma


def _puerto_libre() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


class ServidorDePrueba:
    def __init__(self) -> None:
        self.repo = MemoriaPrograma()
        self.puerto = _puerto_libre()
        self.url = f"http://127.0.0.1:{self.puerto}"
        config = uvicorn.Config(crear_app(ServicioPrograma(self.repo)), host="127.0.0.1", port=self.puerto, log_level="error")
        self._servidor = uvicorn.Server(config)
        self._hilo = threading.Thread(target=self._servidor.run, daemon=True)

    def arrancar(self) -> "ServidorDePrueba":
        self._hilo.start()
        for _ in range(100):
            if self._servidor.started:
                return self
            time.sleep(0.05)
        raise RuntimeError("el servidor no arrancó")

    def apagar(self) -> None:
        self._servidor.should_exit = True
        self._hilo.join(timeout=10)
