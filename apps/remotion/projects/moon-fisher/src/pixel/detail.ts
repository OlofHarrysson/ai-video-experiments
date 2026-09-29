import { Pix } from "./pix";
import type { Vec2 } from "./shapes";

// A detail line over finished shading, such as a fold, seam or hair strand.
// Negative steps darken what is already there and positive steps brighten it,
// so details follow the light. Strokes only touch drawn objects.
export type Stroke = { pts: readonly Vec2[]; steps: number };

export const drawStrokes = (pix: Pix, strokes: readonly Stroke[]): void => {
  for (const s of strokes) {
    const done = new Set<number>();
    const apply = (px: number, py: number) => {
      const key = py * pix.w + px;
      if (done.has(key) || !pix.isSolid(px, py)) return;
      done.add(key);
      if (s.steps < 0) pix.darken(px, py, -s.steps);
      else pix.brighten(px, py, s.steps);
    };
    if (s.pts.length === 1) {
      apply(pix.px(s.pts[0][0]), pix.py(s.pts[0][1]));
      continue;
    }
    for (let i = 0; i < s.pts.length - 1; i++) {
      const [a, b] = [s.pts[i], s.pts[i + 1]];
      pix.trace(a[0], a[1], b[0], b[1], apply);
    }
  }
};

export const flipStrokes = (
  strokes: readonly Stroke[],
  axis: number,
): Stroke[] =>
  strokes.map((s) => ({
    ...s,
    pts: s.pts.map(([x, y]) => [2 * axis - x, y] as const),
  }));
