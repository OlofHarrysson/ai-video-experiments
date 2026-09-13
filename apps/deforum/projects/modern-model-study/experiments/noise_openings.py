"""Five independent Krea openings: native parity and controlled noise distances.

prepare and verify are local-only. Only render submits/collects GPU jobs.
"""
import argparse
import hashlib
import json
import math
from pathlib import Path
import shutil

import numpy as np
from PIL import Image
import ten_dollar as base

HERE = Path(__file__).resolve().parent
OUT = HERE.parent / 'exports/noise-openings-v001'
CONFIGS = HERE / 'noise-openings-configs'
PROMPT_CONFIG = HERE / 'continuity-controls-configs/euler-060.json'
SEED, WIDTH, HEIGHT, STEPS = 918273, 1536, 1024, 8
# Order is significant: establish parity before spending on perturbations.
CASES = {
    'native-euler-simple8': (None, 0),
    'advanced-same-noise': (0., 0),
    'nearby-rho-09998': (.9998, 1),
    'nearby-rho-098': (.98, 1),
    'fresh-seed-918274': (0., 1),
}
NATIVE, PARITY = tuple(CASES)[:2]


def read(path):
    return json.loads(path.read_text())


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def configurations():
    source = read(PROMPT_CONFIG)
    return {case: {
        'case': case, 'prompt': source['prompt'],
        'prompt_source': str(PROMPT_CONFIG.relative_to(HERE)),
        'prompt_source_sha256': base.sha(PROMPT_CONFIG),
        'seed': SEED, 'index': index, 'correlation': rho,
        'tag': None if rho is None else 'noise-openings-v001-' + case,
        'width': WIDTH, 'height': HEIGHT, 'steps': STEPS,
        'sampler': 'euler', 'scheduler': 'simple', 'denoise': 1., 'cfg': 1.,
        'initialization': 'empty latent; no prior image; independent text-to-image opening',
    } for case, (rho, index) in CASES.items()}


def graph(config):
    g = base.graph('krea', config['prompt'], config['seed'])
    g['6']['inputs'].update(width=config['width'], height=config['height'], batch_size=1)
    g['9']['inputs'].update(steps=config['steps'], cfg=config['cfg'],
        sampler_name=config['sampler'], scheduler=config['scheduler'], denoise=config['denoise'])
    if config['correlation'] is not None:
        n = base.node
        g['42'] = n('KSamplerSelect', sampler_name=config['sampler'])
        g['43'] = n('BasicScheduler', model=['1', 0], scheduler=config['scheduler'],
                    steps=config['steps'], denoise=config['denoise'])
        g['44'] = n('DeforumRecordedNoise', seed=config['seed'], index=config['index'],
                    correlation=config['correlation'], tag=config['tag'])
        g['45'] = n('CFGGuider', model=['1', 0], positive=['4', 0], negative=['5', 0], cfg=config['cfg'])
        g['9'] = n('SamplerCustomAdvanced', noise=['44', 0], guider=['45', 0],
                    sampler=['42', 0], sigmas=['43', 0], latent_image=['6', 0])
    g['11']['inputs']['filename_prefix'] = 'noise-openings-v001/' + config['case']
    return g


def load_config(case):
    config = read(CONFIGS / f'{case}.json')
    require(config == configurations()[case], f'Config or stationary prompt changed: {case}')
    require(read(CONFIGS / f'{case}.workflow.json') == graph(config), f'Prepared graph changed: {case}')
    return config


def prepare():
    # Deliberately writes only the assigned config directory, not exports/media.
    for case, config in configurations().items():
        base.save(CONFIGS / f'{case}.json', config)
        base.save(CONFIGS / f'{case}.workflow.json', graph(config))
    print('Prepared five opening graphs locally; no submissions.', flush=True)


def pixels(path):
    with Image.open(path) as im:
        require(im.size == (WIDTH, HEIGHT), f'Unexpected image dimensions: {path}')
        return np.asarray(im.convert('RGB'))


def check_run(case, run, target=None):
    expected = graph(load_config(case))
    require(read(run / 'workflow.api.json') == expected, f'Request graph mismatch: {case}')
    require(read(run / 'workflow.executed.json') == expected, f'Executed graph mismatch: {case}')
    history = read(run / 'history.json')
    require(history['status']['completed'] and history['status']['status_str'] == 'success',
            f'Run did not complete successfully: {case}')
    require(history['prompt'][2] == expected, f'History graph mismatch: {case}')
    prompt_id = read(run / 'submit-response.json')['prompt_id']
    require(history['prompt'][1] == prompt_id, f'History prompt ID mismatch: {case}')
    require(not (run / 'anchor.png').exists() and not (run / 'upload.json').exists(),
            f'Unexpected image initialization: {case}')
    frame = run / 'frames/0000.png'
    require(len(list((run / 'frames').glob('*.png'))) == 1, f'Expected one opening: {case}')
    pixels(frame)
    digest = base.sha(frame)
    if target is not None:
        require(base.sha(target) == digest, f'Output hash mismatch: {case}')
    return {'case': case, 'run': str(run.relative_to(OUT)), 'prompt_id': prompt_id,
            'output_sha256': digest}


def completed(case):
    root = OUT / case
    row = read(root / 'opening.json')
    require(read(root / 'config.json') == load_config(case), f'Saved config mismatch: {case}')
    checked = check_run(case, OUT / row['run'], root / f'{case}.png')
    require(row == checked, f'Receipt mismatch: {case}')
    return checked


