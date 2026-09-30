"""Mix preserved audio against a finished video; never regenerate its picture."""

import argparse
import json
import math
import subprocess
from pathlib import Path

from deforum_lab.records import read, require, save, sha


def run(args):
    result = subprocess.run(args, capture_output=True, text=True, check=False)
    require(result.returncode == 0, result.stderr[-6000:])
    return result


def probe(path):
    return json.loads(
        run(
            [
                "ffprobe",
                "-v",
                "error",
                "-show_streams",
                "-show_format",
                "-of",
                "json",
                str(path),
            ]
        ).stdout
    )


def measure(path):
    result = run(
        [
            "ffmpeg",
            "-hide_banner",
            "-nostdin",
            "-i",
            str(path),
            "-map",
            "0:a:0",
            "-af",
            "loudnorm=I=-18:TP=-2:LRA=11:print_format=json",
            "-f",
            "null",
            "-",
        ]
    )
    return json.JSONDecoder().raw_decode(result.stderr[result.stderr.rfind("{") :])[0]


def video_hash(path):
    return run(
        [
            "ffmpeg",
            "-v",
            "error",
            "-nostdin",
            "-i",
            str(path),
            "-map",
            "0:v:0",
            "-c:v",
            "copy",
            "-f",
            "hash",
            "-hash",
            "sha256",
            "-",
        ]
    ).stdout.strip()


def render(plan_path, output):
    plan_path, output = Path(plan_path).resolve(), Path(output).resolve()
    plan = read(plan_path)
    video = (plan_path.parent / plan["video"]).resolve()
    info = probe(video)
    require(
        not any(s["codec_type"] == "audio" for s in info["streams"]),
        "Source has audio: explicitly include its extracted audio in the plan and use a silent picture copy",
    )
    stream = next(s for s in info["streams"] if s["codec_type"] == "video")
    require(abs(float(stream.get("start_time", 0))) < 0.001, "Use a zero-start video")
    duration = float(stream["duration"])
    require(plan["tracks"], "Plan requires audio tracks")
    source_hash = sha(video)
    inputs = ["ffmpeg", "-hide_banner", "-nostdin", "-n"]
    filters, records = [], []
    for i, track in enumerate(plan["tracks"]):
        path = (plan_path.parent / track["path"]).resolve()
        start = float(track.get("start", 0))
        length = float(track["duration"])
        fade_in = float(track.get("fade_in", 0.2))
        fade_out = float(track.get("fade_out", 1))
        target = float(track["target_lufs"])
        require(
            all(math.isfinite(n) for n in [start, length, fade_in, fade_out, target]),
            "Track settings must be finite",
        )
        require(
            start >= 0 and length > 0 and start + length <= duration + 0.001,
            "Track extends beyond video",
        )
        require(
            0 <= fade_in <= length and 0 <= fade_out <= length, "Invalid fade duration"
        )
        require(
            float(probe(path)["format"]["duration"]) >= length - 0.1,
            f"Audio is shorter than its planned range: {path}",
        )
        stats = measure(path)
        loudness = float(stats["input_i"])
        require(math.isfinite(loudness), f"No measurable audio in {path}")
        gain = target - loudness
        inputs.extend(["-i", str(path)])
        filters.append(
            f"[{i}:a]aresample=48000,aformat=channel_layouts=stereo,"
            f"atrim=duration={length},asetpts=PTS-STARTPTS,volume={gain}dB,"
            f"afade=t=in:st=0:d={fade_in},"
            f"afade=t=out:st={length - fade_out}:d={fade_out},"
            f"adelay={round(start * 48000)}S:all=1[t{i}]"
        )
        records.append(
            {
                "path": str(path),
                "sha256": sha(path),
                "settings": track,
                "analysis": stats,
                "gain_db": gain,
            }
        )
    labels = "".join(f"[t{i}]" for i in range(len(records)))
    filters.append(
        f"{labels}amix=inputs={len(records)}:normalize=0:dropout_transition=0,"
        f"apad,atrim=duration={duration}[mix]"
    )
    output.mkdir(parents=True, exist_ok=False)
    save(output / "plan.json", plan)
    premaster, master, preview = (
        output / n for n in ["premaster.wav", "master.wav", "preview.mp4"]
    )
    run(
        inputs
        + [
            "-filter_complex",
            ";".join(filters),
            "-map",
            "[mix]",
            "-c:a",
            "pcm_f32le",
            str(premaster),
        ]
    )
    measured = measure(premaster)
    normalization = (
        "loudnorm=I=-18:TP=-2:LRA=11:linear=true:"
        f"measured_I={measured['input_i']}:measured_TP={measured['input_tp']}:"
        f"measured_LRA={measured['input_lra']}:measured_thresh={measured['input_thresh']}:"
        f"offset={measured['target_offset']}"
    )
    run(
        [
            "ffmpeg",
            "-hide_banner",
            "-nostdin",
            "-n",
            "-i",
            str(premaster),
            "-af",
            normalization,
            "-ar",
            "48000",
            "-c:a",
            "pcm_s24le",
            str(master),
        ]
    )
    run(
        [
            "ffmpeg",
            "-hide_banner",
            "-nostdin",
            "-n",
            "-i",
            str(video),
            "-i",
            str(master),
            "-map",
            "0:v:0",
            "-map",
            "1:a:0",
            "-c:v",
            "copy",
            "-c:a",
            "aac",
            "-b:a",
            "256k",
            "-t",
            str(duration),
            "-movflags",
            "+faststart",
            str(preview),
        ]
    )
    run(["ffmpeg", "-v", "error", "-nostdin", "-i", str(preview), "-f", "null", "-"])
    original_packets, output_packets = video_hash(video), video_hash(preview)
    require(original_packets == output_packets, "Video packets changed")
    require(sha(video) == source_hash, "Source file changed")
    final_probe, final_audio = probe(preview), measure(preview)
    require(
        abs(float(final_probe["format"]["duration"]) - duration) < 0.05,
        "Export duration differs",
    )
    require(float(final_audio["input_tp"]) < -1, "Encoded audio peak exceeds -1 dBTP")
    receipt = {
        "source": str(video),
        "source_sha256": source_hash,
        "duration": duration,
        "plan_path": str(plan_path),
        "plan_sha256": sha(plan_path),
        "tracks": records,
        "premaster_analysis": measured,
        "normalization": normalization,
        "final_audio_analysis": final_audio,
        "video_packet_hash": output_packets,
        "video_packets_unchanged": True,
        "full_decode_passed": True,
        "outputs": {
            p.name: {"path": str(p), "sha256": sha(p), "bytes": p.stat().st_size}
            for p in [premaster, master, preview]
        },
        "listening_review": "Not performed by this tool; measurements do not establish artistic fit or absence of vocals",
    }
    save(output / "receipt.json", receipt)
    return {
        "preview": str(preview),
        "duration": duration,
        "audio": final_audio,
        "video_packets_unchanged": True,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("plan", type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    args = parser.parse_args()
    print(json.dumps(render(args.plan, args.output_dir), indent=2))


if __name__ == "__main__":
    main()
