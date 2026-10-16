import { Vector3 } from "three";
import { Shot, rideShot } from "./camera";
import { IDENTITY, Mapping, height, leaderS } from "./race";
import { ACT, worldClock } from "./timing";
import { lerp, smootherstep } from "./lib/math";

// The turn. The camera rockets back to a side view of the whole race as a chart. The chart keeps
// refitting itself to the head: it holds while the head flies off the top, then rescales, and
// yesterday's wall drops into the floor. Each refit comes sooner than the last.

/** Refit times. Intervals shrink, so the refits run together into one accelerating collapse. */
export const REFITS = [25.0, 27.0, 28.5, 29.5, 30.1, 30.5, 30.75, 30.9, 31.0];

/** The chart box the camera frames in the side view, in world units. */
export const BOX = { w: 150, h: 84 };

/** Chart time the view is fitted to: it lags the head, then catches up near each refit's end. */
export const fitTime = (t: number) => {
  if (t <= REFITS[0]) return t;
  for (let i = 0; i < REFITS.length - 1; i++) {
    const a = REFITS[i];
    const b = REFITS[i + 1];
    if (t < b) return a + (b - a) * smootherstep(0.55, 1, (t - a) / (b - a));
  }
  // After the last refit the view follows continuously: the L.
  return t;
};

const logLerp = (a: number, b: number, k: number) => Math.exp(lerp(Math.log(a), Math.log(b), k));

export const revealMapping = (t: number): Mapping => {
  const tau = fitTime(t);
  const s = leaderS(worldClock(tau));
  const box: Mapping = { sx: BOX.w / s, sy: BOX.h / height(s), sl: lerp(0.1, 0.03, smootherstep(27, 30, t)), x0: 0 };
  const k = smootherstep(ACT.reveal[0], ACT.reveal[0] + 1.2, t);
  return {
    sx: logLerp(IDENTITY.sx, box.sx, k),
    sy: logLerp(IDENTITY.sy, box.sy, k),
    sl: lerp(1, box.sl, k),
    x0: 0,
  };
};

/** From the frozen climb, straight back and out to a side view of the chart. */
export const revealCamera = (t: number): Shot => {
  const from = rideShot(ACT.reveal[0]);
  const center = new Vector3(0, BOX.h * 0.42, -BOX.w * 0.5);
  const dist = ((BOX.h * 0.5) / Math.tan(((36 / 2) * Math.PI) / 180)) * 1.3;
  const side: Shot = {
    position: center.clone().add(new Vector3(dist, -14, 4)),
    target: center.clone().add(new Vector3(0, 0, -2)),
    roll: 0,
    fov: 36,
  };
  const k = smootherstep(ACT.reveal[0], ACT.reveal[0] + 1.25, t);
  // A slow push toward the corner of the L before the cut.
  const push = smootherstep(30.5, ACT.reveal[1], t);
  const corner = new Vector3(0, 6, -BOX.w + 8);
  const pos = from.position.clone().lerp(side.position, k);
  const tgt = from.target.clone().lerp(side.target, k);
  pos.lerp(corner.clone().add(new Vector3(dist * 0.55, 10, 22)), push * 0.6);
  tgt.lerp(corner, push * 0.5);
  return { position: pos, target: tgt, roll: lerp(from.roll, 0, k), fov: lerp(from.fov, 36, k) };
};
