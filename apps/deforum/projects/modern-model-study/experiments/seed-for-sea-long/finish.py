"""Finish only the new passage; preserve its overlap for a continuous edit."""

import argparse

from run import lab, moving_tail, retiming


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("case")
    args = parser.parse_args()
    config = lab.read(lab.OUT / args.case / "config.json")
    start = config["prefix_through"]
    for stage in ("pair", "full", "check"):
        retiming.retime(args.case, stage, first_frame=start)
    moving_tail.finish(args.case, first_frame=start)


if __name__ == "__main__":
    main()
