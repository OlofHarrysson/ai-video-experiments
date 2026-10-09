import { execFileSync } from 'node:child_process';
import { mkdirSync, writeFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { join } from 'node:path';

// Local postproduction only. This script never submits paid generation jobs.
const ROOT = fileURLToPath(new URL('../', import.meta.url));
const DIR = join(ROOT, '.private/restyle');
const NAMES = ['source', 'film', 'clay'];
const HEIGHT = 720;
const WIDTH = 630;
const FPS = 30;
const run = (command, args) => execFileSync(command, args, { encoding: 'utf8', maxBuffer: 4 * 1024 * 1024 });
const ffmpeg = args => run('ffmpeg', ['-hide_banner', '-loglevel', 'error', '-y', ...args]);
mkdirSync(DIR, { recursive: true });

const metadata = Object.fromEntries(NAMES.map(name => [name, JSON.parse(run('ffprobe', [
  '-v', 'error', '-show_streams', '-show_format', '-of', 'json', join(DIR, name + '.mp4'),
]))]));
const durations = Object.values(metadata).map(m => Number(m.streams.find(s => s.codec_type === 'video').duration));
if (durations.some(d => !Number.isFinite(d) || d < 3)) throw new Error('Missing or invalid video duration.');
const duration = Math.min(...durations);
const filters = NAMES.map((_, i) => `[${i}:v]setpts=PTS-STARTPTS,fps=${FPS},scale=-2:${HEIGHT},crop=${WIDTH}:${HEIGHT},setsar=1[v${i}]`);
filters.push('[v0][v1][v2]hstack=inputs=3:shortest=1[comparison]');
ffmpeg([
  ...NAMES.flatMap(name => ['-i', join(DIR, name + '.mp4')]),
  '-filter_complex', filters.join(';'), '-map', '[comparison]', '-map', '0:a:0',
  '-t', String(duration), '-c:v', 'libx264', '-crf', '19', '-pix_fmt', 'yuv420p',
  '-c:a', 'aac', '-b:a', '160k', '-movflags', '+faststart', join(DIR, 'comparison.mp4'),
]);
ffmpeg(['-ss', '2', '-i', join(DIR, 'comparison.mp4'), '-frames:v', '1', join(DIR, 'comparison-poster.jpg')]);
for (const name of NAMES) ffmpeg([
  '-i', join(DIR, name + '.mp4'), '-vf', 'fps=1,scale=480:-2,tile=4x3',
  '-frames:v', '1', join(DIR, name + '-contact.jpg'),
]);
writeFileSync(join(DIR, 'media-metadata.json'), JSON.stringify({
  comparison: { duration_seconds: duration, fps: FPS, width: WIDTH * NAMES.length, height: HEIGHT,
    audio: 'Source audio only; unchanged timing; AAC re-encoded.',
    image: 'Each video starts at its own first frame, scaled to 720px high, center cropped to 630px wide. No temporal alignment or motion correction applied.' },
  inputs: metadata,
}, null, 2));
console.log(JSON.stringify({ path: join(DIR, 'comparison.mp4'), duration, inputDurations: durations }));
