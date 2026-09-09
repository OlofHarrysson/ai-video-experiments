"""Reopen the saved scene, verify animation, and render selected native frames."""
import argparse
import json
import sys
from pathlib import Path

import bpy

p=argparse.ArgumentParser()
p.add_argument('--output',required=True)
p.add_argument('--step',type=int,default=1)
p.add_argument('--percentage',type=int,default=100)
p.add_argument('--samples',type=int,default=32)
p.add_argument('--verify-only',action='store_true')
args=p.parse_args(sys.argv[sys.argv.index('--')+1:])
out=Path(args.output).resolve(); out.mkdir(parents=True,exist_ok=True)
assert args.step >= 1 and 1 <= args.percentage <= 100 and args.samples >= 1
if not args.verify_only and any(out.glob('frame_*.png')):
    raise FileExistsError('Choose an empty render folder to preserve prior frames')
scene=bpy.context.scene
rig=bpy.data.objects['BISCUIT | pose controls']
assert len(rig.data.bones)==23, len(rig.data.bones)
assert rig.animation_data.action is not None
assert scene.frame_end==90 and scene.render.fps==30
assert all(any(m.type=='ARMATURE' for m in ob.modifiers) for ob in bpy.data.objects
           if ob.type=='MESH' and ob.name!='Plain studio floor')
metrics=[]
for f in range(1,91):
    scene.frame_set(f)
    row={'frame':f,'paws':{}}
    for name in ['front.near','front.far','back.near','back.far']:
        actual=rig.matrix_world @ rig.pose.bones['paw.'+name].head
        target=rig.matrix_world @ rig.pose.bones['CTRL.paw.'+name].head
        row['paws'][name]={'actual':list(actual),'target':list(target),'ik_error':(actual-target).length}
    metrics.append(row)
max_error=max(p['ik_error'] for r in metrics for p in r['paws'].values())
bow_drift=max((max(r['paws'][n]['actual'][axis] for r in metrics[23:33])-
               min(r['paws'][n]['actual'][axis] for r in metrics[23:33]))
              for n in metrics[0]['paws'] for axis in range(3))
report={'blender':bpy.app.version_string,'reopened_scene':bpy.data.filepath,
        'bones':len(rig.data.bones),'max_ik_error':max_error,'bow_paw_max_axis_drift':bow_drift,'frames':metrics}
(out/'rig-verification.json').write_text(json.dumps(report,indent=2)+'\n')
print('RIG_CHECK',json.dumps({k:v for k,v in report.items() if k!='frames'}),flush=True)
assert max_error < .002, 'Paw target exceeds limb reach'
assert bow_drift < .0001, 'Planted paw moves during bow hold'
if args.verify_only:
    raise SystemExit(0)
pref=bpy.context.preferences.addons['cycles'].preferences
pref.compute_device_type='METAL'; pref.get_devices()
metal=[d for d in pref.devices if d.type=='METAL']
assert metal, 'No Metal render device'
for d in pref.devices:
    d.use=d.type=='METAL'
scene.cycles.device='GPU'; scene.cycles.samples=args.samples
scene.render.resolution_percentage=args.percentage
print('RENDER_DEVICE',[d.name for d in metal],flush=True)
for f in range(1,91,args.step):
    scene.frame_set(f)
    scene.render.filepath=str(out/f'frame_{f:04d}.png')
    bpy.ops.render.render(write_still=True)
