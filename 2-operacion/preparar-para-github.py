#!/usr/bin/env python3
"""
preparar-para-github.py — deja la carpeta de una app lista para subirse a GitHub sin llevarse claves ni datos reales.

No sube nada y no toca la carpeta original: la lee, la revisa y arma una copia limpia. Quien empuja es la persona.

Qué hace:
  1. Recorre la carpeta sin entrar a lo que nunca va a git (node_modules, venv, site-packages, __pycache__…).
  2. Aparta lo que no debe subirse: archivos de claves (.env, .pem…), bases de datos y hojas con datos reales, el directorio de
     datos de PostgreSQL, MySQL o MongoDB si la carpeta lo trae adentro, carpetas de subidas y respaldos, archivos de más de
     20 MB y las carpetas que tú pidas con --excluir (por ejemplo, un PostgreSQL instalado dentro de la app).
  3. Busca claves dentro del texto: llaves de servicio de Supabase, contraseñas en URLs de base de datos, tokens de GitHub,
     de AWS y de otros servicios, y asignaciones sospechosas. Nunca muestra el valor completo: solo sus primeras letras.
  4. Arma `<salida>/<nombre>/` con lo que sí puede subirse, más un `.gitignore`, un `.env.example` con los NOMBRES de las
     variables que el código lee, y una `FICHA.md` con las siete preguntas del cerebro (`1-mundo/LENGUAJE.md`).
  5. Con --a copia esa carpeta limpia a `<clon de Multi-erp>/apps/<nombre>/`. El `git add`, el commit y el push los haces tú.

Uso:
  python3 preparar-para-github.py CARPETA --nombre extraordinarios                   # revisa y arma la copia limpia
  python3 preparar-para-github.py CARPETA --nombre extraordinarios --a ../Multi-erp  # y la deja dentro del clon
  python3 preparar-para-github.py CARPETA --nombre auditoria --excluir postgresql    # sin una carpeta ajena que viene dentro
  python3 preparar-para-github.py CARPETA --nombre auditoria --quitar-contrasenas   # la COPIA sale sin las contraseñas escritas en el código
  python3 preparar-para-github.py --autoprueba                                       # se prueba a sí mismo con secretos falsos

Además de lo que imprime, deja el informe completo en `<salida>/<nombre>-informe.txt` (con los valores siempre tapados).

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
from collections import Counter
from pathlib import Path

CARPETAS_QUE_NUNCA_VAN = {"node_modules", ".venv", "venv", "env", "__pycache__", ".git", "dist", "build", ".next", ".pytest_cache",
                          ".idea", ".vscode", ".mypy_cache", ".expo", ".gradle", "coverage", "site-packages", "dist-packages"}
CARPETAS_DE_DATOS = {"uploads", "exports", "backups", "backup", "logs", "instance", "tmp", "temp"}
EXTENSIONES_DE_DATOS = {".db", ".sqlite", ".sqlite3", ".mdb", ".accdb", ".bak", ".backup", ".dump", ".xlsx", ".xls", ".xlsm", ".csv", ".tsv"}
EXTENSIONES_DE_CLAVES = {".pem", ".key", ".pfx", ".p12", ".jks"}
EXTENSIONES_DE_TEXTO = {".py", ".js", ".jsx", ".ts", ".tsx", ".json", ".yaml", ".yml", ".toml", ".ini", ".cfg", ".env", ".html", ".htm",
                        ".sh", ".ps1", ".bat", ".cmd", ".sql", ".md", ".txt", ".conf", ".properties", ".php", ".rb", ".go", ".java", ".cs"}
LIMITE_GRANDE = 20 * 1024 * 1024
LIMITE_DE_LECTURA = 3 * 1024 * 1024
PLACEHOLDERS = ("password", "contraseña", "contrasena", "xxx", "****", "tu_", "tu-", "your", "changeme", "cambia", "ejemplo", "example",
                "<", ">", "${", "{{", "%s", "$", "secret_aqui", "aqui", "dummy", "ficticio", "placeholder", "test", "demo", "...")

NOMBRES_QUE_NO_SON_CLAVES = re.compile(r"(?i)(type|placement|url|uri|endpoint|field|file|path|name|method|hint|source|header|expires?|algorithm|prefix|scope|style)$")
VALORES_QUE_NO_SON_CLAVES = re.compile(r"^(https?://|urn:|#[0-9a-fA-F]{3,8}$)")

CRITICO, AVISO, INFO = "CRÍTICO", "AVISO", "INFO"
MARCA_DE_CLAVE = "CAMBIA_ESTA_CLAVE"


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
    """[(línea, nivel, qué, vista, quitable)] de las claves que parecen de verdad. La vista nunca trae el valor completo;
    `quitable` es (tipo, valor) para las contraseñas escritas en el código que --quitar-contrasenas puede sacar de la copia, o None."""
    salida = []
    for n, linea in enumerate(texto.split("\n"), 1):
        if len(linea) > 4000:  # una línea enorme es un archivo empacado, no código escrito a mano
            linea = linea[:4000]
        for m in re.finditer(r"eyJ[A-Za-z0-9_-]{10,}\.eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}", linea):
            rol = decodificar_jwt(m.group(0)).get("role")
            if rol == "service_role":
                salida.append((n, CRITICO, "llave de servicio de Supabase (salta toda la seguridad por fila)", ocultar(m.group(0)), None))
            elif rol == "anon":
                salida.append((n, INFO, "llave anon de Supabase (pública por diseño; la protege RLS)", ocultar(m.group(0)), None))
            else:
                salida.append((n, AVISO, "token firmado (JWT) con rol " + str(rol), ocultar(m.group(0)), None))
        for m in re.finditer(r"[a-zA-Z][a-zA-Z0-9+.-]*://[^\s:/@'\"]+:([^\s@'\"/]{4,})@[^\s'\"]+", linea):
            if not es_placeholder(m.group(1)):
                if re.search(r"@(localhost|127\.0\.0\.1|0\.0\.0\.0|host\.docker\.internal)\b", m.group(0)):
                    salida.append((n, AVISO, "dirección local con contraseña de desarrollo (revisa que no sea la de producción)", ocultar(m.group(1)), ("url", m.group(1))))
                else:
                    salida.append((n, CRITICO, "dirección de servicio con contraseña adentro", ocultar(m.group(1)), None))
        if re.search(r"-----BEGIN (RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----", linea):
            salida.append((n, CRITICO, "llave privada", "-----BEGIN…", None))
        for m in re.finditer(r"\b(AKIA[0-9A-Z]{16}|ghp_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{30,}|xox[abprs]-[A-Za-z0-9-]{10,}|"
                             r"sk-ant-[A-Za-z0-9_-]{20,}|sk-[A-Za-z0-9]{32,}|AIza[0-9A-Za-z_-]{35})\b", linea):
            if "EXAMPLE" in m.group(0).upper():
                salida.append((n, INFO, "llave de ejemplo de la documentación del servicio", ocultar(m.group(0)), None))
            else:
                salida.append((n, CRITICO, "token de un servicio (AWS, GitHub, Slack, Anthropic, OpenAI o Google)", ocultar(m.group(0)), None))
        if re.search(r"os\.environ|getenv|process\.env|import\.meta\.env", linea):
            continue
        for m in re.finditer(r"(?i)\b([A-Za-z0-9_]*(?:password|passwd|pwd|secret|api[_-]?key|token|contrase[nñ]a)[A-Za-z0-9_]*)\s*[:=]\s*['\"]([^'\"\s]{6,})['\"]", linea):
            if not es_placeholder(m.group(2)) and not NOMBRES_QUE_NO_SON_CLAVES.search(m.group(1)) and not VALORES_QUE_NO_SON_CLAVES.match(m.group(2)):
                salida.append((n, AVISO, "asignación de «" + m.group(1) + "» con un valor escrito en el código", ocultar(m.group(2)), ("asignacion", m.group(2))))
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


def base_de_datos_en(archivos, subcarpetas):
    """Si esta carpeta es el directorio de datos de un gestor de bases (las tablas de verdad), dice cuál."""
    if "PG_VERSION" in archivos and {"base", "global"} & set(subcarpetas):
        return "directorio de datos de PostgreSQL (las tablas de verdad)"
    if "ibdata1" in archivos:
        return "directorio de datos de MySQL o MariaDB (las tablas de verdad)"
    if "WiredTiger" in archivos:
        return "directorio de datos de MongoDB (las tablas de verdad)"
    return None


def revisar(carpeta, excluir=()):
    """Recorre la carpeta y devuelve un informe: qué entra, qué se aparta y por qué, y qué claves aparecen.
    No entra a node_modules, venv, .git ni demás carpetas que nunca van (entrar es lo que tardaba), ni al directorio de datos
    de una base, ni a lo que se pida con `excluir`."""
    pedidas = {e.strip("/\\").replace("\\", "/").lower() for e in excluir}
    entra, aparta, hallazgos, variables, total = [], [], {}, set(), 0
    for raiz, subcarpetas, nombres in os.walk(carpeta):
        raiz = Path(raiz)
        base = base_de_datos_en(nombres, subcarpetas)
        if base:
            aparta.append((raiz.relative_to(carpeta), base))
            subcarpetas[:] = []
            continue
        quedan = []
        for d in sorted(subcarpetas):
            rel_d = (raiz / d).relative_to(carpeta)
            if d in CARPETAS_QUE_NUNCA_VAN:
                continue
            if d.lower() in pedidas or rel_d.as_posix().lower() in pedidas:
                aparta.append((rel_d, "carpeta que pediste dejar fuera con --excluir"))
                continue
            quedan.append(d)
        subcarpetas[:] = quedan
        for nombre in sorted(nombres):
            ruta = raiz / nombre
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
*.backup
pgdata/
uploads/
exports/
backups/
logs/
instance/
# Entornos y empaques
node_modules/
site-packages/
.venv/
venv/
__pycache__/
*.pyc
dist/
build/
.DS_Store
"""


