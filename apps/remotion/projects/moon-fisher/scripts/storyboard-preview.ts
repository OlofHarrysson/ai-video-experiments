// Fast previews of the storyboard panels without Remotion, tiled into one
// sheet by ffmpeg.
//   npx tsx scripts/storyboard-preview.ts [out]
import { execFileSync } from "node:child_process";
import { mkdirSync, writeFileSync } from "node:fs";
import { DESIGN_WIDTH, FILM } from "../src/pixel/density";
import { Pix } from "../src/pixel/pix";
import { drawBoatScene } from "../src/stills/boatScene";
import { SHEET_COLUMNS, SHOTS } from "../src/storyboard/shots";
import { encodePng } from "./png";

const out = process.argv[2] ?? "renders/preview/storyboard";
mkdirSync(out, { recursive: true });
for (const shot of SHOTS) {
  const pix = new Pix(FILM.w, FILM.h, FILM.w / DESIGN_WIDTH);
  drawBoatScene(pix, shot.spec(shot.panel), Math.round(shot.panel * 24));
  writeFileSync(
    `${out}/${shot.id}.png`,
    encodePng(FILM.w, FILM.h, pix.toRGBA(), 2),
  );
}
const inputs = SHOTS.flatMap((s) => ["-i", `${out}/${s.id}.png`]);
const layout = SHOTS.map(
  (_, i) =>
    `${(i % SHEET_COLUMNS) * 372}_${Math.floor(i / SHEET_COLUMNS) * 652}`,
).join("|");
execFileSync("ffmpeg", [
  "-loglevel",
  "error",
  "-y",
  ...inputs,
  "-filter_complex",
  `${SHOTS.map((_, i) => `[${i}]`).join("")}xstack=inputs=${SHOTS.length}:layout=${layout}:fill=0x0d1222`,
  `${out}/sheet.png`,
]);
console.log(`${SHOTS.length} panels → ${out}/sheet.png`);
