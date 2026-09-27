# /// script
# requires-python = ">=3.12"
# dependencies = ["numpy>=2", "pillow>=11"]
# ///
"""Eight-image Krea depth-placement study; prepare, submit once, collect, review."""
import argparse
import hashlib
import json
import shutil
import subprocess
import time
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

PROJECT = Path(__file__).resolve().parent
SIZE, RADIUS, CY = 1024, 180, 512
POSITIONS = {"left": 256, "centre": 512, "right": 768}
SEEDS = (21001, 21101)
PROMPT = (
    "A single whole round watermelon, its entire spherical green rind visible, "
    "with natural dark green winding stripes and fine realistic surface texture. "
    "The watermelon is isolated against a plain dark charcoal studio background. "
    "Soft warm studio lighting from the upper left reveals its rounded volume. "
    "A richly detailed painterly still life with subtle brushwork. "
    "Only one watermelon, no other objects, no cut fruit, no text."
)


def write(path, value):
    path.write_text(json.dumps(value, indent=2) + "\n")


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def request(base, route, payload=None, binary=False):
    body = None if payload is None else json.dumps(payload).encode()
    req = urllib.request.Request(base + route, data=body, headers={"Content-Type": "application/json", "User-Agent": "deforum-experiment/0.1"})
    with urllib.request.urlopen(req, timeout=60) as response:
        data = response.read()
    return data if binary else json.loads(data)


def prepare(folder):
    folder.mkdir(parents=True, exist_ok=False)
    shutil.copyfile(__file__, folder / "runner.py")
    yy, xx = np.mgrid[:SIZE, :SIZE]
    guides = {}
    for label, cx in POSITIONS.items():
        rr = ((xx - cx) ** 2 + (yy - CY) ** 2) / RADIUS**2
        depth = 4 - np.sqrt(np.maximum(0, 1 - rr))
        inv = np.where(rr <= 1, (1 / depth - 1 / 8) / (1 / 3 - 1 / 8), 0)
        path = folder / f"guide-{label}.png"
        Image.fromarray(np.rint(inv * 255).astype(np.uint8)).convert("RGB").save(path)
        mask = folder / f"silhouette-{label}.png"
        Image.fromarray(np.uint8(rr <= 1) * 255).save(mask)
        guides[label] = {"centre": [cx, CY], "radius": RADIUS, "sha256": sha(path)}
    write(folder / "design.json", {"size": SIZE, "prompt": PROMPT, "seeds": SEEDS,
          "guides": guides, "steps": 8, "cfg": 1, "sampler": "euler", "scheduler": "simple",
          "depth_formula": "((1/(4-sqrt(1-r_squared)))-1/8)/(1/3-1/8), r_squared<=1; else 0"})
    print(folder, flush=True)


def graph(label, seed, prefix, guide_name):
    nodes = {}
    def add(kind, **inputs):
        key = str(len(nodes) + 1)
        nodes[key] = {"class_type": kind, "inputs": inputs}
        return [key, 0]
    model = add("UNETLoader", unet_name="krea2_turbo_fp8_scaled.safetensors", weight_dtype="default")
    clip = add("CLIPLoader", clip_name="qwen3vl_4b_fp8_scaled.safetensors", type="krea2", device="default")
    vae = add("VAELoader", vae_name="qwen_image_vae.safetensors")
    positive = add("CLIPTextEncode", clip=clip, text=PROMPT)
    negative = add("ConditioningZeroOut", conditioning=positive)
    latent = add("EmptyLatentImage", width=SIZE, height=SIZE, batch_size=1)
    if label != "baseline":
        model = add("Krea2ControlLoRALoader", model=model, lora_name="watermelon-depth-control-lora.safetensors", strength=1.0)
        guide = add("LoadImage", image=guide_name)
        control = add("Krea2ControlImageEncode", control_image=guide, vae=vae, latent=latent,
                      resize="match_latent_size", upscale_method="lanczos", crop="disabled",
                      channel_mode="grayscale", normalize="per_image_minmax", invert=False,
                      batch_mode="independent_images")
        model = add("Krea2ControlApply", model=model, control_latent=control)
    sampled = add("KSampler", model=model, positive=positive, negative=negative, latent_image=latent,
                  seed=seed, steps=8, cfg=1.0, sampler_name="euler", scheduler="simple", denoise=1.0)
    image = add("VAEDecode", samples=sampled, vae=vae)
    add("SaveImage", images=image, filename_prefix=prefix)
    return nodes


def ssh(deployment, command):
    return subprocess.check_output(["ssh", "-i", deployment["ssh_identity"], "-p", str(deployment["ssh_port"]),
                                   "root@" + deployment["ssh_host"], command], text=True)


