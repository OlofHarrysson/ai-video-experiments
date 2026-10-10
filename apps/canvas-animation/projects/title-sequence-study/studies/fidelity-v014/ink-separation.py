# /// script
# requires-python = ">=3.11"
# dependencies = ["vtracer==0.6.15", "pillow>=11,<13", "numpy>=2,<3", "scipy>=1.15,<2"]
# ///
"""Experimental coverage separation of flat engraving inks; not a glossy-material model."""
import argparse,json,hashlib,time,xml.etree.ElementTree as ET
from pathlib import Path
import numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter
import vtracer
ROOT=Path(__file__).resolve().parent
p=argparse.ArgumentParser();p.add_argument('source',type=Path);p.add_argument('output',type=Path);p.add_argument('--scale',type=int,default=4);args=p.parse_args();args.output.mkdir(parents=True,exist_ok=False)
im=Image.open(args.source).convert('RGB');a=np.asarray(im,dtype=np.float32)/255
inks=np.array([[.99,.91,.73],[.79,.60,.27],[.89,.07,.055],[.02,.26,.65]],np.float32)
names=['ivory','gold','red','blue']
strength=np.clip(np.einsum('hwc,kc->hwk',a,inks)/np.sum(inks*inks,axis=1),0,1)
error=np.stack([np.sum((a-strength[:,:,k,None]*ink)**2,axis=2) for k,ink in enumerate(inks)],axis=2)
winner=np.argmin(error,axis=2)
paths=[];counts={};params=dict(colormode='binary',mode='spline',filter_speckle=3,corner_threshold=90,length_threshold=1,splice_threshold=45,path_precision=3)
for k,name in enumerate(names):
 coverage=np.where(winner==k,strength[:,:,k],0)
 # Broad ink has three tones; high tone preserves cream's dark engraved hatching.
 for level in ([.20,.60,.88] if k<2 else [.30]):
  gray=Image.fromarray(np.uint8(coverage*255)).resize((im.width*args.scale,im.height*args.scale),Image.Resampling.BICUBIC)
  binary=np.asarray(gray)>level*255
  trace_image=Image.fromarray(np.where(binary,0,255).astype(np.uint8)).convert('RGB');input_path=args.output/f'{name}-{level}-mask.png';trace_image.save(input_path)
  svgpath=args.output/f'{name}-{level}.svg';vtracer.convert_image_to_svg_py(str(input_path),str(svgpath),**params)
  tree=ET.fromstring(svgpath.read_text());color='#'+''.join(f'{round(v*255*([.56,.81,1][[.20,.60,.88].index(level)] if k<2 else 1)):02x}' for v in inks[k])
  parts=[dict(d=e.attrib['d'],fill=color,transform=e.attrib.get('transform',''),ink=name,tone=level) for e in tree if e.tag.endswith('path')]
  paths+=parts;counts[f'{name}-{level}']=len(parts);print(name,level,len(parts),flush=True)
# Dark tones first, then bright; foreground cream should cover background ornament where masks overlap.
paths.sort(key=lambda x:(x['tone'],x['ink']=='ivory'))
record=dict(width=im.width,height=im.height,coordinateScale=args.scale,paths=paths)
(args.output/'geometry.json').write_text(json.dumps(record,separators=(',',':')))
(args.output/'report.json').write_text(json.dumps(dict(source=str(args.source),sourceSha256=hashlib.sha256(args.source.read_bytes()).hexdigest(),scale=args.scale,pathCount=len(paths),layers=counts,params=params,limitation='Nearest ink-ray coverage plus three fixed tones; may flatten or misclassify source material.'),indent=2)+'\n')
