"""Preserved-frame interpolation using the author's RIFE 4.25.

Run with work/rife-session/.venv/bin/python. Setup and exact commands are in
projects/brain-entity-study/experiments/rife-results.md. No model downloads,
source edits, device fallback, frame skipping, or motion estimation live here.
"""

import argparse
from datetime import datetime, timezone
from fractions import Fraction
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import platform
import shutil
import subprocess
import sys
import time

PIN = "bbfd2ea90910789a860ea3e2b32a240cd577b75e"
MODEL_URL = "https://drive.google.com/uc?id=1ZKjcbmt1hypiFprJPIKW0Tt0lr_2i7bg"
SOURCE_FRAMES = 48
SOURCE_FPS = 8
MULTIPLIER = 3
SCALES = [16, 8, 4, 2, 1]


def sha256(path):
    with Path(path).open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def command(args):
    return subprocess.run(args, check=True, capture_output=True, text=True).stdout


def frame_plan(count, final_holds=None, multiplier=MULTIPLIER):
    """Each pair owns its left anchor; the final anchor appears just once."""
    if count < 2 or multiplier < 2:
        raise ValueError('At least two frames and multiplier >= 2 required')
    if final_holds is None:
        final_holds = multiplier - 1
    rows = []
    for index in range(count - 1):
        rows.append({"kind": "anchor", "source_index": index})
        for numerator in range(1, multiplier):
            rows.append({"kind": "interpolation", "source_pair": [index, index + 1],
                         "timestep": f"{numerator}/{multiplier}"})
    rows.append({"kind": "anchor", "source_index": count - 1})
    rows.extend({"kind": "final_hold", "source_index": count - 1}
                for _ in range(final_holds))
    return rows


def inventory(source, expected_count=SOURCE_FRAMES):
    from PIL import Image

    files = list(source.glob("*.png"))
    if len(files) != expected_count or any(not p.stem.isdecimal() for p in files):
        raise ValueError(f"Expected exactly {expected_count} numerically named original PNGs")
    files.sort(key=lambda p: int(p.stem))
    if [int(p.stem) for p in files] != list(range(expected_count)):
        raise ValueError(f"Source indices must be unique and contiguous from 0 through {expected_count-1}")
    rows = []
    for path in files:
        with Image.open(path) as im:
            im.load()
            if im.mode != "RGB" or any(n % 2 for n in im.size):
                raise ValueError("Expected RGB PNGs with even dimensions")
            rows.append({"file": str(path), "sha256": sha256(path),
                         "size": list(im.size), "mtime_ns": path.stat().st_mtime_ns})
    if any(row["size"] != rows[0]["size"] for row in rows):
        raise ValueError("Source dimensions differ")
    return files, rows


