// Same animation, three ways of splitting the CREWS picture into parts. Deterministic: renderFrame(t).
const W = 1080, H = 1920, OUT_W = 1920, OUT_H = 1080, DURATION = 4.2, MAP_END = .8;
const clamp = (x, a = 0, b = 1) => Math.min(b, Math.max(a, x));
const outBack = t => { t = clamp(t); const c = 1.7; return 1 + (c + 1) * (t - 1) ** 3 + c * (t - 1) ** 2; };
const outCubic = t => 1 - (1 - clamp(t)) ** 3;
const rng = s => () => (s = (s * 16807) % 2147483647) / 2147483647;
const cv = (w = W, h = H) => { const c = document.createElement('canvas'); c.width = w; c.height = h; return c; };
const img = url => new Promise((ok, fail) => { const i = new Image(); i.onload = () => ok(i); i.onerror = fail; i.src = url; });

function pixels(image) { const c = cv(), g = c.getContext('2d'); g.drawImage(image, 0, 0, W, H); return g.getImageData(0, 0, W, H); }

// Labels: 0 = background, k = part k. Chunks come from column gaps per text row, as in proof v002.
function chunkLabels(pic) {
  const d = pic.data, lab = new Uint8Array(W * H), bands = [[.222, .378], [.39, .552], [.558, .728]];
  const fg = i => (.3 * d[i * 4] + .59 * d[i * 4 + 1] + .11 * d[i * 4 + 2]) / 255 > .1;
  let k = 0;
  for (let y = 0; y < Math.round(.222 * H) - 4; y++) for (let x = 0; x < W; x++) if (fg(y * W + x)) lab[y * W + x] = 255;
  for (const [a, b] of bands) {
    const y0 = Math.round(a * H), y1 = Math.round(b * H); let start = -1;
    for (let x = 0; x <= W; x++) {
      let on = false; if (x < W) { let s = 0; for (let y = y0; y < y1; y += 2) s += fg(y * W + x); on = s > 3; }
      if (on && start < 0) start = x;
      if (!on && start >= 0) { k++; for (let y = y0 - 6; y < y1 + 6; y++) for (let xx = start; xx < x; xx++) if (fg(y * W + xx)) lab[y * W + xx] = k; start = -1; }
    }
  }
  for (let i = 0; i < lab.length; i++) if (lab[i] === 255) lab[i] = k + 1;
  return lab;
}
function fileLabels(image) { const d = pixels(image).data, lab = new Uint8Array(W * H); for (let i = 0; i < lab.length; i++) lab[i] = d[i * 4]; return lab; }

// Cut each part into its own sprite with alpha; black-backed pictures get a soft luminance edge.
function parts(pic, lab, transparent, letterCount) {
  const d = pic.data, out = [], box = new Map();
  for (let i = 0; i < lab.length; i++) {
    const k = lab[i]; if (!k) continue;
    const x = i % W, y = (i / W) | 0, b = box.get(k) || [W, H, 0, 0];
    if (x < b[0]) b[0] = x; if (y < b[1]) b[1] = y; if (x > b[2]) b[2] = x; if (y > b[3]) b[3] = y; box.set(k, b);
  }
  for (const [k, [x0, y0, x1, y1]] of [...box].sort((a, b) => a[0] - b[0])) {
    const w = x1 - x0 + 1, h = y1 - y0 + 1, c = cv(w, h), g = c.getContext('2d'), o = g.createImageData(w, h);
    for (let y = 0; y < h; y++) for (let x = 0; x < w; x++) {
      const i = (y0 + y) * W + x0 + x, j = (y * w + x) * 4;
      if (lab[i] !== k) continue;
      o.data[j] = d[i * 4]; o.data[j + 1] = d[i * 4 + 1]; o.data[j + 2] = d[i * 4 + 2];
      const m = Math.max(d[i * 4], d[i * 4 + 1], d[i * 4 + 2]) / 255;
      o.data[j + 3] = transparent ? d[i * 4 + 3] : 255 * clamp((m - .05) / .1);
    }
    g.putImageData(o, 0, 0);
    out.push({ c, x: x0, y: y0, w, h, k, ribbon: letterCount ? k > letterCount : y1 < .24 * H });
  }
  return out;
}

function colourMap(lab) {
  const c = cv(), g = c.getContext('2d'), o = g.createImageData(W, H), R = rng(9), pal = [[0, 0, 0]];
  for (let k = 1; k < 256; k++) pal.push([60 + R() * 195 | 0, 60 + R() * 195 | 0, 60 + R() * 195 | 0]);
  for (let i = 0; i < lab.length; i++) { const p = pal[lab[i]]; o.data[i * 4] = p[0]; o.data[i * 4 + 1] = p[1]; o.data[i * 4 + 2] = p[2]; o.data[i * 4 + 3] = 255; }
  g.putImageData(o, 0, 0); return c;
}

