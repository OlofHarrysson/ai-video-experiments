// Downloads brand assets that are not redistributable through Git.
// The display face is self-hosted by filmhack.ai; Geist and DSEG7 come from npm.
import { mkdir, writeFile, stat } from 'node:fs/promises';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = join(dirname(fileURLToPath(import.meta.url)), '..');

const ASSETS = [
  {
    url: 'https://filmhack.ai/fonts/MangoGrotesque-ExtBdIta.woff2',
    path: 'assets/fonts/MangoGrotesque-ExtBdIta.woff2',
  },
];

for (const asset of ASSETS) {
  const target = join(ROOT, asset.path);
  const existing = await stat(target).catch(() => null);
  if (existing?.size) {
    console.log(`kept ${asset.path} (${existing.size} bytes)`);
    continue;
  }
  const response = await fetch(asset.url);
  if (!response.ok) throw new Error(`${asset.url} returned ${response.status}`);
  const bytes = Buffer.from(await response.arrayBuffer());
  await mkdir(dirname(target), { recursive: true });
  await writeFile(target, bytes);
  console.log(`saved ${asset.path} (${bytes.length} bytes)`);
}
