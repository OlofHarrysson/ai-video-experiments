import { H, W } from '../config';
import { canvas, type Ctx } from '../util';
import { font } from './fonts';

/** Background top, background bottom, subject tint. */
const PALETTES: [string, string, string][] = [
  ['#2a1b52', '#7a36b3', '#c9a4ff'],
  ['#3d1a0f', '#d9642e', '#ffd0a8'],
];

const COUNTS = [['48.2K', '1,204'], ['312K', '9,870']];

/** Generic Reels, drawn once and scrolled past in the opening flick. */
export function makeFeedCards() {
  return PALETTES.map((palette, i) => {
    const card = canvas(W, H);
    drawCard(card.ctx, palette, COUNTS[i], i);
    return card.el;
  });
}

function roundRect(ctx: Ctx, x: number, y: number, w: number, h: number, r: number) {
  ctx.beginPath();
  ctx.roundRect(x, y, w, h, r);
}

function drawCard(ctx: Ctx, [top, bottom, tint]: [string, string, string], counts: string[], seed: number) {
  const bg = ctx.createLinearGradient(0, 0, 0, H);
  bg.addColorStop(0, top);
  bg.addColorStop(1, bottom);
  ctx.fillStyle = bg;
  ctx.fillRect(0, 0, W, H);

  const light = ctx.createRadialGradient(W * 0.5, H * 0.38, 40, W * 0.5, H * 0.42, 900);
  light.addColorStop(0, 'rgba(255,255,255,0.35)');
  light.addColorStop(1, 'rgba(255,255,255,0)');
  ctx.fillStyle = light;
  ctx.fillRect(0, 0, W, H);

  // someone talking to camera
  ctx.fillStyle = tint;
  ctx.globalAlpha = 0.55;
  ctx.beginPath();
  ctx.arc(W * 0.5 + (seed - 0.5) * 120, 760, 170, 0, Math.PI * 2);
  ctx.fill();
  ctx.beginPath();
  ctx.ellipse(W * 0.5 + (seed - 0.5) * 120, 1420, 420, 480, 0, Math.PI, 0);
  ctx.fill();
  ctx.fillRect(W * 0.5 + (seed - 0.5) * 120 - 420, 1420, 840, 600);
  ctx.globalAlpha = 1;

  // caption sticker
  ctx.fillStyle = '#ffffff';
  roundRect(ctx, 250, 1080, 580, 96, 18);
  ctx.fill();
  ctx.fillStyle = '#111';
  roundRect(ctx, 290, 1112, 500, 32, 10);
  ctx.fill();

  // action column
  ctx.strokeStyle = '#fff';
  ctx.fillStyle = '#fff';
  ctx.lineWidth = 7;
  ctx.lineJoin = 'round';
  const cx = 990;
  heart(ctx, cx, 1180);
  bubble(ctx, cx, 1340);
  plane(ctx, cx, 1500);
  for (let i = -1; i <= 1; i++) {
    ctx.beginPath();
    ctx.arc(cx + i * 20, 1640, 6, 0, Math.PI * 2);
    ctx.fill();
  }
  ctx.font = font.sans(28);
  ctx.textAlign = 'center';
  ctx.fillText(counts[0], cx, 1262);
  ctx.fillText(counts[1], cx, 1422);

  // creator row and caption
  ctx.textAlign = 'left';
  ctx.beginPath();
  ctx.arc(120, 1640, 40, 0, Math.PI * 2);
  ctx.fill();
  roundRect(ctx, 182, 1622, 200, 30, 12);
  ctx.fill();
  ctx.lineWidth = 4;
  roundRect(ctx, 402, 1614, 128, 48, 14);
  ctx.stroke();
  ctx.globalAlpha = 0.85;
  roundRect(ctx, 80, 1712, 620, 22, 10);
  ctx.fill();
  roundRect(ctx, 80, 1752, 440, 22, 10);
  ctx.fill();
  ctx.globalAlpha = 0.35;
  ctx.fillRect(0, 1884, W, 6);
  ctx.globalAlpha = 1;
  ctx.fillRect(0, 1884, W * (0.3 + seed * 0.2), 6);
}

function heart(ctx: Ctx, x: number, y: number) {
  ctx.beginPath();
  ctx.moveTo(x, y + 34);
  ctx.bezierCurveTo(x - 56, y - 6, x - 30, y - 44, x, y - 18);
  ctx.bezierCurveTo(x + 30, y - 44, x + 56, y - 6, x, y + 34);
  ctx.stroke();
}

function bubble(ctx: Ctx, x: number, y: number) {
  ctx.beginPath();
  ctx.arc(x, y, 34, 0.9, Math.PI * 2 + 0.5);
  ctx.lineTo(x + 36, y + 36);
  ctx.closePath();
  ctx.stroke();
}

function plane(ctx: Ctx, x: number, y: number) {
  ctx.beginPath();
  ctx.moveTo(x - 36, y - 26);
  ctx.lineTo(x + 38, y - 30);
  ctx.lineTo(x + 2, y + 36);
  ctx.lineTo(x - 6, y + 2);
  ctx.closePath();
  ctx.stroke();
}
