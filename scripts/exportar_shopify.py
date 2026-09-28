"""
Fase 0.3 — CSV de importación para Shopify

Entrada: data/catalogo_maestro.json, data/precios_icom_final.csv, data/icom_nuevos.csv
Salida:  data/shopify/productos_NN.csv  (formato oficial de importación, < 15 MB cada uno)
         data/shopify/colecciones.csv   (una colección automática por tag cat:/marca:)
         data/shopify/menu.json         (árbol de 3 niveles para el menú principal)
         data/shopify/informe_export.md

Reglas:
  - Precio = PVP con IVA (Shopify se configura con impuestos incluidos en el precio).
  - Precio real si existe (lista Icom). Si no y USAR_PROVISIONALES = True, precio inventado
    (scripts/precios_provisionales.py) con tag `precio-provisional`.
  - Productos que sigan sin precio: precio 0, tag `sin-precio` y estado ESTADO_SIN_PRECIO.
  - Inventario sin seguimiento (todo comprable) hasta tener datos de stock.
  - Imágenes: Shopify las descarga desde las URLs de pihernz.com al importar.
"""
from __future__ import annotations

import csv
import json
import re
from collections import OrderedDict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
OUT = DATA / "shopify"
OUT.mkdir(exist_ok=True)

USAR_PROVISIONALES = True        # precios inventados hasta tener tarifas reales (petición 28/09/2026)
ESTADO_SIN_PRECIO = "draft"      # "active" si se opta por publicarlos con "Consultar precio"
MAX_BYTES = 14 * 1024 * 1024     # margen bajo el límite de 15 MB de Shopify

COLUMNAS = [
    "Handle", "Title", "Body (HTML)", "Vendor", "Product Category", "Type", "Tags", "Published",
    "Option1 Name", "Option1 Value", "Variant SKU", "Variant Grams", "Variant Inventory Tracker",
    "Variant Inventory Qty", "Variant Inventory Policy", "Variant Fulfillment Service",
    "Variant Price", "Variant Compare At Price", "Variant Requires Shipping", "Variant Taxable",
    "Variant Barcode", "Image Src", "Image Position", "Image Alt Text", "Gift Card",
    "SEO Title", "SEO Description", "Status",
]

# Categoría del Excel para los productos Icom nuevos, por patrón de modelo (primera que encaje).
CATEGORIA_ICOM_NUEVOS = [
    (r"^IC-PW2$", "Accesorios Emisoras>Amplificadores Lineales"),
    (r"^(IC-7760|IC-7610|IC-7300|IC-9700|IC-905|IC-705|IC-7100|IC-718|RC-7760)", "Emisoras>Transceptores HF"),
    (r"^(ID-5100E|IC-2730E)", "Emisoras>Transceptores HF"),
    (r"^(ID-52E|ID-50E|IC-T10)", "Walkies>Doble Banda Radioaficionado"),
    (r"^ID-R", "Emisoras"),
    (r"^IC-R8600", "Receptores y scanners"),
    (r"^IC-R(6|15)", "Receptores y scanners"),
    (r"^(SM-|HM-219|HM-151|HM-198|HM-154|HM-207|HM-209|HM-249)", "Accesorios Emisoras>Micrófonos>Comercial o Radioaficionado"),
    (r"^(HM-153|HM-166|HS-|SP-27|SP-40)", "Accesorios Walkies>Microauriculares"),
    (r"^(HM-183|HM-186|HM-243|HM-158|HM-159|HM-168|HM-222)", "Accesorios Walkies>Microaltavoces"),
    (r"^SP-", "Accesorios Emisoras>Altavoces"),
    (r"^BP-", "Accesorios Walkies>Baterías"),
    (r"^BC-214N", "Accesorios Walkies>Cargadores>Cargadores múltiples"),
    (r"^(BC-|AD-55NS|AD-149H)", "Accesorios Walkies>Cargadores"),
    (r"^(CP-|OPC-254L)", "Accesorios Walkies>Cables"),
    (r"^(OPC-478UD|OPC-2218LU|OPC-1529R|OPC-2350LU|OPC-2417|OPC-2418|OPC-2480)", "Accesorios Walkies>Cables>Cables de programación"),
    (r"^(AH-730|AH-705|AL-705)", "Accesorios de antenas>Otros"),
    (r"^(AH-|FA-S270C)", "Antenas"),
    (r"^AD-92SMA", "Accesorios de antenas>Adaptadores"),
    (r"^(MB-127|MB-133)", "Accesorios Walkies>Clips"),
    (r"^(MB-|MBA-|MBF-)", "Accesorios Emisoras>Soportes"),
    (r"^(LC-193|LC-202|LC-203|LC-G1004)", "Accesorios Walkies>Fundas Walkies"),
    (r"^OPC-", "Accesorios Emisoras>Cables"),
]
FALLBACK = "Accesorios Emisoras>Otros"


