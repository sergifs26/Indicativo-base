"""
Giro outdoor, fase 1 — etiquetas de entorno, nivel y licencia.

Lee data/shopify/bulk/productos.jsonl (lo mismo que hay en la tienda) y calcula por producto:
  entorno:<montana|nautica|nieve|camping|caza-pesca>   0..n por producto
  nivel:<empezar|experto>                              como mucho uno
  licencia:<no|si|marina>                              solo equipos que transmiten

Reglas, por este orden:
  1. Tabla de categorías (cat:…) → entornos, nivel y licencia.
  2. Señales del título y la descripción: grado IP, «sumergible», «flotante», marina, caza…
  3. data/entornos_excepciones.csv (handle;añadir;quitar;motivo), editada a mano: manda sobre todo.

Licencias (normativa española verificada el 04/10/2026, fuentes en PROYECTO_INDICATIVO_BASE.md):
  PMR-446 / dPMR446 y CB-27 → uso libre, sin licencia.
  VHF/UHF profesional, DMR, radioaficionado → licencia.
  VHF marina → «marina»: certificado de operador y, según la zona de navegación, licencia de
  estación de barco. El título manda sobre la categoría: un «UHF profesional» metido en la
  categoría PMR del proveedor sale como licencia:si.

Uso:
  python scripts/entornos.py                # dry-run: data/entornos_informe.md + data/entornos_tags.json
  python scripts/entornos.py --jsonl        # + data/shopify/bulk/tags_add.jsonl (y tags_remove.jsonl
                                            #   frente a lo último aplicado) para scripts/bulk_cli.mjs
  python scripts/entornos.py --aplicado     # tras aplicar sin errores: guarda la foto de lo aplicado

Aplicar:  node scripts/bulk_cli.mjs scripts/graphql/tags_add.graphql data/shopify/bulk/tags_add.jsonl --apply
"""
from __future__ import annotations

import csv
import json
import re
import shutil
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
BULK = DATA / "shopify" / "bulk"
PRODUCTOS = BULK / "productos.jsonl"
EXCEPCIONES = DATA / "entornos_excepciones.csv"
TAGS = DATA / "entornos_tags.json"
APLICADO = DATA / "entornos_tags_aplicado.json"
INFORME = DATA / "entornos_informe.md"
PREFIJOS = ("entorno:", "nivel:", "licencia:")

ENTORNOS = {
    "montana": "Montaña",
    "nautica": "Náutica",
    "nieve": "Nieve",
    "camping": "Camping y familia",
    "caza-pesca": "Caza y pesca",
}

# --- categorías (sin el prefijo cat:) -------------------------------------------------------
PMR_OCIO = "Walkies>PMR-446 Uso libre OCIO"
PMR_PRO = "Walkies>PMR-446 Uso Libre PROFESIONAL"
DPMR = "Walkies>dPMR-446 Uso libre"
WALKIES_OUTDOOR = "Outdoor>Walkies Outdoor"
MARINA = ("Walkies>Walkies Marina", "Emisoras>Emisoras marina")
VHF_PRO = ("Walkies>VHF o UHF profesional", "Emisoras>VHF o UHF profesional", "Walkies>DMR")
CB = ("Walkies>CB", "Emisoras>Emisoras CB", "Radios CB")
RADIOAFICION = (
    "Walkies>Doble Banda Radioaficionado", "Emisoras>Doble Banda Radioaficionado",
    "Emisoras>VHF o UHF radioaficionado", "Emisoras>Transceptores HF", "Emisoras>10 M",
)
EXPERTO = RADIOAFICION + (
    "Walkies>DMR", "Antenas>Antenas HF/Dipolos", "Antenas Base>Base Multibanda",
    "Accesorios Emisoras>Medidores ROE y potencia", "Accesorios Emisoras>Amplificadores Lineales",
    "Accesorios de antenas>Rotores", "Receptores y scanners>Escáners Radio",
    "Receptores y scanners>AOR",
)
# Categorías que no aportan entorno por sí mismas (cajones del proveedor)
TRANSMISORES = (PMR_OCIO, PMR_PRO, DPMR, WALKIES_OUTDOOR) + MARINA + VHF_PRO + CB + RADIOAFICION

# --- señales de texto -----------------------------------------------------------------------
PMR_RE = re.compile(r"d?PMR[- ]?446|\b446\b", re.I)
PRO_RE = re.compile(r"\b(VHF|UHF|DMR|NXDN)\b", re.I)
MARINA_RE = re.compile(r"marin[ao]|n[aá]utic|\bbarco|embarcaci", re.I)
IP_RE = re.compile(r"\bIP[- ]?([0-6X])([0-9])\b", re.I)
SUMERGIBLE_RE = re.compile(r"sumergible|flotante|flotabilidad|flota (en|si|sobre)", re.I)
CAZA_RE = re.compile(r"\bcaza\b|cazador|batida|monter[ií]a|hunting|hunter|\bpesca\b|pescador|"
                     r"camo\b|camuflaje|mimetic", re.I)
