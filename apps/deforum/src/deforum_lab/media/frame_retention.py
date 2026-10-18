"""Restore or retire explicitly selected RIFE frames after an exact full rebuild.

Only the current pinned interpolate.py recipe is supported. This never removes
source paintings, videos, manifests, anchors, holds, or whole frame directories.
"""
import argparse
import json
import os
import re
import shutil
import subprocess
import tempfile
from datetime import UTC, datetime
from fractions import Fraction
from pathlib import Path

from .storage import digest

ROOT = Path(__file__).resolve().parents[3]
RUNTIME = ROOT / 'work/rife-session/.venv/bin/python'
RUNNER = ROOT / 'interpolate.py'
RIFE = ROOT / 'work/rife-session/Practical-RIFE'


def save(path, value):
    temporary = path.with_suffix('.tmp')
    with temporary.open('w') as stream:
        json.dump(value, stream, indent=2)
        stream.flush()
        os.fsync(stream.fileno())
    os.replace(temporary, path)


def checked_file(path, expected):
    path = Path(path)
    if path.resolve() != path or not path.is_file():
        raise ValueError(f'Not an ordinary file at its recorded path: {path}')
    before = path.stat()
    if digest(path) != expected or path.stat() != before:
        raise ValueError(f'Changed file: {path}')
    return before


def frame_path(manifest, row):
    if not re.fullmatch(r'frames/[0-9]+\.png', row['file']):
        raise ValueError('Unsupported output path')
    return manifest.parent / row['file']


def selected_frames(manifest, record, candidates):
    allowed = {str(frame_path(manifest, row)): row for row in record['output_frames']
               if row['kind'] == 'interpolation'}
    if len(candidates) != len(set(candidates)) or not set(candidates) <= allowed.keys():
        raise ValueError('Selection contains a duplicate, original, or unknown frame')
    return [allowed[path] for path in candidates]


def dependencies(manifest, record):
    if record.get('status') != 'complete' or record.get('mode') != 'full':
        raise ValueError('Only completed full sequences are supported')
    p = record['provenance']
    checked_file(RUNNER, p['runner_sha256'])
    checked_file(RIFE / 'train_log/flownet.pkl', p['weights_sha256'])
    checked_file(RIFE.parent / 'rife425.zip', p['bundle_sha256'])
    for name, sha in p['code_sha256'].items():
        if Path(name).is_absolute() or '..' in Path(name).parts:
            raise ValueError('Invalid model code path')
        checked_file(RIFE / name, sha)
    for source in record['sources']:
        checked_file(Path(source['file']), source['sha256'])
    checked_file(manifest.parent / 'preview.mp4', record['video_sha256'])
    if not RUNTIME.is_file():
        raise ValueError('Pinned Python runtime is missing')


def verify_rows(manifest, record, rebuilt, output):
    if (rebuilt.get('status') != 'complete'
            or rebuilt['provenance'] != record['provenance']
            or rebuilt['settings'] != record['settings']
            or rebuilt['output_frames'] != record['output_frames']):
        raise ValueError('Reconstructed sequence differs from the saved recipe/hashes')
    for row in record['output_frames']:
        checked_file(output / row['file'], row['sha256'])


def rebuild(manifest, record, scratch):
    sources = [Path(s['file']) for s in record['sources']]
    if not sources or len({p.parent for p in sources}) != 1:
        raise ValueError('Expected one source directory')
    settings = record['settings']
    args = [str(RUNTIME), str(RUNNER), str(sources[0].parent), 'OUTPUT',
            '--source-frames', str(len(sources)), '--motion-scale', str(settings['scale']),
            '--rife-root', str(RIFE)]
    if settings.get('anchor_frames') is not None:
        anchor = scratch / 'anchor-frames.json'
        anchor.write_text(json.dumps(settings['anchor_frames']))
        args += ['--anchor-frames', str(anchor), '--output-fps', str(settings['output_fps']),
                 '--frame-count', str(settings['frame_count'])]
    else:
        fps = Fraction(str(settings['source_fps'])).limit_denominator(1000000)
        args += ['--source-fps', str(fps), '--multiplier', str(settings['multiplier'])]
    env = {**os.environ, 'PYTORCH_ENABLE_MPS_FALLBACK': '0'}
    with (scratch / 'render.log').open('w') as log:
        for mode in ('pair', 'full'):
            output = scratch / mode
            call = args.copy()
            call[3] = str(output)
            call += (['--pair-only'] if mode == 'pair' else
                     ['--validated-pair', str(scratch / 'pair/manifest.json')])
            subprocess.run(call, cwd=ROOT, env=env, stdout=log, stderr=subprocess.STDOUT,
                           check=True, timeout=1800)
            fresh = json.loads((output / 'manifest.json').read_text())
            if mode == 'pair' and (
                    fresh['settings'] != settings or fresh['provenance'] != record['provenance']
                    or fresh['output_frames'] != record['output_frames'][:len(fresh['output_frames'])]):
                raise ValueError('First-pair reconstruction differs; original set retained')
    verify_rows(manifest, record, fresh, output)
    return output, fresh


