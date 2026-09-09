# /// script
# requires-python = ">=3.11"
# dependencies = ["pillow", "numpy"]
# ///
"""Extract RGB art panels; chroma removal belongs to the Blender material."""
import json
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parent
ASSETS = ROOT / 'assets'
SOURCE = ASSETS / 'rottweiler-atlas-v003.png'
PANELS = {
    'body': (50, 5, 775, 453),
    'head': (785, 30, 1260, 472),
    'ear': (1265, 80, 1475, 410),
    'front_leg': (150, 450, 440, 1000),
    'hind_leg': (605, 465, 935, 1000),
    'tail': (1025, 485, 1480, 950),
}


def main():
    image = Image.open(SOURCE).convert('RGB')
    target = ASSETS / 'rottweiler'
    target.mkdir(exist_ok=True)
    provenance = {'source': str(SOURCE), 'parts': {}}
    for name, box in PANELS.items():
        panel = image.crop(box)
        rgb = np.asarray(panel).astype(float) / 255
        key = (rgb[:, :, 0] > .65) & (rgb[:, :, 1] < .3) & (rgb[:, :, 2] > .65)
        yy, xx = np.where(~key)
        bounds = (max(0, int(xx.min())-2), max(0, int(yy.min())-2),
                  min(panel.width, int(xx.max())+3), min(panel.height, int(yy.max())+3))
        panel = panel.crop(bounds)
        output = target / f'{name}.png'
        panel.save(output)
        provenance['parts'][name] = {'panel': box, 'trim': bounds, 'size': panel.size}
    for source, name in [('rottweiler-paw-source.png', 'paw_clean'),
                         ('rottweiler-bow-source.png', 'front_leg_bow'),
                         ('rottweiler-blink-source.png', 'head-delighted')]:
        panel = Image.open(ASSETS/source).convert('RGB')
        rgb = np.asarray(panel).astype(float)/255
        key = (rgb[:, :, 0] > .65) & (rgb[:, :, 1] < .3) & (rgb[:, :, 2] > .65)
        yy, xx = np.where(~key)
        bounds = (max(0, int(xx.min())-2), max(0, int(yy.min())-2),
                  min(panel.width, int(xx.max())+3), min(panel.height, int(yy.max())+3))
        panel = panel.crop(bounds)
        panel.save(target/f'{name}.png')
        provenance['parts'][name] = {'source': source, 'trim': bounds, 'size': panel.size}
    (target / 'parts.json').write_text(json.dumps(provenance, indent=2)+'\n')
    print(json.dumps(provenance, indent=2))


if __name__ == '__main__':
    main()
