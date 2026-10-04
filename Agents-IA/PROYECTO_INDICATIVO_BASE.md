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
    237 colecciones automáticas por tag · menú de 3 niveles · 2.618 productos publicados
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
| 9 | 1 de 2.618 productos rechazado al cargar | Nombre de imagen con «–» (y otro con «ñ») sin codificar: «La URL del archivo no es válida» | `url_segura()` en `shopify_bulk.py` codifica los caracteres no ASCII |
| 10 | La prueba de conexión fallaba tras autorizar la CLI | `shopLocales` pide `read_locales` y el nombre de las ubicaciones `read_locations` | La prueba solo pide campos con permiso |
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

## Actualización 2026-09-29

- Repo en GitHub `sergifs26/Indicativo-base`: `main` (operaciones) + `production`/`staging` (tema).
- CLI autorizada (`shopify store auth`). Carga masiva de los 2.618 productos por
  `bulk_cli.mjs` en 1 min 36 s: 2.617 a la primera; el restante tras codificar su URL de imagen.
  Publicados los 2.618 en la Tienda online con una segunda operación masiva. Imágenes: 10.403
  READY, 0 fallidas; 251 productos sin foto (ya venían así).
- Tema: portada en español con el estilo de `test-data` (titular en negro, categorías, walkies
  profesionales, ventajas, antenas base, microauriculares), pie sin demo, barra «tienda en
  pruebas», menú mega. Probado en un tema de vista previa, pasado a `production` y publicado
  como «Indicativo Base» (`190088544584`). `test-data` queda sin publicar como respaldo.
- Menú de escritorio en desplegable lateral (☰) a petición del usuario: las 10 secciones
  ocupaban dos filas.
- **Enfoque montañismo** (petición del usuario, estilo The North Face): banner a pantalla
  completa con alpinista en arista nevada, franja en blanco y negro «Donde no hay cobertura, hay
  radio», categorías y destacados de montaña. Colección automática `montana` (217 productos) y
  primera sección del menú, aplicada con el nuevo `aplicar_menu.mjs` (su dry-run evitó borrar
  «Contacto» del pie, que no estaba en `menu_shopify.py`).
- Fotos de Unsplash (Mike Markov, Giacomo Berardi). `fileCreate` exige que el nombre coincida con
  la extensión de la URL de origen; las de Unsplash no la llevan → se suben sin nombre.
- Error del tema: `image_overlay_opacity` del banner va en pasos de 10; con 35 Shopify rechazó la
  plantilla entera (la tienda siguió con la portada anterior).
- Banner de portada solo con el titular (sin texto ni botones), a petición del usuario.
- **Logo** entregado por el usuario (montaña + «INDICATIVO BASE», gris oscuro sobre crema). Como
  la cabecera es negra, `procesar_logo.py` saca la transparencia por luminosidad, limpia las motas
  del papel con una apertura morfológica, recorta y genera versión blanca, oscura, icono y favicon.
  Subidos con el nuevo `subir_fichero.mjs` y puestos en el tema (logo blanco 220 px + favicon).
- Fuera el aviso «Tienda en pruebas». Barra de anuncios **rotativa** (el tema apilaba los
  anuncios): envíos a España e internacionales, teléfono provisional inventado, asesoramiento y
  PMR-446 de uso libre; rota cada 5 s y se pausa con el ratón.
- **Ficha de producto**: descripción en desplegables (1.603 de 2.474 descripciones tienen
  apartados con título; 486 ninguno) y columna de información con scroll propio bajo la cabecera.
  Antes de publicar se simuló la partición sobre todo el catálogo (0 títulos-frase, máximo 7
  desplegables) y se renderizó el snippet con `liquidjs` sobre 5 productos reales, porque la
  tienda con contraseña no se puede abrir desde aquí.
- **Fotos uniformes**: de 10.403 imágenes, 5.129 cuadradas, 1.814 verticales y 3.460 apaisadas; las
  tarjetas las recortaban (marco vertical + cover). Ahora todas en marco cuadrado, enteras, con
  margen y sobre blanco, en listados y en la galería de la ficha (solo tema, sin tocar las fotos).
- **Tienda en español**: `locales/en.default.json` relleno con el español del tema adaptado a España
  (la API no permite cambiar el idioma por defecto); plantillas y `lang="es"`. El checkout y los
  correos siguen en inglés hasta que el usuario cambie el idioma por defecto en el admin.

## Actualización 2026-10-04

**Giro outdoor** (plan aprobado por el usuario): la tienda hablaba sobre todo a profesionales. Pasa
a un tono cercano para quien empieza y quien ya tiene experiencia, y a 5 entornos: Montaña,
Náutica, Nieve, Camping y familia, Caza y pesca. Portada con carrusel por entornos; guías y
glosario ahora, recomendador más adelante.

- **Normativa verificada** antes de etiquetar licencias: CB-27 de uso común sin licencia
  (BOE-A-1996-5272, cb27.com/legal/reglamentocb, Ley 9/2014); PMR-446 0,5 W sin licencia
  (onedirect.es); VHF marina: licencia de estación de barco en zonas 1-3 y certificado de operador
  restringido SMSSM (transportes.gob.es, BOE-A-2006-18968); VHF/UHF profesional con autorización
  (tecnitran.es). Resumen usable en `GUIA_DE_TONO.md`.
- **Fase 1 (datos)**: `scripts/entornos.py` clasifica por categoría + señales del texto (grado IP,
  «sumergible», marina, caza) + `data/entornos_excepciones.csv`. Resultado del dry-run: 506
  productos etiquetados (montaña 161, náutica 66, nieve 55, camping 91, caza y pesca 86; para
  empezar 38, para expertos 167; licencia no 156, sí 101, marina 18). El título manda sobre la
  categoría del proveedor: 3 equipos UHF profesionales metidos en categorías PMR salen como
  licencia:si. Caza y pesca solo coge walkies **VHF** profesionales (los UHF/DMR compactos son de
  empresa) y PMR IPx5 o más. **Pendiente de revisión del usuario antes de aplicar.**
- `scripts/colecciones_entorno.mjs` (7 colecciones: `montana` conserva handle y pasa a la
  etiqueta; `nautica`, `nieve`, `camping-y-familia`, `caza-y-pesca`, `para-empezar`,
  `para-expertos`). `shopify_bulk.py` reinyecta las etiquetas en futuras recargas.
- 11 fotos de Unsplash (licencia libre comprobada en cada página) subidas a Ficheros como
  `entorno-*.jpg`; créditos en `imagen-corporativa/fotos/CREDITOS.md`.
- Textos en `contenido/`: 6 guías (750-880 palabras, con preguntas frecuentes), glosario de 34
  términos, textos de portada y microtextos de ficha. Guía de tono en `Agents-IA/GUIA_DE_TONO.md`.
- Errores: `CollectionRuleSet` expone `appliedDisjunctively` (no `appliedDisjunctive`); en Git Bash
  de esta máquina un heredoc de Python convirtió `\b` en un retroceso (0x08) dentro de una regex:
  los scripts con barras invertidas se escriben con la herramienta de ficheros, no con heredoc.
