import { onScreen, type Camera } from "../pixel/pix";
import type { Vec2 } from "../pixel/shapes";
import { HORIZON, SEAT, type SceneSpec } from "../stills/boatScene";
import { KEY_IMAGE } from "../stills/keyImage";
import { startle, startleProgress } from "../stills/motion";
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
import { cat as catFigure, type CatProps } from "../world/cat";
import { fisherman, POSES } from "../world/fisherman";
import {
  dozingOff,
  DOZING_ARMS,
  flicker,
  hauling,
  heaveOn,
  leapSplashes,
  leaping,
  lookingUp,
  move,
  NODDED_OFF,
  noddingOff,
  type Leap,
} from "./acting";

// Storyboard notation over a panel, in design-frame units: arrows for what
// travels during the shot.
export type Notation = {
  arrows?: (readonly [Vec2, Vec2])[];
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
  // Seconds over which it fades up from black or down to black, where time
  // passes; otherwise it cuts.
  fadeIn?: number;
  fadeOut?: number;
};

// Panels per row on the contact sheets.
export const SHEET_COLUMNS = 7;

const WIDE: Camera = { x: 150, y: 330, zoom: 0.75, sx: 135, sy: 337.5 };
const MEDIUM = KEY_IMAGE.camera;
const MEDIUM_WIDE: Camera = { x: 150, y: 330, zoom: 1.2, sx: 140, sy: 285 };
const FACE: Camera = { x: 128, y: 298, zoom: 3.2, sx: 150, sy: 230 };
const CAT: Camera = { x: 192, y: 322, zoom: 3.4, sx: 130, sy: 250 };
// The cat on the foredeck with its fish.
const PRIZE: Camera = { x: 200, y: 330, zoom: 3.2, sx: 140, sy: 280 };
// His face over the rod, with room above for the Z's.
const NOD: Camera = { x: 132, y: 300, zoom: 2.9, sx: 128, sy: 290 };
// The bow and the open horizon past it, with the water in front where the
// moon comes out; he is off to the left, his line running into the frame.
const CATCH: Camera = { x: 205, y: 370, zoom: 1.9, sx: 135, sy: 300 };
const PAIL: Camera = { x: 148, y: 322, zoom: 3, sx: 135, sy: 240 };
// Looking down at the float, in the middle of the moon's glitter.
const WATER: Camera = { x: 172, y: 440, zoom: 3.5, sx: 135, sy: 260 };

// How high the moon stands in each frame. Above the water close-ups it is
// out of frame but still lights them.
const MOON_HEIGHT = { wide: 70, medium: 55, water: -140 };

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
const KEY_CAT = { x: 198, y: 344, pose: "peer", facing: "left" } as const;
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

const BEAT = BAR_SECONDS / 2;
const lerp = (a: number, b: number, k: number) => a + (b - a) * k;

// The haul brings the moon in six steps, from 0 to 1: one as he jolts awake,
// then one with each heave, landing on the beat.
const haulSteps = (t: number) => {
  if (t < BEAT) return move(t, 0.1, 0.5) / 6;
  const p = (t % BEAT) / BEAT;
  return Math.min(1, (Math.floor(t / BEAT) + move(p, 0.65, 1)) / 6);
};

// His body and rod through the haul: the jolt awake into the first heave,
// then lowering the rod and heaving it up again on every beat. The rod bends
// hardest at the top of each heave.
const haulAt = (t: number) => {
  if (t >= BEAT) return hauling(heaveOn(t, BEAT));
  const f = t * FPS;
  const top = hauling(1);
  const k = startleProgress("forearm", f);
  return {
    pose: startle(f, POSES.heave),
    rod: lerp(-37.7, top.rod, k),
    bend: lerp(22, top.bend, k),
  };
};

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
const haulMoon = (t: number) => mix(HAUL_MOON_FROM, HAUL_MOON_TO, haulSteps(t));
const hauledReflection = (t: number) => mix(HOOKED, LANDED, haulSteps(t));

