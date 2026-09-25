import { BEAT, COLOR, b } from '../config';
import { backdrop } from '../draw/fx';
import { drawSlate } from '../draw/slate';
import { slamLine } from '../draw/text';
import type { Env } from '../env';
import { decay, easeInExpo, easeOutCubic, progress, type Ctx } from '../util';

const BOARD = { x: 90, y: 500, w: 900 };
const OPEN = -0.46;
export const SLATE_LINES = ['NOW MAKE', 'ONE.'];

/** Rises once the hook clears (beats 5.5–7.4), claps on beat 8, whips away into the clock on beat 12. */
export function drawSlateScene(ctx: Ctx, t: number, env: Env) {
  if (t >= b(8)) backdrop(ctx, env.fx, { glow: 0.2, glowY: 820 });

  const rise = easeOutCubic(progress(t, b(5.5), b(7.4)));
  const close = progress(t, b(7.55), b(8));
  const arm = t < b(8) ? OPEN * (1 - close * close) : -0.04 * decay(t, b(8), 0.05);
  const push = 1 + 0.035 * easeOutCubic(progress(t, b(8), b(12)));
  const whip = easeInExpo(progress(t, b(11.5), b(12)));

  ctx.save();
  ctx.translate(0, (1 - rise) * 1350 - whip * 1700);
  ctx.translate(540, 780);
  ctx.scale(push, push);
  ctx.translate(-540, -780);
  drawSlate(ctx, BOARD.x, BOARD.y, BOARD.w, {
    arm,
    you: progress(t, b(10), b(10.25)),
    blink: ((t - b(10)) / BEAT) % 0.5 < 0.25,
    split: 2 + 10 * decay(t, b(8), 0.08),
  });
  ctx.restore();

  const size = env.layout.slate;
  const base = 1235;
  ctx.save();
  ctx.translate(0, -whip * 1700);
  slamLine(ctx, SLATE_LINES[0], 92, base, size, t, b(8));
  slamLine(ctx, SLATE_LINES[1], 92, base + size * 0.88, size, t, b(9), { color: COLOR.red, split: 4 });
  ctx.restore();
}
