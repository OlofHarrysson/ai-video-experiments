"""Explicit project orchestration over the existing recurrent Krea package."""

import argparse
import copy
import json
from itertools import pairwise
from pathlib import Path

import numpy as np
from PIL import Image

from deforum_lab.image.warps import warp_at_time
from deforum_lab.infrastructure.pod import PodClient
from deforum_lab.records import copy_verified, read, require, save, sha
from deforum_lab.rendering.feedback import render_paintings
from deforum_lab.rendering.graphs import graph, repaint_graph
from deforum_lab.rendering.schedules import recipe
from deforum_lab.rendering.verification import validate_execution

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parent
APP = HERE.parents[2]
OUT = PROJECT / "exports/v001"
FPS = 24
PREFIX = "night-orchard"


def pixels(path):
    with Image.open(path) as image:
        return np.asarray(image.convert("RGB"))


def opening_graph(config):
    opening = config["opening"]
    result = graph("krea", opening["prompt"], opening["seed"])
    result["6"]["inputs"].update(width=opening["width"], height=opening["height"])
    result["11"]["inputs"]["filename_prefix"] = f"{PREFIX}/{config['case']}/opening"
    return result


def preflight(config):
    positions = config["painting_frames"]
    require(positions and positions[0] == 0, "Opening must start at zero")
    require(
        all(type(f) is int and f >= 0 and f % 12 == 0 for f in positions)
        and all(b - a == 12 for a, b in pairwise(positions)),
        "Expected half-second painting anchors",
    )
    require(positions[-1] + 12 == round(config["duration"] * FPS), "Duration differs")
    require(config["cadence"] == 12 and config["cfg"] == 1, "Recipe changed")
    for frame in positions:
        scene, sigmas = recipe(config, frame / FPS)
        require(bool(scene["prompt"]), "Empty prompt")
        require(
            len(sigmas) == 4
            and sigmas[-1] == 0
            and all(a > b for a, b in pairwise(sigmas)),
            "Expected three descending Euler intervals",
        )
    if "opening" in config:
        opening_graph(config)
    else:
        require(
            "prefix_root" in config and "prefix_through" in config, "Missing source"
        )
        source = (APP / config["prefix_root"]).resolve()
        require(source.is_relative_to(PROJECT), "Source must belong to this project")
    print(f"Valid plan: {config['case']}, {len(positions)} paintings", flush=True)


def prepare(config):
    root = OUT / config["case"]
    save(root / "config.json", config)
    if "prefix_root" not in config:
        return
    source = APP / config["prefix_root"]
    rows = []
    for frame in config["painting_frames"]:
        if frame > config["prefix_through"]:
            break
        original = source / f"anchors/{frame:04d}.png"
        copy_verified(original, root / f"anchors/{frame:04d}.png")
        rows.append(
            {
                "frame": frame,
                "source": str(original.relative_to(APP)),
                "sha256": sha(original),
            }
        )
    save(root / "prefix.json", rows)


def opening(config, deployment):
    prepare(config)
    root = OUT / config["case"]
    run = PodClient.from_path(deployment).submit_once(
        OUT, f"{PREFIX}-{config['case']}-opening", opening_graph(config)
    )
    copy_verified(run / "frames/0000.png", root / "anchors/0000.png")
    save(
        root / "opening.json",
        {"run": str(run.relative_to(OUT)), "sha256": sha(root / "anchors/0000.png")},
    )
    print(root / "anchors/0000.png", flush=True)


def render(config, deployment, through):
    prepare(config)
    first = config.get("prefix_through", 0) + 12
    render_paintings(
        config,
        OUT,
        PodClient.from_path(deployment),
        first_frame=first,
        last_frame=through,
        run_prefix=f"{PREFIX}-{config['case']}",
        filename_prefix=f"{PREFIX}/{config['case']}",
    )


