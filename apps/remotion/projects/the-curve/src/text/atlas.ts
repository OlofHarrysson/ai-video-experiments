import { CanvasTexture, LinearFilter, LinearMipmapLinearFilter, SRGBColorSpace } from "three";
import { HEADLINES, TAG_TEXTS } from "../headlines";
import { TICKS } from "../race";
import { anton, mono } from "./fonts";

// Every string the world shows, drawn once into one texture after the fonts load.

export type AtlasEntry = { u0: number; v0: number; u1: number; v1: number; aspect: number };
export type Atlas = { texture: CanvasTexture; entries: Map<string, AtlasEntry> };

type Spec = { key: string; w: number; h: number; draw: (ctx: CanvasRenderingContext2D, x: number, y: number) => void };

const SIZE_W = 4096;
const SIZE_H = 4096;
const GAP = 6;

const roundRect = (ctx: CanvasRenderingContext2D, x: number, y: number, w: number, h: number, r: number) => {
  ctx.beginPath();
  ctx.moveTo(x + r, y);
  ctx.arcTo(x + w, y, x + w, y + h, r);
  ctx.arcTo(x + w, y + h, x, y + h, r);
  ctx.arcTo(x, y + h, x, y, r);
  ctx.arcTo(x, y, x + w, y, r);
  ctx.closePath();
};

const measure = (font: string, text: string, tracking = 0) => {
  const c = document.createElement("canvas").getContext("2d") as CanvasRenderingContext2D;
  c.font = font;
  return c.measureText(text).width + tracking * Math.max(0, text.length - 1);
};

const tagSpec = (text: string): Spec => {
  const font = `700 44px "${mono.fontFamily}"`;
  const tw = measure(font, text, 3);
  const w = Math.ceil(tw + 52);
  const h = 72;
  return {
    key: `tag:${text}`,
    w,
    h,
    draw: (ctx, x, y) => {
      ctx.strokeStyle = "#fff";
      ctx.lineWidth = 4;
      roundRect(ctx, x + 4, y + 4, w - 8, h - 8, (h - 8) / 2);
      ctx.stroke();
      ctx.fillStyle = "#fff";
      ctx.font = font;
      ctx.textBaseline = "middle";
      (ctx as unknown as { letterSpacing: string }).letterSpacing = "3px";
      ctx.fillText(text, x + 26, y + h / 2 + 2);
      (ctx as unknown as { letterSpacing: string }).letterSpacing = "0px";
    },
  };
};

const tickSpec = (text: string): Spec => {
  const font = `500 40px "${mono.fontFamily}"`;
  const tw = measure(font, text, 2);
  const w = Math.ceil(tw + 16);
  const h = 56;
  return {
    key: `tick:${text}`,
    w,
    h,
    draw: (ctx, x, y) => {
      ctx.fillStyle = "#fff";
      ctx.font = font;
      ctx.textBaseline = "middle";
      (ctx as unknown as { letterSpacing: string }).letterSpacing = "2px";
      ctx.fillText(text, x + 8, y + h / 2 + 2);
      (ctx as unknown as { letterSpacing: string }).letterSpacing = "0px";
    },
  };
};

const headlineSpec = (text: string, bg: string, fg: string): Spec => {
  const font = `400 132px "${anton.fontFamily}"`;
  const tw = measure(font, text, 2);
  const padX = 44;
  const w = Math.ceil(tw + padX * 2);
  const h = 196;
  return {
    key: `headline:${text}`,
    w,
    h,
    draw: (ctx, x, y) => {
      ctx.fillStyle = bg;
      ctx.fillRect(x, y, w, h);
      ctx.fillStyle = fg;
      ctx.font = font;
      ctx.textBaseline = "middle";
      (ctx as unknown as { letterSpacing: string }).letterSpacing = "2px";
      ctx.fillText(text, x + padX, y + h / 2 + 6);
      (ctx as unknown as { letterSpacing: string }).letterSpacing = "0px";
    },
  };
};

export const buildAtlas = (): Atlas => {
  const specs: Spec[] = [
    ...TAG_TEXTS.map(tagSpec),
    ...TICKS.map((t) => tickSpec(t.label)),
    ...HEADLINES.map((h) => headlineSpec(h.text, h.bg, h.fg)),
  ];
  const unique = new Map<string, Spec>();
  for (const s of specs) unique.set(s.key, s);

  const canvas = document.createElement("canvas");
  canvas.width = SIZE_W;
  canvas.height = SIZE_H;
  const ctx = canvas.getContext("2d") as CanvasRenderingContext2D;
  ctx.clearRect(0, 0, SIZE_W, SIZE_H);

  // Shelf packing, tallest first.
  const sorted = [...unique.values()].sort((a, b) => b.h - a.h);
  const entries = new Map<string, AtlasEntry>();
  let x = GAP;
  let y = GAP;
  let shelf = 0;
  for (const s of sorted) {
    if (x + s.w + GAP > SIZE_W) {
      x = GAP;
      y += shelf + GAP;
      shelf = 0;
    }
    if (y + s.h + GAP > SIZE_H) throw new Error("Text atlas is full");
    s.draw(ctx, x, y);
    entries.set(s.key, {
      u0: x / SIZE_W,
      u1: (x + s.w) / SIZE_W,
      v0: 1 - (y + s.h) / SIZE_H,
      v1: 1 - y / SIZE_H,
      aspect: s.w / s.h,
    });
    x += s.w + GAP;
    shelf = Math.max(shelf, s.h);
  }

  const texture = new CanvasTexture(canvas);
  texture.colorSpace = SRGBColorSpace;
  texture.generateMipmaps = true;
  texture.minFilter = LinearMipmapLinearFilter;
  texture.magFilter = LinearFilter;
  texture.anisotropy = 8;
  texture.needsUpdate = true;
  return { texture, entries };
};
