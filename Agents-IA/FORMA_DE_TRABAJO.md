# Forma de trabajo — Indicativo Base

> **Estado:** vigente · **Última revisión:** 2026-09-28
> Metodología del grupo (consolidada en espejoled, grifos y Almacén del Baño) aplicada a esta
> tienda. Es la referencia para cualquier persona o agente de IA que trabaje en estos repos.

## 1. Filosofía

- **Lo nativo de Shopify primero y a coste 0**: tags, colecciones automáticas, metacampos,
  Shopify Flow y funciones nativas antes que cualquier app de pago.
- **La solución más simple que funcione.** Leer la documentación oficial antes de proponer.
- **Intervención quirúrgica**: cambiar lo mínimo, sin añadir lo que nadie ha pedido.
- **Piloto antes de lote**: todo cambio masivo de catálogo se prueba antes con un producto o una
  categoría, y se anota el resultado.
- **Verificar de verdad**: pedido de prueba real para cambios de compra; las URLs tras un
  despliegue las revisa el usuario en su navegador.

## 2. Documentación = memoria del proyecto

- Todo aprendizaje **no obvio** se escribe en `Agents-IA/`, en markdown y en español.
- Cada documento abre con **estado + fecha de última revisión**. Los documentos vivos crecen con
  secciones `## Actualización AAAA-MM-DD` al final; la historia no se borra.
- **Decisiones** en tabla: elegida | descartadas | por qué.
- **Errores resueltos** con formato problema → causa → arreglo.
- **Playbooks genéricos** del grupo (válidos para cualquier tienda) separados de los
  **documentos de instancia** (IDs y estado de esta tienda). Los genéricos no se duplican aquí:
  se consultan en su repo de origen, p. ej. `../../Almacen del baño/Almacen-del-ba-o/Agents-IA/`
  (`SHOPIFY_API_2026_04_NOTAS_TECNICAS.md`, `GTM_SHOPIFY_PLAYBOOK.md`).
- `PLAN_MEJORAS_FUTURAS.md` es el backlog: lo terminado se mueve a su documento o al histórico.

## 3. Repositorios

Un solo repo en GitHub, **`sergifs26/Indicativo-base`**, con dos historias independientes
(a diferencia de Almacén, que usa dos repos; la separación es la misma, solo cambia el contenedor):

| Rama (carpeta local) | Contenido |
|---|---|
| `main` (`Indicativo-base/`) | Operaciones: `Agents-IA/`, `scripts/`, `data/`. **Sin tema.** |
| `production` / `staging` (`indicativo-base-theme/`) | El tema Shopify, con GitHub Integration. |
| Carpeta padre (`Pagina indicativobase/`) | Ficheros de proveedor (Excel, tarifas PDF). **Fuera de git.** |

`main` y las ramas del tema **nunca se mergean entre sí**.

## 4. Scripts

- **Dry-run por defecto**; `--apply` para escribir. Orden: vista previa → dry-run → apply.
- **Idempotentes**: buscar por handle/SKU antes de crear; re-ejecutar nunca duplica.
- **Backup antes de borrar** en `scripts/out/` con fecha UTC.
- **Resultados y logs** en `scripts/out/` para reanudar operaciones largas.
- **Cabecera** con propósito, uso y credencial necesaria.
- **Alias `.myshopify.com`** siempre, nunca el dominio propio.
- Python 3 (pandas) para el pipeline de catálogo; Node `.mjs` sin dependencias para la Admin API.
- Escrituras masivas **por la CLI de Shopify** (`scripts/bulk_cli.mjs`): el conector MCP las bloquea.

## 5. Secretos y seguridad

- **Ningún token ni secreto en git ni en el chat.** Van en `.env` (ignorado) o en la sesión de la CLI.
- `.gitignore` cubre secretos, ficheros de proveedor y datos regenerables.
- Scopes mínimos; rotar credenciales tras cualquier exposición.

## 6. Tema: de desarrollo a producción

- El tema vive en su repo con la **GitHub Integration**: `production` ↔ tema publicado,
  `staging` ↔ tema de vista previa.
- **Lo que se edita en el admin (Personalizar) lo commitea `shopify[bot]` en `production`.**
  Por eso: `git pull` SIEMPRE antes de editar.
- **El código pasa por `staging`**: local → push a `staging` → revisar en vista previa → merge a
  `production` (se despliega solo en ~30 s).
- Una GitHub Action mergea cada push de `production` en `staging` para mantenerlas alineadas.
- **Rollback**: Revert del commit en GitHub (~1 min).
- **Nunca** `shopify theme push` contra el tema publicado ni force-push. El conector MCP tampoco
  puede escribir en el tema publicado: se trabaja sobre un tema no publicado o por git.
- **Un fichero, una persona**: `config/settings_data.json`, `sections/header-group.json`,
  `sections/footer-group.json` y `templates/index.json` son de escritura exclusiva.

## 7. Catálogo y precios

- **Datos de producto**: export de Pihernz (`Export-info-productes.xlsx`) → `limpiar_catalogo.py`.
- **Precios**: tarifas de proveedor. Hoy solo es real la lista Icom (`precios_icom_revisado.csv`,
  revisada a mano porque el PDF desplaza columnas). El resto son **provisionales** (tag
  `precio-provisional`) hasta tener Falcon y el export de Pihernz con precios.
- Prioridad de precio: **real > provisional**. Un precio real nunca se pisa con uno inventado.
- Los errores de datos se corrigen **en la fuente** (o en la tabla de reglas del script), no a
  mano en Shopify: si no, la siguiente carga los devuelve.
- **Los tags son contrato**: las colecciones automáticas dependen de `cat:<ruta>`, `marca:<marca>`,
  `outlet`, `oferta`, `pack`, `icom-nuevo`. No renombrarlos ni borrarlos sin regenerar colecciones.
- Precios siempre **PVP con IVA** (la tienda tiene los impuestos incluidos).

## 8. Commits y ramas

- **Conventional Commits en español, con ámbito**: `feat(catalogo): …`, `fix(precios): …`,
  `docs(agents-ia): …`, `chore(scripts): …`, `ci(tema): …`.
- `main` lineal en operaciones; `production`/`staging` solo en el repo del tema.

## 9. Grupo Intertorrent (multi-tienda)

- Cada tienda es una **isla técnica y legal**: los clientes no se comparten entre tiendas.
- El conector de Shopify de claude.ai y la CLI pueden estar apuntando a **otra tienda del grupo**
  (Almacén del Baño, Espejoled…). **Comprobar siempre la tienda antes de escribir.**

## 10. SEO, GEO y analítica

- Tracking según el playbook GTM del grupo (GTM + Consent Mode v2 + GA4 + píxel de checkout).
- GEO además de SEO: schema completo, `robots.txt` con bots de IA permitidos, página de mapa de
  contenidos, FAQs en metacampos.

---

## Actualización 2026-09-28

Documento creado replicando la forma de trabajo de Almacén del Baño (repo
`intertorrentshopify-design/Almacen-del-ba-o`), adaptada a esta tienda: catálogo desde el export
de Pihernz y tarifas en lugar del PIM ProductSoul, precios provisionales y tienda de desarrollo
como entorno de pruebas.