def slug(texto: str) -> str:
    t = str(texto).lower()
    for a, b in (("á", "a"), ("é", "e"), ("í", "i"), ("ó", "o"), ("ú", "u"), ("ñ", "n"), ("ü", "u")):
        t = t.replace(a, b)
    return re.sub(r"[^a-z0-9]+", "-", t).strip("-")[:80]


def tags_de(rutas: list[str], marcas: list[str]) -> list[str]:
    t: list[str] = []
    for r in rutas:
        partes = [p.strip() for p in r.split(">")]
        for k in range(1, len(partes) + 1):
            tag = "cat:" + ">".join(partes[:k])
            if tag not in t:
                t.append(tag)
    t += ["marca:" + m for m in marcas]
    return t


def cargar() -> list[dict]:
    cat = json.loads((DATA / "catalogo_maestro.json").read_text(encoding="utf-8"))
    por_sku = {p["sku"]: p for p in cat}
    categorias_existentes = {c for p in cat for r in p["categorias_lista"] for c in
                             [">".join(r.split(">")[:k]) for k in range(1, r.count(">") + 2)]}

    with (DATA / "precios_icom_final.csv").open(encoding="utf-8-sig") as f:
        for r in csv.DictReader(f):
            if r["sku_excel"] and r["pvp"]:
                p = por_sku[r["sku_excel"]]
                p["precio"] = float(r["pvp"])
                p["precio_origen"] = "icom-pvp"

    handles = {p["handle"] for p in cat}
    avisos = []
    with (DATA / "icom_nuevos.csv").open(encoding="utf-8-sig") as f:
        for r in csv.DictReader(f):
            modelo = r["modelo"]
            ruta = next((c for pat, c in CATEGORIA_ICOM_NUEVOS if re.match(pat, modelo)), FALLBACK)
            if ruta not in categorias_existentes:
                avisos.append(f"{modelo}: categoría '{ruta}' no existe en el Excel, se usa '{FALLBACK}'")
                ruta = FALLBACK
            h = slug("icom-" + modelo)
            while h in handles:
                h += "-1"
            handles.add(h)
            cat.append({
                "id": None, "sku": modelo.replace(" ", "-"), "ean": "", "handle": h,
                "titulo": f"Icom {modelo} {r['descripcion']}".strip(),
                "vendor": "Icom", "tipo": ruta.split(">")[0], "categoria_principal": ruta,
                "categorias_lista": [ruta], "marcas_lista": ["Icom"],
                "tags": tags_de([ruta], ["Icom"]) + ["icom-nuevo"],
                "descripcion_corta": r["descripcion"],
                "descripcion_html": f"<p>{r['descripcion']}.</p><p>Producto original Icom. Ficha ampliada y fotos pendientes.</p>",
                "peso_g": 500, "imagenes": [],
                "precio": float(r["pvp"]), "precio_origen": "icom-pvp",
            })
    for a in avisos:
        print("  aviso:", a)
    return cat


