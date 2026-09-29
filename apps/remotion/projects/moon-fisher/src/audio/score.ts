import * as Tone from "tone";
import { at, BARS, DURATION_SECONDS, EIGHTH_SECONDS } from "../timing";
import { createBand, type Band, type InstrumentName } from "./instruments";

// The Moon Fisher's score: a lullaby in 6/8 built on one tune.
//
// The tune reaches up a sixth, like a hand toward the moon, and settles back
// by step. The clarinet sings it for the fisherman, the glockenspiel plays it
// like a music box once the moon is in his bucket, it turns minor as the moon
// dims, and it comes home a step higher when the moon rises again.

const SAMPLE_RATE = 48000;
// The glue compressor and the limiter each look 6 ms ahead; the render runs
// that much long and is trimmed.
const MASTER_LATENCY = 0.012;

// [eighth within the bar, note, length in eighths, velocity]
type Note = [eighth: number, note: string, eighths: number, velocity?: number];

// The tune, in D, one bar per line.
const TUNE: Note[][] = [
  [
    [0, "A4", 3],
    [3, "F#5", 2],
    [5, "E5", 1],
  ],
  [
    [0, "D5", 2],
    [2, "E5", 1],
    [3, "F#5", 3],
  ],
  [
    [0, "B4", 3],
    [3, "G5", 2],
    [5, "F#5", 1],
  ],
  [
    [0, "E5", 2],
    [2, "F#5", 1],
    [3, "E5", 3],
  ],
  [
    [0, "A4", 3],
    [3, "F#5", 2],
    [5, "E5", 1],
  ],
  [
    [0, "D5", 2],
    [2, "E5", 1],
    [3, "F#5", 2],
    [5, "A5", 1],
  ],
  [
    [0, "G5", 2],
    [2, "F#5", 1],
    [3, "E5", 2],
    [5, "C#5", 1],
  ],
  [[0, "D5", 6]],
];
const TUNE_CHORDS = ["D", "Bm", "G", "A", "D", "Bm", "G A", "D"];

// Chord roots for the harp and cellos, and whether the third is minor.
const CHORDS: Record<string, { root: string; minor?: boolean }> = {
  D: { root: "D3" },
  Bm: { root: "B2", minor: true },
  G: { root: "G2" },
  A: { root: "A2" },
  Dm: { root: "D3", minor: true },
  Bb: { root: "Bb2" },
  Gm: { root: "G2", minor: true },
  C: { root: "C3" },
  E: { root: "E3" },
  "C#m": { root: "C#3", minor: true },
  B: { root: "B2" },
};

const shift = (note: string, semitones: number): string =>
  Tone.Frequency(note).transpose(semitones).toNote();

const eighths = (n: number) => n * EIGHTH_SECONDS;

type Score = {
  band: Band;
  play: (
    name: InstrumentName,
    bar: number,
    notes: Note[],
    opts?: PlayOpts,
  ) => void;
};
type PlayOpts = { transpose?: number; velocity?: number; legato?: number };

const scorer = (band: Band): Score => ({
  band,
  play: (
    name,
    bar,
    notes,
    { transpose = 0, velocity = 0.6, legato = 1 } = {},
  ) => {
    const sampler = band.samplers[name];
    for (const [e, note, len, v] of notes) {
      sampler.triggerAttackRelease(
        shift(note, transpose),
        eighths(len) * legato,
        at(bar, e),
        v ?? velocity,
      );
    }
  },
});

// The tune's bars `from`..`to` (0-based, exclusive), starting at `bar`.
const tune = (
  s: Score,
  name: InstrumentName,
  bar: number,
  from: number,
  to: number,
  opts?: PlayOpts,
) => {
  for (let i = from; i < to; i++) s.play(name, bar + i - from, TUNE[i], opts);
};

// The harp's rocking figure: root, fifth, octave, tenth, octave, fifth.
const rock = (
  s: Score,
  bar: number,
  chord: string,
  velocity: number,
  transpose = 0,
  eighthsFrom = 0,
  count = 6,
) => {
  const { root, minor } = CHORDS[chord];
  const steps = [0, 7, 12, minor ? 15 : 16, 12, 7];
  const notes: Note[] = steps
    .slice(0, count)
    .map((st, i) => [
      eighthsFrom + i,
      shift(root, st + transpose),
      2.2,
      velocity * (i === 0 ? 1.12 : 1),
    ]);
  s.play("harp", bar, notes);
};

