"""Isolate explicit spatial motion during finishing, using saved paintings only."""

import argparse
import subprocess

import numpy as np
from PIL import Image
from run import lab

from deforum_lab.image.warps import warp_at_time
from deforum_lab.media.sheets import sheet
from deforum_lab.records import copy_verified, read, save, sha

ROOT = lab.OUT / "motion-aware-probe"
SOURCE = lab.OUT / "c3-banking-voyage"


def prepare():
    config = read(SOURCE / "config.json")
    first, last = (0, 564) if ROOT.name == "motion-aware-full" else (96, 192)
    assert not (ROOT / "plan.json").exists()
    rows = []
    for frame in range(first, last, 12):
        root = ROOT / f"pair-{frame:04d}"
        (root / "sources").mkdir(parents=True, exist_ok=False)
        left = SOURCE / f"anchors/{frame:04d}.png"
        right = SOURCE / f"anchors/{frame + 12:04d}.png"
        copy_verified(left, root / "sources/0000.png")
        rgb = warp_at_time(
            np.asarray(Image.open(right).convert("RGB")),
            (frame + 12) / 24,
            frame / 24,
            config["phrases"],
        )
        Image.fromarray(rgb).save(root / "sources/0001.png")
        save(root / "positions.json", [0, 8])
        rows.append(
            {
                "frame": frame,
                "left_sha256": sha(left),
                "right_sha256": sha(right),
                "aligned_right_sha256": sha(root / "sources/0001.png"),
            }
        )
    save(
        ROOT / "plan.json",
        {
            "case": config["case"],
            "source_start": first,
            "source_end": last,
            "tail": 7 if first == 0 else 0,
            "source_config_sha256": sha(SOURCE / "config.json"),
            "rows": rows,
        },
    )
    print("Prepared", len(rows), "aligned pairs", flush=True)


def infer():
    plan = read(ROOT / "plan.json")
    for row in plan["rows"]:
        p = ROOT / f"pair-{row['frame']:04d}"
        subprocess.run(
            [
                str(lab.PATHS.rife_python),
                str(lab.PATHS.rife_script),
                str(p / "sources"),
                str(p / "rife"),
                "--source-frames",
                "2",
                "--anchor-frames",
                str(p / "positions.json"),
                "--output-fps",
                "24",
                "--frame-count",
                "9",
                "--pair-only",
            ],
            check=True,
        )


def compose():
    plan = read(ROOT / "plan.json")
    config = read(SOURCE / "config.json")
    assert plan["source_config_sha256"] == sha(SOURCE / "config.json")
    regular = SOURCE / "faster/rife-moving-tail"
    original = read(regular / "manifest.json")
    assert (
        original["status"] == "complete"
        and sha(regular / "preview.mp4") == original["video_sha256"]
    )
    first, last = plan["source_start"], plan["source_end"]
    last_index = (last - first) * 2 // 3
    count = last_index + 1 + plan.get("tail", 0)
    for mode in ("direct", "explicit-motion"):
        dest = ROOT / mode
        (dest / "frames").mkdir(parents=True, exist_ok=False)
        rows = []
        for i in range(count):
            f = first + i * 1.5
            path = dest / f"frames/{i:04d}.png"
            left = first + (i // 8) * 12
            slot = i % 8
            row = {"index": i, "time_seconds": i / 24, "file": f"frames/{i:04d}.png"}
            if i > last_index:
                old = original["output_frames"][first * 2 // 3 + i]
                assert old["kind"] == "warp"
                copy_verified(regular / old["file"], path)
                row.update(kind="warp", source_index=last_index // 8)
            elif slot == 0:
                copy_verified(SOURCE / f"anchors/{left:04d}.png", path)
                row.update(kind="anchor", source_index=i // 8)
            elif mode == "direct":
                old = original["output_frames"][first * 2 // 3 + i]
                copy_verified(regular / old["file"], path)
                row.update(
                    kind="interpolation",
                    source_pair=[i // 8, i // 8 + 1],
                    timestep=f"{slot}/8",
                )
            else:
                p = ROOT / f"pair-{left:04d}"
                m = read(p / "rife/manifest.json")
                assert (
                    m["status"] == "complete"
                    and m["provenance"]["model"] == "RIFE 4.25"
                )
                src = p / "rife/frames" / f"{slot:04d}.png"
                assert sha(src) == m["output_frames"][slot]["sha256"]
                rgb = warp_at_time(
                    np.asarray(Image.open(src).convert("RGB")),
                    left / 24,
                    f / 24,
                    config["phrases"],
                )
                Image.fromarray(rgb).save(path)
                row.update(
                    kind="interpolation",
                    source_pair=[i // 8, i // 8 + 1],
                    timestep=f"{slot}/8",
                    aligned_interpolation_sha256=sha(src),
                    spatial_warp_after_interpolation=True,
                )
            row["sha256"] = sha(path)
            rows.append(row)
        subprocess.run(
            [
                "ffmpeg",
                "-v",
                "error",
                "-framerate",
                "24",
                "-i",
                str(dest / "frames/%04d.png"),
                "-frames:v",
                str(count),
                "-an",
                "-c:v",
                "libx264",
                "-crf",
                "18",
                "-pix_fmt",
                "yuv420p",
                "-movflags",
                "+faststart",
                str(dest / "preview.mp4"),
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
                str(dest / "preview.mp4"),
                "-f",
                "null",
                "-",
            ],
            check=True,
        )
        for row in rows:
            assert sha(dest / row["file"]) == row["sha256"]
        save(
            dest / "manifest.json",
            {
                "status": "complete",
                "provenance": {"model": "RIFE 4.25", "method": mode},
                "settings": {
                    "output_fps": 24,
                    "scale": 1,
                    "anchor_frames": list(range(0, last_index + 1, 8)),
                },
                "output_frames": rows,
                "final_holds": 0,
                "final_warps": plan.get("tail", 0),
                "video_sha256": sha(dest / "preview.mp4"),
            },
        )
        save(
            dest / "delivery-check.json",
            {
                "verified": True,
                "frames": count,
                "paintings": last_index // 8 + 1,
                "fps": 24,
                "all_paintings_preserved": True,
                "source_frames": list(range(first, last + 1, 12)),
            },
        )
    for start in (64, 160, 248, 352) if count > 100 else (0, 24, 48):
        samples = []
        for i in range(start, start + 9, 2):
            samples.append(
                [
                    (
                        Image.open(ROOT / mode / f"frames/{i:04d}.png").convert("RGB"),
                        f"{mode} · frame {i}",
                    )
                    for mode in ("direct", "explicit-motion")
                ]
            )
        sheet(samples, ROOT / f"comparison-{start:02d}.jpg", size=(576, 384))
    print(ROOT, flush=True)


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("stage", choices=["prepare", "infer", "compose"])
    p.add_argument("--full", action="store_true")
    args = p.parse_args()
    if args.full:
        ROOT = lab.OUT / "motion-aware-full"
    globals()[args.stage]()
