import { BEAT, DURATION, SAMPLE_RATE, b } from '../config';
import { CLOCK_ZERO } from '../draw/clock';
import { CLIPS } from '../scenes/pipeline';
import { Studio, type ChordOptions } from './studio';

type Chord = 'Dm' | 'Bb' | 'F' | 'C';

const VOICING: Record<Chord, number[]> = {
  Dm: [50, 53, 57, 62],
  Bb: [46, 50, 53, 58],
  F: [48, 53, 57, 60],
  C: [48, 52, 55, 60],
};
const ROOT: Record<Chord, number> = { Dm: 38, Bb: 34, F: 41, C: 36 };
const ARP: Record<Chord, number[]> = {
  Dm: [62, 65, 69, 74],
  Bb: [58, 62, 65, 70],
  F: [60, 65, 69, 72],
  C: [60, 64, 67, 72],
};
const ARP_PATTERN = [0, 1, 2, 3, 2, 1, 2, 3];

/** i–VI–III–VII in D minor, lifting through F for the premiere and resolving on the logo. */
const HARMONY: [beat: number, chord: Chord][] = [
  [0, 'Dm'], [12, 'Bb'], [16, 'F'], [20, 'C'], [24, 'Dm'], [28, 'Bb'], [32, 'C'],
  [36, 'F'], [40, 'Bb'], [42, 'C'], [44, 'Dm'], [48, 'Bb'], [52, 'F'], [56, 'C'], [60, 'Dm'],
];

function chordAt(beat: number) {
  let chord: Chord = 'Dm';
  for (const [start, name] of HARMONY) if (beat >= start) chord = name;
  return chord;
}

const at = (beat: number) => b(beat);
const up = (notes: number[]) => notes.map((n) => n + 12);

export async function renderScore(): Promise<AudioBuffer> {
  const ctx = new OfflineAudioContext(2, Math.round(DURATION * SAMPLE_RATE), SAMPLE_RATE);
  arrange(new Studio(ctx, BEAT));
  return ctx.startRendering();
}

function groove(s: Studio, from: number, to: number, o: { kick?: boolean; clap?: boolean } = {}) {
  for (let beat = from; beat < to; beat++) {
    const t = at(beat);
    if (o.kick !== false) s.kick(t, 0.8);
    if (o.clap !== false && beat % 2 === 1) s.clap(t, 0.6);
    for (const k of [0, 1, 3]) s.hat(t + (k * BEAT) / 4, k === 0 ? 0.06 : 0.045);
    s.hat(t + BEAT / 2, 0.07, true);
    s.bass(t + BEAT / 2, ROOT[chordAt(beat)], 0.5, BEAT * 0.42);
  }
}

function arp(s: Studio, from: number, to: number, cutoffFrom: number, cutoffTo: number, vel = 0.13) {
  for (let step = from * 4; step < to * 4; step++) {
    const beat = step / 4;
    const note = ARP[chordAt(beat)][ARP_PATTERN[step % ARP_PATTERN.length]];
    const cutoff = cutoffFrom * Math.pow(cutoffTo / cutoffFrom, (beat - from) / (to - from));
    s.pluck(at(beat), note, vel, cutoff);
  }
}

/** One sustained chord per harmony change inside [from, to). */
function pads(s: Studio, from: number, to: number, o: ChordOptions) {
  const edges = [from, ...HARMONY.map(([start]) => start).filter((x) => x > from && x < to), to];
  for (let i = 0; i < edges.length - 1; i++) {
    s.chord(at(edges[i]), VOICING[chordAt(edges[i])], at(edges[i + 1]) - at(edges[i]), { shape: 'pad', ...o });
  }
}

/** Eighths, then sixteenths, then thirty-seconds, rising in level. */
function snareRoll(s: Studio, from: number, to: number) {
  const len = to - from;
  const beats: number[] = [];
  for (let x = 0; x < len * 0.5; x += 0.5) beats.push(from + x);
  for (let x = len * 0.5; x < len * 0.75; x += 0.25) beats.push(from + x);
  for (let x = len * 0.75; x < len - 0.01; x += 0.125) beats.push(from + x);
  beats.forEach((beat, i) => s.snare(at(beat), 0.1 + (0.38 * i) / beats.length));
}

function stageHit(s: Studio, beat: number) {
  s.chord(at(beat), up(VOICING[chordAt(beat)]), 0.35, { vel: 0.3, cutoff: 5000 });
  s.crash(at(beat), 0.13);
  s.impact(at(beat), 0.3);
}

