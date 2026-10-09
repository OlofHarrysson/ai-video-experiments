// Seconds, measured from the beginning of this eight-second silent take.
export const MOTION_TIMING = Object.freeze({
  duration: 8,
  raiseStart: 0.5,
  raiseEnd: 1.5,
  waveEnd: 3.0,
  lowerEnd: 3.7,
  turnRightStart: 4.1,
  turnRightEnd: 4.7,
  turnLeftStart: 5.2,
  turnLeftEnd: 6.0,
  returnStart: 6.5,
  returnEnd: 7.2,
});

const DEG = Math.PI / 180;
const REST_SHOULDER = -0.11;
const RAISED_SHOULDER = -103 * DEG;
const RAISED_ELBOW = -66 * DEG;
const WAVE_ANGLE = 22 * DEG;
const HEAD_TURN = 60 * DEG;

const smoothstep = (value) => {
  const x = Math.max(0, Math.min(1, value));
  return x * x * (3 - 2 * x);
};
const transition = (time, start, end) => smoothstep((time - start) / (end - start));
const lerp = (from, to, amount) => from + (to - from) * amount;
const euler = (x = 0, y = 0, z = 0) => ({ x, y, z });

// Two full waves: out/in, out/in, then settle at the raised center position.
// Smoothstep between the extrema makes the hand pause briefly at each reversal.
const WAVE_KEYS = [
  [1.5, 0],
  [1.6875, -WAVE_ANGLE],
  [2.0625, WAVE_ANGLE],
  [2.4375, -WAVE_ANGLE],
  [2.8125, WAVE_ANGLE],
  [3.0, 0],
];

function waveAt(time) {
  if (time <= WAVE_KEYS[0][0] || time >= MOTION_TIMING.waveEnd) return 0;
  for (let index = 1; index < WAVE_KEYS.length; index++) {
    const [end, next] = WAVE_KEYS[index];
    if (time <= end) {
      const [start, previous] = WAVE_KEYS[index - 1];
      return lerp(previous, next, transition(time, start, end));
    }
  }
  return 0;
}

/**
 * Pure, deterministic pose in radians, using the character's existing XYZ Eulers.
 * Apply `body` to body.rotation, `headPivot` to headPivot.rotation, and each
 * `arms[side].arm` / `.forearm` to the matching side in avatar.js's arms array.
 * Apply after the ordinary idle animation. The caller keeps speaking/energy off.
 *
 * Side -1 is the character's right arm (screen-left from the default camera).
 * Its upper arm points down local -Y and is 0.65 units long. A -103 degree
 * shoulder rotation lifts the elbow outward to about x=-1.28, y=1.63.
 * The -66 degree elbow bend puts the hand beside the head. The +/-22 degree
 * wave stays outside the face silhouette rather than sweeping across the eyes.
 * Out-of-range times hold the first/last pose; a non-finite time starts at rest.
 */
export function motionPose(t) {
  const time = Number.isFinite(t) ? Math.max(0, Math.min(MOTION_TIMING.duration, t)) : 0;
  const timing = MOTION_TIMING;
  const raised = transition(time, timing.raiseStart, timing.raiseEnd)
    * (1 - transition(time, timing.waveEnd, timing.lowerEnd));

  let yaw = HEAD_TURN * transition(time, timing.turnRightStart, timing.turnRightEnd);
  if (time >= timing.turnLeftStart) {
    yaw = lerp(HEAD_TURN, -HEAD_TURN, transition(time, timing.turnLeftStart, timing.turnLeftEnd));
  }
  if (time >= timing.returnStart) {
    yaw = lerp(-HEAD_TURN, 0, transition(time, timing.returnStart, timing.returnEnd));
  }

  return {
    body: euler(),
    headPivot: euler(0, yaw, 0),
    arms: {
      '-1': {
        arm: euler(-0.12 * raised, 0, lerp(REST_SHOULDER, RAISED_SHOULDER, raised)),
        forearm: euler(0.12 * raised, 0, raised * (RAISED_ELBOW + waveAt(time))),
      },
      '1': { arm: euler(0, 0, -REST_SHOULDER), forearm: euler() },
    },
  };
}
