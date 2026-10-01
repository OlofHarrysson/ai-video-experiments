"""Preserve 32 guided paintings at their authored times; fill gaps with RIFE."""

import argparse
import subprocess
from pathlib import Path

from deforum_lab.records import copy_verified, require, save, sha

APP = Path(__file__).resolve().parents[3]
OUT = APP / "projects/rainbow-mane/exports/guided-morph-v001"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("case")
    parser.add_argument("stage", choices=["pair", "full"])
    args = parser.parse_args()
    require(Path(args.case).name == args.case, "Expected a case name")
    root = OUT / args.case
    rows = []
    for i, frame in enumerate(range(0, 96, 3)):
        original = root / "anchors" / f"{frame:04d}.png"
        require(original.exists(), f"Missing painting {frame}")
        target = root / "rife-sources" / f"{i:04d}.png"
        copy_verified(original, target)
        rows.append(
            {
                "source_frame": frame,
                "delivery_frame": frame,
                "sha256": sha(original),
                "copy": str(target.relative_to(root)),
            }
        )
    save(
        root / "timing.json",
        {
            "fps": 24,
            "frames": 96,
            "paintings": rows,
            "camera": "fixed",
            "speed_multiplier": 1,
            "interpolation_feeds_recurrence": False,
        },
    )
    command = [
        str(APP / "work/rife-session/.venv/bin/python"),
        str(APP / "interpolate.py"),
        str(root / "rife-sources"),
        str(root / ("rife-pair" if args.stage == "pair" else "rife")),
        "--source-frames",
        "32",
        "--source-fps",
        "8",
        "--multiplier",
        "3",
    ]
    if args.stage == "pair":
        command += ["--pair-only"]
    else:
        command += ["--validated-pair", str(root / "rife-pair/manifest.json")]
    subprocess.run(command, check=True)


if __name__ == "__main__":
    main()
