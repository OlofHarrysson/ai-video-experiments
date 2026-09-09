"""Create an editable neutral character stage and reusable collection assets."""
import math
import sys
from pathlib import Path
import bpy
from mathutils import Vector

out=Path(sys.argv[sys.argv.index('--')+1]).resolve()
out.mkdir(parents=True,exist_ok=True)
assert not (out/'characters.blend').exists()
scene=bpy.context.scene;scene.frame_set(1)
scene.sequence_editor_clear()
scene.timeline_markers.clear()
scene.frame_start=1;scene.frame_end=72
scene.name='Biscuit and Bruno | character stage'
collections=[bpy.data.collections['01 Biscuit'],bpy.data.collections['02 Bruno']]
keep={ob for collection in collections for ob in collection.objects}
shadows=[bpy.data.objects['Set | '+name+' contact shadow'] for name in ['Biscuit','Bruno']]
keep.update(shadows)
for ob in list(scene.objects):
    if ob not in keep:bpy.data.objects.remove(ob,do_unlink=True)
for collection in list(scene.collection.children):
    if not collection.objects:bpy.data.collections.remove(collection)
for name,x,scale,collection,shadow in zip(['Biscuit','Bruno'],[-2.4,1.65],[.8,1.1],collections,shadows):
    root=bpy.data.objects[name+' | stage placement']
    source_scale=abs(root.scale.x)
    root.location=(x,0,0);root.scale=(scale,scale,scale)
    for ob in collection.objects:
        if ob.animation_data:
            ob.animation_data.action=None
            for track in list(ob.animation_data.nla_tracks):ob.animation_data.nla_tracks.remove(track)
        if ob.type=='ARMATURE':
            for bone in ob.pose.bones:
                bone.location=(0,0,0);bone.rotation_quaternion=(1,0,0,0);bone.scale=(1,1,1)
            ob['closed_eyes']=False;ob['folded_forelegs']=False
            if name=='Bruno':
                ob.pose.bones['HEAD']['gaze_x']=.3;ob.pose.bones['HEAD']['gaze_y']=0.
            ob.update_tag()
    shadow.animation_data_clear();shadow.location=(x,0,0);shadow.scale=(scale/source_scale,1,1)
    collection.asset_mark()
    collection.asset_data.author='Olof / A Little Brave'
    collection.asset_data.description=f'{name}: a painted 2D dog with 24 bones, paw IK, ear and tail controls, and expression drawing switches. Artwork is packed.'
    for tag in ['2D','Character','Dog','Rigged','A Little Brave']:collection.asset_data.tags.new(tag)
    bpy.data.libraries.write(str(out/(name.lower()+'-asset.blend')),{collection},path_remap='RELATIVE_ALL',fake_user=True)

data=bpy.data.cameras.new('Character stage camera')
camera=bpy.data.objects.new('Character stage camera',data);scene.collection.objects.link(camera)
camera.location=(0,-15,1.65)
camera.rotation_euler=(Vector((0,0,1.65))-camera.location).to_track_quat('-Z','Y').to_euler()
data.type='ORTHO';data.ortho_scale=10.8;scene.camera=camera
world=bpy.data.worlds.new('Warm paper');world.use_nodes=True
world.node_tree.nodes['Background'].inputs[0].default_value=(.925,.889,.800,1)
world.node_tree.nodes['Background'].inputs[1].default_value=1
scene.world=world;scene.render.film_transparent=False
scene.render.use_sequencer=False;scene.render.resolution_percentage=100
scene['description']='Reusable native 2D character stage. Both collections are marked as assets. No performance is applied.'
text=bpy.data.texts.get('START HERE') or bpy.data.texts.new('START HERE')
text.clear()
text.write('BISCUIT AND BRUNO\n\nBoth collections are reusable assets. Open this stage to pose them, or append the character collection from either individual asset file into another scene.\n\nSelect a pose-controls armature and enter Pose Mode. Enable viewport overlays to see the bones. ROOT moves the torso; CTRL.paw.* controls hold the feet. BODY and HEAD rotate around their drawn joints. Ears and tail have separate controls.\n\nObject custom properties: closed_eyes and folded_forelegs switch drawings. Bruno HEAD bone custom properties: gaze_x and gaze_y move the iris. All image dependencies are packed. The underlying painted cutout art has a fixed side view.\n')
bpy.ops.object.select_all(action='DESELECT')
rig=next(ob for ob in collections[0].objects if ob.type=='ARMATURE')
rig.select_set(True);bpy.context.view_layer.objects.active=rig
bpy.context.view_layer.update()
bpy.ops.outliner.orphans_purge(do_recursive=True)
bpy.ops.wm.save_as_mainfile(filepath=str(out/'characters.blend'))
scene.render.filepath=str(out/'characters.png');bpy.ops.render.render(write_still=True)
print('CHARACTER_ASSETS',str(out),flush=True)
