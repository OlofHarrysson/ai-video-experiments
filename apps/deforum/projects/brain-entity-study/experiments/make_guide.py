# /// script
# requires-python = ">=3.12"
# dependencies = ["pillow==12.3.0", "numpy==2.5.3"]
# ///
"""Original six-second silhouette guide; no network or inference.

Run: uv run --offline --script apps/deforum/projects/brain-entity-study/experiments/make_guide.py
Verify without rewriting: append --verify. Requires local ffmpeg and ffprobe.
Frames are RGB PNGs, indexed 0000–0047, ordered left-to-right in strip.png.
"""

import argparse
import hashlib
import json
import math
from pathlib import Path
import subprocess

import numpy as np
from PIL import Image, ImageDraw

WIDTH, HEIGHT, FPS, COUNT = 1024, 576, 8, 48
SUPERSAMPLE = 3
SEGMENTS = 14
OUTPUT = Path(__file__).resolve().parents[1] / "references/assets/guide-v001"


def smooth(start, end, value):
    x = np.clip((value - start) / (end - start), 0, 1)
    return float(x * x * (3 - 2 * x))


def geometry(index):
    t = index / (COUNT - 1)
    # A short face-on establishment, a held narrow midpoint, and a full reopening.
    close = smooth(0.08, 0.46, t) * (1 - smooth(0.55, 0.94, t))
    organic = smooth(0.14, 0.88, t)
    return t, close, organic


def render_frame(index):
    t, close, organic = geometry(index)
    canvas = Image.new("L", (WIDTH * SUPERSAMPLE, HEIGHT * SUPERSAMPLE), 0)
    draw = ImageDraw.Draw(canvas)
    angle = math.radians(-26 * close + 7 * organic)
    scale_x = 1 - 0.82 * close
    scale_y = 1 - 0.035 * close
    spin = 0.14 * smooth(0, 1, t)

    def contour(theta, inner=False):
        # Shared harmonics keep membrane thickness broad and the aperture readable.
        scallop = np.cos(12 * (theta - spin))
        asymmetry = np.sin(3 * theta + 0.5) + 0.5 * np.cos(5 * theta)
        if inner:
            radius = 137 + organic * (5 * scallop + 3 * asymmetry)
        else:
            radius = 197 + organic * (9 + 15 * scallop + 5 * asymmetry)
        x = radius * np.cos(theta) * scale_x
        y = radius * np.sin(theta) * scale_y
        px = WIDTH / 2 + x * math.cos(angle) - y * math.sin(angle)
        py = HEIGHT / 2 + x * math.sin(angle) + y * math.cos(angle)
        return list(zip(px * SUPERSAMPLE, py * SUPERSAMPLE))

    theta = np.linspace(0, 2 * math.pi, 1440, endpoint=False)
    draw.polygon(contour(theta), fill=245)
    draw.polygon(contour(theta, inner=True), fill=0)
    # Actual black gaps between mechanical plates shrink continuously into a membrane.
    gap = 0.043 * (1 - smooth(0.12, 0.57, t))
    if gap > 0:
        for segment in range(SEGMENTS):
            center = 2 * math.pi * segment / SEGMENTS + spin
            arc = np.linspace(center - gap, center + gap, 12)
            draw.polygon(contour(arc) + contour(arc[::-1], inner=True), fill=0)
    return canvas.resize((WIDTH, HEIGHT), Image.Resampling.LANCZOS).convert("RGB")


def pixel_hash(image):
    return hashlib.sha256(image.tobytes()).hexdigest()


def probe_video():
    info = json.loads(subprocess.check_output([
        "ffprobe", "-v", "error", "-count_frames", "-select_streams", "v:0",
        "-show_entries", "stream=width,height,r_frame_rate,nb_read_frames,duration",
        "-of", "json", str(OUTPUT / "preview.mp4"),
    ]))
    stream = info["streams"][0]
    assert (stream["width"], stream["height"]) == (WIDTH, HEIGHT), stream
    assert stream["r_frame_rate"] == "8/1", stream
    assert int(stream["nb_read_frames"]) == COUNT, stream
    assert float(stream["duration"]) == COUNT / FPS, stream
    return stream


