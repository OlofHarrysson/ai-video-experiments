"""Time-resolved stem/band measurements for completed project renders."""

import csv
import json
from itertools import pairwise
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from scipy import signal

import music

BANDS = {
    "low": (30, 180),
    "body": (180, 1200),
    "presence": (1200, 6000),
    "air": (6000, 20000),
}
MEASUREMENT_FLOOR_DBFS = -120


def level(value):
    result = music.db(value)
    return result if result is not None and result >= MEASUREMENT_FLOOR_DBFS else None


def analyze_project(run, out, window_cycles=1):
    run = Path(run).resolve()
    receipt = json.loads((run / "project-render.json").read_text())
    if receipt["status"] != "complete":
        raise ValueError("Analyze a completed project render")
    if not np.isfinite(window_cycles) or window_cycles <= 0:
        raise ValueError("window_cycles must be finite and positive")
    cps, rate, frames = receipt["cps"], receipt["sample_rate"], receipt["frames"]
    hop = window_cycles / cps * rate
    if hop < 1:
        raise ValueError("Window must contain at least one audio frame")
    edges = np.unique(
        np.minimum(np.round(np.arange(0, frames, hop)).astype(int), frames)
    )
    edges = np.r_[edges, frames]
    rows, sources = [], []
    for stem, item in receipt["renders"].items():
        path = run / item["file"]
        if music.digest(path) != item["sha256"]:
            raise ValueError(f"Audio changed since render: {stem}")
        data, sr = music.read_audio(path)
        if sr != rate or len(data) != frames:
            raise ValueError(f"Unaligned rendered stem: {stem}")
        sources.append({"stem": stem, "path": str(path), "sha256": item["sha256"]})
        for band, (low, high) in {"full": (None, None), **BANDS}.items():
            high = min(high, rate * 0.475) if high else None
            if low and low >= high:
                continue
            filtered = (
                data
                if low is None
                else signal.sosfilt(
                    signal.butter(
                        4, [low, high], fs=rate, btype="bandpass", output="sos"
                    ),
                    data,
                    axis=0,
                )
            )
            for i, (start, end) in enumerate(pairwise(edges)):
                clip = filtered[start:end]
                rows.append(
                    {
                        "window": i,
                        "start_seconds": int(start) / rate,
                        "end_seconds": int(end) / rate,
                        "start_cycle": int(start) / rate * cps,
                        "stem": stem,
                        "band": band,
                        "rms_dbfs": level(np.sqrt(np.mean(clip**2))),
                        "peak_dbfs": level(np.max(np.abs(clip))),
                    }
                )
    master = {
        (row["window"], row["band"]): row["rms_dbfs"]
        for row in rows
        if row["stem"] == "master"
    }
    for row in rows:
        reference = master[(row["window"], row["band"])]
        row["relative_to_master_db"] = (
            row["rms_dbfs"] - reference
            if row["rms_dbfs"] is not None and reference is not None
            else None
        )
    out = music.fresh_dir(out)
    report = {
        "status": "complete",
        "run": str(run),
        "sample_rate": rate,
        "frames": frames,
        "cps": cps,
        "window_cycles": window_cycles,
        "method": "RMS of continuous fourth-order Butterworth bandpass filtering, independently rendered stems. Relative levels are not energy shares or perceptual audibility scores. Null means zero energy, below the measurement floor, or unavailable comparison.",
        "measurement_floor_dbfs": MEASUREMENT_FLOOR_DBFS,
        "bands_hz": {
            name: [low, min(high, rate * 0.475)]
            for name, (low, high) in BANDS.items()
            if low < rate * 0.475
        },
        "sections_cycles": receipt.get("sections", {}),
        "sources": sources,
        "windows": rows,
    }
    music.save_json(out / "analysis.json", report)
    with (out / "windows.csv").open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    fig, axes = plt.subplots(
        len(report["bands_hz"]) + 1,
        1,
        figsize=(12, 11),
        sharex=True,
        constrained_layout=True,
    )
    for axis, band in zip(axes, ["full", *report["bands_hz"]], strict=True):
        for stem in receipt["renders"]:
            points = [r for r in rows if r["band"] == band and r["stem"] == stem]
            axis.plot(
                [r["start_seconds"] for r in points],
                [
                    max(r["rms_dbfs"], -90) if r["rms_dbfs"] is not None else -90
                    for r in points
                ],
                label=stem,
                linewidth=2 if stem == "master" else 1,
            )
        axis.set_ylabel(f"{band}\ndBFS RMS")
        axis.set_ylim(-90, 0)
        axis.grid(alpha=0.2)
    axes[0].legend(ncol=min(6, len(receipt["renders"])))
    axes[-1].set_xlabel("Seconds; values below −90 dBFS displayed at the plot floor")
    fig.savefig(out / "levels.png", dpi=130)
    plt.close(fig)
    return {
        "status": "complete",
        "output": str(out.resolve()),
        "windows_per_band": len(edges) - 1,
        "stems": list(receipt["renders"]),
    }
