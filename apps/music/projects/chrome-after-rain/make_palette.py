"""Original percussion and transition sounds for Chrome After Rain.

Run from apps/music with uv run --locked python projects/chrome-after-rain/make_palette.py.
No recordings, speech, pretrained models or third-party samples are used.
"""

import hashlib
import json
from pathlib import Path

import numpy as np
import soundfile as sf
from scipy.signal import butter, sosfilt

ROOT = Path(__file__).resolve().parent
RATE = 48000
BPM = 136
SEED = 241010
rng = np.random.default_rng(SEED)
records = []


def time(seconds):
    return np.arange(round(seconds * RATE)) / RATE


def noise(t, low, high):
    return sosfilt(butter(2, [low, high], fs=RATE, btype="bandpass", output="sos"), rng.normal(size=len(t)))


def save(name, data, peak=.8):
    data = np.asarray(data)
    fade = min(240, len(data) // 8)
    data[:fade] *= np.linspace(0, 1, fade)
    data[-fade:] *= np.linspace(1, 0, fade)
    data *= peak / max(np.max(np.abs(data)), 1e-12)
    path = ROOT / "references" / "assets" / "samples" / name / "01.wav"
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        raise FileExistsError(f"Preserve existing palette: {path}")
    sf.write(path, data, RATE, subtype="PCM_24")
    records.append({"sound": name, "file": str(path.relative_to(ROOT)), "seconds": len(data) / RATE, "sha256": hashlib.sha256(path.read_bytes()).hexdigest()})


t = time(.38)
phase = 2 * np.pi * np.cumsum(48 + 115 * np.exp(-t / .014)) / RATE
kick = np.sin(phase) * np.exp(-t / .095)
kick += .15 * noise(t, 1800, 9000) * np.exp(-t / .003)
save("crkick", np.tanh(kick * 1.5), .92)

t = time(.23)
body = .6 * np.sin(2 * np.pi * 185 * t + 1.4 * np.exp(-t / .012)) * np.exp(-t / .035)
bursts = sum(np.where(t >= onset, np.exp(-np.maximum(t - onset, 0) / decay), 0) for onset, decay in [(0, .009), (.011, .009), (.023, .009), (.036, .052)])
save("crclap", body + noise(t, 1000, 11000) * bursts, .8)

t = time(.095)
rim = sum(a * np.sin(2 * np.pi * hz * t) * np.exp(-t / tau) for hz, a, tau in [(720, 1, .014), (1193, .6, .011), (1877, .27, .009)])
save("crrim", rim + .18 * noise(t, 1400, 7000) * np.exp(-t / .008), .7)

t = time(.14)
metal = sum(np.sign(np.sin(2 * np.pi * hz * t)) for hz in [4021, 5387, 6421, 8137]) / 4
metal = sosfilt(butter(2, 6200, fs=RATE, btype="highpass", output="sos"), metal)
save("crhat", (metal * .35 + noise(t, 6500, 16000)) * np.exp(-t / .023), .65)

t = time(.11)
env = (1 - np.exp(-t / .009)) * np.exp(-t / .024)
save("crshaker", noise(t, 4800, 14000) * env, .55)

t = time(.34)
pitch = 230 + 120 * np.exp(-t / .024)
phase = 2 * np.pi * np.cumsum(pitch) / RATE
save("crwood", (np.sin(phase + 2 * np.sin(phase * 1.47) * np.exp(-t / .014)) + .2 * noise(t, 800, 4500)) * np.exp(-t / .045), .7)

# A resonant F# minor cloud, reversed into a one-bar pickup; its forward form is the landing.
t = time(240 / BPM)
cloud = np.zeros(len(t))
for hz in [369.994, 440, 554.365, 659.255, 830.609]:
    for ratio, amp in [(1, 1), (2.001, .28), (3.99, .09)]:
        cloud += amp * np.sin(2 * np.pi * hz * ratio * t + .2 * np.sin(2 * np.pi * .7 * t)) * np.exp(-t / .48)
cloud += noise(t, 1200, 9000) * np.exp(-t / .2) * .5
save("crlanding", cloud.copy(), .65)
save("crreverse", cloud[::-1].copy(), .65)

# Soft wideband air is used only at transitions, never as a permanent noise floor.
t = time(480 / BPM)
save("crrise", noise(t, 1700, 12000) * (t / t[-1]) ** 2 * (.65 + .35 * np.sin(2 * np.pi * BPM / 60 * 4 * t)), .5)

(ROOT / "references" / "palette.json").write_text(json.dumps({"origin": "Original deterministic procedural synthesis", "sample_rate": RATE, "seed": SEED, "bpm": BPM, "generator_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(), "sounds": records}, indent=2) + "\n")
print(f"Created {len(records)} original sounds.")
