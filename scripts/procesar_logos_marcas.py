"""
Logos de marcas para el carrusel de la portada → imagen-corporativa/logos-marcas/<marca>.png

Para cada fichero de origen (PNG, JPG, WebP o SVG):
  - SVG: se rasteriza con Edge sin ventana y fondo transparente (no hay cairosvg en esta máquina);
  - fondo blanco liso (logos en JPG): se vuelve transparente con un borde suave;
  - se recorta el margen vacío y se escala a 160 px de alto (el carrusel lo pinta a 40 px: 4x
    para pantallas retina), sin pasar de 900 px de ancho.

Uso:  python scripts/procesar_logos_marcas.py <carpeta_origen> [<carpeta_origen> …]
      (el nombre del fichero, sin extensión, es el de la marca: icom.png → logos-marcas/icom.png)
"""
from __future__ import annotations

import re
import subprocess
import sys
import tempfile
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
SALIDA = ROOT / "imagen-corporativa" / "logos-marcas"
EDGE = Path(r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe")
ALTO = 160
ANCHO_MAX = 900


def svg_a_png(svg: Path) -> Image.Image:
    texto = svg.read_text(encoding="utf-8", errors="ignore")
    vb = re.search(r'viewBox="\s*[-\d.]+[ ,]+[-\d.]+[ ,]+([\d.]+)[ ,]+([\d.]+)', texto)
    if vb:
        w, h = float(vb.group(1)), float(vb.group(2))
    else:
        mw = re.search(r'\bwidth="([\d.]+)', texto); mh = re.search(r'\bheight="([\d.]+)', texto)
        w, h = (float(mw.group(1)), float(mh.group(1))) if mw and mh else (4.0, 1.0)
    alto = 400
    ancho = max(50, min(3000, round(alto * w / h)))
    with tempfile.TemporaryDirectory() as tmp:
        html = Path(tmp) / "logo.html"
        html.write_text(
            f'<!doctype html><html><body style="margin:0;background:transparent">'
            f'<img src="{svg.resolve().as_uri()}" style="display:block;width:{ancho}px;height:{alto}px"></body></html>',
            encoding="utf-8")
        png = Path(tmp) / "logo.png"
        subprocess.run([str(EDGE), "--headless=new", "--disable-gpu", "--no-first-run", f"--user-data-dir={tmp}\\perfil",
                        "--allow-file-access-from-files", "--hide-scrollbars", "--default-background-color=00000000",
                        f"--window-size={ancho},{alto}", f"--screenshot={png}", html.as_uri()],
                       check=True, timeout=60, capture_output=True)
        return Image.open(png).convert("RGBA").copy()


def fondo_blanco_a_transparente(im: Image.Image) -> Image.Image:
    """Solo si la imagen no trae transparencia y sus bordes son blancos."""
    im = im.convert("RGBA")
    w, h = im.size
    borde = [im.getpixel((x, 0)) for x in range(w)] + [im.getpixel((x, h - 1)) for x in range(w)]
    if sum(1 for r, g, b, a in borde if min(r, g, b) > 235) < 0.9 * len(borde):
        return im
    px = im.load()
    for y in range(h):
        for x in range(w):
            r, g, b, a = px[x, y]
            claro = min(r, g, b)
            if claro > 245:
                px[x, y] = (r, g, b, 0)
            elif claro > 200:
                px[x, y] = (r, g, b, int(a * (245 - claro) / 45))
    return im


def procesar(origen: Path) -> Path:
    im = svg_a_png(origen) if origen.suffix.lower() == ".svg" else Image.open(origen)
    if im.mode == "P":  # PNG con paleta: su transparencia se pierde si se pasa directo a RGB (Sangean)
        im = im.convert("RGBA")
    if im.mode not in ("RGBA", "LA") or (im.mode == "RGBA" and im.getextrema()[3][0] == 255):
        im = fondo_blanco_a_transparente(im.convert("RGB"))
    im = im.convert("RGBA")
    caja = im.getchannel("A").point(lambda a: 255 if a > 12 else 0).getbbox()
    if caja:
        im = im.crop(caja)
    escala = min(ALTO / im.height, ANCHO_MAX / im.width)
    im = im.resize((max(1, round(im.width * escala)), max(1, round(im.height * escala))), Image.LANCZOS)
    SALIDA.mkdir(parents=True, exist_ok=True)
    destino = SALIDA / f"{origen.stem}.png"
    im.save(destino, optimize=True)
    return destino


if __name__ == "__main__":
    for carpeta in sys.argv[1:]:
        for f in sorted(Path(carpeta).iterdir()):
            if f.suffix.lower() in (".png", ".jpg", ".jpeg", ".webp", ".svg"):
                d = procesar(f)
                print(f"{f.name:28} → {d.name} {Image.open(d).size}")
