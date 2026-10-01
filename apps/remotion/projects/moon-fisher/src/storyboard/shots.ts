import { onScreen, type Camera } from "../pixel/pix";
import type { Vec2 } from "../pixel/shapes";
import { HORIZON, SEAT, type SceneSpec } from "../stills/boatScene";
import { KEY_IMAGE } from "../stills/keyImage";
import { leanBack, startle, startleProgress } from "../stills/motion";
import {
  DOZE,
  FLOAT,
  HAUL,
  HOOKED,
  REFLECTION,
  skyMoon,
  TIP,
} from "../stills/poses";
import { at, BAR_SECONDS, FPS, SECTIONS } from "../timing";
import { moonCenter, MOON_RADIUS } from "../world/bucket";
import { fisherman } from "../world/fisherman";
import {
  dozingOff,
  DOZING_ARMS,
  leapSplashes,
  leaping,
  lookingUp,
  move,
  type Leap,
} from "./acting";

// Storyboard notation over a panel, in design-frame units: arrows for what
// travels during the shot, and shake lines around what shivers.
export type Notation = {
  arrows?: (readonly [Vec2, Vec2])[];
  shakes?: { at: Vec2; r: number }[];
};

// The film, shot by shot, cut on the score's bars. Each shot is a scene spec
// as a function of the seconds since the shot began and since the film
// began; the storyboard shows one moment of it, and the animatic plays it
// through.
export type Shot = {
  id: string;
  // [first bar, bar after the last]
  bars: readonly [number, number];
  framing: "Wide" | "Medium" | "Close";
  title: string;
  action: string;
  sound: string;
  spec: (t: number, film: number) => SceneSpec;
  // Seconds into the shot shown on the storyboard, and its notation at that
  // moment of the film.
  panel: number;
  notation?: (film: number) => Notation;
};

// Panels per row on the contact sheets.
export const SHEET_COLUMNS = 7;

const WIDE: Camera = { x: 150, y: 330, zoom: 0.75, sx: 135, sy: 337.5 };
const MEDIUM = KEY_IMAGE.camera;
const MEDIUM_WIDE: Camera = { x: 150, y: 330, zoom: 1.2, sx: 140, sy: 285 };
const FACE: Camera = { x: 128, y: 298, zoom: 3.2, sx: 150, sy: 230 };
const CAT: Camera = { x: 192, y: 322, zoom: 3.4, sx: 130, sy: 250 };
// The cat low in the frame, with the sky above it.
const CAT_SKY: Camera = { x: 210, y: 333, zoom: 2.6, sx: 175, sy: 345 };
const PAIL: Camera = { x: 148, y: 322, zoom: 3, sx: 135, sy: 240 };
// Looking down at the float, in the middle of the moon's glitter.
const WATER: Camera = { x: 172, y: 440, zoom: 3.5, sx: 135, sy: 260 };

// How high the moon stands in each frame. Above the water close-ups it is
// out of frame but still lights them; in the cat's close-up it hangs up and
// to the left of the cat, which looks up at it.
const MOON_HEIGHT = { wide: 70, medium: 55, water: -140, cat: 135 };

// The haul brings the hooked reflection in beside the boat while the moon
// comes down the sky to the horizon.
const LANDED: Vec2 = [176, 420];

// The rod's tip right above the float, so the line hangs straight down.
const ROD = {
  angle: -37.6,
  length: 64,
  bend: 2,
  line: { to: FLOAT, slack: 6 },
};
// Out on the foredeck, clear of the fishing line.
const PEER_LEFT = { x: 208, y: 342, pose: "peer", facing: "left" } as const;
const PEER_RIGHT = { ...PEER_LEFT, facing: "right" } as const;
const EMPTY_BUCKET = { at: "knees", x: 148, rimY: 326 } as const;

const ramp = (t: number, from: number, to: number, a: number, b: number) =>
  a + (b - a) * Math.min(1, Math.max(0, (t - from) / (to - from)));

// The night wears on: the moon crosses the sky, and its reflection the
// water. It drifts slowly while he fishes, faster while he dozes, and
// wanders into his hook on the tug's downbeat. World x of the reflection,
// from seconds into the film.
const DOZING = at(SECTIONS.doze[0]);
const TUG = at(SECTIONS.tug[0]);
const wander = (film: number) =>
  film < DOZING
    ? ramp(film, 0, DOZING, REFLECTION[0], 161)
    : ramp(film, DOZING, TUG, 161, HOOKED[0]);
