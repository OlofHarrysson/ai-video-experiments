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


def detect_scenes(source, frame_count, threshold, limit, *, timeline=None, min_gap=0):
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
    selected = []
    for row in sorted(candidates, key=lambda row: (-row['score'], row['frame_number'])):
        if timeline is not None and any(abs(timeline[row['frame_number']] - timeline[prior['frame_number']])
                                        < min_gap for prior in selected):
            continue
        selected.append(row)
        if len(selected) == limit:
            break
    selected.sort(key=lambda row: row['frame_number'])
    return {'method': 'FFmpeg scene score: pixel-change heuristic, not semantic event detection',
            'threshold': threshold, 'candidate_count': len(candidates),
            'max_scenes': limit, 'min_gap_seconds': min_gap, 'selected': selected}


def choose_frames(frames, times, events, overview, before, after, scenes, windows=()):
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
    for start, end in windows:
        if end < start:
            raise ValueError('Window end must be at or after its start')
        first = max(0, bisect_right(timeline, min(max(start, 0), timeline[-1])) - 1)
        last = max(0, bisect_right(timeline, min(max(end, 0), timeline[-1])) - 1)
        label = f'window {start:g}-{end:g}s: every displayed frame'
        add(start, f'{label} / start')
        for index in range(first + 1, last):
            add(timeline[index], label)
        add(end, f'{label} / end')
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


