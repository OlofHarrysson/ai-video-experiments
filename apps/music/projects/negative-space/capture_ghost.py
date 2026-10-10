"""Capture this study's own composite dub tail to become a later percussion object."""

import hashlib
import json
from pathlib import Path

import numpy as np
import soundfile as sf
from scipy.signal import butter, sosfilt

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "renders/v001/dub/render.wav"
OUT = ROOT / "references/assets/samples/nsghost/01.wav"
START = 1.0546875
END = 1.875

if OUT.exists():
    raise FileExistsError(OUT)
audio, rate = sf.read(SOURCE, always_2d=True)
segment = audio[round(START * rate) : round(END * rate)].copy()
segment = sosfilt(
    butter(3, [500, 3200], btype="bandpass", fs=rate, output="sos"), segment, axis=0
)
segment /= np.max(np.abs(segment))
segment = np.tanh(segment * 2.4)
segment[:240] *= np.linspace(0, 1, 240)[:, None]
segment[-720:] *= np.linspace(1, 0, 720)[:, None]
segment *= 0.76 / np.max(np.abs(segment))
OUT.parent.mkdir(parents=True, exist_ok=True)
sf.write(OUT, segment, rate, subtype="PCM_24")
(ROOT / "references/ghost.json").write_text(
    json.dumps(
        {
            "source": str(SOURCE.relative_to(ROOT)),
            "source_sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
            "window_seconds": [START, END],
            "transformation": "500–3200 Hz third-order bandpass; tanh saturation; edge fades; peak0.76",
            "output": str(OUT.relative_to(ROOT)),
            "sha256": hashlib.sha256(OUT.read_bytes()).hexdigest(),
            "purpose": "A composite dub tail (direct sound plus echo/reverb) becomes the return section’s syncopated percussion answer.",
        },
        indent=2,
    )
    + "\n"
)
