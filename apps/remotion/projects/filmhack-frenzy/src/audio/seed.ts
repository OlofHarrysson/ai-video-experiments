// One seeded generator for the whole score. It also replaces Math.random before
// Tone.js loads, so Tone's noise buffers render identically each time too.
let state = 20261112;

export const rand = () => {
  state = (state + 0x6d2b79f5) >>> 0;
  let t = state;
  t = Math.imul(t ^ (t >>> 15), t | 1);
  t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
  return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
};

Math.random = rand;