def run(folder, deployment):
    if deployment.get("status") == "deleted":
        raise RuntimeError("Deployment is closed")
    base = deployment["base_url"]
    write(folder / "system-stats.json", request(base, "/system_stats"))
    schema = request(base, "/object_info")
    write(folder / "node-schemas.json", schema)
    for label in POSITIONS:
        path = folder / f"guide-{label}.png"
        remote_name = f"watermelon-{folder.name}-{label}.png"
        remote = deployment["remote_input_dir"] + "/" + remote_name
        subprocess.run(["scp", "-q", "-i", deployment["ssh_identity"], "-P", str(deployment["ssh_port"]),
                        str(path), "root@" + deployment["ssh_host"] + ":" + remote], check=True)
        assert ssh(deployment, "sha256sum " + remote).split()[0] == sha(path)
    for seed in SEEDS:
        for label in ("baseline", *POSITIONS):
            job = folder / f"{seed}-{label}"
            if (job / "verified.json").exists():
                continue
            job.mkdir(exist_ok=True)
            prefix = f"watermelon-depth/{folder.name}/{seed}-{label}"
            guide_name = f"watermelon-{folder.name}-{label}.png"
            g = graph(label, seed, prefix, guide_name)
            assert all(n["class_type"] in schema for n in g.values()), "Required nodes missing"
            if (job / "workflow.api.json").exists():
                assert json.loads((job / "workflow.api.json").read_text()) == g, "Preserve submitted graph"
            write(job / "workflow.api.json", g)
            submission = job / "submission.json"
            if not submission.exists():
                if (job / "submitting.json").exists():
                    raise RuntimeError("Ambiguous submission: inspect queue/history before resubmitting")
                write(job / "submitting.json", {"at": datetime.now(timezone.utc).isoformat()})
                response = request(base, "/prompt", {"prompt": g, "client_id": folder.name})
                write(submission, response)
            response = json.loads(submission.read_text())
            if response.get("node_errors") or not response.get("prompt_id"):
                raise RuntimeError(response)
            prompt_id = response["prompt_id"]
            print(f"Waiting for {seed}-{label}: {prompt_id}", flush=True)
            deadline = time.monotonic() + 900
            while time.monotonic() < deadline:
                history = request(base, "/history/" + prompt_id)
                if prompt_id in history:
                    entry = history[prompt_id]
                    write(job / "history.json", entry)
                    if entry.get("status", {}).get("status_str") == "error":
                        raise RuntimeError(f"Generation failed: {job / 'history.json'}")
                    if entry.get("status", {}).get("completed"):
                        break
                time.sleep(3)
            else:
                raise TimeoutError(f"Job may still run: {prompt_id}")
            images = [im for out in entry["outputs"].values() for im in out.get("images", [])]
            assert len(images) == 1, images
            im = images[0]
            data = request(base, "/view?" + urllib.parse.urlencode(im), binary=True)
            output = job / "image.png"
            output.write_bytes(data)
            with Image.open(output) as decoded:
                decoded.load()
                assert decoded.size == (SIZE, SIZE)
            remote = deployment["remote_output_dir"] + "/" + im["subfolder"] + "/" + im["filename"]
            digest = sha(output)
            assert ssh(deployment, "sha256sum " + remote).split()[0] == digest
            write(job / "verified.json", {"sha256": digest, "remote": remote, "prompt_id": prompt_id})
            print(f"Verified {seed}-{label}", flush=True)
    write(folder / "queue-after.json", request(base, "/queue"))


def review(folder):
    assert all((folder / f"{seed}-{label}" / "verified.json").exists()
               for seed in SEEDS for label in ("baseline", *POSITIONS)), "Collect all eight images before review"
    export = PROJECT / "exports" / folder.name
    export.mkdir(parents=True, exist_ok=True)
    tile, header = 384, 35
    font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 20)
    sheet = Image.new("RGB", (tile * 4, (tile + header) * 3), "#202020")
    draw = ImageDraw.Draw(sheet)
    labels = ("baseline", *POSITIONS)
    for row in range(3):
        for col, label in enumerate(labels):
            x, y = col * tile, row * (tile + header)
            title = ("No guide" if label == "baseline" else label.title()) if row == 0 else f"Seed {SEEDS[row-1]} / {label}"
            draw.text((x + 10, y + 8), title, fill="white", font=font)
            path = folder / f"guide-{label}.png" if row == 0 else folder / f"{SEEDS[row-1]}-{label}" / "image.png"
            if path.exists():
                image = Image.open(path).convert("RGB").resize((tile, tile), Image.Resampling.LANCZOS)
                sheet.paste(image, (x, y + header))
    sheet.save(export / "comparison.jpg", quality=95)
    for seed in SEEDS:
        overlay = Image.new("RGB", (tile * 3, tile + header), "#202020")
        for col, (label, cx) in enumerate(POSITIONS.items()):
            image = Image.open(folder / f"{seed}-{label}" / "image.png").convert("RGB")
            d = ImageDraw.Draw(image)
            d.ellipse((cx-RADIUS, CY-RADIUS, cx+RADIUS, CY+RADIUS), outline="#ff52c8", width=3)
            d.line((cx-12,CY,cx+12,CY),fill="#ff52c8",width=3)
            d.line((cx,CY-12,cx,CY+12),fill="#ff52c8",width=3)
            overlay.paste(image.resize((tile,tile),Image.Resampling.LANCZOS),(col*tile,header))
            ImageDraw.Draw(overlay).text((col*tile+10,8),f"{label.title()} / target outline",font=font,fill="white")
        overlay.save(export / f"overlay-{seed}.jpg",quality=95)
    print(export, flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=["prepare", "run", "review"])
    parser.add_argument("--folder", type=Path, required=True)
    parser.add_argument("--deployment", type=Path)
    args = parser.parse_args()
    if args.action == "prepare":
        prepare(args.folder)
    elif args.action == "review":
        review(args.folder)
    else:
        if not args.deployment:
            parser.error("run requires --deployment")
        run(args.folder, json.loads(args.deployment.read_text()))
