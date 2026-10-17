"""Compare published stems in the same active passage; verify requested changes."""

import json
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from scipy import signal

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
import music

ROOT = Path(__file__).resolve().parent
VERSIONS = ["v002", "v003"]
START = 45.714286
DURATION = 15
OUT = ROOT / "exports/balance-v003"


def main():
    OUT.mkdir(parents=True, exist_ok=False)
    rows = []
    for version in VERSIONS:
        bundle = ROOT / f"exports/player-{version}"
        manifest = json.loads((bundle / "manifest.json").read_text())
        for track in manifest["tracks"]:
            path = bundle / track["url"].lstrip("/")
            assert music.digest(path) == track["sha256"]
            x, sr = music.read_audio(path)
            clip = x[round(START * sr) : round((START + DURATION) * sr)]
            band = signal.sosfilt(
                signal.butter(4, [250, 4000], btype="bandpass", fs=sr, output="sos"),
                clip,
                axis=0,
            )
            rows.append(
                {
                    "version": version,
                    "id": track["id"],
                    "name": track["name"],
                    "sha256": track["sha256"],
                    "rms_dbfs": music.db(np.sqrt(np.mean(clip**2))),
                    "midrange_rms_dbfs": music.db(np.sqrt(np.mean(band**2))),
                }
            )
    before = {r["id"]: r for r in rows if r["version"] == VERSIONS[0]}
    after = {r["id"]: r for r in rows if r["version"] == VERSIONS[1]}
    changes = {k: after[k]["rms_dbfs"] - before[k]["rms_dbfs"] for k in after}
    assert abs(changes["arpeggio"] - 9) < 0.15
    assert abs(changes["harmony"] + 4.5) < 0.15
    # Every formerly absent bar must now contain the kick and bass.
    continuation = {}
    for key in ["kick", "bass"]:
        x, sr = music.read_audio(ROOT / f"exports/player-v003/audio/{key}.wav")
        values = [
            music.db(
                np.sqrt(
                    np.mean(
                        x[
                            round(bar * 240 / 126 * sr) : round(
                                (bar + 1) * 240 / 126 * sr
                            )
                        ]
                        ** 2
                    )
                )
            )
            for bar in range(16, 24)
        ]
        assert all(v is not None and v > -40 for v in values)
        continuation[key] = values
    fig, axes = plt.subplots(1, 2, figsize=(12, 5), constrained_layout=True)
    y = np.arange(len(after))
    for ax, field, label in zip(
        axes,
        ["rms_dbfs", "midrange_rms_dbfs"],
        ["Full-band average level", "250–4000 Hz average level"],
        strict=True,
    ):
        ax.barh(
            y - 0.18,
            [before[k][field] + 80 for k in after],
            0.34,
            left=-80,
            label="Before",
            color="#8c96a8",
        )
        ax.barh(
            y + 0.18,
            [after[k][field] + 80 for k in after],
            0.34,
            left=-80,
            label="Revised",
            color="#416aff",
        )
        ax.set(
            yticks=y,
            yticklabels=[r["name"] for r in after.values()],
            xlim=(-80, 0),
            xlabel="dBFS RMS",
            title=label,
        )
        ax.invert_yaxis()
        ax.grid(axis="x", alpha=0.2)
        ax.legend()
    fig.savefig(OUT / "balance.png", dpi=130)
    plt.close(fig)
    result = {
        "start_seconds": START,
        "duration": DURATION,
        "method": "Same active 15-second passage, published stem gains, channel-power RMS and fourth-order 250–4000 Hz bandpass. No individual normalization. Relative energy is not a perceptual masking score or a target of equal loudness.",
        "rows": rows,
        "changes_db": changes,
        "former_break_bar_rms": continuation,
    }
    music.save_json(ROOT / "balance-v003.json", result)
    lines = [
        "# Instrument balance",
        "",
        result["method"],
        "",
        "![Before and revised balance](balance.png)",
        "",
        "| Part | Before RMS dBFS | Revised RMS dBFS | Change dB |",
        "| --- | ---: | ---: | ---: |",
    ]
    for k, r in after.items():
        lines.append(
            f"| {r['name']} | {before[k]['rms_dbfs']:.1f} | {r['rms_dbfs']:.1f} | {changes[k]:+.1f} |"
        )
    lines += [
        "",
        "The arpeggio was roughly 15 dB below the lead in this passage. Its measured lift and reduced chord level improve the intended separation, but listening is still required to judge audibility and musical balance. The continuous kick/bass in all eight former break/build bars was verified from the rendered stems.",
    ]
    (OUT / "report.md").write_text("\n".join(lines) + "\n")
    print(json.dumps(changes, indent=2))


if __name__ == "__main__":
    main()
