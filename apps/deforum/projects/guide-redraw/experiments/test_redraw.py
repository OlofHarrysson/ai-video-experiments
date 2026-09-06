"""Offline checks for image ordering, preserved lineage and submission boundaries."""

import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from PIL import Image

import redraw


class RedrawTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(dir=redraw.PROJECT / 'references' / 'assets')
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.project = self.root / 'redraw'
        (self.project / 'references' / 'assets').mkdir(parents=True)
        self.guide = self.root / 'guide'
        (self.guide / 'frames').mkdir(parents=True)
        self.parent = {
            '1': {'class_type': 'CheckpointLoaderSimple', 'inputs': {'ckpt_name': 'sd_xl_base_1.0.safetensors'}},
            '2': {'class_type': 'CLIPTextEncode', 'inputs': {'text': redraw.PROMPT, 'clip': ['1', 1]}},
            '3': {'class_type': 'CLIPTextEncode', 'inputs': {'text': 'test negative', 'clip': ['1', 1]}},
            '7': {'class_type': 'DifforumAnimSetup', 'inputs': {'seed': 143}},
            '10': {'class_type': 'DifforumGuideBuilder', 'inputs': {}}}
        redraw.write_json(self.guide / 'workflow.api.json', self.parent)
        redraw.write_json(self.guide / 'submission.json', {
            'project': 'lantern-marsh', 'phase': 'guide', 'collected_at': 'test', 'frames': 12})
        for i in range(12):
            im = Image.new('RGB', (64, 32))
            im.putdata([(i * 17, x % 256, (x * 13) % 256) for x in range(64 * 32)])
            im.save(self.guide / 'frames' / f'{i:04d}.png')
        self.addCleanup(patch.stopall)
        patch.object(redraw, 'PROJECT', self.project).start()

    def test_strip_graph_and_global_order(self):
        bundle = redraw.prepare(self.guide, start=3)
        graph = json.loads((bundle / 'workflow.api.json').read_text())
        lineage = json.loads((bundle / 'lineage.json').read_text())
        self.assertEqual([x['guide_frame'] for x in lineage['frame_map']], list(range(3, 11)))
        with Image.open(bundle / 'anchor.png') as strip:
            for i, row in enumerate(lineage['frame_map']):
                with Image.open(self.guide / 'frames' / f'{i+3:04d}.png') as original:
                    self.assertEqual(strip.crop((64*i, 0, 64*(i+1), 32)).tobytes(), original.tobytes())
                self.assertEqual(redraw.digest(bundle / row['local']), row['sha256'])

        def outputs(link):
            node = graph[link[0]]
            if node['class_type'] == 'ImageBatch':
                return outputs(node['inputs']['image1']) + outputs(node['inputs']['image2'])
            self.assertEqual(node['class_type'], 'VAEDecode')
            sample = graph[node['inputs']['samples'][0]]['inputs']
            encode = graph[sample['latent_image'][0]]
            crop = graph[encode['inputs']['pixels'][0]]
            self.assertEqual(encode['class_type'], 'VAEEncode')
            self.assertEqual(crop['inputs']['image'], ['6', 0])
            self.assertEqual((sample['steps'], sample['cfg'], sample['denoise']), (28, 6.5, .4))
            return [(crop['inputs']['x'], sample['seed'])]

        self.assertEqual(outputs(graph['11']['inputs']['images']), [(i*64, 146+i) for i in range(8)])
        self.assertEqual([n['class_type'] for n in graph.values()].count('SaveImage'), 1)

    def test_reject_incomplete_and_non_rgb_guides(self):
        with self.assertRaises(ValueError):
            redraw.prepare(self.guide, start=5)
        Image.new('RGBA', (64, 32)).save(self.guide / 'frames' / '0000.png')
        with self.assertRaises(ValueError):
            redraw.prepare(self.guide)

    def test_submission_is_shared_and_never_retried(self):
        bundle = redraw.prepare(self.guide)
        with patch.object(redraw.serverless_client, 'submit', side_effect=TimeoutError('uncertain')) as remote:
            with self.assertRaises(TimeoutError):
                redraw.submit(bundle)
            args, kwargs = remote.call_args
            self.assertEqual(args[:2], (self.project, 'independent-redraw'))
            self.assertEqual(args[3], 8)
            self.assertEqual(kwargs['source'], bundle / 'anchor.png')
            with self.assertRaises(FileExistsError):
                redraw.submit(bundle)
            remote.assert_called_once()

    def test_modified_bundle_never_submits(self):
        bundle = redraw.prepare(self.guide)
        (bundle / 'anchor.png').write_bytes(b'changed')
        with patch.object(redraw.serverless_client, 'submit') as remote:
            with self.assertRaises(ValueError):
                redraw.submit(bundle)
            remote.assert_not_called()


if __name__ == '__main__':
    unittest.main()
