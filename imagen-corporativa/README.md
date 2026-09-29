# Imagen corporativa — Indicativo Base

Logo: montaña con nieve + «INDICATIVO BASE» en mayúsculas, tinta gris oscura `#2B2E30`.

| Fichero | Uso | En la tienda (Ficheros) |
|---|---|---|
| `logo-original.jpg` | Original entregado por el usuario (fondo crema texturizado). Fuente de todo lo demás | — |
| `logo-blanco.png` | Cabecera y pie (fondo negro). 1400×295, transparente | `logo-indicativo-base-blanco.png` |
| `logo-oscuro.png` | Fondos claros (checkout, correos, documentos). 1400×295, transparente | `logo-indicativo-base-oscuro.png` |
| `icono-montana.png` | Solo la montaña, gris oscuro, 512×512, transparente | — |
| `favicon.png` | Pestaña del navegador: montaña blanca sobre negro, 512×512 | `favicon-indicativo-base.png` |

Regenerar las variantes: `python scripts/procesar_logo.py`.
Subir a la tienda: `node scripts/subir_fichero.mjs imagen-corporativa/<fichero> <nombre> "alt" --apply`.

En el tema: ajustes `logo` (blanco, `logo_width` 220) y `favicon` de `config/settings_data.json`.
