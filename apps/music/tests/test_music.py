import json

import numpy as np
import pytest
import soundfile as sf

import music


@pytest.fixture
def tone(tmp_path):
    sr = 24000
    t = np.arange(sr * 12) / sr
    wave = 0.25 * np.sin(2 * np.pi * 1000 * t)
    path = tmp_path / "tone.wav"
    sf.write(path, np.column_stack([wave, -wave]), sr, subtype="FLOAT")
    return path


def test_spectrum_does_not_lose_antiphase_audio(tone):
    data, sr = music.read_audio(tone)
    f, _, power = music.spectrogram(data, sr)
    assert abs(f[power.mean(axis=1).argmax()] - 1000) < 10
    assert power.max() > -25


def test_inspection_reports_mono_cancellation(tone, tmp_path):
    report = music.inspect_audio(tone, tmp_path / "analysis", 120)
    assert report["lr_correlation"] == pytest.approx(-1)
    assert report["mono_rms_dbfs"] is None
    assert report["sample_peak_dbfs"] == pytest.approx(-12.04, abs=0.02)
    assert report["integrated_lufs"] is not None
    assert (tmp_path / "analysis" / "spectrogram.png").stat().st_size > 1000


def test_excerpt_exact_frames_preserves_original(tone, tmp_path):
    before = music.digest(tone)
    out = tmp_path / "excerpt.wav"
    music.excerpt(tone, out, 1, 2.5)
    assert sf.info(out).frames == 60000
    assert music.digest(tone) == before
    with pytest.raises(FileExistsError):
        music.excerpt(tone, out, 1, 2)
    with pytest.raises(ValueError):
        music.excerpt(tone, tmp_path / "bad.wav", 11, 3)


def test_mix_preserves_overload_and_rejects_misalignment(tone, tmp_path):
    out = tmp_path / "mix.wav"
    music.mix([tone, tone], out, 12)
    data, _ = music.read_audio(out)
    assert np.max(np.abs(data)) > 1
    short = tmp_path / "short.wav"
    music.excerpt(tone, short, 0, 2)
    with pytest.raises(ValueError):
        music.mix([tone, short], tmp_path / "bad.wav", 0)


def test_loudness_match_attenuates_only(tone, tmp_path):
    quiet = tmp_path / "quiet.wav"
    audio, sr = music.read_audio(tone)
    music.write_audio(quiet, audio * 0.5, sr)
    music.match([tone, quiet], tmp_path / "match")
    result = json.loads((tmp_path / "match" / "manifest.json").read_text())
    assert result["copies"][0]["gain_db"] == pytest.approx(-6.02, abs=0.03)
    assert result["copies"][1]["gain_db"] == 0


def test_calibration_and_silent_analysis(tone, tmp_path):
    out = tmp_path / "calibration"
    music.calibration(tone, out)
    key = json.loads((out / "answer-key.json").read_text())
    for name, condition in key.items():
        audio, sr = music.read_audio(out / name)
        if condition.startswith("silence from"):
            assert np.count_nonzero(audio[8 * sr : 10 * sr]) == 0
            assert np.count_nonzero(audio[: 8 * sr]) > 0
        if condition == "silence":
            report = music.inspect_audio(out / name, tmp_path / "silent")
            assert report["integrated_lufs"] is None
            assert report["sample_peak_dbfs"] is None


def test_review_dry_run_is_offline(tone, tmp_path, monkeypatch):
    def forbidden(*args, **kwargs):
        raise AssertionError("Network called")

    monkeypatch.setattr(music.httpx, "Client", forbidden)
    result = music.review(tone, tmp_path / "dry")
    assert result["sent"] is False
    assert not (tmp_path / "dry").exists()


def test_live_adapter_and_budget(tone, tmp_path, monkeypatch):
    monkeypatch.setattr(music, "ROOT", tmp_path)
    monkeypatch.setenv("OPENROUTER_API_KEY", "test-only")
    calls = []

    class Response:
        def __init__(self, body):
            self.body = body

        def json(self):
            return self.body

        def raise_for_status(self):
            pass

    class Client:
        def __init__(self, **kwargs):
            pass

        def __enter__(self):
            return self

        def __exit__(self, *args):
            pass

        def get(self, url):
            return Response(
                {
                    "data": [
                        {
                            "id": music.MODEL,
                            "architecture": {"input_modalities": ["audio"]},
                            "pricing": {"completion": "0.000012", "audio": "0.000002"},
                        }
                    ]
                }
            )

        def post(self, url, json, headers):
            calls.append(json)
            return Response(
                {
                    "id": "mock",
                    "choices": [
                        {"message": {"content": "Mock review"}, "finish_reason": "stop"}
                    ],
                    "usage": {"cost": 0.01},
                }
            )

    monkeypatch.setattr(music.httpx, "Client", Client)
    for i in range(4):
        assert music.review(tone, tmp_path / f"review-{i}", True)["sent"]
    with pytest.raises(ValueError, match="exhausted"):
        music.review(tone, tmp_path / "review-5", True)
    assert len(calls) == 4
    assert calls[0]["messages"][0]["content"][1]["type"] == "input_audio"
    assert "test-only" not in (tmp_path / "review-0" / "request.json").read_text()
