"""Run frozen cases in the bounded autonomous learning session."""

import argparse
import copy
import json
import subprocess
from itertools import pairwise
from pathlib import Path

import numpy as np
from PIL import Image

from deforum_lab.image.warps import warp_at_time
from deforum_lab.infrastructure.pod import PodClient
from deforum_lab.paths import AppPaths
from deforum_lab.records import copy_verified, read, require, save, sha
from deforum_lab.rendering.feedback import render_paintings
from deforum_lab.rendering.graphs import node, repaint_graph
from deforum_lab.rendering.schedules import recipe
from deforum_lab.rendering.verification import validate_execution

HERE = Path(__file__).resolve().parent
APP = HERE.parents[3]
PATHS = AppPaths(APP)
OUT = HERE.parents[1] / "exports/two-hour-lab-v001"
FPS = 24
CASES = ()
BATCH = "session"


def conditioning_controls(graph, config, seconds):
    """Experimental conditioning changes, kept outside the recurrent loop."""
    for event in config.get("cfg_schedule", []):
        if event["at"] <= seconds:
            graph["9"]["inputs"]["cfg"] = event["cfg"]
    if "negative_prompt" in config:
        graph["50"] = node(
            "CLIPTextEncode", clip=["2", 0], text=config["negative_prompt"]
        )
        graph["9"]["inputs"]["negative"] = ["50", 0]
    if "conditioning_blend" in config:
        blend = config["conditioning_blend"]
        alpha = float(np.interp(seconds, *zip(*blend["schedule"])))
        graph["51"] = node("CLIPTextEncode", clip=["2", 0], text=blend["old"])
        graph["52"] = node("CLIPTextEncode", clip=["2", 0], text=blend["new"])
        if blend["mode"] == "average":
            graph["53"] = node(
                "ConditioningAverage",
                conditioning_from=["51", 0],
                conditioning_to=["52", 0],
                conditioning_to_strength=alpha,
            )
            positive = ["53", 0]
        elif blend["mode"] == "switch":
            positive = ["51", 0] if alpha < 0.5 else ["52", 0]
        else:
            raise ValueError("Unknown conditioning blend mode")
        graph["9"]["inputs"]["positive"] = positive
        graph["5"]["inputs"]["conditioning"] = positive


def pixels(path):
    with Image.open(path) as im:
        return np.array(im.convert("RGB"))


def prepare():
    for case in CASES:
        config = read(HERE / "configs" / f"{case}.json")
        save(OUT / case / "config.json", config)
        prefix = []
        old = APP / config["prefix_root"]
        for frame in [
            f for f in config["painting_frames"] if f <= config["prefix_through"]
        ]:
            prefix.append(
                {
                    "frame": frame,
                    "source": str((old / f"anchors/{frame:04d}.png").relative_to(APP)),
                    "sha256": sha(old / f"anchors/{frame:04d}.png"),
                }
            )
            copy_verified(
                old / f"anchors/{frame:04d}.png",
                OUT / case / f"anchors/{frame:04d}.png",
            )
        save(OUT / case / "prefix.json", prefix)
    print("Prepared", len(CASES), "frozen cases.")


def render(deployment):
    client = PodClient.from_path(deployment)
    for case in CASES:
        config = read(OUT / case / "config.json")
        for row in read(OUT / case / "prefix.json"):
            require(
                sha(OUT / case / f"anchors/{row['frame']:04d}.png") == row["sha256"],
                "Prefix differs",
            )
        render_paintings(
            config,
            OUT,
            client,
            first_frame=next(
                f for f in config["painting_frames"] if f > config["prefix_through"]
            ),
            last_frame=config["painting_frames"][-1],
            run_prefix="two-hour-lab-" + case,
            filename_prefix="two-hour-lab/" + case,
            graph_transform=conditioning_controls,
        )


