"""Reuse the audited two-hour runner with this experiment's paths and cases."""

import argparse
import importlib.util
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location(
    "two_hour_runner", HERE.parent / "two-hour-lab/run.py"
)
lab = importlib.util.module_from_spec(spec)
spec.loader.exec_module(lab)
lab.HERE = HERE
lab.OUT = HERE.parents[1] / "exports/doorway-revision-v001"

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "stage",
        choices=["opening", "prepare", "render", "check", "pair", "full", "delivery"],
    )
    parser.add_argument("--cases", nargs="+", required=True)
    parser.add_argument("--batch", required=True)
    parser.add_argument("--deployment", type=Path)
    parser.add_argument("--last-frame", type=int)
    args = parser.parse_args()
    lab.CASES, lab.BATCH = args.cases, args.batch
    if args.stage in ("opening", "render"):
        if not args.deployment:
            parser.error("--deployment required")
        if args.stage == "opening":
            lab.openings(args.deployment)
        else:
            lab.render(args.deployment, args.last_frame)
    elif args.stage in ("pair", "full"):
        lab.finish(args.stage)
    else:
        getattr(lab, args.stage)()
