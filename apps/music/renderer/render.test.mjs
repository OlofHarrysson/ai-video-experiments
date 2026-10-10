import { test } from 'node:test';
import assert from 'node:assert/strict';
import { mkdtemp, mkdir, writeFile, readFile, access, rm } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { render } from './render.mjs';
import { selectLayers } from './layers.mjs';

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
  await assert.rejects(render(opts), /Unexpected token/);
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

test('layer selection parses multiline labels without rewriting comments or strings', () => {
  const code = '// bass: is a comment\nconst text = \'drums: a string\';\ndrums: s("sine")\n .gain(.2)\nbass: note("c2").s("sine")';
  const result = selectLayers(code, ['bass']);
  assert.deepEqual(result.labels, ['drums', 'bass']);
  assert.ok(result.code.includes('\n_drums: s("sine")'));
  assert.ok(result.code.includes("'drums: a string'"));
  assert.ok(result.code.includes('// bass: is a comment'));
  assert.throws(() => selectLayers(code, ['typo']), /Unknown layer/);
  assert.throws(() => selectLayers('$: s("sine")', ['bass']), /named labels/);
});

test('named dry stems sum to the master and retain original source', async (t) => {
  const code = 'setcpm(60)\nlow: note("c3 ~").s("sine").gain(.2)\nhigh: note("~ g4").s("triangle").gain(.1)';
  const opts = await fixture(t, code, { end: 1 });
  const full = await render(opts);
  const low = await render({ ...opts, out: `${opts.out}-low`, solo: ['low'] });
  const high = await render({ ...opts, out: `${opts.out}-high`, solo: ['high'] });
  const wavs = await Promise.all([full, low, high].map((result) => readFile(result.output)));
  let peak = 0;
  for (let i = 44; i < wavs[0].length; i += 2) peak = Math.max(peak, Math.abs(wavs[0].readInt16LE(i) - wavs[1].readInt16LE(i) - wavs[2].readInt16LE(i)));
  // Three separately quantized PCM16 signals can differ by two steps where
  // release tails overlap, as in the retained overlap/delay fixture.
  assert.ok(peak <= 2, `Stem residual ${peak} steps`);
  assert.equal(await readFile(join(`${opts.out}-low`, 'source.strudel'), 'utf8'), code);
  assert.ok((await readFile(join(`${opts.out}-low`, 'evaluated.strudel'), 'utf8')).includes('_high:'));
});

test('event trace observes global pattern phase and sustained onsets without changing dry audio', async (t) => {
  const code = 'setcpm(60)\nlow: note("c2").s("sine").slow(3).gain(.04)\nhigh: note("<c3 e3 g3 b3>").s("triangle").gain(.03).mask("<0!2 1!2>")';
  const opts = await fixture(t, code, { end: 4, sampleRate: 12000 });
  const plain = await render(opts);
  const traced = await render({ ...opts, out: `${opts.out}-traced`, traceEvents: true });
  assert.deepEqual(await readFile(plain.output), await readFile(traced.output));
  const trace = JSON.parse(await readFile(join(`${opts.out}-traced`, 'events.json')));
  assert.deepEqual(trace.events.map((event) => [event.onset_cycle, event.controls.note]),
    [[0, 'c2'], [2, 'g3'], [3, 'c2'], [3, 'b3']]);
  assert.equal(trace.events[0].scheduled_duration_seconds, 3);
  assert.equal(trace.events[1].onset_seconds, 2);
  assert.equal(trace.events[1].query_begin_cycle, 2);
  const receipt = JSON.parse(await readFile(traced.manifest));
  assert.equal(receipt.event_trace.count, 4);
  assert.equal(receipt.event_trace.sha256.length, 64);
  const cropped = await render({ ...opts, out: `${opts.out}-cropped`, begin: 2, traceEvents: true });
  const crop = JSON.parse(await readFile(join(`${opts.out}-cropped`, 'events.json')));
  assert.deepEqual(crop.events.map((event) => event.onset_seconds), [0, 1, 1]);
  assert.equal(crop.events[0].controls.note, 'g3');
  assert.equal(JSON.parse(await readFile(cropped.manifest)).settings.trace_events, true);
});
