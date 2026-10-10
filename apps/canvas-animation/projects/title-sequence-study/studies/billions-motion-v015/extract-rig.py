# /// script
# requires-python = ">=3.11"
# dependencies = ["pillow>=11,<13", "numpy>=2,<3", "scipy>=1.15,<2", "opencv-python-headless>=4.10,<5"]
# ///
"""BILLIONS-specific separation of eight connected ivory faces; preserves RGB artwork."""
from pathlib import Path
import argparse,json,hashlib
import numpy as np
from PIL import Image
from scipy import ndimage as nd
import cv2
p=argparse.ArgumentParser();p.add_argument('source',type=Path);p.add_argument('rig',type=Path);p.add_argument('output',type=Path);args=p.parse_args();args.output.mkdir(parents=True,exist_ok=False)
a=np.asarray(Image.open(args.source).convert('RGB'),dtype=float);r,g,b=a.transpose(2,0,1)
mask=nd.binary_closing((r>170)&(g>140)&(b/r.clip(1)>.55),iterations=1);labels,n=nd.label(mask);sizes=np.bincount(labels.ravel());ids=np.argsort(sizes[1:])[-8:]+1
ids=sorted(ids,key=lambda i:np.where(labels==i)[1].min());rig=json.loads(args.rig.read_text());letters=[l for l in rig['layers'] if l['role']=='letter'];report=[]
for spec,idx in zip(letters,ids):
 if sizes[idx]<15000:raise ValueError('Expected eight large ivory letter faces')
 face=labels==idx;holes=nd.binary_fill_holes(face)&~face;hl,hn=nd.label(holes);hs=np.bincount(hl.ravel());face|=holes&(hs[hl]<5000)
 y,x=np.ogrid[-6:7,-6:7];expanded=nd.binary_dilation(face,structure=x*x+y*y<=36)
 contours,_=cv2.findContours(expanded.astype(np.uint8),cv2.RETR_LIST,cv2.CHAIN_APPROX_SIMPLE)
 paths=[]
 for contour in contours:
  pts=cv2.approxPolyDP(contour,.3,True).reshape(-1,2)
  paths.append('M'+'L'.join(f'{int(x)},{int(y)}' for x,y in pts)+'Z')
 spec['path']=''.join(paths);spec.pop('padding',None);Image.fromarray((expanded*255).astype(np.uint8)).save(args.output/(spec['id']+'-mask.png'))
 report.append({'id':spec['id'],'facePixels':int(sizes[idx]),'contours':len(contours),'vertices':sum(len(c) for c in contours)})
(args.output/'rig.json').write_text(json.dumps(rig,indent=2)+'\n');(args.output/'report.json').write_text(json.dumps({'sourceSha256':hashlib.sha256(args.source.read_bytes()).hexdigest(),'recipe':'ivory threshold + connected face + small-hole fill + 6px border; source RGB unchanged','letters':report},indent=2)+'\n');print(json.dumps(report))
