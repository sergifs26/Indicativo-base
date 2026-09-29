# Plan de mejoras futuras — Indicativo Base

> **Estado:** vivo · **Última revisión:** 2026-09-28
> Backlog. Al completar una entrada, se mueve a su documento o a `PROYECTO_INDICATIVO_BASE.md`.

## Bloqueantes para vender

- **Precios reales**: tarifa Falcon en buen estado + export de Pihernz con precio. Cruce por
  SKU/EAN (`precios_<fuente>.py`), recarga por `bulk_cli.mjs` y retirada del tag `precio-provisional`.
- **Stock / disponibilidad**: qué hay en almacén y qué es bajo pedido.
- **Datos de empresa**: nombre comercial definitivo, dominio, logo, CIF y dirección, teléfono,
  email de pedidos. Con ellos: aviso legal, privacidad, cookies, condiciones de venta, devoluciones.
- **Tienda de pago**: crear la definitiva y replicar por script (catálogo, colecciones, menús, tema).
- **Pagos y envíos**: Shopify Payments / Bizum / PayPal; tarifas por peso (220 productos tienen
  peso estimado por categoría).

## Catálogo

- Fotos y descripciones de los 144 Icom nuevos (hoy sin imagen).
- 268 descripciones de menos de 100 caracteres.
- Revisar los 6 precios Icom marcados «Verificar» contra el PDF.
- Alojar las imágenes en Shopify ya está cubierto por la carga (Shopify las descarga); confirmar
  que ninguna URL de pihernz.com falla.
- Confirmar con Pihernz el permiso para reutilizar descripciones e imágenes.
- Filtros de colección (Search & Discovery) por marca, banda, tipo; metacampos si hace falta.

## Tema y contenido

- Quitar la barra «Tienda en pruebas · Los precios son provisionales» cuando los precios sean reales.
- Conectar la GitHub Integration y retirar los temas subidos por CLI.
- Imágenes de marca (hero, tarjetas de categoría).

## Analítica y posicionamiento

- GTM + Consent Mode v2 + GA4 + píxel de checkout (playbook del grupo).
- Google Search Console y Merchant Center cuando haya dominio.
- Schema de producto y organización, `robots.txt` con bots de IA, FAQs.
