"""Local audio inspection and bounded OpenRouter listening experiments."""

import argparse
import base64
import fcntl
import hashlib
import json
import math
import os
import subprocess
import uuid
from pathlib import Path

import dotenv
import httpx
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import soundfile as sf
from scipy import signal

ROOT = Path(__file__).resolve().parent
MODEL = "google/gemini-3.1-pro-preview"
API = "https://openrouter.ai/api/v1"
MAX_SECONDS = 60
MAX_AUDIO_BYTES = 24_000_000
MAX_TOKENS = 8192
TRIAL_BUDGET_USD = 1.0
REQUEST_RESERVE_USD = 0.25
PROMPT = """Listen to the attached audio. You are reviewing an instrumental music sketch.
Describe only what you can support from the audio: rhythmic feel, prominent sound
roles, changes over time, low/high balance, stereo impression, and obvious defects.
Give timestamps in seconds for concrete observations, state uncertainty, and propose
at most two useful edits. Do not invent lyrics, exact notes, BPM, instrument identities,
or technical measurements. Distinguish observation from taste. If silent, say so.
No source code, intended style, filename, or test condition is supplied."""


def save_json(path, data):
    Path(path).write_text(json.dumps(data, indent=2, allow_nan=False) + "\n")


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read_audio(path):
    data, sr = sf.read(path, always_2d=True, dtype="float64")
    if not len(data) or not np.isfinite(data).all():
        raise ValueError("Audio must contain finite, nonempty samples")
    if data.shape[1] > 2:
        raise ValueError(
            "Export stereo or mono; multichannel orbit mapping is not supported"
        )
    return data, sr


def db(value):
    return float(20 * np.log10(value)) if value > 0 else None


def fresh_dir(path):
    path = Path(path)
    path.mkdir(parents=True, exist_ok=False)
    return path


