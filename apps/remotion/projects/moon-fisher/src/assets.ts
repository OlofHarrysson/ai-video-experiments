// The asset register: everything the film draws, how a scene calls it, how
// far along it is and what it still needs. `drawBoatScene` labels its pixels
// with these names, so `scripts/tables.ts` can measure where each asset is on
// screen in every shot.

export type AssetName =
  | "fisherman"
  | "cat"
  | "boat"
  | "rod"
  | "float"
  | "bucket"
  | "fish"
  | "moon"
  | "sky"
  | "sea"
  | "glitter"
  | "reflection"
  | "water"
  | "glow"
  | "splash"
  | "ripple"
  | "zzz";

// Placeholder: stands in for the real thing. Rough: the intended design,
// still to be refined. Final: done.
export type Status = "placeholder" | "rough" | "final";

export type Asset = {
  name: string;
  kind: "Character" | "Prop" | "Set" | "Light" | "Effect";
  api: string;
  status: Status;
  // What it still needs, citing the shots that need it.
  next: string;
};

// In the order the register lists them.
export const ASSETS: Record<AssetName, Asset> = {
  fisherman: {
    name: "Fisherman",
    kind: "Character",
    api: "fisherman({ x, y, pose, facing })",
    status: "rough",
    next: "Poses: fish, doze, haul, holdBucket, lookUp, tip, with tweens for nodding off (04, 05), the waking jolt and his heaves (07), the last heave at the catch (08) and looking up (13, 16); he blinks. Needs a smile (10, 19), face detail for his close-ups (04, 10) and a fuller heave than a lean of the chest and arms.",
  },
  cat: {
    name: "Cat",
    kind: "Character",
    api: "cat({ x, y, pose, facing, look, paw })",
    status: "rough",
    next: "One pose, peer, with a head tilt and a front paw that reaches out (11, 18). Needs a pounce and a fish in its mouth (18, 19), a startle, and a tail that moves.",
  },
  moon: {
    name: "Moon",
    kind: "Prop",
    api: 'moonParts({ x, y, radius, glow, waterline }); spec.moon = { in: "sky" | "world" }',
    status: "rough",
    next: "The style frame's moon; it drifts, sets and rises. Needs a brighter burst as it leaves the sea (08) and water streaming off it.",
  },
  bucket: {
    name: "Bucket, with the moon in it",
    kind: "Prop",
    api: "bucket({ x, rimY, moon, tilt, glow })",
    status: "rough",
    next: "The style frame's hero. The moon drops out as he tips it (14) and flickers as it dims (12); it needs water spilling with it.",
  },
  float: {
    name: "Float",
    kind: "Prop",
    api: "spec.float = [x, y]",
    status: "placeholder",
    next: "Two ovals. Needs a drawn red-and-white float, its bob and its plunge (06).",
  },
  rod: {
    name: "Rod and line",
    kind: "Prop",
    api: "drawRod({ grip, angle, length, bend }); drawLine(from, to, slack)",
    status: "rough",
    next: "Needs a reel for the clicks and the whir (06, 07), and a bend that follows each heave (07).",
  },
  fish: {
    name: "Fish",
    kind: "Prop",
    api: "fishParts({ at, angle, size })",
    status: "placeholder",
    next: "A body and a tail, now leaping in arcs (17, 18) and flopping on the deck (18). Needs fins, an eye and a silver sheen, and the one the cat holds (19).",
  },
  boat: {
    name: "Boat",
    kind: "Set",
    api: "boatInterior(BOAT), boatHull(BOAT)",
    status: "rough",
    next: "Planks, ribs and rivets from the style frame. Needs a check of the bow where the cat's close-ups frame it (04, 11), and a gentle rock beyond the one-pixel bob.",
  },
  sky: {
    name: "Sky",
    kind: "Set",
    api: "drawSky, drawStars, drawMilkyWay",
    status: "rough",
    next: "Near final. It dissolves between moonlit and dark as the moon sets (08) and rises (16); its stars could twinkle more.",
  },
  sea: {
    name: "Sea",
    kind: "Set",
    api: "drawSea({ horizon, bands, swell })",
    status: "rough",
    next: "Near final. Its swell lines sway slowly.",
  },
  water: {
    name: "Water reflections",
    kind: "Effect",
    api: "reflectWater({ waterline, step })",
    status: "rough",
    next: "Near final; Olof likes it. Needs to break up around splashes and the plunging float (06, 08).",
  },
  reflection: {
    name: "Moon's reflection",
    kind: "Effect",
    api: "spec.reflection = [x, y], spec.wobble; drawMoonReflection",
    status: "rough",
    next: "Drifts and wobbles. Once hooked it only gains a halo; it should stretch and tear as he hauls it in (07).",
  },
  glitter: {
    name: "Moon's glitter path",
    kind: "Light",
    api: "drawMoonPath({ x, horizon, halfWidth })",
    status: "rough",
    next: "Near final. Should change shape with the moon's height as it comes down (07).",
  },
  glow: {
    name: "Moonlight glow",
    kind: "Light",
    api: "drawHalo, drawShaft; spec.seaGlow",
    status: "rough",
    next: "Halo and shaft around the caught moon, and the glow under the sea (16).",
  },
  splash: {
    name: "Splash",
    kind: "Effect",
    api: "spec.splash = { at, size }; drawSplash",
    status: "placeholder",
    next: "Scattered droplets and a ring, used for the float, the catch, the moon's release and the fish (06, 08, 14, 17, 18). Needs a crown that rises and falls over a few frames, sized to each.",
  },
  zzz: {
    name: "Sleep Z's",
    kind: "Effect",
    api: "spec.zzz = seconds asleep",
    status: "rough",
    next: "Pixel Z's drifting up from his head (04, 05). Could take a hand-drawn letterform.",
  },
  ripple: {
    name: "Ripple",
    kind: "Effect",
    api: "spec.ripple = { at, radius }; drawRipple",
    status: "placeholder",
    next: "Broken rings at one radius. Needs rings that fade as they spread (03).",
  },
};

// Sound effects the storyboard asks for, by shot. The score already carries
// the sea; the rest are not started.
export const SOUND_CUES: readonly { cue: string; shots: string[] }[] = [
  { cue: "A creak of the boat", shots: ["02"] },
  { cue: "A plip, water lapping", shots: ["03"] },
  { cue: "A faint, glassy shiver", shots: ["04"] },
  { cue: "A plop, the reel clicks", shots: ["06"] },
  { cue: "The reel whirs", shots: ["07"] },
  { cue: "A great splash", shots: ["08"] },
  { cue: "Drips", shots: ["09"] },
  { cue: "A curious chirp", shots: ["11"] },
  { cue: "A soft plop", shots: ["14"] },
  { cue: "A swelling shimmer", shots: ["16"] },
  { cue: "Splashes", shots: ["17"] },
  { cue: "A flop, a happy mew", shots: ["18"] },
];
