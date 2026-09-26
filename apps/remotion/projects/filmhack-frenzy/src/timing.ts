// One beat grid drives both the picture and the score.
// 150 BPM at 30 fps puts every beat on a whole frame: 12 frames per beat, 3 per sixteenth.
export const FPS = 30;
export const BPM = 150;
export const FRAMES_PER_BEAT = (FPS * 60) / BPM;
export const TOTAL_BEATS = 64;
export const DURATION_IN_FRAMES = TOTAL_BEATS * FRAMES_PER_BEAT;
export const DURATION_IN_SECONDS = DURATION_IN_FRAMES / FPS;

/** Beats → frames, for the picture. */
export const beat = (beats: number) => Math.round(beats * FRAMES_PER_BEAT);

/** Beats → seconds, for the score. */
export const seconds = (beats: number) => (beats * 60) / BPM;

/** Scene windows in beats. */
export const SCENES = {
  coldOpen: [0, 4],
  stopScrolling: [4, 8],
  lightsCameraAction: [8, 12],
  prompts: [12, 16],
  pipeline: [16, 20],
  crowd: [20, 24],
  chaos: [24, 28],
  sunday: [28, 32],
  premiere: [32, 40],
  facts: [40, 52],
  cta: [52, 64],
} as const;

export type SceneName = keyof typeof SCENES;

export const sceneFrames = (name: SceneName) => beat(SCENES[name][1] - SCENES[name][0]);

/** The 48-hour countdown runs through the montage and hits zero half a beat before the breakdown. */
export const CLOCK_START_BEAT = 12;
export const CLOCK_ZERO_BEAT = 27.5;
