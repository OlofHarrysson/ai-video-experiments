import { b } from '../config';
import { hash, hash2, rng, type Ctx } from '../util';

/** The film-within-the-film starts moving when the MOTION stage begins. */
export const filmTime = (t: number) => Math.max(0, t - b(24));

interface Window {
  x: number;
  y: number;
  w: number;
  h: number;
  warm: boolean;
  seed: number;
}

interface Building {
  x: number;
  w: number;
  h: number;
  windows: Window[];
  beacon: boolean;
}

/** Widths and x are fractions of the frame width; heights are fractions of its height. */
function skyline(seed: number, minW: number, maxW: number, minH: number, maxH: number, windowChance: number) {
  const random = rng(seed);
  const buildings: Building[] = [];
  for (let x = -0.2; x < 1.2; ) {
    const w = minW + random() * (maxW - minW);
    const h = minH + Math.pow(random(), 1.4) * (maxH - minH);
    const cols = Math.max(1, Math.floor(w / 0.011));
    const rows = Math.max(2, Math.floor(h / 0.028));
    const windows: Window[] = [];
    for (let c = 0; c < cols; c++) {
      for (let r = 0; r < rows; r++) {
        if (random() < windowChance) {
          windows.push({ x: (c + 0.28) / cols, y: (r + 0.3) / rows, w: 0.44 / cols, h: 0.36 / rows, warm: random() < 0.7, seed: Math.floor(random() * 1e6) });
        }
      }
    }
    buildings.push({ x, w, h, windows, beacon: random() < 0.22 });
    x += w + random() * 0.006;
  }
  return buildings;
}

const FAR = skyline(11, 0.026, 0.058, 0.1, 0.33, 0.17);
const NEAR = skyline(29, 0.06, 0.12, 0.06, 0.17, 0.08);
const STARS = Array.from({ length: 80 }, (_, i) => ({ x: hash(i * 3 + 1) * 1.2 - 0.1, y: hash(i * 3 + 2) * 0.55, s: 0.6 + hash(i * 3 + 3) * 1.4 }));
const RAIN = Array.from({ length: 260 }, (_, i) => ({ x: hash(i + 500) * 1.3 - 0.05, y: hash(i + 900), len: 0.035 + hash(i + 1300) * 0.05, speed: 1.25 + hash(i + 1700) * 0.7 }));
const CLOUDS = [
  { x: 0.55, y: 0.29, s: 1.0, speed: 0.012 },
  { x: 0.9, y: 0.42, s: 0.75, speed: 0.009 },
  { x: 0.2, y: 0.16, s: 1.2, speed: 0.006 },
];
/** [dx, dy, rx, ry] as fractions of width/height. */
const CLOUD_BLOBS = [
  [0, 0, 0.1, 0.034],
  [0.07, -0.02, 0.07, 0.04],
  [-0.08, 0.008, 0.07, 0.03],
  [0.14, 0.01, 0.05, 0.022],
  [-0.15, 0.014, 0.05, 0.018],
];

export interface CityView {
  t: number;
  zoom?: number;
  /** Camera centre as fractions of the frame. */
  cx?: number;
  cy?: number;
  /** Dolly amount; shifts layers by depth. */
  parallax?: number;
  rain?: number;
}

