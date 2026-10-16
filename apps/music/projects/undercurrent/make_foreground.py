"""Original source tones with evolving envelopes; no reference audio is sampled."""

import hashlib
import json
from pathlib import Path

import numpy as np
import soundfile as sf
from scipy import signal

ROOT = Path(__file__).resolve().parent
RATE = 48000
OVERSAMPLE = 4
OUT = ROOT / "references/assets/foreground-v001"


def tone(freq, openness, hollow=False):
    sr = RATE * OVERSAMPLE
    t = np.arange(round(1.6 * sr)) / sr
    phase = 2 * np.pi * freq * t
    if hollow:
        # Inharmonic attack settles into a pitched, hollow body.
        index = 2.8 * np.exp(-t / 0.065) + 0.65 * np.exp(-t / 0.4)
        x = np.sin(phase + index * np.sin(phase * 1.501))
        x += 0.18 * np.sin(phase * 2.002) * np.exp(-t / 0.12)
        decay = 0.24 + 0.15 * openness
        attack = 0.004
    else:
        # Two detuned harmonic bodies, driven before tone shaping.
        x = (
            sum(
                np.sin(phase * d * h + 0.17 * h) / (h**1.12)
                for d in [0.998, 1.002]
                for h in range(1, 21)
            )
            / 3
        )
        x = np.tanh(x * (1.3 + openness))
        decay = 0.32 + 0.58 * openness
        attack = 0.014
    x = signal.sosfilt(signal.butter(3, 210, "highpass", fs=sr, output="sos"), x)
    dark = signal.sosfilt(signal.butter(3, 550, fs=sr, output="sos"), x)
    bright = signal.sosfilt(
        signal.butter(3, 1100 + openness * 3300, fs=sr, output="sos"), x
    )
    motion = (
        0.18 + 0.82 * np.sin(np.pi * np.minimum(t / (0.4 + openness * 0.5), 1)) ** 2
    ) * (0.4 + 0.6 * openness)
    x = (
        (dark * (1 - motion) + bright * motion)
        * (1 - np.exp(-t / attack))
        * np.exp(-t / decay)
    )
    # A quiet resonant edge makes the attack distinct without a white-noise click.
    if hollow:
        x += 0.07 * np.sin(phase * 3.02) * np.exp(-t / 0.045) * (1 - np.exp(-t / 0.003))
    x[-round(0.08 * sr) :] *= np.linspace(1, 0, round(0.08 * sr))
    return signal.resample_poly(x, 1, OVERSAMPLE)


def main():
    OUT.mkdir(parents=True, exist_ok=False)
    bank = []
    for name, freq, hollow in [
        ("ucpulse", 174.614, False),
        ("uchollowf", 174.614, True),
        ("ucholloweb", 155.563, True),
        ("uchollowc", 130.813, True),
    ]:
        for i in range(5):
            x = tone(freq, i / 4, hollow)
            # One common gain per family preserves the intended energy development.
            x *= 0.6 if hollow else 0.7
            assert np.max(np.abs(x)) < 0.95
            path = OUT / name / f"{i:02}.wav"
            path.parent.mkdir(exist_ok=True)
            sf.write(path, x, RATE, subtype="PCM_24")
            bank.append(
                {
                    "file": str(path.relative_to(ROOT)),
                    "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                }
            )
    (ROOT / "references/foreground-v001.json").write_text(
        json.dumps(
            {
                "origin": "Original oversampled procedural synthesis",
                "sample_rate": RATE,
                "oversampling": OVERSAMPLE,
                "files": bank,
            },
            indent=2,
        )
        + "\n"
    )


if __name__ == "__main__":
    main()
