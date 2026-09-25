import { rng } from '../util';

export const mtof = (midi: number) => 440 * Math.pow(2, (midi - 69) / 12);

function curve(fn: (x: number) => number, size = 2048) {
  const c = new Float32Array(size);
  for (let i = 0; i < size; i++) c[i] = fn((i / (size - 1)) * 2 - 1);
  return c;
}
const softClip = (drive: number) => curve((x) => Math.tanh(drive * x) / Math.tanh(drive));
const STAIRS = curve((x) => Math.round(x * 5) / 5);

export interface ChordOptions {
  vel?: number;
  attack?: number;
  release?: number;
  cutoff?: number;
  cutoffTo?: number;
  voices?: number;
  detune?: number;
  verb?: number;
  /** 'stab' decays exponentially over `dur`; 'pad' sustains and releases. */
  shape?: 'stab' | 'pad';
}

/**
 * A small synthesizer rack on an OfflineAudioContext: drums, bass, supersaw chords,
 * a delayed pluck and trailer-style effects, mixed through a glue compressor and limiter.
 */
export class Studio {
  readonly ctx: OfflineAudioContext;
  readonly master: GainNode;
  readonly music: GainNode;
  readonly drums: GainNode;
  readonly sfx: GainNode;
  readonly verb: GainNode;
  readonly echo: GainNode;
  readonly random: () => number;
  private readonly duck: GainNode;
  private readonly noiseBuffer: AudioBuffer;

  constructor(ctx: OfflineAudioContext, beat: number) {
    this.ctx = ctx;
    this.random = rng(20261113);

    const glue = ctx.createDynamicsCompressor();
    glue.threshold.value = -18;
    glue.knee.value = 8;
    glue.ratio.value = 2.5;
    glue.attack.value = 0.01;
    glue.release.value = 0.2;
    const limiter = ctx.createDynamicsCompressor();
    limiter.threshold.value = -4;
    limiter.knee.value = 0;
    limiter.ratio.value = 20;
    limiter.attack.value = 0.001;
    limiter.release.value = 0.08;
    this.master = this.gain(0.9);
    const rumble = this.filter('highpass', 30, 0.7);
    const shelf = this.filter('lowshelf', 110);
    shelf.gain.value = -4.5;
    const air = this.filter('highshelf', 9000);
    air.gain.value = -2.5;
    this.master.connect(rumble);
    rumble.connect(shelf);
    shelf.connect(air);
    air.connect(glue);
    glue.connect(limiter);
    limiter.connect(ctx.destination);

    this.duck = this.gain(1);
    this.duck.connect(this.master);
    this.music = this.bus(this.duck);
    this.drums = this.bus(this.master);
    this.sfx = this.bus(this.master);

    const reverb = ctx.createConvolver();
    reverb.buffer = this.impulse(2.6, 3.2);
    this.verb = this.gain(1);
    this.verb.connect(reverb);
    reverb.connect(this.bus(this.master, 0.7));

    // Ping-pong echo: each repeat alternates sides, a dotted eighth apart.
    const tone = this.filter('lowpass', 3400, 0.7);
    const left = ctx.createDelay(2);
    const right = ctx.createDelay(2);
    left.delayTime.value = right.delayTime.value = beat * 0.75;
    const echoOut = this.bus(this.music, 0.6);
    this.echo = this.gain(1);
    this.echo.connect(tone);
    tone.connect(left);
    left.connect(this.bus(right, 0.4));
    right.connect(this.bus(left, 0.4));
    left.connect(this.panner(-0.85)).connect(echoOut);
    right.connect(this.panner(0.85)).connect(echoOut);

    this.noiseBuffer = this.makeNoise(4);
  }

  // ── plumbing ────────────────────────────────────────────────────────────
  gain(value = 0) {
    const g = this.ctx.createGain();
    g.gain.value = value;
    return g;
  }

  bus(destination: AudioNode, value = 1) {
    const g = this.gain(value);
    g.connect(destination);
    return g;
  }

  filter(type: BiquadFilterType, frequency: number, q = 0.7) {
    const f = this.ctx.createBiquadFilter();
    f.type = type;
    f.frequency.value = frequency;
    f.Q.value = q;
    return f;
  }

  osc(type: OscillatorType, frequency: number) {
    const o = this.ctx.createOscillator();
    o.type = type;
    o.frequency.value = frequency;
    return o;
  }