def verify():
    manifest = json.loads((OUTPUT / "manifest.json").read_text())
    paths = sorted((OUTPUT / "frames").glob("*.png"))
    assert len(paths) == COUNT
    with Image.open(OUTPUT / "strip.png") as strip:
        assert strip.size == (COUNT * WIDTH, HEIGHT)
        for i, path in enumerate(paths):
            expected = render_frame(i)
            with Image.open(path) as actual:
                assert actual.size == (WIDTH, HEIGHT) and actual.mode == "RGB"
                assert pixel_hash(actual) == pixel_hash(expected) == manifest["frames"][i]["pixel_sha256"]
            tile = strip.crop((i * WIDTH, 0, (i + 1) * WIDTH, HEIGHT))
            assert pixel_hash(tile) == pixel_hash(expected), f"Strip tile {i} differs"
            # Verify ample black margin throughout, including the tilted midpoint.
            box = expected.getbbox()
            assert box[0] > 50 and box[1] > 50
            assert box[2] < WIDTH - 50 and box[3] < HEIGHT - 50
    print(json.dumps({"verified_frames": COUNT, "strip_tiles_match": True, "video": probe_video()}, indent=2))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--verify", action="store_true")
    args = parser.parse_args()
    if args.verify:
        verify()
        return
    if OUTPUT.exists() and any(OUTPUT.iterdir()):
        raise SystemExit(f"Preserving existing assets: {OUTPUT}. Use --verify to check reproducibility.")
    (OUTPUT / "frames").mkdir(parents=True, exist_ok=True)
    strip = Image.new("RGB", (WIDTH * COUNT, HEIGHT))
    thumb_w, thumb_h, label_h = 256, 144, 24
    sheet = Image.new("RGB", (thumb_w * 8, (thumb_h + label_h) * 6), "#171b20")
    labels = ImageDraw.Draw(sheet)
    records = []
    for i in range(COUNT):
        frame = render_frame(i)
        name = f"frames/{i:04d}.png"
        frame.save(OUTPUT / name)
        strip.paste(frame, (WIDTH * i, 0))
        x, y = (i % 8) * thumb_w, (i // 8) * (thumb_h + label_h)
        sheet.paste(frame.resize((thumb_w, thumb_h), Image.Resampling.LANCZOS), (x, y))
        labels.text((x + 8, y + thumb_h + 5), f"{i:02d}  |  {i / FPS:.3f}s", fill="white")
        records.append({"file": name, "time_seconds": i / FPS, "pixel_sha256": pixel_hash(frame)})
    strip.save(OUTPUT / "strip.png")
    sheet.save(OUTPUT / "contact-sheet.png")
    subprocess.run([
        "ffmpeg", "-v", "error", "-nostdin", "-n", "-framerate", str(FPS),
        "-start_number", "0", "-i", str(OUTPUT / "frames/%04d.png"),
        "-frames:v", str(COUNT), "-c:v", "libx264", "-crf", "16",
        "-preset", "slow", "-threads", "1", "-pix_fmt", "yuv420p",
        "-map_metadata", "-1", "-movflags", "+faststart", str(OUTPUT / "preview.mp4"),
    ], check=True)
    manifest = {
        "width": WIDTH, "height": HEIGHT, "fps": FPS, "count": COUNT,
        "duration_seconds": COUNT / FPS, "strip_layout": "48 RGB tiles, left to right; split every 1024 pixels",
        "origin": "Original analytic geometry; no copied reference pixels or model inference",
        "stages": {"0-15": "segmented mechanical ring closes", "16-29": "tilted narrow organic aperture", "30-47": "scalloped membrane reopens"},
        "frames": records,
    }
    (OUTPUT / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    verify()
    print(OUTPUT)


if __name__ == "__main__":
    main()
