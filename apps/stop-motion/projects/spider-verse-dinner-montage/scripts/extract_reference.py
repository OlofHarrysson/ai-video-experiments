# /// script
# requires-python = ">=3.11"
# dependencies = ["numpy", "pillow"]
# ///
"""Extract the dinner-montage reference from a local copy of the film and measure its cadence.

Usage, from this project folder:

    uv run --script scripts/extract_reference.py SOURCE_VIDEO

SOURCE_VIDEO is a local copy of Spider-Man: Across the Spider-Verse (2023). Film media goes to
references/assets/, which Git ignores. The measured cadence goes to references/montage-cadence.json.
"""

import hashlib
import json
import re
import subprocess
import sys
import tempfile
from collections import Counter
from itertools import pairwise
from pathlib import Path

import numpy as np
from PIL import Image

CONTEXT = (224.0, 250.0)  # subway window into the dinner memories, montage, school hallway
MONTAGE = (237.3, 243.0)  # the montage plus a few frames of the shots on either side
# A new image changes the palette; a camera move barely changes a 16 px wide colour thumbnail.
SWAP_WIDTH = 16
NEW_IMAGE_DIFF = 10.0  # mean absolute RGB change (0-255) at SWAP_WIDTH that marks a new image
# Any movement at all shows up in detailed luma; compression noise alone stays below HOLD_DIFF.
MOTION_WIDTH = 480
HOLD_DIFF = 0.6
SHEET_THUMB = (320, 133)
SHEET_COLUMNS = 8

PROJECT = Path(__file__).resolve().parents[1]
REFERENCES = PROJECT / "references"
ASSETS = REFERENCES / "assets"


def ffmpeg(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["ffmpeg", "-y", *args], check=True, capture_output=True, text=True)


def export_clip(source: Path, window: tuple[float, float], name: str) -> None:
    start, end = window
    ffmpeg(
        "-v", "error", "-ss", str(start), "-t", str(end - start), "-i", str(source),
        "-map", "0:v:0", "-map", "0:a:0", "-c:v", "libx264", "-crf", "18", "-preset", "medium",
        "-pix_fmt", "yuv420p", "-c:a", "aac", "-ac", "2", "-b:a", "192k", str(ASSETS / name),
    )


def decode_frames(source: Path, window: tuple[float, float], directory: Path) -> list[float]:
    """Decode every frame in the window as 8-bit PNG and return each frame's time in the film."""
    start, end = window
    result = ffmpeg(
        "-v", "info", "-ss", str(start), "-t", str(end - start), "-i", str(source), "-copyts",
        "-map", "0:v:0", "-vf", "showinfo", "-fps_mode", "passthrough", "-pix_fmt", "rgb24",
        str(directory / "%04d.png"),
    )
    return [float(t) for t in re.findall(r"pts_time:([\d.]+)", result.stderr)]


def thumbnail(path: Path, width: int, mode: str) -> np.ndarray:
    image = Image.open(path).convert(mode)
    size = (width, round(image.height * width / image.width))
    return np.asarray(image.resize(size, Image.Resampling.BOX), dtype=np.float32)


def changes_between(thumbnails: list[np.ndarray]) -> list[float | None]:
    return [None] + [float(np.abs(b - a).mean()) for a, b in pairwise(thumbnails)]


