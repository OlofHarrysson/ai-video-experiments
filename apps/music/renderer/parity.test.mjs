import { test } from 'node:test';
import assert from 'node:assert/strict';
import { existsSync } from 'node:fs';
import { mkdtemp, readFile, rm } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { dirname, resolve, join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { render } from './render.mjs';

const ROOT = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const studies = [
  { name: 'dry synth', project: 'tooling-validation', source: 'v001-full', wav: 'tooling-v001-full', begin: 0, end: 4, tolerance: 0 },
  { name: 'overlap and delay', project: 'tooling-validation', source: 'v002-full', wav: 'tooling-v002-full', begin: 0, end: 4, tolerance: 1 },
  { name: 'practical dry beat with speech and reverse slices', project: 'practical-dogfood', source: 'v003-dry-full', wav: 'practical-v003-dry-full', begin: 2, end: 16, tolerance: 1, samples: ['samples', 'drums'] },
];

// Golden WAVs are preserved locally, not distributed in Git. A fresh clone must
// restore that corpus to run these tests; the synthetic tests need no corpus.
for (const study of studies) {
  const project = resolve(ROOT, 'projects', study.project);
  const reference = resolve(project, 'renders', `${study.wav}.wav`);
  const samples = (study.samples ?? []).map((name) => resolve(project, 'references/assets', name));
  test(`website parity: ${study.name}`, {
    skip: !existsSync(reference) || samples.some((path) => !existsSync(path)) ? 'Restore local reference WAVs/sample folders first' : false,
  }, async (t) => {
    const directory = await mkdtemp(join(tmpdir(), 'music-parity-'));
    t.after(() => rm(directory, { recursive: true, force: true }));
    const result = await render({ input: resolve(project, 'source', `${study.source}.strudel`), out: join(directory, 'render'), begin: study.begin, end: study.end, sampleRate: 48000, timeout: 120, samples });
    const [expected, actual] = await Promise.all([readFile(reference), readFile(result.output)]);
    assert.equal(actual.length, expected.length);
    let peak = 0;
    for (let offset = 44; offset < actual.length; offset += 2) {
      peak = Math.max(peak, Math.abs(actual.readInt16LE(offset) - expected.readInt16LE(offset)));
    }
    assert.ok(peak <= study.tolerance, `Residual peak ${peak} PCM16 steps exceeds ${study.tolerance}; revalidate engine/browser changes`);
  });
}
