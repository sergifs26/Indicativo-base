"""
scripts/procesar_logo.py — genera las variantes del logo de Indicativo Base a partir del original.

Entrada: imagen-corporativa/logo-original.jpg (tinta gris oscura sobre fondo crema con textura).
Salida en imagen-corporativa/:
  logo-blanco.png       logo completo en blanco, fondo transparente (cabecera y pie negros)
  logo-oscuro.png       logo completo en gris oscuro, fondo transparente (fondos claros)
  icono-montana.png     solo la montaña, gris oscuro, cuadrado 512 px, transparente
  favicon.png           montaña blanca sobre cuadrado negro, 512 px (pestaña del navegador)

La transparencia sale de la luminosidad: lo más claro que FONDO_L es fondo (alpha 0), lo más
oscuro que TINTA_L es tinta (alpha 255) y los bordes suavizados quedan en medio, sin dientes.
Uso: python scripts/procesar_logo.py
"""
from pathlib import Path

from PIL import Image, ImageChops, ImageFilter

RAIZ = Path(__file__).resolve().parents[1]
DIR = RAIZ / "imagen-corporativa"
FONDO_L, TINTA_L = 238, 60          # el fondo medido va de 245 a 254; la tinta ronda 49
OSCURO = (43, 46, 48)               # gris del logo original
ANCHO_LOGO = 1400                   # px de las versiones completas (Shopify las reescala)


def alfa(im: Image.Image) -> Image.Image:
    lum = im.convert("L")
    a = lum.point(lambda v: 0 if v >= FONDO_L else 255 if v <= TINTA_L
                  else round(255 * (FONDO_L - v) / (FONDO_L - TINTA_L)))
    # El papel texturizado deja motas oscuras sueltas: una apertura morfológica (erosión +
    # dilatación) conserva solo las formas grandes, y el alpha se limita a su entorno.
    formas = a.point(lambda v: 255 if v > 100 else 0).filter(ImageFilter.MinFilter(7)).filter(ImageFilter.MaxFilter(15))
    return ImageChops.darker(a, formas)


def coloreado(a: Image.Image, color) -> Image.Image:
    out = Image.new("RGBA", a.size, color + (0,))
    out.putalpha(a)
    return out


def recortar(a: Image.Image, margen: int = 0) -> Image.Image:
    x0, y0, x1, y1 = a.getbbox()
    return a.crop((max(0, x0 - margen), max(0, y0 - margen), min(a.width, x1 + margen), min(a.height, y1 + margen)))


def separar_montana(a: Image.Image) -> Image.Image:
    """La montaña es el primer bloque de columnas con tinta; el texto empieza tras un hueco vacío."""
    x0, y0, x1, y1 = a.getbbox()
    columnas = [any(a.getpixel((x, y)) > 40 for y in range(y0, y1, 2)) for x in range(x0, x1)]
    fin = x0
    for i, hay in enumerate(columnas):
        if hay:
            fin = x0 + i
        elif fin > x0 and i - (fin - x0) > 40:     # 40 px seguidos sin tinta = hueco montaña/texto
            break
    return recortar(a.crop((x0, y0, fin + 1, y1)))


def cuadrado(img: Image.Image, lado: int, fondo=(0, 0, 0, 0), ocupacion: float = 0.8) -> Image.Image:
    esc = ocupacion * lado / max(img.size)
    peq = img.resize((round(img.width * esc), round(img.height * esc)), Image.LANCZOS)
    lienzo = Image.new("RGBA", (lado, lado), fondo)
    lienzo.alpha_composite(peq, ((lado - peq.width) // 2, (lado - peq.height) // 2))
    return lienzo


def main() -> None:
    original = Image.open(DIR / "logo-original.jpg").convert("RGB")
    a = recortar(alfa(original), margen=8)
    esc = ANCHO_LOGO / a.width
    a_logo = a.resize((ANCHO_LOGO, round(a.height * esc)), Image.LANCZOS)
    coloreado(a_logo, (255, 255, 255)).save(DIR / "logo-blanco.png", optimize=True)
    coloreado(a_logo, OSCURO).save(DIR / "logo-oscuro.png", optimize=True)

    m = separar_montana(a)
    cuadrado(coloreado(m, OSCURO), 512).save(DIR / "icono-montana.png", optimize=True)
    cuadrado(coloreado(m, (255, 255, 255)), 512, fondo=(0, 0, 0, 255), ocupacion=0.86).save(DIR / "favicon.png", optimize=True)

    for f in ("logo-blanco.png", "logo-oscuro.png", "icono-montana.png", "favicon.png"):
        im = Image.open(DIR / f)
        print(f"{f:20} {im.size[0]}x{im.size[1]}  {(DIR / f).stat().st_size // 1024} KB")


if __name__ == "__main__":
    main()
