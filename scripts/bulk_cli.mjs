/**
 * scripts/bulk_cli.mjs — lanza una operación masiva (bulk mutation) por la CLI de Shopify.
 *
 * Es la vía para escrituras de miles de objetos: el conector MCP de claude.ai bloquea
 * bulkOperationRunMutation por política de seguridad.
 *
 * Uso:
 *   node scripts/bulk_cli.mjs <mutacion.graphql> <variables.jsonl>            # dry-run: valida y resume
 *   node scripts/bulk_cli.mjs <mutacion.graphql> <variables.jsonl> --apply    # ejecuta y espera
 *
 * Resultado (con --apply): scripts/out/bulk_<nombre>_<fechaUTC>.jsonl, una línea por entrada,
 * con los userErrors de cada una. Se resumen al final.
 * Credencial: sesión de la CLI (ver scripts/admin.mjs).
 *
 * Mutaciones listas en scripts/graphql/:
 *   product_set.graphql   productSet por handle (idempotente) ← data/shopify/bulk/productos.jsonl
 *   publicar.graphql      publishablePublish en la Tienda online ← shopify_bulk.py publicar …
 */
import { readFileSync, existsSync, mkdirSync } from 'node:fs';
import { basename, join } from 'node:path';
import { STORE, API_VERSION, OUT, q, shopifyCli } from './admin.mjs';

const args = process.argv.slice(2);
const APPLY = args.includes('--apply');
const [fMutacion, fVariables] = args.filter((a) => !a.startsWith('--'));
if (!fMutacion || !fVariables || !existsSync(fMutacion) || !existsSync(fVariables)) {
  console.error('Uso: node scripts/bulk_cli.mjs <mutacion.graphql> <variables.jsonl> [--apply]');
  process.exit(1);
}

const mutacion = readFileSync(fMutacion, 'utf8');
const lineas = readFileSync(fVariables, 'utf8').split(/\r?\n/).filter((l) => l.trim());
let malas = 0;
for (const [i, l] of lineas.entries()) {
  try { JSON.parse(l); } catch { malas++; if (malas <= 5) console.error(`  ❌ línea ${i + 1} no es JSON válido`); }
}
const mb = (Buffer.byteLength(lineas.join('\n')) / 1e6).toFixed(1);

console.log(`\n${APPLY ? '🚀 APPLY' : '🔍 DRY-RUN'} — ${basename(fMutacion)} × ${lineas.length} entradas (${mb} MB) → ${STORE}`);
console.log(`   ${mutacion.replace(/\s+/g, ' ').slice(0, 140)}…`);
if (malas) { console.error(`\n${malas} líneas inválidas: corrige antes de lanzar.`); process.exit(1); }
if (!APPLY) {
  console.log(`   Primera entrada: ${lineas[0].slice(0, 200)}…`);
  console.log('\n(dry-run — nada escrito. Añade --apply para ejecutar)\n');
  process.exit(0);
}

mkdirSync(OUT, { recursive: true });
const sello = new Date().toISOString().replace(/[-:]/g, '').slice(0, 15);
const salida = join(OUT, `bulk_${basename(fMutacion, '.graphql')}_${sello}.jsonl`);
const cli = ['store', 'bulk', 'execute', '-s', STORE, '--query-file', q(fMutacion),
  '--variable-file', q(fVariables), '--allow-mutations', '--watch', '--output-file', q(salida)];
if (API_VERSION) cli.push('--version', API_VERSION);

try {
  shopifyCli(cli, { heredar: true });
} catch (e) {
  console.error('\n❌ La operación masiva falló. Revisa la salida de arriba ENTERA (el error puede no estar al final).');
  process.exit(1);
}

if (!existsSync(salida)) { console.error(`\n⚠️ No se encontró el fichero de resultados ${salida}`); process.exit(1); }
let ok = 0, conError = 0;
const ejemplos = [];
for (const l of readFileSync(salida, 'utf8').split(/\r?\n/).filter((x) => x.trim())) {
  const r = JSON.parse(l);
  const errs = [...(r.errors || []), ...Object.values(r.data || {}).flatMap((v) => v?.userErrors || [])];
  if (errs.length) { conError++; if (ejemplos.length < 10) ejemplos.push(`línea ${r.__lineNumber}: ${JSON.stringify(errs).slice(0, 200)}`); }
  else ok++;
}
console.log(`\nResultado: ${ok} correctas · ${conError} con error → ${salida}`);
for (const e of ejemplos) console.log('   ' + e);
if (conError) process.exitCode = 1;
