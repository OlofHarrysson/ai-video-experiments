"""Isolated SPEED midpoint audition. No network, provisioning, or ComfyUI calls.

prepare: freeze saved Oracle endpoints and exact-time RIFE controls.
infer: CUDA only, after the main agent grants an explicit lease.
compare: midpoint sheets or 8fps diagnostic clips; never retimes production.
self-test: bounded timestamp/seed/input validation, no model inference.
"""
from __future__ import annotations

import argparse
from fractions import Fraction
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time

PROJECT = Path(__file__).resolve().parents[1]
CODE_COMMIT = '40fadbe85c88cc6e4015062389da464fd7e85ab9'
MODEL_REVISION = '06525dc071b4f18e822cf55d25ed6bfa858d4544'
MODEL_SHA256 = 'abd078f6a1135a84e13f0003e996d121d4adc2c41adf5f67d933c76c958243cd'
MODEL_BYTES = 468610980
PAIRS = [('high3-seedface-4-5', 'high3', 4), ('high3-eye-1-2', 'high3', 1),
         ('high1-late-8-9', 'high1', 8)]
BASE_SEED = 20260910


def sha(path):
    with Path(path).open('rb') as handle:
        return hashlib.file_digest(handle, 'sha256').hexdigest()


def write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix('.tmp')
    tmp.write_text(json.dumps(data, indent=2) + '\n')
    tmp.replace(path)


def copy_exact(source, target):
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists():
        if sha(target) != sha(source):
            raise ValueError(f'Existing file differs: {target}')
    else:
        shutil.copy2(source, target)
    return sha(target)


def schedule(depth):
    """Breadth-first recursion; temporal fractions are exact and seed-stable."""
    if depth not in (1, 3):
        raise ValueError('Only midpoint (1) and bounded eighths (3) are allowed')
    return [(Fraction(i - 1, 2**d), Fraction(i, 2**d), Fraction(i + 1, 2**d))
            for d in range(1, depth + 1) for i in range(1, 2**d, 2)]


def filename(t):
    return f'{t.numerator}_{t.denominator}.png'


def node_seed(pair, t):
    key = f'{BASE_SEED}:{pair}:{t.numerator}/{t.denominator}'
    return int.from_bytes(hashlib.sha256(key.encode()).digest()[:4], 'big')


def review_timeline():
    """Paired diagnostic roles understood by the shared video review reader."""
    return [dict(index=i, time_seconds=i / 8, **(
        {'kind': 'anchor', 'source_index': 0} if i == 0 else
        {'kind': 'final_hold', 'source_index': 1} if i == 8 else
        {'kind': 'interpolation', 'source_pair': [0, 1], 'timestep': str(Fraction(i, 8))}
    )) for i in range(9)]


def checked_manifest(bundle):
    manifest = json.loads((bundle / 'inputs.json').read_text())
    for pair in manifest['pairs']:
        for row in pair['files']:
            if sha(bundle / row['file']) != row['sha256']:
                raise ValueError(f'Input hash mismatch: {row["file"]}')
    return manifest


