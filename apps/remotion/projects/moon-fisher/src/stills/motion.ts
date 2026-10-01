import { POSES, tweenPose, type Bone, type PoseDef } from "../world/fisherman";
import type { SceneSpec } from "./boatScene";
import { DOZE, FLOAT, HAUL, HOOKED } from "./poses";

export const clamp01 = (v: number) => Math.min(1, Math.max(0, v));
export const ease = (t: number) =>
  t < 0.5 ? 4 * t * t * t : 1 - (-2 * t + 2) ** 3 / 2;
const lerp = (a: number, b: number, t: number) => a + (b - a) * t;

const TUG = 24;
const REACT = 26;
// The startle leads with the head; the body follows and the arms come last.
const DELAY: Partial<Record<Bone, number>> = { head: 0, chest: 2, spine: 3 };
const ARMS = 4;
const DURATION: Partial<Record<Bone, number>> = { head: 6 };
const BODY = 12;

// How far a bone has come out of the doze, 0 to 1, `f` frames after he
// jolts awake.
export const startleProgress = (bone: Bone, f: number) =>
  ease(clamp01((f - (DELAY[bone] ?? ARMS)) / (DURATION[bone] ?? BODY)));

// Jolting awake from the doze into a pose of the haul.
export const startle = (f: number, into: PoseDef = POSES.haul): PoseDef =>
  tweenPose(
    POSES.doze,
    into,
    (bone) => startleProgress(bone, f),
    f >= 0 ? "wide" : "closed",
  );

// Leaning back into a pull on the rod: 0 at rest, 1 fully back.
export const leanBack = (pose: PoseDef, amount: number): PoseDef => ({
  ...pose,
  angles: {
    ...pose.angles,
    chest: (pose.angles.chest ?? 0) + 4 * amount,
    forearm: (pose.angles.forearm ?? 0) - 5 * amount,
  },
});

// Three seconds: dozing, a tug on the line, the startle, then hauling in a
// slow pulling rhythm while the catch glows brighter. Action poses hold for
// two frames.
export const haulTest = (frame: number): SceneSpec => {
  const f = Math.floor(frame / 2) * 2;
  const pulling = f >= 40 ? Math.sin(((f - 40) / 24) * 2 * Math.PI) : 0;
  const pose = leanBack(startle(f - REACT), pulling);
  const k = startleProgress("forearm", f - REACT);
  const tugged = f >= TUG;
  return {
    ...DOZE,
    fisherman: pose,
    rod: {
      angle: lerp(-37.7, -52, k),
      length: lerp(70, 72, k),
      bend: tugged ? lerp(10, 18, k) + 2 * pulling : 3,
      line: tugged ? { to: HOOKED, slack: 0 } : { to: FLOAT, slack: 8 },
    },
    float: tugged ? undefined : FLOAT,
    catchGlow: tugged
      ? { at: HOOKED, strength: clamp01((f - TUG) / 36) }
      : undefined,
    // The reflection drifts into the hook on the tug.
    reflection: [lerp(168, HOOKED[0], clamp01(f / TUG)), HOOKED[1]],
    moon: HAUL.moon,
  };
};
