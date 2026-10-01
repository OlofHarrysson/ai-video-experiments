// Regenerate the README's tables from the code: the storyboard's shots and
// the asset register, with where each asset is on screen. Every shot is
// drawn several times a second, and each pixel counts for the asset that
// drew it last.
//   npm run tables
import { readFileSync, writeFileSync } from "node:fs";
import { ASSETS, SOUND_CUES, type AssetName } from "../src/assets";
import { DESIGN_WIDTH, FILM } from "../src/pixel/density";
import { Pix } from "../src/pixel/pix";
import { drawBoatScene } from "../src/stills/boatScene";
import { SHOTS, shotSeconds, shotStart } from "../src/storyboard/shots";
import { FPS } from "../src/timing";

const README = "README.md";
// Moments drawn per second of film.
const RATE = 4;
// Fewer pixels than this is a stray, not the asset on screen.
const VISIBLE = 6;

const clock = (s: number) => {
  const seconds = (s % 60).toFixed(1).padStart(4, "0").replace(/\.0$/, "");
  return `${Math.floor(s / 60)}:${seconds}`;
};
const percent = (v: number) =>
  v < 0.001
    ? "<0.1%"
    : `${v < 0.01 ? (100 * v).toFixed(1) : Math.round(100 * v)}%`;
// Table cells keep a literal pipe only when it is escaped.
const cell = (text: string) => text.replaceAll("|", "\\|");

// "01–08, 13, 15–19" from shot ids in film order.
const ranges = (ids: string[]) => {
  const order = SHOTS.map((s) => s.id).filter((id) => ids.includes(id));
  const index = (id: string) => SHOTS.findIndex((s) => s.id === id);
  const runs: string[][] = [];
  for (const id of order) {
    const run = runs.at(-1);
    if (run && index(id) === index(run.at(-1)!) + 1) run.push(id);
    else runs.push([id]);
  }
  return runs
    .map((r) => (r.length === 1 ? r[0] : `${r[0]}–${r.at(-1)}`))
    .join(", ");
};

type Usage = {
  shots: string[];
  seconds: number;
  share: number;
  largest: number;
  largestIn: string;
};
const usage = Object.fromEntries(
  (Object.keys(ASSETS) as AssetName[]).map((name) => [
    name,
    { shots: [], seconds: 0, share: 0, largest: 0, largestIn: "" } as Usage,
  ]),
) as Record<AssetName, Usage>;

const frame = FILM.w * FILM.h;
const filmSeconds = SHOTS.reduce((sum, s) => sum + shotSeconds(s), 0);
for (const shot of SHOTS) {
  const samples = Math.round(shotSeconds(shot) * RATE);
  for (let i = 0; i < samples; i++) {
    const t = (i + 0.5) / RATE;
    const pix = new Pix(FILM.w, FILM.h, FILM.w / DESIGN_WIDTH);
    drawBoatScene(pix, shot.spec(t, shotStart(shot) + t), Math.round(t * FPS));
    for (const [name, pixels] of pix.assetPixels()) {
      if (!(name in ASSETS)) throw new Error(`${name} is not in the register`);
      if (pixels < VISIBLE) continue;
      const u = usage[name as AssetName];
      const fraction = pixels / frame;
      if (!u.shots.includes(shot.id)) u.shots.push(shot.id);
      u.seconds += 1 / RATE;
      u.share += fraction / RATE / filmSeconds;
      if (fraction > u.largest) {
        u.largest = fraction;
        u.largestIn = shot.id;
      }
    }
  }
}

const storyboard = [
  "| Shot | Bars | Time | Framing | What happens | Sound |",
  "| --- | --- | --- | --- | --- | --- |",
  ...SHOTS.map((s) => {
    const [a, b] = s.bars;
    const bars = b - a === 1 ? `${a}` : `${a}–${b - 1}`;
    return `| ${s.id} | ${bars} | ${clock(shotStart(s))} | ${s.framing} | **${s.title}.** ${s.action} | ${s.sound} |`;
  }),
].join("\n");

const register = [
  "| Asset | Status | On screen | Share of the picture | Largest | Still needs |",
  "| --- | --- | --- | --- | --- | --- |",
  ...(Object.entries(ASSETS) as [AssetName, (typeof ASSETS)[AssetName]][]).map(
    ([name, a]) => {
      const u = usage[name];
      const seen = u.shots.length
        ? `${Math.round(u.seconds)} s in ${ranges(u.shots)}`
        : "not yet on screen";
      const largest = u.shots.length
        ? `${percent(u.largest)} in ${u.largestIn}`
        : "";
      return `| **${a.name}** (${a.kind.toLowerCase()})<br>\`${cell(a.api)}\` | ${a.status} | ${seen} | ${percent(u.share)} | ${largest} | ${cell(a.next)} |`;
    },
  ),
].join("\n");

const sounds = [
  "| Sound | Shots | Status |",
  "| --- | --- | --- |",
  `| The sea | ${ranges(SHOTS.map((s) => s.id))} | rough, in the score |`,
  ...SOUND_CUES.map((c) => `| ${c.cue} | ${ranges(c.shots)} | not started |`),
].join("\n");

const fill = (text: string, block: string, body: string) => {
  const start = `<!-- generated:${block} -->`;
  const end = `<!-- /generated:${block} -->`;
  const a = text.indexOf(start);
  const b = text.indexOf(end);
  if (a < 0 || b < a)
    throw new Error(`${README} has no ${start} … ${end} block`);
  return `${text.slice(0, a + start.length)}\n${body}\n${text.slice(b)}`;
};

let readme = readFileSync(README, "utf8");
readme = fill(readme, "storyboard", storyboard);
readme = fill(readme, "assets", register);
readme = fill(readme, "sounds", sounds);
writeFileSync(README, readme);
console.log(
  `${SHOTS.length} shots and ${Object.keys(ASSETS).length} assets → ${README}`,
);
