/**
 * scripts/colecciones_entorno.mjs — colecciones automáticas de entorno y nivel (giro outdoor).
 *
 * Una colección por etiqueta de scripts/entornos.py. Idempotente por handle: si existe se
 * actualizan reglas, título, descripción e imagen; si no, collectionCreate + publicación en la
 * Tienda online. La de montaña conserva el handle `montana` (menú y portada no cambian) y pasa
 * de su OR de categorías a la etiqueta entorno:montana.
 *
 * ⚠️ Lanzar DESPUÉS de aplicar las etiquetas (tags_add): con --apply se niega a tocar una
 * colección cuya etiqueta no tenga productos en la tienda, para no vaciar `montana`.
 *
 * Uso:
 *   node scripts/colecciones_entorno.mjs            # dry-run: estado actual y productos por etiqueta
 *   node scripts/colecciones_entorno.mjs --apply    # crea/actualiza, publica y guarda los ids en
 *                                                   # data/shopify/colecciones_ids.json (menu_shopify.py)
 * Imágenes: data/shopify/imagenes_entorno.json ({handle: url de Shopify Files}), opcional.
 */
import { readFileSync, writeFileSync, existsSync } from 'node:fs';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
import { adminGraphQL, userErrors } from './admin.mjs';

const RAIZ = join(dirname(fileURLToPath(import.meta.url)), '..');
const APPLY = process.argv.includes('--apply');
const PUBLICACION = 'gid://shopify/Publication/302436352328'; // Tienda online
const F_IDS = join(RAIZ, 'data', 'shopify', 'colecciones_ids.json');
const F_IMG = join(RAIZ, 'data', 'shopify', 'imagenes_entorno.json');

const COLECCIONES = [
  {
    handle: 'montana', title: 'Montaña', tag: 'entorno:montana',
    texto: 'Walkies sin licencia, GPS, frontales y energía para no perder el contacto con tu grupo en la montaña, aunque no haya cobertura. Si es tu primera salida con radio, empieza por los walkies PMR-446: se encienden y funcionan.',
  },
  {
    handle: 'nautica', title: 'Náutica', tag: 'entorno:nautica',
    texto: 'Radios VHF marinas, walkies que aguantan el agua y fundas estancas para salir a navegar tranquilo. Ojo: la VHF marina pide titulación y, según la zona de navegación, licencia de estación de barco. Si tienes dudas, pregúntanos.',
  },
  {
    handle: 'nieve', title: 'Nieve', tag: 'entorno:nieve',
    texto: 'Walkies resistentes al agua, intercomunicadores y frontales para que el frío y la nieve no te dejen incomunicado. Para pistas, travesía y raquetas.',
  },
  {
    handle: 'camping-y-familia', title: 'Camping y familia', tag: 'entorno:camping',
    texto: 'Walkies fáciles para pequeños y mayores, linternas, lámparas y energía para que la acampada salga redonda y nadie se pierda.',
  },
  {
    handle: 'caza-y-pesca', title: 'Caza y pesca', tag: 'entorno:caza-pesca',
    texto: 'Walkies robustos, prismáticos, linternas y cámaras de caza para batidas, esperas y jornadas de pesca. Los walkies PMR-446 son de uso libre; los VHF profesionales necesitan licencia.',
  },
  {
    handle: 'para-empezar', title: 'Para empezar', tag: 'nivel:empezar',
    texto: 'Walkies PMR-446 de uso libre: sin licencia, sin tasas y listos para usar. Lo más sencillo si es tu primera vez con una radio.',
  },
  {
    handle: 'para-expertos', title: 'Para expertos', tag: 'nivel:experto',
    texto: 'Transceptores HF, emisoras doble banda, DMR, antenas HF y medidores para quien ya conoce la radio. Los equipos que transmiten en estas bandas necesitan licencia de radioaficionado o de uso profesional, según el caso.',
  },
];

const imagenes = existsSync(F_IMG) ? JSON.parse(readFileSync(F_IMG, 'utf8')) : {};

