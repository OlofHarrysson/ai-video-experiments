"""Matched Lanczos resampling feedback probe at denoise 0.10."""
import argparse
import json
from pathlib import Path
import numpy as np
import cv2
from PIL import Image
import cathedral_feedback as c
from cathedral_feedback import FPS, FRAMES, CADENCE, WIDTH, HEIGHT, SEED
import audition as a
import opening_art as opening

OUT = a.PROJECT / 'exports/resampling-feedback-v001'
STRENGTHS = {'lanczos010': .10}
a.transport.DEPLOYMENT = a.APP / 'work/repaint-diagnosis-session/deployment.json'


def warp(rgb, start, end):
    assert rgb.shape == (HEIGHT, WIDTH, 3)
    if start == end:
        return rgb.copy()
    coords = a.motion.coordinates(start, end, width=WIDTH, height=HEIGHT)
    return cv2.remap(rgb, coords, None, cv2.INTER_LANCZOS4, borderMode=cv2.BORDER_REFLECT_101)


def graph(strength, seed):
    g = c.graph('krea', 'gentle', seed)
    g['9']['inputs']['denoise'] = STRENGTHS[strength]
    g['11']['inputs']['filename_prefix'] = 'resampling-feedback/' + strength
    return g


def run(strength):
    model = "krea"
    root = OUT / strength
    initial = opening.OUT / 'krea-cathedral/image.png'
    a.copy(initial, root / 'anchors/0000.png')
    a.save(root / 'manifest.json', {'model': model, 'strength': strength, 'fps': FPS,
        'frames': FRAMES, 'cadence': CADENCE, 'seed': SEED, 'width': WIDTH, 'height': HEIGHT,
        'opening_sha256': a.sha(initial), 'prompt': opening.PROMPTS['cathedral'],
        'graph': graph(strength, SEED + 1), 'runner_sha256': a.sha(Path(__file__)),
        'motion_sha256': a.sha(Path(a.motion.__file__)),
        'model_manifest_sha256': a.sha(a.APP / 'serverless/modern-models.json'),
        'resampling': 'INTER_LANCZOS4', 'initialization': 'warped previous generated anchor', 'intermediates': 'preceding anchor warped, no blend'})
    for f in range(CADENCE, FRAMES, CADENCE):
        prior = root / f'anchors/{f-CADENCE:04d}.png'
        source = root / f'warped-inputs/{f:04d}.png'
        a.image(source, warp(np.asarray(Image.open(prior).convert('RGB')), f-CADENCE, f))
        g = graph(strength, SEED + f//CADENCE)
        name = f'resampling-feedback-v001-{model}-{strength}-{f:04d}'
        matches = list((a.PROJECT / 'runs').glob('*-' + name + '-1f'))
        if matches:
            assert len(matches) == 1
            folder = matches[0]
            assert json.loads((folder/'workflow.api.json').read_text()) == g
            assert a.sha(folder/'anchor.png') == a.sha(source)
            a.transport.collect(folder)
        else:
            folder = a.transport.submit(a.PROJECT, name, g, 1, source=source,
                lineage={'source_sha256': a.sha(source), 'parent_sha256': a.sha(prior),
                         'study': 'resampling-feedback-v001', 'frame': f})
        a.copy(folder / 'frames/0000.png', root / f'anchors/{f:04d}.png')
        a.save(root / f'anchor-{f:04d}.json', {'run': str(folder.relative_to(a.PROJECT)),
            'parent_sha256': a.sha(prior), 'initialization_sha256': a.sha(source),
            'output_sha256': a.sha(root / f'anchors/{f:04d}.png')})
        print(model, strength, f//3, '/ 11', flush=True)
    for f in range(FRAMES):
        anchor = f//CADENCE*CADENCE
        rgb = np.asarray(Image.open(root / f'anchors/{anchor:04d}.png').convert('RGB'))
        a.image(root / f'frames/{f:04d}.png', warp(rgb, anchor, f))
    target = root / 'preview.mp4'
    if not target.exists():
        a.editing.encode(root / 'frames', target, fps=FPS)
    a.save(root / 'frame-hashes.json', {p.name: a.sha(p) for p in sorted((root/'frames').glob('*.png'))})
    print(target, flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('strength', choices=STRENGTHS)
    args = parser.parse_args()
    (a.PROJECT / 'runs').mkdir(parents=True, exist_ok=True)
    run(args.strength)