def remove_verified(manifest, record, selected, receipt, state):
    """Check the entire removal set before unlinking; then recheck each file."""
    for row in selected:
        checked_file(frame_path(manifest, row), row['sha256'])
    state.update(status='verified-before-removal', removed=[])
    save(receipt, state)
    with receipt.with_suffix('.deleted.jsonl').open('a') as journal:
        for row in selected:
            path = frame_path(manifest, row)
            checked_file(path, row['sha256'])
            path.unlink()
            state['removed'].append(row['file'])
            journal.write(json.dumps({'file': row['file'], 'sha256': row['sha256']}) + '\n')
            journal.flush()
            os.fsync(journal.fileno())
    state['status'] = 'retired'
    state['finished_utc'] = datetime.now(UTC).isoformat()
    save(receipt, state)


def retire(manifest, plan, receipt, apply=False):
    manifest, receipt = Path(manifest).absolute(), Path(receipt).absolute()
    if not manifest.is_relative_to(ROOT / 'projects/modern-model-study'):
        raise ValueError('Cleanup is limited to older modern-model-study sequences')
    if not receipt.is_relative_to(ROOT / 'work/storage-audit') or receipt.exists():
        raise ValueError('Expected a new private storage-audit receipt')
    checked_file(manifest, plan['manifest_sha256'])
    record = json.loads(manifest.read_text())
    if record['started_utc'] >= '2026-09-18':
        raise ValueError('Recent work is outside this cleanup')
    selected = selected_frames(manifest, record, plan['candidates'])
    if not selected:
        raise ValueError('No unprotected interpolation frames')
    dependencies(manifest, record)
    for row in record['output_frames']:
        checked_file(frame_path(manifest, row), row['sha256'])
    receipt.parent.mkdir(parents=True, exist_ok=True)
    state = {'manifest': str(manifest), 'manifest_sha256': digest(manifest),
             'original': record, 'selected': selected, 'protected': plan.get('protected', []),
             'selected_bytes': sum(frame_path(manifest, r).stat().st_size for r in selected),
             'started_utc': datetime.now(UTC).isoformat(), 'status': 'rebuilding',
             'runtime': str(RUNTIME), 'restore_module': 'deforum_lab.media.frame_retention'}
    save(receipt, state)
    try:
        with tempfile.TemporaryDirectory(prefix='rebuild-', dir=receipt.parent) as folder:
            _output, fresh = rebuild(manifest, record, Path(folder))
            # Preserve the full new provenance and every compared hash, not temporary media.
            state.update(rebuilt=fresh, status='verified', verified_frames=len(fresh['output_frames']))
            dependencies(manifest, record)
            checked_file(manifest, state['manifest_sha256'])
            save(receipt, state)
            if apply:
                remove_verified(manifest, record, selected, receipt, state)
    except Exception as error:
        state.update(status='failed', error=str(error))
        save(receipt, state)
        raise
    return {key: state[key] for key in ('status', 'manifest', 'selected_bytes', 'verified_frames')}


def restore(receipt):
    receipt = Path(receipt).absolute()
    state = json.loads(receipt.read_text())
    if state.get('kind') == 'verified-interpolation-copies':
        from .frame_copies import restore_copies
        return restore_copies(receipt, state)
    manifest = Path(state['manifest'])
    checked_file(manifest, state['manifest_sha256'])
    record = state['original']
    if json.loads(manifest.read_text()) != record:
        raise ValueError('Original manifest differs from restore receipt')
    dependencies(manifest, record)
    selected = selected_frames(manifest, record,
                               [str(frame_path(manifest, row)) for row in state['selected']])
    # Refuse changed existing media, including the anchors and other retained frames.
    for row in record['output_frames']:
        path = frame_path(manifest, row)
        if path.exists() or path.is_symlink():
            checked_file(path, row['sha256'])
        elif row not in selected:
            raise ValueError(f'Unexpected missing retained frame: {path}')
    restored = []
    with tempfile.TemporaryDirectory(prefix='restore-', dir=receipt.parent) as folder:
        output, _ = rebuild(manifest, record, Path(folder))
        for row in selected:
            target = frame_path(manifest, row)
            if not target.exists():
                # Exclusive create: never replace a concurrently created media file.
                with target.open('xb') as dest, (output / row['file']).open('rb') as source:
                    shutil.copyfileobj(source, dest)
                checked_file(target, row['sha256'])
                restored.append(row['file'])
    result = {'status': 'restored', 'manifest': str(manifest), 'frames': len(restored),
              'finished_utc': datetime.now(UTC).isoformat()}
    save(receipt.with_suffix('.restored.json'), result)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='action', required=True)
    r = sub.add_parser('restore')
    r.add_argument('receipt', type=Path)
    v = sub.add_parser('retire')
    v.add_argument('plan', type=Path)
    v.add_argument('--manifest', required=True)
    v.add_argument('--receipt', required=True, type=Path)
    v.add_argument('--apply', action='store_true')
    args = parser.parse_args()
    if args.action == 'restore':
        result = restore(args.receipt)
    else:
        plan = next(p for p in json.loads(args.plan.read_text())['plans'] if p['manifest'] == args.manifest)
        result = retire(args.manifest, plan, args.receipt, args.apply)
    print(json.dumps(result))


if __name__ == '__main__':
    main()
