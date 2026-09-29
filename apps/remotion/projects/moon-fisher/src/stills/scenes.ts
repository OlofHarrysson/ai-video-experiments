import type { SceneSpec } from "./boatScene";
import { KEY_IMAGE } from "./keyImage";
import { haulTest } from "./motion";
import { DOZE, HAUL, TIP } from "./poses";

// Every scene is a spec, or a spec that changes with the frame.
export const SCENES = {
  key: KEY_IMAGE,
  doze: DOZE,
  haul: HAUL,
  tip: TIP,
  haulTest,
} satisfies Record<string, SceneSpec | ((frame: number) => SceneSpec)>;

export type SceneName = keyof typeof SCENES;

export const specAt = (name: SceneName, frame: number): SceneSpec => {
  const s = SCENES[name];
  return typeof s === "function" ? s(frame) : s;
};
