"""
Fase 0.1 — Limpieza del catálogo (Export-info-productes.xlsx -> data/catalogo_maestro.*)

Reglas:
  - Fuera: filas de prueba ("Test nombre completo…") y productos que SOLO están en "Descatalogados".
  - SKU: se generan para packs sin SKU (PACK-<id>) y se resuelven duplicados con SKU_OVERRIDES.
  - Marca: la primera de "Marcas" (separador |) es el vendor; todas van como tag marca:<x>.
  - Categorías: cada ruta "A>B>C" genera tags cat:A, cat:A>B, cat:A>B>C. Tipo = nivel 1 de la
    categoría principal (la primera que no sea Descatalogados/OUTLET/Ofertas/PACKS/Bases).
  - Descripción: enlaces a pihernz.com -> texto plano; se eliminan menciones a Pihernz.
  - Peso: gramos; si falta, mediana de su categoría nivel 1 (tag peso-estimado).

Salida: data/catalogo_maestro.csv, data/catalogo_maestro.json, data/informe_limpieza.md
"""
from __future__ import annotations

import json
import os
import re
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
# Los ficheros de proveedor NO están en git: viven en la carpeta padre del repo
# (o donde diga INDICATIVO_FUENTES).
FUENTES = Path(os.environ.get("INDICATIVO_FUENTES", ROOT.parent))
SRC = FUENTES / "Export-info-productes.xlsx"
OUT = ROOT / "data"
OUT.mkdir(exist_ok=True)

# Categorías "contenedor" que no describen el producto: no se usan como categoría principal.
CATS_SECUNDARIAS = ("Descatalogados", "OUTLET", "Ofertas", "PACKS", "Bases")

# Resolución manual de SKUs duplicados (id de WooCommerce -> SKU nuevo). None = eliminar fila.
SKU_OVERRIDES: dict[int, str | None] = {
    61989: None,            # Test variación 1
    61992: None,            # Test variación 2
    61193: "F226-ARNES",    # Funda Aquapac Extreme VHF Pro 226 con arnés (la otra F226 se queda)
    80612: "ICA220E",       # ICOM IC-A220 TSO (estaba con el SKU del IC-A120)
    64699: None,            # ICOM IC-R15 duplicado (se queda id 63145)
    92618: "PTTABK2-Q8",    # Auricular BT Q8
    92620: "PTTABK2-Q9",    # Auricular BT Q9
    69323: "QDRJ11-CLEYVER",  # Cable QD-RJ11 Plantronics y Cleyver
    93267: "HAMMER-IRONV",  # Hammer Iron V (estaba con el SKU del Ulefone)
}

LINK_RE = re.compile(r'<a\b[^>]*href="[^"]*pihernz\.com[^"]*"[^>]*>(.*?)</a>', re.I | re.S)
ANY_LINK_RE = re.compile(r'<a\b[^>]*>(.*?)</a>', re.I | re.S)
PIHERNZ_RE = re.compile(r'\b(en|de|por)?\s*Pihernz(\s+Comunicaciones)?\b', re.I)


def limpiar_html(texto: str) -> str:
    if not isinstance(texto, str):
        return ""
    t = LINK_RE.sub(r"\1", texto)                 # enlaces a pihernz -> texto
    t = re.sub(r'<img\b[^>]*pihernz\.com[^>]*>', "", t, flags=re.I)
    t = PIHERNZ_RE.sub("", t)                     # menciones a la marca del distribuidor
    t = re.sub(r"[ \t]{2,}", " ", t)
    t = re.sub(r"\n{3,}", "\n\n", t)
    return t.strip()


def slug(texto: str) -> str:
    t = str(texto).lower()
    t = (t.replace("á", "a").replace("é", "e").replace("í", "i").replace("ó", "o")
         .replace("ú", "u").replace("ñ", "n").replace("ü", "u"))
    t = re.sub(r"[^a-z0-9]+", "-", t).strip("-")
    return t[:80] or "producto"


