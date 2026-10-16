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
  height,
  leaderS,
  sAtHeight,
  racerHead,
  racerPoint,
} from "./race";
import { BEAT } from "./timing";
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
      minPx: now ? 30 : tick.major ? 17 : 13,
      world: tick.major ? 0.34 : 0.2,
      maxPx: now ? 90 : tick.major ? 52 : 30,
      color: now ? [2.4, 2.4, 2.6] : rgb(PALETTE.tick, 1.15 * glow),
      opacity: (0.45 + 0.55 * Math.exp(-age * 0.8)) * keep,
      offset: [-0.55, 0.75],
    });
  }
};

// Headline cards appear around the climb, faster and faster, and the camera rushes past them.
type Card = { w: number; s: number; lateral: number; normal: number; text: string; size: number; tilt: number };
export const CARDS: Card[] = (() => {
  const cards: Card[] = [];
  let w = 17.5;
  let i = 0;
  while (w < 24) {
    const r = (n: number) => hash(i, n, 909);
    const ahead = 5 + r(1) * 14;
    cards.push({
      w,
      s: sAtHeight(height(leaderS(w)) + ahead),
      lateral: (r(2) < 0.5 ? -1 : 1) * (3.5 + r(3) * 11),
      normal: -7 + r(4) * 13,
      // Walk the list in a shuffled order so the same card never follows itself.
      text: HEADLINES[(i * 5 + Math.floor(i / HEADLINES.length) * 3) % HEADLINES.length].text,
      size: 0.9 + r(6) * 1.4,
      tilt: (r(7) - 0.5) * 0.3,
    });
    // One card a beat at first, then four.
    w += BEAT / keys(w, [[17.5, 1], [20, 2], [22.5, 4], [24, 6]]);
    i++;
  }
  return cards;
})();

export const headlineCards = (w: number, m: Mapping, out: Label[], fade = 1) => {
  if (fade <= 0.001) return;
  for (const c of CARDS) {
    if (c.w > w) break;
    const age = w - c.w;
    curvePoint(c.s, m, _p);
    curveFrame(c.s, m, _t, _n);
    const p = _p.clone().add(new Vector3(c.lateral, 0, 0)).addScaledVector(_n, c.normal);
    const pop = easeOutBack(clamp(age / 0.12), 2.2);
    out.push({
      key: `headline:${c.text}`,
      position: p,
      minPx: 22 * pop,
      world: c.size * 0.42 * pop,
      maxPx: 230,
      color: [1, 1, 1],
      opacity: fade,
      rotation: c.tilt,
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
      world: campus.radius * 3.2 * Math.max(m.sl, 0.3),
      intensity: 0.16 * lit + 0.9 * pop,
    });
  }
};
