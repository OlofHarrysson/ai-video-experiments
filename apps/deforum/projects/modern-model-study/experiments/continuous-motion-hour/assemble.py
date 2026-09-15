"""Join verified, adjacent finishes without rerendering their unchanged prefixes."""

import argparse
import copy
import os
import subprocess

from run import lab


def assemble(case):
    if case == "c5-under-the-orchids":
        parts = [
            (lab.OUT / "c3-banking-voyage/faster/rife-moving-tail", 376, 0),
            (lab.OUT / case / "excerpt-0564/rife-moving-tail", 200, 47),
        ]
    else:
        raise ValueError(case)
    config = lab.read(lab.OUT / case / "config.json")
    target = lab.OUT / case / "assembled"
    assert not target.exists()
    (target / "frames").mkdir(parents=True)
    frames = []
    sources = []
    for root, count, painting_offset in parts:
        manifest = lab.read(root / "manifest.json")
        assert manifest["status"] == "complete"
        assert lab.sha(root / "preview.mp4") == manifest["video_sha256"]
        sources.append(
            {
                "manifest": str((root / "manifest.json").relative_to(lab.APP)),
                "manifest_sha256": lab.sha(root / "manifest.json"),
                "frames": count,
                "painting_offset": painting_offset,
            }
        )
        for old in manifest["output_frames"][:count]:
            row = copy.deepcopy(old)
            index = len(frames)
            source = root / old["file"]
            assert lab.sha(source) == old["sha256"]
            row.update(
                index=index, time_seconds=index / 24, file=f"frames/{index:04d}.png"
            )
            if "source_index" in row:
                row["source_index"] += painting_offset
            if "source_pair" in row:
                row["source_pair"] = [i + painting_offset for i in row["source_pair"]]
            if row["kind"] == "anchor":
                original = config["painting_frames"][row["source_index"]]
                assert original * 2 // 3 == index
                assert lab.sha(source) == lab.sha(
                    lab.OUT / case / f"anchors/{original:04d}.png"
                )
            os.link(source, target / row["file"])
            frames.append(row)
    assert len(frames) == round(config["duration"] * 16)
    assert sum(r["kind"] == "anchor" for r in frames) == len(config["painting_frames"])
    assert sum(r["kind"] == "warp" for r in frames) == 7
    assert not any(r["kind"] in ("hold", "final_hold") for r in frames)
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
            str(len(frames)),
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
    for row in frames:
        assert lab.sha(target / row["file"]) == row["sha256"]
    result = {
        "status": "complete",
        "provenance": {
            "model": "RIFE 4.25",
            "finishing": "Adjacent verified frame ranges; final native spatial warps",
        },
        "parts": sources,
        "settings": {
            "output_fps": 24,
            "scale": 1,
            "anchor_frames": [f * 2 // 3 for f in config["painting_frames"]],
        },
        "output_frames": frames,
        "final_holds": 0,
        "final_warps": 7,
        "video_sha256": lab.sha(target / "preview.mp4"),
    }
    lab.save(target / "manifest.json", result)
    lab.save(
        target / "delivery-check.json",
        {
            "verified": True,
            "frames": len(frames),
            "paintings": len(config["painting_frames"]),
            "fps": 24,
            "video_sha256": result["video_sha256"],
            "all_source_frame_hashes_verified": True,
            "all_paintings_preserved": True,
            "final_warps": 7,
        },
    )
    print(target, flush=True)


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("case", choices=["c5-under-the-orchids"])
    assemble(p.parse_args().case)
