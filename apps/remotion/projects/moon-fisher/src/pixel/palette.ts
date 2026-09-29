// The film's master palette. Every pixel on screen is one of these colors.
// Indices are stable: ramps, ladders and scenes refer to them by position.
export const PALETTE = [
  // Night: sky, sea and shadow
  "#07080f", // 0 ink
  "#0d1222", // 1 night1
  "#141d36", // 2 night2
  "#1c2a4a", // 3 night3
  "#263a60", // 4 night4
  "#334d78", // 5 night5
  "#466593", // 6 night6
  // Moonlight
  "#6582ab", // 7 silver1
  "#8ea7c8", // 8 silver2
  "#bccbde", // 9 silver3
  "#e3e9ee", // 10 silver4
  "#fbf6e4", // 11 moon
  // Warm: oilskin, wood, skin and cat
  "#1f1418", // 12 umber0
  "#3a2224", // 13 umber1
  "#5a3a31", // 14 umber2
  "#7d5a41", // 15 umber3
  "#a07c46", // 16 ochre1
  "#c9a55a", // 17 ochre2
  "#ecd28a", // 18 ochre3
  "#9c5f4e", // 19 skin1
  "#d08f72", // 20 skin2
  "#f2c4a0", // 21 skin3
  "#b4602f", // 22 ginger1
  "#e39448", // 23 ginger2
] as const;

export const C = {
  ink: 0,
  night1: 1,
  night2: 2,
  night3: 3,
  night4: 4,
  night5: 5,
  night6: 6,
  silver1: 7,
  silver2: 8,
  silver3: 9,
  silver4: 10,
  moon: 11,
  umber0: 12,
  umber1: 13,
  umber2: 14,
  umber3: 15,
  ochre1: 16,
  ochre2: 17,
  ochre3: 18,
  skin1: 19,
  skin2: 20,
  skin3: 21,
  ginger1: 22,
  ginger2: 23,
} as const;

// Material ramps, darkest to lightest. Lighting picks a step on the ramp.
export const RAMPS = {
  oilskin: [C.umber0, C.umber1, C.umber2, C.ochre1, C.ochre2, C.ochre3],
  wood: [C.ink, C.umber0, C.umber1, C.umber2, C.umber3],
  skin: [C.umber0, C.umber1, C.skin1, C.skin2, C.skin3],
  beard: [
    C.night2,
    C.night4,
    C.night6,
    C.silver2,
    C.silver3,
    C.silver4,
    C.moon,
  ],
  tin: [
    C.night1,
    C.night2,
    C.night3,
    C.night5,
    C.silver1,
    C.silver3,
    C.silver4,
  ],
  cat: [C.umber0, C.umber1, C.umber2, C.ginger1, C.ginger2, C.skin3],
  moon: [C.silver2, C.silver3, C.silver4, C.moon],
} as const;

export type Material = keyof typeof RAMPS;

// One step brighter along the color's own family. Glows and light shafts
// climb this ladder, so light never introduces a color outside the palette.
export const BRIGHTER: readonly number[] = [
  1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 11, 13, 14, 15, 16, 17, 18, 18, 20, 21, 21,
  23, 18,
];

export const DARKER: readonly number[] = [
  0, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 0, 12, 13, 14, 15, 16, 17, 14, 19, 20,
  14, 22,
];

const hexToRgb = (hex: string): [number, number, number] => [
  parseInt(hex.slice(1, 3), 16),
  parseInt(hex.slice(3, 5), 16),
  parseInt(hex.slice(5, 7), 16),
];

export const PALETTE_RGB = PALETTE.map(hexToRgb);
