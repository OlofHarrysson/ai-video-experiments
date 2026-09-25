import { BEAT, COLOR, b, white } from '../config';
import { drawCity, filmTime } from '../draw/city';
import { drawClockPanel, remaining, wallClock } from '../draw/clock';
import { font } from '../draw/fonts';
import { backdrop } from '../draw/fx';
import { label, scramble, slamLine } from '../draw/text';
import type { Env } from '../env';
import { canvas, clamp, easeInOutCubic, easeOutExpo, lerp, progress, rng, type Ctx } from '../util';
import { CLOCK_HUD } from './clock';

export const MON = { x: 90, y: 530, w: 900, h: 506 };
const START = 16;

export const STAGES = [
  { key: 'CONCEPT', title: 'WRITE IT.', tag: 'SCRIPT · DRAFT 1' },
  { key: 'IMAGE', title: 'SEE IT.', tag: '' },
  { key: 'MOTION', title: 'MOVE IT.', tag: 'CAM · PUSH-IN · 24 FPS' },
  { key: 'VOICE & SOUND', title: 'HEAR IT.', tag: 'A1 DIALOGUE · A2 SCORE' },
  { key: 'EDIT', title: 'CUT IT.', tag: 'TIMELINE · V1' },
];

const stepAt = (local: number) => clamp(Math.floor(local / (BEAT / 4)), 0, 15);

/** Beats 16–36: one film is written, generated, animated, scored and cut while the clock races to zero. */
export function drawPipeline(ctx: Ctx, t: number, env: Env) {
  backdrop(ctx, env.fx, { glow: 0.14, glowY: 780 });
  const stage = clamp(Math.floor((t / BEAT - START) / 4), 0, 4);
  const t0 = b(START + stage * 4);
  const local = t - t0;

  drawClockPanel(ctx, CLOCK_HUD, remaining(t), t, wallClock(t));

  ctx.save();
  ctx.fillStyle = '#000';
  ctx.fillRect(MON.x, MON.y, MON.w, MON.h);
  [drawScript, drawDenoise, drawMotion, drawSound, drawEdit][stage](ctx, t, local, env);
  monitorChrome(ctx, stage, local);
  ctx.restore();

  const s = STAGES[stage];
  label(ctx, `0${stage + 1} / ${s.key}`, 92, 1112, { size: 30, color: COLOR.cyan, spacing: 4 });
  slamLine(ctx, s.title, 92, 1292, env.layout.stage, t, t0);
  const segW = (900 - 4 * 14) / 5;
  for (let i = 0; i < 5; i++) {
    const x = 90 + i * (segW + 14);
    ctx.fillStyle = i < stage ? white(0.85) : '#1f1f1f';
    ctx.fillRect(x, 1338, segW, 8);
    if (i === stage) {
      ctx.fillStyle = COLOR.red;
      ctx.fillRect(x, 1338, segW * clamp(local / b(4)), 8);
    }
  }
}

function monitorChrome(ctx: Ctx, stage: number, local: number) {
  const { x, y, w, h } = MON;
  const shade = ctx.createLinearGradient(0, y, 0, y + 72);
  shade.addColorStop(0, 'rgba(0,0,0,0.7)');
  shade.addColorStop(1, 'rgba(0,0,0,0)');
  ctx.fillStyle = shade;
  ctx.fillRect(x, y, w, 72);
  label(ctx, 'SC 01 · TK 01', x + 26, y + 38, { size: 20, color: white(0.78) });
  const tag = stage === 1 ? `DENOISE · STEP ${String(stepAt(local) + 1).padStart(2, '0')}/16` : STAGES[stage].tag;
  label(ctx, tag, x + w - 26, y + 38, { size: 20, color: white(0.78), align: 'right' });

  ctx.strokeStyle = '#2a2a2a';
  ctx.lineWidth = 2;
  ctx.strokeRect(x - 1, y - 1, w + 2, h + 2);
  ctx.strokeStyle = white(0.7);
  ctx.lineWidth = 3;
  const arm = 30;
  const m = 12;
  for (const [cx, cy, dx, dy] of [
    [x + m, y + m, 1, 1],
    [x + w - m, y + m, -1, 1],
    [x + m, y + h - m, 1, -1],
    [x + w - m, y + h - m, -1, -1],
  ]) {
    ctx.beginPath();
    ctx.moveTo(cx, cy + dy * arm);
    ctx.lineTo(cx, cy);
    ctx.lineTo(cx + dx * arm, cy);
    ctx.stroke();
  }
}

