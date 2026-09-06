# /// script
# requires-python = ">=3.12"
# dependencies = ["pillow>=11,<13"]
# ///
"""Create an uncropped, labeled review sheet; preserve all source pixels/files."""

from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import uuid

from PIL import Image, ImageDraw, ImageFont, ImageOps

PROJECT = Path(__file__).resolve().parents[1]
REPO = PROJECT.parents[3]
SOURCES = [
    ('SDXL base 1.0 | parent control',
     PROJECT.parent / 'lantern-marsh/runs/20260906T214815368534Z-overscan-1f/frames/0000.png',
     '1280x720 requested | parent-owned generation'),
    ('FLUX.1 dev | documented size fields',
     PROJECT / 'runs/20260906T215105Z-flux-dev-04aa5c65/original-00.jpg',
     '1024x576 + PNG requested | $0.012 reported'),
    ('FLUX.1 dev | landscape request: still square',
     PROJECT / 'runs/20260906T215346Z-flux-dev-1ba040db/original-00.jpg',
     'aspect=landscape + PNG requested | $0.012 reported'),
    ('Seedream 4.0 | hosted T2I',
     PROJECT / 'runs/20260906T215118Z-seedream-4-f5a8fd86/original-00.jpg',
     '2048x1152 requested | $0.027 reported'),
]


def main():
    out = PROJECT / 'runs' / (datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ') +
                             '-contact-sheet-' + uuid.uuid4().hex[:8])
    out.mkdir()
    canvas = Image.new('RGB', (1600, 1160), '#12171d')
    draw = ImageDraw.Draw(canvas)
    title_font = ImageFont.load_default(size=30)
    label_font = ImageFont.load_default(size=23)
    small_font = ImageFont.load_default(size=18)
    draw.text((28, 20), 'LANTERN MARSH | preserved model samples', fill='white', font=title_font)
    draw.text((28, 62), 'Same positive prompt. Different native sizes and APIs. Full images fitted without cropping.',
              fill='#b8c4d1', font=small_font)
    manifest = []
    for i, (label, source, details) in enumerate(SOURCES):
        x, y = 28 + (i % 2) * 792, 110 + (i // 2) * 510
        with Image.open(source) as im:
            native_size, native_format = im.size, im.format
            preview = ImageOps.contain(im.convert('RGB'), (750, 390), Image.Resampling.LANCZOS)
        draw.text((x, y), label, fill='white', font=label_font)
        draw.text((x, y + 31), f'Actual: {native_size[0]}x{native_size[1]} {native_format}',
                  fill='#a8d8ec', font=small_font)
        draw.text((x, y + 55), details, fill='#b8c4d1', font=small_font)
        draw.rectangle((x, y + 86, x + 750, y + 476), fill='#090c10')
        canvas.paste(preview, (x + (750 - preview.width) // 2,
                               y + 86 + (390 - preview.height) // 2))
        manifest.append({'label': label, 'source': str(source.relative_to(REPO)),
                         'sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
                         'native_size': native_size, 'native_format': native_format})
    draw.text((28, 1130), 'Static review only: no evidence here of temporal stability, img2img denoise control or animation cost.',
              fill='#b8c4d1', font=small_font)
    canvas.save(out / 'contact-sheet.png')
    (out / 'sources.json').write_text(json.dumps(manifest, indent=2) + '\n')
    print(out / 'contact-sheet.png')


if __name__ == '__main__':
    main()
