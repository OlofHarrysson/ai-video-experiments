"""Bind the local motion-separated finish to the recorded original paintings."""

import json
import subprocess

import numpy as np
from PIL import Image
from run import lab

from deforum_lab.image.warps import warp_at_time


def main():
    root = lab.OUT / "motion-aware-full"
    source = lab.OUT / "c3-banking-voyage"
    plan = lab.read(root / "plan.json")
    config = lab.read(source / "config.json")
    assert plan["source_config_sha256"] == lab.sha(source / "config.json")
    expected = lab.read(source / "faster/rife/manifest.json")["provenance"]
    for row in plan["rows"]:
        frame = row["frame"]
        pair = root / f"pair-{frame:04d}"
        m = lab.read(pair / "rife/manifest.json")
        assert m["status"] == "complete"
        for key in (
            "commit",
            "weights_sha256",
            "code_sha256",
            "model",
            "runner_sha256",
        ):
            assert m["provenance"][key] == expected[key]
        for src, key in zip(m["sources"], ("left_sha256", "aligned_right_sha256")):
            assert src["sha256"] == row[key] == lab.sha(lab.Path(src["file"]))
        assert row["left_sha256"] == lab.sha(source / f"anchors/{frame:04d}.png")
        right = source / f"anchors/{frame + 12:04d}.png"
        assert row["right_sha256"] == lab.sha(right)
        aligned = warp_at_time(
            np.asarray(Image.open(right).convert("RGB")),
            (frame + 12) / 24,
            frame / 24,
            config["phrases"],
        )
        assert np.array_equal(
            aligned, np.asarray(Image.open(pair / "sources/0001.png"))
        )
    verified = []
    for mode in ("direct", "explicit-motion"):
        dest = root / mode
        m = lab.read(dest / "manifest.json")
        assert m["status"] == "complete"
        assert len(m["output_frames"]) == 384
        assert m["video_sha256"] == lab.sha(dest / "preview.mp4")
        for row in m["output_frames"]:
            assert row["sha256"] == lab.sha(dest / row["file"])
            i = row["index"]
            if row["kind"] == "anchor":
                assert row["sha256"] == lab.sha(
                    source / f"anchors/{i * 3 // 2:04d}.png"
                )
            if mode == "direct" or i > 376:
                assert row["sha256"] == lab.sha(
                    source / f"faster/rife-moving-tail/frames/{i:04d}.png"
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
        assert (probe["width"], probe["height"]) == (1536, 1024)
        assert probe["r_frame_rate"] == "24/1" and int(probe["nb_read_frames"]) == 384
        assert float(probe["duration"]) == 16
        verified.append(
            {"mode": mode, "video_sha256": m["video_sha256"], "probe": probe}
        )
    lab.save(
        root / "verification.json",
        {
            "verified": True,
            "aligned_pairs_recomputed_exactly": len(plan["rows"]),
            "all_48_paintings_preserved": True,
            "pinned_rife_provenance_verified": True,
            "direct_frames_equal_original_delivery": True,
            "final_seven_warps_equal": True,
            "deliveries": verified,
        },
    )
    print("Verified 47 aligned pairs and both complete deliveries", flush=True)


if __name__ == "__main__":
    main()
