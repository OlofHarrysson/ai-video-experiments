#!/usr/bin/env node
// Voice-over: place the script's lines on the timeline and time every word, so the picture can cue on the voice.
//   usage: node tools/voice.mjs pieces/<name> [--scratch] [--rate 0]
// reads  <piece>/voice/script.json:
//   { "lead": 0.8, "tail": 1.5, "lines": [ { "id": "open", "text": "As it is spoken.", "file": "open.mp3", "after": 0.4 }, ... ] }
//   file   the line's audio, relative to <piece>/voice/: a text-to-speech take (e.g. the ElevenLabs MCP's download link,
//          saved there), or the user's own recording. One file per line, so pauses and re-takes stay per line.
//   after  the pause after the line (s); lead = silence before the first line, tail = after the last
// writes <piece>/voice/voice.wav (48 kHz mono, the lines with their pauses) and <piece>/voice.json:
//   { duration, lines: [ { id, text, t0, t1, words: [ { w, t0, t1 } ] } ] }; tools/build.mjs injects it as VOICE.
// Word times are estimated from letter counts within measured audio line durations; no speech recognizer runs.
// --scratch uses OS speech for timing previews. Replace the takes and rerun before delivery.
import { spawnSync } from 'node:child_process';
import fs from 'node:fs';
import path from 'node:path';

const argv = process.argv.slice(2);
const opt = (k, d) => { const i = argv.indexOf(k); return i >= 0 ? argv[i + 1] : d; };
if (!argv[0] || argv[0].startsWith('--')) { console.error('usage: node tools/voice.mjs pieces/<name> [--scratch] [--rate 0]'); process.exit(2); }
const ROOT = path.resolve(argv[0]), VDIR = path.join(ROOT, 'voice'), SR = 48000;
const S = JSON.parse(fs.readFileSync(path.join(VDIR, 'script.json'), 'utf8'));

// --scratch: the OS's own voice for missing lines (timing only; never ship it)
function scratch(text, out) {
  if (process.platform === 'win32') {
    const ps = `Add-Type -AssemblyName System.Speech; $s = New-Object System.Speech.Synthesis.SpeechSynthesizer; $s.Rate = ${Number(opt('--rate', 0))}; $s.SetOutputToWaveFile($env:VO_OUT); $s.Speak($env:VO_TEXT); $s.Dispose()`;
    return spawnSync('powershell', ['-NoProfile', '-Command', ps], { env: { ...process.env, VO_TEXT: text, VO_OUT: out } }).status === 0;
  }
  if (process.platform === 'darwin') return spawnSync('say', ['-o', out, '--data-format=LEI16@22050', text]).status === 0;
  return spawnSync('espeak', ['-w', out, text]).status === 0;
}

// decode a take to 48 kHz mono s16, trimmed of the silence around it
function decode(file) {
  const trim = 'silenceremove=start_periods=1:start_threshold=-45dB:start_silence=0.02';
  const r = spawnSync('ffmpeg', ['-v', 'error', '-i', file, '-af', `${trim},areverse,${trim},areverse`, '-ac', '1', '-ar', String(SR), '-f', 's16le', '-'], { maxBuffer: 1 << 30 });
  if (r.status !== 0) { console.error('could not decode', file, r.stderr.toString()); process.exit(1); }
  return r.stdout;
}

const lead = S.lead ?? 0.8, tail = S.tail ?? 1.5;
const parts = [], lines = [];
let t = lead;
for (const [i, L] of S.lines.entries()) {
  const id = L.id || `l${i + 1}`;
  let file = L.file ? path.join(VDIR, L.file) : path.join(VDIR, `${id}.wav`);
  if (!fs.existsSync(file)) {
    if (!argv.includes('--scratch')) { console.error(`missing take for line "${id}": ${file} (save the take there, or run with --scratch for a timing voice)`); process.exit(1); }
    file = path.join(VDIR, `${id}.scratch.wav`);
    if (!scratch(L.text, file)) { console.error('scratch voice failed for', id); process.exit(1); }
  }
  const pcm = decode(file), dur = pcm.length / 2 / SR;
  lines.push({ id, text: L.text, t0: +t.toFixed(3), t1: +(t + dur).toFixed(3), take: path.relative(ROOT, file).replace(/\\/g, '/') });
  parts.push([Math.round(t * SR), pcm]);
  t += dur + (L.after ?? 0.35);
}
const last = lines[lines.length - 1], total = last.t1 + tail;
const out = Buffer.alloc(Math.ceil(total * SR) * 2);
for (const [s0, pcm] of parts) pcm.copy(out, s0 * 2);
const hdr = Buffer.alloc(44);
hdr.write('RIFF', 0); hdr.writeUInt32LE(36 + out.length, 4); hdr.write('WAVE', 8); hdr.write('fmt ', 12);
hdr.writeUInt32LE(16, 16); hdr.writeUInt16LE(1, 20); hdr.writeUInt16LE(1, 22); hdr.writeUInt32LE(SR, 24); hdr.writeUInt32LE(SR * 2, 28);
hdr.writeUInt16LE(2, 32); hdr.writeUInt16LE(16, 34); hdr.write('data', 36); hdr.writeUInt32LE(out.length, 40);
const wav = path.join(VDIR, 'voice.wav');
fs.writeFileSync(wav, Buffer.concat([hdr, out]));

// ---- explicitly estimated word times within measured line durations
const norm = (w) => w.toLowerCase().replace(/[^a-z0-9]/g, '');
let totalWords = 0;
for (const L of lines) {
  const words = L.text.split(/\s+/).filter((w) => norm(w));
  totalWords += words.length;
  const lens = words.map((w) => norm(w).length + 1), sum = lens.reduce((a, b) => a + b, 0);
  let acc = L.t0;
  L.words = words.map((w, i) => {
    const d = (L.t1 - L.t0) * lens[i] / sum;
    const word = { w, t0: +acc.toFixed(3), t1: +(acc + d).toFixed(3), est: true };
    acc += d;
    return word;
  });
}
const voice = { duration: +total.toFixed(3), lead, tail, lines };
fs.writeFileSync(path.join(ROOT, 'voice.json'), JSON.stringify(voice, null, 1));
console.log(`voice: ${lines.length} lines, ${totalWords} words, ${total.toFixed(2)}s (lead ${lead}s, tail ${tail}s); word times estimated (no speech recognition)`);
for (const L of lines) console.log(`  ${L.id.padEnd(10)} ${L.t0.toFixed(2)}-${L.t1.toFixed(2)}s  ${(L.words.length / (L.t1 - L.t0)).toFixed(2)} w/s  ${L.take}  "${L.text}"`);
console.log(`wrote ${path.relative(process.cwd(), wav)} and ${path.relative(process.cwd(), path.join(ROOT, 'voice.json'))} (rebuild to inject VOICE)`);
