# /// script
# requires-python = ">=3.11"
# dependencies = ["vtracer==0.6.15", "pillow>=11,<13", "numpy>=2,<3"]
# ///
"""Matched crop experiments: isolate quantization, tracing and rendering losses."""
import argparse, hashlib, json, time, xml.etree.ElementTree as ET
from pathlib import Path
from PIL import Image
import vtracer

ROOT=Path(__file__).resolve().parent
CROPS={'billions':(80,210,400,510),'keep-up':(420,420,740,720)}
CONFIGS=[
 ('q256-polygon',256,'polygon','stacked',1,4),
 ('q256-none',256,'none','stacked',0,4),
 ('raw-none',0,'none','stacked',0,4),
 ('raw-polygon',0,'polygon','stacked',0,4),
 ('q256-cutout',256,'none','cutout',0,4),
 ('raw-cutout',0,'none','cutout',0,4),
 ('raw-spline-fine',0,'spline','stacked',0,.5),
 ('q256-spline-fine',256,'spline','stacked',0,.5),
 ('q256-none-speckle1',256,'none','stacked',1,4),
 ('q256-polygon-speckle0',256,'polygon','stacked',0,4),
 ('q256-spline-2x',256,'spline','stacked',2,2),
 ('q256-spline-4x',256,'spline','stacked',4,3),
 ('q256-polygon-4x',256,'polygon','stacked',4,3),
 ('q256-spline-4x-detail',256,'spline','stacked',1,1),
 ('post256-spline-4x',256,'spline','stacked',1,1),
 ('post256-none-4x',256,'none','stacked',0,1),
 ('post256-none-4x-speckle1',256,'none','stacked',1,1),
 ('post256-spline-4x-speckle0',256,'spline','stacked',0,.5),
]

def main():
 p=argparse.ArgumentParser();p.add_argument('output',type=Path);p.add_argument('--only',default='');args=p.parse_args()
 args.output.mkdir(exist_ok=False,parents=True)
 records=[]
 for identity,box in CROPS.items():
  source=ROOT/'../art-direction-v012/reference'/f'{identity}.png'
  im=Image.open(source).convert('RGB');crop=im.crop(box)
  crop.save(args.output/f'{identity}-source.png')
  quant=im.quantize(colors=256,method=Image.Quantize.MEDIANCUT,dither=Image.Dither.NONE).convert('RGB').crop(box)
  quant.save(args.output/f'{identity}-quant256.png')
  for name,colors,mode,hierarchy,speckle,length in CONFIGS:
   if args.only and name not in args.only.split(','):continue
   sample=(quant if colors and not name.startswith('post') else crop).convert('RGBA')
   scale=4 if '4x' in name else 2 if '2x' in name else 1
   if scale>1:sample=sample.resize((sample.width*scale,sample.height*scale),Image.Resampling.LANCZOS)
   if name.startswith('post'):sample=sample.convert('RGB').quantize(colors=256,method=Image.Quantize.MEDIANCUT,dither=Image.Dither.NONE).convert('RGBA')
   params=dict(colormode='color',hierarchical=hierarchy,mode=mode,filter_speckle=speckle,color_precision=8,layer_difference=0,corner_threshold=60,length_threshold=length,splice_threshold=45,path_precision=3)
   start=time.monotonic();svg=vtracer.convert_pixels_to_svg(list(sample.getdata()),sample.size,**params)
   tree=ET.fromstring(svg);paths=[dict(d=e.attrib['d'],fill=e.attrib['fill'],transform=e.attrib.get('transform','')) for e in tree if e.tag.endswith('path')]
   key=identity+'-'+name
   (args.output/f'{key}.json').write_text(json.dumps(dict(width=crop.width,height=crop.height,coordinateScale=scale,paths=paths),separators=(',',':')))
   record=dict(key=key,identity=identity,name=name,crop=box,sourceSha256=hashlib.sha256(source.read_bytes()).hexdigest(),params=params,pathCount=len(paths),svgBytes=len(svg.encode()),traceSeconds=time.monotonic()-start)
   records.append(record);print(json.dumps(record),flush=True)
 (args.output/'manifest.json').write_text(json.dumps(records,indent=2)+'\n')

if __name__=='__main__':main()
