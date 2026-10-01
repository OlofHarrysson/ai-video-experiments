import { random } from "remotion";
import { C } from "../pixel/palette";
import { Pix } from "../pixel/pix";
import { fillBands, type Band } from "./sky";

export type SeaProps = {
  horizon: number;
  bands: readonly Band[];
  seam: number;
  seed: string;
  // 0 is a flat, glassy sea; 1 a gentle swell.
  swell: number;
  // Animation step: each row of swell sways slowly from side to side.
  step?: number;
};

// The sea from the horizon down: darker toward the viewer, crossed by thin
// swell lines that grow longer and farther apart as they come closer.
export const drawSea = (
  pix: Pix,
  { horizon, bands, seam, seed, swell, step = 0 }: SeaProps,
): void => {
  fillBands(pix, horizon, 480, bands, seam);
  const hy = Math.floor(horizon * pix.k);
  // A lighter line where sea meets sky keeps the horizon readable.
  for (let px = 0; px < pix.w; px++) pix.brighten(px, hy, 1);
  if (swell <= 0) return;
  let row = 0;
  for (let y = horizon + 2; y < 480; row++) {
    const depth = (y - horizon) / (480 - horizon);
    const py = Math.floor(y * pix.k);
    const dash = 2 + depth * 14;
    const sway = (1 + 2 * depth) * Math.sin(step * 0.07 + row * 1.9);
    for (let x = random(`${seed}-o-${row}`) * 20 - 20; x < 270; ) {
      const len = dash * (0.5 + random(`${seed}-l-${row}-${x.toFixed(1)}`));
      const gap = dash * (1.5 + 3 * random(`${seed}-g-${row}-${x.toFixed(1)}`));
      if (random(`${seed}-s-${row}-${x.toFixed(1)}`) < swell) {
        const up = random(`${seed}-u-${row}-${x.toFixed(1)}`) < 0.5;
        for (
          let p = Math.floor((x + sway) * pix.k);
          p < Math.floor((x + len + sway) * pix.k);
          p++
        ) {
          if (up) pix.brighten(p, py, 1);
          else pix.darken(p, py, 1);
        }
      }
      x += len + gap;
    }
    y += 2 + depth * 10;
  }
};

export type MoonPathProps = {
  // Column of the moon, in design-frame units.
  x: number;
  horizon: number;
  halfWidth: number;
  seed: string;
  // Animation step: the glints shift as it advances.
  step?: number;
};

// The moon's glitter on a gently moving sea: short bright dashes in a column
// below the moon, narrow at the horizon and widening toward the viewer.
export const drawMoonPath = (
  pix: Pix,
  { x, horizon, halfWidth, seed, step = 0 }: MoonPathProps,
): void => {
  const hy = Math.floor(horizon * pix.k) + 1;
  for (let py = hy; py < pix.h; py++) {
    const t = (py - hy) / (pix.h - hy);
    const half = halfWidth * (0.3 + 0.7 * t);
    const dashes = 3 + Math.floor(6 * t);
    for (let i = 0; i < dashes; i++) {
      const key = `${seed}-${py}-${i}-${Math.floor((step + i) / 2)}`;
      const off = (random(`${key}-a`) + random(`${key}-b`) - 1) * half;
      const g = 1 - Math.abs(off) / half;
      if (random(`${key}-s`) > 0.3 + 0.55 * g) continue;
      const len = 2 + random(`${key}-l`) * (3 + 9 * t);
      const steps = Math.max(1, Math.round(1 + 2 * g));
      const from = Math.floor((x + off - len / 2) * pix.k);
      const to = Math.floor((x + off + len / 2) * pix.k);
      for (let px = from; px <= to; px++) pix.brighten(px, py, steps);
    }
  }
};

export type MoonReflectionProps = {
  // Center and radius, in world units.
  x: number;
  y: number;
  r: number;
  seed: string;
  step?: number;
  // 0 on calm water, up to 1 when a ripple or a tug shakes it.
  wobble?: number;
};

// The moon mirrored in still water: a slightly flattened disc cut into
// ripples that slide sideways as the water moves.
export const drawMoonReflection = (
  pix: Pix,
  { x, y, r, seed, step = 0, wobble = 0 }: MoonReflectionProps,
): void => {
  const ry = r * 0.75;
  const ripple = Math.max(2, Math.round(1.5 * pix.s));
  for (let py = pix.py(y - ry); py <= pix.py(y + ry); py++) {
    const v = (pix.wy(py) - y) / ry;
    if (Math.abs(v) >= 1) continue;
    const band = Math.floor(py / ripple);
    if (
      py % ripple === ripple - 1 &&
      random(`${seed}-gap-${band}-${Math.floor(step / 3)}`) <
        0.35 + 0.3 * wobble
    )
      continue;
    const half = r * Math.sqrt(1 - v * v);
    const shift = Math.round(
      Math.sin(band * 1.7 + step * 0.6) * 0.9 * (1 + 2.5 * wobble) * pix.s,
    );
    for (let px = pix.px(x - half); px <= pix.px(x + half); px++) {
      const u = (pix.wx(px) - x) / half;
      pix.set(px + shift, py, Math.abs(u) > 0.8 ? C.silver1 : C.silver3);
    }
  }
};

export type RippleProps = {
  // Center and radius of the outermost ring, in world units.
  x: number;
  y: number;
  radius: number;
  seed: string;
};

// Rings spreading over still water from something bobbing in it, flattened
// by perspective and broken in places. The newest, innermost ring is the
// brightest.
export const drawRipple = (
  pix: Pix,
  { x, y, radius, seed }: RippleProps,
): void => {
  for (let ring = 0; ring < 3; ring++) {
    const r = radius - ring * 5;
    if (r <= 1) break;
    const lit = new Set<number>();
    const n = Math.max(24, Math.round(4 * Math.PI * r * pix.s));
    for (let i = 0; i < n; i++) {
      if (random(`${seed}-${ring}-${Math.floor((i * 14) / n)}`) < 0.25)
        continue;
      const a = (2 * Math.PI * i) / n;
      const px = pix.px(x + Math.cos(a) * r);
      const py = pix.py(y + Math.sin(a) * r * 0.3);
      if (lit.has(py * pix.w + px)) continue;
      lit.add(py * pix.w + px);
      pix.brighten(px, py, ring === 0 ? 2 : 3);
    }
  }
};
