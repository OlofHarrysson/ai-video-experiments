"""Preserve the first 22 paintings, then hold the last: an eleven-second edit."""

import copy
import subprocess

import run as lab

from deforum_lab.records import copy_verified, read, require, save, sha


def main():
    source = lab.OUT / "r5-velvet/finish/rife"
    manifest = read(source / "manifest.json")
    require(manifest["status"] == "complete", "Incomplete original")
    require(manifest["video_sha256"] == sha(source / "preview.mp4"), "Original changed")
    target = lab.OUT / "velvet-harbour-cut"
    require(not target.exists(), "Preserve the existing edit")
    rows = []
    for frame in range(264):
        original = manifest["output_frames"][min(frame, 252)]
        src = source / original["file"]
        require(sha(src) == original["sha256"], "Original frame changed")
        dest = target / f"frames/{frame:04d}.png"
        copy_verified(src, dest)
        row = copy.deepcopy(original)
        row.update(
            index=frame, file=str(dest.relative_to(target)), time_seconds=frame / 24
        )
        if frame > 252:
            row.update(kind="final_hold", source_index=21)
        rows.append(row)
    video = target / "preview.mp4"
    subprocess.run(
        [
            "ffmpeg",
            "-hide_banner",
            "-loglevel",
            "error",
            "-n",
            "-framerate",
            "24",
            "-i",
            str(target / "frames/%04d.png"),
            "-frames:v",
            "264",
            "-c:v",
            "libx264",
            "-crf",
            "17",
            "-pix_fmt",
            "yuv420p",
            "-movflags",
            "+faststart",
            str(video),
        ],
        check=True,
    )
    subprocess.run(
        ["ffmpeg", "-v", "error", "-xerror", "-i", str(video), "-f", "null", "-"],
        check=True,
    )
    save(
        target / "manifest.json",
        {
            "status": "complete",
            "video_sha256": sha(video),
            "output_frames": rows,
            "settings": {"output_fps": 24, "anchor_frames": list(range(0, 253, 12))},
            "provenance": {
                "model": "RIFE 4.25",
                "source_manifest_sha256": sha(source / "manifest.json"),
                "edit": "Original frames 0–252, then eleven copies of painting frame252",
            },
            "verified": {
                "preserved_original_frame_prefix": 253,
                "painting_count": 22,
                "final_holds": 11,
                "fully_decoded": True,
            },
        },
    )
    print("Verified eleven-second edit: original prefix and 22 paintings preserved.")


if __name__ == "__main__":
    main()
