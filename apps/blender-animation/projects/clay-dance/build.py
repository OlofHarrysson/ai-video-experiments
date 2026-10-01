"""blender -b --python build.py -- --version v001 --stills 1,37,73,145,181,289"""
import argparse
import importlib.util
import json
import shutil
import sys
from pathlib import Path
import bpy

ROOT=Path(__file__).resolve().parent
def module(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    result=importlib.util.module_from_spec(spec);spec.loader.exec_module(result);return result
kit=module('clay_stage',ROOT.parent.parent/'tools/clay_stage.py')
choreo=module('choreography',ROOT/'choreography.py')
p=argparse.ArgumentParser();p.add_argument('--version',required=True);p.add_argument('--stills',default='');p.add_argument('--percentage',type=int,default=60)
args=p.parse_args(sys.argv[sys.argv.index('--')+1:])
out=ROOT/'output'/args.version
if out.exists():raise FileExistsError('Use a fresh version to preserve earlier attempts')
out.mkdir(parents=True)
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
scene=kit.stage();scene.render.fps=choreo.FPS
scene.frame_start=1;scene.frame_end=choreo.FPS*choreo.SECTION_SECONDS*3
ochre=kit.clay('Pip | warm ochre',(.64,.31,.065))
cocoa=kit.clay('Pip | dark cinnamon',(.22,.064,.032))
blue=kit.clay('Bo | dusty blue',(.065,.31,.39))
coral=kit.clay('Bo | coral',(.62,.15,.1))
puppets=[kit.Puppet('PIP','dog',(-1.35,0,0),ochre,cocoa),kit.Puppet('BO','rabbit',(1.25,.12,0),blue,coral)]
rows=[]
for f in range(1,scene.frame_end+1,2):
    seconds=(f-1)/choreo.FPS
    section=int(seconds/choreo.SECTION_SECONDS)
    move=choreo.MOVES[section]
    local=seconds%choreo.SECTION_SECONDS
    row={'frame':f,'move':move,'characters':[]}
    for i,puppet in enumerate(puppets):
        state=choreo.pose(move,local,i)
        row['characters'].append({'name':puppet.name,'pose':state,'limbs':puppet.pose(state,f)})
    rows.append(row)
kit.set_interpolation('CONSTANT')
for i,label in enumerate(choreo.MOVES):
    scene.timeline_markers.new(label.upper(),frame=1+i*choreo.SECTION_SECONDS*choreo.FPS)
scene['beat_bpm']=choreo.BPM;scene['pose_fps']=12;scene['project']='Side by Side'
scene.frame_set(25)
scene.render.resolution_percentage=100
bpy.ops.wm.save_as_mainfile(filepath=str(out/'clay-dance.blend'))
source=out/'source';source.mkdir()
for path in [Path(__file__),ROOT/'choreography.py',ROOT.parent.parent/'tools/clay_stage.py']:
    shutil.copy2(path,source/path.name)
(out/'motion.json').write_text(json.dumps({'fps':24,'duration':18,'cadence':12,'bpm':120,'samples':rows},indent=2)+'\n')
scene.render.resolution_percentage=args.percentage
scene.cycles.samples=24
for f in [int(x) for x in args.stills.split(',') if x]:
    scene.frame_set(f);scene.render.filepath=str(out/'stills'/f'{f:04d}.png')
    bpy.ops.render.render(write_still=True)
print('BUILD_COMPLETE',str(out),flush=True)
