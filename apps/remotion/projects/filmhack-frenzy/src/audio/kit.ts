import * as Tone from 'tone';
import { rand } from './seed';
import { seconds } from '../timing';

const SIXTEENTH = seconds(0.25);

function stereoImpulse(duration: number, decay: number) {
  const context = Tone.getContext();
  const rate = context.sampleRate;
  const length = Math.floor(duration * rate);
  const buffer = context.createBuffer(2, length, rate);
  for (let c = 0; c < 2; c++) {
    const data = buffer.getChannelData(c);
    let smooth = 0;
    for (let i = 0; i < length; i++) {
      smooth += 0.45 * (rand() * 2 - 1 - smooth);
      data[i] = i < 0.015 * rate ? 0 : smooth * Math.pow(1 - i / length, decay);
    }
  }
  return buffer;
}

/**
 * Every instrument and effect in the score, created inside the offline context.
 * Buses: drums and sfx go straight to the master; music is ducked by the kick.
 */
export class Kit {
  readonly master = new Tone.Gain(0.8);
  readonly drums = new Tone.Gain(1);
  readonly music = new Tone.Gain(1);
  readonly sfx = new Tone.Gain(1);
  private readonly duck = new Tone.Gain(1);
  private readonly verb = new Tone.Gain(1);
  private readonly echo = new Tone.Gain(1);

  private readonly kickBody = new Tone.MembraneSynth({
    pitchDecay: 0.045,
    octaves: 4.5,
    envelope: { attack: 0.001, decay: 0.32, sustain: 0, release: 0.05 },
  });
  private readonly kickClick = new Tone.NoiseSynth({ envelope: { attack: 0.0005, decay: 0.015, sustain: 0 }, volume: -16 });
  private readonly snareNoise = new Tone.NoiseSynth({ envelope: { attack: 0.001, decay: 0.15, sustain: 0 }, volume: -5 });
  private readonly snareBody = new Tone.MembraneSynth({ pitchDecay: 0.02, octaves: 1.5, envelope: { attack: 0.001, decay: 0.09, sustain: 0 }, volume: -9 });
  private readonly clapNoise = new Tone.NoiseSynth({ envelope: { attack: 0.001, decay: 0.14, sustain: 0 }, volume: -4 });
  private readonly closedHat = new Tone.MetalSynth({
    envelope: { attack: 0.001, decay: 0.045, release: 0.01 },
    harmonicity: 5.1,
    modulationIndex: 32,
    resonance: 5200,
    octaves: 1.5,
    volume: -15,
  });
  private readonly openHat = new Tone.MetalSynth({
    envelope: { attack: 0.001, decay: 0.22, release: 0.05 },
    harmonicity: 5.1,
    modulationIndex: 32,
    resonance: 5200,
    octaves: 1.5,
    volume: -19,
  });
  private readonly crashMetal = new Tone.MetalSynth({
    envelope: { attack: 0.001, decay: 1.1, release: 0.3 },
    harmonicity: 5.1,
    modulationIndex: 40,
    resonance: 7000,
    octaves: 2,
    volume: -19,
  });
  private readonly crashNoise = new Tone.NoiseSynth({ envelope: { attack: 0.001, decay: 1.1, sustain: 0 }, volume: -15 });

