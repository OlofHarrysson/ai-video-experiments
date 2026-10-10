// Render the motion proof deterministically: node render.mjs <output-dir> [--movie]
import fs from 'node:fs';
import path from 'node:path';
import http from 'node:http';
import { createRequire } from 'node:module';
import { createHash } from 'node:crypto';
import { spawnSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';

const { chromium } = createRequire(new URL('../../../../../.agents/skills/animate/package.json', import.meta.url))('playwright');
const here = path.dirname(fileURLToPath(import.meta.url)), root = path.resolve(here, '..');
const outName = process.argv[2] || 'output-01', movie = process.argv.includes('--movie');
const out = path.join(here, outName);
if (fs.existsSync(out)) throw new Error(`${outName} exists; choose a new output directory`);
fs.mkdirSync(out, { recursive: true });

const TYPES = { '.html': 'text/html', '.js': 'text/javascript', '.mjs': 'text/javascript', '.json': 'application/json', '.ttf': 'font/ttf', '.png': 'image/png' };
const server = http.createServer((req, res) => {
  const file = path.join(root, decodeURIComponent(new URL(req.url, 'http://x').pathname));
  if (!file.startsWith(root) || !fs.existsSync(file) || fs.statSync(file).isDirectory()) { res.writeHead(404); return res.end(); }
  res.writeHead(200, { 'Content-Type': TYPES[path.extname(file)] || 'application/octet-stream' }); fs.createReadStream(file).pipe(res);
});
await new Promise(ok => server.listen(0, '127.0.0.1', ok));
const url = `http://127.0.0.1:${server.address().port}/proof-v002/index.html?t=0`;
const run = args => { const r = spawnSync(args[0], args.slice(1), { encoding: 'utf8' }); if (r.status !== 0) throw new Error(r.stderr); return r.stdout; };

const browser = await chromium.launch();
try {
  const page = await browser.newPage({ viewport: { width: 540, height: 960 } }), errors = [];
  page.on('pageerror', e => errors.push(e.message)); page.on('console', m => m.type() === 'error' && errors.push(m.text()));
  await page.goto(url); await page.waitForFunction(() => window.ready, null, { timeout: 30000 });
  const { DURATION, TIMES } = await page.evaluate(() => ({ DURATION: window.DURATION, TIMES: window.TIMES }));
  const frame = async t => Buffer.from(await page.evaluate(t => { window.renderFrame(t); return document.getElementById('c').toDataURL('image/png').split(',')[1]; }, t), 'base64');
  const FPS = 30, hash = b => createHash('sha256').update(b).digest('hex');

  const stills = [0.2, .87, .9, .94, 1.0, 1.15, 1.32, 1.6, 1.9, 2.17, 2.25, 2.33, 2.45, 2.62, 3.2, 3.6, 3.75, 4.0, 4.3, 4.52, 4.62, 4.75, 4.95, 5.3, 5.9];
  for (const t of stills) fs.writeFileSync(path.join(out, `still-${t.toFixed(2)}.png`), await frame(t));
  run(['ffmpeg', '-v', 'error', '-pattern_type', 'glob', '-i', path.join(out, 'still-*.png'), '-vf', 'scale=216:384,tile=9x3:padding=4:color=0x202020', '-frames:v', '1', path.join(out, 'contact.png')]);
  const deterministic = hash(await frame(2.6)) === hash(await frame(2.6));

  let video = null;
  if (movie) {
    const n = Math.round(DURATION * FPS);
    for (let i = 0; i < n; i++) { fs.writeFileSync(path.join(out, `f${String(i).padStart(4, '0')}.png`), await frame(i / FPS)); if (i % 30 === 0) console.log(`frame ${i}/${n}`); }
    fs.writeFileSync(path.join(out, 'scratch.wav'), scratchScore(DURATION, TIMES));
    run(['ffmpeg', '-v', 'error', '-framerate', String(FPS), '-i', path.join(out, 'f%04d.png'), '-i', path.join(out, 'scratch.wav'),
      '-c:v', 'libx264', '-crf', '16', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '192k', '-shortest', '-movflags', '+faststart', path.join(out, 'proof.mp4')]);
    for (const f of fs.readdirSync(out)) if (/^f\d{4}\.png$/.test(f)) fs.unlinkSync(path.join(out, f));
    video = JSON.parse(run(['ffprobe', '-v', 'quiet', '-show_entries', 'stream=codec_type,width,height,r_frame_rate:format=duration', '-of', 'json', path.join(out, 'proof.mp4')]));
  }
  const sources = Object.fromEntries(['index.html', 'render.mjs', ...fs.readdirSync(path.join(here, 'src')).map(f => 'src/' + f)].map(f => [f, hash(fs.readFileSync(path.join(here, f)))]));
  const report = { errors, deterministic, duration: DURATION, times: TIMES, video, sources, chromium: browser.version() };
  fs.writeFileSync(path.join(out, 'report.json'), JSON.stringify(report, null, 2));
  console.log(JSON.stringify({ errors, deterministic, out }, null, 2));
  if (errors.length) process.exitCode = 1;
} finally { await browser.close(); server.close(); }

// Scratch beat for judging timing only; the real track comes from the music workbench.
function scratchScore(dur, T) {
  const sr = 44100, n = Math.ceil((dur + .5) * sr), a = new Float32Array(n), beat = 60 / 140;
  let seed = 3; const rnd = () => (seed = (seed * 16807) % 2147483647) / 2147483647 - .5;
  const add = (t0, fn, len) => { const i0 = Math.round(t0 * sr); for (let i = 0; i < len * sr && i0 + i < n; i++) a[i0 + i] += fn(i / sr); };
  const kick = t => Math.sin(2 * Math.PI * (48 * t + 110 * (1 - Math.exp(-t * 28)) / 28)) * Math.exp(-t * 9) * .9;
  const hat = t => rnd() * Math.exp(-t * 70) * .12;
  const stab = f => t => (Math.sin(2 * Math.PI * f * t) * .5 + Math.sin(2 * Math.PI * f * 1.5 * t) * .3 + rnd() * .5) * Math.exp(-t * 7) * .55;
  const chime = t => (Math.sin(2 * Math.PI * 1760 * t) + .5 * Math.sin(2 * Math.PI * 2640 * t)) * Math.exp(-t * 5) * .12;
  for (let t = 0; t < dur; t += beat) { add(t, kick, .4); add(t + beat / 2, hat, .08); }
  add(T.yes, stab(220), .6); add(T.yes + beat, stab(330), .3);
  add(T.marquee, stab(262), .6); [1, 2].forEach(k => add(T.marquee + k * beat, chime, .4));
  add(T.alone, chime, .6); add(T.crews, stab(196), .7);
  const peak = a.reduce((m, v) => Math.max(m, Math.abs(v)), 0) || 1;
  const buf = Buffer.alloc(44 + n * 2);
  buf.write('RIFF', 0); buf.writeUInt32LE(36 + n * 2, 4); buf.write('WAVEfmt ', 8); buf.writeUInt32LE(16, 16); buf.writeUInt16LE(1, 20); buf.writeUInt16LE(1, 22);
  buf.writeUInt32LE(sr, 24); buf.writeUInt32LE(sr * 2, 28); buf.writeUInt16LE(2, 32); buf.writeUInt16LE(16, 34); buf.write('data', 36); buf.writeUInt32LE(n * 2, 40);
  for (let i = 0; i < n; i++) buf.writeInt16LE(Math.round(a[i] / peak * .85 * 32767), 44 + i * 2);
  return buf;
}
