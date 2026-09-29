import type { SceneSpec } from "./boatScene";

// The style frame: the moon glowing in the bucket, lighting the fisherman's
// face and the cat's from below while the sky stands empty.
export const KEY_IMAGE: SceneSpec = {
  camera: { x: 150, y: 330, zoom: 1.5, sx: 140, sy: 255 },
  moon: { in: "bucket" },
  fisherman: "holdBucket",
  bucket: { at: "knees", x: 148, rimY: 326 },
  cat: { x: 198, y: 344, pose: "peer", facing: "left" },
  // His rod leans against the thwart behind him, out of the frame.
  leaningRod: [
    [84, 352],
    [20, 236],
  ],
};
