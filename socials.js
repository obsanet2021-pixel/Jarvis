/**
 * JARVIS Social Media Integration via Composio — READ-ONLY
 *
 * Shows connected social accounts and exposes read-only capabilities.
 *
 * Usage: npm run socials
 */

import 'dotenv/config';
import { Composio } from '@composio/core';

const COMPOSIO_API_KEY = process.env.COMPOSIO_API_KEY;
const OPENAI_API_KEY   = process.env.OPENAI_API_KEY ?? '';

if (!COMPOSIO_API_KEY) {
  console.error('ERROR: COMPOSIO_API_KEY not set in .env file');
  process.exit(1);
}

// Native platform actions we care about (read-only by name convention)
const SOCIAL_APPS = [
  { slug: 'twitter',  label: 'Twitter / X', nativePrefix: ['TWITTER_', 'X_'] },
  { slug: 'linkedin', label: 'LinkedIn',    nativePrefix: ['LINKEDIN_'] },
  { slug: 'facebook', label: 'Facebook',    nativePrefix: ['FACEBOOK_'] },
  { slug: 'instagram',label: 'Instagram',   nativePrefix: ['INSTAGRAM_'] },
];

async function fetchAppTools(composio, appSlug, nativePrefixes) {
  try {
    const allSlugs = await composio.tools.getToolsEnum(appSlug);
    return allSlugs.filter((slug) => {
      if (!slug || typeof slug !== 'string') return false;
      // Keep only tools whose slug starts with one of the known native prefixes
      return nativePrefixes.some((p) => slug.startsWith(p));
    });
  } catch (err) {
    console.log(`   ⚠️  Could not list tools for ${appSlug}: ${err.message}`);
    return [];
  }
}

async function executeTool(composio, appSlug, toolSlug, params = {}) {
  try {
    return await composio.tools.execute({
      appSlug,
      actionName: toolSlug,
      params,
    });
  } catch (err) {
    return { _error: err.message };
  }
}

async function main() {
  console.log('🤖 JARVIS Social Media Integration\n');
  console.log(`Composio API key: ${COMPOSIO_API_KEY.slice(0, 8)}...${COMPOSIO_API_KEY.slice(-4)}`);
  console.log(`OpenAI API key:   ${OPENAI_API_KEY ? OPENAI_API_KEY.slice(0, 8) + '...' + OPENAI_API_KEY.slice(-4) : '(not set)'}`);
  console.log();

  const composio = new Composio({ apiKey: COMPOSIO_API_KEY });

  // ── Connected accounts ────────────────────────────────────────────────────────
  console.log('📱 Connected social accounts:\n');

  let connected = [];
  try {
    const acctList = await composio.connectedAccounts.list();
    connected = (acctList.items || []).filter(
      (acc) => SOCIAL_APPS.some((a) => (a.appSlug || a.app)?.toLowerCase() === acc.appSlug?.toLowerCase())
    );
  } catch (_) {}

  if (connected.length === 0) {
    console.log('   No social media accounts connected yet.\n');
    console.log('   Run "npm run connect" to begin the authorization flow.\n');
  } else {
    for (const acc of connected) {
      const appMeta = SOCIAL_APPS.find((a) => (a.slug) === (acc.appSlug || acc.app)?.toLowerCase());
      const appName = appMeta?.label || acc.appName || acc.appSlug || '?';
      const userName = acc.userName || acc.email || acc.username || '—';
      const status = acc.status || acc.connectionStatus || 'unknown';
      console.log(`  • ${appName.padEnd(16)}  ${userName.padEnd(24)}  (${status})`);
    }
    console.log();
  }

  // ── Available read-only tools per platform ────────────────────────────────────
  console.log('🔧 Read-only tools available:\n');

  let totalTools = 0;
  for (const { slug, label, nativePrefix } of SOCIAL_APPS) {
    const slugs = await fetchAppTools(composio, slug, nativePrefix);
    const count = slugs.length;
    totalTools += count;
    console.log(`  ${label}: ${count} native tools`);
    for (const s of slugs.slice(0, 5)) {
      console.log(`     – ${s}`);
    }
    if (count > 5) console.log(`     … and ${count - 5} more`);
    console.log();
  }

  // ── Demo query if accounts are connected ──────────────────────────────────────
  if (connected.length > 0 && totalTools > 0) {
    console.log('🎯 Running sample read-only queries…\n');

    for (const acc of connected) {
      const appMeta = SOCIAL_APPS.find((a) => a.slug === (acc.appSlug || acc.app)?.toLowerCase());
      if (!appMeta) continue;
      const label = appMeta.label;
      const slugs = await fetchAppTools(composio, appMeta.slug, appMeta.nativePrefix);
      // Pick first GET or LIST tool for the demo
      const sampleSlug = slugs.find((s) => /^GET_|^LIST_/i.test(s)) || slugs[0];
      if (!sampleSlug) continue;

      const result = await executeTool(composio, appMeta.slug, sampleSlug, {});
      if (result?._error) {
        console.log(`  ❌ ${label}/${sampleSlug}: ${result._error}\n`);
      } else {
        const summary = JSON.stringify(result).slice(0, 200);
        console.log(`  ✓ ${label}/${sampleSlug}: ${summary}…\n`);
      }
    }
  }

  if (OPENAI_API_KEY && totalTools > 0) {
    console.log('ℹ️  Conversation agent ready when OPENAI_API_KEY is set in .env.\n');
  }

  console.log('✅ Done.');
}

main().catch((err) => {
  console.error('\n❌ Fatal:', err.message);
  process.exit(1);
});