NIEVE_RE = re.compile(r"esqu[ií]|\bski\b|\bnieve\b|\bsnow", re.I)
FRONTAL_RE = re.compile(r"frontal", re.I)
TRABAJO_RE = re.compile(r"trabajo|work flex (stadium|telescope)|stadium|telescope|BL30R|bater[ií]a", re.I)
LAMPARA_CAMPING_RE = re.compile(r"l[aá]mpara de camping", re.I)
POWERBANK_RE = re.compile(r"power ?bank|bater[ií]a externa", re.I)
EMERGENCIA_RE = re.compile(r"emergencia|survivor|dinamo|dynamo|manivela|solar", re.I)
CEECOACH_RE = re.compile(r"ceecoach", re.I)
PAREJA_RE = re.compile(r"pareja|dual pack|\bd[uú]o\b|pack 2 walkies", re.I)


def agua(texto: str) -> int:
    """Protección frente al agua: segundo dígito IP más alto citado; «sumergible» o «flotante» = 7."""
    nivel = max((int(m.group(2)) for m in IP_RE.finditer(texto)), default=0)
    return max(nivel, 7) if SUMERGIBLE_RE.search(texto) else nivel


def texto_plano(html: str) -> str:
    return re.sub(r"<[^>]+>", " ", html or "")


class Producto:
    def __init__(self, entrada: dict):
        p = entrada["input"]
        self.handle = p["handle"]
        self.titulo = p["title"]
        self.cats = {t[4:] for t in p["tags"] if t.startswith("cat:")}
        self.texto = f'{p["title"]} {texto_plano(p.get("descriptionHtml", ""))}'
        self.tags: dict[str, str] = {}  # tag → motivo (para el informe)

    def en(self, *cats: str) -> bool:
        return any(c in self.cats or any(x.startswith(c + ">") for x in self.cats) for c in cats)

    def pon(self, motivo: str, *tags: str) -> None:
        for t in tags:
            self.tags.setdefault(t, motivo)


def e(*claves: str) -> list[str]:
    return [f"entorno:{c}" for c in claves]