// ── 01 CONCEPT ──────────────────────────────────────────────────────────────
const SCRIPT: { text: string; weight: 400 | 700; color: string }[] = [
  { text: 'EXT. ROOFTOP — NIGHT', weight: 700, color: white(0.95) },
  { text: '', weight: 400, color: '' },
  { text: 'A lone filmmaker frames the city.', weight: 400, color: white(0.82) },
  { text: 'Forty-eight hours on the clock.', weight: 400, color: white(0.82) },
];

function drawScript(ctx: Ctx, t: number, local: number, env: Env) {
  const { x, y, w, h } = MON;
  ctx.fillStyle = '#0e0e10';
  ctx.fillRect(x, y, w, h);
  const typed = Math.floor(Math.max(0, local - 0.04) * 62);
  const garble = progress(local, b(3.1), b(3.9));
  const seed = Math.floor(t * 30);
  let left = typed;
  let cursor: [number, number] | null = null;
  ctx.save();
  for (const [i, line] of SCRIPT.entries()) {
    const ly = y + 150 + i * 66;
    label(ctx, String(i + 1), x + 40, ly, { size: 22, color: white(0.22), spacing: 0 });
    if (!line.text) continue;
    const n = clamp(left, 0, line.text.length);
    left -= line.text.length;
    if (n <= 0) continue;
    let text = line.text.slice(0, n);
    if (garble > 0) text = scramble(text, garble, seed + i * 97);
    ctx.font = font.mono(36, line.weight);
    ctx.letterSpacing = '0px';
    ctx.fillStyle = line.color;
    ctx.fillText(text, x + 92, ly);
    cursor = [x + 92 + ctx.measureText(text).width + 4, ly];
  }
  ctx.restore();
  if (cursor && garble < 0.5 && (local / BEAT) % 0.5 < 0.3) {
    const [cx, cy] = cursor;
    ctx.fillStyle = COLOR.cyan;
    ctx.fillRect(cx, cy - 32, 18, 40);
  }
  const noise = progress(local, b(3.45), b(4));
  if (noise > 0) drawNoise(ctx, env, 64, noise * 0.9, 0);
}

// ── 02 IMAGE ────────────────────────────────────────────────────────────────
const STEPS = [64, 50, 40, 32, 25, 19, 15, 11, 8, 6, 4.5, 3.3, 2.4, 1.7, 1.2, 1];

function noiseTile(env: Env, cols: number, rows: number, seed: number) {
  const key = `${cols}x${rows}:${seed}`;
  let tile = env.noise.get(key);
  if (!tile) {
    const c = canvas(cols, rows);
    const img = c.ctx.createImageData(cols, rows);
    const random = rng(seed * 7919 + cols);
    for (let i = 0; i < img.data.length; i += 4) {
      img.data[i] = random() * 255;
      img.data[i + 1] = random() * 255;
      img.data[i + 2] = random() * 255;
      img.data[i + 3] = 255;
    }
    c.ctx.putImageData(img, 0, 0);
    tile = c.el;
    env.noise.set(key, tile);
  }
  return tile;
}

function drawNoise(ctx: Ctx, env: Env, block: number, alpha: number, seed: number) {
  const cols = Math.max(1, Math.round(MON.w / block));
  const rows = Math.max(1, Math.round(MON.h / block));
  ctx.save();
  ctx.imageSmoothingEnabled = false;
  ctx.globalAlpha = alpha;
  ctx.drawImage(noiseTile(env, cols, rows, seed), MON.x, MON.y, MON.w, MON.h);
  ctx.restore();
}

