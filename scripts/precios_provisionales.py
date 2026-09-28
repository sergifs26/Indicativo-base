"""
Precios PROVISIONALES (inventados) para arrancar la tienda mientras llegan las tarifas reales.

- Solo se aplican a productos sin precio real (los de la lista Icom se respetan).
- Cada producto recibe el tag `precio-provisional` y precio_origen = "provisional", para poder
  localizarlos y sustituirlos en bloque cuando lleguen Falcon / Pihernz.
- Deterministas: el mismo SKU da siempre el mismo precio (hash del SKU), así que re-ejecutar
  el pipeline no cambia los precios.
- Método: rango de PVP (con IVA) por categoría, posición dentro del rango según hash + peso
  relativo dentro de su categoría, multiplicador por marca y ajustes por palabras clave.

Uso directo (para revisar): python scripts/precios_provisionales.py
  -> data/precios_provisionales.csv
"""
from __future__ import annotations

import csv
import hashlib
import json
import math
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"

# Rango PVP con IVA (€) por prefijo de categoría. Gana el prefijo más largo que encaje.
RANGOS: dict[str, tuple[float, float]] = {
    # Walkies
    "Walkies": (40, 250),
    "Walkies>PMR-446 Uso libre OCIO": (25, 90),
    "Walkies>PMR-446 Uso Libre PROFESIONAL": (60, 220),
    "Walkies>dPMR-446 Uso libre": (90, 250),
    "Walkies>DMR": (90, 450),
    "Walkies>VHF o UHF profesional": (90, 450),
    "Walkies>Doble Banda Radioaficionado": (40, 350),
    "Walkies>CB": (70, 200),
    "Walkies>Walkies Marina": (90, 300),
    "Walkies>Aérea": (180, 450),
    "Walkies>PoC-LTE": (120, 450),
    "Dynascan": (30, 200),
    # Emisoras
    "Emisoras": (120, 500),
    "Emisoras>Emisoras CB": (90, 350),
    "Emisoras>10 M": (150, 350),
    "Emisoras>Doble Banda Radioaficionado": (180, 550),
    "Emisoras>VHF o UHF radioaficionado": (150, 400),
    "Emisoras>VHF o UHF profesional": (200, 600),
    "Emisoras>Emisoras marina": (180, 700),
    "Emisoras>Transceptores HF": (700, 3500),
    "Radios CB": (90, 250),
    # Accesorios walkies
    "Accesorios Walkies": (8, 40),
    "Accesorios Walkies>Baterías": (15, 70),
    "Accesorios Walkies>Cargadores": (12, 60),
    "Accesorios Walkies>Cargadores>Cargadores múltiples": (60, 250),
    "Accesorios Walkies>Cables": (8, 35),
    "Accesorios Walkies>Cables>Cables de programación": (15, 45),
    "Accesorios Walkies>Cajas portapilas": (8, 25),
    "Accesorios Walkies>Clips": (4, 15),
    "Accesorios Walkies>Eliminadores de batería": (15, 45),
    "Accesorios Walkies>Fundas Walkies": (10, 40),
    "Accesorios Walkies>Maletas": (40, 150),
    "Accesorios Walkies>Microaltavoces": (25, 90),
    "Accesorios Walkies>Microauriculares": (12, 80),
    "Accesorios Walkies>Microauriculares>Laringofonos": (60, 180),
    "Accesorios Walkies>Microauriculares>Diadema": (40, 120),
    # Accesorios emisoras
    "Accesorios Emisoras": (8, 60),
    "Accesorios Emisoras>Altavoces": (15, 80),
    "Accesorios Emisoras>Amplificadores Lineales": (150, 900),
    "Accesorios Emisoras>Cables": (6, 30),
    "Accesorios Emisoras>Conectores/Adaptadores": (3, 15),
    "Accesorios Emisoras>Medidores ROE y potencia": (30, 250),
    "Accesorios Emisoras>Micrófonos": (15, 90),
    "Accesorios Emisoras>Micrófonos>CB": (15, 70),
    "Accesorios Emisoras>Micrófonos>Accesorios": (5, 25),
    "Accesorios Emisoras>Recambios Super Star 3900 antigua": (3, 20),
    "Accesorios Emisoras>Reductores/elevadores tensión": (20, 80),
    "Accesorios Emisoras>Soportes": (8, 40),
    # Antenas
    "Antenas": (20, 150),
    "Antenas>Antenas CB": (20, 120),
    "Antenas>Antenas GSM,3G-UMTS,4G-LTE, 5G": (25, 120),
    "Antenas>Antenas HF/Dipolos": (60, 350),
    "Antenas>Antenas Marina": (40, 180),
    "Antenas>Antenas Móvil": (25, 110),
    "Antenas>Antenas TV": (15, 50),
    "Antenas>Antenas Walkies": (8, 35),
    "Antenas>Diamond Antenas": (30, 250),
    "Antenas>Diamond Antenas>Balun": (30, 90),
    "Antenas Base": (50, 300),
    "Jopix": (20, 120),
    # Accesorios de antenas
    "Accesorios de antenas": (10, 60),
    "Accesorios de antenas>Adaptadores": (3, 15),
    "Accesorios de antenas>Bases": (10, 45),
    "Accesorios de antenas>Cables": (8, 60),
    "Accesorios de antenas>Conectores": (2, 10),
    "Accesorios de antenas>Conmutadores": (20, 90),
    "Accesorios de antenas>Duplexores": (25, 90),
    "Accesorios de antenas>Rotores": (120, 450),
    "Accesorios de antenas>Soportes": (10, 60),
    "Accesorios de antenas>Trípodes": (30, 80),
    # Alimentación
    "Alimentación": (10, 60),
    "Alimentación>Arrancadores baterías": (60, 150),
    "Alimentación>Baterías externas": (25, 70),
    "Alimentación>Cargadores solares": (30, 120),
    "Alimentación>Fuentes de alimentación": (45, 300),
    "Alimentación>Inversores": (40, 150),
    "Alimentación>Pilas y baterías": (3, 25),
    "Alimentación>Tomas de corriente": (8, 35),
    # Receptores
    "Receptores y scanners": (40, 200),
    "Receptores y scanners>AOR": (400, 2500),
    "Receptores y scanners>Accesorios receptores": (8, 50),
    "Receptores y scanners>Altavoz con BLUETOOTH": (20, 80),
    "Receptores y scanners>Escáners Radio": (90, 450),
    "Receptores y scanners>Radio Portátil": (20, 90),
    "Receptores y scanners>Radio Reloj Digital": (20, 60),
    "Receptores y scanners>Radio con Bluetooth": (30, 150),
    "Receptores y scanners>Radio con DAB+": (40, 180),
    "Receptores y scanners>Radio con Radios con Internet/WiFi": (90, 250),
    "Receptores y scanners>Radio de Bolsillo": (15, 60),
    "Receptores y scanners>Radio de Trabajo": (60, 200),
    "Receptores y scanners>Receptor de Radio clásico": (60, 150),
    "Receptores y scanners>Receptores Radio multibanda": (50, 250),
    # Telefonía
    "Telefonía y conectividad": (20, 120),
    "Telefonía y conectividad>Accesorios": (8, 50),
    "Telefonía y conectividad>Adaptadores Bluetooth": (20, 60),
    "Telefonía y conectividad>Amplificadores telefonía móvil": (150, 600),
    "Telefonía y conectividad>Audio-Video conferencia": (80, 400),
    "Telefonía y conectividad>Auriculares con cable": (20, 80),
    "Telefonía y conectividad>Auriculares inalámbricos": (60, 250),
    "Telefonía y conectividad>Modems, Routers y acceso a Internet": (60, 250),
    "Telefonía y conectividad>Teléfonos Satélite": (600, 1500),
    "Telefonía y conectividad>Teléfonos Todoterreno": (180, 600),
    "Telefonía y conectividad>Teléfonos inalámbricos": (30, 120),
    "Telefonía y conectividad>Teléfonos sobremesa": (25, 120),
    "Telefonía y conectividad>Terminales móviles": (150, 500),
    # Outdoor y otros
    "Outdoor": (30, 200),
    "Outdoor>Binoculares": (60, 350),
    "Outdoor>Cámaras Outdoor": (50, 250),
    "Outdoor>Detectores de metales": (80, 400),
    "Outdoor>GPS-GNSS": (150, 700),
    "Outdoor>GPS-GNSS>Accesorios GPS-GNSS": (15, 60),
    "Outdoor>Intercomunicadores": (60, 300),
    "Outdoor>Linternas": (10, 80),
    "Outdoor>Radio Outdoor": (30, 120),
    "Outdoor>Tablets todoterreno": (200, 500),
    "Medición": (20, 150),
    "Medición>Estaciones metereológicas": (30, 250),
    "Medición>Termostatos": (20, 80),
    "Office": (30, 200),
    "Office>Tabletas Firmas": (80, 400),
    "Automóvil": (20, 150),
    "PACKS": (80, 500),
    "Bases": (20, 150),
    "VARIOS": (10, 80),
    "OUTLET (Oportunidades)": (15, 150),
    "Cables": (8, 40),
    "Descatalogados": (10, 80),
}
RANGO_DEFECTO = (15, 90)

