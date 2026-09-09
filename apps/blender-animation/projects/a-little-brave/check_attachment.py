"""Measure textured head/torso overlap for both characters in every film pose.

Reuses the original puppy's projected-triangle checker. This detects silhouette
separation; it does not certify attractive anatomy or invisible paint seams.
"""
import importlib.util
import json
import sys
from pathlib import Path
import bpy
import numpy as np

ROOT=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('puppy_attachment',ROOT.parent/'puppy-2d/attachment_check.py')
raster=importlib.util.module_from_spec(spec);spec.loader.exec_module(raster)
raster.PIXELS_PER_UNIT=90
raster.LEFT,raster.TOP=-5.5,4.0
raster.WIDTH,raster.HEIGHT=1080,450


def alpha_for(ob):
    nodes=ob.data.materials[0].node_tree.nodes
    image=next(n.image for n in nodes if n.type=='TEX_IMAGE')
    pixels=np.empty(len(image.pixels),dtype=np.float32);image.pixels.foreach_get(pixels)
    rgba=pixels.reshape(image.size[1],image.size[0],4)
    alpha=rgba[:,:,3].copy()
    chroma=next((n for n in nodes if n.type=='MAP_RANGE' and n.inputs['Value'].is_linked
                 and n.inputs['Value'].links[0].from_node.type=='MATH'
                 and n.inputs['Value'].links[0].from_node.operation=='MINIMUM'),None)
    if chroma:
        key=np.minimum(rgba[:,:,0]-rgba[:,:,1],rgba[:,:,2]-rgba[:,:,1])
        lo,hi=[chroma.inputs[n].default_value for n in ['From Min','From Max']]
        alpha*=1-np.clip((key-lo)/(hi-lo),0,1)
    for node in nodes:
        if node.type!='MATH' or node.operation!='MAXIMUM':continue
        if not all(s.is_linked and s.links[0].from_node.type=='MAP_RANGE' for s in node.inputs[:2]):continue
        yy,xx=np.mgrid[0:image.size[1],0:image.size[0]]
        coordinates={'X':xx/(image.size[0]-1),'Y':yy/(image.size[1]-1)}
        values=[]
        for socket in node.inputs[:2]:
            fade=socket.links[0].from_node
            channel=fade.inputs['Value'].links[0].from_socket.name
            lo,hi=[fade.inputs[n].default_value for n in ['From Min','From Max']]
            values.append(np.clip((coordinates[channel]-lo)/(hi-lo),0,1))
        alpha*=np.maximum(*values)
    return alpha


out=Path(sys.argv[sys.argv.index('--')+1]).resolve();assert not out.exists()
scene=bpy.context.scene
dogs={name:[bpy.data.objects[name+' / '+part] for part in ['Paint | torso','Drawing | attentive']]
      for name in ['Biscuit','Bruno']}
alphas={name:[alpha_for(ob) for ob in objects] for name,objects in dogs.items()}
rows=[]
for f in range(1,scene.frame_end+1):
    scene.frame_set(f);depsgraph=bpy.context.evaluated_depsgraph_get()
    row={'frame':f,'overlap':{}}
    for name,objects in dogs.items():
        masks=[raster.silhouette(ob,alpha,depsgraph) for ob,alpha in zip(objects,alphas[name])]
        row['overlap'][name]=int(np.count_nonzero(masks[0]&masks[1]))/raster.PIXELS_PER_UNIT**2
    rows.append(row)
    if f%24==0:print('ATTACHMENT',f,row['overlap'],flush=True)
report={'scene':bpy.data.filepath,'frames':len(rows),'pixels_per_unit':raster.PIXELS_PER_UNIT,
        'method':'Projected evaluated triangles and source alpha; keyed RGB alpha estimated from the saved matte settings.',
        'minimum':{name:min(rows,key=lambda row:row['overlap'][name]) for name in dogs},'samples':rows}
out.write_text(json.dumps(report,indent=2)+'\n')
assert all(row['overlap'][name]>.025 for row in rows for name in dogs),report['minimum']
print('ATTACHMENT_COMPLETE',report['minimum'],flush=True)