  panner(pan: number) {
    const p = this.ctx.createStereoPanner();
    p.pan.value = pan;
    return p;
  }

  shaper(c: Float32Array<ArrayBuffer>) {
    const s = this.ctx.createWaveShaper();
    s.curve = c;
    s.oversample = '2x';
    return s;
  }

  send(from: AudioNode, to: AudioNode, amount: number) {
    if (amount > 0) from.connect(this.bus(to, amount));
  }

  /** Linear attack to `peak`, exponential release to silence. */
  env(param: AudioParam, t: number, attack: number, peak: number, release: number) {
    param.setValueAtTime(0.0001, t);
    param.linearRampToValueAtTime(peak, t + attack);
    param.exponentialRampToValueAtTime(0.0001, t + attack + release);
  }

  noise(t: number, dur: number) {
    const src = this.ctx.createBufferSource();
    src.buffer = this.noiseBuffer;
    src.loop = true;
    src.start(t, this.random() * (this.noiseBuffer.duration - 0.1));
    src.stop(t + dur);
    return src;
  }

  /** Pumps everything on the music bus against the kick. */
  sidechain(t: number, depth = 0.5) {
    this.duck.gain.setTargetAtTime(depth, t, 0.003);
    this.duck.gain.setTargetAtTime(1, t + 0.035, 0.07);
  }

  private makeNoise(seconds: number) {
    const buffer = this.ctx.createBuffer(1, Math.floor(seconds * this.ctx.sampleRate), this.ctx.sampleRate);
    const data = buffer.getChannelData(0);
    const random = rng(7);
    for (let i = 0; i < data.length; i++) data[i] = random() * 2 - 1;
    return buffer;
  }

  private impulse(seconds: number, decay: number) {
    const rate = this.ctx.sampleRate;
    const length = Math.floor(seconds * rate);
    const buffer = this.ctx.createBuffer(2, length, rate);
    const random = rng(99);
    for (let c = 0; c < 2; c++) {
      const data = buffer.getChannelData(c);
      let smooth = 0;
      for (let i = 0; i < length; i++) {
        smooth += 0.4 * (random() * 2 - 1 - smooth);
        data[i] = i < 0.018 * rate ? 0 : smooth * Math.pow(1 - i / length, decay);
      }
    }
    return buffer;
  }

  /** TR-808 style metallic tone for hats and cymbals, running only while the hit sounds. */
  private metal(t: number, dur: number) {
    const mix = this.gain(0.2);
    for (const f of [205.3, 304.4, 369.6, 522.7, 540, 800]) {
      const o = this.osc('square', f * 1.4);
      o.connect(mix);
      o.start(t);
      o.stop(t + dur);
    }
    const bp = this.filter('bandpass', 9800, 0.9);
    const hp = this.filter('highpass', 7200, 0.7);
    mix.connect(bp);
    bp.connect(hp);
    return hp;
  }

  // ── drums ───────────────────────────────────────────────────────────────
  kick(t: number, vel = 1) {
    const body = this.osc('sine', 200);
    body.frequency.setValueAtTime(210, t);
    body.frequency.exponentialRampToValueAtTime(62, t + 0.05);
    body.frequency.exponentialRampToValueAtTime(46, t + 0.3);
    const drive = this.shaper(softClip(2.6));
    const g = this.gain();
    this.env(g.gain, t, 0.0015, vel, 0.38);
    body.connect(drive);
    drive.connect(g);
    g.connect(this.drums);
    body.start(t);
    body.stop(t + 0.45);

    const click = this.noise(t, 0.03);
    const hp = this.filter('highpass', 3000);
    const cg = this.gain();
    this.env(cg.gain, t, 0.0005, 0.22 * vel, 0.016);
    click.connect(hp);
    hp.connect(cg);
    cg.connect(this.drums);
    this.sidechain(t);
  }

  clap(t: number, vel = 0.5) {
    const src = this.noise(t, 0.35);
    const bp = this.filter('bandpass', 1250, 1.3);
    const hp = this.filter('highpass', 650);
    const g = this.gain();
    for (const [dt, amp] of [[0, 1], [0.01, 0.85], [0.021, 0.7]]) {
      g.gain.setValueAtTime(amp * vel, t + dt);
      g.gain.exponentialRampToValueAtTime(0.02 * vel, t + dt + 0.009);
    }
    g.gain.setValueAtTime(0.75 * vel, t + 0.031);
    g.gain.exponentialRampToValueAtTime(0.0001, t + 0.24);
    src.connect(bp);
    bp.connect(hp);
    hp.connect(g);
    g.connect(this.drums);
    this.send(g, this.verb, 0.25);
  }

