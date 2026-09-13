"""One-repaint reference screen; only explicit render submits A1, B or C."""
import argparse
import copy
import json
from pathlib import Path
import shutil

import continuity_controls as control

base = control.base
HERE = Path(__file__).resolve().parent
OUT = HERE.parent / 'exports/reference-screen-v001'
CONTROL_CONFIG = control.CONFIGS / 'euler-060.json'
ARMS = ('A0', 'A1', 'B', 'C')
SEED, FRAME = 918273, 6
LORA = {
    'filename': 'krea2_style_reference.safetensors',
    'url': 'https://huggingface.co/ostris/krea2_turbo_style_reference/resolve/'
           '269e1e4266b89bbabdc64a4f8cebfa0b7254078a/krea2_style_reference.safetensors',
    'bytes': 457111760,
    'sha256': 'f50df5a9e62e4be8aa926a63dd5bb1a64770c4004f763c1208007ae13daa82b8',
}


def read(path):
    return json.loads(path.read_text())


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def copy_once(source, target):
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists():
        require(base.sha(source) == base.sha(target), f'Existing file differs: {target}')
    else:
        shutil.copy2(source, target)


def config():
    row = read(CONTROL_CONFIG)
    require(row['seed'] == SEED and row['cadence'] == FRAME,
            'Control seed/cadence changed; re-align this screen explicitly')
    require(row['case'] == 'euler-060' and row['sampler'] == 'euler'
            and row['cfg'] == 1. and row['motion'] == 'none'
            and row['sigmas'] == base.SIGMAS, 'Control recipe changed')
    return row


def graph(row, arm):
    require(arm in ARMS, f'Unknown arm: {arm}')
    g = control.graph(row, 0)
    require(g['9']['inputs']['noise_seed'] == SEED, 'First-repaint seed mismatch')
    if arm == 'A0':
        return g  # Byte-equivalent declared graph, including original SaveImage prefix.
    n = base.node
    g['11']['inputs']['filename_prefix'] = 'reference-screen-v001/' + arm
    del g['4']
    g['62'] = n('TextEncodeQwenImageEditPlus', clip=['2', 0], vae=['3', 0],
                 prompt=row['prompt'])
    g['63'] = n('FluxKontextMultiReferenceLatentMethod', conditioning=['62', 0],
                 reference_latents_method='index_timestep_zero')
    g['5']['inputs']['conditioning'] = ['63', 0]
    g['9']['inputs']['positive'] = ['63', 0]
    if arm in ('B', 'C'):
        g['60'] = n('LoraLoaderModelOnly', model=['1', 0],
                     lora_name=LORA['filename'], strength_model=1.)
        g['9']['inputs']['model'] = ['60', 0]
    if arm == 'C':
        g['30'] = n('LoadImage', image='reference.png')
        g['62']['inputs']['image1'] = ['30', 0]
    require(g['9']['inputs']['latent_image'] == ['24', 0]
            and g['24']['inputs']['pixels'] == ['20', 0], 'Feedback initialization lost')
    return g


def prepare():
    row = config()
    source = control.OUT / 'source/seed.png'
    require(base.sha(source) == base.sha(base.APP / row['source']),
            'Continuity source differs from configured city')
    copy_once(source, OUT / 'source/seed.png')
    copy_once(source, OUT / 'source/reference.png')
    base.save(OUT / 'manifest.json', {
        'study': 'reference-screen-v001', 'seed': SEED, 'frame': FRAME,
        'seconds': FRAME / row['fps'], 'updates_per_arm': 1,
        'control_config': row, 'control_config_sha256': base.sha(CONTROL_CONFIG),
        'source_sha256': base.sha(source), 'reference_sha256': base.sha(source),
        'reference_policy': 'fixed common city opening; only C receives reference',
        'lora': LORA, 'weight_availability': 'main agent must verify; no download here',
        'runners_sha256': {p.name: base.sha(p) for p in (
            Path(__file__), Path(control.__file__), Path(base.__file__),
            Path(base.pod_client.__file__))},
        'graphs': {arm: graph(row, arm) for arm in ARMS},
    })
    print(f'Prepared one-step screen: seed {SEED}, frame {FRAME}: {OUT}', flush=True)