  private readonly bassSynth = new Tone.MonoSynth({
    oscillator: { type: 'sawtooth' },
    filter: { type: 'lowpass', Q: 3, rolloff: -24 },
    envelope: { attack: 0.003, decay: 0.2, sustain: 0.45, release: 0.08 },
    filterEnvelope: { attack: 0.001, decay: 0.16, sustain: 0.3, release: 0.1, baseFrequency: 180, octaves: 3.4 },
    volume: -9,
  });
  private readonly donkSynth = new Tone.MembraneSynth({
    pitchDecay: 0.03,
    octaves: 2.2,
    envelope: { attack: 0.001, decay: 0.17, sustain: 0, release: 0.02 },
    volume: -7,
  });
  private readonly stabSynth = new Tone.PolySynth(Tone.Synth, {
    oscillator: { type: 'fatsawtooth', count: 3, spread: 30 },
    envelope: { attack: 0.003, decay: 0.18, sustain: 0.06, release: 0.12 },
    volume: -13,
  });
  private readonly padSynth = new Tone.PolySynth(Tone.Synth, {
    oscillator: { type: 'fatsawtooth', count: 3, spread: 40 },
    envelope: { attack: 0.35, decay: 0.2, sustain: 0.9, release: 0.5 },
    volume: -18,
  });
  private readonly padFilter = new Tone.Filter(900, 'lowpass');
  private readonly leadSynth = new Tone.Synth({
    oscillator: { type: 'square' },
    envelope: { attack: 0.002, decay: 0.09, sustain: 0.35, release: 0.05 },
    volume: -12,
  });
  private readonly sparkleSynth = new Tone.Synth({
    oscillator: { type: 'triangle' },
    envelope: { attack: 0.002, decay: 0.08, sustain: 0.2, release: 0.05 },
    volume: -16,
  });
  private readonly arpSynth = new Tone.Synth({
    oscillator: { type: 'pulse', width: 0.25 },
    envelope: { attack: 0.001, decay: 0.07, sustain: 0, release: 0.03 },
    volume: -17,
  });
  private readonly arpFilter = new Tone.Filter(2400, 'lowpass');

  private readonly sirenSynth = new Tone.Synth({
    oscillator: { type: 'sawtooth' },
    envelope: { attack: 0.08, decay: 0, sustain: 1, release: 0.25 },
    volume: -22,
  });
  private readonly hornVoices = [-12, 0].map(
    () =>
      new Tone.Synth({
        oscillator: { type: 'fatsawtooth', count: 3, spread: 22 },
        envelope: { attack: 0.008, decay: 0.05, sustain: 0.9, release: 0.07 },
        volume: -14,
      }),
  );
  private readonly zapSynth = new Tone.Synth({
    oscillator: { type: 'square' },
    envelope: { attack: 0.001, decay: 0.13, sustain: 0, release: 0.02 },
    volume: -22,
  });
  private readonly popSynth = new Tone.Synth({
    oscillator: { type: 'sine' },
    envelope: { attack: 0.001, decay: 0.06, sustain: 0, release: 0.01 },
    volume: -20,
  });
  private readonly chimeSynth = new Tone.Synth({
    oscillator: { type: 'square' },
    envelope: { attack: 0.001, decay: 0.3, sustain: 0, release: 0.05 },
    volume: -21,
  });
  private readonly boingSynth = new Tone.Synth({
    oscillator: { type: 'sine' },
    envelope: { attack: 0.001, decay: 0.35, sustain: 0, release: 0.05 },
    volume: -14,
  });
  private readonly beepSynth = new Tone.Synth({
    oscillator: { type: 'sine' },
    envelope: { attack: 0.002, decay: 0, sustain: 1, release: 0.01 },
    volume: -16,
  });
  private readonly clickNoise = new Tone.NoiseSynth({ envelope: { attack: 0.0005, decay: 0.018, sustain: 0 }, volume: -20 });
  private readonly clickFilter = new Tone.Filter({ type: 'bandpass', frequency: 3200, Q: 2 });
  private readonly thudNoise = new Tone.NoiseSynth({ envelope: { attack: 0.0005, decay: 0.05, sustain: 0 }, volume: -10 });
  private readonly woodBody = new Tone.MembraneSynth({ pitchDecay: 0.01, octaves: 1.2, envelope: { attack: 0.001, decay: 0.07, sustain: 0 }, volume: -8 });
  private readonly impactBody = new Tone.MembraneSynth({
    pitchDecay: 0.18,
    octaves: 3.5,
    envelope: { attack: 0.001, decay: 0.8, sustain: 0, release: 0.1 },
    volume: -10,
  });
  private readonly impactNoise = new Tone.NoiseSynth({ envelope: { attack: 0.001, decay: 0.45, sustain: 0 }, volume: -8 });
  private readonly glitchNoise = new Tone.NoiseSynth({ envelope: { attack: 0.0005, decay: 0.022, sustain: 0 }, volume: -18 });
  private readonly sweepSynth = new Tone.Synth({
    oscillator: { type: 'sawtooth' },
    envelope: { attack: 0.01, decay: 0, sustain: 1, release: 0.05 },
    volume: -18,
  });
  private readonly sweepFilter = new Tone.Filter(600, 'lowpass');
  private readonly clapCrowd = new Tone.NoiseSynth({ envelope: { attack: 0.0008, decay: 0.014, sustain: 0 }, volume: -22 });
  private readonly crowdFilter = new Tone.Filter({ type: 'bandpass', frequency: 1500, Q: 1.5 });
  private readonly crowdPan = new Tone.Panner(0);
  private readonly whistleSynth = new Tone.Synth({
    oscillator: { type: 'sine' },
    envelope: { attack: 0.04, decay: 0, sustain: 1, release: 0.12 },
    volume: -26,
  });

