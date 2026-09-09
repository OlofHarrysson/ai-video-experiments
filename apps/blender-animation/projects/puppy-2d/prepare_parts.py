# /// script
# requires-python = ">=3.11"
# dependencies = ["pillow"]
# ///
"""Extract isolated atlas components, preserving generated alpha and source pixels."""
import json
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parent
ASSETS = ROOT / 'assets'
BOXES = {
    'body': (45,45,595,480),
    'head': (610,30,1040,470),
    'ear': (1130,30,1430,490),
    'front_leg': (135,490,455,970),
    'hind_leg': (605,490,950,970),
    'tail': (1080,510,1460,950),
}
atlas = Image.open(ASSETS/'parts-atlas-v001.png').convert('RGBA')
parts={}
for name, box in BOXES.items():
    part=atlas.crop(box)
    bounds=part.getchannel('A').point(lambda a:255 if a>32 else 0).getbbox()
    assert bounds, name
    x0,y0,x1,y1=bounds
    bounds=(max(0,x0-3),max(0,y0-3),min(part.width,x1+3),min(part.height,y1+3))
    part=part.crop(bounds)
    part.save(ASSETS/f'{name}.png')
    parts[name]={'atlas_box':box,'trim_box':bounds,'size':part.size}
(ASSETS/'parts.json').write_text(json.dumps(parts,indent=2)+'\n')
for source,target in [('head-delighted-source.png','head-delighted.png'),
                      ('front-leg-bow-source.png','front_leg_bow.png'),
                      ('paw-clean-source.png','paw_clean.png')]:
    im=Image.open(ASSETS/source).convert('RGBA')
    bounds=im.getchannel('A').point(lambda a:255 if a>32 else 0).getbbox()
    assert bounds,source
    im.crop(bounds).save(ASSETS/target)
print(parts)
