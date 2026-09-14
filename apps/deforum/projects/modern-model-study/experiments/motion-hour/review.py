"""Produce bounded pages of matched paintings for first-pass visual review."""

import argparse
from pathlib import Path

from PIL import Image

from deforum_lab.media.sheets import sheet

HERE = Path(__file__).resolve().parent
OUT = HERE.parents[1] / "exports/motion-hour-v001"

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("left")
    parser.add_argument("right")
    parser.add_argument(
        "--frames",
        type=int,
        nargs="+",
        default=[54, 60, 66, 72, 78, 84, 90, 96, 108, 132, 180],
    )
    parser.add_argument("--finishing", action="store_true")
    args = parser.parse_args()
    dest = (
        OUT
        / "review"
        / (args.left + "--" + args.right + ("-rife" if args.finishing else ""))
    )
    for offset in range(0, len(args.frames), 3):
        rows = []
        for frame in args.frames[offset : offset + 3]:
            pair = []
            for case in [args.left, args.right]:
                p = (
                    OUT
                    / case
                    / ("finish/rife/frames" if args.finishing else "anchors")
                    / f"{frame:04d}.png"
                )
                with Image.open(p) as image:
                    pair.append(
                        (
                            image.convert("RGB"),
                            f"{case} · {frame / 24:.3f}s · frame {frame}",
                        )
                    )
            rows.append(pair)
        target = dest / f"page-{offset // 3 + 1:02d}.jpg"
        sheet(rows, target, size=(576, 384))
        print(target)
