export const W = 1080;
export const H = 1920;
export const FPS = 30;
export const DURATION = 30;
export const FRAMES = FPS * DURATION;
export const SAMPLE_RATE = 48000;

// 128 BPM makes 16 bars fill exactly 30 seconds; every cut sits on this grid.
export const BPM = 128;
export const BEAT = 60 / BPM;
/** Beat position → seconds. */
export const b = (beats: number) => beats * BEAT;

export const COLOR = {
  ink: '#050505',
  red: '#C80528',
  redHot: '#FF1E50',
  cyan: '#00D2E6',
  green: '#00E08A',
  yellow: '#FFD400',
  white: '#FFFFFF',
  glitchCyan: 'rgba(0,228,255,0.95)',
  glitchRed: 'rgba(255,30,80,0.95)',
} as const;

export const white = (alpha: number) => `rgba(255,255,255,${alpha})`;

/** Scene windows in beats. */
export const SCENE = {
  hook: [0, 8],
  slate: [8, 12],
  clock: [12, 16],
  pipeline: [16, 36],
  premiere: [36, 44],
  facts: [44, 56],
  cta: [56, 64],
} as const;

/** Text-safe area for a Reel: clear of Instagram's top bar, caption block and action icons. */
export const SAFE = { left: 90, right: 990, top: 250, bottom: 1450 };

/** The 48-hour clock starts Friday 15:00 on the event weekend. */
export const EVENT_SECONDS = 48 * 3600;