const [orig, sep, samLab, layLab] = await Promise.all([img('../assets/crews.png'), img('../assets/crews-separable.png'), img('../assets/crews-sam21-labels.png'), img('../assets/crews-layers-labels.png')]);
const origPix = pixels(orig), sepPix = pixels(sep);
const variants = [
  { title: '1 · split by gaps', sub: 'chunks: letters that touch stay glued', lab: chunkLabels(origPix), pic: origPix, transparent: false },
  { title: '2 · SAM 2.1 segmentation', sub: 'same picture, cut into 15 letters', lab: fileLabels(samLab), pic: origPix, transparent: false },
  { title: '3 · generated apart', sub: 'transparent picture, letters never touch', lab: fileLabels(layLab), pic: sepPix, transparent: true, letterCount: 15 },
].map(v => {
  const ps = parts(v.pic, v.lab, v.transparent, v.letterCount), R = rng(31);
  const letters = ps.filter(p => !p.ribbon).sort((a, b) => a.k - b.k);
  letters.forEach((p, i) => { p.t0 = MAP_END + .25 + i * .05; p.z = .3 + R() * .7; p.spin = (R() - .5) * 16; });
  ps.filter(p => p.ribbon).forEach((p, i) => { p.t0 = MAP_END + .05 + i * .05; p.z = 1.4; p.spin = (R() - .5) * 20; });
  return { ...v, parts: [...ps.filter(p => p.ribbon), ...letters], map: colourMap(v.lab), count: letters.length, ribbons: ps.length - letters.length, panel: cv() };
});

function drawPanel(v, t) {
  const g = v.panel.getContext('2d');
  g.setTransform(1, 0, 0, 1, 0, 0); g.globalAlpha = 1; g.filter = 'none'; g.fillStyle = '#060505'; g.fillRect(0, 0, W, H);
  if (t < MAP_END) { g.globalAlpha = 1 - clamp((t - MAP_END + .15) / .15); g.drawImage(v.map, 0, 0); g.globalAlpha = 1; return; }
  const pan = clamp((t - 3.0) / 1.2), waveT = t - 2.25;
  for (const p of v.parts) {
    const u = (t - p.t0) / .32;
    if (u <= 0) continue;
    const land = outBack(u), air = 1 - outCubic(u);
    const cx = p.x + p.w / 2, cy = p.y + p.h / 2;
    const wave = waveT > 0 ? -34 * Math.max(0, Math.sin(Math.PI * clamp((waveT - (cx / W) * .35) / .28))) : 0;
    const dx = (pan - .5) * 70 * p.z, dy = -260 * air + wave, scale = 1 + .35 * air, rot = p.spin * air * Math.PI / 180;
    const lift = air + (wave ? -wave / 120 : 0);
    // Shadow grows softer and further away the higher a part is above the page.
    g.save(); g.translate(cx + dx + 12 + 40 * lift, cy + dy * .2 + 20 + 60 * lift); g.rotate(rot); g.scale(scale, scale);
    g.filter = `blur(${6 + 22 * lift}px) brightness(0)`; g.globalAlpha = .55 * clamp(u * 3) * (1 - .4 * lift);
    g.drawImage(p.c, -p.w / 2, -p.h / 2); g.restore();
    g.save(); g.translate(cx + dx, cy + dy); g.rotate(rot); g.scale(scale, scale); g.filter = 'none'; g.globalAlpha = clamp(u * 4);
    g.drawImage(p.c, -p.w / 2, -p.h / 2); g.restore();
  }
}

const out = document.getElementById('c'), ctx = out.getContext('2d');
function renderFrame(t) {
  ctx.fillStyle = '#121212'; ctx.fillRect(0, 0, OUT_W, OUT_H);
  variants.forEach((v, i) => {
    drawPanel(v, t);
    const x = 60 + i * 630;
    ctx.drawImage(v.panel, x, 104, 540, 960);
    ctx.fillStyle = '#ffd84a'; ctx.font = '600 26px -apple-system, Helvetica, sans-serif'; ctx.fillText(v.title, x, 46);
    ctx.fillStyle = '#bdbdbd'; ctx.font = '19px -apple-system, Helvetica, sans-serif';
    ctx.fillText(`${v.sub} — ${v.count} parts${v.ribbons ? ` + ${v.ribbons} ribbon layer${v.ribbons > 1 ? 's' : ''}` : ''}`, x, 80);
  });
}
window.renderFrame = renderFrame; window.DURATION = DURATION; window.TIMES = {}; window.ready = true;
if (new URLSearchParams(location.search).has('play')) { const s = performance.now(); const loop = () => { renderFrame(((performance.now() - s) / 1000) % DURATION); requestAnimationFrame(loop); }; loop(); }
else renderFrame(1.6);
