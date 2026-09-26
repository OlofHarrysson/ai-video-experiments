import * as Tone from 'tone';
import { rand } from './seed';
import { seconds } from '../timing';

/** A stereo noise impulse for the convolution reverbs, darkened by a one-pole lowpass. */
function impulse(duration: number, shape: (x: number) => number) {
  const context = Tone.getContext();
  const rate = context.sampleRate;
  const length = Math.floor(duration * rate);
  const buffer = context.createBuffer(2, length, rate);
  for (let c = 0; c < 2; c++) {
    const data = buffer.getChannelData(c);
    let smooth = 0;
    for (let i = 0; i < length; i++) {
      smooth += 0.4 * (rand() * 2 - 1 - smooth);
      data[i] = i < 0.012 * rate ? 0 : smooth * shape(i / length);
    }
  }
  return buffer;
}

/**
 * Every instrument in the score, created inside the offline context.
 * The bed (bass, pad, plucks) is pumped by the kick; the tune (lead, bell, brass) never is, so the melody stays on top.
 */
export class Kit {
  readonly master = new Tone.Gain(0.8);
  readonly drums = new Tone.Gain(1);
  readonly bed = new Tone.Gain(1);
  readonly tune = new Tone.Gain(1);
  readonly fx = new Tone.Gain(1);
  private readonly pumped = new Tone.Gain(1);
  private readonly hall = new Tone.Gain(1);
  private readonly room = new Tone.Gain(1);
  private readonly echo = new Tone.Gain(1);

  private readonly kickBody = new Tone.MembraneSynth({
    pitchDecay: 0.04,
    octaves: 5,
    envelope: { attack: 0.001, decay: 0.24, sustain: 0, release: 0.02 },
    volume: -7,
  });
  private readonly kickClick = new Tone.NoiseSynth({ envelope: { attack: 0.0005, decay: 0.01, sustain: 0 }, volume: -24 });
  private readonly snareNoise = new Tone.NoiseSynth({ envelope: { attack: 0.001, decay: 0.16, sustain: 0 }, volume: -7 });
  private readonly snareBody = new Tone.MembraneSynth({ pitchDecay: 0.012, octaves: 1.6, envelope: { attack: 0.001, decay: 0.11, sustain: 0 }, volume: -14 });
  private readonly clapNoise = new Tone.NoiseSynth({ envelope: { attack: 0.001, decay: 0.11, sustain: 0 }, volume: -8 });
  private readonly hatNoise = new Tone.NoiseSynth({ envelope: { attack: 0.001, decay: 0.03, sustain: 0 }, volume: -11 });
  private readonly openHatNoise = new Tone.NoiseSynth({ envelope: { attack: 0.002, decay: 0.18, sustain: 0 }, volume: -14 });
  private readonly shakerNoise = new Tone.NoiseSynth({ envelope: { attack: 0.008, decay: 0.04, sustain: 0 }, volume: -21 });
  private readonly crashNoise = new Tone.NoiseSynth({ envelope: { attack: 0.001, decay: 1.5, sustain: 0 }, volume: -15 });
  private readonly tomBody = new Tone.MembraneSynth({ pitchDecay: 0.05, octaves: 2, envelope: { attack: 0.001, decay: 0.42, sustain: 0 }, volume: -7 });

