// Scenes are authored on a 270×480 design frame. A density draws that frame
// on a coarser or finer pixel grid, scaled by a whole number to 1080×1920.
export type Density = { name: string; w: number; h: number; scale: number };

export const DENSITIES = {
  A: { name: "A", w: 180, h: 320, scale: 6 },
  B: { name: "B", w: 270, h: 480, scale: 4 },
} as const satisfies Record<string, Density>;

export type DensityName = keyof typeof DENSITIES;

export const DESIGN_WIDTH = 270;
