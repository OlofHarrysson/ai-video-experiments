# /// script
# requires-python = ">=3.11"
# dependencies = ["numpy>=2,<3", "opencv-python-headless>=4.10,<5"]
# ///
"""Bounded contour simplification of linear traces; never reorders paint layers."""
from pathlib import Path
import argparse,gzip,hashlib,json,re,time
import numpy as np
import cv2
p=argparse.ArgumentParser();p.add_argument('input',type=Path);p.add_argument('output',type=Path);p.add_argument('--error',type=float,default=.12,help='Maximum contour deviation in source-image pixels');args=p.parse_args();args.output.mkdir(parents=True,exist_ok=False)
start=time.monotonic();raw=args.input.read_bytes();data=json.loads(raw);scale=data.get('coordinateScale',1);before=after=0;result=[]
for path in data['paths']:
 d=path['d']
 if re.search(r'[A-KN-Yac-z]',d):raise ValueError('Only absolute linear M/L/Z paths are supported')
 contours=[]
 for contour in d.split('Z'):
  nums=[float(x) for x in re.findall(r'-?\d+(?:\.\d+)?',contour)]
  if not nums:continue
  points=np.array(nums,np.float32).reshape(-1,2);before+=len(points)
  simple=cv2.approxPolyDP(points,args.error*scale,True).reshape(-1,2)
  if len(simple)<3:simple=points
  # Preserve nonzero winding, including holes.
  def area(p):return np.sum(p[:,0]*np.roll(p[:,1],-1)-p[:,1]*np.roll(p[:,0],-1))/2
  if area(points)*area(simple)<0:simple=simple[::-1]
  after+=len(simple)
  fmt=lambda v:f'{float(v):.3f}'.rstrip('0').rstrip('.')
  contours.append('M'+'L'.join(fmt(x)+','+fmt(y) for x,y in simple)+'Z')
 t=[float(x) for x in re.findall(r'-?\d+(?:\.\d+)?',path.get('transform',''))] or [0,0]
 result.append(dict(d=''.join(contours),fill=path['fill'],transform=f'translate({t[0]:g},{t[1]:g})'))
output=dict(width=data['width'],height=data['height'],coordinateScale=scale,paths=result)
encoded=json.dumps(output,separators=(',',':')).encode();(args.output/'geometry.json').write_bytes(encoded);(args.output/'geometry.json.gz').write_bytes(gzip.compress(encoded,compresslevel=9,mtime=0))
svg=f'<svg xmlns="http://www.w3.org/2000/svg" width="{data["width"]}" height="{data["height"]}" viewBox="0 0 {data["width"]*scale} {data["height"]*scale}">'+''.join(f'<path d="{p["d"]}" fill="{p["fill"]}" transform="{p["transform"]}"/>' for p in result)+'</svg>'
(args.output/'art.svg').write_text(svg)
report=dict(input=str(args.input),inputSha256=hashlib.sha256(raw).hexdigest(),errorSourcePixels=args.error,pointsBefore=before,pointsAfter=after,geometryBytes=len(encoded),geometryGzipBytes=(args.output/'geometry.json.gz').stat().st_size,pathCount=len(result),seconds=time.monotonic()-start,limitation='Geometric error bound is per simplified contour; rendered pixels still require comparison.')
(args.output/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
