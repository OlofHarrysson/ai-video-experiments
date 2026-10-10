"""Portable snapshots of completed music runs and their registered sample banks."""

import json
import shutil
from pathlib import Path

import soundfile as sf

import music as audio


def inside(root, relative):
    path = (root / relative).resolve()
    if not path.is_relative_to(root):
        raise ValueError(f"Run file escapes its directory: {relative}")
    return path


def checked(path, expected):
    if audio.digest(path) != expected:
        raise ValueError(f"File changed since rendering: {path}")
    return path


def bundle_project(run, out):
    run = Path(run).resolve()
    receipt_path = run / "project-render.json"
    receipt = json.loads(receipt_path.read_text())
    if receipt.get("status") != "complete":
        raise ValueError("Bundle requires a completed project run")
    source = checked(run / "source.strudel", receipt["source"]["sha256"])
    config_path = checked(run / "project.json", receipt["project"]["sha256"])
    config = json.loads(config_path.read_text())
    revision = receipt["revision"]
    if set(receipt["renders"]) != {"master", *config["stems"]}:
        raise ValueError("Completed master and every declared stem are required")
    copies = [
        (source, "source.strudel", receipt["source"]["sha256"]),
        (config_path, "origin/project.json", receipt["project"]["sha256"]),
        (receipt_path, "origin/project-render.json", audio.digest(receipt_path)),
    ]
    for stem, item in receipt["renders"].items():
        if Path(stem).name != stem or stem in {".", ".."}:
            raise ValueError("Invalid stem name")
        wave = checked(inside(run, item["file"]), item["sha256"])
        info = sf.info(wave)
        if (info.frames, info.samplerate, info.channels) != (
            receipt["frames"],
            receipt["sample_rate"],
            2,
        ):
            raise ValueError(f"Misaligned output: {stem}")
        render_path = wave.parent / "render.json"
        rendered = json.loads(render_path.read_text())
        if (
            rendered.get("status") != "complete"
            or rendered["output"]["sha256"] != item["sha256"]
        ):
            raise ValueError(f"Invalid render receipt: {stem}")
        copies.extend(
            [
                (wave, f"renders/{stem}.wav", item["sha256"]),
                (render_path, f"origin/{stem}-render.json", audio.digest(render_path)),
            ]
        )
    library = receipt.get("sample_library")
    if not isinstance(library, list):
        raise TypeError("Completed run must explicitly record its sample library")
    banks = {}
    sample_origins = []
    for sample in library:
        sound, index = sample["name"], sample["index"]
        if (
            not isinstance(sound, str)
            or not sound
            or Path(sound).name != sound
            or sound in {".", ".."}
            or "\\" in sound
        ):
            raise ValueError("Invalid sample bank name")
        if type(index) is not int or index < 0:
            raise ValueError("Invalid sample index")
        banks.setdefault(sound, []).append(index)
        path = checked(Path(sample["path"]), sample["sha256"])
        # Stable numeric names retain n()/slice sample indexing after relocation.
        destination = f"samples/{sound}/{index:08d}{path.suffix.lower()}"
        copies.append((path, destination, sample["sha256"]))
        sample_origins.append({**sample, "bundled_file": destination})
    if any(sorted(indices) != list(range(len(indices))) for indices in banks.values()):
        raise ValueError("Sample bank indices must be unique and contiguous from zero")
    destinations = [destination for _, destination, _ in copies]
    if len(destinations) != len(set(destinations)):
        raise ValueError("Duplicate bundle destination")

    out = audio.fresh_dir(out).resolve()
    manifest = {
        "status": "preparing",
        "revision": revision,
        "run": str(run),
        "files": [],
    }
    audio.save_json(out / "bundle.json", manifest)
    try:
        for source_path, destination, expected in copies:
            target = out / destination
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source_path, target)
            checked(target, expected)
            manifest["files"].append({"file": destination, "sha256": expected})
        portable = {
            **config,
            "revisions": {
                revision: {**config["revisions"][revision], "source": "source.strudel"}
            },
            "samples": ["samples"] if banks else [],
        }
        audio.save_json(out / "project.json", portable)
        audio.save_json(out / "sample-origins.json", sample_origins)
        for filename in ["project.json", "sample-origins.json"]:
            manifest["files"].append(
                {"file": filename, "sha256": audio.digest(out / filename)}
            )
        (out / "README.md").write_text(
            f"# {config.get('title', 'Music project')} — {revision}\n\n"
            "The saved master/stems and registered sample banks are preserved byte-for-byte. "
            "The editable assembled source and project recipe use only local relative paths. "
            "Sample filenames encode their original indices; all registered samples are retained.\n\n"
            f"From an installed music workbench: `uv run --locked python music.py render-project /PATH/TO/BUNDLE/project.json --revision {revision} --out NEW_OUTPUT`. "
            "The locked workbench, Chrome and FFmpeg are still required. Wet rerenders can vary. "
            "Original module files, generators and research remain in the owning repository; this bundle preserves their assembled source and resulting sample assets. "
            "This local snapshot is not a second-device backup.\n"
        )
        manifest["files"].append(
            {"file": "README.md", "sha256": audio.digest(out / "README.md")}
        )
        manifest["status"] = "complete"
    except BaseException as error:
        manifest.update(status="failed", error=str(error))
        raise
    finally:
        audio.save_json(out / "bundle.json", manifest)
    return {
        "status": "complete",
        "output": str(out),
        "revision": revision,
        "files": len(manifest["files"]),
        "sample_banks": len(banks),
    }