def prepare(args):
    from PIL import Image
    bundle = args.bundle
    rows = []
    for name, case, start in PAIRS:
        root = args.project / 'exports/oracle-steps-v001' / case / 'cadence-24'
        receipt = json.loads((root / 'rife-raw/manifest.json').read_text())
        assert receipt['status'] == 'complete'
        assert receipt['provenance']['model'] == 'RIFE 4.25'
        assert receipt['settings']['scale'] == 1.0
        assert receipt['settings']['output_fps'] == 24
        assert receipt['settings']['source_fps'] == 1.0
        known = {r['file']: r['sha256'] for r in receipt['output_frames']}
        files = []
        for tick in range(9):
            # Source anchors have an absolute runner offset of 72; rife-sources
            # are already indexed by shot seconds. Use those, not anchor numbers.
            index = start * 24 + tick * 3
            src = root / f'rife-raw/frames/{index:04d}.png'
            assert sha(src) == known[f'frames/{index:04d}.png']
            if tick in (0, 8):
                anchor = root / f'rife-sources/{start + tick // 8:04d}.png'
                assert sha(src) == sha(anchor)
            with Image.open(src) as im:
                assert im.size == (1536, 1024) and im.mode == 'RGB'
            rel = f'{name}/rife/{tick:04d}.png'
            files.append({'file': rel, 'sha256': copy_exact(src, bundle / rel),
                          'time': str(Fraction(tick, 8)), 'source': str(src),
                          'source_mtime_ns': src.stat().st_mtime_ns,
                          'source_frame': index, 'shot_seconds': str(Fraction(index, 24))})
        rows.append({'id': name, 'case': case, 'start_seconds': start, 'files': files,
                     'rife_receipt_sha256': sha(root / 'rife-raw/manifest.json'),
                     'rife_provenance': receipt['provenance'], 'rife_settings': receipt['settings']})
    result = {'status': 'prepared-no-inference', 'pairs': rows,
              'code_commit': CODE_COMMIT, 'model_revision': MODEL_REVISION,
              'model_sha256': MODEL_SHA256, 'shape_wh': [1536, 1024],
              'production_fps': 24, 'repaint_seconds': 1,
              'diagnostic_fps': 8, 'base_seed': BASE_SEED,
              'diagnostic_timing': '9 frames at 8fps: endpoint PTS 0 and 1; total container duration 9/8s includes final endpoint display for 1/8s. No repeated or omitted diagnostic frames. RIFE deliberately sampled at exact eighths.'}
    target = bundle / 'inputs.json'
    if target.exists():
        assert json.loads(target.read_text()) == result, 'Prepared inputs changed'
    else:
        write_json(target, result)
    checked_manifest(bundle)
    print(json.dumps({'bundle': str(bundle), 'pairs': len(rows), 'files': 27,
                      'inputs_sha256': sha(target)}, indent=2))


