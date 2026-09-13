"""Replay one recorded Krea painting, then perturb its noise along a fixed arc."""
import argparse
import json
import shutil
from pathlib import Path
import numpy as np
from PIL import Image
import ten_dollar as base

OUT = Path(__file__).resolve().parents[1]/'exports/state-replay-v001'
SOURCE = OUT.parent/'correlated-noise-v001'
SEED = 927182
PATHS = {'small': [i*.005 for i in range(13)], 'wider': [i*.02 for i in range(13)]}


def graph(amount):
    config = json.loads((SOURCE/'independent/config.json').read_text())
    g = base.repaint_graph(config['prompt'], SEED, base.SIGMAS)
    del g['20']; del g['24']
    g['44'] = base.node('DeforumReplaySource', amount=amount, direction_seed=SEED)
    g['45'] = base.node('CFGGuider', model=['1',0], positive=['4',0], negative=['5',0], cfg=1.)
    g['9'] = base.node('SamplerCustomAdvanced', noise=['44',1], guider=['45',0],
        sampler=['42',0], sigmas=['43',0], latent_image=['44',0])
    g['11']['inputs']['filename_prefix'] = f'state-replay-v001/a{round(amount*1000):04d}'
    return g


def render(amount):
    label=f'{round(amount*1000):04d}'
    g=graph(amount)
    run=base.submit_once('state-replay-'+label,g)
    target=OUT/'samples'/f'{label}.png'; target.parent.mkdir(exist_ok=True)
    if target.exists(): assert base.sha(target)==base.sha(run/'frames/0000.png')
    else: shutil.copy2(run/'frames/0000.png',target)
    base.save(OUT/'samples'/f'{label}.json', {'amount':amount,'run':str(run.relative_to(OUT)),
        'output_sha256':base.sha(target),'source_recording_sha256':base.sha(SOURCE/'diagnostics/independent/0000.npz'),
        'kind':'fixed recorded-state probe; not recurrent', 'direction_seed':SEED})
    return target


def main():
    p=argparse.ArgumentParser();p.add_argument('stage',choices=['parity','coarse','finish'])
    p.add_argument('--deployment',type=Path,required=True);a=p.parse_args()
    base.OUT=OUT;base.pod_client.DEPLOYMENT=a.deployment
    OUT.mkdir(parents=True,exist_ok=True)
    if a.stage=='parity':
        output=render(0.)
        old=np.asarray(Image.open(SOURCE/'independent/anchors/0006.png').convert('RGB'))
        new=np.asarray(Image.open(output).convert('RGB'))
        diff=np.abs(old.astype(int)-new.astype(int))
        report={'pixel_identical':bool(np.array_equal(old,new)),'max_abs_difference':int(diff.max()),
            'mean_abs_difference':float(diff.mean()),'historical_painting':'correlated-noise-v001/independent/anchors/0006.png'}
        base.save(OUT/'replay-check.json',report)
        print(report,flush=True)
        if not report['pixel_identical']:raise RuntimeError('Replay mismatch: investigate before perturbing')
    else:
        assert json.loads((OUT/'replay-check.json').read_text())['pixel_identical']
        values=[.02,.06,.12,.24] if a.stage=='coarse' else sorted(set(round(x,6) for v in PATHS.values() for x in v))
        for amount in values:render(amount)


if __name__=='__main__':main()
