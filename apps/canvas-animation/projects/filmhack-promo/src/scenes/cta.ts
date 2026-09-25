import { BEAT, COLOR, b, white } from '../config';
import { font } from '../draw/fonts';
import { backdrop } from '../draw/fx';
import { label, slamLine } from '../draw/text';
import type { Env } from '../env';
import { decay, easeOutBack, progress, type Ctx } from '../util';

export const CTA_LINES = ['GET ON', 'THE LIST.'];
const BUTTON = { x: 90, y: 1000, w: 900, h: 150 };

function typedLabel(ctx: Ctx, text: string, y: number, t: number, t0: number, size: number, color: string) {
  const n = Math.ceil(text.length * progress(t, t0, t0 + 0.3));
  if (n > 0) label(ctx, text.slice(0, n), 540, y, { size, color, align: 'center', spacing: 4 });
}

/** Beats 56–64: the call to action, held long enough to read and screenshot. */
export function drawCta(ctx: Ctx, t: number, env: Env) {
  backdrop(ctx, env.fx, { glow: 0.32, glowY: 1040 });
  const size = env.layout.cta;
  slamLine(ctx, CTA_LINES[0], 92, 640, size, t, b(56));
  slamLine(ctx, CTA_LINES[1], 92, 640 + size * 0.88, size, t, b(56.5));

  if (t >= b(57)) {
    const pop = easeOutBack(progress(t, b(57), b(57) + 0.28), 2);
    const pulse = t < b(62) ? decay(t, b(Math.floor(t / BEAT)), 0.12) : 0;
    const final = decay(t, b(62), 0.3);
    const { x, y, w, h } = BUTTON;
    const scale = 0.8 + 0.2 * pop + 0.02 * pulse;
    ctx.save();
    ctx.translate(x + w / 2, y + h / 2);
    ctx.scale(scale, scale);
    ctx.translate(-(x + w / 2), -(y + h / 2));
    ctx.shadowColor = 'rgba(255,30,80,0.85)';
    ctx.shadowBlur = 50 + 40 * pulse + 70 * final;
    ctx.fillStyle = COLOR.red;
    ctx.fillRect(x, y, w, h);
    ctx.shadowBlur = 0;
    ctx.font = font.mono(62, 700);
    ctx.letterSpacing = '8px';
    ctx.textAlign = 'center';
    ctx.fillStyle = COLOR.white;
    ctx.fillText('FILMHACK.AI  →', x + w / 2 + 4, y + h / 2 + 22);
    ctx.restore();
  }

  typedLabel(ctx, 'LINK IN BIO', 1242, t, b(58), 42, white(0.95));
  typedLabel(ctx, 'NOTIFY ME WHEN APPLICATIONS OPEN', 1296, t, b(58.5), 28, white(0.6));
  typedLabel(ctx, 'FILMAKERS.AI × CHAPTER41', 1374, t, b(59), 24, white(0.45));
  typedLabel(ctx, 'FILMUNIVERSITÄT BABELSBERG · POTSDAM', 1410, t, b(59.5), 24, white(0.45));
}
