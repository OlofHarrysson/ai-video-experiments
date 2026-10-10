// All parts share one AudioContext clock; mute changes gain, never the playhead.
export class Mixer {
  constructor(context, duration) {
    this.context = context; this.duration = duration; this.offset = 0;
    this.playing = false; this.loop = true; this.nodes = [];
    this.muted = new Set(); this.solo = new Set(); this.buffers = {};
    this.output = context.createGain(); this.output.gain.value = .8;
    this.output.connect(context.destination); this.paletteGain = 1; this.generation = 0;
  }
  position() {
    if (!this.playing) return this.offset;
    const raw = this.offset + Math.max(0, this.context.currentTime - this.started);
    return this.loop ? raw % this.duration : Math.min(raw, this.duration);
  }
  audible(id) { return !this.muted.has(id) && (!this.solo.size || this.solo.has(id)); }
  updateGains() {
    const now = this.context.currentTime;
    for (const {id, gain} of this.nodes) {
      gain.gain.cancelScheduledValues(now);
      gain.gain.setTargetAtTime(this.audible(id) ? this.paletteGain : 0, now, .006);
    }
  }
  async play() {
    if (this.playing || !Object.keys(this.buffers).length) return;
    const generation = ++this.generation;
    await this.context.resume();
    if (generation !== this.generation) return;
    if (this.offset >= this.duration) this.offset = 0;
    this.started = this.context.currentTime + .04;
    this.nodes = Object.entries(this.buffers).map(([id, buffer]) => {
      const source = this.context.createBufferSource(), gain = this.context.createGain();
      source.buffer = buffer; source.loop = this.loop; source.loopStart = 0; source.loopEnd = this.duration;
      gain.gain.value = this.audible(id) ? this.paletteGain : 0;
      source.connect(gain); gain.connect(this.output); source.start(this.started, this.offset);
      return {id, source, gain};
    });
    this.playing = true;
  }
  pause() {
    ++this.generation; this.offset = this.position(); this.playing = false;
    for (const {source, gain} of this.nodes) { source.stop(); source.disconnect(); gain.disconnect(); }
    this.nodes = [];
  }
  async seek(value) {
    const running = this.playing; this.pause();
    this.offset = Math.max(0, Math.min(value, this.duration));
    if (running && this.offset < this.duration) await this.play();
  }
  setLoop(value) {
    const position = this.position(); this.offset = position; this.started = this.context.currentTime;
    this.loop = value; for (const n of this.nodes) n.source.loop = value;
  }
  mute(id) { this.muted.has(id) ? this.muted.delete(id) : this.muted.add(id); this.solo.delete(id); this.updateGains(); }
  isolate(id) { this.solo.has(id) ? this.solo.delete(id) : this.solo.add(id); this.muted.delete(id); this.updateGains(); }
  reset() { this.muted.clear(); this.solo.clear(); this.updateGains(); }
}
