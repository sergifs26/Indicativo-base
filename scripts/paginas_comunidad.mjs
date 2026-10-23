/**
 * scripts/paginas_comunidad.mjs — páginas «Nuestra comunidad» y «Comparte tu estación» (23/10/2026).
 *
 * Texto de «Nuestra comunidad» en contenido/nuestra-comunidad.html: el de «La clave de
 * IndicativoBase.doc» del cliente, pulido y escrito como intención donde habla de compromisos que
 * aún no ha confirmado (compras agrupadas, donaciones). Sin el plazo de 5 días ni la entrega en
 * club/locker hasta que los confirme. «Nuestra comunidad» usa la plantilla `page.comunidad` (texto +
 * galería de aficiones con fotos y el cierre «No compres simplemente. Forma parte.», que por eso ya
 * no está en el HTML) y «Comparte tu estación» la `page.comparte` (formulario en
 * sections/comparte-estacion.liquid): subir el tema antes.
 * Idempotente por handle: crea o actualiza título, cuerpo y plantilla; deja las páginas publicadas.
 *
 * Uso:
 *   node scripts/paginas_comunidad.mjs            # dry-run
 *   node scripts/paginas_comunidad.mjs --apply
 */
import { readFileSync } from 'node:fs';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
import { adminGraphQL, userErrors } from './admin.mjs';

const RAIZ = join(dirname(fileURLToPath(import.meta.url)), '..');
const APPLY = process.argv.includes('--apply');
const PAGINAS = [
  { handle: 'nuestra-comunidad', title: 'Nuestra comunidad', body: readFileSync(join(RAIZ, 'contenido', 'nuestra-comunidad.html'), 'utf8'), templateSuffix: 'comunidad' },
  { handle: 'comparte-tu-estacion', title: 'Comparte tu estación', body: '', templateSuffix: 'comparte' },
];

const alias = PAGINAS.map((p, i) => `p${i}: pages(first: 1, query: ${JSON.stringify(`handle:${p.handle}`)}) { nodes { id handle title isPublished templateSuffix } }`).join('\n');
const estado = await adminGraphQL(`query { ${alias} }`);

console.log(`\n${APPLY ? '🚀 APPLY' : '🔍 DRY-RUN'} — páginas de la comunidad\n`);
PAGINAS.forEach((p, i) => {
  const hoy = estado[`p${i}`].nodes.find((n) => n.handle === p.handle);
  console.log(`${hoy ? '✏️  actualizar' : '➕ crear    '} /pages/${p.handle} «${p.title}»${p.templateSuffix ? ` · plantilla page.${p.templateSuffix}` : ''} · ${p.body.length} caracteres`);
});
if (!APPLY) { console.log('\n(dry-run — nada escrito. Añade --apply para aplicar)\n'); process.exit(0); }

for (const [i, p] of PAGINAS.entries()) {
  const hoy = estado[`p${i}`].nodes.find((n) => n.handle === p.handle);
  const page = { title: p.title, body: p.body, templateSuffix: p.templateSuffix, isPublished: true };
  const r = hoy
    ? await adminGraphQL(`mutation($id: ID!, $page: PageUpdateInput!) { pageUpdate(id: $id, page: $page) { page { id handle } userErrors { field message } } }`, { id: hoy.id, page })
    : await adminGraphQL(`mutation($page: PageCreateInput!) { pageCreate(page: $page) { page { id handle } userErrors { field message } } }`, { page: { handle: p.handle, ...page } });
  const res = hoy ? r.pageUpdate : r.pageCreate;
  if (userErrors(r).length) { console.error(`❌ ${p.handle}:`, userErrors(r)); process.exitCode = 1; continue; }
  console.log(`✅ /pages/${res.page.handle} → ${res.page.id}`);
}
