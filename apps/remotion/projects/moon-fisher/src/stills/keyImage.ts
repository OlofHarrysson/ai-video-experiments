import { drawStrokes } from "../pixel/detail";
import { drawLit, type LitScene, type LitStyle } from "../pixel/lit";
import { C } from "../pixel/palette";
import { Pix, type Camera } from "../pixel/pix";
import {
  BOAT,
  boatHull,
  boatInterior,
  drawPlankSeams,
  drawRibs,
} from "../world/boat";
import { bucket, moonCenter } from "../world/bucket";
import { cat } from "../world/cat";
import { fisherman, type Feature } from "../world/fisherman";
import { drawHalo, drawShaft, reflectWater } from "../world/glow";
import { drawSea } from "../world/sea";
import { drawMilkyWay, drawSky, drawStars } from "../world/sky";

const HORIZON = 320;
const BUCKET = { x: 148, rimY: 326, moon: true };
const [MOON_X, MOON_Y] = moonCenter(BUCKET);

// A medium shot: the bucket a little above the middle of the frame.
const CAMERA: Camera = { x: 150, y: 330, zoom: 1.5, sx: 140, sy: 255 };

// The moon, caught in the bucket, is the only light left in the world.
const SCENE: LitScene = {
  lights: [
    {
      kind: "point",
      x: MOON_X,
      y: MOON_Y,
      z: 3,
      strength: 1.8,
      radius: 120,
      falloff: 1.1,
      wrap: 0.3,
      minElev: -0.75,
      soft: 0.2,
    },
    { kind: "dir", dir: [0, -1, 0.7], strength: 0.1 },
  ],
  ambient: 0.04,
};

export const STYLE: LitStyle = { dither: 0, outline: true, cleanup: true };

const drawFeatures = (pix: Pix, features: Feature[]) => {
  for (const f of features) {
    pix.set(pix.px(f.x) + (f.dx ?? 0), pix.py(f.y) + (f.dy ?? 0), f.c);
  }
};

// Ambient motion holds each pose for three frames: eight steps a second at
// 24 fps.
export const HOLD = 3;

// The style frame: the moon glowing in the bucket, lighting the fisherman's
// face and the cat's from below while the sky stands empty. `frame` animates
// the ambient life of the shot; frame 0 is the still.
export const drawKeyImage = (pix: Pix, frame = 0): void => {
  const step = Math.floor(frame / HOLD);
  // The boat rises and settles by one pixel on a two-second swell.
  const bob = step % 16 < 8 ? 0 : 1;
  pix.cam = { ...CAMERA, sy: CAMERA.sy + bob / pix.k };
  const horizon = pix.screenY(HORIZON);
  drawSky(pix, {
    horizon,
    bands: [
      [C.ink, 0],
      [C.night1, 0.25],
      [C.night2, 0.55],
      [C.night3, 0.8],
      [C.night4, 1],
    ],
    seam: 0.5,
  });
  drawMilkyWay(pix, { seed: 7, horizon, strength: 1.3 });
  drawStars(pix, { seed: "key-stars", count: 150, horizon, strength: 1, step });
  drawSea(pix, {
    horizon,
    bands: [
      [C.night3, 0],
      [C.night2, 0.25],
      [C.night1, 0.7],
      [C.ink, 1],
    ],
    seam: 0.35,
    seed: "key-sea",
    swell: 0.25,
  });
  drawShaft(pix, {
    x: MOON_X,
    y: MOON_Y - 6,
    spread: 0.3,
    length: 200,
    steps: 2.2,
  });
  const breath = Math.sin((2 * Math.PI * step) / 16);
  drawHalo(pix, {
    x: MOON_X,
    y: MOON_Y,
    radius: 46 + 2 * breath,
    steps: 3.2 + 0.25 * breath,
  });

  pix.drawingObjects = true;
  // His rod leans against the thwart behind him, out of the frame.
  pix.line(84, 352, 20, 236, C.umber2);

  drawLit(pix, boatInterior(BOAT), SCENE, STYLE);
  drawRibs(pix, BOAT);
  const man = fisherman({
    x: 100,
    y: 358,
    pose: "holdBucket",
    facing: "right",
  });
  const kitty = cat({ x: 198, y: 344, pose: "peer", facing: "left" });
  drawLit(pix, man.body, SCENE, STYLE);
  drawStrokes(pix, man.strokes);
  drawLit(pix, kitty.body, SCENE, STYLE);
  drawStrokes(pix, kitty.strokes);
  drawLit(pix, bucket(BUCKET), SCENE, STYLE);
  drawLit(pix, man.front, SCENE, STYLE);
  drawLit(pix, boatHull(BOAT), SCENE, STYLE);
  drawPlankSeams(pix, BOAT);
  // The cat blinks once in the loop: its eye closes to a line of fur.
  const [eye, pupil, nose] = kitty.features;
  const blinking = step === 21 || step === 22;
  drawFeatures(pix, [
    ...man.features,
    ...(blinking ? [{ ...eye, c: C.umber1 }] : [eye, pupil]),
    nose,
  ]);
  for (const [a, b] of kitty.whiskers)
    pix.line(a[0], a[1], b[0], b[1], C.silver2);
  pix.drawingObjects = false;

  reflectWater(pix, { waterline: BOAT.waterline, seed: "key-water", step });
};
