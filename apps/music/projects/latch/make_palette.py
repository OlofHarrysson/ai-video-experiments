"""Original rough breath, wood and folded-bass objects for Latch."""

import hashlib
import json
from pathlib import Path

import numpy as np
import soundfile as sf
from scipy import signal

ROOT = Path(__file__).resolve().parent
RATE = 48000
SEED = 40831
OUT = ROOT / "references/assets/samples"
rng = np.random.default_rng(SEED)
records = []


def save(name, x, recipe):
    path = OUT / name / "00.wav"
    if path.exists():
        raise FileExistsError(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    x = x - np.mean(x)
    fade = min(240, len(x) // 4)
    x[:fade] *= np.linspace(0, 1, fade)
    x[-fade:] *= np.linspace(1, 0, fade)
    x = x / max(np.max(np.abs(x)), 1e-8) * 0.72
    sf.write(path, x, RATE, subtype="PCM_24")
    records.append(
        {
            "sound": name,
            "file": str(path.relative_to(ROOT)),
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            "recipe": recipe,
            "frames": len(x),
            "sample_rate": RATE,
        }
    )


t = np.arange(round(0.42 * RATE)) / RATE
noise = rng.standard_normal(len(t))
body = signal.sosfilt(
    signal.butter(2, [240, 1700], fs=RATE, btype="bandpass", output="sos"), noise
)
air = signal.sosfilt(
    signal.butter(2, [1700, 4300], fs=RATE, btype="bandpass", output="sos"), noise
)
env = (1 - np.exp(-t / 0.009)) * np.exp(-t / 0.083)
pulses = 0.65 + 0.35 * np.sin(2 * np.pi * (27 * t - 17 * t * t)) ** 2
save(
    "lashuck",
    np.tanh(4 * body) * env * pulses + 0.2 * air * env,
    "Bandlimited friction noise, rough pulsed breath; no voice or recording",
)

t = np.arange(round(0.23 * RATE)) / RATE
freq = 178 + 110 * np.exp(-t / 0.009)
phase = 2 * np.pi * np.cumsum(freq) / RATE
knock = (
    np.sin(phase) + 0.35 * np.sin(2.71 * phase) + 0.13 * np.sin(5.03 * phase)
) * np.exp(-t / 0.045)
knock += 0.055 * rng.standard_normal(len(t)) * np.exp(-t / 0.003)
save(
    "laclack",
    knock,
    "Damped inharmonic wood-like resonator with short noise excitation",
)

t = np.arange(round(0.70 * RATE)) / RATE
f = 43.6535 * (1 + 0.46 * np.exp(-t / 0.028))
phase = 2 * np.pi * np.cumsum(f) / RATE
cutoff = 180 + 1150 * np.exp(-t / 0.09) + 580 * np.exp(-(((t - 0.23) / 0.10) ** 2))
burr = np.zeros_like(t)
for k in range(1, 45):
    burr += (
        np.sin(k * phase + 0.06 * np.sin(2 * np.pi * 3.7 * t) * k)
        * np.exp(-k * f / cutoff)
        / k
    )
burr = np.tanh(burr * 2.1) * (1 - np.exp(-t / 0.003)) * np.exp(-t / 0.22)
burr = signal.sosfilt(
    signal.butter(2, 110, fs=RATE, btype="highpass", output="sos"), burr
)
save(
    "laburr",
    burr,
    "Additive F1 bass with two moving harmonic envelopes, saturation and removed sub; returns as percussion",
)

t = np.arange(round(0.85 * RATE)) / RATE
noise = signal.sosfilt(
    signal.butter(2, [400, 2100], fs=RATE, btype="bandpass", output="sos"),
    rng.standard_normal(len(t)),
)
save(
    "lasuck",
    noise * (t / 0.85) ** 2 * (0.7 + 0.3 * np.sin(2 * np.pi * 19 * t)),
    "Rising narrow noise inhale, isolated transition object",
)
(ROOT / "palette.json").write_text(
    json.dumps(
        {
            "origin": "Original deterministic synthesis; no third-party audio",
            "seed": SEED,
            "assets": records,
        },
        indent=2,
    )
    + "\n"
)