  constructor() {
    this.stabSynth.maxPolyphony = 64;
    this.padSynth.maxPolyphony = 32;
    // Phones cannot play the deep sub, so it only costs headroom: cut it steeply.
    const low = new Tone.Filter({ type: 'highpass', frequency: 38, rolloff: -24 });
    const lowShelf = new Tone.Filter({ type: 'lowshelf', frequency: 120, gain: -6 });
    const presence = new Tone.Filter({ type: 'peaking', frequency: 3200, Q: 0.8, gain: 3 });
    const glue = new Tone.Compressor({ threshold: -16, ratio: 3, attack: 0.01, release: 0.2, knee: 8 });
    const limiter = new Tone.Limiter(-2);
    this.master.chain(low, lowShelf, presence, glue, limiter, Tone.getDestination());
    this.drums.connect(this.master);
    this.sfx.connect(this.master);
    this.music.chain(new Tone.StereoWidener(0.7), this.duck);
    this.duck.connect(this.master);

    const reverb = new Tone.Convolver(stereoImpulse(2.2, 3.4));
    this.verb.connect(reverb);
    reverb.connect(new Tone.Gain(0.6).connect(this.master));

    const delay = new Tone.PingPongDelay({ delayTime: seconds(0.75), feedback: 0.34, wet: 1 });
    const delayTone = new Tone.Filter(3400, 'lowpass');
    this.echo.chain(delay, delayTone, new Tone.Gain(0.55).connect(this.music));

    this.kickBody.chain(new Tone.Distortion({ distortion: 0.3, oversample: '2x', wet: 0.6 }), this.drums);
    this.kickClick.chain(new Tone.Filter(3000, 'highpass'), this.drums);
    this.snareNoise.chain(new Tone.Filter({ type: 'bandpass', frequency: 2600, Q: 0.6 }), this.drums);
    this.snareBody.connect(this.drums);
    const clapFilter = new Tone.Filter({ type: 'bandpass', frequency: 1700, Q: 0.9 });
    this.clapNoise.chain(clapFilter, this.drums);
    this.send(clapFilter, this.verb, 0.25);
    this.closedHat.chain(new Tone.Filter(7000, 'highpass'), this.drums);
    this.openHat.chain(new Tone.Filter(7000, 'highpass'), this.drums);
    const crashFilter = new Tone.Filter(5000, 'highpass');
    this.crashNoise.chain(crashFilter, this.drums);
    this.crashMetal.connect(this.drums);
    this.send(crashFilter, this.verb, 0.3);

    this.bassSynth.chain(new Tone.Distortion({ distortion: 0.25, wet: 0.5 }), this.music);
    this.donkSynth.chain(new Tone.Distortion({ distortion: 0.55, wet: 0.7 }), new Tone.Filter(2600, 'lowpass'), this.music);
    const stabFilter = new Tone.Filter(6500, 'lowpass');
    this.stabSynth.chain(stabFilter, this.music);
    this.send(stabFilter, this.verb, 0.15);
    this.padSynth.chain(this.padFilter, this.music);
    this.send(this.padFilter, this.verb, 0.35);
    const leadFilter = new Tone.Filter(8000, 'lowpass');
    this.leadSynth.chain(leadFilter, this.music);
    this.sparkleSynth.connect(leadFilter);
    this.send(leadFilter, this.echo, 0.3);
    this.send(leadFilter, this.verb, 0.1);
    this.arpSynth.chain(this.arpFilter, this.music);
    this.send(this.arpFilter, this.echo, 0.35);

    this.sirenSynth.chain(new Tone.Filter({ type: 'bandpass', frequency: 1300, Q: 0.9 }), new Tone.Distortion(0.25), this.sfx);
    const hornFilter = new Tone.Filter({ type: 'bandpass', frequency: 1050, Q: 0.7 });
    for (const voice of this.hornVoices) voice.chain(new Tone.Distortion({ distortion: 0.6, wet: 0.8 }), hornFilter);
    hornFilter.connect(this.sfx);
    this.send(hornFilter, this.verb, 0.3);
    this.zapSynth.chain(new Tone.Filter(6000, 'lowpass'), this.sfx);
    this.popSynth.connect(this.sfx);
    this.chimeSynth.chain(new Tone.Filter(7000, 'lowpass'), this.sfx);
    this.send(this.chimeSynth, this.echo, 0.25);
    this.boingSynth.connect(this.sfx);
    this.beepSynth.connect(this.sfx);
    this.clickNoise.chain(this.clickFilter, this.sfx);
    const thudFilter = new Tone.Filter(1400, 'highpass');
    this.thudNoise.chain(thudFilter, this.sfx);
    this.send(thudFilter, this.verb, 0.3);
    this.woodBody.connect(this.sfx);
    this.impactBody.chain(new Tone.Distortion({ distortion: 0.35, wet: 0.5 }), this.sfx);
    const impactFilter = new Tone.Filter(6000, 'lowpass');
    this.impactNoise.chain(impactFilter, this.sfx);
    this.send(impactFilter, this.verb, 0.45);
    this.glitchNoise.chain(new Tone.WaveShaper((x) => Math.round(x * 3) / 3, 1024), new Tone.Filter({ type: 'bandpass', frequency: 2200, Q: 0.8 }), this.sfx);
    this.sweepSynth.chain(this.sweepFilter, new Tone.Distortion(0.3), this.sfx);
    this.clapCrowd.chain(this.crowdFilter, this.crowdPan, this.sfx);
    this.whistleSynth.chain(new Tone.Vibrato({ frequency: 6.5, depth: 0.12 }), this.sfx);
    this.send(this.whistleSynth, this.verb, 0.35);
  }

