import type { Part } from "../pixel/lit";
import { flipParts } from "../pixel/lit";
import { C } from "../pixel/palette";
import { blob, capsule, ellipse, poly, type Vec2 } from "../pixel/shapes";

export type FishermanPose = "holdBucket";

export type FishermanProps = {
  // Where he sits: the hip on the thwart, in design units.
  x: number;
  y: number;
  pose: FishermanPose;
  facing: "left" | "right";
};

// A single pixel placed after lighting, such as an eye. `dx` and `dy` nudge
// it by whole pixels from its world position.
export type Feature = {
  x: number;
  y: number;
  c: number;
  dx?: number;
  dy?: number;
};

export type Figure = {
  // Drawn before the prop he holds.
  body: Part[];
  // Drawn after it: the hands that grip it.
  front: Part[];
  features: Feature[];
};

type Pose = {
  torso: Vec2[];
  thigh: [Vec2, Vec2];
  head: Vec2;
  ear: Vec2;
  crown: Vec2;
  // The sou'wester's brim: a band across the head, a short front brim and a
  // long flap down the back of the neck.
  brim: Vec2[];
  flap: Vec2[];
  // The beard as overlapping puffs: x, y, radius x, radius y.
  beard: [number, number, number, number][];
  mustache: [number, number, number, number][];
  nose: Vec2;
  brow: Vec2;
  eye: Vec2;
  upperArm: [Vec2, Vec2];
  forearm: [Vec2, Vec2];
  nearHand: Vec2;
  farHand: Vec2;
};

// Joint and outline positions relative to the hip, facing right.
const POSES: Record<FishermanPose, Pose> = {
  // Holding the bucket on his knees, bent over the moon inside it.
  holdBucket: {
    torso: [
      [-14, 2],
      [-17, -14],
      [-15, -30],
      [-9, -42],
      [0, -50],
      [9, -54],
      [18, -52],
      [24, -46],
      [27, -34],
      [30, -20],
      [33, -8],
      [30, 2],
      [0, 6],
    ],
    thigh: [
      [4, -3],
      [34, -9],
    ],
    head: [26, -62],
    ear: [19, -60.5],
    crown: [24, -72],
    brim: [
      [15, -70.5],
      [26, -70.5],
      [33, -69.5],
      [37, -71.8],
      [39.5, -71.5],
      [38.5, -68.8],
      [33, -67],
      [26, -67.8],
      [15, -67.5],
    ],
    flap: [
      [17, -70],
      [12, -67.5],
      [7.5, -62],
      [4.5, -55.5],
      [7, -54],
      [11, -58.5],
      [16, -63.5],
      [19, -66],
    ],
    beard: [
      [24, -52, 5.5, 5],
      [29.5, -54.5, 6, 4.5],
      [31, -49, 5.5, 5],
      [26, -45, 5, 4.5],
      [30, -41.5, 4, 3.8],
    ],
    mustache: [
      [33.5, -57, 3.6, 2],
      [36.5, -55.5, 2.2, 1.6],
    ],
    nose: [36.5, -60.5],
    brow: [31.5, -66],
    eye: [31, -63.8],
    upperArm: [
      [10, -46],
      [16, -26],
    ],
    forearm: [
      [16, -26],
      [29, -28],
    ],
    nearHand: [33, -28.5],
    farHand: [64, -29.5],
  },
};

// The old fisherman: yellow oilskins and sou'wester, white beard.
export const fisherman = ({ x, y, pose, facing }: FishermanProps): Figure => {
  const p = POSES[pose];
  const at = ([dx, dy]: Vec2): Vec2 => [x + dx, y + dy];
  const puff = ([px, py, rx, ry]: [number, number, number, number]): Part => ({
    shape: ellipse(...at([px, py]), rx, ry),
    mat: "beard",
    lift: 0.12,
    shadow: true,
  });
  const body: Part[] = [
    { shape: blob(p.torso.map(at)), mat: "oilskin", bevel: 7 },
    { shape: capsule(at(p.thigh[0]), at(p.thigh[1]), 7.5), mat: "oilskin" },
    { shape: ellipse(...at(p.head), 9, 9.5), mat: "skin" },
    { shape: poly(p.flap.map(at)), mat: "oilskin", bevel: 2, shadow: true },
    { shape: ellipse(...at(p.ear), 2.2, 3), mat: "skin", shadow: true },
    ...p.beard.map(puff),
    ...p.mustache.map(puff),
    {
      shape: ellipse(...at(p.nose), 3.5, 3.2),
      mat: "skin",
      shadow: true,
      lift: 0.22,
    },
    {
      shape: ellipse(...at(p.brow), 3.2, 1.6, 0.15),
      mat: "beard",
      lift: 0.12,
      shadow: true,
    },
    { shape: ellipse(...at(p.crown), 9.5, 7, -0.2), mat: "oilskin" },
    { shape: poly(p.brim.map(at)), mat: "oilskin", bevel: 1.2, shadow: true },
    {
      shape: capsule(at(p.upperArm[0]), at(p.upperArm[1]), 5.5, 5),
      mat: "oilskin",
      shadow: true,
    },
    {
      shape: capsule(at(p.forearm[0]), at(p.forearm[1]), 5, 4.3),
      mat: "oilskin",
      shadow: true,
    },
  ];
  const front: Part[] = [
    { shape: ellipse(...at(p.farHand), 3.2, 3.6), mat: "skin", lift: 0.15 },
    { shape: ellipse(...at(p.nearHand), 3.6, 4, 0.3), mat: "skin", lift: 0.15 },
  ];
  const [ex, ey] = at(p.eye);
  const features: Feature[] = [
    { x: ex, y: ey, c: C.ink },
    { x: ex, y: ey, c: C.silver4, dx: 1 },
  ];
  if (facing === "right") return { body, front, features };
  return {
    body: flipParts(body, x),
    front: flipParts(front, x),
    features: features.map((f) => ({ ...f, x: 2 * x - f.x, dx: -(f.dx ?? 0) })),
  };
};
