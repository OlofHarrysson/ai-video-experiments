"""Matched step-count and regional input-noise feedback test; no protection mask."""
import argparse
from concurrent.futures import ThreadPoolExecutor
import json
from pathlib import Path
import shutil

import numpy as np
from PIL import Image, ImageDraw, ImageFont
import repaint_controls as previous

seq, recipe = previous.seq, previous.recipe
OUT = seq.PROJECT/'exports/noise-steps-v001'
FRAMES, FPS, CADENCE, DENOISE = 36, 12, 3, .45
VARIANTS = {'clean18':(18,0), 'clean36':(36,0), 'noise18':(18,.06), 'noise36':(36,.06), 'half36':(36,.03)}


def graph(name, f):
    g = seq.graph(f)
    g['6']['inputs'].update(denoise=DENOISE, steps=VARIANTS[name][0])
    g['11']['inputs']['filename_prefix']='noise-steps/'+name
    return g


def prepare_variant(name):
    root=OUT/name
    root.mkdir(exist_ok=False)
    for sub in ('anchors','clean-warped-inputs','warped-inputs','cadence/frames'):(root/sub).mkdir(parents=True)
    shutil.copyfile(seq.OPENING,root/'anchors/0000.png')
    seq.save(root/'manifest.json',{'steps':VARIANTS[name][0],'noise_std':VARIANTS[name][1],
        'denoise':DENOISE,'graph':graph(name,3),'kind':'reused baseline' if name=='clean18' else 'new feedback'})


def prepare():
    OUT.mkdir(parents=True,exist_ok=False)
    seq.save(OUT/'manifest.json',{'frames':FRAMES,'fps':FPS,'cadence':CADENCE,'denoise':DENOISE,
        'variants':VARIANTS,'opening_sha256':recipe.sha(seq.OPENING),'script_sha256':recipe.sha(Path(__file__)),
        'motion_script_sha256':recipe.sha(Path(seq.__file__)),
        'noise_seed':previous.NOISE_SEED,'noise_region':'fixed top-right, 64px feather',
        'noise_kind':'Gaussian pixel noise shared across RGB, before VAE encoding',
        'sampling_mask':False,'pixel_copyback':False,'rife':False})
    _,weight=previous.regions();Image.fromarray(np.rint(weight*255).astype('uint8')).save(OUT/'noise-region.png')
    for name in ('clean18','clean36','noise18','noise36'):prepare_variant(name)
    source=previous.OUT/'d045'
    a=graph('clean18',3);b=json.loads((source/'manifest.json').read_text())['graph']
    a['11']=b['11'];assert a==b
    for f in range(3,37,3):
        record=json.loads((source/f'anchor-{f:04d}.json').read_text());assert recipe.sha(source/f'anchors/{f:04d}.png')==record['sha256']
        shutil.copyfile(source/f'anchors/{f:04d}.png',OUT/f'clean18/anchors/{f:04d}.png')
        seq.save(OUT/f'clean18/anchor-{f:04d}.json',{**record,'reused_from':str(source.relative_to(seq.PROJECT))})
    finish('clean18')


def render(name):
    root=OUT/name
    if not root.exists():prepare_variant(name)
    assert json.loads((root/'manifest.json').read_text())['graph']==graph(name,3)
    _,weight=previous.regions();std=VARIANTS[name][1]
    for f in range(3,37,3):
        target=root/f'anchors/{f:04d}.png';record=root/f'anchor-{f:04d}.json'
        if target.exists():
            assert recipe.sha(target)==json.loads(record.read_text())['sha256'];continue
        rgb=np.asarray(Image.open(root/f'anchors/{f-3:04d}.png').convert('RGB'))
        moved=seq.warp(rgb,f-3,f)
        clean=root/f'clean-warped-inputs/{f:04d}.png'
        if not clean.exists():Image.fromarray(moved).save(clean)
        if std:
            added=np.random.default_rng(previous.NOISE_SEED+f//3).standard_normal((recipe.HEIGHT,recipe.WIDTH,1))*std*weight[:,:,None]
            moved=np.rint(np.clip(moved.astype('float32')/255+added,0,1)*255).astype('uint8')
        source=root/f'warped-inputs/{f:04d}.png'
        if source.exists():assert np.array_equal(np.asarray(Image.open(source)),moved)
        else:Image.fromarray(moved).save(source)
        run=seq.shared.accepted_run(f'noise-steps-v001-us-{name}-{f:04d}',graph(name,f),1,source,
            {'study':'noise-steps-v001','variant':name,'timeline_frame':f,'fps':FPS,'cadence':CADENCE,
             'steps':VARIANTS[name][0],'noise_std':std,'denoise':DENOISE,'sampling_seed':recipe.SEED+f//3})
        rendered=run/'frames/0000.png'
        if not record.exists():seq.save(record,{'run':str(run.relative_to(seq.PROJECT)),'sha256':recipe.sha(rendered)})
        shutil.copyfile(rendered,target);print(name,f//3,'/12',flush=True)
    finish(name)


def finish(name):
    root=OUT/name;rows=[]
    for f in range(FRAMES):
        a=f//3*3;b=a+3;t=(f-a)/3;target=root/f'cadence/frames/{f:04d}.png'
        if target.exists():raise FileExistsError(target)
        if f==a:shutil.copyfile(root/f'anchors/{a:04d}.png',target)
        else:
            l=seq.warp(np.asarray(Image.open(root/f'anchors/{a:04d}.png').convert('RGB')),a,f)
            r=seq.warp(np.asarray(Image.open(root/f'anchors/{b:04d}.png').convert('RGB')),b,f)
            Image.fromarray(np.rint(l*(1-t)+r*t).astype('uint8')).save(target)
        rows.append({'frame':f,'sha256':recipe.sha(target),'left':a,'right':b,'blend':t})
    seq.save(root/'cadence/manifest.json',{'fps':FPS,'frames':rows})
    recipe.editing.encode(root/'cadence/frames',root/'cadence/preview.mp4',fps=FPS)


def reference_probe():
    source=previous.OUT/'d045/warped-inputs/0003.png'
    run=seq.shared.accepted_run('noise-steps-v001-us-reference-probe',graph('clean18',3),1,source,{'study':'noise-steps-v001','purpose':'validate reused baseline'})
    expected=OUT/'clean18/anchors/0003.png';actual=run/'frames/0000.png'
    identical=np.array_equal(np.asarray(Image.open(expected)),np.asarray(Image.open(actual)))
    seq.save(OUT/'reference-probe.json',{'run':str(run.relative_to(seq.PROJECT)),'pixel_identical':identical,'sha256':recipe.sha(actual)})
    assert identical,'Serving runtime differs; review baseline before comparison'
    print('Reference probe pixel-identical',flush=True)


def check():
    a=graph('noise18',3);b=graph('noise36',3)
    a['6']['inputs']['steps']=36;a['11']=b['11'];assert a==b
    assert not any(n['class_type'] in ('SetLatentNoiseMask','ImageCompositeMasked') for n in a.values())
    _,w=previous.regions();assert w[0,-1]==1 and w[-1,0]==0
    print('Matched step graphs; no sampling mask/copyback; top-right noise map checked')


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('stage',choices=('prepare','render','probe','check'));p.add_argument('--variant',choices=VARIANTS);a=p.parse_args()
    if a.stage=='probe':reference_probe()
    elif a.stage=='render':
        if a.variant:render(a.variant)
        else:
            with ThreadPoolExecutor(max_workers=2) as pool:list(pool.map(render,('noise18','noise36','clean36')))
    else:globals()[a.stage]()
