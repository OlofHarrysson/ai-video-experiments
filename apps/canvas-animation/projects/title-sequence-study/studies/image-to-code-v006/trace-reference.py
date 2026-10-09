# /// script
# requires-python = ">=3.11"
# dependencies = ["vtracer==0.6.15"]
# ///
"""Local vector reconstruction probe. Never embeds source pixels in the SVG."""
from pathlib import Path
import hashlib, json, sys, xml.etree.ElementTree as ET
import vtracer
ROOT = Path(__file__).resolve().parent
source = ROOT / 'output/wild-hours-reference-01.png'
out = ROOT / (sys.argv[1] if len(sys.argv)>1 else 'output-vector-probe')
out.mkdir(exist_ok=False)
settings = dict(colormode='color', hierarchical='stacked', mode='spline', filter_speckle=4, color_precision=8, layer_difference=int(sys.argv[2]) if len(sys.argv)>2 else 12, corner_threshold=60, length_threshold=3.5, max_iterations=10, splice_threshold=45, path_precision=2)
vtracer.convert_image_to_svg_py(str(source),str(out/'trace.svg'),**settings)
root=ET.parse(out/'trace.svg').getroot()
paths=[dict(e.attrib) for e in root.iter() if e.tag.endswith('path')]
(out/'paths.js').write_text('window.VectorPaths = '+json.dumps(paths,separators=(',',':'))+';\n')
(out/'report.json').write_text(json.dumps({'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'settings':settings,'paths':len(paths),'svg_bytes':(out/'trace.svg').stat().st_size},indent=2))
print((out/'report.json').read_text())
