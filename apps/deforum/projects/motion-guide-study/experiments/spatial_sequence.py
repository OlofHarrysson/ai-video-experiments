"""Direct twist, plane turn and ripple with endpoint cadence; no guide flow/depth.

Run from apps/deforum with uv run --with pillow --with opencv-python-headless.
"""
import argparse
import json
from pathlib import Path
import shutil

import cv2
import numpy as np
from PIL import Image

import motion_effects as shared
import seed_comparison as recipe

APP, PROJECT = recipe.APP, recipe.PROJECT
OUT = PROJECT / 'exports/spatial-sequence-v001'
OPENING = recipe.OUT / 'opening.png'
FPS, CADENCE, DURATION = 12, 3, 9
FRAMES = FPS * DURATION
ANCHORS = list(range(0, FRAMES + 1, CADENCE))


def smooth(value):
    p = np.clip(value, 0, 1)
    return p*p*(3-2*p)


def parameters(frame):
    seconds = frame / FPS
    return smooth(seconds/3), .8*smooth((seconds-3)/3), smooth((seconds-6)/3)


def twist(x, y, amount):
    dx, dy = x-256, y-160
    a = amount*np.exp(-(dx*dx+dy*dy)/(2*125**2))
    return 256+np.cos(a)*dx-np.sin(a)*dy, 160+np.sin(a)*dx+np.cos(a)*dy


def turn(x, y, angle, inverse=False):
    dx, dy = x-256, y-160
    if inverse:
        px = dx/(np.cos(angle)-dx*np.sin(angle)/600)
        return 256+px, 160+dy*(1+px*np.sin(angle)/600)
    den = 1+dx*np.sin(angle)/600
    return 256+dx*np.cos(angle)/den, 160+dy/den


def radial_offset(radius, phase):
    front = 24+185*phase
    return 24*np.sin(np.pi*phase)*np.exp(-((radius-front)**2)/(2*28**2))*radius/(radius+18)


def ripple(x, y, phase, inverse=False):
    dx, dy = x-256, y-160
    r = np.hypot(dx, dy)
    if inverse:
        # The chosen radial mapping is monotone; bracket its exact inverse.
        low, high = np.maximum(0, r-24), r+24
        for _ in range(24):
            mid = (low+high)/2
            less = mid+radial_offset(mid, phase) < r
            low, high = np.where(less, mid, low), np.where(less, high, mid)
        mapped = (low+high)/2
    else:
        mapped = r+radial_offset(r, phase)
    scale = np.divide(mapped, r, out=np.ones_like(r), where=r>1e-8)
    return 256+dx*scale, 160+dy*scale


def mapping(x, y, frame, inverse=False):
    a, b, c = parameters(frame)
    if inverse:
        x, y = ripple(x, y, c, True)
        x, y = turn(x, y, b, True)
        return twist(x, y, -a)
    x, y = twist(x, y, a)
    x, y = turn(x, y, b)
    return ripple(x, y, c)


def coordinates(source_frame, target_frame, width=recipe.WIDTH, height=recipe.HEIGHT):
    x, y = np.meshgrid(np.arange(width, dtype=np.float64)*512/width,
                       np.arange(height, dtype=np.float64)*320/height)
    x, y = mapping(x, y, target_frame, inverse=True)
    x, y = mapping(x, y, source_frame)
    return np.stack((x*width/512, y*height/320), axis=-1).astype(np.float32)


def warp(rgb, source_frame, target_frame):
    if source_frame == target_frame:
        return rgb.copy()
    return cv2.remap(rgb, coordinates(source_frame, target_frame), None,
                     cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT_101)


def graph(frame):
    g = shared.wave.graph(frame)
    g['11']['inputs']['filename_prefix'] = 'spatial-sequence/frame'
    # One increment per repaint, independent of delivery frame rate.
    g['6']['inputs']['seed'] = recipe.SEED + frame//CADENCE
    return g


def save(path, data):
    shared.wave.save(path, data)


