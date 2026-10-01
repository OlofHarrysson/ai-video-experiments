"""Create a separate native handoff with packed music and a useful opening view."""
import argparse
import json
import sys
from pathlib import Path
import bpy

p=argparse.ArgumentParser();p.add_argument('--output',required=True);p.add_argument('--score',required=True)
args=p.parse_args(sys.argv[sys.argv.index('--')+1:])
out=Path(args.output).resolve();score=Path(args.score).resolve()
if out.exists():raise FileExistsError(out)
scene=bpy.context.scene
editor=scene.sequence_editor_create()
strip=editor.strips.new_sound('Original score | 120 BPM',str(score),channel=1,frame_start=1)
bpy.ops.file.pack_all()
assert strip.sound.packed_file
scene.frame_set(1)
scene.sync_mode='AUDIO_SYNC'
for screen in bpy.data.screens:
    for area in screen.areas:
        if area.type=='VIEW_3D':
            space=area.spaces.active
            space.region_3d.view_perspective='CAMERA'
            space.shading.type='MATERIAL'
            space.overlay.show_overlays=False
text=bpy.data.texts.new('START HERE')
text.write('''SIDE BY SIDE — PIP & BO

Space plays the 18-second study with the packed original score.
Timeline markers: groove at 1, side step at 145, robot at 289.
24 FPS delivery, with a new authored pose on each odd frame (12 poses/sec).

The opening view is the camera in Material Preview. Rendered lighting differs.
Enable viewport overlays to see the stage/control objects.

PIP | stage and BO | stage place each entire character.
Body, head, ears, eyes and each limb object have normal transform keyframes.
These are baked jointed puppets, not skinned armatures. Moving a chest key
alone does not solve the arms/legs again. For coordinated new poses, edit
choreography.py and rebuild through the shared clay_stage toolkit.

This file packs the score and uses procedural materials. It has no external
artwork, script handlers or add-on requirements. Blender 5.2.1 LTS was used.
''')
bpy.ops.wm.save_as_mainfile(filepath=str(out))
out.with_suffix('.json').write_text(json.dumps({'scene':str(out),'packed_sounds':[s.name for s in bpy.data.sounds if s.packed_file],'start_frame':1,'frames':scene.frame_end,'fps':scene.render.fps,'has_external_images':any(im.source=='FILE' and not im.packed_file for im in bpy.data.images)},indent=2)+'\n')
print('HANDOFF_SAVED',str(out),flush=True)