function arrange(s: Studio) {
  // 0–8 · hook: the feed flicks past, freezes, three word slams, build into the slate
  s.whoosh(0, at(1), { vel: 0.42, from: 350, to: 5200, pan: [-0.4, 0.4], peak: 0.97 });
  s.glitch(at(1) - 0.015, 0.14, 0.2);
  s.impact(at(1), 0.6);
  s.impact(at(2), 0.75);
  s.impact(at(3), 1);
  s.crash(at(3), 0.16);
  s.drone(at(1), at(7.75), 0.16);
  for (let i = 0; i < 14; i++) s.hat(at(4 + i / 4), 0.03 + (0.09 * i) / 14);
  s.riser(at(4), at(7.75), 0.22);
  snareRoll(s, 5, 7.75);
  s.whoosh(at(5.25), 1, { vel: 0.26, from: 200, to: 1800 });
  s.swell(at(7), at(8), 0.32);

  // 8–16 · the slate claps on the drop, then the clock starts
  s.slateClap(at(8));
  s.impact(at(8), 1);
  s.crash(at(8), 0.32);
  groove(s, 8, 16);
  for (const bar of [8, 12]) {
    for (const step of [0, 3, 6, 10, 12]) s.chord(at(bar + step / 4), up(VOICING[chordAt(bar)]), 0.2, { vel: 0.26, cutoff: 4200 });
  }
  s.impact(at(9), 0.35);
  s.beep(at(12));
  s.beep(at(12) + 0.12);
  s.crash(at(12), 0.18);
  for (const beat of [13, 14, 15]) s.tick(at(beat), 0.35);
  s.impact(at(13), 0.3);
  s.impact(at(14), 0.3);
  s.whoosh(at(15.3), 0.6, { vel: 0.22, from: 300, to: 2400 });

  // 16–36 · pipeline: write, see, move, hear, cut
  groove(s, 16, 35);
  s.kick(at(35), 0.95);
  pads(s, 16, 36, { vel: 0.13, cutoff: 2400, attack: 0.04 });
  arp(s, 16, 35.5, 900, 5200);
  for (const beat of [16, 20, 24, 28, 32]) stageHit(s, beat);
  for (let i = 0; i < 13; i++) if (s.random() > 0.15) s.key(at(16 + i / 4) + s.random() * 0.02);
  s.glitch(at(19.2), 0.3, 0.12);
  [74, 77, 79, 81, 84, 81, 79, 77, 74, 77, 79, 81, 84, 86, 89, 91].forEach((m, i) => s.blip(at(20 + i / 4), m, 0.045));
  s.whoosh(at(24), 1.3, { vel: 0.3, from: 250, to: 2600, pan: [-0.6, 0.6] });
  for (const clip of CLIPS) s.snap(at(32 + clip.at / 4), 0.25);
  s.riser(at(32.5), at(35.5), 0.24);
  snareRoll(s, 34, 35.5);
  for (const k of [0, 1, 2]) s.beep(at(CLOCK_ZERO) + k * 0.12, 2637, 0.07, 0.12);

  // 36–44 · premiere: projector, lift, the room cheers
  s.projector(at(36), at(44));
  s.impact(at(36), 0.8);
  s.crash(at(36), 0.25);
  for (let beat = 36; beat < 43; beat++) s.kick(at(beat), 0.85);
  pads(s, 36, 44, { vel: 0.22, attack: 0.25, cutoff: 1400, cutoffTo: 5200, voices: 7, detune: 22, verb: 0.35 });
  groove(s, 40, 43, { kick: false });
  arp(s, 40, 43.5, 3000, 4200, 0.11);
  s.applause(at(39), at(45.5), 70, 0.07);
  s.whistle(at(40.6), 0.6, 0.035, -0.4);
  s.whistle(at(41.9), 0.5, 0.03, 0.5);
  s.swell(at(43), at(44), 0.38);
  [43, 43.25, 43.5].forEach((beat, i) => s.snare(at(beat), 0.2 + i * 0.1));

  // 44–56 · logo slam and the facts
  s.braam(at(44), 1.9, 0.45);
  s.impact(at(44), 1.15);
  s.crash(at(44), 0.4);
  s.glitch(at(44) - 0.01, 0.12, 0.15);
  groove(s, 44, 56);
  pads(s, 44, 56, { vel: 0.13, cutoff: 3000 });
  arp(s, 44, 56, 4200, 4200);
  s.whoosh(at(45), 0.5, { vel: 0.2, from: 500, to: 3000 });
  for (const beat of [46, 48, 50, 52]) {
    s.chord(at(beat), up(VOICING[chordAt(beat)]), 0.16, { vel: 0.24, cutoff: 6000 });
    s.tick(at(beat), 0.3);
  }
  s.impact(at(52), 0.4);
  s.impact(at(54), 0.25);

  // 56–64 · call to action and the final hit
  s.impact(at(56), 0.9);
  s.crash(at(56), 0.32);
  s.chord(at(56), up(VOICING.C), 0.35, { vel: 0.3, cutoff: 5000 });
  s.impact(at(56.5), 0.5);
  s.blip(at(57), 86, 0.07);
  groove(s, 56, 62);
  pads(s, 56, 62, { vel: 0.13, cutoff: 3000 });
  arp(s, 56, 61.5, 4200, 6000);
  s.riser(at(60), at(62), 0.24);
  s.kick(at(62), 1);
  s.braam(at(62), 2, 0.45);
  s.impact(at(62), 1.2);
  s.crash(at(62), 0.42);
  s.chord(at(62), VOICING.Dm, 1.9, { vel: 0.3, cutoff: 4000, voices: 7, detune: 22, verb: 0.4 });
}
