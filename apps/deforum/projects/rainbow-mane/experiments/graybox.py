"""Render neutral relief and depth guides from the approved SVG motion."""

import argparse
import json
import re
import subprocess
import xml.etree.ElementTree as ET
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw

from deforum_lab.records import copy_verified, sha

PROJECT = Path(__file__).resolve().parents[1]
GUIDE = PROJECT / "exports/profile-morph-v002"
STYLE = PROJECT / "exports/guided-morph-v001/guided-n040-a012/anchors/0000.png"
WIDTH, HEIGHT, FPS, FRAMES, SCALE = 1280, 720, 24, 96, 2
NS = "{http://www.w3.org/2000/svg}"


def path_mask(element):
    """The authored SVG paths contain one M followed by cubic C segments."""
    values = [float(v) for v in re.findall(r"-?\d+(?:\.\d+)?", element.attrib["d"])]
    points = np.asarray(values).reshape(-1, 2)
    assert (len(points) - 1) % 3 == 0
    sampled = [points[0]]
    for i in range(1, len(points), 3):
        a, b, c, d = points[i - 1 : i + 3]
        for t in np.linspace(0, 1, 33)[1:]:
            sampled.append(
                (1 - t) ** 3 * a
                + 3 * (1 - t) ** 2 * t * b
                + 3 * (1 - t) * t * t * c
                + t**3 * d
            )
    canvas = Image.new("L", (WIDTH * SCALE, HEIGHT * SCALE))
    ImageDraw.Draw(canvas).polygon([tuple(p * SCALE) for p in sampled], fill=255)
    return np.asarray(canvas.resize((WIDTH, HEIGHT), Image.Resampling.LANCZOS)) / 255.0


def render(svg):
    root = ET.parse(svg).getroot()
    depth = np.full((HEIGHT, WIDTH), 0.04, dtype=np.float32)
    coverage = np.zeros_like(depth)
    filled = [e for e in root.findall(NS + "path") if e.attrib["fill"] != "none"]
    assert len(filled) == 9, f"Unexpected guide topology: {len(filled)}"
    # Six mane sections, far ear, head/neck, near ear. Brighter depth is nearer.
    for i, element in enumerate(filled):
        mask = path_mask(element)
        inside = (mask > 0.5).astype(np.uint8)
        distance = cv2.distanceTransform(inside, cv2.DIST_L2, 5)
        radius = 60 if i == 7 else 24
        relief = np.sqrt(np.clip(distance / radius, 0, 1))
        base, height = (
            (0.50, 0.24) if i == 7 else ((0.75, 0.09) if i == 8 else (0.32, 0.10))
        )
        surface = base + height * relief
        depth = depth * (1 - mask) + surface * mask
        coverage = np.maximum(coverage, mask)
    # Subtle eye/nostril recesses communicate feature positions without drawn ink.
    ellipses = root.findall(NS + "ellipse")
    yy, xx = np.mgrid[:HEIGHT, :WIDTH]
    for element in (ellipses[0], ellipses[-1]):
        a = element.attrib
        radius = ((xx - float(a["cx"])) / float(a["rx"])) ** 2 + (
            (yy - float(a["cy"])) / float(a["ry"])
        ) ** 2
        depth -= 0.065 * np.clip(1 - radius, 0, 1) ** 2 * coverage
    smooth = cv2.GaussianBlur(depth, (0, 0), 1.6)
    dy, dx = np.gradient(smooth * 100)
    normal = np.stack([-dx, -dy, np.ones_like(dx)], axis=2)
    normal /= np.linalg.norm(normal, axis=2, keepdims=True)
    light = np.asarray([-0.45, -0.55, 0.8])
    light /= np.linalg.norm(light)
    lambert = np.clip(normal @ light, 0, 1)
    shade = 110 + 115 * lambert
    clay = (
        np.round(shade * coverage + 58 * (1 - coverage)).clip(0, 255).astype(np.uint8)
    )
    return clay, np.round(depth * 255).clip(0, 255).astype(np.uint8)


def encode(folder, output):
    subprocess.run(
        [
            "ffmpeg",
            "-hide_banner",
            "-loglevel",
            "error",
            "-n",
            "-framerate",
            str(FPS),
            "-i",
            str(folder / "%04d.png"),
            "-c:v",
            "libx264",
            "-crf",
            "15",
            "-pix_fmt",
            "yuv420p",
            "-movflags",
            "+faststart",
            str(output),
        ],
        check=True,
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    out = args.output.resolve()
    out.mkdir(parents=True, exist_ok=False)
    for kind in ("graybox", "depth"):
        (out / kind).mkdir()
    sources = []
    for i in range(FRAMES):
        svg = GUIDE / "svg" / f"{i:04d}.svg"
        sources.append({"frame": i, "sha256": sha(svg)})
        clay, depth = render(svg)
        for kind, pixels in (("graybox", clay), ("depth", depth)):
            Image.fromarray(pixels).save(out / kind / f"{i:04d}.png")
    for kind in ("graybox", "depth"):
        encode(out / kind, out / f"{kind}.mp4")
    copy_verified(STYLE, out / "style-reference.png")
    copy_verified(Path(__file__), out / "source.py")
    copy_verified(GUIDE / "landmarks.json", out / "landmarks.json")
    manifest = {
        "guide_source": str(GUIDE.relative_to(PROJECT)),
        "style_source": str(STYLE.relative_to(PROJECT)),
        "fps": FPS,
        "frames": FRAMES,
        "width": WIDTH,
        "height": HEIGHT,
        "method": "Original filled SVG geometry; no ink strokes or colors. Authored shallow relief, not recovered or fully modeled 3D. Nearer depth is brighter.",
        "source_svg_hashes": sources,
        "files": {
            str(p.relative_to(out)): sha(p)
            for p in sorted(out.rglob("*"))
            if p.is_file()
        },
    }
    (out / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(json.dumps({"output": str(out), "files": len(manifest["files"])}))


if __name__ == "__main__":
    main()
