"""Render an original long rubber articulation for the exposed turnaround."""
import hashlib
import json
from pathlib import Path

import numpy as np
import soundfile as sf
from scipy.signal import butter, sosfilt

ROOT = Path(__file__).resolve().parent
SR = 48000
T = np.arange(int(1.25 * SR)) / SR
BASE = 43.65352893
FREQ = BASE * (1 + .10 * np.exp(-T / .022))
PHASE = 2 * np.pi * np.cumsum(FREQ) / SR
DEPTH = .9 + 3.4 * np.exp(-T / .21) + 1.3 * np.exp(-((T - .43) / .09)**2)
OSC = np.sin(PHASE + DEPTH * np.sin(PHASE * 2))
OSC = np.tanh(OSC * 2.3)
BODY = sosfilt(butter(3, [135, 1700], btype='bandpass', fs=SR, output='sos'), OSC)
ENV = (1 - np.exp(-T / .001)) * np.exp(-T / .35)
ENV *= .72 + .28 * np.cos(2 * np.pi * T / .220588)**2
OUT = BODY * ENV
OUT[:96] *= np.linspace(0, 1, 96)
OUT[-2400:] *= np.linspace(1, 0, 2400)
OUT *= .85 / abs(OUT).max()
P = ROOT / 'references/assets/samples/prbend/01.wav'
if P.exists():
    raise FileExistsError(P)
P.parent.mkdir(parents=True, exist_ok=True)
sf.write(P, OUT, SR, subtype='PCM_24')
(ROOT / 'references/gesture.json').write_text(json.dumps({
    'origin': 'Original procedural F1 FM and saturation with a second timbral swell',
    'generator_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    'sample_rate': SR, 'seconds': len(OUT) / SR, 'file': str(P.relative_to(ROOT)),
    'sha256': hashlib.sha256(P.read_bytes()).hexdigest(),
}, indent=2) + '\n')
