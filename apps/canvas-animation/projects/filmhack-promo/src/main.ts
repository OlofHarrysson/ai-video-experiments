import { renderScore } from './audio/score';
import { encodeWav } from './audio/wav';
import { BEAT, DURATION, FPS, FRAMES, H, SAFE, SCENE, W, b } from './config';
import { loadFonts } from './draw/fonts';
import type { Env } from './env';
import { prepare, renderFrame } from './film';

/** Hooks used by scripts/render.mjs to pull frames and the soundtrack out of the page. */
interface FilmApi {
  ready: boolean;
  frames: number;
  still(t: number): string;
  exportAudio(): Promise<void>;
  exportFrames(start: number, end: number): Promise<void>;
}

declare global {
  interface Window {
    film?: FilmApi;
  }
}

const exporting = new URLSearchParams(location.search).has('export');
const film = document.querySelector<HTMLCanvasElement>('#film')!;
film.width = W;
film.height = H;
const ctx = film.getContext('2d', { alpha: false, willReadFrequently: exporting })!;
const status = document.querySelector<HTMLElement>('#status')!;

let env: Env;
let soundtrack: AudioBuffer;
let time = 0;

async function boot() {
  await loadFonts();
  env = prepare(null);
  renderFrame(ctx, 0, env);
  status.textContent = 'Rendering soundtrack…';
  const started = performance.now();
  soundtrack = await renderScore();
  env.audio = { left: soundtrack.getChannelData(0), right: soundtrack.getChannelData(1), sampleRate: soundtrack.sampleRate };
  status.textContent = `Soundtrack rendered in ${((performance.now() - started) / 1000).toFixed(1)} s`;
  if (exporting) installExportApi();
  else installPlayer();
}

function installExportApi() {
  window.film = {
    ready: true,
    frames: FRAMES,
    still(t) {
      renderFrame(ctx, t, env);
      return film.toDataURL('image/png');
    },
    async exportAudio() {
      const res = await fetch('/__audio', { method: 'POST', body: encodeWav(soundtrack) });
      if (!res.ok) throw new Error(`audio rejected: ${res.status}`);
    },
    async exportFrames(start, end) {
      for (let i = start; i < end; i++) {
        renderFrame(ctx, i / FPS, env);
        const res = await fetch(`/__frame?i=${i}`, { method: 'POST', body: ctx.getImageData(0, 0, W, H).data });
        if (!res.ok) throw new Error(`frame ${i} rejected: ${res.status} ${await res.text()}`);
        if (i % 60 === 0) console.log(`frame ${i}/${end}`);
      }
    },
  };
}

function installPlayer() {
  const play = document.querySelector<HTMLButtonElement>('#play')!;
  const scrub = document.querySelector<HTMLInputElement>('#scrub')!;
  const readout = document.querySelector<HTMLElement>('#time')!;
  const safe = document.querySelector<HTMLInputElement>('#safe')!;
  const chapters = document.querySelector<HTMLElement>('#chapters')!;
  const overlay = document.querySelector<HTMLCanvasElement>('#overlay')!;
  overlay.width = W;
  overlay.height = H;

  let audio: AudioContext | null = null;
  let source: AudioBufferSourceNode | null = null;
  let startedAt = 0;
  let playing = false;

  const draw = () => {
    renderFrame(ctx, time, env);
    scrub.value = String(Math.min(FRAMES - 1, Math.floor(time * FPS)));
    readout.textContent = `${time.toFixed(2)} s · frame ${Math.floor(time * FPS)} · beat ${(time / BEAT).toFixed(2)}`;
  };
  const start = () => {
    audio ??= new AudioContext({ sampleRate: soundtrack.sampleRate });
    source = audio.createBufferSource();
    source.buffer = soundtrack;
    source.connect(audio.destination);
    source.start(0, time);
    startedAt = audio.currentTime - time;
    playing = true;
    play.textContent = 'Pause';
    requestAnimationFrame(tick);
  };
  const stop = () => {
    playing = false;
    source?.stop();
    source = null;
    play.textContent = 'Play';
  };
  const tick = () => {
    if (!playing || !audio) return;
    time = audio.currentTime - startedAt;
    if (time >= DURATION) {
      // Reels loop, so the preview does too.
      stop();
      time = 0;
      start();
      return;
    }
    draw();
    requestAnimationFrame(tick);
  };
  const seek = (t: number) => {
    const resume = playing;
    if (playing) stop();
    time = Math.max(0, Math.min(DURATION - 1 / FPS, t));
    draw();
    if (resume) start();
  };

  play.disabled = false;
  play.onclick = () => (playing ? stop() : start());
  scrub.oninput = () => seek(Number(scrub.value) / FPS);
  for (const [name, [beat]] of Object.entries(SCENE)) {
    const button = document.createElement('button');
    button.textContent = name;
    button.onclick = () => seek(b(beat));
    chapters.append(button);
  }
  window.addEventListener('keydown', (e) => {
    if (e.code === 'Space') {
      e.preventDefault();
      if (playing) stop();
      else start();
    } else if (e.code === 'ArrowRight' || e.code === 'ArrowLeft') {
      seek(time + (e.code === 'ArrowRight' ? 1 : -1) / FPS);
    }
  });
  safe.onchange = () => drawSafeZones(overlay, safe.checked);
  draw();
}

/** Instagram UI overlays and the 3:4 profile-grid crop, for layout checks only. */
function drawSafeZones(overlay: HTMLCanvasElement, show: boolean) {
  const o = overlay.getContext('2d')!;
  o.clearRect(0, 0, W, H);
  if (!show) return;
  o.fillStyle = 'rgba(0,150,255,0.22)';
  o.fillRect(0, 0, W, 220);
  o.fillRect(0, 1500, W, H - 1500);
  o.fillRect(940, 900, 140, 600);
  o.setLineDash([14, 10]);
  o.lineWidth = 4;
  o.strokeStyle = 'rgba(255,220,0,0.9)';
  o.strokeRect(2, 240, W - 4, 1440);
  o.strokeStyle = 'rgba(0,255,140,0.9)';
  o.strokeRect(SAFE.left, SAFE.top, SAFE.right - SAFE.left, SAFE.bottom - SAFE.top);
}

boot().catch((error) => {
  status.textContent = `Failed: ${error}`;
  console.error(error);
});
