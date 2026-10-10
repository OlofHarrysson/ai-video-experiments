"""Join two preserved finished passages into the ten-second checkpoint."""

import argparse
import json
import subprocess
from pathlib import Path

from deforum_lab.records import require, save, sha

PROJECT = Path(__file__).resolve().parents[1]
FPS = 24
FRAMES = 240


def probe(path):
    result = subprocess.check_output([
        "ffprobe", "-v", "error", "-count_frames", "-select_streams", "v:0",
        "-show_entries", "stream=width,height,r_frame_rate,nb_read_frames,duration",
        "-of", "json", str(path),
    ])
    return json.loads(result)["streams"][0]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("jungle", type=Path)
    parser.add_argument("city", type=Path)
    parser.add_argument("--version", required=True)
    args = parser.parse_args()
    inputs = [args.jungle.resolve(), args.city.resolve()]
    require(all(p.is_relative_to(PROJECT) for p in inputs), "Use project media")
    specs = [probe(p) for p in inputs]
    require(all(s["r_frame_rate"] == "24/1" for s in specs), "Expected 24 fps")
    require(all((s["width"], s["height"]) == (1536, 1024) for s in specs), "Dimensions differ")
    counts = [int(s["nb_read_frames"]) for s in specs]
    overlap = sum(counts) - FRAMES
    require(1 <= overlap <= 12, "Expected a short threshold dissolve")
    root = PROJECT / "exports/cuts" / args.version
    require(not root.exists(), "Preserve existing cut")
    root.mkdir(parents=True)
    target = root / "preview.mp4"
    graph = (
        "[0:v]settb=1/24,setpts=PTS-STARTPTS[a];"
        "[1:v]settb=1/24,setpts=PTS-STARTPTS[b];"
        f"[a][b]xfade=transition=fade:duration={overlap / FPS:.9f}:"
        f"offset={(counts[0] - overlap) / FPS:.9f},format=yuv420p[v]"
    )
    command = ["ffmpeg", "-v", "error", "-n", "-i", str(inputs[0]), "-i", str(inputs[1]),
               "-filter_complex", graph, "-map", "[v]", "-an", "-frames:v", str(FRAMES),
               "-r", str(FPS), "-c:v", "libx264", "-preset", "slow", "-crf", "18",
               "-movflags", "+faststart", str(target)]
    record = {
        "inputs": [{"path": str(p.relative_to(PROJECT)), "sha256": sha(p), "probe": s}
                   for p, s in zip(inputs, specs)],
        "command": command, "overlap_frames": overlap,
        "transition_start_frame": counts[0] - overlap,
        "note": "Editorial dissolve between independent recurrent shots. No RIFE across the edit.",
    }
    save(root / "assembly-plan.json", record)
    subprocess.run(command, check=True)
    result = probe(target)
    require(int(result["nb_read_frames"]) == FRAMES and float(result["duration"]) == 10, "Cut timing differs")
    subprocess.run(["ffmpeg", "-v", "error", "-i", str(target), "-f", "null", "-"], check=True)
    require(all(sha(p) == row["sha256"] for p, row in zip(inputs, record["inputs"])), "Source changed")
    save(root / "cut.json", {**record, "verified": True, "output": result, "sha256": sha(target)})
    print(target)


if __name__ == "__main__":
    main()
