import type { Part } from "../pixel/lit";
import { covers, ellipse, poly, type Shape, type Vec3 } from "../pixel/shapes";

// Dark seas on the moon's face, as outlines in units of its radius, with how
// much each one dims the surface. One ragged, connected band and a few
// scattered patches, so the face never reads as eyes and a mouth.
const MARIA: readonly [Shape, number][] = [
  [
    poly([
      [-0.82, 0.05],
      [-0.7, -0.3],
      [-0.52, -0.42],
      [-0.3, -0.62],
      [-0.08, -0.55],
      [0.12, -0.62],
      [0.36, -0.52],
      [0.5, -0.3],
      [0.42, -0.12],
      [0.2, -0.18],
      [0.02, -0.3],
      [-0.18, -0.26],
      [-0.34, -0.1],
      [-0.46, 0.14],
      [-0.66, 0.3],
    ]),
    0.55,
  ],
  [ellipse(0.66, -0.12, 0.14, 0.11), 0.55],
  [ellipse(0.3, 0.3, 0.2, 0.12, 0.4), 0.45],
  [ellipse(-0.18, 0.42, 0.16, 0.1), 0.45],
];

// The moon glows by itself: brightest in the middle, a little darker toward
// its edge, with a few gray seas. Returns a ramp position from 0 to 1.
const moonFace =
  (cx: number, cy: number, r: number) =>
  (x: number, y: number, n: Vec3): number => {
    const u = (x - cx) / r;
    const v = (y - cy) / r;
    let t = 1 - 0.55 * (1 - n[2]) ** 2;
    for (const [shape, depth] of MARIA) if (covers(shape, u, v)) t -= depth;
    return t;
  };

export type MoonProps = { x: number; y: number; radius: number };

export const moonParts = ({ x, y, radius }: MoonProps): Part[] => [
  {
    shape: ellipse(x, y, radius),
    mat: "moon",
    emit: moonFace(x, y, radius),
  },
];
