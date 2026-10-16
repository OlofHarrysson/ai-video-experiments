import { Color, Vector3 } from "three";
import { HEADLINES } from "./headlines";
import { PALETTE } from "./palette";
import {
  LANE_SPACING,
  Mapping,
  RACERS,
  TICKS,
  curveFrame,
  curvePoint,
  S_FREEZE,
  leaderS,
  racerHead,
  racerPoint,
} from "./race";
import { PERSON } from "./person";
import { CAMPUSES } from "./world/DataCenters";
import { Glow } from "./world/Glows";
import { Stroke } from "./world/GuideLines";
import { Label } from "./world/Labels";
import { clamp, easeOutBack, hash, keys, smoothstep } from "./lib/math";

// Everything that is placed in the world as a function of world time: launch beads and flashes,
// NEW MODEL tags, time ticks and the headline storm.

const colorCache = new Map<string, Color>();
const color = (hex: string) => {
  let c = colorCache.get(hex);
  if (!c) {
    c = new Color(hex);
    colorCache.set(hex, c);
  }
  return c;
};
const rgb = (hex: string, k = 1): [number, number, number] => {
  const c = color(hex);
  return [c.r * k, c.g * k, c.b * k];
};

// Where each launch happened, fixed once.
type Launch = { racer: number; k: number; w: number; s: number };
export const LAUNCHES: Launch[] = RACERS.flatMap((r) =>
  r.launches.map((w, k) => ({ racer: r.id, k, w, s: racerHead(r, w) })),
).sort((a, b) => a.w - b.w);

const ribbonHalfWidth = (w: number) => {
  const n = RACERS.filter((r) => r.spawn <= w).length;
  return Math.ceil(n / 2) * LANE_SPACING;
};

const _p = new Vector3();
const _t = new Vector3();
const _n = new Vector3();

export const launchGlows = (w: number, m: Mapping, out: Glow[], sMax = Infinity) => {
  for (const l of LAUNCHES) {
    if (l.w > w) break;
    if (l.s > sMax) continue;
    const racer = RACERS[l.racer];
    const age = w - l.w;
    const p = racerPoint(racer, l.s, m, new Vector3());
    const c = color(racer.color);
    // The bead it leaves on the line.
    out.push({ position: p, color: c, px: 3.2, world: 0.11, intensity: 0.9 });
    // The pop and its ring.
    if (age < 0.25) {
      const k = 1 - age / 0.25;
      out.push({ position: p, color: c, px: 6 + 14 * k, world: 0.25 + 0.5 * k, intensity: 2.0 * k, streak: 1 });
    }
    if (age < 0.7) {
      const k = age / 0.7;
      out.push({ position: p, color: c, px: 24 + 60 * k, world: 0.8 + 2.2 * k, intensity: 1.6 * (1 - k) * (1 - k), ring: 0.35 + 0.55 * k });
    }
  }
};

export const launchTags = (w: number, m: Mapping, out: Label[], fade = 1) => {
  for (const l of LAUNCHES) {
    if (l.w > w) break;
    const age = w - l.w;
    if (age > 1.5) continue;
    const racer = RACERS[l.racer];
    const pop = easeOutBack(clamp(age / 0.16));
    const jitter = hash(l.racer, l.k, 5) - 0.5;
    const early = 1 + 0.6 * (1 - smoothstep(8, 13, l.w));
    out.push({
      key: "tag:NEW MODEL",
      position: racerPoint(racer, l.s, m, new Vector3()),
      minPx: 15 * pop * early,
      world: 0.26 * pop * early,
      maxPx: 46 * pop * early,
      color: rgb(racer.color, 1.7),
      opacity: fade * (1 - smoothstep(1.0, 1.5, age)),
      offset: [jitter * 0.6, 1.0 + age * 0.4],
    });
  }
};

export const tickLabels = (w: number, m: Mapping, glows: Glow[], out: Label[], fade = 1) => {
  for (const tick of TICKS) {
    if (tick.w > w) break;
    const age = w - tick.w;
    const s = leaderS(tick.w);
    curvePoint(s, m, _p);
    curveFrame(s, m, _t, _n);
    const side = (ribbonHalfWidth(tick.w) * (1 + smoothstep(50, 110, s) * 1.6) + 0.9) * m.sl;
    const anchor = _p.clone().add(new Vector3(-side, 0, 0)).addScaledVector(_n, 0.04);
    const glow = 1 + 2 * Math.exp(-age * 4);
    glows.push({ position: anchor, color: color(PALETTE.tick), px: 2.5, world: 0.08, intensity: 0.8 * glow });
    const now = tick.label === "NOW";
    const keep = now ? 1 : fade;
    if (keep <= 0.001) continue;
    out.push({
      key: `tick:${tick.label}`,
      position: anchor,
      minPx: now ? 40 : tick.major ? 17 : 13,
      world: tick.major ? 0.34 : 0.2,
      maxPx: now ? 90 : tick.major ? 52 : 30,
      color: now ? [2.4, 2.4, 2.6] : rgb(PALETTE.tick, 1.15 * glow),
      opacity: (0.45 + 0.55 * Math.exp(-age * 0.8)) * keep,
      offset: [-0.55, 0.75],
    });
  }
};

