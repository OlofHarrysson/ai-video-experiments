import { W, C, canvas, clamp, ease, chaikin, resample, normals, length, partialPath } from './util.js';

const HERSHEY_CAP = 21; // futural: cap top -12, baseline 9

function layout(hershey, lines, { cap, maxW, centerY, gap }) {
  const rows = lines.map(text => {
    const letters = hershey.lines[text];
    const xs = letters.flatMap(l => l.strokes.flat().map(p => p[0]));
    return { letters, x1: Math.min(...xs), x2: Math.max(...xs) };
  });
  const s = Math.min(cap / HERSHEY_CAP, ...rows.map(r => maxW / (r.x2 - r.x1)));
  const lineH = HERSHEY_CAP * s, total = rows.length * lineH + (rows.length - 1) * gap * lineH;
  return rows.map((r, i) => {
    const top = centerY - total / 2 + i * lineH * (1 + gap), dx = W / 2 - (r.x1 + r.x2) / 2 * s, dy = top + 12 * s;
    const strokes = r.letters.flatMap(l => l.strokes.map(st => st.map(([x, y]) => [x * s + dx, y * s + dy])));
    return { strokes, scale: s };
  });
}

// MOST PEOPLE / COME ALONE.: one hairline thread enters from the left edge, writes every letter and leaves to the right.
export function createThread(hershey) {
  const rows = layout(hershey, ['MOST PEOPLE', 'COME ALONE.'], { cap: 62, maxW: 700, centerY: 990, gap: .9 });
  const items = [];
  let prev = null;
  rows.forEach((row, ri) => row.strokes.forEach(st => {
    const pts = resample(chaikin(st, 1), 3);
    if (prev) items.push({ pts: [prev, pts[0]], ink: false });
    items.push({ pts, ink: true }); prev = pts[pts.length - 1];
  }));
  items.push({ pts: [prev, [prev[0] + 60, prev[1] + 10], [W + 30, prev[1] + 10]], ink: false });
  items.forEach(it => it.len = length(it.pts));
  const total = items.reduce((a, it) => a + it.len, 0);

  const first = items[0].pts[0];
  return function draw(ctx, t, T0, { dur = .5, alpha = 1, from } = {}) {
    const u = t - T0;
    if (u < 0 || alpha <= 0) return;
    // The thread leaves the end of the doubt's hairline rule and climbs into the first letter.
    const lead = from ? resample([from, [from[0] - 50, from[1]], [from[0] - 50, first[1] + 34], [first[0] - 70, first[1] + 34], first], 3) : [first];
    const leadLen = length(lead), all = total + leadLen;
    let budget = ease.inOutCubic(u / dur) * all;
    ctx.save(); ctx.strokeStyle = 'rgba(242,232,213,.5)'; ctx.lineWidth = 1.3; ctx.lineCap = 'round';
    ctx.beginPath(); partialPath(ctx, chaikin(lead, 3), Math.min(budget, leadLen)); ctx.stroke(); ctx.restore();
    budget -= leadLen;
    ctx.save(); ctx.lineCap = 'round'; ctx.lineJoin = 'round'; ctx.globalAlpha = alpha;
    for (const it of items) {
      if (budget <= 0) break;
      ctx.beginPath(); partialPath(ctx, it.pts, Math.min(budget, it.len));
      if (it.ink) { ctx.strokeStyle = C.ivory; ctx.lineWidth = 2.6; ctx.shadowColor = 'rgba(242,232,213,.6)'; ctx.shadowBlur = 8; }
      else { ctx.strokeStyle = 'rgba(242,232,213,.28)'; ctx.lineWidth = 1.1; ctx.shadowBlur = 0; }
      ctx.stroke(); budget -= it.len;
    }
    ctx.restore();
  };
}

