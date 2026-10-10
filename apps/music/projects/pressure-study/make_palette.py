"""Original mechanical percussion and resampled mid-bass; deterministic, no external audio."""
import hashlib
import json
from pathlib import Path

import numpy as np
import soundfile as sf
from scipy.signal import butter, sosfilt

ROOT = Path(__file__).resolve().parent
SR = 48000
RNG = np.random.default_rng(1010136)
RECEIPTS = []


def filtered(x, cutoff, kind):
    return sosfilt(butter(3, cutoff, kind, fs=SR, output='sos'), x)


def save(name, index, x, description):
    x = np.asarray(x, dtype=float)
    x[:240] *= np.linspace(0, 1, 240)
    x[-960:] *= np.linspace(1, 0, 960)
    x = x / max(abs(x).max(), 1e-9) * .85
    p = ROOT / 'references/assets/samples' / name / f'{index:02d}.wav'
    if p.exists():
        raise FileExistsError(p)
    p.parent.mkdir(parents=True, exist_ok=True)
    sf.write(p, x, SR, subtype='PCM_24')
    RECEIPTS.append({'name': name, 'index': index - 1, 'path': str(p.relative_to(ROOT)), 'description': description, 'seconds': len(x)/SR, 'sha256': hashlib.sha256(p.read_bytes()).hexdigest()})


for index in range(1, 5):
    t = np.arange(int(.26 * SR)) / SR
    # Different struck resonators retain one recognizable material rather than chromatic notes.
    frequencies = [710, 1183, 1947, 3209, 4701]
    body = sum(np.sin(2*np.pi*f*t + .3*i) * np.exp(-t/(.030 + .011*i)) / (i+1) for i, f in enumerate(frequencies))
    body *= .55 + .1*np.sin(2*np.pi*(31 + index*7)*t)
    grit = filtered(RNG.normal(size=len(t)), [1500, 6500], 'bandpass') * np.exp(-t/.021)
    save('prchain', index, body + .45*grit, 'Original inharmonic resonator strike, amplitude-modulated metal with a short noise attack')

for index in range(1, 5):
    t = np.arange(int(.14 * SR)) / SR
    x = filtered(RNG.normal(size=len(t)), [4200 + index*150, 11500], 'bandpass')
    env = (1-np.exp(-t/.0008))*np.exp(-t/(.018 + index*.008))
    save('prair', index, x*env, 'Original filtered air percussion with four decay lengths')

for index in range(1, 4):
    t = np.arange(int(.20 * SR)) / SR
    phase = 2*np.pi*np.cumsum(145 + 110*np.exp(-t/.012)) / SR
    x = np.sin(phase + 1.7*np.sin(phase*1.49)*np.exp(-t/.028)) * np.exp(-t/.045)
    x += .16*filtered(RNG.normal(size=len(t)), [850, 2600], 'bandpass') * np.exp(-t/.009)
    save('prknock', index, x, 'Original hollow, low mechanical knock; FM body with noise transient')

for index in range(1, 5):
    t = np.arange(int(.36 * SR)) / SR
    f = 43.65352893
    phase = 2*np.pi*np.cumsum(f*(1 + (.12+index*.025)*np.exp(-t/.02))) / SR
    fm = np.sin(phase + (2.8 + index*.45)*np.sin(2*phase)*np.exp(-t/.075))
    saw = 2 * ((f*t + .01) % 1) - 1
    x = np.tanh((fm + .20*saw)*2.2)
    x = filtered(x, [135, 1700 + index*250], 'bandpass')
    x *= (1-np.exp(-t/.002))*np.exp(-t/(.085 + index*.009))
    save('prrubber', index, x, 'Original F1 FM/waveshaped bass articulation, high-passed to reserve the sub region')

t = np.arange(int(.82*SR))/SR
noise = filtered(RNG.normal(size=len(t)), [500, 7500], 'bandpass')
resonance = sum(np.sin(2*np.pi*f*t) for f in [313, 761, 1721]) / 3
scrape = (noise*.7 + resonance*.3) * np.sin(np.pi*t/t[-1])**3 * (.6+.4*np.sin(2*np.pi*31*t)**2)
save('prscrape', 1, scrape, 'Original swelling granular-feeling scrape; three inharmonic resonators plus amplitude-modulated noise')

(ROOT / 'references/palette.json').write_text(json.dumps({'origin': 'Original deterministic procedural synthesis', 'seed': 1010136, 'sample_rate': SR, 'generator_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(), 'sounds': RECEIPTS}, indent=2)+'\n')
