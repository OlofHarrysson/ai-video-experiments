"""Generate and finish a preserved CLI branch with the existing recurrent recipe."""

import argparse
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
APP = HERE.parents[3]
sys.path.insert(0, str(HERE.parent / "doorway-revision"))
from moving_tail import finish
from retime import retime
from run import lab


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("stage", choices=["render", "check", "finish"])
    parser.add_argument("branch", type=Path, help="App-relative saved branch")
    parser.add_argument("--deployment", type=Path)
    parser.add_argument("--through-frame", type=int)
    args = parser.parse_args()
    root = (APP / args.branch).resolve()
    if not root.is_relative_to(APP / "projects/modern-model-study/branches"):
        parser.error("Expected a branch inside modern-model-study")
    config = lab.read(root / "config.json")
    frozen = HERE / "configs" / f"{root.name}.json"
    lab.require(
        config == lab.read(frozen), "Branch differs from frozen production config"
    )
    lab.HERE, lab.OUT, lab.CASES, lab.BATCH = HERE, root.parent, [root.name], root.name
    if args.stage == "render":
        if args.deployment is None:
            parser.error("--deployment is required for inference")
        lab.render(args.deployment, args.through_frame)
    elif args.stage == "check":
        lab.check()
    else:
        for stage in ("pair", "full", "check"):
            retime(root.name, stage, last_frame=args.through_frame)
        finish(root.name, last_frame=args.through_frame)


if __name__ == "__main__":
    main()
