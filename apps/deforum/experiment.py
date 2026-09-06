"""Submit an existing Difforum graph to ComfyUI and retain frames and receipts.

Graph adapted from Difforum's MIT-licensed examples/_smoke_render_sdxl.py.
See DIFforum-LICENSE and README.md for source provenance.
"""

import argparse
import datetime
import json
import pathlib
import subprocess
import time
import urllib.error
import urllib.parse
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parent
WORKFLOW = ROOT / "workflows/sdxl-feedback.api.json"
OUTPUTS = ROOT / "outputs"
RENDER_TIMEOUT_SECONDS = 1800
DIFFORUM_COMMIT = "1d750efd3c1d1dda792b8ef6c14b06a14a69f879"
MODEL_SHA256 = "31e35c80fc4829d14f90153f4c74cd59c90b779f6afe05a74cd6120b893f7e5b"


def request(base, route, payload=None, binary=False):
    data = None if payload is None else json.dumps(payload).encode()
    req = urllib.request.Request(
        base.rstrip("/") + route, data=data,
        headers={"User-Agent": "deforum-experiment/0.1", "Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as response:
            body = response.read()
    except urllib.error.HTTPError as error:
        raise RuntimeError(f"ComfyUI {route}: HTTP {error.code}: {error.read().decode()}") from error
    return body if binary else json.loads(body)


def save_json(path, value):
    path.write_text(json.dumps(value, indent=2) + "\n")


def make_graph(denoise, frames, prefix):
    graph = json.loads(WORKFLOW.read_text())
    graph["7"]["inputs"]["max_frames"] = frames
    graph["9"]["inputs"]["schedule"] = f"0:({denoise})"
    graph["11"]["inputs"]["filename_prefix"] = prefix
    return graph


def preflight(base, graph):
    info = request(base, "/object_info")
    missing = sorted({node["class_type"] for node in graph.values()} - info.keys())
    if missing:
        raise RuntimeError(f"Missing ComfyUI nodes: {missing}")
    checkpoint = graph["1"]["inputs"]["ckpt_name"]
    choices = info["CheckpointLoaderSimple"]["input"]["required"]["ckpt_name"][0]
    if checkpoint not in choices:
        raise RuntimeError(f"Checkpoint not installed: {checkpoint}")
    return request(base, "/system_stats")


def collect(folder):
    receipt = json.loads((folder / "submission.json").read_text())
    base, prompt_id = receipt["base_url"], receipt["prompt_id"]
    deadline = time.monotonic() + RENDER_TIMEOUT_SECONDS
    while time.monotonic() < deadline:
        history = request(base, f"/history/{prompt_id}")
        if prompt_id in history:
            entry = history[prompt_id]
            save_json(folder / "history.json", entry)
            status = entry.get("status", {})
            if status.get("status_str") == "error":
                raise RuntimeError(f"Render failed; inspect {folder / 'history.json'}")
            if status.get("completed"):
                images = entry.get("outputs", {}).get("11", {}).get("images", [])
                if len(images) != receipt["frames"]:
                    raise RuntimeError(f"Expected {receipt['frames']} frames, received {len(images)}")
                break
        time.sleep(3)
    else:
        raise TimeoutError("Render wait expired; the remote job may still run. Use collect to reconnect.")

    frames_dir = folder / "frames"
    frames_dir.mkdir(exist_ok=True)
    for index, image in enumerate(images):
        query = urllib.parse.urlencode({
            "filename": image["filename"], "subfolder": image.get("subfolder", ""),
            "type": image.get("type", "output"),
        })
        data = request(base, "/view?" + query, binary=True)
        if not data.startswith(b"\x89PNG\r\n\x1a\n"):
            raise RuntimeError(f"Frame {index} was not a PNG")
        (frames_dir / f"{index:04d}.png").write_bytes(data)
    subprocess.run([
        "ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-framerate", "8",
        "-i", str(frames_dir / "%04d.png"), "-vf", "fps=24",
        "-c:v", "libx264", "-crf", "18", "-pix_fmt", "yuv420p",
        str(folder / "preview.mp4"),
    ], check=True)
    receipt["collected_at"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
    save_json(folder / "submission.json", receipt)
    print(f"Saved {len(images)} frames and {folder / 'preview.mp4'}", flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    run = commands.add_parser("run")
    run.add_argument("--url", required=True)
    run.add_argument("--denoise", type=float, choices=[0.3, 0.4, 0.5], default=0.4)
    run.add_argument("--frames", type=int, choices=[8, 40], default=40)
    resume = commands.add_parser("collect")
    resume.add_argument("folder", type=pathlib.Path)
    args = parser.parse_args()
    if args.command == "collect":
        collect(args.folder.resolve())
        return
    stamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    name = f"{stamp}-denoise-{args.denoise:.2f}-{args.frames}f"
    graph = make_graph(args.denoise, args.frames, f"deforum/{name}")
    stats = preflight(args.url, graph)
    folder = OUTPUTS / name
    folder.mkdir(parents=True, exist_ok=False)
    save_json(folder / "workflow.api.json", graph)
    save_json(folder / "system-stats.json", stats)
    # Never retry a submission automatically: a lost response can hide an accepted job.
    result = request(args.url, "/prompt", {"prompt": graph})
    save_json(folder / "submit-response.json", result)
    if result.get("node_errors") or not result.get("prompt_id"):
        raise RuntimeError(f"Workflow rejected: {result}")
    save_json(folder / "submission.json", {
        "base_url": args.url, "prompt_id": result["prompt_id"], "frames": args.frames,
        "denoise": args.denoise, "generated_fps": 8, "delivery_fps": 24,
        "difforum_commit": DIFFORUM_COMMIT, "model_sha256": MODEL_SHA256,
        "submitted_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    })
    print(f"Submitted {result['prompt_id']}; receipts: {folder}", flush=True)
    collect(folder)


if __name__ == "__main__":
    main()
