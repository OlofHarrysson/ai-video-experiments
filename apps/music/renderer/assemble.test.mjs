import test from 'node:test';
import assert from 'node:assert/strict';
import { mkdtemp, writeFile, readFile, rm } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { resolve } from 'node:path';
import { validateModules, assembleProject } from './assemble.mjs';

const setup = { file: 'setup.strudel', code: 'setcpm(32)\nconst root = "f1"' };
const bass = { file: 'bass.strudel', stem: 'low', code: 'sub: note(root).s("sine")\nbass: note(root).s("sawtooth")' };
test('module assembly partitions layers and preserves strings/comments', () => {
  const result = validateModules([setup, bass, { file: 'drums.strudel', stem: 'drums', code: '// bass: not a layer\nkick: s("bd:0")' }]);
  assert.deepEqual(result.stems, { low: ['sub', 'bass'], drums: ['kick'] });
  assert.ok(result.code.includes(bass.code));
  assert.ok(result.code.includes('\n;\n\n// Module'));
});
test('assembly rejects collisions and unowned layers before rendering', () => {
  assert.throws(() => validateModules([setup, { file: 'bad.strudel', code: 'throw: s(1)' }]), /bad.strudel: Unexpected token/);
  assert.throws(() => validateModules([setup, bass, { ...bass, file: 'duplicate' }]), /Duplicate.*layer/);
  assert.throws(() => validateModules([setup, bass, { file: 'duplicate', code: 'var root = 2' }]), /Duplicate.*declaration/);
  assert.throws(() => validateModules([setup, { ...bass, stem: undefined }]), /need a stem/);
  assert.throws(() => validateModules([setup, bass, { file: 'tempo', code: 'setcps(2)' }]), /exactly one/);
  assert.throws(() => validateModules([setup, { file: 'empty', stem: 'fx', code: 'const x = 1' }]), /no sound layers/);
});
test('assembly snapshots inputs, rebases sample paths, and never overwrites', async () => {
  const root = await mkdtemp(resolve(tmpdir(), 'music-modules-'));
  try {
    await writeFile(resolve(root, setup.file), setup.code);
    await writeFile(resolve(root, bass.file), bass.code);
    const manifest = resolve(root, 'manifest.json');
    await writeFile(manifest, JSON.stringify({ version: 1, revision: 'v001', end_cycle: 4, samples: ['samples'], sections: { all: [0, 4] }, modules: [ { file: setup.file }, { file: bass.file, stem: bass.stem } ] }));
    const result = await assembleProject(manifest, resolve(root, 'out'));
    const project = JSON.parse(await readFile(result.project));
    assert.deepEqual(project.samples, ['../samples']);
    assert.deepEqual(project.stems.low, ['sub', 'bass']);
    assert.equal(await readFile(resolve(root, 'out/modules/02.strudel'), 'utf8'), bass.code);
    await assert.rejects(assembleProject(manifest, resolve(root, 'out')), /EEXIST/);
  } finally { await rm(root, { recursive: true, force: true }); }
});

test('assembled modules render the same dry audio as a monolithic source', async () => {
  const { render } = await import('./render.mjs');
  const root = await mkdtemp(resolve(tmpdir(), 'music-assembly-audio-'));
  try {
    const setupCode = 'setcpm(60)\nconst rootNote = "c2"';
    const musicCode = 'low: note(rootNote).s("sine").gain(.1)\nhigh: note("c4 e4").s("triangle").gain(.05)';
    await writeFile(resolve(root, 'setup.strudel'), setupCode);
    await writeFile(resolve(root, 'music.strudel'), musicCode);
    await writeFile(resolve(root, 'modules.json'), JSON.stringify({ version: 1, revision: 'v001', end_cycle: 2, modules: [{ file: 'setup.strudel' }, { file: 'music.strudel', stem: 'music' }] }));
    const assembled = await assembleProject(resolve(root, 'modules.json'), resolve(root, 'assembly'));
    const plain = resolve(root, 'plain.strudel');
    await writeFile(plain, `${setupCode}\n${musicCode}`);
    for (const [name, input] of [['assembled', assembled.source], ['plain', plain]]) {
      await render({ input, out: resolve(root, name), begin: 0, end: 2, sampleRate: 24000, timeout: 60, samples: [], solo: [] });
    }
    assert.ok((await readFile(resolve(root, 'assembled/render.wav'))).equals(await readFile(resolve(root, 'plain/render.wav'))));
  } finally { await rm(root, { recursive: true, force: true }); }
});
