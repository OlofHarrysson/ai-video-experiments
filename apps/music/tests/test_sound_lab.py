import json

import numpy as np
import pytest
import soundfile as sf

import sound_lab


def test_windows_stereo_cancellation_silence_and_short_tail():
    x = np.r_[np.ones(100) * 0.25, np.zeros(100), [0.5]]
    rows = sound_lab.windows(np.column_stack([x, -x]), 1000)
    assert rows[0]["rms_dbfs"] == pytest.approx(-12.0412, abs=0.001)
    assert rows[1]["rms_dbfs"] is None
    assert rows[2]["peak_dbfs"] == pytest.approx(-6.0206, abs=0.001)


def test_report_crops_matches_overload_and_rejects_bad_windows(tmp_path):
    sr = 12000
    t = np.arange(sr * 2) / sr
    x = np.sin(2 * np.pi * 440 * t)
    sf.write(tmp_path / "loud.wav", x * 1.15, sr, subtype="FLOAT")
    sf.write(tmp_path / "quiet.wav", x * 0.15, sr, subtype="FLOAT")
    recipe = tmp_path / "recipe.json"
    config = {
        "duration": 1,
        "inputs": [
            {"name": "Loud", "path": "loud.wav", "start": 0.5, "role": "reference"},
            {"name": "Quiet", "path": "quiet.wav", "role": "mix"},
        ],
    }
    recipe.write_text(json.dumps(config))
    out = tmp_path / "report"
    sound_lab.build(recipe, out)
    report = json.loads((out / "report.json").read_text())
    assert report["status"] == "complete"
    rows = report["inputs"]
    assert rows[0]["metrics"]["samples_at_or_above_full_scale"] > 0
    assert (
        abs(
            rows[0]["matching"]["integrated_lufs"]
            - rows[1]["matching"]["integrated_lufs"]
        )
        < 0.1
    )
    assert all(r["matching"]["true_peak_dbtp"] <= -0.9 for r in rows)
    data, _rate = sf.read(out / "01/excerpt.wav")
    original, _ = sf.read(tmp_path / "loud.wav")
    np.testing.assert_array_equal(data, original[sr // 2 : sr * 3 // 2])
    m = sound_lab.momentary(out / "02/excerpt.wav")
    assert m[0]["momentary_lufs"] is None
    assert m[3]["momentary_lufs"] is not None
    with pytest.raises(FileExistsError):
        sound_lab.build(recipe, out)
    config["duration"] = 3
    recipe.write_text(json.dumps(config))
    with pytest.raises(ValueError, match="outside"):
        sound_lab.build(recipe, tmp_path / "invalid")
    assert not (tmp_path / "invalid").exists()
