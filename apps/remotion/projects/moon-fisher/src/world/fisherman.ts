import { flipStrokes, type Stroke } from "../pixel/detail";
import { flipParts, type Part } from "../pixel/lit";
import { C } from "../pixel/palette";
import {
  boneEnd,
  buildRig,
  moveShape,
  poseRig,
  toLocal,
  toWorld,
  type Angles,
  type Frame,
} from "../pixel/rig";
import {
  blend,
  blob,
  capsule,
  ellipse,
  poly,
  type Shape,
  type Vec2,
} from "../pixel/shapes";

// The fisherman's skeleton in its rest pose, holding the bucket, relative to
// the hip. Every part below is drawn in this pose and rides on one bone.
const RIG = buildRig({
  spine: { parent: null, start: [0, 0], end: [6, -24] },
  thigh: { parent: null, start: [4, -3], end: [34, -9] },
  shin: { parent: "thigh", start: [34, -9], end: [37, 18] },
  chest: { parent: "spine", start: [6, -24], end: [17, -47] },
  head: { parent: "chest", start: [17, -47], end: [26, -62] },
  farUpperArm: { parent: "chest", start: [13, -47], end: [20, -28] },
  farForearm: { parent: "farUpperArm", start: [20, -28], end: [33, -30] },
  farHand: { parent: "farForearm", start: [33, -30], end: [37, -30.5] },
  upperArm: { parent: "chest", start: [10, -46], end: [16, -26] },
  forearm: { parent: "upperArm", start: [16, -26], end: [29, -28] },
  hand: { parent: "forearm", start: [29, -28], end: [33, -28.5] },
});

export type Bone =
  | "spine"
  | "thigh"
  | "shin"
  | "chest"
  | "head"
  | "farUpperArm"
  | "farForearm"
  | "farHand"
  | "upperArm"
  | "forearm"
  | "hand";

export type Eyes = "open" | "closed" | "wide";

export type PoseDef = {
  // Absolute bone directions in degrees: 0 right, 90 down, -90 up.
  angles: Partial<Record<Bone, number>>;
  eyes: Eyes;
  // In the rest pose he holds the bucket by both rims: this hand is drawn on
  // the prop instead of at the end of the far arm, which stays hidden.
  farHandOnProp?: Vec2;
  // How far he smiles, 0 to 1: his cheek rises, a laugh line creases above
  // the mustache, and past two thirds his open eyes narrow to happy arcs.
  smile?: number;
};

export const POSES = {
  holdBucket: { angles: {}, eyes: "open", farHandOnProp: [64, -29.5] },
  // Slumped asleep, hands on his lap, hat tipped over his eyes.
  doze: {
    angles: {
      spine: -85,
      chest: -50,
      head: -15,
      upperArm: 92,
      forearm: 35,
      hand: 40,
      farUpperArm: 90,
      farForearm: 32,
      farHand: 40,
    },
    eyes: "closed",
  },
  // Thrown back against the pull of the line, both hands on the rod.
  haul: {
    angles: {
      spine: -95,
      chest: -118,
      head: -70,
      upperArm: 35,
      forearm: -60,
      hand: -70,
      farUpperArm: 40,
      farForearm: -55,
      farHand: -70,
      thigh: -18,
      shin: 65,
    },
    eyes: "wide",
  },
  // The haul's two extremes: thrown back with the rod raised high against
  // the pull, and leaning in with it lowered to take up the line.
  heave: {
    angles: {
      spine: -104,
      chest: -132,
      head: -80,
      upperArm: 10,
      forearm: -82,
      hand: -92,
      farUpperArm: 14,
      farForearm: -78,
      farHand: -92,
      thigh: -22,
      shin: 62,
    },
    eyes: "wide",
  },
  reel: {
    angles: {
      spine: -86,
      chest: -102,
      head: -58,
      upperArm: 52,
      forearm: -38,
      hand: -48,
      farUpperArm: 56,
      farForearm: -34,
      farHand: -48,
      thigh: -16,
      shin: 66,
    },
    eyes: "wide",
  },
  // Leaning out over the gunwale, tipping the bucket.
  tip: {
    angles: {
      spine: -60,
      chest: -40,
      head: -25,
      upperArm: 30,
      forearm: 35,
      hand: 40,
      farUpperArm: 33,
      farForearm: 38,
      farHand: 40,
    },
    eyes: "open",
  },
  // Awake and fishing: sitting up, rod held out in both hands, watching the
  // float.
  fish: {
    angles: {
      spine: -80,
      chest: -68,
      head: -48,
      upperArm: 75,
      forearm: -5,
      hand: -15,
      farUpperArm: 72,
      farForearm: -8,
      farHand: -15,
    },
    eyes: "open",
  },
  // Still holding the bucket, looking up at the empty sky.
  lookUp: {
    angles: { head: -100 },
    eyes: "open",
    farHandOnProp: [64, -29.5],
  },
} satisfies Record<string, PoseDef>;

