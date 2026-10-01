import { onScreen, type Camera } from "../pixel/pix";
import type { SceneSpec } from "./boatScene";
import { KEY_IMAGE } from "./keyImage";

// His line hangs straight down from the rod tip to the float. The moon's
// reflection starts out beside the float and, as the night wears on,
// wanders into his hook.
export const FLOAT = [180, 445] as const;
export const REFLECTION = [156, 443] as const;
export const HOOKED = [174, 443] as const;

// The moon high in the sky, standing over the world column its reflection
// lies in.
export const skyMoon = (camera: Camera, column: number, y = 55) =>
  ({ in: "sky", x: onScreen(camera, [column, 0])[0], y, r: 11 }) as const;

// Setup: he has dozed off while the reflection drifts toward his float.
export const DOZE: SceneSpec = {
  camera: KEY_IMAGE.camera,
  moon: skyMoon(KEY_IMAGE.camera, 166),
  fisherman: "doze",
  reflection: [166, REFLECTION[1]],
  rod: { angle: -37.7, length: 70, bend: 3, line: { to: FLOAT, slack: 8 } },
  float: FLOAT,
};

// Turn: the reflection has wandered into his hook, and he hauls on it.
export const HAUL: SceneSpec = {
  camera: KEY_IMAGE.camera,
  moon: skyMoon(KEY_IMAGE.camera, HOOKED[0]),
  fisherman: "haul",
  reflection: HOOKED,
  rod: { angle: -52, length: 72, bend: 18, line: { to: HOOKED, slack: 0 } },
  catchGlow: { at: HOOKED, strength: 1 },
};

// Payoff: he tips the moon back into the sea while the cat watches.
export const TIP: SceneSpec = {
  camera: KEY_IMAGE.camera,
  moon: { in: "bucket" },
  fisherman: "tip",
  bucket: { at: "hands", tilt: 55, offset: [10, 4] },
  cat: { x: 198, y: 344, pose: "peer", facing: "left" },
};
