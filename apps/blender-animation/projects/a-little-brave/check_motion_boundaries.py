"""Check continuity where source actions meet and stability during foot plants."""
import json
import math
import sys
from pathlib import Path
import bpy

out=Path(sys.argv[sys.argv.index('--')+1]).resolve();assert not out.exists()
scene=bpy.context.scene
rig=next(ob for ob in scene.objects if ob.type=='ARMATURE' and ob.name.startswith('Biscuit'))
rows=[]
for start in [81,210,282]:
    poses=[]
    for frame in [start-1,start]:
        scene.frame_set(frame)
        poses.append({bone.name:(bone.location.copy(),bone.rotation_quaternion.copy()) for bone in rig.pose.bones})
    rotations={name:math.degrees(poses[0][name][1].rotation_difference(poses[1][name][1]).angle) for name in poses[0]}
    translations={name:(poses[0][name][0]-poses[1][name][0]).length for name in poses[0]}
    rows.append({'frame':start,'maximum_rotation_degrees':max(rotations.values()),
                 'maximum_translation':max(translations.values()),'rotations':rotations})
    assert max(rotations.values())<3.0,(start,rotations)
    assert max(translations.values())<.01,(start,translations)
plants=[];previous={}
for frame in range(1,scene.frame_end+1):
    scene.frame_set(frame)
    for rig in [ob for ob in scene.objects if ob.type=='ARMATURE']:
        for name in ['front.near','front.far','back.near','back.far']:
            key=(rig.name,name)
            actual=rig.matrix_world@rig.pose.bones['paw.'+name].head
            target=rig.matrix_world@rig.pose.bones['CTRL.paw.'+name].head
            planted_height=(rig.matrix_world@rig.data.bones['CTRL.paw.'+name].head_local).z
            if key in previous:
                old_actual,old_target=previous[key]
                if (target-old_target).length<1e-6 and abs(target.z-planted_height)<.001:
                    plants.append({'frame':frame,'rig':rig.name,'paw':name,'drift':(actual-old_actual).length})
            previous[key]=(actual.copy(),target.copy())
worst=max(plants,key=lambda row:row['drift'])
assert worst['drift']<.002,worst
report={'scene':bpy.data.filepath,'boundaries':rows,'planted_frame_pairs':len(plants),'maximum_plant_drift':worst,
        'scope':'Native pose continuity and held paw controls; not a perceptual smoothness score.'}
out.write_text(json.dumps(report,indent=2)+'\n')
print('CONTINUITY',[(r['frame'],r['maximum_rotation_degrees']) for r in rows],worst,flush=True)
