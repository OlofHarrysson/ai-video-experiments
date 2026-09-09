"""Prepare and reopen a copy whose external media paths cannot resolve."""
import argparse
import hashlib
import json
import sys
from pathlib import Path
import bpy

p=argparse.ArgumentParser();p.add_argument('--output',required=True);p.add_argument('--prepare',action='store_true')
args=p.parse_args(sys.argv[sys.argv.index('--')+1:])
out=Path(args.output).resolve()
if args.prepare:
    out.mkdir(exist_ok=False)
    for index,image in enumerate(bpy.data.images):
        if image.source=='FILE':
            assert image.packed_file
            image.filepath=f'//missing-source/image-{index}.png'
    for index,font in enumerate(bpy.data.fonts):
        if font.filepath and font.filepath!='<builtin>':
            assert font.packed_file
            font.filepath=f'//missing-source/font-{index}.ttf'
    for index,sound in enumerate(bpy.data.sounds):
        assert sound.packed_file
        sound.filepath=f'//missing-source/sound-{index}.wav'
    bpy.ops.wm.save_as_mainfile(filepath=str(out/'packed-only.blend'))
else:
    assert not (out/'packed-only.png').exists()
    report={'scene':bpy.data.filepath,'packed_files':[]}
    for category,datablocks in [('image',bpy.data.images),('font',bpy.data.fonts),('sound',bpy.data.sounds)]:
        for block in datablocks:
            if category=='image' and block.source!='FILE':continue
            if category=='font' and (not block.filepath or block.filepath=='<builtin>'):continue
            assert block.packed_file,block.name
            assert not Path(bpy.path.abspath(block.filepath)).exists(),block.filepath
            report['packed_files'].append({'kind':category,'name':block.name,
                'sha256':hashlib.sha256(block.packed_file.data).hexdigest()})
    scene=bpy.context.scene;scene.frame_set(384)
    scene.render.resolution_percentage=50;scene.cycles.samples=16
    scene.render.filepath=str(out/'packed-only.png');bpy.ops.render.render(write_still=True)
    (out/'packed-only-check.json').write_text(json.dumps(report,indent=2)+'\n')
    print('PACKED_ONLY',len(report['packed_files']),flush=True)
