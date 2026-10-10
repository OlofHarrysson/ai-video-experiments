import { W, H, C, BEAT, canvas, clamp, ease, rng, flatten, offset, closed, resample, length, partialPath, sprite, frameIndex } from './util.js';

// NO AI EXPERIENCE NEEDED: a cinema marquee that builds itself from code.
const LINES = [['NO AI', 250], ['EXPERIENCE', 178], ['NEEDED', 232]];
const MAX_W = 840, GAP = 50, PAD_X = 38, PAD_Y = 30, CENTER_Y = 900;
const GOLD = '#d9a441', GOLD_DARK = '#7a5520', MAGENTA = '#ff3fb4';

function transform(cmds, s, dx, dy) {
  return cmds.map(c => {
    const o = { type: c.type };
    for (const k of ['x', 'y', 'x1', 'y1', 'x2', 'y2']) if (c[k] !== undefined) o[k] = k[0] === 'x' ? c[k] * s + dx : c[k] * s + dy;
    return o;
  });
}
function pathFromCommands(cmds) {
  const p = new Path2D();
  for (const c of cmds) {
    if (c.type === 'M') p.moveTo(c.x, c.y); else if (c.type === 'L') p.lineTo(c.x, c.y);
    else if (c.type === 'Q') p.quadraticCurveTo(c.x1, c.y1, c.x, c.y); else if (c.type === 'C') p.bezierCurveTo(c.x1, c.y1, c.x2, c.y2, c.x, c.y);
    else if (c.type === 'Z') p.closePath();
  }
  return p;
}
function normalise(polys) {
  const S = 100, paths = polys.map(p => p.map(([x, y]) => ({ X: Math.round(x * S), Y: Math.round(y * S) })));
  return ClipperLib.Clipper.SimplifyPolygons(paths, ClipperLib.PolyFillType.pftNonZero).map(p => p.map(q => [q.X / S, q.Y / S]));
}
function roundRect(x, y, w, h, r) {
  const pts = [], arc = (cx, cy, a0) => { for (let i = 0; i <= 8; i++) { const a = a0 + i / 8 * Math.PI / 2; pts.push([cx + r * Math.cos(a), cy + r * Math.sin(a)]); } };
  arc(x + w - r, y + r, -Math.PI / 2); arc(x + w - r, y + h - r, 0); arc(x + r, y + h - r, Math.PI / 2); arc(x + r, y + r, Math.PI);
  return pts;
}
function star(cx, cy, r) {
  const p = new Path2D();
  for (let i = 0; i < 10; i++) { const a = -Math.PI / 2 + i * Math.PI / 5, rr = i % 2 ? r * .42 : r; i ? p.lineTo(cx + rr * Math.cos(a), cy + rr * Math.sin(a)) : p.moveTo(cx + rr * Math.cos(a), cy + rr * Math.sin(a)); }
  p.closePath(); return p;
}

