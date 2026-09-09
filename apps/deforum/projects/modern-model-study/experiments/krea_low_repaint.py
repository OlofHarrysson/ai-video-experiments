"""Krea-only lower repaint sweep with the preserved cathedral feedback loop."""
import argparse
import json
from pathlib import Path
import numpy as np
from PIL import Image
import cathedral_feedback as c
from cathedral_feedback import warp, FPS, FRAMES, CADENCE, WIDTH, HEIGHT, SEED
import audition as a
import opening_art as opening

OUT = a.PROJECT / 'exports/krea-low-repaint-v001'
STRENGTHS = {'d010': .10, 'd018': .18, 'd024': .24}
a.transport.DEPLOYMENT = a.APP / 'work/krea-low-repaint-session/deployment.json'


def graph(strength, seed):
    g = c.graph('krea', 'gentle', seed)
    g['9']['inputs']['denoise'] = STRENGTHS[strength]
    g['11']['inputs']['filename_prefix'] = 'krea-low-repaint/' + strength
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
        'initialization': 'warped previous generated anchor', 'intermediates': 'preceding anchor warped, no blend'})
    for f in range(CADENCE, FRAMES, CADENCE):
        prior = root / f'anchors/{f-CADENCE:04d}.png'
        source = root / f'warped-inputs/{f:04d}.png'
        a.image(source, warp(np.asarray(Image.open(prior).convert('RGB')), f-CADENCE, f))
        g = graph(strength, SEED + f//CADENCE)
        name = f'krea-low-repaint-v001-{model}-{strength}-{f:04d}'
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
                         'study': 'krea-low-repaint-v001', 'frame': f})
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
