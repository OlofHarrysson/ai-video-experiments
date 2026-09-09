"""Save reusable native pose actions, including each pose's drawing switches."""
import json
import sys
from pathlib import Path
import bpy
from mathutils import Vector

ROOT=Path(__file__).resolve().parent
out=Path(sys.argv[sys.argv.index('--')+1]).resolve();out.mkdir(exist_ok=False)
presets={'Biscuit':[('Attentive',81),('A little unsure',94),('Play bow',231),('Little hop',251),('Trusting greeting',380)],
         'Bruno':[('Attentive',70),('Invitation',140),('Gentle greeting',380)]}
captured={}
for name,choices in presets.items():
    rig=next(ob for ob in bpy.data.objects if ob.type=='ARMATURE' and ob.name.startswith(name+' /'))
    captured[name]=[]
    for label,frame in choices:
        bpy.context.scene.frame_set(frame)
        travel=rig.pose.bones['ROOT'].head.x
        bones={}
        for bone in rig.pose.bones:
            location=bone.location.copy()
            if bone.name=='ROOT' or bone.name.startswith('CTRL.paw.'):
                location-=rig.data.bones[bone.name].matrix_local.to_3x3().inverted()@Vector((travel,0,0))
            properties={prop:bone[prop] for prop in ['gaze_x','gaze_y'] if prop in bone}
            bones[bone.name]={'location':list(location),'rotation':list(bone.rotation_quaternion),
                             'scale':list(bone.scale),'properties':properties}
        captured[name].append({'name':label,'source_frame':frame,'removed_stage_travel':travel,'bones':bones,
                              'closed_eyes':bool(rig['closed_eyes']),'folded_forelegs':bool(rig['folded_forelegs'])})

bpy.ops.wm.open_mainfile(filepath=str(ROOT/'output/characters-v001/characters.blend'))
scene=bpy.context.scene
scene.render.resolution_x=640;scene.render.resolution_y=640;scene.render.resolution_percentage=100
scene.cycles.samples=16
camera=scene.camera;camera.data.ortho_scale=4.6;camera.location.z=1.45
defaults={};manifest=[]
for name,poses in captured.items():
    rig=next(ob for ob in bpy.data.objects if ob.type=='ARMATURE' and ob.name.startswith(name+' /'))
    rig.animation_data_create()
    collection=bpy.data.collections['01 Biscuit' if name=='Biscuit' else '02 Bruno']
    other=bpy.data.collections['02 Bruno' if name=='Biscuit' else '01 Biscuit']
    other.hide_render=True
    camera.location.x=bpy.data.objects[name+' | stage placement'].location.x
    for index,pose in enumerate(poses):
        rig.animation_data.action=None
        action=bpy.data.actions.new(name+' | '+pose['name'])
        rig.animation_data.action=action
        for bone_name,values in pose['bones'].items():
            bone=rig.pose.bones[bone_name]
            bone.location=values['location'];bone.rotation_quaternion=values['rotation'];bone.scale=values['scale']
            for field in ['location','rotation_quaternion','scale']:bone.keyframe_insert(field,frame=1,group=bone_name)
            for prop,value in values['properties'].items():
                bone[prop]=value;bone.keyframe_insert(data_path=f'["{prop}"]',frame=1,group=bone_name)
        for prop in ['closed_eyes','folded_forelegs']:
            rig[prop]=pose[prop];rig.keyframe_insert(data_path=f'["{prop}"]',frame=1,group='Drawing controls')
        action.asset_mark();action.use_fake_user=True
        action.asset_data.author='Olof / A Little Brave'
        action.asset_data.description=f'{name}: {pose["name"]}. Single-frame action including bone transforms and drawing controls. Assign in the Action Editor.'
        for tag in [name,'Pose preset','2D dog']:action.asset_data.tags.new(tag)
        rig.update_tag();scene.frame_set(1);bpy.context.view_layer.update()
        assert rig['closed_eyes']==pose['closed_eyes'] and rig['folded_forelegs']==pose['folded_forelegs']
        if index==0:defaults[name]=action
        filename=f'{name.lower()}-{index+1:02d}.png'
        scene.render.filepath=str(out/filename);bpy.ops.render.render(write_still=True)
        manifest.append({'character':name,'pose':pose['name'],'action':action.name,'image':filename,
                         'source_frame':pose['source_frame'],'closed_eyes':pose['closed_eyes'],
                         'folded_forelegs':pose['folded_forelegs']})
    other.hide_render=False
    rig.animation_data.action=defaults[name]
    rig.animation_data.action_slot=defaults[name].slots[0]

scene.frame_set(1);camera.location.x=0;camera.location.z=1.65;camera.data.ortho_scale=10.8
scene.render.resolution_x=1920;scene.render.resolution_y=1080
text=bpy.data.texts.get('START HERE');text.clear()
text.write('CHARACTER POSE PRESETS\n\nThis file contains eight single-frame native actions. Select a character armature, open the Dope Sheet in Action Editor mode, and choose an action starting with that character name. The action includes the folded-leg and closed-eye drawing controls as well as bone transforms.\n\nUse the separate characters.blend stage for freely posing an unanimated rig. These side-view painted assets support the demonstrated bow, hop and greeting poses; they are not general 3D characters.\n')
bpy.ops.wm.save_as_mainfile(filepath=str(out/'character-actions.blend'))
(out/'presets.json').write_text(json.dumps(captured,indent=2)+'\n')
(out/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
print('POSE_CATALOG',len(manifest),str(out),flush=True)
