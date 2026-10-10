"""Verify the rendered foundation, phrase timing and final audio; save evidence."""

import hashlib
import json
from pathlib import Path

import numpy as np
import soundfile as sf

ROOT = Path(__file__).resolve().parent
RUN = ROOT / "renders/v002"
TRACE = ROOT / "screening/foundation-trace-v002/events.json"
BAR_SECONDS = 1.875


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def level(data):
    rms = float(np.sqrt(np.mean(data**2)))
    return round(20 * np.log10(rms), 3) if rms else None


def main():
    trace = json.loads(TRACE.read_text())
    receipt = json.loads(TRACE.with_name("render.json").read_text())
    assert receipt["source"]["sha256"] == digest(ROOT / "assemblies/v002/source.strudel")
    assert trace["source_sha256"] == receipt["source"]["evaluated_sha256"]
    events = trace["events"]
    active = [bar for bar in range(16) if bar not in [11, 15]]

    def signatures(bar, sound):
        return [
            [round(e["onset_cycle"] - bar, 8), e["controls"].get("note")]
            for e in events
            if int(e["onset_cycle"]) == bar and e["controls"]["s"] == sound
        ]

    for bar in active:
        assert signatures(bar, "bd") == [[0, None], [.25, None], [.5, None], [.75, None]]
        assert signatures(bar, "sine") == signatures(bar % 2, "sine")
    for bar in [11, 15]:
        assert not signatures(bar, "bd") and not signatures(bar, "sine")

    chord_onsets = [round(e["onset_cycle"], 8) for e in events if e["controls"]["s"] == "ucchord"]
    motif_bars = [bar for bar in range(15) if bar != 11]
    expected = [bar + offset for bar in motif_bars for offset in ([5/16, 11/16] if bar % 2 == 0 else [7/16])]
    assert chord_onsets == expected

    original = json.loads((ROOT / "screening/foundation-trace-v001/events.json").read_text())["events"]
    def foundation(rows):
        return [e for e in rows if e["controls"]["s"] in ["bd", "sine"]]
    assert foundation(events) == foundation(original)

    results = {}
    for stem in ["master", "drums", "bass", "theme", "details"]:
        path = RUN / stem / "render.wav"
        data, rate = sf.read(path, always_2d=True)
        metrics = json.loads((RUN / stem / "inspection/metrics.json").read_text())
        assert data.shape == (1440000, 2) and rate == 48000
        assert metrics["pcm_rail_samples"] == 0 and metrics["true_peak_dbtp"] < 0
        assert digest(path) == metrics["sha256"]
        results[stem] = {
            "sha256": digest(path),
            "integrated_lufs": metrics["integrated_lufs"],
            "true_peak_dbtp": metrics["true_peak_dbtp"],
            "pcm_rail_samples": metrics["pcm_rail_samples"],
            "bar_rms_dbfs": [level(data[round(i*BAR_SECONDS*rate):round((i+1)*BAR_SECONDS*rate)]) for i in range(16)],
            "last_20ms_peak_dbfs": round(20*np.log10(max(float(np.abs(data[-960:]).max()), 1e-12)), 2),
        }

    evidence = {
        "revision": "v002", "seconds": 30, "sample_rate": 48000,
        "foundation": {
            "active_bars_zero_based": active,
            "four_even_kicks_every_active_bar": True,
            "bass_matches_same_two_bar_phrase_every_active_bar": True,
            "foundation_trace_unchanged_from_v001": True,
            "motif_rhythm_preserved_through_voicing_change": True,
            "break_seconds": [20.625, 22.5], "return_seconds": 22.5,
            "trace_sha256": digest(TRACE),
            "scope": "Actual export schedule, not audibility. Landing sub at cycle 15 is a separate voice excluded from this trace.",
        },
        "renders": results,
        "screening": "Source/event and signal checks only. No claim of personal hearing or validated model taste judgment; Olof's verdict pending.",
    }
    (ROOT / "evidence.json").write_text(json.dumps(evidence, indent=2) + "\n")
    print(json.dumps({"foundation_verified": True, "master": results["master"]}, indent=2))


if __name__ == "__main__":
    main()
