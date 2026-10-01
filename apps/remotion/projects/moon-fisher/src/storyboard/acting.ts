import type { Vec2 } from "../pixel/shapes";
import { clamp01, ease } from "../stills/motion";
import type { FishProps } from "../world/fish";
import {
  POSES,
  tweenPose,
  type Bone,
  type Eyes,
  type PoseDef,
} from "../world/fisherman";

// Movements within a shot, as functions of the seconds since it began.

// From 0 to 1 between two moments, easing in and out.
export const move = (t: number, from: number, to: number) =>
  ease(clamp01((t - from) / (to - from)));

// Nodding off over the float, over three seconds: two heavy blinks, a nod
// and a jerk back awake, then his eyes close and his head starts to sink.
// Each bone moves from fishing (0) toward the doze (1).
const NODDING: Partial<Record<Bone, (t: number) => number>> = {
  head: (t) =>
    0.5 * move(t, 1.4, 1.8) - 0.4 * move(t, 1.8, 1.95) + 0.5 * move(t, 2.2, 3),
  chest: (t) => 0.15 * move(t, 2.2, 3),
};
const noddingEyes = (t: number): Eyes =>
  (t >= 0.6 && t < 0.9) || (t >= 1.2 && t < 1.5) || t >= 2.1
    ? "closed"
    : "open";
// When the first Z rises, in seconds since he began to nod off.
export const NODDED_OFF = 2.5;
export const noddingOff = (t: number): PoseDef =>
  tweenPose(
    POSES.fish,
    POSES.doze,
    (bone) => NODDING[bone]?.(t) ?? 0,
    noddingEyes(t),
  );

// Falling asleep, carrying on from the nod: the head drops the rest of the
// way, the body slumps and the hands settle in his lap.
export const DOZING_ARMS = [0.4, 1.6] as const;
const DOZING: Partial<Record<Bone, (t: number) => number>> = {
  head: (t) => 0.6 + 0.4 * move(t, 0, 0.8),
  chest: (t) => 0.15 + 0.85 * move(t, 0.2, 1.2),
  spine: (t) => move(t, 0.3, 1.4),
};
export const dozingOff = (t: number): PoseDef =>
  tweenPose(
    POSES.fish,
    POSES.doze,
    (bone) => DOZING[bone]?.(t) ?? move(t, ...DOZING_ARMS),
    "closed",
  );

// Hauling: thrown back with the rod raised as he heaves (1), leaning in
// with it lowered to take up the line (0). The rod follows his hands.
export const hauling = (heave: number) => {
  const pose = tweenPose(POSES.reel, POSES.heave, () => heave, "wide");
  return { pose, rod: (pose.angles.hand ?? 0) + 17, bend: 12 + 16 * heave };
};

// Over each beat he lowers the rod, then heaves it back up to arrive thrown
// back on the next beat.
export const heaveOn = (t: number, beat: number) => {
  const p = (t % beat) / beat;
  return p < 0.65 ? 1 - move(p, 0, 0.65) : move(p, 0.65, 1);
};

// A dying light: a few quick dips, on twos, as it fades.
const FLICKERS = [0.5, 1.25, 1.42, 2.2, 2.62];
export const flicker = (t: number) =>
  FLICKERS.some((f) => t >= f && t < f + 0.09) ? 0.7 : 1;

// Holding the bucket, he looks up at the sky, and back down if `down` says
// when.
export const lookingUp = (
  t: number,
  up: readonly [number, number],
  down?: readonly [number, number],
): PoseDef => {
  const k = move(t, ...up) - (down ? move(t, ...down) : 0);
  return {
    ...tweenPose(POSES.holdBucket, POSES.lookUp, () => k, "open"),
    farHandOnProp: POSES.lookUp.farHandOnProp,
  };
};

export type Leap = {
  from: Vec2;
  to: Vec2;
  // How far the arc rises above the straight line between its ends.
  height: number;
  start: number;
  duration: number;
  size: number;
};

// A fish arcing out of the water: where it is at time `t`, heading along
// its arc, or null while it is not in the air.
export const leaping = (l: Leap, t: number): FishProps | null => {
  const u = (t - l.start) / l.duration;
  if (u < 0 || u > 1) return null;
  const [dx, dy] = [l.to[0] - l.from[0], l.to[1] - l.from[1]];
  const rise = 4 * l.height;
  return {
    at: [l.from[0] + dx * u, l.from[1] + dy * u - rise * u * (1 - u)],
    angle: (Math.atan2(dy - rise * (1 - 2 * u), dx) * 180) / Math.PI,
    size: l.size,
  };
};

// The splashes a leap makes where it leaves the water and, unless it lands
// somewhere dry, where it falls back in.
export const leapSplashes = (
  l: Leap,
  t: number,
  size: number,
  backIn = true,
) => [
  ...(Math.abs(t - l.start) < 0.2 ? [{ at: l.from, size }] : []),
  ...(backIn && Math.abs(t - l.start - l.duration) < 0.25
    ? [{ at: l.to, size }]
    : []),
];
