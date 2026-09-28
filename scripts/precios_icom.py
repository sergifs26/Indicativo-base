"""
Fase 0.2 — Precios Icom (LISTA PVP AFICIONADO 11022026 Rev2.pdf)

Fuente de verdad: data/precios_icom_revisado.csv (tabla revisada a mano página a página; el PDF
tiene las columnas de precio desplazadas en la mitad de las páginas y la extracción automática no
es fiable). Este script:

1. Extrae el texto del PDF (pdftotext -layout) y detecta líneas "MODELO ... tarifa pvp" como
   auditoría: data/precios_icom_extraido.csv (flag ok = pvp ≈ tarifa × 1,21).
2. Valida la tabla revisada (pvp = tarifa × 1,21 ± 0,05) y la contrasta con lo extraído.
3. Cruza con data/catalogo_maestro.json (solo productos Icom) por SKU normalizado y escribe:
     data/precios_icom_final.csv  -> modelo, tarifa, pvp, sku_excel (vacío = producto nuevo)
     data/icom_nuevos.csv         -> modelos con precio que no están en el Excel
"""
from __future__ import annotations

import csv
import json
import os
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
# Ficheros de proveedor fuera de git: carpeta padre del repo (o INDICATIVO_FUENTES).
FUENTES = Path(os.environ.get("INDICATIVO_FUENTES", ROOT.parent))
PDF = FUENTES / "LISTA PVP AFICIONADO 11022026 Rev2.pdf"
OUT = ROOT / "data"
PDFTOTEXT = Path(r"C:\Program Files\Git\mingw64\bin\pdftotext.exe")
IVA = 1.21

LINEA_RE = re.compile(
    r"^\s*([A-Z][A-Z0-9][A-Z0-9\-/\.]{1,18}(?:\s(?:PLUS|Ver\.2|\(PACK\)))?)(?:\s+#\d+)?\s+(?:Ficha\s+)?(.*?)\s+"
    r"(\d{1,3}(?:\.\d{3})*(?:,\d{2})?|S/C)\s+(\d{1,3}(?:\.\d{3})*(?:[,\.]\d{2})?|S/C)\s*$"
)
EXCLUIR = {"MODELO", "TARIFA", "HAM", "TODO"}

# Excel -> modelo de la lista cuando el SKU no coincide letra a letra
EQUIVALENCIAS = {
    "ID52E": "ID52EPLUS",   # el Excel lista "ID-52E"; la tarifa solo tiene la versión PLUS (verificar)
}


def num(s: str) -> float | None:
    s = (s or "").strip()
    if s in ("", "S/C", "--"):
        return None
    if "," in s:
        s = s.replace(".", "").replace(",", ".")
    return round(float(s), 2)


def norm(s: str) -> str:
    return re.sub(r"[^A-Z0-9]", "", str(s).upper().split("#")[0])


def extraer() -> list[dict]:
    txt = subprocess.run([str(PDFTOTEXT), "-layout", str(PDF), "-"], capture_output=True, check=True).stdout
    texto = txt.decode("utf-8", errors="replace")
    (OUT / "precios_icom_texto.txt").write_text(texto, encoding="utf-8")
    filas = []
    for n, linea in enumerate(texto.splitlines(), 1):
        m = LINEA_RE.match(linea)
        if not m:
            continue
        modelo, desc, t, p = m.groups()
        if modelo.split()[0].upper() in EXCLUIR or not re.search(r"\d", modelo):
            continue
        tarifa, pvp = num(t), num(p)
        ok = tarifa is not None and pvp is not None and abs(pvp - round(tarifa * IVA, 2)) <= 0.05
        filas.append({"modelo": modelo.strip(), "descripcion": desc.strip(), "tarifa": tarifa,
                      "pvp": pvp, "ok": ok, "linea": n})
    return filas


def main() -> None:
    extraido = extraer()
    with (OUT / "precios_icom_extraido.csv").open("w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=["modelo", "descripcion", "tarifa", "pvp", "ok", "linea"])
        w.writeheader()
        w.writerows(extraido)
    auto_ok: dict[str, set[float]] = {}
    for r in extraido:
        if r["ok"]:
            auto_ok.setdefault(norm(r["modelo"]), set()).add(r["pvp"])

    # Tabla revisada (fuente de verdad)
    revisado: list[dict] = []
    with (OUT / "precios_icom_revisado.csv").open(encoding="utf-8-sig") as f:
        for r in csv.DictReader(f):
            tarifa, pvp = num(r["tarifa"]), num(r["pvp"])
            if tarifa is not None and pvp is not None:
                assert abs(pvp - round(tarifa * IVA, 2)) <= 0.05, f"{r['modelo']}: {tarifa} x 1,21 != {pvp}"
            revisado.append({"modelo": r["modelo"].strip(), "descripcion": r["descripcion"].strip(),
                             "tarifa": tarifa, "pvp": pvp, "nota": r.get("nota", "").strip()})
    claves = [norm(r["modelo"]) for r in revisado]
    assert len(claves) == len(set(claves)), "modelos repetidos en precios_icom_revisado.csv"

    # Contraste con la extracción automática (informativo)
    coincide = discrepa = sin_auto = 0
    for r in revisado:
        if r["pvp"] is None:
            continue
        vals = auto_ok.get(norm(r["modelo"]))
        if not vals:
            sin_auto += 1
        elif r["pvp"] in vals:
            coincide += 1
        else:
            discrepa += 1
            print(f"  ! {r['modelo']}: revisado {r['pvp']} / automático {sorted(vals)}")

    # Cruce con el catálogo (solo productos Icom)
    cat = json.loads((OUT / "catalogo_maestro.json").read_text(encoding="utf-8"))
    icom = [p for p in cat if p["vendor"].lower() == "icom" or p["titulo"].lower().startswith("icom")]
    por_sku: dict[str, dict] = {}
    for p in icom:
        k = norm(p["sku"])
        por_sku.setdefault(EQUIVALENCIAS.get(k, k), p)

    final, nuevos = [], []
    for r in revisado:
        p = por_sku.get(norm(r["modelo"]))
        fila = {**r, "sku_excel": p["sku"] if p else "", "titulo_excel": p["titulo"] if p else ""}
        final.append(fila)
        if p is None and r["pvp"] is not None:
            nuevos.append(fila)

    campos = ["modelo", "descripcion", "tarifa", "pvp", "nota", "sku_excel", "titulo_excel"]
    for nombre, datos in (("precios_icom_final.csv", final), ("icom_nuevos.csv", nuevos)):
        with (OUT / nombre).open("w", newline="", encoding="utf-8-sig") as f:
            w = csv.DictWriter(f, fieldnames=campos)
            w.writeheader()
            w.writerows(datos)

    con_precio = [r for r in final if r["pvp"] is not None]
    print(f"Extracción automática: {len(extraido)} líneas, {sum(r['ok'] for r in extraido)} válidas")
    print(f"Tabla revisada: {len(revisado)} modelos, {len(con_precio)} con precio, "
          f"{len(revisado) - len(con_precio)} software sin cargo")
    print(f"Contraste con automático: {coincide} coinciden, {discrepa} discrepan, {sin_auto} sin dato automático")
    print(f"Productos Icom en el Excel: {len(icom)} | con precio de la lista: {len([r for r in con_precio if r['sku_excel']])}")
    print("  " + ", ".join(f"{r['modelo']}->{r['sku_excel']}" for r in con_precio if r["sku_excel"]))
    print(f"Nuevos (con precio, no están en el Excel): {len(nuevos)}")


if __name__ == "__main__":
    main()
