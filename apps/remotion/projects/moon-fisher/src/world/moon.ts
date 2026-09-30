import type { Part } from "../pixel/lit";
import { covers, ellipse, poly, type Shape } from "../pixel/shapes";

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
// its edge, with a few gray seas, all dimmed by `glow`. It shades from its
// own sphere, so a moon cut off by the water still looks round. Returns a
// ramp position from 0 to 1.
const moonFace =
  (cx: number, cy: number, r: number, glow: number) =>
  (x: number, y: number): number => {
    const u = (x - cx) / r;
    const v = (y - cy) / r;
    const nz = Math.sqrt(Math.max(0, 1 - u * u - v * v));
    let t = 1 - 0.55 * (1 - nz) ** 2;
    for (const [shape, depth] of MARIA) if (covers(shape, u, v)) t -= depth;
    return t * (0.35 + 0.65 * glow);
  };

export type MoonProps = {
  x: number;
  y: number;
  radius: number;
  // How brightly it shines, 0 to 1.
  glow?: number;
  // A water surface: the part of the moon below it is under the sea.
  waterline?: number;
};

export const moonParts = ({
  x,
  y,
  radius,
  glow = 1,
  waterline,
}: MoonProps): Part[] => {
  let shape: Shape = ellipse(x, y, radius);
  if (waterline !== undefined && waterline < y + radius) {
    // The visible cap: the circle above the waterline, closed by the water.
    const pts: [number, number][] = [];
    for (let i = 0; i <= 32; i++) {
      const a = Math.PI + (Math.PI * i) / 32;
      const py = y + radius * Math.sin(a);
      if (py <= waterline) pts.push([x + radius * Math.cos(a), py]);
    }
    const half = Math.sqrt(Math.max(0, radius * radius - (waterline - y) ** 2));
    pts.unshift([x - half, waterline]);
    pts.push([x + half, waterline]);
    shape = poly(pts);
  }
  return [{ shape, mat: "moon", emit: moonFace(x, y, radius, glow) }];
};
