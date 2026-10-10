export const W = 1080, H = 1920, FPS = 30, BPM = 140, BEAT = 60 / BPM;

export const C = {
  black: '#050404', crimson: '#C80528', cyan: '#00D2E6', ivory: '#F2E8D5',
  gold: '#E8B04A', cobalt: '#2F5BD3', amber: '#FFB347', doubt: '#a59e92',
};

export const clamp = (x, a = 0, b = 1) => Math.min(b, Math.max(a, x));
export const lerp = (a, b, t) => a + (b - a) * t;
export const ease = {
  outCubic: t => 1 - Math.pow(1 - clamp(t), 3),
  inOutCubic: t => (t = clamp(t)) < .5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2,
  outBack: t => { t = clamp(t); const c = 1.9; return 1 + (c + 1) * Math.pow(t - 1, 3) + c * Math.pow(t - 1, 2); },
};
export const smooth = (a, b, x) => { const t = clamp((x - a) / (b - a)); return t * t * (3 - 2 * t); };
export const frameIndex = (t, t0) => Math.floor((t - t0) * FPS + 1e-6);

export function rng(seed) {
  return () => { seed |= 0; seed = seed + 0x6D2B79F5 | 0; let t = Math.imul(seed ^ seed >>> 15, 1 | seed);
    t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t; return ((t ^ t >>> 14) >>> 0) / 4294967296; };
}

export function canvas(w = W, h = H) {
  const c = document.createElement('canvas'); c.width = w; c.height = h; return c;
}

// Polyline helpers. A polyline is an array of [x, y].
export function chaikin(pts, iterations = 2) {
  for (let k = 0; k < iterations; k++) {
    if (pts.length < 3) return pts;
    const out = [pts[0]];
    for (let i = 0; i < pts.length - 1; i++) {
      const [ax, ay] = pts[i], [bx, by] = pts[i + 1];
      out.push([ax * .75 + bx * .25, ay * .75 + by * .25], [ax * .25 + bx * .75, ay * .25 + by * .75]);
    }
    out.push(pts[pts.length - 1]); pts = out;
  }
  return pts;
}

export function resample(pts, step) {
  const out = [pts[0]]; let carry = 0;
  for (let i = 0; i < pts.length - 1; i++) {
    const [ax, ay] = pts[i], [bx, by] = pts[i + 1], len = Math.hypot(bx - ax, by - ay);
    let d = step - carry;
    while (d <= len) { const u = d / len; out.push([ax + (bx - ax) * u, ay + (by - ay) * u]); d += step; }
    carry = len - (d - step);
  }
  const last = pts[pts.length - 1], tail = out[out.length - 1];
  if (Math.hypot(last[0] - tail[0], last[1] - tail[1]) > step * .3) out.push(last);
  return out;
}

export function normals(pts) {
  return pts.map((p, i) => {
    const a = pts[Math.max(0, i - 1)], b = pts[Math.min(pts.length - 1, i + 1)];
    const dx = b[0] - a[0], dy = b[1] - a[1], l = Math.hypot(dx, dy) || 1;
    return [-dy / l, dx / l];
  });
}

export function length(pts) {
  let l = 0; for (let i = 1; i < pts.length; i++) l += Math.hypot(pts[i][0] - pts[i - 1][0], pts[i][1] - pts[i - 1][1]); return l;
}

// Draw the first `amount` pixels of a polyline.
export function partialPath(ctx, pts, amount) {
  if (amount <= 0 || pts.length < 2) return;
  ctx.moveTo(pts[0][0], pts[0][1]); let used = 0;
  for (let i = 1; i < pts.length; i++) {
    const [ax, ay] = pts[i - 1], [bx, by] = pts[i], l = Math.hypot(bx - ax, by - ay);
    if (used + l >= amount) { const u = (amount - used) / l; ctx.lineTo(ax + (bx - ax) * u, ay + (by - ay) * u); return; }
    ctx.lineTo(bx, by); used += l;
  }
}

// Flatten opentype.js path commands into closed polylines.
export function flatten(commands, step = 6) {
  const out = []; let line = [], p = { x: 0, y: 0 }, start = null;
  for (const c of commands) {
    if (c.type === 'M') { if (line.length) out.push(line); line = [[c.x, c.y]]; p = c; start = c; }
    else if (c.type === 'Z') { if (line.length) out.push(line); line = []; p = start; }
    else {
      const a = p, n = c.type === 'L' ? Math.max(1, Math.ceil(Math.hypot(c.x - a.x, c.y - a.y) / step)) : 14;
      for (let i = 1; i <= n; i++) {
        const t = i / n, u = 1 - t; let x, y;
        if (c.type === 'L') { x = a.x + (c.x - a.x) * t; y = a.y + (c.y - a.y) * t; }
        else if (c.type === 'Q') { x = u * u * a.x + 2 * u * t * c.x1 + t * t * c.x; y = u * u * a.y + 2 * u * t * c.y1 + t * t * c.y; }
        else { x = u ** 3 * a.x + 3 * u * u * t * c.x1 + 3 * u * t * t * c.x2 + t ** 3 * c.x; y = u ** 3 * a.y + 3 * u * u * t * c.y1 + 3 * u * t * t * c.y2 + t ** 3 * c.y; }
        line.push([x, y]);
      }
      p = c;
    }
  }
  if (line.length) out.push(line);
  return out;
}

// Inset or outset closed polygons with Clipper (global ClipperLib from the page).
export function offset(polys, delta, round = true) {
  const S = 100, co = new ClipperLib.ClipperOffset(2, 0.25 * S), sol = new ClipperLib.Paths();
  co.AddPaths(polys.map(p => p.map(([x, y]) => ({ X: Math.round(x * S), Y: Math.round(y * S) }))),
    round ? ClipperLib.JoinType.jtRound : ClipperLib.JoinType.jtMiter, ClipperLib.EndType.etClosedPolygon);
  co.Execute(sol, delta * S);
  return sol.map(p => p.map(q => [q.X / S, q.Y / S]));
}

export function closed(pts) { return pts.length ? [...pts, pts[0]] : pts; }

// Soft round sprite for bulbs and glints, drawn additively.
export function sprite(inner, outer, size = 96) {
  const c = canvas(size, size), g = c.getContext('2d'), r = size / 2;
  const grad = g.createRadialGradient(r, r, 0, r, r, r);
  grad.addColorStop(0, '#ffffff'); grad.addColorStop(.18, inner); grad.addColorStop(.42, outer); grad.addColorStop(1, 'rgba(0,0,0,0)');
  g.fillStyle = grad; g.fillRect(0, 0, size, size); return c;
}
