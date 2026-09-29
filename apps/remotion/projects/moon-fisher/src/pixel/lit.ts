import { RAMPS, type Material } from "./palette";
import { clamp, Pix, quantize, smoothstep } from "./pix";
import {
  bounds,
  covers,
  mirror,
  normalize,
  roundNormal,
  type Shape,
  type Vec3,
} from "./shapes";

export type Light =
  | { kind: "dir"; dir: Vec3; strength: number; wrap?: number }
  | {
      kind: "point";
      x: number;
      y: number;
      z: number;
      strength: number;
      radius: number;
      falloff?: number;
      wrap?: number;
      // Light leaves through an opening that faces up, like a bucket's:
      // points below this elevation (sine of the angle) stay dark.
      minElev?: number;
      soft?: number;
    };

// One piece of a drawn object. Later parts sit in front of earlier ones.
export type Part = {
  shape: Shape;
  mat: Material;
  // A fixed normal instead of a rounded surface.
  flat?: Vec3;
  // Width of the rounded edge on polygons, in world units.
  bevel?: number;
  // Shade as an upright cylinder around x = cx with radius rx.
  cylinder?: { cx: number; rx: number };
  // Depth toward the viewer, in design units.
  z?: number;
  // Darkens the parts behind it along its edge.
  shadow?: boolean;
  // Self-lit parts return a ramp position from 0 to 1 instead of being lit.
  emit?: (x: number, y: number, n: Vec3) => number;
  // Brightness added to the light this part receives.
  lift?: number;
};

export type LitScene = { lights: readonly Light[]; ambient: number };

export type LitStyle = {
  // 0 draws clean bands; higher values mix neighboring steps.
  dither: number;
  // Darken the silhouette edge by one step (selective outline).
  outline: boolean;
  // Remove single pixels that differ from all four neighbors.
  cleanup: boolean;
};

const SURFACE_DEPTH = 4;

const cylinderNormal = (c: { cx: number; rx: number }, x: number): Vec3 => {
  const u = clamp((x - c.cx) / c.rx, -1, 1);
  return [u, 0, Math.sqrt(1 - u * u)];
};

export const lightAt = (
  scene: LitScene,
  x: number,
  y: number,
  z: number,
  n: Vec3,
): number => {
  let total = scene.ambient;
  for (const light of scene.lights) {
    const wrap = light.wrap ?? 0;
    if (light.kind === "dir") {
      const [dx, dy, dz] = normalize(light.dir);
      const d = n[0] * dx + n[1] * dy + n[2] * dz;
      total += light.strength * Math.max(0, (d + wrap) / (1 + wrap));
      continue;
    }
    const lx = light.x - x;
    const ly = light.y - y;
    const lz = light.z - z;
    const dist = Math.hypot(lx, ly, lz) || 1e-6;
    const d = (n[0] * lx + n[1] * ly + n[2] * lz) / dist;
    const lambert = Math.max(0, (d + wrap) / (1 + wrap));
    const fall = Math.pow(
      clamp(1 - dist / light.radius, 0, 1),
      light.falloff ?? 1,
    );
    let visible = 1;
    if (light.minElev !== undefined) {
      const soft = light.soft ?? 0.1;
      visible = smoothstep(
        light.minElev - soft,
        light.minElev + soft,
        (light.y - y) / dist,
      );
    }
    total += light.strength * lambert * fall * visible;
  }
  return total;
};

