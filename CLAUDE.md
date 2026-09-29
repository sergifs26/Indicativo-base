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

- Tema antiguo de Dawn: los esquemas de color se llaman `background-1`, `background-2`,
  `inverse`, `accent-1`, `accent-2` (no `scheme-1…`). Poner siempre el valor explícito.
- Las imágenes `shopify://shop_images/…` no viajan en un export/import de tema.
- Una plantilla JSON que referencia una sección que aún no existe en el tema se rechaza: subir
  antes el `.liquid`.
- El idioma de los textos de la tienda (botones, carrito) lo marca el **idioma por defecto de
  la tienda**, hoy `en`: cambiarlo a español en Ajustes → Idiomas. Los textos propios del tema
  van en `locales/es.json`.
