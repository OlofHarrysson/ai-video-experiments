import * as Tone from "tone";
import { at, DURATION_SECONDS, EIGHTH_SECONDS, SECTIONS } from "../timing";
import { createBand, type Band, type InstrumentName } from "./instruments";

// The Moon Fisher's score: a lilting folk tune in 6/8 for clarinet, solo
// violin and piano.
//
// The tune reaches up a sixth, like a hand toward the moon, and settles back
// by step. The clarinet sings it over the piano's bounce while the violin
// weaves a second line; high piano plays it like a music box once the moon
// is in the bucket; the violin mourns it in minor as the moon dims; and it
// comes home a step higher when the moon rises, clarinet below and violin
// soaring an octave above.

const SAMPLE_RATE = 48000;
// The glue compressor and the limiter each look 6 ms ahead; the render runs
// that much long and is trimmed.
const MASTER_LATENCY = 0.012;

// [eighth within the bar, note, length in eighths, velocity]
type Note = [eighth: number, note: string, eighths: number, velocity?: number];

// Every note the score plays, for checking the render against the page.
export type ScoredNote = {
  instrument: InstrumentName;
  time: number;
  note: string;
  duration: number;
};

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

// Each chord's bass note, a close right-hand voicing below the tune, and
// whether its third is minor.
const CHORDS: Record<
  string,
  { bass: string; chord: string[]; minor?: boolean }
> = {
  D: { bass: "D2", chord: ["A3", "D4", "F#4"] },
  Bm: { bass: "B1", chord: ["B3", "D4", "F#4"], minor: true },
  G: { bass: "G1", chord: ["G3", "B3", "D4"] },
  A: { bass: "A1", chord: ["A3", "C#4", "E4"] },
  A7: { bass: "A1", chord: ["G3", "C#4", "E4"] },
  Dm: { bass: "D2", chord: ["A3", "D4", "F4"], minor: true },
  Bb: { bass: "Bb1", chord: ["Bb3", "D4", "F4"] },
  Gm: { bass: "G1", chord: ["G3", "Bb3", "D4"], minor: true },
  C: { bass: "C2", chord: ["G3", "C4", "E4"] },
  E: { bass: "E2", chord: ["G#3", "B3", "E4"] },
  "C#m": { bass: "C#2", chord: ["G#3", "C#4", "E4"], minor: true },
  B: { bass: "B1", chord: ["B3", "D#4", "F#4"] },
};

const shift = (note: string, semitones: number): string =>
  Tone.Frequency(note).transpose(semitones).toNote();

type PlayOpts = { transpose?: number; velocity?: number; legato?: number };

class Score {
  readonly notes: ScoredNote[] = [];
  constructor(readonly band: Band) {}

  play(name: InstrumentName, bar: number, notes: Note[], opts: PlayOpts = {}) {
    const { transpose = 0, velocity = 0.6, legato = 1 } = opts;
    for (const [e, note, len, v] of notes) {
      this.hit(
        name,
        at(bar, e),
        shift(note, transpose),
        len * EIGHTH_SECONDS * legato,
        v ?? velocity,
      );
    }
  }

  hit(
    name: InstrumentName,
    time: number,
    note: string,
    duration: number,
    velocity: number,
  ) {
    this.band.samplers[name].triggerAttackRelease(
      note,
      duration,
      time,
      velocity,
    );
    this.notes.push({ instrument: name, time, note, duration });
  }

  // The tune's bars `from`..`to` (0-based, exclusive), starting at `bar`.
  tune(
    name: InstrumentName,
    bar: number,
    from: number,
    to: number,
    opts?: PlayOpts,
  ) {
    for (let i = from; i < to; i++)
      this.play(name, bar + i - from, TUNE[i], opts);
  }

  // The piano's bounce: bass, chord, chord, fifth, chord, chord. `from` and
  // `count` play part of the bar, for two chords in one bar.
  bounce(bar: number, chord: string, v: number, from = 0, count = 6) {
    const { bass, chord: notes } = CHORDS[chord];
    const low = shift(bass, 12);
    for (let e = from; e < from + count; e++) {
      if (e % 3 === 0) {
        const note = e === from ? low : shift(low, 7);
        this.play("piano", bar, [[e, note, 1.5, v]]);
      } else {
        this.play(
          "piano",
          bar,
          notes.map((n): Note => [e, n, 0.8, v * 0.62]),
        );
      }
    }
  }

