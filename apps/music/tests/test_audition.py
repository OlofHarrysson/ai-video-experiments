import json

import numpy as np
import pytest
import soundfile as sf

import audition
import music


def test_pair_exact_windows_gap_matching_and_private_order(tmp_path, monkeypatch):
    rate = 12000
    t = np.arange(rate * 5) / rate
    tone = np.column_stack([np.sin(2 * np.pi * 240 * t)] * 2) * 0.2
    first, second = tmp_path / "first.wav", tmp_path / "second.wav"
    music.write_audio(first, tone, rate)
    music.write_audio(second, tone * 0.5, rate)
    monkeypatch.setattr(audition.secrets, "randbelow", lambda n: 1)
    out = tmp_path / "pair"
    audition.make_audition(first, second, out, 1, 1, 2, 0.5)
    key = json.loads((out / "answer-key.json").read_text())
    assert key["order"] == {"A": 2, "B": 1}
    audio, sr = sf.read(out / "audition.wav", always_2d=True)
    assert len(audio) == rate * 4.5 and sr == rate
    assert not np.any(audio[2 * rate : int(2.5 * rate)])
    # FFmpeg reports LUFS to two decimals; compare level, not sample identity.
    a_rms = np.sqrt(np.mean(audio[: 2 * rate] ** 2))
    b_rms = np.sqrt(np.mean(audio[int(2.5 * rate) :] ** 2))
    assert abs(20 * np.log10(a_rms / b_rms)) < 0.1
    prompt = (out / "prompt.txt").read_text()
    assert "first.wav" not in prompt and "second.wav" not in prompt
    assert music.digest(first) == key["source_windows"][0]["sha256"]
    with pytest.raises(FileExistsError):
        audition.make_audition(first, second, out, duration=2)
    with pytest.raises(ValueError, match="exceeds source"):
        audition.make_audition(first, second, tmp_path / "bad", duration=6)


def test_identical_control_is_preserved(tmp_path):
    rate = 12000
    wave = np.sin(2 * np.pi * 80 * np.arange(4 * rate) / rate) * 0.1
    f = tmp_path / "tone.wav"
    music.write_audio(f, wave, rate)
    audition.make_audition(f, f, tmp_path / "control", duration=2, gap=1)
    key = json.loads((tmp_path / "control/answer-key.json").read_text())
    assert key["input_excerpts_identical"]
    a, _ = sf.read(tmp_path / "control/audition.wav")
    np.testing.assert_array_equal(a[: 2 * rate], a[3 * rate :])
