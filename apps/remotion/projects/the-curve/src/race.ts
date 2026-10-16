import { Vector3 } from "three";
import { BEAT, worldClock } from "./timing";
import { clamp, hash, keys, lerp, rng, smoothstep } from "./lib/math";

// ── The curve ────────────────────────────────────────────────────────────────
// Chart space: s runs along the ground away from the figure (world −Z), h is height.
export const CURVE_A = 0.05;
export const CURVE_L = 12;
export const height = (s: number) => CURVE_A * (Math.exp(s / CURVE_L) - 1);
export const slope = (s: number) => (CURVE_A / CURVE_L) * Math.exp(s / CURVE_L);

/**
 * Chart → world scale: sx along the ground, sy for height, sl for the ribbon's width, x0 to slide
 * the whole curve sideways. Shrinking sy faster than sx flattens yesterday's wall into a floor.
 */
export type Mapping = { sx: number; sy: number; sl: number; x0: number };
export const IDENTITY: Mapping = { sx: 1, sy: 1, sl: 1, x0: 0 };

export const curvePoint = (s: number, m: Mapping, out = new Vector3()) =>
  out.set(m.x0, height(s) * m.sy, -s * m.sx);

/** Unit tangent and the normal that points up (flat) or back toward the start (vertical). */
export const curveFrame = (s: number, m: Mapping, tangent: Vector3, normal: Vector3) => {
  const dy = slope(s) * m.sy;
  const dz = -m.sx;
  const n = Math.hypot(dy, dz);
  tangent.set(0, dy / n, dz / n);
  normal.set(0, -dz / n, dy / n);
};

// ── The leader ───────────────────────────────────────────────────────────────
// Speed along s in units per second of world time; the head itself never stops accelerating.
const SPEED: ReadonlyArray<readonly [number, number]> = [
  [0, 0],
  [1.5, 0],
  [2.5, 2],
  [6, 3.5],
  [9, 4.5],
  [12, 5.5],
  [15, 6.5],
  [18, 5.5],
  [21, 3.6],
  [24, 2.6],
  // After the freeze the head takes off: each second covers more e-folds than the last.
  [24.3, 6],
  [25, 16],
  [26, 30],
  [27, 55],
  [28, 100],
  [29, 170],
  [30, 200],
  [31, 100],
  [32, 40],
  [44, 40],
];
const STEP = 1 / 240;
const T_MAX = 46;
const S_TABLE = (() => {
  const table = new Float64Array(Math.ceil(T_MAX / STEP) + 2);
  let s = 0;
  for (let i = 0; i < table.length; i++) {
    table[i] = s;
    s += keys(i * STEP + STEP / 2, SPEED) * STEP;
  }
  return table;
})();

export const leaderS = (w: number) => {
  const x = clamp(w, 0, T_MAX) / STEP;
  const i = Math.floor(x);
  return lerp(S_TABLE[i], S_TABLE[i + 1], x - i);
};

/** World time at which the leader reaches s (inverse of leaderS). */
export const timeAtS = (s: number) => {
  let lo = 0;
  let hi = S_TABLE.length - 1;
  if (s <= 0) return 0;
  if (s >= S_TABLE[hi]) return T_MAX;
  while (hi - lo > 1) {
    const mid = (lo + hi) >> 1;
    if (S_TABLE[mid] < s) lo = mid;
    else hi = mid;
  }
  return (lo + (s - S_TABLE[lo]) / (S_TABLE[hi] - S_TABLE[lo])) * STEP;
};

// ── The racers ───────────────────────────────────────────────────────────────
export const RACER_COLORS = [
  "#f4f1ff", // the first line: white
  "#3ee8ff", // cyan
  "#ff4fd8", // magenta
  "#ffb53e", // amber
  "#7dff6a", // lime
  "#9a7bff", // violet
  "#ff5a4f", // red
  "#4f8bff", // blue
];

export type Racer = {
  id: number;
  spawn: number; // world time the spark appears
  lane: number; // lateral offset in the ribbon
  side: number; // side it enters from
  color: string;
  gapBase: number;
  gapAmp: number;
  gapFreq: number;
  gapPhase: number;
  catchUp: number; // how far behind it enters
  sStart: number; // where its line begins
  launches: number[]; // world times of model launches
};

// Spawn times on the beat grid: one line, then a rival, then a crowd.
const SPAWNS = [
  1.5, 6.5, 7.5, 9, 10, 11, 12.5, 13.5, 14, 15, 15.5, 16, 16.5, 17, 17.5, 18, 18.5, 19, 19.25,
  19.5, 20, 20.25, 20.5, 21, 21.25, 21.5, 22,
];
export const LANE_SPACING = 0.42;

/** Launches per second for one racer: occasional, then a blizzard. */
const launchRate = (w: number) =>
  keys(w, [
    [4, 0.22],
    [9, 0.4],
    [13, 0.7],
    [17, 1.4],
    [20, 2.6],
    [24, 4.5],
    [40, 8],
  ]);

const SIXTEENTH = BEAT / 4;

