/**
 * scripts/aplicar_menu.mjs — aplica el menú principal y el del pie definidos en menu_shopify.py.
 *
 * ⚠️ menuUpdate REEMPLAZA el árbol entero: antes de escribir se guarda el menú actual completo
 * (3 niveles) en scripts/out/menu_backup_<fechaUTC>.json.
 *
 * Uso:
 *   python scripts/menu_shopify.py          # genera data/shopify/menu_principal.json y menu_pie.json
 *   node scripts/aplicar_menu.mjs           # dry-run: compara el menú actual con el nuevo
 *   node scripts/aplicar_menu.mjs --apply   # backup + menuUpdate de los dos menús
 * Credencial: sesión de la CLI de Shopify (ver scripts/admin.mjs).
 */
import { readFileSync, writeFileSync, mkdirSync } from 'node:fs';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
import { adminGraphQL, userErrors, OUT } from './admin.mjs';

const RAIZ = join(dirname(fileURLToPath(import.meta.url)), '..');
const APPLY = process.argv.includes('--apply');
const MENUS = [
  { id: 'gid://shopify/Menu/307524960584', title: 'Menú principal', handle: 'main-menu', fichero: 'menu_principal.json' },
  { id: 'gid://shopify/Menu/307524993352', title: 'Pie de página', handle: 'footer', fichero: 'menu_pie.json' },
];

const ITEM = 'title type url resourceId';
const actual = await adminGraphQL(`query($ids: [ID!]!) { nodes(ids: $ids) { ... on Menu { id handle title
  items { ${ITEM} items { ${ITEM} items { ${ITEM} } } } } } }`, { ids: MENUS.map((m) => m.id) });

const titulos = (items, n = 0) => (items || []).flatMap((i) => [`${'  '.repeat(n)}${i.title}`, ...titulos(i.items, n + 1)]);

for (const m of MENUS) {
  const nuevo = JSON.parse(readFileSync(join(RAIZ, 'data', 'shopify', m.fichero), 'utf8'));
  const viejo = actual.nodes.find((n) => n?.id === m.id);
  const a = titulos(viejo?.items), b = titulos(nuevo);
  const quita = a.filter((t) => !b.includes(t)), pone = b.filter((t) => !a.includes(t));
  console.log(`\n${m.handle}: ${a.length} enlaces ahora → ${b.length} nuevos`);
  for (const t of pone) console.log(`  + ${t.trim()}`);
  for (const t of quita) console.log(`  - ${t.trim()}`);
}

if (!APPLY) { console.log('\n(dry-run — nada escrito. Añade --apply para aplicar)\n'); process.exit(0); }

mkdirSync(OUT, { recursive: true });
const copia = join(OUT, `menu_backup_${new Date().toISOString().replace(/[-:]/g, '').slice(0, 15)}.json`);
writeFileSync(copia, JSON.stringify(actual.nodes, null, 1));
console.log(`\nCopia del menú actual: ${copia}`);

const M = `mutation($id: ID!, $title: String!, $handle: String, $items: [MenuItemUpdateInput!]!) {
  menuUpdate(id: $id, title: $title, handle: $handle, items: $items) { menu { id } userErrors { field message code } } }`;
for (const m of MENUS) {
  const items = JSON.parse(readFileSync(join(RAIZ, 'data', 'shopify', m.fichero), 'utf8'));
  const d = await adminGraphQL(M, { id: m.id, title: m.title, handle: m.handle, items });
  const errs = userErrors(d);
  console.log(errs.length ? `❌ ${m.handle}: ${JSON.stringify(errs)}` : `✅ ${m.handle} actualizado`);
  if (errs.length) process.exitCode = 1;
}
