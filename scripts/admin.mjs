/**
 * scripts/admin.mjs — Admin API GraphQL de Indicativo Base a través de la CLI de Shopify.
 *
 * La CLI guarda su propio token por tienda, así que aquí no hay credenciales.
 * Una vez por máquina (abre el navegador para aprobar):
 *   shopify store auth --store indicativo-base.myshopify.com \
 *     --scopes read_products,write_products,read_publications,write_publications,read_online_store_navigation,write_online_store_navigation,read_content,write_content,read_themes,write_themes,read_files,write_files,read_inventory,write_inventory,read_locales
 *
 * Uso desde otro script:
 *   import { adminGraphQL, STORE } from './admin.mjs';
 *   const d = await adminGraphQL(`{ shop { name } }`);
 *
 * Config opcional en .env: SHOPIFY_STORE, SHOPIFY_API_VERSION.
 */
import { readFileSync, writeFileSync, existsSync, unlinkSync, mkdirSync } from 'node:fs';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
import { execSync } from 'node:child_process';

const AQUI = dirname(fileURLToPath(import.meta.url));
const RAIZ = join(AQUI, '..');

function leerEnv() {
  const env = {};
  const f = join(RAIZ, '.env');
  if (!existsSync(f)) return env;
  for (const linea of readFileSync(f, 'utf8').split(/\r?\n/)) {
    const m = linea.match(/^\s*([A-Z0-9_]+)\s*=\s*(.*?)\s*$/);
    if (m && !linea.trim().startsWith('#')) env[m[1]] = m[2].replace(/^["']|["']$/g, '');
  }
  return env;
}

const env = leerEnv();
export const STORE = env.SHOPIFY_STORE || 'indicativo-base.myshopify.com';
export const API_VERSION = env.SHOPIFY_API_VERSION || '';
export const OUT = join(AQUI, 'out');

// La ruta del proyecto lleva espacios ("Pagina indicativobase"): comillas al pasar ficheros a la CLI.
export const q = (s) => `"${s}"`;

// En Windows `shopify` es un .cmd y solo se puede lanzar a través de la shell: se pasa la orden
// ya montada (las rutas con espacios van entre comillas con q()).
export function shopifyCli(args, { heredar = false } = {}) {
  return execSync(['shopify', ...args].join(' '), {
    stdio: heredar ? 'inherit' : ['ignore', 'pipe', 'pipe'],
    encoding: 'utf8',
  });
}

const esperar = (ms) => new Promise((r) => setTimeout(r, ms));

/** Ejecuta una query o mutación. Devuelve el objeto `data`. Lanza si hay `errors`. */
export async function adminGraphQL(query, variables = {}) {
  mkdirSync(OUT, { recursive: true });
  const id = `${process.pid}_${Date.now()}`;
  const fq = join(OUT, `_q_${id}.graphql`);
  const fv = join(OUT, `_v_${id}.json`);
  const fo = join(OUT, `_o_${id}.json`);
  writeFileSync(fq, query); // sin BOM: la CLI rechaza ficheros con BOM
  writeFileSync(fv, JSON.stringify(variables));

  const args = ['store', 'execute', '-s', STORE, '--query-file', q(fq), '--variable-file', q(fv), '--output-file', q(fo)];
  if (/^\s*mutation/.test(query)) args.push('--allow-mutations');
  if (API_VERSION) args.push('--version', API_VERSION);

  // La CLI a veces corta la conexión ("socket disconnected"): reintentos con espera creciente.
  let fallo = null;
  for (let intento = 1; intento <= 4; intento++) {
    try {
      shopifyCli(args);
      fallo = null;
      break;
    } catch (e) {
      fallo = e;
      await esperar(1500 * intento);
    }
  }
  try {
    if (fallo) {
      const detalle = `${fallo.stderr || ''}${fallo.stdout || ''}`.trim().split('\n').slice(-5).join('\n');
      throw new Error(`La CLI de Shopify falló 4 veces.\n${detalle}\n` +
        '¿Falta autenticar? → shopify store auth --store ' + STORE + ' --scopes ...');
    }
    const res = JSON.parse(readFileSync(fo, 'utf8'));
    if (res.errors) throw new Error('Errores de la Admin API: ' + JSON.stringify(res.errors).slice(0, 500));
    return res.data ?? res; // según versión, la CLI escribe con o sin el envoltorio "data"
  } finally {
    for (const f of [fq, fv, fo]) if (existsSync(f)) unlinkSync(f);
  }
}

/** Devuelve la lista de userErrors de todas las mutaciones de la respuesta (vacía si no hay). */
export function userErrors(data) {
  return Object.values(data || {}).flatMap((v) => v?.userErrors || []);
}
