"""Actual guide flow on the Mac, existing ComfyUI img2img on RunPod."""
import argparse
import json
from pathlib import Path
import shutil
import subprocess
import sys

import cv2
import numpy as np
from PIL import Image

import seed_comparison as recipe

APP, PROJECT = recipe.APP, recipe.PROJECT
OUT = PROJECT / 'exports/move-warp-v001'
GUIDE = APP / 'projects/reference-studies/references/assets/artist-channel-2026-09-07/hybrid-guides/Wave-Warp-30s.mp4'
OPENING = recipe.OUT / 'opening.png'
FLOW_FACTOR = 0.55
FRAMES, FPS = recipe.FRAMES, recipe.FPS


def save(path, value):
    with path.open('x') as stream:
        json.dump(value, stream, indent=2)
        stream.write('\n')


def warp(rgb, flow):
    h, w = rgb.shape[:2]
    x, y = np.meshgrid(np.arange(w, dtype=np.float32), np.arange(h, dtype=np.float32))
    coords = np.stack((x, y), axis=-1) - flow * FLOW_FACTOR
    return cv2.remap(rgb, coords, None, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT_101)


def prepare():
    OUT.mkdir(parents=True, exist_ok=False)
    for name in ('flows', 'guide-frames', 'warp-only/frames', 'repaint/frames', 'warped-inputs'):
        (OUT / name).mkdir(parents=True)
    video = cv2.VideoCapture(str(GUIDE))
    assert abs(video.get(cv2.CAP_PROP_FPS) - 12) < 1e-6
    dis = cv2.DISOpticalFlow_create(cv2.DISOPTICAL_FLOW_PRESET_MEDIUM)
    rgb = np.asarray(Image.open(OPENING).convert('RGB'))
    assert rgb.shape == (recipe.HEIGHT, recipe.WIDTH, 3)
    previous_gray, previous_flow = None, None
    stats = []
    for f in range(FRAMES):
        ok, bgr = video.read()
        if not ok:
            raise RuntimeError(f'Missing guide frame {f}')
        bgr = cv2.resize(bgr, (recipe.WIDTH, recipe.HEIGHT), interpolation=cv2.INTER_AREA)
        cv2.imwrite(str(OUT / f'guide-frames/{f:04d}.png'), bgr)
        gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)
        if f:
            flow = dis.calc(previous_gray, gray, None if previous_flow is None else previous_flow.copy())
            assert np.isfinite(flow).all()
            np.save(OUT / f'flows/{f:04d}.npy', flow)
            magnitude = np.linalg.norm(flow * FLOW_FACTOR, axis=-1)
            stats.append({'frame': f, 'p50_px': float(np.median(magnitude)),
                          'p95_px': float(np.percentile(magnitude, 95)),
                          'max_px': float(magnitude.max())})
            rgb = warp(rgb, flow)
            previous_flow = flow
        Image.fromarray(rgb).save(OUT / f'warp-only/frames/{f:04d}.png')
        previous_gray = gray
    video.release()
    shutil.copyfile(OPENING, OUT / 'repaint/frames/0000.png')
    recipe.editing.encode(OUT / 'warp-only/frames', OUT / 'warp-only/preview.mp4', fps=FPS)
    save(OUT / 'manifest.json', {'guide': str(GUIDE.relative_to(APP)),
        'guide_sha256': recipe.sha(GUIDE), 'opening_sha256': recipe.sha(OPENING),
        'frames': FRAMES, 'fps': FPS, 'guide_fps': 12, 'guide_frame_indices': list(range(FRAMES)),
        'flow_factor': FLOW_FACTOR, 'opencv': cv2.__version__, 'flow_method': 'DIS Medium',
        'flow_warm_start': True, 'border': 'BORDER_REFLECT_101', 'interpolation': 'INTER_LINEAR',
        'camera': 'none', 'guide_composite': False, 'flow_statistics': stats})
    print('Prepared', FRAMES, 'frames; median per-step p95 displacement:',
          np.median([s['p95_px'] for s in stats]), flush=True)