const reflectionAt = (x: number): Vec2 => [x, REFLECTION[1]];

// Fishing under the moon, its reflection at world column `x` and the moon
// standing over it at height `y` in the frame: the setup, and the ending
// that mirrors it.
const fishing = (camera: Camera, x: number, y: number): SceneSpec => ({
  camera,
  moon: skyMoon(camera, x, y),
  reflection: reflectionAt(x),
  fisherman: "fish",
  rod: ROD,
  float: FLOAT,
  cat: PEER_LEFT,
});

const mix = (a: Vec2, b: Vec2, p: number): Vec2 => [
  a[0] + (b[0] - a[0]) * p,
  a[1] + (b[1] - a[1]) * p,
];

const horizonIn = (c: Camera) => onScreen(c, [0, HORIZON])[1];

// An arrow running alongside a path, `side` units off it (to the screen
// left of a path going down), with `trim` of its length cut from each end.
const alongside = (
  a: Vec2,
  b: Vec2,
  side: number,
  trim = 0,
): readonly [Vec2, Vec2] => {
  const len = Math.hypot(b[0] - a[0], b[1] - a[1]);
  const [nx, ny] = [
    (-(b[1] - a[1]) / len) * side,
    ((b[0] - a[0]) / len) * side,
  ];
  const [from, to] = [mix(a, b, trim), mix(a, b, 1 - trim)];
  return [
    [from[0] + nx, from[1] + ny],
    [to[0] + nx, to[1] + ny],
  ];
};

// He hauls with one heave on each beat, then holds: progress from 0 to 1
// over `beats` beats.
const BEAT = BAR_SECONDS / 2;
const heaves = (t: number, beats: number) => {
  const i = Math.floor(t / BEAT);
  const heave = Math.min(1, (t - i * BEAT) / (BEAT / 3));
  return Math.min(1, (i + heave) / beats);
};
// His lean into each heave: quickly back, then slowly forward again.
const pullBack = (t: number) => {
  const p = (t % BEAT) / BEAT;
  return p < 1 / 3 ? move(p, 0, 1 / 3) : 1 - move(p, 1 / 3, 1);
};
const lerp = (a: number, b: number, k: number) => a + (b - a) * k;

// He hauls the moon down the sky, from high above its reflection to the
// horizon just past the bow, the stretch the boat does not hide. Sky moons
// are placed in the design frame, over these world columns.
const SETS_OVER = 243;
const HAUL_MOON_FROM: Vec2 = [
  onScreen(MEDIUM_WIDE, [HOOKED[0], 0])[0],
  MOON_HEIGHT.medium,
];
const HAUL_MOON_TO: Vec2 = [
  onScreen(MEDIUM_WIDE, [SETS_OVER, 0])[0],
  horizonIn(MEDIUM_WIDE) - 11,
];
const haulMoon = (t: number) => mix(HAUL_MOON_FROM, HAUL_MOON_TO, heaves(t, 6));
const hauledReflection = (t: number) => mix(HOOKED, LANDED, heaves(t, 6));

// In the catch the moon sinks below that stretch of horizon as it bursts
// out of the sea where the reflection was landed.
const SETTING_X = onScreen(WIDE, [SETS_OVER, 0])[0];
const settingY = (t: number) =>
  ramp(t, 0, 0.4, horizonIn(WIDE) - 11, horizonIn(WIDE) + 11);
const caughtY = (t: number) => ramp(t, 0, 1.2, LANDED[1] + 9, LANDED[1] - 30);

// He tips the moon out of the bucket over the side. Times in seconds into
// the shot; heights in world units.
const TIP_OFFSET: Vec2 = [10, 4];
const tipGrip = fisherman({
  x: SEAT[0],
  y: SEAT[1],
  pose: "tip",
  facing: "right",
}).grip;
const RELEASE = {
  leaves: 0.55,
  falls: 0.35,
  lands: 0.9,
  water: 400,
  from: moonCenter({
    x: tipGrip[0] + TIP_OFFSET[0],
    rimY: tipGrip[1] + TIP_OFFSET[1],
    moon: true,
    tilt: 50,
  }),
};
const clamp01 = (v: number) => Math.min(1, Math.max(0, v));

