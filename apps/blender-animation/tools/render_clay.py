"""Render selected native poses from a saved, self-contained scene."""
import argparse
import json
import sys
from pathlib import Path
import bpy

p=argparse.ArgumentParser()
p.add_argument('--output',required=True);p.add_argument('--percentage',type=int,default=100)
p.add_argument('--samples',type=int,default=32);p.add_argument('--start',type=int,default=1)
p.add_argument('--end',type=int);p.add_argument('--step',type=int,default=2)
p.add_argument('--frames',help='Comma-separated native frame numbers for a short proof')
args=p.parse_args(sys.argv[sys.argv.index('--')+1:])
out=Path(args.output).resolve()
if out.exists():raise FileExistsError('Render into a new directory')
out.mkdir(parents=True)
scene=bpy.context.scene
scene.render.resolution_percentage=args.percentage;scene.cycles.samples=args.samples
prefs=bpy.context.preferences.addons['cycles'].preferences
prefs.compute_device_type='METAL';prefs.get_devices()
for d in prefs.devices:d.use=d.type=='METAL'
scene.cycles.device='GPU'
frames=([int(x) for x in args.frames.split(',')] if args.frames else list(range(args.start,(args.end or scene.frame_end)+1,args.step)))
assert all(scene.frame_start<=f<=scene.frame_end for f in frames)
for index,f in enumerate(frames):
    scene.frame_set(f);scene.render.filepath=str(out/f'{index:04d}.png')
    bpy.ops.render.render(write_still=True)
    print('POSE_RENDERED',f,index+1,len(frames),flush=True)
(out/'manifest.json').write_text(json.dumps({'scene':bpy.data.filepath,'blender':bpy.app.version_string,'frames':frames,'fps':scene.render.fps/args.step,'samples':args.samples,'percentage':args.percentage},indent=2)+'\n')
