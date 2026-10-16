import { Vector3 } from "three";
import { IDENTITY, Mapping, curveFrame, curvePoint, leaderS } from "./race";
import { ACT, worldClock } from "./timing";
import { keys, lerp, noise1, smootherstep, smoothstep } from "./lib/math";

export type Shot = { position: Vector3; target: Vector3; roll: number; fov: number };

const shot = (position: Vector3, target: Vector3, roll = 0, fov = 38): Shot => ({ position, target, roll, fov });

const blend = (a: Shot, b: Shot, k: number): Shot => ({
  position: a.position.clone().lerp(b.position, k),
  target: a.target.clone().lerp(b.target, k),
  roll: lerp(a.roll, b.roll, k),
  fov: lerp(a.fov, b.fov, k),
});

const _t = new Vector3();
const _n = new Vector3();

/** How out of control things feel, 0–1. Drives roll, shake and the post effects. */
export const chaos = (t: number) => smoothstep(17, 23.8, worldClock(t)) * (t < ACT.reveal[0] ? 1 : 0);

/** Behind the lone figure, looking down the line to the horizon; a slow push in. */
const opening = (t: number): Shot =>
  shot(new Vector3(1.55, 1.3, 9.4 - t * 0.25), new Vector3(1.2, 1.25, -40), 0, 30);

/**
 * Riding with the pack in the curve's own frame: behind the leader along the curve, out along
 * its normal, off to one side. As the curve stands up, "behind" becomes "below" and "out" becomes
 * "away from the wall", so the same rig turns from a chase into a climb.
 */
const ride = (t: number, m: Mapping = IDENTITY): Shot => {
  const w = worldClock(t);
  const s = leaderS(w);
  const head = curvePoint(s, m);
  curveFrame(s, m, _t, _n);
  const back = keys(w, [[7, 4.2], [11, 5.0], [14, 6.0], [17, 5.5], [20, 3.4], [24, 2.0]]);
  const out = keys(w, [[7, 1.0], [11, 1.8], [14, 3.6], [17, 5.0], [20, 9.0], [24, 14]]);
  const side = keys(w, [[7, 1.3], [12, 2.0], [17, 3.6], [24, 5.5]]) + noise1(w * 0.3, 3) * 0.3;
  // In the climb the camera aims below the pack, so the lit city spreads out beneath it.
  const ahead = keys(w, [[7, 4.5], [14, 4.0], [18, 2.0], [20, -3], [24, -7]]);
  const c = chaos(t);
  const shake = new Vector3(noise1(w * 9, 21), noise1(w * 9, 22), noise1(w * 9, 23)).multiplyScalar(0.12 * c * c);
  const position = head
    .clone()
    .addScaledVector(_t, -back)
    .addScaledVector(_n, out)
    .add(new Vector3(side, 0, 0))
    .add(shake);
  const lift = keys(w, [[7, -0.9], [12, -2.0], [16, -1.8], [20, -0.5], [24, 0]]);
  const target = head.clone().addScaledVector(_t, ahead).addScaledVector(_n, lift);
  const roll = noise1(w * 0.25, 9) * 0.025 + c * (0.22 * noise1(w * 0.9, 31) + 0.06 * noise1(w * 6, 32));
  return shot(position, target, roll, keys(w, [[7, 44], [18, 48], [24, 60]]));
};

/** The race camera up to the reveal; during the freeze it holds, closing in a touch. */
export const rideShot = (t: number): Shot => {
  const k = smootherstep(5.0, 8.5, t);
  const s = blend(opening(t), ride(t), k);
  // Arc over the figure's head instead of passing through it.
  s.position.y += Math.sin(Math.PI * k) * 1.4;
  const freeze = smoothstep(ACT.freeze[0], ACT.freeze[1], t);
  s.fov -= 5 * freeze;
  return s;
};

export const cameraAt = (t: number): Shot => rideShot(Math.min(t, ACT.reveal[0]));
