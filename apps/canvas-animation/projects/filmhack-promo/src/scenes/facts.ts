import { BEAT, COLOR, b, white } from '../config';
import { font } from '../draw/fonts';
import { backdrop } from '../draw/fx';
import { label, measureLabel, slamLine } from '../draw/text';
import type { Env } from '../env';
import { decay, easeOutExpo, progress, rng, type Ctx } from '../util';

export const CHIPS = [
  { text: 'NOV 12–15, 2026 · POTSDAM', hot: false },
  { text: 'FILMUNIVERSITÄT BABELSBERG', hot: false },
  { text: 'FREE · APPLICATION-BASED', hot: false },
  { text: 'LIMITED TO 100 SPOTS', hot: true },
];
export const AUDIENCE_LINE = 'FOR FILMMAKERS & AI CREATORS';

/** Beats 44–56: logo slam, then the event facts as the site's info chips. */
export function drawFacts(ctx: Ctx, t: number, env: Env) {
  backdrop(ctx, env.fx, { glow: 0.3, glowY: 700 });
  graffiti(ctx);

  slamLine(ctx, 'AI FILMHACK', 92, 610, env.layout.logo, t, b(44), { split: 5, from: 1.4 });

  const wipe = easeOutExpo(progress(t, b(45), b(45) + 0.3));
  if (wipe > 0) {
    ctx.save();
    ctx.beginPath();
    ctx.rect(80, 640, 920 * wipe, 170);
    ctx.clip();
    ctx.font = font.displaySm(54);
    ctx.fillStyle = white(0.94);
    ctx.fillText("EUROPE'S FIRST HYBRID", 92, 706);
    ctx.fillText('AI × FILM CHALLENGE.', 92, 770);
    ctx.restore();
  }

  CHIPS.forEach((chip, i) => drawChip(ctx, chip.text, 90, 840 + i * 120, t, b(46 + i * 2), chip.hot));

  const typed = Math.ceil(AUDIENCE_LINE.length * progress(t, b(54), b(54) + 0.35));
  label(ctx, AUDIENCE_LINE.slice(0, typed), 92, 1384, { size: 34, color: white(0.8), spacing: 4 });
}

function drawChip(ctx: Ctx, text: string, x: number, y: number, t: number, t0: number, hot: boolean) {
  if (t < t0) return;
  const size = 38;
  const padX = 30;
  const h = 100;
  const bullet = 14;
  const gap = 20;
  const w = padX * 2 + bullet + gap + measureLabel(ctx, text, size, 3);
  const open = easeOutExpo(progress(t, t0, t0 + 0.22));
  ctx.save();
  if (hot) {
    ctx.shadowColor = 'rgba(255,30,80,0.9)';
    ctx.shadowBlur = 24 + 30 * decay(t, b(Math.floor(t / BEAT)), 0.14);
  }
  ctx.beginPath();
  ctx.rect(x - 40, y - 40, (w + 80) * open, h + 80);
  ctx.clip();
  ctx.fillStyle = hot ? COLOR.red : '#0b0b0b';
  ctx.fillRect(x, y, w, h);
  ctx.shadowBlur = 0;
  ctx.strokeStyle = hot ? COLOR.redHot : '#2a2a2a';
  ctx.lineWidth = 2;
  ctx.strokeRect(x, y, w, h);
  ctx.fillStyle = hot ? COLOR.white : COLOR.cyan;
  ctx.fillRect(x + padX, y + h / 2 - bullet / 2, bullet, bullet);
  const typed = Math.ceil(text.length * progress(t, t0 + 0.03, t0 + 0.3));
  label(ctx, text.slice(0, typed), x + padX + bullet + gap, y + h / 2 + size * 0.36, { size, color: COLOR.white, spacing: 3 });
  ctx.restore();
}

/** Faint spray-paint echo of the site's "THE FUTURE IS HYBRID" wall. */
function graffiti(ctx: Ctx) {
  ctx.save();
  ctx.translate(540, 1110);
  ctx.rotate(-0.08);
  ctx.font = font.display(250);
  ctx.textAlign = 'center';
  ctx.fillStyle = 'rgba(255,255,255,0.03)';
  ['THE FUTURE', 'IS HYBRID'].forEach((line, i) => {
    for (const [dx, dy] of [[0, 0], [3, -2], [-2, 3]]) ctx.fillText(line, dx, i * 220 + dy);
  });
  const random = rng(505);
  for (let i = 0; i < 16; i++) {
    const x = (random() - 0.5) * 900;
    const y = random() < 0.5 ? 6 : 226;
    const len = 40 + random() * 170;
    const w = 5 + random() * 5;
    ctx.fillRect(x, y, w, len);
    ctx.beginPath();
    ctx.arc(x + w / 2, y + len, w * 0.75, 0, Math.PI * 2);
    ctx.fill();
  }
  ctx.restore();
}