  // The piano's flowing figure: bass, fifth, octave, tenth, octave, fifth.
  flow(bar: number, chord: string, v: number, count = 6) {
    const root = shift(CHORDS[chord].bass, 12);
    const steps = [0, 7, 12, CHORDS[chord].minor ? 15 : 16, 12, 7];
    this.play(
      "piano",
      bar,
      steps
        .slice(0, count)
        .map(
          (st, i): Note => [i, shift(root, st), 2.5, v * (i === 0 ? 1.1 : 0.9)],
        ),
    );
  }

  // Double bass on the beats: the root, then the fifth.
  pulse(bar: number, chord: string, v: number, fifth = true) {
    const bass = CHORDS[chord].bass;
    const notes: Note[] = [[0, bass, 3, v]];
    if (fifth) notes.push([3, shift(bass, 7), 3, v * 0.8]);
    this.play("bassPizz", bar, notes);
  }

  // A sustained cello root in the cello's lowest octave.
  root(bar: number, chord: string, v: number, eighths = 6, from = 0) {
    let midi = Tone.Frequency(CHORDS[chord].bass).toMidi();
    while (midi < 36) midi += 12;
    while (midi > 47) midi -= 12;
    this.play("cello", bar, [
      [from, Tone.Frequency(midi, "midi").toNote(), eighths, v],
    ]);
  }

  // A harp glissando, one note every `gap` seconds.
  gliss(start: number, notes: string[], gap: number, v0: number, v1: number) {
    notes.forEach((note, i) => {
      const t = i / Math.max(1, notes.length - 1);
      this.hit("harp", start + i * gap, note, 1.2, v0 + (v1 - v0) * t);
    });
  }
}

const scale = (from: string, pattern: number[], count: number): string[] => {
  const out: string[] = [];
  let midi = Tone.Frequency(from).toMidi();
  for (let i = 0; i < count; i++) {
    out.push(Tone.Frequency(midi, "midi").toNote());
    midi += pattern[i % pattern.length];
  }
  return out;
};

// Setup: the piano's bounce, the tune on clarinet with the violin weaving
// below it, and a yawn as he dozes off.
function setup(s: Score) {
  s.bounce(1, "D", 0.5);
  s.pulse(1, "D", 0.55);

  s.tune("clarinet", 2, 0, 8, { velocity: 0.66 });
  TUNE_CHORDS.forEach((chord, i) => {
    const [first, second] = chord.split(" ");
    if (second) {
      s.bounce(2 + i, first, 0.5, 0, 3);
      s.bounce(2 + i, second, 0.5, 3, 3);
    } else s.bounce(2 + i, first, 0.5);
    s.pulse(2 + i, first, 0.55, !second);
    if (i >= 4) s.root(2 + i, first, 0.28);
  });
  s.play("violin", 6, [[0, "F#4", 6, 0.48]]);
  s.play("violin", 7, [
    [0, "F#4", 3, 0.48],
    [3, "B4", 3, 0.5],
  ]);
  s.play("violin", 8, [
    [0, "B4", 3, 0.52],
    [3, "C#5", 3, 0.54],
  ]);
  s.play("violin", 9, [[0, "A4", 6, 0.5]]);

  // Bars 10–11, he dozes: a lazy falling line over a slower piano.
  s.play("clarinet", 10, [
    [0, "F#5", 3, 0.52],
    [3, "E5", 2, 0.46],
    [5, "D5", 1, 0.42],
  ]);
  s.play("clarinet", 11, [[0, "A4", 6, 0.38]]);
  s.flow(10, "D", 0.36);
  s.flow(11, "G", 0.3, 3);
  s.play(
    "piano",
    11,
    CHORDS.A.chord.map((n): Note => [3, n, 3, 0.2]),
  );
  s.play("violins", 10, [
    [0, "D5", 12, 0.16],
    [0, "F#5", 12, 0.14],
  ]);
}