def prepared():
    manifest = read(OUT / 'manifest.json')
    require(config() == manifest['control_config'], 'Control config changed after prepare')
    require(base.sha(CONTROL_CONFIG) == manifest['control_config_sha256'],
            'Control config bytes changed after prepare')
    for name in ('seed', 'reference'):
        key = 'source_sha256' if name == 'seed' else 'reference_sha256'
        require(base.sha(OUT / f'source/{name}.png') == manifest[key], f'{name} changed')
    for arm in ARMS:
        require(graph(manifest['control_config'], arm) == manifest['graphs'][arm],
                f'Graph changed after prepare: {arm}')
    return manifest


def verify_run(run, expected, source, reference=None):
    require(read(run / 'workflow.api.json') == expected, f'Declared graph differs: {run}')
    executed = copy.deepcopy(expected)
    for node_id, local_name, upload_name, image in (
        ('20', 'anchor.png', 'upload.json', source),
        ('30', 'reference.png', 'upload-reference.json', reference),
    ):
        if image is None:
            require(not (run / local_name).exists(), 'Unexpected reference input')
            continue
        require(base.sha(run / local_name) == base.sha(image), f'{local_name} differs')
        upload = read(run / upload_name)
        if upload.get('sha256'):
            require(upload['sha256'] == base.sha(image), 'Uploaded hash differs')
        executed[node_id]['inputs']['image'] = '/'.join(
            filter(None, [upload.get('subfolder'), upload['name']]))
    require(read(run / 'workflow.executed.json') == executed, 'Executed graph differs')
    submission = read(run / 'submission.json')
    require(submission.get('prompt_id') and submission['frames'] == 1,
            'Missing accepted single-frame submission')
    history = read(run / 'history.json')
    require(history.get('status', {}).get('completed')
            and history['status'].get('status_str') != 'error', 'Run not successful')
    prompt_record = history.get('prompt')
    require(prompt_record and prompt_record[1] == submission['prompt_id']
            and prompt_record[2] == executed, 'Server history does not match execution')
    output = run / 'frames/0000.png'
    require(base.sha(output) == read(run / 'frame-hashes.json')['0000.png'],
            'Archived output hash differs')
    return output


def finish(arm, run, manifest, reused_from=None):
    reference = OUT / 'source/reference.png' if arm == 'C' else None
    output = verify_run(run, manifest['graphs'][arm], OUT / 'source/seed.png', reference)
    root = OUT / arm
    copy_once(OUT / 'source/seed.png', root / 'anchors/0000.png')
    copy_once(output, root / 'anchors/0006.png')
    # Transport owns the complete run archive, including inputs and executed graph.
    hashes = {str(p.relative_to(run)): base.sha(p)
              for p in sorted(run.rglob('*')) if p.is_file()}
    receipt = {
        'arm': arm, 'frame': FRAME, 'seed': SEED, 'updates': 1,
        'run': str(run.relative_to(OUT)), 'reused_from': reused_from,
        'source_sha256': manifest['source_sha256'],
        'reference_sha256': manifest['reference_sha256'] if arm == 'C' else None,
        'output_sha256': base.sha(output), 'run_file_hashes': hashes,
        'manifest_sha256': base.sha(OUT / 'manifest.json'),
    }
    base.save(root / 'anchor-0006.json', receipt)
    print(f'{arm}: one repaint verified; STOP for visual screening: {root}', flush=True)


