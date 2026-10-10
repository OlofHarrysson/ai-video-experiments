"""Strudel project rendering, audio inspection and OpenRouter listening."""

import argparse
import base64
import fcntl
import hashlib
import json
import math
import os
import subprocess
import uuid
from datetime import UTC, datetime
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
API_TIMEOUT_SECONDS = 600
CATALOG_TIMEOUT_SECONDS = 30
SILENCE_THRESHOLD_DBFS = -80
SILENCE_MIN_SECONDS = 0.1
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


def silence_intervals(data, sr):
    """Contiguous near-zero signal on every channel; rests are not necessarily defects."""
    quiet = np.max(np.abs(data), axis=1) <= 10 ** (SILENCE_THRESHOLD_DBFS / 20)
    edges = np.diff(np.r_[False, quiet, False].astype(int))
    return [
        {"start_seconds": int(start) / sr, "end_seconds": int(end) / sr}
        for start, end in zip(
            np.flatnonzero(edges == 1), np.flatnonzero(edges == -1), strict=True
        )
        if end - start >= sr * SILENCE_MIN_SECONDS
    ]


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


def pcm_rail_metrics(data, subtype):
    """Count representable integer limits; positive PCM full scale is below 1.0."""
    bits = {"PCM_U8": 8, "PCM_S8": 8, "PCM_16": 16, "PCM_24": 24, "PCM_32": 32}.get(
        subtype
    )
    if bits is None:
        return {
            "sample_format": subtype,
            "pcm_rail_samples": None,
            "pcm_rail_longest_run_frames": None,
        }
    positive_limit = 1 - 2 ** (1 - bits)
    rail = (data >= positive_limit) | (data <= -1)
    longest = 0
    for channel in rail.T:
        edges = np.diff(np.r_[False, channel, False].astype(int))
        runs = np.flatnonzero(edges == -1) - np.flatnonzero(edges == 1)
        longest = max(longest, int(runs.max(initial=0)))
    return {
        "sample_format": subtype,
        "pcm_rail_samples": int(rail.sum()),
        "pcm_rail_longest_run_frames": longest,
    }


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
        **pcm_rail_metrics(data, sf.info(path).subtype),
        "bpm_supplied": bpm,
        "silence_threshold_dbfs": SILENCE_THRESHOLD_DBFS,
        "silence_min_seconds": SILENCE_MIN_SECONDS,
        "silence_intervals": silence_intervals(data, sr),
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


def compare(reference, candidate, out):
    """Compare samples without aligning, normalizing or altering either input."""
    original, sr = read_audio(reference)
    other, other_sr = read_audio(candidate)
    if sr != other_sr or original.shape != other.shape:
        raise ValueError(
            "Comparison requires identical sample rates, channels and frame counts"
        )
    residual = other - original
    rms = np.sqrt(np.mean(residual**2))
    original_rms = np.sqrt(np.mean(original**2))
    report = {
        "reference": {"path": str(reference), "sha256": digest(reference)},
        "candidate": {"path": str(candidate), "sha256": digest(candidate)},
        "sample_rate": sr,
        "frames": len(original),
        "channels": original.shape[1],
        "identical_samples": bool(np.array_equal(original, other)),
        "residual_peak_dbfs": db(np.max(np.abs(residual))),
        "residual_rms_dbfs": db(rms),
        "residual_relative_db": db(rms / original_rms) if original_rms else None,
        "method": "candidate minus reference, no alignment or gain adjustment",
    }
    out = fresh_dir(out)
    write_audio(out / "residual.wav", residual, sr)
    save_json(out / "comparison.json", report)
    return report


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


def append_review_event(work, event):
    """Keep each ledger append durable without serializing provider requests."""
    with (work / "review-ledger.jsonl").open("a") as ledger:
        fcntl.flock(ledger, fcntl.LOCK_EX)
        ledger.write(json.dumps(event) + "\n")
        ledger.flush()
        os.fsync(ledger.fileno())