  hat(t: number, vel = 0.15, open = false) {
    const g = this.gain();
    this.env(g.gain, t, 0.001, vel, open ? 0.26 : 0.045);
    this.metal(t, open ? 0.3 : 0.06).connect(g);
    g.connect(this.drums);
    const n = this.noise(t, open ? 0.3 : 0.06);
    const hp = this.filter('highpass', 8500);
    const ng = this.gain();
    this.env(ng.gain, t, 0.001, vel * 0.35, open ? 0.2 : 0.035);
    n.connect(hp);
    hp.connect(ng);
    ng.connect(this.drums);
  }

  snare(t: number, vel = 0.5) {
    const n = this.noise(t, 0.25);
    const bp = this.filter('bandpass', 1900, 0.8);
    const g = this.gain();
    this.env(g.gain, t, 0.001, vel, 0.15);
    n.connect(bp);
    bp.connect(g);
    g.connect(this.drums);
    const tone = this.osc('triangle', 210);
    tone.frequency.setValueAtTime(210, t);
    tone.frequency.exponentialRampToValueAtTime(160, t + 0.08);
    const tg = this.gain();
    this.env(tg.gain, t, 0.001, vel * 0.6, 0.09);
    tone.connect(tg);
    tg.connect(this.drums);
    tone.start(t);
    tone.stop(t + 0.15);
    this.send(g, this.verb, 0.15);
  }

  crash(t: number, vel = 0.4) {
    const n = this.noise(t, 1.8);
    const hp = this.filter('highpass', 5200, 0.6);
    const lp = this.filter('lowpass', 12000, 0.7);
    const g = this.gain();
    this.env(g.gain, t, 0.002, vel, 1.4);
    n.connect(hp);
    hp.connect(lp);
    lp.connect(g);
    g.connect(this.drums);
    const mg = this.gain();
    this.env(mg.gain, t, 0.002, vel * 0.8, 1.4);
    this.metal(t, 1.5).connect(mg);
    mg.connect(this.drums);
    this.send(g, this.verb, 0.3);
  }

  // ── tonal ───────────────────────────────────────────────────────────────
  bass(t: number, midi: number, vel = 0.4, len = 0.2) {
    const f = mtof(midi);
    const saw = this.osc('sawtooth', f);
    const sub = this.osc('sine', f);
    const lp = this.filter('lowpass', 2800, 4);
    lp.frequency.setValueAtTime(2800, t);
    lp.frequency.exponentialRampToValueAtTime(750, t + 0.14);
    const g = this.gain();
    this.env(g.gain, t, 0.004, vel, len);
    const subGain = this.gain(0.35);
    saw.connect(lp);
    lp.connect(g);
    sub.connect(subGain);
    subGain.connect(g);
    g.connect(this.music);
    for (const o of [saw, sub]) {
      o.start(t);
      o.stop(t + len + 0.05);
    }
  }

  /** Detuned-saw chord, either a decaying stab or a sustained pad. */
  chord(t: number, notes: number[], dur: number, o: ChordOptions = {}) {
    const vel = o.vel ?? 0.2;
    const voices = o.voices ?? 5;
    const detune = o.detune ?? 18;
    const lp = this.filter('lowpass', o.cutoff ?? 3000, 0.8);
    if (o.cutoffTo) {
      lp.frequency.setValueAtTime(o.cutoff ?? 3000, t);
      lp.frequency.exponentialRampToValueAtTime(o.cutoffTo, t + dur);
    }
    const g = this.gain();
    if ((o.shape ?? 'stab') === 'stab') {
      this.env(g.gain, t, o.attack ?? 0.004, vel, dur);
    } else {
      const attack = o.attack ?? 0.05;
      const release = o.release ?? 0.15;
      g.gain.setValueAtTime(0, t);
      g.gain.linearRampToValueAtTime(vel, t + attack);
      g.gain.setValueAtTime(vel, t + Math.max(attack, dur - release));
      g.gain.linearRampToValueAtTime(0, t + dur);
    }
    lp.connect(g);
    g.connect(this.music);
    this.send(g, this.verb, o.verb ?? 0.15);
    const per = 1 / (notes.length * Math.sqrt(voices));
    for (const note of notes) {
      for (let v = 0; v < voices; v++) {
        const spread = voices === 1 ? 0 : (v / (voices - 1)) * 2 - 1;
        const saw = this.osc('sawtooth', mtof(note));
        saw.detune.value = spread * detune;
        const vg = this.gain(per);
        const pan = this.panner(spread * 0.7);
        saw.connect(vg);
        vg.connect(pan);
        pan.connect(lp);
        saw.start(t);
        saw.stop(t + dur + 0.05);
      }
    }
  }