export type FishermanPose = keyof typeof POSES;

// An in-between of two poses. Each bone travels at its own time `t(bone)`,
// from 0 at the first pose to 1 at the second, so a movement can lead with
// the head and let the arms follow.
export const tweenPose = (
  from: PoseDef,
  to: PoseDef,
  t: (bone: Bone) => number,
  eyes: Eyes,
): PoseDef => {
  const angles: Partial<Record<Bone, number>> = {};
  for (const b of RIG.bones) {
    const name = b.name as Bone;
    const rest = (b.rest.a * 180) / Math.PI;
    const x = from.angles[name] ?? rest;
    const y = to.angles[name] ?? rest;
    angles[name] = x + (y - x) * t(name);
  }
  return { angles, eyes };
};

export type FishermanProps = {
  // Where he sits: the hip on the thwart, in world units.
  x: number;
  y: number;
  pose: FishermanPose | PoseDef;
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
  // Where each hand closes, in world units.
  grip: Vec2;
  farGrip: Vec2;
};

type Piece = { bone: Bone; shape: Shape };
type Oval = [x: number, y: number, rx: number, ry: number, rot?: number];

const oval = ([x, y, rx, ry, rot]: Oval): Shape =>
  ellipse(x, y, rx, ry, rot ?? 0);

// The rest-pose drawing, relative to the hip.
const LOWER_TORSO: Vec2[] = [
  [-14, 2],
  [-17, -14],
  [-15, -30],
  [-11, -38],
  [10, -38],
  [27, -34],
  [30, -20],
  [33, -8],
  [30, 2],
  [0, 6],
];
const UPPER_TORSO: Vec2[] = [
  [-15, -28],
  [-9, -42],
  [0, -50],
  [9, -54],
  [18, -52],
  [24, -46],
  [27, -34],
  [26, -24],
  [0, -24],
];
const BRIM: Vec2[] = [
  [15, -70.5],
  [26, -70.5],
  [33, -69.5],
  [37, -71.8],
  [39.5, -71.5],
  [38.5, -68.8],
  [33, -67],
  [26, -67.8],
  [15, -67.5],
];
const FLAP: Vec2[] = [
  [17, -70],
  [12, -67.5],
  [7.5, -62],
  [4.5, -55.5],
  [7, -54],
  [11, -58.5],
  [16, -63.5],
  [19, -66],
];
const BEARD: Oval[] = [
  [24, -52, 5.5, 5],
  [29.5, -54.5, 6, 4.5],
  [31, -49, 5.5, 5],
  [26, -45, 5, 4.5],
  [30, -41.5, 4, 3.8],
];
const MUSTACHE: Oval[] = [
  [33.5, -57, 3.6, 2],
  [36.5, -55.5, 2.2, 1.6],
];
const EYE: Vec2 = [31, -63.8];
// A smile's crease from the side of the nose back above the mustache.
const SMILE_LINES: { bone: Bone; pts: Vec2[]; steps: number }[] = [
  {
    bone: "head",
    pts: [
      [35.2, -59.6],
      [34, -58.7],
      [32.6, -58.5],
    ],
    steps: -1,
  },
];
const STROKES: { bone: Bone; pts: Vec2[]; steps: number }[] = [
  // Coat folds down the back, at the elbow, across the lap and the closure.
  {
    bone: "chest",
    pts: [
      [1, -46],
      [-5, -34],
    ],
    steps: -1,
  },
  {
    bone: "spine",
    pts: [
      [-5, -34],
      [-8, -20],
      [-9, -8],
    ],
    steps: -1,
  },
  {
    bone: "upperArm",
    pts: [
      [12.5, -31],
      [15.5, -29],
    ],
    steps: -1,
  },
  {
    bone: "forearm",
    pts: [
      [13, -23.5],
      [16.5, -22.5],
    ],
    steps: -1,
  },
  {
    bone: "thigh",
    pts: [
      [8, -6],
      [18, -8],
    ],
    steps: -1,
  },
  {
    bone: "spine",
    pts: [
      [28, -37],
      [29.5, -26],
      [31.5, -14],
    ],
    steps: -1,
  },
  { bone: "spine", pts: [[29, -31]], steps: 2 },
  { bone: "spine", pts: [[30.3, -21]], steps: 2 },
  // The hat's seam and beard strands.
  {
    bone: "head",
    pts: [
      [15.5, -72],
      [21, -78],
      [29, -76.5],
    ],
    steps: -1,
  },
  {
    bone: "head",
    pts: [
      [24, -54],
      [23.5, -48],
    ],
    steps: -1,
  },
  {
    bone: "head",
    pts: [
      [28.5, -52],
      [28.5, -45],
    ],
    steps: -1,
  },
  {
    bone: "head",
    pts: [
      [32.5, -50.5],
      [31.5, -44],
    ],
    steps: -1,
  },
];
// The bag under his eye, which a smile's cheek pushes away.
const EYE_BAG: { bone: Bone; pts: Vec2[]; steps: number } = {
  bone: "head",
  pts: [
    [29.3, -61.8],
    [31.8, -61.6],
  ],
  steps: -1,
};

