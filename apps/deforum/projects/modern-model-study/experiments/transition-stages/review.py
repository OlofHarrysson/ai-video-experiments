"""Painting pages and matched delivery frames for the descriptive-stage comparison."""

import argparse
import json
import subprocess
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from deforum_lab.media.sheets import sheet

OUT = Path(__file__).resolve().parents[2] / "exports/transition-stages-v001"
CASES = (("control", "Current descriptions"), ("stages", "Smaller described stages"))
CAP_CASES = (
    ("stages", "Stages / original peak"),
    ("stages-capped", "Stages / lower peak"),
)


def pages(frames, folder, prefix, cases=CASES):
    for start in range(0, len(frames), 4):
        rows = [
            [
                (
                    Image.open(OUT / case / folder / f"{frame:04d}.png"),
                    f"{label} | frame {frame} | {frame / 24:.3f}s",
                )
                for case, label in cases
            ]
            for frame in frames[start : start + 4]
        ]
        sheet(rows, OUT / f"review/{prefix}-{start // 4 + 1}.jpg")


def paintings():
    positions = json.loads((OUT / "control/config.json").read_text())["painting_frames"]
    pages(positions, "anchors", "control-stages")
    pages([84, 90, 96, 108, 120, 144, 168, 180], "anchors", "stages-cap", CAP_CASES)


def delivery():
    pages(list(range(78, 97)), "finish/rife/frames", "delivery-78-96")
    pages(list(range(84, 97)), "finish/rife/frames", "cap-delivery-84-96", CAP_CASES)
    pages(
        [54, 66, 78, 90, 108, 120, 156, 191], "finish/rife/frames", "delivery-samples"
    )
    header = OUT / "review/comparison-header.png"
    im = Image.new("RGB", (1536, 30), "#181818")
    d = ImageDraw.Draw(im)
    font = ImageFont.load_default(size=20)
    d.text((12, 4), "CURRENT DESCRIPTIONS", fill="white", font=font)
    d.text((780, 4), "SMALLER DESCRIBED STAGES", fill="white", font=font)
    im.save(header)
    video = OUT / "comparison.mp4"
    if not video.exists():
        subprocess.run(
            [
                "ffmpeg",
                "-v",
                "error",
                "-n",
                "-loop",
                "1",
                "-framerate",
                "24",
                "-i",
                str(header),
                "-i",
                str(OUT / "control/finish/rife/preview.mp4"),
                "-i",
                str(OUT / "stages/finish/rife/preview.mp4"),
                "-filter_complex",
                "[1:v]scale=768:512[l];[2:v]scale=768:512[r];[l][r]hstack[v];[0:v][v]vstack[out]",
                "-map",
                "[out]",
                "-frames:v",
                "192",
                "-an",
                "-c:v",
                "libx264",
                "-crf",
                "18",
                "-pix_fmt",
                "yuv420p",
                "-movflags",
                "+faststart",
                str(video),
            ],
            check=True,
        )
    subprocess.run(
        ["ffmpeg", "-v", "error", "-xerror", "-i", str(video), "-f", "null", "-"],
        check=True,
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("stage", choices=("paintings", "delivery"))
    args = parser.parse_args()
    (paintings if args.stage == "paintings" else delivery)()
