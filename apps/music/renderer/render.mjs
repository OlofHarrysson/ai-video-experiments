import { createHash } from 'node:crypto';
import { createServer } from 'node:http';
import { readFile, readdir, mkdir, writeFile, rename } from 'node:fs/promises';
import { dirname, extname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { parseArgs } from 'node:util';
import { chromium } from 'playwright-core';
import { BUNDLE_SHA256 } from './engine-version.mjs';

const ROOT = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const AUDIO_EXTENSIONS = new Set(['.wav', '.mp3', '.ogg', '.flac', '.m4a']);
const MAX_POLYPHONY = 128;
const sha256 = (bytes) => createHash('sha256').update(bytes).digest('hex');

// Explicit local sample folders keep renders independent of website/profile state.
// Layout: samples/<sound-name>/<files in alphabetical order>.
async function loadSamples(folders) {
  const assets = new Map();
  const map = Object.create(null);
  const records = [];
  for (const folder of folders) {
    for (const entry of (await readdir(folder, { withFileTypes: true })).sort((a, b) => a.name < b.name ? -1 : 1)) {
      if (!entry.isDirectory()) continue;
      const directory = resolve(folder, entry.name);
      const files = (await readdir(directory)).filter((f) => AUDIO_EXTENSIONS.has(extname(f).toLowerCase())).sort();
      if (!files.length) continue;
      if (Object.hasOwn(map, entry.name)) throw new Error(`Duplicate sample name: ${entry.name}`);
      map[entry.name] = [];
      for (const file of files) {
        const path = resolve(directory, file);
        const bytes = await readFile(path);
        const route = `/samples/${records.length}${extname(file).toLowerCase()}`;
        assets.set(route, bytes);
        map[entry.name].push(route);
        records.push({ name: entry.name, index: map[entry.name].length - 1, path, sha256: sha256(bytes), bytes: bytes.length, route });
      }
    }
  }
  return { assets, map, records };
}

export function validateOptions(options) {
  if (!Number.isFinite(options.begin) || options.begin < 0 || !Number.isFinite(options.end) || options.end <= options.begin) {
    throw new Error('Require finite cycles: 0 <= begin < end');
  }
  if (!Number.isInteger(options.sampleRate) || options.sampleRate < 8000 || options.sampleRate > 96000) {
    throw new Error('Sample rate must be an integer between 8000 and 96000');
  }
  if (!Number.isFinite(options.timeout) || options.timeout <= 0) throw new Error('Timeout must be positive');
}

export async function render(options) {
  validateOptions(options);
  const source = await readFile(options.input);
  const { assets, map, records } = await loadSamples(options.samples ?? []);
  const bundle = await readFile(resolve(ROOT, 'node_modules/@strudel/web/dist/index.mjs'));
  if (sha256(bundle) !== BUNDLE_SHA256) throw new Error('Strudel renderer patch is missing or changed; run npm ci');
  assets.set('/strudel.mjs', bundle);
  for (const file of await readdir(resolve(ROOT, 'node_modules/@strudel/web/dist/assets'))) {
    assets.set(`/assets/${file}`, await readFile(resolve(ROOT, 'node_modules/@strudel/web/dist/assets', file)));
  }
  const out = resolve(options.out);
  // Never reuse an output directory, even after a failed render.
  await mkdir(dirname(out), { recursive: true });
  await mkdir(out);
  const receipt = {
    status: 'running', started_at: new Date().toISOString(),
    source: { path: resolve(options.input), sha256: sha256(source) },
    engine: {
      strudel_web: JSON.parse(await readFile(resolve(ROOT, 'node_modules/@strudel/web/package.json'))).version,
      bundle_sha256: sha256(bundle),
      renderer_sha256: sha256(await readFile(fileURLToPath(import.meta.url))),
      lock_sha256: sha256(await readFile(resolve(ROOT, 'package-lock.json'))),
      node: process.version,
    },
    settings: { begin: options.begin, end: options.end, sample_rate: options.sampleRate, max_polyphony: MAX_POLYPHONY, multi_channel_orbits: false, timeout_seconds: options.timeout },
    samples: records, requested_samples: [], logs: [], errors: [],
  };
  const saveReceipt = () => writeFile(resolve(out, 'render.json'), JSON.stringify(receipt, null, 2) + '\n');
  await writeFile(resolve(out, 'source.strudel'), source);
  await saveReceipt();
  let browser;
  let timer;
  let stop;
  const server = createServer((req, res) => {
    const route = req.url;
    if (route === '/') {
      res.setHeader('Content-Type', 'text/html');
      res.end('<!doctype html><title>Music render</title>');
    } else if (route === '/favicon.ico') {
      res.writeHead(204).end();
    } else if (assets.has(route)) {
      if (route.startsWith('/samples/') && !receipt.requested_samples.includes(route)) receipt.requested_samples.push(route);
      res.setHeader('Content-Type', /\.(mjs|js)$/.test(route) ? 'text/javascript' : 'application/octet-stream');
      res.end(assets.get(route));
    } else {
      receipt.errors.push(`Unknown local asset: ${route}`);
      res.writeHead(404).end();
    }
  });
  try {
    await new Promise((yes, no) => { server.once('error', no); server.listen(0, '127.0.0.1', yes); });
    const origin = `http://127.0.0.1:${server.address().port}`;
    browser = await chromium.launch({ channel: 'chrome', headless: true, timeout: options.timeout * 1000 });
    receipt.engine.browser = browser.version();
    const interrupted = new Promise((_, reject) => {
      stop = () => reject(new Error('Render interrupted'));
      process.once('SIGINT', stop);
      process.once('SIGTERM', stop);
      timer = setTimeout(() => reject(new Error(`Render timed out after ${options.timeout}s`)), options.timeout * 1000);
    });
    await Promise.race([interrupted, (async () => {
      const context = await browser.newContext({ acceptDownloads: true });
      // Only explicitly supplied assets are available; no remote dependency drift.
      await context.route('**/*', async (route) => {
        const url = route.request().url();
        if (new URL(url).origin === origin) await route.continue();
        else {
          receipt.errors.push(`External request blocked; supply a local sample folder: ${url}`);
          await route.abort();
        }
      });
      const page = await context.newPage();
      page.on('console', (message) => {
        const text = message.text();
        receipt.logs.push({ type: message.type(), text });
        // Strudel catches individual sound failures and reports them through console.log.
        if (message.type() === 'error' || /\[[^\]]+\] error:/.test(text)) receipt.errors.push(text);
      });
      page.on('pageerror', (error) => receipt.errors.push(error.message));
      page.on('requestfailed', (request) => receipt.errors.push(`Request failed: ${request.url()}: ${request.failure()?.errorText}`));
      page.on('response', (response) => { if (response.status() >= 400) receipt.errors.push(`HTTP ${response.status()}: ${response.url()}`); });
      await page.goto(origin);
      receipt.timing = await page.evaluate(async ({ code, map, begin, end, sampleRate, maxPolyphony }) => {
        document.addEventListener('strudel.log', ({ detail }) => {
          if (detail.type === 'error' || /loading sound .* took too long/.test(detail.message)) console.error(detail.message);
        });
        const engine = await import('/strudel.mjs');
        const repl = await engine.initStrudel();
        await engine.samples(map);
        const pattern = await repl.evaluate(code, false);
        if (!pattern || repl.state.evalError) throw new Error(`Evaluation failed: ${repl.state.evalError?.message ?? 'no pattern returned'}`);
        const cps = repl.scheduler.cps;
        if (!Number.isFinite(cps) || cps <= 0) throw new Error(`Invalid tempo: ${cps}`);
        const frames = Math.floor((end - begin) / cps * sampleRate);
        if (!Number.isSafeInteger(frames) || frames <= 0) throw new Error('Invalid audio frame count');
        window.renderAudio = () => engine.renderPatternAudio(pattern, cps, begin, end, sampleRate, maxPolyphony, false, 'render');
        return { cps, seconds: frames / sampleRate, frames };
      }, { code: source.toString('utf8'), map, begin: options.begin, end: options.end, sampleRate: options.sampleRate, maxPolyphony: MAX_POLYPHONY });
      await saveReceipt();
      const [download] = await Promise.all([
        page.waitForEvent('download', { timeout: options.timeout * 1000 }),
        page.evaluate(() => window.renderAudio()),
      ]);
      await download.saveAs(resolve(out, 'incomplete.wav'));
      if (receipt.errors.length) throw new Error('Engine reported errors; see render.json. Partial audio is incomplete.wav');
      const wav = await readFile(resolve(out, 'incomplete.wav'));
      // The pinned Strudel exporter writes a canonical PCM16 stereo WAV header.
      if (wav.toString('ascii', 0, 4) !== 'RIFF' || wav.toString('ascii', 8, 12) !== 'WAVE' ||
          wav.readUInt16LE(22) !== 2 || wav.readUInt32LE(24) !== options.sampleRate ||
          wav.readUInt16LE(34) !== 16 || wav.length !== 44 + receipt.timing.frames * 4) {
        throw new Error('Unexpected WAV format or frame count; preserved as incomplete.wav');
      }
      await rename(resolve(out, 'incomplete.wav'), resolve(out, 'render.wav'));
      receipt.output = { file: 'render.wav', bytes: wav.length, sha256: sha256(wav) };
      receipt.status = 'complete';
    })()]);
  } catch (error) {
    receipt.status = 'failed';
    receipt.errors.push(error.message);
    throw error;
  } finally {
    clearTimeout(timer);
    if (stop) { process.removeListener('SIGINT', stop); process.removeListener('SIGTERM', stop); }
    try {
      await browser?.close();
    } finally {
      server.closeAllConnections();
      await new Promise((done) => server.close(done));
      receipt.finished_at = new Date().toISOString();
      await saveReceipt();
    }
  }
  return { status: receipt.status, output: resolve(out, 'render.wav'), seconds: receipt.timing.seconds, manifest: resolve(out, 'render.json') };
}

if (process.argv[1] && resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  try {
    const { values, positionals } = parseArgs({ allowPositionals: true, options: {
      out: { type: 'string' }, begin: { type: 'string', default: '0' }, end: { type: 'string' },
      'sample-rate': { type: 'string', default: '48000' }, samples: { type: 'string', multiple: true, default: [] },
      timeout: { type: 'string', default: '120' },
    } });
    if (positionals.length !== 1 || !values.out || !values.end) throw new Error('Usage: render.mjs source.strudel --out NEW_DIR --end CYCLE [--begin 0] [--samples FOLDER]');
    console.log(JSON.stringify(await render({ input: positionals[0], out: values.out, begin: Number(values.begin), end: Number(values.end), sampleRate: Number(values['sample-rate']), samples: values.samples, timeout: Number(values.timeout) }), null, 2));
  } catch (error) {
    console.error(error.message);
    process.exitCode = 1;
  }
}
