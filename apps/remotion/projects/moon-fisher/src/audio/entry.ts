// Browser entry for scripts/score.mjs: renders the score offline and hands
// back a WAV as base64.
import "./seed";
import { renderScore, type RenderOptions } from "./score";
import { encodeWav } from "./wav";

declare global {
  interface Window {
    renderScoreWav: (options?: RenderOptions) => Promise<string>;
  }
}

window.renderScoreWav = async (options) => {
  const bytes = encodeWav(await renderScore(options));
  let binary = "";
  for (let i = 0; i < bytes.length; i += 0x8000) {
    binary += String.fromCharCode(...bytes.subarray(i, i + 0x8000));
  }
  return btoa(binary);
};
