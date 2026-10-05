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
# Secciones por tipo de producto. Hasta el 04/10/2026 eran el primer nivel del menú; ahora van
# dentro de «Productos» (ver MENU al final de la lista).
SECCIONES = [
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

_S = {t: (h, hijos) for t, h, hijos in SECCIONES}
_S.update({t: (h, hijos) for t, h, hijos in _S["Accesorios"][1]})  # accesorios walkies/emisoras/antenas
CONTACTO = "gid://shopify/Page/157018980680"


def _grupo(titulo: str, quitar: tuple = ()) -> tuple:
    """Grupo del desplegable al estilo The North Face: «Ver todo» primero y lista recortada.
    Lo que se quita del menú sigue en la colección del «Ver todo». Shopify admite 3 niveles:
    dentro de «Productos» cada sección conserva solo sus hijos."""
    h, hijos = _S[titulo]
    return (titulo, h, [("Ver todo", h, [])] + [(t, hh, []) for t, hh, _ in hijos if t not in quitar])


def _entorno(titulo: str, handle: str, enlaces: list) -> tuple:
    return (titulo, handle, [("Ver todo", handle, [])] + [(t, h, []) for t, h in enlaces])


PMR_OCIO, PMR_PRO = "walkies-pmr-446-uso-libre-ocio", "walkies-pmr-446-uso-libre-profesional"
GPS, LINTERNAS, SATELITE = "outdoor-gps-gnss", "outdoor-linternas", "telefonia-y-conectividad-telefonos-satelite"
BATERIAS, SOLARES = "alimentacion-baterias-externas", "alimentacion-cargadores-solares"

# Menú del giro outdoor (04/10/2026), con desplegables al estilo The North Face (05/10/2026):
# grupos con «Ver todo» + 4-10 enlaces, apilados en 5 columnas por el tema. El entorno manda
# (como su columna «Actividad»); dos caminos, empezar y expertos.
# «Guías» y «Glosario» se añaden a «Empieza aquí» cuando estén publicados.
MENU = [
    ("¿A dónde vas?", None, [
        _entorno("Montaña", "montana", [
            ("Walkies de ocio", PMR_OCIO), ("Walkies profesionales sin licencia", PMR_PRO),
            ("GPS", GPS), ("Linternas y frontales", LINTERNAS), ("Teléfonos satélite", SATELITE),
            ("Baterías externas", BATERIAS)]),
        _entorno("Náutica", "nautica", [
            ("Walkies marinos", "walkies-walkies-marina"), ("Emisoras marinas", "emisoras-emisoras-marina"),
            ("Antenas marinas", "antenas-antenas-marina"), ("Fundas para walkies", "accesorios-walkies-fundas-walkies"),
            ("Teléfonos satélite", SATELITE)]),
        _entorno("Nieve", "nieve", [
            ("Walkies de ocio", PMR_OCIO), ("Intercomunicadores", "outdoor-intercomunicadores"),
            ("Linternas y frontales", LINTERNAS), ("Baterías externas", BATERIAS)]),
        _entorno("Camping y familia", "camping-y-familia", [
            ("Walkies de ocio", PMR_OCIO), ("Linternas y frontales", LINTERNAS),
            ("Radios de emergencia", "outdoor-radio-outdoor"), ("Baterías externas", BATERIAS),
            ("Cargadores solares", SOLARES)]),
        _entorno("Caza y pesca", "caza-y-pesca", [
            ("Walkies profesionales sin licencia", PMR_PRO),
            ("Walkies VHF / UHF profesionales", "walkies-vhf-o-uhf-profesional"),
            ("Prismáticos", "outdoor-binoculares"), ("Cámaras", "outdoor-camaras-outdoor"),
            ("Linternas y frontales", LINTERNAS)]),
    ]),
    ("Empieza aquí", "para-empezar", [
        ("Equipos fáciles", "para-empezar", [
            ("Ver todo", "para-empezar", []),
            ("Walkies sin licencia de ocio", PMR_OCIO, []),
            ("Walkies sin licencia profesionales", PMR_PRO, []),
            ("Packs", "todos-los-packs", []),
        ]),
        ("Te ayudamos", CONTACTO, [
            ("Cuéntanos tu plan", CONTACTO, []),
        ]),
    ]),
    ("Productos", None, [
        _grupo("Walkies", quitar=("Dynascan",)),
        _grupo("Emisoras", quitar=("Radios CB",)),
        _grupo("Antenas", quitar=("TV", "Antenas Diamond", "Jopix")),
        _grupo("Accesorios walkies", quitar=("Eliminadores de batería", "Maletas")),
        _grupo("Accesorios emisoras"),
        _grupo("Accesorios antenas"),
        _grupo("Receptores", quitar=("Radios Internet / WiFi", "Radios de bolsillo", "Accesorios receptores")),
        _grupo("Alimentación", quitar=("Arrancadores de baterías",)),
        _grupo("Telefonía", quitar=("Teléfonos inalámbricos", "Teléfonos de sobremesa", "Módems y routers", "Accesorios")),
        _grupo("Outdoor", quitar=("Detectores de metales", "Estaciones meteorológicas", "Automóvil")),
    ]),
    ("Para expertos", "para-expertos", [
        ("Equipos", "para-expertos", [
            ("Ver todo", "para-expertos", []),
            ("Transceptores HF", "emisoras-transceptores-hf", []),
            ("Emisoras doble banda", "emisoras-doble-banda-radioaficionado", []),
            ("Emisoras VHF / UHF radioaficionado", "emisoras-vhf-o-uhf-radioaficionado", []),
            ("Walkies doble banda", "walkies-doble-banda-radioaficionado", []),
            ("Walkies DMR", "walkies-dmr", []),
        ]),
        ("Antenas y medición", "antenas-antenas-hf-dipolos", [
            ("Antenas HF y dipolos", "antenas-antenas-hf-dipolos", []),
            ("Antenas base multibanda", "antenas-base-base-multibanda", []),
            ("Medidores ROE y potencia", "accesorios-emisoras-medidores-roe-y-potencia", []),
            ("Amplificadores lineales", "accesorios-emisoras-amplificadores-lineales", []),
            ("Rotores", "accesorios-de-antenas-rotores", []),
        ]),
        ("Escucha", "receptores-y-scanners", [
            ("Escáneres", "receptores-y-scanners-escaners-radio", []),
            ("Receptores multibanda", "receptores-y-scanners-receptores-radio-multibanda", []),
            ("AOR", "receptores-y-scanners-aor", []),
        ]),
    ]),
    ("Ofertas", *_S["Ofertas"]),
    ("Marcas", *_S["Marcas"]),
]

PIE = [
    ("Buscar", "SEARCH", "/search"),
    ("Todos los productos", "CATALOG", "/collections/all"),
    ("Contacto", "PAGE", "gid://shopify/Page/157018980680"),
    ("Office", "COLLECTION", "office"),
    ("Medición", "COLLECTION", "medicion"),
    ("Varios", "COLLECTION", "varios"),
    ("Otros productos", "COLLECTION", "bases"),
]


def item(titulo: str, handle: str | None, hijos: list) -> dict:
    d: dict = {"title": titulo}
    if handle and handle.startswith("gid://shopify/Page/"):
        d.update(type="PAGE", resourceId=handle)
    elif handle:
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
        elif tipo == "PAGE":
            pie.append({"title": titulo, "type": tipo, "resourceId": ref})
        else:
            pie.append({"title": titulo, "type": tipo, "url": ref})
    (SHOP / "menu_principal.json").write_text(json.dumps(principal, ensure_ascii=False), encoding="utf-8")
    (SHOP / "menu_pie.json").write_text(json.dumps(pie, ensure_ascii=False), encoding="utf-8")
    n = sum(1 + len(i.get("items", [])) + sum(len(j.get("items", [])) for j in i.get("items", [])) for i in principal)
    print(f"menú principal: {len(principal)} secciones, {n} enlaces | pie: {len(pie)} enlaces")


if __name__ == "__main__":
    main()
