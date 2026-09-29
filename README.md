# Indicativo Base

Repo de **operaciones** de la tienda Shopify Indicativo Base: radiocomunicación (walkies,
emisoras, antenas, accesorios y receptores). Cuarta tienda del Grupo Intertorrent, tras
espejoled.com, grifos.es y almacendelbaño.com.

> ⚠️ La rama `main` **no contiene el tema**. El tema vive en las ramas `production` y `staging`
> de este mismo repo (en local, carpeta `../indicativo-base-theme`), conectadas a Shopify con la
> GitHub Integration. Son historias independientes: no se mergean con `main`.

## Estructura

```
Agents-IA/     Base de conocimiento (docs en español, con fecha).
               EMPIEZA POR AQUÍ: FORMA_DE_TRABAJO.md e INDICATIVO_KICKOFF.md
scripts/       Pipeline de catálogo (Python) y herramientas de Admin API (Node .mjs)
data/          Salidas de los scripts (regenerables, fuera de git salvo lo editado a mano)
.env.example   Configuración local opcional
```

Los ficheros de proveedor (Excel de Pihernz y tarifas en PDF) están en la carpeta padre, fuera
del repo.

## Documentos clave

| Doc | Qué es |
|---|---|
| `Agents-IA/FORMA_DE_TRABAJO.md` | Metodología (obligatoria para personas y agentes IA) |
| `Agents-IA/INDICATIVO_KICKOFF.md` | Arranque: fuentes de verdad, accesos, decisiones, primeros pasos |
| `Agents-IA/PROYECTO_INDICATIVO_BASE.md` | Documento maestro vivo: arquitectura, historia, errores resueltos |
| `Agents-IA/PLAN_MEJORAS_FUTURAS.md` | Backlog vivo |
| `CLAUDE.md` | Reglas operativas rápidas y datos clave de la tienda |

## Arranque rápido

```bash
npm run catalogo          # Excel + tarifas → data/shopify/ (CSV, JSONL, colecciones, menú)
npm run test:shopify      # comprueba la conexión con la tienda (requiere shopify store auth)
```

## Seguridad

Tokens y secretos **nunca** se commitean. Ver `.gitignore` y `Agents-IA/FORMA_DE_TRABAJO.md` §5.