// The finale's fish, leaping through the moon's path in turn.
const finaleLeap = (
  from: Vec2,
  to: Vec2,
  height: number,
  start: number,
): Leap => ({
  from,
  to,
  height,
  start,
  duration: 0.9,
  size: 2.2,
});
const FINALE_LEAPS: Leap[] = [
  finaleLeap([30, 400], [70, 404], 24, 0.4),
  finaleLeap([200, 398], [245, 402], 26, 1.3),
  finaleLeap([100, 415], [135, 418], 30, 2.2),
  finaleLeap([235, 400], [205, 404], 22, 2.8),
  finaleLeap([60, 410], [25, 412], 26, 3.6),
  finaleLeap([150, 420], [190, 422], 34, 4.5),
];

// The gift: a fish clears the gunwale and lands on the foredeck by the cat.
const GIFT: Leap = {
  from: [216, 425],
  to: [192, 341],
  height: 50,
  start: 0.6,
  duration: 0.9,
  size: 1.3,
};

export const SHOTS: Shot[] = [
  {
    id: "01",
    bars: [1, 5],
    framing: "Wide",
    title: "The boat under the moon",
    action:
      "A tiny boat in the moon's silver path. His line hangs straight down to the float, beside the moon's reflection.",
    sound: "Intro, then the tune. The sea.",
    spec: (_, film) => fishing(WIDE, wander(film), MOON_HEIGHT.wide),
    panel: 2,
  },
  {
    id: "02",
    bars: [5, 8],
    framing: "Medium",
    title: "Nothing bites",
    action: "He waits with the rod out; the cat watches the float.",
    sound: "The tune. A creak of the boat.",
    spec: (_, film) => fishing(MEDIUM, wander(film), MOON_HEIGHT.medium),
    panel: 2,
  },
  {
    id: "03",
    bars: [8, 9],
    framing: "Close",
    title: "A ripple",
    action:
      "The float bobs beside the reflection. Its ripple runs into it, and the reflection wobbles.",
    sound: "The tune's last phrase. A plip, water lapping.",
    spec: (t, film) => ({
      ...fishing(WATER, wander(film), MOON_HEIGHT.water),
      cat: undefined,
      ripple: { at: FLOAT, radius: 18 * (t - 0.1) },
      wobble: ramp(t, 0.78, 0.92, 0, 1) * ramp(t, 0.92, 1.5, 1, 0.5),
    }),
    panel: 1.05,
    notation: (film) => ({
      shakes: [
        {
          at: onScreen(WATER, reflectionAt(wander(film))),
          r: 7.5 * WATER.zoom,
        },
      ],
    }),
  },
  {
    id: "04",
    bars: [9, 10],
    framing: "Close",
    title: "The moon shivers",
    action: "Up in the sky the moon shivers too. Only the cat looks up.",
    sound: "The tune ends. A faint, glassy shiver.",
    spec: (t, film) => {
      const scene = fishing(CAT_SKY, wander(film), MOON_HEIGHT.cat);
      return {
        ...scene,
        moon: {
          ...skyMoon(CAT_SKY, wander(film), MOON_HEIGHT.cat),
          shiver: t < 1 ? 2 : 0,
        },
        cat: { ...PEER_LEFT, look: ramp(t, 0.2, 0.4, 0, 50) },
      };
    },
    panel: 0.75,
    notation: (film) => {
      const moon = skyMoon(CAT_SKY, wander(film), MOON_HEIGHT.cat);
      return { shakes: [{ at: [moon.x, moon.y], r: moon.r }] };
    },
  },
  {
    id: "05",
    bars: [10, 12],
    framing: "Medium",
    title: "He dozes off",
    action:
      "His head sinks; the hat slides over his eyes. Meanwhile the moon drifts on, and its reflection reaches his float.",
    sound: "The doze: a lazy clarinet.",
    spec: (t, film) => {
      // As his hands sink to his lap the rod droops, its tip still over the
      // float.
      const k = move(t, ...DOZING_ARMS);
      return {
        ...DOZE,
        fisherman: dozingOff(t),
        rod: {
          angle: lerp(ROD.angle, -37.7, k),
          length: lerp(ROD.length, 70, k),
          bend: lerp(ROD.bend, 3, k),
          line: { to: FLOAT, slack: 8 },
        },
        moon: skyMoon(MEDIUM, wander(film), MOON_HEIGHT.medium),
        reflection: reflectionAt(wander(film)),
        cat: PEER_LEFT,
      };
    },
    panel: 2,
    // The drift is short, so its arrows start further back to stay legible.
    notation: () => {
      const [from, to] = [wander(DOZING) - 16, HOOKED[0]];
      const sky = (x: number): Vec2 => [
        skyMoon(MEDIUM, x).x,
        MOON_HEIGHT.medium,
      ];
      return {
        arrows: [
          alongside(sky(from), sky(to), -20),
          alongside(
            onScreen(MEDIUM, reflectionAt(from)),
            onScreen(MEDIUM, reflectionAt(to)),
            18,
          ),
        ],
      };
    },
  },
  {
    id: "06",
    bars: [12, 13],
    framing: "Close",
    title: "A tug",
    action:
      "The reflection has wandered into his hook. The float plunges under: it is hooked.",
    sound: "The tug: two plucks. A plop, the reel clicks.",
    spec: (t) => {
      // A jolt on each of the two plucks.
      const jolt = Math.max(ramp(t, 0, 0.4, 1, 0), ramp(t, 0.75, 1.15, 1, 0));
      return {
        ...fishing(WATER, HOOKED[0], MOON_HEIGHT.water),
        cat: undefined,
        float: undefined,
        wobble: 0.3 + 0.7 * jolt,
        rod: { ...ROD, bend: 4, line: { to: FLOAT, slack: 0 } },
        splashes: t < 0.6 ? [{ at: FLOAT, size: 6 }] : [],
        catchGlow: { at: HOOKED, strength: ramp(t, 0, 1.5, 0.3, 0.7) },
      };
    },
    panel: 0.25,
  },
  {
    id: "07",
    bars: [13, 16],
    framing: "Medium",
    title: "He hauls the moon down",
    action:
      "He jolts awake and hauls. Each pull drags the reflection toward the boat and the moon down the sky. The cat stares.",
    sound: "The haul: driving plucks. The reel whirs.",
    spec: (t) => {
      const hooked = hauledReflection(t);
      const [x, y] = haulMoon(t);
      const lean = t < BEAT ? 0 : pullBack(t);
      const k = startleProgress("forearm", t * FPS);
      return {
        ...HAUL,
        camera: MEDIUM_WIDE,
        fisherman: leanBack(startle(t * FPS), lean),
        moon: { in: "sky", x, y, r: 11 },
        reflection: hooked,
        wobble: 0.6,
        rod: {
          angle: lerp(-37.7, -52, k),
          length: lerp(70, 72, k),
          bend: lerp(10, 18, k) + 3 * lean,
          line: { to: hooked, slack: 0 },
        },
        catchGlow: { at: hooked, strength: 1 },
        // The cat follows the moon down to the horizon past the bow.
        cat: { ...PEER_RIGHT, look: lerp(55, 5, heaves(t, 6)) },
      };
    },
    panel: 2,
    notation: () => ({
      arrows: [
        alongside(HAUL_MOON_FROM, HAUL_MOON_TO, 22, 0.15),
        alongside(
          onScreen(MEDIUM_WIDE, HOOKED),
          onScreen(MEDIUM_WIDE, LANDED),
          20,
        ),
      ],
    }),
  },
  {
    id: "08",
    bars: [16, 17],
    framing: "Wide",
    title: "The moon comes out of the water",
    action:
      "As the moon sinks below the horizon, it bursts out of the sea on his line.",
    sound: "The catch: the harp sweeps up. A great splash.",
    spec: (t) => {
      const ball: Vec2 = [LANDED[0], caughtY(t)];
      return {
        camera: WIDE,
        moon: {
          in: "world",
          x: ball[0],
          y: ball[1],
          r: 12,
          waterline: LANDED[1],
        },
        setting: { x: SETTING_X, y: settingY(t), r: 11 },
        fisherman: "haul",
        rod: { angle: -52, length: 72, bend: 18, line: { to: ball, slack: 0 } },
        splashes: [{ at: LANDED, size: 7 }],
        cat: { ...PEER_RIGHT, look: 5 },
      };
    },
    panel: 0.3,
    notation: () => ({
      arrows: [
        alongside(
          [SETTING_X, horizonIn(WIDE) - 30],
          [SETTING_X, horizonIn(WIDE) + 2],
          -18,
        ),
        alongside(
          onScreen(WIDE, [LANDED[0], LANDED[1] + 12]),
          onScreen(WIDE, [LANDED[0], LANDED[1] - 30]),
          -18,
        ),
      ],
    }),
  },
  {
    id: "09",
    bars: [17, 19],
    framing: "Medium",
    title: "The moon in his bucket",
    action: "The moon glows in the bucket, lighting his face from below.",
    sound: "Wonder: the tune on high piano. Drips.",
    spec: () => KEY_IMAGE,
    panel: 1.5,
  },
  {
    id: "10",
    bars: [19, 21],
    framing: "Close",
    title: "Wonder",
    action: "His face in the moonlight; a slow smile.",
    sound: "Wonder.",
    spec: () => ({ ...KEY_IMAGE, camera: FACE }),
    panel: 1.5,
  },
  {
    id: "11",
    bars: [21, 22],
    framing: "Close",
    title: "The cat reaches",
    action: "The cat stretches a paw toward the glow.",
    sound: "The violin answers. A curious chirp.",
    spec: () => ({ ...KEY_IMAGE, camera: CAT }),
    panel: 0.75,
  },
  {
    id: "12",
    bars: [22, 24],
    framing: "Close",
    title: "It dims",
    action: "The moon's glow flickers and fades, like a fish out of water.",
    sound: "The dimming: the tune in minor on the violin.",
    spec: (t) => ({ ...KEY_IMAGE, camera: PAIL, glow: ramp(t, 0, 3, 1, 0.35) }),
    panel: 2.6,
  },
  {
    id: "13",
    bars: [24, 26],
    framing: "Medium",
    title: "The empty sky",
    action:
      "He looks up at the black, moonless sky, then back at the fading moon.",
    sound: "The dimming ends, unresolved.",
    spec: (t) => ({
      ...KEY_IMAGE,
      fisherman: lookingUp(t, [0.3, 1], [2, 2.6]),
      glow: 0.32,
    }),
    panel: 1.5,
  },
  {
    id: "14",
    bars: [26, 27],
    framing: "Medium",
    title: "He lets it go",
    action: "He tips the bucket over the side; the moon slides into the sea.",
    sound: "The release: the harp sinks. A soft plop.",
    spec: (t) => {
      const tilt = ramp(t, 0, 0.8, 20, 60);
      const bucket = { at: "hands", tilt, offset: TIP_OFFSET } as const;
      if (t < RELEASE.leaves) return { ...TIP, glow: 0.4, bucket };
      // It drops from the bucket's mouth into the sea in front of the boat,
      // then sinks and fades.
      const fall = clamp01((t - RELEASE.leaves) / RELEASE.falls);
      const x = RELEASE.from[0] + 8 * fall;
      const y =
        t < RELEASE.lands
          ? RELEASE.from[1] +
            (RELEASE.water - MOON_RADIUS - RELEASE.from[1]) * fall * fall
          : ramp(
              t,
              RELEASE.lands,
              1.5,
              RELEASE.water - MOON_RADIUS,
              RELEASE.water + MOON_RADIUS + 2,
            );
      return {
        ...TIP,
        moon: { in: "world", x, y, r: MOON_RADIUS, waterline: RELEASE.water },
        glow: ramp(t, RELEASE.lands, 1.5, 0.4, 0.12),
        bucket,
        splashes:
          t >= RELEASE.lands && t < RELEASE.lands + 0.35
            ? [{ at: [x, RELEASE.water], size: 4 }]
            : [],
      };
    },
    panel: 0.8,
  },
  {
    id: "15",
    bars: [27, 28],
    framing: "Wide",
    title: "Darkness",
    action: "Only the stars and the boat's faint outline.",
    sound: "Only the sea.",
    spec: () => ({
      camera: WIDE,
      moon: { in: "gone" },
      fisherman: "holdBucket",
      bucket: EMPTY_BUCKET,
      cat: PEER_LEFT,
    }),
    panel: 0.75,
  },
  {
    id: "16",
    bars: [28, 31],
    framing: "Wide",
    title: "The moon rises",
    action:
      "The sea glows from below; the moon rises out of the water beside the boat and climbs into the sky.",
    sound: "The rise: the clarinet reaches up. A swelling shimmer.",
    spec: (t) => {
      const y = ramp(t, 0.5, 4.5, 450, 250);
      return {
        camera: WIDE,
        moon: { in: "world", x: 214, y, r: 12, waterline: 440 },
        seaGlow: {
          at: [214, 440],
          radius: 70,
          strength: ramp(t, 0, 1.5, 0.2, 1),
        },
        fisherman: "holdBucket",
        bucket: EMPTY_BUCKET,
        cat: PEER_RIGHT,
      };
    },
    panel: 1.8,
  },
  {
    id: "17",
    bars: [31, 35],
    framing: "Wide",
    title: "Silver light",
    action: "The moon rides high again. Fish leap through its silver path.",
    sound: "The finale: home in E. Splashes.",
    spec: (t) => ({
      ...fishing(WIDE, REFLECTION[0], MOON_HEIGHT.wide),
      cat: PEER_RIGHT,
      fish: FINALE_LEAPS.flatMap((l) => leaping(l, t) ?? []),
      splashes: FINALE_LEAPS.flatMap((l) => leapSplashes(l, t, 3)),
    }),
    panel: 3,
  },
  {
    id: "18",
    bars: [35, 37],
    framing: "Medium",
    title: "A gift",
    action: "One fish leaps into the boat; the cat is on it at once.",
    sound: "The last phrase again. A flop, a happy mew.",
    spec: (t) => {
      const lands = GIFT.start + GIFT.duration;
      // It flops on the deck for a moment, then lies still.
      const flop = t < lands + 0.8 ? (Math.floor(t * 6) % 2 ? 20 : -20) : 0;
      return {
        ...fishing(MEDIUM, REFLECTION[0], MOON_HEIGHT.medium),
        fish:
          t < lands
            ? [GIFT].flatMap((l) => leaping(l, t) ?? [])
            : [{ at: GIFT.to, angle: 180 + flop, size: GIFT.size }],
        splashes: leapSplashes(GIFT, t, 3, false),
        // The cat watches it fly in, then looks down at its prize.
        cat: {
          ...PEER_LEFT,
          look: 25 * move(t, 0.6, 0.9) - 40 * move(t, 1.4, 1.7),
        },
      };
    },
    panel: 1.3,
  },
  {
    id: "19",
    bars: [37, 41],
    framing: "Wide",
    title: "Like the beginning",
    action:
      "The first shot again: the moon high, his float beside its reflection. He smiles; the cat has its fish.",
    sound: "The coda, the plucked ta-dum and a last high note. The sea.",
    spec: () => ({
      ...fishing(WIDE, REFLECTION[0], MOON_HEIGHT.wide),
      fish: [{ at: [198, 341], angle: 180, size: 1.6 }],
    }),
    panel: 3,
  },
];

export const shotStart = (s: Shot) => (s.bars[0] - 1) * BAR_SECONDS;
export const shotSeconds = (s: Shot) => (s.bars[1] - s.bars[0]) * BAR_SECONDS;

// The film at a frame: the shot playing and its scene. Action moves on twos;
// ambient life follows the frame itself.
export const filmAt = (frame: number) => {
  const action = (Math.floor(frame / 2) * 2) / FPS;
  const shot =
    SHOTS.find((s) => action < shotStart(s) + shotSeconds(s)) ??
    SHOTS[SHOTS.length - 1];
  return { shot, spec: shot.spec(action - shotStart(shot), action) };
};

// The storyboard's frame of a shot, and its notation.
export const panelFrame = (s: Shot) =>
  Math.round((shotStart(s) + s.panel) * FPS);
export const panelNotation = (s: Shot): Notation =>
  s.notation?.(shotStart(s) + s.panel) ?? {};
