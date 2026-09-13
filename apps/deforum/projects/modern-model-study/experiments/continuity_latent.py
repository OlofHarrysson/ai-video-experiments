"""Matched sigma0.10 clean-latent recurrence; main-agent execution only.

One graph, default 15 SamplerCustom calls (45 model evaluations), one source
VAEEncode. Each sampler consumes the previous sampler's output0, with independent
fresh noise at seeds 918273..918287. Decoded RGB is observation-only.

Commands: prepare prints the graph/plan JSON to stdout without writes or network;
render --deployment PATH submits/resumes ONE job; verify is local-only and requires
the RGB control's first repaint for exact parity. --cycles may be 4 or 15 (default).
The entire selected chain runs before parity is checked; 15 cycles is not an early
one-cycle gate. Main decides whether to run after reviewing its VAE-only control.

Every cycle has a unique SaveImage and SaveLatent node/prefix. Node11 additionally
saves an ordered image batch for the unchanged pod_client collector. Its automatic
8fps transport preview is not the four-paintings/sec review timeline. Use saved
paintings and the frame/seconds labels in the verification report for review.

Main must archive the original files listed in remote-artifacts.json, including
all .latent files, before cleanup. Optional verify --archive-root PATH expects a
local mirror of the ComfyUI OUTPUT directory (subfolders retained); it verifies
per-cycle PNG parity and latent container headers/hashes. No custom nodes needed.
SaveLatent source inspection supports 5D tensors; real runtime execution is pending:
https://github.com/Comfy-Org/ComfyUI/blob/12d5279438bfefc058a269eae805ceab6047777f/nodes.py#L454-L502
"""
import argparse
import copy
import json
from pathlib import Path
import shutil
import struct

import numpy as np
from PIL import Image
import continuity_controls as control

base = control.base
OUT = Path(__file__).resolve().parents[1] / 'exports/continuity-latent-v001'
CASE = 'euler-010'
WIDTH, HEIGHT = 1536, 1024


def read(path):
    return json.loads(path.read_text())


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def config():
    c = read(control.CONFIGS / f'{CASE}.json')
    require(c['seed'] == 918273 and c['cfg'] == 1. and c['sampler'] == 'euler',
            'RGB control recipe changed')
    require(c['sigmas'] == [v*.1/.6 for v in base.SIGMAS], 'RGB sigma0.10 schedule changed')
    require(c['motion'] == 'none' and c['cadence'] == 6 and c['fps'] == 24,
            'RGB control timing/motion changed')
    return c


def root(cycles):
    require(cycles in (4, 15), 'Choose 4 or 15 cycles')
    return OUT / f'cycles-{cycles:02d}'


def source(c):
    return base.APP / c['source']


def graph(cycles=15):
    c = config()
    prefix = f'continuity-latent-v001/cycles-{cycles:02d}'
    root(cycles)
    g = control.graph(c, 0)
    sampler = g.pop('9')
    del g['10'], g['11']
    n = base.node
    g['25'] = n('SaveLatent', samples=['24', 0], filename_prefix=prefix + '/initial-encoded-latent')
    previous, batch = ['24', 0], None
    for cycle in range(1, cycles+1):
        sample_id, decode_id = str(100+cycle), str(200+cycle)
        g[sample_id] = copy.deepcopy(sampler)
        g[sample_id]['inputs'].update(latent_image=previous, noise_seed=c['seed']+cycle-1)
        previous = [sample_id, 0]
        g[decode_id] = n('VAEDecode', samples=previous, vae=['3', 0])
        g[str(300+cycle)] = n('SaveImage', images=[decode_id, 0],
            filename_prefix=prefix + f'/painting-{cycle:02d}')
        g[str(400+cycle)] = n('SaveLatent', samples=previous,
            filename_prefix=prefix + f'/sampled-latent-{cycle:02d}')
        if batch is None:
            batch = [decode_id, 0]
        else:
            batch_id = str(500+cycle)
            g[batch_id] = n('ImageBatch', image1=batch, image2=[decode_id, 0])
            batch = [batch_id, 0]
    g['11'] = n('SaveImage', images=batch, filename_prefix=prefix + '/collection-batch')
    return g


def plan(cycles=15):
    c = config()
    return {'cycles': cycles, 'jobs': 1, 'model_evaluations': 3*cycles,
        'config': c, 'source_sha256': base.sha(source(c)), 'graph': graph(cycles),
        'seeds': list(range(c['seed'], c['seed']+cycles)),
        'initialization': 'one VAEEncode; subsequent SamplerCustom output0 directly into next sampler',
        'parity': 'first decoded painting must equal RGB cycle1; checked after the whole job',
        'inference_performed_by_prepare': False}


