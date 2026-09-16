"""Deliver an existing painting sequence 1.5 times faster, still at 24 fps."""

import argparse
import subprocess

from run import lab


def retime(case, stage, first_frame=0, last_frame=None):
    source = lab.OUT / case
    config = lab.read(source / "config.json")
    assert first_frame in config["painting_frames"]
    if last_frame is not None:
        assert first_frame == 0 and last_frame in config['painting_frames']
    old = [frame for frame in config["painting_frames"] if frame >= first_frame
           and (last_frame is None or frame <= last_frame)]
    assert all(frame % 3 == 0 for frame in old)
    positions = [(frame - first_frame) * 2 // 3 for frame in old]
    old_count = (last_frame + 12 if last_frame is not None else round(config["duration"] * 24)) - first_frame
    assert old_count % 3 == 0
    count = old_count * 2 // 3
    root = source / (f'through-{last_frame:04d}' if last_frame is not None else
                     f"excerpt-{first_frame:04d}" if first_frame else "faster")
    sources = root / "sources"
    for i, frame in enumerate(old):
        lab.copy_verified(source / f"anchors/{frame:04d}.png", sources / f"{i:04d}.png")
    lab.save(root / "anchor-frames.json", positions)
    lab.save(
        root / "retiming.json",
        {
            "source_case": case,
            "source_config_sha256": lab.sha(source / "config.json"),
            "speed_multiplier": 1.5,
            "source_start_frame": first_frame,
            "source_anchor_frames": old,
            "delivery_anchor_frames": positions,
            "fps": 24,
            "frame_count": count,
            "new_diffusion_jobs": 0,
        },
    )
    target = root / ("pair" if stage == "pair" else "rife")
    if stage != "check":
        assert not target.exists(), "Preserve previous finishing output"
        command = [
            str(lab.PATHS.rife_python),
            str(lab.PATHS.rife_script),
            str(sources),
            str(target),
            "--source-frames",
            str(len(old)),
            "--anchor-frames",
            str(root / "anchor-frames.json"),
            "--output-fps",
            "24",
            "--frame-count",
            str(count),
        ]
        command += (
            ["--pair-only"]
            if stage == "pair"
            else ["--validated-pair", str(root / "pair/manifest.json")]
        )
        subprocess.run(command, check=True)
        return
    manifest = lab.read(target / "manifest.json")
    assert manifest["status"] == "complete"
    assert lab.sha(target / "preview.mp4") == manifest["video_sha256"]
    assert manifest["settings"]["output_fps"] == 24
    assert manifest["settings"]["anchor_frames"] == positions
    assert manifest["settings"]["scale"] == 1
    assert manifest["provenance"]["model"] == "RIFE 4.25"
    assert len(manifest["output_frames"]) == count
    assert manifest["final_holds"] == count - positions[-1] - 1
    assert [
        r["index"] for r in manifest["output_frames"] if r["kind"] == "anchor"
    ] == positions
    for row in manifest["output_frames"]:
        frame = row["index"]
        image = target / row["file"]
        assert lab.sha(image) == row["sha256"]
        assert row["time_seconds"] == frame / 24
        if row["kind"] == "interpolation":
            a, b = [positions[i] for i in row["source_pair"]]
            assert row["timestep"] == f"{frame - a}/{b - a}"
        else:
            original = source / f"anchors/{old[row['source_index']]:04d}.png"
            assert lab.sha(image) == lab.sha(original)
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
    lab.save(
        root / "delivery-check.json",
        {
            "verified": True,
            "paintings": len(old),
            "frames": count,
            "fps": 24,
            "video_sha256": manifest["video_sha256"],
        },
    )
    print(f"Verified all {len(old)} paintings retained in {count} frames at 24 fps.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("case")
    parser.add_argument("stage", choices=["pair", "full", "check"])
    parser.add_argument("--from-frame", type=int, default=0)
    parser.add_argument("--through-frame", type=int)
    args = parser.parse_args()
    retime(args.case, args.stage, args.from_frame, args.through_frame)
