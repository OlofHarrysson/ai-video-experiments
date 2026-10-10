# /// script
# requires-python = ">=3.11"
# dependencies = ["pillow>=11,<13", "numpy>=2,<3", "scipy>=1.15,<2"]
# ///
"""Adaptive piecewise-linear RGB mesh. Source pixels are offline fitting targets only."""
from pathlib import Path
import argparse,gzip,hashlib,json,time
import numpy as np
from PIL import Image
from scipy.spatial import Delaunay
from scipy import sparse
from scipy.sparse.linalg import cg,LinearOperator

def main():
 p=argparse.ArgumentParser();p.add_argument('source',type=Path);p.add_argument('output',type=Path);p.add_argument('--vertices',type=int,default=90000);p.add_argument('--batch',type=int,default=7500);p.add_argument('--initial-step',type=int,default=24);p.add_argument('--fit-colors',action='store_true');args=p.parse_args();args.output.mkdir(parents=True,exist_ok=False)
 original=Image.open(args.source)
 if 'A' in original.getbands() and original.getchannel('A').getextrema()!=(255,255):raise ValueError('Composite transparent input deliberately before fitting')
 if min(args.vertices,args.batch,args.initial_step)<1:raise ValueError('Vertex budget, batch and initial step must be positive')
 im=original.convert('RGB');rgb=np.asarray(im,dtype=np.float32);h,w=rgb.shape[:2]
 yy,xx=np.mgrid[0:h,0:w];queries=np.column_stack((xx.ravel()+.5,yy.ravel()+.5));target=rgb.reshape(-1,3)
 gx,gy=np.meshgrid(np.arange(.5,w,args.initial_step),np.arange(.5,h,args.initial_step));points=np.column_stack((gx.ravel(),gy.ravel()))
 boundary=np.array([[0,0],[w,0],[w,h],[0,h]],float);points=np.concatenate([points,boundary])
 chosen=np.zeros((h,w),bool);chosen[np.clip(points[:,1].astype(int),0,h-1),np.clip(points[:,0].astype(int),0,w-1)]=True
 if len(points)>args.vertices:raise ValueError('Vertex budget is smaller than the initial grid; increase budget or initial step')
 log=[];start=time.monotonic()
 while True:
  tri=Delaunay(points);colors=rgb[np.clip(points[:,1].astype(int),0,h-1),np.clip(points[:,0].astype(int),0,w-1)]
  simplex=tri.find_simplex(queries);trans=tri.transform[simplex];bary=np.einsum('nij,nj->ni',trans[:,:2],queries-trans[:,2]);bary=np.column_stack((bary,1-bary.sum(axis=1)))
  reconstructed=np.sum(colors[tri.simplices[simplex]]*bary[:,:,None],axis=1)
  residual=np.abs(reconstructed-target);errors=np.max(residual,axis=1).reshape(h,w)
  record=dict(vertices=len(points),triangles=len(tri.simplices),mae=float(residual.mean()),p99=float(np.percentile(residual,99)),elapsed=time.monotonic()-start);log.append(record);print(json.dumps(record),flush=True)
  if len(points)>=args.vertices or float(np.percentile(errors,99.5))<4:break
  # One error maximum per small cell gives spatial coverage, then select strongest residuals.
  errors[chosen]=-1
  cell=4 if len(points)<25000 else 2
  ph=(h+cell-1)//cell*cell;pw=(w+cell-1)//cell*cell
  padded=np.full((ph,pw),-1,dtype=np.float32);padded[:h,:w]=errors
  blocks=padded.reshape(ph//cell,cell,pw//cell,cell).transpose(0,2,1,3).reshape(-1,cell*cell)
  best=np.argmax(blocks,axis=1);scores=blocks[np.arange(len(blocks)),best]
  number=min(args.batch,args.vertices-len(points),int(np.sum(scores>2)))
  if number<1:break
  selected=np.argpartition(scores,-number)[-number:];bx=selected%(pw//cell);by=selected//(pw//cell);sx=bx*cell+best[selected]%cell;sy=by*cell+best[selected]//cell
  chosen[sy,sx]=True;points=np.concatenate([points,np.column_stack((sx+.5,sy+.5))])
 if args.fit_colors:
  A=sparse.csr_matrix((bary.ravel(),(np.repeat(np.arange(len(queries)),3),tri.simplices[simplex].ravel())),shape=(len(queries),len(points)))
  lhs=A.T@A+sparse.eye(len(points))*1e-6;rhs=A.T@target;diagonal=lhs.diagonal();M=LinearOperator(lhs.shape,matvec=lambda x:x/diagonal)
  for c in range(3):
   colors[:,c],info=cg(lhs,rhs[:,c],x0=colors[:,c],M=M,rtol=1e-5,maxiter=160)
   if info:print('color fit convergence code',info,flush=True)
  colors=np.clip(colors,0,255);reconstructed=A@colors;residual=np.abs(reconstructed-target)
  log.append(dict(stage='least-squares vertex colors',mae=float(residual.mean()),p99=float(np.percentile(residual,99))))
  print(json.dumps(log[-1]),flush=True)
 # Store geometric vertices, vertex colors and triangle indices. No bitmap or texture payload.
 geometry=dict(width=w,height=h,positions=points.astype(np.float32).ravel().tolist(),colors=np.rint(colors).astype(np.uint8).ravel().tolist(),triangles=tri.simplices.astype(np.uint32).ravel().tolist())
 data=json.dumps(geometry,separators=(',',':')).encode();(args.output/'mesh.json').write_bytes(data);(args.output/'mesh.json.gz').write_bytes(gzip.compress(data,compresslevel=9,mtime=0))
 preview=np.clip(reconstructed.reshape(h,w,3),0,255).round().astype(np.uint8);Image.fromarray(preview).save(args.output/'cpu-fit.png')
 report=dict(source=str(args.source),sourceSha256=hashlib.sha256(args.source.read_bytes()).hexdigest(),vertices=len(points),triangles=len(tri.simplices),meshGzipBytes=(args.output/'mesh.json.gz').stat().st_size,iterations=log,seconds=time.monotonic()-start,limitation='Mesh-encoded image samples; not semantic glyphs, true surface normals or unlimited source detail.')
 (args.output/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items() if k!='iterations'}),flush=True)

if __name__=='__main__':main()