// Draw an object made of parts, lit by the scene and quantized onto each
// part's color ramp.
export const drawLit = (
  pix: Pix,
  parts: readonly Part[],
  scene: LitScene,
  style: LitStyle,
): void => {
  if (parts.length === 0) return;
  let bx0 = Infinity;
  let by0 = Infinity;
  let bx1 = -Infinity;
  let by1 = -Infinity;
  for (const p of parts) {
    const [x0, y0, x1, y1] = bounds(p.shape);
    bx0 = Math.min(bx0, pix.px(x0) - 1);
    by0 = Math.min(by0, pix.py(y0) - 1);
    bx1 = Math.max(bx1, pix.px(x1) + 1);
    by1 = Math.max(by1, pix.py(y1) + 1);
  }
  bx0 = Math.max(0, bx0);
  by0 = Math.max(0, by0);
  bx1 = Math.min(pix.w - 1, bx1);
  by1 = Math.min(pix.h - 1, by1);
  const W = bx1 - bx0 + 1;
  const H = by1 - by0 + 1;
  if (W <= 0 || H <= 0) return;

  const owner = new Int16Array(W * H).fill(-1);
  const level = new Int8Array(W * H);

  for (let j = 0; j < H; j++) {
    for (let i = 0; i < W; i++) {
      const px = bx0 + i;
      const py = by0 + j;
      const x = pix.wx(px);
      const y = pix.wy(py);
      for (let pi = parts.length - 1; pi >= 0; pi--) {
        const p = parts[pi];
        if (!covers(p.shape, x, y)) continue;
        const steps = RAMPS[p.mat].length - 1;
        const n = p.flat
          ? normalize(p.flat)
          : p.cylinder
            ? cylinderNormal(p.cylinder, x)
            : roundNormal(p.shape, x, y, p.bevel ?? 3);
        const t = p.emit
          ? p.emit(x, y, n)
          : lightAt(scene, x, y, (p.z ?? 0) + n[2] * SURFACE_DEPTH, n) +
            (p.lift ?? 0);
        const dither = p.emit ? 0 : style.dither;
        level[j * W + i] = clamp(
          quantize(clamp(t, 0, 1) * steps, px, py, dither),
          0,
          steps,
        );
        owner[j * W + i] = pi;
        break;
      }
    }
  }

  const at = (i: number, j: number) =>
    i < 0 || j < 0 || i >= W || j >= H ? -1 : owner[j * W + i];
  const lv = (i: number, j: number) => level[j * W + i];
  const N4 = [
    [1, 0],
    [-1, 0],
    [0, 1],
    [0, -1],
  ] as const;

  if (style.cleanup) {
    const fixed = level.slice();
    for (let j = 0; j < H; j++) {
      for (let i = 0; i < W; i++) {
        const o = owner[j * W + i];
        if (o < 0 || parts[o].emit) continue;
        let agree = -1;
        let ok = true;
        for (const [di, dj] of N4) {
          if (at(i + di, j + dj) !== o) {
            ok = false;
            break;
          }
          const l = lv(i + di, j + dj);
          if (agree === -1) agree = l;
          else if (agree !== l) {
            ok = false;
            break;
          }
        }
        if (ok && agree !== lv(i, j)) fixed[j * W + i] = agree;
      }
    }
    level.set(fixed);
  }

  const shaded = level.slice();
  for (let j = 0; j < H; j++) {
    for (let i = 0; i < W; i++) {
      const o = owner[j * W + i];
      if (o < 0 || parts[o].emit) continue;
      let edge = false;
      let shadowed = false;
      for (const [di, dj] of N4) {
        const n = at(i + di, j + dj);
        if (n < 0) edge = true;
        else if (n > o && parts[n].shadow) shadowed = true;
      }
      let l = level[j * W + i];
      if (shadowed) l -= 1;
      if (edge && style.outline) l = l <= 1 ? 0 : l - 1;
      shaded[j * W + i] = Math.max(0, l);
    }
  }

  for (let j = 0; j < H; j++) {
    for (let i = 0; i < W; i++) {
      const o = owner[j * W + i];
      if (o < 0) continue;
      pix.set(bx0 + i, by0 + j, RAMPS[parts[o].mat][shaded[j * W + i]]);
    }
  }
};

// Mirror an object's parts around a vertical axis, for facing left or right.
export const flipParts = (parts: readonly Part[], axis: number): Part[] =>
  parts.map((p) => {
    const flat = p.flat;
    return {
      ...p,
      shape: mirror(p.shape, axis),
      flat: flat ? ([-flat[0], flat[1], flat[2]] as const) : undefined,
    };
  });