def reuse_a0():
    manifest = prepared()
    root = control.OUT / 'euler-060'
    receipt = read(root / 'anchor-0006.json')
    require(receipt['frame'] == FRAME and receipt['seed'] == SEED
            and receipt['sampler'] == 'euler'
            and receipt['sigmas'] == manifest['control_config']['sigmas'],
            'A0 receipt settings differ')
    require(receipt['parent_sha256'] == receipt['initialization_sha256']
            == manifest['source_sha256'] == base.sha(root / 'anchors/0000.png'),
            'A0 parent differs')
    original = (control.OUT / receipt['run']).resolve()
    require(original.is_relative_to(control.OUT.resolve()), 'A0 run outside control archive')
    output = verify_run(original, manifest['graphs']['A0'], OUT / 'source/seed.png')
    require(base.sha(output) == receipt['output_sha256']
            == base.sha(root / 'anchors/0006.png'), 'A0 output receipt differs')
    archived = OUT / 'reused-control' / original.name
    for path in sorted(original.rglob('*')):
        if path.is_file():
            copy_once(path, archived / path.relative_to(original))
    copy_once(root / 'anchor-0006.json', OUT / 'A0/control-anchor-0006.json')
    finish('A0', archived, manifest, str(original))


def render(arm, deployment):
    require(arm in ('A1', 'B', 'C'), 'A0 must be reused, never submitted')
    manifest = prepared()
    base.pod_client.DEPLOYMENT = deployment.resolve()
    name = 'reference-screen-v001-' + arm
    matches = list((OUT / 'runs').glob('*-' + name + '-1f'))
    require(len(matches) <= 1, 'Multiple attempts exist; inspect manually')
    if matches:
        run = matches[0]
        require(read(run / 'workflow.api.json') == manifest['graphs'][arm], 'Attempt graph differs')
        require(read(run / 'submission.json').get('prompt_id'),
                'Uncertain/rejected previous attempt: inspect queue/history; never auto-resubmit')
        # Reconnect only to an already accepted job; no duplicate prompt submission.
        base.pod_client.collect(run)
        if not (run / 'frame-hashes.json').exists():
            base.save(run / 'frame-hashes.json', {'0000.png': base.sha(run / 'frames/0000.png')})
    else:
        (OUT / 'runs').mkdir(parents=True, exist_ok=True)
        run = base.pod_client.submit(OUT, name, manifest['graphs'][arm], 1,
            source=OUT / 'source/seed.png',
            reference=OUT / 'source/reference.png' if arm == 'C' else None,
            lineage={'study': 'reference-screen-v001', 'arm': arm, 'frame': FRAME,
                     'seed': SEED, 'source_sha256': manifest['source_sha256'],
                     'reference_sha256': manifest['reference_sha256'] if arm == 'C' else None,
                     'manifest_sha256': base.sha(OUT / 'manifest.json')})
    finish(arm, run, manifest)


def verify(arm):
    manifest = prepared()
    receipt = read(OUT / arm / 'anchor-0006.json')
    run = OUT / receipt['run']
    require(receipt['manifest_sha256'] == base.sha(OUT / 'manifest.json'), 'Manifest changed')
    for name, digest in receipt['run_file_hashes'].items():
        require(base.sha(run / name) == digest, f'Archive changed: {name}')
    reference = OUT / 'source/reference.png' if arm == 'C' else None
    output = verify_run(run, manifest['graphs'][arm], OUT / 'source/seed.png', reference)
    require(base.sha(output) == receipt['output_sha256']
            == base.sha(OUT / arm / 'anchors/0006.png'), 'Screen output changed')
    require(base.sha(OUT / arm / 'anchors/0000.png') == manifest['source_sha256'],
            'Screen opening changed')
    print(f'{arm}: archive verified offline', flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('stage', choices=('prepare', 'reuse-a0', 'render', 'verify'))
    parser.add_argument('--arm', choices=ARMS)
    parser.add_argument('--deployment', type=Path)
    args = parser.parse_args()
    if args.stage == 'prepare':
        prepare()
    elif args.stage == 'reuse-a0':
        reuse_a0()
    elif args.stage == 'render':
        if args.arm not in ('A1', 'B', 'C') or args.deployment is None:
            parser.error('render requires --arm A1|B|C and explicit --deployment PATH')
        render(args.arm, args.deployment)
    else:
        if args.arm is None:
            parser.error('verify requires --arm')
        verify(args.arm)
