# indicativo-base-theme

Tema de la tienda **Indicativo Base** (`indicativo-base.myshopify.com`, tienda de desarrollo).
Base: "Generated Data Theme" 1.0.0 de Shopify, de la familia **Dawn** (secciones estándar:
image-banner, rich-text, multicolumn, featured-collection, collection-list, image-with-text…).
Ramas: **`production`** = tema publicado · **`staging`** = vista previa.

> GitHub: `sergifs26/Indicativo-base`, ramas `production` y `staging`. La rama `main` de ese
> mismo repo es el repo de operaciones: historia independiente, **nunca se mergea con estas**.

**El usuario quiere conservar el estilo de este tema** (cabecera y pie en negro, fondo claro
`#fafaf9`, acento `#45c0b6`, botones con radio 2) y sustituir todo el contenido demo
(«Generated test data», snowboard, cera de esquí, enlaces a shopify.dev, © Shopify).

## Flujo obligatorio

1. **`git pull` SIEMPRE antes de editar**: el remoto recibe commits de `shopify[bot]` con lo que
   se cambia en el admin.
2. Editar en `staging` → commit (Conventional Commits en español: `feat(portada): …`) → push.
   Revisar en el tema de vista previa → merge a `production`.
3. Si el push se rechaza: `git pull --rebase`. **Nunca `reset --hard` ni force-push.**
4. Ficheros de escritura exclusiva (uno a la vez): `config/settings_data.json`,
   `sections/header-group.json`, `sections/footer-group.json`, `templates/index.json`.
5. Estado (13/10/2026): **el tema publicado es «Indicativo Base (staging)» `190088151368`** (lo
   publicó el usuario desde el admin entre el 08/10 y el 13/10); el antiguo «Indicativo Base»
   `190088544584` queda sin publicar, con el diseño anterior; demo original `test-data`
   `190048174408` como respaldo. Consecuencias: la rama `staging` es lo que está en producción y
   `production` (git) va por detrás; **ya no hay tema de vista previa**: un `theme push` a
   `190088151368` va directo a la tienda y pide `--allow-live`. Antes de subir, comprobar deriva
   (cambios hechos en el editor) con `theme pull` de los JSON y comparación con git.
   Al conectar la GitHub Integration, publicar el tema enlazado a `production`.
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
- `git push` a veces no sube nada, sin dar error visible: **comprobar siempre con
  `git ls-remote origin production staging`**. Causa (05/10/2026): en el Credential Manager de
  Windows hay dos cuentas de GitHub (`sergifs26` e `intertorrentshopify-design`) y Git abría una
  ventana para elegir cuenta y se quedaba esperando. Arreglo en los dos clones (tema y
  operaciones): `git config --local credential.https://github.com.username sergifs26`. Si vuelve a
  pasar: `GIT_TERMINAL_PROMPT=0 GCM_INTERACTIVE=never git push …` lo dice sin colgarse.

- **Portada «La clave» (23/10/2026, documento del cliente «La clave de IndicativoBase.doc»)**: la
  portada pasa de «tienda» a «comunidad con tienda». Orden: banner manifiesto (`hero`, disposición
  `manifiesto`, segunda línea del titular en acento, sin tarjetas) → marcas (Icom y Yaesu primero) →
  `sintonizador` (dial «Sintoniza tu afición»: estaciones ordenadas por frecuencia, aguja con `:has()`
  generado en la sección, iconos en `snippets/icono-aficion.liquid`) → `pilares` (4 ideas clave) →
  «Una tienda de aficionados» → «Lo que más valoramos» (colección manual `lo-que-mas-valoramos`) →
  «Lo más fácil para empezar» → comunidad → **`ayuda` y `envio` con `"disabled": true`** (donaciones
  y 5 días hábiles: no activarlas hasta que el cliente confirme que ya funcionan) → preguntas →
  cierre. Página «Comparte tu estación»: `templates/page.comparte.json` + `sections/comparte-estacion.liquid`
  (formulario de contacto de Shopify; no admite archivos, las fotos se piden por email). Foto del
  banner: silueta con un Yaesu FT-817 en el Monte Cucco (`entorno-hero-yaesu-ft817.jpg`, disposición «manifiesto»; CC BY-SA 2.0 de iz1ksw; la del FT-817 en la roca se probó y no gustó). La disposición «Foto a la izquierda» pone en móvil y tablet la foto arriba y el texto debajo:
  **lleva crédito obligatorio** (ajustes `credito`/`credito_url` del banner); ver
  `Indicativo-base/imagen-corporativa/fotos/CREDITOS.md`.
