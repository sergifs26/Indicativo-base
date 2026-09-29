# scripts/ — convenciones

Obligatorias para todo script de este repo (detalle en `Agents-IA/FORMA_DE_TRABAJO.md` §4):

1. **Dry-run por defecto**: escribir de verdad requiere `--apply`.
2. **Idempotente**: re-ejecutar no duplica nada (upsert por handle/SKU).
3. **Backup antes de borrar** en `scripts/out/` con fecha UTC (carpeta fuera de git).
4. **Resultados y logs** de operaciones largas en `scripts/out/`, para poder reanudar.
5. **Docstring de cabecera**: qué hace, cómo se usa y qué credencial necesita.
6. **Nada de secretos en el código**: `.env` (fuera de git) o la sesión de la CLI.
7. **Siempre el alias `.myshopify.com`**, nunca el dominio propio.
8. Python 3 para el pipeline de catálogo; Node `.mjs` sin dependencias para la Admin API.

## Acceso a la Admin API (una vez por máquina)

```bash
shopify store auth --store indicativo-base.myshopify.com --scopes read_products,write_products,read_publications,write_publications,read_online_store_navigation,write_online_store_navigation,read_content,write_content,read_themes,write_themes,read_files,write_files,read_inventory,write_inventory,read_locales
npm run test:shopify
```

## Importar o actualizar el catálogo completo

```bash
npm run catalogo                                            # regenera data/
python scripts/shopify_bulk.py productos                    # → data/shopify/bulk/productos.jsonl
node scripts/bulk_cli.mjs scripts/graphql/product_set.graphql data/shopify/bulk/productos.jsonl          # dry-run
node scripts/bulk_cli.mjs scripts/graphql/product_set.graphql data/shopify/bulk/productos.jsonl --apply
python scripts/shopify_bulk.py publicar scripts/out/bulk_product_set_<fecha>.jsonl gid://shopify/Publication/302436352328 data/shopify/bulk/publicar.jsonl
node scripts/bulk_cli.mjs scripts/graphql/publicar.graphql data/shopify/bulk/publicar.jsonl --apply
```

`productSet` va por handle: re-ejecutarlo actualiza, no duplica. Así se cargarán los precios
reales cuando lleguen (Falcon, Pihernz).

Alternativa sin CLI: importar `data/shopify/productos_01.csv` desde el admin (Productos → Importar).

## Scripts

| Script | Propósito |
|---|---|
| `limpiar_catalogo.py` | Excel de Pihernz → catálogo maestro limpio |
| `precios_icom.py` | Precios reales de la lista Icom (tabla revisada a mano) |
| `precios_provisionales.py` | Precios inventados, deterministas, con tag `precio-provisional` |
| `exportar_shopify.py` | CSV de importación, colecciones y árbol del menú |
| `shopify_bulk.py` | JSONL para bulk mutations y utilidades sobre sus resultados |
| `menu_shopify.py` | Menú principal y del pie (fuente de verdad de la navegación) |
| `admin.mjs` | Cliente Admin API por la CLI de Shopify |
| `test_conexion.mjs` | Prueba de conexión y avisos de configuración |
| `bulk_cli.mjs` | Operaciones masivas por la CLI |
| `graphql/` | Mutaciones listas para `bulk_cli.mjs` |
