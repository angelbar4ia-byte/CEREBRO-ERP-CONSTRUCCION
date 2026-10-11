"""
Cargar los archivos de OPUS a la base, desde la terminal — D-473.

    # solo revisar: dice qué entra, qué versiona y qué se detiene, y no escribe nada
    python3 -m api.cargar_opus --postgres postgresql://… --usuario ana@obra.mx \
        --presupuesto CATALOGO_DE_PRESUPUESTO.csv --conceptos ANALISIS_DE_BASICOS_CONCEPTOS.csv

    # aplicar lo que entra (lo detenido queda dicho en la carga y no se aplica)
    python3 -m api.cargar_opus … --aplicar
    python3 -m api.cargar_opus … --aplicar --confirmar ACA-01010    (el PU de ese concepto se movió más de 5 % y alguien lo confirmó)

    # un presupuesto que ya existe y llega distinto se reconcilia (D-476): las cantidades y los renglones nuevos entran; una baja pide
    # confirmación con el id que el informe le da, y lo contratado no se toca
    python3 -m api.cargar_opus … --aplicar --confirmar-baja "CAS-00004#1/NIV-00001#1::EST-10010#1"
    python3 -m api.cargar_opus … --aplicar --todas-las-bajas

Quien carga es un usuario dado de alta (`api.usuarios`) y de uno de los roles que tienen `cargar_catalogo_opus` en `ROL_FUNCION`
—Control de obra y Costos por omisión—: queda en la carga con su correo y el rol con que la hizo. Sin `--aplicar` no se escribe nada.
El archivo de compuestos es opcional: sus 267 líneas ya vienen dentro del de conceptos.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Callable, Optional, Sequence, TextIO

from core.accesos import PermisoDenegado, RepositorioAccesos, normalizar_correo
from core.catalogo import CambioDePresupuesto, RepositorioCatalogo, ServicioCarga, informe_de_carga
from core.colgado import citas_de_bajas
from core.importacion_opus import CargaNoProcede
from core.servicio_programa import RepositorioPrograma


def citas_del_programa(programas: RepositorioPrograma, cambios: Sequence[CambioDePresupuesto]) -> str:
    """Qué programas citan lo que se va (D-476), dicho para quien confirma una baja (`core.colgado.citas_de_bajas`)."""
    citas = citas_de_bajas(programas, cambios)
    if not citas:
        return ""
    lineas = [f"  {c.baja}: lo cita el programa {c.programa_id} «{c.programa}» en {c.filas} fila(s); seguirían enlazadas a algo dado de baja" for c in citas]
    return "\n".join(["", "Programas que citan lo que se da de baja"] + lineas)


def cargar(
    catalogo: RepositorioCatalogo,
    accesos: RepositorioAccesos,
    *,
    correo: str,
    conceptos: Path,
    presupuesto: Optional[Path] = None,
    compuestos: Optional[Path] = None,
    tipo: str = "plantilla",
    confirmados: Sequence[str] = (),
    bajas: Sequence[str] = (),
    todas_las_bajas: bool = False,
    programas: Optional[RepositorioPrograma] = None,
    aplicar: bool = False,
    salida: TextIO = sys.stdout,
    errores: TextIO = sys.stderr,
) -> int:
    """0 si se revisó o se aplicó; 1 si el archivo no cuadra; 2 si quien carga no puede."""
    u = accesos.usuario_por_correo(normalizar_correo(correo))
    if u is None or not u.activo:
        print(f"No se pudo: {correo} no es un usuario dado de alta y activo (python3 -m api.usuarios).", file=errores)
        return 2
    servicio = ServicioCarga(catalogo, permisos=accesos.permisos)
    leer = lambda ruta: None if ruta is None else Path(ruta).read_text(encoding="utf-8")
    try:
        r = servicio.revisar(leer(conceptos), leer(presupuesto), leer(compuestos), rol=list(u.roles), usuario=u.correo, tipo=tipo,
                             confirmados=confirmados, bajas_confirmadas=bajas, todas_las_bajas=todas_las_bajas)
    except PermisoDenegado as e:
        print(f"No se pudo: {e}", file=errores)
        return 2
    except CargaNoProcede as e:
        print(f"No se pudo leer: {e}", file=errores)
        return 1
    print(informe_de_carga(r.diagnostico), file=salida)
    if programas is not None:
        citas = citas_del_programa(programas, r.diagnostico.cambios)
        if citas:
            print(citas, file=salida)
    if not r.diagnostico.aplicable:
        return 1
    if not aplicar:
        print("\nNo se escribió nada: con --aplicar se aplica lo que entra.", file=salida)
        return 0
    try:
        res = servicio.aplicar(leer(conceptos), leer(presupuesto), leer(compuestos), rol=list(u.roles), usuario=u.correo, tipo=tipo,
                               confirmados=confirmados, bajas_confirmadas=bajas, todas_las_bajas=todas_las_bajas)
    except CargaNoProcede as e:
        print(f"No se pudo: {e}", file=errores)
        return 1
    print("\n" + (f"Carga {res.carga_id} aplicada." if res.carga_id else "No había nada que aplicar."), file=salida)
    return 0


def main(argv: Optional[Sequence[str]] = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--postgres", required=True, help="cadena de conexión")
    ap.add_argument("--usuario", required=True, help="el correo de quien carga: un usuario dado de alta")
    ap.add_argument("--conceptos", required=True, type=Path, help="ANALISIS_DE_BASICOS_CONCEPTOS.csv")
    ap.add_argument("--presupuesto", type=Path, help="CATALOGO_DE_PRESUPUESTO.csv")
    ap.add_argument("--compuestos", type=Path, help="ANALISIS_DE_BASICOS_COMPUESTOS.csv (ya viene dentro del de conceptos)")
    ap.add_argument("--tipo", default="plantilla", choices=["plantilla", "obra", "escenario"], help="qué son los presupuestos que se crean")
    ap.add_argument("--confirmar", action="append", default=[], metavar="CLAVE", help="confirma el cambio de más de 5 %% en el PU de ese concepto")
    ap.add_argument("--confirmar-baja", action="append", default=[], metavar="ID", dest="bajas",
                    help="confirma la baja de un renglón o bloque de un presupuesto que ya existe (el informe da el id)")
    ap.add_argument("--todas-las-bajas", action="store_true", help="confirma todas las bajas de esta carga")
    ap.add_argument("--aplicar", action="store_true", help="aplica lo que entra; sin esto, solo se revisa")
    a = ap.parse_args(argv)
    import psycopg

    from infra.postgres_accesos import PostgresAccesos
    from infra.postgres_catalogo import PostgresCatalogo
    from infra.postgres_programa import PostgresPrograma, aplicar_migraciones

    conn = psycopg.connect(a.postgres, autocommit=True)
    aplicar_migraciones(conn)
    return cargar(PostgresCatalogo(conn), PostgresAccesos(conn), correo=a.usuario, conceptos=a.conceptos, presupuesto=a.presupuesto,
                  compuestos=a.compuestos, tipo=a.tipo, confirmados=a.confirmar, bajas=a.bajas, todas_las_bajas=a.todas_las_bajas,
                  programas=PostgresPrograma(conn), aplicar=a.aplicar)


if __name__ == "__main__":
    sys.exit(main())
