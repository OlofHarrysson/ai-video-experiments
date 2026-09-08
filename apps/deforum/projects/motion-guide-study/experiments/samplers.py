"""Controlled sampler alternatives; reuse the accepted twist/cadence implementation."""
import argparse
import json
from pathlib import Path
import shutil
import numpy as np
from PIL import Image
import repaint_controls as previous

seq, recipe = previous.seq, previous.recipe
OUT = seq.PROJECT/'exports/samplers-v001'
BASELINE = previous.OUT/'d045'
VARIANTS = {'baseline':'dpmpp_2m', 'euler':'euler', 'ancestral':'euler_ancestral'}
FRAMES, FPS, CADENCE = 36, 12, 3


def graph(name, frame):
    g=previous.graph('d045',frame,.45)
    g['6']['inputs']['sampler_name']=VARIANTS[name]
    g['11']['inputs']['filename_prefix']='samplers/'+name
    return g


def prepare():
    OUT.mkdir(parents=True,exist_ok=False)
    seq.save(OUT/'manifest.json',{'variants':VARIANTS,'frames':FRAMES,'fps':FPS,'cadence':CADENCE,
        'opening_sha256':recipe.sha(seq.OPENING),'script_sha256':recipe.sha(Path(__file__)),
        'motion_script_sha256':recipe.sha(Path(seq.__file__)),
        'extra_pixel_noise':False,'sampling_mask':False,'rife':False})
    for name in VARIANTS:
        root=OUT/name
        for sub in ('anchors','warped-inputs','cadence/frames'):(root/sub).mkdir(parents=True)
        shutil.copyfile(seq.OPENING,root/'anchors/0000.png')
        seq.save(root/'manifest.json',{'graph':graph(name,3),'kind':'reused reference' if name=='baseline' else 'new feedback'})
    a=graph('baseline',3);b=json.loads((BASELINE/'manifest.json').read_text())['graph'];a['11']=b['11'];assert a==b
    for f in range(3,FRAMES+1,3):
        record=json.loads((BASELINE/f'anchor-{f:04d}.json').read_text());assert recipe.sha(BASELINE/f'anchors/{f:04d}.png')==record['sha256']
        shutil.copyfile(BASELINE/f'anchors/{f:04d}.png',OUT/f'baseline/anchors/{f:04d}.png')
        seq.save(OUT/f'baseline/anchor-{f:04d}.json',{**record,'reused_from':str(BASELINE.relative_to(seq.PROJECT))})
    finish('baseline')


def finish(name):
    previous.OUT=OUT
    previous.finish(name)


def render(name):
    root=OUT/name
    assert json.loads((root/'manifest.json').read_text())['graph']==graph(name,3)
    for f in range(3,FRAMES+1,3):
        target=root/f'anchors/{f:04d}.png';record=root/f'anchor-{f:04d}.json'
        if target.exists():
            assert recipe.sha(target)==json.loads(record.read_text())['sha256'];continue
        moved=seq.warp(np.asarray(Image.open(root/f'anchors/{f-3:04d}.png').convert('RGB')),f-3,f)
        source=root/f'warped-inputs/{f:04d}.png'
        if source.exists():assert np.array_equal(np.asarray(Image.open(source)),moved)
        else:Image.fromarray(moved).save(source)
        run=seq.shared.accepted_run(f'samplers-v001-{name}-{f:04d}',graph(name,f),1,source,
            {'study':'samplers-v001','variant':name,'timeline_frame':f,'fps':FPS,'cadence':CADENCE})
        rendered=run/'frames/0000.png'
        if not record.exists():seq.save(record,{'run':str(run.relative_to(seq.PROJECT)),'sha256':recipe.sha(rendered)})
        shutil.copyfile(rendered,target);print(name,f//3,'/12',flush=True)
    finish(name)


def probe():
    run=seq.shared.accepted_run('samplers-v001-reference-probe',graph('baseline',3),1,BASELINE/'warped-inputs/0003.png',
        {'study':'samplers-v001','purpose':'validate reused baseline'})
    expected=OUT/'baseline/anchors/0003.png';actual=run/'frames/0000.png'
    same=np.array_equal(np.asarray(Image.open(expected)),np.asarray(Image.open(actual)))
    seq.save(OUT/'reference-probe.json',{'pixel_equal':bool(same),'run':str(run.relative_to(seq.PROJECT)),
        'expected_sha256':recipe.sha(expected),'actual_sha256':recipe.sha(actual)})
    assert same,'Baseline mismatch; investigate before ranking samplers'
    print('Fresh baseline probe matches archived first anchor exactly.',flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('stage',choices=('prepare','probe','render','finish'));p.add_argument('--variant',choices=tuple(VARIANTS),default='euler');a=p.parse_args()
    if a.stage in ('render','finish'):globals()[a.stage](a.variant)
    else:globals()[a.stage]()
