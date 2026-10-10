// Explain each hybrid card: its generated picture, the masks code derives from it, and the resulting frames.
// node breakdown.mjs <output-dir>
import fs from 'node:fs';
import path from 'node:path';
import http from 'node:http';
import { createRequire } from 'node:module';
import { fileURLToPath } from 'node:url';

const { chromium } = createRequire(new URL('../../../../../.agents/skills/animate/package.json', import.meta.url))('playwright');
const here = path.dirname(fileURLToPath(import.meta.url)), root = path.resolve(here, '..');
const out = path.join(here, process.argv[2] || 'breakdown-01');
if (fs.existsSync(out)) throw new Error('choose a new output directory');
fs.mkdirSync(out, { recursive: true });
const TYPES = { '.html': 'text/html', '.js': 'text/javascript', '.mjs': 'text/javascript', '.json': 'application/json', '.ttf': 'font/ttf', '.png': 'image/png' };
const server = http.createServer((req, res) => {
  const file = path.join(root, decodeURIComponent(new URL(req.url, 'http://x').pathname));
  if (!file.startsWith(root) || !fs.existsSync(file) || fs.statSync(file).isDirectory()) { res.writeHead(404); return res.end(); }
  res.writeHead(200, { 'Content-Type': TYPES[path.extname(file)] || 'application/octet-stream' }); fs.createReadStream(file).pipe(res);
});
await new Promise(ok => server.listen(0, '127.0.0.1', ok));
const browser = await chromium.launch();
try {
  const page = await browser.newPage();
  await page.goto(`http://127.0.0.1:${server.address().port}/proof-v002/index.html?t=0`);
  await page.waitForFunction(() => window.ready);
  const sheets = await page.evaluate(() => {
    const W = 1080, H = 1920, TW = 252, TH = 448, COLS = 5, PAD = 14, LABEL = 52;
    const L = window.LAYERS, T = window.TIMES, main = document.getElementById('c');
    const cv = (w, h) => { const c = document.createElement('canvas'); c.width = w; c.height = h; return c; };
    const onBlack = (fn) => { const c = cv(W, H), g = c.getContext('2d'); g.fillStyle = '#000'; g.fillRect(0, 0, W, H); fn(g); return c; };
    const maskView = m => onBlack(g => g.drawImage(m, 0, 0));
    const frame = t => { window.renderFrame(t); const c = cv(W, H); c.getContext('2d').drawImage(main, 0, 0); return c; };
    function sheet(title, cells) {
      const rows = Math.ceil(cells.length / COLS), c = cv(COLS * (TW + PAD) + PAD, 56 + rows * (TH + LABEL + PAD)), g = c.getContext('2d');
      g.fillStyle = '#161616'; g.fillRect(0, 0, c.width, c.height);
      g.fillStyle = '#fff'; g.font = '600 24px -apple-system, Helvetica, sans-serif'; g.fillText(title, PAD, 36);
      cells.forEach(([img, a, b], i) => {
        const x = PAD + (i % COLS) * (TW + PAD), y = 56 + Math.floor(i / COLS) * (TH + LABEL + PAD);
        g.fillStyle = '#ffd84a'; g.font = '600 15px -apple-system, Helvetica, sans-serif'; g.fillText(a, x, y + 18);
        g.fillStyle = '#bbb'; g.font = '14px -apple-system, Helvetica, sans-serif'; g.fillText(b || '', x, y + 38);
        g.drawImage(img, x, y + LABEL, TW, TH);
      });
      return c.toDataURL('image/png').split(',')[1];
    }
    const band = p => onBlack(g => {
      g.save(); g.translate(W / 2, H / 2); g.rotate(-.95); const x = -1500 + 3000 * p, gr = g.createLinearGradient(x - 170, 0, x + 170, 0);
      gr.addColorStop(0, 'rgba(255,190,140,0)'); gr.addColorStop(.5, 'rgba(255,255,255,1)'); gr.addColorStop(1, 'rgba(120,230,255,0)');
      g.fillStyle = gr; g.fillRect(x - 170, -2000, 340, 4000); g.restore();
    });
    const clipped = (src, m) => { const c = cv(W, H), g = c.getContext('2d'); g.drawImage(src, 0, 0); g.globalCompositeOperation = 'destination-in'; g.drawImage(m, 0, 0); return onBlack(h => h.drawImage(c, 0, 0)); };
    const flats = onBlack(g => { g.save(); g.translate(-270, 0); g.fillStyle = '#C80528'; g.fill(L.yes.flat); g.restore();
      g.save(); g.translate(270, 0); g.lineJoin = 'round'; g.strokeStyle = '#00D2E6'; g.lineWidth = 16; g.stroke(L.yes.flat); g.strokeStyle = '#000'; g.lineWidth = 7; g.stroke(L.yes.flat); g.restore(); });
    const B = 60 / 140;

    const yes = sheet('YES.  — one generated picture; code only decides what is visible, how bright, and when', [
      [L.yes.picture, '1 The picture', 'AI-generated, never redrawn'],
      [maskView(L.yes.metal), '2 Metal mask', 'bright pixels = chrome'],
      [band(.5), '3 A light band', 'just a gradient, made in code'],
      [clipped(band(.5), L.yes.metal), '4 Band × metal mask', 'shine lands only on chrome'],
      [flats, '5 Flat identities', 'drawn from the Anton font'],
      [frame(T.yes + .01), 'frame +0.00 s', 'flat red (2 frames)'],
      [frame(T.yes + .08), 'frame +0.08 s', 'cyan outline (2 frames)'],
      [frame(T.yes + .15), 'frame +0.15 s', 'picture slams in (spring)'],
      [frame(T.yes + .33), 'frame +0.33 s', 'picture + band added'],
      [frame(T.yes + B + .01), 'frame +0.43 s', 'cyan flip on the next beat'],
    ]);
    const spots = onBlack(g => { g.globalAlpha = .35; g.drawImage(L.marquee.picture, 0, 0); g.globalAlpha = 1; g.fillStyle = '#ff3b3b';
      for (const s of L.marquee.spots) { g.beginPath(); g.arc(s.x, s.y, 5, 0, 7); g.fill(); } });
    const marquee = sheet('NO AI EXPERIENCE NEEDED  — the same picture, switched on in stages through masks', [
      [L.marquee.picture, '1 The picture', 'AI-generated, fully lit'],
      [L.marquee.unlit, '2 Unlit copy', 'same pixels, darkened in code'],
      [maskView(L.marquee.neon), '3 Neon mask', 'pixels found by colour'],
      [spots, `4 Bulb finder (${L.marquee.spots.length})`, 'one dot per bright spot'],
      [maskView(L.marquee.glow), '5 Glow mask', 'brightest pixels, for beat flashes'],
      [frame(T.marquee + .05), 'frame +0.05 s', 'wipe uncovers the unlit copy'],
      [frame(T.marquee + .14), 'frame +0.14 s', 'neon mask shows lit pixels'],
      [frame(T.marquee + .26), 'frame +0.26 s', 'bulbs on, outer frame first'],
      [frame(T.marquee + .36), 'frame +0.36 s', 'then the letters'],
      [frame(T.marquee + .62), 'frame +0.62 s', 'full picture, chase dims 1 in 3'],
    ]);
    const boxes = onBlack(g => { g.globalAlpha = .4; g.drawImage(L.crews.picture, 0, 0); g.globalAlpha = 1; g.strokeStyle = '#ffd84a'; g.lineWidth = 4; g.fillStyle = '#ffd84a'; g.font = '600 34px Helvetica';
      L.crews.boxes.forEach((b, i) => { g.strokeRect(b.x0, b.y0, b.x1 - b.x0, b.y1 - b.y0); g.fillText(String(i + 1), b.x0 + 6, b.y0 + 34); }); });
    const crews = sheet('CREWS FORM FRIDAY  — the picture is uncovered letter by letter in reading order', [
      [L.crews.picture, '1 The picture', 'AI-generated ribbon letters'],
      [maskView(L.crews.letters), '2 Letter mask', 'everything that is not black'],
      [boxes, '3 Letter boxes + order', 'found from gaps between letters'],
      [frame(T.crews + .1), 'frame +0.10 s', 'loose ribbons drop in'],
      [frame(T.crews + .2), 'frame +0.20 s', 'thread runs ahead, letters wipe on'],
      [frame(T.crews + .3), 'frame +0.30 s', 'glint rides each wipe edge'],
      [frame(T.crews + .45), 'frame +0.45 s', 'last line lands'],
      [frame(12 * B + .01), 'frame +0.64 s', 'cyan flip on the bar line'],
      [frame(T.crews + .95), 'frame +0.95 s', 'sheen sweeps the ribbons'],
    ]);
    return { yes, marquee, crews };
  });
  for (const [k, v] of Object.entries(sheets)) fs.writeFileSync(path.join(out, `breakdown-${k}.png`), Buffer.from(v, 'base64'));
  console.log('wrote', Object.keys(sheets).map(k => `breakdown-${k}.png`).join(', '), 'to', out);
} finally { await browser.close(); server.close(); }
