"""A shared struck resonator changes from inharmonic metal to elastic low body."""
import hashlib
import json
from pathlib import Path

import numpy as np
import soundfile as sf
from scipy.signal import butter, sosfilt

ROOT = Path(__file__).resolve().parent
SR = 48000
SEED = 101007
FUNDAMENTAL = 43.65352893
METAL = np.array([568, 946.4, 1557.6, 2567.2, 3760.8])
LOW = FUNDAMENTAL * np.array([2, 3, 4, 6, 8])
T = np.arange(int(.9 * SR)) / SR
EXCITATION = np.random.default_rng(SEED).normal(size=len(T))
RECEIPTS = []

for index, alpha in enumerate(np.linspace(0, 1, 13)):
    frequencies = METAL ** (1 - alpha) * LOW ** alpha
    body = np.zeros(len(T))
    for partial, frequency in enumerate(frequencies):
        # One resonator bank: damping lengthens and inharmonic ratios converge.
        decay = (.027 + .006 * partial) * (1 + 5.5 * alpha)
        bend = 1 + .14 * alpha * np.exp(-T / .065)
        phase = 2 * np.pi * np.cumsum(frequency * bend) / SR
        phase += .3 * partial
        # The same rough edge expands into a brief, pressure-like elastic buckle.
        phase += alpha * 1.6 * np.sin(phase * 1.01) * np.exp(-T / .09)
        body += np.sin(phase) * np.exp(-T / decay) / (partial + 1)
    cutoff = [600 * (1 - alpha) + 140 * alpha, 5600 * (1 - alpha) + 2100 * alpha]
    grit = sosfilt(butter(3, cutoff, 'bandpass', fs=SR, output='sos'), EXCITATION)
    grit *= np.exp(-T / (.015 + .022 * alpha))
    signal = body * (.64 + .08 * np.sin(2 * np.pi * 38 * T)) + .40 * grit
    signal = np.tanh(signal * (1.15 + 1.2 * alpha))
    signal *= 1 - np.exp(-T / .0007)
    signal[-2400:] *= np.linspace(1, 0, 2400)
    signal = signal / np.max(abs(signal)) * .85
    path = ROOT / 'references/assets/samples/prmorph' / f'{index + 1:02d}.wav'
    if path.exists():
        raise FileExistsError(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    sf.write(path, signal, SR, subtype='PCM_24')
    RECEIPTS.append({'index': index, 'alpha': float(alpha), 'frequencies_hz': frequencies.tolist(), 'path': str(path.relative_to(ROOT)), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()})

(ROOT / 'references/morph.json').write_text(json.dumps({'origin': 'Original deterministic shared excitation/resonator family', 'seed': SEED, 'sample_rate': SR, 'generator_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(), 'sounds': RECEIPTS}, indent=2) + '\n')
