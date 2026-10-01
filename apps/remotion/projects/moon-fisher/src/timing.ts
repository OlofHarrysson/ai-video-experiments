// One grid drives both the picture and the score. The score is a lilting
// folk tune in 6/8 with a dotted-quarter pulse of 80: a bar every 1.5 s and
// an eighth every six frames at 24 fps. Bars are numbered from 1.
export const FPS = 24;
export const BAR_SECONDS = 1.5;
export const EIGHTH_SECONDS = BAR_SECONDS / 6;
export const BARS = 39;
export const DURATION_SECONDS = BARS * BAR_SECONDS;
export const DURATION_FRAMES = DURATION_SECONDS * FPS;

// Seconds from the start of the film to an eighth within a bar.
export const at = (bar: number, eighth = 0): number =>
  (bar - 1) * BAR_SECONDS + eighth * EIGHTH_SECONDS;

export const frameAt = (bar: number, eighth = 0): number =>
  Math.round(at(bar, eighth) * FPS);

// The story on the grid: [first bar, bar after the last].
export const SECTIONS = {
  // Setup
  intro: [1, 2],
  tune: [2, 10],
  doze: [10, 12],
  // Turn
  tug: [12, 13],
  hooked: [13, 14],
  haul: [14, 17],
  catch: [17, 18],
  wonder: [18, 23],
  dimming: [23, 27],
  // Payoff
  release: [27, 28],
  darkness: [28, 29],
  rise: [29, 32],
  finale: [32, 38],
  coda: [38, 40],
} as const satisfies Record<string, readonly [number, number]>;

export type Section = keyof typeof SECTIONS;
