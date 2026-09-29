// One grid drives both the picture and the score. The score is a lilting
// folk tune in 6/8 with a dotted-quarter pulse of 80: a bar every 1.5 s and
// an eighth every six frames at 24 fps. Bars are numbered from 1.
export const FPS = 24;
export const BAR_SECONDS = 1.5;
export const EIGHTH_SECONDS = BAR_SECONDS / 6;
export const BARS = 40;
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
  haul: [13, 16],
  catch: [16, 17],
  wonder: [17, 22],
  dimming: [22, 26],
  // Payoff
  release: [26, 27],
  darkness: [27, 28],
  rise: [28, 31],
  finale: [31, 37],
  coda: [37, 41],
} as const satisfies Record<string, readonly [number, number]>;

export type Section = keyof typeof SECTIONS;
