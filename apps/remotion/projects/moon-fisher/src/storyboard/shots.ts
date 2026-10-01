import type { Camera } from "../pixel/pix";
import type { Vec2 } from "../pixel/shapes";
import { HORIZON, type SceneSpec } from "../stills/boatScene";
import { KEY_IMAGE } from "../stills/keyImage";
import { DOZE, FLOAT, HAUL, REFLECTION, SKY_MOON, TIP } from "../stills/poses";
import { BAR_SECONDS } from "../timing";

// The film, shot by shot, cut on the score's bars. Each shot is a scene spec
// as a function of the seconds since the shot began; the storyboard shows
// one moment of it, and the animatic plays it through.
export type Shot = {
  id: string;
  // [first bar, bar after the last]
  bars: readonly [number, number];
  framing: "Wide" | "Medium" | "Close";
  title: string;
  action: string;
  sound: string;
  spec: (t: number) => SceneSpec;
  // Seconds into the shot shown on the storyboard.
  panel: number;
  // Storyboard notation over the panel, in design-frame units: arrows for
  // what travels during the shot, and shake lines around what shivers.
  arrows?: (readonly [Vec2, Vec2])[];
  shakes?: { at: Vec2; r: number }[];
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

// In the wide frame the moon stands right above its reflection.
const WIDE_MOON = { in: "sky", x: 152, y: 70, r: 11 } as const;
// Out of frame above the water close-ups; it still lights them.
const HIGH_MOON = { in: "sky", x: 135, y: -140, r: 11 } as const;
// Up and to the left of the cat, which looks up at it.
const CAT_MOON = { in: "sky", x: 50, y: 135, r: 11 } as const;

// The tug drags the reflection toward the float; the haul brings it in
// beside the boat while the moon comes down the sky to the horizon.
const HOOKED: Vec2 = [166, 443];
const LANDED: Vec2 = [166, 420];

const ROD = {
  angle: -28,
  length: 64,
  bend: 2,
  line: { to: FLOAT, slack: 6 },
};
// Out on the foredeck, clear of the fishing line.
const PEER_LEFT = { x: 208, y: 342, pose: "peer", facing: "left" } as const;
const PEER_RIGHT = { ...PEER_LEFT, facing: "right" } as const;
const EMPTY_BUCKET = { at: "knees", x: 148, rimY: 326 } as const;

// Fishing under the moon: the setup, and the ending that mirrors it.
const fishing = (camera: Camera, moon: SceneSpec["moon"]): SceneSpec => ({
  camera,
  moon,
  reflection: REFLECTION,
  fisherman: "fish",
  rod: ROD,
  float: FLOAT,
  cat: PEER_LEFT,
});

const ramp = (t: number, from: number, to: number, a: number, b: number) =>
  a + (b - a) * Math.min(1, Math.max(0, (t - from) / (to - from)));

const mix = (a: Vec2, b: Vec2, p: number): Vec2 => [
  a[0] + (b[0] - a[0]) * p,
  a[1] + (b[1] - a[1]) * p,
];

// Where a world point lands in the design frame.
const onScreen = (c: Camera, [x, y]: Vec2): Vec2 => [
  (x - c.x) * c.zoom + c.sx,
  (y - c.y) * c.zoom + c.sy,
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

// He hauls the moon down the sky, from high above its reflection to the
// horizon just past the bow, the stretch the boat does not hide. Sky moons
// are placed in the design frame, over these world columns.
const SETS_OVER = 243;
const HAUL_MOON_FROM: Vec2 = [onScreen(MEDIUM_WIDE, [172, 0])[0], 55];
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

export const SHOTS: Shot[] = [
  {
    id: "01",
    bars: [1, 5],
    framing: "Wide",
    title: "The boat under the moon",
    action:
      "A tiny boat in the moon's silver path. His float bobs beside the moon's reflection.",
    sound: "Intro, then the tune. The sea.",
    spec: () => fishing(WIDE, WIDE_MOON),
    panel: 2,
  },
  {
    id: "02",
    bars: [5, 8],
    framing: "Medium",
    title: "Nothing bites",
    action: "He waits with the rod out; the cat watches the float.",
    sound: "The tune. A creak of the boat.",
    spec: () => fishing(MEDIUM, SKY_MOON),
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
    spec: (t) => ({
      ...fishing(WATER, HIGH_MOON),
      cat: undefined,
      ripple: { at: FLOAT, radius: 16 * (t - 0.1) },
      wobble: ramp(t, 0.75, 0.9, 0, 1) * ramp(t, 0.9, 1.5, 1, 0.5),
    }),
    panel: 1,
    shakes: [{ at: onScreen(WATER, REFLECTION), r: 7.5 * WATER.zoom }],
  },
  {
    id: "04",
    bars: [9, 10],
    framing: "Close",
    title: "The moon shivers",
    action: "Up in the sky the moon shivers too. Only the cat looks up.",
    sound: "The tune ends. A faint, glassy shiver.",
    spec: (t) => ({
      ...fishing(CAT_SKY, { ...CAT_MOON, shiver: t < 1 ? 2 : 0 }),
      cat: { ...PEER_LEFT, look: ramp(t, 0.2, 0.4, 0, 50) },
    }),
    panel: 0.75,
    shakes: [{ at: [CAT_MOON.x, CAT_MOON.y], r: CAT_MOON.r }],
  },
  {
    id: "05",
    bars: [10, 12],
    framing: "Medium",
    title: "He dozes off",
    action: "His head sinks; the hat slides over his eyes.",
    sound: "The doze: a lazy clarinet.",
    spec: () => ({ ...DOZE, cat: PEER_LEFT }),
    panel: 1.5,
  },
  {
    id: "06",
    bars: [12, 13],
    framing: "Close",
    title: "A tug",
    action:
      "The float plunges under, and the reflection jerks after it: it is hooked.",
    sound: "The tug: two plucks. A plop, the reel clicks.",
    spec: (t) => {
      const jerk = ramp(t, 0.15, 0.3, 0, 1);
      const at = mix(REFLECTION, HOOKED, jerk);
      return {
        ...fishing(WATER, HIGH_MOON),
        cat: undefined,
        float: undefined,
        reflection: at,
        wobble: jerk,
        rod: { ...ROD, line: { to: FLOAT, slack: 0 } },
        splash: { at: FLOAT, size: 6 },
        catchGlow: { at, strength: 0.5 * jerk },
      };
    },
    panel: 0.4,
    arrows: [
      alongside(onScreen(WATER, REFLECTION), onScreen(WATER, FLOAT), -34, 0.05),
    ],
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
      const at = hauledReflection(t);
      const [x, y] = haulMoon(t);
      return {
        ...HAUL,
        camera: MEDIUM_WIDE,
        moon: { in: "sky", x, y, r: 11 },
        reflection: at,
        wobble: 0.6,
        rod: { angle: -52, length: 72, bend: 18, line: { to: at, slack: 0 } },
        catchGlow: { at, strength: 1 },
        cat: { ...PEER_LEFT, look: 30 },
      };
    },
    panel: 2,
    arrows: [
      alongside(HAUL_MOON_FROM, HAUL_MOON_TO, 22, 0.15),
      alongside(
        onScreen(MEDIUM_WIDE, HOOKED),
        onScreen(MEDIUM_WIDE, LANDED),
        20,
      ),
    ],
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
        splash: { at: LANDED, size: 7 },
        cat: { ...PEER_LEFT, look: 20 },
      };
    },
    panel: 0.3,
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
    spec: () => ({ ...KEY_IMAGE, fisherman: "lookUp", glow: 0.32 }),
    panel: 1.5,
  },
  {
    id: "14",
    bars: [26, 27],
    framing: "Medium",
    title: "He lets it go",
    action: "He tips the bucket over the side; the moon slides into the sea.",
    sound: "The release: the harp sinks. A soft plop.",
    spec: (t) => ({
      ...TIP,
      glow: 0.4,
      bucket: { at: "hands", tilt: ramp(t, 0, 1.2, 20, 60), offset: [10, 4] },
    }),
    panel: 1,
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
    spec: () => ({
      ...fishing(WIDE, WIDE_MOON),
      cat: PEER_RIGHT,
      fish: [
        { at: [52, 392], angle: -40, size: 2.2 },
        { at: [118, 412], angle: -75, size: 2.2 },
        { at: [240, 396], angle: -130, size: 2.2 },
      ],
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
    spec: () => ({
      ...fishing(MEDIUM, SKY_MOON),
      fish: [{ at: [186, 316], angle: 35, size: 1.3 }],
    }),
    panel: 1.5,
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
      ...fishing(WIDE, WIDE_MOON),
      fish: [{ at: [198, 341], angle: 180, size: 1.6 }],
    }),
    panel: 3,
  },
];

export const shotStart = (s: Shot) => (s.bars[0] - 1) * BAR_SECONDS;
export const shotSeconds = (s: Shot) => (s.bars[1] - s.bars[0]) * BAR_SECONDS;
