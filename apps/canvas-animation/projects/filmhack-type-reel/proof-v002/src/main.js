import { parse as parseFont } from '../node_modules/opentype.js/dist/opentype.mjs';
import { W, H, FPS, BEAT, C, canvas, clamp, rng } from './util.js';
import { drawDoubt, doubtMetrics, DOUBT } from './doubt.js';
import { createYes } from './yes.js';
import { createMarqueeImage } from './marqueeImage.js';
import { createCrewsImage } from './crewsImage.js';
import { createThread } from './thread.js';

// Bars 1–3 of script v1 at 140 BPM. Times in seconds.
export const T = {
  d1: 0, yes: 2 * BEAT,
  d2: 4 * BEAT, marquee: 5 * BEAT,
  d3: 8 * BEAT, alone: 9 * BEAT, crews: 10.5 * BEAT,
  end: 14 * BEAT,
};
export const DURATION = T.end;

const load = url => fetch(url).then(r => { if (!r.ok) throw new Error(url); return r.arrayBuffer(); });
const img = url => new Promise((ok, fail) => { const i = new Image(); i.onload = () => ok(i); i.onerror = fail; i.src = url; });

const [antonBuf, doubtBuf, hershey, chromeImg, marqueeImg, crewsImg] = await Promise.all([
  load('../fonts/Anton-Regular.ttf'), load('../fonts/CormorantGaramond-Italic.ttf'),
  fetch('data/hershey-futural.json').then(r => r.json()), img('../assets/yes-chrome.png'),
  img('../assets/marquee-lit.png'), img('../assets/crews.png'),
]);
const doubtFace = new FontFace('Doubt', doubtBuf, { style: 'italic', weight: '300 700' });
await doubtFace.load(); document.fonts.add(doubtFace);
const anton = parseFont(antonBuf);

const yes = createYes({ image: chromeImg, anton });
const marquee = createMarqueeImage({ image: marqueeImg });
const thread = createThread(hershey);
const crews = createCrewsImage({ image: crewsImg, anton });

// Film grain: a few fixed tiles cycled per frame.
const R = rng(11), grain = [0, 1, 2, 3].map(() => {
  const c = canvas(540, 960), g = c.getContext('2d'), d = g.createImageData(540, 960);
  for (let i = 0; i < d.data.length; i += 4) { const v = 128 + (R() - .5) * 255; d.data[i] = d.data[i + 1] = d.data[i + 2] = v; d.data[i + 3] = 255; }
  g.putImageData(d, 0, 0); return c;
});

const cv = document.getElementById('c'), ctx = cv.getContext('2d');
const D1 = 'make a film in 48 hours?', D2 = "but I don't do AI…", D3 = "I don't have a crew";

export function renderFrame(t) {
  ctx.save();
  ctx.globalCompositeOperation = 'source-over'; ctx.globalAlpha = 1; ctx.filter = 'none';
  ctx.fillStyle = C.black; ctx.fillRect(0, 0, W, H);

  if (t < T.d2) {
    yes(ctx, t, T.yes, { accent: [T.yes + BEAT] });
    const crush = clamp((t - T.yes) * FPS / 4);
    drawDoubt(ctx, D1, t, { t0: T.d1 - .08, typeDur: .26, crush });
  } else if (t < T.d3) {
    if (t < T.marquee) drawDoubt(ctx, D2, t, { t0: T.d2, typeDur: .16 });
    marquee(ctx, t, T.marquee);
  } else if (t < T.crews) {
    drawDoubt(ctx, D3, t, { t0: T.d3, typeDur: .16, alpha: t < T.alone ? 1 : clamp(1 - (t - T.alone - .12) * 6), cursor: t < T.alone });
    thread(ctx, t, T.alone, { dur: .55, from: [DOUBT.x, DOUBT.y + 22] });
  } else {
    crews(ctx, t, T.crews, { accent: [12 * BEAT] });
  }

  // Grain and a soft vignette over everything.
  ctx.globalCompositeOperation = 'overlay'; ctx.globalAlpha = .07;
  ctx.drawImage(grain[Math.floor(t * FPS) % 4], 0, 0, W, H);
  ctx.globalCompositeOperation = 'source-over'; ctx.globalAlpha = 1;
  const v = ctx.createRadialGradient(W / 2, H / 2, H * .3, W / 2, H / 2, H * .75);
  v.addColorStop(0, 'rgba(0,0,0,0)'); v.addColorStop(1, 'rgba(0,0,0,.45)');
  ctx.fillStyle = v; ctx.fillRect(0, 0, W, H);
  ctx.restore();
}

window.renderFrame = renderFrame;
window.DURATION = DURATION;
window.TIMES = T;
window.ready = true;

if (new URLSearchParams(location.search).has('play')) {
  const start = performance.now();
  const loop = () => { renderFrame(((performance.now() - start) / 1000) % DURATION); requestAnimationFrame(loop); };
  loop();
} else renderFrame(Number(new URLSearchParams(location.search).get('t') || 1.2));
