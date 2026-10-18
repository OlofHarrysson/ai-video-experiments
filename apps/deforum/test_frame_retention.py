import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from deforum_lab.media import frame_retention as retention
from deforum_lab.media.storage import digest


class FrameRetentionTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name).resolve()
        self.manifest = self.root / 'manifest.json'
        (self.root / 'frames').mkdir()
        self.rows = []
        for index, kind in enumerate(('anchor', 'interpolation', 'interpolation', 'final_hold')):
            path = self.root / 'frames' / f'{index:04d}.png'
            path.write_bytes(f'image{index}'.encode())
            self.rows.append({'file': f'frames/{index:04d}.png', 'kind': kind, 'sha256': digest(path)})
        self.record = {'output_frames': self.rows}
        self.manifest.write_text(json.dumps(self.record))
        self.receipt = self.root / 'receipt.json'

    def test_originals_unknown_paths_and_duplicate_selection_rejected(self):
        for names in ([self.root / self.rows[0]['file']], [self.root / '../other.png'],
                      [self.root / self.rows[1]['file']] * 2):
            with self.assertRaises(ValueError):
                retention.selected_frames(self.manifest, self.record, list(map(str, names)))
        with self.assertRaises(ValueError):
            retention.frame_path(self.manifest, {'file': '../source.png'})

    def test_any_mismatch_prevents_all_removals(self):
        (self.root / self.rows[2]['file']).write_bytes(b'changed')
        with self.assertRaises(ValueError):
            retention.remove_verified(self.manifest, self.record, self.rows[1:3], self.receipt, {})
        self.assertTrue((self.root / self.rows[1]['file']).exists())

    def test_symlink_refused(self):
        p = self.root / self.rows[1]['file']
        p.unlink()
        p.symlink_to(self.root / self.rows[0]['file'])
        with self.assertRaises(ValueError):
            retention.checked_file(p, self.rows[0]['sha256'])

    def test_remove_restore_round_trip_preserves_other_frames(self):
        original = {r['file']: (self.root / r['file']).read_bytes() for r in self.rows}
        state = {'manifest': str(self.manifest), 'manifest_sha256': digest(self.manifest),
                 'original': self.record, 'selected': self.rows[1:2]}
        retention.remove_verified(self.manifest, self.record, self.rows[1:2], self.receipt, state)
        self.assertFalse((self.root / self.rows[1]['file']).exists())
        self.assertTrue((self.root / self.rows[2]['file']).exists())
        def rebuild(manifest, record, scratch):
            (scratch / 'frames').mkdir()
            for name, data in original.items():
                (scratch / name).write_bytes(data)
            return scratch, record
        with patch.object(retention, 'dependencies'), patch.object(retention, 'rebuild', rebuild):
            self.assertEqual(retention.restore(self.receipt)['frames'], 1)
        for name, data in original.items():
            self.assertEqual((self.root / name).read_bytes(), data)

    def test_restore_refuses_modified_existing_media(self):
        state = {'manifest': str(self.manifest), 'manifest_sha256': digest(self.manifest),
                 'original': self.record, 'selected': self.rows[1:2]}
        retention.save(self.receipt, state)
        (self.root / self.rows[0]['file']).write_bytes(b'edited painting')
        with patch.object(retention, 'dependencies'), patch.object(retention, 'rebuild') as render:
            with self.assertRaises(ValueError):
                retention.restore(self.receipt)
            render.assert_not_called()

class FrameCopyRetentionTest(unittest.TestCase):
    def test_copy_round_trip_uses_proven_frame_and_keeps_unique_tail(self):
        import os

        from deforum_lab.media import frame_copies as copies
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder).resolve()
            target = root / 'projects/modern-model-study/old/rife-moving-tail'
            target.mkdir(parents=True)
            (target / 'frames').mkdir()
            rows = []
            for index, kind in enumerate(('anchor', 'interpolation', 'warp')):
                p = target / 'frames' / f'{index:04d}.png'
                p.write_bytes(f'image{index}'.encode())
                rows.append({'file': str(p.relative_to(target)), 'kind': kind, 'sha256': digest(p)})
            (target / 'preview.mp4').write_bytes(b'video')
            m = target / 'manifest.json'
            original = {'status': 'complete', 'output_frames': rows, 'video_sha256': digest(target / 'preview.mp4')}
            m.write_text(json.dumps(original))
            os.utime(m, (1700000000, 1700000000))
            audit = root / 'work/storage-audit'
            audit.mkdir(parents=True)
            base = audit / 'base.json'
            base_record = {'output_frames': rows, 'settings': {}, 'provenance': {}}
            base.write_text(json.dumps({'status': 'retired', 'manifest': str(root / 'base/manifest.json'),
                                        'original': base_record, 'rebuilt': {**base_record, 'status': 'complete'}}))
            index = copies.proof_index([base])
            receipt = audit / 'copies.json'
            with patch.object(copies, 'ROOT', root), patch.object(copies, 'dependencies'):
                result = copies.retire_copies(m, [str(target / rows[1]['file'])], index, receipt)
            self.assertEqual(result['frames'], 1)
            self.assertFalse((target / rows[1]['file']).exists())
            self.assertTrue((target / rows[2]['file']).exists())
            def rebuild(manifest, record, scratch):
                (scratch / 'frames').mkdir()
                (scratch / rows[1]['file']).write_bytes(b'image1')
                return scratch, record
            with patch.object(copies, 'dependencies'), patch.object(copies, 'rebuild', rebuild):
                self.assertEqual(retention.restore(receipt)['frames'], 1)
            self.assertEqual((target / rows[1]['file']).read_bytes(), b'image1')
            self.assertEqual((target / rows[2]['file']).read_bytes(), b'image2')
            state = json.loads(base.read_text())
            state['rebuilt']['output_frames'] = []
            base.write_text(json.dumps(state))
            with self.assertRaises(ValueError):
                copies.proof_index([base])


if __name__ == '__main__':
    unittest.main()
