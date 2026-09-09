"""Core-node no-motion Krea feedback with one opening VAE encode."""
import argparse
import copy
import json
from pathlib import Path
import repaint_diagnosis as d

OUT = d.a.PROJECT / 'exports/latent-feedback-v001'
STRENGTHS = {'latent010': .10, 'latent030': .30}
ROUNDS = 24
d.a.transport.DEPLOYMENT = d.a.APP / 'work/latent-feedback-session/deployment.json'


def graph(case):
    g = d.graph('repaint010', d.opening.SEED + 1)
    sampler = g.pop('9')
    del g['10'], g['11']
    n = d.a.workflows.node
    previous = ['24', 0]
    snapshots = []
    for i in range(1, ROUNDS + 1):
        key, decode = str(100 + i), str(200 + i)
        g[key] = copy.deepcopy(sampler)
        g[key]['inputs'].update(latent_image=previous, seed=d.opening.SEED+i,
                                denoise=STRENGTHS[case])
        previous = [key, 0]
        g[decode] = n('VAEDecode', samples=previous, vae=['3', 0])
        snapshots.append([decode, 0])
    batch = snapshots[0]
    for i, snapshot in enumerate(snapshots[1:]):
        key = str(300 + i)
        g[key] = n('ImageBatch', image1=batch, image2=snapshot)
        batch = [key, 0]
    g['11'] = n('SaveImage', images=batch, filename_prefix='latent-feedback/'+case)
    return g


def run(case):
    g = graph(case)
    name = 'latent-feedback-v001-' + case
    runs = d.a.PROJECT / 'runs'
    runs.mkdir(parents=True, exist_ok=True)
    matches = list(runs.glob('*-'+name+f'-{ROUNDS}f'))
    if matches:
        assert len(matches) == 1
        folder = matches[0]
        assert json.loads((folder/'workflow.api.json').read_text()) == g
        assert d.a.sha(folder/'anchor.png') == d.a.sha(d.SOURCE)
        d.a.transport.collect(folder)
    else:
        folder = d.a.transport.submit(d.a.PROJECT, name, g, ROUNDS, source=d.SOURCE,
            lineage={'study': 'latent-feedback-v001', 'case': case,
                     'feedback': 'KSampler LATENT directly to next KSampler; one VAEEncode',
                     'motion': 'none', 'source_sha256': d.a.sha(d.SOURCE)})
    root = OUT / case
    d.a.copy(d.SOURCE, root/'anchors/0000.png')
    for i in range(1, ROUNDS+1):
        d.a.copy(folder/f'frames/{i-1:04d}.png', root/f'anchors/{i:04d}.png')
    d.a.save(root/'manifest.json', {'case': case, 'cycles': ROUNDS,
        'run': str(folder.relative_to(d.a.PROJECT)), 'graph': g,
        'source_sha256': d.a.sha(d.SOURCE), 'runner_sha256': d.a.sha(Path(__file__)),
        'model_manifest_sha256': d.a.sha(d.a.APP/'serverless/modern-models.json'),
        'outputs': {i: d.a.sha(root/f'anchors/{i:04d}.png') for i in range(ROUNDS+1)}})
    print('COMPLETE', case, flush=True)


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('case', choices=STRENGTHS)
    run(p.parse_args().case)
