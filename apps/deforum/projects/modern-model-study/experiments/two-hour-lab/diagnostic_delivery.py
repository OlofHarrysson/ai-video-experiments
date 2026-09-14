"""Show the no-motion diagnostic paintings as certified half-second holds."""

import subprocess

import run as lab

from deforum_lab.records import copy_verified, read, require, save, sha


def main():
    receipt = read(lab.OUT / "checks/r6-generation.json")
    require(receipt["verified"] and len(receipt["jobs"]) == 14, "Unverified paintings")
    for case in ("r6-raw", "r6-turbo"):
        root = lab.OUT / case
        target = root / "finish/diagnostic"
        require(not target.exists(), "Diagnostic delivery already exists")
        positions = read(root / "config.json")["painting_frames"]
        rows = []
        for frame in range(84):
            i = frame // 12
            original = root / f"anchors/{positions[i]:04d}.png"
            output = target / f"frames/{frame:04d}.png"
            copy_verified(original, output)
            rows.append(
                {
                    "index": frame,
                    "file": str(output.relative_to(target)),
                    "sha256": sha(output),
                    "time_seconds": frame / 24,
                    "kind": "anchor"
                    if frame % 12 == 0
                    else "final_hold"
                    if i == 6
                    else "hold",
                    "source_index": i,
                }
            )
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
                "84",
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
                "settings": {"output_fps": 24, "anchor_frames": positions},
                "provenance": {
                    "model": "Repeated painting holds; no interpolation",
                    "generation_check_sha256": sha(
                        lab.OUT / "checks/r6-generation.json"
                    ),
                },
            },
        )
    print("Two diagnostic videos: 84 frames, seven paintings each, no interpolation.")


if __name__ == "__main__":
    main()
