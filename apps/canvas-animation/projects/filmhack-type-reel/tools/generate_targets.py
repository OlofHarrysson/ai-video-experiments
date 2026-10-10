# /// script
# dependencies = []
# ///
"""Generate keyframe visual targets through OpenRouter's images endpoint, with a spend guard.

usage: generate_targets.py <prompts.json> <out_dir> [--limit-usd 3.0] [--only k1-yes,k2-marquee] [--models a,b] [--vector]
Reads OPENROUTER_API_KEY from the environment or apps/music/.env. Never overwrites outputs.
"""
import argparse, base64, hashlib, json, os, sys, time, urllib.request, urllib.error
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from threading import Lock

ENDPOINT = "https://openrouter.ai/api/v1/images"
ENV_FILE = Path(__file__).resolve().parents[4] / "music" / ".env"
WORST_CASE_USD = {"openai/gpt-image-2.5-sunburst": 0.30, "google/gemini-nano-banana-2.1": 0.10,
                  "recraft/recraft-v4.1-pro-vector": 0.30}

ap = argparse.ArgumentParser()
ap.add_argument("prompts"); ap.add_argument("out")
ap.add_argument("--limit-usd", type=float, default=3.0)
ap.add_argument("--only", default=""); ap.add_argument("--models", default=""); ap.add_argument("--vector", action="store_true")
args = ap.parse_args()

key = os.environ.get("OPENROUTER_API_KEY")
if not key and ENV_FILE.exists():
    for line in ENV_FILE.read_text().splitlines():
        if line.startswith("OPENROUTER_API_KEY="): key = line.split("=", 1)[1].strip()
if not key: sys.exit("OPENROUTER_API_KEY not found")

spec = json.loads(Path(args.prompts).read_text())
only = set(filter(None, args.only.split(",")))
model_filter = set(filter(None, args.models.split(",")))
jobs = []
for k in spec["keyframes"]:
    if only and k["id"] not in only: continue
    prompt = f'{spec["shared"]} {k["prompt"]}'
    for m in spec["models"]:
        if model_filter and m["id"] not in model_filter: continue
        jobs.append((k["id"], m["id"], m["params"], prompt))
    vt = spec.get("vector_test")
    if args.vector and vt and k["id"] in vt["keyframes"]:
        jobs.append((k["id"], vt["model"], vt["params"], prompt))

worst = sum(WORST_CASE_USD.get(j[1], 0.5) for j in jobs)
print(f"{len(jobs)} jobs, worst-case ≈ ${worst:.2f}, limit ${args.limit_usd:.2f}")
if worst > args.limit_usd: sys.exit("worst-case estimate exceeds the limit; narrow the job list")

out = Path(args.out); out.mkdir(parents=True, exist_ok=True)
lock, spent, manifest = Lock(), [0.0], []

def run(job):
    kid, model, params, prompt = job
    stem = f'{kid}--{model.split("/")[1]}'
    if any(out.glob(stem + ".*")): return print("exists, skipped:", stem)
    body = json.dumps({"model": model, "prompt": prompt, **params}).encode()
    req = urllib.request.Request(ENDPOINT, body, {"Authorization": f"Bearer {key}", "Content-Type": "application/json"})
    t0 = time.time()
    try:
        with urllib.request.urlopen(req, timeout=600) as r: data = json.loads(r.read())
    except urllib.error.HTTPError as e:
        return print("FAILED", stem, e.code, e.read()[:400].decode(errors="replace"))
    usage = data.get("usage") or {}
    cost = float(usage.get("cost") or 0)
    for i, item in enumerate(data.get("data", [])):
        raw = base64.b64decode(item["b64_json"])
        ext = {"image/png": "png", "image/jpeg": "jpg", "image/webp": "webp", "image/svg+xml": "svg"}.get(item.get("media_type"), "bin")
        path = out / f"{stem}{'' if i == 0 else f'-{i}'}.{ext}"
        path.write_bytes(raw)
        rec = {"keyframe": kid, "model": model, "params": params, "prompt": prompt, "file": path.name,
               "sha256": hashlib.sha256(raw).hexdigest(), "cost_usd": cost, "usage": usage,
               "seconds": round(time.time() - t0, 1), "created": time.strftime("%Y-%m-%dT%H:%M:%S")}
        with lock:
            manifest.append(rec); spent[0] += cost
        print(f"ok {path.name}  ${cost:.3f}  {rec['seconds']}s")

with ThreadPoolExecutor(4) as ex: list(ex.map(run, jobs))
mf = out / "manifest.json"
old = json.loads(mf.read_text()) if mf.exists() else []
mf.write_text(json.dumps(old + manifest, indent=1))
print(f"spent this run ≈ ${spent[0]:.3f} (reported usage)")
