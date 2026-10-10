"""Print a shared short room before saturation into two original Latch objects."""

import hashlib
import json
from pathlib import Path

import numpy as np
import soundfile as sf
from scipy import signal

ROOT = Path(__file__).resolve().parent
RATE = 48000
SEED = 88231
ROOM_SECONDS = 0.11
WET = 0.65
DRIVE = 2.8
OUT_PEAK = 0.72
SOURCE_NAMES = ("lashuck", "laburr")


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    rng = np.random.default_rng(SEED)
    t = np.arange(round(ROOM_SECONDS * RATE)) / RATE
    ir = rng.standard_normal((len(t), 2))
    ir = signal.sosfilt(
        signal.butter(2, [500, 5500], btype="bandpass", fs=RATE, output="sos"),
        ir,
        axis=0,
    )
    ir *= np.exp(-t[:, None] / 0.018)
    ir[:round(0.005 * RATE)] = 0
    ir /= np.sqrt(np.sum(ir ** 2, axis=0))
    records = []
    for name in SOURCE_NAMES:
        src = ROOT / f"references/assets/samples/{name}/00.wav"
        out = ROOT / f"references/assets/samples/{name}room/00.wav"
        if out.exists():
            raise FileExistsError(out)
        x, rate = sf.read(src, always_2d=True)
        if rate != RATE or x.shape[1] != 1:
            raise ValueError("Expected retained mono 48 kHz original")
        x = x[:, 0]
        dry = np.pad(x, (0, len(ir) - 1))[:, None]
        wet = np.stack([signal.fftconvolve(x, ir[:, c]) for c in range(2)], axis=1)
        y = np.tanh(DRIVE * (dry + WET * wet))
        y = signal.sosfilt(
            signal.butter(2, 160, btype="highpass", fs=RATE, output="sos"), y, axis=0
        )
        y -= np.mean(y, axis=0)
        fade = round(0.008 * RATE)
        y[:fade] *= np.linspace(0, 1, fade)[:, None]
        y[-fade:] *= np.linspace(1, 0, fade)[:, None]
        y *= OUT_PEAK / np.max(np.abs(y))
        out.parent.mkdir(parents=True)
        sf.write(out, y, RATE, subtype="PCM_24")
        records.append({
            "source": str(src.relative_to(ROOT)), "source_sha256": digest(src),
            "file": str(out.relative_to(ROOT)), "sha256": digest(out),
            "frames": len(y), "channels": 2,
        })
    (ROOT / "room-objects.json").write_text(json.dumps({
        "origin": "Processing original Latch synthesis; no third-party audio",
        "method": "Shared deterministic short stereo room before tanh saturation; high-pass and edge fades after shaping",
        "seed": SEED, "room_seconds": ROOM_SECONDS, "wet": WET, "drive": DRIVE,
        "sample_rate": RATE, "peak": OUT_PEAK, "generator_sha256": digest(__file__),
        "assets": records,
    }, indent=2) + "\n")


if __name__ == "__main__":
    main()