/** The short film the pipeline builds: a filmmaker on a Berlin rooftop under a red moon. */
export function drawCity(ctx: Ctx, x: number, y: number, w: number, h: number, view: CityView) {
  const { t } = view;
  const par = view.parallax ?? 0;
  const U = (u: number) => u * w;
  const V = (v: number) => v * h;
  const shift = (depth: number) => -par * depth * 0.035;

  ctx.save();
  ctx.beginPath();
  ctx.rect(x, y, w, h);
  ctx.clip();
  ctx.translate(x + w / 2, y + h / 2);
  const zoom = view.zoom ?? 1;
  ctx.scale(zoom, zoom);
  ctx.translate(-(view.cx ?? 0.5) * w, -(view.cy ?? 0.5) * h);

  const sky = ctx.createLinearGradient(0, 0, 0, h);
  sky.addColorStop(0, '#05050b');
  sky.addColorStop(0.5, '#0f0611');
  sky.addColorStop(0.78, '#2c0712');
  sky.addColorStop(1, '#3d0a16');
  ctx.fillStyle = sky;
  ctx.fillRect(-w * 0.2, -h * 0.2, w * 1.4, h * 1.4);

  for (const s of STARS) {
    const twinkle = 0.5 + 0.5 * Math.sin(t * 2.2 + s.x * 47);
    ctx.fillStyle = `rgba(255,255,255,${0.2 + 0.45 * twinkle})`;
    ctx.fillRect(U(s.x + shift(0.05)), V(s.y), s.s, s.s);
  }

  moon(ctx, U(0.7 + shift(0.1)), V(0.34), V(0.17));

  for (const c of CLOUDS) {
    const cx = U((((c.x + t * c.speed + 0.2) % 1.4) - 0.2) + shift(0.15));
    ctx.fillStyle = 'rgba(8,5,12,0.9)';
    for (const [dx, dy, rx, ry] of CLOUD_BLOBS) {
      ctx.beginPath();
      ctx.ellipse(cx + U(dx * c.s), V(c.y + dy * c.s), U(rx * c.s), V(ry * c.s), 0, 0, Math.PI * 2);
      ctx.fill();
    }
  }

  const haze = ctx.createLinearGradient(0, V(0.62), 0, V(0.86));
  haze.addColorStop(0, 'rgba(200,5,40,0)');
  haze.addColorStop(1, 'rgba(200,5,40,0.16)');
  ctx.fillStyle = haze;
  ctx.fillRect(-w * 0.2, V(0.62), w * 1.4, V(0.3));

  tower(ctx, U(0.16 + shift(0.35)), V, U, t);
  drawSkyline(ctx, FAR, U, V, 0.8, shift(0.35), '#0c0b13', t, 0.6);
  drawSkyline(ctx, NEAR, U, V, 0.9, shift(0.7), '#060509', t, 0.75);
  rooftop(ctx, U, V, shift(1));
  filmmaker(ctx, U(0.27 + shift(1)), V(0.875), V(0.34));

  const rain = view.rain ?? 0;
  if (rain > 0) {
    ctx.strokeStyle = `rgba(210,225,255,${0.24 * rain})`;
    ctx.lineWidth = 1.3;
    ctx.beginPath();
    for (const d of RAIN) {
      const yy = ((d.y + t * d.speed) % 1.2) - 0.1;
      const xx = d.x - yy * 0.12;
      ctx.moveTo(U(xx), V(yy));
      ctx.lineTo(U(xx - d.len * 0.2), V(yy + d.len));
    }
    ctx.stroke();
  }
  ctx.restore();
}

function moon(ctx: Ctx, mx: number, my: number, r: number) {
  const glow = ctx.createRadialGradient(mx, my, r * 0.8, mx, my, r * 3.4);
  glow.addColorStop(0, 'rgba(210,10,45,0.42)');
  glow.addColorStop(1, 'rgba(210,10,45,0)');
  ctx.fillStyle = glow;
  ctx.fillRect(mx - r * 3.5, my - r * 3.5, r * 7, r * 7);
  const disc = ctx.createRadialGradient(mx - r * 0.35, my - r * 0.35, r * 0.1, mx, my, r);
  disc.addColorStop(0, '#ff5a74');
  disc.addColorStop(0.5, '#d3102f');
  disc.addColorStop(1, '#78031a');
  ctx.fillStyle = disc;
  ctx.beginPath();
  ctx.arc(mx, my, r, 0, Math.PI * 2);
  ctx.fill();
  ctx.fillStyle = 'rgba(70,0,12,0.28)';
  for (const [dx, dy, cr] of [[-0.3, 0.2, 0.18], [0.25, -0.25, 0.12], [0.35, 0.3, 0.09], [-0.05, -0.45, 0.08], [0.05, 0.05, 0.07]]) {
    ctx.beginPath();
    ctx.arc(mx + dx * r, my + dy * r, cr * r, 0, Math.PI * 2);
    ctx.fill();
  }
}

/** Berlin's TV tower, a nod to the location next door. */
function tower(ctx: Ctx, x: number, V: (v: number) => number, U: (u: number) => number, t: number) {
  ctx.fillStyle = '#0d0c15';
  ctx.beginPath();
  ctx.moveTo(x - U(0.011), V(0.81));
  ctx.lineTo(x + U(0.011), V(0.81));
  ctx.lineTo(x + U(0.0055), V(0.4));
  ctx.lineTo(x - U(0.0055), V(0.4));
  ctx.fill();
  const r = V(0.05);
  ctx.beginPath();
  ctx.arc(x, V(0.37), r, 0, Math.PI * 2);
  ctx.fill();
  ctx.fillRect(x - U(0.0042), V(0.25), U(0.0084), V(0.09));
  ctx.fillRect(x - U(0.0016), V(0.12), U(0.0032), V(0.14));
  ctx.strokeStyle = 'rgba(255,60,90,0.5)';
  ctx.lineWidth = 1.6;
  ctx.beginPath();
  ctx.arc(x, V(0.37), r, -1.0, 0.9);
  ctx.stroke();
  if (t % 1.2 < 0.4) beacon(ctx, x, V(0.12), 7);
}

function beacon(ctx: Ctx, x: number, y: number, r: number) {
  const g = ctx.createRadialGradient(x, y, 0, x, y, r);
  g.addColorStop(0, 'rgba(255,60,80,1)');
  g.addColorStop(1, 'rgba(255,60,80,0)');
  ctx.fillStyle = g;
  ctx.fillRect(x - r, y - r, r * 2, r * 2);
}

