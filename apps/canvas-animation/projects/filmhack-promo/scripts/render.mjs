// Renders the film headlessly: Vite serves the page, Chrome draws each frame and
// synthesises the score, ffmpeg encodes H.264 and loudness-normalises the audio.
//
//   node scripts/render.mjs                      full film → renders/filmhack-reel-v1.mp4
//   node scripts/render.mjs --out renders/x.mp4  choose the output
//   node scripts/render.mjs --stills             key moments → renders/stills/ + contact sheet
//   node scripts/render.mjs --stills 3.9,21.2    specific times in seconds
//   node scripts/render.mjs --audio              soundtrack only → renders/soundtrack-raw.wav
import { spawn } from 'node:child_process';
import { once } from 'node:events';
import { mkdir, rm, writeFile } from 'node:fs/promises';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { chromium } from 'playwright-core';
import { createServer } from 'vite';

const ROOT = join(dirname(fileURLToPath(import.meta.url)), '..');
const W = 1080;
const H = 1920;
const FPS = 30;
// Headroom below -1 dBTP leaves room for Instagram's own AAC re-encode.
const LOUDNESS = 'I=-14:TP=-1.5:LRA=11';
const COVER_AT = 26.0;
const KEY_MOMENTS = [0.1, 0.3, 0.7, 1.9, 3.1, 3.8, 5.2, 6.4, 7.3, 8.6, 10.4, 12.3, 14.6, 15.9, 16.7, 17.6, 19.6, 21.0, 26.0, 26.9, 29.3, 29.9];

const args = process.argv.slice(2);
const option = (name) => {
  const i = args.indexOf(name);
  if (i < 0) return undefined;
  const next = args[i + 1];
  return next && !next.startsWith('--') ? next : true;
};
const stills = option('--stills');
const audioOnly = option('--audio');
const out = join(ROOT, option('--out') ?? 'renders/filmhack-reel-v1.mp4');

let frameSink = null;
let audioBytes = null;

/** Receives raw frames and the soundtrack that the page POSTs back. */
function bridge() {
  return {
    name: 'render-bridge',
    configureServer(server) {
      server.middlewares.use(async (req, res, next) => {
        if (req.method !== 'POST' || !req.url?.startsWith('/__')) return next();
        const chunks = [];
        for await (const chunk of req) chunks.push(chunk);
        const body = Buffer.concat(chunks);
        try {
          if (req.url.startsWith('/__frame')) await frameSink(body);
          else if (req.url.startsWith('/__audio')) audioBytes = body;
          res.statusCode = 204;
          res.end();
        } catch (error) {
          res.statusCode = 500;
          res.end(String(error));
        }
      });
    },
  };
}

function ffmpeg(argv, { capture = false } = {}) {
  return new Promise((resolve, reject) => {
    const proc = spawn('ffmpeg', ['-hide_banner', '-y', ...argv], { stdio: ['ignore', 'ignore', 'pipe'] });
    let stderr = '';
    proc.stderr.on('data', (d) => (stderr += d));
    proc.on('close', (code) => (code === 0 ? resolve(stderr) : reject(new Error(`ffmpeg exited ${code}\n${stderr.slice(-2000)}`))));
  });
}

async function renderStills(page, times) {
  const dir = join(ROOT, 'renders/stills');
  await rm(dir, { recursive: true, force: true });
  await mkdir(dir, { recursive: true });
  for (const [i, t] of times.entries()) {
    const dataUrl = await page.evaluate((time) => window.film.still(time), t);
    const file = join(dir, `${String(i).padStart(2, '0')}-${t.toFixed(2)}s.png`);
    await writeFile(file, Buffer.from(dataUrl.split(',')[1], 'base64'));
  }
  const cols = Math.min(6, times.length);
  const rows = Math.ceil(times.length / cols);
  await ffmpeg(['-pattern_type', 'glob', '-i', join(dir, '*.png'), '-vf', `scale=270:-1,tile=${cols}x${rows}:padding=6:color=0x222222`, '-frames:v', '1', join(dir, 'contact-sheet.png')]);
  console.log(`stills → ${dir}`);
}

