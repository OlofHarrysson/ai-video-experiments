# /// script
# requires-python = ">=3.11"
# dependencies = ["numpy>=2,<3"]
# ///
"""Compact geometry, RGB vertex colors and triangle indices. No bitmap payload."""
from pathlib import Path
import argparse,gzip,hashlib,json,struct
import numpy as np
p=argparse.ArgumentParser();p.add_argument('input',type=Path);p.add_argument('output',type=Path);args=p.parse_args();args.output.mkdir(parents=True,exist_ok=False)
raw=args.input.read_bytes();data=json.loads(raw);xy=np.asarray(data['positions'],dtype=float).reshape(-1,2);rgb=np.asarray(data['colors'],np.uint8).reshape(-1,3);tri=np.asarray(data['triangles'],np.uint32).reshape(-1,3)
if np.min(xy)<0 or np.max(np.abs(xy*2-np.rint(xy*2)))>1e-6 or np.max(xy*2)>65535:raise ValueError('This format requires half-pixel coordinates in uint16 range')
xy=np.rint(xy*2).astype('<u2')
def morton(x):
 x=x.astype(np.uint32);x=(x|(x<<8))&0x00FF00FF;x=(x|(x<<4))&0x0F0F0F0F;x=(x|(x<<2))&0x33333333;x=(x|(x<<1))&0x55555555;return x
order=np.argsort(morton(xy[:,0])|(morton(xy[:,1])<<1),kind='stable');inverse=np.empty(len(order),np.uint32);inverse[order]=np.arange(len(order),dtype=np.uint32)
xy=xy[order];rgb=rgb[order];tri=inverse[tri];tri=np.sort(tri,axis=1);tri=tri[np.lexsort((tri[:,2],tri[:,1],tri[:,0]))].astype('<u4')
payload=struct.pack('<8sIIII',b'GMESH001',data['width'],data['height'],len(xy),tri.size)+xy.tobytes()+rgb.tobytes();payload+=bytes((-len(payload))%4);payload+=tri.tobytes()
compressed=gzip.compress(payload,compresslevel=9,mtime=0);(args.output/'mesh.bin.gz').write_bytes(compressed)
report=dict(format='GMESH001',width=data['width'],height=data['height'],vertices=len(xy),triangles=len(tri),rawBytes=len(payload),gzipBytes=len(compressed),inputSha256=hashlib.sha256(raw).hexdigest(),payloadSha256=hashlib.sha256(payload).hexdigest(),note='Spatially reordered half-pixel coordinates, RGB8 vertex colors and uint32 indices; sorted triangles require culling disabled.')
(args.output/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