// In the catch the moon sinks below that stretch of horizon as it bursts
// out of the sea where the reflection was landed.
const SETTING_X = onScreen(CATCH, [SETS_OVER, 0])[0];
const settingY = (t: number) =>
  ramp(t, 0, 0.4, horizonIn(CATCH) - 11, horizonIn(CATCH) + 11);
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
// Seconds he has slept when the shot of him asleep begins.
const ASLEEP = 3 - NODDED_OFF;

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
  finaleLeap([60, 440], [100, 446], 30, 0.3),
  finaleLeap([200, 430], [240, 436], 32, 1),
  finaleLeap([120, 455], [160, 460], 40, 1.6),
  finaleLeap([235, 440], [195, 444], 30, 2.3),
  finaleLeap([155, 450], [118, 455], 38, 3),
  finaleLeap([50, 445], [85, 450], 28, 3.6),
  finaleLeap([170, 440], [210, 446], 36, 4.3),
  finaleLeap([100, 450], [136, 456], 34, 5),
];

// The cat springs from its seat onto the fish: a crouch as the fish comes
// down, a hop forward with a paw out, and a landing with the paw pinning it.
// `t` is seconds into the shot; `since` seconds since the fish landed.
const POUNCE = { from: 208, to: 199, hop: 0.25 };
const pouncing = (t: number, since: number): CatProps => ({
  ...PEER_LEFT,
  x: lerp(POUNCE.from, POUNCE.to, move(since, 0, POUNCE.hop)),
  y: PEER_LEFT.y - 4 * Math.sin(Math.PI * clamp01(since / POUNCE.hop)),
  look: 25 * move(t, 0.6, 0.9) - 55 * move(since, -0.2, POUNCE.hop),
  lean:
    -8 * move(since, -0.2, 0) +
    33 * move(since, 0, 0.15) -
    13 * move(since, 0.15, 0.4),
  paw: move(since, 0, 0.12) - 0.3 * move(since, POUNCE.hop, POUNCE.hop + 0.25),
});
// In the last shot the cat lifts its fish on the coda's second note.
const LIFT = 0.75;