// The old fisherman: yellow oilskins and sou'wester, white beard. The coat,
// each arm and each hand are grown as single pieces, so joints shade as one
// surface, and the skeleton bends them into any pose.
export const fisherman = ({ x, y, pose, facing }: FishermanProps): Figure => {
  const def: PoseDef = typeof pose === "string" ? POSES[pose] : pose;
  const smile = def.smile ?? 0;
  const frames = poseRig(RIG, [x, y], def.angles as Angles);
  const restAt = (bone: Bone): Frame => RIG.rest[bone];
  const on = (bone: Bone, s: Shape): Shape =>
    moveShape(s, restAt(bone), frames[bone]);
  const point = (bone: Bone, p: Vec2): Vec2 =>
    toWorld(frames[bone], toLocal(restAt(bone), p));
  const grown = (pieces: Piece[], k: number, wobble = 0, seed = 0): Shape =>
    blend(
      pieces.map((p) => on(p.bone, p.shape)),
      k,
      wobble,
      seed,
    );
  const puff = (o: Oval): Part => ({
    shape: on("head", oval(o)),
    mat: "beard",
    lift: 0.12,
    shadow: true,
  });

  const farArm: Part[] = def.farHandOnProp
    ? []
    : [
        {
          shape: grown(
            [
              {
                bone: "farUpperArm",
                shape: capsule([13, -47], [20, -28], 5.2, 4.8),
              },
              {
                bone: "farForearm",
                shape: capsule([20, -28], [33, -30], 4.8, 4.1),
              },
            ],
            3,
            0.3,
            4,
          ),
          mat: "oilskin",
          bevel: 4.8,
          lift: -0.12,
        },
        {
          shape: grown(
            [
              { bone: "farHand", shape: ellipse(37, -30.5, 3.2, 3.4) },
              {
                bone: "farHand",
                shape: capsule([35.5, -33], [38.5, -34], 1.2),
              },
            ],
            1.2,
          ),
          mat: "skin",
          bevel: 2.5,
          lift: 0.05,
        },
      ];

  const body: Part[] = [
    ...farArm,
    {
      shape: grown(
        [
          { bone: "spine", shape: blob(LOWER_TORSO) },
          { bone: "chest", shape: blob(UPPER_TORSO) },
          { bone: "chest", shape: ellipse(10, -48, 8, 6) },
          { bone: "thigh", shape: capsule([4, -3], [34, -9], 7.5) },
          { bone: "shin", shape: capsule([34, -9], [37, 18], 6, 5.5) },
        ],
        5,
        0.5,
        1,
      ),
      mat: "oilskin",
      bevel: 7,
    },
    {
      shape: grown(
        [
          { bone: "head", shape: ellipse(26, -62, 9, 9.5) },
          { bone: "head", shape: ellipse(30.5, -58, 5, 4) },
        ],
        2,
      ),
      mat: "skin",
      bevel: 6,
      lift: 0.08,
      // A smile lifts the cheek under the eye.
      marks:
        smile > 0.15
          ? [
              {
                shape: on(
                  "head",
                  ellipse(
                    31.6,
                    -60.2 - 0.6 * smile,
                    1 + 1.5 * smile,
                    0.8 + smile,
                  ),
                ),
                mat: "cheek",
              },
            ]
          : [],
    },
    { shape: on("head", poly(FLAP)), mat: "oilskin", bevel: 2, shadow: true },
    {
      shape: on("head", ellipse(19, -60.5, 2.2, 3)),
      mat: "skin",
      shadow: true,
    },
    ...BEARD.map(puff),
    // The mustache lifts at the back as he smiles.
    ...MUSTACHE.map(([mx, my, rx, ry], i) =>
      puff([mx, my - (i === 0 ? 0.7 : 0.3) * smile, rx, ry]),
    ),
    {
      shape: on("head", ellipse(36.5, -60.5, 3.5, 3.2)),
      mat: "skin",
      shadow: true,
      lift: 0.22,
    },
    {
      // The eyebrow climbs when he is startled.
      shape: on(
        "head",
        ellipse(31.5, def.eyes === "wide" ? -67.5 : -66, 3.2, 1.6, 0.15),
      ),
      mat: "beard",
      lift: 0.12,
      shadow: true,
    },
    { shape: on("head", ellipse(24, -72, 9.5, 7, -0.2)), mat: "oilskin" },
    { shape: on("head", poly(BRIM)), mat: "oilskin", bevel: 1.2, shadow: true },
    {
      shape: grown(
        [
          { bone: "upperArm", shape: capsule([10, -46], [16, -26], 5.5, 5) },
          { bone: "forearm", shape: capsule([16, -26], [29, -28], 5, 4.3) },
        ],
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
      shape: on("forearm", capsule([27, -27.9], [29.6, -28.2], 4.6)),
      mat: "oilskin",
      lift: 0.12,
    },
  ];

  const nearHand: Part = {
    shape: grown(
      [
        { bone: "hand", shape: ellipse(33, -28.5, 3.4, 3.6, 0.3) },
        { bone: "hand", shape: capsule([31.5, -31.5], [34.5, -33], 1.3) },
      ],
      1.2,
    ),
    mat: "skin",
    bevel: 2.5,
    lift: 0.15,
  };
  const propHand: Part[] = def.farHandOnProp
    ? [
        {
          shape: blend(
            [
              ellipse(
                x + def.farHandOnProp[0],
                y + def.farHandOnProp[1],
                3.2,
                3.6,
              ),
              capsule(
                [x + def.farHandOnProp[0] - 1.5, y + def.farHandOnProp[1] - 3],
                [
                  x + def.farHandOnProp[0] - 3.5,
                  y + def.farHandOnProp[1] - 2.5,
                ],
                1.2,
              ),
            ],
            1.2,
          ),
          mat: "skin",
          bevel: 2.5,
          lift: 0.15,
        },
      ]
    : [];
  const front: Part[] = [...propHand, nearHand];

  const [ex, ey] = point("head", EYE);
  const happy = def.eyes === "open" && smile > 0.65;
  const features: Feature[] =
    def.eyes === "closed"
      ? [
          { x: ex, y: ey, c: C.umber1 },
          { x: ex, y: ey, c: C.umber1, dx: -1 },
        ]
      : happy
        ? [
            { x: ex, y: ey, c: C.umber1, dx: -1 },
            { x: ex, y: ey, c: C.umber1, dy: -1 },
            { x: ex, y: ey, c: C.umber1, dx: 1 },
          ]
        : [
            { x: ex, y: ey, c: C.ink },
            { x: ex, y: ey, c: C.silver4, dx: 1 },
          ];
  const strokes: Stroke[] = [
    ...STROKES,
    ...(smile > 0.35 ? SMILE_LINES : [EYE_BAG]),
  ].map((s) => ({
    pts: s.pts.map((p) => point(s.bone, p)),
    steps: s.steps,
  }));
  const grip = boneEnd(RIG, frames, "hand");
  const farGrip = def.farHandOnProp
    ? ([x + def.farHandOnProp[0], y + def.farHandOnProp[1]] as const)
    : boneEnd(RIG, frames, "farHand");

  if (facing === "right")
    return { body, front, features, strokes, grip, farGrip };
  const fx = ([px, py]: Vec2): Vec2 => [2 * x - px, py];
  return {
    body: flipParts(body, x),
    front: flipParts(front, x),
    features: features.map((f) => ({ ...f, x: 2 * x - f.x, dx: -(f.dx ?? 0) })),
    strokes: flipStrokes(strokes, x),
    grip: fx(grip),
    farGrip: fx(farGrip),
  };
};
