# /// script
# requires-python = ">=3.11"
# dependencies = ["vtracer==0.6.15", "pillow>=11,<13"]
# ///
"""Versioned high-resolution color tracing. Intermediate is diagnostic, never playback."""
from pathlib import Path
import argparse,hashlib,json,time,gzip,xml.etree.ElementTree as ET
from PIL import Image
import vtracer
p=argparse.ArgumentParser();p.add_argument('source',type=Path);p.add_argument('output',type=Path);p.add_argument('--scale',type=int,default=4);p.add_argument('--speckle',type=int,default=1);p.add_argument('--mode',default='spline');p.add_argument('--post-quantize',action='store_true');args=p.parse_args()
args.output.mkdir(parents=True,exist_ok=False)
original=Image.open(args.source).convert('RGB');image=original
if not args.post_quantize:image=image.quantize(colors=256,method=Image.Quantize.MEDIANCUT,dither=Image.Dither.NONE).convert('RGB')
image=image.resize((image.width*args.scale,image.height*args.scale),Image.Resampling.LANCZOS)
if args.post_quantize:image=image.quantize(colors=256,method=Image.Quantize.MEDIANCUT,dither=Image.Dither.NONE).convert('RGB')
intermediate=args.output/'trace-input.png';image.save(intermediate)
params=dict(colormode='color',hierarchical='stacked',mode=args.mode,filter_speckle=args.speckle,color_precision=8,layer_difference=0,corner_threshold=60,length_threshold=1,splice_threshold=45,path_precision=3)
start=time.monotonic();vtracer.convert_image_to_svg_py(str(intermediate),str(args.output/'art.svg'),**params)
tree=ET.parse(args.output/'art.svg').getroot();paths=[dict(d=e.attrib['d'],fill=e.attrib['fill'],transform=e.attrib.get('transform','')) for e in tree if e.tag.endswith('path')]
data=json.dumps(dict(width=original.width,height=original.height,coordinateScale=args.scale,paths=paths),separators=(',',':')).encode()
(args.output/'geometry.json').write_bytes(data);(args.output/'geometry.json.gz').write_bytes(gzip.compress(data,compresslevel=9,mtime=0))
report=dict(source=str(args.source),sourceSha256=hashlib.sha256(args.source.read_bytes()).hexdigest(),scale=args.scale,postQuantize=args.post_quantize,params=params,pathCount=len(paths),svgBytes=(args.output/'art.svg').stat().st_size,geometryGzipBytes=(args.output/'geometry.json.gz').stat().st_size,seconds=time.monotonic()-start,limitation='Ordered color regions, not semantic glyphs; gradients remain approximated.')
(args.output/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
