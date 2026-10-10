import { W, H, canvas, smooth } from './util.js';

// Helpers for animating generated stills in code: full-frame layers, masks derived from pixels, bright-spot detection.

export function layer(image) {
  const c = canvas(), g = c.getContext('2d');
  g.fillStyle = '#000'; g.fillRect(0, 0, W, H); g.drawImage(image, 0, 0, W, H); return c;
}

// Build a white mask whose alpha comes from fn(r, g, b) in 0..1.
export function maskFrom(src, fn) {
  const m = canvas(), mg = m.getContext('2d');
  const d = src.getContext('2d').getImageData(0, 0, W, H), o = mg.createImageData(W, H);
  for (let i = 0; i < d.data.length; i += 4) {
    o.data[i] = o.data[i + 1] = o.data[i + 2] = 255;
    o.data[i + 3] = 255 * fn(d.data[i] / 255, d.data[i + 1] / 255, d.data[i + 2] / 255);
  }
  mg.putImageData(o, 0, 0); return m;
}
export const luma = (r, g, b) => .3 * r + .59 * g + .11 * b;
export const lumaMask = (src, lo, hi) => maskFrom(src, (r, g, b) => smooth(lo, hi, luma(r, g, b)));

// Per-pixel tone transform into a new layer.
export function toned(src, fn) {
  const c = canvas(), cg = c.getContext('2d');
  const d = src.getContext('2d').getImageData(0, 0, W, H);
  for (let i = 0; i < d.data.length; i += 4) {
    const [r, g, b] = fn(d.data[i] / 255, d.data[i + 1] / 255, d.data[i + 2] / 255);
    d.data[i] = 255 * r; d.data[i + 1] = 255 * g; d.data[i + 2] = 255 * b;
  }
  cg.putImageData(d, 0, 0); return c;
}

// Bright-spot centres (bulbs): local luminance maxima above a threshold on a half-resolution grid.
export function brightSpots(src, threshold = .9, minGap = 9) {
  const s = 2, w = W / s, h = H / s, small = canvas(w, h), sg = small.getContext('2d');
  sg.drawImage(src, 0, 0, w, h);
  const d = sg.getImageData(0, 0, w, h).data, L = new Float32Array(w * h);
  for (let i = 0; i < w * h; i++) L[i] = luma(d[i * 4] / 255, d[i * 4 + 1] / 255, d[i * 4 + 2] / 255);
  const spots = [], taken = new Uint8Array(w * h), r = Math.ceil(minGap / s);
  const order = [...L.keys()].filter(i => L[i] >= threshold).sort((a, b) => L[b] - L[a]);
  for (const i of order) {
    if (taken[i]) continue;
    const x = i % w, y = (i / w) | 0;
    spots.push({ x: x * s, y: y * s, v: L[i] });
    for (let dy = -r; dy <= r; dy++) for (let dx = -r; dx <= r; dx++) {
      const xx = x + dx, yy = y + dy; if (xx >= 0 && yy >= 0 && xx < w && yy < h) taken[yy * w + xx] = 1;
    }
  }
  return spots;
}

// Row bands of foreground (e.g. lines of lettering) from a mask's horizontal projection.
export function rowBands(mask, minRows = 30, minFill = .004) {
  const d = mask.getContext('2d').getImageData(0, 0, W, H).data, bands = [];
  let start = -1;
  for (let y = 0; y < H; y++) {
    let sum = 0; for (let x = 0; x < W; x += 2) sum += d[(y * W + x) * 4 + 3];
    const on = sum / 255 / (W / 2) > minFill;
    if (on && start < 0) start = y;
    if (!on && start >= 0) { if (y - start >= minRows) bands.push([start, y]); start = -1; }
  }
  if (start >= 0 && H - start >= minRows) bands.push([start, H]);
  return bands;
}

// Draw `src` through `mask` (both full-frame) onto ctx using a scratch canvas.
const scratch = canvas(), sc = scratch.getContext('2d');
export function drawMasked(ctx, src, paintMask, { op = 'source-over', alpha = 1 } = {}) {
  sc.globalCompositeOperation = 'source-over'; sc.globalAlpha = 1; sc.clearRect(0, 0, W, H);
  paintMask(sc);
  sc.globalCompositeOperation = 'source-in'; sc.drawImage(src, 0, 0);
  ctx.save(); ctx.globalCompositeOperation = op; ctx.globalAlpha = alpha; ctx.drawImage(scratch, 0, 0); ctx.restore();
}
