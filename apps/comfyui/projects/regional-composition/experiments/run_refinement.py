# /// script
# requires-python = ">=3.12"
# dependencies = ["pillow>=11"]
# ///
"""Compare a regional first pass with global latent-initialized refinement."""
import argparse
import hashlib
import json
import struct
from datetime import datetime, timezone
from pathlib import Path

from PIL import Image, ImageChops, ImageStat

from run_baseline import (CFG, MODEL_HASH, PROJECT, STEPS, STYLE, Graph, collect,
                          request, ui_workflow, validate, write_json)

GLOBAL_PROMPT = (
    "one small red tin robot standing on grass on the left, full body, "
    "one blue glass tree rooted in grass on the right, translucent branching canopy, "
    "distant mountains, open meadow, golden sky, " + STYLE
)
ORIGINALS = {
    0: "20260910T080602645918Z-regional-seed21001",
    100: "20260910T080710732830Z-regional-seed21101",
}


def pixel_compare(a, b):
    with Image.open(a) as ia, Image.open(b) as ib:
        ia, ib = ia.convert('RGB'), ib.convert('RGB')
        if ia.size != ib.size:
            raise ValueError('Cannot compare different image dimensions')
        diff = ImageChops.difference(ia, ib)
        return {'identical': diff.getbbox() is None,
                'mean_absolute_difference_8bit': sum(ImageStat.Stat(diff).mean)/3,
                'maximum_channel_difference_8bit': max(v[1] for v in diff.getextrema())}


def only_file(folder, pattern):
    files = list((folder/'outputs').glob(pattern))
    if len(files) != 1:
        raise ValueError(f'Expected one {pattern} in {folder}')
    return files[0]


def latent_tensor_hash(path):
    # Safetensors metadata contains a different graph for each output. Compare
    # the tensor payload itself, including its dtype and shape, not that metadata.
    data = path.read_bytes()
    header_size = struct.unpack('<Q', data[:8])[0]
    header = json.loads(data[8:8+header_size])
    tensor = header['latent_tensor']
    start, end = tensor['data_offsets']
    return {'dtype': tensor['dtype'], 'shape': tensor['shape'],
            'sha256': hashlib.sha256(data[8+header_size+start:8+header_size+end]).hexdigest()}


def build(prefix, seed_offset, size, denoise, mode):
    g = Graph(prefix, seed_offset, 0.25, 'mask')
    g.build('regional')
    first_sampler = next(k for k, n in g.nodes.items() if n['class_type'] == 'KSampler')
    latent = [first_sampler, 0]
    g.add('SaveLatent', samples=latent, filename_prefix=prefix+'/regional-latent')
    if mode == 'refine':
        positive = g.text(GLOBAL_PROMPT)
        if size != 1024:
            latent = g.add('LatentUpscale', samples=latent, upscale_method='bislerp',
                           width=size, height=size, crop='disabled')
            g.save(g.decode(latent), 'enlarged-without-refinement')
        refined = g.sample(latent, positive, 21004+seed_offset, denoise=denoise)
        g.save(g.decode(refined), 'global-refined')
        g.add('SaveLatent', samples=refined, filename_prefix=prefix+'/refined-latent')
    return g.nodes