  pluck(t: number, midi: number, vel = 0.1, cutoff = 2000) {
    const f = mtof(midi);
    const a = this.osc('sawtooth', f);
    const b = this.osc('square', f);
    b.detune.value = 7;
    const bg = this.gain(0.5);
    const lp = this.filter('lowpass', cutoff * 2.2, 3);
    lp.frequency.setValueAtTime(cutoff * 2.2, t);
    lp.frequency.exponentialRampToValueAtTime(cutoff * 0.6, t + 0.1);
    const g = this.gain();
    this.env(g.gain, t, 0.002, vel, 0.11);
    a.connect(lp);
    b.connect(bg);
    bg.connect(lp);
    lp.connect(g);
    g.connect(this.music);
    this.send(g, this.echo, 0.35);
    this.send(g, this.verb, 0.08);
    for (const o of [a, b]) {
      o.start(t);
      o.stop(t + 0.16);
    }
  }

  blip(t: number, midi: number, vel = 0.05) {
    const o = this.osc('triangle', mtof(midi));
    const g = this.gain();
    this.env(g.gain, t, 0.002, vel, 0.07);
    o.connect(g);
    g.connect(this.music);
    this.send(g, this.echo, 0.3);
    o.start(t);
    o.stop(t + 0.1);
  }

  drone(t0: number, t1: number, vel = 0.13) {
    const lp = this.filter('lowpass', 140, 2);
    lp.frequency.setValueAtTime(140, t0);
    lp.frequency.exponentialRampToValueAtTime(1400, t1);
    const g = this.gain();
    g.gain.setValueAtTime(0, t0);
    g.gain.linearRampToValueAtTime(vel, t0 + 0.25);
    g.gain.setValueAtTime(vel, t1 - 0.03);
    g.gain.linearRampToValueAtTime(0, t1);
    for (const note of [38, 45, 50]) {
      for (const d of [-9, 9]) {
        const saw = this.osc('sawtooth', mtof(note));
        saw.detune.value = d;
        const vg = this.gain(0.2);
        saw.connect(vg);
        vg.connect(lp);
        saw.start(t0);
        saw.stop(t1 + 0.05);
      }
    }
    lp.connect(g);
    g.connect(this.music);
    this.send(g, this.verb, 0.3);
  }

  // ── effects ─────────────────────────────────────────────────────────────
  impact(t: number, size = 1) {
    const sub = this.osc('sine', 120);
    sub.frequency.setValueAtTime(120, t);
    sub.frequency.exponentialRampToValueAtTime(45, t + 0.6);
    const drive = this.shaper(softClip(2.5));
    const sg = this.gain();
    this.env(sg.gain, t, 0.002, 0.6 * size, 1.1 * Math.sqrt(size));
    sub.connect(drive);
    drive.connect(sg);
    sg.connect(this.sfx);
    sub.start(t);
    sub.stop(t + 1.6);

    const crack = this.noise(t, 0.5);
    const lp = this.filter('lowpass', 7000);
    const hp = this.filter('highpass', 180);
    const cg = this.gain();
    this.env(cg.gain, t, 0.001, 0.5 * size, 0.28);
    crack.connect(lp);
    lp.connect(hp);
    hp.connect(cg);
    cg.connect(this.sfx);
    this.send(cg, this.verb, 0.5);

    const thump = this.noise(t, 0.4);
    const tl = this.filter('lowpass', 240, 1);
    const tg = this.gain();
    this.env(tg.gain, t, 0.001, 0.6 * size, 0.3);
    thump.connect(tl);
    tl.connect(tg);
    tg.connect(this.sfx);
  }

