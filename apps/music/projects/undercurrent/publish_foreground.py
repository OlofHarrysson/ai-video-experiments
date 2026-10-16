"""Publish two 15-second foreground sketches over one shared preserved bed."""

import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
import music

ROOT = Path(__file__).resolve().parent
BASE = ROOT / "exports/player-v003"
OUT = ROOT / "exports/player-v005"
SECONDS = 15
RATE = 48000
FADE_FRAMES = 960
GAINS_DB = {"pulse": 4, "hollow": 2, "previous": 0}


def main():
    OUT.mkdir(parents=True, exist_ok=False)
    (OUT / "audio").mkdir()
    manifest = json.loads((BASE / "manifest.json").read_text())
    bed = np.zeros((SECONDS * RATE, 2))
    tracks = []
    evidence = {
        "source_bundle": "player-v003",
        "seconds": SECONDS,
        "edge_fade_ms": 20,
        "gains_db": GAINS_DB,
        "bed": {},
        "mixes": {},
    }

    def write(key, name, x, enabled=True, group=None):
        x = x[: SECONDS * RATE].copy()
        x[-FADE_FRAMES:] *= np.linspace(1, 0, FADE_FRAMES)[:, None]
        p = OUT / "audio" / f"{key}.wav"
        music.write_audio(p, x, RATE)
        row = {
            "id": key,
            "name": name,
            "enabled": enabled,
            "url": f"/audio/{key}.wav",
            "sha256": music.digest(p),
            "waveform": np.sqrt(np.mean(x.reshape(240, -1, 2) ** 2, axis=(1, 2)))
            .round(5)
            .tolist(),
        }
        if group:
            row["alternativeGroup"] = group
        tracks.append(row)
        return x

    for t in manifest["tracks"]:
        if t.get("alternativeGroup"):
            continue
        p = BASE / t["url"].lstrip("/")
        assert music.digest(p) == t["sha256"]
        x, sr = music.read_audio(p)
        assert sr == RATE
        bed += write(t["id"], t["name"], x)
        evidence["bed"][t["id"]] = {
            "source_sha256": t["sha256"],
            "output_sha256": tracks[-1]["sha256"],
            "unchanged_before_seconds": 14.98,
        }
    for key, name in [
        ("pulse", "Theme · evolving pulse"),
        ("hollow", "Theme · hollow hook"),
        ("previous", "Chords · previous"),
    ]:
        if key == "previous":
            old = next(t for t in manifest["tracks"] if t["id"] == "chords-pocket")
            p = BASE / old["url"].lstrip("/")
        else:
            p = ROOT / f"renders/{key}-{"v002" if key == "pulse" else "v001"}/render.wav"
            assert (
                json.loads(p.with_name("render.json").read_text())["status"]
                == "complete"
            )
        x, sr = music.read_audio(p)
        assert sr == RATE
        x = write(
            f"theme-{key}",
            name,
            x * 10 ** (GAINS_DB[key] / 20),
            key == "pulse",
            "chords",
        )
        mix = bed + x
        assert np.max(np.abs(mix)) < 1
        p = OUT / f"mix-{key}.wav"
        music.write_audio(p, mix, RATE)
        metrics = music.inspect_audio(p, OUT / f"inspect-{key}", 128)
        assert metrics["true_peak_dbtp"] < 0
        evidence["mixes"][key] = metrics
    music.save_json(
        OUT / "manifest.json",
        {
            "version": 2,
            "title": "Undercurrent",
            "duration": SECONDS,
            "bpm": 128,
            "gain": 1,
            "tracks": tracks,
        },
    )
    music.save_json(ROOT / "foreground-evidence.json", evidence)
    recipes = {
        "foreground-lab": {
            "duration": 15,
            "inputs": [
                {
                    "name": name,
                    "path": f"exports/{OUT.name}/audio/theme-{key}.wav",
                    "role": "stem",
                    "bpm": 128,
                }
                for key, name in [
                    ("previous", "Previous chords"),
                    ("pulse", "Evolving pulse"),
                    ("hollow", "Hollow hook"),
                ]
            ],
        },
        "mix-lab": {
            "duration": 15,
            "inputs": [
                {
                    "name": name,
                    "path": f"exports/{OUT.name}/mix-{key}.wav",
                    "role": "mix",
                    "bpm": 128,
                }
                for key, name in [
                    ("previous", "Previous mix"),
                    ("pulse", "Pulse mix"),
                    ("hollow", "Hollow mix"),
                ]
            ]
            + [
                {
                    "name": "Club phone reference",
                    "path": "references/assets/club-phone-20261015/audio.wav",
                    "start": 1,
                    "role": "reference",
                }
            ],
        },
    }
    for name, recipe in recipes.items():
        music.save_json(ROOT / f"{name}.json", recipe)
    print(
        json.dumps(
            {
                k: {m: v[m] for m in ["integrated_lufs", "true_peak_dbtp"]}
                for k, v in evidence["mixes"].items()
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
