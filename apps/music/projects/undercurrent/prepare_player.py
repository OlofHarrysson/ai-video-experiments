"""Prepare aligned, independently mutable parts from the existing project renders."""

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

import numpy as np
import soundfile as sf

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
import music

TRACKS = [
    ("kick", "Kick", "The steady low drum", ["kick"]),
    ("bass", "Bass", "The repeating low notes", ["sub", "bass", "landing"]),
    ("clap", "Clap", "The backbeat", ["clap"]),
    ("hat", "Closed hi-hat", "Short ticking hits", ["hat"]),
    ("openhat", "Open hi-hat", "Longer, brighter hits", ["openhat"]),
    (
        "brush",
        "Brushed percussion",
        "Small shuffling hits and fills",
        ["brush", "fill"],
    ),
    (
        "chords",
        "Chord stabs & echoes",
        "The pitched sound above the bass",
        ["theme", "colour", "held", "resolve", "reply"],
    ),
    ("air", "Air sweep", "The soft noise before changes", ["intake"]),
]


def prepare(project, out):
    project, out = project.resolve(), out.resolve()
    if (out / "manifest.json").exists():
        raise FileExistsError("Player bundle is complete; choose a new output path")
    out.mkdir(parents=True, exist_ok=True)
    manifest = {
        "title": "Undercurrent",
        "duration": 30,
        "bpm": 128,
        "palettes": [],
        "tracks": [{"id": i, "name": n, "description": d} for i, n, d, _ in TRACKS],
    }
    evidence = {}
    for revision, title in [("v002", "Current"), ("smoke", "Smoke"), ("wire", "Wire")]:
        run = project / "renders" / revision
        receipt = json.loads((run / "master/render.json").read_text())
        source = run / "source.strudel"
        assert music.digest(source) == receipt["source"]["sha256"]
        config = json.loads(
            (project / f"assemblies/{revision}/project.json").read_text()
        )
        samples = [
            (project / f"assemblies/{revision}" / p).resolve()
            for p in config["samples"]
        ]
        summed = np.zeros((1440000, 2))
        tracks = {}
        for key, _, _, labels in TRACKS:
            destination = out / "audio" / revision / f"{key}.wav"
            destination.parent.mkdir(parents=True, exist_ok=True)
            if key == "bass":
                original = project / "renders/v002/bass/render.wav"
            elif key == "kick" and revision != "v002":
                original = out / "audio/v002/kick.wav"
            else:
                render = out / "renders" / revision / key
                if not (render / "render.json").exists():
                    cmd = [
                        "node",
                        str(music.ROOT / "renderer/render.mjs"),
                        str(source),
                        "--out",
                        str(render),
                        "--end",
                        "16",
                        "--sample-rate",
                        "48000",
                        "--timeout",
                        "60",
                    ]
                    for folder in samples:
                        cmd += ["--samples", str(folder)]
                    for label in labels:
                        cmd += ["--solo", label]
                    print(f"Rendering {title}: {key}", flush=True)
                    subprocess.run(cmd, check=True, timeout=180)
                r = json.loads((render / "render.json").read_text())
                assert r["status"] == "complete" and r["source"][
                    "sha256"
                ] == music.digest(source)
                assert r["settings"]["solo"] == labels
                assert r["samples"] == receipt["samples"]
                original = render / "render.wav"
            shutil.copyfile(original, destination)
            data, rate = sf.read(destination, always_2d=True)
            assert rate == 48000 and data.shape == summed.shape
            summed += data
            # Overview energy per track, used as a navigable visual guide.
            blocks = data.reshape(240, 6000, 2)
            envelope = np.sqrt(np.mean(blocks**2, axis=(1, 2)))
            tracks[key] = {
                "url": f"/audio/{revision}/{key}.wav",
                "sha256": music.digest(destination),
                "waveform": envelope.round(5).tolist(),
            }
        mix = out / f"{revision}-sum.wav"
        sf.write(mix, summed, 48000, subtype="FLOAT")
        metrics = music.loudness(mix)
        original, _ = sf.read(run / "master/render.wav", always_2d=True)
        residual = summed - original
        evidence[revision] = {
            "sum_lufs": metrics["integrated_lufs"],
            "sum_peak": float(np.max(np.abs(summed))),
            "residual_rms_dbfs": music.db(np.sqrt(np.mean(residual**2))),
        }
        manifest["palettes"].append(
            {
                "id": revision,
                "name": title,
                "tracks": tracks,
                "lufs": metrics["integrated_lufs"],
            }
        )
    target = min(p["lufs"] for p in manifest["palettes"])
    for p in manifest["palettes"]:
        p["gain"] = 10 ** ((target - p["lufs"]) / 20)
    manifest["target_lufs"] = target
    music.save_json(out / "manifest.json", manifest)
    music.save_json(project / "player-evidence.json", evidence)
    print(
        json.dumps(
            {"bundle": str(out), "target_lufs": target, "evidence": evidence}, indent=2
        )
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("project", type=Path)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    prepare(args.project, args.out)
