"""Nine fixed-input probes: starting noise response, not a video feedback loop."""

import argparse
import copy
from pathlib import Path

import numpy as np
import run as lab
from PIL import Image, ImageDraw

from deforum_lab.infrastructure.pod import PodClient
from deforum_lab.records import read, require, save, sha
from deforum_lab.rendering.graphs import repaint_graph
from deforum_lab.rendering.schedules import recipe
from deforum_lab.rendering.verification import validate_execution

LEVELS = (0.60, 0.62, 0.64, 0.64624, 0.66, 0.68, 0.70, 0.72, 0.74)
ROOT = lab.OUT / "noise-response"
SOURCE = lab.OUT / "r1-current/warped-inputs/0084.png"
PARENT = lab.OUT / "r1-current/anchors/0078.png"


def graph_at(noise):
    config = read(lab.HERE / "configs/r1-current.json")
    config["noise_schedule"] = [{"at": 0, "noise": noise}]
    scene, sigmas = recipe(config, 3.5)
    graph = repaint_graph(scene["prompt"], config["seeds_by_frame"]["84"], sigmas)
    graph["11"]["inputs"]["filename_prefix"] = f"two-hour-lab/noise-response/{noise}"
    return graph


def execute(deployment):
    client = PodClient.from_path(deployment)
    rows = []
    for noise in LEVELS:
        graph = graph_at(noise)
        run = client.submit_once(
            lab.OUT,
            f"two-hour-lab-noise-response-{noise}",
            graph,
            SOURCE,
            {"parent_sha256": sha(PARENT), "initialization_sha256": sha(SOURCE)},
        )
        row = {
            "noise": noise,
            "run": str(run.relative_to(lab.OUT)),
            "output_sha256": sha(run / "frames/0000.png"),
        }
        save(ROOT / f"noise-{noise}.json", row)
        rows.append(row)
    save(ROOT / "runs.json", rows)


def check():
    rows = read(ROOT / "runs.json")
    require([r["noise"] for r in rows] == list(LEVELS), "Noise inventory differs")
    jobs, measurements = [], []
    previous = None
    for row in rows:
        run = lab.OUT / row["run"]
        graph = graph_at(row["noise"])
        require(read(run / "workflow.api.json") == graph, "Requested graph differs")
        pid, _ = validate_execution(
            graph,
            read(run / "workflow.executed.json"),
            read(run / "upload.json"),
            read(run / "history.json"),
            read(run / "submit-response.json"),
            read(run / "submission.json"),
            sha(PARENT),
            sha(SOURCE),
        )
        require(sha(run / "anchor.png") == sha(SOURCE), "Fixed input differs")
        output = run / "frames/0000.png"
        require(sha(output) == row["output_sha256"], "Output differs")
        embedded = copy.deepcopy(read(run / "workflow.executed.json"))
        embedded["20"]["is_changed"] = [sha(SOURCE)]
        with Image.open(output) as im:
            import json

            require(json.loads(im.info["prompt"]) == embedded, "PNG provenance differs")
        rgb = lab.pixels(output).astype(float) / 255
        if row["noise"] == 0.64624:
            require(
                np.array_equal(
                    lab.pixels(output),
                    lab.pixels(lab.OUT / "r1-current/anchors/0084.png"),
                ),
                "Recorded control does not replay",
            )
        measurements.append(
            {
                "noise": row["noise"],
                "change_from_fixed_input": float(
                    np.abs(rgb - lab.pixels(SOURCE) / 255).mean()
                ),
                "change_from_previous_level": None
                if previous is None
                else float(np.abs(rgb - previous).mean()),
            }
        )
        previous = rgb
        jobs.append(pid)
    require(len(jobs) == len(set(jobs)) == len(LEVELS), "Job identity differs")
    save(
        ROOT / "verification.json",
        {
            "verified": True,
            "control_pixel_parity": True,
            "jobs": jobs,
            "measurements": measurements,
            "interpretation": "Fixed-input noise response; not recurrent time steps",
        },
    )
    print("Verified nine fixed-input probes and exact recorded-control pixels.")


def sheet():
    rows = read(ROOT / "runs.json")
    canvas = Image.new("RGB", (1536, 1107), "#171717")
    draw = ImageDraw.Draw(canvas)
    for i, row in enumerate(rows):
        x, y = i % 3 * 512, i // 3 * 369
        draw.text(
            (x + 8, y + 7),
            f"Starting noise {row['noise']} · same input / seed / prompt",
            fill="white",
        )
        image = Image.open(lab.OUT / row["run"] / "frames/0000.png").convert("RGB")
        image.thumbnail((512, 341))
        canvas.paste(image, (x, y + 28))
    canvas.save(ROOT / "comparison.jpg", quality=94)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("stage", choices=["render", "check", "sheet"])
    parser.add_argument("--deployment", type=Path)
    args = parser.parse_args()
    if args.stage == "render":
        if not args.deployment:
            parser.error("--deployment required")
        execute(args.deployment)
    elif args.stage == "check":
        check()
    else:
        sheet()
