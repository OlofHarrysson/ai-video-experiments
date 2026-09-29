// One grid drives both the picture and the score. The score is a lullaby in
// 6/8 with a dotted-quarter pulse of 60: a bar every two seconds and an
// eighth every eight frames at 24 fps. Bars are numbered from 1.
export const FPS = 24;
export const BAR_SECONDS = 2;
export const EIGHTH_SECONDS = BAR_SECONDS / 6;
export const BARS = 30;
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
  lullaby: [2, 10],
  // Turn
  tug: [10, 11],
  haul: [11, 13],
  catch: [13, 14],
  wonder: [14, 18],
  dimming: [18, 21],
  // Payoff
  release: [21, 22],
  darkness: [22, 23],
  rise: [23, 25],
  finale: [25, 29],
  coda: [29, 31],
} as const satisfies Record<string, readonly [number, number]>;

export type Section = keyof typeof SECTIONS;
