"""Build a reusable linked-video review from local media; no server or GPU required."""
import argparse
import base64
import html
import json
import math
from pathlib import Path
import subprocess

from video_review import attach_provenance, probe, sha256

APP = Path(__file__).resolve().parent
ASSETS = APP / 'media_review'
INLINE_LIMIT = 1_000_000


def validate_session(data):
    clips = data.get('clips', [])
    ids = [item['id'] for item in clips]
    if not ids or len(ids) != len(set(ids)):
        raise ValueError('Clip IDs must be nonempty and unique')
    selected = data.get('selected', ids[:2])
    if not 1 <= len(selected) <= 3 or len(set(selected)) != len(selected) or any(i not in ids for i in selected):
        raise ValueError('Select one to three distinct existing clips')
    return selected


def same_timeline(original, preview):
    if original['frame_count'] != preview['frame_count'] or any(
        abs(a['time_seconds'] - b['time_seconds']) > 1e-5
        for a, b in zip(original['frames'], preview['frames'])
    ):
        raise ValueError('Preview changed frame count or timing')


def data_uri(path):
    return 'data:video/mp4;base64,' + base64.b64encode(path.read_bytes()).decode('ascii')


def fragment(data):
    encoded = json.dumps(data, separators=(',', ':'), ensure_ascii=True).replace('<', '\\u003c')
    return (ASSETS.joinpath('viewer.html').read_text()
            .replace('__REVIEW_DATA__', encoded)
            .replace('__REVIEW_TIMELINE__', ASSETS.joinpath('timeline.js').read_text())
            .replace('__REVIEW_CONTROLLER__', ASSETS.joinpath('viewer.js').read_text()))


def check_inline_size(text):
    if len(text.encode()) >= INLINE_LIMIT:
        raise ValueError('Inline review exceeds 1 MB. Choose fewer/shorter clips or a smaller --width; full-quality sources are unchanged.')


def build(session, output, inline, width=480, crf=30):
    data = json.loads(session.read_text())
    selected = validate_session(data)
    output.mkdir(parents=True, exist_ok=True)
    cache = APP / 'work/media-review/cache'
    cache.mkdir(parents=True, exist_ok=True)
    compact, originals, receipts = [], [], []
    for item in data['clips']:
        source = (APP / item['source']).resolve()
        if source.suffix.lower() != '.mp4':
            raise ValueError('This first viewer supports MP4 sources')
        digest = sha256(source)
        info = probe(source)
        rows = [dict(row) for row in info['frames']]
        provenance = attach_provenance(source, digest, info, rows)
        times = [row['time_seconds'] for row in rows]
        duration = float(info['stream']['duration'])
        if not math.isfinite(duration) or duration <= times[-1]:
            raise ValueError('Missing or invalid video duration')
        if abs(rows[0]['pts_seconds']) > 1e-6:
            raise ValueError('Review sources must start at timestamp zero; normalize a separate copy first')
        target = cache / f'{digest}-{width}-crf{crf}.mp4'
        if not target.exists():
            partial = target.with_suffix('.partial.mp4')
            subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', str(source), '-map', '0:v:0', '-an',
                            '-vf', f'scale={width}:-2,setpts=PTS-STARTPTS', '-c:v', 'libx264',
                            '-crf', str(crf), '-preset', 'medium', '-pix_fmt', 'yuv420p',
                            '-fps_mode', 'passthrough', '-enc_time_base', info['stream']['time_base'],
                            '-movflags', '+faststart', str(partial)], check=True)
            same_timeline(info, probe(partial))
            partial.replace(target)
        preview_info = probe(target)
        same_timeline(info, preview_info)
        if abs(float(preview_info['stream']['duration']) - duration) > 1e-5:
            raise ValueError('Preview changed duration')
        subprocess.run(['ffmpeg', '-v', 'error', '-xerror', '-i', str(target), '-f', 'null', '-'], check=True, capture_output=True)
        clip = {k: item[k] for k in ('id', 'label', 'note')}
        clip.update(times=times, duration=duration,
                    roles=[row.get('provenance') for row in rows],
                    anchors=[i for i, row in enumerate(rows) if row.get('provenance', {}).get('kind') == 'anchor'])
        compact.append({**clip, 'src': data_uri(target)})
        originals.append({**clip, 'src': data_uri(source)})
        if sha256(source) != digest:
            raise ValueError('Source changed during review build')
        receipts.append({'id': item['id'], 'source': str(source), 'source_sha256': digest,
                         'frame_count': len(times), 'duration': duration, 'paintings': len(clip['anchors']),
                         'dimensions': [info['stream']['width'], info['stream']['height']],
                         'provenance': provenance, 'preview': str(target), 'preview_sha256': sha256(target),
                         'preview_bytes': target.stat().st_size, 'preview_dimensions': [preview_info['stream']['width'], preview_info['stream']['height']]})
    common = {'title': data['title'], 'selected': selected}
    small = fragment({**common, 'clips': compact, 'quality': f'{width}px compressed previews · same frames and timing'})
    check_inline_size(small)
    full = fragment({**common, 'clips': originals, 'quality': 'Original video files · full resolution'})
    # Standalone document is separate from the size-limited conversation fragment.
    page = ASSETS.joinpath('standalone.html').read_text().replace('__TITLE__', html.escape(data['title'])).replace('__FRAGMENT__', full)
    full_path = output / 'full-quality.html'
    full_path.write_text(page)
    inline.parent.mkdir(parents=True, exist_ok=True)
    inline.write_text(small)
    receipt = {'session': str(session.resolve()), 'session_sha256': sha256(session), 'clips': receipts,
               'inline': str(inline), 'inline_bytes': len(small.encode()), 'inline_sha256': sha256(inline),
               'full_quality': str(full_path), 'full_quality_sha256': sha256(full_path)}
    (output / 'receipt.json').write_text(json.dumps(receipt, indent=2) + '\n')
    return {'inline': str(inline), 'inline_bytes': len(small.encode()), 'full_quality': str(full_path)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('session', type=Path)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--inline', required=True, type=Path)
    parser.add_argument('--width', type=int, default=480)
    parser.add_argument('--crf', type=int, default=30)
    args = parser.parse_args()
    if args.width < 128 or args.width % 2 or not 0 <= args.crf <= 51:
        parser.error('Use an even width >=128 and CRF between 0 and 51')
    print(json.dumps(build(args.session, args.output.resolve(), args.inline.resolve(), args.width, args.crf), indent=2))


if __name__ == '__main__':
    main()
