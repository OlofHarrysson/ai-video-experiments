"""Check that the palette comparison holds the score and bass foundation fixed."""

import json
from pathlib import Path

import numpy as np
import soundfile as sf
from audit import digest

ROOT = Path(__file__).resolve().parent
EXPORT = ROOT / "exports/palette-comparison-v001"


def main():
    import sys

    sys.path.insert(0, str(ROOT.parents[1]))
    import music

    names = ["v002", "smoke", "wire"]
    baseline_source = digest(ROOT / "assemblies/v002/source.strudel")
    baseline_bass, rate = sf.read(ROOT / "renders/v002/bass/render.wav")
    baseline_receipt = json.loads(
        (ROOT / "renders/v002/master/render.json").read_text()
    )
    kick_hash = next(
        s["sha256"]
        for s in baseline_receipt["samples"]
        if s["name"] == "RolandTR909_bd"
    )
    evidence = {
        "source_sha256": baseline_source,
        "unchanged_kick_sha256": kick_hash,
        "palettes": {},
    }

    for name in names:
        run = ROOT / "renders" / name
        assert digest(ROOT / f"assemblies/{name}/source.strudel") == baseline_source
        receipt = json.loads((run / "master/render.json").read_text())
        assert receipt["source"]["sha256"] == baseline_source
        assert (
            next(
                s["sha256"] for s in receipt["samples"] if s["name"] == "RolandTR909_bd"
            )
            == kick_hash
        )
        bass, bass_rate = sf.read(run / "bass/render.wav")
        difference = float(np.abs(bass - baseline_bass).max())
        assert bass_rate == rate == 48000 and difference <= 1 / 32768
        stems = {}
        for stem in ["master", "drums", "bass", "theme", "details"]:
            stem_dir = (
                ROOT / "renders/smoke-details-retry"
                if name == "smoke" and stem == "details"
                else run / stem
            )
            path = stem_dir / "render.wav"
            info = sf.info(path)
            m = json.loads((stem_dir / "inspection/metrics.json").read_text())
            stem_receipt = json.loads((stem_dir / "render.json").read_text())
            assert stem_receipt["status"] == "complete"
            assert stem_receipt["source"]["sha256"] == baseline_source
            assert (
                info.frames == 1440000
                and info.samplerate == 48000
                and info.channels == 2
            )
            assert m["pcm_rail_samples"] == 0 and m["true_peak_dbtp"] < 0
            assert digest(path) == m["sha256"]
            stems[stem] = {
                k: m[k]
                for k in [
                    "sha256",
                    "integrated_lufs",
                    "true_peak_dbtp",
                    "pcm_rail_samples",
                ]
            }
        evidence["palettes"][name] = {
            "bass_max_sample_difference": difference,
            "stems": stems,
        }
        if name == "smoke":
            stems["details"]["recovery_file"] = "renders/smoke-details-retry/render.wav"

    manifest = json.loads((EXPORT / "manifest.json").read_text())
    matched = []
    for name, entry in zip(names, manifest["copies"], strict=True):
        original, original_rate = sf.read(ROOT / f"renders/{name}/master/render.wav")
        output = EXPORT / entry["file"]
        copied, copied_rate = sf.read(output)
        expected = original * 10 ** (entry["gain_db"] / 20)
        assert copied_rate == original_rate == 48000
        assert np.max(np.abs(copied - expected)) < 1e-7
        assert entry["source_sha256"] == digest(
            ROOT / f"renders/{name}/master/render.wav"
        )
        measured = music.loudness(output)
        assert abs(measured["integrated_lufs"] - manifest["target_lufs"]) <= 0.02
        matched.append({**entry, "sha256": digest(output), "measured": measured})
    evidence["comparison"] = {"target_lufs": manifest["target_lufs"], "copies": matched}
    evidence["recovery"] = (
        "Smoke detail export timed out after 180 seconds before loading samples. Original failed receipt preserved; one standalone retry completed at renders/smoke-details-retry. Masters and matched copies are from the original successful exports."
    )
    evidence["scope"] = (
        "Identical score and kick asset. Dry bass rerenders differ by at most one PCM16 step. Sample envelopes/timbres change; perceived groove and taste remain human judgments."
    )
    (ROOT / "palette-comparison-evidence.json").write_text(
        json.dumps(evidence, indent=2) + "\n"
    )
    print(
        json.dumps(
            {
                "score_identical": True,
                "kick_identical": True,
                "matched_lufs": [m["measured"]["integrated_lufs"] for m in matched],
            }
        )
    )


if __name__ == "__main__":
    main()
