"""Export preserved full/cropped views and measure raw guide coverage.

Run with uv run --with pillow --with numpy python .../review.py GUIDE FEEDBACK.
Arguments are collected run names in this project. Exports never overwrite.
"""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess

import numpy as np
from PIL import Image, ImageDraw

PROJECT = Path(__file__).resolve().parents[1]
BOX = (128, 72, 1152, 648)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('guide')
    parser.add_argument('feedback')
    args = parser.parse_args()
    runs = {}
    for kind, name in vars(args).items():
        run = (PROJECT / 'runs' / name).resolve()
        if run.parent != (PROJECT / 'runs').resolve():
            raise ValueError('Expected a run in this project')
        receipt = json.loads((run / 'submission.json').read_text())
        if not receipt.get('collected_at'):
            raise ValueError('Run is not collected')
        runs[kind] = run
    target = PROJECT / 'exports' / ('overscan-' + args.feedback)
    target.mkdir(exist_ok=False)
    evidence = {'crop_xyxy': BOX, 'source_fps': 8, 'delivery_fps': 24, 'runs': {}}
    for kind, run in runs.items():
        frames = sorted((run / 'frames').glob('*.png'))
        evidence['runs'][kind] = {'run': run.name, 'frames': [
            {'file': p.name, 'sha256': hashlib.sha256(p.read_bytes()).hexdigest()}
            for p in frames]}
        subprocess.run(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-n',
            '-framerate', '8', '-i', str(run / 'frames/%04d.png'),
            '-filter_complex', '[0:v]split=2[a][b];[a]scale=640:360[a1];'
            '[b]crop=1024:576:128:72,scale=640:360[b1];'
            '[a1][b1]hstack,fps=24[out]', '-map', '[out]',
            '-c:v', 'libx264', '-crf', '18', '-pix_fmt', 'yuv420p',
            str(target / f'{kind}-full-left-crop-right.mp4')], check=True)
        subprocess.run(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-n',
            '-framerate', '8', '-i', str(run / 'frames/%04d.png'),
            '-vf', 'crop=1024:576:128:72,fps=24', '-c:v', 'libx264',
            '-crf', '18', '-pix_fmt', 'yuv420p',
            str(target / f'{kind}-crop.mp4')], check=True)
    masks = sorted(runs['guide'].glob('cloud/*/34/*.png'))
    if len(masks) != 24:
        raise ValueError(f'Expected one 24-frame guide coverage set, found {len(masks)}')
    coverage = []
    for i, path in enumerate(masks):
        mask = np.array(Image.open(path).convert('L')) / 255
        crop = mask[72:648, 128:1152]
        border = np.ones(mask.shape, dtype=bool)
        border[72:648, 128:1152] = False
        coverage.append({'frame': i, 'full_uncovered_fraction': float((1-mask).mean()),
            'crop_uncovered_fraction': float((1-crop).mean()),
            'border_uncovered_fraction': float((1-mask[border]).mean())})
    evidence['coverage'] = coverage
    evidence['coverage_meaning'] = 'Raw geometric coverage, not perceptual artifact quality.'
    (target / 'review.json').write_text(json.dumps(evidence, indent=2) + '\n')
    sheet = Image.new('RGB', (1280, 3 * 390), '#171923')
    draw = ImageDraw.Draw(sheet)
    for row, frame in enumerate((0, 11, 23)):
        for col, (kind, run) in enumerate(runs.items()):
            draw.text((col*640+12, row*390+9), f'{kind} / frame {frame} / full viewport', fill='white')
            picture = Image.open(run / 'frames' / f'{frame:04d}.png').convert('RGB')
            picture.thumbnail((640, 360))
            sheet.paste(picture, (col*640, row*390+30))
    sheet.save(target / 'guide-feedback-contact.jpg', quality=92)
    print(target)
    print(json.dumps(coverage[-1], indent=2))


if __name__ == '__main__':
    main()