  /** Trailer horn: distorted detuned saws on D with an opening filter. */
  braam(t: number, dur = 1.8, vel = 0.45) {
    const drive = this.shaper(softClip(4));
    const lp = this.filter('lowpass', 150, 2.5);
    lp.frequency.setValueAtTime(150, t);
    lp.frequency.exponentialRampToValueAtTime(2800, t + 0.16);
    lp.frequency.exponentialRampToValueAtTime(500, t + dur);
    const g = this.gain();
    g.gain.setValueAtTime(0, t);
    g.gain.linearRampToValueAtTime(vel, t + 0.025);
    g.gain.exponentialRampToValueAtTime(0.0001, t + dur);
    for (const note of [38, 45, 50]) {
      for (const d of [-12, 0, 12]) {
        const saw = this.osc('sawtooth', mtof(note));
        saw.detune.value = d;
        const vg = this.gain(0.12);
        saw.connect(vg);
        vg.connect(drive);
        saw.start(t);
        saw.stop(t + dur + 0.05);
      }
    }
    drive.connect(lp);
    lp.connect(g);
    g.connect(this.sfx);
    this.send(g, this.verb, 0.45);
  }

  riser(t0: number, t1: number, vel = 0.3) {
    for (const pan of [-0.6, 0.6]) {
      const n = this.noise(t0, t1 - t0 + 0.05);
      const bp = this.filter('bandpass', 400, 2.2);
      bp.frequency.setValueAtTime(400, t0);
      bp.frequency.exponentialRampToValueAtTime(6500, t1);
      const g = this.gain();
      g.gain.setValueAtTime(0.0001, t0);
      g.gain.exponentialRampToValueAtTime(vel, t1 - 0.01);
      g.gain.linearRampToValueAtTime(0, t1 + 0.01);
      const p = this.panner(pan);
      n.connect(bp);
      bp.connect(g);
      g.connect(p);
      p.connect(this.sfx);
    }
    const saw = this.osc('sawtooth', mtof(50));
    saw.frequency.setValueAtTime(mtof(50), t0);
    saw.frequency.exponentialRampToValueAtTime(mtof(74), t1);
    const lp = this.filter('lowpass', 500, 1.5);
    lp.frequency.setValueAtTime(500, t0);
    lp.frequency.exponentialRampToValueAtTime(6000, t1);
    const sg = this.gain();
    sg.gain.setValueAtTime(0.0001, t0);
    sg.gain.exponentialRampToValueAtTime(vel * 0.45, t1 - 0.01);
    sg.gain.linearRampToValueAtTime(0, t1 + 0.01);
    saw.connect(lp);
    lp.connect(sg);
    sg.connect(this.sfx);
    this.send(sg, this.verb, 0.2);
    saw.start(t0);
    saw.stop(t1 + 0.05);
  }

  /** Reverse-cymbal swell that cuts dead on t1. */
  swell(t0: number, t1: number, vel = 0.35) {
    const n = this.noise(t0, t1 - t0 + 0.02);
    const hp = this.filter('highpass', 3500);
    const g = this.gain();
    g.gain.setValueAtTime(0.0001, t0);
    g.gain.exponentialRampToValueAtTime(vel, t1);
    g.gain.linearRampToValueAtTime(0, t1 + 0.012);
    n.connect(hp);
    hp.connect(g);
    g.connect(this.sfx);
    this.send(g, this.verb, 0.2);
  }

  /** Band-passed noise sweep; `peak` sets where in the sweep it is loudest (near 1 = cut dead at the end). */
  whoosh(t: number, dur: number, o: { vel?: number; from?: number; to?: number; pan?: [number, number]; peak?: number } = {}) {
    const n = this.noise(t, dur + 0.05);
    const bp = this.filter('bandpass', o.from ?? 400, 1.4);
    bp.frequency.setValueAtTime(o.from ?? 400, t);
    bp.frequency.exponentialRampToValueAtTime(o.to ?? 3000, t + dur);
    const g = this.gain();
    g.gain.setValueAtTime(0.0001, t);
    g.gain.exponentialRampToValueAtTime(o.vel ?? 0.3, t + dur * (o.peak ?? 0.55));
    g.gain.exponentialRampToValueAtTime(0.0001, t + dur);
    const p = this.panner(0);
    const [from, to] = o.pan ?? [0, 0];
    p.pan.setValueAtTime(from, t);
    p.pan.linearRampToValueAtTime(to, t + dur);
    n.connect(bp);
    bp.connect(g);
    g.connect(p);
    p.connect(this.sfx);
    this.send(g, this.verb, 0.15);
  }

