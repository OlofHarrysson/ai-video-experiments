"""Reproducible, section-based sound inspection using the existing audio tools."""

import argparse
import csv
import json
import re
import subprocess
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

import music

WINDOW_SECONDS = 0.1
SPECTRUM_LIMITS = (-100, -20)


def windows(data, rate):
    """Channel-power RMS and sample peak; never cancel opposing stereo channels."""
    hop = max(1, round(rate * WINDOW_SECONDS))
    rows = []
    for a in range(0, len(data), hop):
        clip = data[a : a + hop]
        rows.append(
            {
                "seconds": a / rate,
                "rms_dbfs": music.db(np.sqrt(np.mean(clip**2))),
                "peak_dbfs": music.db(np.max(np.abs(clip))),
            }
        )
    return rows


def momentary(path):
    """FFmpeg EBU R128 400 ms loudness, timestamped at each window's end."""
    result = subprocess.run(
        [
            "ffmpeg",
            "-nostdin",
            "-v",
            "error",
            "-i",
            str(path),
            "-af",
            "ebur128=metadata=1,ametadata=print:key=lavfi.r128.M:file=-",
            "-f",
            "null",
            "-",
        ],
        capture_output=True,
        text=True,
        check=True,
    )
    pairs = re.findall(r"pts_time:([\d.]+)\s+lavfi.r128.M=([-\d.]+)", result.stdout)
    if not pairs:
        raise ValueError("FFmpeg returned no momentary loudness frames")
    return [
        {
            "seconds": round(float(t) + 0.1, 6),
            "momentary_lufs": float(v)
            if float(t) >= 0.299 and float(v) > -100
            else None,
        }
        for t, v in pairs
    ]


