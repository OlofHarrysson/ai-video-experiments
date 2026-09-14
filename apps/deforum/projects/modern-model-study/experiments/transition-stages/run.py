"""Descriptive intermediate forms and a bounded final noise peak."""

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
from deforum_lab.rendering.graphs import repaint_graph
from deforum_lab.rendering.schedules import recipe
from deforum_lab.rendering.verification import validate_execution

HERE = Path(__file__).resolve().parent
APP = HERE.parents[3]
PATHS = AppPaths(APP)
OUT = HERE.parents[1] / "exports/transition-stages-v001"
OLD = HERE.parents[1] / "exports/transition-frequency-v001/four-transition"
CASES = ("control", "stages", "stages-capped")
FPS, COUNT = 24, 192


def pixels(path):
    with Image.open(path) as im:
        return np.array(im.convert("RGB"))


def prepare():
    for case in CASES:
        config = read(HERE / f"{case}.json")
        save(OUT / case / "config.json", config)
        prefix = []
        for frame in (0, 12, 24, 36, 48):
            prefix.append(
                {
                    "frame": frame,
                    "source": str((OLD / f"anchors/{frame:04d}.png").relative_to(APP)),
                    "sha256": sha(OLD / f"anchors/{frame:04d}.png"),
                }
            )
            copy_verified(
                OLD / f"anchors/{frame:04d}.png",
                OUT / case / f"anchors/{frame:04d}.png",
            )
        save(OUT / case / "prefix.json", prefix)
    print("Prepared three matched cases; 45 new paintings.")


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
            first_frame=54,
            last_frame=180,
            run_prefix="transition-stages-" + case,
            filename_prefix="transition-stages/" + case,
        )


def check():
    jobs, measurements = [], []
    for case in CASES:
        root = OUT / case
        config = read(root / "config.json")
        require(config == read(HERE / f"{case}.json"), "Frozen config differs")
        positions = config["painting_frames"]
        require(
            [int(p.stem) for p in sorted((root / "anchors").glob("*.png"))]
            == positions,
            "Painting inventory differs",
        )
        for f in (0, 12, 24, 36, 48):
            require(
                sha(root / f"anchors/{f:04d}.png") == sha(OLD / f"anchors/{f:04d}.png"),
                "Prefix changed",
            )
        for previous, f in pairwise(positions):
            if f < 54:
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
            graph["11"]["inputs"]["filename_prefix"] = "transition-stages/" + case
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
    require(len(jobs) == len({r["prompt_id"] for r in jobs}) == 45, "Job count differs")
    require(
        np.array_equal(
            pixels(OUT / "stages/anchors/0084.png"),
            pixels(OUT / "stages-capped/anchors/0084.png"),
        ),
        "Matched stages before noise cap differ",
    )
    result = {
        "verified": True,
        "jobs": jobs,
        "measurements": measurements,
        "stages_before_noise_cap_pixel_identical": True,
    }
    save(OUT / "generation-check.json", result)
    print(
        "Verified all 45 jobs, actual warped pixels, parent lineage and matched stages before noise cap."
    )


def finish(stage):
    for case in CASES:
        root = OUT / case
        positions = read(root / "config.json")["painting_frames"]
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
            str(COUNT),
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
        positions = read(root / "config.json")["painting_frames"]
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
            len(m["output_frames"]) == COUNT and m["final_holds"] == 11,
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
                pixels(root / "anchors/0180.png"),
                warp_at_time(
                    pixels(root / "anchors/0180.png"),
                    7.5,
                    8,
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
                "frames": COUNT,
                "fps": FPS,
                "video_sha256": m["video_sha256"],
            }
        )
    prefix = all(
        np.array_equal(
            pixels(OUT / "control/finish/rife/frames" / f"{f:04d}.png"),
            pixels(OUT / "stages/finish/rife/frames" / f"{f:04d}.png"),
        )
        for f in range(49)
    )
    require(prefix, "Shared prefix through 2s differs")
    save(
        OUT / "delivery-check.json",
        {"verified": True, "rows": rows, "pixel_identical_prefix_through_frame": 48},
    )
    print("Verified 192 frames per case, all paintings and shared delivery through 2s.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "stage", choices=["prepare", "render", "check", "pair", "full", "delivery"]
    )
    parser.add_argument("--deployment", type=Path)
    args = parser.parse_args()
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
