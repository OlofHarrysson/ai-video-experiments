import { Vector3 } from "three";
import { Shot } from "./camera";
import { ACT } from "./timing";
import { lerp, smootherstep } from "./lib/math";

// The opening framing again, now facing the column; then a slow rise to show everyone else.
export const endCamera = (t: number): Shot => {
  const start = ACT.end[0];
  const k = smootherstep(start + 3, start + 11.5, t);
  const from = new Vector3(1.55, 1.3, 9.4 - (t - start) * 0.12);
  const to = new Vector3(6, 13, 42);
  const position = from.clone().lerp(to, k);
  const target = new Vector3(1.2, 1.25, -40).lerp(new Vector3(-6.5, 6.5, -30), k);
  return { position, target, roll: 0, fov: lerp(30, 40, k) };
};
