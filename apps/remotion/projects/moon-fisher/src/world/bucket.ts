import type { Part } from "../pixel/lit";
import { ellipse, poly, type Vec2 } from "../pixel/shapes";
import { moonParts } from "./moon";

export type BucketProps = {
  // Center of the opening, in world units.
  x: number;
  rimY: number;
  // The caught moon floats in the opening, most of it above the rim.
  moon: boolean;
};

export const MOON_RADIUS = 12;
export const moonCenter = ({ x, rimY }: BucketProps): [number, number] => [
  x,
  rimY - 3,
];

const RX = 15;
const RY = 3.5;
const HEIGHT = 24;
const TAPER = 2.2;

// Points along the front half of an ellipse around the opening, from the
// right end to the left.
const front = (x: number, y: number, rx: number, ry: number): Vec2[] => {
  const pts: Vec2[] = [];
  for (let i = 0; i <= 16; i++) {
    const a = (Math.PI * i) / 16;
    pts.push([x + rx * Math.cos(a), y + ry * Math.sin(a)]);
  }
  return pts;
};

// A band that follows the front of the bucket at a given depth below the rim.
const band = (x: number, y: number, rx: number, width: number): Vec2[] => [
  ...front(x, y, rx, RY),
  ...front(x, y + width, rx, RY).reverse(),
];

// A tin pail seen from the side and a little above. With the moon inside,
// its opening is the scene's light source.
export const bucket = ({ x, rimY, moon }: BucketProps): Part[] => {
  const lit = moon ? 1 : 0;
  const bottom = rimY + HEIGHT;
  const tin = { cx: x, rx: RX };
  const [mx, my] = moonCenter({ x, rimY, moon });
  return [
    {
      shape: ellipse(x, rimY, RX, RY),
      mat: "tin",
      emit: () => 0.3 + 0.5 * lit,
    },
    ...(moon ? moonParts({ x: mx, y: my, radius: MOON_RADIUS }) : []),
    {
      shape: poly([
        ...front(x, rimY, RX, RY),
        [x - RX + TAPER, bottom],
        [x + RX - TAPER, bottom],
      ]),
      mat: "tin",
      cylinder: tin,
      lift: 0.14,
    },
    // A sheen down the tin where it faces the sky.
    {
      shape: poly([
        [x - 8, rimY + RY + 2],
        [x - 5.5, rimY + RY + 2.3],
        [x - 4.8, bottom - 0.6],
        [x - 7, bottom - 0.8],
      ]),
      mat: "tin",
      flat: [0, 0, 1],
      lift: 0.3,
    },
    {
      shape: poly(band(x, rimY + 10, RX - TAPER * 0.4, 1.3)),
      mat: "tin",
      cylinder: tin,
      lift: 0.3,
    },
    // The shadow under the rolled lip, then the lip itself catching the moon.
    {
      shape: poly(band(x, rimY + 0.6, RX, 1.2)),
      mat: "tin",
      cylinder: tin,
      lift: -0.1,
    },
    {
      shape: poly(band(x, rimY - 0.6, RX + 0.4, 1.2)),
      mat: "tin",
      emit: () => 0.3 + 0.62 * lit,
    },
  ];
};
