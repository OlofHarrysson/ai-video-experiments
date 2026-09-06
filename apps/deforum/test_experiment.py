"""Local archive/scoping checks. No GPU, API key or server is used."""

import argparse
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import experiment


class ProjectArchiveTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.override = patch.object(experiment, "PROJECTS", self.root / "projects")
        self.override.start()
        self.addCleanup(self.override.stop)

    def test_project_creation_preserves_existing_work_and_rejects_path_escape(self):
        experiment.init_project("test-film")
        folder = experiment.PROJECTS / "test-film"
        note = folder / "experiments/baseline.md"
        note.write_text("My creative decisions")
        with self.assertRaises(FileExistsError):
            experiment.init_project("test-film")
        self.assertEqual(note.read_text(), "My creative decisions")
        with self.assertRaises(argparse.ArgumentTypeError):
            experiment.init_project("../outside")
        with self.assertRaises(ValueError):
            experiment.project_for_run("test-film", "unwritten")

    def test_attempts_are_distinct_and_receipts_identify_project_and_experiment(self):
        experiment.init_project("test-film")
        args = ["experiment.py", "run", "--project", "test-film", "--experiment", "baseline",
                "--url", "https://example.invalid", "--frames", "8"]
        with patch("sys.argv", args), patch.object(experiment, "preflight", return_value={}), \
                patch.object(experiment, "request", side_effect=[{"prompt_id": "one"}, {"prompt_id": "two"}]), \
                patch.object(experiment, "collect"):
            experiment.main()
            experiment.main()
        folders = [p for p in (experiment.PROJECTS / "test-film/runs").iterdir() if p.is_dir()]
        self.assertEqual(len(folders), 2)
        receipts = [json.loads((p / "submission.json").read_text()) for p in folders]
        self.assertEqual({r["prompt_id"] for r in receipts}, {"one", "two"})
        self.assertTrue(all(r["project"] == "test-film" and r["experiment"] == "baseline" for r in receipts))
        self.assertTrue(all((p / "workflow.api.json").is_file() for p in folders))

    def test_completed_legacy_run_is_read_only_and_available_offline(self):
        folder = self.root / "old-output"
        (folder / "frames").mkdir(parents=True)
        # The old receipt has no project fields. Completed collection must not need the deleted Pod.
        experiment.save_json(folder / "submission.json", {"frames": 1, "collected_at": "earlier"})
        (folder / "frames/0000.png").write_bytes(b"preserved source")
        (folder / "preview.mp4").write_bytes(b"preserved preview")
        before = {p: (p.read_bytes(), p.stat().st_mtime_ns) for p in folder.rglob("*") if p.is_file()}
        with patch.object(experiment, "request", side_effect=AssertionError("must remain offline")), \
                patch.object(experiment.subprocess, "run", side_effect=AssertionError("must not encode")):
            experiment.collect(folder)
        self.assertEqual(before, {p: (p.read_bytes(), p.stat().st_mtime_ns) for p in before})
        (folder / "preview.mp4").unlink()
        with patch.object(experiment, "request", side_effect=AssertionError("must not regenerate")):
            with self.assertRaises(RuntimeError):
                experiment.collect(folder)


if __name__ == "__main__":
    unittest.main()
