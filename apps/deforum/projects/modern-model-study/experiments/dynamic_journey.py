"""Recurrent scene changes, composed motion phrases, and resumable section rendering."""
import argparse
import json
from pathlib import Path
import shutil

import numpy as np
from PIL import Image

import ten_dollar as base

APP = base.APP
OUT = Path(__file__).resolve().parents[1]/'exports/dynamic-journey-v001'
base.OUT = OUT
FPS, CADENCE = 24, 12


def mapping(points, seconds, phrases, inverse=False):
    selected = reversed(phrases) if inverse else phrases
    for phrase in selected:
        motion = {**phrase, 'settle':phrase['duration'], 'travel_window':[0,phrase['duration']]}
        points = base.transform(points, max(0.,seconds-phrase['start']), motion, inverse)
    return points


def warp(rgb, start, end, phrases):
    if start == end:
        return rgb.copy()
    h,w = rgb.shape[:2]
    y,x = np.mgrid[:h,:w].astype(np.float32)
    points = np.stack([x/h,y/h],-1)
    coords = mapping(mapping(points,end,phrases,True),start,phrases)*h
    return base.remap_rgb(rgb,coords.astype(np.float32))


def recipe(config, seconds):
    scene = [s for s in config['scenes'] if s['at'] <= seconds][-1]
    age = seconds-scene['at']
    if 'transition_ramp' in config:
        repaint = round((seconds-max(scene['at'], .5))*2)
        ramp = config['transition_ramp']
        noise = ramp[repaint] if 0 <= repaint < len(ramp) else config['settle_noise']
    else:
        noise = config['transition_noise'] if age <= 1.5 else config['settle_noise']
    return scene, [s*noise/.6 for s in base.SIGMAS]


def render(config, through):
    root = OUT/config['case']
    base.save(root/'config.json',config)
    (root/'anchors').mkdir(parents=True,exist_ok=True)
    seed_image = OUT/'source/seed.png'
    opening = root/'anchors/0000.png'
    if opening.exists():
        assert base.sha(opening) == base.sha(seed_image)
    else:
        shutil.copy2(seed_image,opening)
    base.save(root/'opening.json',{'source':config['source'], 'source_sha256':base.sha(seed_image),
        'initialization':'same-model continuation from the previous saved snail painting'})
    last = round(config['duration']*FPS)-CADENCE
    if through is not None:
        requested=round(through*FPS)
        if abs(requested-through*FPS)>1e-6 or requested%CADENCE:
            raise ValueError('Section endpoint must lie on a half-second painting')
        last=min(last,requested)
    for f in range(CADENCE,last+1,CADENCE):
        seconds=f/FPS
        parent=root/f'anchors/{f-CADENCE:04d}.png'
        target=root/f'anchors/{f:04d}.png'
        receipt=root/f'anchor-{f:04d}.json'
        scene,sigmas=recipe(config,seconds)
        seed=config['seed']+f//CADENCE
        g=base.repaint_graph(scene['prompt'],seed,sigmas)
        g['11']['inputs']['filename_prefix']='dynamic-journey/'+config['case']
        if receipt.exists():
            row=json.loads(receipt.read_text()); run=OUT/row['run']
            assert row['parent_sha256']==base.sha(parent) and row['output_sha256']==base.sha(target)
            assert json.loads((run/'workflow.api.json').read_text())==g
            print(f'Reusing verified painting {seconds:.1f}s',flush=True)
            continue
        source=root/f'warped-inputs/{f:04d}.png';source.parent.mkdir(exist_ok=True)
        Image.fromarray(warp(np.asarray(Image.open(parent).convert('RGB')),seconds-.5,seconds,config['phrases'])).save(source)
        run=base.submit_once(f'dynamic-{config["case"]}-{f:04d}',g,source,
            {'parent_sha256':base.sha(parent),'frame':f,'seconds':seconds,'scene':scene['name'],
             'sigma_start':sigmas[0],'initialization':'warped previous painting; recurrent loop intact'})
        shutil.copy2(run/'frames/0000.png',target)
        base.save(receipt,{'run':str(run.relative_to(OUT)),'frame':f,'seconds':seconds,'seed':seed,
            'scene':scene['name'],'sigmas':sigmas,'parent_sha256':base.sha(parent),
            'initialization_sha256':base.sha(source),'output_sha256':base.sha(target)})
        print(f'{config["case"]}: {seconds:.1f}s, {scene["name"]}, noise {sigmas[0]:.2f}',flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('config',type=Path)
    p.add_argument('--deployment',required=True,type=Path);p.add_argument('--through',type=float)
    args=p.parse_args();base.pod_client.DEPLOYMENT=args.deployment.resolve()
    render(json.loads(args.config.read_text()),args.through)
