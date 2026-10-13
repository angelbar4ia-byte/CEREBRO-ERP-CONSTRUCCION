#!/usr/bin/env python3
"""
preparar-para-github.py — deja la carpeta de una app lista para subirse a GitHub sin llevarse claves ni datos reales.

No sube nada y no toca la carpeta original: la lee, la revisa y arma una copia limpia. Quien empuja es la persona.

Qué hace:
  1. Recorre la carpeta sin entrar a lo que nunca va a git (node_modules, venv, __pycache__…).
  2. Aparta lo que no debe subirse: archivos de claves (.env, .pem…), bases de datos y hojas con datos reales, carpetas de
     subidas y respaldos, archivos de más de 20 MB.
  3. Busca claves dentro del texto: llaves de servicio de Supabase, contraseñas en URLs de base de datos, tokens de GitHub,
     de AWS y de otros servicios, y asignaciones sospechosas. Nunca muestra el valor completo: solo sus primeras letras.
  4. Arma `<salida>/<nombre>/` con lo que sí puede subirse, más un `.gitignore`, un `.env.example` con los NOMBRES de las
     variables que el código lee, y una `FICHA.md` con las siete preguntas del cerebro (`1-mundo/LENGUAJE.md`).
  5. Con --a copia esa carpeta limpia a `<clon de Multi-erp>/apps/<nombre>/`. El `git add`, el commit y el push los haces tú.

Uso:
  python3 preparar-para-github.py CARPETA --nombre extraordinarios                   # revisa y arma la copia limpia
  python3 preparar-para-github.py CARPETA --nombre extraordinarios --a ../Multi-erp  # y la deja dentro del clon
  python3 preparar-para-github.py --autoprueba                                       # se prueba a sí mismo con secretos falsos

Un archivo con una clave de verdad (nivel CRÍTICO) NO se copia: se mueve la clave a una variable de entorno y se vuelve a
correr. Las hojas de datos y las bases se piden aparte con --incluir-datos, por si alguna es semilla del sistema.
"""
import argparse
import base64
import json
import os
import re
import shutil
import sys
import tempfile
from pathlib import Path

CARPETAS_QUE_NUNCA_VAN = {"node_modules", ".venv", "venv", "env", "__pycache__", ".git", "dist", "build", ".next", ".pytest_cache",
                          ".idea", ".vscode", ".mypy_cache", ".expo", ".gradle", "coverage"}
CARPETAS_DE_DATOS = {"uploads", "exports", "backups", "backup", "logs", "instance", "tmp", "temp"}
EXTENSIONES_DE_DATOS = {".db", ".sqlite", ".sqlite3", ".mdb", ".accdb", ".bak", ".dump", ".xlsx", ".xls", ".xlsm", ".csv", ".tsv"}
EXTENSIONES_DE_CLAVES = {".pem", ".key", ".pfx", ".p12", ".jks"}
EXTENSIONES_DE_TEXTO = {".py", ".js", ".jsx", ".ts", ".tsx", ".json", ".yaml", ".yml", ".toml", ".ini", ".cfg", ".env", ".html", ".htm",
                        ".sh", ".ps1", ".bat", ".cmd", ".sql", ".md", ".txt", ".conf", ".properties", ".php", ".rb", ".go", ".java", ".cs"}
LIMITE_GRANDE = 20 * 1024 * 1024
LIMITE_DE_LECTURA = 3 * 1024 * 1024
PLACEHOLDERS = ("password", "contraseña", "contrasena", "xxx", "****", "tu_", "tu-", "your", "changeme", "cambia", "ejemplo", "example",
                "<", ">", "${", "{{", "%s", "$", "secret_aqui", "aqui", "dummy", "ficticio", "placeholder", "test", "demo", "...")

CRITICO, AVISO, INFO = "CRÍTICO", "AVISO", "INFO"


def es_placeholder(valor):
    v = valor.lower()
    return any(p in v for p in PLACEHOLDERS)


def ocultar(valor):
    return valor[:4] + "…(" + str(len(valor)) + " caracteres)"


def decodificar_jwt(token):
    try:
        carga = token.split(".")[1]
        carga += "=" * (-len(carga) % 4)
        return json.loads(base64.urlsafe_b64decode(carga))
    except (ValueError, IndexError):
        return {}


