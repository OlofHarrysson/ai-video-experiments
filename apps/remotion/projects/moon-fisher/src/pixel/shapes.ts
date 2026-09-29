import { clamp } from "./pix";

export type Vec2 = readonly [number, number];
export type Vec3 = readonly [number, number, number];

// Shapes are authored in design units. Each one also knows its surface
// normal, so drawn objects can be lit from wherever the moon happens to be.
export type Shape =
  | {
      kind: "ellipse";
      cx: number;
      cy: number;
      rx: number;
      ry: number;
      rot: number;
    }
  | { kind: "capsule"; a: Vec2; b: Vec2; ra: number; rb: number }
  | { kind: "poly"; pts: readonly Vec2[] }
  // Several shapes grown together like clay, with fillets about `k` wide.
  // `wobble` roughens the outline, for cloth and fur.
  | {
      kind: "blend";
      shapes: readonly Shape[];
      k: number;
      wobble: number;
      seed: number;
    };

export const ellipse = (
  cx: number,
  cy: number,
  rx: number,
  ry = rx,
  rot = 0,
): Shape => ({ kind: "ellipse", cx, cy, rx, ry, rot });

// A limb: a tapered tube with rounded ends.
export const capsule = (a: Vec2, b: Vec2, ra: number, rb = ra): Shape => ({
  kind: "capsule",
  a,
  b,
  ra,
  rb,
});

export const poly = (pts: readonly Vec2[]): Shape => ({ kind: "poly", pts });

export const blend = (
  shapes: readonly Shape[],
  k: number,
  wobble = 0,
  seed = 0,
): Shape => ({ kind: "blend", shapes, k, wobble, seed });

// A smooth closed outline through control points (Catmull-Rom).
export const blob = (pts: readonly Vec2[], samples = 6): Shape => {
  const out: Vec2[] = [];
  const n = pts.length;
  for (let i = 0; i < n; i++) {
    const p0 = pts[(i - 1 + n) % n];
    const p1 = pts[i];
    const p2 = pts[(i + 1) % n];
    const p3 = pts[(i + 2) % n];
    for (let s = 0; s < samples; s++) {
      const t = s / samples;
      const t2 = t * t;
      const t3 = t2 * t;
      const f = (a: number, b: number, c: number, d: number) =>
        0.5 *
        (2 * b +
          (-a + c) * t +
          (2 * a - 5 * b + 4 * c - d) * t2 +
          (-a + 3 * b - 3 * c + d) * t3);
      out.push([f(p0[0], p1[0], p2[0], p3[0]), f(p0[1], p1[1], p2[1], p3[1])]);
    }
  }
  return poly(out);
};

export const bounds = (s: Shape): [number, number, number, number] => {
  switch (s.kind) {
    case "ellipse": {
      const r = Math.max(s.rx, s.ry);
      return [s.cx - r, s.cy - r, s.cx + r, s.cy + r];
    }
    case "capsule": {
      const r = Math.max(s.ra, s.rb);
      return [
        Math.min(s.a[0], s.b[0]) - r,
        Math.min(s.a[1], s.b[1]) - r,
        Math.max(s.a[0], s.b[0]) + r,
        Math.max(s.a[1], s.b[1]) + r,
      ];
    }
    case "poly": {
      let x0 = Infinity;
      let y0 = Infinity;
      let x1 = -Infinity;
      let y1 = -Infinity;
      for (const [x, y] of s.pts) {
        x0 = Math.min(x0, x);
        y0 = Math.min(y0, y);
        x1 = Math.max(x1, x);
        y1 = Math.max(y1, y);
      }
      return [x0, y0, x1, y1];
    }
    case "blend": {
      const grow = s.k / 4 + s.wobble;
      let x0 = Infinity;
      let y0 = Infinity;
      let x1 = -Infinity;
      let y1 = -Infinity;
      for (const c of s.shapes) {
        const b = bounds(c);
        x0 = Math.min(x0, b[0]);
        y0 = Math.min(y0, b[1]);
        x1 = Math.max(x1, b[2]);
        y1 = Math.max(y1, b[3]);
      }
      return [x0 - grow, y0 - grow, x1 + grow, y1 + grow];
    }
  }
};

