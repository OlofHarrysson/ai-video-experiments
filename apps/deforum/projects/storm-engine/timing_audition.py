"""Shorten the selected film's timing, retaining every diffusion painting at 24 fps."""

import json
import subprocess
import sys
from pathlib import Path

APP = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(APP))
from media_review import build
from video_review import probe, sha256

PROJECT = Path(__file__).resolve().parent
SOURCE = PROJECT / "exports/v001/p05c-the-red-kite/through-2148/rife"
OUTPUT = PROJECT / "exports/timing-v001"
FACTORS = (2, 4)
FPS = 24


def main():
    original = json.loads((SOURCE / "manifest.json").read_text())
    source_hash = sha256(SOURCE / "preview.mp4")
    assert source_hash == original["video_sha256"]
    anchors = [r["index"] for r in original["output_frames"] if r["kind"] == "anchor"]
    assert len(anchors) == 180
    for factor in FACTORS:
        target = OUTPUT / f"{factor}x"
        frames = target / "frames"
        frames.mkdir(parents=True, exist_ok=True)
        assert all(index % factor == 0 for index in anchors)
        rows = []
        for index, source_row in enumerate(original["output_frames"][::factor]):
            source_frame = SOURCE / source_row["file"]
            assert sha256(source_frame) == source_row["sha256"]
            frame = frames / f"{index:04d}.png"
            if not frame.exists():
                frame.symlink_to(source_frame)
            assert sha256(frame) == source_row["sha256"]
            rows.append({**source_row, "parent_frame_index": source_row["index"],
                         "index": index, "time_seconds": index / FPS,
                         "file": str(frame.relative_to(target))})
        command = ["ffmpeg", "-v", "error", "-y", "-framerate", str(FPS),
                   "-i", str(frames / "%04d.png"), "-frames:v", str(len(rows)),
                   "-an", "-c:v", "libx264", "-preset", "fast", "-crf", "18",
                   "-pix_fmt", "yuv420p", "-movflags", "+faststart",
                   str(target / "preview.mp4")]
        subprocess.run(command, check=True)
        info = probe(target / "preview.mp4")
        assert info["frame_count"] == len(rows) == 1440 // factor
        assert abs(float(info["stream"]["duration"]) - 60 / factor) < 1e-6
        assert info["stream"]["avg_frame_rate"] == "24/1"
        assert all(abs(a["time_seconds"] - b["time_seconds"]) < 1e-6
                   for a, b in zip(rows, info["frames"]))
        subprocess.run(["ffmpeg", "-v", "error", "-xerror", "-i",
                        str(target / "preview.mp4"), "-f", "null", "-"], check=True)
        manifest = {"status": "complete", "mode": "retime", "speed_factor": factor,
                    "parent_manifest": str(SOURCE / "manifest.json"),
                    "parent_video_sha256": source_hash, "provenance": original["provenance"],
                    "settings": {"output_fps": FPS, "frame_count": len(rows)},
                    "output_frames": rows, "encode_command": command,
                    "video_sha256": sha256(target / "preview.mp4"),
                    "anchors_verified": True, "full_decode_verified": True,
                    "paintings_retained": sum(r["kind"] == "anchor" for r in rows)}
        assert manifest["paintings_retained"] == 180
        (target / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
        print(f"Verified {factor}x: {len(rows)} frames, {60 / factor:g} seconds, 180 paintings", flush=True)
    assert sha256(SOURCE / "preview.mp4") == source_hash
    print(build(APP / "media_review/sessions/storm-engine-timing.json",
                PROJECT / "exports/media-review-timing-v001", local=True))


if __name__ == "__main__":
    main()
