"""Two sample palettes for the unchanged Undercurrent v002 score."""

import hashlib
import json
import shutil
from pathlib import Path

import numpy as np
import soundfile as sf
from scipy.signal import butter, sosfilt

ROOT = Path(__file__).resolve().parent
RATE = 48000
SEED = 2026101023
NOTES = [[56, 60, 63, 67], [58, 60, 65, 67]]
ASSETS = ROOT / "references/assets"
DRUMS = ROOT.parent / "practical-dogfood/references/assets/drums"


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def filt(audio, cutoff, kind="lowpass"):
    return sosfilt(butter(2, cutoff, btype=kind, fs=RATE, output="sos"), audio)


def envelope(t, attack, decay):
    return (1 - np.exp(-t / attack)) * np.exp(-t / decay)


def chord(notes, palette, rng):
    t = np.arange(round(1.25 * RATE)) / RATE
    body = np.zeros(len(t))
    for note in notes:
        f = 440 * 2 ** ((note - 69) / 12)
        for detune in [0.9975, 1.0025]:
            phase = rng.uniform(0, 2 * np.pi)
            if palette == "smoke":
                for harmonic, amp in [(1, 1), (2, 0.32), (3, 0.10), (4, 0.045)]:
                    body += amp * np.sin(2 * np.pi * f * detune * harmonic * t + phase)
            else:
                for harmonic in range(1, 19):
                    amp = np.sin(np.pi * 0.23 * harmonic) / harmonic
                    body += amp * np.cos(2 * np.pi * f * detune * harmonic * t + phase)
    if palette == "smoke":
        body = filt(np.tanh(body * 0.28), 1100)
        body *= envelope(t, 0.007, 0.27)
    else:
        body = np.tanh(body * 1.45)
        bright, dark = filt(body, 3600), filt(body, 850)
        mix = np.exp(-t / 0.035)
        body = (mix * bright + (1 - mix) * dark) * envelope(t, 0.003, 0.085)
    return filt(body, 200, "highpass")


def percussion(role, palette, rng):
    duration = {"cp": 0.65, "hh": 0.20, "oh": 0.70, "brush": 0.22, "breath": 0.94}[role]
    t = np.arange(round(duration * RATE)) / RATE
    noise = rng.normal(size=len(t))
    if role == "cp":
        if palette == "smoke":
            body = filt(filt(noise, 3100), 550, "highpass")
            env = envelope(t, 0.001, 0.075)
            env += 0.45 * envelope(np.maximum(t - 0.011, 0), 0.001, 0.022)
            env += 0.3 * envelope(np.maximum(t - 0.023, 0), 0.001, 0.022)
        else:
            body = filt(filt(np.tanh(noise * 1.9), 7200), 1150, "highpass")
            env = envelope(t, 0.0008, 0.041)
        return body * env
    if role in ["hh", "oh"]:
        decay = {"hh": 0.031, "oh": 0.12}[role]
        if palette == "smoke":
            body = filt(filt(noise, 7900), 3700, "highpass")
        else:
            metal = sum(
                np.sin(2 * np.pi * f * t + rng.uniform(0, 2 * np.pi))
                for f in [4013, 5627, 7139, 8933]
            )
            body = filt(np.tanh(metal * 0.8) + noise * 0.28, 4400, "highpass")
            decay *= 0.8
        return body * envelope(t, 0.0008, decay)
    if role == "brush":
        band = (900, 3400) if palette == "smoke" else (2200, 6500)
        body = filt(filt(noise, band[1]), band[0], "highpass")
        return body * envelope(t, 0.0015, 0.04 if palette == "smoke" else 0.018)
    body = filt(filt(noise, 1900 if palette == "smoke" else 3900), 950, "highpass")
    return (
        body
        * np.sin(np.pi * t / t[-1]) ** 2
        * (0.6 + 0.4 * np.sin(2 * np.pi * 4.2666667 * t))
    )


def save(path, data, reference):
    original, rate = sf.read(reference, always_2d=True)
    data = data - np.mean(data)
    data[:48] *= np.linspace(0, 1, 48)
    data[-480:] *= np.linspace(1, 0, 480)
    # Match asset energy before the unchanged score gain; bound isolated peaks.
    ref_energy = np.sum(original**2) / original.shape[1] * RATE / rate
    multiplier = np.sqrt(ref_energy / np.sum(data**2))
    peak_limit = 0.92 / np.max(np.abs(data))
    data *= min(multiplier, peak_limit)
    path.parent.mkdir(parents=True, exist_ok=True)
    sf.write(path, data, RATE, subtype="PCM_24")
    return {
        "path": str(path.relative_to(ROOT)),
        "sha256": digest(path),
        "energy_reference": str(reference.relative_to(ROOT.parent)),
        "energy_reference_sha256": digest(reference),
        "energy_match_limited_by_peak": bool(peak_limit < multiplier),
    }


def main():
    destinations = [ASSETS / palette for palette in ["smoke", "wire"]]
    if any(p.exists() for p in destinations):
        raise FileExistsError(
            "Comparison palettes already exist; preserve them and version changes"
        )
    report = {
        "seed": SEED,
        "sample_rate": RATE,
        "notes_midi": NOTES,
        "origin": "Original synthesis, with the existing 909 kick copied unchanged",
        "bank_names": "RolandTR909 names are compatibility slots for the fixed score. Only bd remains a 909 recording; cp/hh/oh are new synthesis.",
        "palettes": {},
    }
    for number, palette in enumerate(["smoke", "wire"]):
        rng = np.random.default_rng(SEED + number)
        out = ASSETS / palette
        outputs = []
        kick = next((DRUMS / "RolandTR909_bd").glob("*.wav"))
        target = out / "RolandTR909_bd/00.wav"
        target.parent.mkdir(parents=True)
        shutil.copyfile(kick, target)
        outputs.append(
            {
                "path": str(target.relative_to(ROOT)),
                "sha256": digest(target),
                "copied_from": str(kick.relative_to(ROOT.parent)),
                "unchanged": True,
            }
        )
        for role in ["cp", "hh", "oh", "brush", "breath"]:
            bank = f"RolandTR909_{role}" if role in ["cp", "hh", "oh"] else f"uc{role}"
            ref = (
                next((DRUMS / bank).glob("*.wav"))
                if role in ["cp", "hh", "oh"]
                else ASSETS / f"samples/{bank}/00.wav"
            )
            outputs.append(
                save(out / bank / "00.wav", percussion(role, palette, rng), ref)
            )
        for index, notes in enumerate(NOTES):
            outputs.append(
                save(
                    out / f"ucchord/{index:02d}.wav",
                    chord(notes, palette, rng),
                    ASSETS / f"samples/ucchord/{index:02d}.wav",
                )
            )
        report["palettes"][palette] = outputs
        manifest = json.loads((ROOT / "assembly-v002.json").read_text())
        manifest["revision"] = palette
        manifest["samples"] = [f"references/assets/{palette}"]
        (ROOT / f"assembly-{palette}.json").write_text(
            json.dumps(manifest, indent=2) + "\n"
        )
    (ROOT / "references/comparison-palettes.json").write_text(
        json.dumps(report, indent=2) + "\n"
    )


if __name__ == "__main__":
    main()
