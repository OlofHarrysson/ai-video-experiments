"""Measure v011 delivery boundaries and mono compatibility; no listening claims."""
import hashlib
import json
from pathlib import Path

import numpy as np
import soundfile as sf
from scipy.signal import butter, sosfilt

ROOT = Path(__file__).resolve().parent
RENDER = ROOT / 'renders/v011'
CYCLE_SECONDS = 240 / 136
BANDS = {'low': (30, 180), 'body': (180, 1200), 'presence': (1200, 6000)}


def db(rms):
    return float(20 * np.log10(max(float(rms), 1e-12)))


def rms(data):
    return float(np.sqrt(np.mean(np.square(data))))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


report = {
    'revision': 'v011',
    'method': 'Offline waveform checks on preserved PCM; mono is arithmetic L/R mean. Band filters run continuously before windowing.',
    'limits': 'No personal listening. Boundary derivatives are measurements, not a click detector. Nonzero mono energy does not establish good translation on a club system.',
    'stems': {},
}
for stem in ['master', 'drums', 'bass', 'percussion', 'space']:
    path = RENDER / stem / 'render.wav'
    data, sr = sf.read(path, always_2d=True)
    mono = np.mean(data, axis=1)
    bands = {}
    for name, cutoffs in BANDS.items():
        filtered = sosfilt(butter(4, cutoffs, btype='bandpass', fs=sr, output='sos'), data, axis=0)
        bands[name] = {
            'stereo_rms_dbfs': db(rms(filtered)),
            'mono_rms_dbfs': db(rms(filtered.mean(axis=1))),
            'mono_loss_db': db(rms(filtered.mean(axis=1))) - db(rms(filtered)),
        }
    tail = np.max(abs(data), axis=1)
    indices = np.flatnonzero(tail >= 10 ** (-80 / 20))
    boundaries = []
    for cycle in [4, 6, 6.5, 7, 7.75, 8, 11, 12, 15, 15.5, 16]:
        frame = round(cycle * CYCLE_SECONDS * sr)
        radius = round(.05 * sr)
        boundaries.append({
            'cycle': cycle, 'seconds': frame / sr,
            'boundary_step_dbfs': db(np.max(abs(data[frame] - data[frame - 1]))),
            'before_50ms_rms_dbfs': db(rms(data[frame-radius:frame])),
            'after_50ms_rms_dbfs': db(rms(data[frame:frame+radius])),
        })
    report['stems'][stem] = {
        'sha256': sha(path), 'frames': len(data), 'sample_rate': sr, 'channels': data.shape[1],
        'seconds': len(data) / sr, 'first_frame': data[0].tolist(), 'last_frame': data[-1].tolist(),
        'last_frame_at_or_above_minus80_dbfs_seconds': (int(indices[-1]) / sr if len(indices) else None),
        'last_100ms_peak_dbfs': db(np.max(abs(data[-round(.1*sr):]))),
        'fullband_mono_loss_db': db(rms(mono)) - db(rms(data)),
        'bands': bands, 'arrangement_boundaries': boundaries,
    }

output = ROOT / 'references/final-audit-v011.json'
output.write_text(json.dumps(report, indent=2) + '\n')
print(output)
for stem, result in report['stems'].items():
    print(stem, 'mono loss', round(result['fullband_mono_loss_db'], 3),
          'last >=-80', result['last_frame_at_or_above_minus80_dbfs_seconds'],
          'last frame', result['last_frame'])
