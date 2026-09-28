"""
Menú principal y de pie para Shopify a partir de las colecciones creadas.

Genera data/shopify/menu_principal.json y data/shopify/menu_pie.json con las variables de
menuUpdate(id, title, handle, items). Los ids de colección salen de data/shopify/colecciones_ids.json
({handle: gid}).
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SHOP = ROOT / "data" / "shopify"
IDS: dict[str, str] = json.loads((SHOP / "colecciones_ids.json").read_text(encoding="utf-8"))

# (título, handle de colección | None, hijos)
MENU = [
    ("Walkies", "walkies", [
        ("PMR-446 uso libre ocio", "walkies-pmr-446-uso-libre-ocio", []),
        ("PMR-446 uso libre profesional", "walkies-pmr-446-uso-libre-profesional", []),
        ("dPMR-446 uso libre", "walkies-dpmr-446-uso-libre", []),
        ("DMR", "walkies-dmr", []),
        ("VHF / UHF profesional", "walkies-vhf-o-uhf-profesional", []),
        ("Radioaficionado doble banda", "walkies-doble-banda-radioaficionado", []),
        ("CB", "walkies-cb", []),
        ("Marina", "walkies-walkies-marina", []),
        ("Banda aérea", "walkies-aerea", []),
        ("PoC-LTE", "walkies-poc-lte", []),
        ("Dynascan", "dynascan", []),
    ]),
    ("Emisoras", "emisoras", [
        ("Transceptores HF", "emisoras-transceptores-hf", []),
        ("Radioaficionado doble banda", "emisoras-doble-banda-radioaficionado", []),
        ("VHF / UHF radioaficionado", "emisoras-vhf-o-uhf-radioaficionado", []),
        ("VHF / UHF profesional", "emisoras-vhf-o-uhf-profesional", []),
        ("Emisoras CB", "emisoras-emisoras-cb", []),
        ("10 metros", "emisoras-10-m", []),
        ("Marina", "emisoras-emisoras-marina", []),
        ("Radios CB", "radios-cb", []),
    ]),
    ("Antenas", "antenas", [
        ("Antenas base", "antenas-base", [
            ("Doble banda", "antenas-base-base-doble-banda", []),
            ("Monobanda", "antenas-base-base-monobanda", []),
            ("Multibanda", "antenas-base-base-multibanda", []),
            ("Recepción", "antenas-base-base-recepcion", []),
        ]),
        ("Antenas móvil", "antenas-antenas-movil", [
            ("Doble banda", "antenas-antenas-movil-movil-doble-banda", []),
            ("Monobanda", "antenas-antenas-movil-movil-monobanda", []),
            ("Multibanda", "antenas-antenas-movil-movil-multibanda", []),
            ("Tribanda", "antenas-antenas-movil-movil-tribanda", []),
        ]),
        ("Antenas walkies", "antenas-antenas-walkies", []),
        ("Antenas CB", "antenas-antenas-cb", []),
        ("HF y dipolos", "antenas-antenas-hf-dipolos", []),
        ("Marina", "antenas-antenas-marina", []),
        ("GSM / 4G / 5G", "antenas-antenas-gsm-3g-umts-4g-lte-5g", []),
        ("TV", "antenas-antenas-tv", []),
        ("Antenas Diamond", "antenas-diamond-antenas", []),
        ("Jopix", "jopix", []),
    ]),
    ("Accesorios", None, [
        ("Accesorios walkies", "accesorios-walkies", [
            ("Baterías", "accesorios-walkies-baterias", []),
            ("Cargadores", "accesorios-walkies-cargadores", []),
            ("Cargadores múltiples", "accesorios-walkies-cargadores-cargadores-multiples", []),
            ("Microauriculares", "accesorios-walkies-microauriculares", []),
            ("Microaltavoces", "accesorios-walkies-microaltavoces", []),
            ("Fundas", "accesorios-walkies-fundas-walkies", []),
            ("Clips", "accesorios-walkies-clips", []),
            ("Cables de programación", "accesorios-walkies-cables-cables-de-programacion", []),
            ("Eliminadores de batería", "accesorios-walkies-eliminadores-de-bateria", []),
            ("Maletas", "accesorios-walkies-maletas", []),
        ]),
        ("Accesorios emisoras", "accesorios-emisoras", [
            ("Micrófonos", "accesorios-emisoras-microfonos", []),
            ("Altavoces", "accesorios-emisoras-altavoces", []),
            ("Medidores ROE y potencia", "accesorios-emisoras-medidores-roe-y-potencia", []),
            ("Amplificadores lineales", "accesorios-emisoras-amplificadores-lineales", []),
            ("Cables", "accesorios-emisoras-cables", []),
            ("Conectores y adaptadores", "accesorios-emisoras-conectores-adaptadores", []),
            ("Soportes", "accesorios-emisoras-soportes", []),
            ("Reductores de tensión", "accesorios-emisoras-reductores-elevadores-tension", []),
        ]),
        ("Accesorios antenas", "accesorios-de-antenas", [
            ("Cables coaxiales", "accesorios-de-antenas-cables", []),
            ("Conectores", "accesorios-de-antenas-conectores", []),
            ("Adaptadores", "accesorios-de-antenas-adaptadores", []),
            ("Bases de antena", "accesorios-de-antenas-bases", []),
            ("Soportes", "accesorios-de-antenas-soportes", []),
            ("Conmutadores", "accesorios-de-antenas-conmutadores", []),
            ("Duplexores", "accesorios-de-antenas-duplexores", []),
            ("Rotores", "accesorios-de-antenas-rotores", []),
        ]),
    ]),
    ("Receptores", "receptores-y-scanners", [
        ("Escáneres", "receptores-y-scanners-escaners-radio", []),
        ("Receptores multibanda", "receptores-y-scanners-receptores-radio-multibanda", []),
        ("AOR", "receptores-y-scanners-aor", []),
        ("Radios DAB+", "receptores-y-scanners-radio-con-dab", []),
        ("Radios Bluetooth", "receptores-y-scanners-radio-con-bluetooth", []),
        ("Radios portátiles", "receptores-y-scanners-radio-portatil", []),
        ("Radios de bolsillo", "receptores-y-scanners-radio-de-bolsillo", []),
        ("Radios Internet / WiFi", "receptores-y-scanners-radio-con-radios-con-internet-wifi", []),
        ("Accesorios receptores", "receptores-y-scanners-accesorios-receptores", []),
    ]),
    ("Alimentación", "alimentacion", [
        ("Fuentes de alimentación", "alimentacion-fuentes-de-alimentacion", []),
        ("Pilas y baterías", "alimentacion-pilas-y-baterias", []),
        ("Tomas de corriente", "alimentacion-tomas-de-corriente", []),
        ("Inversores", "alimentacion-inversores", []),
        ("Cargadores solares", "alimentacion-cargadores-solares", []),
        ("Arrancadores de baterías", "alimentacion-arrancadores-baterias", []),
        ("Baterías externas", "alimentacion-baterias-externas", []),
    ]),
    ("Telefonía", "telefonia-y-conectividad", [
        ("Teléfonos satélite", "telefonia-y-conectividad-telefonos-satelite", []),
        ("Teléfonos todoterreno", "telefonia-y-conectividad-telefonos-todoterreno", []),
        ("Terminales móviles", "telefonia-y-conectividad-terminales-moviles", []),
        ("Amplificadores de cobertura", "telefonia-y-conectividad-amplificadores-telefonia-movil", []),
        ("Módems y routers", "telefonia-y-conectividad-modems-routers-y-acceso-a-internet", []),
        ("Auriculares inalámbricos", "telefonia-y-conectividad-auriculares-inalambricos", []),
        ("Teléfonos inalámbricos", "telefonia-y-conectividad-telefonos-inalambricos", []),
        ("Teléfonos de sobremesa", "telefonia-y-conectividad-telefonos-sobremesa", []),
        ("Accesorios", "telefonia-y-conectividad-accesorios", []),
    ]),
    ("Outdoor", "outdoor", [
        ("GPS", "outdoor-gps-gnss", []),
        ("Intercomunicadores", "outdoor-intercomunicadores", []),
        ("Linternas", "outdoor-linternas", []),
        ("Binoculares", "outdoor-binoculares", []),
        ("Radio outdoor", "outdoor-radio-outdoor", []),
        ("Cámaras", "outdoor-camaras-outdoor", []),
        ("Detectores de metales", "outdoor-detectores-de-metales", []),
        ("Estaciones meteorológicas", "medicion-estaciones-metereologicas", []),
        ("Automóvil", "automovil", []),
    ]),
    ("Ofertas", "outlet-oportunidades", [
        ("Outlet", "outlet-oportunidades", []),
        ("Ofertas", "ofertas", []),
        ("Packs", "todos-los-packs", []),
        ("Novedades Icom", "novedades-icom", []),
    ]),
    ("Marcas", None, [
        (m, "marca-" + h, []) for m, h in [
            ("Icom", "icom"), ("Yaesu", "yaesu"), ("Kenwood", "kenwood"), ("Motorola", "motorola"),
            ("Hytera", "hytera"), ("Alinco", "alinco"), ("Midland", "midland"), ("Dynascan", "dynascan"),
            ("Anytone", "anytone"), ("Wouxun", "wouxun"), ("President", "president"),
            ("Diamond", "diamond-antenna"), ("Sirio", "sirio"), ("Jetfon", "jetfon"),
            ("Garmin", "garmin"), ("Sangean", "sangean"), ("Uniden", "uniden"), ("AOR", "aor"),
        ]
    ]),
]

PIE = [
    ("Buscar", "SEARCH", "/search"),
    ("Todos los productos", "CATALOG", "/collections/all"),
    ("Office", "COLLECTION", "office"),
    ("Medición", "COLLECTION", "medicion"),
    ("Varios", "COLLECTION", "varios"),
    ("Otros productos", "COLLECTION", "bases"),
]


def item(titulo: str, handle: str | None, hijos: list) -> dict:
    d: dict = {"title": titulo}
    if handle:
        d.update(type="COLLECTION", resourceId=IDS[handle])
    else:
        d.update(type="CATALOG", url="/collections/all")
    if hijos:
        d["items"] = [item(*h) for h in hijos]
    return d


def main() -> None:
    principal = [item(*m) for m in MENU]
    pie = []
    for titulo, tipo, ref in PIE:
        if tipo == "COLLECTION":
            pie.append({"title": titulo, "type": tipo, "resourceId": IDS[ref]})
        else:
            pie.append({"title": titulo, "type": tipo, "url": ref})
    (SHOP / "menu_principal.json").write_text(json.dumps(principal, ensure_ascii=False), encoding="utf-8")
    (SHOP / "menu_pie.json").write_text(json.dumps(pie, ensure_ascii=False), encoding="utf-8")
    n = sum(1 + len(i.get("items", [])) + sum(len(j.get("items", [])) for j in i.get("items", [])) for i in principal)
    print(f"menú principal: {len(principal)} secciones, {n} enlaces | pie: {len(pie)} enlaces")


if __name__ == "__main__":
    main()