def hallazgos_de_texto(texto):
    """[(línea, nivel, qué, vista)] de las claves que parecen de verdad. La vista nunca trae el valor completo."""
    salida = []
    for n, linea in enumerate(texto.split("\n"), 1):
        if len(linea) > 4000:  # una línea enorme es un archivo empacado, no código escrito a mano
            linea = linea[:4000]
        for m in re.finditer(r"eyJ[A-Za-z0-9_-]{10,}\.eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}", linea):
            rol = decodificar_jwt(m.group(0)).get("role")
            if rol == "service_role":
                salida.append((n, CRITICO, "llave de servicio de Supabase (salta toda la seguridad por fila)", ocultar(m.group(0))))
            elif rol == "anon":
                salida.append((n, INFO, "llave anon de Supabase (pública por diseño; la protege RLS)", ocultar(m.group(0))))
            else:
                salida.append((n, AVISO, "token firmado (JWT) con rol " + str(rol), ocultar(m.group(0))))
        for m in re.finditer(r"[a-zA-Z][a-zA-Z0-9+.-]*://[^\s:/@'\"]+:([^\s@'\"/]{4,})@[^\s'\"]+", linea):
            if not es_placeholder(m.group(1)):
                if re.search(r"@(localhost|127\.0\.0\.1|0\.0\.0\.0|host\.docker\.internal)\b", m.group(0)):
                    salida.append((n, AVISO, "dirección local con contraseña de desarrollo (revisa que no sea la de producción)", ocultar(m.group(1))))
                else:
                    salida.append((n, CRITICO, "dirección de servicio con contraseña adentro", ocultar(m.group(1))))
        if re.search(r"-----BEGIN (RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----", linea):
            salida.append((n, CRITICO, "llave privada", "-----BEGIN…"))
        for m in re.finditer(r"\b(AKIA[0-9A-Z]{16}|ghp_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{30,}|xox[abprs]-[A-Za-z0-9-]{10,}|"
                             r"sk-ant-[A-Za-z0-9_-]{20,}|sk-[A-Za-z0-9]{32,}|AIza[0-9A-Za-z_-]{35})\b", linea):
            if "EXAMPLE" in m.group(0).upper():
                salida.append((n, INFO, "llave de ejemplo de la documentación del servicio", ocultar(m.group(0))))
            else:
                salida.append((n, CRITICO, "token de un servicio (AWS, GitHub, Slack, Anthropic, OpenAI o Google)", ocultar(m.group(0))))
        if re.search(r"os\.environ|getenv|process\.env|import\.meta\.env", linea):
            continue
        for m in re.finditer(r"(?i)\b([A-Za-z0-9_]*(?:password|passwd|pwd|secret|api[_-]?key|token|contrase[nñ]a)[A-Za-z0-9_]*)\s*[:=]\s*['\"]([^'\"\s]{6,})['\"]", linea):
            if not es_placeholder(m.group(2)):
                salida.append((n, AVISO, "asignación de «" + m.group(1) + "» con un valor escrito en el código", ocultar(m.group(2))))
    return salida


def nombres_de_variables(texto):
    nombres = set()
    for patron in (r"os\.environ(?:\.get)?\s*[\(\[]\s*['\"]([A-Z][A-Z0-9_]+)['\"]", r"os\.getenv\(\s*['\"]([A-Z][A-Z0-9_]+)['\"]",
                   r"process\.env\.([A-Z][A-Z0-9_]+)", r"import\.meta\.env\.([A-Z][A-Z0-9_]+)"):
        nombres.update(re.findall(patron, texto))
    return nombres


def es_archivo_de_claves(ruta):
    nombre = ruta.name.lower()
    if nombre.startswith(".env"):
        return not nombre.endswith((".example", ".sample", ".template", ".test"))
    if ruta.suffix.lower() in EXTENSIONES_DE_CLAVES:
        return True
    return bool(re.match(r"(id_rsa|id_ed25519|\.npmrc|\.pypirc|\.netrc)", nombre) or re.search(r"(credential|service[-_]?account)", nombre) and nombre.endswith(".json"))


def archivos_de(carpeta):
    """Los archivos de la carpeta, sin entrar a node_modules, venv, .git ni las demás carpetas que nunca van (entrar es lo que tardaba)."""
    for raiz, subcarpetas, archivos in os.walk(carpeta):
        subcarpetas[:] = sorted(d for d in subcarpetas if d not in CARPETAS_QUE_NUNCA_VAN)
        for nombre in sorted(archivos):
            yield Path(raiz) / nombre


