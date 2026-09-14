"""A seven-painting recurrent branch from the accepted city reveal."""

import argparse
from pathlib import Path

import numpy as np
from PIL import Image

from deforum_lab.infrastructure.pod import PodClient
from deforum_lab.media.finishing import finish_paintings
from deforum_lab.paths import AppPaths
from deforum_lab.records import copy_verified, read, require, save, sha
from deforum_lab.rendering.feedback import render_paintings

HERE = Path(__file__).resolve().parent
PATHS = AppPaths(HERE.parents[2])
OLD = HERE.parent / "exports/hold-transform-v001/low-hold"
OUT = HERE.parent / "exports/early-settle-v001"
CASE = "early-settle"
CONFIG = HERE / "early-settle-config.json"


def prepare(output=OUT, original=OLD, config_path=CONFIG):
    old = read(original / "config.json")
    config = {
        **old,
        "case": CASE,
        "noise_schedule": [
            *[p for p in old["noise_schedule"] if p["at"] <= 4],
            {"at": 4.5, "noise": 0.25},
            {"at": 5, "noise": 0.1},
            {"at": 8, "noise": 0.1},
        ],
    }
    save(config_path, config)
    save(output / CASE / "config.json", config)
    rows = []
    for frame in range(0, 97, 12):
        source = original / f"anchors/{frame:04d}.png"
        copy_verified(source, output / CASE / f"anchors/{frame:04d}.png")
        rows.append(
            {
                "frame": frame,
                "source": str(source.relative_to(PATHS.root)),
                "sha256": sha(source),
            }
        )
    save(output / CASE / "prefix.json", {"through_frame": 96, "paintings": rows})
    rec = read(original / "anchor-0108.json")
    run = original.parent / rec["run"]
    copy_verified(run / "workflow.api.json", output / "control/workflow.api.json")
    copy_verified(original / "warped-inputs/0108.png", output / "control/input.png")
    copy_verified(original / "anchors/0108.png", output / "control/expected.png")


def render(client, output=OUT):
    root = output / CASE
    config = read(root / "config.json")
    for row in read(root / "prefix.json")["paintings"]:
        require(
            sha(root / f"anchors/{row['frame']:04d}.png") == row["sha256"],
            "Preserved painting differs",
        )
    graph = read(output / "control/workflow.api.json")
    control = client.submit_once(
        output,
        "early-settle-runtime-control",
        graph,
        output / "control/input.png",
        {"parent_sha256": sha(root / "anchors/0096.png"), "frame": 108, "seconds": 4.5},
    )
    with (
        Image.open(control / "frames/0000.png") as actual,
        Image.open(output / "control/expected.png") as expected,
    ):
        same = np.array_equal(np.asarray(actual), np.asarray(expected))
    save(
        output / "control/replay.json",
        {"pixel_identical": same, "run": str(control.relative_to(output))},
    )
    require(same, "Original repaint did not reproduce; inspect before continuing")
    render_paintings(
        config,
        output,
        client,
        first_frame=108,
        last_frame=180,
        run_prefix="early-settle",
        filename_prefix="early-settle/" + CASE,
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "stage", choices=["prepare", "render", "pair", "full", "sheets"]
    )
    parser.add_argument("--deployment", type=Path)
    args = parser.parse_args()
    if args.stage == "prepare":
        prepare()
    elif args.stage == "render":
        if not args.deployment:
            parser.error("render requires --deployment")
        render(PodClient.from_path(args.deployment))
    else:
        finish_paintings(
            PATHS, OUT / CASE, "prepare" if args.stage == "sheets" else args.stage
        )
