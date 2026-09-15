"""Render reference-inspired motion recipes on one unchanged artwork."""

import argparse
import hashlib
import json
import subprocess
from pathlib import Path

import numpy as np
from PIL import Image

from deforum_lab.image.warps import mapping, warp_at_time
from deforum_lab.media.sheets import sheet
from deforum_lab.records import read, save, sha

HERE = Path(__file__).resolve().parent
APP = HERE.parents[3]
OUT = HERE.parents[1] / "exports/motion-recipe-previews-v001"


def render(case):
    config_path = HERE / "configs" / f"{case}.json"
    config = read(config_path)
    source = APP / config["source"]
    source_sha = sha(source)
    rgb = np.asarray(
        Image.open(source)
        .convert("RGB")
        .resize(tuple(config["preview_size"]), Image.Resampling.LANCZOS)
    )
    h, w = rgb.shape[:2]
    fps = config["fps"]
    count = round(config["duration_seconds"] * fps)
    dest = OUT / case
    dest.mkdir(parents=True, exist_ok=False)
    (dest / "render-executed.py").write_bytes(Path(__file__).read_bytes())
    save(dest / "config.json", config)
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
            str(fps),
            "-i",
            "-",
            "-an",
            "-c:v",
            "libx264",
            "-preset",
            "medium",
            "-crf",
            "18",
            "-pix_fmt",
            "yuv420p",
            "-movflags",
            "+faststart",
            str(dest / "preview.mp4"),
        ],
        stdin=subprocess.PIPE,
    )
    y, x = np.mgrid[0.05:0.95:15j, 0.05:1.45:23j]
    grid = np.stack([x, y], -1)
    base = mapping(grid, 0, config["phrases"], inverse=True)
    previous = None
    speeds = []
    rows = []
    samples = []
    sample_frames = set(range(0, count, fps)) | {count - 1}
    try:
        for i in range(count):
            t = i / fps
            warped = warp_at_time(rgb, 0, t, config["phrases"])
            if i == 0:
                assert np.array_equal(warped, rgb)
            process.stdin.write(warped.tobytes())
            moved = mapping(base, t, config["phrases"])
            assert np.isfinite(moved).all()
            np.testing.assert_allclose(
                mapping(moved, t, config["phrases"], True), base, atol=1e-10
            )
            if previous is not None:
                speeds.append(
                    float(
                        np.median(np.linalg.norm(moved - previous, axis=-1)) * h * fps
                    )
                )
            previous = moved
            row = {
                "index": i,
                "time_seconds": t,
                "kind": "anchor" if i == 0 else "warp",
                "source_index": 0,
                "raw_rgb_sha256": hashlib.sha256(warped.tobytes()).hexdigest(),
            }
            if i in sample_frames:
                image = Image.fromarray(warped)
                file = f"sample-{i:04d}.png"
                image.save(dest / file)
                row.update(file=file, sha256=sha(dest / file))
                samples.append((image, f"{config['label']} · {t:.2f}s"))
            rows.append(row)
    finally:
        process.stdin.close()
    assert process.wait() == 0
    subprocess.run(
        [
            "ffmpeg",
            "-v",
            "error",
            "-xerror",
            "-i",
            str(dest / "preview.mp4"),
            "-f",
            "null",
            "-",
        ],
        check=True,
    )
    probe = json.loads(
        subprocess.check_output(
            [
                "ffprobe",
                "-v",
                "error",
                "-count_frames",
                "-select_streams",
                "v:0",
                "-show_entries",
                "stream=width,height,r_frame_rate,nb_read_frames,duration",
                "-of",
                "json",
                str(dest / "preview.mp4"),
            ]
        )
    )["streams"][0]
    assert (probe["width"], probe["height"]) == (w, h)
    assert probe["r_frame_rate"] == f"{fps}/1" and int(probe["nb_read_frames"]) == count
    assert float(probe["duration"]) == config["duration_seconds"]
    assert source_sha == sha(source)
    assert len({r["raw_rgb_sha256"] for r in rows}) == count
    save(
        dest / "manifest.json",
        {
            "status": "complete",
            "provenance": {
                "method": config["method"],
                "source": config["source"],
                "source_sha256": source_sha,
                "config_sha256": sha(config_path),
                "runner_sha256": sha(dest / "render-executed.py"),
                "runner_snapshot": "render-executed.py",
                "warps_sha256": sha(APP / "src/deforum_lab/image/warps.py"),
            },
            "settings": {
                "output_fps": fps,
                "anchor_frames": [0],
                "source_time_multiplier": 1,
            },
            "output_frames": rows,
            "video_sha256": sha(dest / "preview.mp4"),
            "new_diffusion_jobs": 0,
            "interpolation": None,
        },
    )
    save(
        dest / "delivery-check.json",
        {
            "verified": True,
            "probe": probe,
            "all_frames_unique": True,
            "initial_rgb_equals_resized_source": True,
            "finite_invertible_maps_at_all_frames": True,
            "median_grid_speed_pixels_per_second": {
                "min": min(speeds),
                "median": float(np.median(speeds)),
                "max": max(speeds),
            },
            "slowest_interval_ends_at_frame": int(np.argmin(speeds)) + 1,
            "speed_is_geometric_not_a_perceptual_quality_score": True,
        },
    )
    sheet(
        [samples[i : i + 2] for i in range(0, len(samples), 2)],
        dest / "overview.jpg",
        size=(480, 320),
    )
    print(dest, flush=True)


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("case", choices=["floating-drift", "travelling-look-around"])
    render(p.parse_args().case)