def revisar(carpeta):
    """Recorre la carpeta y devuelve un informe: qué entra, qué se aparta y por qué, y qué claves aparecen."""
    entra, aparta, hallazgos, variables, total = [], [], {}, set(), 0
    for ruta in archivos_de(carpeta):
        rel = ruta.relative_to(carpeta)
        partes = rel.parts
        if not ruta.is_file():
            continue
        total += 1
        if total % 2000 == 0:
            print(f"  … {total} archivos revisados", flush=True)
        if es_archivo_de_claves(ruta):
            aparta.append((rel, "archivo de claves"))
            continue
        if any(p.lower() in CARPETAS_DE_DATOS for p in partes[:-1]):
            aparta.append((rel, "carpeta de subidas, respaldos o salidas"))
            continue
        if ruta.suffix.lower() in EXTENSIONES_DE_DATOS:
            aparta.append((rel, "datos (base o hoja)"))
            continue
        try:
            tamano = ruta.stat().st_size
        except OSError:
            aparta.append((rel, "no se pudo leer (¿la tiene abierta otro programa?)"))
            continue
        if tamano > LIMITE_GRANDE:
            aparta.append((rel, "pesa más de 20 MB"))
            continue
        if ruta.suffix.lower() in EXTENSIONES_DE_TEXTO or ruta.name.lower().startswith(".env") or ruta.suffix == "":
            try:
                if tamano <= LIMITE_DE_LECTURA:
                    texto = ruta.read_text(encoding="utf-8", errors="ignore")
                    if "\x00" not in texto[:8000]:
                        variables |= nombres_de_variables(texto)
                        encontrados = hallazgos_de_texto(texto)
                        if encontrados:
                            hallazgos[rel] = encontrados
            except OSError:
                pass
        entra.append(rel)
    return {"entra": entra, "aparta": aparta, "hallazgos": hallazgos, "variables": variables, "total": total}


def con_critico(informe):
    return {r for r, hs in informe["hallazgos"].items() if any(h[1] == CRITICO for h in hs)}


def plantilla_de_ficha(nombre, variables):
    return f"""# {nombre} — ficha

Las siete preguntas que el cerebro (`LENGUAJE.md`, «Antes de la ficha») necesita de cada sistema. Llénalas con tus palabras.

| # | Pregunta | Respuesta |
|---|---|---|
| 1 | ¿Qué es y qué guarda? (nombre, versión, qué datos maneja) | |
| 2 | ¿Quién lo usa y quién manda en él? | |
| 3 | ¿Cómo se llega a sus datos? (exportación a mano, reporte, API, su base de datos, nada) | |
| 4 | ¿Dónde vive? (nube, servidor propio, una sola computadora) | |
| 5 | ¿Hasta dónde puede actuar el cerebro? (leer · proponer · devolver un archivo · escribir directo) | |
| 6 | Dos o tres archivos o respuestas reales de ejemplo | |
| 7 | ¿Qué no se debe tocar nunca? | |

Variables de entorno que el código lee: {", ".join(sorted(variables)) if variables else "ninguna detectada"}.
"""


def bloque_gitignore():
    return """# --- agregado por preparar-para-github.py ---
# Claves
.env
.env.*
!.env.example
*.pem
*.key
*.pfx
# Datos reales: se quedan en la máquina, no en git
*.db
*.sqlite
*.sqlite3
*.bak
uploads/
exports/
backups/
logs/
instance/
# Entornos y empaques
node_modules/
.venv/
venv/
__pycache__/
*.pyc
dist/
build/
.DS_Store
"""


def armar_copia(carpeta, informe, salida, nombre, incluir_datos):
    destino = salida / nombre
    if destino.exists():
        raise SystemExit(f"{destino} ya existe: bórrala o elige otra --salida.")
    omitidos = con_critico(informe)
    copiados = 0
    lista = list(informe["entra"]) + ([r for r, motivo in informe["aparta"] if motivo == "datos (base o hoja)"] if incluir_datos else [])
    for rel in lista:
        if rel in omitidos:
            continue
        origen, fin = carpeta / rel, destino / rel
        fin.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(origen, fin)
        copiados += 1
    previo = (destino / ".gitignore").read_text(encoding="utf-8") if (destino / ".gitignore").exists() else ""
    (destino / ".gitignore").write_text(previo.rstrip("\n") + ("\n\n" if previo else "") + bloque_gitignore(), encoding="utf-8")
    (destino / ".env.example").write_text("".join(f"{v}=\n" for v in sorted(informe["variables"])), encoding="utf-8")
    (destino / "FICHA.md").write_text(plantilla_de_ficha(nombre, informe["variables"]), encoding="utf-8")
    if not (destino / "README.md").exists():
        (destino / "README.md").write_text(f"# {nombre}\n\nVer `FICHA.md`.\n", encoding="utf-8")
    return destino, copiados


