import { BEAT, COLOR, EVENT_SECONDS, b, white } from '../config';
import { lerp, progress, type Ctx } from '../util';
import { font } from './fonts';
import { fitSize, label } from './text';

/** Beat where the countdown reaches 00:00:00, half a beat before the premiere cut. */
export const CLOCK_ZERO = 35.5;

/**
 * Event seconds elapsed on the 48-hour clock. It ticks one second per beat after it starts,
 * then races through the weekend during the pipeline montage.
 */
export function elapsedEvent(t: number) {
  if (t < b(13)) return 0;
  if (t < b(16)) return Math.floor((t - b(13)) / BEAT) + 1;
  const v = progress(t, b(16), b(CLOCK_ZERO));
  return 3 + (EVENT_SECONDS - 3) * Math.pow(v, 1.6);
}

export const remaining = (t: number) => EVENT_SECONDS - elapsedEvent(t);

const pad2 = (n: number) => String(n).padStart(2, '0');

export function hms(seconds: number) {
  const s = Math.max(0, Math.floor(seconds));
  return `${pad2(Math.floor(s / 3600))}:${pad2(Math.floor((s % 3600) / 60))}:${pad2(s % 60)}`;
}

const DAYS = ['FRI', 'SAT', 'SUN'];
const PHASE = ['ALIGN', 'BUILD', 'PREMIERE'];

/** Weekend wall clock: the countdown starts Friday 15:00. */
export function wallClock(t: number) {
  const minutes = 15 * 60 + Math.floor(elapsedEvent(t) / 60);
  const day = Math.min(2, Math.floor(minutes / 1440));
  const hh = Math.floor((minutes % 1440) / 60);
  return `${DAYS[day]} ${pad2(hh)}:${pad2(minutes % 60)} · ${PHASE[day]}`;
}

export interface Rect {
  x: number;
  y: number;
  w: number;
  h: number;
}

export const lerpRect = (a: Rect, c: Rect, p: number): Rect => ({
  x: lerp(a.x, c.x, p),
  y: lerp(a.y, c.y, p),
  w: lerp(a.w, c.w, p),
  h: lerp(a.h, c.h, p),
});

/** The site's "ROLLING IN" countdown panel, scaled to any rect with a 900:330 aspect. */
export function drawClockPanel(ctx: Ctx, r: Rect, seconds: number, t: number, header: string) {
  const k = r.w / 900;
  const alarm = seconds <= 0;
  const beatPhase = (t / BEAT) % 1;

  ctx.fillStyle = '#070707';
  ctx.fillRect(r.x, r.y, r.w, r.h);
  ctx.strokeStyle = '#222';
  ctx.lineWidth = 2 * k;
  ctx.strokeRect(r.x, r.y, r.w, r.h);

  const pad = 34 * k;
  const blink = alarm ? beatPhase % 0.25 < 0.14 : beatPhase < 0.55;
  label(ctx, '■ ROLLING', r.x + pad, r.y + 56 * k, { size: 24 * k, color: blink ? COLOR.redHot : 'rgba(255,30,80,0.3)' });
  label(ctx, header, r.x + r.w - pad, r.y + 56 * k, { size: 24 * k, color: white(0.55), align: 'right' });

  const size = fitSize(ctx, ['88:88:88'], font.seg, r.w - pad * 2.4, 400);
  ctx.save();
  ctx.font = font.seg(size);
  ctx.textBaseline = 'alphabetic';
  const full = ctx.measureText('88:88:88').width;
  const left = r.x + (r.w - full) / 2;
  const base = r.y + r.h - 78 * k;
  const color = alarm ? COLOR.redHot : COLOR.cyan;
  ctx.fillStyle = alarm ? 'rgba(255,30,80,0.09)' : 'rgba(0,210,230,0.08)';
  ctx.fillText('88:88:88', left, base);
  if (!alarm || blink) {
    ctx.shadowColor = color;
    ctx.shadowBlur = 30 * k;
    ctx.fillStyle = color;
    ctx.fillText(hms(seconds), left, base);
  }
  const pair = ctx.measureText('88').width;
  const colon = ctx.measureText('88:').width;
  const pairTwo = ctx.measureText('88:88:').width;
  ctx.restore();

  const unitY = r.y + r.h - 30 * k;
  const unit = { size: 20 * k, color: white(0.4), align: 'center' as const };
  label(ctx, 'HRS', left + pair / 2, unitY, unit);
  label(ctx, 'MIN', left + colon + pair / 2, unitY, unit);
  label(ctx, 'SEC', left + pairTwo + pair / 2, unitY, unit);
}
