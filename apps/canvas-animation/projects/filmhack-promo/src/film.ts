import { BEAT, COLOR, DURATION, FPS, H, W, b } from './config';
import { drawCity } from './draw/city';
import { font } from './draw/fonts';
import { createFx, post, type PostState } from './draw/fx';
import { makeFeedCards } from './draw/feed';
import { fitSize } from './draw/text';
import type { AudioData, Env } from './env';
import { drawClockScene, CLOCK_LINES } from './scenes/clock';
import { drawCta, CTA_LINES } from './scenes/cta';
import { drawFacts } from './scenes/facts';
import { drawHook, HOOK_LINES } from './scenes/hook';
import { drawPipeline, MON, STAGES } from './scenes/pipeline';
import { drawPremiere } from './scenes/premiere';
import { drawSlateScene, SLATE_LINES } from './scenes/slate';
import { canvas, decay, hash, progress, type Ctx } from './util';

/** Accents shared by picture and sound: shake (px), RGB split (px), slice glitch (0–1), flash (0–1). */
interface Hit {
  beat: number;
  shake?: number;
  rgb?: number;
  slices?: number;
  flash?: number;
}

export const HITS: Hit[] = [
  { beat: 1, shake: 16, rgb: 22, slices: 0.8 },
  { beat: 2, shake: 14, rgb: 10 },
  { beat: 3, shake: 22, rgb: 14, flash: 0.12 },
  { beat: 8, shake: 28, rgb: 18, slices: 0.35, flash: 0.55 },
  { beat: 9, shake: 10, rgb: 8 },
  { beat: 12, shake: 8, rgb: 12, slices: 0.3, flash: 0.2 },
  { beat: 13, shake: 6, rgb: 6 },
  { beat: 14, shake: 6, rgb: 6 },
  { beat: 16, shake: 10, rgb: 10, slices: 0.25 },
  { beat: 20, shake: 10, rgb: 10, slices: 0.25 },
  { beat: 24, shake: 10, rgb: 10, slices: 0.25 },
  { beat: 28, shake: 10, rgb: 10, slices: 0.25 },
  { beat: 32, shake: 10, rgb: 10, slices: 0.25 },
  { beat: 36, shake: 20, rgb: 14, slices: 0.3, flash: 0.35 },
  { beat: 40, shake: 8, rgb: 6 },
  { beat: 44, shake: 30, rgb: 24, slices: 0.5, flash: 0.6 },
  { beat: 46, rgb: 5 },
  { beat: 48, rgb: 5 },
  { beat: 50, rgb: 5 },
  { beat: 52, shake: 6, rgb: 8 },
  { beat: 56, shake: 18, rgb: 12, flash: 0.25 },
  { beat: 56.5, shake: 10, rgb: 8 },
  { beat: 62, shake: 14, rgb: 10, flash: 0.18 },
];

export function prepare(audio: AudioData | null): Env {
  const measure = canvas(8, 8).ctx;
  const titles = [...STAGES.map((s) => s.title), 'SCREEN IT.'];
  const still = canvas(MON.w, MON.h);
  drawCity(still.ctx, 0, 0, MON.w, MON.h, { t: 0 });
  return {
    fx: createFx(),
    feed: makeFeedCards(),
    still: still.el,
    scratch: canvas(MON.w, MON.h),
    noise: new Map(),
    audio,
    layout: {
      hook: fitSize(measure, HOOK_LINES, font.display, 880, 380),
      slate: fitSize(measure, SLATE_LINES, font.display, 880, 215),
      clock: fitSize(measure, CLOCK_LINES, font.display, 880, 280),
      stage: fitSize(measure, titles, font.display, 880, 215),
      logo: fitSize(measure, ['AI FILMHACK'], font.display, 890, 320),
      cta: fitSize(measure, CTA_LINES, font.display, 880, 340),
    },
  };
}

function shakeAt(t: number) {
  let amount = 0;
  for (const hit of HITS) amount += (hit.shake ?? 0) * decay(t, b(hit.beat), 0.08);
  const f = Math.floor(t * FPS);
  return { x: amount * (hash(f * 2) * 2 - 1), y: amount * (hash(f * 2 + 1) * 2 - 1) };
}

function postAt(t: number): PostState {
  let rgb = 0;
  let slices = 0;
  let flash = 0;
  for (const hit of HITS) {
    const at = b(hit.beat);
    if (t < at) continue;
    rgb += (hit.rgb ?? 0) * decay(t, at, 0.07);
    if (t - at < 0.1) slices = Math.max(slices, hit.slices ?? 0);
    flash += (hit.flash ?? 0) * decay(t, at, 0.06);
  }
  // Glitch out of the last frames so the loop back into the feed feels deliberate.
  const out = progress(t, b(63.3), DURATION);
  return { rgb: rgb + 26 * out * out, slices: Math.max(slices, out), flash, seed: Math.floor(t * FPS) };
}

export function renderFrame(ctx: Ctx, t: number, env: Env) {
  const beat = t / BEAT;
  ctx.save();
  ctx.setTransform(1, 0, 0, 1, 0, 0);
  ctx.globalAlpha = 1;
  ctx.globalCompositeOperation = 'source-over';
  ctx.fillStyle = COLOR.ink;
  ctx.fillRect(0, 0, W, H);
  const shake = shakeAt(t);
  ctx.translate(shake.x, shake.y);

  if (beat < 8) drawHook(ctx, t, env);
  if (beat >= 5.5 && beat < 12) drawSlateScene(ctx, t, env);
  if (beat >= 12 && beat < 16) drawClockScene(ctx, t, env);
  if (beat >= 16 && beat < 36) drawPipeline(ctx, t, env);
  if (beat >= 36 && beat < 44) drawPremiere(ctx, t, env);
  if (beat >= 44 && beat < 56) drawFacts(ctx, t, env);
  if (beat >= 56) drawCta(ctx, t, env);

  ctx.restore();
  post(ctx, env.fx, postAt(t), Math.floor(t * FPS));
}
