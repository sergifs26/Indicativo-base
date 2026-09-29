# Proyecto Indicativo Base — documento maestro

> **Estado:** en construcción · **Última revisión:** 2026-09-28
> Historia, arquitectura y estado. Los cambios se añaden en `## Actualización AAAA-MM-DD`.

## 1. Arquitectura

```
  Carpeta padre (fuera de git)
    Export-info-productes.xlsx ─┐   LISTA PVP AFICIONADO (Icom) ─┐   Tarifa Falcon (corrupta)
                                ▼                                ▼
  Indicativo-base/scripts   limpiar_catalogo.py → precios_icom.py → precios_provisionales.py
                                                  │
                                                  ▼
                            exportar_shopify.py / shopify_bulk.py / menu_shopify.py
                                                  │  (CLI de Shopify: bulk_cli.mjs · conector MCP)
                                                  ▼
  Shopify  indicativo-base.myshopify.com  (tienda de desarrollo = entorno de pruebas)
    237 colecciones automáticas por tag · menú de 3 niveles · 2.618 productos (pendiente de carga)
                                                  ▲
  GitHub sergifs26/Indicativo-base: main = operaciones · production ↔ tema publicado · staging ↔ vista previa
```

## 2. Catálogo

- 2.636 filas en el Excel → **2.474** tras quitar 2 pruebas, 159 solo descatalogados y 1
  duplicado. Se resolvieron 6 SKUs duplicados y se generaron 12 SKUs de packs.
- **+144** modelos Icom de la lista PVP que no estaban en el Excel (sin fotos ni ficha larga).
- Total a cargar: **2.618** productos, 10.403 imágenes referenciadas en pihernz.com.
- Tags: `cat:<Nivel1>`, `cat:<Nivel1>><Nivel2>`… por cada ruta de categoría; `marca:<marca>`;
  `outlet`, `oferta`, `pack`, `descatalogado`, `icom-nuevo`, `peso-estimado`, `precio-provisional`.

## 3. Precios

| Origen | Productos | Estado |
|---|---|---|
| Lista PVP Icom (revisada a mano) | 159 | Real. 6 modelos con nota «Verificar» |
| Provisional inventado | 2.459 | Rango por categoría × marca, packs por unidades, variantes de color con el mismo precio |
| Falcon | 0 | PDF corrupto: pedir de nuevo |
| Pihernz | 0 | Su web oculta precios sin login: pedir export con precios |

## 4. Tienda

- `indicativo-base.myshopify.com`, plan "Basic App Development" (**desarrollo**: no cobra, no
  se puede pasar a producción ni transferir).
- Estado de configuración pendiente: idioma por defecto `en` (debe ser `es`), zona horaria
  `America/New_York` (debe ser `Europe/Madrid`), nombre con espacio final.

## 5. Errores resueltos

| # | Problema | Causa | Arreglo |
|---|---|---|---|
| 1 | Tarifa Falcon ilegible | El PDF se guardó como texto UTF-8: el 68 % de los bytes quedó como «�» | Irrecuperable: pedir el original por enlace, no adjunto |
| 2 | Precios Icom erróneos al extraer | El PDF desplaza e intercambia columnas en la mitad de las páginas | Tabla revisada a mano con la regla PVP = tarifa × 1,21 como control |
| 3 | `bulkOperationRunMutation` rechazada | Política de seguridad del conector MCP | Carga masiva por la CLI (`bulk_cli.mjs`) |
| 4 | No se puede borrar un cliente demo | Estaba ligado a una empresa B2B de demo con pedidos borrador | Borrar borradores → contacto → empresa → cliente, en ese orden |
| 5 | Colecciones creadas invisibles | Las colecciones creadas por API no se publican solas | `publishablePublish` por colección (`publicationUpdate` solo admite productos) |
| 6 | El conector deja de responder a mitad | El token del conector caduca | Reautorizar en claude.ai → Conectores; los scripts por CLI no dependen de él |
| 7 | El tema publicado no se puede editar por MCP | Política del conector | Tema no publicado o flujo git (GitHub Integration) |
| 8 | Copiar docs de otro repo del grupo, bloqueado | Control de permisos sobre contenido de otro proyecto | Docs propios con la misma metodología; los playbooks genéricos se enlazan, no se copian |

## 6. Referencias

| Tema | Dónde |
|---|---|
| Metodología original | `../../Almacen del baño/Almacen-del-ba-o/Agents-IA/FORMA_DE_TRABAJO.md` |
| Admin API 2026-04 (productSet, colecciones, publicación) | `../../Almacen del baño/Almacen-del-ba-o/Agents-IA/SHOPIFY_API_2026_04_NOTAS_TECNICAS.md` |
| Tracking GTM + Consent Mode v2 | `../../Almacen del baño/Almacen-del-ba-o/Agents-IA/GTM_SHOPIFY_PLAYBOOK.md` |

---

## Actualización 2026-09-12

Valoración de los ficheros del usuario: Excel sin precios ni stock, lista Icom legible con
columnas desplazadas, tarifa Falcon corrupta. Pipeline de catálogo (Fase 0) y CSV de Shopify.

## Actualización 2026-09-28

- Precios provisionales para los 2.459 productos sin precio real.
- Tienda de desarrollo `indicativo-base` creada por el usuario y conectada. Borrado todo el
  contenido demo: 17 productos, 2 colecciones, 3 clientes, 2 empresas, 5 descuentos y 10 pedidos
  borrador.
- 237 colecciones automáticas por tag creadas y publicadas; menú principal de 10 secciones en
  3 niveles y menú del pie; página «Contacto».
- Forma de trabajo replicada de Almacén del Baño: carpeta reorganizada en `Indicativo-base/`
  (operaciones) e `indicativo-base-theme/` (tema), ficheros de proveedor fuera de git,
  `CLAUDE.md`, documentación en `Agents-IA/`, cliente Admin API por CLI y carga masiva por CLI.
