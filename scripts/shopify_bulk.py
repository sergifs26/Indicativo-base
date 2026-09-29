"""
Archivos JSONL para las importaciones masivas (bulkOperationRunMutation) de la Admin API.

  python scripts/shopify_bulk.py productos
      -> data/shopify/bulk/productos.jsonl       (una línea = variables de productSet)
  python scripts/shopify_bulk.py colecciones
      -> data/shopify/bulk/colecciones.jsonl     (collectionCreate, colecciones automáticas por tag)
  python scripts/shopify_bulk.py publicar <resultado_bulk.jsonl> <publicationId> <salida.jsonl>
      -> variables de publishablePublish para todo id creado en un resultado de bulk
  python scripts/shopify_bulk.py mapa <resultado_bulk.jsonl> <salida.json>
      -> {handle: id} a partir de un resultado de bulk

Mutaciones usadas (validadas contra el esquema; ficheros en scripts/graphql/):
  productSet(identifier: $identifier, input: $input, synchronous: true)
  collectionCreate(input: $input)
  publishablePublish(id: $id, input: $input)

Los JSONL se lanzan con: node scripts/bulk_cli.mjs <mutacion.graphql> <fichero.jsonl> [--apply]
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from urllib.parse import quote

sys.path.insert(0, str(Path(__file__).resolve().parent))
from exportar_shopify import cargar, slug  # noqa: E402
from precios_provisionales import asignar  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
BULK = ROOT / "data" / "shopify" / "bulk"
BULK.mkdir(parents=True, exist_ok=True)

# Categorías que no se publican como colección propia (cajones internos del Excel).
CATS_SIN_COLECCION = {"Descatalogados"}


def url_segura(url: str) -> str:
    """Codifica caracteres no ASCII ("–", "ñ"…) del nombre de archivo: Shopify rechaza la URL
    («La URL del archivo no es válida») si van sin codificar. Lo ya codificado no se toca."""
    return quote(url, safe=":/?&=%#+,;@!$'()*[]~")


def producto_input(p: dict) -> dict:
    precio = p.get("precio") or 0
    variante = {
        "optionValues": [{"optionName": "Title", "name": "Default Title"}],
        "price": f"{precio:.2f}",
        "sku": p["sku"],
        "inventoryPolicy": "DENY",
        "taxable": True,
        "inventoryItem": {
            "tracked": False,
            "requiresShipping": True,
            "measurement": {"weight": {"value": float(p["peso_g"]), "unit": "GRAMS"}},
        },
    }
    if p["ean"]:
        variante["barcode"] = p["ean"]
    entrada = {
        "handle": p["handle"],
        "title": p["titulo"],
        "descriptionHtml": p["descripcion_html"],
        "vendor": p["vendor"] or "Indicativo Base",
        "productType": p["tipo"],
        "tags": p["tags"],
        "status": "ACTIVE" if precio else "DRAFT",
        "seo": {"title": p["titulo"][:70], "description": (p["descripcion_corta"] or p["titulo"])[:320]},
        "productOptions": [{"name": "Title", "values": [{"name": "Default Title"}]}],
        "variants": [variante],
    }
    if p["imagenes"]:
        entrada["files"] = [
            {"originalSource": url_segura(url), "contentType": "IMAGE", "alt": p["titulo"][:500]}
            for url in p["imagenes"]
        ]
    # identifier por handle: si el producto ya existe se actualiza (re-ejecutable sin duplicar)
    return {"identifier": {"handle": p["handle"]}, "input": entrada}


def cmd_productos() -> None:
    productos = cargar()
    asignar(productos)
    out = BULK / "productos.jsonl"
    with out.open("w", encoding="utf-8", newline="\n") as f:
        for p in productos:
            f.write(json.dumps(producto_input(p), ensure_ascii=False) + "\n")
    print(f"{len(productos)} productos -> {out} ({out.stat().st_size / 1e6:.1f} MB)")


def colecciones_def(productos: list[dict]) -> list[dict]:
    cuenta: dict[str, int] = {}
    for p in productos:
        for t in set(p["tags"]):
            if t.startswith(("cat:", "marca:")):
                cuenta[t] = cuenta.get(t, 0) + 1
    cats = [t for t in cuenta if t.startswith("cat:") and t[4:].split(">")[0] not in CATS_SIN_COLECCION]
    ultimos: dict[str, int] = {}
    for t in cats:
        u = t[4:].split(">")[-1]
        ultimos[u] = ultimos.get(u, 0) + 1

    defs = []
    for t in sorted(cats):
        partes = t[4:].split(">")
        titulo = partes[-1]
        if ultimos[titulo] > 1 and len(partes) > 1:
            titulo = f"{titulo} · {partes[-2]}"
        defs.append({"tag": t, "titulo": titulo, "handle": slug(t[4:]), "n": cuenta[t]})
    for t in sorted(x for x in cuenta if x.startswith("marca:")):
        defs.append({"tag": t, "titulo": t[6:], "handle": "marca-" + slug(t[6:]), "n": cuenta[t]})
    # Colecciones de campaña
    for tag, titulo, handle in (("outlet", "Outlet", "outlet"), ("oferta", "Ofertas", "ofertas"),
                                ("pack", "Packs", "packs"), ("icom-nuevo", "Novedades Icom", "novedades-icom")):
        n = sum(1 for p in productos if tag in p["tags"])
        if n:
            defs.append({"tag": tag, "titulo": titulo, "handle": handle, "n": n})
    return defs


def cmd_colecciones() -> None:
    productos = cargar()
    defs = colecciones_def(productos)
    out = BULK / "colecciones.jsonl"
    with out.open("w", encoding="utf-8", newline="\n") as f:
        for d in defs:
            entrada = {
                "title": d["titulo"],
                "handle": d["handle"],
                "sortOrder": "BEST_SELLING",
                "ruleSet": {"appliedDisjunctively": False,
                            "rules": [{"column": "TAG", "relation": "EQUALS", "condition": d["tag"]}]},
            }
            f.write(json.dumps({"input": entrada}, ensure_ascii=False) + "\n")
    (BULK / "colecciones_def.json").write_text(json.dumps(defs, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{len(defs)} colecciones -> {out}")


def _ids(resultado: Path) -> list[tuple[str, str]]:
    pares = []
    for linea in resultado.read_text(encoding="utf-8").splitlines():
        if not linea.strip():
            continue
        d = json.loads(linea)
        data = d.get("data") or {}
        for v in data.values():
            obj = (v or {}).get("product") or (v or {}).get("collection")
            if obj and obj.get("id"):
                pares.append((obj.get("handle", ""), obj["id"]))
    return pares


def cmd_publicar(resultado: str, publicacion: str, salida: str) -> None:
    pares = _ids(Path(resultado))
    with Path(salida).open("w", encoding="utf-8", newline="\n") as f:
        for _, gid in pares:
            f.write(json.dumps({"id": gid, "input": [{"publicationId": publicacion}]}) + "\n")
    print(f"{len(pares)} publicaciones -> {salida}")


def cmd_mapa(resultado: str, salida: str) -> None:
    pares = _ids(Path(resultado))
    Path(salida).write_text(json.dumps(dict(pares), ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{len(pares)} ids -> {salida}")


def errores(resultado: str) -> None:
    n = 0
    for linea in Path(resultado).read_text(encoding="utf-8").splitlines():
        if not linea.strip():
            continue
        d = json.loads(linea)
        errs = d.get("errors") or []
        for v in (d.get("data") or {}).values():
            errs += (v or {}).get("userErrors") or []
        if errs:
            n += 1
            if n <= 25:
                print(d.get("__lineNumber"), json.dumps(errs, ensure_ascii=False)[:300])
    print(f"líneas con error: {n}")


if __name__ == "__main__":
    cmd, *args = sys.argv[1:]
    {"productos": cmd_productos, "colecciones": cmd_colecciones, "publicar": cmd_publicar,
     "mapa": cmd_mapa, "errores": errores}[cmd](*args)
