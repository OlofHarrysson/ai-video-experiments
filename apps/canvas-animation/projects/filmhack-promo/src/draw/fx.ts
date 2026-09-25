import { COLOR, H, W } from '../config';
import { canvas, hash, rng, type Ctx } from '../util';

export interface Fx {
  grain: HTMLCanvasElement[];
  vignette: HTMLCanvasElement;
  grid: HTMLCanvasElement;
  buf: { el: HTMLCanvasElement; ctx: Ctx };
  chan: { el: HTMLCanvasElement; ctx: Ctx };
}

export interface PostState {
  /** Horizontal RGB channel separation in px. */
  rgb: number;
  /** Displaced-slice glitch strength, 0–1. */
  slices: number;
  /** White flash opacity. */
  flash: number;
  seed: number;
}

export function createFx(): Fx {
  const grain: HTMLCanvasElement[] = [];
  for (let k = 0; k < 6; k++) {
    const tile = canvas(256, 256);
    const img = tile.ctx.createImageData(256, 256);
    const random = rng(1000 + k);
    for (let i = 0; i < img.data.length; i += 4) {
      const v = random() * 255;
      img.data[i] = img.data[i + 1] = img.data[i + 2] = v;
      img.data[i + 3] = 255;
    }
    tile.ctx.putImageData(img, 0, 0);
    grain.push(tile.el);
  }

  const vignette = canvas(W, H);
  const v = vignette.ctx.createRadialGradient(W / 2, H * 0.47, H * 0.22, W / 2, H * 0.5, H * 0.78);
  v.addColorStop(0, 'rgba(0,0,0,0)');
  v.addColorStop(1, 'rgba(0,0,0,0.6)');
  vignette.ctx.fillStyle = v;
  vignette.ctx.fillRect(0, 0, W, H);

  const grid = canvas(W, H);
  grid.ctx.fillStyle = '#ffffff';
  for (let x = 0; x <= W; x += 90) grid.ctx.fillRect(x, 0, 1, H);
  for (let y = 0; y <= H; y += 90) grid.ctx.fillRect(0, y, W, 1);

  return { grain, vignette: vignette.el, grid: grid.el, buf: canvas(W, H), chan: canvas(W, H) };
}

/** Black stage with the site's red bloom and faint grid. */
export function backdrop(ctx: Ctx, fx: Fx, opts: { glow?: number; glowY?: number; grid?: number } = {}) {
  ctx.fillStyle = COLOR.ink;
  ctx.fillRect(-60, -60, W + 120, H + 120);
  const glow = opts.glow ?? 0.2;
  if (glow > 0) {
    const y = opts.glowY ?? H * 0.45;
    const g = ctx.createRadialGradient(W / 2, y, 0, W / 2, y, H * 0.55);
    g.addColorStop(0, `rgba(200,5,40,${glow})`);
    g.addColorStop(0.5, `rgba(110,3,22,${glow * 0.35})`);
    g.addColorStop(1, 'rgba(0,0,0,0)');
    ctx.fillStyle = g;
    ctx.fillRect(-60, -60, W + 120, H + 120);
  }
  const grid = opts.grid ?? 0.035;
  if (grid > 0) {
    ctx.save();
    ctx.globalAlpha = grid;
    ctx.drawImage(fx.grid, 0, 0);
    ctx.restore();
  }
}

export function post(ctx: Ctx, fx: Fx, state: PostState, frame: number) {
  ctx.save();
  ctx.setTransform(1, 0, 0, 1, 0, 0);
  ctx.globalAlpha = 1;
  ctx.globalCompositeOperation = 'source-over';
  if (state.slices > 0.02) sliceGlitch(ctx, fx, state.slices, state.seed);
  if (state.rgb > 0.5) rgbSplit(ctx, fx, state.rgb);
  if (state.flash > 0.01) {
    ctx.globalAlpha = Math.min(1, state.flash);
    ctx.fillStyle = COLOR.white;
    ctx.fillRect(0, 0, W, H);
    ctx.globalAlpha = 1;
  }

  // Two-pixel film grain, light enough to survive Instagram's compression.
  const pattern = ctx.createPattern(fx.grain[frame % fx.grain.length], 'repeat')!;
  ctx.globalCompositeOperation = 'screen';
  ctx.globalAlpha = 0.05;
  ctx.translate(-hash(frame) * 512, -hash(frame + 7919) * 512);
  ctx.scale(2, 2);
  ctx.fillStyle = pattern;
  ctx.fillRect(0, 0, W / 2 + 512, H / 2 + 512);
  ctx.setTransform(1, 0, 0, 1, 0, 0);
  ctx.globalCompositeOperation = 'source-over';
  ctx.globalAlpha = 1;
  ctx.drawImage(fx.vignette, 0, 0);
  ctx.restore();
}

function snapshot(ctx: Ctx, fx: Fx) {
  fx.buf.ctx.globalCompositeOperation = 'copy';
  fx.buf.ctx.drawImage(ctx.canvas, 0, 0);
}

/** Separate red from cyan (green + blue) and push them apart horizontally. */
function rgbSplit(ctx: Ctx, fx: Fx, amount: number) {
  snapshot(ctx, fx);
  ctx.globalCompositeOperation = 'copy';
  ctx.fillStyle = '#000';
  ctx.fillRect(0, 0, W, H);
  ctx.globalCompositeOperation = 'lighter';
  for (const [tint, dx] of [['#ff0000', amount], ['#00ffff', -amount]] as const) {
    fx.chan.ctx.globalCompositeOperation = 'copy';
    fx.chan.ctx.drawImage(fx.buf.el, 0, 0);
    fx.chan.ctx.globalCompositeOperation = 'multiply';
    fx.chan.ctx.fillStyle = tint;
    fx.chan.ctx.fillRect(0, 0, W, H);
    ctx.drawImage(fx.chan.el, dx, 0);
  }
  ctx.globalCompositeOperation = 'source-over';
}

function sliceGlitch(ctx: Ctx, fx: Fx, amount: number, seed: number) {
  snapshot(ctx, fx);
  const random = rng(seed * 31 + 5);
  const count = 4 + Math.floor(amount * 14);
  for (let i = 0; i < count; i++) {
    const y = random() * H;
    const h = 6 + random() * random() * 240 * amount;
    const dx = (random() - 0.5) * 2 * 190 * amount;
    ctx.drawImage(fx.buf.el, 0, y, W, h, dx, y, W, h);
    if (random() < 0.3 * amount) {
      ctx.globalCompositeOperation = 'difference';
      ctx.globalAlpha = 0.55;
      ctx.fillStyle = random() < 0.5 ? COLOR.cyan : COLOR.red;
      ctx.fillRect(0, y, W, h * 0.6);
      ctx.globalCompositeOperation = 'source-over';
      ctx.globalAlpha = 1;
    }
  }
}
