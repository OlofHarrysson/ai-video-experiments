# /// script
# requires-python = ">=3.11"
# dependencies = ["vtracer==0.6.15", "pillow>=11,<13"]
# ///
"""Convert the generated silhouette board to editable vector paths.
The original PNG is preserved. Thresholding is an explicit segmentation step
for tracing; no derivative raster is saved or used by the animation.
"""
from pathlib import Path
from PIL import Image
import vtracer
import xml.etree.ElementTree as ET
import json, hashlib, re, math

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / 'reference/lettering-board-01.png'
image = Image.open(SOURCE).convert('RGB')
width, height = image.size
# Four separately isolated designs keep paths semantic at the identity level.
regions = {'script': (0, 0, width//2, height//2),
           'machine': (width//2, 0, width, 460),
           'tuscan': (0, 480, width//2, height),
           'liquid': (width//2, 480, width, height)}
output = {}
def clean_polygon(d):
    """Remove raster stair-step vertices while retaining every sharp corner."""
    contours=[]
    for part in d.split('Z'):
        numbers=list(map(float,re.findall(r'-?\d+(?:\.\d+)?',part)))
        points=list(zip(numbers[::2],numbers[1::2]))
        if not points: continue
        changed=True
        while changed and len(points)>3:
            changed=False
            for i,p in enumerate(points):
                a,b=points[i-1],points[(i+1)%len(points)]
                dx,dy=b[0]-a[0],b[1]-a[1]
                length=math.hypot(dx,dy)
                if not length: continue
                cross=abs(dx*(p[1]-a[1])-dy*(p[0]-a[0]))/length
                along=((p[0]-a[0])*dx+(p[1]-a[1])*dy)/(length*length)
                if cross<1.05 and 0<=along<=1:
                    points.pop(i);changed=True;break
        contours.append('M'+' L'.join(f'{x:g},{y:g}' for x,y in points)+' Z')
    return ' '.join(contours)
for name, box in regions.items():
    crop = image.crop(box)
    # VTracer binary foreground is black. Explicit inversion makes white
    # ink the foreground and ignores incidental grey paper-like shading.
    rgba = [(0,0,0,255) if sum(rgb)/3 > 130 else (255,255,255,255)
            for rgb in crop.getdata()]
    svg = vtracer.convert_pixels_to_svg(rgba, crop.size, colormode='binary',
        mode='polygon' if name == 'machine' else 'spline',
        filter_speckle=12, corner_threshold=70,
        length_threshold=3.0, splice_threshold=45, path_precision=3)
    (ROOT / f'{name}.svg').write_text(svg)
    tree = ET.fromstring(svg)
    paths = [{'d': p.attrib['d'], 'transform': p.attrib.get('transform','')}
             for p in tree if p.tag.endswith('path')]
    if name == 'machine':
        for p in paths: p['d']=clean_polygon(p['d'])
        for el,p in zip([e for e in tree if e.tag.endswith('path')],paths): el.set('d',p['d'])
        ET.register_namespace('','http://www.w3.org/2000/svg')
        (ROOT / f'{name}.svg').write_text(ET.tostring(tree,encoding='unicode'))
    output[name] = {'width': crop.width,'height':crop.height,'paths':paths}
    print(name, len(paths), 'paths', sum(len(p['d']) for p in paths), 'path chars')
(ROOT/'geometry.js').write_text('window.CustomLettering = '+json.dumps(output,separators=(',',':'))+';\n')
(ROOT/'reference-source.json').write_text(json.dumps({
    'source':str(SOURCE.relative_to(ROOT)),
    'generated_original':'/Users/olof/.codex/generated_images/01a11531-7ce5-7fd1-bc3d-a4921247fd3d/exec-ebf5248d-db5d-489d-821c-8b89736b4ac0.png',
    'sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
    'dimensions':[width,height], 'threshold':130,
    'vectorizer':'vtracer 0.6.15', 'regions':regions,
    'pixel_use':'Reference and vector extraction only. No PNG loaded at render time.'
},indent=2)+'\n')