def prepare():
    OUT.mkdir(parents=True, exist_ok=False)
    for name in ('anchors', 'warped-inputs', 'motion-only/frames', 'cadence/frames'):
        (OUT/name).mkdir(parents=True)
    shutil.copyfile(OPENING, OUT/'anchors/0000.png')
    rgb = np.asarray(Image.open(OPENING).convert('RGB'))
    save(OUT/'manifest.json', {'fps':FPS, 'cadence':CADENCE, 'duration_seconds':DURATION,
        'frames':FRAMES, 'anchor_indices':ANCHORS, 'opening_sha256':recipe.sha(OPENING),
        'script_sha256':recipe.sha(Path(__file__)),
        'graph':graph(3), 'schedule':[['twist',0,3],['flat-turn',3,6],['ripple',6,9]],
        'composition':'ripple after flat-turn after twist; completed twist and turn persist',
        'cadence_method':'two endpoints warped to each output time, then linear blend; classic-inspired, not an exact WebUI implementation',
        'border':'reflection', 'optical_flow':False, 'depth':False, 'opencv':cv2.__version__})
    for f in range(FRAMES):
        Image.fromarray(warp(rgb, 0, f)).save(OUT/f'motion-only/frames/{f:04d}.png')
    recipe.editing.encode(OUT/'motion-only/frames', OUT/'motion-only/preview.mp4', fps=FPS)
    print('Prepared motion-only sequence', flush=True)


def render(until):
    manifest=json.loads((OUT/'manifest.json').read_text())
    assert manifest['graph']==graph(3) and manifest['opening_sha256']==recipe.sha(OPENING)
    for f in ANCHORS[1:]:
        if f > until: break
        target, record = OUT/f'anchors/{f:04d}.png', OUT/f'anchor-{f:04d}.json'
        if target.exists():
            assert recipe.sha(target)==json.loads(record.read_text())['sha256']
            continue
        previous=OUT/f'anchors/{f-CADENCE:04d}.png'
        moved=warp(np.asarray(Image.open(previous).convert('RGB')), f-CADENCE, f)
        source=OUT/f'warped-inputs/{f:04d}.png'
        if source.exists():assert np.array_equal(np.asarray(Image.open(source)),moved)
        else:Image.fromarray(moved).save(source)
        run=shared.accepted_run(f'spatial-sequence-v001-anchor-{f:04d}',graph(f),1,source,
            {'study':'spatial-sequence-v001','timeline_frame':f,'timeline_fps':FPS,
             'cadence':CADENCE,'sequence_time_seconds':f/FPS,'sampling_seed':recipe.SEED+f//CADENCE})
        rendered=run/'frames/0000.png'
        if not record.exists():save(record,{'run':str(run.relative_to(PROJECT)),'sha256':recipe.sha(rendered)})
        shutil.copyfile(rendered,target)
        print(f'Anchor {f//CADENCE}/{len(ANCHORS)-1} at {f/FPS:.2f}s',flush=True)


def finish():
    rows=[]
    for f in range(FRAMES):
        a=f//CADENCE*CADENCE; b=a+CADENCE; alpha=(f-a)/CADENCE
        left=OUT/f'anchors/{a:04d}.png'; target=OUT/f'cadence/frames/{f:04d}.png'
        if target.exists():raise FileExistsError(target)
        if f==a:
            shutil.copyfile(left,target)
        else:
            right=OUT/f'anchors/{b:04d}.png'
            l=warp(np.asarray(Image.open(left).convert('RGB')),a,f)
            r=warp(np.asarray(Image.open(right).convert('RGB')),b,f)
            Image.fromarray(np.rint(l*(1-alpha)+r*alpha).astype(np.uint8)).save(target)
        rows.append({'frame':f,'seconds':f/FPS,'left_anchor':a,'right_anchor':b,
                     'blend':alpha,'sha256':recipe.sha(target)})
    save(OUT/'cadence/manifest.json',{'fps':FPS,'frames':rows,'terminal_anchor':FRAMES})
    recipe.editing.encode(OUT/'cadence/frames',OUT/'cadence/preview.mp4',fps=FPS)


def check():
    x,y=np.meshgrid(np.linspace(0,512,33),np.linspace(0,320,21))
    errors=[]
    for f in range(FRAMES+1):
        u,v=mapping(x,y,f);a,b=mapping(u,v,f,True)
        errors.append(float(np.max(np.hypot(a-x,b-y))))
        assert np.isfinite(coordinates(max(0,f-3),f,64,36)).all()
    assert max(errors)<.001, max(errors)
    for f in (0,36,72,108):
        before=mapping(x,y,max(0,f-1e-5));after=mapping(x,y,min(FRAMES,f+1e-5))
        assert np.max(np.hypot(after[0]-before[0],after[1]-before[1]))<.001
    assert len(ANCHORS)==37 and FRAMES/FPS==9
    print({'max_inverse_error_in_preview_pixels':max(errors),'anchors':len(ANCHORS),'duration':9})


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('stage',choices=('check','prepare','render','finish'))
    p.add_argument('--until',type=int,default=FRAMES);a=p.parse_args()
    if a.stage=='render':render(a.until)
    else:globals()[a.stage]()