def check_parity():
    for case in (NATIVE, PARITY):
        completed(case)
    a = pixels(OUT / NATIVE / f'{NATIVE}.png')
    b = pixels(OUT / PARITY / f'{PARITY}.png')
    require(np.array_equal(a, b), 'Native/advanced pixels differ; stop before perturbation jobs.')
    return {'pixel_identical': True, 'max_abs_difference': 0}


def render(case):
    base.OUT = OUT
    config = load_config(case)
    if case == PARITY:
        completed(NATIVE)
    if case not in (NATIVE, PARITY):
        check_parity()
    root = OUT / case
    if (root / 'opening.json').exists():
        completed(case)
        print(f'{case}: verified existing opening; no remote call.', flush=True)
    else:
        base.save(root / 'config.json', config)
        # submit_once resumes an existing run by collecting it. It never replaces
        # an uncertain/rejected submission with a second request under a new name.
        run = base.submit_once('noise-openings-v001-' + case, graph(config), source=None,
            lineage={'study': 'noise-openings-v001', 'case': case,
                     'initialization': config['initialization'], 'noise_tag': config['tag']})
        row = check_run(case, run)
        target = root / f'{case}.png'
        if target.exists():
            require(base.sha(target) == row['output_sha256'], f'Output collision: {case}')
        else:
            shutil.copy2(run / 'frames/0000.png', target)
        base.save(root / 'opening.json', row)
        print(f'{case}: collected and checked one opening.', flush=True)
    if case == PARITY:
        base.save(OUT / 'sampler-parity.json', check_parity())


def verify(noise_root):
    """Read local collected jobs and manually archived recorder files; no network."""
    rows = [completed(case) for case in CASES]
    require(len({r['prompt_id'] for r in rows}) == 5, 'Expected five distinct job IDs')
    parity = check_parity()
    noises, metadata = {}, {}
    for case in tuple(CASES)[1:]:
        config = load_config(case)
        path = noise_root / config['tag'] / f"{config['index']:04d}.npz"
        record = read(path.with_suffix('.json'))
        with np.load(path, allow_pickle=False) as data:
            eps, latent = data['noise'].copy(), data['input_latent'].copy()
        require(eps.shape == latent.shape == (1, 16, 1, HEIGHT // 8, WIDTH // 8),
                f'Unexpected actual noise/latent shape: {case}')
        require(np.isfinite(eps).all() and np.isfinite(latent).all(), f'Nonfinite tensor: {case}')
        require(np.count_nonzero(latent) == 0, f'Expected empty input latent: {case}')
        require(record['base_seed'] == SEED and record['index'] == config['index']
                and record['correlation'] == config['correlation']
                and record['sampling_seed'] == SEED + config['index']
                and record['shape'] == list(eps.shape), f'Noise metadata mismatch: {case}')
        require(record['noise_sha256'] == hashlib.sha256(eps.tobytes()).hexdigest(),
                f'Noise checksum mismatch: {case}')
        require(abs(float(eps.mean())) < .015 and abs(float(eps.std()) - 1) < .015,
                f'Unexpected Gaussian statistics: {case}')
        noises[case] = eps
        metadata[case] = {'tag': config['tag'], 'index': config['index'],
            'archive_npz_sha256': base.sha(path), 'archive_json_sha256': base.sha(path.with_suffix('.json')),
            'noise_sha256': record['noise_sha256'], 'mean': float(eps.mean()), 'std': float(eps.std())}
    original, fresh = noises[PARITY], noises['fresh-seed-918274']
    for case, eps in noises.items():
        rho, index = CASES[case]
        if index == 1 and rho:
            expected = np.float32(rho) * original + np.float32(math.sqrt(1 - rho*rho)) * fresh
            np.testing.assert_allclose(eps, expected, atol=5e-7, rtol=1e-6,
                                       err_msg=f'Actual noise recurrence mismatch: {case}')
        corr = float(np.corrcoef(original.ravel(), eps.ravel())[0, 1])
        expected_corr = 1. if index == 0 else rho
        require(abs(corr - expected_corr) < .01, f'Actual correlation mismatch: {case}')
        delta = eps.astype(np.float64) - original.astype(np.float64)
        metadata[case].update(correlation_to_baseline=corr,
            rms_displacement_to_baseline=float(np.sqrt(np.mean(delta*delta))),
            expected_rms_displacement=math.sqrt(2 - 2*expected_corr))
    report = {'verified': True, 'jobs': rows, 'native_advanced_parity': parity,
        'noise': metadata, 'scope': 'Executed graphs, PNG parity, archived actual advanced noise and empty initialization. No perceptual-quality verdict.',
        'native_noise_record': 'advanced-same-noise captures the native-equivalent draw; native KSampler itself is unmodified.'}
    base.save(OUT / 'verification.json', report)
    print('Verified five openings, exact parity, empty initialization and actual noise recurrence.', flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('stage', choices=['prepare', 'render', 'verify'])
    parser.add_argument('--case', choices=CASES, help='render one case; omitted runs all five in order')
    parser.add_argument('--deployment', type=Path, help='explicit existing Pod deployment for render only')
    parser.add_argument('--noise-root', type=Path,
                        help='local archived deforum-noise-study directory, containing the four tag directories')
    args = parser.parse_args()
    if args.stage == 'prepare':
        prepare()
    elif args.stage == 'verify':
        if args.noise_root is None:
            parser.error('verify requires --noise-root pointing to locally archived actual noise')
        verify(args.noise_root.resolve())
    else:
        if args.deployment is None:
            parser.error('render requires --deployment for the main-agent-owned Pod')
        base.pod_client.DEPLOYMENT = args.deployment.resolve()
        for case in ([args.case] if args.case else CASES):
            render(case)


if __name__ == '__main__':
    main()