function drawSkyline(ctx: Ctx, list: Building[], U: (u: number) => number, V: (v: number) => number, base: number, shift: number, fill: string, t: number, windowAlpha: number) {
  for (const bld of list) {
    const bx = U(bld.x + shift);
    const bw = U(bld.w);
    const bh = V(bld.h);
    const by = V(base) - bh;
    ctx.fillStyle = fill;
    ctx.fillRect(bx, by, bw + 1, bh + V(1.2 - base));
    for (const win of bld.windows) {
      if (hash2(win.seed, Math.floor(t * 1.3)) > 0.93) continue;
      ctx.fillStyle = win.warm ? `rgba(255,196,120,${windowAlpha})` : `rgba(120,228,255,${windowAlpha * 0.8})`;
      ctx.fillRect(bx + win.x * bw, by + win.y * bh, Math.max(1.2, win.w * bw), Math.max(1.2, win.h * bh));
    }
    if (bld.beacon && (t + bld.x * 3) % 1.6 < 0.5) beacon(ctx, bx + bw / 2, by - 2, 5);
  }
}

function rooftop(ctx: Ctx, U: (u: number) => number, V: (v: number) => number, shift: number) {
  ctx.fillStyle = '#000';
  ctx.beginPath();
  ctx.moveTo(U(-0.3), V(0.875));
  ctx.lineTo(U(0.63 + shift), V(0.875));
  ctx.lineTo(U(0.66 + shift), V(0.905));
  ctx.lineTo(U(1.3), V(0.905));
  ctx.lineTo(U(1.3), V(1.3));
  ctx.lineTo(U(-0.3), V(1.3));
  ctx.fill();
  // water tank and mast on the far roof
  const tx = U(0.84 + shift);
  ctx.fillRect(tx - U(0.03), V(0.73), U(0.06), V(0.1));
  ctx.beginPath();
  ctx.ellipse(tx, V(0.73), U(0.03), V(0.02), 0, Math.PI, 0);
  ctx.fill();
  ctx.fillRect(tx - U(0.026), V(0.83), U(0.004), V(0.08));
  ctx.fillRect(tx + U(0.022), V(0.83), U(0.004), V(0.08));
  ctx.fillRect(U(0.95 + shift), V(0.6), U(0.003), V(0.3));
  // railing
  for (let i = 0; i < 9; i++) ctx.fillRect(U(-0.02 + i * 0.075 + shift), V(0.845), U(0.003), V(0.03));
  ctx.fillRect(U(-0.3), V(0.845), U(0.93 + shift + 0.3), V(0.004));
}

/** Silhouette of a filmmaker at a tripod camera, rim-lit by the moon. */
function filmmaker(ctx: Ctx, fx: number, fy: number, fh: number) {
  const p = (dx: number, dy: number): [number, number] => [fx + dx * fh, fy + dy * fh];
  const path = new Path2D();
  const poly = (points: [number, number][]) => {
    path.moveTo(...points[0]);
    for (const pt of points.slice(1)) path.lineTo(...pt);
    path.closePath();
  };
  path.moveTo(fx + 0.07 * fh, fy - 0.9 * fh);
  path.arc(fx, fy - 0.9 * fh, 0.07 * fh, 0, Math.PI * 2);
  poly([p(-0.035, -0.84), p(0.035, -0.84), p(0.04, -0.78), p(-0.04, -0.78)]);
  poly([p(-0.13, -0.79), p(0.12, -0.79), p(0.17, -0.33), p(-0.15, -0.33)]);
  poly([p(-0.1, -0.35), p(-0.02, -0.35), p(-0.035, 0), p(-0.11, 0)]);
  poly([p(0.02, -0.35), p(0.1, -0.35), p(0.13, 0), p(0.055, 0)]);
  poly([p(0.07, -0.77), p(0.13, -0.73), p(0.34, -0.635), p(0.33, -0.585)]);
  poly([p(0.31, -0.7), p(0.49, -0.7), p(0.49, -0.575), p(0.31, -0.575)]);
  poly([p(0.49, -0.672), p(0.58, -0.69), p(0.58, -0.6), p(0.49, -0.61)]);
  poly([p(0.39, -0.58), p(0.41, -0.58), p(0.29, 0), p(0.27, 0)]);
  poly([p(0.39, -0.58), p(0.41, -0.58), p(0.415, 0), p(0.395, 0)]);
  poly([p(0.39, -0.58), p(0.41, -0.58), p(0.55, 0), p(0.53, 0)]);
  ctx.save();
  ctx.translate(2.4, -1.4);
  ctx.fillStyle = 'rgba(255,45,85,0.95)';
  ctx.fill(path);
  ctx.restore();
  ctx.fillStyle = '#000';
  ctx.fill(path);
}
