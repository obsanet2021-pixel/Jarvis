/**
 * JARVIS — Social Account Connection Helper
 *
 * Checks which social accounts are already connected and reports what remains.
 * Since Twitter/X and most other platforms require custom OAuth credentials
 * registered by the developer, there is no fully automated flow — the script
 * directs you to the Composio dashboard where the OAuth handoff happens.
 *
 * Usage: npm run connect
 */

import 'dotenv/config';
import { Composio } from '@composio/core';

const COMPOSIO_API_KEY = process.env.COMPOSIO_API_KEY;

if (!COMPOSIO_API_KEY) {
  console.error('ERROR: COMPOSIO_API_KEY not set in .env file');
  process.exit(1);
}

const APPS = [
  { slug: 'twitter',  label: 'Twitter / X' },
  { slug: 'linkedin', label: 'LinkedIn' },
  { slug: 'facebook', label: 'Facebook' },
  { slug: 'instagram',label: 'Instagram' },
];

/**
 * Check whether any connected account matches one of the given slugs.
 */
async function findConnected(composio, targetSlugs) {
  try {
    const list = await composio.connectedAccounts.list();
    return (list.items || []).filter(
      (a) => targetSlugs.includes((a.appSlug || a.app)?.toLowerCase())
    );
  } catch (_) {
    return [];
  }
}

async function main() {
  console.log('🔗 JARVIS — Connect Social Accounts\n');
  console.log(`Composio API key: ${COMPOSIO_API_KEY.slice(0, 8)}...${COMPOSIO_API_KEY.slice(-4)}\n`);

  const composio = new Composio({ apiKey: COMPOSIO_API_KEY });
  const connected = await findConnected(composio, APPS.map((a) => a.slug));
  const connectedSlugs = new Set(connected.map((a) => (a.appSlug || a.app)?.toLowerCase()));

  const stillNeeded = APPS.filter((a) => !connectedSlugs.has(a.slug));

  if (connected.length > 0) {
    console.log('Already connected:');
    for (const acc of connected) {
      const label = APPS.find((a) => a.slug === (acc.appSlug || acc.app))?.label || acc.appSlug;
      const user  = acc.userName || acc.email || acc.username || '—';
      console.log(`  ✅ ${label}  →  ${user}`);
    }
    console.log();
  }

  if (stillNeeded.length === 0) {
    console.log('All social accounts are connected! Run "npm run socials" to start querying.');
    return;
  }

  console.log('Not yet connected:');
  for (const { slug, label } of stillNeeded) {
    console.log(`  ⬜ ${label} (${slug})`);
  }
  console.log();

  console.log('━━━ HOW TO CONNECT ━━━\n');
  console.log('Most social platforms require you to own an OAuth app registered with them.');
  console.log('Composio handles the OAuth exchange once your app is registered.\n');

  console.log('Step 1 — Register developer apps (one-time, free):');
  console.log('  • Twitter/X : https://developer.twitter.com/en/portal/dashboard');
  console.log('  • LinkedIn  : https://www.linkedin.com/developers/apps');
  console.log('  • Facebook  : https://developers.facebook.com/apps');
  console.log('  • Instagram : via Facebook Developer (same page as above)\n');

  console.log('Step 2 — Add credentials to Composio:');
  console.log('  1. Open https://app.composio.dev');
  console.log('  2. Go to Settings → API Keys / Auth Configs');
  console.log('  3. For each platform, paste your Client ID and Client Secret');
  console.log('  4. Save\n');

  console.log('Step 3 — Authorize your accounts:');
  console.log('  1. In Composio dashboard, go to Integrations');
  console.log('  2. Click "Connect" next to each platform');
  console.log('  3. Complete the OAuth redirect in your browser');
  console.log('  4. Return here and run: npm run socials\n');

  console.log('After connecting all accounts, the socials script will show live data.');
}

main().catch((err) => {
  console.error('\n❌ Fatal:', err.message);
  process.exit(1);
});