// The gift: a fish clears the gunwale and lands on the foredeck by the cat.
const GIFT: Leap = {
  from: [216, 425],
  to: [192, 343],
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
      "Out of the dark, a tiny boat in the moon's silver path. His line hangs straight down to the float, beside the moon's reflection.",
    sound: "Intro, then the tune. The sea.",
    spec: (_, film) => fishing(WIDE, wander(film), MOON_HEIGHT.wide),
    panel: 2,
    fadeIn: 1.4,
  },
  {
    id: "02",
    bars: [5, 7],
    framing: "Medium",
    title: "Nothing bites",
    action: "He waits with the rod out; the cat watches the float.",
    sound: "The tune. A creak of the boat.",
    spec: (_, film) => fishing(MEDIUM, wander(film), MOON_HEIGHT.medium),
    panel: 1.5,
  },
  {
    id: "03",
    bars: [7, 8],
    framing: "Close",
    title: "The float beside the moon",
    action: "His float bobs beside the moon's reflection, never on it.",
    sound: "The tune's last phrase. Water lapping.",
    spec: (t, film) => ({
      ...fishing(WATER, wander(film), MOON_HEIGHT.water),
      cat: undefined,
      // Each bob of the float sends out a ring.
      ripple: { at: FLOAT, radius: 16 * ((t + 0.3) % 0.9) },
    }),
    panel: 1,
  },
  {
    id: "04",
    bars: [8, 10],
    framing: "Close",
    title: "He nods off",
    action:
      "His eyelids droop, twice. He nods, jerks awake, then nods off for good.",
    sound: "The tune's last phrase. A long, sleepy breath.",
    spec: (t, film) => ({
      ...fishing(NOD, wander(film), MOON_HEIGHT.medium),
      fisherman: noddingOff(t),
      zzz: t >= NODDED_OFF ? t - NODDED_OFF : undefined,
    }),
    panel: 2.6,
    fadeOut: 0.5,
  },
  {
    id: "05",
    bars: [10, 12],
    framing: "Medium",
    title: "Asleep",
    action:
      "He sleeps. The moon drifts on across the sky, and its reflection wanders into his hook.",
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
        zzz: ASLEEP + t,
      };
    },
    panel: 2,
    fadeIn: 0.6,
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
      "The reflection has wandered into his hook. The float twitches, then plunges under: it is hooked.",
    sound: "The tug: two plucks. A plop, the reel clicks.",
    spec: (t) => {
      // A twitch on the first pluck, the plunge on the second.
      const twitch = t < 0.15 ? 1.5 : 0;
      const plunged = t >= BEAT;
      const jolt = Math.max(
        ramp(t, 0, 0.3, 0.5, 0),
        ramp(t, BEAT, BEAT + 0.4, 1, 0),
      );
      return {
        ...fishing(WATER, HOOKED[0], MOON_HEIGHT.water),
        cat: undefined,
        float: plunged ? undefined : [FLOAT[0], FLOAT[1] + twitch],
        ripple: plunged ? undefined : { at: FLOAT, radius: 3 + 14 * t },
        wobble: 0.2 + 0.8 * jolt,
        rod: {
          ...ROD,
          bend: plunged ? 6 : ROD.bend + twitch,
          line: { to: FLOAT, slack: 0 },
        },
        splashes: [{ at: FLOAT, size: 6, age: t - BEAT }],
        catchGlow: plunged
          ? { at: HOOKED, strength: ramp(t, BEAT, 1.5, 0.3, 0.7) }
          : undefined,
      };
    },
    panel: 0.85,
  },
  {
    id: "07",
    bars: [13, 14],
    framing: "Medium",
    title: "Hooked",
    action:
      "Everything holds still. The line is taut and the rod bends slowly down; he sleeps on. Only the cat looks at the line.",
    sound: "The music holds its breath: the sea and one low cello note.",
    spec: (t) => ({
      ...DOZE,
      fisherman: dozingOff(3),
      moon: skyMoon(MEDIUM, HOOKED[0], MOON_HEIGHT.medium),
      reflection: HOOKED,
      wobble: 0.3,
      rod: {
        angle: -37.7,
        length: 70,
        bend: lerp(3, 22, move(t, 0.1, 1.3)),
        line: { to: HOOKED, slack: 0 },
      },
      float: undefined,
      catchGlow: { at: HOOKED, strength: 0.7 },
      cat: { ...PEER_LEFT, look: -25 * move(t, 0.3, 0.7) },
      zzz: ASLEEP + 3 + 1.5 + t,
    }),
    panel: 1,
  },
  {
    id: "08",
    bars: [14, 17],
    framing: "Medium",
    title: "He hauls the moon down",
    action:
      "He jolts awake and hauls: on every beat he lowers the rod and heaves it up again, the rod bent double. Each heave drags the reflection toward the boat and the moon down the sky. The cat stares.",
    sound: "The haul: driving plucks. The reel whirs.",
    spec: (t) => {
      const hooked = hauledReflection(t);
      const [x, y] = haulMoon(t);
      const { pose, rod, bend } = haulAt(t);
      return {
        ...HAUL,
        camera: MEDIUM_WIDE,
        fisherman: pose,
        moon: { in: "sky", x, y, r: 11 },
        reflection: hooked,
        wobble: 0.6,
        rod: { angle: rod, length: 72, bend, line: { to: hooked, slack: 0 } },
        catchGlow: { at: hooked, strength: 1 },
        // The cat follows the moon down to the horizon past the bow.
        cat: { ...PEER_RIGHT, look: lerp(55, 5, haulSteps(t)) },
      };
    },
    panel: 2.2,
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
    id: "09",
    bars: [17, 18],
    framing: "Medium",
    title: "The moon comes out of the water",
    action:
      "As the moon sinks below the horizon, it bursts out of the sea on his line.",
    sound: "The catch: the harp sweeps up. A great splash.",
    spec: (t) => {
      const ball: Vec2 = [LANDED[0], caughtY(t)];
      // The last heave lands it, and the rod springs back as it comes free.
      const top = hauling(1);
      return {
        camera: CATCH,
        moon: {
          in: "world",
          x: ball[0],
          y: ball[1],
          r: 12,
          waterline: LANDED[1],
        },
        setting: { x: SETTING_X, y: settingY(t), r: 11 },
        moonlight: ramp(t, 0, 0.4, 1, 0),
        fisherman: top.pose,
        rod: {
          angle: top.rod,
          length: 72,
          bend: lerp(top.bend, 10, move(t, 0, 0.5)),
          line: { to: ball, slack: 0 },
        },
        splashes: [{ at: LANDED, size: 15, age: t }],
        cat: { ...PEER_RIGHT, look: 5 },
      };
    },
    panel: 0.3,
    fadeOut: 0.5,
    notation: () => ({
      arrows: [
        alongside(
          [SETTING_X, horizonIn(CATCH) - 30],
          [SETTING_X, horizonIn(CATCH) + 2],
          -20,
        ),
        alongside(
          onScreen(CATCH, [LANDED[0], LANDED[1] + 10]),
          onScreen(CATCH, [LANDED[0], LANDED[1] - 24]),
          -34,
        ),
      ],
    }),
  },
  {
    id: "10",
    bars: [18, 20],
    framing: "Medium",
    title: "The moon in his bucket",
    action: "The moon glows in the bucket, lighting his face from below.",
    sound: "Wonder: the tune on high piano. Drips.",
    spec: () => KEY_IMAGE,
    panel: 1.5,
    fadeIn: 0.75,
  },
  {
    id: "11",
    bars: [20, 22],
    framing: "Close",
    title: "Wonder",
    action: "His face in the moonlight; a slow smile.",
    sound: "Wonder.",
    spec: (t) => ({
      ...KEY_IMAGE,
      camera: FACE,
      fisherman: { ...POSES.holdBucket, smile: move(t, 0.6, 2.2) },
    }),
    panel: 2.4,
  },
  {
    id: "12",
    bars: [22, 23],
    framing: "Close",
    title: "The cat reaches",
    action: "The cat stretches a paw toward the glow.",
    sound: "The violin answers. A curious chirp.",
    spec: (t) => ({
      ...KEY_IMAGE,
      camera: CAT,
      cat: { ...KEY_CAT, paw: move(t, 0.2, 0.7) - 0.4 * move(t, 1.1, 1.4) },
    }),
    panel: 0.9,
  },
  {
    id: "13",
    bars: [23, 25],
    framing: "Close",
    title: "It dims",
    action: "The moon's glow flickers and fades, like a fish out of water.",
    sound: "The dimming: the tune in minor on the violin.",
    spec: (t) => ({
      ...KEY_IMAGE,
      camera: PAIL,
      glow: ramp(t, 0, 3, 1, 0.35) * flicker(t),
    }),
    panel: 2.6,
  },
  {
    id: "14",
    bars: [25, 27],
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
    id: "15",
    bars: [27, 28],
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
        splashes: [{ at: [x, RELEASE.water], size: 4, age: t - RELEASE.lands }],
      };
    },
    panel: 0.8,
  },
  {
    id: "16",
    bars: [28, 29],
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
    panel: 1,
    fadeIn: 1,
  },
  {
    id: "17",
    bars: [29, 32],
    framing: "Wide",
    title: "The moon rises",
    action:
      "The sea glows from below; the moon rises out of the water past the bow, where it set, and climbs into the sky. He and the cat watch it go.",
    sound: "The rise: the clarinet reaches up. A swelling shimmer.",
    spec: (t) => {
      const y = ramp(t, 0.5, 4.5, 450, 250);
      return {
        camera: WIDE,
        moon: { in: "world", x: SETS_OVER, y, r: 12, waterline: 440 },
        moonlight: ramp(t, 2, 4.5, 0, 0.8),
        seaGlow: {
          at: [SETS_OVER, 440],
          radius: 70,
          strength: ramp(t, 0, 1.5, 0.2, 1),
        },
        fisherman: lookingUp(t, [1.5, 3.5]),
        bucket: EMPTY_BUCKET,
        cat: { ...PEER_RIGHT, look: 45 * move(t, 1.5, 4) },
      };
    },
    panel: 1.8,
  },
  {
    id: "18",
    bars: [32, 36],
    framing: "Medium",
    title: "Silver light",
    action: "The moon rides high again. Fish leap through its silver path.",
    sound: "The finale: home in E. Splashes.",
    spec: (t) => ({
      ...fishing(MEDIUM_WIDE, REFLECTION[0], MOON_HEIGHT.medium),
      cat: { ...PEER_RIGHT, look: 15 },
      fish: FINALE_LEAPS.flatMap((l) => leaping(l, t) ?? []),
      splashes: FINALE_LEAPS.flatMap((l) => leapSplashes(l, t, 3.5)),
    }),
    panel: 3,
  },
  {
    id: "19",
    bars: [36, 38],
    framing: "Medium",
    title: "A gift",
    action:
      "One fish leaps into the boat. The cat crouches, pounces and pins it with a paw; he smiles.",
    sound: "The last phrase again. A flop, a happy mew.",
    spec: (t) => {
      const lands = GIFT.start + GIFT.duration;
      const pinned = lands + POUNCE.hop;
      // It flops on the deck until the cat lands on it.
      const flop = t < pinned ? (Math.floor(t * 6) % 2 ? 20 : -20) : 0;
      return {
        ...fishing(MEDIUM, REFLECTION[0], MOON_HEIGHT.medium),
        // He smiles at the cat's luck.
        fisherman: {
          ...POSES.fish,
          smile: move(t, pinned + 0.2, pinned + 0.9),
        },
        fish:
          t < lands
            ? [GIFT].flatMap((l) => leaping(l, t) ?? [])
            : [{ at: GIFT.to, angle: 180 + flop, size: GIFT.size }],
        splashes: leapSplashes(GIFT, t, 3, false),
        cat: pouncing(t, t - lands),
      };
    },
    panel: 1.7,
  },
  {
    id: "20",
    bars: [38, 40],
    framing: "Close",
    title: "The cat's prize",
    action:
      "On the ta-dum the cat bites its fish and lifts its head, the fish dangling from its mouth. An iris closes on it.",
    sound: "The coda: a plucked ta-dum and a last high note.",
    spec: (t) => {
      const lifted = t >= LIFT;
      const pose: CatProps = {
        ...PEER_LEFT,
        x: POUNCE.to,
        // It bends to bite, then snaps its head up on the beat.
        look: lifted
          ? lerp(-38, 20, move(t, LIFT, LIFT + 0.15))
          : lerp(-30, -38, move(t, 0.3, 0.7)),
        lean: lerp(12, 0, move(t, LIFT, LIFT + 0.2)),
        paw: lifted ? 0 : 0.7,
      };
      const [mx, my] = catFigure(pose).mouth;
      // The fish hangs by its head from the cat's mouth and swings to rest.
      const settle = t - LIFT;
      const swing = lifted
        ? 16 * Math.sin(settle * 11) * Math.exp(-settle * 3)
        : 0;
      return {
        ...fishing(PRIZE, REFLECTION[0], MOON_HEIGHT.medium),
        fish: [
          lifted
            ? { at: [mx + 0.5, my + 5.5], angle: -95 + swing, size: GIFT.size }
            : { at: GIFT.to, angle: 180, size: GIFT.size },
        ],
        cat: pose,
        // The iris pauses on its face before it shuts.
        iris: {
          at: [mx + 3, my - 2],
          radius:
            t < 2.2
              ? lerp(300, 46, move(t, 1.4, 2))
              : lerp(46, 0, move(t, 2.2, 2.6)),
        },
      };
    },
    panel: 1.3,
  },
];