// A sustained cello root through the bar, in the cello's lowest octave.
const root = (
  s: Score,
  bar: number,
  chord: string,
  velocity: number,
  eighths = 6,
  from = 0,
  octaveUp = 0,
) => {
  let midi = Tone.Frequency(CHORDS[chord].root).toMidi();
  while (midi > 47) midi -= 12;
  while (midi < 36) midi += 12;
  const note = Tone.Frequency(midi + 12 * octaveUp, "midi").toNote();
  s.play("cello", bar, [[from, note, eighths, velocity]]);
};

// A harp glissando through a scale, one note every `gap` seconds.
const gliss = (
  s: Score,
  start: number,
  notes: string[],
  gap: number,
  v0: number,
  v1: number,
) => {
  notes.forEach((note, i) => {
    const t = i / Math.max(1, notes.length - 1);
    s.band.samplers.harp.triggerAttackRelease(
      note,
      1.2,
      start + i * gap,
      v0 + (v1 - v0) * t,
    );
  });
};

const scale = (
  from: string,
  pattern: number[],
  count: number,
  down = false,
): string[] => {
  const out: string[] = [];
  let midi = Tone.Frequency(from).toMidi();
  for (let i = 0; i < count; i++) {
    out.push(Tone.Frequency(midi, "midi").toNote());
    midi += (down ? -1 : 1) * pattern[i % pattern.length];
  }
  return out;
};

// Setup: the sea, then the clarinet's lullaby over the rocking harp.
function setup(s: Score) {
  rock(s, 1, "D", 0.26);
  s.play("glock", 1, [[3, "A6", 3, 0.22]]);
  tune(s, "clarinet", 2, 0, 8, { velocity: 0.62 });
  TUNE_CHORDS.forEach((chord, i) => {
    const [first, second] = chord.split(" ");
    if (second) {
      rock(s, 2 + i, first, 0.34, 0, 0, 3);
      rock(s, 2 + i, second, 0.34, 0, 3, 3);
    } else rock(s, 2 + i, first, 0.34);
    if (i >= 4) root(s, 2 + i, first, 0.3);
  });
  // He dozes off; the moon twinkles.
  s.play("glock", 9, [[3, "D7", 3, 0.18]]);
}

