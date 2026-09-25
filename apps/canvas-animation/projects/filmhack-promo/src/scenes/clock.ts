import { COLOR, b } from '../config';
import { drawClockPanel, lerpRect, remaining, wallClock, type Rect } from '../draw/clock';
import { backdrop } from '../draw/fx';
import { slamLine } from '../draw/text';
import type { Env } from '../env';
import { easeInExpo, easeInOutCubic, easeOutBack, progress, type Ctx } from '../util';

export const CLOCK_BIG: Rect = { x: 90, y: 560, w: 900, h: 330 };
export const CLOCK_HUD: Rect = { x: 200, y: 232, w: 680, h: 249 };
export const CLOCK_LINES = ['48 HOURS.', 'ONE FILM.'];

/** Beats 12–16: the countdown appears, starts ticking, then docks at the top as the montage HUD. */
export function drawClockScene(ctx: Ctx, t: number, env: Env) {
  backdrop(ctx, env.fx, { glow: 0.2, glowY: 760 });

  const pop = easeOutBack(progress(t, b(12), b(12) + 0.22), 2.2);
  const dock = easeInOutCubic(progress(t, b(15.35), b(16)));
  const rect = lerpRect(CLOCK_BIG, CLOCK_HUD, dock);
  ctx.save();
  ctx.translate(rect.x + rect.w / 2, rect.y + rect.h / 2);
  ctx.scale(0.86 + 0.14 * pop, 0.86 + 0.14 * pop);
  ctx.translate(-(rect.x + rect.w / 2), -(rect.y + rect.h / 2));
  drawClockPanel(ctx, rect, remaining(t), t, wallClock(t));
  ctx.restore();

  const size = env.layout.clock;
  const exit = easeInExpo(progress(t, b(15.4), b(16)));
  ctx.save();
  ctx.translate(-1250 * exit, 0);
  slamLine(ctx, CLOCK_LINES[0], 92, 1150, size, t, b(13));
  slamLine(ctx, CLOCK_LINES[1], 92, 1150 + size * 0.88, size, t, b(14), { color: COLOR.red, split: 4 });
  ctx.restore();
}