def quitar_en_linea(linea, tipo, valor):
    """Cambia SOLO la contraseña por la marca, sin tocar el resto de la línea (el usuario, la dirección, las comillas)."""
    v = re.escape(valor)
    if tipo == "url":
        return re.sub(r"(://[^\s:/@'\"]+:)" + v + r"(@)", lambda m: m.group(1) + MARCA_DE_CLAVE + m.group(2), linea)
    return re.sub(r"(['\"])" + v + r"(['\"])", lambda m: m.group(1) + MARCA_DE_CLAVE + m.group(2), linea)


def quitar_contrasenas(archivo, quitables):
    """Reescribe `archivo` (que es la COPIA) sin las contraseñas de `quitables` [(línea, tipo, valor)]. Respeta los fines de
    línea y los bytes que no son UTF-8. Devuelve cuántas líneas cambió."""
    texto = archivo.read_bytes().decode("utf-8", errors="surrogateescape")
    lineas = texto.split("\n")
    cambiadas = 0
    for n, tipo, valor in quitables:
        if 0 < n <= len(lineas):
            nueva = quitar_en_linea(lineas[n - 1], tipo, valor)
            if nueva != lineas[n - 1]:
                lineas[n - 1] = nueva
                cambiadas += 1
    archivo.write_bytes("\n".join(lineas).encode("utf-8", errors="surrogateescape"))
    return cambiadas


