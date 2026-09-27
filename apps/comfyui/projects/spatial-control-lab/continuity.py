# /// script
# requires-python = ">=3.11"
# dependencies = ["numpy", "pillow"]
# ///
"""Inspect motion-aligned texture changes; this is not an identity benchmark."""
from pathlib import Path
import json
import numpy as np
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).parent
OUT=ROOT/'exports/round3';OUT.mkdir(parents=True,exist_ok=True)
font=ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc',19)
methods={'independent':lambda i:f'sunburst-independent-motion{i}/output-0.png','reference':lambda i:f'sunburst-reference-motion{i}/output-0.png','inpaint':lambda i:f'{17+i}-qwen21-inpaint-motion{i}-43/output.png'}
sheet=Image.new('RGB',(7*210,3*250),'#202428');draw=ImageDraw.Draw(sheet);results={}
yy,xx=np.mgrid[:360,:360];mask=(xx-180)**2+(yy-180)**2<150**2
for row,(method,path) in enumerate(methods.items()):
 crops=[]
 for i in range(7):
  target=json.loads((ROOT/f'references/assets/motion{i}/target.json').read_text());cx=target['cx'];cy=target['cy']
  im=Image.open(ROOT/'runs/round3'/path(i)).convert('RGB')
  crop=im.transform((360,360),Image.Transform.EXTENT,(cx-180,cy-180,cx+180,cy+180),Image.Resampling.BICUBIC);crops.append(np.asarray(crop,dtype=float)/255)
  sheet.paste(crop.resize((210,210)),(i*210,row*250+40));draw.text((i*210+5,row*250+9),f'{method} · {i}',fill='white',font=font)
 errors=[float(np.abs(a-b)[mask].mean()) for a,b in zip(crops,crops[1:])]
 results[method]={'adjacent_mean_absolute_rgb_change':errors,'mean':float(np.mean(errors))}
sheet.save(OUT/'aligned-texture.jpg',quality=95)
(OUT/'continuity.json').write_text(json.dumps({'method':'Target-centred 360px crops; mean absolute RGB difference within inner radius 150, range 0-1. Lighting and small misalignment also contribute. No optical flow or texture matching.','results':results},indent=2));print(json.dumps(results,indent=2))
