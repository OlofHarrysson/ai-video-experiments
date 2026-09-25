import { COLOR, white } from '../config';
import type { Ctx } from '../util';
import { font } from './fonts';
import { glitchText, label } from './text';

export const slateHeight = (w: number) => w * 0.58;
export const stickHeight = (w: number) => w * 0.075;

/** Black-and-white clapper stripes; `dir` flips the slant so arm and stick form chevrons when shut. */
function stripes(ctx: Ctx, x: number, y: number, w: number, h: number, dir: 1 | -1) {
  ctx.save();
  ctx.beginPath();
  ctx.rect(x, y, w, h);
  ctx.clip();
  ctx.fillStyle = '#f1f1f1';
  ctx.fillRect(x, y, w, h);
  ctx.fillStyle = '#0b0b0b';
  const step = w / 6;
  const slant = h * 1.1 * dir;
  for (let i = -2; i < 9; i++) {
    const sx = x + i * step;
    ctx.beginPath();
    ctx.moveTo(sx, y + h);
    ctx.lineTo(sx + step * 0.5, y + h);
    ctx.lineTo(sx + step * 0.5 + slant, y);
    ctx.lineTo(sx + slant, y);
    ctx.closePath();
    ctx.fill();
  }
  ctx.restore();
  ctx.strokeStyle = '#0b0b0b';
  ctx.lineWidth = 2;
  ctx.strokeRect(x, y, w, h);
}

export interface SlateState {
  /** Arm rotation in radians; negative opens it. */
  arm: number;
  /** 0–1 emphasis on the DIRECTOR field. */
  you: number;
  /** Cursor blink phase. */
  blink: boolean;
  split: number;
}

/** The site's slate panel as a physical clapperboard. (x, y) is the board's top-left corner. */
export function drawSlate(ctx: Ctx, x: number, y: number, w: number, s: SlateState) {
  const h = slateHeight(w);
  const stick = stickHeight(w);
  const k = w / 900;

  stripes(ctx, x, y - stick, w, stick, -1);
  ctx.save();
  ctx.translate(x, y - stick);
  ctx.rotate(s.arm);
  stripes(ctx, 0, -stick, w, stick, 1);
  ctx.restore();
  // hinge
  ctx.fillStyle = '#9a9a9a';
  ctx.beginPath();
  ctx.arc(x + 14 * k, y - stick, 9 * k, 0, Math.PI * 2);
  ctx.fill();

  ctx.fillStyle = '#0b0b0b';
  ctx.fillRect(x, y, w, h);
  ctx.strokeStyle = '#2c2c2c';
  ctx.lineWidth = 3 * k;
  ctx.strokeRect(x, y, w, h);

  const rows = [0.3, 0.22, 0.26, 0.22].map((f) => f * h);
  const rowY = rows.reduce<number[]>((acc, r, i) => [...acc, acc[i] + r], [y]);
  ctx.strokeStyle = '#262626';
  ctx.lineWidth = 2 * k;
  const line = (x0: number, y0: number, x1: number, y1: number) => {
    ctx.beginPath();
    ctx.moveTo(x0, y0);
    ctx.lineTo(x1, y1);
    ctx.stroke();
  };
  for (let i = 1; i < rows.length; i++) line(x, rowY[i], x + w, rowY[i]);
  line(x + w * 0.5, rowY[1], x + w * 0.5, rowY[2]);
  line(x + w * 0.4, rowY[2], x + w * 0.4, rowY[3]);
  line(x + w * 0.7, rowY[2], x + w * 0.7, rowY[3]);

  const pad = 26 * k;
  const cap = (text: string, cx: number, cy: number) => label(ctx, text, cx + pad, cy + 38 * k, { size: 20 * k, color: white(0.42) });
  const value = (text: string, cx: number, rowBottom: number, color: string = white(0.92)) =>
    label(ctx, text, cx + pad, rowBottom - 24 * k, { size: 40 * k, color, spacing: 2 * k });

  cap('PROD.', x, rowY[0]);
  ctx.save();
  ctx.font = font.display(Math.round(104 * k));
  glitchText(ctx, 'AI FILMHACK', x + pad, rowY[1] - 24 * k, s.split);
  ctx.restore();

  cap('SCENE', x, rowY[1]);
  value('01', x, rowY[2]);
  cap('TAKE', x + w * 0.5, rowY[1]);
  value('01', x + w * 0.5, rowY[2]);

  cap('DIRECTOR', x, rowY[2]);
  ctx.save();
  if (s.you > 0) {
    ctx.shadowColor = COLOR.cyan;
    ctx.shadowBlur = 26 * k * s.you;
  }
  value('YOU', x, rowY[3], COLOR.cyan);
  ctx.restore();
  if (s.you > 0 && s.blink) {
    ctx.fillStyle = COLOR.cyan;
    ctx.fillRect(x + pad + 84 * k, rowY[3] - 58 * k, 22 * k, 38 * k);
  }
  cap('DATE', x + w * 0.4, rowY[2]);
  value('13.11.26', x + w * 0.4, rowY[3]);
  cap('TIME', x + w * 0.7, rowY[2]);
  value('15:00', x + w * 0.7, rowY[3]);

  cap('LOC.', x, rowY[3]);
  value('FILMUNI BABELSBERG', x, rowY[4]);
}
