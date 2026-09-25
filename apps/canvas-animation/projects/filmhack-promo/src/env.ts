import type { Fx } from './draw/fx';

export interface AudioData {
  left: Float32Array;
  right: Float32Array;
  sampleRate: number;
}

/** Font sizes fitted once the brand fonts have loaded. */
export interface Layout {
  hook: number;
  slate: number;
  clock: number;
  stage: number;
  logo: number;
  cta: number;
}

export interface Env {
  fx: Fx;
  feed: HTMLCanvasElement[];
  /** The finished film frame the IMAGE stage denoises towards. */
  still: HTMLCanvasElement;
  scratch: { el: HTMLCanvasElement; ctx: CanvasRenderingContext2D };
  noise: Map<string, HTMLCanvasElement>;
  layout: Layout;
  audio: AudioData | null;
}
