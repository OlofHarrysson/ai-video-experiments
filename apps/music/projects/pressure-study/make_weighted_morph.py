"""Fixed resonators change damping, excitation and weight without chromatic movement."""
import hashlib
import json
from pathlib import Path

import numpy as np
import soundfile as sf
from scipy.signal import butter, sosfilt

ROOT = Path(__file__).resolve().parent
SR = 48000
SEED = 101007
F = 43.65352893
FREQUENCIES = np.array([F * 4, F * 6, 568, 946.4, 1557.6, 2567.2, 3760.8])
T = np.arange(int(.9 * SR)) / SR
EXCITATION = np.random.default_rng(SEED).normal(size=len(T))
RECEIPTS = []

for index, alpha in enumerate(np.linspace(0, 1, 13)):
    body = np.zeros(len(T))
    for partial, frequency in enumerate(FREQUENCIES):
        is_low = partial < 2
        decay = (.031 + .008 * partial) * (1 + 3.8 * alpha)
        weight = (.035 + 1.35 * alpha) / (partial + 1) if is_low else (1 - .74 * alpha) / (partial - 1)
        phase = 2 * np.pi * frequency * T + .3 * partial
        phase += alpha * .9 * np.sin(2 * np.pi * F * 2 * T) * np.exp(-T / .13)
        body += weight * np.sin(phase) * np.exp(-T / decay)
    cutoff = [420 * (1 - alpha) + 150 * alpha, 4200 * (1 - alpha) + 2300 * alpha]
    grit = sosfilt(butter(3, cutoff, 'bandpass', fs=SR, output='sos'), EXCITATION)
    grit *= np.exp(-T / (.014 + .025 * alpha))
    signal = .58 * body + .38 * grit
    signal = np.tanh(signal * (1.3 + 2.1 * alpha))
    signal *= 1 - np.exp(-T / .0007)
    signal[-2400:] *= np.linspace(1, 0, 2400)
    signal = signal / np.max(abs(signal)) * .85
    path = ROOT / 'references/assets/samples/prweight' / f'{index + 1:02d}.wav'
    if path.exists():
        raise FileExistsError(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    sf.write(path, signal, SR, subtype='PCM_24')
    RECEIPTS.append({'index': index, 'alpha': float(alpha), 'path': str(path.relative_to(ROOT)), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()})

(ROOT / 'references/weighted-morph.json').write_text(json.dumps({'origin': 'Original deterministic shared excitation, fixed resonator family with changing damping and weights', 'seed': SEED, 'sample_rate': SR, 'frequencies_hz': FREQUENCIES.tolist(), 'generator_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(), 'sounds': RECEIPTS}, indent=2) + '\n')
