"""Original muted chord and brushed percussion for Undercurrent."""

import hashlib
import json
from pathlib import Path

import numpy as np
import soundfile as sf
from scipy.signal import butter, sosfilt

ROOT = Path(__file__).resolve().parent
RATE = 48000
SEED = 2026101017
RNG = np.random.default_rng(SEED)
OUT = ROOT / "references/assets/samples"


def filt(audio, cutoff, kind="lowpass"):
    return sosfilt(butter(2, cutoff, fs=RATE, btype=kind, output="sos"), audio)


def save(bank, index, audio):
    path = OUT / bank / f"{index:02d}.wav"
    if path.exists():
        raise FileExistsError(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    audio -= np.mean(audio)
    audio[:240] *= np.linspace(0, 1, 240)
    audio[-960:] *= np.linspace(1, 0, 960)
    audio *= 0.72 / np.max(np.abs(audio))
    sf.write(path, audio, RATE, subtype="PCM_24")
    return {"file": str(path.relative_to(ROOT)), "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}


def chord(notes):
    t = np.arange(round(1.25 * RATE)) / RATE
    signal = np.zeros(len(t))
    for midi in notes:
        freq = 440 * 2 ** ((midi - 69) / 12)
        for detune in [0.9985, 1.0015]:
            phase = RNG.uniform(0, 2 * np.pi)
            for harmonic in range(1, 13):
                signal += np.sin(2 * np.pi * freq * detune * harmonic * t + phase) / harmonic**1.55
    signal = np.tanh(signal * 0.43)
    bright = filt(signal, 1450)
    dark = filt(signal, 420)
    colour = np.exp(-t / 0.075)
    body = (bright * colour + dark * (1 - colour)) * (1 - np.exp(-t / 0.009)) * np.exp(-t / 0.19)
    return filt(body, 210, "highpass")


def brush():
    t = np.arange(round(0.22 * RATE)) / RATE
    noise = filt(filt(RNG.normal(size=len(t)), 4600), 1100, "highpass")
    return noise * (1 - np.exp(-t / 0.0015)) * np.exp(-t / 0.031)


def breath():
    t = np.arange(round(0.94 * RATE)) / RATE
    noise = filt(filt(RNG.normal(size=len(t)), 2700), 900, "highpass")
    return noise * np.sin(np.pi * t / t[-1])**2 * (0.6 + 0.4 * np.sin(2 * np.pi * 4.2666667 * t))


if __name__ == "__main__":
    outputs = [
        save("ucchord", 0, chord([56, 60, 63, 67])),
        save("ucchord", 1, chord([58, 60, 65, 67])),
        save("ucbrush", 0, brush()),
        save("ucbreath", 0, breath()),
    ]
    (ROOT / "references/palette.json").write_text(json.dumps({
        "origin": "Original deterministic synthesis; no artist recordings",
        "seed": SEED, "sample_rate": RATE,
        "chords": ["Ab3 C4 Eb4 G4: rootless Fm9 over F bass", "Bb3 C4 F4 G4: suspended colour over the same F bass"],
        "design": "Muted detuned harmonic bodies, softened attack, fast darkening; filtered noise brush and breath",
        "outputs": outputs,
    }, indent=2) + "\n")
