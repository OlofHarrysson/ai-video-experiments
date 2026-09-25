import { FPS, H, b } from '../config';
import { backdrop } from '../draw/fx';
import { slamLine } from '../draw/text';
import type { Env } from '../env';
import { clamp, easeInCubic, progress, type Ctx } from '../util';

export const HOOK_LINES = ["YOU'VE", 'WATCHED', 'ENOUGH.'];
/** The flick lands on our (black) reel on beat 1. */
const LAND = b(1);
const GAP = 28;

export function drawHook(ctx: Ctx, t: number, env: Env) {
  if (t < LAND) {
    drawFlick(ctx, t, env);
    return;
  }
  backdrop(ctx, env.fx, { glow: 0.22 * progress(t, LAND, LAND + 0.5), glowY: 880 });

  const size = env.layout.hook;
  const lineH = size * 0.88;
  const first = 880 - (0.7 * size + 2 * lineH) / 2 + 0.7 * size;
  const exit = easeInCubic(progress(t, b(5), b(6.25)));
  ctx.save();
  ctx.translate(0, -1300 * exit);
  ctx.globalAlpha = 1 - exit;
  HOOK_LINES.forEach((line, i) => slamLine(ctx, line, 92, first + i * lineH, size, t, b(1 + i)));
  ctx.restore();
}

/** Two generic Reels accelerate past with motion blur and slam to a stop on ours. */
function drawFlick(ctx: Ctx, t: number, env: Env) {
  const cards = env.feed;
  const pitch = H + GAP;
  const total = cards.length * pitch;
  const offset = (x: number) => total * Math.pow(clamp(x / LAND), 2);
  const samples = 8;
  const shutter = 0.5 / FPS;
  ctx.save();
  ctx.globalCompositeOperation = 'lighter';
  ctx.globalAlpha = 1 / samples;
  for (let k = 0; k < samples; k++) {
    const off = offset(t - (shutter * k) / (samples - 1));
    cards.forEach((card, i) => {
      const y = i * pitch - off;
      if (y < H && y + H > 0) ctx.drawImage(card, 0, y);
    });
  }
  ctx.restore();
}
