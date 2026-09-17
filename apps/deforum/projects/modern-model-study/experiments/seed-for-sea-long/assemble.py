"""Join verified RIFE passages at shared paintings without holds or duplicates."""

import argparse
import json
import os
import subprocess
from pathlib import Path

from deforum_lab.records import read, require, save, sha


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("edit", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    edit = read(args.edit)
    app = Path(__file__).resolve().parents[4]
    parts = [(app / row["root"], row["label"]) for row in edit["segments"]]
    manifests = [read(root / "manifest.json") for root, _ in parts]
    for i, ((root, _), manifest) in enumerate(zip(parts, manifests, strict=True)):
        require(manifest["status"] == "complete", "Incomplete source")
        require(
            sha(root / "preview.mp4") == manifest["video_sha256"],
            "Source video differs",
        )
        require(manifest["settings"]["output_fps"] == 24, "Unexpected source rate")
        if i + 1 < len(parts):
            rows = manifest["output_frames"]
            require(rows[-8]["kind"] == "anchor", "Expected seven tail frames")
            require(
                rows[-8]["sha256"] == manifests[i + 1]["output_frames"][0]["sha256"],
                "Passages do not share their boundary painting",
            )
    require(not args.output.exists(), "Preserve existing films")
    (args.output / "frames").mkdir(parents=True)
    rows, sources = [], []
    for segment, ((root, label), manifest) in enumerate(
        zip(parts, manifests, strict=True)
    ):
        selected = (
            manifest["output_frames"]
            if segment == len(parts) - 1
            else manifest["output_frames"][:-8]
        )
        sources.append(
            {
                "root": str(root.relative_to(app)),
                "label": label,
                "manifest_sha256": sha(root / "manifest.json"),
                "start_frame": len(rows),
                "frames": len(selected),
            }
        )
        painting_offset = len(rows) // 8
        for row in selected:
            original = root / row["file"]
            require(sha(original) == row["sha256"], "Source frame differs")
            index = len(rows)
            target = args.output / f"frames/{index:04d}.png"
            os.link(original, target)
            rows.append(
                {
                    **row,
                    "index": index,
                    "time_seconds": index / 24,
                    "file": str(target.relative_to(args.output)),
                    "source_segment": segment,
                    "source_output_index": row["index"],
                }
            )
            if "source_index" in row:
                rows[-1]["segment_source_index"] = row["source_index"]
                rows[-1]["source_index"] = painting_offset + row["source_index"]
            if "source_pair" in row:
                rows[-1]["segment_source_pair"] = row["source_pair"]
                rows[-1]["source_pair"] = [
                    painting_offset + p for p in row["source_pair"]
                ]
    anchors = [r["index"] for r in rows if r["kind"] == "anchor"]
    require(anchors == list(range(0, len(rows), 8)), "Painting timing or count differs")
    require(len(rows) == edit["expected_frames"], "Film duration differs")
    manifest = {
        "status": "encoding",
        "fps": 24,
        "frame_count": len(rows),
        "duration_seconds": len(rows) / 24,
        "sources": sources,
        "output_frames": rows,
        "painting_frames": anchors,
        "final_warps": 7,
        "provenance": {"model": "RIFE 4.25", "edit_sha256": sha(args.edit)},
    }
    save(args.output / "pending-manifest.json", manifest)
    video = args.output / "preview.mp4"
    subprocess.run(
        [
            "ffmpeg",
            "-v",
            "error",
            "-framerate",
            "24",
            "-i",
            str(args.output / "frames/%04d.png"),
            "-frames:v",
            str(len(rows)),
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
            str(video),
        ],
        check=True,
    )
    probe = json.loads(
        subprocess.check_output(
            [
                "ffprobe",
                "-v",
                "error",
                "-select_streams",
                "v:0",
                "-count_frames",
                "-show_entries",
                "stream=width,height,r_frame_rate,nb_read_frames,duration",
                "-of",
                "json",
                str(video),
            ]
        )
    )
    stream = probe["streams"][0]
    require(
        int(stream["nb_read_frames"]) == len(rows) and stream["r_frame_rate"] == "24/1",
        "Encoded frame count or rate differs",
    )
    subprocess.run(
        ["ffmpeg", "-v", "error", "-xerror", "-i", str(video), "-f", "null", "-"],
        check=True,
    )
    manifest.update(status="complete", video_sha256=sha(video), probe=probe)
    save(args.output / "manifest.json", manifest)
    save(
        args.output / "delivery-check.json",
        {
            "verified": True,
            "frames": len(rows),
            "paintings": len(anchors),
            "fps": 24,
            "seconds": len(rows) / 24,
            "final_warps": 7,
            "shared_boundary_paintings_verified": True,
            "video_sha256": manifest["video_sha256"],
        },
    )
    print(video)


if __name__ == "__main__":
    main()
