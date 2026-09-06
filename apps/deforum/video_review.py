"""Inspect decoded video frames without changing the source or earlier reviews."""

import argparse
from bisect import bisect_right
from datetime import datetime, timezone
from fractions import Fraction
import hashlib
import json
import math
from pathlib import Path
import re
import subprocess


def command(args):
    return subprocess.run(args, check=True, capture_output=True, text=True).stdout


def sha256(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def timestamp(value):
    """Accept seconds or HH:MM:SS / MM:SS; reject non-finite values."""
    parts = str(value).split(':')
    if not 1 <= len(parts) <= 3:
        raise ValueError(f'Invalid timestamp: {value}')
    numbers = [float(part) for part in parts]
    if not all(math.isfinite(n) for n in numbers):
        raise ValueError('Timestamps must be finite')
    if len(parts) > 1 and (any(n < 0 for n in numbers)
                           or any(n >= 60 for n in numbers[1:])):
        raise ValueError(f'Invalid clock timestamp: {value}')
    return sum(n * 60 ** i for i, n in enumerate(reversed(numbers)))


def probe(source):
    data = json.loads(command([
        'ffprobe', '-v', 'error', '-select_streams', 'v:0',
        '-show_streams', '-show_frames', '-show_format',
        '-show_entries',
        'stream=index,width,height,time_base,avg_frame_rate,r_frame_rate,start_time,duration:'
        'frame=best_effort_timestamp:format=duration,format_name',
        '-of', 'json', str(source)]))
    if not data.get('streams') or not data.get('frames'):
        raise ValueError('Source must contain decodable video frames')
    stream = data['streams'][0]
    time_base = Fraction(stream['time_base'])
    try:
        pts = [int(frame['best_effort_timestamp']) for frame in data['frames']]
    except (KeyError, TypeError, ValueError) as error:
        raise ValueError('Missing decoded frame timestamps; refusing guessed labels') from error
    if any(b <= a for a, b in zip(pts, pts[1:])):
        raise ValueError('Video frame timestamps must be strictly increasing')
    frames = [{'frame_number': n, 'pts': p,
               'pts_seconds': float(p * time_base),
               'time_seconds': float((p - pts[0]) * time_base)}
              for n, p in enumerate(pts)]
    return {'stream': stream, 'format': data.get('format', {}),
            'frame_count': len(frames), 'first_pts': pts[0], 'frames': frames}


def detect_scenes(source, frame_count, threshold, limit):
    """FFmpeg pixel-change scores; every frame passes so n stays source-indexed."""
    output = command([
        'ffmpeg', '-hide_banner', '-loglevel', 'error', '-noautorotate',
        '-i', str(source), '-map', '0:v:0', '-an',
        '-vf', r'select=gte(scene\,0),metadata=mode=print:key=lavfi.scene_score:file=-',
        '-fps_mode', 'passthrough', '-f', 'null', '-'])
    current = None
    scores = {}
    for line in output.splitlines():
        match = re.match(r'frame:\s*(\d+)', line)
        if match:
            current = int(match[1])
        elif line.startswith('lavfi.scene_score=') and current is not None:
            scores[current] = float(line.split('=', 1)[1])
    if set(scores) != set(range(frame_count)):
        raise ValueError('Scene-score frame inventory differs from ffprobe; refusing mislabeled frames')
    candidates = [{'frame_number': n, 'score': score}
                  for n, score in scores.items() if n > 0 and score > threshold]
    selected = sorted(sorted(candidates, key=lambda row: (-row['score'], row['frame_number']))[:limit],
                      key=lambda row: row['frame_number'])
    return {'method': 'FFmpeg scene score: pixel-change heuristic, not semantic event detection',
            'threshold': threshold, 'candidate_count': len(candidates),
            'max_scenes': limit, 'selected': selected}


def choose_frames(frames, times, events, overview, before, after, scenes):
    timeline = [frame['time_seconds'] for frame in frames]
    selected = {}

    def add(value, reason):
        clamped = min(max(value, 0.0), timeline[-1])
        index = max(0, bisect_right(timeline, clamped) - 1)
        row = selected.setdefault(index, {**frames[index], 'requests': []})
        row['requests'].append({'reason': reason, 'requested_seconds': value,
                                'clamped_seconds': clamped, 'was_clamped': value != clamped})

    for i in range(overview):
        add(timeline[-1] * i / max(overview - 1, 1), f'overview {i + 1}/{overview}')
    for value in times:
        add(value, 'explicit timestamp')
    markers = [(value, f'event: {name}') for name, value in events]
    markers += [(timeline[row['frame_number']], f"scene candidate: score {row['score']:.3f}")
                for row in scenes.get('selected', [])]
    for value, label in markers:
        add(value, label)
        if before:
            add(value - before, f'{label} / before')
        if after:
            add(value + after, f'{label} / after')
    if not selected:
        raise ValueError('No frames selected; request timestamps, events, or an overview')
    return [selected[index] for index in sorted(selected)]


def new_version(root):
    root.mkdir(parents=True, exist_ok=True)
    version = 1
    while True:
        target = root / f'v{version:03d}'
        try:
            target.mkdir()
            return target
        except FileExistsError:
            version += 1


def contact_sheet(target, rows, columns=3):
    from PIL import Image, ImageDraw, ImageFont, ImageOps

    columns = min(columns, len(rows))
    tile_width, image_height, footer = 384, 216, 70
    height = math.ceil(len(rows) / columns) * (image_height + footer)
    sheet = Image.new('RGB', (columns * tile_width, height), '#141821')
    draw = ImageDraw.Draw(sheet)
    font = ImageFont.load_default(size=14)
    for i, row in enumerate(rows):
        x = i % columns * tile_width
        y = i // columns * (image_height + footer)
        with Image.open(target / row['file']) as frame:
            thumbnail = ImageOps.contain(frame.convert('RGB'), (tile_width, image_height))
            sheet.paste(thumbnail, (x + (tile_width - thumbnail.width) // 2,
                                   y + (image_height - thumbnail.height) // 2))
        label = f"{row['time_seconds']:.6f}s | frame {row['frame_number']}"
        draw.text((x + 8, y + image_height + 5), label, font=font, fill='white')
        reasons = '; '.join(request['reason'] for request in row['requests'])
        # Full labels, requests and exact rational time base remain in review.json.
        draw.text((x + 8, y + image_height + 26), reasons[:44], font=font, fill='#c0c8d6')
        if len(reasons) > 44:
            draw.text((x + 8, y + image_height + 44), reasons[44:85] + '...', font=font, fill='#c0c8d6')
    sheet.save(target / 'contact-sheet.jpg', quality=92)


def review(source, *, output_root=None, times=(), events=(), overview=6,
           before=.25, after=.25, scene_threshold=None, max_scenes=12, columns=3):
    source = Path(source).resolve(strict=True)
    if overview < 0 or max_scenes < 1 or columns < 1:
        raise ValueError('Overview must be nonnegative; max-scenes and columns must be positive')
    if not all(math.isfinite(t) for t in [*times, *(t for _, t in events), before, after]):
        raise ValueError('Timestamps and context must be finite')
    if min(before, after) < 0:
        raise ValueError('Before/after context must be nonnegative')
    if scene_threshold is not None and not 0 <= scene_threshold <= 1:
        raise ValueError('Scene threshold must be between 0 and 1')
    digest = sha256(source)
    info = probe(source)
    scenes = (detect_scenes(source, info['frame_count'], scene_threshold, max_scenes)
              if scene_threshold is not None else {'method': 'disabled', 'selected': []})
    rows = choose_frames(info['frames'], times, events, overview, before, after, scenes)
    # Import before creating a version so a missing optional dependency leaves no partial review.
    from PIL import Image  # noqa: F401
    target = new_version(Path(output_root).resolve() if output_root else source.parent / 'reviews' / source.stem)
    (target / 'frames').mkdir()
    expression = '+'.join(f"eq(n\\,{row['frame_number']})" for row in rows)
    command(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-n', '-noautorotate',
             '-i', str(source), '-map', '0:v:0', '-an', '-vf', f'select={expression}',
             '-fps_mode', 'passthrough', '-start_number', '0',
             str(target / 'frames' / '%06d.png')])
    extracted = sorted((target / 'frames').glob('*.png'))
    if len(extracted) != len(rows):
        raise ValueError('Extracted frame count differs from selection')
    for row, path in zip(rows, extracted):
        row.update(file=path.relative_to(target).as_posix(), sha256=sha256(path))
    if sha256(source) != digest:
        raise RuntimeError('Source changed during review; results cannot be certified')
    contact_sheet(target, rows, columns=columns)
    info.pop('frames')
    metadata = {'schema_version': 1, 'created_at': datetime.now(timezone.utc).isoformat(),
                'source': str(source), 'source_sha256': digest, 'source_unchanged': True,
                'media': info, 'time_origin': 'first displayed video frame PTS',
                'selection_rule': 'frame displayed at requested time (at or before); clamp to first/last frame PTS',
                'frame_numbering': 'zero-based decoded source video frames; not generation frame IDs',
                'pixel_policy': 'full decoded frames, no resize, interpolation or autorotation; PNG color conversion may occur',
                'scene_detection': scenes, 'frames': rows,
                'contact_sheet': 'contact-sheet.jpg',
                'review_limit': 'Samples support visual inspection; do not establish playback quality or semantic understanding'}
    with (target / 'review.json').open('x') as stream:
        json.dump(metadata, stream, indent=2)
        stream.write('\n')
    return target


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('video', type=Path)
    parser.add_argument('--output-root', type=Path, help='Parent of new v001, v002, ... directories')
    parser.add_argument('--at', action='append', default=[], help='Seconds or HH:MM:SS; repeatable')
    parser.add_argument('--event', action='append', default=[], metavar='NAME=TIME',
                        help='User-named timestamp, with before/after context; repeatable')
    parser.add_argument('--overview', type=int, default=6, help='Evenly spaced samples (default 6; 0 disables)')
    parser.add_argument('--columns', type=int, default=3, help='Contact-sheet columns; use 6 for an overview strip')
    parser.add_argument('--before', type=float, default=.25, help='Seconds before each event/candidate')
    parser.add_argument('--after', type=float, default=.25, help='Seconds after each event/candidate')
    parser.add_argument('--scene-threshold', type=float, help='Opt-in FFmpeg pixel-change threshold, 0..1 (try 0.3)')
    parser.add_argument('--max-scenes', type=int, default=12, help='Keep strongest candidates, then order by time')
    args = parser.parse_args()
    try:
        events = []
        for event in args.event:
            name, sep, value = event.rpartition('=')
            if not sep or not name.strip():
                raise ValueError('Events require NAME=TIME')
            events.append((name.strip(), timestamp(value)))
        target = review(args.video, output_root=args.output_root,
                        times=[timestamp(t) for t in args.at], events=events,
                        overview=args.overview, before=args.before, after=args.after,
                        scene_threshold=args.scene_threshold, max_scenes=args.max_scenes, columns=args.columns)
    except (ValueError, OSError, subprocess.CalledProcessError) as error:
        parser.exit(1, f'Review failed: {error}\n{getattr(error, "stderr", "") or ""}')
    print(json.dumps({'review_dir': str(target), 'contact_sheet': str(target / 'contact-sheet.jpg'),
                      'metadata': str(target / 'review.json')}, indent=2))


if __name__ == '__main__':
    main()