/** Diffusion-style reveal: colour noise resolves into the frame on every sixteenth note. */
function drawDenoise(ctx: Ctx, _t: number, local: number, env: Env) {
  const step = stepAt(local);
  const block = STEPS[step];
  const cols = Math.max(1, Math.round(MON.w / block));
  const rows = Math.max(1, Math.round(MON.h / block));
  const s = env.scratch;
  s.ctx.globalCompositeOperation = 'copy';
  s.ctx.imageSmoothingEnabled = true;
  s.ctx.imageSmoothingQuality = 'high';
  s.ctx.drawImage(env.still, 0, 0, cols, rows);
  ctx.save();
  ctx.imageSmoothingEnabled = false;
  ctx.filter = `saturate(${(0.15 + (0.85 * step) / 15).toFixed(2)})`;
  ctx.drawImage(s.el, 0, 0, cols, rows, MON.x, MON.y, MON.w, MON.h);
  ctx.restore();
  const noise = Math.pow(1 - step / 15, 1.6) * 0.9;
  if (noise > 0.01) drawNoise(ctx, env, block, noise, step + 1);
  ctx.fillStyle = 'rgba(0,0,0,0.55)';
  ctx.fillRect(MON.x, MON.y + MON.h - 8, MON.w, 8);
  ctx.fillStyle = COLOR.cyan;
  ctx.fillRect(MON.x, MON.y + MON.h - 8, (MON.w * (step + 1)) / 16, 8);
}

// ── 03 MOTION ───────────────────────────────────────────────────────────────
function diamond(ctx: Ctx, x: number, y: number, r: number, color: string) {
  ctx.fillStyle = color;
  ctx.beginPath();
  ctx.moveTo(x, y - r);
  ctx.lineTo(x + r, y);
  ctx.lineTo(x, y + r);
  ctx.lineTo(x - r, y);
  ctx.closePath();
  ctx.fill();
}

function drawMotion(ctx: Ctx, t: number, local: number, _env: Env) {
  const p = progress(local, 0, b(4));
  const eased = easeInOutCubic(p);
  drawCity(ctx, MON.x, MON.y, MON.w, MON.h, { t: filmTime(t), zoom: 1 + 0.12 * eased, parallax: eased, rain: progress(local, 0, b(1)) });

  const sy = MON.y + MON.h - 80;
  ctx.fillStyle = 'rgba(0,0,0,0.6)';
  ctx.fillRect(MON.x, sy, MON.w, 80);
  const x0 = MON.x + 44;
  const x1 = MON.x + MON.w - 44;
  const y0 = sy + 60;
  const y1 = sy + 20;
  ctx.strokeStyle = COLOR.cyan;
  ctx.lineWidth = 3;
  ctx.beginPath();
  for (let i = 0; i <= 64; i++) {
    const u = i / 64;
    const px = lerp(x0, x1, u);
    const py = lerp(y0, y1, easeInOutCubic(u));
    if (i === 0) ctx.moveTo(px, py);
    else ctx.lineTo(px, py);
  }
  ctx.stroke();
  for (const u of [0, 0.5, 1]) diamond(ctx, lerp(x0, x1, u), lerp(y0, y1, easeInOutCubic(u)), 10, COLOR.yellow);
  ctx.fillStyle = COLOR.redHot;
  ctx.fillRect(lerp(x0, x1, p) - 1.5, sy + 6, 3, 68);
}

// ── 04 VOICE & SOUND ────────────────────────────────────────────────────────
function peakAt(env: Env, from: number, to: number) {
  const audio = env.audio;
  if (!audio || to <= 0) return 0;
  const s0 = Math.max(0, Math.floor(from * audio.sampleRate));
  const s1 = Math.min(audio.left.length, Math.floor(to * audio.sampleRate));
  let peak = 0;
  for (let s = s0; s < s1; s += 12) peak = Math.max(peak, Math.abs(audio.left[s]), Math.abs(audio.right[s]));
  return peak;
}

function rmsAt(env: Env, channel: 'left' | 'right', t: number, span = 0.07) {
  const audio = env.audio;
  if (!audio) return 0;
  const data = audio[channel];
  const s1 = Math.min(data.length, Math.floor(t * audio.sampleRate));
  const s0 = Math.max(0, s1 - Math.floor(span * audio.sampleRate));
  let sum = 0;
  let n = 0;
  for (let s = s0; s < s1; s += 4) {
    sum += data[s] * data[s];
    n++;
  }
  return n ? Math.sqrt(sum / n) : 0;
}