def se_puede_cambiar_en_todo(valor):
    """Un valor largo y con números o símbolos casi nunca es una palabra común; uno corto y de letras sí (postgres, admin)."""
    return len(valor) >= 8 and bool(re.search(r"[0-9]|[^A-Za-z0-9]", valor))


def barrer_valores(destino, valores):
    """Busca en TODA la copia las contraseñas que se quitaron de una línea concreta: casi siempre están también en otra forma
    (`CREATE USER … PASSWORD '…'`, `set PGPASSWORD=…`) que ninguna regla reconoce. Las largas se cambian por la marca; las cortas y
    de letras, que serían palabras comunes, solo se avisan. Devuelve ({archivo: veces cambiadas}, {archivo: veces vistas})."""
    cambiados, avisados = {}, {}
    for archivo in sorted(destino.rglob("*")):
        if not archivo.is_file() or archivo.stat().st_size > LIMITE_DE_LECTURA:
            continue
        datos = archivo.read_bytes()
        if b"\x00" in datos[:8000]:
            continue
        rel, nuevo = archivo.relative_to(destino), datos
        for valor in valores:
            aguja = valor.encode("utf-8")
            veces = nuevo.count(aguja)
            if not veces:
                continue
            if se_puede_cambiar_en_todo(valor):
                nuevo = nuevo.replace(aguja, MARCA_DE_CLAVE.encode("utf-8"))
                cambiados[rel] = cambiados.get(rel, 0) + veces
            else:
                avisados[rel] = avisados.get(rel, 0) + veces
        if nuevo != datos:
            archivo.write_bytes(nuevo)
    return cambiados, avisados


