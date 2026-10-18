"""Retain or restore explicitly tagged copies of already rebuilt RIFE frames."""
import json
import shutil
import tempfile
from collections import defaultdict
from datetime import UTC, datetime
from pathlib import Path

from .frame_retention import (
    ROOT,
    checked_file,
    dependencies,
    frame_path,
    rebuild,
    remove_verified,
    save,
)
from .storage import digest


def proof_index(receipts):
    index = {}
    for path in receipts:
        state = json.loads(path.read_text())
        if state.get('status') != 'retired' or 'rebuilt' not in state:
            raise ValueError('Expected a completed full-rebuild receipt')
        original, built = state['original'], state['rebuilt']
        if (built['status'] != 'complete' or built['output_frames'] != original['output_frames']
                or built['settings'] != original['settings'] or built['provenance'] != original['provenance']):
            raise ValueError('Invalid full reconstruction evidence')
        receipt_hash = digest(path)
        for row in built['output_frames']:
            if row['kind'] == 'interpolation':
                index.setdefault(row['sha256'], {'receipt': str(path), 'receipt_sha256': receipt_hash,
                                                 'file': row['file'], 'sha256': row['sha256']})
    return index


def retire_copies(manifest, candidates, proofs, receipt):
    manifest, receipt = Path(manifest).absolute(), Path(receipt).absolute()
    if not manifest.is_relative_to(ROOT / 'projects/modern-model-study'):
        raise ValueError('Copy retirement is limited to the approved older project')
    if receipt.exists() or not receipt.is_relative_to(ROOT / 'work/storage-audit'):
        raise ValueError('Expected a new storage-audit receipt')
    checked_file(manifest, digest(manifest))
    record = json.loads(manifest.read_text())
    if record.get('status') != 'complete' or record.get('mode') == 'first_pair':
        raise ValueError('Only completed deliveries, never validation pairs')
    if (record.get('started_utc', '') >= '2026-09-18'
            or datetime.fromtimestamp(manifest.stat().st_mtime, UTC).isoformat() >= '2026-09-18'):
        # The filesystem date also protects undated assembled deliveries edited recently.

        raise ValueError('Recent delivery is outside this cleanup')
    checked_file(manifest.parent / 'preview.mp4', record['video_sha256'])
    selected, mapping = [], {}
    for row in record['output_frames']:
        path = frame_path(manifest, row)
        checked_file(path, row['sha256'])
        if str(path) in candidates and row['kind'] == 'interpolation' and row['sha256'] in proofs:
            selected.append(row)
            mapping[row['file']] = proofs[row['sha256']]
    if not selected:
        return {'status': 'retained', 'manifest': str(manifest), 'reason': 'No proven unprotected copies'}
    for item in {v['receipt']: v for v in mapping.values()}.values():
        checked_file(Path(item['receipt']), item['receipt_sha256'])
        base = json.loads(Path(item['receipt']).read_text())
        dependencies(Path(base['manifest']), base['original'])
    state = {'kind': 'verified-interpolation-copies', 'manifest': str(manifest),
             'manifest_sha256': digest(manifest), 'original': record, 'selected': selected,
             'mapping': mapping, 'selected_bytes': sum(frame_path(manifest, x).stat().st_size for x in selected),
             'basis': 'Each selected PNG matches an actual full RIFE reconstruction; all other frames remain'}
    checked_file(manifest, state['manifest_sha256'])
    checked_file(manifest.parent / 'preview.mp4', record['video_sha256'])
    remove_verified(manifest, record, selected, receipt, state)
    return {'status': state['status'], 'manifest': str(manifest), 'receipt': str(receipt),
            'frames': len(selected), 'bytes': state['selected_bytes']}


def restore_copies(receipt, state):
    manifest = Path(state['manifest'])
    checked_file(manifest, state['manifest_sha256'])
    record = state['original']
    if json.loads(manifest.read_text()) != record:
        raise ValueError('Copy manifest changed')
    checked_file(manifest.parent / 'preview.mp4', record['video_sha256'])
    groups = defaultdict(list)
    selected = {r['file']: r for r in state['selected']}
    for row in record['output_frames']:
        target = frame_path(manifest, row)
        if target.exists() or target.is_symlink():
            checked_file(target, row['sha256'])
        elif row['file'] not in selected:
            raise ValueError(f'Missing retained frame: {target}')
        else:
            proof = state['mapping'][row['file']]
            if row['kind'] != 'interpolation' or proof['sha256'] != row['sha256']:
                raise ValueError('Invalid copy restoration mapping')
            groups[proof['receipt']].append((row, proof))
    restored = 0
    for base_receipt, rows in groups.items():
        checked_file(Path(base_receipt), rows[0][1]['receipt_sha256'])
        base = json.loads(Path(base_receipt).read_text())
        dependencies(Path(base['manifest']), base['original'])
        with tempfile.TemporaryDirectory(prefix='restore-copies-', dir=receipt.parent) as folder:
            output, _ = rebuild(Path(base['manifest']), base['original'], Path(folder))
            for row, proof in rows:
                source = frame_path(output / 'manifest.json', proof)
                checked_file(source, row['sha256'])
                target = frame_path(manifest, row)
                with target.open('xb') as dest, source.open('rb') as stream:
                    shutil.copyfileobj(stream, dest)
                checked_file(target, row['sha256'])
                restored += 1
    result = {'status': 'restored', 'manifest': str(manifest), 'frames': restored}
    save(receipt.with_suffix('.restored.json'), result)
    return result
