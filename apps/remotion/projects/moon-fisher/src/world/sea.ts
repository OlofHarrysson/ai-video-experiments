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
};

// The sea from the horizon down: darker toward the viewer, crossed by thin
// swell lines that grow longer and farther apart as they come closer.
export const drawSea = (
  pix: Pix,
  { horizon, bands, seam, seed, swell }: SeaProps,
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
    for (let x = random(`${seed}-o-${row}`) * 20 - 20; x < 270; ) {
      const len = dash * (0.5 + random(`${seed}-l-${row}-${x.toFixed(1)}`));
      const gap = dash * (1.5 + 3 * random(`${seed}-g-${row}-${x.toFixed(1)}`));
      if (random(`${seed}-s-${row}-${x.toFixed(1)}`) < swell) {
        const up = random(`${seed}-u-${row}-${x.toFixed(1)}`) < 0.5;
        for (
          let p = Math.floor(x * pix.k);
          p < Math.floor((x + len) * pix.k);
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
  // Center and radius, in design-frame units.
  x: number;
  y: number;
  r: number;
  seed: string;
  step?: number;
};

// The moon mirrored in still water: a slightly flattened disc cut into
// ripples that slide sideways as the water moves.
export const drawMoonReflection = (
  pix: Pix,
  { x, y, r, seed, step = 0 }: MoonReflectionProps,
): void => {
  const ry = r * 0.75;
  for (let py = Math.floor((y - ry) * pix.k); py <= (y + ry) * pix.k; py++) {
    const v = ((py + 0.5) / pix.k - y) / ry;
    if (Math.abs(v) >= 1) continue;
    const band = Math.floor(py / 2);
    if (random(`${seed}-gap-${band}-${Math.floor(step / 3)}`) < 0.2) continue;
    const half = r * Math.sqrt(1 - v * v);
    const shift = Math.round(Math.sin(band * 1.7 + step * 0.6) * 1.3 * pix.k);
    for (
      let px = Math.floor((x - half) * pix.k);
      px <= (x + half) * pix.k;
      px++
    ) {
      const u = ((px + 0.5) / pix.k - x) / half;
      pix.set(px + shift, py, Math.abs(u) > 0.8 ? C.silver1 : C.silver3);
    }
  }
};
