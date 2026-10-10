"""Verify fresh palette reconstruction and preserved render provenance without overwrites."""

import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np
import soundfile as sf

ROOT = Path(__file__).resolve().parent
VERSIONS = ["v007", "v009", "v010", "v011", "v007-rebuild"]


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def db(value):
    return float(20 * np.log10(max(float(value), 1e-12)))


result = {
    "palette": {},
    "renders": {},
    "scope": "Technical reproduction and asset integrity; not musical quality or personal hearing.",
}
with tempfile.TemporaryDirectory(prefix="negative-space-palette-") as temporary:
    fresh = Path(temporary)
    (fresh / "renders/body-probe").mkdir(parents=True)
    shutil.copy2(
        ROOT / "renders/body-probe/render.wav", fresh / "renders/body-probe/render.wav"
    )
    for script in [
        "make_palette.py",
        "make_cloud.py",
        "capture_body.py",
        "perform_object.py",
    ]:
        shutil.copy2(ROOT / script, fresh / script)
        subprocess.run(
            [sys.executable, str(fresh / script)], check=True, capture_output=True
        )
    for path in sorted((fresh / "references/assets/samples").rglob("*.wav")):
        relative = path.relative_to(fresh)
        original = ROOT / relative
        matches = digest(path) == digest(original)
        result["palette"][str(relative)] = {
            "sha256": digest(path),
            "matches_original": matches,
        }
        assert matches, relative
result["palette_note"] = (
    "Mathematical generators and capture/performance transforms match byte-for-byte in a fresh temporary project. Capture starts from the preserved body-probe WAV; regenerating WebAudio reverberation is not claimed byte-identical."
)
for version in VERSIONS:
    directory = ROOT / "renders" / version
    receipt = json.loads((directory / "project-render.json").read_text())
    assert receipt["status"] == "complete"
    outputs = {}
    for name, item in receipt["renders"].items():
        wav = directory / item["file"]
        audio, rate = sf.read(wav, always_2d=True)
        info = sf.info(wav)
        engine = json.loads((wav.parent / "render.json").read_text())
        assert digest(wav) == item["sha256"] == engine["output"]["sha256"]
        assert digest(directory / "source.strudel") == receipt["source"]["sha256"]
        assert (len(audio), rate, audio.shape[1]) == (1440000, 48000, 2)
        rails = int(np.count_nonzero((audio >= 32767 / 32768) | (audio <= -1)))
        assert info.subtype == "PCM_16" and rails == 0
        for sample in engine["samples"]:
            assert digest(Path(sample["path"])) == sample["sha256"]
        outputs[name] = {
            "frames": len(audio),
            "sample_rate": rate,
            "channels": audio.shape[1],
            "sha256": digest(wav),
            "pcm_rail_samples": rails,
            "integrated_lufs": item["metrics"]["integrated_lufs"],
            "true_peak_dbtp": item["metrics"]["true_peak_dbtp"],
            "final_100ms_peak_dbfs": db(np.max(np.abs(audio[-4800:]))),
            "final_sample_peak_dbfs": db(np.max(np.abs(audio[-1]))),
            "mono_rms_loss_db": db(np.sqrt(np.mean(np.mean(audio, axis=1) ** 2)))
            - db(np.sqrt(np.mean(audio**2))),
            "sample_hashes_verified": len(engine["samples"]),
        }
    result["renders"][version] = outputs
original = result["renders"]["v007"]
rebuild = result["renders"]["v007-rebuild"]
result["fresh_v007_render_comparison"] = {
    name: {
        "byte_identical": original[name]["sha256"] == rebuild[name]["sha256"],
        "lufs_difference": round(
            rebuild[name]["integrated_lufs"] - original[name]["integrated_lufs"], 4
        ),
        "true_peak_difference_db": round(
            rebuild[name]["true_peak_dbtp"] - original[name]["true_peak_dbtp"], 4
        ),
    }
    for name in original
}
print(json.dumps(result, indent=2))
