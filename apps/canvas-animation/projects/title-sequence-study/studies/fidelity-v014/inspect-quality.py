# /// script
# requires-python = ">=3.11"
# dependencies = ["pillow>=11,<13", "numpy>=2,<3"]
# ///
"""Matched native crops and delivery error; never substitutes for visual review."""
from pathlib import Path
import argparse, hashlib, json, subprocess
import numpy as np
from PIL import Image, ImageDraw
ROOT=Path(__file__).resolve().parent
p=argparse.ArgumentParser();p.add_argument('render',type=Path);p.add_argument('output',type=Path);args=p.parse_args();args.output.mkdir(parents=True,exist_ok=False)
report={};sheet=Image.new('RGB',(1280,660),'#161616');d=ImageDraw.Draw(sheet)
for row,(kind,box,frame) in enumerate([('billions',(80,210,400,510),24),('keep',(420,420,740,720),120)]):
 source=ROOT/'../art-direction-v012/reference'/('keep-up.png' if kind=='keep' else 'billions.png')
 paths={'Previous SVG':ROOT/f'../identity-motion-v013/output-proof-{kind}-v003/vector.png','Packed mesh':ROOT/f'output-motion-v001/{kind}-unlit.png','Selected hybrid':args.render/f'{kind}-unlit.png','Original':source}
 ref=np.asarray(Image.open(source).convert('RGB'),dtype=float);stats={}
 for col,(label,path) in enumerate(paths.items()):
  im=Image.open(path).convert('RGB');delta=np.abs(np.asarray(im,dtype=float)-ref)
  stats[label]={'mae':float(delta.mean()),'max':float(delta.max()),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
  sheet.paste(im.crop(box),(col*320,row*330));d.text((col*320+6,row*330+310),label,fill='white')
 decoded=args.output/f'{kind}-encoded.png'
 subprocess.run(['ffmpeg','-v','error','-i',str(args.render/'clean-lettering.mp4'),'-vf',f'select=eq(n\\,{frame})','-frames:v','1',str(decoded)],check=True)
 pre=Image.open(args.render/f'frame-{frame:04d}.png').convert('RGB');post=Image.open(decoded).convert('RGB')
 diff=np.abs(np.asarray(pre,dtype=float)-np.asarray(post,dtype=float))
 stats['delivery']={'frame':frame,'mae':float(diff.mean()),'p99':float(np.percentile(diff,99))}
 scaled=tuple(round(v*1600/1672) for v in box)
 pair=Image.new('RGB',(640,330),'#161616');draw=ImageDraw.Draw(pair)
 for col,(name,im) in enumerate([('Before MP4',pre),('Decoded MP4',post)]):
  pair.paste(im.crop(scaled).resize((320,300),Image.Resampling.NEAREST),(col*320,0));draw.text((col*320+6,310),name,fill='white')
 pair.save(args.output/f'{kind}-delivery.png');report[kind]=stats
sheet.save(args.output/'before-after.png');
review=Image.new('RGB',(960,660),'#161616')
for row in range(2):
 for col,sourcecol in enumerate([0,2,3]):review.paste(sheet.crop((sourcecol*320,row*330,sourcecol*320+320,row*330+330)),(col*320,row*330))
review.save(args.output/'review-comparison.png');(args.output/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
