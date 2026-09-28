"""Export a diagnostic guide / initialization / diffusion comparison, no interpolation."""

import argparse
import json
import subprocess
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).parent

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("name")
    args = parser.parse_args()
    folder = ROOT / "exports/sequences" / args.name
    config = json.loads((folder / "sequence.json").read_text())
    panels = folder / "comparison-frames"
    panels.mkdir(exist_ok=True)
    for i in range(config["frames"]):
        canvas = Image.new("RGB", (1152, 252), "#18202a")
        draw = ImageDraw.Draw(canvas)
        guide = Image.new("RGBA", (1024, 576), "#52606d")
        if config["kind"] != "none":
            guide = Image.alpha_composite(
                guide,
                Image.open(
                    ROOT / f"references/assets/{config['kind']}/{i:03d}.png"
                ).convert("RGBA"),
            )
        images = [
            guide,
            Image.open(folder / f"injected/{i:03d}.png"),
            Image.open(folder / f"frames/{i:03d}.png"),
        ]
        for column, (im, label) in enumerate(
            zip(
                images,
                ["REMOTION GUIDE", "BLENDED INTO PREVIOUS PAINTING", "AFTER DIFFUSION"],
            )
        ):
            canvas.paste(im.convert("RGB").resize((384, 216)), (384 * column, 0))
            draw.text((384 * column + 8, 224), label, fill="white")
        canvas.save(panels / f"{i:03d}.png")
    for source, target in [
        (panels, folder / "comparison.mp4"),
        (folder / "frames", folder / "output.mp4"),
    ]:
        subprocess.run(
            [
                "ffmpeg",
                "-v",
                "error",
                "-y",
                "-framerate",
                str(config["fps"]),
                "-i",
                str(source / "%03d.png"),
                "-c:v",
                "libx264",
                "-crf",
                "18",
                "-pix_fmt",
                "yuv420p",
                "-movflags",
                "+faststart",
                str(target),
            ],
            check=True,
        )
        print(target)
