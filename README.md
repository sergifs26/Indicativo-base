# indicativo-base-theme

Tema Shopify de **Indicativo Base** (tienda de radiocomunicación), versionado con la
**GitHub Integration** de Shopify. Base: "Generated Data Theme" 1.0.0 de Shopify (familia Dawn).

> Metodología completa: `Agents-IA/FORMA_DE_TRABAJO.md` §6 en el repo de operaciones
> (`../Indicativo-base`).

## Ramas

| Rama | Conectada a | Quién la toca |
|---|---|---|
| `production` | Tema **publicado** | El admin (Personalizar: `shopify[bot]` commitea solo) y los merges desde `staging` |
| `staging` | Tema de **vista previa** | Desarrollo (push desde local) |

## Las 3 reglas de oro

1. **Lo que se edita en el admin se respeta**: sus cambios llegan solos a `production`.
2. **El código pasa por `staging`**: local → push a `staging` → revisar en vista previa →
   merge a `production` (se despliega en ~30 s). Nunca `shopify theme push` al tema publicado.
3. **Un fichero, una persona**: avisar antes de tocar una zona. Si la sincronización automática
   falla por conflicto, se resuelve a mano en local.

`.github/workflows/sync-staging.yml` mergea cada push de `production` en `staging`.

## Rollback

GitHub → commits de `production` → **Revert** del commit problemático (~1 min hasta el live).

## Trabajo en local

```bash
git pull                     # SIEMPRE antes de editar
# … editar …
git push origin staging      # → se despliega en el tema de vista previa
```
