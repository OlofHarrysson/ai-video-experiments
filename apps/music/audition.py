"""Anonymous, level-matched audio pairs with a private reproducible answer key."""

import secrets
from pathlib import Path

import numpy as np

import music


def make_audition(
    first, second, out, start_first=0, start_second=0, duration=28, gap=2
):
    if not all(np.isfinite(x) for x in [start_first, start_second, duration, gap]):
        raise ValueError("Audition times must be finite")
    if (
        min(start_first, start_second, gap) < 0
        or duration <= 0
        or 2 * duration + gap > 60
    ):
        raise ValueError(
            "Require nonnegative starts/gap, positive duration and at most 60 seconds total"
        )
    paths = [Path(first).resolve(), Path(second).resolve()]
    inputs = [music.read_audio(p) for p in paths]
    rate = inputs[0][1]
    if inputs[1][1] != rate or inputs[0][0].shape[1] != inputs[1][0].shape[1]:
        raise ValueError("Audition sources must have the same sample rate and channels")
    frames = round(duration * rate)
    if frames < 1:
        raise ValueError("Duration must contain at least one frame")
    excerpts = []
    for (data, _), start in zip(inputs, [start_first, start_second], strict=True):
        offset = round(start * rate)
        if offset + frames > len(data):
            raise ValueError("Audition window exceeds source; no padding or truncation")
        excerpts.append(data[offset : offset + frames])
    out = music.fresh_dir(out)
    order = [0, 1] if secrets.randbelow(2) == 0 else [1, 0]
    sources = []
    for i, data in enumerate(excerpts):
        path = out / f"source-{i + 1}.wav"
        music.write_audio(path, data, rate)
        sources.append(path)
    music.match(sources, out / "matched")
    import json

    matching = json.loads((out / "matched/manifest.json").read_text())
    matched = [
        music.read_audio(out / "matched" / record["file"])[0]
        for record in matching["copies"]
    ]
    silence = np.zeros((round(gap * rate), matched[0].shape[1]))
    combined = np.concatenate([matched[order[0]], silence, matched[order[1]]])
    audio = out / "audition.wav"
    music.write_audio(audio, combined, rate)
    first_end = frames / rate
    second_start = (frames + len(silence)) / rate
    prompt = (
        f"Compare two audio excerpts: A at 0–{first_end:g} seconds, B at {second_start:g}–{len(combined) / rate:g} seconds, separated by silence. "
        "They are loudness-matched and may be identical. Describe concrete differences in rhythmic detail, bass/drum interaction, foreground identity, transformation and use of space. "
        "Which changes are actually audible, and which passage has a clearer identity? Do not assume that busier, brighter, wider or louder is better. "
        "Explicitly say if you cannot distinguish them; do not invent differences, guess artists or production chains. Keep under 300 words."
    )
    (out / "prompt.txt").write_text(prompt + "\n")
    key = {
        "status": "complete",
        "source_windows": [
            {
                "path": str(path),
                "sha256": music.digest(path),
                "start_seconds": start,
                "duration_seconds": first_end,
            }
            for path, start in zip(paths, [start_first, start_second], strict=True)
        ],
        "order": {
            label: index + 1 for label, index in zip(["A", "B"], order, strict=True)
        },
        "input_excerpts_identical": bool(np.array_equal(excerpts[0], excerpts[1])),
        "target_lufs": matching["target_lufs"],
        "matching": matching["copies"],
        "audio_sha256": music.digest(audio),
        "duration_seconds": len(combined) / rate,
        "gap_seconds": len(silence) / rate,
        "order_method": "secrets.randbelow; assignment retained here, not in listening prompt",
    }
    music.save_json(out / "answer-key.json", key)
    return {
        "status": "complete",
        "audio": str(audio.resolve()),
        "prompt": str((out / "prompt.txt").resolve()),
        "seconds": len(combined) / rate,
    }