MARCAS: dict[str, float] = {
    "Motorola": 1.40, "Icom": 1.35, "Kenwood": 1.30, "Yaesu": 1.30, "Hytera": 1.30,
    "Garmin": 1.30, "Alinco": 1.10, "Diamond Antenna": 1.10, "AOR": 1.10, "Uniden": 1.05,
    "Midland": 1.00, "Dynascan": 0.95, "Sangean": 1.00, "Avair": 0.90, "Nissei": 0.90,
    "Jetfon": 0.85, "PC": 0.85, "PNI": 0.80, "Varta": 0.90,
}

PAREJA_RE = re.compile(r"\bpareja\b|\btwin\b|\b2\s*(x\s*)?walkies?\b|\bdos walkies\b|\(2\)", re.I)
UNIDADES_RE = re.compile(r"^(\d{1,2})\s|\b(?:pack|kit)\s*(?:de\s*)?(\d{1,2})\s*x?\b", re.I)
COLOR_RE = re.compile(r"\([^)]*\)|\b(blanc[oa]|negr[oa]|gris|roj[oa]|azul|verde|amarill[oa]|naranja|rosa|camuflaje)\b", re.I)


def clave_modelo(titulo: str) -> str:
    """Título sin colores ni paréntesis: variantes de color del mismo modelo comparten precio."""
    return re.sub(r"\s+", " ", COLOR_RE.sub(" ", titulo.lower())).strip()
