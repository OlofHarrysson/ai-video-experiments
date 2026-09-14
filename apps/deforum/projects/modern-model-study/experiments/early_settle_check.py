"""Offline lineage, replay, preserved-prefix and delivery checks for early settling."""

import argparse
import copy
import json
import subprocess

import early_settle as e
import numpy as np
from PIL import Image

from deforum_lab.image.warps import warp_at_time
from deforum_lab.media.verification import check_rife
from deforum_lab.records import sha
from deforum_lab.rendering.graphs import repaint_graph
from deforum_lab.rendering.schedules import recipe
from deforum_lab.rendering.verification import validate_execution


def read(p):
    return json.loads(p.read_text())


def pixels(p):
    return np.asarray(Image.open(p).convert("RGB"))


def validate_job(run, requested, parent, initialization, target):
    assert read(run / "workflow.api.json") == requested
    assert sha(run / "anchor.png") == sha(initialization)
    assert sha(run / "frames/0000.png") == sha(target)
    assert read(run / "frame-hashes.json") == {"0000.png": sha(target)}
    executed = read(run / "workflow.executed.json")
    prompt_id, remote = validate_execution(
        requested,
        executed,
        read(run / "upload.json"),
        read(run / "history.json"),
        read(run / "submit-response.json"),
        read(run / "submission.json"),
        sha(parent),
        sha(initialization),
    )
    expected = copy.deepcopy(executed)
    expected["20"]["is_changed"] = [sha(initialization)]
    assert json.loads(Image.open(target).info["prompt"]) == expected
    return {
        "run": str(run.relative_to(e.OUT)),
        "prompt_id": prompt_id,
        "parent_sha256": sha(parent),
        "initialization_sha256": sha(initialization),
        "output_sha256": sha(target),
        "history_output": remote,
    }


def generation():
    root = e.OUT / e.CASE
    config = read(root / "config.json")
    original = read(e.OLD / "config.json")
    assert config == read(e.CONFIG)
    assert {k: v for k, v in config.items() if k not in ("case", "noise_schedule")} == {
        k: v for k, v in original.items() if k not in ("case", "noise_schedule")
    }
    prefix = read(root / "prefix.json")
    assert prefix["through_frame"] == 96
    assert [r["frame"] for r in prefix["paintings"]] == list(range(0, 97, 12))
    for row in prefix["paintings"]:
        f = row["frame"]
        assert (
            row["sha256"]
            == sha(root / f"anchors/{f:04d}.png")
            == sha(e.OLD / f"anchors/{f:04d}.png")
        )
        assert recipe(config, f / 24) == recipe(original, f / 24)
    assert sorted(p.stem for p in (root / "anchors").glob("*.png")) == [
        f"{f:04d}" for f in range(0, 192, 12)
    ]
    replay = read(e.OUT / "control/replay.json")
    run = e.OUT / replay["run"]
    original_rec = read(e.OLD / "anchor-0108.json")
    old_run = e.OLD.parent / original_rec["run"]
    g = read(old_run / "workflow.api.json")
    assert read(e.OUT / "control/workflow.api.json") == g
    assert sha(e.OUT / "control/input.png") == sha(e.OLD / "warped-inputs/0108.png")
    assert replay["pixel_identical"] and np.array_equal(
        pixels(run / "frames/0000.png"), pixels(e.OLD / "anchors/0108.png")
    )
    rows = [
        validate_job(
            run,
            g,
            root / "anchors/0096.png",
            e.OUT / "control/input.png",
            run / "frames/0000.png",
        )
    ]
    changes = []
    for f in range(108, 181, 12):
        rec = read(root / f"anchor-{f:04d}.json")
        run = e.OUT / rec["run"]
        t = f / 24
        parent = root / f"anchors/{f - 12:04d}.png"
        target = root / f"anchors/{f:04d}.png"
        init = root / f"warped-inputs/{f:04d}.png"
        scene, sigmas = recipe(config, t)
        assert sigmas[0] == (0.25 if f == 108 else 0.1)
        assert (
            rec["sigmas"] == sigmas
            and rec["seed"] == config["seed"] + f // 12
            and rec["frame"] == f
            and rec["seconds"] == t
        )
        assert (
            rec["parent_sha256"] == sha(parent)
            and rec["initialization_sha256"] == sha(init)
            and rec["output_sha256"] == sha(target)
        )
        assert np.array_equal(
            pixels(init), warp_at_time(pixels(parent), t - 0.5, t, config["phrases"])
        )
        g = repaint_graph(scene["prompt"], config["seed"] + f // 12, sigmas)
        g["11"]["inputs"]["filename_prefix"] = "early-settle/" + e.CASE
        rows.append(validate_job(run, g, parent, init, target))
        changes.append(
            {
                "frame": f,
                "seconds": t,
                "sigma_start": sigmas[0],
                "repaint_change_rgb": float(
                    np.abs(
                        pixels(target).astype(float) - pixels(init).astype(float)
                    ).mean()
                    / 255
                ),
            }
        )
    assert len({r["prompt_id"] for r in rows}) == 8
    assert len(list((e.OUT / "runs").iterdir())) == 8
    return {
        "verified": True,
        "new_recurrent_paintings": 7,
        "runtime_control_pixel_identical": True,
        "preserved_paintings": 9,
        "rows": rows,
        "repaint_changes": changes,
    }


def delivery():
    manifest = check_rife(
        e.OUT / e.CASE, "full", size=(1536, 1024), fps=24, cadence=12, frame_count=192
    )
    old = e.OLD / "section-016/rife"
    new = e.OUT / e.CASE / "section-016/rife"
    prefix = []
    for f in range(97):
        assert sha(new / f"frames/{f:04d}.png") == sha(old / f"frames/{f:04d}.png"), f
        prefix.append({"frame": f, "sha256": sha(new / f"frames/{f:04d}.png")})
    assert np.array_equal(
        warp_at_time(
            pixels(e.OUT / e.CASE / "anchors/0180.png"),
            7.5,
            8,
            read(e.CONFIG)["phrases"],
        ),
        pixels(e.OUT / e.CASE / "anchors/0180.png"),
    )
    video = new / "preview.mp4"
    subprocess.run(
        ["ffmpeg", "-v", "error", "-xerror", "-i", str(video), "-f", "null", "-"],
        check=True,
    )
    info = json.loads(
        subprocess.check_output(
            [
                "ffprobe",
                "-v",
                "error",
                "-select_streams",
                "v:0",
                "-count_frames",
                "-show_entries",
                "stream=width,height,r_frame_rate,nb_read_frames,duration",
                "-of",
                "json",
                str(video),
            ]
        )
    )["streams"][0]
    assert (
        info["r_frame_rate"] == "24/1"
        and info["nb_read_frames"] == "192"
        and float(info["duration"]) == 8
    )
    return {
        "verified": True,
        "video": info,
        "prefix_through_frame": 96,
        "prefix": prefix,
        "anchors_retained": 16,
        "rife_intermediates": 165,
        "final_hold_frames": 11,
        "video_sha256": manifest["video_sha256"],
    }


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("stage", choices=["generation", "delivery"])
    args = p.parse_args()
    result = {"generation": generation()}
    if args.stage == "delivery":
        result["delivery"] = delivery()
    result["verified"] = True
    print(json.dumps(result, indent=2))
