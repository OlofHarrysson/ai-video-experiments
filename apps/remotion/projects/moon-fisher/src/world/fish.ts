import { random } from "remotion";
import type { Part } from "../pixel/lit";
import { C } from "../pixel/palette";
import { Pix } from "../pixel/pix";
import { ellipse, poly, type Vec2 } from "../pixel/shapes";

export type FishProps = {
  // Center of the body, in world units.
  at: Vec2;
  // Heading in degrees: 0 swims right, -90 leaps straight up.
  angle: number;
  size?: number;
};

// A silver fish: a slim body and a forked tail, turned along its heading.
export const fishParts = ({
  at: [x, y],
  angle,
  size = 1,
}: FishProps): Part[] => {
  const a = (angle * Math.PI) / 180;
  const [dx, dy] = [Math.cos(a), Math.sin(a)];
  const back = (d: number, side: number): Vec2 => [
    x - dx * d * size - dy * side * size,
    y - dy * d * size + dx * side * size,
  ];
  return [
    {
      shape: poly([
        back(3.6, 0),
        back(6.4, -2.2),
        back(5.8, 0),
        back(6.4, 2.2),
      ]),
      mat: "tin",
      lift: 0.25,
    },
    { shape: ellipse(x, y, 4.4 * size, 1.7 * size, a), mat: "tin", lift: 0.3 },
  ];
};

export type SplashProps = { at: Vec2; size: number; seed: string };

// Water thrown up where something breaks the surface: bright droplets in a
// crown and a pale ring on the water.
export const drawSplash = (
  pix: Pix,
  { at: [x, y], size, seed }: SplashProps,
): void => {
  for (let i = 0; i < 26; i++) {
    const a = Math.PI * (0.1 + 0.8 * random(`${seed}-a-${i}`));
    const r = size * (0.3 + 0.7 * random(`${seed}-r-${i}`));
    const px = pix.px(x + Math.cos(a) * r);
    const py = pix.py(y - Math.sin(a) * r * 1.3);
    pix.set(px, py, random(`${seed}-c-${i}`) < 0.5 ? C.silver4 : C.silver2);
  }
  for (let i = 0; i < 40; i++) {
    const a = (2 * Math.PI * i) / 40;
    pix.brighten(
      pix.px(x + Math.cos(a) * size * 1.1),
      pix.py(y + Math.sin(a) * size * 0.3),
      2,
    );
  }
};
