import { BRIGHTER, DARKER, PALETTE_RGB } from "./palette";

export const EMPTY = 255;

// Where a shot looks: the world point (x, y) appears at screen point (sx, sy)
// of the 270×480 design frame, enlarged by `zoom`.
export type Camera = {
  x: number;
  y: number;
  zoom: number;
  sx: number;
  sy: number;
};

export const IDENTITY: Camera = { x: 0, y: 0, zoom: 1, sx: 0, sy: 0 };

// A low-resolution image of palette indices. The design frame is 270×480;
// `k` converts design units to this image's pixels, so the same scene can be
// drawn at any pixel density. World objects go through the camera; skies and
// stars are placed directly in the design frame.
export class Pix {
  readonly data: Uint8Array;
  // 1 where an object (not sky, sea or air glow) was drawn.
  readonly solid: Uint8Array;
  cam: Camera = IDENTITY;
  // While true, everything drawn counts as a solid object.
  drawingObjects = false;

  constructor(
    readonly w: number,
    readonly h: number,
    readonly k: number,
  ) {
    this.data = new Uint8Array(w * h).fill(EMPTY);
    this.solid = new Uint8Array(w * h);
  }

  // Pixels per world unit.
  get s(): number {
    return this.k * this.cam.zoom;
  }

  // Pixel column or row containing a world coordinate.
  px(x: number): number {
    return Math.floor(
      ((x - this.cam.x) * this.cam.zoom + this.cam.sx) * this.k,
    );
  }

  py(y: number): number {
    return Math.floor(
      ((y - this.cam.y) * this.cam.zoom + this.cam.sy) * this.k,
    );
  }

  // World coordinate at the center of a pixel column or row.
  wx(px: number): number {
    return ((px + 0.5) / this.k - this.cam.sx) / this.cam.zoom + this.cam.x;
  }

  wy(py: number): number {
    return ((py + 0.5) / this.k - this.cam.sy) / this.cam.zoom + this.cam.y;
  }

  // Where a world height lands in the design frame.
  screenY(y: number): number {
    return (y - this.cam.y) * this.cam.zoom + this.cam.sy;
  }

  inside(x: number, y: number): boolean {
    return x >= 0 && y >= 0 && x < this.w && y < this.h;
  }

  get(x: number, y: number): number {
    return this.inside(x, y) ? this.data[y * this.w + x] : EMPTY;
  }

  set(x: number, y: number, c: number): void {
    if (!this.inside(x, y)) return;
    this.data[y * this.w + x] = c;
    if (this.drawingObjects) this.solid[y * this.w + x] = 1;
  }

  isSolid(x: number, y: number): boolean {
    return this.inside(x, y) && this.solid[y * this.w + x] === 1;
  }

  brighten(x: number, y: number, steps: number): void {
    let c = this.get(x, y);
    if (c === EMPTY) return;
    for (let i = 0; i < steps; i++) c = BRIGHTER[c];
    this.set(x, y, c);
  }

  darken(x: number, y: number, steps: number): void {
    let c = this.get(x, y);
    if (c === EMPTY) return;
    for (let i = 0; i < steps; i++) c = DARKER[c];
    this.set(x, y, c);
  }

  // A one-pixel line between two world points (Bresenham).
  line(x0: number, y0: number, x1: number, y1: number, c: number): void {
    this.trace(x0, y0, x1, y1, (x, y) => this.set(x, y, c));
  }

  // Visit every pixel on the line between two world points.
  trace(
    x0: number,
    y0: number,
    x1: number,
    y1: number,
    visit: (x: number, y: number) => void,
  ): void {
    let ax = this.px(x0);
    let ay = this.py(y0);
    const bx = this.px(x1);
    const by = this.py(y1);
    const dx = Math.abs(bx - ax);
    const dy = -Math.abs(by - ay);
    const sx = ax < bx ? 1 : -1;
    const sy = ay < by ? 1 : -1;
    let err = dx + dy;
    for (;;) {
      visit(ax, ay);
      if (ax === bx && ay === by) break;
      const e2 = 2 * err;
      if (e2 >= dy) {
        err += dy;
        ax += sx;
      }
      if (e2 <= dx) {
        err += dx;
        ay += sy;
      }
    }
  }

  toRGBA(): Uint8ClampedArray {
    const out = new Uint8ClampedArray(this.w * this.h * 4);
    for (let i = 0; i < this.data.length; i++) {
      const c = this.data[i];
      if (c === EMPTY) continue;
      const [r, g, b] = PALETTE_RGB[c];
      out[i * 4] = r;
      out[i * 4 + 1] = g;
      out[i * 4 + 2] = b;
      out[i * 4 + 3] = 255;
    }
    return out;
  }
}

const BAYER4 = [0, 8, 2, 10, 12, 4, 14, 6, 3, 11, 1, 9, 15, 7, 13, 5];

// Ordered-dither threshold in (0, 1), fixed to the pixel grid.
export const bayer = (x: number, y: number): number =>
  (BAYER4[(y & 3) * 4 + (x & 3)] + 0.5) / 16;

// Round a continuous level to a whole step. `dither` 0 gives clean bands;
// 1 mixes neighboring steps in an ordered pattern across the whole interval.
export const quantize = (
  v: number,
  x: number,
  y: number,
  dither: number,
): number => Math.floor(v + 0.5 + (bayer(x, y) - 0.5) * dither);

export const clamp = (v: number, lo: number, hi: number): number =>
  v < lo ? lo : v > hi ? hi : v;

export const smoothstep = (a: number, b: number, v: number): number => {
  const t = clamp((v - a) / (b - a), 0, 1);
  return t * t * (3 - 2 * t);
};
