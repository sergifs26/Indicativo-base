/**
 * scripts/subir_fichero.mjs — sube ficheros locales a Ficheros (Files) de la tienda.
 *
 * Flujo: stagedUploadsCreate → POST multipart al almacén temporal → fileCreate → espera READY.
 * Idempotente por nombre: si ya existe un fichero con ese nombre en la tienda, no se sube otra vez.
 * En el tema se referencian como shopify://shop_images/<nombre>.
 *
 * Uso:
 *   node scripts/subir_fichero.mjs <ruta> <nombreEnShopify> ["texto alternativo"]            # dry-run
 *   node scripts/subir_fichero.mjs <ruta> <nombreEnShopify> ["texto alternativo"] --apply
 * Credencial: sesión de la CLI de Shopify (scopes write_files; ver scripts/admin.mjs).
 */
import { readFileSync, existsSync } from 'node:fs';
import { extname } from 'node:path';
import { adminGraphQL, userErrors } from './admin.mjs';

const args = process.argv.slice(2);
const APPLY = args.includes('--apply');
const [ruta, nombre, alt = ''] = args.filter((a) => !a.startsWith('--'));
if (!ruta || !nombre || !existsSync(ruta)) {
  console.error('Uso: node scripts/subir_fichero.mjs <ruta> <nombreEnShopify> ["alt"] [--apply]');
  process.exit(1);
}
const MIME = { '.png': 'image/png', '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg', '.webp': 'image/webp', '.svg': 'image/svg+xml', '.gif': 'image/gif' };
const mime = MIME[extname(nombre).toLowerCase()];
if (!mime || extname(nombre).toLowerCase() !== extname(ruta).toLowerCase()) {
  console.error('El nombre debe ser una imagen con la misma extensión que el fichero local (.png, .jpg, .webp, .svg, .gif).');
  process.exit(1);
}
const bytes = readFileSync(ruta);

const ya = await adminGraphQL(`query($q: String!) { files(first: 5, query: $q) { nodes { id fileStatus ... on MediaImage { image { url } } } } }`,
  { q: `filename:${nombre}` });
const existente = ya.files.nodes.find((n) => n.image?.url?.includes(`/files/${nombre}`));
if (existente) {
  console.log(`⏭  Ya existe en la tienda: ${existente.image.url} → shopify://shop_images/${nombre}`);
  process.exit(0);
}
console.log(`${APPLY ? '🚀' : '🔍'} ${ruta} (${Math.round(bytes.length / 1024)} KB) → ${nombre}`);
if (!APPLY) { console.log('(dry-run — nada subido. Añade --apply)'); process.exit(0); }

const st = await adminGraphQL(`mutation($input: [StagedUploadInput!]!) { stagedUploadsCreate(input: $input) {
  stagedTargets { url resourceUrl parameters { name value } } userErrors { field message } } }`,
  { input: [{ filename: nombre, mimeType: mime, resource: 'IMAGE', httpMethod: 'POST', fileSize: String(bytes.length) }] });
if (userErrors(st).length) throw new Error(JSON.stringify(userErrors(st)));
const destino = st.stagedUploadsCreate.stagedTargets[0];

const form = new FormData();
for (const p of destino.parameters) form.append(p.name, p.value);
form.append('file', new Blob([bytes], { type: mime }), nombre);
const r = await fetch(destino.url, { method: 'POST', body: form });
if (!r.ok) throw new Error(`Subida al almacén temporal: HTTP ${r.status} ${(await r.text()).slice(0, 300)}`);

const fc = await adminGraphQL(`mutation($files: [FileCreateInput!]!) { fileCreate(files: $files) {
  files { id fileStatus } userErrors { field message } } }`,
  { files: [{ originalSource: destino.resourceUrl, filename: nombre, contentType: 'IMAGE', alt }] });
if (userErrors(fc).length) throw new Error(JSON.stringify(userErrors(fc)));
const id = fc.fileCreate.files[0].id;

for (let i = 0; i < 20; i++) {
  await new Promise((res) => setTimeout(res, 3000));
  const q = await adminGraphQL(`query($id: ID!) { node(id: $id) { ... on MediaImage { fileStatus image { url width height } } } }`, { id });
  if (q.node.fileStatus === 'READY') {
    console.log(`✅ ${q.node.image.width}x${q.node.image.height} ${q.node.image.url}\n   En el tema: shopify://shop_images/${nombre}`);
    process.exit(0);
  }
  if (q.node.fileStatus === 'FAILED') throw new Error('Shopify no pudo procesar el fichero');
}
console.log(`⚠️ Subido (${id}) pero aún procesándose; revisa Ficheros en el admin.`);
