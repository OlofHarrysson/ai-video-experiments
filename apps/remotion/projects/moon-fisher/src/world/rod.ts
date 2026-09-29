import { C } from "../pixel/palette";
import { Pix } from "../pixel/pix";
import type { Vec2 } from "../pixel/shapes";

export type RodProps = {
  // Where the hand grips the rod, in world units.
  grip: Vec2;
  // Direction of the rod in degrees: 0 right, -90 up.
  angle: number;
  length: number;
  // How far the tip is pulled down by the line, in world units.
  bend: number;
};

const curve = (a: Vec2, c: Vec2, b: Vec2, n: number): Vec2[] =>
  Array.from({ length: n + 1 }, (_, i) => {
    const t = i / n;
    const u = 1 - t;
    return [
      u * u * a[0] + 2 * u * t * c[0] + t * t * b[0],
      u * u * a[1] + 2 * u * t * c[1] + t * t * b[1],
    ] as const;
  });

const polyline = (pix: Pix, pts: Vec2[], c: number): void => {
  for (let i = 0; i < pts.length - 1; i++) {
    pix.line(pts[i][0], pts[i][1], pts[i + 1][0], pts[i + 1][1], c);
  }
};

// A bamboo rod, a little past the hand behind and bending toward its line.
// Returns the tip.
export const drawRod = (
  pix: Pix,
  { grip, angle, length, bend }: RodProps,
): Vec2 => {
  const a = (angle * Math.PI) / 180;
  const [dx, dy] = [Math.cos(a), Math.sin(a)];
  const butt: Vec2 = [grip[0] - dx * 7, grip[1] - dy * 7];
  const straight: Vec2 = [grip[0] + dx * length, grip[1] + dy * length];
  const tip: Vec2 = [straight[0], straight[1] + bend];
  const mid: Vec2 = [
    grip[0] + dx * length * 0.55,
    grip[1] + dy * length * 0.55,
  ];
  polyline(pix, curve(butt, mid, tip, 16), C.umber2);
  return tip;
};

// A fishing line from the rod tip to the water, sagging by `slack`.
export const drawLine = (
  pix: Pix,
  from: Vec2,
  to: Vec2,
  slack: number,
): void => {
  const mid: Vec2 = [(from[0] + to[0]) / 2, (from[1] + to[1]) / 2 + slack];
  polyline(pix, curve(from, mid, to, 16), C.night6);
};