  private readonly bassSaw = new Tone.MonoSynth({
    oscillator: { type: 'sawtooth' },
    filter: { type: 'lowpass', Q: 1.4, rolloff: -24 },
    envelope: { attack: 0.003, decay: 0.2, sustain: 0.5, release: 0.05 },
    filterEnvelope: { attack: 0.002, decay: 0.15, sustain: 0.28, release: 0.08, baseFrequency: 140, octaves: 3.3 },
    volume: -16,
  });
  private readonly bassSub = new Tone.Synth({ oscillator: { type: 'sine' }, envelope: { attack: 0.005, decay: 0.12, sustain: 0.8, release: 0.05 }, volume: -21 });
  private readonly padSynth = new Tone.PolySynth(Tone.Synth, {
    oscillator: { type: 'fatsawtooth', count: 5, spread: 30 },
    envelope: { attack: 0.03, decay: 0.6, sustain: 0.7, release: 0.45 },
    volume: -21,
  });
  private readonly padFilter = new Tone.Filter({ type: 'lowpass', frequency: 4200, Q: 0.5 });
  private readonly pluckSynth = new Tone.PolySynth(Tone.MonoSynth, {
    oscillator: { type: 'fatsawtooth', count: 3, spread: 16 },
    filter: { type: 'lowpass', Q: 0.9, rolloff: -24 },
    envelope: { attack: 0.002, decay: 0.18, sustain: 0, release: 0.1 },
    filterEnvelope: { attack: 0.001, decay: 0.14, sustain: 0.08, release: 0.1, baseFrequency: 800, octaves: 3.2 },
    volume: -17,
  });
  private readonly brassSynth = new Tone.PolySynth(Tone.MonoSynth, {
    oscillator: { type: 'fatsawtooth', count: 3, spread: 20 },
    filter: { type: 'lowpass', Q: 1, rolloff: -24 },
    envelope: { attack: 0.01, decay: 0.3, sustain: 0.55, release: 0.25 },
    filterEnvelope: { attack: 0.02, decay: 0.32, sustain: 0.32, release: 0.25, baseFrequency: 480, octaves: 3.3 },
    volume: -17,
  });
  private readonly leadSynth = new Tone.MonoSynth({
    portamento: 0.02,
    oscillator: { type: 'fatsawtooth', count: 3, spread: 12 },
    filter: { type: 'lowpass', Q: 1.2, rolloff: -24 },
    envelope: { attack: 0.008, decay: 0.3, sustain: 0.78, release: 0.16 },
    filterEnvelope: { attack: 0.025, decay: 0.3, sustain: 0.5, release: 0.2, baseFrequency: 1350, octaves: 2.3 },
    volume: -11.5,
  });
  private readonly bellSynth = new Tone.PolySynth(Tone.FMSynth, {
    harmonicity: 3,
    modulationIndex: 1.8,
    oscillator: { type: 'sine' },
    modulation: { type: 'sine' },
    envelope: { attack: 0.002, decay: 0.7, sustain: 0, release: 0.5 },
    modulationEnvelope: { attack: 0.002, decay: 0.18, sustain: 0, release: 0.2 },
    volume: -21,
  });

  private readonly boomBody = new Tone.MembraneSynth({
    pitchDecay: 0.2,
    octaves: 3,
    envelope: { attack: 0.001, decay: 1, sustain: 0, release: 0.1 },
    volume: -13,
  });
  private readonly boomNoise = new Tone.NoiseSynth({ noise: { type: 'pink' }, envelope: { attack: 0.001, decay: 0.6, sustain: 0 }, volume: -19 });