def verify_lineage(folder, parent, reproduction=False):
    current = only_file(folder, 'regional_*.png')
    previous = only_file(parent, 'regional_*.png')
    check = pixel_compare(current, previous)
    check.update(comparison_kind='cross-session reproduction' if reproduction else 'within-session parent',
                 parent_run=str(parent.relative_to(PROJECT)),
                 parent_sha256=hashlib.sha256(previous.read_bytes()).hexdigest(),
                 current_sha256=hashlib.sha256(current.read_bytes()).hexdigest())
    if not reproduction:
        a = latent_tensor_hash(only_file(folder, 'regional-latent_*.latent'))
        b = latent_tensor_hash(only_file(parent, 'regional-latent_*.latent'))
        check.update(latent_tensor_identical=a==b, latent_tensor=a)
    write_json(folder/'lineage-check.json', check)
    if not reproduction and (not check['identical'] or not check['latent_tensor_identical']):
        raise RuntimeError(f'First-stage pixels differ; inspect {folder}/lineage-check.json')
    return check


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('action', choices=['run', 'collect'])
    parser.add_argument('--deployment', type=Path, required=True)
    parser.add_argument('--mode', choices=['base', 'refine'], default='refine')
    parser.add_argument('--seed-offset', type=int, choices=[0, 100], default=0)
    parser.add_argument('--size', type=int, choices=[1024, 2048], default=2048)
    parser.add_argument('--denoise', type=float, default=0.45)
    parser.add_argument('--parent-run', type=Path)
    parser.add_argument('--folder', type=Path)
    args = parser.parse_args()
    d = json.loads(args.deployment.read_text())
    if d.get('status') == 'deleted':
        raise RuntimeError('Deployment is closed')
    if args.action == 'collect':
        collect(args.folder, d)
        receipt = json.loads((args.folder/'submission.json').read_text())
        verify_lineage(args.folder, PROJECT/receipt['parent_run'], receipt['mode']=='base')
        return
    if args.mode == 'base':
        args.size, args.denoise = 1024, 1.0
    if not 0 < args.denoise <= 1:
        raise ValueError('denoise must be in (0,1]')
    parent = (args.parent_run.resolve() if args.parent_run else PROJECT/'runs'/ORIGINALS[args.seed_offset])
    parent_receipt = json.loads((parent/'submission.json').read_text())
    if parent_receipt['seed_offset'] != args.seed_offset:
        raise ValueError('Parent seed differs')
    if args.mode == 'refine' and not args.parent_run:
        raise ValueError('Refinement requires the verified base run as --parent-run')
    stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
    label = f'{stamp}-refinement-{args.mode}-s{21001+args.seed_offset}-{args.size}-d{args.denoise:.2f}'
    folder = PROJECT/'runs'/label; folder.mkdir(parents=True)
    graph = build('regional-refinement/'+label, args.seed_offset, args.size, args.denoise, args.mode)
    schema = request(d['base_url'], '/object_info')
    validate(graph, schema)
    ui = ui_workflow(graph, schema)
    write_json(folder/'workflow.api.json', graph)
    write_json(folder/'workflow.json', ui)
    write_json(folder/'node-schemas.json', {n['class_type']: schema[n['class_type']] for n in graph.values()})
    write_json(folder/'system-stats.json', request(d['base_url'], '/system_stats'))
    receipt = {'pod_id': d['pod_id'], 'variant': 'refinement', 'mode': args.mode,
               'seed_offset': args.seed_offset, 'size': args.size, 'denoise': args.denoise,
               'refinement_seed': 21004+args.seed_offset, 'steps': STEPS, 'cfg': CFG,
               'global_prompt': GLOBAL_PROMPT, 'parent_run': str(parent.relative_to(PROJECT)),
               'checkpoint_sha256': MODEL_HASH, 'submitted_at': datetime.now(timezone.utc).isoformat()}
    write_json(folder/'submission.json', receipt)
    try:
        response = request(d['base_url'], '/prompt', {'prompt': graph, 'client_id': label,
                           'extra_data': {'extra_pnginfo': {'workflow': ui}}})
    except Exception as error:
        write_json(folder/'submission-error.json', {'error': str(error),
                   'action': 'Inspect queue/history before retrying an ambiguous submission'})
        raise
    write_json(folder/'submit-response.json', response)
    if not response.get('prompt_id') or response.get('node_errors'):
        raise RuntimeError(response)
    receipt['prompt_id'] = response['prompt_id']; write_json(folder/'submission.json', receipt)
    print(json.dumps({'submitted': response['prompt_id'], 'folder': str(folder)}), flush=True)
    collect(folder, d)
    check = verify_lineage(folder, parent, args.mode=='base')
    print(json.dumps({'first_stage_pixels_identical': check['identical'],
                      'comparison_kind': check['comparison_kind']}), flush=True)


if __name__ == '__main__':
    main()
