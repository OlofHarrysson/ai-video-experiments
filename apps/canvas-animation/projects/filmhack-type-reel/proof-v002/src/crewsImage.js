import { W, H, C, canvas, clamp, ease, frameIndex } from './util.js';
import { layer, lumaMask, drawMasked } from './imagecard.js';

// CREWS / FORM / FRIDAY: the generated ribbon lettering is laid letter by letter behind a lone thread.
const BANDS = { ribbons: [0, .222], lines: [[.222, .378], [.39, .552], [.558, .728]] };

function columns(mask, y0, y1) {
  const g = mask.getContext('2d'), d = g.getImageData(0, y0, W, y1 - y0).data, cols = [];
  let start = -1;
  for (let x = 0; x < W; x++) {
    let sum = 0; for (let y = 0; y < y1 - y0; y += 2) sum += d[(y * W + x) * 4 + 3];
    const on = sum > 255 * 3;
    if (on && start < 0) start = x;
    if (!on && start >= 0) { if (x - start > 24) cols.push([start, x]); start = -1; }
  }
  if (start >= 0) cols.push([start, W]);
  return cols;
}

export function createCrewsImage({ image, anton }) {
  const lit = layer(image), fg = lumaMask(lit, .06, .16);
  const letters = [];
  BANDS.lines.forEach(([a, b], li) => {
    const y0 = Math.round(a * H), y1 = Math.round(b * H);
    for (const [x0, x1] of columns(fg, y0, y1)) letters.push({ x0: x0 - 6, x1: x1 + 6, y0: y0 - 6, y1: y1 + 6, line: li });
  });
  letters.forEach((l, i) => l.t0 = .1 + i * .028 + l.line * .03);
  const lineFront = BANDS.lines.map((_, li) => letters.filter(l => l.line === li));

  // Flat cyan inline identity for the beat flip, matching YES.
  const flat = new Path2D();
  BANDS.lines.forEach(([a, b], li) => {
    const text = ['CREWS', 'FORM', 'FRIDAY'][li], p = anton.getPath(text, 0, 0, 100), bb = p.getBoundingBox();
    const sy = (b - a) * H * .86 / (bb.y2 - bb.y1), sx = Math.min(sy * 1.5, 880 / (bb.x2 - bb.x1));
    flat.addPath(new Path2D(p.toPathData(3)), new DOMMatrix().translate(W / 2, a * H + (b - a) * H * .07).scale(sx, sy).translate(-(bb.x1 + bb.x2) / 2, -bb.y1));
  });

  const glint = canvas(), gg = glint.getContext('2d');

  return function draw(ctx, t, T0, { accent = [] } = {}) {
    const u = t - T0;
    if (u < 0) return;
    for (const a of accent) {
      const f = frameIndex(t, a);
      if (f >= 0 && f <= 1) { ctx.save(); ctx.lineJoin = 'round'; ctx.strokeStyle = C.cyan; ctx.lineWidth = 14; ctx.stroke(flat); ctx.strokeStyle = '#000'; ctx.lineWidth = 6; ctx.stroke(flat); ctx.restore(); return; }
    }
    // Loose ribbons fall in from the top.
    const drop = ease.outCubic(u / .16) * BANDS.ribbons[1] * H;
    drawMasked(ctx, lit, g => { const gr = g.createLinearGradient(0, drop - 60, 0, drop); gr.addColorStop(0, '#fff'); gr.addColorStop(1, 'rgba(255,255,255,0)'); g.fillStyle = gr; g.fillRect(0, 0, W, Math.min(drop, BANDS.ribbons[1] * H + 10)); });

    // The lone thread runs along each line just ahead of the letters, then fades.
    ctx.save(); ctx.strokeStyle = C.ivory; ctx.lineCap = 'round'; ctx.lineWidth = 2.2; ctx.shadowColor = 'rgba(242,232,213,.7)'; ctx.shadowBlur = 8;
    lineFront.forEach((ls, li) => {
      const [a, b] = BANDS.lines[li], y = (a + (b - a) * .55) * H, first = ls[0], last = ls[ls.length - 1];
      const p = clamp((u - first.t0 + .06) / (last.t0 - first.t0 + .14)), fade = 1 - clamp((u - last.t0 - .14) / .12);
      if (p <= 0 || fade <= 0) return;
      ctx.globalAlpha = fade; ctx.beginPath(); ctx.moveTo(first.x0 - 60, y); ctx.lineTo(first.x0 - 60 + (last.x1 - first.x0 + 120) * ease.outCubic(p), y); ctx.stroke();
    });
    ctx.restore();

    // Each letter is laid with a diagonal wipe and a small settle; a glint rides the wipe front.
    gg.globalCompositeOperation = 'source-over'; gg.clearRect(0, 0, W, H);
    for (const l of letters) {
      const p = clamp((u - l.t0) / .14);
      if (p <= 0) continue;
      const settle = (1 - ease.outBack(p)) * -22, w = l.x1 - l.x0, h = l.y1 - l.y0, front = ease.outCubic(p) * (w + h) * 1.1;
      const paint = g => {
        g.save(); g.translate(0, settle); g.beginPath(); g.rect(l.x0, l.y0, w, h); g.clip();
        const gr = g.createLinearGradient(l.x0, l.y0, l.x0 + front * .7, l.y0 + front * .7);
        gr.addColorStop(0, '#fff'); gr.addColorStop(Math.max(0, 1 - 40 / (front + 1)), '#fff'); gr.addColorStop(1, 'rgba(255,255,255,0)');
        g.fillStyle = gr; g.fillRect(l.x0, l.y0, w, h); g.restore();
      };
      ctx.save(); ctx.translate(0, settle); drawMasked(ctx, lit, g => { g.save(); g.translate(0, -settle); paint(g); g.restore(); }); ctx.restore();
      if (p < 1) {
        gg.save(); gg.translate(0, settle); gg.beginPath(); gg.rect(l.x0, l.y0, w, h); gg.clip();
        const fx = l.x0 + front * .7, fy = l.y0 + front * .7, gl = gg.createLinearGradient(fx - 50, fy - 50, fx + 10, fy + 10);
        gl.addColorStop(0, 'rgba(255,240,210,0)'); gl.addColorStop(.8, 'rgba(255,248,230,.95)'); gl.addColorStop(1, 'rgba(255,255,255,0)');
        gg.fillStyle = gl; gg.fillRect(l.x0, l.y0, w, h); gg.restore();
      }
    }
    gg.globalCompositeOperation = 'destination-in'; gg.drawImage(fg, 0, 0);
    ctx.save(); ctx.globalCompositeOperation = 'lighter'; ctx.drawImage(glint, 0, 0); ctx.restore();

    // After the letters land, a light band travels through the ribbons.
    const sweep = clamp((u - .78) / .5);
    if (sweep > 0 && sweep < 1) drawMasked(ctx, lit, g => {
      g.save(); g.translate(W / 2, H * .47); g.rotate(-.9); const x = -1400 + 2800 * sweep, gr = g.createLinearGradient(x - 140, 0, x + 140, 0);
      gr.addColorStop(0, 'rgba(255,255,255,0)'); gr.addColorStop(.5, 'rgba(255,255,255,.75)'); gr.addColorStop(1, 'rgba(255,255,255,0)');
      g.fillStyle = gr; g.fillRect(x - 140, -1800, 280, 3600); g.restore(); g.globalCompositeOperation = 'destination-in'; g.drawImage(fg, 0, 0);
    }, { op: 'lighter', alpha: .55 });
  };
}