  constructor() {
    this.padSynth.maxPolyphony = 24;
    this.pluckSynth.maxPolyphony = 24;
    this.brassSynth.maxPolyphony = 32;
    this.bellSynth.maxPolyphony = 16;

    const low = new Tone.Filter({ type: 'highpass', frequency: 32, rolloff: -24 });
    const weight = new Tone.Filter({ type: 'lowshelf', frequency: 110, gain: -2 });
    const mud = new Tone.Filter({ type: 'peaking', frequency: 300, Q: 0.9, gain: -1.5 });
    const glue = new Tone.Compressor({ threshold: -14, ratio: 2.5, attack: 0.012, release: 0.18, knee: 6 });
    this.master.chain(low, weight, mud, glue, new Tone.Limiter(-1), Tone.getDestination());
    this.drums.connect(this.master);
    this.tune.connect(this.master);
    this.fx.connect(this.master);
    this.bed.chain(this.pumped, this.master);

    this.hall.chain(new Tone.Convolver(impulse(2.4, (x) => Math.pow(1 - x, 3.4))), new Tone.Gain(0.55), this.master);
    this.room.chain(new Tone.Convolver(impulse(0.32, (x) => (x < 0.8 ? 1 : (1 - x) * 5))), new Tone.Gain(0.35), this.drums);
    this.echo.chain(
      new Tone.PingPongDelay({ delayTime: seconds(0.75), feedback: 0.28, wet: 1 }),
      new Tone.Filter(3200, 'lowpass'),
      new Tone.Filter(400, 'highpass'),
      new Tone.Gain(0.5),
      this.tune,
    );

    this.kickBody.chain(new Tone.Distortion({ distortion: 0.18, wet: 0.25 }), this.drums);
    this.kickClick.chain(new Tone.Filter(2500, 'highpass'), this.drums);
    const snareTone = new Tone.Filter({ type: 'bandpass', frequency: 2200, Q: 0.45 });
    this.snareNoise.chain(snareTone, this.drums);
    this.snareBody.connect(this.drums);
    this.send(snareTone, this.room, 0.8);
    this.send(snareTone, this.hall, 0.12);
    const clapTone = new Tone.Filter({ type: 'bandpass', frequency: 1300, Q: 1.1 });
    this.clapNoise.chain(clapTone, this.drums);
    this.send(clapTone, this.room, 0.5);
    this.send(clapTone, this.hall, 0.2);
    this.hatNoise.chain(new Tone.Filter(7000, 'highpass'), new Tone.Panner(0.2), this.drums);
    this.openHatNoise.chain(new Tone.Filter(7000, 'highpass'), new Tone.Filter(13000, 'lowpass'), new Tone.Panner(0.25), this.drums);
    this.shakerNoise.chain(new Tone.Filter({ type: 'bandpass', frequency: 6000, Q: 1.2 }), new Tone.Panner(-0.35), this.drums);
    const crashTone = new Tone.Filter(4500, 'highpass');
    this.crashNoise.chain(crashTone, new Tone.Filter(12000, 'lowpass'), this.drums);
    this.send(crashTone, this.hall, 0.2);
    this.tomBody.connect(this.drums);
    this.send(this.tomBody, this.room, 0.4);

    this.bassSaw.chain(new Tone.Distortion({ distortion: 0.2, wet: 0.3 }), this.bed);
    this.bassSub.connect(this.bed);
    const shimmer = new Tone.Chorus({ frequency: 0.7, delayTime: 4, depth: 0.6, wet: 0.5 }).start();
    this.padSynth.chain(this.padFilter, shimmer);
    this.pluckSynth.connect(shimmer);
    shimmer.connect(this.bed);
    this.send(this.padFilter, this.hall, 0.3);
    this.send(this.pluckSynth, this.hall, 0.18);
    this.send(this.pluckSynth, this.echo, 0.12);
    this.brassSynth.connect(this.tune);
    this.send(this.brassSynth, this.hall, 0.22);
    const chorus = new Tone.Chorus({ frequency: 1.1, delayTime: 3.2, depth: 0.45, wet: 0.3 }).start();
    this.leadSynth.chain(new Tone.Vibrato({ frequency: 5.3, depth: 0.04 }), chorus, this.tune);
    this.send(chorus, this.echo, 0.2);
    this.send(chorus, this.hall, 0.14);
    this.bellSynth.connect(this.tune);
    this.send(this.bellSynth, this.echo, 0.25);
    this.send(this.bellSynth, this.hall, 0.3);

    this.boomBody.chain(new Tone.Distortion({ distortion: 0.3, wet: 0.4 }), this.fx);
    const boomTone = new Tone.Filter(2200, 'lowpass');
    this.boomNoise.chain(boomTone, this.fx);
    this.send(boomTone, this.hall, 0.45);
  }

  private send(from: Tone.ToneAudioNode, to: Tone.ToneAudioNode, amount: number) {
    from.connect(new Tone.Gain(amount).connect(to));
  }

