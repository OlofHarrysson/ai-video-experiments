"""Append each character asset into a fresh scene and exercise its controls."""
import json
import math
import sys
from pathlib import Path
import bpy
from mathutils import Quaternion,Vector

root=Path(sys.argv[sys.argv.index('--')+1]).resolve()
out=root/'roundtrip';out.mkdir(exist_ok=False)
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
scene=bpy.context.scene
report=[]
for name,collection_name,x,scale,facing in [('Biscuit','01 Biscuit',-2.1,.8,1),('Bruno','02 Bruno',1.9,1.1,-1)]:
    with bpy.data.libraries.load(str(root/(name.lower()+'-asset.blend'))) as (src,dst):
        dst.collections=[collection_name]
    collection=dst.collections[0];scene.collection.children.link(collection)
    rig=next(ob for ob in collection.objects if ob.type=='ARMATURE')
    stage=next(ob for ob in collection.objects if ob.type=='EMPTY')
    stage.location=(x,0,0);stage.scale=(scale*facing,scale,scale)
    assert len(rig.data.bones)==24
    assert not (rig.animation_data and rig.animation_data.action)
    for ob in collection.objects:
        for modifier in ob.modifiers:
            if modifier.type=='ARMATURE':assert modifier.object==rig
    rig['closed_eyes']=True;rig['folded_forelegs']=True
    for bone_name,angle in [('BODY',23),('HEAD',-24)]:
        bone=rig.pose.bones[bone_name];rest=rig.data.bones[bone_name].matrix_local.to_quaternion()
        bone.rotation_quaternion=rest.inverted()@Quaternion((0,1,0),math.radians(angle))@rest
    rig.pose.bones['ROOT'].location=rig.data.bones['ROOT'].matrix_local.to_3x3().inverted()@Vector((0,0,-.23))
    for side in ['near','far']:
        bone_name='CTRL.paw.front.'+side
        rig.pose.bones[bone_name].location=rig.data.bones[bone_name].matrix_local.to_3x3().inverted()@Vector((.23,0,0))
    rig.update_tag();bpy.context.view_layer.update()
    assert not bpy.data.objects[name+' / Drawing | delighted eyes'].hide_render
    assert bpy.data.objects[name+' / Paint | front.near'].hide_render
    assert not bpy.data.objects[name+' / Drawing | folded front.near'].hide_render
    report.append({'character':name,'collection':collection.name,'bones':24,'drawing_controls':True,'native_modifiers':True})
assert all(image.packed_file for image in bpy.data.images if image.source=='FILE')
data=bpy.data.cameras.new('Roundtrip camera');camera=bpy.data.objects.new('Roundtrip camera',data)
scene.collection.objects.link(camera);camera.location=(0,-15,1.45)
camera.rotation_euler=(Vector((0,0,1.45))-camera.location).to_track_quat('-Z','Y').to_euler()
data.type='ORTHO';data.ortho_scale=9.6;scene.camera=camera
scene.render.engine='CYCLES';scene.cycles.samples=16;scene.cycles.use_denoising=False;scene.cycles.transparent_max_bounces=32
scene.render.resolution_x=1920;scene.render.resolution_y=1080;scene.render.resolution_percentage=50
scene.view_settings.view_transform='Standard'
world=bpy.data.worlds.new('Paper');world.use_nodes=True
world.node_tree.nodes['Background'].inputs[0].default_value=(.925,.889,.800,1);scene.world=world
bpy.ops.wm.save_as_mainfile(filepath=str(out/'appended-characters.blend'))
scene.render.filepath=str(out/'posed-characters.png');bpy.ops.render.render(write_still=True)
(out/'check.json').write_text(json.dumps(report,indent=2)+'\n')
print('ASSET_ROUNDTRIP',report,flush=True)
