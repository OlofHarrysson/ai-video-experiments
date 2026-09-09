"""Reopen and assign every native pose action, checking its drawing drivers."""
import json
import sys
from pathlib import Path
import bpy

root=Path(sys.argv[sys.argv.index('--')+1]).resolve()
out=root/'reopened-check.json';assert not out.exists()
manifest=json.loads((root/'manifest.json').read_text())
presets=json.loads((root/'presets.json').read_text())
rows=[]
for entry in manifest:
    name=entry['character']
    pose=next(pose for pose in presets[name] if pose['name']==entry['pose'])
    rig=next(ob for ob in bpy.data.objects if ob.type=='ARMATURE' and ob.name.startswith(name+' /'))
    action=bpy.data.actions[entry['action']]
    rig.animation_data.action=action;rig.animation_data.action_slot=action.slots[0]
    bpy.context.scene.frame_set(1);bpy.context.view_layer.update()
    assert action.asset_data and len(action.slots)==1
    for prop in ['closed_eyes','folded_forelegs']:assert rig[prop]==pose[prop]
    assert bpy.data.objects[name+' / Drawing | delighted eyes'].hide_render==(not pose['closed_eyes'])
    assert bpy.data.objects[name+' / Paint | front.near'].hide_render==pose['folded_forelegs']
    maximum=0.
    for bone_name,values in pose['bones'].items():
        bone=rig.pose.bones[bone_name]
        for field,expected in [('location',values['location']),('rotation_quaternion',values['rotation']),('scale',values['scale'])]:
            maximum=max(maximum,max(abs(a-b) for a,b in zip(getattr(bone,field),expected)))
    assert maximum<1e-5,(entry,maximum)
    rows.append({'action':action.name,'maximum_channel_difference':maximum,'drawing_drivers':True})
out.write_text(json.dumps({'scene':bpy.data.filepath,'poses':rows},indent=2)+'\n')
print('POSE_REOPEN',len(rows),max(row['maximum_channel_difference'] for row in rows),flush=True)
