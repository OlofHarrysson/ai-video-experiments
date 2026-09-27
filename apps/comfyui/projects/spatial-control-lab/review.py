# /// script
# requires-python = ">=3.11"
# dependencies = ["numpy", "pillow", "scipy"]
# ///
from pathlib import Path
import json,math,argparse,re
import numpy as np
from PIL import Image,ImageDraw,ImageFont
from scipy import ndimage
ROOT=Path(__file__).parent
p=argparse.ArgumentParser();p.add_argument('--round',default='round1');a=p.parse_args();round_dir=ROOT/'runs'/a.round;exp=ROOT/'exports'/a.round;exp.mkdir(parents=True,exist_ok=True)
font=ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc',16)
results=[];tiles=[]
for folder in sorted(round_dir.iterdir()):
 output=folder/'output-0.png'
 if not output.exists():output=folder/'output.png'
 if not output.exists():continue
 motion=re.search(r'motion[0-6]',folder.name)
 case=motion.group() if motion else next((c for c in ['centre','right','small','large','left'] if c in folder.name),'left')
 target=json.loads((ROOT/'references/assets'/case/'target.json').read_text())
 original=Image.open(output);im=original.convert('RGB').resize((1024,1024),Image.Resampling.LANCZOS);rgb=np.array(im).astype(float)
 r,g,b=rgb[:,:,0],rgb[:,:,1],rgb[:,:,2]
 # Diagnostic foreground estimate for this green-fruit/neutral-background scene only.
 mask=(g>r*0.8)&(g>b*1.15)&(g-b>5)&(g>15)
 mask=ndimage.binary_fill_holes(ndimage.binary_closing(mask,iterations=3)); lab,n=ndimage.label(mask)
 if n:
  sizes=np.bincount(lab.ravel());sizes[0]=0;mask=lab==sizes.argmax();mask=ndimage.binary_fill_holes(mask)
 yy,xx=np.mgrid[:1024,:1024];goal=(xx-target['cx'])**2+(yy-target['cy'])**2<=target['radius']**2
 ys,xs=np.nonzero(mask)
 if len(xs):
  cx,cy=xs.mean(),ys.mean();diam=2*math.sqrt(len(xs)/math.pi);bbox=[int(xs.min()),int(ys.min()),int(xs.max()+1),int(ys.max()+1)]
  m={'label':folder.name,'case':case,'image_size':original.size,'estimated_centre':[round(cx,2),round(cy,2)],'centre_error_px':round(math.hypot(cx-target['cx'],cy-target['cy']),2),'equivalent_diameter':round(diam,2),'diameter_error_percent':round(100*(diam/(2*target['radius'])-1),2),'silhouette_iou':round(float((mask&goal).sum()/(mask|goal).sum()),4),'estimated_bbox':bbox,'alpha_extrema':original.getchannel('A').getextrema() if original.mode=='RGBA' else None}
 else:m={'label':folder.name,'error':'no green foreground found'}
 results.append(m)
 draw=ImageDraw.Draw(im);draw.ellipse(target['bbox'],outline=(255,50,150),width=2)
 tile=Image.new('RGB',(384,436),'#202428');tile.paste(im.resize((384,384)),(0,52));td=ImageDraw.Draw(tile);td.text((8,5),folder.name[:38],font=font,fill='white');td.text((8,28),f"centre {m.get('centre_error_px')}px | IoU {m.get('silhouette_iou')}",font=font,fill='white');tiles.append(tile)
 if len(xs):
  overlay=np.array(Image.open(output).convert('RGB').resize((1024,1024)));boundary=mask^ndimage.binary_erosion(mask);overlay[boundary]=[0,255,255];Image.fromarray(overlay).save(exp/(folder.name+'-segmentation.png'))
cols=3;rows=math.ceil(len(tiles)/cols)
if tiles:
 sheet=Image.new('RGB',(cols*384,rows*436),'#16191c')
 for i,tile in enumerate(tiles):sheet.paste(tile,((i%cols)*384,(i//cols)*436))
 sheet.save(exp/'comparison.jpg',quality=94)
(exp/'metrics.json').write_text(json.dumps({'method':'Approximate green foreground, largest connected component and hole fill; normalized to 1024 canvas. Requires visual contour validation. Not ground-truth segmentation.','results':results},indent=2));print(json.dumps(results,indent=2))
