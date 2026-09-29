# /// script
# requires-python = ">=3.11"
# dependencies = ["numpy", "soundfile"]
# ///
"""Measure the pitch each downloaded sample actually plays.

Sample libraries disagree about octave numbering, so the score maps notes by
measured pitch rather than by file name. Writes samples/pitches.json:
{"harp/KSHarp_D4_mf.wav": {"midi": 62, "cents": -3.1, "hz": 293.1}, ...}
"""
import json
import math
from pathlib import Path

import numpy as np
import soundfile as sf

ROOT = Path(__file__).resolve().parent.parent
SAMPLES = ROOT / "samples"
NAMES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]


def f0(x: np.ndarray, rate: int) -> float:
    """YIN-style cumulative mean normalized difference on a steady window."""
    lo, hi = 25.0, 4400.0
    x = x - x.mean()
    max_lag = int(rate / lo)
    n = len(x) - max_lag
    if n <= 256:
        raise ValueError("window too short")
    d = np.zeros(max_lag)
    for lag in range(1, max_lag):
        diff = x[:n] - x[lag : lag + n]
        d[lag] = np.dot(diff, diff)
    cmnd = np.ones(max_lag)
    running = np.cumsum(d[1:])
    cmnd[1:] = d[1:] * np.arange(1, max_lag) / np.maximum(running, 1e-12)
    min_lag = int(rate / hi)
    lags = np.arange(min_lag, max_lag - 1)
    below = lags[cmnd[min_lag : max_lag - 1] < 0.15]
    if len(below):
        lag = below[0]
        while lag + 1 < max_lag - 1 and cmnd[lag + 1] < cmnd[lag]:
            lag += 1
    else:
        lag = min_lag + int(np.argmin(cmnd[min_lag : max_lag - 1]))
    a, b, c = cmnd[lag - 1], cmnd[lag], cmnd[lag + 1]
    shift = 0.5 * (a - c) / (a - 2 * b + c) if (a - 2 * b + c) != 0 else 0.0
    return rate / (lag + shift)


def measure(path: Path) -> dict:
    audio, rate = sf.read(path, always_2d=True)
    mono = audio.mean(axis=1)
    # Skip the attack, then take the loudest steady stretch.
    start = int(0.08 * rate)
    win = int(0.25 * rate)
    seg = mono[start : start + win * 4]
    hops = max(1, (len(seg) - win) // (win // 2) + 1)
    best = max(
        range(hops),
        key=lambda i: float(np.sum(seg[i * win // 2 : i * win // 2 + win] ** 2)),
    )
    window = seg[best * win // 2 : best * win // 2 + win]
    # Downsample for speed on low notes; the pitch survives.
    step = 2 if rate > 48000 else 1
    hz = f0(window[::step], rate // step)
    midi_float = 69 + 12 * math.log2(hz / 440)
    midi = round(midi_float)
    return {"midi": midi, "note": f"{NAMES[midi % 12]}{midi // 12 - 1}", "cents": round(100 * (midi_float - midi), 1), "hz": round(hz, 2)}


def main() -> None:
    result = {}
    for path in sorted(SAMPLES.glob("*/*.wav")):
        key = f"{path.parent.name}/{path.name}"
        result[key] = measure(path)
        m = result[key]
        print(f"{key:58s} {m['note']:4s} {m['cents']:+6.1f}c {m['hz']:8.2f} Hz")
    (SAMPLES / "pitches.json").write_text(json.dumps(result, indent=2) + "\n")


if __name__ == "__main__":
    main()
