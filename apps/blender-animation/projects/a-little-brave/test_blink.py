"""Render a small eyelid-deformation audition without altering source scenes."""
import sys
from pathlib import Path
import bpy

ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT))
from blink import add_blink

scene=bpy.context.scene
scene.frame_set(1)
head=bpy.data.objects['Drawing | attentive']
eye=bpy.data.objects['Drawing | delighted eyes']
eye.animation_data_clear();eye.hide_render=True
key=add_blink(head,'puppy')
scene.camera.data.ortho_scale=3.0
scene.camera.location.x=.55
scene.camera.location.z=1.72
scene.render.resolution_x=960
scene.render.resolution_y=960
scene.render.resolution_percentage=100
scene.cycles.samples=16
out=ROOT/'output/blink-v002'
out.mkdir(exist_ok=False)
for index,value in enumerate([0,.45,.8,1.]):
    key.value=value
    scene.render.filepath=str(out/f'blink_{index}.png')
    bpy.ops.render.render(write_still=True)
bpy.ops.wm.save_as_mainfile(filepath=str(out/'blink-audition.blend'))
