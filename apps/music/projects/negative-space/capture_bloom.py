"""Print one complete original dub gesture for recognizable resampling transformations."""

import hashlib
import json
from pathlib import Path

import numpy as np
import soundfile as sf

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "renders/v004/dub/render.wav"
START = 0.703125
END = 2.578125
x, rate = sf.read(SOURCE, always_2d=True)
x = x[round(START * rate) : round(END * rate)].copy()
x[:144] *= np.linspace(0, 1, 144)[:, None]
x[-960:] *= np.linspace(1, 0, 960)[:, None]
x *= 0.8 / np.max(np.abs(x))
assets = []
for name, audio in [("nsbloom", x), ("nsbloomrev", x[::-1].copy())]:
    out = ROOT / "references/assets/samples" / name / "01.wav"
    if out.exists():
        raise FileExistsError(out)
    out.parent.mkdir(parents=True, exist_ok=True)
    sf.write(out, audio, rate, subtype="PCM_24")
    assets.append(
        {
            "name": name,
            "output": str(out.relative_to(ROOT)),
            "sha256": hashlib.sha256(out.read_bytes()).hexdigest(),
        }
    )
(ROOT / "references/bloom.json").write_text(
    json.dumps(
        {
            "source": str(SOURCE.relative_to(ROOT)),
            "source_sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
            "window_seconds": [START, END],
            "scope": "Composite original nscloud direct chord, slowed echo layer, delay and reverb. No external recording.",
            "processing": "3ms onset taper,20ms end taper,peak0.8; reverse copy of same waveform",
            "purpose": "Whole hollow gesture, expanded memory in the vacuum, chopped return, and final whole gesture.",
            "assets": assets,
        },
        indent=2,
    )
    + "\n"
)