def infer(args):
    if not args.lease_id:
        raise ValueError('An explicit main-agent GPU lease ID is required')
    # A caller-supplied token records the granted lease; this is not a cloud API.
    import platform
    import random
    import numpy as np
    import torch
    manifest = checked_manifest(args.bundle)
    code = args.upstream.resolve()
    commit = subprocess.check_output(['git', '-C', str(code), 'rev-parse', 'HEAD'], text=True).strip()
    assert commit == CODE_COMMIT
    assert not subprocess.check_output(['git', '-C', str(code), 'status', '--porcelain', '--untracked-files=no'], text=True).strip()
    assert args.weights.stat().st_size == MODEL_BYTES and sha(args.weights) == MODEL_SHA256
    assert torch.cuda.is_available(), 'CUDA-only leased execution; no CPU/MPS fallback'
    assert torch.cuda.is_bf16_supported(), 'This audition uses bf16 as specified'
    sys.path.insert(0, str(code))
    import inference as upstream
    from src.config import load_config
    from src.runtime import build_model_from_config
    # Do not install xformers: use the implementation's native SDPA branch.
    from src.models.modules import attention
    assert attention._xformers_attention is None, 'Expected isolated PyTorch SDPA environment'
    os.environ.setdefault('CUBLAS_WORKSPACE_CONFIG', ':4096:8')
    torch.backends.cuda.matmul.allow_tf32 = False
    torch.backends.cudnn.allow_tf32 = False
    torch.backends.cudnn.benchmark = False
    torch.use_deterministic_algorithms(True)
    device = torch.device('cuda:0')
    started = time.monotonic()
    source_files = sorted(p for p in set([code / 'inference.py'] + list((code / 'src').rglob('*.py'))
                          + list((code / 'configs').glob('*.yaml'))) if not p.name.startswith('._'))
    identity = {'code_commit': commit, 'code_sha256': {str(p.relative_to(code)): sha(p) for p in source_files},
                'weights_sha256': MODEL_SHA256, 'inputs_sha256': sha(args.bundle / 'inputs.json'),
                'runner_sha256': sha(Path(__file__)), 'precision': 'bf16', 'attention': 'upstream PyTorch SDPA',
                'torch': torch.__version__, 'cuda': torch.version.cuda, 'numpy': np.__version__,
                'gpu': torch.cuda.get_device_name(), 'python': platform.python_version(),
                'base_seed': BASE_SEED, 'deterministic_algorithms': True, 'tf32': False}
    args.output.mkdir(parents=True, exist_ok=True)
    run_path = args.output / 'inference.json'
    report = json.loads(run_path.read_text()) if run_path.exists() else {'identity': identity, 'nodes': {}, 'sessions': []}
    assert report['identity'] == identity, 'Resume identity changed; use a new output directory'
    session = {'lease_id': args.lease_id, 'depth': args.depth, 'max_calls': args.max_calls,
               'max_seconds': args.max_seconds, 'status': 'loading', 'calls': 0}
    report['sessions'].append(session)
    write_json(run_path, report)
    try:
        torch.cuda.reset_peak_memory_stats()
        model, info = build_model_from_config(load_config(code / 'configs/eval_config.yaml'),
                            device=device, pretrained_path=str(args.weights), strict_load=True,
                            require_checkpoint=True, eval_mode=True)
        assert not info['missing_keys'] and not info['unexpected_keys']
        report['parameters'] = info['total_params']
        session['model_load_seconds'] = time.monotonic() - started
        session['status'] = 'running'
        write_json(run_path, report)

        def predict(pair_id, t, left, right, destination):
            if session['calls'] >= args.max_calls or time.monotonic() - started >= args.max_seconds:
                raise RuntimeError('Explicit inference lease budget reached')
            seed = node_seed(pair_id, t)
            random.seed(seed)
            np.random.seed(seed)
            torch.manual_seed(seed)
            torch.cuda.manual_seed_all(seed)
            a, b = upstream.read_rgb_image(left), upstream.read_rgb_image(right)
            assert a.shape == b.shape == (1024, 1536, 3)
            torch.cuda.synchronize()
            before = time.monotonic()
            prediction = upstream.interpolate_batch(model, [a], [b], device, precision='bf16')[0]
            torch.cuda.synchronize()
            elapsed = time.monotonic() - before
            assert prediction.shape == a.shape and prediction.dtype == np.uint8
            upstream.write_rgb_image(destination, prediction)
            session['calls'] += 1
            return {'seed': seed, 'time': str(t), 'sha256': sha(destination),
                    'parents_sha256': [sha(left), sha(right)], 'inference_seconds': elapsed,
                    'file': str(destination.relative_to(args.output))}

        for pair in manifest['pairs']:
            pair_id = pair['id']
            root = args.output / pair_id / 'speed'
            root.mkdir(parents=True, exist_ok=True)
            paths = {Fraction(0): root / filename(Fraction(0)), Fraction(1): root / filename(Fraction(1))}
            copy_exact(args.bundle / f'{pair_id}/rife/0000.png', paths[Fraction(0)])
            copy_exact(args.bundle / f'{pair_id}/rife/0008.png', paths[Fraction(1)])
            for left_t, t, right_t in schedule(args.depth):
                target = root / filename(t)
                key = f'{pair_id}:{t}'
                if key in report['nodes']:
                    row = report['nodes'][key]
                    assert sha(target) == row['sha256']
                    assert row['seed'] == node_seed(pair_id, t)
                    assert row['parents_sha256'] == [sha(paths[left_t]), sha(paths[right_t])]
                else:
                    assert not target.exists(), f'Unreceipted output: {target}'
                    report['nodes'][key] = predict(pair_id, t, paths[left_t], paths[right_t], target)
                    report['nodes'][key]['parents_time'] = [str(left_t), str(right_t)]
                    write_json(run_path, report)
                    print(json.dumps({'node': key, **report['nodes'][key]}), flush=True)
                paths[t] = target
            if args.repeat_check and pair_id == manifest['pairs'][0]['id'] and 'repeat_check' not in report:
                repeat = args.output / 'repeat-midpoint.png'
                assert not repeat.exists(), 'Unreceipted repeat output exists'
                row = predict(pair_id, Fraction(1, 2), paths[Fraction(0)], paths[Fraction(1)], repeat)
                row['matches_first'] = row['sha256'] == report['nodes'][f'{pair_id}:1/2']['sha256']
                report['repeat_check'] = row
                write_json(run_path, report)
                assert row['matches_first'], 'Same-seed repetition was not byte-identical'
        session['status'] = 'complete'
    except Exception as exc:
        session['status'] = 'failed'
        session['error'] = f'{type(exc).__name__}: {exc}'
        raise
    finally:
        session['elapsed_seconds'] = time.monotonic() - started
        session['peak_allocated_bytes'] = torch.cuda.max_memory_allocated()
        session['peak_reserved_bytes'] = torch.cuda.max_memory_reserved()
        write_json(run_path, report)
        print(json.dumps(session), flush=True)


