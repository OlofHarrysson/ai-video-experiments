"""A bounded, resumable Krea prompt matrix using the native graph and receipts."""

import argparse
import json
from pathlib import Path

from PIL import Image

from deforum_lab.infrastructure.pod import PodClient
from deforum_lab.records import copy_verified, read, require, save, sha
from deforum_lab.rendering.graphs import graph

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parents[1]
OUT = PROJECT / "exports/v002/prompt-study"


def make_graph(case):
    result = graph("krea", case["prompt"], case["seed"])
    result["6"]["inputs"].update(width=case.get("width", 1536), height=case.get("height", 1024))
    result["11"]["inputs"]["filename_prefix"] = "world-seed/prompt-study/" + case["id"]
    return result


def check(case):
    root = OUT / case["id"]
    receipt = read(root / "opening.json")
    run = OUT / receipt["run"]
    expected = make_graph(case)
    require(read(root / "case.json") == case, "Frozen case differs")
    require(read(run / "workflow.executed.json") == read(run / "workflow.api.json") == expected, "Graph differs")
    history = read(run / "history.json")
    require(history["status"]["completed"] and history["status"]["status_str"] == "success", "Job failed")
    require(history["prompt"][2] == expected, "History graph differs")
    require(history["prompt"][1] == read(run / "submission.json")["prompt_id"], "Job identity differs")
    target = root / "anchors/0000.png"
    require(sha(target) == receipt["sha256"] == sha(run / "frames/0000.png"), "Image differs")
    with Image.open(target) as im:
        require(json.loads(im.info["prompt"]) == expected, "Embedded graph differs")
        require(im.size == (case.get("width", 1536), case.get("height", 1024)), "Dimensions differ")
    return {"id": case["id"], "sha256": sha(target), "prompt_id": history["prompt"][1]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("stage", choices=["render", "check"])
    parser.add_argument("matrix", type=Path)
    parser.add_argument("--deployment", type=Path)
    parser.add_argument("--ids", nargs="+")
    args = parser.parse_args()
    cases = read(args.matrix)["cases"]
    if args.ids:
        cases = [case for case in cases if case["id"] in args.ids]
        require(len(cases) == len(args.ids), "Unknown or duplicate case id")
    require(len({case["id"] for case in cases}) == len(cases), "Duplicate cases")
    rows = []
    for case in cases:
        require(Path(case["id"]).name == case["id"], "Invalid id")
        if args.stage == "render":
            require(args.deployment is not None, "Explicit deployment required")
            root = OUT / case["id"]
            frozen = root / "case.json"
            if frozen.exists():
                require(read(frozen) == case, "Immutable case differs")
            save(frozen, case)
            run = PodClient.from_path(args.deployment).submit_once(OUT, "prompt-study-" + case["id"], make_graph(case))
            copy_verified(run / "frames/0000.png", root / "anchors/0000.png")
            save(root / "opening.json", {"run": str(run.relative_to(OUT)), "sha256": sha(root / "anchors/0000.png")})
        rows.append(check(case))
        print("Verified " + case["id"], flush=True)
    save(OUT / (args.matrix.stem + "-check.json"), {"verified": True, "cases": rows})


if __name__ == "__main__":
    main()
