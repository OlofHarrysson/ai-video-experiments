import { random } from "remotion";
import { C } from "../pixel/palette";
import { bayer, Pix, quantize, smoothstep } from "../pixel/pix";
import { noise } from "../pixel/shapes";

// A color and the height where it is purest: 0 at the top of the region,
// 1 at its bottom.
export type Band = readonly [color: number, at: number];

// Solid bands of color joined by short ordered-dither seams. `seam` is the
// share of each interval given to the seam. `cover` below 1 lays the bands
// over what is there through an ordered-dither mask, so one sky can dissolve
// into another.
export const fillBands = (
  pix: Pix,
  top: number,
  bottom: number,
  bands: readonly Band[],
  seam: number,
  cover = 1,
): void => {
  const y0 = Math.max(0, Math.floor(top * pix.k));
  const y1 = Math.min(pix.h, Math.floor(bottom * pix.k));
  for (let py = y0; py < y1; py++) {
    const t = (py + 0.5 - y0) / (y1 - y0);
    let a = bands[0];
    let b = bands[bands.length - 1];
    if (t <= a[1]) b = a;
    for (let i = 0; i < bands.length - 1; i++) {
      if (t >= bands[i][1] && t < bands[i + 1][1]) {
        a = bands[i];
        b = bands[i + 1];
        break;
      }
    }
    const f = b === a ? 0 : (t - a[1]) / (b[1] - a[1]);
    const m = smoothstep(0.5 - seam / 2, 0.5 + seam / 2, f);
    for (let px = 0; px < pix.w; px++) {
      if (cover < 1 && bayer(px, py) >= cover) continue;
      pix.set(px, py, m > bayer(px, py) ? b[0] : a[0]);
    }
  }
};

export type SkyProps = {
  horizon: number;
  // The moonless sky, and the moonlit one dissolved over it by `moonlight`
  // from 0 to 1.
  dark: readonly Band[];
  lit: readonly Band[];
  moonlight: number;
  seam: number;
};

export const drawSky = (
  pix: Pix,
  { horizon, dark, lit, moonlight, seam }: SkyProps,
): void => {
  fillBands(pix, 0, horizon, dark, seam);
  if (moonlight > 0) fillBands(pix, 0, horizon, lit, seam, moonlight);
};

export type StarsProps = {
  seed: string;
  count: number;
  horizon: number;
  // 0 hides the stars, 1 shows them at full strength.
  strength: number;
  // Animation step: some stars dim for a moment as they twinkle.
  step?: number;
};

// Scattered stars, fewer and dimmer toward the horizon. The brightest few
// get a small cross.
export const drawStars = (
  pix: Pix,
  { seed, count, horizon, strength, step = 0 }: StarsProps,
): void => {
  for (let i = 0; i < count; i++) {
    const x = random(`${seed}-x-${i}`) * 270;
    const y = Math.pow(random(`${seed}-y-${i}`), 1.4) * (horizon - 8);
    const haze = 1 - 0.6 * (y / horizon);
    const twinkle = random(`${seed}-t-${i}-${step}`) < 0.12 ? 0.75 : 1;
    const b = random(`${seed}-b-${i}`) * haze * strength * twinkle;
    if (b < 0.25) continue;
    const c =
      b > 0.93
        ? C.silver3
        : b > 0.8
          ? C.silver1
          : b > 0.55
            ? C.night6
            : C.night5;
    const px = Math.floor(x * pix.k);
    const py = Math.floor(y * pix.k);
    pix.set(px, py, c);
    if (b > 0.95) {
      for (const [dx, dy] of [
        [1, 0],
        [-1, 0],
        [0, 1],
        [0, -1],
      ]) {
        pix.set(px + dx, py + dy, C.night6);
      }
    }
  }
};

export type MilkyWayProps = {
  seed: number;
  horizon: number;
  // 0 hides the band; 1 shows it at full strength.
  strength: number;
};

// A faint river of stars across the sky, which only shows once the moon is
// gone. It runs from upper left to lower right, clumpy and fading toward the
// horizon.
export const drawMilkyWay = (
  pix: Pix,
  { seed, horizon, strength }: MilkyWayProps,
): void => {
  const [ax, ay, bx, by] = [-20, 10, 290, 190];
  const len = Math.hypot(bx - ax, by - ay);
  const [ux, uy] = [(bx - ax) / len, (by - ay) / len];
  const density = (x: number, y: number) => {
    const along = (x - ax) * ux + (y - ay) * uy;
    const across = -(x - ax) * uy + (y - ay) * ux;
    const drift = 12 * noise(along * 0.015, 0.5, seed);
    const band = Math.exp(-2 * ((across + drift) / 34) ** 2);
    const clump = 0.5 + 0.5 * noise(x * 0.06, y * 0.06, seed + 1);
    return band * clump * (1 - 0.7 * (y / horizon)) * strength;
  };
  for (let py = 0; py < Math.floor(horizon * pix.k); py++) {
    for (let px = 0; px < pix.w; px++) {
      const g = density((px + 0.5) / pix.k, (py + 0.5) / pix.k);
      pix.brighten(px, py, Math.max(0, quantize(g * 0.9, px, py, 1)));
    }
  }
  for (let i = 0; i < 220; i++) {
    const x = random(`mw-${seed}-x-${i}`) * 270;
    const y = random(`mw-${seed}-y-${i}`) * (horizon - 10);
    const g = density(x, y);
    if (random(`mw-${seed}-k-${i}`) > g) continue;
    const c = random(`mw-${seed}-c-${i}`) < 0.3 ? C.silver1 : C.night6;
    pix.set(Math.floor(x * pix.k), Math.floor(y * pix.k), c);
  }
};