def armar_copia(carpeta, informe, salida, nombre, incluir_datos, quitar=False):
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
        quitables = [(n, q[0], q[1]) for n, _, _, _, q in informe["hallazgos"].get(rel, []) if q]
        if quitar and quitables:
            quitar_contrasenas(fin, quitables)
            informe.setdefault("sin_quitar", [])
            texto_final = fin.read_text(encoding="utf-8", errors="ignore")
            if any(h[4] for h in hallazgos_de_texto(texto_final)):
                informe["sin_quitar"].append(rel)  # sigue habiendo una contraseña: se avisa, no se calla
            else:
                informe.setdefault("sin_contrasena", []).append(rel)
    if quitar:
        valores = {q[1] for hs in informe["hallazgos"].values() for _, _, _, _, q in hs if q}
        informe["barrido"] = barrer_valores(destino, valores) if valores else ({}, {})
    previo = (destino / ".gitignore").read_text(encoding="utf-8") if (destino / ".gitignore").exists() else ""
    (destino / ".gitignore").write_text(previo.rstrip("\n") + ("\n\n" if previo else "") + bloque_gitignore(), encoding="utf-8")
    if not (destino / ".env.example").exists():  # el que ya traía la app (con sus comentarios) vale más que una lista de nombres
        (destino / ".env.example").write_text("".join(f"{v}=\n" for v in sorted(informe["variables"])), encoding="utf-8")
    (destino / "FICHA.md").write_text(plantilla_de_ficha(nombre, informe["variables"]), encoding="utf-8")
    if not (destino / "README.md").exists():
        (destino / "README.md").write_text(f"# {nombre}\n\nVer `FICHA.md`.\n", encoding="utf-8")
    return destino, copiados


def carpeta_alta(rel):
    return rel.parts[0] if len(rel.parts) > 1 else "(raíz)"


def imprimir(informe, carpeta, maximo=25, p=print):
    """El informe en pantalla (con `maximo` líneas por nivel) o completo (maximo=None) para el archivo."""
    p(f"\nRevisé {informe['total']} archivos de {carpeta}\n")
    p(f"  Entran a git:  {len(informe['entra'])}")
    donde = Counter(carpeta_alta(r) for r in informe["entra"])
    if donde:
        p("     por carpeta: " + " · ".join(f"{k} {v}" for k, v in donde.most_common(8)) + (" …" if len(donde) > 8 else ""))
    p(f"  Se apartan:    {len(informe['aparta'])}")
    por_motivo = {}
    for rel, motivo in informe["aparta"]:
        por_motivo.setdefault(motivo, []).append(rel)
    for motivo, lista in sorted(por_motivo.items(), key=lambda kv: -len(kv[1])):
        vista = lista if maximo is None else lista[:3]
        p(f"     – {len(lista):4}  {motivo}: " + ", ".join(r.as_posix() for r in vista) + (" …" if len(vista) < len(lista) else ""))
    por_carpeta = Counter(carpeta_alta(r) for r in informe["hallazgos"])
    rango = {CRITICO: 0, AVISO: 1, INFO: 2}
    filas = [(rel, n, nivel, que, vista) for rel, hs in informe["hallazgos"].items() for n, nivel, que, vista, _ in hs]
    filas.sort(key=lambda f: (rango[f[2]], por_carpeta[carpeta_alta(f[0])], f[0].as_posix(), f[1]))  # primero lo de las carpetas con pocos hallazgos
    criticos = con_critico(informe)
    por_nivel = Counter(f[2] for f in filas)
    p(f"\n  Claves: {len(informe['hallazgos'])} archivos con algo, {len(criticos)} de ellos con nivel CRÍTICO (esos NO se copian).")
    p(f"     líneas: {por_nivel[CRITICO]} críticas · {por_nivel[AVISO]} avisos · {por_nivel[INFO]} informativas")
    if por_carpeta:
        p("     archivos con hallazgos por carpeta: " + " · ".join(f"{k} {v}" for k, v in por_carpeta.most_common(6)))
    for nivel in (CRITICO, AVISO) + ((INFO,) if maximo is None else ()):
        del_nivel = [f for f in filas if f[2] == nivel]
        for rel, n, _, que, vista in (del_nivel if maximo is None else del_nivel[:maximo]):
            p(f"     [{nivel}] {rel.as_posix()}:{n}  {que}  → {vista}")
        if maximo is not None and len(del_nivel) > maximo:
            p(f"     … y {len(del_nivel) - maximo} {nivel} más, en el informe completo")
    if not filas:
        p("     ninguna")
    nombres = sorted(informe["variables"])
    corte = len(nombres) if maximo is None else 30
    p(f"\n  Variables de entorno que el código lee ({len(nombres)}): " + (", ".join(nombres[:corte]) or "ninguna") + (f" … y {len(nombres) - corte} más" if len(nombres) > corte else ""))


