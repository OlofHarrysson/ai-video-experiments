// Renders the picture with Remotion, then muxes the mastered soundtrack with ffmpeg.
// Remotion's own AAC track carries the encoder's 2048-sample priming as audio, which puts every hit
// 43 ms (1.3 frames) late; ffmpeg's MP4 muxer signals the priming in an edit list instead.
//
//   node scripts/render.mjs   → renders/filmhack-frenzy-v2.mp4
import { spawn } from 'node:child_process';
import { rm } from 'node:fs/promises';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const OUTPUT = 'renders/filmhack-frenzy-v2.mp4';

const ROOT = join(dirname(fileURLToPath(import.meta.url)), '..');
const PICTURE = join(ROOT, 'renders/.picture.mp4');

function run(command, args) {
  return new Promise((resolve, reject) => {
    const proc = spawn(command, args, { cwd: ROOT, stdio: 'inherit' });
    proc.on('close', (code) => (code === 0 ? resolve() : reject(new Error(`${command} exited ${code}`))));
  });
}

await run('npx', [
  'remotion', 'render', 'FilmhackFrenzy', PICTURE, '--muted',
  '--codec=h264', '--crf=17', '--x264-preset=slow', '--pixel-format=yuv420p', '--color-space=bt709', '--jpeg-quality=95',
]);
await run('ffmpeg', [
  '-hide_banner', '-loglevel', 'error', '-y', '-i', PICTURE, '-i', 'public/soundtrack.wav',
  '-map', '0:v', '-map', '1:a', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '320k', '-shortest', '-movflags', '+faststart', OUTPUT,
]);
await rm(PICTURE);
console.log(`film → ${join(ROOT, OUTPUT)}`);
