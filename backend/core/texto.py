"""
Qué diferencia de texto dispara alerta — `CONOCIMIENTO.md` §2.7.1, D-477.

**Un porcentaje de diferencia no sirve como regla**: engaña en los dos sentidos. *De 3.00 a 4.20 m* es un cambio mínimo de texto y
enorme de significado; reordenar una frase es un cambio grande sin consecuencia. Por eso:

1. **Primero se normaliza** —minúsculas, acentos, plurales, los conectores, el «Incluye:» y los sinónimos que se le den— y se compara el
   **núcleo**. Idéntico → era cosmético, sin alerta.
2. **Si difiere, se clasifica por qué tipo de palabra cambió:**

   | Cambió | Nivel |
   |---|---|
   | Un número o una dimensión (*3.00 → 4.20*, *15x30 → 15x20*) | **alta** |
   | El verbo o el elemento (*colocación → suministro*, *tabique → block*) | **alta** |
   | El orden de las palabras, o un calificativo (*nuevo*, *similar*, *aproximado*…) | informativa |

Los números se comparan como números (*3.00* es *3*), no como texto. Una palabra que cambia es alta salvo que sea de las que la lista
de calificativos reconoce: ante la duda se alerta, porque «alerta» no detiene nada por sí sola —lo que detiene es cruzar el texto con
la huella (`catalogo.py`)—.

El diccionario de sinónimos de §2.7.1 no existe todavía en este repositorio: `comparar` lo recibe como parámetro (`{palabra: canónica}`)
y sin él solo normaliza lo demás. Es pura: no lee ni escribe nada.
"""
from __future__ import annotations

import re
import unicodedata
from collections import Counter
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from typing import Dict, FrozenSet, List, Mapping, Optional, Tuple

IGUAL, INFORMATIVA, ALTA = "igual", "informativa", "alta"

# conectores: no llevan significado propio en una descripción de concepto
CONECTORES: FrozenSet[str] = frozenset({"de", "del", "la", "las", "el", "los", "en", "y", "e", "o", "u", "con", "para", "por", "a", "al", "un", "una", "que", "se"})
# el «Incluye:» con que OPUS abre algunas descripciones largas
PREFIJOS: FrozenSet[str] = frozenset({"incluye"})
# palabras que califican y no cambian de qué se trata; el resto, si cambia, es alta
CALIFICATIVOS: FrozenSet[str] = frozenset({
    "nuevo", "nueva", "aprox", "aproximado", "aproximada", "similar", "comercial", "estandar", "normal", "completo", "completa", "adicional", "general",
    "corregido", "corregida", "actualizado", "actualizada", "revisado", "revisada",  # lo que se le anota a un texto sin cambiar de qué se trata
})

_TOKEN = re.compile(r"\d+(?:[.,]\d+)?|[^\W\d_]+")


@dataclass(frozen=True)
class DiferenciaDeTexto:
    nivel: str  # igual · informativa · alta
    motivo: str = ""  # numero · palabra · orden · calificativo; vacío si es igual
    detalle: str = ""  # lo que cambió, para quien decide: «3.00 → 4.20», «tabique → block»

    @property
    def alerta(self) -> bool:
        return self.nivel != IGUAL


def _plural(palabra: str) -> str:
    """Un plural casi siempre es el mismo elemento: se compara en singular. No pretende ser correcto en español, solo estable."""
    if len(palabra) > 5 and palabra.endswith("ones"):
        return palabra[:-2]
    if len(palabra) > 3 and palabra.endswith("s"):
        return palabra[:-1]
    return palabra


def nucleo(texto: str, sinonimos: Optional[Mapping[str, str]] = None) -> Tuple[Tuple[str, ...], Tuple[Decimal, ...]]:
    """(palabras, números) del texto ya normalizado, cada uno en el orden en que aparece."""
    sin_acentos = "".join(c for c in unicodedata.normalize("NFKD", texto.casefold()) if not unicodedata.combining(c))
    canon = {_plural(k): v for k, v in (sinonimos or {}).items()}
    palabras: List[str] = []
    numeros: List[Decimal] = []
    for t in _TOKEN.findall(sin_acentos):
        if t[0].isdigit():
            try:
                numeros.append(Decimal(t.replace(",", ".")).normalize())
            except InvalidOperation:  # pragma: no cover  (el patrón solo deja pasar números)
                palabras.append(t)
            continue
        if t in PREFIJOS or t in CONECTORES:
            continue
        p = _plural(t)
        palabras.append(canon.get(p, p))
    return tuple(palabras), tuple(numeros)


def _numero(d: Decimal) -> str:
    return format(d, "f")


def comparar(antes: str, despues: str, sinonimos: Optional[Mapping[str, str]] = None) -> DiferenciaDeTexto:
    """Cómo cambió un texto: nada, algo informativo o algo que alerta, y qué."""
    pa, na = nucleo(antes, sinonimos)
    pd, nd = nucleo(despues, sinonimos)
    if pa == pd and na == nd:
        return DiferenciaDeTexto(IGUAL)
    if Counter(na) != Counter(nd):
        quitados = sorted((Counter(na) - Counter(nd)).elements())
        puestos = sorted((Counter(nd) - Counter(na)).elements())
        return DiferenciaDeTexto(ALTA, "numero", f"{' '.join(map(_numero, quitados)) or '—'} → {' '.join(map(_numero, puestos)) or '—'}")
    if Counter(pa) == Counter(pd):
        return DiferenciaDeTexto(INFORMATIVA, "orden", "las mismas palabras en otro orden")
    quitadas = sorted((Counter(pa) - Counter(pd)).elements())
    puestas = sorted((Counter(pd) - Counter(pa)).elements())
    if all(p in CALIFICATIVOS for p in quitadas + puestas):
        return DiferenciaDeTexto(INFORMATIVA, "calificativo", f"{' '.join(quitadas) or '—'} → {' '.join(puestas) or '—'}")
    return DiferenciaDeTexto(ALTA, "palabra", f"{' '.join(quitadas) or '—'} → {' '.join(puestas) or '—'}")


def clave_nueva(clave: str, existentes: FrozenSet[str]) -> str:
    """La clave que se propone cuando un concepto cambió tanto que es otro (§2.7.1: «el sistema propone clave nueva»): la siguiente libre
    del mismo prefijo, con el mismo ancho de número. Una propuesta, no una decisión: quien decide la puede cambiar."""
    m = re.fullmatch(r"(.*?)(\d+)", clave)
    if m is None:
        return clave + "-2"
    prefijo, numero = m.group(1), m.group(2)
    mayor = max([int(x.group(2)) for k in existentes | {clave} if (x := re.fullmatch(r"(.*?)(\d+)", k)) and x.group(1) == prefijo] or [int(numero)])
    return f"{prefijo}{mayor + 1:0{len(numero)}d}"
