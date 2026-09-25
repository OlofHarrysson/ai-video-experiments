import { BEAT, COLOR, H, W, b, white } from '../config';
import { drawCity, filmTime } from '../draw/city';
import { label, slamLine } from '../draw/text';
import type { Env } from '../env';
import { decay, easeOutBack, hash, lerp, progress, rng, type Ctx } from '../util';

const SCREEN = { x: 90, y: 300, w: 900, h: 506 };
const START = b(36);
const CHEER = b(40);
export const PREMIERE_LINE = 'SUNDAY · REAL CINEMA · FULL HOUSE';

interface Person {
  x: number;
  y: number;
  r: number;
  phase: number;
  cheer: boolean;
  phone: boolean;
}

const PEOPLE: Person[] = (() => {
  const random = rng(4242);
  const rows = [
    { y: 1335, r: 34, n: 12 },
    { y: 1485, r: 47, n: 9 },
    { y: 1675, r: 66, n: 7 },
  ];
  const people: Person[] = [];
  for (const row of rows) {
    for (let i = 0; i < row.n; i++) {
      people.push({
        x: (i + 0.5 + (random() - 0.5) * 0.5) * (W / row.n),
        y: row.y + (random() - 0.5) * 18,
        r: row.r * (0.9 + random() * 0.2),
        phase: random() * Math.PI * 2,
        cheer: random() < 0.55,
        phone: random() < 0.3,
      });
    }
  }
  return people;
})();

const DUST = Array.from({ length: 120 }, (_, i) => ({
  u: hash(i * 5 + 1),
  v: hash(i * 5 + 2),
  size: 1.2 + hash(i * 5 + 3) * 2.4,
  speed: 0.012 + hash(i * 5 + 4) * 0.03,
  twinkle: hash(i * 5 + 5) * 6,
}));

const FLICKER = [0, 1, 0.12, 0.9, 0.35, 1];

/** Beats 36–44: the film we just watched being made plays to a full cinema. */
export function drawPremiere(ctx: Ctx, t: number, env: Env) {
  const lt = t - START;
  const on = lt < FLICKER.length * 0.04 ? FLICKER[Math.floor(Math.max(0, lt) / 0.04)] : 1;

  ctx.fillStyle = '#030303';
  ctx.fillRect(-60, -60, W + 120, H + 120);
  const cx = SCREEN.x + SCREEN.w / 2;
  const cy = SCREEN.y + SCREEN.h / 2;
  const spill = ctx.createRadialGradient(cx, cy, 200, cx, cy, 1150);
  spill.addColorStop(0, `rgba(190,20,50,${0.34 * on})`);
  spill.addColorStop(1, 'rgba(0,0,0,0)');
  ctx.fillStyle = spill;
  ctx.fillRect(-60, -60, W + 120, H + 120);
  curtains(ctx, on);

  drawCity(ctx, SCREEN.x, SCREEN.y, SCREEN.w, SCREEN.h, { t: filmTime(t), zoom: 1.04, parallax: 1.6, rain: 1 });
  if (on < 1) {
    ctx.fillStyle = `rgba(0,0,0,${1 - on})`;
    ctx.fillRect(SCREEN.x, SCREEN.y, SCREEN.w, SCREEN.h);
  }
  beam(ctx, lt, on);
  audience(ctx, t, on);
  flashes(ctx, t);

  label(ctx, '06 / PREMIERE', 92, 950, { size: 30, color: COLOR.cyan, spacing: 4 });
  slamLine(ctx, 'SCREEN IT.', 92, 1122, env.layout.stage, t, START, { color: COLOR.red, split: 4 });
  const typed = Math.ceil(PREMIERE_LINE.length * progress(t, b(38), b(38) + 0.4));
  label(ctx, PREMIERE_LINE.slice(0, typed), 92, 1196, { size: 36, color: white(0.92), spacing: 3 });
}

function curtains(ctx: Ctx, on: number) {
  for (const side of [0, 1]) {
    for (let i = 0; i < 7; i++) {
      const x = side === 0 ? i * 11 : W - 77 + i * 11;
      ctx.fillStyle = i % 2 === 0 ? `rgba(95,4,20,${0.85 * on})` : `rgba(38,1,8,${0.9 * on})`;
      ctx.fillRect(x, 230, 11, 700);
    }
  }
  const fade = ctx.createLinearGradient(0, 700, 0, 940);
  fade.addColorStop(0, 'rgba(3,3,3,0)');
  fade.addColorStop(1, 'rgba(3,3,3,1)');
  ctx.fillStyle = fade;
  ctx.fillRect(0, 700, 80, 240);
  ctx.fillRect(W - 80, 700, 80, 240);
}