  /** Digital glitch: a burst of random square blips plus bit-crushed noise. */
  glitch(t: number, dur = 0.16, vel = 0.18) {
    const hp = this.filter('highpass', 250);
    const out = this.gain(vel);
    hp.connect(out);
    out.connect(this.sfx);
    for (let x = t; x < t + dur; ) {
      const len = 0.007 + this.random() * 0.02;
      const o = this.osc('square', 200 + this.random() * 3800);
      const g = this.gain();
      g.gain.setValueAtTime(0.4 + 0.6 * this.random(), x);
      g.gain.setValueAtTime(0, x + len);
      o.connect(g);
      g.connect(hp);
      o.start(x);
      o.stop(x + len + 0.002);
      x += len;
    }
    const n = this.noise(t, dur);
    const crush = this.shaper(STAIRS);
    const bp = this.filter('bandpass', 1800, 0.8);
    const ng = this.gain();
    this.env(ng.gain, t, 0.001, 0.5, dur);
    n.connect(crush);
    crush.connect(bp);
    bp.connect(ng);
    ng.connect(out);
  }

  /** Wooden clapperboard snap. */
  slateClap(t: number) {
    const n = this.noise(t, 0.12);
    const hp = this.filter('highpass', 1400);
    const g = this.gain();
    this.env(g.gain, t, 0.0004, 1, 0.05);
    n.connect(hp);
    hp.connect(g);
    g.connect(this.sfx);
    this.send(g, this.verb, 0.35);
    for (const [f, a] of [[820, 0.5], [1310, 0.3], [2150, 0.18]]) {
      const o = this.osc('sine', f);
      const og = this.gain();
      this.env(og.gain, t, 0.0005, a, 0.07);
      o.connect(og);
      og.connect(this.sfx);
      o.start(t);
      o.stop(t + 0.1);
    }
    const knock = this.osc('sine', 190);
    knock.frequency.setValueAtTime(190, t);
    knock.frequency.exponentialRampToValueAtTime(110, t + 0.06);
    const kg = this.gain();
    this.env(kg.gain, t, 0.0008, 0.7, 0.09);
    knock.connect(kg);
    kg.connect(this.sfx);
    knock.start(t);
    knock.stop(t + 0.12);
  }

  beep(t: number, freq = 2093, dur = 0.07, vel = 0.1) {
    const o = this.osc('square', freq);
    const lp = this.filter('lowpass', 6000);
    const g = this.gain();
    g.gain.setValueAtTime(0, t);
    g.gain.linearRampToValueAtTime(vel, t + 0.002);
    g.gain.setValueAtTime(vel, t + dur);
    g.gain.linearRampToValueAtTime(0, t + dur + 0.004);
    o.connect(lp);
    lp.connect(g);
    g.connect(this.sfx);
    o.start(t);
    o.stop(t + dur + 0.01);
  }

  tick(t: number, vel = 0.3) {
    const n = this.noise(t, 0.03);
    const bp = this.filter('bandpass', 3800, 6);
    const g = this.gain();
    this.env(g.gain, t, 0.0003, vel, 0.02);
    n.connect(bp);
    bp.connect(g);
    g.connect(this.sfx);
    const o = this.osc('sine', 1600);
    const og = this.gain();
    this.env(og.gain, t, 0.0005, vel * 0.3, 0.015);
    o.connect(og);
    og.connect(this.sfx);
    o.start(t);
    o.stop(t + 0.03);
  }

  /** Typewriter key. */
  key(t: number, vel = 0.14) {
    const n = this.noise(t, 0.03);
    const bp = this.filter('bandpass', 2400 + this.random() * 2200, 3);
    const g = this.gain();
    this.env(g.gain, t, 0.0004, vel, 0.018);
    n.connect(bp);
    bp.connect(g);
    g.connect(this.sfx);
    const o = this.osc('sine', 140 + this.random() * 40);
    const og = this.gain();
    this.env(og.gain, t, 0.0008, vel * 0.5, 0.03);
    o.connect(og);
    og.connect(this.sfx);
    o.start(t);
    o.stop(t + 0.05);
  }

  /** Edit-timeline snap. */
  snap(t: number, vel = 0.25) {
    const n = this.noise(t, 0.02);
    const hp = this.filter('highpass', 2500);
    const g = this.gain();
    this.env(g.gain, t, 0.0003, vel, 0.01);
    n.connect(hp);
    hp.connect(g);
    g.connect(this.sfx);
    const o = this.osc('sine', 2800);
    const og = this.gain();
    this.env(og.gain, t, 0.0005, vel * 0.4, 0.012);
    o.connect(og);
    og.connect(this.sfx);
    o.start(t);
    o.stop(t + 0.03);
  }

