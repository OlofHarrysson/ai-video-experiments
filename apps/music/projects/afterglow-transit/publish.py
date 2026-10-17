"""Publish aligned rendered stems to the shared player without replacing archives."""

import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
import music

ROOT = Path(__file__).resolve().parent
RENDER = ROOT / "renders/v002"
OUT = ROOT / "exports/player-v002"
GAIN = 0.85
NAMES = {
    "kick": "Kick",
    "bass": "Bass",
    "clap": "Clap",
    "hats": "Hi-hats",
    "percussion": "Wood percussion",
    "harmony": "Warm chords",
    "melody": "Lead melody",
    "arpeggio": "Arpeggio",
    "air": "Air swells",
}


def main():
    receipt = json.loads((RENDER / "project-render.json").read_text())
    assert receipt["status"] == "complete" and not receipt["warnings"]
    OUT.mkdir(parents=True, exist_ok=False)
    (OUT / "audio").mkdir()
    tracks, sources = [], {}
    total = np.zeros((receipt["frames"], 2))
    for key, name in NAMES.items():
        p = RENDER / receipt["renders"][key]["file"]
        assert music.digest(p) == receipt["renders"][key]["sha256"]
        x, rate = music.read_audio(p)
        assert rate == 48000 and x.shape == total.shape
        # Equal master attenuation and a short common end fade preserve stem balance.
        x *= GAIN
        x[-7200:] *= np.linspace(1, 0, 7200)[:, None]
        total += x
        dest = OUT / "audio" / f"{key}.wav"
        music.write_audio(dest, x, rate)
        waveform = [float(np.sqrt(np.mean(part**2))) for part in np.array_split(x, 240)]
        tracks.append(
            {
                "id": key,
                "name": name,
                "enabled": True,
                "url": f"/audio/{key}.wav",
                "sha256": music.digest(dest),
                "waveform": waveform,
            }
        )
        sources[key] = {
            "source_sha256": music.digest(p),
            "published_sha256": music.digest(dest),
        }
    assert np.max(np.abs(total)) < 1
    music.write_audio(OUT / "afterglow-transit.wav", total, rate)
    metrics = music.inspect_audio(
        OUT / "afterglow-transit.wav", OUT / "inspection", 126
    )
    assert metrics["true_peak_dbtp"] < -1
    music.save_json(
        OUT / "manifest.json",
        {
            "version": 2,
            "title": "Afterglow Transit",
            "duration": len(total) / rate,
            "bpm": 126,
            "gain": 1,
            "tracks": tracks,
        },
    )
    music.save_json(
        ROOT / "evidence.json",
        {
            "revision": "v002",
            "gain": GAIN,
            "end_fade_seconds": 0.15,
            "master": metrics,
            "stems": sources,
            "note": "Playback and standalone file use the same sum of separately rendered stems. The independently rendered wet master is preserved.",
        },
    )
    music.save_json(
        ROOT / "sound-lab.json",
        {
            "duration": 15,
            "inputs": [
                {
                    "name": "Theme: complete mix",
                    "path": "exports/player-v002/afterglow-transit.wav",
                    "start": 15.238095,
                    "role": "mix",
                    "bpm": 126,
                },
                {
                    "name": "Return: complete mix",
                    "path": "exports/player-v002/afterglow-transit.wav",
                    "start": 45.714286,
                    "role": "mix",
                    "bpm": 126,
                },
                {
                    "name": "Return: lead melody",
                    "path": "exports/player-v002/audio/melody.wav",
                    "start": 45.714286,
                    "role": "stem",
                    "bpm": 126,
                },
                {
                    "name": "Return: warm chords",
                    "path": "exports/player-v002/audio/harmony.wav",
                    "start": 45.714286,
                    "role": "stem",
                    "bpm": 126,
                },
            ],
        },
    )
    print(
        json.dumps(
            {
                k: metrics[k]
                for k in [
                    "seconds",
                    "integrated_lufs",
                    "true_peak_dbtp",
                    "samples_at_or_above_full_scale",
                ]
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