def pixels(path):
    with Image.open(path) as im:
        require(im.size == (WIDTH, HEIGHT), f'Unexpected dimensions: {path}')
        return np.asarray(im.convert('RGB'))


def copy_same(src, dest):
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists():
        require(base.sha(src) == base.sha(dest), f'Local output collision: {dest}')
    else:
        shutil.copy2(src, dest)


def find_run(cycles):
    name = f'continuity-latent-v001-cycles-{cycles:02d}'
    matches = list((OUT/'runs').glob(f'*-{name}-{cycles}f'))
    require(len(matches) == 1, f'Expected one existing run for {name}, found {len(matches)}')
    return matches[0]


def check_run(cycles, run):
    c = config()
    expected = graph(cycles)
    require(read(run/'workflow.api.json') == expected, 'Requested graph mismatch')
    require(base.sha(run/'anchor.png') == base.sha(source(c)), 'Source mismatch')
    upload = read(run/'upload.json')
    expected['20']['inputs']['image'] = '/'.join(filter(None, [upload.get('subfolder'), upload['name']]))
    require(read(run/'workflow.executed.json') == expected, 'Executed graph mismatch')
    h = read(run/'history.json')
    require(h['status']['completed'] and h['status']['status_str'] == 'success', 'Job not successful')
    require(h['prompt'][2] == expected, 'History graph mismatch')
    pid = read(run/'submit-response.json')['prompt_id']
    require(h['prompt'][1] == pid, 'History prompt ID mismatch')
    require(len(h['outputs']['11']['images']) == cycles, 'Collector batch count mismatch')
    require(len(list((run/'frames').glob('*.png'))) == cycles, 'Collected frame count mismatch')
    artifacts = []
    for cycle in range(1, cycles+1):
        for node_id, kind in ((str(300+cycle), 'images'), (str(400+cycle), 'latents')):
            files = h['outputs'][node_id][kind]
            require(len(files) == 1, f'Expected one artifact for cycle{cycle} node{node_id}')
            artifacts.append({'cycle': cycle, 'node': node_id, 'kind': kind, **files[0]})
    initial = h['outputs']['25']['latents']
    require(len(initial) == 1, 'Missing initial encoded latent')
    artifacts.append({'cycle': 0, 'node': '25', 'kind': 'latents', **initial[0]})
    return pid, artifacts


def render(cycles, deployment):
    p = plan(cycles)
    case_root = root(cycles)
    base.save(case_root/'plan.json', p)
    base.pod_client.DEPLOYMENT = deployment.resolve()
    name = f'continuity-latent-v001-cycles-{cycles:02d}'
    (OUT/'runs').mkdir(parents=True, exist_ok=True)
    matches = list((OUT/'runs').glob(f'*-{name}-{cycles}f'))
    if matches:
        require(len(matches) == 1, 'Multiple matching runs; refusing duplicate submission')
        run = matches[0]
        require(read(run/'workflow.api.json') == p['graph'], 'Resume graph changed')
        require(base.sha(run/'anchor.png') == p['source_sha256'], 'Resume source changed')
        base.pod_client.collect(run)
    else:
        run = base.pod_client.submit(OUT, name, p['graph'], cycles, source=source(p['config']),
            lineage={'study': 'continuity-latent-v001', 'cycles': cycles,
                     'source_sha256': p['source_sha256'], 'feedback': p['initialization']})
    pid, artifacts = check_run(cycles, run)
    copy_same(run/'anchor.png', case_root/'paintings/00-source.png')
    for cycle in range(1, cycles+1):
        copy_same(run/f'frames/{cycle-1:04d}.png', case_root/f'paintings/{cycle:02d}-latent.png')
    base.save(case_root/'run.json', {'run': str(run.relative_to(OUT)), 'prompt_id': pid,
                                    'source_sha256': p['source_sha256']})
    base.save(case_root/'remote-artifacts.json', artifacts)
    print(f'Collected one {cycles}-cycle job. First-painting parity and raw latent archiving remain to verify.')


