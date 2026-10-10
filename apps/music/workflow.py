"""Saved project renders, exact master excerpts, and matched revision comparisons."""

import json
import math
import re
import subprocess
import sys
from pathlib import Path

import soundfile as sf

import music as audio


def name(value):
    if not isinstance(value, str) or not re.fullmatch(r"[a-z][a-z0-9_-]*", value):
        raise ValueError(f"Use a lowercase name with letters, digits, - or _: {value}")
    return value


def finite(value):
    if (
        isinstance(value, bool)
        or not isinstance(value, (int, float))
        or not math.isfinite(value)
    ):
        raise ValueError(f"Expected a finite number: {value}")
    return value


def load_project(path, revision):
    path = Path(path).resolve()
    config = json.loads(path.read_text())
    if config.get("version") != 1:
        raise ValueError("Project version must be 1")
    selected = config["revisions"][revision]
    source = (path.parent / selected["source"]).resolve()
    end = finite(config["end_cycle"])
    rate = config.get("sample_rate", 48000)
    if end <= 0 or type(rate) is not int or not 8000 <= rate <= 96000:
        raise ValueError(
            "Require positive end_cycle and integer sample_rate between 8000 and 96000"
        )
    stems = config["stems"]
    layers = []
    if not isinstance(stems, dict) or not stems:
        raise ValueError("Declare at least one named stem")
    for stem, labels in stems.items():
        if name(stem) == "master" or not isinstance(labels, list) or not labels:
            raise ValueError(
                "Stem names must differ from master and contain a nonempty label list"
            )
        if any(not isinstance(label, str) for label in labels):
            raise ValueError("Stem labels must be strings")
        layers.extend(labels)
    if len(layers) != len(set(layers)):
        raise ValueError("Each source layer must belong to exactly one stem")
    for section, bounds in config["sections"].items():
        name(section)
        if len(bounds) != 2 or not 0 <= finite(bounds[0]) < finite(bounds[1]) <= end:
            raise ValueError(f"Section {section} must lie within 0..end_cycle")
    samples = [(path.parent / folder).resolve() for folder in config.get("samples", [])]
    if not source.is_file() or any(not folder.is_dir() for folder in samples):
        raise ValueError("Restore the source and all sample folders before rendering")
    return config, selected, source, samples


def render_project(path, revision, out, timeout=120):
    config, selected, source, samples = load_project(path, revision)
    out = audio.fresh_dir(out).resolve()
    (out / "project.json").write_bytes(Path(path).read_bytes())
    (out / "source.strudel").write_bytes(source.read_bytes())
    receipt = {
        "status": "running",
        "title": config.get("title", Path(path).parent.name),
        "revision": revision,
        "notes": selected.get("notes", ""),
        "project": {"path": str(Path(path).resolve()), "sha256": audio.digest(path)},
        "source": {"path": str(source), "sha256": audio.digest(source)},
        "end_cycle": config["end_cycle"],
        "sections": config["sections"],
        "renders": {},
    }
    audio.save_json(out / "project-render.json", receipt)
    try:
        for stem, solo in {"master": [], **config["stems"]}.items():
            print(
                f"Rendering and inspecting {revision}/{stem}",
                file=sys.stderr,
                flush=True,
            )
            command = [
                "node",
                str(audio.ROOT / "renderer/render.mjs"),
                str(out / "source.strudel"),
                "--out",
                str(out / stem),
                "--end",
                str(config["end_cycle"]),
                "--sample-rate",
                str(config.get("sample_rate", 48000)),
                "--timeout",
                str(timeout),
            ]
            for folder in samples:
                command.extend(["--samples", str(folder)])
            for label in solo:
                command.extend(["--solo", label])
            process = subprocess.run(
                command, capture_output=True, text=True, check=False
            )
            if process.returncode:
                raise ValueError(f"{stem} failed: {process.stderr.strip()}")
            rendered = json.loads((out / stem / "render.json").read_text())
            if rendered["status"] != "complete":
                raise ValueError(f"{stem} did not complete")
            if stem == "master":
                labels = rendered["layers"]
                declared = [
                    label for group in config["stems"].values() for label in group
                ]
                if len(set(labels)) != len(labels) or set(labels) != set(declared):
                    raise ValueError(
                        "Source labels and stem groups must form the same complete, unique set"
                    )
                receipt["cps"] = rendered["timing"]["cps"]
                receipt["sample_rate"] = rendered["settings"]["sample_rate"]
                receipt["frames"] = rendered["timing"]["frames"]
                receipt["sample_library"] = rendered["samples"]
            elif (
                rendered["timing"]["cps"],
                rendered["timing"]["frames"],
                rendered["samples"],
            ) != (receipt["cps"], receipt["frames"], receipt["sample_library"]):
                raise ValueError(
                    "Tempo, duration or sample library changed between master and stems"
                )
            metrics = audio.inspect_audio(
                out / stem / "render.wav", out / stem / "inspection"
            )
            receipt["renders"][stem] = {
                "file": f"{stem}/render.wav",
                "sha256": rendered["output"]["sha256"],
                "metrics": metrics,
            }
            audio.save_json(out / "project-render.json", receipt)
        receipt["status"] = "complete"
        (out / "README.md").write_text(
            f"# {receipt['title']} — {revision}\n\n{receipt['notes']}\n\n"
            "| Render | Seconds | LUFS | Peak dBFS |\n| --- | ---: | ---: | ---: |\n"
            + "".join(
                f"| [{stem}]({item['file']}) | {item['metrics']['seconds']:.2f} | {item['metrics']['integrated_lufs']} | {item['metrics']['sample_peak_dbfs']} |\n"
                for stem, item in receipt["renders"].items()
            )
            + "\nStems are separate renders of named layers. Shared effects can differ; preserve the master.\n"
        )
    except BaseException as error:
        receipt.update(status="failed", error=str(error))
        raise
    finally:
        audio.save_json(out / "project-render.json", receipt)
    return {
        "status": "complete",
        "output": str(out),
        "revision": revision,
        "renders": list(receipt["renders"]),
    }