def graph(frame):
    g = recipe.base()
    g['4'] = recipe.node('LoadImage', image='anchor.png')
    g['5'] = recipe.node('VAEEncode', pixels=['4', 0], vae=['1', 2])
    g['6'] = recipe.node('KSampler', model=['21', 0], positive=['2', 0], negative=['3', 0],
        latent_image=['5', 0], seed=recipe.SEED + frame, steps=recipe.STEPS, cfg=recipe.CFG,
        sampler_name='dpmpp_2m', scheduler='karras', denoise=recipe.DENOISE)
    g['7'] = recipe.node('VAEDecode', samples=['6', 0], vae=['1', 2])
    g['11'] = recipe.node('SaveImage', images=['7', 0], filename_prefix='move-warp/frame')
    return g


def render(until):
    if not 1 <= until <= FRAMES:
        raise ValueError('Invalid exclusive frame limit')
    manifest = json.loads((OUT / 'manifest.json').read_text())
    assert manifest['flow_factor'] == FLOW_FACTOR
    assert manifest['opening_sha256'] == recipe.sha(OPENING)
    for f in range(1, until):
        target = OUT / f'repaint/frames/{f:04d}.png'
        record = OUT / f'repaint/frame-{f:04d}-run.json'
        if target.exists():
            saved = json.loads(record.read_text())
            assert recipe.sha(target) == saved['sha256']
            continue
        source = OUT / f'warped-inputs/{f:04d}.png'
        rgb = np.asarray(Image.open(OUT / f'repaint/frames/{f-1:04d}.png').convert('RGB'))
        moved = warp(rgb, np.load(OUT / f'flows/{f:04d}.npy'))
        if source.exists():
            assert np.array_equal(np.asarray(Image.open(source).convert('RGB')), moved)
        else:
            Image.fromarray(moved).save(source)
        experiment = f'move-warp-v001-frame-{f:04d}'
        matches = list((PROJECT / 'runs').glob(f'*-{experiment}-1f'))
        if len(matches) > 1:
            raise RuntimeError('Multiple accepted attempts require explicit selection')
        if matches:
            folder = matches[0]
            receipt = json.loads((folder / 'submission.json').read_text())
            assert receipt['source_sha256'] == recipe.sha(source)
            assert json.loads((folder / 'workflow.api.json').read_text()) == graph(f)
            recipe.serverless_client.collect(folder)
        else:
            folder = recipe.serverless_client.submit(PROJECT, experiment, graph(f), 1, source=source,
                lineage={'study': 'move-warp-v001', 'frame': f, 'seed': recipe.SEED + f,
                         'parent_frame': f-1, 'source_sha256': recipe.sha(source),
                         'flow_sha256': recipe.sha(OUT / f'flows/{f:04d}.npy')})
        rendered = folder / 'frames/0000.png'
        with Image.open(rendered) as im:
            assert im.size == (recipe.WIDTH, recipe.HEIGHT)
        if not record.exists():
            save(record, {'run': str(folder.relative_to(PROJECT)), 'sha256': recipe.sha(rendered)})
        shutil.copyfile(rendered, target)
        print(f'Completed frame {f}/{FRAMES-1}', flush=True)
    preview = OUT / f'repaint/preview-{until:02d}f.mp4'
    if not preview.exists():
        recipe.editing.encode(OUT / 'repaint/frames', preview, fps=FPS)


def review():
    subprocess.run([sys.executable, str(APP / 'video_review.py'),
        str(OUT / 'repaint/preview-48f.mp4'), '--compare', str(OUT / 'warp-only/preview.mp4'),
        '--label', 'Wave plus repaint', '--compare-label', 'Wave only',
        '--output-root', str(OUT / 'reviews'), '--overview', '6', '--max-frames', '12',
        '--page-size', '12'], check=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('stage', choices=('prepare', 'render', 'review'))
    parser.add_argument('--until', type=int, default=FRAMES)
    args = parser.parse_args()
    if args.stage == 'prepare':
        prepare()
    elif args.stage == 'render':
        render(args.until)
    else:
        review()
