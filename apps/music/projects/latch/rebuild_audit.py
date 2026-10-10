"""Rebuild original Latch assets in a fresh directory and verify retained hashes."""

import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
GENERATORS = ("make_palette.py", "make_room_objects.py")
RECEIPTS = ("palette.json", "room-objects.json")


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    records = []
    with tempfile.TemporaryDirectory(prefix="latch-rebuild-") as temp:
        rebuilt = Path(temp)
        for generator in GENERATORS:
            shutil.copy2(ROOT / generator, rebuilt / generator)
            subprocess.run([sys.executable, str(rebuilt / generator)], check=True)
        for receipt_name in RECEIPTS:
            receipt = json.loads((ROOT / receipt_name).read_text())
            generated = json.loads((rebuilt / receipt_name).read_text())
            for item in receipt["assets"]:
                relative = item["file"]
                actual = digest(ROOT / relative)
                fresh = digest(rebuilt / relative)
                if not actual == fresh == item["sha256"]:
                    raise ValueError(f"Asset mismatch: {relative}")
                records.append({"file": relative, "sha256": actual})
            if receipt != generated:
                raise ValueError(f"Recipe mismatch: {receipt_name}")
    print(json.dumps({"status": "complete", "method": "Fresh generator execution; retained and regenerated asset hashes plus full recipe receipts agree", "assets": records}, indent=2))


if __name__ == "__main__":
    main()
