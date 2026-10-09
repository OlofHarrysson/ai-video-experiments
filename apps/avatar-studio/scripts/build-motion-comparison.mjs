import { execFileSync } from 'node:child_process';
import { mkdirSync, writeFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { join } from 'node:path';

// Local postproduction only; generation is a separate, budgeted operation.
const DIR = fileURLToPath(new URL('../.private/motion/', import.meta.url));
const NAMES = ['source', 'styled'];
const WIDTH = 960;
const HEIGHT = 720;
const FPS = 30;
const CHECKPOINTS = [0, 1.5, 1.7, 2.0667, 2.4333, 2.8, 3.7, 5, 5.6, 6.2667, 7.2, 7.8];
const run = (command, args) => execFileSync(command, args, { encoding: 'utf8', maxBuffer: 4 * 1024 * 1024 });
const ffmpeg = args => run('ffmpeg', ['-hide_banner', '-loglevel', 'error', '-y', ...args]);
mkdirSync(join(DIR, 'checkpoints'), { recursive: true });
const metadata = Object.fromEntries(NAMES.map(name => [name, JSON.parse(run('ffprobe', [
  '-v', 'error', '-show_streams', '-show_format', '-of', 'json', join(DIR, name + '.mp4'),
]))]));
const durations = Object.values(metadata).map(m => Number(m.streams.find(s => s.codec_type === 'video').duration));
if (durations.some(d => !Number.isFinite(d) || d < 3)) throw new Error('Missing or invalid video duration.');
const duration = Math.min(...durations);
const filters = NAMES.map((_, i) => `[${i}:v]setpts=PTS-STARTPTS,fps=${FPS},scale=${WIDTH}:${HEIGHT}:force_original_aspect_ratio=decrease,pad=${WIDTH}:${HEIGHT}:(ow-iw)/2:(oh-ih)/2:color=0xf4f1ea,setsar=1[v${i}]`);
filters.push('[v0][v1]hstack=inputs=2:shortest=1[comparison]');
ffmpeg([
  ...NAMES.flatMap(name => ['-i', join(DIR, name + '.mp4')]),
  '-filter_complex', filters.join(';'), '-map', '[comparison]', '-an', '-t', String(duration),
  '-c:v', 'libx264', '-crf', '19', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', join(DIR, 'comparison.mp4'),
]);
ffmpeg(['-ss', '2', '-i', join(DIR, 'comparison.mp4'), '-frames:v', '1', join(DIR, 'comparison-poster.jpg')]);
for (const name of NAMES) ffmpeg([
  '-i', join(DIR, name + '.mp4'), '-vf', 'fps=2,scale=400:-2,tile=4x4',
  '-frames:v', '1', join(DIR, name + '-contact.jpg'),
]);
for (const [i, time] of CHECKPOINTS.entries()) ffmpeg([
  '-ss', String(time), '-i', join(DIR, 'comparison.mp4'), '-vf', 'scale=1280:-2',
  '-frames:v', '1', join(DIR, 'checkpoints', String(i).padStart(2, '0') + '.jpg'),
]);
ffmpeg([
  '-framerate', '1', '-i', join(DIR, 'checkpoints', '%02d.jpg'), '-vf', 'scale=640:-2,tile=3x4',
  '-frames:v', '1', join(DIR, 'checkpoint-contact.jpg'),
]);
writeFileSync(join(DIR, 'media-metadata.json'), JSON.stringify({
  comparison: { duration_seconds: duration, fps: FPS, width: WIDTH * 2, height: HEIGHT, audio: false,
    image: 'Full frames fitted into equal 960x720 panels with padding; no crop. Source left, Kling right.',
    timing: 'Both clips start at their own first frame; no time scaling or motion correction. 30fps display duplicates frames when needed. Comparison ends at shorter input.',
    checkpoint_seconds: CHECKPOINTS },
  inputs: metadata,
}, null, 2) + '\n');
console.log(JSON.stringify({ path: join(DIR, 'comparison.mp4'), duration, inputDurations: durations }));
