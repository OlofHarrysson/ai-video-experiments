// Renders stills from one bundle, then a labelled contact sheet.
//
//   node scripts/stills.mjs 2 8.5 14 21            seconds → renders/stills/t02.00.png …, sheet.png
//   node scripts/stills.mjs --out renders/look 3 20 40
import { bundle } from '@remotion/bundler';
import { openBrowser, renderStill, selectComposition } from '@remotion/renderer';
import { spawn } from 'node:child_process';
import { mkdir } from 'node:fs/promises';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = join(dirname(fileURLToPath(import.meta.url)), '..');
const args = process.argv.slice(2);
let outDir = join(ROOT, 'renders/stills');
let scale = 1;
const times = [];
for (let i = 0; i < args.length; i++) {
  if (args[i] === '--out') outDir = join(ROOT, args[++i]);
  else if (args[i] === '--scale') scale = Number(args[++i]);
  else times.push(Number(args[i]));
}
if (times.length === 0) throw new Error('Give one or more times in seconds.');

const chromiumOptions = { gl: 'angle' };
await mkdir(outDir, { recursive: true });
const serveUrl = await bundle({ entryPoint: join(ROOT, 'src/index.ts'), rspack: true });
const browser = await openBrowser('chrome', { chromiumOptions });
const composition = await selectComposition({ serveUrl, id: 'TheCurve', puppeteerInstance: browser, chromiumOptions });

const files = [];
for (const t of times) {
  const frame = Math.min(composition.durationInFrames - 1, Math.round(t * composition.fps));
  const output = join(outDir, `t${t.toFixed(2).padStart(5, '0')}.png`);
  const started = Date.now();
  await renderStill({ composition, serveUrl, output, frame, puppeteerInstance: browser, chromiumOptions, imageFormat: 'png', scale });
  console.log(`${output}  (frame ${frame}, ${Date.now() - started} ms)`);
  files.push({ output, t });
}
await browser.close({ silent: true });

// Contact sheet: two columns at half size, in the order given (this ffmpeg build has no drawtext).
const run = (cmd, a) =>
  new Promise((resolve, reject) => {
    const p = spawn(cmd, a, { stdio: ['ignore', 'ignore', 'inherit'] });
    p.on('close', (code) => (code === 0 ? resolve() : reject(new Error(`${cmd} exited ${code}`))));
  });
const cols = Math.min(2, files.length);
const rows = Math.ceil(files.length / cols);
const inputs = files.flatMap((f) => ['-i', f.output]);
const labelled = files
  .map(
    (f, i) =>
      `[${i}:v]scale=960:-1[v${i}]`,
  )
  .join(';');
const layout = files.map((_, i) => `${(i % cols) * 960}_${Math.floor(i / cols) * 540}`).join('|');
const pad = rows * cols - files.length;
let filter = labelled;
let stackInputs = files.map((_, i) => `[v${i}]`).join('');
if (pad > 0) {
  filter += `;color=black:s=960x540:d=1[pad]`;
  stackInputs += '[pad]';
}
const sheet = join(outDir, 'sheet.png');
if (files.length === 1) {
  await run('ffmpeg', ['-y', '-loglevel', 'error', ...inputs, '-filter_complex', labelled, '-map', '[v0]', '-frames:v', '1', sheet]);
} else {
  const all = files.length + (pad > 0 ? 1 : 0);
  const fullLayout = pad > 0 ? `${layout}|${(files.length % cols) * 960}_${Math.floor(files.length / cols) * 540}` : layout;
  filter += `;${stackInputs}xstack=inputs=${all}:layout=${fullLayout}[out]`;
  await run('ffmpeg', ['-y', '-loglevel', 'error', ...inputs, '-filter_complex', filter, '-map', '[out]', '-frames:v', '1', sheet]);
}
console.log(`sheet → ${sheet}`);
