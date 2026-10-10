"""Add one chord-only comparison to the player, preserving its other seven files."""

import copy
import json
import sys
from pathlib import Path

import numpy as np
import soundfile as sf

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
import music

ROOT = Path(__file__).resolve().parent
BUNDLE = ROOT / "exports/player-v001"


def main():
    manifest_path = BUNDLE / "manifest.json"
    old_bytes = manifest_path.read_bytes()
    manifest = json.loads(old_bytes)
    if any(p["id"] == "haze" for p in manifest["palettes"]):
        raise FileExistsError("Haze is already published")
    original = next(p for p in manifest["palettes"] if p["id"] == "v002")
    old_path = BUNDLE / original["tracks"]["chords"]["url"].lstrip("/")
    old, rate = sf.read(old_path, always_2d=True)
    new_path = ROOT / "renders/haze-chords/render.wav"
    new, new_rate = sf.read(new_path, always_2d=True)
    assert rate == new_rate == 48000 and old.shape == new.shape == (1440000, 2)
    before = json.loads((BUNDLE / "renders/v002/chords/render.json").read_text())
    after = json.loads((ROOT / "renders/haze-chords/render.json").read_text())
    assert before["source"]["evaluated_sha256"] == after["source"]["evaluated_sha256"]
    assert after["status"] == "complete"
    assert (
        music.pcm_rail_metrics(new, sf.info(new_path).subtype)["pcm_rail_samples"] == 0
    )
    factor = np.sqrt(np.mean(old**2) / np.mean(new**2))
    new *= factor
    out = BUNDLE / "audio/haze/chords.wav"
    if out.exists():
        raise FileExistsError(out)
    out.parent.mkdir(parents=True)
    sf.write(out, new, rate, subtype="FLOAT")
    palette = copy.deepcopy(original)
    palette["id"] = "haze"
    palette["name"] = "Haze · new chords"
    palette["tracks"]["chords"] = {
        "url": "/audio/haze/chords.wav",
        "sha256": music.digest(out),
        "waveform": np.sqrt(np.mean(new.reshape(240, 6000, 2) ** 2, axis=(1, 2)))
        .round(5)
        .tolist(),
    }
    bed = np.zeros_like(new)
    unchanged = {}
    for key, track in original["tracks"].items():
        if key == "chords":
            continue
        assert palette["tracks"][key] == track
        path = BUNDLE / track["url"].lstrip("/")
        assert music.digest(path) == track["sha256"]
        data, sr = sf.read(path, always_2d=True)
        assert sr == rate and data.shape == new.shape
        bed += data
        unchanged[key] = track["sha256"]
    mix = (bed + new) * palette["gain"]
    assert np.max(np.abs(mix)) < 0.95
    mixpath = ROOT / "renders/haze-chords/haze.wav"
    sf.write(mixpath, mix, rate, subtype="FLOAT")
    metrics = music.inspect_audio(mixpath, ROOT / "renders/haze-chords/mix-inspection")
    assert metrics["true_peak_dbtp"] < 0
    palette["lufs"] = metrics["integrated_lufs"]
    # Retain Current's gain so every other part remains sample-for-sample unchanged.
    manifest["palettes"].append(palette)
    backup = BUNDLE / "manifest-before-haze.json"
    if backup.exists():
        raise FileExistsError(backup)
    backup.write_bytes(old_bytes)
    tmp = BUNDLE / "manifest-haze.tmp"
    tmp.write_text(json.dumps(manifest, indent=2) + "\n")
    tmp.replace(manifest_path)
    evidence = {
        "baseline": "Current v002 player mix",
        "changed_part": "chords",
        "unchanged_parts": unchanged,
        "same_score_sha256": after["source"]["sha256"],
        "same_evaluated_score_sha256": after["source"]["evaluated_sha256"],
        "chord_only_gain_db": float(20 * np.log10(factor)),
        "global_gain_unchanged": palette["gain"],
        "chords_sha256": music.digest(out),
        "mix": metrics,
        "method": "Only the new chord stem is energy-matched. Other seven stem URLs, samples and playback gain are identical to Current.",
    }
    (ROOT / "haze-evidence.json").write_text(json.dumps(evidence, indent=2) + "\n")
    print(
        json.dumps(
            {
                "mix": str(mixpath),
                "integrated_lufs": metrics["integrated_lufs"],
                "true_peak_dbtp": metrics["true_peak_dbtp"],
                "unchanged_parts": list(unchanged),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