def clasificar(p: Producto) -> None:
    t, txt = p.titulo, p.texto
    es_pmr = p.en(PMR_OCIO, PMR_PRO, DPMR) or (p.en(WALKIES_OUTDOOR, "PACKS") and PMR_RE.search(t))
    es_marina = p.en(*MARINA) or (p.en(WALKIES_OUTDOOR) and MARINA_RE.search(t))
    es_pro = not es_pmr and not es_marina and (p.en(*VHF_PRO) or (p.en(WALKIES_OUTDOOR) and PRO_RE.search(t)))
    # Un título que dice UHF/VHF sin PMR-446 es un equipo profesional aunque el proveedor lo
    # haya puesto en la categoría PMR (p. ej. «Pack 8 Hytera S1 UHF»).
    if es_pmr and PRO_RE.search(t) and not PMR_RE.search(t):
        es_pmr, es_pro = False, True
    # Ocio: la categoría de ocio del proveedor, los PMR de Outdoor no profesionales y las parejas
    # sencillas (no los packs de 6-16 con cargador múltiple, que son para empresas).
    ocio = es_pmr and (p.en(PMR_OCIO) or (p.en(WALKIES_OUTDOOR) and not re.search("profesional", t, re.I))
                       or (PAREJA_RE.search(t) and not re.search("cargador m[uú]ltiple", t, re.I)))
    a = agua(txt)

    # --- licencia (solo lo que transmite) ---
    if es_marina:
        p.pon("walkie/emisora VHF marina", "licencia:marina")
    elif es_pmr:
        p.pon("PMR-446/dPMR446: uso libre", "licencia:no")
    elif p.en(*CB):
        p.pon("CB-27: uso libre", "licencia:no")
    elif es_pro or p.en(*RADIOAFICION):
        p.pon("VHF/UHF profesional, DMR o radioaficionado", "licencia:si")

    # --- walkies ---
    if es_pmr:
        p.pon("walkie PMR-446 de uso libre", *e("montana"))
        if ocio:
            p.pon("walkie PMR de ocio", *e("camping"), "nivel:empezar")
        if a >= 4 or NIEVE_RE.search(txt):
            p.pon(f"walkie PMR resistente al agua (IPx{a})" if a >= 4 else "walkie PMR para nieve", *e("nieve"))
        if a >= 7:
            p.pon(f"walkie PMR sumergible/flotante (IPx{a})", *e("nautica"))
        if a >= 5 or CAZA_RE.search(txt):
            p.pon("walkie PMR robusto (IPx5 o más) o para caza", *e("caza-pesca"))
    if es_marina:
        p.pon("radio VHF marina", *e("nautica"))
    # En caza se usa VHF (mejor alcance en monte); los UHF y DMR compactos son de empresa.
    if es_pro and p.en("Walkies", WALKIES_OUTDOOR, "PACKS") and not p.en("Walkies>DMR") and (
            re.search(r"\bVHF\b", t, re.I) or CAZA_RE.search(txt)):
        p.pon("walkie VHF profesional (con licencia)", *e("caza-pesca"))

    # --- náutica ---
    if p.en("Antenas>Antenas Marina") or MARINA_RE.search(t):
        p.pon("antena o accesorio marino", *e("nautica"))
    if p.en("Accesorios Walkies>Fundas Walkies") and re.search(r"aquapac|acu[aá]tic|estanc", t, re.I):
        p.pon("funda estanca para walkie", *e("nautica"))

    # --- outdoor ---
    if p.en("Outdoor>GPS-GNSS"):
        p.pon("GPS", *e("montana"))
    if p.en("Telefonía y conectividad>Teléfonos Satélite"):
        p.pon("teléfono satélite", *e("montana", "nautica"))
    if p.en("Outdoor>Binoculares"):
        p.pon("prismáticos", *e("montana", "caza-pesca"))
    if p.en("Outdoor>Intercomunicadores") and CEECOACH_RE.search(t):
        p.pon("intercomunicador Ceecoach (esquí, bici, monta)", *e("nieve", "montana"))
    if p.en("Outdoor>Cámaras Outdoor") and CAZA_RE.search(t):
        p.pon("cámara de caza", *e("caza-pesca"))
    if p.en("Outdoor>Linternas"):
        if POWERBANK_RE.search(t):
            p.pon("batería externa", *e("montana", "camping"))
        elif LAMPARA_CAMPING_RE.search(t):
            p.pon("lámpara de camping", *e("camping"))
        elif FRONTAL_RE.search(t):
            p.pon("linterna frontal", *e("montana", "nieve", "camping", "caza-pesca"))
        elif not TRABAJO_RE.search(t):
            p.pon("linterna de mano", *e("camping", "caza-pesca"))
    if p.en("Outdoor>Radio Outdoor") and not re.search(r"ducha", t, re.I):
        p.pon("radio outdoor/emergencia", *e("camping"))
    if p.en("Receptores y scanners") and not p.en("Outdoor>Radio Outdoor") and EMERGENCIA_RE.search(t):
        p.pon("radio de emergencia/solar", *e("camping"))
    if p.en("Alimentación>Baterías externas", "Alimentación>Cargadores solares"):
        p.pon("batería externa o cargador solar", *e("montana", "camping"))
    if re.search(r"\bcaza\b|hunting", t, re.I) and not p.en("Outdoor>Cámaras Outdoor"):
        p.pon("producto de caza", *e("caza-pesca"))

    # --- nivel experto ---
    if p.en(*EXPERTO) and "nivel:empezar" not in p.tags:
        p.pon("radioafición, HF, DMR o medición", "nivel:experto")


def leer_excepciones() -> dict[str, tuple[list[str], list[str], str]]:
    if not EXCEPCIONES.exists():
        return {}
    out = {}
    with EXCEPCIONES.open(encoding="utf-8-sig", newline="") as f:
        for fila in csv.DictReader(f, delimiter=";"):
            h = (fila.get("handle") or "").strip()
            if h and not h.startswith("#"):
                out[h] = ((fila.get("añadir") or "").split(), (fila.get("quitar") or "").split(),
                          (fila.get("motivo") or "").strip())
    return out


def mapa_ids() -> dict[str, str]:
    """handle → gid a partir de los resultados de la carga masiva (el último manda)."""
    ids: dict[str, str] = {}
    for f in sorted((ROOT / "scripts" / "out").glob("bulk_product_set_*.jsonl")):
        for linea in f.read_text(encoding="utf-8").splitlines():
            for v in (json.loads(linea).get("data") or {}).values():
                prod = (v or {}).get("product")
                if prod and prod.get("id"):
                    ids[prod["handle"]] = prod["id"]
    return ids


