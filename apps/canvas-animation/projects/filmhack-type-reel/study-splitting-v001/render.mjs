// node render.mjs <output-dir>: stills, contact sheet and a silent MP4 of the splitting comparison.
import fs from 'node:fs';
import path from 'node:path';
import http from 'node:http';
import { createRequire } from 'node:module';
import { createHash } from 'node:crypto';
import { spawnSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';

const { chromium } = createRequire(new URL('../../../../../.agents/skills/animate/package.json', import.meta.url))('playwright');
const here = path.dirname(fileURLToPath(import.meta.url)), root = path.resolve(here, '..');
const out = path.join(here, process.argv[2] || 'output-01');
if (fs.existsSync(out)) throw new Error('choose a new output directory');
fs.mkdirSync(out, { recursive: true });
const TYPES = { '.html': 'text/html', '.js': 'text/javascript', '.png': 'image/png' };
const server = http.createServer((req, res) => {
  const file = path.join(root, decodeURIComponent(new URL(req.url, 'http://x').pathname));
  if (!file.startsWith(root) || !fs.existsSync(file) || fs.statSync(file).isDirectory()) { res.writeHead(404); return res.end(); }
  res.writeHead(200, { 'Content-Type': TYPES[path.extname(file)] || 'application/octet-stream' }); fs.createReadStream(file).pipe(res);
});
await new Promise(ok => server.listen(0, '127.0.0.1', ok));
const run = args => { const r = spawnSync(args[0], args.slice(1), { encoding: 'utf8' }); if (r.status !== 0) throw new Error(r.stderr); return r.stdout; };
const browser = await chromium.launch();
try {
  const page = await browser.newPage(), errors = [];
  page.on('pageerror', e => errors.push(e.message));
  await page.goto(`http://127.0.0.1:${server.address().port}/${path.basename(here)}/index.html`);
  await page.waitForFunction(() => window.ready, null, { timeout: 120000 });
  const DURATION = await page.evaluate(() => window.DURATION), FPS = 30;
  const frame = async t => Buffer.from(await page.evaluate(t => { window.renderFrame(t); return document.getElementById('c').toDataURL('image/png').split(',')[1]; }, t), 'base64');
  for (const t of [.3, 1.2, 1.45, 1.8, 2.4, 3.8]) fs.writeFileSync(path.join(out, `still-${t.toFixed(2)}.png`), await frame(t));
  const n = Math.round(DURATION * FPS);
  for (let i = 0; i < n; i++) fs.writeFileSync(path.join(out, `f${String(i).padStart(4, '0')}.png`), await frame(i / FPS));
  run(['ffmpeg', '-v', 'error', '-framerate', String(FPS), '-i', path.join(out, 'f%04d.png'), '-c:v', 'libx264', '-crf', '17', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', path.join(out, 'splitting.mp4')]);
  for (const f of fs.readdirSync(out)) if (/^f\d{4}\.png$/.test(f)) fs.unlinkSync(path.join(out, f));
  const hash = b => createHash('sha256').update(b).digest('hex');
  fs.writeFileSync(path.join(out, 'report.json'), JSON.stringify({ errors, deterministic: hash(await frame(2.0)) === hash(await frame(2.0)), sources: { 'main.js': hash(fs.readFileSync(path.join(here, 'main.js'))) } }, null, 2));
  console.log(JSON.stringify({ errors, out }));
  if (errors.length) process.exitCode = 1;
} finally { await browser.close(); server.close(); }
