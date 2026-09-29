import { random } from "remotion";
import { Pix, quantize } from "../pixel/pix";

// Light in the air brightens whatever is already drawn by climbing the
// palette ladder, so glows stay inside the palette and dither naturally.
// Positions and sizes are in world units.

export type HaloProps = { x: number; y: number; radius: number; steps: number };

export const drawHalo = (
  pix: Pix,
  { x, y, radius, steps }: HaloProps,
): void => {
  for (let py = pix.py(y - radius); py <= pix.py(y + radius); py++) {
    for (let px = pix.px(x - radius); px <= pix.px(x + radius); px++) {
      const d = Math.hypot(pix.wx(px) - x, pix.wy(py) - y) / radius;
      if (d >= 1) continue;
      const g = Math.pow(1 - d, 1.8);
      pix.brighten(px, py, Math.max(0, quantize(g * steps, px, py, 1)));
    }
  }
};

export type ShaftProps = {
  x: number;
  y: number;
  // Half-width gained per unit of height.
  spread: number;
  length: number;
  steps: number;
};

// A cone of light rising from an opening, as if through a thin sea mist.
export const drawShaft = (
  pix: Pix,
  { x, y, spread, length, steps }: ShaftProps,
): void => {
  for (let py = pix.py(y - length); py < pix.py(y); py++) {
    const h = y - pix.wy(py);
    const half = 4 + h * spread;
    const along = h / length;
    for (let px = pix.px(x - half); px <= pix.px(x + half); px++) {
      const across = Math.abs(pix.wx(px) - x) / half;
      if (across >= 1) continue;
      const g = Math.pow(1 - along, 1.6) * (1 - across * across);
      pix.brighten(px, py, Math.max(0, quantize(g * steps, px, py, 1)));
    }
  }
};

export type WaterProps = {
  // World height of the water surface below the objects.
  waterline: number;
  seed: string;
  // Animation step: ripples drift and re-break as it advances.
  step?: number;
};

// Still water mirrors what floats on it. Each row below the waterline shows
// the matching row above it, a step or two darker and nudged sideways by
// ripples; thin gaps between ripples let the sea show through.
export const reflectWater = (
  pix: Pix,
  { waterline, seed, step = 0 }: WaterProps,
): void => {
  const wl = pix.py(waterline);
  // Ripples are about two world units tall at any pixel density.
  const ripple = Math.max(2, Math.round(2 * pix.s));
  const phase = random(`${seed}-phase`) * 6;
  for (let py = wl; py < pix.h; py++) {
    const d = py - wl;
    const src = wl - 1 - d;
    if (src < 0) break;
    const band = Math.floor(d / ripple);
    const far = d / (pix.h - wl);
    const gap =
      random(`${seed}-gap-${band}-${Math.floor((step + band) / 4)}`) <
      0.1 + 0.45 * far;
    if (gap && d % ripple === ripple - 1) continue;
    const shift = Math.round(
      Math.sin(band * 1.3 + phase + step * 0.45) * (0.4 + 3 * far) * pix.s,
    );
    const steps = far < 0.35 ? 1 : 2;
    for (let px = 0; px < pix.w; px++) {
      const sx = px + shift;
      if (!pix.isSolid(sx, src)) continue;
      pix.set(px, py, pix.get(sx, src));
      pix.darken(px, py, steps);
    }
  }
};
