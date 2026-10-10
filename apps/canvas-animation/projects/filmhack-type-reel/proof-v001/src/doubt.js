import { C, clamp, lerp, ease } from './util.js';

// The recurring quiet identity: small italic, low-left, typed with a cursor over a hairline rule.
export const DOUBT = { x: 104, y: 1150, size: 54, font: 'Doubt' };

export function doubtMetrics(ctx, text) {
  ctx.font = `italic 400 ${DOUBT.size}px ${DOUBT.font}`;
  return ctx.measureText(text).width;
}

// t0: typing start; typeDur: seconds to type; crush: 0..1 as an answer lands; ruleExtra: px the rule reaches past the text.
export function drawDoubt(ctx, text, t, { t0, typeDur = .22, crush = 0, alpha = 1, ruleExtra = 0, cursor = true }) {
  const local = t - t0;
  if (local < 0 || alpha <= 0) return;
  const n = Math.round(text.length * clamp(local / typeDur));
  const shown = text.slice(0, n);
  ctx.save();
  ctx.globalAlpha = alpha * lerp(1, .5, crush);
  const e = ease.outCubic(crush);
  ctx.translate(DOUBT.x, DOUBT.y + 70 * e);
  ctx.scale(lerp(1, 1.08, e), lerp(1, .14, e));
  ctx.font = `italic 400 ${DOUBT.size}px ${DOUBT.font}`;
  ctx.fillStyle = C.doubt;
  ctx.shadowColor = 'rgba(255,214,170,.35)'; ctx.shadowBlur = 10;
  ctx.fillText(shown, 0, 0);
  ctx.shadowBlur = 0;
  const w = ctx.measureText(shown).width;
  ctx.fillStyle = 'rgba(165,158,146,.55)';
  ctx.fillRect(0, 22, w + ruleExtra, 1.6);
  const typing = local < typeDur + .05;
  if (cursor && crush === 0 && (typing || Math.floor(local / .26) % 2 === 0)) {
    ctx.fillStyle = 'rgba(242,232,213,.85)';
    ctx.fillRect(w + 8, -40, 2.4, 50);
  }
  ctx.restore();
}