def timecode(seconds: float) -> str:
    return f"{int(seconds // 60)}:{seconds % 60:06.3f}"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as file:
        for block in iter(lambda: file.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def contact_sheet(stills: list[Path], output: Path) -> None:
    width, height = SHEET_THUMB
    rows = -(-len(stills) // SHEET_COLUMNS)
    sheet = Image.new("RGB", (SHEET_COLUMNS * (width + 4), rows * (height + 4)), "black")
    for index, path in enumerate(stills):
        thumb = Image.open(path).convert("RGB").resize(SHEET_THUMB, Image.Resampling.LANCZOS)
        sheet.paste(thumb, ((index % SHEET_COLUMNS) * (width + 4), (index // SHEET_COLUMNS) * (height + 4)))
    sheet.save(output, quality=90)


def main(source: Path) -> None:
    stills_dir = ASSETS / "stills"
    stills_dir.mkdir(parents=True, exist_ok=True)
    for previous in stills_dir.glob("image-*.png"):
        previous.unlink()
    (ASSETS / "SOURCE.txt").write_text(f"{source}\n{source.stat().st_size} bytes\n")

    export_clip(source, CONTEXT, "scene-context.mp4")
    export_clip(source, MONTAGE, "montage.mp4")

    with tempfile.TemporaryDirectory() as temporary:
        frames_dir = Path(temporary)
        times = decode_frames(source, MONTAGE, frames_dir)
        frames = sorted(frames_dir.glob("*.png"))
        if len(frames) != len(times):
            raise RuntimeError(f"decoded {len(frames)} frames but read {len(times)} timestamps")

        swaps = changes_between([thumbnail(path, SWAP_WIDTH, "RGB") for path in frames])
        motion = changes_between([thumbnail(path, MOTION_WIDTH, "L") for path in frames])
        changes = [i for i, swap in enumerate(swaps) if swap is not None and swap > NEW_IMAGE_DIFF]
        if len(changes) < 3:
            raise RuntimeError("expected the montage to start and end with a cut inside the window")

        # The first change is the cut into the montage; the last is the cut out of it.
        images = []
        for number, (first, following) in enumerate(pairwise(changes), start=1):
            images.append({
                "image": number,
                "time": round(times[first], 3),
                "timecode": timecode(times[first]),
                "frames": following - first,
                "swap_in": round(swaps[first], 2),
            })
            still = stills_dir / f"image-{number:02d}.png"
            still.write_bytes(frames[first].read_bytes())

    held = [i for i in range(changes[0] + 1, changes[-1]) if i not in changes]
    exposures = Counter(image["frames"] for image in images)
    duration = times[changes[-1]] - times[changes[0]]
    summary = {
        "starts": timecode(times[changes[0]]),
        "ends": timecode(times[changes[-1]]),
        "duration_seconds": round(duration, 3),
        "images": len(images),
        "frames": changes[-1] - changes[0],
        "images_per_second": round(len(images) / duration, 2),
        "exposure_lengths": {f"{length} frames": count for length, count in sorted(exposures.items())},
        "smallest_swap_between_images": round(min(image["swap_in"] for image in images), 2),
        "largest_swap_within_an_image": round(max(swaps[i] for i in held), 2),
        "mean_motion_within_an_image": round(sum(motion[i] for i in held) / len(held), 2),
        "exact_repeats_within_images": sum(motion[i] < HOLD_DIFF for i in held),
    }

    stills = sorted(stills_dir.glob("image-*.png"))
    contact_sheet(stills, ASSETS / "montage-sheet.jpg")
    media = [ASSETS / "scene-context.mp4", ASSETS / "montage.mp4", ASSETS / "montage-sheet.jpg", *stills]
    (ASSETS / "SHA256SUMS").write_text(
        "".join(f"{sha256(path)}  {path.relative_to(ASSETS)}\n" for path in media)
    )

    record = {
        "film": "Spider-Man: Across the Spider-Verse (2023)",
        "source": "local 1080p digital copy, 1920x800 at 24000/1001 fps; path recorded in assets/SOURCE.txt",
        "window_seconds": list(MONTAGE),
        "measure": {
            "swap": f"mean absolute RGB change from the previous frame at {SWAP_WIDTH} px wide, 0-255; "
                    f"a new image above {NEW_IMAGE_DIFF}",
            "motion": f"mean absolute luma change from the previous frame at {MOTION_WIDTH} px wide, 0-255; "
                      f"an exact repeat below {HOLD_DIFF}",
        },
        "summary": summary,
        "images": images,
        "frames": [
            {"time": round(t, 3),
             "swap": None if s is None else round(s, 2),
             "motion": None if m is None else round(m, 2)}
            for t, s, m in zip(times, swaps, motion)
        ],
    }
    (REFERENCES / "montage-cadence.json").write_text(json.dumps(record, indent=1) + "\n")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    main(Path(sys.argv[1]).expanduser().resolve())
