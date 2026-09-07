"""Three preserved preset-component studies using existing ComfyUI nodes."""
import argparse
import json
import math
import shutil
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

import move_warp as wave
import seed_comparison as recipe

APP, PROJECT = recipe.APP, recipe.PROJECT
OUT = PROJECT / 'exports/motion-effects-v001'
ASSETS = APP / 'projects/reference-studies/references/assets/artist-channel-2026-09-07'
OPENING = recipe.OUT / 'opening.png'
FRAMES, FPS = 48, 8
EFFECTS = {
    'turn-bank': {'preset': 'Move-Around-30s', 'guide': None},
    'radial-unfold': {'preset': 'Move-Around-30s', 'guide': 'Kaleidoscope-30s.mp4',
                      'method': None, 'factor': 0.8},
    'ring-expand': {'preset': 'Evolve-Zoom-Slow-30s', 'guide': 'Circle-Zoom-30s.mp4',
                    'method': cv2.DISOPTICAL_FLOW_PRESET_MEDIUM, 'factor': 0.8},
}
# WebUI's DIS Fine starts from the default preset and overrides four parameters.


def schedule(values):
    return ', '.join(f'{f}:({value:.9f})' for f, value in enumerate(values))


def camera():
    vals = {k: [0.0] for k in ('translation_x', 'translation_y', 'translation_z',
                              'rotation_3d_x', 'rotation_3d_y', 'rotation_3d_z')}
    for f in range(1, FRAMES):
        t = 1.5 * f
        c, s = math.cos(3.141*t/60), math.sin(3.141*t/60)
        for key, value in zip(vals, (0, .0015*c, -.0375*s, .39*c, 1.2*c, 1.05*c)):
            vals[key].append(value)
    return recipe.node('DifforumCamera', params=['70', 0], mode='3d', fov=60.0,
                       zoom='0:(1)', **{k: schedule(v) for k, v in vals.items()})


def graph(effect, frame, preview=False):
    g = wave.graph(frame)
    g['11']['inputs']['filename_prefix'] = f'motion-effects/{effect}/frames'
    if effect != 'turn-bank':
        return g
    g['70'] = recipe.node('DifforumAnimSetup', width=recipe.WIDTH, height=recipe.HEIGHT,
        fps=FPS, max_frames=FRAMES, seed=recipe.SEED)
    g['71'] = camera()
    g['60'] = recipe.node('DownloadAndLoadDepthAnythingV2Model',
        model='depth_anything_v2_vits_fp32.safetensors', precision='fp32')
    g['61'] = recipe.node('DepthAnything_V2', da_model=['60', 0], images=['4', 0])
    g['62'] = recipe.node('SaveImage', images=['61', 0], filename_prefix='motion-effects/depth')
    depth = dict(depth=['61', 0], near=2.0, far=10.0, invert_depth=False, translation_scale=1.0)
    if preview:
        g['72'] = recipe.node('DifforumGuideBuilder', anchor_image=['4', 0], camera=['71', 0],
            params=['70', 0], warp_mode='force_3d', **depth)
        g['11']['inputs']['images'] = ['72', 0]
        for k in ('1', '21', '2', '3', '5', '6', '7'):
            del g[k]
    else:
        g['72'] = recipe.node('DifforumWarp', image=['4', 0], camera=['71', 0],
            frame=frame, warp_mode='force_3d', **depth)
        g['5']['inputs']['pixels'] = ['72', 0]
        g['73'] = recipe.node('SaveImage', images=['72', 0], filename_prefix='motion-effects/warped')
    g['74'] = recipe.node('MaskToImage', mask=['72', 1])
    g['75'] = recipe.node('SaveImage', images=['74', 0], filename_prefix='motion-effects/coverage')
    return g


def accepted_run(experiment, g, frames, source, lineage):
    matches = list((PROJECT/'runs').glob(f'*-{experiment}-{frames}f'))
    if len(matches) > 1:
        raise RuntimeError('Multiple attempts require explicit selection')
    if matches:
        folder = matches[0]
        receipt = json.loads((folder/'submission.json').read_text())
        assert receipt['source_sha256'] == recipe.sha(source)
        assert json.loads((folder/'workflow.api.json').read_text()) == g
        recipe.serverless_client.collect(folder)
        return folder
    return recipe.serverless_client.submit(PROJECT, experiment, g, frames, source=source,
        lineage={'study':'motion-effects-v001', 'source_sha256':recipe.sha(source), **lineage})


