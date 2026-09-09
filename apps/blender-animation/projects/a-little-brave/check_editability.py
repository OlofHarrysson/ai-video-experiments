"""Verify packed dependencies and drawing controls in a reopened film."""
import json
import sys
from pathlib import Path
import bpy

scene=bpy.context.scene
out=Path(sys.argv[sys.argv.index('--')+1]).resolve()
assert not out.exists()
report={'scene':bpy.data.filepath,'frames':scene.frame_end,'images':[],
        'fonts':[],'sounds':[],'characters':{},'drawing_frames_checked':0}
for image in bpy.data.images:
    if image.source=='FILE':
        assert image.packed_file,image.name
        report['images'].append({'name':image.name,'size':list(image.size),'packed':True})
for font in bpy.data.fonts:
    if font.filepath and font.filepath!='<builtin>':
        assert font.packed_file,font.name
        report['fonts'].append({'name':font.name,'packed':True})
for sound in bpy.data.sounds:
    assert sound.packed_file,sound.name
    report['sounds'].append({'name':sound.name,'packed':True})
rigs=[ob for ob in scene.objects if ob.type=='ARMATURE']
assert len(rigs)==2
for rig in rigs:
    name=rig.name.split(' / ')[0]
    assert rig.animation_data.action
    report['characters'][name]={'bones':len(rig.data.bones),'action':rig.animation_data.action.name,
                               'drawing_controls':['closed_eyes','folded_forelegs']}
    for f in range(1,scene.frame_end+1):
        scene.frame_set(f)
        assert bpy.data.objects[name+' / Drawing | delighted eyes'].hide_render == (not rig['closed_eyes'])
        for side in ['near','far']:
            assert bpy.data.objects[name+' / Paint | front.'+side].hide_render == rig['folded_forelegs']
            assert bpy.data.objects[name+' / Drawing | folded front.'+side].hide_render == (not rig['folded_forelegs'])
        report['drawing_frames_checked']+=1
    for ob in scene.objects:
        if ob.name.startswith(name+' /') and ob.animation_data:
            for driver in ob.animation_data.drivers:
                assert driver.driver.is_valid,(ob.name,driver.data_path)
report['camera_cuts']=[{'frame':m.frame,'camera':m.camera.name} for m in scene.timeline_markers if m.camera]
report['title']=bpy.data.objects['Title | A Little Brave'].data.body
out.write_text(json.dumps(report,indent=2)+'\n')
print('EDITABILITY',len(report['images']),len(report['fonts']),len(report['sounds']),report['drawing_frames_checked'],flush=True)
