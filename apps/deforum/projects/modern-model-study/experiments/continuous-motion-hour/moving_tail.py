"""Keep spatial motion running after the final RIFE painting, without inference."""

import argparse
import copy
import os
import subprocess

import numpy as np
from PIL import Image
from run import lab

from deforum_lab.image.warps import warp_at_time


def finish(case, first_frame=0):
    source = lab.OUT / case
    config = lab.read(source / "config.json")
    section = source / (f"excerpt-{first_frame:04d}" if first_frame else "faster")
    timing = lab.read(section / "retiming.json")
    raw = section / "rife"
    original = lab.read(raw / "manifest.json")
    assert original["status"] == "complete"
    assert lab.sha(raw / "preview.mp4") == original["video_sha256"]
    target = section / "rife-moving-tail"
    assert not target.exists(), "Preserve earlier deliveries"
    (target / "frames").mkdir(parents=True)
    manifest = copy.deepcopy(original)
    manifest["status"] = "finishing"
    manifest["parent_video_sha256"] = original["video_sha256"]
    last = timing["delivery_anchor_frames"][-1]
    last_source = timing["source_anchor_frames"][-1]
    last_image = lab.pixels(source / f"anchors/{last_source:04d}.png")
    tail_count = 0
    for row in manifest["output_frames"]:
        path = target / row["file"]
        path.parent.mkdir(parents=True, exist_ok=True)
        if row["index"] <= last:
            os.link(raw / row["file"], path)
        else:
            seconds = (first_frame + row["index"] * timing["speed_multiplier"]) / 24
            rgb = warp_at_time(last_image, last_source / 24, seconds, config["phrases"])
            Image.fromarray(rgb).save(path)
            row.update(
                kind="warp",
                source_index=len(timing["source_anchor_frames"]) - 1,
                source_time_seconds=seconds,
                sha256=lab.sha(path),
            )
            tail_count += 1
        assert lab.sha(path) == row["sha256"]
    manifest["final_holds"] = 0
    manifest["final_warps"] = tail_count
    manifest["tail_recipe"] = {
        "source_frame": last_source,
        "first_frame": first_frame,
        "speed_multiplier": timing["speed_multiplier"],
        "config_sha256": lab.sha(source / "config.json"),
    }
    lab.save(target / "pending-manifest.json", manifest)
    subprocess.run(
        [
            "ffmpeg",
            "-v",
            "error",
            "-framerate",
            "24",
            "-i",
            str(target / "frames/%04d.png"),
            "-frames:v",
            str(len(manifest["output_frames"])),
            "-an",
            "-c:v",
            "libx264",
            "-preset",
            "slow",
            "-crf",
            "18",
            "-pix_fmt",
            "yuv420p",
            "-movflags",
            "+faststart",
            str(target / "preview.mp4"),
        ],
        check=True,
    )
    subprocess.run(
        [
            "ffmpeg",
            "-v",
            "error",
            "-xerror",
            "-i",
            str(target / "preview.mp4"),
            "-f",
            "null",
            "-",
        ],
        check=True,
    )
    for row in manifest["output_frames"]:
        path = target / row["file"]
        assert row["time_seconds"] == row["index"] / 24
        assert lab.sha(path) == row["sha256"]
        if row["kind"] == "anchor":
            original_frame = timing["source_anchor_frames"][row["source_index"]]
            assert lab.sha(path) == lab.sha(
                source / f"anchors/{original_frame:04d}.png"
            )
        elif row["kind"] == "warp":
            expected = warp_at_time(
                last_image,
                last_source / 24,
                row["source_time_seconds"],
                config["phrases"],
            )
            assert np.array_equal(lab.pixels(path), expected)
        else:
            assert lab.sha(path) == lab.sha(raw / row["file"])
    manifest.update(status="complete", video_sha256=lab.sha(target / "preview.mp4"))
    lab.save(target / "manifest.json", manifest)
    lab.save(
        target / "delivery-check.json",
        {
            "verified": True,
            "frames": len(manifest["output_frames"]),
            "paintings": len(timing["source_anchor_frames"]),
            "fps": 24,
            "final_warps": tail_count,
            "video_sha256": manifest["video_sha256"],
            "preserved_through_delivery_frame": last,
            "tail_changed_pixels": bool(
                np.any(
                    lab.pixels(target / manifest["output_frames"][-1]["file"])
                    != last_image
                )
            ),
        },
    )
    print(target, flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("case")
    parser.add_argument("--from-frame", type=int, default=0)
    args = parser.parse_args()
    finish(args.case, args.from_frame)