def imprimir(informe, carpeta):
    print(f"\nRevisé {informe['total']} archivos de {carpeta}\n")
    print(f"  Entran a git:  {len(informe['entra'])}")
    print(f"  Se apartan:    {len(informe['aparta'])}")
    por_motivo = {}
    for rel, motivo in informe["aparta"]:
        por_motivo.setdefault(motivo, []).append(rel)
    for motivo, lista in sorted(por_motivo.items(), key=lambda kv: -len(kv[1])):
        print(f"     – {len(lista):4}  {motivo}: " + ", ".join(r.as_posix() for r in lista[:3]) + (" …" if len(lista) > 3 else ""))
    criticos = con_critico(informe)
    print(f"\n  Claves encontradas en {len(informe['hallazgos'])} archivos ({len(criticos)} con nivel CRÍTICO, que NO se copian):")
    for rel, hs in informe["hallazgos"].items():
        for n, nivel, que, vista in hs:
            print(f"     [{nivel}] {rel.as_posix()}:{n}  {que}  → {vista}")
    if not informe["hallazgos"]:
        print("     ninguna")
    print(f"\n  Variables de entorno que el código lee: {', '.join(sorted(informe['variables'])) or 'ninguna'}")


def autoprueba():
    """Crea una app falsa con claves sembradas y comprueba que se detectan, se apartan y no se copian."""
    def jwt(rol):
        cab = base64.urlsafe_b64encode(b'{"alg":"HS256","typ":"JWT"}').decode().rstrip("=")
        carga = base64.urlsafe_b64encode(json.dumps({"iss": "supabase", "role": rol, "ref": "abcdefgh"}).encode()).decode().rstrip("=")
        return f"{cab}.{carga}.firmaFalsaFirmaFalsaFirmaFalsa"
    with tempfile.TemporaryDirectory() as tmp:
        raiz = Path(tmp)
        app = raiz / "app"
        (app / "node_modules" / "x").mkdir(parents=True)
        (app / "node_modules" / "x" / "i.js").write_text("eyJ aaaaaaaaaaaaaaa", encoding="utf-8")
        (app / "uploads").mkdir()
        (app / "uploads" / "estimacion.xlsx").write_bytes(b"PK\x03\x04datos")
        (app / "uploads" / "recibo.png").write_bytes(b"\x89PNG")  # no es hoja de datos: solo la carpeta lo delata
        (app / "app.py").write_text("import os\nSECRET_KEY = 'una-clave-larga-12345'\nTOKEN_X = os.environ.get('TOKEN_X')\nDB = 'postgresql://admin:Contra123@db.ejemplo.com:5432/obra'\n", encoding="utf-8")
        (app / "config.js").write_text(f"export const servicio = '{jwt('service_role')}';\nexport const anon = '{jwt('anon')}';\nconst u = process.env.VITE_URL;\n", encoding="utf-8")
        (app / "dev.py").write_text("URL = 'postgresql://postgres:postgres@localhost:5432/x'\nK = 'AKIAIOSFODNN7EXAMPLE'\n", encoding="utf-8")
        (app / "limpio.py").write_text("print('hola')\nclave = os.getenv('CLAVE_API')\npassword = 'password'\n", encoding="utf-8")
        (app / ".env").write_text("SUPABASE_SERVICE_KEY=algo\n", encoding="utf-8")
        (app / ".env.example").write_text("SUPABASE_URL=\n", encoding="utf-8")
        (app / "datos.db").write_bytes(b"SQLite format 3\x00" + b"\x00" * 100)
        (app / "grande.bin").write_bytes(b"\x00" * (LIMITE_GRANDE + 1))
        informe = revisar(app)
        apartados = {r.as_posix() for r, _ in informe["aparta"]}
        esperado_apartado = {".env", "datos.db", "uploads/estimacion.xlsx", "uploads/recibo.png", "grande.bin"}
        errores = []
        if apartados != esperado_apartado:
            errores.append(f"apartados {sorted(apartados)} ≠ {sorted(esperado_apartado)}")
        crit = {r.as_posix() for r in con_critico(informe)}
        if crit != {"app.py", "config.js"}:
            errores.append(f"críticos {sorted(crit)} ≠ ['app.py', 'config.js']")
        niveles = {(r.as_posix(), h[1]) for r, hs in informe["hallazgos"].items() for h in hs}
        for esperado in (("config.js", INFO), ("app.py", AVISO), ("app.py", CRITICO), ("config.js", CRITICO)):
            if esperado not in niveles:
                errores.append(f"no detectó {esperado}")
        if "dev.py" in crit or "dev.py" not in {r.as_posix() for r in informe["hallazgos"]}:
            errores.append("dev.py (dirección local y llave de ejemplo) debía dar solo AVISO o INFO")
        if "limpio.py" in informe["hallazgos"]:
            errores.append("marcó un archivo limpio (password='password' es un marcador)")
        if informe["variables"] != {"TOKEN_X", "VITE_URL", "CLAVE_API"}:
            errores.append(f"variables {sorted(informe['variables'])}")
        destino, copiados = armar_copia(app, informe, raiz / "salida", "prueba", False)
        dentro = {p.relative_to(destino).as_posix() for p in destino.rglob("*") if p.is_file()}
        for prohibido in ("app.py", "config.js", ".env", "datos.db", "uploads/estimacion.xlsx", "uploads/recibo.png", "grande.bin", "node_modules/x/i.js"):
            if prohibido in dentro:
                errores.append(f"copió {prohibido}")
        for requerido in ("limpio.py", "dev.py", ".gitignore", ".env.example", "FICHA.md", "README.md"):
            if requerido not in dentro:
                errores.append(f"faltó {requerido}")
        resumen = "\n".join("falló: " + e for e in errores)
        print("autoprueba: " + ("OK — detecta, aparta y no copia lo sembrado" if not errores else "FALLÓ\n" + resumen))
        return 0 if not errores else 1