export function createMarquee({ anton }) {
  const stemRef = anton.getPath('I', 0, 0, 100).getBoundingBox();
  const stemRatio = (stemRef.x2 - stemRef.x1) / (stemRef.y2 - stemRef.y1);
  const R = rng(7);

  // Layout lines.
  const laid = LINES.map(([text, capMax]) => {
    const b = anton.getPath(text, 0, 0, 100).getBoundingBox();
    const s = Math.min(MAX_W / (b.x2 - b.x1), capMax / (b.y2 - b.y1));
    return { text, s, b, w: (b.x2 - b.x1) * s, h: (b.y2 - b.y1) * s };
  });
  const totalH = laid.reduce((a, l) => a + l.h + 2 * PAD_Y, 0) + GAP * (laid.length - 1);
  let y = CENTER_Y - totalH / 2;
  const glyphs = [], panels = [];
  for (const l of laid) {
    const top = y + PAD_Y, dx = W / 2 - (l.b.x1 + l.b.x2) / 2 * l.s, dy = top - l.b.y1 * l.s;
    panels.push({ x: W / 2 - l.w / 2 - PAD_X, y, w: l.w + 2 * PAD_X, h: l.h + 2 * PAD_Y, cap: l.h });
    for (const gp of anton.getPaths(l.text, 0, 0, 100)) {
      if (!gp.commands.length) continue;
      const cmds = transform(gp.commands, l.s, dx, dy);
      const polys = normalise(flatten(cmds, 4));
      const stem = stemRatio * l.h, r = .04 * l.h;
      const inner = offset(polys, -.1 * l.h);
      const channel = offset(polys, -stem * .3);
      const bulbs = [];
      for (const poly of channel) for (const p of resample(closed(poly), .112 * l.h).slice(0, -1)) bulbs.push({ x: p[0], y: p[1], r, j: R() });
      const outline = polys.map(p => resample(closed(p), 6));
      glyphs.push({ path: pathFromCommands(cmds), outline, inner, bulbs, cap: l.h, cx: polys[0]?.[0]?.[0] ?? W / 2, line: glyphs.length });
    }
    y += l.h + 2 * PAD_Y + GAP;
  }
  glyphs.forEach((g, i) => g.order = i);

  // Panel borders with chasing bulbs.
  const borders = panels.map(p => {
    const pts = resample(closed(roundRect(p.x, p.y, p.w, p.h, 22)), 4);
    return { pts, len: length(pts), bulbs: resample(pts, 26).slice(0, -1).map(q => ({ x: q[0], y: q[1] })) };
  });

  // Outer shield: rounded body, crown arc on top, pointed base. Drawn as two halves from the base outward.
  const top = panels[0].y - 34, bottom = panels[panels.length - 1].y + panels[panels.length - 1].h + 34;
  const left = Math.min(...panels.map(p => p.x)) - 34, right = Math.max(...panels.map(p => p.x + p.w)) + 34;
  const crownR = 150, crownY = top;
  const half = side => {
    const s = side, pts = [[W / 2, bottom + 78], [W / 2 + s * 70, bottom], [W / 2 + s * (right - W / 2), bottom], [W / 2 + s * (right - W / 2), top + 40]];
    pts.push([W / 2 + s * (right - W / 2 - 30), top], [W / 2 + s * crownR, top]);
    for (let i = 0; i <= 24; i++) { const a = i / 24 * Math.PI / 2; pts.push([W / 2 + s * crownR * Math.cos(a), crownY - crownR * Math.sin(a)]); }
    return resample(pts, 5);
  };
  const shield = [half(1), half(-1)].map(pts => ({ pts, len: length(pts) }));
  const rays = [];
  for (let i = 0; i < 11; i++) {
    const a = Math.PI + (i + .5) / 11 * Math.PI, pts = [];
    for (let k = 0; k < 5; k++) { const rr = 34 + k * 24; pts.push({ x: W / 2 + Math.cos(a) * rr, y: crownY + Math.sin(a) * rr }); }
    rays.push(pts);
  }
  const burst = Array.from({ length: 23 }, (_, i) => Math.PI + (i + .5) / 23 * Math.PI);
  const shieldBulbs = shield.map(h => resample(h.pts, 30).map(q => ({ x: q[0], y: q[1] })));
  const stars = [[W / 2, crownY - crownR - 46, 34], [left + 10, top - 34, 26], [right - 10, top - 34, 26], [W / 2, bottom + 118, 24]];

  const bulbWarm = sprite('#ffe9b0', 'rgba(255,150,40,.55)'), bulbHot = sprite('#fff6dc', 'rgba(255,190,90,.7)');
  const light = canvas(), lg = light.getContext('2d');

  return function draw(ctx, t, T0) {
    const u = t - T0;
    if (u < 0) return;
    const build = k => clamp(k);
    const flash = [1, 2].some(k => { const f = frameIndex(t, T0 + k * BEAT); return f >= 0 && f <= 1; });
    const chase = Math.floor(u * 14);
    lg.globalCompositeOperation = 'source-over'; lg.clearRect(0, 0, W, H);

    // Shield neon tubes.
    for (const [color, width, inset] of [[MAGENTA, 5, 0], [C.cyan, 3.5, 16]]) {
      for (const h of shield) {
        const p = ease.outCubic(build(u / .22)) * h.len;
        lg.save(); lg.translate(W / 2, (top + bottom) / 2); lg.scale(1 + inset / 400, 1 + inset / 700); lg.translate(-W / 2, -(top + bottom) / 2);
        lg.strokeStyle = color; lg.lineWidth = width; lg.lineCap = 'round'; lg.lineJoin = 'round';
        lg.beginPath(); partialPath(lg, h.pts, p); lg.stroke(); lg.restore();
      }
    }

    // Deco sunburst inside the crown and a gold inner shield line.
    ctx.save(); ctx.strokeStyle = GOLD; ctx.globalAlpha = .55; ctx.lineWidth = 2;
    burst.forEach((a, i) => { const p = clamp((u - .12 - Math.abs(i - 11) * .006) / .12); if (p <= 0) return;
      ctx.beginPath(); ctx.moveTo(W / 2 + Math.cos(a) * 26, crownY + Math.sin(a) * 26); ctx.lineTo(W / 2 + Math.cos(a) * (26 + (crownR - 40) * ease.outCubic(p)), crownY + Math.sin(a) * (26 + (crownR - 40) * ease.outCubic(p))); ctx.stroke(); });
    ctx.globalAlpha = 1; ctx.lineWidth = 2.5;
    for (const h of shield) { ctx.save(); ctx.translate(W / 2, (top + bottom) / 2); ctx.scale(.965, .975); ctx.translate(-W / 2, -(top + bottom) / 2);
      ctx.beginPath(); partialPath(ctx, h.pts, ease.outCubic(build((u - .05) / .25)) * h.len); ctx.stroke(); ctx.restore(); }
    ctx.restore();
    shieldBulbs.forEach(list => list.forEach((q, k) => { if (k / list.length > build((u - .08) / .25)) return;
      const on = (k + chase) % 4 === 0; lg.globalAlpha = u < .42 ? .8 : on ? 1 : .3; lg.drawImage(on ? bulbHot : bulbWarm, q.x - 11, q.y - 11, 22, 22); }));
    lg.globalAlpha = 1;

    // Panels.
    borders.forEach((b, i) => {
      const p = build((u - .04 - i * .03) / .22);
      ctx.save(); ctx.strokeStyle = GOLD; ctx.lineWidth = 4; ctx.beginPath(); partialPath(ctx, b.pts, ease.outCubic(p) * b.len); ctx.stroke(); ctx.restore();
      b.bulbs.forEach((q, k) => {
        if (k / b.bulbs.length > p) return;
        const on = (k + chase) % 3 === 0, a = u < .42 ? .9 : (on ? 1 : .32);
        lg.globalAlpha = a; lg.drawImage(on ? bulbHot : bulbWarm, q.x - 13, q.y - 13, 26, 26);
      });
    });

    // Letters: dark face, double gold outline, bulbs in the channel.
    lg.globalAlpha = 1;
    for (const g of glyphs) {
      const p = build((u - .06 - g.order * .012) / .2);
      if (p <= 0) continue;
      ctx.save(); ctx.globalAlpha = ease.outCubic(p); ctx.fillStyle = '#160b05'; ctx.fill(g.path); ctx.restore();
      ctx.save(); ctx.strokeStyle = GOLD; ctx.lineWidth = .024 * g.cap; ctx.lineJoin = 'round';
      for (const o of g.outline) { ctx.beginPath(); partialPath(ctx, o, ease.outCubic(p) * length(o)); ctx.stroke(); }
      ctx.strokeStyle = GOLD_DARK; ctx.lineWidth = 1.6;
      for (const o of g.inner) { ctx.beginPath(); ctx.moveTo(o[0][0], o[0][1]); for (const q of o) ctx.lineTo(q[0], q[1]); ctx.closePath(); ctx.globalAlpha = p; ctx.stroke(); }
      ctx.restore();
      const n = g.bulbs.length;
      g.bulbs.forEach((bl, k) => {
        const pop = build((u - .1 - g.order * .016 - k / n * .1) / .06);
        if (pop <= 0) return;
        const flick = Math.floor(u * 15 + bl.j * 9) % 7 === 0 && bl.j < .06 ? .25 : .82 + .18 * Math.sin(bl.j * 40 + Math.floor(u * 15));
        const sz = bl.r * 4.4 * ease.outBack(pop) * (flash ? 1.2 : 1);
        lg.globalAlpha = clamp(flick * (flash ? 1.3 : 1));
        lg.drawImage(flash ? bulbHot : bulbWarm, bl.x - sz / 2, bl.y - sz / 2, sz, sz);
        ctx.fillStyle = '#2a1608'; ctx.globalAlpha = pop; ctx.beginPath(); ctx.arc(bl.x, bl.y, bl.r * 1.05, 0, 7); ctx.fill();
        ctx.fillStyle = '#ffeec8'; ctx.beginPath(); ctx.arc(bl.x, bl.y, bl.r * .62, 0, 7); ctx.fill(); ctx.globalAlpha = 1;
      });
    }

    // Crown fan and stars.
    rays.forEach((ray, i) => ray.forEach((q, k) => {
      const p = build((u - .14 - k * .03 - Math.abs(i - 5) * .01) / .05);
      if (p <= 0) return;
      const on = (k + chase) % 2 === 0;
      lg.globalAlpha = p * (u < .45 ? .9 : on ? 1 : .45); lg.drawImage(bulbWarm, q.x - 12, q.y - 12, 24, 24);
    }));
    lg.globalAlpha = 1;
    stars.forEach(([x, y, r], i) => {
      const p = ease.outBack(build((u - .28 - i * .03) / .1));
      if (p <= 0) return;
      const s = star(x, y, r * p);
      ctx.save(); ctx.strokeStyle = GOLD; ctx.lineWidth = 3; ctx.stroke(s); ctx.restore();
      lg.save(); lg.strokeStyle = i % 2 ? C.cyan : '#ffd27a'; lg.lineWidth = 3; lg.stroke(s); lg.restore();
    });

    // Glow passes, then the sharp light layer.
    ctx.save(); ctx.globalCompositeOperation = 'lighter';
    ctx.filter = 'blur(26px)'; ctx.globalAlpha = .42; ctx.drawImage(light, 0, 0);
    ctx.filter = 'blur(5px)'; ctx.globalAlpha = .45; ctx.drawImage(light, 0, 0);
    ctx.filter = 'none'; ctx.globalAlpha = 1; ctx.drawImage(light, 0, 0);
    ctx.restore();
  };
}
