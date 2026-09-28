/**
 * scripts/test_conexion.mjs — comprueba que la Admin API responde y muestra los datos clave de la tienda.
 * Uso: npm run test:shopify   (o: node scripts/test_conexion.mjs)
 * Credencial: sesión de la CLI de Shopify (ver scripts/admin.mjs).
 */
import { adminGraphQL, STORE } from './admin.mjs';

const QUERY = `{
  shop {
    name myshopifyDomain currencyCode ianaTimezone taxesIncluded
    primaryDomain { url }
    plan { publicDisplayName partnerDevelopment }
  }
  shopLocales { locale primary published }
  productsCount { count }
  collectionsCount { count }
  publications(first: 10) { nodes { id catalog { title } } }
  locations(first: 5) { nodes { id name } }
}`;

try {
  console.log(`\n🔌 Conectando a ${STORE}…\n`);
  const d = await adminGraphQL(QUERY);
  const s = d.shop;
  const idioma = d.shopLocales.find((l) => l.primary)?.locale;
  console.log(`✅ ${s.name.trim()} (${s.myshopifyDomain})`);
  console.log(`   Web:          ${s.primaryDomain?.url}`);
  console.log(`   Plan:         ${s.plan.publicDisplayName}${s.plan.partnerDevelopment ? '  ⚠️ tienda de DESARROLLO (no cobra)' : ''}`);
  console.log(`   Moneda:       ${s.currencyCode} · IVA incluido: ${s.taxesIncluded ? 'sí' : 'NO'}`);
  console.log(`   Zona horaria: ${s.ianaTimezone}${s.ianaTimezone !== 'Europe/Madrid' ? '  ⚠️ debería ser Europe/Madrid' : ''}`);
  console.log(`   Idioma:       ${idioma}${idioma !== 'es' ? '  ⚠️ debería ser es' : ''}`);
  console.log(`   Productos:    ${d.productsCount.count} · Colecciones: ${d.collectionsCount.count}`);
  for (const p of d.publications.nodes) console.log(`   Canal:        ${p.catalog?.title} → ${p.id}`);
  for (const l of d.locations.nodes) console.log(`   Ubicación:    ${l.name} → ${l.id}`);
  console.log('');
} catch (e) {
  console.error('❌ No se pudo conectar:\n' + e.message);
  process.exit(1);
}
