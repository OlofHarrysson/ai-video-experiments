import { drawStrokes } from "../pixel/detail";
import {
  drawLit,
  type Light,
  type LitScene,
  type LitStyle,
  type Part,
} from "../pixel/lit";
import { C } from "../pixel/palette";
import { IDENTITY, Pix, type Camera } from "../pixel/pix";
import { ellipse, type Vec2 } from "../pixel/shapes";
import {
  BOAT,
  boatHull,
  boatInterior,
  drawPlankSeams,
  drawRibs,
} from "../world/boat";
import { bucket, moonCenter, type BucketProps } from "../world/bucket";
import { cat, type CatProps } from "../world/cat";
import { drawSplash, fishParts, type FishProps } from "../world/fish";
import {
  fisherman,
  type Feature,
  type FishermanPose,
  type PoseDef,
} from "../world/fisherman";
import { drawHalo, drawShaft, reflectWater } from "../world/glow";
import { moonParts } from "../world/moon";
import { drawLine, drawRod } from "../world/rod";
import {
  drawMoonPath,
  drawMoonReflection,
  drawRipple,
  drawSea,
} from "../world/sea";
import { drawMilkyWay, drawSky, drawStars, type Band } from "../world/sky";

export const HORIZON = 320;
// Where the fisherman sits on the thwart.
export const SEAT: Vec2 = [100, 358];
// Ambient motion holds each pose for three frames: eight steps a second at
// 24 fps.
export const HOLD = 3;
export const STYLE: LitStyle = { dither: 0, outline: true, cleanup: true };
// A shivering moon jumps sideways every two frames, by these fractions of
// its shiver.
const SHIVER = [1, -1, 0.5, -1, 1, -0.5];

type SkyMoon = { x: number; y: number; r: number };

export type SceneSpec = {
  camera: Camera;
  // Where the moon is: in the sky (in design-frame units, shivering by
  // `shiver` of them), caught in the bucket, loose in the world (world
  // units; `waterline` hides the part still under the sea), or gone. A sky
  // moon below the horizon is hidden by the sea.
  moon:
    | (SkyMoon & { in: "sky"; shiver?: number })
    | { in: "bucket" }
    | { in: "world"; x: number; y: number; r: number; waterline?: number }
    | { in: "gone" };
  // How brightly a caught moon still shines, 0 to 1.
  glow?: number;
  // The moon in the sky sinking below the horizon as the caught one comes
  // out of the water, in design-frame units.
  setting?: SkyMoon;
  // Where the moon's reflection lies on the water, in world units, and how
  // hard it shakes, 0 to 1.
  reflection?: Vec2;
  wobble?: number;
  fisherman: FishermanPose | PoseDef;
  // A bucket standing on his knees, or held in his hands and tipped.
  bucket?:
    | { at: "knees"; x: number; rimY: number }
    | { at: "hands"; tilt: number; offset: Vec2 };
  rod?: {
    angle: number;
    length: number;
    bend: number;
    line: { to: Vec2; slack: number };
  };
  cat?: CatProps;
  // A rod set aside, as a straight line between two world points.
  leaningRod?: [Vec2, Vec2];
  // The float, bobbing where the line meets the water, and the rings
  // spreading from it.
  float?: Vec2;
  ripple?: { at: Vec2; radius: number };
  // Something bright caught on the hook, glowing in the water; strength
  // from 0 to 1.
  catchGlow?: { at: Vec2; strength: number };
  splash?: { at: Vec2; size: number };
  fish?: FishProps[];
  // Light spreading under the sea, from 0 to 1.
  seaGlow?: { at: Vec2; radius: number; strength: number };
};

const DARK_SKY: Band[] = [
  [C.ink, 0],
  [C.night1, 0.25],
  [C.night2, 0.55],
  [C.night3, 0.8],
  [C.night4, 1],
];
const MOONLIT_SKY: Band[] = [
  [C.night1, 0],
  [C.night2, 0.3],
  [C.night3, 0.62],
  [C.night4, 0.86],
  [C.night5, 1],
];
const SEA: Band[] = [
  [C.night3, 0],
  [C.night2, 0.25],
  [C.night1, 0.7],
  [C.ink, 1],
];

const drawFeatures = (pix: Pix, features: Feature[]) => {
  for (const f of features) {
    pix.set(pix.px(f.x) + (f.dx ?? 0), pix.py(f.y) + (f.dy ?? 0), f.c);
  }
};

