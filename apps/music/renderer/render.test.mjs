import { test } from 'node:test';
import assert from 'node:assert/strict';
import { mkdtemp, mkdir, writeFile, readFile, access, rm } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { render } from './render.mjs';

async function fixture(t, code, overrides = {}) {
  const dir = await mkdtemp(join(tmpdir(), 'music-render-test-'));
  t.after(() => rm(dir, { recursive: true, force: true }));
  const input = join(dir, 'source.strudel');
  await writeFile(input, code);
  return { input, out: join(dir, 'output'), begin: 0, end: 0.25, sampleRate: 48000, timeout: 20, ...overrides };
}

test('synth render preserves source/tempo, is audible, and cannot overwrite output', async (t) => {
  const opts = await fixture(t, 'setcpm(60)\n$: note("c3").s("sine").gain(.2)');
  const result = await render(opts);
  assert.equal(result.seconds, 0.25);
  const wav = await readFile(result.output);
  assert.equal(wav.length, 44 + 12000 * 4);
  assert.ok(wav.subarray(44).some((byte) => byte !== 0));
  assert.deepEqual(await readFile(join(opts.out, 'source.strudel')), await readFile(opts.input));
  const receipt = JSON.parse(await readFile(result.manifest));
  assert.equal(receipt.status, 'complete');
  assert.equal(receipt.timing.cps, 1);
  assert.equal(receipt.errors.length, 0);
  await assert.rejects(render(opts), /EEXIST/);
  assert.deepEqual(await readFile(result.output), wav);
});

test('local sample is restored in fresh profiles, hashed, and sliced/reversed deterministically', async (t) => {
  const opts = await fixture(t, 'setcpm(60)\n$: s("voice").slice(4,"0 2").speed(-1).gain(.5)', { begin: 1, end: 1.25 });
  const samples = join(opts.out, '..', 'samples');
  await mkdir(join(samples, 'voice'), { recursive: true });
  const wave = Buffer.alloc(44 + 4800 * 2);
  wave.write('RIFF'); wave.writeUInt32LE(wave.length - 8, 4); wave.write('WAVEfmt ', 8);
  wave.writeUInt32LE(16, 16); wave.writeUInt16LE(1, 20); wave.writeUInt16LE(1, 22);
  wave.writeUInt32LE(48000, 24); wave.writeUInt32LE(96000, 28); wave.writeUInt16LE(2, 32); wave.writeUInt16LE(16, 34);
  wave.write('data', 36); wave.writeUInt32LE(wave.length - 44, 40);
  for (let i = 0; i < 4800; i++) wave.writeInt16LE(Math.round(8000 * Math.sin(i * 2 * Math.PI * 220 / 48000)), 44 + 2 * i);
  await writeFile(join(samples, 'voice', 'phrase.wav'), wave);
  opts.samples = [samples];
  const first = await render(opts);
  const second = await render({ ...opts, out: `${opts.out}-repeat` });
  assert.deepEqual(await readFile(first.output), await readFile(second.output));
  const wav = await readFile(first.output);
  assert.ok(wav.subarray(44).some((byte) => byte !== 0));
  const receipt = JSON.parse(await readFile(first.manifest));
  assert.equal(receipt.samples.length, 1);
  assert.equal(receipt.samples[0].sha256.length, 64);
  assert.equal(receipt.requested_samples.length, 1);
});

test('missing sound cannot silently produce a successful partial render', async (t) => {
  const opts = await fixture(t, 'setcpm(60)\n$: s("missing_sound")');
  await assert.rejects(render(opts), /Engine reported errors/);
  const receipt = JSON.parse(await readFile(join(opts.out, 'render.json')));
  assert.equal(receipt.status, 'failed');
  assert.ok(receipt.errors.some((error) => error.includes('not found')));
  await assert.rejects(access(join(opts.out, 'render.wav')));
  await access(join(opts.out, 'incomplete.wav'));
});

test('invalid source fails with a receipt', async (t) => {
  const opts = await fixture(t, '$: note(');
  await assert.rejects(render(opts), /Evaluation failed/);
  assert.equal(JSON.parse(await readFile(join(opts.out, 'render.json'))).status, 'failed');
  await assert.rejects(access(join(opts.out, 'render.wav')));
});

test('remote dependencies fail explicitly without a network fallback', async (t) => {
  const opts = await fixture(t, "samples('https://example.invalid/samples.json')\n$: s(\"voice\")");
  await assert.rejects(render(opts));
  const receipt = JSON.parse(await readFile(join(opts.out, 'render.json')));
  assert.equal(receipt.status, 'failed');
  assert.ok(receipt.errors.some((error) => error.includes('External request blocked')));
});

test('nonterminating source times out and closes the browser', async (t) => {
  const opts = await fixture(t, '(() => { while (true) {} })()\n$: s("sine")', { timeout: 2 });
  await assert.rejects(render(opts), /timed out/);
  assert.equal(JSON.parse(await readFile(join(opts.out, 'render.json'))).status, 'failed');
});
