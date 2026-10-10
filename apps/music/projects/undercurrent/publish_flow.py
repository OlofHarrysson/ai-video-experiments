"""Publish the original and revised chord rhythm as alternative player rows."""

import copy
import json
import shutil
import sys
from pathlib import Path

import numpy as np
import soundfile as sf

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
import music

ROOT = Path(__file__).resolve().parent
BASE = ROOT / "exports/player-v001"
OUT = ROOT / "exports/player-v002"
RENDER = ROOT / "renders/flow-v002-chords"


def main():
    if OUT.exists():
        raise FileExistsError(OUT)
    original = json.loads((BASE / "manifest.json").read_text())
    current = next(p for p in original["palettes"] if p["id"] == "v002")
    receipt = json.loads((RENDER / "render.json").read_text())
    assert receipt["status"] == "complete"
    baseline_receipt = json.loads(
        (BASE / "renders/v002/chords/render.json").read_text()
    )
    # Every loaded chord sample has the same hash as the original bank.
    sample_manifest = receipt["samples"]
    baseline_samples = baseline_receipt["samples"]
    baseline_hashes = {(s["name"], s["index"]): s["sha256"] for s in baseline_samples}
    assert all(
        baseline_hashes[(s["name"], s["index"])] == s["sha256"] for s in sample_manifest
    )
    events = json.loads((RENDER / "events.json").read_text())["events"]
    rhythmic = [e for e in events if e["controls"].get("orbit") in [5, 6]]
    assert len(rhythmic) == 28
    assert all(e["onset_cycle"] % 1 in [0.25, 0.75] for e in rhythmic)
    assert not any(e["controls"].get("orbit") == 9 for e in events)
    old_source = (ROOT / "assemblies/v002/source.strudel").read_text()
    new_source = (ROOT / "source/flow-v002.strudel").read_text()
    unchanged_labels = [
        "kick",
        "clap",
        "hat",
        "brush",
        "openhat",
        "sub",
        "bass",
        "landing",
        "fill",
        "intake",
    ]
    for label in unchanged_labels:
        old = next(
            line for line in old_source.splitlines() if line.startswith(label + ":")
        )
        new = next(
            line for line in new_source.splitlines() if line.startswith(label + ":")
        )
        assert old == new
    data, rate = sf.read(RENDER / "render.wav", always_2d=True)
    assert rate == 48000 and data.shape == (1440000, 2)
    assert (
        music.pcm_rail_metrics(data, sf.info(RENDER / "render.wav").subtype)[
            "pcm_rail_samples"
        ]
        == 0
    )
    # Keep note velocity and revised delay balance; no whole-mix normalization.
    OUT.mkdir(parents=True)
    tracks, hashes = [], {}
    bed = np.zeros_like(data)
    for track in original["tracks"]:
        key = track["id"]
        audio = current["tracks"][key]
        source = BASE / audio["url"].lstrip("/")
        assert music.digest(source) == audio["sha256"]
        destination = OUT / audio["url"].lstrip("/")
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, destination)
        item = {
            "id": key,
            "name": track["name"],
            "enabled": True,
            **copy.deepcopy(audio),
        }
        if key == "chords":
            item.update(
                id="chords-original",
                name="Chords · original rhythm",
                enabled=False,
                alternativeGroup="chords",
            )
            new = copy.deepcopy(item)
            new.update(
                id="chords-flow",
                name="Chords · steady rhythm",
                enabled=True,
                url="/audio/flow/chords.wav",
            )
            target = OUT / "audio/flow/chords.wav"
            target.parent.mkdir(parents=True)
            shutil.copyfile(RENDER / "render.wav", target)
            new["sha256"] = music.digest(target)
            new["waveform"] = (
                np.sqrt(np.mean(data.reshape(240, 6000, 2) ** 2, axis=(1, 2)))
                .round(5)
                .tolist()
            )
            tracks.append(new)
        else:
            hashes[key] = music.digest(destination)
            audio_data, sr = sf.read(destination, always_2d=True)
            assert sr == rate and audio_data.shape == data.shape
            bed += audio_data
        tracks.append(item)
    mix = (bed + data) * current["gain"]
    assert np.max(np.abs(mix)) < 1
    mix_path = RENDER / "flow.wav"
    sf.write(mix_path, mix, rate, subtype="FLOAT")
    metrics = music.inspect_audio(mix_path, RENDER / "mix-inspection")
    assert metrics["true_peak_dbtp"] < 0
    manifest = {
        "version": 2,
        "title": "Undercurrent",
        "duration": 30,
        "bpm": 128,
        "gain": current["gain"],
        "tracks": tracks,
    }
    music.save_json(OUT / "manifest.json", manifest)
    evidence = {
        "source_sha256": music.digest(ROOT / "source/flow-v002.strudel"),
        "unchanged_parts": hashes,
        "unchanged_source_labels": unchanged_labels,
        "same_samples": sample_manifest,
        "rhythmic_onsets": len(rhythmic),
        "onset_positions_per_bar": [0.25, 0.75],
        "reply_onsets": 0,
        "global_gain_unchanged": current["gain"],
        "mix": metrics,
    }
    music.save_json(ROOT / "flow-evidence.json", evidence)
    print(
        json.dumps(
            {
                "bundle": str(OUT),
                "lufs": metrics["integrated_lufs"],
                "true_peak": metrics["true_peak_dbtp"],
                "rhythmic_onsets": len(rhythmic),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
