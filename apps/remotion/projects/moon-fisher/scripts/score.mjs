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
// A stem is one instrument alone and dry, for checking notes and levels.
const INSTRUMENTS = Object.keys(
  JSON.parse(await readFile(join(ROOT, "src/audio/samples.json"), "utf8")),
);
const stemArg = process.argv.indexOf("--stem");
const stem = stemArg >= 0 ? process.argv[stemArg + 1] : null;
if (stem && !INSTRUMENTS.includes(stem))
  throw new Error(`Unknown stem ${stem}`);
const OUT = stem
  ? join(ROOT, `renders/score/${stem}.wav`)
  : join(ROOT, "public/score.wav");
const RAW = `${OUT}.raw.wav`;
// A calm film: quieter than the usual −14 LUFS for Reels, with headroom for
// AAC encoding. The ceiling is a sample peak of −2 dBFS, leaving room for the
// peaks between samples.
const TARGET_LUFS = -16;
const CEILING = 0.79;

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
  const { wav, notes } = await page.evaluate(
    (o) => window.renderScoreWav(o),
    stem ? { only: [stem], dry: true } : {},
  );
  await mkdir(dirname(OUT), { recursive: true });
  await writeFile(RAW, Buffer.from(wav, "base64"));
  // Every scheduled note, for scripts/check-tune.py.
  await mkdir(join(ROOT, "renders/score"), { recursive: true });
  await writeFile(
    join(ROOT, "renders/score/notes.json"),
    JSON.stringify(notes),
  );
  console.log(
    `score rendered in ${((Date.now() - started) / 1000).toFixed(1)} s`,
  );
} finally {
  await browser.close();
}

if (stem) {
  await ffmpeg(["-i", RAW, "-ar", "48000", "-c:a", "pcm_s24le", OUT]);
} else {
  // One fixed gain to the target loudness, so every passage keeps its level
  // relative to the others, and a fast limiter that only catches the rare
  // transient above the ceiling. (ffmpeg's loudnorm falls back to dynamic
  // normalization when a fixed gain would clip, which flattens the dynamics.)
  const loudness = async (file) => {
    const log = await ffmpeg([
      "-i",
      file,
      "-af",
      "ebur128=peak=true",
      "-f",
      "null",
      "-",
    ]);
    const summary = log.slice(log.lastIndexOf("Summary:"));
    return {
      i: Number(/I:\s+(-?[\d.]+) LUFS/.exec(summary)[1]),
      peak: Number(/Peak:\s+(-?[\d.]+) dBFS/.exec(summary)[1]),
    };
  };
  const raw = await loudness(RAW);
  const gain = TARGET_LUFS - raw.i;
  await ffmpeg([
    "-i",
    RAW,
    "-af",
    `volume=${gain.toFixed(2)}dB,alimiter=limit=${CEILING}:attack=4:release=60:level=disabled`,
    "-ar",
    "48000",
    "-c:a",
    "pcm_s24le",
    OUT,
  ]);
  const done = await loudness(OUT);
  console.log(
    `raw mix ${raw.i} LUFS, peak ${raw.peak} dBTP; +${gain.toFixed(1)} dB → ${done.i} LUFS, peak ${done.peak} dBTP`,
  );
  if (Math.abs(done.i - TARGET_LUFS) > 0.5) {
    throw new Error(
      `Master missed ${TARGET_LUFS} LUFS: the limiter is doing too much`,
    );
  }
}
await rm(RAW);
console.log(`→ ${OUT}`);
