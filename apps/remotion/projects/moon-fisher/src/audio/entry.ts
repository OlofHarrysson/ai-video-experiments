// Browser entry for scripts/score.mjs: renders the score offline and hands
// back the WAV as base64 and every note it scheduled.
import "./seed";
import { renderScore, type RenderOptions, type ScoredNote } from "./score";
import { encodeWav } from "./wav";

declare global {
  interface Window {
    renderScoreWav: (
      options?: RenderOptions,
    ) => Promise<{ wav: string; notes: ScoredNote[] }>;
  }
}

window.renderScoreWav = async (options) => {
  const { buffer, notes } = await renderScore(options);
  const bytes = encodeWav(buffer);
  let binary = "";
  for (let i = 0; i < bytes.length; i += 0x8000) {
    binary += String.fromCharCode(...bytes.subarray(i, i + 0x8000));
  }
  return { wav: btoa(binary), notes };
};
