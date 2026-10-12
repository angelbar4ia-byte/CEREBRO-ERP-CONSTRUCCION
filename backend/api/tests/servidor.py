"""Un servidor de verdad (uvicorn en un hilo) con el adaptador en memoria, para las pruebas que hablan por HTTP.

En modo `token` verifica tokens de verdad (HS256, con `SECRETO`) y tiene a los usuarios de siempre dados de alta."""
import socket
import threading
import time

import uvicorn

from api.app import crear_app
from api.autenticacion import VerificadorJWT, emitir_token, por_cabeceras, por_token
from core.accesos import MemoriaAccesos
from core.memoria_bandeja import MemoriaBandeja
from core.memoria_catalogo import MemoriaCatalogo
from core.memoria_programa import MemoriaPrograma
from core.servicio_programa import ServicioPrograma

SECRETO = "un-secreto-compartido-de-prueba-largo-de-32-bytes!"
LOGIN = "https://proveedor.example/entrar"
USUARIOS = (  # correo, nombre, roles
    ("luis@obra.mx", "Luis Pérez", ["control_de_obra"]),
    ("ana@obra.mx", "Ana Soto", ["residente"]),
    ("sinrol@obra.mx", "Sin Rol", []),
)


def _puerto_libre() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


class ServidorDePrueba:
    def __init__(self, modo: str = "cabeceras") -> None:
        self.repo = MemoriaPrograma()
        self.catalogo = MemoriaCatalogo()
        self.bandeja = MemoriaBandeja()
        self.accesos = MemoriaAccesos()
        for correo, nombre, roles in USUARIOS:
            self.accesos.agregar_usuario(nombre, correo, roles)
        autenticacion = por_token(VerificadorJWT(secreto=SECRETO), self.accesos, LOGIN) if modo == "token" else por_cabeceras()
        self.puerto = _puerto_libre()
        self.url = f"http://127.0.0.1:{self.puerto}"
        config = uvicorn.Config(crear_app(ServicioPrograma(self.repo, permisos=self.accesos.permisos), autenticacion, self.catalogo, self.bandeja), host="127.0.0.1", port=self.puerto, log_level="error")
        self._servidor = uvicorn.Server(config)
        self._hilo = threading.Thread(target=self._servidor.run, daemon=True)

    @staticmethod
    def token(correo: str, **kw) -> str:
        return emitir_token(SECRETO, correo, **kw)

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
