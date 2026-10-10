# /// script
# requires-python = ">=3.11"
# dependencies = ["pillow>=11,<13", "numpy>=2,<3"]
# ///
"""Diagnostic errors and close-up sheets, not a substitute for visual judgment."""
from pathlib import Path
import argparse,json
import numpy as np
from PIL import Image,ImageDraw
p=argparse.ArgumentParser();p.add_argument('output',type=Path);args=p.parse_args();out=args.output
records=[]
for identity in ['billions','keep-up']:
 source=np.asarray(Image.open(out/f'{identity}-source.png').convert('RGB'),dtype=float)
 files=[out/f'{identity}-baseline.png',out/f'{identity}-quant256.png']+sorted(out.glob(f'{identity}-*-ss*.png'))
 for f in files:
  arr=np.asarray(Image.open(f).convert('RGB'),dtype=float);d=arr-source;edge=np.max(np.abs(np.diff(source,axis=1)),axis=2)>25
  records.append(dict(identity=identity,file=f.name,mae=float(np.abs(d).mean()),rmse=float(np.sqrt((d*d).mean())),edgeMae=float(np.abs(d[:,:-1])[edge].mean()),p99=float(np.percentile(np.abs(d),99))))
 selected=['source','baseline','quant256','q256-polygon-ss1','q256-none-ss1','raw-none-ss1','raw-polygon-ss1','raw-cutout-ss1','raw-spline-fine-ss1'] if (out/f'{identity}-raw-none-ss1.png').exists() else ['source','baseline','quant256','q256-none-speckle1-ss1','q256-polygon-speckle0-ss1','q256-spline-2x-ss1','q256-spline-4x-ss1','q256-polygon-4x-ss1','q256-spline-4x-detail-ss1']
 sheet=Image.new('RGB',(960,3*330),(20,20,24));draw=ImageDraw.Draw(sheet)
 for i,key in enumerate(selected):
  im=Image.open(out/f'{identity}-{key}.png').convert('RGB');x=i%3*320;y=i//3*330;sheet.paste(im,(x,y));draw.text((x+8,y+307),key,fill='white')
 sheet.save(out/f'{identity}-matrix.png')
(out/'metrics.json').write_text(json.dumps(records,indent=2)+'\n')
for identity in ['billions','keep-up']:
 print(identity)
 for r in sorted([r for r in records if r['identity']==identity],key=lambda r:r['mae']):print(r['file'],round(r['mae'],3),round(r['edgeMae'],3))
