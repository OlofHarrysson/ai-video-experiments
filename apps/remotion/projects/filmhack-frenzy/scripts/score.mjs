// Renders the Tone.js score in headless Chrome and masters it for Instagram:
// bundle src/audio/entry.ts → OfflineAudioContext → WAV → two-pass loudness normalization.
//
//   node scripts/score.mjs   → public/soundtrack.wav (used by the composition)
import { spawn } from 'node:child_process';
import { mkdir, rm, writeFile } from 'node:fs/promises';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { build } from 'esbuild';
import { chromium } from 'playwright-core';

const ROOT = join(dirname(fileURLToPath(import.meta.url)), '..');
const RAW = join(ROOT, 'public/.soundtrack-raw.wav');
const MASTER = join(ROOT, 'public/soundtrack.wav');
// Headroom below -1 dBTP leaves room for AAC encoding in Remotion and again on Instagram.
const LOUDNESS = 'I=-14:TP=-1.5:LRA=11';

function ffmpeg(args) {
  return new Promise((resolve, reject) => {
    const proc = spawn('ffmpeg', ['-hide_banner', '-y', ...args], { stdio: ['ignore', 'ignore', 'pipe'] });
    let stderr = '';
    proc.stderr.on('data', (d) => (stderr += d));
    proc.on('close', (code) => (code === 0 ? resolve(stderr) : reject(new Error(`ffmpeg exited ${code}\n${stderr.slice(-1500)}`))));
  });
}

const bundle = await build({
  entryPoints: [join(ROOT, 'src/audio/entry.ts')],
  bundle: true,
  format: 'iife',
  platform: 'browser',
  target: 'chrome120',
  write: false,
  logLevel: 'warning',
});

const browser = await chromium.launch({ channel: 'chrome', headless: true });
try {
  const page = await browser.newPage();
  page.on('pageerror', (e) => console.error(`[page error] ${e.message}`));
  await page.setContent('<!doctype html><html><body></body></html>');
  await page.addScriptTag({ content: bundle.outputFiles[0].text });
  const started = Date.now();
  const base64 = await page.evaluate(() => window.renderScoreWav());
  await mkdir(dirname(RAW), { recursive: true });
  await writeFile(RAW, Buffer.from(base64, 'base64'));
  console.log(`score rendered in ${((Date.now() - started) / 1000).toFixed(1)} s`);
} finally {
  await browser.close();
}

const analysis = await ffmpeg(['-i', RAW, '-af', `loudnorm=${LOUDNESS}:print_format=json`, '-f', 'null', '-']);
const m = JSON.parse(analysis.slice(analysis.lastIndexOf('{'), analysis.lastIndexOf('}') + 1));
console.log(`raw mix: ${m.input_i} LUFS, true peak ${m.input_tp} dBTP, LRA ${m.input_lra}`);
const measured = `measured_I=${m.input_i}:measured_TP=${m.input_tp}:measured_LRA=${m.input_lra}:measured_thresh=${m.input_thresh}:offset=${m.target_offset}`;
await ffmpeg(['-i', RAW, '-af', `loudnorm=${LOUDNESS}:${measured}:linear=true`, '-ar', '48000', '-c:a', 'pcm_s24le', MASTER]);
if (!process.argv.includes('--keep-raw')) await rm(RAW);
console.log(`soundtrack → ${MASTER}`);
