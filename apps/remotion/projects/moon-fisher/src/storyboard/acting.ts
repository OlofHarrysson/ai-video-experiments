import type { Vec2 } from "../pixel/shapes";
import { clamp01, ease } from "../stills/motion";
import type { FishProps } from "../world/fish";
import { POSES, tweenPose, type Bone, type PoseDef } from "../world/fisherman";

// Movements within a shot, as functions of the seconds since it began.

// From 0 to 1 between two moments, easing in and out.
export const move = (t: number, from: number, to: number) =>
  ease(clamp01((t - from) / (to - from)));

// Nodding off: the head sinks first, then the body slumps and the hands
// settle in his lap. His eyes close on the way down.
const DOZING: Partial<Record<Bone, readonly [number, number]>> = {
  head: [0.2, 1.3],
  chest: [0.5, 1.7],
  spine: [0.6, 1.9],
};
export const DOZING_ARMS = [0.7, 2] as const;
export const dozingOff = (t: number): PoseDef =>
  tweenPose(
    POSES.fish,
    POSES.doze,
    (bone) => move(t, ...(DOZING[bone] ?? DOZING_ARMS)),
    t < 0.9 ? "open" : "closed",
  );

// Holding the bucket, he looks up at the sky and back down.
export const lookingUp = (
  t: number,
  up: readonly [number, number],
  down: readonly [number, number],
): PoseDef => {
  const k = move(t, ...up) - move(t, ...down);
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