def main() -> None:
    df = pd.read_excel(SRC, sheet_name=0)
    n0 = len(df)
    df = df.drop(columns=[c for c in df.columns if c.startswith("Unnamed") or c == "Marcas.1"])
    df["id"] = df["id"].astype(int)

    # 1. Filas de prueba y descatalogados
    es_test = df["Title"].str.startswith("Test nombre completo", na=False)
    cats = df["Categorías del producto"].fillna("").astype(str)
    solo_desc = cats.apply(lambda s: s != "" and all(p.strip().startswith("Descatalogados") for p in s.split("|")))
    df = df[~es_test & ~solo_desc].copy()
    n_test, n_desc = int(es_test.sum()), int(solo_desc.sum())

    # 2. SKU
    df["SKU"] = df["SKU"].apply(lambda v: "" if pd.isna(v) else str(v).strip())
    eliminar = [i for i, s in SKU_OVERRIDES.items() if s is None]
    df = df[~df["id"].isin(eliminar)].copy()
    for pid, nuevo in SKU_OVERRIDES.items():
        if nuevo:
            df.loc[df["id"] == pid, "SKU"] = nuevo
    sin_sku = df["SKU"] == ""
    df.loc[sin_sku, "SKU"] = "PACK-" + df.loc[sin_sku, "id"].astype(str)
    dup = df["SKU"].duplicated(keep=False)
    assert not dup.any(), f"SKUs duplicados sin resolver: {df.loc[dup, ['id','SKU','Title']].to_dict('records')}"

    # 3. Marcas
    marcas = df["Marcas"].fillna("").astype(str).apply(lambda s: [m.strip() for m in s.split("|") if m.strip()])
    df["vendor"] = marcas.apply(lambda l: l[0] if l else "")
    df["marcas_lista"] = marcas

    # 4. Categorías
    def rutas(s: str) -> list[str]:
        return [r.strip() for r in str(s).split("|") if r.strip()]

    df["categorias_lista"] = df["Categorías del producto"].fillna("").apply(rutas)

    # Categorías huérfanas de nivel 1 (p. ej. "Baterías") que en el resto del Excel existen como
    # hoja de una sola ruta ("Accesorios Walkies>Baterías") se llevan a esa ruta. No se tocan las
    # que tienen hijos propios ni "Bases" (cajón de sastre sin relación con bases de antena).
    todas = {r for rs in df["categorias_lista"] for r in rs}
    con_hijos = {r.split(">")[0].strip() for r in todas if ">" in r}
    padres: dict[str, set[str]] = {}
    for r in todas:
        if ">" in r:
            padres.setdefault(r.split(">")[-1].strip(), set()).add(r)
    NO_REMAPEAR = {"Bases"}
    remapeo = {x: next(iter(ps)) for x, ps in padres.items()
               if len(ps) == 1 and x in todas and x not in con_hijos and x not in NO_REMAPEAR}
    n_remap = int(df["categorias_lista"].apply(lambda rs: any(r in remapeo for r in rs)).sum())

    def remapear(rs: list[str]) -> list[str]:
        out: list[str] = []
        for r in rs:
            r2 = remapeo.get(r, r)
            if r2 not in out:
                out.append(r2)
        return out

    df["categorias_lista"] = df["categorias_lista"].apply(remapear)

    def principal(rs: list[str]) -> str:
        for r in rs:
            if not r.startswith(CATS_SECUNDARIAS):
                return r
        return rs[0] if rs else "Sin categoría"

    df["categoria_principal"] = df["categorias_lista"].apply(principal)
    df["tipo"] = df["categoria_principal"].str.split(">").str[0].str.strip()

    def tags(row) -> list[str]:
        t: list[str] = []
        for r in row["categorias_lista"]:
            partes = [p.strip() for p in r.split(">")]
            for k in range(1, len(partes) + 1):
                tag = "cat:" + ">".join(partes[:k])
                if tag not in t:
                    t.append(tag)
        for m in row["marcas_lista"]:
            t.append("marca:" + m)
        if any(r.startswith("OUTLET") for r in row["categorias_lista"]):
            t.append("outlet")
        if any(r.startswith("Ofertas") for r in row["categorias_lista"]):
            t.append("oferta")
        if any(r.startswith("PACKS") for r in row["categorias_lista"]) or row["SKU"].startswith("PACK-"):
            t.append("pack")
        if any(r.startswith("Descatalogados") for r in row["categorias_lista"]):
            t.append("descatalogado")
        return t

    df["tags"] = df.apply(tags, axis=1)

    # 5. Descripciones
    df["descripcion_html"] = df["Content"].apply(limpiar_html)
    df["descripcion_corta"] = df["Short Description"].fillna("").astype(str).str.strip()
    restos = df["descripcion_html"].str.contains("pihernz", case=False).sum()

    # 6. Peso en gramos
    df["peso_g"] = pd.to_numeric(df["Weight"], errors="coerce")
    df.loc[df["peso_g"] <= 0, "peso_g"] = pd.NA
    mediana_tipo = df.groupby("tipo")["peso_g"].median()
    global_med = df["peso_g"].median()
    falta_peso = df["peso_g"].isna()
    df.loc[falta_peso, "peso_g"] = df.loc[falta_peso, "tipo"].map(mediana_tipo).fillna(global_med)
    df.loc[falta_peso, "tags"] = df.loc[falta_peso, "tags"].apply(lambda t: t + ["peso-estimado"])
    df["peso_g"] = df["peso_g"].round().astype(int)

    # 7. Imágenes, EAN, handle
    df["imagenes"] = df["Image URL"].fillna("").apply(lambda s: [u.strip() for u in str(s).split("|") if u.strip()])
    df["ean"] = df["EAN (old)"].apply(lambda v: "" if pd.isna(v) else str(v).split(".")[0])
    df["handle"] = df["Title"].apply(slug)
    dh = df["handle"].duplicated(keep=False)
    df.loc[dh, "handle"] = df.loc[dh, "handle"] + "-" + df.loc[dh, "SKU"].str.lower().str.replace(r"[^a-z0-9]+", "-", regex=True)
    assert not df["handle"].duplicated().any()

    # 8. Salida
    cols = ["id", "SKU", "ean", "handle", "Title", "vendor", "tipo", "categoria_principal",
            "categorias_lista", "marcas_lista", "tags", "descripcion_corta", "descripcion_html",
            "peso_g", "imagenes"]
    out = df[cols].rename(columns={"Title": "titulo", "SKU": "sku"})
    out["precio"] = None          # se rellena en precios_*.py
    out["precio_origen"] = ""     # icom-pvp | falcon | pihernz | manual

    csv = out.copy()
    for c in ["categorias_lista", "marcas_lista", "tags", "imagenes"]:
        csv[c] = csv[c].apply(lambda l: "|".join(l))
    csv.to_csv(OUT / "catalogo_maestro.csv", index=False, encoding="utf-8-sig")
    out.to_json(OUT / "catalogo_maestro.json", orient="records", force_ascii=False, indent=1)

    informe = f"""# Informe de limpieza del catálogo

- Filas en el Excel: {n0}
- Eliminadas: {n_test} de prueba, {n_desc} solo descatalogados, {len(eliminar) - n_test} duplicados fusionados
- **Productos en el catálogo maestro: {len(out)}**
- SKUs generados para packs: {int(sin_sku.sum())}
- SKUs renombrados por duplicado: {sum(1 for v in SKU_OVERRIDES.values() if v)}
- Sin imagen: {int((out['imagenes'].str.len() == 0).sum())}
- Sin marca (vendor vacío): {int((out['vendor'] == '').sum())}
- Sin descripción: {int((out['descripcion_html'] == '').sum())}
- Descripciones con restos de 'pihernz': {int(restos)}
- Peso estimado por categoría: {int(falta_peso.sum())}
- Categorías huérfanas remapeadas ({n_remap} productos): {"; ".join(f"{k} -> {v}" for k, v in sorted(remapeo.items())) or "ninguna"}
- Tipos (nivel 1): {out['tipo'].nunique()} — tags cat: distintos: {len({t for ts in out['tags'] for t in ts if t.startswith('cat:')})}
- Marcas (vendor) distintas: {out['vendor'].nunique()}
"""
    (OUT / "informe_limpieza.md").write_text(informe, encoding="utf-8")
    print(informe)


if __name__ == "__main__":
    main()