// Turn: the tug, the haul, the catch, the moon in the bucket, its dimming.
function turn(s: Score) {
  // Bar 10, the tug: the harp stops; the bass plucks twice.
  s.play("bassPizz", 10, [
    [0, "D2", 3, 0.9],
    [3, "A1", 3, 0.6],
  ]);
  // Bars 11–12, the haul: plucked cellos climb in D minor.
  s.play("celloPizz", 11, [
    [0, "D3", 1, 0.72],
    [1, "F3", 1, 0.72],
    [2, "A3", 1, 0.78],
    [3, "D4", 1, 0.81],
    [4, "A3", 1, 0.75],
    [5, "F3", 1, 0.78],
  ]);
  s.play("celloPizz", 12, [
    [0, "Bb2", 1, 0.81],
    [1, "D3", 1, 0.83],
    [2, "F3", 1, 0.86],
    [3, "Bb3", 1, 0.91],
    [4, "D4", 1, 0.94],
    [5, "F4", 1, 0.98],
  ]);
  s.play("bassPizz", 11, [[0, "D2", 3, 0.78]]);
  s.play("bassPizz", 12, [[0, "Bb1", 3, 0.85]]);
  s.play("violins", 12, [
    [0, "A4", 6, 0.32],
    [0, "D5", 6, 0.32],
  ]);

  // Bar 13, the catch: a harp glissando up through G Lydian as the moon comes
  // out of the water, and the wonder chord with its raised fourth.
  const lydian = scale("G3", [2, 2, 2, 1, 2, 2, 1], 19);
  gliss(s, at(13), lydian, 0.055, 0.35, 0.65);
  s.play("violins", 13, [
    [2, "B4", 10, 0.48],
    [2, "D5", 10, 0.46],
    [2, "F#5", 10, 0.46],
    [2, "C#6", 10, 0.38],
  ]);
  s.play("glock", 13, [
    [3, "D6", 1, 0.45],
    [4, "F#6", 1, 0.45],
    [5, "C#7", 2, 0.48],
  ]);
  s.play("cello", 13, [[0, "G2", 10, 0.36]]);
  s.play("bassPizz", 13, [[0, "G1", 3, 0.65]]);

  // Bars 14–17, the moon in the bucket: the tune as a music box.
  tune(s, "glock", 14, 0, 4, { transpose: 12, velocity: 0.62 });
  const wonder = ["D", "Bm", "G", "A"];
  const pads: string[][] = [
    ["A4", "D5", "F#5"],
    ["B4", "D5", "F#5"],
    ["B4", "D5", "G5", "C#6"],
    ["C#5", "E5", "A5"],
  ];
  wonder.forEach((chord, i) => {
    rock(s, 14 + i, chord, 0.24, 12, 0, 3);
    root(s, 14 + i, chord, 0.26);
    s.play(
      "violins",
      14 + i,
      pads[i].map((n): Note => [0, n, 6.4, 0.3]),
    );
  });

  // Bars 18–20, the moon dims: the tune turns minor and thins out, ending on
  // a suspension that does not resolve.
  s.play("clarinet", 18, [
    [0, "A4", 3, 0.5],
    [3, "F5", 2, 0.5],
    [5, "E5", 1, 0.46],
  ]);
  s.play("clarinet", 19, [
    [0, "D5", 2, 0.44],
    [2, "E5", 1, 0.42],
    [3, "F5", 3, 0.44],
  ]);
  s.play("clarinet", 20, [
    [0, "E5", 3, 0.38],
    [3, "D5", 3, 0.34],
  ]);
  rock(s, 18, "Dm", 0.24, 0, 0, 3);
  rock(s, 19, "Bb", 0.2, 0, 0, 3);
  rock(s, 20, "Gm", 0.16, 0, 0, 3);
  root(s, 18, "Dm", 0.24);
  root(s, 19, "Bb", 0.22);
  root(s, 20, "Gm", 0.2, 3);
  root(s, 20, "A", 0.2, 3, 3);
  s.play("glock", 18, [[0, "A5", 3, 0.38]]);
  s.play("glock", 19, [[0, "D6", 3, 0.26]]);
  s.play("glock", 20, [[0, "E6", 3, 0.16]]);
}