def prepare(effect):
    root = OUT/effect
    root.mkdir(parents=True, exist_ok=False)
    for name in ('flows','guide-frames','warp-only/frames','repaint/frames','warped-inputs'):
        (root/name).mkdir(parents=True)
    spec = EFFECTS[effect]
    manifest = dict(effect=effect, spec=spec, frames=FRAMES, fps=FPS,
        opening_sha256=recipe.sha(OPENING), preset_sha256=recipe.sha(ASSETS/'presets'/f'{spec["preset"]}.txt'),
        graph=graph(effect,1), opencv=cv2.__version__)
    shutil.copyfile(OPENING, root/'repaint/frames/0000.png')
    if spec['guide']:
        guide = ASSETS/'hybrid-guides'/spec['guide']
        manifest.update(guide_sha256=recipe.sha(guide), guide_frames=list(range(FRAMES)),
                        guide_fps=12, flow_statistics=[])
        capture = cv2.VideoCapture(str(guide))
        assert abs(capture.get(cv2.CAP_PROP_FPS)-12) < 1e-6
        dis = cv2.DISOpticalFlow_create(spec['method'])
        if effect == 'radial-unfold':
            dis.setGradientDescentIterations(192)
            dis.setFinestScale(0)
            dis.setPatchSize(8)
            dis.setPatchStride(4)
        manifest['dis_finest_scale'] = dis.getFinestScale()
        previous, flow = None, None
        rgb = np.asarray(Image.open(OPENING).convert('RGB'))
        for f in range(FRAMES):
            ok, bgr = capture.read()
            if not ok:
                raise RuntimeError(f'Missing guide frame {f}')
            bgr = cv2.resize(bgr,(recipe.WIDTH,recipe.HEIGHT),interpolation=cv2.INTER_AREA)
            cv2.imwrite(str(root/f'guide-frames/{f:04d}.png'),bgr)
            gray = cv2.cvtColor(bgr,cv2.COLOR_BGR2GRAY)
            if f:
                flow = dis.calc(previous,gray,None if flow is None else flow.copy())
                scaled = flow*spec['factor']
                assert np.isfinite(scaled).all()
                np.save(root/f'flows/{f:04d}.npy',scaled)
                rgb = warp(rgb,scaled)
                manifest['flow_statistics'].append({'frame':f,'mean_dx':float(scaled[:,:,0].mean()),
                    'mean_dy':float(scaled[:,:,1].mean()),'p95_px':float(np.percentile(np.linalg.norm(scaled,axis=-1),95))})
            Image.fromarray(rgb).save(root/f'warp-only/frames/{f:04d}.png')
            previous = gray
        capture.release()
        recipe.editing.encode(root/'warp-only/frames',root/'warp-only/preview.mp4',fps=FPS)
    wave.save(root/'manifest.json',manifest)
    print('Prepared',effect,flush=True)


def warp(rgb, flow):
    h,w=rgb.shape[:2]
    x,y=np.meshgrid(np.arange(w,dtype=np.float32),np.arange(h,dtype=np.float32))
    return cv2.remap(rgb,np.stack((x,y),axis=-1)-flow,None,cv2.INTER_LINEAR,
                     borderMode=cv2.BORDER_REFLECT_101)


def preview_camera():
    root=OUT/'turn-bank'
    run=accepted_run('motion-effects-v001-turn-bank-guide',graph('turn-bank',0,True),FRAMES,
        OPENING,{'effect':'turn-bank','camera_only':True})
    for f in range(FRAMES):
        target=root/f'warp-only/frames/{f:04d}.png'
        if not target.exists():
            shutil.copyfile(run/f'frames/{f:04d}.png',target)
    if not (root/'warp-only/preview.mp4').exists():
        shutil.copyfile(run/'preview.mp4',root/'warp-only/preview.mp4')
    if not (root/'camera-guide-run.json').exists():
        wave.save(root/'camera-guide-run.json',{'run':str(run.relative_to(PROJECT))})


def render(effect,until):
    assert 1 <= until <= FRAMES
    root=OUT/effect
    assert json.loads((root/'manifest.json').read_text())['graph'] == graph(effect,1)
    for f in range(1,until):
        target=root/f'repaint/frames/{f:04d}.png'
        record=root/f'repaint/frame-{f:04d}-run.json'
        if target.exists():
            assert recipe.sha(target)==json.loads(record.read_text())['sha256']
            continue
        previous=root/f'repaint/frames/{f-1:04d}.png'
        source=previous
        if effect!='turn-bank':
            source=root/f'warped-inputs/{f:04d}.png'
            moved=warp(np.asarray(Image.open(previous).convert('RGB')),np.load(root/f'flows/{f:04d}.npy'))
            if source.exists():
                assert np.array_equal(np.asarray(Image.open(source)),moved)
            else:
                Image.fromarray(moved).save(source)
        run=accepted_run(f'motion-effects-v001-{effect}-frame-{f:04d}',graph(effect,f),1,source,
            {'effect':effect,'frame':f,'parent_frame':f-1,'seed':recipe.SEED+f})
        rendered=run/'frames/0000.png'
        if not record.exists():
            wave.save(record,{'run':str(run.relative_to(PROJECT)),'sha256':recipe.sha(rendered)})
        shutil.copyfile(rendered,target)
        print(f'{effect}: {f}/{FRAMES-1}',flush=True)
    video=root/f'repaint/preview-{until:02d}f.mp4'
    if not video.exists():
        recipe.editing.encode(root/'repaint/frames',video,fps=FPS)


if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('stage',choices=('prepare','camera-preview','render'))
    p.add_argument('--effect',choices=tuple(EFFECTS),default='turn-bank')
    p.add_argument('--until',type=int,default=FRAMES)
    a=p.parse_args()
    if a.stage=='prepare': prepare(a.effect)
    elif a.stage=='camera-preview': preview_camera()
    else: render(a.effect,a.until)
