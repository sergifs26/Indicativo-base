/**
 * scripts/coleccion_seleccion.mjs — colección manual «Lo que más valoramos» (portada, 23/10/2026).
 *
 * Selección de Icom y Yaesu, las marcas que el cliente dice que más se valoran («La clave de
 * IndicativoBase.doc»). Solo modelos con foto. Idempotente por handle: crea la colección o
 * actualiza título, texto y productos (añade los que falten, quita los que sobren y deja el
 * orden de la lista). Se publica en la Tienda online.
 *
 * Uso:
 *   node scripts/coleccion_seleccion.mjs            # dry-run
 *   node scripts/coleccion_seleccion.mjs --apply
 */
import { adminGraphQL, userErrors } from './admin.mjs';

const APPLY = process.argv.includes('--apply');
const PUBLICACION = 'gid://shopify/Publication/302436352328'; // Tienda online
const HANDLE = 'lo-que-mas-valoramos';
const TITULO = 'Lo que más valoramos';
const TEXTO = 'Icom y Yaesu: los equipos que más se valoran entre radioaficionados, navegantes y gente de montaña. Una selección para la estación, el barco, la ruta y la banda aérea.';
const PRODUCTOS = [
  'icom-ic-705-transceptor-portatil-hf-vhf-uhf-gps-bluetooth',
  'yaesu-ft-991a-transceptor-hf-vhf-uhf',
  'icom-ic-7300-mk2-transceptor-movil-hf',
  'yaesu-ft5de-walkie-digital-doble-banda',
  'yaesu-ft-891-transceptor-hf-y-50-mhz-100w',
  'icom-ic-m25-euro-evo-azul-walkie-marina-vhf',
  'yaesu-ft-65e-walkie-doble-banda-vhf-uhf',
  'yaesu-fta-550l-walkie-banda-aerea',
];

const alias = PRODUCTOS.map((h, i) => `p${i}: productByIdentifier(identifier: { handle: ${JSON.stringify(h)} }) { id title status media(first: 1) { nodes { id } } }`).join('\n');
const estado = await adminGraphQL(`query {
  c: collectionByHandle(handle: ${JSON.stringify(HANDLE)}) { id title ruleSet { rules { column } } products(first: 50) { nodes { id } } }
  ${alias}
}`);

const productos = PRODUCTOS.map((h, i) => ({ handle: h, ...estado[`p${i}`] }));
console.log(`\n${APPLY ? '🚀 APPLY' : '🔍 DRY-RUN'} — ${TITULO} (${estado.c ? 'actualizar' : 'crear'})\n`);
for (const p of productos) {
  console.log(`${!p.id ? '❌ no existe ' : p.status !== 'ACTIVE' ? `⚠️ ${p.status.padEnd(9)}` : !p.media.nodes.length ? '⚠️ sin foto  ' : '✅           '} ${p.title ?? p.handle}`);
}
const malos = productos.filter((p) => !p.id || p.status !== 'ACTIVE' || !p.media.nodes.length);
if (malos.length) { console.error('\n❌ Corrige la lista: hay productos que no existen, no están activos o no tienen foto.'); process.exit(1); }
if (estado.c?.ruleSet) { console.error(`\n❌ ${HANDLE} existe y es automática: no se toca.`); process.exit(1); }
if (!APPLY) { console.log('\n(dry-run — nada escrito. Añade --apply para aplicar)\n'); process.exit(0); }

const ids = productos.map((p) => p.id);
let id = estado.c?.id;
if (!id) {
  const r = await adminGraphQL(`mutation($input: CollectionInput!) { collectionCreate(input: $input) {
    collection { id } userErrors { field message } } }`,
  { input: { handle: HANDLE, title: TITULO, descriptionHtml: `<p>${TEXTO}</p>`, sortOrder: 'MANUAL', products: ids } });
  if (userErrors(r).length) { console.error('❌', userErrors(r)); process.exit(1); }
  id = r.collectionCreate.collection.id;
} else {
  const r = await adminGraphQL(`mutation($input: CollectionInput!) { collectionUpdate(input: $input) {
    collection { id } userErrors { field message } } }`,
  { input: { id, title: TITULO, descriptionHtml: `<p>${TEXTO}</p>`, sortOrder: 'MANUAL' } });
  if (userErrors(r).length) { console.error('❌', userErrors(r)); process.exit(1); }
  const hoy = estado.c.products.nodes.map((n) => n.id);
  const faltan = ids.filter((x) => !hoy.includes(x));
  const sobran = hoy.filter((x) => !ids.includes(x));
  if (faltan.length) {
    const a = await adminGraphQL(`mutation($id: ID!, $p: [ID!]!) { collectionAddProducts(id: $id, productIds: $p) { userErrors { field message } } }`, { id, p: faltan });
    if (userErrors(a).length) console.error('⚠️ añadir:', userErrors(a));
  }
  if (sobran.length) {
    const q = await adminGraphQL(`mutation($id: ID!, $p: [ID!]!) { collectionRemoveProducts(id: $id, productIds: $p) { userErrors { field message } } }`, { id, p: sobran });
    if (userErrors(q).length) console.error('⚠️ quitar:', userErrors(q));
  }
  const o = await adminGraphQL(`mutation($id: ID!, $m: [MoveInput!]!) { collectionReorderProducts(id: $id, moves: $m) { userErrors { field message } } }`,
    { id, m: ids.map((p, i) => ({ id: p, newPosition: String(i) })) });
  if (userErrors(o).length) console.error('⚠️ ordenar:', userErrors(o));
}
const p = await adminGraphQL(`mutation($id: ID!, $input: [PublicationInput!]!) { publishablePublish(id: $id, input: $input) {
  userErrors { field message } } }`, { id, input: [{ publicationId: PUBLICACION }] });
if (userErrors(p).length) console.error('⚠️ sin publicar:', userErrors(p));
console.log(`✅ ${HANDLE} → ${id}`);