def section_window(run, section, lead=0, tail=0, stem="master"):
    run = Path(run).resolve()
    receipt = json.loads((run / "project-render.json").read_text())
    if receipt["status"] != "complete":
        raise ValueError("Use a completed project render")
    if finite(lead) < 0 or finite(tail) < 0:
        raise ValueError("Lead and tail seconds must be nonnegative")
    begin, end = receipt["sections"][section]
    cps = receipt["cps"]
    start, stop = begin / cps - lead, end / cps + tail
    duration = receipt["frames"] / receipt["sample_rate"]
    if start < 0 or stop > duration:
        raise ValueError(
            "Requested lead/tail exceeds the master; extend the arrangement/export or request less context"
        )
    item = receipt["renders"][stem]
    path = run / item["file"]
    if audio.digest(path) != item["sha256"]:
        raise ValueError("Rendered audio changed since the receipt was written")
    return receipt, path, start, stop


def preview(run, section, out, lead=0, tail=0, stem="master"):
    receipt, path, start, stop = section_window(run, section, lead, tail, stem)
    out = audio.fresh_dir(out)
    audio.excerpt(path, out / "preview.wav", start, stop - start)
    result = {
        "revision": receipt["revision"],
        "section": section,
        "stem": stem,
        "source": str(path),
        "source_sha256": audio.digest(path),
        "start_seconds": start,
        "end_seconds": stop,
        "lead_seconds": lead,
        "tail_seconds": tail,
        "output_sha256": audio.digest(out / "preview.wav"),
        "method": "exact excerpt of completed render, preserving prior effect state; context includes adjacent notes",
    }
    audio.save_json(out / "preview.json", result)
    return result


def compare_revisions(
    reference, candidate, section, out, lead=0, tail=0, stem="master"
):
    windows = [
        section_window(run, section, lead, tail, stem) for run in [reference, candidate]
    ]
    # Different tempo/range needs a deliberate comparison definition, not stretching.
    a, b = windows
    if (a[0]["cps"], a[0]["sample_rate"], a[0]["sections"][section]) != (
        b[0]["cps"],
        b[0]["sample_rate"],
        b[0]["sections"][section],
    ):
        raise ValueError(
            "Revision comparison requires the same section cycles, tempo and sample rate"
        )
    out = audio.fresh_dir(out)
    result = {"status": "running", "section": section, "stem": stem, "versions": {}}
    audio.save_json(out / "comparison.json", result)
    try:
        originals = []
        for label, (receipt, path, start, stop) in zip(
            ["A", "B"], windows, strict=True
        ):
            clip = out / f"{label}.wav"
            audio.excerpt(path, clip, start, stop - start)
            originals.append(clip)
            result["versions"][label] = {
                "revision": receipt["revision"],
                "notes": receipt["notes"],
                "source": str(path),
                "source_sha256": audio.digest(path),
                "start_seconds": start,
                "end_seconds": stop,
                "original_sha256": audio.digest(clip),
            }
        audio.match(originals, out / "matched")
        matched = json.loads((out / "matched/manifest.json").read_text())
        for label, record in zip(["A", "B"], matched["copies"], strict=True):
            path = out / "matched" / record["file"]
            result["versions"][label].update(
                file=f"matched/{record['file']}",
                gain_db=record["gain_db"],
                sha256=audio.digest(path),
                frames=sf.info(path).frames,
            )
        result.update(
            status="complete",
            target_lufs=matched["target_lufs"],
            method=matched["method"],
        )
        (out / "README.md").write_text(
            f"# {section}: {stem} revision comparison\n\n"
            + "\n\n".join(
                f"[{label}: {item['revision']}]({item['file']}) — {item['notes']}"
                for label, item in result["versions"].items()
            )
            + f"\n\nMatched to {result['target_lufs']} LUFS by constant attenuation. No compression or time alignment. Context includes adjacent notes. Reverb may vary independently of the revision.\n"
        )
    except BaseException as error:
        result.update(status="failed", error=str(error))
        raise
    finally:
        audio.save_json(out / "comparison.json", result)
    return result
