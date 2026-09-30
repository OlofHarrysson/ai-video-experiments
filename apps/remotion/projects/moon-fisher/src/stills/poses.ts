import type { SceneSpec } from "./boatScene";
import { KEY_IMAGE } from "./keyImage";

// The moon high in the sky over the bow. Its reflection lies below the boat,
// right where his line goes in.
export const SKY_MOON = { in: "sky", x: 173, y: 55, r: 11 } as const;
export const REFLECTION = [172, 443] as const;

// Setup: he has dozed off; the float bobs in the moon's reflection.
export const DOZE: SceneSpec = {
  camera: KEY_IMAGE.camera,
  moon: SKY_MOON,
  fisherman: "doze",
  reflection: REFLECTION,
  rod: { angle: -35, length: 70, bend: 3, line: { to: REFLECTION, slack: 8 } },
  float: REFLECTION,
};

// Turn: the line snags the reflection and he hauls on it.
export const HAUL: SceneSpec = {
  camera: KEY_IMAGE.camera,
  moon: SKY_MOON,
  fisherman: "haul",
  reflection: REFLECTION,
  rod: { angle: -52, length: 72, bend: 18, line: { to: REFLECTION, slack: 0 } },
  catchGlow: { at: REFLECTION, strength: 1 },
};

// Payoff: he tips the moon back into the sea while the cat watches.
export const TIP: SceneSpec = {
  camera: KEY_IMAGE.camera,
  moon: { in: "bucket" },
  fisherman: "tip",
  bucket: { at: "hands", tilt: 55, offset: [10, 4] },
  cat: { x: 198, y: 344, pose: "peer", facing: "left" },
};