def check():
    jobs, measurements = [], []
    for case in CASES:
        root = OUT / case
        config = read(root / "config.json")
        require(
            config == read(HERE / "configs" / f"{case}.json"), "Frozen config differs"
        )
        positions = config["painting_frames"]
        require(
            [int(p.stem) for p in sorted((root / "anchors").glob("*.png"))]
            == positions,
            "Painting inventory differs",
        )
        old = APP / config["prefix_root"]
        for f in [x for x in positions if x <= config["prefix_through"]]:
            require(
                sha(root / f"anchors/{f:04d}.png") == sha(old / f"anchors/{f:04d}.png"),
                "Prefix changed",
            )
        for previous, f in pairwise(positions):
            if f <= config["prefix_through"]:
                continue
            rec = read(root / f"anchor-{f:04d}.json")
            run = OUT / rec["run"]
            parent = root / f"anchors/{previous:04d}.png"
            target = root / f"anchors/{f:04d}.png"
            source = root / f"warped-inputs/{f:04d}.png"
            scene, sigmas = recipe(config, f / FPS)
            graph = repaint_graph(
                scene["prompt"], config["seeds_by_frame"][str(f)], sigmas
            )
            graph["9"]["inputs"]["cfg"] = config.get("cfg", 1.0)
            conditioning_controls(graph, config, f / FPS)
            graph["11"]["inputs"]["filename_prefix"] = "two-hour-lab/" + case
            require(read(run / "workflow.api.json") == graph, "Graph differs")
            require(
                rec["sigmas"] == sigmas
                and rec["seed"] == config["seeds_by_frame"][str(f)],
                "Schedule differs",
            )
            require(rec["parent_sha256"] == sha(parent), "Parent differs")
            require(
                rec["initialization_sha256"] == sha(source) == sha(run / "anchor.png"),
                "Input differs",
            )
            require(
                rec["output_sha256"] == sha(target) == sha(run / "frames/0000.png"),
                "Output differs",
            )
            require(
                read(run / "frame-hashes.json") == {"0000.png": sha(target)},
                "Frame hash record differs",
            )
            require(
                np.array_equal(
                    pixels(source),
                    warp_at_time(
                        pixels(parent), previous / FPS, f / FPS, config["phrases"]
                    ),
                ),
                "Warp pixels differ",
            )
            executed = read(run / "workflow.executed.json")
            prompt_id, _ = validate_execution(
                graph,
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
            with Image.open(target) as im:
                require(
                    json.loads(im.info["prompt"]) == embedded, "PNG provenance differs"
                )
            jobs.append(
                {
                    "case": case,
                    "frame": f,
                    "prompt_id": prompt_id,
                    "run": rec["run"],
                    "parent_sha256": sha(parent),
                    "initialization_sha256": sha(source),
                    "output_sha256": sha(target),
                }
            )
            measurements.append(
                {
                    "case": case,
                    "frame": f,
                    "seconds": f / FPS,
                    "sigma_start": sigmas[0],
                    "change_from_warped_input": float(
                        np.abs(
                            pixels(source).astype(float) - pixels(target).astype(float)
                        ).mean()
                        / 255
                    ),
                }
            )
    expected = sum(
        sum(
            f > read(OUT / c / "config.json")["prefix_through"]
            for f in read(OUT / c / "config.json")["painting_frames"]
        )
        for c in CASES
    )
    require(
        len(jobs) == len({r["prompt_id"] for r in jobs}) == expected,
        "Job count differs",
    )
    save(
        OUT / "checks" / f"{BATCH}-generation.json",
        {"verified": True, "jobs": jobs, "measurements": measurements},
    )
    print("Verified", len(jobs), "jobs, warped pixels and parent lineage.")


def finish(stage):
    for case in CASES:
        root = OUT / case
        config = read(root / "config.json")
        positions = config["painting_frames"]
        count = round(config["duration"] * FPS)
        section = root / "finish"
        source = section / "sources"
        for i, f in enumerate(positions):
            copy_verified(root / f"anchors/{f:04d}.png", source / f"{i:04d}.png")
        save(section / "anchor-frames.json", positions)
        target = section / ("pair" if stage == "pair" else "rife")
        require(
            not target.exists(), "Choose a new output rather than overwrite a finish"
        )
        args = [
            str(PATHS.rife_python),
            str(PATHS.rife_script),
            str(source),
            str(target),
            "--source-frames",
            str(len(positions)),
            "--anchor-frames",
            str(section / "anchor-frames.json"),
            "--output-fps",
            str(FPS),
            "--frame-count",
            str(count),
        ]
        args += (
            ["--pair-only"]
            if stage == "pair"
            else ["--validated-pair", str(section / "pair/manifest.json")]
        )
        subprocess.run(args, check=True)


def delivery():
    rows = []
    for case in CASES:
        root = OUT / case
        target = root / "finish/rife"
        m = read(target / "manifest.json")
        config = read(root / "config.json")
        positions = config["painting_frames"]
        count = round(config["duration"] * FPS)
        require(
            m["status"] == "complete"
            and m["video_sha256"] == sha(target / "preview.mp4"),
            "Incomplete delivery",
        )
        require(
            m["settings"]["output_fps"] == FPS
            and m["settings"]["anchor_frames"] == positions,
            "Timeline settings differ",
        )
        require(
            m["provenance"]["model"] == "RIFE 4.25" and m["settings"]["scale"] == 1,
            "RIFE changed",
        )
        require(
            len(m["output_frames"]) == count
            and m["final_holds"] == count - positions[-1] - 1,
            "Frame count differs",
        )
        require(
            [r["index"] for r in m["output_frames"] if r["kind"] == "anchor"]
            == positions,
            "Anchor positions differ",
        )
        for row in m["output_frames"]:
            p = target / row["file"]
            f = row["index"]
            require(
                sha(p) == row["sha256"] and row["time_seconds"] == f / FPS,
                "Frame hash/time differs",
            )
            if row["kind"] == "interpolation":
                a, b = [positions[i] for i in row["source_pair"]]
                require(
                    row["timestep"] == f"{f - a}/{b - a}",
                    "Interpolation fraction differs",
                )
            else:
                require(
                    sha(p)
                    == sha(root / f"anchors/{positions[row['source_index']]:04d}.png"),
                    "Anchor/hold changed",
                )
        require(
            np.array_equal(
                pixels(root / f"anchors/{positions[-1]:04d}.png"),
                warp_at_time(
                    pixels(root / f"anchors/{positions[-1]:04d}.png"),
                    positions[-1] / FPS,
                    count / FPS,
                    read(root / "config.json")["phrases"],
                ),
            ),
            "Final motion is not settled",
        )
        subprocess.run(
            [
                "ffmpeg",
                "-v",
                "error",
                "-xerror",
                "-i",
                str(target / "preview.mp4"),
                "-f",
                "null",
                "-",
            ],
            check=True,
        )
        rows.append(
            {
                "case": case,
                "paintings": len(positions),
                "frames": count,
                "fps": FPS,
                "video_sha256": m["video_sha256"],
            }
        )
    save(OUT / "checks" / f"{BATCH}-delivery.json", {"verified": True, "rows": rows})
    print("Verified delivery counts, all anchor pixels and timestamps.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "stage", choices=["prepare", "render", "check", "pair", "full", "delivery"]
    )
    parser.add_argument("--deployment", type=Path)
    parser.add_argument("--cases", nargs="+", required=True)
    parser.add_argument("--batch", required=True)
    args = parser.parse_args()
    CASES = args.cases
    BATCH = args.batch
    if args.stage == "prepare":
        prepare()
    elif args.stage == "render":
        if not args.deployment:
            parser.error("--deployment required")
        render(args.deployment)
    elif args.stage == "check":
        check()
    elif args.stage == "delivery":
        delivery()
    else:
        finish(args.stage)
