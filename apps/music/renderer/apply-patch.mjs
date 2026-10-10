import { createHash } from 'node:crypto';
import { readFileSync } from 'node:fs';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { execFileSync } from 'node:child_process';
import { BUNDLE_SHA256 } from './engine-version.mjs';

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const bundle = resolve(root, 'node_modules/@strudel/web/dist/index.mjs');
const hash = () => createHash('sha256').update(readFileSync(bundle)).digest('hex');
const original = '50beb01abd04589333a10e078dce182c82e2de75b43e9bbe81a34bd069948931';
if (hash() !== BUNDLE_SHA256) {
  if (hash() !== original) throw new Error('Unexpected Strudel bundle. Revalidate the pinned renderer before updating it.');
  execFileSync('patch', ['--batch', '--forward', '-p1', '-i', 'patches/@strudel+web+1.3.0.patch'], { cwd: root, stdio: 'inherit' });
  if (hash() !== BUNDLE_SHA256) throw new Error('Strudel scheduling patch checksum mismatch');
}
console.log('Verified Strudel 1.3.0 with chunked scheduling patch');
