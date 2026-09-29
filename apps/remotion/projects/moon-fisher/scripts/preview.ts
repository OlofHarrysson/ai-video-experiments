// Fast local previews of the style frame without starting Remotion:
// the same drawing code, written straight to PNG.
import { mkdirSync, writeFileSync } from "node:fs";
import { DESIGN_WIDTH, FILM } from "../src/pixel/density";
import { Pix } from "../src/pixel/pix";
import { drawKeyImage } from "../src/stills/keyImage";
import { encodePng } from "./png";

const out = process.argv[2] ?? "renders/preview";
const frame = Number(process.argv[3] ?? 0);
mkdirSync(out, { recursive: true });

const pix = new Pix(FILM.w, FILM.h, FILM.w / DESIGN_WIDTH);
const t0 = performance.now();
drawKeyImage(pix, frame);
const ms = performance.now() - t0;
const rgba = pix.toRGBA();
writeFileSync(`${out}/key.png`, encodePng(FILM.w, FILM.h, rgba, FILM.scale));
writeFileSync(`${out}/key-1x.png`, encodePng(FILM.w, FILM.h, rgba, 1));
console.log(
  `${FILM.w}×${FILM.h} ×${FILM.scale}, frame ${frame}, ${ms.toFixed(0)} ms`,
);
