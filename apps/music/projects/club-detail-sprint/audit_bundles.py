"""Verify the selected portable bundles and their independently rebuilt runs."""

import json
import sys
from pathlib import Path

import numpy as np
import soundfile as sf

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
import music
import workflow

SPRINT = Path(__file__).resolve().parent
PAIRS = [
    ("pressure-lock", "pressure-study", "bundle-pressure"),
    ("negative-space", "negative-space", "bundle-negative"),
]


def main():
    results = []
    for name, project, rendered in PAIRS:
        folder = SPRINT / "exports/bundles" / name
        manifest = json.loads((folder / "bundle.json").read_text())
        assert manifest["status"] == "complete"
        for item in manifest["files"]:
            assert music.digest(folder / item["file"]) == item["sha256"]
        _, _, source, samples = workflow.load_project(folder / "project.json", "v011")
        assert all(path.is_relative_to(folder) for path in [source, *samples])
        original = ROOT / "projects" / project / "renders/v011"
        before = json.loads((original / "project-render.json").read_text())
        rebuilt = SPRINT / "screening" / rendered
        after = json.loads((rebuilt / "project-render.json").read_text())
        assert after["status"] == "complete"
        assert before["source"]["sha256"] == after["source"]["sha256"]
        bank = lambda receipt: sorted(
            (s["name"], s["index"], s["sha256"]) for s in receipt["sample_library"]
        )
        assert bank(before) == bank(after)
        assert all(
            Path(s["path"]).is_relative_to(folder) for s in after["sample_library"]
        )
        stems = []
        for stem, item in after["renders"].items():
            path = rebuilt / item["file"]
            assert music.digest(path) == item["sha256"]
            info = sf.info(path)
            assert (info.frames, info.samplerate, info.channels) == (1440000, 48000, 2)
            assert item["metrics"]["pcm_rail_samples"] == 0
            assert item["metrics"]["true_peak_dbtp"] < 0
            new, _ = sf.read(path)
            old, _ = sf.read(original / before["renders"][stem]["file"])
            residual = float(np.sqrt(np.mean((new - old) ** 2)))
            stems.append(
                {
                    "stem": stem,
                    "sha256": item["sha256"],
                    "integrated_lufs": item["metrics"]["integrated_lufs"],
                    "true_peak_dbtp": item["metrics"]["true_peak_dbtp"],
                    "residual_rms_dbfs": 20 * np.log10(residual) if residual else None,
                }
            )
        results.append(
            {
                "name": name,
                "bundle": str(folder.relative_to(SPRINT)),
                "bundle_manifest_sha256": music.digest(folder / "bundle.json"),
                "verified_files": len(manifest["files"]),
                "sample_assets": len(bank(before)),
                "all_runtime_paths_inside_bundle": True,
                "source_and_bank_indices_hashes_unchanged": True,
                "rebuilt_stems": stems,
            }
        )
    evidence = {
        "status": "verified",
        "scope": "Local relocated recipe and sample banks; installed workbench required. Original saved outputs are exact; wet rerenders vary.",
        "frames": 1440000,
        "sample_rate": 48000,
        "channels": 2,
        "pcm_rail_samples_all_outputs": 0,
        "bundles": results,
    }
    music.save_json(SPRINT / "bundle-evidence.json", evidence)
    print(json.dumps(evidence, indent=2))


if __name__ == "__main__":
    main()