def main():
    ap = argparse.ArgumentParser(description="Deja la carpeta de una app lista para GitHub sin claves ni datos reales.")
    ap.add_argument("carpeta", nargs="?", type=Path, help="la carpeta de la app")
    ap.add_argument("--nombre", help="cómo se llamará la carpeta dentro del repo (extraordinarios, auditoria…)")
    ap.add_argument("--salida", type=Path, default=Path("para-github"), help="dónde armar la copia limpia (por omisión ./para-github)")
    ap.add_argument("--a", type=Path, help="el clon de Multi-erp: la copia limpia se deja en <clon>/apps/<nombre>")
    ap.add_argument("--incluir-datos", action="store_true", help="incluye bases y hojas (solo si son semillas del sistema y no datos reales)")
    ap.add_argument("--autoprueba", action="store_true", help="se prueba a sí mismo con claves falsas y sale")
    a = ap.parse_args()
    if a.autoprueba:
        return autoprueba()
    if not a.carpeta or not a.nombre:
        ap.error("hace falta la CARPETA y --nombre")
    if not a.carpeta.is_dir():
        raise SystemExit(f"{a.carpeta} no es una carpeta")
    print(f"Revisando {a.carpeta} … (si la carpeta es grande puede tardar; irá avisando)", flush=True)
    informe = revisar(a.carpeta)
    imprimir(informe, a.carpeta)
    destino, copiados = armar_copia(a.carpeta, informe, a.salida, a.nombre, a.incluir_datos)
    print(f"\nCopia limpia: {destino}  ({copiados} archivos + .gitignore, .env.example, FICHA.md)")
    criticos = con_critico(informe)
    if criticos:
        print("\nOJO: hay archivos con claves que NO se copiaron. Mueve cada clave a una variable de entorno (.env) y vuelve a correr.")
    if a.a:
        fin = a.a / "apps" / a.nombre
        if fin.exists():
            raise SystemExit(f"{fin} ya existe: no se pisa.")
        fin.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(destino, fin)
        print(f"\nLista dentro del clon: {fin}\nAhora, desde {a.a}:\n  git add apps/{a.nombre}\n  git commit -m \"Agrega {a.nombre}\"\n  git push")
    else:
        print(f"\nSiguiente: clona Multi-erp, copia {destino} a apps/{a.nombre}/ dentro del clon, y haz git add, commit y push.")
    return 2 if criticos else 0


if __name__ == "__main__":
    sys.exit(main())
