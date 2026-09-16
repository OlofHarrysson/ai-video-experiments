"""Create A Seed for the Sea with the established recurrent and finishing tools."""

import argparse
import importlib.util
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location(
    "seed_sea_runner", HERE.parent / "two-hour-lab/run.py"
)
lab = importlib.util.module_from_spec(spec)
spec.loader.exec_module(lab)
sys.path.insert(0, str(HERE.parent / "doorway-revision"))
import moving_tail
import retime as retiming

moving_tail.lab = lab
retiming.lab = lab

lab.HERE = HERE
lab.OUT = HERE.parents[1] / "exports/seed-for-sea-v001"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "stage", choices=["opening", "prepare", "render", "check", "finish"]
    )
    parser.add_argument("--cases", nargs="+", required=True)
    parser.add_argument("--deployment", type=Path)
    parser.add_argument("--through-frame", type=int)
    args = parser.parse_args()
    lab.CASES, lab.BATCH = args.cases, "-".join(args.cases)
    if args.stage in ("opening", "render"):
        if args.deployment is None:
            parser.error("--deployment is required for inference")
        if args.stage == "opening":
            lab.openings(args.deployment)
        else:
            lab.render(args.deployment, args.through_frame)
    elif args.stage == "finish":
        for case in args.cases:
            for stage in ("pair", "full", "check"):
                retiming.retime(case, stage, last_frame=args.through_frame)
            moving_tail.finish(case, last_frame=args.through_frame)
    else:
        getattr(lab, args.stage)()


if __name__ == "__main__":
    main()
