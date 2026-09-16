import json
import math
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import numpy as np
from PIL import Image

from deforum_lab.image.warps import mapping
from deforum_lab.media.branching import BranchPlanner, incoming_velocity, owner_at
from deforum_lab.records import save, sha


class MotionTests(unittest.TestCase):
    def test_continuation_matches_velocity_and_round_trips(self):
        v = [0.02, -0.03, 0.12, 0.08]
        p = {
            "kind": "continuation",
            "start": 2,
            "duration": 4,
            "center": [0.75, 0.5],
            "end": [0.1, 0.2, math.log(2), -0.2],
            "velocity_start": v,
            "velocity_end": [0.01, 0, 0, 0],
        }
        q = np.array([[0.75, 0.5], [0.9, 0.3], [0.2, 0.8]])
        dt = 1e-5
        d = (mapping(q, 2 + dt, [p]) - q) / dt
        relative = q - [0.75, 0.5]
        expected = np.stack(
            [
                v[0] + v[2] * relative[:, 0] - v[3] * relative[:, 1],
                v[1] + v[2] * relative[:, 1] + v[3] * relative[:, 0],
            ],
            -1,
        )
        np.testing.assert_allclose(d, expected, atol=1e-5)
        for t in (1, 2, 3, 6, 7):
            np.testing.assert_allclose(
                mapping(mapping(q, t, [p]), t, [p], True), q, atol=1e-12
            )
        np.testing.assert_allclose(
            (mapping(q, 6 + dt, [p]) - mapping(q, 6, [p])) / dt,
            [[0.01, 0]] * 3,
            atol=1e-8,
        )

    def test_incoming_fit_recovers_similarity_and_flags_regional_motion(self):
        fitted, residual = incoming_velocity(
            [
                {
                    "kind": "cruise",
                    "start": 0,
                    "velocity": [0, 0],
                    "log_zoom_rate": 0.12,
                    "roll_rate": 4,
                }
            ],
            2,
            [0.75, 0.5],
        )
        np.testing.assert_allclose(fitted, [0, 0, 0.12, math.radians(4)], atol=2e-5)
        self.assertLess(residual, 1e-8)
        _, residual = incoming_velocity(
            [
                {
                    "start": 0,
                    "duration": 4,
                    "zoom": 0,
                    "turn": 60,
                    "travel": [0, 0],
                    "radius": 0.35,
                }
            ],
            2,
            [0.75, 0.5],
        )
        self.assertGreater(residual, 0.005)


class BranchTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.app = Path(self.tmp.name)
        self.root = self.app / "projects/study/exports/round/case"
        self.delivery = self.root / "faster/rife-moving-tail"
        (self.delivery / "frames").mkdir(parents=True)
        self.config = {
            "case": "case",
            "seed": 42,
            "cadence": 12,
            "duration": 1.5,
            "cfg": 1,
            "scenes": [{"at": 0, "name": "scene", "prompt": "A doorway"}],
            "noise_schedule": [{"at": 0, "noise": 0.6}],
            "painting_frames": [0, 12, 24],
            "phrases": [
                {
                    "kind": "cruise",
                    "start": 0,
                    "velocity": [0.02, 0],
                    "log_zoom_rate": 0.1,
                }
            ],
        }
        save(self.root / "config.json", self.config)
        rows = []
        for f in range(24):
            image = Image.new("RGB", (96, 64), (f * 9, 90, 120))
            path = self.delivery / f"frames/{f:04d}.png"
            image.save(path)
            row = {
                "index": f,
                "file": f"frames/{f:04d}.png",
                "sha256": sha(path),
                "kind": "anchor" if f % 8 == 0 else "interpolation",
            }
            if f % 8 == 0:
                row["source_index"] = f // 8
                target = self.root / f"anchors/{f // 8 * 12:04d}.png"
                target.parent.mkdir(exist_ok=True)
                target.write_bytes(path.read_bytes())
            rows.append(row)
        self.video = self.delivery / "preview.mp4"
        self.video.write_bytes(b"fixture source; previews render archived PNGs")
        save(
            self.delivery / "manifest.json",
            {
                "status": "complete",
                "video_sha256": sha(self.video),
                "output_frames": rows,
            },
        )
        save(
            self.root / "faster/retiming.json",
            {
                "source_config_sha256": sha(self.root / "config.json"),
                "fps": 24,
                "source_start_frame": 0,
                "speed_multiplier": 1.5,
                "source_anchor_frames": [0, 12, 24],
                "delivery_anchor_frames": [0, 8, 16],
            },
        )
        self.source = str(self.video.relative_to(self.app))
        self.planner = BranchPlanner(self.app)
        self.request = {
            "source": self.source,
            "frame": 10,
            "duration": 1,
            "zoom": 1.2,
            "pan_x": 0.1,
            "pan_y": 0,
            "roll": 0,
            "center_x": 0.5,
            "center_y": 0.5,
            "noise": 0.5,
            "end_drift": 0.02,
            "match_speed": True,
            "prompt": "A new forest",
            "intent": "Arrive and reveal",
        }

    def test_snap_retime_and_replace_only_future(self):
        s, c, summary = self.planner.plan(self.request)
        self.assertEqual(s["source_frame"], 12)
        self.assertEqual(s["display_frame"], 8)
        self.assertEqual(c["prefix_through"], 12)
        self.assertEqual(c["painting_frames"], [0, 12, 24, 36, 48])
        self.assertEqual(c["phrases"][0]["start"], 0.5)
        self.assertEqual(c["prompt_schedule"][-1]["at"], 1)
        self.assertEqual(c["noise_schedule"][-1]["noise"], 0.5)
        self.assertEqual(summary["duration"], 1)
        self.assertEqual(
            json.loads((self.root / "config.json").read_text()), self.config
        )

    def test_refuse_outside_workspace_and_changed_anchor(self):
        with self.assertRaises(ValueError):
            self.planner.describe("../../secret", 0)
        (self.root / "anchors/0012.png").write_bytes(b"changed")
        with self.assertRaises(ValueError):
            self.planner.describe(self.source, 10)

    def test_preview_save_preserves_prefix_and_is_idempotent(self):
        before = {p: sha(p) for p in self.root.rglob("*") if p.is_file()}
        preview = self.planner.preview(self.request)
        self.assertEqual(preview["lead_seconds"], 8 / 24)
        self.assertTrue((self.planner.work / preview["id"] / "preview.mp4").is_file())
        result = self.planner.save_draft(preview["id"])
        root = self.app / result["path"]
        self.assertEqual(result["paintings_preserved"], 2)
        self.assertEqual(self.planner.save_draft(preview["id"]), result)
        self.assertEqual({p: sha(p) for p in before}, before)
        self.assertEqual(
            sha(root / "anchors/0012.png"), sha(self.root / "anchors/0012.png")
        )
        self.assertEqual(
            json.loads((root / "draft.json").read_text())["status"],
            "draft-not-generated",
        )
        self.assertFalse((root / "anchors/0024.png").exists())

    def test_changed_source_after_preview_cannot_be_saved(self):
        preview = self.planner.preview(self.request)
        self.video.write_bytes(b"changed")
        with self.assertRaises(ValueError):
            self.planner.save_draft(preview["id"])

    def test_changed_earlier_painting_leaves_no_partial_branch(self):
        preview = self.planner.preview(self.request)
        (self.root / "anchors/0000.png").write_bytes(b"changed")
        with self.assertRaisesRegex(ValueError, "earlier preserved painting"):
            self.planner.save_draft(preview["id"])
        self.assertFalse((self.app / "projects/study/branches").exists())

    def test_incoming_owner_follows_prefix_at_the_join(self):
        child = self.app / "projects/study/exports/child"
        save(
            child / "config.json",
            {
                **self.config,
                "case": "child",
                "prefix_root": str(self.root.relative_to(self.app)),
                "prefix_through": 12,
            },
        )
        self.assertEqual(owner_at(self.app, child, 12)["case"], "case")
        self.assertEqual(owner_at(self.app, child, 24)["case"], "child")

    def test_reject_nonfinite_or_excessive_request(self):
        for change in (
            {"zoom": float("nan")},
            {"zoom": 33},
            {"duration": 99},
            {"prompt": ""},
        ):
            with self.assertRaises(ValueError):
                self.planner.plan({**self.request, **change})

    def test_large_doorway_push_warns_and_releases_zoom(self):
        _, config, summary = self.planner.plan(
            {**self.request, "zoom": 26, "duration": 6}
        )
        self.assertTrue(
            any("Large enlargement" in warning for warning in summary["warnings"])
        )
        phrase = config["phrases"][0]
        end = phrase["start"] + phrase["duration"]
        points = np.array([[0.4, 0.4], [0.6, 0.6]])
        a = mapping(points, end, [phrase])
        b = mapping(points, end + 1, [phrase])
        np.testing.assert_allclose(b[1] - b[0], a[1] - a[0])
        self.assertLess(b[0, 0], a[0, 0])

    def cli(self, *args, success=True):
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "deforum_lab.media.motion_preview",
                "--app",
                str(self.app),
                *args,
            ],
            cwd=self.tmp.name,
            capture_output=True,
            text=True,
            check=False,
        )
        if success:
            self.assertEqual(result.returncode, 0, result.stderr)
            return json.loads(result.stdout)
        self.assertEqual(result.returncode, 2)
        self.assertNotIn("Traceback", result.stderr)
        return result.stderr

    def test_cli_inspect_edit_preview_and_save_without_server(self):
        info = self.cli("inspect", self.source, "--frame", "10")
        self.assertEqual(info["source_frame"], 12)
        self.assertTrue(Path(info["painting_path"]).is_file())
        initialized = self.cli(
            "init",
            self.source,
            "--frame",
            "10",
            "--intent",
            "Reveal the forest",
            "--out",
            "plan.json",
        )
        plan_path = Path(initialized["plan_path"])
        plan = json.loads(plan_path.read_text())
        self.assertEqual(plan["prompt"], "A doorway")
        plan.update(zoom=1.4, duration=1, prompt="A new forest")
        plan_path.write_text(json.dumps(plan))
        preview = self.cli("preview", str(plan_path))
        self.assertTrue(Path(preview["preview_path"]).is_file())
        self.assertTrue(Path(preview["summary_path"]).is_file())
        self.assertNotIn("preview_url", preview)
        saved = self.cli("save", preview["id"])
        self.assertEqual(saved["paintings_preserved"], 2)
        self.assertTrue((Path(saved["branch_path"]) / "config.json").is_file())
        self.assertEqual(self.cli("save", preview["id"]), saved)

    def test_cli_rejects_overwrite_and_bad_plan(self):
        path = self.app / "plan.json"
        path.write_text("retained")
        error = self.cli(
            "init",
            self.source,
            "--frame",
            "10",
            "--intent",
            "Reveal",
            "--out",
            str(path),
            success=False,
        )
        self.assertIn("already exists", error)
        self.assertEqual(path.read_text(), "retained")
        self.assertIn("motion-preview:", self.cli("preview", str(path), success=False))


if __name__ == "__main__":
    unittest.main()
