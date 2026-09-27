# /// script
# requires-python = ">=3.11"
# dependencies = ["pillow", "numpy"]
# ///
from pathlib import Path
import json,hashlib
import numpy as np
from PIL import Image,ImageDraw
ROOT=Path(__file__).parent
N=1024
BG=(32,36,40)
ASSETS=ROOT/'references/assets'; ASSETS.mkdir(parents=True,exist_ok=True)
cases={'left':(256,512,180),'centre':(512,512,180),'right':(768,512,180),'small':(720,320,100),'large':(350,650,260)}
for name,(cx,cy,r) in cases.items():
 d=ASSETS/name;d.mkdir(exist_ok=True)
 svg=f'<svg xmlns="http://www.w3.org/2000/svg" width="1024" height="1024" viewBox="0 0 1024 1024"><rect width="1024" height="1024" fill="#202428"/><circle cx="{cx}" cy="{cy}" r="{r}" fill="#559530"/></svg>'
 (d/'shape.svg').write_text(svg)
 # Analytic raster counterpart of the SVG. Supersampling preserves the circle edge.
 s=4; im=Image.new('RGB',(N*s,N*s),BG);ImageDraw.Draw(im).ellipse(((cx-r)*s,(cy-r)*s,(cx+r)*s,(cy+r)*s),fill='#559530');im.resize((N,N),Image.Resampling.LANCZOS).save(d/'shape.png')
 yy,xx=np.mgrid[:N,:N]; rr=((xx-cx)**2+(yy-cy)**2)/r**2;inside=rr<=1
 mask=(inside*255).astype('uint8');Image.fromarray(mask).save(d/'mask.png')
 edge=Image.new('L',(N*s,N*s));ImageDraw.Draw(edge).ellipse(((cx-r)*s,(cy-r)*s,(cx+r)*s,(cy+r)*s),outline=255,width=3*s);edge.resize((N,N),Image.Resampling.LANCZOS).save(d/'edge.png')
 depth=np.zeros((N,N));z=4-np.sqrt(np.maximum(0,1-rr));depth[inside]=(1/z[inside]-1/8)/(1/3-1/8);Image.fromarray(np.uint8(np.clip(depth,0,1)*255)).save(d/'depth.png')
 Image.new('RGB',(N,N),BG).save(d/'blank.png')
 alpha=Image.new('RGBA',(N,N),(255,255,255,255));alpha.putalpha(Image.fromarray(255-mask));alpha.save(d/'alpha-mask.png')
 (d/'target.json').write_text(json.dumps({'width':N,'height':N,'cx':cx,'cy':cy,'radius':r,'bbox':[cx-r,cy-r,cx+r,cy+r]},indent=2))
print(json.dumps({str(p.relative_to(ROOT)):p.stat().st_size for p in ASSETS.rglob('*.png')},indent=2))
