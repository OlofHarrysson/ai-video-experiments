"""The Red Rite: recurrent Krea opening with immutable painting receipts."""

import argparse
import json
from itertools import pairwise
from pathlib import Path

import numpy as np
from PIL import Image

from deforum_lab.image.warps import warp_at_time
from deforum_lab.infrastructure.pod import PodClient
from deforum_lab.records import copy_verified, read, require, save, sha
from deforum_lab.rendering.feedback import render_paintings
from deforum_lab.rendering.graphs import repaint_graph
from deforum_lab.rendering.schedules import recipe
from deforum_lab.rendering.verification import validate_execution

HERE = Path(__file__).resolve().parent
APP = HERE.parents[2]
PROJECT = HERE.parent
OUT = PROJECT / "exports/v001"


def check(config, last):
    root = OUT / config["case"]
    require(read(root / "config.json") == config, "Frozen configuration differs")
    require(
        sha(root / "anchors/0000.png") == config["initial_sha256"], "Opening differs"
    )
    jobs = []
    positions = [f for f in config["painting_frames"] if f <= last]
    for previous, frame in pairwise(positions):
        row = read(root / f"anchor-{frame:04d}.json")
        run = OUT / row["run"]
        parent = root / f"anchors/{previous:04d}.png"
        source = root / f"warped-inputs/{frame:04d}.png"
        target = root / f"anchors/{frame:04d}.png"
        require(row["parent_sha256"] == sha(parent), "Feedback parent differs")
        require(
            row["initialization_sha256"] == sha(source) == sha(run / "anchor.png"),
            "Initialization differs",
        )
        require(
            row["output_sha256"] == sha(target) == sha(run / "frames/0000.png"),
            "Output differs",
        )
        scene, sigmas = recipe(config, frame / 24)
        expected = repaint_graph(scene["prompt"], config["seed"] + frame // 12, sigmas)
        expected["9"]["inputs"]["cfg"] = config["cfg"]
        expected["11"]["inputs"]["filename_prefix"] = "red-rite/" + config["case"]
        require(read(run / "workflow.api.json") == expected, "Requested graph differs")
        executed = read(run / "workflow.executed.json")
        prompt_id, _ = validate_execution(
            expected,
            executed,
            read(run / "upload.json"),
            read(run / "history.json"),
            read(run / "submit-response.json"),
            read(run / "submission.json"),
            sha(parent),
            sha(source),
        )
        with Image.open(parent) as im:
            wanted = warp_at_time(
                np.asarray(im.convert("RGB")),
                previous / 24,
                frame / 24,
                config["phrases"],
            )
        with Image.open(source) as im:
            require(
                np.array_equal(np.asarray(im.convert("RGB")), wanted), "Warp differs"
            )
        with Image.open(target) as im:
            embedded = json.loads(im.info["prompt"])
            for node in embedded.values():
                node.pop("is_changed", None)
            require(
                embedded == executed and im.size == (1536, 1024),
                "PNG graph or dimensions differ",
            )
        jobs.append({"frame": frame, "prompt_id": prompt_id, "sha256": sha(target)})
    require(len({j["prompt_id"] for j in jobs}) == len(jobs), "Repeated job id")
    suffix = "" if last == config["painting_frames"][-1] else f"-through-{last:04d}"
    save(root / f"study-check{suffix}.json", {"verified": True, "jobs": jobs})
    return jobs


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("stage", choices=["render", "check"])
    parser.add_argument("matrix", type=Path)
    parser.add_argument("--deployment", type=Path)
    parser.add_argument("--through-frame", type=int)
    args = parser.parse_args()
    for config in read(args.matrix)["cases"]:
        require(
            config["case"].startswith("rr-")
            and Path(config["case"]).name == config["case"],
            "Invalid case",
        )
        require(
            config["cfg"] == 1
            and config["cadence"] == 12
            and config["sampler"] == "euler"
            and config["reference_mode"] == "none",
            "Opening recipe differs",
        )
        last = args.through_frame or config["painting_frames"][-1]
        require(last in config["painting_frames"][1:], "Expected repaint boundary")
        if args.stage == "render":
            require(args.deployment is not None, "Explicit deployment required")
            source = APP / config["initial_image"]
            require(sha(source) == config["initial_sha256"], "Opening source differs")
            root = OUT / config["case"]
            save(root / "config.json", config)
            copy_verified(source, root / "anchors/0000.png")
            render_paintings(
                config,
                OUT,
                PodClient.from_path(args.deployment),
                first_frame=12,
                last_frame=last,
                run_prefix=config["case"],
                filename_prefix="red-rite/" + config["case"],
            )
        jobs = check(config, last)
        print(f"VERIFIED {config['case']}: {len(jobs)} paintings", flush=True)


if __name__ == "__main__":
    main()
