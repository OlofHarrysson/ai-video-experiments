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


def test_live_adapter_records_cost_without_spending_limit(tone, tmp_path, monkeypatch):
    monkeypatch.setattr(music, "ROOT", tmp_path)
    monkeypatch.setenv("OPENROUTER_API_KEY", "test-only")
    (tmp_path / "work").mkdir()
    legacy = json.dumps({"output": "historical", "reserved_usd": 1.0}) + "\n"
    (tmp_path / "work" / "review-ledger.jsonl").write_text(legacy)
    calls = []

    class Response:
        is_error = False

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

        def get(self, url, **kwargs):
            return Response(
                {
                    "data": [
                        {
                            "id": music.MODEL,
                            "architecture": {"input_modalities": ["audio"]},
                            "supported_parameters": ["reasoning", "max_tokens"],
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
    for i in range(5):
        assert music.review(tone, tmp_path / f"review-{i}", True)["sent"]
    assert len(calls) == 5
    receipt = json.loads((tmp_path / "review-4" / "request.json").read_text())
    assert receipt["usage"]["cost"] == 0.01
    assert receipt["status"] == "complete"
    assert "request_reserve_usd" not in receipt
    assert (tmp_path / "work" / "review-ledger.jsonl").read_text().startswith(legacy)
    assert calls[0]["messages"][0]["content"][1]["type"] == "input_audio"
    assert "test-only" not in (tmp_path / "review-0" / "request.json").read_text()


def test_silence_intervals_require_all_channels_and_minimum_duration():
    data = np.ones((3000, 2)) * 0.1
    data[500:1500] = 0
    data[1600:1650] = 0
    data[2000:, 0] = 0
    assert music.silence_intervals(data, 1000) == [
        {"start_seconds": 0.5, "end_seconds": 1.5}
    ]
    assert music.silence_intervals(np.zeros((1000, 2)), 1000) == [
        {"start_seconds": 0.0, "end_seconds": 1.0}
    ]


def test_compare_detects_timing_error_without_aligning(tone, tmp_path):
    data, sr = music.read_audio(tone)
    shifted = tmp_path / "shifted.wav"
    music.write_audio(shifted, np.roll(data, 1, axis=0), sr)
    same = music.compare(tone, tone, tmp_path / "same")
    assert same["identical_samples"]
    assert same["residual_peak_dbfs"] is None
    changed = music.compare(tone, shifted, tmp_path / "changed")
    assert not changed["identical_samples"]
    residual, _ = music.read_audio(tmp_path / "changed" / "residual.wav")
    assert np.allclose(residual, np.roll(data, 1, axis=0) - data)
    short = tmp_path / "short.wav"
    music.excerpt(tone, short, 0, 2)
    with pytest.raises(ValueError, match="identical"):
        music.compare(tone, short, tmp_path / "bad")


@pytest.mark.parametrize("finish,content", [("length", "Partial text"), ("stop", "")])
def test_review_rejects_incomplete_result_but_preserves_cost(
    tone, tmp_path, monkeypatch, finish, content
):
    import httpx

    monkeypatch.setattr(music, "ROOT", tmp_path)
    monkeypatch.setenv("OPENROUTER_API_KEY", "test-only")
    calls = []

    def respond(request):
        if request.method == "GET":
            return httpx.Response(
                200,
                json={
                    "data": [
                        {
                            "id": music.MODEL,
                            "architecture": {"input_modalities": ["audio"]},
                            "supported_parameters": ["reasoning", "max_tokens"],
                        }
                    ]
                },
            )
        calls.append(json.loads(request.content))
        return httpx.Response(
            200,
            json={
                "choices": [{"message": {"content": content}, "finish_reason": finish}],
                "usage": {"cost": 0.02},
            },
        )

    client_class = httpx.Client
    monkeypatch.setattr(
        music.httpx,
        "Client",
        lambda **kwargs: client_class(transport=httpx.MockTransport(respond)),
    )
    out = tmp_path / "review"
    with pytest.raises(ValueError, match="Incomplete"):
        music.review(tone, out, True, "Report only silence.")
    assert len(calls) == 1
    assert calls[0]["messages"][0]["content"][0]["text"] == "Report only silence."
    assert not (out / "review.md").exists()
    receipt = json.loads((out / "request.json").read_text())
    assert receipt["status"] == "incomplete"
    assert receipt["usage"]["cost"] == 0.02


def test_transport_timeout_records_unknown_outcome_without_retry(
    tone, tmp_path, monkeypatch
):
    import httpx

    monkeypatch.setattr(music, "ROOT", tmp_path)
    monkeypatch.setenv("OPENROUTER_API_KEY", "test-only")
    posts = []

    def respond(request):
        if request.method == "GET":
            return httpx.Response(
                200,
                json={
                    "data": [
                        {
                            "id": music.MODEL,
                            "architecture": {"input_modalities": ["audio"]},
                            "supported_parameters": ["reasoning", "max_tokens"],
                        }
                    ]
                },
            )
        posts.append(request.method)
        raise httpx.ReadTimeout("test timeout", request=request)

    client_class = httpx.Client
    monkeypatch.setattr(
        music.httpx,
        "Client",
        lambda **kwargs: client_class(transport=httpx.MockTransport(respond)),
    )
    out = tmp_path / "review"
    with pytest.raises(httpx.ReadTimeout):
        music.review(tone, out, True)
    receipt = json.loads((out / "request.json").read_text())
    assert receipt["sent"] is None
    assert receipt["status"] == "transport_error"
    assert receipt["error_type"] == "ReadTimeout"
    assert "usage" not in receipt
    assert posts == ["POST"]
    assert not (out / "review.md").exists()


def test_pcm_positive_rail_is_not_missed(tmp_path):
    path = tmp_path / "clipped.wav"
    samples = np.zeros((24000, 2))
    samples[100:120, 0] = 1.2
    samples[400:405, 1] = -1.2
    sf.write(path, samples, 24000, subtype="PCM_16")
    data, _ = music.read_audio(path)
    assert data[100, 0] < 1
    # The old >=1 metric counts only negative saturation in a PCM16 file.
    assert np.sum(np.abs(data) >= 1) == 5
    measured = music.pcm_rail_metrics(data, sf.info(path).subtype)
    assert measured["pcm_rail_samples"] == 25
    assert measured["pcm_rail_longest_run_frames"] == 20
    assert music.pcm_rail_metrics(data * 0.9, "PCM_16")["pcm_rail_samples"] == 0
    assert music.pcm_rail_metrics(data, "FLOAT")["pcm_rail_samples"] is None


def test_reviews_overlap_network_calls_without_corrupting_ledger(
    tone, tmp_path, monkeypatch
):
    from concurrent.futures import ThreadPoolExecutor
    from threading import Barrier

    import httpx

    monkeypatch.setattr(music, "ROOT", tmp_path)
    monkeypatch.setenv("OPENROUTER_API_KEY", "test-only")
    gate = Barrier(2)

    def respond(request):
        if request.method == "GET":
            return httpx.Response(
                200,
                json={
                    "data": [
                        {
                            "id": music.MODEL,
                            "architecture": {"input_modalities": ["audio"]},
                            "supported_parameters": ["reasoning", "max_tokens"],
                        }
                    ]
                },
            )
        # Both paid requests must arrive before either returns; a network-wide lock deadlocks this.
        gate.wait(timeout=3)
        return httpx.Response(
            200,
            json={
                "choices": [
                    {
                        "message": {"content": "Controlled response"},
                        "finish_reason": "stop",
                    }
                ],
                "usage": {"cost": 0.01},
            },
        )

    client = httpx.Client
    monkeypatch.setattr(
        music.httpx,
        "Client",
        lambda **kw: client(transport=httpx.MockTransport(respond)),
    )
    with ThreadPoolExecutor(max_workers=2) as pool:
        jobs = [
            pool.submit(music.review, tone, tmp_path / f"review-{i}", True)
            for i in range(2)
        ]
        results = [job.result(timeout=10) for job in jobs]
    assert all(r["status"] == "complete" for r in results)
    rows = [
        json.loads(line)
        for line in (tmp_path / "work/review-ledger.jsonl").read_text().splitlines()
    ]
    assert len(rows) == 4 and len({r["request_id"] for r in rows}) == 2
    assert len([r for r in rows if r.get("status") == "complete"]) == 2


def test_catalog_failure_records_no_paid_dispatch(tone, tmp_path, monkeypatch):
    import httpx

    monkeypatch.setattr(music, "ROOT", tmp_path)
    monkeypatch.setenv("OPENROUTER_API_KEY", "test-only")
    methods = []

    def respond(request):
        methods.append(request.method)
        raise httpx.ConnectTimeout("catalog unavailable", request=request)

    client = httpx.Client
    monkeypatch.setattr(
        music.httpx,
        "Client",
        lambda **kw: client(transport=httpx.MockTransport(respond)),
    )
    out = tmp_path / "failed"
    with pytest.raises(httpx.ConnectTimeout):
        music.review(tone, out, True)
    receipt = json.loads((out / "request.json").read_text())
    assert receipt["sent"] is False and receipt["status"] == "preflight_error"
    assert methods == ["GET"] and "dispatch_at" not in receipt


@pytest.mark.parametrize(
    "parameters,expected",
    [(["max_tokens"], None), (["max_tokens", "reasoning"], "high")],
)
def test_explicit_audio_model_uses_catalog_reasoning_capability(
    tone, tmp_path, monkeypatch, parameters, expected
):
    import httpx

    monkeypatch.setattr(music, "ROOT", tmp_path)
    monkeypatch.setenv("OPENROUTER_API_KEY", "test-only")
    selected = "test/full-audio-model"
    posts = []

    def respond(request):
        if request.method == "GET":
            return httpx.Response(
                200,
                json={
                    "data": [
                        {
                            "id": selected,
                            "architecture": {"input_modalities": ["audio"]},
                            "supported_parameters": parameters,
                        }
                    ]
                },
            )
        posts.append(json.loads(request.content))
        return httpx.Response(
            200,
            json={
                "choices": [
                    {
                        "message": {"content": "Controlled reply"},
                        "finish_reason": "stop",
                    }
                ],
                "usage": {"cost": 0.01},
            },
        )

    client_class = httpx.Client
    monkeypatch.setattr(
        music.httpx,
        "Client",
        lambda **kwargs: client_class(transport=httpx.MockTransport(respond)),
    )
    receipt = music.review(
        tone, tmp_path / "review", True, model_id=selected, provider="TestProvider"
    )
    assert receipt["model"] == selected and receipt["reasoning_effort"] == expected
    assert posts[0]["model"] == selected
    assert posts[0]["provider"]["only"] == ["TestProvider"]
    assert receipt["provider_requested"] == "TestProvider"
    assert posts[0].get("reasoning") == ({"effort": "high"} if expected else None)
    assert posts[0]["provider"]["allow_fallbacks"] is False
