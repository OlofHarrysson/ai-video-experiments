// One clock for picture and, later, music: 120 BPM at 30 fps puts every beat on frame multiples of 15.
export const FPS = 30;
export const BPM = 120;
export const BEAT = 60 / BPM;
export const BAR = BEAT * 4;
export const DURATION = 45;
export const DURATION_FRAMES = DURATION * FPS;
export const WIDTH = 1920;
export const HEIGHT = 1080;

// Story beats, in seconds.
export const ACT = {
  open: [0, 6],
  race: [6, 12],
  build: [12, 18],
  wall: [18, 24],
  freeze: [24, 25],
  reveal: [25, 33],
  end: [33, 45],
} as const;

/** World time: everything in the world holds still through the freeze, then carries on. */
export const worldClock = (t: number) => {
  const [f0, f1] = ACT.freeze;
  if (t < f0) return t;
  if (t < f1) return f0;
  return t - (f1 - f0);
};

export const beats = (n: number) => n * BEAT;
