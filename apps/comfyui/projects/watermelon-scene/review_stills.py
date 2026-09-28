# /// script
# requires-python = ">=3.11"
# dependencies = ["numpy", "pillow", "scipy"]
# ///
from pathlib import Path
import json,math
import numpy as np
from PIL import Image,ImageDraw,ImageFont
from scipy import ndimage
ROOT=Path(__file__).parent
OUT=ROOT/'exports/stills';OUT.mkdir(parents=True,exist_ok=True)
bg=np.asarray(Image.open(ROOT/'runs/stills/background/output-0.png').convert('RGB'),dtype=float)
manifest=json.loads((ROOT/'references/assets/manifest.json').read_text())
font=ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc',15)
yy,xx=np.mgrid[:1024,:1024];records=[];tiles=[]
for folder in sorted((ROOT/'runs/stills').iterdir()):
 p=folder/'output-0.png'
 if not p.exists() or folder.name=='background':continue
 cfg=json.loads((folder/'input.json').read_text());i=cfg['index'];target=manifest['frames'][i];cx,cy,r=target['cx'],target['cy'],target['radius']
 im=Image.open(p).convert('RGB').resize((1024,1024));rgb=np.asarray(im,dtype=float);red,green,blue=rgb[:,:,0],rgb[:,:,1],rgb[:,:,2]
 mask=(green>red*.98)&(green>blue*1.15)&(green-blue>10)&(yy>430)
 mask=ndimage.binary_fill_holes(ndimage.binary_closing(mask,iterations=3));lab,n=ndimage.label(mask);sizes=np.bincount(lab.ravel());sizes[0]=0
 mask=ndimage.binary_fill_holes(lab==sizes.argmax()) if n else mask
 ys,xs=np.nonzero(mask);goal=(xx-cx)**2+(yy-cy)**2<=r*r
 edit=((xx-cx)**2+(yy-cy)**2<=(r+20)**2)|(((xx-cx-45)/190)**2+((yy-cy-r)/55)**2<=1)
 rec={'label':folder.name,'target':target,'method':'Colour-based fruit estimate below y=430, largest component, hole-fill; inspect contours. Background difference excludes intended fruit and shadow region.'}
 if len(xs):rec.update(centre=[float(xs.mean()),float(ys.mean())],centre_error_px=float(math.hypot(xs.mean()-cx,ys.mean()-cy)),diameter_error_percent=float((2*math.sqrt(len(xs)/math.pi)/(2*r)-1)*100),silhouette_iou=float((mask&goal).sum()/(mask|goal).sum()))
 if 'layout' not in folder.name:
  diff=np.abs(rgb-bg);rec.update(background_mae_255=float(diff[~edit].mean()),background_pixels_changed_over_10_percent=float(100*(diff.max(2)[~edit]>10).mean()))
 records.append(rec);ov=np.array(im);ov[mask^ndimage.binary_erosion(mask)]=[0,255,255];ov=Image.fromarray(ov);d=ImageDraw.Draw(ov);d.ellipse((cx-r,cy-r,cx+r,cy+r),outline='#ff3296',width=2);ov.save(OUT/(folder.name+'-contour.png'))
 tile=Image.new('RGB',(384,440),'#202428');tile.paste(im.resize((384,384)),(0,56));d=ImageDraw.Draw(tile);d.text((8,6),folder.name,fill='white',font=font);d.text((8,29),f"centre {rec.get('centre_error_px',0):.1f}px | diameter {rec.get('diameter_error_percent',0):+.1f}%",fill='white',font=font);tiles.append(tile)
for page,start in enumerate(range(0,len(tiles),9)):
 subset=tiles[start:start+9];sheet=Image.new('RGB',(1152,440*math.ceil(len(subset)/3)),'#202428')
 for i,t in enumerate(subset):sheet.paste(t,((i%3)*384,(i//3)*440))
 sheet.save(OUT/f'comparison-{page}.jpg',quality=94)
(OUT/'metrics.json').write_text(json.dumps(records,indent=2));print(json.dumps([{k:v for k,v in x.items() if k not in ('method','target')} for x in records],indent=2))
aligned=Image.new('RGB',(1120,620),'#202428')
for i,target in enumerate(manifest['frames']):
 p=ROOT/f'runs/stills/sunburst-guide-{i}/output-0.png'
 if not p.exists():continue
 cx,cy=target['cx'],target['cy'];crop=Image.open(p).crop((round(cx-150),round(cy-150),round(cx+150),round(cy+150))).resize((280,280))
 x=(i%4)*280;y=(i//4)*310;aligned.paste(crop,(x,y+30));ImageDraw.Draw(aligned).text((x+8,y+7),f'Position {i+1} / 7',fill='white',font=font)
aligned.save(OUT/'sunburst-aligned-rind.jpg',quality=95)
