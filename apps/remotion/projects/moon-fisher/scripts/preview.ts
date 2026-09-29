// Fast local previews of the style frame without starting Remotion:
// the same drawing code, written straight to PNG.
import { mkdirSync, writeFileSync } from "node:fs";
import { DENSITIES, DESIGN_WIDTH } from "../src/pixel/density";
import { Pix } from "../src/pixel/pix";
import { drawKeyImage } from "../src/stills/keyImage";
import { encodePng } from "./png";

const out = process.argv[2] ?? "renders/preview";
mkdirSync(out, { recursive: true });

for (const d of Object.values(DENSITIES)) {
  const pix = new Pix(d.w, d.h, d.w / DESIGN_WIDTH);
  const t0 = performance.now();
  drawKeyImage(pix);
  const ms = performance.now() - t0;
  const rgba = pix.toRGBA();
  writeFileSync(`${out}/key-${d.name}.png`, encodePng(d.w, d.h, rgba, d.scale));
  writeFileSync(`${out}/key-${d.name}-1x.png`, encodePng(d.w, d.h, rgba, 1));
  console.log(
    `${d.name}: ${d.w}×${d.h} ×${d.scale}, drawn in ${ms.toFixed(0)} ms`,
  );
}
