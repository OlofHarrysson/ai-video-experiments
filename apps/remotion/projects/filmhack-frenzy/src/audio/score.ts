import * as Tone from 'tone';
import { rand } from './seed';
import { CLOCK_ZERO_BEAT, DURATION_IN_SECONDS, seconds as at } from '../timing';
import { Kit } from './kit';

export const SAMPLE_RATE = 48000;

type Chord = 'E' | 'B' | 'C#m' | 'A';

/** One chord per bar: I–V–vi–IV in E major, parked on the dominant for the builds. */
const BARS: Chord[] = ['E', 'B', 'E', 'B', 'C#m', 'A', 'B', 'A', 'E', 'B', 'C#m', 'A', 'E', 'B', 'C#m', 'A'];
const chordAt = (beat: number) => BARS[Math.min(BARS.length - 1, Math.floor(beat / 4))];

const STAB: Record<Chord, string[]> = {
  E: ['E4', 'G#4', 'B4', 'E5'],
  B: ['D#4', 'F#4', 'B4', 'D#5'],
  'C#m': ['C#4', 'E4', 'G#4', 'C#5'],
  A: ['C#4', 'E4', 'A4', 'C#5'],
};
const PAD: Record<Chord, string[]> = {
  E: ['E3', 'B3', 'G#4', 'B4'],
  B: ['B2', 'F#3', 'D#4', 'F#4'],
  'C#m': ['C#3', 'G#3', 'E4', 'G#4'],
  A: ['A2', 'E3', 'C#4', 'E4'],
};
const BASS: Record<Chord, string> = { E: 'E2', B: 'B1', 'C#m': 'C#2', A: 'A1' };
const ARP: Record<Chord, string[]> = {
  E: ['E5', 'G#5', 'B5', 'E6'],
  B: ['D#5', 'F#5', 'B5', 'D#6'],
  'C#m': ['C#5', 'E5', 'G#5', 'C#6'],
  A: ['C#5', 'E5', 'A5', 'C#6'],
};
const ARP_PATTERN = [0, 1, 2, 3, 2, 1, 2, 3];

/** The hook: a bouncing chord-tone line on syncopated sixteenths. */
const HOOK: Record<Chord, [sixteenth: number, note: string][]> = {
  E: [[0, 'E5'], [2, 'G#5'], [4, 'B5'], [6, 'G#5'], [7, 'B5'], [9, 'E6'], [11, 'B5'], [13, 'G#5']],
  B: [[0, 'D#5'], [2, 'F#5'], [4, 'B5'], [6, 'F#5'], [7, 'B5'], [9, 'D#6'], [11, 'B5'], [13, 'F#5']],
  'C#m': [[0, 'C#5'], [2, 'E5'], [4, 'G#5'], [6, 'E5'], [7, 'G#5'], [9, 'C#6'], [11, 'G#5'], [13, 'E5']],
  A: [[0, 'C#5'], [2, 'E5'], [4, 'A5'], [6, 'E5'], [7, 'A5'], [9, 'C#6'], [11, 'B5'], [13, 'G#5']],
};

/** Breakbeat bars, in sixteenths. */
const BREAKS = [
  { kick: [0, 6, 10], snare: [4, 12], ghost: [9, 15], bass: [[0, 3], [6, 2], [10, 4]] },
  { kick: [0, 3, 10, 11], snare: [4, 12], ghost: [7, 14], bass: [[0, 2], [3, 3], [10, 1], [11, 3]] },
] as const;

const STAB_RHYTHM = [0, 3, 6, 10, 12];

export async function renderScore(): Promise<AudioBuffer> {
  const buffer = await Tone.Offline(() => {
    const kit = new Kit();
    arrange(kit);
    kit.flush();
  }, DURATION_IN_SECONDS, 2, SAMPLE_RATE);
  return buffer.get()!;
}

