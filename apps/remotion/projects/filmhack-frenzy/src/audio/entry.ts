// Browser entry for scripts/score.mjs: renders the score offline and hands back a WAV.
import './seed';
import { renderScore } from './score';
import { encodeWav } from './wav';

declare global {
  interface Window {
    renderScoreWav: () => Promise<string>;
  }
}

window.renderScoreWav = async () => {
  const bytes = encodeWav(await renderScore());
  let binary = '';
  for (let i = 0; i < bytes.length; i += 0x8000) binary += String.fromCharCode(...bytes.subarray(i, i + 0x8000));
  return btoa(binary);
};
