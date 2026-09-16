"""Bounded painting sheets and spatial previews for this art session."""

import argparse
import subprocess

import numpy as np
from PIL import Image
from run import HERE, lab

from deforum_lab.image.warps import warp_at_time
from deforum_lab.media.sheets import sheet


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=["paintings", "motion"])
    parser.add_argument("case")
    parser.add_argument("--frames", type=int, nargs="+")
    parser.add_argument("--start", type=int, default=0)
    parser.add_argument("--tag", default="overview")
    args = parser.parse_args()
    config = lab.read(HERE / "configs" / f"{args.case}.json")
    target = lab.OUT / "review" / f"{args.case}-{args.tag}"
    target.mkdir(parents=True, exist_ok=True)
    if args.mode == "paintings":
        frames = args.frames or config["painting_frames"]
        for offset in range(0, len(frames), 6):
            tiles = []
            for frame in frames[offset : offset + 6]:
                path = lab.OUT / args.case / f"anchors/{frame:04d}.png"
                with Image.open(path) as im:
                    tiles.append(
                        (
                            im.convert("RGB"),
                            f"{args.case} | source {frame / 24:g}s | {frame}",
                        )
                    )
            out = target / f"{offset // 6 + 1:02d}.jpg"
            sheet(
                [tiles[i : i + 2] for i in range(0, len(tiles), 2)],
                out,
                size=(640, 426),
            )
            print(out)
        return
    image_path = lab.APP / config["prefix_root"] / f"anchors/{args.start:04d}.png"
    with Image.open(image_path) as im:
        image = im.convert("RGB")
        image.thumbnail((720, 480))
        rgb = np.asarray(image)
    out = target / "motion.mp4"
    lab.require(not out.exists(), "Preserve earlier spatial previews")
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
            "-an",
            "-c:v",
            "libx264",
            "-pix_fmt",
            "yuv420p",
            "-crf",
            "19",
            "-movflags",
            "+faststart",
            str(out),
        ],
        stdin=subprocess.PIPE,
    )
    tiles = []
    count = round((config["duration"] * 24 - args.start) / 1.5)
    for frame in range(count):
        seconds = (args.start + 1.5 * frame) / 24
        warped = warp_at_time(rgb, args.start / 24, seconds, config["phrases"])
        process.stdin.write(warped.tobytes())
        if frame in set(np.linspace(0, count - 1, 6).round().astype(int)):
            tiles.append(
                (Image.fromarray(warped), f"source {seconds:.2f}s | motion only")
            )
    process.stdin.close()
    lab.require(process.wait() == 0, "Spatial preview failed")
    sheet(
        [tiles[i : i + 2] for i in range(0, len(tiles), 2)],
        target / "motion.jpg",
        size=(640, 426),
    )
    lab.save(target / "config.json", config)
    print(target)


if __name__ == "__main__":
    main()
