import { random } from "remotion";
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
