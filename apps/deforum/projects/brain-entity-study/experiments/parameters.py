"""Run one explicitly recorded change against an immutable parent workflow.

Run from apps/deforum using uv run --env-file .env python PATH --help.
"""

import argparse
import hashlib
import json
from pathlib import Path
import sys

APP = Path(__file__).resolve().parents[3]
PROJECT = Path(__file__).resolve().parents[1]
BASELINE = "20260907T072631982593Z-feedback-v002-48f"
sys.path.insert(0, str(APP))
import serverless_client


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("label")
    p.add_argument("--parent", default=BASELINE)
    p.add_argument("--control", type=float)
    p.add_argument("--denoise", type=float)
    p.add_argument("--steps", type=int)
    p.add_argument("--cfg", type=float)
    p.add_argument("--noise", type=float)
    p.add_argument("--sharpen", type=float)
    p.add_argument("--coherence", type=float)
    p.add_argument("--cadence", type=int)
    p.add_argument("--seed-mode", choices=("fixed", "increment"))
    p.add_argument("--constant-prompt", action="store_true",
                   help="Keep the parent's frame-zero prompt throughout the clip")
    p.add_argument("--dry-run", action="store_true")
    args = p.parse_args()
    parent = PROJECT / "runs" / args.parent
    original = (parent / "workflow.api.json").read_bytes()
    graph = json.loads(original)
    changes = []
    mapping = {"control": "control_strength", "steps": "steps", "cfg": "cfg",
               "noise": "noise", "sharpen": "sharpen", "coherence": "color_coherence",
               "cadence": "cadence", "seed_mode": "seed_mode"}
    for option, field in mapping.items():
        value = getattr(args, option)
        if value is not None:
            old = graph["10"]["inputs"][field]
            graph["10"]["inputs"][field] = value
            changes.append({"node": "10", "field": field, "old": old, "new": value})
    if args.denoise is not None:
        old = graph["9"]["inputs"]["schedule"]
        graph["9"]["inputs"]["schedule"] = f"0:({args.denoise})"
        changes.append({"node": "9", "field": "schedule", "old": old,
                        "new": graph["9"]["inputs"]["schedule"]})
    if args.constant_prompt:
        old = graph["12"]["inputs"]["prompts"]
        first = old.splitlines()[0]
        if not first.startswith("0:"):
            p.error("Constant-prompt comparison requires a frame-zero prompt")
        graph["12"]["inputs"]["prompts"] = first
        changes.append({"node": "12", "field": "prompts", "old": old, "new": first})
    if not changes:
        p.error("Provide at least one explicit parameter change")
    receipt = {"parent_run": args.parent, "parent_workflow_sha256": hashlib.sha256(original).hexdigest(),
               "changes": changes, "study": "feedback-parameters"}
    print(json.dumps(receipt, indent=2), flush=True)
    if args.dry_run:
        return
    serverless_client.submit(PROJECT, args.label, graph, graph["7"]["inputs"]["max_frames"],
                             lineage=receipt, source=parent / "anchor.png")


if __name__ == "__main__":
    main()
