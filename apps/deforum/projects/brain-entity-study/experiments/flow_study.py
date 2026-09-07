# /// script
# requires-python = ">=3.11,<3.12"
# dependencies = ["torch==2.11.0", "numpy==2.4.6", "opencv-python==5.0.0.93", "pillow==12.3.0"]
# ///
"""Apply the pinned Difforum FlowStabilize implementation to preserved P03 frames.

Run with uv run --script; see continuity.md for execution.
This calls upstream code directly with its node defaults, on CPU, without ComfyUI.
"""

import hashlib
import importlib.util
import json
from pathlib import Path
import platform
import sys
import time
import urllib.request

import cv2
import numpy as np
from PIL import Image
import PIL
import torch

APP = Path(__file__).resolve().parents[3]
PROJECT = Path(__file__).resolve().parents[1]
PARENT = "20260907T075457156677Z-p03-cfg-45-48f"
PIN = "1d750efd3c1d1dda792b8ef6c14b06a14a69f879"
SOURCE_SHA256 = "6a5f8f898ce85ee8baaac39c5edf9166c5cbadabededbc6325d3aeca5e3c608a"
SOURCE_URL = f"https://raw.githubusercontent.com/chillithebillis/Difforum/{PIN}/core/flow.py"
SETTINGS = {"strength": 0.5, "flow_scale": 0.5, "error_gate": 0.15}
EXPORT = PROJECT / "exports/p03-flow-stabilize"
sys.path.insert(0, str(APP))
import editing


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    if EXPORT.exists():
        raise FileExistsError(f"Preserved export already exists: {EXPORT}")
    source = APP / "work/brain-continuity-session/difforum-flow.py"
    source.parent.mkdir(parents=True, exist_ok=True)
    if not source.exists():
        with urllib.request.urlopen(SOURCE_URL, timeout=60) as response:
            data = response.read()
        if hashlib.sha256(data).hexdigest() != SOURCE_SHA256:
            raise ValueError("Upstream source checksum mismatch")
        source.write_bytes(data)
    if sha(source) != SOURCE_SHA256:
        raise ValueError("Cached source checksum mismatch")
    spec = importlib.util.spec_from_file_location("difforum_flow", source)
    flow = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(flow)
    parent = PROJECT / "runs" / PARENT
    receipt = json.loads((parent / "submission.json").read_text())
    assert receipt["collected_at"] and receipt["frames"] == 48 and receipt["generated_fps"] == 8
    paths = [parent / "frames" / f"{i:04d}.png" for i in range(48)]
    frames = torch.from_numpy(np.stack([np.asarray(Image.open(p).convert("RGB"), dtype=np.float32) / 255 for p in paths]))
    torch.set_num_threads(4)
    start = time.monotonic()
    with torch.inference_mode():
        result = flow.stabilize(frames, **SETTINGS)
    seconds = time.monotonic() - start
    assert result.shape == frames.shape and torch.isfinite(result).all()
    assert torch.equal(result[0], frames[0]), "The stabilizer must preserve its opening anchor"
    output = EXPORT / "frames"
    output.mkdir(parents=True, exist_ok=False)
    records = []
    for i, (path, tensor) in enumerate(zip(paths, result)):
        target = output / f"{i:04d}.png"
        Image.fromarray((tensor.numpy() * 255).round().clip(0, 255).astype(np.uint8)).save(target)
        records.append({"source": path.relative_to(PROJECT).as_posix(), "source_sha256": sha(path),
                        "output": target.relative_to(EXPORT).as_posix(), "output_sha256": sha(target)})
    metadata = {"parent_run": PARENT, "operation": "Difforum FlowStabilize (upstream core function)",
                "source_url": SOURCE_URL, "source_sha256": SOURCE_SHA256, "settings": SETTINGS,
                "runtime": {"python": platform.python_version(), "torch": torch.__version__,
                            "numpy": np.__version__, "opencv": cv2.__version__, "pillow": PIL.__version__,
                            "device": "cpu", "torch_threads": 4}, "processing_seconds": seconds,
                "source_fps": 8, "output_unique_frames": 48, "delivery_fps": 24,
                "delivery_method": "repeat each processed image three times", "duration_seconds": 6,
                "frames": records}
    (EXPORT / "processing.json").write_text(json.dumps(metadata, indent=2) + "\n")
    editing.encode(output, EXPORT / "preview.mp4")
    print(json.dumps({"export": str(EXPORT), "processing_seconds": seconds}), flush=True)


if __name__ == "__main__":
    main()