  /** Projector start: a mechanical clunk, then a whir fluttering at 24 frames per second. */
  projector(t0: number, t1: number) {
    const n = this.noise(t0, 0.2);
    const lp = this.filter('lowpass', 500);
    const g = this.gain();
    this.env(g.gain, t0, 0.001, 0.6, 0.14);
    n.connect(lp);
    lp.connect(g);
    g.connect(this.sfx);
    const k = this.osc('sine', 85);
    const kg = this.gain();
    this.env(kg.gain, t0, 0.001, 0.5, 0.18);
    k.connect(kg);
    kg.connect(this.sfx);
    k.start(t0);
    k.stop(t0 + 0.25);

    const whir = this.noise(t0, t1 - t0 + 0.1);
    const bp = this.filter('bandpass', 1100, 0.9);
    const wg = this.gain();
    wg.gain.setValueAtTime(0, t0);
    wg.gain.linearRampToValueAtTime(0.05, t0 + 0.4);
    wg.gain.setValueAtTime(0.05, t1 - 0.5);
    wg.gain.linearRampToValueAtTime(0, t1);
    const lfo = this.osc('square', 24);
    const depth = this.gain(0.03);
    lfo.connect(depth);
    depth.connect(wg.gain);
    lfo.start(t0);
    lfo.stop(t1);
    whir.connect(bp);
    bp.connect(wg);
    wg.connect(this.sfx);
  }

  /** Granular applause: Poisson-timed hand claps plus a crowd roar. */
  applause(t0: number, t1: number, peakRate = 60, vel = 0.07) {
    const span = t1 - t0;
    const shape = (x: number) => (x < 0.2 ? x / 0.2 : x > 0.6 ? Math.max(0, 1 - (x - 0.6) / 0.4) : 1);
    for (let x = t0; ; ) {
      const level = shape((x - t0) / span);
      x += -Math.log(1 - this.random()) / Math.max(4, peakRate * level);
      if (x >= t1) break;
      const n = this.noise(x, 0.05);
      const bp = this.filter('bandpass', 900 + this.random() * 1900, 1.2 + this.random() * 2);
      const g = this.gain();
      this.env(g.gain, x, 0.0008, vel * (0.4 + 0.6 * this.random()) * (0.3 + 0.7 * level), 0.008 + this.random() * 0.018);
      const p = this.panner((this.random() * 2 - 1) * 0.85);
      n.connect(bp);
      bp.connect(g);
      g.connect(p);
      p.connect(this.sfx);
    }
    const roar = this.noise(t0, span + 0.1);
    const lp = this.filter('lowpass', 1600);
    const bp = this.filter('bandpass', 650, 0.5);
    const rg = this.gain();
    rg.gain.setValueAtTime(0, t0);
    rg.gain.linearRampToValueAtTime(vel * 1.4, t0 + span * 0.25);
    rg.gain.setValueAtTime(vel * 1.4, t0 + span * 0.6);
    rg.gain.linearRampToValueAtTime(0, t1);
    roar.connect(lp);
    lp.connect(bp);
    bp.connect(rg);
    rg.connect(this.sfx);
    this.send(rg, this.verb, 0.3);
  }

  whistle(t: number, dur = 0.6, vel = 0.035, pan = 0) {
    const o = this.osc('sine', 1500);
    o.frequency.setValueAtTime(1500, t);
    o.frequency.linearRampToValueAtTime(2500, t + 0.16);
    o.frequency.linearRampToValueAtTime(2250, t + dur);
    const vib = this.osc('sine', 6.5);
    const depth = this.gain(35);
    vib.connect(depth);
    depth.connect(o.frequency);
    const g = this.gain();
    g.gain.setValueAtTime(0, t);
    g.gain.linearRampToValueAtTime(vel, t + 0.05);
    g.gain.setValueAtTime(vel, t + dur - 0.12);
    g.gain.linearRampToValueAtTime(0, t + dur);
    const p = this.panner(pan);
    o.connect(g);
    g.connect(p);
    p.connect(this.sfx);
    this.send(g, this.verb, 0.35);
    for (const x of [o, vib]) {
      x.start(t);
      x.stop(t + dur + 0.02);
    }
  }
}
