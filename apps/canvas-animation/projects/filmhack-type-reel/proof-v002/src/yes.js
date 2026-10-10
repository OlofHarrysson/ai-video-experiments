import { W, H, C, FPS, canvas, clamp, smooth, frameIndex } from './util.js';

// YES.: generated chrome target used as an image layer, animated in code (slam, flat identity flips, travelling light band).
export function createYes({ image, anton }) {
  const chrome = canvas(), g = chrome.getContext('2d');
  g.fillStyle = '#000'; g.fillRect(0, 0, W, H);
  g.drawImage(image, 0, 0, W, H);
  // The target bakes a squashed doubt under the S; remove it so the code doubt is the only one.
  const cut = H * .835, fade = g.createLinearGradient(0, cut - 24, 0, cut + 10);
  fade.addColorStop(0, 'rgba(0,0,0,0)'); fade.addColorStop(1, 'rgba(0,0,0,1)');
  g.fillStyle = fade; g.fillRect(0, cut - 24, W, H - cut + 24);

  // Letter mask from luminance, used to confine the light band to the metal.
  const mask = canvas(), mg = mask.getContext('2d');
  const src = g.getImageData(0, 0, W, H), out = mg.createImageData(W, H);
  for (let i = 0; i < src.data.length; i += 4) {
    const l = (.3 * src.data[i] + .59 * src.data[i + 1] + .11 * src.data[i + 2]) / 255;
    out.data[i] = out.data[i + 1] = out.data[i + 2] = 255;
    out.data[i + 3] = 255 * smooth(.08, .2, l);
  }
  mg.putImageData(out, 0, 0);

  // Flat identities for the hard flips: extended Anton capitals, stacked like the chrome.
  const rows = [['Y', 60, 600], ['E', 640, 1080], ['S.', 1110, 1560]];
  const flat = new Path2D();
  for (const [ch, top, bottom] of rows) {
    const p = anton.getPath(ch, 0, 0, 100), b = p.getBoundingBox();
    const sy = (bottom - top) / (b.y2 - b.y1), sx = Math.min(sy * 1.75, 860 / (b.x2 - b.x1));
    const m = new DOMMatrix().translate(W / 2, top).scale(sx, sy).translate(-(b.x1 + b.x2) / 2, -b.y1);
    flat.addPath(new Path2D(p.toPathData(3)), m);
  }

  const band = canvas(), bg = band.getContext('2d');

  function drawFlat(ctx, kind) {
    ctx.save();
    if (kind === 'red') { ctx.fillStyle = C.crimson; ctx.fill(flat); }
    else { ctx.lineJoin = 'round'; ctx.strokeStyle = C.cyan; ctx.lineWidth = 16; ctx.stroke(flat); ctx.strokeStyle = '#000'; ctx.lineWidth = 7; ctx.stroke(flat); }
    ctx.restore();
  }

  const draw = function (ctx, t, T0, { accent = [] } = {}) {
    const local = t - T0, f = frameIndex(t, T0);
    if (local < 0) return;
    if (f <= 1) return drawFlat(ctx, 'red');
    if (f <= 3) return drawFlat(ctx, 'cyan');
    for (const a of accent) { const fa = frameIndex(t, a); if (fa >= 0 && fa <= 1) return drawFlat(ctx, 'cyan'); }
    const tau = local - 4 / FPS;
    const s = 1 + .13 * Math.exp(-tau / .07) * Math.cos(tau * 38) + .018 * clamp(local / .9);
    ctx.save();
    ctx.translate(W / 2, 820); ctx.scale(s, s); ctx.translate(-W / 2, -820);
    ctx.drawImage(chrome, 0, 0);
    // Light band travelling diagonally through the letters.
    const p = clamp((local - .1) / .5);
    if (p > 0 && p < 1) {
      bg.globalCompositeOperation = 'source-over'; bg.clearRect(0, 0, W, H);
      bg.save(); bg.translate(W / 2, H / 2); bg.rotate(-0.95);
      const x = -1500 + 3000 * p, gr = bg.createLinearGradient(x - 170, 0, x + 170, 0);
      gr.addColorStop(0, 'rgba(255,190,140,0)'); gr.addColorStop(.42, 'rgba(255,215,180,.55)');
      gr.addColorStop(.5, 'rgba(255,255,255,.95)'); gr.addColorStop(.58, 'rgba(160,240,255,.5)'); gr.addColorStop(1, 'rgba(120,230,255,0)');
      bg.fillStyle = gr; bg.fillRect(x - 170, -2000, 340, 4000); bg.restore();
      bg.globalCompositeOperation = 'destination-in'; bg.drawImage(mask, 0, 0);
      ctx.globalCompositeOperation = 'lighter'; ctx.drawImage(band, 0, 0);
    }
    ctx.restore();
  };
  draw.layers = { picture: chrome, metal: mask, flat };
  return draw;
}