// Estado actual: colección por handle + nº de productos con la etiqueta en la tienda
const alias = COLECCIONES.map((c, i) => `
  c${i}: collectionByHandle(handle: ${JSON.stringify(c.handle)}) { id title productsCount { count } ruleSet { appliedDisjunctively rules { column condition } } }
  n${i}: productsCount(query: ${JSON.stringify(`tag:'${c.tag}'`)}) { count }`).join('');
const estado = await adminGraphQL(`query { ${alias} }`);

console.log(`\n${APPLY ? '🚀 APPLY' : '🔍 DRY-RUN'} — colecciones de entorno y nivel\n`);
COLECCIONES.forEach((c, i) => {
  const col = estado[`c${i}`], n = estado[`n${i}`]?.count ?? 0;
  const reglas = col?.ruleSet?.rules?.map((r) => r.condition).join(col.ruleSet.appliedDisjunctively ? ' OR ' : ' AND ');
  console.log(`${col ? '✏️  actualizar' : '➕ crear    '} ${c.handle.padEnd(18)} etiqueta ${c.tag.padEnd(20)} ${String(n).padStart(4)} productos en tienda` +
    (col ? ` · hoy ${col.productsCount.count} productos por «${(reglas || '').slice(0, 60)}${(reglas || '').length > 60 ? '…' : ''}»` : '') +
    (imagenes[c.handle] ? ' · con imagen' : ''));
});

if (!APPLY) { console.log('\n(dry-run — nada escrito. Añade --apply para aplicar)\n'); process.exit(0); }

const vacias = COLECCIONES.filter((_, i) => !(estado[`n${i}`]?.count));
if (vacias.length) {
  console.error(`\n❌ Sin productos con la etiqueta: ${vacias.map((c) => c.tag).join(', ')}. Aplica antes tags_add.`);
  process.exit(1);
}

const ids = existsSync(F_IDS) ? JSON.parse(readFileSync(F_IDS, 'utf8')) : {};
for (const [i, c] of COLECCIONES.entries()) {
  const input = {
    title: c.title,
    descriptionHtml: `<p>${c.texto}</p>`,
    ruleSet: { appliedDisjunctively: false, rules: [{ column: 'TAG', relation: 'EQUALS', condition: c.tag }] },
    ...(imagenes[c.handle] ? { image: { src: imagenes[c.handle], altText: c.title } } : {}),
  };
  const existente = estado[`c${i}`];
  let id;
  if (existente) {
    const r = await adminGraphQL(`mutation($input: CollectionInput!) { collectionUpdate(input: $input) {
      collection { id } userErrors { field message } } }`, { input: { id: existente.id, ...input } });
    if (userErrors(r).length) { console.error(`❌ ${c.handle}:`, userErrors(r)); process.exitCode = 1; continue; }
    id = existente.id;
  } else {
    const r = await adminGraphQL(`mutation($input: CollectionInput!) { collectionCreate(input: $input) {
      collection { id } userErrors { field message } } }`, { input: { handle: c.handle, ...input } });
    if (userErrors(r).length) { console.error(`❌ ${c.handle}:`, userErrors(r)); process.exitCode = 1; continue; }
    id = r.collectionCreate.collection.id;
  }
  // Las colecciones creadas por API no se publican solas (error #5); publicar de nuevo no hace daño.
  const p = await adminGraphQL(`mutation($id: ID!, $input: [PublicationInput!]!) { publishablePublish(id: $id, input: $input) {
    userErrors { field message } } }`, { id, input: [{ publicationId: PUBLICACION }] });
  if (userErrors(p).length) console.error(`⚠️ ${c.handle} sin publicar:`, userErrors(p));
  ids[c.handle] = id;
  console.log(`✅ ${c.handle} → ${id}`);
}
writeFileSync(F_IDS, JSON.stringify(ids, null, 1));
console.log(`\nIds guardados en ${F_IDS}`);
