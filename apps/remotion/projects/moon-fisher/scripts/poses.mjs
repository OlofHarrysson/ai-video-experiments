// Render the fisherman's key poses and the haul motion test through Remotion
// into a versioned folder, with a side-by-side sheet of the poses.
//   npm run poses -- v001
import { execFileSync } from "node:child_process";
import { existsSync, mkdirSync } from "node:fs";

const version = process.argv[2];
if (!version) throw new Error("Usage: npm run poses -- v001");
const out = `renders/poses/${version}`;
if (existsSync(out))
  throw new Error(`${out} exists; render a new version instead`);
mkdirSync(out, { recursive: true });

const run = (cmd, args) => execFileSync(cmd, args, { stdio: "inherit" });
const poses = ["Doze", "Haul", "Tip"];
for (const p of poses)
  run("npx", [
    "remotion",
    "still",
    `Pose${p}`,
    `${out}/${p.toLowerCase()}.png`,
  ]);
run("npx", [
  "remotion",
  "render",
  "HaulTest",
  `${out}/haul-test.mp4`,
  "--codec=h264",
  "--crf=12",
]);
run("ffmpeg", [
  "-loglevel",
  "error",
  ...poses.flatMap((p) => ["-i", `${out}/${p.toLowerCase()}.png`]),
  "-filter_complex",
  "[0][1][2]hstack=inputs=3,scale=iw/2:ih/2:flags=neighbor",
  `${out}/sheet.png`,
]);
console.log(`Wrote ${out}`);
