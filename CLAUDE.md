# indicativo-base-theme

Tema de la tienda **Indicativo Base** (`indicativo-base.myshopify.com`, tienda de desarrollo).
Base: "Generated Data Theme" 1.0.0 de Shopify, de la familia **Dawn** (secciones estándar:
image-banner, rich-text, multicolumn, featured-collection, collection-list, image-with-text…).
Ramas: **`production`** = tema publicado · **`staging`** = vista previa.

> GitHub: `sergifs26/Indicativo-base`, ramas `production` y `staging`. La rama `main` de ese
> mismo repo es el repo de operaciones: historia independiente, **nunca se mergea con estas**.

**El usuario quiere conservar el estilo de este tema** (cabecera y pie en negro, fondo claro
`#fafaf9`, acento `#45c0b6`, Helvetica, botones con radio 2) y sustituir todo el contenido demo
(«Generated test data», snowboard, cera de esquí, enlaces a shopify.dev, © Shopify).

## Flujo obligatorio

1. **`git pull` SIEMPRE antes de editar**: el remoto recibe commits de `shopify[bot]` con lo que
   se cambia en el admin.
2. Editar en `staging` → commit (Conventional Commits en español: `feat(portada): …`) → push.
   Revisar en el tema de vista previa → merge a `production`.
3. Si el push se rechaza: `git pull --rebase`. **Nunca `reset --hard` ni force-push.**
4. Ficheros de escritura exclusiva (uno a la vez): `config/settings_data.json`,
   `sections/header-group.json`, `sections/footer-group.json`, `templates/index.json`.
5. Estado (29/09/2026): publicado «Indicativo Base» `190088544584` (subido por CLI desde
   `production`); vista previa «Indicativo Base (staging)» `190088151368`; demo original
   `test-data` `190048174408` como respaldo. Al conectar la GitHub Integration, publicar el tema
   enlazado a `production` y borrar los dos subidos por CLI.
6. Mientras la GitHub Integration no esté conectada, subir a un tema **no publicado** con
   `shopify theme push -s indicativo-base.myshopify.com -t <id> -n -o <fichero>` y publicarlo
   desde el admin. El conector MCP de claude.ai no puede escribir en el tema publicado.

## Gotchas conocidos

- **Idioma**: la tienda tiene el inglés como idioma por defecto (la API no deja cambiarlo), así que
  `locales/en.default.json` contiene **los textos en español** (español de España: «Añadir al
  carrito»…) con las mismas claves que el inglés. Cualquier cambio de texto va en `en.default.json`
  **y** en `es.json`. `<html lang>` sale como `es` mientras el idioma servido sea el de por defecto.
- **Fotos**: todas en marco cuadrado, enteras y sobre blanco — tarjetas por
  `assets/indicativo-base.css` (global) + `image_ratio: square` en las plantillas; galería de la
  ficha por `snippets/product-thumbnail.liquid` (ratio 1 para imágenes).
- Las tiendas de desarrollo muestran una página de contraseña genérica de Shopify (en inglés) que
  el tema no controla: `templates/password.json` solo se verá en la tienda definitiva.
- **Antes de cada commit, `git checkout staging`**: si la sesión se quedó en `production`, el
  commit acaba ahí y `staging` se desalinea (pasó el 29/09; se arregló con un fast-forward).

- **Ficha de producto**: la descripción se pinta en desplegables con
  `snippets/descripcion-desplegable.liquid` (parte por h2/h3/h4; títulos de más de 40 caracteres
  quedan dentro; máximo 6 más el resto agrupado; «Datos del producto» al final). Estilos y scroll
  propio de la columna de información en `assets/indicativo-producto.css`.
- La tienda tiene contraseña y no se puede ver renderizada desde aquí: la lógica Liquid se prueba
  en local con `liquidjs` y descripciones reales antes de publicar (ver `PROYECTO_INDICATIVO_BASE.md`).

- **Barra de anuncios rotativa** (código propio en `sections/announcement-bar.liquid`): con varios
  bloques muestra uno cada vez (ajuste `segundos` de la sección). Al subirla, primero el `.liquid`
  y después `sections/header-group.json`, que usa el ajuste nuevo.
- El teléfono de la barra (`+34 960 000 000`) es **inventado y provisional**: cambiarlo por el real.
- `git push` a veces no sube nada justo después de un `shopify theme push`, sin dar error visible:
  **comprobar siempre con `git ls-remote origin production staging`** y repetir si hace falta.

- **Portada estilo The North Face (04/10/2026, a petición del usuario)**: una sola foto a pantalla
  completa (sección `hero`, image-banner, texto abajo centrado y 2 botones translúcidos) y cabecera
  con menú horizontal (`logo_position: middle-left`, `menu_type_desktop: mega`) **transparente
  sobre la foto solo en la portada**: `body.ib-portada` + script en `layout/theme.liquid` que pone
  `html.ib-cabecera-solida` al bajar; el banner sube con `margin-top: -var(--header-height)`. El
  carrusel de 5 entornos se probó y se descartó (el usuario prefiere una foto).
- **Giro outdoor (04/10/2026)**: mosaico «¿A dónde vas?». El
  mosaico usa la imagen de cada colección a sangre (cover) gracias a la regla
  `[id$="__entornos"]` de `assets/indicativo-base.css`: **si se cambia la clave `entornos` de la
  sección en `index.json`, las fotos vuelven al marco blanco de producto**.
- Ficha: `snippets/producto-entornos.liquid` (chips de entorno, nivel y licencia, leídos de las
  etiquetas `entorno:`/`nivel:`/`licencia:` del repo de operaciones), `snippets/producto-ayuda.liquid`
  (caja «¿Dudas?») y la sección `mas-del-entorno`. Los enlaces a guías solo aparecen cuando el
  artículo existe en el blog `aprende` (`articles['aprende/<handle>']`).

- Tema antiguo de Dawn: los esquemas de color se llaman `background-1`, `background-2`,
  `inverse`, `accent-1`, `accent-2` (no `scheme-1…`). Poner siempre el valor explícito.
- Las imágenes `shopify://shop_images/…` no viajan en un export/import de tema.
- Una plantilla JSON que referencia una sección que aún no existe en el tema se rechaza: subir
  antes el `.liquid`.
- El idioma de los textos de la tienda (botones, carrito) lo marca el **idioma por defecto de
  la tienda**, hoy `en`: cambiarlo a español en Ajustes → Idiomas. Los textos propios del tema
  van en `locales/es.json`.
