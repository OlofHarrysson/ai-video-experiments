"""Breathy pitched-noise chord samples; the original score and other sounds stay fixed."""

import json
from pathlib import Path

import numpy as np
import soundfile as sf
from make_comparison_palettes import digest
from scipy.signal import butter, iirpeak, lfilter, sosfilt

ROOT = Path(__file__).resolve().parent
RATE = 48000
SEED = 2026101029
NOTES = [[56, 60, 63, 67], [58, 60, 65, 67]]
OUT = ROOT / "references/assets/haze/ucchord"


def main():
    if OUT.exists():
        raise FileExistsError(OUT)
    OUT.mkdir(parents=True)
    rng = np.random.default_rng(SEED)
    records = []
    for index, notes in enumerate(NOTES):
        t = np.arange(60000) / RATE
        tone = np.zeros(len(t))
        for midi in notes:
            freq = 440 * 2 ** ((midi - 69) / 12)
            voice = np.zeros(len(t))
            for harmonic, amplitude in [(1, 1), (2, 0.23), (3, 0.07)]:
                b, a = iirpeak(freq * harmonic, 20, fs=RATE)
                breath = lfilter(b, a, rng.normal(size=len(t)))
                breath /= max(np.std(breath), 1e-12)
                voice += breath * amplitude
            voice += 0.3 * np.sin(2 * np.pi * freq * t + rng.uniform(0, 2 * np.pi))
            tone += voice
        tone = sosfilt(butter(2, 1700, fs=RATE, output="sos"), tone)
        tone *= (1 - np.exp(-t / 0.022)) * np.exp(-t / 0.24)
        tone[:240] *= np.linspace(0, 1, 240)
        tone[-960:] *= np.linspace(1, 0, 960)
        tone *= 0.8 / np.max(np.abs(tone))
        path = OUT / f"{index:02d}.wav"
        sf.write(path, tone, RATE, subtype="PCM_24")
        records.append(
            {
                "file": str(path.relative_to(ROOT)),
                "sha256": digest(path),
                "notes_midi": notes,
            }
        )
    (ROOT / "references/haze.json").write_text(
        json.dumps(
            {
                "origin": "Original deterministic pitched-noise synthesis",
                "seed": SEED,
                "sample_rate": RATE,
                "design": "Noise resonators at the original chord pitches with a quiet sine component; 22ms attack, 240ms decay, no hard saturation",
                "outputs": records,
            },
            indent=2,
        )
        + "\n"
    )


if __name__ == "__main__":
    main()
