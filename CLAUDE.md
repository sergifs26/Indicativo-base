# Indicativo Base — repo de operaciones

Tienda Shopify de radiocomunicación (walkies, emisoras, antenas, accesorios, receptores) del
Grupo Intertorrent. Tienda **`indicativo-base.myshopify.com`**: es una **tienda de DESARROLLO**
(plan "Basic App Development") → sirve de tienda de pruebas; no cobra y no se puede convertir en
la tienda real. Al lanzar se creará la definitiva con plan de pago y se re-desplegará todo por script.

GitHub: **`sergifs26/Indicativo-base`**, un solo repo con dos historias independientes:
rama `main` = este repo de operaciones · ramas `production` (tema publicado) y `staging`
(vista previa) = el tema, que en local está en la carpeta hermana `../indicativo-base-theme`.
**Nunca mergear `main` con `production`/`staging`**: no comparten historia ni ficheros.
La metodología completa está en `Agents-IA/FORMA_DE_TRABAJO.md`: **léela antes de tocar nada**.

## ⚠️ Reglas que ya nos han costado algo (leer siempre)

1. **Los precios son PROVISIONALES (inventados)** salvo los 159 de la lista Icom. Llevan el tag
   `precio-provisional`. La tienda no puede abrirse al público con ellos.
2. **`menuUpdate` reemplaza el árbol entero.** Nunca escribir menús a mano: el menú se define en
   `scripts/menu_shopify.py` y se aplica con `scripts/aplicar_menu.mjs` (dry-run, luego `--apply`). Antes de cualquier cambio de menú, leer los
   3 niveles (`items{ items{ items{ title } } }`).
3. **Tema: git es la fuente de verdad.** `git pull` antes de editar, commit, push. Ficheros de
   escritura exclusiva (uno a la vez): `config/settings_data.json`, `sections/header-group.json`,
   `sections/footer-group.json`, `templates/index.json`.
4. **Nunca `git reset --hard` ni force-push** sin mirar qué hay en remoto.
5. Los ficheros de proveedor (Excel de Pihernz, tarifas PDF) **no entran en git**: viven en la
   carpeta padre `../`.

## Cómo llegar a la Admin API

| Vía | Para qué | Limitaciones |
|---|---|---|
| Conector MCP de Shopify (claude.ai) | Lecturas y mutaciones sueltas; menús; colecciones | **Bloquea `bulkOperationRunMutation`** y la escritura en el tema publicado. El token caduca: reautorizar en claude.ai → Conectores |
| CLI `shopify store execute` (`scripts/admin.mjs`) | Scripts del repo | Requiere `shopify store auth` una vez por máquina (ver `scripts/README.md`) |
| CLI `shopify store bulk execute` (`scripts/bulk_cli.mjs`) | **Escrituras masivas** (importar/actualizar miles de productos) | Igual que la anterior |
| CLI `shopify theme pull/push` | Temas | Usa la sesión de la cuenta; ya funciona en esta máquina |

Al lanzar operaciones por la CLI, **leer la salida entera**: los errores pueden salir arriba y
el final parecer correcto.

## Scripts (dry-run por defecto, `--apply` para escribir)

| Script | Qué hace |
|---|---|
| `limpiar_catalogo.py` | Excel de Pihernz → `data/catalogo_maestro.json` (limpieza, SKUs, tags, pesos) |
| `precios_icom.py` | Lista PVP Icom → precios reales; fuente de verdad `data/precios_icom_revisado.csv` |
| `precios_provisionales.py` | Precios inventados deterministas por categoría × marca (tag `precio-provisional`) |
| `exportar_shopify.py` | CSV de importación + `colecciones.csv` + `menu.json` en `data/shopify/` |
| `shopify_bulk.py` | JSONL para operaciones masivas (`productos`, `colecciones`, `publicar`, `mapa`, `errores`) |
| `menu_shopify.py` | Define el menú principal y el del pie (variables de `menuUpdate`) |
| `procesar_logo.py` | Variantes del logo (blanco, oscuro, icono, favicon) desde `imagen-corporativa/logo-original.jpg` |
| `subir_fichero.mjs` | Sube una imagen local a Ficheros de la tienda (idempotente por nombre) |
| `aplicar_menu.mjs` | Aplica esos menús: compara en dry-run, y con `--apply` guarda copia y hace `menuUpdate` |
| `admin.mjs` | Cliente Admin API por la CLI (lo importan los demás `.mjs`) |
| `test_conexion.mjs` | `npm run test:shopify`: datos de la tienda y avisos de configuración |
| `bulk_cli.mjs` | Lanza una bulk mutation (`scripts/graphql/*.graphql` + JSONL) |

Cadena de catálogo completa: `npm run catalogo`.

## Datos clave de la tienda de pruebas

- Canal Tienda online: `gid://shopify/Publication/302436352328`
- Ubicaciones: `gid://shopify/Location/112428384584` (Shop location) · `…/112428450120` (My Custom Location, de la demo)
- Menús: principal `gid://shopify/Menu/307524960584` · pie `gid://shopify/Menu/307524993352`
- **Barra de anuncios rotativa** (29/09/2026): envíos a España e internacionales, teléfono, asesoramiento y PMR-446. El teléfono `+34 960 000 000` es **inventado**, pedido así por el usuario: sustituirlo por el real.
- **Logo** (29/09/2026): `imagen-corporativa/` (ver su README). En el tema: logo blanco `logo-indicativo-base-blanco.png` a 220 px en la cabecera negra y favicon `favicon-indicativo-base.png`.
- **Enfoque de la tienda: montañismo** (29/09/2026). Colección `montana` (`gid://shopify/Collection/672921092424`, OR de tags de walkies PMR-446, GPS, linternas, intercomunicadores, radio outdoor, prismáticos, teléfonos satélite, baterías externas, cargadores solares) y primera sección del menú.
- Fotos de la portada (licencia Unsplash, uso comercial libre): `photo-1643903096045-07741be1f245.jpg` (Mike Markov) y `photo-1563442162585-fa1426255ea9.jpg` (Giacomo Berardi), en Ficheros de la tienda.
- Colecciones: 237 automáticas por tag, ids en `data/shopify/colecciones_ids.json` (no versionado: regenerar con `shopify_bulk.py mapa` o consultando la API)
- Productos: 2.618 cargados y publicados (29/09/2026) por `bulk_cli.mjs`; 2.459 con `precio-provisional`; 251 sin foto (107 del Excel + 144 Icom nuevos). Las 10.403 imágenes, en estado READY.
- Temas: **`Indicativo Base` publicado `190088544584`** (rama `production`, subido por CLI) · `Indicativo Base (staging)` `190088151368` (vista previa, rama `staging`) · `test-data` `190048174408` (demo original, respaldo) · Horizon `190048108872` · debut-vintage `190048141640` · Tinker `190048305480`. Cuando se conecte la GitHub Integration aparecerán dos temas nuevos enlazados a las ramas: publicar el de `production` y borrar entonces los subidos por CLI.
- Precios siempre **PVP con IVA** (la tienda tiene `taxesIncluded: true`). Inventario sin seguimiento hasta tener stock.

## Commits

Conventional Commits en español con ámbito: `feat(catalogo): …`, `fix(precios): …`,
`docs(agents-ia): …`, `chore(scripts): …`. Rama `main` lineal en este repo.
