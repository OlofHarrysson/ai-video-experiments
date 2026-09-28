"""Verify downloaded paintings against an independently collected remote hash manifest."""

import argparse
import hashlib
import json
import statistics
from pathlib import Path

ROOT = Path(__file__).parent


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("remote_hashes", type=Path)
    args = parser.parse_args()
    remote = json.loads(args.remote_hashes.read_text())
    records = []
    for folder in sorted((ROOT / "runs").iterdir()):
        history = json.loads((folder / "history.json").read_text())
        assert (
            history["status"]["completed"]
            and history["status"]["status_str"] == "success"
        )
        images = history["outputs"]["11"]["images"]
        assert len(images) == 1
        output = images[0]
        key = output["subfolder"] + "/" + output["filename"]
        local = folder / "frames/0000.png"
        digest = hashlib.sha256(local.read_bytes()).hexdigest()
        assert remote[key] == digest, f"Remote/local output mismatch: {key}"
        assert (
            json.loads((folder / "frame-hashes.json").read_text())["0000.png"] == digest
        )
        messages = dict(history["status"]["messages"])
        seconds = (
            messages["execution_success"]["timestamp"]
            - messages["execution_start"]["timestamp"]
        ) / 1000
        records.append(
            {
                "run": folder.name,
                "remote": key,
                "sha256": digest,
                "execution_seconds": seconds,
            }
        )
    assert len(records) == len(remote), (
        "Some remote paintings are not preserved locally"
    )
    warm = [r["execution_seconds"] for r in records if "-opening-" not in r["run"]]
    receipt = {
        "verified_paintings": len(records),
        "remote_output_files": len(remote),
        "warm_execution_median_seconds": statistics.median(warm),
        "warm_execution_total_seconds": sum(warm),
        "records": records,
    }
    output = ROOT / "exports/preservation.json"
    output.write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps({k: v for k, v in receipt.items() if k != "records"}, indent=2))