def informe(productos: list[Producto], excepciones: dict, sin_handle: list[str]) -> str:
    cuenta = Counter(t for p in productos for t in p.tags)
    con_entorno = sum(1 for p in productos if any(t.startswith("entorno:") for t in p.tags))
    L = [
        "# Informe de entornos (dry-run)", "",
        f"Productos analizados: **{len(productos)}** · con algún entorno: **{con_entorno}** · "
        f"excepciones manuales: **{len(excepciones)}**", "",
        "Nada se ha escrito en la tienda. Revisa los ejemplos; para corregir un producto concreto, "
        "añade una fila a `data/entornos_excepciones.csv` y vuelve a lanzar el script.", "",
        "## Recuento", "", "| Etiqueta | Productos |", "|---|---|",
    ]
    L += [f"| `{t}` | {n} |" for t, n in sorted(cuenta.items())]
    if sin_handle:
        L += ["", f"⚠️ Excepciones con handle que no existe: {', '.join(sin_handle)}"]

    for clave, nombre in ENTORNOS.items():
        tag = f"entorno:{clave}"
        grupo = [p for p in productos if tag in p.tags]
        motivos = Counter(p.tags[tag] for p in grupo)
        L += ["", f"## {nombre} — {len(grupo)} productos", "",
              "Por qué entran: " + " · ".join(f"{m} ({n})" for m, n in motivos.most_common()), ""]
        # 10 ejemplos repartidos entre los motivos
        vistos, ejemplos = Counter(), []
        for p in grupo:
            if vistos[p.tags[tag]] < max(1, 10 // max(1, len(motivos))) and len(ejemplos) < 10:
                vistos[p.tags[tag]] += 1
                ejemplos.append(p)
        for p in grupo:
            if len(ejemplos) >= 10:
                break
            if p not in ejemplos:
                ejemplos.append(p)
        L += [f"- {p.titulo} — _{p.tags[tag]}_" for p in ejemplos]

    for tag, titulo in (("nivel:empezar", "Para empezar"), ("nivel:experto", "Para expertos")):
        grupo = [p for p in productos if tag in p.tags]
        L += ["", f"## {titulo} — {len(grupo)} productos", ""]
        L += [f"- {p.titulo}" for p in grupo[:10]]

    # Casos en los que el título contradice la categoría del proveedor
    corregidos = [p for p in productos if p.tags.get("licencia:si") and p.en(PMR_PRO, PMR_OCIO, DPMR)]
    if corregidos:
        L += ["", "## Licencia corregida por el título", "",
              "Están en una categoría PMR del proveedor, pero el título dice VHF/UHF sin PMR-446:", ""]
        L += [f"- {p.titulo}" for p in corregidos]
    return "\n".join(L) + "\n"


def main() -> None:
    args = set(sys.argv[1:])
    if "--aplicado" in args:
        shutil.copyfile(TAGS, APLICADO)
        print(f"Foto de lo aplicado → {APLICADO}")
        return

    productos = [Producto(json.loads(l)) for l in PRODUCTOS.read_text(encoding="utf-8").splitlines() if l.strip()]
    for p in productos:
        clasificar(p)

    excepciones = leer_excepciones()
    por_handle = {p.handle: p for p in productos}
    sin_handle = [h for h in excepciones if h not in por_handle]
    for h, (anadir, quitar, motivo) in excepciones.items():
        if h in por_handle:
            p = por_handle[h]
            for t in quitar:
                p.tags.pop(t, None)
            p.pon(f"excepción: {motivo or 'manual'}", *anadir)

    tags = {p.handle: sorted(p.tags) for p in productos if p.tags}
    TAGS.write_text(json.dumps(tags, ensure_ascii=False, indent=1), encoding="utf-8")
    INFORME.write_text(informe(productos, excepciones, sin_handle), encoding="utf-8")
    cuenta = Counter(t for ts in tags.values() for t in ts)
    print(f"{len(tags)} productos con etiquetas → {TAGS.name}; informe → {INFORME.name}")
    for t, n in sorted(cuenta.items()):
        print(f"  {t:22} {n}")

    if "--jsonl" in args:
        ids = mapa_ids()
        antes = json.loads(APLICADO.read_text(encoding="utf-8")) if APLICADO.exists() else {}
        anadir, quitar = defaultdict(list), defaultdict(list)
        for h in set(tags) | set(antes):
            nuevos, viejos = set(tags.get(h, [])), set(antes.get(h, []))
            if nuevos - viejos:
                anadir[h] = sorted(nuevos - viejos)
            if viejos - nuevos:
                quitar[h] = sorted(viejos - nuevos)
        faltan = sorted(h for h in set(anadir) | set(quitar) if h not in ids)
        for nombre, cambios in (("tags_add", anadir), ("tags_remove", quitar)):
            ruta = BULK / f"{nombre}.jsonl"
            with ruta.open("w", encoding="utf-8", newline="\n") as f:
                for h, ts in sorted(cambios.items()):
                    if h in ids:
                        f.write(json.dumps({"id": ids[h], "tags": ts}, ensure_ascii=False) + "\n")
            print(f"{nombre}: {sum(1 for h in cambios if h in ids)} productos → {ruta}")
        if faltan:
            print(f"⚠️ {len(faltan)} handles sin id en scripts/out/bulk_product_set_*.jsonl: {faltan[:10]}")


if __name__ == "__main__":
    main()
