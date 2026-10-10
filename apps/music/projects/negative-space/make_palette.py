"""Original deterministic synthesis for Negative Space. Run from music via uv."""

import hashlib
import json
from pathlib import Path

import numpy as np
import soundfile as sf
from scipy.signal import butter, sosfilt

ROOT = Path(__file__).resolve().parent
RATE = 48000
RNG = np.random.default_rng(20261010)
RECORDS = []


def filt(x, cutoff, kind="lowpass", order=3):
    return sosfilt(butter(order, cutoff, btype=kind, fs=RATE, output="sos"), x, axis=0)


def save(name, x, description, peak=0.82):
    x = np.asarray(x)
    x -= x.mean(axis=0)
    edge = min(240, len(x) // 4)
    envelope = np.ones(len(x))
    envelope[:edge] = np.linspace(0, 1, edge)
    envelope[-edge:] = np.linspace(1, 0, edge)
    x *= envelope[:, None] if x.ndim == 2 else envelope
    x *= peak / max(1e-12, np.max(np.abs(x)))
    folder = ROOT / "references/assets/samples" / name
    folder.mkdir(parents=True, exist_ok=True)
    target = folder / "01.wav"
    if target.exists():
        raise FileExistsError(target)
    sf.write(target, x, RATE, subtype="PCM_24")
    RECORDS.append(
        {
            "name": name,
            "file": str(target.relative_to(ROOT)),
            "seconds": len(x) / RATE,
            "sha256": hashlib.sha256(target.read_bytes()).hexdigest(),
            "description": description,
        }
    )


# A short struck spring: intentionally inharmonic, attack-rich, no singable pitch.
t = np.arange(int(0.29 * RATE)) / RATE
metal = sum(
    a * np.sin(2 * np.pi * f * t + p) * np.exp(-t / tau)
    for f, a, tau, p in [
        (727, 1, 0.032, 0.1),
        (1181, 0.7, 0.045, 1.3),
        (1873, 0.45, 0.021, 2),
        (3127, 0.24, 0.018, 0.6),
    ]
)
metal += filt(RNG.normal(size=len(t)), 1400, "highpass") * 0.65 * np.exp(-t / 0.012)
save("nsspring", metal, "Original inharmonic struck spring with bright noise attack.")

# Rough servo gesture with formant-like moving resonances. Not speech.
t = np.arange(int(0.47 * RATE)) / RATE
phase = 2 * np.pi * np.cumsum(70 + 75 * np.exp(-t / 0.055)) / RATE
servo = np.sin(phase + 3.2 * np.sin(phase * 0.501)) * np.exp(-t / 0.14)
servo += 0.35 * np.sin(phase * 3.031) * np.exp(-t / 0.055)
servo = filt(np.tanh(2.3 * servo), [130, 2400], "bandpass")
save(
    "nsservo",
    servo,
    "Original rough servo response: falling FM pulse, saturation, bandpassed body.",
)

# Dry dub chord to resample: close unresolved colour on F, spectrally dark.
t = np.arange(int(0.78 * RATE)) / RATE
voices = []
for hz in [
    174.614,
    207.652,
    261.626,
    369.994,
]:  # F3 Ab3 C4 F#4: no melodic progression.
    voice = np.zeros(len(t))
    for ratio in [0.9983, 1.0021]:
        for harmonic in range(1, 23):
            voice += np.sin(
                2 * np.pi * hz * ratio * harmonic * t + RNG.uniform(0, 2 * np.pi)
            ) / (harmonic**1.22)
    voices.append(voice)
chord = sum(voices) / len(voices)
env = (1 - np.exp(-t / 0.003)) * np.exp(-t / 0.16)
chord = filt(np.tanh(chord * 0.9), 1700) * env
chord = filt(chord, 230, "highpass")
save(
    "nschord",
    chord,
    "Original detuned F3-Ab3-C4-F#4 dub chord, short struck envelope and tape-like saturation.",
)

# Granular friction layer, generated with stochastic microbursts and separate stereo trajectories.
t = np.arange(int(1.35 * RATE)) / RATE
channels = []
for side in range(2):
    noise = filt(RNG.normal(size=len(t)), [650, 6800], "bandpass")
    grains = np.zeros(len(t))
    for start, dur, amp in zip(
        RNG.uniform(0, 1.2, 70), RNG.uniform(0.004, 0.039, 70), RNG.uniform(0.1, 1, 70)
    ):
        a = int(start * RATE)
        n = int(dur * RATE)
        grains[a : a + n] += np.hanning(n) * amp
    x = noise * grains
    x += 0.012 * np.sin(2 * np.pi * (1279 + side * 17) * t)
    channels.append(x)
save(
    "nsfriction",
    np.stack(channels, axis=1),
    "Original stereo friction micrograins; independently seeded left and right textures.",
    0.65,
)

# Reverse the original chord, rather than use a stock riser.
rev = chord[::-1].copy()
save("nsreverse", rev, "Reversed original dub chord for short pre-impact suction.")

# Deep closing impact with a quiet stereo reflection, preserving central bass.
t = np.arange(int(1.6 * RATE)) / RATE
phase = 2 * np.pi * np.cumsum(43 + 36 * np.exp(-t / 0.026)) / RATE
body = np.sin(phase) * np.exp(-t / 0.29)
body += 0.09 * filt(RNG.normal(size=len(t)), 1700) * np.exp(-t / 0.025)
left = body.copy()
right = body.copy()
for delay, level in [(0.063, 0.12), (0.127, 0.06), (0.211, 0.03)]:
    n = int(delay * RATE)
    left[n:] += filt(body[:-n], 450, "highpass") * level
    right[n + 37 :] += filt(body[: -n - 37], 450, "highpass") * level
save(
    "nslanding",
    np.stack([left, right], axis=1),
    "Original sub impact with pitch fall and short asymmetric high-passed reflections.",
)

(ROOT / "references/palette.json").write_text(
    json.dumps(
        {
            "sample_rate": RATE,
            "seed": 20261010,
            "origin": "Original mathematical synthesis; no third-party recording or speech",
            "assets": RECORDS,
        },
        indent=2,
    )
    + "\n"
)
print(json.dumps(RECORDS, indent=2))
