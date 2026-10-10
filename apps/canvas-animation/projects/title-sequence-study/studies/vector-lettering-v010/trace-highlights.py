# /// script
# requires-python = ">=3.11"
# dependencies = ["vtracer==0.6.15", "pillow>=11,<13"]
# ///
"""Extract two editable specular layers, not a full-color image trace.
These deliberately shaped highlights supplement geometric lighting on script.
"""
from pathlib import Path
from PIL import Image
import vtracer, json, xml.etree.ElementTree as ET, hashlib
ROOT=Path(__file__).resolve().parent
source=ROOT/'reference/material-board-01.png'
crop=Image.open(source).convert('RGB').crop((0,0,768,512))
layers={}
for name,test in {
 'warm': lambda r,g,b: r>220 and g>120 and b>60,
 'white':lambda r,g,b: r>235 and g>205 and b>140,
}.items():
 pixels=[(0,0,0,255) if test(*rgb) else (255,255,255,255) for rgb in crop.getdata()]
 svg=vtracer.convert_pixels_to_svg(pixels,crop.size,colormode='binary',mode='spline',filter_speckle=10,corner_threshold=75,length_threshold=3,splice_threshold=50,path_precision=3)
 root=ET.fromstring(svg)
 layers[name]=[{'d':p.attrib['d'],'transform':p.attrib.get('transform','')} for p in root if p.tag.endswith('path')]
 print(name,len(layers[name]))
(ROOT/'highlights.js').write_text('window.LetteringHighlights = '+json.dumps(layers,separators=(',',':'))+';\n')
(ROOT/'material-source.json').write_text(json.dumps({'source':'reference/material-board-01.png','original':'/Users/olof/.codex/generated_images/01a11531-7ce5-7fd1-bc3d-a4921247fd3d/exec-4ea59272-2437-4d9e-aeae-dbde5f592df7.png','sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'use':'Two thresholded specular layers vectorized for the script identity. No source pixels in runtime.'},indent=2)+'\n')
