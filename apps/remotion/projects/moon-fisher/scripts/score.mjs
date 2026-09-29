// Render the Tone.js score in headless Chrome with the recorded samples, then
// master it: bundle src/audio/entry.ts → OfflineAudioContext → WAV → two-pass
// loudness normalization.
//   npm run score                 → public/score.wav, used by the film
//   npm run score -- --stem clarinet → renders/score/clarinet.wav, dry, for checks
import { spawn } from "node:child_process";
import { mkdir, readFile, rm, writeFile } from "node:fs/promises";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import { build } from "esbuild";
import { chromium } from "playwright-core";

const ROOT = join(dirname(fileURLToPath(import.meta.url)), "..");
// Dry single-instrument stems for checking the notes by pitch tracking.
const STEMS = {
  clarinet: { only: ["clarinet"], dry: true },
  glock: { only: ["glock"], dry: true },
};
const stemArg = process.argv.indexOf("--stem");
const stem = stemArg >= 0 ? process.argv[stemArg + 1] : null;
if (stem && !STEMS[stem]) throw new Error(`Unknown stem ${stem}`);
const OUT = stem
  ? join(ROOT, `renders/score/${stem}.wav`)
  : join(ROOT, "public/score.wav");
const RAW = `${OUT}.raw.wav`;
// A calm film: quieter than the usual −14 LUFS for Reels, with headroom for
// AAC encoding.
const LOUDNESS = "I=-16:TP=-1.5:LRA=14";

function ffmpeg(args) {
  return new Promise((resolve, reject) => {
    const proc = spawn("ffmpeg", ["-hide_banner", "-y", ...args], {
      stdio: ["ignore", "ignore", "pipe"],
    });
    let stderr = "";
    proc.stderr.on("data", (d) => (stderr += d));
    proc.on("close", (code) =>
      code === 0
        ? resolve(stderr)
        : reject(new Error(`ffmpeg exited ${code}\n${stderr.slice(-1500)}`)),
    );
  });
}

const bundle = await build({
  entryPoints: [join(ROOT, "src/audio/entry.ts")],
  bundle: true,
  format: "iife",
  platform: "browser",
  target: "chrome120",
  write: false,
  logLevel: "warning",
});

const browser = await chromium.launch({ channel: "chrome", headless: true });
try {
  const page = await browser.newPage();
  page.on("pageerror", (e) => console.error(`[page error] ${e.message}`));
  // One made-up origin serves the page and the samples, so nothing is
  // cross-origin.
  await page.route("https://score.local/**", async (route) => {
    const path = decodeURIComponent(new URL(route.request().url()).pathname);
    if (path === "/") {
      return route.fulfill({
        contentType: "text/html",
        body: "<!doctype html><title>score</title>",
      });
    }
    const file = join(ROOT, path.replace(/^\//, ""));
    try {
      return route.fulfill({
        contentType: "audio/wav",
        body: await readFile(file),
      });
    } catch {
      console.error(`missing sample ${path}`);
      return route.fulfill({ status: 404, body: "" });
    }
  });
  await page.goto("https://score.local/");
  await page.addScriptTag({ content: bundle.outputFiles[0].text });
  const started = Date.now();
  const base64 = await page.evaluate(
    (o) => window.renderScoreWav(o),
    stem ? STEMS[stem] : {},
  );
  await mkdir(dirname(OUT), { recursive: true });
  await writeFile(RAW, Buffer.from(base64, "base64"));
  console.log(
    `score rendered in ${((Date.now() - started) / 1000).toFixed(1)} s`,
  );
} finally {
  await browser.close();
}

if (stem) {
  await ffmpeg(["-i", RAW, "-ar", "48000", "-c:a", "pcm_s24le", OUT]);
} else {
  const analysis = await ffmpeg([
    "-i",
    RAW,
    "-af",
    `loudnorm=${LOUDNESS}:print_format=json`,
    "-f",
    "null",
    "-",
  ]);
  const m = JSON.parse(
    analysis.slice(analysis.lastIndexOf("{"), analysis.lastIndexOf("}") + 1),
  );
  console.log(
    `raw mix: ${m.input_i} LUFS, true peak ${m.input_tp} dBTP, LRA ${m.input_lra}`,
  );
  const measured = `measured_I=${m.input_i}:measured_TP=${m.input_tp}:measured_LRA=${m.input_lra}:measured_thresh=${m.input_thresh}:offset=${m.target_offset}`;
  await ffmpeg([
    "-i",
    RAW,
    "-af",
    `loudnorm=${LOUDNESS}:${measured}:linear=true`,
    "-ar",
    "48000",
    "-c:a",
    "pcm_s24le",
    OUT,
  ]);
}
await rm(RAW);
console.log(`→ ${OUT}`);