// Turn: the tug, the hooked moon, the haul, the catch, the moon in the
// bucket, its dimming. Each passage starts where its section does.
function turn(s: Score) {
  const [TUG] = SECTIONS.tug;
  const [HOOKED] = SECTIONS.hooked;
  const [HAUL] = SECTIONS.haul;
  const [CATCH] = SECTIONS.catch;
  const [WONDER] = SECTIONS.wonder;
  const [DIM] = SECTIONS.dimming;

  // The tug: everything stops for two plucks and a low piano jolt.
  s.play("bassPizz", TUG, [
    [0, "D2", 3, 0.95],
    [3, "A1", 3, 0.72],
  ]);
  s.play("piano", TUG, [
    [0, "D2", 1, 0.55],
    [0, "D3", 1, 0.5],
  ]);

  // The hooked moon: the music holds its breath over the sea, with only a
  // low cello note, until he wakes.
  s.play("cello", HOOKED, [[0, "D2", 6, 0.2]]);

  // The haul: plucked strings drive upward under a rising violin and short
  // piano stabs, D minor to B flat to C.
  const haul: [string, string[], string][] = [
    ["Dm", ["D3", "F3", "A3", "D4", "A3", "F3"], "D5"],
    ["Bb", ["Bb2", "D3", "F3", "Bb3", "F3", "D3"], "F5"],
    ["C", ["C3", "E3", "G3", "C4", "E4", "G4"], "G5"],
  ];
  haul.forEach(([chord, plucks, high], i) => {
    const bar = HAUL + i;
    const v = 0.62 + 0.1 * i;
    s.play(
      "celloPizz",
      bar,
      plucks.map((n, e): Note => [e, n, 1, v + 0.02 * e]),
    );
    s.pulse(bar, chord, 0.75 + 0.05 * i);
    const { bass, chord: notes } = CHORDS[chord];
    s.play("piano", bar, [
      [0, bass, 1, 0.5 + 0.05 * i],
      [0, shift(bass, 12), 1, 0.45 + 0.05 * i],
      ...notes.flatMap((n): Note[] => [
        [2, n, 0.6, 0.4 + 0.05 * i],
        [5, n, 0.6, 0.42 + 0.05 * i],
      ]),
    ]);
    s.play("violin", bar, [[0, high, 6, 0.48 + 0.07 * i]]);
    s.play(
      "violins",
      bar,
      notes.slice(1).map((n): Note => [0, shift(n, 12), 6.2, 0.24 + 0.08 * i]),
    );
  });

  // The catch: a harp sweep up through G Lydian as the moon comes out of the
  // water, and the wonder chord with its raised fourth.
  s.gliss(at(CATCH), scale("G3", [2, 2, 2, 1, 2, 2, 1], 19), 0.045, 0.3, 0.58);
  s.play("violins", CATCH, [
    [2, "B4", 10, 0.4],
    [2, "D5", 10, 0.38],
    [2, "F#5", 10, 0.38],
    [2, "C#6", 10, 0.32],
  ]);
  s.play("piano", CATCH, [
    [3, "D6", 1, 0.45],
    [4, "F#6", 1, 0.45],
    [5, "C#7", 2, 0.5],
  ]);
  s.play("cello", CATCH, [[0, "G2", 10, 0.34]]);
  s.play("bassPizz", CATCH, [[0, "G1", 3, 0.7]]);

  // The moon in the bucket: high piano plays the tune like a music box over
  // soft strings; the violin answers.
  s.tune("piano", WONDER, 0, 4, { transpose: 12, velocity: 0.95 });
  s.tune("piano", WONDER, 0, 4, { velocity: 0.6 });
  const wonder = ["D", "Bm", "G", "A"];
  const pads: string[][] = [
    ["A4", "D5", "F#5"],
    ["B4", "D5", "F#5"],
    ["B4", "D5", "G5", "C#6"],
    ["C#5", "E5", "A5"],
  ];
  wonder.forEach((chord, i) => {
    s.flow(WONDER + i, chord, 0.36);
    s.root(WONDER + i, chord, 0.32);
    s.play(
      "violins",
      WONDER + i,
      pads[i].map((n): Note => [0, n, 6.4, 0.46]),
    );
  });
  s.play("violin", WONDER + 4, [
    [0, "E5", 2, 0.5],
    [2, "F#5", 1, 0.5],
    [3, "E5", 3, 0.48],
  ]);
  s.flow(WONDER + 4, "A", 0.22);
  s.root(WONDER + 4, "A", 0.22);

  // The moon dims: the violin sings the tune in minor while the piano thins
  // out, ending on an unresolved A7.
  s.play("violin", DIM, [
    [0, "A4", 3, 0.76],
    [3, "F5", 2, 0.76],
    [5, "E5", 1, 0.72],
  ]);
  s.play("violin", DIM + 1, [
    [0, "D5", 2, 0.7],
    [2, "E5", 1, 0.68],
    [3, "F5", 3, 0.7],
  ]);
  s.play("violin", DIM + 2, [
    [0, "E5", 3, 0.66],
    [3, "D5", 3, 0.62],
  ]);
  s.play("violin", DIM + 3, [[0, "C#5", 6, 0.6]]);
  s.flow(DIM, "Dm", 0.3);
  s.flow(DIM + 1, "Bb", 0.26, 4);
  s.flow(DIM + 2, "Gm", 0.22, 3);
  s.play(
    "piano",
    DIM + 3,
    CHORDS.A7.chord.map((n): Note => [0, n, 6, 0.18]),
  );
  s.root(DIM, "Dm", 0.24);
  s.root(DIM + 1, "Bb", 0.22);
  s.root(DIM + 2, "Gm", 0.2);
  s.root(DIM + 3, "A", 0.18);
}

