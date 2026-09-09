"""Isolate repeated repainting, VAE round trips, and spatial resampling."""
import argparse
import json
from pathlib import Path
import numpy as np
from PIL import Image
import cathedral_feedback as c
import audition as a
import opening_art as opening

OUT = a.PROJECT / 'exports/repaint-diagnosis-v001'
ROUNDS = 24
CASES = {'repaint010': .10, 'repaint030': .30, 'vae-only': None}
SOURCE = opening.OUT / 'krea-cathedral/image.png'
a.transport.DEPLOYMENT = a.APP / 'work/repaint-diagnosis-session/deployment.json'


def graph(case, seed):
    if case == 'vae-only':
        n = a.workflows.node
        return {'3': n('VAELoader', vae_name='qwen_image_vae.safetensors'),
                '20': n('LoadImage', image='anchor.png'),
                '24': n('VAEEncode', pixels=['20', 0], vae=['3', 0]),
                '10': n('VAEDecode', samples=['24', 0], vae=['3', 0]),
                '11': n('SaveImage', images=['10', 0], filename_prefix='repaint-diagnosis/vae-only')}
    g = c.graph('krea', 'gentle', seed)
    g['9']['inputs']['denoise'] = CASES[case]
    g['11']['inputs']['filename_prefix'] = 'repaint-diagnosis/' + case
    return g


def run(case):
    root = OUT / case
    a.copy(SOURCE, root / 'anchors/0000.png')
    a.save(root / 'manifest.json', {'case': case, 'rounds': ROUNDS, 'denoise': CASES[case],
        'source_sha256': a.sha(SOURCE), 'seed_start': opening.SEED, 'graph': graph(case, opening.SEED + 1),
        'motion': 'none; previous output PNG loaded unchanged', 'width': c.WIDTH, 'height': c.HEIGHT,
        'runner_sha256': a.sha(Path(__file__)), 'model_manifest_sha256': a.sha(a.APP/'serverless/modern-models.json')})
    (a.PROJECT/'runs').mkdir(parents=True, exist_ok=True)
    for i in range(1, ROUNDS + 1):
        prior = root / f'anchors/{i-1:04d}.png'
        g = graph(case, opening.SEED + i)
        name = f'repaint-diagnosis-v001-{case}-{i:04d}'
        matches = list((a.PROJECT/'runs').glob('*-' + name + '-1f'))
        if matches:
            assert len(matches) == 1
            folder = matches[0]
            assert json.loads((folder/'workflow.api.json').read_text()) == g
            assert a.sha(folder/'anchor.png') == a.sha(prior)
            a.transport.collect(folder)
        else:
            folder = a.transport.submit(a.PROJECT, name, g, 1, source=prior,
                lineage={'study': 'repaint-diagnosis-v001', 'case': case, 'round': i, 'parent_sha256': a.sha(prior), 'motion': 'none'})
        output = root/f'anchors/{i:04d}.png'
        a.copy(folder/'frames/0000.png', output)
        a.save(root/f'round-{i:04d}.json', {'run': str(folder.relative_to(a.PROJECT)),
            'input_sha256': a.sha(prior), 'output_sha256': a.sha(output)})
        print(case, i, '/', ROUNDS, flush=True)
    for i in range(ROUNDS+1):
        a.copy(root/f'anchors/{i:04d}.png', root/f'frames/{i:04d}.png')
    if not (root/'preview.mp4').exists():
        a.editing.encode(root/'frames',root/'preview.mp4',fps=4)
    print('COMPLETE',case,flush=True)


def spatial_controls():
    original = np.asarray(Image.open(SOURCE).convert('RGB'))
    repeated = original.copy()
    for i in range(12):
        if i:
            repeated = c.warp(repeated, (i-1)*3, i*3)
        a.image(OUT/f'warp-repeated/anchors/{i:04d}.png', repeated)
        a.image(OUT/f'warp-once/anchors/{i:04d}.png', c.warp(original, 0, i*3))
    previous = SOURCE
    for i in range(ROUNDS+1):
        dest = OUT/f'png-only/anchors/{i:04d}.png'
        a.image(dest, np.asarray(Image.open(previous).convert('RGB')))
        assert np.array_equal(np.asarray(Image.open(dest).convert('RGB')), original)
        previous = dest
    a.save(OUT/'local-controls.json', {'png_cycles': ROUNDS, 'png_rgb_identical': True,
        'warp_cycles': 11, 'warp_source_frames': [i*3 for i in range(12)],
        'warp': 'same bilinear/remap/reflected border as prior clips',
        'note': 'Once-per-endpoint isolates compounded resampling, with possible numerical coordinate inversion differences; this is not a proposed feedback replacement.'})
    print('Local spatial and PNG controls complete')


if __name__ == '__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('case', choices=[*CASES,'local'])
    args=p.parse_args()
    spatial_controls() if args.case=='local' else run(args.case)
