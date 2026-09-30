import type { Part } from "../pixel/lit";
import { moveShape, toLocal, toWorld, type Frame } from "../pixel/rig";
import { ellipse, poly, type Vec2 } from "../pixel/shapes";
import { moonParts } from "./moon";

export type BucketProps = {
  // Center of the opening, in world units.
  x: number;
  rimY: number;
  // The caught moon floats in the opening, most of it above the rim.
  moon: boolean;
  // Degrees the bucket is tipped, clockwise, about its middle.
  tilt?: number;
  // How brightly the moon inside still shines, 0 to 1.
  glow?: number;
};

export const MOON_RADIUS = 12;

// Upright bucket, then the tipped one: the same pivot, turned by the tilt.
const pivots = ({ x, rimY, tilt = 0 }: BucketProps): [Frame, Frame] => {
  const at = { x, y: rimY + HEIGHT / 2 };
  return [
    { ...at, a: 0 },
    { ...at, a: (tilt * Math.PI) / 180 },
  ];
};

export const moonCenter = (b: BucketProps): Vec2 => {
  const [upright, tipped] = pivots(b);
  return toWorld(tipped, toLocal(upright, [b.x, b.rimY - 3]));
};

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
export const bucket = (props: BucketProps): Part[] => {
  const { x, rimY, moon, tilt = 0, glow = 1 } = props;
  const lit = moon ? 1 : 0;
  const bottom = rimY + HEIGHT;
  const tin = { cx: x, rx: RX };
  const [mx, my] = moonCenter(props);
  const opening: Part = {
    shape: ellipse(x, rimY, RX, RY),
    mat: "tin",
    emit: () => 0.3 + 0.5 * lit * glow,
  };
  const pail: Part[] = [
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
      emit: () => 0.3 + 0.62 * lit * glow,
    },
  ];
  const [upright, tipped] = pivots(props);
  const tip = (part: Part): Part =>
    tilt === 0
      ? part
      : {
          ...part,
          shape: moveShape(part.shape, upright, tipped),
          // A tipped pail is shaded from its own outline.
          cylinder: undefined,
          bevel: part.cylinder ? 6 : part.bevel,
        };
  return [
    tip(opening),
    ...(moon ? moonParts({ x: mx, y: my, radius: MOON_RADIUS, glow }) : []),
    ...pail.map(tip),
  ];
};