  // Tone.js sources only accept triggers in time order, so every trigger is queued
  // and the arrangement can be written in whatever order reads best.
  private readonly queue: { t: number; seq: number; voice: string; run: () => void }[] = [];

  /** Queue a trigger on a monophonic `voice`; when two land on the same instant, the later call wins. */
  private at(t: number, voice: string, run: () => void) {
    this.queue.push({ t, seq: this.queue.length, voice, run });
  }

  /** Schedule everything that was queued, earliest first. */
  flush() {
    const sorted = this.queue.sort((a, b) => a.t - b.t || a.seq - b.seq);
    const kept: typeof sorted = [];
    const next = new Map<string, number>();
    for (let i = sorted.length - 1; i >= 0; i--) {
      const event = sorted[i];
      const later = next.get(event.voice);
      if (event.voice !== 'poly' && later !== undefined && later - event.t < 1e-4) continue;
      next.set(event.voice, event.t);
      kept.push(event);
    }
    for (let i = kept.length - 1; i >= 0; i--) kept[i].run();
    this.queue.length = 0;
  }

  // ── drums ────────────────────────────────────────────────────────────────
  /** `pump` ducks the bed under the kick; the stop-time hits leave it alone so chords and kick land together. */
  kick(t: number, vel = 0.95, pump = true) {
    this.at(t, 'kick', () => {
      this.kickBody.triggerAttackRelease('A1', 0.25, t, vel);
      this.kickClick.triggerAttackRelease(0.01, t, vel);
      if (!pump) return;
      this.pumped.gain.setTargetAtTime(0.4, t, 0.004);
      this.pumped.gain.setTargetAtTime(1, t + 0.04, 0.07);
    });
  }

  snare(t: number, vel = 0.8) {
    this.at(t, 'snare', () => {
      this.snareNoise.triggerAttackRelease(0.15, t, vel);
      this.snareBody.triggerAttackRelease('E3', 0.1, t, vel);
    });
  }

  clap(t: number, vel = 0.8) {
    for (const [dt, v] of [[0, 0.8], [0.01, 0.7], [0.021, 1]]) {
      this.at(t + dt, 'clap', () => this.clapNoise.triggerAttackRelease(0.1, t + dt, vel * v));
    }
  }

  hat(t: number, vel = 0.5) {
    this.at(t, 'hat', () => this.hatNoise.triggerAttackRelease(0.03, t, vel));
  }

  openHat(t: number, vel = 0.5) {
    this.at(t, 'openHat', () => this.openHatNoise.triggerAttackRelease(0.16, t, vel));
  }

  shaker(t: number, vel = 0.5) {
    this.at(t, 'shaker', () => this.shakerNoise.triggerAttackRelease(0.04, t, vel));
  }

  crash(t: number, vel = 0.7) {
    this.at(t, 'crash', () => this.crashNoise.triggerAttackRelease(1.4, t, vel));
  }

  tom(t: number, note: string, vel = 0.85) {
    this.at(t, 'tom', () => this.tomBody.triggerAttackRelease(note, 0.35, t, vel));
  }

  // ── tonal ────────────────────────────────────────────────────────────────
  /** Filtered saw bass; `sub` doubles the note with a sine for weight on the low notes. */
  bass(t: number, note: string, dur: number, vel = 0.9, sub = false) {
    this.at(t, 'bass', () => this.bassSaw.triggerAttackRelease(note, dur, t, vel));
    if (sub) this.at(t, 'sub', () => this.bassSub.triggerAttackRelease(note, dur, t, vel));
  }

  /** Sustained supersaw chord; the cutoff can sweep from `from` to `to` over the chord. */
  pad(t: number, notes: string[], dur: number, vel = 0.7, from = 4200, to = from) {
    this.at(t, 'poly', () => {
      this.padFilter.frequency.setValueAtTime(from, t);
      if (to !== from) this.padFilter.frequency.exponentialRampToValueAtTime(to, t + dur);
      this.padSynth.triggerAttackRelease(notes, dur, t, vel);
    });
  }

