import * as Tone from "tone";
import LAYOUT from "./samples.json";
import { rand } from "./seed";

// Where the score's page fetches samples; scripts/score.mjs serves them from
// samples/.
export const SAMPLE_URL = "https://score.local/samples/";

export type InstrumentName = keyof typeof LAYOUT;

type Layout = {
  source: string;
  notes: string;
  octaveShift: number;
  sounds?: Record<string, string>;
  // Median RMS of each file's loudest 0.3 s, in dBFS. The library records
  // instruments at levels nearly 20 dB apart; the mix calibrates them to a
  // common level before voicing.
  recordedRms: number;
};

const REFERENCE_RMS = -24;

// Most VSCO file names number octaves one lower than scientific pitch; the
// harp's do not. Pitches were checked by spectrum analysis, which also found
// one clarinet file a semitone off its name.
const soundingNote = (layout: Layout, note: string): string => {
  const fixed = layout.sounds?.[note];
  if (fixed) return fixed;
  const m = /^([A-G]#?)(-?\d)$/.exec(note);
  if (!m) throw new Error(`Bad note ${note}`);
  return `${m[1]}${Number(m[2]) + layout.octaveShift}`;
};

const urlsFor = (layout: Layout): Record<string, string> =>
  Object.fromEntries(
    layout.notes.split(" ").map((note) => {
      const file = layout.source.replace("{note}", note).split("/").pop()!;
      return [soundingNote(layout, note), encodeURIComponent(file)];
    }),
  );

// How each instrument is played: envelope, level after calibration, place in
// the stereo field and how much hall it gets. The clarinet carries the tune.
const VOICING: Record<
  InstrumentName,
  { attack: number; release: number; volume: number; pan: number; hall: number }
> = {
  harp: { attack: 0, release: 1.6, volume: -12, pan: -0.25, hall: 0.35 },
  // One note at a time, like a real clarinet: each stops as the next begins.
  clarinet: { attack: 0.03, release: 0.09, volume: -4, pan: 0.08, hall: 0.3 },
  // Rings about as long as a music box, so the tune stays clear.
  glock: { attack: 0, release: 1.1, volume: -9, pan: 0.3, hall: 0.5 },
  cello: { attack: 0.3, release: 1.2, volume: -13, pan: -0.12, hall: 0.3 },
  celloPizz: { attack: 0, release: 0.9, volume: -11, pan: -0.15, hall: 0.25 },
  violins: { attack: 0.45, release: 1.6, volume: -13, pan: 0.22, hall: 0.4 },
  bassPizz: { attack: 0, release: 1.2, volume: -12, pan: 0, hall: 0.2 },
};

// A stereo hall: noise with an exponential tail, darkened as it decays.
const hallImpulse = (seconds: number): AudioBuffer => {
  const context = Tone.getContext();
  const rate = context.sampleRate;
  const length = Math.floor(seconds * rate);
  const buffer = context.createBuffer(2, length, rate);
  for (let c = 0; c < 2; c++) {
    const data = buffer.getChannelData(c);
    let smooth = 0;
    for (let i = 0; i < length; i++) {
      const t = i / length;
      const tone = 0.55 - 0.4 * t;
      smooth += tone * (rand() * 2 - 1 - smooth);
      data[i] = i < 0.015 * rate ? 0 : smooth * Math.pow(1 - t, 3.2);
    }
  }
  return buffer;
};

export type Band = {
  samplers: Record<InstrumentName, Tone.Sampler>;
  master: Tone.Gain;
  // A soft sea under everything; its level is automated by the score.
  sea: Tone.Gain;
};

// Every instrument in the score, created inside the offline context. `only`
// renders a subset, and `dry` leaves out the hall, for analysis.
export const createBand = (only?: InstrumentName[], dry = false): Band => {
  const master = new Tone.Gain(0.9);
  const glue = new Tone.Compressor({
    threshold: -20,
    ratio: 1.6,
    attack: 0.02,
    release: 0.25,
    knee: 8,
  });
  const low = new Tone.Filter({
    type: "highpass",
    frequency: 35,
    rolloff: -24,
  });
  master.chain(low, glue, new Tone.Limiter(-1), Tone.getDestination());

  const hall = new Tone.Convolver(new Tone.ToneAudioBuffer(hallImpulse(3.2)));
  const hallReturn = new Tone.Gain(dry ? 0 : 0.55);
  hall.chain(hallReturn, master);

  const samplers = {} as Record<InstrumentName, Tone.Sampler>;
  for (const [name, layout] of Object.entries(LAYOUT) as [
    InstrumentName,
    Layout,
  ][]) {
    const v = VOICING[name];
    const sampler = new Tone.Sampler({
      urls: urlsFor(layout),
      baseUrl: `${SAMPLE_URL}${name}/`,
      attack: v.attack,
      release: v.release,
    });
    const calibration = REFERENCE_RMS - layout.recordedRms;
    const channel = new Tone.Channel({
      volume: only && !only.includes(name) ? -Infinity : v.volume + calibration,
      pan: v.pan,
    });
    const send = new Tone.Gain(v.hall);
    sampler.connect(channel);
    channel.connect(master);
    channel.connect(send);
    send.connect(hall);
    samplers[name] = sampler;
  }

  // The sea: a low rumble of brown noise and a faint hiss of foam.
  const sea = new Tone.Gain(0);
  const rumble = new Tone.Noise("brown").start(0);
  const foam = new Tone.Noise("pink").start(0);
  const rumbleFilter = new Tone.Filter({
    type: "lowpass",
    frequency: 380,
    Q: 0.4,
  });
  const foamFilter = new Tone.Filter({
    type: "bandpass",
    frequency: 2600,
    Q: 0.6,
  });
  const foamLevel = new Tone.Gain(0.12);
  rumble.chain(rumbleFilter, sea);
  foam.chain(foamFilter, foamLevel, sea);
  sea.connect(master);
  const seaSend = new Tone.Gain(0.2);
  sea.connect(seaSend);
  seaSend.connect(hall);

  return { samplers, master, sea };
};