function breakBar(k: Kit, bar: number, variant: 0 | 1, density = 1) {
  const b0 = bar * 4;
  const chord = chordAt(b0);
  const s = (n: number) => at(b0 + n / 4);
  const p = BREAKS[variant];
  for (const n of p.kick) k.kick(s(n), 0.9);
  for (const n of p.snare) k.snare(s(n), 0.85);
  for (const n of p.ghost) k.snare(s(n), 0.22);
  for (let n = 0; n < 16; n++) k.hat(s(n), n % 2 === 0 ? 0.55 : 0.3 + 0.2 * density);
  k.openHatAt(s(14), 0.4);
  for (const [n, len] of p.bass) k.bass(s(n), BASS[chord], at(len / 4) * 0.9);
  for (const n of STAB_RHYTHM) k.stab(s(n), STAB[chord], 0.12, 0.65);
}

function fourBar(k: Kit, bar: number, withHook = true, lastBeat = 4) {
  const b0 = bar * 4;
  const chord = chordAt(b0);
  for (let beat = 0; beat < lastBeat; beat++) {
    const t = at(b0 + beat);
    k.kick(t, 0.95);
    if (beat % 2 === 1) k.clap(t, 0.75);
    k.hat(t + at(0.25), 0.3);
    k.openHatAt(t + at(0.5), 0.45);
    k.hat(t + at(0.75), 0.3);
    k.donk(t + at(0.5), BASS[chord], 0.9);
  }
  for (const n of [0, 3, 6, 10, 12]) if (n / 4 < lastBeat) k.stab(at(b0 + n / 4), STAB[chord], 0.12, 0.55);
  if (!withHook) return;
  const hook = HOOK[chord];
  hook.forEach(([n, note], i) => {
    const next = hook[i + 1]?.[0] ?? 16;
    if (n / 4 < lastBeat) k.lead(at(b0 + n / 4), note, Math.min(at((next - n) / 4) * 0.85, 0.18), 0.85);
  });
}

function arpBar(k: Kit, bar: number, cutoffFrom: number, cutoffTo: number) {
  const b0 = bar * 4;
  const tones = ARP[chordAt(b0)];
  for (let n = 0; n < 16; n++) {
    k.arp(at(b0 + n / 4), tones[ARP_PATTERN[n % ARP_PATTERN.length]], cutoffFrom * Math.pow(cutoffTo / cutoffFrom, n / 16), 0.7);
  }
}

