"""Verify native text-blend endpoints on one fixed recurrent input."""

import argparse
import json
from pathlib import Path

import numpy as np
import run as lab
from PIL import Image

from deforum_lab.infrastructure.pod import PodClient
from deforum_lab.records import save, sha
from deforum_lab.rendering.graphs import node, repaint_graph
from deforum_lab.rendering.schedules import recipe
from deforum_lab.rendering.verification import validate_execution


def execute(deployment):
    config = json.loads((lab.HERE / "configs/r4-blend.json").read_text())
    client = PodClient.from_path(deployment)
    root = lab.OUT / "conditioning-probe"
    source = lab.OUT / "r1-plateau060/warped-inputs/0054.png"
    parent = lab.OUT / "r1-plateau060/anchors/0048.png"
    sigmas = recipe(config, 2.25)[1]
    seed = config["seeds_by_frame"]["54"]
    rows = []
    for label, alpha, mode in [
        ("old-direct", 0, "direct"),
        ("old-blend", 0, "average"),
        ("new-direct", 1, "direct"),
        ("new-blend", 1, "average"),
        ("old-empty-negative", 0, "empty"),
    ]:
        prompt = config["conditioning_blend"]["new" if alpha else "old"]
        graph = repaint_graph(prompt, seed, sigmas)
        if mode == "average":
            c = json.loads(json.dumps(config))
            c["conditioning_blend"]["schedule"] = [[0, alpha], [8, alpha]]
            lab.conditioning_controls(graph, c, 2.25)
        if mode == "empty":
            graph["50"] = node("CLIPTextEncode", clip=["2", 0], text="")
            graph["9"]["inputs"]["negative"] = ["50", 0]
        graph["11"]["inputs"]["filename_prefix"] = (
            "two-hour-lab/conditioning-probe/" + label
        )
        run = client.submit_once(
            lab.OUT,
            "two-hour-lab-probe-" + label,
            graph,
            source,
            {"parent_sha256": sha(parent), "initialization_sha256": sha(source)},
        )
        record = {
            "label": label,
            "run": str(run.relative_to(lab.OUT)),
            "output_sha256": sha(run / "frames/0000.png"),
        }
        save(root / (label + ".json"), record)
        rows.append(record)
    save(root / "runs.json", rows)


def verify():
    root = lab.OUT / "conditioning-probe"
    rows = json.loads((root / "runs.json").read_text())
    images = {}
    parent = lab.OUT / "r1-plateau060/anchors/0048.png"
    source = lab.OUT / "r1-plateau060/warped-inputs/0054.png"
    jobs = []
    for row in rows:
        path = lab.OUT / row["run"]

        def read(name, run_path=path):
            return json.loads((run_path / name).read_text())

        graph = read("workflow.api.json")
        assert graph["9"]["inputs"]["cfg"] == 1 and graph["9"]["inputs"][
            "latent_image"
        ] == ["24", 0]
        prompt_id, _ = validate_execution(
            graph,
            read("workflow.executed.json"),
            read("upload.json"),
            read("history.json"),
            read("submit-response.json"),
            read("submission.json"),
            sha(parent),
            sha(source),
        )
        assert sha(path / "anchor.png") == sha(source)
        assert sha(path / "frames/0000.png") == row["output_sha256"]
        with Image.open(path / "frames/0000.png") as image:
            images[row["label"]] = np.array(image.convert("RGB"))
        jobs.append(prompt_id)
    checks = {}
    for a, b in [
        ("old-direct", "old-blend"),
        ("new-direct", "new-blend"),
        ("old-direct", "old-empty-negative"),
    ]:
        checks[a + "--" + b] = bool(np.array_equal(images[a], images[b]))
    save(
        root / "verification.json",
        {"pixel_parity": checks, "jobs": jobs, "verified": all(checks.values())},
    )
    print(json.dumps(checks))
    assert all(checks.values()), (
        "Endpoint or CFG1 negative parity failed; do not run the blend experiment"
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("stage", choices=["render", "check"])
    parser.add_argument("--deployment", type=Path)
    args = parser.parse_args()
    if args.stage == "render":
        if not args.deployment:
            parser.error("--deployment required")
        execute(args.deployment)
    else:
        verify()