  private send(from: Tone.ToneAudioNode, to: Tone.ToneAudioNode, amount: number) {
    from.connect(new Tone.Gain(amount).connect(to));
  }

  // Tone.js sources only accept triggers in time order, so every trigger is queued
  // and the arrangement can be written in whatever order reads best.
  private readonly queue: { t: number; seq: number; voice: string; run: () => void }[] = [];

  /** Queue a trigger on a monophonic `voice`; a voice sounds at most once per instant. */
  private at(t: number, voice: string, run: () => void) {
    this.queue.push({ t, seq: this.queue.length, voice, run });
  }

  /** Schedule everything that was queued, earliest first. */
  flush() {
    const last = new Map<string, number>();
    for (const event of this.queue.sort((a, b) => a.t - b.t || a.seq - b.seq)) {
      const previous = last.get(event.voice);
      if (event.voice !== 'poly' && previous !== undefined && event.t - previous < 1e-4) continue;
      last.set(event.voice, event.t);
      event.run();
    }
    this.queue.length = 0;
  }

  // ── drums ────────────────────────────────────────────────────────────────
  kick(t: number, vel = 0.9) {
    this.at(t, 'kick', () => {
      this.kickBody.triggerAttackRelease('A1', 0.2, t, vel);
      this.kickClick.triggerAttackRelease(0.015, t, vel);
      this.duck.gain.setTargetAtTime(0.45, t, 0.003);
      this.duck.gain.setTargetAtTime(1, t + 0.03, 0.06);
    });
  }