def autoprueba():
    """Crea una app falsa con claves sembradas y comprueba que se detectan, se apartan y no se copian."""
    global quitar_contrasenas
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
        (app / "pgdata" / "base" / "1").mkdir(parents=True)  # el directorio de datos de un PostgreSQL metido en la app
        (app / "pgdata" / "global").mkdir()
        (app / "pgdata" / "PG_VERSION").write_text("16\n", encoding="utf-8")
        (app / "pgdata" / "base" / "1" / "1259").write_bytes(b"\x00" * 64)
        (app / "pgdata" / "global" / "pg_control").write_bytes(b"\x00" * 64)
        (app / "lib" / "site-packages" / "x").mkdir(parents=True)  # código ajeno instalado: no es de la app y trae ejemplos de claves
        (app / "lib" / "site-packages" / "x" / "m.py").write_text("DB = 'postgresql://u:clave12345@db.ejemplo.com/x'\n", encoding="utf-8")
        (app / "vendor").mkdir()  # lo que el usuario pide dejar fuera con --excluir
        (app / "vendor" / "v.py").write_text("print('ajeno')\n", encoding="utf-8")
        (app / "cfg.py").write_text("SECRET_KEY = 'otra-clave-larga-999'\nNOMBRE = 'postgres'\n", encoding="utf-8")
        (app / "win.bat").write_bytes(b"@echo off\r\nset URL=postgresql://obra_usr:obra_dev1@localhost:5432/obra\r\nrem acci\xf3n en latin-1\r\n")
        (app / "inst.bat").write_text('psql -c "CREATE USER obra_usr WITH PASSWORD \'obra_dev1\'"\n', encoding="utf-8")  # la misma contraseña, en una forma que ninguna regla reconoce
        (app / "notas.txt").write_text("usuario postgres en la base postgres\n", encoding="utf-8")  # palabra común: se avisa, no se cambia
        (app / ".env.example").write_text("SUPABASE_URL=\n# comentario del autor\n", encoding="utf-8")
        (app / "tipos.py").write_text("TOKEN_TYPE = 'bearer-largo'\nAPI_KEY_URL = 'https://x.example/k'\n", encoding="utf-8")
        informe = revisar(app, excluir=["Vendor"])
        apartados = {r.as_posix() for r, _ in informe["aparta"]}
        esperado_apartado = {".env", "datos.db", "uploads/estimacion.xlsx", "uploads/recibo.png", "grande.bin", "pgdata", "vendor"}
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
        if "tipos.py" in {r.as_posix() for r in informe["hallazgos"]}:
            errores.append("marcó TOKEN_TYPE y API_KEY_URL, que no son claves")
        if "limpio.py" in informe["hallazgos"]:
            errores.append("marcó un archivo limpio (password='password' es un marcador)")
        if informe["variables"] != {"TOKEN_X", "VITE_URL", "CLAVE_API"}:
            errores.append(f"variables {sorted(informe['variables'])}")
        destino, copiados = armar_copia(app, informe, raiz / "salida", "prueba", False)
        dentro = {p.relative_to(destino).as_posix() for p in destino.rglob("*") if p.is_file()}
        for prohibido in ("app.py", "config.js", ".env", "datos.db", "uploads/estimacion.xlsx", "uploads/recibo.png", "grande.bin", "node_modules/x/i.js",
                           "pgdata/PG_VERSION", "pgdata/base/1/1259", "pgdata/global/pg_control", "vendor/v.py", "lib/site-packages/x/m.py"):
            if prohibido in dentro:
                errores.append(f"copió {prohibido}")
        sin, _ = armar_copia(app, informe, raiz / "salida_sin", "prueba", False, quitar=True)
        orig_dev = (app / "dev.py").read_text(encoding="utf-8")
        copia_dev = (sin / "dev.py").read_text(encoding="utf-8")
        if "postgres:postgres@" in copia_dev or MARCA_DE_CLAVE not in copia_dev:
            errores.append("--quitar-contrasenas no sacó la contraseña de la copia de dev.py")
        if "postgresql://postgres:" + MARCA_DE_CLAVE + "@localhost:5432/x" not in copia_dev:
            errores.append("--quitar-contrasenas tocó más que la contraseña (usuario, esquema o dirección)")
        if "postgres:postgres@" not in orig_dev:
            errores.append("¡--quitar-contrasenas cambió el ORIGINAL!")
        copia_cfg = (sin / "cfg.py").read_text(encoding="utf-8")
        if "otra-clave-larga-999" in copia_cfg or "SECRET_KEY = '" + MARCA_DE_CLAVE + "'" not in copia_cfg or "NOMBRE = 'postgres'" not in copia_cfg:
            errores.append("--quitar-contrasenas falló con una asignación (o tocó una línea que no era la hallada)")
        copia_bat = (sin / "win.bat").read_bytes()
        if b"obra_dev1" in copia_bat or b"\r\n" not in copia_bat or b"acci\xf3n" not in copia_bat:
            errores.append("--quitar-contrasenas rompió los fines de línea o los bytes no UTF-8 de win.bat")
        if informe.get("sin_quitar"):
            errores.append("quedó una contraseña sin quitar: " + str(informe["sin_quitar"]))
        inst = (sin / "inst.bat").read_bytes()
        if b"obra_dev1" in inst or MARCA_DE_CLAVE.encode() not in inst:
            errores.append("el barrido no cambió la misma contraseña escrita en otra forma (inst.bat)")
        if b"usuario postgres en la base postgres" not in (sin / "notas.txt").read_bytes():
            errores.append("el barrido cambió una palabra común y corta (postgres)")
        if "notas.txt" not in {r.as_posix() for r in informe["barrido"][1]}:
            errores.append("el barrido no avisó de la palabra corta que dejó sin cambiar")
        if b"comentario del autor" not in (sin / ".env.example").read_bytes():
            errores.append("pisó el .env.example que ya traía la app")
        real = quitar_contrasenas  # si quitar no logra quitar, tiene que avisar y no callar
        quitar_contrasenas = lambda *args: 0
        try:
            otro = dict(informe)
            otro.pop("sin_quitar", None)
            otro.pop("sin_contrasena", None)
            armar_copia(app, otro, raiz / "salida_x", "prueba", False, quitar=True)
        finally:
            quitar_contrasenas = real
        if not otro.get("sin_quitar"):
            errores.append("no avisó que quedaba una contraseña en la copia")
        lineas = []
        imprimir(informe, app, maximo=None, p=lineas.append)
        if not any("PostgreSQL" in l and "pgdata" in l for l in lineas):
            errores.append("el informe completo no nombra el directorio de datos de PostgreSQL")
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
    ap.add_argument("--excluir", action="append", default=[], metavar="CARPETA",
                    help="deja fuera una carpeta entera por su nombre o ruta relativa (se puede repetir); p. ej. --excluir postgresql")
    ap.add_argument("--quitar-contrasenas", action="store_true",
                    help="en la COPIA (nunca en tu app) cambia las contraseñas escritas en el código por " + MARCA_DE_CLAVE)
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
    informe = revisar(a.carpeta, a.excluir)
    imprimir(informe, a.carpeta)
    destino, copiados = armar_copia(a.carpeta, informe, a.salida, a.nombre, a.incluir_datos, a.quitar_contrasenas)
    completo = []
    imprimir(informe, a.carpeta, maximo=None, p=completo.append)
    archivo_informe = a.salida / f"{a.nombre}-informe.txt"
    archivo_informe.write_text("\n".join(completo) + "\n", encoding="utf-8")
    print(f"\nCopia limpia: {destino}  ({copiados} archivos + .gitignore, .env.example, FICHA.md)")
    print(f"Informe completo (valores tapados): {archivo_informe}")
    if a.quitar_contrasenas:
        quitados = informe.get("sin_contrasena", [])
        print(f"\nContraseñas quitadas de la copia (cambiadas por {MARCA_DE_CLAVE}): {len(quitados)} archivos."
              + (" Tu app original no se tocó." if quitados else " No había ninguna que quitar."))
        cambiados, avisados = informe.get("barrido", ({}, {}))
        if cambiados:
            print(f"Barrido del resto de la copia: la misma contraseña estaba también, en otra forma, en {len(cambiados)} archivos más "
                  f"(cambiada): {', '.join(r.as_posix() for r in list(cambiados)[:8])}" + (" …" if len(cambiados) > 8 else ""))
        if avisados:
            print(f"  Aparece también, sin cambiarse por ser una palabra corta y común, en: "
                  f"{', '.join(r.as_posix() + ' (' + str(v) + ')' for r, v in list(avisados.items())[:8])}. Revisa si es la contraseña o solo la palabra.")
        for rel in informe.get("sin_quitar", []):
            print(f"  OJO: en {rel.as_posix()} sigue habiendo una contraseña; quítala a mano antes de subir.")
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
    return 2 if (criticos or informe.get("sin_quitar")) else 0


if __name__ == "__main__":
    sys.exit(main())
