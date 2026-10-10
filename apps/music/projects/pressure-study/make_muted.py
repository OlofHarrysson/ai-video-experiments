"""Three dry, noisy articulations from the same original metallic sound family."""
import hashlib
import json
from pathlib import Path

import numpy as np
import soundfile as sf
from scipy.signal import butter, sosfilt

ROOT = Path(__file__).resolve().parent
SR = 48000
RNG = np.random.default_rng(101036)
ITEMS = []
for index in range(3):
    t = np.arange(int(.135 * SR)) / SR
    body = sum(np.sin(2 * np.pi * f * t + i * .7) * np.exp(-t / (.018 + .004 * i)) / (i + 1) for i, f in enumerate([710, 1183, 1947, 3209, 4701]))
    noise = sosfilt(butter(3, [500, 4700], btype='bandpass', fs=SR, output='sos'), RNG.normal(size=len(t)))
    env = np.exp(-t / (.012 + index * .004))
    x = body * .29 + noise * env * .95
    x[:48] *= np.linspace(0, 1, 48)
    x[-960:] *= np.linspace(1, 0, 960)
    x *= .85 / abs(x).max()
    p = ROOT / f'references/assets/samples/prmute/{index + 1:02d}.wav'
    if p.exists():
        raise FileExistsError(p)
    p.parent.mkdir(parents=True, exist_ok=True)
    sf.write(p, x, SR, subtype='PCM_24')
    ITEMS.append({'file': str(p.relative_to(ROOT)), 'sha256': hashlib.sha256(p.read_bytes()).hexdigest(), 'seconds': len(x) / SR})
(ROOT / 'references/muted.json').write_text(json.dumps({'origin': 'Original deterministic noise-rich and damped variant of prchain; same five resonator frequencies', 'seed': 101036, 'generator_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(), 'samples': ITEMS}, indent=2) + '\n')