function drawSound(ctx: Ctx, t: number, local: number, env: Env) {
  const p = progress(local, 0, b(4));
  drawCity(ctx, MON.x, MON.y, MON.w, MON.h, { t: filmTime(t), zoom: 1.12 + 0.05 * p, parallax: 1 + 0.4 * p, rain: 1 });

  const bandY = MON.y + 292;
  const bandH = 116;
  ctx.fillStyle = 'rgba(0,0,0,0.5)';
  ctx.fillRect(MON.x, bandY, MON.w - 84, bandH);
  const bars = 84;
  const span = 1.6;
  const wx = MON.x + 22;
  const ww = MON.w - 128;
  for (let i = 0; i < bars; i++) {
    const from = t - span + (i / bars) * span;
    const peak = peakAt(env, from, from + span / bars);
    const hh = Math.max(2, Math.min(1, peak * 1.25) * bandH * 0.42);
    ctx.fillStyle = COLOR.cyan;
    ctx.globalAlpha = 0.3 + (0.7 * i) / bars;
    ctx.fillRect(wx + (i * ww) / bars, bandY + bandH / 2 - hh, ww / bars - 3, hh * 2);
  }
  ctx.globalAlpha = 1;

  const mx = MON.x + MON.w - 66;
  const my = MON.y + 86;
  const mh = 322;
  const segs = 14;
  (['left', 'right'] as const).forEach((channel, c) => {
    const lit = Math.round(clamp(rmsAt(env, channel, t) * 3.4) * segs);
    for (let s = 0; s < segs; s++) {
      ctx.fillStyle = s >= segs - 2 ? COLOR.redHot : s >= segs - 5 ? COLOR.yellow : COLOR.green;
      ctx.globalAlpha = s < lit ? 0.95 : 0.14;
      ctx.fillRect(mx + c * 24, my + mh - (s + 1) * (mh / segs) + 3, 18, mh / segs - 6);
    }
  });
  ctx.globalAlpha = 1;

  if (local > 0.14) {
    ctx.save();
    ctx.font = font.sans(34);
    ctx.textAlign = 'center';
    const text = '“Forty-eight hours. Roll camera.”';
    const tw = ctx.measureText(text).width;
    const cx = MON.x + (MON.w - 84) / 2;
    const base = MON.y + MON.h - 34;
    ctx.fillStyle = 'rgba(0,0,0,0.65)';
    ctx.fillRect(cx - tw / 2 - 18, base - 38, tw + 36, 52);
    ctx.fillStyle = COLOR.white;
    ctx.fillText(text, cx, base);
    ctx.restore();
  }
}

// ── 05 EDIT ─────────────────────────────────────────────────────────────────
const TRACKS = ['V2', 'V1', 'A1', 'A2'];
const TRACK_COLOR = [COLOR.cyan, COLOR.red, COLOR.green, '#0b9a61'];
const SHOTS = [
  { zoom: 1, cx: 0.5, cy: 0.5 },
  { zoom: 2.3, cx: 0.34, cy: 0.66 },
  { zoom: 2.0, cx: 0.7, cy: 0.36 },
  { zoom: 2.2, cx: 0.17, cy: 0.44 },
  { zoom: 1.12, cx: 0.5, cy: 0.52 },
];
/** Clips land on sixteenth notes (`at`), matching the snaps in the score. */
export const CLIPS = [
  { track: 1, from: 0, to: 0.22, at: 1, shot: 0 },
  { track: 1, from: 0.22, to: 0.4, at: 2, shot: 1 },
  { track: 1, from: 0.4, to: 0.58, at: 3, shot: 2 },
  { track: 1, from: 0.58, to: 0.78, at: 4, shot: 3 },
  { track: 1, from: 0.78, to: 1, at: 5, shot: 4 },
  { track: 0, from: 0.1, to: 0.3, at: 6 },
  { track: 0, from: 0.62, to: 0.9, at: 7 },
  { track: 2, from: 0.05, to: 0.35, at: 8 },
  { track: 2, from: 0.45, to: 0.72, at: 9 },
  { track: 3, from: 0, to: 1, at: 10 },
];