async function renderFilm(page) {
  await mkdir(dirname(out), { recursive: true });
  const video = join(ROOT, 'renders/.video.mp4');
  const rawWav = join(ROOT, 'renders/.soundtrack-raw.wav');
  const masterWav = out.replace(/\.mp4$/, '.wav');

  await page.evaluate(() => window.film.exportAudio());
  await writeFile(rawWav, audioBytes);

  const encoder = spawn(
    'ffmpeg',
    [
      '-hide_banner', '-y', '-loglevel', 'error',
      '-f', 'rawvideo', '-pix_fmt', 'rgba', '-s', `${W}x${H}`, '-r', String(FPS), '-i', '-',
      '-vf', 'scale=out_color_matrix=bt709:out_range=tv,format=yuv420p',
      '-c:v', 'libx264', '-preset', 'medium', '-crf', '17', '-maxrate', '24M', '-bufsize', '48M', '-profile:v', 'high',
      '-color_primaries', 'bt709', '-color_trc', 'bt709', '-colorspace', 'bt709',
      video,
    ],
    { stdio: ['pipe', 'inherit', 'inherit'] },
  );
  const frameBytes = W * H * 4;
  frameSink = async (buffer) => {
    if (buffer.length !== frameBytes) throw new Error(`frame has ${buffer.length} bytes, expected ${frameBytes}`);
    if (!encoder.stdin.write(buffer)) await once(encoder.stdin, 'drain');
  };
  const started = Date.now();
  const frames = await page.evaluate(() => window.film.frames);
  await page.evaluate(([a, z]) => window.film.exportFrames(a, z), [0, frames]);
  encoder.stdin.end();
  const [code] = await once(encoder, 'close');
  if (code !== 0) throw new Error(`video encoder exited ${code}`);
  console.log(`encoded ${frames} frames in ${((Date.now() - started) / 1000).toFixed(1)} s`);

  const analysis = await ffmpeg(['-i', rawWav, '-af', `loudnorm=${LOUDNESS}:print_format=json`, '-f', 'null', '-']);
  const m = JSON.parse(analysis.slice(analysis.lastIndexOf('{'), analysis.lastIndexOf('}') + 1));
  console.log(`raw mix: ${m.input_i} LUFS, true peak ${m.input_tp} dBTP, LRA ${m.input_lra}`);
  const measured = `measured_I=${m.input_i}:measured_TP=${m.input_tp}:measured_LRA=${m.input_lra}:measured_thresh=${m.input_thresh}:offset=${m.target_offset}`;
  await ffmpeg(['-i', rawWav, '-af', `loudnorm=${LOUDNESS}:${measured}:linear=true`, '-ar', '48000', '-c:a', 'pcm_s24le', masterWav]);

  await ffmpeg(['-i', video, '-i', masterWav, '-map', '0:v', '-map', '1:a', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '256k', '-ar', '48000', '-shortest', '-movflags', '+faststart', out]);
  await ffmpeg(['-ss', String(COVER_AT), '-i', out, '-frames:v', '1', '-q:v', '2', out.replace(/\.mp4$/, '-cover.jpg')]);
  await rm(video);
  await rm(rawWav);
  console.log(`film → ${out}`);
}

// No watcher or hot reload: an edit mid-render must not reload the page and abort the export.
const server = await createServer({ root: ROOT, logLevel: 'warn', server: { port: 5191, hmr: false, watch: null }, plugins: [bridge()] });
await server.listen();
const browser = await chromium.launch({ channel: 'chrome', headless: true });
try {
  const page = await browser.newPage({ viewport: { width: 540, height: 1000 } });
  page.on('console', (m) => console.log(`[page] ${m.text()}`));
  page.on('pageerror', (e) => console.error(`[page error] ${e.message}`));
  await page.goto(`${server.resolvedUrls.local[0]}?export=1`);
  await page.waitForFunction(() => window.film?.ready === true, null, { timeout: 180_000 });
  if (stills) {
    await renderStills(page, stills === true ? KEY_MOMENTS : String(stills).split(',').map(Number));
  } else if (audioOnly) {
    const file = join(ROOT, 'renders/soundtrack-raw.wav');
    await page.evaluate(() => window.film.exportAudio());
    await writeFile(file, audioBytes);
    console.log(`soundtrack → ${file}`);
  } else {
    await renderFilm(page);
  }
} finally {
  await browser.close();
  await server.close();
}
