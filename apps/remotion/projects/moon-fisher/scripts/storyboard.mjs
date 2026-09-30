// Render the storyboard contact sheet through Remotion into a versioned folder.
//   npm run storyboard -- v001
import { execFileSync } from "node:child_process";
import { existsSync, mkdirSync } from "node:fs";

const version = process.argv[2];
if (!version) throw new Error("Usage: npm run storyboard -- v001");
const out = `renders/storyboard/${version}`;
if (existsSync(out))
  throw new Error(`${out} exists; render a new version instead`);
mkdirSync(out, { recursive: true });
execFileSync(
  "npx",
  ["remotion", "still", "Storyboard", `${out}/storyboard.png`],
  { stdio: "inherit" },
);
console.log(`Wrote ${out}`);