def build(recipe, out):
    recipe = Path(recipe).resolve()
    config = json.loads(recipe.read_text())
    duration = float(config["duration"])
    if not np.isfinite(duration) or duration < 0.4:
        raise ValueError("Duration must be finite and at least 0.4 seconds")
    if not config.get("inputs"):
        raise ValueError("At least one input is required")
    prepared = []
    for item in config["inputs"]:
        path = (recipe.parent / item["path"]).resolve()
        data, sr = music.read_audio(path)
        start = float(item.get("start", 0))
        if (
            not np.isfinite(start)
            or start < 0
            or round((start + duration) * sr) > len(data)
        ):
            raise ValueError(f"Window outside source: {item['name']}")
        a, b = round(start * sr), round((start + duration) * sr)
        prepared.append((item, path, data[a:b], sr))
    out = music.fresh_dir(out).resolve()
    music.save_json(out / "recipe.json", config)
    report = {
        "status": "running",
        "duration": duration,
        "inputs": [],
        "method": "Unnormalized measurements on extracted audio. Spectrograms average channel power, fixed -100 to -20 dB/bin scale. Momentary loudness uses FFmpeg EBU R128 400 ms windows; first 300 ms unavailable. Null denotes silence/below -100 LUFS or unavailable. Cropping retains source tails, but loudness integration restarts at the selected window.",
        "limits": "No taste score, instrument recognition, automatic pitch transcription or proof of masking. Phone/PA/room coloration is not a studio target.",
    }
    music.save_json(out / "report.json", report)
    try:
        fig, axes = plt.subplots(
            len(prepared),
            1,
            figsize=(13, 3 * len(prepared)),
            squeeze=False,
            constrained_layout=True,
        )
        levels, laxes = plt.subplots(
            2, 1, figsize=(13, 7), sharex=True, constrained_layout=True
        )
        zoom, zaxes = plt.subplots(
            len(prepared),
            1,
            figsize=(13, 2 * len(prepared)),
            squeeze=False,
            constrained_layout=True,
        )
        for i, (item, path, data, sr) in enumerate(prepared):
            folder = out / f"{i + 1:02d}"
            folder.mkdir()
            clip = folder / "excerpt.wav"
            music.write_audio(clip, data, sr)
            metrics = music.inspect_audio(clip, folder / "inspection", item.get("bpm"))
            timeline = windows(data, sr)
            loudness = momentary(clip)
            music.save_json(
                folder / "timeline.json", {"levels": timeline, "momentary": loudness}
            )
            with (folder / "levels.csv").open("w", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=list(timeline[0]))
                writer.writeheader()
                writer.writerows(timeline)
            f, t, power = music.spectrogram(data, sr)
            ax = axes[i, 0]
            mesh = ax.pcolormesh(
                t,
                f[1:],
                power[1:],
                shading="auto",
                cmap="magma",
                vmin=SPECTRUM_LIMITS[0],
                vmax=SPECTRUM_LIMITS[1],
            )
            ax.set(
                title=item["name"],
                yscale="log",
                ylim=(30, min(16000, sr / 2)),
                xlim=(0, duration),
                ylabel="Hz",
                xlabel="Seconds into excerpt",
            )
            ax.set_yticks([60, 250, 1000, 4000, 16000])
            ax.yaxis.set_major_formatter(plt.ScalarFormatter())
            fig.colorbar(mesh, ax=ax, label="dB per frequency bin")
            for row in timeline:
                row["plot_rms"] = (
                    max(-80, row["rms_dbfs"]) if row["rms_dbfs"] is not None else -80
                )
            laxes[0].plot(
                [r["seconds"] for r in timeline],
                [r["plot_rms"] for r in timeline],
                label=item["name"],
            )
            laxes[1].plot(
                [r["seconds"] for r in loudness],
                [r["momentary_lufs"] for r in loudness],
                label=item["name"],
            )
            end = min(len(data), round(2 * sr))
            # A fixed two-second close-up, not an automatically inferred note envelope.
            zaxes[i, 0].plot(np.arange(end) / sr, data[:end, 0], lw=0.35)
            zaxes[i, 0].set(
                title=item["name"],
                ylim=(-1, 1),
                xlim=(0, min(2, duration)),
                ylabel="L amplitude",
                xlabel="Seconds into excerpt",
            )
            peak, rms = metrics["sample_peak_dbfs"], metrics["rms_dbfs"]
            record = {
                "name": item["name"],
                "role": item.get("role", "unspecified"),
                "source": str(path),
                "source_sha256": music.digest(path),
                "start": item.get("start", 0),
                "folder": folder.name,
                "metrics": metrics,
                "crest_db": peak - rms
                if peak is not None and rms is not None
                else None,
            }
            report["inputs"].append(record)
        for ax in laxes:
            ax.grid(alpha=0.2)
            ax.legend(fontsize=8, ncol=3)
            ax.set_xlim(0, duration)
        laxes[0].set(ylabel="100 ms RMS (dBFS)", ylim=(-80, 0))
        laxes[1].set(
            ylabel="400 ms loudness (LUFS)",
            xlabel="Seconds into excerpt",
            ylim=(-60, 0),
        )
        fig.savefig(out / "spectra.png", dpi=120)
        plt.close(fig)
        levels.savefig(out / "dynamics.png", dpi=130)
        plt.close(levels)
        zoom.savefig(out / "attacks.png", dpi=120)
        plt.close(zoom)
        # Match ONLY complete mixes/reference recordings, never individual stems.
        comparable = [
            r
            for r in report["inputs"]
            if r["role"] in ["mix", "reference"]
            and r["metrics"]["integrated_lufs"] is not None
        ]
        if comparable:
            # One common target also guarantees at least 1 dB true-peak headroom.
            target = min(
                min(
                    r["metrics"]["integrated_lufs"],
                    r["metrics"]["integrated_lufs"]
                    - r["metrics"]["true_peak_dbtp"]
                    - 1,
                )
                for r in comparable
            )
            report["matched_target_lufs"] = target
            for r in comparable:
                clip, sr = music.read_audio(out / r["folder"] / "excerpt.wav")
                gain = target - r["metrics"]["integrated_lufs"]
                dest = out / r["folder"] / "matched.wav"
                music.write_audio(dest, clip * 10 ** (gain / 20), sr)
                r["matching"] = {
                    "gain_db": gain,
                    "sha256": music.digest(dest),
                    **music.loudness(dest),
                }
                if r["matching"]["true_peak_dbtp"] > -0.9:
                    raise ValueError("Matched copy exceeds expected true-peak headroom")
        report["status"] = "complete"
        lines = [
            "# Sound inspection",
            "",
            report["method"],
            "",
            report["limits"],
            "",
            "| Sound | Integrated LUFS | True peak dBTP | Crest dB |",
            "|---|---:|---:|---:|",
        ]

        def fmt(v):
            return "—" if v is None else f"{v:.2f}"

        for r in report["inputs"]:
            m = r["metrics"]
            lines.append(
                f"| {r['name']} | {fmt(m['integrated_lufs'])} | {fmt(m['true_peak_dbtp'])} | {fmt(r['crest_db'])} |"
            )
        lines += [
            "",
            "![Frequency over time](spectra.png)",
            "",
            "![Level over time](dynamics.png)",
            "",
            "![First two seconds, left channel](attacks.png)",
        ]
        for r in report["inputs"]:
            lines += [
                "",
                f"## {r['name']}",
                "",
                f"[Original-level excerpt]({r['folder']}/excerpt.wav) · [Detailed measurements]({r['folder']}/inspection/metrics.json)",
            ]
            if "matching" in r:
                lines += [
                    f"[Level-matched listening copy]({r['folder']}/matched.wav), {r['matching']['gain_db']:.2f} dB constant attenuation."
                ]
        (out / "report.md").write_text("\n".join(lines) + "\n")
    except Exception as exc:
        report.update(status="failed", error=str(exc))
        raise
    finally:
        music.save_json(out / "report.json", report)
        plt.close("all")
    return {
        "status": "complete",
        "report": str(out / "report.md"),
        "inputs": len(prepared),
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("recipe", type=Path)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(build(args.recipe, args.out), indent=2))
