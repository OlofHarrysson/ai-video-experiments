// Scenes are authored on a 270×480 design frame and drawn on a coarser
// 180×320 grid, enlarged six times to 1080×1920. Olof chose this density over
// 270×480 on 2026-09-29: it hides the geometric shapes underneath.
export type Density = { w: number; h: number; scale: number };

export const FILM: Density = { w: 180, h: 320, scale: 6 };

export const DESIGN_WIDTH = 270;