  pluck(t: number, notes: string[], vel = 0.8) {
    this.at(t, 'poly', () => this.pluckSynth.triggerAttackRelease(notes, 0.12, t, vel));
  }

  brass(t: number, notes: string[], dur: number, vel = 0.85) {
    this.at(t, 'poly', () => this.brassSynth.triggerAttackRelease(notes, dur, t, vel));
  }

  lead(t: number, note: string, dur: number, vel = 0.85) {
    this.at(t, 'lead', () => this.leadSynth.triggerAttackRelease(note, dur, t, vel));
  }

  bell(t: number, note: string, vel = 0.7) {
    this.at(t, 'poly', () => this.bellSynth.triggerAttackRelease(note, 0.3, t, vel));
  }

  // ── effects ──────────────────────────────────────────────────────────────
  /** Silences the bed from `t0` to `t1`: the breath before a drop. */
  breath(t0: number, t1: number) {
    this.at(t0, 'pump', () => {
      this.pumped.gain.setTargetAtTime(0, t0, 0.008);
      this.pumped.gain.setTargetAtTime(1, t1, 0.004);
    });
  }

  /** A deep boom with a burst of air. */
  impact(t: number, size = 1) {
    this.at(t, 'impact', () => {
      this.boomBody.triggerAttackRelease('A1', 0.8, t, Math.min(1, 0.7 * size));
      this.boomNoise.triggerAttackRelease(0.5, t, Math.min(1, 0.6 * size));
    });
  }

  /** Pink noise sweeping up through a bandpass, cut dead at `t1`. */
  riser(t0: number, t1: number, level = 0.2) {
    const filter = new Tone.Filter({ type: 'bandpass', frequency: 350, Q: 1.6 });
    const gain = new Tone.Gain(0);
    const noise = new Tone.Noise('pink').chain(filter, gain, this.fx);
    this.send(gain, this.hall, 0.3);
    filter.frequency.setValueAtTime(350, t0);
    filter.frequency.exponentialRampToValueAtTime(5000, t1);
    gain.gain.setValueAtTime(0.0001, t0);
    gain.gain.exponentialRampToValueAtTime(level, t1 - 0.01);
    gain.gain.linearRampToValueAtTime(0, t1 + 0.005);
    noise.start(t0).stop(t1 + 0.01);
  }

  /** A reversed cymbal: airy noise swelling into `t1`. */
  swell(t0: number, t1: number, level = 0.15) {
    const gain = new Tone.Gain(0);
    const noise = new Tone.Noise('white').chain(new Tone.Filter(3000, 'highpass'), new Tone.Filter(10000, 'lowpass'), gain, this.fx);
    gain.gain.setValueAtTime(0.0001, t0);
    gain.gain.exponentialRampToValueAtTime(level, t1 - 0.005);
    gain.gain.linearRampToValueAtTime(0, t1);
    noise.start(t0).stop(t1 + 0.01);
  }

  /** A chord that winds down like a switched-off tape machine. */
  tapeStop(t: number, notes: string[], length: number) {
    const gain = new Tone.Gain(1).connect(this.fx);
    const filter = new Tone.Filter({ type: 'lowpass', frequency: 4000, Q: 0.6 }).connect(gain);
    filter.frequency.setValueAtTime(4000, t);
    filter.frequency.exponentialRampToValueAtTime(150, t + length);
    gain.gain.setValueAtTime(1, t);
    gain.gain.linearRampToValueAtTime(0, t + length);
    for (const note of notes) {
      const voice = new Tone.Synth({
        oscillator: { type: 'fatsawtooth', count: 3, spread: 18 },
        envelope: { attack: 0.004, decay: 0, sustain: 1, release: 0.03 },
        volume: -17,
      }).connect(filter);
      const f = Tone.Frequency(note).toFrequency();
      voice.triggerAttack(f, t);
      voice.frequency.exponentialRampToValueAtTime(f / 6, t + length);
      voice.triggerRelease(t + length);
    }
  }
}