// A red-and-white float, a little over two world units tall.
const floatParts = ([x, y]: Vec2): Part[] => [
  { shape: ellipse(x, y, 1.1, 1.3), mat: "beard", lift: 0.5 },
  { shape: ellipse(x, y - 1.4, 1, 1.1), mat: "cat", lift: 0.45 },
];

// The boat on the night sea, with the fisherman, the cat and whatever the
// moon is doing. Every shot of the film is one of these with its own spec;
// `frame` animates the ambient life, and frame 0 is the still.
export const drawBoatScene = (pix: Pix, spec: SceneSpec, frame = 0): void => {
  const step = Math.floor(frame / HOLD);
  // The boat rises and settles by one pixel on a two-second swell.
  const bob = step % 16 < 8 ? 0 : 1;
  const camera = { ...spec.camera, sy: spec.camera.sy + bob / pix.k };
  pix.cam = camera;
  const horizon = pix.screenY(HORIZON);
  const skyMoon = spec.moon.in === "sky" ? spec.moon : null;
  const looseMoon = spec.moon.in === "world" ? spec.moon : null;
  const glow = spec.glow ?? 1;

  const man = fisherman({
    x: SEAT[0],
    y: SEAT[1],
    pose: spec.fisherman,
    facing: "right",
  });
  const inBucket = spec.moon.in === "bucket";
  const pail: BucketProps | null = !spec.bucket
    ? null
    : spec.bucket.at === "knees"
      ? { x: spec.bucket.x, rimY: spec.bucket.rimY, moon: inBucket }
      : {
          x: man.grip[0] + spec.bucket.offset[0],
          rimY: man.grip[1] + spec.bucket.offset[1],
          moon: inBucket,
          tilt: spec.bucket.tilt,
        };
  const caught = pail?.moon
    ? moonCenter(pail)
    : looseMoon
      ? ([looseMoon.x, looseMoon.y] as const)
      : null;

  // Moonlight from the sky comes from behind the boat and rims everything;
  // a caught or loose moon lights the boat from where it is.
  const lights: Light[] = [];
  if (skyMoon) {
    const fx = (SEAT[0] + 20 - camera.x) * camera.zoom + camera.sx;
    const fy = (SEAT[1] - 40 - camera.y) * camera.zoom + camera.sy;
    const d = Math.hypot(skyMoon.x - fx, skyMoon.y - fy);
    lights.push(
      {
        kind: "dir",
        dir: [(skyMoon.x - fx) / d, (skyMoon.y - fy) / d, -0.25],
        strength: 1.3,
        wrap: 0.35,
      },
      { kind: "dir", dir: [0, 1, 0.5], strength: 0.08 },
    );
  } else if (caught) {
    lights.push(
      {
        kind: "point",
        x: caught[0],
        y: caught[1],
        z: 3,
        strength: 1.8 * glow,
        radius: 120,
        falloff: 1.1,
        wrap: 0.3,
        minElev: inBucket ? -0.75 : -1.1,
        soft: 0.2,
      },
      { kind: "dir", dir: [0, -1, 0.7], strength: 0.1 },
    );
  } else {
    lights.push({ kind: "dir", dir: [0, -1, 0.6], strength: 0.14 });
  }
  const scene: LitScene = { lights, ambient: skyMoon ? 0.07 : 0.04 };

  drawSky(pix, { horizon, bands: skyMoon ? MOONLIT_SKY : DARK_SKY, seam: 0.5 });
  if (!skyMoon) drawMilkyWay(pix, { seed: 7, horizon, strength: 1.3 });
  drawStars(pix, {
    seed: "key-stars",
    count: 150,
    horizon,
    strength: skyMoon ? 0.6 : 1,
    step,
  });
  drawSea(pix, {
    horizon,
    bands: SEA,
    seam: 0.35,
    seed: "key-sea",
    swell: skyMoon ? 0.45 : 0.25,
  });
  const seaRow = Math.max(0, Math.floor(horizon * pix.k) + 1);
  if (spec.seaGlow) {
    const { at, radius, strength } = spec.seaGlow;
    drawHalo(pix, {
      x: at[0],
      y: at[1],
      radius,
      steps: 4 * strength,
      fromRow: seaRow,
    });
  }

  // A moon in the sky and its halo; the sea hides whatever has sunk below
  // the horizon.
  const drawSkyMoon = ({ x, y, r }: SkyMoon) => {
    pix.cam = IDENTITY;
    drawHalo(pix, { x, y, radius: r * 5, steps: 3 });
    drawLit(
      pix,
      moonParts({ x, y, radius: r, waterline: horizon }),
      scene,
      STYLE,
    );
    pix.cam = camera;
  };
  if (spec.setting) drawSkyMoon(spec.setting);
  if (skyMoon) {
    const shiver =
      (skyMoon.shiver ?? 0) * SHIVER[Math.floor(frame / 2) % SHIVER.length];
    drawSkyMoon({ ...skyMoon, x: skyMoon.x + shiver });
    pix.cam = IDENTITY;
    drawMoonPath(pix, {
      x: skyMoon.x,
      horizon,
      halfWidth: 38,
      seed: "moon-path",
      step,
    });
    pix.cam = camera;
    if (spec.reflection) {
      drawMoonReflection(pix, {
        x: spec.reflection[0],
        y: spec.reflection[1],
        r: 7.5,
        seed: "moon-reflection",
        step,
        wobble: spec.wobble,
      });
    }
  } else if (caught) {
    if (inBucket) {
      drawShaft(pix, {
        x: caught[0],
        y: caught[1] - 6,
        spread: 0.3,
        length: 200,
        steps: 2.2 * glow,
      });
    }
    const breath = Math.sin((2 * Math.PI * step) / 16);
    drawHalo(pix, {
      x: caught[0],
      y: caught[1],
      radius: (46 + 2 * breath) * (0.5 + 0.5 * glow),
      steps: (3.2 + 0.25 * breath) * glow,
    });
  }

  pix.drawingObjects = true;
  if (spec.leaningRod) {
    const [[ax, ay], [bx, by]] = spec.leaningRod;
    pix.line(ax, ay, bx, by, C.umber2);
  }
  drawLit(pix, boatInterior(BOAT), scene, STYLE);
  drawRibs(pix, BOAT);
  drawLit(pix, man.body, scene, STYLE);
  drawStrokes(pix, man.strokes);
  const kitty = spec.cat ? cat(spec.cat) : null;
  if (kitty) {
    drawLit(pix, kitty.body, scene, STYLE);
    drawStrokes(pix, kitty.strokes);
  }
  if (pail) drawLit(pix, bucket({ ...pail, glow }), scene, STYLE);
  const tip = spec.rod
    ? drawRod(pix, {
        grip: man.grip,
        angle: spec.rod.angle,
        length: spec.rod.length,
        bend: spec.rod.bend,
      })
    : null;
  drawLit(pix, man.front, scene, STYLE);
  drawLit(pix, boatHull(BOAT), scene, STYLE);
  drawPlankSeams(pix, BOAT);
  if (spec.rod && tip)
    drawLine(pix, tip, spec.rod.line.to, spec.rod.line.slack);
  drawFeatures(pix, man.features);
  if (kitty) {
    // The cat blinks once in the loop: its eye closes to a line of fur.
    const [eye, pupil, nose] = kitty.features;
    const blinking = step === 21 || step === 22;
    drawFeatures(pix, [
      ...(blinking ? [{ ...eye, c: C.umber1 }] : [eye, pupil]),
      nose,
    ]);
    for (const [a, b] of kitty.whiskers)
      pix.line(a[0], a[1], b[0], b[1], C.silver2);
  }
  pix.drawingObjects = false;

  reflectWater(pix, { waterline: BOAT.waterline, seed: "key-water", step });
  // Things out on the water in front of the boat are drawn over the
  // reflections.
  if (looseMoon) {
    drawLit(
      pix,
      moonParts({
        x: looseMoon.x,
        y: looseMoon.y,
        radius: looseMoon.r,
        glow,
        waterline: looseMoon.waterline,
      }),
      scene,
      STYLE,
    );
  }
  for (const f of spec.fish ?? []) drawLit(pix, fishParts(f), scene, STYLE);
  if (spec.ripple) {
    drawRipple(pix, {
      x: spec.ripple.at[0],
      y: spec.ripple.at[1],
      radius: spec.ripple.radius,
      seed: "ripple",
    });
  }
  if (spec.float) {
    // The float rises and dips a little with the ripples.
    const dip = step % 6 < 3 ? 0 : 0.8;
    drawLit(
      pix,
      floatParts([spec.float[0], spec.float[1] + dip]),
      scene,
      STYLE,
    );
  }
  if (spec.splash) {
    drawSplash(pix, {
      at: spec.splash.at,
      size: spec.splash.size,
      seed: `splash-${step}`,
    });
  }
  if (spec.catchGlow) {
    const { at, strength } = spec.catchGlow;
    drawHalo(pix, {
      x: at[0],
      y: at[1],
      radius: 8 + 10 * strength,
      steps: 1 + 2.5 * strength,
    });
  }
};