def filas_producto(p: dict) -> list[dict]:
    precio = p.get("precio")
    tags = list(p["tags"])
    if not precio:
        tags.append("sin-precio")
    estado = "active" if precio else ESTADO_SIN_PRECIO
    base = {c: "" for c in COLUMNAS}
    base.update({
        "Handle": p["handle"], "Title": p["titulo"], "Body (HTML)": p["descripcion_html"],
        "Vendor": p["vendor"], "Type": p["tipo"], "Tags": ", ".join(tags),
        "Published": "TRUE" if estado == "active" else "FALSE",
        "Option1 Name": "Title", "Option1 Value": "Default Title",
        "Variant SKU": p["sku"], "Variant Grams": int(p["peso_g"]),
        "Variant Inventory Tracker": "", "Variant Inventory Qty": "",
        "Variant Inventory Policy": "deny", "Variant Fulfillment Service": "manual",
        "Variant Price": f"{precio:.2f}" if precio else "0.00", "Variant Compare At Price": "",
        "Variant Requires Shipping": "TRUE", "Variant Taxable": "TRUE",
        "Variant Barcode": p["ean"], "Gift Card": "FALSE",
        "SEO Title": p["titulo"][:70], "SEO Description": (p["descripcion_corta"] or p["titulo"])[:320],
        "Status": estado,
    })
    imgs = p["imagenes"]
    filas = []
    if imgs:
        base.update({"Image Src": imgs[0], "Image Position": 1, "Image Alt Text": p["titulo"]})
    filas.append(base)
    for i, url in enumerate(imgs[1:], 2):
        extra = {c: "" for c in COLUMNAS}
        extra.update({"Handle": p["handle"], "Image Src": url, "Image Position": i, "Image Alt Text": p["titulo"]})
        filas.append(extra)
    return filas


def escribir_csvs(productos: list[dict]) -> list[Path]:
    for f in OUT.glob("productos_*.csv"):
        f.unlink()
    archivos, n, buf, tam = [], 1, [], 0

    def volcar():
        nonlocal n, buf, tam
        path = OUT / f"productos_{n:02d}.csv"
        with path.open("w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=COLUMNAS)
            w.writeheader()
            w.writerows(buf)
        archivos.append(path)
        n, buf, tam = n + 1, [], 0

    for p in productos:
        filas = filas_producto(p)
        peso = sum(len(str(v)) for r in filas for v in r.values()) + 40 * len(filas)
        if buf and tam + peso > MAX_BYTES:
            volcar()
        buf += filas
        tam += peso
    if buf:
        volcar()
    return archivos


def colecciones_y_menu(productos: list[dict]) -> None:
    cuenta: dict[str, int] = {}
    for p in productos:
        for t in set(p["tags"]):
            if t.startswith(("cat:", "marca:")):
                cuenta[t] = cuenta.get(t, 0) + 1
    with (OUT / "colecciones.csv").open("w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(["titulo", "handle", "tag", "productos"])
        for t, c in sorted(cuenta.items()):
            nombre = t.split(":", 1)[1]
            titulo = nombre.split(">")[-1] if t.startswith("cat:") else nombre
            w.writerow([titulo, slug(nombre), t, c])

    arbol: "OrderedDict[str, dict]" = OrderedDict()
    for t, c in sorted(cuenta.items()):
        if not t.startswith("cat:"):
            continue
        nodo = arbol
        for parte in t[4:].split(">"):
            nodo = nodo.setdefault(parte, OrderedDict())
    (OUT / "menu.json").write_text(json.dumps(arbol, ensure_ascii=False, indent=1), encoding="utf-8")


def main() -> None:
    productos = cargar()
    reales = sum(1 for p in productos if p.get("precio"))
    provisionales = 0
    if USAR_PROVISIONALES:
        from precios_provisionales import asignar
        provisionales = asignar(productos)
    archivos = escribir_csvs(productos)
    colecciones_y_menu(productos)
    con_precio = sum(1 for p in productos if p.get("precio"))
    nuevos = sum(1 for p in productos if "icom-nuevo" in p["tags"])
    imgs = sum(len(p["imagenes"]) for p in productos)
    informe = (
        f"# Export Shopify\n\n- Productos: {len(productos)} ({nuevos} Icom nuevos)\n"
        f"- Precio real (lista Icom): {reales} | precio provisional inventado: {provisionales}\n"
        f"- Con precio: {con_precio} | sin precio ({ESTADO_SIN_PRECIO}): {len(productos) - con_precio}\n"
        f"- Imágenes referenciadas: {imgs}\n- Archivos: "
        + ", ".join(f"{a.name} ({a.stat().st_size / 1e6:.1f} MB)" for a in archivos) + "\n"
    )
    (OUT / "informe_export.md").write_text(informe, encoding="utf-8")
    print(informe)


if __name__ == "__main__":
    main()
