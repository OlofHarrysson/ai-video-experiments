"""Offline isolation, resume and submission safety checks for the shared package."""

import copy
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import numpy as np
from PIL import Image

from deforum_lab.infrastructure.pod import PodClient
from deforum_lab.records import read, save, sha
from deforum_lab.rendering.feedback import render_paintings
from deforum_lab.rendering.schedules import SIGMAS, recipe


class LocalClient:
    def __init__(self):
        self.calls = []

    def submit_once(self, output, name, graph, source, lineage):
        self.calls.append((output, name, graph, lineage))
        run = output / "runs" / name
        (run / "frames").mkdir(parents=True)
        (run / "anchor.png").write_bytes(source.read_bytes())
        with Image.open(source) as im:
            pixels = np.array(im)
        # A deterministic stand-in response makes successive parent use observable.
        pixels[0, 0] = [len(self.calls), 0, 0]
        Image.fromarray(pixels).save(run / "frames/0000.png")
        save(run / "workflow.api.json", graph)
        return run


class PackageTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.config = {
            "case": "test",
            "seed": 71,
            "cadence": 12,
            "scenes": [{"at": 0, "name": "city", "prompt": "a city"}],
            "noise_schedule": [{"at": 0, "noise": 0.1}],
            "phrases": [],
        }

    def opening(self, output):
        folder = output / "test/anchors"
        folder.mkdir(parents=True)
        Image.fromarray(np.full((16, 24, 3), 127, dtype=np.uint8)).save(
            folder / "0000.png"
        )

    def run_frames(self, output, client, config=None):
        render_paintings(
            config or self.config,
            output,
            client,
            first_frame=12,
            last_frame=24,
            run_prefix="test",
            filename_prefix="test",
        )

    def test_recurrence_resume_and_config_rejection(self):
        output = self.root / "one"
        self.opening(output)
        client = LocalClient()
        self.run_frames(output, client)
        self.assertEqual(len(client.calls), 2)
        self.assertEqual(
            client.calls[1][3]["parent_sha256"], sha(output / "test/anchors/0012.png")
        )
        with Image.open(output / "test/warped-inputs/0024.png") as im:
            self.assertEqual(tuple(np.array(im)[0, 0]), (1, 0, 0))
        self.run_frames(output, client)
        self.assertEqual(len(client.calls), 2)
        changed = {**self.config, "noise_schedule": [{"at": 0, "noise": 0.6}]}
        with self.assertRaisesRegex(ValueError, "Saved record differs"):
            self.run_frames(output, client, changed)
        self.assertEqual(len(client.calls), 2)

    def test_resume_detects_changed_output(self):
        self.opening(self.root)
        client = LocalClient()
        self.run_frames(self.root, client)
        (self.root / "test/anchors/0012.png").write_bytes(b"changed")
        with self.assertRaisesRegex(ValueError, "output differs"):
            self.run_frames(self.root, client)
        self.assertEqual(len(client.calls), 2)

    def test_irregular_paintings_use_actual_parent_time_and_seed(self):
        self.opening(self.root)
        client = LocalClient()
        config = {
            **self.config,
            "painting_frames": [0, 12, 18, 24],
            "seeds_by_frame": {"12": 72, "18": 999, "24": 73},
        }
        with patch(
            "deforum_lab.rendering.feedback.warp_at_time",
            side_effect=lambda pixels, start, end, phrases: pixels,
        ) as warp:
            self.run_frames(self.root, client, config)
        self.assertEqual(
            [(x.args[1], x.args[2]) for x in warp.call_args_list],
            [(0, 0.5), (0.5, 0.75), (0.75, 1)],
        )
        self.assertEqual(
            client.calls[-1][3]["parent_sha256"],
            sha(self.root / "test/anchors/0018.png"),
        )
        self.assertEqual(read(self.root / "test/anchor-0018.json")["seed"], 999)
        self.run_frames(self.root, client, config)
        self.assertEqual(len(client.calls), 3)

    def test_outputs_and_deployments_are_isolated(self):
        deployment = {"base_url": "http://first.invalid", "pod_id": "one"}
        first = PodClient(deployment)
        second = PodClient({"base_url": "http://second.invalid", "pod_id": "two"})
        deployment["base_url"] = "http://changed.invalid"
        self.assertEqual(first.deployment["base_url"], "http://first.invalid")
        self.assertEqual(second.deployment["pod_id"], "two")
        original_config = copy.deepcopy(self.config)
        clients = [LocalClient(), LocalClient()]
        for name, client in zip(("one", "two"), clients):
            output = self.root / name
            self.opening(output)
            self.run_frames(output, client)
            self.assertTrue(all(row[0] == output for row in client.calls))
        self.assertEqual(self.config, original_config)
        self.assertEqual(
            sha(self.root / "one/test/anchors/0024.png"),
            sha(self.root / "two/test/anchors/0024.png"),
        )

    def test_sigma_placement_preserves_noise_and_recurrent_initialization(self):
        self.opening(self.root)
        client = LocalClient()
        config = {**self.config, "sigma_ratios": [1, 2 / 3, 1 / 3, 0]}
        self.run_frames(self.root, client, config)
        graph = client.calls[0][2]
        self.assertEqual(graph["9"]["inputs"]["latent_image"], ["24", 0])
        self.assertEqual(graph["24"]["inputs"]["pixels"], ["20", 0])
        actual = [float(x) for x in graph["43"]["inputs"]["sigmas"].split(",")]
        np.testing.assert_allclose(actual, [0.1, 0.1 * 2 / 3, 0.1 / 3, 0], atol=1e-12)
        self.assertEqual(
            read(self.root / "test/anchor-0024.json")["parent_sha256"],
            sha(self.root / "test/anchors/0012.png"),
        )
        self.assertEqual(recipe(self.config, 1)[1], [s * 0.1 / 0.6 for s in SIGMAS])

    def test_invalid_sigma_placement_fails_before_inference(self):
        for ratios in (
            [1, 0.5, 0.7, 0],
            [0.8, 0.5, 0],
            [1, 0.5],
            [1, float("nan"), 0],
            [1, 1, 0],
        ):
            with (
                self.subTest(ratios=ratios),
                self.assertRaisesRegex(ValueError, "Sigma ratios"),
            ):
                recipe({**self.config, "sigma_ratios": ratios}, 1)

    def test_graph_transform_keeps_recurrence_and_resume_checks(self):
        self.opening(self.root)
        client = LocalClient()

        def transform(graph, config, seconds):
            graph["9"]["inputs"]["cfg"] = 1.3 if seconds < 1 else 1.0

        args = {
            "first_frame": 12,
            "last_frame": 24,
            "run_prefix": "test",
            "filename_prefix": "test",
            "graph_transform": transform,
        }
        render_paintings(self.config, self.root, client, **args)
        self.assertEqual([r[2]["9"]["inputs"]["cfg"] for r in client.calls], [1.3, 1.0])
        self.assertTrue(
            all(r[2]["9"]["inputs"]["latent_image"] == ["24", 0] for r in client.calls)
        )
        self.assertEqual(
            client.calls[1][3]["parent_sha256"],
            sha(self.root / "test/anchors/0012.png"),
        )
        render_paintings(self.config, self.root, client, **args)
        self.assertEqual(len(client.calls), 2)
        with self.assertRaisesRegex(ValueError, "Saved painting graph differs"):
            self.run_frames(self.root, client)
        self.assertEqual(len(client.calls), 2)

    def test_uncertain_submission_never_resubmits(self):
        client = PodClient({"base_url": "http://unused.invalid", "pod_id": "test"})
        graph = {"11": {"class_type": "SaveImage", "inputs": {}}}
        with patch(
            "deforum_lab.infrastructure.pod.request",
            side_effect=[{}, TimeoutError("connection lost")],
        ) as request:
            with self.assertRaises(TimeoutError):
                client.submit_once(self.root, "probe", graph)
            with self.assertRaisesRegex(ValueError, "Uncertain submission"):
                client.submit_once(self.root, "probe", graph)
            self.assertEqual(request.call_count, 2)
        run = next((self.root / "runs").iterdir())
        self.assertTrue((run / "submission-error.json").exists())

    def test_accepted_submission_resumes_collection_without_resubmission(self):
        client = PodClient({"base_url": "http://unused.invalid", "pod_id": "test"})
        graph = {"11": {"class_type": "SaveImage", "inputs": {}}}
        run = self.root / "runs/saved-probe-1f"
        save(run / "workflow.api.json", graph)
        save(
            run / "submission.json",
            {"prompt_id": "accepted", "parent_sha256": "parent"},
        )
        with (
            patch("deforum_lab.infrastructure.pod.request") as request,
            patch("deforum_lab.infrastructure.pod.collect") as collect,
        ):
            actual = client.submit_once(
                self.root, "probe", graph, lineage={"parent_sha256": "parent"}
            )
            self.assertEqual(actual, run)
            collect.assert_called_once_with(run)
            request.assert_not_called()
        self.assertEqual(read(run / "submission.json")["prompt_id"], "accepted")


if __name__ == "__main__":
    unittest.main()