// Payoff: the release, darkness, the moon rising, the tune come home in E,
// the fish, the cat, and a last rock of the boat.
function payoff(s: Score) {
  // Bar 21, he tips it back: the harp sinks through A7.
  const sinking = [
    "A5",
    "G5",
    "E5",
    "C#5",
    "A4",
    "G4",
    "E4",
    "C#4",
    "A3",
    "G3",
    "E3",
    "C#3",
    "A2",
  ];
  gliss(s, at(21), sinking, 0.12, 0.42, 0.14);
  s.play("cello", 21, [[0, "A2", 6, 0.24]]);

  // Bar 22 is silent but for the sea.

  // Bars 23–24, the moon rises: C and D climb toward E, and the clarinet
  // reaches up the tune's opening sixth twice.
  rock(s, 23, "C", 0.3);
  rock(s, 24, "D", 0.4);
  root(s, 23, "C", 0.28);
  root(s, 24, "D", 0.36);
  s.play("clarinet", 23, [
    [0, "G4", 3, 0.56],
    [3, "E5", 3, 0.64],
  ]);
  s.play("clarinet", 24, [
    [0, "A4", 3, 0.7],
    [3, "F#5", 3, 0.78],
  ]);
  s.play("violins", 23, [
    [0, "G4", 6.4, 0.22],
    [0, "C5", 6.4, 0.22],
  ]);
  s.play("violins", 24, [
    [0, "A4", 6.4, 0.3],
    [0, "D5", 6.4, 0.3],
  ]);
  s.play("glock", 24, [
    [3, "E6", 1, 0.26],
    [4, "G#6", 1, 0.28],
    [5, "B6", 1, 0.3],
  ]);

  // Bars 25–28, home in E: the tune's second half, clarinet and violins
  // together, the glockenspiel an octave above.
  tune(s, "clarinet", 25, 4, 8, { transpose: 2, velocity: 0.82 });
  tune(s, "violins", 25, 4, 8, { transpose: 2, velocity: 0.46 });
  tune(s, "glock", 25, 4, 6, { transpose: 14, velocity: 0.24 });
  s.play("glock", 27, [
    [0, "A6", 2, 0.24],
    [2, "G#6", 1, 0.24],
  ]);
  const home = ["E", "C#m", "A B", "E"];
  home.forEach((chord, i) => {
    const [first, second] = chord.split(" ");
    // Keep the harp's figure low: roots from C3 up drop an octave.
    const low = (c: string) =>
      Tone.Frequency(CHORDS[c].root).toMidi() >= 48 ? -12 : 0;
    if (second) {
      rock(s, 25 + i, first, 0.5, low(first), 0, 3);
      rock(s, 25 + i, second, 0.5, low(second), 3, 3);
      root(s, 25 + i, first, 0.4, 3);
      root(s, 25 + i, second, 0.4, 3, 3);
    } else {
      rock(s, 25 + i, first, 0.5, low(first));
      root(s, 25 + i, first, 0.4);
    }
  });
  // A fish leaps; it lands in the boat; the cat has it.
  s.play("glock", 27, [
    [3, "E6", 0.5, 0.3],
    [3.5, "G#6", 0.5, 0.3],
    [4, "B6", 1, 0.32],
  ]);
  s.play("celloPizz", 28, [
    [0, "E3", 2, 0.6],
    [4, "B2", 1, 0.5],
    [5, "E3", 1, 0.56],
  ]);

  // Bars 29–30, the coda: the boat rocks, the tune reaches up once more and
  // settles, the moon twinkles.
  rock(s, 29, "E", 0.32, -12);
  rock(s, 30, "E", 0.24, -12);
  root(s, 29, "E", 0.22, 12);
  root(s, 30, "E", 0.18, 6);
  s.play("clarinet", 29, [
    [0, "B4", 3, 0.5],
    [3, "G#5", 3, 0.48],
  ]);
  s.play("clarinet", 30, [
    [0, "F#5", 2, 0.42],
    [2, "E5", 4, 0.4],
  ]);
  s.play("violins", 29, [
    [0, "B4", 12, 0.18],
    [0, "E5", 12, 0.18],
  ]);
  s.play("glock", 30, [[3, "B6", 3, 0.18]]);
}

// The sea swells a little every three bars, rises in the silent bar, and
// fades out with the film.
function sea(band: Band) {
  const level = band.sea.gain;
  const quiet = 0.007;
  const alone = 0.02;
  level.setValueAtTime(0, 0);
  level.linearRampToValueAtTime(alone, 1.2);
  level.linearRampToValueAtTime(quiet, at(3));
  for (let bar = 3; bar <= BARS; bar += 1.5) {
    const top = bar >= 22 && bar < 23 ? alone : quiet * 1.35;
    level.linearRampToValueAtTime(top, at(bar) + 1.5);
    level.linearRampToValueAtTime(
      bar >= 21 && bar < 22.5 ? alone : quiet,
      at(bar + 1.5),
    );
  }
  level.linearRampToValueAtTime(alone * 0.8, at(29));
  level.linearRampToValueAtTime(0, DURATION_SECONDS);
}

export type RenderOptions = { only?: InstrumentName[]; dry?: boolean };

export async function renderScore(
  options: RenderOptions = {},
): Promise<AudioBuffer> {
  const buffer = await Tone.Offline(
    async () => {
      const band = createBand(options.only, options.dry);
      await Tone.loaded();
      const s = scorer(band);
      setup(s);
      turn(s);
      payoff(s);
      if (!options.only) sea(band);
      // The last reverb tails fade with the picture.
      band.master.gain.setValueAtTime(0.9, DURATION_SECONDS - 1.2);
      band.master.gain.linearRampToValueAtTime(0, DURATION_SECONDS);
    },
    DURATION_SECONDS + MASTER_LATENCY,
    2,
    SAMPLE_RATE,
  );
  return buffer.slice(MASTER_LATENCY).get()!;
}
