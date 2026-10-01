"""Verify guided-repaint graphs, source paintings, parent lineage and finishing."""

import json
from pathlib import Path

from PIL import Image

from deforum_lab.records import read, require, save, sha
from deforum_lab.rendering.verification import validate_execution

APP = Path(__file__).resolve().parents[3]
ROOT = APP / "projects/rainbow-mane/exports/guided-morph-v001"
GUIDE = APP / "projects/rainbow-mane/exports/profile-morph-v002"


def main():
    verified = []
    for run in sorted((ROOT / "runs").iterdir()):
        submission = read(run / "submission.json")
        init_hash = sha(run / "anchor.png")
        expected, executed = (
            read(run / "workflow.api.json"),
            read(run / "workflow.executed.json"),
        )
        prompt_id, _ = validate_execution(
            expected,
            executed,
            read(run / "upload.json"),
            read(run / "history.json"),
            read(run / "submit-response.json"),
            submission,
            submission.get("parent_sha256"),
            init_hash,
        )
        case, number = expected["11"]["inputs"]["filename_prefix"].split("/")[1:]
        frame = int(number)
        config = read(ROOT / case / "config.json")
        require(config["guide_sha256"] == sha(GUIDE / "manifest.json"), "Guide changed")
        prefix = ROOT / case
        require(
            sha(prefix / "anchors" / f"{frame:04d}.png")
            == sha(run / "frames/0000.png"),
            "Selected image differs",
        )
        png = Image.open(run / "frames/0000.png")
        require(png.size == (1280, 720), "Size differs")
        metadata = json.loads(png.info["prompt"])
        fingerprint = metadata["20"].pop("is_changed", None)
        require(
            fingerprint is None or fingerprint == [init_hash],
            "Input fingerprint differs",
        )
        require(metadata == executed, "PNG provenance differs")
        sampler = expected["9"]["inputs"]
        require(
            sampler["latent_image"] == ["24", 0] and sampler["cfg"] == 1,
            "Feedback recipe differs",
        )
        if frame:
            require(
                submission["parent_sha256"]
                == sha(prefix / "anchors" / f"{frame - 3:04d}.png"),
                "Parent differs",
            )
            require(
                init_hash == sha(prefix / "inputs" / f"{frame:04d}.png"),
                "Prepared input differs",
            )
            require(
                submission["guide_sha256"]
                == sha(GUIDE / "frames" / f"{frame:04d}.png"),
                "Guide frame differs",
            )
        else:
            require(
                init_hash == sha(GUIDE / "frames/0000.png"), "Opening guide differs"
            )
        verified.append(
            {
                "case": case,
                "frame": frame,
                "prompt_id": prompt_id,
                "sha256": sha(run / "frames/0000.png"),
            }
        )
    finishes = []
    for case in ["guided-n055-a012", "guided-n040-a012"]:
        manifest = read(ROOT / case / "rife/manifest.json")
        require(
            manifest["status"] == "complete" and len(manifest["output_frames"]) == 96,
            "Finishing incomplete",
        )
        for row in manifest["output_frames"]:
            require(
                sha(ROOT / case / "rife" / row["file"]) == row["sha256"],
                "Delivered frame differs",
            )
            if row["kind"] != "interpolation":
                source = ROOT / case / "anchors" / f"{row['source_index'] * 3:04d}.png"
                require(sha(source) == row["sha256"], "Painting not preserved")
        finishes.append(
            {
                "case": case,
                "frames": 96,
                "paintings": 32,
                "video_sha256": sha(ROOT / case / "rife/preview.mp4"),
            }
        )
    require(len(verified) == 65, "Expected 3 opening probes and 62 recurrent jobs")
    save(
        ROOT / "verification.json",
        {"jobs": verified, "finishes": finishes, "status": "passed"},
    )
    print(f"Verified {len(verified)} jobs and {len(finishes)} four-second deliveries")


if __name__ == "__main__":
    main()
