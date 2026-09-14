"""Replay archived model responses through the current runner; never contact a GPU."""

import argparse
import contextlib
import io
import json
import shutil
from pathlib import Path

import early_settle as experiment
import numpy as np
from PIL import Image

from deforum_lab.records import read, require, sha


class RecordedClient:
    def __init__(self, archive):
        self.archive = archive
        self.calls = []

    def submit_once(self, output, name, graph, source, lineage):
        matches = list((self.archive / "runs").glob("*-" + name + "-1f"))
        require(len(matches) == 1, "Missing or ambiguous archived response")
        recorded = matches[0]
        require(
            read(recorded / "workflow.api.json") == graph,
            "Requested graph differs from archive",
        )
        original_input = recorded / "anchor.png"
        with Image.open(source) as actual, Image.open(original_input) as expected:
            require(
                actual.mode == expected.mode == "RGB"
                and actual.size == expected.size
                and np.array_equal(np.asarray(actual), np.asarray(expected)),
                "Recurrent input pixels differ from archive",
            )
            encoding_differs = sha(source) != sha(original_input)
            if encoding_differs:
                encoded = io.BytesIO()
                Image.fromarray(np.asarray(expected)).save(encoded, format="PNG")
                require(
                    encoded.getvalue() == source.read_bytes(),
                    "Difference is not explained by local PNG encoding",
                )
        submission = read(recorded / "submission.json")
        require(
            all(
                submission.get(key) == value
                for key, value in lineage.items()
                if key != "initialization_sha256"
            ),
            "Parent lineage differs",
        )
        if "initialization_sha256" in lineage:
            require(
                lineage["initialization_sha256"] == sha(source),
                "Input receipt hash differs",
            )
        target = output / "runs" / recorded.name
        if not target.exists():
            (target / "frames").mkdir(parents=True)
            shutil.copy2(recorded / "workflow.api.json", target / "workflow.api.json")
            shutil.copy2(recorded / "frames/0000.png", target / "frames/0000.png")
            shutil.copy2(source, target / "anchor.png")
            # These are replay inputs and recorded responses, not new execution histories.
            (target / "replay-request.json").write_text(json.dumps(lineage, indent=2))
        self.calls.append(
            {
                "name": name,
                "input_sha256": sha(source),
                "graph_matched": True,
                "input_pixels_matched": True,
                "png_encoding_differs": encoding_differs,
            }
        )
        return target


def replay(output):
    output.mkdir(parents=True, exist_ok=False)
    client = RecordedClient(experiment.OUT)
    experiment.prepare(output=output, config_path=output / "config.json")
    log = io.StringIO()
    with contextlib.redirect_stdout(log):
        experiment.render(client, output=output)
    require(
        len(client.calls) == 8, "Expected one control and seven recurrent responses"
    )
    actual = output / experiment.CASE
    original = experiment.OUT / experiment.CASE
    for path in (actual / "anchors").glob("*.png"):
        require(
            sha(path) == sha(original / "anchors" / path.name),
            "Painting differs: " + path.name,
        )
    for path in actual.glob("*.json"):
        current, previous = read(path), read(original / path.name)
        if path.name.startswith("anchor-"):
            frame = current["frame"]
            require(
                current.pop("initialization_sha256")
                == sha(actual / f"warped-inputs/{frame:04d}.png"),
                "Replayed input receipt hash differs",
            )
            previous.pop("initialization_sha256")
        require(current == previous, "Receipt differs: " + path.name)
    calls = len(client.calls)
    with contextlib.redirect_stdout(log):
        experiment.render(client, output=output)
    require(
        len(client.calls) == calls + 1,
        "Resume should only recheck its recorded runtime control",
    )
    (output / "replay.log").write_text(log.getvalue())
    report = {
        "verified": True,
        "scope": "Offline response replay; no model inference or cloud access",
        "source_archive": str(experiment.OUT),
        "paintings_identical": 16,
        "warped_initialization_pixels_identical": 7,
        "graphs_and_parent_lineage_identical": 8,
        "input_png_encoding_differences": sum(
            row["png_encoding_differs"] for row in client.calls[:8]
        ),
        "encoding_note": "Input pixels and locally re-encoded reference bytes match. Input-file hashes "
        "may differ from the original Pod encoder; replay receipts use their actual local hashes.",
        "new_paintings_on_resume": 0,
        "calls": client.calls,
    }
    (output / "replay-check.json").write_text(json.dumps(report, indent=2) + "\n")
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    print(json.dumps(replay(args.output.resolve()), indent=2))