const ellipseLocal = (
  s: Extract<Shape, { kind: "ellipse" }>,
  x: number,
  y: number,
) => {
  const cos = Math.cos(s.rot);
  const sin = Math.sin(s.rot);
  const dx = x - s.cx;
  const dy = y - s.cy;
  return {
    u: (dx * cos + dy * sin) / s.rx,
    v: (-dx * sin + dy * cos) / s.ry,
    cos,
    sin,
  };
};

const capsuleLocal = (
  s: Extract<Shape, { kind: "capsule" }>,
  x: number,
  y: number,
) => {
  const abx = s.b[0] - s.a[0];
  const aby = s.b[1] - s.a[1];
  const len2 = abx * abx + aby * aby || 1e-9;
  const t = clamp(((x - s.a[0]) * abx + (y - s.a[1]) * aby) / len2, 0, 1);
  const dx = x - (s.a[0] + abx * t);
  const dy = y - (s.a[1] + aby * t);
  return { dx, dy, d: Math.hypot(dx, dy), r: s.ra + (s.rb - s.ra) * t };
};

const insidePoly = (pts: readonly Vec2[], x: number, y: number): boolean => {
  let inside = false;
  for (let i = 0, j = pts.length - 1; i < pts.length; j = i++) {
    const [xi, yi] = pts[i];
    const [xj, yj] = pts[j];
    if (yi > y !== yj > y && x < ((xj - xi) * (y - yi)) / (yj - yi) + xi) {
      inside = !inside;
    }
  }
  return inside;
};

export const covers = (s: Shape, x: number, y: number): boolean => {
  switch (s.kind) {
    case "ellipse": {
      const { u, v } = ellipseLocal(s, x, y);
      return u * u + v * v <= 1;
    }
    case "capsule": {
      const { d, r } = capsuleLocal(s, x, y);
      return d <= r;
    }
    case "poly":
      return insidePoly(s.pts, x, y);
    case "blend":
      return sdf(s, x, y) < 0;
  }
};

// Polynomial smooth minimum: joins two distance fields with a fillet.
const smin = (a: number, b: number, k: number): number => {
  const h = Math.max(k - Math.abs(a - b), 0) / k;
  return Math.min(a, b) - h * h * k * 0.25;
};

const hash = (x: number, y: number, seed: number): number => {
  let h =
    Math.imul(x | 0, 374761393) ^
    Math.imul(y | 0, 668265263) ^
    Math.imul(seed | 0, 1442695041);
  h = Math.imul(h ^ (h >>> 13), 1274126177);
  return ((h ^ (h >>> 16)) >>> 0) / 4294967295;
};

// Smooth value noise between -1 and 1, fixed by its seed.
export const noise = (x: number, y: number, seed: number): number => {
  const xi = Math.floor(x);
  const yi = Math.floor(y);
  const fx = x - xi;
  const fy = y - yi;
  const sx = fx * fx * (3 - 2 * fx);
  const sy = fy * fy * (3 - 2 * fy);
  const a = hash(xi, yi, seed);
  const b = hash(xi + 1, yi, seed);
  const c = hash(xi, yi + 1, seed);
  const d = hash(xi + 1, yi + 1, seed);
  return 2 * (a + (b - a) * sx + (c - a) * sy + (a - b - c + d) * sx * sy) - 1;
};

// Signed distance to the outline: negative inside, in world units.
export const sdf = (s: Shape, x: number, y: number): number => {
  switch (s.kind) {
    case "ellipse": {
      const { u, v } = ellipseLocal(s, x, y);
      const k0 = Math.hypot(u, v);
      const k1 = Math.hypot(u / s.rx, v / s.ry);
      return k1 < 1e-9 ? -Math.min(s.rx, s.ry) : (k0 * (k0 - 1)) / k1;
    }
    case "capsule": {
      const { d, r } = capsuleLocal(s, x, y);
      return d - r;
    }
    case "poly": {
      let best = Infinity;
      const pts = s.pts;
      for (let i = 0, j = pts.length - 1; i < pts.length; j = i++) {
        const [ax, ay] = pts[j];
        const [bx, by] = pts[i];
        const ex = bx - ax;
        const ey = by - ay;
        const len2 = ex * ex + ey * ey || 1e-9;
        const t = clamp(((x - ax) * ex + (y - ay) * ey) / len2, 0, 1);
        best = Math.min(best, Math.hypot(x - ax - ex * t, y - ay - ey * t));
      }
      return insidePoly(pts, x, y) ? -best : best;
    }
    case "blend": {
      let d = sdf(s.shapes[0], x, y);
      for (let i = 1; i < s.shapes.length; i++) {
        d = smin(d, sdf(s.shapes[i], x, y), s.k);
      }
      return s.wobble ? d + s.wobble * noise(x * 0.4, y * 0.4, s.seed) : d;
    }
  }
};

