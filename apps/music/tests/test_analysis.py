import json

import numpy as np
import pytest
import soundfile as sf

import analysis
import music


def fixture_run(path):
    path.mkdir()
    rate = 12000
    t = np.arange(rate * 3) / rate
    wave = 0.25 * np.sin(2 * np.pi * 80 * t)
    wave[rate : 2 * rate] = 0
    renders = {}
    for name, gain in [("master", 1), ("bass", 0.5)]:
        f = path / f"{name}.wav"
        sf.write(f, np.column_stack([wave, wave]) * gain, rate, subtype="FLOAT")
        renders[name] = {"file": f.name, "sha256": music.digest(f)}
    music.save_json(
        path / "project-render.json",
        {
            "status": "complete",
            "cps": 1,
            "sample_rate": rate,
            "frames": len(t),
            "renders": renders,
        },
    )
    return path


def test_band_windows_measure_relative_level_and_preserve_silence(tmp_path):
    run = fixture_run(tmp_path / "run")
    analysis.analyze_project(run, tmp_path / "report", 0.5)
    report = json.loads((tmp_path / "report/analysis.json").read_text())
    rows = report["windows"]
    low = next(
        r
        for r in rows
        if r["stem"] == "bass" and r["band"] == "low" and r["window"] == 0
    )
    assert low["relative_to_master_db"] == pytest.approx(-6.0206, abs=0.002)
    quiet = next(
        r
        for r in rows
        if r["stem"] == "bass" and r["band"] == "full" and r["window"] == 2
    )
    assert quiet["rms_dbfs"] is None and quiet["relative_to_master_db"] is None
    assert len([r for r in rows if r["stem"] == "master" and r["band"] == "full"]) == 6
    assert "air" not in report["bands_hz"]
    assert (tmp_path / "report/levels.png").stat().st_size > 1000
    with pytest.raises(FileExistsError):
        analysis.analyze_project(run, tmp_path / "report")


def test_analysis_rejects_changed_audio_and_invalid_window(tmp_path):
    run = fixture_run(tmp_path / "run")
    with pytest.raises(ValueError, match="positive"):
        analysis.analyze_project(run, tmp_path / "bad", 0)
    with (run / "bass.wav").open("ab") as f:
        f.write(b"changed")
    with pytest.raises(ValueError, match="changed since"):
        analysis.analyze_project(run, tmp_path / "changed")
    assert not (tmp_path / "changed").exists()
