import json
from types import SimpleNamespace

import numpy as np
import pytest
import soundfile as sf

import music
import workflow


def saved_run(root, revision="v001", gain=1):
    root.mkdir()
    sr = 24000
    time = np.arange(8 * sr) / sr
    # The selected section starts after the note, inside its decay tail.
    wave = 0.4 * np.sin(2 * np.pi * 440 * time) * np.exp(-time / 2) * gain
    path = root / "master.wav"
    sf.write(path, np.column_stack([wave, wave]), sr, subtype="FLOAT")
    music.save_json(
        root / "project-render.json",
        {
            "status": "complete",
            "revision": revision,
            "notes": "Controlled test",
            "cps": 1,
            "sample_rate": sr,
            "frames": len(time),
            "sections": {"tail": [2, 4]},
            "renders": {"master": {"file": "master.wav", "sha256": music.digest(path)}},
        },
    )
    return root


def test_preview_preserves_prior_audio_state_and_exact_window(tmp_path):
    run = saved_run(tmp_path / "run")
    report = workflow.preview(run, "tail", tmp_path / "preview", lead=0.5, tail=0.75)
    original, sr = sf.read(run / "master.wav", always_2d=True)
    preview, _ = sf.read(tmp_path / "preview/preview.wav", always_2d=True)
    np.testing.assert_array_equal(preview, original[int(1.5 * sr) : int(4.75 * sr)])
    assert np.max(np.abs(preview[:sr])) > 0.05
    assert report["start_seconds"] == 1.5
    with pytest.raises(FileExistsError):
        workflow.preview(run, "tail", tmp_path / "preview")


def test_preview_rejects_insufficient_context_and_changed_audio(tmp_path):
    run = saved_run(tmp_path / "run")
    with pytest.raises(ValueError, match="exceeds the master"):
        workflow.preview(run, "tail", tmp_path / "too-long", tail=5)
    with (run / "master.wav").open("ab") as stream:
        stream.write(b"changed")
    with pytest.raises(ValueError, match="changed since"):
        workflow.preview(run, "tail", tmp_path / "changed")


def test_revision_comparison_matches_levels_and_preserves_inputs(tmp_path):
    first = saved_run(tmp_path / "first")
    second = saved_run(tmp_path / "second", "v002", 0.5)
    original_hashes = [music.digest(run / "master.wav") for run in [first, second]]
    result = workflow.compare_revisions(first, second, "tail", tmp_path / "ab")
    assert result["status"] == "complete"
    assert result["versions"]["A"]["gain_db"] == pytest.approx(-6.02, abs=0.03)
    assert result["versions"]["B"]["gain_db"] == 0
    a, _ = sf.read(tmp_path / "ab" / result["versions"]["A"]["file"])
    b, _ = sf.read(tmp_path / "ab" / result["versions"]["B"]["file"])
    assert np.max(np.abs(a - b)) < 0.001
    assert [
        music.digest(run / "master.wav") for run in [first, second]
    ] == original_hashes


def test_revision_comparison_rejects_different_tempo_and_retains_failed_silence(
    tmp_path,
):
    first = saved_run(tmp_path / "first")
    second = saved_run(tmp_path / "second", "v002", 0)
    with pytest.raises(ValueError, match="silent"):
        workflow.compare_revisions(first, second, "tail", tmp_path / "silent")
    assert (
        json.loads((tmp_path / "silent/comparison.json").read_text())["status"]
        == "failed"
    )
    receipt = json.loads((second / "project-render.json").read_text())
    receipt["cps"] = 0.5
    music.save_json(second / "project-render.json", receipt)
    with pytest.raises(ValueError, match="same section"):
        workflow.compare_revisions(first, second, "tail", tmp_path / "wrong-tempo")


def project_file(tmp_path):
    (tmp_path / "source.strudel").write_text('setcpm(60)\nvoice: s("sine")')
    config = {
        "version": 1,
        "revisions": {"v001": {"source": "source.strudel"}},
        "end_cycle": 4,
        "stems": {"voice": ["voice"]},
        "sections": {"intro": [0, 2]},
    }
    path = tmp_path / "project.json"
    music.save_json(path, config)
    return path, config


def test_project_validates_partition_and_relative_paths(tmp_path):
    path, config = project_file(tmp_path)
    _, _, source, _ = workflow.load_project(path, "v001")
    assert source == tmp_path / "source.strudel"
    config["stems"]["duplicate"] = ["voice"]
    music.save_json(path, config)
    with pytest.raises(ValueError, match="exactly one"):
        workflow.load_project(path, "v001")


def test_project_records_failure_without_claiming_complete(tmp_path, monkeypatch):
    path, _ = project_file(tmp_path)
    monkeypatch.setattr(
        workflow.subprocess,
        "run",
        lambda *args, **kwargs: SimpleNamespace(returncode=1, stderr="sound missing"),
    )
    with pytest.raises(ValueError, match="sound missing"):
        workflow.render_project(path, "v001", tmp_path / "failed")
    receipt = json.loads((tmp_path / "failed/project-render.json").read_text())
    assert receipt["status"] == "failed"
    assert (tmp_path / "failed/source.strudel").read_text() == (
        tmp_path / "source.strudel"
    ).read_text()
