// Renders the silent film. Each version gets its own file so earlier cuts stay intact.
//
//   node scripts/render.mjs v001            → renders/the-curve-v001.mp4
//   node scripts/render.mjs v001 --concurrency 4
import { spawn } from 'node:child_process';
import { existsSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = join(dirname(fileURLToPath(import.meta.url)), '..');
const [version, ...rest] = process.argv.slice(2);
if (!version || !/^v\d{3}$/.test(version)) throw new Error('Give a version like v001.');
const output = join('renders', `the-curve-${version}.mp4`);
if (existsSync(join(ROOT, output))) throw new Error(`${output} exists; pick a new version.`);
const concurrencyFlag = rest.indexOf('--concurrency');
const concurrency = concurrencyFlag >= 0 ? rest[concurrencyFlag + 1] : '4';

const args = [
  'remotion', 'render', 'TheCurve', output, '--muted',
  '--codec=h264', '--crf=16', '--x264-preset=slow', '--pixel-format=yuv420p', '--color-space=bt709',
  `--concurrency=${concurrency}`, '--gl=angle',
];
const started = Date.now();
await new Promise((resolve, reject) => {
  const p = spawn('npx', args, { cwd: ROOT, stdio: 'inherit' });
  p.on('close', (code) => (code === 0 ? resolve() : reject(new Error(`remotion exited ${code}`))));
});
console.log(`film → ${join(ROOT, output)} (${((Date.now() - started) / 1000).toFixed(0)} s)`);
