"""
Un token como los que daría el proveedor de identidad — **solo para trabajar y probar** (B-96, D-469).

    python3 -m api.emitir_token --secreto "$PROGRAMA_JWT_SECRETO" --correo luis@obra.mx
    # y para abrir la pantalla con esa sesión:   http://127.0.0.1:8000/#access_token=<el token>

En producción los tokens los emite el proveedor; la API solo los verifica.
"""
from __future__ import annotations

import argparse
import os

from .autenticacion import emitir_token


def main(argv=None) -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--secreto", default=os.environ.get("PROGRAMA_JWT_SECRETO"), help="el mismo que usa `servir`")
    ap.add_argument("--correo", required=True)
    ap.add_argument("--horas", type=float, default=8)
    ap.add_argument("--audiencia")
    ap.add_argument("--emisor")
    ap.add_argument("--reclamo-correo", default="email")
    a = ap.parse_args(argv)
    if not a.secreto:
        raise SystemExit("Falta el secreto: --secreto o PROGRAMA_JWT_SECRETO.")
    print(emitir_token(a.secreto, a.correo, horas=a.horas, audiencia=a.audiencia, emisor=a.emisor, reclamo_correo=a.reclamo_correo))


if __name__ == "__main__":
    main()