/** In the reveal, a dashed drop line from the floor to where we froze, so NOW can be followed down. */
export const nowMarker = (m: Mapping, strength: number, out: Stroke[]) => {
  if (strength <= 0.001) return;
  const top = curvePoint(S_FREEZE, m, new Vector3());
  const dashes = 14;
  for (let i = 0; i < dashes; i++) {
    const a = i / dashes;
    const b = (i + 0.55) / dashes;
    out.push({
      points: [new Vector3(top.x, top.y * a, top.z), new Vector3(top.x, top.y * b, top.z)],
      color: color(PALETTE.tick),
      brightness: 0.55 * strength,
    });
  }
};

/** Light pollution: a soft glow over every campus once it is lit, with a pop as it comes online. */
export const campusGlows = (w: number, m: Mapping, out: Glow[]) => {
  const c = color(PALETTE.cityGlow);
  for (const campus of CAMPUSES) {
    const age = w - campus.build;
    if (age < -0.3) continue;
    const lit = smoothstep(-0.3, 0.6, age);
    const pop = Math.exp(-Math.max(age, 0) * 3.5) * smoothstep(-0.3, 0, age);
    out.push({
      position: new Vector3(campus.x * m.sl, 0.4 * Math.min(1, m.sy), campus.z * m.sx),
      color: c,
      px: 4,
      world: Math.min(campus.radius * 2.6, 70) * Math.max(m.sl, 0.3),
      intensity: 0.07 * lit + 0.5 * pop,
    });
  }
};

// ── The storm around the person ─────────────────────────────────────────────
// Notifications pop up in the air around them, faster and faster, until they stand in a cloud
// of NEW MODEL tags and headlines.
type StormCard = {
  w: number;
  key: string;
  tag: boolean;
  pos: Vector3;
  drift: Vector3;
  size: number;
  tilt: number;
  color: [number, number, number];
  life: number;
};

export const STORM: StormCard[] = (() => {
  const cards: StormCard[] = [];
  let w = 11.5;
  let i = 0;
  while (w < 24.2) {
    const r = (n: number) => hash(i, n, 2024);
    const angle = r(1) * Math.PI * 2;
    // Outside the camera's orbit, so no card fills the lens.
    const radius = 5 + r(2) * 9;
    const tag = r(4) < 0.45;
    const dir = new Vector3(Math.sin(angle), 0, Math.cos(angle));
    cards.push({
      w,
      key: tag ? "tag:NEW MODEL" : `headline:${HEADLINES[(i * 7) % HEADLINES.length].text}`,
      tag,
      pos: PERSON.clone().addScaledVector(dir, radius).add(new Vector3(0, 0.5 + r(3) * 5.5, 0)),
      drift: dir.clone().multiplyScalar(0.25).add(new Vector3(0, 0.18, 0)),
      size: tag ? 0.3 + r(5) * 0.15 : 0.45 + r(5) * 0.5,
      tilt: (r(6) - 0.5) * 0.35,
      color: tag ? rgb(RACERS[i % RACERS.length].color, 1.8) : [1, 1, 1],
      life: 1.8 + r(7) * 1.2,
    });
    // One every second or so at first, about ten a second by the end.
    w += 1 / keys(w, [[11.5, 1.2], [15, 2.5], [18, 4.5], [21, 7], [23.5, 11]]);
    i++;
  }
  return cards;
})();

export const stormLabels = (w: number, fade: number, tags: Label[], headlines: Label[]) => {
  if (fade <= 0.001) return;
  for (const c of STORM) {
    if (c.w > w) break;
    const age = w - c.w;
    if (age > c.life) continue;
    const pop = easeOutBack(clamp(age / 0.14), 2.0);
    const out = 1 - smoothstep(c.life - 0.4, c.life, age);
    (c.tag ? tags : headlines).push({
      key: c.key,
      position: c.pos.clone().addScaledVector(c.drift, age),
      minPx: 12 * pop,
      world: c.size * pop,
      maxPx: 220,
      color: c.color,
      opacity: out * fade,
      rotation: c.tilt,
    });
  }
};

/** In the reveal, YOU marks where the person still stands: the start of the chart. */
export const youMarker = (strength: number, glows: Glow[], labels: Label[]) => {
  if (strength <= 0.001) return;
  const at = PERSON.clone().add(new Vector3(0, 0.3, 0));
  glows.push({ position: at, color: color("#ffffff"), px: 5, world: 0.4, intensity: 1.6 * strength });
  labels.push({
    key: "tick:YOU",
    position: at,
    minPx: 40,
    world: 0.5,
    maxPx: 70,
    color: [2.2, 2.2, 2.4],
    opacity: strength,
    offset: [0, 1.1],
  });
};
