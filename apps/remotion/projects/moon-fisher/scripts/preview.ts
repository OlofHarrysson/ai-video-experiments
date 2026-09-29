// Fast local previews of any scene without starting Remotion: the same
// drawing code, written straight to PNG.
//   npx tsx scripts/preview.ts [out] [frame] [scene...]
import { mkdirSync, writeFileSync } from "node:fs";
import { DESIGN_WIDTH, FILM } from "../src/pixel/density";
import { Pix } from "../src/pixel/pix";
import { drawBoatScene } from "../src/stills/boatScene";
import { SCENES, specAt, type SceneName } from "../src/stills/scenes";
import { encodePng } from "./png";

const [out = "renders/preview", frameArg = "0", ...names] =
  process.argv.slice(2);
const frame = Number(frameArg);
mkdirSync(out, { recursive: true });

for (const name of (names.length
  ? names
  : Object.keys(SCENES)) as SceneName[]) {
  const pix = new Pix(FILM.w, FILM.h, FILM.w / DESIGN_WIDTH);
  const t0 = performance.now();
  drawBoatScene(pix, specAt(name, frame), frame);
  const ms = performance.now() - t0;
  const rgba = pix.toRGBA();
  writeFileSync(
    `${out}/${name}.png`,
    encodePng(FILM.w, FILM.h, rgba, FILM.scale),
  );
  writeFileSync(`${out}/${name}-1x.png`, encodePng(FILM.w, FILM.h, rgba, 1));
  console.log(`${name}: frame ${frame}, ${ms.toFixed(0)} ms`);
}