def motion_settings(scale):
    """Author RIFE_HDv3.inference scales and inference_video padding rule."""
    if scale not in (0.5, 1.0):
        raise ValueError("Motion scale must be 0.5 or 1.0")
    return [value / scale for value in SCALES], max(128, int(128 / scale))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--source-frames", type=int, default=SOURCE_FRAMES)
    parser.add_argument("--source-fps", type=Fraction, default=Fraction(SOURCE_FPS),
                        help="Original anchor rate, including fractions such as 12/5")
    parser.add_argument("--multiplier", type=int, default=MULTIPLIER)
    parser.add_argument("--motion-scale", type=float, choices=(0.5, 1.0), default=1.0,
                        help="Internal motion estimation scale; output remains full resolution")
    parser.add_argument("--rife-root", type=Path,
                        default=Path(__file__).parent / "work/rife-session/Practical-RIFE")
    parser.add_argument("--pair-only", action="store_true")
    parser.add_argument("--validated-pair", type=Path,
                        help="Successful first-pair manifest, inspected before full execution")
    args = parser.parse_args()
    if args.source_frames < 2 or args.source_fps <= 0 or args.multiplier < 2:
        parser.error('Need at least two frames, positive FPS and multiplier >= 2')
    exact_output_fps = args.source_fps * args.multiplier
    output_fps = int(exact_output_fps) if exact_output_fps.denominator == 1 else float(exact_output_fps)
    multiplier = args.multiplier
    scales, padding_multiple = motion_settings(args.motion_scale)
    started = time.perf_counter()
    source, output, root = args.source.resolve(), args.output.resolve(), args.rife_root.resolve()
    if output.exists() or output.is_relative_to(source):
        raise ValueError("Output must be new and outside the source directory")
    if os.environ.get("PYTORCH_ENABLE_MPS_FALLBACK", "0") != "0":
        raise ValueError("Disable PYTORCH_ENABLE_MPS_FALLBACK; this experiment requires MPS")
    files, source_rows = inventory(source, args.source_frames)
    commit = command(["git", "-C", str(root), "rev-parse", "HEAD"]).strip()
    dirty = command(["git", "-C", str(root), "status", "--porcelain", "--untracked-files=no"])
    if commit != PIN or dirty:
        raise ValueError("Practical-RIFE must be at the requested pin with unchanged tracked files")
    code_files = sorted((root / "model").glob("*.py")) + sorted((root / "train_log").glob("*.py"))
    provenance = {
        "repository": "https://github.com/hzwer/Practical-RIFE", "commit": commit,
        "model": "RIFE 4.25", "model_url": MODEL_URL,
        "weights_sha256": sha256(root / "train_log/flownet.pkl"),
        "bundle_sha256": sha256(root.parent / "rife425.zip"),
        "code_sha256": {str(p.relative_to(root)): sha256(p) for p in code_files},
        "runner_sha256": sha256(__file__),
    }
    import numpy as np
    from PIL import Image
    import torch
    import torch.nn.functional as F

    if not torch.backends.mps.is_available():
        raise RuntimeError("MPS unavailable; no automatic CPU or cloud fallback")
    versions = {name: importlib.metadata.version(name) for name in ("torch", "numpy", "pillow")}
    settings = {"source_fps": float(args.source_fps), "output_fps": output_fps,
                "multiplier": multiplier, "timesteps": [f"{i}/{multiplier}" for i in range(1,multiplier)],
                "scale_list": scales, "scale": args.motion_scale, "device": "mps", "dtype": "float32",
                "batch_size": 1, "ensemble": False, "fastmode": True, "compilation": False,
                "padding": f"right/bottom zero padding to multiples of {padding_multiple}, cropped afterward",
                "color": "RGB, uint8 / 255", "quantization": "multiply by 255, truncate to uint8",
                "scene_detection": False, "static_frame_skipping": False,
                "mps_cpu_fallback": False, "versions": versions}
    if not args.pair_only:
        if not args.validated_pair:
            raise ValueError("Run and inspect --pair-only before supplying --validated-pair")
        gate = json.loads(args.validated_pair.read_text())
        if (gate.get("status") != "complete" or gate.get("mode") != "first_pair"
                or gate["sources"] != source_rows or gate["provenance"] != provenance
                or gate["settings"] != settings):
            raise ValueError("First-pair validation does not match sources, implementation or settings")
        for row in gate["output_frames"]:
            if sha256(args.validated_pair.parent / row["file"]) != row["sha256"]:
                raise ValueError("First-pair output changed after validation")

    sys.path.insert(0, str(root))
    # Exact author network and forward call from train_log/RIFE_HDv3.py inference().
    # Avoid its training-only optimizer/loss setup and CUDA/CPU-only device selector.
    from train_log.IFNet_HDv3 import IFNet

    torch.set_grad_enabled(False)
    network = IFNet()
    weights = torch.load(root / "train_log/flownet.pkl", map_location="cpu", weights_only=True)
    weights = {k.removeprefix("module."): v for k, v in weights.items()}
    # The author bundle comments out these two training-only modules in IFNet.
    training_keys = [k for k in weights if k.startswith(("teacher.", "caltime."))]
    network.load_state_dict({k: v for k, v in weights.items() if k not in training_keys}, strict=True)
    network.eval().to(device="mps", dtype=torch.float32)
    torch.mps.synchronize()
    model_ready = time.perf_counter()
    output.mkdir(parents=True)
    (output / "frames").mkdir()
    selected = files[:2] if args.pair_only else files
    plan = frame_plan(len(selected), final_holds=0 if args.pair_only else multiplier-1,
                      multiplier=multiplier)
    width, height = source_rows[0]["size"]
    padding = (0, (-width) % padding_multiple, 0, (-height) % padding_multiple)
    receipt = {"status": "running", "mode": "first_pair" if args.pair_only else "full",
               "started_utc": datetime.now(timezone.utc).isoformat(),
               "command": [sys.executable, *sys.argv], "cwd": str(Path.cwd()),
               "platform": platform.platform(), "python": sys.version,
               "hardware": command(["sysctl", "-n", "machdep.cpu.brand_string"]).strip(),
               "sources": source_rows, "provenance": provenance, "settings": settings,
               "validated_pair": str(args.validated_pair.resolve()) if args.validated_pair else None,
               "padding_pixels": list(padding), "pair_timings_seconds": [], "output_frames": [],
               "setup_seconds": model_ready - started, "discarded_training_weight_keys": training_keys,
               "ffmpeg_version": command(["ffmpeg", "-version"]).splitlines()[0]}

    def save_receipt():
        (output / "manifest.json").write_text(json.dumps(receipt, indent=2) + "\n")

    def tensor(path):
        with Image.open(path) as im:
            array = np.array(im, dtype=np.uint8)
        value = torch.from_numpy(array.transpose(2, 0, 1).copy()).unsqueeze(0).to("mps").float() / 255
        return F.pad(value, padding)

    save_receipt()
    left = tensor(selected[0])
    try:
        with torch.inference_mode():
            for index in range(len(selected) - 1):
                pair_start = time.perf_counter()
                right = tensor(selected[index + 1])
                shutil.copy2(selected[index], output / "frames" / f"{index * multiplier:04d}.png")
                for offset in range(1, multiplier):
                    _, _, merged = network(torch.cat((left, right), 1), offset / multiplier, scales,
                                           fastmode=True, ensemble=False)
                    result = merged[-1][0, :, :height, :width]
                    if result.shape != (3, height, width) or not torch.isfinite(result).all().item():
                        raise RuntimeError("Invalid RIFE tensor shape or nonfinite output")
                    if result.min().item() < -0.00001 or result.max().item() > 1.00001:
                        raise RuntimeError("RIFE output exceeds normalized RGB range")
                    pixels = (result * 255).byte().cpu().numpy().transpose(1, 2, 0)
                    Image.fromarray(pixels).save(output / "frames" / f"{index * multiplier + offset:04d}.png")
                    del merged, result
                left = right
                torch.mps.synchronize()
                receipt["pair_timings_seconds"].append(time.perf_counter() - pair_start)
                save_receipt()
                print(f"{output.name}: pair {index + 1}/{len(selected) - 1} "
                      f"{receipt['pair_timings_seconds'][-1]:.2f}s", flush=True)
        for index in range((len(selected) - 1) * multiplier, len(plan)):
            shutil.copy2(selected[-1], output / "frames" / f"{index:04d}.png")
        for index, row in enumerate(plan):
            path = output / "frames" / f"{index:04d}.png"
            digest = sha256(path)
            if row["kind"] != "interpolation" and digest != source_rows[row["source_index"]]["sha256"]:
                raise RuntimeError("Original anchor/hold was not preserved byte-for-byte")
            receipt["output_frames"].append({**row, "index": index, "time_seconds": index / output_fps,
                                               "file": str(path.relative_to(output)), "sha256": digest})
        receipt["render_seconds"] = time.perf_counter() - model_ready
        encode_start = time.perf_counter()
        encode = ["ffmpeg", "-hide_banner", "-loglevel", "error", "-n", "-framerate", str(exact_output_fps),
                  "-start_number", "0", "-i", str(output / "frames/%04d.png"),
                  "-frames:v", str(len(plan)), "-an", "-c:v", "libx264", "-preset", "slow",
                  "-crf", "18", "-pix_fmt", "yuv420p", "-movie_timescale", str(exact_output_fps.numerator),
                  "-movflags", "+faststart", str(output / "preview.mp4")]
        command(encode)
        receipt["encode_command"] = encode
        receipt["encode_seconds"] = time.perf_counter() - encode_start
        probe = json.loads(command(["ffprobe", "-v", "error", "-count_frames", "-select_streams", "v:0",
                                    "-show_streams", "-of", "json", str(output / "preview.mp4")]))
        stream = probe["streams"][0]
        if (int(stream["nb_read_frames"]) != len(plan) or Fraction(stream["avg_frame_rate"]) != exact_output_fps
                or abs(float(stream["duration"]) - len(plan) / output_fps) > 0.00001
                or (stream["width"], stream["height"]) != (width, height)):
            raise RuntimeError("Encoded video count, FPS, duration or dimensions differ")
        if inventory(source, args.source_frames)[1] != source_rows:
            raise RuntimeError("Source PNGs changed during execution")
        receipt.update(status="complete", probe=probe, video_sha256=sha256(output / "preview.mp4"),
                       elapsed_seconds=time.perf_counter() - started,
                       anchors_verified=True, source_hashes_and_mtimes_preserved=True,
                       final_holds=0 if args.pair_only else multiplier-1)
        save_receipt()
        print(json.dumps({"output": str(output), "frames": len(plan), "status": "complete"}), flush=True)
    except BaseException as error:
        receipt.update(status="failed", error=repr(error), elapsed_seconds=time.perf_counter() - started)
        save_receipt()
        raise


if __name__ == "__main__":
    main()
