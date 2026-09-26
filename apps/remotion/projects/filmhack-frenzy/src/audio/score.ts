import * as Tone from 'tone';
import { DURATION_IN_SECONDS, seconds as at } from '../timing';
import { Kit } from './kit';

export const SAMPLE_RATE = 48000;

type Chord = 'A' | 'D' | 'E' | 'F#m' | 'F' | 'G';
/** [beat within the bar, note, length in beats] */
type Note = [beat: number, note: string, beats: number];
type Bar = { chord: Chord; tune: Note[] };

const TONES: Record<Chord, string[]> = {
  A: ['A', 'C#', 'E'],
  D: ['D', 'F#', 'A'],
  E: ['E', 'G#', 'B'],
  'F#m': ['F#', 'A', 'C#'],
  F: ['F', 'A', 'C'],
  G: ['G', 'B', 'D'],
};

/** Close voicings for the pad and the off-beat plucks, voice-led around C#4–A4. */
const TRIAD: Record<Chord, string[]> = {
  A: ['C#4', 'E4', 'A4'],
  D: ['D4', 'F#4', 'A4'],
  E: ['B3', 'E4', 'G#4'],
  'F#m': ['C#4', 'F#4', 'A4'],
  F: ['C4', 'F4', 'A4'],
  G: ['B3', 'D4', 'G4'],
};

/** Bass roots. E–F–G climbs out of the chaos, and drop two lands an octave down on A. */
const ROOT: Record<Chord, string> = { A: 'A1', D: 'D2', E: 'E2', 'F#m': 'F#1', F: 'F2', G: 'G2' };

const midi = (note: string) => Tone.Frequency(note).toMidi();
const noteName = (m: number) => Tone.Frequency(m, 'midi').toNote();
const octaveUp = (note: string) => noteName(midi(note) + 12);

/** A brass voicing: chord tones stacked down from the tune's note, over the root in the third octave. */
function stack(chord: Chord, top: string, size = 4) {
  const classes = TONES[chord].map((n) => midi(`${n}4`) % 12);
  const notes: number[] = [];
  for (let m = midi(top); notes.length < size; m--) if (classes.includes(m % 12)) notes.push(m);
  return [midi(`${TONES[chord][0]}3`), ...notes.reverse()].map(noteName);
}

/** The hook, in the rhythm of LIGHTS! CAM-er-a AC-TION!: a run up to the octave. */
const HOOK: Note[] = [[0, 'E5', 1], [1, 'A4', 0.5], [1.5, 'B4', 0.25], [1.75, 'C#5', 0.25], [2, 'E5', 0.5], [2.5, 'A5', 1]];
/** The hook's run, landing somewhere new. */
const hook = (last: string, beats = 1): Note[] => [...HOOK.slice(0, 5), [2.5, last, beats]];
/** The answer: a held note that sighs down through the chord. */
const sigh = (a: string, b: string, c: string, d: string): Note[] => [[0, a, 1.5], [1.5, b, 0.5], [2, c, 0.5], [2.5, d, 1]];

/** Beats 8–24: I–V–vi–IV, the hook and its answer twice. */
const DROP_ONE: Bar[] = [
  { chord: 'A', tune: HOOK },
  { chord: 'E', tune: sigh('G#5', 'F#5', 'E5', 'C#5') },
  { chord: 'F#m', tune: HOOK },
  { chord: 'D', tune: sigh('A5', 'G#5', 'F#5', 'D5') },
];

/**
 * Beats 32–64: the same four bars reaching higher, then vi–IV–V climbing to the top note
 * on GET ON THE LIST! and home to I on the final hit, beat 62.
 */
const DROP_TWO: Bar[] = [
  { chord: 'A', tune: HOOK },
  { chord: 'E', tune: sigh('G#5', 'F#5', 'E5', 'C#5') },
  { chord: 'F#m', tune: hook('C#6') },
  { chord: 'D', tune: sigh('B5', 'A5', 'F#5', 'D5') },
  { chord: 'F#m', tune: [[0, 'A5', 1], [1, 'F#5', 0.5], [1.5, 'G#5', 0.25], [1.75, 'A5', 0.25], [2, 'C#6', 0.5], [2.5, 'B5', 1.5]] },
  { chord: 'D', tune: [[0, 'A5', 0.5], [0.5, 'D6', 1.5], [2, 'C#6', 0.5], [2.5, 'B5', 0.5], [3, 'A5', 1]] },
  { chord: 'E', tune: sigh('G#5', 'F#5', 'E5', 'C#5') },
  { chord: 'E', tune: hook('A5', 1.5) },
];

/** Chrome's compressor looks 6 ms ahead, and the master runs two (glue and limiter); the render is trimmed by that much. */
const MASTER_LATENCY = 0.012;

export async function renderScore(): Promise<AudioBuffer> {
  const buffer = await Tone.Offline(() => {
    const kit = new Kit();
    arrange(kit);
    kit.flush();
  }, DURATION_IN_SECONDS + MASTER_LATENCY, 2, SAMPLE_RATE);
  return buffer.slice(MASTER_LATENCY).get()!;
}

