// Query the pinned renderer's actual event positions; no audio or remote request.
import { createServer } from 'node:http';
import { readFile } from 'node:fs/promises';
import { resolve, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
import { createHash } from 'node:crypto';
import { chromium } from 'playwright-core';
import { selectLayers } from '../../renderer/layers.mjs';
import { BUNDLE_SHA256 } from '../../renderer/engine-version.mjs';
const root = dirname(fileURLToPath(import.meta.url));
const music = resolve(root, '../..');
const bundle = await readFile(resolve(music, 'node_modules/@strudel/web/dist/index.mjs'));
if (createHash('sha256').update(bundle).digest('hex') !== BUNDLE_SHA256) throw new Error('Engine hash mismatch');
const server = createServer((req, res) => {
  if (req.url === '/strudel.mjs') { res.setHeader('Content-Type', 'application/javascript'); res.end(bundle); }
  else if (req.url === '/') { res.setHeader('Content-Type', 'text/html'); res.end('<html><body></body></html>'); }
  else { res.statusCode = 404; res.end(); }
});
let browser;
try {
  await new Promise((yes, no) => { server.once('error', no); server.listen(0, '127.0.0.1', yes); });
  const origin = `http://127.0.0.1:${server.address().port}`;
  browser = await chromium.launch({channel:'chrome', headless:true, timeout:30000});
  const context = await browser.newContext();
  await context.route('**/*', async route => new URL(route.request().url()).origin === origin ? route.continue() : route.abort());
  const page = await context.newPage();
  await page.goto(origin);
  const result = {engine_sha256:BUNDLE_SHA256, scope:'Pattern onset positions, not perceived timing or audibility', versions:{}};
  for (const revision of ['v007','v010','v011']) {
    const source = await readFile(resolve(root, 'assemblies',revision,'source.strudel'),'utf8');
    const selected = selectLayers(source,['bass','ghost']);
    const events = await page.evaluate(async code => {
      const engine = await import('/strudel.mjs');
      const repl = await engine.initStrudel();
      const pattern = await repl.evaluate(code,false);
      if (!pattern || repl.state.evalError) throw new Error('Pattern evaluation failed');
      return pattern.queryArc(10,14).filter(h=>h.hasOnset()).map(h=>({
        sound:h.value.s, start_cycle:Number(h.whole.begin), end_cycle:Number(h.whole.end),
        sixteenth:Number(h.whole.begin.sub(Math.floor(Number(h.whole.begin))))*16,
        bar:Math.floor(Number(h.whole.begin)),
      }));
    },selected.code);
    const bass = events.filter(event=>event.sound === 'sawtooth');
    const object = events.filter(event=>event.sound === 'nsbloomwarm');
    const simultaneous = bass.filter(event=>object.some(answer=>answer.start_cycle === event.start_cycle));
    result.versions[revision] = {
      source_sha256:createHash('sha256').update(source).digest('hex'),
      coincident_bass_object_onsets:simultaneous.length,
      events,
    };
    if (revision === 'v011' && simultaneous.length) throw new Error('Return has an unintended bass/object onset collision');
  }
  console.log(JSON.stringify(result,null,2));
} finally {
  await browser?.close();
  server.closeAllConnections();
  await new Promise(done=>server.close(done));
}