  snare(t: number, vel = 0.8) {
    this.at(t, 'snare', () => {
      this.snareNoise.triggerAttackRelease(0.14, t, vel);
      this.snareBody.triggerAttackRelease('G3', 0.08, t, vel);
    });
  }

  clap(t: number, vel = 0.8) {
    for (const [dt, v] of [[0, 1], [0.011, 0.8], [0.022, 0.9]]) {
      this.at(t + dt, 'clap', () => this.clapNoise.triggerAttackRelease(0.12, t + dt, vel * v));
    }
  }

  hat(t: number, vel = 0.5) {
    this.at(t, 'hat', () => this.closedHat.triggerAttackRelease(320, 0.04, t, vel));
  }

  openHatAt(t: number, vel = 0.5) {
    this.at(t, 'openHat', () => this.openHat.triggerAttackRelease(320, 0.2, t, vel));
  }

  crash(t: number, vel = 0.7) {
    this.at(t, 'crash', () => {
      this.crashMetal.triggerAttackRelease(420, 1, t, vel);
      this.crashNoise.triggerAttackRelease(1, t, vel);
    });
  }

  /** Eighths, sixteenths, then thirty-seconds, rising. */
  snareRoll(t0: number, t1: number) {
    const span = t1 - t0;
    const hits: number[] = [];
    for (let x = 0; x < span * 0.5 - 1e-6; x += SIXTEENTH * 2) hits.push(t0 + x);
    for (let x = span * 0.5; x < span * 0.75 - 1e-6; x += SIXTEENTH) hits.push(t0 + x);
    for (let x = span * 0.75; x < span - 1e-6; x += SIXTEENTH / 2) hits.push(t0 + x);
    hits.forEach((t, i) => this.snare(t, 0.2 + (0.7 * i) / hits.length));
  }

  // ── tonal ────────────────────────────────────────────────────────────────
  bass(t: number, note: string, dur: number, vel = 0.9) {
    this.at(t, 'bass', () => this.bassSynth.triggerAttackRelease(note, dur, t, vel));
  }

  donk(t: number, note: string, vel = 0.9) {
    this.at(t, 'donk', () => this.donkSynth.triggerAttackRelease(note, 0.15, t, vel));
  }

  stab(t: number, notes: string[], dur = 0.16, vel = 0.8) {
    this.at(t, 'poly', () => this.stabSynth.triggerAttackRelease(notes, dur, t, vel));
  }

  pad(t: number, notes: string[], dur: number, vel = 0.7, open = false) {
    this.at(t, 'poly', () => {
      if (open) {
        this.padFilter.frequency.setValueAtTime(700, t);
        this.padFilter.frequency.exponentialRampToValueAtTime(5200, t + dur);
      } else {
        this.padFilter.frequency.setValueAtTime(900, t);
      }
      this.padSynth.triggerAttackRelease(notes, dur, t, vel);
    });
  }

  lead(t: number, note: string, dur: number, vel = 0.8) {
    this.at(t, 'lead', () => {
      this.leadSynth.triggerAttackRelease(note, dur, t, vel);
      this.sparkleSynth.triggerAttackRelease(Tone.Frequency(note).transpose(12).toFrequency(), dur, t, vel * 0.7);
    });
  }

  arp(t: number, note: string, cutoff: number, vel = 0.7) {
    this.at(t, 'arp', () => {
      this.arpFilter.frequency.setValueAtTime(cutoff, t);
      this.arpSynth.triggerAttackRelease(note, 0.07, t, vel);
    });
  }

