// Downloads the brand fonts into public/fonts (ignored by Git).
// MangoGrotesque is self-hosted by filmhack.ai; Geist Mono and DSEG7 are OFL fonts served from npm via jsDelivr.
import { mkdir, stat, writeFile } from 'node:fs/promises';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = join(dirname(fileURLToPath(import.meta.url)), '..');

const FONTS = {
  'MangoGrotesque-ExtBdIta.woff2': 'https://filmhack.ai/fonts/MangoGrotesque-ExtBdIta.woff2',
  'GeistMono-Bold.woff2': 'https://cdn.jsdelivr.net/npm/geist@1.7.2/dist/fonts/geist-mono/GeistMono-Bold.woff2',
  'GeistMono-Medium.woff2': 'https://cdn.jsdelivr.net/npm/geist@1.7.2/dist/fonts/geist-mono/GeistMono-Medium.woff2',
  'DSEG7Classic-BoldItalic.woff2': 'https://cdn.jsdelivr.net/npm/dseg@0.46.0/fonts/DSEG7-Classic/DSEG7Classic-BoldItalic.woff2',
};

for (const [name, url] of Object.entries(FONTS)) {
  const target = join(ROOT, 'public/fonts', name);
  const existing = await stat(target).catch(() => null);
  if (existing?.size) {
    console.log(`kept public/fonts/${name}`);
    continue;
  }
  const response = await fetch(url);
  if (!response.ok) throw new Error(`${url} returned ${response.status}`);
  const bytes = Buffer.from(await response.arrayBuffer());
  await mkdir(dirname(target), { recursive: true });
  await writeFile(target, bytes);
  console.log(`saved public/fonts/${name} (${bytes.length} bytes)`);
}
