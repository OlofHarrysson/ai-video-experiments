# /// script
# requires-python = ">=3.11"
# dependencies = ["vtracer==0.6.15", "pillow>=11,<13", "numpy>=2,<3", "scipy>=1.15,<2"]
# ///
"""Structural lighting masks: preserve source artwork; do not quantize its surface."""
from pathlib import Path
import argparse,json,hashlib,xml.etree.ElementTree as ET
import numpy as np
from PIL import Image
from scipy import ndimage as nd
import vtracer
p=argparse.ArgumentParser();p.add_argument('source',type=Path);p.add_argument('output',type=Path);p.add_argument('--kind',choices=['billions','keep'],required=True);args=p.parse_args();args.output.mkdir(parents=True,exist_ok=False)
im=Image.open(args.source).convert('RGB');a=np.asarray(im,dtype=float)/255;r,g,b=a.transpose(2,0,1)
def disk(radius):
 y,x=np.ogrid[-radius:radius+1,-radius:radius+1];return x*x+y*y<=radius*radius
def clean(mask,close=2,min_area=60,hole_area=500):
 mask=nd.binary_closing(mask,structure=disk(close))
 labels,n=nd.label(mask);sizes=np.bincount(labels.ravel());mask &= sizes[labels]>=min_area
 holes=nd.binary_fill_holes(mask)&~mask;labels,n=nd.label(holes);sizes=np.bincount(labels.ravel());mask |= holes&(sizes[labels]<=hole_area)
 return mask
if args.kind=='keep':
 masks={'enamel':clean((r>g*1.7)&(r>b*1.7)&(r>.14),close=5,min_area=160,hole_area=2500)}
else:
 masks={'face':clean((r>.56)&(g/r.clip(.01)>.70)&(b/r.clip(.01)>.38),close=2,min_area=300,hole_area=250),
        'red':clean((r>g*1.8)&(r>b*1.5)&(r>.2),close=1,min_area=25,hole_area=40),
        'blue':clean((b>r*1.35)&(b>g*1.1)&(b>.14),close=1,min_area=25,hole_area=40)}
layers={};params=dict(colormode='binary',mode='spline',filter_speckle=4,corner_threshold=85,length_threshold=2,splice_threshold=45,path_precision=3)
for name,mask in masks.items():
 # Smooth mask edges only. The artwork itself is never filtered.
 smooth=nd.gaussian_filter(mask.astype(float),.65)
 plane=Image.fromarray(np.uint8(smooth*255)).resize((im.width*4,im.height*4),Image.Resampling.BICUBIC)
 binary=Image.fromarray(np.where(np.asarray(plane)>127,0,255).astype(np.uint8)).convert('RGB');input_path=args.output/f'{name}-input.png';binary.save(input_path)
 svg=args.output/f'{name}.svg';vtracer.convert_image_to_svg_py(str(input_path),str(svg),**params)
 tree=ET.parse(svg).getroot();layers[name]=[dict(d=e.attrib['d'],transform=e.attrib.get('transform','')) for e in tree if e.tag.endswith('path')]
 print(name,len(layers[name]),flush=True)
record=dict(width=im.width,height=im.height,coordinateScale=4,layers=layers)
(args.output/'masks.json').write_text(json.dumps(record,separators=(',',':')))
(args.output/'report.json').write_text(json.dumps(dict(source=str(args.source),sourceSha256=hashlib.sha256(args.source.read_bytes()).hexdigest(),kind=args.kind,layerPaths={k:len(v) for k,v in layers.items()},params=params,limitation='Broad visible-surface masks for exposure and reveals; no recovered hidden geometry or true surface normals.'),indent=2)+'\n')
