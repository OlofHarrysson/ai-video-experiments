"""Finish The Glass Tide with retained paintings and a moving tail."""

import argparse
from pathlib import Path

from deforum_lab.media.retiming import RetimedDelivery

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parent
APP = HERE.parents[2]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("case")
    parser.add_argument("stage", choices=["pair", "full", "check", "tail"])
    parser.add_argument("--version", choices=["v001", "v002"], default="v001")
    parser.add_argument(
        "--through-frame",
        type=int,
        help="Last source painting frame; default: all paintings",
    )
    args = parser.parse_args()
    delivery = RetimedDelivery(APP, PROJECT)
    _, root, config, timing = delivery.prepare(
        args.case, args.through_frame, args.stage in ("pair", "full"), args.version
    )
    if args.stage in ("pair", "full"):
        delivery.interpolate(root, timing, config, args.stage)
    elif args.stage == "tail":
        delivery.tail(root, timing, config)
    else:
        delivery.verify(root, timing, config, "rife")
        if (root / "rife-moving-tail").exists():
            delivery.verify(root, timing, config, "rife-moving-tail")
    delivery.prepare(args.case, args.through_frame, False, args.version)
    print(f"Verified {args.stage}: {root}", flush=True)


if __name__ == "__main__":
    main()