def compare(args):
    from PIL import Image, ImageDraw, ImageFont
    manifest = checked_manifest(args.bundle)
    report = json.loads((args.output / 'inference.json').read_text())
    assert report['identity']['inputs_sha256'] == sha(args.bundle / 'inputs.json')
    assert report['identity']['weights_sha256'] == MODEL_SHA256
    for row in report['nodes'].values():
        assert sha(args.output / row['file']) == row['sha256']
    font = ImageFont.load_default(size=22)
    results = []
    for pair in manifest['pairs']:
        name = pair['id']
        root = args.output / name
        midpoint = root / 'speed/1_2.png'
        assert midpoint.exists()
        sources = [args.bundle / f'{name}/rife/0000.png', args.bundle / f'{name}/rife/0004.png',
                   midpoint, args.bundle / f'{name}/rife/0008.png']
        sheet = Image.new('RGB', (1536, 548), '#16191d')
        draw = ImageDraw.Draw(sheet)
        for i, (source, label) in enumerate(zip(sources, ['Start', 'RIFE midpoint', 'SPEED midpoint', 'End'])):
            with Image.open(source) as im:
                sheet.paste(im.resize((384, 256), Image.Resampling.LANCZOS), (i * 384, 36))
                # Native-resolution central 384x224 crop to inspect fine texture.
                sheet.paste(im.crop((576, 400, 960, 624)), (i * 384, 324))
            draw.text((i * 384 + 10, 7), label, font=font, fill='white')
        draw.text((10, 295), f'{name} | lower row: center detail at native pixels', font=font, fill='white')
        sheet.save(root / 'midpoint-comparison.png')
        if not args.video:
            continue
        frames = root / 'diagnostic-8fps/frames'
        frames.mkdir(parents=True, exist_ok=True)
        rows = []
        for tick in range(9):
            t = Fraction(tick, 8)
            speed = root / 'speed' / filename(t)
            rife = args.bundle / f'{name}/rife/{tick:04d}.png'
            if tick in (0, 8):
                assert sha(speed) == sha(rife), 'Endpoint altered'
            else:
                assert report['nodes'][f'{name}:{t}']['sha256'] == sha(speed)
            canvas = Image.new('RGB', (1536, 586), '#16191d')
            draw = ImageDraw.Draw(canvas)
            for x, src, title in [(0, rife, 'RIFE 4.25'), (768, speed, 'SPEED recursive')]:
                with Image.open(src) as im:
                    canvas.paste(im.resize((768, 512), Image.Resampling.LANCZOS), (x, 44))
                draw.text((x + 10, 10), f'{title} | 8fps DIAGNOSTIC | t={float(t):.3f}s', font=font, fill='white')
            draw.text((10, 561), 'Endpoint PTS: 0s / 1s | final endpoint held 1.000-1.125s | production 24fps unchanged',
                      font=font, fill='white')
            dest = frames / f'{tick:04d}.png'
            canvas.save(dest)
            rows.append({'frame': tick, 'pts': str(t), 'speed_sha256': sha(speed), 'rife_sha256': sha(rife), 'sha256': sha(dest)})
        video = frames.parent / 'comparison.mp4'
        if video.exists():
            raise ValueError(f'Preserving existing video; choose a fresh comparison directory: {video}')
        subprocess.run(['ffmpeg', '-v', 'error', '-n', '-framerate', '8', '-i', str(frames / '%04d.png'),
                        '-frames:v', '9', '-c:v', 'libx264', '-crf', '17', '-pix_fmt', 'yuv420p',
                        '-movflags', '+faststart', str(video)], check=True)
        probe = json.loads(subprocess.check_output(['ffprobe', '-v', 'error', '-count_frames', '-select_streams', 'v:0',
                          '-show_streams', '-show_frames', '-of', 'json', str(video)]))
        stream = probe['streams'][0]
        assert stream['avg_frame_rate'] == '8/1' and int(stream['nb_read_frames']) == 9
        assert Fraction(stream['duration']) == Fraction(9, 8)
        assert [Fraction(f['pts']) * Fraction(stream['time_base']) for f in probe['frames']] == [Fraction(i, 8) for i in range(9)]
        subprocess.run(['ffmpeg', '-v', 'error', '-xerror', '-i', str(video), '-f', 'null', '-'], check=True)
        record = {'status': 'complete', 'frames': rows, 'output_frames': review_timeline(),
                  'video_sha256': sha(video), 'probe': stream,
                  'timing': manifest['diagnostic_timing'], 'production_changed': False,
                  'inputs_sha256': sha(args.bundle / 'inputs.json'), 'inference_sha256': sha(args.output / 'inference.json')}
        write_json(frames.parent / 'manifest.json', record)
        results.append(str(video))
    print(json.dumps({'comparisons': results, 'midpoint_sheets': len(manifest['pairs'])}, indent=2))


