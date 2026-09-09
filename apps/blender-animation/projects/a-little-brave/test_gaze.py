"""Audition a controllable iris before adopting it in the film."""
import sys
from pathlib import Path
import bpy
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT))
from gaze import add_gaze
character=sys.argv[sys.argv.index('--')+1] if '--' in sys.argv else 'bruno'
scene=bpy.context.scene;scene.frame_set(1)
head=bpy.data.objects['Drawing | attentive']
add_gaze(head,character)
rig=next(m.object for m in head.modifiers if m.type=='ARMATURE')
eye=bpy.data.objects['Drawing | delighted eyes'];eye.animation_data_clear();eye.hide_render=True
scene.camera.data.ortho_scale=2.7
scene.camera.location.x=.65;scene.camera.location.z=1.75
scene.render.resolution_x=960;scene.render.resolution_y=960
scene.render.resolution_percentage=100;scene.cycles.samples=16
out=ROOT/('output/gaze-biscuit-v001' if character=='biscuit' else 'output/gaze-v002');out.mkdir(exist_ok=False)
for index,(x,y) in enumerate([(0,0),(-.5,-.7),(.5,.5)]):
    rig.pose.bones['HEAD']['gaze_x']=x;rig.pose.bones['HEAD']['gaze_y']=y
    rig.update_tag();bpy.context.view_layer.update()
    scene.render.filepath=str(out/f'gaze_{index}.png');bpy.ops.render.render(write_still=True)
bpy.ops.wm.save_as_mainfile(filepath=str(out/'gaze-audition.blend'))
