# /// script
# requires-python = ">=3.11"
# dependencies = ["vtracer==0.6.15", "pillow>=11,<13"]
# ///
"""A bounded full-detail vector transfer experiment; no intermediate bitmap saved."""
from pathlib import Path
import argparse, hashlib, json, runpy, xml.etree.ElementTree as ET
from PIL import Image
import vtracer

ROOT = Path(__file__).resolve().parent
p = argparse.ArgumentParser()
p.add_argument('source', type=Path)
p.add_argument('output', type=Path)
p.add_argument('--colors', type=int, default=16)
p.add_argument('--palette', help='Comma-separated exact hex inks; segmentation before tracing')
p.add_argument('--mode', choices=['spline','polygon'], default='spline')
args=p.parse_args()
if args.output.exists(): raise SystemExit('Choose a new output directory')
source=Image.open(args.source).convert('RGB')
# Palette reduction is segmentation for vector extraction, not a rendered asset.
if args.palette:
    inks=[tuple(bytes.fromhex(c.lstrip('#'))) for c in args.palette.split(',')]
    if not 2<=len(inks)<=256 or any(len(c)!=3 for c in inks): raise ValueError('Need 2..256 RGB inks')
    table=Image.new('P',(1,1));table.putpalette([v for c in inks for v in c]+[0]*(768-3*len(inks)))
    palette=source.quantize(palette=table,dither=Image.Dither.NONE).convert('RGBA')
else:
    palette=source.quantize(colors=args.colors, method=Image.Quantize.MEDIANCUT,
                            dither=Image.Dither.NONE).convert('RGBA')
params=dict(colormode='color', hierarchical='stacked', mode=args.mode,
            filter_speckle=4, color_precision=8, layer_difference=1,
            corner_threshold=60, length_threshold=4, splice_threshold=45, path_precision=2)
svg=vtracer.convert_pixels_to_svg(list(palette.getdata()), palette.size, **params)
tree=ET.fromstring(svg)
if args.mode=='polygon':
    clean=runpy.run_path(str(ROOT/'../../../../tools/lettering/trace.py'))['clean_polygon']
    for el in tree:
        if el.tag.endswith('path'): el.set('d',clean(el.attrib['d'],0.55))
    ET.register_namespace('','http://www.w3.org/2000/svg')
    svg=ET.tostring(tree,encoding='unicode')
paths=[dict(d=el.attrib['d'],fill=el.attrib['fill'],transform=el.attrib.get('transform',''))
       for el in tree if el.tag.endswith('path')]
args.output.mkdir(parents=True)
(args.output/'art.svg').write_text(svg)
record=dict(width=source.width,height=source.height,paths=paths)
(args.output/'geometry.json').write_text(json.dumps(record,separators=(',',':')))
report=dict(source=str(args.source),sourceSha256=hashlib.sha256(args.source.read_bytes()).hexdigest(),
            colors=len(inks) if args.palette else args.colors,palette=args.palette,params=params,simplify=0.55 if args.mode=='polygon' else 0,pathCount=len(paths),svgBytes=len(svg.encode()),
            limitation='Paint paths preserve color and order; they are not semantic glyphs or a lighting model.')
(args.output/'report.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report))
