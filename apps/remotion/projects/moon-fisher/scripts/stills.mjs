// Render the style-frame stills and the ambient loop through Remotion into a
// versioned folder, then lay the stills side by side with the palette below.
import { execFileSync } from "node:child_process";
import { existsSync, mkdirSync } from "node:fs";

const version = process.argv[2];
if (!version) throw new Error("Usage: npm run stills -- v001");
const out = `renders/style-frame/${version}`;
if (existsSync(out))
  throw new Error(`${out} exists; render a new version instead`);
mkdirSync(out, { recursive: true });

for (const d of ["A", "B"]) {
  execFileSync(
    "npx",
    ["remotion", "still", `StyleFrame${d}`, `${out}/key-${d}.png`],
    {
      stdio: "inherit",
    },
  );
}
execFileSync(
  "npx",
  [
    "remotion",
    "render",
    "StyleLoopB",
    `${out}/loop-B.mp4`,
    "--codec=h264",
    "--crf=12",
  ],
  { stdio: "inherit" },
);
execFileSync("npx", ["tsx", "scripts/palette.ts", `${out}/palette.png`], {
  stdio: "inherit",
});
execFileSync(
  "ffmpeg",
  [
    "-loglevel",
    "error",
    "-i",
    `${out}/key-A.png`,
    "-i",
    `${out}/key-B.png`,
    "-i",
    `${out}/palette.png`,
    "-filter_complex",
    "[0][1]hstack=inputs=2[pair];[pair]pad=iw+0:ih+24:0:0:color=0x07080f[p];[p][2]vstack=inputs=2",
    `${out}/comparison.png`,
  ],
  { stdio: "inherit" },
);
console.log(`Wrote ${out}`);
