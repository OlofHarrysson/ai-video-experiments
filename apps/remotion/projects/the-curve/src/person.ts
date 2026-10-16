import { Vector3 } from "three";
import { Shot } from "./camera";
import { Pose } from "./world/Figure";
import { ACT, worldClock } from "./timing";
import { easeInOutCubic, keys, lerp, noise1, smoothstep, spline } from "./lib/math";

// The person the film happens to. They stand where the race began, try to follow it, turn,
// step back and finally look up at a wall they will never reach.

export const PERSON = new Vector3(-0.45, 0, 0);

type Keys = ReadonlyArray<readonly [number, number]>;
const ease = (t: number, k: Keys) => keys(t, k, easeInOutCubic);

// Head turns follow each rival as it streaks past: right, left, right… (positive yaw = left).
const HEAD_YAW: Keys = [
  [6.6, 0], [7.0, -0.75], [7.7, -0.1],
  [7.9, 0.75], [8.6, 0.05],
  [9.5, 0], [9.8, -0.6], [10.3, 0],
  [10.5, 0.6], [11.0, 0],
  [11.4, -0.55], [11.8, 0],
  [16.6, 0], [16.9, 0.45], [17.3, -0.4], [17.7, 0.3], [18.1, -0.25], [18.6, 0.2],
  [19.4, -0.18], [20.2, 0.15], [21.2, -0.12], [22.4, 0.08], [24, 0],
];

// Turning round to see what is coming from behind, then back.
const YAW: Keys = [[12.0, 0], [13.3, -2.5], [14.3, -2.5], [15.5, 0]];

// Two steps back.
const STEP: Keys = [[15.6, 0], [16.3, 0.45], [20.4, 0.45], [21.0, 0.8]];

// Looking up at the wall, leaning back a little.
const PITCH: Keys = [[17.5, 0], [21, 0.5], [24, 0.82]];
const LEAN: Keys = [[18, 0], [24, 0.07]];

export const personPose = (t: number): Pose => {
  const w = Math.min(worldClock(t), ACT.freeze[0]);
  const step = ease(w, STEP);
  const stepping = (w > 15.6 && w < 16.3) || (w > 20.4 && w < 21.0);
  return {
    yaw: ease(w, YAW),
    headYaw: ease(w, HEAD_YAW),
    headPitch: ease(w, PITCH),
    lean: ease(w, LEAN),
    step,
    bob: stepping ? -0.025 * Math.sin(Math.PI * ((w * 2) % 1)) : 0,
  };
};

// ── The camera stays with the person ───────────────────────────────────────
// Polar around the person: angle 0 is directly behind them (+Z), positive swings to their right.
// The last stretch whips round faster and faster and ends behind them for the freeze.
const ANGLE: Keys = [
  [0, 0.21], [5.5, 0.21], [8, 0.35], [11, 1.2], [14, 2.4], [17, 3.6], [20, 5.6], [22.5, 8.4], [24, 12.6],
];
const RADIUS: Keys = [[0, 9.6], [5.5, 9.0], [8, 4.0], [11, 3.6], [14, 4.2], [17, 4.0], [20, 3.5], [24, 3.0]];
const HEIGHT: Keys = [[0, 1.3], [5.5, 1.3], [8, 1.5], [11, 1.2], [14, 0.9], [17, 0.8], [20, 0.6], [24, 0.42]];
const FOV: Keys = [[0, 30], [5.5, 30], [8, 40], [14, 46], [20, 54], [24, 62]];

/** How out of control things feel, 0–1. */
export const overwhelm = (t: number) => smoothstep(17, 23.8, worldClock(t)) * (t < ACT.reveal[0] ? 1 : 0);

export const personShot = (t: number): Shot => {
  const w = worldClock(t);
  // Splines carry speed through the keys, so the orbit builds instead of lurching.
  const angle = spline(w, ANGLE);
  const radius = spline(w, RADIUS);
  const height = spline(w, HEIGHT);
  const c = overwhelm(t);
  const position = PERSON.clone().add(new Vector3(radius * Math.sin(angle), height, radius * Math.cos(angle)));
  // Always keep them in shot: from behind we aim a little past them toward the race (more in
  // the climb, so the wall rises over them); from the side or front we look at them.
  const behind = (1 + Math.cos(angle)) / 2;
  const head = PERSON.clone().add(new Vector3(0, 1.4, 0));
  const far = new Vector3(1.2, lerp(1.25, 26, smoothstep(17, 23, w)), -40);
  // The aim never strays more than about a third of the camera's distance from them, so they
  // stay anchored in frame while everything else moves.
  const toward = far.clone().sub(head).normalize();
  const target = head.clone().addScaledVector(toward, radius * 0.42 * (0.4 + 0.6 * behind));
  // Opening: exactly the original Rückenfigur framing.
  if (w < 5.5) target.copy(new Vector3(1.2, 1.25, -40));
  else if (w < 8) target.lerp(new Vector3(1.2, 1.25, -40), 1 - smoothstep(5.5, 8, w));
  const shake = new Vector3(noise1(w * 9, 21), noise1(w * 9, 22), noise1(w * 9, 23)).multiplyScalar(0.05 * c * c);
  position.add(shake);
  const roll = noise1(w * 0.25, 9) * 0.02 + c * (0.2 * noise1(w * 0.8, 31) + 0.05 * noise1(w * 6, 32));
  const freeze = smoothstep(ACT.freeze[0], ACT.freeze[1], t);
  return { position, target, roll, fov: spline(w, FOV) - 5 * freeze };
};
