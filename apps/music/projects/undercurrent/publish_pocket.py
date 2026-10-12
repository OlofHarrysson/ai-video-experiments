"""Publish an offbeat chord alternative while preserving every existing track."""

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
BASE = ROOT / "exports/player-v002"
OUT = ROOT / "exports/player-v003"
RENDER = ROOT / "renders/pocket-v001-chords"
SOURCE = ROOT / "source/pocket-v001.strudel"


def main():
    if OUT.exists():
        raise FileExistsError(OUT)
    manifest = json.loads((BASE / "manifest.json").read_text())
    receipt = json.loads((RENDER / "render.json").read_text())
    assert receipt["status"] == "complete"
    baseline = ROOT / "renders/flow-v002-chords"
    old_receipt = json.loads((baseline / "render.json").read_text())
    samples = {(s["name"], s["index"]): s["sha256"] for s in receipt["samples"]}
    assert samples == {
        (s["name"], s["index"]): s["sha256"] for s in old_receipt["samples"]
    }
    old_source = (ROOT / "source/flow-v002.strudel").read_text().splitlines()
    new_source = SOURCE.read_text().splitlines()
    unchanged = ["kick", "clap", "hat", "brush", "openhat", "sub", "bass",
                 "landing", "fill", "intake", "held", "resolve", "reply"]
    for label in unchanged:
        assert next(s for s in old_source if s.startswith(label + ":")) == next(
            s for s in new_source if s.startswith(label + ":")
        )
    events = json.loads((RENDER / "events.json").read_text())["events"]
    rhythmic = [e for e in events if e["controls"].get("orbit") in [5, 6]]
    active_bars = list(range(11)) + [12, 13, 14]
    expected = sorted(
        bar + position for bar in active_bars
        for position in ([.125, .625] if bar % 2 == 0 else [.125])
    )
    assert sorted(e["onset_cycle"] for e in rhythmic) == expected
    assert all(e["controls"].get("delay") == 0 for e in rhythmic)
    assert not any(e["controls"].get("orbit") == 9 for e in events)
    data, rate = sf.read(RENDER / "render.wav", always_2d=True)
    assert rate == 48000 and data.shape == (1440000, 2)
    assert music.pcm_rail_metrics(data, sf.info(RENDER / "render.wav").subtype)[
        "pcm_rail_samples"
    ] == 0
    OUT.mkdir(parents=True)
    hashes, tracks = {}, []
    bed = np.zeros_like(data)
    for track in manifest["tracks"]:
        source = BASE / track["url"].lstrip("/")
        assert music.digest(source) == track["sha256"]
        destination = OUT / track["url"].lstrip("/")
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, destination)
        hashes[track["id"]] = music.digest(destination)
        assert hashes[track["id"]] == track["sha256"]
        item = copy.deepcopy(track)
        if track.get("alternativeGroup") == "chords":
            item["enabled"] = False
        else:
            audio, sr = sf.read(source, always_2d=True)
            assert sr == rate and audio.shape == data.shape
            bed += audio
        if track["id"] == "chords-flow":
            target = OUT / "audio/pocket/chords.wav"
            target.parent.mkdir(parents=True)
            shutil.copyfile(RENDER / "render.wav", target)
            tracks.append({
                "id": "chords-pocket", "name": "Chords · offbeat pocket",
                "enabled": True, "alternativeGroup": "chords",
                "url": "/audio/pocket/chords.wav", "sha256": music.digest(target),
                "waveform": np.sqrt(np.mean(
                    data.reshape(240, 6000, 2) ** 2, axis=(1, 2)
                )).round(5).tolist(),
            })
        tracks.append(item)
    mix = (bed + data) * manifest["gain"]
    assert np.max(np.abs(mix)) < 1
    mix_path = RENDER / "pocket.wav"
    sf.write(mix_path, mix, rate, subtype="FLOAT")
    metrics = music.inspect_audio(mix_path, RENDER / "mix-inspection")
    assert metrics["true_peak_dbtp"] < 0
    manifest["tracks"] = tracks
    music.save_json(OUT / "manifest.json", manifest)
    evidence = {
        "source_sha256": music.digest(SOURCE),
        "unchanged_audio": hashes, "unchanged_source_labels": unchanged,
        "samples_unchanged": True, "rhythmic_onsets": expected,
        "rhythmic_delay": 0, "reply_onsets": 0,
        "global_gain_unchanged": manifest["gain"], "mix": metrics,
        "tail_peak_dbfs": float(20 * np.log10(max(
            np.max(np.abs(mix[-960:])), 1e-15
        ))),
        "human_preference": "pending",
    }
    music.save_json(ROOT / "pocket-evidence.json", evidence)
    print(json.dumps({"bundle": str(OUT), "lufs": metrics["integrated_lufs"],
                      "true_peak": metrics["true_peak_dbtp"],
                      "rhythmic_onsets": len(expected)}, indent=2))


if __name__ == "__main__":
    main()