def review(path, out, send=False, prompt=PROMPT, model_id=MODEL, provider=None):
    data, sr = read_audio(path)
    if len(data) / sr > MAX_SECONDS or Path(path).stat().st_size > MAX_AUDIO_BYTES:
        raise ValueError(
            "Review accepts at most 60 seconds / 24 MB per call; make an excerpt"
        )
    if Path(path).suffix.lower() != ".wav":
        raise ValueError("Review requires WAV")
    if not prompt.strip():
        raise ValueError("Review prompt must not be empty")
    # Provider-independent PCM16 WAV, without changing sample rate or channel count.
    import io

    buffer = io.BytesIO()
    if np.max(np.abs(data)) > 1:
        raise ValueError("Audio exceeds full scale; fix the mix before review")
    sf.write(buffer, data, sr, format="WAV", subtype="PCM_16")
    payload = {
        "model": model_id,
        "max_tokens": MAX_TOKENS,
        "provider": {"require_parameters": True, "allow_fallbacks": False},
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
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
    if provider:
        payload["provider"]["only"] = [provider]
    receipt = {
        "model": model_id,
        "provider_requested": provider,
        "source_sha256": digest(path),
        "submitted_audio": {
            "sha256": hashlib.sha256(buffer.getvalue()).hexdigest(),
            "bytes": len(buffer.getvalue()),
            "format": "PCM_16 WAV",
            "sample_rate": sr,
            "channels": data.shape[1],
            "frames": len(data),
        },
        "seconds": len(data) / sr,
        "prompt": prompt,
        "max_tokens": MAX_TOKENS,
        "reasoning_effort": "high_if_supported",
        "sent": False,
        "created_at": datetime.now(UTC).isoformat(),
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
    receipt.update(status="preflight", request_id=str(uuid.uuid4()))
    save_json(out / "request.json", receipt)
    with httpx.Client(timeout=API_TIMEOUT_SECONDS) as client:
        try:
            response = client.get(API + "/models", timeout=CATALOG_TIMEOUT_SECONDS)
            response.raise_for_status()
            model = next(
                (m for m in response.json()["data"] if m["id"] == model_id), None
            )
            if model is None:
                raise ValueError(
                    f"Model is absent from the current catalog: {model_id}"
                )
            if "audio" not in model["architecture"]["input_modalities"]:
                raise ValueError("Selected model no longer advertises audio input")
            parameters = model.get("supported_parameters")
            if not isinstance(parameters, list):
                raise TypeError("Model catalog does not declare supported parameters")
            if "reasoning" in parameters:
                payload["reasoning"] = {"effort": "high"}
                receipt["reasoning_effort"] = "high"
            else:
                receipt["reasoning_effort"] = None
            save_json(out / "model.json", model)
        except Exception as error:
            receipt.update(
                status="preflight_error",
                error_type=type(error).__name__,
                finished_at=datetime.now(UTC).isoformat(),
            )
            save_json(out / "request.json", receipt)
            append_review_event(work, {"output": str(out.resolve()), **receipt})
            raise
        receipt.update(
            sent=None, status="dispatching", dispatch_at=datetime.now(UTC).isoformat()
        )
        save_json(out / "request.json", receipt)
        append_review_event(
            work,
            {
                "output": str(out.resolve()),
                "event": "dispatching",
                "request_id": receipt["request_id"],
            },
        )
        try:
            response = client.post(
                API + "/chat/completions",
                json=payload,
                headers={"Authorization": "Bearer " + key},
            )
        except httpx.RequestError as error:
            receipt.update(
                status="transport_error",
                error_type=type(error).__name__,
                finished_at=datetime.now(UTC).isoformat(),
            )
            save_json(out / "request.json", receipt)
            append_review_event(work, {"output": str(out.resolve()), **receipt})
            raise
        receipt.update(
            sent=True,
            status="response_received",
            finished_at=datetime.now(UTC).isoformat(),
        )
        save_json(out / "request.json", receipt)
        # Store response privately, never the key or base64 payload.
        try:
            result = response.json()
        except ValueError:
            receipt.update(status="invalid_response", http_status=response.status_code)
            save_json(out / "request.json", receipt)
            (out / "response.txt").write_text(response.text)
            append_review_event(work, {"output": str(out.resolve()), **receipt})
            raise ValueError("Non-JSON provider response; inspect private response.txt")
        save_json(out / "response.json", result)
        choices = result.get("choices") or []
        choice = choices[0] if choices else {}
        content = choice.get("message", {}).get("content")
        receipt.update(
            provider=result.get("provider"),
            usage=result.get("usage"),
            id=result.get("id"),
            finish_reason=choice.get("finish_reason"),
        )
        complete = (
            not response.is_error
            and not result.get("error")
            and isinstance(content, str)
            and bool(content.strip())
            and receipt["finish_reason"] == "stop"
        )
        receipt["status"] = "complete" if complete else "incomplete"
        save_json(out / "request.json", receipt)
        append_review_event(work, {"output": str(out.resolve()), **receipt})
        if isinstance(content, str) and content:
            filename = "review.md" if complete else "review-incomplete.md"
            (out / filename).write_text(content + "\n")
        response.raise_for_status()
        if not complete:
            raise ValueError(
                "Incomplete review; inspect private response.json and request.json"
            )

    return receipt


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    command = sub.add_parser(
        "assemble", help="Assemble named Strudel modules into a saved project"
    )
    command.add_argument("manifest", type=Path)
    command.add_argument("--out", type=Path, required=True)
    command = sub.add_parser(
        "analyze-project", help="Measure stem levels by time window and frequency band"
    )
    command.add_argument("run", type=Path)
    command.add_argument("--out", type=Path, required=True)
    command.add_argument("--window-cycles", type=float, default=1)
    command = sub.add_parser(
        "audition", help="Make an anonymous, loudness-matched audio pair"
    )
    command.add_argument("first", type=Path)
    command.add_argument("second", type=Path)
    command.add_argument("--out", type=Path, required=True)
    command.add_argument("--start-first", type=float, default=0)
    command.add_argument("--start-second", type=float, default=0)
    command.add_argument("--duration", type=float, default=28)
    command.add_argument("--gap", type=float, default=2)
    command = sub.add_parser(
        "render-project", help="Render and inspect a saved project master and stems"
    )
    command.add_argument("project", type=Path)
    command.add_argument("--revision", required=True)
    command.add_argument("--out", type=Path, required=True)
    command.add_argument("--timeout", type=float, default=120)
    for operation in ["preview", "compare-revisions"]:
        command = sub.add_parser(
            operation,
            help={
                "preview": "Extract a section from a completed master or stem",
                "compare-revisions": "Create labelled, loudness-matched section comparisons",
            }[operation],
        )
        if operation == "preview":
            command.add_argument("run", type=Path)
        else:
            command.add_argument("reference", type=Path)
            command.add_argument("candidate", type=Path)
        command.add_argument("--section", required=True)
        command.add_argument("--stem", default="master")
        command.add_argument(
            "--lead", type=float, default=0, help="Seconds of preceding context"
        )
        command.add_argument(
            "--tail", type=float, default=0, help="Seconds of following context"
        )
        command.add_argument("--out", type=Path, required=True)
    command = sub.add_parser(
        "render", help="Render trusted Strudel source in a fresh headless Chrome"
    )
    command.add_argument("input", type=Path)
    command.add_argument("--out", type=Path, required=True)
    command.add_argument("--begin", type=float, default=0)
    command.add_argument("--end", type=float, required=True)
    command.add_argument("--sample-rate", type=int, default=48000)
    command.add_argument("--samples", type=Path, action="append", default=[])
    command.add_argument(
        "--solo",
        action="append",
        default=[],
        help="Named source layer; repeat to group",
    )
    command.add_argument("--timeout", type=float, default=120)
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
                "--provider", help="Explicit OpenRouter provider name; no fallback"
            )
            command.add_argument(
                "--model",
                default=MODEL,
                help="Explicit OpenRouter audio-model ID; no fallback",
            )
            command.add_argument(
                "--prompt-file",
                type=Path,
                help="A focused listening question; saved in the receipt",
            )
            command.add_argument(
                "--send", action="store_true", help="Upload audio; incurs API usage"
            )
    for name in ["mix", "match"]:
        command = sub.add_parser(name)
        command.add_argument("inputs", nargs="+", type=Path)
        command.add_argument("--out", type=Path, required=True)
        if name == "mix":
            command.add_argument("--gain-db", type=float, default=0)
    command = sub.add_parser("compare")
    command.add_argument("reference", type=Path)
    command.add_argument("candidate", type=Path)
    command.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    if args.command == "audition":
        import audition

        result = audition.make_audition(
            args.first,
            args.second,
            args.out,
            args.start_first,
            args.start_second,
            args.duration,
            args.gap,
        )
    elif args.command == "analyze-project":
        import analysis

        result = analysis.analyze_project(args.run, args.out, args.window_cycles)
    elif args.command == "assemble":
        completed = subprocess.run(
            [
                "node",
                str(ROOT / "renderer/assemble.mjs"),
                str(args.manifest),
                "--out",
                str(args.out),
            ],
            check=False,
        )
        if completed.returncode:
            raise SystemExit(completed.returncode)
        return
    elif args.command in {"render-project", "preview", "compare-revisions"}:
        import workflow

        if args.command == "render-project":
            result = workflow.render_project(
                args.project, args.revision, args.out, args.timeout
            )
        elif args.command == "preview":
            result = workflow.preview(
                args.run, args.section, args.out, args.lead, args.tail, args.stem
            )
        else:
            result = workflow.compare_revisions(
                args.reference,
                args.candidate,
                args.section,
                args.out,
                args.lead,
                args.tail,
                args.stem,
            )
    elif args.command == "render":
        command = [
            "node",
            str(ROOT / "renderer/render.mjs"),
            str(args.input),
            "--out",
            str(args.out),
            "--begin",
            str(args.begin),
            "--end",
            str(args.end),
            "--sample-rate",
            str(args.sample_rate),
            "--timeout",
            str(args.timeout),
        ]
        for folder in args.samples:
            command.extend(["--samples", str(folder)])
        for label in args.solo:
            command.extend(["--solo", label])
        completed = subprocess.run(command, check=False)
        if completed.returncode:
            raise SystemExit(completed.returncode)
        return
    elif args.command == "inspect":
        result = inspect_audio(args.input, args.out, args.bpm)
    elif args.command == "excerpt":
        result = excerpt(args.input, args.out, args.start, args.duration)
    elif args.command == "mix":
        result = mix(args.inputs, args.out, args.gain_db)
    elif args.command == "match":
        result = match(args.inputs, args.out)
    elif args.command == "calibration":
        result = calibration(args.input, args.out)
    elif args.command == "compare":
        result = compare(args.reference, args.candidate, args.out)
    else:
        prompt = args.prompt_file.read_text() if args.prompt_file else PROMPT
        result = review(
            args.input, args.out, args.send, prompt, args.model, args.provider
        )
    if result is not None:
        print(json.dumps(result, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
