"""Original deterministic palette for Afterglow Transit, rendered at 96 kHz."""

import hashlib
import json
from pathlib import Path

import numpy as np
import soundfile as sf
from scipy import signal

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "references/assets/v001"
RATE = 96000
BPM = 126
RNG = np.random.default_rng(171026)


def filt(x, freq, kind="lowpass"):
    return signal.sosfilt(
        signal.butter(2, freq, kind, fs=RATE, output="sos"), x, axis=0
    )


def freq(midi):
    return 440 * 2 ** ((midi - 69) / 12)


def body(t, midi, bright=10):
    voices = []
    for detune in [0.9975, 1.0025]:
        phase = 2 * np.pi * freq(midi) * detune * t
        voices.append(
            sum(np.sin(phase * h + h * 0.23) / h**1.35 for h in range(1, bright + 1))
        )
    return np.column_stack(voices) * 0.35


def main():
    OUT.mkdir(parents=True, exist_ok=False)
    records = []

    def save(bank, index, x):
        x = np.asarray(x)
        n = min(len(x), round(RATE * 0.025))
        fade = np.linspace(1, 0, n)
        x[-n:] *= fade[:, None] if x.ndim == 2 else fade
        x = signal.resample_poly(x, 1, 2)
        assert np.max(np.abs(x)) < 0.98, (bank, np.max(np.abs(x)))
        p = OUT / bank / f"{index:02}.wav"
        p.parent.mkdir(exist_ok=True)
        sf.write(p, x, RATE // 2, subtype="PCM_24")
        records.append(
            {
                "file": str(p.relative_to(ROOT)),
                "sha256": hashlib.sha256(p.read_bytes()).hexdigest(),
            }
        )

    # Dm9, Bbmaj9, Fmaj9, Cadd9: close voice-leading above the bass.
    for i, notes in enumerate(
        [[57, 60, 64, 65], [57, 60, 62, 65], [57, 60, 64, 67], [55, 60, 62, 64]]
    ):
        t = np.arange(round(RATE * (8 * 60 / BPM + 0.5))) / RATE
        x = sum(body(t, n, 8) for n in notes) / 5
        dark, bright = filt(x, 1200), filt(x, 3400)
        motion = (0.3 + 0.3 * np.sin(t * 1.3))[:, None]
        env = np.minimum(t / 0.13, 1) * np.minimum(np.maximum((4.31 - t) / 0.5, 0), 1)
        pump = 0.24 + 0.76 * (1 - np.exp(-(t % (60 / BPM)) / 0.10))
        save(
            "atpad", i, (dark * (1 - motion) + bright * motion) * (env * pump)[:, None]
        )

    # One lead family across the notes D4 E4 F4 G4 A4 C5 D5.
    for i, midi in enumerate([62, 64, 65, 67, 69, 72, 74]):
        t = np.arange(round(RATE * 1.8)) / RATE
        x = body(t, midi, 16)
        dark, bright = filt(x, 1000), filt(x, 4500)
        opening = (0.12 + 0.7 * np.exp(-t / 0.19))[:, None]
        env = (1 - np.exp(-t / 0.012)) * np.exp(-t / 0.44)
        save(
            "atlead", i, (dark * (1 - opening) + bright * opening) * env[:, None] * 0.8
        )
        arp = np.sin(
            2 * np.pi * freq(midi) * t
            + 0.8 * np.exp(-t / 0.06) * np.sin(2 * np.pi * freq(midi) * 2 * t)
        )
        save(
            "atarp",
            i,
            filt(arp, 3500) * (1 - np.exp(-t / 0.004)) * np.exp(-t / 0.12) * 0.5,
        )

    t = np.arange(round(RATE * 0.7)) / RATE
    hz = 48 + 100 * np.exp(-t / 0.018) + 17 * np.exp(-t / 0.08)
    kick = np.sin(2 * np.pi * np.cumsum(hz) / RATE) * np.exp(-t / 0.17)
    kick += filt(RNG.normal(size=len(t)), 2200) * np.exp(-t / 0.007) * 0.18
    save("atkick", 0, np.tanh(kick * 1.6) * 0.8 * np.minimum(t / 0.0015, 1))
    for i, decay in enumerate([0.038, 0.16]):
        t = np.arange(round(RATE * 0.5)) / RATE
        noise = filt(filt(RNG.normal(size=len(t)), 6500, "highpass"), 13000)
        save("athat", i, noise * np.exp(-t / decay) * np.minimum(t / 0.001, 1) * 0.19)
    t = np.arange(round(RATE * 0.45)) / RATE
    noise = filt(filt(RNG.normal(size=len(t)), 1000, "highpass"), 7000)
    env = sum(
        np.where(t >= a, np.exp(-np.maximum(t - a, 0) / d), 0)
        for a, d in [(0, 0.006), (0.012, 0.006), (0.026, 0.06)]
    )
    save("atclap", 0, noise * env * 0.20)
    t = np.arange(round(RATE * 0.3)) / RATE
    perc = np.sin(
        2 * np.pi * 560 * t + 2 * np.exp(-t / 0.015) * np.sin(2 * np.pi * 813 * t)
    )
    save("atwood", 0, perc * np.exp(-t / 0.045) * np.minimum(t / 0.002, 1) * 0.5)
    t = np.arange(round(RATE * 3.8)) / RATE
    noise = filt(filt(RNG.normal(size=len(t)), 1500, "highpass"), 8000)
    save("atair", 0, noise * (np.sin(np.pi * t / 3.8) ** 2) * 0.10)
    (ROOT / "references/palette-v001.json").write_text(
        json.dumps(
            {
                "origin": "Original procedural synthesis; no reference sampling",
                "sample_rate": 48000,
                "synthesis_rate": RATE,
                "seed": 171026,
                "files": records,
            },
            indent=2,
        )
        + "\n"
    )


if __name__ == "__main__":
    main()