// A surface inflated from the outline: rising over `radius` from the edge,
// flat beyond it. Joins in a blend shade as one continuous surface.
const inflateNormal = (
  s: Shape,
  x: number,
  y: number,
  radius: number,
): Vec3 => {
  const e = 0.35;
  const inside = -sdf(s, x, y);
  if (inside >= radius) return [0, 0, 1];
  const gx = (sdf(s, x + e, y) - sdf(s, x - e, y)) / (2 * e);
  const gy = (sdf(s, x, y + e) - sdf(s, x, y - e)) / (2 * e);
  const g = Math.hypot(gx, gy) || 1;
  const k = clamp((radius - inside) / radius, 0, 1);
  return [(gx / g) * k, (gy / g) * k, Math.sqrt(1 - k * k)];
};

// The outward-rounded surface normal at a point inside the shape: a dome for
// ellipses, a tube for capsules, and a bevelled edge `bevel` wide for polygons.
// Screen convention: +x right, +y down, +z toward the viewer.
export const roundNormal = (
  s: Shape,
  x: number,
  y: number,
  bevel: number,
): Vec3 => {
  switch (s.kind) {
    case "ellipse": {
      const { u, v, cos, sin } = ellipseLocal(s, x, y);
      const w = Math.sqrt(Math.max(0, 1 - u * u - v * v));
      return normalize([u * cos - v * sin, u * sin + v * cos, w]);
    }
    case "capsule": {
      const { dx, dy, d, r } = capsuleLocal(s, x, y);
      if (d < 1e-6) return [0, 0, 1];
      const k = Math.min(1, d / r);
      return [(dx / d) * k, (dy / d) * k, Math.sqrt(1 - k * k)];
    }
    case "poly": {
      let best = Infinity;
      let gx = 0;
      let gy = 0;
      const pts = s.pts;
      for (let i = 0, j = pts.length - 1; i < pts.length; j = i++) {
        const [ax, ay] = pts[j];
        const [bx, by] = pts[i];
        const ex = bx - ax;
        const ey = by - ay;
        const len2 = ex * ex + ey * ey || 1e-9;
        const t = clamp(((x - ax) * ex + (y - ay) * ey) / len2, 0, 1);
        const qx = ax + ex * t;
        const qy = ay + ey * t;
        const d = Math.hypot(x - qx, y - qy);
        if (d < best) {
          best = d;
          gx = x - qx;
          gy = y - qy;
        }
      }
      if (best >= bevel || best < 1e-6) return [0, 0, 1];
      const k = (bevel - best) / bevel;
      return [(-gx / best) * k, (-gy / best) * k, Math.sqrt(1 - k * k)];
    }
    case "blend":
      return inflateNormal(s, x, y, bevel);
  }
};

export const normalize = (v: Vec3): Vec3 => {
  const l = Math.hypot(v[0], v[1], v[2]) || 1;
  return [v[0] / l, v[1] / l, v[2] / l];
};

export const mirror = (s: Shape, axis: number): Shape => {
  const fx = (x: number) => 2 * axis - x;
  switch (s.kind) {
    case "ellipse":
      return { ...s, cx: fx(s.cx), rot: -s.rot };
    case "capsule":
      return { ...s, a: [fx(s.a[0]), s.a[1]], b: [fx(s.b[0]), s.b[1]] };
    case "poly":
      return { ...s, pts: s.pts.map(([x, y]) => [fx(x), y] as const) };
    case "blend":
      return { ...s, shapes: s.shapes.map((c) => mirror(c, axis)) };
  }
};
