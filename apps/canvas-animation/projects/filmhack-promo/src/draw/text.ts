import { COLOR, white } from '../config';
import { clamp, decay, easeOutExpo, hash2, lerp, type Ctx } from '../util';
import { font } from './fonts';

/** Largest size (≤ maxPx) at which every line fits within maxWidth. */
export function fitSize(ctx: Ctx, lines: string[], face: (px: number) => string, maxWidth: number, maxPx: number) {
  ctx.save();
  ctx.font = face(100);
  ctx.letterSpacing = '0px';
  const widest = Math.max(...lines.map((line) => ctx.measureText(line).width));
  ctx.restore();
  return Math.min(maxPx, Math.floor((maxWidth / widest) * 100));
}

/** The site's chromatic offset: cyan fringe left, red fringe right, fill on top. */
export function glitchText(ctx: Ctx, text: string, x: number, y: number, split: number, fill: string = COLOR.white) {
  if (split > 0.4) {
    ctx.save();
    ctx.globalCompositeOperation = 'lighter';
    ctx.fillStyle = COLOR.glitchCyan;
    ctx.fillText(text, x - split, y);
    ctx.fillStyle = COLOR.glitchRed;
    ctx.fillText(text, x + split, y);
    ctx.restore();
  }
  ctx.fillStyle = fill;
  ctx.fillText(text, x, y);
}

export interface SlamOptions {
  color?: string;
  /** Resting chromatic offset in px. */
  split?: number;
  align?: CanvasTextAlign;
  face?: (px: number) => string;
  /** Starting scale of the slam. */
  from?: number;
}

/** A display line that slams in at t0: overshoot scale, glitch burst, then a steady offset. */
export function slamLine(ctx: Ctx, text: string, x: number, y: number, size: number, t: number, t0: number, opts: SlamOptions = {}) {
  if (t < t0) return;
  const p = clamp((t - t0) / 0.16);
  const scale = lerp(opts.from ?? 1.22, 1, easeOutExpo(p));
  const split = (opts.split ?? 3) + 20 * decay(t, t0, 0.08);
  const pivotY = y - size * 0.34;
  ctx.save();
  ctx.font = (opts.face ?? font.display)(size);
  ctx.textAlign = opts.align ?? 'left';
  ctx.textBaseline = 'alphabetic';
  ctx.translate(x, pivotY);
  ctx.scale(scale, scale);
  ctx.globalAlpha *= clamp(p * 5);
  glitchText(ctx, text, 0, y - pivotY, split, opts.color);
  ctx.restore();
}

export interface LabelOptions {
  size?: number;
  color?: string;
  align?: CanvasTextAlign;
  weight?: 400 | 500 | 700;
  spacing?: number;
}

/** Tracked uppercase mono label, the site's small-caps voice. */
export function label(ctx: Ctx, text: string, x: number, y: number, opts: LabelOptions = {}) {
  ctx.save();
  ctx.font = font.mono(opts.size ?? 26, opts.weight ?? 500);
  ctx.letterSpacing = `${opts.spacing ?? 3}px`;
  ctx.fillStyle = opts.color ?? white(0.55);
  ctx.textAlign = opts.align ?? 'left';
  ctx.textBaseline = 'alphabetic';
  ctx.fillText(text, x, y);
  ctx.restore();
}

export function measureLabel(ctx: Ctx, text: string, size: number, spacing = 3, weight: 400 | 500 | 700 = 500) {
  ctx.save();
  ctx.font = font.mono(size, weight);
  ctx.letterSpacing = `${spacing}px`;
  const width = ctx.measureText(text).width;
  ctx.restore();
  return width;
}

const GLYPHS = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789#%&*+=/<>';

/** Replace a share of characters with random glyphs; stable for a given seed. */
export function scramble(text: string, amount: number, seed: number) {
  let out = '';
  for (let i = 0; i < text.length; i++) {
    const c = text[i];
    out += c === ' ' || hash2(seed, i) >= amount ? c : GLYPHS[Math.floor(hash2(seed + 7, i) * GLYPHS.length)];
  }
  return out;
}
