# /// script
# requires-python = ">=3.11"
# dependencies = ["pillow>=11,<13", "numpy>=2,<3"]
# ///
from pathlib import Path
import argparse,json,hashlib,subprocess
from PIL import Image,ImageDraw,ImageFont
import numpy as np
ROOT=Path(__file__).resolve().parent
p=argparse.ArgumentParser();p.add_argument('render',type=Path);p.add_argument('output',type=Path);args=p.parse_args();args.output.mkdir(parents=True,exist_ok=False)
source=ROOT/'../fidelity-v014/assets/billions.png';a=np.asarray(Image.open(source).convert('RGB'),dtype=float);report={'sourceSha256':hashlib.sha256(source.read_bytes()).hexdigest(),'fidelity':{}}
for name in ['assembled-native','hold-native']:
 b=np.asarray(Image.open(args.render/f'{name}.png').convert('RGB'),dtype=float);delta=abs(a-b);report['fidelity'][name]={'mae':float(delta.mean()),'max':float(delta.max())}
poses=json.loads((args.render/'poses.json').read_text());report['motion']={}
for id in ['B','I1','L1','L2','I2','O','N','S']:
 rows=[l for f in poses for l in f['layers'] if l['id']==id and l['alpha']>.1];report['motion'][id]={'verticalTravelSourcePixels':float(max(l['y'] for l in rows)-min(l['y'] for l in rows)),'rotationRangeDegrees':float((max(l['r'] for l in rows)-min(l['r'] for l in rows))*180/np.pi)}
font=ImageFont.load_default(size=20);old=ROOT/'../fidelity-v014/output-motion-v004';changes={'before':[],'after':[]};prior={}
for n in range(72):
 sheet=Image.new('RGB',(1600,490),'#101010');d=ImageDraw.Draw(sheet)
 for col,(label,folder,key) in enumerate([('Before: light only',old,'before'),('Now: moving letters and ornaments',args.render,'after')]):
  im=Image.open(folder/f'frame-{n:04d}.png').convert('RGB');small=np.asarray(im.resize((400,225)),dtype=float)
  if key in prior:changes[key].append(float(abs(small-prior[key]).mean()))
  prior[key]=small;sheet.paste(im.resize((800,450),Image.Resampling.LANCZOS),(col*800,40));d.text((col*800+16,10),label,font=font,fill='white')
 sheet.save(args.output/f'compare-{n:04d}.png')
subprocess.run(['ffmpeg','-v','error','-framerate','24','-i',str(args.output/'compare-%04d.png'),'-c:v','libx264','-crf','14','-pix_fmt','yuv420p','-movflags','+faststart',str(args.output/'before-after.mp4')],check=True)
report['meanConsecutiveFrameDifference']={key:float(np.mean(v)) for key,v in changes.items()};report['note']='Pixel difference measures activity, not artistic quality. Full assembled native and actual timeline hold must preserve RGB.'
report['passed']=all(v['max']==0 for v in report['fidelity'].values());(args.output/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
