"""Same-model cathedral feedback, two repaint strengths, cadence 3, no blending."""
import argparse
import json
from pathlib import Path
import cv2
import numpy as np
from PIL import Image
import audition as a
import opening_art as opening

OUT = a.PROJECT / 'exports/cathedral-feedback-v001'
FPS, FRAMES, CADENCE = 12, 36, 3
WIDTH, HEIGHT = 1536, 1024
SEED = opening.SEED
a.transport.DEPLOYMENT = a.APP / 'work/cathedral-feedback-session/deployment.json'


def warp(rgb, start, end):
    assert rgb.shape == (HEIGHT, WIDTH, 3), rgb.shape
    if start == end:
        return rgb.copy()
    coords = a.motion.coordinates(start, end, width=WIDTH, height=HEIGHT)
    return cv2.remap(rgb, coords, None, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT_101)


def graph(model, strength, seed):
    g = opening.build(model + '-cathedral')
    n = a.workflows.node
    del g['6']
    g['20'] = n('LoadImage', image='anchor.png')
    g['24'] = n('VAEEncode', pixels=['20', 0], vae=['3', 0])
    g['9']['inputs']['latent_image'] = ['24', 0]
    if model == 'krea':
        g['9']['inputs'].update(seed=seed, denoise=.30 if strength == 'gentle' else .45)
    else:
        steps = 40 if strength == 'gentle' else 24
        g['13']['inputs']['steps'] = steps
        g['25'] = n('SplitSigmas', sigmas=['13', 0], step=steps - 4)
        g['9']['inputs']['sigmas'] = ['25', 1]
        g['8']['inputs']['noise_seed'] = seed
    assert not any(n['class_type'].startswith('Empty') or n['class_type'] == 'ReferenceLatent' for n in g.values())
    g['11']['inputs']['filename_prefix'] = 'cathedral-feedback/' + model + '-' + strength
    return g


def prepare():
    for model in ('klein', 'krea'):
        source = opening.OUT / (model + '-cathedral') / 'image.png'
        root = OUT / model
        a.copy(source, root / 'opening.png')
        rgb = np.asarray(Image.open(source).convert('RGB'))
        for f in range(FRAMES):
            a.image(root / f'motion-only/frames/{f:04d}.png', warp(rgb, 0, f))
        target = root / 'motion-only/preview.mp4'
        if not target.exists():
            a.editing.encode(target.parent / 'frames', target, fps=FPS)
    # Genuine invariants: keep full image size and test the exact identity mapping.
    assert np.array_equal(warp(rgb, 0, 0), rgb)
    for model in ('klein', 'krea'):
        for strength in ('gentle', 'stronger'):
            g = graph(model, strength, SEED + 1)
            assert g['9']['inputs']['latent_image'] == ['24', 0]
    print('Prepared motion previews and verified initialized graphs', flush=True)


def run(model, strength):
    root = OUT / model / strength
    initial = OUT / model / 'opening.png'
    a.copy(initial, root / 'anchors/0000.png')
    a.save(root / 'manifest.json', {'model': model, 'strength': strength, 'fps': FPS,
        'frames': FRAMES, 'cadence': CADENCE, 'seed': SEED, 'width': WIDTH, 'height': HEIGHT,
        'opening_sha256': a.sha(initial), 'prompt': opening.PROMPTS['cathedral'],
        'graph': graph(model, strength, SEED + 1), 'runner_sha256': a.sha(Path(__file__)),
        'motion_sha256': a.sha(Path(a.motion.__file__)),
        'model_manifest_sha256': a.sha(a.APP / 'serverless/modern-models.json'),
        'initialization': 'warped previous generated anchor', 'intermediates': 'preceding anchor warped, no blend'})
    for f in range(CADENCE, FRAMES, CADENCE):
        prior = root / f'anchors/{f-CADENCE:04d}.png'
        source = root / f'warped-inputs/{f:04d}.png'
        a.image(source, warp(np.asarray(Image.open(prior).convert('RGB')), f-CADENCE, f))
        g = graph(model, strength, SEED + f//CADENCE)
        name = f'cathedral-feedback-v001-{model}-{strength}-{f:04d}'
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
                         'study': 'cathedral-feedback-v001', 'frame': f})
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
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('model', choices=('prepare', 'klein', 'krea'))
    p.add_argument('strength', choices=('gentle', 'stronger'), nargs='?')
    args = p.parse_args()
    if args.model == 'prepare':
        prepare()
    else:
        if args.strength is None:
            p.error('strength is required')
        run(args.model, args.strength)
