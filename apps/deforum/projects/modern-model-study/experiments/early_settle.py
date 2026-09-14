"""A seven-painting recurrent branch from the accepted city reveal."""
import argparse
import json
from pathlib import Path
import shutil

import numpy as np
from PIL import Image

import dynamic_journey as journey
import dynamic_journey_finish as finish

HERE = Path(__file__).resolve().parent
OLD = HERE.parent / 'exports/hold-transform-v001/low-hold'
OUT = HERE.parent / 'exports/early-settle-v001'
CASE = 'early-settle'
CONFIG = HERE / 'early-settle-config.json'
base = journey.base


def configure():
    journey.OUT = base.OUT = OUT


def copy_verified(source, target):
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists():
        assert base.sha(target) == base.sha(source), target
    else:
        shutil.copy2(source, target)


def prepare():
    old = json.loads((OLD/'config.json').read_text())
    config = {**old, 'case': CASE, 'noise_schedule': [
        *[p for p in old['noise_schedule'] if p['at'] <= 4],
        {'at':4.5,'noise':.25}, {'at':5,'noise':.1}, {'at':8,'noise':.1}]}
    base.save(CONFIG,config);base.save(OUT/CASE/'config.json',config)
    rows=[]
    for f in range(0,97,12):
        source=OLD/f'anchors/{f:04d}.png';target=OUT/CASE/f'anchors/{f:04d}.png'
        copy_verified(source,target)
        rows.append({'frame':f,'source':str(source.relative_to(journey.APP)),'sha256':base.sha(source)})
    base.save(OUT/CASE/'prefix.json',{'through_frame':96,'paintings':rows})
    rec=json.loads((OLD/'anchor-0108.json').read_text());run=OLD.parent/rec['run']
    copy_verified(run/'workflow.api.json',OUT/'control/workflow.api.json')
    copy_verified(OLD/'warped-inputs/0108.png',OUT/'control/input.png')
    copy_verified(OLD/'anchors/0108.png',OUT/'control/expected.png')


def render():
    root=OUT/CASE;config=json.loads((root/'config.json').read_text())
    for row in json.loads((root/'prefix.json').read_text())['paintings']:
        assert base.sha(root/f'anchors/{row["frame"]:04d}.png')==row['sha256']
    g=json.loads((OUT/'control/workflow.api.json').read_text())
    control=base.submit_once('early-settle-runtime-control',g,OUT/'control/input.png',
        {'parent_sha256':base.sha(root/'anchors/0096.png'),'frame':108,'seconds':4.5})
    same=np.array_equal(np.asarray(Image.open(control/'frames/0000.png')),
                        np.asarray(Image.open(OUT/'control/expected.png')))
    base.save(OUT/'control/replay.json',{'pixel_identical':same,'run':str(control.relative_to(OUT))})
    if not same:
        raise RuntimeError('Original repaint did not reproduce; inspect before continuing')
    for f in range(108,181,12):
        t=f/24;parent=root/f'anchors/{f-12:04d}.png';target=root/f'anchors/{f:04d}.png'
        source=root/f'warped-inputs/{f:04d}.png';source.parent.mkdir(exist_ok=True)
        scene,sigmas=journey.recipe(config,t);seed=config['seed']+f//12
        g=base.repaint_graph(scene['prompt'],seed,sigmas)
        g['11']['inputs']['filename_prefix']='early-settle/'+CASE
        receipt=root/f'anchor-{f:04d}.json'
        if receipt.exists():
            row=json.loads(receipt.read_text());run=OUT/row['run']
            assert row['parent_sha256']==base.sha(parent) and row['output_sha256']==base.sha(target)
            assert json.loads((run/'workflow.api.json').read_text())==g
            continue
        Image.fromarray(journey.warp(np.asarray(Image.open(parent).convert('RGB')),t-.5,t,config['phrases'])).save(source)
        run=base.submit_once(f'early-settle-{f:04d}',g,source,
            {'parent_sha256':base.sha(parent),'initialization_sha256':base.sha(source),
             'frame':f,'seconds':t,'scene':scene['name'],'sigma_start':sigmas[0]})
        copy_verified(run/'frames/0000.png',target)
        base.save(receipt,{'run':str(run.relative_to(OUT)),'frame':f,'seconds':t,'seed':seed,
            'scene':scene['name'],'sigmas':sigmas,'parent_sha256':base.sha(parent),
            'initialization_sha256':base.sha(source),'output_sha256':base.sha(target)})
        print(f'Painting {f}: noise {sigmas[0]:.2f}',flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('stage',choices=['prepare','render','pair','full','sheets'])
    p.add_argument('--deployment',type=Path);args=p.parse_args();configure()
    if args.stage=='prepare':prepare()
    elif args.stage=='render':
        if not args.deployment:p.error('render requires --deployment')
        base.pod_client.DEPLOYMENT=args.deployment.resolve();render()
    else:finish.run(CASE,'prepare' if args.stage=='sheets' else args.stage)
