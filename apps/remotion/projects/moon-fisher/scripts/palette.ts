// The film's palette as a strip of swatches, for comparison sheets.
import { writeFileSync } from "node:fs";
import { PALETTE_RGB } from "../src/pixel/palette";
import { encodePng } from "./png";

const out = process.argv[2] ?? "renders/palette.png";
const W = 2160;
const H = 90;
const rgba = new Uint8ClampedArray(W * H * 4);
const sw = W / PALETTE_RGB.length;
for (let y = 0; y < H; y++) {
  for (let x = 0; x < W; x++) {
    const [r, g, b] =
      PALETTE_RGB[Math.min(PALETTE_RGB.length - 1, Math.floor(x / sw))];
    const i = (y * W + x) * 4;
    rgba.set([r, g, b, 255], i);
  }
}
writeFileSync(out, encodePng(W, H, rgba));
