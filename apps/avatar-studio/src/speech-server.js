import { execFile } from 'node:child_process';
import { promisify } from 'node:util';
import { mkdir, mkdtemp, readFile, writeFile, rm } from 'node:fs/promises';
import { randomUUID } from 'node:crypto';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
const run = promisify(execFile);
const MAX_SCRIPT = 1800;

export function validateSpeech(input, voices) {
  if (typeof input.text !== 'string' || !input.text.trim() || input.text.length > MAX_SCRIPT)
    throw new Error(`Enter a script between 1 and ${MAX_SCRIPT} characters.`);
  if (!voices.some(v => v.name === input.voice)) throw new Error('Choose an installed voice.');
  const rate = Number(input.rate);
  if (!Number.isFinite(rate) || rate < 100 || rate > 250) throw new Error('Speech rate must be between 100 and 250 words per minute.');
  // macOS speech embeds control instructions in double square brackets. Treat scripts as plain text.
  if (/\[\[|\]\]/.test(input.text)) throw new Error('Speech control tags are not supported. Use plain text.');
  return { text: input.text.trim(), voice: input.voice, rate: Math.round(rate) };
}

async function getVoices() {
  const { stdout } = await run('/usr/bin/say', ['-v', '?']);
  return stdout.split('\n').map(line => line.match(/^(.+?)\s{2,}([a-z]{2}_[A-Z]{2})\s+#/)).filter(Boolean)
    .map(m => ({ name: m[1].trim(), language: m[2] }))
    .filter(v => ['Samantha', 'Daniel', 'Alex', 'Karen', 'Moira', 'Rishi', 'Tessa', 'Alva'].includes(v.name));
}

export function speechPlugin() {
  let voices;
  let busy = false;
  return {
    name: 'local-speech',
    configureServer(server) {
      server.middlewares.use(async (req, res, next) => {
        const path = req.url?.split('?')[0];
        if (!['/api/voices', '/api/speech', '/api/export'].includes(path) && !path?.startsWith('/api/exports/')) return next();
        const json = (status, data) => { res.writeHead(status, { 'Content-Type': 'application/json' }); res.end(JSON.stringify(data)); };
        if (req.headers.origin && req.headers.origin !== `http://${req.headers.host}`) return json(403, { error: 'Open this studio locally to generate speech.' });
        let ownsSpeechLock = false;
        try {
          const exportDir = join(process.cwd(), '.private', 'exports');
          if (path.startsWith('/api/exports/') && req.method === 'GET') {
            const id = path.slice('/api/exports/'.length);
            if (!/^[a-f0-9-]{36}\.webm$/.test(id)) return json(400, { error: 'Invalid export.' });
            const file = await readFile(join(exportDir, id));
            res.writeHead(200, { 'Content-Type': 'video/webm', 'Content-Length': file.length, 'Content-Disposition': 'attachment; filename="character-performance.webm"' });
            return res.end(file);
          }
          if (path === '/api/export' && req.method === 'POST') {
            if (!req.headers['content-type']?.startsWith('video/webm')) return json(415, { error: 'Expected a WebM video.' });
            const chunks = []; let size = 0;
            for await (const chunk of req) { size += chunk.length; if (size > 100 * 1024 * 1024) return json(413, { error: 'Video exceeds the 100 MB demo limit.' }); chunks.push(chunk); }
            if (size < 100) return json(400, { error: 'Video recording was empty.' });
            await mkdir(exportDir, { recursive: true });
            const id = `${randomUUID()}.webm`;
            await writeFile(join(exportDir, id), Buffer.concat(chunks));
            return json(200, { url: `/api/exports/${id}`, path: join(exportDir, id) });
          }
          if (process.platform !== 'darwin') return json(501, { error: 'Local script voices require macOS. The sample and imported audio still work.' });
          voices ??= await getVoices();
          if (path === '/api/voices' && req.method === 'GET') return json(200, voices);
          if (path !== '/api/speech' || req.method !== 'POST') return json(405, { error: 'Method not allowed.' });
          if (busy) return json(409, { error: 'Another script is being voiced. Try again when it finishes.' });
          busy = true; ownsSpeechLock = true;
          let body = '';
          for await (const chunk of req) {
            body += chunk;
            if (Buffer.byteLength(body) > 16000) return json(413, { error: 'Script is too large.' });
          }
          const input = validateSpeech(JSON.parse(body), voices);
          const dir = await mkdtemp(join(tmpdir(), 'avatar-speech-'));
          try {
            const file = join(dir, 'speech.wav');
            const script = join(dir, 'script.txt');
            await writeFile(script, input.text);
            await run('/usr/bin/say', ['-v', input.voice, '-r', String(input.rate), '-o', file, '--file-format=WAVE', '--data-format=LEI16@24000', '-f', script], { timeout: 90000, maxBuffer: 1024 * 1024 });
            const audio = await readFile(file);
            res.writeHead(200, { 'Content-Type': 'audio/wav', 'Cache-Control': 'no-store', 'Content-Length': audio.length });
            res.end(audio);
          } finally { await rm(dir, { recursive: true, force: true }); }
        } catch (error) { json(400, { error: error.message }); }
        finally { if (ownsSpeechLock) busy = false; }
      });
    },
  };
}
