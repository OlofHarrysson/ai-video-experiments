"""Verify evaluated shoes, silhouette bounds and object keys after reopening a scene."""
import argparse
import hashlib
import json
import sys
from pathlib import Path
import bpy
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view

p=argparse.ArgumentParser();p.add_argument('--motion',required=True);p.add_argument('--output',required=True)
p.add_argument('--packed-score',help='Also compare reopened packed audio with the source WAV')
args=p.parse_args(sys.argv[sys.argv.index('--')+1:])
out=Path(args.output)
if out.exists():raise FileExistsError(out)
motion=json.loads(Path(args.motion).read_text())
scene=bpy.context.scene
previous={};max_error=0;max_drift=0;min_height=1;min_separation=100;bounds=[1,1,0,0];rows=[];partner_gap=100
for row in motion['samples']:
    scene.frame_set(row['frame'])
    for character in row['characters']:
        name=character['name'];state=character['pose'];stage=bpy.data.objects[name+' | stage']
        feet=[]
        for i,sign in enumerate([-1,1]):
            ob=bpy.data.objects[name+f' leg {sign} shoe']
            actual=ob.matrix_world.translation
            expected=stage.matrix_world@Vector(state['feet'][i])
            max_error=max(max_error,(actual-expected).length)
            min_height=min(min_height,actual.z-.125)
            feet.append(actual.copy())
            k=name,sign
            if k in previous:
                old,old_support,old_move=previous[k]
                if old_support and state['support'][i] and old_move==row['move']:
                    max_drift=max(max_drift,(actual-old).length)
            previous[k]=(actual.copy(),state['support'][i],row['move'])
        min_separation=min(min_separation,(feet[0]-feet[1]).length)
    # Project every mesh corner; stage geometry and lights are intentionally excluded.
    character_x={'PIP':[100,-100],'BO':[100,-100]}
    for ob in bpy.data.objects:
        if ob.type=='MESH' and ob.name.startswith(('PIP','BO')):
            name=ob.name.split()[0]
            for point in ob.bound_box:
                world=ob.matrix_world@Vector(point)
                character_x[name]=[min(character_x[name][0],world.x),max(character_x[name][1],world.x)]
                x,y,z=world_to_camera_view(scene,scene.camera,world)
                assert z>0
                bounds=[min(bounds[0],x),min(bounds[1],y),max(bounds[2],x),max(bounds[3],y)]
    partner_gap=min(partner_gap,character_x['BO'][0]-character_x['PIP'][1])
    rows.append(row['frame'])
report={'reopened_scene':bpy.data.filepath,'pose_count':len(rows),'shoe_target_error':max_error,'planted_shoe_drift':max_drift,'minimum_shoe_bottom_z':min_height,'minimum_shoe_center_distance':min_separation,'camera_bounds_xy':bounds,'scope':'Evaluated object transforms and bounding boxes, not a general collision or perceptual-motion test.'}
report['minimum_partner_mesh_x_gap']=partner_gap
if args.packed_score:
    expected=hashlib.sha256(Path(args.packed_score).read_bytes()).hexdigest()
    actual=[hashlib.sha256(sound.packed_file.data).hexdigest() for sound in bpy.data.sounds if sound.packed_file]
    assert actual==[expected], 'Packed sound differs from the source WAV'
    report['packed_score_sha256']=expected
out.write_text(json.dumps(report,indent=2)+'\n')
assert max_error<1e-5,report
assert max_drift<1e-5,report
assert min_height>=-1e-5,report
assert min_separation>.39,report
assert partner_gap>0,report  # Disjoint world-X bounds guarantee the two puppets do not intersect.
assert bounds[0]>.03 and bounds[1]>.03 and bounds[2]<.97 and bounds[3]<.97,report
print('SCENE_CHECK_PASS',json.dumps(report),flush=True)
