"""A softer original dub object, designed after v003's spiky-attack critique."""

import hashlib
import json
from pathlib import Path

import numpy as np
import soundfile as sf
from scipy.signal import butter, sosfilt

ROOT = Path(__file__).resolve().parent
RATE = 48000
OUT = ROOT / "references/assets/samples/nscloud/01.wav"
RNG = np.random.default_rng(2026101004)
if OUT.exists():
    raise FileExistsError(OUT)
t = np.arange(round(1.3 * RATE)) / RATE
raw = np.zeros(len(t))
for fundamental in [174.614, 207.652, 261.626, 311.127]:
    for ratio in [0.9971, 1.0018]:
        for harmonic in range(1, 25):
            raw += (
                np.sin(
                    2 * np.pi * fundamental * ratio * harmonic * t
                    + RNG.uniform(0, 2 * np.pi)
                )
                / harmonic**1.3
            )
raw = np.tanh(raw * 0.3)
bright = sosfilt(butter(3, 2200, fs=RATE, output="sos"), raw)
dark = sosfilt(butter(3, 550, fs=RATE, output="sos"), raw)
colour = np.exp(-t / 0.15)
audio = (
    (bright * colour + dark * (1 - colour))
    * (1 - np.exp(-t / 0.011))
    * np.exp(-t / 0.24)
)
audio = sosfilt(butter(3, 260, fs=RATE, btype="highpass", output="sos"), audio)
audio[-480:] *= np.linspace(1, 0, 480)
audio *= 0.8 / np.max(np.abs(audio))
OUT.parent.mkdir(parents=True, exist_ok=True)
sf.write(OUT, audio, RATE, subtype="PCM_24")
(ROOT / "references/cloud.json").write_text(
    json.dumps(
        {
            "origin": "Original deterministic mathematical synthesis",
            "seed": 2026101004,
            "notes": "F3 Ab3 C4 Eb4, two detuned partial sets per note",
            "envelope": "11ms softened attack,240ms decay,1.3sec preserved tail",
            "colour": "Crossfade2200Hz to550Hz lowpass voices over150ms;260Hz highpass",
            "output": str(OUT.relative_to(ROOT)),
            "sha256": hashlib.sha256(OUT.read_bytes()).hexdigest(),
        },
        indent=2,
    )
    + "\n"
)
