"""Preview a planned camera move on one actual painting, without inference."""

import argparse
import json
import subprocess
from pathlib import Path

import numpy as np
from PIL import Image

from deforum_lab.image.warps import warp_at_time
from deforum_lab.records import read, require, save, sha

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parent
APP = HERE.parents[2]
FPS = 24
SPEED = 1.5


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("case")
    parser.add_argument("--until", type=float, required=True, help="Source seconds")
    parser.add_argument("--output", type=Path, help="New directory for a longer preview")
    args = parser.parse_args()
    config = read(HERE / "configs" / f"{args.case}.json")
    frame = config["prefix_through"]
    source = APP / config["prefix_root"] / f"anchors/{frame:04d}.png"
    start = frame / FPS
    count = round((args.until - start) * FPS / SPEED)
    require(count > 0, "Preview must extend the source painting")
    root = args.output or PROJECT / "exports/motion-previews" / args.case
    require(not root.exists(), "Preserve existing motion previews")
    root.mkdir(parents=True)
    with Image.open(source) as image:
        rgb = np.asarray(
            image.convert("RGB").resize((768, 512), Image.Resampling.LANCZOS)
        )
    command = [
        "ffmpeg",
        "-v",
        "error",
        "-f",
        "rawvideo",
        "-pixel_format",
        "rgb24",
        "-video_size",
        "768x512",
        "-framerate",
        str(FPS),
        "-i",
        "-",
        "-an",
        "-c:v",
        "libx264",
        "-crf",
        "18",
        "-pix_fmt",
        "yuv420p",
        "-movflags",
        "+faststart",
        str(root / "preview.mp4"),
    ]
    with subprocess.Popen(command, stdin=subprocess.PIPE) as encoder:
        for index in range(count):
            warped = warp_at_time(
                rgb, start, start + index * SPEED / FPS, config["phrases"]
            )
            encoder.stdin.write(warped.tobytes())
        encoder.stdin.close()
        require(encoder.wait() == 0, "Preview encoding failed")
    save(
        root / "preview.json",
        {
            "source": str(source.relative_to(APP)),
            "source_sha256": sha(source),
            "config": config,
            "source_start_seconds": start,
            "source_end_seconds": args.until,
            "speed_multiplier": SPEED,
            "fps": FPS,
            "frames": count,
            "inference_jobs": 0,
            "limitation": "Warps one painting; does not predict repainting or newly revealed content.",
            "video_sha256": sha(root / "preview.mp4"),
        },
    )
    print(json.dumps({"preview": str(root / "preview.mp4")}))


if __name__ == "__main__":
    main()
