"""
Antena original de recambio para cada walkie (casilla «Añade una antena de recambio» de la ficha).

Solo la antena ORIGINAL del modelo, nunca universales: en los PMR-446 la normativa exige antena
integrada, así que solo cabe el recambio del fabricante. Una antena es la original de un walkie si:
  1. es una antena (categoría Antenas…, «antena» en el título, no un kit);
  2. es de la misma marca (vendor) o cita la marca del walkie en su título;
  3. su TÍTULO cita el modelo del walkie (en la descripción no basta: ahí salen compatibles);
  4. la banda no choca (un walkie UHF no recibe una antena que solo dice VHF, y al revés).
Si hay varias (normal y corta), se queda la normal. data/antenas_excepciones.csv
(handle;antena;motivo) manda sobre todo: antena = handle de otra antena, o «-» para ninguna.

Uso:
  python scripts/antenas.py            # informe data/antenas_informe.md + data/antenas_recambio.json
Aplicar (metacampo custom.antenas_recambio):  node scripts/aplicar_antenas.mjs [--apply]
"""
from __future__ import annotations

import csv
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
PRODUCTOS = DATA / "shopify" / "bulk" / "productos.jsonl"
EXCEPCIONES = DATA / "antenas_excepciones.csv"
SALIDA = DATA / "antenas_recambio.json"
INFORME = DATA / "antenas_informe.md"

CODIGO_RE = re.compile(r"\b(?:[A-Z]{1,4}-?[A-Z]{0,3}\d{1,4}[A-Z]{0,3}|\d{3,4}[A-Z]{1,2})\+?(?![\w-])")
TAMANO_RE = re.compile(r"corta|larga|telesc[oó]pica|flexible|t[aá]ctica", re.I)


def plano(html: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html or ""))


def codigos(titulo: str) -> set[str]:
    """Códigos de modelo del título, normalizados sin guiones: «R-58» → «R58», «L-88+» → «L88»."""
    out = set()
    for m in CODIGO_RE.findall(titulo.upper()):
        c = m.replace("-", "").rstrip("+")
        if re.search(r"446|PMR|MHZ|MAH", c) or re.fullmatch(r"\d+[A-Z]?", c) and not re.fullmatch(r"\d{3,4}[A-Z]{1,2}", c):
            continue
        if len(c) >= 3:
            out.add(c)
    return out


def _letra_de_mas(largo: str, corto: str) -> bool:
    return len(corto) >= 3 and largo.startswith(corto) and len(largo) - len(corto) == 1 and largo[-1].isalpha()


def bandas(texto: str) -> set[str]:
    return {b for b in ("VHF", "UHF") if re.search(rf"\b{b}\b", texto, re.I)}


def leer():
    productos = [json.loads(l)["input"] for l in PRODUCTOS.read_text(encoding="utf-8").splitlines() if l.strip()]
    for p in productos:
        p["_cats"] = {t[4:] for t in p["tags"] if t.startswith("cat:")}
    return productos


def es_walkie(p) -> bool:
    return any(c.startswith("Walkies>") or c == "Outdoor>Walkies Outdoor" for c in p["_cats"])


def es_antena(p) -> bool:
    return (any(c.startswith("Antenas") for c in p["_cats"]) and re.search(r"antena", p["title"], re.I)
            and not re.search(r"\bkit\b", p["title"], re.I))


def original(walkie, antenas) -> list[dict]:
    marca = (walkie["vendor"] or "").lower()
    cods = codigos(walkie["title"])
    banda_w = bandas(walkie["title"])
    elegidas = []
    for a in antenas:
        t = a["title"]
        if not ((a["vendor"] or "").lower() == marca or (marca and marca in t.lower())):
            continue
        tokens = {x.replace("-", "").rstrip("+") for x in re.findall(r"[A-Z0-9][A-Z0-9+-]*", t.upper())}
        # mismo código, o que uno lleve una letra de más al final («FT-4X» / «FT-4XE», «FTA-250L» / «FTA-250»)
        if not any(tok == c or _letra_de_mas(tok, c) or _letra_de_mas(c, tok) for c in cods for tok in tokens):
            continue
        banda_a = bandas(t)
        if banda_w and banda_a and not (banda_w & banda_a):
            continue
        elegidas.append(a)
    # la normal antes que la corta/larga; a igualdad, la de título más corto
    return sorted(elegidas, key=lambda a: (bool(TAMANO_RE.search(a["title"])), len(a["title"])))


def main() -> None:
    productos = leer()
    por_handle = {p["handle"]: p for p in productos}
    antenas = [p for p in productos if es_antena(p)]
    walkies = [p for p in productos if es_walkie(p)]

    excepciones = {}
    if EXCEPCIONES.exists():
        with EXCEPCIONES.open(encoding="utf-8-sig", newline="") as f:
            for fila in csv.DictReader(f, delimiter=";"):
                h = (fila.get("handle") or "").strip()
                if h and not h.startswith("#"):
                    excepciones[h] = ((fila.get("antena") or "").strip(), (fila.get("motivo") or "").strip())

    pares, filas, sin = {}, [], []
    for w in walkies:
        cands = original(w, antenas)
        motivo = "regla"
        if w["handle"] in excepciones:
            antena, motivo = excepciones[w["handle"]]
            cands = [] if antena == "-" else [por_handle[antena]] if antena in por_handle else cands
            motivo = f"excepción: {motivo}"
        if cands:
            pares[w["handle"]] = [cands[0]["handle"]]
            otras = f" (también: {', '.join(c['title'] for c in cands[1:])})" if len(cands) > 1 else ""
            filas.append(f"| {w['title']} | {cands[0]['title']}{otras} | {motivo} |")
        else:
            sin.append(w)

    SALIDA.write_text(json.dumps(pares, ensure_ascii=False, indent=1), encoding="utf-8")
    pmr = re.compile(r"PMR|446", re.I)
    sin_desmontable = [w for w in sin if not pmr.search(w["title"]) and not any("PMR" in c for c in w["_cats"])]
    L = ["# Antena original de recambio por walkie", "",
         f"Walkies: **{len(walkies)}** · con antena original: **{len(pares)}** · antenas candidatas: {len(antenas)}", "",
         "Solo antenas originales del modelo (misma marca, modelo citado en el título de la antena, banda "
         "compatible). Para corregir: `data/antenas_excepciones.csv`.", "",
         "| Walkie | Antena original | Origen |", "|---|---|---|", *filas, "",
         f"## Walkies de antena desmontable sin antena original en el catálogo ({len(sin_desmontable)})", "",
         *[f"- {w['title']}" for w in sin_desmontable], "",
         "Los PMR-446 sin antena original no aparecen: llevan la antena fija (normativa)."]
    INFORME.write_text("\n".join(L) + "\n", encoding="utf-8")
    print(f"{len(pares)} walkies con antena original → {SALIDA.name}; informe → {INFORME.name}")


if __name__ == "__main__":
    main()
