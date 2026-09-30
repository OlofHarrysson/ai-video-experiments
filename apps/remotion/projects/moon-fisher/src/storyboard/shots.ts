import type { Camera } from "../pixel/pix";
import type { Vec2 } from "../pixel/shapes";
import type { SceneSpec } from "../stills/boatScene";
import { KEY_IMAGE } from "../stills/keyImage";
import { DOZE, HAUL, REFLECTION, SKY_MOON, TIP } from "../stills/poses";
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
};

const WIDE: Camera = { x: 150, y: 330, zoom: 0.75, sx: 135, sy: 337.5 };
const MEDIUM = KEY_IMAGE.camera;
const MEDIUM_WIDE: Camera = { x: 150, y: 330, zoom: 1.2, sx: 140, sy: 285 };
const FACE: Camera = { x: 128, y: 298, zoom: 3.2, sx: 150, sy: 230 };
const CAT: Camera = { x: 192, y: 322, zoom: 3.4, sx: 130, sy: 250 };
const PAIL: Camera = { x: 148, y: 322, zoom: 3, sx: 135, sy: 240 };
// Looking down at the float, in the middle of the moon's glitter.
const WATER: Camera = { x: 172, y: 440, zoom: 3.5, sx: 135, sy: 260 };

// In the wide frame the moon stands right above its reflection.
const WIDE_MOON = { in: "sky", x: 152, y: 70, r: 11 } as const;
// Out of frame above the water close-ups; it still lights them.
const HIGH_MOON = { in: "sky", x: 135, y: -140, r: 11 } as const;

const ROD = {
  angle: -28,
  length: 64,
  bend: 2,
  line: { to: REFLECTION, slack: 6 },
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
  float: REFLECTION,
  cat: PEER_LEFT,
});

const ramp = (t: number, from: number, to: number, a: number, b: number) =>
  a + (b - a) * Math.min(1, Math.max(0, (t - from) / (to - from)));

export const SHOTS: Shot[] = [
  {
    id: "01",
    bars: [1, 5],
    framing: "Wide",
    title: "The boat under the moon",
    action:
      "A tiny boat in the moon's silver path. The float bobs in the moon's reflection.",
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
    bars: [8, 10],
    framing: "Close",
    title: "The float in the moon",
    action: "The float rides the moon's wobbling reflection.",
    sound: "The tune ends. Water lapping.",
    spec: () => ({ ...fishing(WATER, HIGH_MOON), cat: undefined }),
    panel: 1,
  },
  {
    id: "04",
    bars: [10, 12],
    framing: "Medium",
    title: "He dozes off",
    action: "His head sinks; the hat slides over his eyes.",
    sound: "The doze: a lazy clarinet.",
    spec: () => ({ ...DOZE, cat: PEER_LEFT }),
    panel: 1.5,
  },
  {
    id: "05",
    bars: [12, 13],
    framing: "Close",
    title: "A tug",
    action: "The float plunges under; the reflection shatters.",
    sound: "The tug: two plucks. A plop, the reel clicks.",
    spec: () => ({
      ...fishing(WATER, HIGH_MOON),
      cat: undefined,
      float: undefined,
      rod: { ...ROD, line: { to: REFLECTION, slack: 0 } },
      splash: { at: REFLECTION, size: 4 },
    }),
    panel: 0.4,
  },
  {
    id: "06",
    bars: [13, 16],
    framing: "Medium",
    title: "He hauls",
    action: "He jolts awake and hauls; the rod bends double. The cat startles.",
    sound: "The haul: driving plucks. The reel whirs.",
    spec: () => ({ ...HAUL, camera: MEDIUM_WIDE, cat: PEER_RIGHT }),
    panel: 2.5,
  },
  {
    id: "07",
    bars: [16, 17],
    framing: "Wide",
    title: "The moon comes out of the water",
    action:
      "A glowing moon bursts from the sea on his line. The one in the sky is gone.",
    sound: "The catch: the harp sweeps up. A great splash.",
    spec: (t) => {
      const y = ramp(t, 0, 1.2, 440, 402);
      const moon: Vec2 = [178, y];
      return {
        camera: WIDE,
        moon: { in: "world", x: moon[0], y, r: 12, waterline: 443 },
        fisherman: "haul",
        rod: { angle: -52, length: 72, bend: 18, line: { to: moon, slack: 0 } },
        splash: { at: [174, 443], size: 7 },
        cat: PEER_RIGHT,
      };
    },
    panel: 0.9,
  },
  {
    id: "08",
    bars: [17, 19],
    framing: "Medium",
    title: "The moon in his bucket",
    action: "The moon glows in the bucket, lighting his face from below.",
    sound: "Wonder: the tune on high piano. Drips.",
    spec: () => KEY_IMAGE,
    panel: 1.5,
  },
  {
    id: "09",
    bars: [19, 21],
    framing: "Close",
    title: "Wonder",
    action: "His face in the moonlight; a slow smile.",
    sound: "Wonder.",
    spec: () => ({ ...KEY_IMAGE, camera: FACE }),
    panel: 1.5,
  },
  {
    id: "10",
    bars: [21, 22],
    framing: "Close",
    title: "The cat reaches",
    action: "The cat stretches a paw toward the glow.",
    sound: "The violin answers. A curious chirp.",
    spec: () => ({ ...KEY_IMAGE, camera: CAT }),
    panel: 0.75,
  },
  {
    id: "11",
    bars: [22, 24],
    framing: "Close",
    title: "It dims",
    action: "The moon's glow flickers and fades, like a fish out of water.",
    sound: "The dimming: the tune in minor on the violin.",
    spec: (t) => ({ ...KEY_IMAGE, camera: PAIL, glow: ramp(t, 0, 3, 1, 0.35) }),
    panel: 2.6,
  },
  {
    id: "12",
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
    id: "13",
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
    id: "14",
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
    id: "15",
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
    id: "16",
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
    id: "17",
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
    id: "18",
    bars: [37, 41],
    framing: "Wide",
    title: "Like the beginning",
    action:
      "The first shot again: the moon high, its reflection by his float. He smiles; the cat has its fish.",
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
