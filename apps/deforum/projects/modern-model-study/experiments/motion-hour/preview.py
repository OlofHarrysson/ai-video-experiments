"""Preview only the prescribed spatial transform, sampling the original sheet."""

import argparse
import json
import subprocess

import numpy as np
from PIL import Image
from run import HERE, lab

from deforum_lab.image.warps import warp_at_time
from deforum_lab.media.sheets import sheet


def preview(case, start_frame=0):
    config = json.loads((HERE / "configs" / f"{case}.json").read_text())
    original = lab.APP / config["prefix_root"] / f"anchors/{start_frame:04d}.png"
    image = Image.open(original).convert("RGB")
    image.thumbnail((720, 480))
    rgb = np.asarray(image)
    out = lab.OUT / "motion-only" / case
    if start_frame:
        out = out / f"from-{start_frame:04d}"
    out.mkdir(parents=True, exist_ok=True)
    h, w = rgb.shape[:2]
    process = subprocess.Popen(
        [
            "ffmpeg",
            "-v",
            "error",
            "-f",
            "rawvideo",
            "-pix_fmt",
            "rgb24",
            "-s",
            f"{w}x{h}",
            "-r",
            "24",
            "-i",
            "-",
            "-c:v",
            "libx264",
            "-pix_fmt",
            "yuv420p",
            "-crf",
            "19",
            "-movflags",
            "+faststart",
            "-y",
            str(out / "preview.mp4"),
        ],
        stdin=subprocess.PIPE,
    )
    samples = []
    for frame in range(start_frame, round(config["duration"] * 24)):
        warped = warp_at_time(rgb, start_frame / 24, frame / 24, config["phrases"])
        process.stdin.write(warped.tobytes())
        if frame in (0, 48, 96, 144, 192, 240, 288, 312):
            pic = Image.fromarray(warped)
            pic.save(out / f"{frame:04d}.png")
            samples.append((pic, f"{case} · {frame / 24:g}s · spatial transform only"))
    process.stdin.close()
    assert process.wait() == 0
    sheet(
        [samples[i : i + 2] for i in range(0, len(samples), 2)],
        out / "overview.jpg",
        size=(576, 384),
    )
    print(out, flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("cases", nargs="+")
    parser.add_argument("--from-frame", type=int, default=0)
    args = parser.parse_args()
    for name in args.cases:
        preview(name, args.from_frame)