  // ── effects ──────────────────────────────────────────────────────────────
  /** Two-tone police-style wail between t0 and t1. */
  siren(t0: number, t1: number) {
    this.at(t0, 'siren', () => {
      const cycle = seconds(1);
      this.sirenSynth.triggerAttack(700, t0);
      for (let t = t0, up = true; t < t1; t += cycle / 2, up = !up) {
        this.sirenSynth.frequency.linearRampToValueAtTime(up ? 1350 : 700, Math.min(t1, t + cycle / 2));
      }
      this.sirenSynth.triggerRelease(t1);
    });
  }

  /** Stadium air horn: BWA-BWA-BWAAAA with a scooped attack on every blast. */
  airHorn(t: number, long = true) {
    const blasts: [number, number][] = long ? [[0, 0.1], [0.15, 0.1], [0.3, 0.55]] : [[0, 0.1], [0.15, 0.22]];
    for (const [dt, len] of blasts) {
      this.at(t + dt, 'horn', () =>
        this.hornVoices.forEach((voice, i) => {
          voice.triggerAttackRelease(i === 0 ? 'A#3' : 'A#4', len, t + dt, 0.9);
          voice.detune.setValueAtTime(-280, t + dt);
          voice.detune.linearRampToValueAtTime(0, t + dt + 0.05);
        }),
      );
    }
  }

  zap(t: number, from = 2400, to = 140) {
    this.at(t, 'zap', () => {
      this.zapSynth.triggerAttackRelease(from, 0.13, t, 0.8);
      this.zapSynth.frequency.exponentialRampToValueAtTime(to, t + 0.12);
    });
  }

  pop(t: number, pitch = 1) {
    this.at(t, 'pop', () => {
      this.popSynth.triggerAttackRelease(320 * pitch, 0.05, t, 0.8);
      this.popSynth.frequency.exponentialRampToValueAtTime(980 * pitch, t + 0.04);
    });
  }

  /** Two-note coin chime. */
  coin(t: number) {
    this.at(t, 'chime', () => this.chimeSynth.triggerAttackRelease('B5', 0.07, t, 0.8));
    this.at(t + 0.075, 'chime', () => this.chimeSynth.triggerAttackRelease('E6', 0.35, t + 0.075, 0.8));
  }

  /** Cartoon spring for the bouncing map pin. */
  boing(t: number) {
    this.at(t, 'boing', () => {
      this.boingSynth.triggerAttackRelease(180, 0.35, t, 0.9);
      const steps = 10;
      for (let i = 1; i <= steps; i++) {
        const x = i / steps;
        this.boingSynth.frequency.linearRampToValueAtTime(180 + 260 * Math.exp(-3 * x) * Math.abs(Math.sin(x * 11)), t + x * 0.35);
      }
    });
  }

  beep(t: number, freq = 1000, dur = 0.08) {
    this.at(t, 'beep', () => this.beepSynth.triggerAttackRelease(freq, dur, t, 0.9));
  }

  typing(t: number, keys: number, span: number) {
    for (let i = 0; i < keys; i++) {
      const key = t + (i * span) / keys + rand() * 0.006;
      const tone = 2600 + rand() * 1800;
      const vel = 0.7 + rand() * 0.3;
      this.at(key, 'click', () => {
        this.clickFilter.frequency.setValueAtTime(tone, key);
        this.clickNoise.triggerAttackRelease(0.018, key, vel);
      });
    }
  }

  /** Clapperboard snap. */
  slate(t: number) {
    this.at(t, 'thud', () => {
      this.thudNoise.triggerAttackRelease(0.05, t, 1);
      this.woodBody.triggerAttackRelease('C5', 0.06, t, 1);
    });
  }

  shutter(t: number) {
    this.at(t, 'thud', () => this.thudNoise.triggerAttackRelease(0.03, t, 0.6));
    this.at(t + 0.06, 'thud', () => this.thudNoise.triggerAttackRelease(0.03, t + 0.06, 0.45));
  }

  impact(t: number, size = 1) {
    this.at(t, 'impact', () => {
      this.impactBody.triggerAttackRelease('A1', 0.7, t, Math.min(1, 0.6 * size));
      this.impactNoise.triggerAttackRelease(0.4, t, Math.min(1, 0.7 * size));
    });
  }

