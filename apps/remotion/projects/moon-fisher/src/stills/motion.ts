import { POSES, tweenPose, type Bone } from "../world/fisherman";
import type { SceneSpec } from "./boatScene";
import { DOZE, FLOAT, HAUL, REFLECTION } from "./poses";

const clamp01 = (v: number) => Math.min(1, Math.max(0, v));
const ease = (t: number) =>
  t < 0.5 ? 4 * t * t * t : 1 - (-2 * t + 2) ** 3 / 2;
const lerp = (a: number, b: number, t: number) => a + (b - a) * t;

const TUG = 24;
const REACT = 26;
// The startle leads with the head; the body follows and the arms come last.
const DELAY: Partial<Record<Bone, number>> = { head: 0, chest: 2, spine: 3 };
const ARMS = 4;
const DURATION: Partial<Record<Bone, number>> = { head: 6 };
const BODY = 12;

// Three seconds: dozing, a tug on the line, the startle, then hauling in a
// slow pulling rhythm while the catch glows brighter. Action poses hold for
// two frames.
export const haulTest = (frame: number): SceneSpec => {
  const f = Math.floor(frame / 2) * 2;
  const t = (bone: Bone) =>
    ease(
      clamp01((f - REACT - (DELAY[bone] ?? ARMS)) / (DURATION[bone] ?? BODY)),
    );
  const pose = tweenPose(
    POSES.doze,
    POSES.haul,
    t,
    f >= REACT ? "wide" : "closed",
  );
  const pulling = f >= 40 ? Math.sin(((f - 40) / 24) * 2 * Math.PI) : 0;
  pose.angles.chest = (pose.angles.chest ?? 0) + 4 * pulling;
  pose.angles.forearm = (pose.angles.forearm ?? 0) - 5 * pulling;
  const k = t("forearm");
  const tugged = f >= TUG;
  return {
    ...DOZE,
    fisherman: pose,
    rod: {
      angle: lerp(-35, -52, k),
      length: lerp(70, 72, k),
      bend: tugged ? lerp(10, 18, k) + 2 * pulling : 3,
      line: tugged ? { to: REFLECTION, slack: 0 } : { to: FLOAT, slack: 8 },
    },
    float: tugged ? undefined : FLOAT,
    catchGlow: tugged
      ? { at: REFLECTION, strength: clamp01((f - TUG) / 36) }
      : undefined,
    moon: HAUL.moon,
  };
};