FUENTE_RE = re.compile(r"\bfuente\s+(de\s+)?alimentaci", re.I)
TIPOS_WALKIE = ("Walkies", "Dynascan", "PACKS", "Ofertas")
PACK_RE = re.compile(r"\bpack\b|\bkit\b|\+", re.I)
METRO_RE = re.compile(r"por metros?\b", re.I)
ROLLO_RE = re.compile(r"\b(rollo|bobina)\b", re.I)


def _hash01(texto: str) -> float:
    return int(hashlib.sha1(texto.encode("utf-8")).hexdigest()[:8], 16) / 0xFFFFFFFF


def _rango(ruta: str) -> tuple[float, float]:
    mejor = None
    for pref, r in RANGOS.items():
        if ruta == pref or ruta.startswith(pref + ">"):
            if mejor is None or len(pref) > len(mejor[0]):
                mejor = (pref, r)
    return mejor[1] if mejor else RANGO_DEFECTO


def redondear(p: float) -> float:
    """Precio 'de tienda': 4,95 · 24,90 · 149,90 · 1.299,00"""
    if p < 10:
        return max(1.95, round(p) - 0.05)
    if p < 100:
        return math.floor(p) + 0.90
    if p < 1000:
        return math.ceil(p / 10) * 10 - 0.10
    return math.ceil(p / 50) * 50 - 1.0


def asignar(productos: list[dict]) -> int:
    """Rellena precio a los productos que no lo tienen. Devuelve cuántos ha rellenado."""
    # percentil de peso dentro de cada categoría principal
    por_cat: dict[str, list[float]] = {}
    for p in productos:
        por_cat.setdefault(p["categoria_principal"], []).append(float(p["peso_g"] or 0))
    for v in por_cat.values():
        v.sort()

    n = 0
    for p in productos:
        if p.get("precio"):
            continue
        titulo = p["titulo"]
        lo, hi = _rango(p["categoria_principal"])
        if FUENTE_RE.search(titulo):
            lo, hi = RANGOS["Alimentación>Fuentes de alimentación"]
        pesos = por_cat[p["categoria_principal"]]
        wpct = (sum(1 for w in pesos if w < float(p["peso_g"] or 0)) / max(1, len(pesos) - 1)) if len(pesos) > 1 else 0.5
        m = UNIDADES_RE.search(titulo)
        unidades = int(m.group(1) or m.group(2)) if m else 0
        es_walkie = p["tipo"] in TIPOS_WALKIE or "walkie" in titulo.lower()
        if unidades >= 2 and p["tipo"] == "PACKS":
            lo, hi = RANGOS["Walkies"]            # el pack se calcula como N unidades sueltas
        clave = clave_modelo(titulo)
        pos = 0.8 * _hash01(clave) + 0.2 * wpct
        precio = lo * (hi / lo) ** pos            # escala logarítmica: más productos baratos que caros

        if METRO_RE.search(titulo):
            precio = 1.5 + 4.5 * _hash01(p["sku"] + "m")
        elif ROLLO_RE.search(titulo):
            precio = 60 + 190 * _hash01(p["sku"] + "r")
        else:
            precio *= MARCAS.get(p["vendor"], 1.0)
            precio = min(precio, hi * 1.4)
            if es_walkie and 2 <= unidades <= 20:
                precio *= unidades * 0.85          # pack de N walkies: ~15 % de descuento por unidad
            elif es_walkie and PAREJA_RE.search(titulo):
                precio *= 1.7
            elif PACK_RE.search(titulo) and "pack" in p["tags"]:
                precio *= 1.25

        p["precio"] = round(redondear(precio), 2)
        p["precio_origen"] = "provisional"
        if "precio-provisional" not in p["tags"]:
            p["tags"] = list(p["tags"]) + ["precio-provisional"]
        n += 1
    return n


def main() -> None:
    cat = json.loads((DATA / "catalogo_maestro.json").read_text(encoding="utf-8"))
    asignar(cat)
    with (DATA / "precios_provisionales.csv").open("w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f, delimiter=";")
        w.writerow(["sku", "titulo", "marca", "categoria", "peso_g", "precio_provisional"])
        for p in sorted(cat, key=lambda x: (x["categoria_principal"], x["precio"])):
            w.writerow([p["sku"], p["titulo"], p["vendor"], p["categoria_principal"], p["peso_g"],
                        f"{p['precio']:.2f}".replace(".", ",")])
    print(f"{len(cat)} precios provisionales -> data/precios_provisionales.csv")


if __name__ == "__main__":
    main()