export function arrange(k: Kit) {
  coldOpen(k);
  stopScrolling(k);
  dropOne(k);
  chaos(k);
  sunday(k);
  dropTwo(k);
}

/** The lead, with a bell on top in drop two; slightly detached except for the sixteenth-note runs. */
function play(k: Kit, b0: number, tune: Note[], bell = false) {
  for (const [b, note, beats] of tune) {
    const t = at(b0 + b);
    k.lead(t, note, at(beats) * (beats <= 0.25 ? 0.95 : 0.86));
    if (bell) k.bell(t, note);
  }
}

/** One bar of a drop: a rock backbeat in drop one, four-on-the-floor with claps and off-beat open hats in drop two. */
function groove(k: Kit, b0: number, bar: Bar, floor: boolean, beats = 4) {
  const s = (n: number) => at(b0 + n / 4);
  const steps = beats * 4;
  const root = ROOT[bar.chord];
  for (const n of floor ? [0, 4, 8, 12] : [0, 6, 8]) if (n < steps) k.kick(s(n));
  for (const n of [4, 12]) {
    if (n >= steps) continue;
    k.snare(s(n), 0.85);
    if (floor) k.clap(s(n), 0.7);
  }
  for (let n = 0; n < steps; n += 2) {
    if (floor && n % 4 === 2) k.openHat(s(n), 0.55);
    if (!floor && n !== 14) k.hat(s(n), n % 4 === 0 ? 0.6 : 0.4);
  }
  if (floor) for (let n = 0; n < steps; n++) k.shaker(s(n), n % 2 ? 0.45 : 0.7);
  else if (steps === 16) k.openHat(s(14), 0.5);
  for (let n = 0; n < steps; n += 2) {
    const low = n % 4 === 0;
    k.bass(s(n), low ? root : octaveUp(root), at(0.42), low ? 0.95 : 0.8, low);
  }
  k.pad(s(0), TRIAD[bar.chord], at(beats) * 0.97, 0.7);
  for (let n = 2; n < steps; n += 4) k.pluck(s(n), TRIAD[bar.chord], 0.85);
  play(k, b0, bar.tune, floor);
}

/** Beats 0–4: the hook's run as a fanfare, one chord per slammed word, I–IV–V–I. */
function coldOpen(k: Kit) {
  const hits: [number, Chord, string][] = [[0, 'A', 'E5'], [1, 'D', 'A4'], [2, 'E', 'E5'], [3, 'A', 'A5']];
  k.impact(at(0), 0.9);
  for (const [b, chord, top] of hits) {
    const len = at(b === 3 ? 0.95 : 0.45);
    k.kick(at(b), 1, false);
    k.brass(at(b), stack(chord, top), len, b === 3 ? 1 : 0.85);
    k.bass(at(b), ROOT[chord], len, 1, true);
  }
  k.snare(at(3), 0.95);
  k.crash(at(3), 0.8);
  play(k, 0, [[0, 'E5', 1], [1, 'A4', 0.5], [1.5, 'B4', 0.25], [1.75, 'C#5', 0.25], [2, 'E5', 1], [3, 'A5', 1]]);
}

/** Beats 4–8: STOP STOP STOP SCROLLING on the dominant, then START CREATING builds to a breath before the drop. */
function stopScrolling(k: Kit) {
  const stab = stack('E', 'B4');
  [4, 4.5, 5, 5.5, 6, 6.5].forEach((b, i) => {
    k.kick(at(b), 0.9, false);
    k.brass(at(b), stab, at(i < 4 ? 0.3 : 0.4), 0.72 + 0.04 * i);
  });
  [4, 4.5, 5, 5.5].forEach((b) => k.bass(at(b), 'E2', at(0.3), 0.9, true));
  for (let b = 6; b < 7.75; b += 0.5) k.bass(at(b), b % 1 ? 'E3' : 'E2', at(0.42), 0.85, b % 1 === 0);
  [6, 6.5, 7, 7.25, 7.5].forEach((b, i) => k.snare(at(b), 0.45 + 0.1 * i));
  k.pad(at(6), TRIAD.E, at(1.7), 0.6, 700, 4000);
  k.riser(at(6), at(7.75), 0.22);
  k.breath(at(7.75), at(8));
  play(k, 7, [[0, 'B4', 0.25], [0.25, 'C#5', 0.25], [0.5, 'D5', 0.25]]);
}

/** Beats 8–24: drop one. The slate claps on ACTION!, beat 10. */
function dropOne(k: Kit) {
  k.impact(at(8), 1);
  k.crash(at(8), 0.85);
  DROP_ONE.forEach((bar, i) => groove(k, 8 + 4 * i, bar, false));
  k.snare(at(10), 0.95);
  k.clap(at(10), 1);
  k.crash(at(10), 0.6);
  [23.25, 23.5, 23.75].forEach((b, i) => k.snare(at(b), 0.5 + 0.15 * i));
}