def latent_header(path):
    # SaveLatent uses a safetensors container without imposing a 4D shape.
    # Inspect its header/length without introducing torch or loading arbitrary code.
    with path.open('rb') as f:
        size_bytes = f.read(8)
        require(len(size_bytes) == 8, f'Truncated latent: {path}')
        size = struct.unpack('<Q', size_bytes)[0]
        require(0 < size <= 1_000_000, f'Invalid latent header size: {path}')
        header = json.loads(f.read(size))
    tensor = header['latent_tensor']
    require(tensor['shape'] == [1, 16, 1, HEIGHT//8, WIDTH//8], f'Unexpected latent shape: {path}')
    widths = {'F16': 2, 'BF16': 2, 'F32': 4, 'F64': 8}
    require(tensor['dtype'] in widths, f'Unexpected latent dtype: {path}')
    start, end = tensor['data_offsets']
    require(0 <= start < end and end-start == int(np.prod(tensor['shape']))*widths[tensor['dtype']],
            f'Invalid latent data offsets: {path}')
    require(path.stat().st_size >= 8+size+end, f'Truncated latent tensor: {path}')
    return {'shape': tensor['shape'], 'dtype': tensor['dtype'], 'sha256': base.sha(path)}


def verify(cycles, rgb_root, archive_root=None):
    case_root = root(cycles)
    require(read(case_root/'plan.json') == plan(cycles), 'Prepared plan/source changed')
    run = find_run(cycles)
    pid, artifacts = check_run(cycles, run)
    c = config()
    # Verify the actual first RGB job, not merely a conveniently named image.
    frame = c['cadence']
    rgb = read(rgb_root/f'anchor-{frame:04d}.json')
    rgb_run = control.OUT/rgb['run']
    require(read(rgb_run/'workflow.api.json') == control.graph(c, 0), 'RGB first-job recipe mismatch')
    require(rgb['parent_sha256'] == base.sha(run/'anchor.png') == base.sha(rgb_run/'anchor.png'),
            'RGB/latent initial source mismatch')
    rgb_image = rgb_root/f'anchors/{frame:04d}.png'
    require(rgb['output_sha256'] == base.sha(rgb_image) == base.sha(rgb_run/'frames/0000.png'),
            'RGB first output hash mismatch')
    first = case_root/'paintings/01-latent.png'
    require(base.sha(first) == base.sha(run/'frames/0000.png'), 'Latent first output hash mismatch')
    a, b = pixels(first), pixels(rgb_image)
    delta = np.abs(a.astype(np.int16)-b.astype(np.int16))
    parity = {'pixel_identical': bool(np.array_equal(a, b)), 'max_abs_difference': int(delta.max()),
              'rgb_sha256': base.sha(rgb_image), 'latent_sha256': base.sha(first)}
    base.save(case_root/'first-painting-parity.json', parity)
    require(parity['pixel_identical'], 'First decoded painting differs from RGB: do not interpret later drift.')
    rows = []
    for cycle in range(1, cycles+1):
        local = case_root/f'paintings/{cycle:02d}-latent.png'
        require(base.sha(local) == base.sha(run/f'frames/{cycle-1:04d}.png'), f'Painting{cycle} hash mismatch')
        pixels(local)
        rows.append({'cycle': cycle, 'seed': c['seed']+cycle-1, 'frame': cycle*c['cadence'],
                     'seconds': cycle*c['cadence']/c['fps'], 'sha256': base.sha(local)})
    archived = []
    if archive_root is not None:
        for item in artifacts:
            require(item['type'] == 'output', 'Unexpected remote artifact type')
            path = archive_root/item.get('subfolder', '')/item['filename']
            if item['kind'] == 'latents':
                evidence = latent_header(path)
            else:
                local = case_root/f"paintings/{item['cycle']:02d}-latent.png"
                require(np.array_equal(pixels(path), pixels(local)), 'Individual SaveImage/batch pixel mismatch')
                evidence = {'sha256': base.sha(path)}
            archived.append({'node': item['node'], 'cycle': item['cycle'], **evidence})
    report = {'verified': True, 'prompt_id': pid, 'cycles': cycles, 'first_painting_parity': parity,
              'paintings': rows, 'raw_archive_verified': archive_root is not None, 'archived': archived,
              'scope': 'One encode, direct sampled output0 recurrence, matching fresh seeds/sigmas; no visual-quality conclusion.'}
    # Separate filenames allow graph/parity checking before the raw archive arrives.
    base.save(case_root/('archive-verification.json' if archive_root is not None else 'verification.json'), report)
    print(f'Verified {cycles} latent updates and exact first-RGB parity; raw archive verified={archive_root is not None}.')


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('stage', choices=['prepare', 'render', 'verify'])
    parser.add_argument('--cycles', type=int, choices=[4, 15], default=15)
    parser.add_argument('--deployment', type=Path)
    parser.add_argument('--rgb-root', type=Path, default=control.OUT/CASE,
                        help='local matched RGB euler-010 branch directory')
    parser.add_argument('--archive-root', type=Path, help='local mirror of ComfyUI output directory')
    args = parser.parse_args()
    if args.stage == 'prepare':
        print(json.dumps(plan(args.cycles), indent=2))
    elif args.stage == 'render':
        if args.deployment is None:
            parser.error('render requires the main-agent-owned --deployment path')
        render(args.cycles, args.deployment)
    else:
        verify(args.cycles, args.rgb_root, args.archive_root)


if __name__ == '__main__':
    main()
