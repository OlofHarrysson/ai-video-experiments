import { random } from "remotion";
import type { Part } from "../pixel/lit";
import { Pix } from "../pixel/pix";
import { covers, poly, type Shape, type Vec2 } from "../pixel/shapes";

// A small wooden rowing boat seen broadside, stern left and bow right, from
// slightly above the gunwale so a sliver of the far side shows inside.
export type BoatProps = {
  stern: number;
  bow: number;
  // Height of the near gunwale at its lowest point, and where that is.
  gunwale: number;
  mid: number;
  waterline: number;
  sheerBow: number;
  sheerStern: number;
  // How much of the far side shows above the near gunwale amidships.
  inside: number;
};

export const BOAT: BoatProps = {
  stern: 30,
  bow: 225,
  gunwale: 356,
  mid: 125,
  waterline: 384,
  sheerBow: 16,
  sheerStern: 8,
  inside: 6,
};

export const gunwaleY = (b: BoatProps, x: number): number =>
  x > b.mid
    ? b.gunwale - b.sheerBow * ((x - b.mid) / (b.bow - b.mid)) ** 2
    : b.gunwale - b.sheerStern * ((b.mid - x) / (b.mid - b.stern)) ** 2;

const farGunwaleY = (b: BoatProps, x: number): number => {
  const u = (2 * (x - b.stern)) / (b.bow - b.stern) - 1;
  return gunwaleY(b, x) - b.inside * (1 - u * u);
};

const along = (b: BoatProps, f: (x: number) => number, step = 3): Vec2[] => {
  const pts: Vec2[] = [];
  for (let x = b.stern; x < b.bow; x += step) pts.push([x, f(x)]);
  pts.push([b.bow, f(b.bow)]);
  return pts;
};

const hullShape = (b: BoatProps): Shape => {
  const top = along(b, (x) => gunwaleY(b, x));
  const bowTop = gunwaleY(b, b.bow);
  const drop = b.waterline - bowTop;
  const stem: Vec2[] = [
    [b.bow - 1.5, bowTop + drop * 0.3],
    [b.bow - 5, bowTop + drop * 0.62],
    [b.bow - 10, bowTop + drop * 0.88],
    [b.bow - 16, b.waterline],
  ];
  return poly([
    ...top,
    ...stem,
    [b.stern + 8, b.waterline],
    [b.stern, gunwaleY(b, b.stern)],
  ]);
};

// The inside of the far side, drawn behind the crew.
export const boatInterior = (b: BoatProps): Part[] => {
  const far = along(b, (x) => farGunwaleY(b, x));
  const near = along(b, (x) => gunwaleY(b, x)).reverse();
  const rail = [
    ...along(b, (x) => farGunwaleY(b, x) - 1.6),
    ...along(b, (x) => farGunwaleY(b, x) + 0.4).reverse(),
  ];
  return [
    { shape: poly([...far, ...near]), mat: "wood", flat: [0, -0.3, 1], z: -25 },
    { shape: poly(rail), mat: "wood", flat: [0, -1, 0.6], lift: 0.1, z: -25 },
  ];
};

// The near side, drawn in front of the crew.
export const boatHull = (b: BoatProps): Part[] => {
  const rail = [
    ...along(b, (x) => gunwaleY(b, x)),
    ...along(b, (x) => gunwaleY(b, x) + 3).reverse(),
  ];
  return [
    { shape: hullShape(b), mat: "wood", flat: [0, 0.15, 1], z: 25 },
    { shape: poly(rail), mat: "wood", bevel: 1.5, lift: 0.12, z: 22 },
  ];
};

const PLANKS = [9, 17, 24];

// Clinker planks: each plank's lower edge catches a little light, copper
// rivets dot the seams, and short dark streaks of grain run along the wood.
export const drawPlankSeams = (pix: Pix, b: BoatProps): void => {
  const hull = hullShape(b);
  const onHull = (x: number, py: number) => covers(hull, x, pix.wy(py));
  for (const offset of PLANKS) {
    for (let px = pix.px(b.stern); px <= pix.px(b.bow); px++) {
      const x = pix.wx(px);
      const py = pix.py(gunwaleY(b, x) + offset);
      if (onHull(x, py)) pix.brighten(px, py, 1);
    }
    for (let x = b.stern + 6; x < b.bow - 6; x += 9) {
      const py = pix.py(gunwaleY(b, x) + offset) - 1;
      if (onHull(x, py)) pix.brighten(pix.px(x), py, 2);
    }
  }
  for (let i = 0; i < 70; i++) {
    const x = b.stern + random(`grain-x-${i}`) * (b.bow - b.stern);
    const depth = 3 + random(`grain-y-${i}`) * 26;
    const len = 3 + random(`grain-l-${i}`) * 7;
    for (let dx = 0; dx < len; dx += 1 / pix.s) {
      const py = pix.py(gunwaleY(b, x + dx) + depth);
      if (onHull(x + dx, py)) pix.darken(pix.px(x + dx), py, 1);
    }
  }
};

// The boat's ribs, seen on the inside of the far side.
export const drawRibs = (pix: Pix, b: BoatProps): void => {
  for (let x = b.stern + 10; x < b.bow - 8; x += 11) {
    const top = pix.py(farGunwaleY(b, x)) + 1;
    const bottom = pix.py(gunwaleY(b, x));
    for (let py = top; py < bottom; py++) {
      if (pix.isSolid(pix.px(x), py)) pix.darken(pix.px(x), py, 1);
    }
  }
};
