"""Hashes and immutable experiment records."""

import hashlib
import json
import shutil
from pathlib import Path


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def save(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        require(json.loads(path.read_text()) == data, f"Saved record differs: {path}")
    else:
        path.write_text(json.dumps(data, indent=2) + "\n")


def copy_verified(source, target):
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists():
        require(sha(target) == sha(source), f"Saved copy differs: {target}")
    else:
        shutil.copy2(source, target)


def read(path):
    return json.loads(Path(path).read_text())


def require(condition, message):
    if not condition:
        raise ValueError(message)
