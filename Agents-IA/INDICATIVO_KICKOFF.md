# Kickoff — Indicativo Base

> **Estado:** en curso · **Última revisión:** 2026-09-28
> Documento de arranque. Cuarta tienda Shopify del Grupo Intertorrent.

## 1. Qué es

**Indicativo Base**: tienda online de radiocomunicación (walkies PMR/profesionales/radioaficionado,
emisoras HF/VHF/UHF/CB, antenas, accesorios, receptores y escáneres, alimentación, telefonía y
outdoor). Tienda completa con carrito y pago en Shopify. Nombre comercial provisional (del nombre
de la carpeta del proyecto): confirmar.

## 2. Fuentes de verdad

| Dominio | Fuente | Notas |
|---|---|---|
| Datos de producto | `Export-info-productes.xlsx` (export WooCommerce de pihernz.com) | 2.636 filas → 2.474 tras limpieza. Imágenes alojadas en pihernz.com |
| Precios Icom radioafición | `LISTA PVP AFICIONADO 11022026 Rev2.pdf` → `data/precios_icom_revisado.csv` | 159 precios reales; 144 modelos nuevos que no estaban en el Excel |
| Precios del resto | **Pendiente**: tarifa Falcon (el PDF llegó corrupto) y export de Pihernz con precios | Mientras tanto, precios provisionales inventados |
| Stock | **Pendiente** | Inventario sin seguimiento: todo comprable |
| Diseño | Tema publicado `test-data` (Dawn) | El usuario quiere conservar su estilo, sin el contenido demo |

## 3. Accesos

| Acceso | Estado |
|---|---|
| Tienda Shopify | ✅ `indicativo-base.myshopify.com`, tienda de desarrollo, EUR, España |
| Conector Shopify (claude.ai) | ⚠️ Conectado pero caduca; reautorizar en claude.ai → Conectores |
| CLI de Shopify, temas | ✅ `shopify theme …` funciona con la sesión de la cuenta |
| CLI de Shopify, Admin API | ✅ `shopify store auth` hecho el 29/09 (sin `read_locales` ni `read_locations`) |
| Repo GitHub | ✅ `sergifs26/Indicativo-base` (main = operaciones; production/staging = tema) |
| GitHub Integration del tema | ❌ Pendiente conectar las ramas desde el admin |
| Dominio propio, tienda de pago | ❌ Cuando haya precios reales |
| GTM / GA4 / GSC / GMC | ❌ Pendiente |

## 4. Decisiones

| Decisión | Elegida | Descartadas | Por qué |
|---|---|---|---|
| Plataforma | Shopify | Web a medida (Next.js), WooCommerce | Tienda completa con pagos, pedidos, envíos e IVA resueltos |
| Entorno de pruebas | Tienda de desarrollo `indicativo-base` | Montar directamente la de pago | Gratis, siempre con contraseña: no se puede vender por error a precios inventados |
| Catálogo | Excel de Pihernz limpio + 144 Icom de la lista PVP | Todo tal cual | Fuera descatalogados, pruebas y duplicados |
| Precios | Provisionales inventados con tag | Esperar a tener todos los precios | El usuario quiere avanzar con la tienda ya |
| Categorías | Colecciones automáticas por tag `cat:` y `marca:` | Colecciones manuales | Se llenan solas al importar y al cambiar productos |
| Carga masiva | CLI `shopify store bulk execute` | MCP (bloqueado), CSV del admin | Automatizable, idempotente por handle y re-ejecutable |
| Estilo | Tema `test-data` actual | Otros temas | Petición expresa del usuario |

## 5. Primeros pasos

1. ✅ Valoración de ficheros y pipeline de catálogo (Fase 0)
2. ✅ Precios provisionales
3. ✅ Tienda de pruebas limpia de demo; colecciones y menús creados
4. ✅ Forma de trabajo replicada de Almacén del Baño (este repo + repo del tema)
5. ✅ Repo en GitHub · ⬜ GitHub Integration del tema (conectar `production` y `staging` desde el admin)
6. ✅ `shopify store auth` y carga de los 2.618 productos por `bulk_cli.mjs` (29/09)
7. ✅ Portada y textos del tema en español con el estilo actual, tema publicado (29/09)
8. ⬜ Ajustes: idioma por defecto español, zona horaria Madrid, nombre sin espacio final
9. ⬜ Precios reales (Falcon + Pihernz), stock, datos legales de empresa
10. ⬜ Tienda de pago, dominio, analítica y lanzamiento

---

## Actualización 2026-09-28

Documento creado al replicar la forma de trabajo de Almacén del Baño.
