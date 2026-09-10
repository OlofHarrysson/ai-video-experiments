"""Verify and assemble the local RIFE scale comparison from preserved paintings."""
import hashlib
import json
from pathlib import Path
import shutil
import subprocess

from PIL import Image, ImageDraw, ImageFont

PROJECT = Path(__file__).resolve().parents[1]
BASE = PROJECT / 'exports/repaint-intervals-v001/cadence-24'
OUT = PROJECT / 'exports/rife-scale-v001'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save(path, data):
    text = json.dumps(data, indent=2) + '\n'
    if path.exists():
        assert path.read_text() == text, path
    else:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)


def copy(source, target):
    target.parent.mkdir(parents=True, exist_ok=True)
    if not target.exists():
        shutil.copy2(source, target)
    assert sha(source) == sha(target)


def encode(root, size):
    video = root / 'preview.mp4'
    if not video.exists():
        subprocess.run(['ffmpeg', '-v', 'error', '-n', '-framerate', '24', '-i',
                        str(root / 'frames/%04d.png'), '-frames:v', '144', '-an',
                        '-c:v', 'libx264', '-crf', '18', '-pix_fmt', 'yuv420p',
                        '-movflags', '+faststart', str(video)], check=True)
    stream = json.loads(subprocess.check_output(['ffprobe', '-v', 'error', '-count_frames',
                        '-select_streams', 'v:0', '-show_streams', '-of', 'json', str(video)]))['streams'][0]
    assert stream['nb_read_frames'] == '144' and stream['avg_frame_rate'] == '24/1'
    assert float(stream['duration']) == 6 and (stream['width'], stream['height']) == size
    subprocess.run(['ffmpeg', '-v', 'error', '-xerror', '-i', str(video), '-f', 'null', '-'], check=True)
    return {'frames': 144, 'fps': 24, 'duration_seconds': 6, 'size': size,
            'video_sha256': sha(video), 'full_decode_passed': True}


def main():
    raw = OUT / 'half-scale/rife-raw'
    new = json.loads((raw / 'manifest.json').read_text())
    old = json.loads((BASE / 'rife-raw/manifest.json').read_text())
    old_finished = json.loads((BASE / 'interpolated/manifest.json').read_text())
    assert new['status'] == old['status'] == 'complete'
    assert new['anchors_verified'] and new['source_hashes_and_mtimes_preserved']
    assert new['sources'] == old['sources']
    for row in new['sources']:
        assert sha(Path(row['file'])) == row['sha256']
    for key in ('commit', 'weights_sha256', 'bundle_sha256', 'code_sha256'):
        assert new['provenance'][key] == old['provenance'][key]
    ignore = {'scale', 'scale_list', 'padding'}
    assert {k:v for k,v in new['settings'].items() if k not in ignore} == {
        k:v for k,v in old['settings'].items() if k not in ignore}
    assert new['settings']['scale'] == 0.5 and old['settings']['scale'] == 1
    assert new['settings']['scale_list'] == [32,16,8,4,2]
    assert new['padding_pixels'] == old['padding_pixels'] == [0,0,0,0]
    assert len(new['output_frames']) == len(old_finished['frames']) == 144
    for row in new['output_frames']:
        assert sha(raw / row['file']) == row['sha256']
    for row in old_finished['frames']:
        assert sha(BASE / f"interpolated/frames/{row['frame']:04d}.png") == row['sha256']
    finished = OUT / 'half-scale/interpolated'
    rows = []
    for i in range(144):
        source = raw / f'frames/{i:04d}.png' if i < 120 else BASE / f'interpolated/frames/{i:04d}.png'
        target = finished / f'frames/{i:04d}.png'
        copy(source, target)
        rows.append({'frame': i, 'seconds': i/24, 'source': str(source.relative_to(PROJECT)), 'sha256': sha(target)})
    for i in range(6):
        with Image.open(finished / f'frames/{i*24:04d}.png') as frame, Image.open(BASE / f'rife-sources/{i:04d}.png') as anchor:
            assert frame.mode == anchor.mode and frame.size == anchor.size and frame.tobytes() == anchor.tobytes()
    save(finished / 'manifest.json', {'frames': rows, 'video': encode(finished, (1536,1024)),
         'anchors_pixel_identical': True, 'final_warp_identical_to_baseline': True,
         'final_warp_starts_seconds': 5, 'repaint_seconds': 1, 'feedback_generation_changed': False,
         'rife_receipt_sha256': sha(raw / 'manifest.json'), 'baseline_receipt_sha256': sha(BASE / 'interpolated/manifest.json')})
    comparison = OUT / 'comparison'
    (comparison / 'frames').mkdir(parents=True, exist_ok=True)
    font = ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc', 23)
    for i in range(144):
        canvas = Image.new('RGB', (1536,554), '#15191d')
        draw = ImageDraw.Draw(canvas)
        for x, path, label in ((0, BASE / 'interpolated', 'Current | full-scale motion estimate'),
                               (768, finished, 'Test | half-scale motion estimate')):
            with Image.open(path / f'frames/{i:04d}.png') as frame:
                canvas.paste(frame.resize((768,512), Image.Resampling.LANCZOS), (x,42))
            draw.text((x+12,9), label, font=font, fill='white')
        target = comparison / f'frames/{i:04d}.png'
        if target.exists():
            with Image.open(target) as previous:
                assert previous.tobytes() == canvas.tobytes()
        else:
            canvas.save(target)
    save(comparison / 'manifest.json', {'video': encode(comparison, (1536,554)),
         'panels': [str((BASE/'interpolated').relative_to(PROJECT)), str(finished.relative_to(PROJECT))],
         'frame_hashes': {p.name:sha(p) for p in sorted((comparison/'frames').glob('*.png'))}})
    print(json.dumps({'verified': True, 'comparison': str(comparison/'preview.mp4'),
                      'half_scale_inference_seconds': sum(new['pair_timings_seconds']),
                      'full_scale_inference_seconds': sum(old['pair_timings_seconds'])}))


if __name__ == '__main__':
    main()
