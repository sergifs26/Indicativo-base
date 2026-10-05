/**
 * scripts/aplicar_antenas.mjs — guarda en cada walkie su antena original de recambio
 * (metacampo custom.antenas_recambio, lista de productos) a partir de data/antenas_recambio.json,
 * que genera scripts/antenas.py. La ficha del tema lo lee para la casilla «Añade una antena de
 * recambio» (snippets/producto-antena-recambio.liquid).
 *
 * Uso:
 *   python scripts/antenas.py                 # empareja e informa (data/antenas_informe.md)
 *   node scripts/aplicar_antenas.mjs          # dry-run: qué se pondría y qué se quitaría
 *   node scripts/aplicar_antenas.mjs --apply  # crea la definición si falta, metafieldsSet y
 *                                             # metafieldsDelete; guarda la foto de lo aplicado
 * Credencial: sesión de la CLI de Shopify (ver scripts/admin.mjs).
 */
import { readFileSync, writeFileSync, existsSync, readdirSync } from 'node:fs';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
import { adminGraphQL, userErrors, OUT } from './admin.mjs';

const RAIZ = join(dirname(fileURLToPath(import.meta.url)), '..');
const APPLY = process.argv.includes('--apply');
const F_PARES = join(RAIZ, 'data', 'antenas_recambio.json');
const F_APLICADO = join(RAIZ, 'data', 'antenas_recambio_aplicado.json');
const NS = 'custom';
const KEY = 'antenas_recambio';
const TIPO = 'list.product_reference';

// handle → gid a partir de los resultados de la carga masiva de productos (el último manda)
const ids = {};
for (const f of readdirSync(OUT).filter((n) => /^bulk_product_set_.*\.jsonl$/.test(n)).sort()) {
  for (const l of readFileSync(join(OUT, f), 'utf8').split(/\r?\n/).filter(Boolean)) {
    for (const v of Object.values(JSON.parse(l).data || {})) if (v?.product?.id) ids[v.product.handle] = v.product.id;
  }
}

const pares = JSON.parse(readFileSync(F_PARES, 'utf8'));
const antes = existsSync(F_APLICADO) ? JSON.parse(readFileSync(F_APLICADO, 'utf8')) : {};
const poner = Object.entries(pares).filter(([h, a]) => JSON.stringify(antes[h]) !== JSON.stringify(a));
const quitar = Object.keys(antes).filter((h) => !(h in pares));
const faltan = [...new Set([...Object.keys(pares), ...Object.values(pares).flat()])].filter((h) => !ids[h]);

console.log(`\n${APPLY ? '🚀 APPLY' : '🔍 DRY-RUN'} — ${NS}.${KEY}: ${Object.keys(pares).length} walkies con antena`);
console.log(`   poner/cambiar: ${poner.length} · quitar: ${quitar.length}${faltan.length ? ` · ⚠️ sin id: ${faltan.join(', ')}` : ''}`);
if (faltan.length) process.exit(1);
if (!APPLY) { console.log('\n(dry-run — nada escrito. Añade --apply para aplicar)\n'); process.exit(0); }

// 1. Definición del metacampo (para verlo y editarlo en el admin del producto)
const def = await adminGraphQL(`query { metafieldDefinitions(first: 1, ownerType: PRODUCT, namespace: "${NS}", key: "${KEY}") { nodes { id } } }`);
if (!def.metafieldDefinitions.nodes.length) {
  const r = await adminGraphQL(`mutation($d: MetafieldDefinitionInput!) { metafieldDefinitionCreate(definition: $d) {
    createdDefinition { id } userErrors { field message code } } }`, { d: {
    name: 'Antena de recambio', namespace: NS, key: KEY, type: TIPO, ownerType: 'PRODUCT',
    description: 'Antena original del modelo que se ofrece en la ficha del walkie (scripts/antenas.py)' } });
  if (userErrors(r).length) { console.error('❌ definición:', userErrors(r)); process.exit(1); }
  console.log('✅ definición creada');
}

// 2. Poner (lotes de 25, el máximo de metafieldsSet)
for (let i = 0; i < poner.length; i += 25) {
  const lote = poner.slice(i, i + 25).map(([h, a]) => ({
    ownerId: ids[h], namespace: NS, key: KEY, type: TIPO, value: JSON.stringify(a.map((x) => ids[x])) }));
  const r = await adminGraphQL(`mutation($m: [MetafieldsSetInput!]!) { metafieldsSet(metafields: $m) {
    metafields { id } userErrors { field message code } } }`, { m: lote });
  if (userErrors(r).length) { console.error('❌ metafieldsSet:', userErrors(r)); process.exit(1); }
  console.log(`✅ ${Math.min(i + 25, poner.length)}/${poner.length} puestos`);
}

// 3. Quitar los que ya no tienen antena
if (quitar.length) {
  const r = await adminGraphQL(`mutation($m: [MetafieldIdentifierInput!]!) { metafieldsDelete(metafields: $m) {
    deletedMetafields { key } userErrors { field message } } }`, { m: quitar.map((h) => ({ ownerId: ids[h], namespace: NS, key: KEY })) });
  if (userErrors(r).length) { console.error('❌ metafieldsDelete:', userErrors(r)); process.exit(1); }
  console.log(`✅ ${quitar.length} quitados`);
}

writeFileSync(F_APLICADO, JSON.stringify(pares, null, 1));
console.log(`\nFoto de lo aplicado → ${F_APLICADO}`);
