"""Exaggerated ring, turbulent guide, and a rolling version of the liked unfolding."""
import argparse
import json
import shutil

import cv2
import numpy as np
from PIL import Image

import motion_effects as first
import seed_comparison as recipe

PROJECT, APP = first.PROJECT, first.APP
OUT = PROJECT/'exports/motion-effects-v002'
OPENING, FRAMES, FPS = first.OPENING, first.FRAMES, first.FPS
SPECS = {
    'strong-ring': {'source_effect':'ring-expand','multiplier':4.0,'roll':0.0},
    'turbulent': {'guide':'Turbulent-noise-30s.mp4','factor':2.0,'roll':0.0},
    'rolling-unfold': {'source_effect':'radial-unfold','multiplier':1.0,'roll':0.9},
}


def move(rgb, flow, roll):
    if roll:
        h,w=rgb.shape[:2]
        transform=cv2.getRotationMatrix2D(((w-1)/2,(h-1)/2),roll,1.0)
        rgb=cv2.warpAffine(rgb,transform,(w,h),flags=cv2.INTER_LINEAR,borderMode=cv2.BORDER_REFLECT_101)
    return first.warp(rgb,flow)


def graph(effect,frame):
    g=first.graph('ring-expand',frame)
    g['11']['inputs']['filename_prefix']=f'motion-effects-2/{effect}/frames'
    return g


def prepare(effect):
    root=OUT/effect;root.mkdir(parents=True,exist_ok=False)
    for name in ('flows','guide-frames','warp-only/frames','repaint/frames','warped-inputs'):
        (root/name).mkdir(parents=True)
    spec=SPECS[effect]
    manifest={'effect':effect,'spec':spec,'frames':FRAMES,'fps':FPS,'opening_sha256':recipe.sha(OPENING),
              'graph':graph(effect,1),'opencv':cv2.__version__,'flow_statistics':[],'flow_sha256':{}}
    if 'guide' in spec:
        guide=first.ASSETS/'hybrid-guides'/spec['guide']
        manifest.update(guide_sha256=recipe.sha(guide),guide_fps=12,guide_frames=list(range(FRAMES)),
                        preset_sha256=recipe.sha(first.ASSETS/'presets/Evolve-Slow-30s.txt'))
        cap=cv2.VideoCapture(str(guide));assert cap.get(cv2.CAP_PROP_FPS)==12
        dis=cv2.DISOpticalFlow_create(cv2.DISOPTICAL_FLOW_PRESET_MEDIUM)
    else:
        parent=first.OUT/spec['source_effect']
        manifest['parent_manifest_sha256']=recipe.sha(parent/'manifest.json')
    rgb=np.asarray(Image.open(OPENING).convert('RGB'));previous=None;flow=None
    for f in range(FRAMES):
        if 'guide' in spec:
            ok,bgr=cap.read();assert ok
            bgr=cv2.resize(bgr,(recipe.WIDTH,recipe.HEIGHT),interpolation=cv2.INTER_AREA)
            cv2.imwrite(str(root/f'guide-frames/{f:04d}.png'),bgr)
            gray=cv2.cvtColor(bgr,cv2.COLOR_BGR2GRAY)
            if f:
                flow=dis.calc(previous,gray,None if flow is None else flow.copy())
                applied=flow*spec['factor']
            previous=gray
        elif f:
            applied=np.load(parent/f'flows/{f:04d}.npy')*spec['multiplier']
        if f:
            assert np.isfinite(applied).all()
            path=root/f'flows/{f:04d}.npy';np.save(path,applied)
            manifest['flow_sha256'][str(f)]=recipe.sha(path)
            magnitude=np.linalg.norm(applied,axis=-1)
            manifest['flow_statistics'].append({'frame':f,'p95_px':float(np.percentile(magnitude,95)),
                'mean_dx':float(applied[:,:,0].mean()),'mean_dy':float(applied[:,:,1].mean())})
            rgb=move(rgb,applied,spec['roll'])
        Image.fromarray(rgb).save(root/f'warp-only/frames/{f:04d}.png')
    if 'guide' in spec:cap.release()
    shutil.copyfile(OPENING,root/'repaint/frames/0000.png')
    first.wave.save(root/'manifest.json',manifest)
    recipe.editing.encode(root/'warp-only/frames',root/'warp-only/preview.mp4',fps=FPS)
    print('Prepared',effect,flush=True)


def render(effect,until):
    assert 1<=until<=FRAMES
    root=OUT/effect;manifest=json.loads((root/'manifest.json').read_text())
    assert manifest['graph']==graph(effect,1)
    for f in range(1,until):
        target=root/f'repaint/frames/{f:04d}.png';record=root/f'repaint/frame-{f:04d}-run.json'
        if target.exists():
            assert recipe.sha(target)==json.loads(record.read_text())['sha256'];continue
        previous=root/f'repaint/frames/{f-1:04d}.png';source=root/f'warped-inputs/{f:04d}.png'
        flow_path=root/f'flows/{f:04d}.npy'
        assert recipe.sha(flow_path)==manifest['flow_sha256'][str(f)]
        rgb=move(np.asarray(Image.open(previous).convert('RGB')),np.load(flow_path),SPECS[effect]['roll'])
        if source.exists():assert np.array_equal(np.asarray(Image.open(source)),rgb)
        else:Image.fromarray(rgb).save(source)
        run=first.accepted_run(f'motion-effects-v002-{effect}-frame-{f:04d}',graph(effect,f),1,source,
            {'study':'motion-effects-v002','effect':effect,'frame':f,'parent_frame':f-1,
             'seed':recipe.SEED+f,'flow_sha256':recipe.sha(flow_path)})
        rendered=run/'frames/0000.png'
        if not record.exists():first.wave.save(record,{'run':str(run.relative_to(PROJECT)),'sha256':recipe.sha(rendered)})
        shutil.copyfile(rendered,target)
        print(f'{effect}: {f}/{FRAMES-1}',flush=True)
    video=root/f'repaint/preview-{until:02d}f.mp4'
    if not video.exists():recipe.editing.encode(root/'repaint/frames',video,fps=FPS)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('stage',choices=('prepare','render'))
    p.add_argument('--effect',required=True,choices=tuple(SPECS));p.add_argument('--until',type=int,default=FRAMES)
    a=p.parse_args()
    if a.stage=='prepare':prepare(a.effect)
    else:render(a.effect,a.until)
