import { flipStrokes, type Stroke } from "../pixel/detail";
import type { Mark, Part } from "../pixel/lit";
import { flipParts } from "../pixel/lit";
import { C } from "../pixel/palette";
import { blend, capsule, ellipse, poly, type Vec2 } from "../pixel/shapes";
import type { Feature } from "./fisherman";

export type CatPose = "peer";

export type CatProps = {
  // Where the cat sits, in world units.
  x: number;
  y: number;
  pose: CatPose;
  facing: "left" | "right";
  // Degrees the head tilts up, toward the side the cat faces.
  look?: number;
  // How far the front paw reaches out, 0 to 1.
  paw?: number;
  // Degrees the whole cat leans forward over its front paws, as in a pounce.
  lean?: number;
};

export type CatFigure = {
  body: Part[];
  features: Feature[];
  strokes: Stroke[];
  // Fine lines drawn after lighting, in the moon's color.
  whiskers: (readonly [Vec2, Vec2])[];
  // Where it would hold something in its mouth, in world units.
  mouth: Vec2;
};

type Oval = [x: number, y: number, rx: number, ry: number, rot?: number];
type Limb = [Vec2, Vec2, number];

type Pose = {
  haunch: Oval;
  chest: Oval;
  neck: Oval;
  legs: Limb[];
  tail: Vec2[];
  head: Oval;
  muzzle: Oval;
  cheek: Oval;
  ears: [Vec2[], Vec2[]];
  innerEar: Vec2[];
  chestPatch: Oval;
  muzzlePatch: Oval;
  bodyStripes: Limb[];
  headStripes: Limb[];
  eye: Vec2;
  nose: Vec2;
  mouth: Vec2;
  whiskers: [Vec2, Vec2][];
  legGap: Vec2[];
};

// Positions relative to where the cat sits, facing left.
const POSES: Record<CatPose, Pose> = {
  // Sitting up, leaning toward something interesting, tail curled in a
  // question mark.
  peer: {
    haunch: [5, -7, 8.5, 7.5],
    chest: [-3, -13, 6, 8.5, 0.25],
    neck: [-6, -19, 4.2, 4],
    legs: [
      [[-3.5, -9], [-3.5, 0], 1.9],
      [[-6, -10], [-6.5, 0], 1.8],
    ],
    tail: [
      [11, -4],
      [15, -9],
      [16, -16],
      [14, -21],
      [11, -22],
    ],
    head: [-9, -24, 6.5, 6],
    muzzle: [-14.2, -22.5, 2.4, 1.9],
    cheek: [-10.5, -20.8, 4, 2.6],
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
    innerEar: [
      [-12.6, -28.8],
      [-11.8, -32.8],
      [-9.6, -29.6],
    ],
    chestPatch: [-6.8, -11.5, 2.6, 6, 0.2],
    muzzlePatch: [-14.3, -21.6, 2.7, 2.1],
    bodyStripes: [
      [[1.5, -13.5], [3.5, -6], 0.75],
      [[6, -14.5], [8.5, -7], 0.75],
      [[10.5, -11.5], [12.5, -5], 0.65],
    ],
    headStripes: [
      [[-9.5, -29.6], [-9.6, -27], 0.55],
      [[-7.2, -29.4], [-7.5, -27.2], 0.55],
      [[-4.8, -28.4], [-5.4, -26.4], 0.5],
    ],
    eye: [-12.6, -25.4],
    nose: [-16.2, -23.4],
    mouth: [-13.4, -20.6],
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
    legGap: [
      [-4.9, -8],
      [-5, 0],
    ],
  },
};

// Turning part of a pose about a pivot, by degrees that lift the front of
// a left-facing cat. The head turns about the top of the neck, carrying its
// face with it; the whole cat leans about its front paws.
const NECK_TOP: Vec2 = [-7, -20];
const FRONT_PAWS: Vec2 = [-5, 0];

const turnPose = (
  p: Pose,
  pivot: Vec2,
  degrees: number,
  whole: boolean,
): Pose => {
  if (!degrees) return p;
  const a = (degrees * Math.PI) / 180;
  const [cos, sin] = [Math.cos(a), Math.sin(a)];
  const turn = ([x, y]: Vec2): Vec2 => {
    const [dx, dy] = [x - pivot[0], y - pivot[1]];
    return [pivot[0] + dx * cos - dy * sin, pivot[1] + dx * sin + dy * cos];
  };
  const oval = ([x, y, rx, ry, rot = 0]: Oval): Oval => {
    const [tx, ty] = turn([x, y]);
    return [tx, ty, rx, ry, rot + a];
  };
  const limb = ([u, v, r]: Limb): Limb => [turn(u), turn(v), r];
  const head = {
    head: oval(p.head),
    muzzle: oval(p.muzzle),
    cheek: oval(p.cheek),
    ears: [p.ears[0].map(turn), p.ears[1].map(turn)] as [Vec2[], Vec2[]],
    innerEar: p.innerEar.map(turn),
    muzzlePatch: oval(p.muzzlePatch),
    headStripes: p.headStripes.map(limb),
    eye: turn(p.eye),
    nose: turn(p.nose),
    mouth: turn(p.mouth),
    whiskers: p.whiskers.map(([u, v]): [Vec2, Vec2] => [turn(u), turn(v)]),
  };
  if (!whole) return { ...p, ...head };
  return {
    ...p,
    ...head,
    haunch: oval(p.haunch),
    chest: oval(p.chest),
    neck: oval(p.neck),
    legs: p.legs.map(limb),
    tail: p.tail.map(turn),
    chestPatch: oval(p.chestPatch),
    bodyStripes: p.bodyStripes.map(limb),
    legGap: p.legGap.map(turn),
  };
};

