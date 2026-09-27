# /// script
# requires-python = ">=3.11"
# dependencies = ["numpy", "pillow"]
# ///
"""Prepare masks and targets from the rendered Remotion guide manifest."""
from pathlib import Path
import json,shutil
import numpy as np
from PIL import Image
ROOT=Path(__file__).parent
REMOTION=ROOT.parents[2]/'remotion/projects/watermelon-guides/renders/v001'
manifest=json.loads((REMOTION/'manifest.json').read_text())
y,x=np.mgrid[:1024,:1024]
for item in manifest['frames']:
 i=item['index'];d=ROOT/f'references/assets/motion{i}';d.mkdir(parents=True,exist_ok=True)
 cx,cy,r=item['cx'],item['cy'],item['radius']
 Image.fromarray(np.uint8(((x-cx)**2+(y-cy)**2<=r*r)*255)).save(d/'mask.png')
 Image.new('RGB',(1024,1024),'#202428').save(d/'blank.png')
 shutil.copyfile(REMOTION/f'guide-{i}.png',d/'shape.png')
 (d/'target.json').write_text(json.dumps({**item,'bbox':[cx-r,cy-r,cx+r,cy+r]},indent=2))
