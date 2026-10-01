// Render a version of the animatic: every shot at final timing with the
// locked score, muxed by ffmpeg (Remotion's AAC priming would put it 43 ms
// late).
//   npm run animatic -- v001
import { execFileSync } from "node:child_process";
import { copyFileSync, existsSync, mkdirSync } from "node:fs";

const SCORE = "renders/score/v005/score.wav";

const version = process.argv[2];
if (!version) throw new Error("Usage: npm run animatic -- v001");
if (!existsSync(SCORE))
  throw new Error(`${SCORE} is missing; render it with npm run score:review`);
const out = `renders/animatic/${version}`;
if (existsSync(out))
  throw new Error(`${out} exists; render a new version instead`);
mkdirSync(out, { recursive: true });

const run = (cmd, args) => execFileSync(cmd, args, { stdio: "inherit" });
copyFileSync(SCORE, `${out}/score.wav`);
run("npx", [
  "remotion",
  "render",
  "Animatic",
  `${out}/silent.mp4`,
  "--muted",
  "--codec=h264",
  "--crf=18",
]);
run("ffmpeg", [
  "-loglevel",
  "error",
  "-i",
  `${out}/silent.mp4`,
  "-i",
  `${out}/score.wav`,
  "-map",
  "0:v",
  "-map",
  "1:a",
  "-c:v",
  "copy",
  "-c:a",
  "aac",
  "-b:a",
  "256k",
  "-shortest",
  `${out}/animatic.mp4`,
]);
console.log(`Wrote ${out}/animatic.mp4`);