/** Beats 24–28: a stab climbs on every new panel over an E pedal, then the clock hits zero and the tape stops. */
function chaos(k: Kit) {
  const hits: [number, Chord, string][] = [[24, 'E', 'B4'], [25, 'A', 'C#5'], [26, 'D', 'D5'], [26.5, 'E', 'E5'], [27, 'F#m', 'F#5']];
  k.crash(at(24), 0.7);
  for (const [b, chord, top] of hits) {
    k.kick(at(b), 0.9);
    k.brass(at(b), stack(chord, top), at(0.4), 0.8);
    k.lead(at(b), top, at(0.4), 0.8);
  }
  k.pad(at(24), ['E3', 'B3', 'E4', 'B4'], at(3.5), 0.6, 900, 5000);
  for (let b = 24; b < 27.5; b += 0.5) k.bass(at(b), b % 1 ? 'E3' : 'E2', at(0.42), 0.85, b % 1 === 0);
  for (let b = 24; b < 26; b += 0.5) k.snare(at(b), 0.3 + 0.08 * (b - 24));
  for (let b = 26; b < 27.5; b += 0.25) k.snare(at(b), 0.5 + 0.25 * (b - 26));
  k.riser(at(24.5), at(27.5), 0.2);
  k.kick(at(27.5), 1, false);
  k.tapeStop(at(27.5), ['E2', 'B3', 'E4', 'G#4', 'B4', 'G#5'], 0.32);
  k.breath(at(27.5), at(28.25));
}

/** Beats 28–32: a hush for "…and then", SUNDAY. on the flat sixth, and the film leader counting 3-2-1 up the flat seventh into drop two. */
function sunday(k: Kit) {
  k.pad(at(28.25), ['E3', 'B3', 'E4', 'B4'], at(1.25), 0.35, 500, 1600);
  k.swell(at(28.75), at(29.5), 0.12);
  k.impact(at(29.5), 0.9);
  k.crash(at(29.5), 0.7);
  const hits: [number, Chord, string, string | null][] = [
    [29.5, 'F', 'A4', null],
    [30, 'F', 'C5', 'G2'],
    [30.5, 'G', 'D5', 'B2'],
    [31, 'G', 'D5', 'D3'],
  ];
  for (const [b, chord, top, tom] of hits) {
    k.kick(at(b), 0.95, false);
    k.brass(at(b), stack(chord, top), at(0.45), 0.85);
    k.bass(at(b), ROOT[chord], at(0.45), 1, true);
    if (tom) k.tom(at(b), tom, 0.9);
  }
  k.pad(at(29.5), TRIAD.F, at(1), 0.6, 1200, 2400);
  k.pad(at(30.5), TRIAD.G, at(1.25), 0.65, 1200, 4000);
  [31, 31.25, 31.5].forEach((b, i) => k.snare(at(b), 0.5 + 0.15 * i));
  k.riser(at(30), at(31.75), 0.2);
  k.breath(at(31.75), at(32));
  play(k, 29.5, [[0, 'A4', 0.5], [0.5, 'C5', 0.5], [1, 'D5', 0.5], [1.5, 'D5', 0.75]]);
}

/** Beats 32–64: drop two, from the premiere through the facts to GET ON THE LIST! and the final hit on beat 62. */
function dropTwo(k: Kit) {
  k.impact(at(32), 1.1);
  for (const b of [32, 40, 52]) k.crash(at(b), 0.85);
  k.crash(at(36), 0.55);
  DROP_TWO.forEach((bar, i) => groove(k, 32 + 4 * i, bar, true, i === DROP_TWO.length - 1 ? 2 : 4));
  [47.25, 47.5, 47.75, 51.25, 51.5, 51.75].forEach((b, i) => k.snare(at(b), 0.45 + 0.08 * (i % 3)));
  [50, 50.25, 50.5].forEach((b, i) => k.brass(at(b), stack('F#m', 'A4'), at(0.2), 0.6 + 0.1 * i));
  k.impact(at(52), 0.7);
  [56, 56.5, 57].forEach((b, i) => k.brass(at(b), stack('E', 'B4'), at(0.2), 0.55 + 0.1 * i));
  for (let b = 60; b < 62; b += 0.25) k.snare(at(b), 0.35 + 0.3 * (b - 60));
  k.riser(at(60), at(61.9), 0.18);
  k.kick(at(62), 1, false);
  k.impact(at(62), 1.1);
  k.crash(at(62), 0.9);
  k.clap(at(62), 0.9);
  k.brass(at(62), stack('A', 'E5'), at(1.5), 0.9);
  k.pad(at(62), TRIAD.A, at(1.9), 0.7, 2400, 1200);
  k.bass(at(62), 'A1', at(1.8), 1, true);
  k.swell(at(63), at(64), 0.15);
}
