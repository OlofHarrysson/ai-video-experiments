"""Sculpt a blooming articulation from the same original printed dub object."""

import hashlib
import json
from pathlib import Path

import numpy as np
import soundfile as sf
from scipy.ndimage import gaussian_filter1d
from scipy.signal import butter, sosfilt

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "references/assets/samples/nsbloomwarm/01.wav"
OUT = ROOT / "references/assets/samples/nsbloomrise/01.wav"
if OUT.exists():
    raise FileExistsError(OUT)
audio, rate = sf.read(SOURCE, always_2d=True)
t = np.arange(len(audio)) / rate
# A measured local envelope preserves the object's grain while moving its weight.
rms = np.sqrt(gaussian_filter1d(np.mean(audio**2, axis=1), 0.018 * rate))
target = (1 - np.exp(-t / 0.085)) ** 2 * np.exp(-t / 0.34)
target *= rms.max() / target.max()
correction = np.minimum(target / np.maximum(rms, 1e-5), 3.5)
audio *= correction[:, None]
# Darkness opens with the bloom then folds back; no added oscillator or recording.
soft = sosfilt(butter(2, 650, fs=rate, output="sos"), audio, axis=0)
opening = (1 - np.exp(-t / 0.06)) * np.exp(-t / 0.45)
audio = soft * (1 - opening[:, None]) + audio * opening[:, None]
audio[:144] *= np.linspace(0, 1, 144)[:, None]
audio[-960:] *= np.linspace(1, 0, 960)[:, None]
audio *= 0.8 / np.max(np.abs(audio))
OUT.parent.mkdir(parents=True, exist_ok=True)
sf.write(OUT, audio, rate, subtype="PCM_24")
envelope = np.sqrt(gaussian_filter1d(np.mean(audio**2, axis=1), 0.010 * rate))
(ROOT / "references/performed-object.json").write_text(
    json.dumps(
        {
            "source": str(SOURCE.relative_to(ROOT)),
            "source_sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
            "origin": "Envelope and spectral articulation of the same original composite dub print",
            "processing": "18 ms smoothed RMS envelope; 85 ms curved rise and 340 ms fall; correction capped 3.5x; 650 Hz lowpass blend opens then darkens; 3 ms / 20 ms edge fades; peak 0.8",
            "envelope_peak_seconds": float(np.argmax(envelope) / rate),
            "output": str(OUT.relative_to(ROOT)),
            "sha256": hashlib.sha256(OUT.read_bytes()).hexdigest(),
        },
        indent=2,
    )
    + "\n"
)