// Payoff: the release, darkness, the moon rising, the tune come home in E,
// the fish, the cat, and a last lilt of the boat.
function payoff(s: Score) {
  const [RELEASE] = SECTIONS.release;
  const [RISE] = SECTIONS.rise;
  const [FINALE] = SECTIONS.finale;
  const [CODA] = SECTIONS.coda;

  // He tips it back: the harp sinks through A7.
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
  s.gliss(at(RELEASE), sinking, 0.1, 0.42, 0.14);
  s.play("cello", RELEASE, [[0, "A2", 6, 0.22]]);

  // The darkness is silent but for the sea.

  // The moon rises: C, D and B lead home to E; the clarinet reaches up the
  // tune's opening sixth twice, then runs up into the key.
  const rise: [string, Note[], string][] = [
    [
      "C",
      [
        [0, "G4", 3],
        [3, "E5", 3],
      ],
      "E5",
    ],
    [
      "D",
      [
        [0, "A4", 3],
        [3, "F#5", 3],
      ],
      "F#5",
    ],
    [
      "B",
      [
        [0, "B4", 2],
        [2, "C#5", 1],
        [3, "D#5", 3],
      ],
      "A5",
    ],
  ];
  rise.forEach(([chord, reach, held], i) => {
    const bar = RISE + i;
    s.play("clarinet", bar, reach, { velocity: 0.6 + 0.08 * i });
    s.play("violin", bar, [[0, held, 6, 0.42 + 0.07 * i]]);
    s.flow(bar, chord, 0.32 + 0.08 * i);
    s.pulse(bar, chord, 0.55 + 0.08 * i);
    s.root(bar, chord, 0.28 + 0.05 * i);
    s.play(
      "violins",
      bar,
      CHORDS[chord].chord
        .slice(1)
        .map((n): Note => [0, shift(n, 12), 6.2, 0.24 + 0.07 * i]),
    );
  });

  // Home in E: the tune's second half, clarinet and the violin an octave
  // above it, over the piano's bounce.
  s.tune("clarinet", FINALE, 4, 8, { transpose: 2, velocity: 0.98 });
  s.tune("violin", FINALE, 4, 8, { transpose: 14, velocity: 0.7 });
  const home = ["E", "C#m", "A B", "E"];
  home.forEach((chord, i) => {
    const [first, second] = chord.split(" ");
    if (second) {
      s.bounce(FINALE + i, first, 0.7, 0, 3);
      s.bounce(FINALE + i, second, 0.7, 3, 3);
      s.root(FINALE + i, first, 0.46, 3);
      s.root(FINALE + i, second, 0.46, 3, 3);
    } else {
      s.bounce(FINALE + i, first, 0.7);
      s.root(FINALE + i, first, 0.46);
    }
    s.pulse(FINALE + i, first, 0.76, !second);
    s.play(
      "violins",
      FINALE + i,
      CHORDS[first].chord
        .slice(1)
        .map((n): Note => [0, shift(n, 12), 6.2, 0.34]),
    );
  });

  // The finale's last two bars, the tune's last phrase once more, a little
  // softer. A fish leaps up the B chord and lands on the home note; the cat
  // has it.
  const GIFT = FINALE + 4;
  s.tune("clarinet", GIFT, 6, 8, { transpose: 2, velocity: 0.82 });
  s.tune("violin", GIFT, 6, 8, { transpose: 14, velocity: 0.56 });
  s.bounce(GIFT, "A", 0.6, 0, 3);
  s.bounce(GIFT, "B", 0.6, 3, 3);
  s.bounce(GIFT + 1, "E", 0.52);
  s.play("bassPizz", GIFT, [
    [0, "A1", 3, 0.64],
    [3, "B1", 3, 0.62],
  ]);
  s.pulse(GIFT + 1, "E", 0.56);
  s.root(GIFT, "A", 0.4, 3);
  s.root(GIFT, "B", 0.4, 3, 3);
  s.root(GIFT + 1, "E", 0.38);
  s.play("violins", GIFT, [
    [0, "C#5", 3, 0.3],
    [0, "E5", 3, 0.3],
    [3, "D#5", 3, 0.3],
    [3, "F#5", 3, 0.3],
  ]);
  s.play("violins", GIFT + 1, [
    [0, "B4", 6, 0.28],
    [0, "E5", 6, 0.28],
  ]);
  s.play("piano", GIFT, [
    [3, "B5", 0.5, 0.5],
    [3.5, "D#6", 0.5, 0.52],
    [4, "F#6", 0.5, 0.54],
    [4.5, "B6", 1.5, 0.56],
  ]);
  s.play("celloPizz", GIFT + 1, [[0, "E3", 1, 0.6]]);

  // The coda: the piano's lilt carries on, quieter; the tune reaches up once
  // more and settles; a plucked ta-dum and a last high note like a star.
  s.bounce(CODA, "E", 0.42);
  s.bounce(CODA + 1, "A", 0.36);
  s.pulse(CODA, "E", 0.45);
  s.pulse(CODA + 1, "A", 0.4);
  s.root(CODA, "E", 0.3);
  s.root(CODA + 1, "A", 0.26);
  s.play("clarinet", CODA, [
    [0, "B4", 3, 0.56],
    [3, "G#5", 3, 0.54],
  ]);
  s.play("clarinet", CODA + 1, [
    [0, "F#5", 2, 0.48],
    [2, "E5", 4, 0.46],
  ]);
  s.play(
    "piano",
    CODA + 2,
    CHORDS.B.chord.map((n): Note => [0, n, 2, 0.24]),
  );
  s.play("celloPizz", CODA + 2, [
    [0, "B2", 1, 0.5],
    [3, "E3", 1, 0.56],
  ]);
  s.play("piano", CODA + 2, [
    [3, "E2", 9, 0.32],
    [3.2, "B2", 9, 0.28],
    [3.4, "E3", 9, 0.28],
    [3.6, "G#3", 9, 0.26],
    [3.8, "B3", 9, 0.26],
  ]);
  s.play("violin", CODA + 2, [[3, "B5", 9, 0.3]]);
  s.play("cello", CODA + 2, [[3, "E2", 9, 0.24]]);
  s.play("piano", CODA + 3, [[1, "E6", 5, 0.28]]);
}

