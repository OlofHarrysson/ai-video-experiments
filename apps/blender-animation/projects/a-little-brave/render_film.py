"""Reopen, inspect the native scene, and render a versioned frame sequence."""
import argparse
import json
import sys
from pathlib import Path

import bpy

p = argparse.ArgumentParser()
p.add_argument('--output', required=True)
p.add_argument('--percentage', type=int, default=50)
p.add_argument('--samples', type=int, default=8)
p.add_argument('--start', type=int, default=1)
p.add_argument('--end', type=int, default=384)
p.add_argument('--step', type=int, default=1)
p.add_argument('--verify-only', action='store_true')
args = p.parse_args(sys.argv[sys.argv.index('--')+1:])
out = Path(args.output).resolve()
out.mkdir(parents=True, exist_ok=True)
assert not any(out.glob('frame_*.png')), 'Choose a new render folder'
assert 1 <= args.start <= args.end <= 384 and args.step > 0
assert 1 <= args.percentage <= 100 and args.samples > 0
scene = bpy.context.scene
assert scene.render.fps == 24 and scene.frame_end == 384
rigs = [ob for ob in bpy.data.objects if ob.type == 'ARMATURE']
assert len(rigs) == 2 and all(len(ob.data.bones)==24 for ob in rigs)
assert all(image.packed_file for image in bpy.data.images if image.source=='FILE')
rows = []
for f in range(1,385):
    scene.frame_set(f)
    row = {'frame':f,'camera':scene.camera.name,'errors':{}}
    for rig in rigs:
        errors = {}
        for name in ('front.near','front.far','back.near','back.far'):
            a = rig.matrix_world @ rig.pose.bones['paw.'+name].head
            b = rig.matrix_world @ rig.pose.bones['CTRL.paw.'+name].head
            errors[name] = (a-b).length
        row['errors'][rig.name] = errors
    rows.append(row)
maximum = max(value for row in rows for dog in row['errors'].values() for value in dog.values())
report = {'scene':bpy.data.filepath,'blender':bpy.app.version_string,
          'frames':384,'fps':24,'maximum_paw_error':maximum,'samples':rows}
(out/'reopened-scene-check.json').write_text(json.dumps(report,indent=2)+'\n')
assert maximum < .003, f'Paw control is beyond limb reach: {maximum}'
print('REOPEN_CHECK',maximum,flush=True)
if not args.verify_only:
    scene.cycles.device = 'CPU'
    scene.cycles.samples = args.samples
    scene.render.resolution_percentage = args.percentage
    for f in range(args.start,args.end+1,args.step):
        scene.frame_set(f)
        scene.render.filepath = str(out/f'frame_{f:04d}.png')
        bpy.ops.render.render(write_still=True)