export const RACERS: Racer[] = SPAWNS.map((spawn, id) => {
  const r = rng(1000 + id * 17);
  const slot = Math.ceil(id / 2) * (id % 2 === 0 ? -1 : 1);
  const gapBase = id === 0 ? 0 : 0.2 + r() * 1.3;
  // Rivals come from behind the person and streak past them to join the pack.
  const catchUp = id === 0 ? 0 : leaderS(spawn) - gapBase + 18 + r() * 20;
  const racer: Racer = {
    id,
    spawn,
    lane: slot * LANE_SPACING,
    side: slot >= 0 ? 1 : -1,
    color: RACER_COLORS[id % RACER_COLORS.length],
    gapBase,
    gapAmp: id === 0 ? 0 : 0.4 + r() * 0.8,
    gapFreq: 0.35 + r() * 0.6,
    gapPhase: r() * Math.PI * 2,
    catchUp,
    sStart: 0,
    launches: [],
  };
  racer.sStart = id === 0 ? 0 : leaderS(spawn) - gapBase - catchUp;
  // Launch times, quantised to sixteenths. The first line's first launches set the rhythm.
  let w = id === 0 ? 5 : spawn + 0.75 + r() * 1.5;
  while (w < 44) {
    racer.launches.push(Math.round(w / SIXTEENTH) * SIXTEENTH);
    w += (0.6 + r() * 0.8) / launchRate(w);
  }
  return racer;
});

/** How far behind the pack's virtual leader a racer runs at world time w. */
export const racerGap = (racer: Racer, w: number) => {
  if (racer.id === 0) {
    // The first line leads alone, then is swallowed by the pack.
    return smoothstep(9, 16, w) * (0.8 + 0.7 * Math.sin(w * 0.5 + 1));
  }
  const age = w - racer.spawn;
  const enter = racer.catchUp * Math.exp(-Math.max(0, age) * 1.3);
  return racer.gapBase + racer.gapAmp * Math.sin(w * racer.gapFreq + racer.gapPhase) + enter;
};

/** Gaps are measured along the line, so the pack stays together when the curve stands up. */
export const racerHead = (racer: Racer, w: number) => {
  const lead = leaderS(w);
  const stretch = Math.hypot(1, slope(lead));
  return Math.max(racer.sStart, lead - racerGap(racer, w) / stretch);
};

/** The ribbon twists as it climbs; flat on the ground at first. */
export const twistAngle = (s: number) => {
  const sway = smoothstep(55, 75, s) * 0.32 * Math.sin((s - 55) * 0.16);
  const column = smoothstep(96, 112, s) * (s - 96) * 0.085;
  return sway + column;
};

/** Lateral and normal offset of a racer's line at s (the entry ramp sweeps in from the dark). */
export const laneOffset = (racer: Racer, s: number, out: { a: number; b: number }) => {
  const ramp = racer.id === 0 ? 1 : smoothstep(racer.sStart, racer.sStart + 9, s);
  const lateral = lerp(racer.lane + racer.side * 9, racer.lane, ramp);
  const lift = racer.id === 0 ? 0 : (1 - ramp) * 0.0;
  const angle = twistAngle(s);
  // Ribbon widens as it climbs so the pack stays readable from farther away, and bows out
  // around the person as it passes them.
  const widen = 1 + smoothstep(50, 110, s) * 1.6 + 1.0 * Math.exp(-((s / 11) ** 2));
  out.a = lateral * widen * Math.cos(angle);
  out.b = lateral * widen * Math.sin(angle) + lift;
  return out;
};

const _t = new Vector3();
const _n = new Vector3();
const _offset = { a: 0, b: 0 };

/** World position of a racer's line at s. */
export const racerPoint = (racer: Racer, s: number, m: Mapping, out = new Vector3()) => {
  curvePoint(s, m, out);
  curveFrame(s, m, _t, _n);
  laneOffset(racer, s, _offset);
  out.x += _offset.a * m.sl;
  out.addScaledVector(_n, _offset.b * m.sl);
  // Never sink below the ground.
  out.y = Math.max(out.y, 0.015);
  return out;
};

// ── Time ticks stamped along the curve ───────────────────────────────────────
export type Tick = { w: number; label: string; major: boolean };

const MONTHS = ["FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT"];
const DAYS = ["MON", "TUE", "WED", "THU", "FRI"];

export const TICKS: Tick[] = (() => {
  const ticks: Tick[] = [];
  const years: [number, string][] = [
    [2.0, "2016"],
    [4.0, "2018"],
    [6.0, "2020"],
    [7.5, "2021"],
    [8.75, "2022"],
    [9.75, "2023"],
    [10.75, "2024"],
    [11.5, "2025"],
    [12.25, "2026"],
  ];
  for (const [w, label] of years) ticks.push({ w, label, major: true });
  MONTHS.forEach((label, i) => ticks.push({ w: 12.75 + i * 0.375, label, major: false }));
  DAYS.forEach((label, i) => ticks.push({ w: 16.25 + i * 0.25, label, major: false }));
  // Hours, then minutes, closing in on now.
  let w = 17.5;
  for (let h = 8; h <= 17; h++) {
    ticks.push({ w, label: `${String(h).padStart(2, "0")}:00`, major: false });
    w += 0.25;
  }
  for (let m = 5; w < 23.9; m += 5) {
    const hh = 17 + Math.floor(m / 60);
    ticks.push({ w, label: `${hh}:${String(m % 60).padStart(2, "0")}`, major: false });
    w += 0.125;
  }
  ticks.push({ w: 24, label: "NOW", major: true });
  return ticks;
})();

export const tickS = (tick: Tick) => leaderS(tick.w);

/** Where the leader froze: everything before it is the race we lived through. */
export const S_FREEZE = 96.6;


/** Deterministic per-launch variety. */
export const launchSeed = (racer: Racer, k: number) => hash(racer.id, k, 77);

export const worldTime = (frame: number, fps: number) => worldClock(frame / fps);