// CREWS / FORM / FRIDAY: three coloured strands braid around the same kind of skeleton, led by the ivory thread.
export function createBraid(hershey) {
  const cap = 228, rows = layout(hershey, ['CREWS', 'FORM', 'FRIDAY'], { cap, maxW: 900, centerY: 935, gap: .5 });
  const strandW = .1 * cap, amp = .05 * cap, lambda = .58 * cap;
  const STRANDS = [C.crimson, C.cobalt, C.gold];
  const shades = STRANDS.map(hex => {
    const n = parseInt(hex.slice(1), 16), r = n >> 16, g = n >> 8 & 255, b = n & 255;
    return Array.from({ length: 17 }, (_, i) => { const k = .5 + .5 * i / 16; return `rgb(${r * k | 0},${g * k | 0},${b * k | 0})`; });
  });
  const lines = rows.map(row => {
    let s0 = 0;
    const strokes = row.strokes.map(st => {
      const pts = resample(chaikin(st, 2), 4), nrm = normals(pts), s = [];
      let acc = s0; pts.forEach((p, i) => { if (i) acc += Math.hypot(p[0] - pts[i - 1][0], p[1] - pts[i - 1][1]); s.push(acc); });
      s0 = acc + 1; return { pts, nrm, s };
    });
    return { strokes, len: s0 };
  });

  const layer = canvas(), lc = layer.getContext('2d');

  return function draw(target, t, T0) {
    const u = t - T0;
    if (u < 0) return;
    const flow = u * 150, ctx = lc;
    ctx.clearRect(0, 0, layer.width, layer.height);
    ctx.save(); ctx.lineJoin = 'round';
    lines.forEach((line, li) => {
      const lead = ease.outCubic((u - li * .04) / .36) * line.len;
      const reach = STRANDS.map((_, k) => ease.outCubic((u - .05 - k * .06 - li * .04) / .44) * line.len);
      // Lead thread.
      ctx.strokeStyle = C.ivory; ctx.lineWidth = 2.4; ctx.lineCap = 'round';
      for (const st of line.strokes) {
        if (st.s[0] > lead) break;
        ctx.beginPath(); partialPath(ctx, st.pts, lead - st.s[0]); ctx.stroke();
      }
      // Braided strands, sorted by depth per segment for over/under weaving.
      for (const st of line.strokes) {
        const { pts, nrm, s } = st;
        for (let i = 0; i < pts.length - 1; i++) {
          const order = [0, 1, 2].map(k => {
            const th0 = (s[i] - flow) / lambda * 2 * Math.PI + k * 2 * Math.PI / 3;
            const th1 = (s[i + 1] - flow) / lambda * 2 * Math.PI + k * 2 * Math.PI / 3;
            return { k, o0: amp * Math.sin(th0), o1: amp * Math.sin(th1), d: Math.cos(th0) };
          }).sort((a, b) => a.d - b.d);
          for (const { k, o0, o1, d } of order) {
            if (s[i + 1] > reach[k]) continue;
            const [ax, ay] = pts[i], [bx, by] = pts[i + 1], [anx, any] = nrm[i], [bnx, bny] = nrm[i + 1], h = strandW / 2;
            const c0x = ax + anx * o0, c0y = ay + any * o0, c1x = bx + bnx * o1, c1y = by + bny * o1;
            ctx.beginPath();
            ctx.moveTo(c0x + anx * h, c0y + any * h); ctx.lineTo(c1x + bnx * h, c1y + bny * h);
            ctx.lineTo(c1x - bnx * h, c1y - bny * h); ctx.lineTo(c0x - anx * h, c0y - any * h); ctx.closePath();
            const col = shades[k][Math.round((d + 1) / 2 * 16)];
            ctx.fillStyle = col; ctx.strokeStyle = col; ctx.lineWidth = .8; ctx.fill(); ctx.stroke();
            // Edge shadow keeps crossings readable.
            ctx.strokeStyle = 'rgba(0,0,0,.45)'; ctx.lineWidth = 1.1;
            ctx.beginPath(); ctx.moveTo(c0x + anx * h, c0y + any * h); ctx.lineTo(c1x + bnx * h, c1y + bny * h);
            ctx.moveTo(c0x - anx * h, c0y - any * h); ctx.lineTo(c1x - bnx * h, c1y - bny * h); ctx.stroke();
            if (d > .55) { ctx.strokeStyle = 'rgba(255,248,230,.35)'; ctx.lineWidth = 1.4; ctx.beginPath(); ctx.moveTo(c0x, c0y); ctx.lineTo(c1x, c1y); ctx.stroke(); }
          }
        }
      }
    });
    ctx.restore();
    // Soft drop shadow for depth, then the strands.
    target.save(); target.filter = 'blur(10px) brightness(0)'; target.globalAlpha = .7; target.drawImage(layer, 10, 16);
    target.filter = 'none'; target.globalAlpha = 1; target.drawImage(layer, 0, 0); target.restore();
  };
}
