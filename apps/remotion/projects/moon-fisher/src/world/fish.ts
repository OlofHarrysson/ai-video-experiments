import { random } from "remotion";
import type { Stroke } from "../pixel/detail";
import type { Part } from "../pixel/lit";
import { C } from "../pixel/palette";
import { Pix } from "../pixel/pix";
import { blend, ellipse, poly, type Vec2 } from "../pixel/shapes";
import type { Feature } from "./fisherman";

export type FishProps = {
  // Center of the body, in world units.
  at: Vec2;
  // Heading in degrees: 0 swims right, -90 leaps straight up.
  angle: number;
  size?: number;
};

export type FishFigure = {
  body: Part[];
  // The gill line and a glint along the flank, over the shading.
  strokes: Stroke[];
  eye: Feature;
};

// A silver fish with a dark back: a tapering body, forked tail, dorsal and
// belly fins, a gill line and an eye. Points are given heading right, back
// up, and turned along the heading; a fish heading left is mirrored so its
// back stays up.
export const fish = ({
  at: [x, y],
  angle,
  size = 1,
}: FishProps): FishFigure => {
  const a = (angle * Math.PI) / 180;
  const [dx, dy] = [Math.cos(a), Math.sin(a)];
  const up = dx >= 0 ? 1 : -1;
  const place = ([u, v]: Vec2): Vec2 => [
    x + (dx * u - dy * v * up) * size,
    y + (dy * u + dx * v * up) * size,
  ];
  const oval = (u: number, v: number, ru: number, rv: number) => {
    const [px, py] = place([u, v]);
    return ellipse(px, py, ru * size, rv * size, a);
  };
  const tri = (pts: Vec2[]) => poly(pts.map(place));
  const body: Part[] = [
    {
      shape: tri([
        [-4.4, 0],
        [-7, -2.6],
        [-6.1, 0],
        [-7, 2.6],
      ]),
      mat: "fishBack",
      lift: 0.2,
    },
    {
      shape: tri([
        [-0.8, -1.6],
        [1.4, -1.8],
        [-2, -3.2],
      ]),
      mat: "fishBack",
      lift: 0.2,
    },
    {
      shape: tri([
        [-1.6, 1.4],
        [0.2, 1.5],
        [-2.3, 2.6],
      ]),
      mat: "tin",
      lift: 0.15,
    },
    {
      shape: blend(
        [oval(2.3, 0, 2.4, 1.6), oval(0, 0, 3.4, 1.9), oval(-3.4, 0, 1.7, 0.8)],
        1.2,
      ),
      mat: "tin",
      bevel: 1.2,
      lift: 0.35,
      // Countershading: dark along the back, silver below.
      marks: [{ shape: oval(-0.4, -1.3, 4.4, 1.1), mat: "fishBack" }],
    },
  ];
  const line = (pts: Vec2[]) => pts.map(place);
  const strokes: Stroke[] = [
    {
      pts: line([
        [2, -1.2],
        [1.5, 0],
        [2, 1.2],
      ]),
      steps: -1,
    },
    {
      pts: line([
        [-1.8, 0.3],
        [1, 0.2],
      ]),
      steps: 1,
    },
  ];
  const [ex, ey] = place([3.3, -0.4]);
  return { body, strokes, eye: { x: ex, y: ey, c: C.ink } };
};

export type SplashProps = {
  at: Vec2;
  size: number;
  // Seconds since it broke the surface.
  age: number;
  seed: string;
};

// Water thrown up where something breaks the surface: a white burst flashes
// at the water, jets of spray shoot up and collapse, droplets fly up and fall
// back, and a ring spreads and fades. Bigger splashes throw more water and
// last longer.
export const drawSplash = (
  pix: Pix,
  { at: [x, y], size, age, seed }: SplashProps,
): void => {
  const life = 0.35 + 0.06 * size;
  if (age < 0 || age > life) return;
  const done = age / life;
  if (age < 0.12) {
    // The burst: a bright mound of broken water.
    for (let i = 0; i < 30; i++) {
      const u = random(`${seed}-bx-${i}`) * 2 - 1;
      const h = random(`${seed}-by-${i}`) * (1 - u * u);
      pix.set(
        pix.px(x + u * size * 0.7),
        pix.py(y - h * size * 0.9),
        i % 3 ? C.silver4 : C.moon,
      );
    }
  }
  // Jets of spray fan up from the water, rise, and fall back into it.
  const jets = Math.round(3 + size / 3);
  const rise = Math.sin(Math.PI * Math.min(1, done * 1.4));
  for (let j = 0; j < jets; j++) {
    const fan = (j - (jets - 1) / 2) / Math.max(1, jets - 1);
    const angle =
      Math.PI / 2 - fan * 1.1 + 0.2 * (random(`${seed}-ja-${j}`) - 0.5);
    const length = size * (0.9 + 0.7 * random(`${seed}-jl-${j}`)) * rise;
    if (length < 0.5) continue;
    const bx = x + fan * size * 0.5;
    const tx = bx + Math.cos(angle) * length;
    const ty = y - Math.sin(angle) * length;
    pix.line(bx, y, tx, ty, done < 0.5 ? C.silver3 : C.silver2);
    pix.set(pix.px(tx), pix.py(ty), done < 0.5 ? C.moon : C.silver3);
  }
  for (let i = 0; i < 8 + 4 * size; i++) {
    const dropLife = life * (0.55 + 0.45 * random(`${seed}-l-${i}`));
    const u = age / dropLife;
    if (u > 1) continue;
    const side = random(`${seed}-s-${i}`) * 2 - 1;
    const height = size * (0.8 + 1.6 * random(`${seed}-h-${i}`));
    const px = pix.px(x + side * size * (0.3 + 0.9 * u));
    const py = pix.py(y - height * 4 * u * (1 - u));
    pix.set(px, py, u < 0.6 ? C.silver4 : C.silver2);
  }
  // The ring on the water, flattened by perspective.
  const r = size * (0.6 + 2.2 * done);
  const steps = done < 0.5 ? 2 : 1;
  const lit = new Set<number>();
  for (let i = 0; i < 48; i++) {
    const t = (2 * Math.PI * i) / 48;
    const px = pix.px(x + Math.cos(t) * r);
    const py = pix.py(y + Math.sin(t) * r * 0.3);
    if (lit.has(py * pix.w + px)) continue;
    lit.add(py * pix.w + px);
    pix.brighten(px, py, steps);
  }
};
