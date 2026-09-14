"""ComfyUI HTTP requests and archive collection, independent of the legacy CLI."""

import datetime
import json
import subprocess
import time
import urllib.error
import urllib.parse
import urllib.request

RENDER_TIMEOUT_SECONDS = 1800


def request(base, route, payload=None, binary=False):
    data = None if payload is None else json.dumps(payload).encode()
    req = urllib.request.Request(
        base.rstrip("/") + route,
        data=data,
        headers={
            "User-Agent": "deforum-experiment/0.1",
            "Content-Type": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as response:
            body = response.read()
    except urllib.error.HTTPError as error:
        raise RuntimeError(
            f"ComfyUI {route}: HTTP {error.code}: {error.read().decode()}"
        ) from error
    return body if binary else json.loads(body)


def save_json(path, value):
    path.write_text(json.dumps(value, indent=2) + "\n")


def collect(folder):
    receipt = json.loads((folder / "submission.json").read_text())
    if receipt.get("transport") == "runpod-serverless":
        raise ValueError("Use the serverless collector for this receipt")
    if receipt.get("collected_at"):
        assets = [folder / "preview.mp4"] + [
            folder / "frames" / f"{i:04d}.png" for i in range(receipt["frames"])
        ]
        if not all(path.is_file() and path.stat().st_size for path in assets):
            raise RuntimeError(
                "Completed archive is missing assets; restore them from backup."
            )
        print(f"Already collected: {folder / 'preview.mp4'}", flush=True)
        return
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
                    raise RuntimeError(
                        f"Expected {receipt['frames']} frames, received {len(images)}"
                    )
                break
        time.sleep(3)
    else:
        raise TimeoutError(
            "Render wait expired; the remote job may still run. Use collect to reconnect."
        )

    frames_dir = folder / "frames"
    frames_dir.mkdir(exist_ok=True)
    for index, image in enumerate(images):
        target = frames_dir / f"{index:04d}.png"
        if target.exists():
            with target.open("rb") as existing:
                if existing.read(8) != b"\x89PNG\r\n\x1a\n":
                    raise RuntimeError(f"Existing frame is invalid: {target}")
            continue
        query = urllib.parse.urlencode(
            {
                "filename": image["filename"],
                "subfolder": image.get("subfolder", ""),
                "type": image.get("type", "output"),
            }
        )
        data = request(base, "/view?" + query, binary=True)
        if not data.startswith(b"\x89PNG\r\n\x1a\n"):
            raise RuntimeError(f"Frame {index} was not a PNG")
        with target.open("xb") as output:
            output.write(data)
    preview = folder / "preview.mp4"
    if not preview.exists():
        temporary = folder / "preview.encoding.mp4"
        subprocess.run(
            [
                "ffmpeg",
                "-hide_banner",
                "-loglevel",
                "error",
                "-y",
                "-framerate",
                "8",
                "-i",
                str(frames_dir / "%04d.png"),
                "-vf",
                "fps=24",
                "-c:v",
                "libx264",
                "-crf",
                "18",
                "-pix_fmt",
                "yuv420p",
                str(temporary),
            ],
            check=True,
        )
        temporary.rename(preview)
    receipt["collected_at"] = datetime.datetime.now(datetime.UTC).isoformat()
    save_json(folder / "submission.json", receipt)
    print(f"Saved {len(images)} frames and {folder / 'preview.mp4'}", flush=True)
