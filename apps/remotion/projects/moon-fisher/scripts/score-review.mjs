// Keep a version of the score and a review video: the story passages with the
// current one lit, the score muxed by ffmpeg (Remotion's AAC priming would put
// it 43 ms late).
//   npm run score:review -- v001
import { execFileSync } from "node:child_process";
import { copyFileSync, existsSync, mkdirSync } from "node:fs";

const version = process.argv[2];
if (!version) throw new Error("Usage: npm run score:review -- v001");
const out = `renders/score/${version}`;
if (existsSync(out))
  throw new Error(`${out} exists; render a new version instead`);
mkdirSync(out, { recursive: true });

const run = (cmd, args) => execFileSync(cmd, args, { stdio: "inherit" });
copyFileSync("public/score.wav", `${out}/score.wav`);
run("ffmpeg", [
  "-loglevel",
  "error",
  "-i",
  `${out}/score.wav`,
  "-c:a",
  "libmp3lame",
  "-b:a",
  "256k",
  `${out}/score.mp3`,
]);
run("npx", [
  "remotion",
  "render",
  "ScoreMap",
  `${out}/map-silent.mp4`,
  "--muted",
  "--codec=h264",
  "--crf=20",
]);
run("ffmpeg", [
  "-loglevel",
  "error",
  "-i",
  `${out}/map-silent.mp4`,
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
  `${out}/score-map.mp4`,
]);
console.log(`Wrote ${out}`);
