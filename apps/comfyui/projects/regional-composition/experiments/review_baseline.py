# /// script
# requires-python = ">=3.12"
# dependencies = ["pillow>=11"]
# ///
"""Create comparison sheets and verify masked pixel preservation."""
import argparse
import hashlib
import json
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFont

PROJECT = Path(__file__).resolve().parents[1]


def find(folder, label):
    matches = list((folder/'outputs').glob(label+'_*.png'))
    if len(matches) != 1:
        raise ValueError(f'Expected one {label} in {folder}, got {len(matches)}')
    return matches[0]


def font(size):
    path = Path('/System/Library/Fonts/Helvetica.ttc')
    return ImageFont.truetype(str(path), size) if path.exists() else ImageFont.load_default(size=size)


def sheet(entries, columns, size, destination):
    rows = (len(entries)+columns-1)//columns
    canvas = Image.new('RGB', (columns*size, rows*(size+60)), '#18202a')
    draw = ImageDraw.Draw(canvas)
    for i, (title, path) in enumerate(entries):
        x, y = (i % columns)*size, (i//columns)*(size+60)
        draw.text((x+16, y+18), title, fill='white', font=font(22))
        with Image.open(path) as source:
            image = source.convert('RGB').resize((size, size), Image.Resampling.LANCZOS)
        canvas.paste(image, (x, y+60))
    canvas.save(destination)


def main():
    parser = argparse.ArgumentParser()
    for name in ('regional', 'noisy', 'layered'):
        parser.add_argument('--'+name, type=Path, required=True)
    parser.add_argument('--version', required=True)
    args = parser.parse_args()
    dest = PROJECT/'exports'/args.version; dest.mkdir(parents=True, exist_ok=False)
    entries = [('Regional prompting', find(args.regional, 'regional')),
               ('Noisy latent composition', find(args.noisy, 'noisy-final')),
               ('Layered: before finishing', find(args.layered, 'after-object-2')),
               ('Layered: after finishing', find(args.layered, 'layered-finished'))]
    sheet(entries, 2, 512, dest/'comparison.png')
    stages = [('Background', find(args.layered, 'background')),
              ('Add robot', find(args.layered, 'after-object-1')),
              ('Add glass tree', find(args.layered, 'after-object-2')),
              ('Finish', find(args.layered, 'layered-finished'))]
    sheet(stages, 4, 384, dest/'layered-stages.png')
    checks = []
    for i in (1, 2):
        parent = find(args.layered, 'background' if i == 1 else 'after-object-1')
        child = find(args.layered, f'after-object-{i}')
        # The feathered float mask has positive values throughout its rectangle.
        # Its 8-bit preview rounds tiny corner values to zero, so use the binary
        # rectangle image to represent the exact support of the composite mask.
        mask_path = find(args.layered, f'object-{i}-sampling-mask')
        with Image.open(parent) as p, Image.open(child) as c, Image.open(mask_path) as m:
            difference = ImageChops.difference(p.convert('RGB'), c.convert('RGB'))
            outside = m.convert('L').point(lambda v: 255 if v == 0 else 0).convert('RGB')
            changed = ImageChops.multiply(difference, outside).getbbox()
        checks.append({'stage': i, 'outside_mask_identical': changed is None})
        if changed is not None:
            raise AssertionError(f'Stage {i} changed pixels outside its composite mask')
    manifest = {'entries': [{'title': title, 'source': str(path.resolve().relative_to(PROJECT)),
                              'sha256': hashlib.sha256(path.read_bytes()).hexdigest()} for title, path in entries],
                'preservation_checks': checks,
                'note': 'Pixel checks verify edit boundaries, not semantic placement or visual quality.'}
    (dest/'review.json').write_text(json.dumps(manifest, indent=2)+'\n')
    print(json.dumps({'export': str(dest), 'checks': checks}))


if __name__ == '__main__':
    main()
