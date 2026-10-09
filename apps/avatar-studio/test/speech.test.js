import { test } from 'node:test';
import assert from 'node:assert/strict';
import { validateSpeech } from '../src/speech-server.js';
const voices = [{ name: 'Samantha' }];
const valid = { text: 'A short script.', voice: 'Samantha', rate: 170 };
test('accepts plain text including shell punctuation without interpreting it', () => {
  assert.equal(validateSpeech({ ...valid, text: 'Hello; $(whoami) `test`' }, voices).text, 'Hello; $(whoami) `test`');
});
test('rejects missing content, invalid voices and unsupported control tags', () => {
  for (const input of [{ ...valid, text: '' }, { ...valid, text: 'a'.repeat(1801) }, { ...valid, voice: 'Samantha; touch /tmp/x' }, { ...valid, text: '[[rate 900]] hi' }, { ...valid, rate: 0 }])
    assert.throws(() => validateSpeech(input, voices));
});