def write_audio(path, data, sr):
    path = Path(path)
    if path.exists():
        raise FileExistsError(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    # Float WAV preserves headroom, exposing overload instead of silently clipping.
    sf.write(path, data, sr, subtype="FLOAT")


def loudness(path):
    result = subprocess.run(
        [
            "ffmpeg",
            "-nostdin",
            "-hide_banner",
            "-i",
            str(Path(path).resolve()),
            "-af",
            "loudnorm=I=-23:TP=-1:LRA=7:print_format=json",
            "-f",
            "null",
            "-",
        ],
        capture_output=True,
        text=True,
        check=True,
    )
    raw, _ = json.JSONDecoder().raw_decode(result.stderr[result.stderr.rfind("{") :])

    def finite(key):
        value = float(raw[key])
        return value if math.isfinite(value) else None

    return {
        "integrated_lufs": finite("input_i"),
        "true_peak_dbtp": finite("input_tp"),
        "loudness_range_lu": finite("input_lra"),
    }


def spectrogram(data, sr):
    n = min(4096, len(data))
    frequency, time, power = signal.spectrogram(
        data,
        fs=sr,
        nperseg=n,
        noverlap=n * 3 // 4,
        axis=0,
        scaling="spectrum",
        mode="psd",
    )
    # Average channel power, never sum L/R waveforms (which can cancel).
    return frequency, time, 10 * np.log10(np.maximum(power.mean(axis=1), 1e-12))


def inspect_audio(path, out, bpm=None):
    data, sr = read_audio(path)
    if bpm is not None and bpm <= 0:
        raise ValueError("BPM must be positive")
    out = fresh_dir(out)
    rms = np.sqrt(np.mean(data**2))
    report = {
        "source": str(Path(path).resolve()),
        "sha256": digest(path),
        "seconds": len(data) / sr,
        "sample_rate": sr,
        "channels": data.shape[1],
        "sample_peak_dbfs": db(np.max(np.abs(data))),
        "rms_dbfs": db(rms),
        "samples_at_or_above_full_scale": int(np.sum(np.abs(data) >= 1)),
        "bpm_supplied": bpm,
        **loudness(path),
    }
    if data.shape[1] == 2:
        report["lr_correlation"] = (
            float(np.corrcoef(data.T)[0, 1])
            if np.all(np.std(data, axis=0) > 1e-12)
            else None
        )
        report["mono_rms_dbfs"] = db(np.sqrt(np.mean(data.mean(axis=1) ** 2)))
    save_json(out / "metrics.json", report)
    fig, axes = plt.subplots(
        2, 1, figsize=(13, 7), constrained_layout=True, sharex=True
    )
    # Min/max envelope retains transients even on a long overview.
    hop = max(1, len(data) // 6000)
    for channel in range(data.shape[1]):
        trimmed = data[: len(data) // hop * hop, channel].reshape(-1, hop)
        t = np.arange(len(trimmed)) * hop / sr
        axes[0].fill_between(
            t,
            trimmed.min(axis=1),
            trimmed.max(axis=1),
            alpha=0.5,
            label=["L / mono", "R"][channel],
        )
    axes[0].set(ylabel="Amplitude", title=Path(path).name)
    axes[0].legend(loc="upper right")
    f, t, power_db = spectrogram(data, sr)
    mesh = axes[1].pcolormesh(
        t, f[1:], power_db[1:], shading="auto", cmap="magma", vmin=-100, vmax=0
    )
    axes[1].set(
        yscale="log",
        ylim=(20, sr / 2),
        xlabel="Time (seconds)",
        ylabel="Frequency (Hz)",
    )
    axes[1].set_yticks(
        [
            v
            for v in [30, 60, 125, 250, 500, 1000, 2000, 4000, 8000, 16000]
            if v < sr / 2
        ]
    )
    axes[1].yaxis.set_major_formatter(matplotlib.ticker.ScalarFormatter())
    fig.colorbar(mesh, ax=axes[1], label="Power (dB re digital full scale; per bin)")
    if bpm:
        for second in np.arange(0, len(data) / sr, 240 / bpm):
            for ax in axes:
                ax.axvline(second, color="gray", lw=0.5, alpha=0.35)
    fig.savefig(out / "spectrogram.png", dpi=140)
    plt.close(fig)
    return report


def excerpt(path, out, start, duration):
    data, sr = read_audio(path)
    a, b = round(start * sr), round((start + duration) * sr)
    if start < 0 or duration <= 0 or b > len(data) or b <= a:
        raise ValueError("Requested excerpt must lie inside the source")
    write_audio(out, data[a:b], sr)
    save_json(
        str(out) + ".json",
        {
            "source_sha256": digest(path),
            "start": start,
            "duration": duration,
            "output_sha256": digest(out),
        },
    )


def mix(paths, out, gain_db):
    tracks = [read_audio(p) for p in paths]
    reference, sr = tracks[0]
    if any(rate != sr or audio.shape != reference.shape for audio, rate in tracks):
        raise ValueError(
            "Stems must have identical sample rates, channels and frame counts"
        )
    audio = np.sum([track for track, _ in tracks], axis=0) * 10 ** (gain_db / 20)
    write_audio(out, audio, sr)
    save_json(
        str(out) + ".json",
        {
            "sources": [{"path": str(p), "sha256": digest(p)} for p in paths],
            "gain_db": gain_db,
            "sample_peak_dbfs": db(np.max(np.abs(audio))),
        },
    )


def match(paths, out):
    levels = [loudness(p)["integrated_lufs"] for p in paths]
    if any(level is None for level in levels):
        raise ValueError("Cannot loudness-match silent/ungated audio")
    out = fresh_dir(out)
    target = min(levels)
    records = []
    for i, (path, level) in enumerate(zip(paths, levels, strict=True)):
        data, sr = read_audio(path)
        gain = target - level
        filename = f"{i + 1:02d}-{Path(path).stem}.wav"
        write_audio(out / filename, data * 10 ** (gain / 20), sr)
        records.append(
            {"source_sha256": digest(path), "file": filename, "gain_db": gain}
        )
    save_json(
        out / "manifest.json",
        {
            "target_lufs": target,
            "copies": records,
            "method": "constant attenuation, no compression",
        },
    )


def calibration(path, out):
    data, sr = read_audio(path)
    if len(data) / sr < 12:
        raise ValueError("Calibration source must be at least 12 seconds")
    out = fresh_dir(out)
    data = data[: 20 * sr]
    variants = {"unaltered": data, "silence": np.zeros_like(data)}
    dropout = data.copy()
    dropout[8 * sr : 10 * sr] = 0
    variants["silence from 8 to 10 seconds"] = dropout
    variants["low-pass at 450 Hz"] = signal.sosfilt(
        signal.butter(8, 450, fs=sr, output="sos"), data, axis=0
    )
    answer_key = {}
    for condition, audio in variants.items():
        filename = uuid.uuid4().hex[:8] + ".wav"
        write_audio(out / filename, audio, sr)
        answer_key[filename] = condition
    save_json(out / "answer-key.json", answer_key)
    return {"clips": len(answer_key), "directory": str(out)}


def review(path, out, send=False):
    data, sr = read_audio(path)
    if len(data) / sr > MAX_SECONDS or Path(path).stat().st_size > MAX_AUDIO_BYTES:
        raise ValueError(
            "Review accepts at most 60 seconds / 24 MB per call; make an excerpt"
        )
    if Path(path).suffix.lower() != ".wav":
        raise ValueError("Review requires WAV")
    # Provider-independent PCM16 WAV, without changing sample rate or channel count.
    import io

    buffer = io.BytesIO()
    if np.max(np.abs(data)) > 1:
        raise ValueError("Audio exceeds full scale; fix the mix before review")
    sf.write(buffer, data, sr, format="WAV", subtype="PCM_16")
    payload = {
        "model": MODEL,
        "max_tokens": MAX_TOKENS,
        "reasoning": {"effort": "high"},
        "provider": {"require_parameters": True, "allow_fallbacks": False},
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": PROMPT},
                    {
                        "type": "input_audio",
                        "input_audio": {
                            "data": base64.b64encode(buffer.getvalue()).decode(),
                            "format": "wav",
                        },
                    },
                ],
            }
        ],
    }
    receipt = {
        "model": MODEL,
        "source_sha256": digest(path),
        "seconds": len(data) / sr,
        "prompt": PROMPT,
        "max_tokens": MAX_TOKENS,
        "reasoning_effort": "high",
        "request_reserve_usd": REQUEST_RESERVE_USD,
        "sent": False,
    }
    if not send:
        return receipt
    dotenv.load_dotenv(ROOT / ".env", override=False)
    key = os.environ.get("OPENROUTER_API_KEY", "").strip()
    if not key:
        raise ValueError(f"Set OPENROUTER_API_KEY in {ROOT / '.env'}")
    out = fresh_dir(out)
    work = ROOT / "work"
    work.mkdir(exist_ok=True)
    # Lock across processes; pending/failed calls retain reservations (no blind retries).
    with (work / "review-ledger.jsonl").open("a+") as ledger:
        fcntl.flock(ledger, fcntl.LOCK_EX)
        ledger.seek(0)
        reserved = sum(
            json.loads(line)["reserved_usd"] for line in ledger if line.strip()
        )
        if reserved + REQUEST_RESERVE_USD > TRIAL_BUDGET_USD:
            raise ValueError(
                "Trial reservations exhausted; review ledger before agreeing another budget"
            )
        with httpx.Client(timeout=180) as client:
            response = client.get(API + "/models")
            response.raise_for_status()
            model = next(m for m in response.json()["data"] if m["id"] == MODEL)
            if "audio" not in model["architecture"]["input_modalities"]:
                raise ValueError("Selected model no longer advertises audio input")
            # Fail on price changes instead of silently spending under stale assumptions.
            prices = model["pricing"]
            if (
                float(prices["completion"]) > 0.000012
                or float(prices["audio"]) > 0.000002
            ):
                raise ValueError(
                    "Model pricing increased; reassess trial cost before sending"
                )
            save_json(out / "model.json", model)
            ledger.write(
                json.dumps(
                    {"output": str(out.resolve()), "reserved_usd": REQUEST_RESERVE_USD}
                )
                + "\n"
            )
            ledger.flush()
            os.fsync(ledger.fileno())
            receipt.update(sent=None, status="dispatching")
            save_json(out / "request.json", receipt)
            response = client.post(
                API + "/chat/completions",
                json=payload,
                headers={"Authorization": "Bearer " + key},
            )
            receipt.update(sent=True, status="response_received")
            save_json(out / "request.json", receipt)
            # Store response privately, never the key or base64 payload.
            save_json(out / "response.json", response.json())
            response.raise_for_status()
            result = response.json()
            if result.get("error"):
                raise ValueError(
                    "Provider returned an error; inspect private response.json"
                )
            content = result["choices"][0]["message"].get("content")
            if not content:
                raise ValueError(
                    "No review text; inspect finish reason before another paid call"
                )
            (out / "review.md").write_text(content + "\n")
            receipt.update(
                sent=True,
                usage=result.get("usage"),
                id=result.get("id"),
                finish_reason=result["choices"][0].get("finish_reason"),
            )
            save_json(out / "request.json", receipt)
    return receipt


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    for name in ["inspect", "excerpt", "review", "calibration"]:
        command = sub.add_parser(name)
        command.add_argument("input", type=Path)
        command.add_argument("--out", type=Path, required=True)
        if name == "inspect":
            command.add_argument("--bpm", type=float)
        elif name == "excerpt":
            command.add_argument("--start", type=float, required=True)
            command.add_argument("--duration", type=float, required=True)
        elif name == "review":
            command.add_argument(
                "--send", action="store_true", help="Upload audio; incurs API usage"
            )
    for name in ["mix", "match"]:
        command = sub.add_parser(name)
        command.add_argument("inputs", nargs="+", type=Path)
        command.add_argument("--out", type=Path, required=True)
        if name == "mix":
            command.add_argument("--gain-db", type=float, default=0)
    args = parser.parse_args()
    if args.command == "inspect":
        result = inspect_audio(args.input, args.out, args.bpm)
    elif args.command == "excerpt":
        result = excerpt(args.input, args.out, args.start, args.duration)
    elif args.command == "mix":
        result = mix(args.inputs, args.out, args.gain_db)
    elif args.command == "match":
        result = match(args.inputs, args.out)
    elif args.command == "calibration":
        result = calibration(args.input, args.out)
    else:
        result = review(args.input, args.out, args.send)
    if result is not None:
        print(json.dumps(result, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
