import { useLayoutEffect, useMemo } from "react";
import { Color, Mesh, Vector2, Vector3 } from "three";
import { Mapping, RACERS, Racer, S_FREEZE, height, racerHead, racerPoint, slope } from "../race";
import { LineBatch, createGlowLineMaterial } from "./glowLine";
import { clamp, smoothstep } from "../lib/math";

// Every racer's trail from where it entered to its spark, sampled finer near the camera.

const linearColors = new Map<number, Color>();
export const racerColor = (racer: Racer) => {
  let c = linearColors.get(racer.id);
  if (!c) {
    c = new Color(racer.color);
    linearColors.set(racer.id, c);
  }
  return c;
};

export const activeRacers = (w: number) => RACERS.filter((r) => w >= r.spawn);

type Props = {
  w: number;
  cam: Vector3;
  mapping: Mapping;
  resolution: Vector2;
  near: number;
  intensity?: number;
  worldWidth?: number;
  sMax?: number;
};

const FUTURE = new Color(1, 1, 1);

const sampleRacer = (
  racer: Racer,
  sHead: number,
  cam: Vector3,
  m: Mapping,
  pts: Vector3[],
  bright: number[],
  colors: Color[],
) => {
  pts.length = 0;
  bright.length = 0;
  colors.length = 0;
  const base = racerColor(racer);
  const p = new Vector3();
  let s = racer.sStart;
  // Walk from the tail to the head with steps sized by distance to the camera.
  for (let guard = 0; guard < 4000; guard++) {
    racerPoint(racer, s, m, p);
    pts.push(p.clone());
    // The race we lived through keeps its lab colours; everything after the freeze is white-hot.
    colors.push(base.clone().lerp(FUTURE, smoothstep(S_FREEZE, S_FREEZE + 5, s)));
    const toHead = sHead - s;
    bright.push(0.5 + 1.1 * Math.exp(-toHead / 1.5) + 0.35 * Math.exp(-toHead / 12));
    if (s >= sHead) break;
    const speed = Math.hypot(m.sx, slope(s) * m.sy) + 1e-6;
    const dist = p.distanceTo(cam);
    const step = clamp((dist * 0.01) / speed, 0.002, 6);
    s = Math.min(sHead, s + step);
  }
  // A newly entered line fades up from nothing at its tail.
  const n = pts.length;
  for (let i = 0; i < Math.min(n, 12); i++) bright[i] *= smoothstep(0, 11, i);
  return n;
};

export const Racers: React.FC<Props> = ({
  w,
  cam,
  mapping,
  resolution,
  near,
  intensity = 1,
  worldWidth = 0.12,
  sMax = Infinity,
}) => {
  const { batch, material } = useMemo(() => ({ batch: new LineBatch(16384), material: createGlowLineMaterial() }), []);
  const mesh = useMemo(() => {
    const m = new Mesh(batch.geometry, material);
    m.frustumCulled = false;
    m.renderOrder = 4;
    return m;
  }, [batch, material]);

  useLayoutEffect(() => {
    const pts: Vector3[] = [];
    const bright: number[] = [];
    const colors: Color[] = [];
    batch.begin();
    for (const racer of activeRacers(w)) {
      const sHead = Math.min(racerHead(racer, w), sMax);
      if (sHead <= racer.sStart + 1e-3) continue;
      sampleRacer(racer, sHead, cam, mapping, pts, bright, colors);
      batch.add(pts, bright, racerColor(racer), colors);
    }
    batch.end();
    const u = material.uniforms;
    u.uResolution.value.copy(resolution);
    u.uNear.value = near;
    u.uIntensity.value = intensity;
    u.uWorldWidth.value = worldWidth;
  });

  return <primitive object={mesh} />;
};

export const headPosition = (racer: Racer, w: number, m: Mapping, out = new Vector3()) =>
  racerPoint(racer, racerHead(racer, w), m, out);

export { height };