def contact_sheet(target, rows, columns=3, filename='contact-sheet.jpg'):
    from PIL import Image, ImageDraw, ImageFont, ImageOps

    columns = min(columns, len(rows))
    tile_width, image_height, footer = 384, 216, 70
    height = math.ceil(len(rows) / columns) * (image_height + footer)
    sheet = Image.new('RGB', (columns * tile_width, height), '#141821')
    draw = ImageDraw.Draw(sheet)
    font = ImageFont.load_default(size=14)

    def fit(text):
        if draw.textlength(text, font=font) <= tile_width - 16:
            return text
        while text and draw.textlength(text + '...', font=font) > tile_width - 16:
            text = text[:-1]
        return text + '...'

    for i, row in enumerate(rows):
        x = i % columns * tile_width
        y = i // columns * (image_height + footer)
        with Image.open(target / row['file']) as frame:
            thumbnail = ImageOps.contain(frame.convert('RGB'), (tile_width, image_height))
            sheet.paste(thumbnail, (x + (tile_width - thumbnail.width) // 2,
                                   y + (image_height - thumbnail.height) // 2))
        prefix = f"{row['video_label']} | " if row.get('video_label') else ''
        label = f"{prefix}{row['time_seconds']:.6f}s | frame {row['frame_number']}"
        draw.text((x + 8, y + image_height + 5), fit(label), font=font, fill='white')
        reasons = '; '.join(request['reason'] for request in row['requests'])
        # Full labels, requests and exact rational time base remain in review.json.
        lines = [row['provenance_label'], reasons] if row.get('provenance_label') else [reasons]
        for offset, text in zip((26, 44), lines):
            draw.text((x + 8, y + image_height + offset), fit(text), font=font, fill='#c0c8d6')
    sheet.save(target / filename, quality=92)


def extract(source, target, rows, subdirectory):
    """Decode each selected frame once; comparison rows may reuse a held frame."""
    folder = target / subdirectory
    folder.mkdir()
    indices = sorted({row['frame_number'] for row in rows})
    expression = '+'.join(f"eq(n\\,{index})" for index in indices)
    command(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-n', '-noautorotate',
             '-i', str(source), '-map', '0:v:0', '-an', '-vf', f'select={expression}',
             '-fps_mode', 'passthrough', '-start_number', '0', str(folder / '%06d.png')])
    extracted = sorted(folder.glob('*.png'))
    if len(extracted) != len(indices):
        raise ValueError('Extracted frame count differs from selection')
    mapping = {index: {'file': path.relative_to(target).as_posix(), 'sha256': sha256(path)}
               for index, path in zip(indices, extracted)}
    for row in rows:
        row.update(mapping[row['frame_number']])


def attach_provenance(source, digest, info, rows):
    """Only label RIFE frame roles when its manifest binds this exact video/timeline."""
    path = source.parent / 'manifest.json'
    if not path.is_file():
        return {'status': 'unavailable'}
    data = json.loads(path.read_text())
    output = data.get('output_frames', [])
    if data.get('status') != 'complete' or data.get('video_sha256') != digest:
        return {'status': 'unverified', 'reason': 'Manifest does not certify this exact video'}
    if (len(output) != info['frame_count'] or
            any(row.get('index') != frame['frame_number'] or
                not isinstance(row.get('time_seconds'), (int, float)) or
                not math.isfinite(row['time_seconds']) or
                abs(row['time_seconds'] - frame['time_seconds']) > 1e-6
                for row, frame in zip(output, info['frames']))):
        raise ValueError('Frame provenance timeline disagrees with decoded video')
    for row in rows:
        item = output[row['frame_number']]
        kind = item.get('kind')
        if kind == 'interpolation':
            left, right = item['source_pair']
            method = 'RIFE' if data.get('provenance', {}).get('model', '').startswith('RIFE') else 'In-between'
            label = f"{method} {item['timestep']} between source {left}->{right}"
        elif kind in ('anchor', 'final_hold'):
            label = f"{'Original' if kind == 'anchor' else 'Final hold'} source {item['source_index']}"
        else:
            raise ValueError(f'Unknown frame provenance kind: {kind}')
        row['provenance'] = {k: item[k] for k in ('kind', 'source_index', 'source_pair', 'timestep') if k in item}
        row['provenance_label'] = label
    return {'status': 'verified', 'manifest': str(path), 'manifest_sha256': sha256(path)}


def review(source, *, output_root=None, times=(), events=(), overview=6,
           before=.25, after=.25, scene_threshold=None, max_scenes=12, columns=None,
           windows=(), page_size=12, max_frames=64, scene_gap=.5,
           compare=None, label='A', compare_label='B'):
    source = Path(source).resolve(strict=True)
    columns = columns if columns is not None else (4 if compare else 3)
    if overview < 0 or max_scenes < 1 or columns < 1:
        raise ValueError('Overview must be nonnegative; max-scenes and columns must be positive')
    if page_size < 1 or max_frames < 1 or (compare and (columns % 2 or page_size % 2)):
        raise ValueError('Page size and max-frames must be positive; comparison columns/page size must be even')
    if not all(math.isfinite(t) for t in [*times, *(t for _, t in events), before, after, scene_gap,
                                         *(t for window in windows for t in window)]):
        raise ValueError('Timestamps and context must be finite')
    if min(before, after, scene_gap) < 0:
        raise ValueError('Before/after context and scene gap must be nonnegative')
    if scene_threshold is not None and not 0 <= scene_threshold <= 1:
        raise ValueError('Scene threshold must be between 0 and 1')
    digest = sha256(source)
    info = probe(source)
    scenes = (detect_scenes(source, info['frame_count'], scene_threshold, max_scenes,
                           timeline=[f['time_seconds'] for f in info['frames']], min_gap=scene_gap)
              if scene_threshold is not None else {'method': 'disabled', 'selected': []})
    rows = choose_frames(info['frames'], times, events, overview, before, after, scenes, windows)
    count = len(rows) * (2 if compare else 1)
    if count > max_frames:
        raise ValueError(f'Selection has {count} displayed images, exceeding --max-frames {max_frames}. '
                         'Choose fewer overview/candidate frames or shorter windows; raise the explicit budget if needed.')
    provenance = attach_provenance(source, digest, info, rows)
    comparison = None
    other_rows = []
    if compare:
        compare = Path(compare).resolve(strict=True)
        other_digest = sha256(compare)
        other_info = probe(compare)
        # Align by elapsed movie time, never by FPS or frame-number arithmetic.
        timeline = [f['time_seconds'] for f in other_info['frames']]
        intervals = [frames[-1]['time_seconds'] - frames[-2]['time_seconds']
                     for frames in (info['frames'], other_info['frames']) if len(frames) > 1]
        tolerance = max(intervals, default=1e-6)
        if abs(info['frames'][-1]['time_seconds'] - timeline[-1]) > tolerance + 1e-6:
            raise ValueError('Comparison timelines differ in length; select matching shot exports')
        for row in rows:
            at = row['time_seconds']
            index = max(0, bisect_right(timeline, at) - 1)
            other_rows.append({**other_info['frames'][index], 'comparison_time_seconds': at,
                               'requests': [{'reason': 'matched time from A', 'requested_seconds': at,
                                             'clamped_seconds': min(at, timeline[-1]),
                                             'was_clamped': at > timeline[-1]}], 'video_label': compare_label})
            row.update(video_label=label, comparison_time_seconds=at)
        other_provenance = attach_provenance(compare, other_digest, other_info, other_rows)
        comparison = {'source': str(compare), 'source_sha256': other_digest,
                      'label': compare_label, 'media': {k: v for k, v in other_info.items() if k != 'frames'},
                      'provenance': other_provenance, 'frames': other_rows,
                      'alignment': 'same elapsed time from first displayed PTS; B uses frame displayed then'}
    # Import before creating a version so a missing optional dependency leaves no partial review.
    from PIL import Image  # noqa: F401
    target = new_version(Path(output_root).resolve() if output_root else source.parent / 'reviews' / source.stem)
    extract(source, target, rows, 'frames')
    if compare:
        extract(compare, target, other_rows, 'comparison-frames')
        if sha256(compare) != other_digest:
            raise RuntimeError('Comparison source changed during review')
        comparison['source_unchanged'] = True
    if sha256(source) != digest:
        raise RuntimeError('Source changed during review; results cannot be certified')
    displayed = [item for pair in zip(rows, other_rows) for item in pair] if compare else rows
    pages = []
    for start in range(0, len(displayed), page_size):
        filename = 'contact-sheet.jpg' if not pages else f'contact-sheet-{len(pages) + 1:03d}.jpg'
        subset = displayed[start:start + page_size]
        contact_sheet(target, subset, columns=columns, filename=filename)
        pages.append({'file': filename, 'displayed_images': len(subset),
                      'frames': [{'source': r.get('video_label', 'A'), 'frame_number': r['frame_number'],
                                  'file': r['file']} for r in subset]})
    info.pop('frames')
    metadata = {'schema_version': 2, 'created_at': datetime.now(timezone.utc).isoformat(),
                'source': str(source), 'source_sha256': digest, 'source_unchanged': True,
                'media': info, 'time_origin': 'first displayed video frame PTS',
                'selection_rule': 'frame displayed at requested time (at or before); clamp to first/last frame PTS',
                'frame_numbering': 'zero-based decoded source video frames; not generation frame IDs',
                'pixel_policy': 'full decoded frames, no resize, interpolation or autorotation; PNG color conversion may occur',
                'scene_detection': scenes, 'frames': rows,
                'contact_sheet': 'contact-sheet.jpg',
                'contact_sheets': pages, 'provenance': provenance, 'comparison': comparison,
                'windows': [list(w) for w in windows], 'label': label,
                'attention_budget': {'max_displayed_images': max_frames, 'selected_images': count,
                                     'images_per_page': page_size},
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
    parser.add_argument('--window', nargs=2, action='append', default=[], metavar=('START', 'END'),
                        help='Every displayed frame from START through END, inclusive; repeatable')
    parser.add_argument('--event', action='append', default=[], metavar='NAME=TIME',
                        help='User-named timestamp, with before/after context; repeatable')
    parser.add_argument('--overview', type=int, default=6, help='Evenly spaced samples (default 6; 0 disables)')
    parser.add_argument('--columns', type=int, help='Columns: default 3, or 4 for paired comparisons')
    parser.add_argument('--page-size', type=int, default=12, help='Maximum images per contact sheet (default 12)')
    parser.add_argument('--max-frames', type=int, default=64, help='Explicit displayed-image budget, counting both sides of comparisons')
    parser.add_argument('--compare', type=Path, help='Matching shot to compare at the same elapsed timestamps')
    parser.add_argument('--label', default='A', help='Short label for the primary video')
    parser.add_argument('--compare-label', default='B', help='Short label for the comparison video')
    parser.add_argument('--before', type=float, default=.25, help='Seconds before each event/candidate')
    parser.add_argument('--after', type=float, default=.25, help='Seconds after each event/candidate')
    parser.add_argument('--scene-threshold', type=float, help='Opt-in FFmpeg pixel-change threshold, 0..1 (try 0.3)')
    parser.add_argument('--max-scenes', type=int, default=12, help='Keep strongest candidates, then order by time')
    parser.add_argument('--scene-gap', type=float, default=.5, help='Minimum seconds between selected scene candidates')
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
                        scene_threshold=args.scene_threshold, max_scenes=args.max_scenes, columns=args.columns,
                        windows=[tuple(timestamp(t) for t in window) for window in args.window],
                        page_size=args.page_size, max_frames=args.max_frames, scene_gap=args.scene_gap,
                        compare=args.compare, label=args.label, compare_label=args.compare_label)
    except (ValueError, OSError, subprocess.CalledProcessError) as error:
        parser.exit(1, f'Review failed: {error}\n{getattr(error, "stderr", "") or ""}')
    data = json.loads((target / 'review.json').read_text())
    print(json.dumps({'review_dir': str(target), 'contact_sheet': str(target / 'contact-sheet.jpg'),
                      'contact_sheets': [str(target / page['file']) for page in data['contact_sheets']],
                      'metadata': str(target / 'review.json')}, indent=2))


if __name__ == '__main__':
    main()
