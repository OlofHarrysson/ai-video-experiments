import { flipStrokes, type Stroke } from "../pixel/detail";
import type { Part } from "../pixel/lit";
import { flipParts } from "../pixel/lit";
import { C } from "../pixel/palette";
import {
  blend,
  blob,
  capsule,
  ellipse,
  poly,
  type Vec2,
} from "../pixel/shapes";

export type FishermanPose = "holdBucket";

export type FishermanProps = {
  // Where he sits: the hip on the thwart, in world units.
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
  // Folds, seams and strands, drawn over the finished shading.
  strokes: Stroke[];
};

type Oval = [x: number, y: number, rx: number, ry: number];

type Pose = {
  torso: Vec2[];
  shoulder: Oval;
  thigh: [Vec2, Vec2];
  head: Vec2;
  cheek: Vec2;
  ear: Vec2;
  crown: Vec2;
  // The sou'wester's brim across the head, and its long flap down the neck.
  brim: Vec2[];
  flap: Vec2[];
  // The beard as overlapping puffs.
  beard: Oval[];
  mustache: Oval[];
  nose: Vec2;
  brow: Vec2;
  eye: Vec2;
  // Shoulder, elbow and wrist of the near arm.
  arm: [Vec2, Vec2, Vec2];
  nearHand: Vec2;
  nearThumb: [Vec2, Vec2];
  farHand: Vec2;
  farFingers: [Vec2, Vec2];
  folds: Vec2[][];
  seams: Vec2[][];
  strands: Vec2[][];
  toggles: Vec2[];
};

// Positions relative to the hip, facing right.
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
    shoulder: [10, -48, 8, 6],
    thigh: [
      [4, -3],
      [34, -9],
    ],
    head: [26, -62],
    cheek: [30.5, -58],
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
    arm: [
      [10, -46],
      [16, -26],
      [29, -28],
    ],
    nearHand: [33, -28.5],
    nearThumb: [
      [31.5, -31.5],
      [34.5, -33],
    ],
    farHand: [64, -29.5],
    farFingers: [
      [62.5, -32.5],
      [60.5, -32],
    ],
    folds: [
      [
        [1, -46],
        [-5, -34],
        [-8, -20],
        [-9, -8],
      ],
      [
        [12.5, -31],
        [15.5, -29],
      ],
      [
        [13, -23.5],
        [16.5, -22.5],
      ],
      [
        [8, -6],
        [18, -8],
      ],
      [
        [28, -37],
        [29.5, -26],
        [31.5, -14],
      ],
      [
        [29.3, -61.8],
        [31.8, -61.6],
      ],
    ],
    seams: [
      [
        [15.5, -72],
        [21, -78],
        [29, -76.5],
      ],
    ],
    strands: [
      [
        [24, -54],
        [23.5, -48],
      ],
      [
        [28.5, -52],
        [28.5, -45],
      ],
      [
        [32.5, -50.5],
        [31.5, -44],
      ],
    ],
    toggles: [
      [29, -31],
      [30.3, -21],
    ],
  },
};

// The old fisherman: yellow oilskins and sou'wester, white beard. The coat,
// the arm and each hand are grown as single pieces, so joints shade as one
// surface instead of separate tubes.
export const fisherman = ({ x, y, pose, facing }: FishermanProps): Figure => {
  const p = POSES[pose];
  const at = ([dx, dy]: Vec2): Vec2 => [x + dx, y + dy];
  const oval = ([ox, oy, rx, ry]: Oval, rot = 0) =>
    ellipse(...at([ox, oy]), rx, ry, rot);
  const puff = (o: Oval): Part => ({
    shape: oval(o),
    mat: "beard",
    lift: 0.12,
    shadow: true,
  });
  const [shoulder, elbow, wrist] = p.arm.map(at);
  const body: Part[] = [
    {
      shape: blend(
        [
          blob(p.torso.map(at)),
          oval(p.shoulder),
          capsule(at(p.thigh[0]), at(p.thigh[1]), 7.5),
        ],
        5,
        0.5,
        1,
      ),
      mat: "oilskin",
      bevel: 7,
    },
    {
      shape: blend(
        [ellipse(...at(p.head), 9, 9.5), ellipse(...at(p.cheek), 5, 4)],
        2,
      ),
      mat: "skin",
      bevel: 6,
      lift: 0.08,
    },
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
      shape: blend(
        [capsule(shoulder, elbow, 5.5, 5), capsule(elbow, wrist, 5, 4.3)],
        3,
        0.3,
        3,
      ),
      mat: "oilskin",
      bevel: 4.8,
      shadow: true,
    },
    // The cuff: a slightly thicker, lighter ring at the end of the sleeve.
    {
      shape: capsule(
        [wrist[0] - 2, wrist[1] + 0.1],
        [wrist[0] + 0.6, wrist[1] - 0.2],
        4.6,
      ),
      mat: "oilskin",
      lift: 0.12,
    },
  ];
  const front: Part[] = [
    {
      shape: blend(
        [
          ellipse(...at(p.farHand), 3.2, 3.6),
          capsule(at(p.farFingers[0]), at(p.farFingers[1]), 1.2),
        ],
        1.2,
      ),
      mat: "skin",
      bevel: 2.5,
      lift: 0.15,
    },
    {
      shape: blend(
        [
          ellipse(...at(p.nearHand), 3.4, 3.6, 0.3),
          capsule(at(p.nearThumb[0]), at(p.nearThumb[1]), 1.3),
        ],
        1.2,
      ),
      mat: "skin",
      bevel: 2.5,
      lift: 0.15,
    },
  ];
  const [ex, ey] = at(p.eye);
  const features: Feature[] = [
    { x: ex, y: ey, c: C.ink },
    { x: ex, y: ey, c: C.silver4, dx: 1 },
  ];
  const line = (pts: Vec2[], steps: number): Stroke => ({
    pts: pts.map(at),
    steps,
  });
  const strokes: Stroke[] = [
    ...p.folds.map((f) => line(f, -1)),
    ...p.seams.map((f) => line(f, -1)),
    ...p.strands.map((f) => line(f, -1)),
    ...p.toggles.map((t) => line([t], 2)),
  ];
  if (facing === "right") return { body, front, features, strokes };
  return {
    body: flipParts(body, x),
    front: flipParts(front, x),
    features: features.map((f) => ({
      ...f,
      x: 2 * x - f.x,
      dx: -(f.dx ?? 0),
    })),
    strokes: flipStrokes(strokes, x),
  };
};
