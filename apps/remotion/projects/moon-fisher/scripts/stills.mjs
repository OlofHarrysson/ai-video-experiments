// Render the style-frame still and the ambient loop through Remotion into a
// versioned folder. With an earlier still, also lay out a before/after sheet
// with the palette underneath.
//   npm run stills -- v003 [renders/style-frame/v002/key-A.png]
import { execFileSync } from "node:child_process";
import { existsSync, mkdirSync } from "node:fs";

const [version, before] = process.argv.slice(2);
if (!version) throw new Error("Usage: npm run stills -- v003 [before.png]");
const out = `renders/style-frame/${version}`;
if (existsSync(out))
  throw new Error(`${out} exists; render a new version instead`);
mkdirSync(out, { recursive: true });

const run = (cmd, args) => execFileSync(cmd, args, { stdio: "inherit" });

run("npx", ["remotion", "still", "StyleFrame", `${out}/key.png`]);
run("npx", [
  "remotion",
  "render",
  "StyleLoop",
  `${out}/loop.mp4`,
  "--codec=h264",
  "--crf=12",
]);
if (before) {
  run("npx", ["tsx", "scripts/palette.ts", `${out}/palette.png`, "2160"]);
  run("ffmpeg", [
    "-loglevel",
    "error",
    "-i",
    before,
    "-i",
    `${out}/key.png`,
    "-i",
    `${out}/palette.png`,
    "-filter_complex",
    "[0][1]hstack=inputs=2[pair];[pair]pad=iw:ih+24:0:0:color=0x07080f[p];[p][2]vstack=inputs=2",
    `${out}/before-after.png`,
  ]);
}
console.log(`Wrote ${out}`);
