"""Matched initial-noise schedule comparison using core ComfyUI nodes."""
import argparse
import copy
import json
from pathlib import Path
import repaint_diagnosis as d

OUT = d.a.PROJECT / 'exports/turbo-schedule-v001'
CASES = {'turbo-tail': (8, 7), 'small-updates': (64, 56)}
ROUNDS = 24
d.a.transport.DEPLOYMENT = d.a.APP / 'work/turbo-schedule-session/deployment.json'


def repaint_graph(case, seed):
    g = d.graph('repaint010', seed)
    old = g.pop('9')['inputs']
    n = d.a.workflows.node
    steps, split = CASES[case]
    g['40'] = n('BasicScheduler', model=old['model'], scheduler='simple', steps=steps, denoise=1.0)
    g['41'] = n('SplitSigmas', sigmas=['40', 0], step=split)
    g['42'] = n('KSamplerSelect', sampler_name='euler')
    g['9'] = n('SamplerCustom', model=old['model'], add_noise=True, noise_seed=seed,
               cfg=1.0, positive=old['positive'], negative=old['negative'],
               sampler=['42',0], sigmas=['41',1], latent_image=['24',0])
    g['11']['inputs']['filename_prefix'] = 'turbo-schedule/' + case
    return g


def graph(case):
    g = repaint_graph(case, d.opening.SEED+1)
    sampler = g.pop('9')
    del g['10'], g['11']
    n = d.a.workflows.node
    previous = ['24', 0]
    snapshots = []
    for i in range(1, ROUNDS+1):
        key, dec = str(100+i), str(200+i)
        g[key] = copy.deepcopy(sampler)
        g[key]['inputs'].update(latent_image=previous, noise_seed=d.opening.SEED+i)
        previous = [key,0]
        g[dec] = n('VAEDecode', samples=previous, vae=['3',0])
        snapshots.append([dec,0])
    batch = snapshots[0]
    for i, snapshot in enumerate(snapshots[1:]):
        key = str(300+i)
        g[key] = n('ImageBatch', image1=batch, image2=snapshot)
        batch = [key,0]
    g['11'] = n('SaveImage', images=batch, filename_prefix='turbo-schedule/'+case)
    return g


def run(case):
    g = graph(case)
    name = 'turbo-schedule-v001-' + case
    runs = d.a.PROJECT/'runs'; runs.mkdir(parents=True, exist_ok=True)
    matches = list(runs.glob('*-'+name+f'-{ROUNDS}f'))
    if matches:
        assert len(matches)==1
        folder=matches[0]
        assert json.loads((folder/'workflow.api.json').read_text())==g
        assert d.a.sha(folder/'anchor.png')==d.a.sha(d.SOURCE)
        d.a.transport.collect(folder)
    else:
        folder=d.a.transport.submit(d.a.PROJECT,name,g,ROUNDS,source=d.SOURCE,
            lineage={'study':'turbo-schedule-v001','case':case,'motion':'none',
                     'feedback':'direct sampler latent; one opening encode',
                     'source_sha256':d.a.sha(d.SOURCE)})
    root=OUT/case
    d.a.copy(d.SOURCE,root/'anchors/0000.png')
    for i in range(1,ROUNDS+1):d.a.copy(folder/f'frames/{i-1:04d}.png',root/f'anchors/{i:04d}.png')
    d.a.save(root/'manifest.json',{'case':case,'cycles':ROUNDS,'graph':g,
        'run':str(folder.relative_to(d.a.PROJECT)),'source_sha256':d.a.sha(d.SOURCE),
        'runner_sha256':d.a.sha(Path(__file__)),
        'model_manifest_sha256':d.a.sha(d.a.APP/'serverless/modern-models.json'),
        'outputs':{i:d.a.sha(root/f'anchors/{i:04d}.png') for i in range(ROUNDS+1)}})
    print('COMPLETE',case,flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('case',choices=CASES)
    run(p.parse_args().case)