// The sea: quiet under the music, rising while the hooked moon holds its
// breath, alone in the darkness, gone at the end.
function sea(band: Band) {
  const level = band.sea.gain;
  const quiet = 0.007;
  const alone = 0.02;
  const [HOOKED, HAUL] = SECTIONS.hooked;
  const [RELEASE, DARKNESS] = SECTIONS.release;
  const [RISE] = SECTIONS.rise;
  const [CODA] = SECTIONS.coda;
  level.setValueAtTime(0, 0);
  level.linearRampToValueAtTime(alone, 1);
  level.linearRampToValueAtTime(quiet, at(3));
  level.setValueAtTime(quiet, at(HOOKED));
  level.linearRampToValueAtTime(alone, at(HOOKED, 2));
  level.setValueAtTime(alone, at(HAUL) - 0.2);
  level.linearRampToValueAtTime(quiet, at(HAUL));
  level.setValueAtTime(quiet, at(RELEASE));
  level.linearRampToValueAtTime(alone, at(DARKNESS));
  level.setValueAtTime(alone, at(RISE));
  level.linearRampToValueAtTime(quiet, at(RISE + 1));
  level.setValueAtTime(quiet, at(CODA + 1));
  level.linearRampToValueAtTime(alone * 0.8, at(CODA + 2));
  level.linearRampToValueAtTime(0, DURATION_SECONDS);
}

export type RenderOptions = { only?: InstrumentName[]; dry?: boolean };

export async function renderScore(
  options: RenderOptions = {},
): Promise<{ buffer: AudioBuffer; notes: ScoredNote[] }> {
  let notes: ScoredNote[] = [];
  const buffer = await Tone.Offline(
    async () => {
      const band = createBand(options.only, options.dry);
      await Tone.loaded();
      const s = new Score(band);
      setup(s);
      turn(s);
      payoff(s);
      notes = s.notes;
      if (!options.only) sea(band);
      // The last reverb tails fade with the picture.
      band.master.gain.setValueAtTime(0.9, DURATION_SECONDS - 1.2);
      band.master.gain.linearRampToValueAtTime(0, DURATION_SECONDS);
    },
    DURATION_SECONDS + MASTER_LATENCY,
    2,
    SAMPLE_RATE,
  );
  return { buffer: buffer.slice(MASTER_LATENCY).get()!, notes };
}
