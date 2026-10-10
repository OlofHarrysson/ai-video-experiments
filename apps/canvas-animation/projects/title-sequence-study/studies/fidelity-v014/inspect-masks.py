# /// script
# requires-python = ">=3.11"
# dependencies = ["pillow>=11,<13", "numpy>=2,<3", "scipy>=1.15,<2"]
# ///
from pathlib import Path
import argparse,json
import numpy as np
from PIL import Image,ImageDraw
from scipy.ndimage import uniform_filter
p=argparse.ArgumentParser();p.add_argument('input',type=Path);args=p.parse_args();report={}
for kind in ['billions','keep']:
 candidates=[]
 for time in [0,.5,1,1.5,2,2.5,3]:
  hard=Image.open(args.input/f'{kind}-f0-{time}.png').convert('RGB');soft=Image.open(args.input/f'{kind}-f3-{time}.png').convert('RGB')
  delta=np.abs(np.asarray(hard,dtype=float)-np.asarray(soft,dtype=float)).mean(axis=2);region=uniform_filter(delta,100);y,x=np.unravel_index(np.argmax(region),region.shape)
  candidates.append((region[y,x],time,x,y,hard,soft))
 score,time,x,y,hard,soft=max(candidates,key=lambda z:z[0]);x=min(max(x-160,0),hard.width-320);y=min(max(y-150,0),hard.height-300);box=(x,y,x+320,y+300)
 sheet=Image.new('RGB',(1280,660),'#141414');d=ImageDraw.Draw(sheet)
 for col,(name,im) in enumerate([('Hard control edges',hard),('Feathered control edges',soft)]):
  sheet.paste(im.crop(box).resize((640,600),Image.Resampling.NEAREST),(col*640,0));d.text((col*640+12,620),name,fill='white')
 sheet.save(args.input/f'{kind}-peak-mask-change.png');report[kind]={'time':time,'crop':list(map(int,box)),'localMeanChange':float(score),'purpose':'Largest 100px local effect of feathering; crop is magnified 2x nearest, not an artistic score.'}
(args.input/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
