# /// script
# requires-python = ">=3.11"
# dependencies = ["pillow"]
# ///
"""Assemble held images into a clip under a pull-back that moves on every frame.

Usage, from this project folder:

    uv run --script scripts/assemble.py OUTPUT.mp4 IMAGE [IMAGE ...] [--anchor X Y] [--start 0.62] [--end 1.0]

Each image is held for FRAMES_PER_IMAGE frames with no interpolation. The crop is the largest
2.4:1 window scaled from --start to --end with an ease-in-out, and its centre travels from the
anchor (fractions of image width and height) to the image centre.
"""

import argparse
import subprocess
from pathlib import Path

from PIL import Image

FPS = 24
FRAMES_PER_IMAGE = 2
SIZE = (1920, 800)


def smoothstep(t: float) -> float:
    return t * t * (3 - 2 * t)


def crop_box(width: int, height: int, scale: float, anchor: tuple[float, float], t: float) -> tuple[float, ...]:
    aspect = SIZE[0] / SIZE[1]
    crop_width = min(width, height * aspect) * scale
    crop_height = crop_width / aspect
    centre_x = anchor[0] * width + (width / 2 - anchor[0] * width) * t
    centre_y = anchor[1] * height + (height / 2 - anchor[1] * height) * t
    left = min(max(centre_x - crop_width / 2, 0), width - crop_width)
    top = min(max(centre_y - crop_height / 2, 0), height - crop_height)
    return (left, top, left + crop_width, top + crop_height)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("output", type=Path)
    parser.add_argument("images", type=Path, nargs="+")
    parser.add_argument("--anchor", type=float, nargs=2, default=(0.5, 0.5), metavar=("X", "Y"))
    parser.add_argument("--start", type=float, default=0.62, help="crop scale on the first frame")
    parser.add_argument("--end", type=float, default=1.0, help="crop scale on the last frame")
    args = parser.parse_args()

    frames = len(args.images) * FRAMES_PER_IMAGE
    encoder = subprocess.Popen(
        [
            "ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
            "-s", f"{SIZE[0]}x{SIZE[1]}", "-r", str(FPS), "-i", "-",
            "-c:v", "libx264", "-crf", "18", "-pix_fmt", "yuv420p", "-movflags", "+faststart",
            str(args.output),
        ],
        stdin=subprocess.PIPE,
    )
    current, image = None, None
    for frame in range(frames):
        path = args.images[frame // FRAMES_PER_IMAGE]
        if path != current:
            current, image = path, Image.open(path).convert("RGB")
        t = smoothstep(frame / max(frames - 1, 1))
        scale = args.start + (args.end - args.start) * t
        box = crop_box(image.width, image.height, scale, tuple(args.anchor), t)
        encoder.stdin.write(image.resize(SIZE, Image.Resampling.LANCZOS, box=box).tobytes())
    encoder.stdin.close()
    if encoder.wait() != 0:
        raise SystemExit("ffmpeg failed")
    print(f"{args.output}: {len(args.images)} images, {frames} frames, {frames / FPS:.2f} s")


if __name__ == "__main__":
    main()
