"""Compare the preserved v011/v012 solo reply renders without changing audio."""

import json
import sys
from pathlib import Path

import numpy as np
import soundfile as sf

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
import music

SPRINT = Path(__file__).resolve().parent
WINDOW_SECONDS = 0.1171875
RUNS = ["negative-ghost-final", "negative-ghost-v012"]


def read(name):
    folder = SPRINT / "screening" / name
    receipt = json.loads((folder / "render.json").read_text())
    assert receipt["status"] == "complete"
    assert receipt["settings"]["solo"] == ["ghost"]
    wave = folder / receipt["output"]["file"]
    trace_path = folder / receipt["event_trace"]["file"]
    assert music.digest(wave) == receipt["output"]["sha256"]
    assert music.digest(trace_path) == receipt["event_trace"]["sha256"]
    trace = json.loads(trace_path.read_text())
    assert trace["source_sha256"] == receipt["source"]["evaluated_sha256"]
    data, rate = sf.read(wave)
    return receipt, trace["events"], data, rate


def main():
    ra, a, x, sr = read(RUNS[0])
    rb, b, y, other_sr = read(RUNS[1])
    assert sr == other_sr == 48000 and x.shape == y.shape == (1440000, 2)
    assert len(a) == len(b) == 12
    rows = []
    for p, q in zip(a, b, strict=True):
        for key in [
            "onset_seconds",
            "onset_cycle",
            "end_cycle",
            "scheduled_duration_seconds",
        ]:
            assert p[key] == q[key]
        assert {k: v for k, v in p["controls"].items() if k != "gain"} == {
            k: v for k, v in q["controls"].items() if k != "gain"
        }
        t = p["onset_seconds"]
        i, j = round(t * sr), round((t + WINDOW_SECONDS) * sr)

        def level(data, start=i, end=j):
            return float(20 * np.log10(np.sqrt(np.mean(data[start:end] ** 2))))

        rows.append(
            {
                "onset_seconds": t,
                "slice_begin": p["controls"]["begin"],
                "gain_before": p["controls"]["gain"],
                "gain_after": q["controls"]["gain"],
                "rms_before_dbfs": level(x),
                "rms_after_dbfs": level(y),
                "rms_change_db": level(y) - level(x),
            }
        )
    output = {
        "status": "verified",
        "scope": "Solo ghost layer; onset windows include previous effect tails and wet-render variation. Signal level is not perceived audibility or preference.",
        "window_seconds": WINDOW_SECONDS,
        "input_audio_sha256": [ra["output"]["sha256"], rb["output"]["sha256"]],
        "input_event_trace_sha256": [
            ra["event_trace"]["sha256"],
            rb["event_trace"]["sha256"],
        ],
        "event_count": len(rows),
        "onsets_and_all_non_gain_controls_unchanged": True,
        "events": rows,
    }
    music.save_json(SPRINT / "reply-dynamics-study.json", output)
    print(
        "Verified 12 reply events: only gain controls change; hashes and timing match."
    )


if __name__ == "__main__":
    main()