function drawEdit(ctx: Ctx, t: number, local: number, _env: Env) {
  const { x, y, w, h } = MON;
  const shrink = easeOutExpo(progress(local, 0, 0.3));
  const vw = lerp(w, 520, shrink);
  const vh = (vw * 9) / 16;
  const vx = x + (w - vw) / 2;
  const vy = lerp(y, y + 50, shrink);
  const tlX = x + 74;
  const tlW = w - 104;
  const tlY = y + 362;
  const rowH = 30;
  const gap = 6;
  const head = progress(local, b(0.4), b(3.6));

  ctx.fillStyle = '#0b0b0c';
  ctx.fillRect(x, y, w, h);
  const current = CLIPS.find((c) => c.track === 1 && local >= b(c.at / 4) && head >= c.from && head < c.to);
  const shot = SHOTS[current?.shot ?? 0];
  drawCity(ctx, vx, vy, vw, vh, { t: filmTime(t), rain: 1, parallax: 1.4, ...shot });
  ctx.strokeStyle = '#333';
  ctx.lineWidth = 2;
  ctx.strokeRect(vx, vy, vw, vh);

  ctx.save();
  ctx.globalAlpha = shrink;
  ctx.fillStyle = white(0.28);
  for (let i = 0; i <= 40; i++) {
    const tall = i % 5 === 0;
    ctx.fillRect(tlX + (tlW * i) / 40, tlY - (tall ? 18 : 11), 2, tall ? 12 : 6);
  }
  TRACKS.forEach((name, i) => {
    const ry = tlY + i * (rowH + gap);
    label(ctx, name, x + 24, ry + 22, { size: 18, color: white(0.55) });
    ctx.fillStyle = '#151516';
    ctx.fillRect(tlX, ry, tlW, rowH);
  });
  for (const clip of CLIPS) {
    const arrive = b(clip.at / 4);
    if (local < arrive) continue;
    const fly = 1 - easeOutExpo(progress(local, arrive, arrive + 0.14));
    const ry = tlY + clip.track * (rowH + gap);
    const cx = tlX + tlW * clip.from + fly * 460;
    const cw = tlW * (clip.to - clip.from) - 4;
    ctx.fillStyle = TRACK_COLOR[clip.track];
    ctx.fillRect(cx, ry + 2, cw, rowH - 4);
    ctx.fillStyle = 'rgba(0,0,0,0.35)';
    if (clip.track >= 2) {
      for (let i = 0; i < cw / 6; i++) {
        const amp = 3 + Math.abs(Math.sin(i * 1.7 + clip.from * 20)) * 9;
        ctx.fillRect(cx + i * 6, ry + rowH / 2 - amp / 2, 3, amp);
      }
    } else {
      ctx.fillRect(cx, ry + 2, 4, rowH - 4);
    }
  }
  const px = tlX + tlW * head;
  ctx.fillStyle = COLOR.redHot;
  ctx.fillRect(px - 1.5, tlY - 24, 3, 4 * (rowH + gap) + 18);
  ctx.beginPath();
  ctx.moveTo(px - 10, tlY - 30);
  ctx.lineTo(px + 10, tlY - 30);
  ctx.lineTo(px, tlY - 18);
  ctx.closePath();
  ctx.fill();
  ctx.restore();

  if (local > b(3.5)) {
    const text = 'RENDER 100% ✓';
    ctx.save();
    ctx.font = font.mono(28, 700);
    ctx.letterSpacing = '3px';
    const tw = ctx.measureText(text).width;
    ctx.fillStyle = COLOR.cyan;
    ctx.fillRect(vx + vw / 2 - tw / 2 - 22, vy + vh / 2 - 34, tw + 44, 62);
    ctx.fillStyle = '#001a1d';
    ctx.textAlign = 'center';
    ctx.fillText(text, vx + vw / 2, vy + vh / 2 + 9);
    ctx.restore();
  }
}
