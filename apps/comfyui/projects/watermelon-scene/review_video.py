# /// script
# requires-python = ">=3.11"
# dependencies = ["numpy", "pillow", "scipy"]
# ///
from pathlib import Path
import json, subprocess, math
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy import ndimage
ROOT=Path(__file__).parent
OUT=ROOT/'exports/video';OUT.mkdir(parents=True,exist_ok=True)
font=ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc',17)
yy,xx=np.mgrid[:512,:512]
all_metrics=[]
for p in sorted((ROOT/'runs/video').glob('*/output.mp4')):
 name=p.parent.name
 probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-of','json',str(p)]))
 stream=next(s for s in probe['streams'] if s['codec_type']=='video')
 num,den=map(float,stream['r_frame_rate'].split('/'));fps=num/den
 raw=subprocess.check_output(['ffmpeg','-v','error','-i',str(p),'-vf','scale=512:512','-f','rawvideo','-pix_fmt','rgb24','-'])
 frames=np.frombuffer(raw,dtype=np.uint8).reshape(-1,512,512,3)
 records=[];overlays=[]
 for i,arr in enumerate(frames):
  red,green,blue=np.moveaxis(arr.astype(float),2,0)
  mask=(green>red*.98)&(red>green*.45)&(green>blue*1.15)&(green-blue>10)&(yy>215)
  mask=ndimage.binary_fill_holes(ndimage.binary_closing(mask,iterations=2));lab,n=ndimage.label(mask);sizes=np.bincount(lab.ravel());sizes[0]=0
  if n:mask=ndimage.binary_fill_holes(lab==sizes.argmax())
  ys,xs=np.nonzero(mask);t=i/(len(frames)-1);cx=125+260*t;cy=325;r=65
  rec={'frame':i,'time':i/fps,'target_cx_1024':cx*2}
  rec['fruit_detected']=bool(len(xs)>math.pi*r*r*.25)
  if rec['fruit_detected']:rec.update(centre_1024=[float(xs.mean()*2),float(ys.mean()*2)],centre_error_px_1024=float(math.hypot(xs.mean()-cx,ys.mean()-cy)*2),diameter_error_percent=float((math.sqrt(len(xs)/math.pi)/r-1)*100))
  records.append(rec)
  if i in np.rint(np.linspace(0,len(frames)-1,9)).astype(int):
   im=Image.fromarray(arr);im.save(OUT/f'{name}-frame-{i:03d}.jpg',quality=95)
   ov=arr.copy();ov[mask^ndimage.binary_erosion(mask)]=[0,255,255];ov=Image.fromarray(ov);d=ImageDraw.Draw(ov);d.ellipse((cx-r,cy-r,cx+r,cy+r),outline='#ff3296',width=2)
   error_label=f'{rec["centre_error_px_1024"]:.0f}px' if rec['fruit_detected'] else 'no fruit detected'
   tile=Image.new('RGB',(512,552),'#202428');tile.paste(ov,(0,40));d=ImageDraw.Draw(tile);d.text((8,8),f'{name} | {i/fps:.2f}s | {error_label}',fill='white',font=font);overlays.append(tile)
 sheet=Image.new('RGB',(1536,1656),'#202428')
 for i,tile in enumerate(overlays):sheet.paste(tile,((i%3)*512,(i//3)*552))
 sheet.save(OUT/f'{name}-contact.jpg',quality=94)
 errors=[r['centre_error_px_1024'] for r in records if 'centre_error_px_1024' in r]
 summary={'name':name,'frames':len(frames),'detected_frames':len(errors),'fps':fps,'source_size':[stream['width'],stream['height']],'mean_centre_error_px_1024':float(np.mean(errors)) if len(errors)==len(frames) else None,'max_centre_error_px_1024':float(np.max(errors)) if len(errors)==len(frames) else None,'first':records[0],'last':records[-1],'method':'Approximate colour-based largest fruit contour, excluding saturated synthetic green. Missing or tiny fruit detections invalidate whole-clip error statistics. Values at 1024 scale, expected uniform horizontal motion over returned clip. Visual checks required; does not measure identity or physical correctness.'}
 (OUT/f'{name}-metrics.json').write_text(json.dumps({'summary':summary,'frames':records},indent=2));all_metrics.append(summary)
(OUT/'metrics.json').write_text(json.dumps(all_metrics,indent=2));print(json.dumps(all_metrics,indent=2))
