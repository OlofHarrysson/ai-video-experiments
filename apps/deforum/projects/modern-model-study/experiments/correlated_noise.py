"""Stationary recurrent Krea: independent versus correlated noise, equal sigma."""
import argparse
import json
import shutil
from pathlib import Path

import numpy as np
from PIL import Image
import ten_dollar as base

HERE = Path(__file__).resolve().parent
OUT = HERE.parent / 'exports/correlated-noise-v001'
CONFIGS = HERE / 'correlated-noise-configs'
FPS, CADENCE, DURATION, SEED = 24, 6, 4, 918273
CASES = {'independent': 0., 'correlated': .85}
SOURCE = 'projects/modern-model-study/exports/refresh-rate-v001/two-current/anchors/0144.png'


def prepare():
    prompt = json.loads((HERE/'cfg-audition-configs/cfg-10.json').read_text())['scenes'][0]['prompt']
    for case, rho in CASES.items():
        base.save(CONFIGS/f'{case}.json', {'case': case, 'correlation': rho, 'seed': SEED,
            'source': SOURCE, 'duration': DURATION, 'cadence': CADENCE, 'fps': FPS,
            'cfg': 1., 'sigmas': base.SIGMAS, 'prompt': prompt, 'motion': 'none'})
    dest = OUT/'source/seed.png'; dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists():
        assert base.sha(dest) == base.sha(base.APP/SOURCE)
    else:
        shutil.copy2(base.APP/SOURCE, dest)


def graph(config, index, legacy=False):
    g = base.repaint_graph(config['prompt'], SEED+index, config['sigmas'])
    g['11']['inputs']['filename_prefix'] = 'correlated-noise-v001/'+config['case']
    if legacy:
        return g
    n = base.node
    g['44'] = n('DeforumRecordedNoise', seed=SEED, index=index,
                correlation=config['correlation'], tag='v001-'+config['case'])
    g['45'] = n('CFGGuider', model=['1',0], positive=['4',0], negative=['5',0], cfg=1.)
    g['9'] = n('SamplerCustomAdvanced', noise=['44',0], guider=['45',0],
               sampler=['42',0], sigmas=['43',0], latent_image=['24',0])
    # Diagnostic only: this decoded noisy latent never initializes another painting.
    if index in (0, 1, 7, 14):
        g['46'] = n('AddNoise', model=['1',0], noise=['44',0], sigmas=['43',0], latent_image=['24',0])
        g['47'] = n('VAEDecode', samples=['46',0], vae=['3',0])
        g['48'] = n('SaveImage', images=['47',0], filename_prefix='correlated-noise-v001/diagnostic-'+config['case'])
    return g


def parity():
    config = json.loads((CONFIGS/'independent.json').read_text())
    first = []
    for legacy in (True, False):
        run = base.submit_once('noise-parity-'+('legacy' if legacy else 'advanced'),
                               graph(config, 0, legacy), OUT/'source/seed.png')
        first.append(run)
    a,b = [np.asarray(Image.open(p/'frames/0000.png').convert('RGB')) for p in first]
    same = np.array_equal(a,b)
    base.save(OUT/'sampler-parity.json', {'pixel_identical':same,
        'max_abs_difference':int(np.abs(a.astype(int)-b.astype(int)).max()),
        'runs':[str(p.relative_to(OUT)) for p in first]})
    if not same:
        raise RuntimeError('Native and explicit-noise sampler outputs differ; investigate before rendering')


def render(case):
    config = json.loads((CONFIGS/f'{case}.json').read_text())
    assert json.loads((OUT/'sampler-parity.json').read_text())['pixel_identical']
    root = OUT/case
    base.save(root/'config.json', config)
    (root/'anchors').mkdir(parents=True,exist_ok=True)
    opening=root/'anchors/0000.png'
    if opening.exists(): assert base.sha(opening)==base.sha(OUT/'source/seed.png')
    else: shutil.copy2(OUT/'source/seed.png', opening)
    for f in range(CADENCE, DURATION*FPS, CADENCE):
        index=f//CADENCE-1
        parent=root/f'anchors/{f-CADENCE:04d}.png'; target=root/f'anchors/{f:04d}.png'
        receipt=root/f'anchor-{f:04d}.json'; g=graph(config,index)
        if receipt.exists():
            row=json.loads(receipt.read_text()); run=OUT/row['run']
            assert base.sha(parent)==row['parent_sha256'] and base.sha(target)==row['output_sha256']
            assert json.loads((run/'workflow.api.json').read_text())==g
            continue
        # Preserve exact PNG feedback, with no warp/resampling in this diagnostic.
        run=base.submit_once(f'noise-{case}-{f:04d}',g,parent,
            {'frame':f,'seconds':f/FPS,'noise_index':index,'correlation':config['correlation'],
             'parent_sha256':base.sha(parent),'initialization':'previous painting, no motion'})
        shutil.copy2(run/'frames/0000.png', target)
        base.save(receipt, {'frame':f,'seconds':f/FPS,'noise_index':index,'seed':SEED+index,
            'correlation':config['correlation'],'sigmas':config['sigmas'],
            'run':str(run.relative_to(OUT)),'parent_sha256':base.sha(parent),
            'initialization_sha256':base.sha(parent),'output_sha256':base.sha(target)})
        print(f'{case}: painting {index+1}/15, {f/FPS:.2f}s',flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('stage',choices=['prepare','parity','render'])
    p.add_argument('--case',choices=CASES);p.add_argument('--deployment',type=Path)
    args=p.parse_args();base.OUT=OUT
    if args.deployment:base.pod_client.DEPLOYMENT=args.deployment.resolve()
    if args.stage=='prepare':prepare()
    elif args.stage=='parity':parity()
    else:
        for case in ([args.case] if args.case else CASES):render(case)