export const shotStart = (s: Shot) => (s.bars[0] - 1) * BAR_SECONDS;
export const shotSeconds = (s: Shot) => (s.bars[1] - s.bars[0]) * BAR_SECONDS;

// The film at a frame: the shot playing and its scene, faded toward black
// where the shot fades in or out. Action moves on twos; ambient life follows
// the frame itself.
export const filmAt = (frame: number) => {
  const action = (Math.floor(frame / 2) * 2) / FPS;
  const shot =
    SHOTS.find((s) => action < shotStart(s) + shotSeconds(s)) ??
    SHOTS[SHOTS.length - 1];
  const t = action - shotStart(shot);
  const length = shotSeconds(shot);
  const spec = shot.spec(t, action);
  const fade = Math.max(
    spec.fade ?? 0,
    shot.fadeIn ? 1 - move(t, 0, shot.fadeIn) : 0,
    shot.fadeOut ? move(t, length - shot.fadeOut, length) : 0,
  );
  return { shot, spec: fade ? { ...spec, fade } : spec };
};

// The storyboard's frame of a shot, and its notation.
export const panelFrame = (s: Shot) =>
  Math.round((shotStart(s) + s.panel) * FPS);
export const panelNotation = (s: Shot): Notation =>
  s.notation?.(shotStart(s) + s.panel) ?? {};
