"""Archive, continuation and cut invariants without a GPU or paid requests."""

import base64
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import tempfile
import unittest
import urllib.error
from unittest.mock import patch

import editing
import experiment
import serverless_client as client

spec = importlib.util.spec_from_file_location('archive_worker', Path(__file__).parent / 'serverless/handler.py')
worker = importlib.util.module_from_spec(spec)
spec.loader.exec_module(worker)
PNG = b'\x89PNG\r\n\x1a\nexample-frame'


class ServerlessTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def test_rejected_submission_preserves_error_without_retry(self):
        project = self.root / 'film'
        (project / 'runs').mkdir(parents=True)
        deployment = self.root / 'deployment.json'
        client.save(deployment, {'endpoint_id': 'endpoint', 'volume_id': 'volume'})
        failure = urllib.error.HTTPError('https://api.runpod.ai', 409, 'Conflict', {},
                                        io.BytesIO(b'{"error":"endpoint not ready"}'))
        with patch.dict(client.os.environ, {key: 'test' for key in
                ('RUNPOD_API_KEY', 'RUNPOD_S3_ACCESS_KEY_ID', 'RUNPOD_S3_SECRET_ACCESS_KEY')}), \
             patch.object(client, 'storage'), \
             patch.object(client.urllib.request, 'urlopen', side_effect=failure) as request:
            with self.assertRaisesRegex(RuntimeError, 'HTTP 409.*endpoint not ready'):
                client.submit(project, 'test', {}, 1, deployment=deployment)
        self.assertEqual(request.call_count, 1)
        receipt = json.loads(next(project.glob('runs/*/submission-error.json')).read_text())
        self.assertIn('endpoint not ready', receipt['error'])
        self.assertFalse(list(project.glob('runs/*/submit-response.json')))

    def parent(self, name='parent', frames=40, start=0):
        folder = self.root / 'projects/film/runs' / name
        (folder / 'frames').mkdir(parents=True)
        experiment.save_json(folder / 'submission.json', {'frames': frames, 'start_frame': start,
                              'generated_fps': 8, 'collected_at': 'already'})
        experiment.save_json(folder / 'workflow.api.json', experiment.make_graph(.4, 40, 'old'))
        for i in range(frames):
            (folder / 'frames' / f'{i:04d}.png').write_bytes(PNG + str(i).encode())
        return folder

    def test_continuation_preserves_global_seed_schedule_and_parent(self):
        parent = self.parent()
        before = (parent / 'workflow.api.json').read_bytes()
        graph, image, lineage = editing.continuation(parent, 19, 8)
        self.assertEqual((lineage['start_frame'], lineage['end_frame'], lineage['frames']), (19, 28, 9))
        self.assertEqual(graph['7']['inputs']['max_frames'], 40)
        self.assertEqual(graph['7']['inputs']['seed'], 21)
        self.assertEqual(graph['10']['inputs']['start_frame'], 19)
        self.assertEqual(lineage['parent_sha256'], hashlib.sha256(image.read_bytes()).hexdigest())
        self.assertEqual((parent / 'workflow.api.json').read_bytes(), before)
        nested = self.parent('branch', 9, 19)
        self.assertEqual(editing.continuation(nested, 7, 8)[2]['start_frame'], 26)
        with self.assertRaises(ValueError):
            editing.continuation(parent, 40, 8)

    def archived(self, fail=False):
        root = self.root / 'volume/deforum'
        job = {'id': 'job-one', 'input': {'project': 'film', 'run': 'run-one',
               'workflow': experiment.make_graph(.4, 1, 'old'), 'expected_frames': 1}}
        def render(request):
            prefix = request['input']['workflow']['11']['inputs']['filename_prefix']
            path = root / (prefix + '_00001_.png')
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(PNG)
            return {'error': 'test failure'} if fail else {'images': [{'type': 'base64', 'data': base64.b64encode(PNG).decode()}]}
        result = worker.archive_job(job, render, root)
        return root, result

    def test_retries_have_distinct_durable_attempts_and_small_results(self):
        root, first = self.archived()
        _, second = self.archived()
        self.assertNotEqual(first['attempt'], second['attempt'])
        self.assertNotIn('images', first)
        self.assertEqual(len(list(root.rglob('manifest.json'))), 2)
        self.assertTrue(all(p.stat().st_size for p in root.rglob('*.png')))

    def test_failed_attempt_preserves_partial_frames_and_manifest(self):
        root, result = self.archived(fail=True)
        self.assertIn('error', result)
        self.assertEqual(len(list(root.rglob('*.png'))), 1)
        self.assertEqual(json.loads(next(root.rglob('manifest.json')).read_text())['error'], 'test failure')

    def test_completed_volume_archive_recovers_without_live_job_api(self):
        root, result = self.archived()
        class FakeS3:
            def get_object(self, Bucket, Key):
                return {'Body': io.BytesIO((root.parent / Key).read_bytes())}
        folder = self.root / 'local'
        folder.mkdir()
        client.save(folder / 'submission.json', {'transport': 'runpod-serverless',
                    'project': 'film', 'run': 'run-one', 'frames': 1,
                    'deployment': {'volume_id': 'volume'}})
        with patch.object(client, 'storage', return_value=FakeS3()), \
             patch.object(client, 'manifest_keys', return_value=[result['manifest_key']]), \
             patch.object(client, 'api', side_effect=AssertionError('Expired job must not be needed')), \
             patch.object(editing, 'encode', side_effect=lambda frames, target: target.write_bytes(b'video')):
            client.collect(folder)
        self.assertEqual((folder / 'frames/0000.png').read_bytes(), PNG)
        before = {p: (p.read_bytes(), p.stat().st_mtime_ns) for p in folder.rglob('*') if p.is_file()}
        with patch.object(client, 'storage', side_effect=AssertionError('Completed archive must work offline')):
            client.collect(folder)
        self.assertEqual(before, {p: (p.read_bytes(), p.stat().st_mtime_ns) for p in before})

    def test_corrupt_cloud_frame_is_rejected(self):
        root, result = self.archived()
        next(root.rglob('*.png')).write_bytes(b'corrupt')
        class FakeS3:
            def get_object(self, Bucket, Key):
                return {'Body': io.BytesIO((root.parent / Key).read_bytes())}
        with self.assertRaisesRegex(ValueError, 'checksum'):
            client.download_attempt(FakeS3(), {'volume_id': 'volume'}, result['manifest_key'], self.root / 'local')

    def test_cut_has_no_duplicate_anchor_and_never_overwrites_an_old_cut(self):
        parent, branch = self.parent(), self.parent('branch', 9, 19)
        project = parent.parent.parent
        (project / 'cuts').mkdir()
        ranges = [{'run': 'parent', 'in': 0, 'out': 20}, {'run': 'branch', 'in': 1, 'out': 9}]
        with patch.object(editing, 'encode', side_effect=lambda frames, target: target.write_bytes(b'video')):
            export = editing.assemble(project, 'v001', ranges)
            self.assertEqual(len(list((export / 'frames').glob('*.png'))), 28)
            self.assertEqual((export / 'frames/0019.png').read_bytes(), (parent / 'frames/0019.png').read_bytes())
            self.assertEqual((export / 'frames/0020.png').read_bytes(), (branch / 'frames/0001.png').read_bytes())
            with self.assertRaises(FileExistsError):
                editing.assemble(project, 'v001', ranges)

    def test_archive_components_reject_escape(self):
        for value in ('../outside', '/tmp', '.', '', 'run/another'):
            with self.assertRaises(ValueError):
                worker.component(value)


if __name__ == '__main__':
    unittest.main()
