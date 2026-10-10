import { W, H, BEAT, canvas, clamp, ease, rng, sprite, frameIndex } from './util.js';
import { layer, maskFrom, lumaMask, toned, luma, brightSpots, drawMasked } from './imagecard.js';

// NO AI EXPERIENCE NEEDED: the generated marquee switches itself on.
// The unlit state is derived from the same pixels, so both states align exactly.
export function createMarqueeImage({ image }) {
  const lit = layer(image);
  const unlit = toned(lit, (r, g, b) => {
    const l = luma(r, g, b), k = .17;
    return [k * (r * .7 + l * .3) * 1.05, k * (g * .7 + l * .3), k * (b * .7 + l * .3) * .85];
  });
  const neon = maskFrom(lit, (r, g, b) => {
    const magenta = clamp((Math.min(r, b) - g - .15) * 4), cyan = clamp((Math.min(g, b) - r - .2) * 4);
    return Math.max(magenta, cyan);
  });
  const glow = lumaMask(lit, .35, .8);

  // Bulbs: bright local maxima, ordered from the outer frame inward, with a little seeded jitter.
  const R = rng(5), spots = brightSpots(lit, .86, 12);
  const cx = spots.reduce((a, s) => a + s.x, 0) / spots.length, cy = spots.reduce((a, s) => a + s.y, 0) / spots.length;
  spots.forEach(s => {
    s.d = Math.hypot((s.x - cx) / (W * .45), (s.y - cy) / (H * .32)) + R() * .08;
    s.a = Math.atan2(s.y - cy, s.x - cx);
  });
  const build = [...spots].sort((a, b) => b.d - a.d);
  const ring = [...spots].sort((a, b) => a.a - b.a);
  const soft = sprite('#ffffff', 'rgba(255,255,255,.6)', 64);

  return function draw(ctx, t, T0) {
    const u = t - T0;
    if (u < 0) return;
    // Power arrives from the base: the unlit sign is uncovered by a fast radial wipe.
    const wipe = ease.outCubic(u / .14) * 1900;
    drawMasked(ctx, unlit, g => { g.beginPath(); g.arc(W / 2, H * .82, wipe, 0, 7); g.fill(); });

    // Neon tubes stutter on.
    const neonOn = u > .07 && (u > .22 || [1, 0, 1, 1, 0, 1][frameIndex(t, T0 + .07) % 6]);
    if (neonOn) drawMasked(ctx, lit, g => g.drawImage(neon, 0, 0));

    // Bulbs pop on one by one, then the whole sign blooms.
    const bloom = ease.outCubic((u - .4) / .12);
    if (bloom < 1) {
      const n = Math.floor(ease.inOutCubic((u - .1) / .3) * build.length);
      if (n > 0) drawMasked(ctx, lit, g => {
        for (let i = 0; i < n; i++) { const s = build[i], r = i > n - 12 ? 30 : 22; g.drawImage(soft, s.x - r, s.y - r, 2 * r, 2 * r); }
      });
    }
    if (bloom > 0) { ctx.save(); ctx.globalAlpha = bloom; ctx.drawImage(lit, 0, 0); ctx.restore(); }

    // Chase: every third bulb around the ring drops to its unlit state.
    if (u > .55) {
      const phase = Math.floor(u * 12) % 3;
      drawMasked(ctx, unlit, g => { ring.forEach((s, i) => { if (i % 3 === phase) g.drawImage(soft, s.x - 13, s.y - 13, 26, 26); }); }, { alpha: .75 });
    }
    // Beat flashes on the two beats after the landing.
    if ([1, 2].some(k => { const f = frameIndex(t, T0 + k * BEAT); return f >= 0 && f <= 1; }))
      drawMasked(ctx, lit, g => g.drawImage(glow, 0, 0), { op: 'lighter', alpha: .45 });
  };
}