  glitch(t: number, span = seconds(0.5)) {
    for (let x = 0; x < span; x += SIXTEENTH / 2) {
      const vel = 0.5 + rand() * 0.5;
      this.at(t + x, 'glitch', () => this.glitchNoise.triggerAttackRelease(0.02, t + x, vel));
    }
  }

  riser(t0: number, t1: number, level = 0.3) {
    const filter = new Tone.Filter({ type: 'bandpass', frequency: 400, Q: 2.2 });
    const gain = new Tone.Gain(0);
    const noise = new Tone.Noise('white').chain(filter, gain, this.sfx);
    filter.frequency.setValueAtTime(400, t0);
    filter.frequency.exponentialRampToValueAtTime(7000, t1);
    gain.gain.setValueAtTime(0.0001, t0);
    gain.gain.exponentialRampToValueAtTime(level, t1 - 0.01);
    gain.gain.linearRampToValueAtTime(0, t1 + 0.01);
    noise.start(t0).stop(t1 + 0.02);
    this.at(t0, 'sweep', () => {
      this.sweepFilter.frequency.setValueAtTime(500, t0);
      this.sweepFilter.frequency.exponentialRampToValueAtTime(5000, t1);
      this.sweepSynth.triggerAttack('B2', t0, 0.6);
      this.sweepSynth.frequency.exponentialRampToValueAtTime(Tone.Frequency('B4').toFrequency(), t1);
      this.sweepSynth.triggerRelease(t1);
    });
  }

  /** Everything winds down like a switched-off tape machine. */
  powerDown(t: number) {
    this.at(t, 'sweep', () => {
      this.sweepFilter.frequency.setValueAtTime(4000, t);
      this.sweepFilter.frequency.exponentialRampToValueAtTime(120, t + 0.55);
      this.sweepSynth.triggerAttack(900, t, 0.8);
      this.sweepSynth.frequency.exponentialRampToValueAtTime(32, t + 0.55);
      this.sweepSynth.triggerRelease(t + 0.55);
    });
  }

  /** Granular applause with a crowd roar and whistles. */
  crowd(t0: number, t1: number, peakRate = 60) {
    const span = t1 - t0;
    const shape = (x: number) => (x < 0.15 ? x / 0.15 : x > 0.65 ? Math.max(0, 1 - (x - 0.65) / 0.35) : 1);
    for (let t = t0; ; ) {
      const level = shape((t - t0) / span);
      t += -Math.log(1 - rand()) / Math.max(6, peakRate * level);
      if (t >= t1) break;
      const clap = t;
      const tone = 900 + rand() * 2000;
      const pan = rand() * 1.7 - 0.85;
      const vel = (0.3 + 0.7 * rand()) * (0.3 + 0.7 * level);
      this.at(clap, 'crowdClap', () => {
        this.crowdFilter.frequency.setValueAtTime(tone, clap);
        this.crowdPan.pan.setValueAtTime(pan, clap);
        this.clapCrowd.triggerAttackRelease(0.014, clap, vel);
      });
    }
    const roarGain = new Tone.Gain(0);
    const roar = new Tone.Noise('pink').chain(new Tone.Filter({ type: 'bandpass', frequency: 700, Q: 0.6 }), roarGain, this.sfx);
    roarGain.gain.setValueAtTime(0, t0);
    roarGain.gain.linearRampToValueAtTime(0.09, t0 + span * 0.15);
    roarGain.gain.setValueAtTime(0.09, t0 + span * 0.65);
    roarGain.gain.linearRampToValueAtTime(0, t1);
    roar.start(t0).stop(t1);
  }

  whistle(t: number) {
    this.at(t, 'whistle', () => {
      this.whistleSynth.triggerAttack(1500, t, 0.9);
      this.whistleSynth.frequency.linearRampToValueAtTime(2500, t + 0.16);
      this.whistleSynth.frequency.linearRampToValueAtTime(2250, t + 0.5);
      this.whistleSynth.triggerRelease(t + 0.5);
    });
  }
}