/** Projector light arriving from behind the audience, with drifting dust. */
function beam(ctx: Ctx, lt: number, on: number) {
  if (on <= 0) return;
  const bottom = SCREEN.y + SCREEN.h;
  const top = -140;
  const edge = (y: number) => {
    const k = (y - top) / (bottom - top);
    return [lerp(-420, SCREEN.x, k), lerp(W + 420, SCREEN.x + SCREEN.w, k)];
  };
  ctx.save();
  ctx.globalCompositeOperation = 'lighter';
  const g = ctx.createLinearGradient(0, top, 0, bottom);
  g.addColorStop(0, `rgba(255,236,220,${0.11 * on})`);
  g.addColorStop(1, `rgba(255,236,220,${0.02 * on})`);
  ctx.fillStyle = g;
  ctx.beginPath();
  ctx.moveTo(-420, top);
  ctx.lineTo(W + 420, top);
  ctx.lineTo(SCREEN.x + SCREEN.w, bottom);
  ctx.lineTo(SCREEN.x, bottom);
  ctx.closePath();
  ctx.fill();
  for (let i = 0; i < 9; i++) {
    const u = hash(i + 50);
    const tx = SCREEN.x + SCREEN.w * u;
    const ty = SCREEN.y + SCREEN.h * hash(i + 80);
    const sx = -300 + (W + 600) * u;
    const wobble = 0.6 + 0.4 * Math.sin(lt * 1.3 + i);
    ctx.fillStyle = `rgba(255,240,225,${0.04 * wobble * on})`;
    ctx.beginPath();
    ctx.moveTo(sx - 70, top);
    ctx.lineTo(sx + 70, top);
    ctx.lineTo(tx + 6, ty);
    ctx.lineTo(tx - 6, ty);
    ctx.closePath();
    ctx.fill();
  }
  for (const d of DUST) {
    const y = lerp(top, bottom, (d.v + lt * d.speed) % 1);
    const [l, r] = edge(y);
    const x = lerp(l, r, d.u) + Math.sin(lt * 0.8 + d.twinkle) * 12;
    const a = (0.2 + 0.5 * (0.5 + 0.5 * Math.sin(lt * 3 + d.twinkle))) * on;
    ctx.fillStyle = `rgba(255,245,235,${a})`;
    ctx.fillRect(x, y, d.size, d.size);
  }
  ctx.restore();
}

function audience(ctx: Ctx, t: number, on: number) {
  const cheer = easeOutBack(progress(t, CHEER, CHEER + 0.35), 1.4);
  const rim = `rgba(255,70,105,${0.45 * on})`;
  for (const p of PEOPLE) {
    const lift = p.cheer || p.phone ? cheer : 0;
    const bounce = lift > 0 ? Math.sin(((t - CHEER) / BEAT) * Math.PI * 2 + p.phase) : 0;
    for (const [dy, color] of [[-3, rim], [0, '#000']] as const) {
      ctx.fillStyle = color;
      ctx.strokeStyle = color;
      ctx.beginPath();
      ctx.ellipse(p.x, p.y + 1.9 * p.r + dy, 1.85 * p.r, 1.2 * p.r, 0, Math.PI, 0);
      ctx.fill();
      ctx.fillRect(p.x - 1.85 * p.r, p.y + 1.9 * p.r + dy - 1, 3.7 * p.r, 500);
      ctx.beginPath();
      ctx.arc(p.x, p.y + dy, p.r, 0, Math.PI * 2);
      ctx.fill();
      if (lift <= 0) continue;
      ctx.lineWidth = 0.5 * p.r;
      ctx.lineCap = 'round';
      for (const side of p.phone ? [1] : [-1, 1]) {
        const sx = p.x + side * 1.25 * p.r;
        const sy = p.y + 1.35 * p.r + dy;
        const hx = p.x + side * (1.3 + 0.45 * lift) * p.r;
        const hy = p.y + dy - lift * 2.1 * p.r + bounce * 0.22 * p.r;
        ctx.beginPath();
        ctx.moveTo(sx, sy);
        ctx.quadraticCurveTo(sx + side * 0.5 * p.r, (sy + hy) / 2, hx, hy);
        ctx.stroke();
        if (p.phone) {
          ctx.fillRect(hx - 0.34 * p.r, hy - 1.05 * p.r, 0.68 * p.r, 1.15 * p.r);
          if (color === '#000') {
            ctx.fillStyle = `rgba(215,232,255,${0.92 * on})`;
            ctx.fillRect(hx - 0.26 * p.r, hy - 0.97 * p.r, 0.52 * p.r, 0.95 * p.r);
            ctx.fillStyle = color;
          }
        } else {
          ctx.beginPath();
          ctx.arc(hx, hy, 0.3 * p.r, 0, Math.PI * 2);
          ctx.fill();
        }
      }
    }
  }
}

/** Phone-camera flashes popping across the crowd once it starts cheering. */
function flashes(ctx: Ctx, t: number) {
  if (t < CHEER) return;
  ctx.save();
  ctx.globalCompositeOperation = 'lighter';
  for (let i = 0; i < 9; i++) {
    const at = CHEER + hash(i + 300) * b(3.6);
    const k = decay(t, at, 0.09);
    if (k < 0.02) continue;
    const x = 80 + hash(i + 400) * (W - 160);
    const y = 1230 + hash(i + 500) * 420;
    const r = 60 * k;
    const g = ctx.createRadialGradient(x, y, 0, x, y, r);
    g.addColorStop(0, `rgba(255,255,255,${0.95 * k})`);
    g.addColorStop(1, 'rgba(255,255,255,0)');
    ctx.fillStyle = g;
    ctx.fillRect(x - r, y - r, r * 2, r * 2);
    ctx.fillStyle = `rgba(255,255,255,${0.8 * k})`;
    ctx.fillRect(x - r * 1.6, y - 1.5, r * 3.2, 3);
    ctx.fillRect(x - 1.5, y - r * 1.6, 3, r * 3.2);
  }
  ctx.restore();
}