def self_test(args):
    plan = schedule(3)
    available = {Fraction(0), Fraction(1)}
    for left, t, right in plan:
        assert left in available and right in available
        assert t == (left + right) / 2 and t not in available
        available.add(t)
    assert sorted(available) == [Fraction(i, 8) for i in range(9)]
    assert len(plan) == 7 and len(schedule(1)) == 1
    assert schedule(1)[0] == plan[0]
    assert Fraction(1, 24) not in available
    assert all((Fraction(i, 8) * 24).denominator == 1 for i in range(9))
    assert [Fraction(str(r['time_seconds'])) for r in review_timeline()] == sorted(available)
    assert review_timeline()[-1]['kind'] == 'final_hold'
    seeds = [node_seed(pair, t) for pair, _, _ in PAIRS for _, t, _ in plan]
    assert len(seeds) == len(set(seeds))
    assert node_seed(PAIRS[0][0], Fraction(1, 2)) == node_seed(PAIRS[0][0], Fraction(4, 8))
    if (args.bundle / 'inputs.json').exists():
        manifest = checked_manifest(args.bundle)
        for pair in manifest['pairs']:
            for row in pair['files']:
                src = Path(row['source'])
                assert sha(src) == row['sha256']
                assert src.stat().st_mtime_ns == row['source_mtime_ns']
    print('PASS: recursion ancestry, exact timestamps, 24fps incompatibility, stable distinct seeds, frozen inputs and source mtimes; no inference')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['prepare', 'infer', 'compare', 'self-test'])
    parser.add_argument('--project', type=Path, default=PROJECT)
    parser.add_argument('--bundle', type=Path, default=PROJECT / 'work/speed-oracle-session/bundle')
    parser.add_argument('--upstream', type=Path, default=PROJECT / 'work/speed-oracle-session/SPEED')
    parser.add_argument('--weights', type=Path, default=PROJECT / 'work/speed-oracle-session/speed.pt')
    parser.add_argument('--output', type=Path, default=PROJECT / 'exports/speed-oracle-v001')
    parser.add_argument('--lease-id', help='Main-agent authorization receipt; infer only')
    parser.add_argument('--depth', type=int, choices=[1, 3], default=1)
    parser.add_argument('--max-calls', type=int, default=4)
    parser.add_argument('--max-seconds', type=int, default=600)
    parser.add_argument('--repeat-check', action='store_true')
    parser.add_argument('--video', action='store_true')
    args = parser.parse_args()
    if args.max_calls < 1 or args.max_seconds < 1:
        parser.error('Budgets must be positive')
    for name in ['project', 'bundle', 'upstream', 'weights', 'output']:
        setattr(args, name, getattr(args, name).resolve())
    {'prepare': prepare, 'infer': infer, 'compare': compare, 'self-test': self_test}[args.action](args)


if __name__ == '__main__':
    main()
