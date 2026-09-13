"""Matched stationary Krea preservation probes with explicit starting sigmas."""
import argparse
import json
import shutil
from pathlib import Path

import ten_dollar as base

HERE = Path(__file__).resolve().parent
OUT = HERE.parent / 'exports/continuity-controls-v001'
CONFIGS = HERE / 'continuity-controls-configs'
FPS, CADENCE, DURATION, SEED = 24, 6, 4, 918273
SOURCE = 'projects/modern-model-study/exports/refresh-rate-v001/two-current/anchors/0144.png'
CASES = {'euler-060': ('euler', .6), 'euler-010': ('euler', .1),
         'euler-020': ('euler', .2), 'vae-only': (None, None),
         'heun-060': ('heun', .6)}


def prepare():
    prompt = json.loads((HERE/'cfg-audition-configs/cfg-10.json').read_text())['scenes'][0]['prompt']
    for case, (sampler, sigma) in CASES.items():
        sigmas = [v*sigma/.6 for v in base.SIGMAS] if sigma is not None else None
        if sigmas:
            assert all(a > b for a, b in zip(sigmas, sigmas[1:])) and sigmas[-1] == 0
        base.save(CONFIGS/f'{case}.json', {'case': case, 'sampler': sampler,
            'seed': SEED, 'source': SOURCE, 'duration': DURATION, 'cadence': CADENCE,
            'fps': FPS, 'cfg': 1., 'sigmas': sigmas, 'prompt': prompt, 'motion': 'none'})
    dest = OUT/'source/seed.png'; dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists():
        assert base.sha(dest) == base.sha(base.APP/SOURCE)
    else:
        shutil.copy2(base.APP/SOURCE, dest)


def graph(config, index):
    n = base.node
    if config['sampler'] is None:
        return {'3': n('VAELoader', vae_name='qwen_image_vae.safetensors'),
            '20': n('LoadImage', image='anchor.png'),
            '24': n('VAEEncode', pixels=['20', 0], vae=['3', 0]),
            '10': n('VAEDecode', samples=['24', 0], vae=['3', 0]),
            '11': n('SaveImage', images=['10', 0], filename_prefix='continuity-controls-v001/vae-only')}
    g = base.repaint_graph(config['prompt'], config['seed']+index, config['sigmas'])
    g['42']['inputs']['sampler_name'] = config['sampler']
    g['11']['inputs']['filename_prefix'] = 'continuity-controls-v001/'+config['case']
    return g


def render(case):
    config = json.loads((CONFIGS/f'{case}.json').read_text())
    root = OUT/case
    base.save(root/'config.json', config)
    (root/'anchors').mkdir(parents=True, exist_ok=True)
    opening = root/'anchors/0000.png'
    if opening.exists():
        assert base.sha(opening) == base.sha(OUT/'source/seed.png')
    else:
        shutil.copy2(OUT/'source/seed.png', opening)
    for frame in range(CADENCE, DURATION*FPS, CADENCE):
        index = frame//CADENCE-1
        parent = root/f'anchors/{frame-CADENCE:04d}.png'
        target = root/f'anchors/{frame:04d}.png'
        receipt = root/f'anchor-{frame:04d}.json'
        g = graph(config, index)
        if receipt.exists():
            row = json.loads(receipt.read_text()); run = OUT/row['run']
            assert base.sha(parent) == row['parent_sha256'] and base.sha(target) == row['output_sha256']
            assert json.loads((run/'workflow.api.json').read_text()) == g
            continue
        run = base.submit_once(f'preserve-{case}-{frame:04d}', g, parent,
            {'frame': frame, 'seconds': frame/FPS, 'parent_sha256': base.sha(parent),
             'initialization': 'previous painting, no motion', 'sampler': config['sampler']})
        shutil.copy2(run/'frames/0000.png', target)
        base.save(receipt, {'frame': frame, 'seconds': frame/FPS, 'seed': config['seed']+index,
            'sampler': config['sampler'], 'sigmas': config['sigmas'],
            'run': str(run.relative_to(OUT)), 'parent_sha256': base.sha(parent),
            'initialization_sha256': base.sha(parent), 'output_sha256': base.sha(target)})
        print(f'{case}: update {index+1}/15, {frame/FPS:.2f}s', flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('stage', choices=['prepare', 'render'])
    parser.add_argument('--case', choices=CASES)
    parser.add_argument('--deployment', type=Path)
    args = parser.parse_args(); base.OUT = OUT
    if args.deployment:
        base.pod_client.DEPLOYMENT = args.deployment.resolve()
    if args.stage == 'prepare':
        prepare()
    else:
        if not args.case:
            parser.error('render requires an explicitly selected --case')
        render(args.case)