def check(config, through):
    root = OUT / config["case"]
    require(read(root / "config.json") == config, "Frozen config differs")
    positions = [f for f in config["painting_frames"] if f <= through]
    require(
        all((root / f"anchors/{f:04d}.png").exists() for f in positions),
        "Missing painting",
    )
    jobs = []
    if "opening" in config:
        row = read(root / "opening.json")
        run = OUT / row["run"]
        expected = opening_graph(config)
        history, submission = read(run / "history.json"), read(run / "submission.json")
        require(
            read(run / "workflow.api.json")
            == read(run / "workflow.executed.json")
            == expected,
            "Opening graph differs",
        )
        require(
            history["status"]["completed"]
            and history["status"]["status_str"] == "success",
            "Opening incomplete",
        )
        require(
            history["prompt"][1]
            == submission["prompt_id"]
            == read(run / "submit-response.json")["prompt_id"],
            "Opening prompt id differs",
        )
        require(history["prompt"][2] == expected, "Opening history differs")
        target = root / "anchors/0000.png"
        require(
            sha(target) == row["sha256"] == sha(run / "frames/0000.png"),
            "Opening hash differs",
        )
        with Image.open(target) as image:
            require(
                json.loads(image.info["prompt"]) == expected,
                "Opening PNG provenance differs",
            )
            require(
                image.size == (config["opening"]["width"], config["opening"]["height"]),
                "Opening dimensions differ",
            )
        jobs.append(
            {"frame": 0, "prompt_id": submission["prompt_id"], "sha256": sha(target)}
        )
    else:
        for row in read(root / "prefix.json"):
            require(
                sha(root / f"anchors/{row['frame']:04d}.png")
                == row["sha256"]
                == sha(APP / row["source"]),
                "Prefix differs",
            )
    for previous, frame in pairwise(positions):
        if frame <= config.get("prefix_through", 0):
            continue
        row = read(root / f"anchor-{frame:04d}.json")
        run = OUT / row["run"]
        parent = root / f"anchors/{previous:04d}.png"
        target = root / f"anchors/{frame:04d}.png"
        source = root / f"warped-inputs/{frame:04d}.png"
        scene, sigmas = recipe(config, frame / FPS)
        seed = config.get("seeds_by_frame", {}).get(
            str(frame), config["seed"] + frame // 12
        )
        expected = repaint_graph(scene["prompt"], seed, sigmas)
        expected["11"]["inputs"]["filename_prefix"] = f"{PREFIX}/{config['case']}"
        require(read(run / "workflow.api.json") == expected, "Requested graph differs")
        require(row["parent_sha256"] == sha(parent), "Parent differs")
        require(
            row["output_sha256"] == sha(target) == sha(run / "frames/0000.png"),
            "Output differs",
        )
        require(
            row["initialization_sha256"] == sha(source) == sha(run / "anchor.png"),
            "Input differs",
        )
        require(
            np.array_equal(
                pixels(source),
                warp_at_time(
                    pixels(parent), previous / FPS, frame / FPS, config["phrases"]
                ),
            ),
            "Warp differs",
        )
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
        embedded = copy.deepcopy(executed)
        embedded["20"]["is_changed"] = [sha(source)]
        with Image.open(target) as image:
            require(
                json.loads(image.info["prompt"]) == embedded, "PNG provenance differs"
            )
        jobs.append({"frame": frame, "prompt_id": prompt_id, "sha256": sha(target)})
    require(len({row["prompt_id"] for row in jobs}) == len(jobs), "Repeated job id")
    save(
        root / f"generation-check-{through:04d}.json",
        {"verified": True, "through_frame": through, "jobs": jobs},
    )
    print(f"Verified {len(jobs)} generated paintings and preserved prefix", flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "stage", choices=["plan", "opening", "prepare", "render", "check"]
    )
    parser.add_argument("case")
    parser.add_argument("--deployment", type=Path)
    parser.add_argument("--through", type=int)
    args = parser.parse_args()
    require(Path(args.case).name == args.case, "Expected a case name")
    config = read(HERE / "configs" / f"{args.case}.json")
    require(config["case"] == args.case, "Case id differs")
    preflight(config)
    through = config["painting_frames"][-1] if args.through is None else args.through
    require(through in config["painting_frames"], "Expected a painting boundary")
    if args.stage in ("opening", "render") and args.deployment is None:
        parser.error("Inference requires an explicit owned deployment receipt")
    if args.stage == "opening":
        opening(config, args.deployment)
    elif args.stage == "prepare":
        prepare(config)
    elif args.stage == "render":
        render(config, args.deployment, through)
    elif args.stage == "check":
        check(config, through)


if __name__ == "__main__":
    main()
