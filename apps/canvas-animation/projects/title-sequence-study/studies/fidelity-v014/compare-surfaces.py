# /// script
# requires-python = ">=3.11"
# dependencies = ["pillow>=11,<13", "numpy>=2,<3"]
# ///
from pathlib import Path
import argparse,json
import numpy as np
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parent
p=argparse.ArgumentParser();p.add_argument('output',type=Path);p.add_argument('--surface-version',default='v001');args=p.parse_args();args.output.mkdir(parents=True,exist_ok=False)
crops={'billions':[(80,210,400,510),(620,35,940,335)],'keep':[(420,420,740,720),(1200,360,1520,660)]};report=[]
for id,boxes in crops.items():
 source=ROOT/'../art-direction-v012/reference'/('keep-up.png' if id=='keep' else 'billions.png')
 choices={'Original':source,'Previous SVG':ROOT/f'../identity-motion-v013/output-proof-{id}-v003/vector.png','4x trace':ROOT/f'output-proof-hires-{id}-v001/vector.png','Color mesh':ROOT/f'output-surface-{id}-{args.surface_version}/mesh.png','Hybrid':ROOT/f'output-surface-{id}-{args.surface_version}/hybrid.png'}
 images={k:Image.open(v).convert('RGB') for k,v in choices.items()};reference=np.asarray(images['Original'],dtype=float)
 for label,img in images.items():
  diff=np.abs(np.asarray(img,dtype=float)-reference);edge=np.max(np.abs(np.diff(reference,axis=1)),axis=2)>25
  report.append(dict(id=id,label=label,mae=float(diff.mean()),edgeMae=float(diff[:,:-1][edge].mean()),cropMae=[float(diff[b[1]:b[3],b[0]:b[2]].mean()) for b in boxes]))
 sheet=Image.new('RGB',(len(images)*320,len(boxes)*330),(20,20,24));draw=ImageDraw.Draw(sheet)
 for row,box in enumerate(boxes):
  for col,(label,img) in enumerate(images.items()):sheet.paste(img.crop(box),(col*320,row*330));draw.text((col*320+5,row*330+310),label,fill='white')
 sheet.save(args.output/f'{id}-crops.png')
(args.output/'metrics.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