- **Carrusel de marcas (20/10/2026)**: sección `marcas-carrusel` (clave `marcas`, justo debajo del banner): logos en bucle continuo, en gris y a color al pasar el ratón, enlazados a `marca-<x>`. La altura de cada logo se ajusta a su proporción en la propia sección. Logos y licencias: `Indicativo-base/imagen-corporativa/logos-marcas/`.
- **Banner principal (07/10/2026)**: sección propia `hero-indicativo` (clave `hero`): foto con un walkie a la vista, texto a la derecha, botones a walkies/emisoras y 4 tarjetas de cristal por categoría con nº de modelos en vivo. Estilos «Banner principal» en `assets/indicativo-base.css`.
- **Portada estilo The North Face (04/10/2026, a petición del usuario)**: una sola foto a pantalla
  completa (sección `hero`; hasta el 07/10 era un image-banner con texto abajo centrado) y cabecera
  con menú horizontal (`logo_position: middle-left`, `menu_type_desktop: mega`) **transparente
  sobre la foto solo en la portada**: `body.ib-portada` + script en `layout/theme.liquid` que pone
  `html.ib-cabecera-solida` al bajar; el banner sube con `margin-top: -var(--header-height)`. El
  carrusel de 5 entornos se probó y se descartó (el usuario prefiere una foto).
- **Antena de recambio (05/10/2026)**: `snippets/producto-antena-recambio.liquid` (casilla con foto encima de «Añadir al carrito», lee `product.metafields.custom.antenas_recambio`). **`assets/product-form.js` está modificado**: con la casilla `ib_antena` marcada manda walkie y antena juntos (`items` en JSON) y copia `key`/`id` del walkie a la respuesta para la ventana/panel del carrito. Si se actualiza el tema, conservar ese bloque.
- **Liquid glass (05/10/2026)**: todos los botones (`.button` y «Comprar ya») son cápsulas de cristal (CSS «Liquid glass» al final de `assets/indicativo-base.css`; sustituye el borde/sombra de ::before/::after del tema). Variantes: principal oscuro, secundario blanco, y cristal claro dentro de `.banner`, `.color-inverse`, `.color-accent-*` y las tarjetas de «Tres entornos». Los ajustes de botones del editor (radio, borde, sombra) ya no tienen efecto.
- **Tres entornos (05/10/2026)**: sección `destacados-entorno` en la portada (clave `tres_entornos`): 3 fotos verticales a sangre con tarjeta del producto. Productos elegidos por el ranking de popularidad de Pihernz (ver `PROYECTO_INDICATIVO_BASE.md`); rótulo «Imprescindible en…», nunca «el más vendido» sin ventas propias. Se cambian desde el editor de temas.
- **Tipografía (05/10/2026)**: **Inter**, al estilo de The North Face (que usa Helvetica Neue/Now, de pago). Alojada en el tema (`assets/inter-latin-var.woff2`, OFL 1.1) y fijada por CSS al principio de `assets/indicativo-base.css`: **cambiar la fuente en el editor de temas no tiene efecto**. Los ajustes decían «Helvetica», que Shopify no descarga (en Windows salía Arial).
- **Panel direccional (23/10/2026, adaptado del «Directional Menu» de 21st.dev, autor hyperiux)**:
  en escritorio con ratón, `assets/indicativo-menu.js` pone un único panel blanco flotante
  (`.ib-dm__fondo`, creado por el script) bajo la cabecera; al pasar de un apartado a otro el
  contenido entra deslizándose desde ese lado y el panel cambia de alto (Web Animations API, sin
  React ni GSAP). Los `<details>` del tema siguen igual (teclado y móvil sin cambios). Estilos
  «Panel direccional» en `assets/indicativo-base.css`, solo con `html.ib-dm`. Ojo: `base.css`
  oculta los `div` vacíos (`div:empty`), por eso el fondo lleva `display: block`.
- **21st.dev**: MCP configurado en `Pagina indicativobase/.mcp.json` (clave en la variable de entorno
  `API_KEY_21ST`, cuenta gratuita: 2 descargas de código al día). Sus componentes son React +
  Tailwind: se adaptan a Liquid/CSS/JS a mano. La API REST (`/api/v1/components/search?scope=public`,
  `/components/install/{autor}/{slug}`) funciona aunque el buscador del MCP falle.
- **Desplegables (05/10/2026)**: estilo The North Face (CSS «Desplegables» en `assets/indicativo-base.css`) y apertura al pasar el cursor con `assets/indicativo-menu.js` (solo escritorio con ratón; el clic de ratón no los cierra; el teclado sigue como en el tema).
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
