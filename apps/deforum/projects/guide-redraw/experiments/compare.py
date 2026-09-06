"""Make an immutable local comparison from collected redraw and feedback runs."""

import argparse
import datetime
import json
from pathlib import Path

from PIL import Image, ImageDraw

import redraw
import editing


def compare(run, feedback):
    run, feedback = run.resolve(), feedback.resolve()
    receipt = json.loads((run / 'submission.json').read_text())
    other = json.loads((feedback / 'submission.json').read_text())
    if run.parent != (redraw.PROJECT / 'runs').resolve():
        raise ValueError('Redraw must be this project\'s collected run')
    if not receipt.get('collected_at') or not other.get('collected_at'):
        raise ValueError('Collect both runs first')
    if other.get('phase') != 'feedback' or receipt.get('phase') != 'independent-redraw':
        raise ValueError('Require independent redraw and sequential feedback')
    if not receipt.get('reference_sha256') or other.get('parent_sha256') != receipt['reference_sha256']:
        raise ValueError('Comparison must share the exact original reference')
    stamp = datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
    folder = redraw.PROJECT / 'exports' / f'{stamp}-comparison'
    frames = folder / 'frames'
    frames.mkdir(parents=True, exist_ok=False)
    rows = receipt['frame_map']
    contact = Image.new('RGB', (4 * 320, 6 * 204), '#171717')
    mapping = []
    for i, row in enumerate(rows):
        guide = Path(receipt['input_bundle']) / row['local']
        sources = [guide, run / 'frames' / f'{i:04d}.png',
                   feedback / 'frames' / f'{row["guide_frame"]:04d}.png']
        triptych = Image.new('RGB', (3 * 640, 384), '#171717')
        records = []
        for column, (label, source) in enumerate(zip(['Guide', 'Independent redraw', 'Feedback'], sources)):
            with Image.open(source) as im:
                if im.size != (receipt['width'], receipt['height']):
                    raise ValueError('Comparison dimensions differ')
                triptych.paste(im.resize((640, 360), Image.Resampling.LANCZOS), (column * 640, 24))
                x, y = (i % 4) * 320, ((i // 4) * 3 + column) * 204
                contact.paste(im.resize((320, 180), Image.Resampling.LANCZOS), (x, y + 24))
            caption = f'{label} | guide {row["guide_frame"]:02d}'
            ImageDraw.Draw(triptych).text((column * 640 + 8, 6), caption, fill='white')
            ImageDraw.Draw(contact).text((x + 8, y + 6), caption, fill='white')
            records.append({'label': label, 'source': str(source), 'sha256': redraw.digest(source)})
        triptych.save(frames / f'{i:04d}.png')
        mapping.append({'frame': i, 'guide_frame': row['guide_frame'], 'sources': records})
    contact.save(folder / 'contact.png')
    redraw.write_json(folder / 'comparison.json', {
        'redraw_run': str(run), 'feedback_run': str(feedback), 'frames': mapping,
        'generated_fps': 8, 'delivery_fps': 24,
        'layout': 'guide, independent redraw, feedback from left to right',
        'caveats': 'Feedback frame zero is unmodified. Workflows differ in noise/color/sharpen controls.'})
    editing.encode(frames, folder / 'preview.mp4')
    return folder


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--redraw-run', required=True, type=Path)
    parser.add_argument('--feedback-run', required=True, type=Path)
    args = parser.parse_args()
    print(compare(args.redraw_run, args.feedback_run))