// The front leg lifts and stretches out toward the side the cat faces.
const PAW_REACH: Limb = [[-7, -11], [-15, -9], 1.8];

const reachPaw = (p: Pose, paw: number): Pose => {
  if (!paw) return p;
  const [a, b, r] = p.legs[1];
  const mix = (u: Vec2, v: Vec2): Vec2 => [
    u[0] + (v[0] - u[0]) * paw,
    u[1] + (v[1] - u[1]) * paw,
  ];
  return {
    ...p,
    legs: [p.legs[0], [mix(a, PAW_REACH[0]), mix(b, PAW_REACH[1]), r]],
  };
};

// Short stripes across the tail, one per segment.
const tailStripes = (tail: Vec2[]): Mark[] =>
  tail.slice(0, -1).map((a, i) => {
    const b = tail[i + 1];
    const len = Math.hypot(b[0] - a[0], b[1] - a[1]);
    const [nx, ny] = [-(b[1] - a[1]) / len, (b[0] - a[0]) / len];
    const [cx, cy] = [(a[0] + b[0]) / 2, (a[1] + b[1]) / 2];
    return {
      shape: capsule(
        [cx - nx * 2.2, cy - ny * 2.2],
        [cx + nx * 2.2, cy + ny * 2.2],
        0.6,
      ),
      mat: "catStripe",
    };
  });

// The fisherman's ginger tabby with a white chest. Body, legs and neck are
// grown as one piece, and so are the head, muzzle and ears.
export const cat = ({
  x,
  y,
  pose,
  facing,
  look = 0,
  paw = 0,
  lean = 0,
}: CatProps): CatFigure => {
  const p = turnPose(
    reachPaw(turnPose(POSES[pose], NECK_TOP, look, false), paw),
    FRONT_PAWS,
    -lean,
    true,
  );
  const at = ([dx, dy]: Vec2): Vec2 => [x + dx, y + dy];
  const oval = ([ox, oy, rx, ry, rot]: Oval) =>
    ellipse(...at([ox, oy]), rx, ry, rot ?? 0);
  const limb = ([a, b, r]: Limb) => capsule(at(a), at(b), r, r * 0.92);
  const stripe = (l: Limb): Mark => ({ shape: limb(l), mat: "catStripe" });
  const tail = p.tail.map(at);
  const tailShapes = tail
    .slice(0, -1)
    .map((a, i) => capsule(a, tail[i + 1], 1.8 - 0.12 * i, 1.7 - 0.12 * i));
  const body: Part[] = [
    {
      shape: blend(tailShapes, 1.5),
      mat: "cat",
      bevel: 1.8,
      marks: tailStripes(tail),
    },
    {
      shape: blend(
        [
          oval(p.haunch),
          oval(p.chest),
          oval(p.neck),
          ...p.legs.map(limb),
          capsule(at([9, -3]), at([12, -4]), 2),
        ],
        3,
        0.35,
        11,
      ),
      mat: "cat",
      bevel: 4.5,
      marks: [
        { shape: oval(p.chestPatch), mat: "catWhite" },
        ...p.bodyStripes.map(stripe),
      ],
    },
    {
      shape: blend(
        [
          oval(p.head),
          oval(p.muzzle),
          oval(p.cheek),
          poly(p.ears[0].map(at)),
          poly(p.ears[1].map(at)),
        ],
        1.5,
        0.2,
        12,
      ),
      mat: "cat",
      bevel: 3.8,
      shadow: true,
      marks: [
        { shape: poly(p.innerEar.map(at)), mat: "skin" },
        { shape: oval(p.muzzlePatch), mat: "catWhite" },
        ...p.headStripes.map(stripe),
      ],
    },
  ];
  const [ex, ey] = at(p.eye);
  const features: Feature[] = [
    { x: ex, y: ey, c: C.ochre3 },
    { x: ex, y: ey, c: C.ink, dx: -1 },
    { x: at(p.nose)[0], y: at(p.nose)[1], c: C.skin1 },
  ];
  // The shadow between the front legs goes once a paw is lifted.
  const strokes: Stroke[] =
    paw < 0.3 ? [{ pts: p.legGap.map(at), steps: -1 }] : [];
  const lines = p.whiskers.map(([a, b]) => [at(a), at(b)] as const);
  const mouth = at(p.mouth);
  if (facing === "left")
    return { body, features, strokes, whiskers: lines, mouth };
  const fx = (v: Vec2): Vec2 => [2 * x - v[0], v[1]];
  return {
    body: flipParts(body, x),
    features: features.map((f) => ({
      ...f,
      x: 2 * x - f.x,
      dx: -(f.dx ?? 0),
    })),
    strokes: flipStrokes(strokes, x),
    whiskers: lines.map(([a, b]) => [fx(a), fx(b)] as const),
    mouth: fx(mouth),
  };
};
