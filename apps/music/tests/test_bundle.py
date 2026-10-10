import json
from pathlib import Path

import numpy as np
import pytest
import soundfile as sf

import bundle
import music
import workflow


def fixture(root):
    run = root / "run"
    run.mkdir()
    source = run / "source.strudel"
    source.write_text('setcpm(60)\nvoice: s("voice:1")\n')
    bank = root / "original-bank" / "voice"
    bank.mkdir(parents=True)
    assets = []
    for index, filename in enumerate(["alpha.wav", "zeta.wav"]):
        path = bank / filename
        sf.write(path, np.full(1200, 0.02 * (index + 1)), 12000, subtype="PCM_16")
        assets.append(
            {
                "name": "voice",
                "index": index,
                "path": str(path),
                "sha256": music.digest(path),
            }
        )
    config = {
        "version": 1,
        "title": "Fixture",
        "sample_rate": 12000,
        "end_cycle": 0.1,
        "revisions": {"v001": {"source": "source.strudel", "notes": "Preserve index1"}},
        "samples": [str(bank.parent)],
        "stems": {"voice": ["voice"]},
        "sections": {},
    }
    music.save_json(run / "project.json", config)
    renders = {}
    for stem in ["master", "voice"]:
        folder = run / stem
        folder.mkdir()
        path = folder / "render.wav"
        sf.write(path, np.zeros((1200, 2)), 12000, subtype="PCM_16")
        renders[stem] = {"file": f"{stem}/render.wav", "sha256": music.digest(path)}
        music.save_json(
            folder / "render.json",
            {"status": "complete", "output": {"sha256": music.digest(path)}},
        )
    music.save_json(
        run / "project-render.json",
        {
            "status": "complete",
            "revision": "v001",
            "source": {"sha256": music.digest(source)},
            "project": {"sha256": music.digest(run / "project.json")},
            "sample_rate": 12000,
            "frames": 1200,
            "renders": renders,
            "sample_library": list(reversed(assets)),
        },
    )
    return run, bank


def test_bundle_relocates_recipe_preserves_indices_and_all_bytes(tmp_path):
    run, bank = fixture(tmp_path)
    result = bundle.bundle_project(run, tmp_path / "bundle")
    out = Path(result["output"])
    manifest = json.loads((out / "bundle.json").read_text())
    assert manifest["status"] == "complete"
    for item in manifest["files"]:
        assert music.digest(out / item["file"]) == item["sha256"]
    originals = [music.digest(bank / name) for name in ["alpha.wav", "zeta.wav"]]
    assert [
        music.digest(p) for p in sorted((out / "samples/voice").glob("*.wav"))
    ] == originals
    bank.parent.rename(tmp_path / "unavailable-original-bank")
    _, _, source, samples = workflow.load_project(out / "project.json", "v001")
    assert source == out / "source.strudel"
    assert samples == [out / "samples"]
    assert all(path.is_relative_to(out) for path in [source, *samples])
    assert (out / "renders/master.wav").read_bytes() == (
        run / "master/render.wav"
    ).read_bytes()
    # Existing destinations are never replaced, even by an identical input.
    (tmp_path / "unavailable-original-bank").rename(bank.parent)
    with pytest.raises(FileExistsError):
        bundle.bundle_project(run, out)


@pytest.mark.parametrize("changed", ["source", "sample", "incomplete"])
def test_bundle_rejects_invalid_inputs_before_creating_output(tmp_path, changed):
    run, bank = fixture(tmp_path)
    if changed == "source":
        (run / "source.strudel").write_text("changed")
    elif changed == "sample":
        (bank / "zeta.wav").write_bytes(b"changed")
    else:
        path = run / "project-render.json"
        receipt = json.loads(path.read_text())
        receipt["status"] = "running"
        music.save_json(path, receipt)
    with pytest.raises(ValueError):
        bundle.bundle_project(run, tmp_path / "rejected")
    assert not (tmp_path / "rejected").exists()


def test_bundle_records_copy_failure_and_preserves_originals(tmp_path, monkeypatch):
    run, _ = fixture(tmp_path)
    before = music.digest(run / "source.strudel")

    def fail(*args):
        raise OSError("Controlled copy failure")

    monkeypatch.setattr(bundle.shutil, "copyfile", fail)
    with pytest.raises(OSError, match="Controlled"):
        bundle.bundle_project(run, tmp_path / "failed")
    assert (
        json.loads((tmp_path / "failed/bundle.json").read_text())["status"] == "failed"
    )
    assert music.digest(run / "source.strudel") == before


def test_bundle_detects_source_change_between_preflight_and_copy(tmp_path, monkeypatch):
    run, _ = fixture(tmp_path)
    copy = bundle.shutil.copyfile

    def mutate_then_copy(source, target):
        if source == run / "source.strudel":
            source.write_text("changed after preflight")
        return copy(source, target)

    monkeypatch.setattr(bundle.shutil, "copyfile", mutate_then_copy)
    with pytest.raises(ValueError, match="changed since rendering"):
        bundle.bundle_project(run, tmp_path / "changed-during-copy")
    receipt = json.loads((tmp_path / "changed-during-copy/bundle.json").read_text())
    assert receipt["status"] == "failed"


@pytest.mark.parametrize("metadata", ["missing", None])
def test_bundle_requires_explicit_sample_provenance(tmp_path, metadata):
    run, _ = fixture(tmp_path)
    path = run / "project-render.json"
    receipt = json.loads(path.read_text())
    if metadata == "missing":
        del receipt["sample_library"]
    else:
        receipt["sample_library"] = metadata
    music.save_json(path, receipt)
    with pytest.raises(TypeError, match="explicitly record its sample library"):
        bundle.bundle_project(run, tmp_path / "rejected")
    assert not (tmp_path / "rejected").exists()
