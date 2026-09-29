import type { Part } from "../pixel/lit";
import { flipParts } from "../pixel/lit";
import { C } from "../pixel/palette";
import { capsule, ellipse, poly, type Vec2 } from "../pixel/shapes";
import type { Feature } from "./fisherman";

export type CatPose = "peer";

export type CatProps = {
  // Where the cat sits, in design units.
  x: number;
  y: number;
  pose: CatPose;
  facing: "left" | "right";
};

export type CatFigure = {
  body: Part[];
  features: Feature[];
  // Fine lines drawn after lighting, in the moon's color.
  whiskers: (readonly [Vec2, Vec2])[];
};

type Pose = {
  haunch: Vec2;
  chest: [Vec2, number];
  head: Vec2;
  ears: [Vec2[], Vec2[]];
  muzzle: Vec2;
  legs: [Vec2, Vec2][];
  tail: Vec2[];
  eye: Vec2;
  nose: Vec2;
  whiskers: [Vec2, Vec2][];
};

// Positions relative to where the cat sits, facing left.
const POSES: Record<CatPose, Pose> = {
  // Sitting up, leaning toward something interesting, tail curled in a
  // question mark.
  peer: {
    haunch: [5, -7],
    chest: [[-3, -13], 0.25],
    head: [-9, -24],
    ears: [
      [
        [-6, -28.5],
        [-3.5, -35],
        [-1.5, -27.5],
      ],
      [
        [-13.5, -28],
        [-12, -35],
        [-8, -29.5],
      ],
    ],
    muzzle: [-14.2, -22.5],
    legs: [
      [
        [-3.5, -9],
        [-3.5, 0],
      ],
      [
        [-6, -10],
        [-6.5, 0],
      ],
    ],
    tail: [
      [11, -4],
      [15, -9],
      [16, -16],
      [14, -21],
      [11, -22],
    ],
    eye: [-12.6, -25.4],
    nose: [-16.2, -23.4],
    whiskers: [
      [
        [-15.5, -22],
        [-21.5, -23.5],
      ],
      [
        [-15.5, -21.2],
        [-21, -19.8],
      ],
    ],
  },
};

// The fisherman's ginger cat.
export const cat = ({ x, y, pose, facing }: CatProps): CatFigure => {
  const p = POSES[pose];
  const at = ([dx, dy]: Vec2): Vec2 => [x + dx, y + dy];
  const tail: Part[] = [];
  for (let i = 0; i < p.tail.length - 1; i++) {
    const r = 1.8 - (0.5 * i) / (p.tail.length - 2);
    tail.push({
      shape: capsule(at(p.tail[i]), at(p.tail[i + 1]), r, r - 0.15),
      mat: "cat",
    });
  }
  const body: Part[] = [
    ...tail,
    { shape: ellipse(...at(p.haunch), 8.5, 7.5), mat: "cat" },
    {
      shape: ellipse(...at(p.chest[0]), 6, 8.5, p.chest[1]),
      mat: "cat",
      bevel: 5,
    },
    ...p.legs.map(
      ([a, b]): Part => ({
        shape: capsule(at(a), at(b), 1.8, 1.7),
        mat: "cat",
        shadow: true,
      }),
    ),
    { shape: poly(p.ears[0].map(at)), mat: "cat", bevel: 1 },
    { shape: ellipse(...at(p.head), 6.5, 6), mat: "cat", shadow: true },
    { shape: poly(p.ears[1].map(at)), mat: "cat", bevel: 1.2, shadow: true },
    { shape: ellipse(...at(p.muzzle), 2.4, 1.9), mat: "cat", lift: 0.1 },
  ];
  const features: Feature[] = [
    { x: at(p.eye)[0], y: at(p.eye)[1], c: C.ochre3 },
    { x: at(p.nose)[0], y: at(p.nose)[1], c: C.skin1 },
  ];
  const lines = p.whiskers.map(([a, b]) => [at(a), at(b)] as const);
  if (facing === "left") return { body, features, whiskers: lines };
  const fx = (v: Vec2): Vec2 => [2 * x - v[0], v[1]];
  return {
    body: flipParts(body, x),
    features: features.map((f) => ({ ...f, x: 2 * x - f.x })),
    whiskers: lines.map(([a, b]) => [fx(a), fx(b)] as const),
  };
};
