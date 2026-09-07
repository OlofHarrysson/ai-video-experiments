"""Local integration tests; synthetic media only, no network or paid inference."""

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from PIL import Image

import video_review as vr


class VideoReviewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory()
        cls.root = Path(cls.temp.name)
        cls.cut = cls.root / 'cut.mkv'
        cls.vfr = cls.root / 'vfr.mkv'
        vr.command(['ffmpeg', '-v', 'error', '-n',
                    '-f', 'lavfi', '-i', 'color=black:s=64x48:r=10:d=0.5',
                    '-f', 'lavfi', '-i', 'color=white:s=64x48:r=10:d=0.5',
                    '-filter_complex', '[0:v][1:v]concat=n=2:v=1:a=0[out]',
                    '-map', '[out]', '-c:v', 'ffv1', str(cls.cut)])
        # Irregular intervals and a nonzero start PTS catch FPS arithmetic and origin mistakes.
        vr.command(['ffmpeg', '-v', 'error', '-n', '-f', 'lavfi', '-i',
                    'testsrc2=s=64x48:r=10:d=0.6', '-vf',
                    r'setpts=if(lt(N\,2)\,N\,2+(N-2)*3)+20',
                    '-fps_mode', 'vfr', '-c:v', 'ffv1', str(cls.vfr)])

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def read_review(self, source, **kwargs):
        target = vr.review(source, **kwargs)
        return target, json.loads((target / 'review.json').read_text())

    def test_vfr_timestamp_selects_displayed_frame_and_exact_pixels(self):
        target, data = self.read_review(self.vfr, overview=0, times=[.45, .51])
        rows = data['frames']
        self.assertEqual([r['frame_number'] for r in rows], [2, 3])
        self.assertEqual([r['time_seconds'] for r in rows], [.2, .5])
        self.assertEqual([r['pts_seconds'] for r in rows], [2.2, 2.5])
        # Decode the entire source independently, then compare the selected pixels by index.
        raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', str(self.vfr),
                              '-map', '0:v:0', '-fps_mode', 'passthrough',
                              '-pix_fmt', 'rgb24', '-f', 'rawvideo', '-'],
                             check=True, capture_output=True).stdout
        frame_bytes = 64 * 48 * 3
        for row in rows:
            index = row['frame_number']
            with Image.open(target / row['file']) as im:
                self.assertEqual(im.size, (64, 48))
                self.assertEqual(im.convert('RGB').tobytes(),
                                 raw[index * frame_bytes:(index + 1) * frame_bytes])

    def test_scene_cut_and_context(self):
        _, data = self.read_review(self.cut, overview=0, scene_threshold=.3,
                                   before=.1, after=.1)
        scenes = data['scene_detection']
        self.assertEqual(scenes['candidate_count'], 1)
        self.assertEqual(scenes['selected'][0]['frame_number'], 5)
        self.assertEqual([r['frame_number'] for r in data['frames']], [4, 5, 6])
        self.assertIn('not semantic', scenes['method'])

    def test_clamping_named_events_and_deduplication(self):
        _, data = self.read_review(self.cut, overview=0, times=[-5, 999],
                                   events=[('reveal', 0)], before=.25, after=.25)
        self.assertEqual([r['frame_number'] for r in data['frames']], [0, 2, 9])
        requests = data['frames'][0]['requests']
        self.assertTrue(any(r['was_clamped'] for r in requests))
        self.assertTrue(any(r['reason'] == 'event: reveal' for r in requests))

    def test_source_and_previous_review_immutable(self):
        before = (vr.sha256(self.cut), self.cut.stat().st_mtime_ns)
        output = self.root / 'versions'
        first, _ = self.read_review(self.cut, output_root=output, overview=3)
        prior = {p.relative_to(first): vr.sha256(p) for p in first.rglob('*') if p.is_file()}
        second, _ = self.read_review(self.cut, output_root=output, overview=3)
        self.assertEqual(first.name, 'v001')
        self.assertEqual(second.name, 'v002')
        self.assertEqual(before, (vr.sha256(self.cut), self.cut.stat().st_mtime_ns))
        self.assertEqual(prior, {p.relative_to(first): vr.sha256(p)
                                 for p in first.rglob('*') if p.is_file()})
        with Image.open(first / 'contact-sheet.jpg') as sheet:
            self.assertEqual(sheet.size, (1152, 286))

    def test_timestamp_and_argument_validation(self):
        self.assertEqual(vr.timestamp('01:02.5'), 62.5)
        self.assertEqual(vr.timestamp('1:02:03'), 3723)
        for value in ['nan', 'inf', '1:61', '1:2:3:4']:
            with self.assertRaises(ValueError):
                vr.timestamp(value)
        for kwargs in [{'before': -1}, {'times': [float('nan')]},
                       {'scene_threshold': 1.1}, {'overview': -1},
                       {'overview': 0}, {'columns': 0}]:
            with self.assertRaises(ValueError):
                vr.review(self.cut, **kwargs)

    def test_cli_six_frame_strip(self):
        output = vr.command([sys.executable, str(Path(vr.__file__)), str(self.cut),
                             '--overview', '6', '--columns', '6',
                             '--output-root', str(self.root / 'cli-review')])
        receipt = json.loads(output)
        metadata = json.loads(Path(receipt['metadata']).read_text())
        self.assertEqual(len(metadata['frames']), 6)
        with Image.open(receipt['contact_sheet']) as sheet:
            self.assertEqual(sheet.size, (2304, 286))

    def test_window_includes_every_displayed_vfr_frame(self):
        _, data = self.read_review(self.vfr, overview=0, windows=[(.15, .85)])
        self.assertEqual([r['frame_number'] for r in data['frames']], [1, 2, 3, 4])
        self.assertEqual([r['time_seconds'] for r in data['frames']], [.1, .2, .5, .8])
        self.assertEqual(data['frames'][0]['requests'][0]['requested_seconds'], .15)
        self.assertEqual(data['frames'][-1]['requests'][-1]['requested_seconds'], .85)

    def test_window_budget_fails_before_creating_review(self):
        output = self.root / 'too-many-images'
        with self.assertRaisesRegex(ValueError, 'exceeding --max-frames'):
            vr.review(self.cut, output_root=output, overview=0, windows=[(0, 1)], max_frames=4)
        self.assertFalse(output.exists())
        for windows in [[(.8, .2)], [(0, float('nan'))]]:
            with self.assertRaises(ValueError):
                vr.review(self.cut, output_root=output, overview=0, windows=windows)
        self.assertFalse(output.exists())

    def test_pages_cover_selection_once_without_oversized_sheet(self):
        target, data = self.read_review(self.cut, overview=0, windows=[(0, 1)], page_size=4, columns=2)
        pages = data['contact_sheets']
        self.assertEqual([p['displayed_images'] for p in pages], [4, 4, 2])
        self.assertEqual([r['frame_number'] for page in pages for r in page['frames']], list(range(10)))
        for page in pages:
            with Image.open(target / page['file']) as sheet:
                self.assertLessEqual(sheet.height, 572)

    def test_comparison_uses_elapsed_pts_and_reuses_held_frames(self):
        # Same 1.2-second display extent, different frame spacing and source start PTS.
        regular = self.root / 'regular.mkv'
        vr.command(['ffmpeg', '-v', 'error', '-n', '-f', 'lavfi', '-i',
                    'testsrc2=s=64x48:r=10:d=1.2', '-c:v', 'ffv1', str(regular)])
        target, data = self.read_review(regular, overview=0, times=[.3, .4, .5],
                                        compare=self.vfr, label='new', compare_label='old', page_size=4)
        a, b = data['frames'], data['comparison']['frames']
        self.assertEqual([r['frame_number'] for r in a], [3, 4, 5])
        self.assertEqual([r['frame_number'] for r in b], [2, 2, 3])
        self.assertEqual([r['pts_seconds'] for r in b], [2.2, 2.2, 2.5])
        self.assertEqual([r['comparison_time_seconds'] for r in b], [.3, .4, .5])
        self.assertEqual(b[0]['file'], b[1]['file'])
        self.assertEqual(len(list((target / 'comparison-frames').glob('*.png'))), 2)
        self.assertEqual([r['source'] for p in data['contact_sheets'] for r in p['frames']],
                         ['new', 'old'] * 3)
        self.assertTrue(data['comparison']['source_unchanged'])
        with self.assertRaisesRegex(ValueError, 'exceeding --max-frames'):
            vr.review(self.cut, overview=3, compare=self.cut, max_frames=5)

    def test_matching_manifest_labels_intermediate_and_original_frames(self):
        # Isolate a matching manifest next to a copied video; source video bytes are unchanged.
        folder = self.root / 'provenance'
        folder.mkdir()
        video = folder / 'clip.mkv'
        video.write_bytes(self.cut.read_bytes())
        frames = vr.probe(video)['frames']
        output = [{'index': f['frame_number'], 'time_seconds': f['time_seconds'],
                   'kind': 'anchor', 'source_index': f['frame_number']} for f in frames]
        output[1] = {'index': 1, 'time_seconds': .1, 'kind': 'interpolation',
                     'source_pair': [0, 1], 'timestep': '1/3'}
        manifest = {'status': 'complete', 'video_sha256': vr.sha256(video), 'output_frames': output}
        path = folder / 'manifest.json'
        path.write_text(json.dumps(manifest))
        _, data = self.read_review(video, overview=0, times=[0, .1])
        self.assertEqual(data['provenance']['status'], 'verified')
        self.assertEqual([r['provenance']['kind'] for r in data['frames']], ['anchor', 'interpolation'])
        manifest['video_sha256'] = 'stale'
        path.write_text(json.dumps(manifest))
        _, stale = self.read_review(video, overview=0, times=[0])
        self.assertEqual(stale['provenance']['status'], 'unverified')
        self.assertNotIn('provenance', stale['frames'][0])
        manifest['video_sha256'] = vr.sha256(video)
        manifest['output_frames'][1]['time_seconds'] = .11
        path.write_text(json.dumps(manifest))
        with self.assertRaisesRegex(ValueError, 'timeline disagrees'):
            vr.review(video)

    def test_candidate_spacing_preserves_strongest_separated_changes(self):
        scores = [0, .01, .4, .8, .7, .02, .01, .5, .9, .3]
        output = '\n'.join(f'frame:{i}\nlavfi.scene_score={value}' for i, value in enumerate(scores))
        with patch.object(vr, 'command', return_value=output):
            result = vr.detect_scenes(self.cut, 10, .2, 3,
                                       timeline=[i / 10 for i in range(10)], min_gap=.3)
        self.assertEqual([r['frame_number'] for r in result['selected']], [3, 8])

    def test_cli_window_and_comparison_pages(self):
        output = vr.command([sys.executable, str(Path(vr.__file__)), str(self.cut),
                             '--overview', '0', '--window', '0.3', '0.5',
                             '--compare', str(self.cut), '--label', 'reference', '--compare-label', 'candidate',
                             '--page-size', '4', '--output-root', str(self.root / 'cli-window')])
        result = json.loads(output)
        self.assertEqual(len(result['contact_sheets']), 2)
        data = json.loads(Path(result['metadata']).read_text())
        self.assertEqual([r['frame_number'] for r in data['frames']], [3, 4, 5])


if __name__ == '__main__':
    unittest.main()