function arrange(k: Kit) {
  // Bar 0 · cold open: siren wail, one slam per word
  k.siren(at(0), at(4));
  k.impact(at(0), 1.2);
  k.crash(at(0), 0.6);
  [0, 1, 2, 3].forEach((b, i) => {
    k.kick(at(b), 1);
    k.stab(at(b), STAB.E, 0.22, 0.7 + 0.1 * i);
    if (i > 0) k.impact(at(b), 0.35 + 0.15 * i);
  });
  k.pop(at(3.25), 1.2);
  k.pop(at(3.5), 1.5);

  // Bar 1 · STOP STOP STOP SCROLLING / START CREATING: the build
  [4, 4.5, 5].forEach((b) => {
    k.glitch(at(b), at(0.25));
    k.stab(at(b), STAB.B, 0.1, 0.8);
    k.kick(at(b), 0.9);
  });
  k.zap(at(5.5), 3200, 180);
  k.impact(at(6), 0.6);
  k.kick(at(6), 0.9);
  k.stab(at(6), STAB.B, 0.18, 0.8);
  k.stab(at(6.5), STAB.B, 0.18, 0.8);
  [7, 7.5].forEach((b) => k.kick(at(b), 0.9));
  for (let n = 0; n < 15; n++) k.hat(at(4 + n / 4), 0.2 + (0.5 * n) / 15);
  k.snareRoll(at(6), at(7.75));
  k.riser(at(4), at(7.75), 0.26);

  // Bar 2 · LIGHTS! CAMERA! ACTION! — drop one
  k.impact(at(8), 1.3);
  k.crash(at(8), 0.8);
  k.airHorn(at(8), false);
  k.shutter(at(9));
  k.slate(at(10));
  k.crash(at(10), 0.6);
  k.airHorn(at(10), true);
  k.pop(at(11), 1);
  k.pop(at(11.25), 1.3);
  k.pop(at(11.5), 1.6);
  breakBar(k, 2, 0);

  // Bars 3–5 · the 48-hour montage
  breakBar(k, 3, 1);
  breakBar(k, 4, 0);
  breakBar(k, 5, 1);
  arpBar(k, 3, 900, 1800);
  arpBar(k, 4, 1800, 3200);
  arpBar(k, 5, 3200, 5200);
  [12, 13, 14, 15].forEach((b) => {
    k.typing(at(b), 8, at(0.6));
    k.shutter(at(b + 0.75));
  });
  for (let i = 0; i < 8; i++) k.zap(at(16 + i / 2), 1400 + i * 260, 160 + i * 20);
  for (let i = 0; i < 100; i++) k.pop(at(20) + rand() * at(2.4), 0.8 + rand() * 0.9);
  k.impact(at(22), 0.6);
  k.impact(at(23), 0.6);
  k.airHorn(at(22), false);

  // Bar 6 · chaos build, the clock hits zero
  breakBar(k, 6, 0, 1.4);
  arpBar(k, 6, 5200, 7000);
  k.impact(at(24), 0.7);
  k.airHorn(at(26), false);
  k.glitch(at(26.75), at(0.25));
  k.glitch(at(27.25), at(0.25));
  k.snareRoll(at(26), at(27.5));
  k.riser(at(24.5), at(27.5), 0.28);
  [0, 1, 2].forEach((i) => k.beep(at(CLOCK_ZERO_BEAT) + i * 0.1, 2637, 0.06));

  // Bar 7 · breakdown: power down, "…and then", SUNDAY., film-leader countdown
  k.powerDown(at(28));
  k.typing(at(28.5), 9, at(0.6));
  k.impact(at(29.5), 0.7);
  k.pad(at(29.5), PAD.A, at(2.2), 0.6, true);
  [30, 30.5, 31].forEach((b) => k.beep(at(b), 1000, 0.09));
  k.snareRoll(at(30), at(31.75));
  k.riser(at(30), at(31.75), 0.3);
  k.kick(at(31), 0.8);
  k.kick(at(31.5), 0.85);

  // Bars 8–9 · premiere: drop two, the hook arrives, the room goes wild
  k.impact(at(32), 1.4);
  k.crash(at(32), 0.9);
  k.airHorn(at(32), true);
  fourBar(k, 8);
  fourBar(k, 9);
  k.pad(at(32), PAD.E, at(4), 0.55, true);
  k.pad(at(36), PAD.B, at(4), 0.55, true);
  k.crash(at(36), 0.6);
  k.crowd(at(32), at(40.5), 60);
  k.whistle(at(33.5));
  k.whistle(at(35.25));
  [32.25, 32.5, 36.25, 36.5].forEach((b, i) => k.pop(at(b), 1.4 + (i % 2) * 0.4));

  // Bars 10–12 · facts
  k.impact(at(40), 1.3);
  k.crash(at(40), 0.8);
  k.airHorn(at(40), true);
  k.glitch(at(40), at(0.25));
  fourBar(k, 10);
  fourBar(k, 11);
  fourBar(k, 12);
  k.zap(at(44), 3000, 400);
  k.impact(at(44), 0.4);
  k.boing(at(46));
  k.coin(at(48));
  k.impact(at(48), 0.4);
  k.beep(at(50), 1760, 0.07);
  k.beep(at(50.25), 1760, 0.07);
  k.impact(at(50), 0.5);

  // Bars 13–15 · call to action, final hit on beat 62
  k.impact(at(52), 1.1);
  k.crash(at(52), 0.7);
  k.impact(at(52.5), 0.6);
  fourBar(k, 13);
  fourBar(k, 14);
  fourBar(k, 15, true, 2);
  k.pop(at(54), 1.2);
  k.zap(at(55), 600, 2400);
  [56, 56.25, 56.5, 56.75].forEach((b, i) => k.pop(at(b), 1.2 + i * 0.25));
  k.snareRoll(at(60), at(61.75));
  k.riser(at(60), at(61.75), 0.26);
  k.kick(at(62), 1);
  k.impact(at(62), 1.4);
  k.crash(at(62), 0.9);
  k.airHorn(at(62), true);
  k.stab(at(62), STAB.E, 1.1, 0.9);
  k.pad(at(62), PAD.E, at(1.6), 0.6, true);
  [62.25, 62.5, 62.75, 63].forEach((b, i) => k.pop(at(b), 1.3 + i * 0.3));
}
