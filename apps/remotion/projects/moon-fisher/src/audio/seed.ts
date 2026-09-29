// One seeded generator for the whole score. It also replaces Math.random before
// Tone.js loads, so noise and reverb render identically each time.
let state = 20260929;

export const rand = () => {
  state = (state + 0x6d2b79f5) >>> 0;
  let t = state;
  t = Math.imul(t ^ (t >>> 15), t | 1);
  t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
  return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
};

Math.random = rand;
